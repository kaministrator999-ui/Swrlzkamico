#!/usr/bin/env python3
"""Narrow, read-only source-backed browser diagnosis of Smooth Cliff Hand materials."""
import argparse,asyncio,json,hashlib,base64
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import urlsplit
from playwright.async_api import async_playwright

a=argparse.ArgumentParser();a.add_argument("--package",required=True);a.add_argument("--chromium");a.add_argument("--block-atlas",action="store_true");args=a.parse_args()
root=Path(args.package).resolve()
origin="https://kamiloki-swrlz-forge-moba.static.hf.space"
atlas_requests=[]
async def handle(route):
    u=urlsplit(route.request.url)
    if u.scheme+'://'+u.netloc==origin:
        p=u.path.lstrip('/') or 'index.html'
        if p=='modeler.html':p='modeler.html'
        if p=='assets/cliff-hand/cliff_pbr_atlas_384.jpg':
            atlas_requests.append(route.request.url)
            if args.block_atlas:return await route.fulfill(status=404,body='Deliberate offline atlas block')
        file=(root/p).resolve()
        if not file.is_relative_to(root) or not file.is_file():
            return await route.fulfill(status=404,body="missing:"+p)
        if p=='modeler.html':
            html=file.read_text('utf8')
            needle='status:()=>({active:!!model(),open:!!panel&&!panel.hidden,count:model()?.parts?.length||0,selected:selection})'
            extra="""status:()=>({active:!!model(),open:!!panel&&!panel.hidden,count:model()?.parts?.length||0,selected:selection,
              liveMeshes:modelRoot?.children?.filter(o=>o.isMesh).map(o=>{
                const m=o.material,g=o.geometry;
                const texture=t=>t?({channel:t.channel,ready:!!t.image,imageWidth:t.image?.width,
                  kind:t.constructor.name,version:t.version}):null;
                const a=n=>g.getAttribute(n);
                return {name:o.name,kind:o.type,visible:o.visible,
                  materialType:m?.type,materialName:m?.name,color:m?.color?.getHexString(),
                  map:texture(m?.map),normal:texture(m?.normalMap),ao:texture(m?.aoMap),
                  roughness:texture(m?.roughnessMap),wireframe:m?.wireframe,
                  opaque:m?.opacity,vertexColors:m?.vertexColors,needsUpdate:m?.version,
                  uv:a('uv')?.count,uv1:a('uv1')?.count,uv2:a('uv2')?.count,
                  position:a('position')?.count,meshUserData:o.userData,worldVisible:o.visible,
                  uvCoverage:(()=>{
                    const uv=a('uv'),c=m?.map?.image,ctx=c?.getContext?.('2d');
                    if(!uv)return null;
                    const pixels=ctx?.getImageData?.(0,0,c.width,c.height)?.data;
                    let uMin=Infinity,vMin=Infinity,uMax=-Infinity,vMax=-Infinity;
                    let dark=0,samples=0;const bins=Array(16).fill(0);
                    let nr=0,ng=0,nb=0;
                    for(let i=0;i<uv.count;i++){
                      const u=uv.getX(i),v=uv.getY(i);
                      uMin=Math.min(uMin,u);uMax=Math.max(uMax,u);
                      vMin=Math.min(vMin,v);vMax=Math.max(vMax,v);
                      const x=Math.max(0,Math.min(3,Math.floor(u*4)));
                      const y=Math.max(0,Math.min(3,Math.floor(v*4)));
                      bins[y*4+x]++;
                      if(pixels){
                        const j=(Math.max(0,Math.min(c.height-1,Math.floor((1-v)*c.height)))*
                          c.width+Math.max(0,Math.min(c.width-1,Math.floor(u*c.width))))*4;
                        nr+=pixels[j];ng+=pixels[j+1];nb+=pixels[j+2];
                        if((pixels[j]+pixels[j+1]+pixels[j+2])/3<100)dark++;
                        samples++;
                      }
                    }
                    return {uMin,vMin,uMax,vMax,bins,samples,dark,meanRGB:[nr/samples,ng/samples,nb/samples]};
                  })()}
              })||[]})"""
            if html.count(needle)!=1:raise RuntimeError('Cannot install read-only Model Atelier mesh inspection')
            return await route.fulfill(body=html.replace(needle,extra,1),content_type='text/html')
        return await route.fulfill(path=str(file))
    return await route.continue_()
