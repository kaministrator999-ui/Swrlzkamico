"""§E v11.510: previewable cone-sector UVs and measurable distortion, preserving legacy projection."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_510_CONE_AWARE_UV'
PARENT_SHA='26367c6cc6273c1017aeaa2a428ce5c51cf21a50a637adaf7067fab3f9c1b03e'
def once(html,old,new,label):
 n=html.count(old)
 if n!=1:raise AssertionError(('v11.510 '+label,n,old[:120]))
 return html.replace(old,new,1)
def apply(html):
 assert hashlib.sha256(html.encode('utf8')).hexdigest()==PARENT_SHA,'v11.509 sealed source changed'
 assert 'SE503_UV_ISLAND_MATH_START' in html and 'SE508_UV' not in html or 'V11_508_UV_DEGENERATE_PREVIEW' in html
 helper=(ROOT/'runtime/model_uv_cone_metric_v11_510.js').read_text('utf8')
 assert 'SE510_CONE_AWARE_UV_START' in helper
 html=once(html,'/* SE503_UV_ISLAND_MATH_START',helper+'\n/* SE503_UV_ISLAND_MATH_START','helper before atlas math')
 html=once(html,
  "  const preset=options.preset==='panels'?'panels':'panels-rim';",
  """  const requested=options.preset||'auto-rim';
  const preset=requested==='panels'?'panels':'panels-rim';""",
  'projection request')
 html=once(html,
  "  const cut=yMin+(yMax-yMin)*cutFraction;\n  let degenerate3D=0,valid3D=0;",
  """  const cut=yMin+(yMax-yMin)*cutFraction;
  const coneProfile=se510ConeUV.profile(t,cut,yMax);
  const useCone=(requested==='auto-rim'||requested==='cone-rim')&&coneProfile.tapered;
  if(requested==='cone-rim'&&!coneProfile.tapered)
   throw Error('Cone-aware projection requires an upright tapered crown. Select Auto or Flat panels for this model.');
  let degenerate3D=0,valid3D=0;""",
  'cone fallback')
 html=once(html,
  "   const coords=p.map(v=>project(v,group));",
  "   const coords=p.map(v=>useCone&&group<2?se510ConeUV.project(v,group,coneProfile):project(v,group));",
  'curved crown projection')
 html=once(html,
  "  return {data:next,stats:stats.filter(s=>s.count).map(({id,name,color,count,rect,collapsed})=>({",
  """  const distortion=se510ConeUV.compare(t,tris,coneProfile,useCone);
  return {data:next,distortion,projectionMode:useCone?'cone-surface':'flat-panels',
   stats:stats.filter(s=>s.count).map(({id,name,color,count,rect,collapsed})=>({""",
  'surface distortion metrics')
 html=once(html,
  "let se503Preview=null,se503Tweaks={},se503Preset='panels-rim',se503Brim=.18;",
  "let se503Preview=null,se503Tweaks={},se503Preset='auto-rim',se503Brim=.18;",
  'default automatic tapered detection')
 html=once(html,
  """'<label>Projection <select id="se503Preset"><option value="panels-rim">Front / back / brim / underside</option><option value="panels">Front and back only</option></select></label>'+""",
  """'<label>Projection <select id="se503Preset"><option value="auto-rim">Auto · cone-aware for tapered meshes</option><option value="cone-rim">Cone surface + separate brim</option><option value="panels-rim">Flat panels + separate brim (legacy)</option><option value="panels">Front and back only (legacy)</option></select></label>'+""",
  'selector includes measured cone and legacy')
 html=once(html,
  """'<canvas id="se503AtlasCanvas" width="768" height="768" hidden></canvas>'+""",
  """'<label style="justify-content:flex-start"><input id="se510StretchHeat" type="checkbox"> Color UV distortion (green = low, red = high)</label>'+
 '<canvas id="se503AtlasCanvas" width="768" height="768" hidden></canvas>'+""",
  'diagnostic color toggle')
 html=once(html,
  """  ctx.globalAlpha=.33;ctx.stroke();""",
  """  if(face.group<2&&root.querySelector('#se510StretchHeat')?.checked){
   const points=face.sourceIds.map(id=>info.part.topologyMesh.positions.slice(id*3,id*3+3));
   const sample=se510ConeUV.stretch(points,pts);
   const d=sample?.ratio||1;
   ctx.fillStyle=d<1.25?'rgba(53,197,130,.42)':d<1.8?
    'rgba(241,194,65,.42)':'rgba(244,79,78,.42)';
   ctx.globalAlpha=1;ctx.fill();
  }
  ctx.globalAlpha=.33;ctx.stroke();""",
  'per-face distortion heatmap display')
 html=once(html,
  """ summary.textContent=m.vertices+' vertices ('+m.duplicatedVertices+' seam duplicates) · '+""",
  """ const metric=m.distortion;
 const label=metric?.current?
  ' UV stretch (lower is better): '+metric.current+'×'+
  (m.projectionMode==='cone-surface'?' vs '+metric.projected+'× flat panels. ':
   ' (flat projection). '):'';
 summary.textContent=(m.projectionMode==='cone-surface'?'Cone-aware surface':'Flat panel surface')+
  ' · '+label+m.vertices+' vertices ('+m.duplicatedVertices+' seam duplicates) · '+""",
  'measured preview feedback')
 html=once(html,
  """ root.querySelector('#se503AtlasExport').addEventListener('click',se503ExportGuide);""",
  """ root.querySelector('#se503AtlasExport').addEventListener('click',se503ExportGuide);
 root.querySelector('#se510StretchHeat').addEventListener('change',()=>{
  if(se503Preview)se503ShowPreview(se503Preview);
 });""",
  'toggle distortion visual')
 html=once(html,
  """ if(!checkPart(result.proposed)){status('Saved-model validation rejected the UV atlas.',true);return;}
 checkpoint();""",
  """ if(!checkPart(result.proposed)){status('Saved-model validation rejected the UV atlas.',true);return;}
 if(result.oldTexture&&!window.confirm(
   'Apply new UV coordinates? Your existing painted texture cannot follow the new unwrap and will be detached. '+ 
   'The source model is preserved by Undo / project revisions. Export the guide before repainting. Continue?'))return;
 checkpoint();""",
  'explicit confirmation before detaching artwork')
 for old,new in (
  ('SWYRL_ENGINE_DEPLOY_MARKER: V11_509_RAIL_REEXPAND',MARKER),
  ('ENGINE · MAKER v11.509','ENGINE · MAKER v11.510'),
  ('v11.509 · restore collapsed tool rail expand control','v11.510 · measured curvature-aware UV islands'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.509'","window.SWRLZ_FORGE_BUILD={version:'v11.510'"),
  ('<title>§wyrl§ Engine · Maker v11.509</title>',
   '<title>§wyrl§ Engine · Maker v11.510</title>'),
 ):html=once(html,old,new,'release identity')
 old=" source.engine='§wyrl§ Engine · Maker v11.509';source.version=11.509;"
 assert html.count(old)==5,('v11.510 project provenance',html.count(old))
 html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.510';source.version=11.510;")
 key='const SE_RELEASE_NOTES='
 pos=html.index(key)+len(key)
 notes,width=json.JSONDecoder().raw_decode(html[pos:])
 notes['history']=[x for x in notes.get('history',[]) if x.get('version')!='v11.509']
 notes['history'].insert(0,{'version':'v11.509','changes':notes.get('changes',[])})
 notes.update(version='v11.510',date='2026-11-18',
  title='Measured cone-aware front/back UV islands and stretch visualization',
  changes=[
   'Auto-detect an upright tapered crown; use developed cone-sector UV coordinates for front/back, retain flat projection for non-tapered meshes.',
   'Provide explicit Cone surface and legacy flat panel projection modes; separate circular brim and underside UV islands.',
   'Measure area-weighted directional stretch on crown triangles and display cone vs flat-panel stretch in the UV atlas preview.',
   'Add optional colored stretch heatmap to identify distorted UV triangles without altering any mesh data.',
   'Preview, adjustment and exported guides remain non-destructive. Confirm before Apply detaches existing texture, preserve project Undo and revisions.',
   'Continue v11.508 degenerate-triangle diagnostics and retain the v11.509 tool rail behavior.'
  ])
 return html[:pos]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\\/')+html[pos+width:]
