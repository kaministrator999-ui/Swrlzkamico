import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {mkdir,readFile} from 'node:fs/promises';
import {resolve} from 'node:path';

// A body-piece fit must rebuild the painted WebGL puppet, preserve animation,
// and survive native Save/Load. Attachment checks inspect actual alpha edges.
const base=(process.env.SWYRL_ANIME_TEST_URL||'http://127.0.0.1:8773').replace(/\/$/,'');
const output=resolve(process.env.SWYRL_ANIME_SCREENSHOTS_DIR||'character-alignment-acceptance');
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
const model=(page,character)=>page.evaluate(character=>window.SWYRL_ENGINE_RIG.model(character),character);
const rendered=(page,character)=>page.evaluate(character=>window.SWYRL_ENGINE_RIG.renderStatus(character),character);
const stage=page=>page.evaluate(()=>window.SWYRL_ENGINE_STORYBOARD.stageStatus());
const status=page=>page.evaluate(()=>window.SWYRL_ENGINE_ANIMATION.status());
const frames=page=>page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
const close=(actual,expected,label,tolerance=1e-5)=>assert.ok(Number.isFinite(actual)&&Math.abs(actual-expected)<=tolerance,
  label+': expected '+expected+', received '+actual);
const distance=(a,b)=>Math.hypot(...a.map((value,index)=>value-b[index]));
const nativeScene=saved=>({background:saved.scene.background,layers:saved.editor.layers,
  actors:saved.scene.actors.map(actor=>({id:actor.id,type:actor.type,position:actor.position,
    rotation:actor.rotation,scale:actor.scale,manualVisible:actor.manualVisible,editorLayerIds:actor.editorLayerIds}))});
const poseKeys=saved=>Object.fromEntries(Object.entries(saved.project.animeRigs.characters)
  .map(([id,config])=>[id,{joints:config.joints,face:config.face}]));
