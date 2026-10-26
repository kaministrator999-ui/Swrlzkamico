// §E v11.132 — allow canvas descendants as true meadow drag targets,
// opt-in repeat placement, and a short cancellable construction beat.
const st132Rapid={on:false,placements:0,queued:0,limit:8};
function st132MeadowTarget(target){
 const viewport=$('viewport');
 // Never treat HUD elements, building buttons, or screen overlays as ground.
 return !!viewport&&!!target&&(target===viewport||viewport.contains(target));
}
function st132RapidSet(on){
 st132Rapid.on=!!on&&!!stSession&&!stSession.simulate&&stSession.role==='sheep'&&!stSession.winner;
 st132RapidUpdate();return st132Rapid.on;
}
function st132RapidUpdate(){
 const btn=$('stRapidBuild');if(!btn)return;
 btn.hidden=!stSession||stSession.simulate||!stUi.shown||stSession.role!=='sheep'||!!stSession.winner;
 btn.setAttribute('aria-pressed',String(st132Rapid.on));
 btn.classList.toggle('active',st132Rapid.on);
 btn.setAttribute('aria-label',st132Rapid.on?'Rapid Build on. Tap to turn off.':'Rapid Build off. Tap to stay in selected build mode.');
 btn.title=st132Rapid.on?'Rapid Build ON: retain house tool after placing.':'Rapid Build OFF: place one house at a time.';
 const caption=btn.querySelector('small');if(caption)caption.textContent=st132Rapid.on?'ON':'OFF';
}
function st132RapidInstall(){
 if($('stRapidBuild')||!$('sheepTagHUD'))return;
 const button=document.createElement('button');button.type='button';
 button.id='stRapidBuild';button.className='st-rapid-build';
 button.innerHTML='<span aria-hidden="true">🏠<sup>↻</sup></span><small>OFF</small>';
 button.setAttribute('aria-pressed','false');
 button.addEventListener('click',event=>{
  event.preventDefault();event.stopPropagation();
  const on=st132RapidSet(!st132Rapid.on);
  stUiFeedback(on?'Rapid Build on. Drag the meadow and release to place houses repeatedly.':'Rapid Build off. Building placement returns to single use.');
 });
 $('sheepTagHUD').appendChild(button);st132RapidUpdate();
}
const st132UiInstallBase=stInstallUI;
stInstallUI=function(){const result=st132UiInstallBase();st132RapidInstall();return result;};
const st132HudBase=stRefreshHUD;
stRefreshHUD=function(...args){const result=st132HudBase(...args);st132RapidUpdate();return result;};
// The skill-button pointerup path is still a *selection*, while the next
// touch and drag on the actual meadow controls the preview. On successful
// meadow release, keep the chosen tool only if Rapid Build is ON.
const st132BuildBase=stIssueBuild;
stIssueBuild=function(unit,kind,x,z,rotation=0){
 if(st132Rapid.on&&unit?.order?.action==='build'){
  const fit=stCanBuild(kind,x,z,unit.id,rotation);
  if(!fit.ok)return fit;
  if(!stBuildApproach(unit,fit.x,fit.z,fit.kind,fit.rotation))
   return stResult(false,'That new house cannot be reached.');
  const queue=unit.st132BuildQueue||(unit.st132BuildQueue=[]);
  if(queue.length>=st132Rapid.limit)return stResult(false,'Rapid Build queue is full.');
  queue.push({kind:fit.kind,x:fit.x,z:fit.z,rotation:fit.rotation});
  st132Rapid.queued++;return stResult(true,'House queued.',{rapid:true,queued:queue.length});
 }
 return st132BuildBase(unit,kind,x,z,rotation);
};
// Real house construction starts a tiny game-time recovery, not a global
// pause. Non-building sheep, wolves and all joystick controls keep running.
const st132NewBuildingBase=stNewBuilding;
stNewBuilding=function(kind,x,z,owner,authored=null,rotation=0){
 const built=st132NewBuildingBase(kind,x,z,owner,authored,rotation);
 if(built&&!authored&&stSession){
  const sheep=stSession.units.find(u=>u.id===owner&&u.kind==='sheep');
  if(sheep){sheep.st132BuildHoldUntil=stSession.elapsed+.18;st132Rapid.placements++;}
 }
 return built;
};
function st132CancelBuildBeat(unit){
 if(!unit)return;
 unit.st132BuildHoldUntil=-Infinity;
 if(unit.st132BuildQueue)unit.st132BuildQueue.length=0;
}
const st132CommandBase=stCommand;
stCommand=function(action,payload={}){
 if(action==='move'){
  const unit=stSession?.units.find(u=>u.id===stSession.controlledId);
  st132CancelBuildBeat(unit);
 }
 return st132CommandBase(action,payload);
};
const st132StickBase=stMobileStickPoint;
stMobileStickPoint=function(event){
 const value=st132StickBase(event);
 if(stMobile.strength>.16&&stMobile.unit)st132CancelBuildBeat(stMobile.unit);
 return value;
};
const st132UpdateSheepBase=stUpdateSheep;
stUpdateSheep=function(unit,dt){
 if(!unit.captured&&stSession?.elapsed<(unit.st132BuildHoldUntil||-Infinity)
  &&!(stMobile.unit===unit&&stMobile.pointer!==null&&stMobile.strength>.16)){
  stPlaceUnit(unit);return;
 }
 const wasBuilding=unit.order?.action==='build';
 const result=st132UpdateSheepBase(unit,dt);
 if(wasBuilding&&unit.order?.action!=='build'&&!unit.captured&&unit.st132BuildQueue?.length){
  while(unit.st132BuildQueue.length){
   const next=unit.st132BuildQueue.shift();
   const issued=st132BuildBase(unit,next.kind,next.x,next.z,next.rotation);
   if(issued?.ok)break;
   if(unit.id===stSession?.controlledId)stUiFeedback(issued?.reason||'Queued house blocked.',true);
  }
 }
 return result;
};
const st132StopBase=stStop;
stStop=function(...args){
 st132Rapid.on=false;st132Rapid.queued=0;
 return st132StopBase(...args);
};
const st132StatusBase=stUiStatus;
stUiStatus=function(){
 const status=st132StatusBase();
 const s=stSession,unit=s?.units.find(u=>u.id===s.controlledId);
 return {...status,rapidBuild:{
  enabled:st132Rapid.on,placements:st132Rapid.placements,
  queued:unit?.st132BuildQueue?.length||0,
  holdRemaining:unit?Math.max(0,(unit.st132BuildHoldUntil||0)-s.elapsed):0
 }};
};
