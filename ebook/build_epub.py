#!/usr/bin/env python3
"""
SOE RHYTHM QUEST: ESSENTIAL PICTURE DICTIONARY
EPUB Build Script

This script packages the XHTML, CSS, and content files into a
valid EPUB 3 file. It also documents the pagination strategy
for generating the remaining 5 Lands.

Usage:
  python build_epub.py
  python build_epub.py --count
  python build_epub.py --strategy

Output:
  SOE_Essential_Picture_Dictionary.epub
"""

import os
import sys
import re
import zipfile
from pathlib import Path

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ─── Configuration ───────────────────────────────────────────

EBOOK_DIR = Path(__file__).parent
OEBPS_DIR = EBOOK_DIR / "OEBPS"
PAGES_DIR = OEBPS_DIR / "pages"
STYLES_DIR = OEBPS_DIR / "styles"
CONTENT_DIR = EBOOK_DIR / "content"
OUTPUT_FILE = EBOOK_DIR / "SOE_Essential_Picture_Dictionary.epub"

# File reading order (spine) — dynamically built from pages/ directory
NAV_FILE = "nav.xhtml"
STATIC_PAGES = ["cover.xhtml", "frontmatter.xhtml"]


def get_all_pages():
    """Discover all land*.xhtml and back_*.xhtml pages and sort them properly."""
    land_pages = []
    back_pages = []
    for f in PAGES_DIR.glob("land*.xhtml"):
        land_pages.append(f.name)
    for f in PAGES_DIR.glob("back_*.xhtml"):
        back_pages.append(f.name)
    # Sort land pages by land number then alphabetically within each land
    def land_sort_key(name):
        match = re.match(r'land(\d+)-', name)
        land_num = int(match.group(1)) if match else 99
        return (land_num, name)
    land_pages = sorted(land_pages, key=land_sort_key)
    # Sort back matter pages alphabetically
    back_pages = sorted(back_pages)
    return land_pages + back_pages


def build_epub():
    """
    Build a valid EPUB 3 file from the OEBPS directory.

    EPUB structure:
      mimetype          (first entry, stored uncompressed)
      META-INF/
        container.xml
      OEBPS/
        content.opf
        styles/dictionary.css
        pages/*.xhtml
    """

    print("═" * 60)
    print("  SOE Rhythm Quest: Essential Picture Dictionary")
    print("  Building EPUB...")
    print("═" * 60)

    # Validate required files exist
    required_files = [
        EBOOK_DIR / "mimetype",
        EBOOK_DIR / "META-INF" / "container.xml",
        OEBPS_DIR / "content.opf",
        STYLES_DIR / "dictionary.css",
        PAGES_DIR / NAV_FILE,
    ]

    for f in required_files:
        if not f.exists():
            print(f"  ❌ Missing required file: {f}")
            sys.exit(1)

    # Build dynamic page list
    land_pages = get_all_pages()
    all_pages = STATIC_PAGES + land_pages

    # Remove old output if exists
    if OUTPUT_FILE.exists():
        OUTPUT_FILE.unlink()
        print(f"  🗑️  Removed old: {OUTPUT_FILE.name}")

    # Build the ZIP/EPUB
    with zipfile.ZipFile(OUTPUT_FILE, 'w') as epub:

        # 1. mimetype MUST be the first entry, stored (not compressed)
        mimetype_path = EBOOK_DIR / "mimetype"
        epub.write(mimetype_path, "mimetype", compress_type=zipfile.ZIP_STORED)
        print("  ✅ mimetype (stored, uncompressed)")

        # 2. META-INF/container.xml
        container_path = EBOOK_DIR / "META-INF" / "container.xml"
        epub.write(container_path, "META-INF/container.xml")
        print("  ✅ META-INF/container.xml")

        # 3. content.opf
        opf_path = OEBPS_DIR / "content.opf"
        epub.write(opf_path, "OEBPS/content.opf")
        print("  ✅ OEBPS/content.opf")

        # 4. Stylesheet
        css_path = STYLES_DIR / "dictionary.css"
        epub.write(css_path, "OEBPS/styles/dictionary.css")
        print("  ✅ OEBPS/styles/dictionary.css")

        # 5. Navigation
        nav_path = PAGES_DIR / NAV_FILE
        epub.write(nav_path, f"OEBPS/pages/{NAV_FILE}")
        print(f"  ✅ OEBPS/pages/{NAV_FILE}")

        # 6. All content pages (static + land pages)
        for page in all_pages:
            page_path = PAGES_DIR / page
            if page_path.exists():
                epub.write(page_path, f"OEBPS/pages/{page}")
                print(f"  ✅ OEBPS/pages/{page}")
            else:
                print(f"  ⚠️  Skipping missing: {page}")

        # 7. Any images in OEBPS/images/
        images_dir = OEBPS_DIR / "images"
        if images_dir.exists():
            for img in images_dir.iterdir():
                if img.is_file():
                    epub.write(img, f"OEBPS/images/{img.name}")
                    print(f"  ✅ OEBPS/images/{img.name}")

    file_size = OUTPUT_FILE.stat().st_size / 1024
    print()
    print("═" * 60)
    print(f"  ✅ EPUB built successfully!")
    print(f"  📁 Output: {OUTPUT_FILE}")
    print(f"  📦 Size: {file_size:.1f} KB")
    print("═" * 60)


