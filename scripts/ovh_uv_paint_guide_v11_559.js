/* SE559: separate the actual paint atlas from island-identification badges. */
let se559Legend=null,se559LegendKey='';
function se559RegionInfo(t,r){
 const pos=t.mesh.geometry.getAttribute('position');
 const descriptions=['Torso front','Torso back','Pelvis underside','Head front','Head back','Crown cap','Arm -X end cap','Arm -X shell','Hand -X digit A','Hand -X digit B','Hand -X digit C','Hand -X digit D','Hand -X thumb','Arm +X end cap','Arm +X shell','Hand +X digit A','Hand +X digit B','Hand +X digit C','Hand +X digit D','Hand +X thumb','Leg -X / foot','Leg +X / foot'];
 const counts=[715,715,135,475,475,193,99,777,64,64,64,64,50,99,777,64,64,64,64,50,673,673];
 const named=t.part.id==='clean-topology-humanoid-base'&&r.groups.length===22&&r.groups.every((g,i)=>g.ids.size===counts[i]);
 return r.groups.map((g,i)=>{
  const centerZ=[...g.ids].reduce((s,v)=>s+pos.getZ(v),0)/g.ids.size;
  let name=named?descriptions[i]:r.anatomical?se552Names[g.id]:'Island '+(i+1);
  if(named&&(i===0||i===1))name='Torso '+(centerZ>0?'front (+Z)':'back (-Z)');
  if(named&&(i===3||i===4))name='Head '+(centerZ>0?'front (+Z)':'back (-Z)');
  return {group:g,id:r.anatomical?g.id+1:i+1,name,color:se552Color(g,i,r.anatomical)};
 });
}
function se559Boundary(ctx,uv,faces,size){
 const edges=new Map(),point=v=>[uv.getX(v),uv.getY(v)],key=p=>p.map(x=>x.toFixed(6)).join(',');
 for(const f of faces)for(let i=0;i<3;i++){
  const a=point(f[i]),b=point(f[(i+1)%3]),ka=key(a),kb=key(b),k=ka<kb?ka+'|'+kb:kb+'|'+ka;
  if(edges.has(k))edges.get(k).n++;else edges.set(k,{a,b,n:1});
 }
 ctx.beginPath();
 for(const {a,b,n} of edges.values())if(n===1){ctx.moveTo(a[0]*size,(1-a[1])*size);ctx.lineTo(b[0]*size,(1-b[1])*size);}
 ctx.stroke();
}
function se559UpdateLegend(t,rows){
 if(!se559Legend?.isConnected)return;
 const key=t.part.id+'|'+rows.map(x=>[x.id,x.name,x.color].join(':')).join('|');
 if(key===se559LegendKey)return;
 se559LegendKey=key;
 const list=se559Legend.querySelector('[data-se559-list]');list.replaceChildren();
 for(const row of rows){
  const b=document.createElement('button');b.type='button';b.dataset.se559Island=String(row.id);
  const sw=document.createElement('span');sw.style.cssText='width:12px;height:12px;flex:none;border-radius:3px;background:'+row.color;
  const txt=document.createElement('span');txt.textContent=row.id+' · '+row.name;b.append(sw,txt);
  b.onclick=()=>{
   const target=se551Target();if(!target)return;
   const item=se559RegionInfo(target,se552Regions(target)).find(x=>x.id===row.id);
   if(!item)return;
   se551Selection={part:target.part,ids:[...item.group.ids]};se356UVPreviewSchedule();
   se559Legend.open=false;status('Selected UV island '+row.id+' · '+item.name);
  };list.append(b);
 }
 se559Legend.querySelector('summary').textContent='Island legend · '+rows.length;
}
se552DrawRegions=function(t,cv,exporting=false){
 const r=se552Regions(t),rows=se559RegionInfo(t,r),ctx=cv.getContext('2d'),size=cv.width;
 const selected=new Set(se551Selection?.part===t.part?se551Selection.ids:[]);
 ctx.save();
 for(const {group:g,color} of rows){
  ctx.fillStyle=color;ctx.globalAlpha=exporting?.45:selected.size&&[...g.ids].every(v=>selected.has(v))?.7:.32;
  for(const f of g.faces){ctx.beginPath();f.forEach((v,k)=>{const x=r.topo.uv.getX(v)*size,y=(1-r.topo.uv.getY(v))*size;k?ctx.lineTo(x,y):ctx.moveTo(x,y);});ctx.closePath();ctx.fill();}
  ctx.globalAlpha=.9;ctx.strokeStyle=color;ctx.lineWidth=Math.max(1,size/900);se559Boundary(ctx,r.topo.uv,g.faces,size);
 }
 ctx.restore();if(!exporting)se559UpdateLegend(t,rows);return r.groups;
};
function se559ExportPaintGuide(){
 const t=se551Target();if(!t){status('Select a mesh to export its clean paint guide.');return;}
 const r=se552Regions(t),size=4096,cv=document.createElement('canvas');cv.width=cv.height=size;
 const ctx=cv.getContext('2d');ctx.strokeStyle='#181e29';ctx.lineWidth=3;ctx.lineJoin='round';
 for(const g of r.groups)se559Boundary(ctx,r.topo.uv,g.faces,size);
 cv.toBlob(blob=>{
  if(!blob){status('Unable to export paint guide.');return;}
  const a=document.createElement('a'),url=URL.createObjectURL(blob);a.href=url;a.download='se-ai-paint-guide-4096.png';document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);
  status('4096² exact boundary guide exported · transparent, no labels, no triangulation. Keep all UV positions fixed.');
 },'image/png');
}
const se559OpenBase=se552Open;
se552Open=function(){
 se559OpenBase();
 const host=se552Portal?.host,controls=host?.children?.[1];if(!controls||controls.querySelector('[data-se559-legend]'))return;
 const regions=controls.querySelector('[data-se552-regions]');
 if(regions?.parentNode?.lastChild?.nodeType===3)regions.parentNode.lastChild.textContent=' UV island colors';
 const details=document.createElement('details');details.dataset.se559Legend='1';details.style.cssText='position:static;flex:none';
 details.innerHTML='<summary style="cursor:pointer;padding:7px 9px;border:1px solid #658797;border-radius:6px">Island legend</summary><div data-se559-list style="position:fixed;z-index:2147483647;top:90px;right:12px;background:#102334;border:1px solid #658797;border-radius:8px;min-width:190px;max-width:80vw;max-height:45dvh;overflow:auto;padding:6px;display:flex;flex-direction:column;gap:3px"></div>';
 controls.append(details);se559Legend=details;se559LegendKey='';
 const style=document.createElement('style');style.textContent='[data-se559-list] button{display:flex;gap:7px;align-items:center;text-align:left;white-space:normal!important;padding:6px;background:#20394c;color:white;border:0;border-radius:4px}';
 details.append(style);
 function button(name,fn){const b=document.createElement('button');b.type='button';b.textContent=name;b.style.cssText='padding:8px;background:#254658;color:white;border:1px solid #537e91;border-radius:6px';controls.append(b);b.onclick=fn;}
 button('Export clean 4K paint guide',se559ExportPaintGuide);controls.lastChild.dataset.se559Export='1';
 button('AI anatomical layout',()=>void se557Optimize(false,'anatomical'));controls.lastChild.dataset.se559Layout='1';
 const t=se551Target();if(t)se559UpdateLegend(t,se559RegionInfo(t,se552Regions(t)));se356UVPreviewSchedule();
};
/* SE559_PAINT_GUIDE_END */

