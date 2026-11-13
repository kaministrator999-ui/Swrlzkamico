// SE437_SHEEP_TERRITORY_CAPTURE_START
// Keep SOLO AI sheep from treating the human player's houses as a shared settlement.
// No changes to player placement, LAN authority, saved spawn transforms or movement physics.
const se437Flock={session:null,ready:[],nextWarmAt:.65,warmed:0,hits:0,misses:0,
  captures:0,lastCaptureMs:0,maxCaptureMs:0,disposedIdle:0};
function se437Solo(s){
 return !!s&&!s.simulate&&!(typeof se150Match!=='undefined'&&se150Match.active);
}
function se437BaseCandidates(unit){
 const s=stSession,home=unit.home;
 if(!se437Solo(s))return [home.clone(),...s.buildings.filter(b=>
   b.hp>0&&s.units.some(u=>u.id===b.owner&&u.kind==='sheep')).slice(0,12)
   .map(b=>b.pos.clone().add(new THREE.Vector3(4.5,0,4.5)))];
 const angle=(Number(unit.botIndex)||0)*2.399963229728653;
 const sites=[home.clone()];
 for(const radius of [16,23,30]){
  for(const offset of [0,-.73,.73,1.46]){
   sites.push(new THREE.Vector3(home.x+Math.cos(angle+offset)*radius,0,
     home.z+Math.sin(angle+offset)*radius));
  }
 }
 return sites;
}
function se437BaseAllowed(unit,point){
 const s=stSession;if(!se437Solo(s))return true;
 const player=s.units.find(u=>u.id===s.controlledId&&u.kind==='sheep'&&!u.captured);
 if(player&&player!==unit){
  if(point.distanceToSquared(player.home)<100||
     point.distanceToSquared(player.pos)<144)return false;
  for(const house of s.buildings)if(house.hp>0&&house.owner===player.id&&
    point.distanceToSquared(house.pos)<144)return false;
 }
 for(const other of s.units)if(other!==unit&&!other.captured&&
   !other.isIllusion&&other.kind==='sheep'&&other.base&&
   point.distanceToSquared(other.base)<121)return false;
 return true;
}
function se437BuildAllowed(unit,x,z){
 const s=stSession;if(!se437Solo(s))return true;
 const position={x,z};
 // Independent building plots: AI never extends its maze into another sheep's base.
 for(const other of s.units){
  if(other===unit||other.kind!=='sheep'||other.captured||other.isIllusion)continue;
  const centre=other.id===s.controlledId?other.pos:other.base;
  if(centre&&(x-centre.x)**2+(z-centre.z)**2<81)return false;
 }
 const player=s.units.find(u=>u.id===s.controlledId&&u.kind==='sheep');
 if(player&&player!==unit){
  if((x-player.home.x)**2+(z-player.home.z)**2<81)return false;
  for(const b of s.buildings)if(b.hp>0&&b.owner===player.id&&
    (x-b.pos.x)**2+(z-b.pos.z)**2<81)return false;
 }
 return true;
}
const se437NativeMakeSpirit=stMakeSpirit;
function se437ClearPool(){
 while(se437Flock.ready.length){
  stDisposeVisual(se437Flock.ready.pop());
  se437Flock.disposedIdle++;
 }
 se437Flock.session=null;
}
function se437CheckPoolSession(s){
 if(se437Flock.session===s)return;
 se437ClearPool();
 se437Flock.session=s;
 se437Flock.nextWarmAt=.65;
}
function se437WarmSpirit(){
 const s=stSession;if(!se437Solo(s)||paused||s.winner||
    !renderer.xr?.isPresenting)return;
 se437CheckPoolSession(s);
 const active=s.units.filter(u=>u.kind==='sheep'&&!u.captured&&!u.isIllusion).length;
 const limit=Math.min(4,active);
 if(!limit||se437Flock.ready.length>=limit||s.elapsed<se437Flock.nextWarmAt)return;
 // One unattached visual per spaced game tick, never an entire flock in one frame.
 se437Flock.nextWarmAt=s.elapsed+.75;
 se437Flock.ready.push(se437NativeMakeSpirit());
 se437Flock.warmed++;
}
stMakeSpirit=function(...args){
 const s=stSession;
 if(s&&se437Solo(s))se437CheckPoolSession(s);
 if(s&&se437Flock.session===s&&se437Flock.ready.length){
  se437Flock.hits++;return se437Flock.ready.pop();
 }
 se437Flock.misses++;return se437NativeMakeSpirit(...args);
};
const se437PriorUpdate=stUpdate;
stUpdate=function(...args){
 const result=se437PriorUpdate(...args);
 se437WarmSpirit();
 return result;
};
const se437PriorStop=stStop;
stStop=function(...args){
 se437ClearPool();
 return se437PriorStop(...args);
};
const se437PriorCapture=stCapture;
stCapture=function(unit,wolf){
 const begun=performance.now(),already=!!unit?.captured;
 const result=se437PriorCapture(unit,wolf);
 if(!already&&unit?.captured){
  const ms=performance.now()-begun;
  se437Flock.captures++;
  se437Flock.lastCaptureMs=ms;
  se437Flock.maxCaptureMs=Math.max(se437Flock.maxCaptureMs,ms);
 }
 return result;
};
window.SWYRL_ENGINE_SHEEP_TERRITORY_CAPTURE_436=Object.freeze({
 diagnose:()=>({active:!!stSession,solo:se437Solo(stSession),
   pooledSpirits:se437Flock.ready.length,warmed:se437Flock.warmed,
   poolHits:se437Flock.hits,poolMisses:se437Flock.misses,
   captures:se437Flock.captures,lastCaptureJsMs:+se437Flock.lastCaptureMs.toFixed(2),
   slowestCaptureJsMs:+se437Flock.maxCaptureMs.toFixed(2),
   idleSpiritsDisposed:se437Flock.disposedIdle,
   note:'Capture timing excludes the subsequent GPU render and compositor frame.'})
});
// SE437_SHEEP_TERRITORY_CAPTURE_END
