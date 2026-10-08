import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {mkdir, readFile} from 'node:fs/promises';
import {resolve} from 'node:path';

// Exercise the native authoring UI and the actual renderer. The runtime APIs
// supply observable state, while Save/Load uses a real downloaded project.
const base=(process.env.SWYRL_ANIME_TEST_URL||'http://127.0.0.1:8765').replace(/\/$/,'');
const output=resolve(process.env.SWYRL_ANIME_SCREENSHOTS_DIR||'storybook-acceptance');
await mkdir(output,{recursive:true});
const browser=await chromium.launch({headless:true,
  ...(process.env.SWYRL_CHROMIUM_PATH?{executablePath:process.env.SWYRL_CHROMIUM_PATH}:{}),
  args:['--no-sandbox','--disable-dev-shm-usage','--enable-webgl',
    '--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader']});

const modes=[
  {name:'desktop',viewport:{width:1440,height:900},isMobile:false,hasTouch:false},
  {name:'mobile',viewport:{width:390,height:844},isMobile:true,hasTouch:true}
].filter(mode=>!process.env.SWYRL_ANIME_TEST_MODE||process.env.SWYRL_ANIME_TEST_MODE===mode.name);
assert.ok(modes.length,'SWYRL_ANIME_TEST_MODE must be desktop or mobile');
const timeline=page=>page.evaluate(()=>window.SWYRL_ENGINE_ANIMATION.getTimeline());
const project=page=>page.evaluate(()=>window.SWYRL_ENGINE_ANIMATION.serializedProject());
const stage=page=>page.evaluate(()=>window.SWYRL_ENGINE_STORYBOARD.stageStatus());
const status=page=>page.evaluate(()=>window.SWYRL_ENGINE_ANIMATION.status());
const frames=page=>page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
const trackKey=(model,track,time)=>model.tracks[track].find(key=>Math.abs(key.time-time)<1e-6);
const close=(actual,expected,message,tolerance=1e-5)=>assert.ok(Math.abs(actual-expected)<=tolerance,
  message+': expected '+expected+', received '+actual);

async function input(page,selector,value){
  await page.locator(selector).evaluate((element,value)=>{
    element.value=String(value);element.dispatchEvent(new Event('input',{bubbles:true}));
    element.dispatchEvent(new Event('change',{bubbles:true}));
  },value);
}
async function openStudio(page){
  if(!await page.locator('#storyStudioPanel').isVisible())await page.locator('#storyStudioBtn').click();
  assert.equal(await page.locator('#storyStudioPanel').isVisible(),true,'Animation studio did not open');
}
async function closeStudio(page){
  if(await page.locator('#storyStudioPanel').isVisible())await page.locator('#storyClose').click();
}
async function historyAction(page,action){
  const quick=page.locator(action==='undo'?'#quickUndoBtn':'#quickRedoBtn');
  if(await quick.isVisible()){await quick.click();return;}
  await page.locator('#mobileToolsBtn').click();
  await page.locator('#mobileToolsPanel [data-click="'+action+'Btn"]').click();
}
async function addKeyUI(page,track,time,fields){
  await openStudio(page);await page.locator('#storyTrack').selectOption(track);
  await input(page,'#storyTime',time);
  for(const [field,value] of Object.entries(fields))await input(page,'[data-story-field="'+field+'"]',value);
  await page.locator('#storyAddKey').click();
  const key=trackKey(await timeline(page),track,time);
  assert.ok(key,'UI did not save '+track+' key at '+time+'s');
  for(const [field,value] of Object.entries(fields))close(key[field],value,'UI key '+track+'.'+field);
  return key;
}
async function seek(page,time){
  const ok=await page.evaluate(time=>window.SWYRL_ENGINE_ANIMATION.seek(time),time);
  assert.equal(ok,true,'Seeking '+time+'s failed');await frames(page);
  return stage(page);
}

