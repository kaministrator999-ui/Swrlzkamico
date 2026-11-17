'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),http=require('node:http');
const {chromium}=require('playwright');
const root=path.resolve(process.argv[2]||'projects/swrlz-forge-moba/_release_v11_482_candidate');
const mime={'.html':'text/html; charset=utf-8','.js':'text/javascript','.css':'text/css','.json':'application/json',
 '.png':'image/png','.jpg':'image/jpeg','.webp':'image/webp','.svg':'image/svg+xml'};
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
   let confirmations=0;page.on('dialog',async d=>{confirmations++;
    assert(/original model remains|original model|UV/.test(d.message()));
    await d.accept();
   });
   await page.addInitScript(()=>{
    const old=window.setTimeout;
    window.setTimeout=function(fn,ms,...a){return old.call(window,fn,ms===16000?180:ms,...a);};
   });
   try{
    await page.goto('http://127.0.0.1:'+server.address().port+'/modeler.html',
     {waitUntil:'domcontentloaded',timeout:45000});
    await page.waitForSelector('#se476StartupGate',{state:'visible',timeout:25000});
    await page.waitForFunction(()=>!document.getElementById('se476SignalLost')?.hidden,{timeout:12000});
    await page.locator('#se476OfflineContinue').click({timeout:12000});
    await page.waitForSelector('#modelAtelierToolRail',{state:'visible',timeout:25000});
    await page.waitForFunction(()=>!!window.SWYRL_ENGINE_TEXTURED_TOPOLOGY_481&&
     !!window.SWYRL_ENGINE_PROGRESSIVE_RAIL_475?.inspect?.()?.mounted,{timeout:25000});
    const created=await page.evaluate(()=>window.SWYRL_ENGINE_MODEL_WORKSHOP.create('sphere'));
    assert(created?.ok,'Native source part required');
    await page.waitForSelector('#se336UVFile',{state:'attached',timeout:12000});
    // Use the real UV image importer. A cyan-free high-contrast geometric
    // pattern detects texture loss much more reliably than an unpainted mesh.
    const dataUrl=await page.evaluate(()=>{
     const c=document.createElement('canvas');c.width=c.height=32;
     const x=c.getContext('2d');
     x.fillStyle='#2438db';x.fillRect(0,0,32,32);
     x.fillStyle='#d66d25';x.fillRect(0,0,16,16);
     x.fillStyle='#f0e400';x.fillRect(16,16,16,16);
     x.fillStyle='#d11962';x.fillRect(20,0,12,12);
     return c.toDataURL('image/png');
    });
    await page.locator('#se336UVFile').setInputFiles({
     name:'uv-fidelity-pattern.png',mimeType:'image/png',
     buffer:Buffer.from(dataUrl.slice(dataUrl.indexOf(',')+1),'base64')});
    await page.waitForFunction(()=>window.SWYRL_ENGINE_TEXTURED_TOPOLOGY_481.inspect().available,
      {timeout:18000});
    const paint=await page.evaluate(()=>{
      const uv=window.SWYRLZ_E_MODEL_UV_SLIDE;
      const before=uv.state();
      if(!before.enabled)uv.toggle();
      uv.nudge('left');uv.nudge('up');
      const slid=uv.state();
      if(slid.enabled)uv.toggle();
      return {before,slid,status:window.SWYRL_ENGINE_TEXTURED_TOPOLOGY_481.inspect()};
    });
    assert(paint.status.available,'Painting must enable UV-faithful conversion');
    assert(paint.slid.offset.some(x=>Math.abs(x)>.001),'Texture offset should be nonzero to verify alignment');
    console.log('SE482_TEXTURED_SOURCE_'+cfg.name+' '+JSON.stringify({
     source:created.id,slid:paint.slid.offset,faces:paint.status.faces,
     vertices:paint.status.vertices
    }));
    await page.locator('#modelAtelierToolRail > button').filter({hasText:/^Sculpt$/}).first().click({timeout:14000});
    await page.locator('#se474ToolFlyout button[data-se474-value="Extrude"]').click({timeout:14000});
    await page.locator('#se477SelectionShapes button[data-se474-value="fill"]').click({timeout:14000});
    await page.waitForSelector('#se480EditableEntry',{state:'visible',timeout:11000});
    const card=await page.evaluate(()=>({
      entry:window.SWYRL_ENGINE_EDITABLE_ENTRY_480.inspect(),
      text:document.getElementById('se480MakeEditable').textContent,
      reason:document.getElementById('se480EditableReason').textContent
    }));
    assert(card.entry.visible&&card.entry.enabled,'Painted source must show actionable conversion');
    assert.equal(card.text,'Make textured editable copy');
    assert(/original UVs/i.test(card.reason),'User must be told the texture UV mapping is retained');
    await page.screenshot({path:path.join(root,'se481-textured-source-'+cfg.name+'.png')});
    await page.locator('#se480MakeEditable').click({timeout:14000});
    const result=await page.evaluate(()=>{
      const api=window.SWYRL_ENGINE_TEXTURED_TOPOLOGY_481;
      const source=api.inspectSource(),fidelity=api.inspectFidelity(),
       native=window.SWYRL_ENGINE_MODEL_WORKSHOP.inspect(),
       progressive=window.SWYRL_ENGINE_PROGRESSIVE_TOOLS_474.inspect();
      return {fidelity,nativeMode:native.selection.mode,
       nativeConvert:native.convert,progressive,
       selected:api.inspect(),source:{
        sourceId:source.sourceId,copyId:source.copyId,
        sourceHidden:source.sourceHidden,copyHidden:source.copyHidden,
        sameTexture:source.sourceTexture===source.copyTexture,
        sameOffsets:JSON.stringify(source.sourceUVSettings)===JSON.stringify(source.copyUVSettings),
        sourceKind:source.sourceKind,copyKind:source.copyKind,
        topology:source.copyTopology
       }
      };
    });
    console.log('SE482_UV_FIDELITY_'+cfg.name+' '+JSON.stringify(result));
    assert.equal(confirmations,1);
    assert.equal(result.nativeMode,'vertex','Return to vertex mode from native copy');
    assert.equal(result.progressive.shape,'fill','Retain filled vertex ring tool');
    assert(result.source.sourceHidden&&!result.source.copyHidden,'Original must be hidden, copy visible');
    assert(result.source.sameTexture&&result.source.sameOffsets,'Image and UV correction must match exactly');
    assert.equal(result.source.copyKind,'topologyMesh');
    assert(result.source.sourceKind!=='topologyMesh','Original source kind preserved');
    assert(result.fidelity.ok,'Full triangle-corner positions/UVs and painted material must match source');
    assert.equal(result.fidelity.uvDifferences,0);
    assert.equal(result.fidelity.positionDifferences,0);
    assert(result.fidelity.sameUVOffset&&result.fidelity.sameUVRepeat);
    assert(!result.nativeConvert.available,'Original native converter no longer needed on working copy');
    const ring=await page.evaluate(()=>{
     const visibility=window.SWYRL_ENGINE_RIM_VISIBILITY_479;
     const max=window.SWYRL_ENGINE_TEXTURED_TOPOLOGY_481.inspectSource().copyTopology.vertices;
     let pick=-1;
     for(let i=0;i<max;i++)if(visibility.isVisibleSlot(i)){pick=i;break;}
     if(pick<0)return {ok:false,reason:'No visible vertex'};
     const r=visibility.selectRim(pick);
     const overlay=window.SWYRL_ENGINE_RING_HIGHLIGHT_478.inspect();
     const ops=window.SWYRL_ENGINE_MODEL_WORKSHOP.inspect().operations;
     return {...r,overlay,ringTransform:ops.ringTransform};
    });
    console.log('SE482_RING_SELECTED_'+cfg.name+' '+JSON.stringify(ring).slice(0,1600));
    assert(ring.ok,'UV-faithful copy must support visible filled-ring selection');
    assert(ring.selectedCount>0&&ring.overlay.highlightedCount===ring.selectedCount,
      'All selected vertices visibly highlighted on texture');
    assert(ring.ringTransform?.available,'Working copy must remain native ring-editable');
    await page.screenshot({path:path.join(root,'se481-painted-vertices-'+cfg.name+'.png')});
    const preview=await page.evaluate(()=>{
     const slider=window.SWYRL_ENGINE_RING_HEIGHT_478;
     const before=window.SWYRL_ENGINE_MODEL_WORKSHOP.inspect().selection.vertexCount;
     const response=slider.previewHeight(.07);
     const active=window.SWYRL_ENGINE_MODEL_WORKSHOP.inspect().preview.active;
     const cancel=window.SWYRL_ENGINE_MODEL_WORKSHOP.cancel();
     return {before,response,active,cancel};
    });
    console.log('SE482_RING_PREVIEW_'+cfg.name+' '+JSON.stringify(preview));
    assert(preview.response.ok&&preview.active&&preview.cancel?.ok,
      'UV-safe ring height preview must be available and cancelable');

    // On a top-down painted sphere, a real circle at fixed local XZ radius
    // must include the whole latitude band, not a graph-step diamond.
    await page.locator('#se477SelectionShapes button[data-se474-value="ring"]').click({timeout:14000});
    const circular=await page.evaluate(()=>{
      const geom=window.SWYRL_ENGINE_GEOMETRIC_RING_482;
      const visible=window.SWYRL_ENGINE_RIM_VISIBILITY_479;
      window.SWYRL_ENGINE_MODEL_VIEW?.setCamera?.('top');
      const max=window.SWYRL_ENGINE_TEXTURED_TOPOLOGY_481.inspectSource().copyTopology.vertices;
      let seed=-1;
      for(let i=0;i<max;i++){
       const p=visible.vertexLocalPosition(i);
       if(!p||!visible.isVisibleSlot(i))continue;
       const r=Math.hypot(p[0],p[2]);
       if(r>.3&&r<.45&&p[1]>.15&&p[1]<.4){seed=i;break;}
      }
      if(seed<0)for(let i=0;i<max;i++)if(visible.isVisibleSlot(i)){
       const p=visible.vertexLocalPosition(i);
       if(p&&Math.hypot(p[0],p[2])>.2&&p[1]>.1){seed=i;break;}
      }
      const picked=visible.selectRim(seed);
      const selected=geom.sampleSlots(picked.vertexSlots||[]);
      const radii=(selected||[]).map(x=>Math.hypot(x.position[0],x.position[2]));
      const highlighted=window.SWYRL_ENGINE_RING_HIGHLIGHT_478.inspect();
      return {seed,picked,selected,highlighted,
       variance:radii.length?Math.max(...radii)-Math.min(...radii):null,
       inspect:geom.inspect()};
    });
    console.log('SE482_GEOMETRIC_CIRCLE_'+cfg.name+' '+JSON.stringify({
      seed:circular.seed,count:circular.picked?.selectedCount,
      variance:circular.variance,band:circular.inspect.bandPercent
    }));
    assert(circular.picked?.ok,'A textured circular rim must be selectable');
    assert(circular.picked.selectedCount>=8,'A geometric circle must reach multiple angular vertices');
    assert(circular.variance<.016,'Selected ring must be constant-radius in the real mesh');
    assert.equal(circular.highlighted.highlightedCount,circular.picked.selectedCount,
      'Every selected geometric circle vertex must be visibly highlighted');
    await page.waitForSelector('#se482BandRange',{state:'visible',timeout:12000});
    const inspector=await page.evaluate(()=>{
      const display=id=>{
       const node=document.getElementById(id);
       return node?getComputedStyle(node).display:null;
      };
      return {faceGuide:display('se451FaceWorkflow'),faceQuick:display('se445ShapeQuick'),
       circle:display('se482CircleControl'),ring:display('se466RingControls'),
       layout:window.SWYRL_ENGINE_RING_HEIGHT_LAYOUT_482?.inspect()};
    });
    console.log('SE482_VERTEX_INSPECTOR_'+cfg.name+' '+JSON.stringify(inspector));
    assert.equal(inspector.faceGuide,'none','Vertex mode hides Face-only guide');
    assert.equal(inspector.faceQuick,'none','Vertex mode hides Face quick tools');
    assert(inspector.circle!=='none'&&inspector.ring!=='none',
      'Vertex circle settings must be visible instead');
    await page.waitForFunction(()=>
      window.SWYRL_ENGINE_RING_HEIGHT_LAYOUT_482?.inspect()?.visible===true,
      {timeout:12000});
    const height=page.locator('#se478RingHeightSlider');
    const rect=await height.boundingBox();
    const bar=await page.locator('#se477SelectionShapes').boundingBox();
    assert(rect&&rect.width>=240&&rect.height>=115,'Ring Height should have readable mobile dimensions');
    assert(rect.y>=bar.y+bar.height-2,'Floating Ring Height should not cover selection bar');
    const moved=await page.evaluate(()=>{
      const panel=window.SWYRL_ENGINE_RING_HEIGHT_LAYOUT_482;
      const old=panel.inspect();
      panel.setPosition(old.left+55,old.top+37);
      return {old,newPosition:panel.inspect()};
    });
    assert(moved.newPosition.userMoved&&moved.newPosition.attached,
      'Ring Height panel must provide persistent movable coordinates');
    await page.screenshot({path:path.join(root,'se482-ring-controls-'+cfg.name+'.png')});
    const actual=await page.evaluate(()=>{
      const geometry=window.SWYRL_ENGINE_GEOMETRIC_RING_482;
      const native=window.SWYRL_ENGINE_MODEL_WORKSHOP;
      const slots=window.SWYRL_ENGINE_RING_HIGHLIGHT_478.inspect().selectedSlots;
      const before=geometry.sampleSlots(slots);
      const started=window.SWYRL_ENGINE_RING_HEIGHT_478.previewHeight(.18);
      const live=native.inspect().preview.active;
      const after=geometry.sampleSlots(slots);
      const cancelled=native.cancel();
      const restored=geometry.sampleSlots(slots);
      const moved=before.map((p,i)=>after?.[i]?.position?.[1]-p.position[1]);
      const revert=before.map((p,i)=>restored?.[i]?.position?.[1]-p.position[1]);
      const uvDelta=before.flatMap((p,i)=>p.uv.map((x,k)=>
       Math.abs(x-(after?.[i]?.uv?.[k]??NaN))));
      return {started,live,cancelled,moved,revert,uvDelta,vertices:slots.length};
    });
    console.log('SE482_GEOMETRY_HEIGHT_'+cfg.name+' '+JSON.stringify(actual).slice(0,1600));
    assert(actual.started.ok&&actual.live&&actual.cancelled.ok,
      'Native ring height preview and Cancel must succeed');
    assert(actual.moved.length>0&&actual.moved.some(n=>Math.abs(n-.18)<.02),
      'Preview must actually move selected surface geometry by the requested height');
    assert(actual.revert.every(n=>Math.abs(n)<.0001),
      'Cancel must restore original surface positions');
    assert(actual.uvDelta.every(n=>n<.00001),'Live height preview must not change painted UV coordinates');
    await page.locator('#se482BandRange').evaluate(el=>{
      el.value='2.0';el.dispatchEvent(new Event('input',{bubbles:true}));
      el.dispatchEvent(new Event('change',{bubbles:true}));
    });
    assert.equal((await page.evaluate(()=>
      window.SWYRL_ENGINE_GEOMETRIC_RING_482.inspect())).bandPercent,2);
    console.log('SE482_CIRCLE_UI_PASS_'+cfg.name);
    await page.locator('#se481OriginalSourceToggle').click({timeout:14000});
    const restored=await page.evaluate(()=>{
     const api=window.SWYRL_ENGINE_TEXTURED_TOPOLOGY_481;
     return {status:api.inspectSource(),fidelity:api.inspectFidelity()};
    });
    assert(!restored.status.sourceHidden&&restored.status.copyHidden,
      'Original source restores without deleting edited copy');
    assert(restored.status.sourceTexture===restored.status.copyTexture);
    await page.locator('#se481OriginalSourceToggle').click({timeout:14000});
    const resumed=await page.evaluate(()=>{
     const api=window.SWYRL_ENGINE_TEXTURED_TOPOLOGY_481;
     return {status:api.inspectSource(),fidelity:api.inspectFidelity()};
    });
    assert(resumed.status.sourceHidden&&!resumed.status.copyHidden);
    assert(resumed.fidelity.ok,'UV source and copy survive reversible visibility switch');
    assert(errors.length===0,'Unexpected browser errors '+JSON.stringify(errors.slice(0,3)));
    console.log('SE482_BROWSER_PASS_'+cfg.name);
   }finally{await page.close();}
  }
 }finally{await browser.close();await new Promise(resolve=>server.close(resolve));}
})().catch(e=>{console.error('SE482_BROWSER_FAIL',e.stack||e);process.exitCode=1;
 try{server.close();}catch{}});
