import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import * as THREE from 'three';
const root=new URL('../',import.meta.url),read=p=>fs.readFileSync(new URL(p,root),'utf8');
const html=fs.readFileSync(process.env.SWYRL_PORTRAIT_HTML||'dist/swrlz-forge-moba/index.html','utf8');
const model=JSON.parse(read('scenes/model-atelier-festival-polish-v11-19.swyrl.json')).project.modelAtelier;
const previous=JSON.parse(read('scenes/model-atelier-festival-reference-v11-18.swyrl.json')).project.modelAtelier;
const reference=read('runtime/model_atelier_reference_v11_13.js'),leaf=reference.slice(reference.indexOf('function atelierReferenceLeaf('),reference.indexOf('function atelierValidateAssemblies('));
const ctx=vm.createContext({THREE,console,model:()=>model,atelierSculptApply:(geometry,part)=>{assert.ok(!part?.sculptBrushes?.length&&!part?.sculptVertexEdits?.length,'Historical anatomy fixture must have no native sculpt edits');return geometry;}});
vm.runInContext(read('runtime/model_atelier_density_v11_16.js')+'\n'+leaf+'\n'+html.slice(html.indexOf('// Native HD finishes:'),html.indexOf('// §E v11.52: camera-plane-exact pixel brush sizing',html.indexOf('// Native HD finishes:'))),ctx);
const byId=id=>model.parts.find(p=>p.id===id),head=byId('model-0001'),g=ctx.atelierHDGeometry(head),base=ctx.atelierHDGeometry({...head,portraitFinish:undefined});
for(const key of ['position','normal','color'])for(const v of g.attributes[key].array)assert.ok(Number.isFinite(v),'Non-finite portrait '+key);
g.computeBoundingBox();base.computeBoundingBox();
assert.ok(g.boundingBox.min.y-base.boundingBox.min.y>.14,'Lower face must actually become shorter');
assert.equal(g.boundingBox.max.y,base.boundingBox.max.y,'Crown attachment must not move');
assert.equal(g.index.count,base.index.count,'Portrait sampling controls must remain authoritative');
let nose=0;for(let i=0;i<g.attributes.position.count;i++)nose=Math.max(nose,g.attributes.position.getZ(i)-base.attributes.position.getZ(i));
assert.ok(nose>.015&&nose<.06,'Nose tip must have restrained real relief');
assert.notDeepEqual(Array.from(g.attributes.color.array),Array.from(base.attributes.color.array),'Skin warmth must change saved vertex colors');
const old=vm.createContext({THREE,console});vm.runInContext(read('runtime/model_atelier_density_v11_16.js')+'\n'+read('runtime/model_atelier_hd_v11_17.js'),old);
const historical=old.atelierHDSphere({...head,portraitFinish:undefined});
for(const key of ['position','normal','color'])assert.deepEqual(Array.from(base.attributes[key].array),Array.from(historical.attributes[key].array),'Unannotated historical head changed');
console.log('PORTRAIT_SHORTER_CHIN_NOSE_RELIEF_WARMTH_AND_HISTORICAL_DEFAULT_PASS');
const material=new THREE.MeshBasicMaterial({side:THREE.DoubleSide}),mesh=new THREE.Mesh(g,material);mesh.position.fromArray(head.position);mesh.scale.fromArray(head.scale);mesh.rotation.set(...head.rotation);mesh.updateMatrixWorld(true);
const ray=new THREE.Raycaster();
for(const id of ['smile','lower-lip','left-brow','right-brow',model.parts.find(p=>p.name.startsWith('Mouth opening')).id,model.parts.find(p=>p.name.startsWith('Upper teeth')).id]){
 const p=byId(id);assert.equal(p.path.length,33);
 let maxGap=0;for(const q of p.path){const world=new THREE.Vector3(...q).multiply(new THREE.Vector3(...p.scale)).applyEuler(new THREE.Euler(...p.rotation)).add(new THREE.Vector3(...p.position));ray.set(new THREE.Vector3(world.x,world.y,2),new THREE.Vector3(0,0,-1));const hit=ray.intersectObject(mesh,false)[0];assert.ok(hit,'Fitted facial contour is outside the real head');const gap=world.z-hit.point.z;assert.ok(gap>=-1e-6&&gap<(p.name.startsWith('Upper teeth')?.006:.002),'Facial contour floats above or sinks through the head');maxGap=Math.max(maxGap,gap);}
 const curve=ctx.atelierHDGeometry(p);for(const key of ['position','normal'])for(const n of curve.attributes[key].array)assert.ok(Number.isFinite(n));
 console.log('PORTRAIT_ACTUAL_HEAD_CONTOUR_CONTACT_PASS',id,maxGap);
}
assert.equal(ctx.atelierPortraitFit({...byId('smile'),path:[[99,99,0],[100,100,0]]},head,.001),null,'Outside-face fit must reject atomically');
assert.equal(ctx.atelierPortraitFit(byId('smile'),head,-1),null);assert.equal(ctx.atelierPortraitFit(byId('smile'),byId('hair-cap'),.001),null);
const neck=byId('model-0002');assert.ok(neck.path[0][1]>head.position[1]+g.boundingBox.min.y*head.scale[1],'Neck must meet the shortened jaw');
for(const side of ['left','right'])assert.deepEqual(byId('arm-'+side).path.at(-1),previous.parts.find(p=>p.id==='arm-'+side).path.at(-1),'Wrist moved away from the hand');
for(const p of previous.parts)if(p.group!=='Character'||/leg$|^(sock|shoe|heel|sole)-/.test(p.id))assert.deepEqual(byId(p.id),p,'Calf/foot/creature data changed');
for(const id of ['model-0002','model-0003','arm-left','arm-right']){const g=ctx.atelierHDGeometry(byId(id));for(const key of ['position','normal'])for(const n of g.attributes[key].array)assert.ok(Number.isFinite(n),'Invalid body surface');}
console.log('PORTRAIT_NECK_CONTACT_WRISTS_AND_PRESERVED_CALVES_FEET_CREATURES_PASS');
