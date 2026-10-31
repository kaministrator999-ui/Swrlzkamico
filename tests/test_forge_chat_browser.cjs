/* Controlled two-origin browser fixture: no real login, inference, remote page or editor mutation. */
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const ROOT=path.resolve(__dirname,'..');
const CHAT='https://kamiloki-swyrlz.hf.space',FORGE='https://kamiloki-swrlz-forge-moba.static.hf.space';
const protocol='swrlz-forge-chat-v1',hostId='host_01234567890123456789',channelId='chan_01234567890123456789';
const pairId='a'.repeat(32),leaseId='b'.repeat(32),batchId='c'.repeat(32);
const token='sfe1_PRIVATE_CONTROLLED_BROWSER_FIXTURE';
const stationSource=fs.readFileSync(path.join(ROOT,'hf_space/station.py'),'utf8');
const presentationAdapter=stationSource.match(/^    adapter='([^']*)'/m)?.[1]||'';
const presentationCss=stationSource.match(/^    css='([^']*)'/m)?.[1]||'';
assert.ok(presentationAdapter.includes('rich-widgets-v284.js'),'use the actual Station presentation adapter');
const initialProfile={display_name:'Account user',preferences:{general:{enterToSend:true,personalityProfile:'default'},profile:{pronouns:'',role:'',communicationStyle:'adaptive',outputStyle:'adaptive'},proposalPolicy:{}},model_preferences:{defaultModel:'700m',effort:'auto',responseLength:'adaptive'},ui_preferences:{density:'compact',glass:'standard',motion:'off',fontScale:'1',highContrast:false,reducedTransparency:false},companion_profile:{name:'§wyrlz',title:'Glitch Dragon Kompanion',form:'Glitch Dragon',pronouns:'',warmth:'adaptive',directness:'adaptive',humor:'adaptive',loreDensity:'adaptive'},version:0,updated_at:0};
const parentHtml=`<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><style>body{margin:0;background:#161022}iframe{position:absolute;inset:0 0 0 auto;width:min(480px,100vw);height:100dvh;border:0}button{position:relative;z-index:2}</style></head><body><iframe id="chat" title="§wyrlz Chat" src="${CHAT}/?forgeEmbed=1"></iframe><script>
const protocol=${JSON.stringify(protocol)},hostId=${JSON.stringify(hostId)},channelId=${JSON.stringify(channelId)},chatOrigin=${JSON.stringify(CHAT)};
const frame=document.getElementById('chat');let port=null;window.received=[];const pending=new Map();
function send(type,payload,requestId=crypto.randomUUID()){port.postMessage({protocol,hostId,channelId,type,payload,requestId});return requestId;}
window.parentRPC=(type,payload={})=>new Promise((resolve,reject)=>{const requestId=crypto.randomUUID();pending.set(requestId,{resolve,reject});send(type,payload,requestId);});
window.addEventListener('message',event=>{if(event.origin!==chatOrigin||event.source!==frame.contentWindow||event.data?.protocol!==protocol||event.data.hostId!==hostId||event.data.channelId!==channelId||event.data.type!=='iframe.ready'||port)return;const channel=new MessageChannel();port=channel.port1;port.onmessage=event=>{const m=event.data;window.received.push(m);if(m.type==='rpc.result'){const task=pending.get(m.requestId);if(task){pending.delete(m.requestId);m.payload.ok===false?task.reject(Error(m.payload.error)):task.resolve(m.payload.result??m.payload);}}if(m.type==='host.context')send('rpc.result',{ok:true,result:{projectId:'native-project',context:{mode:'edit',workspace:'model',epoch:1,meshes:[]}}},m.requestId);if(m.type==='host.presence')send('rpc.result',{ok:true,result:{leaseId:${JSON.stringify(leaseId)}}},m.requestId);};port.start();frame.contentWindow.postMessage({protocol,hostId,channelId,type:'host.connect',requestId:crypto.randomUUID(),payload:{}},chatOrigin,[channel.port2]);send('host.visibility',{visible:true});window.hostReady=true;});
frame.onload=()=>frame.contentWindow.postMessage({protocol,hostId,channelId,type:'host.hello',requestId:crypto.randomUUID(),payload:{}},chatOrigin);
window.closeHost=()=>send('host.inactive',{reason:'closed'});
</script></body></html>`;

