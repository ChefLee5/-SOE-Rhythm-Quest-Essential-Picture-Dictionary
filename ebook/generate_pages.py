#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════
 MARKDOWN → XHTML PAGE GENERATOR
 Reads all land*.md content files and generates one XHTML page
 per sub-scene, plus updates content.opf and nav.xhtml.
═══════════════════════════════════════════════════════════════
"""

import os
import sys
import re
import html
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

EBOOK_DIR = Path(__file__).parent
CONTENT_DIR = EBOOK_DIR / "content"
PAGES_DIR = EBOOK_DIR / "OEBPS" / "pages"

# ─── Land Configuration ──────────────────────────────────────

LANDS = {
    1: {
        "name": "Harmonia",
        "icon": "🎵",
        "color": "#d4a843",
        "characters": "Kenji &amp; Aiko",
        "char_desc": '<strong>Kenji</strong> the Rhythm Keeper &amp; <strong>Aiko</strong> the Melody Weaver',
    },
    2: {
        "name": "Numeria",
        "icon": "🔢",
        "color": "#7fb685",
        "characters": "Kwame &amp; Octavia",
        "char_desc": '<strong>Kwame</strong> the Pattern Master &amp; <strong>Octavia</strong> the Data Dancer',
    },
    3: {
        "name": "Terrasol",
        "icon": "🌿",
        "color": "#10B981",
        "characters": "Silas &amp; Vesta",
        "char_desc": '<strong>Silas</strong> the Shape Finder &amp; <strong>Vesta</strong> the Space Navigator',
    },
    4: {
        "name": "Aquaria",
        "icon": "🌊",
        "color": "#2563EB",
        "characters": "Ronan &amp; Nerissa",
        "char_desc": '<strong>Ronan</strong> the Wave Rider &amp; <strong>Nerissa</strong> the Deep Diver',
    },
    5: {
        "name": "Vitalis",
        "icon": "🤸",
        "color": "#c4785a",
        "characters": "Felix &amp; Amara",
        "char_desc": '<strong>Felix</strong> the Body Guardian &amp; <strong>Amara</strong> the Wellness Guide',
    },
    6: {
        "name": "Luminosity",
        "icon": "📖",
        "color": "#d4897a",
        "characters": "Ezra &amp; Athena",
        "char_desc": '<strong>Ezra</strong> the Builder &amp; <strong>Athena</strong> the Wise',
    },
    7: {
        "name": "Celestia",
        "icon": "⏰",
        "color": "#9678c4",
        "characters": "Elias &amp; Selene",
        "char_desc": '<strong>Elias</strong> the Star Gazer &amp; <strong>Selene</strong> the Time Keeper',
    },
}

BACK_MATTER = {
    "back_sight_words": {
        "name": "Sight Words & High-Frequency Words",
        "icon": "📖",
        "color": "#e67e22",
        "characters": "All Rhythm Quest Heroes",
        "char_desc": '<strong>All Rhythm Quest Heroes</strong>',
        "prefix": "back",
    },
    "back_action_verbs": {
        "name": "Action Verbs Gallery",
        "icon": "💪",
        "color": "#e74c3c",
        "characters": "All Rhythm Quest Heroes",
        "char_desc": '<strong>All Rhythm Quest Heroes</strong>',
        "prefix": "back",
    },
    "back_adjectives": {
        "name": "Descriptive Words (Adjectives)",
        "icon": "🎨",
        "color": "#9b59b6",
        "characters": "All Rhythm Quest Heroes",
        "char_desc": '<strong>All Rhythm Quest Heroes</strong>',
        "prefix": "back",
    },
    "back_az_index": {
        "name": "A–Z Word Index",
        "icon": "🔤",
        "color": "#2c3e50",
        "characters": "All Rhythm Quest Heroes",
        "char_desc": '<strong>All Rhythm Quest Heroes</strong>',
        "prefix": "back",
    },
    "back_visual_glossary": {
        "name": "Visual Glossary",
        "icon": "👁️",
        "color": "#16a085",
        "characters": "All Rhythm Quest Heroes",
        "char_desc": '<strong>All Rhythm Quest Heroes</strong>',
        "prefix": "back",
    },
    "back_parent_teacher": {
        "name": "Parent & Teacher Guide",
        "icon": "🍎",
        "color": "#c0392b",
        "characters": "All Rhythm Quest Heroes",
        "char_desc": '<strong>All Rhythm Quest Heroes</strong>',
        "prefix": "back",
    },
    "back_asl_alphabet": {
        "name": "ASL Alphabet & Numbers",
        "icon": "🤟",
        "color": "#8B5CF6",
        "characters": "All Rhythm Quest Heroes",
        "char_desc": '<strong>All Rhythm Quest Heroes</strong>',
        "prefix": "back",
    },
    "back_asl_essential": {
        "name": "100 Essential ASL Signs",
        "icon": "🤟",
        "color": "#7C3AED",
        "characters": "All Rhythm Quest Heroes",
        "char_desc": '<strong>All Rhythm Quest Heroes</strong>',
        "prefix": "back",
    },
}


def slugify(text):
    """Convert scene title to a URL-friendly slug."""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s]+', '-', text.strip())
    text = re.sub(r'-+', '-', text)
    return text


def escape_xml(text):
    """Escape text for safe XML embedding."""
    return html.escape(text, quote=True).replace("'", "&#39;")


def parse_markdown(filepath):
    """
    Parse a land markdown file into structured data.
    Returns a list of scenes, each with:
      - scene_number
      - scene_title
      - scene_description
      - words: list of {num, word, phonetic, context}
      - tip_icon, tip_character, tip_text
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    scenes = []
    # Split on scene headers: ## Scene N: Title
    scene_blocks = re.split(r'^## Scene \d+:', content, flags=re.MULTILINE)

    for i, block in enumerate(scene_blocks):
        if i == 0:
            continue  # Skip the header before first scene

        lines = block.strip().split('\n')
        scene_title = lines[0].strip()
        scene_number = i

        # Extract description (italic text after title)
        description = ""
        for line in lines[1:]:
            stripped = line.strip()
            if stripped.startswith('*') and stripped.endswith('*'):
                description = stripped.strip('*').strip()
                break

        # Extract vocabulary rows from the table
        words = []
        for line in lines:
            # Match table rows: | num | word | phonetic | context | asl | translation |
            # First try 6-column (with ASL)
            match6 = re.match(
                r'^\|\s*(\d+)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*.*\|',
                line.strip()
            )
            # Fallback to 5-column (without ASL)
            match5 = re.match(
                r'^\|\s*(\d+)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*.*\|',
                line.strip()
            )
            if match6:
                words.append({
                    'num': match6.group(1).strip(),
                    'word': match6.group(2).strip(),
                    'phonetic': match6.group(3).strip(),
                    'context': match6.group(4).strip(),
                    'asl': match6.group(5).strip(),
                })
            elif match5:
                words.append({
                    'num': match5.group(1).strip(),
                    'word': match5.group(2).strip(),
                    'phonetic': match5.group(3).strip(),
                    'context': match5.group(4).strip(),
                    'asl': '',
                })

        # Extract character tip
        tip_text = ""
        tip_character = ""
        tip_icon = "💡"
        for line in lines:
            stripped = line.strip()
            # Look for blockquote tips: > **emoji Character's Tip:** *"text"*
            tip_match = re.match(
                r'^>\s*\*\*(.+?)\s+(.+?)[\u2019\']s\s+(?:Final\s+)?Tip:?\*\*\s*\*[\u201c\u201d"\']*(.+?)[\u201c\u201d"\']*\*',
                stripped
            )
            if tip_match:
                tip_icon = tip_match.group(1).strip()
                tip_character = tip_match.group(2).strip() + "'s Tip:"
                tip_text = tip_match.group(3).strip().rstrip('"').rstrip("'").rstrip("*")
                break

        if words:  # Only add scenes that have vocabulary
            scenes.append({
                'scene_number': scene_number,
                'scene_title': scene_title,
                'scene_description': description,
                'words': words,
                'tip_icon': tip_icon,
                'tip_character': tip_character,
                'tip_text': tip_text,
            })

    return scenes


