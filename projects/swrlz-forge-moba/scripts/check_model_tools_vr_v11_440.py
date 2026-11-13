#!/usr/bin/env python3
"""Actual controller/menu audit. Fresh disposable guests only; no physical Quest claims."""
from pathlib import Path
import types,os,asyncio,json,hashlib,traceback
HELPER=Path(__file__).with_name('check_model_vr_v11_390.py')
VERSION=os.environ.get('MODEL_TEST_VERSION','v11.440')
s=HELPER.read_text().rsplit('\nasyncio.run(main())',1)[0].replace('version===\"v11.390\"','version===\"'+VERSION+'\"')
H=types.ModuleType('vr_helpers');H.__file__=str(HELPER);exec(compile(s,str(HELPER),'exec'),H.__dict__)
expected=os.environ.get('MODEL_TEST_SHA');assert expected and hashlib.sha256(H.html.read_bytes()).hexdigest()==expected,'Set MODEL_TEST_SHA to the sealed source digest'
H.distance=lambda a,b:sum((x-y)**2 for x,y in zip(a,b))**.5
# Observation-only fields expose the native offset-space pose and which hand
# owns a hover. They never dispatch a tool, change geometry or advance time.
OBSERVED_HTML=H.html.read_text()
a="controllers:se340XR.controllers.map(r=>({index:r.index,handedness:r.input?.handedness||'none',"
b=a+"hitAction:r.hit?.action||null,blockTrigger:!!r.blockTrigger,blockGrip:!!r.blockGrip,triggerValue:r.input?.gamepad?.buttons?.[0]?.value,"
assert OBSERVED_HTML.count(a)==1;OBSERVED_HTML=OBSERVED_HTML.replace(a,b,1)
a="center:se340XR.pivot.position.toArray(),yaw:se340XR.yaw}"
b="center:se340XR.pivot.position.toArray(),yaw:se340XR.yaw,pitch:se340XR.pitch,baseYaw:se340XR.baseYaw}"
assert OBSERVED_HTML.count(a)==1;OBSERVED_HTML=OBSERVED_HTML.replace(a,b,1)
a="const result={schema:'swyrl-model-vr-v1'"
b="const result={actionTrace:window.__model438Actions||[],schema:'swyrl-model-vr-v1'"
assert OBSERVED_HTML.count(a)==1;OBSERVED_HTML=OBSERVED_HTML.replace(a,b,1)
a='installPerformanceSettings();se189InstallPerfUI();'
b="""(()=>{const prior=se340ModelXRAction;se340ModelXRAction=function(action,record){const before={view:se340XR.viewMode,page:se340XR.page},result=prior.apply(this,arguments);const log=window.__model438Actions||(window.__model438Actions=[]);log.push({action,before,after:{view:se340XR.viewMode,page:se340XR.page},result,hand:record?.input?.handedness});if(log.length>25)log.shift();return result;};})();\n"""+a
assert OBSERVED_HTML.count(a)==1;OBSERVED_HTML=OBSERVED_HTML.replace(a,b,1)
a="const result={actionTrace:window.__model438Actions||[],schema:'swyrl-model-vr-v1'"
b="const result={inputTrace:window.__model438Input||[],actionTrace:window.__model438Actions||[],schema:'swyrl-model-vr-v1'"
assert OBSERVED_HTML.count(a)==1;OBSERVED_HTML=OBSERVED_HTML.replace(a,b,1)
a='installPerformanceSettings();se189InstallPerfUI();'
b="""(()=>{const prior=se350Dispatch;se350Dispatch=function(sample){if(sample.events?.length){const log=window.__model438Input||(window.__model438Input=[]);log.push({events:sample.events.map(e=>({action:e.action,phase:e.phase,hand:e.hand})),blocks:se340XR.controllers.map(r=>({hand:r.input?.handedness,blocked:r.blockTrigger,tracked:r.targetTracked}))});if(log.length>15)log.shift();}return prior.apply(this,arguments);};})();\n"""+a
assert OBSERVED_HTML.count(a)==1;OBSERVED_HTML=OBSERVED_HTML.replace(a,b,1)
a='const start=performance.now(),hit=se340Hit(record,false);record.hit=hit;record.se372TriggerHit=hit;'
b=a+"record.observedTriggerHit={action:hit?.action,id:hit?.id,ui:hit?.ui,gizmo:hit?.gizmo,quest:hit?.quest,disabled:hit?.target?.userData?.se340Disabled};"
assert OBSERVED_HTML.count(a)==1;OBSERVED_HTML=OBSERVED_HTML.replace(a,b,1)
a="hitAction:r.hit?.action||null,blockTrigger:"
b="triggerHit:r.observedTriggerHit,hitAction:r.hit?.action||null,blockTrigger:"
assert OBSERVED_HTML.count(a)==1;OBSERVED_HTML=OBSERVED_HTML.replace(a,b,1)
original_transport=H.transport
async def observed_transport(route):
 u=H.urlsplit(route.request.url)
 if u.scheme+'://'+u.netloc==H.FORGE and u.path in ('/','/index.html','/modeler.html'):
  return await route.fulfill(body=OBSERVED_HTML,content_type='text/html')
 return await original_transport(route)
