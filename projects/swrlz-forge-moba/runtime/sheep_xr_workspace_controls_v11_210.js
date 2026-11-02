// §E v11.210 · Sheep Tag Quest: independent VR information panels,
// persistent safe head-relative layouts, Play-only controls/diagnostics,
// honest native ability cooldown readout and remappable A/X or stick-click.
// No editor gizmos, game authority, object rotation or Meta OS windows changed.
const se210UI={
 panels:new Map(),held:false,grabbing:null,lastAt:0,lastDraw:0,lastWheelAt:0,
 prefKey:'swyrl.sheep.vr.workspace.v1',binding:'classic',
 haptics:true,holdMs:340,layout:{},storeReads:0,storeWrites:0,
 panelBuilds:0,panelDisposals:0,panelPaints:0,panelHits:0,
 panelSelects:0,panelGrabFrames:0,panelPins:0,sessionRestores:0,
 xrMenus:0,remaps:0,sessionVisible:false,lastError:''
};
const se210Kinds=['camera','build','skills','metrics','controls'];
function se210Active(){
 return se193XRGameActive()&&se195Active()&&!se195.photo&&!se205OverlayActive();
}
function se210ReadPrefs(){
 try{
  const raw=localStorage.getItem(se210UI.prefKey);
  if(!raw)return;
  const data=JSON.parse(raw);
  if(['classic','sticks','hybrid'].includes(data.binding))se210UI.binding=data.binding;
  se210UI.haptics=data.haptics!==false;
  if([280,340,450].includes(data.holdMs))se210UI.holdMs=data.holdMs;
  if(data.layout&&typeof data.layout==='object'){
   for(const kind of se210Kinds){
    const p=data.layout[kind];
    if(p&&Array.isArray(p.offset)&&p.offset.length===3&&
       p.offset.every(v=>Number.isFinite(v)&&Math.abs(v)<3)&&
       Number.isFinite(p.scale))
      se210UI.layout[kind]={offset:p.offset,scale:THREE.MathUtils.clamp(p.scale,.65,1.6),
       follow:!!p.follow,open:p.open===true};
   }
  }
  se210UI.storeReads++;
 }catch(e){se210UI.lastError='Local VR layout storage unavailable';}
}
function se210Persist(){
 try{
  localStorage.setItem(se210UI.prefKey,JSON.stringify({
   binding:se210UI.binding,haptics:se210UI.haptics,
   holdMs:se210UI.holdMs,layout:se210UI.layout
  }));se210UI.storeWrites++;
 }catch(e){se210UI.lastError='VR layout changes are session-only';}
}
se210ReadPrefs();
function se210ApplyProfile(binding){
 if(!['classic','sticks','hybrid'].includes(binding))return false;
 se210UI.binding=binding;
 se210UI.holdMs=binding==='sticks'?280:binding==='hybrid'?450:340;
 se204.holdMs=se210UI.holdMs;
 se210UI.remaps++;se210Persist();return true;
}
se204.holdMs=se210UI.holdMs;
function se210Held(record,side){
 const selected=se210UI.binding;
 const index=selected==='sticks'?3:(selected==='hybrid'&&side==='left'?3:4);
 return !!se192Pressed(record,index);
}
const se210OldHaptic=se204Haptic;
se204Haptic=function(record){
 if(se210UI.haptics)return se210OldHaptic(record);
};
function se210SetHaptic(enabled){
 se210UI.haptics=!!enabled;se210Persist();
}
function se210StatusSkill(id){
 const session=stSession,u=session?.units?.find(u=>u.id===session.controlledId);
 const native=u&&session?.archive?stArchiveStatus(u):null;
 if(!id)return {label:'NONE',remaining:0,ready:false};
 if(id==='split'){
  if(!session?.rules?.split)return {label:'RULE LOCKED',remaining:0,ready:false};
  if(native&&!native.splitUnlocked)
   return {label:'LV '+(session.rules.splitUnlock||'?')+' UNLOCK',remaining:0,ready:false};
  const seconds=native?.splitCooldownRemaining??0;
  return seconds>0?{label:Math.ceil(seconds)+'s RECHARGE',remaining:seconds,ready:false}:
   {label:'READY',remaining:0,ready:true};
 }
 if(id==='totem'){
  if(!session?.rules?.totems)return {label:'RULE LOCKED',remaining:0,ready:false};
  if(native?.totemUsed&&session.rules.totemLimit==='once')
   return {label:'USED THIS MATCH',remaining:0,ready:false};
  const seconds=native?.totemCooldownRemaining??0;
  if(seconds>0)return {label:Math.ceil(seconds)+'s RECHARGE',remaining:seconds,ready:false};
  if(native&&!native.canTotem)return {label:'NEED OWN 9-HOUSE CLUSTER',remaining:0,ready:false};
  return {label:'READY',remaining:0,ready:true};
 }
 return {label:'UNAVAILABLE',remaining:0,ready:false};
}
const se210OldSkillLabel=se209OptionStatus;
se209OptionStatus=function(panel,entry){
 if(panel?.type==='skill'&&entry?.id)return se210StatusSkill(entry.id).label;
 return se210OldSkillLabel(panel,entry);
};
function se210Pose(){
 const pose=se191XRHeadPose();if(!pose)return null;
 const forward=pose.forward.clone();forward.y=0;
 if(forward.lengthSq()<.0001)forward.set(0,0,-1);
 forward.normalize();
 const right=new THREE.Vector3().crossVectors(forward,new THREE.Vector3(0,1,0)).normalize();
 return {eye:pose.eye,forward,right,up:new THREE.Vector3(0,1,0)};
}
const se210SavedOffset=(kind)=>{
 const defaults={camera:[-.65,.14,1.15],build:[.65,.1,1.15],
  skills:[-.65,-.3,1.12],metrics:[.65,-.3,1.12],
  controls:[0,.28,1.1]};
 return se210UI.layout[kind]?.offset||defaults[kind]||[0,0,1.15];
};
function se210Place(panel,pose){
 if(!pose)return;
 const off=se210SavedOffset(panel.kind);
 panel.root.position.copy(pose.eye)
  .addScaledVector(pose.right,off[0])
  .addScaledVector(pose.up,off[1])
  .addScaledVector(pose.forward,off[2]);
 panel.root.quaternion.setFromRotationMatrix(
  new THREE.Matrix4().lookAt(panel.root.position,pose.eye,pose.up));
 panel.root.updateMatrixWorld(true);
}
function se210SavePanel(panel){
 const pose=se210Pose();if(!pose)return;
 const delta=panel.root.position.clone().sub(pose.eye);
 se210UI.layout[panel.kind]={
  offset:[
   THREE.MathUtils.clamp(delta.dot(pose.right),-2.4,2.4),
   THREE.MathUtils.clamp(delta.dot(pose.up),-1.5,1.5),
   THREE.MathUtils.clamp(delta.dot(pose.forward),.35,2.7)
  ],scale:panel.scale,follow:panel.follow,open:panel.root.visible
 };
 se210Persist();
}
function se210PanelLines(panel){
 const session=stSession,u=session?.units?.find(u=>u.id===session.controlledId);
 const perf=window.SWYRL_ENGINE_QUEST_PERFORMANCE_210.diagnose();
 if(panel.kind==='camera')return [
  'VIEW '+String(se205.profile).toUpperCase(),
  'SHEEP '+(u?.name||session?.controlledId||'NONE').slice(0,22),
  'TACTICAL: overhead / FORWARD: low view',
  'RIGHT STICK: orbit / zoom',
  'CENTER: toggle tactical / forward'
 ];
 if(panel.kind==='build')return [
  'EQUIPPED '+(se204.building||'none').toUpperCase(),
  'GOLD '+(Number(session?.resources?.[session?.controlledId])||0),
  'GRID '+(session?.rules?.buildSnap>=3?'6.0':'3.6')+'m · NO HOUSE ROTATION',
  'A HOLD: house wheel / A TAP: build',
  'Native collisions + sheep lanes enforced'
 ];
 if(panel.kind==='skills'){
  const split=se210StatusSkill('split'),totem=se210StatusSkill('totem');
  return [
   'EQUIPPED '+(se204.skill||'none').toUpperCase(),
   'MIRROR '+split.label,'TOTEM '+totem.label,
   'X HOLD: skill wheel / X TAP: cast',
   'Cooldowns from actual match state'
  ];
 }
 if(panel.kind==='metrics')return [
  'QUEST XR '+perf.fps+' FPS · '+perf.avgFrameMs+'ms',
  'DRAWS '+perf.rendererDrawCalls+' / TRIANGLES '+perf.triangles,
  'TEXTURES '+perf.gpuTextureCount+' / GEOMETRY '+perf.gpuGeometryCount,
  'FOG CPU '+perf.fogUpdateCpuMs+'ms / '+perf.fogSampleCalls+' calls',
  'QUALITY '+perf.cosmeticQuality.toUpperCase()+(perf.autoReduced?' (REDUCED)':''),
  'CENTER: cycle cosmetic quality'
 ];
 return [
  'PROFILE '+se210UI.binding.toUpperCase(),
  'BUILD '+(se210UI.binding==='sticks'?'RIGHT STICK CLICK':'RIGHT A'),
  'SKILL '+(se210UI.binding==='classic'?'LEFT X':'LEFT STICK CLICK'),
  'HOLD '+se210UI.holdMs+'ms · HAPTICS '+(se210UI.haptics?'ON':'OFF'),
  'RIGHT B: full menu / RIGHT GRIP: move panel',
  'LEFT Y: recenter / CENTER: cycle input profile'
 ];
}
function se210CanvasRender(panel){
 if(!panel.root.visible)return;
 const lines=se210PanelLines(panel),key=panel.kind+'|'+lines.join('|');
 if(panel.lastKey===key)return;
 const c=panel.canvas,g=c.getContext('2d');if(!g)return;
 g.clearRect(0,0,c.width,c.height);
 const gradient=g.createLinearGradient(0,0,0,c.height);
 gradient.addColorStop(0,'#102d3b');gradient.addColorStop(1,'#071420');
 g.fillStyle=gradient;g.fillRect(0,0,c.width,c.height);
 g.strokeStyle='#58d7cf';g.lineWidth=4;
 g.strokeRect(6,6,c.width-12,c.height-12);
 g.fillStyle='#8ce9df';g.font='bold 31px sans-serif';
 g.fillText('§E  /  '+panel.kind.toUpperCase(),23,47);
 g.font='22px sans-serif';g.fillStyle='#def6ee';
 lines.forEach((line,i)=>g.fillText(String(line).slice(0,57),23,89+i*35));
 g.fillStyle='#76bbb5';g.font='17px sans-serif';
 g.fillText('TOP LEFT FOLLOW  ·  TOP RIGHT CLOSE',23,318);
 g.fillText('BOTTOM LEFT -  ·  BOTTOM RIGHT +  ·  CENTER ACTION',23,347);
 panel.texture.needsUpdate=true;panel.lastKey=key;se210UI.panelPaints++;
}
function se210PanelCreate(kind){
 if(!se210Kinds.includes(kind))return null;
 let panel=se210UI.panels.get(kind);
 if(panel){panel.root.visible=true;se210SavePanel(panel);return panel;}
 const canvas=document.createElement('canvas');canvas.width=640;canvas.height=384;
 const texture=new THREE.CanvasTexture(canvas);
 texture.colorSpace=THREE.SRGBColorSpace;
 texture.minFilter=THREE.LinearFilter;texture.magFilter=THREE.LinearFilter;
 texture.generateMipmaps=false;
 const root=new THREE.Group();root.name='§E Sheep Tag independent '+kind+' panel';
 root.userData.se210Panel=kind;
 const mesh=new THREE.Mesh(new THREE.PlaneGeometry(.84,.5),
  new THREE.MeshBasicMaterial({map:texture,transparent:true,
   depthTest:false,depthWrite:false,side:THREE.DoubleSide,toneMapped:false}));
 mesh.name='VR spatial '+kind+' interactive surface';
 mesh.userData.se210Panel=kind;mesh.renderOrder=10750;
 mesh.frustumCulled=false;root.add(mesh);
 const rim=new THREE.Mesh(new THREE.PlaneGeometry(.862,.522),
  new THREE.MeshBasicMaterial({color:0x46bfb1,transparent:true,opacity:.32,
   depthTest:false,depthWrite:false,side:THREE.DoubleSide,toneMapped:false}));
 rim.position.z=-.008;rim.renderOrder=10749;root.add(rim);
 const saved=se210UI.layout[kind];
 panel={kind,root,mesh,texture,canvas,lastKey:'',follow:saved?.follow||false,
  pinned:true,scale:saved?.scale||1,grabbing:false,handle:rim};
 root.scale.setScalar(panel.scale);
 se210Place(panel,se210Pose());
 root.visible=true;scene.add(root);
 se210UI.panels.set(kind,panel);se210UI.panelBuilds++;
 se210CanvasRender(panel);se210SavePanel(panel);
 return panel;
}
function se210PanelClose(kind){
 const panel=se210UI.panels.get(kind);if(!panel)return false;
 panel.root.visible=false;panel.grabbing=false;
 se210SavePanel(panel);return true;
}
function se210PanelHit(record){
 if(!se210Active()||se195.visible||se204.wheel)return null;
 const cast=se192Ray(record);if(!cast)return null;
 let best=null;
 for(const panel of se210UI.panels.values()){
  if(!panel.root.visible)continue;
  panel.root.updateMatrixWorld(true);
  const hit=cast.ray.intersectObject(panel.mesh,false)?.[0];
  if(hit&&(!best||hit.distance<best.distance))
   best={panel,point:hit.point,uv:hit.uv,
    distance:hit.distance,ui:'se210:'+panel.kind};
 }
 if(best)se210UI.panelHits++;
 return best;
}
function se210PanelPress(hit){
 if(!hit)return false;
 const panel=hit.panel,uv=hit.uv||{x:.5,y:.5};
 if(uv.y>.79&&uv.x>.78)se210PanelClose(panel.kind);
 else if(uv.y>.79&&uv.x<.22){
  panel.follow=!panel.follow;se210SavePanel(panel);
 }else if(uv.y<.17&&uv.x<.35){
  panel.scale=THREE.MathUtils.clamp(panel.scale-.11,.65,1.6);
  panel.root.scale.setScalar(panel.scale);se210SavePanel(panel);
 }else if(uv.y<.17&&uv.x>.65){
  panel.scale=THREE.MathUtils.clamp(panel.scale+.11,.65,1.6);
  panel.root.scale.setScalar(panel.scale);se210SavePanel(panel);
 }else if(panel.kind==='camera'){
  se205ApplyCamera(se205.profile==='tactical'?'forward':'tactical');
 }else if(panel.kind==='metrics'){
  const names=['auto','balanced','performance','quality'];
  const i=names.indexOf(se210World.mode);
  se210Quality(names[(i+1)%names.length]);
 }else if(panel.kind==='controls'){
  const names=['classic','sticks','hybrid'];
  const i=names.indexOf(se210UI.binding);
  se210ApplyProfile(names[(i+1)%names.length]);
 }
 panel.lastKey='';se210CanvasRender(panel);se210UI.panelSelects++;
 return true;
}
const se210UIOldOptions=se195Options;
se195Options=function(mode=se195.mode,page=se195.page){
 if(mode==='game'&&page==='workspace')return [
  ['workspaceCamera','CAMERA'],['workspaceBuild','BUILD'],
  ['workspaceSkills','SKILLS'],['workspaceMetrics','METRICS'],
  ['workspaceControls','CONTROLS'],['workspaceQuality','QUALITY'],
  ['back','BACK']
 ];
 if(mode==='game'&&page==='bindings')return [
  ['bindClassic','A / X'],['bindSticks','STICK CLICKS'],
  ['bindHybrid','HYBRID'],['toggleHaptic','HAPTICS'],
  ['holdSpeed','HOLD SPEED'],['back','BACK']
 ];
 const opts=se210UIOldOptions(mode,page);
 if(mode==='game'&&page==='more')return [...opts,['workspacePage','WORKSPACE']];
 return opts;
};
const se210UIOldAction=se195HandleAction;
se195HandleAction=function(action,record){
 if(se195.mode==='game'){
  if(action==='workspacePage'){se210UI.xrMenus++;se195Page('workspace');return true;}
  if(action.startsWith('workspace')){
   const kind=action.slice('workspace'.length).toLowerCase();
   if(kind==='quality'){
    se195Page('bindings');return true;
   }
   if(se210Kinds.includes(kind)){
    se210PanelCreate(kind);se195SetVisible(false);return true;
   }
  }
  if(action==='bindClassic'||action==='bindSticks'||action==='bindHybrid'){
   se210ApplyProfile(action==='bindClassic'?'classic':action==='bindSticks'?'sticks':'hybrid');
   return true;
  }
  if(action==='toggleHaptic'){se210SetHaptic(!se210UI.haptics);return true;}
  if(action==='holdSpeed'){
   se210UI.holdMs=se210UI.holdMs===280?340:se210UI.holdMs===340?450:280;
   se204.holdMs=se210UI.holdMs;se210Persist();return true;
  }
 }
 return se210UIOldAction(action,record);
};
const se210UIOldRaycast=se192Raycast;
se192Raycast=function(record){
 const hit=se210PanelHit(record);
 return hit||se210UIOldRaycast(record);
};
const se210UIOldSelect=se192Select;
se192Select=function(record){
 const hit=se210PanelHit(record);
 if(hit){se210PanelPress(hit);return;}
 return se210UIOldSelect(record);
};
const se210UIOldRayRender=se192RenderRay;
se192RenderRay=function(record,hit){
 const panelHit=se210PanelHit(record);
 const result=se210UIOldRayRender(record,panelHit||hit);
 if(panelHit&&record?.se192){
  const cast=se192Ray(record);
  if(cast){
   const target=panelHit.point.clone().addScaledVector(cast.direction,-.015);
   record.se192.dot.position.copy(target);
   record.se192.dot.visible=true;
   for(const node of record.se192.dot.children)node.renderOrder=10900;
   record.se192.beam.scale.z=panelHit.distance;
  }
 }
 return result;
};
function se210PanelGrabFrame(){
 const active=se210Active()&&!se195.visible&&!se204.wheel;
 const record=se192InputRecord('right'),down=!!record&&se192Pressed(record,1);
 const now=performance.now(),dt=Math.min(.05,Math.max(0,(now-(se210UI.lastAt||now))/1000));
 se210UI.lastAt=now;
 if(!active){
  if(se210UI.grabbing)se210PanelRelease(false);
  se210UI.held=down;return;
 }
 if(down&&!se210UI.held){
  const hit=se210PanelHit(record);
  if(hit?.panel?.root){
   const panel=hit.panel,hand=record.controller;
   hand?.updateMatrixWorld(true);
   if(hand){
    const pos=hand.getWorldPosition(new THREE.Vector3());
    const rotation=hand.getWorldQuaternion(new THREE.Quaternion());
    panel.grabOffset=panel.root.position.clone().sub(pos).applyQuaternion(rotation.clone().invert());
    panel.grabRotation=rotation.clone().invert().multiply(panel.root.quaternion);
    panel.grabbing=true;panel.follow=false;se210UI.grabbing={panel,record};
   }
  }
 }else if(!down&&se210UI.held&&se210UI.grabbing)se210PanelRelease(true);
 se210UI.held=down;
 const grab=se210UI.grabbing;
 if(grab&&down){
  const {panel,record:r}=grab,hand=r.controller;
  hand.updateMatrixWorld(true);
  const pos=hand.getWorldPosition(new THREE.Vector3());
  const rotation=hand.getWorldQuaternion(new THREE.Quaternion());
  panel.root.position.copy(panel.grabOffset.clone().applyQuaternion(rotation).add(pos));
  panel.root.quaternion.copy(rotation).multiply(panel.grabRotation);
  panel.root.updateMatrixWorld(true);
  const axes=r.input?.gamepad?.axes||[],y=Number(axes.at(-1))||0;
  if(Math.abs(y)>.25){
   panel.scale=THREE.MathUtils.clamp(panel.scale-y*dt*.65,.65,1.6);
   panel.root.scale.setScalar(panel.scale);
  }
  se210UI.panelGrabFrames++;
 }
}
function se210PanelRelease(save=true){
 const current=se210UI.grabbing;if(!current)return;
 current.panel.grabbing=false;
 se210UI.grabbing=null;
 if(save){se210UI.panelPins++;se210SavePanel(current.panel);}
}
const se210UIOldStick=se192Stick;
se192Stick=function(record){
 if(se210UI.grabbing&&record===se192InputRecord('right'))return {x:0,y:0};
 return se210UIOldStick(record);
};
function se210PanelFrame(){
 if(!se210Active())return;
 const now=performance.now();
 if(now-se210UI.lastDraw>=960){
  se210UI.lastDraw=now;
  const pose=se210Pose();
  for(const panel of se210UI.panels.values()){
   if(!panel.root.visible)continue;
   if(panel.follow&&!panel.grabbing)se210Place(panel,pose);
   se210CanvasRender(panel);
  }
  if(se204.wheel?.root.visible)se209RefreshWheel(se204.wheel);
 }
}
const se210UIOldFrame=se193XRFrame;
se193XRFrame=function(){
 const result=se210UIOldFrame();
 se210PanelGrabFrame();se210PanelFrame();
 return result;
};
function se210UIDispose(){
 se210PanelRelease(false);
 for(const panel of se210UI.panels.values()){
  scene.remove(panel.root);
  panel.root.traverse(node=>{
   node.geometry?.dispose?.();
   if(Array.isArray(node.material))node.material.forEach(m=>m?.dispose?.());
   else node.material?.dispose?.();
  });
  panel.texture.dispose();se210UI.panelDisposals++;
 }
 se210UI.panels.clear();se210UI.held=false;se210UI.lastAt=0;
}
const se210UIOldCleanup=se193XRCleanup;
se193XRCleanup=function(){
 se210UIDispose();return se210UIOldCleanup();
};
const se210UIOldStart=se193XRStart;
se193XRStart=function(){
 se210UIDispose();se204.holdMs=se210UI.holdMs;
 const result=se210UIOldStart();
 // Restore panel *offsets relative to the present headset*, not raw
 // world coordinates from a previous Guardian/origin.
 for(const kind of se210Kinds)
  if(se210UI.layout[kind]?.open)se210PanelCreate(kind);
 se210UI.sessionRestores++;
 return result;
};
window.SWYRL_ENGINE_QUEST_WORKSPACE_210=Object.freeze({
 diagnose:()=>({
  panels:[...se210UI.panels].map(([name,p])=>({name,visible:p.root.visible,
   follow:p.follow,pinned:!p.follow,scale:p.scale})),
  bindingProfile:se210UI.binding,holdMs:se210UI.holdMs,
  haptics:se210UI.haptics,storedLayoutCount:Object.keys(se210UI.layout).length,
  storageWrites:se210UI.storeWrites,panelBuilds:se210UI.panelBuilds,
  panelPaints:se210UI.panelPaints,panelDisposals:se210UI.panelDisposals,
  panelHits:se210UI.panelHits,panelSelections:se210UI.panelSelects,
  panelGripFrames:se210UI.panelGrabFrames,
  realMirrorCooldown:se210StatusSkill('split'),
  realTotemCooldown:se210StatusSkill('totem'),
  editorControlsUntouched:true,lastError:se210UI.lastError
 }),
 openPanel:se210PanelCreate,setProfile:se210ApplyProfile
});
