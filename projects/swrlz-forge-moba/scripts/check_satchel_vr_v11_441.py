#!/usr/bin/env python3
"""Actual IWER Quest 2 controller walkthrough of the seven-objective satchel lesson.

The fixture is disposable guest geometry. Browser emulation proves software
transactions/rendering, not physical headset comfort or sustained frame time.
The pinned emulator never enters the engine package.
"""
import argparse
import asyncio
import hashlib
import json
import math
import tempfile
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
from playwright.async_api import async_playwright
ROOT=Path(__file__).resolve().parents[1]
FORGE='https://kamiloki-swrlz-forge-moba.static.hf.space'
CHAT='https://kamiloki-swyrlz.hf.space'
CDN='https://cdn.jsdelivr.net'
THREE_URL=CDN+'/npm/three@0.169.0/+esm'
IWER_URL=CDN+'/npm/iwer@2.8.0/build/iwer.min.js'
IWER_BYTES=384266
IWER_SHA='79fb12295642d3cbab36b28a2a4ba8b4a48a5053ce70057da2f249b67daa9780'
cli=argparse.ArgumentParser(description=__doc__)
cli.add_argument('--html',required=True)
cli.add_argument('--output')
cli.add_argument('--chromium',default='/usr/bin/chromium')
cli.add_argument('--iwer')
cli.add_argument('--expect-sha')
cli.add_argument('--assets-root', help='Reuse packaged assets without copying')
cli.add_argument('--three', help='Local exact Three r169 ESM for controller math')
cli.add_argument('--diagnostic-header-grip',action='store_true',help='Temporary diagnostic: grip the unobstructed quest header instead of its overlapping body area')
args=cli.parse_args()
html=Path(args.html).resolve();assert html.is_file(),html
SHA=hashlib.sha256(html.read_bytes()).hexdigest()
if args.expect_sha:assert SHA==args.expect_sha,'The test must use the sealed artifact'
out=Path(args.output or tempfile.mkdtemp(prefix='swrlz-satchel-vr441-')).resolve();out.mkdir(parents=True,exist_ok=True)
if args.iwer:iwer_bytes=Path(args.iwer).read_bytes()
else:
    with urlopen(IWER_URL,timeout=30) as response:iwer_bytes=response.read(IWER_BYTES+1)
assert len(iwer_bytes)==IWER_BYTES and hashlib.sha256(iwer_bytes).hexdigest()==IWER_SHA
assets=Path(args.assets_root).resolve() if args.assets_root else html.parent
three=Path(args.three).resolve() if args.three else None
# The engine lives in a private IIFE. Add a test-only observer to the routed
# response, never to the sealed file. It returns values and world-space button
# centers only; no tool dispatcher, editable object, or mutation is exposed.
OBSERVED_HTML=html.read_text()
anchor='installPerformanceSettings();se189InstallPerfUI();'
observer='''window.__SATCHEL441_BEGIN_TRACE=[];window.__SATCHEL441_DISPATCH_TRACE=[];window.__SATCHEL441_TRIGGER_TRACE=[];
(()=>{const prior=se340BeginGesture;se340BeginGesture=function(record,purpose){
 const fresh=se340Hit(record,false),contact=se360MenuContact(record),pose=se340GripPose(record);
 const before={hand:record?.input?.handedness,purpose,held:record?.held,hitAction:record?.hit?.action,
  hitQuest:!!record?.hit?.quest,gripTracked:record?.gripTracked,pose:!!pose,
  fresh:{id:fresh?.id,action:fresh?.action,quest:!!fresh?.quest,distance:fresh?.distance},
  contact:{id:contact?.id,action:contact?.action,quest:!!contact?.quest,distance:contact?.distance},
  gesture:se340XR.gesture?.kind||null};
 const result=prior.apply(this,arguments);window.__SATCHEL441_BEGIN_TRACE.push({before,result,
  after:{questDrag:!!se340XR.se413Quest?.drag,gesture:se340XR.gesture?.kind||null}});
 return result;
};const trigger=se340Trigger;se340Trigger=function(record){
 const fresh=se340Hit(record,false),contact=se360MenuContact(record);
 const before={hand:record?.input?.handedness,hoverAction:record?.hit?.action,
  fresh:{id:fresh?.id,action:fresh?.action,quest:!!fresh?.quest,distance:fresh?.distance},
  contact:{id:contact?.id,action:contact?.action,quest:!!contact?.quest,distance:contact?.distance}};
 const result=trigger.apply(this,arguments);window.__SATCHEL441_TRIGGER_TRACE.push({before,result,
  questMessage:se340XR.se413Quest?.message||''});return result;
};const dispatch=se350Dispatch;se350Dispatch=function(sample){if(sample.events?.length){
 window.__SATCHEL441_DISPATCH_TRACE.push(sample.events.map(e=>({action:e.action,phase:e.phase,hand:e.hand,
  sourceHand:e.source?.record?.input?.handedness||null})));}return dispatch.apply(this,arguments);};})();
window.__SATCHEL441_OBSERVE=()=>({
 orbit:{pitch:se340XR.pitch,yaw:se340XR.yaw,baseYaw:se340XR.baseYaw,
   center:se340XR.rig?.position.toArray()||[0,0,0]},
 questTargets:(se340XR.se413Quest?.buttons||[]).filter(b=>b.visible!==false).map(b=>({
   action:b.userData.se340Action,center:b.getWorldPosition(new THREE.Vector3()).toArray()})),
 viewerPosition:se340XR.lastViewer?.position?.toArray?.()||null,
 questPose:se340XR.se413Quest?{position:se340XR.se413Quest.root.position.toArray(),quaternion:se340XR.se413Quest.root.quaternion.toArray(),userPositioned:!!se340XR.se413Quest.userPositioned}:null,
 consolePose:se340XR.ui?{position:se340XR.ui.root.position.toArray(),quaternion:se340XR.ui.root.quaternion.toArray()}:null,
 questMessage:se340XR.se413Quest?.message||'',projectBusy:!!se340XR.se372ProjectBusy,
 input:{beginTrace:window.__SATCHEL441_BEGIN_TRACE.slice(-10),dispatchTrace:window.__SATCHEL441_DISPATCH_TRACE.slice(-10),triggerTrace:window.__SATCHEL441_TRIGGER_TRACE.slice(-10),
   events:(se340XR.inputSample?.events||[]).map(e=>({action:e.action,phase:e.phase,hand:e.hand})),
   held:Object.keys(se340XR.inputSample?.held||{}),controllers:se340XR.controllers.map(r=>({
     hand:r.input?.handedness,held:r.held,blockGrip:r.blockGrip,blockTrigger:r.blockTrigger,
     hitQuest:!!r.hit?.quest,hitUI:!!r.hit?.ui,hitAction:r.hit?.action||null}))},
 message:se340XR.message||'',workflow:currentProject?.se441TutorialWorkflow||null,
 instanceId:currentProject?.instanceId||null,tutorial:currentProject?.se412Tutorial||null
});\n'''
assert OBSERVED_HTML.count(anchor)==1
OBSERVED_HTML=OBSERVED_HTML.replace(anchor,observer+anchor,1)
anchor="controllers:se340XR.controllers.map(r=>({index:r.index,handedness:r.input?.handedness||'none',"
assert OBSERVED_HTML.count(anchor)==1
OBSERVED_HTML=OBSERVED_HTML.replace(anchor,anchor+"hitAction:r.hit?.action||null,",1)
OBSERVED_SHA=hashlib.sha256(OBSERVED_HTML.encode()).hexdigest()