H.transport=observed_transport
RESULT={'version':VERSION,'testedHtmlSha256':hashlib.sha256(H.html.read_bytes()).hexdigest(),'instrumentedSha256':hashlib.sha256(OBSERVED_HTML.encode()).hexdigest(),'instrumentation':'read-only inspector pose/hover fields; actual native tool input only','physicalHeadsetAcceptance':False,'runtime':'Chromium / official IWER 2.8 Quest 2 / native spatial ray and physical button events','status':'RUNNING','checks':[],'pageErrors':[],'failures':[],'untested':['Physical Quest touch/comfort/tracking fidelity','Authenticated account save/sync: fresh guest deliberately unauthenticated','VR object Delete absent from native spatial menu; not represented as tested','Controller-profile remapping and full two-hand fine-clutch coverage use existing separate native tests']}
def save():
 (H.out/'verification.json').write_text(json.dumps(RESULT,indent=2)+'\n')
def record(message,**extra):
 RESULT['checks'].append({'check':message,**extra});save();print('VR438_PASS '+message,flush=True)
original_tap=H.tap
async def tap_and_resolve(page,side,key):
 await original_tap(page,side,key)
 # Live profiles reserve a short window for X+Trigger/X+Y chords. Allow
 # that real input dispatcher to resolve the released tap before asserting.
 await page.wait_for_timeout(250);await H.frames(page,2)
H.tap=tap_and_resolve
async def menu_layout_ready(page):
 await page.wait_for_function('()=>{const s=window.SWYRL_ENGINE_MODEL_VR.inspect(),m=s.menu;return !s.sessionAttached||!s.paletteVisible||!!m&&m.motion?.reveal>.999&&m.motion?.transition>.999}',timeout=20000)
 await H.frames(page,2)
H.settle_menu=menu_layout_ready
original_aim=H.aim
async def aim_in_reference(page,target,side='right',origin=None):
 # IWER device poses are in its base tracking space. Native camera presets
 # orbit an offset reference space, so convert intended native-world hand/ray
 # poses back into base space before sending actual controller input.
 state=await H.read(page,True);view=state.get('viewMode','orbit');presentation=state.get('presentation',{})
 pitch=presentation.get('pitch',0)
 yaw=presentation.get('yaw',0)-presentation.get('baseYaw',0);center=presentation.get('position',[0,0,0]);origin=origin or ([.22,1.3,-.35] if side=='right' else [-.22,1.3,-.35])
 transformed=await page.evaluate('''([center,yaw,pitch,origin,target])=>{const T=window.__VR_THREE,q=new T.Quaternion().setFromEuler(new T.Euler(pitch,yaw,0,'YXZ')),c=new T.Vector3(...center),t=c.clone().sub(c.clone().applyQuaternion(q));return [origin,target].map(p=>new T.Vector3(...p).applyQuaternion(q).add(t).toArray());}''',[center,yaw,pitch,origin,target])
 return await original_aim(page,transformed[1],side=side,origin=transformed[0])
H.aim=aim_in_reference
async def press_card(page,action,side='right'):
 detail=await H.read(page,True);target=next((x for x in detail['paletteActions'] if x['action']==action),None)
 assert target,'Missing visible card '+action
 point=target['center'];origins=[None,[point[0],point[1],point[2]+.25],[point[0]-.25,point[1],point[2]],[point[0]+.25,point[1],point[2]]]
 for origin in origins:
  await H.aim(page,point,side=side,origin=origin)
  if any(c.get('handedness')==side and c.get('hitAction')==action for c in (await H.read(page))['controllers']):break
 else:raise AssertionError('Controller did not hover '+action+' before pressing; '+str((await H.read(page)).get('menu',{}).get('hovered')))
 await H.tap(page,side,'trigger');await H.settle_menu(page)
