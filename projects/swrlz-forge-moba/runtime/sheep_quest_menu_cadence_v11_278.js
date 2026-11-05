// §E v11.278 · Quest metrics clearance + low-frequency HUD redraw + menu-gap telemetry.
// Loaded after v11.276 wrist tracking and v11.265 diagnostics.
// No new WebGL context, texture, scene graph, player input or frame scheduler.
const se278StatsScratch=new THREE.Vector3();
const se278Perf={
  lastSample:0,lastPaint:0,paintPage:-1,paints:0,throttledPaints:0,
  paintCpuMs:0,paintCpuMaxMs:0,
  samples:{neither:{count:0,avgMs:0},stats:{count:0,avgMs:0},
    radial:{count:0,avgMs:0},both:{count:0,avgMs:0}},
  lastMode:'neither'
};
// Keep existing full-size readable metrics surface, but move it ~12 cm
// farther forward and ~6 cm above the left-hand Quest controller.
se276StatsWrist.offset.set(.13,.30,-.30);
// Metrics-only canvas updates are expensive on a low-end Quest under heavy
// draw pressure. Do not upload a new GPU CanvasTexture every ~960 ms.
// Immediate creation and center-click page changes bypass the limit.
const se278PriorCanvasRender=se210CanvasRender;
se210CanvasRender=function(panel){
  if(panel?.kind!=='metrics'||!renderer.xr?.isPresenting)
    return se278PriorCanvasRender(panel);
  const now=performance.now();
  const page=se265Perf.metricPage;
  if(panel.lastKey&&page===se278Perf.paintPage&&
     now-se278Perf.lastPaint<1850){
    se278Perf.throttledPaints++;
    return;
  }
  const started=performance.now();
  const result=se278PriorCanvasRender(panel);
  const took=performance.now()-started;
  if(panel.lastKey){
    se278Perf.lastPaint=now;
    se278Perf.paintPage=page;
    se278Perf.paints++;
    se278Perf.paintCpuMs=took;
    se278Perf.paintCpuMaxMs=Math.max(se278Perf.paintCpuMaxMs,took);
  }
  return result;
};
// Track the existing callback cadence by menu state to distinguish
// extra UI overhead from a busy scene. It is NOT a GPU timestamp or a
// controlled before/after benchmark; the underlying house count may change.
const se278PriorFrame=se193XRFrame;
se193XRFrame=function(...args){
  const result=se278PriorFrame(...args);
  if(!se193XRGameActive()||!renderer.xr?.isPresenting){
    se278Perf.lastSample=0;return result;
  }
  const now=performance.now();
  const dt=se278Perf.lastSample?now-se278Perf.lastSample:0;
  se278Perf.lastSample=now;
  const stats=!!se210UI.panels.get('metrics')?.root?.visible;
  const radial=!!se195.radial?.visible&&!!se195.visible||
    !!se204.wheel?.root?.visible;
  const mode=stats?(radial?'both':'stats'):(radial?'radial':'neither');
  se278Perf.lastMode=mode;
  if(dt>1&&dt<500){
    const bucket=se278Perf.samples[mode];
    bucket.count++;
    bucket.avgMs+=(dt-bucket.avgMs)*Math.min(.22,1/bucket.count);
  }
  return result;
};
function se278SampleLabel(bucket){
  return bucket.count>=8?bucket.avgMs.toFixed(1)+'ms / '+bucket.count+' samples':'not enough samples';
}
// Add the fourth optional Nerd Stats page without replacing fog/house stats.
const se278PreviousStatsLines=se265Lines;
se265Lines=function(snapshot,page){
  if(page===3)return [
    'FRAME CADENCE BY MENU STATE · NOT GPU TIME',
    'BOTH CLOSED  '+se278SampleLabel(se278Perf.samples.neither),
    'NERD ONLY    '+se278SampleLabel(se278Perf.samples.stats),
    'MENU ONLY    '+se278SampleLabel(se278Perf.samples.radial),
    'BOTH OPEN    '+se278SampleLabel(se278Perf.samples.both),
    'PAGE 4/4 · CENTER: NEXT PAGE'
  ];
  const lines=se278PreviousStatsLines(snapshot,page);
  return lines.map(line=>line.replace('PAGE '+(page+1)+'/3','PAGE '+(page+1)+'/4'));
};
const se278PreviousPanelPress=se210PanelPress;
se210PanelPress=function(hit){
  const uv=hit?.uv;
  if(hit?.panel?.kind==='metrics'&&uv&&uv.y>=.17&&uv.y<=.79){
    se265Perf.metricPage=(se265Perf.metricPage+1)%4;
    hit.panel.lastKey='';
    se210CanvasRender(hit.panel);
    return true;
  }
  return se278PreviousPanelPress(hit);
};
const se278PriorCleanup=se193XRCleanup;
se193XRCleanup=function(...args){
  se278Perf.lastSample=0;
  se278Perf.lastPaint=0;
  se278Perf.paintPage=-1;
  for(const bucket of Object.values(se278Perf.samples)){
    bucket.count=0;bucket.avgMs=0;
  }
  return se278PriorCleanup(...args);
};
window.SWYRL_ENGINE_QUEST_MENU_CADENCE_278=Object.freeze({
  diagnose:()=>({
    active:se193XRGameActive()&&!!renderer.xr?.isPresenting,
    leftWristOffsetMeters:se276StatsWrist.offset.toArray(),
    lastMode:se278Perf.lastMode,
    hudPaints:se278Perf.paints,
    skippedHudRepaints:se278Perf.throttledPaints,
    lastHudPaintCpuMs:Number(se278Perf.paintCpuMs.toFixed(2)),
    maxHudPaintCpuMs:Number(se278Perf.paintCpuMaxMs.toFixed(2)),
    callbackCadenceByMenuState:Object.fromEntries(
      Object.entries(se278Perf.samples).map(([name,v])=>
        [name,{samples:v.count,approxMs:v.count?Number(v.avgMs.toFixed(2)):null}])
    ),
    cadenceIsNotGpuTime:true
  })
});