async def main():
    async with async_playwright() as p:
        kw={'headless':True,'args':['--no-sandbox','--disable-dev-shm-usage','--enable-webgl','--enable-unsafe-swiftshader']}
        if args.chromium:kw['executable_path']=args.chromium
        browser=await p.chromium.launch(**kw)
        ctx=await browser.new_context(viewport={'width':1280,'height':900})
        await ctx.route(origin+'/**',handle)
        page=await ctx.new_page()
        issues=[]
        page.on('pageerror',lambda e:issues.append('PAGE_ERROR '+str(e)))
        page.on('requestfailed',lambda req:issues.append('REQUEST_FAILED '+req.url+' '+str(req.failure)))
        page.on('console',lambda msg:issues.append('CONSOLE_'+msg.type+' '+msg.text[:500]) if msg.type=='error' else None)
        page.on('response',lambda r:issues.append('HTTP '+str(r.status)+' '+r.url) if r.status>=400 and 'cliff' in r.url else None)
        await page.goto(origin+'/modeler.html',wait_until='domcontentloaded',timeout=90000)
        try:
            await page.wait_for_function("() => !!window.SWYRL_ENGINE_PLAIN_HAND_BASE?.open && !!window.SWYRL_ENGINE_CLIFF_MATERIAL_291",timeout=35000)
        except Exception as error:
            state=await page.evaluate("""() => ({title:document.title,ready:document.readyState,body:document.body?.innerText?.slice(0,500),studio:window.SWYRL_ENGINE_STUDIOS?.active?.(),build:window.SWRLZ_FORGE_BUILD?.version,openType:typeof window.SWYRL_ENGINE_PLAIN_HAND_BASE?.open,material:!!window.SWYRL_ENGINE_CLIFF_MATERIAL_291,canvases:document.querySelectorAll('canvas').length})""")
            print('CLIFF_BROWSER_BOOT_FAILURE='+json.dumps({'state':state,'issues':issues[-35:],'error':str(error)}),flush=True)
            raise
        if await page.locator('#seReleaseNotesDialog[open]').count():
            await page.locator('#seReleaseNotesDialog[open] button').last.click()
        assert not await page.locator('#seReleaseNotesDialog[open]').count(), 'Release notes obscured actual rendered viewport'
        opened=await page.evaluate("() => window.SWYRL_ENGINE_PLAIN_HAND_BASE.open(true)")
        await page.wait_for_timeout(3500)
        detail=await page.evaluate("""() => {
          const state=window.SWYRL_ENGINE_CLIFF_MATERIAL_291.status();
          const native=window.SWYRL_ENGINE_MODEL_ATELIER.status();
          const mat=window.SWYRL_ENGINE_CLIFF_MATERIAL_291.createMaterial({});
          function sample(t){
            const c=t?.image,ctx=c?.getContext?.('2d');
            if(!ctx)return {present:!!t,error:'no-canvas'};
            const d=ctx.getImageData(0,0,c.width,c.height).data;
            let min=255,max=0,s=0,cracks=0,distinct=new Set();
            for(let i=0;i<d.length;i+=4){const v=(d[i]+d[i+1]+d[i+2])/3;
                s+=v;min=Math.min(min,v);max=Math.max(max,v);
                if(v<95)cracks++;if(distinct.size<50)distinct.add(Math.round(v/4));
            }
            return {width:c.width,height:c.height,mean:s/(d.length/4),min,max,
              darkPixels:cracks,levels:distinct.size,center:[...d.slice((192*384+192)*4,(192*384+192)*4+4)]}
          }
          const project=window.SWYRL_ENGINE_AGENT?.inspectScene?.()?.project;
          return {
            engine:window.SWRLZ_FORGE_BUILD?.version,
            scene:{name:project?.name,partCount:project?.modelAtelier?.parts?.length,
               cliffPBR:project?.modelAtelier?.parts?.[0]?.cliffPBR,
               uvCount:project?.modelAtelier?.parts?.[0]?.topologyMesh?.uvs?.length},
            state,native,viewport:window.SWYRL_ENGINE_MODEL_ATELIER?.status(),
            fractures:window.SWYRL_ENGINE_CLIFF_FRACTURES_332?.status(),
            crystals:window.SWYRL_ENGINE_CLIFF_HAND_337?.status(),
            color:sample(mat.map),normal:sample(mat.normalMap),ao:sample(mat.aoMap),
            roughness:sample(mat.roughnessMap),
            map:!!mat.map,aoChannel:mat.aoMap?.channel,material:mat.name,
            viewportFlags:typeof atelierViewStatus==='function'?atelierViewStatus():null
          }
        }""")
        print('CLIFF_BROWSER_INSPECTION='+json.dumps({'opened':opened,'details':detail,'errors':issues},default=str),flush=True)
        viewport=page.locator('#modelAtelierViewport canvas').first
        if await viewport.count():
            png=await viewport.screenshot(type='jpeg',quality=70,timeout=15000)
            print('CLIFF_VIEWPORT_JPEG_BASE64='+base64.b64encode(png).decode('ascii'),flush=True)
        # Rotate the actual WebGL canvas around the hand to see the dorsal
        # crystal texture (the initial camera shows the user's palm).
        if await viewport.count():
            box=await viewport.bounding_box()
            if box:
                y=box['y']+box['height']*.65
                x0=box['x']+box['width']*.72
                x1=max(box['x']+box['width']*.1,x0-365)
                await page.mouse.move(x0,y)
                await page.mouse.down()
                await page.mouse.move(x1,y,steps=14)
                await page.mouse.up()
                await page.wait_for_timeout(650)
                photo=await viewport.screenshot(type='jpeg',quality=74,timeout=15000)
                print('CLIFF_DORSAL_VIEWPORT_JPEG_BASE64='+base64.b64encode(photo).decode('ascii'),flush=True)
        live=detail.get('viewport',{}).get('liveMeshes',[])
        if not opened or len(live)!=1 or not live[0].get('map') or not live[0].get('normal'):
            raise AssertionError('LIVE_CLIFF_MESH_NOT_USING_PBR '+json.dumps(live))
        # Compare a fresh Android-sized WebGL context, not merely desktop metadata.
        mobile=await browser.new_context(viewport={'width':390,'height':844},
            device_scale_factor=2.75,is_mobile=True,has_touch=True,
            user_agent='Mozilla/5.0 (Linux; Android 16; moto g power - 2026) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Mobile Safari/537.36')
        await mobile.route(origin+'/**',handle)
        phone=await mobile.new_page()
        mobile_errors=[]
        phone.on('pageerror',lambda e:mobile_errors.append(str(e)))
        await phone.goto(origin+'/modeler.html',wait_until='domcontentloaded',timeout=90000)
        await phone.wait_for_function("() => !!window.SWYRL_ENGINE_PLAIN_HAND_BASE?.open && !!window.SWYRL_ENGINE_CLIFF_MATERIAL_291",timeout=50000)
        if await phone.locator('#seReleaseNotesDialog[open]').count():
            await phone.locator('#seReleaseNotesDialog[open] button').last.click()
        phone_open=await phone.evaluate("() => window.SWYRL_ENGINE_PLAIN_HAND_BASE.open(true)")
        await phone.wait_for_function("() => window.SWYRL_ENGINE_CLIFF_MATERIAL_291.status().ready===true",timeout=40000)
        await phone.wait_for_timeout(700)
        mobile_detail=await phone.evaluate("""() => ({
            build:window.SWRLZ_FORGE_BUILD?.version,
            model:window.SWYRL_ENGINE_MODEL_ATELIER?.status(),
            texture:window.SWYRL_ENGINE_CLIFF_MATERIAL_291.status(),
            fractures:window.SWYRL_ENGINE_CLIFF_FRACTURES_332?.status(),
            crystals:window.SWYRL_ENGINE_CLIFF_HAND_337?.status(),
            releaseDialogVisible:!!document.querySelector('#seReleaseNotesDialog[open]')
        })""")
        print('CLIFF_ANDROID_BROWSER_INSPECTION='+json.dumps({
            'opened':phone_open,'details':mobile_detail,'errors':mobile_errors},default=str),flush=True)
        if await phone.locator('#modelAtelierViewport canvas').count():
            image=await phone.locator('#modelAtelierViewport canvas').first.screenshot(type='jpeg',quality=70,timeout=20000)
            print('CLIFF_MOBILE_VIEWPORT_JPEG_BASE64='+base64.b64encode(image).decode('ascii'),flush=True)
        if not phone_open or mobile_errors or mobile_detail['texture']['failures']:
            raise AssertionError('Android viewport could not render Smooth Cliff Hand '+str(mobile_detail))
        await mobile.close()
        # External hosting check: whether the actual static Space serves the sealed build.
        for remote in ('https://kamiloki-swrlz-forge-moba.static.hf.space/SOURCE.json',
                       'https://huggingface.co/spaces/kamiloki/swrlz-forge-moba/resolve/main/SOURCE.json',
                       'https://kamiloki-swrlz-forge-moba.static.hf.space/assets/cliff-hand/cliff_pbr_atlas_384.jpg',
                       'https://huggingface.co/spaces/kamiloki/swrlz-forge-moba/resolve/main/assets/cliff-hand/cliff_pbr_atlas_384.jpg'):
            try:
                def get_remote():
                    with urlopen(Request(remote,headers={'Cache-Control':'no-cache','User-Agent':'SwrlzCliffDiagnostics/1.0'}),timeout=20) as response:
                        return response.status,response.headers.get('Cache-Control'),response.read(800000)
                code,cache,content=await asyncio.to_thread(get_remote)
                if remote.endswith('.jpg'):
                    local=(root/'assets/cliff-hand/cliff_pbr_atlas_384.jpg').read_bytes()
                    print('CLIFF_HOSTED_ATLAS='+json.dumps({'url':remote,'status':code,'cacheControl':cache,
                        'bytes':len(content),'sha256':hashlib.sha256(content).hexdigest(),
                        'matchesPackagedAtlas':content==local}),flush=True)
                else:
                    obj=json.loads(content)
                    print('CLIFF_HOSTED_SOURCE='+json.dumps({'url':remote,'status':code,'cacheControl':cache,
                        'version':obj.get('sourceVersion'),'sha256':obj.get('finalSha256'),
                        'bytes':obj.get('finalBytes')}),flush=True)
            except Exception as e:
                print('CLIFF_HOSTED_SOURCE_ERROR='+json.dumps({'url':remote,'error':str(e)[:500]}),flush=True)
        print('CLIFF_ATLAS_HTTP_REQUESTS='+json.dumps({'blockAtlas':args.block_atlas,
            'attempts':len(atlas_requests),'urls':atlas_requests[:4]}),flush=True)
        if args.block_atlas:
            assert not atlas_requests, 'Native cliff material still requires a separate atlas image fetch'
            assert detail['engine']=='v11.337'
            assert detail['state'].get('atlasSource')=='embedded-original-jpeg'
            assert detail['fractures']['passes']>=1
            assert mobile_detail['texture'].get('atlasSource')=='embedded-original-jpeg'
        if not detail.get('crystals') or detail['crystals']['shaderInstalls']<1:
            raise AssertionError('Dorsal-only geode shader was not installed in real WebGL renderer')
        if not mobile_detail.get('crystals') or mobile_detail['crystals']['shaderInstalls']<1:
            raise AssertionError('Dorsal geode shader did not compile on Android-sized WebGL')
        if issues or mobile_errors:
            raise AssertionError('Model Atelier had WebGL shader errors: '+str(issues+mobile_errors))
        await browser.close()
asyncio.run(main())
