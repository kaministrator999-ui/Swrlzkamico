import assert from 'node:assert/strict';
import fs from 'node:fs';import vm from 'node:vm';import {pathToFileURL} from 'node:url';import path from 'node:path';
const ROOT=path.resolve(path.dirname(new URL(import.meta.url).pathname),'..');
const THREE=await import(pathToFileURL(path.resolve(process.argv[2])).href);
const html=fs.readFileSync(process.argv[3],'utf8');
const start=html.indexOf('function stMakeVisual('),end=html.indexOf('\nfunction ',start+20);assert.ok(start>0&&end>start);
const c={THREE,window:{},stRules:()=>({bounds:64}),console};vm.createContext(c);vm.runInContext(html.slice(start,end),c);
vm.runInContext(fs.readFileSync(path.join(ROOT,'runtime/sheep_visual_batch_v11_434.js'),'utf8')+'\nglobalThis.compact=se434CompactVisual;',c);
const baseFactory=vm.runInContext('se434PriorMakeVisual',c);let groups=0;
function metrics(root){root.updateMatrixWorld(true);const materials=new Set(),pivots=[];let meshes=0,triangles=0;root.traverse(o=>{if(o.isMesh){meshes++;triangles+=(o.geometry.index?.count||o.geometry.attributes.position?.count||0)/3;materials.add(o.material);}if(o.name.startsWith('st'))pivots.push(o.name);});return {meshes,triangles,materials,pivots:pivots.sort(),bounds:new THREE.Box3().setFromObject(root)};}
for(const kind of ['st-tree','st-rock','st-farm','st-income','st-fort','st-shop','st-pond']){
 const root=baseFactory(kind),before=metrics(root);c.compact(root);const after=metrics(root);
 assert.equal(after.triangles,before.triangles,kind+' triangle fidelity');assert.equal(after.materials.size,before.materials.size,kind+' material count');for(const m of before.materials)assert.ok(after.materials.has(m),kind+' original material objects');
 assert.deepEqual(after.pivots,before.pivots,kind+' named animation pivots');assert.ok(after.bounds.min.distanceTo(before.bounds.min)<1e-5&&after.bounds.max.distanceTo(before.bounds.max)<1e-5,kind+' exact shape bounds');assert.ok(after.meshes<=before.meshes);
 console.log(kind,before.meshes,'->',after.meshes,'triangles',after.triangles);groups++;
}
{
 const root=new THREE.Group(),m=new THREE.MeshStandardMaterial({color:'#6ca34f'}),expected={};const old=[];
 for(let i=0;i<4;i++){const mesh=new THREE.Mesh(new THREE.BoxGeometry(1,2,.5),m);mesh.position.set(i*.7,.3*i,-i);mesh.rotation.set(.12*i,.15*i,.2*i);mesh.scale.set(1+i*.1,.8,1.2);mesh.castShadow=true;mesh.receiveShadow=true;mesh.updateMatrix();root.add(mesh);old.push(mesh.geometry);
 const g=mesh.geometry.clone().applyMatrix4(mesh.matrix);for(const [name,a] of Object.entries(g.attributes))(expected[name]||(expected[name]=[])).push(...a.array);g.dispose();}
 c.compact(root);assert.equal(root.children.length,1);const merged=root.children[0];assert.equal(merged.material,m);assert.ok(merged.castShadow&&merged.receiveShadow);
 for(const [name,values] of Object.entries(expected))assert.deepEqual(Array.from(merged.geometry.attributes[name].array),values,name+' transformed attributes are retained exactly');groups++;
 let disposed=0;for(const g of old)g.addEventListener('dispose',()=>disposed++);merged.geometry.dispose();merged.geometry.dispose();assert.equal(disposed,4,'Retired source buffers dispose once through native derived-geometry lifecycle');groups++;
}
{
 const root=new THREE.Group(),m=new THREE.MeshBasicMaterial(),g=new THREE.BoxGeometry();
 for(let i=0;i<4;i++){const o=new THREE.Mesh(g,m);o.name='editable-'+i;root.add(o);}c.compact(root);assert.equal(root.children.length,4,'Named editable nodes are not flattened');groups++;
 const r=new THREE.Group();for(let i=0;i<4;i++){const o=new THREE.Mesh(g,m);o.userData.authoring=true;r.add(o);}c.compact(r);assert.equal(r.children.length,4,'Metadata-bearing nodes are not flattened');groups++;
 const t=new THREE.Group(),transparent=new THREE.MeshBasicMaterial({transparent:true,opacity:.4});for(let i=0;i<4;i++)t.add(new THREE.Mesh(g,transparent));c.compact(t);assert.equal(t.children.length,4,'Transparent sorting remains independent');groups++;
}
console.log('SHEEP_VISUAL_BATCH_434_PASS',JSON.stringify({groups,three:THREE.REVISION,trianglesMaterialsNormalsUVsPreserved:true}));
