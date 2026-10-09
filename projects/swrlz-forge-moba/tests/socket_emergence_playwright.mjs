import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {mkdir,readFile} from 'node:fs/promises';
import {resolve} from 'node:path';
import {inflateSync} from 'node:zlib';

// Inspect transformed WebGL geometry and measured socket endpoints during real
// native Play. A fade, an attachment label, or a browser cache cannot pass.
const base=(process.env.SWYRL_ANIME_TEST_URL||'http://127.0.0.1:8775').replace(/\/$/,'');
const output=resolve(process.env.SWYRL_ANIME_SCREENSHOTS_DIR||'socket-emergence-acceptance');
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
const frames=page=>page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
const project=page=>page.evaluate(()=>window.SWYRL_ENGINE_ANIMATION.serializedProject());
const stage=page=>page.evaluate(()=>window.SWYRL_ENGINE_STORYBOARD.stageStatus());
const status=page=>page.evaluate(()=>window.SWYRL_ENGINE_ANIMATION.status());
const rig=(page,character)=>page.evaluate(character=>window.SWYRL_ENGINE_RIG.renderStatus(character),character);
const socketModel=(page,character)=>page.evaluate(character=>window.SWYRL_ENGINE_SOCKETS.model(character),character);
const emergence=page=>page.evaluate(()=>window.SWYRL_ENGINE_EMERGENCE.status());
const scenery=page=>page.evaluate(()=>window.SWYRL_ENGINE_SCENERY.renderStatus());
const distance=(a,b)=>Math.hypot(...a.map((value,index)=>value-b[index]));
const close=(actual,expected,label,tolerance=1e-5)=>assert.ok(Number.isFinite(actual)&&Math.abs(actual-expected)<=tolerance,
  label+': expected '+expected+', received '+actual);
const nativeScene=saved=>({background:saved.scene.background,layers:saved.editor.layers,
  actors:saved.scene.actors.map(actor=>({id:actor.id,type:actor.type,position:actor.position,
    rotation:actor.rotation,scale:actor.scale,manualVisible:actor.manualVisible,editorLayerIds:actor.editorLayerIds}))});
const poseCount=saved=>Object.values(saved.project.animeRigs.characters).reduce((sum,character)=>sum+
  character.face.length+Object.values(character.joints).reduce((count,keys)=>count+keys.length,0),0);
