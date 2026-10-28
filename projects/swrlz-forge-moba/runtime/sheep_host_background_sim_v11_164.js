// §E v11.164 — keep host-authoritative Sheep Tag simulation advancing
// while its rendering tab is backgrounded but the existing world snapshot
// timer still fires. No new timer, rendering loop, worker, or server.
// Physical two-browser test: houses 12/12; host construction 9% stalled.
const se164={
 wallAt:0,elapsedAt:0,world:null,snapshots:0,
 fallbackCalls:0,fallbackSteps:0,fallbackSeconds:0,
 lastWallGap:0,lastNativeAdvance:0,lastCatchup:0,lastMode:'starting',
 errors:0,lastError:'',lastGuestClock:null
};
function se164HostClock(){
 const s=stSession;
 if(!se150Match.active||se150Match.role!=='host'||!s)return;
 const wall=Date.now();
 if(se164.world!==s||!se164.wallAt){
  se164.world=s;se164.wallAt=wall;se164.elapsedAt=s.elapsed;
  se164.lastMode='starting';return;
 }
 // Paused games must never accumulate a hidden-tab catch-up debt.
 const gap=Math.max(0,Math.min(30,(wall-se164.wallAt)/1000));
 const native=Math.max(0,(Number(s.elapsed)||0)-(Number(se164.elapsedAt)||0));
 se164.lastWallGap=gap;se164.lastNativeAdvance=native;
 se164.wallAt=wall;
 se164.lastCatchup=0;
 if(paused||s.winner||s.simulate||!playing){
  se164.lastMode=paused?'paused':'inactive';
  se164.elapsedAt=s.elapsed;return;
 }
 // Normally requestAnimationFrame already ran stUpdate. During an Android
 // browser switch it may stop, though the existing 130ms PeerJS world timer
 // keeps sending stale progress and house orders. Catch up ONLY the missing
 // native simulation time, never tick both clocks for the same duration.
 const missing=Math.max(0,gap-native);
 if(missing<.075){
  se164.lastMode='native render';
  se164.elapsedAt=s.elapsed;return;
 }
 // A throttled background interval can report a large wall-clock gap.
 // Bound work to 3s / callback and native 50ms substeps for safe physics,
 // AI and building progress. Fully suspended browser pages cannot run code.
 const budget=Math.min(3,missing);
 const steps=Math.min(60,Math.ceil(budget/.05));
 const dt=steps?budget/steps:0;
 let done=0;
 for(let i=0;i<steps&&se150Match.active&&stSession===s&&
       !paused&&!s.winner;i++){
  const before=s.elapsed;
  try{
   // Use the FINAL host gameplay wrapper, including native construction
   // progress, build approach, team AI, fog and existing multiplayer gates.
   stUpdate(dt,performance.now()/1000);
  }catch(error){
   se164.errors++;se164.lastError=String(error?.message||error).slice(0,130);
   console.warn('§E LAN authoritative host clock',error);break;
  }
  const advanced=Math.max(0,s.elapsed-before);
  if(advanced<.000001)break;
  done+=advanced;
  se164.fallbackSteps++;
 }
 if(done>.000001){
  se164.fallbackCalls++;se164.fallbackSeconds+=done;
  se164.lastCatchup=done;se164.lastMode='background catch-up';
 }else se164.lastMode='host simulation not advancing';
 se164.elapsedAt=s.elapsed;
}
const se164PriorSnapshot=se152Snapshot;
se152Snapshot=function(...args){
 if(se150Match.active&&se150Match.role==='host'){
  se164.snapshots++;
  // Simulation must advance BEFORE constructing the network packet.
  se164HostClock();
 }
 return se164PriorSnapshot(...args);
};
// The diagnostic travels with the same genuine host world snapshots, not
// through a second unverified channel. No extra PII or credentials.
const se164PriorSend=se152Send;
se152Send=function(conn,packet){
 if(packet?.kind==='world'&&se150Match.active&&se150Match.role==='host'){
  packet={...packet,hostSimClock:{
   mode:se164.lastMode,
   catchupMs:Math.round(se164.lastCatchup*1000),
   elapsed:Number(stSession?.elapsed)||0,
   totalFallbackMs:Math.round(se164.fallbackSeconds*1000)
  }};
 }
 return se164PriorSend(conn,packet);
};
const se164PriorClientApply=se152ClientApply;
se152ClientApply=function(packet){
 const before=se152.received;
 const result=se164PriorClientApply(packet);
 if(packet?.seq>before&&packet.seq===se152.received&&
    se150Match.active&&se150Match.role==='guest'&&packet.hostSimClock)
  se164.lastGuestClock=packet.hostSimClock;
 return result;
};
const se164PriorLabel=se154GuestLabel;
se154GuestLabel=function(...args){
 const result=se164PriorLabel(...args);
 const clock=se164.lastGuestClock;
 if(se150Match.active&&se150Match.role==='guest'&&se150Match.badge&&clock&&
   (clock.mode==='background catch-up'||
    clock.mode==='host simulation not advancing'))
  se150Match.badge.textContent+=' · host '+clock.mode;
 return result;
};
const se164PriorStopWorld=se152StopWorld;
se152StopWorld=function(...args){
 se164.world=null;se164.wallAt=0;se164.elapsedAt=0;
 se164.snapshots=0;se164.fallbackCalls=0;se164.fallbackSteps=0;
 se164.fallbackSeconds=0;se164.lastWallGap=0;
 se164.lastNativeAdvance=0;se164.lastCatchup=0;
 se164.lastMode='stopped';se164.errors=0;se164.lastError='';
 se164.lastGuestClock=null;
 return se164PriorStopWorld(...args);
};
window.SWYRL_ENGINE_LAN.hostSimulationClock=()=>({
 active:se150Match.active,role:se150Match.role,
 mode:se150Match.role==='guest'?
  (se164.lastGuestClock?.mode||'waiting for host'):se164.lastMode,
 hostGameElapsed:se150Match.role==='guest'?
  (se164.lastGuestClock?.elapsed??null):stSession?.elapsed,
 snapshots:se164.snapshots,
 fallbackCalls:se164.fallbackCalls,
 fallbackSteps:se164.fallbackSteps,
 fallbackSeconds:Number(se164.fallbackSeconds.toFixed(2)),
 lastGapSeconds:Number(se164.lastWallGap.toFixed(2)),
 nativeAdvanceSeconds:Number(se164.lastNativeAdvance.toFixed(2)),
 lastCatchupSeconds:Number(se164.lastCatchup.toFixed(2)),
 errors:se164.errors,lastError:se164.lastError,
 guestLastHostClock:se164.lastGuestClock
});
