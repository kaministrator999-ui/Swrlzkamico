import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {mkdir,readFile} from 'node:fs/promises';
import {resolve} from 'node:path';

// Exercise the native editor and the actual WebGL objects, not a detached
// scenery model. A flattened backdrop or a lost Save/Load must fail this test.
const base=(process.env.SWYRL_ANIME_TEST_URL||'http://127.0.0.1:8769').replace(/\/$/,'');
const output=resolve(process.env.SWYRL_ANIME_SCREENSHOTS_DIR||'depth-theatre-acceptance');
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
const project=page=>page.evaluate(()=>window.SWYRL_ENGINE_ANIMATION.serializedProject());
const model=page=>page.evaluate(()=>window.SWYRL_ENGINE_SCENERY.model());
const rendered=page=>page.evaluate(()=>window.SWYRL_ENGINE_SCENERY.renderStatus());
const stage=page=>page.evaluate(()=>window.SWYRL_ENGINE_STORYBOARD.stageStatus());
const status=page=>page.evaluate(()=>window.SWYRL_ENGINE_ANIMATION.status());
const frames=page=>page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
const close=(actual,expected,label,tolerance=1e-5)=>assert.ok(Number.isFinite(actual)&&Math.abs(actual-expected)<=tolerance,
  label+': expected '+expected+', received '+actual);
const distance=(a,b)=>Math.hypot(...a.map((value,index)=>value-b[index]));
const keyAt=(scenery,id,time)=>scenery.objects[id].keys.find(key=>Math.abs(key.time-time)<1e-6);
const nativeScene=saved=>({background:saved.scene.background,layers:saved.editor.layers,
  actors:saved.scene.actors.map(actor=>({id:actor.id,type:actor.type,position:actor.position,
    rotation:actor.rotation,scale:actor.scale,manualVisible:actor.manualVisible,editorLayerIds:actor.editorLayerIds}))});

