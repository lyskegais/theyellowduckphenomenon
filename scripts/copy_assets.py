"""Copy fresh title-page images from Dropbox into the project, and copy
the 5 artwork JPGs from the extracted EPUB into src/assets/images/defff/.
"""
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# 1. Replace title pages
TITLE_SRC = Path(r"C:\Users\studi\Dropbox (Personal)\• Overhead\WEBSITE\The Yellow Duck\Claude Duck\Title pages")
TITLE_DST = ROOT / "src" / "assets" / "images" / "title-pages"

if TITLE_DST.exists():
    for old in TITLE_DST.iterdir():
        if old.is_file():
            old.unlink()
TITLE_DST.mkdir(parents=True, exist_ok=True)

copied = 0
for src in TITLE_SRC.glob("*.png"):
    dst = TITLE_DST / src.name
    shutil.copy2(src, dst)
    copied += 1
print(f"Copied {copied} title page images to {TITLE_DST}")

# 2. Copy 5 EPUB artwork images to defff/
EPUB_IMG = ROOT / "epub_extracted" / "OEBPS" / "image"
DEFFF = ROOT / "src" / "assets" / "images" / "defff"
DEFFF.mkdir(parents=True, exist_ok=True)
copied = 0
for src in EPUB_IMG.glob("*"):
    if src.suffix.lower() in (".jpg", ".jpeg", ".png") and src.name != "1.png":
        dst = DEFFF / src.name
        shutil.copy2(src, dst)
        copied += 1
        print(f"  defff/{src.name}")
print(f"Copied {copied} artwork images to {DEFFF}")
