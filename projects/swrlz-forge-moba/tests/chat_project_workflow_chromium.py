#!/usr/bin/env python3
"""Actual native project workflow; controlled Chat transport, no Google acceptance."""
import argparse, hashlib, json, time
from pathlib import Path
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright
from chat_account_panel_chromium import ROOT, FORGE, CHAT, CDN, IFRAME


def run(html_path,vendor,out):
    raw=html_path.read_bytes();rows=[]
    imports={'/npm/three@0.169.0/+esm':'three-esm.js','/npm/three@0.169.0/examples/jsm/controls/OrbitControls.js/+esm':'orbit-esm.js','/npm/three@0.169.0/examples/jsm/controls/TransformControls.js/+esm':'transform-esm.js'}
    with sync_playwright() as playwright:
        browser=playwright.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage','--enable-webgl','--enable-unsafe-swiftshader'])
        for mobile in (False,True):
            errors=[];handshake_retries=0;state={'finished':[],'calls':[],'ops':[],'context':None,'generation':'test'}
            context=browser.new_context(viewport={'width':412 if mobile else 1440,'height':915 if mobile else 1000},has_touch=mobile,is_mobile=mobile,ignore_https_errors=True)
            def route(control):
                request=control.request;url=urlsplit(request.url);origin=f'{url.scheme}://{url.netloc}'
                if origin==FORGE:
                    if url.path in ('','/','/index.html'):control.fulfill(status=200,content_type='text/html',body=raw);return
                    path=(ROOT/url.path.lstrip('/')).resolve()
                    if path.is_relative_to(ROOT) and path.is_file():control.fulfill(status=200,path=str(path));return
                    control.fulfill(status=404,body='Missing fixture');return
                if origin==CDN and url.path in imports:control.fulfill(status=200,content_type='text/javascript',headers={'Access-Control-Allow-Origin':'*'},path=str(vendor/imports[url.path]));return
                if origin==CHAT:
                    if url.path in ('','/'):control.fulfill(status=200,content_type='text/html',body=IFRAME);return
                    if url.path.startswith('/api/forge/embed/host/'):
                        cors={'Access-Control-Allow-Origin':FORGE,'Access-Control-Allow-Methods':'POST, OPTIONS','Access-Control-Allow-Headers':'Content-Type, X-Swrlz-Forge-Host'}
                        if request.method=='OPTIONS':control.fulfill(status=204,headers=cors);return
                        body=request.post_data_json;state['calls'].append({'path':url.path,'body':body});data={}
                        if url.path.endswith('/activate'):
                            state['context']=body['context'];state['threadId']=body['threadId'];data={'leaseId':'lease-project','hostToken':'sfh1_CONTROLLED_PROJECT','heartbeatSeconds':5}
                        elif url.path.endswith('/take'):
                            data={'operations':state['ops'],'receiptNonce':'sfr1_CONTROLLED_PROJECT','preconditions':{'leaseId':'lease-project','projectId':state['context']['projectId'],'threadId':state['threadId'],'generationId':state['generation'],'context':state['context']}}
                        elif url.path.endswith('/finish'):
                            state['finished'].append(body);data={'allSucceeded':all(row['ok'] for row in body['results'])}
                        control.fulfill(status=200,content_type='application/json',headers=cors,body=json.dumps(data));return
                control.abort()
            context.route('**/*',route);page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
            page.goto(FORGE+'/',wait_until='domcontentloaded',timeout=60000)
            page.wait_for_function("()=>!!window.SWYRL_ENGINE_AGENT&&document.documentElement.classList.contains('se127-editor-ready')",timeout=60000)
            page.evaluate("()=>{const d=document.getElementById('seReleaseNotesDialog');if(d?.open)d.close();}")
            page.locator('#seChatToggle').click();page.wait_for_function("()=>!!document.getElementById('seChatFrame')?.src")
            iframe=None;deadline=time.monotonic()+15
            while iframe is None and time.monotonic()<deadline:iframe=page.frame(url=lambda x:x.startswith(CHAT));page.wait_for_timeout(50)
            assert iframe;iframe.wait_for_function('()=>fixture.ready',timeout=15000)
            def inspect():return iframe.evaluate("()=>fixture.rpc('host.context')")['context']
            def connect():
                nonlocal handshake_retries
                # Native template helpers can settle queued viewport/selection
                # state after creation. A changed snapshot is correctly denied;
                # only gather a fresh binding, never reuse a rejected one.
                for attempt in range(3):
                    value=iframe.evaluate("()=>fixture.rpc('host.context')")
                    try:
                        iframe.evaluate("x=>fixture.rpc('host.presence',{ticket:'sfp1_CONTROLLED_PROJECT',threadId:'thread-project',projectId:x.projectId})",value);return value['context']
                    except Exception as exc:
                        if 'EDITOR_CONTEXT_CHANGED' not in str(exc) or attempt==2:raise
                        handshake_retries+=1;page.wait_for_timeout(100)
            def execute(ops,tag,success=True,reconnect=True):
                before=connect() if reconnect else state['context'];state['ops']=ops;state['generation']=tag;n=len(state['finished'])
                iframe.evaluate('payload=>fixture.batch(payload)',{'batchId':tag,'leaseId':'lease-project','generationId':tag})
                deadline=time.monotonic()+20
                while len(state['finished'])==n and time.monotonic()<deadline:page.wait_for_timeout(50)
                assert len(state['finished'])==n+1,(tag,page.locator('#seChatStatus').inner_text(),errors)
                receipt=state['finished'][-1]
                assert all(x['ok'] for x in receipt['results']) is success,(tag,receipt)
                page.wait_for_timeout(80);return before,receipt
            before=inspect();assert len(before['starters'])==11 and before['project']['name']
            name='My literal §§ <b>model</b>'
            old,result=execute([{'op':'project.create','starterId':'blank-model','name':name}],'create-first')
            created=inspect();first_id=created['projectId'];assert first_id!=old['projectId'];assert created['project']['name']==name;assert created['workspace']=='model-atelier' and created['totalMeshes']==1
            assert created['project']['sourceStarterId']=='blank-model';assert result['results'][0]['localSaved'] is True
            assert page.locator('#se175ActiveProject').inner_text().startswith('Active project · '+name);assert page.locator('#se175ActiveProject b').count()==0
            created_image=out.with_name(out.stem+('-created-mobile' if mobile else '-created-desktop')+'.png');page.screenshot(path=str(created_image))
            calls=state['calls'];finish_index=next(i for i,x in enumerate(calls) if '/create-first/finish' in x['path']);assert any(x['path'].endswith('/close') for x in calls[finish_index+1:]),'old lease must retire after receipt'
            native=page.evaluate('()=>SWYRL_ENGINE_AGENT.inspectScene()');assert native['project']['instanceId']==first_id and native['project']['levelPack']['root']=='project-'+first_id
            _,added=execute([{'op':'mesh.add','kind':'box','name':'Owned addition'}],'add-first')
            assert inspect()['totalMeshes']==2
            page.wait_for_timeout(600)
            saved=page.evaluate("""id=>new Promise((resolve,reject)=>{const q=indexedDB.open('swyrl-engine-projects-v1',2);q.onsuccess=()=>{const db=q.result,r=db.transaction('projects').objectStore('projects').get(id);r.onsuccess=()=>{resolve(r.result);db.close();};r.onerror=reject;};q.onerror=reject;})""",first_id)
            assert len(saved['data']['project']['modelAtelier']['parts'])==2,'native mesh edits must autosave full project'
            _,second=execute([{'op':'project.create','starterId':'blank-model','name':'Second independent model'}],'create-second')
            next_ctx=inspect();assert next_ctx['projectId']!=first_id and next_ctx['totalMeshes']==1,'starter must not inherit owned edits'
            second_id=next_ctx['projectId']
            # Same typed create is forbidden when mixed with edits.
            _,mixed=execute([{'op':'project.create','starterId':'blank-model','name':'Bad mixed'},{'op':'mesh.add','kind':'box'}],'mixed-denied',False)
            assert inspect()['projectId']==second_id
            # Actual storage failure stops before replacing the current editor.
            page.evaluate("()=>{window.fixtureIdbOpen=indexedDB.open;indexedDB.open=()=>{throw Error('CONTROLLED_STORAGE_FAILURE')};}")
            _,failed=execute([{'op':'project.create','starterId':'blank-model','name':'Must not open'}],'storage-denied',False)
            page.evaluate("()=>{indexedDB.open=window.fixtureIdbOpen;delete window.fixtureIdbOpen;}")
            assert inspect()['projectId']==second_id and inspect()['project']['name']=='Second independent model'
            if not mobile:
                # A failed new-project commit rolls back the native editor,
                # including its dirty/history state, after the builder ran.
                baseline=inspect()
                page.wait_for_timeout(600)
                page.evaluate("()=>{window.fixtureIdbOpen=indexedDB.open;let n=0;indexedDB.open=function(...args){if(++n===2)throw Error('CONTROLLED_NEW_COMMIT_FAILURE');return fixtureIdbOpen.apply(this,args);};}")
                _,rollback=execute([{'op':'project.create','starterId':'blank-model','name':'Must roll back'}],'new-save-denied',False)
                page.evaluate("()=>{indexedDB.open=window.fixtureIdbOpen;delete window.fixtureIdbOpen;}")
                rolled=inspect();assert rolled['projectId']==baseline['projectId'] and rolled['project']==baseline['project'] and rolled['dirty']==baseline['dirty'] and rolled['canUndo']==baseline['canUndo']
            # Existing native My Projects picker reopens the first owned copy.
            page.locator('#seChatClose').click();page.evaluate('()=>SWYRL_ENGINE_AGENT.openProjects()');page.locator('#se170-tab-mine').click()
            page.wait_for_function("id=>!!document.querySelector('#se175LocalProjectList option[value=\"'+id+'\"]')",arg=first_id)
            page.locator('#se175LocalProjectList').select_option(first_id);page.locator('#se175LoadLocal').click()
            page.wait_for_function("id=>SWYRL_ENGINE_AGENT.project().instanceId===id",arg=first_id)
            assert not page.locator('#projectHub').evaluate("el=>el.classList.contains('show')")
            page.locator('#seChatToggle').click();restored=inspect();assert restored['projectId']==first_id and restored['totalMeshes']==2 and restored['project']['name']==name
            # Stale native snapshot cannot mutate an edited/switching project.
            stale=connect();page.evaluate("()=>SWYRL_ENGINE_AGENT.spawn('wall',{name:'Manual scene edit'})")
            _,denied=execute([{'op':'mesh.add','kind':'box','name':'Stale must not apply'}],'stale-denied',False,False)
            assert inspect()['totalMeshes']==2
            # Basic blank scene supports a visible new scene and follow-up edit.
            _,scene=execute([{'op':'project.create','starterId':'blank-scene','name':'My new scene'}],'create-scene')
            scene_context=inspect();assert scene_context['workspace']=='scene' and scene_context['totalActors']==0 and scene_context['project']['name']=='My new scene'
            _,wall=execute([{'op':'sceneactor.add','prefab':'wall','name':'Scene first wall'}],'edit-scene')
            assert inspect()['totalActors']==1
            # A nonblank authored native starter keeps its scene and levels
            # while gaining an independent project identity. No game is started.
            _,den=execute([{'op':'project.create','starterId':'glitch-dragons-den','name':'My authored den'}],'create-authored-den')
            den_context=inspect();den_native=page.evaluate('()=>SWYRL_ENGINE_AGENT.inspectScene()')
            assert den_context['totalActors']>=60 and den_context['project']['name']=='My authored den'
            assert den_native['project']['sourceStarterId']=='glitch-dragons-den' and den_native['project']['canonicalId']=='embervault-atelier'
            assert den_native['project']['levelPack']['root']=='project-'+den_context['projectId'] and len(den_native['project']['levelPack']['levels'])>=1
            assert all(row['data']['project']['instanceId']==den_context['projectId'] for row in den_native['project']['levelPack']['levels'])
            den_image=out.with_name(out.stem+('-den-mobile' if mobile else '-den-desktop')+'.png');page.screenshot(path=str(den_image))
            # Workspace code/document drafts belong to each independent copy.
            # Legacy canonical drafts must not hydrate a newly created starter.
            station_actor=next(row for row in den_native['scene']['actors'] if (row.get('workspace') or {}).get('kind')=='code')
            station_id=station_actor['id'];pristine=den_native['project']['workspaces']['stations'][station_id]['files'][0]['content']
            page.locator('#seChatClose').click();page.evaluate('id=>SWYRL_ENGINE_AGENT.openWorkspace(id)',station_id)
            page.locator('#workspaceText').fill('ONLY OWNED COPY A §§');page.wait_for_timeout(600);page.locator('#workspacePanelClose').click()
            own_key='swyrl.workspace.v1:'+den_context['projectId']+':'+station_id
            owned_cache=page.evaluate('key=>JSON.parse(localStorage.getItem(key))',own_key);assert owned_cache['station']['files'][0]['content']=='ONLY OWNED COPY A §§'
            page.evaluate("""row=>{const station=structuredClone(row.station);station.updatedAt=Date.now()+1000000;station.files[0].content='LEGACY TEMPLATE DRAFT MUST NOT LEAK';localStorage.setItem('swyrl.workspace.v1:embervault-atelier:'+encodeURIComponent(row.id),JSON.stringify({schema:'swyrl-workspace-local-v1',station}));}""",{'id':station_id,'station':owned_cache['station']})
            page.locator('#seChatToggle').click()
            _,den_b=execute([{'op':'project.create','starterId':'glitch-dragons-den','name':'My second authored den'}],'create-authored-den-b')
            den_b_context=inspect();den_b_native=page.evaluate('()=>SWYRL_ENGINE_AGENT.inspectScene()')
            assert den_b_context['projectId']!=den_context['projectId']
            assert den_b_native['project']['workspaces']['stations'][station_id]['files'][0]['content']==pristine,'copy B must use starter source, never copy A or legacy canonical drafts'
            assert page.evaluate('key=>JSON.parse(localStorage.getItem(key)).station.files[0].content',own_key)=='ONLY OWNED COPY A §§'
            page.locator('#seChatClose').click();page.evaluate('()=>SWYRL_ENGINE_AGENT.openProjects()');page.locator('#se170-tab-mine').click()
            page.wait_for_function("id=>!!document.querySelector('#se175LocalProjectList option[value=\"'+id+'\"]')",arg=den_context['projectId'])
            page.locator('#se175LocalProjectList').select_option(den_context['projectId']);page.locator('#se175LoadLocal').click()
            page.wait_for_function("id=>SWYRL_ENGINE_AGENT.project().instanceId===id",arg=den_context['projectId'])
            recovered_den=page.evaluate('()=>SWYRL_ENGINE_AGENT.inspectScene()');assert recovered_den['project']['workspaces']['stations'][station_id]['files'][0]['content']=='ONLY OWNED COPY A §§'
            page.locator('#seChatToggle').click()
            # A normal user-selected starter changes project context immediately.
            page.evaluate("()=>SWYRL_ENGINE_AGENT.createProject('blank-model')")
            manual=inspect();assert manual['projectId']!=scene_context['projectId'] and manual['totalMeshes']==1 and manual['project']['name']=='Untitled Model' and manual['project']['sourceStarterId']==''
            assert not errors,errors
            image=out.with_name(out.stem+('-mobile' if mobile else '-desktop')+'.png');page.screenshot(path=str(image))
            rows.append({'mobile':mobile,'projectCreated':created,'secondProjectId':second_id,'localReloadId':restored['projectId'],'literalNamePreserved':True,'starterUnchanged':True,'nativeEditAutosave':True,'previousProjectRecoverable':True,'storageFailurePreservedWorkspace':True,'mixedCreateDenied':True,'staleSnapshotDenied':True,'blankSceneAndFollowupEdit':True,'authoredStarterClone':{'actorCount':den_context['totalActors'],'projectId':den_context['projectId'],'canonicalId':den_native['project']['canonicalId']},'workspaceDocumentsIsolated':True,'legacyDraftNotHydratedIntoCopy':True,'manualStarterContextUpdated':True,'leaseRetiredAfterReceipt':True,'contextHandshakeRetries':handshake_retries,'pageErrors':errors,'image':str(image)})
            context.close()
        browser.close()
    receipt={'schema':'swrlz-native-project-workflow-browser-v1','classification':'CONTROLLED_NATIVE_BROWSER_NOT_REAL_GOOGLE_OR_DEVICE_ACCEPTANCE','htmlBytes':len(raw),'htmlSha256':hashlib.sha256(raw).hexdigest(),'passed':True,'results':rows}
    out.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n');print(json.dumps(receipt,ensure_ascii=False))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--html',type=Path,required=True);parser.add_argument('--vendor',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();run(args.html,args.vendor,args.output)
