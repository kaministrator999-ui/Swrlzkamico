import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {mkdir,writeFile} from 'node:fs/promises';
import {resolve} from 'node:path';
import {createHash} from 'node:crypto';

// Tap the native Watch controls and drive the actual engine RAF, Three.Clock,
// timeline, geometry and renderer. Fixed 50 ms frames make signed-rate checks
// independent of software WebGL frame times; no production functions are mocked.
// Preserve the published full-staff editor fixture for this compatibility suite.
// The new starter has its own acceptance suite; all original authored-key,
// geometry, facial, socket and transport assertions below remain unchanged.
async function loadHistoricalEpisode(page){
  assert.equal(await page.evaluate(()=>window.SWYRL_ENGINE_ANIMATION.status().playing),false,
    'Historical episode must load into a stopped native editor');
  const imported=await page.evaluate(async()=>{
    const response=await fetch('scenes/ghosts-in-different-forms-ep01-full-staff.swyrl.json');
    if(!response.ok)throw new Error('Preserved full-staff native scene is missing');
    return window.SWYRL_ENGINE_STORYBOARD.importProject(await response.json());
  });
  assert.equal(imported,true,'Preserved full-staff native project import failed');
  await page.waitForFunction(()=>{
    const state=window.SWYRL_ENGINE_STORYBOARD.stageStatus();
    return state.assetsReady||state.assetErrors?.length;
  },undefined,{timeout:45000,polling:100});
}

const base=(process.env.SWYRL_ANIME_TEST_URL||'http://127.0.0.1:8765').replace(/\/$/,'');
const query=new URLSearchParams(process.env.SWYRL_ANIME_TEST_QUERY||'');
query.set('project','anime-ghosts-ep01');
const output=resolve(process.env.SWYRL_ANIME_SCREENSHOTS_DIR||'episode-transport-acceptance');
await mkdir(output,{recursive:true});
const modes=[
  {name:'desktop',viewport:{width:1440,height:900},isMobile:false,hasTouch:false},
  {name:'mobile',viewport:{width:390,height:844},isMobile:true,hasTouch:true}
].filter(mode=>!process.env.SWYRL_ANIME_TEST_MODE||process.env.SWYRL_ANIME_TEST_MODE===mode.name);
assert.ok(modes.length,'SWYRL_ANIME_TEST_MODE must be desktop or mobile');
const browser=await chromium.launch({headless:true,
  ...(process.env.SWYRL_CHROMIUM_PATH?{executablePath:process.env.SWYRL_CHROMIUM_PATH}:{}),
  args:['--no-sandbox','--disable-dev-shm-usage','--enable-webgl',
    '--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader']});
const receipts=[];
const touchPages=new WeakSet();
const state=page=>page.evaluate(()=>window.SWYRL_ENGINE_TRANSPORT.status());
const animation=page=>page.evaluate(()=>window.SWYRL_ENGINE_ANIMATION.status());
const project=page=>page.evaluate(()=>window.SWYRL_ENGINE_ANIMATION.serializedProject());
const frames=(page,count=1,ms=50)=>page.evaluate(({count,ms})=>window.__episodeTestClock.step(count,ms),{count,ms});
const close=(actual,expected,label,tolerance=1e-6)=>assert.ok(Number.isFinite(actual)&&Math.abs(actual-expected)<=tolerance,
  label+': expected '+expected+', received '+actual);
const cleanScene=saved=>({background:saved.scene.background,layers:saved.editor.layers,
  actors:saved.scene.actors.map(actor=>({id:actor.id,type:actor.type,position:actor.position,
    rotation:actor.rotation,scale:actor.scale,manualVisible:actor.manualVisible,editorLayerIds:actor.editorLayerIds}))});
