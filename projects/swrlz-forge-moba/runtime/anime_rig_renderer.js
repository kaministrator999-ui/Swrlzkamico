// Articulated paper cutouts. Pose pivots, facial ink and silhouette thickness
// share the native story clock; the original atlas pixels remain immutable.
const RIG_SLOTS={torso:0,pelvis:1,head:2,cape:3,leftUpperArm:4,leftForearm:5,leftHand:6,staff:7,rightUpperArm:8,rightForearm:9,rightHand:10,quill:11,leftUpperLeg:12,leftLowerLeg:13,leftFoot:14,rightUpperLeg:15,rightLowerLeg:16,rightFoot:17,grimoire:18,magic:19};
function rigAtlasCells(texture,character){
  if(texture.userData.rigCells?.[character])return texture.userData.rigCells[character];
  const image=texture.image;if(!image?.width)return null;
  const canvas=document.createElement('canvas');canvas.width=image.width;canvas.height=image.height;
  const context=canvas.getContext('2d',{willReadFrequently:true});context.drawImage(image,0,0);
  const pixels=context.getImageData(0,0,canvas.width,canvas.height).data;
  const bundledKami=character==='kami'&&rigModel().characters[character].asset==='assets/anime/kami-rig.png';
  const y0=bundledKami?75:0,height=bundledKami?1320:image.height,cells=[];
  for(let slot=0;slot<20;slot++){
    const l=Math.floor(slot%4*image.width/4),r=Math.floor((slot%4+1)*image.width/4),t=Math.floor(y0+Math.floor(slot/4)*height/5),b=Math.floor(y0+(Math.floor(slot/4)+1)*height/5);
    let x0=r,y1=b,x1=l,y2=t;
    for(let y=t;y<b;y++)for(let x=l;x<r;x++)if(pixels[(y*image.width+x)*4+3]>20){x0=Math.min(x0,x);x1=Math.max(x1,x+1);y1=Math.min(y1,y);y2=Math.max(y2,y+1);}
    if(x1<=x0){x0=l;x1=r;y1=t;y2=b;}
    x0=Math.max(l,x0-2);x1=Math.min(r,x1+2);y1=Math.max(t,y1-2);y2=Math.min(b,y2+2);
    const size=48,mask=[];
    for(let j=0;j<size;j++)for(let i=0;i<size;i++){
      const x=Math.min(x1-1,Math.floor(x0+(i+.5)*(x1-x0)/size)),y=Math.min(y2-1,Math.floor(y1+(j+.5)*(y2-y1)/size));
      mask.push(pixels[(y*image.width+x)*4+3]>40);
    }
    cells.push({x0,x1,y0:y1,y1:y2,width:image.width,height:image.height,mask,size});
  }
  texture.userData.rigCells??={};texture.userData.rigCells[character]=cells;return cells;
}
function rigGeometry(cell,w,h,thickness){
  const plane=new THREE.PlaneGeometry(w,h),uv=plane.getAttribute('uv');
  if(cell)for(let i=0;i<uv.count;i++)uv.setXY(i,(cell.x0+uv.getX(i)*(cell.x1-cell.x0))/cell.width,1-(cell.y0+(1-uv.getY(i))*(cell.y1-cell.y0))/cell.height);
  uv.needsUpdate=true;
  const vertices=[],n=cell?.size||1,mask=cell?.mask||[true];
  const inside=(x,y)=>x>=0&&y>=0&&x<n&&y<n&&mask[y*n+x];
  const quad=(a,b)=>{const [x0,y0]=a,[x1,y1]=b,z=thickness/2;vertices.push(x0,y0,z,x1,y1,z,x1,y1,-z,x0,y0,z,x1,y1,-z,x0,y0,-z);};
  for(let y=0;y<n;y++)for(let x=0;x<n;x++)if(inside(x,y)){
    const l=(x/n-.5)*w,r=((x+1)/n-.5)*w,t=(.5-y/n)*h,b=(.5-(y+1)/n)*h;
    if(!inside(x-1,y))quad([l,b],[l,t]);if(!inside(x+1,y))quad([r,t],[r,b]);
    if(!inside(x,y-1))quad([l,t],[r,t]);if(!inside(x,y+1))quad([r,b],[l,b]);
  }
  const edge=new THREE.BufferGeometry();edge.setAttribute('position',new THREE.Float32BufferAttribute(vertices,3));edge.computeVertexNormals();return {plane,edge};
}
function rigMakePart(texture,cell,width,height,thickness,id){
  const group=new THREE.Group(),geometry=rigGeometry(cell,width,height,thickness);
  const front=new THREE.Mesh(geometry.plane,new THREE.MeshBasicMaterial({map:texture,side:THREE.DoubleSide,transparent:true,alphaTest:.025,depthWrite:true,fog:false,toneMapped:false}));
  front.position.z=thickness/2;front.name=id+' · painted front';
  const back=new THREE.Mesh(geometry.plane.clone(),front.material.clone());back.position.z=-thickness/2;back.material.color.set('#8a643a');back.name=id+' · paper back';
  const edge=new THREE.Mesh(geometry.edge,new THREE.MeshBasicMaterial({color:'#b68a4f',side:THREE.DoubleSide,transparent:true,fog:false,toneMapped:false}));edge.name=id+' · cut paper edge';
  group.add(front,back,edge);group.userData.rigPart=id;return group;
}
// These footprints sit inside the blank skin on the bundled head cards. Kami's
// old placement crossed the chin into the neck; the skull has its own anatomy.
const RIG_FACE_FIT={kami:{x:-.10,y:-.165,width:.70,height:.45},swyrlz:{x:.065,y:-.635,width:.78,height:.67}};
function rigFaceSurface(character){
  const canvas=document.createElement('canvas');canvas.width=256;canvas.height=192;
  const texture=new THREE.CanvasTexture(canvas);texture.colorSpace=THREE.SRGBColorSpace;
  const fit=RIG_FACE_FIT[character];
  const mesh=new THREE.Mesh(new THREE.PlaneGeometry(fit.width,fit.height),new THREE.MeshBasicMaterial({map:texture,transparent:true,alphaTest:.01,depthWrite:true,side:THREE.DoubleSide,fog:false,toneMapped:false}));
  mesh.name=character+' · animated eyes brows and mouth';mesh.userData.rigFace=true;return {mesh,texture,canvas,fit,hash:null,applied:null};
}
function rigPaintFace(face,character,sample,time){
  const s={...sample},cue=storyBeat(time)?.cue||'';
  const speaking=s.speech&&(character==='kami'?/^KAMI\b/i:/^[§$]?WYRLZ\b/i).test(cue.trim());
  // Modest jaw motion keeps speech within the painted face and below the nose.
  if(speaking)s.mouth=Math.max(s.mouth,.12+.38*(.5+.5*Math.sin(time*31)));
  const hash=[s.expression,...Object.keys(RIG_FACE_BOUNDS).map(k=>Math.round(s[k]*50))].join(':');
  face.applied=s;if(face.hash===hash)return;face.hash=hash;
  const c=face.canvas.getContext('2d');c.clearRect(0,0,256,192);
  const skull=character==='swyrlz',happy=s.expression==='happy',sad=s.expression==='sad',determined=s.expression==='determined',surprised=s.expression==='surprised';
  const opening=Math.max(0,(1-s.blink)*(surprised?1.05:determined?.53:happy?.72:.86));
  c.lineCap='round';c.lineJoin='round';
  for(const side of [-1,1]){
    const x=128+side*44,y=67,ew=skull?29:28,eh=(skull?27:17)*opening;
    if(opening<.075){
      c.strokeStyle=skull?'#3b2418':'#583b2d';c.lineWidth=skull?4:3;
      c.beginPath();c.moveTo(x-ew,y-1);c.quadraticCurveTo(x,y+(happy?8:4),x+ew,y-1);c.stroke();
    }else if(skull){
      // Dark hollow sockets and warm embers belong to a skull, rather than
      // the human sclera and black pupils used on Kami's anime face.
      c.save();c.translate(x,y);c.rotate(side*(determined?-.10:.06));
      c.fillStyle='#281b14';c.strokeStyle='#755035';c.lineWidth=2.4;
      c.beginPath();c.ellipse(0,0,ew,eh,0,0,Math.PI*2);c.fill();c.stroke();
      c.clip();const gx=s.gazeX*9,gy=s.gazeY*7;
      const glow=c.createRadialGradient(gx,gy,1,gx,gy,12);glow.addColorStop(0,'#fff3b1');glow.addColorStop(.3,'#ffd66c');glow.addColorStop(.62,'#db8c27');glow.addColorStop(1,'rgba(166,86,18,0)');
      c.fillStyle=glow;c.beginPath();c.ellipse(gx,gy,12,Math.max(3,Math.min(13,eh*.7)),0,0,Math.PI*2);c.fill();
      c.restore();
    }else{
      // Tapered corners, one dark upper lash and a fine lower lid prevent the
      // full ellipse outlines from reading as round spectacles.
      const tilt=side*(determined?-3:sad?2:0),eyePath=()=>{
        c.beginPath();c.moveTo(x-ew,y+tilt);c.bezierCurveTo(x-ew*.42,y-eh,x+ew*.35,y-eh,x+ew,y-tilt);
        c.bezierCurveTo(x+ew*.4,y+eh*.55,x-ew*.4,y+eh*.62,x-ew,y+tilt);c.closePath();
      };
      eyePath();c.fillStyle='#f4dec8';c.fill();c.save();c.clip();
      const gx=x+s.gazeX*9,gy=y+s.gazeY*6;
      const iris=c.createLinearGradient(0,y-eh,0,y+eh);iris.addColorStop(0,'#6e451d');iris.addColorStop(.5,'#b17a31');iris.addColorStop(1,'#e1ad56');
      c.fillStyle=iris;c.beginPath();c.ellipse(gx,gy,10,Math.max(3,eh*.98),0,0,Math.PI*2);c.fill();
      c.fillStyle='#342318';c.beginPath();c.ellipse(gx,gy,3.7,Math.max(2,eh*.68),0,0,Math.PI*2);c.fill();
      c.fillStyle='#fff0ce';c.beginPath();c.ellipse(gx-3,gy-4,2.1,2.8,0,0,Math.PI*2);c.fill();c.restore();
      c.strokeStyle='#573a2a';c.lineWidth=3.3;c.beginPath();c.moveTo(x-ew,y+tilt);c.bezierCurveTo(x-ew*.42,y-eh,x+ew*.35,y-eh,x+ew,y-tilt);c.stroke();
      c.strokeStyle='#90684c';c.lineWidth=1.1;c.beginPath();c.moveTo(x-ew*.8,y+eh*.25);c.quadraticCurveTo(x,y+eh*.7,x+ew*.85,y+eh*.2);c.stroke();
      c.strokeStyle='#694c39';c.lineWidth=1.2;c.beginPath();c.moveTo(x-ew*.78,y-eh-4);c.quadraticCurveTo(x,y-eh-7,x+ew*.6,y-eh-4);c.stroke();
    }
    const browY=38-s.brow*6-(surprised?6:0),tilt=determined?-side*6:sad?side*6:0;
    c.strokeStyle=skull?'#8b633b':'#6f4d37';c.lineWidth=skull?2.2:2.7;c.beginPath();
    c.moveTo(x-ew*.8,browY-tilt);c.quadraticCurveTo(x,browY-3,x+ew*.76,browY+tilt);c.stroke();
  }
  if(skull){
    c.fillStyle='#39271b';c.beginPath();c.moveTo(127,102);c.quadraticCurveTo(121,107,119,116);c.quadraticCurveTo(125,115,128,118);c.quadraticCurveTo(131,114,137,115);c.lineTo(130,103);c.closePath();c.fill();
  }else{
    c.strokeStyle='#bd8a68';c.lineWidth=1.7;c.beginPath();c.moveTo(127,101);c.quadraticCurveTo(123,109,128,111);c.lineTo(132,110);c.stroke();
  }
  const smile=s.smile+(happy?.6:sad?-.4:0),mouthY=143;
  c.strokeStyle=skull?'#714b2f':'#945a43';c.lineWidth=skull?2.4:1.9;
  if(s.mouth>.06){
    const mouthWidth=skull?20:15+(surprised?2:0),mouthHeight=1.5+s.mouth*(skull?12:9);
    c.fillStyle=skull?'#332219':'#693c2c';c.beginPath();c.ellipse(128,mouthY,mouthWidth,mouthHeight,0,0,Math.PI*2);c.fill();c.stroke();
    if(skull){
      c.strokeStyle='#d5b583';c.lineWidth=2;for(let x=116;x<=140;x+=8){c.beginPath();c.moveTo(x,mouthY-mouthHeight+1);c.lineTo(x,mouthY-mouthHeight+4);c.moveTo(x,mouthY+mouthHeight-1);c.lineTo(x,mouthY+mouthHeight-3);c.stroke();}
    }else if(s.mouth>.24){
      c.fillStyle='#c59173';c.beginPath();c.ellipse(128,mouthY+mouthHeight*.55,8,Math.max(1,mouthHeight*.23),0,0,Math.PI*2);c.fill();
    }
  }else{
    c.beginPath();c.moveTo(skull?105:111,mouthY);c.quadraticCurveTo(128,mouthY+smile*(skull?10:7),skull?151:145,mouthY);c.stroke();
    if(skull){c.lineWidth=1.6;for(let x=112;x<=144;x+=8){c.beginPath();c.moveTo(x,mouthY-2);c.lineTo(x,mouthY+4);c.stroke();}}
  }
  face.texture.needsUpdate=true;
}
function rigBuildVisual(visual,character){
  const cfg=rigModel().characters[character],texture=storyTexture(cfg.asset),cells=rigAtlasCells(texture,character);
  const group=new THREE.Group();group.userData.storyVisual=visual;group.userData.popupHinge=true;
  const hinge=new THREE.Group();hinge.userData.storyCastHinge=true;hinge.position.y=-visual.height/2;group.add(hinge);
  const body=new THREE.Group(),factor=character==='swyrlz'?.53:1;body.scale.setScalar(factor);body.position.y=2.95*factor;hinge.add(body);
  const joints={},parts=[];
  const defs=[
    ['torso',null,0,.35,.02,1.9,1.95,0,-.5,0],['pelvis','torso',0,-.9,.08,2.2,2.25,0,-.85,0],
    ['head','torso',0,.7,.24,character==='swyrlz'?2.5:1.8,character==='swyrlz'?2.35:1.75,0,.7,0],
    ['cape','torso',0,.65,-.2,2.6,3.8,0,-1.3,0],
    ['leftUpperArm','torso',-.77,.3,.10,.78,1.25,0,-.43,-.16],['leftForearm','leftUpperArm',0,-.93,.05,.62,1.08,0,-.40,-.76],['leftHand','leftForearm',0,-.8,.11,.64,.58,0,-.13,0],
    ['rightUpperArm','torso',.77,.3,.12,.8,1.20,0,-.43,.18],['rightForearm','rightUpperArm',0,-.9,.06,.64,1.03,0,-.4,.70],['rightHand','rightForearm',0,-.8,.14,.66,.62,0,-.12,0],
    ['leftUpperLeg','pelvis',-.4,-.18,-.03,.65,1.20,0,-.45,0],['leftLowerLeg','leftUpperLeg',0,-.94,.05,.51,1.05,0,-.4,0],['leftFoot','leftLowerLeg',0,-.81,.1,.78,.52,-.08,-.15,0],
    ['rightUpperLeg','pelvis',.4,-.18,-.03,.65,1.20,0,-.45,0],['rightLowerLeg','rightUpperLeg',0,-.94,.05,.51,1.05,0,-.4,0],['rightFoot','rightLowerLeg',0,-.81,.1,.78,.52,.08,-.15,0],
    ['staff','leftHand',-.1,0,.12,1.24,1.73,0,2.1,.92],['quill','rightHand',.12,0,.12,.46,1.2,0,.4,-.48],['grimoire','leftHand',-.25,.25,.20,2.05,1.65,-.4,.2,.77]
  ];
  for(const [id,parent,x,y,z,w,h,mx,my,rz] of defs){
    const rest=new THREE.Group();rest.position.set(x,y,z*cfg.depth);rest.rotation.z=rz;rest.userData.rigBaseDepth=z;
    (parent?joints[parent]:body).add(rest);const pose=new THREE.Group();pose.name=character+' · '+id+' pivot';rest.add(pose);joints[id]=pose;
    const omit=character==='kami'?id==='grimoire':id==='staff'||id==='quill';
    if(!omit){const part=rigMakePart(texture,cells?.[RIG_SLOTS[id]],w,h,cfg.thickness,id);part.position.set(mx,my,0);pose.add(part);pose.userData.part=part;parts.push(part);}
  }
  if(character==='kami'){
    const shaft=new THREE.Mesh(new THREE.CylinderGeometry(.043,.043,3.55,8),new THREE.MeshBasicMaterial({color:'#6b4728',transparent:true,toneMapped:false}));shaft.position.set(0,-.28,0);joints.staff.add(shaft);
  }else{const magic=rigMakePart(texture,cells?.[19],.8,1.1,cfg.thickness,'magic');magic.position.set(-.4,1.05,.06);joints.grimoire.add(magic);parts.push(magic);}
  const face=rigFaceSurface(character);face.mesh.position.set(face.fit.x,face.fit.y,cfg.thickness/2+.02);joints.head.userData.part.add(face.mesh);
  group.userData.rig={character,joints,parts,face,texture,signature:JSON.stringify([cfg.enabled,cfg.asset,cfg.thickness,cfg.depth]),cellsReady:!!cells,thickness:cfg.thickness};
  rigAnimateCharacter(group,character,0);return group;
}
const rigOriginalPaperVisual=storyPaperVisual;
storyPaperVisual=function(value){
  const visual=storyCleanVisual(value),character=rigCharacterId(visual.layer);
  return character&&rigModel().characters[character].enabled?rigBuildVisual(visual,character):rigOriginalPaperVisual(visual);
};
function rigAnimateCharacter(group,character,time){
  const rig=group.userData.rig;if(!rig)return;
  const cfg=rigModel().characters[character];
  for(const [id,pivot] of Object.entries(rig.joints)){
    const key=rigSample(character,id,time);pivot.rotation.set(key.rotationX,key.rotationY,key.rotationZ);pivot.position.z=key.depth*cfg.depth;
    pivot.parent.position.z=pivot.parent.userData.rigBaseDepth*cfg.depth;
  }
  rigPaintFace(rig.face,character,rigSample(character,'face',time),time);
}
function rigDisposeChildren(group){
  for(const child of [...group.children]){group.remove(child);child.traverse(o=>{o.geometry?.dispose();for(const m of Array.isArray(o.material)?o.material:o.material?[o.material]:[])m.dispose();if(o.userData.rigFace)o.material.map.dispose();});}
}
function rigRebuildActor(actor){
  const replacement=storyPaperVisual(actor.userData.storyVisual);rigDisposeChildren(actor);
  for(const child of [...replacement.children])actor.add(child);
  if(replacement.userData.rig)actor.userData.rig=replacement.userData.rig;else delete actor.userData.rig;
}
function rigRefreshNativeActors(){
  for(const character of RIG_CHARACTERS){const actor=storyBoundActor(character);if(actor)rigRebuildActor(actor);}
}
function rigRefreshStage(){
  if(!currentProject?.animeRigs)return;
  for(const character of RIG_CHARACTERS){
    const cfg=rigModel().characters[character],signature=JSON.stringify([cfg.enabled,cfg.asset,cfg.thickness,cfg.depth]);
    const cast=animeCine?.cast?.[character==='kami'?'kami':'wisp'];
    for(const actor of [storyBoundActor(character),cast].filter(Boolean)){
      if(actor.userData.rig?.signature!==signature&&(cfg.enabled||actor.userData.rig))rigRebuildActor(actor);
      if(actor.userData.rig&&!actor.userData.rig.cellsReady&&actor.userData.rig.texture.image?.width)rigRebuildActor(actor);
      rigAnimateCharacter(actor,character,animeCine?.elapsed||0);
    }
  }
  if(animeCine)storyRender();
}
function rigTextureLoaded(texture,source){
  if(currentProject?.animeRigs&&RIG_CHARACTERS.some(id=>rigModel().characters[id].asset===source))rigRefreshStage();
}
function rigFitCamera(c){
  scene.updateMatrixWorld(true);
  const box=new THREE.Box3();for(const actor of [c.cast.kami,c.cast.wisp])if(actor.visible)box.expandByObject(actor);
  if(box.isEmpty())return;
  const tangent=Math.tan(THREE.MathUtils.degToRad(perspectiveCamera.fov)*.5),aspect=perspectiveCamera.aspect||1;
  // Include off-center limbs and their frontmost surface, even in portrait.
  const target=storySample('camera',c.elapsed),halfWidth=Math.max(Math.abs(box.min.x-target.tx),Math.abs(box.max.x-target.tx)),halfHeight=Math.max(Math.abs(box.min.y-target.ty),Math.abs(box.max.y-target.ty));
  const z=Math.max(perspectiveCamera.position.z,box.max.z+halfWidth*1.15/(tangent*aspect),box.max.z+halfHeight*1.12/tangent,box.max.z+6.5);
  perspectiveCamera.position.z=z;perspectiveCamera.lookAt(target.tx,target.ty,target.tz);perspectiveCamera.updateMatrixWorld(true);
}
function rigFaceInkStatus(face){
  const w=face.canvas.width,h=face.canvas.height,pixels=face.canvas.getContext('2d').getImageData(0,0,w,h).data;
  let x0=w,y0=h,x1=0,y1=0,pixelCount=0;
  for(let y=0;y<h;y++)for(let x=0;x<w;x++)if(pixels[(y*w+x)*4+3]>8){pixelCount++;x0=Math.min(x0,x);y0=Math.min(y0,y);x1=Math.max(x1,x+1);y1=Math.max(y1,y+1);}
  const p=face.mesh.position,fit=face.fit;
  return {pixelCount,canvasInkBounds:pixelCount?{min:[x0,y0],max:[x1,y1]}:null,
    featureInkBounds:pixelCount?{min:[p.x+(x0/w-.5)*fit.width,p.y+(.5-y1/h)*fit.height,p.z],max:[p.x+(x1/w-.5)*fit.width,p.y+(.5-y0/h)*fit.height,p.z]}:null};
}
function rigRenderStatus(character){
  if(!rigCharacterId(character))return null;
  const actor=animeCine?.cast?.[character==='kami'?'kami':'wisp']||storyBoundActor(character),rig=actor?.userData.rig;
  if(!rig)return {active:!!actor,rigged:false,partCount:0};
  actor.updateWorldMatrix(true,true);const box=new THREE.Box3().setFromObject(actor),joints={};let meshCount=0;actor.traverse(o=>{if(o.isMesh)meshCount++;});
  for(const [id,pivot] of Object.entries(rig.joints))joints[id]={rotation:[pivot.rotation.x,pivot.rotation.y,pivot.rotation.z],position:pivot.parent.position.clone().add(pivot.position).toArray(),worldPosition:pivot.getWorldPosition(new THREE.Vector3()).toArray(),partWorldPosition:(pivot.userData.part||pivot).getWorldPosition(new THREE.Vector3()).toArray()};
  return {active:!!animeCine,rigged:true,partCount:rig.parts.length,meshCount,thickness:rig.thickness,depthSpan:box.max.z-box.min.z,bounds:{min:box.min.toArray(),max:box.max.toArray()},joints,face:{...rig.face.applied,textureVersion:rig.face.texture.version,anchor:rig.face.mesh.position.toArray(),footprint:{width:rig.face.fit.width,height:rig.face.fit.height},...rigFaceInkStatus(rig.face)}};
}
window.SWYRL_ENGINE_RIG=Object.freeze({...window.SWYRL_ENGINE_RIG,renderStatus:rigRenderStatus});
