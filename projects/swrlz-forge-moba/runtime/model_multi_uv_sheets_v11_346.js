/* SE346_MULTI_UV_SHEETS_START */
// Character-wide UV authoring stays pixel-readable by paging large selections.
// Each sheet exports its own paired PNG + exact part-mapping JSON.
let se346AtlasPage=0;
function se346AtlasPageInfo(){
 const count=se345AtlasParts().filter(t=>se345AtlasSelected.has(t.part.id)).length;
 const pages=Math.max(1,Math.ceil(count/SE345_ATLAS_MAX));
 se346AtlasPage=Math.min(Math.max(0,se346AtlasPage),pages-1);
 return {total:count,pages,page:se346AtlasPage,pageSize:SE345_ATLAS_MAX,
  visible:Math.min(SE345_ATLAS_MAX,Math.max(0,count-se346AtlasPage*SE345_ATLAS_MAX))};
}
function se346AtlasReset(resetPage=true){
 if(resetPage)se346AtlasPage=0;
 se345AtlasPlan=null;se345AtlasGuide=null;
}
function se346AtlasGo(delta){
 if(se345AtlasBusy)return false;
 const info=se346AtlasPageInfo(),next=info.page+delta;
 if(!Number.isInteger(next)||next<0||next>=info.pages)return false;
 se346AtlasPage=next;se346AtlasReset(false);
 se345AtlasCount();se345AtlasPreview();
 const el=document.getElementById('se345AtlasStatus');
 if(el)el.textContent='Sheet '+(next+1)+' of '+info.pages+': export GUIDE.png and MAP.json for this set of original model parts.';
 return true;
}
function se346AtlasSuffix(plan){
 const sheet=plan?.sheetIndex||1,pages=plan?.sheetCount||1;
 const size=Math.max(2,String(pages).length);
 return '-SHEET-'+String(sheet).padStart(size,'0')+'-of-'+String(pages).padStart(size,'0');
}
/* SE346_MULTI_UV_SHEETS_END */
