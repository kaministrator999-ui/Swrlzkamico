// §E v11.193 candidate — native Quest Sheep Tag menu, strategic camera and capture.
// Single existing Three/WebXR renderer; never persists gameplay objects into authored scenes.
// Browser/mobile Sheep Tag remains owned by st140Menu, stUi and stCommand.
const se193={
 kind:'',page:'main',menuDismissed:false,editorCaptureOpen:false,panel:null,buttons:[],textures:[],panelOpen:true,
 follow:true,angle:0,zoom:1,focus:new THREE.Vector3(),ready:false,lastFrame:0,
 held:new Map(),previewAt:0,lastAction:'',lastError:'',capture:null,captureCount:0
};
function se193XRMenuActive(){
 if(currentProject?.kind!=='sheep-tag'||stSession||se193.menuDismissed)return false;
 return !!st140Menu?.open||!!seLevels?.playingMenu||
  (seLevelsCurrent()?.role==='menu'&&seLevelsOwns());
}
function se193XRGameActive(){
 return currentProject?.kind==='sheep-tag'&&!!stSession&&!stSession.simulate;
}
function se193XRKind(){
 return se193XRMenuActive()?'menu':se193XRGameActive()?'game':
  se193.editorCaptureOpen?'editor-capture':'';
}
function se193XRDisposePanel(){
 if(se193.panel){
  scene.remove(se193.panel);
  // Dispose headings, backplates and buttons, not just clickable controls.
  se193.panel.traverse(o=>{
   if(o.isMesh){o.geometry?.dispose();
    if(Array.isArray(o.material))o.material.forEach(m=>m.dispose());
    else o.material?.dispose();}
  });
 }
 for(const t of se193.textures)t.dispose();
 se193.panel=null;se193.buttons=[];se193.textures=[];
}
function se193XRPanelLine(text,highlight=false){
 const canvas=document.createElement('canvas');
 canvas.width=768;canvas.height=140;
 const ctx=canvas.getContext('2d');if(!ctx)return null;
 ctx.fillStyle=highlight?'#165e63':'#102638';ctx.fillRect(0,0,768,140);
 ctx.strokeStyle=highlight?'#9bfce2':'#416b7d';ctx.lineWidth=7;
 ctx.strokeRect(4,4,760,132);
 ctx.textBaseline='middle';ctx.textAlign='center';
 ctx.fillStyle='#edfff9';ctx.font=highlight?'bold 53px sans-serif':'bold 45px sans-serif';
 ctx.fillText(text,384,72,724);
 const tex=new THREE.CanvasTexture(canvas);tex.colorSpace=THREE.SRGBColorSpace;
 se193.textures.push(tex);return tex;
}
function se193XRPanelFor(kind){
 se193XRDisposePanel();
 if(!kind)return;
 const entries=kind==='editor-capture'?
  [['heading','§E · VR CAPTURE'],['capture','CLEAN SCENE PNG'],
   ['debug','DEBUG PNG + JSON'],['stereo','STEREO 3D PNG'],['back','← EDITOR']]:
  kind==='menu'?
  se193.page==='help'?
  [['heading','QUEST CONTROLS'],['info','TRIGGER · SELECT / ORDER'],['info','X · TOOLS   A · BUILD'],
   ['info','Y · RECENTER   B · CANCEL'],['back','← BACK']]:
  [['heading','SHEEP TAG · VR'],['start','▶ START GAME'],['editor','MAP EDITOR'],
   ['help','VR CONTROLS'],['capture','📷 SCREENSHOT'],['exit','EXIT VR']]:
  se193.page==='build'?
  [['heading','BUILD TOOLS'],['farm','FARM · FREE'],['income','INCOME FARM'],['fort','FORTIFIED FARM'],['back','← BACK']]:
  se193.page==='capture'?
  [['heading','VR CAPTURE STUDIO'],['capture','CLEAN IMAGE'],['debug','DEBUG + DATA'],['stereo','STEREO 3D'],['back','← BACK']]:
  se193.page==='session'?
  [['heading','GAME SESSION'],['pause','PAUSE / RESUME'],['restart','RESTART ROUND'],
   ['stop','STOP GAME'],['back','← BACK']]:
  [['heading','SHEEP TAG · VR'],['follow','◎ FOLLOW SHEEP'],['free','FREE CAMERA'],
   ['buildMenu','BUILDINGS'],['captureMenu','CAPTURE STUDIO'],['sessionMenu','GAME SESSION'],['exit','EXIT VR']];
 const group=new THREE.Group();group.name='§E · Sheep Tag immersive controls';
 const step=.16,top=(entries.length-1)*step/2;
 // Single low-cost, unlit glass-like backplate keeps the menu readable
 // over both bright meadows and the dark Dragon Den.
 const glass=new THREE.Mesh(new THREE.PlaneGeometry(1.04,entries.length*step+.23),
  new THREE.MeshBasicMaterial({color:0x071a2c,transparent:true,opacity:.88,
   depthTest:false,depthWrite:false,side:THREE.DoubleSide,toneMapped:false}));
 glass.position.z=-.018;glass.renderOrder=10006;group.add(glass);
 const rim=new THREE.Mesh(new THREE.PlaneGeometry(.96,.008),
  new THREE.MeshBasicMaterial({color:0x68e0d2,depthTest:false,depthWrite:false,
   side:THREE.DoubleSide,toneMapped:false}));
 rim.position.set(0,top+.13,.004);rim.renderOrder=10007;group.add(rim);
 for(let i=0;i<entries.length;i++){
  const [action,label]=entries[i],texture=se193XRPanelLine(label,i===0||action==='start');
  if(!texture)continue;
  const mesh=new THREE.Mesh(new THREE.PlaneGeometry(.86,.141),
   new THREE.MeshBasicMaterial({map:texture,transparent:true,side:THREE.DoubleSide,
    depthTest:false,depthWrite:false,toneMapped:false}));
  mesh.name='Sheep VR '+action;mesh.userData.se193Action=action;
  mesh.position.set(0,top-i*step,0);mesh.renderOrder=10008;mesh.frustumCulled=false;
  group.add(mesh);if(action!=='heading'&&action!=='info')se193.buttons.push(mesh);
 }
 scene.add(group);se193.panel=group;se193.panelOpen=true;
 const pose=se191XRHeadPose();
 if(pose){
  const forward=pose.forward.clone();forward.y=0;
  if(forward.lengthSq()<.02)forward.set(0,0,-1);
  forward.normalize();
  const right=new THREE.Vector3().crossVectors(forward,new THREE.Vector3(0,1,0)).normalize();
  group.position.copy(pose.eye).addScaledVector(forward,1.6)
   .addScaledVector(right,.35);
  group.lookAt(pose.eye);
 }
}
function se193XRPanelHit(record,cast=se192Ray(record)){
 if(!se193.panel?.visible||!cast||!se193.buttons.length)return null;
 const hits=cast.ray.intersectObjects(se193.buttons,false);
 if(!hits.length)return null;
 return {ui:'se193:'+hits[0].object.userData.se193Action,
  distance:hits[0].distance,point:hits[0].point};
}
function se193XRHit(record,cast){
 return se193XRPanelHit(record,cast);
}
function se193XRGameGround(record){
 const cast=se192Ray(record);if(!cast)return null;
 return cast.ray.ray.intersectPlane(new THREE.Plane(new THREE.Vector3(0,1,0),0),new THREE.Vector3());
}
function se193XRFeedback(result,success){
 const ok=typeof success==='boolean'?success:result?.ok!==false;
 se193.lastAction=ok?(result?.reason||'Command sent'):(result?.reason||'Action blocked');
 if(!ok)se193.lastError=se193.lastAction;
 if(typeof stUiFeedback==='function')stUiFeedback(se193.lastAction,!ok);
}
function se193XRGameSelect(record){
 if(!se193XRGameActive())return false;
 const state=stStatus();
 if(!state||state.winner)return true;
 const ground=se193XRGameGround(record);
 if(stUi.build){
  if(!ground){se193XRFeedback({reason:'Aim at the ground to place a building.'},false);return true;}
  stUiPlacePreview(ground);
  const fit=stUi.placement;
  if(!fit?.ok){se193XRFeedback({reason:fit?.reason||'Blocked building site.'},false);return true;}
  const result=stUiCommand('build',{kind:stUi.build,x:fit.x,z:fit.z});
  se193XRFeedback(result);
  if(result?.ok){stUi.build=null;stUiClearPreview();stRefreshHUD(true);}
  return true;
 }
 const hit=se192Raycast(record);
 const cast=se192Ray(record);
 // Runtime-built farms are session meshes, NOT authored actors. Ray-test both.
 let dynamic=null;
 if(cast){
  const runtime=stSession.buildings.filter(b=>!b.authored&&b.hp>0&&b.mesh?.visible!==false);
  const roots=runtime.map(b=>b.mesh),hits=cast.ray.intersectObjects(roots,true);
  for(const test of hits){
   const building=runtime.find(b=>{
    let node=test.object;
    while(node){if(node===b.mesh)return true;node=node.parent;}
    return false;
   });
   if(building&&(!hit?.object||test.distance<hit.distance)){
    dynamic=building;break;
   }
  }
 }
 const id=dynamic?.id||hit?.object?.userData?.id;
 const entity=id?[...state.units,...state.buildings].find(e=>e.id===id):null;
 if(entity){
  if(state.role==='wolf'&&(entity.kind==='sheep'||entity.kind?.startsWith('st-'))){
   stUiCommand('select',{id:state.controlledId});
   se193XRFeedback(stUiCommand('attack',{id:entity.id}));return true;
  }
  if(state.role==='sheep'&&entity.captured&&entity.id!==state.controlledId){
   stUiCommand('select',{id:state.controlledId});
   se193XRFeedback(stUiCommand('rescue',{id:entity.id}));return true;
  }
  stUi.buildingId=entity.kind?.startsWith('st-')?entity.id:null;
  se193XRFeedback(stUiCommand('select',{id:entity.id}));return true;
 }
 if(ground){
  stUi.buildingId=null;
  stUiCommand('select',{id:state.controlledId});
  se193XRFeedback(stUiCommand('move',{x:ground.x,z:ground.z}));
 }
 return true;
}
function se193XRSnapFollow(){
 se193.follow=true;se193.ready=false;se193.lastAction='Follow sheep';
 if(typeof stUi!=='undefined')stUi.follow=true;
}
function se193XRBuild(kind){
 if(!se193XRGameActive())return;
 stUiChooseBuild(kind);
 se193.lastAction=stUi.build?'Selected '+kind:'Build cancelled';
}
function se193XRAction(action){
 if(action==='start'){
  if(se193XRMenuActive()){
   if(seLevelsCurrent()?.role==='menu'&&seLevelsOwns())seLevelsTransition('',true);
   else st140MenuStart();
  }
  return;
 }
 if(action==='editor'){
  if(seLevels?.playingMenu)seLevelsStopMenu();
  if(st140Menu?.open)st140MenuClose();
  se193.menuDismissed=true;
  se193.lastAction='Returned to native map editor';return;
 }
 if(action==='exit'){void se181XRExit();return;}
 if(action==='editorCapture'){
  se193.editorCaptureOpen=true;se192PanelsVisible(false);
  se193.kind='';return;
 }
 if(action==='pause'){document.getElementById('pauseBtn')?.click();return;}
 if(action==='restart'){document.getElementById('stRestart')?.click();return;}
 if(action==='stop'){document.getElementById('stopBtn')?.click();return;}
 if(action==='back'&&se193.editorCaptureOpen){
  se193.editorCaptureOpen=false;se193XRDisposePanel();se193.kind='';
  se192PanelsVisible(true);return;
 }
 if(action==='buildMenu'||action==='captureMenu'||action==='sessionMenu'||action==='help'||action==='back'){
  se193.page=action==='back'?'main':action==='buildMenu'?'build':
   action==='captureMenu'?'capture':action==='help'?'help':'session';
  se193XRPanelFor(se193.kind);return;
 }
 if(action==='follow'){se193XRSnapFollow();return;}
 if(action==='free'){se193.follow=false;se193.lastAction='Free VR camera';return;}
 if(action==='farm'){se193XRBuild('st-farm');return;}
 if(action==='income'){se193XRBuild('st-income');return;}
 if(action==='fort'){se193XRBuild('st-fort');return;}
 if(action==='capture'||action==='stereo'||action==='debug'){
  se193XRCapture(action==='stereo'?'stereo':action==='debug'?'debug':'clean');return;
 }
}
function se193XRSelect(record){
 if(!se181XR.session||!renderer.xr.isPresenting)return false;
 const panel=se193XRPanelHit(record);
 if(panel){se193XRAction(panel.ui.slice(6));return true;}
 if(se193.editorCaptureOpen)return true; // Modal capture UI blocks editor actor mutations.
 if(se193XRMenuActive())return true; // The 2D title is intentionally not targetable in XR.
 if(se193XRGameActive())return se193XRGameSelect(record);
 return false;
}
function se193XRGameButton(record,button){
 const kind=se193XRKind();if(!kind)return false;
 if(kind==='editor-capture'){
  if(button==='x')se193XRAction('back');
  return true;
 }
 if(button==='x'){
  if(kind==='game'&&se193.panel){
   se193.panelOpen=!se193.panelOpen;se193.panel.visible=se193.panelOpen;
  }
  return true;
 }
 if(button==='a'){
  if(kind==='menu')se193XRAction('start');
  else{
   const order=['st-farm','st-income','st-fort',null],i=order.indexOf(stUi.build);
   const next=order[(i+1)%order.length];
   if(next)se193XRBuild(next);
   else if(stUi.build){stUi.build=null;stUiClearPreview();stRefreshHUD(true);}
  }
  return true;
 }
 return false;
}
function se193XRButtonEdges(){
 for(const record of se181XR.controllers){
  if(!record?.input?.gamepad)continue;
  const side=record.input.handedness|| (record.index===0?'left':'right');
  const held=se192Pressed(record,5),previous=se193.held.get(record.index)||false;
  if(held&&!previous&&se193XRGameActive()){
   if(side==='left')se193XRSnapFollow();
   else if(stUi.build){stUi.build=null;stUiClearPreview();stRefreshHUD(true);}
   else se193.follow=false;
  }
  se193.held.set(record.index,held);
 }
}
function se193XRCameraFrame(dt){
 if(!se193XRGameActive())return;
 const state=stStatus(),unit=state?.units?.find(u=>u.id===state.controlledId);
 if(!unit?.pos)return;
 const head=se191XRHeadPose();if(!head)return;
 if(!se193.ready){
  const forward=head.forward.clone();forward.y=0;
  if(forward.lengthSq()<.001)forward.set(0,0,-1);
  forward.normalize();
  se193.angle=Math.atan2(forward.x,forward.z);
  se193.focus.set(unit.pos[0],0,unit.pos[2]);
  se193.ready=true;
 }
 const l=se192Stick(se192InputRecord('left')),r=se192Stick(se192InputRecord('right'));
 if(Math.abs(l.x)+Math.abs(l.y)>.08){
  se193.follow=false;
  const forwards=new THREE.Vector3(Math.sin(se193.angle),0,Math.cos(se193.angle));
  const right=new THREE.Vector3(forwards.z,0,-forwards.x);
  se193.focus.addScaledVector(right,l.x*dt*18*se193.zoom)
   .addScaledVector(forwards,-l.y*dt*18*se193.zoom);
 }
 se193.angle+=r.x*dt*1.05;se193.zoom=THREE.MathUtils.clamp(se193.zoom+r.y*dt*.65,.7,2.2);
 if(se193.follow){
  const t=Math.min(1,dt*7);
  se193.focus.lerp(new THREE.Vector3(unit.pos[0],0,unit.pos[2]),t);
 }
 const bounds=Number(stRules()?.bounds)||40;
 se193.focus.x=THREE.MathUtils.clamp(se193.focus.x,-bounds,bounds);
 se193.focus.z=THREE.MathUtils.clamp(se193.focus.z,-bounds,bounds);
 const facing=new THREE.Vector3(Math.sin(se193.angle),0,Math.cos(se193.angle));
 // Place the tracked head ABOVE and BEHIND the sheep. Never lock headset rotation.
 const desired=se193.focus.clone().addScaledVector(facing,-24*se193.zoom);
 desired.y=15.5*se193.zoom;
 const delta=desired.sub(head.eye),maxStep=Math.max(.015,dt*46);
 if(delta.length()>maxStep)delta.setLength(maxStep);
 if(delta.lengthSq()>.000004)se192MoveBy(delta.x,delta.y,delta.z);
 // VR uses the XR tracking origin, not stUi's 2D perspectiveCamera.
}
function se193XRDownloadButton(){
 let b=document.getElementById('se193DownloadCapture');
 if(b)return b;
 b=document.createElement('button');b.id='se193DownloadCapture';b.type='button';
 b.textContent='📷 Download VR Capture';b.hidden=true;
 b.onclick=()=>se193XRDownload();
 const bar=document.querySelector('.topbar')||document.body;bar.appendChild(b);
 return b;
}
function se193XRDownload(){
 if(!se193.capture)return false;
 const a=document.createElement('a');
 a.href=se193.capture.url;a.download=se193.capture.filename;
 document.body.appendChild(a);a.click();a.remove();
 if(se193.capture.mode==='debug'){
  const json=document.createElement('a');
  json.href='data:application/json;charset=utf-8,'+encodeURIComponent(JSON.stringify(se193.capture.metadata,null,2));
  json.download=se193.capture.filename.replace(/\.png$/,'.json');
  document.body.appendChild(json);json.click();json.remove();
 }
 return true;
}
function se193XRCapture(mode='clean'){
 if(!se181XR.session||!renderer.xr.isPresenting)return false;
 const width=mode==='stereo'?960:1280,height=mode==='stereo'?540:720;
 const output=document.createElement('canvas');
 output.width=width*(mode==='stereo'?2:1);output.height=height;
 const ctx=output.getContext('2d');if(!ctx){se193.lastError='Capture canvas unavailable';return false;}
 const rt=new THREE.WebGLRenderTarget(width,height,{depthBuffer:true,stencilBuffer:false});
 const oldTarget=renderer.getRenderTarget(),oldEnabled=renderer.xr.enabled;
 const viewport=renderer.getViewport(new THREE.Vector4());
 const scissor=renderer.getScissor(new THREE.Vector4()),scissorTest=renderer.getScissorTest();
 const oldVisibility=[];
 const hide=[se193.panel,se192.panel,se181XR.exitPanel,se191XR.beacon];
 if(mode==='clean'){
  for(const record of se181XR.controllers){hide.push(record.controller,record.se192?.dot);}
  for(const item of hide)if(item){oldVisibility.push([item,item.visible]);item.visible=false;}
 }
 try{
  const xrCamera=renderer.xr.getCamera(perspectiveCamera);
  xrCamera.updateMatrixWorld(true);
  const eyes=mode==='stereo'&&xrCamera.cameras?.length>=2?
   xrCamera.cameras.slice(0,2):[xrCamera];
  const count=mode==='stereo'?2:1;
  for(let i=0;i<count;i++){
   const from=eyes[Math.min(i,eyes.length-1)];
   // Match the headset's vertical projection angle instead of arbitrarily
   // cropping the image to a tight FOV (which looked zoomed in on Quest shots).
   const py=Math.abs(Number(from?.projectionMatrix?.elements?.[5])||1);
   const verticalFov=THREE.MathUtils.clamp(2*Math.atan(1/py)*180/Math.PI,50,112);
   const camera=new THREE.PerspectiveCamera(verticalFov,width/height,.05,2000);
   from.updateMatrixWorld(true);
   camera.position.copy(from.getWorldPosition(new THREE.Vector3()));
   camera.quaternion.copy(from.getWorldQuaternion(new THREE.Quaternion()));
   if(count===2&&eyes.length===1)
    camera.translateX(i===0?-.032:.032);
   camera.updateMatrixWorld(true);
   renderer.xr.enabled=false;renderer.setRenderTarget(rt);
   renderer.setViewport(0,0,width,height);renderer.setScissorTest(false);
   renderer.clear(true,true,true);renderer.render(scene,camera);
   const data=new Uint8Array(width*height*4);
   renderer.readRenderTargetPixels(rt,0,0,width,height,data);
   const image=ctx.createImageData(width,height),stride=width*4;
   for(let row=0;row<height;row++)
    image.data.set(data.subarray((height-1-row)*stride,(height-row)*stride),row*stride);
   ctx.putImageData(image,i*width,0);
  }
  const stamp=new Date().toISOString().replace(/[:.]/g,'-');
  const cameraMode=se193XRGameActive()?(se193.follow?'follow':'free'):'editor';
  se193.capture={url:output.toDataURL('image/png'),
   filename:'sE-VR-'+mode+'-'+stamp+'.png',
   metadata:{schema:'se-vr-debug-v1',mode,cameraMode,
    project:currentProject?.name||'project',selectedActor:selected?.name||null,
    game:se193XRGameActive()?{selectedId:stStatus().selectedId,
     controlledId:stStatus().controlledId,build:stUi.build}:null,
    build:window.SWRLZ_FORGE_BUILD?.version||'unavailable',
    frame:se181XR.frames,controllers:se181XR.tracked.map(t=>({index:t.index,
     handedness:t.handedness,targetRayMode:t.targetRayMode})),
    capturedAt:new Date().toISOString()},mode,number:++se193.captureCount};
  const button=se193XRDownloadButton();button.hidden=false;
  se193.lastAction='Capture ready · Download VR Capture when you exit immersive mode';
  // Preserve the captured image even if Quest blocks automatic XR downloads.
  return true;
 }catch(e){se193.lastError='VR capture: '+String(e?.message||e).slice(0,150);return false;}
 finally{
  for(const [item,visible] of oldVisibility)item.visible=visible;
  renderer.setRenderTarget(oldTarget);renderer.setViewport(viewport);
  renderer.setScissor(scissor);renderer.setScissorTest(scissorTest);
  renderer.xr.enabled=oldEnabled;rt.dispose();
 }
}
function se193XRFrame(){
 if(!se181XR.session||!renderer.xr.isPresenting)return;
 const now=performance.now(),dt=Math.min(.05,Math.max(0,(now-(se193.lastFrame||now))/1000));
 se193.lastFrame=now;
 const kind=se193XRKind();
 if(kind!==se193.kind){
  se193.kind=kind;se193.page='main';se193.ready=false;se193.held.clear();
  se193XRPanelFor(kind);
  if(kind)se192PanelsVisible(false);
  else se192PanelsVisible(true);
 }
 if(kind==='game'){
  se193XRButtonEdges();se193XRCameraFrame(dt);
  if(stUi.build&&now-se193.previewAt>100){
   const right=se192InputRecord('right'),point=right&&se193XRGameGround(right);
   if(point)stUiPlacePreview(point);
   se193.previewAt=now;
  }
 }
}
function se193XRStart(){
 se193.kind='';se193.ready=false;se193.follow=true;
 se193.menuDismissed=false;se193.editorCaptureOpen=false;
 se193.lastFrame=performance.now();
 se193.held.clear();se193XRDownloadButton();
}
function se193XRCleanup(){
 se193XRDisposePanel();se193.kind='';se193.ready=false;
 se193.editorCaptureOpen=false;
 se193.lastFrame=0;se193.held.clear();
 // Captures intentionally survive leaving XR so Quest can download them in 2D.
}
window.SWYRL_ENGINE_SHEEP_VR=Object.freeze({
 diagnose:()=>({active:!!se181XR.session&&renderer.xr.isPresenting,
  mode:se193.kind,follow:se193.follow,zoom:se193.zoom,
  menuVisible:!!se193.panel?.visible,selectedBuild:typeof stUi!=='undefined'?stUi.build:null,
  captureReady:!!se193.capture,lastAction:se193.lastAction,lastError:se193.lastError}),
 capture:se193XRCapture,download:se193XRDownload,snapToSheep:se193XRSnapFollow
});