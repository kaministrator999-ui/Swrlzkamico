#!/usr/bin/env python3
"""Focused real Chromium/native §E acceptance with a controlled Chat transport.

Uses the exact generated HTML passed by --html. Google/backend account flow is
mocked; no claim of live deployment or real-account acceptance. No model code is
executed. Native adapter only receives fixed trusted operation data.
"""
import argparse, hashlib, json, time
from pathlib import Path
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
FORGE='https://kamiloki-swrlz-forge-moba.static.hf.space'
CHAT='https://kamiloki-swyrlz.hf.space'
CDN='https://cdn.jsdelivr.net'
IFRAME='''<!doctype html><meta charset="utf-8"><title>Controlled Chat transport</title><p>Controlled Chat transport; not a Google login test.</p><script>
const protocol='swrlz-forge-chat-v1';let binding=null,port=null,n=0;const pending=new Map();
window.fixture={ready:false,rpc(type,payload={}){return new Promise((resolve,reject)=>{const requestId='fixture-request-'+(++n);pending.set(requestId,{resolve,reject});port.postMessage({protocol,...binding,type,requestId,payload:{...payload,...(type==='host.presence'?binding:{})}});});},batch(payload){port.postMessage({protocol,...binding,type:'host.batch',requestId:'fixture-batch-'+(++n),payload});}};
addEventListener('message',e=>{if(e.source!==parent||e.origin!==''' + json.dumps(FORGE) + '''||e.data.protocol!==protocol)return;const m=e.data;
if(m.type==='host.hello'){binding={hostId:m.hostId,channelId:m.channelId};parent.postMessage({...m,type:'iframe.ready',payload:{}},e.origin);}
if(m.type==='host.connect'&&binding&&m.hostId===binding.hostId&&m.channelId===binding.channelId&&e.ports.length===1){port=e.ports[0];port.onmessage=e=>{const m=e.data;if(m.type==='cloud.list'){port.postMessage({...m,type:'rpc.result',payload:{ok:true,result:{projects:[{id:'owner-a-project',name:'Previous account project',revision:3}]}}});return;}if(m.protocol!==protocol||m.hostId!==binding.hostId||m.channelId!==binding.channelId)return;if(m.type==='rpc.result'){const p=pending.get(m.requestId);if(p){pending.delete(m.requestId);m.payload.ok===false?p.reject(Error(m.payload.error)):p.resolve(m.payload.result);}}};port.start();fixture.ready=true;}}
);</script>'''


