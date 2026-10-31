// Focused first-paint browser check: no engine-module JS is required.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const {chromium}=require('playwright');
(async()=>{
 const source=fs.readFileSync(process.env.SE186_HTML||'/tmp/se186-package/index.html','utf8');
 const body=source.search(/<body\b/i);
 const start=source.indexOf('data-se186-early');
 const earlyScript=source.indexOf('<script id="se186StartupBeforeEngine">');
 const engine=source.indexOf('window.SWRLZ_FORGE_BUILD=');
 assert(body>=0&&start>body&&earlyScript>start&&engine>earlyScript,'Startup markup and script must be ahead of engine module');
 const close=source.indexOf('</script>',earlyScript);
 assert(close>earlyScript);
 const firstPaintDocument=source.slice(0,close+9)+'\n</body></html>';
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 try{
  for(const width of [390,980]){
   const page=await browser.newPage({viewport:{width,height:844},reducedMotion:'no-preference'});
   await page.setContent(firstPaintDocument,{waitUntil:'domcontentloaded'});
   const state=await page.evaluate(()=>{
    const splash=document.getElementById('se185Init');
    const halo=document.querySelector('.se185-halo');
    const dots=document.querySelectorAll('.se185-particles i');
    const css=window.getComputedStyle(dots[0]);
    const bounds=halo.getBoundingClientRect();
    return {
      mounted:!!splash,early:window.SWYRL_ENGINE_EARLY_SPLASH===true,
      visible:!!splash&&getComputedStyle(splash).visibility==='visible',
      particles:dots.length,animation:css.animationName,
      haloX:Math.round(bounds.x),haloWidth:Math.round(bounds.width),
      text:splash?.textContent||''
    };
   });
   assert(state.mounted&&state.early&&state.visible,state);
   assert.equal(state.particles,32);
   assert(state.animation.includes('se185Fragment'),state);
   assert(state.haloX>=0&&state.haloX+state.haloWidth<=width,state);
   assert(state.text.includes('§wyrl§ ENGINE')&&state.text.includes('GLITCH · WISP'),state);
   await page.evaluate(()=>document.documentElement.classList.add('se127-editor-ready'));
   await page.waitForTimeout(850);
   assert.equal(await page.locator('#se185Init').evaluate(e=>getComputedStyle(e).visibility),'hidden');
   console.log('SE186_FIRST_PAINT_PASS',JSON.stringify({width,...state}));
   await page.close();
  }
  const reduced=await browser.newPage({viewport:{width:390,height:844},reducedMotion:'reduce'});
  await reduced.setContent(firstPaintDocument,{waitUntil:'domcontentloaded'});
  const anim=await reduced.locator('.se185-ring-a').evaluate(e=>getComputedStyle(e).animationName);
  assert.equal(anim,'none');
  console.log('SE186_REDUCED_MOTION_PASS');
  await reduced.close();
 }finally{await browser.close()}
})().catch(error=>{console.error(error);process.exitCode=1});
