#!/usr/bin/env python3
"""Browser geometry and load-routing checks; fresh isolated profile, no account login.
Requires Playwright Python and Chromium. Local sealed HTML is fulfilled at the
canonical app origin; CDN/guest Chat use verified TLS. No credentials are reused.
"""
import argparse,asyncio,json,tempfile
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import urlsplit
from types import SimpleNamespace
from playwright.async_api import async_playwright
ROOT=Path(__file__).resolve().parents[1]
cli=argparse.ArgumentParser();cli.add_argument('--html',required=True);cli.add_argument('--output');cli.add_argument('--native-project');args=cli.parse_args()
out=Path(args.output or tempfile.mkdtemp(prefix='swrlz-ui320-')).resolve();out.mkdir(parents=True,exist_ok=True)
html=Path(args.html).resolve();assert html.is_file()
FORGE='https://kamiloki-swrlz-forge-moba.static.hf.space';CHAT='https://kamiloki-swyrlz.hf.space';CDN='https://cdn.jsdelivr.net'
def http(url,method,headers,body):
 from urllib.error import HTTPError
 try:r=urlopen(Request(url,data=body,headers=headers,method=method),timeout=25)
 except HTTPError as e:r=e
 with r:
  data=r.readline(262144) if urlsplit(url).path=='/api/lalm_station/stream' else r.read()
  wanted={'content-type','content-security-policy','access-control-allow-origin','access-control-allow-credentials','cache-control'}
  return r.status,{k:v for k,v in r.headers.items() if k.lower() in wanted},data
async def transport(route):
 req=route.request;u=urlsplit(req.url);origin=u.scheme+'://'+u.netloc
 if origin==FORGE:
  if u.path in ('/','/index.html','/modeler.html'):return await route.fulfill(path=str(html),content_type='text/html')
  asset=(html.parent/u.path.lstrip('/')).resolve()
  if asset.is_relative_to(html.parent) and asset.is_file():return await route.fulfill(path=str(asset))
  return await route.fulfill(status=404,body='Missing packaged test asset')
 if origin not in (CHAT,CDN):return await route.abort('blockedbyclient')
 allowed={'accept','content-type','origin','referer'}
 headers={k:v for k,v in (await req.all_headers()).items() if k.lower() in allowed}
 try:status,headers,data=await asyncio.to_thread(http,req.url,req.method,headers,req.post_data_buffer)
 except Exception:return await route.abort('failed')
 return await route.fulfill(status=status,headers=headers,body=data)
relay=SimpleNamespace(FORGE=FORGE,CHAT=CHAT,CDN=CDN,transport=transport)
if args.native_project:native_file=Path(args.native_project).resolve()
else:
 public=json.loads((ROOT/'scenes/model-atelier-prism-jester.swyrl.json').read_text())
 fixture={'project':{'name':'Studio UI check model','kind':'model-atelier','canonicalId':'studio-ui-check-model','template':'custom','environment':'spatial-workspace','modelAtelier':{'schema':'swyrl-model-atelier-v1','name':'Studio UI check model','parts':public['project']['modelAtelier']['parts'][:1]}},'editor':{},'scene':{'background':'#111827','paths':{},'actors':[]}}
 native_file=out/'ui-model.swyrl.json';native_file.write_text(json.dumps(fixture))
expected_count=len(json.loads(native_file.read_text())['project']['modelAtelier']['parts']);assert expected_count>0
async def rect(page,selector):
 return await page.locator(selector).bounding_box()
def overlap(a,b):
 if not a or not b:return 0
 return max(0,min(a['x']+a['width'],b['x']+b['width'])-max(a['x'],b['x']))*max(0,min(a['y']+a['height'],b['y']+b['height'])-max(a['y'],b['y']))
