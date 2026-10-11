// A complete painted staff owns its silhouette from the flaming crown to the
// pointed foot. Its saved grip socket remains the origin of the articulated rig.
const RIG_FULL_STAFF_ASSET='assets/anime/kami-full-staff.png';
const RIG_FULL_STAFF_STYLE='painted-full-v1';
const RIG_FULL_STAFF_ANCHORS=Object.freeze({axisX:442,gripY:1030,shaftY:540,magicY:130,coreFootY:1600});
const RIG_FULL_STAFF_FRONT=.09;
function rigUsesFullStaff(config=rigModel().characters.kami){
  return rigUsesNaturalGrip('kami',config)&&config.staffArt===RIG_FULL_STAFF_STYLE;
}
const fullStaffOriginalCleanLayout=rigCleanPartLayout;
rigCleanPartLayout=function(character,part,value){
  const result=fullStaffOriginalCleanLayout(character,part,value);
  if(character==='kami'&&part==='staff')result.height=storyNumber(rigObject(value).height,result.height,.2,8);
  return result;
};
const fullStaffOriginalSanitize=rigSanitizeModel;
rigSanitizeModel=function(value,duration){
  const result=fullStaffOriginalSanitize(value,duration),input=rigObject(rigObject(value).characters).kami,
    staff=rigObject(rigObject(rigObject(input).layout).staff),fitted=['width','height'].every(field=>
      Object.hasOwn(staff,field)&&Number.isFinite(Number(staff[field]))&&Number(staff[field])>=.2);
  // An explicit full-art flag without its fitted card cannot safely inherit
  // the old wand dimensions. Keep that incomplete import on its atlas profile.
  result.characters.kami.staffArt=rigUsesNaturalGrip('kami',result.characters.kami)&&fitted&&rigObject(input).staffArt===RIG_FULL_STAFF_STYLE?RIG_FULL_STAFF_STYLE:'atlas';
  return result;
};
const fullStaffOriginalSignature=rigVisualSignature;
rigVisualSignature=function(config,character){return fullStaffOriginalSignature(config,character)+JSON.stringify([config.staffArt]);};
const fullStaffOriginalPublicModel=rigPublicModel;
rigPublicModel=function(character){
  const result=fullStaffOriginalPublicModel(character);if(!result)return result;
  return {...result,staffArt:rigModel().characters[character].staffArt||'atlas',
    layoutBoundsByPart:character==='kami'?{staff:{height:[.2,8]}}:{}};
};
const fullStaffOriginalFit=rigFitPart;
rigFitPart=function(character,part,value){
  if(character!=='kami'||part!=='staff')return fullStaffOriginalFit(character,part,value);
  if(!value||typeof value!=='object'||Array.isArray(value))return false;
  return rigMutate('Body piece fit · '+character+' · '+part,draft=>{
    const fit=draft.characters[character].layout[part];
    for(const [field,[low,high]] of Object.entries(RIG_LAYOUT_BOUNDS))
      if(Object.hasOwn(value,field))fit[field]=storyNumber(value[field],fit[field],low,field==='height'?8:high);
  },true);
};
function rigFullStaffCell(texture){
  if(texture.userData.fullStaffCell)return texture.userData.fullStaffCell;
  const image=texture.image;if(!image?.width)return null;
  const canvas=document.createElement('canvas');canvas.width=image.width;canvas.height=image.height;
  const context=canvas.getContext('2d',{willReadFrequently:true});context.drawImage(image,0,0);
  const pixels=context.getImageData(0,0,canvas.width,canvas.height).data;
  texture.userData.rigPixels=pixels;let x0=image.width,y0=image.height,x1=0,y1=0;
  for(let y=0;y<image.height;y++)for(let x=0;x<image.width;x++)if(pixels[(y*image.width+x)*4+3]>40){
    x0=Math.min(x0,x);y0=Math.min(y0,y);x1=Math.max(x1,x);y1=Math.max(y1,y);
  }
  if(x1<x0)return null;
  // Padding uses the measured outer pixel coordinates, matching the authored
  // crop. Very faint isolated export pixels do not enlarge the staff card.
  x0=Math.max(0,x0-2);y0=Math.max(0,y0-2);x1=Math.min(image.width,x1+2);y1=Math.min(image.height,y1+2);
  const size=96,mask=[];
  for(let y=0;y<size;y++)for(let x=0;x<size;x++){
    const px=Math.min(x1-1,Math.floor(x0+(x+.5)*(x1-x0)/size)),py=Math.min(y1-1,Math.floor(y0+(y+.5)*(y1-y0)/size));
    mask.push(pixels[(py*image.width+px)*4+3]>40);
  }
  return texture.userData.fullStaffCell={x0,y0,x1,y1,width:image.width,height:image.height,size,mask};
}
function rigFullStaffLocal(cell,width,height,pixelX,pixelY){
  return {x:((pixelX-cell.x0)/(cell.x1-cell.x0)-.5)*width,y:(.5-(pixelY-cell.y0)/(cell.y1-cell.y0))*height,z:0};
}
function rigFullStaffMetadata(){
  const texture=storyTexture(RIG_FULL_STAFF_ASSET),cell=rigFullStaffCell(texture);if(!cell)return null;
  const height=5.45,width=height*(cell.x1-cell.x0)/(cell.y1-cell.y0),a=RIG_FULL_STAFF_ANCHORS;
  return {asset:RIG_FULL_STAFF_ASSET,source:{width:cell.width,height:cell.height,crop:{x0:cell.x0,y0:cell.y0,x1:cell.x1,y1:cell.y1},anchors:{...a}},
    width,height,attach:rigFullStaffLocal(cell,width,height,a.axisX,a.gripY),
    shaft:rigFullStaffLocal(cell,width,height,a.axisX,a.shaftY),magic:rigFullStaffLocal(cell,width,height,a.axisX,a.magicY)};
}
const fullStaffOriginalMakePart=rigMakePart;
rigMakePart=function(texture,cell,width,height,thickness,id){
  const full=id==='staff'&&rigUsesFullStaff();
  if(full){texture=storyTexture(RIG_FULL_STAFF_ASSET);cell=rigFullStaffCell(texture);}
  const part=fullStaffOriginalMakePart(texture,cell,width,height,thickness,id);
  if(full){part.userData.rigTexture=texture;part.userData.fullStaff=true;part.userData.fullStaffReady=!!cell;
    for(const mesh of part.children)mesh.name='staff · '+(mesh.name.endsWith('painted front')?'painted front':mesh.name.endsWith('paper back')?'paper back':'cut paper edge');}
  return part;
};
function rigFullStaffSpan(texture,cell,width,pixelY,pixelX,threshold=235){
  const pixels=texture.userData.rigPixels,row=Math.max(0,Math.min(cell.height-1,Math.round(pixelY))),axis=Math.max(cell.x0,Math.min(cell.x1-1,Math.round(pixelX)));
  if(!pixels||pixels[(row*cell.width+axis)*4+3]<threshold)return {pixelY:row,minX:axis,maxX:axis,opaqueWidth:0,widthLocal:0};
  let minX=axis,maxX=axis;
  while(minX>cell.x0&&pixels[(row*cell.width+minX-1)*4+3]>=threshold)minX--;
  while(maxX<cell.x1-1&&pixels[(row*cell.width+maxX+1)*4+3]>=threshold)maxX++;
  return {pixelY:row,minX,maxX,opaqueWidth:maxX-minX+1,widthLocal:(maxX-minX+1)*width/(cell.x1-cell.x0)};
}
function rigFullStaffCoreMaterial(part,topPixel,bottomPixel){
  const canvas=document.createElement('canvas');canvas.width=128;canvas.height=1024;
  const context=canvas.getContext('2d'),texture=part.userData.rigTexture,cell=part.userData.rigCell,pixels=texture.userData.rigPixels;
  if(cell&&pixels){
    const image=context.createImageData(canvas.width,canvas.height),axis=RIG_FULL_STAFF_ANCHORS.axisX;
    for(let y=0;y<canvas.height;y++){
      const sourceY=Math.max(0,Math.min(cell.height-1,Math.round(topPixel+(bottomPixel-topPixel)*y/(canvas.height-1))));
      for(let x=0;x<canvas.width;x++){
        const sourceX=axis+Math.round(6*Math.sin(x/(canvas.width-1)*Math.PI*2)),source=(sourceY*cell.width+sourceX)*4,target=(y*canvas.width+x)*4;
        const shade=.72+.28*Math.abs(Math.cos(x/(canvas.width-1)*Math.PI*2));
        image.data[target]=pixels[source]*shade;image.data[target+1]=pixels[source+1]*shade;image.data[target+2]=pixels[source+2]*shade;image.data[target+3]=255;
      }
    }
    context.putImageData(image,0,0);
  }else{context.fillStyle='#5c3d2a';context.fillRect(0,0,canvas.width,canvas.height);}
  const map=new THREE.CanvasTexture(canvas);map.colorSpace=THREE.SRGBColorSpace;map.userData.rigOwnedTexture=true;
  return new THREE.MeshBasicMaterial({map,fog:false,toneMapped:false});
}
const fullStaffOriginalBuildShaft=rigBuildStaffShaft;
rigBuildStaffShaft=function(pivot,config){
  const result=fullStaffOriginalBuildShaft(pivot,config);if(!rigUsesFullStaff(config))return result;
  const shaft=pivot.userData.gripShaft,ferrule=pivot.userData.gripFerrule,part=pivot.userData.part,cell=part.userData.rigCell,
    socket=pivot.userData.rigSocketPart,attach=socket.attach,point=socket.sockets.shaft,{width,height}=part.userData.rigSize;
  for(const child of [...shaft.children]){child.removeFromParent();child.geometry?.dispose();
    const materials=Array.isArray(child.material)?child.material:[child.material];for(const material of materials){if(material?.map?.userData.rigOwnedTexture)material.map.dispose();material?.dispose();}}
  delete shaft.userData.rigStaffOrnament;
  const gripPixel=cell?{x:cell.x0+(attach.x/width+.5)*(cell.x1-cell.x0),y:cell.y0+(.5-attach.y/height)*(cell.y1-cell.y0)}:{x:442,y:1030},
    span=cell?rigFullStaffSpan(part.userData.rigTexture,cell,width,gripPixel.y,gripPixel.x):null,
    radius=Math.max(.05,Math.min(.075,(span?.widthLocal||.10)*.49));
  const coreFoot=cell?rigFullStaffLocal(cell,width,height,RIG_FULL_STAFF_ANCHORS.axisX,RIG_FULL_STAFF_ANCHORS.coreFootY):{y:-height/2},
    reach=Math.max(.04,attach.y-coreFoot.y),paintedReach=height/2+attach.y,
    mount=new THREE.Vector3(point.x-attach.x,point.y-attach.y,(point.z-attach.z)*config.depth),distance=mount.length(),
    axis=distance>.0001?mount.clone().divideScalar(distance):new THREE.Vector3(0,1,0),insert=.06,top=distance+insert,
    coreHeight=reach+top,centre=(top-reach)/2;
  shaft.geometry.dispose();if(shaft.material.map?.userData.rigOwnedTexture)shaft.material.map.dispose();shaft.material.dispose();
  shaft.geometry=new THREE.CylinderGeometry(radius,radius,coreHeight,24);shaft.material=rigFullStaffCoreMaterial(part,540,1600);
  shaft.position.copy(axis).multiplyScalar(centre);shaft.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0),axis);
  shaft.name='Kami · painted full-staff round core';
  shaft.userData.rigShaft={radius,height:coreHeight,gripY:-centre,mountY:distance-centre,lowerReach:reach,insert,axis:axis.toArray(),mount:mount.toArray()};
  shaft.userData.fullStaffCore={sourceGripSpan:span,paintedReach,coreFootPixel:RIG_FULL_STAFF_ANCHORS.coreFootY};
  // The painted tapered foot is backed by a restrained round taper, rather
  // than a flat cylinder end protruding through the point of the illustration.
  if(cell&&paintedReach>reach){
    const profile=[];
    for(const row of [1600,1640,1680,1720,1740,1762]){
      const local=rigFullStaffLocal(cell,width,height,RIG_FULL_STAFF_ANCHORS.axisX,row),rowSpan=rigFullStaffSpan(part.userData.rigTexture,cell,width,row,RIG_FULL_STAFF_ANCHORS.axisX,40),
        r=Math.min(radius,Math.max(0,rowSpan.widthLocal*.44));profile.push(new THREE.Vector2(r,local.y-attach.y-centre));
    }
    profile.push(new THREE.Vector2(0,-paintedReach-centre));profile.reverse();
    const foot=new THREE.Mesh(new THREE.LatheGeometry(profile,24),rigFullStaffCoreMaterial(part,1600,1762));
    foot.name='Kami · painted pointed staff foot core';shaft.add(foot);shaft.userData.fullStaffFoot=foot;
  }
  ferrule.geometry.dispose();if(ferrule.material.map?.userData.rigOwnedTexture)ferrule.material.map.dispose();ferrule.material.dispose();
  ferrule.geometry=new THREE.CylinderGeometry(.018,.018,.035,24);ferrule.material=new THREE.MeshBasicMaterial({color:'#76502e',fog:false,toneMapped:false});
  ferrule.position.copy(mount);ferrule.position.z-=.045;ferrule.quaternion.copy(shaft.quaternion);
  ferrule.name='Kami · internal full-staff neck support';return result;
};
const fullStaffOriginalPartRelief=rigPartRelief;
rigPartRelief=function(part,amount,pins){
  const result=fullStaffOriginalPartRelief(part,amount,pins);if(!part?.userData.fullStaff)return result;
  const thickness=part.userData.reliefThickness||part.userData.reliefBaseThickness,cell=part.userData.rigCell,
    front=part.children.find(mesh=>mesh.name.endsWith('painted front')),
    neck=cell?rigFullStaffLocal(cell,part.userData.rigSize.width,part.userData.rigSize.height,442,540).y:part.userData.rigSize.height/2,
    mountY=part.parent?.userData.rigSocketPart?.sockets.shaft?.y??neck,
    // Surface sampling interpolates adjacent grid rows. Pin the first row
    // above the real neck as well, so maximum relief cannot lift the joining
    // ink away from the cylinder through the triangle containing the mount.
    pinLimit=Math.max(neck,mountY)+part.userData.rigSize.height/(front.geometry.parameters.heightSegments||1);
  for(const mesh of part.children.filter(child=>child.userData.rigRestVertices)){
    const front=mesh.name.endsWith('painted front'),back=mesh.name.endsWith('paper back');
    mesh.position.z=front?RIG_FULL_STAFF_FRONT:back?RIG_FULL_STAFF_FRONT-thickness:RIG_FULL_STAFF_FRONT-thickness/2;
    const positions=mesh.geometry.getAttribute('position'),rest=mesh.userData.rigRestVertices;
    for(let i=0;i<positions.count;i++)if(rest[i*3+1]<=pinLimit)
      positions.setZ(i,rest[i*3+2]*thickness/part.userData.reliefBaseThickness);
    positions.needsUpdate=true;mesh.geometry.computeBoundingBox();mesh.geometry.computeBoundingSphere();
  }
  return result;
};
const fullStaffOriginalBuildVisual=rigBuildVisual;
rigBuildVisual=function(visual,character){
  const group=fullStaffOriginalBuildVisual(visual,character);
  if(character==='kami'&&rigUsesFullStaff())group.userData.rig.cellsReady=group.userData.rig.cellsReady&&!!group.userData.rig.joints.staff.userData.part.userData.fullStaffReady;
  return group;
};
const fullStaffOriginalTextureLoaded=rigTextureLoaded;
rigTextureLoaded=function(texture,source){const result=fullStaffOriginalTextureLoaded(texture,source);
  if(source===RIG_FULL_STAFF_ASSET&&currentProject?.animeRigs){if(rigUsesFullStaff())rigRefreshStage();rigFullStaffEditorSync();}return result;};
