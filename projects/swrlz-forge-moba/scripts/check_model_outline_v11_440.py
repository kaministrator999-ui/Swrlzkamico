#!/usr/bin/env python3
from pathlib import Path
import os
import types,sys,asyncio,json,hashlib
helper=Path(__file__).with_name('check_model_vr_v11_390.py')
s=helper.read_text().rsplit('\nasyncio.run(main())',1)[0].replace('version===\"v11.390\"','version===\"v11.440\"')
H=types.ModuleType('helpers');H.__file__=str(helper);exec(compile(s,str(helper),'exec'),H.__dict__)
assert os.environ.get('MODEL_TEST_SHA')==hashlib.sha256(H.html.read_bytes()).hexdigest(),'Set MODEL_TEST_SHA to the sealed source digest'
async def main():
 errors=[];result={'sourceSha256':hashlib.sha256(H.html.read_bytes()).hexdigest(),'pageErrors':errors,'physicalQuest':False,'status':'RUNNING'}
 async with H.async_playwright() as p:
  browser=await p.chromium.launch(executable_path=H.args.chromium,headless=True,args=['--no-sandbox','--disable-dev-shm-usage','--enable-webgl','--enable-unsafe-swiftshader'])
  context,page=await H.open_model(browser,errors,quest=True)
  try:
   await H.enter(page);await H.settle_menu(page);await H.ray_find(page,'draw')
   before=await H.parts(page);depth=(await H.read(page))['undoDepth']
   await H.aim(page,[.5,1.25,-1.4],origin=[.5,1.25,-.35]);await H.button(page,'right','trigger',True,3)
   for delta in ([.08,0,0],[0,.08,0],[-.08,0,0],[0,-.08,0]):await H.move_hand(page,delta)
   await H.button(page,'right','trigger',False,4);drawn=await H.parts(page)
   new_id=next(x['id'] for x in drawn if x['id'] not in {x['id'] for x in before});result['createdOutline']=next(x for x in drawn if x['id']==new_id);result['afterDraw']=await H.read(page,True)
   await H.ray_find(page,'extrude');result['afterThickenButton']=await H.read(page,True)
   await H.aim_part(page,new_id);await H.button(page,'right','squeeze',True,4);result['afterGrip']=await H.read(page,True)
   await H.move_hand(page,[0,0,.045]);await H.button(page,'right','squeeze',False,4);result['geometryChanged']=await H.parts(page)!=drawn;result['afterRelease']=await H.read(page,True)
   await H.screenshot_xr(page,'outline-thicken-result.png')
   assert result['geometryChanged'],'Thicken outline did not change geometry; mode='+result['afterGrip']['mode']+' manual='+str(result['afterGrip'].get('manual'))
   assert (await H.read(page))['undoDepth']==depth+2
   result['status']='PASS'
  except Exception as e:result['status']='FAIL';result['failure']=str(e);print('REPRO_FAIL',str(e),flush=True)
  finally:
   (H.out/'outline-repro.json').write_text(json.dumps(result,indent=2)+'\n');await context.close();await browser.close();print(json.dumps({'status':result['status'],'failure':result.get('failure'),'file':str(H.out/'outline-repro.json')},indent=2),flush=True)
if __name__=='__main__':
 asyncio.run(main())
