import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {mkdir,readFile} from 'node:fs/promises';
import {resolve} from 'node:path';

// Save real editor keys and inspect the meshes/pivots actually rendered by Play.
// These checks deliberately compare render state with authored state: a detached
// pose panel, a single flat character image, or a lost import must fail.
const base=(process.env.SWYRL_ANIME_TEST_URL||'http://127.0.0.1:8768').replace(/\/$/,'');
const output=resolve(process.env.SWYRL_ANIME_SCREENSHOTS_DIR||'character-rig-acceptance');
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
const model=(page,character)=>page.evaluate(character=>window.SWYRL_ENGINE_RIG.model(character),character);
const rendered=(page,character)=>page.evaluate(character=>window.SWYRL_ENGINE_RIG.renderStatus(character),character);
const project=page=>page.evaluate(()=>window.SWYRL_ENGINE_ANIMATION.serializedProject());
const stage=page=>page.evaluate(()=>window.SWYRL_ENGINE_STORYBOARD.stageStatus());
const status=page=>page.evaluate(()=>window.SWYRL_ENGINE_ANIMATION.status());
const frames=page=>page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
const keyAt=(rig,part,time)=>rig.tracks[part].find(key=>Math.abs(key.time-time)<1e-6);
const close=(actual,expected,label,tolerance=1e-5)=>assert.ok(Number.isFinite(actual)&&Math.abs(actual-expected)<=tolerance,
  label+': expected '+expected+', received '+actual);
