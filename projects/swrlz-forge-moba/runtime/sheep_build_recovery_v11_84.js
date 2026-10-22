// One placement pointer owner for both skill drags and meadow drags.
const stBuildInput={pointer:null,element:null,session:null,source:null,kind:null,startX:0,startY:0,moved:false,outcome:null,lastReason:'ready',rejections:0};
function stBuildInputOwns(){return !!stSession&&!stSession.simulate&&stUi.shown;}
function stBuildInputCost(kind){const cost=stBuildingConfig(kind)?.cost??0,gold=stSession?.resources[stSession.controlledId]??0;return {cost,gold,ok:gold>=cost};}
function stBuildInputFundsMessage(kind){const f=stBuildInputCost(kind);return (stUiBuildNames[kind]||'Building')+' costs '+f.cost+' gold; you have '+Math.floor(f.gold)+'. Use the free House or wait for income.';}
function stBuildInputFinish(reason,keepTool=false){
 const id=stBuildInput.pointer,element=stBuildInput.element;stBuildInput.pointer=null;stBuildInput.element=null;stBuildInput.session=null;stBuildInput.lastReason=reason;
 stBuildDragReset(reason);stTouchPlacementReset(reason);stTouchPlacement.touchPointers.clear();stTouchPlacement.blockedPointers.clear();stUi.drag=null;
 if(id!==null&&element?.hasPointerCapture(id))element.releasePointerCapture(id);
 if(!keepTool){stUi.build=null;stUiClearPreview();}else stTouchPlacementHide(null);
 stRefreshHUD(true);
}
function stBuildInputReject(reason){stBuildInput.rejections++;stBuildInputFinish(reason);stUiFeedback(reason,true);}
function stBuildInputAim(event){
 const g=stTouchPlacement.gesture;if(!g)return;
 g.x=event.clientX;g.y=event.clientY;stBuildInput.moved ||= Math.hypot(g.x-stBuildInput.startX,g.y-stBuildInput.startY)>8;
 stTouchPlacementContext(event);const point=stTouchPlacementGround(g.x,g.y);if(point)stUiPlacePreview(point);
}
window.addEventListener('pointerdown',event=>{
 if(!stBuildInputOwns())return;
 const button=event.target?.closest?.('button[data-st-skill^="st-"]'),world=event.target===$('viewport');
 if(!button&&!(world&&stUi.build)){
  if(stBuildInput.pointer!==null&&!event.target?.closest?.('#stMoveStick'))stBuildInputFinish('Placement cancelled by another control');return;
 }
 if(event.button!==0||button?.disabled||paused||stSession.winner)return;
 event.preventDefault();event.stopImmediatePropagation();
 const kind=button?.dataset.stSkill||stUi.build;
 stBuildInputFinish('New placement');
 if(!stBuildInputCost(kind).ok){stBuildInputReject(stBuildInputFundsMessage(kind));return;}
 stUiChooseBuild(kind);if(!stTouchPlacementEnabled())return;
 Object.assign(stBuildInput,{pointer:event.pointerId,element:button||$('viewport'),session:stSession,source:button?'skill':'meadow',kind,startX:event.clientX,startY:event.clientY,moved:false,outcome:null});
 stTouchPlacement.gesture={id:event.pointerId,x:event.clientX,y:event.clientY,session:stSession,kind};
 stBuildInput.element.setPointerCapture(event.pointerId);
 if(world)stBuildInputAim(event);else stTouchPlacementHide(null);
 stUiFeedback('Drag onto clear meadow ground; release on green to build.');
},true);
window.addEventListener('pointermove',event=>{
 if(event.pointerId!==stBuildInput.pointer)return;
 event.preventDefault();event.stopImmediatePropagation();
 if(stBuildInput.session!==stSession||!stTouchPlacementEnabled()||event.pointerType==='mouse'&&event.buttons===0){stBuildInputFinish('Placement interrupted');return;}
 stBuildInputAim(event);
},true);
window.addEventListener('pointerup',event=>{
 if(event.pointerId!==stBuildInput.pointer)return;
 event.preventDefault();event.stopImmediatePropagation();
 if(stBuildInput.session!==stSession||!stTouchPlacementEnabled()){stBuildInputFinish('Placement unavailable');return;}
 const source=stBuildInput.source;stBuildInputAim(event);
 if(!stBuildInput.moved&&source==='skill'){stBuildInputFinish('Tool selected',true);stUiFeedback('Drag on the meadow and release to place.');return;}
 if(!stTouchPlacement.valid){stBuildInputReject('Drop on clear meadow ground, away from controls.');return;}
 const fit=stUi.placement;
 if(!fit?.ok){stBuildInputReject(fit?.reason||'That site is blocked. Drag a building icon to try another spot.');return;}
 stBuildInput.outcome=null;stUiOrderAt(event.clientX,event.clientY);
 const outcome=stBuildInput.outcome;
 if(outcome?.ok){stBuildInputFinish('Building accepted');stUiFeedback('Building ordered.');}
 else stBuildInputReject(outcome?.reason||'That site cannot be reached. Choose another clear spot.');
},true);
for(const type of ['pointercancel','lostpointercapture'])window.addEventListener(type,event=>{if(event.pointerId===stBuildInput.pointer)stBuildInputFinish('Placement cancelled');},true);
for(const type of ['blur','resize','pagehide'])window.addEventListener(type,()=>{if(stBuildInput.pointer!==null||stUi.build)stBuildInputFinish('Placement interrupted');});
document.addEventListener('visibilitychange',()=>{if(document.hidden&&(stBuildInput.pointer!==null||stUi.build))stBuildInputFinish('Placement hidden');});
const stRecoverChooseBase=stUiChooseBuild;stUiChooseBuild=function(kind){if(stBuildInputOwns()&&!stBuildInputCost(kind).ok){stBuildInputReject(stBuildInputFundsMessage(kind));return;}return stRecoverChooseBase(kind);};
const stRecoverCommandBase=stUiCommand;stUiCommand=function(action,payload={}){const result=stRecoverCommandBase(action,payload);if(action==='build')stBuildInput.outcome=result;return result;};
const stRecoverHudBase=stRefreshHUD;stRefreshHUD=function(...args){const result=stRecoverHudBase(...args);if(!stSession||!stUi.shown)return result;
 for(const [id,kind] of stUiBuildButtons){const b=$(id),f=stBuildInputCost(kind);b.classList.toggle('st-unaffordable',!f.ok);b.setAttribute('aria-disabled',String(b.disabled||!f.ok));b.title=f.ok?'Drag to place · release to build':stBuildInputFundsMessage(kind);}
 return result;
};
const stRecoverDisposeBase=stDisposeUI;stDisposeUI=function(){stBuildInputFinish('Stop');return stRecoverDisposeBase();};
const stRecoverStatusBase=stUiStatus;stUiStatus=function(){const result=stRecoverStatusBase();return {...result,buildDrag:{...result.buildDrag,active:stBuildInput.pointer!==null,pointerId:stBuildInput.pointer},placementInput:{active:stBuildInput.pointer!==null,source:stBuildInput.source,lastReason:stBuildInput.lastReason,rejections:stBuildInput.rejections},buildAvailability:stSession?Object.fromEntries(stUiBuildButtons.map(([,kind])=>[kind,stBuildInputCost(kind)])):null};};
const stRecoverStyle=document.createElement('style');stRecoverStyle.textContent='.st-unaffordable{filter:saturate(.3);opacity:.58}#stUpperRoute,#stExitWall{display:none!important}';document.head.append(stRecoverStyle);
