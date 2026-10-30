#!/usr/bin/env python3
"""Focused native §E mobile viewport geometry, using local controlled assets only."""
import argparse
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
FORGE = 'https://kamiloki-swrlz-forge-moba.static.hf.space'
CDN = 'https://cdn.jsdelivr.net'
METRICS = r'''() => {
const entry=e=>{if(!e)return null;const r=e.getBoundingClientRect(),c=getComputedStyle(e);return {tag:e.tagName,id:e.id,cls:e.className?.baseVal??e.className,x:r.x,y:r.y,w:r.width,h:r.height,display:c.display,position:c.position,height:c.height,minHeight:c.minHeight,maxHeight:c.maxHeight,flex:c.flex,flexDirection:c.flexDirection,gridTemplateRows:c.gridTemplateRows,overflow:c.overflow,visibility:c.visibility,hidden:e.hidden}};
const canvas=document.getElementById('viewport');let e=canvas;const chain=[];while(e){chain.push(entry(e));e=e.parentElement;}
return {viewport:{width:innerWidth,height:innerHeight,dpr:devicePixelRatio,visualHeight:visualViewport?.height,visualWidth:visualViewport?.width},html:entry(document.documentElement),body:entry(document.body),canvas:entry(canvas),drawing:{width:canvas?.width,height:canvas?.height},chain,topbar:entry(document.querySelector('.topbar')),status:entry(document.querySelector('.statusbar')),help:entry(document.querySelector('.help')),tabs:entry(document.querySelector('.mobile-tabs')),badge:entry(document.querySelector('.badgeBox')),stamp:entry(document.querySelector('.build-stamp')),statsPill:entry(document.querySelector('.engine-stats-pill')),chatPanel:entry(document.getElementById('seChatAccountPanel')),levels:entry(document.getElementById('seLevelsBar')||document.getElementById('st141LevelBar')),panels:[...document.querySelectorAll('main,.viewport-wrap,.workspace,.editor')].map(entry),build:window.SWRLZ_FORGE_BUILD,atelier:window.SWYRL_ENGINE_MODEL_ATELIER?.status?.()};
}'''

