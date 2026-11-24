/* v11.552: independent mobile UV alignment workspace and readable island overlays. */
let se552Portal=null,se552ShowWires=false,se552ShowRegions=false,se552Pan=false,se552Touch=new Map();
function se552Edges(t,ids){
 const topo=se551Topology(t),chosen=new Set(ids),counts=new Map();
 for(const face of topo.faces){
  if(!face.every(i=>chosen.has(i)))continue;
  for(let k=0;k<3;k++){
   const a=face[k],b=face[(k+1)%3],uv=topo.uv;
   const pa=[uv.getX(a),uv.getY(a)],pb=[uv.getX(b),uv.getY(b)];
   const ka=pa.map(x=>x.toFixed(5)).join(','),kb=pb.map(x=>x.toFixed(5)).join(',');
   const key=ka<kb?ka+'|'+kb:kb+'|'+ka;
   const old=counts.get(key);counts.set(key,{n:(old?.n||0)+1,a:pa,b:pb});
  }
 }
 return [...counts.values()].filter(x=>x.n===1);
}
function se552Paint(){
 if(!se552Portal)return;
 const root=se356UVPreviewRoot(),cv=root?.querySelector('#se356UVCanvas');
 const t=se551Target();if(!cv||!t)return;
 const ctx=cv.getContext('2d'),size=cv.width;
 // Texture first: no dense cyan triangulation obscuring artwork.
 if(se356UVMode==='paint'){
  ctx.clearRect(0,0,size,size);
  se356UVCheckboard(ctx,size);
  const img=se356UVLoadImage(t.part);
  if(img)se356UVPaintImage(ctx,img,t.part,size);
  else {ctx.fillStyle='#e8edf5';ctx.font='16px system-ui';ctx.fillText('Import a texture to align UVs',16,30);}
  if(se552ShowWires){const guide=document.createElement('canvas');guide.width=guide.height=size;
   se336UVLayout(t.mesh,guide);ctx.globalAlpha=.28;ctx.drawImage(guide,0,0);ctx.globalAlpha=1;}
 }
 const s=se551Selection;
 if(!s||s.part!==t.part)return;
 const edges=se552Edges(t,s.ids);
 ctx.save();ctx.lineWidth=3;ctx.strokeStyle='#080e20';ctx.setLineDash([]);
 for(const edge of edges){ctx.beginPath();ctx.moveTo(edge.a[0]*size,(1-edge.a[1])*size);
  ctx.lineTo(edge.b[0]*size,(1-edge.b[1])*size);ctx.stroke();}
 ctx.lineWidth=2;ctx.strokeStyle='#fff36d';
 for(const edge of edges){ctx.beginPath();ctx.moveTo(edge.a[0]*size,(1-edge.a[1])*size);
  ctx.lineTo(edge.b[0]*size,(1-edge.b[1])*size);ctx.stroke();}
 ctx.restore();
}
/* Export the ACTUAL current mesh UVs, not an AI-guessed island arrangement.
   Transparent guide keeps pixel registration when used as a locked paint layer. */
