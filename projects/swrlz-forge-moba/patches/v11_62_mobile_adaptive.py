"""§E v11.62 governed mobile Model Atelier presentation atop sealed v11.61.

Preserve the 283-part original scene, all existing mesh/native actions, and
the 43 bundled assets. The tool UI uses the tested v11.62 preview patch.
"""
from pathlib import Path
import json
import runpy

OLD = 'SWYRL_ENGINE_DEPLOY_MARKER: V11_61_ADAPTIVE_CONTEXT_TOOL_WORKBENCH'
NEW = 'SWYRL_ENGINE_DEPLOY_MARKER: V11_62_MOBILE_ADAPTIVE_TOOL_SHEET'
CANONICAL = 'const MODEL_ATELIER_CANONICAL_PROJECT='

def original_scene(html):
    assert html.count(CANONICAL) == 1
    data = html.split(CANONICAL, 1)[1]
    _, end = json.JSONDecoder().raw_decode(data)
    return data[:end]

def apply(html):
    assert html.count(OLD) == 1
    scene = original_scene(html)
    preview = Path(__file__).with_name('v11_62_mobile_adaptive_preview.py')
    updated = runpy.run_path(str(preview))['apply'](html)
    for before, after in (
        (OLD, NEW),
        ('ENGINE · MAKER v11.61', 'ENGINE · MAKER v11.62'),
        ('v11.61 · adaptive Model Atelier tools', 'v11.62 · mobile adaptive Model Atelier tools'),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.61'", "window.SWRLZ_FORGE_BUILD={version:'v11.62'"),
        ('<title>§wyrl§ Engine · Maker v11.61</title>', '<title>§wyrl§ Engine · Maker v11.62</title>'),
    ):
        assert updated.count(before) == 1, ('Missing/ambiguous release label', before, updated.count(before))
        updated = updated.replace(before, after, 1)
    assert original_scene(updated) == scene, 'Canonical 283-part model changed'
    assert updated.count(NEW) == 1
    assert updated.count('function atelierMobileLayoutInstall(panel)') == 1
    assert updated.count('atelierMobileLayoutInstall(panel);') == 2
    assert updated.count('function atelierAdaptiveInstall(panel)') == 1
    return updated
