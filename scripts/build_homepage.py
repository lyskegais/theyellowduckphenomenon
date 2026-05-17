"""Build the homepage index.njk with the full text of every chapter,
section headings inline, and ducks marking every replaced image."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
THESIS = ROOT / "src" / "thesis"
OUT = ROOT / "src" / "index.njk"

DUCK_SRC = '{{ "/assets/images/07_Yellow_Ducks.png" | url }}'


def html_attr(s: str) -> str:
    return (
        s.replace("&", "&amp;")
         .replace('"', "&quot;")
         .replace("<", "&lt;")
         .replace(">", "&gt;")
    )


def img_url(path: str) -> str:
    """Wrap an asset path in the Nunjucks | url filter."""
    return f'{{{{ "{path}" | url }}}}'


def duck(label: str, image: str | None = None, url: str | None = None) -> str:
    attrs = [f'data-label="{html_attr(label)}"']
    if image:
        attrs.append(f'data-image="{img_url(image)}"')
    if url:
        attrs.append(f'data-url="{img_url(url)}"')
    return f'<img class="duck" src="{DUCK_SRC}" alt="" {" ".join(attrs)}>'


def parse_md(path: Path):
    """Return (preview_text, list_of_blocks).

    blocks is a list of dicts: {"type": "para"|"heading"|"quote"|"image", "text": ...}.
    Stops at the `---` separator that begins the footnote definitions.
    """
    raw = path.read_text(encoding="utf-8")
    # Strip frontmatter
    raw = re.sub(r"^---\n.*?\n---\n", "", raw, count=1, flags=re.DOTALL)
    # Drop footnote definitions section (everything from a line that is just `---`)
    raw = re.split(r"\n---\n", raw, maxsplit=1)[0]
    # Strip footnote markers like [^1] from the visible homepage text
    raw = re.sub(r"\[\^\d+\]", "", raw)

    blocks = []
    current_para = []

    def flush(kind):
        if current_para:
            text = " ".join(current_para).strip()
            if text:
                blocks.append({"type": kind, "text": text})
            current_para.clear()

    state = "para"
    for line in raw.split("\n"):
        stripped = line.strip()
        if not stripped:
            flush(state)
            state = "para"
            continue
        # Skip footnote definitions and standalone image lines (handled
        # via inline_ducks not the raw markdown image syntax)
        if re.match(r"^\[\^\d+\]:", stripped):
            continue
        if stripped.startswith("![") or stripped.startswith("!["):
            flush(state)
            continue  # images on the chapter page are not shown inline on the homepage
        if stripped.startswith("## "):
            flush(state)
            blocks.append({"type": "heading", "text": stripped[3:].strip()})
            state = "para"
            continue
        if stripped.startswith("> "):
            if state != "quote":
                flush(state)
                state = "quote"
            current_para.append(stripped[2:].strip())
            continue
        if stripped == ">":
            continue
        if state != "para":
            flush(state)
            state = "para"
        current_para.append(stripped)
    flush(state)

    preview = ""
    for b in blocks:
        if b["type"] in ("para", "quote") and len(b["text"]) > 60:
            preview = b["text"][:240].rsplit(" ", 1)[0] + "…"
            break
    return preview, blocks


def render_chapter_html(blocks, inline_ducks=None):
    """inline_ducks: dict mapping section heading -> duck dict or tuple."""
    inline_ducks = inline_ducks or {}
    parts = []
    for b in blocks:
        text = b["text"]
        if b["type"] == "heading":
            if b["text"] in inline_ducks:
                d = inline_ducks[b["text"]]
                parts.append(duck(d["label"], d.get("image"), d.get("url")))
            parts.append(f'<span class="section-head">{text}</span>')
        elif b["type"] == "quote":
            parts.append(f'<span class="pull-quote">“{text}”</span>')
        else:
            parts.append(text)
    return " ".join(parts)


# ---------- chapter map ----------
TITLE_PAGES = "/assets/images/title-pages"

CHAPTERS = [
    {
        "md": None,  # cover has its own special body
        "url": "/thesis/cover/",
        "label": "Cover",
        "before": [
            {"label": "Cover — The Yellow Duck Phenomenon", "image": f"{TITLE_PAGES}/Cover.png", "url": "/thesis/cover/"},
        ],
        "inline_ducks": {},
    },
    {
        "md": "introduction.md",
        "url": "/thesis/introduction/",
        "label": "Introducing the Yellow Duck",
        "before": [
            {"label": "Introducing the Yellow Duck — title page", "image": f"{TITLE_PAGES}/Introducing the Yellow Duck.png", "url": "/thesis/introduction/"},
        ],
        "inline_ducks": {},
    },
    {
        "md": "chapter-1.md",
        "url": "/thesis/chapter-1/",
        "label": "Chapter I — A fixed set of rules",
        "before": [
            {"label": "Chapter I — A fixed set of rules", "image": f"{TITLE_PAGES}/01_A fixed set of rules.png", "url": "/thesis/chapter-1/"},
        ],
        "inline_ducks": {},
    },
    {
        "md": "chapter-2.md",
        "url": "/thesis/chapter-2/",
        "label": "Chapter II — A fixed set of rules on art",
        "before": [
            {"label": "Chapter II — A fixed set of rules on art", "image": f"{TITLE_PAGES}/02_A fixed set of rules on art.png", "url": "/thesis/chapter-2/"},
        ],
        "inline_ducks": {},
    },
    {
        "md": "chapter-3.md",
        "url": "/thesis/chapter-3/",
        "label": "Chapter III — Explained by artworks",
        "before": [
            {"label": "Chapter III — A fixed set of rules on art explained by artworks", "image": f"{TITLE_PAGES}/03_A fixed set of rules on art explained by artworks.png", "url": "/thesis/chapter-3/"},
        ],
        "inline_ducks": {
            "A Transition From an Object-Oriented to a System-Oriented Culture": {
                "label": "Four-sided Vortex — Robert Smithson, 1967",
                "image": "/assets/images/defff/Smithson.jpg",
                "url": "/thesis/chapter-3/",
            },
            "Art Does Not Reside in Material Entities": {
                "label": "Condensation Cube — Hans Haacke, 1963–65",
                "image": "/assets/images/defff/63_65condensationcube2_347x500jpg.jpg",
                "url": "/thesis/chapter-3/",
            },
            "Art is Not Autonomous": {
                "label": "Measurement: Room — Mel Bochner, 1969",
                "image": "/assets/images/defff/Mel_Brochner_measurment_room.jpg",
                "url": "/thesis/chapter-3/",
            },
            "Art is Conceptual Focus": {
                "label": "Homes for America — Dan Graham, 1966–67",
                "image": "/assets/images/defff/homes_for_america_002.jpg",
                "url": "/thesis/chapter-3/",
            },
            "No Definition or Theory of Art Can Be Historically Unvarying": {
                "label": "The Bowery in Two Inadequate Descriptive Systems — Martha Rosler, 1974–75",
                "image": "/assets/images/defff/rosler_004.jpg",
                "url": "/thesis/chapter-3/",
            },
        },
    },
    {
        "md": "approach.md",
        "url": "/thesis/approach/",
        "label": "Approach",
        "before": [
            {"label": "Approach", "image": f"{TITLE_PAGES}/Approach.png", "url": "/thesis/approach/"},
        ],
        "inline_ducks": {},
    },
    {
        "md": "chapter-4.md",
        "url": "/thesis/chapter-4/",
        "label": "Chapter IV — Composition of Thoughts",
        "before": [
            {"label": "Chapter IV — Composition of Thoughts", "image": f"{TITLE_PAGES}/04_Composition of Thoughts.png", "url": "/thesis/chapter-4/"},
        ],
        "inline_ducks": {},
    },
    {
        "md": "chapter-5.md",
        "url": "/thesis/chapter-5/",
        "label": "Chapter V — Finding the Yellow Duck",
        "before": [
            {"label": "Chapter V — Finding the Yellow Duck", "image": f"{TITLE_PAGES}/05_Finding the Yellow Duck.png", "url": "/thesis/chapter-5/"},
        ],
        "inline_ducks": {},
    },
    {
        "md": "conclusion.md",
        "url": "/thesis/conclusion/",
        "label": "Concluding That Ducks Never Remain Yellow",
        "before": [
            {"label": "Concluding That Ducks Never Remain Yellow", "image": f"{TITLE_PAGES}/Concluding that ducks never remain yellow.png", "url": "/thesis/conclusion/"},
        ],
        "inline_ducks": {},
    },
    {
        "md": "appendix.md",
        "url": "/thesis/appendix/",
        "label": "Appendix — Jack Burnham, Systems Esthetics",
        "before": [
            {"label": "Appendix — Jack Burnham, Systems Esthetics", "image": f"{TITLE_PAGES}/Appendix.png", "url": "/thesis/appendix/"},
        ],
        "inline_ducks": {},
    },
    {
        "md": "bibliography.md",
        "url": "/thesis/bibliography/",
        "label": "Bibliography",
        "before": [
            {"label": "Bibliography", "image": f"{TITLE_PAGES}/Bibliography.png", "url": "/thesis/bibliography/"},
        ],
        "inline_ducks": {},
    },
    {
        "md": "colofon.md",
        "url": "/thesis/colofon/",
        "label": "Colofon",
        "before": [
            {"label": "Colofon", "image": f"{TITLE_PAGES}/Colofon.png", "url": "/thesis/colofon/"},
        ],
        "inline_ducks": {},
    },
]


def build():
    body_parts = []
    for ch in CHAPTERS:
        for d in ch["before"]:
            body_parts.append(duck(d["label"], d.get("image"), d.get("url")))

        if ch["md"] is None:
            # Cover — no body text; the duck before it is enough
            continue

        preview, blocks = parse_md(THESIS / ch["md"])
        inner = render_chapter_html(blocks, ch["inline_ducks"])

        body_parts.append(
            '<span class="home-section" '
            f'data-label="{html_attr(ch["label"])}" '
            f'data-url="{img_url(ch["url"])}" '
            f'data-text="{html_attr(preview)}">'
            f'{inner}'
            '</span>'
        )

    body = "\n      ".join(body_parts)

    page = f"""---
