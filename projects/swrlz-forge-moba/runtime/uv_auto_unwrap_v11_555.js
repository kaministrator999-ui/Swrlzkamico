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
  se555Modules=Promise.all([
   import(base+'uv_atlas_core_v11_555.mjs'),
   import(base+'index.mjs')
  ]).then(([core,wasm])=>({core,createXAtlas:wasm.default}));
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
   weldSeams:true,faceMaterialData:marked.size?seams.materials:null,
   resolution:1024,padding:8,maxCost:10,
   maxVertices:t.part.id==='clean-topology-humanoid-base'?9000:120000,
   maxCharts:100
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
  status('Real xatlas unwrap: '+result.charts+' charts, '+result.positions.length/3+
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
 const unwrap=make('Auto unwrap · xatlas','se555Auto');
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