def run(html_path,vendor_path,out):
    html=html_path.read_bytes();errors=[];rows=[]
    imports={'/npm/three@0.169.0/+esm':'three-esm.js','/npm/three@0.169.0/examples/jsm/controls/OrbitControls.js/+esm':'orbit-esm.js','/npm/three@0.169.0/examples/jsm/controls/TransformControls.js/+esm':'transform-esm.js'}
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage','--enable-webgl','--enable-unsafe-swiftshader'])
        for mobile in (False,True):
            context=browser.new_context(viewport={'width':412 if mobile else 1440,'height':915 if mobile else 1000},is_mobile=mobile,has_touch=mobile,ignore_https_errors=True)
            batch_state={'context':None,'ops':None,'finished':[],'calls':[],'generation':'generation-native-1'}
            def route(reqroute):
                request=reqroute.request;parsed=urlsplit(request.url)
                cors={'Access-Control-Allow-Origin':FORGE,'Access-Control-Allow-Methods':'POST, OPTIONS','Access-Control-Allow-Headers':'Content-Type, X-Swrlz-Forge-Host','Cache-Control':'no-store'}
                origin=f'{parsed.scheme}://{parsed.netloc}'
                if origin==FORGE:
                    if parsed.path in ('','/','/index.html'):
                        reqroute.fulfill(status=200,content_type='text/html',body=html);return
                    path=(ROOT/parsed.path.lstrip('/')).resolve()
                    if path.is_relative_to(ROOT) and path.is_file():
                        reqroute.fulfill(status=200,path=str(path));return
                    reqroute.fulfill(status=404,body='Missing local fixture');return
                if origin==CDN and parsed.path in imports:
                    reqroute.fulfill(status=200,content_type='text/javascript',headers={'Access-Control-Allow-Origin':'*'},path=str(vendor_path/imports[parsed.path]));return
                if origin==CHAT:
                    if parsed.path in ('','/'):
                        reqroute.fulfill(status=200,content_type='text/html',body=IFRAME);return
                    if parsed.path.startswith('/api/forge/embed/host/'):
                        if request.method=='OPTIONS':reqroute.fulfill(status=204,headers=cors);return
                        body=request.post_data_json;batch_state['calls'].append({'path':parsed.path,'body':body,'hostHeader':request.headers.get('x-swrlz-forge-host')})
                        data={}
                        if parsed.path.endswith('/activate'):
                            assert body['visible'] is True;batch_state['context']=body['context'];batch_state['threadId']=body['threadId'];data={'leaseId':'lease-native','hostToken':'sfh1_CONTROLLED_PARENT_PRIVATE','heartbeatSeconds':5}
                        elif parsed.path.endswith('/take'):
                            assert request.headers.get('x-swrlz-forge-host')=='sfh1_CONTROLLED_PARENT_PRIVATE'
                            data={'batchId':parsed.path.split('/')[-2],'operations':batch_state['ops'],'receiptNonce':'sfr1_CONTROLLED_PRIVATE','preconditions':{'leaseId':'lease-native','projectId':batch_state['context']['projectId'],'threadId':batch_state['threadId'],'generationId':batch_state['generation'],'context':batch_state['context']}}
                        elif parsed.path.endswith('/finish'):
                            batch_state['finished'].append(body);data={'allSucceeded':all(x['ok'] for x in body['results']),'receipts':body['results']}
                        reqroute.fulfill(status=200,content_type='application/json',headers=cors,body=json.dumps(data));return
                reqroute.abort()
            context.route('**/*',route)
            page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
            page.goto(FORGE+'/',wait_until='domcontentloaded',timeout=60000)
            page.wait_for_function("()=>!!window.SWYRL_ENGINE_AGENT&&!!document.getElementById('seChatToggle')",timeout=60000)
            page.wait_for_function("()=>document.documentElement.classList.contains('se127-editor-ready')",timeout=20000)
            page.evaluate("()=>{const d=document.getElementById('seReleaseNotesDialog');if(d?.open)d.close();}")
            # The explicit blank-model template uses real native handlers without
            # disturbing any saved account project or requiring a starter asset.
            page.evaluate("()=>window.SWYRL_ENGINE_AGENT.createProject('blank-model')")
            page.wait_for_function("()=>window.SWYRL_ENGINE_MODEL_ATELIER.status().open",timeout=15000)
            page.locator('#seChatToggle').click()
            page.wait_for_function("()=>!!document.getElementById('seChatFrame')?.contentWindow",timeout=10000)
            deadline=time.monotonic()+15;iframe=None
            while iframe is None and time.monotonic()<deadline:
                iframe=page.frame(url=lambda url:url.startswith(CHAT));page.wait_for_timeout(50)
            assert iframe is not None,{'frames':[f.url for f in page.frames],'element':page.locator('#seChatFrame').evaluate('(e)=>({src:e.src,attribute:e.getAttribute("src"),parentHidden:e.parentNode.hidden})'),'errors':errors}
            iframe.wait_for_function('()=>window.fixture?.ready',timeout=15000)
            metrics=page.evaluate("""()=>{const p=document.getElementById('seChatAccountPanel'),r=p.getBoundingClientRect();return {bodySibling:p.parentNode===document.body,canvasChild:!!p.closest('canvas'),w:r.width,h:r.height,x:r.x,y:r.y,vw:innerWidth,vh:innerHeight,closeFocused:document.activeElement?.id==='seChatClose',sandbox:document.getElementById('seChatFrame').getAttribute('sandbox')}}""")
            assert metrics['bodySibling'] and not metrics['canvasChild'];assert 300<=metrics['w']<=metrics['vw'];assert metrics['h']<=metrics['vh'];assert metrics['closeFocused'];assert 'allow-popups-to-escape-sandbox' in metrics['sandbox']
            page.locator('#seChatRefresh').click()
            page.wait_for_function("()=>!!document.querySelector('#seChatProjects option[value=\"owner-a-project\"]')")
            iframe.evaluate("()=>{void fixture.rpc('host.revoke',{reason:'account-changed'});}")
            page.wait_for_function("()=>document.getElementById('seChatProjects').children.length===0")
            def connect():
                value=iframe.evaluate("()=>fixture.rpc('host.context')")
                result=iframe.evaluate("value=>fixture.rpc('host.presence',{ticket:'sfp1_CONTROLLED',threadId:'thread-native',projectId:value.projectId})",value)
                assert result['leaseId']=='lease-native';return value['context']
            def execute(ops,tag):
                ctx=connect();batch_state['ops']=ops;batch_state['generation']=tag;n=len(batch_state['finished'])
                iframe.evaluate("p=>fixture.batch(p)",{'batchId':tag,'leaseId':'lease-native','generationId':tag})
                deadline=time.monotonic()+15
                while len(batch_state['finished'])==n and time.monotonic()<deadline:page.wait_for_timeout(50)
                assert len(batch_state['finished'])==n+1,(tag,errors,page.locator('#seChatStatus').inner_text())
                receipt=batch_state['finished'][-1];assert all(r['ok'] for r in receipt['results']),(tag,receipt)
                return receipt
            add=execute([{'op':'mesh.add','kind':'box','name':'Exact label §§ 3D Editor','color':'#ff2288','position':[1,2,3],'rotation':[0,.4,0],'scale':[.5,.75,.5]}],'batch-native-add')
            saved=page.evaluate("()=>{const s=window.SWYRL_ENGINE_AGENT.inspectScene();return s.project.modelAtelier.parts.map(p=>({id:p.id,name:p.name,kind:p.kind,color:p.color,position:p.position,scale:p.scale}));}")
            assert len(saved)==2;added=next(x for x in saved if x['id']==add['results'][0]['id']);assert added['name']=='Exact label §§ 3D Editor' and added['position']==[1,2,3] and added['color']=='#ff2288'
            execute([{'op':'editor.undo'}],'batch-native-undo')
            assert page.evaluate("()=>window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier.parts.length")==1
            execute([{'op':'editor.redo'}],'batch-native-redo')
            assert page.evaluate("()=>window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier.parts.length")==2
            # Real scene actor prefab handler, separate from model project scope.
            page.evaluate("()=>document.getElementById('modelAtelierClose').click()")
            scene_add=execute([{'op':'sceneactor.add','prefab':'wall','name':'Literal <b>wall</b> §§','position':[2,1,3]}],'batch-native-scene')
            actor=page.evaluate("id=>window.SWYRL_ENGINE_AGENT.listActors().find(a=>a.id===id)",scene_add['results'][0]['id']);assert actor['name']=='Literal <b>wall</b> §§' and actor['position']==[2,1,3]
            if mobile:
                page.locator('#seChatClose').click()
                # Existing level bar can overlap this legacy button. Invoke its
                # real handler directly to test literal-label presentation only.
                page.locator('#mobileInspectorBtn').evaluate('(e)=>e.click()')
                label=page.locator('#seChatMobileActorLabel');assert label.inner_text()=='Literal <b>wall</b> §§';assert label.locator('b').count()==0
                page.locator('#seChatToggle').click()
            execute([{'op':'editor.undo'}],'batch-native-scene-undo')
            assert page.evaluate("id=>!window.SWYRL_ENGINE_AGENT.listActors().some(a=>a.id===id)",actor['id'])
            # Escape closes the native aside and retires editor authorization.
            closed_before=sum(x['path'].endswith('/close') for x in batch_state['calls'])
            page.locator('#seChatClose').focus();page.keyboard.press('Escape');page.wait_for_timeout(100)
            assert page.locator('#seChatAccountPanel').is_hidden()
            assert page.evaluate("()=>document.activeElement.id")== 'seChatToggle'
            assert sum(x['path'].endswith('/close') for x in batch_state['calls'])>closed_before
            try:iframe.evaluate("()=>fixture.rpc('host.context')");raise AssertionError('hidden editor context leaked')
            except Exception as exc:assert 'EDITOR_PANEL_NOT_VISIBLE' in str(exc)
            image=out.with_name(out.stem+('-mobile' if mobile else '-desktop')+'.png');page.screenshot(path=str(image))
            rows.append({'viewport':'mobile' if mobile else 'desktop','metrics':metrics,'nativeMeshAdded':added,'sceneActorAdded':actor,'nativeUndoRedo':True,'sceneUndoRetainedScope':True,'closedHostDenied':True,'accountProjectListCleared':True,'screenshot':str(image),'pageErrors':list(errors)})
            context.close()
        browser.close()
    receipt={'schema':'swrlz-forge-native-chat-browser-v1','classification':'CONTROLLED_BROWSER_FIXTURE_NOT_LIVE_OR_GOOGLE_ACCEPTANCE','htmlSha256':hashlib.sha256(html).hexdigest(),'htmlBytes':len(html),'results':rows,'passed':True}
    out.write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+'\n');print(json.dumps(receipt,ensure_ascii=False))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--html',type=Path,required=True);ap.add_argument('--vendor',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();run(a.html,a.vendor,a.output)