def generate_xhtml(land_num, scene, land_config, prefix=None):
    """Generate a complete XHTML page for one scene."""
    slug = slugify(scene['scene_title'])
    if prefix:
        filename = f"{prefix}-{slug}.xhtml"
    else:
        filename = f"land{land_num}-{slug}.xhtml"

    word_count = len(scene['words'])

    # Check if any word in this scene has ASL data
    has_asl = any(w.get('asl', '') for w in scene['words'])

    # Build table rows
    rows = []
    for w in scene['words']:
        asl_cell = f'\n                <td class="col-asl">{escape_xml(w.get("asl", ""))}</td>' if has_asl else ''
        rows.append(f"""            <tr>
                <td class="col-num">{escape_xml(w['num'])}</td>
                <td class="col-word">{escape_xml(w['word'])}</td>
                <td class="col-phonetic">{escape_xml(w['phonetic'])}</td>
                <td class="col-context">{escape_xml(w['context'])}</td>{asl_cell}
                <td class="col-translation"></td>
            </tr>""")

    table_rows = '\n'.join(rows)

    # Character tip section
    tip_html = ""
    if scene['tip_text']:
        tip_html = f"""
    <!-- Character Tip -->
    <div class="character-tip">
        <span class="tip-icon">{scene['tip_icon']}</span>
        <p class="tip-character">{escape_xml(scene['tip_character'])}</p>
        <p class="tip-text">"{escape_xml(scene['tip_text'])}"</p>
    </div>"""

    # Illustration — check if actual image exists
    illust_desc = f"A richly detailed scene depicting '{scene['scene_title']}' with numbered callout markers (1\u2013{word_count}) indicating each vocabulary item's location in the scene."
    base_slug = filename.replace('.xhtml', '')
    img_file = PAGES_DIR.parent / 'images' / f'{base_slug}.png'
    if img_file.exists():
        illust_html = f"""
    <!-- Scene Illustration -->
    <div class="scene-illustration">
        <img src="../images/{base_slug}.png" alt="{escape_xml(illust_desc)}" class="scene-image" />
    </div>"""
    else:
        illust_html = f"""
    <!-- Illustration Area -->
    <div class="scene-illustration">
        <div class="placeholder-text">
            \U0001F5BC\uFE0F <strong>Illustration: {escape_xml(scene['scene_title'])}</strong><br />
            {escape_xml(illust_desc)}
        </div>
    </div>"""

    xhtml = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="en">

