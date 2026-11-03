"""§E v11.239 — remove duplicate native editor actor raycasts in XR Sheep Tag."""
from pathlib import Path
import json

def once(text,old,new):
    assert text.count(old)==1, ('v11.239 source anchor',old[:90],text.count(old))
    return text.replace(old,new,1)

def apply(html):
    root=Path(__file__).resolve().parents[1]
    js=(root/'runtime/engine_quest_gameplay_raycast_budget_v11_239.js').read_text(encoding='utf8')
    for dep in (
      'function se181XRRaycast(record)',
      'function se181XRRender()',
      'function se193XRGameActive()',
      'SWYRL_ENGINE_QUEST_RADIAL_STABILITY_238',
      'window.SWYRL_ENGINE_QUEST_PERFORMANCE_210'
    ):
      assert dep in html, ('v11.239 missing dependency',dep)
    html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=')
    old=" source.engine='§wyrl§ Engine · Maker v11.238';source.version=11.238;"
    assert html.count(old)==2
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.239';source.version=11.239;")
    for before,after in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_238_QUEST_RADIAL_AND_WORKSPACE',
       'SWYRL_ENGINE_DEPLOY_MARKER: V11_239_QUEST_HEADTURN_RAYCAST_BUDGET'),
      ('ENGINE · MAKER v11.238','ENGINE · MAKER v11.239'),
      ('v11.238 · Quest radial menu frame recovery and studio layout',
       'v11.239 · Quest fast-turn frame budget and native raycast removal'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.238'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.239'"),
      ('<title>§wyrl§ Engine · Maker v11.238</title>',
       '<title>§wyrl§ Engine · Maker v11.239</title>'),
    ]: html=once(html,before,after)
    marker='const SE_RELEASE_NOTES='
    at=html.index(marker)+len(marker)
    obj,n=json.JSONDecoder().raw_decode(html[at:])
    obj.update(title='Quest Sheep Tag fast head-turn raycast budget',date='2026-11-03',
      changes=[
        'When immersive Sheep Tag Play is active, skip the superseded editor actor-mesh triangle raycasts that the original WebXR gateway performed for both controllers every frame. The newer native game input and authoritative controller targeting remain untouched.',
        'Continue testing the existing EXIT VR world panel against both controllers without intersecting every nested scene mesh; keep original editor actor selection and raycasts outside gameplay.',
        'Track per-XR-frame callback gaps over 20, 35, and 70 milliseconds, including whether the menu was open, with SWYRL_ENGINE_QUEST_HEADTURN_239.diagnose().',
        'Preserve native WebXR head tracking, stereo projections, resolution, frame loop, fog-of-war logical visibility, sheep collision, gamepad input, save data, Model Atelier and §C.',
        'User Quest 2 acceptance is required to verify whether the fast-head-turn black-edge problem improves. The Meta compositor is not controlled by the engine.'
      ])
    return html[:at]+json.dumps(obj,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+n:]
