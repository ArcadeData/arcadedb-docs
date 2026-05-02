# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is the ArcadeDB documentation repository. It produces the HTML site at `docs.arcadedb.com` (built with [Antora](https://antora.org/)) and the `ArcadeDB-Manual.pdf` (built with the Asciidoctor Maven plugin). Both pipelines read from the same canonical AsciiDoc sources in `src/main/asciidoc/`.

## Documentation Pipeline

Two outputs, one source tree:

- **HTML site (production)** — `docs.arcadedb.com` is the Antora build. The Antora playbook reads from `docs/modules/ROOT/{pages,images}/`, which is **regenerated from `src/main/asciidoc/` on every CI run by `scripts/migrate.sh`** (it wipes and rebuilds the `docs/modules/ROOT/` tree). Deploy workflow: `.github/workflows/cloudflare-deploy.yml` — on every push to `main` it does `npm ci` → `bash scripts/migrate.sh` → `npm run build` → `wrangler pages deploy build/site` to the `arcadedb-docs` Cloudflare Pages project.
- **PDF (production)** — `ArcadeDB-Manual.pdf` is built by `mvn` from `src/main/asciidoc/` directly. Workflow: `.github/workflows/pdf.yml`.

**Where to edit content**: `src/main/asciidoc/` is the only place to edit. CI runs `scripts/migrate.sh` automatically on push to `main`, so you do **not** need to run it by hand. Only run it locally if you want to preview the Antora site before pushing.

The legacy single-page Asciidoctor HTML build (`mvn generate-resources` → `target/generated-docs/index.html`) still works and is useful for quick local previews of `src/main/asciidoc/` edits, but it is no longer deployed anywhere — `docs.arcadedb.com` is Antora.

## Building and Serving Documentation

### Preview the Antora site (matches what's live)
```shell
npm ci
bash scripts/migrate.sh
npm run build      # build/site/
npm run serve      # http://localhost:8080
```

### Quick single-page HTML preview (no Antora, no migrate)
```shell
mvn generate-resources                   # → target/generated-docs/index.html
```
Or for a live-served version:
```shell
mvn jetty:run                            # http://localhost:8080
```

### Build the PDF
```shell
mvn -Pgenerate-pdf generate-resources    # → target/generated-docs/ArcadeDB-Manual.pdf
```

## Animated SVG diagrams — house style

When the user asks for an animated SVG, follow this template. Two examples already use it: the polyglot-persistence panels on `concepts/multi-model.adoc` (`.ppd-*` classes) and the bucket-selection animation on `concepts/basics.adoc` (`.bss-*` classes). Stick to the same conventions so all diagrams feel of a piece.

### Where things go

