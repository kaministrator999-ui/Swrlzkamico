"""§wyrl§ Engine v8.1 — graphics scalability, FPS telemetry, and frame-time diagnostics."""
def _once(s,a,b):
    if s.count(a)!=1: raise RuntimeError("v8.1 expected one anchor: "+a[:140])
    return s.replace(a,b,1)

CSS=r"""
<style id="performanceSettingsStyles">
.perf-overlay{position:absolute;z-index:95;top:82px;right:12px;padding:6px 9px;border:1px solid #31445d;border-radius:7px;background:#07111cdd;color:#bfe8ff;font:700 11px/1.25 ui-monospace,monospace;pointer-events:none;white-space:nowrap}
.perf-overlay.warn{color:#ffd48a;border-color:#725a30}.perf-overlay.bad{color:#ff9da9;border-color:#743746}
.perf-settings{position:fixed;z-index:260;inset:0;background:#02070db8;display:none;align-items:center;justify-content:center;padding:16px}.perf-settings.show{display:flex}
.perf-card{width:min(520px,94vw);max-height:88vh;overflow:auto;background:#0d1724;border:1px solid #344a64;border-radius:12px;box-shadow:0 18px 60px #000b;padding:16px;color:#dbe9f8}
.perf-card h2{margin:0 0 4px;font-size:17px}.perf-card .sub{font-size:11px;color:#8fa6bd;margin-bottom:14px}.perf-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px}.perf-field{background:#101d2c;border:1px solid #25384e;border-radius:8px;padding:9px}.perf-field label{display:block;font-size:10px;color:#91a8bf;margin-bottom:5px}.perf-field select,.perf-field input[type=range]{width:100%}.perf-check{display:flex;gap:8px;align-items:center;font-size:12px}.perf-actions{display:flex;gap:8px;justify-content:flex-end;margin-top:14px}.perf-note{font-size:10px;color:#89a0b7;margin-top:10px}
@media(max-width:620px){.perf-overlay{top:70px;right:6px;font-size:9px}.perf-grid{grid-template-columns:1fr}}
</style>
"""

