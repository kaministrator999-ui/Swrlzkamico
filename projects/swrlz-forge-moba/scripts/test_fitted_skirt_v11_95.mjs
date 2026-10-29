import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import {installSystemCATransport} from './browser_tls_v11_92.mjs';
const base=process.env.SWYRL_TEST_URL||'http://127.0.0.1:8809',out=process.env.SWYRL_TEST_OUT||'/workspace/.setup/fitted-v11-95/test';await fs.mkdir(out,{recursive:true});
const browser=await chromium.launch({headless:true,executablePath:'/usr/bin/chromium',args:['--no-sandbox','--disable-dev-shm-usage','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader']});
try{
 const context=await browser.newContext({viewport:{width:1200,height:1100},acceptDownloads:true});const page=await context.newPage();page.setDefaultTimeout(300000);await installSystemCATransport(page);
 const errors=[];page.on('pageerror',e=>{errors.push(e.message);console.error('PAGE_ERROR',e.message);});page.on('dialog',d=>d.accept());
 await page.goto(base+'/?project=organic-anime-girl',{waitUntil:'domcontentloaded'});
 await page.waitForFunction(()=>window.SWYRL_ENGINE_AGENT?.inspectScene().project.modelAtelier?.appearanceRevision==='v11.95'&&window.SWYRL_ENGINE_MODEL_ATELIER.presentation()?.groups['Festival companion']?.visible===0,null,{timeout:180000,polling:500});
 await page.evaluate(()=>{document.getElementById('seReleaseNotesClose')?.click();window.requestAnimationFrame=cb=>setTimeout(()=>cb(performance.now()),250);});
 const presentation=await page.evaluate(()=>window.SWYRL_ENGINE_MODEL_ATELIER.presentation());
 for(const name of ['Azure frost','Coral flare']){assert.equal(presentation.groups[name].visible,28,'Default view must show the actual hair piñatas');assert.equal(presentation.groups[name].inView,28,'Default camera must fit them');}
 await page.screenshot({path:out+'/default-pinatas.png'});
 const state=await page.evaluate(()=>{const m=window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier;return {status:window.SWYRL_ENGINE_MODEL_ATELIER.animalStatus(),portrait:m.portraitRefinement,legs:m.legRefinement,smoothing:m.anatomySmoothing,finish:m.festivalFinish,coverage:m.coverageRefinement,kneeSkirt:m.kneeSkirtRefinement,skirtFit:m.skirtFitV1195};});
 assert.equal(state.status.valid,true);
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
 console.log('DEFAULT_PINATAS_AND_OPAQUE_COVERAGE_PASS');

 // Test the outer armor pieces independently from the opaque shorts. Every
 // azimuth must meet an actual panel at each thigh/hip height and at the fitted upper waist.
 const skirtGeometry=await page.evaluate(async()=>{
  const T=await import('https://cdn.jsdelivr.net/npm/three@0.169.0/+esm'),parts=window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier.parts;
  const make=p=>{const g=new T.BufferGeometry();g.setAttribute('position',new T.Float32BufferAttribute(p.topologyMesh.positions,3));g.setIndex(p.topologyMesh.indices);const n=new T.Mesh(g,new T.MeshBasicMaterial({side:T.DoubleSide}));n.position.fromArray(p.position);n.rotation.fromArray(p.rotation);n.scale.fromArray(p.scale);n.updateMatrixWorld(true);return n;};
  const panels=parts.filter(p=>/^skirt-(?:panel-|side-)/.test(p.id)).map(make),skin=make(parts.find(p=>p.id==='girl-organic-body')),rays=[];
  for(const y of [2.0,2.25,2.5,2.65,2.7,2.75,2.79,2.8,2.85,2.9])for(let azimuth=0;azimuth<72;azimuth++){
   const angle=azimuth/72*Math.PI*2,origin=new T.Vector3(Math.sin(angle)*1.4,y,Math.cos(angle)*1.4),ray=new T.Raycaster(origin,new T.Vector3(-Math.sin(angle),0,-Math.cos(angle)),0,1.4),hit=ray.intersectObjects(panels)[0],skinHit=ray.intersectObject(skin).find(h=>Math.abs(h.point.x)<.62&&Math.abs(h.point.z)<.42);
   rays.push({y,azimuthDegrees:azimuth*5,covered:!!hit&&(!skinHit||hit.distance<skinHit.distance-.002),distance:hit?.distance,skinDistance:skinHit?.distance,clearance:hit&&skinHit?skinHit.distance-hit.distance:null});
  }
  const affected=new Set(window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier.kneeSkirtRefinement.affectedParts),lowerParts=parts.filter(p=>affected.has(p.id)||/^skirt-|^girl-dress-|^light(?:-cord)?-/.test(p.id)),bounds=lowerParts.map(p=>{const n=make(p),v=new T.Vector3(),a=n.geometry.attributes.position;let minY=Infinity,maxY=-Infinity;for(let i=0;i<a.count;i++){v.fromBufferAttribute(a,i).applyMatrix4(n.matrixWorld);minY=Math.min(minY,v.y);maxY=Math.max(maxY,v.y);}n.geometry.dispose();n.material.dispose();return {id:p.id,minY,maxY};});
  for(const n of [...panels,skin]){n.geometry.dispose();n.material.dispose();}
  return {panelCount:panels.length,rays,bounds};
 });
 assert.equal(skirtGeometry.panelCount,9,'Use all seven lower armor panels and both side pieces');
 assert.equal(skirtGeometry.rays.length,720);
 assert.ok(skirtGeometry.rays.every(r=>r.covered),'Skirt gaps: '+JSON.stringify(skirtGeometry.rays.filter(r=>!r.covered)));
 assert.ok(skirtGeometry.bounds.every(b=>b.minY>=1.52-0.00001),'Below kneecaps: '+JSON.stringify(skirtGeometry.bounds.filter(b=>b.minY<1.52-0.00001)));
 console.log('FULL_SKIRT_360_DEGREES_AND_KNEE_HEM_PASS');
 const fittedGeometry=await page.evaluate(async()=>{
  const T=await import('https://cdn.jsdelivr.net/npm/three@0.169.0/+esm'),current=window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier,prior=(await(await fetch('scenes/model-atelier-knee-armor-v11-94.swyrl.json')).json()).project.modelAtelier;
  const affected=new Set(current.skirtFitV1195.affectedParts),anchor=current.skirtFitV1195.anchorY,oldById=new Map(prior.parts.map(p=>[p.id,p]));
  let unchangedPartsExact=true,topologyExact=true,transformsExact=true,worldHeightPreserved=true,identityLocalYExact=true,maxWorldHeightDelta=0,hemExact=true,hemVertices=0,changedVertices=0;
  for(const p of current.parts){
   const old=oldById.get(p.id);if(!old){unchangedPartsExact=false;continue;}
   if(!affected.has(p.id)&&JSON.stringify(p)!==JSON.stringify(old))unchangedPartsExact=false;
   const a=p.topologyMesh,b=old.topologyMesh;
   if(['position','rotation','scale'].some(key=>JSON.stringify(p[key])!==JSON.stringify(old[key])))transformsExact=false;
   if(JSON.stringify(a.indices)!==JSON.stringify(b.indices)||JSON.stringify(a.uvs)!==JSON.stringify(b.uvs))topologyExact=false;
   if(!affected.has(p.id))continue;
   const matrix=new T.Matrix4().compose(new T.Vector3(...p.position),new T.Quaternion().setFromEuler(new T.Euler(...p.rotation)),new T.Vector3(...p.scale)),oldMatrix=new T.Matrix4().compose(new T.Vector3(...old.position),new T.Quaternion().setFromEuler(new T.Euler(...old.rotation)),new T.Vector3(...old.scale)),identity=p.position.every(v=>v===0)&&p.rotation.every(v=>v===0)&&p.scale.every(v=>v===1),before=new T.Vector3(),after=new T.Vector3();
   for(let i=0;i<a.positions.length;i+=3){
    before.fromArray(b.positions,i).applyMatrix4(oldMatrix);after.fromArray(a.positions,i).applyMatrix4(matrix);
    const deltaY=Math.abs(before.y-after.y);maxWorldHeightDelta=Math.max(maxWorldHeightDelta,deltaY);if(deltaY>2e-6)worldHeightPreserved=false;
    if(identity&&a.positions[i+1]!==b.positions[i+1])identityLocalYExact=false;
    if(before.y<=anchor){hemVertices++;if(a.positions[i]!==b.positions[i]||a.positions[i+1]!==b.positions[i+1]||a.positions[i+2]!==b.positions[i+2]||before.distanceTo(after)>2e-6)hemExact=false;}
    if(a.positions[i]!==b.positions[i]||a.positions[i+1]!==b.positions[i+1]||a.positions[i+2]!==b.positions[i+2])changedVertices++;
   }
  }
  // Intersect the actual triangles with each horizontal plane. Loose vertex
  // bands would overestimate flare and could hide an unchanged waist silhouette.
  const section=(model,y)=>{
   let minX=Infinity,maxX=-Infinity,minZ=Infinity,maxZ=-Infinity,points=0;
   for(const p of model.parts.filter(p=>/^skirt-(?:panel-|side-)/.test(p.id))){
    const a=p.topologyMesh,matrix=new T.Matrix4().compose(new T.Vector3(...p.position),new T.Quaternion().setFromEuler(new T.Euler(...p.rotation)),new T.Vector3(...p.scale));
    for(let i=0;i<a.indices.length;i+=3){const vertices=a.indices.slice(i,i+3).map(n=>new T.Vector3().fromArray(a.positions,n*3).applyMatrix4(matrix));for(let e=0;e<3;e++){const from=vertices[e],to=vertices[(e+1)%3];if((from.y-y)*(to.y-y)>0||Math.abs(to.y-from.y)<1e-10)continue;const t=(y-from.y)/(to.y-from.y);if(t<0||t>1)continue;const x=from.x+(to.x-from.x)*t,z=from.z+(to.z-from.z)*t;minX=Math.min(minX,x);maxX=Math.max(maxX,x);minZ=Math.min(minZ,z);maxZ=Math.max(maxZ,z);points++;}}
   }
   return {y,minX,maxX,minZ,maxZ,width:maxX-minX,depth:maxZ-minZ,points};
  };
  const sections=[2.65,2.8,2.9].map(y=>{const now=section(current,y),old=section(prior,y);return {y,current:now,previous:old,widthRatio:now.width/old.width,depthRatio:now.depth/old.depth};});
  return {anchorY:anchor,unchangedPartsExact,topologyExact,transformsExact,worldHeightPreserved,identityLocalYExact,maxWorldHeightDelta,hemExact,hemVertices,changedVertices,sections};
 });
 assert.equal(state.skirtFit.version,'v11.95');
 assert.equal(fittedGeometry.unchangedPartsExact,true,'Body, face, piñatas, shorts and every unaffected part stay exact');
 assert.equal(fittedGeometry.topologyExact,true,'Every native UV and index array stays exact');
 assert.equal(fittedGeometry.transformsExact,true,'Native part transforms stay exact');
 assert.equal(fittedGeometry.worldHeightPreserved,true,'Every fitted world-space height stays within 0.000002 units');
 assert.equal(fittedGeometry.identityLocalYExact,true,'Identity-transform panels keep their exact authored local Y');
 assert.equal(fittedGeometry.hemExact,true,'Lower skirt and hem vertices stay exact');
 assert.ok(fittedGeometry.hemVertices>10000&&fittedGeometry.changedVertices>1000,'Fit changes the upper skirt and preserves a substantial lower region');
 for(const section of fittedGeometry.sections){assert.ok(section.current.points>100&&section.previous.points>100);assert.ok(section.widthRatio<=(section.y===2.65 ? .852 : .82),'Upper skirt width must visibly narrow: '+JSON.stringify(section));assert.ok(section.depthRatio<=(section.y===2.65 ? .87 : .83),'Upper skirt depth must visibly narrow: '+JSON.stringify(section));}
 console.log('UPPER_SKIRT_FIT_AND_PRESERVED_MODEL_PASS',JSON.stringify(fittedGeometry));

 for(const [mode,view] of [['body','front'],['body','three'],['legs','front'],['legs','three']]){
  await page.evaluate(([m,v])=>window.SWYRL_ENGINE_MODEL_ATELIER.frameGirl(m,v),[mode,view]);await page.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));
  const visible=await page.evaluate(()=>window.SWYRL_ENGINE_MODEL_ATELIER.presentation());for(const name of ['Azure frost','Coral flare'])assert.equal(visible.groups[name].visible,28,'View changes must not hide hair companions');
  if(['body','all'].includes(mode))for(const name of ['Azure frost','Coral flare'])assert.equal(visible.groups[name].inView,28);
  await page.screenshot({path:out+'/'+(mode==='legs'?'waist-skirt':mode)+'-'+view+'.png'});
 }
 const phone=await context.newPage();phone.on('pageerror',e=>errors.push(e.message));await phone.setViewportSize({width:390,height:844});await installSystemCATransport(phone);await phone.goto(base+'/?project=organic-anime-girl',{waitUntil:'domcontentloaded'});await phone.waitForFunction(()=>window.SWYRL_ENGINE_AGENT?.inspectScene().project.modelAtelier?.appearanceRevision==='v11.95'&&window.SWYRL_ENGINE_MODEL_ATELIER.presentation()?.groups['Festival companion']?.visible===0,null,{timeout:180000,polling:500});await phone.evaluate(()=>document.getElementById('seReleaseNotesClose')?.click());
 const phonePresentation=await phone.evaluate(()=>window.SWYRL_ENGINE_MODEL_ATELIER.presentation());for(const name of ['Azure frost','Coral flare']){assert.equal(phonePresentation.groups[name].visible,28);assert.equal(phonePresentation.groups[name].inView,28);}await phone.screenshot({path:out+'/phone-default-pinatas.png'});for(const view of ['front','three']){await phone.evaluate(v=>window.SWYRL_ENGINE_MODEL_ATELIER.frameGirl('body',v),view);await phone.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));await phone.screenshot({path:out+'/phone-body-'+view+'.png'});}await phone.close();
 await page.evaluate(()=>{window.requestAnimationFrame=()=>0;});
 const hash=()=>page.evaluate(async()=>{const parts=window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier.parts,bytes=new TextEncoder().encode(JSON.stringify(parts));return Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))).map(v=>v.toString(16).padStart(2,'0')).join('');});
 const initialHash=await hash();
 await page.evaluate(()=>document.getElementById('modelAtelierCourierStudio').click());
 await page.locator('#modelAtelierParts').selectOption('skirt-panel-0');
 await page.evaluate(()=>{document.getElementById('modelAtelierAtlasNormal').value='.34';document.getElementById('modelAtelierAtlasApply').click();});
 const edited=await page.evaluate(()=>window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier.parts.find(p=>p.id==='skirt-panel-0').textureBinding);
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
 const receipt={version:'v11.95',parts:state.status.parts,triangles:state.status.triangles,presentation,phonePresentation,portrait:state.portrait,legs:state.legs,smoothing:state.smoothing,finish:state.finish,coverage:state.coverage,coverageRays,skirtGeometry,fittedGeometry,kneeSkirt:state.kneeSkirt,skirtFit:state.skirtFit,nativeFactory:factory,materialEditUndoExact:true,nativeSaveImportExact:true,nativeBytes:savedInfo.size,texturedGLB:{bytes:glb.length,meshes:scene.meshes.length,embeddedImages:scene.images.length},pageErrors:errors};
 await fs.writeFile(out+'/receipt.json',JSON.stringify(receipt,null,2)+'\n');console.log('FITTED_SKIRT_EDITOR_AND_NATIVE_EXPORT_PASS');
}catch(error){console.error('FITTED_SKIRT_TEST_FAILURE',error);throw error;}finally{await browser.close();}