/* SE560: persistent editor feedback and non-native confirmation. */
function se560Feedback(message){
 const box=se552Portal?.host?.querySelector('[data-se560-status]');
 if(box)box.textContent=message;
}
function se560BusyControls(busy){
 for(const b of se552Portal?.host?.querySelectorAll('[data-se559-layout],[data-se557-optimize],[data-se557-optimize-all],[data-se559-export]')||[])b.disabled=busy;
}
function se560Confirm(message){
 const host=se552Portal?.host,box=host?.querySelector('[data-se560-confirm]');
 if(!host||!box)return Promise.resolve(false);
 return new Promise(resolve=>{
  let done=false;
  const observer=new MutationObserver(()=>{if(!host.isConnected)finish(false);});
  const finish=value=>{
   if(done)return;done=true;observer.disconnect();box.hidden=true;
   box.querySelector('[data-se560-apply]').onclick=null;box.querySelector('[data-se560-cancel]').onclick=null;resolve(value);
  };
  box.querySelector('[data-se560-prompt]').textContent=message;
  box.querySelector('[data-se560-apply]').onclick=()=>finish(true);
  box.querySelector('[data-se560-cancel]').onclick=()=>finish(false);
  box.hidden=false;se560Feedback('Preview ready — choose Apply or Cancel.');
  observer.observe(document.body,{childList:true});
 });
}
const se560PreviousOpen=se552Open;
se552Open=function(){
 se560PreviousOpen();
 const host=se552Portal?.host;
 if(!host||host.querySelector('[data-se560-status]'))return;
 const panel=document.createElement('div');panel.style.cssText='flex:none;background:#172d3b;border:1px solid #4d788c;border-radius:6px;padding:6px 9px;margin-bottom:5px;font-size:12px;line-height:1.35';
 panel.innerHTML='<div data-se560-status role="status" aria-live="polite">AI anatomical layout: tap to prepare upright face, chest and legs. Apply confirms; Undo reverses.</div><div data-se560-confirm hidden><div data-se560-prompt style="white-space:pre-line;padding:7px 0"></div><div style="display:flex;gap:8px;flex-wrap:wrap"><button type="button" data-se560-apply style="padding:9px 15px;background:#2c7961;color:white;border:1px solid #82c5a5;border-radius:6px">Apply layout</button><button type="button" data-se560-cancel style="padding:9px 15px;background:#293947;color:white;border:1px solid #8295a5;border-radius:6px">Cancel</button></div></div>';
 host.insertBefore(panel,host.children[2]);
 host.querySelector('[data-se551="fit"]')?.click();
};
/* SE560_FEEDBACK_END */

