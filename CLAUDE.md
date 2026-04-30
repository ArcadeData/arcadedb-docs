# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is the ArcadeDB documentation repository, which generates HTML and PDF documentation from AsciiDoc source files. **A migration to [Antora](https://antora.org/) is in progress on the `feat/antora` branch** — see "Documentation Pipeline" below.

## Documentation Pipeline (transitional state)

The repo currently runs two HTML pipelines in parallel:

- **Legacy (production)**: `mvn generate-resources` → single-page HTML + `ArcadeDB-Manual.pdf`. Source: `src/main/asciidoc/`. Deployed to `docs.arcadedb.com` via `.github/workflows/cloudflare-deploy.yml`.
- **Antora (preview, `feat/antora` branch only)**: `npm run build` → multi-page site at `build/site/`. Source: `docs/modules/ROOT/{pages,images}/`, **regenerated from `src/main/asciidoc/` by `scripts/migrate.sh`**. Deployed to a Cloudflare Pages preview branch via `.github/workflows/antora-preview.yml`.

**Where to edit content**: `src/main/asciidoc/` remains the canonical source. After editing, run `scripts/migrate.sh` to refresh `docs/modules/ROOT/` (or rely on CI to do it). The migration is end-to-end re-runnable — it wipes and rebuilds `docs/modules/ROOT/{pages,images}` on every invocation.

The PDF build is unchanged — it still reads from `src/main/asciidoc/`.

## Building and Serving Documentation

### Generate legacy HTML + PDF
```shell
mvn generate-resources
```

Output is generated in `target/generated-docs/`

### Build the Antora site
```shell
npm ci
bash scripts/migrate.sh
npm run build      # build/site/
npm run serve      # http://localhost:8080
```

### Serve documentation locally
```shell
mvn jetty:run
```

Then open http://localhost:8080

### Using Docker (no local Maven installation needed)
```shell
# Build documentation
docker run --rm -v "$PWD":/docs -w /docs maven:3.8.8 mvn generate-resources

# Serve documentation
docker run --rm -it -p 8080:8080 -v "$PWD":/docs -w /docs maven:3.8.8 mvn jetty:run
```

### Validate documentation
```shell
python docs-validator.py
```

This checks:
- File naming conventions (lowercase with hyphens)
- Anchor naming conventions (lowercase with hyphens)
- Cross-reference validity (all references point to existing anchors)
- Orphaned pages (pages not referenced by other pages)

### Fix cross-references
```shell
python fix-crossrefs.py
```

This script can automatically fix known cross-reference issues based on a predefined mapping.

## Documentation Structure

All documentation source files are located in `src/main/asciidoc/` with the following organization:

- `administration-guide/` - Server configuration and administration
- `api-reference/` - API documentation for Java, HTTP, and other interfaces
- `core-concepts/` - Core database concepts and architecture
- `developer-guide/` - Developer-focused documentation
- `getting-started/` - Tutorials and quick start guides
- `images/` - All documentation images
- `introduction/` - Introduction and overview content
- `query-languages/` - SQL and Cypher query language documentation
  - `sql/` - SQL command reference
  - `cypher/` - Cypher query language documentation
- `reference/` - Technical references
- `tools-guide/` - Tools and utilities documentation
  - `studio/` - ArcadeDB Studio documentation
- `index.adoc` - Main entry point for the web documentation
- `manual.adoc` - Entry point for the PDF manual
- `content.adoc` - Include file that aggregates all documentation sections

## Critical Naming Conventions

The documentation enforces strict naming conventions that are validated in CI:

### Files
All `.adoc` files MUST use lowercase with hyphens:
- ✅ `getting-started.adoc`
- ❌ `GettingStarted.adoc`, `getting_started.adoc`, `GETTINGSTARTED.adoc`

### Anchors
All document anchors MUST use lowercase with hyphens:
```asciidoc
[[my-anchor-id]]
== Section Title
```

### Cross-references
Reference anchors using lowercase with hyphens:
```asciidoc
See the <<my-anchor-id,related section>> for more information.
```

## Technology Stack

- **Build tool**: Maven 3.x
- **Documentation format**: AsciiDoc
- **HTML generator**: Asciidoctor Maven Plugin 3.2.0 with asciidoctorj 2.5.1
- **PDF generator**: asciidoctorj-pdf 2.3.23
- **Diagrams**: asciidoctorj-diagram 3.1.0 (supports PlantUML, Graphviz, D2)
- **Local server**: Jetty Maven Plugin 11.0.26
- **Validation**: Python 3.6+ scripts

## CI/CD Pipeline

GitHub Actions workflow (`.github/workflows/docs-validation.yml`) runs on every push and PR:

1. Validates documentation with `docs-validator.py`
2. Generates documentation with `mvn generate-resources` (verifies diagrams compile)
3. Validates HTML output with html5validator

The workflow requires:
- Python 3.10
- Java 21 (Temurin distribution)
- Graphviz
- D2 diagram tool

## Content Guidelines

When editing documentation:

- Write clear, concise language
- Provide practical examples with code snippets
- Use proper syntax highlighting in code blocks
- Organize content with clear headings
- Add cross-references to related sections using `<<anchor-id,display text>>` syntax
- All anchor IDs must be lowercase with hyphens

## Important Files

- `pom.xml` - Maven build configuration with Asciidoctor plugin settings
- `docs-validator.py` - Documentation validation script
- `fix-crossrefs.py` - Cross-reference fixing utility
- `src/main/asciidoc/index.adoc` - Web documentation entry point
- `src/main/asciidoc/manual.adoc` - PDF manual entry point
- `src/main/asciidoc/content.adoc` - Main include file that aggregates all sections

## Common Issues

### Broken cross-references
If you add or modify anchors, ensure all cross-references are updated. Use `fix-crossrefs.py` for known mappings or update references manually.

### Invalid naming
The validator will fail in CI if files or anchors don't follow the lowercase-with-hyphens convention. Fix these before committing.

### Diagram rendering failures
The build requires Graphviz and D2 to be installed for diagram generation. Locally, ensure these tools are available in your PATH.

## Git Workflow

This repository uses:
- Main branch: `main`
- Mergify for automated PR merging (`.mergify.yml`)
- GitHub Actions for validation on every push/PR
- Netlify for deployment (badge in README.md)
