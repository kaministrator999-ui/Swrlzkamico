import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {mkdir,readFile} from 'node:fs/promises';
import {resolve} from 'node:path';

// Verify the real indexed costume surfaces, their physical back faces and
// movement driven by saved body poses, through native Play and Watch.
const base=(process.env.SWYRL_ANIME_TEST_URL||'http://127.0.0.1:8775').replace(/\/$/,'');
const output=resolve(process.env.SWYRL_ANIME_SCREENSHOTS_DIR||'character-relief-acceptance');
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
const rig=(page,character)=>page.evaluate(character=>window.SWYRL_ENGINE_RIG.renderStatus(character),character);
const relief=(page,character)=>page.evaluate(character=>window.SWYRL_ENGINE_RELIEF.renderStatus(character),character);
const reliefModel=(page,character)=>page.evaluate(character=>window.SWYRL_ENGINE_RELIEF.model(character),character);
const distance=(a,b)=>Math.hypot(...a.map((value,index)=>value-b[index]));
const boxCenter=box=>box.max.map((value,index)=>(value+box.min[index])*.5);
const close=(actual,expected,label,tolerance=1e-5)=>assert.ok(Number.isFinite(actual)&&Math.abs(actual-expected)<=tolerance,
  label+': expected '+expected+', received '+actual);