def run(html_path, vendor, output, strict=False, controls_only=False):
    html = html_path.read_bytes()
    imports = {'/npm/three@0.169.0/+esm':'three-esm.js', '/npm/three@0.169.0/examples/jsm/controls/OrbitControls.js/+esm':'orbit-esm.js', '/npm/three@0.169.0/examples/jsm/controls/TransformControls.js/+esm':'transform-esm.js'}
    rows=[]
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch(executable_path='/usr/bin/chromium', headless=True,args=['--no-sandbox','--disable-dev-shm-usage','--enable-webgl','--enable-unsafe-swiftshader'])
            cases=[(390,740,True)] if controls_only else [(390,740,True),(412,915,True),(980,1850,False)]
            for width,height,mobile in cases:
                context=browser.new_context(viewport={'width':width,'height':height},is_mobile=mobile,has_touch=mobile,ignore_https_errors=True)
                errors=[]
                def route(r):
                    u=urlsplit(r.request.url);origin=f'{u.scheme}://{u.netloc}'
                    if origin==FORGE:
                        if u.path in ('','/','/index.html'):r.fulfill(status=200,content_type='text/html',body=html);return
                        path=(ROOT/u.path.lstrip('/')).resolve()
                        if path.is_relative_to(ROOT) and path.is_file():r.fulfill(status=200,path=str(path));return
                        r.fulfill(status=404,body='No local fixture');return
                    if origin==CDN and u.path in imports:r.fulfill(status=200,content_type='text/javascript',headers={'Access-Control-Allow-Origin':'*'},path=str(vendor/imports[u.path]));return
                    r.abort()
                context.route('**/*',route)
                page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
                page.goto(FORGE+'/',wait_until='domcontentloaded',timeout=60000)
                page.wait_for_function("()=>!!window.SWYRL_ENGINE_AGENT && document.documentElement.classList.contains('se127-editor-ready')",timeout=60000)
                page.evaluate("()=>{const d=document.getElementById('seReleaseNotesDialog');if(d?.open)d.close();}")
                page.wait_for_timeout(300)
                stages=[('default',None),('blank-model',"()=>window.SWYRL_ENGINE_AGENT.createProject('blank-model')"),('scene-after-model',"()=>{document.getElementById('modelAtelierClose')?.click();}")]
                if controls_only:stages=stages[:1]
                for name,action in stages:
                    if action:page.evaluate(action);page.wait_for_timeout(150)
                    metrics=page.evaluate(METRICS);name=f'{width}x{height}-'+name
                    image=output.with_name(output.stem+'-'+name+'.png');page.screenshot(path=str(image))
                    row={'case':name,'mobile':mobile,'metrics':metrics,'pageErrors':list(errors),'image':str(image)};rows.append(row)
                    print(json.dumps({'case':name,'viewport':metrics['viewport'],'canvas':metrics['canvas'],'chain':metrics['chain']},ensure_ascii=False),flush=True)
                    if mobile and name.endswith('-default'):
                        # Native touch buttons must be actionable, without synthetic
                        # dispatch through controls obscured by the level toolbar.
                        page.locator('#mobileInspectorBtn').click(timeout=5000)
                        page.wait_for_function("()=>document.getElementById('mobileDrawer').classList.contains('show')")
                        page.locator('#mobileInspectorBtn').click(timeout=5000)
                        page.wait_for_function("()=>!document.getElementById('mobileDrawer').classList.contains('show')")
                        row['nativeInspectorActionable']=True
                        page.locator('#mobileInspectorBtn').tap(timeout=15000)
                        page.wait_for_function("()=>document.getElementById('mobileDrawer').classList.contains('show')")
                        page.locator('#mobileInspectorBtn').tap(timeout=15000)
                        page.wait_for_function("()=>!document.getElementById('mobileDrawer').classList.contains('show')")
                        row['nativeInspectorTouchActionable']=True
                        # This is a CSS-state compatibility check only: no match,
                        # simulation or extra render loop is started.
                        runtime=page.evaluate("()=>{document.body.classList.add('se145-runtime');try{return ("+METRICS+")();}finally{document.body.classList.remove('se145-runtime');}}")
                        runtime_host=runtime['chain'][1]
                        assert runtime_host['position']=='fixed',runtime_host
                        assert abs(runtime_host['h']-runtime['viewport']['height'])<2,runtime_host
                        assert abs(runtime['canvas']['h']-runtime['viewport']['height'])<2,runtime['canvas']
                        row['runtimeCssCompatibility']={'host':runtime_host,'canvas':runtime['canvas'],'noGameStarted':True}
                        page.wait_for_timeout(100)
                        restored=page.evaluate(METRICS)
                        assert abs(restored['canvas']['h']-restored['chain'][2]['h'])<2,restored
                        page.locator('#seChatToggle').click()
                        chat_metrics=page.evaluate(METRICS)
                        assert chat_metrics['chatPanel']['y']>=47.5,chat_metrics['chatPanel']
                        assert chat_metrics['chatPanel']['y']+chat_metrics['chatPanel']['h']<=height+1,chat_metrics['chatPanel']
                        row['chatHeaderClearance']=chat_metrics['chatPanel']
                        page.locator('#seChatClose').click()
                        assert page.locator('#seChatAccountPanel').is_hidden()
                if mobile and not controls_only:
                    page.set_viewport_size({'width':height,'height':width});page.wait_for_timeout(250)
                    metrics=page.evaluate(METRICS);rows.append({'case':f'{width}x{height}-landscape','mobile':True,'metrics':metrics,'pageErrors':list(errors)})
                context.close()
            browser.close()
    except Exception as exc:
        output.write_text(json.dumps({'schema':'swrlz-mobile-native-viewport-v1','htmlBytes':len(html),'htmlSha256':hashlib.sha256(html).hexdigest(),'results':rows,'passed':False,'failure':str(exc)[:6000],'classification':'CONTROLLED_NATIVE_BROWSER_NOT_REAL_DEVICE_ACCEPTANCE'},indent=2,ensure_ascii=False)+'\n')
        raise
    findings=[]
    for row in rows:
        m=row['metrics'];vh=m['viewport']['height'];canvas=m['canvas']
        workspace=next((node for node in m['chain'] if node.get('cls')=='workspace'),None)
        if canvas and canvas['h']<vh*.5:findings.append({'case':row['case'],'issue':'canvas-less-than-half-viewport','canvasHeight':canvas['h'],'viewportHeight':vh})
        if canvas and workspace and abs(canvas['h']-workspace['h'])>2:findings.append({'case':row['case'],'issue':'canvas-does-not-fill-native-workspace','canvasHeight':canvas['h'],'workspaceHeight':workspace['h']})
        if row['pageErrors']:findings.append({'case':row['case'],'issue':'native-page-errors','errors':row['pageErrors']})
        narrow=m['viewport']['width']<=620
        if narrow and m.get('tabs') and m.get('levels') and m['levels']['h']>0 and m['tabs']['y']<m['levels']['y']+m['levels']['h']+7:findings.append({'case':row['case'],'issue':'mobile-tabs-overlap-level-toolbar','tabs':m['tabs'],'levels':m['levels']})
        if narrow and m.get('badge') and m['badge']['h']>0 and m.get('tabs') and m['badge']['y']<m['tabs']['y']+m['tabs']['h']:findings.append({'case':row['case'],'issue':'selection-badge-overlaps-mobile-tabs','badge':m['badge'],'tabs':m['tabs']})
        for key in ('help','stamp','statsPill'):
            if narrow and m.get(key) and m[key]['display']!='none':findings.append({'case':row['case'],'issue':'desktop-overlay-visible-on-phone','overlay':key,'metrics':m[key]})
        if narrow and canvas and m.get('levels') and m['levels']['h']>canvas['h']*.3:findings.append({'case':row['case'],'issue':'level-controls-cover-most-view','controlsHeight':m['levels']['h'],'canvasHeight':canvas['h']})
    receipt={'schema':'swrlz-mobile-native-viewport-v1','htmlBytes':len(html),'htmlSha256':hashlib.sha256(html).hexdigest(),'results':rows,'findings':findings,'passed':not findings,'classification':'CONTROLLED_NATIVE_BROWSER_NOT_REAL_DEVICE_ACCEPTANCE'}
    output.write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+'\n')
    if strict:assert not findings,findings

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--html',type=Path,required=True);p.add_argument('--vendor',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--assert-layout',action='store_true');p.add_argument('--controls-only',action='store_true',help='One390px native phone case for focused pointer/control revalidation');a=p.parse_args();run(a.html,a.vendor,a.output,a.assert_layout,a.controls_only)
