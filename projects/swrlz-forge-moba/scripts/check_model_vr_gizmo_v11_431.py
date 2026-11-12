#!/usr/bin/env python3
"""Focused real IWER controller acceptance for accessible transform handles.

A disposable guest cube is manipulated only through controller rays and physical
button/pose samples. The read-only gizmo inspector locates padded targets; it
never executes modeling commands. This verifies software, not headset comfort.
"""
import asyncio
import json
import math
import types
from pathlib import Path

# Reuse the established transport, pinned emulator and controller/UI helpers,
# without invoking its unrelated manual-modeling flow or main().
HELPERS=Path(__file__).with_name('check_model_vr_v11_430.py')
text=HELPERS.read_text().rstrip()+'\n'
assert text.count('version===\"v11.430\"')==1
text=text.replace('version===\"v11.430\"','version===\"v11.431\"')
assert text.endswith('asyncio.run(main())\n')
H=types.ModuleType('vr430_helpers');H.__file__=str(HELPERS)
exec(compile(text.rsplit('\nasyncio.run(main())',1)[0],str(HELPERS),'exec'),H.__dict__)
H.expected_parts[0]['id']='vr431-gizmo-cube'
H.expected_parts[0]['name']='Transform handle practice cube'
H.native_file.write_text(json.dumps(H.public))
OUT=H.out

async def gizmo(page):
    return await page.evaluate('()=>window.SWYRL_ENGINE_MODEL_VR_GIZMO_ACCESS.inspect()')

async def tool(page,mode):
    await H.action_ray(page,mode)
    await page.wait_for_function('(mode)=>window.SWYRL_ENGINE_MODEL_VR_GIZMO_ACCESS.inspect().mode===mode',arg=mode)
    await H.frames(page,4)

async def padded_target(page,mode,axis):
    """Aim just outside the visual mesh, inside its bounded native pick shell."""
    state=await gizmo(page)
    type_name={'move':'ConeGeometry','rotate':'TorusGeometry','scale':'BoxGeometry'}[mode]
    handle=next(h for h in state['handles'] if h['visible'] and h['axis']==axis and h['type']==type_name)
    targets=await page.evaluate('''({handle,mode})=>{
      const T=window.__VR_THREE,m=new T.Matrix4().fromArray(handle.matrixWorld),center=new T.Vector3().setFromMatrixPosition(m);
      const normal=new T.Vector3(0,0,1).transformDirection(m),result=[];
      const points=mode==='move'?[[.028,0,0],[-.028,0,0]]:
        mode==='scale'?[[.038,0,0],[-.038,0,0],[0,.038,0]]:
        [.45,.85,1.25,1.75,2.25,2.75,3.25,3.75,4.25,4.75,5.25,5.75].map(a=>[.168*Math.cos(a),.168*Math.sin(a),0]);
      for(const point of points){const target=new T.Vector3(...point).applyMatrix4(m);
        for(const sign of [1,-1])result.push({target:target.toArray(),origin:target.clone().addScaledVector(normal,.70*sign).toArray()});}
      return result;
    }''',{'handle':handle,'mode':mode})
    for target in targets:
        await H.aim(page,target['target'],origin=target['origin'])
        await H.frames(page,4)
        state=await gizmo(page)
        contact=next(c for c in state['controllers'] if c['hand']=='right')
        if contact['axis']==axis and contact['padded']:
            return target
    raise AssertionError(('Cannot acquire intended padded controller handle',mode,axis,state))

async def move_pose(page,mode,axis):
    await page.evaluate('''({mode,axis,matrix})=>{
      const T=window.__VR_THREE,c=xrTestDevice.controllers.right,m=new T.Matrix4().fromArray(matrix);
      const direction=new T.Vector3(axis==='x'?1:0,axis==='y'?1:0,axis==='z'?1:0).transformDirection(m);
      if(mode==='move'){c.position.x+=direction.x*.10;c.position.y+=direction.y*.10;c.position.z+=direction.z*.10;}
      else if(mode==='scale')c.position.y+=.13;
      else{const delta=new T.Quaternion().setFromAxisAngle(direction,.28),q=new T.Quaternion(c.quaternion.x,c.quaternion.y,c.quaternion.z,c.quaternion.w);q.premultiply(delta);c.quaternion.set(q.x,q.y,q.z,q.w);}
    }''',{'mode':mode,'axis':axis,'matrix':(await gizmo(page))['rootMatrixWorld']})
    await H.frames(page,5)

