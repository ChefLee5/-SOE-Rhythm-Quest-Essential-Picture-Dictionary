#!/usr/bin/env python3
"""
Regenerate specific XHTML pages from markdown source.
Targets the 8 pages where the XHTML is out of sync with the expanded markdown.
"""

import re
import sys
import html
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
PAGES_DIR = BASE_DIR / "OEBPS" / "pages"
CONTENT_DIR = BASE_DIR / "content"

# Map of: (md_file, scene_number) -> xhtml_filename
PAGES_TO_FIX = {
    ("land2_numeria.md", 4):   "land2-the-bank.xhtml",
    ("land4_aquaria.md", 5):   "land4-hotels-lodging.xhtml",
    ("land6_luminosity.md", 7): "land6-money-management-bills.xhtml",
    ("land3_terrasol.md", 7):  "land3-silas-vestas-cottage-outside.xhtml",
    ("land3_terrasol.md", 14): "land3-rocks-minerals.xhtml",
    ("land3_terrasol.md", 15): "land3-recycling-sustainability.xhtml",
    ("land6_luminosity.md", 9):    "land6-community-helpers-services.xhtml",
    ("land6_luminosity.md", 10):   "land6-rights-responsibilities.xhtml",
    ("land7_celestia.md", 7):  "land7-the-scientific-method.xhtml",
    ("land7_celestia.md", 8):  "land7-the-calendar-cycles.xhtml",
    ("land7_celestia.md", 10): "land7-the-future-dreams.xhtml",
}

# Land metadata
LAND_INFO = {
    "land2_numeria.md": {
        "land_num": 2, "land_total": 7,
        "land_name": "Numeria", "land_icon": "🔢",
        "accent": "#7fb685",
        "char1": "Kwame", "char2": "Octavia",
        "char_desc": "Guided by <strong>Kwame</strong> the Pattern Master &amp; <strong>Octavia</strong> the Data Dancer",
    },
    "land4_aquaria.md": {
        "land_num": 4, "land_total": 7,
        "land_name": "Aquaria", "land_icon": "🌊",
        "accent": "#2563EB",
        "char1": "Ronan", "char2": "Nerissa",
        "char_desc": "Guided by <strong>Ronan</strong> the Wave Rider &amp; <strong>Nerissa</strong> the Deep Diver",
    },
    "land3_terrasol.md": {
        "land_num": 3, "land_total": 7,
        "land_name": "TerraSol", "land_icon": "🌿",
        "accent": "#5ba57e",
        "char1": "Silas", "char2": "Vesta",
        "char_desc": "Guided by <strong>Silas</strong> the Farmer &amp; <strong>Vesta</strong> the Nature Guide",
    },
    "land6_luminosity.md": {
        "land_num": 6, "land_total": 7,
        "land_name": "Luminosity", "land_icon": "📖",
        "accent": "#d4897a",
        "char1": "Ezra", "char2": "Athena",
        "char_desc": "Guided by <strong>Ezra</strong> the Builder &amp; <strong>Athena</strong> the Wise",
    },
    "land7_celestia.md": {
        "land_num": 7, "land_total": 7,
        "land_name": "Celestia", "land_icon": "🔭",
        "accent": "#9678c4",
        "char1": "Elias", "char2": "Selene",
        "char_desc": "Guided by <strong>Elias</strong> the Star Gazer &amp; <strong>Selene</strong> the Time Keeper",
    },
}