function assertSafeScene(observation,label){
  assert.ok(observation,'Missing stage diagnostics: '+label);
  assert.equal(observation.assetErrors?.length||0,0,'Artwork failed: '+label);
  assert.equal(observation.occlusionSafe,true,'Scenery hides the actors/camera: '+label);
  for(const plate of observation.scenery||[])assert.ok(plate.frontZ<=plate.z+.001,
    'The folded '+plate.id+' plate swung toward the camera: '+label);
  assert.ok(observation.camera?.position?.every(Number.isFinite),'Invalid camera: '+label);
  assert.ok(Number.isFinite(observation.safeCameraGap)&&observation.safeCameraGap>1,
    'Scenery entered the camera near field: '+label);
  if(observation.castBounds?.some(actor=>actor.id==='kami'&&actor.visible)&&Number.isFinite(observation.bookTopY)&&Number.isFinite(observation.foregroundInkTopY)){
    assert.ok(observation.bookTopY<3&&observation.foregroundInkTopY<3,
      'Book/foreground rises through the mage torsos: '+label);
  }
}
function assertCastReadable(observation,label){
  const bounds=observation.castBounds;
  assert.ok(Array.isArray(bounds)&&bounds.length>=2,'Separate mage bounds missing: '+label);
  for(const name of ['kami','swyrlz']){
    const actor=bounds.find(entry=>String(entry.id||entry.name||'').toLowerCase().includes(name));
    assert.ok(actor,'Missing '+name+' bounds: '+label);
    assert.notEqual(actor.visible,false,name+' hidden: '+label);
    // Bounds are projected into viewport pixels by the renderer diagnostics.
    const rectangle=actor.screen||actor.rect||actor;
    if(['left','right','top','bottom'].every(key=>Number.isFinite(rectangle[key]))){
      const width=observation.viewport?.width||observation.camera?.viewport?.width;
      const height=observation.viewport?.height||observation.camera?.viewport?.height;
      const normalized=rectangle.normalized===true;
      assert.ok(rectangle.right-rectangle.left>(normalized?.05:20)&&rectangle.bottom-rectangle.top>(normalized?.1:40),
        name+' is too small to read: '+label);
      if(normalized){
        assert.ok(rectangle.right>0&&rectangle.left<1&&rectangle.bottom>0&&rectangle.top<1,
          name+' is outside the camera: '+label);
      }else if(Number.isFinite(width)&&Number.isFinite(height)){
        assert.ok(rectangle.right>0&&rectangle.left<width&&rectangle.bottom>0&&rectangle.top<height,
          name+' is outside the camera: '+label);
      }
    }
  }
}
function cleanScene(saved){
  // Workstation hydration and editor revision bookkeeping are independent of
  // whether transient render nodes were restored after a cinematic session.
  return {background:saved.scene.background,actors:saved.scene.actors.map(actor=>({id:actor.id,type:actor.type,
    position:actor.position,rotation:actor.rotation,scale:actor.scale,
    manualVisible:actor.manualVisible,editorLayerIds:actor.editorLayerIds})),layers:saved.editor.layers};
}

function watch(page){
  const failures={errors:[],images:[]};
  page.on('pageerror',error=>failures.errors.push(String(error)));
  page.on('response',response=>{if(response.status()>=400&&response.url().startsWith(base)&&/\.png(?:\?|$)/i.test(response.url()))failures.images.push(response.status()+' '+response.url())});
  page.on('requestfailed',request=>{if(request.url().startsWith(base)&&/\.png(?:\?|$)/i.test(request.url()))failures.images.push(request.failure()?.errorText+' '+request.url())});
  return failures;
}
function assertNoFailures(failures,label){
  assert.deepEqual(failures.errors,[],'Unhandled browser errors: '+label);
  assert.deepEqual(failures.images,[],'Local artwork requests failed: '+label);
}
async function start(page,projectId='anime-ghosts-ep01'){
  await page.goto(base+'/index.html?project='+projectId,{waitUntil:'domcontentloaded',timeout:60000});
  await page.waitForFunction(()=>window.SWYRL_ENGINE_ANIMATION&&window.SWYRL_ENGINE_STORYBOARD,
    undefined,{timeout:60000});
  if(projectId==='anime-ghosts-ep01')await page.waitForFunction(()=>{
    const state=window.SWYRL_ENGINE_STORYBOARD.stageStatus();return state?.assetsReady||state?.assetErrors?.length;
  },undefined,{timeout:45000});
  await frames(page);
}

