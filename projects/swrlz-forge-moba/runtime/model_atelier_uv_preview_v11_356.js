// §E v11.356 — true selected-mesh UV preview and bidirectional surface link.
// Injected inside native ModelAtelier closure; never mutates UV vertices/model.
let se356UVMode='surface',se356UVPickMode=false,se356UVMarker=null,se356UVPending=false;
let se356UVImage=null,se356UVImageSource=null,se356UVPin=null,se356UVReport=null;
function se356UVPreviewRoot(){return document.getElementById('se356UVPreview');}
function se356UVPopupVisible(){
 const popup=document.getElementById('se355UVPopup');
 return !!popup&&!popup.hidden&&!panel.hidden;
}
function se356UVPreviewSchedule(){
 if(se356UVPending||!se356UVPopupVisible())return;
 se356UVPending=true;
 requestAnimationFrame(()=>{se356UVPending=false;se356UVRender();});
}
function se356UVMarkerClear(){
 if(se356UVMarker){
  se356UVMarker.removeFromParent();
  se356UVMarker.geometry?.dispose();se356UVMarker.material?.dispose();
  se356UVMarker=null;
 }
}
function se356UVDrawPin(ctx,canvas,u,v){
 const x=u*canvas.width,y=(1-v)*canvas.height;
 ctx.save();ctx.strokeStyle='#080e20';ctx.lineWidth=5;ctx.beginPath();
 ctx.arc(x,y,10,0,Math.PI*2);ctx.stroke();
 ctx.strokeStyle='#fffbd0';ctx.lineWidth=3;ctx.beginPath();
 ctx.arc(x,y,10,0,Math.PI*2);ctx.stroke();
 ctx.beginPath();ctx.moveTo(x-16,y);ctx.lineTo(x+16,y);
 ctx.moveTo(x,y-16);ctx.lineTo(x,y+16);ctx.stroke();ctx.restore();
}
function se356UVCheckboard(ctx,size){
 ctx.fillStyle='#162b38';ctx.fillRect(0,0,size,size);
 ctx.fillStyle='#254454';
 for(let row=0;row<16;row++)for(let col=0;col<16;col++)
  if((row+col)%2===0)ctx.fillRect(col*size/16,row*size/16,size/16,size/16);
}
function se356UVLoadImage(part){
 if(!part?.uvPaintPNG){se356UVImage=null;se356UVImageSource=null;return null;}
 if(se356UVImageSource===part.uvPaintPNG)return se356UVImage;
 se356UVImageSource=part.uvPaintPNG;se356UVImage=null;
 const image=new Image();const source=part.uvPaintPNG;
 image.onload=()=>{if(se356UVImageSource===source){se356UVImage=image;se356UVPreviewSchedule();}};
 image.onerror=()=>{if(se356UVImageSource===source)se356UVImage=null;};
 image.src=source;
 return null;
}
function se356UVPaintImage(ctx,img,part,size){
 const [u,v]=Array.isArray(part.uvPaintOffset)?part.uvPaintOffset:[0,0];
 // Canvas Y runs down; native UV V runs up. Match Three Texture.offset
 // under RepeatWrapping without altering saved image or source vertices.
 const dx=-u*size,dy=v*size;
 const startX=Math.floor((-dx-size)/size),endX=Math.ceil((size-dx)/size);
 const startY=Math.floor((-dy-size)/size),endY=Math.ceil((size-dy)/size);
 for(let y=startY;y<=endY;y++)for(let x=startX;x<=endX;x++)
  ctx.drawImage(img,dx+x*size,dy+y*size,size,size);
}
function se356UVDescribe(u,v,point=null,region=null,overlaps=0){
 const root=se356UVPreviewRoot();if(!root)return;
 const r=se336SelectedMesh();
 const label=region===null?'UV island':SE336_SURFACE_REGIONS[region]?.label||'Surface';
 const extra=overlaps>1?' · '+overlaps+' overlapping UV triangles (not one-to-one)':'';
 root.querySelector('#se356UVPinInfo').textContent=
  'U '+u.toFixed(3)+' · V '+v.toFixed(3)+' → '+label+
  (point?' · highlighted on selected 3D mesh':'')+extra;
}
function se356UVMarkWorld(mesh,world,region){
 se356UVMarkerClear();
 if(!mesh||!modelRoot||!world)return;
 const size=new THREE.Box3().setFromObject(mesh).getSize(new THREE.Vector3()).length();
 const radius=THREE.MathUtils.clamp(size*.018,.006,.075);
 const color=SE336_SURFACE_REGIONS[region]?.color||'#fff2a5';
 const mark=new THREE.Mesh(new THREE.SphereGeometry(radius,12,8),
  new THREE.MeshBasicMaterial({color,depthTest:false,depthWrite:false}));
 mark.userData.atelierHelper=true;mark.renderOrder=10000;
 modelRoot.updateWorldMatrix(true,false);
 mark.position.copy(modelRoot.worldToLocal(world.clone()));
 modelRoot.add(mark);se356UVMarker=mark;
}
function se356UVResolve(u,v){
 const target=se336SelectedMesh();if(!target)return;
 const mesh=target.mesh,g=mesh.geometry,uv=g?.getAttribute('uv'),
  pos=g?.getAttribute('position'),indices=g?.getIndex();
 if(!uv||!pos)return;
 const count=Math.floor((indices?.count||pos.count)/3);
 let first=null,overlaps=0;
 for(let face=0;face<count;face++){
  const ids=[0,1,2].map(i=>indices?indices.getX(face*3+i):face*3+i);
  const ua=uv.getX(ids[0]),va=uv.getY(ids[0]);
  const ub=uv.getX(ids[1]),vb=uv.getY(ids[1]);
  const uc=uv.getX(ids[2]),vc=uv.getY(ids[2]);
  const denominator=(vb-vc)*(ua-uc)+(uc-ub)*(va-vc);
  if(Math.abs(denominator)<1e-12)continue;
  const a=((vb-vc)*(u-uc)+(uc-ub)*(v-vc))/denominator;
  const b=((vc-va)*(u-uc)+(ua-uc)*(v-vc))/denominator,c=1-a-b;
  if(a<-.00001||b<-.00001||c<-.00001)continue;
  overlaps++;if(first)continue;
  const p0=new THREE.Vector3().fromBufferAttribute(pos,ids[0]);
  const p1=new THREE.Vector3().fromBufferAttribute(pos,ids[1]);
  const p2=new THREE.Vector3().fromBufferAttribute(pos,ids[2]);
  const p=p0.multiplyScalar(a).addScaledVector(p1,b).addScaledVector(p2,c);
  const normal=p1.clone().sub(p0).cross(p2.clone().sub(p0)).normalize();
  // Compute face normal from unscaled original triangle to classify world side.
  const v0=new THREE.Vector3().fromBufferAttribute(pos,ids[0]);
  const v1=new THREE.Vector3().fromBufferAttribute(pos,ids[1]);
  const v2=new THREE.Vector3().fromBufferAttribute(pos,ids[2]);
  const n=v1.sub(v0).cross(v2.sub(v0)).normalize()
   .applyMatrix3(new THREE.Matrix3().getNormalMatrix(mesh.matrixWorld)).normalize();
  p.addScaledVector(n,.002);
  first={world:mesh.localToWorld(p),region:se336SurfaceRegion(n.x,n.y,n.z)};
 }
 se356UVPin={id:target.part.id,u,v};
 if(first)se356UVMarkWorld(mesh,first.world,first.region);
 else se356UVMarkerClear();
 se356UVDescribe(u,v,first?.world||null,first?.region??null,overlaps);
 se356UVPreviewSchedule();
}
function se356UVRender(){
 const root=se356UVPreviewRoot();if(!root||!se356UVPopupVisible())return;
 const canvas=root.querySelector('#se356UVCanvas'),ctx=canvas?.getContext('2d');
 if(!ctx)return;
 const target=se336SelectedMesh(),size=canvas.width;
 ctx.clearRect(0,0,size,size);se356UVCheckboard(ctx,size);
 const info=root.querySelector('#se356UVInfo');
 if(!target){
  info.textContent='Select a mesh to preview its real UV layout.';
  se356UVMarkerClear();se356UVPin=null;return;
 }
 const guide=document.createElement('canvas');guide.width=guide.height=size;
 try{
  const metrics=se336UVLayout(target.mesh,guide);
  if(se356UVMode==='surface'){
   const layer=document.createElement('canvas');layer.width=layer.height=size;
   se356UVReport=se336SurfaceAnalysis(target.mesh,layer);
   ctx.drawImage(layer,0,0);
  }else if(se356UVMode==='paint'){
   const img=se356UVLoadImage(target.part);
   if(img)se356UVPaintImage(ctx,img,target.part,size);
   else if(!target.part.uvPaintPNG){ctx.fillStyle='#e6d1aa';ctx.font='15px system-ui';ctx.fillText('No painted PNG on this mesh',14,28);}
  }
  ctx.globalAlpha=se356UVMode==='guide'?1:.8;
  ctx.drawImage(guide,0,0);ctx.globalAlpha=1;
  info.textContent=target.part.name+' · '+metrics.triangles+' actual triangles · 1024px export coordinate guide'+
   (se356UVMode==='paint'?' · current texture offset included':'');
  if(se356UVPin?.id===target.part.id)se356UVDrawPin(ctx,canvas,se356UVPin.u,se356UVPin.v);
  for(const b of root.querySelectorAll('[data-se356-region]')){
   const index=Number(b.dataset.se356Region),item=se356UVReport?.regions[index];
   b.disabled=!item?.anchorUV;
   b.title=item?.anchorUV?'Show '+item.label+' on actual selected mesh':'No mapped faces in region';
  }
 }catch(error){info.textContent='UV preview: '+error.message;}
}
function se356UVPick3D(event){
 if(!se356UVPickMode||!se356UVPopupVisible()||!camera)return;
 const target=se336SelectedMesh();if(!target)return;
 const viewport=panel?.querySelector('#modelAtelierViewport');
 const rect=viewport?.getBoundingClientRect();
 if(!rect?.width||!rect?.height)return;
 const mouse=new THREE.Vector2((event.clientX-rect.left)/rect.width*2-1,
  1-(event.clientY-rect.top)/rect.height*2);
 const ray=new THREE.Raycaster();ray.setFromCamera(mouse,camera);
 const hit=ray.intersectObject(target.mesh,false)[0];
 if(!hit?.uv)return;
 event.preventDefault();event.stopImmediatePropagation();
 se356UVResolve(hit.uv.x,hit.uv.y);
}
function se356UVInstallPreview(){
 const root=document.getElementById('modelAtelierUVLayout');
 if(!root||root.querySelector('#se356UVPreview'))return;
 const wrap=document.createElement('section');
 wrap.id='se356UVPreview';wrap.className='se356-uv-preview';
 wrap.innerHTML=
  '<strong>Actual UV layout preview</strong>'+
  '<p id="se356UVInfo">Choose a mesh to inspect its UVs.</p>'+
  '<div class="se356-uv-preview-modes">'+
   '<button type="button" data-se356-mode="guide" aria-pressed="false">Export wireframe</button>'+
   '<button type="button" data-se356-mode="surface" aria-pressed="true">Surface map</button>'+
   '<button type="button" data-se356-mode="paint" aria-pressed="false">Applied texture</button></div>'+
  '<canvas id="se356UVCanvas" width="512" height="512" aria-label="Actual native UV image layout; tap a triangle to locate it on the model"></canvas>'+
  '<p id="se356UVPinInfo">Tap a UV triangle to locate it on the 3D mesh.</p>'+
  '<div class="se356-uv-directions" aria-label="Mapped surface directions"></div>'+
  '<div class="se356-uv-preview-actions">'+
   '<button type="button" id="se356UVPick3D" aria-pressed="false">Pick on model → UV</button>'+
   '<button type="button" id="se356UVRefresh">Refresh preview</button></div>'+
  '<p class="se356-uv-hint">The preview uses this mesh’s actual UV triangle coordinates, not a camera projection. Colored regions indicate world-facing normals. Overlapping UV islands may cover multiple surfaces; the highlight marks one matching triangle.</p>';
 root.querySelector('h3')?.after(wrap);
 const directions=wrap.querySelector('.se356-uv-directions');
 SE336_SURFACE_REGIONS.forEach((reg,index)=>{
  const b=document.createElement('button');b.type='button';
  b.dataset.se356Region=String(index);b.textContent=reg.label;
  b.style.setProperty('--se356-region',reg.color);directions.append(b);
 });
 wrap.addEventListener('click',event=>{
  const mode=event.target.closest('[data-se356-mode]');
  if(mode){
   se356UVMode=mode.dataset.se356Mode;
   for(const b of wrap.querySelectorAll('[data-se356-mode]'))
    b.setAttribute('aria-pressed',String(b===mode));
   se356UVPreviewSchedule();return;
  }
  const region=event.target.closest('[data-se356-region]');
  if(region&&!region.disabled){
   const item=se356UVReport?.regions[Number(region.dataset.se356Region)];
   if(item?.anchorUV)se356UVResolve(...item.anchorUV);return;
  }
 });
 wrap.querySelector('#se356UVCanvas').addEventListener('click',event=>{
  const rect=event.currentTarget.getBoundingClientRect();
  const u=THREE.MathUtils.clamp((event.clientX-rect.left)/rect.width,0,1);
  const v=1-THREE.MathUtils.clamp((event.clientY-rect.top)/rect.height,0,1);
  se356UVResolve(u,v);
 });
 const pick=wrap.querySelector('#se356UVPick3D');
 pick.addEventListener('click',()=>{
  se356UVPickMode=!se356UVPickMode;
  if(se356UVPickMode&&se336SlideState().enabled)se336SlideToggle();
  pick.setAttribute('aria-pressed',String(se356UVPickMode));
  pick.textContent=se356UVPickMode?'✓ Pick on model ON':'Pick on model → UV';
 });
 wrap.querySelector('#se356UVRefresh').addEventListener('click',se356UVPreviewSchedule);
 const viewport=panel.querySelector('#modelAtelierViewport');
 if(viewport&&!viewport.dataset.se356UVPick){
  viewport.dataset.se356UVPick='true';
  viewport.addEventListener('pointerdown',se356UVPick3D,true);
 }
 se356UVPreviewSchedule();
}
const se356BaseEnsurePanel=ensurePanel;
ensurePanel=function(){
 const result=se356BaseEnsurePanel.apply(this,arguments);
 se356UVInstallPreview();
 return result;
};
const se356BaseRefreshInspector=refreshInspector;
refreshInspector=function(){
 const result=se356BaseRefreshInspector.apply(this,arguments);
 if(se356UVPin?.id!==selection){se356UVPin=null;se356UVMarkerClear();}
 se356UVPreviewSchedule();
 return result;
};