const fullStaffOriginalMagicFrame=staffMagicFrame;
staffMagicFrame=function(c,time){
  const result=fullStaffOriginalMagicFrame(c,time),pivot=c.cast.kami?.userData.rig?.joints.staff;
  if(c.staffMagic&&pivot&&rigUsesFullStaff()){
    const part=pivot.userData.part,point=pivot.userData.rigSocketPart.sockets.magic;
    part.localToWorld(c.staffMagic.anchor.set(point.x,point.y,RIG_FULL_STAFF_FRONT+.03));c.staffMagic.group.position.copy(c.staffMagic.anchor);
  }
  return result;
};
function rigFullStaffPixelSample(part,x,y){
  const texture=part.userData.rigTexture,cell=part.userData.rigCell,pixels=texture.userData.rigPixels;
  x=Math.max(0,Math.min(cell.width-1,Math.round(x)));y=Math.max(0,Math.min(cell.height-1,Math.round(y)));
  const index=(y*cell.width+x)*4,{width,height}=part.userData.rigSize,point=rigFullStaffLocal(cell,width,height,x+.5,y+.5),front=part.children.find(mesh=>mesh.name.endsWith('painted front'));
  const local=new THREE.Vector3(point.x,point.y,rigPlaneSurfaceZ(front,point.x,point.y)),world=part.localToWorld(local.clone());
  return {pixel:[x,y],rgb:Array.from(pixels.slice(index,index+3)),alpha:pixels[index+3]/255,local:local.toArray(),world:world.toArray(),screen:rigProjectedWorld(world)};
}
function rigFullStaffStatus(pivot){
  const part=pivot?.userData.part;if(!part?.userData.fullStaff)return null;
  const cell=part.userData.rigCell,shaft=pivot.userData.gripShaft;
  if(!cell)return {style:RIG_FULL_STAFF_STYLE,asset:RIG_FULL_STAFF_ASSET,ready:false};
  const front=part.children.find(mesh=>mesh.name.endsWith('painted front')),back=part.children.find(mesh=>mesh.name.endsWith('paper back')),
    edge=part.children.find(mesh=>mesh.name.endsWith('cut paper edge')),positions=front.geometry.getAttribute('position'),vertices=[];
  for(let i=0;i<positions.count;i+=3){const local=new THREE.Vector3().fromBufferAttribute(positions,i);local.z+=front.position.z;
    vertices.push({local:local.toArray(),world:part.localToWorld(local.clone()).toArray()});}
  const regions=[['crest',190],['neck',540],['upperPole',750],['gripContact',1030],['lowerPole',1300],['shoe',1660]].map(([id,y])=>({id,
    samples:[-16,0,16].flatMap(dy=>[-12,-6,0,6,12].map(dx=>rigFullStaffPixelSample(part,442+dx,y+dy)))
      .filter(sample=>sample.alpha>.9)})),spine=[];
  for(let y=130;y<=1745;y+=32)spine.push(rigFullStaffPixelSample(part,442,y));
  const data=shaft.userData.rigShaft,core=shaft.userData.fullStaffCore,attach=pivot.userData.rigSocketPart.attach,
    atGrip=rigSurfacePoint(part,attach.x,attach.y),gripInPivot=part.position.clone().add(atGrip),
    actualCoreFront=shaft.localToWorld(new THREE.Vector3(0,data.gripY,data.radius)),paintedFront=part.localToWorld(atGrip.clone()),
    foot=shaft.userData.fullStaffFoot,footVertices=[];
  if(foot){const attribute=foot.geometry.getAttribute('position');for(let i=0;i<attribute.count;i++){
    const world=foot.localToWorld(new THREE.Vector3().fromBufferAttribute(attribute,i));
    footVertices.push({local:shaft.worldToLocal(world.clone()).toArray(),world:world.toArray()});}}
  return {style:RIG_FULL_STAFF_STYLE,asset:RIG_FULL_STAFF_ASSET,ready:!!part.userData.fullStaffReady,
    source:{width:cell.width,height:cell.height,crop:{x0:cell.x0,y0:cell.y0,x1:cell.x1,y1:cell.y1},anchors:{...RIG_FULL_STAFF_ANCHORS}},
    card:{partUUID:part.uuid,frontMesh:front.uuid,backMesh:back.uuid,edgeMesh:edge.uuid,width:part.userData.rigSize.width,height:part.userData.rigSize.height,
      matrixWorld:part.matrixWorld.toArray(),frontBaseZ:front.position.z,vertices},
    core:{meshUUID:shaft.uuid,radius:data.radius,radialSegments:shaft.geometry.parameters.radialSegments,height:data.height,lowerReach:data.lowerReach,insert:data.insert,
      matrixWorld:shaft.matrixWorld.toArray(),endpointsLocal:[[0,-data.height/2,0],[0,data.height/2,0]],
      endpointsWorld:[shaft.localToWorld(new THREE.Vector3(0,-data.height/2,0)).toArray(),shaft.localToWorld(new THREE.Vector3(0,data.height/2,0)).toArray()],
      gripLocal:[0,data.gripY,0],sourceGripSpan:core.sourceGripSpan,paintedFootReach:core.paintedReach,footMesh:foot?.uuid||null,
      foot:foot?{meshUUID:foot.uuid,matrixWorld:foot.matrixWorld.toArray(),geometryType:foot.geometry.type,vertices:footVertices}:null},
    socketAnchors:storyCopy(pivot.userData.rigSocketPart),regions,spine,
    poleFrontClearance:gripInPivot.z-pivot.worldToLocal(actualCoreFront.clone()).z,
    paintedGripFrontWorld:paintedFront.toArray(),coreGripFrontWorld:actualCoreFront.toArray()};
}
const fullStaffOriginalGripStatus=rigStaffGripStatus;
rigStaffGripStatus=function(actor,rig){const status=fullStaffOriginalGripStatus(actor,rig);
  return status?{...status,fullStaff:rigFullStaffStatus(rig.joints.staff)}:status;};
