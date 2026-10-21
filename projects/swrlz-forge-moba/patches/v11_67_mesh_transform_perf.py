"""§E v11.67: optimize mesh transform commits without rebuilding geometry."""
from pathlib import Path
import json

OLD='SWYRL_ENGINE_DEPLOY_MARKER: V11_66_MESH_SELECTION_UX_REPAIR'
NEW='SWYRL_ENGINE_DEPLOY_MARKER: V11_67_MESH_TRANSFORM_PERFORMANCE'
CANONICAL='const MODEL_ATELIER_CANONICAL_PROJECT='

def once(html,before,after):
    assert html.count(before)==1,(before[:120],html.count(before))
    return html.replace(before,after,1)

def original_scene(html):
    assert html.count(CANONICAL)==1
    source=html.split(CANONICAL,1)[1]
    _,end=json.JSONDecoder().raw_decode(source)
    return source[:end]

def apply(html):
    original=original_scene(html)
    js=(Path(__file__).resolve().parents[1]/'runtime/model_atelier_transform_fast_v11_67.js').read_text(encoding='utf-8')
    html=once(html,'function atelierMeshCommit(snap,pivot,mode,axis,amount){',
              js+'\nfunction atelierMeshCommit(snap,pivot,mode,axis,amount){')
    html=once(html,
        ' for(const t of next){const p=partById(t.id);p.position=t.position;p.rotation=t.rotation;p.scale=t.scale;}\n signalEdited();atelierMeshToolbarRefresh();',
        ' for(const t of next){const p=partById(t.id);p.position=t.position;p.rotation=t.rotation;p.scale=t.scale;}\n atelierMeshTransformOnlyCommit(next);')
    html=once(html,
        "  status('Transform exceeds valid native position/rotation/scale bounds.',true);renderParts();return false;",
        "  status('Transform exceeds valid native position/rotation/scale bounds.',true);atelierMeshRestoreLiveTransforms(snap);return false;")
    html=once(html,
        " if(Math.abs(d.mode==='scale'?d.amount-1:d.amount)<1e-6){renderParts();return true;}",
        " if(Math.abs(d.mode==='scale'?d.amount-1:d.amount)<1e-6){atelierMeshRestoreLiveTransforms(d.snapshot);return true;}")
    html=once(html,
        "function atelierMeshGizmoCancel(){\n if(!atelierMeshDrag)return false;\n atelierMeshDrag=null;renderParts();return true;\n}",
        "function atelierMeshGizmoCancel(){\n if(!atelierMeshDrag)return false;\n const before=atelierMeshDrag.snapshot;atelierMeshDrag=null;\n atelierMeshRestoreLiveTransforms(before);return true;\n}")
    for old,new in (
        (OLD,NEW),
        ('ENGINE · MAKER v11.66','ENGINE · MAKER v11.67'),
        ('v11.66 · cyber mesh gizmos','v11.67 · fluid mesh transforms'),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.66'","window.SWRLZ_FORGE_BUILD={version:'v11.67'"),
        ('<title>§wyrl§ Engine · Maker v11.66</title>','<title>§wyrl§ Engine · Maker v11.67</title>'),
    ):
        html=once(html,old,new)
    assert original_scene(html)==original
    assert html.count(NEW)==1
    assert html.count('function atelierMeshTransformOnlyCommit(records)')==1
    return html
