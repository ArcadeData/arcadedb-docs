#!/usr/bin/env python3
"""
Give every Antora page a `:description:` header attribute so the
rendered HTML carries `<meta name="description" content="...">`.

Antora's default UI only emits the meta tag when the page sets
`:description:`, and almost no page in src/main/asciidoc/ does, so
search engines (Bing Webmaster Tools in particular) flag the whole
site for missing descriptions.

For each page under docs/modules/ROOT/pages/ that has no explicit
`:description:`, this script derives one from the first prose
paragraph (falling back to the chapter card titles for chapter
landing pages, or to the page title), strips AsciiDoc markup and
trims it to ~160 characters. Pages that already declare a
`:description:` (in src/main/asciidoc/ or a template) keep theirs, so
a hand-written description always wins over the generated one.

Idempotent: generated descriptions are tagged with a trailing comment
line and replaced on every run.
"""
from __future__ import annotations

import html
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PAGES = REPO / "docs" / "modules" / "ROOT" / "pages"

MAX_LEN = 160
MIN_LEN = 70
MARKER = "// description (auto-generated)"

TITLE_RE = re.compile(r"^=\s+(.+?)\s*$")
HEADING_RE = re.compile(r"^={2,6}\s+\S")
DESCRIPTION_RE = re.compile(r"^:description:", re.MULTILINE)
ATTR_ENTRY_RE = re.compile(r"^:[\w-]+!?:")
ANCHOR_RE = re.compile(r"^\[\[[^\]]*\]\]\s*$")
BLOCK_ATTR_RE = re.compile(r"^\[[^\]]*\]\s*$")
BLOCK_TITLE_RE = re.compile(r"^\.[^\s.]")
DELIMITER_RE = re.compile(r"^(-{2,}|\.{4,}|\+{4,}|={4,}|\*{4,}|_{4,}|/{4,}|\|={3,}|```.*)\s*$")
ADMONITION_RE = re.compile(r"^(NOTE|TIP|IMPORTANT|WARNING|CAUTION):\s+")
LIST_RE = re.compile(r"^\s*(\*+|-|\.+|\d+\.)\s+(.*)$")
SKIP_LINE_RE = re.compile(r"^(image|video|audio|include|toc)::|^ifdef::|^ifndef::|^endif::|^'{3,}$|^<{3}$")
PREAMBLE_END_RE = re.compile(r"^(-{4,}|\.{4,}|\|={3,}|```.*)\s*$")
BOLD_LINE_RE = re.compile(r"^\*[^*]+\*:?$")
CARD_TITLE_RE = re.compile(r'<span class="chapter-card-title">(.*?)</span>')


def _xref_text(m: re.Match) -> str:
    """xref text, or a readable name derived from the target when empty."""
    if m.group(2).strip():
        return m.group(2)
    target = m.group(1)
    name = target.split("#", 1)[1] if "#" in target else Path(target).stem
    return re.sub(r"[-_]+", " ", name)


def strip_markup(text: str) -> str:
    """Reduce inline AsciiDoc to plain text."""
    # Shield backslash-escaped marks (e.g. `\*`) from the formatting passes.
    text = re.sub(r"\\([*_`#+{}\[\]<>])", lambda m: f"\0{ord(m.group(1))}\0", text)
    text = re.sub(r"\bpass:\w*\[(.*?)\]", r"\1", text)
    # xref:target[text] / <<id,text>> / <<id>>
    text = re.sub(r"\bxref:([^\[\s]+)\[([^\]]*)\]", _xref_text, text)
    text = re.sub(r"<<[^,>]+,\s*([^>]+)>>", r"\1", text)
    text = re.sub(r"<<([^>]+)>>", lambda m: m.group(1).replace("-", " "), text)
    # link:url[text], https://url[text], bare URLs
    text = re.sub(r"\b(?:link:)?(?:https?|ftp|mailto):[^\s\[]*\[([^\]]*)\]", r"\1", text)
    text = re.sub(r"\blink:[^\s\[]+\[([^\]]*)\]", r"\1", text)
    text = re.sub(r"\b(?:kbd|btn|menu|footnote|footnoteref|icon|image|stem|latexmath|asciimath):[^\[\s]*\[([^\]]*)\]", r"\1", text)
    # Formatting marks: [.role]#text#, *bold*, _italic_, `mono`, +literal+, ^sup^, ~sub~
    text = re.sub(r"\[[^\]]*\]#([^#]*)#", r"\1", text)
    text = re.sub(r"#([^#]+)#", r"\1", text)
    text = re.sub(r"`\+?([^`]*?)\+?`", r"\1", text)
    text = re.sub(r"(?<![\w*])\*{1,2}(?=\S)([^*]+?)(?<=\S)\*{1,2}(?![\w*])", r"\1", text)
    text = re.sub(r"(?<![\w_])_{1,2}(?=\S)([^_]+?)(?<=\S)_{1,2}(?![\w_])", r"\1", text)
    text = re.sub(r"(?<!\w)\+{1,3}([^+]+?)\+{1,3}(?!\w)", r"\1", text)
    text = re.sub(r"\^([^\^\s]+)\^", r"\1", text)
    # Attribute references and replacements
    text = text.replace("{nbsp}", " ").replace("{empty}", "")
    text = re.sub(r"\{[\w-]+\}", "", text)
    text = text.replace("(C)", "©").replace("(R)", "®").replace("(TM)", "™")
    text = text.replace(" -- ", " – ").replace("...", "…")
    text = text.replace(" +\n", " ").replace("\n", " ")
    text = html.unescape(text)
    text = re.sub(r"\0(\d+)\0", lambda m: chr(int(m.group(1))), text)
    return re.sub(r"\s+", " ", text).strip()


