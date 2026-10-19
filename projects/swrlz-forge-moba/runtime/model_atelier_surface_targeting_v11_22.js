// §E v11.22 precision selection. The existing spherical brush remains
// backward-compatible: older strokes lacking surfaceMode use through-volume.
// New strokes default to FRONT-facing and connected-surface selection.
// All computation uses part-LOCAL vertices and never alters source topology.
const atelierSurfaceModes=['front','connected','inside','through','nearest','occluded','visible-geodesic'];
function atelierSurfaceTangent(axis) {
 const n=new THREE.Vector3(...axis).normalize();
 const helper=Math.abs(n.y)<.84?new THREE.Vector3(0,1,0):new THREE.Vector3(1,0,0);
 const u=new THREE.Vector3().crossVectors(helper,n).normalize();
 return [u,new THREE.Vector3().crossVectors(n,u).normalize()];
}
function atelierSurfaceCenter(stroke) {
 const c=new THREE.Vector3(...stroke.center),[u,v]=atelierSurfaceTangent(stroke.axis);
 return c.addScaledVector(u,stroke.offsetU||0).addScaledVector(v,stroke.offsetV||0);
}
function atelierSurfaceWeights(geometry,stroke) {
 const a=geometry.attributes.position;
 const mode=stroke.surfaceMode||'through';
 const radius=stroke.selectionRadius||stroke.radius;
 const origin=atelierSurfaceCenter(stroke),axis=new THREE.Vector3(...stroke.axis).normalize();
 const count=a.count,dist=new Float32Array(count);dist.fill(Infinity);
 const valid=new Uint8Array(count),xyz=new Float32Array(count*3);
 const normal=geometry.attributes.normal;
 let nearest=-1,nearestDist=Infinity;
 for(let i=0;i<count;i++){
   const x=a.getX(i),y=a.getY(i),z=a.getZ(i),k=i*3;
   xyz[k]=x;xyz[k+1]=y;xyz[k+2]=z;
   const dx=x-origin.x,dy=y-origin.y,dz=z-origin.z;
   const d=Math.hypot(dx,dy,dz);
   // A front-facing shell is not a mere spatial sphere. Reject surfaces
   // whose normals face away from the picked visible face. Never displace
   // far-side vertices on a thin double-sided object by accident.
   const oriented=normal?
     normal.getX(i)*axis.x+normal.getY(i)*axis.y+normal.getZ(i)*axis.z:1;
   // Deliberate interior mode selects the inward-facing opposite-normal
   // shell. The usual front/connected modes retain their legacy behavior.
   const faceOk=mode==='through'||mode==='occluded'||mode==='visible-geodesic'||!normal||
     (mode==='inside'?oriented<-.12:oriented>-.08);
   if(!faceOk||d>radius+1e-5)continue;
   valid[i]=1;
   if(d<nearestDist){nearest=i;nearestDist=d;}
   if(mode!=='connected'&&mode!=='visible-geodesic')dist[i]=d;
 }
 // Conservative nearest-facing shell for stacked same-normal geometry.
 // This is a projected depth filter relative to the picked brush axis, NOT
 // full camera pixel-accurate occlusion or an artistically inferred surface.
 // Existing front/inside/through/connected behavior remains unchanged.
 if(mode==='nearest'){
   const [u,v]=atelierSurfaceTangent(stroke.axis);
   const cell=Math.max(.004,radius/32),limit=Math.max(.008,cell*1.25);
   const binKeys=new Array(count),heights=new Float32Array(count),depth=new Map();
   for(let i=0;i<count;i++){
     if(!valid[i])continue;
     const k=i*3,dx=xyz[k]-origin.x,dy=xyz[k+1]-origin.y,dz=xyz[k+2]-origin.z;
     const ucoord=(dx*u.x+dy*u.y+dz*u.z)/cell;
     const vcoord=(dx*v.x+dy*v.y+dz*v.z)/cell;
     const key=Math.floor(ucoord)+','+Math.floor(vcoord);
     const d=dx*axis.x+dy*axis.y+dz*axis.z;
     binKeys[i]=key;heights[i]=d;
     if(!depth.has(key)||d>depth.get(key))depth.set(key,d);
   }
   for(let i=0;i<count;i++){
     if(!valid[i])continue;
     if(heights[i]+limit<depth.get(binKeys[i])){
       valid[i]=0;dist[i]=Infinity;
     }
   }
   return {dist,origin,valid,radius};
 }
 if(mode==='occluded'||mode==='visible-geodesic'){
  // Camera-eye rays are tested against actual frontmost triangles, not
  // sampled normals or projected depth bins. Missing/oversize data fails shut.
  const visible=atelierBrushOcclusionMask(geometry,stroke.cameraLocal,valid,radius);
  if(!visible){dist.fill(Infinity);valid.fill(0);
    return {dist,origin,valid,radius,error:'Occlusion mesh/eye exceeds safe bounds'};}
  for(let i=0;i<count;i++)if(valid[i]&&!visible[i]){
    valid[i]=0;dist[i]=Infinity;
  }
  if(mode==='occluded')return {dist,origin,valid,radius};
  // The initial nearest vertex might itself have been occluded.
  // Pick the closest *camera-visible* seed before doing geodesic traversal.
  nearest=-1;nearestDist=Infinity;
  for(let i=0;i<count;i++)if(valid[i]){
   const k=i*3,d=Math.hypot(xyz[k]-origin.x,xyz[k+1]-origin.y,xyz[k+2]-origin.z);
   if(d<nearestDist){nearestDist=d;nearest=i;}
  }
  if(nearest<0)return {dist,origin,valid,radius};
 }
 if((mode!=='connected'&&mode!=='visible-geodesic')||nearest<0)
   return {dist,origin,valid,radius};
 // Geodesic traversal is restricted to actual connected triangles. Camera-
 // visible mode has already removed all ray-occluded vertex candidates.
 // UV seam
 // duplicates with coincident coordinates are welded virtually for selection
 // only; underlying UVs and vertex indices are not modified.
 const welded=new Map(),groups=[],keys=new Int32Array(count);
 for(let i=0;i<count;i++){
   const j=3*i,key=Math.round(xyz[j]*1e5)+','+Math.round(xyz[j+1]*1e5)+','+Math.round(xyz[j+2]*1e5);
   let id=welded.get(key);
   if(id===undefined){id=groups.length;welded.set(key,id);groups.push([]);}
   keys[i]=id;groups[id].push(i);
 }
 const links=Array.from({length:groups.length},()=>new Set());
 const indices=geometry.index;
 const faceCount=indices?Math.floor(indices.count/3):Math.floor(count/3);
 const edge=(a,b)=>{if(a!==b){links[a].add(b);links[b].add(a);}};
 for(let face=0;face<faceCount;face++){
   const a=indices?indices.getX(face*3):face*3;
   const b=indices?indices.getX(face*3+1):face*3+1;
   const c=indices?indices.getX(face*3+2):face*3+2;
   const x=keys[a],y=keys[b],z=keys[c];
   edge(x,y);edge(y,z);edge(z,x);
 }
 const enabled=new Uint8Array(groups.length);
 for(let i=0;i<count;i++)if(valid[i])enabled[keys[i]]=1;
 const shortest=new Float32Array(groups.length);shortest.fill(Infinity);
 const seed=keys[nearest],queue=[[0,seed]];shortest[seed]=nearestDist;
 // Bounded Dijkstra: heap avoids O(N²) scans on high-resolution mobile head.
 const push=(item)=>{queue.push(item);let i=queue.length-1;
   while(i){const p=(i-1)>>1;if(queue[p][0]<=item[0])break;queue[i]=queue[p];i=p;}
   queue[i]=item;};
 const pop=()=>{const top=queue[0],last=queue.pop();if(queue.length){
   let i=0;while(i*2+1<queue.length){let child=i*2+1;
     if(child+1<queue.length&&queue[child+1][0]<queue[child][0])child++;
     if(last[0]<=queue[child][0])break;queue[i]=queue[child];i=child;}
   queue[i]=last;
 }return top;};
 const pos=(id)=>{const i=groups[id][0]*3;return [xyz[i],xyz[i+1],xyz[i+2]];};
 while(queue.length){
   const [d,id]=pop();
   if(d>shortest[id]+1e-6||d>radius)continue;
   const p=pos(id);
   for(const n of links[id]){
     if(!enabled[n])continue;
     const q=pos(n),length=Math.hypot(p[0]-q[0],p[1]-q[1],p[2]-q[2]);
     const next=d+length;
     if(next<=radius&&next+1e-6<shortest[n]){shortest[n]=next;push([next,n]);}
   }
 }
 for(let i=0;i<count;i++)dist[i]=valid[i]?shortest[keys[i]]:Infinity;
 return {dist,origin,valid,radius};
}
function atelierSurfacePreviewClear(){
 const p=atelierSurfacePreview;
 if(!p)return;
 p.parent?.remove(p);
 p.geometry?.dispose();p.material?.dispose();
 atelierSurfacePreview=null;
}
let atelierSurfacePreview=null;
function atelierSurfacePreviewRefresh(){
 atelierSurfacePreviewClear();
 if(!atelierSculptHit||!modelRoot||!world)return;
 const part=partById(selection);
 if(!part||part.id!==atelierSculptHit.partId)return;
 const mesh=modelRoot.children.find(o=>o.isMesh&&o.userData.atelierId===part.id);
 if(!mesh)return;
 const stroke=atelierSculptForm();
 if(!stroke)return;
 const selection=atelierSurfaceWeights(mesh.geometry,stroke),array=mesh.geometry.attributes.position;
 const n=array.count,stride=Math.max(1,Math.ceil(n/2500)),verts=[];
 for(let i=0;i<n;i+=stride){
   if(selection.dist[i]>=selection.radius)continue;
   const p=mesh.localToWorld(new THREE.Vector3(array.getX(i),array.getY(i),array.getZ(i)));
   verts.push(p.x,p.y,p.z);
 }
 const geometry=new THREE.BufferGeometry();
 geometry.setAttribute('position',new THREE.Float32BufferAttribute(verts,3));
 atelierSurfacePreview=new THREE.Points(geometry,new THREE.PointsMaterial({
   color:0xffc34b,size:5,sizeAttenuation:false,depthTest:true
 }));
 atelierSurfacePreview.name='Surface selection preview';
 atelierSurfacePreview.userData.atelierHelper=true;
 atelierSurfacePreview.renderOrder=26;world.add(atelierSurfacePreview);
 const info=$m('SurfaceSelectionInfo');
 if(info)info.textContent=(verts.length/3)+' visible preview control points · '+
  (stroke.surfaceMode||'through')+' · selection radius '+selection.radius.toFixed(2)+
  ' · influence radius '+stroke.radius.toFixed(2);
}
function atelierSculptSurfaceInstall(){
 for(const id of ['SculptBrushRadiusUnits','SculptBrushRadiusScreen','SculptBrushSelectRadiusScreen']){
  $m(id)?.addEventListener('input',()=>{
   atelierBrushSizingRefresh();atelierSurfacePreviewRefresh();
  });
  $m(id)?.addEventListener('change',()=>{
   atelierBrushSizingRefresh();atelierSurfacePreviewRefresh();
  });
 }
 for(const id of ['SculptBrushSelectRadius','SculptBrushSurfaceMode','SculptBrushOffsetU',
    'SculptBrushOffsetV','SculptBrushRadius']){
   $m(id)?.addEventListener('input',atelierSurfacePreviewRefresh);
   $m(id)?.addEventListener('change',atelierSurfacePreviewRefresh);
 }
 $m('SculptBrushPreview')?.addEventListener('click',()=>{
   if(!atelierSculptHit){status('Pick a point on a selected mesh before previewing.',true);return;}
   atelierSurfacePreviewRefresh();
 });
 $m('SculptBrushPreviewClear')?.addEventListener('click',atelierSurfacePreviewClear);
}
