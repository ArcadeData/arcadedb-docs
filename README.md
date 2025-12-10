[![Netlify Status](https://api.netlify.com/api/v1/badges/eef44996-0500-4b34-bd74-c9043079e547/deploy-status)](https://app.netlify.com/sites/laughing-saha-bb44e9/deploys)

# ArcadeDB Documentation

Generate html and pdf documentation:

```shell
mvn generate-resources
```

> **Tip:** You can build the documentation without installing Maven locally by using Docker:
> ```sh
> docker run --rm -v "$PWD":/docs -w /docs maven:3.8.8 mvn generate-resources
> ```

Documentation is generated under `target/generated-docs` folder

Serve documentation on local http server:

```shell
mvn jetty:run
```

> **Tip:** You can also serve the documentation using Docker without installing Maven:
>
> ```sh
> docker run --rm -it -p 8080:8080 -v "$PWD":/docs -w /docs maven:3.8.8 mvn jetty:run
> ```
>
> Then open your browser to [http://localhost:8080](http://localhost:8080)

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

## Validation

The documentation includes automated validation to ensure consistency and correctness.

### Running the Validator

Run the documentation validator locally:

```shell
python docs-validator.py
```

This validator checks:
1. File naming conventions (lowercase with hyphens)
2. Anchor naming conventions (lowercase with hyphens)
3. Cross-reference validity (all references point to existing anchors)
4. Orphaned pages (pages not referenced by other pages)

### Continuous Integration

The documentation validator runs automatically on GitHub when changes are pushed or pull requests are created. This ensures that documentation standards are maintained consistently.
