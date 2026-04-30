#!/usr/bin/env bash
# Re-runnable, end-to-end Antora content migration.
#
# Wipes docs/modules/ROOT/{pages,images} and rebuilds them from
# src/main/asciidoc/. Each transform is idempotent in isolation, but
# running them in sequence on already-transformed content drifts (e.g.
# heading promotion is not idempotent against itself), so this script
# is the canonical entry point.
#
# Usage: scripts/migrate.sh

set -euo pipefail

REPO=$(cd "$(dirname "$0")/.." && pwd)
cd "$REPO"

SRC=src/main/asciidoc
DEST_PAGES=docs/modules/ROOT/pages
DEST_IMAGES=docs/modules/ROOT/images

echo "==> Wiping $DEST_PAGES and $DEST_IMAGES"
rm -rf "$DEST_PAGES" "$DEST_IMAGES"
mkdir -p "$DEST_PAGES" "$DEST_IMAGES"

echo "==> Copying .adoc tree from $SRC"
cp -R "$SRC"/tutorials       "$DEST_PAGES"/
cp -R "$SRC"/use-cases       "$DEST_PAGES"/
cp -R "$SRC"/concepts        "$DEST_PAGES"/
cp -R "$SRC"/core-concepts   "$DEST_PAGES"/
cp -R "$SRC"/how-to          "$DEST_PAGES"/
cp -R "$SRC"/reference       "$DEST_PAGES"/
cp -R "$SRC"/tools           "$DEST_PAGES"/
cp -R "$SRC"/api-reference   "$DEST_PAGES"/
cp -R "$SRC"/appendix        "$DEST_PAGES"/

echo "==> Copying images"
cp -R "$SRC"/images/. "$DEST_IMAGES"/

echo "==> Writing landing index.adoc"
cp "$REPO"/scripts/templates/index.adoc "$DEST_PAGES"/index.adoc

echo "==> Stripping include:: directives from chapter aggregators"
python3 scripts/strip-includes.py

echo "==> Promoting heading levels"
python3 scripts/promote-headings.py

echo "==> Fixing legacy image paths"
python3 scripts/fix-image-paths.py

echo "==> Rewriting cross-page xrefs"
python3 scripts/rewrite-xrefs.py

echo "==> Generating nav.adoc"
python3 scripts/generate-nav.py

echo
echo "Migration complete. Build with: npm run build"
