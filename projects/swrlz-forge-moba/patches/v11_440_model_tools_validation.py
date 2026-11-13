"""§E v11.440 — preserve outline extrusion and predictable tool previews."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_440_MODEL_TOOLS_VALIDATION'
def one(html,old,new):
    assert html.count(old)==1,('v11.440 anchor',old[:100],html.count(old))
    return html.replace(old,new,1)
def apply(html):
    # Native drawn outlines have n boundary vertices and n-2 triangles. This
    # conservative routing hint leaves their full validation and live thickness
    # transaction with the original surface tool; it never edits geometry.
    old="if(!part||!['box','topologyMesh'].includes(part.kind))return se436PreviousModelXRAction(action,record);"
    new="""const t=part?.kind==='topologyMesh'?part.topologyMesh:null;
 // SE440_NATIVE_OUTLINE_ROUTE: preserve Draw -> Thicken outline.
 const outline=Array.isArray(t?.positions)&&Array.isArray(t?.indices)&&
  t.positions.length>=9&&t.positions.length%3===0&&
  t.indices.length===(t.positions.length/3-2)*3;
 if(!part||!['box','topologyMesh'].includes(part.kind)||outline)return se436PreviousModelXRAction(action,record);"""
    html=one(html,old,new)
    html=one(html,"op==='inset'?.03:op==='extrude'?-4:.005","op==='inset'?.03:op==='extrude'?-4:op==='subdivide'?.025:.005")
    html=one(html,"operation.addEventListener('change',()=>{\n  const config=se430BeginnerAmount(operation.value)","""operation.addEventListener('change',()=>{
  // SE440_TOOL_PREVIEW_IDENTITY: guide links may change a disabled selector.
  const api=se430BeginnerAPI();
  if(api?.inspect().preview.active)api.cancel('Tool changed. Preview again to review the new operation before Apply.');
  const config=se430BeginnerAmount(operation.value)""")
    html=one(html,"if(id.startsWith('accessory-')&&!accessoryNavigation.has(id)&&!state.accessoryActive)return false;", "if(['accessory-body','accessory-details','accessory-fit'].includes(id)&&!state.accessoryActive)return false;\nif(id.startsWith('accessory-')&&!accessoryNavigation.has(id)&&!state.accessoryActive)return false;")
    html=one(html,"if(!state.accessoryActive&&id.startsWith('accessory-')&&!accessoryNavigation.has(id))return 'Start a pouch preview first';", "if(!state.accessoryActive&&id.startsWith('accessory-')&&id!=='accessory-menu')return 'Start a pouch preview first';")
    html=one(html,"const hit=raycaster.intersectObject(mesh,false)[0],triangle=top.tri[hit?.faceIndex];", """const hit=raycaster.intersectObject(mesh,false)[0];
 let triangle=top.tri[hit?.faceIndex];
 // SE440_TOUCH_COMPONENT_BORDER: nearby front-surface samples tolerate a
 // rounded phone tap on a silhouette. Bound work to eight extra raycasts;
 // retain native vertex/edge distance checks and exact face/mouse picking.
 if(!triangle&&e.pointerType==='touch'&&['vertex','edge'].includes(atelierComponentMode)){
  const center=point(e),rect=renderer.domElement.getBoundingClientRect();
  if(rect.width>0&&rect.height>0)for(const [dx,dy] of [[-12,0],[12,0],[0,-12],[0,12],[-8,-8],[-8,8],[8,-8],[8,8]]){
   mouse.set(center.x+dx*2/rect.width,center.y-dy*2/rect.height);raycaster.setFromCamera(mouse,camera);
   const nearby=raycaster.intersectObject(mesh,false)[0];triangle=top.tri[nearby?.faceIndex];if(triangle)break;
  }
  mouse.set(center.x,center.y);raycaster.setFromCamera(mouse,camera);
 }""")
    assembly_sync="""/* SE440_ASSEMBLY_MENU_SYNC_START */
// Refresh source-owned assembly controls when loading/reopening/Undo changes
// the native document, not on every pointer preview or animation frame.
let se440AssemblyDocument=null,se440AssemblySource=null,se440AssemblyPicker=null;
const se440PreviousInspector=refreshInspector;
refreshInspector=function(...args){
 const result=se440PreviousInspector.apply(this,args),doc=model(),source=doc?.assemblies,picker=$m('AssemblyComponent');
 if(doc!==se440AssemblyDocument||source!==se440AssemblySource||picker!==se440AssemblyPicker){
  se440AssemblyDocument=doc;se440AssemblySource=source;se440AssemblyPicker=picker;
  atelierAssemblyRefresh();
 }
 return result;
};
/* SE440_ASSEMBLY_MENU_SYNC_END */
"""
    html=one(html,'/* SE430_MODEL_WORKSHOP_BRIDGE_END */','/* SE430_MODEL_WORKSHOP_BRIDGE_END */\n'+assembly_sync)
    html=one(html,"try{return !!frame.getPose(space,renderer.xr.getReferenceSpace());}catch(_){return false;}","""try{
  // SE440_CURRENT_CONTROLLER_POSE: model VR has its own native XR callback;
  // Three's event/controller update can precede or follow it. Reuse this
  // existing tracking pose query so tool rays/grips use this exact frame and
  // the current offset reference space, including after camera presets.
  const pose=frame.getPose(space,renderer.xr.getReferenceSpace()),node=kind==='grip'?record.grip:record.target,matrix=pose?.transform?.matrix;
  if(!node||!matrix||matrix.length!==16||!Array.from(matrix).every(Number.isFinite))return false;
  node.matrix.fromArray(matrix);node.matrix.decompose(node.position,node.quaternion,node.scale);node.matrixWorldNeedsUpdate=true;
  return true;
 }catch(_){return false;}""")
    html=one(html,"return raycaster.intersectObjects(targets,false)[0]||null;}","root.updateWorldMatrix(true,true);return raycaster.intersectObjects(targets.filter(target=>target.visible!==false),false)[0]||null;} // SE440_VISIBLE_MENU_TARGETS")
    for before,after in [
        ('SWYRL_ENGINE_DEPLOY_MARKER: V11_439_SHEEP_CAPTURE_PURSUIT',MARKER),
        ('ENGINE · MAKER v11.439','ENGINE · MAKER v11.440'),
        ('v11.439 · smooth wolf pursuit and capture diagnosis','v11.440 · checked VR and touch modeling tools'),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.439'","window.SWRLZ_FORGE_BUILD={version:'v11.440'"),
        ('<title>§wyrl§ Engine · Maker v11.439</title>','<title>§wyrl§ Engine · Maker v11.440</title>')
    ]:html=one(html,before,after)
    old=" source.engine='§wyrl§ Engine · Maker v11.439';source.version=11.439;"
    assert html.count(old)==5,('v11.440 provenance',html.count(old))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.440';source.version=11.440;")
    key='const SE_RELEASE_NOTES=';at=html.index(key)+len(key);notes,n=json.JSONDecoder().raw_decode(html[at:])
    notes['history']=[x for x in notes.get('history',[]) if x.get('version')!='v11.439']
    notes['history'].insert(0,{'version':'v11.439','changes':notes.get('changes',[])})
    notes.update(version='v11.440',date='2026-11-13',title='Model tools checked for VR and touch',changes=[
        'Drawn outline faces keep the native Thicken outline grip preview, Apply on release, Cancel and Undo. The cube face Extrude shortcut still opens the manual face workshop.',
        'VR Subdivide amount stops at the native minimum target edge length of 0.025, avoiding an invalid enabled preview.',
        'Changing a manual mesh tool through the learning guide cancels the previous preview so Apply cannot commit geometry from a different tool.',
        'Phone vertex/edge picks tolerate small triangle misses at a mesh silhouette, with at most eight extra selected-mesh raycasts and unchanged mouse/face selection.',
        'Loading or restoring a model refreshes its native assembly-motion picker instead of retaining the previous project choices.',
        'VR tool rays and grips reuse the existing current-frame tracking pose, preventing stale controller matrices after offset-space camera changes. Head tracking and the XR loop remain native.',
        'Hidden VR menu cards are excluded from ray picking while visible disabled cards retain pointer ownership.',
        'Accessory shape/detail/fit cards explain that a pouch preview is required and stay disabled until one is active.',
        'Focused native, controller-emulation and Android touch checks are recorded separately from physical-device acceptance. Existing incomplete modeling operations remain clearly labeled.'
    ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[at+n:]
