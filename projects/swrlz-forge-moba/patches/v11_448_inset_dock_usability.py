"""§E v11.448: usable Inset on edited cubes and aligned Model Studio dock grips.

Preserves rendered sculpt-vertex changes through an explicit, undoable topology
bake only for safe primitive parts. Does not bypass authored-texture/rig guards,
mutate geometry merely by choosing a tool, or add a second modeling editor.
"""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_448_INSET_DOCK_USABILITY'
def one(s,old,new):
    count=s.count(old)
    if count!=1:raise AssertionError(('v11.448 anchor',old[:145],count))
    return s.replace(old,new,1)

def apply(html):
    # Native workshop: permit explicitly supported, checked source-indexed
    # vertex moves on a plain primitive, not arbitrary authored asset metadata.
    html=one(html,
      "'meshDensity','topologyMesh','runtimeLOD']);",
      "'meshDensity','topologyMesh','runtimeLOD','sculptVertexEdits']);")
    html=one(html,
      """if(Object.keys(p).some(key=>!ordinary.has(key)))return 'This mesh has authored deformation, paint, texture, rig or procedural data. Keep that source intact; use a plain independent mesh.';""",
      """if(Object.keys(p).some(key=>!ordinary.has(key)))return 'This mesh has protected paint, texture, rig or procedural data. Create an independent plain mesh for topology editing.';
  if(p.sculptVertexEdits?.length&&(!['box','sphere','cylinder','cone'].includes(p.kind)||!atelierSculptVertexValid(p)))
   return 'These vertex edits cannot be safely baked here. Use an independent plain mesh.';""")
    html=one(html,
      "if(convert.available)convert.reason='Creates welded editable topology and regenerates plain UV coordinates. Convert only when you are ready to edit faces.';",
      """if(convert.available)convert.reason=p.sculptVertexEdits?.length?
   'Bake saved vertex edits into welded editable topology, regenerating plain UVs; Undo preserves the original editable source.':
   'Creates welded editable topology and regenerates plain UV coordinates. Convert only when you are ready to edit faces.';""")
    html=one(html,
      "let source,result;try{source=atelierCourierBaseGeometry(p);result=se430MeshOps.convert(source);}",
      """const bakedVertexEdits=!!p.sculptVertexEdits?.length;
  let source,result;try{
   source=atelierCourierBaseGeometry(p);
   if(bakedVertexEdits)atelierSculptApply(source,p);
   result=se430MeshOps.convert(source);
  }""")
    html=one(html,
      "const candidate={...p,kind:'topologyMesh',topologyMesh:clone(result.data)};delete candidate.meshDensity;delete candidate.runtimeLOD;",
      "const candidate={...p,kind:'topologyMesh',topologyMesh:clone(result.data)};delete candidate.meshDensity;delete candidate.runtimeLOD;delete candidate.sculptVertexEdits;")
    html=one(html,
      "checkpoint();p.kind='topologyMesh';p.topologyMesh=candidate.topologyMesh;delete p.meshDensity;delete p.runtimeLOD;",
      "checkpoint();p.kind='topologyMesh';p.topologyMesh=candidate.topologyMesh;delete p.meshDensity;delete p.runtimeLOD;delete p.sculptVertexEdits;")
    html=one(html,
      "publish('Primitive converted to welded editable topology. Plain UV coordinates were regenerated. Pick a face region; Undo restores the primitive.');",
      "publish(bakedVertexEdits?'Saved vertex edits baked into welded editable topology. Select a face region; Undo restores the original edit layers.':'Primitive converted to welded editable topology. Plain UV coordinates were regenerated. Pick a face region; Undo restores the primitive.');")
    # The existing quick buttons now follow a live native operation path.
    adapter=(ROOT/'runtime/model_shape_quick_actions_v11_448.js').read_text(encoding='utf-8')
    html=one(html,
      " faceQuick.addEventListener('click',event=>{",
      adapter+"\n faceQuick.addEventListener('click',event=>{")
    old="""  if(state.selection.partId&&state.selection.mode!=='face')api.setComponentMode('face');
  if(operation==='more')window.SWYRL_E_UNIFIED_TOOLS?.select?.('Topology','Manual mesh modeling');
  else se430BeginnerNavigate(operation);
  se430BeginnerWrite(hint,(operation==='more'?'All face tools':button.textContent)+' · select a flat region. Convert a plain primitive first, then Preview / Apply.');
  se430BeginnerQueue();"""
    new="""  if(operation==='more'){
   window.SWYRL_E_UNIFIED_TOOLS?.select?.('Topology','Manual mesh modeling');
   se430BeginnerWrite(hint,'All native face operations are in Topology. Pick a valid face then Preview / Apply.');
   se430BeginnerQueue();
   return;
  }
  se448ShapeQuickActivate(faceQuick,operation);"""
    html=one(html,old,new)
    html=one(html,
      "Pick a tool, select a face region, then Preview and Apply. Plain primitives need Make mesh editable first.",
      "Select a face and tap Inset or Extrude to preview. Editable cubes with vertex edits can be safely baked with confirmation.")
    # Existing splitters remain the sole input owners; align them to actual
    # model grid tracks, including the independently-collapsed right dock.
    styles=(ROOT/'runtime/model_dock_grip_alignment_v11_448.css').read_text(encoding='utf-8')
    assert '<body' in html and '</head>' in html
    html=html.replace('</head>','<style id="se448DockGripAlignment">\n'+styles+'\n</style>\n</head>',1)
    for before,after in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_447_SMOOTH_FACE_ORBIT',MARKER),
      ('ENGINE · MAKER v11.447','ENGINE · MAKER v11.448'),
      ('v11.447 · smooth face and preview camera orbit','v11.448 · actionable Inset and aligned panel grips'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.447'","window.SWRLZ_FORGE_BUILD={version:'v11.448'"),
      ('<title>§wyrl§ Engine · Maker v11.447</title>','<title>§wyrl§ Engine · Maker v11.448</title>')
    ]:html=one(html,before,after)
    old=" source.engine='§wyrl§ Engine · Maker v11.447';source.version=11.447;"
    assert html.count(old)==5,('v11.448 provenance',html.count(old))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.448';source.version=11.448;")
    key='const SE_RELEASE_NOTES=';at=html.index(key)+len(key)
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    notes['history']=[entry for entry in notes.get('history',[]) if entry.get('version')!='v11.447']
    notes['history'].insert(0,{'version':'v11.447','changes':notes.get('changes',[])})
    notes.update(version='v11.448',date='2026-11-14',
      title='Inset preview on selected faces and properly docked resize grips',
      changes=[
      'Inset/Extrude Shape shortcuts run the existing native Preview whenever a valid face is already selected. Preview remains non-destructive; Apply is still required to commit a mesh edit.',
      'A plain cube with saved component-vertex edits can be explicitly converted through a confirmation prompt: source-indexed deformations are baked into the native welded mesh, with one Undo checkpoint and safe removal of consumed edit layers. Painted, rigged and procedural parts remain guarded.',
      'On conversion the tapped face is reselected through the native connected planar-region operation, so the current square face continues directly into Inset preview without manually hunting for Convert or Select flat region.',
      'The old purple sidebar resize handles now occupy the real hierarchy/viewport and tools/inspector grid boundaries rather than using stale two-column absolute offsets. Collapsed inspector and compact layout hide only the handles that no longer correspond to visible docks.',
      'Single existing panel ownership, native input, selected geometry, Save/Load, Preview/Apply/Cancel, camera controls, transform gizmos, Undo and VR menus are preserved.'
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[at+width:]
