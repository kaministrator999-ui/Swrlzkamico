#!/usr/bin/env python3
"""Narrow, read-only source-backed browser diagnosis of Smooth Cliff Hand materials."""
import argparse,asyncio,json,hashlib,base64
from pathlib import Path
from urllib.parse import urlsplit
from playwright.async_api import async_playwright

a=argparse.ArgumentParser();a.add_argument("--package",required=True);a.add_argument("--chromium");args=a.parse_args()
root=Path(args.package).resolve()
origin="https://kamiloki-swrlz-forge-moba.static.hf.space"
async def handle(route):
    u=urlsplit(route.request.url)
    if u.scheme+'://'+u.netloc==origin:
        p=u.path.lstrip('/') or 'index.html'
        if p=='modeler.html':p='modeler.html'
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
        live=detail.get('viewport',{}).get('liveMeshes',[])
        if not opened or len(live)!=1 or not live[0].get('map') or not live[0].get('normal'):
            raise AssertionError('LIVE_CLIFF_MESH_NOT_USING_PBR '+json.dumps(live))
        await browser.close()
asyncio.run(main())