def sanitize(text: str) -> str:
    """Make the text safe as an AsciiDoc attribute value rendered unescaped
    into an HTML attribute by the Antora UI template."""
    text = text.replace('"', "'").replace("<", "").replace(">", "")
    text = text.replace("{", "(").replace("}", ")")
    return text.rstrip("\\ ").strip()


def truncate(text: str) -> str:
    if len(text) <= MAX_LEN:
        return text
    # Prefer ending on a sentence boundary that keeps most of the budget.
    cut = text[:MAX_LEN]
    sentence_end = max(cut.rfind(". "), cut.rfind("! "), cut.rfind("? "))
    if sentence_end >= MIN_LEN:
        return cut[: sentence_end + 1]
    space = cut.rfind(" ")
    cut = cut[: space if space > 0 else MAX_LEN - 1].rstrip(",;:–- ")
    return cut + "…"


def scan(lines: list[str]) -> tuple[list[tuple[str, bool]], list[str]]:
    """Walk the page body and return (paragraphs, section_titles).

    Section titles are the level-1 sections (`==`), or, on pages that have
    none, the standalone bold lines used as pseudo-headings.

    Each paragraph is (plain_text, in_preamble), where in_preamble means it
    appears before the first section heading, code listing or table. A paragraph that introduces a
    list ("...:") gets the list items folded in. Delimited blocks (code,
    tables, admonition and passthrough blocks), lists and admonition
    paragraphs are skipped.
    """
    paragraphs: list[tuple[str, bool]] = []
    sections: list[str] = []
    bold_titles: list[str] = []
    in_preamble = True
    delimiter: str | None = None
    collected: list[str] = []
    i, n = 0, len(lines)

    def flush() -> None:
        nonlocal i
        if not collected:
            return
        paragraph = strip_markup("\n".join(collected))
        collected.clear()
        if paragraph.endswith(":"):
            j = i
            while j < n and not lines[j].strip():
                j += 1
            items: list[str] = []
            while j < n and (m := LIST_RE.match(lines[j])):
                items.append(strip_markup(m.group(2)).rstrip(".;,"))
                j += 1
            if items:
                paragraph = f"{paragraph} {', '.join(items)}."
                i = j
            elif len(paragraph) < 40:
                return  # a bare lead-in such as "Build:" is not prose
            else:
                # Drop a trailing "For example:" style lead-in sentence.
                sentences = re.split(r"(?<=[.!?])\s+", paragraph)
                if len(sentences) > 1:
                    paragraph = " ".join(sentences[:-1])
                else:
                    paragraph = paragraph[:-1].rstrip() + "."
        paragraphs.append((paragraph, in_preamble))

    while i < n:
        line = lines[i].rstrip()
        stripped = line.strip()
        i += 1
        if delimiter is not None:
            if stripped == delimiter:
                delimiter = None
            continue
        if DELIMITER_RE.match(stripped):
            flush()
            delimiter = stripped
            if PREAMBLE_END_RE.match(stripped):
                # Prose after a code listing or table is no longer the
                # page's introduction.
                in_preamble = False
            continue
        if not stripped:
            flush()
            continue
        if stripped.startswith("//"):
            continue
        if collected and not (LIST_RE.match(line) or BLOCK_ATTR_RE.match(stripped)):
            collected.append(stripped)
            continue
        flush()
        if HEADING_RE.match(stripped):
            in_preamble = False
            if stripped.startswith("== "):
                sections.append(strip_markup(stripped[3:]))
            continue
        if BOLD_LINE_RE.match(stripped):
            in_preamble = False
            bold_titles.append(re.sub(r"^Overview\s+", "", strip_markup(stripped).rstrip(":")))
            continue
        if (
            TITLE_RE.match(stripped)
            or ATTR_ENTRY_RE.match(stripped)
            or ANCHOR_RE.match(stripped)
            or BLOCK_ATTR_RE.match(stripped)
            or BLOCK_TITLE_RE.match(stripped)
            or SKIP_LINE_RE.match(stripped)
            or stripped.startswith("|")
        ):
            continue
        if ADMONITION_RE.match(stripped) or LIST_RE.match(line):
            # Swallow the rest of the block so its continuation lines
            # aren't mistaken for prose.
            while i < n and lines[i].strip():
                i += 1
            continue
        collected.append(stripped)
    flush()
    return paragraphs, sections or bold_titles


