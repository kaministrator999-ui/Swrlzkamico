// §E v11.380 — extend the existing graphics window without creating a new one.
// Native WebGL antialias is immutable after context creation. FXAA is browser
// only; WebXR owns stereo framebuffer, foveation and compositor timing.
const se380Key='swyrl.engine.graphics.advanced.v1';
const se380Defaults=Object.freeze({aa:'native',anisotropy:4,foveation:'medium',vrScale:'preset',shadowDistance:'normal',lod:'default'});
let se380Prefs={...se380Defaults};
try{const stored=JSON.parse(localStorage.getItem(se380Key)||'null');if(stored&&typeof stored==='object'){
 for(const key of Object.keys(se380Defaults))if(Object.prototype.hasOwnProperty.call(stored,key))se380Prefs[key]=stored[key];
}}catch{}
const se380Choices={aa:['native','fxaa'],anisotropy:[1,2,4,8,16],foveation:['off','low','medium','high'],vrScale:['preset','.55','.60','.65','.70','.75','.80','.85','.90'],shadowDistance:['near','normal','far'],lod:['near','default','far']};
for(const [key,choices] of Object.entries(se380Choices)){
 if(!choices.includes(se380Prefs[key]))se380Prefs[key]=se380Defaults[key];
}
const se380Stats={textures:0,lodObjects:0,nativeAA:!!renderer.getContext?.()?.getContextAttributes?.()?.antialias,
 maxAnisotropy:Math.max(1,Number(renderer.capabilities?.getMaxAnisotropy?.()||1)),lastScan:0,
 xrFoveation:'not applied',xrScale:'preset',fxaaFrames:0,fxaaAllocations:0};
const se380TexKeys=['map','alphaMap','aoMap','bumpMap','normalMap','roughnessMap','metalnessMap','emissiveMap','displacementMap','lightMap','envMap','specularMap','clearcoatMap'];
const se380LODOriginal=new WeakMap();
const se380ShadowCamera=sun?.shadow?.camera;
const se380ShadowOriginal=se380ShadowCamera?{
 left:se380ShadowCamera.left,right:se380ShadowCamera.right,
 top:se380ShadowCamera.top,bottom:se380ShadowCamera.bottom}:null;