async function tap(page,id){
  const button=page.locator('#'+id);
  assert.equal(await button.isVisible(),true,'Transport control is not visible: '+id);
  // A paused test RAF cannot satisfy Playwright's two-frame stability wait.
  // These remain actual mouse/touch pointer events on the visible button.
  if(touchPages.has(page))await button.tap({force:true});
  else await button.click({force:true});
}
async function scrub(page,time){
  await page.locator('#animeCineScrub').evaluate((input,time)=>{
    input.value=String(time);input.dispatchEvent(new Event('input',{bubbles:true}));
  },time);
  close((await state(page)).elapsed,time,'Visible seek slider did not seek');
}
async function assertRate(page,rate,label){
  const s=await state(page);close(s.rate,rate,label+' signed rate');
  assert.equal(s.active,true,label+' lost native cinema');
  const rewind=page.locator('#animeCineRewind'),forward=page.locator('#animeCineFastForward');
  assert.equal(await rewind.getAttribute('aria-pressed'),String(rate<0),label+' rewind pressed state');
  assert.equal(await forward.getAttribute('aria-pressed'),String(rate>1),label+' forward pressed state');
  assert.match(await page.locator('#animeCineRate').innerText(),new RegExp(String(Math.abs(rate))+'\\s*[×x]'),label+' speed is not visible');
  if(rate<0)assert.match(await page.locator('#animeCineRate').innerText(),/rewind|◀|⏪/i,label+' reverse direction is not visible');
  return s;
}
async function rateFrames(page,rate,label){
  const before=await assertRate(page,rate,label);
  assert.equal(before.paused,false,label+' did not start playback');
  await frames(page,3);
  const after=await state(page);
  close(after.elapsed-before.elapsed,rate*.15,label+' actual Three.Clock progression');
  close(after.rate,rate,label+' rate changed during rendering');
  return {rate,before:before.elapsed,after:after.elapsed};
}
async function frozenScene(page){
  return page.evaluate(()=>{
    const stage=window.SWYRL_ENGINE_STORYBOARD.stageStatus();
    const emergence=window.SWYRL_ENGINE_EMERGENCE.status();
    const rigs=Object.fromEntries(['kami','swyrlz'].map(character=>{
      const rig=window.SWYRL_ENGINE_RIG.renderStatus(character);
      return [character,{joints:rig.joints,bounds:rig.bounds,
        face:Object.fromEntries(['expression','blink','mouth','speech','brow'].map(key=>[key,rig.face[key]])),
        connections:rig.connections.map(c=>({child:c.child,error:c.error,parentSocketWorld:c.parentSocketWorld,
          childAttachWorld:c.childAttachWorld}))}];
    }));
    return {camera:stage.camera,cast:stage.castBounds,scenery:stage.scenery,book:stage.bookBounds,
      staffMagic:stage.staffMagic,emergence,rigs,hud:{
        caption:document.getElementById('animeCineCaption').textContent,
        title:document.getElementById('animeCineScene').textContent,
        chapter:[...document.querySelectorAll('#storyCinemaChapters button')].map(button=>button.getAttribute('aria-current'))}};
  });
}
async function canvasPixels(page){
  const data=await page.evaluate(()=>{
    // Read the real WebGL drawing buffer in the same task as a paused render.
    // A page clip also captures the overlaid HUD and its touch hover states.
    window.__episodeTestClock.step(1,50);
    return document.querySelector('#storyCinemaStage canvas').toDataURL('image/png');
  });
  return Buffer.from(data.split(',')[1],'base64');
}
async function backwardsFrame(page,time,mode){
  // Enter the frame by actual rewind, then compare it to native direct seeking.
  await scrub(page,time+.4);
  if((await state(page)).rate!==1){
    // Clicking the opposite direction selects 2x before entering rewind 2x.
    if((await state(page)).rate<0)await tap(page,'animeCineFastForward');
  }
  await tap(page,'animeCineRewind');
  await assertRate(page,-2,'backwards '+time+'s');
  await frames(page,4);
  await tap(page,'animeCinePause');
  const exact=(await state(page)).elapsed;close(exact,time,'Rewind did not enter target story frame');
  await frames(page,2);
  const reversed=await frozenScene(page),stage=await page.evaluate(()=>window.SWYRL_ENGINE_STORYBOARD.stageStatus());
  assert.equal(stage.assetsReady,true,'Backward rendering has missing artwork');
  assert.deepEqual(stage.assetErrors,[],'Backward rendering has failed artwork');
  assert.ok(stage.camera.position.every(Number.isFinite),'Backward rendering has invalid camera');
  for(const rig of Object.values(reversed.rigs))for(const c of rig.connections)
    assert.ok(c.error<1e-5,'Rewind detached a body piece: '+c.child);
  const backward=await canvasPixels(page);
  assert.ok(backward.length>20000,'Backwards frame rendered an empty scene');
  await writeFile(resolve(output,mode+'-rewind-'+time+'.png'),backward);
  await scrub(page,72);await frames(page,2);
  await page.evaluate(time=>window.SWYRL_ENGINE_ANIMATION.seek(time),exact);
  await frames(page,2);
  assert.deepEqual(await frozenScene(page),reversed,'Rewind differs from authored frame geometry at '+time+'s');
  const direct=await canvasPixels(page);
  assert.equal(createHash('sha256').update(direct).digest('hex'),createHash('sha256').update(backward).digest('hex'),
    'Rewind does not reconstruct the same actual WebGL pixels as a native seek at '+time+'s');
  return {time:exact,pngSha256:createHash('sha256').update(backward).digest('hex'),bytes:backward.length};
}
try{
  for(const mode of modes){
    const context=await browser.newContext({viewport:mode.viewport,isMobile:mode.isMobile,hasTouch:mode.hasTouch});
    await context.addInitScript(()=>{
      const nativeRAF=window.requestAnimationFrame.bind(window),nativeCancel=window.cancelAnimationFrame.bind(window);
      const nativeNow=performance.now.bind(performance),queue=new Map();
      let frozen=false,now=0,next=1000000000;
      Object.defineProperty(performance,'now',{configurable:true,value:()=>frozen?now:nativeNow()});
      window.requestAnimationFrame=callback=>{
        if(!frozen)return nativeRAF(callback);
        const id=next++;queue.set(id,callback);return id;
      };
      window.cancelAnimationFrame=id=>{queue.delete(id);nativeCancel(id);};
      window.__episodeTestClock={
        freeze:()=>{frozen=true;now=nativeNow();return new Promise(resolve=>nativeRAF(()=>nativeRAF(resolve)));},
        step:(count,ms)=>{
          if(!frozen)throw new Error('The test frame clock is not frozen');
          for(let i=0;i<count;i++){
            now+=ms;const pending=[...queue.values()];queue.clear();
            if(!pending.length)throw new Error('No actual engine RAF callbacks remain');
            for(const callback of pending)callback(now);
          }
          return {now,pending:queue.size};
        }
      };
    });
    const page=await context.newPage(),errors=[];
    if(mode.hasTouch)touchPages.add(page);
    page.on('pageerror',error=>errors.push(String(error)));
    page.setDefaultTimeout(30000);
    await page.goto(base+'/index.html?'+query,{waitUntil:'domcontentloaded',timeout:60000});
    await page.waitForFunction(()=>window.SWYRL_ENGINE_TRANSPORT&&window.SWYRL_ENGINE_ANIMATION?.status().projectId==='ghosts-different-forms-ep01',undefined,{timeout:60000});
    await loadHistoricalEpisode(page);
    // Compare story frames at the same native resolution. Auto graphics may
    // adapt the drawing buffer during the deliberately slow fixed test RAF.
    await page.locator('#perfPreset').selectOption('medium',{force:true});
    const initial=await project(page);
    await page.locator('#animeScreeningBtn').click();
    await page.waitForFunction(()=>window.SWYRL_ENGINE_SCREENING.status().open&&window.SWYRL_ENGINE_STORYBOARD.stageStatus().assetsReady&&
      window.SWYRL_ENGINE_RIG.renderStatus('kami').staffGrip?.fullStaff?.ready,undefined,{timeout:60000});
    await page.evaluate(()=>window.__episodeTestClock.freeze());
    await frames(page,2); // Drain the real clock's initial half-frame once.
    await assertRate(page,1,'new Watch session');
    assert.equal(await page.locator('#storyCinemaStage canvas').count(),1,'Watch did not retain the native renderer');
    assert.equal(await page.locator('#animeCineHud .anime-episode-transport').count(),1,'Episode transport is duplicated');
    const ids=await page.locator('.anime-episode-transport').evaluate(group=>[...group.querySelectorAll('button')].map(button=>button.id));
    assert.deepEqual(ids,['animeCinePrev','animeCineRewind','animeCinePause','animeCineFastForward','animeCineNext'],
      'Shuttle buttons are not beside the existing previous/next controls');
    const metrics=await page.locator('.anime-episode-transport').evaluate(group=>{
      const nodes=[...group.querySelectorAll('button')];return nodes.map(button=>{
        const r=button.getBoundingClientRect();return {id:button.id,left:r.left,right:r.right,top:r.top,bottom:r.bottom,
          width:r.width,height:r.height,viewportWidth:innerWidth,viewportHeight:innerHeight};});
    });
    for(const r of metrics){
      assert.ok(r.left>=0&&r.right<=r.viewportWidth+1&&r.top>=0&&r.bottom<=r.viewportHeight+1,'Phone/desktop transport overflows: '+JSON.stringify(r));
      assert.ok(r.width>=31&&r.height>=28,'Transport button is too small to tap: '+r.id);
    }
    assert.ok(Math.max(...metrics.map(r=>r.top))-Math.min(...metrics.map(r=>r.top))<2,'Playback buttons wrap away from their skip controls');
    await scrub(page,40);
    const deltas=[];
    for(const rate of [2,4,8,1]){await tap(page,'animeCineFastForward');deltas.push(await rateFrames(page,rate,'forward '+rate+'x'));}
    for(const rate of [-2,-4,-8,1]){await tap(page,'animeCineRewind');deltas.push(await rateFrames(page,rate,'reverse '+rate+'x'));}

    await tap(page,'animeCineRewind');await tap(page,'animeCineRewind');
    await assertRate(page,-4,'pause reverse');await tap(page,'animeCinePause');
    const pausedTime=(await state(page)).elapsed;
    await frames(page,5);close((await state(page)).elapsed,pausedTime,'Pause advanced the reverse clock');
    close((await state(page)).rate,-4,'Pause discarded reverse speed');
    await scrub(page,75);assert.equal((await state(page)).paused,true,'Paused scrubbing resumed playback');
    await tap(page,'animeCinePause');deltas.push(await rateFrames(page,-4,'resume reverse'));
    await tap(page,'animeCineFastForward');deltas.push(await rateFrames(page,2,'switch reverse to forward'));
    await tap(page,'animeCinePause');await tap(page,'animeCineFastForward');
    deltas.push(await rateFrames(page,4,'choose fast-forward while paused'));

    const model=await page.evaluate(()=>window.SWYRL_ENGINE_ANIMATION.getTimeline());
    await tap(page,'animeCineRewind');await tap(page,'animeCineRewind');
    await scrub(page,75);await assertRate(page,-4,'seek during rewind');
    assert.equal((await state(page)).paused,false,'Running seek paused shuttle playback');
    await tap(page,'animeCinePrev');close((await state(page)).elapsed,[...model.beats].reverse().find(beat=>beat.time<74.75).time,'Previous scene');
    await assertRate(page,-4,'previous scene retains rewind');
    const beforeNext=(await state(page)).elapsed;
    await tap(page,'animeCineNext');close((await state(page)).elapsed,model.beats.find(beat=>beat.time>beforeNext+.25).time,'Next scene');
    await assertRate(page,-4,'next scene retains rewind');
    await page.locator('#storyCinemaChapters button').nth(3).click({force:true});
    close((await state(page)).elapsed,model.beats[3].time,'Chapter selection');
    await assertRate(page,-4,'chapter retains rewind');

    await tap(page,'animeCineRewind');await assertRate(page,-8,'zero boundary setup');await scrub(page,.2);
    await frames(page,1);let bound=await state(page);
    close(bound.elapsed,0,'Rewind went below zero');close(bound.rate,1,'Rewind boundary did not reset to normal');
    assert.equal(bound.paused,true,'Rewind boundary did not pause');
    assert.equal((await page.evaluate(()=>window.SWYRL_ENGINE_CINEMATIC.status())).ended,false,'Rewind to start incorrectly marked the episode ended');
    await frames(page,3);close((await state(page)).elapsed,0,'Rewind boundary continued ticking');
    await tap(page,'animeCineRewind');close((await state(page)).elapsed,0,'Rewind at zero jumped to the episode end');
    close((await state(page)).rate,1,'Rewind at zero left a stalled negative rate');
    assert.equal((await state(page)).paused,true,'Rewind at zero did not remain paused');
    await tap(page,'animeCinePause');deltas.push(await rateFrames(page,1,'resume from start boundary'));

    await scrub(page,model.duration-.2);
    for(let i=0;i<3;i++)await tap(page,'animeCineFastForward');
    await frames(page,1);bound=await state(page);
    close(bound.elapsed,model.duration,'Fast-forward passed the episode end');close(bound.rate,1,'End boundary did not reset speed');
    assert.equal(bound.paused,true,'End boundary did not pause');
    assert.equal((await page.evaluate(()=>window.SWYRL_ENGINE_CINEMATIC.status())).ended,true,'Forward completion did not preserve Replay');
    await frames(page,3);close((await state(page)).elapsed,model.duration,'Completed episode kept ticking');
    await tap(page,'animeCineRewind');deltas.push(await rateFrames(page,-2,'rewind from completed episode'));
    await tap(page,'animeCineFastForward');await scrub(page,model.duration-.1);await frames(page,2);
    await tap(page,'animeCineFastForward');close((await state(page)).elapsed,0,'Fast-forward from end did not replay from zero');
    deltas.push(await rateFrames(page,2,'fast replay'));
    await scrub(page,model.duration-.1);await frames(page,2);await tap(page,'animeCinePause');
    close((await state(page)).elapsed,0,'Replay did not restart the episode');
    deltas.push(await rateFrames(page,1,'normal Replay'));

    const rendered=[];
    rendered.push(await backwardsFrame(page,19,mode.name));
    rendered.push(await backwardsFrame(page,6,mode.name));
    await page.screenshot({path:resolve(output,mode.name+'-watch-rewind.png')});
    await tap(page,'animeScreeningClose');
    assert.equal((await animation(page)).active,false,'Closing Watch left cinematic playback active');
    assert.equal((await state(page)).rate,1,'Closing Watch leaked shuttle speed');
    assert.equal((await page.evaluate(()=>window.SWYRL_ENGINE_SCREENING.status())).open,false,'Closing Watch left its canvas mounted');
    assert.equal(await page.locator('#storyCinemaStage canvas').count(),0,'Closing Watch did not restore the editor canvas');
    await tap(page,'animeScreeningBtn');await assertRate(page,1,'reopened Watch defaults');
    await tap(page,'animeCineFastForward');await tap(page,'animeCineExit');
    assert.equal((await animation(page)).playing,false,'Stop did not end episode playback');
    assert.equal((await state(page)).rate,1,'Stop leaked shuttle speed into next session');
    assert.equal((await page.evaluate(()=>window.SWYRL_ENGINE_SCREENING.status())).open,false,'Stop did not close Watch');
    await tap(page,'animeScreeningBtn');
    for(let i=0;i<3;i++)await tap(page,'animeCineFastForward');
    await assertRate(page,8,'Explore setup');await tap(page,'animeCineExplore');
    assert.equal((await state(page)).active,false,'Explore retained cinematic playback');
    close((await state(page)).rate,1,'Explore leaked shuttle speed into walking');
    assert.equal((await animation(page)).playing,true,'Explore failed to enter the native set');
    assert.equal((await page.evaluate(()=>window.SWYRL_ENGINE_SCREENING.status())).open,false,'Explore did not return the canvas to its native set');
    // Explore has already closed Watch. Use the native editor session controls
    // to finish walking, then start a fresh ordinary Play session.
    await page.evaluate(()=>document.getElementById('stopBtn').click());
    await page.evaluate(()=>document.getElementById('playBtn').click());
    deltas.push(await rateFrames(page,1,'new native editor Play'));
    assert.equal((await page.evaluate(()=>window.SWYRL_ENGINE_SCREENING.status())).open,false,'Editor Play unexpectedly opened Watch');
    await tap(page,'animeCineExit');
    const saved=await project(page);
    assert.deepEqual(saved.project,initial.project,'Transport wrote transient speed/time into authored project metadata');
    assert.deepEqual(cleanScene(saved),cleanScene(initial),'Transport changed saved actors/layers');
    assert.deepEqual(errors,[],'Unhandled page errors: '+errors.join('\n'));
    receipts.push({mode:mode.name,deltas,rendered,metrics});
    console.log('EPISODE_TRANSPORT_'+mode.name.toUpperCase()+'_ACTUAL_BUTTONS_SIGNED_RATES_BOUNDARIES_RENDER_RESET_PASS');
    await context.close();
  }
  await writeFile(resolve(output,'receipt.json'),JSON.stringify({pass:true,viewports:receipts},null,2));
  console.log('EPISODE_TRANSPORT_ALL_VIEWPORTS_PASSED');
}finally{await browser.close();}
