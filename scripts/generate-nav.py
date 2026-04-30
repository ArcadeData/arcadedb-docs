#!/usr/bin/env python3
"""
Generate docs/modules/ROOT/nav.adoc by walking the include:: tree in
src/main/asciidoc/content.adoc (the legacy single-page aggregator).

Top-level order is the order in content.adoc.
Within each chapter, file order is the order of include:: directives.

Idempotent — safe to re-run; overwrites nav.adoc.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SRC = REPO / "src" / "main" / "asciidoc"
PAGES = REPO / "docs" / "modules" / "ROOT" / "pages"
NAV = REPO / "docs" / "modules" / "ROOT" / "nav.adoc"

INCLUDE_RE = re.compile(r"^include::([^\[]+\.adoc)\[", re.MULTILINE)
HEADING_RE = re.compile(r"^=+\s+(.+?)\s*$")


def iter_includes(file_path: Path):
    if not file_path.exists():
        return
    text = file_path.read_text(encoding="utf-8")
    for m in INCLUDE_RE.finditer(text):
        rel = m.group(1).strip()
        if rel.startswith("http"):
            continue
        target = (file_path.parent / rel).resolve()
        if target.exists():
            yield target


def first_heading(page_path: Path, fallback: str) -> str:
    text = page_path.read_text(encoding="utf-8")
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith((":", "//")):
            continue
        if s.startswith(("[[", "[#", "[discrete", "[id=")):
            continue
        m = HEADING_RE.match(s)
        if m:
            return m.group(1).replace("`", "").strip()
    return fallback


def to_pages_rel(src_path: Path) -> str | None:
    try:
        return src_path.relative_to(SRC).as_posix()
    except ValueError:
        return None


def walk(node: Path, depth: int, lines: list[str], seen: set[Path]) -> None:
    if node in seen:
        return
    seen.add(node)
    rel = to_pages_rel(node)
    if rel is None:
        return
    page_path = PAGES / rel
    if page_path.exists():
        title = first_heading(page_path, page_path.stem.replace("-", " ").title())
        bullet = "*" * depth
        lines.append(f"{bullet} xref:{rel}[{title}]")
    for child in iter_includes(node):
        walk(child, depth + 1, lines, seen)


def main() -> int:
    if not (SRC / "content.adoc").exists():
        print(f"ERROR: {SRC / 'content.adoc'} not found", file=sys.stderr)
        return 1

    lines: list[str] = ["* xref:index.adoc[Welcome]", ""]
    seen: set[Path] = set()

    for chapter in iter_includes(SRC / "content.adoc"):
        if chapter.name in {"footer.adoc", "web-footer.adoc"}:
            continue
        before = len(lines)
        walk(chapter, 1, lines, seen)
        if len(lines) > before:
            lines.append("")

    NAV.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    print(f"Wrote {NAV.relative_to(REPO)}")
    print(f"  Entries: {sum(1 for line in lines if line.startswith('*'))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
