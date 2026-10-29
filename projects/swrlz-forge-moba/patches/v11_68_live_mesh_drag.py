"""§E v11.68: live-preview gizmo and selected mesh on touch/drag."""
from pathlib import Path
import json

OLD='SWYRL_ENGINE_DEPLOY_MARKER: V11_67_MESH_TRANSFORM_PERFORMANCE'
NEW='SWYRL_ENGINE_DEPLOY_MARKER: V11_68_LIVE_MESH_GIZMO_FEEDBACK'
CANONICAL='const MODEL_ATELIER_CANONICAL_PROJECT='
def once(html,before,after):
    assert html.count(before)==1,(before[:120],html.count(before))
    return html.replace(before,after,1)
def scene(html):
    assert html.count(CANONICAL)==1
    source=html.split(CANONICAL,1)[1]
    _,end=json.JSONDecoder().raw_decode(source)
    return source[:end]
def apply(html):
    before_scene=scene(html)
    js=(Path(__file__).resolve().parents[1]/'runtime/model_atelier_live_drag_v11_68.js').read_text(encoding='utf-8')
    html=once(html,'function atelierMeshGizmoMove(e){',js+'\nfunction atelierMeshGizmoMove(e){')
    # The toolbar refresh at drag start previously destroyed/recreated active
    # gizmo objects; preserve their identity until pointerup/cancel.
    html=once(html,' atelierMeshGizmoBuild();\n atelierMeshToolbarPosition();',
        ' if(!atelierMeshDrag)atelierMeshGizmoBuild();\n atelierMeshToolbarPosition();')
    original=''' for(const t of values){
  const mesh=modelRoot.children.find(o=>o.isMesh&&o.userData.atelierId===t.id);
  if(!mesh)continue;
  mesh.position.set(...t.position);mesh.rotation.set(...t.rotation);mesh.scale.set(...t.scale);
 }
 return true;
}
function atelierMeshGizmoUp(e){'''
    updated=''' atelierMeshLiveDragPreview(values);
 return true;
}
function atelierMeshGizmoUp(e){'''
    html=once(html,original,updated)
    # Selection changes should only change the existing native BoxHelper,
    # not recreate all 283 render meshes before the outline becomes visible.
    begin='  function select(id){'
    assert html.count(begin)==1
    start=html.index(begin)
    end=html.find('\n  function ',start+len(begin))
    assert end>start
    select_body=html[start:end]
    assert select_body.count('renderParts();')==1,select_body[:500]
    html=html[:start]+select_body.replace('renderParts();','atelierMeshSelectFast();',1)+html[end:]
    # Recenter the gizmo after zero-movement or canceled gestures, without
    # regenerating any source geometry.
    html=once(html,
        "atelierMeshRestoreLiveTransforms(d.snapshot);return true;",
        "atelierMeshRestoreLiveTransforms(d.snapshot);atelierMeshToolbarRefresh();return true;")
    html=once(html,
        "atelierMeshRestoreLiveTransforms(before);return true;",
        "atelierMeshRestoreLiveTransforms(before);atelierMeshToolbarRefresh();return true;")
    html=once(html,
        "status('Transform exceeds valid native position/rotation/scale bounds.',true);atelierMeshRestoreLiveTransforms(snap);return false;",
        "status('Transform exceeds valid native position/rotation/scale bounds.',true);atelierMeshRestoreLiveTransforms(snap);atelierMeshToolbarRefresh();return false;")
    for old,new in (
        (OLD,NEW),
        ('ENGINE · MAKER v11.67','ENGINE · MAKER v11.68'),
        ('v11.67 · fluid mesh transforms','v11.68 · live transform feedback'),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.67'","window.SWRLZ_FORGE_BUILD={version:'v11.68'"),
        ('<title>§wyrl§ Engine · Maker v11.67</title>','<title>§wyrl§ Engine · Maker v11.68</title>')
    ):html=once(html,old,new)
    assert scene(html)==before_scene
    assert html.count('function atelierMeshLiveDragPreview(records)')==1
    assert html.count('function atelierMeshSelectFast()')==1
    assert html.count(NEW)==1
    return html
