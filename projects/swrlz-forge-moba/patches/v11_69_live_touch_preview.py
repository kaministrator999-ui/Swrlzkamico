"""§E v11.69 — event-driven live drag paint with real lightweight updates."""
import json
from pathlib import Path
OLD='SWYRL_ENGINE_DEPLOY_MARKER: V11_68_LIVE_MESH_GIZMO_FEEDBACK'
NEW='SWYRL_ENGINE_DEPLOY_MARKER: V11_69_DRAG_PREVIEW_RENDER'
CANONICAL='const MODEL_ATELIER_CANONICAL_PROJECT='
def once(s,a,b):
    assert s.count(a)==1,(a[:110],s.count(a))
    return s.replace(a,b,1)
def scene(html):
    assert html.count(CANONICAL)==1
    part=html.split(CANONICAL,1)[1]
    _,end=json.JSONDecoder().raw_decode(part)
    return part[:end]
def apply(html):
    original=scene(html)
    js=(Path(__file__).resolve().parents[1]/'runtime/model_atelier_touch_drag_v11_69.js').read_text(encoding='utf-8')
    start='function atelierMeshLiveDragPreview(records){'
    end='function atelierMeshSelectFast(){'
    assert html.count(start)==1 and html.count(end)==1
    a=html.index(start);b=html.index(end,a)
    html=html[:a]+js+'\n'+html[b:]
    # Let the DOM gesture system know the active gizmo owns touch movement.
    html=once(html,
       'function atelierMeshGizmoMove(e){\n const d=atelierMeshDrag;if(!d||e.pointerId!==d.pointerId)return false;',
       'function atelierMeshGizmoMove(e){\n const d=atelierMeshDrag;if(!d||e.pointerId!==d.pointerId)return false;\n if(e.cancelable)e.preventDefault();')
    for before,after in (
      (OLD,NEW),
      ('ENGINE · MAKER v11.68','ENGINE · MAKER v11.69'),
      ('v11.68 · live transform feedback','v11.69 · direct live drag rendering'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.68'","window.SWRLZ_FORGE_BUILD={version:'v11.69'"),
      ('<title>§wyrl§ Engine · Maker v11.68</title>','<title>§wyrl§ Engine · Maker v11.69</title>')
    ):html=once(html,before,after)
    assert scene(html)==original
    assert html.count(NEW)==1
    assert html.count('function atelierMeshLiveDragPreview(records)')==1
    assert 'renderer.render(world,camera);\n  atelierLiveDragRenderUpdates++;' in html
    return html
