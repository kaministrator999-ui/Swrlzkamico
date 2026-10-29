import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import {installSystemCATransport} from './browser_tls_v11_92.mjs';
const base=process.env.SWYRL_TEST_URL||'http://127.0.0.1:8809',out=process.env.SWYRL_TEST_OUT||'/workspace/.setup/smooth-v11-93/test';await fs.mkdir(out,{recursive:true});
const browser=await chromium.launch({headless:true,executablePath:'/usr/bin/chromium',args:['--no-sandbox','--disable-dev-shm-usage','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader']});
try{
 const context=await browser.newContext({viewport:{width:1200,height:1100},acceptDownloads:true});const page=await context.newPage();page.setDefaultTimeout(300000);await installSystemCATransport(page);
 const errors=[];page.on('pageerror',e=>{errors.push(e.message);console.error('PAGE_ERROR',e.message);});page.on('dialog',d=>d.accept());
 await page.goto(base+'/?project=organic-anime-girl',{waitUntil:'domcontentloaded'});
 await page.waitForFunction(()=>window.SWYRL_ENGINE_AGENT?.inspectScene().project.modelAtelier?.appearanceRevision==='v11.93'&&window.SWYRL_ENGINE_MODEL_ATELIER.presentation()?.groups['Festival companion']?.visible===0,null,{timeout:180000,polling:500});
 await page.evaluate(()=>{document.getElementById('seReleaseNotesClose')?.click();window.requestAnimationFrame=cb=>setTimeout(()=>cb(performance.now()),250);});
 const presentation=await page.evaluate(()=>window.SWYRL_ENGINE_MODEL_ATELIER.presentation());
 for(const name of ['Azure frost','Coral flare']){assert.equal(presentation.groups[name].visible,28,'Default view must show the actual hair piñatas');assert.equal(presentation.groups[name].inView,28,'Default camera must fit them');}
 await page.screenshot({path:out+'/default-pinatas.png'});
 const state=await page.evaluate(()=>{const m=window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier;return {status:window.SWYRL_ENGINE_MODEL_ATELIER.animalStatus(),portrait:m.portraitRefinement,legs:m.legRefinement,smoothing:m.anatomySmoothing,finish:m.festivalFinish,coverage:m.coverageRefinement};});
 assert.equal(state.status.valid,true);assert.ok(state.legs.changedVertices>10000);assert.ok(state.smoothing.upperBody.vertices>10000);assert.ok(state.smoothing.upperBody.laplacianAfter<state.smoothing.upperBody.laplacianBefore*.5);assert.equal(state.smoothing.upperBody.normalStrength,.03);
 for(const side of ['left','right']){const eye=state.portrait.eyeCorners[side];assert.ok(eye.outer[1]-eye.inner[1]>.04);assert.equal(eye.slopeDegrees,14);}
 assert.deepEqual(state.finish.restoredGripParts,['hair-grip--1','hair-grip-1']);assert.equal(state.finish.hairScale,.58);assert.equal(state.coverage.underlayer,'festival-shorts');
 for(const item of presentation.coverage){assert.equal(item.opacity,1);assert.equal(item.transparent,false);assert.equal(item.side,2);}
 await page.waitForFunction(()=>{const b=window.SWYRL_ENGINE_MODEL_ATELIER.animalStatus().meshes.find(p=>p.id==='girl-organic-body');return b?.baseColorSize[0]===4096&&b?.normalSize[0]===4096;},null,{timeout:60000,polling:500});
 // Cast rays independently through the real native geometry from multiple
 // directions. The opaque shorts must intercept before the pelvis skin.
 const coverageRays=await page.evaluate(async()=>{
  const T=await import('https://cdn.jsdelivr.net/npm/three@0.169.0/+esm'),m=window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier;
  const mesh=id=>{const p=m.parts.find(p=>p.id===id),g=new T.BufferGeometry();g.setAttribute('position',new T.Float32BufferAttribute(p.topologyMesh.positions,3));g.setIndex(p.topologyMesh.indices);const n=new T.Mesh(g,new T.MeshBasicMaterial({side:T.DoubleSide}));n.position.fromArray(p.position);n.rotation.fromArray(p.rotation);n.scale.fromArray(p.scale);n.updateMatrixWorld(true);return n;};
  const body=mesh('girl-organic-body'),shorts=mesh('festival-shorts'),rays=[['front',[0,2.56,1.3],[0,2.56,0]],['back',[0,2.56,-1.3],[0,2.56,0]],['left',[-1.3,2.56,0],[0,2.56,0]],['right',[1.3,2.56,0],[0,2.56,0]],['below',[0,1,0],[0,2.56,0]],['below-front',[0,1.2,1.2],[0,2.56,0]]];
  const result=rays.map(([name,a,b])=>{const origin=new T.Vector3(...a),direction=new T.Vector3(...b).sub(origin).normalize(),ray=new T.Raycaster(origin,direction),skin=ray.intersectObject(body)[0],cloth=ray.intersectObject(shorts)[0];return {name,skin:skin?.distance,cloth:cloth?.distance,covered:!!skin&&!!cloth&&cloth.distance<skin.distance-.002};});body.geometry.dispose();shorts.geometry.dispose();return result;
 });
 assert.ok(coverageRays.every(r=>r.covered),JSON.stringify(coverageRays));
 const armorRays=await page.evaluate(async()=>{
  const T=await import('https://cdn.jsdelivr.net/npm/three@0.169.0/+esm'),parts=window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier.parts;
  const make=id=>{const p=parts.find(p=>p.id===id),g=new T.BufferGeometry();g.setAttribute('position',new T.Float32BufferAttribute(p.topologyMesh.positions,3));g.setIndex(p.topologyMesh.indices);const mesh=new T.Mesh(g,new T.MeshBasicMaterial({side:T.DoubleSide}));mesh.position.fromArray(p.position);mesh.rotation.fromArray(p.rotation);mesh.scale.fromArray(p.scale);mesh.updateMatrixWorld(true);return mesh;};
  const body=make('girl-organic-body'),targets=[['right-arm-band',.515,3.22],['left-wrist-cuff',-.875,2.855],['bodice-stitch-2',0,3.645],['right-wrist-0',.6675,3.055],['right-wrist-1',.759,2.9595],['right-wrist-2',.847,2.871],['model-0003',0,3.2],['dark-shoulder',-.16,3.46]],result=[];
  for(const [id,x,y] of targets){const armor=make(id);for(const side of [-1,1]){const ray=new T.Raycaster(new T.Vector3(x,y,side*1.5),new T.Vector3(0,0,-side)),skin=ray.intersectObject(body)[0],cloth=ray.intersectObject(armor)[0];result.push({id,side,skin:skin?.distance,cloth:cloth?.distance,covered:!!skin&&!!cloth&&cloth.distance<skin.distance-.002});}armor.geometry.dispose();}body.geometry.dispose();return result;
 });
 assert.ok(armorRays.every(r=>r.covered),JSON.stringify(armorRays));console.log('DEFAULT_PINATAS_SMOOTH_SKIN_EYE_RISE_AND_OPAQUE_COVERAGE_PASS');
 for(const [mode,view] of [['body','three'],['portrait','front'],['portrait','three'],['legs','front'],['legs','right'],['hands','front'],['all','three']]){
  await page.evaluate(([m,v])=>window.SWYRL_ENGINE_MODEL_ATELIER.frameGirl(m,v),[mode,view]);await page.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));
  const visible=await page.evaluate(()=>window.SWYRL_ENGINE_MODEL_ATELIER.presentation());for(const name of ['Azure frost','Coral flare'])assert.equal(visible.groups[name].visible,28,'View changes must not hide hair companions');
  if(['body','all'].includes(mode))for(const name of ['Azure frost','Coral flare'])assert.equal(visible.groups[name].inView,28);
  if(mode!=='hands'&&mode!=='all')await page.screenshot({path:out+'/'+mode+'-'+view+'.png'});
 }
 const phone=await context.newPage();phone.on('pageerror',e=>errors.push(e.message));await phone.setViewportSize({width:390,height:844});await installSystemCATransport(phone);await phone.goto(base+'/?project=organic-anime-girl',{waitUntil:'domcontentloaded'});await phone.waitForFunction(()=>window.SWYRL_ENGINE_AGENT?.inspectScene().project.modelAtelier?.appearanceRevision==='v11.93'&&window.SWYRL_ENGINE_MODEL_ATELIER.presentation()?.groups['Festival companion']?.visible===0,null,{timeout:180000,polling:500});await phone.evaluate(()=>document.getElementById('seReleaseNotesClose')?.click());
 const phonePresentation=await phone.evaluate(()=>window.SWYRL_ENGINE_MODEL_ATELIER.presentation());for(const name of ['Azure frost','Coral flare']){assert.equal(phonePresentation.groups[name].visible,28);assert.equal(phonePresentation.groups[name].inView,28);}await phone.screenshot({path:out+'/phone-default-pinatas.png'});await phone.close();
 await page.evaluate(()=>{window.requestAnimationFrame=()=>0;});
 const hash=()=>page.evaluate(async()=>{const parts=window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier.parts,bytes=new TextEncoder().encode(JSON.stringify(parts));return Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))).map(v=>v.toString(16).padStart(2,'0')).join('');});
 const initialHash=await hash();
 await page.evaluate(()=>document.getElementById('modelAtelierCourierStudio').click());
 await page.locator('#modelAtelierParts').selectOption('model-0003');
 await page.evaluate(()=>{document.getElementById('modelAtelierAtlasNormal').value='.34';document.getElementById('modelAtelierAtlasApply').click();});
 const edited=await page.evaluate(()=>window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier.parts.find(p=>p.id==='model-0003').textureBinding);
 assert.equal(edited.normalStrength,.34);assert.equal(edited.set,'festival-4k');
 assert.notEqual(await hash(),initialHash,'Material control changes native data');
 await page.evaluate(()=>document.getElementById('modelAtelierUndo').click());
 assert.equal(await hash(),initialHash,'Undo restores exact native geometry and materials');
 console.log('FESTIVAL_MATERIAL_EDIT_UNDO_EXACT_PASS');
 const save=page.waitForEvent('download');await page.evaluate(()=>document.getElementById('modelAtelierExport').click());
 await(await save).saveAs(out+'/festival-girl.model.json');
 const savedInfo=await fs.stat(out+'/festival-girl.model.json');assert.ok(savedInfo.size>1000000&&savedInfo.size<256000000);
 await page.locator('#modelAtelierImportFile').setInputFiles(out+'/festival-girl.model.json');
 await page.waitForFunction(()=>document.getElementById('modelAtelierStatus').textContent.startsWith('Validated model,'),null,{polling:500});
 assert.equal(await hash(),initialHash,'Native save/import retains every refined part exactly');
 console.log('FESTIVAL_NATIVE_SAVE_IMPORT_EXACT_PASS',savedInfo.size);
 const exportGLB=page.waitForEvent('download');await page.evaluate(()=>document.getElementById('modelAtelierExportGLB').click());
 await(await exportGLB).saveAs(out+'/festival-girl.glb');
 const glb=await fs.readFile(out+'/festival-girl.glb');
 assert.equal(glb.readUInt32LE(0),0x46546c67);assert.equal(glb.readUInt32LE(4),2);assert.equal(glb.readUInt32LE(8),glb.length);
 const scene=JSON.parse(glb.subarray(20,20+glb.readUInt32LE(12)).toString());
 assert.ok(scene.meshes.length>100,'Export retains separately editable geometry');
 assert.ok(scene.images.length>=2&&scene.images.every(image=>Number.isInteger(image.bufferView)),'Color and normal images are embedded in textured GLB');
 assert.ok(scene.textures.length>=2);
 const factory=await page.evaluate(async()=>{
  const current=window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier,rebuilt=window.SWYRL_ENGINE_MODEL_ATELIER.createGirlProject().project.modelAtelier;
  const hash=async value=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(JSON.stringify(value))))).map(v=>v.toString(16).padStart(2,'0')).join('');
  return {partsExact:await hash(current.parts)===await hash(rebuilt.parts),groupsExact:await hash(current.meshGroups)===await hash(rebuilt.meshGroups),assembliesExact:await hash(current.assemblies)===await hash(rebuilt.assemblies)};
 });
 assert.deepEqual(factory,{partsExact:true,groupsExact:true,assembliesExact:true},'Current source factory must reproduce the packaged scene');
 console.log('FESTIVAL_CURRENT_FACTORY_MATCHES_PACKAGED_PARTS_GROUPS_ASSEMBLIES_PASS');
 assert.deepEqual(errors,[]);
 const receipt={version:'v11.93',parts:state.status.parts,triangles:state.status.triangles,presentation,phonePresentation,portrait:state.portrait,legs:state.legs,smoothing:state.smoothing,finish:state.finish,coverage:state.coverage,coverageRays,armorRays,nativeFactory:factory,materialEditUndoExact:true,nativeSaveImportExact:true,nativeBytes:savedInfo.size,texturedGLB:{bytes:glb.length,meshes:scene.meshes.length,embeddedImages:scene.images.length},pageErrors:errors};
 await fs.writeFile(out+'/receipt.json',JSON.stringify(receipt,null,2)+'\n');console.log('SMOOTH_ANATOMY_PINATAS_COVERAGE_EDITOR_AND_NATIVE_EXPORT_PASS');
}catch(error){console.error('SMOOTH_PINATAS_TEST_FAILURE',error);throw error;}finally{await browser.close();}
