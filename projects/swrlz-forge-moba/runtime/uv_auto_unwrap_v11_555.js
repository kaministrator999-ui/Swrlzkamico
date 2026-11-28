/* §E v11.555: reusable native xatlas UV unwrapping controls.
   Actual mesh topology + texture are changed, never a screenshot or guide.
   The original UV/texture are retained in undo history before any mutation. */
let se555Mode='inspect',se555SeamKeys=new Set(),se555Busy=false,se555Heatmap=null;
let se555Modules=null;
const se555PhysicalKey=(p,i)=>[p[3*i],p[3*i+1],p[3*i+2]].map(x=>Number(x).toFixed(6)).join(',');
const se555EdgeKey=(p,a,b)=>{
 const x=se555PhysicalKey(p,a),y=se555PhysicalKey(p,b);
 return x<y?x+'|'+y:y+'|'+x;
};
function se555FaceGroups(p,ix,seams){
 const neighbors=new Map(),adj=Array.from({length:ix.length/3},()=>new Set());
 for(let t=0;t<ix.length;t+=3){
  for(let k=0;k<3;k++){
   const edge=se555EdgeKey(p,ix[t+k],ix[t+(k+1)%3]);
   if(seams.has(edge))continue;
   if(neighbors.has(edge)){const j=neighbors.get(edge);adj[t/3].add(j);adj[j].add(t/3);}
   else neighbors.set(edge,t/3);
  }
 }
 const materials=new Uint32Array(ix.length/3);
 let groups=0;
 for(let i=0;i<materials.length;i++){
  if(materials[i])continue;
  groups++;
  const stack=[i];materials[i]=groups;
  while(stack.length){
   const x=stack.pop();
   for(const j of adj[x])if(!materials[j]){materials[j]=groups;stack.push(j);}
  }
 }
 return {materials,groups};
}
function se555ModelData(t){
 const m=t?.part?.topologyMesh;
 if(!m||!Array.isArray(m.positions)||!Array.isArray(m.indices)||m.indices.length%3)
  throw Error('Select an editable topology mesh first');
 return m;
}
async function se555Imports(){
 if(!se555Modules){
  const base=new URL('assets/uv-unwrapper/',document.baseURI).href;
  se555Modules=import(base+'uv_atlas_core_v11_555.mjs')
   .then(core=>({core,createXAtlas:null}));
 }
 return se555Modules;
}
function se555Checker(){
 const cv=document.createElement('canvas');cv.width=cv.height=1024;
 const c=cv.getContext('2d');if(!c)throw Error('Checker canvas unavailable');
 for(let y=0;y<32;y++)for(let x=0;x<32;x++){
  c.fillStyle=(x+y)%2?'#bec6d6':'#6b899b';
  c.fillRect(x*32,y*32,32,32);
 }
 return {canvas:cv,data:cv.toDataURL('image/png')};
}
function se555HeatmapClear(){
 if(!se555Heatmap)return;
 se555Heatmap.removeFromParent();
 se555Heatmap.geometry.dispose();se555Heatmap.material.dispose();se555Heatmap=null;
}
function se555DistortionOverlay(t){
 se555HeatmapClear();
 const m=se555ModelData(t),p=m.positions,ix=m.indices,uv=m.uvs;
 const values=[],coords=[];
 for(let k=0;k<ix.length;k+=3){
  const ids=[ix[k],ix[k+1],ix[k+2]];
  const xyz=ids.map(i=>p.slice(i*3,i*3+3));
  const a=xyz[1].map((v,i)=>v-xyz[0][i]),b=xyz[2].map((v,i)=>v-xyz[0][i]);
  const area3=Math.hypot(a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]);
  const u=ids.map(i=>uv.slice(i*2,i*2+2));
  const area2=Math.abs((u[1][0]-u[0][0])*(u[2][1]-u[0][1])-
                       (u[1][1]-u[0][1])*(u[2][0]-u[0][0]));
  values.push(area3>1e-9&&area2>1e-12?Math.sqrt(area2/area3):0);
  xyz.forEach(v=>coords.push(...v));
 }
 const positive=values.filter(x=>x>0).sort((a,b)=>a-b);
 const med=positive[Math.floor(positive.length/2)]||1;
 const colors=[];
 for(const value of values){
  const dev=value<=0?2:Math.abs(Math.log2(value/med));
  const bad=Math.max(0,Math.min(1,dev/2));
  for(let i=0;i<3;i++)colors.push(.12+.88*bad,.78*(1-bad)+.05,.92*(1-bad)+.08);
 }
 const g=new THREE.BufferGeometry();
 g.setAttribute('position',new THREE.Float32BufferAttribute(coords,3));
 g.setAttribute('color',new THREE.Float32BufferAttribute(colors,3));
 const mat=new THREE.MeshBasicMaterial({vertexColors:true,transparent:true,
   opacity:.76,side:THREE.DoubleSide,polygonOffset:true,
   polygonOffsetFactor:-2,polygonOffsetUnits:-2,depthWrite:false});
 se555Heatmap=new THREE.Mesh(g,mat);
 se555Heatmap.raycast=()=>{};
 t.mesh.add(se555Heatmap);
 status('UV density heatmap: teal = near median, red = stretched/compressed. Toggle to remove.');
}
function se555SeamsFromPart(t){
 const saved=t.part.uvMarkedSeams;
 return new Set(Array.isArray(saved)?saved:[]);
}
function se555NearestEdge(t,canvas,e){
 const m=se555ModelData(t),p=m.positions,uv=m.uvs,ix=m.indices;
 const rect=canvas.getBoundingClientRect();
 const x=(e.clientX-rect.left)/rect.width,y=1-(e.clientY-rect.top)/rect.height;
 let key=null,best=Infinity;
 for(let i=0;i<ix.length;i+=3)for(let k=0;k<3;k++){
  const a=ix[i+k],b=ix[i+(k+1)%3],ax=uv[a*2],ay=uv[a*2+1],
        bx=uv[b*2],by=uv[b*2+1],dx=bx-ax,dy=by-ay;
  const d=dx*dx+dy*dy;if(d<1e-12)continue;
  const u=Math.max(0,Math.min(1,((x-ax)*dx+(y-ay)*dy)/d));
  const dist=(x-ax-u*dx)**2+(y-ay-u*dy)**2;
  if(dist<best){best=dist;key=se555EdgeKey(p,a,b);}
 }
 if(best>Math.pow(18/Math.min(rect.width,rect.height),2))return null;
 return key;
}
async function se555AutoUnwrap(){
 if(se555Busy)return false;
 const t=se551Target();
 if(!t){status('Select an editable topology mesh before unwrapping.');return false;}
 const mesh=se555ModelData(t);
 if(!confirm('Rebuild UV coordinates from actual 3D geometry? This replaces the current UV layout and texture with a diagnostic checker. Undo restores them. Save only after reviewing the result.'))return false;
 se555Busy=true;
 try{
  const {core,createXAtlas}=await se555Imports();
  const marked=se555SeamsFromPart(t);
  const seams=se555FaceGroups(mesh.positions,mesh.indices,marked);
  if(marked.size&&seams.groups===1)
   throw Error('Seams do not divide the surface into charts; complete a seam loop or mark a boundary');
  const result=await core.unwrapMesh(createXAtlas,mesh,{
    method:'lscm',
    faceMaterialData:marked.size?seams.materials:null,
    resolution:1024,padding:8,
    maxVertices:t.part.id==='clean-topology-humanoid-base'?9000:120000,
    maxCharts:70
  });
  if(result.indices.length!==mesh.indices.length||result.charts<1)
   throw Error('UV solver returned an incomplete atlas');
  const checker=se555Checker();
  // Transactional apply: no mutation until every solver and texture gate passes.
  checkpoint();se555HeatmapClear();
  const newmesh={...mesh,positions:result.positions,
                 indices:result.indices,uvs:result.uvs};
  const g=new THREE.BufferGeometry();
  g.setAttribute('position',new THREE.Float32BufferAttribute(result.positions,3));
  g.setAttribute('uv',new THREE.Float32BufferAttribute(result.uvs,2));
  g.setIndex(result.indices);g.computeVertexNormals();
  // Smooth normals from physical coordinates, not from UV seam-split
  // indices, so chart boundaries cannot introduce visible shading ridges.
  const normals=g.getAttribute('normal'),sums=new Map();
  for(let i=0;i<result.positions.length;i+=3){
   const key=result.positions.slice(i,i+3).map(v=>v.toFixed(6)).join(',');
   const n=i/3,old=sums.get(key)||[0,0,0,0];
   old[0]+=normals.getX(n);old[1]+=normals.getY(n);
   old[2]+=normals.getZ(n);old[3]++;sums.set(key,old);
  }
  for(let i=0;i<result.positions.length;i+=3){
   const key=result.positions.slice(i,i+3).map(v=>v.toFixed(6)).join(',');
   const n=i/3,v=sums.get(key),d=Math.hypot(v[0],v[1],v[2])||1;
   normals.setXYZ(n,v[0]/d,v[1]/d,v[2]/d);
  }
  normals.needsUpdate=true;
  const previous=t.mesh.geometry;
  t.part.topologyMesh=newmesh;t.part.uvPaintPNG=checker.data;
  t.mesh.geometry=g;previous.dispose();
  const map=new THREE.CanvasTexture(checker.canvas);
  if('colorSpace' in map&&THREE.SRGBColorSpace)map.colorSpace=THREE.SRGBColorSpace;
  for(const material of (Array.isArray(t.mesh.material)?t.mesh.material:[t.mesh.material])){
   if(!material)continue;material.map=map;
   if(material.color?.set)material.color.set('#ffffff');
   material.needsUpdate=true;
  }
  se551Selection=null;se552ClearRegionMesh();
  signalEdited();se356UVPreviewSchedule();
  status(result.method+': '+result.charts+' charts, '+result.positions.length/3+
   ' UV vertices. Density P95/P5 '+result.distortion.p95P05.toFixed(2)+
   '. Diagnostic checker applied; undo restores the previous UV and texture.');
  const count=se552Portal?.host?.querySelector('[data-se555-summary]');
  if(count)count.textContent=result.charts+' charts · density '+result.distortion.p95P05.toFixed(2);
  return true;
 }catch(e){
  console.error('§E xatlas unwrap failed',e);
  status('UV unwrap not applied: '+String(e?.message||e).slice(0,220));
  return false;
 }finally{se555Busy=false;}
}
function se555InstallControls(){
 const host=se552Portal?.host,controls=host?.children?.[1];
 if(!host||!controls||controls.querySelector('[data-se555-auto]'))return;
 const make=(label,id)=>{
  const b=document.createElement('button');
  b.type='button';b.dataset[id]='1';b.textContent=label;
  b.style.cssText='padding:8px;background:#254658;color:white;border:1px solid #537e91;border-radius:6px';
  controls.append(b);return b;
 };
 const unwrap=make('UV unwrap · conformal LSCM','se555Auto');
 const mark=make('Mark UV seam','se555Seam');
 const clear=make('Clear seams','se555Clear');
 const heat=make('UV distortion','se555Distort');
 const summary=document.createElement('span');summary.dataset.se555Summary='1';
 summary.style.cssText='font-size:12px;color:#b7d9e9';
 controls.append(summary);
 unwrap.addEventListener('click',()=>{void se555AutoUnwrap();});
 mark.addEventListener('click',()=>{
  se555Mode=se555Mode==='mark'?'inspect':'mark';
  mark.textContent=se555Mode==='mark'?'Tap UV edges · marking':'Mark UV seam';
  status(se555Mode==='mark'?'Tap UV edges to mark/unmark physical seams. Complete a loop before unwrapping.':'Seam marking finished');
 });
 clear.addEventListener('click',()=>{
  const t=se551Target();if(!t)return;
  checkpoint();t.part.uvMarkedSeams=[];se555SeamKeys.clear();
  signalEdited();status('Removed marked UV seams.');summary.textContent='0 seams';
 });
 heat.addEventListener('click',()=>{
  const t=se551Target();if(!t)return;
  if(se555Heatmap){se555HeatmapClear();status('UV distortion overlay hidden');}
  else se555DistortionOverlay(t);
 });
 const cv=se356UVPreviewRoot()?.querySelector('#se356UVCanvas');
 if(cv&&!cv.dataset.se555SeamListener){
  cv.dataset.se555SeamListener='1';
  cv.addEventListener('pointerdown',e=>{
   if(se555Mode!=='mark'||e.button!==0)return;
   e.preventDefault();e.stopImmediatePropagation();
   const t=se551Target();if(!t)return;
   const key=se555NearestEdge(t,cv,e);
   if(!key){status('Tap closer to an existing UV edge');return;}
   checkpoint();const marked=se555SeamsFromPart(t);
   if(marked.has(key))marked.delete(key);else marked.add(key);
   t.part.uvMarkedSeams=[...marked];
   se555SeamKeys=marked;signalEdited();
   summary.textContent=marked.size+' seam edges';
   status('Marked '+marked.size+' physical seam edges. Close a loop to split a chart.');
  },true);
 }
}
const se555PreviousOpen=se552Open;
se552Open=function(){se555PreviousOpen();se555InstallControls();};
window.SWYRL_ENGINE_UV_UNWRAP=Object.freeze({
 unwrap:se555AutoUnwrap,clearOverlay:se555HeatmapClear,
 status:()=>({ready:!!se552Portal,busy:se555Busy,
   seamMode:se555Mode,markedSeams:se555SeamKeys.size})
});
/* SE555_XATLAS_REAL_UNWRAP_END */

