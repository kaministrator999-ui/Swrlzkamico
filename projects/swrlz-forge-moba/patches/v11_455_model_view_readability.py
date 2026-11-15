"""§E v11.455 — native model viewport shading, topology clarity, and modes.

Keeps the pre-existing shaded/wireframe/X-Ray and six-axis camera source of
truth. Adds Solid, Flat, Clay and a viewport menu; its geometry is not edited.
"""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_455_VIEW_READABILITY'
def once(html,old,new):
 n=html.count(old)
 if n!=1:raise AssertionError(('v11.455 anchor',old[:150],n))
 return html.replace(old,new,1)

def apply(html):
 js=(ROOT/'runtime/model_view_readability_v11_455.js').read_text('utf8')
 css=(ROOT/'runtime/model_view_readability_v11_455.css').read_text('utf8')
 assert js.count('/* SE455_VIEW_READABILITY_START */')==1
 assert js.count('/* SE455_TRANSIENT_FACE_HIGHLIGHT_START */')==1
 html=once(html,'SWYRL_ENGINE_DEPLOY_MARKER: V11_454_INSET_TOP_STEPS',MARKER)
 html=once(html,'/* SE454_INSET_TOP_STEPS_END */',
  '/* SE454_INSET_TOP_STEPS_END */\n'+
  '/* Historical v11.454 marker: SWYRL_ENGINE_DEPLOY_MARKER: V11_454_INSET_TOP_STEPS */\n'+js)
 html=html.replace('</head>','<style id="se455ModelViewReadabilityStyles">\n'+css+'\n</style>\n</head>',1)
 html=once(html,
  "const atelierViewModes=['shaded','wireframe','overlay','xray'];",
  "const atelierViewModes=['shaded','solid','wireframe','overlay','xray','flat','clay'];")
 html=once(html,
  "let atelierViewGlobal='shaded',atelierViewOverrides=new Map();",
  "let atelierViewGlobal='solid',atelierViewOverrides=new Map();")
 helper="""/* SE455_NATIVE_SURFACE_SHADING_START */
// Crisp opaque geometry for modeling. The original material remains untouched
// and is available under Material mode; view settings are NEVER serialized.
function se455SolidSurface(mesh,part,mode){
 const base=mesh.material;
 if(!base||Array.isArray(base))return false;
 const color=mode==='clay'?new THREE.Color('#bbc5d0'):
   base.color?.clone?.()||new THREE.Color('#b9b8da');
 const mat=new THREE.MeshStandardMaterial({
  color,metalness:0,roughness:.89,flatShading:mode==='flat',
  transparent:false,opacity:1,depthTest:true,depthWrite:true,
  side:THREE.FrontSide,
  emissive:color.clone().multiplyScalar(.09),
  emissiveIntensity:.2
 });
 mat.userData={atelierViewportClone:true,se455ModelDisplay:true};
 mesh.material=mat;
 return true;
}
/* SE455_NATIVE_SURFACE_SHADING_END */
"""
 html=once(html,'function atelierViewModeApply(mesh,part){',
  helper+'\nfunction atelierViewModeApply(mesh,part){\n'+
  ' if(!mesh.userData.se455OriginalMaterial)mesh.userData.se455OriginalMaterial=mesh.material;\n'+
  " const se455Requested=atelierViewModeFor(part);\n"+
  " if(['solid','flat','clay'].includes(se455Requested)){\n"+
  "  if(part.kind==='faceSheet'&&atelierFaceHeatmap&&se455Requested==='solid'){atelierFaceVolumeHeatmap(mesh,part);return mesh;}\n"+
  "  if(se455SolidSurface(mesh,part,se455Requested))return mesh;\n"+
  " }")
 # Replace the triangle-lattice overlay with actual dihedral mesh edges, so
 # triangulated quads do not render a distracting diagonal/grid pattern.
 old=""" if(mode==='overlay'){
   const material=new THREE.MeshBasicMaterial({
     wireframe:true,color:atelierViewWireTint,
     transparent:true,opacity:.95,side:THREE.DoubleSide,
     depthTest:true,depthWrite:false,
     polygonOffset:true,polygonOffsetFactor:-2,polygonOffsetUnits:-2
   });
   const overlay=new THREE.Mesh(mesh.geometry,material);
   overlay.name='Viewport wireframe overlay';
   overlay.userData.atelierHelper=true;
   overlay.renderOrder=3;
   mesh.add(overlay);
 }"""
 new=""" if(mode==='overlay'){
   const geometry=new THREE.EdgesGeometry(mesh.geometry,18);
   const material=new THREE.LineBasicMaterial({
     color:atelierViewWireTint,transparent:true,opacity:.88,
     depthTest:true,depthWrite:false
   });
   const overlay=new THREE.LineSegments(geometry,material);
   overlay.name='Viewport wireframe overlay';
   overlay.userData.atelierHelper=true;
   overlay.userData.se455DisplayEdges=true;
   overlay.userData.se455OwnedGeometry=true;
   overlay.renderOrder=3;
   mesh.add(overlay);
 }"""
 html=once(html,old,new)
 html=once(html,
  "overlay:objs.filter(o=>o.children.some(c=>c.isMesh&&c.userData.atelierHelper)).length,",
  "overlay:objs.filter(o=>o.children.some(c=>(c.isMesh||c.isLineSegments)&&c.userData.atelierHelper)).length,")
 # Existing native preview record continues to own every helper allocation.
 old='window.se453RimBorderClear?.(record);'
 assert html.count(old)==2,('v11.455 rim cleanup count',html.count(old))
 html=html.replace(old,old+'\n  window.se455PreviewTintClear?.(record);')
 html=once(html,
  'window.se453RimBorderAdd?.(record);',
  'window.se453RimBorderAdd?.(record);\n  window.se455PreviewTintAdd?.(record);')
 for old,new in [
   ('ENGINE · MAKER v11.454','ENGINE · MAKER v11.455'),
   ('v11.454 · top-bar rim then inward depth','v11.455 · readable solid modeling and viewport modes'),
   ("window.SWRLZ_FORGE_BUILD={version:'v11.454'","window.SWRLZ_FORGE_BUILD={version:'v11.455'"),
   ('<title>§wyrl§ Engine · Maker v11.454</title>','<title>§wyrl§ Engine · Maker v11.455</title>')
 ]:html=once(html,old,new)
 prior=" source.engine='§wyrl§ Engine · Maker v11.454';source.version=11.454;"
 assert html.count(prior)==5,('v11.455 provenance',html.count(prior))
 html=html.replace(prior," source.engine='§wyrl§ Engine · Maker v11.455';source.version=11.455;")
 key='const SE_RELEASE_NOTES=';at=html.index(key)+len(key)
 notes,width=json.JSONDecoder().raw_decode(html[at:])
 notes['history']=[r for r in notes.get('history',[]) if r.get('version')!='v11.454']
 notes['history'].insert(0,{'version':'v11.454','changes':notes.get('changes',[])})
 notes.update(version='v11.455',date='2026-11-14',
  title='Readable modeling surfaces and discoverable viewport modes',
  changes=[
   'A compact touch-friendly View selector inside the model viewport exposes Solid, Material, Shaded Wire, Wireframe, X-Ray, Flat and Clay, plus existing Front/Right/Top/Three-quarter camera orientations.',
   'Solid is the model editing default: opaque rough material with depth writing and existing object color, avoiding unintended translucent/checkerboard surfaces. Material mode restores authored shading; none of these displays alters saved mesh material, topology or Undo.',
   'Shaded Wire uses angle-filtered dihedral edges rather than a triangle lattice; individual coplanar half-quads are no longer drawn as prominent diagonal wires.',
   'The valid transient native Inset/Extrude preview gains a subtle selected cap tint and retains its precise connected rim outline; helper meshes, GPU resources and highlights dispose on Apply, Cancel and replacement.',
   'Changing a view mode while Inset/Extrude preview is active updates only current live material and redraws without calling renderParts, so it cannot cancel or commit the pending geometry. Original two-stage sliders, touch gestures, native camera, advanced view settings and VR tools remain.'
  ])
 return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[at+width:]