function se552ExportExactGuide(){
 const t=se551Target();
 if(!t){status('Select a textured mesh before exporting its UV guide.');return;}
 const uv=t.mesh.geometry.getAttribute('uv'),ix=t.mesh.geometry.getIndex();
 if(!uv){status('Selected mesh has no UV coordinates.');return;}
 const size=2048,canvas=document.createElement('canvas');
 canvas.width=canvas.height=size;
 const ctx=canvas.getContext('2d');
 if(!ctx){status('UV export canvas unavailable.');return;}
 ctx.clearRect(0,0,size,size);
 ctx.strokeStyle='#161d32';ctx.lineWidth=1.5;ctx.lineJoin='round';
 const count=ix?ix.count:uv.count;
 let drawn=0,invalid=0;
 for(let i=0;i+2<count;i+=3){
  const ids=[0,1,2].map(j=>ix?ix.getX(i+j):i+j);
  const points=ids.map(k=>[uv.getX(k),uv.getY(k)]);
  if(points.some(p=>p.some(v=>!Number.isFinite(v)||v<0||v>1))){invalid++;continue;}
  ctx.beginPath();
  points.forEach(([u,v],j)=>j?ctx.lineTo(u*size,(1-v)*size):ctx.moveTo(u*size,(1-v)*size));
  ctx.closePath();ctx.stroke();drawn++;
 }
 if(!drawn){status('No valid UV triangles to export.');return;}
 if(se552ShowRegions)se552DrawRegions(t,canvas,true);
 canvas.toBlob(blob=>{
  if(!blob){status('Could not encode UV guide.');return;}
  const url=URL.createObjectURL(blob),a=document.createElement('a');
  a.href=url;a.download='se-exact-mesh-uv-guide-2048.png';
  document.body.append(a);a.click();a.remove();
  setTimeout(()=>URL.revokeObjectURL(url),1000);
  status('Exact UV guide exported: '+drawn+' triangles'+(invalid?' · '+invalid+' invalid skipped':'')+'. Keep this layer registered; do not reposition islands in image editors.');
 },'image/png');
}
/* Deterministic color/number overlay of actual connected UV shells. This does not
   re-unwrap geometry: labels are based on UV connectivity, not guessed anatomy. */
