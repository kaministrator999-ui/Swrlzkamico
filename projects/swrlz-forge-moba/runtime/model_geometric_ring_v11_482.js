/* SE482_GEOMETRIC_RING_START */
// True object-local circular vertex selection for painted meshes. Selection
// remains owned by the native component editor, not a detached mesh overlay.
const se482GeometricRing=(()=>{
 'use strict';
 const fail=reason=>({ok:false,reason,error:reason});
 let bandPercent=1.2,last=null;
 const axisFor=plane=>plane==='xy'?[0,1,2]:plane==='yz'?[1,2,0]:[0,2,1];
 function measure(top,g,plane){
  const attr=g?.attributes?.position,axes=axisFor(plane);
  if(!top?.vertices?.length||!attr)return null;
  const xyz=top.vertices.map(id=>[attr.getX(id),attr.getY(id),attr.getZ(id)]);
  const range=[0,1,2].map(k=>[
   Math.min(...xyz.map(p=>p[k])),Math.max(...xyz.map(p=>p[k]))
  ]);
  const center=range.map(([a,b])=>(a+b)*.5);
  const planar=Math.max(
   range[axes[0]][1]-range[axes[0]][0],
   range[axes[1]][1]-range[axes[1]][0],.0001);
  const perp=Math.max(range[axes[2]][1]-range[axes[2]][0],.0001);
  return {xyz,range,center,axes,planar,perp};
 }
 function choose(top,geometry,seed,options={}){
  const mode=options.mode||'outline',kind=options.kind||'rim';
  if(!['fill','outline'].includes(mode)||!['rim','center'].includes(kind)||
    !Number.isInteger(seed)||seed<0||seed>=top?.vertices?.length)
   return fail('Choose a real vertex for the circular selection.');
  const plane=options.plane||'xz',m=measure(top,geometry,plane);
  if(!m)return fail('No editable mesh geometry or vertices.');
  const {xyz,center,axes,planar,perp}=m;
  const coords=xyz.map(p=>[p[axes[0]],p[axes[1]]]);
  const chosen=coords[seed],pivot=kind==='center'?chosen:[center[axes[0]],center[axes[1]]];
  const radiusAt=p=>Math.hypot(p[0]-pivot[0],p[1]-pivot[1]);
  const distance=kind==='center'?(options.steps||0)*medianSeedStep(top,xyz,seed,axes,planar):radiusAt(chosen);
  const tolerance=Math.max(.00005,planar*(options.bandPercent||bandPercent)/100);
  const normalY=xyz[seed][axes[2]];
  const axialTolerance=Math.max(perp*.055,planar*.012);
  const arcStart=Number(options.arcStart)||0,arcSweep=Number(options.arcSweep??360);
  const angleOf=p=>((Math.atan2(p[1]-pivot[1],p[0]-pivot[0])*180/Math.PI)%360+360)%360;
  const start=(arcStart%360+360)%360;
  const adj=Array.from({length:top.vertices.length},()=>[]);
  const index=new Map(top.vertices.map((id,i)=>[id,i]));
  for(const [a,b] of top.edges||[]){
   const u=index.get(a),v=index.get(b);
   if(u===undefined||v===undefined||u===v)continue;
   adj[u].push(v);adj[v].push(u);
  }
  const connected=new Set([seed]),queue=[seed];
  for(let i=0;i<queue.length;i++)for(const v of adj[queue[i]]){
   if(!connected.has(v)){connected.add(v);queue.push(v);}
  }
  // Only a circular band (or its interior) is selected. Graph adjacency is
  // used to reject unrelated mesh islands, NOT as a proxy for circular radius.
  let vertexSlots=[];
  for(const i of connected){
   const radial=radiusAt(coords[i]),delta=(angleOf(coords[i])-start+360)%360;
   if(arcSweep<360&&delta>arcSweep+1e-6&&i!==seed)continue;
   if(mode==='outline'){
    if(Math.abs(radial-distance)>tolerance)continue;
    if(kind==='rim'&&Math.abs(xyz[i][axes[2]]-normalY)>axialTolerance)continue;
   }else if(radial>distance+tolerance)continue;
   vertexSlots.push(i);
  }
  // A tap on the outer rim must be part of that rim even with the narrowest band.
  if(kind==='rim'&&!vertexSlots.includes(seed))vertexSlots.push(seed);
  if(mode==='fill'&&kind==='center'&&!vertexSlots.includes(seed))vertexSlots.push(seed);
  vertexSlots.sort((a,b)=>a-b);
  return vertexSlots.length?{
   ok:true,vertexSlots,seed,mode,kind,plane,
   radius:distance,tolerance,connectedVertices:connected.size,
   circular:true
  }:fail('No circular vertices intersect this radius. Increase circle band width.');
 }
 function medianSeedStep(top,xyz,seed,axes,planar){
  const index=new Map(top.vertices.map((id,i)=>[id,i]));
  const source=top.vertices[seed],samples=[];
  for(const [a,b] of top.edges||[]){
   let other;
   if(a===source)other=index.get(b);else if(b===source)other=index.get(a);
   if(other===undefined)continue;
   const d=Math.hypot(xyz[other][axes[0]]-xyz[seed][axes[0]],
    xyz[other][axes[1]]-xyz[seed][axes[1]]);
   if(d>planar*.001)samples.push(d);
  }
  samples.sort((a,b)=>a-b);
  return samples.length?samples[Math.floor(samples.length/2)]:planar*.08;
 }
 function selectCenter(slot,opts={}){
  if(window.SWYRL_ENGINE_MODEL_WORKSHOP?.inspect?.()?.preview?.active)
   return fail('Apply or Cancel the active preview before selecting another circle.');
  const mesh=atelierComponentMesh(),top=mesh&&atelierComponentTopology(mesh);
  if(!top||!mesh||partById(selection)?.kind!=='topologyMesh')return fail('Select editable vertex topology.');
  const shape=window.SWYRL_ENGINE_PROGRESSIVE_TOOLS_474?.inspect?.()?.shape;
  const calculated=choose(top,mesh.geometry,slot,{...opts,kind:'center',
   mode:shape==='fill'?'fill':'outline',bandPercent});
  if(!calculated.ok)return calculated;
  const visible=window.SWYRL_ENGINE_RIM_VISIBILITY_479;
  const ids=visible?.inspect?.()?.frontOnly?
   calculated.vertexSlots.filter(i=>visible.isVisibleSlot(i)):calculated.vertexSlots;
  if(!ids.length)return fail('No camera-visible vertices in this circle.');
  atelierComponentMode='vertex';atelierComponentPartId=selection;atelierComponentIds=ids;
  atelierComponentGesture=null;atelierComponentDrag=null;atelierComponentRefresh();
  last={kind:'center',seed:slot,partId:selection};
  const message='Geometric '+(shape==='fill'?'filled circle':'circle')+' · '+ids.length+' selected vertices';
  status(message);
  window.SWYRL_ENGINE_RING_HEIGHT_478?.sync?.();
  return {...calculated,ok:true,vertexSlots:ids,selectedCount:ids.length,message};
 }
 function noteRim(slot){last={kind:'rim',seed:slot,partId:selection};}
 function reselect(){
  if(!last||last.partId!==selection||window.SWYRL_ENGINE_MODEL_WORKSHOP?.inspect?.()?.preview?.active)return;
  if(last.kind==='center'){
   const ctrl=panel?.querySelector('#se466RingSteps'),steps=Number(ctrl?.value)||2;
   selectCenter(last.seed,{steps,plane:panel?.querySelector('#se466RingPlane')?.value||'xz',
    arcStart:Number(panel?.querySelector('#se466ArcStart')?.value)||0,
    arcSweep:Number(panel?.querySelector('#se466ArcSweep')?.value)||360});
  }else window.SWYRL_ENGINE_RIM_VISIBILITY_479?.selectRim(last.seed);
 }
 let ui=null,bound=false;
 function ensure(){
  const block=panel?.querySelector('#se466RingControls');
  if(!block)return;
  if(ui?.isConnected)return;
  ui=document.createElement('div');ui.id='se482CircleControl';
  const title=document.createElement('label');title.htmlFor='se482BandRange';title.textContent='Circle band width';
  const slider=document.createElement('input');slider.type='range';slider.id='se482BandRange';
  slider.min='0.3';slider.max='8';slider.step='.1';slider.value=String(bandPercent);
  const out=document.createElement('output');out.id='se482BandValue';out.textContent=bandPercent.toFixed(1)+'%';
  const note=document.createElement('small');
  note.textContent='Matches a true circular radius in the selected mesh plane; adjust for uneven geometry.';
  ui.append(title,slider,out,note);
  const summary=block.querySelector('summary');
  if(summary)summary.after(ui);else block.prepend(ui);
  slider.addEventListener('input',()=>{
   bandPercent=Number(slider.value);
   out.textContent=bandPercent.toFixed(1)+'%';
  });
  slider.addEventListener('change',reselect);
  refresh();
 }
 function refresh(){
  const p=panel||document.getElementById('modelAtelierPanel');
  const state=window.SWYRL_ENGINE_PROGRESSIVE_TOOLS_474?.inspect?.();
  const active=!!state?.operation&&state.selectionType==='vertex';
  if(ui)ui.hidden=!active;
  if(!active)return;
  const block=p?.querySelector('#se466RingControls');
  if(block&&['ring','fill'].includes(state.shape))block.open=true;
  const label=p?.querySelector('#se466RingSteps')?.closest('label');
  if(label&&label.firstChild?.nodeType===Node.TEXT_NODE)
   label.firstChild.textContent='Center radius steps';
  const nativeSelection=block?.querySelector('.se466-row');
  if(nativeSelection)nativeSelection.hidden=true;
 }
 function mount(){
  ensure();refresh();
  if(!bound){
   bound=true;
   window.addEventListener('swrlz:model-workshop-change',refresh);
   const p=document.getElementById('modelAtelierPanel');
   if(p)new MutationObserver(refresh).observe(p,{attributes:true,attributeFilter:[
    'data-se477-selection-type','data-se477-selection-shape','data-se477-operation']});
  }
 }
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',mount,{once:true});
 else mount();
 window.addEventListener('swrlz:model-workshop-change',mount);
 const se482PreviousInstall=se430BeginnerInstall;
 se430BeginnerInstall=function(...args){
  const result=se482PreviousInstall.apply(this,args);
  queueMicrotask(mount);
  return result;
 };
 function sampleSlots(slots=[]){
  const mesh=atelierComponentMesh(),top=mesh&&atelierComponentTopology(mesh);
  const attr=mesh?.geometry?.getAttribute?.('position');
  const uv=mesh?.geometry?.getAttribute?.('uv');
  if(!top?.vertices||!attr)return null;
  return slots.map(slot=>{
   const id=top.vertices[slot];
   return {slot,id,position:id===undefined?null:[
    attr.getX(id),attr.getY(id),attr.getZ(id)],
    uv:id===undefined||!uv?null:[uv.getX(id),uv.getY(id)]};
  });
 }
 window.SWYRL_ENGINE_GEOMETRIC_RING_482=Object.freeze({
  choose,selectCenter,noteRim,reselect,refresh:mount,sampleSlots,
  inspect:()=>({bandPercent,last:last?{...last}:null,circular:true})
 });
})();
 /* SE482_GEOMETRIC_RING_END */