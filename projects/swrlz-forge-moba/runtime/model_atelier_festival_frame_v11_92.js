// Fit the new upward hair silhouette as well as the underlying anatomical head.
function atelierAnimeFrame(mode='body',view='three'){
 if(currentProject.canonicalId!=='organic-anime-girl'||!modelRoot)return false;
 if(mode==='all'||mode==='hands')return atelierAnimeFrameV1191(mode,view);
 const box=new THREE.Box3();
 for(const mesh of modelRoot.children){
  const part=partById(mesh.userData.atelierId);if(!part)continue;
  mesh.visible=part.group==='Character';if(!mesh.visible)continue;
  mesh.updateMatrixWorld(true);
  if(mode==='portrait'){
   if(part.id==='girl-organic-body'){
    const position=mesh.geometry.attributes.position;
    for(let i=0;i<position.count;i++){const p=new THREE.Vector3().fromBufferAttribute(position,i).applyMatrix4(mesh.matrixWorld);if(p.y>=3.72)box.expandByPoint(p);}
   }else if(['hair','splitHair','eye','iris','lid','lip','brow'].includes(part.organicSurface?.region))box.union(new THREE.Box3().setFromObject(mesh));
  }else box.union(new THREE.Box3().setFromObject(mesh));
 }
 if(box.isEmpty())return false;
 box.expandByScalar(mode==='portrait'?.045:.12);
 const center=box.getCenter(new THREE.Vector3()),yaw=({front:0,back:Math.PI,right:Math.PI/2,left:-Math.PI/2,three:.32})[view]??.32;
 atelierDetailTarget=center;atelierCameraPan.set(0,0,0);orbit={yaw,pitch:mode==='portrait'?.02:.08,distance:5};cameraUpdate();
 const inverse=camera.quaternion.clone().invert(),tanY=Math.tan(camera.fov*Math.PI/360),tanX=tanY*camera.aspect;let distance=.1;
 for(const x of [box.min.x,box.max.x])for(const y of [box.min.y,box.max.y])for(const z of [box.min.z,box.max.z]){const p=new THREE.Vector3(x,y,z).sub(center).applyQuaternion(inverse);distance=Math.max(distance,Math.abs(p.x)/tanX+p.z,Math.abs(p.y)/tanY+p.z);}
 orbit.distance=distance*1.12+.05;cameraUpdate();atelierHDDirty=true;return true;
}
