"""§E v11.390 — fluent controller shortcuts for native selection, manipulation and creation."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_390_MODEL_VR_FLUENT_HOTKEYS'
def one(src,old,new):
    assert src.count(old)==1,('v11.390 anchor',old[:110],src.count(old))
    return src.replace(old,new,1)
def apply(html):
    native=(ROOT/'runtime/model_vr_quick_create_v11_390.js').read_text('utf8')
    html=one(html,'/* ATELIER_BRIDGE_END */',native+'\n/* ATELIER_BRIDGE_END */')
    html=one(html,'vrSurface:se350ModelSurface,chatAction:',
             'vrSurface:se350ModelSurface,vrCreate:se390ModelCreate,chatAction:')
    html=one(html,(ROOT/'runtime/model_vr_input_profile_v11_350.js').read_text('utf8'),
             (ROOT/'runtime/model_vr_input_profile_v11_390.js').read_text('utf8'))
    a=html.index('/* SE360_MODEL_VR_UI_START */');b=html.index('/* SE360_MODEL_VR_UI_END */',a)+len('/* SE360_MODEL_VR_UI_END */')
    html=html[:a]+(ROOT/'runtime/model_studio_vr_ui_v11_390.js').read_text('utf8').rstrip()+html[b:]
    runtime='\n'.join((ROOT/'runtime'/n).read_text('utf8') for n in ['model_vr_grab_v11_390.js','model_vr_fluent_tools_v11_390.js','model_vr_hotkey_hints_v11_390.js'])
    html=one(html,'const se340Bridge=()=>ModelAtelier?.xrBridge;',
             'const se340Bridge=()=>ModelAtelier?.xrBridge;\n'+runtime)
    html=one(html,"const ACTIONS=new Set(['tool-wheel'","const ACTIONS=new Set(['create-menu','tool-wheel'")
    html=one(html,"if(s.mode==='two-hand'){\n  const pair=se350Pair();",
             "if(s.mode==='grab')return se390BeginGrab(record,purpose,pose);\n if(s.mode==='two-hand'){\n  const pair=se350Pair();")
    html=one(html,'axis};se372GuideStart(s.gesture);','axis};se390BeginPose(s.gesture,pose);se372GuideStart(s.gesture);')
    html=one(html,"if(g.kind==='sculpt'){se350UpdateStroke(g);return;}",
             "if(g.kind==='group'){se390UpdatePose(g,pose,gain);return;}\n if(g.kind==='sculpt'){se350UpdateStroke(g);return;}")
    old="""if(g.kind==='extrude'){
  const delta=pose.position.clone().applyMatrix4(g.rootInverse).sub(g.hand.position.clone().applyMatrix4(g.rootInverse));
  const result=se350Surface().extrudeUpdate(delta.dot(g.normal)*gain);if(result?.ok===false)se340CancelGesture(result.error);return;
 }"""
    html=one(html,old,"if(g.kind==='extrude'){se390UpdateExtrude(g,pose,gain);return;}")
    html=one(html,"""translation.copy(mid).applyMatrix4(g.rootInverse).sub(g.pair.mid.clone().applyMatrix4(g.rootInverse)).multiplyScalar(gain);
  scale=Math.pow(THREE.MathUtils.clamp(span.length()/g.pair.distance,.05,20),gain);
  const world=new THREE.Quaternion().setFromUnitVectors(g.pair.span.clone().normalize(),span.normalize());
  rotation.slerp(g.rootQuaternion.clone().invert().multiply(world).multiply(g.rootQuaternion),gain);""",
      "const candidate=se390PairCandidate(g,mid,span,gain);translation.fromArray(candidate.translation);rotation.fromArray(candidate.rotation);scale=candidate.scale;")
    html=one(html,"if(s.mode==='extrude'){\n  if(!hit?.id)return false;\n  se350Tools().select(hit.id);\n  const result=se350Surface().extrudeBegin(hit.id);",
        "if(s.mode==='extrude'){\n  const chosen=se350Tools().selection(),id=chosen.primaryId||chosen.ids[0];\n  if(!id){se340Notice('Select an outline face before extruding.');return false;}\n  const result=se350Surface().extrudeBegin(id);")
    html=one(html,"s.gesture={kind:'extrude',record,id:hit.id,mode:'extrude'", "s.gesture={kind:'extrude',record,id,mode:'extrude'")
    html=one(html,"Point at a drawn face, hold grip and pull to add thickness.","Selected outline · hold grip and pull to add thickness; B cancels.")
    html=one(html,"if(!['move','rotate','scale'].includes(g.mode)||!g.record?.target)return;", "if(!['move','rotate','scale','grab'].includes(g.mode)||!g.record?.target)return;")
    html=one(html,"if(g.mode==='move'){\n  const shift=translation.clone()", "if(g.mode==='move'||g.mode==='grab'){\n  const shift=translation.clone()")
    html=one(html,"}else if(g.mode==='scale')guide.live.scale.setScalar(THREE.MathUtils.clamp(scale,.4,1.8));", "}else if(g.mode==='scale')guide.live.scale.setScalar(THREE.MathUtils.clamp(scale,.4,1.8));\n if(g.mode==='grab')guide.live.scale.setScalar(THREE.MathUtils.clamp(scale,.4,1.8));")
    html=one(html,"if(!s.inputSample?.buttons?.LT?.physical||!w.record.targetTracked", "if(!(w.keys||['LT']).every(key=>s.inputSample?.buttons?.[key]?.physical)||!w.record.targetTracked")
    html=one(html,'const bounds=focus&&selected?se340PartBox(selected.mesh):allBounds;',
        "const ids=new Set(se350Tools().selection().ids),selectedBounds=new THREE.Box3();\n for(const entry of entries)if(ids.has(entry.id))selectedBounds.union(se340PartBox(entry.mesh));\n const bounds=focus&&!selectedBounds.isEmpty()?selectedBounds:allBounds;")
    html=one(html,'se350Dispatch(sample);se350Navigate(sample,dt);','se390CreationFrame(s,dt);se350Dispatch(sample);se350Navigate(sample,dt);')
    html=one(html,"const state={selectedRegionId:", "const state={creationActive:!!s.se390Creation,creationKind:s.se390Creation?.kind||'',creationSize:s.se390Creation?.factor||1,selectedRegionId:")
    html=one(html,"s.session=requested;s.mode='inspect';", "s.se390AxisLatch=null;\n  s.session=requested;s.mode='inspect';")
    for before,after in [
        ('SWYRL_ENGINE_DEPLOY_MARKER: V11_381_XR_GUEST_HOST_SYNC',MARKER),
        ('ENGINE · MAKER v11.381','ENGINE · MAKER v11.390'),
        ('v11.381 · Quest guest multiplayer movement','v11.390 · fluent Grab, selection and creation shortcuts'),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.381'","window.SWRLZ_FORGE_BUILD={version:'v11.390'"),
        ('<title>§wyrl§ Engine · Maker v11.381</title>','<title>§wyrl§ Engine · Maker v11.390</title>')]:html=one(html,before,after)
    previous=" source.engine='§wyrl§ Engine · Maker v11.381';source.version=11.381;"
    assert html.count(previous)==5,('v11.390 native provenance',html.count(previous))
    html=html.replace(previous," source.engine='§wyrl§ Engine · Maker v11.390';source.version=11.390;")
    key='const SE_RELEASE_NOTES=';at=html.index(key)+len(key);notes,size=json.JSONDecoder().raw_decode(html[at:])
    if not any(x.get('version')=='v11.381' for x in notes.get('history',[])):
        notes.setdefault('history',[]).insert(0,{'version':'v11.381','changes':notes.get('changes',[])})
    notes.update(version='v11.390',date='2026-11-10',title='Select, Grab and create with fewer controller steps',changes=[
        'Selecting a part from Inspect explicitly arms Grab. Right grip moves and turns the existing selection together, its stick sizes while held, and the off-hand trigger provides a precision clutch without jumping the preview. Inspect itself remains geometry-safe.',
        'A taps cycle Move, Rotate and Scale only; hold A for broader tools. X+A opens Create, and X+Trigger duplicates the selected group in one native Undo step. Custom profiles and mirrored controls dispatch actual actions with updated contextual labels.',
        'Create Cube, Sphere, Cylinder or Cone with a native ghost preview, point into the workspace and confirm with a fresh Trigger press. B, tracking/source changes and VR exit discard uncommitted previews. New parts hand directly to Grab.',
        'Group focus frames the whole selection; Draw hands off to selected-face extrusion without precise re-aiming. Selection sweeps follow their mapped input instead of a fixed physical left trigger.',
        'Native sculpt, selector lassos, movable menus, account/project actions, camera orbit, controller models, image/UV tools and current graphics settings remain in place.'
    ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+size:]