/* SE556: one region identity, one color and number on UV and 3D. */
let se556Labels=null,se556LabelsSource=null,se556ShowModel=true;
// A new single-mesh starter may be opened before its part is selected.
// Use the native selection path, not a synthetic preview-only mesh.
const se556TargetBase=se551Target;
se551Target=function(){
 const current=se556TargetBase();if(current)return current;
 const parts=model()?.parts;
 if(parts?.length===1&&parts[0].id==='clean-topology-humanoid-base'){
  const part=parts[0],mesh=modelRoot?.children.find(x=>x.isMesh&&x.userData.atelierId===part.id);
  if(mesh?.geometry?.getAttribute('uv')?.count*2===part.topologyMesh?.uvs?.length)
   return {part,mesh};
 }
 return null;
};
const se556BaseColor=se552Color;
se552Color=function(g,i,anatomical){
 if(anatomical)return se556BaseColor(g,i,anatomical);
 return '#'+new THREE.Color().setHSL((i*.61803398875+.08)%1,.72,.56).getHexString();
};
function se556Representative(t,topo,g){
 // Select a real face near the UV centroid, not an empty island bounding box.
 const uv=topo.uv;
 let u=0,v=0,n=0;
 for(const f of g.faces)for(const i of f){u+=uv.getX(i);v+=uv.getY(i);n++;}
 u/=n;v/=n;let best=null,score=Infinity;
 for(const f of g.faces){
  const x=f.reduce((a,i)=>a+uv.getX(i),0)/3,y=f.reduce((a,i)=>a+uv.getY(i),0)/3;
  const d=(x-u)**2+(y-v)**2;
  if(d<score){best={f,u:x,v:y};score=d;}
 }
 return best;
}
se552DrawRegions=function(t,cv,exporting=false){
 const {topo,groups,anatomical}=se552Regions(t),ctx=cv.getContext('2d'),size=cv.width;
 const selected=new Set(se551Selection?.part===t.part?se551Selection.ids:[]);
 ctx.save();
 groups.forEach((g,i)=>{
  const color=se552Color(g,i,anatomical);
  ctx.fillStyle=color;ctx.globalAlpha=exporting?.60:selected.size&&[...g.ids].every(v=>selected.has(v))?.85:.55;
  for(const f of g.faces){ctx.beginPath();f.forEach((v,k)=>{const x=topo.uv.getX(v)*size,y=(1-topo.uv.getY(v))*size;k?ctx.lineTo(x,y):ctx.moveTo(x,y);});ctx.closePath();ctx.fill();}
  const p=se556Representative(t,topo,g);if(!p)return;
  const label=String(anatomical?g.id+1:i+1)+(exporting&&anatomical?' '+se552Names[g.id]:'');
  ctx.globalAlpha=1;ctx.font='bold '+Math.max(11,size/55)+'px system-ui';ctx.textAlign='center';ctx.textBaseline='middle';
  const w=ctx.measureText(label).width+8,h=Math.max(17,size/44),x=p.u*size,y=(1-p.v)*size;
  ctx.fillStyle='#07101d';ctx.fillRect(x-w/2,y-h/2,w,h);ctx.fillStyle=color;ctx.fillRect(x-w/2,y-h/2,3,h);ctx.fillStyle='#fff';ctx.fillText(label,x,y);
 });ctx.restore();return groups;
};
function se556ClearLabels(){
 if(se556Labels){se556Labels.removeFromParent();for(const child of se556Labels.children){child.material.map?.dispose();child.material.dispose();}}
 se556Labels=null;se556LabelsSource=null;
}
const se556ClearBase=se552ClearRegionMesh;
se552ClearRegionMesh=function(){se556ClearLabels();se556ClearBase();};
const se556ModelBase=se552ModelRegions;
se552ModelRegions=function(t){
 if(!se556ShowModel||!se552ShowRegions||!t){se552ClearRegionMesh();return;}
 if(se556LabelsSource!==t.mesh.geometry&&se552RegionMesh)se552ClearRegionMesh();
 se556ModelBase(t);
 if(!se552RegionMesh||se556Labels)return;
 const {topo,groups,anatomical}=se552Regions(t);
 const pos=t.mesh.geometry.getAttribute('position');
 const read=i=>new THREE.Vector3(pos.getX(i),pos.getY(i),pos.getZ(i));
 const group=new THREE.Group();group.userData.se552Diagnostic=true;group.raycast=()=>{};
 t.mesh.geometry.computeBoundingBox();const bounds=t.mesh.geometry.boundingBox;
 const size=Math.max(.025,Math.min(.22,bounds.getSize(new THREE.Vector3()).length()*.031));
 groups.forEach((g,i)=>{
  const p=se556Representative(t,topo,g);if(!p)return;
  const [a,b,c]=p.f.map(read);
  const center=a.clone().add(b).add(c).multiplyScalar(1/3);
  const normal=b.clone().sub(a).cross(c.clone().sub(a)).normalize();
  center.addScaledVector(normal,size*.21);
  const cv=document.createElement('canvas');cv.width=cv.height=128;
  const ctx=cv.getContext('2d');ctx.fillStyle='#07101d';ctx.beginPath();ctx.arc(64,64,56,0,Math.PI*2);ctx.fill();
  ctx.strokeStyle=se552Color(g,i,anatomical);ctx.lineWidth=10;ctx.stroke();
  ctx.fillStyle='#fff';ctx.font='bold 64px system-ui';ctx.textAlign='center';ctx.textBaseline='middle';
  ctx.fillText(String(anatomical?g.id+1:i+1),64,66);
  const texture=new THREE.CanvasTexture(cv);if(THREE.SRGBColorSpace)texture.colorSpace=THREE.SRGBColorSpace;
  const sprite=new THREE.Sprite(new THREE.SpriteMaterial({map:texture,depthTest:true,depthWrite:false,transparent:true}));
  sprite.position.copy(center);sprite.scale.set(size,size,1);sprite.renderOrder=25;sprite.raycast=()=>{};sprite.userData.se552Diagnostic=true;
  group.add(sprite);
 });
 t.mesh.add(group);se556Labels=group;se556LabelsSource=t.mesh.geometry;
};
const se556OpenBase=se552Open;
se552Open=function(){
 se556OpenBase();
 const host=se552Portal?.host,controls=host?.children?.[1];
 if(!controls||controls.querySelector('[data-se556-model]'))return;
 const regions=controls.querySelector('[data-se552-regions]');
 const t=se551Target();if(t&&selection!==t.part.id)select(t.part.id);
 regions?.addEventListener('change',()=>{if(regions.checked){se552ShowRegions=true;se552ModelRegions(se551Target());}else{se552ShowRegions=false;se552ClearRegionMesh();}se356UVPreviewSchedule();});
 if(regions?.parentNode?.lastChild?.nodeType===3)regions.parentNode.lastChild.textContent=' UV colors + numbers';
 const label=document.createElement('label');label.style.cssText='display:flex;align-items:center;gap:5px';
 label.innerHTML='<input type="checkbox" data-se556-model> Show colors + numbers on 3D model';
 controls.append(label);const check=label.firstChild;check.checked=se556ShowModel;
 check.addEventListener('change',()=>{
  se556ShowModel=check.checked;
  if(check.checked&&regions&&!regions.checked){regions.checked=true;regions.dispatchEvent(new Event('change'));}
  se552ModelRegions(se551Target());se356UVPreviewSchedule();
 });
 const view=document.createElement('button');view.type='button';view.dataset.se556View='1';view.textContent='View numbered model';
 view.style.cssText='padding:8px;background:#254658;color:white;border:1px solid #537e91;border-radius:6px';
 controls.append(view);
 view.addEventListener('click',()=>{
  se556ShowModel=true;check.checked=true;
  if(regions){regions.checked=true;regions.dispatchEvent(new Event('change'));}
  se552ModelRegions(se551Target());se552Portal?.close();
  document.getElementById('se355UVClose')?.click();
  status('Numbered UV overlay active. Reopen expanded UV Editor to toggle it off.');
 });
};
window.SWYRL_ENGINE_UV_NUMBERING=Object.freeze({
 inspect:()=>({enabled:se552ShowRegions,model:se556ShowModel,labels:se556Labels?.children.length||0,target:se551Target()?.part?.id||null,selected:selection,meshCount:modelRoot?.children?.length||0,attached:!!se556Labels?.parent})
});
// On native starter load, compute the same area-weighted normal on every
// coincident physical vertex, even where the UV chart has split its index.
const se556GeometryBase=atelierTopologyGeometry;
atelierTopologyGeometry=function(part){
 const geo=se556GeometryBase(part);
 if(part?.id!=='clean-topology-humanoid-base')return geo;
 const p=geo.getAttribute('position'),ix=geo.getIndex(),n=geo.getAttribute('normal');
 if(!p||!ix||!n)return geo;
 const keys=Array.from({length:p.count},(_,i)=>[p.getX(i),p.getY(i),p.getZ(i)].map(v=>v.toFixed(6)).join(','));
 const sums=new Map(),a=new THREE.Vector3(),b=new THREE.Vector3(),c=new THREE.Vector3();
 for(let k=0;k<ix.count;k+=3){
  const ids=[ix.getX(k),ix.getX(k+1),ix.getX(k+2)];
  a.fromBufferAttribute(p,ids[0]);b.fromBufferAttribute(p,ids[1]);c.fromBufferAttribute(p,ids[2]);
  b.sub(a);c.sub(a);b.cross(c);
  for(const id of ids){let v=sums.get(keys[id]);if(!v){v=new THREE.Vector3();sums.set(keys[id],v);}v.add(b);}
 }
 for(let i=0;i<p.count;i++){const v=sums.get(keys[i]);if(v&&v.lengthSq()>1e-20){v.normalize();n.setXYZ(i,v.x,v.y,v.z);}}
 n.needsUpdate=true;return geo;
};
/* SE556_NUMBERED_MODEL_UV_END */


