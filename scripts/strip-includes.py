#!/usr/bin/env python3
"""
Strip `include::` directives from chapter.adoc and other aggregator pages
under docs/modules/ROOT/pages/.

In the legacy single-page build, chapter.adoc files used include:: to
compose multi-page sections. In Antora each page is independent and
nav.adoc owns the hierarchy, so include:: aggregators no longer apply.

Idempotent — safe to re-run.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

PAGES_ROOT = Path(__file__).resolve().parents[1] / "docs" / "modules" / "ROOT" / "pages"
INCLUDE_RE = re.compile(r"^\s*include::[^\[]+\.adoc\[[^\]]*\]\s*$")


def strip(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    out: list[str] = []
    stripped = 0
    for line in lines:
        if INCLUDE_RE.match(line):
            stripped += 1
            continue
        out.append(line)
    new_text = "\n".join(out)
    new_text = re.sub(r"\n{3,}", "\n\n", new_text)
    if not new_text.endswith("\n"):
        new_text += "\n"
    if new_text != text:
        path.write_text(new_text, encoding="utf-8")
    return stripped


def main() -> int:
    targets = list(PAGES_ROOT.rglob("chapter.adoc"))
    targets.append(PAGES_ROOT / "reference" / "java-api" / "java-reference.adoc")
    total = 0
    for path in targets:
        if not path.exists():
            continue
        n = strip(path)
        if n:
            print(f"{path.relative_to(PAGES_ROOT)}: stripped {n} include(s)")
        total += n
    print(f"\nTotal includes stripped: {total} across {len(targets)} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
