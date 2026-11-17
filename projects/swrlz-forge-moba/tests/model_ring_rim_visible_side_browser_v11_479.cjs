'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),http=require('node:http');
const {chromium}=require('playwright');
const root=path.resolve(process.argv[2]||'projects/swrlz-forge-moba/_release_v11_479_candidate');
const mime={'.html':'text/html; charset=utf-8','.js':'text/javascript','.css':'text/css',
 '.json':'application/json','.png':'image/png','.jpg':'image/jpeg','.webp':'image/webp','.svg':'image/svg+xml'};
const server=http.createServer((req,res)=>{
 let u;try{u=decodeURIComponent(new URL(req.url,'http://localhost').pathname);}catch{res.writeHead(400).end();return;}
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
   const errors=[];
   page.on('pageerror',e=>errors.push(e.stack||String(e)));
   await page.addInitScript(()=>{
    const previous=window.setTimeout;
    window.setTimeout=function(fn,ms,...args){
     return previous.call(window,fn,ms===16000?180:ms,...args);
    };
   });
   try{
    await page.goto('http://127.0.0.1:'+server.address().port+'/modeler.html',
      {waitUntil:'domcontentloaded',timeout:45000});
    await page.waitForSelector('#se476StartupGate',{state:'visible',timeout:25000});
    await page.waitForFunction(()=>!document.getElementById('se476SignalLost')?.hidden,
      {timeout:12000});
    await page.locator('#se476OfflineContinue').click({timeout:12000});
    await page.waitForSelector('#modelAtelierToolRail',{state:'visible',timeout:25000});
    await page.waitForFunction(()=>!!window.SWYRL_ENGINE_RIM_VISIBILITY_479&&
      !!window.SWYRL_ENGINE_PROGRESSIVE_RAIL_475?.inspect?.()?.mounted,{timeout:25000});
    const fixture=await page.evaluate(()=>{
      const api=window.SWYRL_ENGINE_MODEL_WORKSHOP;
      return {created:api.create('sphere'),converted:api.convert()};
    });
    assert(fixture.created.ok&&fixture.converted.ok,'Editable sphere fixture required');
    await page.locator('#modelAtelierToolRail > button').filter({hasText:/^Sculpt$/}).first().click({timeout:16000});
    await page.locator('#se474ToolFlyout button[data-se474-value="Extrude"]').click({timeout:16000});
    await page.waitForFunction(()=>window.SWYRL_ENGINE_PROGRESSIVE_TOOLS_474?.inspect?.()?.tool==='Extrude',{timeout:10000});
    await page.locator('#se477SelectionShapes button[data-se474-value="ring"]').click({timeout:14000});
    await page.waitForSelector('#se479CenterToggle',{state:'visible',timeout:10000});
    const control=page.locator('#se479CenterToggle');
    assert.equal(await control.getAttribute('aria-pressed'),'false',
      'Tapping a vertex uses rim-first mode by default');
    const rim=await page.evaluate(()=>{
      const api=window.SWYRL_ENGINE_RIM_VISIBILITY_479;
      const chosen=api.selectRim(20);
      return {chosen,state:api.inspect(),overlay:window.SWYRL_ENGINE_RING_HIGHLIGHT_478.inspect()};
    });
    console.log('SE479_RIM_'+cfg.name+' '+JSON.stringify(rim));
    assert(rim.chosen.ok,rim.chosen.reason||'Rim calculation must work');
    assert(rim.chosen.vertexSlots.includes(20),'Tapped vertex must be on selected rim');
    assert(rim.chosen.vertexSlots.length>1,'Rim selection must expand beyond one point');
    assert.equal(rim.overlay.highlightedCount,rim.overlay.selectedCount,
      'All resulting ring vertices must appear selected');
    assert.equal(rim.overlay.selectedCount,rim.chosen.selectedCount);
    assert.equal(rim.state.centerMode,false);
    assert.equal(rim.state.selectedVisible,rim.state.selectedCount,
      'Visible-only rim must not select back vertices');

    await control.click({timeout:12000});
    assert.equal(await control.getAttribute('aria-pressed'),'true');
    const centerMode=await page.evaluate(()=>{
      const api=window.SWYRL_ENGINE_RIM_VISIBILITY_479;
      const result=window.SWYRL_ENGINE_RING_HIGHLIGHT_478.selectCenter(20);
      return {centerMode:api.inspect().centerMode,result,
       selected:window.SWYRL_ENGINE_RING_HIGHLIGHT_478.inspect()};
    });
    console.log('SE479_CENTER_'+cfg.name+' '+JSON.stringify(centerMode));
    assert(centerMode.centerMode&&centerMode.result.ok,
      'Explicit center toggle preserves native center-based ring selection');
    await control.click({timeout:12000});
    assert.equal(await control.getAttribute('aria-pressed'),'false');
    await page.locator('#se477SelectionShapes button[data-se474-value="fill"]').click({timeout:14000});
    const fill=await page.evaluate(()=>{
      const api=window.SWYRL_ENGINE_RIM_VISIBILITY_479;
      const chosen=api.selectRim(20);
      return {chosen,after:api.inspect(),
       overlay:window.SWYRL_ENGINE_RING_HIGHLIGHT_478.inspect()};
    });
    console.log('SE479_FILL_'+cfg.name+' '+JSON.stringify(fill));
    assert(fill.chosen.ok&&fill.chosen.vertexSlots.includes(20),
      'Filled ring must use the tapped point on its outer rim');
    assert(fill.after.selectedVisible===fill.after.selectedCount,
      'Filled selection excludes hidden backside vertices');
    assert(fill.overlay.highlightedCount===fill.overlay.selectedCount,
      'Every filled-ring vertex shows the selected highlight');
    assert(fill.chosen.selectedCount>=rim.chosen.selectedCount,
      'Filled ring includes the area inside the outline');

    await page.locator('#se455ViewButton').click({timeout:12000});
    await page.locator('#se479MaterialVertices').click({timeout:12000});
    const material=await page.evaluate(()=>({
      view:window.SWYRL_ENGINE_MODEL_VIEW.inspect(),
      ring:window.SWYRL_ENGINE_RIM_VISIBILITY_479.inspect(),
      mode:window.SWYRL_ENGINE_MODEL_WORKSHOP.inspect().selection.mode
    }));
    console.log('SE479_MATERIAL_'+cfg.name+' '+JSON.stringify(material));
    assert.equal(material.view.mode,'shaded','Material+Vertices must preserve actual material view');
    assert.equal(material.mode,'vertex');
    assert.equal(material.ring.frontOnly,true,'Material+Vertices defaults to front-surface-only');
    await page.screenshot({path:path.join(root,'se479-rim-material-'+cfg.name+'.png')});

    await page.locator('#se455ViewButton').click({timeout:12000});
    const visibleToggle=page.locator('#se479VisibleSideOnly');
    assert(await visibleToggle.isChecked());
    await visibleToggle.uncheck({timeout:12000});
    assert.equal((await page.evaluate(()=>window.SWYRL_ENGINE_RIM_VISIBILITY_479.inspect())).frontOnly,false);
    await visibleToggle.check({timeout:12000});
    assert.equal((await page.evaluate(()=>window.SWYRL_ENGINE_RIM_VISIBILITY_479.inspect())).frontOnly,true);
    await page.locator('#se455ViewButton').click({timeout:12000});

    // A cube seen from the top projects front and rear vertices onto identical
    // pixels. The camera depth filter must exclude the bottom vertices from
    // the actual selected list (not merely conceal their highlighted dots).
    const box=await page.evaluate(()=>{
      const native=window.SWYRL_ENGINE_MODEL_WORKSHOP;
      const created=native.create('box'),converted=native.convert();
      const camera=window.SWYRL_ENGINE_MODEL_VIEW?.setCamera('top');
      const vertex=native.setComponentMode('vertex');
      const activated=window.SWYRL_ENGINE_VERTEX_ENTRY_477?.activate?.();
      return {created,converted,camera,vertex,activated,after:native.inspect().selection};
    });
    console.log('SE479_BOX_'+cfg.name+' '+JSON.stringify(box));
    assert(box.created.ok&&box.converted.ok&&box.vertex.ok&&box.activated.ok,
      'Top camera must have an editable topology cube in vertex mode');
    const behind=await page.evaluate(()=>{
      const api=window.SWYRL_ENGINE_RIM_VISIBILITY_479;
      const count=window.SWYRL_ENGINE_MODEL_WORKSHOP.inspect().selection.vertexCount;
      const all=Array.from({length:count},(_,slot)=>({slot,visible:api.isVisibleSlot(slot)}));
      const front=all.filter(x=>x.visible).map(x=>x.slot);
      const back=all.filter(x=>!x.visible).map(x=>x.slot);
      const result=api.selectRim(front[0]);
      return {count,front,back,result,selection:api.inspect(),
       overlay:window.SWYRL_ENGINE_RING_HIGHLIGHT_478.inspect()};
    });
    console.log('SE479_BOX_OCCLUSION_'+cfg.name+' '+JSON.stringify(behind));
    assert(behind.front.length>0,'At least one front vertex should be visible');
    assert(behind.back.length>0,'Backside vertices must be occluded under top camera');
    assert(behind.result.ok,'Top-front rim must be selectable');
    assert(behind.selection.selectedCount>0&&
      behind.selection.selectedVisible===behind.selection.selectedCount,
      'Rim group must contain only actual camera-visible vertices');
    assert(behind.selection.selectedSlots.every(slot=>!behind.back.includes(slot)),
      'Bottom face must not be selected while viewing the top');
    assert.equal(behind.overlay.highlightedCount,behind.selection.selectedCount);
    await page.screenshot({path:path.join(root,'se479-rim-top-'+cfg.name+'.png')});
    assert(errors.length===0,'Unexpected JS errors '+JSON.stringify(errors.slice(0,4)));
    console.log('SE479_BROWSER_PASS_'+cfg.name);
   }finally{await page.close();}
  }
 }finally{await browser.close();await new Promise(resolve=>server.close(resolve));}
})().catch(e=>{console.error('SE479_BROWSER_FAIL',e.stack||e);process.exitCode=1;
 try{server.close();}catch{}});
