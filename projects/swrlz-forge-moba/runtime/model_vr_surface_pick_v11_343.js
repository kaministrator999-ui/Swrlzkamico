/* SE343_MODEL_VR_SURFACE_HOVER_START */
// Simplified continuous picking skin for passive XR hover. These hidden
// meshes are never rendered or persisted as part of the model document.
// Only Trigger and Grip use the original, full-resolution editable geometry.
const SE343_HOVER_FACE_BUDGET=3600;
function se343HoverGeometry(source,isSkinned){
 const pos=source?.getAttribute?.('position'),idx=source?.getIndex?.();
 if(!pos||pos.itemSize!==3)return null;
 const triangles=Math.floor((idx?idx.count:pos.count)/3);
 if(!triangles)return null;
 if(triangles<=SE343_HOVER_FACE_BUDGET)return {geometry:source,owned:false,faces:triangles};
 const skinIdx=isSkinned?source.getAttribute('skinIndex'):null;
 const skinWt=isSkinned?source.getAttribute('skinWeight'):null;
 if(isSkinned&&(!skinIdx||!skinWt))return null;
 if(!source.boundingBox)source.computeBoundingBox();
 const min=source.boundingBox.min,extent=source.boundingBox.getSize(new THREE.Vector3());
 const maxSize=Math.max(extent.x,extent.y,extent.z,.0001);
 const remap=new Int32Array(pos.count);
 const values=(a,i)=>[a.getX(i),a.getY(i),a.getZ(i),a.getW(i)];
 let chosen=null;
 // Spatial vertex clustering creates a connected shell rather than sparse
 // isolated triangles. The principal bone ID protects adjacent fingers from
 // being welded together when their positions are close in bind pose.
 for(const divisions of [32,25,20,16,12,9,7,5,3]){
  const groups=[],lookup=new Map(),scale=divisions/maxSize;
  for(let i=0;i<pos.count;i++){
   const x=pos.getX(i),y=pos.getY(i),z=pos.getZ(i);
   let bone=0;
   if(skinIdx&&skinWt){
    const w=values(skinWt,i),b=values(skinIdx,i);
    let highest=-1;
    for(let j=0;j<4;j++)if(w[j]>highest){highest=w[j];bone=b[j];}
   }
   const key=Math.floor((x-min.x)*scale)+','+Math.floor((y-min.y)*scale)+','+Math.floor((z-min.z)*scale)+','+bone;
   let group=lookup.get(key);
   if(group===undefined){group=groups.length;lookup.set(key,group);groups.push({x:0,y:0,z:0,count:0,original:i});}
   const item=groups[group];item.x+=x;item.y+=y;item.z+=z;item.count++;remap[i]=group;
  }
  const faces=[],used=new Set();
  for(let i=0;i<triangles;i++){
   const a=remap[idx?idx.getX(i*3):i*3],b=remap[idx?idx.getX(i*3+1):i*3+1],c=remap[idx?idx.getX(i*3+2):i*3+2];
   if(a===b||a===c||b===c)continue;
   const key=[a,b,c].sort((x,y)=>x-y).join(':');
   if(used.has(key))continue;
   used.add(key);faces.push(a,b,c);
  }
  if(!faces.length)continue;
  chosen={groups,faces};
  if(faces.length/3<=SE343_HOVER_FACE_BUDGET)break;
 }
 if(!chosen)return null;
 const {groups,faces}=chosen,xyz=new Float32Array(groups.length*3);
 const joints=isSkinned?new Uint16Array(groups.length*4):null;
 const weights=isSkinned?new Float32Array(groups.length*4):null;
 for(let i=0;i<groups.length;i++){
  const g=groups[i],j=i*3;
  xyz[j]=g.x/g.count;xyz[j+1]=g.y/g.count;xyz[j+2]=g.z/g.count;
  if(joints){
   const original=g.original,ids=values(skinIdx,original),ws=values(skinWt,original);
   for(let k=0;k<4;k++){joints[i*4+k]=ids[k];weights[i*4+k]=ws[k];}
  }
 }
 const geo=new THREE.BufferGeometry();
 geo.setAttribute('position',new THREE.BufferAttribute(xyz,3));geo.setIndex(faces);
 if(joints){
  geo.setAttribute('skinIndex',new THREE.BufferAttribute(joints,4));
  geo.setAttribute('skinWeight',new THREE.BufferAttribute(weights,4));
 }
 geo.computeBoundingBox();geo.computeBoundingSphere();
 return {geometry:geo,owned:true,faces:faces.length/3};
}
function se343DropHoverSurfaces(){
 const s=se340XR;
 for(const geo of s.hoverGeometries)geo.dispose();
 s.hoverGeometries.clear();s.hoverSurfaceCache=new WeakMap();
}
function se343SurfaceMesh(mesh){
 const s=se340XR,geometry=mesh?.geometry,version=geometry?.getAttribute?.('position')?.version||0;
 if(!geometry)return null;
 let entry=s.hoverSurfaceCache.get(mesh);
 if(entry&&entry.source===geometry&&entry.version===version)return entry.proxy;
 if(entry?.owned){entry.proxy.geometry.dispose();s.hoverGeometries.delete(entry.proxy.geometry);}
 const sampled=se343HoverGeometry(geometry,!!mesh.isSkinnedMesh);
 if(!sampled)return null;
 if(!s.hoverSurfaceMaterial)s.hoverSurfaceMaterial=se340Own(new THREE.MeshBasicMaterial({side:THREE.DoubleSide}));
 const proxy=mesh.isSkinnedMesh?new THREE.SkinnedMesh(sampled.geometry,s.hoverSurfaceMaterial):
  new THREE.Mesh(sampled.geometry,s.hoverSurfaceMaterial);
 proxy.matrixAutoUpdate=false;proxy.matrixWorldAutoUpdate=false;
 if(mesh.isSkinnedMesh){
  proxy.skeleton=mesh.skeleton;proxy.bindMode=mesh.bindMode;
  proxy.bindMatrix.copy(mesh.bindMatrix);proxy.bindMatrixInverse.copy(mesh.bindMatrixInverse);
  // Three's SkinnedMesh.raycast would otherwise rebuild posed bounds by
  // transforming every proxy vertex on each pointer move.
  if(!sampled.geometry.boundingBox)sampled.geometry.computeBoundingBox();
  if(!sampled.geometry.boundingSphere)sampled.geometry.computeBoundingSphere();
  const size=sampled.geometry.boundingBox.getSize(new THREE.Vector3());
  const pad=Math.max(size.x,size.y,size.z)*.75+.04;
  proxy.boundingBox=sampled.geometry.boundingBox.clone().expandByScalar(pad);
  proxy.boundingSphere=sampled.geometry.boundingSphere.clone();
  proxy.boundingSphere.radius+=pad;
 }
 if(sampled.owned)s.hoverGeometries.add(sampled.geometry);
 s.hoverSurfaceCache.set(mesh,{source:geometry,version,proxy,owned:sampled.owned});
 return proxy;
}
function se343HoverContact(part,cast){
 const mesh=part.mesh,proxy=se343SurfaceMesh(mesh);
 if(!proxy)return null;
 proxy.matrixWorld.copy(mesh.matrixWorld);
 if(mesh.isSkinnedMesh){
  proxy.skeleton=mesh.skeleton;proxy.bindMatrix.copy(mesh.bindMatrix);
  proxy.bindMatrixInverse.copy(mesh.bindMatrixInverse);
 }
 const contacts=[];
 proxy.raycast(cast,contacts);
 let first=null;
 for(const hit of contacts)
  if(hit.distance>=cast.near&&hit.distance<=cast.far&&(!first||hit.distance<first.distance))first=hit;
 return first?{id:part.id,name:part.name,mesh,
  distance:first.distance,point:first.point,hoverSurface:true}:null;
}
/* SE343_MODEL_VR_SURFACE_HOVER_END */