/* SE557 selected-mesh UV optimization and conservative painted PNG rebake.
   Existing geometry, skinning, vertex order, materials and seam topology stay intact. */
let se557Busy=false,se557ExpandedBefore=false;
async function se557Rebake(part,mesh,next){
 const source=part.uvPaintPNG;
 if(!source)return null;
 if(typeof source!=='string'||!source.startsWith('data:image/png;base64,'))throw Error('Only embedded painted PNG textures can be safely rebaked');
 const img=new Image();img.src=source;await img.decode();
 const w=img.naturalWidth,h=img.naturalHeight;
 if(w!==h||w<256||w>2048)throw Error('Paint rebake currently supports square 256–2048 px PNG textures');
 const cv=document.createElement('canvas');cv.width=w;cv.height=h;
 const ctx=cv.getContext('2d',{willReadFrequently:true});ctx.drawImage(img,0,0);
 const src=ctx.getImageData(0,0,w,h).data,dst=ctx.createImageData(w,h),out=dst.data,mask=new Uint8Array(w*h);
 const old=mesh.uvs,ix=mesh.indices,off=part.uvPaintOffset||[0,0];
 if(!Array.isArray(off)||off.length!==2||off.some(v=>!Number.isFinite(v)))throw Error('Unsupported paint offset');
 const wrap=x=>((x%1)+1)%1;
 for(let k=0;k<ix.length;k+=3){
  const ids=ix.slice(k,k+3),a=ids.map(i=>[next[i*2]*w,(1-next[i*2+1])*h]);
  const [A,B,C]=a,det=(B[0]-A[0])*(C[1]-A[1])-(B[1]-A[1])*(C[0]-A[0]);
  if(Math.abs(det)<1e-12)throw Error('Collapsed rebake triangle');
  const minX=Math.max(0,Math.floor(Math.min(...a.map(p=>p[0])))),maxX=Math.min(w-1,Math.ceil(Math.max(...a.map(p=>p[0]))));
  const minY=Math.max(0,Math.floor(Math.min(...a.map(p=>p[1])))),maxY=Math.min(h-1,Math.ceil(Math.max(...a.map(p=>p[1]))));
  for(let y=minY;y<=maxY;y++)for(let x=minX;x<=maxX;x++){
   const X=x+.5-A[0],Y=y+.5-A[1],b=(X*(C[1]-A[1])-Y*(C[0]-A[0]))/det,c=((B[0]-A[0])*Y-(B[1]-A[1])*X)/det,d=1-b-c;
   if(Math.min(b,c,d)<-1e-8)continue;
   const u=old[ids[0]*2]*d+old[ids[1]*2]*b+old[ids[2]*2]*c;
   const v=old[ids[0]*2+1]*d+old[ids[1]*2+1]*b+old[ids[2]*2+1]*c;
   const sx=Math.min(w-1,Math.floor(wrap(u+off[0])*w)),sy=Math.min(h-1,Math.floor((1-wrap(v+off[1]))*h)),j=y*w+x,i=(sy*w+sx)*4;
   out.set(src.subarray(i,i+4),j*4);mask[j]=1;
  }
 }
 if(!mask.some(Boolean))throw Error('Texture rebake produced no pixels');
 // Bounded gutter dilation, without overwriting any actual triangle pixels.
 for(let pass=0;pass<4;pass++){
  const prev=mask.slice();
  for(let y=0;y<h;y++)for(let x=0;x<w;x++){
   const i=y*w+x;if(prev[i])continue;
   const j=[x?i-1:-1,x+1<w?i+1:-1,y?i-w:-1,y+1<h?i+w:-1].find(j=>j>=0&&prev[j]);
   if(j===undefined)continue;out.set(out.subarray(j*4,j*4+4),i*4);mask[i]=1;
  }
 }
 ctx.putImageData(dst,0,0);
 return {canvas:cv,data:cv.toDataURL('image/png')};
}
async function se557Prepare(t,core){
 const mesh=se555ModelData(t),uv=t.mesh.geometry.getAttribute('uv'),mat=t.mesh.material;
 if(Array.isArray(mat)||!mat||!uv||uv.count*2!==mesh.uvs?.length||uv.isInterleavedBufferAttribute)throw Error('Requires one editable UV mesh and one material');
 if(['normalMap','roughnessMap','metalnessMap','aoMap','emissiveMap','alphaMap','lightMap','bumpMap','displacementMap'].some(k=>mat[k]))throw Error('Additional texture channels require a multi-map rebake; model left untouched');
 if(mat.map&&!t.part.uvPaintPNG)throw Error('External/material texture cannot be rebaked safely');
 if(mat.map&&(mat.map.rotation!==0||mat.map.repeat.x!==1||mat.map.repeat.y!==1||mat.map.flipY!==true))throw Error('Unsupported texture transform; model left untouched');
 const result=core.optimizeExistingUV(mesh,{resolution:2048,padding:8});
 if(!result.changed)return {t,mesh,result};
 const paint=await se557Rebake(t.part,mesh,result.uvs);
 const map=paint?new THREE.CanvasTexture(paint.canvas):null;
 if(map&&THREE.SRGBColorSpace)map.colorSpace=THREE.SRGBColorSpace;
 if(map){map.wrapS=map.wrapT=THREE.RepeatWrapping;}
 return {t,mesh,result,paint,map,originalUV:mesh.uvs.slice(),originalPNG:t.part.uvPaintPNG,originalOffset:JSON.stringify(t.part.uvPaintOffset||[0,0])};
}
async function se557Optimize(all=false){
 if(se557Busy||se555Busy)return false;
 const current=se551Target(),targets=all?(model()?.parts||[]).map(part=>({part,mesh:modelRoot?.children.find(x=>x.isMesh&&x.userData.atelierId===part.id)})).filter(t=>t.mesh&&t.part.topologyMesh):current?[current]:[];
 if(!targets.length){status('Select an editable topology mesh first');return false;}
 se557Busy=true;const prepared=[],skipped=[];
 try{
  const {core}=await se555Imports();
  for(const t of targets){try{const p=await se557Prepare(t,core);if(p.result.changed)prepared.push(p);else skipped.push(t.part.name+': no measurable improvement');}catch(e){skipped.push(t.part.name+': '+String(e.message||e));}}
  if(!prepared.length){status('No UV changes. '+skipped.join('; ').slice(0,200));return false;}
  const summary=prepared.map(p=>{const r=p.result.report;return p.t.part.name+': '+(r.packing?'area '+(r.packing.baselineTriangleArea*100).toFixed(1)+'% → '+(r.packing.candidateTriangleArea*100).toFixed(1)+'%':'packing unchanged')+(r.relaxation?', worst stretch '+r.relaxation.before.max.toFixed(2)+' → '+r.relaxation.after.max.toFixed(2):'');}).join('\n');
  if(!confirm('Apply verified UV improvement to '+prepared.length+' mesh(es)?\n'+summary+(skipped.length?'\nSkipped: '+skipped.join('; ').slice(0,350):'')+'\nEmbedded PNG paint is rebaked where supported. Undo restores original.'))return false;
  // Reject stale targets if the user edited/switched the project during async rebake.
  for(const p of prepared){if(!model()?.parts?.includes(p.t.part)||p.t.part.topologyMesh!==p.mesh||p.mesh.uvs.some((x,i)=>x!==p.originalUV[i])||p.t.part.uvPaintPNG!==p.originalPNG||JSON.stringify(p.t.part.uvPaintOffset||[0,0])!==p.originalOffset)throw Error('Mesh changed during preview; retry');}
  checkpoint();se555HeatmapClear();se552ClearRegionMesh();se551Selection=null;
  for(const p of prepared){
   const {t,mesh,result,paint,map}=p;
   mesh.uvs=result.uvs.slice();
   const uv=t.mesh.geometry.getAttribute('uv');for(let i=0;i<uv.count;i++)uv.setXY(i,result.uvs[i*2],result.uvs[i*2+1]);uv.needsUpdate=true;
   if(paint){t.part.uvPaintPNG=paint.data;t.part.uvPaintOffset=[0,0];t.mesh.material.map=map;t.mesh.material.needsUpdate=true;p.map=null;}
  }
  signalEdited();se356UVPreviewSchedule();
  status('UV optimization applied to '+prepared.length+' mesh(es); '+skipped.length+' skipped. '+summary.replace(/\n/g,'; ').slice(0,200));
  const label=se552Portal?.host?.querySelector('[data-se555-summary]');if(label)label.textContent=summary.replace(/\n/g,' · ').slice(0,300);
  return true;
 }catch(e){status('UV optimization stopped: '+String(e.message||e).slice(0,220));return false;}
 finally{for(const p of prepared)p.map?.dispose();se557Busy=false;}
}
const se557OpenBase=se552Open;
se552Open=function(){
 // Original expanded portal forces paint mode; default to complete UV
 // wireframe and numbered regions so an untextured mesh is never invisible.
 if(!se557ExpandedBefore){se552ShowWires=true;se552ShowRegions=true;se557ExpandedBefore=true;}
 se557OpenBase();
 const host=se552Portal?.host,controls=host?.children?.[1];
 if(!controls||controls.querySelector('[data-se557-optimize]'))return;
 controls.style.cssText='display:flex;flex-wrap:wrap;align-items:center;gap:6px;padding:6px 0;max-height:38dvh;overflow:auto;flex:none';
 for(const el of controls.querySelectorAll('label'))el.style.cssText+=';flex:0 1 auto;min-width:0;white-space:normal;overflow-wrap:anywhere;font-size:12px';
 for(const el of controls.querySelectorAll('button'))el.style.cssText+=';max-width:100%;min-height:34px;white-space:normal;font-size:12px';
 const wires=controls.querySelector('[data-se552-wires]');if(wires)wires.checked=se552ShowWires;
 const regions=controls.querySelector('[data-se552-regions]');if(regions)regions.checked=se552ShowRegions;
 const make=(label,key,all)=>{const b=document.createElement('button');b.type='button';b.dataset[key]='1';b.textContent=label;b.style.cssText='padding:8px;background:#254658;color:white;border:1px solid #537e91;border-radius:6px;min-height:34px';controls.append(b);b.onclick=()=>void se557Optimize(all);};
 make('Optimize UV','se557Optimize',false);make('Optimize all editable meshes','se557OptimizeAll',true);
 se356UVPreviewSchedule();
};
window.SWYRL_ENGINE_UV_OPTIMIZE=Object.freeze({optimize:se557Optimize,status:()=>({busy:se557Busy,scope:'editable indexed meshes, per-mesh atlas'})});
/* SE557_UNIVERSAL_UV_END */
