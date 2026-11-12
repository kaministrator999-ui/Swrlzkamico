#!/usr/bin/env python3
"""Focused native transform-handle browser acceptance.

Runs disposable guest fixtures under the editor's real static origin. Read-only
inspectors locate the rendered handles; actual browser mouse/touch input starts
and completes every transformation. No model command is invoked through eval.
Android means Chromium's Android-sized touch profile, not a physical device.
"""
import asyncio
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path

# The established harness owns routing, fixture loading and native UI helpers.
# Its supported CLI is deliberately also this script's CLI; importing it does
# not run its main() or its modeling workflow.
SPEC=importlib.util.spec_from_file_location('model_studio_browser430',Path(__file__).with_name('check_model_studio_v11_430.py'))
H=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(H)
ARGS,HTML,OUT,SHA=H.ARGS,H.HTML,H.OUT,H.SHA
CASES=set(filter(None,os.environ.get('SWYRLZ_GIZMO_CASES','').split(',')))
VALID_CASES={f'{kind}:{tool}:{axis}' for kind in ('object','component') for tool in ('move','rotate','scale') for axis in (('x','y','z','all') if tool=='scale' else ('x','y','z'))}
assert CASES<=VALID_CASES, 'Unknown gizmo test case'
FIXTURE=OUT/'gizmo-practice.swyrl.json'
data=H.fixture()
data['project']['name']=data['project']['projectName']='Transform handle practice'
data['project']['modelAtelier']['name']='Transform handle practice'
data['project']['modelAtelier']['parts']=[{'id':'gizmo431-cube','name':'Handle practice cube','kind':'box','position':[0,1.1,0],'rotation':[0,0,0],'scale':[.6,.6,.6],'color':'#c1a3ef','material':'matte','group':'Practice'}]
FIXTURE.write_text(json.dumps(data,indent=2)+'\n')


def authored(value):
    # Undo legitimately marks an imported document edited locally. Preserve
    # every authored field while excluding only that dirty-state timestamp.
    return {key:item for key,item in value.items() if key!='editedAt'}


async def access(page):
    return await page.evaluate('()=>window.SWYRL_ENGINE_MODEL_GIZMO_ACCESS.inspect()')


async def mode_ui(page,mode):
    await H.click_visible(page.locator('#se320ModelTransform [data-se320-transform="'+mode+'"]'))
    await page.wait_for_function('(m)=>window.SWYRL_ENGINE_MODEL_GIZMO_ACCESS.inspect().mode===m',arg=mode)
    await page.wait_for_timeout(100)


async def inspector(page,show):
    label='Show inspector' if show else 'Hide inspector'
    node=page.get_by_role('button',name=label,exact=True)
    if await node.count() and await node.is_visible():
        await H.click_visible(node)
        await page.wait_for_timeout(120)


async def prepare_view(page):
    # The existing 3/4 view keeps every axis visible instead of testing the
    # depth axis end-on. Collapse Settings and the inspector through real UI.
    await H.open_views(page)
    await H.click_visible(page.locator('[data-at-view="three"]'))
    await H.close_views(page)
    settings=page.locator('#se185AtelierTopToggle')
    if await settings.count() and await settings.get_attribute('aria-expanded')=='true':
        await H.click_visible(settings)
    await inspector(page,False)
    await H.click_visible(page.locator('#modelAtelierFrameSelected'))
    await page.wait_for_timeout(180)


async def ensure_component_selection(page):
    if (await H.workshop(page))['selection']['faceIds']:
        return
    await inspector(page,True)
    part=(await H.source(page))['parts'][0]
    await H.click_top_face(page,part)
    await prepare_view(page)