def describe(text: str, title: str) -> str:
    paragraphs, sections = scan(text.splitlines())
    cards = [html.unescape(c) for c in CARD_TITLE_RE.findall(text)]

    # 1. The page's own introduction (preamble), joined until it is long
    #    enough to be useful.
    intro = ""
    for paragraph, in_preamble in paragraphs:
        if not in_preamble or len(intro) >= MIN_LEN:
            break
        intro = f"{intro} {paragraph}".strip()
    if len(intro) >= MIN_LEN:
        return truncate(sanitize(intro))

    subject = f"ArcadeDB {title}" if title else "ArcadeDB documentation"
    # 2. Chapter landing pages: list what the chapter contains.
    if cards:
        return truncate(sanitize(f"{subject}: {', '.join(cards)}."))
    # 3. Reference pages that open straight into sections: list the sections.
    if len(sections) >= 2:
        return truncate(sanitize(f"{subject}: {', '.join(sections)}."))
    # 4. Any substantial paragraph further down the page.
    for paragraph, _ in paragraphs:
        if len(paragraph) >= MIN_LEN:
            return truncate(sanitize(paragraph))
    # 5. Last resort: whatever is there, led by the title.
    lead = f"{subject} documentation." if title else subject + "."
    return truncate(sanitize(f"{lead} {intro}".strip()))


def process(path: Path) -> bool:
    original = path.read_text(encoding="utf-8")
    # Drop any previously generated description so the run is idempotent.
    text = re.sub(rf"^:description:.*\n{re.escape(MARKER)}\n", "", original, flags=re.MULTILINE)
    if DESCRIPTION_RE.search(text):
        if text != original:
            path.write_text(text, encoding="utf-8")
        return False

    lines = text.splitlines(keepends=True)
    title = ""
    insert_at = 0
    for idx, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or ANCHOR_RE.match(stripped) or stripped.startswith("//"):
            continue
        m = TITLE_RE.match(stripped)
        if m:
            title = strip_markup(m.group(1))
            insert_at = idx + 1
            # Header attribute entries must stay contiguous with the title.
            while insert_at < len(lines) and ATTR_ENTRY_RE.match(lines[insert_at]):
                insert_at += 1
        else:
            insert_at = idx
        break

    description = describe(text, title)
    if not description:
        return False
    entry = f":description: {description}\n{MARKER}\n"
    if not title:
        # No document title: attribute entries must open the document to
        # land in the (implicit) header.
        insert_at = 0
    lines.insert(insert_at, entry)
    path.write_text("".join(lines), encoding="utf-8")
    return True


def main() -> int:
    pages = sorted(PAGES.rglob("*.adoc"))
    if not pages:
        print(f"no pages under {PAGES}; run the earlier migrate steps first", file=sys.stderr)
        return 1
    added = sum(process(p) for p in pages if p.name != "nav.adoc")
    print(f"  added descriptions to {added} of {len(pages)} pages")
    return 0


if __name__ == "__main__":
    sys.exit(main())
