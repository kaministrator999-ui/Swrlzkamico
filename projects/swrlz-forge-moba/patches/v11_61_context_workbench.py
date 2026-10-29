"""Governed §E v11.61 context tool workbench atop byte-sealed v11.60.
Preserves native 283-part scene and previous 43 packaged assets.
"""
from pathlib import Path
import json,runpy

OLD='SWYRL_ENGINE_DEPLOY_MARKER: V11_60_FLOATING_MODEL_ATELIER_DOCK'
NEW='SWYRL_ENGINE_DEPLOY_MARKER: V11_61_ADAPTIVE_CONTEXT_TOOL_WORKBENCH'
CANONICAL='const MODEL_ATELIER_CANONICAL_PROJECT='

def original_scene(html):
    assert html.count(CANONICAL)==1
    src=html.split(CANONICAL,1)[1]
    obj,end=json.JSONDecoder().raw_decode(src)
    return src[:end]

def apply(html):
    assert html.count(OLD)==1
    original=original_scene(html)
    previous=Path(__file__).with_name('v11_61_context_workbench_preview.py')
    updated=runpy.run_path(str(previous))['apply'](html)
    for before,after in (
        (OLD,NEW),
        ('ENGINE · MAKER v11.60','ENGINE · MAKER v11.61'),
        ('v11.60 · floating Model Atelier tools','v11.61 · adaptive Model Atelier tools'),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.60'","window.SWRLZ_FORGE_BUILD={version:'v11.61'"),
        ('<title>§wyrl§ Engine · Maker v11.60</title>','<title>§wyrl§ Engine · Maker v11.61</title>'),
    ):
        assert updated.count(before)==1,('Missing/ambiguous source label',before,updated.count(before))
        updated=updated.replace(before,after,1)
    assert original_scene(updated)==original,'Original model data changed'
    assert updated.count(NEW)==1
    assert updated.count('function atelierAdaptiveInstall(panel)')==1
    assert updated.count('function atelierContextWatchForDock()')==1
    return updated
