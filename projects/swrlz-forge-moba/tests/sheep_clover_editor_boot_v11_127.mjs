import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const THREE=require(process.env.SE_THREE_MODULE);
const root='projects/swrlz-forge-moba/';
const organic=fs.readFileSync(root+'runtime/sheep_clover_organic_walk_swurv_v11_127.js','utf8');
const source=fs.readFileSync(root+'runtime/model_atelier_animals_v11_87.js','utf8');
let natives=0,afterCalls=0;
const ctx={THREE,console,
 stMakeVisual:type=>{
  natives++;
  const g=new THREE.Group(),old=new THREE.Mesh(new THREE.BoxGeometry(),new THREE.MeshBasicMaterial());
  g.add(old);return g;
 },
 stArchiveAfterUpdate:()=>afterCalls++};
vm.createContext(ctx);
vm.runInContext(source,ctx);
vm.runInContext(organic,ctx);
const a=ctx.stMakeVisual('st-sheep');
const b=ctx.stMakeVisual('st-sheep');
assert.equal(natives,2);
const rigA=a.getObjectByName('Clover · organic starter sheep');
const rigB=b.getObjectByName('Clover · organic starter sheep');
assert.ok(rigA&&rigB,'actual Clover organic model must replace fallback sheep visual');
assert.equal(a.children[0].visible,false);
assert.equal(b.children[0].visible,false);
assert.equal(rigA.scale.x,.53);
const parts=[];rigA.traverse(n=>{if(n.isMesh)parts.push(n)});
assert.ok(parts.length>=20,'native starter has detailed organic sheep parts');
assert.ok(parts.some(p=>p.name.includes('Fleece')));
assert.ok(parts.some(p=>p.name.includes('split hoof')));
assert.ok(parts.some(p=>p.name.includes('eye')));
assert.ok(parts.every(p=>p.geometry.attributes.position.count>0));
const bParts=[];rigB.traverse(n=>{if(n.isMesh)bParts.push(n)});
assert.equal(parts[0].geometry,bParts[0].geometry,'cached geometry shared across sheep');
for(let k=0;k<4;k++)assert.ok(rigA.getObjectByName('stLeg'+k),'all four walk pivots');
assert.ok(rigA.getObjectByName('stHead'));
assert.equal(Object.keys(a.userData).some(k=>k==='st127Rig'),false,'no cyclic project serialization');
const pos=new THREE.Vector3(5,0,10),unit={id:'sheep-01',kind:'sheep',captured:false,isIllusion:false,actor:a,pos,phase:.22,walkBlend:.95,walkDistance:12,order:{action:'move'},st127NextPounce:4.9};
const s={elapsed:5,units:[unit]};
ctx.stArchiveAfterUpdate(s,.016,0);
assert.ok(unit.st127PounceAt===5);
assert.ok(unit.st127NextPounce>12,'pounce has natural non-spam interval');
s.elapsed=5.275;unit.walkDistance+=1;
ctx.stArchiveAfterUpdate(s,.016,0);
assert.ok(rigA.position.y>.1,'cute hop adds visible lift');
assert.ok(Math.abs(rigA.position.x)>.01,'swurv adds tiny sideways *visual* motion');
assert.deepEqual([pos.x,pos.y,pos.z],[5,0,10],'no native collision/physics movement');
s.elapsed=6.1;ctx.stArchiveAfterUpdate(s,.016,0);
assert.ok(rigA.position.y<.03,'returns to native gait after leap');
unit.archiveOnUpper=true;unit.st127NextPounce=6.5;s.elapsed=7;
ctx.stArchiveAfterUpdate(s,.016,0);
assert.ok(!Number.isFinite(unit.st127PounceAt)||unit.st127PounceAt!==7,'no pounce on narrow deck');
assert.equal(afterCalls,4,'preserve previous animation handler');
const boot=fs.readFileSync(root+'runtime/engine_editor_boot_gate_v11_127.js','utf8');
const css=fs.readFileSync(root+'runtime/engine_editor_boot_gate_v11_127.css','utf8');
assert.ok(css.includes('html:not(.se127-editor-ready) body::after'));
assert.ok(boot.includes('lastSignature')&&boot.includes('currentProject')&&boot.includes('clearInterval(interval)'));
assert.ok(boot.includes('setTimeout(finish,11000)'));
if(process.env.SE_ASSEMBLED_HTML){
 const s=fs.readFileSync(process.env.SE_ASSEMBLED_HTML,'utf8');
 for(const tok of [
  'SWYRL_ENGINE_DEPLOY_MARKER: V11_127_CLOVER_SHEEP_SWURV_AND_STABLE_EDITOR_BOOT',
  'st127BuildOrganicPrototype','st127AfterUpdateBase','se127-editor-boot',
  'se127InstallBootGate','st126InstallStarterRoutes','stHonestGapLocalClear'
 ])assert.ok(s.includes(tok),'missing source integration '+tok);
}
console.log('SE_V11127_ORGANIC_CLOVER_SHEEP_GAIT_POUNCE_AND_EDITOR_BOOT_PASS',
 parts.length,parts.reduce((n,p)=>n+(p.geometry.index?.count||0)/3,0));
