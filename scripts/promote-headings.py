#!/usr/bin/env python3
"""
Promote heading levels in docs/modules/ROOT/pages/ so each page starts
at level 1 (= Page Title). The legacy single-page build nested every
file under a chapter at level 2 (==), so individual files use === / ====
for their own structure. As stand-alone Antora pages they need to be
shifted up — otherwise Asciidoctor warns "section title out of sequence"
and the rendered HTML lacks an h1.

Algorithm:
  - For each page, find the shallowest heading level outside any
    delimited block (listing, literal, passthrough, example, quote,
    sidebar) and outside front-matter / passthrough lines.
  - Shift every heading up by (min_level - 1).
  - Skip files where min_level is already 1.

Idempotent — safe to re-run.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

PAGES = Path(__file__).resolve().parents[1] / "docs" / "modules" / "ROOT" / "pages"

HEADING_RE = re.compile(r"^(=+)(\s+\S.*)$")
# A line that is a block delimiter on its own (4+ identical chars).
# Note: ====+ is also a delimiter (example block); a heading "==== Foo"
# always has trailing text and so does NOT match this regex.
DELIM_RE = re.compile(
    r"^(?:----+|\.\.\.\.+|\+\+\+\++|====+|____+|\*\*\*\*+|//{4,}|--)\s*$"
)


def find_first_heading_level(lines: list[str]) -> int | None:
    in_block: str | None = None
    for line in lines:
        if in_block is None:
            m = DELIM_RE.match(line)
            if m:
                in_block = m.group(0).strip()
                continue
            hm = HEADING_RE.match(line)
            if hm:
                return len(hm.group(1))
        else:
            if line.strip() == in_block:
                in_block = None
    return None


def promote(text: str) -> tuple[str, int]:
    """Shift headings so the first heading becomes `= Title` (level 1) and
    every later heading drops by the same amount but is clamped to level 2
    or deeper. This guarantees a single page-title h1 in article doctype
    and avoids "invalid part" warnings when sibling sections share the
    file's top level."""
    lines = text.splitlines()
    first_level = find_first_heading_level(lines)
    if first_level is None or first_level == 1:
        return text, 0
    shift = first_level - 1
    out: list[str] = []
    in_block: str | None = None
    promoted = 0
    seen_first = False
    for line in lines:
        if in_block is None:
            m = DELIM_RE.match(line)
            if m:
                in_block = m.group(0).strip()
                out.append(line)
                continue
            hm = HEADING_RE.match(line)
            if hm:
                level = len(hm.group(1))
                if not seen_first:
                    new_level = 1
                    seen_first = True
                else:
                    new_level = max(2, level - shift)
                out.append("=" * new_level + hm.group(2))
                promoted += 1
                continue
            out.append(line)
        else:
            out.append(line)
            if line.strip() == in_block:
                in_block = None
    new_text = "\n".join(out)
    if text.endswith("\n") and not new_text.endswith("\n"):
        new_text += "\n"
    return new_text, promoted


def main() -> int:
    files_changed = 0
    headings_promoted = 0
    for path in PAGES.rglob("*.adoc"):
        text = path.read_text(encoding="utf-8")
        new_text, n = promote(text)
        if n and new_text != text:
            path.write_text(new_text, encoding="utf-8")
            files_changed += 1
            headings_promoted += n
    print(f"Promoted {headings_promoted} headings in {files_changed} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
