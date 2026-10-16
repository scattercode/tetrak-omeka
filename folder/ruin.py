#!/usr/bin/env python3
"""Make the deliberately ruined scan for tutorials/a-folder-of-scans.md.

Takes the Inside Facts front page from the Los Angeles collection and makes
it look like a bad photocopy of a bad photocopy: shrunk to a quarter and
blown back up, blurred, its contrast flattened, peppered with specks and
saved as a low-quality JPEG. Tetrak's quality gate should send it to triage,
and does: it scores 0.0724 with auto-local in Tetrak 5.14.1, against a
threshold of 0.10.

The output is committed beside this script, so the tutorial needs nothing
but the file. This is the record of how it was made, and makes it again
byte for byte with the same Pillow (12.3.0).

Prerequisites: Pillow, which Tetrak's virtual environment has.

Usage:
    python folder/ruin.py
"""

import random
from pathlib import Path

from PIL import Image, ImageEnhance, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "collections/los-angeles-ephemera/inside-facts-1930-cover.jpg"
OUTPUT = Path(__file__).resolve().parent / "inside-facts-1930-cover-ruined.jpg"

page = Image.open(SOURCE).convert("L")
width, height = page.size
page = page.resize((width // 4, height // 4), Image.BILINEAR)
page = page.filter(ImageFilter.GaussianBlur(2.0))
page = ImageEnhance.Contrast(page).enhance(0.35)
page = page.resize((width, height), Image.BILINEAR)

random.seed(1)
pixels = page.load()
for _ in range(width * height // 12):
    x, y = random.randrange(width), random.randrange(height)
    pixels[x, y] = random.choice((0, 255))

page.save(OUTPUT, quality=20)
print(f"Wrote {OUTPUT.relative_to(ROOT)}")