def http(url, method, headers, body):
    try:
        response = urlopen(Request(url, data=body, headers=headers, method=method), timeout=25)
    except HTTPError as error:
        response = error
    with response:
        data = response.readline(262144) if urlsplit(url).path == '/api/lalm_station/stream' else response.read()
        wanted = {'content-type', 'content-security-policy', 'access-control-allow-origin',
                  'access-control-allow-credentials', 'cache-control'}
        return response.status, {k: v for k, v in response.headers.items() if k.lower() in wanted}, data

async def transport(route):
    request = route.request
    url = urlsplit(request.url)
    origin = url.scheme + '://' + url.netloc
    if origin == FORGE:
        if url.path in ('/', '/index.html', '/modeler.html'):
            return await route.fulfill(body=OBSERVED_HTML, content_type='text/html')
        asset = (assets / url.path.lstrip('/')).resolve()
        if asset.is_relative_to(assets) and asset.is_file():
            return await route.fulfill(path=str(asset))
        return await route.fulfill(status=404, body='Missing packaged test asset')
    if three and request.url == THREE_URL:
        return await route.fulfill(path=str(three), content_type='text/javascript')
    if origin not in (CHAT, CDN):
        return await route.abort('blockedbyclient')
    allowed = {'accept', 'content-type', 'origin', 'referer'}
    headers = {k: v for k, v in (await request.all_headers()).items() if k.lower() in allowed}
    try:
        status, headers, data = await asyncio.to_thread(http, request.url, request.method, headers, request.post_data_buffer)
    except Exception:
        return await route.abort('failed')
    return await route.fulfill(status=status, headers=headers, body=data)

async def read(page, geometry=False):
    return await page.evaluate('(geometry)=>window.SWYRL_ENGINE_MODEL_VR.inspect({geometry})', geometry)

async def parts(page):
    return await page.evaluate('()=>window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier.parts')

async def frames(page, count=3):
    state=await read(page)
    if not state['sessionAttached']:
        return
    start=state['frameCount']
    await page.wait_for_function('(n)=>{const s=window.SWYRL_ENGINE_MODEL_VR.inspect();return !s.sessionAttached||s.frameCount>=n}', arg=start+count, timeout=20000)

async def button(page, side, key, pressed, count=2):
    await page.evaluate('([side,key,value])=>xrTestDevice.controllers[side].updateButtonValue(key,value)', [side, key, 1 if pressed else 0])
    await frames(page, count)
    if key=='squeeze' and pressed:
        await page.wait_for_timeout(260);await frames(page,3)

async def tap(page, side, key):
    await button(page, side, key, True, 2)
    await button(page, side, key, False, 3)
    await page.wait_for_timeout(260)
    await frames(page,2)

