import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import {installSystemCATransport} from './browser_tls_v11_92.mjs';
const base=process.env.SWYRL_TEST_URL||'http://127.0.0.1:8809',out=process.env.SWYRL_TEST_OUT||'/workspace/.setup/knee-v11-94/test';await fs.mkdir(out,{recursive:true});
const browser=await chromium.launch({headless:true,executablePath:'/usr/bin/chromium',args:['--no-sandbox','--disable-dev-shm-usage','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader']});
try{
 const context=await browser.newContext({viewport:{width:1200,height:1100},acceptDownloads:true});const page=await context.newPage();page.setDefaultTimeout(300000);await installSystemCATransport(page);
 const errors=[];page.on('pageerror',e=>{errors.push(e.message);console.error('PAGE_ERROR',e.message);});page.on('dialog',d=>d.accept());
 await page.goto(base+'/?project=organic-anime-girl',{waitUntil:'domcontentloaded'});
 await page.waitForFunction(()=>window.SWYRL_ENGINE_AGENT?.inspectScene().project.modelAtelier?.appearanceRevision==='v11.94'&&window.SWYRL_ENGINE_MODEL_ATELIER.presentation()?.groups['Festival companion']?.visible===0,null,{timeout:180000,polling:500});
 await page.evaluate(()=>{document.getElementById('seReleaseNotesClose')?.click();window.requestAnimationFrame=cb=>setTimeout(()=>cb(performance.now()),250);});
 const presentation=await page.evaluate(()=>window.SWYRL_ENGINE_MODEL_ATELIER.presentation());
 for(const name of ['Azure frost','Coral flare']){assert.equal(presentation.groups[name].visible,28,'Default view must show the actual hair piñatas');assert.equal(presentation.groups[name].inView,28,'Default camera must fit them');}
 await page.screenshot({path:out+'/default-pinatas.png'});
 const state=await page.evaluate(()=>{const m=window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier;return {status:window.SWYRL_ENGINE_MODEL_ATELIER.animalStatus(),portrait:m.portraitRefinement,legs:m.legRefinement,smoothing:m.anatomySmoothing,finish:m.festivalFinish,coverage:m.coverageRefinement,kneeSkirt:m.kneeSkirtRefinement,headRefinement:m.portraitRefinementV1194};});
 assert.equal(state.status.valid,true);
 for(const side of ['left','right']){const eye=state.portrait.eyeCorners[side];assert.ok(eye.outer[1]-eye.inner[1]>.04);}
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
 assert.ok(armorRays.every(r=>r.covered),JSON.stringify(armorRays));console.log('DEFAULT_PINATAS_AND_OPAQUE_COVERAGE_PASS');

 // Test the outer armor pieces independently from the opaque shorts. Every
 // azimuth must meet an actual panel at each of three thigh/hip heights.
 const skirtGeometry=await page.evaluate(async()=>{
  const T=await import('https://cdn.jsdelivr.net/npm/three@0.169.0/+esm'),parts=window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier.parts;
  const make=p=>{const g=new T.BufferGeometry();g.setAttribute('position',new T.Float32BufferAttribute(p.topologyMesh.positions,3));g.setIndex(p.topologyMesh.indices);const n=new T.Mesh(g,new T.MeshBasicMaterial({side:T.DoubleSide}));n.position.fromArray(p.position);n.rotation.fromArray(p.rotation);n.scale.fromArray(p.scale);n.updateMatrixWorld(true);return n;};
  const panels=parts.filter(p=>/^skirt-(?:panel-|side-)/.test(p.id)).map(make),skin=make(parts.find(p=>p.id==='girl-organic-body')),rays=[];
  for(const y of [2.5,2.25,2.0])for(let azimuth=0;azimuth<72;azimuth++){
   const angle=azimuth/72*Math.PI*2,origin=new T.Vector3(Math.sin(angle)*1.4,y,Math.cos(angle)*1.4),ray=new T.Raycaster(origin,new T.Vector3(-Math.sin(angle),0,-Math.cos(angle)),0,1.4),hit=ray.intersectObjects(panels)[0],skinHit=ray.intersectObject(skin)[0];
   rays.push({y,azimuthDegrees:azimuth*5,covered:!!hit&&(!skinHit||hit.distance<skinHit.distance-.002),distance:hit?.distance,skinDistance:skinHit?.distance,clearance:hit&&skinHit?skinHit.distance-hit.distance:null});
  }
  const affected=new Set(window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier.kneeSkirtRefinement.affectedParts),lowerParts=parts.filter(p=>affected.has(p.id)||/^skirt-|^girl-dress-|^light(?:-cord)?-/.test(p.id)),bounds=lowerParts.map(p=>{const n=make(p),v=new T.Vector3(),a=n.geometry.attributes.position;let minY=Infinity,maxY=-Infinity;for(let i=0;i<a.count;i++){v.fromBufferAttribute(a,i).applyMatrix4(n.matrixWorld);minY=Math.min(minY,v.y);maxY=Math.max(maxY,v.y);}n.geometry.dispose();n.material.dispose();return {id:p.id,minY,maxY};});
  for(const n of [...panels,skin]){n.geometry.dispose();n.material.dispose();}
  return {panelCount:panels.length,rays,bounds};
 });
 assert.equal(skirtGeometry.panelCount,9,'Use all seven lower armor panels and both side pieces');
 assert.equal(skirtGeometry.rays.length,216);
 assert.ok(skirtGeometry.rays.every(r=>r.covered),'Skirt gaps: '+JSON.stringify(skirtGeometry.rays.filter(r=>!r.covered)));
 assert.ok(skirtGeometry.bounds.every(b=>b.minY>=1.52-0.00001),'Below kneecaps: '+JSON.stringify(skirtGeometry.bounds.filter(b=>b.minY<1.52-0.00001)));
 console.log('FULL_SKIRT_360_DEGREES_AND_KNEE_HEM_PASS');
 const portraitGeometry=await page.evaluate(async()=>{
  const current=window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier,prior=(await(await fetch('scenes/model-atelier-smooth-girl-v11-93.swyrl.json')).json()).project.modelAtelier;
  const skin=current.parts.find(p=>p.id==='girl-organic-body').topologyMesh,old=prior.parts.find(p=>p.id==='girl-organic-body').topologyMesh;
  let width=0,oldWidth=0,bridge=-Infinity,oldBridge=-Infinity,tip=-Infinity,oldTip=-Infinity,changedHeadVertices=0;
  for(let i=0;i<old.positions.length;i+=3){const [x,y,z]=old.positions.slice(i,i+3),nx=skin.positions[i],nz=skin.positions[i+2];if(y>3.85&&y<4.25&&z>.10&&Math.abs(x)<.25){width=Math.max(width,Math.abs(nx));oldWidth=Math.max(oldWidth,Math.abs(x));}if(y>4.03&&y<4.10&&Math.abs(x)<.035&&z>.25){bridge=Math.max(bridge,nz);oldBridge=Math.max(oldBridge,z);}if(y>3.97&&y<4.03&&Math.abs(x)<.04&&z>.25){tip=Math.max(tip,nz);oldTip=Math.max(oldTip,z);}if(y>3.7&&(x!==nx||z!==nz))changedHeadVertices++;}
  const priorParts=new Map(prior.parts.map(p=>[p.id,p]));let preservedTopology=true;
  for(const p of current.parts){const old=priorParts.get(p.id);if(!old||JSON.stringify(p.topologyMesh.indices)!==JSON.stringify(old.topologyMesh.indices)||JSON.stringify(p.topologyMesh.uvs)!==JSON.stringify(old.topologyMesh.uvs))preservedTopology=false;}
  return {width,oldWidth,widthRatio:width/oldWidth,bridge,oldBridge,tip,oldTip,changedHeadVertices,preservedTopology};
 });
 assert.ok(portraitGeometry.widthRatio<.99&&portraitGeometry.widthRatio>.90,'Head should be subtly narrower: '+JSON.stringify(portraitGeometry));
 assert.ok(portraitGeometry.changedHeadVertices>1000,'Head contour must change on actual native skin');
 assert.ok(portraitGeometry.bridge<portraitGeometry.oldBridge-.003,'Nasal bridge relief must be softened on actual skin: '+JSON.stringify(portraitGeometry));
 assert.ok(portraitGeometry.tip<portraitGeometry.oldTip-.028,'Nasal tip relief must be softened on actual skin: '+JSON.stringify(portraitGeometry));
 assert.equal(state.headRefinement.nose.tipFairingPasses,4);
 assert.equal(state.headRefinement.version,'v11.94');
 assert.equal(state.kneeSkirt.revision,'v11.94');
 assert.equal(portraitGeometry.preservedTopology,true,'Refinement retains each original UV and index array');
 console.log('NARROWER_HEAD_AND_NATIVE_TOPOLOGY_PASS',JSON.stringify(portraitGeometry));

 for(const [mode,view] of [['body','front'],['body','back'],['body','left'],['body','right'],['body','three'],['portrait','front'],['portrait','right'],['portrait','three'],['all','three']]){
  await page.evaluate(([m,v])=>window.SWYRL_ENGINE_MODEL_ATELIER.frameGirl(m,v),[mode,view]);await page.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));
  const visible=await page.evaluate(()=>window.SWYRL_ENGINE_MODEL_ATELIER.presentation());for(const name of ['Azure frost','Coral flare'])assert.equal(visible.groups[name].visible,28,'View changes must not hide hair companions');
  if(['body','all'].includes(mode))for(const name of ['Azure frost','Coral flare'])assert.equal(visible.groups[name].inView,28);
  if(mode!=='hands'&&mode!=='all')await page.screenshot({path:out+'/'+mode+'-'+view+'.png'});
 }
 const phone=await context.newPage();phone.on('pageerror',e=>errors.push(e.message));await phone.setViewportSize({width:390,height:844});await installSystemCATransport(phone);await phone.goto(base+'/?project=organic-anime-girl',{waitUntil:'domcontentloaded'});await phone.waitForFunction(()=>window.SWYRL_ENGINE_AGENT?.inspectScene().project.modelAtelier?.appearanceRevision==='v11.94'&&window.SWYRL_ENGINE_MODEL_ATELIER.presentation()?.groups['Festival companion']?.visible===0,null,{timeout:180000,polling:500});await phone.evaluate(()=>document.getElementById('seReleaseNotesClose')?.click());
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
 const receipt={version:'v11.94',parts:state.status.parts,triangles:state.status.triangles,presentation,phonePresentation,portrait:state.portrait,legs:state.legs,smoothing:state.smoothing,finish:state.finish,coverage:state.coverage,coverageRays,armorRays,skirtGeometry,portraitGeometry,kneeSkirt:state.kneeSkirt,headRefinement:state.headRefinement,nativeFactory:factory,materialEditUndoExact:true,nativeSaveImportExact:true,nativeBytes:savedInfo.size,texturedGLB:{bytes:glb.length,meshes:scene.meshes.length,embeddedImages:scene.images.length},pageErrors:errors};
 await fs.writeFile(out+'/receipt.json',JSON.stringify(receipt,null,2)+'\n');console.log('KNEE_SKIRT_SOFT_NOSE_EDITOR_AND_NATIVE_EXPORT_PASS');
}catch(error){console.error('KNEE_SKIRT_TEST_FAILURE',error);throw error;}finally{await browser.close();}
