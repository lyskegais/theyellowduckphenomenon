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

    blocks is a list of dicts: {"type": "para"|"heading"|"quote", "text": "..."}.
    """
    raw = path.read_text(encoding="utf-8")
    # Strip frontmatter
    raw = re.sub(r"^---\n.*?\n---\n", "", raw, count=1, flags=re.DOTALL)

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
        if not line.strip():
            flush(state)
            state = "para"
            continue
        if line.startswith("## "):
            flush(state)
            blocks.append({"type": "heading", "text": line[3:].strip()})
            state = "para"
            continue
        if line.startswith("> "):
            if state != "quote":
                flush(state)
                state = "quote"
            current_para.append(line[2:].strip())
            continue
        if line.strip() == ">":
            continue
        if state != "para":
            flush(state)
            state = "para"
        current_para.append(line.strip())
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
CHAPTERS = [
    {
        "md": "introduction.md",
        "url": "/thesis/introduction/",
        "label": "Introducing the Yellow Duck",
        "before": [
            {
                "label": "Introduction — title page",
                "image": "/assets/images/title-pages/Introduction.png",
                "url": "/thesis/introduction/",
            },
        ],
        "inline_ducks": {},
    },
    {
        "md": "chapter-1.md",
        "url": "/thesis/chapter-1/",
        "label": "Chapter I — A fixed set of rules",
        "before": [
            {
                "label": "Part I — A fixed set of rules",
                "image": "/assets/images/title-pages/Part_I.png",
                "url": "/thesis/chapter-1/",
            },
            {
                "label": "Chapter I — title page",
                "image": "/assets/images/title-pages/Chapter_1.png",
                "url": "/thesis/chapter-1/",
            },
        ],
        "inline_ducks": {
            "Definition of System": {
                "label": "General System Theory — Ludwig von Bertalanffy, 1968",
                "url": "/thesis/chapter-1/",
            },
        },
    },
    {
        "md": "chapter-2.md",
        "url": "/thesis/chapter-2/",
        "label": "Chapter II — A fixed set of rules on art",
        "before": [
            {
                "label": "Chapter II — title page",
                "image": "/assets/images/title-pages/Chapter_2.png",
                "url": "/thesis/chapter-2/",
            },
        ],
        "inline_ducks": {
            "Conceptual Art": {
                "label": "Statements — Lawrence Weiner, 1968",
                "url": "/thesis/chapter-2/",
            },
        },
    },
    {
        "md": "chapter-3.md",
        "url": "/thesis/chapter-3/",
        "label": "Chapter III — Explained by artworks",
        "before": [
            {
                "label": "Chapter III — title page",
                "image": "/assets/images/title-pages/Chapter_3.png",
                "url": "/thesis/chapter-3/",
            },
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
                "image": "/assets/images/defff/grahamhomes6667.jpg",
                "url": "/thesis/chapter-3/",
            },
            "No Definition or Theory of Art Can Be Historically Unvarying": {
                "label": "The Bowery in Two Inadequate Descriptive Systems — Martha Rosler, 1974–75",
                "image": "/assets/images/defff/Rosler.jpg",
                "url": "/thesis/chapter-3/",
            },
        },
    },
    {
        "md": "chapter-4.md",
        "url": "/thesis/chapter-4/",
        "label": "Chapter IV — Composition of Thoughts",
        "before": [
            {
                "label": "Part II — Composition",
                "image": "/assets/images/title-pages/Part_II.png",
                "url": "/thesis/chapter-4/",
            },
            {
                "label": "Chapter IV — title page",
                "url": "/thesis/chapter-4/",
            },
        ],
        "inline_ducks": {
            "System": {
                "label": "Vorm — Lyske Gais",
                "image": "/assets/images/defff/Vorm.jpg",
                "url": "/projects/",
            },
        },
    },
    {
        "md": "chapter-5.md",
        "url": "/thesis/chapter-5/",
        "label": "Chapter V — Finding the Yellow Duck",
        "before": [
            {
                "label": "Chapter V — title page",
                "url": "/thesis/chapter-5/",
            },
        ],
        "inline_ducks": {
            "Plan (Order)": {
                "label": "Lyske Gais — planning process",
                "image": "/assets/images/defff/F1010007.jpg",
                "url": "/projects/",
            },
        },
    },
    {
        "md": "conclusion.md",
        "url": "/thesis/conclusion/",
        "label": "Concluding That Ducks Never Remain Yellow",
        "before": [
            {
                "label": "Conclusion — title page",
                "url": "/thesis/conclusion/",
            },
        ],
        "inline_ducks": {},
    },
    {
        "md": "bibliography.md",
        "url": "/thesis/bibliography/",
        "label": "Bibliography",
        "before": [
            {
                "label": "Bibliography — title page",
                "url": "/thesis/bibliography/",
            },
        ],
        "inline_ducks": {},
    },
]


def build():
    body_parts = []
    for ch in CHAPTERS:
        for d in ch["before"]:
            body_parts.append(duck(d["label"], d.get("image"), d.get("url")))

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
    <a href="{{{{ "/thesis/introduction/" | url }}}}">Read the thesis</a>
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
