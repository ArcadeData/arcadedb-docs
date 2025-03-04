[![Netlify Status](https://api.netlify.com/api/v1/badges/eef44996-0500-4b34-bd74-c9043079e547/deploy-status)](https://app.netlify.com/sites/laughing-saha-bb44e9/deploys)

# ArcadeDB Documentation

Generate html and pdf documentation:

```shell
mvn generate-resources
```

Documentation is generated under `target/generated-docs` folder

Serve documentation on local http server:

```shell
mvn jetty:run
```

then open the browser to http://localhost:8080

## Documentation Conventions

To maintain consistency across the documentation, please follow these naming conventions:

### File Naming Conventions

All documentation files should use lowercase naming with hyphens between words:

- ✅ `lowercase-with-hyphens.adoc`
- ❌ `CamelCase.adoc`
- ❌ `UPPERCASE.adoc`
- ❌ `snake_case.adoc`

### Document ID Anchors

Document anchors should also use lowercase with hyphens:

```asciidoc
[[anchor-id-example]]
== Section Title
```

### Cross-References

Cross-references should use the lowercase anchor IDs:

```asciidoc
See the <<anchor-id-example,related section>> for more information.
```
