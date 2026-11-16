'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const http=require('node:http');
const {chromium}=require('playwright');
const root=path.resolve(process.argv[2]||'projects/swrlz-forge-moba/_release_v11_475_candidate');
const mime={'.html':'text/html; charset=utf-8','.js':'text/javascript','.css':'text/css','.json':'application/json',
 '.png':'image/png','.jpg':'image/jpeg','.jpeg':'image/jpeg','.webp':'image/webp','.svg':'image/svg+xml'};
const server=http.createServer((req,res)=>{
 let name;try{name=decodeURIComponent(new URL(req.url,'http://localhost').pathname)}catch{res.writeHead(400).end();return;}
 const file=path.resolve(root,'.'+name);
 if(!file.startsWith(root+path.sep)||!fs.existsSync(file)||!fs.statSync(file).isFile()){
  res.writeHead(404).end('not found');return;
 }
 res.writeHead(200,{'content-type':mime[path.extname(file).toLowerCase()]||'application/octet-stream'});
 fs.createReadStream(file).pipe(res);
});
async function run(){
 await new Promise(r=>server.listen(0,'127.0.0.1',r));
 const port=server.address().port,host='http://127.0.0.1:'+port;
 const browser=await chromium.launch({headless:true,args:['--no-sandbox','--enable-unsafe-swiftshader']});
 try{
  for(const cfg of [
   {name:'touch-desktop-layout',width:980,height:780},
   {name:'compact-mobile-layout',width:412,height:915}
  ]){
   const page=await browser.newPage({
    viewport:{width:cfg.width,height:cfg.height},
    isMobile:true,hasTouch:true,deviceScaleFactor:2
   });
   const errors=[];
   page.on('pageerror',e=>errors.push(e.stack||String(e)));
   try{
    await page.goto(host+'/modeler.html',{waitUntil:'domcontentloaded',timeout:45000});
    await page.waitForSelector('#modelAtelierToolRail',{state:'attached',timeout:25000});
    await page.evaluate(()=>document.querySelector('#seReleaseNotesDialog[open]')?.close?.());
    await page.waitForFunction(()=>!!window.SWYRL_ENGINE_PROGRESSIVE_RAIL_475?.inspect?.()?.mounted,{timeout:25000});
    const rail=page.locator('#modelAtelierToolRail');
    const category=rail.locator(':scope > button').filter({hasText:/^Sculpt$/}).first();
    await category.click({timeout:15000});
    await page.waitForFunction(()=>window.SWYRL_ENGINE_PROGRESSIVE_TOOLS_474?.inspect?.()?.family==='Sculpt',
     {timeout:12000});
    const initial=await page.evaluate(()=>{
     const el=id=>document.getElementById(id);
     const p=el('modelAtelierPanel'),bar=el('se474ToolFlyout'),rail=el('modelAtelierToolRail');
     const r=e=>{const box=e?.getBoundingClientRect();return box&&{x:box.x,y:box.y,width:box.width,height:box.height,right:box.right,bottom:box.bottom};};
     const sculpt=[...rail.querySelectorAll(':scope > button')].find(b=>b.textContent.trim()==='Sculpt');
     const meshes=[...rail.querySelectorAll(':scope > button')].find(b=>b.textContent.trim()==='Meshes');
     return {layout:p.dataset.se251Layout,
      progressive:window.SWYRL_ENGINE_PROGRESSIVE_RAIL_475?.inspect?.(),
      native:window.SWYRL_ENGINE_PROGRESSIVE_TOOLS_474?.inspect?.(),
      flyout:r(bar),rail:r(rail),sculpt:r(sculpt),
      barParent:bar?.parentElement?.className,
      flyoutDisplay:bar&&getComputedStyle(bar).display,flyoutHidden:bar?.hidden,
      sculptPressed:sculpt?.getAttribute('aria-pressed'),meshesPressed:meshes?.getAttribute('aria-pressed')};
    });
    console.log('SE475_BROWSER_SCULPT_'+cfg.name+' '+JSON.stringify(initial));
    assert.equal(initial.native.family,'Sculpt');
    assert.equal(initial.progressive.flyoutInBody,true,'Tool choices must not be clipped by scrolling rail');
    assert.equal(initial.progressive.flyoutVisible,true);
    assert.equal(initial.sculptPressed,'true');
    assert.equal(initial.meshesPressed,'false');
    assert(initial.flyout&&initial.flyout.width>110&&initial.flyout.height>80,'Visible actual tool flyout');
    assert(initial.flyoutDisplay!=='none'&&!initial.flyoutHidden);
    if(initial.layout!=='compact')assert(initial.flyout.right<=initial.rail.x+5,'Flyout should be LEFT of right-side rail');
    await page.locator('#se474ToolFlyout button[data-se474-value="Vertex"]').click({timeout:15000});
    await page.waitForFunction(()=>window.SWYRL_ENGINE_PROGRESSIVE_TOOLS_474?.inspect?.()?.tool==='Vertex',
     {timeout:12000});
    const after=await page.evaluate(()=>{
      const top=document.querySelector('#se474SpecificModes');
      const trans=document.querySelector('#se320ModelTransform');
      const scene=document.querySelector('#modelAtelierPanel .atelier-scene');
      const rect=n=>{const r=n?.getBoundingClientRect();return r&&{x:r.x,y:r.y,width:r.width,height:r.height,right:r.right,bottom:r.bottom};};
      return {native:window.SWYRL_ENGINE_PROGRESSIVE_TOOLS_474.inspect(),
       progressive:window.SWYRL_ENGINE_PROGRESSIVE_RAIL_475.inspect(),
       top:rect(top),trans:rect(trans),scene:rect(scene),hidden:top.hidden,
       computed:getComputedStyle(top).display,
       modes:[...top.querySelectorAll('button')].map(x=>x.textContent.trim())};
    });
    console.log('SE475_BROWSER_VERTEX_'+cfg.name+' '+JSON.stringify(after));
    assert.equal(after.native.tool,'Vertex');
    assert.equal(after.progressive.modesVisible,true);
    assert(after.modes.includes('Ring fill')&&after.modes.includes('Vertex ring'));
    assert(!after.hidden&&after.computed!=='none'&&after.top.width>130);
    assert(after.top.x>=after.scene.x-4&&after.top.right<=after.scene.right+6,'Top modes stay inside model viewport');
    if(after.trans&&after.trans.height>0)
     assert(after.top.y>=after.trans.bottom-3,'Top modes should not overlap transform bar');
    await page.screenshot({path:path.join(root,'se475-'+cfg.name+'.png')});
    await page.locator('#se474SpecificModes button[data-se474-value="fill"]').click({timeout:12000});
    await page.waitForFunction(()=>window.SWYRL_ENGINE_PROGRESSIVE_TOOLS_474?.inspect?.()?.mode==='fill',
     {timeout:10000});
    const selected=await page.evaluate(()=>({
     state:window.SWYRL_ENGINE_PROGRESSIVE_TOOLS_474.inspect(),
     settings:document.getElementById('modelAtelierPanel').dataset.se474SettingsOpen
    }));
    assert.equal(selected.state.mode,'fill');
    assert.equal(selected.settings,'true');
    const ringRuntime=await page.evaluate(()=>{
     const entries=[...document.scripts].map((node,index)=>({
      index,code:node.textContent||''
     })).filter(e=>e.code.includes('se466RingUIInstall'));
     return {
      ringPanel:!!document.getElementById('se466RingControls'),
      native:!!window.SWYRL_ENGINE_MODEL_WORKSHOP?.selectRing,
      fnType:typeof se466RingUIInstall,
      bridgeType:typeof window.SWYRL_ENGINE_RING_UI_INSTALL_475,
      scripts:entries.map(e=>{
       const a=e.code.indexOf('function se466RingUIInstall');
       const b=e.code.indexOf('se430BeginnerInstall(panel);se466RingUIInstall(panel);');
       return {index:e.index,length:e.code.length,functionOffset:a,callOffset:b,
        beforeFunction:a>=0?e.code.slice(a-210,a+130):null,
        beforeCall:b>=0?e.code.slice(b-180,b+100):null};
      })
     };
    });
    console.log('SE475_RING_SCOPE_'+cfg.name+' '+JSON.stringify(ringRuntime));
    assert.equal(ringRuntime.bridgeType,'function','Ring installer must be exported from ModelAtelier scope');
    assert.equal(ringRuntime.ringPanel,true,'Actual native ring settings panel must install');
    assert(errors.length===0,'Browser page errors '+JSON.stringify(errors.slice(0,4)));
    console.log('SE475_BROWSER_PASS_'+cfg.name);
   }finally{await page.close();}
  }
 }finally{await browser.close();await new Promise(r=>server.close(r));}
}
run().catch(err=>{console.error('SE475_BROWSER_FAIL',err.stack||err);process.exitCode=1;server.close();});
