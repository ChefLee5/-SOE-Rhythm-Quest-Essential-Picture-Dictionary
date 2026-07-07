"""Verify the built EPUB package structure.

Usage: py ebook/scripts/verify_epub.py [path-to-epub]
Defaults to ebook/output/soe-rhythm-quest-dictionary.epub.
"""
import sys
import zipfile
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

DEFAULT_EPUB = Path(__file__).parent.parent / "output" / "soe-rhythm-quest-dictionary.epub"
epub_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_EPUB

epub = zipfile.ZipFile(epub_path, 'r')
names = epub.namelist()
print(f'EPUB: {epub_path}')
print(f'Total files in EPUB: {len(names)}')
print(f'First entry: {names[0]} (must be mimetype)')

mimetype_info = epub.getinfo(names[0])
mimetype_stored = mimetype_info.compress_type == zipfile.ZIP_STORED
print(f'mimetype stored uncompressed: {mimetype_stored}')

pages = [n for n in names if n.startswith('OEBPS/pages/') and n.endswith('.xhtml')]
images = [n for n in names if n.startswith('OEBPS/images/') and n.endswith('.jpg')]
fonts = [n for n in names if n.startswith('OEBPS/fonts/')]
print(f'XHTML pages: {len(pages)}')
print(f'Images: {len(images)}')
print(f'Fonts: {len(fonts)}')

checks = {
    'content.opf': 'OEBPS/content.opf' in names,
    'nav.xhtml': 'OEBPS/pages/nav.xhtml' in names,
    'dictionary.css': 'OEBPS/styles/dictionary.css' in names,
    'META-INF/container.xml': 'META-INF/container.xml' in names,
    'mimetype first': names[0] == 'mimetype',
    'mimetype stored': mimetype_stored,
}
for label, ok in checks.items():
    print(f'  {"OK " if ok else "FAIL"} {label}')

epub.close()
if all(checks.values()):
    print('\nEPUB package is valid!')
else:
    print('\nEPUB package FAILED verification.')
    sys.exit(1)
