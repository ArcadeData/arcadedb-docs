#!/usr/bin/env python3
"""
Rewrite cross-page <<id>> / <<id,text>> references in
docs/modules/ROOT/pages/ to Antora xref:path/page.adoc#id[text] form.

Same-page references are left as <<id>> (Antora supports both forms,
and not rewriting them keeps diffs small and behaviour identical).

Idempotent — safe to re-run.
"""
from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

PAGES = Path(__file__).resolve().parents[1] / "docs" / "modules" / "ROOT" / "pages"

# [[anchor-id]] on its own line — block anchor / section alias
ANCHOR_RE = re.compile(r"^\[\[([a-zA-Z_][a-zA-Z0-9_.\-]*)\]\]\s*$", re.MULTILINE)
# [#anchor-id] or [#anchor-id,role] block anchor
BLOCK_ID_RE = re.compile(
    r"^\[#([a-zA-Z_][a-zA-Z0-9_.\-]*)(?:,[^\]]+)?\]\s*$", re.MULTILINE
)
# <<id>> or <<id,text>>; non-greedy text capture so adjacent xrefs don't merge
XREF_RE = re.compile(r"<<([a-zA-Z_][a-zA-Z0-9_.\-]*)(?:,(.+?))?>>")


def find_anchors(text: str) -> set[str]:
    return set(ANCHOR_RE.findall(text)) | set(BLOCK_ID_RE.findall(text))


def main() -> int:
    pages = sorted(PAGES.rglob("*.adoc"))
    anchor_to_page: dict[str, str] = {}
    page_anchors: dict[Path, set[str]] = {}
    duplicates: dict[str, list[str]] = defaultdict(list)

    for p in pages:
        rel = p.relative_to(PAGES).as_posix()
        text = p.read_text(encoding="utf-8")
        anchors = find_anchors(text)
        page_anchors[p] = anchors
        for a in anchors:
            if a in anchor_to_page:
                duplicates[a].append(rel)
            else:
                anchor_to_page[a] = rel

    print(f"Indexed {len(anchor_to_page)} unique anchors across {len(pages)} pages")
    if duplicates:
        print(f"\nWARNING: {len(duplicates)} anchors are defined in multiple files")
        print("  (the first occurrence wins for xref rewrites; review these)")
        for anchor, locations in sorted(duplicates.items())[:15]:
            primary = anchor_to_page[anchor]
            print(f"  [[{anchor}]] -> {primary}; also in: {locations}")
        if len(duplicates) > 15:
            print(f"  ... and {len(duplicates) - 15} more duplicate anchors")

    rewrites_total = 0
    files_changed = 0
    broken: list[tuple[str, str]] = []

    for p in pages:
        rel = p.relative_to(PAGES).as_posix()
        text = p.read_text(encoding="utf-8")
        local = page_anchors[p]
        counter = [0]

        def replace(m: re.Match) -> str:
            target = m.group(1)
            text_part = m.group(2)
            if target in local:
                return m.group(0)
            target_page = anchor_to_page.get(target)
            if target_page is None:
                broken.append((rel, target))
                return m.group(0)
            counter[0] += 1
            text_str = f"[{text_part}]" if text_part else "[]"
            return f"xref:{target_page}#{target}{text_str}"

        new_text = XREF_RE.sub(replace, text)
        if new_text != text:
            p.write_text(new_text, encoding="utf-8")
            files_changed += 1
            rewrites_total += counter[0]

    print(f"\nRewrote {rewrites_total} cross-page xrefs across {files_changed} files")
    if broken:
        print(f"\n{len(broken)} broken references (anchor not found anywhere):")
        for src, target in broken[:30]:
            print(f"  {src}: <<{target}>>")
        if len(broken) > 30:
            print(f"  ... and {len(broken) - 30} more")
    return 0


if __name__ == "__main__":
    sys.exit(main())
