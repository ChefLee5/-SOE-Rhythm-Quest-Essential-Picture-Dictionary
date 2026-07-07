#!/usr/bin/env python3
"""
Regenerate out-of-sync XHTML pages from markdown source.

Auto-discovers every "## Scene N:" in the land content files, maps each to
its XHTML page by filename slug (FILENAME_OVERRIDES handles irregular names),
compares MD vs XHTML word counts, and regenerates only the stale pages.
Back-matter pages (back_*.md) use different templates and are NOT covered.

Usage:
  py ebook/scripts/regen_pages.py            # regenerate stale pages
  py ebook/scripts/regen_pages.py --check    # report only, write nothing
  py ebook/scripts/regen_pages.py --force    # regenerate ALL matched pages
"""

import re
import sys
import html
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
PAGES_DIR = BASE_DIR / "OEBPS" / "pages"
CONTENT_DIR = BASE_DIR / "content"

# Explicit (md_file, scene_number) -> xhtml_filename mappings for scenes whose
# page filename does not match slugify(scene title). Checked before the slug.
FILENAME_OVERRIDES = {
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
    "land1_harmonia.md": {
        "land_num": 1, "land_total": 7,
        "land_name": "Harmonia", "land_icon": "🎵",
        "accent": "#d4a843",
        "char1": "Kenji", "char2": "Aiko",
        "char_desc": "Guided by <strong>Kenji</strong> the Rhythm Keeper &amp; <strong>Aiko</strong> the Melody Weaver",
    },
    "land5_vitalis.md": {
        "land_num": 5, "land_total": 7,
        "land_name": "Vitalis", "land_icon": "🤸",
        "accent": "#c4785a",
        "char1": "Felix", "char2": "Amara",
        "char_desc": "Guided by <strong>Felix</strong> the Body Guardian &amp; <strong>Amara</strong> the Wellness Guide",
    },
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


def slugify(title):
    """Scene title -> page filename slug (matches the existing naming scheme)."""
    s = title.lower()
    s = s.replace("&", " ")
    s = re.sub(r"[’']", "", s)
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def discover_scenes():
    """Yield (md_name, scene_num, title, xhtml_filename_or_None) for every land scene."""
    for md_name in sorted(LAND_INFO):
        md_path = CONTENT_DIR / md_name
        text = md_path.read_text(encoding='utf-8')
        land_num = LAND_INFO[md_name]['land_num']
        for m in re.finditer(r'^## Scene (\d+): (.+)$', text, re.M):
            sn, title = int(m.group(1)), m.group(2).strip()
            candidate = FILENAME_OVERRIDES.get((md_name, sn)) or f"land{land_num}-{slugify(title)}.xhtml"
            yield md_name, sn, title, (candidate if (PAGES_DIR / candidate).exists() else None)


def xhtml_word_count(xhtml_path):
    with open(xhtml_path, 'r', encoding='utf-8') as f:
        return len(re.findall(r'<td class="col-num">\d+</td>', f.read()))


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    check_only = "--check" in sys.argv
    force = "--force" in sys.argv

    print("=" * 80)
    print("REGENERATING OUT-OF-SYNC XHTML PAGES" + (" (check only)" if check_only else ""))
    print("=" * 80)

    matched = unmatched = in_sync = fixed = errors = 0
    for md_name, scene_num, title, xhtml_name in discover_scenes():
        if xhtml_name is None:
            unmatched += 1
            print(f"⚠️  NO PAGE FOUND: {md_name} Scene {scene_num}: {title}")
            print(f"    (expected land{LAND_INFO[md_name]['land_num']}-{slugify(title)}.xhtml — "
                  f"add a FILENAME_OVERRIDES entry, or create page + OPF/nav entries for a new scene)")
            continue
        matched += 1

        md_path = CONTENT_DIR / md_name
        xhtml_path = PAGES_DIR / xhtml_name
        scene = parse_scene(md_path, scene_num)
        if not scene['entries']:
            errors += 1
            print(f"❌ ERROR: no entries parsed for {md_name} Scene {scene_num}")
            continue

        old_count = xhtml_word_count(xhtml_path)
        if old_count == len(scene['entries']) and not force:
            in_sync += 1
            continue

        print(f"📄 {md_name} Scene {scene_num} -> {xhtml_name}")
        print(f"   XHTML: {old_count} words | MD: {len(scene['entries'])} words")
        if check_only:
            continue
        new_xhtml = generate_xhtml(scene, LAND_INFO[md_name], xhtml_name)
        with open(xhtml_path, 'w', encoding='utf-8', newline='\r\n') as f:
            f.write(new_xhtml)
        print(f"   ✅ Regenerated: {len(scene['entries'])} words written")
        fixed += 1

    print(f"\n{'='*80}")
    print(f"scenes matched: {matched} | in sync: {in_sync} | regenerated: {fixed} | "
          f"unmatched: {unmatched} | errors: {errors}")
    print("="*80)
    if unmatched or errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
