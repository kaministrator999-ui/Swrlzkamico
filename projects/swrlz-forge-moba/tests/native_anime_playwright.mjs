import {chromium} from 'playwright';
import assert from 'node:assert/strict';

const base=process.env.SWYRL_ANIME_TEST_URL||'http://127.0.0.1:8765';
const browser=await chromium.launch({
  headless:true,args:['--no-sandbox','--disable-dev-shm-usage',
    '--enable-webgl','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader']
});
let success=false;
try{
  for(const mode of [
    {name:'desktop',viewport:{width:1280,height:800},mobile:false},
    {name:'mobile',viewport:{width:390,height:844},mobile:true}
  ]){
    const ctx=await browser.newContext({viewport:mode.viewport,isMobile:mode.mobile,hasTouch:mode.mobile});
    const page=await ctx.newPage(),errors=[];
    page.on('pageerror',e=>errors.push(String(e)));
    page.on('console',m=>{if(m.type()==='error')console.log('[browser console]',m.text())});
    await page.goto(base+'/index.html?project=anime-ghosts-ep01',{waitUntil:'domcontentloaded',timeout:60000});
    await page.waitForFunction(()=>!!window.SWYRL_ENGINE_CINEMATIC,{timeout:60000});
    await page.waitForTimeout(1200);
    const project=await page.evaluate(()=>window.SWYRL_ENGINE_CINEMATIC.status().projectId);
    assert.equal(project,'ghosts-different-forms-ep01','Anime starter did not load');
    await page.evaluate(()=>document.getElementById('playBtn').click());
    await page.waitForFunction(()=>window.SWYRL_ENGINE_CINEMATIC.status().active,{timeout:15000});
    const before=await page.evaluate(()=>window.SWYRL_ENGINE_CINEMATIC.status());
    await page.waitForTimeout(1500);
    const after=await page.evaluate(()=>window.SWYRL_ENGINE_CINEMATIC.status());
    assert.ok(after.elapsed>before.elapsed+.5,mode.name+' cinema clock did not advance');
    assert.ok(after.camera&&after.camera.every(Number.isFinite),mode.name+' camera missing');
    assert.notEqual(after.camera[0],before.camera[0],mode.name+' camera did not move');
    const hud=await page.locator('#animeCineHud').isVisible();
    assert.ok(hud,mode.name+' cinematic HUD missing');
    const visual=await page.evaluate(()=>window.SWYRL_ENGINE_CINEMATIC.status());
    assert.deepEqual(Object.keys(visual.layers||{}).sort(),
      ['background','atmosphere','midground','characters','effects','foreground'].sort(),
      mode.name+' missing 2.5D layer stack');
    assert.ok(visual.celCount>=3,mode.name+' illustrated anime cels missing');
    assert.equal(await page.locator('#animeCineLayers').isVisible(),true,mode.name+' Layers UI missing');
    await page.locator('#animeCineLayers').click();
    await page.locator('input[data-anime-layer="foreground"]').uncheck();
    assert.equal((await page.evaluate(()=>window.SWYRL_ENGINE_CINEMATIC.status())).layers.foreground,false);
    await page.locator('input[data-anime-layer="foreground"]').check();
    await page.locator('#animeCineLayers').click();
    const subtitle=await page.locator('#animeCineCaption').innerText();
    assert.ok(subtitle.length>15,mode.name+' dialogue missing');
    const captionBox=await page.locator('#animeCineCaption').evaluate(el=>{
      const b=el.getBoundingClientRect();return {left:b.left,right:b.right,width:innerWidth};
    });
    assert.ok(captionBox.left>=-2&&captionBox.right<=captionBox.width+2,
      mode.name+' caption overflows horizontally');
    const seek=await page.evaluate(()=>window.SWYRL_ENGINE_CINEMATIC.seek(72));
    assert.equal(seek,true);
    const stage=await page.evaluate(()=>window.SWYRL_ENGINE_CINEMATIC.status().stage);
    assert.equal(stage,4,mode.name+' scene seeking failed');
    const stageCaption=await page.locator('#animeCineCaption').innerText();
    assert.ok(/DRAGON|KAMI/.test(stageCaption),mode.name+' authored cue missing');
    await page.locator('#animeCinePause').click();
    const t1=await page.evaluate(()=>window.SWYRL_ENGINE_CINEMATIC.status().elapsed);
    await page.waitForTimeout(450);
    const t2=await page.evaluate(()=>window.SWYRL_ENGINE_CINEMATIC.status().elapsed);
    assert.ok(Math.abs(t2-t1)<.12,mode.name+' paused clock advanced unexpectedly');
    await page.locator('#animeCineExplore').click();
    const explore=await page.evaluate(()=>window.SWYRL_ENGINE_CINEMATIC.status());
    assert.equal(explore.active,false,mode.name+' cinematic did not release');
    assert.equal(explore.playing,true,mode.name+' did not enter first-person exploration');
    await page.evaluate(()=>document.getElementById('stopBtn').click());
    const stop=await page.evaluate(()=>window.SWYRL_ENGINE_CINEMATIC.status());
    assert.equal(stop.playing,false,mode.name+' Stop failed');
    assert.equal(errors.length,0,mode.name+' unhandled browser errors: '+errors.join('\n'));
    console.log('NATIVE_ANIME_'+mode.name.toUpperCase()+'_PASS',JSON.stringify({elapsed:after.elapsed,stage,subtitle:subtitle.slice(0,60)}));
    await page.screenshot({path:'native-anime-'+mode.name+'.png',fullPage:false});
    await ctx.close();
  }
  success=true;
}finally{
  await browser.close();
}
if(success)console.log('NATIVE_ANIME_BOTH_VIEWPORTS_PASSED');
