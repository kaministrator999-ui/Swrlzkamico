import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';

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
    // First-run WebGL texture uploads may briefly stall software-rendered CI;
    // require the clock to progress through actual rendered frames, not simply
    // one arbitrary 1500 ms wall-time window.
    await page.waitForFunction(baseline=>window.SWYRL_ENGINE_CINEMATIC.status().elapsed>baseline+.5,
      before.elapsed,{timeout:15000});
    const after=await page.evaluate(()=>window.SWYRL_ENGINE_CINEMATIC.status());
    assert.ok(after.elapsed>before.elapsed+.5,mode.name+' cinema clock did not advance');
    assert.ok(after.camera&&after.camera.every(Number.isFinite),mode.name+' camera missing');
    assert.notEqual(after.camera[0],before.camera[0],mode.name+' camera did not move');
    const hud=await page.locator('#animeCineHud').isVisible();
    assert.ok(hud,mode.name+' cinematic HUD missing');
    const visual=await page.evaluate(()=>window.SWYRL_ENGINE_CINEMATIC.status());
    assert.deepEqual(Object.keys(visual.layers||{}).sort(),
      ['background','atmosphere','midground','characters','kami','swyrlz','guardian','effects','foreground'].sort(),
      mode.name+' missing 2.5D layer stack');
    assert.ok(visual.celCount>=3,mode.name+' illustrated anime cels missing');
    assert.equal(await page.locator('#animeCineLayers').isVisible(),true,mode.name+' Layers UI missing');
    await page.locator('#animeCineLayers').click();
    await page.locator('input[data-anime-layer="foreground"]').uncheck();
    assert.equal((await page.evaluate(()=>window.SWYRL_ENGINE_CINEMATIC.status())).layers.foreground,false);
    await page.locator('input[data-anime-layer="foreground"]').check();
    await page.locator('#animeCineLayers').click();
    const setPopUp=await page.evaluate(()=>window.SWYRL_ENGINE_CINEMATIC.setPopUp('swyrlz','offsetX',-2.7));
    assert.equal(setPopUp,true,mode.name+' Director cannot edit independent §wyrlz cel');
    assert.equal((await page.evaluate(()=>window.SWYRL_ENGINE_CINEMATIC.director())).layers.swyrlz.offsetX,-2.7);
    assert.equal(await page.locator('#animeDirectorBtn').isVisible(),true,mode.name+' editor Director control missing');
    assert.equal(await page.locator('#animeCineHud #animeDirectorBtn').count(),1,
      mode.name+' Director did not dock inside live cinematic controls');
    await page.locator('#animeDirectorBtn').click();
    assert.equal(await page.locator('#animeDirectorPanel').isVisible(),true,mode.name+' Director missing');
    await page.locator('#animeDirectorLayer').selectOption('kami');
    await page.locator('input[data-pop-field="delay"]').evaluate(input=>{input.value='2.25';input.dispatchEvent(new Event('input',{bubbles:true}))});
    assert.equal((await page.evaluate(()=>window.SWYRL_ENGINE_CINEMATIC.director())).layers.kami.delay,2.25);
    await page.locator('#animeDirectorDone').click();
    // Unlike a flat background, each scenery plane unfolds from its own hinge.
    const pop=await page.evaluate(()=>window.SWYRL_ENGINE_CINEMATIC.popUpStatus());
    assert.ok(pop.bookCount>=1&&pop.hinges>=5,mode.name+' storybook does not have physical pop-up planes');
    assert.ok(pop.characterCels.kami>=1&&pop.characterCels.swyrlz>=1,mode.name+' distinct character layers missing');
    assert.ok(pop.sceneZ.background<pop.sceneZ.midground&&pop.sceneZ.midground<pop.sceneZ.foreground,
      mode.name+' pop-up book lacks depth separation');
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
    // Director parameters must survive a real downloadable editor Save Project.
    const downloadPending=page.waitForEvent('download',{timeout:15000});
    await page.locator('#saveBtn').click();
    const download=await downloadPending;
    const saved=JSON.parse(await readFile(await download.path(),'utf8'));
    assert.equal(saved.project?.animePopUp?.schema,'anime-popup-v1',
      mode.name+' director state missing from exported project');
    assert.equal(saved.project.animePopUp.layers.kami.delay,2.25,
      mode.name+' Kami cel timing not saved');
    assert.equal(saved.project.animePopUp.layers.swyrlz.offsetX,-2.7,
      mode.name+' §wyrlz cel staging not saved');
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