async def main():
 async with async_playwright() as p:
  browser=await p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage','--enable-webgl','--enable-unsafe-swiftshader'])
  context=await browser.new_context(viewport={'width':1440,'height':1000},accept_downloads=True)
  for origin in (relay.FORGE,relay.CHAT,relay.CDN):await context.route(origin+'/**',relay.transport)
  page=await context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.on('dialog',lambda d:asyncio.create_task(d.accept()))
  try:
   await page.goto(relay.FORGE+'/modeler.html',wait_until='domcontentloaded',timeout=90000)
   await page.wait_for_function('()=>!!window.SWYRL_ENGINE_AGENT&&!!document.querySelector("#modelAtelierPanel[data-se320-ui]")',timeout=60000)
   if await page.locator('#seReleaseNotesDialog[open]').count():await page.locator('#seReleaseNotesDialog[open] button').last.evaluate('(x)=>x.click()')
   await page.locator('#fileInput').set_input_files(str(native_file))
   await page.wait_for_function('n=>window.SWYRL_ENGINE_STUDIOS.active()==="modeler"&&document.querySelector("#modelAtelierParts").children.length===n',arg=expected_count)
   await page.wait_for_timeout(600)
   rail=await rect(page,'#modelAtelierToolRail');inspector=await rect(page,'.atelier-inspector');scene=await rect(page,'.atelier-scene')
   print('MODEL_LAYOUT',json.dumps({'rail':rail,'inspector':inspector,'scene':scene,'overlap':overlap(rail,inspector)}),flush=True)
   assert not overlap(rail,inspector) and rail['x']+rail['width']<=inspector['x']+1
   await page.screenshot(path=str(out/'model-desktop.png'))
   tree=page.locator('#se251ModelLibrary .se320-tree-toggle')
   await tree.evaluate('(x)=>x.click()');await page.wait_for_timeout(100);assert await tree.is_visible();assert await tree.get_attribute('aria-expanded')=='false'
   await tree.evaluate('(x)=>x.click()');await page.wait_for_timeout(100);assert await tree.get_attribute('aria-expanded')=='true'
   await page.locator('#modelAtelierPanel .se251-external-collapse').evaluate('(x)=>x.click()');await page.wait_for_timeout(300)
   assert not await page.locator('.atelier-inspector').is_visible()
   rail=await rect(page,'#modelAtelierToolRail');body=await rect(page,'.atelier-body');assert abs(rail['x']+rail['width']-body['x']-body['width'])<=2
   await page.screenshot(path=str(out/'model-inspector-collapsed.png'))
   await page.locator('#modelAtelierToolRail [data-atelier-tool-category="Sculpt"]').evaluate('(x)=>x.click()');await page.wait_for_timeout(300)
   assert await page.locator('.atelier-inspector').is_visible()
   assert await page.locator('#seAtelierModes').evaluate('(x)=>!!x.closest(".atelier-inspector")')
   await page.locator('.atelier-tool-handle [aria-label="Hide editing tools"]').evaluate('(x)=>x.click()');await page.wait_for_timeout(100)
   assert not await page.locator('.atelier-inspector').is_visible()
   await page.locator('#modelAtelierPanel .se251-external-collapse').evaluate('(x)=>x.click()');await page.wait_for_timeout(100)
   assert await page.locator('.atelier-inspector').is_visible()
   await page.locator('#se320ModelProjects').evaluate('(x)=>x.click()');await page.wait_for_timeout(300)
   mainTabs=await rect(page,'#projectHub .se170-hub-tabs');subTabs=await rect(page,'#se236StarterGroups')
   assert overlap(mainTabs,subTabs)==0
   await page.screenshot(path=str(out/'projects-desktop.png'))
   await page.locator('#se170-pane-starter').evaluate('(x)=>x.scrollTop=900');await page.wait_for_timeout(100)
   assert overlap(await rect(page,'#projectHub .se170-hub-tabs'),await rect(page,'#se236StarterGroups'))==0
   await page.get_by_role('tab',name='My Projects',exact=True).evaluate('(x)=>x.click()');await page.wait_for_timeout(200)
   assert await page.locator('#se170-pane-mine').is_visible()
   await page.screenshot(path=str(out/'my-projects-desktop.png'))
   await page.locator('#projectHub .project-head button').evaluate('(x)=>x.click()')
   # Test the direct Modeler route's first switch with a loaded game: retain data.
   game=await context.new_page();game.on('pageerror',lambda e:errors.append(str(e)));game.on('dialog',lambda d:asyncio.create_task(d.accept()))
   await game.goto(relay.FORGE+'/index.html',wait_until='domcontentloaded',timeout=90000)
   await game.wait_for_function('()=>window.SWYRL_ENGINE_AGENT?.inspectScene()?.scene?.actors?.length>0',timeout=60000)
   if await game.locator('#seReleaseNotesDialog[open]').count():await game.locator('#seReleaseNotesDialog[open] button').last.evaluate('(x)=>x.click()')
   native=await game.evaluate('()=>window.SWYRL_ENGINE_AGENT.inspectScene()');native['project'].update(name='Routing check game',kind='default',template='custom',canonicalId='routing-check-game',levelPack=None,levelSystem=None,levelProjectRoot=None);native['scene']['actors']=native['scene']['actors'][:3];native['scene']['paths']={};native['editor']['studioWorkspace']='game'
   path=out/'routing-game.json';path.write_text(json.dumps(native))
   await game.screenshot(path=str(out/'game-desktop.png'));await game.close()
   await page.locator('#fileInput').set_input_files(str(path));await page.wait_for_function('()=>window.SWYRL_ENGINE_STUDIOS.active()==="game"');await page.wait_for_timeout(300)
   result=await page.evaluate('()=>{const d=window.SWYRL_ENGINE_AGENT.inspectScene();return {name:d.project.name,actors:d.scene.actors.length}}')
   assert result=={'name':'Routing check game','actors':len(native['scene']['actors'])},result
   print('GAME_LOAD_PRESERVED',result,flush=True)
   await page.locator('#se320GameMore>summary').evaluate('(x)=>x.click()');assert await page.locator('#se320GameMore .se320-game-extras').is_visible()
   await page.screenshot(path=str(out/'game-more-tools.png'));await page.locator('#se320GameMore>summary').evaluate('(x)=>x.click()')
   native['project']['name']='Routing check particles';native['editor']['studioWorkspace']='particles';native['project']['particleStudio']={'schema':'swyrl-particle-studio-v1','emitters':[]}
   path=out/'routing-particles.json';path.write_text(json.dumps(native))
   await page.locator('#fileInput').set_input_files(str(path));await page.wait_for_function('()=>window.SWYRL_ENGINE_STUDIOS.active()==="particles"');await page.wait_for_timeout(500)
   assert await page.evaluate('()=>window.SWYRL_ENGINE_AGENT.inspectScene().project.name')=='Routing check particles'
   await page.screenshot(path=str(out/'particles-desktop.png'))
   print('PARTICLE_LOAD_PRESERVED',flush=True)
   # Test compact layouts, project tabs, and inspector reachability on a phone.
   await page.set_viewport_size({'width':390,'height':844});await page.wait_for_timeout(500)
   await page.screenshot(path=str(out/'particles-phone.png'))
   tools=page.locator('#se249Root .se249-menus details').filter(has=page.locator('summary:text-is("Tools")'))
   await tools.locator('summary').evaluate('(x)=>x.click()');await page.wait_for_timeout(100)
   box=tools.locator('.se249-menu-pop');bounds=await box.bounding_box()
   assert bounds and bounds['x']>=0 and bounds['x']+bounds['width']<=390
   assert await box.evaluate('(x)=>{const r=x.getBoundingClientRect();return x.contains(document.elementFromPoint(r.left+20,r.top+20))}'),'Particle menu must be visible and receive input, not merely have a bounding box'
   await page.screenshot(path=str(out/'particles-phone-menu.png'));await tools.locator('summary').evaluate('(x)=>x.click()')
   await page.locator('#projectBtn').evaluate('(x)=>x.click()');await page.get_by_role('tab',name='Starter Projects',exact=True).evaluate('(x)=>x.click()');await page.wait_for_timeout(200)
   assert overlap(await rect(page,'#projectHub .se170-hub-tabs'),await rect(page,'#se236StarterGroups'))==0
   await page.screenshot(path=str(out/'projects-phone.png'));await page.locator('#projectHub .project-head button').evaluate('(x)=>x.click()')
   await page.locator('#fileInput').set_input_files(str(native_file));await page.wait_for_function('()=>window.SWYRL_ENGINE_STUDIOS.active()==="modeler"');await page.wait_for_timeout(500)
   assert await page.locator('#modelAtelierToolRail').is_visible()
   assert await page.locator('[data-component-controls]').evaluate('(x)=>!!x.closest(".atelier-inspector")')
   print('PHONE_MODEL_BOUNDS',json.dumps({'rail':await rect(page,'#modelAtelierToolRail'),'inspector':await rect(page,'.atelier-inspector')}),flush=True)
   await page.screenshot(path=str(out/'model-phone-debug.png'))
   assert overlap(await rect(page,'#modelAtelierToolRail'),await rect(page,'.atelier-inspector'))==0
   await page.screenshot(path=str(out/'model-phone.png'))
   counts=await page.evaluate('()=>({parts:window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier.parts.length,rows:document.querySelector("#modelAtelierParts").children.length})');assert counts=={'parts':expected_count,'rows':expected_count}
   # Repeated native switches must not install a second Game tab rail.
   for n in range(2):
    await page.locator('#modelAtelierPanel [data-se187-tab=game]').evaluate('(x)=>x.click()');await page.wait_for_timeout(100)
    assert await page.locator('.app .se187-game-tabs').count()==1
    assert await page.locator('.app>.topbar>.se187-game-tabs').count()==0
    await page.locator('#se320GameHeader [data-se187-tab=modeler]').evaluate('(x)=>x.click()');await page.wait_for_timeout(100)
   print('FINAL_UI_BROWSER_PASS',json.dumps({'mage':counts,'pageErrors':errors}),flush=True)
   if errors:raise RuntimeError('PAGE_ERRORS_'+json.dumps(errors))
  finally:await browser.close()
asyncio.run(main())
