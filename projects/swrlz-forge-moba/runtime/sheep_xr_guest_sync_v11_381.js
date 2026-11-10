// §E v11.381 — Quest guest of a PHONE-HOSTED Sheep Tag game.
// A WebRTC guest receives authoritative buildings and sheep positions, but
// the old sheep interpolator is scheduled only on window.requestAnimationFrame.
// Quest immersive presentation uses the existing WebXR animation loop instead.
// Separately, the guest-stick-v2 sender read the touch joystick, never XR's
// left controller. Both make an active Quest guest appear frozen at spawn.
// No new clock, renderer, owner, transport, game rule, save or physics path.
const se381={
 xrFrames:0,guestInterpolationFrames:0,skippedBrowserFrames:0,
 xrIntentPackets:0,xrActivePackets:0,neutralPackets:0,
 lastSendAt:-Infinity,lastActive:false,lastStrength:0,lastDirection:null,
 lastMatchId:'',lastSeat:'',lastPacketSeq:0,errors:0,lastError:'',
 lastObservedSnapshot:0,lastObservedUnitX:null,lastObservedUnitZ:null
};
function se381XRGuest(){
 return !!renderer.xr?.isPresenting&&!!se181XR.session&&
   currentProject?.kind==='sheep-tag'&&!!stSession&&!stSession.simulate&&
   !!se150Match.active&&se150Match.role==='guest';
}
function se381InputAllowed(){
 const s=stSession,u=s?.units?.find(unit=>unit.id===se152.assigned);
 return !!u&&!u.captured&&!u.isIllusion&&!s.winner&&!paused&&
  (u.kind!=='wolf'||s.elapsed>=s.rules.headstart)&&
  !se211Paused();
}
function se381Emit(x,z,strength){
 if(!se152Guest()||!se152.assigned)return false;
 const seq=++se154.clientSeq;
 se152Send(se151.guestConn,{
  kind:'guest-stick-v2',roomId:se150Match.roomId,
  matchId:se150Match.matchId,seq,x,z,strength
 });
 se154.tx++;se381.xrIntentPackets++;
 if(strength>.13)se381.xrActivePackets++;
 else se381.neutralPackets++;
 se381.lastPacketSeq=seq;se381.lastStrength=strength;
 se381.lastDirection={x,z};se381.lastSendAt=performance.now();
 se381.lastActive=strength>.13;
 return true;
}
function se381SendXRStick(force=false){
 if(!se381XRGuest()||!se152Guest()||!se152.assigned)return false;
 const match=String(se150Match.matchId||''),seat=se152.assigned;
 if(se381.lastMatchId!==match||se381.lastSeat!==seat){
  se381.lastMatchId=match;se381.lastSeat=seat;
  se381.lastSendAt=-Infinity;se381.lastActive=false;
 }
 let intent={strength:0,x:0,z:0};
 if(se381InputAllowed()){
  try{intent=se199StickIntent();}
  catch(error){se381.errors++;se381.lastError=String(error?.message||error).slice(0,100);}
 }
 const strength=Math.max(0,Math.min(1,Number(intent?.strength)||0));
 const x=strength>.13&&Number.isFinite(intent?.x)?Math.max(-1,Math.min(1,intent.x)):0;
 const z=strength>.13&&Number.isFinite(intent?.z)?Math.max(-1,Math.min(1,intent.z)):0;
 const active=strength>.13,now=performance.now();
 // Follow the XR input frames (not throttled window RAF). Re-send active
 // intent well inside the host's 650ms stale-input window and send release
 // immediately even if the WebXR hand disappears or the menu gains focus.
 if(!force&&se381.lastActive===active&&
    now-se381.lastSendAt<(active?75:260))return false;
 return se381Emit(x,z,active?strength:0);
}
// The LAN guest's original 115ms send interval still runs. When immersive,
// redirect it to the same single bounded XR intent sender; never send stale
// touch-pointer zero packets over an active headset movement command.
const se381OriginalGuestControls=se152GuestControls;
se152GuestControls=function(...args){
 if(se381XRGuest())return se381SendXRStick();
 return se381OriginalGuestControls(...args);
};
// v11.156 owns the existing browser guest RAF. Ignore only its VISUAL update
// while WebXR is presenting, because the native XR callback below owns it.
// The browser RAF keeps its normal lifecycle so exiting VR restores animation.
const se381OriginalGuestFrameOnce=se156GuestFrameOnce;
se156GuestFrameOnce=function(...args){
 if(se381XRGuest()){se381.skippedBrowserFrames++;return;}
 return se381OriginalGuestFrameOnce(...args);
};
// Reuse the existing XR callback already used by cameras, controller rays,
// menu and frame diagnostics; never create a second requestAnimationFrame loop.
// Update authoritative tracked sheep BEFORE camera follow, then send the
// headset-left-stick intent AFTER strategic heading / XR controller sampling.
const se381OriginalXRFrame=se193XRFrame;
se193XRFrame=function(...args){
 const xrGuest=se381XRGuest();
 if(xrGuest){
  se381.xrFrames++;
  if(se152Guest()&&se152.received>0&&!se211Paused()){
   se152GuestFrame(.016); // v11.161/165/166 existing visual reconciliation
   se381.guestInterpolationFrames++;
   se381.lastObservedSnapshot=se152.received;
   const u=stSession.units.find(u=>u.id===se152.assigned);
   if(u){se381.lastObservedUnitX=u.pos.x;se381.lastObservedUnitZ=u.pos.z;}
  }
 }
 const result=se381OriginalXRFrame(...args);
 if(xrGuest)se381SendXRStick();
 return result;
};
function se381Reset(){
 se381.lastSendAt=-Infinity;se381.lastActive=false;se381.lastStrength=0;
 se381.lastMatchId='';se381.lastSeat='';se381.lastDirection=null;
 se381.lastPacketSeq=0;se381.lastObservedSnapshot=0;
 se381.lastObservedUnitX=null;se381.lastObservedUnitZ=null;
}
const se381OriginalStopWorld=se152StopWorld;
se152StopWorld=function(...args){
 se381Reset();
 return se381OriginalStopWorld(...args);
};
const se381OriginalXRCleanup=se193XRCleanup;
se193XRCleanup=function(...args){
 // Release only OUR sent XR intent; do not modify another player's stick.
 if(se381.lastActive&&se150Match.active&&se150Match.role==='guest')
  se381Emit(0,0,0);
 se381Reset();
 return se381OriginalXRCleanup(...args);
};
window.SWYRL_ENGINE_SHEEP_XR_GUEST_381=Object.freeze({
 diagnose:()=>({
  active:se381XRGuest(),role:se150Match.role,
  hostAuthoritative:true,hostSnapshot:se152.received,
  assignedUnit:se152.assigned,
  xrFrames:se381.xrFrames,visualSyncFrames:se381.guestInterpolationFrames,
  browserFramesSuppressedInXR:se381.skippedBrowserFrames,
  xrJoystickPackets:se381.xrIntentPackets,nonzeroPackets:se381.xrActivePackets,
  stopPackets:se381.neutralPackets,lastStickStrength:se381.lastStrength,
  lastStickDirection:se381.lastDirection,lastInputSeq:se381.lastPacketSeq,
  lastAppliedSnapshot:se381.lastObservedSnapshot,
  lastDisplayedSheep:[se381.lastObservedUnitX,se381.lastObservedUnitZ],
  errors:se381.errors,lastError:se381.lastError
 })
});