JS=r"""
const PERFORMANCE_PREF_KEY='swyrl.engine.performance.v1';
const PERFORMANCE_PRESETS={
  low:{renderScale:.65,shadows:false,shadowSize:512,maxFps:45},
  medium:{renderScale:.82,shadows:true,shadowSize:1024,maxFps:60},
  high:{renderScale:1,shadows:true,shadowSize:2048,maxFps:0}
};
let performancePrefs={preset:'auto',renderScale:.82,shadows:true,shadowSize:1024,maxFps:60,editorFps:false,playFps:false};
let performanceTelemetry={fps:60,frameMs:16.7,emaMs:16.7,lastNow:performance.now(),frames:0,lastSample:performance.now(),renderLast:0,autoScale:.82,autoLast:0};
function loadPerformancePrefs(){
  try{const v=JSON.parse(localStorage.getItem(PERFORMANCE_PREF_KEY)||'null');if(v&&typeof v==='object')performancePrefs={...performancePrefs,...v}}catch{}
  if(!['auto','low','medium','high','custom'].includes(performancePrefs.preset))performancePrefs.preset='auto';
  performancePrefs.renderScale=THREE.MathUtils.clamp(Number(performancePrefs.renderScale)||.82,.5,1);
  performancePrefs.shadowSize=[512,1024,2048].includes(Number(performancePrefs.shadowSize))?Number(performancePrefs.shadowSize):1024;
  performancePrefs.maxFps=[0,30,45,60].includes(Number(performancePrefs.maxFps))?Number(performancePrefs.maxFps):60;
}
function savePerformancePrefs(){try{localStorage.setItem(PERFORMANCE_PREF_KEY,JSON.stringify(performancePrefs))}catch{}}
function performancePixelRatio(){const scale=performancePrefs.preset==='auto'?performanceTelemetry.autoScale:performancePrefs.renderScale;return Math.min(devicePixelRatio,2)*scale}
function applyPerformanceSettings(){
  const p=PERFORMANCE_PRESETS[performancePrefs.preset];
  if(p)performancePrefs={...performancePrefs,...p,preset:performancePrefs.preset};
  renderer.setPixelRatio(performancePixelRatio());
  renderer.shadowMap.enabled=!!performancePrefs.shadows;
  sun.castShadow=!!performancePrefs.shadows;
  const size=performancePrefs.shadowSize;sun.shadow.mapSize.set(size,size);if(sun.shadow.map){sun.shadow.map.dispose();sun.shadow.map=null}
  savePerformancePrefs();resize();syncPerformanceUI();updatePerformanceOverlay(true);
}
function updateAutoPerformance(now){
  if(performancePrefs.preset!=='auto'||now-performanceTelemetry.autoLast<1800)return;
  performanceTelemetry.autoLast=now;const ms=performanceTelemetry.emaMs;let next=performanceTelemetry.autoScale;
  if(ms>24)next=Math.max(.55,next-.08);else if(ms<17.2)next=Math.min(1,next+.04);
  if(Math.abs(next-performanceTelemetry.autoScale)>.001){performanceTelemetry.autoScale=next;renderer.setPixelRatio(performancePixelRatio());resize()}
}
function samplePerformance(now){
  const delta=Math.max(.1,now-performanceTelemetry.lastNow);performanceTelemetry.lastNow=now;
  performanceTelemetry.emaMs=performanceTelemetry.emaMs*.9+delta*.1;performanceTelemetry.frames++;
  if(now-performanceTelemetry.lastSample>=500){const span=now-performanceTelemetry.lastSample;performanceTelemetry.fps=performanceTelemetry.frames*1000/span;performanceTelemetry.frameMs=performanceTelemetry.emaMs;performanceTelemetry.frames=0;performanceTelemetry.lastSample=now;updatePerformanceOverlay()}
  updateAutoPerformance(now);
}
function shouldRenderFrame(now){
  const cap=performancePrefs.maxFps;if(!cap)return true;
  const interval=1000/cap;if(now-performanceTelemetry.renderLast+0.25<interval)return false;
  performanceTelemetry.renderLast=now;return true;
}
function updatePerformanceOverlay(force=false){
  const d=$('performanceOverlay');if(!d)return;
  const visible=playing?performancePrefs.playFps:performancePrefs.editorFps;
  d.hidden=!visible;if(!visible&&!force)return;
  const fps=performanceTelemetry.fps,ms=performanceTelemetry.frameMs,scale=performancePrefs.preset==='auto'?performanceTelemetry.autoScale:performancePrefs.renderScale;
  d.className='perf-overlay'+(fps<30?' bad':fps<50?' warn':'');
  d.textContent=Math.round(fps)+' FPS · '+ms.toFixed(1)+' ms · '+Math.round(scale*100)+'%'+(performancePrefs.preset==='auto'?' AUTO':'');
}
function syncPerformanceUI(){
  const q=id=>$(id);if(!q('perfPreset'))return;
  q('perfPreset').value=performancePrefs.preset;q('perfScale').value=performancePrefs.renderScale;q('perfScaleValue').textContent=Math.round(performancePrefs.renderScale*100)+'%';
  q('perfShadows').checked=!!performancePrefs.shadows;q('perfShadowSize').value=String(performancePrefs.shadowSize);q('perfMaxFps').value=String(performancePrefs.maxFps);
  q('perfEditorFps').checked=!!performancePrefs.editorFps;q('perfPlayFps').checked=!!performancePrefs.playFps;
}
function installPerformanceSettings(){
  if($('performanceSettings'))return;
  const overlay=document.createElement('div');overlay.id='performanceOverlay';overlay.className='perf-overlay';overlay.hidden=true;($('viewport')?.parentElement||document.body).appendChild(overlay);
  const modal=document.createElement('div');modal.id='performanceSettings';modal.className='perf-settings';modal.innerHTML='<div class="perf-card"><h2>Graphics & Performance</h2><div class="sub">Scalability is engine-local. FPS displays can be enabled independently for Editor and Play.</div><div class="perf-grid"><div class="perf-field"><label>Preset</label><select id="perfPreset"><option value="auto">Auto</option><option value="low">Low</option><option value="medium">Medium</option><option value="high">High</option><option value="custom">Custom</option></select></div><div class="perf-field"><label>Render scale · <span id="perfScaleValue"></span></label><input id="perfScale" type="range" min=".5" max="1" step=".05"></div><div class="perf-field"><label>Shadow quality</label><select id="perfShadowSize"><option value="512">Low · 512</option><option value="1024">Medium · 1024</option><option value="2048">High · 2048</option></select><label class="perf-check"><input id="perfShadows" type="checkbox"> Dynamic shadows</label></div><div class="perf-field"><label>Frame cap</label><select id="perfMaxFps"><option value="0">Unlimited</option><option value="30">30 FPS</option><option value="45">45 FPS</option><option value="60">60 FPS</option></select></div><div class="perf-field"><label class="perf-check"><input id="perfEditorFps" type="checkbox"> Show FPS in Editor</label></div><div class="perf-field"><label class="perf-check"><input id="perfPlayFps" type="checkbox"> Show FPS in Play / Simulate</label></div></div><div class="perf-note">Auto watches sustained frame time and adjusts render resolution only. Gameplay simulation remains requestAnimationFrame-driven and delta-time based.</div><div class="perf-actions"><button id="perfReset">Reset Auto</button><button id="perfClose" class="accent">Done</button></div></div>';document.body.appendChild(modal);
  const custom=()=>{performancePrefs.preset='custom';applyPerformanceSettings()};
  $('perfPreset').onchange=e=>{performancePrefs.preset=e.target.value;if(e.target.value==='auto')performanceTelemetry.autoScale=.82;applyPerformanceSettings()};
  $('perfScale').oninput=e=>{performancePrefs.renderScale=Number(e.target.value);$('perfScaleValue').textContent=Math.round(performancePrefs.renderScale*100)+'%'};$('perfScale').onchange=custom;
  $('perfShadows').onchange=e=>{performancePrefs.shadows=e.target.checked;custom()};$('perfShadowSize').onchange=e=>{performancePrefs.shadowSize=Number(e.target.value);custom()};
  $('perfMaxFps').onchange=e=>{performancePrefs.maxFps=Number(e.target.value);custom()};
  $('perfEditorFps').onchange=e=>{performancePrefs.editorFps=e.target.checked;savePerformancePrefs();updatePerformanceOverlay(true)};
  $('perfPlayFps').onchange=e=>{performancePrefs.playFps=e.target.checked;savePerformancePrefs();updatePerformanceOverlay(true)};
  $('perfReset').onclick=()=>{performancePrefs={preset:'auto',renderScale:.82,shadows:true,shadowSize:1024,maxFps:60,editorFps:performancePrefs.editorFps,playFps:performancePrefs.playFps};performanceTelemetry.autoScale=.82;applyPerformanceSettings()};
  $('perfClose').onclick=()=>modal.classList.remove('show');modal.addEventListener('click',e=>{if(e.target===modal)modal.classList.remove('show')});
  syncPerformanceUI();
}
function openPerformanceSettings(){installPerformanceSettings();syncPerformanceUI();$('performanceSettings').classList.add('show')}
"""

