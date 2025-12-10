# Contributing to ArcadeDB Documentation

Thank you for your interest in contributing to the ArcadeDB documentation! This guide provides information on how to contribute effectively.

## Documentation Structure

The ArcadeDB documentation is structured as follows:

- `src/main/asciidoc/` - Main documentation source files
  - `api/` - API documentation for different languages and interfaces
  - `appendix/` - Technical references and detailed information
  - `concepts/` - Core concepts explanation
  - `images/` - Documentation images
  - `introduction/` - Getting started information
  - `security/` - Security-related documentation
  - `server/` - Server configuration and administration
  - `sql/` - SQL command reference
  - `studio/` - ArcadeDB Studio documentation
  - `tools/` - Tools and utilities documentation

## Naming Conventions

To maintain consistency throughout the documentation, please follow these naming conventions:

### File Naming

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

## Content Guidelines

- Use clear, concise language
- Provide practical examples where possible
- Include code snippets with language specifiers for syntax highlighting
- Use headings and subheadings to organize content
- Add cross-references to related sections

## Building the Documentation

To build the documentation locally:

```shell
mvn generate-resources
```

Documentation is generated in the `target/generated-docs` folder.

To serve the documentation on a local HTTP server:

```shell
mvn jetty:run
```

Then open your browser to http://localhost:8080

## Submitting Changes

1. Fork the repository
2. Create a new branch for your changes
3. Make your changes
4. Build and preview the documentation locally
5. Submit a pull request with a clear description of the changes

Thank you for your contributions to making the ArcadeDB documentation better!
