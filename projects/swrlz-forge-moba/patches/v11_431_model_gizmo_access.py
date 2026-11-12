"""§E v11.431 — comfortable native touch and controller transform handles."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_431_MODEL_GIZMO_ACCESS'
def one(src,old,new):
    assert src.count(old)==1,('v11.431 anchor',old[:110],src.count(old))
    return src.replace(old,new,1)
def apply(html):
    native=(ROOT/'runtime/model_gizmo_access_v11_431.js').read_text('utf8')
    xr=(ROOT/'runtime/model_vr_gizmo_access_v11_431.js').read_text('utf8')
    html=one(html,'/* ATELIER_BRIDGE_END */',native+'\n/* ATELIER_BRIDGE_END */')
    html=one(html,'camera:se430ModelCamera,chatAction:', 'camera:se430ModelCamera,gizmoAccess:se431GizmoAccess,chatAction:')
    html=one(html,'window.SWYRL_ENGINE_MODEL_WORKSHOP=ModelAtelier.workshop;', 'window.SWYRL_ENGINE_MODEL_GIZMO_ACCESS=ModelAtelier.gizmoAccess;\nwindow.SWYRL_ENGINE_MODEL_WORKSHOP=ModelAtelier.workshop;')
    html=one(html,'atelierAssemblyTick(performance.now());se430BeginnerTick(performance.now());','atelierAssemblyTick(performance.now());se430BeginnerTick(performance.now());se431GizmoAccess.refresh();')
    html=one(html,'const hit=raycaster.intersectObjects(handles,false)[0];\n if(!hit)return false;\n const axis=hit.object.userData.meshGizmoAxis;', 'const hit=se431GizmoAccess.pick(e);\n if(!hit)return false;\n const axis=hit.object.userData.meshGizmoAxis;')
    html=one(html,'const hit=raycaster.intersectObjects(atelierMeshGizmo.children.filter(o=>o.userData.meshGizmoAxis),false)[0];', 'const hit=se431GizmoAccess.pick(e);')
    html=one(html,'installPerformanceSettings();se189InstallPerfUI();',xr+'\ninstallPerformanceSettings();se189InstallPerfUI();')
    for before,after in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_430_MODEL_STUDIO_VISUAL_WORKSHOP',MARKER),
      ('ENGINE · MAKER v11.430','ENGINE · MAKER v11.431'),
      ('v11.430 · learn and build with real mesh tools','v11.431 · comfortable touch and VR transform handles'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.430'","window.SWRLZ_FORGE_BUILD={version:'v11.431'"),
      ('<title>§wyrl§ Engine · Maker v11.430</title>','<title>§wyrl§ Engine · Maker v11.431</title>')]:html=one(html,before,after)
    old=" source.engine='§wyrl§ Engine · Maker v11.430';source.version=11.430;"
    assert html.count(old)==5
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.431';source.version=11.431;")
    key='const SE_RELEASE_NOTES=';at=html.index(key)+len(key);notes,length=json.JSONDecoder().raw_decode(html[at:])
    # Older history generation sees the current manifest; replace its generic
    # v11.430 placeholder with the actual previous release notes only once.
    notes['history']=[item for item in notes.get('history',[]) if item.get('version')!='v11.430']
    notes['history'].insert(0,{'version':'v11.430','changes':notes.get('changes',[])})
    notes.update(version='v11.431',date='2026-11-12',title='Easier transform handles for touch and VR',changes=[
      'Native Move, Rotate and Scale handles gain input-appropriate selection tolerance and clearer feedback. The same native object/component drag and Undo transactions remain authoritative.',
      'VR transform picking and contact feedback use the same mode-aware hit path, with easier controller targets and existing menu/input priority preserved.',
      'This targets transform-handle usability; existing modeling operations, saved geometry, controller profiles and independent world-space menu placement remain compatible.'
    ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[at+length:]
