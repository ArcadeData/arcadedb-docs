#!/usr/bin/env python3
"""
Drop the .html extension from relative links in the built site.

The playbook sets `urls.html_extension_style: drop`, so every link Antora
generates (xrefs, nav, canonical, sitemap) is already extensionless, matching
Cloudflare Pages, which 308s /page.html to /page. Links written by hand in
passthrough HTML (hero sections, landing cards, the chapter cards added by
enrich-chapters.py) still say `page.html`, and each one costs a redirect.
This rewrites those after `antora` has run:

    href="tutorials/run.html#docker"  ->  href="tutorials/run#docker"
    href="concepts/index.html"        ->  href="concepts/"

Absolute URLs (https://...) and site assets under _/ are left alone.

Usage: drop-html-links.py build/site
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

LINK_RE = re.compile(r'href="(?![a-z][a-z0-9+.-]*:|//|#|_/|\.\./_/)([^"]*?)\.html(#[^"]*)?"')


def rewrite(m: re.Match) -> str:
    path, fragment = m.group(1), m.group(2) or ""
    if path == "index" or path.endswith("/index"):
        path = path[: -len("index")] or "./"
    return f'href="{path}{fragment}"'


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__, file=sys.stderr)
        return 1
    site = Path(sys.argv[1])
    changed = 0
    for page in site.rglob("*.html"):
        text = page.read_text(encoding="utf-8")
        new = LINK_RE.sub(rewrite, text)
        if new != text:
            page.write_text(new, encoding="utf-8")
            changed += 1
    print(f"  dropped .html from links in {changed} pages")
    return 0


if __name__ == "__main__":
    sys.exit(main())