H.action_ray=press_card
async def find_action(page, action):
 # Navigate through the current real page cards. The older v390 helper
 # assumes Inspect is always in the A wheel; Sculpt correctly uses a brush
 # wheel instead. Use the visible Mesh -> Inspect card in every context.
 for nav in [None,'tools','studio','mesh','create-menu','draw','views','cameras','aim','projects','objects','selector','sculpt']:
  available={x['action'] for x in (await H.read(page,True))['paletteActions']}
  if action in available:return await H.action_ray(page,action)
  if nav and nav in available:await H.action_ray(page,nav)
 raise AssertionError('No visible route to '+action)
H.ray_find=find_action
async def select_first(page):
 await H.ray_find(page,'inspect');await H.aim_part(page,H.expected_parts[0]['id']);await H.tap(page,'right','trigger');assert (await H.read(page))['selectionIds']==[H.expected_parts[0]['id']]
async def create_flow(page):
 original=await H.parts(page);await select_first(page)
 for kind in ('box','sphere','cylinder','cone'):
  await H.ray_find(page,'create-menu');before=await H.parts(page);depth=(await H.read(page))['undoDepth'];await H.action_ray(page,'create-'+kind)
  assert (await H.read(page))['creation']['active'] and await H.parts(page)==before
  await H.aim(page,[1.05,1.40,-1.10]);await H.tap(page,'right','trigger');after=await H.parts(page)
  created=[x for x in after if x['id'] not in {p['id'] for p in before}]
  assert len(created)==1 and created[0]['kind']==kind and (await H.read(page))['undoDepth']==depth+1
  assert (await H.read(page))['selectionIds']==[created[0]['id']]
  await H.tap(page,'left','y-button');assert await H.parts(page)==before
  record('Create '+kind+': visible native ghost stays uncommitted, mapped Trigger places once, selects new shape, Undo restores original')
 await select_first(page);await H.ray_find(page,'duplicate');after=await H.parts(page);assert len(after)==len(original)+1
 await H.tap(page,'left','y-button');assert await H.parts(page)==original
 record('Duplicate copies selected native part through spatial button and one Undo restores exact source')
 await H.ray_find(page,'create-menu');await H.action_ray(page,'create-box');assert (await H.read(page))['creation']['active'];await H.tap(page,'right','b-button');assert not (await H.read(page))['creation']['active'] and await H.parts(page)==original
 record('B cancels primitive placement without changing saved source')
 await H.screenshot_xr(page,'create-menu.png')
async def sculpt_flow(page):
 original=await H.parts(page)
 for operation in ('push','smooth','flatten','inflate','pinch','translate'):
  await select_first(page);await H.ray_find(page,'sculpt');await H.action_ray(page,'sculpt-'+operation)
  assert (await H.read(page))['sculptTool']==operation
  # A little extra native radius includes enough vertices for all six operations.
  for _ in range(4):await H.action_ray(page,'brush-radius-plus')
  before=await H.parts(page);depth=(await H.read(page))['undoDepth'];await H.aim_part(page,H.expected_parts[0]['id']);await H.button(page,'right','trigger',True,6)
  assert (await H.read(page))['gesture']['kind']=='sculpt'
  if operation=='translate':await H.move_hand(page,[.018,.008,0])
  await H.frames(page,8);assert await H.parts(page)==before
  await H.button(page,'right','trigger',False,4);after=await H.parts(page)
  assert after!=before and after[0].get('sculptVertexEdits'),operation+' must persist actual native vertex edits'
  assert (await H.read(page))['undoDepth']==depth+1
  await H.tap(page,'left','y-button');assert await H.parts(page)==before
  record('Sculpt '+operation+': actual ray stroke previews real vertices, release persists one native edit, Undo restores exact geometry')
 await H.ray_find(page,'sculpt');before=await H.read(page)
 await H.action_ray(page,'brush-radius-minus');after=await H.read(page);assert after['brushRadius']<before['brushRadius'];await H.action_ray(page,'brush-radius-plus')
 await H.action_ray(page,'brush-strength-minus');assert (await H.read(page))['brushStrength']<before['brushStrength'];await H.action_ray(page,'brush-strength-plus');assert abs((await H.read(page))['brushStrength']-before['brushStrength'])<1e-6
 assert await H.parts(page)==original
 record('Brush radius/strength plus and minus alter live native parameters without source or Undo writes')
 await H.screenshot_xr(page,'sculpt-menu.png')