(async()=>{
  const playwright=await import(process.env.PLAYWRIGHT_MODULE||require.resolve('playwright'));
  const {chromium}=playwright.chromium?playwright:playwright.default;
  const executablePath=process.env.CHROMIUM_PATH||process.env.SWRLZ_CHROMIUM_PATH||(fs.existsSync('/usr/bin/chromium')?'/usr/bin/chromium':undefined);
  const browser=await chromium.launch({headless:true,...(executablePath?{executablePath}:{}),args:['--no-sandbox','--disable-dev-shm-usage']});
  try{
    for(const [width,height,label] of [[1440,900,'desktop'],[390,844,'mobile'],[980,844,'android-desktop-site']]){
      const context=await browser.newContext({viewport:{width,height},serviceWorkers:'block',...(label==='android-desktop-site'?{isMobile:true,hasTouch:true}:{})});
      const page=await context.newPage(),pageErrors=[],requests=[],saves=[];
      page.on('pageerror',error=>pageErrors.push(error.message));
      let profile=structuredClone(initialProfile),sent=null;
      // Station-saved verified chooser: this fixture isolates the real Chat
      // widget renderer from backend WIDGET-stream timing (tested in Python).
      let projectSetupWidget={contract:'swrlz-widget-v1',kind:'forge-project-setup',title:'New §e Project',
        provider:'Current editor starter catalog',data:{schema:'swrlz-forge-project-setup-v1',
          currentProject:'Sheep Tag',suggestedStarterId:'blank-scene',
          starters:[{id:'blank-scene',name:'Blank scene',group:'fresh',workspace:'scene'},
            {id:'blank-model',name:'Blank 3D model',group:'fresh',workspace:'model-atelier'},
            {id:'sheep-tag-meadow',name:'Sheep Tag',group:'starter',workspace:'scene'},
            {id:'glitch-dragons-den',name:'Dragon Den',group:'starter',workspace:'scene'}],
          notice:'Your current project will be preserved.'}};

      const designPreviewWidget={contract:'swrlz-widget-v1',kind:'forge-design-preview',
        title:'§E Design Studio · Review',provider:'Current native context',data:{
          schema:'swrlz-forge-design-preview-v1',project:'Sheep Tag',workspace:'model-atelier',
          operationCount:2,request:'Design a two-piece robot model',
          followup:"Apply in §e now: Add a box mesh, name='Robot body'; Add a sphere mesh, name='Robot head'",
          steps:[{index:1,op:'mesh.add',name:'Robot body',kind:'box',position:[0,0,0],scale:[1,1,1],color:'#65d9f5'},
            {index:2,op:'mesh.add',name:'Robot head',kind:'sphere',position:[0,2,0],scale:[.6,.6,.6],color:'#9c87ff'}],
          notice:'Conceptual proposal only. No editor operation has run.'}};
      await context.route('**/*',async route=>{
        const request=route.request(),url=new URL(request.url()),pathname=decodeURIComponent(url.pathname);
        if(url.origin===FORGE)return route.fulfill({contentType:'text/html',body:parentHtml});
        if(url.origin!==CHAT)return route.fulfill({status:200,contentType:url.pathname.endsWith('.css')?'text/css':'application/javascript',body:''});
        if(pathname.startsWith('/api/')){
          const auth=request.headers()['authorization']||'';requests.push({pathname,auth});
          const body=request.postDataJSON?.()||null;
          const json=(value,status=200)=>route.fulfill({status,contentType:'application/json',body:JSON.stringify(value)});
          if(pathname==='/api/forge/embed/pair')return json({pairId,loginUrl:'/forge/login?pairId='+pairId,expiresAt:Date.now()/1000+300,recoveryCode:'b'.repeat(12)});
          if(pathname==='/api/forge/embed/pair/'+pairId)return json({approved:true});
          if(pathname==='/api/forge/embed/pair/exchange')return json({token,expiresAt:Date.now()/1000+3600,parentOrigin:FORGE,hostId,channelId,user:{id:'google:controlled',displayName:'Account user'}});
          if(pathname==='/api/account/status')return json({googleClientId:'controlled-fixture'});
          if(auth!=='Bearer '+token)return json({detail:'CONTROLLED_AUTH_REQUIRED'},401);
          if(pathname==='/api/account/me')return json({user:{id:'google:controlled',displayName:'Account user'},profile,durable:true});
          if(pathname==='/api/account/profile'){
            saves.push(body);profile={display_name:body.displayName,preferences:body.preferences,model_preferences:body.modelPreferences,ui_preferences:body.uiPreferences,companion_profile:body.companionProfile,version:profile.version+1,updated_at:Date.now()};return json({ok:true,profile,durable:true,saved:true});
          }
          if(pathname==='/api/lalm_station/sync')return json({revision:1,currentThread:{id:'saved-chat'},threads:[{id:'saved-chat',title:'Saved account conversation',pinned:false,createdAt:1,messages:[{id:'history-user',role:'user',text:'Earlier account project question',createdAt:1},{id:'history-assistant',role:'assistant',text:'This history belongs to the shared Google account.',createdAt:2},...(projectSetupWidget?[{id:'wizard-message',role:'assistant',text:'What kind of §e project would you like to start?',createdAt:3,meta:{widgets:[projectSetupWidget]}},{id:'design-message',role:'assistant',text:'Here is the proposed primitive blockout. No changes have been made.',createdAt:4,meta:{widgets:[designPreviewWidget]}}]:[])]}],activeGeneration:null});
          if(pathname==='/api/github/status')return json({configured:false,linked:false});
          if(pathname==='/api/forge/embed/presence')return json({ticket:'sfp1_CONTROLLED_TICKET',hostId,channelId,threadId:body.threadId,projectId:body.projectId});
          if(pathname==='/api/lalm_station/send'){sent=body;return json({requestId:body.requestId});}
          if(pathname==='/api/lalm_station/stream'){
            const wizard=sent.prompt==='Start a new project';
            const values=wizard?[
              {type:'DELTA',text:'What kind of §e project would you like to start?',requestId:sent.requestId,seq:1},
              {type:'WIDGET',widget:{contract:'swrlz-widget-v1',kind:'forge-project-setup',title:'New §e Project',
                provider:'Current editor starter catalog',data:{schema:'swrlz-forge-project-setup-v1',
                  currentProject:'Sheep Tag',suggestedStarterId:'blank-scene',
                  starters:[{id:'blank-scene',name:'Blank scene',group:'fresh',workspace:'scene'},
                    {id:'blank-model',name:'Blank 3D model',group:'fresh',workspace:'model-atelier'},
                    {id:'sheep-tag-meadow',name:'Sheep Tag',group:'starter',workspace:'scene'},
                    {id:'glitch-dragons-den',name:'Dragon Den',group:'starter',workspace:'scene'}],
                  notice:'Your current project will be preserved.'}},requestId:sent.requestId,seq:2},
              {type:'COMPLETED',terminal:true,requestId:sent.requestId,seq:3}
            ]:[{type:'FORGE_BATCH_READY',batchId,leaseId,threadId:sent.threadId,generationId:sent.requestId,projectId:'native-project',requestId:sent.requestId,seq:1},
              {type:'DELTA',text:'Native receipt confirmed.',requestId:sent.requestId,seq:2},
              {type:'COMPLETED',terminal:true,requestId:sent.requestId,seq:3}];
            if(wizard)projectSetupWidget=values.find(v=>v.type==='WIDGET').widget;
            return route.fulfill({contentType:'application/x-ndjson',body:values.map(value=>JSON.stringify(value)).join('\n')+'\n'});
          }
          return json({ok:true});
        }
        const relative=pathname==='/'?'chat/§wyrlz/index.html':pathname.replace(/^\//,'');
        let filename=path.resolve(ROOT,relative);
        if(!filename.startsWith(ROOT+path.sep))return route.fulfill({status:404,body:''});
        if(!fs.existsSync(filename)&&relative.startsWith('chat/§wyrlz/assets/'))filename=path.resolve(ROOT,'hf_space',relative);
        if(!fs.existsSync(filename))return route.fulfill({status:404,body:''});
        const ext=path.extname(filename),mime={'.html':'text/html','.js':'application/javascript','.json':'application/json','.css':'text/css','.png':'image/png'}[ext]||'application/octet-stream';
        let content=fs.readFileSync(filename);
        if(relative==='chat/§wyrlz/index.html')content=content.toString('utf8').replace('</head>',presentationCss+'</head>').replace('</body>',presentationAdapter+'</body>');
        return route.fulfill({contentType:mime,body:content});
      });
      await page.goto(FORGE+'/',{waitUntil:'domcontentloaded'});
      await page.waitForFunction(()=>window.hostReady===true);
      const frame=page.frames().find(frame=>frame.url().startsWith(CHAT));assert.ok(frame);
      assert.equal(await frame.locator('#accountName').textContent(),'Google Account');
      const pairing=await page.evaluate(()=>window.parentRPC('account.signIn'));assert.equal(pairing.pairId,pairId);
      await frame.waitForFunction(()=>document.getElementById('accountName').textContent==='Account user');
      await frame.getByText('This history belongs to the shared Google account.',{exact:true}).waitFor();
      if(await frame.locator('#chatUpdatesDialog[open]').count())await frame.locator('#chatUpdatesClose').click();
      await frame.locator('#menuButton').click();await frame.locator('#settingsGear').click();
      assert.equal(await frame.locator('#settingsSave').isEnabled(),true,'version0 settings can be saved');
      assert.match(await frame.locator('#settingsSaveState').textContent(),/not been saved/);
      await frame.locator('[data-settings-section="model"]').click();
      await frame.locator('#settingDefaultModel').selectOption('coder');await frame.locator('#settingsSave').click();
      await frame.waitForFunction(()=>document.getElementById('settingsSaveState').textContent.includes('Saved account settings loaded'));
      assert.equal(saves.length,1);assert.equal(saves[0].version,0);assert.equal(saves[0].modelPreferences.defaultModel,'coder');
      await frame.locator('#settingsClose').click();
      if(await frame.locator('body').evaluate(node=>node.classList.contains('menu-open')))await frame.locator('#menuButton').click();
      if(label==='android-desktop-site'){
        assert.equal(await frame.evaluate(()=>matchMedia('(any-pointer:coarse)').matches),true,'Android desktop-site emulation has coarse pointer');
        const beforeScale=await page.evaluate(()=>window.visualViewport?.scale??1);
        await frame.locator('#prompt').focus();
        const metrics=await frame.locator('#prompt').evaluate(node=>({
          fontSize:parseFloat(getComputedStyle(node).fontSize),
          lineHeight:parseFloat(getComputedStyle(node).lineHeight),
          height:node.getBoundingClientRect().height
        }));
        assert.ok(metrics.fontSize>=18,'Touch composer font must be >=18px despite wide desktop-site viewport');
        assert.ok(metrics.height>=48,'Touch focus field must fit readable glyphs without clipping');
        assert.ok(metrics.lineHeight>=24,'Touch composer line height must fit increased font size');
        assert.equal(await page.evaluate(()=>window.visualViewport?.scale??1),beforeScale,
          'Controlled desktop-site browser focus does not magnify the parent viewport');
        const meta=await frame.locator('meta[name="viewport"]').getAttribute('content');
        assert.ok(!/user-scalable\s*=\s*no|maximum-scale\s*=\s*1/.test(meta||''),
          'Keep manual browser pinch-zoom and accessibility available');
      }
      const designCard=frame.locator('.forge-design-preview');
      await designCard.waitFor();
      assert.equal(await designCard.locator('svg').count(),1,label+' Design Studio renders a conceptual SVG');
      assert.match(await designCard.locator('svg').getAttribute('aria-label'),/top view/i);
      await designCard.getByRole('button',{name:'Front view'}).click();
      assert.match(await designCard.locator('svg').getAttribute('aria-label'),/front view/i);
      await designCard.locator('.forge-design-progress input').fill('1');
      assert.match(await designCard.locator('.forge-design-progress').textContent(),/1 \/ 2/);
      await designCard.getByRole('button',{name:/Expand preview/}).click();
      assert.equal(await frame.locator('.forge-design-overlay [role="dialog"]').count(),1);
      await frame.locator('.forge-design-overlay').getByRole('button',{name:/Close/}).click();
      assert.equal(await frame.locator('.forge-design-overlay').count(),0);
      assert.equal(sent,null,'inspecting the design preview never submits editor work');
      await frame.locator('#prompt').fill('Add a blue cube in the editor.');await frame.locator('#sendButton').click();
      await page.waitForFunction(()=>window.received.some(message=>message.type==='host.batch'));
      assert.equal(sent.forgeLeaseId,leaseId);assert.equal(sent.modelId,'coder');
      // Controlled server WIDGET simulates the verified current native starter
      // catalog; no actual project or account write occurs in this fixture.
      const setup=frame.locator('.forge-project-setup');
      try{await setup.locator('.forge-project-name').waitFor({timeout:8000});}
      catch(error){
        console.error('PROJECT_SETUP_BROWSER_DIAG_PRE',JSON.stringify({
          sentPrompt:sent?.prompt,projectSetupWidget:!!projectSetupWidget,pageErrors},null,2));
        const debug=await Promise.race([
          frame.evaluate(()=>({
            focused:document.activeElement?.id||'',
            composer:document.getElementById('prompt')?.value,
            widgetKinds:Array.from(document.querySelectorAll('.swrlz-widget')).map(n=>n.dataset.widgetKind),
            widgetStackCount:document.querySelectorAll('.message-widget-stack').length,
            assistantTexts:Array.from(document.querySelectorAll('.assistant-message .assistant-body')).slice(-4).map(n=>(n.textContent||'').slice(0,350)),
            threadRows:document.querySelectorAll('.thread-row').length
          })).catch(e=>({error:String(e)})),
          new Promise(resolve=>setTimeout(()=>resolve({error:'FRAME_DIAG_TIMEOUT'}),2500))
        ]);
        console.error('PROJECT_SETUP_BROWSER_DIAG',JSON.stringify(debug,null,2));
        throw error;
      }
      assert.equal(await setup.locator('.forge-project-name').count(),1,
        'New project defaults to naming an independent blank scene, not opening a starter');
      await setup.getByRole('button',{name:'← Change starting point'}).click();
      assert.equal(await setup.locator('button[data-starter-id="blank-scene"]').count(),1);
      assert.equal(await setup.locator('button[data-starter-id="blank-model"]').count(),1);
      await setup.getByRole('button',{name:'← Back'}).click();
      await setup.getByRole('button',{name:/Starter pack/i}).click();
      await setup.locator('button[data-starter-id="sheep-tag-meadow"]').click();
      const newName=setup.locator('.forge-project-name');await newName.fill('Wolf Quest');
      await setup.getByRole('button',{name:'Review project →'}).click();
      assert.match(await setup.locator('.forge-project-review').textContent(),/Wolf Quest[\s\S]*Sheep Tag/);
      assert.equal(sent.prompt,'Add a blue cube in the editor.','review never executes a native operation');
      await setup.getByRole('button',{name:'Create project in §e'}).click();
      const expectedProjectCommand='Create a new project from the sheep-tag-meadow starter named exactly "Wolf Quest"';
      for(let attempt=0;attempt<40 && sent?.prompt!==expectedProjectCommand;attempt++)
        await new Promise(resolve=>setTimeout(resolve,100));
      assert.equal(sent?.prompt,expectedProjectCommand,
        'explicit owner click sends the exact native request to the authenticated Station transport');
      await frame.locator('#sendButton').waitFor({state:'visible'});
      await frame.waitForFunction(()=>!document.getElementById('sendButton').disabled);
      await designCard.getByRole('button',{name:/Approve · request build/}).click();
      for(let attempt=0;attempt<40 && !String(sent?.prompt||'').startsWith('Apply in §e now:');attempt++)
        await new Promise(resolve=>setTimeout(resolve,100));
      assert.ok(sent?.prompt.startsWith('Apply in §e now: Add a box mesh'),
        'design approval sends a NEW current editor request, not an unauthorized native batch');
      // The fixture intentionally does not persist the new command as a
      // conversation bubble; don't mistake that artificial sync for a product bug.
      const parentData=await page.evaluate(()=>JSON.stringify(window.received));assert.ok(!parentData.includes(token));assert.ok(!parentData.includes('Earlier account project question'));
      const dimensions=await frame.evaluate(()=>({overflow:document.documentElement.scrollWidth>innerWidth,width:innerWidth}));assert.equal(dimensions.overflow,false,label+' Chat fits panel width');
      await page.evaluate(()=>window.closeHost());
      const batchCount=await page.evaluate(()=>window.received.filter(message=>message.type==='host.batch').length);
      await frame.evaluate(({batchId,leaseId})=>window.SwrlzForgeEmbedV1.forwardBatch({batchId,leaseId,threadId:'saved-chat'}),{batchId:'f'.repeat(32),leaseId});
      assert.equal(await page.evaluate(()=>window.received.filter(message=>message.type==='host.batch').length),batchCount);
      assert.deepEqual(pageErrors,[],label+' canonical UI has no browser exceptions');
      assert.ok(requests.filter(item=>item.auth).every(item=>item.auth==='Bearer '+token));
      console.log(label+' PASS: canonical iframe, private pairing, shared history, first explicit settings save, native batch forwarding/revocation, no overflow');
      await context.close();
    }
  }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
