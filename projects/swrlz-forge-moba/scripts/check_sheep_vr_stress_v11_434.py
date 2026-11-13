#!/usr/bin/env python3
"""Disposable native Sheep Tag stress profile with real IWER head poses.

The served HTML receives test-only timers and a bounded native-simulation setup
hook. Setup acceleration is excluded from measurements. No cloud/account writes.
CPU/callback measurements on software Chromium are not Quest GPU/FPS promises.
"""
import argparse,asyncio,hashlib,json,math,tempfile,time
from pathlib import Path
from urllib.parse import urlsplit
from playwright.async_api import async_playwright
P=argparse.ArgumentParser(description=__doc__)
P.add_argument('--html',required=True);P.add_argument('--output');P.add_argument('--seconds',type=float,default=4)
P.add_argument('--iwer',default='/workspace/scratch/vr340-tools/node_modules/iwer/build/iwer.min.js')
P.add_argument('--setup-seconds',type=float,default=105)
A=P.parse_args();ROOT=Path(__file__).resolve().parents[1];HTML=Path(A.html).resolve();OUT=Path(A.output or tempfile.mkdtemp(prefix='sheep-stress434-'));OUT.mkdir(parents=True,exist_ok=True)
FORGE='https://kamiloki-swrlz-forge-moba.static.hf.space';THREE_URL='https://cdn.jsdelivr.net/npm/three@0.169.0/+esm'
original=HTML.read_bytes();SHA=hashlib.sha256(original).hexdigest()
functions=['stUpdate','stUpdateVision','stPath','stCanBuild','stBlocked','stRefreshHUD','stStatus','stUiStatus','stUpdateCamera','se193XRFrame','se181XRRender','se192VRFrame','se191XRRenderFrame','updateWispVisuals','updateDragonRigs','updateDragonSurfaceContacts','updateWorkspaceInteraction','animeUpdateCinematic','stRunAfterTick','st140MenuTick','se223Frame','se225MaterialFrame']
INSTRUMENT="""
const __s434={collect:false,stats:{},frames:[],calls:[],triangles:[],windowAt:0};
function __s434Timed(name,fn,context,args){const at=performance.now();try{return fn.apply(context,args)}finally{if(__s434.collect){const ms=performance.now()-at,s=__s434.stats[name]||(__s434.stats[name]={calls:0,ms:0,max:0});s.calls++;s.ms+=ms;s.max=Math.max(s.max,ms);}}}
"""
for f in functions:INSTRUMENT+=f"const __s434_{f}={f};{f}=function(...args){{return __s434Timed('{f}',__s434_{f},this,args)}};\n"
INSTRUMENT+="""
const __s434Render=renderer.render;
renderer.render=function(...args){const at=performance.now();try{return __s434Timed('renderer.render',__s434Render,this,args)}finally{if(__s434.collect){__s434.frames.push(at);__s434.calls.push(renderer.info.render.calls);__s434.triangles.push(renderer.info.render.triangles);}}};
window.__SHEEP_STRESS_434={
 reset(){__s434.stats={};__s434.frames=[];__s434.calls=[];__s434.triangles=[];__s434.windowAt=performance.now();__s434.collect=true;},
 read(){__s434.collect=false;let meshes=0,visibleMeshes=0,vertices=0;scene.traverse(o=>{if(o.isMesh){meshes++;let visible=true;for(let n=o;n;n=n.parent)if(!n.visible)visible=false;if(visible){visibleMeshes++;vertices+=o.geometry?.attributes?.position?.count||0;}}});return {stats:__s434.stats,frames:__s434.frames,calls:__s434.calls,triangles:__s434.triangles,wallMs:performance.now()-__s434.windowAt,graph:{meshes,visibleMeshes,vertices},game:stSession?{elapsed:stSession.elapsed,houses:stSession.buildings.filter(b=>b.hp>0).length,sheep:stSession.units.filter(u=>u.kind==='sheep'&&!u.captured).length,bots:stSession.units.filter(u=>u.kind==='sheep'&&u.id!==stSession.controlledId&&!u.captured).length,winner:stSession.winner,owners:[...new Set(stSession.buildings.filter(b=>b.hp>0).map(b=>b.owner))]}:null,follow:se193.follow,renderer:renderer.info.memory,shadows:{enabled:renderer.shadowMap.enabled,type:renderer.shadowMap.type},batch:window.SWYRL_ENGINE_SHEEP_VISUAL_BATCH_434?.diagnose(),recovery:window.SWYRL_ENGINE_SHEEP_VISIBLE_RECOVERY_434?.diagnose(),shadowCache:window.SWYRL_ENGINE_EDITOR_SHADOW_CACHE_434?.diagnose(),xray:window.SWYRL_ENGINE_SHEEP_XRAY_434?.diagnose(),headturn:window.SWYRL_ENGINE_QUEST_HEADTURN_239?.diagnose(),focus:window.SWYRL_ENGINE_QUEST_OS_STABILITY_211?.diagnose(),clip:{near:camera.near,far:camera.far,eyes:renderer.xr.isPresenting?renderer.xr.getCamera(camera).cameras.map(c=>({matrix:c.projectionMatrix.toArray(),world:c.matrixWorld.toArray()})):[]},contextLost:renderer.getContext().isContextLost(),pursuit:window.SWYRL_ENGINE_SHEEP_PURSUIT_306?.diagnose(),planning:window.SWYRL_ENGINE_SHEEP_AI_FRAME_BUDGET_411?.diagnose()};},
 advance(steps){for(let i=0;i<Math.min(20,steps)&&stSession&&!stSession.winner;i++)stUpdate(.05,performance.now()/1000);return stSession?{elapsed:stSession.elapsed,houses:stSession.buildings.filter(b=>b.hp>0).length,sheep:stSession.units.filter(u=>u.kind==='sheep'&&!u.captured).length}:null;},
 follow(value){se193.follow=!!value;},
 buildings(){return stSession?.buildings.filter(b=>b.hp>0).map(b=>({kind:b.kind,pos:b.pos.toArray(),rotation:b.rotation||0}))||[];}
};
"""
anchor=b'installPerformanceSettings();se189InstallPerfUI();';assert original.count(anchor)==1
DATA=original.replace(anchor,INSTRUMENT.encode()+b'\n'+anchor,1)
IWER=Path(A.iwer).read_bytes();assert hashlib.sha256(IWER).hexdigest()=='79fb12295642d3cbab36b28a2a4ba8b4a48a5053ce70057da2f249b67daa9780'
fixture=json.loads((ROOT/'scenes/sheep-tag-wildwood-v11-79.swyrl.json').read_text())
fixture['project']['name']='Disposable max-flock performance practice';fixture['project']['canonicalId']='stress434-private-fixture';fixture['project']['sheepTag']['headstart']=120;fixture['project']['sheepTag']['duration']=1200;fixture['project']['sheepTag']['startGold']=500;fixture['project']['sheepTag']['events']=False
fixture['editor']['studioWorkspace']='game';FILE=OUT/'practice.swyrl.json';FILE.write_text(json.dumps(fixture))
async def route(r):
 u=urlsplit(r.request.url)
 if u.scheme+'://'+u.netloc==FORGE:
  if u.path in ('/','/index.html','/modeler.html'):return await r.fulfill(body=DATA,content_type='text/html')
  p=(HTML.parent/u.path.lstrip('/')).resolve()
  if p.is_relative_to(HTML.parent) and p.is_file():return await r.fulfill(path=str(p))
  return await r.fulfill(status=404,body='Missing fixture asset')
 if r.request.url==THREE_URL:return await r.fulfill(path='/workspace/scratch/vr340-tools/node_modules/three/build/three.module.js',content_type='text/javascript')
 if u.netloc.endswith('hf.space'):return await r.fulfill(status=503,body='Offline performance fixture')
 return await r.continue_()