const distance=(a,b)=>Math.hypot(...a.map((value,index)=>value-b[index]));
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
  assert.deepEqual(failures.artwork,[],'Character artwork failed: '+label);
}
async function start(page){
  await page.bringToFront();
  await page.goto(base+'/index.html?project=anime-ghosts-ep01',{waitUntil:'domcontentloaded',timeout:60000});
  await page.waitForFunction(()=>window.SWYRL_ENGINE_RIG&&window.SWYRL_ENGINE_ANIMATION&&window.SWYRL_ENGINE_STORYBOARD,
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
  const quick=page.locator(action==='undo'?'#quickUndoBtn':'#quickRedoBtn');
  if(await quick.isVisible()){await quick.click();return;}
  await page.locator('#mobileToolsBtn').click();
  await page.locator('#mobileToolsPanel [data-click="'+action+'Btn"]').click();
}
async function seek(page,time){
  assert.equal(await page.evaluate(time=>window.SWYRL_ENGINE_ANIMATION.seek(time),time),true,'Seek failed at '+time+'s');
  await frames(page);return stage(page);
}
async function choosePart(page,character,part,time){
  await openStudio(page);await page.locator('#storyTrack').selectOption(character);
  await input(page,'#storyTime',time);await page.locator('#rigPart').selectOption(part);
}
async function limbKey(page,character,part,time,values){
  await choosePart(page,character,part,time);
  for(const [name,value] of Object.entries(values))await input(page,'#rig'+name[0].toUpperCase()+name.slice(1),value);
  await page.locator('#rigAddKey').click();await frames(page);
  const key=keyAt(await model(page,character),part,time);
  assert.ok(key,'Native UI did not save '+character+'.'+part+' at '+time+'s');
  for(const [field,value] of Object.entries(values))close(key[field],field.startsWith('rotation')?value*Math.PI/180:value,
    'Native UI '+character+'.'+part+'.'+field);
  return key;
}
async function faceKey(page,character,time,values){
  await choosePart(page,character,'face',time);
  await page.locator('#rigExpression').selectOption(values.expression);
  for(const [name,value] of Object.entries(values))if(name!=='expression')await input(page,'#rig'+name[0].toUpperCase()+name.slice(1),value);
  await page.locator('#rigAddKey').click();await frames(page);
  const key=keyAt(await model(page,character),'face',time);
  assert.ok(key,'Native UI did not save '+character+' facial expression');
  assert.equal(key.expression,values.expression);close(key.blink,values.blink,'Saved blink');close(key.mouth,values.mouth,'Saved mouth');
  assert.equal(key.speech,values.speech,'Saved speech switch');return key;
}
function safe(observation,label){
  assert.equal(observation.occlusionSafe,true,'Rigged actors/scenery entered the camera: '+label);
  assert.deepEqual(observation.assetErrors||[],[],'Artwork failed: '+label);
  assert.ok(observation.safeCameraGap>6,'Camera moved through a popped-out character: '+label);
  for(const id of ['kami','swyrlz']){
    const actor=observation.castBounds.find(actor=>actor.id===id);
    assert.ok(actor&&actor.visible,id+' is hidden: '+label);
    assert.ok(actor.width>.035&&actor.height>.08,id+' is too small to read: '+label);
    assert.ok(actor.right>0&&actor.left<1&&actor.bottom>0&&actor.top<1,id+' is outside the shot: '+label);
  }
}
function hasDepth(rig,label){
  assert.equal(rig.rigged,true,'A flat image replaced the character rig: '+label);
  assert.ok(rig.partCount>=18,'Too few independently poseable character parts: '+label);
  assert.ok(rig.meshCount>=rig.partCount*3,'Character parts lack front/back/edge geometry: '+label);
  assert.ok(rig.thickness>0&&rig.depthSpan>.05,'Character has no real pop-out depth: '+label);
  assert.ok(rig.bounds.max[2]-rig.bounds.min[2]>.05,'Actual rig geometry remains a flat plane: '+label);
  for(const id of ['head','leftUpperArm','leftForearm','rightHand','leftUpperLeg','rightLowerLeg','cape']){
    const joint=rig.joints[id];assert.ok(joint,'Missing independently articulated '+id+': '+label);
    assert.ok(joint.rotation.every(Number.isFinite)&&joint.worldPosition.every(Number.isFinite)&&joint.partWorldPosition.every(Number.isFinite),
      'Non-finite rendered joint: '+label+' '+id);
  }
}
function actualJoint(rig,part,key,label){
  const joint=rig.joints[part];assert.ok(joint,'Missing rendered '+part+': '+label);
  for(const [axis,field] of ['rotationX','rotationY','rotationZ'].entries())close(joint.rotation[axis],key[field],
    'Saved key did not rotate the actual '+part+' '+field+': '+label,.002);
}
function paintedRegions(face,label){
  const art=face.paintedFeatures;
  assert.ok(art?.asset&&art.inkHash&&art.regions,'Animated facial controls are not compositing painted feature pixels: '+label);
  for(const id of ['leftEye','rightEye','nose','mouth']){
    const region=art.regions[id];
    assert.ok(region&&typeof region.inkHash==='string'&&region.inkHash.length>0&&region.alphaPixels>0,
      'No measured painted pixels in facial region '+id+': '+label);
  }
  return art.regions;
}
async function paintedFaceControls(page,character,time,label){
  const original=await model(page,character),baseFace={expression:'neutral',blink:0,mouth:0,speech:false,
    gazeX:0,gazeY:0,smile:0,brow:0};
  await faceKey(page,character,time,baseFace);await seek(page,time);
  const open=paintedRegions((await rendered(page,character)).face,label+' neutral');
  const minimumWidths=character==='kami'?{leftEye:62,rightEye:62,mouth:40}:{leftEye:66,rightEye:66,mouth:53};
  for(const [id,width] of Object.entries(minimumWidths)){
    const bounds=open[id].canvasInkBounds;
    assert.ok(bounds?.min?.length===2&&bounds.max?.length===2&&bounds.max[0]-bounds.min[0]>=width,
      'Painted '+id+' is still as small as the original facial features: '+label);
  }
  for(const [field,value,changed,unchanged] of [
    ['blink',1,['leftEye','rightEye'],['nose','mouth']],
    ['gazeX',.75,['leftEye','rightEye'],['nose','mouth']],
    ['mouth',.9,['mouth'],['leftEye','rightEye','nose']]
  ]){
    await faceKey(page,character,time,{...baseFace,[field]:value});await seek(page,time);
    const actual=paintedRegions((await rendered(page,character)).face,label+' '+field);
    for(const id of changed)assert.notEqual(actual[id].inkHash,open[id].inkHash,
      'The native '+field+' control changes metadata without changing painted '+id+' pixels: '+label);
    for(const id of unchanged)assert.equal(actual[id].inkHash,open[id].inkHash,
      'The native '+field+' control repaints unrelated '+id+' pixels: '+label);
    if(field==='blink')for(const id of changed)assert.ok(actual[id].alphaPixels<open[id].alphaPixels,
      'Closing the eyelids does not reduce the actual painted eye aperture: '+label+' '+id);
    await closeStudio(page);await historyAction(page,'undo');await seek(page,time);
    const restored=paintedRegions((await rendered(page,character)).face,label+' Undo '+field);
    for(const id of ['leftEye','rightEye','nose','mouth'])assert.equal(restored[id].inkHash,open[id].inkHash,
      'One native Undo restores face settings without restoring actual painted '+id+' pixels: '+label);
  }
  await closeStudio(page);await historyAction(page,'undo');await seek(page,time);
  assert.deepEqual(await model(page,character),original,'Painted facial control checks lose original authored keys: '+label);
}

let allPassed=false;
try{
  for(const mode of modes){
    const options={viewport:mode.viewport,isMobile:mode.isMobile,hasTouch:mode.hasTouch,acceptDownloads:true};
    const context=await browser.newContext(options),page=await context.newPage(),failures=watch(page);
    await start(page);
    const original=await project(page),originalScene=nativeScene(original);
    assert.equal(original.project.animeRigs?.schema,'anime-character-rigs-v1','Starter has no portable character rigs');
    assert.deepEqual(Object.keys(original.project.animeRigs.characters).sort(),['kami','swyrlz'],'The two mages need separate saved rigs');
    const bodyTracks=original.project.animeTimeline.tracks;
    assert.equal(Object.keys(bodyTracks).length,9,'Rigging replaced the independent story/camera tracks');
    safe(await seek(page,17.25),mode.name+' initial rigged shot');
    const initialKami=await rendered(page,'kami'),initialCompanion=await rendered(page,'swyrlz');
    hasDepth(initialKami,mode.name+' Kami');hasDepth(initialCompanion,mode.name+' §wyrlz');
    const companionBefore=await model(page,'swyrlz');

    // A forearm moves in depth and around its own elbow. Its sibling arm and
    // the other character retain their exact pose at the same saved playhead.
    const beforeArm=initialKami.joints.leftForearm,otherArm=initialKami.joints.rightForearm;
    const arm=await limbKey(page,'kami','leftForearm',17.25,{rotationX:7,rotationY:25,rotationZ:-18,depth:.28});
    await seek(page,17.25);const afterArm=await rendered(page,'kami');
    actualJoint(afterArm,'leftForearm',arm,mode.name+' native forearm key');
    assert.ok(distance(afterArm.joints.leftForearm.partWorldPosition,beforeArm.partWorldPosition)>.02,
      'The authored forearm rotates only metadata, not its visible part');
    assert.ok(distance(afterArm.joints.leftHand.partWorldPosition,initialKami.joints.leftHand.partWorldPosition)>.02,
      'The hand detached from its articulated forearm parent');
    assert.deepEqual(afterArm.joints.rightForearm,otherArm,'Posing the left forearm altered its independent sibling');
    assert.deepEqual(await model(page,'swyrlz'),companionBefore,'Posing Kami altered the companion rig');
    assert.deepEqual((await project(page)).project.animeTimeline.tracks,bodyTracks,'Limb keys altered whole-body or camera animation');
    await closeStudio(page);await historyAction(page,'undo');await frames(page);
    assert.equal(keyAt(await model(page,'kami'),'leftForearm',17.25),undefined,'Undo did not remove the limb key');
    await historyAction(page,'redo');await frames(page);
    assert.deepEqual(keyAt(await model(page,'kami'),'leftForearm',17.25),arm,'Redo lost the limb pose');
    actualJoint(await renderedAfterSeek(page,'kami',17.25),'leftForearm',arm,mode.name+' limb Redo');

    for(const character of ['kami','swyrlz'])await paintedFaceControls(page,character,17.25,mode.name+' '+character);
    // Face controls repaint the real facial surface; they are neither a caption
    // nor a character-wide texture replacement. The companion is independent.
    const faceBefore=(await rendered(page,'kami')).face;
    const face=await faceKey(page,'kami',17.25,{expression:'happy',blink:.8,mouth:.7,speech:false});
    await seek(page,17.25);const faceAfter=(await rendered(page,'kami')).face;
    assert.equal(faceAfter.expression,'happy','Rendered face ignores saved expression');
    close(faceAfter.blink,.8,'Rendered eyelids ignore blink',.01);
    assert.ok(faceAfter.mouth>.3,'Rendered mouth did not open');
    assert.notEqual(faceAfter.textureVersion,faceBefore.textureVersion,'Facial expression did not change the painted face surface');
    assert.deepEqual(await model(page,'swyrlz'),companionBefore,'Kami facial edits altered the companion');
    await closeStudio(page);await historyAction(page,'undo');await frames(page);
    assert.equal(keyAt(await model(page,'kami'),'face',17.25),undefined,'Undo did not remove the facial key');
    await historyAction(page,'redo');await frames(page);
    assert.deepEqual(keyAt(await model(page,'kami'),'face',17.25),face,'Redo lost the facial expression');
    await limbKey(page,'swyrlz','rightUpperArm',17.25,{rotationX:-5,rotationY:-20,rotationZ:26,depth:.18});
    const companionFace=await faceKey(page,'swyrlz',17.25,{expression:'surprised',blink:.15,mouth:.5,speech:false});
    await seek(page,17.25);
    assert.equal((await rendered(page,'swyrlz')).face.expression,companionFace.expression,'§wyrlz has no independent facial expression');
    assert.equal((await rendered(page,'kami')).face.expression,face.expression,'The companion replaced Kami’s expression');

    // Configuration builds actual thickness/depth, and is saved with the rig.
    const beforeDepthConfig=await rendered(page,'kami');
    await choosePart(page,'kami','head',17.25);
    await input(page,'#rigEnabled',true);await input(page,'#rigThickness',.12);await input(page,'#rigDepthAmount',.4);
    await page.locator('#rigApplyConfig').click();await seek(page,17.25);
    const configured=await rendered(page,'kami');hasDepth(configured,mode.name+' configured depth');
    close(configured.thickness,.12,'Thickness control does not rebuild the character geometry',.003);
    assert.ok(['head','cape','torso','staff'].some(part=>
      distance(configured.joints[part].surfaceWorldPosition,beforeDepthConfig.joints[part].surfaceWorldPosition)>.02),
    'Pop-out depth changed only saved settings, not actual painted surface geometry');
    for(const connection of configured.connections)
      assert.ok(connection.error<1e-5,'Changing paper depth separates a snapped socket: '+connection.child);
    safe(await stage(page),mode.name+' configured depth safety');
    await page.screenshot({path:resolve(output,'character-rig-'+mode.name+'-editor.png')});
    const downloadPending=page.waitForEvent('download',{timeout:15000});
    await page.locator('#storySaveProject').click();
    const download=await downloadPending,exported=JSON.parse(await readFile(await download.path(),'utf8'));
    assert.deepEqual(exported.project.animeRigs,(await project(page)).project.animeRigs,'Save Project lost joint, face, or depth data');
    assert.deepEqual(nativeScene(exported),originalScene,'Rig preview mutated native editor actors or layers');

    // Native Play, paused pose editing, and Stop share the same saved rig.
    await closeStudio(page);await page.evaluate(()=>window.SWYRL_ENGINE_STORYBOARD.exitPreview());await frames(page);
    const editorCamera=(await stage(page)).editorCamera;
    await page.locator('#playBtn').click();
    await page.waitForFunction(()=>window.SWYRL_ENGINE_ANIMATION.status().active,undefined,{timeout:15000});
    await page.locator('#animeCinePause').click();assert.equal((await status(page)).paused,true,'Native Play did not pause');
    await seek(page,17.25);actualJoint(await rendered(page,'kami'),'leftForearm',arm,mode.name+' native Play');
    assert.equal((await rendered(page,'kami')).face.expression,'happy','Play ignores authored facial keys');
    const pausedTime=(await status(page)).elapsed;await frames(page);close((await status(page)).elapsed,pausedTime,'Paused playhead advanced',.001);
    const pausedHand=await limbKey(page,'kami','rightHand',18.5,{rotationX:10,rotationY:12,rotationZ:-24,depth:.21});
    await closeStudio(page);
    for(const time of [12,17.25,18.5,45,72,110,130]){
      safe(await seek(page,time),mode.name+' Play '+time+'s');
      hasDepth(await rendered(page,'kami'),mode.name+' Play Kami '+time+'s');
      hasDepth(await rendered(page,'swyrlz'),mode.name+' Play §wyrlz '+time+'s');
    }
    await seek(page,17.25);await page.screenshot({path:resolve(output,'character-rig-'+mode.name+'-play.png')});
    await page.locator('#animeCineExit').click();await frames(page);
    assert.equal((await status(page)).playing,false,'Stop failed to return to the editor');
    assert.deepEqual(keyAt(await model(page,'kami'),'rightHand',18.5),pausedHand,'Stop discarded a paused limb edit');
    assert.deepEqual(nativeScene(await project(page)),originalScene,'Play/Stop altered native editor actors/layers');
    assert.deepEqual((await stage(page)).editorCamera,editorCamera,'Rigged Play did not restore the editor camera');

    // Import into a clean browser: no previous rig nodes, texture cache, or UI
    // state may rescue a broken portable Save/Load implementation.
    // All primary checks and snapshots are complete. The portable import uses
    // a fresh context with no still-rendering primary scene to rescue its data.
    await context.close();
    const freshContext=await browser.newContext(options),fresh=await freshContext.newPage(),freshFailures=watch(fresh);
    await start(fresh);await fresh.evaluate(data=>window.SWYRL_ENGINE_STORYBOARD.importProject(data),exported);await frames(fresh);
    assert.deepEqual((await project(fresh)).project.animeRigs,exported.project.animeRigs,'Fresh import changed the saved rigs');
    safe(await seek(fresh,17.25),mode.name+' imported character shot');
    actualJoint(await rendered(fresh,'kami'),'leftForearm',arm,mode.name+' imported forearm');
    assert.equal((await rendered(fresh,'kami')).face.expression,'happy','Fresh import lost the facial expression');
    await choosePart(fresh,'kami','leftForearm',17.25);await fresh.locator('#rigDeleteKey').click();
    assert.equal(keyAt(await model(fresh,'kami'),'leftForearm',17.25),undefined,'Delete Joint Key failed');
    await closeStudio(fresh);await historyAction(fresh,'undo');await frames(fresh);
    assert.deepEqual(keyAt(await model(fresh,'kami'),'leftForearm',17.25),arm,'Undo joint deletion failed');
    actualJoint(await renderedAfterSeek(fresh,'kami',17.25),'leftForearm',arm,mode.name+' imported Undo');

    // Older portable projects have no rig section. Malformed new pose data
    // must also be bounded before it reaches Three.js or canvas face painting.
    const old=structuredClone(exported);delete old.project.animeRigs;
    await fresh.evaluate(data=>window.SWYRL_ENGINE_STORYBOARD.importProject(data),old);await frames(fresh);
    safe(await seek(fresh,12),mode.name+' older project without rig metadata');
    const bad=structuredClone(exported),badKami=bad.project.animeRigs.characters.kami;
    badKami.thickness=1e99;badKami.depth=-1e99;
    badKami.joints.head=[{time:-100,rotationX:1e99,rotationY:'NaN',rotationZ:null,depth:1e99},
      {time:1e99,rotationX:-1e99,rotationY:Infinity,rotationZ:'bad',depth:-1e99}];
    badKami.face=[{time:0,expression:'<script>bad</script>',blink:1e99,mouth:-1e99,gazeX:Infinity,brow:'NaN',speech:'yes'}];
    await fresh.evaluate(data=>window.SWYRL_ENGINE_STORYBOARD.importProject(data),bad);await frames(fresh);
    const sanitized=await model(fresh,'kami'),duration=exported.project.animeTimeline.duration;
    for(const [part,keys] of Object.entries(sanitized.tracks)){
      assert.equal(keys[0].time,0,'Missing initial '+part+' key after malformed import');
      assert.equal(keys.at(-1).time,duration,'Missing final '+part+' key after malformed import');
      for(const key of keys)for(const [field,value] of Object.entries(key)){
        if(typeof value==='number')assert.ok(Number.isFinite(value),'Non-finite imported '+part+'.'+field);
        if(field==='depth')assert.ok(value>=-.3&&value<=.65,'Imported joint depth escaped bounds');
        if(field.startsWith('rotation'))assert.ok(Math.abs(value)<=Math.PI,'Imported joint angle escaped safe bounds');
        if(field==='blink'||field==='mouth')assert.ok(value>=0&&value<=1,'Imported expression escaped bounds');
        if(field==='expression')assert.ok(['neutral','happy','determined','surprised','sad'].includes(value),'Unknown expression reached face renderer');
      }
    }
    safe(await seek(fresh,12),mode.name+' sanitized malformed rig');

    // The existing single-image artwork tool keeps its visible behavior. A
    // replacement cel must not silently disappear behind the puppet atlas;
    // one native Undo restores both the prior art and the articulated mode.
    await fresh.evaluate(data=>window.SWYRL_ENGINE_STORYBOARD.importProject(data),exported);await frames(fresh);
    await choosePart(fresh,'kami','head',17.25);
    const replacementPng=await fresh.evaluate(()=>{
      const canvas=document.createElement('canvas');canvas.width=canvas.height=16;
      const context=canvas.getContext('2d');context.fillStyle='#d4a75f';context.fillRect(0,0,16,16);
      return canvas.toDataURL('image/png').split(',')[1];
    });
    await fresh.locator('#storyArtwork').setInputFiles({name:'replacement-cel.png',mimeType:'image/png',buffer:Buffer.from(replacementPng,'base64')});
    await fresh.waitForFunction(()=>window.SWYRL_ENGINE_ANIMATION.serializedProject().project.animeRigs.characters.kami.enabled===false,
      undefined,{timeout:15000});
    await fresh.waitForFunction(()=>window.SWYRL_ENGINE_STORYBOARD.stageStatus().assetsReady,undefined,{timeout:15000});
    safe(await seek(fresh,17.25),mode.name+' replacement character cel');
    assert.equal((await rendered(fresh,'kami')).rigged,false,'Imported single-image artwork remained hidden behind the rig atlas');
    assert.ok((await project(fresh)).scene.actors.find(actor=>actor.storyVisual?.layer==='kami').storyVisual.asset.startsWith('data:image/png;'),
      'The imported character artwork was not saved');
    await closeStudio(fresh);await historyAction(fresh,'undo');await frames(fresh);
    await seek(fresh,17.25);hasDepth(await rendered(fresh,'kami'),mode.name+' one Undo restores character rig');
    assert.deepEqual((await project(fresh)).project.animeRigs,exported.project.animeRigs,
      'Artwork replacement took more than one Undo to restore the saved puppet');
    noFailures(freshFailures,mode.name+' portable rig import');await freshContext.close();
    noFailures(failures,mode.name+' native rig authoring/Play');
    console.log('CHARACTER_RIG_'+mode.name.toUpperCase()+'_PASS',JSON.stringify({parts:{kami:initialKami.partCount,swyrlz:initialCompanion.partCount},
      meshes:{kami:initialKami.meshCount,swyrlz:initialCompanion.meshCount},screenshots:output}));
  }
  allPassed=true;
}finally{await browser.close();}
if(allPassed)console.log(modes.length===2?'CHARACTER_RIG_BOTH_VIEWPORTS_PASSED':'CHARACTER_RIG_SELECTED_VIEWPORT_PASSED');

async function renderedAfterSeek(page,character,time){await seek(page,time);return rendered(page,character);}
