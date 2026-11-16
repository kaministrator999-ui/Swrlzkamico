'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),http=require('node:http');
const {chromium}=require('playwright');
const root=path.resolve(process.argv[2]||'projects/swrlz-forge-moba/_release_v11_478_candidate');
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
    const original=window.setTimeout;
    window.setTimeout=function(fn,ms,...args){return original.call(window,fn,ms===16000?180:ms,...args);};
   });
   try{
    await page.goto('http://127.0.0.1:'+server.address().port+'/modeler.html',
     {waitUntil:'domcontentloaded',timeout:45000});
    await page.waitForSelector('#se476StartupGate',{state:'visible',timeout:20000});
    await page.waitForFunction(()=>!document.getElementById('se476SignalLost')?.hidden,{timeout:10000});
    await page.locator('#se476OfflineContinue').click({timeout:12000});
    await page.waitForSelector('#modelAtelierToolRail',{state:'visible',timeout:25000});
    await page.waitForFunction(()=>!!window.SWYRL_ENGINE_RING_HIGHLIGHT_478&&
      !!window.SWYRL_ENGINE_VERTEX_ENTRY_477&&
      !!window.SWYRL_ENGINE_PROGRESSIVE_RAIL_475?.inspect?.()?.mounted,{timeout:25000});
    const initial=await page.evaluate(()=>{
      const api=window.SWYRL_ENGINE_MODEL_WORKSHOP;
      const before=api?.inspect?.();
      const created=api?.create?.('sphere');
      const converted=api?.convert?.();
      return {before:before?.selection,created,converted,after:api?.inspect?.()?.selection,
       entry:window.SWYRL_ENGINE_VERTEX_ENTRY_477?.inspect?.()};
    });
    console.log('SE478_TEST_MODEL_'+cfg.name+' '+JSON.stringify(initial));
    assert(initial.created?.ok,'Native sphere test fixture must create an editable part');
    assert(initial.converted?.ok,'Native sphere must be converted to topology for ring tests');
    const sculpt=page.locator('#modelAtelierToolRail > button').filter({hasText:/^Sculpt$/}).first();
    await sculpt.click({timeout:16000});
    await page.waitForFunction(()=>window.SWYRL_ENGINE_PROGRESSIVE_TOOLS_474?.inspect?.()?.family==='Sculpt',
     {timeout:10000});
    const choices=await page.locator('#se474ToolFlyout button[data-se474-kind=tool]').evaluateAll(
     buttons=>buttons.map(b=>b.textContent.trim()));
    console.log('SE478_TOOL_LIST_'+cfg.name+' '+JSON.stringify(choices));
    assert(choices.includes('Inset')&&choices.includes('Extrude'),'Operation flyout must include Inset/Extrude');
    assert(!choices.includes('Vertex')&&!choices.includes('Vertex editing'),'Vertex must not be an operation');
    await page.locator('#se474ToolFlyout button[data-se474-value="Extrude"]').click({timeout:16000});
    await page.waitForFunction(()=>window.SWYRL_ENGINE_PROGRESSIVE_TOOLS_474?.inspect?.()?.tool==='Extrude',
     {timeout:10000});
    const selected=await page.evaluate(()=>{
     const $=id=>document.getElementById(id);
     const rect=id=>{const r=$(id)?.getBoundingClientRect();return r?{
      x:r.x,y:r.y,width:r.width,height:r.height,right:r.right,bottom:r.bottom}:null;};
     return {state:window.SWYRL_ENGINE_PROGRESSIVE_TOOLS_474?.inspect?.(),
      vertex:window.SWYRL_ENGINE_VERTEX_ENTRY_477?.inspect?.(),
      top:[...$('se474SpecificModes').querySelectorAll('button')].map(b=>b.textContent.trim()),
      shapes:[...$('se477SelectionShapes').querySelectorAll('button')].map(b=>b.textContent.trim()),
      topRect:rect('se474SpecificModes'),shapeRect:rect('se477SelectionShapes'),
      transformRect:rect('se320ModelTransform'),
      topHidden:$('se474SpecificModes').hidden,shapeHidden:$('se477SelectionShapes').hidden,
      inspector:$('modelAtelierPanel').dataset.se474SettingsOpen};
    });
    console.log('SE478_VERTEX_ENTRY_'+cfg.name+' '+JSON.stringify(selected));
    assert.equal(selected.state.operation,true);
    assert.equal(selected.state.flyout,false,'Tool flyout must collapse after operation selection to expose selection bars');
    assert.equal(selected.state.selectionType,'vertex');
    assert.equal(selected.state.shape,'single');
    assert.equal(selected.vertex.mode,'vertex');
    assert(selected.vertex.pointCount>0&&selected.vertex.visiblePointOverlay,
     'Selecting Extrude must reveal native selectable vertices');
    assert(selected.top.includes('Vertex')&&selected.top.includes('Face')&&selected.top.includes('Edge'));
    assert(selected.shapes.includes('Single vertex')&&selected.shapes.includes('Vertex ring')&&
      selected.shapes.includes('Filled vertex ring'));
    assert(!selected.topHidden&&!selected.shapeHidden);
    assert.equal(selected.inspector,'false','No settings inspector until selection type chosen');
    assert(selected.shapeRect.y>=selected.topRect.bottom-2,'Selection shape bar below component-type bar');
    if(selected.transformRect&&selected.transformRect.height>0)
      assert(selected.topRect.y>=selected.transformRect.bottom-3,'First bar below transform bar');
    await page.screenshot({path:path.join(root,'se478-vertex-'+cfg.name+'.png')});
    await page.locator('#se477SelectionShapes button[data-se474-value="ring"]').click({timeout:15000});
    await page.waitForFunction(()=>window.SWYRL_ENGINE_PROGRESSIVE_TOOLS_474?.inspect?.()?.shape==='ring',
     {timeout:10000});
    await page.waitForFunction(()=>window.SWYRL_ENGINE_PROGRESSIVE_TOOLS_474?.inspect?.()?.shape==='ring',
     {timeout:10000});
    const ringSelected=await page.evaluate(()=>{
      const result=window.SWYRL_ENGINE_RING_HIGHLIGHT_478.selectCenter(0);
      const view=window.SWYRL_ENGINE_RING_HIGHLIGHT_478.inspect();
      return {result,view};
    });
    console.log('SE478_RING_SELECTED_'+cfg.name+' '+JSON.stringify(ringSelected));
    assert(ringSelected.result?.ok,ringSelected.result?.reason||'Tap center should select ring');
    assert(ringSelected.view.selectedCount>0,'Ring must select connected vertices');
    assert.equal(ringSelected.view.highlightedCount,ringSelected.view.selectedCount,
      'Every ring vertex must have a native highlighted point');
    assert(!ringSelected.view.selectedSlots.includes(0),'Outline must exclude the center vertex');
    assert.equal(ringSelected.view.shape,'outline');
    await page.locator('#se477SelectionShapes button[data-se474-value="fill"]').click({timeout:15000});
    const fill=await page.evaluate(()=>({
      state:window.SWYRL_ENGINE_PROGRESSIVE_TOOLS_474.inspect(),
      ring:!!document.getElementById('se466RingControls'),
      component:window.SWYRL_ENGINE_VERTEX_ENTRY_477.inspect(),
      open:document.getElementById('modelAtelierPanel').dataset.se474SettingsOpen
    }));
    assert.equal(fill.state.shape,'fill');
    assert(fill.ring,'The existing editable-topology ring panel must be mounted');
    assert.equal(fill.open,'true');
    const selection=await page.evaluate(()=>window.SWYRL_ENGINE_RING_HIGHLIGHT_478.inspect());
    console.log('SE478_FILL_SELECTED_'+cfg.name+' '+JSON.stringify(selection));
    assert.equal(selection.shape,'fill');
    assert(selection.selectedSlots.includes(0),'Filled radius must include center vertex');
    assert(selection.selectedCount>ringSelected.view.selectedCount,'Fill must include interior ring vertices');
    assert.equal(selection.highlightedCount,selection.selectedCount,
      'Every ring-fill vertex must have a native highlighted point');
    assert.notEqual(selection.pointColor,ringSelected.view.pointColor,'Ring fill should have distinct highlight color');
    const changedCenter=await page.evaluate(()=>window.SWYRL_ENGINE_RING_HIGHLIGHT_478.selectCenter(1));
    assert(changedCenter?.ok,'Tapping another center should replace and rehighlight the ring');
    const moved=await page.evaluate(()=>window.SWYRL_ENGINE_RING_HIGHLIGHT_478.inspect());
    assert(moved.selectedSlots.includes(1),'New fill center must appear in selected group');
    assert.equal(moved.highlightedCount,moved.selectedCount,'New center must refresh every highlight');
    await page.locator('#se474SpecificModes button[data-se474-value="face"]').click({timeout:12000});
    const face=await page.evaluate(()=>({
     state:window.SWYRL_ENGINE_PROGRESSIVE_TOOLS_474.inspect(),
     shapes:[...document.querySelectorAll('#se477SelectionShapes button')].map(b=>b.textContent.trim()),
     mode:window.SWYRL_ENGINE_MODEL_WORKSHOP?.inspect?.()?.selection?.mode
    }));
    assert.equal(face.state.selectionType,'face');
    assert.equal(face.mode,'face');
    assert(face.shapes.includes('Face region'));
    await sculpt.click({timeout:12000}); // reopen the retained operation list
    await page.locator('#se474ToolFlyout button[data-se474-value="Inset"]').click({timeout:12000});
    const inset=await page.evaluate(()=>({
     state:window.SWYRL_ENGINE_PROGRESSIVE_TOOLS_474.inspect(),
     entry:window.SWYRL_ENGINE_VERTEX_ENTRY_477.inspect()
    }));
    assert.equal(inset.state.tool,'Inset');
    assert.equal(inset.state.selectionType,'vertex');
    assert(inset.entry.pointCount>0&&inset.entry.visiblePointOverlay);
    assert(errors.length===0,'Unexpected script errors '+JSON.stringify(errors.slice(0,4)));
    console.log('SE478_BROWSER_PASS_'+cfg.name);
   }finally{await page.close();}
  }
 }finally{await browser.close();await new Promise(resolve=>server.close(resolve));}
})().catch(e=>{console.error('SE478_BROWSER_FAIL',e.stack||e);process.exitCode=1;try{server.close();}catch{}});