def describe(d):
 ts=d['frames'];gaps=sorted(b-a for a,b in zip(ts,ts[1:]));n=max(1,len(ts));mean=lambda a:sum(a)/max(1,len(a))
 return {**{k:v for k,v in d.items() if k not in ('frames','calls','triangles')},'renderedFrames':len(ts),'callbackMeanMs':mean(gaps),'callbackP95Ms':gaps[min(len(gaps)-1,int(len(gaps)*.95))] if gaps else 0,'drawCallsMean':mean(d['calls']),'trianglesMean':mean(d['triangles']),'renderCpuPerFrame':d['stats'].get('renderer.render',{}).get('ms',0)/n,'hotFunctions':sorted([{'name':k,'calls':v['calls'],'meanMs':v['ms']/max(1,v['calls']),'maxMs':v['max'],'totalMs':v['ms']} for k,v in d['stats'].items()],key=lambda v:v['totalMs'],reverse=True)}
async def profile(page,label,moving=False,editor=False):
 print('PROFILE',label,flush=True);await page.evaluate('()=>window.__SHEEP_STRESS_434.reset()');start=time.monotonic()
 while time.monotonic()-start<A.seconds:
  if moving:
   phase=(time.monotonic()-start)*2
   if editor:await page.mouse.move(500+140*math.sin(phase),350+60*math.cos(phase),steps=2)
   else:await page.evaluate('([yaw,x])=>{xrTestDevice.quaternion.set(0,Math.sin(yaw/2),0,Math.cos(yaw/2));xrTestDevice.position.set(x,1.65,0)}',[.48*math.sin(phase),.12*math.sin(phase*.7)])
  await page.wait_for_timeout(45)
 d=describe(await page.evaluate('()=>window.__SHEEP_STRESS_434.read()'));(OUT/(label+'.json')).write_text(json.dumps(d,indent=2));await page.screenshot(path=str(OUT/(label+'.png')));print('RESULT',label,json.dumps({k:d[k] for k in ['renderedFrames','callbackMeanMs','drawCallsMean','trianglesMean','renderCpuPerFrame','game','graph']}),flush=True);return d