async def flow(browser,errors,record):
    context,page=await H.open_model(browser,errors,quest=True)
    try:
        original=await H.parts(page)
        await H.enter(page);await H.settle_menu(page)
        await H.aim_part(page,'vr431-gizmo-cube');await H.tap(page,'right','trigger')
        assert (await H.read(page))['selectionIds']==['vr431-gizmo-cube']
        for mode in ('move','rotate','scale'):
            for axis in (('uniform',) if mode=='scale' else ('x','y','z')):
                await tool(page,mode)
                target=await padded_target(page,mode,axis)
                before=await H.parts(page);depth=(await H.read(page))['undoDepth']
                await H.button(page,'right','squeeze',True,4)
                active=(await gizmo(page))['gesture']
                assert active and active['kind']=='group' and active['mode']==mode and active['axis']==axis,(mode,axis,active)
                await move_pose(page,mode,axis)
                assert await H.parts(page)==before,'Pending controller preview must not write saved source'
                await H.button(page,'right','squeeze',False,4)
                after=await H.parts(page)
                assert after!=before,(mode,axis,'Native controller transform did not change source')
                assert (await H.read(page))['undoDepth']==depth+1
                await H.tap(page,'left','y-button')
                assert await H.parts(page)==before and (await H.read(page))['undoDepth']==depth
                record(mode+' '+axis+': padded ray hover and grip agree; native transform commits once and Undo restores source',target=target)
            await H.screenshot_xr(page,mode+'-handles.png')

        await tool(page,'move')
        await padded_target(page,'move','x')
        before=await H.parts(page);depth=(await H.read(page))['undoDepth']
        await H.button(page,'right','squeeze',True,3)
        assert (await gizmo(page))['gesture']['axis']=='x'
        await move_pose(page,'move','x')
        await H.tap(page,'right','b-button')
        await H.button(page,'right','squeeze',False,3)
        assert not (await gizmo(page))['gesture'] and await H.parts(page)==before and (await H.read(page))['undoDepth']==depth
        record('B cancels a padded-handle transform without saving geometry or adding history')

        await tool(page,'rotate')
        await padded_target(page,'rotate','y')
        await H.button(page,'right','squeeze',True,3)
        assert (await gizmo(page))['gesture']['axis']=='y'
        await move_pose(page,'rotate','y')
        await page.evaluate('()=>{xrTestDevice.controllers.right.connected=false;}')
        await H.frames(page,6)
        assert not (await gizmo(page))['gesture'] and await H.parts(page)==before and (await H.read(page))['undoDepth']==depth
        await page.evaluate('()=>{const c=xrTestDevice.controllers.right;c.setButtonValueImmediate("trigger",0);c.setButtonValueImmediate("squeeze",0);c.connected=true;}')
        await page.wait_for_function('()=>window.SWYRL_ENGINE_MODEL_VR.inspect().controllers.filter(c=>c.targetTracked&&c.gripTracked).length===2')
        await H.frames(page,4)
        record('Controller tracking loss cancels a padded-handle preview and restores native source/history')

        await tool(page,'move')
        state=await H.read(page,True)
        target=next(p['center'] for p in state['paletteActions'] if p['action']=='rotate')
        await H.aim(page,target)
        contact=next(c for c in (await gizmo(page))['controllers'] if c['hand']=='right')
        assert contact['axis'] is None
        await H.button(page,'right','squeeze',True,3)
        assert (await gizmo(page))['gesture']['kind']=='menu','A spatial menu must own its grip before geometry handles'
        await H.tap(page,'right','b-button');await H.button(page,'right','squeeze',False,3)
        assert await H.parts(page)==before and (await H.read(page))['undoDepth']==depth
        record('Spatial-menu hover/grip takes priority over transform handles without modifying the model')

        assert await H.parts(page)==original
        await H.action_ray(page,'exit')
        await page.wait_for_function('()=>!window.SWYRL_ENGINE_MODEL_VR.inspect().sessionAttached')
        assert (await H.read(page))['nativeParentRestored']
        assert not errors,errors
        record('XR Exit restores the desktop model root and original native cube with zero page errors')
    except Exception as error:
        try:error.gizmo_state=await gizmo(page)
        except Exception:pass
        try:error.xr_state=await H.read(page,True)
        except Exception:pass
        try:await H.screenshot_xr(page,'failure.png')
        except Exception:pass
        raise
    finally:
        await context.close()

async def main():
    errors=[]
    result={'version':'v11.431','testedHtmlSha256':H.SHA,'runtime':'IWER 2.8.0 / Quest 2 / actual XR renderer and native controller input','iwerSha256':H.IWER_SHA,'physicalHeadsetAcceptance':False,'status':'RUNNING','checks':[],'pageErrors':errors}
    def save():
        (OUT/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
    def record(message,**extra):
        result['checks'].append({'check':message,**extra});save();print('VR431 PASS '+message,flush=True)
    save()
    async with H.async_playwright() as playwright:
        browser=await playwright.chromium.launch(executable_path=H.args.chromium,headless=True,args=['--no-sandbox','--disable-dev-shm-usage','--enable-webgl','--enable-unsafe-swiftshader'])
        try:
            await flow(browser,errors,record);result['status']='PASS';print('MODEL_VR_GIZMO_V11_431_BROWSER_PASS '+json.dumps({'checks':len(result['checks']),'sha256':H.SHA,'output':str(OUT)}),flush=True)
        except Exception as error:
            result['status']='FAIL';result['failure']=type(error).__name__+': '+str(error)
            if hasattr(error,'gizmo_state'):result['gizmo']=error.gizmo_state
            if hasattr(error,'xr_state'):result['xr']=error.xr_state
            print('MODEL_VR_GIZMO_V11_431_BROWSER_FAIL '+result['failure'],flush=True)
            raise
        finally:
            save();await browser.close()

if __name__=='__main__':
    asyncio.run(main())