let allPassed=false;
try{
  for(const mode of modes){
    const contextOptions={viewport:mode.viewport,isMobile:mode.isMobile,hasTouch:mode.hasTouch,acceptDownloads:true};
    const context=await browser.newContext(contextOptions);
    const page=await context.newPage(),failures=watch(page);
    await start(page);
    assert.equal((await status(page)).projectId,'ghosts-different-forms-ep01');
    const initial=await project(page),initialScene=cleanScene(initial);

    // Public Watch must enter the *current saved v9 native 2.5D episode*, not
    // the historical separate 2D iframe. Exercise a real mobile/desktop tap.
    await page.locator('#animeScreeningBtn').click();
    await page.waitForFunction(()=>window.SWYRL_ENGINE_ANIMATION.status().active,undefined,{timeout:15000});
    assert.equal(await page.locator('#animeScreening').evaluate(el=>el.classList.contains('open')),true,
      'Watch did not reopen the requested pop-up video player');
    assert.equal(await page.locator('#animeEpisodeFrame').getAttribute('src'),null,
      'The old standalone 2D episode should not load for native Watch');
    assert.equal(await page.locator('#animeScreeningNative').isVisible(),true,
      'Native cinematic is not visible within the pop-up');
    assert.equal((await page.evaluate(()=>window.SWYRL_ENGINE_SCREENING.status())).source,
      'authored-native-2.5d','The player was not routed to the live scene');
    assert.equal(await page.locator('#storyCinemaStage canvas').count(),1,
      'The original WebGL canvas was not mounted in the pop-up');
    assert.equal(await page.locator('#storyCinemaStage #animeCineHud').count(),1,
      'The native episode transport and subtitles were not mounted in the pop-up');
    assert.equal(await page.locator('#storyCinemaChapters button').count(),8,
      'The pop-up lost its eight clickable scene selectors');
    const canvasMetrics=await page.locator('#storyCinemaStage canvas').evaluate(node=>{
      const b=node.getBoundingClientRect();return {width:b.width,height:b.height,viewportWidth:innerWidth};});
    assert.ok(canvasMetrics.width>160&&canvasMetrics.height>150&&
      canvasMetrics.width<=canvasMetrics.viewportWidth+2,
      'Pop-up WebGL canvas does not fit the phone/desktop viewport: '+JSON.stringify(canvasMetrics));
    assert.equal((await status(page)).playing,true,'Native Watch did not start the episode');
    assert.equal((await stage(page)).occlusionSafe,true,'Native Watch scene is not camera-safe');
    assert.ok((await stage(page)).actorBindings?.length>=8,'Native Watch lacks the illustrated pop-up actors');
    await page.locator('#storyCinemaChapters button').nth(3).click();
    assert.ok((await status(page)).elapsed>=40,'Chapter selector did not seek the authored video');
    assert.match(await page.locator('#animeCineCaption').innerText(),/./,
      'The native dialogue caption is missing from the pop-up');
    await page.screenshot({path:resolve(output,'storybook-'+mode.name+'-popup-native.png')});
    await page.locator('#animeCinePause').click();
    assert.equal((await status(page)).paused,true,'Pop-up pause did not pause native video');
    await page.locator('#animeCinePause').click();
    assert.equal((await status(page)).paused,false,'Pop-up resume did not resume native video');
    await page.locator('#animeCineExit').click();await frames(page);
    assert.equal((await status(page)).active,false,'Native Watch could not Stop');
    assert.equal(await page.locator('#animeScreening').evaluate(el=>el.classList.contains('open')),false,
      'Native Stop did not close the pop-up');
    assert.equal((await page.evaluate(()=>window.SWYRL_ENGINE_SCREENING.status())).open,false,
      'Native Stop left the player mounted');
    assert.equal(await page.locator('#storyCinemaStage canvas').count(),0,
      'Native Stop failed to return the live canvas to the editor');
    await page.locator('#animeScreeningBtn').click();
    assert.equal(await page.locator('#animeScreeningNative').isVisible(),true,
      'Native pop-up could not be reopened');
    await page.locator('#animeScreeningClose').click();
    assert.equal((await status(page)).active,false,
      'Closing the pop-up X did not stop playback and restore editing');
    // The original historical film remains opt-in and is explicitly labeled.
    await openStudio(page);
    await page.locator('#storyWatchOriginal').click();
    assert.equal(await page.locator('#animeScreening').evaluate(el=>el.classList.contains('open')),true,
      'Original 2D archive is no longer accessible');
    assert.equal(await page.locator('#animeEpisodeFrame').getAttribute('src'),
      'episodes/ghosts-in-different-forms-ep01.html','Archive loaded an unexpected recording');
    assert.equal((await status(page)).active,false,'Archive accidentally started the native cinematic');
    await page.locator('#animeScreeningClose').click();await frames(page);
    assert.equal(await page.locator('#animeEpisodeFrame').getAttribute('src'),null,
      'Closing archive did not unmount playback');
    assert.deepEqual(cleanScene(await project(page)),initialScene,
      'Watching either episode changed the authored scene');
    assert.equal(initial.project.animeTimeline?.schema,'anime-timeline-v1','Starter has no saved animation');
    const layerNames=initial.editor.layers.map(layer=>layer.name.toLowerCase());
    assert.ok(layerNames.some(name=>name.includes('kami')),'Kami needs a native editor layer');
    assert.ok(layerNames.some(name=>/swyrl|§wyrl|wyrl/.test(name)),'§wyrlz needs a separate native editor layer');
    assert.ok(layerNames.filter(name=>/background|atmosphere|midground|foreground|scenery/.test(name)).length>=3,
      'Scenery needs several native editor layers');

    // v9 clean-room default: preserve all 62 historical actors, but keep the
    // obsolete signs, stages, crystals and guardian off the active book set.
    const legacyIds=['layer-ep-sets','layer-ep-fx','layer-ep-cast'];
    const legacyLayers=initial.editor.layers.filter(layer=>legacyIds.includes(layer.id));
    assert.equal(legacyLayers.length,3,'Historical editor layers were discarded');
    assert.ok(legacyLayers.every(layer=>layer.visible===false),
      'Historical platforms, signs and kiosks must be hidden by default');
    const paperLayers=initial.editor.layers.filter(layer=>layer.id.startsWith('anime-layer-'));
    assert.equal(paperLayers.length,8,'Missing paper-theatre layers');
    assert.ok(paperLayers.every(layer=>layer.visible===true),'Paper stage should open visible');
    assert.equal(initial.editor.activeLayerId,'anime-layer-kami','New objects would be assigned to archived scenery');
    assert.equal(initial.scene.actors.length,70,'The original episode assets must remain editable');
    const legacyActors=initial.scene.actors.filter(actor=>(actor.editorLayerIds||[]).some(id=>legacyIds.includes(id)));
    assert.equal(legacyActors.length,60,'Historical layered set assets should remain recoverable');
    // Serialized actor.visible is the authored manual-visibility preference,
    // not the rendered effective visibility after the editor-layer mask.
    assert.ok(legacyActors.every(actor=>actor.manualVisible===true && actor.visible===true),
      'Historical actors should remain individually recoverable when their layer is restored');
    assertSafeScene(await seek(page,8),mode.name+' initial rendered editor preview');
    await page.evaluate(()=>window.SWYRL_ENGINE_STORYBOARD.exitPreview());await frames(page);

    // Create an authored key through the editor and restore it with native history.
    const kamiBefore=await page.evaluate(()=>window.SWYRL_ENGINE_ANIMATION.sample('kami',10));
    const kamiX=Math.min(3.5,kamiBefore.x+.35);
    await addKeyUI(page,'kami',10,{x:kamiX});await closeStudio(page);
    await historyAction(page,'undo');await frames(page);
    assert.equal(trackKey(await timeline(page),'kami',10),undefined,'Undo did not remove the new character key');
    await historyAction(page,'redo');await frames(page);
    close(trackKey(await timeline(page),'kami',10).x,kamiX,'Redo did not restore the character key');
    assertSafeScene(await seek(page,10),mode.name+' preview after Undo/Redo');

    await addKeyUI(page,'camera',12,{x:.55,z:13.6,fov:46});
    await input(page,'#storyTime',12);await page.locator('#storyPreview').click();await frames(page);
    const cameraPreview=await stage(page);
    assert.equal(cameraPreview.preview,true,'UI Preview did not show the saved shot');
    close(cameraPreview.camera.position[0],.55,'Preview ignores saved camera X',.04);
    if(mode.isMobile)assert.ok(cameraPreview.camera.position[2]>=13.6,'Mobile fit places the camera ahead of the authored Z');
    else close(cameraPreview.camera.position[2],13.6,'Preview ignores saved camera Z',.04);
    assertSafeScene(cameraPreview,mode.name+' camera key preview');
    const repeatedA=await seek(page,12),repeatedB=await seek(page,12);
    assert.deepEqual(repeatedA.camera.position,repeatedB.camera.position,'Preview seek depends on wall-clock time');

    // Dialogue edited in the same panel must drive the rendered episode caption.
    await page.locator('details.story-beat-editor').evaluate(details=>{details.open=true});
    await page.locator('#storyBeatSelect').selectOption('0');
    await input(page,'#storyBeatTitle','The Ember Signal');
    await input(page,'#storyDialogue','KAMI: The pages remember.\n§WYRLZ: Then let us give them a story.');
    await page.locator('#storySaveBeat').click();
    assert.equal((await timeline(page)).beats[0].title,'The Ember Signal','Scene title was not saved');
    assert.ok((await timeline(page)).beats[0].cues.some(cue=>cue.text.includes('The pages remember.')),
      'Scene dialogue was not saved');
    await page.screenshot({path:resolve(output,'storybook-'+mode.name+'-editor.png')});

    // Save Project produces a real portable project, including the editor layers.
    const downloadPending=page.waitForEvent('download',{timeout:15000});
    await page.locator('#storySaveProject').click();
    const download=await downloadPending;
    const exported=JSON.parse(await readFile(await download.path(),'utf8'));
    assert.deepEqual(exported.project.animeTimeline,await timeline(page),'Downloaded timeline differs from authoring state');
    close(trackKey(exported.project.animeTimeline,'kami',10).x,kamiX,'Character key missing from saved project');
    close(trackKey(exported.project.animeTimeline,'camera',12).z,13.6,'Camera key missing from saved project');
    assert.deepEqual(cleanScene(exported),initialScene,'Preview altered authored scene transforms/visibility');

    // The native Play button uses the authored sequence. Pause, edit, and Stop
    // must retain the edit while restoring the native set and editor camera.
    await closeStudio(page);
    await page.evaluate(()=>window.SWYRL_ENGINE_STORYBOARD.exitPreview());await frames(page);
    const beforePlay=await stage(page);
    await page.locator('#playBtn').click();
    await page.waitForFunction(()=>window.SWYRL_ENGINE_ANIMATION.status().active,undefined,{timeout:15000});
    await page.waitForFunction(()=>window.SWYRL_ENGINE_ANIMATION.status().elapsed>.5,undefined,{timeout:15000});
    assertSafeScene(await stage(page),mode.name+' native Play');
    await page.locator('#animeCinePause').click();
    assert.equal((await status(page)).paused,true,'Pause button failed');
    const pausedTime=(await status(page)).elapsed;await frames(page);await frames(page);
    close((await status(page)).elapsed,pausedTime,'Paused playhead advanced',1e-3);
    await seek(page,2);
    assert.equal((await status(page)).paused,true,'Scrub unexpectedly resumed paused playback');
    assert.match(await page.locator('#animeCineCaption').innerText(),/The pages remember|give them a story/,
      'Play caption does not use authored dialogue');
    await openStudio(page);await addKeyUI(page,'swyrlz',11,{x:-1.8});await closeStudio(page);

    // Visit the whole episode with rendered frames so every shot receives the
    // same occlusion checks, including page turns and the last scene.
    const duration=(await timeline(page)).duration;
    for(let time=0;time<=duration;time+=2){
      const observation=await seek(page,time);
      assertSafeScene(observation,mode.name+' '+time+'s');
      // Opening fold legitimately conceals the paper characters for a moment.
      if(time>=8)assertCastReadable(observation,mode.name+' '+time+'s');
    }
    for(const time of [12,50,98,128].filter(time=>time<duration)){
      assertCastReadable(await seek(page,time),mode.name+' screenshot '+time+'s');
      await page.screenshot({path:resolve(output,'storybook-'+mode.name+'-'+time+'s.png')});
    }
    await page.locator('#animeCineExit').click();await frames(page);
    assert.equal((await status(page)).active,false,'Stop left the cinematic active');
    assert.equal((await status(page)).playing,false,'Stop did not return to native editing');
    close(trackKey(await timeline(page),'swyrlz',11).x,-1.8,'Paused authoring edit lost on Stop');
    assert.deepEqual(cleanScene(await project(page)),initialScene,'Stop altered saved actors/layers');
    const afterPlay=await stage(page);
    if(beforePlay.editorCamera&&afterPlay.editorCamera)assert.deepEqual(afterPlay.editorCamera,beforePlay.editorCamera,
      'Stop did not restore the precise editor camera');

    // A second browser has no previous timeline state. Importing the downloaded
    // project must rebuild its render bindings and preserve exactly those keys.
    const reloadContext=await browser.newContext(contextOptions);
    const reloadPage=await reloadContext.newPage(),reloadFailures=watch(reloadPage);
    await start(reloadPage);
    const imported=await reloadPage.evaluate(data=>window.SWYRL_ENGINE_STORYBOARD.importProject(data),exported);
    assert.notEqual(imported,false,'Saved project import failed');await frames(reloadPage);
    assert.deepEqual(await timeline(reloadPage),exported.project.animeTimeline,'Saved/imported timeline changed');
    assert.deepEqual(cleanScene(await project(reloadPage)),initialScene,'Import lost native layers or actor transforms');
    assertSafeScene(await seek(reloadPage,12),mode.name+' imported preview');
    await openStudio(reloadPage);await reloadPage.locator('#storyTrack').selectOption('kami');
    await input(reloadPage,'#storyTime',10);await reloadPage.locator('#storyDeleteKey').click();
    assert.equal(trackKey(await timeline(reloadPage),'kami',10),undefined,'Delete Key UI failed');
    await closeStudio(reloadPage);await historyAction(reloadPage,'undo');await frames(reloadPage);
    close(trackKey(await timeline(reloadPage),'kami',10).x,kamiX,'Undo key deletion failed');

    // Non-finite and excessive imported camera/scenery values must be bounded
    // before entering the renderer. This also verifies imported data wins over
    // any prior project state held by the editor.
    const bad=structuredClone(exported);
    bad.project.animeTimeline.tracks.camera=[{time:-100,x:1e99,y:null,z:'NaN',fov:Infinity},
      {time:1e99,x:-1e99,z:-1e99,tx:1e99,fov:-1e99}];
    bad.project.animeTimeline.tracks.midground=[{time:0,z:1e99,scale:1e99,opacity:'NaN'}];
    await reloadPage.evaluate(data=>window.SWYRL_ENGINE_STORYBOARD.importProject(data),bad);await frames(reloadPage);
    const sanitized=await timeline(reloadPage);
    for(const [track,keys] of Object.entries(sanitized.tracks)){
      assert.ok(keys[0].time===0&&keys.at(-1).time===sanitized.duration,'Missing endpoint keys on '+track);
      for(const key of keys)for(const [field,value] of Object.entries(key))if(typeof value==='number')assert.ok(Number.isFinite(value),'Non-finite '+track+'.'+field);
    }
    for(const key of sanitized.tracks.camera){assert.ok(key.x>=-4&&key.x<=4&&key.z>=9&&key.z<=24&&key.fov>=35&&key.fov<=65,'Imported camera escaped bounds')}
    assertSafeScene(await seek(reloadPage,12),mode.name+' sanitized imported preview');

    // The book owns its transform and visibility. A hidden or scaled foreground
    // plate must never hide or shrink it through a shared render parent.
    await reloadPage.evaluate(data=>window.SWYRL_ENGINE_STORYBOARD.importProject(data),exported);
    await seek(reloadPage,12);
    const foregroundLayer=(await stage(reloadPage)).actorBindings.find(actor=>actor.layer==='foreground')?.layerIds?.[0];
    assert.ok(foregroundLayer,'Foreground has no native editor layer binding');
    assert.equal(await reloadPage.evaluate(layer=>window.SWYRL_ENGINE_AGENT.setLayerVisibility(layer,false),foregroundLayer),true);
    assert.equal(await reloadPage.evaluate(()=>window.SWYRL_ENGINE_ANIMATION.upsertKey('foreground',
      {time:12,visible:false,scale:.25})),true);
    const bookWithSmallForeground=await seek(reloadPage,12);
    assert.equal(bookWithSmallForeground.bookVisible,true,'Hiding the foreground hid the independent book');
    assert.ok(bookWithSmallForeground.bookBounds?.min&&bookWithSmallForeground.bookBounds?.max,
      'Book needs observable world bounds independent of scenery');
    assert.equal(await reloadPage.evaluate(()=>window.SWYRL_ENGINE_ANIMATION.upsertKey('foreground',
      {time:12,visible:false,scale:2})),true);
    const bookWithLargeForeground=await seek(reloadPage,12);
    assert.equal(bookWithLargeForeground.bookVisible,true,'Hidden enlarged foreground hid the book');
    for(const edge of ['min','max'])for(let axis=0;axis<3;axis++)close(bookWithLargeForeground.bookBounds[edge][axis],
      bookWithSmallForeground.bookBounds[edge][axis],'Foreground scale changed the book world bounds');
    await reloadPage.evaluate(()=>window.SWYRL_ENGINE_ANIMATION.upsertKey('book',{time:12,scale:.65,visible:true,opacity:1}));
    const smallBook=await seek(reloadPage,12);
    await reloadPage.evaluate(()=>window.SWYRL_ENGINE_ANIMATION.upsertKey('book',{time:12,scale:1.1,visible:true,opacity:1}));
    const largeBook=await seek(reloadPage,12);
    assert.equal(smallBook.bookVisible,true);assert.equal(largeBook.bookVisible,true);
    const smallWidth=smallBook.bookBounds.max[0]-smallBook.bookBounds.min[0],largeWidth=largeBook.bookBounds.max[0]-largeBook.bookBounds.min[0];
    assert.ok(largeWidth>smallWidth*1.4,'Book track scale does not control the independent book');
    assertSafeScene(largeBook,mode.name+' independently scaled book');

    // A replacement image can paint every foreground pixel. Safety must use
    // its real painted extent, rather than the starter trim's transparent top.
    await reloadPage.evaluate(layer=>window.SWYRL_ENGINE_AGENT.setLayerVisibility(layer,true),foregroundLayer);
    const opaquePng=await reloadPage.evaluate(()=>{
      const canvas=document.createElement('canvas');canvas.width=canvas.height=16;
      const context=canvas.getContext('2d');context.fillStyle='#39222c';context.fillRect(0,0,16,16);
      return canvas.toDataURL('image/png');
    });
    assert.equal(await reloadPage.evaluate(source=>window.SWYRL_ENGINE_STORYBOARD.bindArtwork('foreground',source),opaquePng),true,
      'Opaque replacement artwork was not assigned');
    await reloadPage.evaluate(()=>window.SWYRL_ENGINE_ANIMATION.upsertKey('foreground',
      {time:12,visible:true,opacity:1,scale:2,y:12,z:6}));
    await reloadPage.waitForFunction(()=>window.SWYRL_ENGINE_STORYBOARD.stageStatus().assetsReady,undefined,{timeout:15000});
    const opaqueStage=await seek(reloadPage,12);
    assertSafeScene(opaqueStage,mode.name+' opaque foreground replacement');
    const kamiPose=await reloadPage.evaluate(()=>window.SWYRL_ENGINE_ANIMATION.sample('kami',12));
    assert.ok(opaqueStage.foregroundInkTopY<kamiPose.y-3*kamiPose.scale,
      'Opaque foreground pixels still overlap Kami despite reported safety');
    const savedOpaque=await project(reloadPage);
    assert.equal(savedOpaque.scene.actors.find(actor=>actor.storyVisual?.layer==='foreground').storyVisual.asset,opaquePng,
      'Replacement artwork is missing from portable project data');
    await reloadPage.evaluate(()=>{
      window.SWYRL_ENGINE_ANIMATION.upsertKey('kami',{time:12,visible:false,opacity:0});
      window.SWYRL_ENGINE_ANIMATION.upsertKey('swyrlz',{time:12,visible:true,opacity:1,y:1.2,scale:1.1});
    });
    const companionOnly=await seek(reloadPage,12);
    assert.equal(companionOnly.castBounds.find(actor=>actor.id==='kami').visible,false);
    assert.equal(companionOnly.castBounds.find(actor=>actor.id==='swyrlz').visible,true);
    assertSafeScene(companionOnly,mode.name+' low companion-only opaque foreground');
    assert.ok(companionOnly.foregroundInkTopY<1.2-1.65*1.1&&companionOnly.bookTopY<1.2-1.65*1.1,
      'Foreground or book hides the low companion when Kami is hidden');

    // Malformed optional art metadata must fall back to an ordinary valid cel.
    const nullVisual=structuredClone(exported),cel=nullVisual.scene.actors.find(actor=>actor.type==='animeCel');
    assert.ok(cel,'Starter contains no saved native paper actors');cel.storyVisual=null;
    assert.equal(await reloadPage.evaluate(data=>window.SWYRL_ENGINE_STORYBOARD.importProject(data),nullVisual),true,
      'A null optional storyVisual crashed project loading');
    await reloadPage.waitForFunction(()=>window.SWYRL_ENGINE_STORYBOARD.stageStatus().assetsReady,undefined,{timeout:15000});
    assertSafeScene(await seek(reloadPage,12),mode.name+' null visual fallback');

    // Authoring can copy an ordinary native actor Inspector pose into its
    // animation key without altering the other character's track.
    await reloadPage.evaluate(data=>window.SWYRL_ENGINE_STORYBOARD.importProject(data),exported);
    const captureProject=await project(reloadPage),kamiActor=captureProject.scene.actors.find(actor=>actor.storyVisual?.layer==='kami');
    const companionBeforeCapture=(await timeline(reloadPage)).tracks.swyrlz;
    assert.equal(await reloadPage.evaluate(id=>window.SWYRL_ENGINE_AGENT.setTransform(id,
      {position:[1.75,4.3,-.8],rotation:[0,0,.13],scale:[.9,.9,.9]}),kamiActor.id),true);
    await openStudio(reloadPage);await reloadPage.locator('#storyTrack').selectOption('kami');
    await input(reloadPage,'#storyTime',19.25);await reloadPage.locator('#storyCapturePose').click();
    const capturedPose=trackKey(await timeline(reloadPage),'kami',19.25);
    assert.ok(capturedPose,'Capture Actor Pose did not create a keyframe');
    for(const [field,value] of Object.entries({x:1.75,y:4.3,z:-.8,rotation:.13,scale:.9}))close(capturedPose[field],value,
      'Capture Actor Pose ignored the native Inspector '+field);
    assert.deepEqual((await timeline(reloadPage)).tracks.swyrlz,companionBeforeCapture,
      'Capturing Kami changed the independent companion track');
    await closeStudio(reloadPage);
    await historyAction(reloadPage,'undo');await frames(reloadPage);
    assert.equal(trackKey(await timeline(reloadPage),'kami',19.25),undefined,'Undo did not remove the captured pose');
    await historyAction(reloadPage,'redo');await frames(reloadPage);
    assert.deepEqual(trackKey(await timeline(reloadPage),'kami',19.25),capturedPose,'Redo did not restore the captured pose');
    assertNoFailures(reloadFailures,mode.name+' Save/Load/sanitization');await reloadContext.close();

    // Switching projects disposes the episode preview and preserves ordinary
    // first-person Play and each independent project's authored destinations.
    for(const other of [
      {template:'glitch-dragons-den',id:'embervault-atelier',actors:170,zones:8},
      {template:'starforge-observatory',id:'starforge-observatory',actors:123,zones:7}
    ]){
      await page.evaluate(template=>window.SWYRL_ENGINE_AGENT.createProject(template),other.template);await frames(page);
      const saved=await project(page),observation=await stage(page);
      assert.equal(saved.project.canonicalId,other.id,'Project chooser loaded wrong project');
      assert.equal(saved.scene.actors.length,other.actors,'Storybook changed the '+other.id+' set');
      assert.equal(saved.project.teleportZones.length,other.zones,'Storybook changed the '+other.id+' destinations');
      assert.equal(observation.preview,false,'Episode preview survived a project switch');
      const otherScene=cleanScene(saved);
      await page.locator('#playBtn').click();await frames(page);
      assert.equal((await status(page)).active,false,'Other project unexpectedly started an anime cinematic');
      assert.equal((await status(page)).playing,true,'Other project ordinary Play failed');
      await page.evaluate(()=>document.getElementById('stopBtn').click());await frames(page);
      assert.deepEqual(cleanScene(await project(page)),otherScene,'Other project actors/layers changed after Play/Stop');
    }
    assertNoFailures(failures,mode.name+' authoring/Play');
    console.log('STORYBOOK_AUTHORING_'+mode.name.toUpperCase()+'_PASS',JSON.stringify({duration,
      savedKeys:Object.fromEntries(Object.entries(exported.project.animeTimeline.tracks).map(([name,keys])=>[name,keys.length])),screenshots:output}));
    await context.close();
  }
  allPassed=true;
}finally{await browser.close()}
if(allPassed)console.log(modes.length===2?'STORYBOOK_AUTHORING_BOTH_VIEWPORTS_PASSED':'STORYBOOK_AUTHORING_SELECTED_VIEWPORT_PASSED');
