# Build Pipeline & Automation Scripts

Full reference for the EPUB build pipeline and all automation scripts.

> **Source:** `SOE-Orginal-Repository/ebook/scripts/` (16 files)
> **Root scripts:** `SOE-Orginal-Repository/ebook/generate_pages.py`, `build_epub.py`, `audit.py`

---

## Full Rebuild Workflow

Run this sequence after any content changes:

```bash
# Step 1: Validate MD source (sequential numbering, no gaps)
python ebook/scripts/audit_numbers.py
# Output: ebook/scripts/audit_results.txt

# Step 2: Regenerate changed XHTML pages from Markdown
python ebook/scripts/regen_pages.py
# Edit PAGES_TO_FIX dict to target specific scenes

# Step 3: Cross-validate word counts (MD source = XHTML output)
python ebook/scripts/audit_crossref.py
# Expected: "TOTALS: MD Source = 4232 words | XHTML Pages = 4232 words | Difference = 0"

# Step 4: Build EPUB 3.3 package
python ebook/scripts/build_epub.py
# Output: ebook/output/soe-rhythm-quest-dictionary.epub

# Step 5: Verify EPUB integrity
python ebook/scripts/verify_epub.py
# Checks: mimetype first, 160 pages, 157 images, 4 fonts, content.opf, nav.xhtml
```

---

## Script Inventory

### Core Build Scripts

| Script | Location | Purpose |
|--------|----------|---------|
| `generate_pages.py` | `ebook/` (root) | **Full page generator** — converts ALL content/*.md → OEBPS/pages/*.xhtml (20 KB) |
| `regen_pages.py` | `ebook/scripts/` | **Incremental regenerator** — converts specific changed scenes only (9 KB) |
| `build_epub.py` | `ebook/scripts/` | Packages OEBPS/ + META-INF/ → valid EPUB3 ZIP (1.8 KB) |
| `build_epub.py` | `ebook/` (root) | **Extended builder** — full packaging with extra validations (10 KB) |
| `compress_images.py` | `ebook/scripts/` | Batch compresses scene illustration JPGs (5.5 KB) |
| `fix_opf_manifest.py` | `ebook/scripts/` | Repairs content.opf manifest entries (1.9 KB) |
| `update_refs.py` | `ebook/scripts/` | Updates cross-references between pages (0.6 KB) |

### Audit & Validation Scripts

| Script | Location | Purpose |
|--------|----------|---------|
| `audit_numbers.py` | `ebook/scripts/` | Validates sequential word numbering in each MD scene (6.6 KB) |
| `audit_crossref.py` | `ebook/scripts/` | Cross-validates word counts between MD and XHTML (8.8 KB) |
| `audit_xhtml_pages.py` | `ebook/scripts/` | Validates XHTML page structure and encoding (6 KB) |
| `validate_epub.py` | `ebook/scripts/` | Full EPUB structure validation (4.4 KB) |
| `verify_epub.py` | `ebook/scripts/` | Quick sanity check on built EPUB (1.6 KB) |
| `audit.py` | `ebook/` (root) | Root-level audit runner (2.1 KB) |

### Audit Results (committed)

| File | Contents |
|------|----------|
| `audit_results.txt` | Numbering validation results (13 KB) |
| `crossref_results.txt` | Word count cross-reference (6.7 KB) |
| `crossref_final.txt` | Final cross-reference pass (3.5 KB) |
| `regen_results.txt` | Page regeneration log (2 KB) |
| `validation_results.txt` | EPUB validation results (1.2 KB) |
| `xhtml_audit_results.txt` | XHTML structure audit (10 KB) |

---

## regen_pages.py Usage

To regenerate specific scenes after editing Markdown:

```python
# Edit the PAGES_TO_FIX dict in regen_pages.py:
PAGES_TO_FIX = {
    ("land3_terrasol.md", 7): "land3-silas-vestas-cottage-outside.xhtml",
    # (markdown_file, scene_number): xhtml_filename
}
```

Then run: `python ebook/scripts/regen_pages.py`

---

## Known Quirks

- **Apostrophe encoding**: `audit_crossref.py` may flag `'` (MD) vs `&#x27;` (XHTML) as mismatches. This is cosmetic — both render identically in EPUB readers.
- **images_backup/**: `build_epub.py` skips this directory if present.
- **Two build_epub.py files**: The root version (10 KB) is the extended builder; the scripts/ version (1.8 KB) is the minimal packager.