def count_vocabulary():
    """
    Count total vocabulary words across all Markdown content files.
    """
    total = 0
    for md_file in sorted(CONTENT_DIR.glob("*.md")):
        count = 0
        with open(md_file, "r", encoding="utf-8") as f:
            for line in f:
                # Count table rows that start with "| [number]"
                if re.match(r'^\|\s*\d+\s*\|', line.strip()):
                    count += 1
        total += count
        print(f"  📖 {md_file.name}: {count} words")

    print(f"\n  📊 Total vocabulary: {total} words")
    return total


# ─── Pagination Strategy ─────────────────────────────────────

PAGINATION_STRATEGY = """
═══════════════════════════════════════════════════════════════
 PAGINATION STRATEGY: 4,162-Word Picture Dictionary — COMPLETE
═══════════════════════════════════════════════════════════════

 Current State: ALL CONTENT COMPLETE ✅

 ┌──────────────────────┬─────────────┬─────────────────────┐
 │ Land                 │ Word Count  │ Status              │
 ├──────────────────────┼─────────────┼─────────────────────┤
 │ 1. Harmonia          │ 620         │ ✅ Complete         │
 │ 2. Numeria           │ 510         │ ✅ Complete         │
 │ 3. Terrasol          │ 585         │ ✅ Complete         │
 │ 4. Aquaria           │ 485         │ ✅ Complete         │
 │ 5. Vitalis           │ 520         │ ✅ Complete         │
 │ 6. Luminosity        │ 425         │ ✅ Complete         │
 │ 7. Celestia          │ 390         │ ✅ Complete         │
 ├──────────────────────┼─────────────┼─────────────────────┤
 │ Sight Words          │ 90          │ ✅ Complete         │
 │ Action Verbs         │ 50          │ ✅ Complete         │
 │ Adjectives           │ 50          │ ✅ Complete         │
 │ A–Z Word Index       │ 120         │ ✅ Complete         │
 │ Visual Glossary      │ 100         │ ✅ Complete         │
 │ Parent & Teacher     │ 80          │ ✅ Complete         │
 │ ASL Alphabet         │ 37          │ ✅ Complete         │
 │ 100 Essential ASL    │ 100         │ ✅ Complete         │
 ├──────────────────────┼─────────────┼─────────────────────┤
 │ TOTAL                │ 4,162       │ ✅ COMPLETE         │
 └──────────────────────┴─────────────┴─────────────────────┘

 ═══ BUILD WORKFLOW ═══

 1. Generate XHTML pages from Markdown:
      python generate_pages.py

 2. Build EPUB:
      python build_epub.py

 ═══ CONVERTING EPUB → PDF ═══

 Using Calibre's command-line tool:

   ebook-convert SOE_Essential_Picture_Dictionary.epub \\
                 SOE_Essential_Picture_Dictionary.pdf \\
                 --pdf-page-size=letter \\
                 --pdf-default-font-size=11 \\
                 --pdf-mono-font-size=10

 Or use a browser: Open each XHTML page and Print → Save as PDF.

═══════════════════════════════════════════════════════════════
"""


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--count":
        print()
        count_vocabulary()
    elif len(sys.argv) > 1 and sys.argv[1] == "--strategy":
        print(PAGINATION_STRATEGY)
    else:
        build_epub()
        print()
        count_vocabulary()
