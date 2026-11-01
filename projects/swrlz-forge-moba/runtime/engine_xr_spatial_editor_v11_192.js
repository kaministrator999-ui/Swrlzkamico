// §E v11.192 — first native in-world Quest map authoring layer.
// Uses existing XR session, one render loop, native actor selection,
// transactions, authored scene geometry and saved Kami Precision game controls.
const se192={
 mode:'edit',left:null,right:null,moveSpeed:1.7,flySpeed:1.1,
 turnDegrees:20,lastTurn:0,turnLatched:false,lastFrame:0,
 panel:null,panelButtons:[],panelTextures:[],panelVisible:true,panelPositioned:false,labelsAnchored:false,
 beams:[],cursors:[],sprites:[],grabs:new Map(),lastError:'',
 lastAction:'',savedAim:[0,0],inputSamples:0
};
function se192AimRead(){
 try{const data=JSON.parse(localStorage.getItem('swyrl.xr.aim.v1')||'null');
 if(Array.isArray(data)&&data.length===2&&data.every(x=>Number.isFinite(x)&&Math.abs(x)<=.25))
 return data.slice();}catch(_){}
 return [0,0];
}
se192.savedAim=se192AimRead();
function se192InputRecord(side){
 const records=se181XR.controllers;
 return records.find(r=>r.input?.handedness===side)||
  records[side==='left'?0:1]||null;
}
function se192Stick(record){
 const a=record?.input?.gamepad?.axes;
 if(!a||a.length<2)return {x:0,y:0};
 const x=Number(a[a.length-2])||0,y=Number(a[a.length-1])||0;
 if(!Number.isFinite(x)||!Number.isFinite(y))return {x:0,y:0};
 const d=.2,m=Math.hypot(x,y);
 if(m<d)return {x:0,y:0};
 const scaled=Math.min(1,(m-d)/(1-d))/m;
 return {x:x*scaled,y:y*scaled};
}
function se192Pressed(record,index){
 const b=record?.input?.gamepad?.buttons?.[index];
 return !!b&&(b.pressed===true||b.value>.7);
}
function se192TaperGeometry(){
 const radial=10,rings=[[0,.00045],[-.07,.0047],[-.91,.0047],[-1,.00045]];
 const verts=[],faces=[];
 for(const [z,rad] of rings)for(let i=0;i<radial;i++){
  const a=i*2*Math.PI/radial;verts.push(rad*Math.cos(a),rad*Math.sin(a),z);
 }
 for(let k=0;k<rings.length-1;k++)for(let i=0;i<radial;i++){
  const n=(i+1)%radial,a=k*radial+i,b=k*radial+n,c=(k+1)*radial+i,d=(k+1)*radial+n;
  faces.push(a,c,b,b,c,d);
 }
 const geo=new THREE.BufferGeometry();
 geo.setAttribute('position',new THREE.Float32BufferAttribute(verts,3));
 geo.setIndex(faces);geo.computeVertexNormals();return geo;
}
function se192PrepareRay(record){
 if(record.se192)return;
 const pivot=new THREE.Group();pivot.name='§E calibrated target ray';
 record.controller.add(pivot);pivot.rotation.y=se192.savedAim[record.index]||0;
 const beam=new THREE.Mesh(se192TaperGeometry(),new THREE.MeshBasicMaterial({
  color:record.index===0?0x65f8fc:0xffd77b,transparent:true,opacity:.9,
  depthTest:false,depthWrite:false,toneMapped:false,side:THREE.DoubleSide
 }));
 beam.name='§E tapered controller beam';beam.renderOrder=9999;beam.frustumCulled=false;
 pivot.add(beam);
 const dot=new THREE.Group();dot.name='§E target reticle';
 for(const [radius,thickness,alpha] of [[.018,.0038,1],[.035,.002,.65]]){
  const ring=new THREE.Mesh(new THREE.RingGeometry(radius,radius+thickness,30),
   new THREE.MeshBasicMaterial({color:record.index===0?0x7df6fd:0xffe3a3,
    transparent:true,opacity:alpha,side:THREE.DoubleSide,
    depthTest:false,depthWrite:false,toneMapped:false}));
  ring.renderOrder=10002;dot.add(ring);
 }
 scene.add(dot);record.ray.visible=false;
 record.se192={pivot,beam,dot,markerDistance:3};
 se192.beams.push(record.se192);se192.cursors.push(dot);
}
function se192Ray(record){
 const pivot=record?.se192?.pivot||record?.controller;
 if(!pivot)return null;
 pivot.updateMatrixWorld(true);
 const origin=pivot.getWorldPosition(new THREE.Vector3());
 const direction=new THREE.Vector3(0,0,-1).transformDirection(pivot.matrixWorld).normalize();
 return {origin,direction,ray:new THREE.Raycaster(origin,direction,.025,35)};
}
function se192Raycast(record){
 const cast=se192Ray(record);if(!cast)return null;
 // Native exit sign, built-in XR tools and authored actors use SAME ray.
 const exit=se181XR.exitSurface;
 if(exit?.visible){
  const hits=cast.ray.intersectObject(exit,false);
  if(hits.length)return {exit:true,distance:hits[0].distance,point:hits[0].point};
 }
 if(se192.panelVisible&&se192.panelButtons.length){
  const hits=cast.ray.intersectObjects(se192.panelButtons,false);
  if(hits.length){
   const mesh=hits[0].object;
   return {ui:mesh.userData.se192Action,distance:hits[0].distance,point:hits[0].point};
  }
 }
 // Real game editor actor roots; prevent GUI and helper selection.
 const roots=Array.isArray(actors)?actors.filter(o=>o?.isObject3D&&o.visible!==false&&
   o.userData?.actorType!=='ground'&&o.userData?.type!=='ground'):[];
 const hits=cast.ray.intersectObjects(roots,true);
 for(const hit of hits){
  let p=hit.object;
  while(p&&!roots.includes(p))p=p.parent;
  if(!p||p.visible===false)continue;
  const root=rootGroupFor(p);
  if(root?.visible!==false&&root?.userData?.actorType!=='ground')
   return {object:root,distance:hit.distance,point:hit.point,normal:hit.face?.normal};
 }
 // Floor cursor even when no actor selected; never select the ground.
 const floorPlane=new THREE.Plane(new THREE.Vector3(0,1,0),0);
 const point=cast.ray.ray.intersectPlane(floorPlane,new THREE.Vector3());
 if(point&&point.distanceTo(cast.origin)<35&&point.distanceTo(cast.origin)>.025)
  return {ground:true,distance:point.distanceTo(cast.origin),point};
 return {empty:true,distance:3,point:cast.origin.clone().addScaledVector(cast.direction,3)};
}
function se192RenderRay(record,hit){
 if(!record?.se192)return;
 const {beam,dot}=record.se192,cast=se192Ray(record);
 if(!cast)return;
 const dist=THREE.MathUtils.clamp(Number(hit?.distance)||3,.12,20);
 beam.scale.z=dist; // local Z beam endpoint and raycast share a calibrated origin
 beam.material.color.setHex(hit?.object||hit?.ui||hit?.exit?0xacfcc7:
  record.index===0?0x65f8fc:0xffd77b);
 dot.position.copy(cast.origin).addScaledVector(cast.direction,dist);
 // Aim reticle planes toward the controller to keep them readable on surfaces.
 dot.quaternion.setFromUnitVectors(new THREE.Vector3(0,0,1),cast.direction.clone().negate());
 dot.visible=!!hit&&!hit.empty;
}
function se192TextPanelLine(label,selected=false){
 const c=document.createElement('canvas');c.width=640;c.height=130;
 const x=c.getContext('2d');
 x.fillStyle=selected?'#176b72':'#142b3d';x.fillRect(0,0,640,130);
 x.strokeStyle=selected?'#b7ffeb':'#5a94a1';x.lineWidth=8;x.strokeRect(4,4,632,122);
 x.fillStyle='#edfffd';x.textAlign='center';x.textBaseline='middle';
 x.font='bold 46px sans-serif';x.fillText(label,320,66,610);
 const texture=new THREE.CanvasTexture(c);texture.colorSpace=THREE.SRGBColorSpace;
 se192.panelTextures.push(texture);return texture;
}
function se192CreatePanel(){
 if(se192.panel)return;
 const group=new THREE.Group();group.name='§E · VR Map Editor tools';
 // World anchored panel. Tool items are ray-selectable meshes, not browser UI.
 const actions=[
 ['select','SELECT'],['move','GRAB / MOVE'],['wall','PLACE WALL'],
 ['rock','PLACE ROCK'],['undo','UNDO'],['aimLeft','AIM ←'],
 ['aimRight','AIM →'],['exit','EXIT VR']
 ];
 const width=.68,height=.135;
 for(let i=0;i<actions.length;i++){
  const [key,label]=actions[i],mesh=new THREE.Mesh(
   new THREE.PlaneGeometry(width,height),
   new THREE.MeshBasicMaterial({map:se192TextPanelLine(label,i===0),
    transparent:true,depthTest:false,depthWrite:false,toneMapped:false,side:THREE.DoubleSide})
  );
  mesh.name='§E VR editor · '+label;
  mesh.userData.se192Action=key;mesh.renderOrder=10004;
  mesh.position.set(0,.55-i*.155,0);
  mesh.frustumCulled=false;group.add(mesh);se192.panelButtons.push(mesh);
 }
 scene.add(group);se192.panel=group;se192.panelPositioned=false;se192.panelVisible=true;
}
function se192PanelPosition(){
 if(!se192.panel||se192.panelPositioned)return;
 const pose=se191XRHeadPose();if(!pose)return;
 const facing=pose.forward.clone();facing.y=0;
 if(facing.lengthSq()<.03)facing.set(0,0,-1);
 facing.normalize();
 const right=new THREE.Vector3().crossVectors(facing,new THREE.Vector3(0,1,0)).normalize();
 se192.panel.position.copy(pose.eye).addScaledVector(facing,1.2)
  .addScaledVector(right,.60).add(new THREE.Vector3(0,-.42,0));
 se192.panel.lookAt(pose.eye);
 se192.panelPositioned=true;
}
function se192PanelsVisible(value){
 se192.panelVisible=!!value;
 if(se192.panel)se192.panel.visible=se192.panelVisible;
}
function se192FreezeBillboards(){
 if(!scene?.traverse)return;
 const head=se191XRHeadPose();
 scene.updateMatrixWorld(true);
 scene.traverse(obj=>{
  if(!obj.isSprite||obj.userData?.se192LabelFixed)return;
  // Only native, world-placed editor labels; don't alter other game sprites.
  if(!/WorkspaceStationLabel/i.test(obj.name||'')||!obj.visible)return;
  const parent=obj.parent;if(!parent)return;
  const mat=new THREE.MeshBasicMaterial({
   map:obj.material.map,transparent:true,depthWrite:false,
   depthTest:true,side:THREE.DoubleSide,toneMapped:false
  });
  const plane=new THREE.Mesh(new THREE.PlaneGeometry(1,1),mat);
  plane.name='§E anchored '+obj.name;
  plane.position.copy(obj.position);plane.scale.set(obj.scale.x,obj.scale.y,1);
  parent.add(plane);
  if(head)plane.lookAt(head.eye); // Orient once at launch, never per head frame.
  obj.visible=false;obj.userData.se192LabelFixed=true;
  se192.sprites.push({original:obj,plane,parent,wasVisible:obj.visible});
 });
}
function se192RestoreBillboards(){
 for(const s of se192.sprites){
  if(s.plane.parent)s.plane.parent.remove(s.plane);
  s.plane.geometry.dispose();s.plane.material.dispose(); // NOT shared sprite texture
  s.original.visible=s.wasVisible;delete s.original.userData.se192LabelFixed;
 }
 se192.sprites.length=0;se192.labelsAnchored=false;
}
function se192MoveBy(x,y,z){
 const space=renderer.xr.getReferenceSpace?.();
 if(!space?.getOffsetReferenceSpace||typeof XRRigidTransform!=='function')return false;
 try{
  renderer.xr.setReferenceSpace(space.getOffsetReferenceSpace(
   new XRRigidTransform({x:-x,y:-y,z:-z})));
  return true;
 }catch(e){se192.lastError='VR move: '+String(e?.message||e);return false;}
}
function se192SnapTurn(radians){
 const space=renderer.xr.getReferenceSpace?.(),pose=se191XRHeadPose();
 if(!space?.getOffsetReferenceSpace||!pose||typeof XRRigidTransform!=='function')return false;
 // New reference-space axes rotate around the current tracked head, not world 0.
 const p=pose.eye;
 const c=Math.cos(radians),s=Math.sin(radians);
 const rx=c*p.x+s*p.z,rz=-s*p.x+c*p.z;
 const d={x:p.x-rx,y:0,z:p.z-rz};
 try{
  renderer.xr.setReferenceSpace(space.getOffsetReferenceSpace(new XRRigidTransform(
   {x:-d.x,y:0,z:-d.z},
   {x:0,y:-Math.sin(radians/2),z:0,w:Math.cos(radians/2)}
  )));
  return true;
 }catch(e){se192.lastError='VR turn: '+String(e?.message||e);return false;}
}
function se192MoveFrame(dt){
 const left=se192InputRecord('left'),right=se192InputRecord('right');
 const ls=se192Stick(left),rs=se192Stick(right),head=se191XRHeadPose();
 if(head&&(Math.abs(ls.x)+Math.abs(ls.y)>.05)){
  const forward=head.forward.clone();forward.y=0;
  if(forward.lengthSq()<.001)forward.set(0,0,-1);
  forward.normalize();
  const rightVec=new THREE.Vector3().crossVectors(forward,new THREE.Vector3(0,1,0)).normalize();
  const travel=forward.multiplyScalar(-ls.y).addScaledVector(rightVec,ls.x);
  const normal=Math.max(1,travel.length());travel.divideScalar(normal);
  const fly=se192Pressed(left,1);
  if(fly){
   // Left grip + stick Y = float vertically, stick X = lateral drift.
   travel.y=-ls.y*se192.flySpeed/se192.moveSpeed;
   travel.addScaledVector(head.forward.clone().setY(0).normalize(),ls.y);
  }
  travel.multiplyScalar(se192.moveSpeed*dt);
  se192MoveBy(travel.x,travel.y,travel.z);
 }
 if(Math.abs(rs.x)<.42)se192.turnLatched=false;
 else if(!se192.turnLatched&&performance.now()-se192.lastTurn>320){
  se192.turnLatched=true;se192.lastTurn=performance.now();
  se192SnapTurn((rs.x>0?-1:1)*THREE.MathUtils.degToRad(se192.turnDegrees));
 }
 se192.inputSamples++;
}
function se192GrabFrame(record){
 if(!record||record.input?.handedness!=='right')return;
 const gripping=se192Pressed(record,1);
 let state=se192.grabs.get(record.index);
 if(!gripping&&state){
  se192.grabs.delete(record.index);
  try{
   if(state.moved){
    state.actor.userData.spawnPos=state.actor.position.toArray();
    commitTransaction('VR move '+state.actor.name);
    rebuildHierarchy();syncInspector();refreshDebug();
   }
  }catch(e){se192.lastError='VR move commit: '+String(e?.message||e);}
  return;
 }
 if(!gripping||playing||simulating)return;
 const cast=se192Ray(record);if(!cast)return;
 if(!state){
  const hit=se192Raycast(record);
  const actor=hit?.object||selected;
  if(!actor||actor.userData?.actorType==='ground')return;
  const world=actor.getWorldPosition(new THREE.Vector3());
  const distance=THREE.MathUtils.clamp(world.distanceTo(cast.origin),.2,12);
  const point=cast.origin.clone().addScaledVector(cast.direction,distance);
  try{beginTransaction('VR move '+actor.name);}catch(e){se192.lastError=String(e);return;}
  state={actor,distance,offset:world.sub(point),moved:false};
  se192.grabs.set(record.index,state);selectActor(actor);
 }
 const point=cast.origin.clone().addScaledVector(cast.direction,state.distance).add(state.offset);
 if(![point.x,point.y,point.z].every(Number.isFinite)||point.length()>1000)return;
 const parent=state.actor.parent;
 const local=parent?parent.worldToLocal(point.clone()):point;
 state.actor.position.copy(local);state.actor.updateMatrixWorld(true);
 state.moved=true;
}
function se192Place(type,record){
 if(playing||simulating)return;
 const cast=record&&se192Ray(record);
 if(!cast)return;
 const hit=se192Raycast(record);
 const at=hit?.point?.clone()||cast.origin.clone().addScaledVector(cast.direction,2);
 // Do not place assets on floating editor UI or exit panel.
 if(hit?.exit||hit?.ui)return;
 try{
  beginTransaction('VR place '+type);
  const prev=new Set(actors);
  createPrefab(type);
  const newly=actors.find(a=>!prev.has(a))||selected;
  if(!newly)throw Error('Prefab not created');
  const parent=newly.parent;
  const local=parent?parent.worldToLocal(at.clone()):at;
  newly.position.copy(local);newly.userData.spawnPos=newly.position.toArray();
  selectActor(newly);rebuildHierarchy();refreshDebug();
  commitTransaction('VR place '+type);
  se192.lastAction='Placed '+type;
 }catch(e){se192.lastError='VR place: '+String(e?.message||e).slice(0,130);}
}
function se192Action(action,record){
 se192.lastAction=action;
 if(action==='exit'){void se181XRExit();return true;}
 if(action==='aimLeft'||action==='aimRight'){
  const idx=record?.index??1,sign=action==='aimLeft'?-1:1;
  se192.savedAim[idx]=THREE.MathUtils.clamp(se192.savedAim[idx]+sign*.012,-.25,.25);
  const target=se181XR.controllers.find(r=>r.index===idx);
  if(target?.se192)target.se192.pivot.rotation.y=se192.savedAim[idx];
  try{localStorage.setItem('swyrl.xr.aim.v1',JSON.stringify(se192.savedAim));}catch(_){}
  return true;
 }
 if(action==='wall'||action==='rock'){se192Place(action,record);return true;}
 if(action==='undo'){
  try{const b=document.getElementById('undoBtn');if(b?.click)b.click();}
  catch(e){se192.lastError='VR undo: '+String(e).slice(0,90);}
  return true;
 }
 if(action==='move'){se192.mode='move';se192PanelsVisible(false);return true;}
 if(action==='select'){se192.mode='edit';return true;}
 return false;
}
function se192Select(record){
 const hit=se192Raycast(record);
 if(hit?.exit){void se181XRExit();return;}
 if(hit?.ui){se192Action(hit.ui,record);return;}
 if(playing||simulating)return;
 if(hit?.object){
  selectActor(hit.object);se181XR.selectedCount++;se192.lastAction='Selected '+hit.object.name;
 }
}
function se192VRFrame(){
 if(!se181XR.session||!renderer.xr.isPresenting)return;
 const now=performance.now(),dt=Math.min(.055,Math.max(0,(now-(se192.lastFrame||now))/1000));
 se192.lastFrame=now;
 for(const record of se181XR.controllers){
  se192PrepareRay(record);
  const hit=se191XRRayHit(record);
  se192RenderRay(record,hit);
  se192GrabFrame(record);
  if(record.input?.gamepad){
   const pressed=se192Pressed(record,4);
   if(pressed&&!record.se192.actionHeld){
    if(record.input?.handedness==='left')se192XRGamepadButton(record,'x');
    if(record.input?.handedness==='right')se192XRGamepadButton(record,'a');
   }
   record.se192.actionHeld=pressed;
  }
 }
 se192PanelPosition();
 if(!se192.labelsAnchored){se192FreezeBillboards();se192.labelsAnchored=true;}
 if(!playing&&!simulating)se192MoveFrame(dt);
}
function se192VRStart(){
 se192.lastFrame=performance.now();se192.inputSamples=0;
 se192.labelsAnchored=false;se192CreatePanel();
}
function se192VRCleanup(){
 for(const [key,state] of se192.grabs){
  try{if(state.moved){state.actor.userData.spawnPos=state.actor.position.toArray();commitTransaction('VR move '+state.actor.name);}}catch(_){}
 }
 se192.grabs.clear();
 for(const record of se181XR.controllers){
  const extra=record.se192;if(!extra)continue;
  record.controller.remove(extra.pivot);
  scene.remove(extra.dot);
  extra.beam.geometry?.dispose();extra.beam.material?.dispose();
  extra.dot.traverse(o=>{o.geometry?.dispose();o.material?.dispose();});
  record.ray.visible=true;delete record.se192;
 }
 se192.beams.length=0;se192.cursors.length=0;
 if(se192.panel){scene.remove(se192.panel);
  for(const mesh of se192.panelButtons){mesh.geometry.dispose();mesh.material.dispose();}
  for(const t of se192.panelTextures)t.dispose();
 }
 se192.panel=null;se192.panelButtons=[];se192.panelTextures=[];
 se192.panelPositioned=false;se192RestoreBillboards();
 se192.lastFrame=0;se192.mode='edit';
}
function se192XRGamepadButton(record,button){
 if(record.input?.handedness==='left'&&button==='x'){
  se192PanelsVisible(!se192.panelVisible);
  return true;
 }
 if(record.input?.handedness==='right'&&button==='a'){
  se192.mode=se192.mode==='edit'?'move':'edit';
  se192PanelsVisible(true);
  return true;
 }
 return false;
}
window.SWYRL_ENGINE_VR_EDITOR=Object.freeze({
 diagnose:()=>({active:!!se181XR.session&&renderer.xr.isPresenting,
  mode:se192.mode,movementFrames:se192.inputSamples,
  beams:se192.beams.length,cursors:se192.cursors.length,signsAnchored:se192.sprites.length,
  paletteVisible:se192.panelVisible,aimRadians:se192.savedAim.slice(),
  controllerHands:se181XR.controllers.map(r=>r.input?.handedness||'unknown'),
  lastAction:se192.lastAction,lastError:se192.lastError}),
 togglePalette:()=>se192PanelsVisible(!se192.panelVisible)
});
