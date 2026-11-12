#!/usr/bin/env python3
"""
Write build/site/llms.txt (https://llmstxt.org) from the Antora nav.

Sections follow the sidebar: one H2 per nav title and per top-level nav
group, a link per page with the page's meta description. Links point at the
HTML pages: Markdown copies of the pages are not published yet.

Run after Antora, so the built pages (for descriptions) and the generated
nav files (docs/modules/ROOT/nav*.adoc, written by migrate.sh) both exist.

Usage: scripts/generate-llms-txt.py build/site
"""
from __future__ import annotations

import html
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
NAV_DIR = REPO / "docs" / "modules" / "ROOT"
NAV_FILES = ["nav.adoc", "nav-query.adoc"]
SITE_URL = "https://docs.arcadedb.com"
COMPONENT = "arcadedb"

NAV_TITLE_RE = re.compile(r"^\.(\S.*)$")
ITEM_RE = re.compile(r"^(\*+)\s+(.*)$")
XREF_RE = re.compile(r"^xref:([^\[#]+)\.adoc(#[^\[]*)?\[(.*)\]\s*$")
DESC_RE = re.compile(r'<meta name="description" content="([^"]*)"')
TITLE_RE = re.compile(r"<title>(.*?)(?: :: [^<]*)?</title>", re.S)

HEADER = """# ArcadeDB Documentation

> ArcadeDB is an open-source multi-model database: graph, document, key/value, time-series, vector and geospatial data in one engine, queried with SQL, Cypher, Gremlin, GraphQL, MongoDB QL or Redis commands, embedded in Java or run as a server.

The documentation is organized like its sidebar: getting started and examples, language drivers, data modeling and operations guides, then the query language and API reference. The current release is listed on the home page.
"""


def page_url(path: str) -> str:
    if path == "index":
        return f"{SITE_URL}/{COMPONENT}/"
    return f"{SITE_URL}/{COMPONENT}/{path}"


def description(site: Path, path: str) -> str:
    f = site / COMPONENT / (path + ".html")
    if not f.exists():
        return ""
    m = DESC_RE.search(f.read_text(encoding="utf-8"))
    return html.unescape(m.group(1)).strip() if m else ""


def link(label: str, url: str, desc: str) -> str:
    label = label.replace("[", "(").replace("]", ")")
    return f"- [{label}]({url})" + (f": {desc}" if desc else "")


def main() -> int:
    site = Path(sys.argv[1] if len(sys.argv) > 1 else "build/site")
    out = [HEADER]
    seen: set[str] = set()
    section: list[str] = []

    def flush(title: str | None) -> None:
        if title and section:
            out.append(f"## {title}\n")
            out.extend(section)
            out.append("")
        section.clear()

    title = None
    groups: list[str] = []  # label path of unlinked parent groups
    for nav in NAV_FILES:
        for raw in (NAV_DIR / nav).read_text(encoding="utf-8").splitlines():
            if m := NAV_TITLE_RE.match(raw):
                flush(title)
                title, groups = m.group(1), []
                continue
            m = ITEM_RE.match(raw)
            if not m:
                continue
            depth, text = len(m.group(1)), m.group(2).strip()
            groups = groups[: depth - 1]
            x = XREF_RE.match(text)
            if depth == 1:
                flush(title)
                title = x.group(3) if x else text
            if not x:
                groups.append(text if depth > 1 else "")
                continue
            groups.append("")
            path, frag, label = x.group(1), x.group(2) or "", x.group(3)
            url = page_url(path) + frag
            if url in seen:
                continue
            seen.add(url)
            prefix = ": ".join(g for g in groups[1:-1] if g)
            section.append(link(f"{prefix}: {label}" if prefix else label, url,
                                "" if frag else description(site, path)))
    flush(title)

    # The Python bindings component has its own nav in another repository;
    # list its pages from the sitemap Antora wrote for it.
    py_sitemap = site / "sitemap-arcadedb-python.xml"
    if py_sitemap.exists():
        out.append("## Python Bindings (arcadedb-python)\n")
        for loc in re.findall(r"<loc>([^<]+)</loc>", py_sitemap.read_text(encoding="utf-8")):
            rel = loc[len(SITE_URL) + 1:]
            f = site / (rel + "index.html" if rel.endswith("/") else rel + ".html")
            if not f.exists():
                continue
            text = f.read_text(encoding="utf-8")
            t = TITLE_RE.search(text)
            d = DESC_RE.search(text)
            out.append(link(html.unescape(t.group(1)).strip() if t else rel, loc,
                            html.unescape(d.group(1)).strip() if d else ""))
        out.append("")

    (site / "llms.txt").write_text("\n".join(out).rstrip() + "\n", encoding="utf-8")
    print(f"llms.txt: {sum(1 for l in out if l.startswith('- ['))} links")
    return 0


if __name__ == "__main__":
    sys.exit(main())
