"""§E v11.520 — owner Quest QA: UV-textured sculpt, browser geometry pick,
trigger-held immersive move and native world-menu headset facing.
Append-only; no new tool menu, renderer, model schema or controller profile.
"""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_520_QUEST_SCULPT_TRIGGER_MENUS'
def one(s,before,after,label):
 n=s.count(before)
 if n!=1:raise AssertionError(('v11.520',label,n,before[:120]))
 return s.replace(before,after,1)
def section(s,start,end,fn):
 a=s.index(start);b=s.index(end,a)
 if a>=b:raise AssertionError(('v11.520 section order',start,end))
 return s[:a]+fn(s[a:b])+s[b:]
def apply(html):
 assert 'SWYRL_ENGINE_DEPLOY_MARKER: V11_519_QUEST_BROWSER_TRANSFORMS' in html
 xr=(ROOT/'runtime/model_vr_interaction_repair_v11_520.js').read_text('utf8')
 quest=(ROOT/'runtime/model_quest_browser_picking_v11_520.js').read_text('utf8')
 assert 'SE520_VR_INTERACTION_REPAIR_END' in xr
 assert 'SE520_QUEST_BROWSER_PICK_END' in quest
 # Real original Three.js Model Atelier closure; no alternate canvas picking.
 html=one(html,'/* ATELIER_BRIDGE_END */',quest+'\n/* ATELIER_BRIDGE_END */',
  'Quest Browser mesh picking after prior v11.519 selection controls')
 # Existing outer WebXR script, after all earlier native wrappers.
 html=one(html,'installPerformanceSettings();se189InstallPerfUI();',
  xr+'\ninstallPerformanceSettings();se189InstallPerfUI();',
  'on-frame XR gesture and native spatial panel alignment')

 def trigger(s):
  s=one(s,'const hit=se374GizmoContact(record);\n  if(!hit?.gizmo)return false;',
    """const hit=se374GizmoContact(record);
  // Trigger on a native handle still has highest priority. When the ray
  // instead hits an ALREADY selected mesh in Move/Grab, start continuous
  // free movement from the actual controller pose. First trigger on an
  // unselected mesh remains pure selection; panels always own their rays.
  const direct=!hit?.gizmo&&['move','grab'].includes(s.mode)?se340Hit(record,false):null;
  const chosen=se350Tools()?.selection?.();
  if(!hit?.gizmo&&!(direct?.id&&!direct.ui&&chosen?.ids?.includes(direct.id)))return false;""",
    'trigger-selected model direct move without replacing gizmo')
  s=one(s,"if(hit.axis==='uniform'&&mode!=='scale')return false;",
    "if(hit?.axis==='uniform'&&mode!=='scale')return false;",
    'only existing uniform handle has axis')
  s=one(s,"mode,axis:hit.axis,hand:pose,",
    "mode,axis:hit?.axis||null,hand:pose,se520DirectTrigger:!!direct?.id,se520Activated:false,",
    'record direct selected-model gesture')
  s=one(s,"se340Notice('Trigger drag · '+mode+' '+hit.axis.toUpperCase()+' · release applies · B cancels.');",
    "se340Notice(direct?.id?'Hold Trigger and move controller to move selected model · B cancels.':'Trigger drag · '+mode+' '+hit.axis.toUpperCase()+' · release applies · B cancels.');",
    'distinguish selected-mesh direct translation feedback')
  s=one(s,
    "se340FinishGesture(record);\n    else if(se340XR.gesture===session.gesture)",
    """session.gesture.se520DirectTrigger&&!session.gesture.se520Activated
      ?se340CancelGesture('Trigger tap selected the model; no move committed.')
      :se340FinishGesture(record);
    else if(se340XR.gesture===session.gesture)""",
    'cancel no-movement trigger taps without phantom native Undo')
  return s
 html=section(html,'/* SE512_MODEL_VR_TRIGGER_GIZMO_START','/* SE512_MODEL_VR_TRIGGER_GIZMO_END',trigger)

 def sculpt(s):
  # UV art is only a material: sculpt edits the native position attribute,
  # preserving the original UV attribute and paint PNG. Coarse source meshes
  # may have no vertices within the chosen brush radius; avoid silent no-op.
  s=one(s,"const radius = sample.radius ?? g.radius, strength = sample.strength ?? g.strength;",
    """let radius = sample.radius ?? g.radius;
    const strength = sample.strength ?? g.strength;
    let se520BrushAdjusted = false;
    if(g.part.uvPaintPNG && sample.center && !g.regionId){
      const attr=g.preview.attributes.position;
      let nearest=Infinity;
      for(let i=0;i<attr.count;i++){
        const dx=attr.getX(i)-sample.center[0],dy=attr.getY(i)-sample.center[1],dz=attr.getZ(i)-sample.center[2];
        const squared=dx*dx+dy*dy+dz*dz;
        if(squared<nearest)nearest=squared;
      }
      const distance=Math.sqrt(nearest);
      if(distance>radius&&distance<2.25){
        radius=Math.min(2.5,Math.max(radius,distance*1.28+.025));
        se520BrushAdjusted=true;
      }
    }""",
    'adaptive effective UV brush radius for sparse textured geometry')
  s=one(s,"return {ok: true, changed, affected, sampled: true};",
    "return {ok: true, changed, affected, sampled: true, se520BrushAdjusted, effectiveRadius:radius};",
    'allow user-facing UV brush radius feedback')
  return s
 html=section(html,'/* SE350_MODEL_VR_SURFACE_START','/* SE350_MODEL_VR_SURFACE_END',sculpt)
 # Native helper bound boxes are display only, not selectable polygons.
 def box(s):
  return one(s,
   "for(const outline of bounds()){outline.visible=boundsVisible;boundsApplied++;}",
   """for(const outline of bounds()){
    outline.visible=boundsVisible;
    if(quest())outline.raycast=function(){};
    boundsApplied++;
   }""",
   'Quest Browser boundary boxes cannot steal mesh ray selections')
 html=section(html,'/* SE519_QUEST_BROWSER_TRANSFORM_START','/* SE519_QUEST_BROWSER_TRANSFORM_END',box)

 # Sculpt UV textures occasionally use front-sided materials with mirrored
 # UV or inside-facing triangles. Retry only genuine textured geometry with a
 # temporary, immediately-restored double-sided raycast; never edit the
 # material, UV, texture, or selection itself to perform the stroke.
 def surface(s):
  return one(s,
   "  return finish({distance:1.2,point:cast.ray.at(1.2,new THREE.Vector3())});\n}\nfunction se340Pressed",
   """  if(se340XR.mode==='sculpt'){
    let selected=null;
    for(const entry of entries){
     const mesh=entry.mesh,mats=Array.isArray(mesh.material)?mesh.material:[mesh.material];
     if(!mesh.geometry?.getAttribute?.('uv')||!mats.some(m=>!!m?.map))continue;
     const saved=mats.map(m=>m?.side);
     let intersections=[];
     try{
      for(const mat of mats)if(mat?.map)mat.side=THREE.DoubleSide;
      intersections=cast.intersectObject(mesh,true);
     }finally{mats.forEach((m,i)=>{if(m)m.side=saved[i];});}
     for(const hit of intersections){
      if(hit.object.userData?.atelierHelper||hit.object.userData?.se350SurfacePreview)continue;
      if(!selected||hit.distance<selected.hit.distance)selected={entry,hit};
     }
    }
    if(selected)return finish({id:selected.entry.id,name:selected.entry.name,
     mesh:selected.entry.mesh,distance:selected.hit.distance,point:selected.hit.point,
     face:selected.hit.face,normal:selected.hit.normal});
   }
   return finish({distance:1.2,point:cast.ray.at(1.2,new THREE.Vector3())});
 }
 function se340Pressed""",
   'UV-textured mesh exact fallback raycast without side effects')
 html=section(html,'/* SE340_MODEL_VR_WORKSPACE_START','/* SE340_MODEL_VR_WORKSPACE_END',surface)
 html=one(html,
  "if(result?.ok===false)se340CancelGesture(result.error||'Sculpt source changed.');",
  """if(result?.ok===false)se340CancelGesture(result.error||'Sculpt source changed.');
  else if(result?.se520BrushAdjusted&&!g.se520RadiusNotice){
   g.se520RadiusNotice=true;
   se340Notice('Textured mesh has sparse vertices · sculpt radius adapted to '+result.effectiveRadius.toFixed(2)+' model units.');
  }""",
  'show one native-status notice when UV sculpt radius needs adjustment')
 for before,after in [
  ('SWYRL_ENGINE_DEPLOY_MARKER: V11_519_QUEST_BROWSER_TRANSFORMS',MARKER),
  ('ENGINE · MAKER v11.519','ENGINE · MAKER v11.520'),
  ('v11.519 · Quest browser gizmo drag, tap-deselect and bounds toggle',
   'v11.520 · textured sculpt, real 2D mesh picking, trigger-held moves and facing menus'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.519'",
   "window.SWRLZ_FORGE_BUILD={version:'v11.520'"),
  ('<title>§wyrl§ Engine · Maker v11.519</title>',
   '<title>§wyrl§ Engine · Maker v11.520</title>')
 ]:html=one(html,before,after,'runtime release identity')
 old=" source.engine='§wyrl§ Engine · Maker v11.519';source.version=11.519;"
 if html.count(old)!=5:raise AssertionError(('v11.520 provenance',html.count(old)))
 html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.520';source.version=11.520;")
 marker='const SE_RELEASE_NOTES=';at=html.index(marker)+len(marker)
 notes,length=json.JSONDecoder().raw_decode(html[at:])
 notes['history']=[v for v in notes.get('history',[]) if v.get('version')!='v11.519']
 notes['history'].insert(0,{'version':'v11.519','changes':notes.get('changes',[])})
 notes.update(version='v11.520',date='2026-11-18',
  title='Quest model sculpt and direct manipulation QA',
  changes=[
   'Immersive VR: sculpt on UV-painted meshes now uses the actual source triangles with a double-sided texture-aware fallback and adapts small brush radius when sparse original vertices otherwise receive zero influence; UV coordinates and painted image remain unchanged while mesh geometry edits save through native stroke Undo.',
   'Regular Quest Browser 2D: native BoxHelper selection boundaries never take controller ray hits. A surface hit is authoritative over helper candidates; clicking the same model still deselects while existing transform gizmo hit ownership remains highest priority.',
   'Immersive VR: selecting a model with Trigger still works. On the already-selected model in Move/Grab mode, holding Trigger and physically moving the controller now streams native move preview; release commits once, B cancels, and a micro-jitter tap performs no movement.',
   'Immersive VR: the original anchored three-stage world-space menu is reoriented toward the tracked headset every XR frame, including menu placement; its world position, current page, selected tool and native ray buttons do not relocate.',
   'No new controller profile, model format, alternate menu, renderer or browser context was introduced. Physical Quest acceptance remains pending.'
  ])
 return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[at+length:]