async def handle_target(page,axis,offset=True):
    state=await access(page)
    # Test native padded picking rather than relying on a synthetic mesh ray.
    # Prefer a non-overlapping curve point and an unobstructed canvas position.
    result=await page.evaluate('''({s,axis,offset})=>{
      const hs=s.handles.filter(h=>h.axis===axis&&!h.offCanvas&&(s.mode!=='rotate'||s.componentMode!=='mesh'||h.kind==='arc')),pivot=s.pivot||[innerWidth/2,innerHeight/2];
      const controls=[...document.querySelectorAll('#modelAtelierPanel button,#modelAtelierPanel summary,#se320ModelTransform')].filter(n=>{const r=n.getBoundingClientRect();if(r.width<=0||r.height<=0||r.bottom<=0||r.top>=innerHeight||getComputedStyle(n).visibility==='hidden')return false;const hit=document.elementFromPoint(Math.max(0,Math.min(innerWidth-1,r.left+r.width/2)),Math.max(0,Math.min(innerHeight-1,r.top+r.height/2)));return hit===n||n.contains(hit);}).map(n=>n.getBoundingClientRect());
      const relevant=s.handles.filter(h=>s.mode!=='rotate'||s.componentMode!=='mesh'||h.kind==='arc');
      const pointsOf=h=>(h.samples||h.points||[h.point]).map(p=>Array.isArray(p)?p:p?.inside?p.point:null).filter(Boolean);
      const distanceTo=(h,x,y)=>{
        const ps=pointsOf(h);if(!ps.length)return Infinity;
        if(h.kind!=='arc'||ps.length<2)return Math.hypot(x-ps[0][0],y-ps[0][1]);
        let distance=Infinity;
        for(let i=1;i<ps.length;i++){
          const a=ps[i-1],b=ps[i],dx=b[0]-a[0],dy=b[1]-a[1],n=dx*dx+dy*dy;
          const t=n?Math.max(0,Math.min(1,((x-a[0])*dx+(y-a[1])*dy)/n)):0;
          distance=Math.min(distance,Math.hypot(x-a[0]-dx*t,y-a[1]-dy*t));
        }
        return distance;
      };
      const candidates=[];
      for(const h of hs){
        const points=(h.samples||h.points||[h.point]).map(p=>Array.isArray(p)?p:p?.inside?p.point:null).filter(Boolean);
        for(let i=0;i<points.length;i++){
          const p=points[i];if(!p||p.length<2)continue;
          const next=points[(i+1)%points.length]||p;
          const before=points[(i+points.length-1)%points.length]||p;
          let dx=p[0]-pivot[0],dy=p[1]-pivot[1];
          if(h.kind==='arc'&&points.length>1){dx=next[0]-before[0];dy=next[1]-before[1];}
          let len=Math.hypot(dx,dy);if(len<1){dx=1;dy=-1;len=Math.SQRT2;}dx/=len;dy/=len;
          const r=h.radiusPx||s.touchRadius||22,visual=h.visualRadiusPx||5;
          const pad=offset?Math.min(r-3,Math.max(visual+3,12)):0;
          if(offset&&pad<=visual+1)continue;
          for(const sign of [-1,1]){
            // Arc offset is normal to its tangent; axis-tip offset is normal
            // to the drag direction, leaving the intended axis unambiguous.
            const x=p[0]-dy*pad*sign,y=p[1]+dx*pad*sign;
            if(document.elementFromPoint(x,y)?.tagName!=='CANVAS')continue;
            const clearance=Math.min(...controls.map(c=>Math.hypot(Math.max(c.left-x,0,x-c.right),Math.max(c.top-y,0,y-c.bottom))));
            if(clearance<28)continue;
            if(relevant.some(other=>other.axis!==axis&&distanceTo(other,x,y)<=pad+2))continue;
            candidates.push({x,y,dx,dy,axis,kind:h.kind,pad,visual,clearance,point:p,radius:r});
          }
        }
      }
      return candidates.sort((a,b)=>b.clearance-a.clearance)[0];
    }''',{'s':state,'axis':axis,'offset':offset})
    assert result,('No unobstructed target',axis,state)
    return result


async def gesture(page,session,target,mobile,cancel=False):
    x,y=target['x'],target['y']
    dx,dy=target['dx'],target['dy']
    # Arc targets carry a tangent direction. Other targets carry the native
    # projected axis direction. Uniform scale uses a diagonal displacement.
    if target['axis'] in ('all','uniform'):
        dx,dy=1/math.sqrt(2),-1/math.sqrt(2)
    travel=38
    if mobile:
        await session.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':x,'y':y,'id':1}]})
        for step in range(1,7):
            await session.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'x':x+dx*travel*step/6,'y':y+dy*travel*step/6,'id':1}]})
            await page.wait_for_timeout(12)
        active=await access(page)
        await session.send('Input.dispatchTouchEvent',{'type':'touchCancel' if cancel else 'touchEnd','touchPoints':[]})
    else:
        await page.mouse.move(x,y)
        await page.mouse.down()
        await page.mouse.move(x+dx*travel,y+dy*travel,steps=6)
        active=await access(page)
        active['browserPointerLocked']=await page.evaluate('()=>!!document.pointerLockElement')
        if cancel:
            await page.keyboard.press('Escape')
            if (await access(page)).get('dragging'):
                await page.keyboard.press('Escape')
        await page.mouse.up()
        await page.wait_for_timeout(120)
        # Desktop's existing precision workflow locks the mouse. A real Escape
        # releases that browser capture before clicking a toolbar or Undo.
        if not cancel and await page.evaluate('()=>!!document.pointerLockElement'):
            await page.keyboard.press('Escape')
            await page.wait_for_function('()=>!document.pointerLockElement')
            await page.wait_for_timeout(100)
    await page.wait_for_timeout(120)
    return active


