// Partition the original indexed atlas grid without replacing its pixels or
// changing the head triangles shared by the animated facial expression surface.
function reliefPartitionMesh(mesh,width){
  const geometry=mesh.geometry,position=geometry.getAttribute('position');
  const original=geometry.index?Array.from(geometry.index.array):Array.from({length:position.count},(_,i)=>i);
  const buckets=RELIEF_SECTION_IDS.map(()=>[]);
  for(let i=0;i<original.length;i+=3){
    const triangle=original.slice(i,i+3),x=triangle.reduce((sum,id)=>sum+position.getX(id),0)/3;
    buckets[x<-width/6?0:x>width/6?2:1].push(...triangle);
  }
  geometry.setIndex(buckets.flat());geometry.clearGroups();let start=0;
  for(let i=0;i<buckets.length;i++){geometry.addGroup(start,buckets[i].length,i);start+=buckets[i].length;}
  const material=mesh.material;
  mesh.material=RELIEF_SECTION_IDS.map((section,index)=>{
    const value=index===0?material:material.clone();value.name=mesh.name+' · '+section+' relief section';return value;
  });
  geometry.userData.reliefPartitions=buckets.map((indices,i)=>({id:RELIEF_SECTION_IDS[i],indices}));
}
const reliefOriginalMakePart=rigMakePart,reliefOriginalVisualSignature=rigVisualSignature;
rigMakePart=function(texture,cell,width,height,thickness,id){
  const part=reliefOriginalMakePart(texture,cell,width,height,thickness,id);
  part.userData.reliefBaseThickness=thickness;
  for(const mesh of part.children.filter(child=>child.userData.rigRestVertices))reliefPartitionMesh(mesh,width);
  return part;
};
rigVisualSignature=function(config,character){
  return reliefOriginalVisualSignature(config,character)+(character?JSON.stringify(reliefModel().characters[character]):'');
};
const reliefOriginalFaceSurface=rigFaceSurface;
rigFaceSurface=function(character,layout,headPart){
  const headGeometry=headPart.children[0].geometry,center=headGeometry.userData.rigPlaneCenter;
  const face=reliefOriginalFaceSurface(character,layout,headPart);
  // BufferGeometry.clone() shares userData. The cropped facial grid's centre
  // must not shift the head sampler that supplied its original triangles.
  face.mesh.geometry.userData={...face.mesh.geometry.userData};
  headGeometry.userData={...headGeometry.userData};
  if(center)headGeometry.userData.rigPlaneCenter=center.slice();else delete headGeometry.userData.rigPlaneCenter;
  return face;
};
function reliefSectionField(config,x,width){
  // Each saved section has a plateau and a continuous fold into its neighbour.
  // No disconnected slivers or duplicate atlas fragments cover the face.
  const t=THREE.MathUtils.clamp(x/Math.max(width,.01)+.5,0,1);
  const smooth=value=>value*value*(3-2*value);
  if(t<1/6)return config.left;
  if(t<.5)return THREE.MathUtils.lerp(config.left,config.center,smooth((t-1/6)*3));
  if(t<5/6)return THREE.MathUtils.lerp(config.center,config.right,smooth((t-.5)*3));
  return config.right;
}
function reliefMotionSample(character,id,time,flex){
  if(!flex)return 0;
  const lag=.18,earlier=Math.max(0,time-lag),elapsed=Math.max(time-earlier,.001);
  let speed=0,weight=1,part=id;
  while(part){
    const now=rigSample(character,part,time),before=rigSample(character,part,earlier);
    speed+=weight*((now.rotationZ-before.rotationZ)+.55*(now.rotationY-before.rotationY)+.3*(now.rotationX-before.rotationX))/elapsed;
    part=SOCKET_CONNECTIONS[part]?.[0];weight*=.6;
  }
  const now=storySample(character,time),before=storySample(character,earlier);
  speed+=((now.rotation-before.rotation)+.12*(now.x-before.x))/elapsed;
  // This evaluates saved curves at two explicit times. Seeking, replaying and
  // loading produce exactly the same cloth pose, with no simulation history.
  return THREE.MathUtils.clamp(speed,-2,2)*flex*.055;
}
const reliefOriginalPartRelief=rigPartRelief;
rigPartRelief=function(part,amount,pins){
  if(!part?.userData.reliefContext)return reliefOriginalPartRelief(part,amount,pins);
  const {config,motion}=part.userData.reliefContext,{width,height}=part.userData.rigSize;
  const signature=JSON.stringify([amount,pins,config,motion]);
  if(part.userData.reliefSignature===signature)return;
  part.userData.reliefSignature=signature;part.userData.rigRelief=amount;part.userData.rigReliefPins=pins;
  part.userData.reliefMotion=motion;part.userData.reliefThickness=config.thickness;
  const baseThickness=part.userData.reliefBaseThickness;
  for(const mesh of part.children.filter(child=>child.userData.rigRestVertices)){
    const attribute=mesh.geometry.getAttribute('position'),rest=mesh.userData.rigRestVertices;
    const front=mesh.name.endsWith('painted front'),back=mesh.name.endsWith('paper back');
    if(front)mesh.position.z=config.thickness/2;if(back)mesh.position.z=-config.thickness/2;
    for(let i=0;i<attribute.count;i++){
      const x=rest[i*3],y=rest[i*3+1],distance=Math.min(...pins.map(point=>Math.hypot(x-point.x,y-point.y)));
      const pinWeight=Math.min(1,distance/.22)**2;
      const section=reliefSectionField(config,x,width);
      const hem=THREE.MathUtils.clamp(.5-y/Math.max(height,.01),0,1);
      const side=THREE.MathUtils.clamp(2*x/Math.max(width,.01),-1,1);
      const secondary=motion*hem*hem*(.35+.65*side);
      attribute.setXYZ(i,x,y,rest[i*3+2]*config.thickness/baseThickness+(amount+section+secondary)*pinWeight);
    }
    attribute.needsUpdate=true;mesh.geometry.computeBoundingBox();mesh.geometry.computeBoundingSphere();
  }
};
const reliefOriginalAnimate=rigAnimateCharacter;
const reliefOriginalFaceRelief=rigFaceRelief;
rigFaceRelief=function(face,amount,pins,part){
  if(face.reliefSignature!==part.userData.reliefSignature){
    face.relief=NaN;face.reliefSignature=part.userData.reliefSignature;
  }
  const result=reliefOriginalFaceRelief(face,amount,pins,part);
  const front=part.children.find(mesh=>mesh.name?.endsWith('painted front'));
  face.mesh.position.z=front.position.z+.02;
  return result;
};
rigAnimateCharacter=function(group,character,time){
  const rig=group.userData.rig;if(!rig)return reliefOriginalAnimate(group,character,time);
  const configs=reliefModel().characters[character].parts;
  for(const [id,pivot] of Object.entries(rig.joints))if(pivot.userData.part){
    const config=configs[id];pivot.userData.part.userData.reliefContext={config,motion:reliefMotionSample(character,id,time,config.flex)};
  }
  // Facial geometry resamples only when the actual head surface changes.
  // Its exact indexed grid stays .02 above the skin without work at rest.
  const result=reliefOriginalAnimate(group,character,time);
  for(const part of rig.parts)if(part.userData.rigPart==='magic'){
    const config=configs.grimoire;part.userData.reliefContext={config,motion:reliefMotionSample(character,'grimoire',time,config.flex)};
    rigPartRelief(part,0,[{x:0,y:0,z:0}]);
  }
  return result;
};
function reliefBounds(points){
  if(!points.length)return null;
  const box=new THREE.Box3();for(const point of points)box.expandByPoint(point);
  return {min:box.min.toArray(),max:box.max.toArray(),depthSpan:box.max.z-box.min.z};
}
function reliefPartStatus(part,rig){
  const front=part.children.find(mesh=>mesh.name?.endsWith('painted front'));
  const back=part.children.find(mesh=>mesh.name?.endsWith('paper back'));
  const edge=part.children.find(mesh=>mesh.name?.endsWith('cut paper edge'));
  if(!part.userData.reliefInkSamples){
    const {width,height}=part.userData.rigSize,pixels=rig.texture.userData.rigPixels,groups=RELIEF_SECTION_IDS.map(()=>[]);
    for(let y=0;y<48;y++)for(let x=0;x<48;x++){
      const px=((x+.5)/48-.5)*width,py=(.5-(y+.5)/48)*height;
      const ink=rigPartInkSample(part,pixels,px,py);if(ink.alpha<200/255)continue;
      groups[px<-width/6?0:px>width/6?2:1].push({x:px,y:py,alpha:ink.alpha});
    }
    part.userData.reliefInkSamples=groups;
  }
  const sections=RELIEF_SECTION_IDS.map((id,index)=>{
    const indices=front.geometry.userData.reliefPartitions[index].indices,local=[],world=[];
    const attribute=front.geometry.getAttribute('position');
    for(const vertex of new Set(indices)){
      const point=new THREE.Vector3().fromBufferAttribute(attribute,vertex);point.z+=front.position.z;
      local.push(point);world.push(part.localToWorld(point.clone()));
    }
    const ink=part.userData.reliefInkSamples[index],samples=[];
    // Spread the diagnostic points across real opaque atlas ink, then sample
    // both actual indexed surfaces at the same XY. Configuration labels alone
    // never serve as proof that a rendered piece has physical paper thickness.
    for(let sample=0;sample<Math.min(12,ink.length);sample++){
      const point=ink[Math.floor(sample*ink.length/Math.min(12,ink.length))];
      const frontLocal=new THREE.Vector3(point.x,point.y,rigPlaneSurfaceZ(front,point.x,point.y));
      const backLocal=new THREE.Vector3(point.x,point.y,rigPlaneSurfaceZ(back,point.x,point.y));
      const frontWorld=part.localToWorld(frontLocal.clone()),backWorld=part.localToWorld(backLocal.clone());
      samples.push({alpha:point.alpha,frontLocal:frontLocal.toArray(),backLocal:backLocal.toArray(),
        frontWorld:frontWorld.toArray(),backWorld:backWorld.toArray(),thickness:frontLocal.z-backLocal.z,worldThickness:frontWorld.distanceTo(backWorld)});
    }
    return {id,configuredDepth:part.userData.reliefContext.config[id],triangleCount:indices.length/3,
      frontTriangles:indices.length/3,backTriangles:back.geometry.userData.reliefPartitions[index].indices.length/3,
      edgeTriangles:edge.geometry.userData.reliefPartitions[index].indices.length/3,
      localBounds:reliefBounds(local),worldBounds:reliefBounds(world),inkCount:ink.length,surfaceSamples:samples};
  });
  return {rendered:true,thickness:part.userData.reliefThickness,secondaryFlex:part.userData.reliefMotion,
    parented:true,sections,indexed:true,frontMesh:front.uuid,backMesh:back.uuid,edgeMesh:edge.uuid};
}
function reliefRenderStatus(character){
  if(!rigCharacterId(character))return null;
  const actor=animeCine?.cast?.[character==='kami'?'kami':'wisp']||storyBoundActor(character),rig=actor?.userData.rig;
  if(!rig)return {schema:RELIEF_SCHEMA,rigged:false,parts:{}};
  actor.updateWorldMatrix(true,true);
  const parts=Object.fromEntries(RIG_JOINT_IDS.map(id=>[id,rig.joints[id].userData.part?
    reliefPartStatus(rig.joints[id].userData.part,rig):{rendered:false,sections:RELIEF_SECTION_IDS.map(section=>({id:section,configuredDepth:reliefModel().characters[character].parts[id][section]}))}]));
  if(character==='swyrlz'){const magic=rig.parts.find(part=>part.userData.rigPart==='magic');if(magic)parts.magic=reliefPartStatus(magic,rig);}
  return {schema:RELIEF_SCHEMA,rigged:true,sectionCount:Object.values(parts).filter(part=>part.rendered).length*3,
    deterministic:true,socketPinned:true,parts};
}
const reliefOriginalRenderStatus=rigRenderStatus;
rigRenderStatus=function(character){
  const status=reliefOriginalRenderStatus(character);if(!status)return status;
  return {...status,depthSections:reliefRenderStatus(character)};
};
window.SWYRL_ENGINE_RIG=Object.freeze({...window.SWYRL_ENGINE_RIG,renderStatus:rigRenderStatus});
window.SWYRL_ENGINE_RELIEF=Object.freeze({...window.SWYRL_ENGINE_RELIEF,renderStatus:reliefRenderStatus});
