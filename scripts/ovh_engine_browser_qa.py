#!/usr/bin/python3
"""Fixed OVH §E browser QA. Run as swrlz-deploy, not root. No network credentials."""
import base64, hashlib, io, json, mimetypes, os, re, socket, sys, tempfile, time, zipfile
from pathlib import Path
from urllib.parse import urlsplit, unquote
from playwright.sync_api import sync_playwright
LIVE=Path('/var/www/swrlz-engine')
SOURCE=Path('/srv/swrlz/source/.deploy')
ORIGIN='https://40.160.61.231'
SCENE='scenes/model-atelier-clean-topology-humanoid-v11-554.swyrl.json'
RUNTIME='swrlz-engine-v11.552.js'
CHROMIUM='/usr/bin/chromium'
def require(cond,msg):
    if not cond:raise RuntimeError(msg)
def sha(data):return hashlib.sha256(data).hexdigest()
def load_file(root,rel):
    path=root/rel
    require(path.resolve().is_relative_to(root.resolve()) and path.is_file(),'Missing/unsafe asset: '+rel)
    require(path.stat().st_size<=16*1024*1024,'Asset too large: '+rel)
    return path.read_bytes()
def main():
    require(os.geteuid()!=0,'Never run browser as root')
    require(len(sys.argv) in (2,3) and sys.argv[1] in ('live','candidate'),'Invalid QA mode')
    mode=sys.argv[1]
    profile=sys.argv[2] if len(sys.argv)==3 else 'mobile'
    require(profile in ('mobile','desktop'),'Invalid browser profile')
    mobile=profile=='mobile'
    viewport={'width':412,'height':915} if mobile else {'width':2560,'height':1440}
    receipt_path=LIVE/'.swrlz-starter-receipt.json'
    if not receipt_path.exists():receipt_path=LIVE/'SOURCE.json'
    live_receipt=json.loads(receipt_path.read_text())
    assets={}
    for rel in ('modeler.html',RUNTIME,SCENE):
        data=load_file(LIVE,rel);record=live_receipt['assets'][rel]
        require(sha(data)==record['sha256'] and len(data)==record['bytes'],'Live receipt mismatch: '+rel)
    if mode=='candidate':
        for name, schema, allowed in (
            ('engine-runtime','swrlz-ovh-runtime-overlay-v1',{'index.html','modeler.html',RUNTIME,'assets/uv-unwrapper/uv_atlas_core_v11_555.mjs','assets/uv-unwrapper/uv_lscm_core_v11_555.mjs'}),
            ('engine-uv','swrlz-engine-uv-overlay-v1',{SCENE,'assets/models/clean-topology-humanoid-v11-554-uv-test.png','assets/models/clean-topology-humanoid-v11-554-uv-guide-2048.png'})):
            root=SOURCE/name/'payload'
            manifest=json.loads((root/'manifest.json').read_text())
            require(manifest['schema']==schema and manifest['target']==str(LIVE),'Bad candidate manifest')
            require(set(manifest['assets'])==allowed,'Unexpected candidate paths')
            for rel,rec in manifest['assets'].items():
                data=load_file(root/'overlay',rel)
                require(sha(data)==rec['sha256'] and len(data)==rec['bytes'],'Candidate integrity mismatch: '+rel)
                assets[rel]=data
    def read(rel):
        return assets[rel] if rel in assets else load_file(LIVE,rel)
    errors=[]; missing=[]; shots={}; served={}; result={'mode':mode,'executionHost':socket.gethostname(),'browserExecutable':CHROMIUM,'origin':ORIGIN,'transport':'server filesystem through isolated browser routes; not authenticated HTTP','accountIntegrationVerified':False,'sandbox':True}
    result.update(profile=profile,viewport=viewport,deviceScaleFactor=1,isMobile=mobile,hasTouch=mobile)
    start=time.monotonic()
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path=CHROMIUM,headless=True,chromium_sandbox=True,proxy={'server':'http://127.0.0.1:9','bypass':''},args=['--proxy-bypass-list=<-loopback>','--disable-dev-shm-usage','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-background-networking'],timeout=20000)
        result['chromiumVersion']=browser.version
        context=browser.new_context(viewport=viewport,screen=viewport,is_mobile=mobile,has_touch=mobile,device_scale_factor=1,service_workers='block',accept_downloads=False)
        context.set_default_timeout(20000)
        def route(r):
            u=urlsplit(r.request.url)
            if u.scheme+'://'+u.netloc!=ORIGIN or r.request.method!='GET':
                r.abort();return
            rel=unquote(u.path).lstrip('/') or 'index.html'
            if not re.fullmatch(r'[A-Za-z0-9_. /§-]+',rel) or '..' in rel.split('/') or rel.startswith('.'):
                r.abort();return
            try:data=read(rel)
            except (OSError,RuntimeError):
                missing.append(rel);r.fulfill(status=404,body='Not found');return
            served[rel]=sha(data)
            mime={'.js':'text/javascript','.mjs':'text/javascript','.glb':'model/gltf-binary'}.get(Path(rel).suffix,mimetypes.guess_type(rel)[0] or 'application/octet-stream')
            r.fulfill(status=200,body=data,headers={'Content-Type':mime,'Cache-Control':'no-store','X-Content-Type-Options':'nosniff'})
        context.route('**/*',route)
        context.route_web_socket('**/*',lambda ws:ws.close())
        page=context.new_page()
        page.on('pageerror',lambda e:errors.append(str(e)[:500]))
        page.on('popup',lambda p:p.close())
        page.on('dialog',lambda d:d.dismiss())
        def shot(name):
            page.wait_for_timeout(250)
            data=page.screenshot(timeout=25000,scale='css')
            require(data[:8]==b'\x89PNG\r\n\x1a\n','Expected PNG screenshot')
            require(int.from_bytes(data[16:20],'big')==viewport['width'] and int.from_bytes(data[20:24],'big')==viewport['height'],'Screenshot resolution mismatch')
            shots[name+'.png']=data
        try:
            nav=page.goto(ORIGIN+'/modeler.html?serverqa=1',wait_until='domcontentloaded',timeout=60000)
            require(nav.status==200 and sha(nav.body())==sha(read('modeler.html')),'Entry mismatch')
            result['browserDisplay']=page.evaluate("()=>({width:innerWidth,height:innerHeight,dpr:devicePixelRatio,screenWidth:screen.width,screenHeight:screen.height,touch:navigator.maxTouchPoints,coarse:matchMedia('(pointer: coarse)').matches,userAgent:navigator.userAgent})")
            if not mobile:
                display=result['browserDisplay']
                require(display['width']==2560 and display['height']==1440 and display['dpr']==1 and display['touch']==0 and not display['coarse'],'Desktop emulation mismatch')
            page.wait_for_function("!!window.SWRLZ_FORGE_BUILD?.version && !!window.SWYRL_ENGINE_UV_UNWRAP && !!window.SWYRL_ENGINE_STARTUP_476?.inspect?.()?.ready",timeout=60000)
            require(page.locator('#seChatFrame').count()==0,'Unexpected credentialed iframe on OVH')
            if page.locator('#se476StartupGate').is_visible():page.locator('#se476ContinueLocal').click()
            page.wait_for_function("document.getElementById('se476StartupGate')?.hidden===true && document.documentElement.classList.contains('se127-editor-ready')",timeout=45000)
            if page.locator('#seReleaseNotesDialog[open]').count():page.locator('#seReleaseNotesClose').click()
            page.evaluate("()=>{document.getElementById('projectHub').classList.add('show');document.getElementById('se236StarterTab-models').click()}")
            card=page.locator('#se236StarterModels button[data-project-template="clean-topology-humanoid"]')
            card.wait_for(state='visible');card.scroll_into_view_if_needed()
            shot('starter-library')
            with page.expect_response(lambda r:r.url.startswith(ORIGIN+'/'+SCENE) and r.status==200,timeout=30000) as response:
                card.click()
            scene_hash=sha(response.value.body())
            require(scene_hash==sha(read(SCENE)),'Starter bytes differ')
            page.wait_for_function("window.SWYRL_ENGINE_CLEAN_TOPOLOGY.status().active===true&&!window.SWYRL_ENGINE_CLEAN_TOPOLOGY.status().busy&&!document.getElementById('projectHub').classList.contains('show')")
            shot('native-starter')
            page.locator('#se355UVEditorOpen').click()
            page.locator('[data-se551="expand"]').click()
            shot('expanded-uv-default')
            page.locator('#se552UVHost [data-se552-regions]').check()
            page.wait_for_function("window.SWYRL_ENGINE_UV_NUMBERING.inspect().labels>=1")
            labels=page.evaluate("window.SWYRL_ENGINE_UV_NUMBERING.inspect()")
            require(labels['enabled'] and labels['model'] and labels['labels']>=1,'UV numbering failed')
            shot('native-uv-numbered')
            page.locator('[data-se556-model]').uncheck()
            page.wait_for_function("window.SWYRL_ENGINE_UV_NUMBERING.inspect().labels===0")
            page.locator('[data-se556-model]').check()
            page.locator('[data-se556-view]').click()
            page.wait_for_function("!document.getElementById('se552UVHost')&&window.SWYRL_ENGINE_UV_NUMBERING.inspect().labels>=1")
            shot('native-numbered-model')
            require(not errors,'Browser errors: '+repr(errors[:5]))
            result.update(ok=True,realStarterCard=True,sceneSha256=scene_hash,labels=labels)
        except Exception as e:
            result.update(ok=False,error=str(e)[:1000])
            try:shot('failure')
            except Exception:pass
        finally:
            context.close();browser.close()
    result.update(errors=errors[:20],missing=missing[:30],served=served,durationMs=round((time.monotonic()-start)*1000),screenshots={k:sha(v) for k,v in shots.items()})
    out=io.BytesIO()
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
        z.writestr('receipt.json',json.dumps(result,indent=2))
        for k,v in shots.items():z.writestr(k,v)
    raw=out.getvalue()
    require(len(raw)<=8*1024*1024,'QA evidence exceeds 8 MiB')
    print('SWRLZ_ENGINE_QA_ZIP '+base64.b64encode(raw).decode(),flush=True)
    return 0 if result['ok'] else 1
if __name__=='__main__':sys.exit(main())
