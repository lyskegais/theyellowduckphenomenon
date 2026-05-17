"""Extract the new EPUB into ./epub_extracted/ and list contents."""
import zipfile
from pathlib import Path
import shutil

EPUB = Path(r"C:\Users\studi\Dropbox (Personal)\• Overhead\WEBSITE\The Yellow Duck\Claude Duck\260517_The_Yellow_Duck_POCKET_for-web_v02.epub")
OUT = Path(__file__).resolve().parents[1] / "epub_extracted"

if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir(parents=True)

with zipfile.ZipFile(EPUB) as z:
    z.extractall(OUT)

for p in sorted(OUT.rglob("*")):
    if p.is_file():
        print(f"{p.stat().st_size:>10}  {p.relative_to(OUT)}")