<head>
    <meta charset="UTF-8" />
    <title>{escape_xml(land_config['name'])} — {escape_xml(scene['scene_title'])}</title>
    <link rel="stylesheet" href="../styles/dictionary.css" type="text/css" />
    <style>
        :root {{
            --accent-color: {land_config['color']};
        }}
    </style>
</head>

<body>
    <!-- Land Header -->
    <div class="land-header">
        <div class="land-number">{'Back Matter' if prefix else f'Land {land_num} of 7'}</div>
        <h1 class="land-name"><span class="land-icon">{land_config['icon']}</span> {escape_xml(land_config['name'])}</h1>
        <p class="land-characters">Guided by {land_config['char_desc']}</p>
    </div>

    <!-- Scene Header -->
    <div class="scene-header">
        <h2 class="scene-title">Scene {scene['scene_number']}: {escape_xml(scene['scene_title'])}</h2>
        <p class="scene-description">{escape_xml(scene['scene_description'])}</p>
    </div>
{illust_html}

    <!-- Vocabulary Table -->
    <table class="vocab-table{' has-asl' if has_asl else ''}">
        <thead>
            <tr>
                <th class="col-num">#</th>
                <th>Word</th>
                <th>Pronunciation</th>
                <th>In the Story\u2026</th>
                {'<th>ASL Sign \U0001F91F</th>' if has_asl else ''}
                <th>My Language</th>
            </tr>
        </thead>
        <tbody>
{table_rows}
        </tbody>
    </table>
{tip_html}

