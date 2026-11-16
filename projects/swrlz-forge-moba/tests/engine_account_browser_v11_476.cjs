'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),http=require('node:http');
const {chromium}=require('playwright');
const root=path.resolve(process.argv[2]||'projects/swrlz-forge-moba/_release_v11_476_candidate');
const mime={'.html':'text/html; charset=utf-8','.js':'text/javascript','.css':'text/css',
 '.json':'application/json','.png':'image/png','.jpg':'image/jpeg','.webp':'image/webp','.svg':'image/svg+xml'};
const server=http.createServer((req,res)=>{
 let url;try{url=decodeURIComponent(new URL(req.url,'http://localhost').pathname);}catch{res.writeHead(400).end();return;}
 const name=path.resolve(root,'.'+url);
 if(!name.startsWith(root+path.sep)||!fs.existsSync(name)||!fs.statSync(name).isFile()){
  res.writeHead(404).end('not found');return;
 }
 res.writeHead(200,{'content-type':mime[path.extname(name).toLowerCase()]||'application/octet-stream'});
 fs.createReadStream(name).pipe(res);
});
(async()=>{
 await new Promise(r=>server.listen(0,'127.0.0.1',r));
 const browser=await chromium.launch({headless:true,args:['--no-sandbox','--enable-unsafe-swiftshader']});
 try{
  for(const p of [{name:'mobile',width:412,height:915},{name:'desktop-site',width:980,height:780}]){
   const page=await browser.newPage({viewport:{width:p.width,height:p.height},
    isMobile:true,hasTouch:true,deviceScaleFactor:2,reducedMotion:'reduce'});
   const errors=[];
   page.on('pageerror',e=>errors.push(String(e)));
   await page.addInitScript(()=>{
    const native=window.setTimeout;
    window.setTimeout=function(fn,ms,...args){return native.call(window,fn,ms===16000?180:ms,...args);};
   });
   try{
    await page.goto('http://127.0.0.1:'+server.address().port+'/index.html',
     {waitUntil:'domcontentloaded',timeout:45000});
    await page.waitForSelector('#se476StartupGate',{state:'visible',timeout:25000});
    await page.waitForFunction(()=>!!window.SWYRL_ENGINE_STARTUP_476?.inspect?.()?.ready,{timeout:30000});
    const before=await page.evaluate(()=>{
      const gate=document.getElementById('se476StartupGate');
      const sel=document.getElementById('se476Projects');
      return {visible:!gate.hidden,hasLogin:!!document.getElementById('se476SignIn'),
       hasSavedProjects:!!sel,hasCheckbox:!!document.getElementById('se476Remember'),
       controller:window.SWYRL_ENGINE_STARTUP_476?.inspect?.()};
    });
    assert(before.visible&&before.hasLogin&&before.hasSavedProjects&&before.hasCheckbox,
      'Account-first gate must cover editor with real controls');
    await page.waitForFunction(()=>document.getElementById('se476SignalLost')?.hidden===false,{timeout:8000});
    const outage=await page.evaluate(()=>{
      const root=document.getElementById('se476SignalLost');
      const r=root.getBoundingClientRect();
      return {fullScreen:Math.abs(r.width-innerWidth)<5&&Math.abs(r.height-innerHeight)<5,
       display:getComputedStyle(root).display,heading:root.querySelector('h2')?.textContent,
       buttons:[...root.querySelectorAll('button')].map(b=>b.textContent.trim()),
       reducedMotion:matchMedia('(prefers-reduced-motion: reduce)').matches};
    });
    assert(outage.fullScreen&&outage.display!=='none','Downtime state must fill viewport');
    assert(outage.buttons.some(b=>b.includes('Reconnect')),'Retry button required');
    assert(outage.buttons.some(b=>b.includes('offline')),'Offline continue required');
    assert(outage.reducedMotion,'Should honor device reduced-motion preference');
    console.log('SE476_PAGE_DOWN_'+p.name+' '+JSON.stringify(outage));
    await page.screenshot({path:path.join(root,'se476-page-down-'+p.name+'.png')});
    await page.waitForFunction(()=>!document.getElementById('seReleaseNotesDialog')?.open,{timeout:5000});
    const notesClosed=await page.evaluate(()=>!document.getElementById('seReleaseNotesDialog')?.open);
    assert(notesClosed,'Native release notes must not intercept first-paint account or Page Down actions');
    await page.locator('#se476OfflineContinue').click({timeout:20000});
    await page.waitForFunction(()=>document.getElementById('se476StartupGate')?.hidden===true,{timeout:12000});
    const after=await page.evaluate(()=>window.SWYRL_ENGINE_STARTUP_476.inspect());
    assert(after.finished===true,'Continue offline must open editor, not trap the user');
    assert(errors.length===0,'Browser errors: '+JSON.stringify(errors.slice(0,3)));
    console.log('SE476_BROWSER_PASS_'+p.name+' '+JSON.stringify({finished:after.finished,account:after.account}));
   }finally{await page.close();}
  }
 }finally{await browser.close();await new Promise(r=>server.close(r));}
})().catch(e=>{console.error('SE476_BROWSER_FAIL',e.stack||e);process.exitCode=1;try{server.close();}catch{}});