function watch(page){
  const failures={errors:[],artwork:[]};
  page.on('pageerror',error=>failures.errors.push(String(error)));
  page.on('response',response=>{if(response.status()>=400&&response.url().startsWith(base)&&/\.(?:png|webp|jpe?g)(?:\?|$)/i.test(response.url()))
    failures.artwork.push(response.status()+' '+response.url());});
  page.on('requestfailed',request=>{if(request.url().startsWith(base)&&/\.(?:png|webp|jpe?g)(?:\?|$)/i.test(request.url()))
    failures.artwork.push(request.failure()?.errorText+' '+request.url());});
  return failures;
}
function noFailures(failures,label){
  assert.deepEqual(failures.errors,[],'Unhandled browser errors: '+label);
  assert.deepEqual(failures.artwork,[],'Layered scenery artwork failed: '+label);
}
async function start(page){
  await page.bringToFront();
  await page.goto(base+'/index.html?project=anime-ghosts-ep01',{waitUntil:'domcontentloaded',timeout:60000});
  await page.waitForFunction(()=>window.SWYRL_ENGINE_SCENERY&&window.SWYRL_ENGINE_RIG&&window.SWYRL_ENGINE_ANIMATION&&window.SWYRL_ENGINE_STORYBOARD,
    undefined,{timeout:60000,polling:100});
  await page.waitForFunction(()=>{const state=window.SWYRL_ENGINE_STORYBOARD.stageStatus();
    return state.assetsReady||state.assetErrors?.length;},undefined,{timeout:45000,polling:100});
  await frames(page);
}
async function input(page,selector,value){
  await page.locator(selector).evaluate((element,value)=>{
    if(element.type==='checkbox')element.checked=!!value;else element.value=String(value);
    element.dispatchEvent(new Event('input',{bubbles:true}));element.dispatchEvent(new Event('change',{bubbles:true}));
  },value);
}
async function openStudio(page){
  if(!await page.locator('#storyStudioPanel').isVisible())await page.locator('#storyStudioBtn').click();
}
async function closeStudio(page){
  if(await page.locator('#storyStudioPanel').isVisible())await page.locator('#storyClose').click();
}
async function historyAction(page,action){
  // The native cinematic preview hides mobile editor sheets. Return to the
  // editor before invoking its real Undo/Redo controls; re-seek after history.
  if(!(await status(page)).playing){
    await page.evaluate(()=>window.SWYRL_ENGINE_STORYBOARD.exitPreview());await frames(page);
  }
  const quick=page.locator(action==='undo'?'#quickUndoBtn':'#quickRedoBtn');
  if(await quick.isVisible()){await quick.click();return;}
  if(!await page.locator('#mobileToolsPanel').isVisible())await page.locator('#mobileToolsBtn').click();
  await page.locator('#mobileToolsPanel [data-click="'+action+'Btn"]').click();
}
async function seek(page,time){
  assert.equal(await page.evaluate(time=>window.SWYRL_ENGINE_ANIMATION.seek(time),time),true,'Seek failed at '+time+'s');
  await frames(page);return stage(page);
}
function safe(observation,label){
  assert.equal(observation.occlusionSafe,true,'Scenery obstructs the mages or camera: '+label);
  assert.deepEqual(observation.assetErrors||[],[],'Artwork failed: '+label);
  assert.ok(observation.safeCameraGap>6,'Camera moved through a popped-out object: '+label);
  for(const id of ['kami','swyrlz']){
    const actor=observation.castBounds.find(actor=>actor.id===id);
    assert.ok(actor&&actor.visible,id+' is hidden: '+label);
    assert.ok(actor.width>.035&&actor.height>.08,id+' is too small to read: '+label);
    assert.ok(actor.right>0&&actor.left<1&&actor.bottom>0&&actor.top<1,id+' is outside the shot: '+label);
  }
}
function foldedScenerySafe(observation,label){
  assert.equal(observation.occlusionSafe,true,'Folding scenery obstructs the mages or camera: '+label);
  assert.ok(observation.safeCameraGap>6,'Folding scenery enters the camera: '+label);
  for(const plate of observation.scenery)
    assert.ok(plate.frontZ<=plate.z+.001,'The folded '+plate.id+' crosses its parent hinge plane: '+label);
}
function detailedScenery(observation,label){
  assert.equal(observation.active,true,'Scenery renderer is inactive: '+label);
  assert.equal(observation.enabled,true,'Layered scenery is disabled: '+label);
  assert.ok(observation.objects.length>=30,'The library remains a few flattened plates: '+label);
  assert.equal(new Set(observation.objects.map(object=>object.id)).size,observation.objects.length,
    'Scenery objects share an authoring identity: '+label);
  const stars=new Set(observation.starLayers.map(layer=>layer.id));
  const cutouts=observation.objects.filter(object=>!stars.has(object.id));
  assert.ok(cutouts.length>=20,'Missing independently layered arches, shelves, banners and props: '+label);
  for(const parent of ['background','midground','atmosphere','effects'])
    assert.ok(cutouts.some(object=>object.parent===parent),'Missing '+parent+' cutout objects: '+label);
  for(const object of cutouts){
    assert.ok(object.meshCount>=3,'Cutout has no painted front/back/edge: '+label+' '+object.id);
    assert.ok(object.thickness>0,'Cutout has no real paper thickness: '+label+' '+object.id);
    assert.ok(Number.isFinite(object.depthSpan)&&object.depthSpan>0,'Cutout stays a depthless plane: '+label+' '+object.id);
    assert.ok(object.position.every(Number.isFinite)&&object.rotation.every(Number.isFinite)&&object.worldPosition.every(Number.isFinite),
      'Non-finite actual scenery transform: '+label+' '+object.id);
  }
  assert.equal(observation.starLayers.length,3,'Stars need near/middle/far layers: '+label);
  assert.ok(observation.starLayers.reduce((sum,layer)=>sum+layer.pointCount,0)>=100,'Missing independently layered stars: '+label);
  const depths=observation.starLayers.map(layer=>layer.z).sort((a,b)=>a-b);
  assert.ok(depths[1]-depths[0]>.4&&depths[2]-depths[1]>.4,'Star layers occupy the same flat depth: '+label);
}
function actualObject(observation,id,key,label,expectedPosition){
  const object=observation.objects.find(object=>object.id===id);
  assert.ok(object,'Missing actual scenery object: '+label+' '+id);
  assert.ok(object.position.every(Number.isFinite),'Non-finite actual scenery position: '+label+' '+id);
  if(expectedPosition)for(const [axis,field] of ['x','y','z'].entries())close(object.position[axis],expectedPosition[axis],
    'Saved scenery pose did not reproduce '+id+'.'+field+': '+label,.002);
  for(const [axis,field] of ['rotationX','rotationY','rotationZ'].entries())close(object.rotation[axis],key[field],
    'Saved scenery key does not rotate '+id+'.'+field+': '+label,.002);
  return object;
}
async function chooseObject(page,parent,id,time){
  await openStudio(page);await page.locator('#storyTrack').selectOption(parent);
  await input(page,'#storyTime',time);await page.locator('#sceneryObject').selectOption(id);
}
async function sceneryKey(page,parent,id,time,values){
  await chooseObject(page,parent,id,time);
  for(const [name,value] of Object.entries(values))await input(page,'#scenery'+name[0].toUpperCase()+name.slice(1),value);
  await page.locator('#sceneryAddKey').click();await frames(page);
  const key=keyAt(await model(page),id,time);
  assert.ok(key,'Native UI did not save '+id+' at '+time+'s');
  for(const [field,value] of Object.entries(values)){
    if(typeof value==='boolean')assert.equal(key[field],value,'Native UI '+id+'.'+field);
    else close(key[field],field.startsWith('rotation')?value*Math.PI/180:value,'Native UI '+id+'.'+field,.002);
  }
  return key;
}
async function facialAlignment(page,label){
  // These broad anatomical regions were checked against the immutable atlas
  // head cards. Inspect actual painted pixels, so the old eyes/mouth crossing
  // Kami's chin into the neck fail even if an anchor label says "correct".
  const skin={kami:{min:[-.43,-.40],max:[.24,.065]},swyrlz:{min:[-.4,-.88],max:[.45,-.36]}};
  for(const character of ['kami','swyrlz']){
    const face=(await page.evaluate(character=>window.SWYRL_ENGINE_RIG.renderStatus(character),character)).face;
    assert.ok(face.pixelCount>100,'No actual painted facial features: '+label+' '+character);
    assert.ok(face.featureInkBounds&&face.canvasInkBounds,'Missing actual face-surface bounds: '+label+' '+character);
    for(const axis of [0,1]){
      assert.ok(face.featureInkBounds.min[axis]>=skin[character].min[axis]&&
        face.featureInkBounds.max[axis]<=skin[character].max[axis],
        'Animated facial ink crosses the head card skin into hair/chin/neck: '+label+' '+character+' axis '+axis);
    }
    assert.ok(face.canvasInkBounds.min[0]>0&&face.canvasInkBounds.min[1]>0&&
      face.canvasInkBounds.max[0]<256&&face.canvasInkBounds.max[1]<192,
      'Animated face is clipped by its own surface: '+label+' '+character);
  }
}

