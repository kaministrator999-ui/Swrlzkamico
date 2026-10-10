// The original glove atlas remains intact. Its bundled Kami profile uses two
// aligned painted layers so the cylindrical staff passes through a real grip.
const RIG_NATURAL_GRIP_ASSET='assets/anime/kami-grip-layers.png';
function rigUsesNaturalGrip(character,config){
  return character==='kami'&&config.gripStyle==='natural-v1'&&config.asset==='assets/anime/kami-rig.png';
}
function rigGripCells(texture){
  if(texture.userData.gripCells)return texture.userData.gripCells;
  const image=texture.image;if(!image?.width)return null;
  const canvas=document.createElement('canvas');canvas.width=image.width;canvas.height=image.height;
  const context=canvas.getContext('2d',{willReadFrequently:true});context.drawImage(image,0,0);
  const pixels=context.getImageData(0,0,canvas.width,canvas.height).data;texture.userData.rigPixels=pixels;
  // The generated layers use separate UV rectangles with the same dimensions.
  // Their shared coordinates align the cuff, knuckles and opposed thumb.
  const scaleX=image.width/1774,scaleY=image.height/887,size=48;
  const cells=[[253,180,765,730],[1003,180,1515,730]].map(rect=>{
    const [x0,y0,x1,y1]=rect.map((v,i)=>Math.round(v*(i%2?scaleY:scaleX))),mask=[];
    for(let y=0;y<size;y++)for(let x=0;x<size;x++){
      const px=Math.min(x1-1,Math.floor(x0+(x+.5)*(x1-x0)/size));
      const py=Math.min(y1-1,Math.floor(y0+(y+.5)*(y1-y0)/size));
      mask.push(pixels[(py*image.width+px)*4+3]>40);
    }
    return {x0,y0,x1,y1,width:image.width,height:image.height,mask,size};
  });
  texture.userData.gripCells=cells;return cells;
}
function rigMakeNaturalGrip(texture,width,height,thickness){
  const cells=rigGripCells(texture),palm=rigMakePart(texture,cells?.[0],width,height,thickness,'leftHand');
  const fingers=rigMakePart(texture,cells?.[1],width,height,thickness,'leftHand');
  palm.userData.rigTexture=texture;palm.userData.rigGripLayer='palm';
  fingers.userData.rigTexture=texture;fingers.userData.rigGripLayer='fingers';
  const layers={palm:{userData:{rigCell:palm.userData.rigCell,rigSize:{width,height},rigTexture:texture}},fingers};
  for(const [id,layer] of Object.entries({palm,fingers}))for(const mesh of [...layer.children]){
    mesh.name='leftHand · '+(id==='palm'?'rear palm':'curled fingers and thumb')+' · '+
      (mesh.name.endsWith('painted front')?'painted front':mesh.name.endsWith('paper back')?'paper back':'cut paper edge');
    mesh.userData.rigGripLayer=id;mesh.userData.rigLayerOffset=id==='palm'?-.15:.15;
    if(id==='fingers')palm.add(mesh);
  }
  // The layer containers share one socket-bearing part and one depth profile.
  // Their actual grids and alpha masks are retained for painted-point sampling.
  palm.userData.rigGripLayers=layers;
  layers.fingers.userData.frontMesh=palm.children.find(mesh=>mesh.userData.rigGripLayer==='fingers'&&mesh.name.endsWith('painted front'));
  layers.palm.userData.frontMesh=palm.children.find(mesh=>mesh.userData.rigGripLayer==='palm'&&mesh.name.endsWith('painted front'));
  return palm;
}
const rigNaturalOriginalSurfacePoint=rigSurfacePoint;
rigSurfacePoint=function(part,x,y){
  const fingers=part?.userData.rigGripLayers?.fingers;
  if(fingers?.userData.frontMesh&&rigPartInkSample(fingers,null,x,y).alpha>.4)
    return new THREE.Vector3(x,y,rigPlaneSurfaceZ(fingers.userData.frontMesh,x,y));
  return rigNaturalOriginalSurfacePoint(part,x,y);
};
const rigNaturalOriginalPartRelief=rigPartRelief;
rigPartRelief=function(part,amount,pins){
  const result=rigNaturalOriginalPartRelief(part,amount,pins);
  if(part?.userData.rigGripLayers){
    const thickness=part.userData.reliefThickness||part.userData.reliefBaseThickness;
    for(const mesh of part.children.filter(value=>value.userData.rigGripLayer))
      mesh.position.z=mesh.userData.rigLayerOffset+(mesh.name.endsWith('painted front')?thickness/2:mesh.name.endsWith('paper back')?-thickness/2:0);
  }
  return result;
};
function rigGripLayerSamples(hand,id,point,shaft,camera){
  const layer=hand.userData.rigGripLayers?.[id];if(!layer)return [];
  const cell=layer.userData.rigCell,pixels=layer.userData.rigTexture.userData.rigPixels,mesh=layer.userData.frontMesh;
  if(!cell||!pixels)return [];
  const {width,height}=hand.userData.rigSize,{radius,gripY}=shaft.userData.rigShaft;
  const grip=shaft.localToWorld(new THREE.Vector3(0,gripY,0)),axis=new THREE.Vector3(0,1,0).transformDirection(shaft.matrixWorld);
  const samples=[];
  for(let y=0;y<48;y++)for(let x=0;x<48;x++){
    const px=((x+.5)/48-.5)*width,py=(.5-(y+.5)/48)*height;
    if(Math.abs(px-point.x)>.065||Math.abs(py-point.y)>.19)continue;
    const ink=rigPartInkSample(layer,pixels,px,py);if(ink.alpha<235/255)continue;
    const local=new THREE.Vector3(px,py,rigPlaneSurfaceZ(mesh,px,py)),world=hand.localToWorld(local.clone());
    const along=world.clone().sub(grip).dot(axis),axisWorld=grip.clone().addScaledVector(axis,along);
    const outward=camera.clone().sub(axisWorld);outward.addScaledVector(axis,-outward.dot(axis)).normalize();
    const scale=shaft.getWorldScale(new THREE.Vector3()),frontWorld=axisWorld.clone().addScaledVector(outward,radius*Math.max(scale.x,scale.z));
    samples.push({local:local.toArray(),world:world.toArray(),screen:rigProjectedWorld(world),alpha:ink.alpha,rgb:ink.rgb,
      gripDistance:Math.hypot(px-point.x,py-point.y),shaftAxisWorld:axisWorld.toArray(),shaftFrontWorld:frontWorld.toArray(),
      frontClearance:camera.distanceTo(frontWorld)-camera.distanceTo(world)});
  }
  samples.sort((a,b)=>a.gripDistance-b.gripDistance);return samples.slice(0,16);
}
function rigNaturalGripStatus(hand,point,shaft,camera){
  if(!hand.userData.rigGripLayers)return {layered:false};
  return {layered:true,asset:RIG_NATURAL_GRIP_ASSET,cameraWorld:camera.toArray(),
    palmSamples:rigGripLayerSamples(hand,'palm',point,shaft,camera),fingerSamples:rigGripLayerSamples(hand,'fingers',point,shaft,camera),
    palmMesh:hand.userData.rigGripLayers.palm.userData.frontMesh.uuid,
    fingerMesh:hand.userData.rigGripLayers.fingers.userData.frontMesh.uuid};
}
function rigRoundShaftStatus(shaft){
  const attribute=shaft.geometry.getAttribute('position'),height=shaft.geometry.parameters.height,points=[];
  for(let i=0;i<attribute.count;i++){
    if(Math.abs(attribute.getY(i)-height/2)>1e-6)continue;
    const point=[attribute.getX(i),attribute.getY(i),attribute.getZ(i)];
    if(Math.hypot(point[0],point[2])<1e-6||points.some(p=>Math.hypot(p[0]-point[0],p[2]-point[2])<1e-6))continue;
    points.push(point);
  }
  return {type:shaft.geometry.type,radialSegments:shaft.geometry.parameters.radialSegments,
    crossSectionVertexCount:points.length,radialSamplesLocal:points,radius:shaft.userData.rigShaft.radius,diameter:shaft.userData.rigShaft.radius*2};
}
function rigWoodShaftMaterial(){
  const canvas=document.createElement('canvas');canvas.width=256;canvas.height=256;
  const context=canvas.getContext('2d'),shade=context.createLinearGradient(0,0,256,0);
  shade.addColorStop(0,'#382619');shade.addColorStop(.18,'#785237');shade.addColorStop(.36,'#bc8550');
  shade.addColorStop(.5,'#8c5e35');shade.addColorStop(.8,'#4c321f');shade.addColorStop(1,'#382619');
  context.fillStyle=shade;context.fillRect(0,0,256,256);
  context.strokeStyle='rgba(36,22,13,.16)';context.lineWidth=1;
  for(let x=5;x<256;x+=11){context.beginPath();for(let y=0;y<=256;y+=8){const px=x+2*Math.sin(y*.035+x);if(y)context.lineTo(px,y);else context.moveTo(px,y);}context.stroke();}
  const texture=new THREE.CanvasTexture(canvas);texture.colorSpace=THREE.SRGBColorSpace;texture.wrapT=THREE.RepeatWrapping;texture.repeat.y=3;
  texture.userData.rigOwnedTexture=true;
  return new THREE.MeshBasicMaterial({map:texture,toneMapped:false});
}