function se380Save(){try{localStorage.setItem(se380Key,JSON.stringify(se380Prefs))}catch{}}
function se380ScanScene(){
 const limit=Math.max(1,Math.min(Number(se380Prefs.anisotropy)||1,se380Stats.maxAnisotropy));
 const textures=new Set();let count=0;
 scene.traverse?.(object=>{
  if(object.isLOD&&Array.isArray(object.levels)){
   if(!se380LODOriginal.has(object))se380LODOriginal.set(object,object.levels.map(level=>level.distance));
   const baseline=se380LODOriginal.get(object),mult={near:.7,default:1,far:1.5}[se380Prefs.lod];
   object.levels.forEach((level,i)=>{if(Number.isFinite(baseline[i]))level.distance=baseline[i]*mult;});
   count++;
  }
  if(!object.material)return;
  const materials=Array.isArray(object.material)?object.material:[object.material];
  for(const material of materials){
   if(!material)continue;
   for(const key of se380TexKeys){
    const tex=material[key];
    if(!tex?.isTexture||textures.has(tex))continue;
    textures.add(tex);
    // Changing the effective anisotropy is a texture sampler change only;
    // do not reload asset images, recalc UVs or modify material color.
    if(tex.anisotropy!==limit){tex.anisotropy=limit;tex.needsUpdate=true;}
   }
  }
 });
 se380Stats.textures=textures.size;se380Stats.lodObjects=count;se380Stats.lastScan=performance.now();
}
function se380ApplyShadowDistance(){
 if(!se380ShadowCamera||!se380ShadowOriginal)return;
 const factor={near:.62,normal:1,far:1.25}[se380Prefs.shadowDistance];
 for(const edge of ['left','right','top','bottom']){
  const base=se380ShadowOriginal[edge];
  if(Number.isFinite(base))se380ShadowCamera[edge]=base*factor;
 }
 se380ShadowCamera.updateProjectionMatrix?.();
}
function se380ApplyFoveation(){
 if(!renderer.xr?.isPresenting){se380Stats.xrFoveation='next VR entry';return;}
 if(typeof renderer.xr.setFoveation!=='function'){
  se380Stats.xrFoveation='unsupported by this XR renderer';return;
 }
 const wanted={off:0,low:.25,medium:.5,high:1}[se380Prefs.foveation];
 try{
  renderer.xr.setFoveation(wanted);
  const actual=renderer.xr.getFoveation?.();
  se380Stats.xrFoveation=Number.isFinite(actual)?String(actual):'requested '+wanted+'; not reported';
 }catch(error){se380Stats.xrFoveation='unavailable: '+String(error?.message||error).slice(0,70);}
}
renderer.xr?.addEventListener?.('sessionstart',se380ApplyFoveation);
renderer.xr?.addEventListener?.('sessionend',()=>{se380Stats.xrFoveation='next VR entry';});
// The v11.379 preset-aware Sheep Tag XR scale remains the default. An
// explicit user override is sampled at the *next* XR entry; never resize
// the headset's active stereo target in-flight.
const se380PreviousFramebuffer=se191XRPrepareFramebuffer;
se191XRPrepareFramebuffer=function(){
 if(currentProject?.kind!=='sheep-tag'||se380Prefs.vrScale==='preset'){
  se380Stats.xrScale='preset';return se380PreviousFramebuffer();
 }
 const value=Number(se380Prefs.vrScale);
 if(!Number.isFinite(value)||value<.55||value>.9)return se380PreviousFramebuffer();
 se191XR.framebufferScale=value;
 se380Stats.xrScale=value;
 se379Frame.lastPreset=String(performancePrefs.preset||'auto')+' + advanced override';
 se379Frame.lastXRScale=value;
 se379Frame.framebufferChoices++;
 return se195OriginalFramebuffer();
};
// A deliberately isolated extra fullscreen browser pass. This is NOT
// injected into WebXR's stereo loop, and it leaves the native context MSAA
// configuration untouched. Browser-only FXAA trades GPU cost for smoother edges.
let se380FXAA=null;
const se380OriginalRender=renderer.render.bind(renderer);
function se380EnsureFXAA(w,h){
 if(!se380FXAA){
  const material=new THREE.ShaderMaterial({
   depthTest:false,depthWrite:false,toneMapped:false,
   uniforms:{tDiffuse:{value:null},invSize:{value:new THREE.Vector2(1/w,1/h)}},
   vertexShader:'varying vec2 uv0; void main(){uv0=uv;gl_Position=vec4(position.xy,0.0,1.0);}',
   fragmentShader:`precision mediump float;
   varying vec2 uv0;uniform sampler2D tDiffuse;uniform vec2 invSize;
   float lum(vec3 c){return dot(c,vec3(0.299,0.587,0.114));}
   void main(){
    vec3 nw=texture2D(tDiffuse,uv0+vec2(-1.,-1.)*invSize).rgb;
    vec3 ne=texture2D(tDiffuse,uv0+vec2(1.,-1.)*invSize).rgb;
    vec3 sw=texture2D(tDiffuse,uv0+vec2(-1.,1.)*invSize).rgb;
    vec3 se=texture2D(tDiffuse,uv0+vec2(1.,1.)*invSize).rgb;
    vec4 center=texture2D(tDiffuse,uv0);
    float l=lum(center.rgb),lMin=min(l,min(min(lum(nw),lum(ne)),min(lum(sw),lum(se))));
    float lMax=max(l,max(max(lum(nw),lum(ne)),max(lum(sw),lum(se))));
    vec2 dir=vec2(-((lum(nw)+lum(ne))-(lum(sw)+lum(se))),
                   ((lum(nw)+lum(sw))-(lum(ne)+lum(se))));
    float reduce=max((lum(nw)+lum(ne)+lum(sw)+lum(se))*.03125,.0078125);
    float inv=1.0/(min(abs(dir.x),abs(dir.y))+reduce);
    dir=clamp(dir*inv,vec2(-8.),vec2(8.))*invSize;
    vec3 a=.5*(texture2D(tDiffuse,uv0+dir*(1./3.-.5)).rgb+
                 texture2D(tDiffuse,uv0+dir*(2./3.-.5)).rgb);
    vec3 b=a*.5+.25*(texture2D(tDiffuse,uv0+dir*-.5).rgb+
                      texture2D(tDiffuse,uv0+dir*.5).rgb);
    gl_FragColor=vec4(lum(b)<lMin||lum(b)>lMax?a:b,center.a);
    #include <colorspace_fragment>
   }`
  });
  const quad=new THREE.Mesh(new THREE.PlaneGeometry(2,2),material);
  quad.frustumCulled=false;
  const pass=new THREE.Scene();pass.add(quad);
  se380FXAA={target:new THREE.WebGLRenderTarget(w,h,{depthBuffer:true,stencilBuffer:false}),
   scene:pass,camera:new THREE.OrthographicCamera(-1,1,1,-1,0,1),material,w,h};
  se380Stats.fxaaAllocations++;
 }else if(se380FXAA.w!==w||se380FXAA.h!==h){
  se380FXAA.target.setSize(w,h);se380FXAA.w=w;se380FXAA.h=h;
 }
 se380FXAA.material.uniforms.invSize.value.set(1/w,1/h);
 return se380FXAA;
}
renderer.render=function(sceneArg,cameraArg){
 const enabled=se380Prefs.aa==='fxaa'&&!renderer.xr?.isPresenting&&sceneArg===scene&&
  !renderer.getRenderTarget?.();
 if(!enabled)return se380OriginalRender(sceneArg,cameraArg);
 const w=Math.max(1,renderer.domElement?.width||1),h=Math.max(1,renderer.domElement?.height||1);
 const fxaa=se380EnsureFXAA(w,h);
 renderer.setRenderTarget(fxaa.target);
 try{se380OriginalRender(sceneArg,cameraArg);}finally{renderer.setRenderTarget(null);}
 fxaa.material.uniforms.tDiffuse.value=fxaa.target.texture;
 se380OriginalRender(fxaa.scene,fxaa.camera);
 se380Stats.fxaaFrames++;
 return;
};
function se380Value(key,value){
 if(!se380Choices[key]?.includes(value))return;
 se380Prefs[key]=value;se380Save();
 if(key==='foveation')se380ApplyFoveation();
 if(key==='anisotropy'||key==='lod')se380ScanScene();
 if(key==='shadowDistance')se380ApplyShadowDistance();
 se380RefreshStatus();
}
function se380Field(parent,label,options,key,help){
 const field=document.createElement('div');field.className='perf-field';
 const heading=document.createElement('label');heading.textContent=label;field.appendChild(heading);
 const select=document.createElement('select');select.id='se380-'+key;
 for(const [value,name] of options){const option=document.createElement('option');option.value=String(value);option.textContent=name;select.appendChild(option);}
 select.value=String(se380Prefs[key]);select.addEventListener('change',()=>se380Value(key,key==='anisotropy'?Number(select.value):select.value));
 field.appendChild(select);
 if(help){const hint=document.createElement('div');hint.className='se380-field-note';hint.textContent=help;field.appendChild(hint);}
 parent.appendChild(field);return select;
}
let se380ActiveTab='graphics';
function se380Tab(next){
 se380ActiveTab=next;
 for(const key of ['graphics','performance','vr']){
  const panel=document.getElementById('se380-panel-'+key);
  const tab=document.getElementById('se380-tab-'+key);
  if(panel)panel.hidden=key!==next;
  if(tab){tab.setAttribute('aria-selected',String(key===next));tab.tabIndex=key===next?0:-1;}
 }
 se380RefreshStatus();
}
function se380RefreshStatus(){
 const status=document.getElementById('se380-status');if(!status)return;
 const browserAA=se380Stats.nativeAA?'enabled':'not available';
 const foveation=renderer.xr?.isPresenting?se380Stats.xrFoveation:'applies during VR';
 const diag=window.SWYRL_ENGINE_SHEEP_VR_CADENCE_379?.diagnose?.();
 status.textContent='Browser native AA: '+browserAA+' · FXAA: '+(se380Prefs.aa==='fxaa'?'enabled (browser only)':'off')+
  ' · texture filtering: '+Math.min(se380Prefs.anisotropy,se380Stats.maxAnisotropy)+'× / '+se380Stats.maxAnisotropy+'× max'+
  '\nScene: '+se380Stats.textures+' textured maps · '+se380Stats.lodObjects+' authored LOD objects'+
  '\nXR foveation: '+foveation+' · XR scale: '+(diag?.xrFramebufferScaleAtEntry??'not sampled')+
  '\nWebGL draws: '+(se189Profile?.drawCalls??'n/a')+' · triangles: '+(se189Profile?.triangles??'n/a')+
  '\nMeasurements are CPU-submission/estimated frame cadence, not actual headset GPU time.';
}
function se380InstallUI(){
 const modal=document.getElementById('performanceSettings');
 if(!modal||document.getElementById('se380-tabs'))return;
 const card=modal.querySelector('.perf-card'),oldGrid=card?.querySelector('.perf-grid');
 if(!oldGrid)return;
 const bar=document.createElement('div');bar.id='se380-tabs';bar.setAttribute('role','tablist');
 const panels={};
 for(const [id,title] of [['graphics','Graphics'],['performance','Performance'],['vr','VR']]){
  const tab=document.createElement('button');tab.type='button';tab.id='se380-tab-'+id;
  tab.textContent=title;tab.setAttribute('role','tab');tab.setAttribute('aria-controls','se380-panel-'+id);
  tab.addEventListener('click',()=>se380Tab(id));bar.appendChild(tab);
  const panel=document.createElement('section');panel.id='se380-panel-'+id;
  panel.setAttribute('role','tabpanel');panel.className='se380-panel';panel.hidden=id!=='graphics';
  panels[id]=panel;
 }
 card.insertBefore(bar,oldGrid);
 const graphicsGrid=document.createElement('div');graphicsGrid.className='perf-grid';
 const perfGrid=document.createElement('div');perfGrid.className='perf-grid';
 const vrGrid=document.createElement('div');vrGrid.className='perf-grid';
 for(const field of [...oldGrid.children]){
  const performanceControl=field.querySelector('#perfMaxFps, #perfEditorFps, #perfPlayFps');
  (performanceControl?perfGrid:graphicsGrid).appendChild(field);
 }
 oldGrid.replaceWith(panels.graphics,panels.performance,panels.vr);
 panels.graphics.appendChild(graphicsGrid);
 panels.performance.appendChild(perfGrid);
 panels.vr.appendChild(vrGrid);
 se380Field(graphicsGrid,'Anti-aliasing (browser)',[['native','Native MSAA (as available)'],['fxaa','Native + FXAA smoothing']],'aa',
  'WebGL native AA cannot be disabled without recreating the canvas; FXAA adds a browser-only GPU pass.');
 se380Field(graphicsGrid,'Texture filtering',[[1,'1× basic'],[2,'2×'],[4,'4×'],[8,'8×'],[16,'16×']],'anisotropy',
  'Limited to hardware capability; improves oblique terrain/material textures.');
 se380Field(graphicsGrid,'Shadow coverage',[["near",'Near · faster'],['normal','Normal'],['far','Far · more coverage']],'shadowDistance',
  'Adjusts the existing sunlight shadow camera; does not change shadows inside XR menus.');
 se380Field(graphicsGrid,'Authored LOD distance',[["near",'Switch earlier'],['default','As authored'],['far','Switch later']],'lod',
  'Only changes actual Three.js LOD objects. Never removes interactive game actors.');
 se380Field(vrGrid,'Quest foveation',[["off",'Off'],['low','Low'],['medium','Medium'],['high','High']],'foveation',
  'Only when WebXR runtime supports it. Does not change tracking or refresh rate.');
 se380Field(vrGrid,'Sheep Tag VR render scale',[["preset",'Follow graphics preset'],['.55','55%'],['.60','60%'],['.65','65%'],['.70','70%'],['.75','75%'],['.80','80%'],['.85','85%'],['.90','90%']],'vrScale',
  'Resolution changes take effect when re-entering VR; no mid-session stereo reallocations.');
 const browserNote=document.createElement('p');browserNote.className='perf-note';
 browserNote.textContent='Browser Auto already adjusts render resolution based on measured callback cadence. In VR the native headset owns display timing; the browser FPS cap does not set Quest refresh rate.';
 panels.performance.appendChild(browserNote);
 const vrNote=document.createElement('p');vrNote.className='perf-note';
 vrNote.textContent='VR anti-aliasing is controlled by the XR compositor/framebuffer. Browser FXAA is intentionally disabled inside the headset.';
 panels.vr.appendChild(vrNote);
 for(const sel of ['.se190-perf-actions','#se190Comparison','#se190AuditResults','#se189PerfMetrics']){
  const element=card.querySelector(sel);if(element)panels.performance.appendChild(element);
 }
 const status=document.createElement('pre');status.id='se380-status';status.className='se380-status';
 status.textContent='Graphics capability diagnostics';panels.performance.appendChild(status);
 const refresh=document.createElement('button');refresh.type='button';refresh.textContent='Refresh graphics diagnostics';
 refresh.className='se380-refresh';refresh.addEventListener('click',()=>{se380ScanScene();se380RefreshStatus();});
 panels.performance.appendChild(refresh);
 const actions=card.querySelector('.perf-actions');
 const boost=document.getElementById('se189MobileBoost');if(boost)panels.performance.insertBefore(boost,perfGrid);
 const intro=card.querySelector('.sub');if(intro)intro.textContent='Renderer controls shared by Model Studio and games. XR overrides apply separately.';
 if(actions)actions.classList.add('se380-footer');
 se380Tab('graphics');se380ScanScene();se380ApplyShadowDistance();
}
const se380PreviousOpen=openPerformanceSettings;
openPerformanceSettings=function(){se380PreviousOpen();se380InstallUI();se380RefreshStatus();};
// The original settings bootstrap precedes this append-only runtime helper.
se380InstallUI();
renderer.xr?.isPresenting&&se380ApplyFoveation();
// No additional frame loop: periodic texture/LOD discovery piggybacks on
// existing render calls, and is skipped outside the open settings panel.
const se380LayerRender=renderer.render;
renderer.render=function(s,c){
 if(s===scene&&!renderer.xr?.isPresenting&&
    document.getElementById('performanceSettings')?.classList.contains('show')&&
    performance.now()-se380Stats.lastScan>5000)se380ScanScene();
 return se380LayerRender(s,c);
};
window.SWYRL_ENGINE_ADVANCED_GRAPHICS_380=Object.freeze({
 snapshot:()=>({...se380Prefs,...se380Stats,foveationActuallyReported:renderer.xr?.getFoveation?.()??null,
  browserNativeAntialias:se380Stats.nativeAA,live:!!renderer.xr?.isPresenting}),
 rescan:()=>{se380ScanScene();se380RefreshStatus();return se380Stats.textures},
 open:()=>openPerformanceSettings()
});