const se552Palette=['#ef4444','#3b82f6','#22c55e','#eab308','#a855f7','#f97316'];
const se552Names=['Head','Neck / torso','Left arm','Right arm','Left leg','Right leg'];
let se552RegionMesh=null,se552RegionSource=null;
function se552Regions(t){
 const topo=se551Topology(t),pos=t.mesh.geometry.getAttribute('position'),groups=new Map();
 const anatomical=t.part.id==='humanoid-body-unified';
 topo.faces.forEach((face,i)=>{
  let id=topo.root(i);
  if(anatomical){const x=face.reduce((s,v)=>s+pos.getX(v),0)/3,y=face.reduce((s,v)=>s+pos.getY(v),0)/3;
   id=y>=4.08?0:Math.abs(x)>.69&&y>3.30?(x<0?2:3):y<=2.35?(x<0?4:5):1;}
  if(!groups.has(id))groups.set(id,{id,faces:[],ids:new Set()});
  const g=groups.get(id);g.faces.push(face);face.forEach(v=>g.ids.add(v));
 });
 return {topo,groups:[...groups.values()].sort((a,b)=>a.id-b.id),anatomical};
}
function se552Color(g,i,anatomical){return anatomical?se552Palette[g.id]:se552Palette[i%6];}
function se552DrawRegions(t,cv,exporting=false){
 const {topo,groups,anatomical}=se552Regions(t),ctx=cv.getContext('2d'),size=cv.width;
 const selectedIds=new Set(se551Selection?.part===t.part?se551Selection.ids:[]);
 ctx.save();
 groups.forEach((g,i)=>{
  const color=se552Color(g,i,anatomical),selected=selectedIds.size>0&&[...g.ids].every(v=>selectedIds.has(v));
  ctx.fillStyle=color;ctx.globalAlpha=exporting?.46:selected?.83:.40;
  let x=0,y=0,n=0;
  for(const f of g.faces){ctx.beginPath();f.forEach((v,k)=>{const u=topo.uv.getX(v)*size,w=(1-topo.uv.getY(v))*size;k?ctx.lineTo(u,w):ctx.moveTo(u,w);x+=u;y+=w;n++;});ctx.closePath();ctx.fill();}
  ctx.globalAlpha=1;ctx.font='bold '+Math.max(15,size/42)+'px system-ui';ctx.textAlign='center';ctx.textBaseline='middle';
  const label=String(anatomical?g.id+1:i+1)+(exporting&&anatomical?' '+se552Names[g.id]:'');
  const w=ctx.measureText(label).width+12,h=Math.max(24,size/32);ctx.fillStyle='#07101d';ctx.fillRect(x/n-w/2,y/n-h/2,w,h);ctx.fillStyle='#fff';ctx.fillText(label,x/n,y/n);
 });ctx.restore();
 return groups;
}
function se552ClearRegionMesh(){
 if(se552RegionMesh){se552RegionMesh.removeFromParent();se552RegionMesh.geometry.dispose();se552RegionMesh.material.dispose();}
 se552RegionMesh=null;se552RegionSource=null;
}
function se552ModelRegions(t){
 if(!se552ShowRegions||!t){se552ClearRegionMesh();return;}
 if(se552RegionSource!==t.mesh){se552ClearRegionMesh();
  const {groups,anatomical}=se552Regions(t),pos=t.mesh.geometry.getAttribute('position'),xyz=[],colors=[];
  groups.forEach((g,i)=>{const c=new THREE.Color(se552Color(g,i,anatomical));for(const f of g.faces)for(const v of f){xyz.push(pos.getX(v),pos.getY(v),pos.getZ(v));colors.push(c.r,c.g,c.b);}});
  const geo=new THREE.BufferGeometry();geo.setAttribute('position',new THREE.Float32BufferAttribute(xyz,3));geo.setAttribute('color',new THREE.Float32BufferAttribute(colors,3));
  se552RegionMesh=new THREE.Mesh(geo,new THREE.MeshBasicMaterial({vertexColors:true,side:THREE.DoubleSide,polygonOffset:true,polygonOffsetFactor:-2,polygonOffsetUnits:-2}));
  se552RegionMesh.raycast=()=>{};se552RegionMesh.userData.se552Diagnostic=true;t.mesh.add(se552RegionMesh);se552RegionSource=t.mesh;
 }
}
function se552RegionOverlay(){
 const t=se551Target(),cv=se356UVPreviewRoot()?.querySelector('#se356UVCanvas');if(!t||!cv)return;
 const groups=se552DrawRegions(t,cv);se552ModelRegions(t);
 const el=se552Portal?.host?.querySelector('[data-se552-region-count]');if(el)el.textContent=groups.length+' regions · shared model and export colors';
}
function se552Open(){
 const root=se356UVPreviewRoot();if(!root||se552Portal)return;
 const cv=root.querySelector('#se356UVCanvas'),bar=root.querySelector('[data-se551="expand"]')?.parentElement;
 if(!cv||!bar)return;
 const host=document.createElement('div');host.id='se552UVHost';
 host.style.cssText='position:fixed;inset:0;z-index:2147483646;background:#0b1420;display:flex;flex-direction:column;overflow:hidden;color:#e8f4ff;font:14px system-ui;padding:env(safe-area-inset-top) 8px env(safe-area-inset-bottom);box-sizing:border-box';
 const header=document.createElement('div');header.style.cssText='display:flex;align-items:center;justify-content:space-between;gap:8px;padding:8px 4px';
 header.innerHTML='<strong>UV Texture Alignment</strong><button type="button" data-se552-close style="padding:10px 16px;background:#29495b;color:white;border:1px solid #6a98aa;border-radius:8px">Close ✕</button>';
 const controls=document.createElement('div');controls.style.cssText='display:flex;flex-wrap:wrap;gap:6px;padding:6px 0';
 controls.innerHTML='<label style="display:flex;align-items:center;gap:5px">Tool <select data-se552-tool style="padding:9px;background:#1c3446;color:white;border:1px solid #658797;border-radius:6px"><option value="island">Move island</option><option value="vertex">Vertex</option><option value="edge">Edge</option><option value="off">Inspect</option></select></label>'+
 '<label style="display:flex;align-items:center;gap:5px"><input type="checkbox" data-se552-wires> Wireframe</label>'+
 '<label style="display:flex;align-items:center;gap:5px"><input type="checkbox" data-se552-pan> Pan</label>'+
 '<label style="display:flex;align-items:center;gap:5px"><input type="checkbox" data-se552-regions> Colored numbered UV regions</label>'+
 '<span data-se552-region-count style="font-size:12px;color:#b7d9e9">Enable regions to inspect UV shells</span>'+
 '<button type="button" data-se552-texture style="padding:8px;background:#254658;color:white;border:1px solid #537e91;border-radius:6px">Show texture</button>'+
 '<button type="button" data-se552-export style="padding:8px;background:#254658;color:white;border:1px solid #537e91;border-radius:6px">Export exact UV guide</button>';
 const originalMode=root.querySelector('#se356EditMode');
 const viewport=cv.parentElement;
 const originalParent=root.parentNode,originalNext=root.nextSibling;
 const originalRootStyle=root.getAttribute('style'),oldText=bar.querySelector('[data-se551="expand"]')?.textContent;
 const oldMode=originalMode?.value||'off';
 const holder=document.createElement('div');originalParent.insertBefore(holder,root);
 host.append(header,controls,root);document.body.append(host);
 root.style.cssText='flex:1;min-height:0;overflow:auto;background:#111f2d;border:0;padding:0;margin:0;max-width:none;width:100%;';
 // Hide all content except mode controls, UV canvas, history and transforms.
 for(const child of [...root.children]){
  child.dataset.se552Hidden=child.style.display||'';
  if(!child.contains(cv)&&!child.contains(bar)&&!child.contains(originalMode))child.style.display='none';
 }
 viewport.style.cssText='overflow:auto;max-height:calc(100dvh - 205px);width:100%;touch-action:pan-x pan-y;background:#192a38;border:1px solid #537080;border-radius:8px';
 bar.style.cssText='display:flex;flex-wrap:wrap;gap:5px;align-items:center;position:sticky;top:0;background:#112332;padding:6px 0;z-index:2';
 const expand=bar.querySelector('[data-se551="expand"]');if(expand)expand.style.display='none';
 originalMode.value='island';originalMode.dispatchEvent(new Event('change',{bubbles:true}));
 se356UVMode='paint';
 const buttons=root.querySelectorAll('[data-se356-mode]');
 buttons.forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.se356Mode==='paint')));
 const setZoom=()=>{const fit=Math.max(.65,Math.min(2,(viewport.clientWidth-18)/512));se551Zoom=fit;
  cv.style.width=(512*fit)+'px';cv.style.height=(512*fit)+'px';cv.style.maxWidth='none';
  const z=bar.querySelector('[data-se551-zoom]');if(z)z.textContent=Math.round(fit*100)+'%';};
 setZoom();se356UVPreviewSchedule();
 const close=()=>{
  se552Portal=null;host.remove();
  holder.replaceWith(root);
  if(originalRootStyle===null)root.removeAttribute('style');else root.setAttribute('style',originalRootStyle);
  for(const child of [...root.children])if(child.dataset.se552Hidden!==undefined){child.style.display=child.dataset.se552Hidden;delete child.dataset.se552Hidden;}
  viewport.style.cssText='overflow:auto;max-height:65vh;max-width:100%;touch-action:pan-x pan-y;overscroll-behavior:contain';
  bar.style.cssText='display:flex;flex-wrap:wrap;gap:6px;align-items:center';
  if(expand){expand.style.display='';expand.textContent=oldText||'⛶ Expand';}
  originalMode.value=oldMode;originalMode.dispatchEvent(new Event('change',{bubbles:true}));
  se356UVPreviewSchedule();
 };
 header.querySelector('[data-se552-close]').addEventListener('click',close);
 controls.querySelector('[data-se552-tool]').addEventListener('change',e=>{
  originalMode.value=e.target.value;originalMode.dispatchEvent(new Event('change',{bubbles:true}));
 });
 controls.querySelector('[data-se552-wires]').addEventListener('change',e=>{se552ShowWires=e.target.checked;se356UVPreviewSchedule();});
 controls.querySelector('[data-se552-regions]').checked=se552ShowRegions;
 controls.querySelector('[data-se552-regions]').addEventListener('change',e=>{se552ShowRegions=e.target.checked;se552ModelRegions(se551Target());se356UVPreviewSchedule();});
 controls.querySelector('[data-se552-export]').addEventListener('click',se552ExportExactGuide);
 controls.querySelector('[data-se552-pan]').addEventListener('change',e=>{se552Pan=e.target.checked;cv.style.touchAction=se552Pan?'pan-x pan-y':'none';});
 controls.querySelector('[data-se552-texture]').addEventListener('click',()=>{se356UVMode='paint';se356UVPreviewSchedule();});
 // Pan mode bypasses UV editing and scrolls the enlarged canvas.
 cv.addEventListener('pointerdown',e=>{if(se552Pan){e.stopImmediatePropagation();}},true);
 se552Portal={host,close};se356UVPreviewSchedule();
}
function se552Install(){
 const root=se356UVPreviewRoot(),expand=root?.querySelector('[data-se551="expand"]');
 if(!expand||expand.dataset.se552)return;expand.dataset.se552='1';
 expand.addEventListener('click',e=>{
  e.preventDefault();e.stopImmediatePropagation();
  // v11.551 handler is on the parent bar; capture blocks the old inline expansion.
  se552Open();
 },true);
}
const se552PrevInstall=se356EditInstall;
se356EditInstall=function(){se552PrevInstall();se552Install();};
const se552PrevRender=se356UVRender;
se356UVRender=function(){se552PrevRender();se552Paint();if(se552ShowRegions)se552RegionOverlay();else se552ClearRegionMesh();};