def apply(html):
    s=html
    if "</style>" not in s: raise RuntimeError("v8.1 style anchor missing")
    s=s.replace("</style>",CSS+"</style>",1)
    s=_once(s,"const renderer = new THREE.WebGLRenderer({canvas:$('viewport'), antialias:true});\nrenderer.setPixelRatio(Math.min(devicePixelRatio,2));","const renderer = new THREE.WebGLRenderer({canvas:$('viewport'), antialias:true});\n"+JS+"\nloadPerformancePrefs();\nrenderer.setPixelRatio(performancePixelRatio());")
    s=_once(s,"scene.add(sun);","scene.add(sun);\ninstallPerformanceSettings();applyPerformanceSettings();")
    s=_once(s,"View:[['Focus Selection','focus'],['Frame Selection','frame'],['Top View','top'],['World / Local','space'],['Terrain Snap','terrain'],['sep'],['Outliner','outliner'],['Inspector / Details','inspector']],","View:[['Focus Selection','focus'],['Frame Selection','frame'],['Top View','top'],['World / Local','space'],['Terrain Snap','terrain'],['sep'],['Graphics & Performance','performance'],['Outliner','outliner'],['Inspector / Details','inspector']],")
    s=_once(s,"Tools:[['Workspace Launcher','workspaces'],['Components','components'],['World Tools','world'],['Bake Ghosts','bake'],['sep'],['Input Mapping','input'],['Physics','physics'],['Lighting','lighting'],['Profiler','profiler']],","Tools:[['Workspace Launcher','workspaces'],['Components','components'],['World Tools','world'],['Bake Ghosts','bake'],['sep'],['Graphics & Performance','performance'],['Input Mapping','input'],['Physics','physics'],['Lighting','lighting'],['Profiler','profiler']],")
    # Existing menu action fallback marks unknown tools as planned; make performance a real action.
    s=_once(s,"const action=(key)=>{","const action=(key)=>{\n    if(key==='performance'){openPerformanceSettings();return;}")
    s=_once(s,"function tick(){\n  requestAnimationFrame(tick);resize();const dt=Math.min(clock.getDelta(),0.05),t=performance.now()/1000;const runtimeActive=playing||simulating;","function tick(){\n  requestAnimationFrame(tick);const frameNow=performance.now();samplePerformance(frameNow);resize();const dt=Math.min(clock.getDelta(),0.05),t=frameNow/1000;const runtimeActive=playing||simulating;")
    s=_once(s,"updateWorkspaceInteraction(t);renderer.render(scene,camera);","updateWorkspaceInteraction(t);if(shouldRenderFrame(frameNow))renderer.render(scene,camera);")
    # Make session-mode changes immediately switch the independently configured FPS overlay.
    s=_once(s,"playing=true;simulating=false;paused=false;keepSimulationChanges=false;","playing=true;simulating=false;paused=false;keepSimulationChanges=false;updatePerformanceOverlay(true);")
    s=_once(s,"simulating=true;playing=false;paused=false;keepSimulationChanges=false;","simulating=true;playing=false;paused=false;keepSimulationChanges=false;updatePerformanceOverlay(true);")
    s=_once(s,"playing=false;simulating=false;paused=false;restorePlaySnapshot();applyLayerVisibility();","playing=false;simulating=false;paused=false;restorePlaySnapshot();applyLayerVisibility();updatePerformanceOverlay(true);")
    # v8.0 controller audit: movement/look already use dt. Bound pathological long frames
    # before controller work while preserving the existing 50 ms simulation cap.
    s=_once(s,"function updateHero(dt, t){\n  if(workspacePanelOpen)return;","function updateHero(dt, t){\n  dt=Math.min(Math.max(Number(dt)||0,0),0.05);\n  if(workspacePanelOpen)return;")
    # Promote release surfaces.
    s=s.replace("V8_0_EMBERVAULT_WORKSPACE","V8_1_PERFORMANCE_GRAPHICS")
    s=s.replace("Maker v8.0","Maker v8.1").replace("MAKER v8.0","MAKER v8.1")
    s=s.replace("version:'v8.0'","version:'v8.1'").replace("version:'swyrl-engine-agent-v6.0'","version:'swyrl-engine-agent-v6.1'")
    s=s.replace("version:8.0","version:8.1").replace("v8.0 · EMBERVAULT WORKSPACE","v8.1 · PERFORMANCE + GRAPHICS")
    s=s.replace("§E v8.0 Tools","§E v8.1 Tools")
    s=s.replace("§wyrl§ Engine v8.0 · Embervault Atelier · three-tier workspace ready","§wyrl§ Engine v8.1 · Embervault Atelier · performance controls ready")
    return s