const boxSize=box=>box.max.map((value,index)=>value-box.min[index]);
const boxCenter=box=>box.max.map((value,index)=>(value+box.min[index])*.5);
function pngPixels(buffer){
  // Chromium screenshots use 8-bit RGB/RGBA PNG. Decode them directly so the
  // acceptance test can sample the actual WebGL output without dependencies.
  let width=0,height=0,channels=0;const data=[];
  for(let offset=8;offset<buffer.length;){
    const length=buffer.readUInt32BE(offset),type=buffer.toString('ascii',offset+4,offset+8),chunk=buffer.subarray(offset+8,offset+8+length);
    if(type==='IHDR'){width=chunk.readUInt32BE(0);height=chunk.readUInt32BE(4);assert.equal(chunk[8],8,'Unsupported screenshot bit depth');
      assert.ok(chunk[9]===2||chunk[9]===6,'Unsupported screenshot color type');channels=chunk[9]===6?4:3;assert.equal(chunk[12],0,'Interlaced screenshot');}
    if(type==='IDAT')data.push(chunk);offset+=length+12;
  }
  const raw=inflateSync(Buffer.concat(data)),stride=width*channels,pixels=Buffer.alloc(stride*height);
  const paeth=(a,b,c)=>{const p=a+b-c,pa=Math.abs(p-a),pb=Math.abs(p-b),pc=Math.abs(p-c);return pa<=pb&&pa<=pc?a:pb<=pc?b:c;};
  for(let y=0;y<height;y++){
    const filter=raw[y*(stride+1)];
    for(let x=0;x<stride;x++){
      const index=y*stride+x,a=x>=channels?pixels[index-channels]:0,b=y?pixels[index-stride]:0,c=y&&x>=channels?pixels[index-stride-channels]:0;
      const prediction=filter===0?0:filter===1?a:filter===2?b:filter===3?Math.floor((a+b)/2):filter===4?paeth(a,b,c):NaN;
      assert.ok(Number.isFinite(prediction),'Unknown screenshot PNG filter');pixels[index]=(raw[y*(stride+1)+x+1]+prediction)&255;
    }
  }
  return {width,height,rgb:(x,y)=>Array.from(pixels.subarray((y*width+x)*channels,(y*width+x)*channels+3))};
}
function finiteBox(box,label){
  assert.ok(box&&box.min?.length===3&&box.max?.length===3&&box.min.every(Number.isFinite)&&box.max.every(Number.isFinite),
    'Missing actual world geometry bounds: '+label);
  assert.ok(boxSize(box).every(value=>value>=0),'Inverted geometry bounds: '+label);
}
function watch(page){
  const errors=[];page.on('pageerror',error=>errors.push(String(error)));
  page.on('response',response=>{if(response.status()>=400&&response.url().startsWith(base)&&/\.(?:png|webp|jpe?g)(?:\?|$)/i.test(response.url()))
    errors.push('Artwork '+response.status()+' '+response.url());});
  page.on('requestfailed',request=>{if(request.url().startsWith(base)&&/\.(?:png|webp|jpe?g)(?:\?|$)/i.test(request.url()))
    errors.push('Artwork '+request.failure()?.errorText+' '+request.url());});
  return errors;
}
async function start(page){
  // Each isolated context opens a new headless window. Explicitly focus it;
  // a background window can suspend RAF even after its APIs have initialized.
  await page.bringToFront();
  await page.goto(base+'/index.html?project=anime-ghosts-ep01',{waitUntil:'domcontentloaded',timeout:60000});
  await page.waitForFunction(()=>window.SWYRL_ENGINE_SOCKETS?.renderStatus&&window.SWYRL_ENGINE_EMERGENCE?.status&&
    window.SWYRL_ENGINE_RIG&&window.SWYRL_ENGINE_SCENERY&&window.SWYRL_ENGINE_ANIMATION&&window.SWYRL_ENGINE_STORYBOARD,
    undefined,{timeout:60000,polling:100});
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
async function seek(page,time){
  assert.equal(await page.evaluate(time=>window.SWYRL_ENGINE_ANIMATION.seek(time),time),true,'Native seek failed at '+time+'s');
  await frames(page);return stage(page);
}
async function openStudio(page){
  if(!await page.locator('#storyStudioPanel').isVisible())await page.locator('#storyStudioBtn').click();
}
async function closeStudio(page){
  if(await page.locator('#storyStudioPanel').isVisible())await page.locator('#storyClose').click();
}
async function historyAction(page,action){
  await closeStudio(page);
  if(!(await status(page)).playing){await page.evaluate(()=>window.SWYRL_ENGINE_STORYBOARD.exitPreview());await frames(page);}
  const quick=page.locator(action==='undo'?'#quickUndoBtn':'#quickRedoBtn');
  if(await quick.isVisible()){await quick.click();return;}
  if(!await page.locator('#mobileToolsPanel').isVisible())await page.locator('#mobileToolsBtn').click();
  await page.locator('#mobileToolsPanel [data-click="'+action+'Btn"]').click();
}
async function chooseSocket(page,character,part,name,time){
  await openStudio(page);await page.locator('#storyTrack').selectOption(character);
  await input(page,'#storyTime',time);await page.locator('#socketPart').selectOption(part);
  await page.locator('#socketName').selectOption(name);await frames(page);
}
async function socketPose(page,character,part,name,time,point){
  await chooseSocket(page,character,part,name,time);
  for(const field of ['x','y','z'])await input(page,'#socket'+field.toUpperCase(),point[field]);
  await page.locator('#socketApply').click();await seek(page,time);
  const model=await socketModel(page,character),saved=name==='attach'?model.parts[part].attach:model.parts[part].sockets[name];
  for(const field of ['x','y','z'])close(saved[field],point[field],'Native socket coordinate did not save '+field,.000002);
  return saved;
}
async function poseKey(page,character,part,time,key){
  await openStudio(page);await page.locator('#storyTrack').selectOption(character);
  await input(page,'#storyTime',time);await page.locator('#rigPart').selectOption(part);
  for(const field of ['rotationX','rotationY','rotationZ','depth'])
    await input(page,'#rig'+field[0].toUpperCase()+field.slice(1),field==='depth'?key[field]:key[field]*180/Math.PI);
  await page.locator('#rigAddKey').click();await seek(page,time);
  const saved=await page.evaluate(({character,part,time})=>window.SWYRL_ENGINE_RIG.sample(character,part,time),{character,part,time});
  for(const field of ['rotationX','rotationY','rotationZ','depth'])close(saved[field],key[field],'Native socket rotation key did not save '+field,.000002);
  return saved;
}
function safe(state,label,readable=false){
  assert.equal(state.occlusionSafe,true,'Paper scenery or props obstruct the cast/camera: '+label);
  assert.deepEqual(state.assetErrors||[],[],'Artwork failed: '+label);
  assert.ok(state.safeCameraGap>6,'An expanding cutout passes through the camera: '+label);
  for(const plate of state.scenery)assert.ok(plate.frontZ<=plate.z+.001,
    'Folding scenery crosses its parent hinge plane: '+label+' '+plate.id);
  if(readable)for(const id of ['kami','swyrlz']){
    const actor=state.castBounds.find(actor=>actor.id===id);
    assert.ok(actor&&actor.visible&&actor.width>.035&&actor.height>.08,'Expanded character is unreadable: '+label+' '+id);
    assert.ok(actor.right>0&&actor.left<1&&actor.bottom>0&&actor.top<1,'Expanded character leaves the camera: '+label+' '+id);
  }
}
function connected(render,label,detached=[]){
  assert.equal(render.rigged,true,'Articulated puppet disappeared: '+label);
  assert.ok(render.partCount>=18&&render.meshCount>=render.partCount*3,'Missing thick painted body pieces: '+label);
  assert.ok(render.connections?.length>=18,'Not every limb/prop has an attachment socket: '+label);
  assert.equal(new Set(render.connections.map(connection=>connection.child)).size,render.connections.length,
    'Multiple parent connections share a child: '+label);
  for(const connection of render.connections){
    assert.equal(connection.connected,!detached.includes(connection.child),'Unexpected attachment state: '+label+' '+connection.child);
    assert.ok(connection.childAttachWorld?.length===3&&connection.parentSocketWorld?.length===3&&
      connection.childAttachWorld.every(Number.isFinite)&&connection.parentSocketWorld.every(Number.isFinite),
      'Connection lacks actual transformed 3D endpoints: '+label+' '+connection.child);
    const error=distance(connection.childAttachWorld,connection.parentSocketWorld);
    close(connection.error,error,'Reported socket error ignores its endpoints: '+label+' '+connection.child,1e-7);
    if(connection.connected)assert.ok(error<1e-5,'A limb/prop pulls away from its parent under rotation: '+label+' '+connection.child+' gap '+error);
  }
}
function expandedGeometry(view,label){
  assert.equal(view.enabled,true,'Book emergence is disabled: '+label);
  assert.ok(view.origin?.length===3&&view.origin.every(Number.isFinite),'No measured book-page origin: '+label);
  finiteBox(view.pageBounds,label+' actual pages');
  assert.ok(view.layers?.length>=8,'Opening omits a scene layer: '+label);
  assert.equal(view.objects?.length,34,'Opening omits independently layered scenery objects: '+label);
  for(const item of [...view.layers,...view.objects]){
    finiteBox(item.bounds,label+' '+item.id);
    assert.ok(Number.isFinite(item.progress)&&item.progress>=0&&item.progress<=1,'Invalid expansion progress: '+label+' '+item.id);
  }
}
function faceFront(render,label){
  const face=render.face;
  assert.ok(face.pixelCount>100&&face.featureSurfaceSampleCount>30,'No measured high-alpha animated facial ink: '+label);
  assert.ok(face.surfaceSamples?.length>20,'Facial visibility reports a nominal anchor instead of actual painted feature surfaces: '+label);
  assert.ok(face.minFeatureClearance>.008,'The deformed head covers animated eyes/mouth: '+label+' clearance '+face.minFeatureClearance);
  for(const sample of face.surfaceSamples){
    assert.ok(sample.alpha>=80/255&&sample.faceWorld?.every(Number.isFinite)&&sample.headWorld?.every(Number.isFinite),
      'Facial ink lacks actual front/head triangle samples: '+label);
    assert.ok(sample.clearance>.008,'An actual animated facial feature is behind its head card: '+label);
    assert.ok(distance(sample.faceWorld,sample.headWorld)>0,'Face/head geometry occupies the same surface: '+label);
  }
}
function staffAttached(render,label){
  const grip=render.staffGrip;
  assert.ok(grip&&grip.visible,'Kami is missing the hand that holds the staff: '+label);
  assert.ok(grip.handSampleCount>=12&&grip.handFrontSamples.length>=6,'No actual painted hand ink around the staff grip: '+label);
  for(const sample of grip.handFrontSamples){
    assert.ok(sample.alpha>.9&&sample.world.every(Number.isFinite)&&sample.screen.every(Number.isFinite),
      'Staff hand diagnostic does not sample actual painted alpha: '+label);
    assert.ok(sample.screen[0]>0&&sample.screen[0]<1&&sample.screen[1]>0&&sample.screen[1]<1,
      'The staff hand is outside the visible camera: '+label);
  }
  close(grip.gripError,distance(grip.gripWorld,grip.shaftGripWorld),'Staff grip error ignores actual transformed geometry: '+label,1e-7);
  assert.ok(grip.gripError<1e-5,'Staff floats away from the hand socket: '+label);
  assert.ok(grip.fingerFrontClearance>.005,'The staff shaft hides the hand/fingers: '+label+' clearance '+grip.fingerFrontClearance);
  close(grip.shaftLength,distance(grip.shaftBaseWorld,grip.shaftTopWorld),'Staff shaft measurement is not actual geometry: '+label,1e-6);
  assert.ok(grip.shaftLength>.3&&grip.shaftRadius>0,'Missing actual wooden staff shaft: '+label);
  finiteBox(grip.headBounds,label+' staff ornament');finiteBox(grip.ferruleBounds,label+' head ferrule');
  close(grip.headStemToShaftTop,distance(grip.headStemWorld,grip.shaftTopWorld),'Staff head connection ignores actual geometry: '+label,1e-7);
  assert.ok(grip.headStemToShaftTop<grip.shaftRadius*3.5,'Staff head and shaft leave a visible gap: '+label);
  assert.ok(grip.headStemAlpha>.9&&grip.headStemPixel?.length===2&&grip.headStemRGB?.length===3,
    'The staff mounts into transparent margin instead of painted stem ink: '+label);
  close(grip.shaftMountError,distance(grip.headStemAnchorWorld,grip.shaftMountWorld),
    'Staff shaft mount error ignores the actual outgoing socket: '+label,1e-7);
  assert.ok(grip.shaftMountError<1e-5&&grip.headStemAxisError<1e-5,
    'The long pole misses the painted head stem: '+label);
  assert.ok(grip.headStemAxialOverlap>0,'The pole stops short of its inserted head stem: '+label);
  assert.ok(grip.ferruleFrontClearance>.001&&grip.shaftFrontClearance>.001&&grip.ferruleFrontWorldClearance>0,
    'The ferrule or pole covers the painted joining stem: '+label);
}
function handWrapsRight(render,label){
  const grip=render.staffGrip;
  assert.ok(grip.wristScreen.every(Number.isFinite)&&grip.gripScreen.every(Number.isFinite),
    'The hand orientation has no actual projected wrist and grip: '+label);
  assert.ok(grip.wristScreen[0]<grip.gripScreen[0]&&grip.gripFacingRight===true,
    'The holding hand does not enter from the viewer’s left and wrap right around the staff: '+label);
  close(grip.gripDirectionScreen[0],grip.gripScreen[0]-grip.wristScreen[0],
    'The hand direction ignores the actual projected sockets: '+label,1e-7);
}
async function paintedHandOnScreen(page,render,label){
  // Sample projected high-alpha glove pixels in the genuine rendered canvas.
  // This catches a correctly labelled hand that is still hidden by the torso.
  const canvas=page.locator('canvas:visible').first(),image=pngPixels(await canvas.screenshot());
  let matches=0;
  for(const sample of render.staffGrip.handFrontSamples){
    const cx=Math.round(sample.screen[0]*image.width),cy=Math.round(sample.screen[1]*image.height);let error=Infinity;
    // The rotated fingertips may cover less than one native render pixel.
    // Include their two-pixel interpolation footprint without relaxing the
    // required painted colors or replacing this genuine GPU image check.
    for(let y=Math.max(0,cy-2);y<=Math.min(image.height-1,cy+2);y++)for(let x=Math.max(0,cx-2);x<=Math.min(image.width-1,cx+2);x++)
      error=Math.min(error,distance(image.rgb(x,y),sample.rgb)/Math.sqrt(3));
    if(error<43)matches++;
  }
  assert.ok(matches>=3,'The actual WebGL image does not show the painted staff hand: '+label+' matched samples '+matches);
}
async function paintedStemOnScreen(page,render,label){
  const grip=render.staffGrip,image=pngPixels(await page.locator('canvas:visible').first().screenshot());
  const cx=Math.round(grip.headStemScreen[0]*image.width),cy=Math.round(grip.headStemScreen[1]*image.height);
  assert.ok(cx>=0&&cy>=0&&cx<image.width&&cy<image.height,'The painted joining stem leaves the camera: '+label);
  let error=Infinity;
  for(let y=Math.max(0,cy-2);y<=Math.min(image.height-1,cy+2);y++)for(let x=Math.max(0,cx-2);x<=Math.min(image.width-1,cx+2);x++)
    error=Math.min(error,distance(image.rgb(x,y),grip.headStemRGB)/Math.sqrt(3));
  assert.ok(error<43,'The actual WebGL image does not show the painted staff joining stem: '+label+' RGB error '+error);
}
function originalContent(saved,original,label){
  assert.deepEqual(saved.project.animeTimeline,original.project.animeTimeline,'Socket edit overwrites story/camera keys: '+label);
  assert.deepEqual(saved.project.animeScenery,original.project.animeScenery,'Socket edit overwrites scenery keys: '+label);
  assert.deepEqual(nativeScene(saved),nativeScene(original),'Preview/socket edit mutates native actors or layers: '+label);
}

let allPassed=false;
try{
  for(const mode of modes){
    const options={viewport:mode.viewport,isMobile:mode.isMobile,hasTouch:mode.hasTouch,acceptDownloads:true};
    const context=await browser.newContext(options),page=await context.newPage(),errors=watch(page);
    await start(page);
    const original=await project(page),editorCamera=(await stage(page)).editorCamera;
    assert.equal(original.project.animeSockets?.schema,'anime-rig-sockets-v1','Starter has no portable socket assembly');
    assert.equal(original.project.animeEmergence?.schema,'anime-book-emergence-v1','Starter has no portable book emergence');
    assert.equal(original.scene.actors.length,70,'Opening replaced native editor actors');
    assert.equal(original.editor.layers.length,11,'Opening replaced the original editor layers');
    assert.equal(Object.keys(original.project.animeTimeline.tracks).length,9,'Opening lost independent story/camera tracks');
    assert.equal(original.project.animeTimeline.duration,134,'Opening changed episode duration');
    assert.equal(poseCount(original),425,'Opening replaced the authored character poses/faces');
    assert.equal(Object.values(original.project.animeScenery.objects).reduce((sum,item)=>sum+item.keys.length,0),341,
      'Opening replaced independent scenery keyframes');

    // Pause actual native Play, then inspect shared-clock intermediate frames.
    await page.locator('#playBtn').click();
    await page.waitForFunction(()=>window.SWYRL_ENGINE_ANIMATION.status().active,undefined,{timeout:15000});
    await page.locator('#animeCinePause').click();
    const opening=[];
    for(const time of [0,.25,1,2,4,6,8,10,12,14,19,72,110]){
      safe(await seek(page,time),mode.name+' native Play '+time+'s',time>=14);
      const view=await emergence(page);expandedGeometry(view,mode.name+' '+time+'s');
      if(time<=14)opening.push({time,view});
      for(const character of ['kami','swyrlz'])connected(await rig(page,character),mode.name+' '+character+' '+time+'s');
      if([14,19,72,110].includes(time))staffAttached(await rig(page,'kami'),mode.name+' authored staff '+time+'s');
      if([19,72,110].includes(time)){
        const held=await rig(page,'kami');handWrapsRight(held,mode.name+' authored staff '+time+'s');
        await paintedHandOnScreen(page,held,mode.name+' authored staff '+time+'s');
        await paintedStemOnScreen(page,held,mode.name+' authored staff '+time+'s');
      }
      if([0,4,8,14,19].includes(time))await page.screenshot({path:resolve(output,'socket-emergence-'+mode.name+'-opening-'+time+'.png')});
    }
    const collapsed=opening[0].view,complete=opening.at(-1).view;
    const closedPages=boxSize(collapsed.pageBounds),openPages=boxSize(complete.pageBounds);
    assert.ok(closedPages[0]<openPages[0]*.65&&closedPages[0]>openPages[0]*.35,
      'The physical book pages do not begin closed together and unfold into a spread: '+mode.name);
    assert.ok(opening.some(frame=>boxSize(frame.view.pageBounds)[1]>closedPages[1]+1),
      'Book covers/pages only change a caption instead of rotating through the opening: '+mode.name);
    for(const first of [...collapsed.layers,...collapsed.objects].filter(item=>item.id!=='book')){
      const last=[...complete.layers,...complete.objects].find(item=>item.id===first.id);
      assert.ok(last,'An opening object disappears from the assembled scene: '+first.id);
      close(first.progress,0,'Geometry begins already expanded: '+mode.name+' '+first.id);
      close(last.progress,1,'Geometry never fully expands from the book: '+mode.name+' '+first.id);
      assert.ok(Math.max(...boxSize(first.bounds))<Math.max(...boxSize(last.bounds))*.065,
        'Opening only changes opacity instead of expanding actual geometry: '+mode.name+' '+first.id);
      const center=boxCenter(first.bounds);
      assert.ok(Math.abs(center[0]-collapsed.origin[0])<1&&Math.abs(center[1]-collapsed.origin[1])<1,
        'Collapsed scenery/character begins away from the actual book page: '+mode.name+' '+first.id);
    }
    for(const id of ['background','midground','kami','swyrlz','foreground']){
      const steps=opening.map(frame=>frame.view.layers.find(layer=>layer.id===id).progress);
      assert.ok(steps.some(value=>value>.02&&value<.98),'Layer teleports directly from closed to open: '+mode.name+' '+id);
      for(let index=1;index<steps.length;index++)assert.ok(steps[index]+1e-6>=steps[index-1],
        'A layer contracts during the opening: '+mode.name+' '+id);
    }
    const stars=(await scenery(page)).starLayers;
    assert.equal(stars.length,3,'Book emergence flattens the star shells');
    assert.equal(stars.reduce((sum,item)=>sum+item.pointCount,0),210,'Book emergence loses the real layered stars');
    await page.locator('#animeCineExit').click();await frames(page);
    originalContent(await project(page),original,mode.name+' Play/Stop');

    // Author a staggered entrance using the actual opening panel. The saved
    // timing must change the transformed puppet, and one Undo restores it.
    await openStudio(page);await input(page,'#storyTime',4);
    await page.locator('#emergenceLayer').selectOption('kami');
    await input(page,'#emergenceDelay',3.25);await input(page,'#emergenceLayerDuration',6.5);
    await page.locator('#emergenceApply').click();await seek(page,4);
    const configured=(await project(page)).project.animeEmergence,configuredOpening=await emergence(page);
    close(configured.layers.kami.delay,3.25,'Native opening delay did not save');
    close(configured.layers.kami.duration,6.5,'Native opening duration did not save');
    const originalFour=opening.find(frame=>frame.time===4).view.layers.find(layer=>layer.id==='kami');
    const configuredFour=configuredOpening.layers.find(layer=>layer.id==='kami');
    assert.ok(Math.abs(configuredFour.progress-originalFour.progress)>.001,'Opening timing only changes a label');
    assert.ok(distance(boxSize(configuredFour.bounds),boxSize(originalFour.bounds))>.001,
      'Opening timing does not change the actual emerging character geometry');
    for(const id of Object.keys(configured.layers))if(id!=='kami')assert.deepEqual(configured.layers[id],original.project.animeEmergence.layers[id],
      'Changing one entrance time changes the independent '+id+' entrance');
    await historyAction(page,'undo');await seek(page,4);
    assert.deepEqual((await project(page)).project.animeEmergence,original.project.animeEmergence,
      'One Undo does not restore the opening timing');
    close(distance(boxSize((await emergence(page)).layers.find(layer=>layer.id==='kami').bounds),boxSize(originalFour.bounds)),0,
      'Opening Undo does not restore the actual puppet expansion',.002);
    await historyAction(page,'redo');await seek(page,4);
    assert.deepEqual((await project(page)).project.animeEmergence,configured,'Redo loses the opening timing');

    // Move an actual parent's outgoing elbow socket through the native editor.
    // Its connected forearm, hand and prop follow; the parent and sibling stay.
    await seek(page,17.25);
    const originalSockets=await socketModel(page,'kami'),before=await rig(page,'kami'),companionBefore=await rig(page,'swyrlz');
    assert.equal(Object.keys(originalSockets.parts).length,19,'Every body piece requires an incoming and outgoing socket frame');
    for(const [id,part] of Object.entries(originalSockets.parts)){
      assert.ok(part.attach&&Object.keys(part.sockets).length,'Missing attach/child socket: '+id);
      for(const point of [part.attach,...Object.values(part.sockets)])assert.ok(['x','y','z'].every(axis=>Number.isFinite(point[axis])),
        'Socket has non-finite local coordinates: '+id);
    }
    assert.notEqual(await page.evaluate(()=>{const copy=window.SWYRL_ENGINE_SOCKETS.model('kami');
      copy.parts.leftUpperArm.sockets.elbow.x=999;return window.SWYRL_ENGINE_SOCKETS.model('kami').parts.leftUpperArm.sockets.elbow.x;}),999,
      'The public socket model permits mutation without native history');
    const elbow=originalSockets.parts.leftUpperArm.sockets.elbow,authoredPoint={x:elbow.x+.075,y:elbow.y-.025,z:elbow.z+.018};
    await socketPose(page,'kami','leftUpperArm','elbow',17.25,authoredPoint);
    const after=await rig(page,'kami'),authoredSockets=await socketModel(page,'kami');connected(after,mode.name+' authored elbow');
    assert.ok(distance(before.joints.leftForearm.worldPosition,after.joints.leftForearm.worldPosition)>.025,
      'Socket editor changes metadata without moving the attached forearm');
    assert.ok(distance(before.joints.leftHand.worldPosition,after.joints.leftHand.worldPosition)>.025,
      'The forearm moves without its hand');
    assert.ok(distance(before.joints.staff.worldPosition,after.joints.staff.worldPosition)>.025,
      'The attached hand moves without its staff');
    close(distance(before.joints.leftUpperArm.worldPosition,after.joints.leftUpperArm.worldPosition),0,
      'Editing the elbow moves its parent pivot');
    close(distance(before.joints.rightHand.worldPosition,after.joints.rightHand.worldPosition),0,
      'Editing the left socket moves the independent right arm');
    close(distance(companionBefore.joints.head.worldPosition,(await rig(page,'swyrlz')).joints.head.worldPosition),0,
      'Editing Kami changes the companion');
    originalContent(await project(page),original,mode.name+' socket authoring');
    assert.deepEqual((await project(page)).project.animeRigs,original.project.animeRigs,'Socket placement overwrites body fits or pose keys');
    await historyAction(page,'undo');await seek(page,17.25);
    assert.deepEqual(await socketModel(page,'kami'),originalSockets,'One Undo does not restore the original socket graph');
    close(distance(before.joints.leftForearm.worldPosition,(await rig(page,'kami')).joints.leftForearm.worldPosition),0,
      'Undo restores the socket label without restoring the actual forearm');
    await historyAction(page,'redo');await seek(page,17.25);
    assert.deepEqual(await socketModel(page,'kami'),authoredSockets,'Redo loses the socket graph');
    close(distance(after.joints.leftHand.worldPosition,(await rig(page,'kami')).joints.leftHand.worldPosition),0,
      'Redo loses the actual connected hand');
    // Detach a forearm, position it independently, then snap the real cutout
    // back to the parent's outgoing elbow. A permanently-connected no-op
    // cannot satisfy this sequence or reproduce it through native history.
    await chooseSocket(page,'kami','leftForearm','attach',17.25);await page.locator('#socketDetach').click();await seek(page,17.25);
    assert.equal((await socketModel(page,'kami')).connections.leftForearm.connected,false,'Detach leaves the limb connected');
    const detachedBefore=await rig(page,'kami'),parentSocketBefore=detachedBefore.connections.find(connection=>connection.child==='leftForearm').parentSocketWorld;
    await page.locator('#rigPart').selectOption('leftForearm');
    const detachedFit=await page.evaluate(()=>window.SWYRL_ENGINE_RIG.model('kami').layout.leftForearm);
    await input(page,'#rigFitX',detachedFit.x+.28);await input(page,'#rigFitY',detachedFit.y-.12);
    await page.locator('#rigApplyFit').click();await seek(page,17.25);
    const detachedRender=await rig(page,'kami'),loose=detachedRender.connections.find(connection=>connection.child==='leftForearm');
    assert.equal(loose.connected,false,'Fitting a detached limb silently reattaches it');
    assert.ok(distance(loose.childAttachWorld,loose.parentSocketWorld)>.08,'A detached limb cannot move away from the parent socket');
    assert.ok(distance(detachedBefore.joints.leftForearm.worldPosition,detachedRender.joints.leftForearm.worldPosition)>.1,
      'Fitting a detached piece only changes metadata');
    close(distance(parentSocketBefore,loose.parentSocketWorld),0,'Moving a detached limb moves its parent socket');
    close(distance(detachedBefore.joints.leftUpperArm.worldPosition,detachedRender.joints.leftUpperArm.worldPosition),0,
      'Moving a detached limb moves its parent');
    const detachedDownloadPending=page.waitForEvent('download',{timeout:15000});await page.locator('#storySaveProject').click();
    const detachedDownload=await detachedDownloadPending,detachedExport=JSON.parse(await readFile(await detachedDownload.path(),'utf8'));
    assert.equal(detachedExport.project.animeSockets.characters.kami.connections.leftForearm.connected,false,
      'Native Save discards an intentionally detached limb');
    await chooseSocket(page,'kami','leftForearm','attach',17.25);await page.locator('#socketSnap').click();await seek(page,17.25);
    const snapped=await rig(page,'kami');connected(snapped,mode.name+' native Snap to Parent');
    assert.ok(distance(detachedRender.joints.leftForearm.worldPosition,snapped.joints.leftForearm.worldPosition)>.08,
      'Snap does not move the detached cutout to the parent socket');
    close(distance(parentSocketBefore,snapped.connections.find(connection=>connection.child==='leftForearm').parentSocketWorld),0,
      'Snapping a child moves its parent socket');
    await historyAction(page,'undo');await seek(page,17.25);
    assert.equal((await socketModel(page,'kami')).connections.leftForearm.connected,false,'Undo Snap fails to restore intentional detachment');
    close(distance(detachedRender.joints.leftForearm.worldPosition,(await rig(page,'kami')).joints.leftForearm.worldPosition),0,
      'Undo Snap loses the actual detached placement');
    await historyAction(page,'redo');await seek(page,17.25);connected(await rig(page,'kami'),mode.name+' native Snap Redo');
    const snapshot=await socketModel(page,'kami');
    for(const request of [
      ['kami','torso','leftHand','grip'],['kami','leftUpperArm','leftHand','grip'],
      ['kami','leftForearm','rightUpperArm','elbow'],['kami','not-a-part','torso','neck']])
      assert.equal(await page.evaluate(args=>window.SWYRL_ENGINE_SOCKETS.connect(...args),request),false,
        'Socket API accepts a cycle, wrong limb parent or unknown piece');
    assert.equal(await page.evaluate(()=>window.SWYRL_ENGINE_SOCKETS.setSocket('kami','leftUpperArm','unknown',{x:1})),false,
      'Socket API accepts an unknown outgoing anchor');
    assert.equal(await page.evaluate(()=>window.SWYRL_ENGINE_SOCKETS.setSocket('kami','leftUpperArm','elbow',{x:Infinity})),false,
      'Socket API accepts a non-finite anchor');
    assert.deepEqual(await socketModel(page,'kami'),snapshot,'A rejected socket edit mutates the native assembly');

    // The painted staff head owns its pole mount. Editing that outgoing socket
    // changes actual cylinder geometry, and resizing follows the same painted
    // UV point in one native history action rather than adding another Undo.
    const mountBefore=await socketModel(page,'kami'),mountedBefore=await rig(page,'kami');
    const originalMount=mountBefore.parts.staff.sockets.shaft,authoredMount={...originalMount,z:originalMount.z-.012};
    await socketPose(page,'kami','staff','shaft',17.25,authoredMount);
    const mountedAfter=await rig(page,'kami');staffAttached(mountedAfter,mode.name+' edited staff shaft mount');
    assert.ok(distance(mountedBefore.staffGrip.shaftMountWorld,mountedAfter.staffGrip.shaftMountWorld)>.003,
      'Editing the outgoing shaft socket leaves the actual pole mount unchanged');
    close(distance(mountedBefore.joints.staff.worldPosition,mountedAfter.joints.staff.worldPosition),0,
      'Editing an outgoing staff mount moves the staff’s incoming hand pivot');
    await historyAction(page,'undo');await seek(page,17.25);
    assert.deepEqual(await socketModel(page,'kami'),mountBefore,'One Undo loses the original staff mount');
    close(distance(mountedBefore.staffGrip.shaftMountWorld,(await rig(page,'kami')).staffGrip.shaftMountWorld),0,
      'Undo restores a staff socket label without restoring actual pole geometry');
    await historyAction(page,'redo');await seek(page,17.25);
    assert.deepEqual((await socketModel(page,'kami')).parts.staff.sockets.shaft,authoredMount,'Redo loses the editable painted staff mount');
    await openStudio(page);await page.locator('#storyTrack').selectOption('kami');await page.locator('#rigPart').selectOption('staff');
    const fitBefore=await page.evaluate(()=>window.SWYRL_ENGINE_RIG.model('kami').layout.staff),socketsBeforeResize=await socketModel(page,'kami');
    const resized={width:fitBefore.width*1.045,height:fitBefore.height*1.035};
    await input(page,'#rigFitWidth',resized.width);await input(page,'#rigFitHeight',resized.height);
    await page.locator('#rigApplyFit').click();await seek(page,17.25);
    const resizedFit=await page.evaluate(()=>window.SWYRL_ENGINE_RIG.model('kami').layout.staff),resizedSockets=await socketModel(page,'kami');
    close(resizedFit.width,resized.width,'Native staff width was not saved',.000002);
    close(resizedFit.height,resized.height,'Native staff height was not saved',.000002);
    close(resizedSockets.parts.staff.sockets.shaft.x,authoredMount.x*resized.width/fitBefore.width,
      'Resizing the head loses its painted shaft mount X',.000002);
    close(resizedSockets.parts.staff.sockets.shaft.y,authoredMount.y*resized.height/fitBefore.height,
      'Resizing the head loses its painted shaft mount Y',.000002);
    const resizedRender=await rig(page,'kami');staffAttached(resizedRender,mode.name+' resized staff head');
    assert.ok(distance(mountedAfter.staffGrip.shaftMountWorld,resizedRender.staffGrip.shaftMountWorld)>.005,
      'Resizing the staff head leaves the pole attached to its obsolete size');
    await historyAction(page,'undo');await seek(page,17.25);
    assert.deepEqual(await page.evaluate(()=>window.SWYRL_ENGINE_RIG.model('kami').layout.staff),fitBefore,
      'One Undo does not restore the staff’s fitted size');
    assert.deepEqual(await socketModel(page,'kami'),socketsBeforeResize,'Resizing requires a second Undo to restore the mount');
    close(distance(mountedAfter.staffGrip.shaftMountWorld,(await rig(page,'kami')).staffGrip.shaftMountWorld),0,
      'Resizing Undo does not restore the actual mounted pole');
    await historyAction(page,'redo');await seek(page,17.25);
    assert.deepEqual(await socketModel(page,'kami'),resizedSockets,'Redo loses the head’s scaled painted mount');
    staffAttached(await rig(page,'kami'),mode.name+' resized staff Redo');

    // Exercise all three pose axes and authored paper depth. Geometry can move
    // between paper layers, while every incoming anchor stays at its parent.
    for(const [part,key] of [
      ['leftUpperArm',{rotationX:.23,rotationY:-.28,rotationZ:.34,depth:.31}],
      ['leftForearm',{rotationX:-.18,rotationY:.21,rotationZ:-.38,depth:.24}],
      ['leftHand',{rotationX:.16,rotationY:-.17,rotationZ:.2,depth:.22}],
      ['staff',{rotationX:.12,rotationY:.15,rotationZ:-.13,depth:.18}]
    ]){
      await poseKey(page,'kami',part,17.25,key);
      const posed=await rig(page,'kami');connected(posed,mode.name+' XYZ/depth '+part);
      for(const [axis,field] of ['rotationX','rotationY','rotationZ'].entries())close(posed.joints[part].rotation[axis],key[field],
        'Pose key does not rotate the actual socket joint: '+part+' '+field,.002);
    }
    // Maximum supported relief must keep actual facial ink in front of the
    // exact deformed head triangles, including their interior interpolation.
    for(const character of ['kami','swyrlz']){
      await openStudio(page);await page.locator('#storyTrack').selectOption(character);
      await input(page,'#rigDepthAmount',1.5);await page.locator('#rigApplyConfig').click();
      await poseKey(page,character,'head',17.25,{rotationX:.32,rotationY:-.31,rotationZ:.18,depth:.65});
      const head=await rig(page,character);connected(head,mode.name+' maximum '+character+' head relief');
      faceFront(head,mode.name+' maximum '+character+' head relief');
      close(head.joints.head.artDepth,.975,'Maximum head relief does not deform the actual paper surface',.002);
    }
    const posedRig=await rig(page,'kami');
    assert.ok(distance(after.joints.leftHand.worldPosition,posedRig.joints.leftHand.worldPosition)>.03,
      'The hand fails to follow actual ancestor socket rotations');
    await closeStudio(page);await page.evaluate(()=>window.SWYRL_ENGINE_STORYBOARD.exitPreview());await frames(page);
    await page.locator('#playBtn').click();
    await page.waitForFunction(()=>window.SWYRL_ENGINE_ANIMATION.status().active,undefined,{timeout:15000});
    await openStudio(page);await page.locator('#storyTrack').selectOption('kami');
    await page.locator('#animeCinePause').evaluate(button=>button.click());
    await page.waitForFunction(()=>{const state=window.SWYRL_ENGINE_ANIMATION.status();return state.playing&&!state.paused;},undefined,{timeout:15000});
    await page.waitForFunction(()=>document.getElementById('socketApply').disabled&&document.getElementById('emergenceApply').disabled,
      undefined,{timeout:15000});
    assert.equal(await page.evaluate(()=>window.SWYRL_ENGINE_SOCKETS.setSocket('kami','leftUpperArm','elbow',{x:.01})),false,
      'Live playback permits socket mutation');
    assert.equal(await page.evaluate(()=>window.SWYRL_ENGINE_EMERGENCE.configure({duration:14})),false,
      'Live playback permits opening-timing mutation');
    await closeStudio(page);await page.locator('#animeCinePause').click();
    await chooseSocket(page,'kami','leftUpperArm','elbow',17.25);
    assert.equal(await page.locator('#socketApply').isDisabled(),false,'Paused playback does not enable socket fitting');
    assert.equal(await page.locator('#emergenceApply').isDisabled(),false,'Paused playback does not enable opening edits');
    await page.screenshot({path:resolve(output,'socket-emergence-'+mode.name+'-sockets-editor.png')});
    const downloadPending=page.waitForEvent('download',{timeout:15000});await page.locator('#storySaveProject').click();
    const download=await downloadPending,exported=JSON.parse(await readFile(await download.path(),'utf8'));
    assert.deepEqual(exported.project.animeSockets,(await project(page)).project.animeSockets,'Native Save Project loses the socket graph');
    assert.deepEqual(exported.project.animeEmergence,(await project(page)).project.animeEmergence,'Native Save Project loses physical book emergence');
    originalContent(exported,original,mode.name+' saved socket project');
    await closeStudio(page);await page.locator('#animeCineExit').click();await frames(page);
    assert.equal((await status(page)).playing,false,'Stop does not restore the native editor after paused socket editing');
    assert.deepEqual((await stage(page)).editorCamera,editorCamera,'Socketed Play/Stop changes the editor camera');

    // Watch mounts the same actual articulated WebGL stage on desktop/phone.
    await page.locator('#animeScreeningBtn').click();
    await page.waitForFunction(()=>window.SWYRL_ENGINE_ANIMATION.status().active,undefined,{timeout:15000});
    assert.equal(await page.locator('#animeScreeningNative').isVisible(),true,'Watch does not use the actual native paper theatre');
    assert.equal(await page.locator('#storyCinemaStage canvas').count(),1,'Watch has no actual WebGL canvas');
    await page.locator('#animeCinePause').click();
    for(const time of [0,4,8,14,17.25,19,72,110]){
      safe(await seek(page,time),mode.name+' Watch '+time+'s',time>=14);
      expandedGeometry(await emergence(page),mode.name+' Watch '+time+'s');
      for(const character of ['kami','swyrlz'])connected(await rig(page,character),mode.name+' Watch '+character+' '+time+'s');
      if(time>=14)staffAttached(await rig(page,'kami'),mode.name+' Watch staff '+time+'s');
      if([19,72,110].includes(time)){
        const held=await rig(page,'kami');
        await paintedHandOnScreen(page,held,mode.name+' Watch staff '+time+'s');
        await paintedStemOnScreen(page,held,mode.name+' Watch staff '+time+'s');
      }
      if(time===17.25)for(const character of ['kami','swyrlz'])faceFront(await rig(page,character),mode.name+' Watch '+character+' max face depth');
    }
    await seek(page,19);await page.screenshot({path:resolve(output,'socket-emergence-'+mode.name+'-watch.png')});
    await page.locator('#animeScreeningClose').click();await frames(page);
    assert.equal((await status(page)).active,false,'Closing Watch does not restore native editing');

    // Fresh context ensures Save/Load cannot rely on an already-built puppet.
    // Release the completed editor first: two active software-rendered native
    // engines compete for the same headless GPU process and stall startup.
    assert.deepEqual(errors,[],'Unhandled errors or missing artwork: '+mode.name);
    await context.close();
    const freshContext=await browser.newContext(options),fresh=await freshContext.newPage(),freshErrors=watch(fresh);
    await start(fresh);await fresh.evaluate(data=>window.SWYRL_ENGINE_STORYBOARD.importProject(data),exported);await frames(fresh);
    assert.deepEqual((await project(fresh)).project.animeSockets,exported.project.animeSockets,'Fresh native Load changes the authored sockets');
    assert.deepEqual((await project(fresh)).project.animeEmergence,exported.project.animeEmergence,'Fresh native Load loses the book opening');
    assert.deepEqual((await project(fresh)).project.animeRigs,exported.project.animeRigs,'Fresh native Load loses the resized staff fit');
    safe(await seek(fresh,17.25),mode.name+' imported articulated pose',true);
    const imported=await rig(fresh,'kami');connected(imported,mode.name+' fresh imported Kami');
    for(const id of Object.keys(posedRig.joints))close(distance(posedRig.joints[id].worldPosition,imported.joints[id].worldPosition),0,
      'Native Save/Load loses the actual articulated joint '+id,.002);
    staffAttached(imported,mode.name+' fresh imported staff mount');
    close(distance(posedRig.staffGrip.shaftMountWorld,imported.staffGrip.shaftMountWorld),0,
      'Fresh Load changes the actual authored head-to-pole mount',.002);
    for(const time of [0,4,8,14]){await seek(fresh,time);expandedGeometry(await emergence(fresh),mode.name+' imported opening '+time+'s');}
    await fresh.evaluate(data=>window.SWYRL_ENGINE_STORYBOARD.importProject(data),detachedExport);await frames(fresh);
    assert.equal((await socketModel(fresh,'kami')).connections.leftForearm.connected,false,
      'Fresh native Load discards an intentionally detached limb');
    await seek(fresh,17.25);const importedDetached=await rig(fresh,'kami');
    connected(importedDetached,mode.name+' fresh detached import',['leftForearm']);
    close(distance(importedDetached.joints.leftForearm.worldPosition,detachedRender.joints.leftForearm.worldPosition),0,
      'Native Save/Load loses the actual detached forearm placement',.002);
    const malformed=structuredClone(exported);
    malformed.project.animeSockets.characters.kami.connections.leftUpperArm={parent:'leftHand',socket:'grip',connected:false};
    malformed.project.animeSockets.characters.kami.parts.unknownPiece={attach:{x:0,y:0,z:0},sockets:{}};
    malformed.project.animeSockets.characters.kami.parts.leftUpperArm.sockets.unknown={x:0,y:0,z:0};
    malformed.project.animeSockets.characters.kami.parts.leftUpperArm.sockets.elbow.x=Infinity;
    malformed.project.animeEmergence.layers.unknown={delay:0,duration:1};
    await fresh.evaluate(data=>window.SWYRL_ENGINE_STORYBOARD.importProject(data),malformed);await frames(fresh);
    const sanitized=await socketModel(fresh,'kami');
    assert.deepEqual(sanitized.connections.leftUpperArm,{parent:'torso',socket:'leftShoulder',connected:true},
      'Native Load admits a cyclic or disconnected socket tree');
    assert.equal(sanitized.parts.unknownPiece,undefined,'Native Load retains an unknown piece');
    assert.equal(sanitized.parts.leftUpperArm.sockets.unknown,undefined,'Native Load retains an unknown socket');
    assert.ok(Number.isFinite(sanitized.parts.leftUpperArm.sockets.elbow.x),'Native Load retains a non-finite socket');
    assert.equal((await project(fresh)).project.animeEmergence.layers.unknown,undefined,'Native Load retains an unknown entrance');
    await seek(fresh,19);connected(await rig(fresh,'kami'),mode.name+' malformed import repaired native tree');
    assert.deepEqual(freshErrors,[],'Fresh imported project errors: '+mode.name);await freshContext.close();

    console.log('SOCKET_EMERGENCE_'+mode.name.toUpperCase()+'_PASS',JSON.stringify({screenshots:output}));
  }
  allPassed=true;
}finally{await browser.close();}
if(allPassed)console.log(modes.length===2?'SOCKET_EMERGENCE_BOTH_VIEWPORTS_PASSED':'SOCKET_EMERGENCE_SELECTED_VIEWPORT_PASSED');