async def aim(page, target, side='right', origin=None):
    """Set only IWER controller pose; invert the native reference-space orbit."""
    origin=origin or ([.22,1.3,-.35] if side=='right' else [-.22,1.3,-.35])
    orbit=await page.evaluate('()=>window.__SATCHEL441_OBSERVE().orbit')
    await page.evaluate('''([side,origin,target,orbit])=>{
      const T=window.__VR_THREE,c=xrTestDevice.controllers[side];
      const p=new T.Vector3(...origin),d=new T.Vector3(...target).sub(p).normalize();
      const orientation=new T.Quaternion().setFromUnitVectors(new T.Vector3(0,0,-1),d);
      // Engine inspectors and panels are in the active offset reference space.
      // Read its transform; controllers themselves remain actual IWER devices.
      const q=new T.Quaternion().setFromEuler(new T.Euler(orbit.pitch,orbit.yaw-orbit.baseYaw,0,'YXZ'));
      const pivot=new T.Vector3(...orbit.center),t=pivot.clone().sub(pivot.clone().applyQuaternion(q));
      p.applyQuaternion(q).add(t);orientation.premultiply(q);
      c.position.set(p.x,p.y,p.z);c.quaternion.set(orientation.x,orientation.y,orientation.z,orientation.w);
    }''', [side,origin,target,orbit])
    await frames(page,4)

async def aim_part(page, part_id, side='right'):
    detail = await read(page, True)
    target = next(item for item in detail['targetCenters'] if item['id'] == part_id)
    await aim(page, target['center'], side=side)
    await page.wait_for_function('([id,side])=>window.SWYRL_ENGINE_MODEL_VR.inspect().controllers.some(c=>c.handedness===side&&c.hoverId===id)', arg=[part_id, side])
    return target

async def action_ray(page, action, side='right'):
    detail = await read(page, True)
    target = next((item for item in detail['paletteActions'] if item['action'] == action), None)
    if target is None:
        raise AssertionError('Action '+action+' missing on page '+str(detail.get('page'))+': '+str([i['action'] for i in detail['paletteActions']]))
    await press_world_action(page,action,target['center'],side)
    await settle_menu(page)


async def press_world_action(page,action,target,side='right'):
    origins=[None,plus(target,[0,0,.25]),plus(target,[-.25,0,0]),plus(target,[.25,0,0])]
    for origin in origins:
        await aim(page,target,side=side,origin=origin)
        if any(c.get('handedness')==side and c.get('hitAction')==action for c in (await read(page))['controllers']):break
    else:raise AssertionError(('Actual controller did not hover visible action',action,await read(page,True)))
    await tap(page,side,'trigger')

async def chord(page, controls, count=3):
    """Depress/release the named hardware controls together in actual XR frames."""
    await page.evaluate('(items)=>{for(const [side,key]of items)xrTestDevice.controllers[side].updateButtonValue(key,1)}',controls)
    await frames(page,count)
    await page.evaluate('(items)=>{for(const [side,key]of items)xrTestDevice.controllers[side].updateButtonValue(key,0)}',controls)
    await frames(page,3)

async def hints(page):
    return await page.evaluate('()=>window.SWYRL_ENGINE_VR_CONTROLLER_HINTS?.inspect?.()||null')

def distance(a,b):
    return sum((x-y)**2 for x,y in zip(a,b))**.5

async def screenshot_xr(page, name):
    # A real headset excludes browser DOM. Raise only IWER's test preview
    # container so the screenshot reflects the actual XR canvas, not DOM UI.
    await page.evaluate('()=>{xrTestDevice.canvasContainer.style.zIndex="2147483647";}')
    await page.screenshot(path=str(out / name))

async def open_model(browser, errors, emulated=True, denied=False, quest=False):
    options={'viewport': {'width': 1280, 'height': 960}, 'accept_downloads': True}
    if quest:
        options['user_agent']='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) OculusBrowser/33.0.0.0 Chrome/126.0.0.0 VR Safari/537.36'
    context = await browser.new_context(**options)
    if emulated:
        setup = iwer_bytes.decode() + '''\nif(location.origin===''' + json.dumps(FORGE) + '''){
          window.xrTestDevice=new IWER.XRDevice(IWER.metaQuest2,{stereoEnabled:false});
          xrTestDevice.installRuntime({forceInstall:true});xrTestDevice.position.set(0,1.65,0);
          xrTestDevice.controllers.left.position.set(-.3,1.22,-.4);xrTestDevice.controllers.right.position.set(.3,1.22,-.4);
        }'''
        await context.add_init_script(script=setup)
    for origin in (FORGE, CHAT, CDN):
        await context.route(origin + '/**', transport)
    page = await context.new_page()
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.on('dialog', lambda dialog: asyncio.create_task(dialog.accept()))
    await page.goto(FORGE + '/modeler.html', wait_until='domcontentloaded', timeout=90000)
    await page.wait_for_function('()=>window.SWRLZ_FORGE_BUILD?.version==="v11.441"&&!!window.SWYRL_ENGINE_MODEL_VR&&!!window.SWYRL_ENGINE_MODEL_WORKSHOP')
    if await page.locator('#seReleaseNotesDialog[open]').count():
        await page.locator('#seReleaseNotesDialog[open] button').last.evaluate('(node)=>node.click()')
    await open_projects(page)
    await page.locator('#se412Tab').click()
    await page.get_by_role('button', name='Start new satchel quest', exact=True).click()
    await page.wait_for_function('()=>window.SWYRL_ENGINE_TUTORIAL_412?.status().active&&document.querySelector("#se340EnterModelVR")')
    if emulated:
        await page.evaluate('async(url)=>{window.__VR_THREE=await import(url)}', THREE_URL)
    if denied:
        await page.evaluate('()=>{navigator.xr.requestSession=()=>Promise.reject(new Error("Test permission denial"));}')
    return context, page

