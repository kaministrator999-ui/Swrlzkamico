function atelierHairPinataGroupsV1193(){
 return new Set((model()?.assemblies?.components||[]).filter(c=>['azure','coral'].includes(c.id)).map(c=>c.group));
}
function atelierFitBoxV1193(box,view='three'){
 if(box.isEmpty())return false;
 box.expandByScalar(.15);const center=box.getCenter(new THREE.Vector3()),yaw=({front:0,back:Math.PI,right:Math.PI/2,left:-Math.PI/2,three:.22})[view]??.22;
 atelierDetailTarget=center;atelierCameraPan.set(0,0,0);orbit={yaw,pitch:.04,distance:5};cameraUpdate();
 const inverse=camera.quaternion.clone().invert(),tanY=Math.tan(camera.fov*Math.PI/360),tanX=tanY*camera.aspect;let distance=.1;
 for(const x of [box.min.x,box.max.x])for(const y of [box.min.y,box.max.y])for(const z of [box.min.z,box.max.z]){const p=new THREE.Vector3(x,y,z).sub(center).applyQuaternion(inverse);distance=Math.max(distance,Math.abs(p.x)/tanX+p.z,Math.abs(p.y)/tanY+p.z);}
 orbit.distance=distance*1.10+.08;cameraUpdate();atelierHDDirty=true;return true;
}
function atelierAnimeFrame(mode='body',view='three'){
 if(mode==='legs'&&currentProject.canonicalId==='organic-anime-girl'&&modelRoot){const mesh=modelRoot.children.find(m=>m.userData.atelierId==='girl-organic-body'),box=new THREE.Box3();mesh.updateMatrixWorld(true);const a=mesh.geometry.attributes.position;for(let i=0;i<a.count;i++){const p=new THREE.Vector3().fromBufferAttribute(a,i).applyMatrix4(mesh.matrixWorld);if(p.y<2.76)box.expandByPoint(p);}return atelierFitBoxV1193(box,view);}
 const result=atelierAnimeFrameV1192(mode,view);if(currentProject.canonicalId!=='organic-anime-girl'||!modelRoot)return result;
 // Hair companions stay part of the girl in every detail view. Portrait/hands
 // retain their close framing; only full/body views fit the complete assembly.
 const groups=atelierHairPinataGroupsV1193();
 for(const mesh of modelRoot.children){const part=partById(mesh.userData.atelierId);if(part&&groups.has(part.group))mesh.visible=true;}
 if(mode==='body'){const box=new THREE.Box3();for(const mesh of modelRoot.children)if(mesh.visible)box.union(new THREE.Box3().setFromObject(mesh));return atelierFitBoxV1193(box,view);}
 atelierHDDirty=true;return result;
}
function atelierGirlPresentationV1193(){
 if(!modelRoot)return null;
 camera.updateMatrixWorld(true);const frustum=new THREE.Frustum().setFromProjectionMatrix(new THREE.Matrix4().multiplyMatrices(camera.projectionMatrix,camera.matrixWorldInverse)),groups={};
 for(const mesh of modelRoot.children){const part=partById(mesh.userData.atelierId);if(!part)continue;const group=groups[part.group]||(groups[part.group]={parts:0,visible:0,inView:0});group.parts++;if(mesh.visible){group.visible++;if(frustum.intersectsBox(new THREE.Box3().setFromObject(mesh)))group.inView++;}}
 return {revision:'v11.93',groups,hairGroups:[...atelierHairPinataGroupsV1193()],camera:{distance:orbit.distance,aspect:camera.aspect},coverage:modelRoot.children.filter(mesh=>['festival-shorts','right-arm-band','left-wrist-cuff','bodice-stitch-2'].includes(mesh.userData.atelierId)).map(mesh=>({id:mesh.userData.atelierId,opacity:mesh.material.opacity,transparent:mesh.material.transparent,side:mesh.material.side,visible:mesh.visible})),assemblies:atelierAssemblyStatus()};
}

const atelierPinataStudioBaseV1193=atelierAnimeStudio;
atelierAnimeStudio=function(){atelierPinataStudioBaseV1193();const bar=document.getElementById('modelAtelierAnimeViews');if(currentProject.canonicalId!=='organic-anime-girl'||!bar||document.getElementById('modelAtelierLegDetail'))return;const button=document.createElement('button');button.id='modelAtelierLegDetail';button.textContent='Leg detail';button.style.cssText='min-height:44px;padding:6px 12px;border:1px solid #608f9d;border-radius:8px;background:#172a40e8;color:#e7f3ec;font:600 12px system-ui';button.onclick=()=>atelierAnimeFrame('legs','three');bar.append(button);};
