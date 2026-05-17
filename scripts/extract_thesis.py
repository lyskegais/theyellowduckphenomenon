"""Parse the new EPUB's XHTML and emit one markdown file per section
into src/thesis/. The InDesign export puts all body text in document
order followed by a back-matter block of decorative title pages, so we
ignore the Overcross-1-1-tot-grid markers and use a combination of
known first-section-headings and page-number thresholds to split.

Sections (in document order):
  cover              (title page only — no body)
  introduction       Introducing the Yellow Duck            pages 9-14
  chapter-1          A fixed set of rules                   pages 15-30
  chapter-2          A fixed set of rules on art            pages 31-40
  chapter-3          A fixed set of rules on art explained  pages 41-65
                       by artworks
  approach           Approach                               pages 66-70
  chapter-4          Composition of Thoughts                pages 71-83
  chapter-5          Finding the Yellow Duck                pages 85-96
  conclusion         Concluding That Ducks Never Remain     pages 97-101
                       Yellow
  appendix           Appendix — Jack Burnham,               pages 102-117
                       Systems Esthetics
  bibliography       Bibliography                           pages 118-123
  colofon            Colofon                                pages 124-125
"""

from __future__ import annotations
import re
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString, Tag

ROOT = Path(__file__).resolve().parents[1]
XHTML = ROOT / "epub_extracted" / "OEBPS" / "260517_The_Yellow_Duck_POCKET_for-web_v02.xhtml"
OUT_DIR = ROOT / "src" / "thesis"

# (slug, title, label, title_page_image, prev, next)
CHAPTERS = [
    ("cover",        "The Yellow Duck Phenomenon",                       "Cover",        "Cover.png",                                         None,           "introduction"),
    ("introduction", "Introducing the Yellow Duck",                      "Introduction", "Introducing the Yellow Duck.png",                   "cover",        "chapter-1"),
    ("chapter-1",    "A fixed set of rules",                             "Chapter I",    "01_A fixed set of rules.png",                       "introduction", "chapter-2"),
    ("chapter-2",    "A fixed set of rules on art",                      "Chapter II",   "02_A fixed set of rules on art.png",                "chapter-1",    "chapter-3"),
    ("chapter-3",    "A fixed set of rules on art explained by artworks","Chapter III",  "03_A fixed set of rules on art explained by artworks.png", "chapter-2", "approach"),
    ("approach",     "Approach",                                         "Approach",     "Approach.png",                                      "chapter-3",    "chapter-4"),
    ("chapter-4",    "Composition of Thoughts",                          "Chapter IV",   "04_Composition of Thoughts.png",                    "approach",     "chapter-5"),
    ("chapter-5",    "Finding the Yellow Duck",                          "Chapter V",    "05_Finding the Yellow Duck.png",                    "chapter-4",    "conclusion"),
    ("conclusion",   "Concluding That Ducks Never Remain Yellow",        "Conclusion",   "Concluding that ducks never remain yellow.png",     "chapter-5",    "appendix"),
    ("appendix",     "Appendix — Jack Burnham, Systems Esthetics",       "Appendix",     "Appendix.png",                                      "conclusion",   "bibliography"),
    ("bibliography", "Bibliography",                                     "Bibliography", "Bibliography.png",                                  "appendix",     "colofon"),
    ("colofon",      "Colofon",                                          "Colofon",      "Colofon.png",                                       "bibliography", None),
]

# Heading -> chapter slug (these are unique first headings of each chapter)
HEADING_SWITCHES = {
    "Origin":                                "chapter-1",
    "Burnham":                               "chapter-2",
    "System Aesthetic":                      "chapter-3",
    "Truth":                                 "chapter-4",
    "Inspiration (See)":                     "chapter-5",
    "Jack Burnham - Systems Esthetics":      "appendix",
}

# Page-number thresholds for chapters that have NO Paragraph-title heading
# of their own (Approach, Conclusion, Bibliography, Colofon). The script
# switches to these once page >= threshold.
PAGE_SWITCHES = [
    (66,  "approach"),
    (98,  "conclusion"),
    (119, "bibliography"),
    (124, "colofon"),
]


