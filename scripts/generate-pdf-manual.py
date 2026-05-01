#!/usr/bin/env python3
"""
Generate docs/pdf/manual.adoc — a single-document aggregator over every
page in docs/modules/ROOT/pages/ in the same order as the Antora
sidebar nav. Asciidoctor-PDF (driven from pom.xml) consumes this file
to produce ArcadeDB-Manual.pdf.

Reading the existing nav.adoc / nav-query.adoc as the
source of truth keeps the PDF table-of-contents and the website nav
in sync without duplicating the structure in two places.

Idempotent — overwrites the manual on every run.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
NAV_DIR = REPO / "docs" / "modules" / "ROOT"
PAGES = NAV_DIR / "pages"
PDF_DIR = REPO / "docs" / "pdf"
PDF_PAGES = PDF_DIR / "pages"  # stripped page copies for the PDF aggregator

NAV_FILES = ["nav.adoc", "nav-query.adoc"]

XREF_RE = re.compile(r"xref:([^\[\s#]+\.adoc)(?:#[^\[\s]+)?\[([^\]]*)\]")
TITLE_LINE_RE = re.compile(r"^\.([^\s].*?)\s*$")
GROUP_LINE_RE = re.compile(r"^\*\s+([A-Z][^*\[]+?)\s*$")
# Match an entire `++++` HTML passthrough block — `++++` (4+ plus signs)
# on its own line, then any content, then `++++` on its own line.
# Asciidoctor-pdf can't render embedded HTML/SVG, so it dumps these
# blocks as literal text in the PDF; strip them before they get there.
PASSTHROUGH_BLOCK_RE = re.compile(
    r"^\+{4,}[ \t]*$.*?^\+{4,}[ \t]*$\n?",
    re.MULTILINE | re.DOTALL,
)


def parse_nav(nav_path: Path) -> tuple[str, list[tuple[str | None, str]]]:
    """Return (tab_title, [(group_or_None, page_rel)]) preserving order."""
    text = nav_path.read_text(encoding="utf-8")
    tab_title = ""
    items: list[tuple[str | None, str]] = []
    current_group: str | None = None
    for line in text.splitlines():
        if not tab_title:
            m = TITLE_LINE_RE.match(line)
            if m:
                tab_title = m.group(1).strip()
                continue
        # Top-level group label: '* GroupName' with no xref.
        if line.startswith("* ") and "xref:" not in line:
            label = line[2:].strip()
            if label:
                current_group = label
            continue
        # Top-level xref that's also a group header (clickable group).
        if line.startswith("* xref:"):
            m = XREF_RE.search(line)
            if m:
                current_group = m.group(2) or m.group(1)
                items.append((current_group, m.group(1)))
            continue
        # Child page (** xref:...)
        m = XREF_RE.search(line)
        if m:
            items.append((current_group, m.group(1)))
    return tab_title, items


def write_stripped_page(rel: str) -> bool:
    """Copy docs/modules/ROOT/pages/<rel> to docs/pdf/pages/<rel> with
    every ++++ HTML passthrough block removed. Returns True if the
    target was written, False if the source page is missing."""
    src = PAGES / rel
    if not src.exists():
        return False
    dst = PDF_PAGES / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    text = src.read_text(encoding="utf-8")
    stripped = PASSTHROUGH_BLOCK_RE.sub("", text)
    # Collapse runs of 3+ blank lines that the strip can leave behind.
    stripped = re.sub(r"\n{3,}", "\n\n", stripped)
    dst.write_text(stripped, encoding="utf-8")
    return True


def main() -> int:
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    # Re-create the stripped-pages tree from scratch each run so deleted
    # source pages don't linger in PDF builds.
    if PDF_PAGES.exists():
        for p in sorted(PDF_PAGES.rglob("*"), reverse=True):
            if p.is_file():
                p.unlink()
            elif p.is_dir():
                p.rmdir()
    PDF_PAGES.mkdir(parents=True, exist_ok=True)

    out: list[str] = [
        "= ArcadeDB Manual",
        ":revnumber: 26.5.1",
        ":doctype: book",
        ":imagesdir: ../modules/ROOT/images",
        ":source-highlighter: rouge",
        ":icons: font",
        ":toc:",
        ":toclevels: 3",
        ":sectnums:",
        ":sectnumlevels: 3",
        ":idprefix:",
        ":idseparator: -",
        "",
    ]

    seen: set[str] = set()

    for fname in NAV_FILES:
        nav_path = NAV_DIR / fname
        if not nav_path.exists():
            print(f"  WARN: missing {fname}", file=sys.stderr)
            continue
        tab_title, entries = parse_nav(nav_path)
        if not entries:
            continue
        out.append("")
        out.append(f"= {tab_title}")
        out.append("")
        last_group: str | None = None
        for group, page_rel in entries:
            if group and group != last_group:
                out.append("")
                out.append(f"== {group}")
                out.append("")
                last_group = group
            if page_rel in seen:
                continue
            if not write_stripped_page(page_rel):
                print(f"  WARN: missing page {page_rel}", file=sys.stderr)
                continue
            seen.add(page_rel)
            # leveloffset=+2 so each page's `= Title` becomes `=== Title`
            # under the part / chapter levels we emit above it.
            out.append(f"include::pages/{page_rel}[leveloffset=+2]")
            out.append("")

    text = "\n".join(out).rstrip() + "\n"
    target = PDF_DIR / "manual.adoc"
    target.write_text(text, encoding="utf-8")
    print(f"Wrote {target.relative_to(REPO)} ({len(seen)} pages)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