/* SE561: visual review refinements, isolated from UV coordinate/history changes. */
let se561Preview='editor',se561FrameReceipt=null;
function se561PreviewDraw(){
 if(se561Preview==='editor'||!se552Portal)return;
 const t=se551Target(),cv=se552Portal.host.querySelector('#se356UVCanvas');
 if(!t||!cv)return;
 const ctx=cv.getContext('2d'),n=cv.width;
 ctx.save();ctx.globalAlpha=1;ctx.clearRect(0,0,n,n);
 if(se561Preview==='guide'){
  ctx.fillStyle='#f8fafc';ctx.fillRect(0,0,n,n);
  const r=se552Regions(t);
  ctx.strokeStyle='#182b3c';ctx.lineWidth=Math.max(1,n/1024);ctx.lineJoin='round';
  for(const g of r.groups)se559Boundary(ctx,r.topo.uv,g.faces,n);
 }else{
  se356UVCheckboard(ctx,n);
  const img=se356UVLoadImage(t.part);
  if(img)se356UVPaintImage(ctx,img,t.part,n);
  else{ctx.fillStyle='#e8edf5';ctx.font='16px system-ui';ctx.fillText('No painted texture imported',16,30);}
 }
 ctx.restore();
}
const se561RenderBase=se356UVRender;
se356UVRender=function(){se561RenderBase();se561PreviewDraw();};
function se561SetPreview(mode){
 if(!['editor','guide','texture'].includes(mode))return;
 se561Preview=mode;
 const host=se552Portal?.host;
 for(const b of host?.querySelectorAll('[data-se561-preview]')||[])b.setAttribute('aria-pressed',String(b.dataset.se561Preview===mode));
 se356UVPreviewSchedule();
}
function se561ProjectedBounds(){
 if(!camera||!renderer||!modelRoot)return null;
 const cv=renderer.domElement.getBoundingClientRect();
 if(!cv.width||!cv.height)return null;
 camera.updateMatrixWorld(true);modelRoot.updateWorldMatrix(true,true);
 let left=Infinity,right=-Infinity,top=Infinity,bottom=-Infinity,n=0;
 const v=new THREE.Vector3();
 for(const mesh of modelRoot.children){
  if(!mesh.isMesh||!mesh.userData.atelierId||mesh.visible===false)continue;
  const p=mesh.geometry?.getAttribute('position');if(!p)continue;
  for(let i=0;i<p.count;i++){
   v.fromBufferAttribute(p,i).applyMatrix4(mesh.matrixWorld).project(camera);
   if(!Number.isFinite(v.x)||!Number.isFinite(v.y))continue;
   const x=cv.left+(v.x+1)*cv.width/2,y=cv.top+(1-v.y)*cv.height/2;
   left=Math.min(left,x);right=Math.max(right,x);top=Math.min(top,y);bottom=Math.max(bottom,y);n++;
  }
 }
 return n?{left,right,top,bottom,cv}:null;
}
function se561SafeRect(cv){
 let top=cv.top+12,bottom=cv.bottom-24;
 for(const el of [$m('ViewportModes'),panel?.querySelector('[data-component-controls]'),panel?.querySelector('.atelier-top-camera')]){
  if(!el||el.hidden)continue;const r=el.getBoundingClientRect();
  if(r.width>cv.width*.35&&r.top<cv.top+cv.height*.55&&r.bottom>top)top=Math.min(cv.bottom-40,r.bottom+12);
 }
 return {left:cv.left+16,right:cv.right-16,top,bottom};
}
function se561FrameReference(){
 if(!camera||!modelRoot||atelierCameraInterior)return false;
 if(!se430ModelCamera.frame('all',true))return false;
 for(let n=0;n<6;n++){
  let b=se561ProjectedBounds();if(!b)return false;
  const safe=se561SafeRect(b.cv),w=safe.right-safe.left,h=safe.bottom-safe.top;
  if(w<64||h<64)return false;
  const ratio=Math.max((b.right-b.left)/(w*.94),(b.bottom-b.top)/(h*.94));
  if(ratio>1.005){orbit.distance*=ratio*1.025;cameraUpdate();b=se561ProjectedBounds();}
  const dx=(safe.left+safe.right-b.left-b.right)/2,dy=(safe.top+safe.bottom-b.top-b.bottom)/2;
  if(Math.abs(dx)>1||Math.abs(dy)>1)atelierCameraPanByPixels(dx,dy);
 }
 const b=se561ProjectedBounds();if(!b)return false;const safe=se561SafeRect(b.cv);
 const clearance=Math.min(b.left-safe.left,safe.right-b.right,b.top-safe.top,safe.bottom-b.bottom);
 se561FrameReceipt={clearancePx:clearance,top:b.top,safeTop:safe.top,width:b.right-b.left,height:b.bottom-b.top};
 return clearance>=-2;
}
function se561DeclutterLabels(){
 if(!camera||!renderer||!se556Labels)return;
 const rect=renderer.domElement.getBoundingClientRect();if(!rect.width||!rect.height)return;
 camera.updateMatrixWorld(true);se556Labels.updateWorldMatrix(true,true);
 const right=new THREE.Vector3(1,0,0).applyQuaternion(camera.quaternion),center=new THREE.Vector3(),scale=new THREE.Vector3(),p=new THREE.Vector3(),q=new THREE.Vector3();
 const items=se556Labels.children.map((sprite,i)=>{
  sprite.getWorldPosition(center);sprite.getWorldScale(scale);
  p.copy(center).project(camera);q.copy(center).addScaledVector(right,scale.x/2).project(camera);
  return {sprite,i,x:(p.x+1)*rect.width/2,y:(1-p.y)*rect.height/2,z:p.z,r:Math.max(7,Math.abs(q.x-p.x)*rect.width/2)};
 }).sort((a,b)=>a.z-b.z||b.r-a.r);
 const placed=[];
 for(const a of items){
  a.sprite.visible=Number.isFinite(a.x)&&Number.isFinite(a.y)&&a.z>=-1&&a.z<=1&&a.x>=0&&a.x<=rect.width&&a.y>=0&&a.y<=rect.height&&!placed.some(b=>Math.hypot(a.x-b.x,a.y-b.y)<a.r+b.r+3);
  if(a.sprite.visible)placed.push(a);
 }
}
const se561RegionsBase=se552ModelRegions;
se552ModelRegions=function(t){se561RegionsBase(t);se561DeclutterLabels();};
const se561CameraBase=cameraUpdate;
cameraUpdate=function(){se561CameraBase.apply(this,arguments);se561DeclutterLabels();};
const se561OpenBase=se552Open;
se552Open=function(){
 se561OpenBase();
 const host=se552Portal?.host,controls=host?.children?.[1];
 if(!host||!controls||controls.querySelector('[data-se561-preview]'))return;
 se561Preview='editor';
 const existing=controls.querySelector('[data-se552-texture]');
 const btn=(text,mode)=>{
  const b=document.createElement('button');b.type='button';b.textContent=text;b.dataset.se561Preview=mode;
  b.style.cssText='padding:8px;background:#254658;color:white;border:1px solid #537e91;border-radius:6px;min-height:34px';
  b.onclick=()=>se561SetPreview(mode);return b;
 };
 if(existing){existing.textContent='Texture only';existing.dataset.se561Preview='texture';existing.addEventListener('click',()=>se561SetPreview('texture'));}
 const group=document.createElement('div');group.style.cssText='display:flex;gap:5px;flex-wrap:wrap';
 group.append(btn('UV editor','editor'),btn('Clean guide','guide'));controls.append(group);
 const view=controls.querySelector('[data-se556-view]');
 if(view)view.addEventListener('click',()=>{se561FrameReference();se561DeclutterLabels();});
 const tool=controls.querySelector('[data-se552-tool]');tool?.addEventListener('change',()=>se561SetPreview('editor'));
 se561SetPreview('editor');
};
window.SWYRL_ENGINE_UV_VISUAL_REVIEW=Object.freeze({inspect:()=>({preview:se561Preview,frame:se561FrameReceipt,visibleLabels:se556Labels?.children.filter(x=>x.visible).length||0,totalLabels:se556Labels?.children.length||0})});
/* SE561_VISUAL_REVIEW_END */

