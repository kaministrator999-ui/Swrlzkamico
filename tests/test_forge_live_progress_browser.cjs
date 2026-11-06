/* Real canonical Chat UI under controlled two-origin transport. No live account/editor.
   Includes EOF before batch readiness, 503 recovery, Stop and account ownership. */
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const ROOT=path.resolve(__dirname,'..');
const CHAT='https://kamiloki-swyrlz.hf.space',FORGE='https://kamiloki-swrlz-forge-moba.static.hf.space';
const protocol='swrlz-forge-chat-v1',hostId='host_01234567890123456789',channelId='chan_01234567890123456789';
const pairId='a'.repeat(32),leaseId='b'.repeat(32),batchId='c'.repeat(32),proposalId='d'.repeat(32);
const token='sfe1_PRIVATE_PROGRESS_BROWSER_FIXTURE',threadId='saved-chat';
const stationSource=fs.readFileSync(path.join(ROOT,'hf_space/station.py'),'utf8');
const adapter=stationSource.match(/^    adapter='([^']*)'/m)?.[1]||'';
const css=stationSource.match(/^    css='([^']*)'/m)?.[1]||'';
const fields={kind:'loft',name:'<img src=x onerror=alert(1)> staff',position:[-.8,0,0],rotation:[0,0,0],scale:[1,1,1],path:[[0,0,0],[.1,1,0],[0,2,0]],radii:[.07,.06,.05],segments:24,color:'#795333'};
const steps=Array.from({length:40},(_,index)=>({index:index+1,op:'mesh.add',name:'Reviewable part '+(index+1),kind:'sphere',position:[0,index/20,0],scale:[.1,.1,.1],color:'#73518f',fields:{kind:'sphere',name:'Reviewable part '+(index+1),position:[0,index/20,0],scale:[.1,.1,.1],color:'#73518f'}}));
steps[0]={index:1,op:'mesh.add',name:fields.name,kind:'loft',position:fields.position,scale:fields.scale,color:fields.color,fields};
steps[1]={index:2,op:'mesh.add',name:'Hood shell',kind:'lathe',position:[0,2,0],scale:[1,1,1],color:'#73518f',fields:{kind:'lathe',name:'Hood shell',position:[0,2,0],scale:[1,1,1],profile:[[.9,-.5],[1,0],[.7,.8],[0,1]],arcStart:.5,arcLength:5.2,segments:32,color:'#73518f'}};
steps[39]={index:40,op:'editor.frame',name:'Final front view',kind:'object',position:[0,0,0],scale:[1,1,1],color:'#73518f',fields:{view:'front'}};
const widget={contract:'swrlz-widget-v1',kind:'forge-design-preview',title:'Review curved character',data:{schema:'swrlz-forge-design-preview-v2',project:'Character',workspace:'model-atelier',operationCount:40,steps,proposalId,planDigest:'e'.repeat(64),expiresAt:Date.now()/1000+900,followup:'Approve §e design preview '+proposalId,notice:'Exact frozen proposal; no editor writes have run.'}};
const parentHtml=`<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><style>body{margin:0}iframe{width:min(480px,100vw);height:100dvh;border:0}</style></head><body><iframe id="chat" src="${CHAT}/?forgeEmbed=1"></iframe><script>
const protocol=${JSON.stringify(protocol)},hostId=${JSON.stringify(hostId)},channelId=${JSON.stringify(channelId)},origin=${JSON.stringify(CHAT)};
const frame=document.getElementById('chat');let port;const pending=new Map();window.received=[];
const send=(type,payload,requestId=crypto.randomUUID())=>port.postMessage({protocol,hostId,channelId,type,payload,requestId});
window.hostProgress=payload=>send('host.progress',payload);
window.parentRPC=(type,payload={})=>new Promise((resolve,reject)=>{const id=crypto.randomUUID();pending.set(id,{resolve,reject});send(type,payload,id);});
window.addEventListener('message',event=>{const m=event.data;if(event.origin!==origin||event.source!==frame.contentWindow||m?.protocol!==protocol||m.hostId!==hostId||m.channelId!==channelId||m.type!=='iframe.ready'||port)return;
const channel=new MessageChannel();port=channel.port1;port.onmessage=event=>{const m=event.data;window.received.push(m);if(m.type==='rpc.result'){const p=pending.get(m.requestId);if(p){pending.delete(m.requestId);m.payload.ok?p.resolve(m.payload.result):p.reject(Error(m.payload.error));}}if(m.type==='host.context')send('rpc.result',{ok:true,result:{projectId:'native-project',context:{mode:'edit',workspace:'model-atelier',epoch:1,meshes:[]}}},m.requestId);if(m.type==='host.presence')send('rpc.result',{ok:true,result:{leaseId:${JSON.stringify(leaseId)}}},m.requestId);};port.start();frame.contentWindow.postMessage({protocol,hostId,channelId,type:'host.connect',requestId:crypto.randomUUID(),payload:{}},origin,[channel.port2]);send('host.visibility',{visible:true});window.hostReady=true;});
frame.onload=()=>frame.contentWindow.postMessage({protocol,hostId,channelId,type:'host.hello',requestId:crypto.randomUUID(),payload:{}},origin);
</script></body></html>`;
async function assertEventually(check,label){
  const deadline=Date.now()+12000;
  while(!check()){if(Date.now()>deadline)assert.fail('Timed out: '+label);await new Promise(resolve=>setTimeout(resolve,40));}
}
(async()=>{
  const module=await import(process.env.PLAYWRIGHT_MODULE||require.resolve('playwright'));
  const {chromium}=module.chromium?module:module.default;
  const browser=await chromium.launch({headless:true,executablePath:process.env.CHROMIUM_PATH||'/usr/bin/chromium',args:['--no-sandbox','--disable-dev-shm-usage']});
  try{for(const viewport of [{width:1440,height:900},{width:390,height:844}]){
    const context=await browser.newContext({viewport,serviceWorkers:'block'}),page=await context.newPage();
    const errors=[];page.on('pageerror',e=>errors.push(e.message));
    let sent=null,active=null,terminal=false,allowBatch=false,streamClosed=false;
    let failures=0,syncAttempts=0,sendCount=0,accountNumber=1,cancelCount=0;
    let holdSync=null,heldSync=null,holdCancel=null,heldCancel=null,holdSend=null,heldSend=null,holdPresence=null,heldPresence=null;
    let wrongTerminal=false,omitActive=false,failNextSend=false;
    const streamedRequests=[];
    const gate=()=>{let release;const promise=new Promise(resolve=>{release=resolve;});return {promise,release};};
    const account=()=>({id:'google:controlled-'+accountNumber,displayName:'Account user '+accountNumber});
    const snapshot=()=>({revision:1,currentThread:{id:threadId},threads:[{id:threadId,title:'Mage '+accountNumber,createdAt:1,messages:[...history,...(wrongTerminal&&sent?[{id:'wrong-terminal',role:'assistant',text:'Unrelated terminal receipt',createdAt:3,meta:{requestId:'unrelated-request',state:'COMPLETE'}}]:[]),...(terminal&&sent?[{id:'final-'+sent.requestId,role:'assistant',text:'Server receipts confirm the actual editor result.',createdAt:4,meta:{requestId:sent.requestId,state:'COMPLETE'}}]:[])]}],activeGeneration:active&&!omitActive?{...active,forgeBatches:allowBatch?active.forgeBatches:[],terminal,terminalType:terminal?'COMPLETE':'',text:terminal?'Server receipts confirm the actual editor result.':'Applying the approved native plan.'}:null});
    const history=[{id:'prior-diagnostic',role:'assistant',text:'Prior editor failure.',createdAt:0,meta:{state:'FAILED',requestId:'prior-failure',progressTrace:{events:[{phase:'FORGE_FAILED',code:'FORGE_PLANNER_FAILED',reason:'Edit could not be verified.'},{phase:'FORGE_FAILED',code:'FORGE_BAD <secret>',reason:'Safe bounded message.'},{phase:'UNRELATED',code:'FORGE_UNRELATED',reason:'Unrelated status.'}]}}},{id:'user',role:'user',text:'Create a character',createdAt:1},{id:'preview',role:'assistant',text:'Review the exact character plan.',createdAt:2,meta:{widgets:[widget]}},{id:'incomplete-preview',role:'assistant',text:'A malformed cached preview.',createdAt:3,meta:{widgets:[{...widget,title:'Incomplete preview',data:{...widget.data,operationCount:41}}]}}];
    await context.route('**/*',async route=>{
      const request=route.request(),url=new URL(request.url()),pathname=decodeURIComponent(url.pathname);
      if(url.origin===FORGE)return route.fulfill({contentType:'text/html',body:parentHtml});
      if(url.origin!==CHAT)return route.fulfill({contentType:url.pathname.endsWith('.css')?'text/css':'application/javascript',body:''});
      if(pathname.startsWith('/api/')){
        const body=request.postDataJSON?.()||null;
        const json=(v,status=200)=>route.fulfill({status,contentType:'application/json',body:JSON.stringify(v)});
        if(pathname==='/api/forge/embed/pair')return json({pairId,loginUrl:'/forge/login?pairId='+pairId,expiresAt:Date.now()/1000+300,recoveryCode:'b'.repeat(12)});
        if(pathname==='/api/forge/embed/pair/'+pairId)return json({approved:true});
        if(pathname==='/api/forge/embed/pair/exchange')return json({token,expiresAt:Date.now()/1000+3600,parentOrigin:FORGE,hostId,channelId,user:account()});
        if(pathname==='/api/account/status')return json({googleClientId:'controlled-fixture'});
        if(request.headers().authorization!=='Bearer '+token)return json({detail:'CONTROLLED_AUTH_REQUIRED'},401);
        if(pathname==='/api/account/me')return json({user:account()});
        if(pathname==='/api/github/status')return json({configured:false,linked:false});
        if(pathname==='/api/lalm_station/sync'){
          const value=snapshot();
          if(holdSync){const pending=holdSync;holdSync=null;heldSync=pending;await pending.promise;}
          if(sent){syncAttempts++;if(failures>0){failures--;return json({detail:'Transient Space restart'},503);}}
          return json(value);
        }
        if(pathname==='/api/forge/embed/presence'){
          if(holdPresence){const pending=holdPresence;holdPresence=null;heldPresence=pending;await pending.promise;}
          return json({ticket:'sfp1_CONTROLLED_TICKET',hostId,channelId,threadId:body.threadId,projectId:body.projectId});
        }
        if(pathname==='/api/lalm_station/send'){
          if(failNextSend){failNextSend=false;return json({detail:'Controlled send rejection'},503);}
          sent=body;sendCount++;failures=2;streamClosed=false;active={requestId:body.requestId,threadId:body.threadId,text:'Applying the approved native plan.',status:[{type:'FORGE_APPLYING',phase:'FORGE_APPLYING'}],terminal:false,lastSeq:1,forgeBatches:[{type:'FORGE_BATCH_READY',batchId,leaseId,threadId:body.threadId,generationId:body.requestId,projectId:'native-project'}]};
          if(holdSend){const pending=holdSend;holdSend=null;heldSend=pending;await pending.promise;}
          return json({requestId:body.requestId});
        }
        if(pathname==='/api/lalm_station/stream'){
          streamedRequests.push(url.searchParams.get('requestId'));
          // A genuine response ends after its initial status, before any ready batch.
          await route.fulfill({contentType:'application/x-ndjson',body:JSON.stringify({type:'QUEUED',requestId:sent.requestId,seq:1})+'\n'});
          streamClosed=true;return;
        }
        if(pathname==='/api/lalm_station/cancel'){
          cancelCount++;
          if(holdCancel){const pending=holdCancel;holdCancel=null;heldCancel=pending;await pending.promise;}
          return json({ok:true});
        }
        return json({ok:true});
      }
      const relative=pathname==='/'?'chat/§wyrlz/index.html':pathname.replace(/^\//,'');
      let filename=path.resolve(ROOT,relative);
      if(!filename.startsWith(ROOT+path.sep))return route.fulfill({status:404,body:''});
      if(!fs.existsSync(filename)&&relative.startsWith('chat/§wyrlz/assets/'))filename=path.resolve(ROOT,'hf_space',relative);
      if(!fs.existsSync(filename))return route.fulfill({status:404,body:''});
      let content=fs.readFileSync(filename);if(relative==='chat/§wyrlz/index.html')content=content.toString().replace('</head>',css+'</head>').replace('</body>',adapter+'</body>');
      return route.fulfill({contentType:{'.html':'text/html','.js':'application/javascript','.css':'text/css','.json':'application/json','.png':'image/png'}[path.extname(filename)]||'application/octet-stream',body:content});
    });
    await page.goto(FORGE+'/',{waitUntil:'domcontentloaded'});await page.waitForFunction(()=>window.hostReady);
    const frame=page.frames().find(f=>f.url().startsWith(CHAT));assert.ok(frame);
    await page.evaluate(()=>window.parentRPC('account.signIn'));
    await frame.waitForFunction(()=>document.getElementById('accountName').textContent==='Account user 1');
    if(await frame.locator('#chatUpdatesDialog[open]').count())await frame.locator('#chatUpdatesClose').click();
    const diagnostic=frame.locator('[data-message-id="prior-diagnostic"] .station-activity');
    await diagnostic.waitFor();
    assert.match(await diagnostic.textContent(),/FORGE_PLANNER_FAILED/,'trusted bounded Forge failure code remains inspectable');
    assert.doesNotMatch(await diagnostic.textContent(),/FORGE_BAD|<secret>|FORGE_UNRELATED/,'invalid and unrelated codes are omitted');
    const preview=frame.locator('.forge-design-preview').filter({hasText:'40 exact native steps'});await preview.waitFor();
    const incomplete=frame.locator('.forge-design-preview').filter({hasText:'The complete plan could not be reviewed'});
    assert.equal(await incomplete.getByRole('button',{name:'Approve exact plan in §E'}).isDisabled(),true,'an incomplete count cannot approve unseen steps');
    assert.match(await preview.locator('.forge-design-proof').textContent(),/40 exact native steps/);
    assert.equal(await preview.locator('.forge-design-step').count(),40,'all steps beyond the legacy16 limit are reviewable');
    const fieldText=await preview.locator('.forge-design-fields').allTextContents();
    assert.deepEqual(JSON.parse(fieldText[0]),fields,'every frozen loft field survives review');
    assert.equal(JSON.parse(fieldText[1]).arcLength,5.2);assert.equal(JSON.parse(fieldText[39]).view,'front');
    assert.equal(await preview.locator('img[src="x"]').count(),0,'model names are literal text');
    assert.ok(await preview.locator('svg polyline').count()>0,'curved preview uses actual bounded path/profile points');
    await preview.getByRole('button',{name:'Approve exact plan in §E'}).click();
    await frame.waitForFunction(()=>!document.getElementById('stopButton').hidden);
    await assertEventually(()=>streamClosed&&failures===0,'EOF and two transient 503 snapshots');
    assert.ok(syncAttempts>=2);
    assert.equal(await page.evaluate(()=>window.received.filter(m=>m.type==='host.batch').length),0,'EOF precedes ready batch');
    assert.equal(await frame.locator('#stopButton').isVisible(),true,'EOF/503 keeps the acknowledged request cancellable');
    assert.equal(await frame.locator('#sendButton').isHidden(),true);
    await frame.locator('#prompt').fill('Must not send a competing request');
    await frame.locator('#prompt').press('Enter');
    assert.equal(sendCount,1,'EOF does not release the send admission guard');
    await frame.locator('#prompt').fill('');
    allowBatch=true;
    await page.waitForFunction(()=>window.received.some(m=>m.type==='host.batch'));
    assert.equal(sent.prompt,'Approve §e design preview '+proposalId,'approval submits only the frozen proposal ID');
    const progress=completed=>({batchId,generationId:sent.requestId,completed,total:40,op:'mesh.add',name:fields.name,ok:true});
    await page.evaluate(v=>window.hostProgress(v),{...progress(1),generationId:'stale-generation'});
    assert.equal(await frame.locator('.forge-native-progress').count(),0,'stale generation is rejected');
    await page.evaluate(v=>window.hostProgress(v),progress(1));
    const panel=frame.locator('.forge-native-progress');await panel.waitFor();
    assert.match(await panel.textContent(),/1 \/ 40/);assert.match(await panel.textContent(),/awaiting server receipts/);
    assert.equal(await panel.getByRole('progressbar').getAttribute('max'),'40');
    assert.equal(await panel.locator('img').count(),0,'live native labels remain literal text');
    await page.evaluate(v=>window.hostProgress(v),progress(40));
    await frame.waitForFunction(()=>document.querySelector('.forge-native-progress progress')?.value===40);
    assert.match(await panel.textContent(),/awaiting server receipts/,'100% native progress does not claim final success');
    holdCancel=gate();const firstCancel=holdCancel;
    await frame.locator('#stopButton').click();
    await assertEventually(()=>heldCancel===firstCancel,'held cancel reached server');
    assert.equal(await frame.locator('#stopButton').isDisabled(),true);
    assert.equal(await frame.locator('#stopButton').isVisible(),true,'pending cancellation stays visible');
    await page.waitForFunction(()=>window.received.some(m=>m.type==='host.revoke'&&m.payload.reason==='generation-cancelled'));
    assert.equal(heldCancel,firstCancel,'host revocation is observed while server cancellation remains pending');
    assert.equal(await panel.count(),1,'Stop keeps transient evidence until the server terminal receipt');
    await page.evaluate(v=>window.hostProgress(v),{...progress(40),name:'unauthorized after Stop'});
    assert.doesNotMatch(await panel.textContent(),/unauthorized after Stop/,'revocation immediately blocks further native updates');
    firstCancel.release();
    await frame.waitForFunction(()=>!document.getElementById('stopButton').disabled);
    assert.equal(await frame.locator('#stopButton').isVisible(),true,'cancel acknowledgement is not a terminal receipt');
    wrongTerminal=true;
    await frame.evaluate(()=>window.dispatchEvent(new Event('focus')));
    await frame.getByText('Unrelated terminal receipt',{exact:true}).waitFor();
    assert.equal(await frame.locator('#stopButton').isVisible(),true,'an unrelated terminal message cannot settle the acknowledged request');
    terminal=true;
    await panel.waitFor({state:'detached',timeout:10000});
    await frame.getByText('Server receipts confirm the actual editor result.',{exact:true}).waitFor();
    await frame.waitForFunction(()=>document.getElementById('stopButton').hidden&&!document.getElementById('sendButton').disabled);
    // A delayed nonterminal snapshot for this same finished request cannot
    // resurrect it or re-forward native work after terminal cleanup.
    terminal=false;
    await frame.evaluate(()=>window.dispatchEvent(new Event('focus')));
    await frame.waitForTimeout(900);
    assert.equal(await frame.locator('#stopButton').isHidden(),true,'terminal evidence is monotonic across delayed snapshots');
    assert.equal(await panel.count(),0);
    terminal=true;

    if(viewport.width===1440){
      // Hold both old-account cancellation and hydration across a real broker
      // re-pair; their eventual cleanup must not own the next account/request.
      active=null;sent=null;terminal=false;allowBatch=false;
      await frame.locator('#prompt').fill('Old account job');await frame.locator('#sendButton').click();
      await assertEventually(()=>streamClosed&&failures===0,'old account stream EOF');
      holdCancel=gate();const oldCancel=holdCancel;
      holdSync=gate();const oldSync=holdSync;
      await frame.evaluate(()=>window.dispatchEvent(new Event('focus')));
      await assertEventually(()=>heldSync===oldSync,'old account snapshot held');
      await frame.locator('#stopButton').click();
      await assertEventually(()=>heldCancel===oldCancel,'old account cancel held');
      accountNumber=2;active=null;sent=null;terminal=false;
      await page.evaluate(()=>window.parentRPC('account.signIn'));
      await frame.waitForFunction(()=>document.getElementById('accountName').textContent==='Account user 2');
      await frame.waitForFunction(()=>document.body.innerText.includes('Mage 2'));
      assert.equal(await frame.locator('#sendButton').isEnabled(),true,'old sync cannot block new account hydration');
      await frame.locator('#prompt').fill('New account job');await frame.locator('#sendButton').click();
      await assertEventually(()=>streamClosed&&failures===0,'new account stream EOF');
      holdCancel=gate();const newCancel=holdCancel;
      await frame.locator('#stopButton').click();
      await assertEventually(()=>heldCancel===newCancel,'new account cancel held');
      oldCancel.release();oldSync.release();
      await frame.waitForTimeout(400);
      assert.equal(await frame.locator('#accountName').textContent(),'Account user 2');
      assert.equal(await frame.locator('#stopButton').isVisible(),true);
      assert.equal(await frame.locator('#stopButton').isDisabled(),true,'old finally cannot release a new cancellation owner');
      assert.equal(await frame.locator('#sendButton').isHidden(),true);
      newCancel.release();terminal=true;omitActive=true;
      await frame.evaluate(()=>window.dispatchEvent(new Event('focus')));
      await frame.waitForFunction(()=>document.getElementById('stopButton').hidden&&!document.getElementById('sendButton').disabled);
      assert.equal(cancelCount,3);
      assert.equal(await frame.locator('#stopButton').isHidden(),true,'exact persisted terminal settles an omitted active projection');

      // A delayed acknowledgement from the previous account must neither open
      // its stream nor release ownership of a newly submitted account turn.
      active=null;sent=null;terminal=false;omitActive=false;streamClosed=false;
      holdSend=gate();const oldAck=holdSend;
      await frame.locator('#prompt').fill('Old pending acknowledgement');await frame.locator('#sendButton').click();
      await assertEventually(()=>heldSend===oldAck,'old acknowledgement held');
      const oldRequestId=sent.requestId;
      accountNumber=3;active=null;sent=null;terminal=false;
      await page.evaluate(()=>window.parentRPC('account.signIn'));
      await frame.waitForFunction(()=>document.getElementById('accountName').textContent==='Account user 3');
      await frame.waitForFunction(()=>document.body.innerText.includes('Mage 3'));
      holdSend=gate();const newAck=holdSend;
      await frame.locator('#prompt').fill('New pending acknowledgement');await frame.locator('#sendButton').click();
      await assertEventually(()=>heldSend===newAck,'new acknowledgement held');
      const newRequestId=sent.requestId;
      oldAck.release();await frame.waitForTimeout(300);
      assert.equal(await frame.locator('#stopButton').isVisible(),true);
      assert.equal(await frame.locator('#sendButton').isDisabled(),true);
      assert.equal(streamedRequests.includes(oldRequestId),false,'stale account acknowledgement cannot open an old stream');
      newAck.release();await assertEventually(()=>streamedRequests.includes(newRequestId)&&failures===0,'new request keeps ownership');
      terminal=true;omitActive=true;
      await frame.evaluate(()=>window.dispatchEvent(new Event('focus')));
      await frame.waitForFunction(()=>document.getElementById('stopButton').hidden&&!document.getElementById('sendButton').disabled);

      const forwardedBeforeStale=await page.evaluate(()=>window.received.filter(m=>m.type==='host.batch').length);
      terminal=false;omitActive=false;allowBatch=true;
      await frame.evaluate(()=>window.dispatchEvent(new Event('focus')));
      await frame.waitForTimeout(400);
      assert.equal(await frame.locator('#stopButton').isHidden(),true);
      assert.equal(await page.evaluate(()=>window.received.filter(m=>m.type==='host.batch').length),forwardedBeforeStale,'finished generation cannot forward a late ready batch even without Stop');

      // Preserve the newest source's first-turn rollback if admission fails.
      active=null;sent=null;terminal=false;
      await frame.locator('#newThreadButton').evaluate(button=>button.click());
      failNextSend=true;
      await frame.locator('#prompt').fill('Restore this unsaved first turn');await frame.locator('#sendButton').click();
      await frame.waitForFunction(()=>document.getElementById('prompt').value==='Restore this unsaved first turn'&&!document.getElementById('sendButton').disabled);
      assert.equal(await frame.locator('.user-message').filter({hasText:'Restore this unsaved first turn'}).count(),0,'unaccepted optimistic turn is removed');
      const sendsBeforeStop=sendCount;
      holdPresence=gate();const pendingPresence=holdPresence;
      await frame.locator('#prompt').fill('Stop before native authority arrives');await frame.locator('#sendButton').click();
      await assertEventually(()=>heldPresence===pendingPresence,'native activation held before admission');
      const cancelsBeforeStop=cancelCount;
      await frame.locator('#stopButton').click();
      await assertEventually(()=>cancelCount>cancelsBeforeStop,'pre-admission cancel requested');
      pendingPresence.release();
      await frame.waitForFunction(()=>document.getElementById('prompt').value==='Stop before native authority arrives'&&!document.getElementById('sendButton').disabled);
      assert.equal(sendCount,sendsBeforeStop,'Stop cannot be followed by admission after delayed lease activation');
      assert.equal(await page.evaluate(()=>window.received.at(-1)?.type==='host.revoke'||window.received.some(m=>m.type==='host.revoke'&&m.payload.reason==='generation-cancelled')),true);
    }
    assert.equal(await page.evaluate(secret=>JSON.stringify(window.received).includes(secret),token),false,'progress transport never exposes the Chat credential');
    assert.equal(await frame.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,'full geometry review fits the panel');
    assert.deepEqual(errors,[]);
    console.log(viewport.width+' PASS: 40-step preview, EOF-before-ready, 503 retries, guarded admission, snapshot batch, immediate Stop, terminal-only cleanup'+(viewport.width===1440?', stale account sync/cancel ownership':''));
    await context.close();
  }}finally{await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
