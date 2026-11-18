/* SE515_SPATIAL_VR_POLISH_START
 * #3 world-anchored immersive menu; #8 native Quest button leader/glow labels.
 * Extends the existing se372 menu placement + se362 controller visual pipeline,
 * without creating any new menu, hit targets, input profile or XR frame loop. */
const se515SpatialPolish=(()=>{
 'use strict';
 const stats={menuAnchors:0,controllerGuides:0,controllerButtons:0};
 const colors=Object.freeze({
  LT:0x7be6d5,RT:0x7be6d5,LG:0x8fc6ff,RG:0x8fc6ff,
  LS:0xbfa9ff,RS:0xbfa9ff,X:0xffd5a0,A:0xffd5a0,
  Y:0xffb5cc,B:0xffb5cc
 });
 const offsets=Object.freeze({
  LT:[-.024,.003,-.019],RT:[.024,.003,-.019],
  LG:[.026,.004,.024],RG:[-.026,.004,.024],
  LS:[-.019,.025,-.012],RS:[.019,.025,-.012],
  X:[-.027,.020,-.003],B:[-.027,.020,-.003],
  Y:[.027,.020,-.003],A:[.027,.020,-.003]
 });
 const css=key=>'#'+(colors[key]||0xb7dcec).toString(16).padStart(6,'0');
 const sceneOwner=()=>!!(se340XR.session&&se340XR.ui&&se340XR.scene&&se340VisibleSession());
 function anchor(record,key,partKey){
  const side=record?.input?.handedness;
  const asset=typeof se361ControllerCache==='undefined'?null:se361ControllerCache.get(side);
  const part=asset?.parts?.find(p=>p.key===partKey);
  if(part){
   const center=se362PartCenter(part);
   if(center)return center.sub(new THREE.Vector3(0,1.79,0)).multiplyScalar(.09);
  }
  return se362FallbackPoint(key);
 }
 function alignGuide(record,visual,key,partKey){
  const h=visual.hints.get(key);if(!h)return;
  const at=anchor(record,key,partKey);
  const label=at.clone().add(new THREE.Vector3(...(offsets[key]||[.02,.02,0])));
  h.mesh.position.copy(label);h.buttonAnchor=at.clone();
  if(h.leader){
   const geom=new THREE.BufferGeometry().setFromPoints([at,label]);
   h.leader.geometry.dispose();h.leader.geometry=geom;
  }
  if(h.glow)h.glow.position.copy(at);
 }
 function newGuideVisual(record,visual){
  if(!visual||visual.se515Attached)return visual;
  visual.se515Attached=true;visual.se515Parts=[];
  for(const [key,partKey] of se362Keys[visual.side]||[]){
   const h=visual.hints.get(key);if(!h)continue;
   const c=colors[key]||0xb7dcec;
   // Old labels were 94 mm wide. Retain the original THREE CanvasTexture
   // resource but reduce the plane and render small, legible typed labels.
   h.mesh.geometry.dispose();h.mesh.geometry=new THREE.PlaneGeometry(.070,.0197);
   h.mesh.renderOrder=9470;h.mesh.frustumCulled=false;
   const line=new THREE.Line(new THREE.BufferGeometry(),
    new THREE.LineBasicMaterial({color:c,transparent:true,opacity:.68,depthTest:false,depthWrite:false}));
   line.name='Quest Touch '+key+' · precise button guide';line.renderOrder=9440;
   line.frustumCulled=false;line.userData.editorOnly=true;
   const glow=new THREE.Mesh(new THREE.SphereGeometry(.006,10,8),
    new THREE.MeshBasicMaterial({color:c,transparent:true,opacity:.28,depthTest:false,depthWrite:false}));
   glow.name='Quest Touch '+key+' · hardware button glow';glow.renderOrder=9450;
   glow.frustumCulled=false;glow.userData.editorOnly=true;
   visual.root.add(line,glow);h.leader=line;h.glow=glow;visual.se515Parts.push(line,glow);
   alignGuide(record,visual,key,partKey);stats.controllerGuides++;
  }
  return visual;
 }
 function updateGuide(record,visual){
  if(!visual?.se515Attached)return;
  for(const [key,partKey] of se362Keys[visual.side]||[])
   alignGuide(record,visual,key,partKey);
 }
 const previousMake=se362MakeVisual;
 se362MakeVisual=function(record){
  const visual=previousMake(record);
  return newGuideVisual(record,visual);
 };
 const previousLoad=se362LoadVisual;
 se362LoadVisual=async function(record,visual){
  await previousLoad(record,visual);
  if(record.se362Visual===visual&&se340XR.session)updateGuide(record,visual);
 };
 const previousDraw=se362DrawHint;
 se362DrawHint=function(hint,title,down=false,expanded=false){
  if(!hint?.se515Label&&hint?.key)hint.se515Label=true;
  const label=String(title||'').replace(/\s+/g,' ').trim().slice(0,34);
  if(hint.text===label&&hint.down===down&&hint.expanded===expanded)return;
  // No alternate menu. The established per-controller CanvasTexture keeps
  // refreshing from the original se362Frame binding interpreter.
  hint.text=label;hint.down=!!down;hint.expanded=!!expanded;
  const c=hint.canvas?.getContext?.('2d');if(!c)return;
  const w=hint.canvas.width,h=hint.canvas.height;
  c.clearRect(0,0,w,h);
  if(!label){hint.mesh.visible=false;return;}
  const hue=css(hint.key);
  c.fillStyle=down?'rgba(27,54,55,.94)':'rgba(13,19,32,.80)';
  c.beginPath();
  if(typeof c.roundRect==='function')c.roundRect(5,12,w-10,h-24,19);
  else c.rect(5,12,w-10,h-24);
  c.fill();
  c.strokeStyle=hue;c.lineWidth=down?6:3;c.stroke();
  c.textAlign='left';c.textBaseline='middle';
  c.fillStyle=hue;c.font='800 31px system-ui,sans-serif';
  c.fillText(hint.key,18,h/2);
  c.fillStyle='#f0f5fa';
  let size=30;
  for(;size>=18;size-=2){
   c.font='650 '+size+'px system-ui,sans-serif';
   if(c.measureText(label).width<=398)break;
  }
  c.fillText(label,103,h/2,398);
  hint.texture.needsUpdate=true;hint.mesh.visible=true;
 };
 const previousFrame=se362Frame;
 se362Frame=function(s){
  const result=previousFrame(s);
  for(const record of s.controllers||[]){
   const visual=record.se362Visual;
   if(!visual?.se515Attached||!visual.root.visible)continue;
   for(const [key] of se362Keys[visual.side]||[]){
    const hint=visual.hints.get(key);
    if(!hint?.leader||!hint.glow)continue;
    const shown=!!hint.mesh.visible&&!!record.gripTracked;
    hint.leader.visible=shown;hint.glow.visible=shown;
    if(!shown)continue;
    hint.leader.material.opacity=hint.down?.95:.68;
    hint.glow.material.opacity=hint.down?.85:.30;
    hint.glow.scale.setScalar(hint.down?1.38:1);
    if(hint.down)stats.controllerButtons++;
   }
  }
  return result;
 };
 const previousDisconnect=se362ControllerDisconnected;
 se362ControllerDisconnected=function(record){
  const visual=record.se362Visual;
  if(visual?.se515Parts){
   for(const part of visual.se515Parts){
    part.geometry.dispose();part.material.dispose();
    part.removeFromParent();
   }
   visual.se515Parts.length=0;
  }
  return previousDisconnect(record);
 };
 // v11.372 used the model's orbit to move the VR panel across the room.
 // Keep its baseline world position fixed; only face the headset, preserving
 // the user's Grip-dragged placement, saved anchor and model-independent menu.
 const previousOrbit=se372MenuOrbit;
 se372MenuOrbit=function(...args){
  const s=se340XR,b=s.se372MenuBase;
  if(!sceneOwner()||!b||s.gesture?.kind==='menu')return;
  s.ui.root.position.copy(b.position);
  if(s.lastViewer?.position?.isVector3&&
    s.lastViewer.position.distanceToSquared(b.position)>.005)
   s.ui.root.lookAt(s.lastViewer.position);
  else s.ui.root.quaternion.copy(b.quaternion);
  s.ui.root.visible=s.paletteVisible;
  s.ui.root.updateWorldMatrix(true,true);
  stats.menuAnchors++;
 };
 const previousDragFinish=se372MenuDragFinish;
 se372MenuDragFinish=function(gesture,commit){
  const s=se340XR,ui=s.ui;
  if(!ui||!commit)return previousDragFinish.apply(this,arguments);
  // Old implementation transformed the dragged panel through the camera
  // orbit quaternion; storing that position would cause lateral movement.
  s.se372MenuBase={
   position:ui.root.position.clone(),quaternion:ui.root.quaternion.clone()
  };
  se372MenuRemember();
  return undefined;
 };
 return Object.freeze({inspect:()=>({
   anchored:!!se340XR.se372MenuBase,
   worldAnchor:se340XR.se372MenuBase?.position?.toArray?.()||null,
   worldMenu:se340XR.ui?.root?.position?.toArray?.()||null,
   activeControllerGuides:stats.controllerGuides,
   menuAnchorFrames:stats.menuAnchors,
   buttonPressFrames:stats.controllerButtons
  }),reposition:record=>{
   const v=record?.se362Visual;
   if(v?.se515Attached)updateGuide(record,v);
  }});
})();
window.SWYRL_ENGINE_VR_SPATIAL_POLISH_515=se515SpatialPolish;
/* SE515_SPATIAL_VR_POLISH_END */
