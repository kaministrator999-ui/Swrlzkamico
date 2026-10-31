// §E v11.184 — project preview cards inside native My Projects.
// Local thumbnails are derived from real saved scene actor positions; a
// cloud project gets a fast illustrative card and can fetch an actual
// scene overview on demand, without importing or replacing the editor.
const SE184_SVG='http://www.w3.org/2000/svg';
const se184CloudPreviews=new Map();
const se184LocalPreviews=new Map();
const se184LocalPreviewQueue=[];
let se184LocalPreviewActive=0,se184LocalPreviewObserver=null;
function se184QueueLocalPreview(card){
 if(!card?.isConnected||card.dataset.se184AutoState)return;
 card.dataset.se184AutoState='queued';
 se184LocalPreviewQueue.push(card);se184RunLocalPreviews();
}
function se184RunLocalPreviews(){
 while(se184LocalPreviewActive<2&&se184LocalPreviewQueue.length){
  const card=se184LocalPreviewQueue.shift();
  if(!card?.isConnected)continue;
  se184LocalPreviewActive++;
  (async()=>{
   try{
    const id=card.dataset.projectId;
    let preview=se184LocalPreviews.get(id);
    if(!preview){
     const row=await se175Read(id);
     preview=se184ExtractPreview(row?.data);
     if(preview){
      if(se184LocalPreviews.size>=48)se184LocalPreviews.delete(se184LocalPreviews.keys().next().value);
      se184LocalPreviews.set(id,preview);
     }
    }
    if(preview&&card.isConnected&&typeof card.se184ApplyPreview==='function')
     card.se184ApplyPreview(preview);
   }catch{/* Older project still has an accessible manual Preview scene action. */}
   finally{se184LocalPreviewActive--;se184RunLocalPreviews();}
  })();
 }
}
function se184WatchLocalPreviews(gallery){
 const cards=[...gallery.querySelectorAll('.se184-project-card[data-se184-needs-preview]')];
 if(!cards.length)return;
 if(typeof IntersectionObserver==='undefined'){
  cards.slice(0,8).forEach(se184QueueLocalPreview);return;
 }
 if(!se184LocalPreviewObserver){
  se184LocalPreviewObserver=new IntersectionObserver(entries=>{
   for(const entry of entries)if(entry.isIntersecting){
    se184LocalPreviewObserver.unobserve(entry.target);
    se184QueueLocalPreview(entry.target);
   }
  },{root:null,rootMargin:'120px 0px',threshold:0.01});
 }
 cards.forEach(card=>se184LocalPreviewObserver.observe(card));
}

