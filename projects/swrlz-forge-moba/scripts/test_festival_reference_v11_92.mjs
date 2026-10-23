import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import {gunzipSync} from 'node:zlib';
import {installSystemCATransport} from './browser_tls_v11_92.mjs';

const base=process.env.SWYRL_TEST_URL||'http://127.0.0.1:8809';
const out=process.env.SWYRL_TEST_OUT||'/workspace/.setup/festival-v11-92/test';
await fs.mkdir(out,{recursive:true});
const payload=new URL('../payload/festival-girl/',import.meta.url);
const chunks=(await fs.readdir(payload)).filter(name=>name.startsWith('organic-v11-91.swyrl.json.gz.part')).sort();
assert.ok(chunks.length>0,'Previous starter is required for a real geometry comparison');
const previous=JSON.parse(gunzipSync(Buffer.concat(await Promise.all(chunks.map(name=>fs.readFile(new URL(name,payload)))))));
const oldParts=previous.project.modelAtelier.parts;
const axisBounds=(part,axis)=>{const a=part.topologyMesh.positions;let min=Infinity,max=-Infinity;for(let i=axis;i<a.length;i+=3){min=Math.min(min,a[i]);max=Math.max(max,a[i]);}return [min,max];};
const oldGoldHem=axisBounds(oldParts.find(part=>part.id==='skirt-panel-1'),1)[0];
const browser=await chromium.launch({headless:true,executablePath:'/usr/bin/chromium',args:['--no-sandbox','--disable-dev-shm-usage','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader']});
try{
 const context=await browser.newContext({viewport:{width:1200,height:1100},acceptDownloads:true});
 const page=await context.newPage();page.setDefaultTimeout(240000);
 await installSystemCATransport(page);
 const errors=[];page.on('pageerror',error=>{errors.push(error.message);console.error('FESTIVAL_PAGE_ERROR',error.message);});
 page.on('dialog',dialog=>dialog.accept());
 await page.goto(base+'/?project=organic-anime-girl',{waitUntil:'domcontentloaded'});
 await page.waitForFunction(()=>window.SWYRL_ENGINE_MODEL_ATELIER?.animalStatus()?.species==='anime',null,{timeout:150000,polling:500});
 await page.evaluate(()=>{document.getElementById('seReleaseNotesClose')?.click();window.requestAnimationFrame=callback=>setTimeout(()=>callback(performance.now()),250);});
 const state=await page.evaluate(()=>{
  const model=window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier,part=id=>model.parts.find(p=>p.id===id);
  const bounds=p=>{const a=p.topologyMesh.positions;const lo=[Infinity,Infinity,Infinity],hi=[-Infinity,-Infinity,-Infinity];for(let i=0;i<a.length;i++) {const axis=i%3;lo[axis]=Math.min(lo[axis],a[i]);hi[axis]=Math.max(hi[axis],a[i]);}return {min:lo,max:hi};};
  const eyes=['left','right'].map(side=>({side,sclera:bounds(part(side+'-sclera')),brow:bounds(part(side+'-brow')),upper:bounds(part(side+'-upper-lid')),iris:!!part(side+'-iris'),pupil:!!part('girl-pupil-'+side)}));
  return {status:window.SWYRL_ENGINE_MODEL_ATELIER.animalStatus(),profile:model.referenceProfile,dress:model.festivalDress,eyes,gold:bounds(part('skirt-panel-1')),cyan:bounds(part('skirt-panel-3')),teal:bounds(part('skirt-panel-0')),tendril:bounds(part('girl-reference-cyan-tendril')),ponytailTop:Math.max(...model.parts.filter(p=>p.id.startsWith('girl-reference-ponytail-')).map(p=>bounds(p).max[1])),newHair:model.parts.filter(p=>p.id.startsWith('girl-reference-')).length,bodyVertices:part('girl-organic-body').topologyMesh.positions.length/3,partIds:model.parts.map(p=>p.id)};
 });
 assert.equal(state.status.valid,true,'Native model validation');
 assert.equal(state.profile.version,'v11.92');
 assert.equal(state.profile.face.eyeShape,'upturned almond');
 assert.equal(state.profile.face.chin,'small rounded taper');
 assert.match(state.profile.hair.silhouette,/short bob/);
 assert.ok(state.ponytailTop>4.8,'Upward tied hair tufts are real visible geometry');
 assert.ok(state.newHair>=24,'Layered locks must be actual native parts');
 assert.ok(state.tendril.min[1]<3.85&&state.tendril.max[1]>4.2,'Cyan lock must reach past the cheek');
 assert.equal(state.bodyVertices,oldParts.find(p=>p.id==='girl-organic-body').topologyMesh.positions.length/3,'Refinement preserves the continuous body vertex topology');
 for(const eye of state.eyes){
  assert.ok(eye.iris&&eye.pupil,'Separate amber iris and pupil retained');
  const width=eye.sclera.max[0]-eye.sclera.min[0],height=eye.sclera.max[1]-eye.sclera.min[1];
  assert.ok(width>height*1.35&&width>.17,'Eyes must have a visible almond silhouette');
  assert.ok(eye.brow.min[1]>4.13,'Lifted brow stays above eye');
  assert.ok(eye.brow.max[0]-eye.brow.min[0]>.13,'Brows are shaped geometry');
 }
 assert.ok(state.gold.min[1]<oldGoldHem-.5&&state.gold.min[1]<1.6,'Gold tail must visibly lengthen toward the knee');
 assert.ok(state.cyan.min[1]<1.8&&state.teal.min[1]<1.95,'Front and teal outer dress layers must lengthen too');
 assert.equal(state.dress.pastelBaubles,15);
 assert.ok(state.dress.detailParts.includes('girl-dress-inset-pleat-seams'));
 assert.ok(state.partIds.includes('girl-dress-brocade-diamonds'));
 console.log('FESTIVAL_FACE_HAIR_AND_LONGER_DRESS_NATIVE_GEOMETRY_PASS');
 await page.waitForFunction(()=>{const meshes=window.SWYRL_ENGINE_MODEL_ATELIER.animalStatus().meshes,body=meshes.find(mesh=>mesh.id==='girl-organic-body');return body?.baseColorSize[0]===4096&&body?.normalSize[0]===4096;},null,{polling:500,timeout:60000});
 for(const [mode,view] of [['body','front'],['body','three'],['portrait','front'],['portrait','three']]){
  assert.equal(await page.evaluate(([mode,view])=>window.SWYRL_ENGINE_MODEL_ATELIER.frameGirl(mode,view),[mode,view]),true);
  await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
  await page.screenshot({path:out+'/'+mode+'-'+view+'.png'});
 }
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
 const receipt={version:'v11.92',nativeFactory:factory,geometryVerified:true,profile:state.profile,dress:state.dress,eyes:state.eyes,oldGoldHem,newGoldHem:state.gold.min[1],parts:state.status.parts,triangles:state.status.triangles,materialEditUndoExact:true,nativeSaveImportExact:true,nativeBytes:savedInfo.size,texturedGLB:{bytes:glb.length,meshes:scene.meshes.length,embeddedImages:scene.images.length},screenshots:['body-front.png','body-three.png','portrait-front.png','portrait-three.png'],pageErrors:errors};
 await fs.writeFile(out+'/receipt.json',JSON.stringify(receipt,null,2)+'\n');
 console.log('FESTIVAL_REFERENCE_EDITOR_SAVE_UNDO_IMPORT_TEXTURED_GLB_PASS');
}catch(error){console.error('FESTIVAL_REFERENCE_TEST_FAILURE',error);throw error;}finally{await browser.close();}
