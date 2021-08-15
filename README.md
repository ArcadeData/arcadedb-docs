[![Netlify Status](https://api.netlify.com/api/v1/badges/0dbeb04c-0408-4273-90cf-5ca7d7c600e1/deploy-status)](https://app.netlify.com/sites/amazing-booth-ce1e9d/deploys)

# ArcadeDB Documentation

Generate html and pdf documentation:

```shell
mvn generate-sources
```
Documentation is generated under `target/generated-docs` folder

Serve documentation on local http server:
```shell
mvn jetty:run
```
then open the browser to http://localhost:8080