</body>

</html>"""

    return filename, xhtml


def generate_content_opf(all_pages):
    """Generate a complete content.opf with all pages in the manifest and spine."""
    manifest_items = []
    spine_items = []

    # Static items
    manifest_items.append('    <item id="css" href="styles/dictionary.css" media-type="text/css"/>')
    manifest_items.append('    <item id="nav" href="pages/nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>')
    manifest_items.append('    <item id="cover" href="pages/cover.xhtml" media-type="application/xhtml+xml"/>')
    manifest_items.append('    <item id="frontmatter" href="pages/frontmatter.xhtml" media-type="application/xhtml+xml"/>')

    spine_items.append('    <itemref idref="cover"/>')
    spine_items.append('    <itemref idref="frontmatter"/>')

    for page in all_pages:
        item_id = page['filename'].replace('.xhtml', '').replace('-', '_')
        manifest_items.append(f'    <item id="{item_id}" href="pages/{page["filename"]}" media-type="application/xhtml+xml"/>')
        spine_items.append(f'    <itemref idref="{item_id}"/>')

    # Add image manifest items for all scene illustrations
    images_dir = PAGES_DIR.parent / 'images'
    if images_dir.exists():
        for img in sorted(images_dir.iterdir()):
            if img.is_file() and img.suffix.lower() in ('.png', '.jpg', '.jpeg', '.gif', '.svg'):
                img_id = 'img_' + img.stem.replace('-', '_').replace('.', '_')
                media_types = {
                    '.png': 'image/png',
                    '.jpg': 'image/jpeg',
                    '.jpeg': 'image/jpeg',
                    '.gif': 'image/gif',
                    '.svg': 'image/svg+xml',
                }
                media_type = media_types.get(img.suffix.lower(), 'image/png')
                manifest_items.append(f'    <item id="{img_id}" href="images/{img.name}" media-type="{media_type}"/>')

    # Compute total word count for description
    total_words = sum(p['word_count'] for p in all_pages)

    # Use current date for modified timestamp
    from datetime import datetime, timezone
    modified_date = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

    opf = f"""<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid" xml:lang="en">

  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="uid">soe-rhythm-quest-dictionary-2026</dc:identifier>
    <dc:title>SOE Rhythm Quest: Essential Picture Dictionary</dc:title>
    <dc:creator>The Sound of Essentials</dc:creator>
    <dc:language>en</dc:language>
    <dc:description>A {total_words:,}-word picture dictionary mapped to the Oxford Picture Dictionary scope, contextualized in the 7 Lands of the SOE Rhythm Quest universe.</dc:description>
    <dc:rights>© 2026 The Sound of Essentials. All rights reserved.</dc:rights>
    <meta property="dcterms:modified">{modified_date}</meta>
  </metadata>

  <manifest>
{chr(10).join(manifest_items)}
  </manifest>

  <spine>
{chr(10).join(spine_items)}
  </spine>

</package>"""

    return opf


def generate_nav_xhtml(lands_scenes, back_matter_pages=None):
    """Generate the nav.xhtml table of contents."""
    nav_items = []

    for land_num in sorted(lands_scenes.keys()):
        land_config = LANDS[land_num]
        scenes = lands_scenes[land_num]

        scene_links = []
        for page in scenes:
            scene_links.append(f'                <li><a href="{page["filename"]}">{page["scene_title"]}</a></li>')

        nav_items.append(f"""            <li>
                <a href="{scenes[0]['filename']}">{land_config['icon']} Land {land_num}: {land_config['name']}</a>
                <ol>
{chr(10).join(scene_links)}
                </ol>
            </li>""")

    # Back matter navigation
    if back_matter_pages:
        bm_links = []
        for page in back_matter_pages:
            bm_links.append(f'                <li><a href="{page["filename"]}">{page["scene_title"]}</a></li>')
        nav_items.append(f"""            <li>
                <a href="{back_matter_pages[0]['filename']}">📚 Back Matter</a>
                <ol>
{chr(10).join(bm_links)}
                </ol>
            </li>""")

    nav = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="en">
<head>
    <meta charset="UTF-8"/>
    <title>Table of Contents</title>
    <link rel="stylesheet" href="../styles/dictionary.css" type="text/css"/>
</head>
<body>
    <nav epub:type="toc" id="toc">
        <h1>Table of Contents</h1>
        <ol>
            <li><a href="cover.xhtml">Cover</a></li>
            <li><a href="frontmatter.xhtml">How to Use This Book</a></li>
{chr(10).join(nav_items)}
        </ol>
    </nav>
</body>
</html>"""

    return nav


