"""Native Sheep Tag archive: precise mazes, tactical pursuit and optional magic."""
import json
from pathlib import Path


def once(html, old, new):
    assert html.count(old) == 1, 'Sheep Tag archive anchor missing/ambiguous: ' + old[:90]
    return html.replace(old, new, 1)


def apply(html):
    root = Path(__file__).resolve().parent.parent
    starter = json.loads((root / 'scenes/sheep-tag-moonbell-archive.swyrl.json').read_text())
    encoded = json.dumps(starter, separators=(',', ':'), ensure_ascii=False).replace('</', '<\\/')
    modules = ['archive_sheep_visuals.js', 'archive_sheep_game.js', 'archive_sheep_magic.js',
               'archive_sheep_ui.js', 'archive_sheep_creator.js', 'archive_sheep_integration.js']
    js = "const ST_ARCHIVE_SOURCE_SCENE='scenes/sheep-tag-moonbell-archive.swyrl.json';\n" + 'const ST_CANONICAL_PROJECT=' + encoded + ';\n' + '\n'.join((root / 'runtime' / name).read_text() for name in modules)
    start = html.index('const ST_CANONICAL_PROJECT=')
    end = html.index('window.SWRLZ_FORGE_BUILD=', start)
    assert html.count('const ST_CANONICAL_PROJECT=') == 1
    html = html[:start] + js + '\n' + html[end:]
    css_start = html.index('<style id="sheepTagStyles">')
    css_end = html.index('</style>', css_start) + len('</style>')
    html = html[:css_start] + '<style id="sheepTagStyles">\n' + (root / 'runtime/archive_sheep_ui.css').read_text() + '\n</style>' + html[css_end:]
    html = once(html, 'storyEditorInstall();stInstallUI();refreshAssetList();',
                'storyEditorInstall();stInstallUI();stInstallCreator();refreshAssetList();')
    html = once(html, 'V10_0_SHEEP_TAG_STARTER', 'V10_1_SHEEP_TAG_ARCHIVE')
    html = html.replace('Maker v10.0', 'Maker v10.1').replace('MAKER v10.0', 'MAKER v10.1')
    html = html.replace("version:'v10.0'", "version:'v10.1'").replace('version:10.0', 'version:10.1')
    html = html.replace("stamp:'2026.10.11'", "stamp:'2026.10.12'").replace('§E v10.0 Tools', '§E v10.1 Tools')
    html = html.replace('v10.0 · SHEEP TAG · MOONBELL MEADOW', 'v10.1 · SHEEP TAG ARCHIVE · MOONBELL MEADOW')
    html = html.replace('§wyrl§ Engine v10.0 · Sheep Tag and native editor starters', '§wyrl§ Engine v10.1 · tactical Sheep Tag and native map creator')
    html = html.replace('Build farm mazes, outrun wolf hunters, and rescue captured wisps from the central pen. Play either side with computer teammates.',
                        'Craft precise house mazes, breach defenses, and rescue wisps. Curated map creator and optional archive magic: thorns, totems, raised routes and Illusive Split.')
    return html