let allPassed=false;
try{
  for(const mode of modes){
    const options={viewport:mode.viewport,isMobile:mode.isMobile,hasTouch:mode.hasTouch,acceptDownloads:true};
    const context=await browser.newContext(options),page=await context.newPage(),failures=watch(page);
    await start(page);
    const original=await project(page),originalScene=nativeScene(original),originalTracks=original.project.animeTimeline.tracks;
    assert.equal(original.project.animeScenery?.schema,'anime-scenery-v1','Starter has no portable layered scenery');
    assert.equal(Object.keys(originalTracks).length,9,'Scenery replaced the independent story/camera tracks');
    assert.equal(original.scene.actors.length,70,'Scenery creation altered existing editor actors');
    assert.equal(original.editor.layers.length,11,'Scenery creation altered existing editor layers');

    // Include intermediate opening frames. Sky geometry below its bottom
    // hinge or an unprotected thick cutout can otherwise swing toward camera.
    for(const time of [0,.2,1,2,4,7,9,12])foldedScenerySafe(await seek(page,time),mode.name+' unfolding '+time+'s');
    safe(await seek(page,17.25),mode.name+' initial layered shot');
    const initial=await rendered(page);detailedScenery(initial,mode.name+' initial theatre');
    await facialAlignment(page,mode.name+' authored faces');
    const oldFaces=(await project(page)).project.animeRigs;
    for(const character of ['kami','swyrlz']){
      const before=(await page.evaluate(character=>window.SWYRL_ENGINE_RIG.renderStatus(character),character)).face;
      assert.equal(await page.evaluate(({character,time})=>window.SWYRL_ENGINE_RIG.upsertKey(character,'face',
        {time,expression:'surprised',blink:0,mouth:1,speech:false,gazeX:.5,gazeY:.3,smile:0,brow:1}),
        {character,time:17.25}),true,'Facial expression key failed');
      await seek(page,17.25);await facialAlignment(page,mode.name+' open speech mouth');
      const after=(await page.evaluate(character=>window.SWYRL_ENGINE_RIG.renderStatus(character),character)).face;
      assert.notEqual(after.textureVersion,before.textureVersion,'Expression did not repaint the actual facial surface');
      await historyAction(page,'undo');await seek(page,17.25);
    }
    assert.deepEqual((await project(page)).project.animeRigs,oldFaces,'Face-expression Undo altered the original character rigs');
    const originalModel=await model(page),archBefore=initial.objects.find(object=>object.id==='arches-left'),
      siblingBefore=initial.objects.find(object=>object.id==='arches-right');
    assert.ok(archBefore&&siblingBefore,'The distant arches need independent paper pieces');
    const sample=await page.evaluate(time=>window.SWYRL_ENGINE_SCENERY.sample('arches-left',time),17.25);
    const key=await sceneryKey(page,'background','arches-left',17.25,{x:sample.x+.22,y:sample.y-.08,z:sample.z-.18,
      rotationX:6,rotationY:9,rotationZ:5,scale:sample.scale,opacity:.92,visible:true,unfold:.84});
    safe(await seek(page,17.25),mode.name+' authored arch');
    const afterArch=await rendered(page),actualArch=actualObject(afterArch,'arches-left',key,mode.name+' native object key');
    close(actualArch.position[0]-archBefore.position[0],key.x-sample.x,'Native X key does not translate the actual arch',.002);
    close(actualArch.position[1]-archBefore.position[1],key.y-sample.y,'Native Y key does not translate the actual arch',.002);
    close(actualArch.position[2]-archBefore.position[2],(key.z-sample.z)*originalModel.depth,
      'Native Z key does not change the actual arch depth',.002);
    assert.ok(distance(actualArch.worldPosition,archBefore.worldPosition)>.05,
      'Scenery controls changed metadata without moving the rendered arch');
    assert.deepEqual(afterArch.objects.find(object=>object.id==='arches-right'),siblingBefore,
      'Posing one arch changed its independent sibling');
    assert.deepEqual((await project(page)).project.animeTimeline.tracks,originalTracks,
      'An object key altered the camera, cast or whole-layer story tracks');
    const withArch=await model(page);
    for(const id of Object.keys(originalModel.objects))if(id!=='arches-left')
      assert.deepEqual(withArch.objects[id],originalModel.objects[id],'Posing one arch changed saved '+id);
    await closeStudio(page);await historyAction(page,'undo');await frames(page);
    assert.deepEqual(keyAt(await model(page),'arches-left',17.25),keyAt(originalModel,'arches-left',17.25),
      'Undo did not restore the original scenery key');
    await historyAction(page,'redo');await frames(page);
    assert.deepEqual(keyAt(await model(page),'arches-left',17.25),key,'Redo lost the scenery pose');
    await seek(page,17.25);actualObject(await rendered(page),'arches-left',key,mode.name+' scenery Redo',actualArch.position);

    // A camera pan projects the actual three star shells differently. Merely
    // painting stars into a single background cannot reproduce these depths.
    const beforePan=await rendered(page);
    const cameraSample=await page.evaluate(time=>window.SWYRL_ENGINE_ANIMATION.sample('camera',time),17.25);
    assert.equal(await page.evaluate(key=>window.SWYRL_ENGINE_ANIMATION.upsertKey('camera',key),
      {...cameraSample,time:17.25,x:cameraSample.x+.3,tx:cameraSample.tx+.3}),true,'Camera pan key failed');
    safe(await seek(page,17.25),mode.name+' actual star parallax');
    const afterPan=await rendered(page),displacements=[];
    for(const before of beforePan.starLayers){
      const after=afterPan.starLayers.find(layer=>layer.id===before.id);
      assert.ok(before.screenPosition.every(Number.isFinite)&&after.screenPosition.every(Number.isFinite),
        'Star shell has no actual camera projection');
      displacements.push(after.screenPosition[0]-before.screenPosition[0]);
    }
    assert.ok(displacements.every(delta=>Math.abs(delta)>1e-5),'The actual camera does not move relative to the stars');
    assert.ok(Math.max(...displacements)-Math.min(...displacements)>1e-5,
      'Near, middle and far stars move as one flattened backdrop');
    assert.deepEqual((await model(page)).objects,withArch.objects,'Camera pan altered saved star or scenery keys');
    await historyAction(page,'undo');await seek(page,17.25);
    assert.deepEqual((await project(page)).project.animeTimeline.tracks,originalTracks,'Camera pan Undo lost the original story tracks');

    // Global depth changes the physical stack without changing actor roots or
    // the saved independent object keys. The configuration is also portable.
    const depthBefore=await rendered(page);
    await chooseObject(page,'background','arches-left',17.25);
    await input(page,'#sceneryDepth',.65);await page.locator('#sceneryApplyConfig').click();
    await seek(page,17.25);const depthAfter=await rendered(page);detailedScenery(depthAfter,mode.name+' changed paper depth');
    close((await model(page)).depth,.65,'Global pop-out depth was not saved');
    assert.ok(depthBefore.objects.some(before=>{
      const after=depthAfter.objects.find(object=>object.id===before.id);
      return Math.abs(after.worldPosition[2]-before.worldPosition[2])>.01;
    }),'Depth control changed only the saved setting, not the rendered stack');
    safe(await stage(page),mode.name+' configured paper depth');
    const configuredArch=depthAfter.objects.find(object=>object.id==='arches-left');
    await page.screenshot({path:resolve(output,'depth-theatre-'+mode.name+'-editor.png')});
    const downloadPending=page.waitForEvent('download',{timeout:15000});await page.locator('#storySaveProject').click();
    const download=await downloadPending,exported=JSON.parse(await readFile(await download.path(),'utf8'));
    assert.deepEqual(exported.project.animeScenery,(await project(page)).project.animeScenery,
      'Save Project lost independent scenery poses or the depth stack');
    assert.deepEqual(nativeScene(exported),originalScene,'Scenery preview mutated native actors or layers');

    // Native Play uses that exact saved scenery. A paused edit survives Stop;
    // all existing shots retain clear space for the separate character rigs.
    await closeStudio(page);await page.evaluate(()=>window.SWYRL_ENGINE_STORYBOARD.exitPreview());await frames(page);
    const editorCamera=(await stage(page)).editorCamera;
    await page.locator('#playBtn').click();
    await page.waitForFunction(()=>window.SWYRL_ENGINE_ANIMATION.status().active,undefined,{timeout:15000});
    await page.locator('#animeCinePause').click();assert.equal((await status(page)).paused,true,'Native Play did not pause');
    await seek(page,17.25);actualObject(await rendered(page),'arches-left',key,mode.name+' native Play',configuredArch.position);
    const pausedTime=(await status(page)).elapsed;await frames(page);close((await status(page)).elapsed,pausedTime,'Paused playhead advanced',.001);
    const pillarSample=await page.evaluate(time=>window.SWYRL_ENGINE_SCENERY.sample('pillars-left',time),18.5);
    const pausedKey=await sceneryKey(page,'midground','pillars-left',18.5,{x:pillarSample.x-.12,y:pillarSample.y,z:pillarSample.z-.12,
      rotationX:0,rotationY:-7,rotationZ:0,scale:pillarSample.scale,opacity:.95,visible:true,unfold:.9});
    await closeStudio(page);
    for(const time of [12,17.25,18.5,45,72,110,130]){
      safe(await seek(page,time),mode.name+' Play '+time+'s');
      detailedScenery(await rendered(page),mode.name+' Play '+time+'s');
      await facialAlignment(page,mode.name+' Play face '+time+'s');
    }
    await seek(page,17.25);await page.screenshot({path:resolve(output,'depth-theatre-'+mode.name+'-play.png')});
    await page.locator('#animeCineExit').click();await frames(page);
    assert.equal((await status(page)).playing,false,'Stop failed to return to the editor');
    assert.deepEqual(keyAt(await model(page),'pillars-left',18.5),pausedKey,'Stop discarded a paused scenery edit');
    assert.deepEqual(nativeScene(await project(page)),originalScene,'Layered Play/Stop altered native actors/layers');
    assert.deepEqual((await stage(page)).editorCamera,editorCamera,'Layered Play did not restore the editor camera');

    // The public Watch pop-up must show the same genuine cutouts, not the old
    // flattened archival iframe. Verify mounting and framing on the phone too.
    await page.locator('#animeScreeningBtn').click();
    await page.waitForFunction(()=>window.SWYRL_ENGINE_ANIMATION.status().active,undefined,{timeout:15000});
    assert.equal(await page.locator('#animeScreeningNative').isVisible(),true,'Watch did not open the native 2.5D screening');
    assert.equal(await page.locator('#storyCinemaStage canvas').count(),1,'Watch did not mount the actual WebGL canvas');
    assert.equal(await page.locator('#animeEpisodeFrame').getAttribute('src'),null,'Watch loaded the old flattened iframe');
    await page.locator('#animeCinePause').click();
    safe(await seek(page,17.25),mode.name+' Watch framing');detailedScenery(await rendered(page),mode.name+' Watch depth');
    const canvasMetrics=await page.locator('#storyCinemaStage canvas').evaluate(node=>{
      const b=node.getBoundingClientRect();return {width:b.width,height:b.height,viewportWidth:innerWidth};});
    assert.ok(canvasMetrics.width>160&&canvasMetrics.height>150&&canvasMetrics.width<=canvasMetrics.viewportWidth+2,
      'Layered Watch does not fit the viewport');
    await page.screenshot({path:resolve(output,'depth-theatre-'+mode.name+'-watch.png')});
    await page.locator('#animeScreeningClose').click();await frames(page);
    assert.equal((await status(page)).active,false,'Closing Watch did not restore editing');

    // A clean browser cannot rescue missing scenery using an existing mesh
    // cache. The downloaded native project must reproduce the same poses.
    // All primary checks and snapshots are complete. The portable import uses
    // a fresh context with no still-rendering primary scene to rescue its data.
    await context.close();
    const freshContext=await browser.newContext(options),fresh=await freshContext.newPage(),freshFailures=watch(fresh);
    await start(fresh);await fresh.evaluate(data=>window.SWYRL_ENGINE_STORYBOARD.importProject(data),exported);await frames(fresh);
    assert.deepEqual((await project(fresh)).project.animeScenery,exported.project.animeScenery,'Fresh import changed portable scenery');
    safe(await seek(fresh,17.25),mode.name+' imported layered shot');detailedScenery(await rendered(fresh),mode.name+' imported theatre');
    actualObject(await rendered(fresh),'arches-left',key,mode.name+' imported arch',configuredArch.position);
    await chooseObject(fresh,'background','arches-left',17.25);await fresh.locator('#sceneryDeleteKey').click();
    assert.equal(keyAt(await model(fresh),'arches-left',17.25),undefined,'Delete Object Key failed');
    await closeStudio(fresh);await historyAction(fresh,'undo');await frames(fresh);
    assert.deepEqual(keyAt(await model(fresh),'arches-left',17.25),key,'Undo object deletion failed');
    await seek(fresh,17.25);actualObject(await rendered(fresh),'arches-left',key,mode.name+' imported Undo',configuredArch.position);
    noFailures(freshFailures,mode.name+' portable depth import');await freshContext.close();

    noFailures(failures,mode.name+' native scenery authoring/Play');
    console.log('DEPTH_THEATRE_'+mode.name.toUpperCase()+'_PASS',JSON.stringify({screenshots:output}));
  }
  allPassed=true;
}finally{await browser.close();}
if(allPassed)console.log(modes.length===2?'DEPTH_THEATRE_BOTH_VIEWPORTS_PASSED':'DEPTH_THEATRE_SELECTED_VIEWPORT_PASSED');