def normalize(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def extract_footnotes(soup) -> dict[str, str]:
    notes = {}
    for li in soup.select("li._idFootnote"):
        fid = li.get("id", "")
        p = li.find("p")
        if not p:
            continue
        backlink = p.find("a", class_="_idFootnoteAnchor")
        if backlink:
            backlink.decompose()
        text = normalize(p.get_text(separator=" "))
        notes[fid] = text
    return notes


def linearize(p: Tag, fn_counter: list, fn_map: dict, fn_collection: list) -> str:
    """Convert a <p> into plain markdown text with italic markers and
    footnote references inlined."""
    parts: list[str] = []

    def walk(el):
        for child in el.children:
            if isinstance(child, NavigableString):
                parts.append(str(child))
                continue
            if not isinstance(child, Tag):
                continue
            cls = " ".join(child.get("class") or [])
            if child.get("role") == "doc-pagebreak":
                continue
            if "Footnote-Reference" in cls:
                a = child.find("a")
                if a and a.get("href"):
                    fid = a["href"].split("#")[-1]
                    if fid in fn_map:
                        fn_counter[0] += 1
                        n = fn_counter[0]
                        fn_collection.append((n, fn_map[fid]))
                        parts.append(f"[^{n}]")
                continue
            if "ITALIC" in cls or "Emphasis" in cls or child.name in ("em", "i"):
                parts.append("*")
                walk(child)
                parts.append("*")
                continue
            if child.name == "br":
                parts.append(" ")
                continue
            walk(child)

    walk(p)
    text = "".join(parts)
    text = re.sub(r"\*\s*\*", "", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def parse():
    raw = XHTML.read_text(encoding="utf-8")
    soup = BeautifulSoup(raw, "html.parser")

    fn_map = extract_footnotes(soup)

    body = soup.find("body")
    endnotes = soup.find("section", attrs={"epub:type": "endnotes"})
    toc = soup.find("div", attrs={"epub:type": "toc"})
    skip_ancestors = {x for x in (endnotes, toc) if x is not None}

    def in_skipped(el):
        for parent in el.parents:
            if parent in skip_ancestors:
                return True
        return False

    chapters = {slug: {"blocks": [], "footnotes": []} for slug, *_ in CHAPTERS}
    current_slug = None
    current_page = None
    page_switches_left = list(PAGE_SWITCHES)
    fn_counter = [0]
    # Once we cross page 9 (where Introduction starts), begin emitting
    # into the introduction.
    INTRO_PAGE = 9

    # Walk all <p>, <img>, and page-break <div>s in order
    for el in body.find_all(["p", "img", "div"]):
        if in_skipped(el):
            continue

        # Page break marker — update current_page and possibly switch chapter
        if el.name == "div":
            if el.get("role") == "doc-pagebreak":
                pg_id = el.get("id", "")
                m = re.match(r"page(\d+)", pg_id)
                if m:
                    current_page = int(m.group(1))
                    if current_slug is None and current_page >= INTRO_PAGE:
                        current_slug = "introduction"
                        fn_counter = [0]
                    while page_switches_left and current_page >= page_switches_left[0][0]:
                        threshold, slug = page_switches_left.pop(0)
                        current_slug = slug
                        fn_counter = [0]
            # Ignore container divs entirely — only the <p> and <img> inside matter
            continue

        if el.name == "img":
            src = el.get("src", "")
            if src.startswith("image/"):
                fname = src.split("/", 1)[1]
                # The artwork images all live at the back of the EPUB as
                # an image plate; they belong with Chapter III's discussion.
                chapters["chapter-3"]["blocks"].append(("image", fname))
            continue

        # Paragraphs
        cls = " ".join(el.get("class") or [])

        # Decorative title-page text — skip (these appear both at the front
        # of each chapter and again bunched up at the back of the document)
        if "Overcross-1-1-tot-grid" in cls:
            continue

        text = normalize(el.get_text(separator=" "))
        if not text:
            continue

        # Skip running headers / chapter numbers
        if "Overcross-7pt-grijs" in cls or "Chaper-numbers" in cls:
            continue

        # Skip the front matter (title page text) — only emit once we have
        # a current chapter
        if current_slug is None:
            continue

        if cls == "Paragraph-title":
            # Section heading — may switch chapter
            if text in HEADING_SWITCHES:
                current_slug = HEADING_SWITCHES[text]
                fn_counter = [0]
            chapters[current_slug]["blocks"].append(("heading", text))
            continue

        if "onderschriften" in cls:
            chapters[current_slug]["blocks"].append(("caption", text))
            continue

        # Normal paragraph
        line = linearize(el, fn_counter, fn_map, chapters[current_slug]["footnotes"])
        if line.strip():
            chapters[current_slug]["blocks"].append(("para", line))

    return chapters


def yaml_escape(s: str) -> str:
    if any(c in s for c in ':"#') or s.startswith(("-", "?", "!", "&", "*")):
        return '"' + s.replace('"', '\\"') + '"'
    return s


def write_markdown(chapters):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    # Delete any existing thesis md files first
    for old in OUT_DIR.glob("*.md"):
        old.unlink()

    for i, (slug, title, label, image, prev_slug, next_slug) in enumerate(CHAPTERS):
        ch = chapters[slug]
        blocks = ch["blocks"]
        notes = ch["footnotes"]

        fm = [
            "---",
            "layout: thesis.njk",
            "bodyClass: thesis",
            f"title: {yaml_escape(title)}",
            f"chapterLabel: {yaml_escape(label)}",
            f"slug: {slug}",
            f"order: {i}",
            f"titlePage: /assets/images/title-pages/{image}",
        ]
        if prev_slug:
            prev_title = next(c[1] for c in CHAPTERS if c[0] == prev_slug)
            fm += ["prevChapter:", f"  title: {yaml_escape(prev_title)}", f"  url: /thesis/{prev_slug}/"]
        if next_slug:
            next_title = next(c[1] for c in CHAPTERS if c[0] == next_slug)
            fm += ["nextChapter:", f"  title: {yaml_escape(next_title)}", f"  url: /thesis/{next_slug}/"]
        fm.append("---")
        fm.append("")

        body_lines: list[str] = []

        if slug == "cover":
            body_lines.append(f"![Cover](/assets/images/title-pages/{image})")
            body_lines.append("")
            body_lines.append("**The Yellow Duck Phenomenon — *ways to order***")
            body_lines.append("")
            body_lines.append("A Master's thesis in Applied Art submitted to the Post Graduate School of the Sandberg Institute in partial fulfillment of the requirements for the degree of Master of Design.")
            body_lines.append("")
            body_lines.append("Lyske Gais — Sandberg Institute, Amsterdam — July 2012")
        else:
            for kind, content in blocks:
                if kind == "heading":
                    body_lines.append("")
                    body_lines.append(f"## {content}")
                    body_lines.append("")
                elif kind == "image":
                    body_lines.append("")
                    body_lines.append(f"![](/assets/images/defff/{content})")
                    body_lines.append("")
                elif kind == "caption":
                    body_lines.append(f"*{content}*")
                    body_lines.append("")
                elif kind == "para":
                    body_lines.append(content)
                    body_lines.append("")

            if notes:
                body_lines.append("")
                body_lines.append("---")
                body_lines.append("")
                for n, txt in notes:
                    body_lines.append(f"[^{n}]: {txt}")
                    body_lines.append("")

        out_path = OUT_DIR / f"{slug}.md"
        out_path.write_text("\n".join(fm) + "\n".join(body_lines).rstrip() + "\n", encoding="utf-8")
        print(f"Wrote {out_path.name:20s}  ({len([b for b in blocks if b[0]=='para'])} paras, "
              f"{len([b for b in blocks if b[0]=='heading'])} headings, "
              f"{len([b for b in blocks if b[0]=='image'])} images, "
              f"{len(notes)} footnotes)")


if __name__ == "__main__":
    chapters = parse()
    write_markdown(chapters)
