import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {mkdir,readFile,writeFile} from 'node:fs/promises';
import {resolve} from 'node:path';
import {inflateSync} from 'node:zlib';

// Verify the real indexed costume surfaces, their physical back faces and
// movement driven by saved body poses, through native Play and Watch.
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
  assert.equal(await page.evaluate(()=>window.SWRLZ_FORGE_BUILD?.version),'v11.62','Staff acceptance loaded a different engine release');
  await page.waitForFunction(()=>{const state=window.SWYRL_ENGINE_STORYBOARD.stageStatus();
    return state.assetsReady||state.assetErrors?.length;},undefined,{timeout:45000,polling:100});
  await loadHistoricalEpisode(page);
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
  // Native authoring advances the editor history revision; all saved layer
  // properties and the other editor settings still need to remain identical.
  const {revision:savedRevision,...savedEditor}=saved.editor;
  const {revision:originalRevision,...originalEditor}=original.editor;
  assert.deepEqual(savedEditor,originalEditor,'Piece depth editing overwrites native layers or settings: '+label);
}

// Use the same independent PNG decoder as the socket acceptance. The gold
// material must appear in the WebGL image, in addition to having real geometry.
function pngPixels(buffer){
  let width=0,height=0,channels=0;const data=[];
  for(let offset=8;offset<buffer.length;){
    const length=buffer.readUInt32BE(offset),type=buffer.toString('ascii',offset+4,offset+8),chunk=buffer.subarray(offset+8,offset+8+length);
    if(type==='IHDR'){width=chunk.readUInt32BE(0);height=chunk.readUInt32BE(4);assert.equal(chunk[8],8,'Unsupported screenshot bit depth');
      assert.ok(chunk[9]===2||chunk[9]===6,'Unsupported screenshot color type');channels=chunk[9]===6?4:3;assert.equal(chunk[12],0,'Interlaced screenshot');}
    if(type==='IDAT')data.push(chunk);offset+=length+12;
  }
  const raw=inflateSync(Buffer.concat(data)),stride=width*channels,pixels=Buffer.alloc(stride*height);
  const paeth=(a,b,c)=>{const p=a+b-c,pa=Math.abs(p-a),pb=Math.abs(p-b),pc=Math.abs(p-c);return pa<=pb&&pa<=pc?a:pb<=pc?b:c;};
  for(let y=0;y<height;y++)for(let x=0;x<stride;x++){
    const filter=raw[y*(stride+1)],index=y*stride+x,a=x>=channels?pixels[index-channels]:0,
      b=y?pixels[index-stride]:0,c=y&&x>=channels?pixels[index-stride-channels]:0;
    const prediction=filter===0?0:filter===1?a:filter===2?b:filter===3?Math.floor((a+b)/2):filter===4?paeth(a,b,c):NaN;
    assert.ok(Number.isFinite(prediction),'Unknown screenshot PNG filter');pixels[index]=(raw[y*(stride+1)+x+1]+prediction)&255;
  }
  return {width,height,rgb:(x,y)=>Array.from(pixels.subarray((y*width+x)*channels,(y*width+x)*channels+3)),
    alpha:(x,y)=>channels===4?pixels[(y*width+x)*channels+3]:255};
}
function transformed(point,matrix){
  const [x,y,z]=point,w=matrix[3]*x+matrix[7]*y+matrix[11]*z+matrix[15];
  return [0,1,2].map(row=>(matrix[row]*x+matrix[row+4]*y+matrix[row+8]*z+matrix[row+12])/w);
}
function ornamentBox(box,label){
  assert.ok(box?.min?.length===3&&box.max?.length===3&&box.min.every(Number.isFinite)&&box.max.every(Number.isFinite),
    'Staff metalwork has no measured vertex bounds: '+label);
  assert.ok(box.max.every((value,index)=>value>=box.min[index]),'Staff metalwork bounds are inverted: '+label);
}
function finishMaterial(material,label){
  assert.equal(material?.type,'MeshBasicMaterial','Staff finish is not painted onto its actual mesh: '+label);
  assert.equal(material.mapIsCanvas,true,'Staff finish has no actual painted canvas texture: '+label);
  assert.ok(material.mapType!==null&&material.width>=256&&material.height>=128,'Staff finish has no resolved texture image: '+label);
}
function ornamentGeometry(render,label){
  const grip=render.staffGrip,ornament=grip?.ornament,core=grip?.shaftGeometry;
  assert.equal(ornament?.style,'ebony-inlay-v1','Kami is missing the ornate socketed staff: '+label);
  assert.equal(core?.type,'CylinderGeometry','Staff ornament replaced the continuous round pole: '+label);
  assert.equal(core.radialSegments,24,'The fitted pole lost its actual round cross-section: '+label);
  close(core.diameter,.11,'Staff metalwork changed the grip diameter: '+label,1e-7);
  close(grip.gripError,distance(grip.gripWorld,grip.shaftGripWorld),'Staff ornament grip error ignores measured sockets: '+label,1e-7);
  close(grip.shaftMountError,distance(grip.headStemAnchorWorld,grip.shaftMountWorld),'Staff ornament mount error ignores measured sockets: '+label,1e-7);
  assert.ok(grip.gripError<1e-5&&grip.shaftMountError<1e-5&&grip.headStemAxisError<1e-5,
    'Decorating the staff separated its hand or painted crest socket: '+label);
  assert.ok(grip.ferruleFrontClearance>.001&&grip.shaftFrontClearance>.001&&grip.ferruleFrontWorldClearance>0,
    'The rounded crest sleeve covers the painted joining stem: '+label);
  assert.ok(ornament.shaftMatrixWorld?.length===16&&ornament.shaftMatrixWorld.every(Number.isFinite)&&
    ornament.cameraWorld?.length===3&&ornament.cameraWorld.every(Number.isFinite),'Staff metalwork lacks the actual pole/camera transforms: '+label);
  const matrix=ornament.shaftMatrixWorld,scaleY=Math.hypot(matrix[4],matrix[5],matrix[6]),
    gripY=ornament.shaftEndpoints[0]+grip.lowerPoleReach/scaleY;
  close(distance(transformed([0,ornament.shaftEndpoints[0],0],matrix),grip.shaftBaseWorld),0,
    'Ornament pole endpoints do not use the actual shaft matrix: '+label,1e-6);
  close(distance(transformed([0,ornament.shaftEndpoints[1],0],matrix),grip.shaftTopWorld),0,
    'Ornament top does not use the actual shaft matrix: '+label,1e-6);
  close(distance(transformed([0,gripY,0],matrix),grip.shaftGripWorld),0,
    'Ornament grip exclusion does not follow the actual hand socket: '+label,1e-6);
  finishMaterial(ornament.coreMaterial,label+' ebony core');
  assert.ok(ornament.coreSamples?.length>=12,'Ebony material has no real camera-facing ray intersections: '+label);
  const colors=[];
  for(const sample of ornament.coreSamples){
    assert.equal(sample.meshUUID,ornament.shaftMesh,'Core texture sample belongs to a different mesh: '+label);
    assert.ok(sample.mapPixel?.length===2&&sample.mapRGB?.length===3&&sample.rgb?.length===3&&sample.alpha>.9,
      'Core detail sample does not read actual texture RGBA: '+label);
    close(distance(transformed(sample.local,matrix),sample.world),0,'Core texture sample ignores actual pole geometry: '+label,1e-6);
    colors.push(sample.mapRGB);
  }
  assert.ok(colors.some((rgb,index)=>colors.slice(index+1).some(next=>distance(rgb,next)>30)),
    'The staff finish is a flat color with no measured grain/inlay variation: '+label);
  assert.deepEqual(ornament.parts.map(part=>part.id).sort(),['butt-cap','neck','ring-1','ring-2','ring-3','ring-4'],
    'Staff loses the rounded crest sleeve, close-fitting bands or lower shoe: '+label);
  assert.equal(new Set(ornament.parts.map(part=>part.meshUUID)).size,6,'Staff details reuse a nominal mesh instead of separate geometry: '+label);
  let measuredGripClearance=Infinity,measuredEndpointClearance=Infinity;
  for(const part of ornament.parts){
    const partLabel=label+' '+part.id;
    assert.equal(part.geometryType,'LatheGeometry','Staff detail has a box silhouette: '+partLabel);
    assert.equal(part.radialSegments,24,'Staff detail is not built around the round pole: '+partLabel);
    assert.ok(part.vertexCount>=48&&part.vertices?.length>=48,'Staff detail has no actual rounded geometry vertices: '+partLabel);
    ornamentBox(part.boundsLocal,partLabel+' local');ornamentBox(part.boundsWorld,partLabel+' world');finishMaterial(part.material,partLabel);
    const center=[0,2].map(axis=>(part.boundsLocal.min[axis]+part.boundsLocal.max[axis])*.5),angles=new Set();
    for(const vertex of part.vertices){
      assert.ok(vertex.local?.length===3&&vertex.world?.length===3&&vertex.local.every(Number.isFinite)&&vertex.world.every(Number.isFinite),
        'Staff detail contains a non-finite actual vertex: '+partLabel);
      close(distance(transformed(vertex.local,matrix),vertex.world),0,'Staff detail does not follow its real pole matrix: '+partLabel,1e-6);
      for(let axis=0;axis<3;axis++){
        assert.ok(vertex.local[axis]>=part.boundsLocal.min[axis]-1e-7&&vertex.local[axis]<=part.boundsLocal.max[axis]+1e-7,
          'Staff detail local bounds exclude its actual vertices: '+partLabel);
        assert.ok(vertex.world[axis]>=part.boundsWorld.min[axis]-1e-7&&vertex.world[axis]<=part.boundsWorld.max[axis]+1e-7,
          'Staff detail world bounds exclude its actual vertices: '+partLabel);
      }
      const radius=Math.hypot(vertex.local[0]-center[0],vertex.local[2]-center[1]);
      assert.ok(radius<=part.radialRange[1]+1e-6,'Staff detail radius ignores its actual geometry: '+partLabel);
      if(radius>.001)angles.add(Math.round(Math.atan2(vertex.local[2]-center[1],vertex.local[0]-center[0])*1e5));
      const poleY=vertex.local[1]-gripY;
      assert.ok(Math.abs(poleY)>.30,'A metal ornament occupies the space needed by the fingers: '+partLabel);
      measuredGripClearance=Math.min(measuredGripClearance,Math.abs(poleY)-.30);
      if(part.id==='butt-cap')measuredEndpointClearance=Math.min(measuredEndpointClearance,
        vertex.local[1]-ornament.shaftEndpoints[0],ornament.shaftEndpoints[1]-vertex.local[1]);
    }
    assert.ok(angles.size>=24,'Staff detail only reports rounded bounds around angular/box geometry: '+partLabel);
    close(part.axialRange[0],part.boundsLocal.min[1],'Staff detail axial range ignores actual bounds: '+partLabel,1e-7);
    close(part.axialRange[1],part.boundsLocal.max[1],'Staff detail axial range ignores actual bounds: '+partLabel,1e-7);
    for(let index=0;index<2;index++)close(part.poleAxialRange[index],part.axialRange[index]-gripY,
      'Staff detail axial position ignores the hand socket: '+partLabel,1e-6);
    if(part.id.startsWith('ring-')){
      assert.ok(part.radialRange[1]>=.063&&part.radialRange[1]<=.068001,'A staff band is too thin to read or has become a broad collar: '+partLabel);
      assert.ok(Math.abs(center[0])<1e-6&&Math.abs(center[1])<1e-6,'A staff band is not centred around the actual pole: '+partLabel);
    }else assert.ok(part.radialRange[1]<=.068001,'The staff crest sleeve or shoe has become an oversized block: '+partLabel);
    if(part.id==='butt-cap'){
      assert.ok(part.axialRange[0]>=ornament.shaftEndpoints[0]-1e-7&&part.axialRange[1]<=ornament.shaftEndpoints[0]+.24,
        'The rounded shoe extends the staff into the book: '+partLabel);
    }
    for(const sample of part.screenSamples){
      assert.equal(sample.meshUUID,part.meshUUID,'Staff gold sample belongs to a different mesh: '+partLabel);
      assert.ok(sample.uv?.length===2&&sample.mapPixel?.length===2&&sample.rgb?.length===3&&sample.alpha>.9,
        'Staff gold sample does not come from an actual textured ray intersection: '+partLabel);
      close(distance(transformed(sample.local,matrix),sample.world),0,'Staff gold sample is not on its transformed mesh: '+partLabel,1e-6);
    }
  }
  close(ornament.gripExclusionHalfLength,.30,'Staff metalwork does not preserve the finger contact zone: '+label,1e-7);
  close(ornament.gripZoneClearance,measuredGripClearance,'Grip clearance does not measure actual ornament vertices: '+label,1e-6);
  assert.ok(ornament.gripZoneClearance>0,'Staff metalwork collides with the gripping hand: '+label);
  close(ornament.endpointClearance,measuredEndpointClearance,'Staff shoe endpoint clearance is not actual geometry: '+label,1e-6);
  assert.ok(ornament.endpointClearance>=-1e-7,'Staff shoe crosses the original pole endpoint: '+label);
  return ornament;
}
async function goldOnScreen(page,render,label){
  const ornament=render.staffGrip.ornament,buffer=await page.locator('canvas:visible').first().screenshot(),image=pngPixels(buffer),measured=[];
  let matches=0;const matchedParts=new Set();
  for(const part of ornament.parts)for(const sample of part.screenSamples){
    const cx=Math.round(sample.screen[0]*image.width),cy=Math.round(sample.screen[1]*image.height);let error=Infinity;
    assert.ok(sample.screen.every(Number.isFinite),'Staff gold has no actual camera projection: '+label+' '+part.id);
    for(let y=Math.max(0,cy-2);y<=Math.min(image.height-1,cy+2);y++)for(let x=Math.max(0,cx-2);x<=Math.min(image.width-1,cx+2);x++)
      error=Math.min(error,distance(image.rgb(x,y),sample.rgb)/Math.sqrt(3));
    measured.push({id:part.id,screen:sample.screen,rgb:sample.rgb,error});
    if(error<43){matches++;matchedParts.add(part.id);}
  }
  if(matches<3||matchedParts.size<2){
    const name=label.replace(/[^a-z0-9]+/gi,'-');
    await writeFile(resolve(output,name+'-staff-gold-failure.png'),buffer);
    await writeFile(resolve(output,name+'-staff-gold-failure.json'),JSON.stringify({width:image.width,height:image.height,ornament,measured},null,2));
  }
  assert.ok(matches>=3&&matchedParts.size>=2,'The actual WebGL image does not show the staff metalwork: '+label+
    ' matched samples '+matches+' on '+matchedParts.size+' parts');
}
function ornamentFollows(frames,label){
  const first=frames[0];assert.ok(frames.length>=3,'Staff animation was inspected at too few authored poses: '+label);
  assert.ok(frames.some(frame=>distance(frame.render.staffGrip.shaftTopWorld,first.render.staffGrip.shaftTopWorld)>.003),
    'The authored story never moves the ornamented staff: '+label);
  for(const frame of frames.slice(1))for(const original of first.ornament.parts){
    const next=frame.ornament.parts.find(part=>part.id===original.id);
    assert.equal(next.meshUUID,original.meshUUID,'An animated ornament is rebuilt as a detached prop: '+label+' '+original.id);
    for(const bound of ['min','max'])close(distance(next.boundsLocal[bound],original.boundsLocal[bound]),0,
      'An ornament drifts relative to the moving pole: '+label+' '+original.id,1e-6);
  }
}
async function fullStaffSource(page){
  const response=await page.request.get(base+'/assets/anime/kami-full-staff.png');
  assert.equal(response.status(),200,'The complete painted staff artwork is not packaged');
  return pngPixels(await response.body());
}
function fullStaffGeometry(render,source,label){
  const grip=render.staffGrip,full=grip?.fullStaff,shaft=grip?.shaftGeometry;
  assert.equal(full?.style,'painted-full-v1','Kami is still holding a separate small wand above a pole: '+label);
  assert.equal(full.asset,'assets/anime/kami-full-staff.png','Staff card uses the old isolated crest artwork: '+label);
  assert.equal(grip.ornament,null,'Full painted staff has duplicate collars over its integrated shaft: '+label);
  assert.equal(full.source.width,source.width,'Staff source width differs from its actual PNG: '+label);
  assert.equal(full.source.height,source.height,'Staff source height differs from its actual PNG: '+label);
  const crop=full.source.crop,card=full.card,core=full.core,matrix=card.matrixWorld;
  assert.ok(crop.x0>=0&&crop.y0>=0&&crop.x1<=source.width&&crop.y1<=source.height&&crop.x1>crop.x0&&crop.y1>crop.y0,
    'Complete staff artwork has an invalid source crop: '+label);
  assert.ok(card.width>.7&&card.height>4.5&&card.height<6.5,'The complete painted staff still has wand proportions: '+label);
  close(card.width/card.height,(crop.x1-crop.x0)/(crop.y1-crop.y0),'The staff card stretches its painted proportions: '+label,1e-6);
  assert.ok(card.frontMesh&&card.backMesh&&card.edgeMesh&&new Set([card.frontMesh,card.backMesh,card.edgeMesh]).size===3,
    'Complete staff lacks separate painted front, back and paper cut edge: '+label);
  assert.ok(matrix?.length===16&&matrix.every(Number.isFinite)&&card.vertices?.length>=24,
    'Complete staff has no actual transformed card geometry: '+label);
  for(const vertex of card.vertices){
    assert.ok(vertex.local?.length===3&&vertex.world?.length===3&&vertex.local.every(Number.isFinite)&&vertex.world.every(Number.isFinite),
      'Complete staff contains a non-finite actual vertex: '+label);
    close(distance(transformed(vertex.local,matrix),vertex.world),0,'The painted staff does not follow its real card transform: '+label,1e-6);
  }
  assert.equal(shaft?.type,'CylinderGeometry','Complete staff has no physical round core inside the grip: '+label);
  assert.equal(core.radialSegments,24,'Complete staff core has a box cross-section: '+label);
  close(core.radius*2,shaft.diameter,'Painted staff core width ignores its actual cylinder: '+label,1e-7);
  assert.ok(shaft.diameter>=.10&&shaft.diameter<=.15,'Complete staff core is too narrow or has become a broad block: '+label);
  const span=core.sourceGripSpan;
  assert.ok(Number.isInteger(span?.pixelY)&&Number.isInteger(span.minX)&&Number.isInteger(span.maxX)&&span.maxX>=span.minX,
    'The staff core does not measure the actual painted grip width: '+label);
  for(let x=span.minX;x<=span.maxX;x++)assert.ok(source.alpha(x,span.pixelY)>=235,
    'The fitted staff core measures transparent grip margin: '+label);
  close(span.opaqueWidth,span.maxX-span.minX+1,'The staff grip width ignores actual opaque source pixels: '+label,1e-7);
  close(span.widthLocal,span.opaqueWidth*card.width/(crop.x1-crop.x0),'Staff grip width ignores its actual painted card scale: '+label,1e-7);
  assert.ok(shaft.diameter<=span.widthLocal*1.02,'The round core protrudes beyond the painted staff grip: '+label);
  assert.ok(core.matrixWorld?.length===16&&core.matrixWorld.every(Number.isFinite),'The full staff core lacks its actual transform: '+label);
  assert.ok(core.foot&&core.foot.meshUUID===core.footMesh&&core.foot.geometryType==='LatheGeometry'&&core.foot.vertices?.length>=48,
    'The complete painted staff shoe has no measured round tapered backing: '+label);
  let coreFootY=Infinity;
  for(const vertex of core.foot.vertices){
    assert.ok(vertex.local?.length===3&&vertex.world?.length===3&&vertex.local.every(Number.isFinite)&&vertex.world.every(Number.isFinite),
      'The tapered staff shoe contains a non-finite actual vertex: '+label);
    close(distance(transformed(vertex.local,core.matrixWorld),vertex.world),0,'The tapered shoe does not follow its real staff core transform: '+label,1e-6);
    assert.ok(Math.hypot(vertex.local[0],vertex.local[2])<=core.radius+1e-6,'The shoe expands into a box beneath the painted staff: '+label);
    coreFootY=Math.min(coreFootY,vertex.local[1]);
  }
  const physicalPoleLength=core.endpointsLocal[1][1]-coreFootY;
  assert.ok(physicalPoleLength/card.height>.65&&physicalPoleLength/card.height<.9,
    'The painted crest is not integrated with a full-length round pole and tapered foot: '+label);
  close(core.gripLocal[1]-coreFootY,core.paintedFootReach,'The painted shoe reach ignores its actual backing vertices: '+label,1e-6);
  for(let index=0;index<2;index++){
    close(distance(transformed(core.endpointsLocal[index],core.matrixWorld),core.endpointsWorld[index]),0,
      'The full staff endpoints ignore actual core geometry: '+label,1e-6);
    close(distance(core.endpointsWorld[index],index?grip.shaftTopWorld:grip.shaftBaseWorld),0,
      'The painted staff core and measured shaft endpoints differ: '+label,1e-6);
  }
  close(core.height,distance(core.endpointsLocal[0],core.endpointsLocal[1]),'Full staff core height does not measure its actual endpoints: '+label,1e-6);
  close(distance(transformed(core.gripLocal,core.matrixWorld),grip.shaftGripWorld),0,
    'Full painted staff core misses its actual grip point: '+label,1e-6);
  close(grip.gripError,distance(grip.gripWorld,grip.shaftGripWorld),'Painted staff grip error ignores actual sockets: '+label,1e-7);
  close(grip.shaftMountError,distance(grip.headStemAnchorWorld,grip.shaftMountWorld),'Painted staff stem mount ignores actual sockets: '+label,1e-7);
  assert.ok(grip.gripError<1e-5&&grip.shaftMountError<1e-5&&grip.headStemAxisError<1e-5,
    'The complete painted staff separates from its hand or upper stem: '+label);
  assert.ok(full.poleFrontClearance>.005,'The round core obscures the painted pole inside the grip: '+label);
  assert.ok(grip.naturalGrip?.layered&&grip.fingerFrontClearance>.005,'The fingers do not wrap in front of the complete staff: '+label);
  for(const [field,sign] of [['palmSamples',-1],['fingerSamples',1]]){
    assert.ok(grip.naturalGrip[field]?.length>=3,'Complete staff has no measured '+field+' around its grip: '+label);
    for(const sample of grip.naturalGrip[field]){
      const clearance=distance(grip.naturalGrip.cameraWorld,sample.shaftFrontWorld)-distance(grip.naturalGrip.cameraWorld,sample.world);
      close(sample.frontClearance,clearance,'Painted staff grip layering ignores actual surfaces: '+label,1e-7);
      assert.ok(clearance*sign>.001,'Complete staff is not between its rear palm and front fingers: '+label);
    }
  }
  assert.deepEqual(full.regions.map(region=>region.id).sort(),['crest','gripContact','lowerPole','neck','shoe','upperPole'],
    'The complete staff does not measure its crest, integrated stem, grip and lower pole separately: '+label);
  const checkPaintedSample=(sample,sampleLabel)=>{
    assert.ok(sample.pixel?.length===2&&sample.pixel.every(Number.isInteger)&&sample.pixel[0]>=0&&sample.pixel[0]<source.width&&
      sample.pixel[1]>=0&&sample.pixel[1]<source.height,'A painted staff sample has no actual source pixel: '+sampleLabel);
    const sourceRGB=source.rgb(...sample.pixel);
    assert.ok(sample.rgb?.length===3&&sample.rgb.every((value,index)=>Math.abs(value-sourceRGB[index])<=1),
      'Painted staff RGB differs from the actual supplied PNG beyond canvas alpha-rounding: '+sampleLabel);
    close(sample.alpha,source.alpha(...sample.pixel)/255,'Painted staff alpha differs from the actual supplied PNG: '+sampleLabel,1e-7);
    assert.ok(sample.alpha>.9,'Complete staff samples transparent margin instead of painted ink: '+sampleLabel);
    const expectedX=((sample.pixel[0]+.5-crop.x0)/(crop.x1-crop.x0)-.5)*card.width,
      expectedY=(.5-(sample.pixel[1]+.5-crop.y0)/(crop.y1-crop.y0))*card.height;
    close(sample.local[0],expectedX,'Staff sample is detached from its source-image X: '+sampleLabel,card.width/(crop.x1-crop.x0)*.501);
    close(sample.local[1],expectedY,'Staff sample is detached from its source-image Y: '+sampleLabel,card.height/(crop.y1-crop.y0)*.501);
    close(distance(transformed(sample.local,matrix),sample.world),0,'Painted staff ink is not on the actual transformed card: '+sampleLabel,1e-6);
    assert.ok(sample.screen?.length===3&&sample.screen.every(Number.isFinite),'Painted staff ink has no actual camera projection: '+sampleLabel);
  };
  for(const region of full.regions){
    assert.ok(region.samples.length>=3,'Complete staff has no high-alpha painted samples in '+region.id+': '+label);
    for(const sample of region.samples)checkPaintedSample(sample,label+' '+region.id);
  }
  assert.ok(full.spine?.length>=35,'The complete staff has no measured painted continuity from crest to shoe: '+label);
  for(const sample of full.spine)checkPaintedSample(sample,label+' painted spine');
  const poleSpine=full.spine.filter(sample=>sample.pixel[1]>=full.source.anchors.shaftY).sort((a,b)=>a.pixel[1]-b.pixel[1]);
  assert.ok(poleSpine.length>=25&&poleSpine[0].pixel[1]<=full.source.anchors.shaftY+64&&poleSpine.at(-1).pixel[1]>=crop.y1-64,
    'The integrated painted pole stops at the hand or misses its upper stem/lower shoe: '+label);
  for(let index=1;index<poleSpine.length;index++)assert.ok(poleSpine[index].pixel[1]-poleSpine[index-1].pixel[1]<=64,
    'The full staff has a transparent break between its crest and lower pole: '+label);
  return full;
}
async function fullStaffOnScreen(page,render,label){
  const full=render.staffGrip.fullStaff,buffer=await page.locator('canvas:visible').first().screenshot(),image=pngPixels(buffer),measured=[];
  assert.ok(render.staffGrip.gripFacingRight&&render.staffGrip.wristScreen[0]<render.staffGrip.gripScreen[0],
    'Kami’s hand does not enter from the viewer’s left and wrap right around the complete staff: '+label);
  for(const id of ['crest','neck','upperPole','lowerPole']){
    const region=full.regions.find(region=>region.id===id);let matches=0;
    for(const sample of region.samples){
      const cx=Math.round(sample.screen[0]*image.width),cy=Math.round(sample.screen[1]*image.height);let error=Infinity;
      for(let y=Math.max(0,cy-2);y<=Math.min(image.height-1,cy+2);y++)for(let x=Math.max(0,cx-2);x<=Math.min(image.width-1,cx+2);x++)
        error=Math.min(error,distance(image.rgb(x,y),sample.rgb)/Math.sqrt(3));
      measured.push({id,pixel:sample.pixel,screen:sample.screen,rgb:sample.rgb,error});if(error<43)matches++;
    }
    if(matches<3){
      const name=label.replace(/[^a-z0-9]+/gi,'-');
      await writeFile(resolve(output,name+'-full-staff-failure.png'),buffer);
      await writeFile(resolve(output,name+'-full-staff-failure.json'),JSON.stringify({width:image.width,height:image.height,full,measured},null,2));
    }
    assert.ok(matches>=3,'The actual WebGL image does not show the complete painted staff '+id+': '+label+' matched '+matches);
  }
}
function fullStaffFollows(frames,label){
  const first=frames[0];assert.ok(frames.length>=3,'Complete staff inspected at too few authored poses: '+label);
  assert.ok(frames.some(frame=>distance(frame.render.staffGrip.shaftTopWorld,first.render.staffGrip.shaftTopWorld)>.003),
    'The authored animation never moves the complete staff: '+label);
  for(const frame of frames.slice(1)){
    assert.equal(frame.full.card.frontMesh,first.full.card.frontMesh,'The complete painted staff is rebuilt as a detached prop: '+label);
    assert.equal(frame.full.core.meshUUID,first.full.core.meshUUID,'The staff core detaches while the painted prop animates: '+label);
    for(const region of first.full.regions){
      const actual=frame.full.regions.find(value=>value.id===region.id);
      assert.deepEqual(actual.samples.map(sample=>sample.pixel),region.samples.map(sample=>sample.pixel),
        'An animated staff changes its authored source-image anchor: '+label+' '+region.id);
    }
  }
}