function rigApplyFullStaff(reset=false){
  if(!storyEditable()||!currentProject||!rigUsesNaturalGrip('kami',rigModel().characters.kami))return false;
  const meta=rigFullStaffMetadata();if(!meta)return false;
  const rigs=storyCopy(rigModel()),sockets=storyCopy(socketModel()),cfg=rigs.characters.kami;
  cfg.staffArt=RIG_FULL_STAFF_STYLE;
  if(reset===true){
    const previous=cfg.layout.staff,defaults=rigDefaultPartLayout('kami','staff'),connection=sockets.characters.kami.connections.staff;
    if(connection.connected){const grip=sockets.characters.kami.parts[connection.parent].sockets[connection.socket];
      grip.x+=defaults.x-previous.x;grip.y+=defaults.y-previous.y;}
    cfg.layout.staff=defaults;
  }
  Object.assign(cfg.layout.staff,{width:meta.width,height:meta.height,artX:-meta.attach.x,artY:-meta.attach.y});
  sockets.characters.kami.parts.staff={attach:meta.attach,sockets:{shaft:meta.shaft,magic:meta.magic}};
  const next=rigSanitizeModel(rigs);if(JSON.stringify(next)===JSON.stringify(rigModel())&&JSON.stringify(sockets)===JSON.stringify(socketModel()))return true;
  const label=reset===true?'Reset body piece fit · kami · staff':'Use full-length staff';
  beginTransaction(label);currentProject.animeRigs=next;rigValidatedProject=currentProject;rigValidatedModel=next;
  currentProject.animeSockets=socketSanitizeModel(sockets);socketValidatedProject=currentProject;socketValidatedModel=currentProject.animeSockets;
  rigRefreshNativeActors();commitTransaction(label);rigNotify();socketNotify();return true;
}
const fullStaffOriginalResetFit=rigResetPartFit;
rigResetPartFit=function(character,part){
  return character==='kami'&&part==='staff'&&rigUsesFullStaff()?rigApplyFullStaff(true):fullStaffOriginalResetFit(character,part);
};
function rigFullStaffEditorSync(){
  const character=rigEditorCharacter(),section=document.getElementById('rigFitSection');if(!section)return;
  let button=document.getElementById('rigUseFullStaff');if(!button){button=document.createElement('button');button.id='rigUseFullStaff';button.type='button';button.textContent='Use full-length staff';
    button.dataset.rigEditable='true';button.addEventListener('click',()=>{if(rigApplyFullStaff())rigEditorNotice('Full-length staff fitted to Kami’s grip.');else rigEditorNotice('The staff artwork is still loading.',true);});section.append(button);}
  button.hidden=character!=='kami'||!rigUsesNaturalGrip('kami',rigModel().characters.kami);
  // Preparing the panel loads the asset before the first click. The load
  // callback enables the button only after its measured crop is available.
  const metadata=button.hidden?null:rigFullStaffMetadata();button.disabled=!rigEditorEditable()||!metadata;
  if(character==='kami'&&rigEditorParts.kami==='staff'){
    const input=document.getElementById('rigFitHeight');if(input){input.max='8';input.value=rigEditorNumber(rigModel().characters.kami.layout.staff.height);}
  }
}
const fullStaffOriginalEditorSync=rigEditorSync;
rigEditorSync=function(){const result=fullStaffOriginalEditorSync();rigFullStaffEditorSync();return result;};
window.SWYRL_ENGINE_RIG=Object.freeze({...window.SWYRL_ENGINE_RIG,model:rigPublicModel,fitPart:rigFitPart,resetPartFit:rigResetPartFit});
window.SWYRL_ENGINE_STAFF=Object.freeze({applyFullStaff:rigApplyFullStaff,metadata:rigFullStaffMetadata});
rigFullStaffEditorSync();