const keyCount=saved=>Object.values(poseKeys(saved)).reduce((count,config)=>count+config.face.length+
  Object.values(config.joints).reduce((sum,keys)=>sum+keys.length,0),0);

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
  assert.deepEqual(failures.artwork,[],'Puppet artwork failed: '+label);
}
async function start(page){
  await page.goto(base+'/index.html?project=anime-ghosts-ep01',{waitUntil:'domcontentloaded',timeout:60000});
  await page.waitForFunction(()=>window.SWYRL_ENGINE_RIG?.fitPart&&window.SWYRL_ENGINE_RIG?.resetPartFit&&
    window.SWYRL_ENGINE_SCENERY&&window.SWYRL_ENGINE_ANIMATION&&window.SWYRL_ENGINE_STORYBOARD,
    undefined,{timeout:60000});
  await page.waitForFunction(()=>{const state=window.SWYRL_ENGINE_STORYBOARD.stageStatus();
    return state.assetsReady||state.assetErrors?.length;},undefined,{timeout:45000});
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
  // The phone's cinematic preview hides the editor sheet. Use the native
  // editor controls after returning from a non-playing preview.
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
async function choosePart(page,character,part,time){
  await openStudio(page);await page.locator('#storyTrack').selectOption(character);
  await input(page,'#storyTime',time);await page.locator('#rigPart').selectOption(part);await frames(page);
}
async function fitPiece(page,character,part,time,fit){
  await choosePart(page,character,part,time);
  for(const [field,value] of Object.entries(fit))
    await input(page,'#rigFit'+field[0].toUpperCase()+field.slice(1),field==='rotationZ'?value*180/Math.PI:value);
  await page.locator('#rigApplyFit').click();await seek(page,time);
  const saved=(await model(page,character)).layout[part];
  for(const [field,value] of Object.entries(fit))close(saved[field],value,'Native body-piece fit '+character+'.'+part+'.'+field,.002);
  return saved;
}
function safe(observation,label,cast=true){
  assert.equal(observation.occlusionSafe,true,'Puppet/scenery obstructs the camera: '+label);
  assert.deepEqual(observation.assetErrors||[],[],'Artwork failed: '+label);
  assert.ok(observation.safeCameraGap>6,'Camera enters the popped-out puppet: '+label);
  for(const plate of observation.scenery)
    assert.ok(plate.frontZ<=plate.z+.001,'Folding scenery crosses its parent hinge: '+label+' '+plate.id);
  if(cast)for(const id of ['kami','swyrlz']){
    const actor=observation.castBounds.find(actor=>actor.id===id);
    assert.ok(actor&&actor.visible,id+' is hidden: '+label);
    assert.ok(actor.width>.035&&actor.height>.08,id+' is too small to read: '+label);
    assert.ok(actor.right>0&&actor.left<1&&actor.bottom>0&&actor.top<1,id+' leaves the shot: '+label);
  }
}
function attachments(rig,label){
  assert.equal(rig.rigged,true,'A single flat cel replaced the articulated puppet: '+label);
  assert.ok(rig.partCount>=18&&rig.meshCount>=rig.partCount*3,'Missing painted front/back/edge body pieces: '+label);
  assert.ok(rig.depthSpan>.05,'The articulated character has no pop-out depth: '+label);
  assert.ok(Array.isArray(rig.attachments)&&rig.attachments.length>=15,'Missing measured body-piece seams: '+label);
  for(const seam of rig.attachments){
    assert.ok(seam.anchor?.every(Number.isFinite)&&seam.parentPoint?.every(Number.isFinite)&&seam.childPoint?.every(Number.isFinite),
      'Attachment has no actual alpha-edge points around its joint: '+label+' '+seam.id);
    assert.ok(Number.isFinite(seam.parentGap)&&Number.isFinite(seam.childGap),
      'Attachment does not measure both actual painted edges: '+label+' '+seam.id);
    assert.ok(Number.isFinite(seam.gap)&&Number.isFinite(seam.limit)&&seam.limit>0&&seam.limit<=.32,
      'Non-finite painted attachment: '+label+' '+seam.id);
    close(Math.max(seam.parentGap,seam.childGap),seam.gap,'Attachment ignores one painted edge: '+label+' '+seam.id,.003);
    close(distance(seam.anchor,seam.parentPoint),seam.parentGap,'Attachment parent distance ignores the painted edge: '+label+' '+seam.id,.003);
    close(distance(seam.anchor,seam.childPoint),seam.childGap,'Attachment child distance ignores the painted edge: '+label+' '+seam.id,.003);
    if(seam.visible)assert.ok(seam.gap<=seam.limit,'Visible body pieces detach at '+seam.id+': '+label+' gap '+seam.gap+' > '+seam.limit);
  }
}
function facialAlignment(rig,character,label){
  const skin={kami:{min:[-.43,-.40],max:[.24,.065]},swyrlz:{min:[-.4,-.88],max:[.45,-.36]}};
  const face=rig.face;
  assert.ok(face.pixelCount>100&&face.featureInkBounds&&face.canvasInkBounds,'Missing actual facial ink: '+label);
  for(const axis of [0,1])assert.ok(face.featureInkBounds.min[axis]>=skin[character].min[axis]&&
    face.featureInkBounds.max[axis]<=skin[character].max[axis],
    'Moving body pieces displaces the face into the hair, chin or neck: '+label+' '+character);
}
function independent(saved,original,label){
  assert.deepEqual(poseKeys(saved),poseKeys(original),'Piece fitting overwrote authored poses or expressions: '+label);
  assert.equal(keyCount(saved),425,'Piece fitting lost the 425 original character keys: '+label);
  assert.deepEqual(saved.project.animeTimeline,original.project.animeTimeline,'Piece fitting altered the story/camera timeline: '+label);
  assert.deepEqual(saved.project.animeScenery,original.project.animeScenery,'Piece fitting altered independently layered scenery: '+label);
  assert.deepEqual(nativeScene(saved),nativeScene(original),'Piece fitting mutated editor actors or layers: '+label);
}
function changedGeometry(before,after,label){
  assert.ok(before.alphaBounds&&after.alphaBounds,'Missing actual painted-part bounds: '+label);
  assert.ok(distance(before.worldPosition,after.worldPosition)>.025,'Fitting changed metadata without moving the visible cutout: '+label);
  assert.ok(distance(before.alphaBounds.min,after.alphaBounds.min)+distance(before.alphaBounds.max,after.alphaBounds.max)>.04,
    'Fitting changed metadata without rebuilding the painted geometry: '+label);
}
function sameJoint(before,after,label){
  for(const field of ['position','rotation','worldPosition','partWorldPosition'])
    before[field].forEach((value,index)=>close(after[field][index],value,label+' '+field+'.'+index,.002));
}

let allPassed=false;
try{
  for(const mode of modes){
    const options={viewport:mode.viewport,isMobile:mode.isMobile,hasTouch:mode.hasTouch,acceptDownloads:true};
    const context=await browser.newContext(options),page=await context.newPage(),failures=watch(page);
    await start(page);
    const original=await project(page),baselineLayouts={};
    assert.equal(keyCount(original),425,'Starter character animation changed before body-piece fitting');
    assert.equal(Object.values(original.project.animeScenery.objects).reduce((sum,item)=>sum+item.keys.length,0),341,
      'Starter lost its independently animated scenery');
    for(const character of ['kami','swyrlz']){
      const rig=await model(page,character);baselineLayouts[character]=rig.layout;
      assert.equal(Object.keys(rig.layout).length,19,'Missing portable joint/painted-card rest fits');
      const detached=await page.evaluate(character=>{
        const view=window.SWYRL_ENGINE_RIG.model(character);view.layout.leftForearm.x=999;
        return window.SWYRL_ENGINE_RIG.model(character).layout.leftForearm.x;
      },character);
      assert.notEqual(detached,999,'The public fit model exposes mutable project data');
    }
    // Inspect both animated bodies at real unfolding frames and every later
    // shot. This catches gaps that only appear when an elbow/knee is bent.
    await page.locator('#playBtn').click();
    await page.waitForFunction(()=>window.SWYRL_ENGINE_ANIMATION.status().active,undefined,{timeout:15000});
    await page.locator('#animeCinePause').click();
    for(const time of [0,.2,1,2,4,7,9,12,19,72,110,134]){
      safe(await seek(page,time),mode.name+' authored '+time+'s',time>=12);
      for(const character of ['kami','swyrlz']){
        const rig=await rendered(page,character);attachments(rig,mode.name+' '+character+' '+time+'s');
        facialAlignment(rig,character,mode.name+' '+time+'s');
      }
      if([19,72,110].includes(time))await page.screenshot({path:resolve(output,'character-alignment-'+mode.name+'-authored-'+time+'.png')});
    }
    await page.locator('#animeCineExit').click();await frames(page);
    independent(await project(page),original,mode.name+' authored native Play/Stop');
    await seek(page,17.25);
    const before=await rendered(page,'kami'),companionBefore=await rendered(page,'swyrlz'),part='leftForearm',defaultFit=baselineLayouts.kami[part];
    const fit={...defaultFit,x:defaultFit.x+.055,y:defaultFit.y-.045,width:defaultFit.width*1.1,
      height:defaultFit.height*1.08,artX:defaultFit.artX+.065,artY:defaultFit.artY-.035,rotationZ:defaultFit.rotationZ+.04};
    const authoredFit=await fitPiece(page,'kami',part,17.25,fit),after=await rendered(page,'kami');
    changedGeometry(before.pieces[part],after.pieces[part],mode.name+' native forearm fit');
    close(after.pieces[part].width/before.pieces[part].width,authoredFit.width/defaultFit.width,
      'Body width fit did not rebuild the actual front geometry',.002);
    close(after.pieces[part].height/before.pieces[part].height,authoredFit.height/defaultFit.height,
      'Body height fit did not rebuild the actual front geometry',.002);
    assert.ok(distance(before.joints.leftHand.worldPosition,after.joints.leftHand.worldPosition)>.02,
      'The fitted forearm moved without its attached hand');
    sameJoint(before.joints.rightForearm,after.joints.rightForearm,'Fitting the left arm altered its independent right sibling');
    sameJoint(companionBefore.joints.head,(await rendered(page,'swyrlz')).joints.head,'Fitting Kami altered §wyrlz');
    const fitted=await project(page);independent(fitted,original,mode.name+' body fit');
    for(const id of Object.keys(baselineLayouts.kami))if(id!==part)
      assert.deepEqual(fitted.project.animeRigs.characters.kami.layout[id],baselineLayouts.kami[id],'Fitting one part altered '+id);
    assert.deepEqual(fitted.project.animeRigs.characters.swyrlz,original.project.animeRigs.characters.swyrlz,'Fitting Kami altered the companion model');
    await closeStudio(page);await historyAction(page,'undo');await seek(page,17.25);
    assert.deepEqual((await model(page,'kami')).layout[part],defaultFit,'Undo did not restore the body-piece fit');
    sameJoint(before.joints[part],(await rendered(page,'kami')).joints[part],'Undo did not restore the actual forearm');
    await historyAction(page,'redo');await seek(page,17.25);
    assert.deepEqual((await model(page,'kami')).layout[part],authoredFit,'Redo lost the body-piece fit');
    sameJoint(after.joints[part],(await rendered(page,'kami')).joints[part],'Redo did not restore actual forearm geometry');
    await choosePart(page,'kami',part,17.25);await page.locator('#rigResetFit').click();await seek(page,17.25);
    const resetFit=(await model(page,'kami')).layout[part];
    for(const [field,value] of Object.entries(defaultFit))
      close(resetFit[field],value,'Reset Piece Fit did not restore the assembled default '+field,1e-6);
    attachments(await rendered(page,'kami'),mode.name+' reset default seams');
    independent(await project(page),original,mode.name+' reset body fit');
    await closeStudio(page);await historyAction(page,'undo');await seek(page,17.25);
    assert.deepEqual((await model(page,'kami')).layout[part],authoredFit,'One Undo did not restore the custom fit after reset');

    await choosePart(page,'kami',part,17.25);
    await page.screenshot({path:resolve(output,'character-alignment-'+mode.name+'-editor.png')});
    const downloadPending=page.waitForEvent('download',{timeout:15000});await page.locator('#storySaveProject').click();
    const download=await downloadPending,exported=JSON.parse(await readFile(await download.path(),'utf8'));
    assert.deepEqual(exported.project.animeRigs,(await project(page)).project.animeRigs,'Save Project lost the body-piece fits');
    independent(exported,original,mode.name+' saved fit');

    await closeStudio(page);await page.evaluate(()=>window.SWYRL_ENGINE_STORYBOARD.exitPreview());await frames(page);
    const editorCamera=(await stage(page)).editorCamera;
    await page.locator('#playBtn').click();
    await page.waitForFunction(()=>window.SWYRL_ENGINE_ANIMATION.status().active,undefined,{timeout:15000});
    await openStudio(page);await page.locator('#storyTrack').selectOption('kami');await page.locator('#rigPart').selectOption(part);
    assert.equal((await status(page)).paused,true,'Opening Animation Studio does not pause for editing');
    // Studio deliberately pauses on entry. Invoke the native Resume button
    // while leaving its panel open, so its live-state controls are exercised.
    await page.locator('#animeCinePause').evaluate(button=>button.click());
    await page.waitForFunction(()=>{const s=window.SWYRL_ENGINE_ANIMATION.status();return s.playing&&!s.paused;},
      undefined,{timeout:15000});
    await page.waitForFunction(()=>document.getElementById('rigApplyFit').disabled,undefined,{timeout:15000});
    assert.equal(await page.locator('#rigApplyFit').isDisabled(),true,'Live playback allows a body-fit mutation');
    assert.equal(await page.locator('#rigResetFit').isDisabled(),true,'Live playback allows a body-fit reset');
    assert.equal(await page.evaluate(()=>window.SWYRL_ENGINE_RIG.fitPart('kami','leftForearm',{x:.01})),false,
      'Live playback permits a fit mutation through the public model API');
    await closeStudio(page);await page.locator('#animeCinePause').click();
    await choosePart(page,'kami',part,17.25);
    assert.equal(await page.locator('#rigApplyFit').isDisabled(),false,'Pausing does not enable body-piece fitting');
    const pausedFit={...authoredFit,artX:authoredFit.artX+.015};
    await fitPiece(page,'kami',part,17.25,pausedFit);
    const pausedTime=(await status(page)).elapsed;await frames(page);close((await status(page)).elapsed,pausedTime,'Paused playhead advanced',.001);
    await closeStudio(page);safe(await stage(page),mode.name+' paused fit');
    await page.screenshot({path:resolve(output,'character-alignment-'+mode.name+'-play.png')});
    await page.locator('#animeCineExit').click();await frames(page);
    assert.equal((await status(page)).playing,false,'Stop failed to return to the native editor');
    assert.deepEqual((await model(page,'kami')).layout[part],pausedFit,'Stop discarded a paused body fit');
    assert.deepEqual((await stage(page)).editorCamera,editorCamera,'Play/Stop altered the editor camera');
    independent(await project(page),original,mode.name+' Play/Stop fit');

    // A clean browser cannot rescue Save/Load through an existing rig cache.
    const freshContext=await browser.newContext(options),fresh=await freshContext.newPage(),freshFailures=watch(fresh);
    await start(fresh);await fresh.evaluate(data=>window.SWYRL_ENGINE_STORYBOARD.importProject(data),exported);await frames(fresh);
    assert.deepEqual((await project(fresh)).project.animeRigs,exported.project.animeRigs,'Fresh import changed the saved body-piece fits');
    safe(await seek(fresh,17.25),mode.name+' imported fitted puppet');
    sameJoint(after.joints[part],(await rendered(fresh,'kami')).joints[part],'Fresh import did not reproduce fitted geometry');
    await fresh.screenshot({path:resolve(output,'character-alignment-'+mode.name+'-import.png')});

    // v9.2 saves have the same pose data but no static-fit section. They must
    // acquire the improved default assembly without losing a single key.
    const legacy=structuredClone(original);
    for(const config of Object.values(legacy.project.animeRigs.characters))delete config.layout;
    delete legacy.project.animeSockets;
    delete legacy.project.animeEmergence;
    await fresh.evaluate(data=>window.SWYRL_ENGINE_STORYBOARD.importProject(data),legacy);await frames(fresh);
    independent(await project(fresh),original,mode.name+' older project default fits');
    await seek(fresh,19);
    for(const character of ['kami','swyrlz']){
      const migrated=(await model(fresh,character)).layout;
      assert.deepEqual(Object.keys(migrated),Object.keys(baselineLayouts[character]),'Older save lost default body parts');
      // Native degree fields round-trip through radians. A few billionths of
      // a radian do not change geometry or indicate a failed migration.
      for(const [id,fit] of Object.entries(baselineLayouts[character]))for(const [field,value] of Object.entries(fit))
        close(migrated[id][field],value,'Older save did not receive improved default assembly '+character+'.'+id+'.'+field,1e-6);
      attachments(await rendered(fresh,character),mode.name+' imported older '+character);
    }
    const beforeInvalid=await project(fresh);
    assert.equal(await fresh.evaluate(()=>window.SWYRL_ENGINE_RIG.fitPart('kami','face',{x:1})),false,'A facial expression is incorrectly treated as a body cutout');
    assert.equal(await fresh.evaluate(()=>window.SWYRL_ENGINE_RIG.fitPart('unknown','head',{x:1})),false,'Unknown character acquired a body fit');
    assert.equal(await fresh.evaluate(()=>window.SWYRL_ENGINE_RIG.resetPartFit('kami','unknown')),false,'Unknown body part acquired a fit');
    assert.deepEqual(await project(fresh),beforeInvalid,'Invalid body-fit requests mutated the project');
    const bad=structuredClone(exported),badLayout=bad.project.animeRigs.characters.kami.layout;
    badLayout.leftForearm={x:1e99,y:-1e99,width:1e99,height:-1e99,artX:'NaN',artY:Infinity,rotationZ:1e99};
    badLayout.unknownPart={x:2};
    await fresh.evaluate(data=>window.SWYRL_ENGINE_STORYBOARD.importProject(data),bad);await frames(fresh);
    const bounded=await model(fresh,'kami');
    assert.equal(Object.hasOwn(bounded.layout,'unknownPart'),false,'Unknown imported body part reached the renderer');
    for(const [id,fit] of Object.entries(bounded.layout))for(const [field,value] of Object.entries(fit)){
      const [low,high]=bounded.layoutBounds[field];
      assert.ok(Number.isFinite(value)&&value>=low&&value<=high,'Imported body fit escaped finite bounds: '+id+'.'+field);
    }
    independent(await project(fresh),original,mode.name+' malformed fit import');
    // Return to valid art before checking shared scenery/Watch surfaces.
    await fresh.evaluate(data=>window.SWYRL_ENGINE_STORYBOARD.importProject(data),original);await frames(fresh);await seek(fresh,19);
    const scenery=await fresh.evaluate(()=>window.SWYRL_ENGINE_SCENERY.renderStatus());
    assert.equal(scenery.objects.length,34,'Body fitting flattened or lost layered background objects');
    assert.equal(scenery.starLayers.length,3,'Body fitting flattened the near/middle/far star shells');
    assert.equal(scenery.starLayers.reduce((sum,layer)=>sum+layer.pointCount,0),210,'Body fitting lost layered stars');
    await fresh.evaluate(()=>window.SWYRL_ENGINE_STORYBOARD.exitPreview());await frames(fresh);
    await fresh.locator('#animeScreeningBtn').click();
    await fresh.waitForFunction(()=>window.SWYRL_ENGINE_ANIMATION.status().active,undefined,{timeout:15000});
    await fresh.locator('#animeCinePause').click();await seek(fresh,19);
    for(const character of ['kami','swyrlz'])attachments(await rendered(fresh,character),mode.name+' Watch '+character);
    safe(await stage(fresh),mode.name+' native Watch');
    await fresh.screenshot({path:resolve(output,'character-alignment-'+mode.name+'-watch.png')});
    await fresh.locator('#animeScreeningClose').click();await frames(fresh);
    noFailures(freshFailures,mode.name+' portable fitted character');await freshContext.close();
    noFailures(failures,mode.name+' native fitted character');
    console.log('CHARACTER_ALIGNMENT_'+mode.name.toUpperCase()+'_PASS',JSON.stringify({parts:19,poseKeys:425,sceneryKeys:341,screenshots:output}));
    await context.close();
  }
  allPassed=true;
}finally{await browser.close();}
if(allPassed)console.log(modes.length===2?'CHARACTER_ALIGNMENT_BOTH_VIEWPORTS_PASSED':'CHARACTER_ALIGNMENT_SELECTED_VIEWPORT_PASSED');