function watch(page){
  const errors=[];page.on('pageerror',error=>errors.push(String(error)));
  page.on('response',response=>{if(response.status()>=400&&response.url().startsWith(base)&&/\.(?:png|webp|jpe?g)(?:\?|$)/i.test(response.url()))
    errors.push('Artwork '+response.status()+' '+response.url());});
  page.on('requestfailed',request=>{if(request.url().startsWith(base)&&/\.(?:png|webp|jpe?g)(?:\?|$)/i.test(request.url()))
    errors.push('Artwork '+request.failure()?.errorText+' '+request.url());});
  return errors;
}
async function start(page){
  await page.bringToFront();
  await page.goto(base+'/index.html?project=anime-ghosts-ep01',{waitUntil:'domcontentloaded',timeout:60000});
  await page.waitForFunction(()=>window.SWYRL_ENGINE_RELIEF?.renderStatus&&window.SWYRL_ENGINE_RIG?.renderStatus&&
    window.SWYRL_ENGINE_SOCKETS?.model&&window.SWYRL_ENGINE_ANIMATION&&window.SWYRL_ENGINE_STORYBOARD,
    undefined,{timeout:60000,polling:100});
  await page.waitForFunction(()=>{const state=window.SWYRL_ENGINE_STORYBOARD.stageStatus();
    return state.assetsReady||state.assetErrors?.length;},undefined,{timeout:45000,polling:100});
  await frames(page);
}
async function input(page,selector,value){
  await page.locator(selector).evaluate((element,value)=>{
    element.value=String(value);element.dispatchEvent(new Event('input',{bubbles:true}));
    element.dispatchEvent(new Event('change',{bubbles:true}));
  },value);
}
async function seek(page,time){
  assert.equal(await page.evaluate(time=>window.SWYRL_ENGINE_ANIMATION.seek(time),time),true,'Native seek failed at '+time+'s');
  await frames(page);return page.evaluate(()=>window.SWYRL_ENGINE_STORYBOARD.stageStatus());
}
async function openStudio(page){
  if(!await page.locator('#storyStudioPanel').isVisible())await page.locator('#storyStudioBtn').click();
}
async function closeStudio(page){
  if(await page.locator('#storyStudioPanel').isVisible())await page.locator('#storyClose').click();
}
async function historyAction(page,action){
  await closeStudio(page);
  if(!(await page.evaluate(()=>window.SWYRL_ENGINE_ANIMATION.status())).playing){
    await page.evaluate(()=>window.SWYRL_ENGINE_STORYBOARD.exitPreview());await frames(page);
  }
  const quick=page.locator(action==='undo'?'#quickUndoBtn':'#quickRedoBtn');
  if(await quick.isVisible()){await quick.click();return;}
  if(!await page.locator('#mobileToolsPanel').isVisible())await page.locator('#mobileToolsBtn').click();
  await page.locator('#mobileToolsPanel [data-click="'+action+'Btn"]').click();
}
async function depthConfig(page,character,part,time,value){
  await openStudio(page);await page.locator('#storyTrack').selectOption(character);await input(page,'#storyTime',time);
  await page.locator('#reliefPart').selectOption(part);
  for(const field of ['left','center','right','thickness','flex'])
    await input(page,'#relief'+field[0].toUpperCase()+field.slice(1),value[field]);
  await page.locator('#reliefApply').click();await seek(page,time);
  const saved=(await reliefModel(page,character)).parts[part];
  for(const field of Object.keys(value))close(saved[field],value[field],'Native piece depth did not save '+part+' '+field,.000002);
}
async function poseKey(page,character,part,time,key){
  await openStudio(page);await page.locator('#storyTrack').selectOption(character);await input(page,'#storyTime',time);
  await page.locator('#rigPart').selectOption(part);
  for(const field of ['rotationX','rotationY','rotationZ','depth'])
    await input(page,'#rig'+field[0].toUpperCase()+field.slice(1),field==='depth'?key[field]:key[field]*180/Math.PI);
  await page.locator('#rigAddKey').click();await seek(page,time);
  const saved=await page.evaluate(({character,part,time})=>window.SWYRL_ENGINE_RIG.sample(character,part,time),{character,part,time});
  for(const field of Object.keys(key))close(saved[field],key[field],'Native body pose did not save '+part+' '+field,.000002);
}
function safe(state,label){
  assert.equal(state.occlusionSafe,true,'Piece relief or costume motion obscures the cast/camera: '+label);
  assert.deepEqual(state.assetErrors||[],[],'Artwork failed: '+label);
  assert.ok(state.safeCameraGap>6,'Costume geometry crosses the camera: '+label);
}
function pinned(render,label){
  assert.equal(render.rigged,true,'Character lost its articulated paper rig: '+label);
  assert.ok(render.connections.length>=18,'Piece depth loses anatomical sockets: '+label);
  for(const connection of render.connections){
    assert.equal(connection.connected,true,'Depth sections detach a body piece: '+label+' '+connection.child);
    close(connection.error,distance(connection.childAttachWorld,connection.parentSocketWorld),
      'Joint error ignores its actual XYZ endpoints: '+label+' '+connection.child,1e-7);
    assert.ok(connection.error<1e-5,'Relief or cloth motion pulls a limb from its socket: '+label+' '+connection.child);
  }
}
function finiteBox(box,label){
  assert.ok(box?.min?.length===3&&box.max?.length===3&&box.min.every(Number.isFinite)&&box.max.every(Number.isFinite),
    'Section has no actual transformed bounds: '+label);
  assert.ok(box.max.every((value,index)=>value>=box.min[index]),'Section has inverted actual bounds: '+label);
  close(box.depthSpan,box.max[2]-box.min[2],'Section depth does not measure its actual vertices: '+label,1e-7);
}
function pieceDepth(render,model,label){
  assert.equal(render.schema,'anime-character-relief-v1','Missing portable piece depth schema: '+label);
  assert.equal(render.rigged,true,'No actual character depth geometry: '+label);
  assert.equal(Object.keys(model.parts).length,19,'Every saved body/prop piece needs its own depth sections: '+label);
  let rendered=0;
  for(const [part,config] of Object.entries(model.parts)){
    for(const field of ['left','center','right','thickness','flex'])assert.ok(Number.isFinite(config[field]),
      'Non-finite saved depth configuration: '+label+' '+part+' '+field);
    assert.ok(config.thickness>0,'A saved body piece has no physical paper thickness: '+label+' '+part);
  }
  for(const [part,value] of Object.entries(render.parts)){
    assert.deepEqual(value.sections.map(section=>section.id),['left','center','right'],
      'A character piece loses an independent depth section: '+label+' '+part);
    if(!value.rendered)continue;
    rendered++;assert.equal(value.indexed,true,'Depth sections are labels instead of indexed painted geometry: '+label+' '+part);
    assert.ok(value.frontMesh&&value.backMesh&&value.edgeMesh&&new Set([value.frontMesh,value.backMesh,value.edgeMesh]).size===3,
      'A character piece lacks separate front, back and cut-edge geometry: '+label+' '+part);
    assert.ok(Number.isFinite(value.secondaryFlex),'Costume flex does not evaluate the saved story clock: '+label+' '+part);
    const config=model.parts[part==='magic'?'grimoire':part];
    close(value.thickness,config.thickness,'Rendered thickness ignores the saved piece: '+label+' '+part,.000002);
    for(const section of value.sections){
      const sectionLabel=label+' '+part+' '+section.id;
      close(section.configuredDepth,config[section.id],'Rendered section ignores its saved depth: '+sectionLabel,.000002);
      assert.ok(section.frontTriangles>0&&section.backTriangles>0&&section.triangleCount===section.frontTriangles,
        'Section has no actual indexed front/back triangles: '+sectionLabel);
      assert.ok(section.edgeTriangles>=0,'Section has invalid cut-edge geometry: '+sectionLabel);
      finiteBox(section.localBounds,sectionLabel+' local');finiteBox(section.worldBounds,sectionLabel+' world');
      assert.ok(section.localBounds.depthSpan>1e-5,'A painted piece section remains flat: '+sectionLabel);
      assert.ok(section.worldBounds.depthSpan>0,'A piece section has no actual world depth: '+sectionLabel);
      assert.ok(Number.isInteger(section.inkCount)&&section.inkCount>=0&&Array.isArray(section.surfaceSamples),
        'Section has no proof from the original painted alpha: '+sectionLabel);
      if(section.inkCount)assert.ok(section.surfaceSamples.length>0,'An opaque costume section has no measured front/back surfaces: '+sectionLabel);
      for(const sample of section.surfaceSamples){
        assert.ok(sample.alpha>=200/255&&[sample.frontLocal,sample.backLocal,sample.frontWorld,sample.backWorld].every(point=>
          point.length===3&&point.every(Number.isFinite)),'Section sample does not measure actual high-alpha indexed surfaces: '+sectionLabel);
        close(sample.thickness,sample.frontLocal[2]-sample.backLocal[2],
          'Physical piece thickness ignores actual front/back triangles: '+sectionLabel,1e-7);
        close(sample.worldThickness,distance(sample.frontWorld,sample.backWorld),
          'World thickness ignores the transformed paper surfaces: '+sectionLabel,1e-7);
        close(sample.thickness,config.thickness,'Painted front/back thickness does not follow the saved piece: '+sectionLabel,.000002);
        assert.ok(sample.thickness>0&&sample.worldThickness>0,'A painted depth section lacks physical space between its front and back: '+sectionLabel);
      }
    }
    assert.ok(value.sections.reduce((sum,section)=>sum+section.inkCount,0)>0,
      'Piece depth samples transparent cards instead of any actual painted character ink: '+label+' '+part);
  }
  assert.ok(rendered>=18,'Not every visible character piece has real depth sections: '+label);
  assert.equal(render.sectionCount,rendered*3,'Section count ignores actual rendered geometry: '+label);
}
function sameGeometry(actual,expected,label,tolerance=.00002){
  for(const [id,part] of Object.entries(expected.parts))if(part.rendered){
    assert.equal(actual.parts[id].rendered,true,'Saved geometry loses a rendered part: '+label+' '+id);
    close(actual.parts[id].secondaryFlex,part.secondaryFlex,'Saved/repeated motion changes costume flex: '+label+' '+id,tolerance);
    for(const section of part.sections){
      const next=actual.parts[id].sections.find(value=>value.id===section.id);
      for(const bound of ['min','max'])close(distance(next.localBounds[bound],section.localBounds[bound]),0,
        'Saved/repeated seek changes actual local section geometry: '+label+' '+id+' '+section.id+' '+bound,tolerance);
    }
  }
}
function faceFront(render,label){
  const face=render.face;
  assert.ok(face.featureSurfaceSampleCount>30&&face.surfaceSamples.length>20,'No measured animated facial feature surfaces: '+label);
  assert.ok(face.minFeatureClearance>.008,'Piece sections cover the facial expression: '+label);
  for(const sample of face.surfaceSamples){
    assert.ok(sample.alpha>=80/255&&sample.clearance>.008,'Actual face ink sits behind its deformed head triangle: '+label);
    assert.ok(sample.faceWorld.every(Number.isFinite)&&sample.headWorld.every(Number.isFinite)&&distance(sample.faceWorld,sample.headWorld)>0,
      'Face ink has no actual separate head/feature surfaces: '+label);
  }
}
function unchangedContent(saved,original,label){
  for(const field of ['animeTimeline','animeScenery','animeSockets','animeEmergence'])
    assert.deepEqual(saved.project[field],original.project[field],'Piece depth edits overwrite '+field+': '+label);
  assert.deepEqual(saved.scene,original.scene,'Piece depth editing overwrites native actors: '+label);
  assert.deepEqual(saved.editor,original.editor,'Piece depth editing overwrites native layers: '+label);
}