def parse_scene(md_path, scene_num):
    """Extract a specific scene from a markdown file."""
    with open(md_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    lines = text.split('\n')
    in_scene = False
    scene_title = ""
    scene_desc = ""
    entries = []
    tip_text = ""
    tip_icon = ""
    tip_char = ""
    
    for i, line in enumerate(lines):
        line = line.rstrip('\r')
        
        # Match scene header
        m = re.match(r'^## Scene (\d+): (.+)$', line)
        if m:
            sn = int(m.group(1))
            if sn == scene_num:
                in_scene = True
                scene_title = m.group(2)
                continue
            elif in_scene:
                break  # End of our scene
            continue
        
        if not in_scene:
            continue
        
        # Scene description (italic line)
        if line.startswith('*') and not entries and not scene_desc:
            scene_desc = line.strip('*').strip()
            continue
        
        # Table rows
        if line.startswith('|') and not line.startswith('|---') and not line.startswith('| #'):
            parts = [p.strip() for p in line.split('|')]
            parts = [p for p in parts if p]
            if len(parts) >= 6:
                try:
                    num = int(parts[0])
                    word = parts[1].strip('**').strip()
                    phonetic = parts[2].strip()
                    context = parts[3].strip()
                    asl = parts[4].strip()
                    entries.append({
                        'num': num,
                        'word': word,
                        'phonetic': phonetic,
                        'context': context,
                        'asl': asl,
                    })
                except (ValueError, IndexError):
                    pass
            continue
        
        # Tip block
        if line.startswith('> **'):
            tip_match = re.match(r'> \*\*(.+?) (.+?):\*\* \*(.+)\*$', line)
            if tip_match:
                tip_icon = tip_match.group(1)
                tip_char = tip_match.group(2)
                tip_text = tip_match.group(3)
    
    return {
        'title': scene_title,
        'description': scene_desc,
        'entries': entries,
        'tip_icon': tip_icon,
        'tip_char': tip_char,
        'tip_text': tip_text,
        'scene_num': scene_num,
    }


def escape_xml(text):
    """Escape text for XHTML."""
    return html.escape(text, quote=True)


def generate_xhtml(scene, land_info, xhtml_filename):
    """Generate XHTML page content."""
    slug = xhtml_filename.replace('.xhtml', '')
    word_count = len(scene['entries'])
    
    # Build table rows
    rows = []
    for entry in scene['entries']:
        rows.append(f"""            <tr>
                <td class="col-num">{entry['num']}</td>
                <td class="col-word">{escape_xml(entry['word'])}</td>
                <td class="col-phonetic">{escape_xml(entry['phonetic'])}</td>
                <td class="col-context">{escape_xml(entry['context'])}</td>
                <td class="col-asl">{escape_xml(entry['asl'])}</td>
                <td class="col-translation"></td>
            </tr>""")
    
    rows_html = '\n'.join(rows)
    
    # Build tip section
    tip_html = ""
    if scene['tip_text']:
        tip_html = f"""
    <!-- Character Tip -->
    <div class="character-tip">
        <span class="tip-icon">{scene['tip_icon']}</span>
        <p class="tip-character">{escape_xml(scene['tip_char'])}:</p>
        <p class="tip-text">{escape_xml(scene['tip_text'])}</p>
    </div>"""
    
    xhtml = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="en">

<head>
    <meta charset="UTF-8" />
    <title>{land_info['land_name']} — {escape_xml(scene['title'])}</title>
    <link rel="stylesheet" href="../styles/dictionary.css" type="text/css" />
    <style>
        :root {{
            --accent-color: {land_info['accent']};
        }}
    </style>
</head>

<body>
    <!-- Land Header -->
    <div class="land-header">
        <div class="land-number">Land {land_info['land_num']} of {land_info['land_total']}</div>
        <h1 class="land-name"><span class="land-icon">{land_info['land_icon']}</span> {land_info['land_name']}</h1>
        <p class="land-characters">{land_info['char_desc']}</p>
    </div>

    <!-- Scene Header -->
    <div class="scene-header">
        <h2 class="scene-title">Scene {scene['scene_num']}: {escape_xml(scene['title'])}</h2>
        <p class="scene-description">{escape_xml(scene['description'])}</p>
    </div>

    <!-- Scene Illustration -->
    <div class="scene-illustration">
        <img src="../images/{slug}.jpg" alt="A richly detailed scene depicting '{escape_xml(scene['title'])}' with numbered callout markers (1–{word_count}) indicating each vocabulary item's location in the scene." class="scene-image" />
    </div>

    <!-- Vocabulary Table -->
    <table class="vocab-table has-asl">
        <thead>
            <tr>
                <th class="col-num">#</th>
                <th>Word</th>
                <th>Pronunciation</th>
                <th>In the Story…</th>
                <th>ASL Sign 🤟</th>
                <th>My Language</th>
            </tr>
        </thead>
        <tbody>
{rows_html}
        </tbody>
    </table>
{tip_html}

</body>

</html>"""
    
    return xhtml


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    
    print("=" * 80)
    print("REGENERATING OUT-OF-SYNC XHTML PAGES")
    print("=" * 80)
    
    fixed = 0
    for (md_name, scene_num), xhtml_name in PAGES_TO_FIX.items():
        md_path = CONTENT_DIR / md_name
        xhtml_path = PAGES_DIR / xhtml_name
        land_info = LAND_INFO[md_name]
        
        print(f"\n📄 {md_name} Scene {scene_num} -> {xhtml_name}")
        
        # Parse scene from markdown
        scene = parse_scene(md_path, scene_num)
        
        if not scene['entries']:
            print(f"  ❌ ERROR: No entries found for Scene {scene_num} in {md_name}")
            continue
        
        # Check current XHTML word count
        if xhtml_path.exists():
            with open(xhtml_path, 'r', encoding='utf-8') as f:
                old_content = f.read()
            old_count = len(re.findall(r'<td class="col-num">\d+</td>', old_content))
            print(f"  Current XHTML: {old_count} words")
        
        print(f"  MD Source: {len(scene['entries'])} words")
        print(f"  Scene title: {scene['title']}")
        
        # Generate new XHTML
        new_xhtml = generate_xhtml(scene, land_info, xhtml_name)
        
        # Write
        with open(xhtml_path, 'w', encoding='utf-8', newline='\r\n') as f:
            f.write(new_xhtml)
        
        print(f"  ✅ Regenerated: {len(scene['entries'])} words written")
        fixed += 1
    
    print(f"\n{'='*80}")
    print(f"DONE: {fixed}/{len(PAGES_TO_FIX)} pages regenerated")
    print("="*80)


if __name__ == "__main__":
    main()
