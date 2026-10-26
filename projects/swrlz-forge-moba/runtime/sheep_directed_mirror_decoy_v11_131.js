// §E v11.131 — direct a short-lived Mirror decoy by dragging the ability.
// This is a native §E sheep gameplay extension, not a new movement system.
function st131MirrorVector(dx,dy){
 const magnitude=Math.hypot(dx,dy);
 if(!Number.isFinite(magnitude)||magnitude<12)return null;
 // Fixed RTS camera maps screen right to +X and screen down to +Z.
 return Math.atan2(dx,dy);
}
function st131MirrorDirection(unit,payload={}){
 const requested=Number(payload.angle);
 if(Number.isFinite(requested))return requested;
 if(unit?.velocity?.lengthSq?.()>.35)return Math.atan2(unit.velocity.x,unit.velocity.z);
 return Number.isFinite(unit?.actor?.rotation?.y)?unit.actor.rotation.y:0;
}
stArchiveSplit=function(s,unit,payload={}){
 if(!s?.archive||!s.rules.split)return stResult(false,'Mirror is disabled in these rules.');
 if(!unit||unit.kind!=='sheep'||unit.captured||unit.isIllusion)return stResult(false,'Only a free sheep can cast Mirror.');
 if((unit.archiveLevel||1)<s.rules.splitUnlock)return stResult(false,'Mirror is not unlocked yet.');
 const cooldown=Math.max(0,(unit.archiveSplitAt??-Infinity)+s.rules.splitCooldown-s.elapsed);
 if(cooldown>0)return stResult(false,'Mirror recharges in '+Math.ceil(cooldown)+'s.',{cooldown});
 const angle=st131MirrorDirection(unit,payload);
 // The decoy aims where the user dragged, with small near-angle retries if a
 // wall clips the destination. Do not change the real sheep's existing order.
 let target=null;
 for(const offset of [0,.2,-.2,.43,-.43,.74,-.74]){
  target=stArchiveDashTarget(unit,angle+offset,8);
  if(target)break;
 }
 if(!target)return stResult(false,'No clear route for the decoy. Try another direction.');
 const previousOrder=unit.order; // informational only — never mutate it
 const copy=stArchiveCloneSheep(s,unit);
 copy.speed=Math.max(unit.speed*1.55,7.5);
 // Short visual trick: at most four seconds, respecting shorter rule values.
 copy.archiveExpires=s.elapsed+Math.min(4,Math.max(1,Number(s.rules.splitLifetime)||4));
 copy.st131MirrorAngle=angle;
 if(target.plan)stArchiveSetRoute(copy,target.plan);
 else stSetOrder(copy,{action:'move',x:target.x,z:target.z});
 unit.archiveSplitAt=s.elapsed;
 s.message='Mirror! Your decoy darts away while your sheep keeps moving.';
 return stResult(true,'',{cooldown:s.rules.splitCooldown,lifetime:copy.archiveExpires-s.elapsed,decoyId:copy.id,direction:angle});
};
let st131Pointer=null,st131LastPointerCast=-Infinity;
function st131MirrorCast(angle){
 if(!stSession||stSession.simulate||stSession.winner||paused)return false;
 const unit=stSession.units.find(u=>u.id===stSession.controlledId);
 if(!unit||unit.captured||unit.kind!=='sheep')return false;
 stUi.buildingId=null;
 // Explicitly DON'T issue select/move/stop here: player can keep holding
 // joystick with another finger while the decoy shoots off.
 const result=stUiCommand('split',Number.isFinite(angle)?{angle}:{});
 if(result?.ok){
  stUiFeedback('Mirror dashes away! Decoy fades in '+(result.lifetime||4).toFixed(1)+'s.');
 }else if(result?.reason)stUiFeedback(result.reason,true);
 stRefreshHUD(true);
 return !!result?.ok;
}
function st131InstallMirrorControl(){
 const btn=$('stSplit');
 if(!btn||btn.dataset.st131MirrorReady==='1')return;
 btn.dataset.st131MirrorReady='1';
 btn.title='Drag in any direction to send the decoy; tap to release forward.';
 btn.style.position='relative';
 btn.style.touchAction='none'; // only this ability button; gameplay pinch intact
 const counter=document.createElement('span');
 counter.className='st131-mirror-cooldown';counter.hidden=true;
 counter.setAttribute('aria-hidden','true');
 btn.appendChild(counter);
 btn.addEventListener('pointerdown',e=>{
  if(btn.disabled||e.button!==0||st131Pointer)return;
  e.preventDefault();e.stopPropagation();
  st131Pointer={id:e.pointerId,x:e.clientX,y:e.clientY,dx:0,dy:0};
  btn.setPointerCapture?.(e.pointerId);
 },true);
 btn.addEventListener('pointermove',e=>{
  if(!st131Pointer||st131Pointer.id!==e.pointerId)return;
  e.preventDefault();e.stopPropagation();
  st131Pointer.dx=e.clientX-st131Pointer.x;
  st131Pointer.dy=e.clientY-st131Pointer.y;
 },true);
 btn.addEventListener('pointerup',e=>{
  if(!st131Pointer||st131Pointer.id!==e.pointerId)return;
  e.preventDefault();e.stopPropagation();
  const gesture=st131Pointer;st131Pointer=null;
  const dx=e.clientX-gesture.x,dy=e.clientY-gesture.y;
  // A pointer action includes the physical touch release, even if Chrome
  // suppresses its synthetic click. Suppress only the duplicate click.
  st131LastPointerCast=performance.now();
  st131MirrorCast(st131MirrorVector(dx,dy));
 },true);
 for(const type of ['pointercancel','lostpointercapture'])btn.addEventListener(type,e=>{
  if(st131Pointer?.id===e.pointerId)st131Pointer=null;
 },true);
 // Preserve keyboard activation and accessibility; don't cast twice on touch.
 btn.onclick=()=>{
  if(performance.now()-st131LastPointerCast<600)return;
  st131MirrorCast(null);
 };
}
const st131InstallBase=stInstallUI;
stInstallUI=function(){st131InstallBase();st131InstallMirrorControl();};
const st131ArchiveRefreshBase=stUiRefreshArchive;
stUiRefreshArchive=function(state,controlled,building,mayBuild,now){
 const result=st131ArchiveRefreshBase(state,controlled,building,mayBuild,now);
 const btn=$('stSplit'),counter=btn?.querySelector('.st131-mirror-cooldown');
 if(!counter)return result;
 const magic=state.progression||controlled?.archive||controlled||{};
 const seconds=Math.max(0,Number(magic.splitCooldownRemaining)||0);
 counter.hidden=seconds<.05||btn.hidden;
 counter.textContent=seconds>0?String(Math.ceil(seconds)):'';
 btn.dataset.st131Cooldown=seconds>0?String(Math.ceil(seconds)):'ready';
 btn.setAttribute('aria-label',seconds>0?'Mirror decoy · '+Math.ceil(seconds)+' seconds remaining':'Mirror decoy · drag to choose direction');
 return result;
};
