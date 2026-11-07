// §E v11.306 — Sheep Tag pursuit pathfinding and simulation-cadence diagnostics.
// Observational only: no extra XR pose reads, scene traversal or frame loops.
const se306Perf={
  started:performance.now(),lastTickAt:0,session:null,
  wolf:{calls:0,ms:0,max:0,misses:0},
  sheep:{calls:0,ms:0,max:0,misses:0},
  adoptions:0,reuses:0,frames:0,simSeconds:0,wallSeconds:0,updateMs:0,
  latest:null
};
function se306ResetWindow(now){
  se306Perf.started=now;
  for(const kind of ['wolf','sheep'])se306Perf[kind]={calls:0,ms:0,max:0,misses:0};
  se306Perf.adoptions=0;se306Perf.reuses=0;se306Perf.frames=0;
  se306Perf.simSeconds=0;se306Perf.wallSeconds=0;se306Perf.updateMs=0;
}
function se306Roll(now){
  const seconds=(now-se306Perf.started)/1000;
  if(seconds<2)return;
  const snapshot={seconds,frames:se306Perf.frames,
    wolf:{...se306Perf.wolf},sheep:{...se306Perf.sheep},
    adoptions:se306Perf.adoptions,reuses:se306Perf.reuses,
    simSeconds:se306Perf.simSeconds,wallSeconds:se306Perf.wallSeconds,
    updateMs:se306Perf.updateMs};
  snapshot.simRatio=snapshot.wallSeconds>.01?snapshot.simSeconds/snapshot.wallSeconds:null;
  se306Perf.latest=snapshot;
  se306ResetWindow(now);
}
const se306PriorPath=stPath;
stPath=function(...args){
  const start=performance.now();
  const kind=Math.abs(args[2]-ST_WOLF_RADIUS)<.001?'wolf':'sheep';
  let route=null;
  try{return route=se306PriorPath(...args);}
  finally{
    const ms=performance.now()-start,stat=se306Perf[kind];
    stat.calls++;stat.ms+=ms;stat.max=Math.max(stat.max,ms);
    if(!route)stat.misses++;
  }
};
const se306PriorUpdate=stUpdate;
stUpdate=function(...args){
  const s=stSession,active=!!s&&!paused&&!s.winner,now=performance.now();
  if(s!==se306Perf.session){
    se306Perf.session=s;se306Perf.lastTickAt=0;
    se306Perf.latest=null;se306ResetWindow(now);
  }
  const before=s?.elapsed||0,previous=se306Perf.lastTickAt;
  try{return se306PriorUpdate(...args);}
  finally{
    const ended=performance.now();
    if(active&&s===stSession){
      const wallDelta=previous?(now-previous)/1000:0;
      if(wallDelta>0&&wallDelta<.25)se306Perf.wallSeconds+=wallDelta;
      se306Perf.simSeconds+=Math.max(0,s.elapsed-before);
      se306Perf.frames++;se306Perf.updateMs+=ended-now;
      se306Perf.lastTickAt=now;
    }else se306Perf.lastTickAt=0;
    se306Roll(ended);
  }
};
function se306Lines(page){
  const s=se306Perf.latest,fmt=n=>Number(n||0).toFixed(1);
  if(!s)return ['MEASURING SHEEP TAG GAMEPLAY','Run or chase wolves for at least 2 seconds',
    'Metrics measure JavaScript CPU, not GPU time','PAGE '+(page+1)+'/8 · WOLF/FRAME DIAGNOSTICS'];
  if(page===6)return [
    'WOLF-RADIUS A* '+s.wolf.calls+' / '+fmt(s.wolf.ms)+'ms CPU total',
    'SHEEP-RADIUS A* '+s.sheep.calls+' / '+fmt(s.sheep.ms)+'ms CPU total',
    'SLOWEST PATH W '+fmt(s.wolf.max)+'ms / S '+fmt(s.sheep.max)+'ms',
    'NO-ROUTE RADIUS W '+s.wolf.misses+' / S '+s.sheep.misses,
    'REUSED '+s.reuses+' · ADOPTED '+s.adoptions,
    'PAGE 7/8 · LAST '+fmt(s.seconds)+'s'
  ];
  return [
    'SIM/REAL '+(s.simRatio===null?'--':Math.round(s.simRatio*100)+'%')+' (1:1 = 100%)',
    'SIM '+fmt(s.simSeconds)+'s / WALL '+fmt(s.wallSeconds)+'s',
    'GAME UPDATE '+fmt(s.updateMs)+'ms CPU total',
    'GAME FRAMES '+s.frames+' IN '+fmt(s.seconds)+'s',
    'FPS GAP IS NOT A GPU TIME MEASUREMENT',
    'PAGE 8/8 · SIMULATION CLOCK'
  ];
}
const se306PriorNerdLines=se265Lines;
se265Lines=function(snapshot,page){
  if(page===6||page===7)return se306Lines(page);
  return se306PriorNerdLines(snapshot,page).map(line=>line.replace(/PAGE ([1-6])\/6/g,'PAGE $1/8'));
};
window.SWYRL_ENGINE_SHEEP_PURSUIT_306=Object.freeze({
  diagnose:()=>({...se306Perf.latest,active:!!stSession&&!paused,
    currentWolfPaths:se306Perf.wolf.calls,currentSheepPaths:se306Perf.sheep.calls,
    meaning:'path CPU grouped by path radius (not caller), simulation time measured; GPU time not measured'})
});
