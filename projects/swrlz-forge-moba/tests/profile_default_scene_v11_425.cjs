'use strict';
const {chromium}=require('playwright');
const fs=require('node:fs'),path=require('node:path');
const ROOT='/tmp/se425-browser';
const HTML=fs.readFileSync(path.join(ROOT,'index.html'),'utf8');
let done=false;
setTimeout(()=>{if(!done){console.log('SE425_WATCHDOG_TERMINATE');process.exit(3);}},45000);
(async()=>{
 const original='se128LaunchStartupProject();';
 console.log('SE425_BUILD',JSON.stringify({bytes:Buffer.byteLength(HTML),launchCalls:HTML.split(original).length-1,
   denDeclarations:(HTML.match(/function loadCanonicalGlitchDen\(\)\s*\{/g)||[]).length,
   sceneLoads:(HTML.match(/function loadProject\s*\(/g)||[]).length,
   st127Ready:HTML.includes('se127-editor-ready')}));
 const browser=await chromium.launch({headless:true,args:['--no-sandbox','--enable-unsafe-swiftshader','--disable-dev-shm-usage']});
 const page=await browser.newPage({viewport:{width:390,height:820},isMobile:true,hasTouch:true});
 const cd=await page.context().newCDPSession(page);
 await cd.send('Profiler.enable');await cd.send('Profiler.start');
 const errors=[],markers=[];
 page.on('pageerror',e=>{errors.push(e.stack);console.log('SE425_PAGE_ERROR',e.message);});
 page.on('console',m=>{
  const t=m.text();if(t.startsWith('SE425_')){markers.push(t);console.log('SE425_BROWSER',t);}
  if(m.type()==='error')errors.push('console:'+t);
 });
 let altered=HTML;
 altered=altered.replace(original,"console.log('SE425_BEFORE_STARTER');"+original+"console.log('SE425_AFTER_STARTER');");
 altered=altered.replace(/function loadCanonicalGlitchDen\(\)\s*\{/,match=>match+"console.log('SE425_DEN_ENTER');");
 const denStart=altered.indexOf('function loadCanonicalGlitchDen(){');
 if(denStart>=0){
  const limit=altered.indexOf('function createProjectFromTemplate(',denStart);
  if(limit>denStart){
   let block=altered.slice(denStart,limit);
   block=block.replace('const p=structuredClone(CANONICAL_GLITCH_DEN_PROJECT);',
    "console.log('SE425_DEN_CLONE_START');const p=structuredClone(CANONICAL_GLITCH_DEN_PROJECT);console.log('SE425_DEN_CLONE_DONE',p?.scene?.actors?.length);");
   block=block.replace('loadProject(p);',"console.log('SE425_DEN_LOAD_START');loadProject(p);console.log('SE425_DEN_LOAD_DONE');");
   block=block.replace("initializeHistory('Opened canonical Glitch Dragon Den');",
    "console.log('SE425_DEN_HISTORY_START');initializeHistory('Opened canonical Glitch Dragon Den');console.log('SE425_DEN_HISTORY_DONE');");
   altered=altered.slice(0,denStart)+block+altered.slice(limit);
  }
 }
 altered=altered.replace(/function loadProject\s*\([^)]*\)\s*\{/,
  match=>match+"console.log('SE425_NATIVE_LOADPROJECT_ENTER');");
 await page.route('https://kamiloki-swrlz-forge-moba.hf.space/**',route=>{
  const pathname=decodeURIComponent(new URL(route.request().url()).pathname).replace(/^\//,'')||'index.html';
  const file=path.join(ROOT,pathname);
  if(!file.startsWith(ROOT)||!fs.existsSync(file))return route.fulfill({status:404,body:'not found'});
  const type=pathname.endsWith('.html')?'text/html':pathname.endsWith('.js')?'application/javascript':pathname.endsWith('.json')?'application/json':'application/octet-stream';
  return route.fulfill({status:200,contentType:type,body:pathname==='index.html'?altered:fs.readFileSync(file)});
 });
 await page.goto('https://kamiloki-swrlz-forge-moba.hf.space/index.html',{waitUntil:'commit',timeout:12000});
 await new Promise(r=>setTimeout(r,13500));
 try{
  const {profile}=await Promise.race([cd.send('Profiler.stop'),new Promise((_,rej)=>setTimeout(()=>rej(Error('CDP profiler timeout')),5000))]);
  const hits=new Map(),nodes=new Map(profile.nodes.map(n=>[n.id,n]));
  for(const id of profile.samples||[]){
   const n=nodes.get(id);if(!n)continue;
   const name=(n.callFrame?.functionName||'(anonymous)')+' @ '+(n.callFrame?.url||'').split('/').pop()+':'+n.callFrame?.lineNumber;
   hits.set(name,(hits.get(name)||0)+1);
  }
  console.log('SE425_CPU_TOP',JSON.stringify([...hits].sort((a,b)=>b[1]-a[1]).slice(0,22)));
 }catch(e){console.log('SE425_CPU_ERROR',e.message);}
 try{
  const shot=await Promise.race([page.evaluate(()=>({ready:document.readyState,
   splash:document.getElementById('se185BootStage')?.textContent,
   version:window.SWRLZ_FORGE_BUILD?.version,
   tabs:[...document.querySelectorAll('.se170-hub-tabs button')].map(x=>x.textContent),
   editor:window.SWYRL_ENGINE_LEVELS?.status?.(),
   actorsText:[...document.querySelectorAll('footer')].map(x=>x.innerText.slice(0,150))})),
   new Promise((_,rej)=>setTimeout(()=>rej(Error('DOM snapshot blocked')),3500))]);
  console.log('SE425_DOM',JSON.stringify(shot));
 }catch(e){console.log('SE425_DOM_ERROR',e.message);}
 console.log('SE425_RESULT',JSON.stringify({errors:errors.slice(0,5),marks:markers.length}));
 done=true;await Promise.race([browser.close(),new Promise(r=>setTimeout(r,2000))]);process.exit(0);
})().catch(e=>{console.log('SE425_FATAL',e.stack);process.exit(1)});