async def selection_flow(page):
 original=await H.parts(page);depth=(await H.read(page))['undoDepth'];second=H.expected_parts[1]['id']
 for mode in ('lasso-front','lasso-through'):
  await H.ray_find(page,'selector');await H.action_ray(page,'selector-'+mode);await H.action_ray(page,'selection-clear')
  state=await H.read(page,True);t=next(x for x in state['targetCenters'] if x['id']==second);c=t['center'];dx=max(.065,t['size'][0]*.65);dy=max(.08,t['size'][1]*.65)
  corners=[[c[0]-dx,c[1]-dy,c[2]],[c[0]+dx,c[1]-dy,c[2]],[c[0]+dx,c[1]+dy,c[2]],[c[0]-dx,c[1]+dy,c[2]],[c[0]-dx,c[1]-dy,c[2]]]
  await H.aim(page,corners[0],side='left');await H.button(page,'left','squeeze',True,3);assert (await H.read(page))['gesture']['kind']=='selection-lasso'
  for corner in corners[1:]:await H.aim(page,corner,side='left')
  await H.button(page,'left','squeeze',False,4);assert second in (await H.read(page))['selectionIds'],(mode,await H.read(page))
  assert await H.parts(page)==original and (await H.read(page))['undoDepth']==depth
  record('Selector '+mode+': held Left Grip traces a visible selection loop; release selects native object without source/history edits')
 await select_first(page);await H.ray_find(page,'draw');await H.action_ray(page,'lasso')
 await H.aim_part(page,H.expected_parts[0]['id']);await H.button(page,'right','trigger',True,3);assert (await H.read(page))['gesture']['kind']=='lasso'
 for delta in ([.02,0,0],[0,.02,0],[-.02,0,0],[0,-.02,0]):await H.move_hand(page,delta)
 assert await H.parts(page)==original
 await H.button(page,'right','trigger',False,4);after=await H.parts(page)
 assert after!=original and after[0].get('sculptLassos') and (await H.read(page))['undoDepth']==depth+1
 assert (await H.read(page))['surface']['selectedRegionId']
 await H.ray_find(page,'lasso-clear');assert (await H.read(page))['surface']['selectedRegionId'] is None
 await H.tap(page,'left','y-button');assert await H.parts(page)==original
 record('Surface Lasso saves real attached control pins and active mask in one Undo step; Whole surface clears mask; Undo restores original source')
 await H.screenshot_xr(page,'selection-tools.png')
async def camera_debug(page):
 await H.ray_find(page,'views');await H.action_ray(page,'cameras')
 for view in ('bottom','iso'):
  await H.action_ray(page,'view-'+view);await page.wait_for_timeout(900)
  state=await H.read(page,True);print('CAMERA_DEBUG '+json.dumps({'wanted':view,'view':state['viewMode'],'trace':state.get('actionTrace'),'input':state.get('inputTrace'),'controllers':state.get('controllers')}),flush=True)
  assert state['viewMode']==view
 record('Bottom to isometric actual controller camera transition')
