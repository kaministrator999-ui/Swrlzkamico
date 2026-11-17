"""§E v11.484 · UV-safe ring density, concentric topology and group transforms.

Surgical augmentation of the native se430 workshop. No alternate editor,
project persistence, source snapshot, or Undo implementation is introduced.
"""
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_484_RING_DETAIL_AND_TRANSFORMS'

def one(src,old,new):
 n=src.count(old)
 assert n==1,('v11.484 source anchor',old[:140],n)
 return src.replace(old,new,1)

def apply(html):
 assert 'SWYRL_ENGINE_DEPLOY_MARKER: V11_483_SORTING_HAT_STARTER' in html
 kernel=(ROOT/'runtime/model_ring_detail_kernel_v11_483.js').read_text('utf8')
 studio=(ROOT/'runtime/model_ring_detail_studio_v11_483.js').read_text('utf8')
 css=(ROOT/'runtime/model_ring_detail_studio_v11_483.css').read_text('utf8')
 assert '/* SE483_RING_DETAIL_KERNEL_END */' in kernel
 assert '/* SE483_RING_DETAIL_STUDIO_END */' in studio
 assert '/* SE483_RING_DETAIL_STUDIO_STYLES_END */' in css
 html=one(html,'/* SE482_RING_HEIGHT_LAYOUT_END */',
  '/* SE482_RING_HEIGHT_LAYOUT_END */\n'+kernel+'\n'+studio)
 # Native workshop operation list and allowlist are expanded conservatively.
 html=one(html,
  "ops=['inset','extrude','deleteFaces','solidify','splitEdge','subdivide','fillHole','repairNormals','ringTransform','ringRefine','ringExtrude']",
  "ops=['inset','extrude','deleteFaces','solidify','splitEdge','subdivide','fillHole','repairNormals','ringTransform','ringRefine','ringExtrude','ringDetail']")
 html=one(html,
  "for(const op of ['ringTransform','ringRefine','ringExtrude'])",
  "for(const op of ['ringTransform','ringRefine','ringExtrude','ringDetail'])")
 html=one(html,
  "if(operation==='ringTransform')return se466RingKernel.transform(p.topologyMesh,verts,params);",
  """if(operation==='ringTransform')return se483RingDetailKernel.transform(p.topologyMesh,verts,params);
   if(operation==='ringDetail')return se483RingDetailKernel.detail(p.topologyMesh,verts,params);""")
 html=one(html,
  "'amount','offset','tilt','scale','leftScale','rightScale','falloff','axis'].includes(k)",
  "'amount','offset','tilt','scale','leftScale','rightScale','falloff','axis','action','target','innerRings','spacing','plane','center','radius','pivot','twist'].includes(k)")
 # Store accurate membership of new rings in the native source descriptor on
 # Apply, after the existing Undo checkpoint. No speculative source edits
 # occur while the candidate is previewed.
 html=one(html,
  "  record.selectedVertices=Array.isArray(result.selectedVertices)?[...result.selectedVertices]:[];",
  """  record.selectedVertices=Array.isArray(result.selectedVertices)?[...result.selectedVertices]:[];
  record.ringMetadata=operation==='ringDetail'&&Array.isArray(result.ringRadii)?{
   partId:p.id,center:[...result.ringCenter],plane:result.ringPlane,
   radii:[...result.ringRadii],members:result.ringMembers.map(ids=>[...ids]),
   outerRadius:result.outerRadius,outerMembers:[...result.outerMembers]
  }:null;""")
 html=one(html,
  """  active=null;restore(record);checkpoint();record.part.topologyMesh=candidatePart.topologyMesh;delete record.part.runtimeLOD;""",
  """  active=null;restore(record);checkpoint();record.part.topologyMesh=candidatePart.topologyMesh;
  if(record.operation==='ringDetail'){
   if(record.ringMetadata)record.part.se483Rings=clone(record.ringMetadata);
   else if(record.stats?.operation==='ring-density-reduce')delete record.part.se483Rings;
  }
  delete record.part.runtimeLOD;""")
 pattern=r"const ordinary=new Set\(\[([^\]]+)\]\);"
 matches=list(re.finditer(pattern,html))
 assert len(matches)==1,('v11.484 native descriptor whitelist',len(matches))
 content=matches[0].group(1)
 assert "'se483Rings'" not in content
 html=html[:matches[0].start()]+("const ordinary=new Set(["+content+",'se483Rings']);")+html[matches[0].end():]
 # The viewport circle selection and native height controller remain unchanged.
 # This UI extends the selected Ring/Fill inspector without duplicating tools.
 html=html.replace('</head>',
  '<style id="se483RingDetailStudioStyles">\n'+css+'\n</style>\n</head>',1)
 for old,new in (
  ('SWYRL_ENGINE_DEPLOY_MARKER: V11_483_SORTING_HAT_STARTER',MARKER),
  ('ENGINE · MAKER v11.483','ENGINE · MAKER v11.484'),
  ('v11.483 · The Sorting Hat editable starter','v11.484 · ring detail and group transforms'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.483'","window.SWRLZ_FORGE_BUILD={version:'v11.484'"),
  ('<title>§wyrl§ Engine · Maker v11.483</title>',
   '<title>§wyrl§ Engine · Maker v11.484</title>')
 ):html=one(html,old,new)
 old=" source.engine='§wyrl§ Engine · Maker v11.483';source.version=11.483;"
 assert html.count(old)==5
 html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.484';source.version=11.484;")
 key='const SE_RELEASE_NOTES=';at=html.index(key)+len(key)
 notes,size=json.JSONDecoder().raw_decode(html[at:])
 notes['history']=[e for e in notes.get('history',[]) if e.get('version')!='v11.483']
 notes['history'].insert(0,{'version':'v11.483','changes':notes.get('changes',[])})
 notes.update(version='v11.484',date='2026-11-17',
  title='Ring vertex density, genuine inserted concentric subrings and precision group transforms',
  changes=[
   'A compact Ring/Fill inspector adds editable target vertices per circumference, previewed UV-preserving edge subdivision, and conservative safe midpoint reduction (unsupported arbitrary decimation is explicitly refused).',
   'Filled Ring can insert 1–8 connected concentric internal ring edges and vertices using bounded, shared-edge geometry cuts and original UV interpolation. Even or center/outer-biased ring spacing is supported.',
   'Inserted subrings are stored as source topology membership and selectable individually, including after rotating, lifting or relocating them.',
   'Position XYZ, rotation XYZ, scale, configurable selection/circle/custom pivot, edge-row falloff, and progressive ring twist all use native preview, Apply, Cancel and one Undo checkpoint.',
   'A conservative native mesh audit refuses degenerate, nonmanifold, over-budget, or invalid UV changes instead of damaging the painted model.',
   'Previous Ring Height and geometric Ring/Fill selection, viewport visibility gating, textures, UV Slide, projects, save, Face tools and VR controls remain available; physical device acceptance is separate.'
  ])
 return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[at+size:]