layout: false
---
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>The Yellow Duck Phenomenon — ways to order — Lyske Gais</title>
  <meta name="description" content="A Master's thesis in Applied Art connecting Systems Theory, Conceptual Art, and art practice. Sandberg Institute, Amsterdam, 2012. By Lyske Gais.">
  <link rel="stylesheet" href="{{{{ "/assets/css/style.css" | url }}}}">
  <link rel="stylesheet" href="{{{{ "/assets/css/home.css" | url }}}}">
</head>
<body class="home">

  <div class="home-canvas">
    <div class="home-text">

      <div class="home-title-block">
        <div class="home-title-main">The Yellow Duck Phenomenon</div>
        <div class="home-title-line2">
          <span class="home-title-sub">ways to order</span>
          <span class="home-title-sep"> — </span>
          <span class="home-title-author">Lyske Gais</span>
        </div>
      </div>

      {body}

    </div><!-- .home-text -->
  </div><!-- .home-canvas -->

  <!-- Magnifier overlay -->
  <div class="text-magnifier" id="text-magnifier" role="tooltip">
    <div class="magnifier-label" id="magnifier-label"></div>
    <img class="magnifier-image" id="magnifier-image" alt="" hidden>
    <div class="magnifier-text" id="magnifier-text"></div>
    <a class="magnifier-cta" id="magnifier-cta" href="#"></a>
  </div>

  <!-- Bottom nav -->
  <nav class="home-nav">
    <a href="{{{{ "/thesis/introduction/" | url }}}}">Read the text</a>
    <a href="{{{{ "/projects/" | url }}}}">View projects</a>
  </nav>

  <script src="{{{{ "/assets/js/home.js" | url }}}}"></script>
</body>
</html>
"""
    OUT.write_text(page, encoding="utf-8")
    print(f"Wrote {OUT} ({len(page):,} bytes)")


if __name__ == "__main__":
    build()
