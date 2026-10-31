// §E v11.190 — measure actual rendered frames, compare presets in the SAME
// scene/camera, and audit visible draw calls only on demand.
// The RAF / simulation tick is deliberately tracked independently from WebGL submissions.
function se190CountSubmittedFrame(now,didRender){
 const t=performanceTelemetry;
 if(didRender){t.submittedFrames++;t.totalSubmitted++;}
 const span=now-t.submitSampleStart;
 if(span>=900){
  t.submittedFps=t.submittedFrames*1000/span;
  t.submittedFrameMs=t.submittedFrames?span/t.submittedFrames:0;
  t.submittedFrames=0;t.submitSampleStart=now;
  updatePerformanceOverlay();
 }
}
function se190VisibleActorDrawAudit(){
 // Demand-driven, CPU-only tree inspection: conservative candidate counts
 // rather than pretending Three.js reports exact per-actor GPU draw calls.
 const candidates=[];
 if(typeof actors==='undefined'||!Array.isArray(actors))return candidates;
 for(const actor of actors){
  if(!actor||!actor.visible)continue;
  let meshes=0,instances=0,triangles=0;
  actor.traverse?.(child=>{
   if(child===actor||!child.visible)return;
   if(child.isMesh||child.isInstancedMesh){
    meshes++;
    if(child.isInstancedMesh)instances+=child.count;
    const geometry=child.geometry,idx=geometry?.index;
    const pos=geometry?.attributes?.position;
    if(idx||pos)triangles+=(idx?idx.count:pos.count)/3*(child.isInstancedMesh?child.count:1);
   }
  });
  if(meshes>0)candidates.push({name:String(actor.name||actor.userData?.id||'Actor').slice(0,75),meshes,instances,triangles:Math.round(triangles)});
 }
 return candidates.sort((a,b)=>b.meshes-a.meshes).slice(0,8);
}
let se190CompareBusy=false;
const se190Wait=ms=>new Promise(resolve=>setTimeout(resolve,ms));
async function se190ComparePresets(){
 if(se190CompareBusy||renderer.xr.isPresenting)return;
 se190CompareBusy=true;
 const button=document.getElementById('se190Compare');
 const metrics=document.getElementById('se190Comparison');
 const original={...performancePrefs};
 if(button)button.disabled=true;
 const outputs=[];
 try{
  for(const preset of ['low','mobile']){
   if(metrics)metrics.textContent='Measuring '+(preset==='low'?'Low':'Mobile Boost')+' with the same 60 FPS cap… Keep the camera still.';
   performancePrefs.preset=preset;
   applyPerformanceSettings();
   // Both presets are benchmarked under identical cap, regardless of normal
   // Low's saved 45 FPS cap. This temporary override does not persist.
   performancePrefs.maxFps=60;
   await se190Wait(550); // settle graphics allocation / first shader draw
   const start=performance.now(),rendered=performanceTelemetry.totalSubmitted;
   await se190Wait(2700);
   const end=performance.now();
   outputs.push({preset,fps:((performanceTelemetry.totalSubmitted-rendered)*1000/(end-start)),draws:se189Profile.drawCalls,
    triangles:se189Profile.triangles,scale:performancePrefs.renderScale});
  }
  const low=outputs[0],boost=outputs[1];
  const change=boost.fps-low.fps;
  if(metrics)metrics.textContent='Same view · 60 FPS cap for both: Low '+low.fps.toFixed(1)+
   ' rendered FPS ('+Math.round(low.scale*100)+'%), Mobile Boost '+boost.fps.toFixed(1)+
   ' rendered FPS ('+Math.round(boost.scale*100)+'%). Difference '+(change>=0?'+':'')+
   change.toFixed(1)+' FPS. '+boost.draws+' visible draws. Results vary with temperature and scene motion.';
 }catch(error){
  if(metrics)metrics.textContent='Comparison could not complete: '+String(error?.message||error).slice(0,120);
 }finally{
  performancePrefs={...original}; // preserve the user's original choice and caps
  applyPerformanceSettings();
  se190CompareBusy=false;
  if(button)button.disabled=false;
 }
}
function se190InstallDiagnostics(){
 const settings=document.getElementById('performanceSettings');
 if(!settings||document.getElementById('se190Compare'))return;
 const card=settings.querySelector('.perf-card');
 if(!card)return;
 const buttons=document.createElement('div');
 buttons.className='se190-perf-actions';
 const compare=document.createElement('button');
 compare.id='se190Compare';compare.type='button';
 compare.textContent='Compare Low / Boost';
 compare.title='Benchmarks both graphics presets at the same temporary 60 FPS cap, with your existing scene and camera';
 compare.addEventListener('click',()=>void se190ComparePresets());
 const audit=document.createElement('button');
 audit.id='se190Audit';audit.type='button';
 audit.textContent='Inspect draw calls';
 audit.addEventListener('click',()=>{
  const rows=se190VisibleActorDrawAudit();
  const e=document.getElementById('se190AuditResults');
  if(!e)return;
  e.textContent='WebGL draws last frame: '+se189Profile.drawCalls+
   '. Largest visible actor submesh counts (not exact per-actor GPU draws):\n'+
   (rows.length?rows.map(x=>x.name+': '+x.meshes+' meshes, '+x.instances+' instanced pieces').join('\n'):'No visible actor meshes');
 });
 buttons.append(compare,audit);
 const summary=document.createElement('p');
 summary.id='se190Comparison';summary.className='se189-perf-metrics';
 summary.textContent='Comparison temporarily uses a matched 60 FPS cap; original settings are restored afterward.';
 const detail=document.createElement('pre');
 detail.id='se190AuditResults';detail.className='se190-audit-results';
 detail.textContent='Draw-call contributors are inspected only when requested.';
 card.append(buttons,summary,detail);
}
window.SWYRL_ENGINE_PERFORMANCE_V11190=Object.freeze({
 snapshot:()=>({
  renderedFps:Number(performanceTelemetry.submittedFps.toFixed(2)),
  renderedFrameMs:Number(performanceTelemetry.submittedFrameMs.toFixed(2)),
  updateFps:Number(performanceTelemetry.fps.toFixed(2)),
  draws:se189Profile.drawCalls,
  triangles:se189Profile.triangles,
  preset:performancePrefs.preset,
  maxFps:performancePrefs.maxFps,
  totalRendered:performanceTelemetry.totalSubmitted,
  batches:'built-in vault canopy, rib, chamber wall and oculus submeshes'
 }),
 audit:se190VisibleActorDrawAudit,
 compare:se190ComparePresets
});
