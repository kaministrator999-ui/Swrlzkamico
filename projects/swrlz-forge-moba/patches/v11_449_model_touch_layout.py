"""§E v11.449 — restore model hierarchy track, dock resizers and two-finger camera.

The v11.448 resize bars occupied grid cells. Place original splitters on real
four-column borders without adding a grid row; restore Face-mode multitouch to
the existing native pinch/pan handler. Keep authored mesh/Undo boundaries.
"""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_449_MODEL_TOUCH_LAYOUT'
def one(s,old,new):
 n=s.count(old)
 if n!=1:raise AssertionError(('v11.449 source anchor',old[:165],n))
 return s.replace(old,new,1)

def apply(html):
 # Component selection sits before the camera in the original pointer dispatch.
 # Track touch first in component mode, then choose between camera multi-touch
 # and the original single-finger face/edge/vertex editor. Exactly one tracker
 # must own any given pointer event.
 html=one(html,
  "function atelierComponentPointerDown(e){\n if(atelierComponentMode==='mesh'||e.button!==0)return false;",
  """function atelierComponentPointerDown(e){
 if(atelierComponentMode==='mesh'||e.button!==0)return false;
 if(e.pointerType==='touch'&&atelierCameraPointerDown(e)){
  if(atelierComponentGesture)se447CameraOrbitStop(atelierComponentGesture,e,false);
  atelierComponentCancel();
  if(e.cancelable)e.preventDefault();
  return true;
 }""")
 html=one(html,
  "function atelierComponentPointerMove(e){\n if(atelierComponentDrag)return atelierComponentGizmoMove(e);",
  """function atelierComponentPointerMove(e){
 if(atelierComponentMode!=='mesh'&&e.pointerType==='touch'&&atelierCameraPointerMove(e)){
  if(e.cancelable)e.preventDefault();
  return true;
 }
 if(atelierComponentDrag)return atelierComponentGizmoMove(e);""")
 html=one(html,
  "function atelierComponentPointerUp(e){\n if(atelierComponentDrag)return atelierComponentGizmoUp(e);",
  """function atelierComponentPointerUp(e){
 if(atelierComponentMode!=='mesh'&&e.pointerType==='touch'&&atelierCameraPointerUp(e)){
  if(atelierComponentGesture)se447CameraOrbitStop(atelierComponentGesture,e,false);
  atelierComponentCancel();
  if(e.cancelable)e.preventDefault();
  return true;
 }
 if(atelierComponentDrag)return atelierComponentGizmoUp(e);""")
 html=one(html,
  "function atelierComponentCancel(){\n if(atelierComponentDrag){atelierComponentDrag=null;renderParts();}\n atelierComponentGesture=null;\n}",
  """function atelierComponentCancel(){
 if(atelierComponentDrag){atelierComponentDrag=null;renderParts();}
 if(atelierComponentGesture)se447CameraOrbitStop(atelierComponentGesture,null,false);
 atelierComponentGesture=null;
}""")

 # Resize grips retain the original pointerdown/move/up and keyboard handlers.
 # Bound changes against actual model body width and the live opposing dock,
 # not a fixed 'innerWidth - 430' unrelated to the new four-column layout.
 helper="""/* SE449_DOCK_SIZE_GUARD_START */
function se449ModelDockMetrics(){
 const panel=q('#modelAtelierPanel'),body=panel?.querySelector('.atelier-body');
 const width=body?.getBoundingClientRect?.().width||innerWidth;
 const rail=Number.parseFloat(getComputedStyle(panel).getPropertyValue('--se320-rail'))||78;
 return {width,rail,budget:Math.max(290,Math.floor(width-rail-190))};
}
function se449ModelDockFit(){
 const {budget}=se449ModelDockMetrics(),d=state.model;
 if(d.left+d.right<=budget)return;
 const original=d.left+d.right;
 let left=Math.max(145,Math.min(d.left,Math.round(budget*d.left/original)));
 let right=Math.max(145,Math.min(d.right,budget-left));
 if(left+right>budget)left=Math.max(145,budget-right);
 d.left=left;d.right=right;
}
function se449ModelDockMax(side){
 const {budget}=se449ModelDockMetrics();
 return Math.max(145,Math.min(480,budget-state.model[side==='left'?'right':'left']));
}
/* SE449_DOCK_SIZE_GUARD_END */
"""
 html=one(html,"function sync(){\n const mode=layout();",
    helper+"function sync(){\n const mode=layout();\n if(mode==='desktop')se449ModelDockFit();")
 html=one(html,
   "const bound=Math.max(180,innerWidth-430);",
   "const bound=what==='model'?se449ModelDockMax(side):Math.max(180,innerWidth-430);")
 html=one(html,
   "Math.min(475,state[what][side]+dirKey*10*dir)",
   "Math.min(what==='model'?se449ModelDockMax(side):475,state[what][side]+dirKey*10*dir)")
 # Preserve the native four-column editor; CSS overrides obsolete v11.448
 # in-grid splitter styles and old 19vw/30vw caps.
 style=(ROOT/'runtime/model_dock_touch_layout_v11_449.css').read_text(encoding='utf8')
 assert '</head>' in html
 html=html.replace('</head>','<style id="se449ModelTouchLayout">\n'+style+'\n</style>\n</head>',1)

 # A native topology mesh can retain source-indexed vertex deltas from the
 # earlier component transform tool. Offer an explicit one-step bake, with the
 # SAME native Undo safety and intact UV/triangle indices. Other authored
 # mesh types and invalid edits continue to be blocked.
 html=one(html,
 "if(p.sculptVertexEdits?.length&&(!['box','sphere','cylinder','cone'].includes(p.kind)||!atelierSculptVertexValid(p)))",
 "if(p.sculptVertexEdits?.length&&(!['box','sphere','cylinder','cone','topologyMesh'].includes(p.kind)||!atelierSculptVertexValid(p)))")
 html=one(html,
   "convert.available=['box','sphere','cylinder','cone'].includes(p.kind);",
   "convert.available=['box','sphere','cylinder','cone'].includes(p.kind)||(p.kind==='topologyMesh'&&!!p.sculptVertexEdits?.length);")
 html=one(html,
   "if(p.kind!=='topologyMesh'){\n   for(const op of ops)result[op].reason='Convert this plain primitive to editable topology first.';\n   return {operations:result,convert};\n  }",
   """if(p.kind!=='topologyMesh'){
   for(const op of ops)result[op].reason='Convert this plain primitive to editable topology first.';
   return {operations:result,convert};
  }
  if(p.sculptVertexEdits?.length){
   for(const op of ops)result[op].reason='Bake validated vertex edits into topology first; Undo preserves their source.';
   return {operations:result,convert};
  }""")
 # Explicit bake: existing topology meshes retain authored UV/indices. Only
 # verified matching geometry counts can replace the base vertex positions.
 html=one(html,
   "const bakedVertexEdits=!!p.sculptVertexEdits?.length;\n  let source,result;try{",
   "const bakedVertexEdits=!!p.sculptVertexEdits?.length;const sourceWasTopology=p.kind==='topologyMesh';\n  let source,result;try{")
 html=one(html,
   "if(bakedVertexEdits)atelierSculptApply(source,p);\n   result=se430MeshOps.convert(source);",
   """if(bakedVertexEdits)atelierSculptApply(source,p);
   if(p.kind==='topologyMesh'&&bakedVertexEdits){
    const attr=source.getAttribute?.('position'),base=p.topologyMesh;
    if(!attr||attr.count!==base.positions.length/3)return fail('Edited topology vertex count changed. Conversion would lose source mapping.');
    if(p.sculptVertexEdits.some(e=>e.resolution.some((v,i)=>v!==atelierSculptResolution(p)[i])||e.indices.some(id=>id>=attr.count)))
     return fail('Saved vertex edit resolution no longer matches this topology.');
    const positions=[];for(let id=0;id<attr.count;id++)positions.push(attr.getX(id),attr.getY(id),attr.getZ(id));
    const data={positions,uvs:[...base.uvs],indices:[...base.indices]};
    const checked=se430MeshOps.audit(data);
    result=checked.ok?{ok:true,data,stats:{operation:'bakeVertexEdits',sourceVertices:attr.count,facesAfter:base.indices.length/3,uvReprojected:false}}:checked;
   }else result=se430MeshOps.convert(source);""")
 html=one(html,
   "const candidate={...p,kind:'topologyMesh',topologyMesh:clone(result.data)};delete candidate.meshDensity;delete candidate.runtimeLOD;delete candidate.sculptVertexEdits;",
   "const candidate={...p,kind:'topologyMesh',topologyMesh:clone(result.data)};if(p.kind!=='topologyMesh')delete candidate.meshDensity;delete candidate.runtimeLOD;delete candidate.sculptVertexEdits;")
 html=one(html,
   "checkpoint();p.kind='topologyMesh';p.topologyMesh=candidate.topologyMesh;delete p.meshDensity;delete p.runtimeLOD;delete p.sculptVertexEdits;",
   "checkpoint();p.kind='topologyMesh';p.topologyMesh=candidate.topologyMesh;if(!sourceWasTopology)delete p.meshDensity;delete p.runtimeLOD;delete p.sculptVertexEdits;")
 # Preserve meshDensity for source-mapped topology vertex edits; primitive
 # conversion may still clear the procedural density parameter as before.

 for old,new in [
  ('SWYRL_ENGINE_DEPLOY_MARKER: V11_448_INSET_DOCK_USABILITY',MARKER),
  ('ENGINE · MAKER v11.448','ENGINE · MAKER v11.449'),
  ('v11.448 · actionable Inset and aligned panel grips','v11.449 · repaired model layout, grips and multitouch'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.448'","window.SWRLZ_FORGE_BUILD={version:'v11.449'"),
  ('<title>§wyrl§ Engine · Maker v11.448</title>','<title>§wyrl§ Engine · Maker v11.449</title>')
 ]:html=one(html,old,new)
 old=" source.engine='§wyrl§ Engine · Maker v11.448';source.version=11.448;"
 assert html.count(old)==5,('v11.449 provenance',html.count(old))
 html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.449';source.version=11.449;")
 key='const SE_RELEASE_NOTES=';at=html.index(key)+len(key)
 notes,width=json.JSONDecoder().raw_decode(html[at:])
 notes['history']=[x for x in notes.get('history',[]) if x.get('version')!='v11.448']
 notes['history'].insert(0,{'version':'v11.448','changes':notes.get('changes',[])})
 notes.update(version='v11.449',date='2026-11-14',
   title='Model hierarchy layout, live resize grips and restored multitouch',
   changes=[
    'The Meshes hierarchy now occupies the first column of the same editor row as the viewport, tool rail and inspector. The previous in-grid splitter reservation that pushed it beneath the viewport is removed.',
    'Model-dock splitters retain their actual pointer capture and keyboard resizing. Their handles are absolutely anchored to the hierarchy/viewport and rail/inspector boundaries, with width budgets preserving a usable central viewport.',
    'Two-finger pinch and pan now receive the original native touch-start/move/end events even when Face, Edge or Vertex component selection is active. One-finger selection and live orbit remain unchanged; switching to multitouch cancels pending component orbit.',
    'The 3D canvas disables browser touch zoom interception but normal sidebar scrolling remains enabled.',
    'Existing topology meshes with validated source-indexed vertex edits can be explicitly baked without reindexing triangles or resetting UVs; one native Undo checkpoint preserves the original edit layers. Protected or invalid mesh sources remain guarded.'
   ])
 return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[at+width:]
