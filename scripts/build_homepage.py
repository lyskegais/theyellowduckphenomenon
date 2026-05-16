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


def duck(label: str) -> str:
    return (
        f'<img class="duck" src="{DUCK_SRC}" alt="" '
        f'data-label="{html_attr(label)}">'
    )


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

    state = "para"  # para | quote
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
        # plain prose
        if state != "para":
            flush(state)
            state = "para"
        current_para.append(line.strip())
    flush(state)

    # Build preview from first prose para
    preview = ""
    for b in blocks:
        if b["type"] in ("para", "quote") and len(b["text"]) > 60:
            preview = b["text"][:240].rsplit(" ", 1)[0] + "…"
            break
    return preview, blocks


def render_chapter_html(blocks, inline_ducks=None):
    """Render the blocks as inline HTML for inside a .home-section span.

    inline_ducks: dict mapping section heading -> duck label to insert
                  right BEFORE the heading.
    """
    inline_ducks = inline_ducks or {}
    parts = []
    for b in blocks:
        text = b["text"]
        if b["type"] == "heading":
            if b["text"] in inline_ducks:
                parts.append(duck(inline_ducks[b["text"]]))
            parts.append(
                f'<span class="section-head">{text}</span>'
            )
        elif b["type"] == "quote":
            parts.append(
                f'<span class="pull-quote">“{text}”</span>'
            )
        else:
            parts.append(text)
    return " ".join(parts)


# ---------- chapter map ----------
CHAPTERS = [
    {
        "md": "introduction.md",
        "url": "/thesis/introduction/",
        "label": "Introducing the Yellow Duck",
        "before": [("Introduction — title page",)],
        "inline_ducks": {},
    },
    {
        "md": "chapter-1.md",
        "url": "/thesis/chapter-1/",
        "label": "Chapter I — A fixed set of rules",
        "before": [
            ("Part I — A fixed set of rules",),
            ("Chapter I — title page",),
        ],
        "inline_ducks": {
            "Definition of System": "General System Theory — Ludwig von Bertalanffy, 1968",
        },
    },
    {
        "md": "chapter-2.md",
        "url": "/thesis/chapter-2/",
        "label": "Chapter II — A fixed set of rules on art",
        "before": [("Chapter II — title page",)],
        "inline_ducks": {
            "Conceptual Art": "Statements — Lawrence Weiner, 1968",
        },
    },
    {
        "md": "chapter-3.md",
        "url": "/thesis/chapter-3/",
        "label": "Chapter III — Explained by artworks",
        "before": [("Chapter III — title page",)],
        "inline_ducks": {
            "A Transition From an Object-Oriented to a System-Oriented Culture":
                "Four-sided Vortex — Robert Smithson, 1967",
            "Art Does Not Reside in Material Entities":
                "Condensation Cube — Hans Haacke, 1963–65",
            "Art is Not Autonomous":
                "Measurement: Room — Mel Bochner, 1969",
            "Art is Conceptual Focus":
                "Homes for America — Dan Graham, 1966–67",
            "No Definition or Theory of Art Can Be Historically Unvarying":
                "The Bowery in Two Inadequate Descriptive Systems — Martha Rosler, 1974–75",
        },
    },
    {
        "md": "chapter-4.md",
        "url": "/thesis/chapter-4/",
        "label": "Chapter IV — Composition of Thoughts",
        "before": [
            ("Part II — Composition",),
            ("Chapter IV — title page",),
        ],
        "inline_ducks": {
            "System": "Lyske Gais — work documentation",
        },
    },
    {
        "md": "chapter-5.md",
        "url": "/thesis/chapter-5/",
        "label": "Chapter V — Finding the Yellow Duck",
        "before": [("Chapter V — title page",)],
        "inline_ducks": {
            "Plan (Order)": "Lyske Gais — planning process",
        },
    },
    {
        "md": "conclusion.md",
        "url": "/thesis/conclusion/",
        "label": "Concluding That Ducks Never Remain Yellow",
        "before": [("Conclusion — title page",)],
        "inline_ducks": {},
    },
    {
        "md": "bibliography.md",
        "url": "/thesis/bibliography/",
        "label": "Bibliography",
        "before": [("Bibliography — title page",)],
        "inline_ducks": {},
    },
]


def build():
    body_parts = []
    for ch in CHAPTERS:
        # Insert title-page / divider ducks before chapter text
        for label_tuple in ch["before"]:
            body_parts.append(duck(label_tuple[0]))

        preview, blocks = parse_md(THESIS / ch["md"])
        inner = render_chapter_html(blocks, ch["inline_ducks"])

        body_parts.append(
            '<span class="home-section" '
            f'data-label="{html_attr(ch["label"])}" '
            f'data-url="{{{{ "{ch["url"]}" | url }}}}" '
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

      <span class="home-title-inline">The Yellow Duck Phenomenon</span>
      <span class="home-title-sub"> — ways to order — </span>
      <span class="home-title-author">Lyske Gais — </span>

      {body}

    </div><!-- .home-text -->
  </div><!-- .home-canvas -->

  <!-- Magnifier overlay -->
  <div class="text-magnifier" id="text-magnifier" role="tooltip">
    <div class="magnifier-label" id="magnifier-label"></div>
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
