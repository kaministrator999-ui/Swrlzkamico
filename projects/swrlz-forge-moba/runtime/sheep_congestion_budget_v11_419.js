// SE419_SHEEP_CONGESTION_BUDGET_START
// A global path-search quota only for non-player SOLO Quest sheep.
const se419Traffic={session:null,frame:-1,used:0,perFrame:1,planned:0,deferred:0,
  yieldProbes:0,blockedStatic:0,blockedUnits:0};
function se419TrafficActive(unit){
 const s=stSession;
 return !!s&&unit?.kind==='sheep'&&unit.id!==s.controlledId&&
   !unit.captured&&!unit.isIllusion&&!s.simulate&&
   typeof renderer!=='undefined'&&!!renderer.xr?.isPresenting&&
   typeof se193XRGameActive==='function'&&se193XRGameActive()&&
   !(typeof se150Match!=='undefined'&&se150Match.active);
}
function se419TrafficPermit(unit){
 if(!se419TrafficActive(unit))return true;
 const s=stSession;
 if(se419Traffic.session!==s){
   se419Traffic.session=s;se419Traffic.frame=-1;se419Traffic.used=0;
   se419Traffic.planned=0;se419Traffic.deferred=0;
   se419Traffic.yieldProbes=0;se419Traffic.blockedStatic=0;se419Traffic.blockedUnits=0;
 }
 if(se419Traffic.frame!==s.elapsed){se419Traffic.frame=s.elapsed;se419Traffic.used=0;}
 if(se419Traffic.used>=se419Traffic.perFrame){se419Traffic.deferred++;return false;}
 se419Traffic.used++;se419Traffic.planned++;return true;
}
function se419TrafficPause(unit,base=.15){
 return base+(Math.abs(Number(unit?.botIndex)||0)%5)*.075;
}
window.SWYRL_ENGINE_SHEEP_CONGESTION_419=Object.freeze({
 diagnose:()=>({active:!!stSession,
  soloQuestOnly:true,perGameTick:se419Traffic.perFrame,
  paths:se419Traffic.planned,deferred:se419Traffic.deferred,
  yieldProbes:se419Traffic.yieldProbes,blockedStatic:se419Traffic.blockedStatic,
  blockedUnits:se419Traffic.blockedUnits,
  waiting:stSession?.units?.filter(u=>se419TrafficActive(u)&&
    (u.traffic?.retryAt||0)>stSession.elapsed).length||0})
});
// SE419_SHEEP_CONGESTION_BUDGET_END