- **The `<svg>` markup** lives inline in the AsciiDoc page, wrapped in `++++` passthrough fences so Asciidoctor leaves it alone.
- **The CSS** goes in **two** places (one for each pipeline), with identical content:
  - `src/main/asciidoc/docinfo.html` — for the legacy single-page build.
  - `docs/ui/supplemental/css/arcadedb.css` — for the Antora build that serves `docs.arcadedb.com`. **This is the file the live site uses.** Forgetting to mirror styles here means the live site renders unstyled (it's how the function-badge bug happened — only the legacy file was updated).
- **One CSS class prefix per diagram** (`.ppd-*`, `.bss-*`, …). Pick a 2-3 letter prefix from the topic and apply it to every element in that diagram so styles never collide between diagrams.

### Color palette (use these, don't invent new ones)

CSS variables to prefer for chrome/text:

- `--color-text-primary` (`#1A1D23`) — primary labels, dot fill
- `--color-text-secondary` (`#4A5568`) — captions, sub-labels
- `--color-border` (`#E2E8F0`) — neutral box strokes
- `--color-border-light` (`#EDF2F7`) — divider lines
- `--color-primary` (`#0066CC`) — accent for the "good" / ArcadeDB-branded path

Brand accent palette for color-coded actors / categories (use in this order so multi-actor diagrams look consistent):

- Blue: stroke `#93C5FD`, text/dot `#0066CC`
- Purple: stroke `#C4B5FD`, text/dot `#7C3AED` (or text `#65A30D` for the lime variant)
- Green: stroke `#6EE7B7`, text `#10B981` / `#047857` (dot `#10B981`)
- Lime: stroke `#84CC16`, text `#65A30D` (used for MongoDB in the polyglot diagram)
- Red: stroke `#FCA5A5`, text `#EF4444` / `#B91C1C` (used to mark "bad totals")
- Yellow: stroke `#FCD34D`, text `#F59E0B`

Use translucent fills (`rgba(R,G,B,0.08-0.12)`) for emphasised "totals" boxes, never as primary fills.

### Geometry & box style

- `viewBox="0 0 1200 <height>"` — pick the height; CSS scales width responsively. For multi-panel diagrams, stack panels vertically at ~300-320 px each separated by a `<line class="…-divider" stroke-dasharray="4 6"/>`.
- All rects: `rx="8"` (small boxes), `rx="10"` (large containers), `rx="999"` for pills.
- Stroke-width: `1.5` everywhere; stroke is colored, fill is `#fff` (or `#FAFBFC` for the "engine" / hash containers).
- Connectors: `stroke-width: 2` for live data paths, `1.5` for layout dividers; `stroke-linecap: round`; `stroke-dasharray: 4 4` for "schematic" connectors, solid for active flows. Use `opacity: 0.35-0.55` on connectors so the dots stand out.
- Dots traveling along paths: `<circle r="7">` filled with the actor's brand color, `stroke="#fff" stroke-width="1"`.

### Font sizes (post-2026-05 bump)

These are the sizes that read well on a 1200px-wide diagram. Use the same scale for new diagrams.

- Section title: **29px**, weight 700, `letter-spacing: 0.06em`, color `--color-text-secondary`
- Section subtitle / caption: **21px**, italic, `--color-text-secondary`
- Box label / actor title: **20-21px**, weight 600-700
- Box subtitle (e.g. file name under a bucket): **17px**, `--color-text-secondary`
- Lane / thread label: **18px**, weight 700, `letter-spacing: 0.05em`
- Code-style label inside a box (e.g. `hash(id) % 3`): **20px**, weight 700, `font-family: var(--font-code)`

If the user asks for "bigger / smaller", scale the whole set proportionally — don't tweak one element in isolation.

### Animation pattern (SMIL)

The whole pattern is dots fading in, gliding along a labeled path, then fading out — repeating forever. Implementation:

1. Define each path with an `id` (`<path id="…-leg1" d="…" class="… …-conn-pg"/>`). Use cubic Bezier (`C`) curves for visually smooth flows.
2. For each dot, render a `<circle r="7" class="… …-dot-pg" opacity="0">` containing:
   - `<animateMotion id="…-leg1" begin="0s; …-legN.end+0.7s" dur="0.5s" fill="freeze"><mpath href="#…-leg1"/></animateMotion>` — `dur` is per-leg flight time, typically 0.5-1.2s.
   - `<set attributeName="opacity" to="1" begin="0s; …-legN.end+0.7s"/>` — fade in *at the same time* the motion starts.
   - `<set attributeName="opacity" to="0" begin="…-leg1.end"/>` — fade out when motion ends.
3. Chain begin times: each leg starts a small delay (`+0.1s` to `+0.7s`) after the previous leg's `id.end`. The very first leg has a literal time (`0s`) **and** a "loop-back" time keyed off the last leg of the cycle, so the animation repeats forever without `repeatCount`.
4. To run several actors in parallel (like the THREAD panel), give them all the same `begin` expression so they start in lockstep.

This pattern works in every modern browser and degrades gracefully (the diagram is still readable as a static image if SMIL is disabled).

### Accessibility & responsive

- Always set `role="img"` and `aria-label="<one-sentence description of what the animation shows>"` on the outer `<svg>`.
- In CSS: `@media (max-width: 700px) { .…-svg { display: none; } }` — diagrams at 1200px don't shrink to phones gracefully, so hide them on narrow viewports rather than ship a broken layout.

### Process checklist when adding a new diagram

1. Pick a 2-3 letter class prefix; reserve it (grep to confirm it's free).
2. Sketch the panels at `viewBox="0 0 1200 <height>"`; align everything on a 10-px grid.
3. Write the `<svg>` inline in the page, wrapped in `++++` … `++++`.
4. Add the CSS to **both** `src/main/asciidoc/docinfo.html` and `docs/ui/supplemental/css/arcadedb.css`.
5. Run `bash scripts/migrate.sh && npm run build` and inspect `build/site/<page>.html` to confirm the SVG and CSS arrived.
6. Push — CI deploys to `docs.arcadedb.com`.

### Algolia DocSearch

DocSearch is wired into the Antora UI bundle. It's enabled in CI when the `ALGOLIA_APP_ID`, `ALGOLIA_API_KEY` (search-only key), and `ALGOLIA_INDEX_NAME` repo secrets are set — `cloudflare-deploy.yml` and `antora-preview.yml` both pick them up and turn on the search UI by setting `SITE_SEARCH_PROVIDER=algolia`. Locally, export the same three env vars plus `SITE_SEARCH_PROVIDER=algolia` before `npm run build` to preview search.

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
- Cloudflare Pages for deployment of `docs.arcadedb.com` (`cloudflare-deploy.yml`)
