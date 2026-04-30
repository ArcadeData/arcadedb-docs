#!/usr/bin/env python3
"""
Rewrite legacy `https://docs.arcadedb.com/#<anchor>` links across the
arcadedb-website repo to the new Antora URLs from the migration map.

Default target is /Users/luca/Documents/GitHub/arcadedb-website. Pass
a different path as the first argument to override.

Tries the anchor exactly as written, then progressively cheaper
fallbacks: lowercase, strip leading underscore (legacy auto-IDs),
swap underscores for hyphens, and the lowercased combination of
those. Anchors that still don't match are reported but left in
place so a human can decide what to do.

Plain `https://docs.arcadedb.com` and `https://docs.arcadedb.com/`
(homepage links, no fragment) are left untouched. Plain
`http://docs.arcadedb.com` is upgraded to `https`.

Doesn't commit. Run, then `cd arcadedb-website && git diff`.
"""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

DOCS_REPO = Path(__file__).resolve().parents[1]
TSV = DOCS_REPO / "scripts" / "url-migration-map.tsv"
DEFAULT_WEB = Path("/Users/luca/Documents/GitHub/arcadedb-website")

# https?://docs.arcadedb.com[/]#<anchor>
LINK_RE = re.compile(r"https?://docs\.arcadedb\.com/?#([A-Za-z_][\w.-]*)")
# Plain http://docs.arcadedb.com (no fragment) -> upgrade to https.
PLAIN_HTTP_RE = re.compile(r"\bhttp://docs\.arcadedb\.com\b")

EXTS = {".html", ".md", ".txt", ".yml", ".xml"}
SKIP_DIRS = {"_site", ".git", "node_modules", "vendor"}


def load_mapping(path: Path) -> dict[str, str]:
    mapping: dict[str, str] = {}
    with path.open(encoding="utf-8") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            mapping[row["anchor"]] = row["new_url"]
    return mapping


EXPLICIT_OVERRIDES = {
    # Legacy shorthand the website used before the docs were
    # restructured. None of these survive the automated fallbacks
    # (different anchor IDs, page-only URLs, etc.) so they're hard-
    # coded against the new Antora pages.
    "API": "https://docs.arcadedb.com/arcadedb/reference/http-api/http.html#http-json-api",
    "HTTP-API": "https://docs.arcadedb.com/arcadedb/reference/http-api/http.html#http-json-api",
    "MongoDB-API": "https://docs.arcadedb.com/arcadedb/reference/mongodb-ql/mongo.html",
    "Redis-API": "https://docs.arcadedb.com/arcadedb/reference/redis-ql/redis.html",
    "_run-arcadedb": "https://docs.arcadedb.com/arcadedb/tutorials/run.html",
    "java-api": "https://docs.arcadedb.com/arcadedb/reference/java-api/chapter.html",
}


def lookup(mapping: dict[str, str], anchor: str) -> str | None:
    """Try the anchor and a few fallbacks. Returns the new URL or None."""
    if anchor in EXPLICIT_OVERRIDES:
        return EXPLICIT_OVERRIDES[anchor]
    candidates = [
        anchor,
        anchor.lower(),
        anchor.lstrip("_"),
        anchor.lstrip("_").lower(),
        anchor.replace("_", "-"),
        anchor.replace("_", "-").lower(),
        anchor.lstrip("_").replace("_", "-").lower(),
    ]
    for c in candidates:
        hit = mapping.get(c)
        if hit:
            return hit
    return None


def main() -> int:
    web = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_WEB
    if not web.is_dir():
        print(f"ERROR: {web} is not a directory", file=sys.stderr)
        return 1
    if not TSV.exists():
        print(f"ERROR: {TSV} missing — run scripts/url-migration-map.py first", file=sys.stderr)
        return 1

    mapping = load_mapping(TSV)
    print(f"Loaded {len(mapping)} anchor -> URL mappings")

    replaced = 0
    http_upgraded = 0
    files_changed = 0
    unmatched: dict[str, list[Path]] = {}

    for p in web.rglob("*"):
        if not p.is_file() or p.suffix not in EXTS:
            continue
        if any(part in SKIP_DIRS for part in p.parts):
            continue

        try:
            text = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if "docs.arcadedb.com" not in text:
            continue

        local_replaced = [0]
        local_http = [0]

        def repl_link(m: re.Match) -> str:
            anchor = m.group(1)
            new = lookup(mapping, anchor)
            if new:
                local_replaced[0] += 1
                return new
            unmatched.setdefault(anchor, []).append(p)
            return m.group(0)

        new_text = LINK_RE.sub(repl_link, text)
        new_text, n = PLAIN_HTTP_RE.subn("https://docs.arcadedb.com", new_text)
        local_http[0] = n

        if new_text != text:
            p.write_text(new_text, encoding="utf-8")
            files_changed += 1
            replaced += local_replaced[0]
            http_upgraded += local_http[0]

    print(f"\nReplaced {replaced} legacy fragment links")
    print(f"Upgraded {http_upgraded} http:// references to https://")
    print(f"Files changed: {files_changed}")

    if unmatched:
        print(f"\n{len(unmatched)} anchors had no match; review by hand:")
        for anchor in sorted(unmatched):
            files = sorted({str(f.relative_to(web)) for f in unmatched[anchor]})
            preview = ", ".join(files[:4]) + (" ..." if len(files) > 4 else "")
            print(f"  #{anchor:<35} ({len(files)} occurrence(s): {preview})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
