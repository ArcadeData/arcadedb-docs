#!/usr/bin/env python3
"""
Remove the legacy "Edit this section" inline image macros from
src/main/asciidoc/**/*.adoc.

In the legacy single-page build every section header was followed by
an `image:../images/edit.png[link=...]` floated to the right that
linked to the file on GitHub. With Antora the same affordance lives
in the page toolbar, so the inline buttons are now visual noise.

The script targets the canonical source (src/main/asciidoc/) so the
PDF build picks up the removal too. Idempotent — safe to re-run.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src" / "main" / "asciidoc"

# image:: (block) or image: (inline) pointing at any path that ends
# in /edit.png, with any attribute list.
EDIT_IMG_RE = re.compile(r"image::?[^\[\n]*edit\.png\[[^\]]*\]")
# Lines that, after the image is removed, contain only whitespace.
BLANK_AFTER_STRIP_RE = re.compile(r"^\s*$")


def strip(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    if "edit.png" not in text:
        return 0
    lines = text.splitlines()
    out: list[str] = []
    removed = 0
    for line in lines:
        new_line, n = EDIT_IMG_RE.subn("", line)
        if n:
            removed += n
            if BLANK_AFTER_STRIP_RE.match(new_line):
                # Drop the whole line — the image was its only content.
                continue
        out.append(new_line)
    new_text = "\n".join(out)
    new_text = re.sub(r"\n{3,}", "\n\n", new_text)
    if not new_text.endswith("\n"):
        new_text += "\n"
    if new_text != text:
        path.write_text(new_text, encoding="utf-8")
    return removed


def main() -> int:
    total = 0
    files_changed = 0
    for path in SRC.rglob("*.adoc"):
        n = strip(path)
        if n:
            total += n
            files_changed += 1
    print(f"Removed {total} edit-button image macros across {files_changed} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
