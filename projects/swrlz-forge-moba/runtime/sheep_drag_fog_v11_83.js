// A single owner for a skill-to-meadow drag; construction keeps native orders.
const stBuildDrag={pointer:null,button:null,session:null,kind:null,x:0,y:0,startX:0,startY:0,moved:false,lastResult:null};
function stBuildDragReset(reason='released'){
 const id=stBuildDrag.pointer,button=stBuildDrag.button;
 stBuildDrag.pointer=null;stBuildDrag.button=null;stBuildDrag.session=null;
 if(button?.hasPointerCapture(id))button.releasePointerCapture(id);
 if(id!==null){stTouchPlacement.touchPointers.delete(id);stTouchPlacement.blockedPointers.delete(id);if(stTouchPlacement.gesture?.id===id)stTouchPlacementReset(reason);}
}
function stBuildDragActive(){return stBuildDrag.pointer!==null&&stBuildDrag.session===stSession&&stTouchPlacementEnabled()&&stTouchPlacement.gesture?.id===stBuildDrag.pointer;}
function stBuildDragAim(event){
 stBuildDrag.x=event.clientX;stBuildDrag.y=event.clientY;
 stBuildDrag.moved ||= Math.hypot(event.clientX-stBuildDrag.startX,event.clientY-stBuildDrag.startY)>8;
 const gesture=stTouchPlacement.gesture;if(!gesture)return;
 gesture.x=event.clientX;gesture.y=event.clientY;
 stTouchPlacementContext(event);
 const point=stTouchPlacementGround(event.clientX,event.clientY);if(point)stUiPlacePreview(point);
}
window.addEventListener('pointerdown',event=>{
 if(stBuildDrag.pointer!==null&&!stBuildDragActive())stBuildDragReset('mode changed');
 const button=event.target?.closest?.('button[data-st-skill]'),kind=button?.dataset.stSkill;
 if(!stSession||stSession.simulate||!stUi.shown||paused||stSession.winner||!button||button.disabled||!kind?.startsWith('st-')||event.button!==0)return;
 event.preventDefault();event.stopImmediatePropagation();
 if(stBuildDrag.pointer!==null)return;
 if(stUi.build!==kind)stUiChooseBuild(kind);
 if(!stTouchPlacementEnabled())return;
 Object.assign(stBuildDrag,{pointer:event.pointerId,button,session:stSession,kind,x:event.clientX,y:event.clientY,startX:event.clientX,startY:event.clientY,moved:false});
 stTouchPlacement.blockedPointers.delete(event.pointerId);
 stTouchPlacement.gesture={id:event.pointerId,x:event.clientX,y:event.clientY,session:stSession,kind};
 button.setPointerCapture(event.pointerId);stBuildDragAim(event);
 stUiFeedback('Drag the house onto the meadow, then release to build.');
},true);
window.addEventListener('pointermove',event=>{
 if(event.pointerId!==stBuildDrag.pointer)return;
 event.preventDefault();event.stopImmediatePropagation();
 if(!stBuildDragActive()){stBuildDragReset('drag unavailable');return;}
 stBuildDragAim(event);
},true);
window.addEventListener('pointerup',event=>{
 if(event.pointerId!==stBuildDrag.pointer)return;
 event.preventDefault();event.stopImmediatePropagation();
 try{
  if(!stBuildDragActive())return;
  stBuildDragAim(event);
  if(stBuildDrag.moved&&stTouchPlacement.valid)stUiOrderAt(event.clientX,event.clientY);
  else if(stBuildDrag.moved)stUiFeedback('Drop on clear meadow ground to build.',true);
  else stUiFeedback('Drag on the meadow and release to build.');
 }finally{stBuildDragReset('skill drag released');if(stUi.build)stTouchPlacementHide(null);stRefreshHUD(true);}
},true);
for(const type of ['pointercancel','lostpointercapture'])window.addEventListener(type,event=>{if(event.pointerId===stBuildDrag.pointer){stBuildDragReset(type);stTouchPlacementHide(null);}},true);
for(const type of ['blur','pagehide','resize'])window.addEventListener(type,()=>stBuildDragReset(type));
document.addEventListener('visibilitychange',()=>{if(document.hidden)stBuildDragReset('document hidden');});
const stDragInstallBase=stInstallUI;stInstallUI=function(){stDragInstallBase();for(const [id] of stUiBuildButtons){const b=$(id);if(b.dataset.dragReady)continue;b.dataset.dragReady='true';b.addEventListener('click',event=>{if(event.detail>0){event.preventDefault();event.stopImmediatePropagation();}},true);b.title='Drag to place · release to build';}};
// Empty ground taps never generate a movement order. Exact visible geometry
// still selects houses/units and supports native rescue/attack actions.
const stDragOrderBase=stUiOrderAt;
stUiOrderAt=function(x,y){
 if(!stSession||stSession.simulate||stUi.build)return stDragOrderBase(x,y);
 if(paused||stSession.winner)return;
 const state=stUiView(),hit=stTouchVisibleEntity(x,y,state),entity=hit?.entity;
 stTouchSelectionReset('joystick movement');
 if(!entity){stUiFeedback('Use the left joystick to move. Drag the meadow to pan.');return;}
 if(state.role==='wolf'&&(entity.kind==='sheep'||entity.kind.startsWith('st-'))){stUiCommand('select',{id:state.controlledId});stUiCommand('attack',{id:entity.id});}
 else if(state.role==='sheep'&&entity.captured&&entity.id!==state.controlledId){stUiCommand('select',{id:state.controlledId});stUiCommand('rescue',{id:entity.id});}
 else {stUi.buildingId=hit.building?entity.id:null;stUiCommand('select',{id:entity.id});}
};
const stDragCommandBase=stUiCommand;
stUiCommand=function(action,payload={}){
 const result=stDragCommandBase(action,payload);
 if(action==='build'){
  stBuildDrag.lastResult={ok:!!result?.ok,reason:result?.reason||'',kind:payload.kind,x:payload.x,z:payload.z};
  // A held thumb must not replace this construction order on the next frame.
  if(result?.ok){stMobileReset('construction accepted');stUiFeedback('Building ordered. Your sheep will approach the site.');}
 }
 return result;
};
const stDragResetStickBase=stMobileReset;stMobileReset=function(reason){const id=stMobile.pointer;stDragResetStickBase(reason);const stick=$('stMoveStick');if(id!==null&&stick?.hasPointerCapture(id))stick.releasePointerCapture(id);};
let stDragPreviewAt=-1;
const stDragHudBase=stRefreshHUD;
stRefreshHUD=function(...args){
 const result=stDragHudBase(...args);if(!stSession||!stUi.shown)return result;
 if(stBuildDrag.pointer!==null&&!stBuildDragActive())stBuildDragReset('session or mode changed');
 // Gold and site occupancy can change while the aiming finger is stationary.
 if(stUi.build&&stUi.placementPoint&&(args[0]||stSession.elapsed>=stDragPreviewAt)){
  stDragPreviewAt=stSession.elapsed+.1;stUiPlacePreview(stUi.placementPoint.clone());
 }
 stUiText('stTip',stUi.build?'Drag a house above your finger; release on green ground to build.':'Joystick to move · drag a house icon to build · drag meadow to pan');
 return result;
};
const stDragDisposeBase=stDisposeUI;stDisposeUI=function(){stBuildDragReset('Stop');stDragPreviewAt=-1;return stDragDisposeBase();};
// Cosmetic mask only: the native visibility arrays, sight ranges, bot knowledge
// and enemy filtering are unchanged. Paint analytic feathered circles at 4x
// the logical grid resolution, at most 10 Hz, with linear GPU sampling.
function stSoftFogCircle(ctx,unit,range,f){
 const scale=f.canvas.width/(f.extent*2),x=(unit.pos.x+f.extent)*scale,y=(unit.pos.z+f.extent)*scale,r=range*scale;
 const gradient=ctx.createRadialGradient(x,y,Math.max(0,r-f.feather*scale),x,y,r);
 gradient.addColorStop(0,'rgba(255,255,255,1)');gradient.addColorStop(1,'rgba(255,255,255,0)');
 ctx.fillStyle=gradient;ctx.beginPath();ctx.arc(x,y,r,0,Math.PI*2);ctx.fill();
}
function stSoftFogPaint(s){
 const f=s.fog;if(!f)return;
 const viewers=s.units.filter(u=>u.kind===s.role&&!u.captured&&!u.isIllusion&&(s.rules.fogMode!=='solo'||u.id===s.controlledId));
 const range=(s.role==='wolf'?s.rules.wolfVision:s.rules.sheepVision)*(s.archive?.visionMultiplier??1),ctx=f.canvas.getContext('2d'),memory=f.softMemory.getContext('2d'),size=f.canvas.width;
 for(const unit of viewers)stSoftFogCircle(memory,unit,range,f);
 ctx.globalCompositeOperation='source-over';ctx.globalAlpha=1;ctx.clearRect(0,0,size,size);ctx.fillStyle='rgba(10,21,30,'+(165/255)+')';ctx.fillRect(0,0,size,size);
 ctx.globalCompositeOperation='destination-out';ctx.globalAlpha=85/165;ctx.drawImage(f.softMemory,0,0);ctx.globalAlpha=1;
 for(const unit of viewers)stSoftFogCircle(ctx,unit,range,f);
 ctx.globalCompositeOperation='source-over';f.texture.needsUpdate=true;
}
const stSoftFogCreateBase=stCreateFog;stCreateFog=function(s){
 stSoftFogCreateBase(s);const f=s.fog;if(!f)return;
 f.canvas.width=f.canvas.height=Math.min(1024,f.width*4);f.softMemory=document.createElement('canvas');f.softMemory.width=f.softMemory.height=f.canvas.width;f.feather=1.5;
 f.texture.magFilter=THREE.LinearFilter;f.texture.minFilter=THREE.LinearFilter;f.texture.generateMipmaps=false;
};
const stDragStatusBase=stUiStatus;stUiStatus=function(){const f=stSession?.fog,result=stDragStatusBase();return {...result,buildingSelection:{...result.buildingSelection,mode:'visible-tap'},buildDrag:{active:stBuildDragActive(),pointerId:stBuildDrag.pointer,lastResult:stBuildDrag.lastResult},movement:'joystick',fogDisplay:f?{resolution:f.canvas.width,logicalWidth:f.width,feather:f.feather,linear:f.texture.magFilter===THREE.LinearFilter}:null};};
