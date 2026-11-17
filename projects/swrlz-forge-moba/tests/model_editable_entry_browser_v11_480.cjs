'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),http=require('node:http');
const {chromium}=require('playwright');
const root=path.resolve(process.argv[2]||'projects/swrlz-forge-moba/_release_v11_480_candidate');
const mime={'.html':'text/html; charset=utf-8','.js':'text/javascript','.css':'text/css',
 '.json':'application/json','.png':'image/png','.jpg':'image/jpeg','.webp':'image/webp','.svg':'image/svg+xml'};
const server=http.createServer((req,res)=>{
 let u;try{u=decodeURIComponent(new URL(req.url,'http://localhost').pathname);}
 catch{res.writeHead(400).end();return;}
 const file=path.resolve(root,'.'+u);
 if(!file.startsWith(root+path.sep)||!fs.existsSync(file)||!fs.statSync(file).isFile()){
  res.writeHead(404).end('not found');return;
 }
 res.writeHead(200,{'content-type':mime[path.extname(file).toLowerCase()]||'application/octet-stream'});
 fs.createReadStream(file).pipe(res);
});
(async()=>{
 await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
 const browser=await chromium.launch({headless:true,args:['--no-sandbox','--enable-unsafe-swiftshader']});
 try{
  for(const cfg of [{name:'mobile-desktop-site',width:980,height:780},
                    {name:'narrow-touch',width:412,height:915}]){
   const page=await browser.newPage({viewport:{width:cfg.width,height:cfg.height},
    isMobile:true,hasTouch:true,deviceScaleFactor:2,reducedMotion:'reduce'});
   const errors=[];page.on('pageerror',e=>errors.push(e.stack||String(e)));
   const confirmations=[];page.on('dialog',async dialog=>{
    confirmations.push({type:dialog.type(),message:dialog.message()});
    await dialog.accept();
   });
   await page.addInitScript(()=>{
    const old=window.setTimeout;
    window.setTimeout=function(fn,ms,...args){return old.call(window,fn,ms===16000?180:ms,...args);};
   });
   try{
    await page.goto('http://127.0.0.1:'+server.address().port+'/modeler.html',
     {waitUntil:'domcontentloaded',timeout:45000});
    await page.waitForSelector('#se476StartupGate',{state:'visible',timeout:25000});
    await page.waitForFunction(()=>!document.getElementById('se476SignalLost')?.hidden,{timeout:12000});
    await page.locator('#se476OfflineContinue').click({timeout:12000});
    await page.waitForSelector('#modelAtelierToolRail',{state:'visible',timeout:25000});
    await page.waitForFunction(()=>!!window.SWYRL_ENGINE_EDITABLE_ENTRY_480&&
      !!window.SWYRL_ENGINE_PROGRESSIVE_RAIL_475?.inspect?.()?.mounted,{timeout:25000});
    const primitive=await page.evaluate(()=>{
      const api=window.SWYRL_ENGINE_MODEL_WORKSHOP;
      const result=api.create('sphere');
      return {result,inspect:api.inspect()};
    });
    console.log('SE480_PRIMITIVE_'+cfg.name+' '+JSON.stringify(primitive));
    assert(primitive.result?.ok,'Need a native plain sphere');
    assert(primitive.inspect?.convert?.available,'Native converter should accept an ordinary sphere');
    const sculpt=page.locator('#modelAtelierToolRail > button').filter({hasText:/^Sculpt$/}).first();
    await sculpt.click({timeout:16000});
    await page.locator('#se474ToolFlyout button[data-se474-value="Extrude"]').click({timeout:16000});
    await page.waitForFunction(()=>window.SWYRL_ENGINE_PROGRESSIVE_TOOLS_474?.inspect?.()?.tool==='Extrude',
      {timeout:10000});
    await page.locator('#se477SelectionShapes button[data-se474-value="fill"]').click({timeout:14000});
    console.log('SE480_MOUNT_DIAG_'+cfg.name+' '+JSON.stringify(await page.evaluate(()=>({
      widget:window.SWYRL_ENGINE_EDITABLE_ENTRY_480.inspect(),
      element:!!document.getElementById('se480EditableEntry'),
      scene:!!document.querySelector('#modelAtelierPanel .atelier-scene'),
      progressive:window.SWYRL_ENGINE_PROGRESSIVE_TOOLS_474.inspect()
    }))));
    await page.waitForSelector('#se480EditableEntry',{state:'visible',timeout:10000});
    const entry=await page.evaluate(()=>{
      const api=window.SWYRL_ENGINE_EDITABLE_ENTRY_480;
      const node=document.getElementById('se480EditableEntry');
      const r=node.getBoundingClientRect();
      const scene=document.querySelector('#modelAtelierPanel .atelier-scene').getBoundingClientRect();
      const shape=document.getElementById('se477SelectionShapes').getBoundingClientRect();
      return {state:api.inspect(),rect:{x:r.x,y:r.y,w:r.width,h:r.height,b:r.bottom},
       scene:{x:scene.x,y:scene.y,w:scene.width,h:scene.height},
       shape:{y:shape.y,b:shape.bottom},
       text:node.textContent};
    });
    console.log('SE480_CONVERT_ENTRY_'+cfg.name+' '+JSON.stringify(entry));
    assert(entry.state.visible&&entry.state.enabled,'Contextual conversion must be actionable');
    assert(entry.rect.w>150&&entry.rect.h>60,'Contextual conversion must have usable dimensions');
    assert(entry.rect.y>=entry.shape.b-2,'Contextual conversion must not overlap the top selection strip');
    assert(entry.rect.x>=entry.scene.x-2,'Conversion card stays inside the real scene');
    assert(entry.rect.b<=entry.scene.y+entry.scene.h+3,
      'Conversion card must not escape the viewport');
    await page.screenshot({path:path.join(root,'se480-before-convert-'+cfg.name+'.png')});
    await page.locator('#se480MakeEditable').click({timeout:14000});
    const converted=await page.evaluate(()=>{
      return {native:window.SWYRL_ENGINE_MODEL_WORKSHOP.inspect(),
       progressive:window.SWYRL_ENGINE_PROGRESSIVE_TOOLS_474.inspect(),
       entry:window.SWYRL_ENGINE_EDITABLE_ENTRY_480.inspect(),
       vertex:window.SWYRL_ENGINE_VERTEX_ENTRY_477.inspect()};
    });
    console.log('SE480_CONVERTED_'+cfg.name+' '+JSON.stringify(converted));
    assert.equal(confirmations.length,1,'Native UV regeneration requires one explicit approval');
    assert(/UV/i.test(confirmations[0].message),'Prompt must disclose UV regeneration');
    assert.equal(converted.native.selection.mode,'vertex',
      'Return to progressive Vertex selection after native converter forces Face');
    assert.equal(converted.progressive.shape,'fill','Do not lose Ring Fill context');
    assert.equal(converted.entry.visible,false,'Conversion CTA hides once mesh is editable');
    assert(converted.vertex.pointCount>0,'Editable topology produces vertex points');
    const selected=await page.evaluate(()=>({
      result:window.SWYRL_ENGINE_RIM_VISIBILITY_479.selectRim(20),
      highlighted:window.SWYRL_ENGINE_RING_HIGHLIGHT_478.inspect()
    }));
    assert(selected.result?.ok,'Rim selection must work immediately on converted primitive');
    assert.equal(selected.result.selectedCount,selected.highlighted.highlightedCount,
      'All selected rim vertices remain highlighted');

    // New primitive and second operation exercise same contextual entry.
    const next=await page.evaluate(()=>{
      const api=window.SWYRL_ENGINE_MODEL_WORKSHOP;
      return {created:api.create('box'),state:api.inspect()};
    });
    assert(next.created?.ok&&next.state.convert.available);
    await sculpt.click({timeout:12000});
    await page.locator('#se474ToolFlyout button[data-se474-value="Inset"]').click({timeout:12000});
    await page.locator('#se477SelectionShapes button[data-se474-value="ring"]').click({timeout:12000});
    await page.waitForSelector('#se480EditableEntry',{state:'visible',timeout:9000});
    const inset=await page.evaluate(()=>({
      state:window.SWYRL_ENGINE_EDITABLE_ENTRY_480.inspect(),
      active:window.SWYRL_ENGINE_PROGRESSIVE_TOOLS_474.inspect()
    }));
    assert(inset.state.visible&&inset.state.enabled&&inset.active.tool==='Inset');

    // A protected authored mesh is refused by the native availability
    // contract; no fake "force conversion" affordance is permitted.
    const blocked=await page.evaluate(()=>{
      const original=window.SWYRL_ENGINE_MODEL_WORKSHOP;
      window.__se480OriginalWorkshop=original;
      window.__se480UnsafeConvertCalled=false;
      window.SWYRL_ENGINE_MODEL_WORKSHOP={...original,
       inspect(){const state=original.inspect();return {...state,convert:{
        available:false,reason:'This mesh has protected paint or texture data. Use an independent plain mesh.'
       }};},
       convert(){window.__se480UnsafeConvertCalled=true;return {ok:false};}
      };
      window.SWYRL_ENGINE_EDITABLE_ENTRY_480.refresh();
      return true;
    });
    assert(blocked);
    await page.waitForFunction(()=>window.SWYRL_ENGINE_EDITABLE_ENTRY_480.inspect().enabled===false,
      {timeout:9000});
    const protectedView=await page.evaluate(()=>({
      entry:window.SWYRL_ENGINE_EDITABLE_ENTRY_480.inspect(),
      disabled:document.getElementById('se480MakeEditable').disabled,
      reason:document.getElementById('se480EditableReason').textContent,
      called:window.__se480UnsafeConvertCalled
    }));
    assert(protectedView.entry.visible&&!protectedView.entry.enabled&&protectedView.disabled);
    assert(/protected paint or texture/.test(protectedView.reason),
      'Show native protection reason rather than hiding the unavailable converter');
    assert(!protectedView.called,'Protection must never invoke conversion');
    await page.evaluate(()=>{
      window.SWYRL_ENGINE_MODEL_WORKSHOP=window.__se480OriginalWorkshop;
      delete window.__se480OriginalWorkshop;
      window.SWYRL_ENGINE_EDITABLE_ENTRY_480.refresh();
    });
    console.log('SE480_PROTECTED_'+cfg.name+' '+JSON.stringify(protectedView));
    await page.screenshot({path:path.join(root,'se480-protected-'+cfg.name+'.png')});
    assert(errors.length===0,'Unexpected script errors '+JSON.stringify(errors.slice(0,4)));
    console.log('SE480_BROWSER_PASS_'+cfg.name);
   }finally{await page.close();}
  }
 }finally{await browser.close();await new Promise(resolve=>server.close(resolve));}
})().catch(e=>{console.error('SE480_BROWSER_FAIL',e.stack||e);process.exitCode=1;
 try{server.close();}catch{}});
