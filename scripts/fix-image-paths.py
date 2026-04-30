#!/usr/bin/env python3
"""
Rewrite legacy image paths under docs/modules/ROOT/pages/ to Antora-style
references. In Antora the module's images/ folder is auto-resolved, so
`image::foo.png[]` is correct regardless of the page's depth.

Replaces:
  image::../images/foo.png[...]      -> image::foo.png[...]
  image::../../images/foo.png[...]   -> image::foo.png[...]
  image:../images/foo.png[...]       -> image:foo.png[...]
  image:../../images/foo.png[...]    -> image:foo.png[...]

Idempotent.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

PAGES = Path(__file__).resolve().parents[1] / "docs" / "modules" / "ROOT" / "pages"

# image:: (block) or image: (inline) followed by 1+ "../" segments and "images/"
IMAGE_RE = re.compile(r"(image::?)(?:\.\./)+images/")


def main() -> int:
    changed = 0
    refs = 0
    for path in PAGES.rglob("*.adoc"):
        text = path.read_text(encoding="utf-8")
        new_text, n = IMAGE_RE.subn(lambda m: m.group(1), text)
        if n:
            path.write_text(new_text, encoding="utf-8")
            changed += 1
            refs += n
    print(f"Rewrote {refs} image references across {changed} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