def main():
    print("=" * 60)
    print("  XHTML Page Generator")
    print("  Converting Markdown → XHTML for all 7 Lands")
    print("=" * 60)

    all_pages = []  # flat list for content.opf
    lands_scenes = {}  # {land_num: [pages]} for nav

    # Process each land file
    for land_num in sorted(LANDS.keys()):
        land_config = LANDS[land_num]
        md_file = CONTENT_DIR / f"land{land_num}_{land_config['name'].lower()}.md"

        if not md_file.exists():
            print(f"  ⚠️  Missing: {md_file.name}")
            continue

        scenes = parse_markdown(md_file)
        print(f"\n  📖 Land {land_num}: {land_config['name']} — {len(scenes)} scenes")

        lands_scenes[land_num] = []

        for scene in scenes:
            filename, xhtml_content = generate_xhtml(land_num, scene, land_config)

            # Write XHTML file
            output_path = PAGES_DIR / filename
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(xhtml_content)

            word_count = len(scene['words'])
            print(f"     ✅ {filename} ({word_count} words)")

            page_info = {
                'filename': filename,
                'land_num': land_num,
                'scene_title': f"Scene {scene['scene_number']}: {scene['scene_title']}",
                'word_count': word_count,
            }
            all_pages.append(page_info)
            lands_scenes[land_num].append(page_info)

    # Process back matter files
    back_matter_pages = []
    for bm_key, bm_config in BACK_MATTER.items():
        md_file = CONTENT_DIR / f"{bm_key}.md"
        if not md_file.exists():
            print(f"  ⚠️  Missing back matter: {md_file.name}")
            continue

        scenes = parse_markdown(md_file)
        print(f"\n  📚 Back Matter: {bm_config['name']} — {len(scenes)} scenes")

        for scene in scenes:
            filename, xhtml_content = generate_xhtml(0, scene, bm_config, prefix=bm_key)

            output_path = PAGES_DIR / filename
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(xhtml_content)

            word_count = len(scene['words'])
            print(f"     ✅ {filename} ({word_count} words)")

            page_info = {
                'filename': filename,
                'land_num': 'back',
                'scene_title': scene['scene_title'],
                'word_count': word_count,
            }
            all_pages.append(page_info)
            back_matter_pages.append(page_info)

    # Generate content.opf
    opf_content = generate_content_opf(all_pages)
    opf_path = EBOOK_DIR / "OEBPS" / "content.opf"
    with open(opf_path, 'w', encoding='utf-8') as f:
        f.write(opf_content)
    print(f"\n  ✅ content.opf updated ({len(all_pages)} pages in manifest)")

    # Generate nav.xhtml
    nav_content = generate_nav_xhtml(lands_scenes, back_matter_pages)
    nav_path = PAGES_DIR / "nav.xhtml"
    with open(nav_path, 'w', encoding='utf-8') as f:
        f.write(nav_content)
    print(f"  ✅ nav.xhtml updated (7 lands + back matter, {len(all_pages)} scenes)")

    # Summary
    total_words = sum(p['word_count'] for p in all_pages)
    print(f"\n{'=' * 60}")
    print(f"  ✅ Generated {len(all_pages)} XHTML pages")
    print(f"  📊 Total vocabulary: {total_words} words")
    print(f"  📁 Output: {PAGES_DIR}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
