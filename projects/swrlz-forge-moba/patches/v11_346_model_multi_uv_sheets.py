"""§E v11.346 · paginate whole-character native UV atlas exports without shrinking readable islands."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
def one(html,before,after,label):
 count=html.count(before)
 assert count==1,('v11.346 anchor',label,count,before[:95])
 return html.replace(before,after,1)
def apply(html):
 helper=(ROOT/'runtime/model_multi_uv_sheets_v11_346.js').read_text('utf8')
 html=one(html,'const SE345_ATLAS_MAX=96;',
  'const SE345_ATLAS_MAX=96;\n'+helper,'pagination helpers')
 html=one(html,
  "se345AtlasModel=native;se345AtlasSelected=new Set();se345AtlasPlan=null;se345AtlasGuide=null;se345AtlasCatalog='';",
  "se345AtlasModel=native;se345AtlasSelected=new Set();se346AtlasReset();se345AtlasCatalog='';",
  'reset sheet upon model change')
 html=one(html,
  """ if(ordered.length>SE345_ATLAS_MAX)throw Error('Select at most '+SE345_ATLAS_MAX+' parts per UV sheet.');
 return ordered;""",
  """ const info=se346AtlasPageInfo();
 return ordered.slice(info.page*SE345_ATLAS_MAX,(info.page+1)*SE345_ATLAS_MAX);""",
  'selected parts sheet slicing')
 html=one(html,
  "modelName:current?.name||currentProject?.name||'Model Studio',",
  """modelName:current?.name||currentProject?.name||'Model Studio',
   sheetIndex:se346AtlasPage+1,sheetCount:se346AtlasPageInfo().pages,
   selectedPartCount:se346AtlasPageInfo().total,""",
  'include sheet manifest')
 html=one(html,
  "se345AtlasFilename()+'-GUIDE.png'",
  "se345AtlasFilename()+se346AtlasSuffix(plan)+'-GUIDE.png'",
  'unique guide filename')
 html=one(html,
  "se345AtlasFilename()+'-MAP.json'",
  "se345AtlasFilename()+se346AtlasSuffix(se345AtlasPlan)+'-MAP.json'",
  'matching linked manifest filename')
 html=one(html,
  "se345AtlasSelected=new Set(plan.parts.map(p=>p.id));",
  "se345AtlasSelected=new Set(plan.parts.map(p=>p.id));se346AtlasPage=0;",
  'import saved mapping resets sheet')
 html=one(html,
  "else se345AtlasSelected.delete(t.part.id);se345AtlasCount();",
  "else se345AtlasSelected.delete(t.part.id);se346AtlasReset();se345AtlasCount();se345AtlasPreview();",
  'checkbox invalidation')
 html=one(html,
  """  row.classList.toggle('se345-uv-current',id===current);""",
  """  row.classList.toggle('se345-uv-current',id===current);
  const check=row.querySelector('input');if(check)check.checked=se345AtlasSelected.has(id);""",
  'reuse existing selection rows instead of rebuilding hundreds')
 html=one(html,
  "text.textContent=se345AtlasSelected.size+' of '+eligible.length+' mesh parts selected · source UVs unchanged';",
  """const info=se346AtlasPageInfo();
 text.textContent=info.total+' of '+eligible.length+' mesh parts selected · source UVs unchanged';
 const sheet=node.querySelector('#se346AtlasSheetLabel');
 if(sheet)sheet.textContent='Sheet '+(info.page+1)+' / '+info.pages+' · '+info.visible+' meshes on this sheet';
 const back=node.querySelector('#se346AtlasPrev');if(back)back.disabled=info.page===0;
 const next=node.querySelector('#se346AtlasNext');if(next)next.disabled=info.page+1>=info.pages;""",
  'page meter')
 html=one(html,
  """  '<div id="se345AtlasCount" class="se345-uv-help"></div>'+""",
  """  '<div id="se345AtlasCount" class="se345-uv-help"></div>'+
  '<div class="se345-uv-tools"><button type="button" id="se346AtlasPrev">Previous sheet</button><span id="se346AtlasSheetLabel" class="se345-uv-help">Sheet 1 / 1</span><button type="button" id="se346AtlasNext">Next sheet</button></div>'+""",
  'sheet paging integrated inside UV inspector')
 html=one(html,
  "se345AtlasSelected=new Set(se345AtlasParts().map(t=>t.part.id));se345AtlasRefresh(true);",
  "se345AtlasSelected=new Set(se345AtlasParts().map(t=>t.part.id));se346AtlasReset();se345AtlasRefresh();",
  'select whole character without huge DOM rebuild')
 html=one(html,
  "se345AtlasSelected.clear();se345AtlasRefresh(true);",
  "se345AtlasSelected.clear();se346AtlasReset();se345AtlasRefresh();",
  'clear selected parts')
 html=one(html,
  """se345AtlasSelected=new Set(se345AtlasParts().filter(t=>!group||(t.part.group||'Ungrouped')===group).map(t=>t.part.id));
  se345AtlasRefresh(true);""",
  """se345AtlasSelected=new Set(se345AtlasParts().filter(t=>!group||(t.part.group||'Ungrouped')===group).map(t=>t.part.id));
  se346AtlasReset();se345AtlasRefresh();""",
  'group select no DOM rebuild')
 html=one(html,
  "by('se345AtlasGuideExport').addEventListener('click',()=>void se345AtlasBuild());",
  """by('se346AtlasPrev').addEventListener('click',()=>se346AtlasGo(-1));
 by('se346AtlasNext').addEventListener('click',()=>se346AtlasGo(1));
 by('se345AtlasGuideExport').addEventListener('click',()=>void se345AtlasBuild());""",
  'wire page controls')
 html=one(html,
  """<p class="se345-uv-help">One region per model part; UV islands that overlap within a part remain as authored. Import saves one cropped texture per part with one Undo step.</p>""",
  """<p class="se345-uv-help">One region per model part. Whole characters exceeding 96 parts are exported as numbered sheets: export GUIDE.png + MAP.json for each sheet. UV islands overlapping within a part remain as authored. Import saves one cropped texture per part with one Undo step.</p>""",
  'explain multi-sheet limitation clearly')
 html=one(html,
  "model:se345AtlasCurrent()?.name||null,selected:[...se345AtlasSelected],",
  "model:se345AtlasCurrent()?.name||null,selected:[...se345AtlasSelected],sheet:se346AtlasPageInfo(),",
  'inspector pagination')
 html=one(html,
  "selectAll:()=>{se345AtlasSelected=new Set(se345AtlasParts().map(x=>x.part.id));se345AtlasRefresh(true);return se345AtlasSelected.size;}",
  "selectAll:()=>{se345AtlasSelected=new Set(se345AtlasParts().map(x=>x.part.id));se346AtlasReset();se345AtlasRefresh();return se345AtlasSelected.size;},\n sheet:()=>se346AtlasPageInfo(),nextSheet:()=>se346AtlasGo(1),previousSheet:()=>se346AtlasGo(-1)",
  'programmable sheet navigation')
 for old,new in [
  ('SWYRL_ENGINE_DEPLOY_MARKER: V11_345_MODEL_MULTI_UV_VR_DISPLAY','SWYRL_ENGINE_DEPLOY_MARKER: V11_346_MODEL_MULTI_UV_SHEETS'),
  ('ENGINE · MAKER v11.345','ENGINE · MAKER v11.346'),
  ('v11.345 · VR wireframe modes and linked multi-object UV atlas','v11.346 · complete multi-sheet UV export for complex characters'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.345'","window.SWRLZ_FORGE_BUILD={version:'v11.346'"),
  ('<title>§wyrl§ Engine · Maker v11.345</title>','<title>§wyrl§ Engine · Maker v11.346</title>'),
 ]:html=one(html,old,new,'version')
 old=" source.engine='§wyrl§ Engine · Maker v11.345';source.version=11.345;"
 assert html.count(old)==3
 html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.346';source.version=11.346;")
 key='const SE_RELEASE_NOTES=';i=html.index(key)+len(key)
 notes,n=json.JSONDecoder().raw_decode(html[i:])
 if not any(x.get('version')=='v11.345' for x in notes.get('history',[])):
  notes.setdefault('history',[]).insert(0,{'version':'v11.345','changes':notes.get('changes',[])})
 notes.update(version='v11.346',date='2026-11-08',title='Complete large-character UV atlas sheet export',changes=[
  'Select All can include entire complex characters, including hundreds of native mesh parts. UV guide export paginates selections into legible numbered sheets of up to 96 real part UV layouts, retaining original UV coordinates and per-part links.',
  'Previous/Next sheet controls sit inside the existing UV inspector; each sheet exports a correspondingly numbered GUIDE.png and MAP.json. Painted atlas import continues to operate on an individual sheet without rewriting other model parts.',
  'Large group and Select All operations now reuse the existing checkbox UI instead of rebuilding hundreds of model-part rows. VR model display modes remain unchanged.'
 ])
 return html[:i]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[i+n:]
