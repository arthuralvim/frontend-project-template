# frontend-project-template

> Just a simple frontend template to start working.

## RUN

### Dependencies

```bash
 $ npm install -g grunt-cli
 $ npm install -g bower
```

### Packages

```bash
 $ bower install <package name> --save
```
### Build

```bash
 $ npm install
 $ bower install
```

### Development

```bash
 $ grunt serve
```

Open: http://localhost:9000/

### Deploy

```bash
 $ cp deploy/.env-example deploy/.env
 $ grunt clean
 $ grunt build
```

In order to deploy to Amazon S3 directly you must set these enviroment vars:

* AWS\_ACCESS\_KEY\_ID
* AWS\_SECRET\_ACCESS\_KEY
* BUCKET\_NAME
