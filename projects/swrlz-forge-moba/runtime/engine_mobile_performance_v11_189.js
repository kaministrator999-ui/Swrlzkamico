// §E v11.189: lightweight editor frame profiling and resize invalidation.
// Keeps the native main render loop, WebXR frame ownership, projects and physics.
let se189ResizeInvalid=true,se189LastResize=-Infinity,se189ResizeSamples=0;
const se189ResizeHost=$('viewport')?.parentElement;
const se189InvalidateViewport=()=>{se189ResizeInvalid=true;};
if(typeof ResizeObserver==='function'&&se189ResizeHost){
 const observer=new ResizeObserver(se189InvalidateViewport);
 observer.observe(se189ResizeHost);
}
window.addEventListener('resize',se189InvalidateViewport,{passive:true});
window.visualViewport?.addEventListener('resize',se189InvalidateViewport,{passive:true});
window.addEventListener('orientationchange',se189InvalidateViewport,{passive:true});
function se189ResizeIfNeeded(now){
 if(renderer.xr.isPresenting)return;
 if(!se189ResizeInvalid&&now-se189LastResize<250)return;
 se189ResizeInvalid=false;se189LastResize=now;se189ResizeSamples++;
 resize();
}
const se189Profile={
 samples:0,updateCpuMs:0,renderSubmitMs:0,
 drawCalls:0,triangles:0,lastProfileAt:0,rendered:0
};
function se189TrackMainFrame(frameStart,renderBegin,didRender){
 const now=performance.now();
 const update=Math.max(0,renderBegin-frameStart);
 se189Profile.updateCpuMs=se189Profile.samples===0?update:se189Profile.updateCpuMs*.85+update*.15;
 se189Profile.samples++;
 if(didRender){
  const submit=Math.max(0,now-renderBegin);
  se189Profile.renderSubmitMs=se189Profile.rendered===0?submit:se189Profile.renderSubmitMs*.85+submit*.15;
  se189Profile.rendered++;
  se189Profile.drawCalls=renderer.info?.render?.calls||0;
  se189Profile.triangles=renderer.info?.render?.triangles||0;
 }
 if(now-se189Profile.lastProfileAt>1200){
  se189Profile.lastProfileAt=now;
  const status=document.getElementById('se189PerfMetrics');
  if(status&&document.getElementById('performanceSettings')?.classList.contains('show'))
   status.textContent='JS/update: '+se189Profile.updateCpuMs.toFixed(1)+' ms · render submission: '+
    se189Profile.renderSubmitMs.toFixed(1)+' ms · '+se189Profile.drawCalls+
    ' draws · '+Math.round(se189Profile.triangles).toLocaleString()+' triangles. '+
    'GPU completion time is not measured.';
 }
}
function se189InstallPerfUI(){
 const settings=document.getElementById('performanceSettings');
 const select=document.getElementById('perfPreset');
 if(!settings||!select||document.getElementById('se189MobileBoost'))return;
 if(![...select.options].some(o=>o.value==='mobile')){
  const item=new Option('Mobile Boost · faster 3D','mobile');
  select.add(item,1);
 }
 const action=document.createElement('button');
 action.type='button';action.id='se189MobileBoost';
 action.textContent='⚡ Mobile Boost';
 action.title='Set 62% render scale, turn off shadows and keep a 60 FPS cap; does not change geometry';
 action.addEventListener('click',()=>{
  performancePrefs.preset='mobile';
  applyPerformanceSettings();
  const metrics=document.getElementById('se189PerfMetrics');
  if(metrics)metrics.textContent='Mobile Boost active · 62% resolution · shadows disabled. Watch FPS while moving the camera.';
 });
 const controls=settings.querySelector('.perf-actions');
 controls?.prepend(action);
 const metrics=document.createElement('p');metrics.id='se189PerfMetrics';
 metrics.className='se189-perf-metrics';
 metrics.textContent='Frame diagnostics appear here while the engine runs. GPU completion time is not measured.';
 settings.querySelector('.perf-card')?.append(metrics);
}
window.SWYRL_ENGINE_PERFORMANCE_V11189=Object.freeze({
 snapshot:()=>({
  fps:Number(performanceTelemetry.fps.toFixed(1)),
  frameMs:Number(performanceTelemetry.frameMs.toFixed(1)),
  renderScale:Number((performancePrefs.preset==='auto'?performanceTelemetry.autoScale:performancePrefs.renderScale).toFixed(2)),
  preset:performancePrefs.preset,shadows:!!renderer.shadowMap.enabled,
  jsUpdateMs:Number(se189Profile.updateCpuMs.toFixed(2)),
  renderSubmitMs:Number(se189Profile.renderSubmitMs.toFixed(2)),
  draws:se189Profile.drawCalls,triangles:se189Profile.triangles,
  viewportSizeChecks:se189ResizeSamples,frames:se189Profile.samples,
  note:'renderSubmitMs is CPU WebGL submission, not actual GPU completion'
 }),
 mobileBoost:()=>{performancePrefs.preset='mobile';applyPerformanceSettings();}
});
