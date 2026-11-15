'use strict';
// Real-headless mobile startup smoke: the editor must leave scene/tool sync.
// Run from repo root with playwright installed and /tmp/se461-browser built.
const {chromium}=require('playwright');
const fs=require('node:fs'),path=require('node:path');
const root='/tmp/se461-browser';
const browserHost='https://kamiloki-swrlz-forge-moba.hf.space';
const deadline=setTimeout(()=>{console.error('SE461_BROWSER_HARD_TIMEOUT');process.exit(9)},75000);
(async()=>{
 const browser=await chromium.launch({headless:true,
  args:['--no-sandbox','--enable-unsafe-swiftshader','--disable-web-security']});
 const page=await browser.newPage({viewport:{width:412,height:915},isMobile:true,hasTouch:true,deviceScaleFactor:2});
 const errors=[],failed=[];
 page.on('pageerror',e=>{errors.push(String(e.stack||e));console.log('SE461_BROWSER_PAGEERROR '+String(e.stack||e).slice(0,1100))});
 page.on('requestfailed',r=>failed.push({url:r.url(),reason:r.failure()?.errorText}));
 page.on('console',m=>{if(m.type()==='error')console.log('SE461_BROWSER_CONSOLE_ERROR '+m.text().slice(0,350))});
 await page.route(browserHost+'/**',async route=>{
  const u=new URL(route.request().url());
  const name=decodeURIComponent(u.pathname).replace(/^\/+/,'')||'index.html';
  const target=path.resolve(root,name);
  if(!target.startsWith(root+path.sep)||!fs.existsSync(target)||!fs.statSync(target).isFile()){
   return route.fulfill({status:404,body:'Not found'});
  }
  const b=fs.readFileSync(target);
  const ext=path.extname(target).toLowerCase();
  const type={'.html':'text/html','.js':'text/javascript','.css':'text/css',
   '.json':'application/json','.png':'image/png','.jpg':'image/jpeg',
   '.webp':'image/webp','.glb':'model/gltf-binary'}[ext]||'application/octet-stream';
  return route.fulfill({status:200,body:b,contentType:type});
 });
 await page.goto(browserHost+'/modeler.html',{waitUntil:'domcontentloaded',timeout:35000});
 await page.waitForTimeout(9500);
 const result=await page.evaluate(()=>{
  const p=document.querySelector('#modelAtelierPanel');
  const bodyText=(document.body?.innerText||'').slice(0,1300);
  const status=[...document.querySelectorAll('[role="status"],.statusbar,.loading,.loading-status')]
   .filter(x=>{const css=getComputedStyle(x);return x.getBoundingClientRect().height>0&&
     css.display!=='none'&&css.visibility!=='hidden'&&Number(css.opacity)>.1;})
   .map(x=>x.textContent.trim().slice(0,180)).slice(0,15);
  return {documentReady:document.readyState,
   version:window.SWRLZ_FORGE_BUILD?.version||null,
   editorReady:document.documentElement.classList.contains('se127-editor-ready'),
   splashVisibility:getComputedStyle(document.getElementById('se185Init')).visibility,
   panelPresent:!!p,panelVisible:!!p&&!p.hidden,
   hasViewport:!!p?.querySelector('canvas'),
   toolRail:!!p?.querySelector('#modelAtelierToolRail'),
   topText:bodyText,visibleStatuses:status,
   helper:window.SWYRL_ENGINE_MODEL_VIEW_STABILITY_458?.inspect?.()||null};
 });
 console.log('SE461_BROWSER_RESULT '+JSON.stringify(result));
 console.log('SE461_BROWSER_REQUESTS_FAILED '+JSON.stringify(failed.slice(0,16)));
 console.log('SE461_BROWSER_ERRORS '+JSON.stringify(errors.slice(0,12)));

 if(result.version!=='v11.461')throw Error('Engine build version never initialized in browser');

 const native=await page.evaluate(()=>({
  view:window.SWYRL_ENGINE_MODEL_VIEW?.inspect?.()||null,
  camera:window.SWYRL_ENGINE_MODEL_CAMERA?.inspect?.()||null
 }));
 console.log('SE461_NATIVE_BRIDGE_READY '+JSON.stringify(native));
 if(!native.view?.available||!native.camera?.ready)
  throw Error('Native Model Atelier scene/view or camera bridge is not ready');
 // The release-notes dialog intentionally blocks UI until dismissed.
 // Close it as a normal prerequisite for inspecting the Model Studio controls.
 await page.evaluate(()=>{const notes=document.querySelector('#seReleaseNotesDialog[open]');
  if(notes&&typeof notes.close==='function')notes.close();});
 const clicks=[];
 for(const mode of ['shaded','overlay','wireframe','xray','flat','clay','solid']){
  await page.locator('#se455ViewButton').click({timeout:7000});
  if(mode==='xray'){
   const layout=await page.evaluate(()=>{
    const x=document.querySelector('[data-se455-mode="xray"]');
    const root=document.querySelector('#se455ViewSwitch');
    const menu=document.querySelector('#se455ViewMenu');
    const controls=document.querySelector('.atelier-viewport-controls');
    const zoom=document.querySelector('#modelAtelierZoomOut');
    const b=x?.getBoundingClientRect(),point=b&&{x:b.x+b.width/2,y:b.y+b.height/2};
    const hit=point?document.elementFromPoint(point.x,point.y):null;
    const info=e=>e?{z:getComputedStyle(e).zIndex,position:getComputedStyle(e).position,
      transform:getComputedStyle(e).transform,rect:(()=>{let r=e.getBoundingClientRect();return [r.x,r.y,r.width,r.height]})()}:null;
    return {point,hit:hit?.outerHTML?.slice(0,230),xray:info(x),menu:info(menu),
      switch:info(root),viewportControls:info(controls),zoom:info(zoom),
      scene:info(document.querySelector('.atelier-scene'))};
   });
   console.log('SE461_VIEW_LAYOUT_DIAGNOSTIC '+JSON.stringify(layout));
  }
  await page.locator('[data-se455-mode="'+mode+'"]').click({timeout:7000});
  const current=await page.evaluate(()=>({
   mode:window.SWYRL_ENGINE_MODEL_VIEW?.inspect?.()?.mode,
   label:document.querySelector('#se455ViewButton')?.textContent,
   expanded:document.querySelector('#se455ViewMenu')?.hidden
  }));
  clicks.push({kind:'display',request:mode,...current});
  if(current.mode!==mode)throw Error('Display '+mode+' failed: '+JSON.stringify(current));
 }
 for(const view of ['front','right','top','three']){
  await page.locator('#se455ViewButton').click({timeout:7000});
  await page.locator('[data-se455-camera="'+view+'"]').click({timeout:7000});
  const current=await page.evaluate(()=>({
   camera:window.SWYRL_ENGINE_MODEL_CAMERA?.inspect?.(),
   view:window.SWYRL_ENGINE_MODEL_VIEW?.inspect?.()
  }));
  clicks.push({kind:'camera',request:view,observed:current.camera?.view});
  if(current.camera?.view!==view)throw Error('Camera '+view+' failed: '+JSON.stringify(current));
 }
 console.log('SE461_VIEW_BUTTON_CLICKS '+JSON.stringify(clicks));
 console.log('SE461_VIEW_PANEL_ACCEPTANCE_PASS: 7 display modes and 4 camera presets changed native state through actual touch-capable browser clicks');


 // Test the viewport as a wide desktop layout on a touch-capable mobile page.
 // The user's browser shows all four model columns even though the phone is
 // narrow; the native compact mode intentionally hides splitters.
 await page.setViewportSize({width:980,height:915});
 await page.waitForTimeout(420);
 const bounds=await page.evaluate(()=>{
  const root=document.querySelector('#modelAtelierPanel');
  const grip=side=>{
   const e=document.querySelector('#se251-split-model-'+side);
   const b=e?.getBoundingClientRect();
   if(!b)return null;
   const x=b.x+b.width/2,y=b.y+b.height/2;
   return {x,y,w:b.width,h:b.height,hit:document.elementFromPoint(x,y)?.id||null};
  };
  return {layout:root?.dataset.se251Layout,left:grip('left'),right:grip('right'),
   widths:[root?.style.getPropertyValue('--se251-left'),root?.style.getPropertyValue('--se251-right')]};
 });
 console.log('SE461_MOBILE_SPLITTER_BOUNDS '+JSON.stringify(bounds));
 if(bounds.layout!=='desktop')throw Error('Wide touch layout should expose native desktop dock');
 for(const side of ['left','right']){
  const g=bounds[side];
  if(!g||g.w<25||g.h<20||g.hit!=='se251-split-model-'+side)
   throw Error('Mobile '+side+' splitter is not tappable: '+JSON.stringify(g));
  const id=side==='left'?'--se251-left':'--se251-right';
  const before=await page.evaluate(key=>parseFloat(document.querySelector('#modelAtelierPanel').style.getPropertyValue(key)),id);
  const client=await page.context().newCDPSession(page);
  await client.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:g.x,y:g.y}]});
  const direction=side==='left'?1:-1;
  for(let i=1;i<=7;i++)
   await client.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x:g.x+direction*6*i,y:g.y}]});
  await client.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
  await client.detach();
  const after=await page.evaluate(key=>parseFloat(document.querySelector('#modelAtelierPanel').style.getPropertyValue(key)),id);
  console.log('SE461_MOBILE_SPLITTER_DRAG '+JSON.stringify({side,before,after}));
  if(!(after>before+12))
   throw Error('Touch drag failed to resize '+side+' panel: '+before+' → '+after);
 }
 console.log('SE461_BOTH_TOUCH_SPLITTERS_PASS: actual left/right touch resize on desktop-style mobile viewport');

 // Put a real native cube into the blank model. The production source still
 // owns creation; this only drives its already-installed Add control.
 const cubeAdded=await page.evaluate(()=>{
  const native=document.getElementById('modelAtelierAdd');
  if(!native)return false;
  native.click();return true;
 });
 if(!cubeAdded)throw Error('Native Add cube command missing from model');
 await page.waitForTimeout(350);
 const mesh=await page.evaluate(()=>({
  camera:window.SWYRL_ENGINE_MODEL_CAMERA?.inspect?.(),
  pivot:window.SWYRL_ENGINE_MODEL_HARD_SURFACE_461?.inspect?.()
 }));
 console.log('SE461_REAL_CUBE_INITIAL '+JSON.stringify(mesh));
 if(!mesh.pivot?.bounds)throw Error('Created native cube is absent from the orbit bounds');
 // A one-finger canvas drag should orbit the box and reacquire its actual
 // world-space center without changing yaw/pitch presets or zoom distance.
 const canvas=page.locator('#modelAtelierViewport canvas');
 const b=await canvas.boundingBox();
 if(!b)throw Error('Model viewport canvas is missing');
 const x=b.x+b.width*.54,y=b.y+b.height*.59;
 const client=await page.context().newCDPSession(page);
 await client.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x,y}]});
 for(let i=1;i<=8;i++)
  await client.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x:x+8*i,y:y+2*i}]});
 await client.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
 await client.detach();
 const after=await page.evaluate(()=>({
  camera:window.SWYRL_ENGINE_MODEL_CAMERA?.inspect?.(),
  pivot:window.SWYRL_ENGINE_MODEL_HARD_SURFACE_461?.inspect?.()
 }));
 console.log('SE461_REAL_CUBE_AFTER_ORBIT '+JSON.stringify(after));
 const drift=Math.hypot(...after.pivot.bounds.map((v,i)=>v-after.camera.target[i]));
 if(drift>.08)throw Error('Actual one-finger orbit is NOT centered on native cube: drift '+drift);
 if(Math.abs(after.camera.distance-mesh.camera.distance)>.001)
  throw Error('Orbit alignment silently reset zoom/distance');
 if(Math.abs(after.pivot.yaw-mesh.pivot.yaw)<.015)
  throw Error('Actual one-finger gesture failed to rotate camera about model');
 console.log('SE461_MODEL_CENTERED_MOBILE_ORBIT_PASS: native cube pivot exact, yaw changed, zoom preserved');

 if(!result.editorReady||result.splashVisibility!=='hidden')
  throw Error('Initial loading screen is actually displayed over the editor');
 if(!result.panelPresent||!result.toolRail)throw Error('Model Studio tool rail did not initialize');
 if(!result.hasViewport)throw Error('Model Studio canvas did not initialize');
 if(/Synchronizing scene and tools|Startup is taking longer than expected/i.test(result.visibleStatuses.join(' ')))
  throw Error('Scene/tools startup warning still visible after initialization');
 const fatal=errors.filter(e=>/ReferenceError|SyntaxError|TypeError|atelierViewModeApply|se458|se459|se460/i.test(e));
 if(fatal.length)throw Error('Native JS exception after view clicks: '+fatal.slice(0,3).join('; '));
 console.log('SE461_REAL_BROWSER_BOOT_PASS: v11.461 page and Model Studio canvas/tool rail initialized without fatal script errors');
 await browser.close();clearTimeout(deadline);
 process.exit(0);
})().catch(e=>{clearTimeout(deadline);console.error('SE461_REAL_BROWSER_BOOT_FAIL '+(e.stack||e));process.exit(1)});
