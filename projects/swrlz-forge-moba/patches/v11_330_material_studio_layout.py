"""§E v11.330: dedicated Material & Texture Studio with responsive native tools."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKER = 'SWYRL_ENGINE_DEPLOY_MARKER: V11_330_MATERIAL_STUDIO_LAYOUT'


def once(html, old, new):
    count = html.count(old)
    if count != 1:
        raise AssertionError(('v11.330 anchor', old[:110], count))
    return html.replace(old, new, 1)


def apply(html):
    css = (ROOT / 'runtime/material_studio_layout_v11_330.css').read_text('utf8')
    script = (ROOT / 'runtime/material_studio_layout_v11_330.js').read_text('utf8')
    assert html.index('</head>') < html.index('<body')
    html = html.replace('</head>', '<style id="se330MaterialStudioStyle">\n' + css + '\n</style>\n</head>', 1)
    html = once(html, 'window.SWRLZ_FORGE_BUILD=', script + '\nwindow.SWRLZ_FORGE_BUILD=')
    html = once(html, "mode==='materials'?q('#se225MaterialsPanel .se225-m-title')",
                "mode==='materials'?(q('#se330MaterialTools')||q('#se225MaterialsPanel .se225-m-title'))")
    previous = " source.engine='§wyrl§ Engine · Maker v11.321';source.version=11.321;"
    assert html.count(previous) == 3
    html = html.replace(previous, " source.engine='§wyrl§ Engine · Maker v11.330';source.version=11.330;")
    for old, new in [
        ('SWYRL_ENGINE_DEPLOY_MARKER: V11_321_SHEEP_SIGHT_XR_CROWD', MARKER),
        ('ENGINE · MAKER v11.321', 'ENGINE · MAKER v11.330'),
        ('v11.321 · Sheep Tag sightlines and busy Quest metrics',
         'v11.330 · dedicated Materials workspace and responsive authoring'),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.321'", "window.SWRLZ_FORGE_BUILD={version:'v11.330'"),
        ('<title>§wyrl§ Engine · Maker v11.321</title>', '<title>§wyrl§ Engine · Maker v11.330</title>'),
    ]:
        html = once(html, old, new)
    key = 'const SE_RELEASE_NOTES='
    at = html.index(key) + len(key)
    notes, width = json.JSONDecoder().raw_decode(html[at:])
    if not any(item.get('version') == 'v11.321' for item in notes.get('history', [])):
        notes.setdefault('history', []).insert(0, {'version': 'v11.321', 'changes': notes.get('changes', [])})
    notes.update(version='v11.330', title='A dedicated Material & Texture Studio', date='2026-11-07', changes=[
        'Material & Texture Studio has a dedicated library, texture workspace and property inspector with clear primary actions instead of panels floating over the Game editor.',
        'Compact layouts provide Library, Texture and Properties navigation, including wide portrait phone frames, while keeping native studio switching available.',
        'Empty material libraries show a clear create action and hide unavailable properties. Creating or selecting a material populates the existing native controls.',
        'Texture patterns, direct painting, brush undo, PNG/image and JSON library workflows retain their existing native handlers and saved project data.',
        'Texture editing keeps the covered 3D viewport idle. Selecting the visible 3D preview resumes it; other studios and immersive rendering retain their native behavior.',
        'Native scene material assignment and preview stay available; preserve Game, Model and Particle navigation and all Sheep/Quest fixes through v11.321.',
    ])
    return html[:at] + json.dumps(notes, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/') + html[at + width:]
