// Close-fitting metalwork belongs to the socketed pole, so every detail follows
// the hand, the popup hinge and the authored staff pose without a second rig.
// Original and custom-atlas profiles retain their original wooden pole.
const RIG_STAFF_ORNAMENT_STYLE='ebony-inlay-v1';
const RIG_STAFF_GRIP_EXCLUSION=.30;
function rigStaffFinishTexture(kind,shaftData){
  const canvas=document.createElement('canvas');canvas.width=512;canvas.height=kind==='ebony'?1024:128;
  const context=canvas.getContext('2d',{willReadFrequently:true}),width=canvas.width,height=canvas.height;
  const shade=context.createLinearGradient(0,0,width,0);
  const stops=kind==='ebony'?[[0,'#a07847'],[.10,'#735032'],[.24,'#35261e'],[.42,'#211b17'],
    [.56,'#45301f'],[.72,'#a97a42'],[.82,'#735132'],[1,'#a07847']]:
    [[0,'#edc582'],[.09,'#c4934c'],[.24,'#78512b'],[.39,'#9b713a'],[.55,'#e8b96d'],
      [.66,'#f8dca1'],[.79,'#b7823e'],[.91,'#b88948'],[1,'#edc582']];
  for(const [at,color] of stops)shade.addColorStop(at,color);
  context.fillStyle=shade;context.fillRect(0,0,width,height);
  if(kind==='ebony'){
    // Long quiet grain retains the painted illustration's warm directional
    // shading. A few broad gold lines remain readable at the full-stage scale.
    context.strokeStyle='rgba(230,179,102,.17)';context.lineWidth=1.8;
    for(let x=7;x<width;x+=29){
      context.beginPath();for(let y=0;y<=height;y+=12){const px=x+2.5*Math.sin(y*.018+x*.07);
        if(y)context.lineTo(px,y);else context.moveTo(px,y);}context.stroke();
    }
    const yForPole=position=>height*(.5-(shaftData.gripY+position)/shaftData.height);
    // A resized crest/socket can shorten the exposed upper pole. Keep the
    // entire .36-long scroll inside its endpoints and outside the bare grip.
    const upperEnd=shaftData.height/2-shaftData.gripY,upperInlay=Math.min(.71,upperEnd-.19),
      exclusion=shaftData.gripExclusion||RIG_STAFF_GRIP_EXCLUSION,inlays=[];
    if(upperInlay-.18>=exclusion+.01)inlays.push(upperInlay);
    if(1.12-.18>=exclusion+.01)inlays.push(-1.12);
    // Wrap the inlay over the UV seam on the camera-facing side of the pole.
    for(const pole of inlays)for(const x of [0,width/2,width]){
      const y=yForPole(pole),ry=height*.10/shaftData.height;
      context.strokeStyle='#ddb06a';context.lineWidth=4;context.beginPath();
      context.moveTo(x,y-ry);context.lineTo(x+13,y);context.lineTo(x,y+ry);
      context.lineTo(x-13,y);context.closePath();context.stroke();
      context.strokeStyle='rgba(197,147,75,.9)';context.lineWidth=2.3;
      context.beginPath();context.moveTo(x,y-ry*1.8);context.bezierCurveTo(x+21,y-ry*1.45,x+20,y-ry*.9,x,y-ry*.65);
      context.moveTo(x,y+ry*1.8);context.bezierCurveTo(x-21,y+ry*1.45,x-20,y+ry*.9,x,y+ry*.65);context.stroke();
    }
  }else{
    const age=context.createLinearGradient(0,0,0,height);
    age.addColorStop(0,'rgba(57,35,18,.43)');age.addColorStop(.18,'rgba(57,35,18,0)');
    age.addColorStop(.75,'rgba(57,35,18,0)');age.addColorStop(1,'rgba(57,35,18,.40)');
    context.fillStyle=age;context.fillRect(0,0,width,height);
    context.strokeStyle='rgba(255,233,178,.35)';context.lineWidth=2;
    context.beginPath();context.moveTo(0,height*.25);context.lineTo(width,height*.25);context.stroke();
  }
  const texture=new THREE.CanvasTexture(canvas);texture.colorSpace=THREE.SRGBColorSpace;
  texture.userData.rigOwnedTexture=true;
  texture.userData.rigStaffFinishPixels=context.getImageData(0,0,width,height).data;
  return texture;
}
function rigStaffFinishMaterial(kind,data){
  return new THREE.MeshBasicMaterial({map:rigStaffFinishTexture(kind,data),fog:false,toneMapped:false});
}
function rigStaffLathe(profile){
  return new THREE.LatheGeometry(profile.map(([radius,y])=>new THREE.Vector2(radius,y)),24);
}
const rigOrnamentOriginalBuildShaft=rigBuildStaffShaft;
rigBuildStaffShaft=function(pivot,config){
  const result=rigOrnamentOriginalBuildShaft(pivot,config);
  if(!rigUsesNaturalGrip('kami',config))return result;
  const shaft=pivot.userData.gripShaft,data=shaft.userData.rigShaft,ferrule=pivot.userData.gripFerrule;
  const handGrip=socketModel().characters.kami.parts.leftHand.sockets.grip;
  data.gripExclusion=Math.max(RIG_STAFF_GRIP_EXCLUSION,config.layout.leftHand.height/2+Math.abs(handGrip.y));
  if(shaft.material.map?.userData.rigOwnedTexture)shaft.material.map.dispose();shaft.material.dispose();
  shaft.material=rigStaffFinishMaterial('ebony',data);shaft.name='Kami · engraved ebony staff shaft';
  const parts=[];
  function add(id,name,profile,poleY){
    const mesh=new THREE.Mesh(rigStaffLathe(profile),rigStaffFinishMaterial('gold',data));
    mesh.name='Kami · '+name;mesh.position.y=data.gripY+poleY;shaft.add(mesh);parts.push({id,mesh});return mesh;
  }
  const ring=[[.055,-.035],[.060,-.035],[.065,-.025],[.068,-.006],
    [.068,.006],[.065,.025],[.060,.035],[.055,.035]];
  const upperEnd=data.height/2-data.gripY,upperLimit=upperEnd-.035,lowerLimit=data.gripExclusion+.04,
    upperBands=[];
  if(upperLimit>=lowerLimit){
    let first=Math.max(lowerLimit,Math.min(.50,upperLimit)),second=Math.min(.92,upperLimit);
    if(second-first<.14&&second-lowerLimit>=.14)first=second-.14;
    upperBands.push(first);if(second-first>=.14-1e-8)upperBands.push(second);
  }
  const bandPositions=[...upperBands,...[-.62,-1.62].filter(poleY=>Math.abs(poleY)>=lowerLimit)];
  for(const [index,poleY] of bandPositions.entries())add('ring-'+(index+1),'antique-gold staff band '+(index+1),ring,poleY);
  // This rounded shoe sits within the original pole endpoints; it adds no
  // reach into the book and leaves the lower silhouette continuous.
  if(data.lowerReach-.16>data.gripExclusion)add('butt-cap','tapered gold staff shoe',[[0,-.08],[.045,-.08],[.059,-.062],
    [.064,-.04],[.062,.015],[.057,.065],[.055,.08]],-data.lowerReach+.08);
  ferrule.geometry.dispose();if(ferrule.material.map?.userData.rigOwnedTexture)ferrule.material.map.dispose();ferrule.material.dispose();
  // Retain the ferrule's original transform and maximum radius. Its rounded
  // sleeve stays behind the painted stem rather than becoming a square collar.
  ferrule.geometry=rigStaffLathe([[0,-.08],[.057,-.08],[.059,-.06],[.061,-.025],
    [.0625,.015],[.0638,.05],[.061,.08],[0,.08]]);
  ferrule.material=rigStaffFinishMaterial('gold',data);ferrule.name='Kami · tapered antique-gold crest sleeve';
  parts.push({id:'neck',mesh:ferrule});
  shaft.userData.rigStaffOrnament={style:RIG_STAFF_ORNAMENT_STYLE,parts};
  return result;
};
function rigStaffMaterialStatus(material){
  const map=material.map,image=map?.image;
  return {type:material.type,mapType:map?.type||null,mapIsCanvas:!!image?.getContext,width:image?.width||0,height:image?.height||0};
}
function rigStaffMapSample(mesh,uv){
  const material=mesh.material,map=material.map,image=map?.image;
  if(!image?.width||!uv)return {uv:null,mapRGB:null,rgb:null,alpha:null};
  const mapped=uv.clone();map.updateMatrix();map.transformUv(mapped);
  const x=Math.max(0,Math.min(image.width-1,Math.floor(mapped.x*image.width))),
    y=Math.max(0,Math.min(image.height-1,Math.floor(mapped.y*image.height)));
  const pixels=map.userData.rigStaffFinishPixels||image.getContext('2d',{willReadFrequently:true}).getImageData(0,0,image.width,image.height).data;
  const index=(y*image.width+x)*4,mapRGB=Array.from(pixels.slice(index,index+3));
  return {uv:uv.toArray(),mapUV:mapped.toArray(),mapPixel:[x,y],mapRGB,rgb:mapRGB,alpha:pixels[index+3]/255};
}
function rigStaffMeshSample(mesh,target,shaft,camera){
  const world=mesh.localToWorld(target.clone()),ray=new THREE.Raycaster(camera,world.clone().sub(camera).normalize());
  const intersection=ray.intersectObject(mesh,false)[0];if(!intersection)return null;
  return {meshUUID:mesh.uuid,local:shaft.worldToLocal(intersection.point.clone()).toArray(),world:intersection.point.toArray(),
    screen:rigProjectedWorld(intersection.point),...rigStaffMapSample(mesh,intersection.uv)};
}
function rigStaffOrnamentStatus(shaft){
  const ornament=shaft?.userData.rigStaffOrnament;if(!ornament)return null;
  shaft.updateWorldMatrix(true,true);
  const camera=perspectiveCamera.getWorldPosition(new THREE.Vector3()),data=shaft.userData.rigShaft,
    inverse=new THREE.Matrix4().copy(shaft.matrixWorld).invert();
  let gripZoneClearance=Infinity,endpointClearance=Infinity;
  const parts=ornament.parts.map(({id,mesh})=>{
    mesh.updateWorldMatrix(true,false);
    const positions=mesh.geometry.getAttribute('position'),matrix=new THREE.Matrix4().copy(inverse).multiply(mesh.matrixWorld),
      localBox=new THREE.Box3(),worldBox=new THREE.Box3(),vertices=[],seen=new Set();
    let minRadius=Infinity,maxRadius=0,shaftMinRadius=Infinity,shaftMaxRadius=0,minNativeY=Infinity,maxNativeY=-Infinity;
    for(let i=0;i<positions.count;i++){
      const native=new THREE.Vector3().fromBufferAttribute(positions,i),local=native.clone().applyMatrix4(matrix),world=local.clone().applyMatrix4(shaft.matrixWorld);
      localBox.expandByPoint(local);worldBox.expandByPoint(world);
      minRadius=Math.min(minRadius,Math.hypot(native.x,native.z));maxRadius=Math.max(maxRadius,Math.hypot(native.x,native.z));
      shaftMinRadius=Math.min(shaftMinRadius,Math.hypot(local.x,local.z));shaftMaxRadius=Math.max(shaftMaxRadius,Math.hypot(local.x,local.z));
      minNativeY=Math.min(minNativeY,native.y);maxNativeY=Math.max(maxNativeY,native.y);
      const key=native.toArray().map(value=>value.toFixed(7)).join(',');
      if(!seen.has(key)){seen.add(key);vertices.push({local:local.toArray(),world:world.toArray()});}
      const poleY=local.y-data.gripY;gripZoneClearance=Math.min(gripZoneClearance,Math.abs(poleY)-data.gripExclusion);
      if(id==='butt-cap')endpointClearance=Math.min(endpointClearance,local.y+data.height/2,data.height/2-local.y);
    }
    const screenSamples=[.30,.50,.70].map(fraction=>rigStaffMeshSample(mesh,
      new THREE.Vector3(0,minNativeY+(maxNativeY-minNativeY)*fraction,0),shaft,camera)).filter(Boolean);
    return {id,meshUUID:mesh.uuid,geometryType:mesh.geometry.type,vertexCount:positions.count,radialSegments:mesh.geometry.parameters.segments,
      material:rigStaffMaterialStatus(mesh.material),matrixWorld:mesh.matrixWorld.toArray(),
      boundsLocal:{min:localBox.min.toArray(),max:localBox.max.toArray()},boundsWorld:{min:worldBox.min.toArray(),max:worldBox.max.toArray()},
      radialRange:[minRadius,maxRadius],shaftRadialRange:[shaftMinRadius,shaftMaxRadius],
      axialRange:[localBox.min.y,localBox.max.y],poleAxialRange:[localBox.min.y-data.gripY,localBox.max.y-data.gripY],vertices,screenSamples};
  });
  // Rays along only the axis see one narrow texture column. Sample either
  // side of the real visible cylinder as well as the engraved diamond tips,
  // so the witnesses cover its curved directional shading and painted inlay.
  const cameraLocal=shaft.worldToLocal(camera.clone()),tangent=new THREE.Vector3(cameraLocal.z,0,-cameraLocal.x);
  if(tangent.lengthSq()<1e-12)tangent.set(1,0,0);else tangent.normalize();
  const coreTargets=[-.40,-.50,-.85,-.97,-1.10,-1.22,-1.38,-1.85,-2.03,.36,.68,1.02].map(pole=>[pole,0]);
  for(const pole of [-.85,-1.10,-1.38,.36,.68,1.02])for(const lateral of [-.040,.040])coreTargets.push([pole,lateral]);
  const upperEnd=data.height/2-data.gripY,upperInlay=Math.min(.71,upperEnd-.19);
  if(upperInlay-.18>=data.gripExclusion+.01)coreTargets.push([upperInlay-.10,0],[upperInlay+.10,0]);
  if(1.12-.18>=data.gripExclusion+.01)coreTargets.push([-1.22,0],[-1.02,0]);
  const coreSamples=coreTargets.filter(([pole])=>Math.abs(pole)>data.gripExclusion+.01).map(([pole,lateral])=>rigStaffMeshSample(shaft,
    tangent.clone().multiplyScalar(lateral).setY(data.gripY+pole),shaft,camera)).filter(Boolean);
  return {style:ornament.style,shaftMesh:shaft.uuid,shaftMatrixWorld:shaft.matrixWorld.toArray(),cameraWorld:camera.toArray(),
    coreMaterial:rigStaffMaterialStatus(shaft.material),gripExclusionHalfLength:data.gripExclusion,gripZoneClearance,
    shaftEndpoints:[-data.height/2,data.height/2],endpointClearance:Number.isFinite(endpointClearance)?endpointClearance:null,parts,coreSamples};
}
const rigOrnamentOriginalGripStatus=rigStaffGripStatus;
rigStaffGripStatus=function(actor,rig){
  const status=rigOrnamentOriginalGripStatus(actor,rig);
  return status?{...status,ornament:rigStaffOrnamentStatus(rig.joints.staff.userData.gripShaft)}:status;
};
