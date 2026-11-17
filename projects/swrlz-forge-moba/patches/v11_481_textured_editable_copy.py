"""§E v11.481 · UV-faithful editable working copy with preserved original."""
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_481_TEXTURED_EDITABLE_COPY'

def once(s,old,new):
 n=s.count(old)
 assert n==1,('v11.481 anchor',old[:160],n)
 return s.replace(old,new,1)

def apply(html):
 assert 'SWYRL_ENGINE_DEPLOY_MARKER: V11_480_EDITABLE_ENTRY' in html
 src=(ROOT/'runtime/model_textured_editable_copy_v11_481.js').read_text('utf8')
 assert '/* SE481_TEXTURED_EDITABLE_COPY_END */' in src
 html=once(html,'/* SE480_EDITABLE_ENTRY_END */',
  '/* SE480_EDITABLE_ENTRY_END */\n'+src)
 # Do not weaken native safeguards globally: allow only the known painted
 # atlas fields on safe, independently validated working-copy topology.
 pat=r"const ordinary=new Set\(\[([^\]]+)\]\);"
 matches=list(re.finditer(pat,html))
 assert len(matches)==1,('Native safe descriptor whitelist',len(matches))
 allowed=matches[0].group(1)
 for field in ('uvPaintPNG','uvPaintOffset','uvPaintRepeat','uvPaintMaxSize',
               'uvPaintSourceW','uvPaintSourceH','uvPaintSourceBytes',
               'se481SourceId','se481WorkHidden'):
  assert "'"+field+"'" not in allowed
 allowed+=","+",".join("'"+x+"'" for x in
   ('uvPaintPNG','uvPaintOffset','uvPaintRepeat','uvPaintMaxSize',
    'uvPaintSourceW','uvPaintSourceH','uvPaintSourceBytes','se481SourceId','se481WorkHidden'))
 html=html[:matches[0].start()]+"const ordinary=new Set(["+allowed+"]);"+html[matches[0].end():]
 # v11.480 existing button is reused: no competing converter or modal.
 html=once(html,
  "  const already=part?.kind==='topologyMesh';",
  "  const already=part?.kind==='topologyMesh'||!!part?.se481WorkId;")
 html=once(html,
  "  const converting=!!native?.convert?.available&&!native?.preview?.active;",
  """  const textured=window.SWYRL_ENGINE_TEXTURED_TOPOLOGY_481?.inspect?.();
  const preparing=!!textured?.available&&!native?.preview?.active;
  const converting=(!!native?.convert?.available||preparing)&&!native?.preview?.active;""")
 html=once(html,
  """  else if(converting)message=
   /bake.*vertex edit/i.test(native.convert.reason||'')?""",
  """  else if(preparing)message=
   'Create an editable working copy with original UVs, textures and material. Keep the source model recoverable without reprojecting the artwork.';
  else if(converting)message=
   /bake.*vertex edit/i.test(native.convert.reason||'')?""")
 html=once(html,
  """  else message=native?.convert?.reason||
    'The selected model cannot be converted by the current native topology tool.';""",
  """  else message=(textured?.hasPaint&&textured.reason)||native?.convert?.reason||
    'The selected model cannot be converted by the current native topology tool.';""")
 html=once(html,
  "  write(button,/bake.*vertex edit/i.test(native?.convert?.reason||'')?'Bake edits & make editable':'Make mesh editable');",
  "  write(button,preparing?'Make textured editable copy':/bake.*vertex edit/i.test(native?.convert?.reason||'')?'Bake edits & make editable':'Make mesh editable');")
 html=once(html,
  """ function convert(){
  const api=workshop(),s=api?.inspect?.();""",
  """ function convert(){
  const api=workshop(),s=api?.inspect?.();
  const textured=window.SWYRL_ENGINE_TEXTURED_TOPOLOGY_481?.inspect?.();
  if(textured?.available){
   if(typeof window.confirm!=='function'||!window.confirm(
    'Make an independent editable copy? The original model remains in this project, hidden and recoverable. Exact mesh UVs, painted texture and texture positioning are retained. No UV reprojection.'
   ))return {ok:false,cancelled:true,reason:'Original unchanged.'};
   const result=window.SWYRL_ENGINE_TEXTURED_TOPOLOGY_481.prepare();
   if(result?.ok){card.hidden=true;refresh();}
   else{write(reason,result?.reason||'Could not prepare the UV-preserving copy.');refresh();}
   return result;
  }""")
 # One physical vertex may have several atlas seam corner indices.
 # Ring/Fill selection must move all corresponding UV variants together,
 # otherwise a height adjustment tears the painted surface at the seam.
 html=once(html,
  """  return [...new Set(atelierComponentIds.map(i=>top.vertices[i]).filter(id=>Number.isInteger(id)&&id>=0&&id<p.topologyMesh.positions.length/3))];""",
  """  return [...new Set(atelierComponentIds.flatMap(i=>{
   const representative=top.vertices[i];
   return Number.isInteger(representative)?
    (top.groups.get(top.keys[representative])||[]):[];
  }).filter(id=>Number.isInteger(id)&&id>=0&&id<p.topologyMesh.positions.length/3))];""")
 # Existing native converter remains unchanged and still warns about UV regeneration
 # for untextured primitives. No silent fallback if a painted copy is unsafe.
 css="""/* SE481_TEXTURED_EDITABLE_COPY_STYLES_START */
html #modelAtelierPanel #se477SelectionShapes #se481OriginalSourceToggle{
 flex:0 0 auto!important;min-width:158px!important;
 background:#234e55!important;border:1px solid #8fe4d4!important;
 color:#e9fffa!important;padding:6px 9px!important;
}
html #modelAtelierPanel #se477SelectionShapes #se481OriginalSourceToggle:focus-visible{
 outline:2px solid #e4ffe9!important;outline-offset:1px!important;
}
/* SE481_TEXTURED_EDITABLE_COPY_STYLES_END */"""
 html=html.replace('</head>','<style id="se481TexturedEditableCopyStyles">\n'+css+'\n</style>\n</head>',1)
 for old,new in (
  ('SWYRL_ENGINE_DEPLOY_MARKER: V11_480_EDITABLE_ENTRY',MARKER),
  ('ENGINE · MAKER v11.480','ENGINE · MAKER v11.481'),
  ('v11.480 · accessible editable mesh conversion','v11.481 · texture-preserving editable working copies'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.480'","window.SWRLZ_FORGE_BUILD={version:'v11.481'"),
  ('<title>§wyrl§ Engine · Maker v11.480</title>','<title>§wyrl§ Engine · Maker v11.481</title>')
 ):html=once(html,old,new)
 old=" source.engine='§wyrl§ Engine · Maker v11.480';source.version=11.480;"
 assert html.count(old)==5
 html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.481';source.version=11.481;")
 key='const SE_RELEASE_NOTES=';at=html.index(key)+len(key)
 notes,size=json.JSONDecoder().raw_decode(html[at:])
 notes['history']=[e for e in notes.get('history',[]) if e.get('version')!='v11.480']
 notes['history'].insert(0,{'version':'v11.480','changes':notes.get('changes',[])})
 notes.update(version='v11.481',date='2026-11-16',
  title='Texture-preserving editable topology working copy',
  changes=[
   'A selected UV-painted model can create an independent editable topology copy without reprojecting UV coordinates or discarding the painted PNG, UV Slide offset, repeat/shape correction or material.',
   'Source mesh descriptor remains in the saved project, hidden to prevent overlapping geometry; Source / Editable switch restores either model as needed and Undo returns to the prior state.',
   'Indexed topology is constructed from exact rendered position+UV pairs. Different UV atlas seam coordinates remain distinct rather than averaged or overwritten; original canvas artwork is unchanged.',
   'The existing contextual Make mesh editable control offers a texture-preserving copy when the native primitive converter is blocked by painted model metadata.',
   'Existing native ring/vertex selection, selected point overlays, safe topology operations, undo and editor panels remain the only geometry editing pipeline.',
   'Conversion refuses malformed UVs, unsupported multi-material/rigged/vertex-painted sources, or source geometry exceeding the interactive native vertex/face limits. It never silently reduces textures or reshapes the UFO.',
   'Browser verification uses an actual painted, UV-slid model and compares UV triangle coordinates, texture data, source recoverability and visible selected vertex points.'
  ])
 return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[at+size:]
