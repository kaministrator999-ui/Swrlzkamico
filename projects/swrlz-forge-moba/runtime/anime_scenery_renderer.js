// Genuine paper scenery in the same scene/camera as native editor Play.
// UV rectangles select the original generated atlas; no pixels are rewritten.
const SCENERY_ATLAS_REGIONS=[[0,0,306,319],[306,0,573,319],[573,0,850,319],[850,0,1122,319],[0,319,306,634],[306,319,573,634],[573,319,850,634],[850,319,1122,634],[0,634,306,895],[306,634,573,895],[573,634,850,895],[850,634,1122,895],[0,895,306,1135],[306,895,573,1135],[573,895,850,1135],[850,895,1122,1135],[0,1135,306,1402],[306,1135,559,1402],[559,1135,882,1402],[882,1135,1122,1402]];
let scenerySkyTexture=null;
function scenerySky(){
  if(scenerySkyTexture)return scenerySkyTexture;
  scenerySkyTexture=animeDrawSurface((c,w,h)=>{
    const g=c.createLinearGradient(0,0,0,h);g.addColorStop(0,'#111829');g.addColorStop(.45,'#2e2935');g.addColorStop(.78,'#765035');g.addColorStop(1,'#17151c');c.fillStyle=g;c.fillRect(0,0,w,h);
    for(let i=0;i<14;i++){const x=(i*317)%w,y=h*.25+(i*71)%(h*.55),r=100+(i%4)*45,cloud=c.createRadialGradient(x,y,0,x,y,r);cloud.addColorStop(0,'#dca76218');cloud.addColorStop(1,'#e0bb7300');c.fillStyle=cloud;c.fillRect(x-r,y-r,2*r,2*r);}
  },1536,864);return scenerySkyTexture;
}
function sceneryAtlas(texture){
  if(texture.userData.sceneryCells)return texture.userData.sceneryCells;
  const image=texture.image;if(!image?.width)return null;
  const canvas=document.createElement('canvas');canvas.width=image.width;canvas.height=image.height;
  const context=canvas.getContext('2d',{willReadFrequently:true});context.drawImage(image,0,0);
  const rgba=context.getImageData(0,0,canvas.width,canvas.height).data,cells=[];
  for(const region of SCENERY_ATLAS_REGIONS){
    const [l,t,r,b]=region.map((n,i)=>Math.round(n*(i%2?image.height/1402:image.width/1122)));
    let x0=r,x1=l,y0=b,y1=t;
    for(let y=t;y<b;y++)for(let x=l;x<r;x++)if(rgba[(y*image.width+x)*4+3]>12){x0=Math.min(x0,x);x1=Math.max(x1,x+1);y0=Math.min(y0,y);y1=Math.max(y1,y+1);}
    if(x1<=x0){x0=l;x1=r;y0=t;y1=b;}
    x0=Math.max(l,x0-2);x1=Math.min(r,x1+2);y0=Math.max(t,y0-2);y1=Math.min(b,y1+2);
    const size=48,mask=[];
    for(let j=0;j<size;j++)for(let i=0;i<size;i++){
      const x=Math.min(x1-1,Math.floor(x0+(i+.5)*(x1-x0)/size)),y=Math.min(y1-1,Math.floor(y0+(j+.5)*(y1-y0)/size));mask.push(rgba[(y*image.width+x)*4+3]>110);
    }
    cells.push({x0,x1,y0,y1,width:image.width,height:image.height,size,mask});
  }
  texture.userData.sceneryCells=cells;return cells;
}
function sceneryStars(spec){
  const shape=new THREE.Shape();for(let j=0;j<10;j++){const angle=Math.PI/2+j*Math.PI/5,r=j%2?.35:1;const x=Math.cos(angle)*r,y=Math.sin(angle)*r;if(j===0)shape.moveTo(x,y);else shape.lineTo(x,y);}shape.closePath();
  const geometry=new THREE.ExtrudeGeometry(shape,{depth:spec.thickness,bevelEnabled:false,steps:1});geometry.translate(0,0,-spec.thickness/2);
  const stars=new THREE.InstancedMesh(geometry,new THREE.MeshBasicMaterial({color:'#efd7a6',transparent:true,fog:false,toneMapped:false}),spec.count);
  const dummy=new THREE.Object3D(),seed=spec.id==='stars-far'?7:spec.id==='stars-middle'?19:31;
  for(let i=0;i<spec.count;i++){
    const u=((i*137+seed*97)%997)/997,v=((i*281+seed*53)%991)/991,s=.035+((i*17+seed)%37)/370;
    dummy.position.set((u-.5)*spec.width,v*(spec.height-1)+.5,0);dummy.rotation.z=(i*.618+seed)%Math.PI;dummy.scale.set(s,s,1);dummy.updateMatrix();stars.setMatrixAt(i,dummy.matrix);
    stars.setColorAt(i,new THREE.Color(i%3===0?'#fff3cc':i%3===1?'#d7ac64':'#b5c7e0'));
  }
  stars.instanceMatrix.needsUpdate=true;stars.computeBoundingBox();stars.name=spec.label+' · individual paper stars';stars.userData.sceneryStars=spec.count;return stars;
}
function scenerySignature(){const m=sceneryModel();return JSON.stringify([m.enabled,...Object.values(m.objects).map(o=>[o.id,o.parent,o.asset,o.slot,o.width,o.height,o.thickness])]);}
function sceneryBuildVisual(visual){
  const group=new THREE.Group();group.userData.storyVisual=visual;group.userData.popupHinge=true;
  const data={parent:visual.layer,signature:scenerySignature(),objects:{},cellsReady:true};
  if(visual.layer==='background'){
    const sky=new THREE.Mesh(new THREE.PlaneGeometry(70,40),new THREE.MeshBasicMaterial({map:scenerySky(),side:THREE.DoubleSide,transparent:true,fog:false,toneMapped:false}));
    sky.position.set(0,20,-27);sky.name='Painted twilight sky · behind every constellation';group.add(sky);data.sky=sky;
  }
  for(const spec of Object.values(sceneryModel().objects).filter(o=>o.parent===visual.layer)){
    const pivot=new THREE.Group(),hinge=new THREE.Group();pivot.name=spec.label+' · independent bottom pivot';pivot.add(hinge);group.add(pivot);
    let part;
    if(spec.kind==='stars'){part=sceneryStars(spec);hinge.add(part);}
    else{
      const texture=storyTexture(spec.asset),cells=sceneryAtlas(texture);if(!cells)data.cellsReady=false;
      part=rigMakePart(texture,cells?.[spec.slot],spec.width,spec.height,spec.thickness,spec.id);part.position.y=spec.height/2;hinge.add(part);
    }
    data.objects[spec.id]={spec,pivot,hinge,part};
  }
  group.userData.storyScenery=data;sceneryAnimateGroup(group,visual.layer,0,storySample('camera',0));return group;
}
const sceneryOriginalPaperVisual=storyPaperVisual;
storyPaperVisual=function(value){
  const visual=storyCleanVisual(value);
  return SCENERY_PARENTS.includes(visual.layer)&&sceneryModel().enabled?sceneryBuildVisual(visual):sceneryOriginalPaperVisual(visual);
};
function sceneryAnimateGroup(group,parent,time,cam){
  const data=group?.userData.storyScenery;if(!data)return;
  const model=sceneryModel(),whole=storySample(parent,time);
  for(const [id,item] of Object.entries(data.objects)){
    const key=scenerySample(id,time),spec=model.objects[id];
    item.pivot.position.set(key.x+cam.x*spec.parallax*.35,key.y,key.z*model.depth);
    item.pivot.rotation.set(key.rotationX,key.rotationY,key.rotationZ);item.pivot.scale.setScalar(key.scale);
    item.hinge.rotation.x=-(1-key.unfold)*Math.PI*.5;
    item.pivot.visible=key.visible&&key.opacity>.01;storyApplyOpacity(item.part,key.opacity*whole.opacity);
  }
  if(data.sky)data.sky.material.opacity=whole.opacity;
}
function sceneryRebuildActor(actor){
  const replacement=storyPaperVisual(actor.userData.storyVisual);rigDisposeChildren(actor);
  for(const child of [...replacement.children])actor.add(child);
  if(replacement.userData.storyScenery)actor.userData.storyScenery=replacement.userData.storyScenery;else delete actor.userData.storyScenery;
}
function sceneryRefreshNativeActors(){
  for(const parent of SCENERY_PARENTS){const actor=storyBoundActor(parent);if(actor)sceneryRebuildActor(actor);}
}
function sceneryRefreshStage(){
  if(!sceneryIsProject())return;
  const model=sceneryModel(),signature=scenerySignature(),time=animeCine?.elapsed||0;
  for(const parent of SCENERY_PARENTS)for(const actor of [storyBoundActor(parent),animeCine?.layers[parent]?.children[0]].filter(Boolean)){
    const data=actor.userData.storyScenery;
    if((data?.signature!==signature&&(model.enabled||data))||data&&!data.cellsReady&&Object.values(data.objects).some(o=>o.spec.kind!=='stars'&&storyTexture(o.spec.asset).image?.width))sceneryRebuildActor(actor);
    sceneryAnimateGroup(actor,parent,time,storySample('camera',time));
  }
  if(animeCine)storyRender();
}
const sceneryRigTextureLoaded=rigTextureLoaded;
rigTextureLoaded=function(texture,source){
  sceneryRigTextureLoaded(texture,source);
  if(currentProject?.animeScenery&&Object.values(sceneryModel().objects).some(o=>o.asset===source))sceneryRefreshStage();
};
function scenerySetArtworkMode(parent){
  if(!SCENERY_PARENTS.includes(parent)||!sceneryIsProject())return;
  const model=storyCopy(sceneryModel());model.enabled=false;currentProject.animeScenery=model;sceneryValidatedProject=currentProject;sceneryValidatedModel=model;
  // The caller already owns the artwork transaction, including this rebuild.
  sceneryRefreshNativeActors();
}
function sceneryRenderStatus(){
  if(!sceneryIsProject())return {active:false,enabled:false,objects:[],starLayers:[]};
  scene.updateMatrixWorld(true);perspectiveCamera.updateMatrixWorld(true);
  const objects=[],starLayers=[];
  for(const parent of SCENERY_PARENTS){
    const actor=animeCine?.layers[parent]?.children[0]||storyBoundActor(parent),data=actor?.userData.storyScenery;if(!data)continue;
    for(const [id,item] of Object.entries(data.objects)){
      let meshCount=0;item.part.traverse(o=>{if(o.isMesh)meshCount++;});
      const box=new THREE.Box3().setFromObject(item.part),world=box.getCenter(new THREE.Vector3()),screen=world.clone().project(perspectiveCamera);
      const value={id,parent,visible:item.pivot.visible&&actor.visible&&(!animeCine||animeCine.layers[parent].visible),position:item.pivot.position.toArray(),rotation:[item.pivot.rotation.x,item.pivot.rotation.y,item.pivot.rotation.z],worldPosition:world.toArray(),screenPosition:[screen.x*.5+.5,.5-screen.y*.5],depthSpan:box.max.z-box.min.z,meshCount,thickness:item.spec.thickness};
      objects.push(value);if(item.spec.kind==='stars')starLayers.push({...value,z:world.z,pointCount:item.spec.count});
    }
  }
  return {active:!!animeCine,enabled:sceneryModel().enabled,objects,starLayers};
}
window.SWYRL_ENGINE_SCENERY=Object.freeze({...window.SWYRL_ENGINE_SCENERY,renderStatus:sceneryRenderStatus});