/* SE562: compact mobile controls, preserving every native action. */
const se562OpenBase=se552Open;
se552Open=function(){
 se562OpenBase();
 const host=se552Portal?.host,controls=host?.children?.[1];
 const cv=host?.querySelector('#se356UVCanvas'),bar=host?.querySelector('[data-se551="fit"]')?.parentElement;
 if(!host||!controls||!cv||!bar||controls.dataset.se562Compact)return;
 controls.dataset.se562Compact='1';
 if(!document.getElementById('se562CompactCSS')){
  const style=document.createElement('style');style.id='se562CompactCSS';
  style.textContent=
   '@media(max-width:700px){'+
   '#se552UVHost [data-se562-compact]{display:flex!important;gap:4px!important;flex-wrap:wrap!important;align-items:center!important;max-height:none!important;overflow:visible!important;padding:4px 0!important}'+
   '#se552UVHost [data-se562-compact] button{font-size:11px!important;min-height:30px!important;padding:5px 7px!important;white-space:nowrap!important}'+
   '#se552UVHost [data-se562-compact] label{font-size:11px!important;white-space:nowrap!important;max-width:100%}'+
   '#se552UVHost [data-se562-compact] summary{font-size:11px!important;padding:6px 7px!important}'+
   '#se552UVHost [data-se562-legacy]{display:none!important}'+
   '#se552UVHost [data-se562-bar]{flex-wrap:nowrap!important;overflow-x:auto!important;overflow-y:hidden!important;white-space:nowrap!important;gap:4px!important;padding:4px 0!important;scrollbar-width:thin}'+
   '#se552UVHost [data-se562-bar]>*{flex:none!important;font-size:11px!important}'+
   '#se552UVHost [data-se562-bar] button{min-height:30px!important;padding:5px 7px!important}'+
   '#se552UVHost [data-se551-info]{display:none!important}'+
   '#se552UVHost [data-se560-status]{font-size:11px;line-height:1.25}'+
   '#se552UVHost [data-se562-extra]{position:fixed;left:8px;right:8px;z-index:2147483647;background:#142638;border:1px solid #6c92a8;border-radius:8px;box-shadow:0 8px 28px #0009;padding:8px;display:flex;flex-wrap:wrap;gap:5px;max-height:55dvh;overflow:auto}'+
   '#se552UVHost [data-se562-more]:not([open]) [data-se562-extra]{display:none!important}'+
   '#se552UVHost [data-se562-more] summary{cursor:pointer;border:1px solid #658797;border-radius:6px;background:#243849}'+
   '}'+
   '@media(min-width:701px){#se552UVHost [data-se562-more]{display:contents}#se552UVHost [data-se562-more]>summary{display:none}#se552UVHost [data-se562-extra]{display:contents!important}}';
  document.head.append(style);
 }
 bar.dataset.se562Bar='1';
 const legacy=host.querySelector('#se356EditMode')?.closest('.se356-uv-preview-actions');
 if(legacy&&legacy!==bar){
  legacy.dataset.se562Legacy='1';
 }
 const details=document.createElement('details');details.dataset.se562More='1';details.innerHTML='<summary>More tools</summary><div data-se562-extra></div>';
 const extra=details.lastElementChild;
 const primary=e=>e.matches('[data-se559-layout],[data-se559-export],[data-se559-legend],[data-se556-view],[data-se561-preview]')||e.querySelector('[data-se552-regions],[data-se556-model],[data-se561-preview]');
 const children=[...controls.children];
 for(const e of children)if(!primary(e))extra.append(e);
 // The hidden duplicate native editor row is still the source of its
 // unique commands; expose proxy controls rather than cloning handlers.
 if(legacy)for(const old of legacy.querySelectorAll('button')){
  const b=document.createElement('button');b.type='button';b.textContent=old.textContent;
  b.style.cssText='background:#254658;color:white;border:1px solid #537e91;border-radius:6px';
  b.onclick=()=>old.click();extra.append(b);
 }
 controls.append(details);
 const compactLabel=(selector,text)=>{
  const node=controls.querySelector(selector)?.parentNode;
  if(node?.lastChild?.nodeType===3)node.lastChild.textContent=' '+text;
 };
 compactLabel('[data-se552-regions]','UV colors');compactLabel('[data-se556-model]','3D labels');
 const layout=controls.querySelector('[data-se559-layout]'),exportGuide=controls.querySelector('[data-se559-export]'),view=controls.querySelector('[data-se556-view]');
 if(layout)layout.textContent='AI anatomical layout';
 if(exportGuide)exportGuide.textContent='Export 4K guide';
 if(view)view.textContent='3D model';
 // Refit when the confirmation, status, or QA header changes height.
 let pending=false;
 const fit=()=>{
  if(pending)return;pending=true;
  requestAnimationFrame(()=>{pending=false;if(!host.isConnected)return;
   if(matchMedia('(max-width:700px)').matches)bar.__se558Fit?.();
   const r=details.getBoundingClientRect();extra.style.top=Math.min(innerHeight-80,Math.max(40,r.bottom+5))+'px';
  });
 };
 const ro=new ResizeObserver(fit);
 for(const node of [host.children[0],controls,host.querySelector('[data-se560-status]')?.parentElement,bar])if(node)ro.observe(node);
 const mo=new MutationObserver(()=>{if(!host.isConnected){ro.disconnect();mo.disconnect();}});
 mo.observe(document.body,{childList:true});details.addEventListener('toggle',fit);fit();
};
/* SE562_COMPACT_END */
