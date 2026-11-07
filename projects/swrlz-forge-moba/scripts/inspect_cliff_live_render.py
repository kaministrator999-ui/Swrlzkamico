#!/usr/bin/env python3
"""Narrow, read-only source-backed browser diagnosis of Smooth Cliff Hand materials."""
import argparse,asyncio,json,hashlib
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
        page.on('pageerror',lambda e:issues.append(str(e)))
        page.on('response',lambda r:issues.append('HTTP '+str(r.status)+' '+r.url) if r.status>=400 and 'cliff' in r.url else None)
        await page.goto(origin+'/modeler.html',wait_until='domcontentloaded',timeout=90000)
        await page.wait_for_function("() => typeof createProjectFromTemplate==='function' && !!window.SWYRL_ENGINE_CLIFF_MATERIAL_291",timeout=90000)
        opened=await page.evaluate("() => createProjectFromTemplate('plain-hand-base',true)")
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
          return {
            engine:window.SWRLZ_FORGE_BUILD?.version,opened,
            scene:{name:currentProject?.name,partCount:currentProject?.modelAtelier?.parts?.length,
               cliffPBR:currentProject?.modelAtelier?.parts?.[0]?.cliffPBR,
               uvCount:currentProject?.modelAtelier?.parts?.[0]?.topologyMesh?.uvs?.length},
            state,native,viewport:window.SWYRL_ENGINE_MODEL_ATELIER?.status(),
            color:sample(mat.map),normal:sample(mat.normalMap),ao:sample(mat.aoMap),
            roughness:sample(mat.roughnessMap),
            map:!!mat.map,aoChannel:mat.aoMap?.channel,material:mat.name,
            viewportFlags:typeof atelierViewStatus==='function'?atelierViewStatus():null
          }
        }""")
        print('CLIFF_BROWSER_INSPECTION='+json.dumps({'opened':opened,'details':detail,'errors':issues},default=str),flush=True)
        await browser.close()
asyncio.run(main())