/* SE552_BIDIRECTIONAL_REGIONS_START
 * The six anatomical regions share a single face classification in UV and 3D.
 * A separate non-pickable diagnostic mesh preserves the model's real material.
 */
let se552RegionSelected=-1,se552PickingModel=false,se552PickViewport=null;
let se552FirstRegionOpen=true,se552PickPopup=null,se552PickPopupVisibility='';
function se552RestorePopup(){if(se552PickPopup){se552PickPopup.style.visibility=se552PickPopupVisibility;se552PickPopup=null;}}
function se552LeaveModelPick(){se552PickingModel=false;se552RestorePopup();if(se552Portal)se552Portal.host.style.display='flex';}
function se552PickFaceUV(t,cv,e){
 const rect=cv.getBoundingClientRect();
 const q=[(e.clientX-rect.left)/rect.width,1-(e.clientY-rect.top)/rect.height];
 const {topo,groups}=se552Regions(t);
 const cross=(a,b,c)=>(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]);
 for(const group of groups)for(const f of group.faces){
  const p=f.map(v=>[topo.uv.getX(v),topo.uv.getY(v)]),area=cross(p[0],p[1],p[2]);
  if(Math.abs(area)<1e-12)continue;
  if(cross(p[0],p[1],q)/area>=-1e-5&&cross(p[1],p[2],q)/area>=-1e-5&&cross(p[2],p[0],q)/area>=-1e-5)
   return group.id;
 }
 return null;
}
function se552SyncSelection(t,id){
 const {groups,anatomical}=se552Regions(t),group=groups.find(g=>g.id===id);
 if(!group)return false;
 se552RegionSelected=id;se551Selection={part:t.part,ids:[...group.ids]};
 const label=anatomical?se552Names[id]:'UV shell '+(groups.indexOf(group)+1);
 const info=se356UVPreviewRoot()?.querySelector('[data-se551-info]');
 if(info)info.textContent=label+' · '+group.faces.length+' triangles';
 se552RefreshModelTint(t);se356UVPreviewSchedule();return true;
}
function se552RefreshModelTint(t){
 if(!se552ShowRegions||!t)return;
 // Rebuild only when selection or selected mesh changes, never on every frame.
 if(se552RegionMesh&&se552RegionSource===t.mesh)se552ClearRegionMesh();
 se552ModelRegions(t);
 if(!se552RegionMesh)return;
 const {groups,anatomical}=se552Regions(t),colors=se552RegionMesh.geometry.getAttribute('color');
 let k=0;
 for(const [i,g] of groups.entries()){
  const c=new THREE.Color(se552Color(g,i,anatomical));
  const scale=se552RegionSelected<0||se552RegionSelected===g.id?1:.22;
  for(let n=0;n<g.faces.length*3;n++,k++)colors.setXYZ(k,c.r*scale,c.g*scale,c.b*scale);
 }
 colors.needsUpdate=true;
}
const se552OriginalPick=se551Pick;
se551Pick=function(t,cv,e){
 if(se552ShowRegions&&t?.part?.id==='humanoid-body-unified'){
  const id=se552PickFaceUV(t,cv,e);
  if(id!==null){se552RegionSelected=id;
   const group=se552Regions(t).groups.find(g=>g.id===id);
   se552RefreshModelTint(t);return [...group.ids];}
 }
 return se552OriginalPick(t,cv,e);
};
function se552PickFromModel(e){
 if(!se552PickingModel||!se552Portal||!camera)return;
 const t=se551Target(),view=panel?.querySelector('#modelAtelierViewport'),rect=view?.getBoundingClientRect();
 if(!t||!rect?.width||!rect?.height)return;
 const ray=new THREE.Raycaster();
 ray.setFromCamera(new THREE.Vector2((e.clientX-rect.left)/rect.width*2-1,
   1-(e.clientY-rect.top)/rect.height*2),camera);
 const hit=ray.intersectObject(t.mesh,false)[0];
 e.preventDefault();e.stopImmediatePropagation();
 se552LeaveModelPick();
 if(!hit)return;
 const topo=se551Topology(t),f=topo.faces[hit.faceIndex],pos=t.mesh.geometry.getAttribute('position');
 if(!f)return;
 const x=f.reduce((v,i)=>v+pos.getX(i),0)/3,y=f.reduce((v,i)=>v+pos.getY(i),0)/3;
 const id=t.part.id==='humanoid-body-unified'
  ?(y>=4.08?0:Math.abs(x)>.69&&y>3.30?(x<0?2:3):y<=2.35?(x<0?4:5):1)
  :topo.root(hit.faceIndex);
 se552SyncSelection(t,id);
 if(hit.uv)se356UVResolve(hit.uv.x,hit.uv.y);
}
const se552OriginalInstall=se552Install;
se552Install=function(){
 se552OriginalInstall();
 const view=panel?.querySelector('#modelAtelierViewport');
 if(view&&view!==se552PickViewport){
  if(se552PickViewport)se552PickViewport.removeEventListener('pointerdown',se552PickFromModel,true);
  view.addEventListener('pointerdown',se552PickFromModel,true);se552PickViewport=view;
 }
};
const se552OriginalOpen=se552Open;
se552Open=function(){
 if(se552FirstRegionOpen&&se551Target()?.part?.id==='humanoid-body-unified'){
  se552ShowRegions=true;se552FirstRegionOpen=false;
 }
 se552OriginalOpen();
 const host=se552Portal?.host,controls=host?.children?.[1];
 if(!host||!controls||controls.querySelector('[data-se552-pick3d]'))return;
 const button=document.createElement('button');button.type='button';
 button.dataset.se552Pick3d='1';button.textContent='Pick region on 3D model';
 button.style.cssText='padding:8px;background:#254658;color:white;border:1px solid #537e91;border-radius:6px';
 controls.append(button);
 button.addEventListener('click',()=>{
  if(!se551Target()||!camera||!se552PickViewport){status('Select an editable model first.');return;}
  se552PickingModel=true;
  se552PickPopup=document.getElementById('se355UVPopup');
  if(se552PickPopup){se552PickPopupVisibility=se552PickPopup.style.visibility;se552PickPopup.style.visibility='hidden';}
  host.style.display='none';
  status('Tap the model to select an anatomical region.');
 });
 const close=se552Portal.close;
 se552Portal.close=()=>{se552LeaveModelPick();close();};
 host.addEventListener('pointerdown',e=>{
  const cv=se356UVPreviewRoot()?.querySelector('#se356UVCanvas'),t=se551Target();
  if(e.target!==cv||!t||!se552ShowRegions||se552Pan)return;
  const id=se552PickFaceUV(t,cv,e);
  if(id!==null)se552SyncSelection(t,id);
 },true);
};
/* SE552_BIDIRECTIONAL_REGIONS_END */
