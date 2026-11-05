// §E v11.279 · Blank VR Hands starter + physically mirrored Arcane Glove.
// The source hand, native rig, saved scenes and existing XR controller bindings
// remain intact. Both hands use the SAME authored editable meshes and 17 joints.
const se279GameId='blank-vr-hands';
const se279LeftId='arcane-glove-left';
const se279Hands={attached:new Map(),lastError:'',updates:0};
function se279MirrorPose(pose){
 const reflected={};
 for(const [id,angles] of Object.entries(pose||{}))
  reflected[id]=[angles[0],-angles[1],-angles[2]];
 return reflected;
}
// Mirror actual mesh vertices, not a negative-scale renderer shortcut.
// A reflection reverses triangle winding; reverse it again for outward faces.
function se279LeftScene(){
 const source=se212HandScene();
 const model=source.project.modelAtelier;
 if(!se220RigValidate(model.rigging))throw Error('The original glove rig is missing.');
 for(const part of model.parts){
  part.id='left-'+part.id;part.name='Left · '+part.name;
  part.position[0]=-part.position[0];
  part.rotation[1]=-part.rotation[1];part.rotation[2]=-part.rotation[2];
  const topology=part.topologyMesh;
  if(topology?.positions?.length){
   for(let i=0;i<topology.positions.length;i+=3)topology.positions[i]=-topology.positions[i];
   if(topology.indices)for(let i=0;i<topology.indices.length;i+=3){
    const swap=topology.indices[i+1];
    topology.indices[i+1]=topology.indices[i+2];topology.indices[i+2]=swap;
   }
   if(topology.normals)for(let i=0;i<topology.normals.length;i+=3)
    topology.normals[i]=-topology.normals[i];
  }
 }
 for(const group of model.meshGroups||[])
  group.members=group.members.map(id=>'left-'+id);
 const rig=model.rigging;
 rig.handedness='left';
 for(const b of rig.bones)b.rest[0]=-b.rest[0];
 for(const d of rig.digits){d.x=-d.x;d.splay=-d.splay;}
 rig.pose=se279MirrorPose(rig.pose);
 rig.timeline=rig.timeline.map(k=>({time:k.time,pose:se279MirrorPose(k.pose)}));
 model.name='Floating Hand · Arcane Glove (Left)';
 model.reference='Mirrored from the editable original Arcane Glove. Native mesh faces, thumb side, rig pivots and gesture axes are reflected.';
 source.project.name=model.name;
 source.project.canonicalId=se279LeftId;source.project.template=se279LeftId;
 source.engine='§wyrl§ Engine · Maker v11.279';source.version=11.279;
 if(!se220RigValidate(rig))throw Error('Mirrored hand skeleton is invalid.');
 return source;
}
// The original procedural skin solver expects a thumb on X-negative.
// Reflect only the INPUT to the solver for a left rig; bone IDs stay the same.
const se279WeightSources=new WeakMap();
const se279OriginalWeights=se220RigWeights;
se220RigWeights=function(point,rig){
 if(rig?.handedness!=='left')return se279OriginalWeights(point,rig);
 let canonical=se279WeightSources.get(rig);
 if(!canonical){
  canonical={...rig,handedness:'right',digits:rig.digits.map(d=>({...d,x:-d.x,splay:-d.splay}))};
  se279WeightSources.set(rig,canonical);
 }
 return se279OriginalWeights([-point[0],point[1],point[2]],canonical);
};
// Euler XYZ reflection about X leaves X rotation unchanged and negates Y/Z.
// Apply to gesture PRESETS as well as the saved rig and default timeline.
const se279OriginalGesture=se221GesturePose;
se221GesturePose=function(rig,kind){
 const pose=se279OriginalGesture(rig,kind);
 return rig?.handedness==='left'?se279MirrorPose(pose):pose;
};
const se279OriginalWave=se223WavePose;
se223WavePose=function(rig,side,flutter=0){
 if(rig?.handedness!=='left')return se279OriginalWave(rig,side,flutter);
 const canonical={...rig,handedness:'right'};
 return se279MirrorPose(se279OriginalWave(canonical,side,flutter));
};
function se279OpenLeft(force=false){
 if(dirty&&!force&&!confirm('Open the left Arcane Glove and discard unsaved changes?'))return false;
 try{
  const source=se279LeftScene();
  ModelAtelier.close();loadProject(source,{workspaceLocal:true});
  initializeHistory('Opened mirrored left Arcane Glove');markSaved();
  document.getElementById('projectHub')?.classList.remove('show');
  se232ActivateSelectedModelWorkspace();ModelAtelier.syncProject();
  requestAnimationFrame(()=>requestAnimationFrame(()=>window.SWYRL_ENGINE_MODEL_ATELIER?.view?.('three')));
  toast('Left Arcane Glove · all 17 mirrored joints and gesture clips are editable');
  return true;
 }catch(e){se279Hands.lastError=String(e);console.error('Left hand starter',e);
  toast('Cannot open left glove: '+e.message);return false;}
}
function se279CreateBlank(){
 clearAll();
 applyProjectMeta({name:'Blank VR · Arcane Hands',template:se279GameId,
  kind:se279GameId,environment:'starter'});
 setProjectBackground('#10131d');
 rebuildTerrain();makeGroundActor(); // One editable ground; no trees, pawns, AI or props.
 finishTemplate('hero');
 initializeHistory('Created blank VR hand level');markSaved();
 document.getElementById('projectHub')?.classList.remove('show');
 toast('Blank VR level ready. Enter VR to see both Arcane Glove controllers.');
 return true;
}
const se279PriorTemplate=createProjectFromTemplate;
createProjectFromTemplate=function(id,force=false){
 if(id===se279LeftId)return se279OpenLeft(force);
 if(id===se279GameId){
  if(dirty&&!force&&!confirm('Create a blank VR hand level and discard unsaved changes?'))return false;
  return se279CreateBlank();
 }
 return se279PriorTemplate(id,force);
};
// Build GPU-skinned native glove meshes from source parts. Merge meshes with
// identical materials so Quest draws far fewer objects than the modeler list.
function se279PartGeometry(part){
 let geo;
 if(part.kind==='topologyMesh'){
  const t=part.topologyMesh;if(!t?.positions?.length||!t.indices?.length)return null;
  geo=new THREE.BufferGeometry();
  geo.setAttribute('position',new THREE.Float32BufferAttribute(t.positions,3));
  if(t.uvs?.length===t.positions.length/3*2)
   geo.setAttribute('uv',new THREE.Float32BufferAttribute(t.uvs,2));
  geo.setIndex(t.indices);
 }else if(part.kind==='sphere')geo=new THREE.SphereGeometry(1,14,10);
 else if(part.kind==='cylinder')geo=new THREE.CylinderGeometry(1,1,1,12,1);
 else if(part.kind==='box')geo=new THREE.BoxGeometry(1,1,1);
 else if(part.kind==='cone')geo=new THREE.ConeGeometry(1,1,12);
 else return null;
 const t=new THREE.Matrix4().compose(new THREE.Vector3(...part.position),
  new THREE.Quaternion().setFromEuler(new THREE.Euler(...part.rotation)),
  new THREE.Vector3(...part.scale));
 geo.applyMatrix4(t);
 if(!geo.getAttribute('normal'))geo.computeVertexNormals();
 return geo;
}
function se279Material(p){
 const color=new THREE.Color(p.color);
 if(p.material==='emissive')return new THREE.MeshBasicMaterial({color,side:THREE.DoubleSide});
 return new THREE.MeshStandardMaterial({color,side:THREE.DoubleSide,
  metalness:p.material==='metal'?.68:.05,
  roughness:p.material==='metal'?.28:p.material==='silk'?.53:.82});
}
function se279BuildGlove(side){
 const source=side==='left'?se279LeftScene():se212HandScene();
 const model=source.project.modelAtelier,rig=model.rigging;
 if(!se220RigValidate(rig))throw Error(side+' glove needs a valid skeleton.');
 const poseGroup=new THREE.Group();
 poseGroup.name=side+' · Arcane Glove controller';
 poseGroup.position.set(side==='left'?-.014:.014,-.034,.108);
 poseGroup.rotation.x=-Math.PI/2;
 const modelGroup=new THREE.Group();modelGroup.scale.setScalar(.12);poseGroup.add(modelGroup);
 const boneMap={};
 for(const spec of rig.bones){
  const bone=new THREE.Bone();bone.name=spec.id;
  const parent=spec.parent?rig.bones.find(b=>b.id===spec.parent):null;
  const origin=parent?.rest||[0,0,0];
  bone.position.set(...spec.rest.map((v,i)=>v-origin[i]));
  boneMap[spec.id]=bone;
  if(parent)boneMap[parent.id].add(bone);
  else modelGroup.add(bone);
 }
 const groups=new Map();
 for(const part of model.parts){
  const geo=se279PartGeometry(part);if(!geo)continue;
  const name=part.material+'|'+part.color;
  if(!groups.has(name))groups.set(name,{sample:part,pos:[],norm:[],uv:[],idx:[],bones:[],weights:[],count:0});
  const g=groups.get(name),pos=geo.getAttribute('position'),nor=geo.getAttribute('normal'),uv=geo.getAttribute('uv');
  for(let i=0;i<pos.count;i++){
   const x=pos.getX(i),y=pos.getY(i),z=pos.getZ(i);
   g.pos.push(x,y,z);g.norm.push(nor.getX(i),nor.getY(i),nor.getZ(i));
   g.uv.push(uv?uv.getX(i):0,uv?uv.getY(i):0);
   const inf=se220RigWeights([x,y,z],rig);
   g.bones.push(...inf.indices);g.weights.push(...inf.weights);
  }
  if(geo.index)for(let i=0;i<geo.index.count;i++)g.idx.push(g.count+geo.index.getX(i));
  else for(let i=0;i<pos.count;i++)g.idx.push(g.count+i);
  g.count+=pos.count;geo.dispose();
 }
 const skeleton=new THREE.Skeleton(rig.bones.map(b=>boneMap[b.id]));
 const meshes=[];
 for(const entry of groups.values()){
  const geo=new THREE.BufferGeometry();
  geo.setAttribute('position',new THREE.Float32BufferAttribute(entry.pos,3));
  geo.setAttribute('normal',new THREE.Float32BufferAttribute(entry.norm,3));
  geo.setAttribute('uv',new THREE.Float32BufferAttribute(entry.uv,2));
  geo.setAttribute('skinIndex',new THREE.Uint16BufferAttribute(entry.bones,4));
  geo.setAttribute('skinWeight',new THREE.Float32BufferAttribute(entry.weights,4));
  geo.setIndex(entry.idx);
  const mesh=new THREE.SkinnedMesh(geo,se279Material(entry.sample));
  mesh.frustumCulled=false;mesh.name='Arcane Glove · '+entry.sample.material;
  mesh.normalizeSkinWeights();modelGroup.add(mesh);meshes.push(mesh);
 }
 modelGroup.updateMatrixWorld(true);skeleton.calculateInverses();
 for(const mesh of meshes){mesh.updateMatrixWorld(true);mesh.bind(skeleton,mesh.matrixWorld.clone());}
 const poses={relaxed:se221GesturePose(rig,'relaxed'),
  fist:se221GesturePose(rig,'fist'),grab:se221GesturePose(rig,'grab'),
  pinch:se221GesturePose(rig,'pinch')};
 return {side,root:poseGroup,bones:boneMap,rig,meshes,skeleton,poses,last:0};
}
function se279ReleaseHand(view){
 if(!view)return;
 view.root.removeFromParent();
 for(const m of view.meshes){m.geometry.dispose();m.material.dispose();}
 view.skeleton.dispose?.();
}
function se279Cleanup(){
 for(const view of se279Hands.attached.values())se279ReleaseHand(view);
 se279Hands.attached.clear();
}
function se279Animate(view,record){
 const pad=record?.input?.gamepad;
 const pressed=i=>Math.max(0,Math.min(1,Number(pad?.buttons?.[i]?.value)||0));
 const trigger=pressed(0),grip=pressed(1);
 const a=view.poses.relaxed,b=grip>.84?view.poses.fist:view.poses.grab,c=view.poses.pinch;
 const boneSpecs=view.rig.bones;
 const damp=.35;
 for(const spec of boneSpecs){
  const start=a[spec.id]||[0,0,0],fold=b[spec.id]||start,pinch=c[spec.id]||start;
  const rot=view.bones[spec.id].rotation;
  for(let i=0;i<3;i++){
   const target=(start[i]*(1-grip)+fold[i]*grip)*(1-trigger)+pinch[i]*trigger;
   if(i===0)rot.x+=(target-rot.x)*damp;
   else if(i===1)rot.y+=(target-rot.y)*damp;
   else rot.z+=(target-rot.z)*damp;
  }
 }
 view.skeleton.update();se279Hands.updates++;
}
function se279XRFrame(){
 if(!se181XR.session||!renderer.xr.isPresenting||currentProject?.kind!==se279GameId){
  if(se279Hands.attached.size)se279Cleanup();
  return;
 }
 for(const side of ['left','right']){
  // WebXR source handedness, not hardcoded controller index, is authoritative.
  const record=se181XR.controllers.find(r=>r.input?.handedness===side);
  const previous=se279Hands.attached.get(side);
  if(!record){
   if(previous){se279ReleaseHand(previous);se279Hands.attached.delete(side);}
   continue;
  }
  let hand=previous;
  if(hand&&!hand.root.parent){se279ReleaseHand(hand);se279Hands.attached.delete(side);hand=null;}
  if(!hand){
   try{
    hand=se279BuildGlove(side);record.controller.add(hand.root);
    se279Hands.attached.set(side,hand);
   }catch(e){se279Hands.lastError=String(e);console.error('VR glove build',e);continue;}
  }
  if(hand.root.parent!==record.controller)record.controller.add(hand.root);
  se279Animate(hand,record);
 }
}
window.SWYRL_ENGINE_BLANK_VR_HANDS=Object.freeze({
 create:se279CreateBlank,openLeft:se279OpenLeft,
 leftModel:()=>se279LeftScene(),
 status:()=>({active:currentProject?.kind===se279GameId,
  tracking:[...se279Hands.attached.keys()],updates:se279Hands.updates,
  error:se279Hands.lastError})
});