async def enter(page):
    entry = page.locator('#se340EnterModelVR')
    await entry.scroll_into_view_if_needed()
    assert await entry.is_enabled()
    await entry.click()
    await page.wait_for_function('()=>window.SWYRL_ENGINE_MODEL_VR.inspect().active&&window.SWYRL_ENGINE_MODEL_VR.inspect().frameCount>4', timeout=30000)
    await page.wait_for_function('()=>window.SWYRL_ENGINE_MODEL_VR.inspect().controllers.filter(c=>c.targetTracked&&c.gripTracked).length===2')
    await frames(page, 3)

async def settle_menu(page):
    if not (await read(page))['sessionAttached']:
        return
    await page.wait_for_function('()=>{const s=window.SWYRL_ENGINE_MODEL_VR.inspect(),m=s.menu;return !s.sessionAttached||!!m&&(!m.motion?.active||(!!s.gesture||!!s.creation?.active||!!s.accessory?.active)&&m.motion?.reveal>.999&&m.motion?.transition>.999)}', timeout=15000)
    if (await read(page))['sessionAttached']:
        await frames(page, 2)


def native(state):
    return state.get('manual',{}).get('native',{})


def topology_audit(data):
    xyz=data['positions'];indices=data['indices'];edges={};volume=0
    assert len(xyz)%3==0 and len(indices)%3==0
    for f in range(0,len(indices),3):
        ids=indices[f:f+3];assert len(set(ids))==3
        a,b,c=[xyz[i*3:i*3+3] for i in ids]
        ab=[b[k]-a[k] for k in range(3)];ac=[c[k]-a[k] for k in range(3)]
        cross=[ab[1]*ac[2]-ab[2]*ac[1],ab[2]*ac[0]-ab[0]*ac[2],ab[0]*ac[1]-ab[1]*ac[0]]
        assert sum(x*x for x in cross)>1e-18,'A rendered operation collapsed a triangle'
        volume+=(a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0]))/6
        for k in range(3):
            edge=(ids[k],ids[(k+1)%3]);edges.setdefault(tuple(sorted(edge)),[]).append(edge)
    assert all(len(value)==2 and value[0]==value[1][::-1] for value in edges.values()),'The cavity must remain consistently wound and manifold'
    return {'vertices':len(xyz)//3,'triangles':len(indices)//3,'signedVolume':volume}


async def manual_menu(page):
    await action_ray(page,'studio')
    await action_ray(page,'mesh')
    await action_ray(page,'manual-mesh')
    state=await read(page);assert state['manual']['active'] and state['page']=='manual-mesh'


async def quest_state(page):
    return await page.evaluate('''()=>{const observed=window.__SATCHEL441_OBSERVE();return {status:window.SWYRL_ENGINE_TUTORIAL_412.status(),
      steps:window.SWYRL_ENGINE_TUTORIAL_412.steps(),
      quest:window.SWYRL_ENGINE_TUTORIAL_VR_413.inspect(),
      academy:window.SWYRL_E_SATCHEL_ACADEMY_416.inspect(),
      coach:window.SWYRL_E_SATCHEL_VR_COACH_416.status(),
      message:observed.questMessage,workflow:observed.workflow,
      visibleQuestActions:observed.questTargets.map(b=>b.action),
      instanceId:observed.instanceId,tutorial:observed.tutorial}}''')


async def quest_ray(page, action):
    target=await page.evaluate('action=>window.__SATCHEL441_OBSERVE().questTargets.find(b=>b.action===action)?.center||null',action)
    assert target is not None, ('Visible quest control missing',action,await quest_state(page))
    await press_world_action(page,action,target)
    await frames(page,10)
    await settle_menu(page)


async def advance(page, completed):
    state=await quest_state(page)
    assert state['steps'][completed]['done'],state
    await quest_ray(page,'se413-next')
    assert (await quest_state(page))['quest']['step']==completed+1


async def verify(page,index,expected=True):
    await quest_ray(page,'se413-check')
    state=await quest_state(page)
    assert state['quest']['step']==index,state
    assert state['steps'][index]['done']==expected,state
    return state


async def report_geometry(page):
    return await page.evaluate('''()=>window.SWYRL_E_SATCHEL_WORKFLOW_441.inspect(
      window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier.parts,{allowLegacy:false})''')


def point(matrix,p):
    return [sum(matrix[k*4+i]*p[k] for k in range(3))+matrix[12+i] for i in range(3)]


def vector(matrix,p):
    return [sum(matrix[k*4+i]*p[k] for k in range(3)) for i in range(3)]


def plus(a,b):return [x+y for x,y in zip(a,b)]
def minus(a,b):return [x-y for x,y in zip(a,b)]


async def move_hand(page,delta,side='right'):
    orbit=await page.evaluate('()=>window.__SATCHEL441_OBSERVE().orbit')
    await page.evaluate('''([side,delta,orbit])=>{
      const T=window.__VR_THREE,c=xrTestDevice.controllers[side];
      const q=new T.Quaternion().setFromEuler(new T.Euler(orbit.pitch,orbit.yaw-orbit.baseYaw,0,'YXZ'));
      const d=new T.Vector3(...delta).applyQuaternion(q);
      c.position.set(c.position.x+d.x,c.position.y+d.y,c.position.z+d.z);
    }''',[side,delta,orbit])
    await frames(page,7)


async def mesh_mode(page,mode):
    await action_ray(page,'tools');await action_ray(page,'studio');await action_ray(page,'mesh')
    await action_ray(page,mode)
    assert (await read(page))['mode']==mode


async def angle(page,name):
    await action_ray(page,'views');await action_ray(page,'cameras');await action_ray(page,'view-'+name)
    await frames(page,8)
    assert (await read(page))['viewMode']==name


async def move_selected(page,delta):
    # Grab edits the existing Trigger selection even when pointing into air.
    await aim(page,[-1.6,1.0,-1.1])
    await button(page,'right','squeeze',True,3)
    assert (await read(page))['gesture']['mode']=='grab',await read(page)
    await move_hand(page,delta)
    await button(page,'right','squeeze',False,4)
    assert not (await read(page))['gesture']


async def move_quest_window(page,side='right',delta=None):
    # Test the same ray + Grip drag with either native controller.
    before=await parts(page);history=(await read(page))['undoDepth']
    layout=await page.evaluate('()=>window.__SATCHEL441_OBSERVE().consolePose')
    targets=await page.evaluate('()=>window.__SATCHEL441_OBSERVE().questTargets')
    grip_action='se413-fold' if args.diagnostic_header_grip else 'se413-check'
    target=next(t['center'] for t in targets if t['action']==grip_action)
    await aim(page,target,side=side)
    await page.wait_for_function('([action,side])=>window.SWYRL_ENGINE_MODEL_VR.inspect().controllers.some(c=>c.handedness===side&&c.hitAction===action)',arg=[grip_action,side])
    await button(page,side,'squeeze',True,3)
    assert (await quest_state(page))['coach']['dragging'],await page.evaluate('()=>window.__SATCHEL441_OBSERVE().input')
    delta=delta or [0,.55 if args.diagnostic_header_grip else .38,0]
    await move_hand(page,delta,side=side)
    await button(page,side,'squeeze',False,4)
    assert not (await quest_state(page))['coach']['dragging']
    after=await page.evaluate('action=>window.__SATCHEL441_OBSERVE().questTargets.find(t=>t.action===action).center',grip_action)
    assert all(abs(after[i]-target[i]-delta[i])<.005 for i in range(3))
    observed=await page.evaluate('()=>window.__SATCHEL441_OBSERVE()')
    assert observed['questPose']['userPositioned'] and observed['consolePose']==layout
    assert await parts(page)==before and (await read(page))['undoDepth']==history


async def fixed_quest_during_head_motion(page):
    observed=await page.evaluate('()=>window.__SATCHEL441_OBSERVE()')
    before=observed['questPose'];viewer=observed['viewerPosition']
    model=await parts(page)
    await page.evaluate('()=>{xrTestDevice.position.x+=.06;}')
    await frames(page,8)
    moved=await page.evaluate('()=>window.__SATCHEL441_OBSERVE()')
    assert viewer and moved['viewerPosition'] and abs(moved['viewerPosition'][0]-viewer[0]-.06)<.005
    assert moved['questPose']==before
    assert await parts(page)==model
    await page.evaluate('()=>{xrTestDevice.position.x-=.06;}')
    await frames(page,5)


async def draw_component(page,points,depth,name,hit_point,offset=(-2.0,0,0)):
    """Trace physical rays on the native fixed .5m plane, thicken, then Grab fit.

    Source points determine an intended silhouette only. Every saved vertex
    comes from the controller's Trigger/Grip sampled by the real XR loop.
    """
    await action_ray(page,'create-menu');await action_ray(page,'draw')
    # Native X hides the console while drawing in the adjacent open space.
    # This prevents a visible console card from owning the later thickness Grip.
    await tap(page,'left','x-button');assert not (await read(page))['paletteVisible']
    matrix=(await read(page,True))['modelRootMatrix']
    source=[plus(p,offset) for p in points]
    targets=[point(matrix,p) for p in source]
    normal=vector(matrix,[0,0,1]);length=math.sqrt(sum(v*v for v in normal));normal=[v/length for v in normal]
    origin=plus(targets[0],[v*.5 for v in normal])
    before=await parts(page);history=(await read(page))['undoDepth']
    await aim(page,targets[0],origin=origin)
    await button(page,'right','trigger',True,3)
    assert (await read(page))['gesture']['kind']=='draw',await read(page)
    for target in targets[1:]:await aim(page,target,origin=origin)
    assert await parts(page)==before,'Draw preview must not save any vertices before release'
    await button(page,'right','trigger',False,4)
    created=[p for p in await parts(page) if p['id'] not in {x['id'] for x in before}]
    assert len(created)==1,('Draw failed',created,await read(page))
    component=created[0];assert component['name']==name,component
    assert (await read(page))['mode']=='extrude'
    flat=await parts(page);assert (await read(page))['undoDepth']==history+1
    # Aim into actual material of the U-band, never its empty bounding center.
    target=point(matrix,plus(hit_point,offset))
    await aim(page,target,origin=plus(target,[v*.55 for v in normal]))
    await button(page,'right','squeeze',True,3)
    assert (await read(page))['gesture']['kind']=='extrude',await read(page)
    await move_hand(page,vector(matrix,[0,0,depth]))
    assert await parts(page)==flat,'Thickness preview must preserve source'
    await button(page,'right','squeeze',False,4)
    thick=next(p for p in await parts(page) if p['id']==component['id'])
    audit=topology_audit(thick['topologyMesh']);assert audit['signedVolume']>0
    assert (await read(page))['undoDepth']==history+2
    await tap(page,'left','x-button');await settle_menu(page)
    await mesh_mode(page,'grab')
    await move_selected(page,vector(matrix,[-v for v in offset]))
    fitted=next(p for p in await parts(page) if p['id']==component['id'])
    assert distance(fitted['position'],component['position'])>1
    return component['id'],audit


async def save_local(page):
    await action_ray(page,'projects');await action_ray(page,'save-local')
    await page.wait_for_function('()=>{const s=window.__SATCHEL441_OBSERVE();return !s.projectBusy&&String(s.message).startsWith("Device save confirmed")}',timeout=30000)


async def exit_vr(page):
    await action_ray(page,'tools');await action_ray(page,'exit')
    await page.wait_for_function('()=>!window.SWYRL_ENGINE_MODEL_VR.inspect().sessionAttached')
    assert (await read(page))['nativeParentRestored']


async def open_projects(page):
    studio=page.locator('#se320ModelProjects')
    await (studio if await studio.is_visible() else page.locator('#projectBtn')).click()


async def reopen_local(page,lesson_id):
    token=(await read(page))['documentToken']
    await open_projects(page)
    await page.locator('#se170-tab-mine').click()
    card=page.locator('#se184LocalCards .se184-project-card[data-source="local"][data-project-id="'+lesson_id+'"]')
    await card.get_by_role('button',name='Open project',exact=True).click()
    await page.wait_for_function('''([id,token])=>window.__SATCHEL441_OBSERVE().instanceId===id&&
      window.SWYRL_ENGINE_TUTORIAL_412.status().active&&
      window.SWYRL_ENGINE_MODEL_VR.inspect().documentToken!==token&&
      !document.querySelector('#projectHub').classList.contains('show')''',arg=[lesson_id,token])


async def flow(browser,errors,record):
    context,page=await open_model(browser,errors,quest=True)
    try:
        original=await parts(page);lesson=await quest_state(page);lesson_id=lesson['instanceId']
        assert len(original)==1 and original[0]['id']=='model-seed' and original[0]['kind']=='box',original
        assert original[0]['scale']==[1.4,1,.65] and lesson['workflow']=='one-body-v1',lesson
        await enter(page);await settle_menu(page)
        assert (await quest_state(page))['quest']['worldSpace']
        copy_layout=await page.evaluate('''()=>{
          const c=document.createElement('canvas').getContext('2d');
          function lines(text,font,width){c.font=font;let line='',count=1;for(const word of text.split(/\\s+/)){
            const next=line?line+' '+word:word;if(c.measureText(next).width<=width)line=next;else{count++;line=word;}}return count;}
          return window.SWYRL_E_SATCHEL_LESSON_441.steps.map(s=>({title:s.title,
            taskLines:lines(s.vrTask,'29px system-ui',950),hintLines:lines('TIP: '+s.vrHint,'italic 27px system-ui',947)}));
        }''')
        assert all(row['taskLines']<=4 and row['hintLines']<=2 for row in copy_layout),copy_layout
        await aim_part(page,'model-seed') # Default quest placement must leave the first model pick clear.
        await fixed_quest_during_head_motion(page)
        await screenshot_xr(page,'01-one-cube-quest.png')
        await move_quest_window(page)
        await move_quest_window(page,side='left',delta=[.04,-.04,0])
        await fixed_quest_during_head_motion(page)
        await screenshot_xr(page,'01b-quest-window-moved-aside.png')
        await aim_part(page,'model-seed');await tap(page,'right','trigger')
        await quest_ray(page,'se416-show')
        await action_ray(page,'grab')
        matrix=(await read(page,True))['modelRootMatrix']
        await move_selected(page,vector(matrix,[.06,.03,0]))
        assert await parts(page)!=original
        await tap(page,'left','y-button');assert await parts(page)==original
        await quest_ray(page,'se416-checkpoint')
        assert (await quest_state(page))['academy']['checkpoints'],await quest_state(page)
        await move_selected(page,vector(matrix,[.05,0,0]));moved=await parts(page)
        await quest_ray(page,'se416-restore')
        assert await parts(page)==moved,'Restore requires a second deliberate confirmation before replacing current work'
        await quest_ray(page,'se416-restore');assert await parts(page)==original
        await tap(page,'left','y-button');assert await parts(page)==moved,'Undo must reverse a confirmed checkpoint restore'
        await tap(page,'left','y-button');assert await parts(page)==original
        await verify(page,0);await advance(page,0)
        record('Native Tutorials Start new creates one independent cube; default tutorial leaves the model pick clear, either-hand Grip moves only its own window, and head motion preserves the layout; Trigger/Grab/Y Undo and confirmed checkpoints preserve the body')

        await aim_part(page,'model-seed');await tap(page,'right','trigger')
        await quest_ray(page,'se416-show');assert (await read(page))['manual']['active']
        await action_ray(page,'manual-convert')
        converted=await parts(page);assert converted[0]['kind']=='topologyMesh'
        matrix=(await read(page,True))['modelRootMatrix'];top=point(matrix,[0,2,0])
        await aim(page,top,origin=plus(top,vector(matrix,[0,.65,.01])))
        await tap(page,'right','trigger')
        assert len(native(await read(page))['selection']['faceIds'])==2
        await quest_ray(page,'se416-show')
        assert (await read(page))['manual']['operation']=='inset' and (await read(page))['manual']['amount']==.2
        await action_ray(page,'manual-preview');assert native(await read(page))['preview']['active']
        assert await parts(page)==converted
        await tap(page,'right','b-button');assert not native(await read(page))['preview']['active']
        assert await parts(page)==converted
        await action_ray(page,'manual-preview');await action_ray(page,'manual-apply')
        inset=await parts(page);assert len(native(await read(page))['selection']['faceIds'])==2
        await quest_ray(page,'se416-show')
        assert (await read(page))['manual']['operation']=='extrude' and (await read(page))['manual']['amount']==-.75
        await action_ray(page,'manual-preview');assert await parts(page)==inset
        await screenshot_xr(page,'02-inward-cavity-preview.png')
        await action_ray(page,'manual-apply');cavity=await parts(page)
        audit=topology_audit(cavity[0]['topologyMesh']);assert audit['vertices']==16 and audit['triangles']==28
        assert (await report_geometry(page))['body']['ok']
        await tap(page,'left','y-button');assert await parts(page)==inset
        await chord(page,[['left','x-button'],['left','y-button']],count=5)
        await page.wait_for_timeout(260);await frames(page,3)
        assert await parts(page)==cavity
        await verify(page,1);await advance(page,1)
        record('Actual menu and controller top-face selection perform Inset .20 and inward Extrude -.75 with uncommitted Preview, B Cancel, retained cap, native Apply, Undo and Redo')

        await angle(page,'front')
        await quest_ray(page,'se416-ghost');ghost_before=await parts(page)
        assert (await quest_state(page))['academy']['ghostMeshes']==1
        await quest_ray(page,'se416-ghost');assert await parts(page)==ghost_before
        flap_points=[[-.65,1.95,.36],[.65,1.95,.36],[.57,1.55,.36],[0,1.43,.36],[-.57,1.55,.36]]
        flap_id,flap_audit=await draw_component(page,flap_points,.04,'Satchel flap',[0,1.80,.36])
        assert (await report_geometry(page))['flap']['ok'],await report_geometry(page)
        await screenshot_xr(page,'03-drawn-pointed-flap.png')
        await verify(page,2);await advance(page,2)
        assert not (await report_geometry(page))['strap']['ok'],'Body/flap cannot falsely satisfy the strap'
        strap_points=[[-.72,1.65,.32],[-.72,2.80,.32],[-.50,3.05,.32],[.50,3.05,.32],[.72,2.80,.32],[.72,1.65,.32],[.56,1.65,.32],[.56,2.73,.32],[.43,2.90,.32],[-.43,2.90,.32],[-.56,2.73,.32],[-.56,1.65,.32]]
        strap_id,strap_audit=await draw_component(page,strap_points,.035,'Satchel strap',[0,2.97,.32])
        assert (await report_geometry(page))['strap']['ok'],await report_geometry(page)
        await screenshot_xr(page,'04-drawn-u-strap.png')
        await verify(page,3);await quest_ray(page,'se416-checkpoint');await advance(page,3)
        record('Actual Trigger strokes create separate pointed flap and concave U-band in open space; real Grip gives closed thickness, explicit Grab fits them, and the strap retains its empty middle')

        clasp_points=[[-.10,1.68,.405],[0,1.79,.405],[.10,1.68,.405],[0,1.57,.405]]
        clasp_id,clasp_audit=await draw_component(page,clasp_points,.03,'Satchel clasp',[0,1.68,.405])
        assert (await report_geometry(page))['clasp']['ok'],await report_geometry(page)
        assert next(p for p in await parts(page) if p['id']==clasp_id)['material']=='matte'
        assert 'se416-metal' not in (await quest_state(page))['visibleQuestActions'],'Materials must wait until the finishing objective'
        await verify(page,4);await advance(page,4)
        await verify(page,5,expected=False)
        await quest_ray(page,'se416-show')
        assert (await quest_state(page))['coach']['coachMode']=='material'
        await mesh_mode(page,'inspect')
        # Use real rays on exposed portions of each intended mesh. Part centers
        # may be occluded by the independently fitted flap or clasp.
        matrix=(await read(page,True))['modelRootMatrix']
        for source,part_id,paint in [([.55,1.20,.325],'model-seed','se416-leather'),([.40,1.75,.40],flap_id,'se416-leather'),([-.64,2.4,.355],strap_id,'se416-leather'),([0,1.68,.435],clasp_id,'se416-metal')]:
            target=point(matrix,source)
            await aim(page,target,origin=plus(target,vector(matrix,[0,0,.65])))
            await tap(page,'right','trigger')
            assert (await read(page))['selectionIds']==[part_id],(part_id,await read(page))
            await quest_ray(page,paint)
            expected='metal' if paint.endswith('metal') else 'matte'
            actual=next(p for p in await parts(page) if p['id']==part_id)
            assert actual['material']==expected and actual['color']==('#c9a56c' if expected=='metal' else '#916b48'),actual
        await verify(page,5);await advance(page,5)
        record('A native thickened diamond clasp passes geometry before Metal; actual quest Materials-row rays paint the selected body/flap Leather and clasp Metal, then finishing Verify passes')

        for view in ['top','front','left','back','right','front']:await angle(page,view)
        final=await report_geometry(page);assert final['ok'] and final['visualReviewRequired']
        before_save=await parts(page);assert len(before_save)==4
        await verify(page,6,expected=False)
        await save_local(page);await screenshot_xr(page,'05-finished-satchel.png')
        await exit_vr(page);await reopen_local(page,lesson_id)
        assert await parts(page)==before_save
        reopened=await quest_state(page);assert reopened['workflow']=='one-body-v1' and reopened['status']['progress']==6,reopened
        await enter(page);await settle_menu(page)
        assert (await quest_state(page))['quest']['step']==6
        await quest_ray(page,'se413-mark');assert (await quest_state(page))['status']['progress']==7
        await save_local(page);await screenshot_xr(page,'06-seven-complete-saved.png')
        await exit_vr(page);await reopen_local(page,lesson_id)
        assert await parts(page)==before_save
        reopened=await quest_state(page);assert reopened['status']['progress']==7 and all(s['done'] for s in reopened['steps']),reopened
        assert reopened['workflow']=='one-body-v1' and reopened['tutorial']=='satchel-001'
        assert not errors,errors
        record('Actual angle controls inspect top/front/sides/back; native Projects Save then My Projects reopen preserves all editable parts/materials and the method flag; final deliberate Done and second Save/reopen retain all seven checkoffs')
        return {'parts':4,'cavity':audit,'flap':flap_audit,'strap':strap_audit,'clasp':clasp_audit,
          'lessonId':lesson_id,'progressAfterReopen':7,'nativeParentRestored':True,'visualReviewRequired':True,
          'physicalHeadsetAcceptance':False,'authenticatedAccountSave':'UNTESTED'}
    except Exception as error:
        try:error.manual_state={'vr':await read(page,True),'observation':await page.evaluate('()=>window.__SATCHEL441_OBSERVE()'),'lesson':await quest_state(page),'parts':await parts(page),'workflow':await report_geometry(page)}
        except Exception:pass
        try:await screenshot_xr(page,'failure.png')
        except Exception:pass
        raise
    finally:await context.close()


async def main():
    errors=[]
    receipt={'version':'v11.441','testedHtmlSha256':SHA,
      'instrumentedSha256':OBSERVED_SHA,'instrumentation':'Read-only observer exposes native orbit, quest targets/message, save busy/message and tutorial identity; passive Begin/Trigger/dispatch traces preserve native calls; no editor operations or mutations',
      'runtime':'IWER 2.8.0 / Meta Quest 2 / actual controller rays, buttons and native XR renderer',
      'iwerSha256':IWER_SHA,'physicalHeadsetAcceptance':False,'authenticatedAccountSave':'UNTESTED',
      'checks':[],'pageErrors':errors,'status':'RUNNING'}
    def record(message):
        receipt['checks'].append(message);(out/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n')
        print('SATCHEL441_CHECK',message,flush=True)
    (out/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n')
    async with async_playwright() as playwright:
        browser=await playwright.chromium.launch(executable_path=args.chromium,headless=True,args=['--no-sandbox','--disable-dev-shm-usage','--enable-webgl','--enable-unsafe-swiftshader'])
        try:
            receipt['walkthrough']=await flow(browser,errors,record);assert not errors,errors;receipt['status']='PASS'
            print('MODEL_SATCHEL_VR_V11_441_BROWSER_PASS',json.dumps(receipt),flush=True)
        except Exception as error:
            receipt['status']='FAIL';receipt['failure']=type(error).__name__+': '+str(error)
            if hasattr(error,'manual_state'):receipt['failureState']=error.manual_state
            print('MODEL_SATCHEL_VR_V11_441_BROWSER_FAIL',receipt['failure'],'; receipt:',str(out/'verification.json'),flush=True)
            raise
        finally:
            (out/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');await browser.close()


asyncio.run(main())


