#!/usr/bin/env python3
"""
Append a "What's inside" cards section to every chapter.adoc that
ended up nearly empty after the include:: stripping pass.

Antora can't transitively render include:: aggregators across pages,
so the legacy chapter.adoc files (which were just `= Title` plus a
list of `include::child.adoc[]`) become useless landing pages with
nothing but a heading. This script walks each chapter.adoc, looks
up its original include order from the src/main/asciidoc tree, and
appends a card grid linking to each child page with its title.

Idempotent — strips any previously generated card block and
re-emits it from current state.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SRC = REPO / "src" / "main" / "asciidoc"
PAGES = REPO / "docs" / "modules" / "ROOT" / "pages"

INCLUDE_RE = re.compile(r"^include::([^\[]+\.adoc)\[", re.MULTILINE)
HEADING_RE = re.compile(r"^=+\s+(.+?)\s*$")
ANCHOR_RE = re.compile(r"^\[\[[^\]]+\]\]\s*$")
TITLE_RE = re.compile(r"^=\s+\S")
GENERATED_BEGIN = "// >>> chapter-cards (auto-generated) <<<"
GENERATED_END = "// <<< chapter-cards (auto-generated) >>>"

# A short blurb per top-level chapter. Children inherit a generic
# "Open page" description, which the card UI hides under the title.
CHAPTER_DESCRIPTIONS: dict[str, str] = {
    "tutorials": "Step-by-step guides to get you up and running with ArcadeDB.",
    "use-cases": "Production-ready example projects you can clone and run.",
    "concepts": "Architecture, data models, and design decisions behind ArcadeDB.",
    "how-to": "Practical recipes for specific tasks and integrations.",
    "reference": "Complete technical reference for languages, APIs, and configuration.",
    "tools": "Studio, console, and other tools that ship with ArcadeDB.",
    "appendix": "Algorithms reference, community resources, and known issues.",
}


def first_heading(page_path: Path) -> str | None:
    if not page_path.exists():
        return None
    for line in page_path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith((":", "//")):
            continue
        if s.startswith(("[[", "[#", "[discrete", "[id=")):
            continue
        m = HEADING_RE.match(s)
        if m:
            return m.group(1).replace("`", "").strip()
    return None


def includes_in(src_chapter: Path) -> list[Path]:
    if not src_chapter.exists():
        return []
    text = src_chapter.read_text(encoding="utf-8")
    out: list[Path] = []
    for rel in INCLUDE_RE.findall(text):
        rel = rel.strip()
        if rel.startswith("http"):
            continue
        target = (src_chapter.parent / rel).resolve()
        if target.exists():
            out.append(target)
    return out


def src_to_pages_rel(src_path: Path) -> str | None:
    try:
        return src_path.relative_to(SRC).as_posix()
    except ValueError:
        return None


def strip_existing_block(text: str) -> str:
    pattern = re.compile(
        re.escape(GENERATED_BEGIN) + r".*?" + re.escape(GENERATED_END) + r"\n*",
        re.S,
    )
    return pattern.sub("", text).rstrip() + "\n"


SUBHEADING_RE = re.compile(r"^==+\s+\S")


def strip_orphan_subheadings(text: str) -> str:
    """Remove sub-headings (== or deeper) whose body is empty.

    The legacy chapter.adoc files used sub-headings purely as labels
    above batches of include:: directives (e.g. tutorials/chapter.adoc
    has `=== Application Developer Guide` between the early tutorials
    and the developer-focused ones). Once includes are stripped and
    the cards block takes over navigation, those labels become orphan
    headings with no following content. Drop them so chapter pages
    don't render bare "Application Developer Guide" stubs.

    Preserves the page's level-1 title and any sub-heading that has
    real prose / table / list content below it before the next heading.
    """
    lines = text.splitlines()
    # Find page title line; only act on the body that follows.
    title_idx = next(
        (i for i, l in enumerate(lines) if TITLE_RE.match(l)), None
    )
    if title_idx is None:
        return text
    head = lines[: title_idx + 1]
    body = lines[title_idx + 1:]

    # Identify spans that belong to each sub-heading: from any preceding
    # [[anchor]] / blank lines up through the heading itself, then the
    # body until the next heading or EOF. Drop spans whose body is empty.
    out: list[str] = []
    i = 0
    while i < len(body):
        line = body[i]
        if SUBHEADING_RE.match(line):
            # Walk back over preceding [[anchor]]s and blank lines we
            # already emitted, since they belong to this orphan.
            attached = []
            while out and (
                out[-1].strip() == ""
                or out[-1].strip().startswith("[[")
                or out[-1].strip().startswith("[#")
            ):
                attached.insert(0, out.pop())
            # Walk forward over any blank lines after the heading.
            j = i + 1
            while j < len(body) and not body[j].strip():
                j += 1
            # Is the next meaningful line another heading or EOF?
            if j == len(body) or SUBHEADING_RE.match(body[j]) or TITLE_RE.match(body[j]):
                # Orphan — drop the heading and its preceding anchors.
                i = j
                continue
            # Real content follows; keep the heading and its preceding lines.
            out.extend(attached)
            out.append(line)
            i += 1
            continue
        out.append(line)
        i += 1

    return "\n".join(head + out).rstrip() + "\n"


def render_card(page_path: Path, page_rel: str) -> str | None:
    title = first_heading(page_path) or page_path.stem.replace("-", " ").title()
    title_attr = title.replace('"', "&quot;")
    return (
        f'  <a class="chapter-card" href="{page_rel.replace(".adoc", ".html")}">'
        f'<span class="chapter-card-title">{title_attr}</span>'
        f"</a>"
    )


def render_block(cards: list[str]) -> str:
    return (
        "\n"
        f"{GENERATED_BEGIN}\n"
        "++++\n"
        '<div class="chapter-cards">\n'
        + "\n".join(cards)
        + "\n</div>\n"
        "++++\n"
        f"{GENERATED_END}\n"
    )


def has_meaningful_intro(body: str) -> bool:
    """A chapter has 'real' content if its body contains a heading
    other than the page title, a table, an admonition, or a substantial
    list. Used to decide where the cards block should land — we
    always append, but if there's nothing else we lead with the
    chapter description above the cards."""
    return bool(re.search(r"^(==+\s|\|===|\[NOTE\]|\* )", body, re.M))


def body_already_lists_children(text: str, children: list[Path]) -> bool:
    """Return True if the chapter body already cross-references its
    children — typically a hand-written bullet list of `xref:foo.adoc`
    entries — so the auto-cards block would just duplicate them.

    Uses a per-child filename check rather than a count, so a chapter
    with three children and three matching xrefs still triggers the
    skip, while a chapter with fifteen children and one stray xref
    does not."""
    if not children:
        return False
    matched = 0
    for child in children:
        # Match xref:.../<basename>[...] anywhere in the body — child
        # paths in the source still use forward slashes.
        # An xref to a child looks like xref:path/to/foo.adoc[label] or
        # xref:path/to/foo.adoc#anchor[label]; the `#anchor` is optional.
        pattern = rf"xref:[^\[\s]*{re.escape(child.name)}(?:#[^\[\s]*)?\["
        if re.search(pattern, text):
            matched += 1
    return matched >= max(3, (len(children) + 1) // 2)


def process(chapter: Path) -> bool:
    rel = chapter.relative_to(PAGES).as_posix()
    src_chapter = SRC / rel
    if not src_chapter.exists():
        return False
    children = includes_in(src_chapter)
    if not children:
        return False
    cards: list[str] = []
    for child in children:
        child_rel = src_to_pages_rel(child)
        if child_rel is None:
            continue
        page_path = PAGES / child_rel
        if not page_path.exists():
            continue
        rendered = render_card(page_path, child_rel)
        if rendered:
            cards.append(rendered)
    if not cards:
        return False

    text = chapter.read_text(encoding="utf-8")
    text = strip_existing_block(text)
    text = strip_orphan_subheadings(text)

    # If the chapter already lists its children via xref:, the cards
    # would be redundant and the link targets often clash with the
    # hand-curated path-relative bullet list. Save the cleaned text
    # without re-emitting the cards block.
    if body_already_lists_children(text, children):
        chapter.write_text(text, encoding="utf-8")
        return False

    section = rel.split("/", 1)[0]
    blurb = CHAPTER_DESCRIPTIONS.get(section)
    body_after_title = re.split(TITLE_RE, text, maxsplit=1)
    inject_blurb = blurb and not has_meaningful_intro(text)
    if inject_blurb and len(body_after_title) >= 2:
        head_lines = text.splitlines()
        out: list[str] = []
        title_seen = False
        for line in head_lines:
            out.append(line)
            if not title_seen and TITLE_RE.match(line):
                title_seen = True
                out.append("")
                out.append(blurb)
        text = "\n".join(out).rstrip() + "\n"

    text = text.rstrip() + "\n" + render_block(cards)
    chapter.write_text(text, encoding="utf-8")
    return True


def main() -> int:
    chapters = sorted(PAGES.rglob("chapter.adoc"))
    enriched = 0
    for ch in chapters:
        if process(ch):
            enriched += 1
    print(f"Enriched {enriched} chapter pages with auto-generated cards")
    return 0


if __name__ == "__main__":
    sys.exit(main())
