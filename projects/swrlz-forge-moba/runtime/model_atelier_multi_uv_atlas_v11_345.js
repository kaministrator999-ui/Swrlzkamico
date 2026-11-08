// §E v11.345 · linked, multi-part UV atlas for the existing native Model Studio.
// Every rectangle is one real mesh UV space, not a guessed camera projection.
// Atlas imports are split into each part's pre-existing uvPaintPNG storage so
// that no model schema or native UV coordinates are silently rewritten.
let se345AtlasSelected=new Set(),se345AtlasPlan=null,se345AtlasGuide=null;
let se345AtlasModel=null,se345AtlasBusy=false,se345AtlasCatalog='';
const SE345_ATLAS_MAX=96;
function se345AtlasParts(){
 const native=model(),byId=new Map((native?.parts||[]).map(part=>[part.id,part]));
 return (modelRoot?.children||[]).filter(mesh=>mesh.isMesh&&byId.has(mesh.userData?.atelierId))
  .map(mesh=>({part:byId.get(mesh.userData.atelierId),mesh}));
}
function se345AtlasFingerprint(target){
 const g=target?.mesh?.geometry,p=g?.getAttribute?.('position'),uv=g?.getAttribute?.('uv'),idx=g?.getIndex?.();
 if(!p||!uv||uv.count!==p.count)return null;
 let h=2166136261;
 const hash=str=>{for(let i=0;i<str.length;i++){h^=str.charCodeAt(i);h=Math.imul(h,16777619);}};
 hash(String(target.part.id)+'|'+p.count+'|'+(idx?.count||0)+'|'+uv.count);
 const sample=(attr,fn,n)=>{
  const step=Math.max(1,Math.floor(attr.count/n));
  for(let i=0;i<attr.count;i+=step)hash(fn(attr,i));
  if(attr.count>1)hash(fn(attr,attr.count-1));
 };
 sample(uv,(a,i)=>a.getX(i).toFixed(6)+','+a.getY(i).toFixed(6),80);
 sample(p,(a,i)=>a.getX(i).toFixed(5)+','+a.getY(i).toFixed(5)+','+a.getZ(i).toFixed(5),50);
 if(idx)sample(idx,(a,i)=>String(a.getX(i)),70);
 return (h>>>0).toString(16).padStart(8,'0');
}
function se345AtlasLayout(count,resolution=2048){
 if(!Number.isInteger(count)||count<1||count>SE345_ATLAS_MAX)throw Error('Choose 1–'+SE345_ATLAS_MAX+' model parts.');
 if(![2048,4096].includes(resolution))throw Error('Choose 2048px or 4096px.');
 const columns=Math.ceil(Math.sqrt(count)),rows=Math.ceil(count/columns);
 const cell=Math.floor(resolution/Math.max(columns,rows));
 const padding=Math.max(8,Math.floor(cell*.035));
 const header=Math.max(26,Math.floor(cell*.085));
 const size=cell-header-padding*2;
 if(size<85)throw Error('Atlas too dense. Choose 4096px or select fewer parts.');
 return {width:resolution,height:resolution,columns,rows,cell,padding,header,size,
  rect:i=>{const c=i%columns,r=Math.floor(i/columns);return [c*cell+padding,r*cell+header+padding,size,size];}};
}
function se345AtlasMetrics(mesh){
 const g=mesh.geometry,uv=g?.getAttribute?.('uv'),pos=g?.getAttribute?.('position'),idx=g?.getIndex?.();
 if(!uv||!pos||uv.count!==pos.count)throw Error('Missing or incomplete mesh UV data.');
 const faces=Math.floor((idx?.count||pos.count)/3);
 if(faces<1||faces>180000)throw Error('UV faces outside the supported 1–180000 range.');
 let loU=Infinity,loV=Infinity,hiU=-Infinity,hiV=-Infinity;
 for(let i=0;i<uv.count;i++){
  const u=uv.getX(i),v=uv.getY(i);
  if(!Number.isFinite(u)||!Number.isFinite(v)||u<-.00001||u>1.00001||v<-.00001||v>1.00001)
   throw Error('Source UVs are not inside 0–1; run native UV repair first.');
  loU=Math.min(loU,u);loV=Math.min(loV,v);hiU=Math.max(hiU,u);hiV=Math.max(hiV,v);
 }
 return {triangles:faces,vertices:pos.count,uvBounds:[loU,loV,hiU,hiV]};
}
function se345AtlasCurrent(){
 const native=model();
 if(native!==se345AtlasModel){
  se345AtlasModel=native;se345AtlasSelected=new Set();se345AtlasPlan=null;se345AtlasGuide=null;se345AtlasCatalog='';
 }
 return native;
}
function se345AtlasLabel(s){
 return String(s||'').replace(/[\r\n\t]/g,' ').slice(0,88);
}
function se345AtlasFilename(){
 return (se345AtlasLabel(model()?.name||currentProject?.name||'model')||'model')
  .replace(/[^a-z0-9_-]+/gi,'-').slice(0,48)+'-multi-part-uv';
}
async function se345AtlasDownload(blob,name){
 const url=URL.createObjectURL(blob),link=document.createElement('a');
 try{
  link.href=url;link.download=name;document.body.append(link);link.click();link.remove();
 }finally{setTimeout(()=>URL.revokeObjectURL(url),3000);}
}
function se345AtlasBlob(canvas){
 return new Promise((resolve,reject)=>{
  canvas.toBlob(blob=>blob?resolve(blob):reject(Error('Browser could not encode the UV atlas PNG.')),'image/png');
 });
}
function se345AtlasSelectedParts(){
 se345AtlasCurrent();
 const ordered=se345AtlasParts().filter(t=>se345AtlasSelected.has(t.part.id));
 if(!ordered.length)throw Error('Select model parts first (Select All includes the whole character).');
 if(ordered.length>SE345_ATLAS_MAX)throw Error('Select at most '+SE345_ATLAS_MAX+' parts per UV sheet.');
 return ordered;
}
async function se345AtlasBuild(){
 if(se345AtlasBusy)return null;
 se345AtlasBusy=true;
 const node=document.getElementById('se345UVAtlas'),statusEl=node?.querySelector('#se345AtlasStatus');
 try{
  const current=se345AtlasCurrent(),targets=se345AtlasSelectedParts();
  const resolution=Number(node?.querySelector('#se345AtlasResolution')?.value)||2048;
  const layout=se345AtlasLayout(targets.length,resolution);
  const canvas=document.createElement('canvas');
  canvas.width=layout.width;canvas.height=layout.height;
  const ctx=canvas.getContext('2d');if(!ctx)throw Error('Unable to create 2D atlas canvas.');
  ctx.clearRect(0,0,layout.width,layout.height);
  const draft=document.createElement('canvas');draft.width=draft.height=1024;
  const entries=[];
  for(let i=0;i<targets.length;i++){
   const target=targets[i],part=target.part;
   if(current!==model()||partById(part.id)!==part)throw Error('Model changed during export. Start again.');
   const info=se345AtlasMetrics(target.mesh),rect=layout.rect(i);
   se336UVLayout(target.mesh,draft); // True authored UV coordinates and indexed triangles
   ctx.drawImage(draft,...rect);
   const col=i%layout.columns,row=Math.floor(i/layout.columns),x=col*layout.cell,y=row*layout.cell;
   ctx.strokeStyle='rgba(50,225,231,.8)';ctx.lineWidth=Math.max(1,layout.cell/200);
   ctx.strokeRect(rect[0]-.5,rect[1]-.5,rect[2]+1,rect[3]+1);
   ctx.fillStyle='#dbfaff';ctx.font='600 '+Math.max(13,Math.floor(layout.header*.42))+'px system-ui,sans-serif';
   const title=String(i+1).padStart(2,'0')+' · '+se345AtlasLabel(part.name);
   ctx.fillText(title,x+layout.padding,y+layout.header*.73,layout.cell-layout.padding*2);
   const footprint=se345AtlasFingerprint(target);
   const p=rect.map(v=>v/layout.width);
   entries.push({index:i+1,id:part.id,name:part.name,group:part.group||'',kind:part.kind||'',
    uvRectPx:rect,uvRect01:p,uvBounds:info.uvBounds,triangles:info.triangles,
    vertices:info.vertices,fingerprint:footprint});
   if(statusEl)statusEl.textContent='Unwrapping actual UVs · '+(i+1)+' / '+targets.length+' parts';
   if(i%2===1)await new Promise(resolve=>requestAnimationFrame(resolve));
  }
  const plan={schema:'swyrl-model-uv-atlas-v1',engineVersion:'v11.345',
   modelName:current?.name||currentProject?.name||'Model Studio',
   generatedAt:new Date().toISOString(),width:layout.width,height:layout.height,
   parts:entries,
   orientation:'Image top-left is UV v=1; bottom edge UV v=0; no UV projections or geometry edits.',
   note:'Each cell maps one original native mesh; islands overlapping INSIDE a mesh remain overlapping. The cells do not auto-unwrap hidden surfaces.'};
  se345AtlasPlan=plan;se345AtlasGuide=canvas;
  se345AtlasPreview();
  const png=await se345AtlasBlob(canvas);
  await se345AtlasDownload(png,se345AtlasFilename()+'-GUIDE.png');
  if(statusEl)statusEl.textContent='Guide exported: '+entries.length+' linked mesh UV cells. Export mapping JSON too; send both for accurate texture painting.';
  status('UV atlas guide exported. Next export mapping JSON; both identify the actual model parts.');
  return plan;
 }catch(error){
  if(statusEl)statusEl.textContent='Atlas export: '+error.message;
  status('Multi-part UV atlas: '+error.message,true);return null;
 }finally{se345AtlasBusy=false;}
}
function se345AtlasPreview(){
 const node=document.getElementById('se345UVAtlas'),canvas=node?.querySelector('#se345AtlasPreview');
 if(!canvas||!se345AtlasGuide||!se345AtlasPlan)return;
 const ctx=canvas.getContext('2d');if(!ctx)return;
 ctx.clearRect(0,0,canvas.width,canvas.height);
 ctx.drawImage(se345AtlasGuide,0,0,canvas.width,canvas.height);
 const entry=se345AtlasPlan.parts.find(p=>p.id===selection);
 if(entry){
  const rect=entry.uvRect01;ctx.strokeStyle='#ffcc5d';ctx.lineWidth=3;
  ctx.strokeRect(rect[0]*canvas.width,rect[1]*canvas.height,rect[2]*canvas.width,rect[3]*canvas.height);
 }
 const active=node.querySelector('#se345AtlasLink');
 if(active)active.textContent=entry?'Selected mesh ↔ region '+entry.index+': '+entry.name+' ('+entry.id+')':
  'Tap an atlas region or Focus in the list to locate its 3D mesh.';
}
function se345AtlasExportJSON(){
 try{
  if(!se345AtlasPlan)throw Error('Export the UV guide first to establish the exact mapping.');
  const blob=new Blob([JSON.stringify(se345AtlasPlan,null,2)+'\n'],{type:'application/json'});
  void se345AtlasDownload(blob,se345AtlasFilename()+'-MAP.json');
  status('UV atlas mapping JSON exported. Send both GUIDE.png and MAP.json for pixel-accurate texture artwork.');
 }catch(error){status('Atlas JSON: '+error.message,true);}
}
function se345AtlasVerify(plan){
 if(!plan||plan.schema!=='swyrl-model-uv-atlas-v1'||!Array.isArray(plan.parts)
  ||!Number.isInteger(plan.width)||plan.width>4096||plan.width<256||plan.height!==plan.width
  ||!plan.parts.length||plan.parts.length>SE345_ATLAS_MAX)
  throw Error('Unrecognized or unsafe UV mapping manifest.');
 const current=se345AtlasParts(),lookup=new Map(current.map(t=>[t.part.id,t])),seen=new Set();
 for(const record of plan.parts){
  if(typeof record.id!=='string'||seen.has(record.id)||!Array.isArray(record.uvRectPx)||record.uvRectPx.length!==4)
   throw Error('Mapping has missing or duplicate part IDs.');
  seen.add(record.id);
  const target=lookup.get(record.id);
  if(!target||se345AtlasFingerprint(target)!==record.fingerprint)
   throw Error('Model geometry/UVs changed or missing: '+se345AtlasLabel(record.name)+'. Export a new guide.');
  const [x,y,w,h]=record.uvRectPx;
  if(![x,y,w,h].every(Number.isFinite)||x<0||y<0||w<8||h<8||x+w>plan.width||y+h>plan.height)
   throw Error('Mapping has invalid atlas coordinates.');
 }
 return lookup;
}
async function se345AtlasReadMap(file){
 if(!file||file.size>500000)throw Error('Mapping JSON must be smaller than 500 KB.');
 const plan=JSON.parse(await file.text());
 se345AtlasVerify(plan);
 se345AtlasPlan=plan;se345AtlasGuide=null;
 se345AtlasSelected=new Set(plan.parts.map(p=>p.id));
 se345AtlasRefresh(true);
 const node=document.getElementById('se345UVAtlas');
 node.querySelector('#se345AtlasStatus').textContent='Loaded '+plan.parts.length+' exact mesh links. Import the matching painted atlas PNG.';
 return plan;
}
async function se345AtlasImportImage(file){
 if(!file)throw Error('Choose a painted atlas PNG.');
 if(file.type!=='image/png'||file.size>18000000)throw Error('Import a PNG under 18 MB.');
 const plan=se345AtlasPlan;
 if(!plan)throw Error('Export guide and mapping JSON first, or load an existing mapping JSON.');
 const lookup=se345AtlasVerify(plan),reference=model(),url=URL.createObjectURL(file);
 const image=new Image();
 try{
  await new Promise((resolve,reject)=>{image.onload=resolve;image.onerror=()=>reject(Error('Unable to decode painted atlas.'));image.src=url;});
  if(image.naturalWidth!==image.naturalHeight||image.naturalWidth<512||image.naturalWidth>4096)
   throw Error('Painted atlas must be a square 512–4096px PNG matching the guide layout.');
  const prepared=[];
  for(const record of plan.parts){
   const target=lookup.get(record.id),[rx,ry,rw,rh]=record.uvRectPx;
   const a=rx/plan.width*image.naturalWidth,b=ry/plan.height*image.naturalHeight;
   const width=rw/plan.width*image.naturalWidth,height=rh/plan.height*image.naturalHeight;
   let png=null,chosen=0;
   for(const tileSize of [512,384,256,192]){
    const cropped=document.createElement('canvas');cropped.width=cropped.height=tileSize;
    const ctx=cropped.getContext('2d');if(!ctx)throw Error('Canvas unavailable.');
    ctx.drawImage(image,a,b,width,height,0,0,tileSize,tileSize);
    const value=cropped.toDataURL('image/png');
    if(value.length<=360000){png=value;chosen=tileSize;break;}
   }
   if(!png)throw Error('Painted tile for '+se345AtlasLabel(record.name)+' is too detailed for native save limits.');
   const candidate={...target.part,uvPaintPNG:png};
   if(!checkPart(candidate))throw Error('Native model rejected atlas texture for '+se345AtlasLabel(record.name));
   prepared.push({part:target.part,png,resolution:chosen});
   if(record.index%3===0)await new Promise(resolve=>requestAnimationFrame(resolve));
  }
  if(reference!==model())throw Error('Model changed while the atlas was being imported.');
  se345AtlasVerify(plan);
  const previous=selection;
  checkpoint();
  for(const item of prepared)item.part.uvPaintPNG=item.png;
  signalEdited();
  if(previous&&partById(previous))select(previous);
  status('Applied painted atlas to '+prepared.length+' real model parts in one Undo step. Save Model to preserve it.');
  const node=document.getElementById('se345UVAtlas');
  if(node)node.querySelector('#se345AtlasStatus').textContent='Mapped '+prepared.length+' original mesh UVs · one Undo checkpoint. Save Model.';
 }finally{URL.revokeObjectURL(url);}
}
function se345AtlasRefresh(force=false){
 const node=document.getElementById('se345UVAtlas');if(!node)return;
 se345AtlasCurrent();
 const parts=se345AtlasParts(),sig=parts.map(t=>t.part.id+'|'+t.part.name+'|'+(t.part.group||'')).join('\n');
 const list=node.querySelector('#se345AtlasList'),groups=node.querySelector('#se345AtlasGroup');
 if(force||sig!==se345AtlasCatalog){
  se345AtlasCatalog=sig;
  for(const id of [...se345AtlasSelected])if(!parts.some(t=>t.part.id===id))se345AtlasSelected.delete(id);
  list.replaceChildren();
  const distinct=[...new Set(parts.map(t=>t.part.group||'Ungrouped'))].sort();
  const previous=groups.value;
  groups.replaceChildren(new Option('All groups',''));
  for(const g of distinct)groups.add(new Option(g,g));
  if([...groups.options].some(o=>o.value===previous))groups.value=previous;
  for(const t of parts){
   const row=document.createElement('div');row.className='se345-uv-row';
   const label=document.createElement('label'),check=document.createElement('input');
   check.type='checkbox';check.dataset.partId=t.part.id;check.checked=se345AtlasSelected.has(t.part.id);
   check.addEventListener('change',()=>{if(check.checked)se345AtlasSelected.add(t.part.id);else se345AtlasSelected.delete(t.part.id);se345AtlasCount();});
   label.append(check,document.createTextNode(se345AtlasLabel(t.part.name)));
   label.title=t.part.id+' · '+se345AtlasLabel(t.part.group||'Ungrouped');
   const valid=!!t.mesh.geometry?.getAttribute?.('uv');
   const badge=document.createElement('small');badge.textContent=valid?'UV':'NO UV';badge.className=valid?'se345-uv-good':'se345-uv-missing';
   const focus=document.createElement('button');focus.type='button';focus.textContent='Focus';focus.title='Select this exact native 3D mesh';
   focus.addEventListener('click',()=>{select(t.part.id);se345AtlasPreview();});
   row.append(label,badge,focus);list.append(row);
  }
 }
 const current=selection;
 for(const row of list.children){
  const id=row.querySelector('input')?.dataset.partId;
  row.classList.toggle('se345-uv-current',id===current);
 }
 se345AtlasCount();
 se345AtlasPreview();
}
function se345AtlasCount(){
 const node=document.getElementById('se345UVAtlas');if(!node)return;
 const text=node.querySelector('#se345AtlasCount');
 const eligible=se345AtlasParts();
 text.textContent=se345AtlasSelected.size+' of '+eligible.length+' mesh parts selected · source UVs unchanged';
}
function se345AtlasInstall(){
 const inspector=document.getElementById('modelAtelierUVLayout');
 if(!inspector||inspector.querySelector('#se345UVAtlas'))return;
 const details=document.createElement('details');details.id='se345UVAtlas';
 details.className='se345-uv-atlas';details.open=false;
 details.innerHTML=
  '<summary>🧩 Whole-model UV atlas · linked parts</summary>'+
  '<p class="se345-uv-help">Select the whole character or just its parts. Each exported cell is one original mesh’s true UV layout. Focus links a cell to its actual 3D mesh.</p>'+
  '<div class="se345-uv-tools"><button type="button" id="se345AtlasAll">Select all</button><button type="button" id="se345AtlasClear">Clear</button>'+
  '<select id="se345AtlasGroup" aria-label="Model group"><option value="">All groups</option></select>'+
  '<button type="button" id="se345AtlasGroupPick">Select group</button></div>'+
  '<div id="se345AtlasCount" class="se345-uv-help"></div>'+
  '<div id="se345AtlasList" class="se345-uv-list" role="group" aria-label="Select multiple source model meshes"></div>'+
  '<div class="se345-uv-tools"><label>Atlas size <select id="se345AtlasResolution"><option value="2048" selected>2048 px</option><option value="4096">4096 px</option></select></label>'+
  '<button type="button" id="se345AtlasGuideExport">Export UV guide PNG</button>'+
  '<button type="button" id="se345AtlasMappingExport">Export part map JSON</button></div>'+
  '<canvas id="se345AtlasPreview" width="512" height="512" aria-label="UV atlas preview: tap a region to select the corresponding model part"></canvas>'+
  '<p id="se345AtlasLink" class="se345-uv-help"></p>'+
  '<div class="se345-uv-tools"><button type="button" id="se345AtlasLoadMap">Load saved map JSON</button>'+
  '<button type="button" id="se345AtlasLoadPaint">Import painted atlas PNG</button></div>'+
  '<input id="se345AtlasMapFile" type="file" accept=".json,application/json" hidden>'+
  '<input id="se345AtlasPaintFile" type="file" accept="image/png" hidden>'+
  '<p id="se345AtlasStatus" role="status" class="se345-uv-help">Export GUIDE.png + MAP.json together; send both to ChatGPT for an accurately aligned painted texture image.</p>'+
  '<p class="se345-uv-help">One region per model part; UV islands that overlap within a part remain as authored. Import saves one cropped texture per part with one Undo step.</p>';
 inspector.append(details);
 const by=id=>details.querySelector('#'+id);
 by('se345AtlasAll').addEventListener('click',()=>{
  se345AtlasSelected=new Set(se345AtlasParts().map(t=>t.part.id));se345AtlasRefresh(true);
 });
 by('se345AtlasClear').addEventListener('click',()=>{se345AtlasSelected.clear();se345AtlasRefresh(true);});
 by('se345AtlasGroupPick').addEventListener('click',()=>{
  const group=by('se345AtlasGroup').value;
  se345AtlasSelected=new Set(se345AtlasParts().filter(t=>!group||(t.part.group||'Ungrouped')===group).map(t=>t.part.id));
  se345AtlasRefresh(true);
 });
 by('se345AtlasGuideExport').addEventListener('click',()=>void se345AtlasBuild());
 by('se345AtlasMappingExport').addEventListener('click',se345AtlasExportJSON);
 by('se345AtlasLoadMap').addEventListener('click',()=>by('se345AtlasMapFile').click());
 by('se345AtlasLoadPaint').addEventListener('click',()=>by('se345AtlasPaintFile').click());
 by('se345AtlasMapFile').addEventListener('change',async event=>{
  try{await se345AtlasReadMap(event.target.files?.[0]);}
  catch(error){status('Atlas mapping: '+error.message,true);}
  finally{event.target.value='';}
 });
 by('se345AtlasPaintFile').addEventListener('change',async event=>{
  if(se345AtlasBusy){status('UV atlas is already exporting or importing.',true);return;}
  se345AtlasBusy=true;
  try{await se345AtlasImportImage(event.target.files?.[0]);}
  catch(error){status('Painted atlas: '+error.message,true);}
  finally{se345AtlasBusy=false;event.target.value='';}
 });
 by('se345AtlasPreview').addEventListener('click',event=>{
  const plan=se345AtlasPlan;
  if(!plan)return;
  const canvas=event.currentTarget,bounds=canvas.getBoundingClientRect();
  const x=(event.clientX-bounds.left)/bounds.width,y=(event.clientY-bounds.top)/bounds.height;
  const entry=plan.parts.find(t=>{
   const r=t.uvRect01||t.uvRectPx.map(v=>v/plan.width);
   return x>=r[0]&&x<=r[0]+r[2]&&y>=r[1]&&y<=r[1]+r[3];
  });
  if(entry&&partById(entry.id)){select(entry.id);se345AtlasPreview();}
 });
 se345AtlasRefresh(true);
}
const se345PrevEnsureUV=ensurePanel;
ensurePanel=function(){
 const result=se345PrevEnsureUV.apply(this,arguments);
 se345AtlasInstall();return result;
};
const se345PrevRefreshUV=refreshInspector;
refreshInspector=function(){
 const result=se345PrevRefreshUV.apply(this,arguments);
 se345AtlasRefresh();return result;
};
window.SWYRL_ENGINE_UV_ATLAS=Object.freeze({
 inspect:()=>({schema:'swyrl-model-uv-atlas-v1',
  model:se345AtlasCurrent()?.name||null,selected:[...se345AtlasSelected],
  mapped:se345AtlasPlan?.parts?.map(p=>({id:p.id,name:p.name,rect:p.uvRectPx}))||[]}),
 selectAll:()=>{se345AtlasSelected=new Set(se345AtlasParts().map(x=>x.part.id));se345AtlasRefresh(true);return se345AtlasSelected.size;}
});