async def undo(page):
    # The existing inspector owns a fully visible native Undo action on narrow
    # screens; its floating toolbar shortcut can sit under the view widget.
    await inspector(page,True)
    await H.undo_redo(page,'Undo')
    await inspector(page,False)
    await page.wait_for_timeout(180)


async def run_mode(browser,mode):
    mobile=mode=='android'
    directory=OUT/mode;directory.mkdir(exist_ok=True)
    context=await browser.new_context(viewport={'width':390 if mobile else 1440,'height':844 if mobile else 1000},is_mobile=mobile,has_touch=mobile,device_scale_factor=1)
    for origin in (H.FORGE,H.CHAT,H.CDN):
        await context.route(origin+'/**',H.transport)
    page=await context.new_page();page.set_default_timeout(30000)
    session=await context.new_cdp_session(page)
    page.on('dialog',lambda dialog:asyncio.create_task(dialog.accept()))
    errors=[]
    def page_error(error):
        errors.append(str(error));print(mode.upper()+' PAGE_ERROR '+str(error),flush=True)
    page.on('pageerror',page_error)
    result={'version':'v11.431','mode':mode,'testedHtmlSha256':SHA,'status':'RUNNING','checks':[],'pageErrors':errors,'physicalDeviceAcceptance':False,'requestedCases':sorted(CASES or VALID_CASES)}
    def save():
        (directory/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
    def passed(message,**extra):
        result['checks'].append({'check':message,**extra});save();print(mode.upper()+' PASS '+message,flush=True)
    async def stage(text):
        result['stage']=text;save();print(mode.upper()+' STAGE '+text,flush=True)
    try:
        await stage('Load assembled editor and disposable cube')
        await page.goto(H.FORGE+'/modeler.html',wait_until='domcontentloaded',timeout=90000)
        await stage('Wait for native gizmo integration')
        await page.wait_for_function('()=>window.SWRLZ_FORGE_BUILD?.version==="v11.431"&&!!window.SWYRL_ENGINE_MODEL_GIZMO_ACCESS',timeout=90000)
        notes=page.locator('#seReleaseNotesDialog[open]')
        if await notes.count():
            await notes.locator('button').last.click()
        await stage('Import disposable cube through native file input')
        await page.locator('#fileInput').set_input_files(str(FIXTURE))
        await page.wait_for_function('()=>window.SWYRL_ENGINE_AGENT.inspectScene().project?.modelAtelier?.parts?.[0]?.id==="gizmo431-cube"')
        await stage('Select cube through existing inspector')
        await H.choose_category(page,'Meshes','Select & organize')
        await page.locator('#atelierContextProxy_modelAtelierParts').select_option('gizmo431-cube')
        await prepare_view(page)
        for component in (False,True):
            label='component' if component else 'object'
            if component:
                await inspector(page,True)
                await H.manual(page)
                await H.native_action(page,'Make mesh editable')
                await page.wait_for_function('()=>window.SWYRL_ENGINE_MODEL_WORKSHOP.inspect().selection.mode==="face"')
                await ensure_component_selection(page)
            for tool in ('move','rotate','scale'):
                axes=('x','y','z','all') if tool=='scale' else ('x','y','z')
                for axis in axes:
                    if CASES and f'{label}:{tool}:{axis}' not in CASES:
                        continue
                    await stage(label+' '+tool+' '+axis+' padded handle')
                    if component:
                        await ensure_component_selection(page)
                    await mode_ui(page,tool)
                    before=await H.source(page)
                    before_history=await H.history(page)
                    zero_extent=False
                    if component and tool=='scale' and axis in ('x','y','z'):
                        selection=(await H.workshop(page))['selection']
                        part=next(p for p in before['parts'] if p['id']==selection['partId'])
                        topology=part['topologyMesh'];vertices={v for face in selection['faceIds'] for v in topology['indices'][face*3:face*3+3]}
                        values=[topology['positions'][v*3+'xyz'.index(axis)] for v in vertices]
                        zero_extent=bool(values) and max(values)-min(values)<1e-8
                    target=await handle_target(page,axis,offset=mobile)
                    if not mobile and not component and tool=='move' and axis=='x':
                        await page.mouse.move(target['x'],target['y'])
                        await page.wait_for_timeout(40)
                        hovered=await access(page)
                        assert hovered.get('activeAxis')=='x' and not hovered.get('dragging')
                        assert await H.source(page)==before and await H.history(page)==before_history
                        await page.screenshot(path=str(directory/'hover-feedback.png'))
                        passed('Mouse hover identifies the intended handle without changing geometry/history')
                    active=await gesture(page,session,target,mobile)
                    assert active.get('dragging'),('Padded handle did not begin native drag',target,active)
                    drag=active.get('dragging')
                    active_axis=(drag.get('axis') if isinstance(drag,dict) else None) or active.get('activeAxis') or active.get('axis')
                    assert active_axis==axis,('A neighboring handle captured the drag',axis,active_axis,target,active)
                    after=await H.source(page)
                    if zero_extent:
                        assert authored(after)==authored(before) and await H.history(page)==before_history
                        passed(label+' scale '+axis+' grabs the intended handle; a face with zero extent on that axis remains unchanged without adding history',target=target)
                        continue
                    assert authored(after)!=authored(before),('Native geometry did not change',tool,axis,target,active)
                    assert (await H.history(page))['undo']==before_history['undo']+1
                    await undo(page)
                    restored=await H.source(page)
                    for _ in range(20):
                        if authored(restored)==authored(before):
                            break
                        await page.wait_for_timeout(100)
                        restored=await H.source(page)
                    if authored(restored)!=authored(before):
                        result['undoDiagnostic']={'before':before,'after':after,'restored':restored,'historyBefore':before_history,'historyAfterUndo':await H.history(page),'pointerLockedAfterUndo':await page.evaluate('()=>!!document.pointerLockElement'),'target':target,'active':active}
                        print('UNDO_DIAGNOSTIC '+json.dumps(result['undoDiagnostic']),flush=True)
                    assert authored(restored)==authored(before),('Native Undo failed exact geometry restoration',label,tool,axis)
                    passed(label+' '+tool+' '+axis+' accepts '+('padded touch' if mobile else 'mouse')+' drag and one-step Undo with exact geometry restoration',target=target)
            await page.screenshot(path=str(directory/(label+'-handles.png')))
        if mobile:
            await stage('Cancel pending object drag')
            await inspector(page,True)
            await H.manual(page)
            await H.click_visible(page.locator('[data-component-mode="mesh"]'))
            await prepare_view(page)
            await mode_ui(page,'move')
            before=await H.source(page);before_history=await H.history(page)
            target=await handle_target(page,'x',offset=mobile)
            active=await gesture(page,session,target,mobile,cancel=True)
            assert active.get('dragging') and await H.source(page)==before and await H.history(page)==before_history
            passed('Cancel restores a pending native object drag without source/history mutation')
        else:
            # Escape is browser-owned during desktop pointer lock. This scoped
            # handle test verifies picking/edits/Undo; it does not certify that
            # existing browser gesture as a native cancellation command.
            result['desktopEscapeCancel']='NOT_VERIFIED_UNDER_POINTER_LOCK'
        assert not errors,errors
        result['status']='PASS'
        return result
    except Exception as error:
        result['status']='FAIL';result['error']=str(error)
        try:
            result['gizmo']=await access(page)
            result['workshop']=await H.workshop(page)
            await page.screenshot(path=str(directory/'failure.png'))
        except Exception:
            pass
        raise
    finally:
        save();await context.close()


async def main():
    async with H.async_playwright() as playwright:
        browser=await playwright.chromium.launch(executable_path=ARGS.chromium,headless=True,args=['--no-sandbox','--disable-dev-shm-usage','--enable-webgl','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader'])
        try:
            results=[]
            for mode in H.MODES:
                results.append(await run_mode(browser,mode))
            result={'status':'PASS','version':'v11.431','testedHtmlSha256':SHA,'runtime':'real native Model Studio with actual browser mouse/touch input','results':results,'physicalDeviceAcceptance':False}
            (OUT/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
            print(json.dumps({'status':'PASS','checks':sum(len(r['checks']) for r in results),'sha256':SHA,'output':str(OUT)},indent=2),flush=True)
        finally:
            await browser.close()


if __name__=='__main__':
    asyncio.run(main())
