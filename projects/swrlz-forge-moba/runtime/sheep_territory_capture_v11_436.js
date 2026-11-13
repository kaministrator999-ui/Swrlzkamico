// SE436_SHEEP_TERRITORY_CAPTURE_START
// Keep SOLO AI sheep from treating the human player's houses as a shared settlement.
// No changes to player placement, LAN authority, saved spawn transforms or movement physics.
const se436Flock={session:null,ready:[],nextWarmAt:.65,warmed:0,hits:0,misses:0,
  captures:0,lastCaptureMs:0,maxCaptureMs:0,disposedIdle:0};
function se436Solo(s){
 return !!s&&!s.simulate&&!(typeof se150Match!=='undefined'&&se150Match.active);
}
function se436BaseCandidates(unit){
 const s=stSession,home=unit.home;
 if(!se436Solo(s))return [home.clone(),...s.buildings.filter(b=>
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
function se436BaseAllowed(unit,point){
 const s=stSession;if(!se436Solo(s))return true;
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
function se436BuildAllowed(unit,x,z){
 const s=stSession;if(!se436Solo(s))return true;
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
const se436NativeMakeSpirit=stMakeSpirit;
function se436ClearPool(){
 while(se436Flock.ready.length){
  stDisposeVisual(se436Flock.ready.pop());
  se436Flock.disposedIdle++;
 }
 se436Flock.session=null;
}
function se436CheckPoolSession(s){
 if(se436Flock.session===s)return;
 se436ClearPool();
 se436Flock.session=s;
 se436Flock.nextWarmAt=.65;
}
function se436WarmSpirit(){
 const s=stSession;if(!se436Solo(s)||paused||s.winner||
    !renderer.xr?.isPresenting)return;
 se436CheckPoolSession(s);
 const active=s.units.filter(u=>u.kind==='sheep'&&!u.captured&&!u.isIllusion).length;
 const limit=Math.min(4,active);
 if(!limit||se436Flock.ready.length>=limit||s.elapsed<se436Flock.nextWarmAt)return;
 // One unattached visual per spaced game tick, never an entire flock in one frame.
 se436Flock.nextWarmAt=s.elapsed+.75;
 se436Flock.ready.push(se436NativeMakeSpirit());
 se436Flock.warmed++;
}
stMakeSpirit=function(...args){
 const s=stSession;
 if(s&&se436Solo(s))se436CheckPoolSession(s);
 if(s&&se436Flock.session===s&&se436Flock.ready.length){
  se436Flock.hits++;return se436Flock.ready.pop();
 }
 se436Flock.misses++;return se436NativeMakeSpirit(...args);
};
const se436PriorUpdate=stUpdate;
stUpdate=function(...args){
 const result=se436PriorUpdate(...args);
 se436WarmSpirit();
 return result;
};
const se436PriorStop=stStop;
stStop=function(...args){
 se436ClearPool();
 return se436PriorStop(...args);
};
const se436PriorCapture=stCapture;
stCapture=function(unit,wolf){
 const begun=performance.now(),already=!!unit?.captured;
 const result=se436PriorCapture(unit,wolf);
 if(!already&&unit?.captured){
  const ms=performance.now()-begun;
  se436Flock.captures++;
  se436Flock.lastCaptureMs=ms;
  se436Flock.maxCaptureMs=Math.max(se436Flock.maxCaptureMs,ms);
 }
 return result;
};
window.SWYRL_ENGINE_SHEEP_TERRITORY_CAPTURE_436=Object.freeze({
 diagnose:()=>({active:!!stSession,solo:se436Solo(stSession),
   pooledSpirits:se436Flock.ready.length,warmed:se436Flock.warmed,
   poolHits:se436Flock.hits,poolMisses:se436Flock.misses,
   captures:se436Flock.captures,lastCaptureJsMs:+se436Flock.lastCaptureMs.toFixed(2),
   slowestCaptureJsMs:+se436Flock.maxCaptureMs.toFixed(2),
   idleSpiritsDisposed:se436Flock.disposedIdle,
   note:'Capture timing excludes the subsequent GPU render and compositor frame.'})
});
// SE436_SHEEP_TERRITORY_CAPTURE_END
