# -*- coding: utf-8 -*-

from boto.s3.connection import Location
from boto.s3 import connect_to_region
from boto.s3.key import Key
from decouple import config
import gzip
import os
import sys
import tempfile

AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
BUCKET_NAME = config('BUCKET_NAME')
SOURCE_FOLDER = 'frontend/dist/'
S3_FOLDER = ''
INDEX_DOC_ROOT = 'index.html'
ERROR_DOC = '404.html'


def add_file(source_file, s3_key):
    """write a file to an s3 key"""
    if source_file.endswith(".js") or source_file.endswith(".css"):
        print("gzipping %s to %s" % (source_file, s3_key.key))
        gzip_to_key(source_file, s3_key)
    else:
        print("uploading %s to %s" % (source_file, s3_key.key))
        s3_key.set_contents_from_filename(source_file)


def gzip_to_key(source_file, key):
    tmp_file = tempfile.NamedTemporaryFile(mode="wb", suffix=".gz",
                                           delete=False)
    with open(source_file, 'rb') as f_in:
        with gzip.open(tmp_file.name, 'wb') as gz_out:
            gz_out.writelines(f_in)
    key.set_metadata(
        'Content-Type',
        'application/x-javascript' if source_file.endswith(".js") else
        'text/css')
    key.set_metadata('Content-Encoding', 'gzip')
    key.set_contents_from_filename(tmp_file.name)
    os.unlink(tmp_file.name)


def dir_to_bucket(src_directory, bucket):
    """recursively copy files from source directory to boto bucket"""
    for root, sub_folders, files in os.walk(src_directory):
        for file in files:
            abs_path = os.path.join(root, file)
            rel_path = os.path.relpath(abs_path, src_directory)
            # get S3 key for this file
            k = Key(bucket)
            k.key = rel_path
            add_file(abs_path, k)
            k.set_acl('public-read')


def percent_cb(complete, total):
    sys.stdout.write('.')
    sys.stdout.flush()

c = connect_to_region(
    Location.SAEast,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

BKT = c.lookup(BUCKET_NAME)
if BKT is None:
    BKT = c.create_bucket(BUCKET_NAME, location=Location.SAEast)
    print "Creating bucket!"
else:
    BKT = c.get_bucket(BUCKET_NAME)
    print "Bucket already exists!"

filez = BKT.list()
folder = [key.name for key in filez]
folder_size = len(folder)

if folder_size > 0:
    print "Do you want to clean your bucket? "
    answ = raw_input("> ")

    if answ.lower() in {"y", "yes", "yea", "si", "sim", "go", "aye", "sure"}:
        result = BKT.delete_keys(folder)
        print "Cleaned!"
        print "Uploading all!"
        dir_to_bucket(SOURCE_FOLDER, BKT)
    else:
        print "Ok. So let's upload this way! The files will be overwritten."
        print "Do you want to continue?"
        answ = raw_input("> ")
        if answ.lower() in {"y", "yes", "yea", "si",
                            "sim", "go", "aye", "sure"}:
            dir_to_bucket(SOURCE_FOLDER, BKT)
else:
    print "Uploading all!"
    dir_to_bucket(SOURCE_FOLDER, BKT)

# set site config
BKT.delete_website_configuration()
BKT.configure_website(suffix=INDEX_DOC_ROOT, error_key=ERROR_DOC)

# enable logging
BKT.set_as_logging_target()
BKT.enable_logging(target_bucket=BUCKET_NAME, target_prefix='logs/')

print 'Finish! =)'
