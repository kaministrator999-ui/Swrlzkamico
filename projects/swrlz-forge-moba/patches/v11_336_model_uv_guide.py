"""§E v11.336: export true selected-mesh UV guide PNG and remap painted PNG."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKER = 'SWYRL_ENGINE_DEPLOY_MARKER: V11_336_MESH_UV_GUIDE'

def once(html, old, new, label):
    count = html.count(old)
    if count != 1:
        raise AssertionError(('v11.336', label, count, old[:100]))
    return html.replace(old, new, 1)

def apply(html):
    js = (ROOT / 'runtime/model_atelier_uv_layout_v11_336.js').read_text('utf8')
    css = (ROOT / 'runtime/model_atelier_uv_layout_v11_336.css').read_text('utf8')
    assert 'function se336UVLayout(mesh, canvas)' in js
    html = once(html, '  function ensurePanel(){',
        js + '\n  function ensurePanel(){', 'native Model Atelier closure')
    # Head-close text also occurs in embedded literals; patch the first real head close.
    assert '</head>' in html and html.index('</head>') < html.index('<body')
    html = html.replace('</head>', '<style id="se336MeshUVStyle">\n' + css + '\n</style>\n</head>', 1)
    old = " source.engine='§wyrl§ Engine · Maker v11.335';source.version=11.335;"
    if html.count(old) != 3:
        raise AssertionError(('v11.336 scene provenance', html.count(old)))
    html = html.replace(old,
        " source.engine='§wyrl§ Engine · Maker v11.336';source.version=11.336;")
    for previous, next_value in (
        ('SWYRL_ENGINE_DEPLOY_MARKER: V11_335_CLIFF_ULNAR_CONTOUR', MARKER),
        ('ENGINE · MAKER v11.335', 'ENGINE · MAKER v11.336'),
        ('v11.335 · refined pinky-side palm contour',
         'v11.336 · selected mesh UV image guides and painted texture import'),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.335'",
         "window.SWRLZ_FORGE_BUILD={version:'v11.336'"),
        ('<title>§wyrl§ Engine · Maker v11.335</title>',
         '<title>§wyrl§ Engine · Maker v11.336</title>'),
    ):
        html = once(html, previous, next_value, 'release identity')
    key = 'const SE_RELEASE_NOTES='
    start = html.index(key) + len(key)
    notes, length = json.JSONDecoder().raw_decode(html[start:])
    if not any(v.get('version') == 'v11.335' for v in notes.get('history', [])):
        notes.setdefault('history', []).insert(0, {
            'version': 'v11.335', 'changes': notes.get('changes', [])})
    notes.update(
        version='v11.336', date='2026-11-07',
        title='Model Atelier: mesh UV guide extraction and painted PNG reimport',
        changes=[
            'Model Atelier inspector exposes UV Layout for the selected actual mesh; no guessed camera projection.',
            'Export a 1024×1024 transparent PNG wireframe generated directly from the selected mesh UV attribute and triangle indices.',
            'Paint on a separate image layer and import a PNG/JPEG back onto the selected mesh using its unchanged UV coordinates and correct vertical orientation.',
            'Imported 512×512 artwork is stored as a bounded PNG on the model part, included in model project save/export and native undo history.',
            'Painted textures preview on the model itself without tint multiplication. Modeler-owned GPU maps are released when meshes rebuild.',
            'Missing/out-of-range UVs and oversized/unreadable textures are rejected rather than projected or silently distorted.',
            'Existing UV inspection, planar reprojection, Material Studio, game editor, Quest renderer and unrelated model parts are unchanged.',
        ])
    return html[:start] + json.dumps(
        notes, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/') + html[start + length:]
