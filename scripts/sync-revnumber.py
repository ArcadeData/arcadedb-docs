#!/usr/bin/env python3
"""
Copy the release number from src/main/asciidoc/version.adoc into the
`revnumber` attribute of docs/antora.yml.

version.adoc is the one place to set the current ArcadeDB release. The
legacy single-page build includes it directly, generate-pdf-manual.py
reads it for the PDF, and this script feeds it to Antora, so install and
run snippets written as `{revnumber}` show the same release everywhere.

Idempotent: rewrites antora.yml only when the value differs.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
VERSION_FILE = REPO / "src" / "main" / "asciidoc" / "version.adoc"
ANTORA_YML = REPO / "docs" / "antora.yml"

VERSION_RE = re.compile(r"^:revnumber:\s*(\S+)\s*$", re.M)
ANTORA_RE = re.compile(r"^(\s*revnumber:\s*)'[^']*'\s*$", re.M)


def read_revnumber() -> str:
    m = VERSION_RE.search(VERSION_FILE.read_text(encoding="utf-8"))
    if not m:
        sys.exit(f"no :revnumber: line in {VERSION_FILE}")
    return m.group(1)


def main() -> int:
    rev = read_revnumber()
    text = ANTORA_YML.read_text(encoding="utf-8")
    if not ANTORA_RE.search(text):
        sys.exit(f"no revnumber attribute in {ANTORA_YML}")
    new = ANTORA_RE.sub(lambda m: f"{m.group(1)}'{rev}'", text, count=1)
    if new != text:
        ANTORA_YML.write_text(new, encoding="utf-8")
    print(f"revnumber: {rev}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
