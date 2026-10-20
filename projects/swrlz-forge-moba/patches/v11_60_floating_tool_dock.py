"""§E v11.60 governed floating Model Atelier dock release.

Additive on the sealed v11.59, keeping the exact existing serialized 283-part
character, original references and other project assets untouched.
"""
import json
import runpy
from pathlib import Path

CANONICAL = 'const MODEL_ATELIER_CANONICAL_PROJECT='
OLD_MARKER = 'SWYRL_ENGINE_DEPLOY_MARKER: V11_59_PRECISION_MODEL_ATELIER'
NEW_MARKER = 'SWYRL_ENGINE_DEPLOY_MARKER: V11_60_FLOATING_MODEL_ATELIER_DOCK'

def _original_scene(html):
    source = html.split(CANONICAL, 1)[1]
    value, length = json.JSONDecoder().raw_decode(source)
    return source[:length]

def apply(html):
    assert html.count(CANONICAL) == 1
    assert html.count(OLD_MARKER) == 1
    original_scene = _original_scene(html)
    preview = Path(__file__).with_name('v11_60_floating_tool_dock_preview.py')
    updated = runpy.run_path(str(preview))['apply'](html)
    for previous, current in (
        (OLD_MARKER, NEW_MARKER),
        ('ENGINE · MAKER v11.59', 'ENGINE · MAKER v11.60'),
        ('v11.59 · precision Model Atelier', 'v11.60 · floating Model Atelier tools'),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.59'", "window.SWRLZ_FORGE_BUILD={version:'v11.60'"),
        ('<title>§wyrl§ Engine · Maker v11.59</title>',
         '<title>§wyrl§ Engine · Maker v11.60</title>'),
    ):
        assert updated.count(previous) == 1, 'Missing/ambiguous release label: ' + previous
        updated = updated.replace(previous, current, 1)
    assert _original_scene(updated) == original_scene, 'Original 283-part scene changed'
    assert updated.count(NEW_MARKER) == 1
    assert updated.count('    atelierToolDockInstall(panel);\n') == 1
    return updated
