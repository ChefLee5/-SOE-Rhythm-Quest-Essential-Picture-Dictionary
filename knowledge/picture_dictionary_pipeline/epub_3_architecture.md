# EPUB 3.3 Architecture

The Picture Dictionary is packaged as a standards-compliant **EPUB 3.3** file.

> **GitHub source:** https://github.com/ChefLee5/SOE-Orginal-Repository-/tree/main/ebook
> **Final size:** ~36.5 MB
> **Last verified:** April 2026

## Package Structure

```
soe-rhythm-quest-dictionary.epub (ZIP)
├── mimetype                           ← "application/epub+zip" (uncompressed, first entry)
├── META-INF/
│   └── container.xml                  ← Points to OEBPS/content.opf
└── OEBPS/
    ├── content.opf                    ← Package manifest + spine order (29 KB)
    ├── pages/                         ← 160 XHTML pages
    │   ├── cover.xhtml
    │   ├── frontmatter.xhtml
    │   ├── nav.xhtml                  ← EPUB3 navigation document (TOC)
    │   ├── land1-*.xhtml              ← 20 Land 1 pages
    │   ├── land2-*.xhtml              ← 19 Land 2 pages
    │   ├── land3-*.xhtml              ← 20 Land 3 pages
    │   ├── land4-*.xhtml              ← 19 Land 4 pages
    │   ├── land5-*.xhtml              ← 17 Land 5 pages
    │   ├── land6-*.xhtml              ← 19 Land 6 pages
    │   ├── land7-*.xhtml              ← 18 Land 7 pages
    │   └── back_*.xhtml               ← 25 back matter pages
    ├── images/
    │   └── *.jpg                      ← 157 scene illustrations (compressed)
    ├── styles/
    │   └── dictionary.css             ← Full design system
    └── fonts/
        ├── FredokaOne-Regular.woff2   ← Display/header font
        ├── Nunito-Regular.woff2
        ├── Nunito-SemiBold.woff2
        └── Nunito-Bold.woff2
```

## Content Source Pipeline

```
ebook/content/*.md (15 Markdown files, 583 KB total)
        ↓
  regen_pages.py          ← Converts MD scenes → XHTML
        ↓
  OEBPS/pages/*.xhtml     ← 160 generated XHTML pages
        ↓
  build_epub.py           ← Zips OEBPS + META-INF → .epub
        ↓
  output/*.epub           ← Final deliverable (36.5 MB)
```

## Scripts (16 files in `ebook/scripts/`)

| Script | Purpose |
|--------|---------|
| `regen_pages.py` | Regenerates specific XHTML pages from MD source |
| `build_epub.py` | Packages OEBPS + META-INF into EPUB ZIP |
| `audit_numbers.py` | Validates sequential numbering in MD scenes |
| `audit_crossref.py` | Cross-validates word counts (MD vs XHTML) |
| `audit_xhtml_pages.py` | Validates XHTML page structure |
| `validate_epub.py` | Full EPUB structure validation |
| `verify_epub.py` | Quick sanity check on built EPUB |
| `compress_images.py` | Batch compresses scene JPGs |
| `fix_opf_manifest.py` | Repairs content.opf manifest entries |
| `update_refs.py` | Updates cross-references |

Additional root-level scripts: `generate_pages.py` (20 KB, full page generator), `build_epub.py` (10 KB, extended builder), `audit.py` (2 KB).

## Distribution Targets

| Platform | Format | Notes |
|----------|--------|-------|
| Amazon KDP | EPUB 3 | May auto-convert to AZW3; test on Kindle Previewer |
| Apple Books | EPUB 3 | Native EPUB support; best rendering |
| Kobo | EPUB 3 | Native EPUB support |
| Google Play Books | EPUB 3 | Upload via Play Books Partner Center |
| Direct download | EPUB 3 | Host on website or GitHub Releases |

## Local Preview (No EPUB Reader Needed)

```bash
python -m http.server 8080 --directory ebook/OEBPS
# Browse: http://localhost:8080/pages/nav.xhtml
```