let se184LastAccountState=null,se184PreviewEpoch=0;
function se184ExtractPreview(data){
 if(!data?.project||!Array.isArray(data.scene?.actors))return null;
 const meta=data.project,actors=data.scene.actors;
 const points=[];
 const stride=Math.max(1,Math.ceil(actors.length/72));
 for(let i=0;i<actors.length&&points.length<72;i+=stride){
  const a=actors[i],v=a?.position;
  if(!Array.isArray(v)||v.length<3||!Number.isFinite(Number(v[0]))||!Number.isFinite(Number(v[2])))continue;
  const x=Number(v[0]),z=Number(v[2]);
  if(Math.abs(x)>1e6||Math.abs(z)>1e6)continue;
  points.push({x:+x.toFixed(2),z:+z.toFixed(2),
   type:String(a.type||a.actorType||'object').slice(0,36)});
 }
 const parts=Array.isArray(meta?.modelAtelier?.parts)?meta.modelAtelier.parts.length:0;
 const color=/^#[a-f0-9]{6}$/i.test(data.scene.background||'')?data.scene.background:'#102a3f';
 return {schema:'se184-scene-overview-v1',kind:String(meta.kind||'project').slice(0,40),
  template:String(meta.template||'').slice(0,60),count:actors.length,parts,
  background:color,points};
}
function se184SafePreview(input){
 if(!input||input.schema!=='se184-scene-overview-v1'||!Array.isArray(input.points)||input.points.length>72)return null;
 const points=input.points.filter(p=>p&&Number.isFinite(p.x)&&Number.isFinite(p.z)&&
   Math.abs(p.x)<1e6&&Math.abs(p.z)<1e6).slice(0,72).map(p=>({
    x:p.x,z:p.z,type:typeof p.type==='string'?p.type.slice(0,36):'object'}));
 return {...input,points,kind:String(input.kind||'project').slice(0,40),
  count:Math.max(0,Math.min(1e6,Number(input.count)||0)),
  parts:Math.max(0,Math.min(1e6,Number(input.parts)||0))};
}
function se184Svg(type,attrs={},parent){
 const el=document.createElementNS(SE184_SVG,type);
 for(const [k,v] of Object.entries(attrs))el.setAttribute(k,String(v));
 parent?.append(el);return el;
}
function se184PreviewView(preview,record){
 const saved=se184SafePreview(preview);
 const view=document.createElement('div');view.className='se184-preview';
 view.setAttribute('role','img');
 view.setAttribute('aria-label',saved?'Overview of saved scene actors':'Project illustration; scene preview not downloaded');
 const svg=se184Svg('svg',{viewBox:'0 0 320 180',preserveAspectRatio:'xMidYMid slice'});
 const defs=se184Svg('defs',{},svg);
 const grad=se184Svg('linearGradient',{id:'se184-grad-'+(++se184PreviewEpoch),x1:'0',y1:'0',x2:'1',y2:'1'},defs);
 se184Svg('stop',{offset:'0%','stop-color':'#214f60'},grad);
 se184Svg('stop',{offset:'100%','stop-color':saved?.background||'#131f3c'},grad);
 se184Svg('rect',{x:0,y:0,width:320,height:180,fill:'url(#'+grad.id+')'},svg);
 for(let x=0;x<=320;x+=32)se184Svg('path',{d:'M'+x+' 0V180',stroke:'#9bd2cd','stroke-opacity':'.09'},svg);
 for(let y=0;y<=180;y+=30)se184Svg('path',{d:'M0 '+y+'H320',stroke:'#9bd2cd','stroke-opacity':'.09'},svg);
 if(saved?.points.length){
  const xs=saved.points.map(p=>p.x),zs=saved.points.map(p=>p.z);
  const minX=Math.min(...xs),maxX=Math.max(...xs),minZ=Math.min(...zs),maxZ=Math.max(...zs);
  const extent=Math.max(maxX-minX,maxZ-minZ,12),cx=(maxX+minX)/2,cz=(maxZ+minZ)/2;
  const hue=t=>/sheep|wolf|hero|player|avatar|dragon/i.test(t)?'#f7e6b3':
   /tree|bush|grass|foliage/i.test(t)?'#8cdb9e':
   /house|wall|building|tower|rock|structure/i.test(t)?'#add0f3':'#b8b8e5';
  for(const p of saved.points){
   const x=160+(p.x-cx)*138/extent,y=90+(p.z-cz)*70/extent;
   se184Svg('circle',{cx:+x.toFixed(1),cy:+y.toFixed(1),r:4.1,
    fill:hue(p.type),stroke:'#0b2030','stroke-width':1.5},svg);
  }
 }else{
  // An illustrative wireframe communicates the project category accurately,
  // without pretending a scene screenshot has been downloaded.
  se184Svg('path',{d:'M160 27 L247 72 160 126 73 72Z',fill:'#33828a','fill-opacity':'.21',
   stroke:'#95ddce','stroke-width':2},svg);
  se184Svg('path',{d:'M73 72V124L160 170V126M247 72V124L160 170',
   fill:'none',stroke:'#88c2e3','stroke-width':2},svg);
  se184Svg('circle',{cx:160,cy:78,r:29,fill:'#d8c58b','fill-opacity':'.55',
   stroke:'#e6f6ea','stroke-width':1.5},svg);
 }
 view.append(svg);
 const tag=document.createElement('span');tag.className='se184-preview-tag';
 tag.textContent=saved?(saved.parts?'Scene · '+saved.parts+' model parts':saved.count+' scene actors'):
   'Project preview';
 view.append(tag);
 return view;
}
function se184ChooseDefault(source,id,box){
 const api=window.SWYRL_ENGINE_SAVED_DEFAULT;
 if(!api)return;
 const ok=box.checked?api.set(source,id):api.set(null);
 if(!ok)api.sync();
 if(ok){
  const note=source==='cloud'?' (sign-in required at startup)':'';
  if(typeof toast==='function')toast(box.checked?'Default saved project selected'+note+'.':'Default project cleared.');
 }
}
function se184ProjectCard(record,source){
 const id=String(record?.id||'');
 const article=document.createElement('article');
 article.className='se184-project-card';
 article.dataset.source=source;article.dataset.projectId=id;
 if(source==='local'&&!record.preview)article.dataset.se184NeedsPreview='1';
 let preview=se184PreviewView(record.preview,record);article.append(preview);
 article.se184ApplyPreview=summary=>{
  const next=se184PreviewView(summary,record);
  preview.replaceWith(next);preview=next;
  article.querySelector('.se184-card-actions button:nth-child(2)')?.removeAttribute('aria-busy');
 };
 const info=document.createElement('div');info.className='se184-card-info';
 const title=document.createElement('strong');title.textContent=summaryName(record?.name)||'Untitled project';
 title.title=title.textContent;
 const meta=document.createElement('small');
 const itemKind=String(record?.kind||record?.preview?.kind||'').slice(0,50);
 meta.textContent=source==='cloud'
  ?'Saved to account'+(Number.isInteger(record.revision)?' · Revision '+record.revision:'')
  :'On this device'+(itemKind?' · '+itemKind:'');
 info.append(title,meta);article.append(info);
 const actions=document.createElement('div');actions.className='se184-card-actions';
 const open=document.createElement('button');open.type='button';open.textContent='Open project';
 const see=document.createElement('button');see.type='button';
 see.textContent=record.preview?'Refresh preview':'Preview scene';
 const result=document.createElement('p');result.className='se184-preview-status';
 result.setAttribute('role','status');result.setAttribute('aria-live','polite');
 open.onclick=async()=>{
  if(source==='cloud'){
   if(cloudBusy)return;
   open.disabled=true;result.textContent='Opening saved account project…';
   try{
    const ok=await loadCloud(id);
    if(ok){document.getElementById('projectHub')?.classList.remove('show');result.textContent='Project opened.';}
    else result.textContent='Could not open project. Your active scene was preserved.';
   }finally{open.disabled=false}
  }else{
   if(se175LocalLoading||se175Transition||cloudBusy)return;
   const select=document.getElementById('se175LocalProjectList');
   if(!select)return;
   select.value=id;if(select.value!==id){result.textContent='Local project missing. Refresh the library.';return}
   result.textContent='Opening project on this device…';
   await se175LoadLocal();
   result.textContent=document.getElementById('se175LocalStatus')?.textContent||'Local project operation completed.';
  }
 };
 see.onclick=async()=>{
  if(see.disabled)return;
  see.disabled=true;see.textContent='Reading scene…';
  result.textContent=source==='cloud'?'Fetching scene for preview only…':'Reading scene snapshot…';
  try{
   let data;
   if(source==='local'){
    const row=await se175Read(id);data=row?.data;
   }else{
    if(!ready)throw Error('Connect § Chat to preview this project.');
    const reply=await rpc('cloud.load',{projectId:id});
    const bytes=reply?.bytes;
    if(!(bytes instanceof ArrayBuffer)||bytes.byteLength>MAX_RAW)
     throw Error('Preview data unavailable or too large.');
    data=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(bytes));
   }
   const summary=se184ExtractPreview(data);
   if(!summary)throw Error('No valid scene preview in this saved project.');
   if(source==='cloud'){
    if(se184CloudPreviews.size>=24)se184CloudPreviews.delete(se184CloudPreviews.keys().next().value);
    se184CloudPreviews.set(id,summary);
   }
   article.se184ApplyPreview(summary);
   result.textContent='Scene overview ready. The active editor was not changed.';
  }catch(error){
   result.textContent='Could not preview: '+String(error?.message||error).slice(0,140);
  }finally{
   see.disabled=false;see.textContent='Refresh preview';
  }
 };
 actions.append(open,see);article.append(actions);
 const label=document.createElement('label');label.className='se184-default-label';
 const box=document.createElement('input');box.type='checkbox';
 box.dataset.se184Default='saved:'+source+':'+id;
 box.setAttribute('aria-label','Load '+title.textContent+' by default when §E opens');
 box.addEventListener('change',()=>se184ChooseDefault(source,id,box));
 const txt=document.createElement('span');txt.textContent='Load this project by default';
 label.append(box,txt);article.append(label,result);
 return article;
}
function se184SyncDefaultBoxes(){
 window.SWYRL_ENGINE_SAVED_DEFAULT?.sync();
}
function se184InstallLocalGallery(){
 const pane=document.getElementById('se170-pane-mine');
 const section=document.getElementById('se175LocalProjects');
 if(!pane||!section)return null;
 if(document.getElementById('se184LocalCards'))return document.getElementById('se184LocalCards');
 section.classList.add('se184-local-controls');
 const details=document.createElement('details');details.id='se184LocalTools';
 const summary=document.createElement('summary');summary.textContent='List controls';
 details.append(summary);
 const head=section.querySelector('strong');
 for(const child of [...section.children]){
  if(child!==head)details.append(child);
 }
 section.append(details);
 const gallery=document.createElement('div');gallery.id='se184LocalCards';
 gallery.className='se184-project-list';
 gallery.setAttribute('aria-label','On-device project preview cards');
 section.after(gallery);
 return gallery;
}
function se184RenderLocalProjects(records){
 const gallery=se184InstallLocalGallery();if(!gallery)return;
 const rows=(Array.isArray(records)?records:[]).filter(p=>p&&bounded(p.id,160)).slice(0,1000);
 const frag=document.createDocumentFragment();
 for(const row of rows)frag.append(se184ProjectCard({...row,preview:se184SafePreview(row.preview)},'local'));
 gallery.replaceChildren(frag);
 se184WatchLocalPreviews(gallery);
 se184SyncDefaultBoxes();
}
function se184RenderCloudProjects(rows){
 const list=se170Cards;if(!list)return;
 let heading=document.getElementById('se184CloudHeading');
 if(!heading){
  heading=document.createElement('h3');heading.id='se184CloudHeading';
  heading.className='se184-gallery-heading';heading.textContent='Saved to your account';
  list.before(heading);
 }
 const frag=document.createDocumentFragment();
 for(const p of (Array.isArray(rows)?rows:[]).slice(0,1000)){
  if(!bounded(p?.id,160))continue;
  const cached=se184CloudPreviews.get(p.id);
  frag.append(se184ProjectCard({...p,preview:cached||se184SafePreview(p.preview)},'cloud'));
 }
 list.replaceChildren(frag);se184SyncDefaultBoxes();
}
function se184AccountReset(){
 se184CloudPreviews.clear();
}
function se184TryCloudDefault(){
 const boot=window.SWYRL_ENGINE_SAVED_DEFAULT;
 if(!boot?.pending()||!se184LastAccountState?.authenticated||!se184LastAccountState?.user||!ready)return;
 void boot.openCloud(id=>loadCloud(id));
}

function se184KickCloudStartup(){
 // An account default must initialize the normal authenticated Chat iframe,
 // even if the user has not opened the Chat panel yet. No credentials or
 // account data are copied into the editor or persisted by this code.
 const boot=window.SWYRL_ENGINE_SAVED_DEFAULT?.pending();
 if(boot?.source!=='cloud')return;
 if(frame&&!frame.src)frame.src=CHAT_ORIGIN+'/?forgeEmbed=1';
 se184TryCloudDefault();
}