async def menu_flow(page):
 original=await H.parts(page);depth=(await H.read(page))['undoDepth']
 await H.ray_find(page,'objects');await H.action_ray(page,'index-part-0');assert (await H.read(page))['selectionIds']==[H.expected_parts[0]['id']]
 await H.action_ray(page,'index-add');await H.action_ray(page,'index-part-1');assert set((await H.read(page))['selectionIds'])=={H.expected_parts[0]['id'],H.expected_parts[1]['id']}
 await H.action_ray(page,'index-part-1');assert (await H.read(page))['selectionIds']==[H.expected_parts[0]['id']]
 record('Object Index native name buttons select, Multi ON adds/removes components, selection does not edit source')
 for mode in ('textured','solid','wireframe','xray','normals'):
  await H.ray_find(page,'views');await H.action_ray(page,'display-'+mode);assert (await H.read(page))['displayMode']==mode
  record('Display '+mode+': native spatial action selects expected renderer display state without source writes')
 await H.action_ray(page,'display-textured');await H.action_ray(page,'cameras')
 for view in ('front','back','left','right','top','bottom','iso'):
  await H.action_ray(page,'view-'+view,side='left' if view=='iso' else 'right');assert (await H.read(page))['viewMode']==view
  record('Camera '+view+': native spatial action changes model presentation while retaining saved geometry')
 await H.action_ray(page,'focus');assert await H.parts(page)==original
 record('Focus selection frames the selected model without changing source')
 await H.ray_find(page,'aim');initial=await H.read(page);hand='right'
 # Calibrate the non-pointing hand first so the actual controller ray remains centered.
 await H.action_ray(page,'aim-hand')
 for action in ('aim-yaw-plus','aim-yaw-minus','aim-pitch-plus','aim-pitch-minus'):
  before=await H.read(page);await H.action_ray(page,action);after=await H.read(page);assert after['aimCalibration']!=before['aimCalibration']
 await H.action_ray(page,'aim-reset');await H.action_ray(page,'aim-reset-all');assert (await H.read(page))['aimCalibration']=={'left':{'yaw':0,'pitch':0},'right':{'yaw':0,'pitch':0}}
 record('Pointer hand selection, yaw/pitch + and −, per-hand Reset and Reset both use real menu input and restore zero calibration')
 await H.ray_find(page,'mesh');before=await H.read(page);await H.action_ray(page,'precision');assert (await H.read(page))['precision']!=before['precision'];await H.action_ray(page,'precision')
 await H.action_ray(page,'snap');assert (await H.read(page))['snap']!=before['snap'];await H.action_ray(page,'snap');record('Precision and Snap toggles change native controller policy without source/history edits')
 await H.ray_find(page,'studio');await H.action_ray(page,'menu-reset');anchor=next(x['center'] for x in (await H.read(page,True))['paletteActions'] if x['action']=='objects')
 target=next(x['center'] for x in (await H.read(page,True))['paletteActions'] if x['action']=='mesh');await H.aim(page,target);await H.button(page,'right','squeeze',True,3);assert (await H.read(page))['gesture']['kind']=='menu'
 await H.move_hand(page,[.035,.02,0]);moved=next(x['center'] for x in (await H.read(page,True))['paletteActions'] if x['action']=='objects');assert H.distance(anchor,moved)>.02
 await H.tap(page,'right','b-button');await H.button(page,'right','squeeze',False,3);restored=next(x['center'] for x in (await H.read(page,True))['paletteActions'] if x['action']=='objects');assert H.distance(anchor,restored)<1e-6
 record('Grip ray moves independent world-space console, and B cancels placement exactly without moving model geometry')
 await H.action_ray(page,'menu-hide');assert not (await H.read(page))['paletteVisible'];await H.tap(page,'left','x-button');assert (await H.read(page))['paletteVisible'];await H.settle_menu(page)
 await H.ray_find(page,'help');assert (await H.read(page))['helpVisible'];await H.action_ray(page,'help');assert not (await H.read(page))['helpVisible']
 record('Hide menu/X restore and Controller Guide open/close retain usable native menu input')
 assert await H.parts(page)==original and (await H.read(page))['undoDepth']==depth
 await H.screenshot_xr(page,'display-menu.png')
async def run_case(browser,name,flow):
 context,page=await H.open_model(browser,RESULT['pageErrors'],quest=True)
 try:
  await H.enter(page);await H.settle_menu(page);await flow(page)
  await H.ray_find(page,'exit');await page.wait_for_function('()=>!window.SWYRL_ENGINE_MODEL_VR.inspect().sessionAttached');assert (await H.read(page))['nativeParentRestored'];record(name+': Exit restores native desktop model parent')
 except Exception as e:
  info={'case':name,'failure':type(e).__name__+': '+str(e),'traceback':traceback.format_exc()}
  try:info['state']=await H.read(page,True);await H.screenshot_xr(page,name+'-failure.png')
  except Exception:pass
  RESULT['failures'].append(info);save();print('VR438_FAIL '+name+' '+str(e),flush=True)
 finally:await context.close()
async def main():
 save()
 async with H.async_playwright() as p:
  browser=await p.chromium.launch(executable_path=H.args.chromium,headless=True,args=['--no-sandbox','--disable-dev-shm-usage','--enable-webgl','--enable-unsafe-swiftshader'])
  try:
   for name,flow in [('creation',create_flow),('sculpt',sculpt_flow),('selection',selection_flow),('menus',menu_flow),('camera-debug',camera_debug)]:
    if not os.environ.get('MODEL_VR_CASES') or name in os.environ['MODEL_VR_CASES'].split(','):await run_case(browser,name,flow)
  finally:await browser.close()
 RESULT['status']='PASS' if not RESULT['failures'] and not RESULT['pageErrors'] else 'FAIL';save();print(json.dumps({'status':RESULT['status'],'checks':len(RESULT['checks']),'failures':[x['case']+': '+x['failure'] for x in RESULT['failures']],'pageErrors':RESULT['pageErrors']}),flush=True)
if __name__=='__main__':
 asyncio.run(main())
