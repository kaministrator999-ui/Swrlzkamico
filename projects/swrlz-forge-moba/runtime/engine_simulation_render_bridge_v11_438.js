/* SE438_ENGINE_SIMULATION_RENDER_BRIDGE_START */
// §E engine-owned nonblocking job boundary. Keep the native WebXR render loop,
// native game simulation, LAN authority, and human input untouched.
// Only pure SOLO XR NPC A* route search crosses a Worker boundary; messages
// contain immutable numeric nav snapshots, never THREE/scene object references.
const se438Stats={workerRoutes:0,workerCompleted:0,workerErrors:0,workerFallbacks:0,
  staleRoutes:0,queueFull:0,navCopies:0,simTicks:0,slowSimTicks:0,
  lastSimCpuMs:0,maxSimCpuMs:0,renderCalls:0,lastRenderSubmitCpuMs:0,
  maxRenderSubmitCpuMs:0,visibleFrameGaps:0,maxVisibleGapMs:0};
let se438Worker=null,se438WorkerReady=false,se438WorkerFailed=false;
let se438WorkerUrl=null,se438RequestSerial=0,se438LastSimAt=0;
const se438Pending=new Map(),se438Requests=new Map();
const se438WorkerSource=String.raw`
'use strict';
const nearest=(nav,x,z)=>{
 const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
 const gx=clamp(Math.round(x/nav.grid),-nav.extent,nav.extent);
 const gz=clamp(Math.round(z/nav.grid),-nav.extent,nav.extent);
 const first=(gz+nav.extent)*nav.width+gx+nav.extent;
 if(!nav.blocked[first])return first;
 let best=-1,distance=Infinity;
 for(let ring=1;ring<=Math.min(64,nav.width);ring++){
  for(let dz=-ring;dz<=ring;dz++)for(let dx=-ring;dx<=ring;dx++){
   if(Math.abs(dx)!==ring&&Math.abs(dz)!==ring)continue;
   const cx=gx+dx,cz=gz+dz;
   if(Math.abs(cx)>nav.extent||Math.abs(cz)>nav.extent)continue;
   const id=(cz+nav.extent)*nav.width+cx+nav.extent;
   if(nav.blocked[id])continue;
   const d=(cx*nav.grid-x)**2+(cz*nav.grid-z)**2;
   if(d<distance){distance=d;best=id;}
  }
  if(best!==-1)return best;
 }
 return -1;
};
function route(q){
 const nav={blocked:new Uint8Array(q.blocked),width:q.width,extent:q.extent,grid:q.grid};
 const first=nearest(nav,q.startX,q.startZ),last=nearest(nav,q.targetX,q.targetZ);
 if(first<0||last<0)return null;
 const pt=id=>[(id%nav.width-nav.extent)*nav.grid,
   (Math.floor(id/nav.width)-nav.extent)*nav.grid];
 if(first===last)return [pt(last)];
 const n=nav.blocked.length,scores=new Float64Array(n),
   parents=new Int32Array(n),closed=new Uint8Array(n);
 scores.fill(Infinity);parents.fill(-1);
 const heap=[];
 function push(id,f){
  let i=heap.length;heap.push({id,f});
  while(i){const p=(i-1)>>1;if(heap[p].f<=f)break;
   heap[i]=heap[p];i=p;}heap[i]={id,f};
 }
 function pop(){
  const top=heap[0],tail=heap.pop();
  if(heap.length){let i=0;while(i*2+1<heap.length){
    let c=i*2+1;if(c+1<heap.length&&heap[c+1].f<heap[c].f)c++;
    if(heap[c].f>=tail.f)break;heap[i]=heap[c];i=c;
   }heap[i]=tail;}return top.id;
 }
 const goalX=last%nav.width,goalZ=Math.floor(last/nav.width);
 const h=id=>{const dx=Math.abs(id%nav.width-goalX),dz=Math.abs(Math.floor(id/nav.width)-goalZ);
  return Math.max(dx,dz)+(Math.SQRT2-1)*Math.min(dx,dz);};
 scores[first]=0;push(first,h(first));
 let expanded=0,found=false;
 while(heap.length&&expanded<18000){
  const id=pop();if(closed[id])continue;
  if(id===last){found=true;break;}closed[id]=1;expanded++;
  const x=id%nav.width,z=Math.floor(id/nav.width);
  for(let dz=-1;dz<=1;dz++)for(let dx=-1;dx<=1;dx++){
   if(!dx&&!dz)continue;const nx=x+dx,nz=z+dz;
   if(nx<0||nz<0||nx>=nav.width||nz>=nav.width)continue;
   const next=nz*nav.width+nx;
   if(nav.blocked[next]||closed[next])continue;
   if(dx&&dz&&(nav.blocked[z*nav.width+nx]||nav.blocked[nz*nav.width+x]))continue;
   const score=scores[id]+(dx&&dz?Math.SQRT2:1);
   if(score>=scores[next])continue;
   scores[next]=score;parents[next]=id;push(next,score+h(next));
  }
 }
 if(!found)return null;
 const path=[];let id=last;
 while(id!==first&&id>=0){path.push(pt(id));id=parents[id];}
 path.reverse();return path;
}
onmessage=e=>{
 const q=e.data;
 if(q.kind==='hello'){postMessage({kind:'ready'});return;}
 if(q.kind!=='route')return;
 try{postMessage({kind:'result',id:q.id,path:route(q)});}
 catch(error){postMessage({kind:'failure',id:q.id});}
};
`;
function se438CancelRequests(){
 for(const q of se438Requests.values())
  if(q.session===stSession&&q.unit)q.unit.repathAt=0;
 se438Pending.clear();se438Requests.clear();
}
function se438DisableWorker(){
 se438WorkerFailed=true;se438WorkerReady=false;se438Stats.workerErrors++;
 se438Worker?.terminate();se438Worker=null;
 if(se438WorkerUrl){URL.revokeObjectURL(se438WorkerUrl);se438WorkerUrl=null;}
 se438CancelRequests();
}
function se438RouteResponse(event){
 const reply=event.data;
 if(reply?.kind==='ready'){
  se438WorkerReady=true;
  if(se438WorkerUrl){URL.revokeObjectURL(se438WorkerUrl);se438WorkerUrl=null;}
  return;
 }
 if(reply?.kind!=='result'&&reply?.kind!=='failure')return;
 const q=se438Requests.get(reply.id);
 if(!q){se438Stats.staleRoutes++;return;}
 se438Requests.delete(reply.id);
 if(se438Pending.get(q.unit)===q)se438Pending.delete(q.unit);
 const s=stSession,u=q.unit;
 if(reply.kind==='failure'){
  se438DisableWorker();if(s===q.session)u.repathAt=0;return;
 }
 if(s!==q.session||!s||u.captured||s.navVersion!==q.navVersion||
    (u.pathTarget&&u.pathTarget.distanceToSquared(q.target)>1)||
    u.pathVersion!==q.navVersion){
  se438Stats.staleRoutes++;
  if(s===q.session&&u.pathVersion===q.navVersion)u.repathAt=0;
  return;
 }
 // Apply only a route for the live matching session/nav/goal. The existing
 // main-thread sweep/collision still validates every actual movement step.
 u.path=Array.isArray(reply.path)?reply.path.map(p=>new THREE.Vector3(p[0],0,p[1])):[];
 u.pathVersion=s.navVersion;u.pathTarget=q.target.clone();
 u.repathAt=s.elapsed+.8;se438Stats.workerCompleted++;
}
function se438InitWorker(){
 if(se438Worker||se438WorkerFailed)return;
 try{
  if(typeof Worker!=='function'||typeof Blob!=='function'||
     !URL?.createObjectURL)throw Error('Worker unavailable');
  se438WorkerUrl=URL.createObjectURL(new Blob([se438WorkerSource],{type:'text/javascript'}));
  se438Worker=new Worker(se438WorkerUrl);
  se438Worker.onmessage=se438RouteResponse;
  se438Worker.onerror=()=>se438DisableWorker();
  se438Worker.postMessage({kind:'hello'});
 }catch(error){se438DisableWorker();}
}
function se438EligibleRoute(unit){
 const s=stSession;
 return !!s&&!s.simulate&&!s.winner&&renderer.xr?.isPresenting&&
   typeof se437Solo==='function'&&se437Solo(s)&&
   unit&&unit.id!==s.controlledId&&!unit.captured&&
   typeof ST_GRID==='number'&&typeof stNavigation==='function';
}
// A pending Worker search returns no route for THIS npc. Rendering, human
// movement, simulation and other NPCs continue on their established cadence.
function se438Route(unit,start,target,radius){
 if(!se438EligibleRoute(unit))return stPath(start,target,radius);
 se438InitWorker();
 if(!se438WorkerReady){
  se438Stats.workerFallbacks++;return stPath(start,target,radius);
 }
 const s=stSession,prev=se438Pending.get(unit);
 if(prev){
  if(prev.session===s&&prev.navVersion===s.navVersion&&
     prev.target.distanceToSquared(target)<=1)return [];
  se438Pending.delete(unit);se438Requests.delete(prev.id);
 }
 if(se438Requests.size>=12){se438Stats.queueFull++;return [];}
 const nav=stNavigation(radius);
 if(!nav?.blocked||nav.blocked.length>65536||
    !Number.isFinite(start.x)||!Number.isFinite(target.x)||
    !Number.isFinite(start.z)||!Number.isFinite(target.z)){
  se438Stats.workerFallbacks++;return stPath(start,target,radius);
 }
 const id=++se438RequestSerial;
 const q={id,unit,session:s,navVersion:s.navVersion,target:target.clone()};
 se438Pending.set(unit,q);se438Requests.set(id,q);
 try{
  const blocked=new Uint8Array(nav.blocked);
  se438Stats.navCopies++;se438Stats.workerRoutes++;
  se438Worker.postMessage({kind:'route',id,width:nav.width,extent:nav.extent,
    grid:ST_GRID,blocked:blocked.buffer,startX:start.x,startZ:start.z,
    targetX:target.x,targetZ:target.z},[blocked.buffer]);
 }catch(error){
  se438DisableWorker();se438Stats.workerFallbacks++;
  return stPath(start,target,radius);
 }
 return [];
}
const se438NativeStart=stStart;
stStart=function(...args){se438CancelRequests();return se438NativeStart.apply(this,args);};
const se438NativeStop=stStop;
stStop=function(...args){se438CancelRequests();return se438NativeStop.apply(this,args);};
const se438NativeUpdate=stUpdate;
stUpdate=function(...args){
 const at=performance.now(),gap=se438LastSimAt?at-se438LastSimAt:0;se438LastSimAt=at;
 if(renderer.xr?.isPresenting&&gap>40&&gap<5000){
  se438Stats.visibleFrameGaps++;
  se438Stats.maxVisibleGapMs=Math.max(gap,se438Stats.maxVisibleGapMs);
 }
 try{return se438NativeUpdate.apply(this,args);}
 finally{
  const duration=performance.now()-at;
  se438Stats.simTicks++;se438Stats.lastSimCpuMs=+duration.toFixed(2);
  se438Stats.maxSimCpuMs=Math.max(duration,se438Stats.maxSimCpuMs);
  if(duration>8)se438Stats.slowSimTicks++;
 }
};
const se438NativeRender=renderer.render;
renderer.render=function(...args){
 const at=performance.now();
 try{return se438NativeRender.apply(this,args);}
 finally{
  const ms=performance.now()-at;
  se438Stats.renderCalls++;se438Stats.lastRenderSubmitCpuMs=+ms.toFixed(2);
  se438Stats.maxRenderSubmitCpuMs=Math.max(ms,se438Stats.maxRenderSubmitCpuMs);
 }
};
window.SWYRL_ENGINE_RENDER_BRIDGE_438=Object.freeze({
 diagnose:()=>({...se438Stats,workerReady:se438WorkerReady,
  workerFailed:se438WorkerFailed,pendingRoutes:se438Requests.size,
  renderAndSimulationSeparatedByWorkerFor:'solo XR NPC numeric A* route computation only',
  nativeXRLoopPreserved:true,nativeLANAuthorityPreserved:true,
  gpuAndCompositorTimesNotMeasured:true}),
 // Diagnostics do not spin an additional RAF, timer or render loop.
 resetCounters:()=>{for(const key of Object.keys(se438Stats))se438Stats[key]=0;}
});
/* SE438_ENGINE_SIMULATION_RENDER_BRIDGE_END */