async def main():
 errors=[];results={};webgl_messages=[];result={'sourceSha256':SHA,'instrumentedSha256':hashlib.sha256(DATA).hexdigest(),'profile':'software Chromium + native engine + IWER Quest stereo','physicalQuestMeasured':False,'pageErrors':errors,'webglMessages':webgl_messages,'phases':results}
 async with async_playwright() as p:
  browser=await p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage','--enable-webgl','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader'])
  context=await browser.new_context(viewport={'width':960,'height':720})
  await context.add_init_script(script=IWER.decode()+"\nif(location.origin==="+json.dumps(FORGE)+"){window.xrTestDevice=new IWER.XRDevice(IWER.metaQuest2,{stereoEnabled:true});xrTestDevice.installRuntime({forceInstall:true});xrTestDevice.position.set(0,1.65,0);xrTestDevice.controllers.left.position.set(-.3,1.22,-.4);xrTestDevice.controllers.right.position.set(.3,1.22,-.4);}")
  await context.route('**/*',route);page=await context.new_page();page.set_default_timeout(45000);page.on('pageerror',lambda e:errors.append(str(e)));page.on('dialog',lambda d:asyncio.create_task(d.accept()));page.on('console',lambda message:webgl_messages.append(message.text[:300]) if message.text[:300] not in webgl_messages and len(webgl_messages)<20 and message.type in ('warning','error') and any(word in message.text.lower() for word in ('webgl','framebuffer','gl_invalid','context lost')) else None)
  try:
   print('LOAD',SHA,flush=True);await page.goto(FORGE+'/',wait_until='domcontentloaded',timeout=90000);await page.wait_for_function('()=>!!window.__SHEEP_STRESS_434&&!!window.SWYRL_ENGINE_SHEEP_TAG',timeout=90000)
   notes=page.locator('#seReleaseNotesDialog[open]')
   if await notes.count():await notes.locator('button').last.click()
   await page.locator('#fileInput').set_input_files(str(FILE));await page.wait_for_function('()=>window.SWYRL_ENGINE_AGENT.inspectScene().project.kind==="sheep-tag"')
   await page.evaluate('()=>window.SWYRL_ENGINE_SHEEP_TAG.frame()');await page.wait_for_timeout(600)
   results['editor-empty']=await profile(page,'editor-empty')
   await page.evaluate('()=>window.SWYRL_ENGINE_SHEEP_TEAM_SETUP_416.setCount(7)');await page.locator('#playBtn').click();await page.wait_for_function('()=>window.SWYRL_ENGINE_SHEEP_TAG.status().active');print('PLAY',json.dumps(await page.evaluate('()=>window.SWYRL_ENGINE_SHEEP_TAG.status().counts')),flush=True)
   results['game-empty']=await profile(page,'game-empty')
   await page.evaluate('async()=>await window.SWYRL_ENGINE_XR.enter()');await page.wait_for_function('()=>window.SWYRL_ENGINE_SHEEP_VR.diagnose().active',timeout=45000);await page.wait_for_timeout(1800)
   results['vr-empty']=await profile(page,'vr-empty')
   print('GROW_NATIVE_AI',flush=True)
   target=A.setup_seconds
   for i in range(int(target*20/20)+20):
    setup=await page.evaluate('()=>window.__SHEEP_STRESS_434.advance(20)')
    if i%10==0:print('GROW',setup,flush=True)
    if setup['elapsed']>=target or setup['sheep']<8:break
    await page.wait_for_timeout(1)
   assert setup['sheep']==8,setup
   assert setup['houses']>=16,setup
   result['setup']=setup;await page.wait_for_timeout(600)
   results['vr-built-still']=await profile(page,'vr-built-still')
   results['vr-built-headturn']=await profile(page,'vr-built-headturn',True)
   await page.evaluate('()=>window.__SHEEP_STRESS_434.follow(false)');await page.wait_for_timeout(250)
   results['vr-built-free-headturn']=await profile(page,'vr-built-free-headturn',True)
   print('META_STYLE_VISIBILITY_INTERRUPTION',flush=True)
   before_menu=await page.evaluate('()=>window.SWYRL_ENGINE_SHEEP_TAG.status()')
   await page.evaluate('()=>xrTestDevice.updateVisibilityState("visible-blurred")')
   await page.wait_for_function('()=>xrTestDevice.visibilityState==="visible-blurred"',timeout=15000)
   await page.wait_for_timeout(1300)
   await page.evaluate('()=>xrTestDevice.updateVisibilityState("visible")')
   await page.wait_for_function('()=>xrTestDevice.visibilityState==="visible"',timeout=15000)
   await page.wait_for_timeout(1500)
   results['vr-built-after-menu-headturn']=await profile(page,'vr-built-after-menu-headturn',True)
   after_menu=await page.evaluate('()=>window.SWYRL_ENGINE_SHEEP_TAG.status()')
   assert len(after_menu['units'])==len(before_menu['units'])
   assert not results['vr-built-after-menu-headturn']['contextLost']
   for eye in results['vr-built-after-menu-headturn']['clip']['eyes']:
    assert all(math.isfinite(v) for v in eye['matrix']+eye['world'])
   buildings=await page.evaluate('()=>window.__SHEEP_STRESS_434.buildings()')
   await page.evaluate('async()=>await window.SWYRL_ENGINE_XR.exit()')
   await page.wait_for_function('()=>!window.SWYRL_ENGINE_SHEEP_VR.diagnose().active',timeout=15000)
   await page.locator('#stStop').click()
   editor=json.loads(FILE.read_text());template=next(a for a in editor['scene']['actors'] if a['type']=='st-sheep')
   for i,b in enumerate(buildings):
    a={**template,'id':'stress-house-'+str(i),'name':'Native stress house '+str(i),'type':b['kind'],'role':'','team':'neutral','position':b['pos'],'rotation':[0,b['rotation'],0],'scale':[1,1,1],'blueprintClass':'SheepTag/farm','folder':'Sheep Tag/Stress houses'};editor['scene']['actors'].append(a)
   efile=OUT/'editor-houses.swyrl.json';efile.write_text(json.dumps(editor));await page.locator('#fileInput').set_input_files(str(efile));await page.wait_for_timeout(800);await page.evaluate('()=>window.SWYRL_ENGINE_SHEEP_TAG.frame()')
   results['editor-built']=await profile(page,'editor-built')
   viewport=page.locator('#viewport');box=await viewport.bounding_box();await page.mouse.move(box['x']+box['width']*.5,box['y']+box['height']*.5);await page.mouse.down(button='right')
   results['editor-built-pan']=await profile(page,'editor-built-pan',True,True);await page.mouse.up(button='right')
   result['status']='PASS';assert not errors,errors
  except Exception as error:
   result['status']='FAIL';result['error']=str(error);await page.screenshot(path=str(OUT/'failure.png'));raise
  finally:
   (OUT/'verification.json').write_text(json.dumps(result,indent=2));await browser.close()
 print('STRESS_PROFILE_PASS',str(OUT),flush=True)
if __name__=='__main__':asyncio.run(main())
