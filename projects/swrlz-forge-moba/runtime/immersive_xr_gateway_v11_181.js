// §E v11.181 — actual immersive WebXR on the EXISTING main §E renderer.
// Separate Model Atelier renderer is not silently repurposed. Quest 2 acceptance pending.
const se181XR={
 session:null,busy:false,supported:null,capabilityChecked:false,
 controllers:[],exitPanel:null,exitSurface:null,exitTexture:null,frames:0,
 viewerAnchored:false,previous:null,lastError:'',selectedCount:0,tracked:[],
 button:null,status:null
};
function se181XRRead(){
 return {mode:renderer.xr.isPresenting?'immersive-vr':'browser-2d',
  active:!!se181XR.session&&renderer.xr.isPresenting,
  supported:se181XR.supported,capabilityChecked:se181XR.capabilityChecked,
  rendererShared:renderer.domElement===$('viewport'),
  nativeSceneShared:true,
  trackedControllers:se181XR.tracked.map(x=>({...x})),
  nativeSelectionCount:se181XR.selectedCount,
  modelAtelierXR:false,sculptXR:false,locomotionXR:false,
  controllerRays:se181XR.controllers.length,lastError:se181XR.lastError};
}
function se181XRNote(message,bad=false){
 if(se181XR.status){se181XR.status.textContent=message;se181XR.status.dataset.error=String(bad);}
}
function se181XRLabel(){
 const b=se181XR.button;if(!b)return;
 b.disabled=se181XR.busy||(!se181XR.session&&(se181XR.capabilityChecked&&se181XR.supported===false));
 b.textContent=se181XR.session?'🥽 Exit VR':'🥽 Enter VR';
 b.setAttribute('aria-pressed',String(!!se181XR.session));
 b.title=se181XR.session?'Leave immersive §E':'Step inside the current §E game editor scene';
}
async function se181XRCheckSupport(){
 if(se181XR.capabilityChecked)return se181XR.supported;
 const xr=navigator.xr;
 if(!xr||typeof xr.isSessionSupported!=='function'||typeof xr.requestSession!=='function'){
  se181XR.capabilityChecked=true;se181XR.supported=false;
  se181XRNote('WebXR immersive VR is unavailable. Open §E in Meta Quest Browser over HTTPS.',true);
  se181XRLabel();return false;
 }
 try{se181XR.supported=!!await xr.isSessionSupported('immersive-vr');}
 catch(e){se181XR.supported=false;se181XR.lastError=String(e?.message||e).slice(0,180);}
 se181XR.capabilityChecked=true;se181XRLabel();
 if(!se181XR.supported)se181XRNote('This browser does not currently offer immersive VR. Normal 2D §E remains available.',true);
 else se181XRNote('WebXR ready · tap Enter VR to step into the 3D scene.');
 return se181XR.supported;
}
function se181XRActiveModel(){
 const panel=document.getElementById('modelAtelierPanel');
 return !!panel&&!panel.hidden&&getComputedStyle(panel).display!=='none';
}
function se181XRMakeExitPanel(){
 const c=document.createElement('canvas');c.width=640;c.height=220;
 const g=c.getContext('2d');
 if(!g)return;
 g.fillStyle='rgba(9,24,40,0.92)';g.fillRect(0,0,c.width,c.height);
 g.strokeStyle='#9cf0d5';g.lineWidth=10;g.strokeRect(5,5,c.width-10,c.height-10);
 g.fillStyle='#f2faff';g.textAlign='center';g.font='bold 70px sans-serif';g.fillText('EXIT VR',320,116);
 g.font='30px sans-serif';g.fillText('Aim + trigger · or Quest menu',320,169);
 const texture=new THREE.CanvasTexture(c);texture.colorSpace=THREE.SRGBColorSpace;
 const surface=new THREE.Mesh(new THREE.PlaneGeometry(.69,.24),
   new THREE.MeshBasicMaterial({map:texture,transparent:true,depthTest:false,side:THREE.DoubleSide}));
 surface.name='§E Exit VR';surface.renderOrder=9999;surface.visible=false;
 scene.add(surface);se181XR.exitPanel=surface;se181XR.exitSurface=surface;
 se181XR.exitTexture=texture;se181XR.viewerAnchored=false;
}
function se181XRMakeController(index){
 const controller=renderer.xr.getController(index);
 const geo=new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(0,0,0),new THREE.Vector3(0,0,-1)]);
 const mat=new THREE.LineBasicMaterial({color:index===0?0x65f8fc:0xffd77b,transparent:true,opacity:.95,depthTest:false});
 const ray=new THREE.Line(geo,mat);ray.name='§E XR target ray';ray.scale.z=10;ray.renderOrder=9998;
 controller.add(ray);scene.add(controller);
 const record={index,controller,ray,input:null};
 const onConnected=e=>{
  record.input=e.data||null;
  se181XR.tracked[index]={index,handedness:record.input?.handedness||'unknown',
    targetRayMode:record.input?.targetRayMode||'unknown',
    profiles:Array.isArray(record.input?.profiles)?record.input.profiles.slice(0,6):[]};
 };
 const onDisconnected=()=>{record.input=null;delete se181XR.tracked[index];};
 const onSelect=()=>{if(se181XR.session&&renderer.xr.isPresenting)se181XRSelect(record);};
 controller.addEventListener('connected',onConnected);
 controller.addEventListener('disconnected',onDisconnected);
 controller.addEventListener('selectstart',onSelect);
 record.detach=()=>{
  controller.removeEventListener('connected',onConnected);
  controller.removeEventListener('disconnected',onDisconnected);
  controller.removeEventListener('selectstart',onSelect);
  controller.remove(ray);scene.remove(controller);geo.dispose();mat.dispose();
 };
 return record;
}
function se181XRRaycast(record){
 const controller=record.controller;
 controller.updateMatrixWorld(true);
 const origin=new THREE.Vector3().setFromMatrixPosition(controller.matrixWorld);
 const direction=new THREE.Vector3(0,0,-1).transformDirection(controller.matrixWorld);
 const rc=new THREE.Raycaster(origin,direction,.05,24);
 const exit=se181XR.exitSurface;
 if(exit?.visible){
  const hits=rc.intersectObject(exit,false);
  if(hits.length)return {exit:true,distance:hits[0].distance};
 }
 // Only actual native actor objects; never synthetic GUI, effect helper, or rays.
 const roots=Array.isArray(actors)?actors.filter(o=>o?.isObject3D&&o.visible!==false&&
   o.userData?.actorType!=='ground'&&o.userData?.type!=='ground'):[];
 if(!roots.length)return null;
 const hits=rc.intersectObjects(roots,true);
 for(const hit of hits){
  let native=hit.object;
  while(native&&!roots.includes(native))native=native.parent;
  if(!native||native.userData?.actorType==='ground')continue;
  const root=rootGroupFor(native);
  if(root&&root.visible!==false&&root.userData?.actorType!=='ground')
   return {object:root,distance:hit.distance};
 }
 return null;
}
function se181XRSelect(record){
 const hit=se181XRRaycast(record);
 if(!hit)return;
 if(hit.exit){void se181XRExit();return;}
 if(playing||simulating)return; // No synthesized gameplay input.
 try{selectActor(hit.object);se181XR.selectedCount++;}
 catch(e){se181XR.lastError='XR target select: '+String(e?.message||e).slice(0,140);}
}
function se181XRRender(){
 if(!se181XR.session||!renderer.xr.isPresenting)return;
 se181XR.frames++;
 if(!se181XR.viewerAnchored&&se181XR.frames>2&&se181XR.exitPanel){
  const c=renderer.xr.getCamera(perspectiveCamera);
  c.updateMatrixWorld(true);
  const eye=c.getWorldPosition(new THREE.Vector3());
  const forward=c.getWorldDirection(new THREE.Vector3());
  forward.y=0;
  if(forward.lengthSq()>.01&&Number.isFinite(eye.y)){
   forward.normalize();
   const right=new THREE.Vector3().crossVectors(forward,new THREE.Vector3(0,1,0)).normalize();
   se181XR.exitPanel.position.copy(eye).addScaledVector(forward,1.45)
     .addScaledVector(right,-.65).add(new THREE.Vector3(0,.26,0));
   se181XR.exitPanel.lookAt(eye);
   se181XR.exitPanel.visible=true;se181XR.viewerAnchored=true;
  }
 }
 // This loop reads tracked poses only; no extra animation frame is created.
 for(const record of se181XR.controllers){
  const hit=se181XRRaycast(record);
  record.ray.scale.z=Math.max(.15,Math.min(hit?.distance||10,24));
  record.ray.material.color.setHex(hit?0xa4ffa1:(record.index===0?0x65f8fc:0xffd77b));
 }
}
function se181XRRelease(){
 for(const record of se181XR.controllers){try{record.detach();}catch(e){console.warn('XR controller cleanup',e);}}
 se181XR.controllers=[];se181XR.tracked=[];
 if(se181XR.exitPanel){
  scene.remove(se181XR.exitPanel);
  se181XR.exitPanel.geometry?.dispose();
  se181XR.exitPanel.material?.dispose();
  se181XR.exitTexture?.dispose();
 }
 se181XR.exitPanel=se181XR.exitSurface=se181XR.exitTexture=null;
 se181XR.viewerAnchored=false;se181XR.frames=0;
 if(se181XR.previous){
  camera=se181XR.previous.camera;
  orbit.enabled=se181XR.previous.orbitEnabled;
  if(se181XR.previous.helper)se181XR.previous.helper.visible=se181XR.previous.helperVisible;
  se181XR.previous=null;
 }
 se181XR.session=null;se181XR.busy=false;
 se181XRLabel();
 se181XRNote('Back to the §E browser workspace. Your scene was preserved.');
 try{resize();}catch(e){console.warn('XR resize recovery',e);}
}
async function se181XRExit(){
 if(!se181XR.session)return false;
 try{await se181XR.session.end();return true;}
 catch(e){se181XR.lastError=String(e?.message||e).slice(0,180);se181XRNote('Could not exit VR: '+se181XR.lastError,true);return false;}
}
async function se181XREnter(){
 if(se181XR.busy||se181XR.session)return false;
 if(se181XRActiveModel()){
  se181XRNote('Close Model Atelier first. This VR doorway opens the main §E scene; immersive sculpting needs its own adapter.',true);
  return false;
 }
 if(!navigator.xr||typeof navigator.xr.requestSession!=='function'){
  se181XRNote('Open in Meta Quest Browser with an XR-capable headset.',true);return false;
 }
 // The request MUST occur synchronously during the user click's activation.
 se181XR.busy=true;se181XRLabel();se181XRNote('Asking Quest to enter the immersive §E scene…');
 let requested=null;
 try{
  renderer.xr.enabled=true;
  renderer.xr.setReferenceSpaceType('local-floor');
  requested=await navigator.xr.requestSession('immersive-vr',{requiredFeatures:['local-floor']});
  requested.addEventListener('end',()=>{if(se181XR.session===requested)se181XRRelease();},{once:true});
  se181XR.previous={camera,orbitEnabled:orbit.enabled,helper:transform.getHelper(),helperVisible:transform.getHelper().visible};
  camera=perspectiveCamera;orbit.enabled=false;
  se181XR.previous.helper.visible=false;
  await renderer.xr.setSession(requested);
  se181XR.session=requested;
  se181XR.controllers=[se181XRMakeController(0),se181XRMakeController(1)];
  se181XRMakeExitPanel();
  try{window.SWYRL_VR_CONTROLS?.attachSession?.(requested);}catch(e){console.warn('XR studio diagnostics adapter',e);}
  se181XR.supported=true;se181XR.capabilityChecked=true;
  se181XR.lastError='';se181XR.busy=false;se181XRLabel();
  se181XRNote('Immersive §E active · trigger selects actors · aim at EXIT VR or use Quest menu.');
  return true;
 }catch(e){
  se181XR.lastError=String(e?.message||e).slice(0,180);
  se181XRNote('Immersive entry failed: '+se181XR.lastError+'. The browser editor is unchanged.',true);
  if(requested){try{await requested.end();}catch(_e){}}
  se181XRRelease();
  return false;
 }
}
function se181XRMount(){
 if(se181XR.button)return;
 const bar=document.querySelector('.topbar');if(!bar)return;
 const b=document.createElement('button');b.type='button';b.id='se181EnterVR';
 b.setAttribute('aria-label','Enter immersive VR using the current §E main scene');
 b.addEventListener('click',()=>{if(se181XR.session)void se181XRExit();else void se181XREnter();});
 const s=document.createElement('span');s.id='se181XRStatus';s.setAttribute('role','status');
 s.textContent='WebXR checking…';
 bar.append(b);bar.append(s);se181XR.button=b;se181XR.status=s;
 se181XRLabel();void se181XRCheckSupport();
}
window.SWYRL_ENGINE_XR=Object.freeze({
 read:se181XRRead,checkSupport:se181XRCheckSupport,
 enter:se181XREnter,exit:se181XRExit
});
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',se181XRMount,{once:true});
else se181XRMount();
window.addEventListener('load',se181XRMount,{once:true});