let passed=false;
try{
  for(const mode of modes){
    const options={viewport:mode.viewport,isMobile:mode.isMobile,hasTouch:mode.hasTouch,acceptDownloads:true};
    const context=await browser.newContext(options),page=await context.newPage(),errors=watch(page);
    await start(page);
    const original=await project(page);
    assert.equal(original.project.animeRelief?.schema,'anime-character-relief-v1','Starter does not save independent character piece relief');
    assert.equal(original.scene.actors.length,70,'Relief replaces native actors');assert.equal(original.editor.layers.length,11,'Relief replaces editor layers');
    const originals=Object.fromEntries(await Promise.all(['kami','swyrlz'].map(async character=>[character,await reliefModel(page,character)])));
    for(const character of ['kami','swyrlz'])assert.equal(Object.keys(originals[character].parts).length,19,
      'The starter omits saved depth sections for a character piece: '+character);
    await page.locator('#playBtn').click();
    await page.waitForFunction(()=>window.SWYRL_ENGINE_ANIMATION.status().active,undefined,{timeout:15000});
    await page.locator('#animeCinePause').click();
    const story=[];
    for(const time of [0,6,12,19,38,72,110]){
      safe(await seek(page,time),mode.name+' native Play '+time+'s');
      const snapshot={time,characters:{}};
      for(const character of ['kami','swyrlz']){
        const actual=await relief(page,character);pieceDepth(actual,originals[character],mode.name+' '+character+' '+time+'s');
        pinned(await rig(page,character),mode.name+' '+character+' '+time+'s');snapshot.characters[character]=actual;
      }
      story.push(snapshot);
      if([12,19,72].includes(time))await page.screenshot({path:resolve(output,'character-relief-'+mode.name+'-play-'+time+'.png')});
    }
    for(const character of ['kami','swyrlz'])for(const id of ['cape','pelvis','torso']){
      assert.ok(story.some(frame=>Math.abs(frame.characters[character].parts[id].secondaryFlex)>1e-7),
        'The saved robe/body poses never drive costume flex: '+mode.name+' '+character+' '+id);
    }
    await seek(page,19);const repeat=await relief(page,'kami');await seek(page,72);await seek(page,19);
    sameGeometry(await relief(page,'kami'),repeat,mode.name+' repeated saved pose');
    await page.locator('#animeCineExit').click();await frames(page);
    unchangedContent(await project(page),original,mode.name+' native Play/Stop');

    // Edit real left/centre/right folds and physical thickness in the editor.
    await seek(page,19);const before=await relief(page,'kami'),beforeRig=await rig(page,'kami');
    const authored={left:.08,center:.14,right:.105,thickness:.12,flex:.9};
    await depthConfig(page,'kami','cape',19,authored);
    const changed=await relief(page,'kami'),changedRig=await rig(page,'kami');
    pieceDepth(changed,await reliefModel(page,'kami'),mode.name+' authored cape');pinned(changedRig,mode.name+' authored cape');
    assert.ok(changed.parts.cape.sections.some((section,index)=>distance(section.localBounds.max,before.parts.cape.sections[index].localBounds.max)>.01),
      'Editing piece depth changes labels without deforming actual indexed costume geometry');
    for(const id of Object.keys(beforeRig.joints))close(distance(beforeRig.joints[id].worldPosition,changedRig.joints[id].worldPosition),0,
      'Editing costume relief moves a connected skeletal pivot: '+id,.00002);
    assert.deepEqual((await project(page)).project.animeRigs,original.project.animeRigs,'Section depth replaces the saved body/face keys');
    unchangedContent(await project(page),original,mode.name+' depth authoring');
    await historyAction(page,'undo');await seek(page,19);
    assert.deepEqual((await project(page)).project.animeRelief,original.project.animeRelief,'One Undo does not restore piece depth');
    sameGeometry(await relief(page,'kami'),before,mode.name+' depth Undo');
    await historyAction(page,'redo');await seek(page,19);
    assert.deepEqual((await reliefModel(page,'kami')).parts.cape,authored,'Redo loses saved section depth');
    sameGeometry(await relief(page,'kami'),changed,mode.name+' depth Redo');
    await openStudio(page);await page.locator('#storyTrack').selectOption('kami');await page.locator('#reliefPart').selectOption('cape');
    await page.locator('#reliefReset').click();await seek(page,19);
    assert.deepEqual((await reliefModel(page,'kami')).parts.cape,{left:.045,center:.085,right:.055,
      thickness:original.project.animeRigs.characters.kami.thickness,flex:.65},
      'Native Reset does not restore the selected robe section defaults');
    await historyAction(page,'undo');await seek(page,19);
    assert.deepEqual((await reliefModel(page,'kami')).parts.cape,authored,'Undo Reset loses the authored robe sections');
    const immutable=await reliefModel(page,'kami');
    assert.notEqual(await page.evaluate(()=>{const model=window.SWYRL_ENGINE_RELIEF.model('kami');model.parts.cape.center=999;
      return window.SWYRL_ENGINE_RELIEF.model('kami').parts.cape.center;}),999,'Public relief model permits mutation outside native history');
    for(const args of [['kami','unknownPiece',{center:.2}],['unknown','cape',{center:.2}],['kami','cape',{center:Infinity}]])
      assert.equal(await page.evaluate(args=>window.SWYRL_ENGINE_RELIEF.configure(...args),args),false,'Relief API accepts an unknown or non-finite edit');
    assert.deepEqual(await reliefModel(page,'kami'),immutable,'Rejected piece depth edit mutates saved geometry');

    // Saved body rotations drive robe and armor together. Compare the actual
    // local fold with flex on/off at one time to isolate secondary deformation.
    for(const [time,key] of [[12,{rotationX:0,rotationY:0,rotationZ:0,depth:0}],
      [38,{rotationX:.16,rotationY:.2,rotationZ:.55,depth:0}]])await poseKey(page,'kami','torso',time,key);
    for(const [time,key] of [[12,{rotationX:0,rotationY:0,rotationZ:0,depth:0}],
      [38,{rotationX:.19,rotationY:-.17,rotationZ:.6,depth:.18}]])await poseKey(page,'kami','leftUpperArm',time,key);
    await seek(page,12);const motionBefore=await relief(page,'kami');
    await seek(page,20);const moving=await relief(page,'kami'),movingRig=await rig(page,'kami');
    pieceDepth(moving,await reliefModel(page,'kami'),mode.name+' keyed costume motion');pinned(movingRig,mode.name+' keyed costume motion');
    for(const id of ['cape','pelvis','torso','leftUpperArm']){
      assert.ok(Math.abs(moving.parts[id].secondaryFlex)>1e-7,'Body movement leaves '+id+' secondary sections rigid');
      assert.ok(distance(boxCenter(motionBefore.parts[id].sections[1].worldBounds),boxCenter(moving.parts[id].sections[1].worldBounds))>.005,
        'The robe or armor does not follow its actual moving body socket: '+id);
    }
    await depthConfig(page,'kami','cape',20,{...authored,flex:0});const rigid=await relief(page,'kami');
    close(rigid.parts.cape.secondaryFlex,0,'Disabling costume flex leaves secondary motion');
    assert.ok(rigid.parts.cape.sections.some((section,index)=>distance(section.localBounds.max,moving.parts.cape.sections[index].localBounds.max)>1e-6),
      'Costume flex changes a scalar without changing actual painted robe geometry');
    await historyAction(page,'undo');await seek(page,20);
    sameGeometry(await relief(page,'kami'),moving,mode.name+' deterministic costume flex Undo');
    await seek(page,110);await seek(page,0);await seek(page,20);
    sameGeometry(await relief(page,'kami'),moving,mode.name+' arbitrary seek order');

    // Faces must stay on their exact head triangles after section depth,
    // maximum whole-piece relief and rotations around all three socket axes.
    for(const character of ['kami','swyrlz']){
      await openStudio(page);await page.locator('#storyTrack').selectOption(character);
      await input(page,'#rigDepthAmount',1.5);await page.locator('#rigApplyConfig').click();
      const headConfig={left:.13,center:.24,right:.18,thickness:.14,flex:0};
      await depthConfig(page,character,'head',20,headConfig);
      await poseKey(page,character,'head',20,{rotationX:.32,rotationY:-.31,rotationZ:.18,depth:.65});
      const actual=await rig(page,character);pinned(actual,mode.name+' maximum '+character+' head depth');
      faceFront(actual,mode.name+' maximum '+character+' head depth');
      close(actual.joints.head.artDepth,.975,'Head relief does not use the saved maximum depth',.002);
      pieceDepth(actual.depthSections,await reliefModel(page,character),mode.name+' maximum '+character+' section depth');
    }
    unchangedContent(await project(page),original,mode.name+' posed depth sections');
    await closeStudio(page);await page.evaluate(()=>window.SWYRL_ENGINE_STORYBOARD.exitPreview());await frames(page);
    await page.locator('#playBtn').click();
    await page.waitForFunction(()=>window.SWYRL_ENGINE_ANIMATION.status().active,undefined,{timeout:15000});
    await openStudio(page);await page.locator('#storyTrack').selectOption('kami');
    await page.waitForFunction(()=>document.getElementById('reliefApply').disabled&&document.getElementById('reliefReset').disabled,
      undefined,{timeout:15000,polling:100});
    assert.equal(await page.evaluate(()=>window.SWYRL_ENGINE_RELIEF.configure('kami','cape',{left:.01})),false,
      'Running Play permits changes to saved costume depth');
    assert.equal(await page.evaluate(()=>window.SWYRL_ENGINE_RELIEF.reset('kami','cape')),false,
      'Running Play permits a costume reset');
    await closeStudio(page);await page.locator('#animeCinePause').click();await seek(page,20);
    await openStudio(page);await page.locator('#storyTrack').selectOption('kami');
    assert.equal(await page.locator('#reliefApply').isDisabled(),false,'Paused Play does not permit native depth editing');
    const downloadPending=page.waitForEvent('download',{timeout:15000});await page.locator('#storySaveProject').click();
    const download=await downloadPending,exported=JSON.parse(await readFile(await download.path(),'utf8'));
    assert.deepEqual(exported.project.animeRelief,(await project(page)).project.animeRelief,'Native Save drops independent piece depth sections');
    assert.deepEqual(exported.project.animeRigs,(await project(page)).project.animeRigs,'Native Save drops depth-driven costume poses');
    unchangedContent(exported,original,mode.name+' saved depth project');
    const savedGeometry=Object.fromEntries(await Promise.all(['kami','swyrlz'].map(async character=>[character,await relief(page,character)])));
    await page.screenshot({path:resolve(output,'character-relief-'+mode.name+'-editor.png')});
    await closeStudio(page);await page.locator('#animeCineExit').click();await frames(page);
    await page.locator('#animeScreeningBtn').click();
    await page.waitForFunction(()=>window.SWYRL_ENGINE_ANIMATION.status().active,undefined,{timeout:15000});
    assert.equal(await page.locator('#storyCinemaStage canvas').count(),1,'Watch does not mount the genuine WebGL character depth stage');
    await page.locator('#animeCinePause').click();
    for(const time of [20,38,72,110]){
      safe(await seek(page,time),mode.name+' Watch '+time+'s');
      for(const character of ['kami','swyrlz']){
        const actual=await rig(page,character);pinned(actual,mode.name+' Watch '+character+' '+time+'s');
        pieceDepth(actual.depthSections,await reliefModel(page,character),mode.name+' Watch '+character+' '+time+'s');
        if(time===20){faceFront(actual,mode.name+' Watch '+character+' maximum face');sameGeometry(actual.depthSections,savedGeometry[character],mode.name+' Watch '+character);}
      }
    }
    await seek(page,20);await page.screenshot({path:resolve(output,'character-relief-'+mode.name+'-watch.png')});
    await page.locator('#animeScreeningClose').click();await frames(page);
    assert.deepEqual(errors,[],'Native character relief produces errors or missing artwork: '+mode.name);
    // A completed software-rendered editor is closed before opening another.
    // This also ensures loaded geometry cannot reuse the original puppet.
    await context.close();
    const freshContext=await browser.newContext(options),fresh=await freshContext.newPage(),freshErrors=watch(fresh);
    await start(fresh);await fresh.evaluate(data=>window.SWYRL_ENGINE_STORYBOARD.importProject(data),exported);await frames(fresh);
    assert.deepEqual((await project(fresh)).project.animeRelief,exported.project.animeRelief,'Fresh native Load loses saved per-piece depth');
    assert.deepEqual((await project(fresh)).project.animeRigs,exported.project.animeRigs,'Fresh native Load loses body-driven garment motion');
    safe(await seek(fresh,20),mode.name+' fresh loaded costume pose');
    for(const character of ['kami','swyrlz']){
      const actual=await rig(fresh,character);pinned(actual,mode.name+' fresh '+character);faceFront(actual,mode.name+' fresh '+character+' face');
      pieceDepth(actual.depthSections,await reliefModel(fresh,character),mode.name+' fresh '+character);
      sameGeometry(actual.depthSections,savedGeometry[character],mode.name+' fresh '+character);
    }
    const legacy=structuredClone(exported);delete legacy.project.animeRelief;
    await fresh.evaluate(data=>window.SWYRL_ENGINE_STORYBOARD.importProject(data),legacy);await frames(fresh);await seek(fresh,19);
    for(const character of ['kami','swyrlz'])pieceDepth(await relief(fresh,character),await reliefModel(fresh,character),mode.name+' legacy '+character);
    const malformed=structuredClone(exported);
    malformed.project.animeRelief.characters.kami.parts.unknown={left:.2};
    malformed.project.animeRelief.characters.kami.parts.cape.center=Infinity;
    malformed.project.animeRelief.characters.kami.parts.cape.left=20;
    malformed.project.animeRelief.characters.kami.parts.cape.thickness=-2;
    await fresh.evaluate(data=>window.SWYRL_ENGINE_STORYBOARD.importProject(data),malformed);await frames(fresh);
    const cleaned=await reliefModel(fresh,'kami');assert.equal(cleaned.parts.unknown,undefined,'Native Load retains an unknown piece depth section');
    close(cleaned.parts.cape.center,.085,'Native Load retains non-finite section depth');
    close(cleaned.parts.cape.left,.3,'Native Load permits unbounded relief');close(cleaned.parts.cape.thickness,.02,'Native Load permits inverted paper thickness');
    await seek(fresh,19);pinned(await rig(fresh,'kami'),mode.name+' repaired malformed depth');
    assert.deepEqual(freshErrors,[],'Fresh character relief import errors: '+mode.name);await freshContext.close();
    console.log('CHARACTER_RELIEF_'+mode.name.toUpperCase()+'_PASS',JSON.stringify({screenshots:output}));
  }
  passed=true;
}finally{await browser.close();}
if(passed)console.log(modes.length===2?'CHARACTER_RELIEF_BOTH_VIEWPORTS_PASSED':'CHARACTER_RELIEF_SELECTED_VIEWPORT_PASSED');