let passed=false;
try{
  for(const mode of modes){
    const options={viewport:mode.viewport,isMobile:mode.isMobile,hasTouch:mode.hasTouch,acceptDownloads:true};
    const context=await browser.newContext(options),page=await context.newPage(),errors=watch(page);
    await start(page);
    const original=await project(page),staffSource=await fullStaffSource(page);
    assert.equal(original.project.animeRigs.characters.kami.staffArt,'painted-full-v1','Starter does not save the complete staff artwork profile');
    assert.equal(original.project.animeRelief?.schema,'anime-character-relief-v1','Starter does not save independent character piece relief');
    assert.equal(original.scene.actors.length,70,'Relief replaces native actors');assert.equal(original.editor.layers.length,11,'Relief replaces editor layers');
    const originals=Object.fromEntries(await Promise.all(['kami','swyrlz'].map(async character=>[character,await reliefModel(page,character)])));
    for(const character of ['kami','swyrlz'])assert.equal(Object.keys(originals[character].parts).length,19,
      'The starter omits saved depth sections for a character piece: '+character);
    await page.locator('#playBtn').click();
    await page.waitForFunction(()=>window.SWYRL_ENGINE_ANIMATION.status().active,undefined,{timeout:15000});
    await page.locator('#animeCinePause').click();
    const story=[],staffPlay=[];
    for(const time of [0,6,12,19,38,72,110]){
      safe(await seek(page,time),mode.name+' native Play '+time+'s');
      const snapshot={time,characters:{}};
      for(const character of ['kami','swyrlz']){
        const actual=await relief(page,character);pieceDepth(actual,originals[character],mode.name+' '+character+' '+time+'s');
        const body=await rig(page,character);pinned(body,mode.name+' '+character+' '+time+'s');snapshot.characters[character]=actual;
        if(character==='kami'&&time>=12){
          staffPlay.push({time,render:body,full:fullStaffGeometry(body,staffSource,mode.name+' native Play '+time+'s')});
          if([19,72,110].includes(time))await fullStaffOnScreen(page,body,mode.name+' native Play '+time+'s');
        }
      }
      story.push(snapshot);
      if([12,19,72].includes(time))await page.screenshot({path:resolve(output,'character-relief-'+mode.name+'-play-'+time+'.png')});
    }
    fullStaffFollows(staffPlay,mode.name+' native Play');
    for(const character of ['kami','swyrlz'])for(const id of ['cape','pelvis','torso']){
      assert.ok(story.some(frame=>Math.abs(frame.characters[character].parts[id].secondaryFlex)>1e-7),
        'The saved robe/body poses never drive costume flex: '+mode.name+' '+character+' '+id);
    }
    await seek(page,19);const repeat=await relief(page,'kami');await seek(page,72);await seek(page,19);
    sameGeometry(await relief(page,'kami'),repeat,mode.name+' repeated saved pose');
    await page.locator('#animeCineExit').click();await frames(page);
    unchangedContent(await project(page),original,mode.name+' native Play/Stop');

    // Inspect the original authored camera and staff poses in Watch before
    // the depth/pose edits below, including the genuine canvas pixels.
    await page.locator('#animeScreeningBtn').click();
    await page.waitForFunction(()=>window.SWYRL_ENGINE_ANIMATION.status().active,undefined,{timeout:15000});
    assert.equal(await page.locator('#storyCinemaStage canvas').count(),1,'Staff Watch does not mount the genuine WebGL stage');
    await page.locator('#animeCinePause').click();const staffWatch=[];
    for(const time of [12,19,72,110]){
      safe(await seek(page,time),mode.name+' original staff Watch '+time+'s');
      const actual=await rig(page,'kami');pinned(actual,mode.name+' original staff Watch '+time+'s');
      staffWatch.push({time,render:actual,full:fullStaffGeometry(actual,staffSource,mode.name+' original staff Watch '+time+'s')});
      if([19,72,110].includes(time))await fullStaffOnScreen(page,actual,mode.name+' original staff Watch '+time+'s');
    }
    fullStaffFollows(staffWatch,mode.name+' original Watch');
    await seek(page,19);await page.screenshot({path:resolve(output,'character-relief-'+mode.name+'-staff-watch.png')});
    await page.locator('#animeScreeningClose').click();await frames(page);
    unchangedContent(await project(page),original,mode.name+' staff Watch/Close');

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
    assert.ok((await project(page)).editor.revision>original.editor.revision,
      'Native depth authoring does not advance the editor history revision');
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
    fullStaffGeometry(movingRig,staffSource,mode.name+' keyed costume motion');
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
    // Opening the native studio pauses Play so that poses can be inspected.
    // Resume through its existing transport before checking running locks.
    await page.locator('#animeCinePause').evaluate(button=>button.click());
    await page.waitForFunction(()=>{const state=window.SWYRL_ENGINE_ANIMATION.status();return state.playing&&!state.paused;},
      undefined,{timeout:15000});
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
        if(character==='kami')fullStaffGeometry(actual,staffSource,mode.name+' posed staff Watch '+time+'s');
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
      if(character==='kami')fullStaffGeometry(actual,staffSource,mode.name+' fresh staff');
    }
    const legacy=structuredClone(exported);delete legacy.project.animeRelief;
    await fresh.evaluate(data=>window.SWYRL_ENGINE_STORYBOARD.importProject(data),legacy);await frames(fresh);await seek(fresh,19);
    for(const character of ['kami','swyrlz'])pieceDepth(await relief(fresh,character),await reliefModel(fresh,character),mode.name+' legacy '+character);

    // The previous natural-grip export must retain its socketed ebony/gold
    // assembly until the native preset explicitly authors the complete staff.
    const natural=await fresh.evaluate(async()=>await (await fetch('scenes/ghosts-in-different-forms-ep01-natural-grip.swyrl.json')).json());
    delete natural.project.animeRigs.characters.kami.staffArt;
    await fresh.evaluate(data=>window.SWYRL_ENGINE_STORYBOARD.importProject(data),natural);await frames(fresh);
    const previousProfile=await project(fresh),previousStaff=[];
    await fresh.evaluate(()=>window.SWYRL_ENGINE_STORYBOARD.exitPreview());await frames(fresh);
    await fresh.locator('#playBtn').click();
    await fresh.waitForFunction(()=>window.SWYRL_ENGINE_ANIMATION.status().active,undefined,{timeout:15000});
    await fresh.locator('#animeCinePause').click();
    for(const time of [12,19,72,110]){
      safe(await seek(fresh,time),mode.name+' imported natural staff '+time+'s');
      const actual=await rig(fresh,'kami');pinned(actual,mode.name+' imported natural staff '+time+'s');
      assert.equal(actual.staffGrip.fullStaff,null,'A historical natural-grip project silently acquired the complete staff artwork');
      previousStaff.push({time,render:actual,ornament:ornamentGeometry(actual,mode.name+' imported natural staff '+time+'s')});
      if([19,72,110].includes(time))await goldOnScreen(fresh,actual,mode.name+' imported natural staff '+time+'s');
    }
    ornamentFollows(previousStaff,mode.name+' imported natural staff');
    await fresh.locator('#animeCineExit').click();await frames(fresh);
    await fresh.locator('#animeScreeningBtn').click();
    await fresh.waitForFunction(()=>window.SWYRL_ENGINE_ANIMATION.status().active,undefined,{timeout:15000});
    await fresh.locator('#animeCinePause').click();const previousWatch=[];
    for(const time of [12,19,72,110]){
      safe(await seek(fresh,time),mode.name+' imported natural staff Watch '+time+'s');
      const actual=await rig(fresh,'kami');pinned(actual,mode.name+' imported natural staff Watch '+time+'s');
      previousWatch.push({time,render:actual,ornament:ornamentGeometry(actual,mode.name+' imported natural staff Watch '+time+'s')});
      if([19,72,110].includes(time))await goldOnScreen(fresh,actual,mode.name+' imported natural staff Watch '+time+'s');
    }
    ornamentFollows(previousWatch,mode.name+' imported natural staff Watch');
    await fresh.locator('#animeScreeningClose').click();await frames(fresh);
    await openStudio(fresh);await fresh.locator('#storyTrack').selectOption('kami');await fresh.locator('#rigPart').selectOption('staff');
    await input(fresh,'#storyTime',19);
    assert.equal(await fresh.locator('#rigUseFullStaff').isDisabled(),false,'Paused editor does not permit the complete staff preset');
    await fresh.locator('#rigUseFullStaff').click();await seek(fresh,19);
    const preset=await project(fresh);
    assert.equal(preset.project.animeRigs.characters.kami.staffArt,'painted-full-v1','Native preset does not save the full staff profile');
    for(const field of ['animeTimeline','animeScenery','animeEmergence'])assert.deepEqual(preset.project[field],previousProfile.project[field],
      'Staff preset overwrites the saved story, scenery or book opening: '+field);
    assert.deepEqual(preset.scene,previousProfile.scene,'Staff preset overwrites native actors');
    for(const character of ['kami','swyrlz'])for(const field of ['joints','face'])assert.deepEqual(
      preset.project.animeRigs.characters[character][field],previousProfile.project.animeRigs.characters[character][field],
      'Staff preset overwrites saved limb or face animation: '+character+' '+field);
    fullStaffGeometry(await rig(fresh,'kami'),staffSource,mode.name+' native full staff preset');
    await fullStaffOnScreen(fresh,await rig(fresh,'kami'),mode.name+' native full staff preset');
    await historyAction(fresh,'undo');await seek(fresh,19);
    for(const field of ['animeRigs','animeSockets'])assert.deepEqual((await project(fresh)).project[field],previousProfile.project[field],
      'One native Undo does not restore the previous staff artwork, fit and socket assembly: '+field);
    assert.equal((await rig(fresh,'kami')).staffGrip.fullStaff,null,'One Undo leaves the complete staff attached to the previous profile');
    ornamentGeometry(await rig(fresh,'kami'),mode.name+' full staff preset Undo');
    await historyAction(fresh,'redo');await seek(fresh,19);
    for(const field of ['animeRigs','animeSockets'])assert.deepEqual((await project(fresh)).project[field],preset.project[field],
      'Native Redo does not restore the complete staff artwork, fit and socket assembly: '+field);
    fullStaffGeometry(await rig(fresh,'kami'),staffSource,mode.name+' full staff preset Redo');
    await openStudio(fresh);await fresh.locator('#storyTrack').selectOption('kami');await fresh.locator('#rigPart').selectOption('staff');
    await input(fresh,'#rigFitHeight',6.2);await input(fresh,'#rigFitArtX',.1);await input(fresh,'#rigFitRotationZ',10);
    await fresh.locator('#rigApplyFit').click();await seek(fresh,19);
    const resizedStaff=await project(fresh);
    close(resizedStaff.project.animeRigs.characters.kami.layout.staff.height,6.2,'Native full staff height is clamped to the old wand limit');
    await fresh.locator('#rigResetFit').click();await seek(fresh,19);
    for(const field of ['animeRigs','animeSockets'])assert.deepEqual((await project(fresh)).project[field],preset.project[field],
      'Native Reset restores the old wand fit instead of the full staff fit and sockets: '+field);
    fullStaffGeometry(await rig(fresh,'kami'),staffSource,mode.name+' full staff native Reset');
    await historyAction(fresh,'undo');await seek(fresh,19);
    for(const field of ['animeRigs','animeSockets'])assert.deepEqual((await project(fresh)).project[field],resizedStaff.project[field],
      'One native Undo does not restore the resized full staff before Reset: '+field);
    await historyAction(fresh,'redo');await seek(fresh,19);
    for(const field of ['animeRigs','animeSockets'])assert.deepEqual((await project(fresh)).project[field],preset.project[field],
      'Native Redo loses the full staff Reset: '+field);
    await openStudio(fresh);const presetDownloadPending=fresh.waitForEvent('download',{timeout:15000});
    await fresh.locator('#storySaveProject').click();const presetDownload=await presetDownloadPending,
      presetExport=JSON.parse(await readFile(await presetDownload.path(),'utf8'));
    for(const field of ['animeRigs','animeSockets'])assert.deepEqual(presetExport.project[field],preset.project[field],
      'Native Save loses the full staff artwork, fit or sockets: '+field);
    await closeStudio(fresh);await fresh.evaluate(data=>window.SWYRL_ENGINE_STORYBOARD.importProject(data),natural);await frames(fresh);
    await fresh.evaluate(data=>window.SWYRL_ENGINE_STORYBOARD.importProject(data),presetExport);await frames(fresh);await seek(fresh,19);
    for(const field of ['animeRigs','animeSockets'])assert.deepEqual((await project(fresh)).project[field],presetExport.project[field],
      'Native Load loses the saved complete staff preset: '+field);
    fullStaffGeometry(await rig(fresh,'kami'),staffSource,mode.name+' loaded native full staff preset');
    const originalGrip=structuredClone(exported);originalGrip.project.animeRigs.characters.kami.gripStyle='original';
    await fresh.evaluate(data=>window.SWYRL_ENGINE_STORYBOARD.importProject(data),originalGrip);await frames(fresh);await seek(fresh,19);
    assert.equal((await rig(fresh,'kami')).staffGrip.ornament,null,'An original glove profile acquired incompatible staff metalwork');
    assert.equal((await rig(fresh,'kami')).staffGrip.fullStaff,null,'An original glove profile acquired incompatible complete staff artwork');
    const customAtlas=structuredClone(exported);customAtlas.project.animeRigs.characters.kami.asset='assets/anime/swyrlz-rig.png';
    await fresh.evaluate(data=>window.SWYRL_ENGINE_STORYBOARD.importProject(data),customAtlas);await frames(fresh);await seek(fresh,19);
    assert.equal((await project(fresh)).project.animeRigs.characters.kami.asset,customAtlas.project.animeRigs.characters.kami.asset,
      'Staff finish replaces a supplied custom atlas');
    assert.equal((await rig(fresh,'kami')).staffGrip.ornament,null,'A custom atlas acquired incompatible staff metalwork');
    assert.equal((await rig(fresh,'kami')).staffGrip.fullStaff,null,'A custom atlas acquired incompatible complete staff artwork');
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
