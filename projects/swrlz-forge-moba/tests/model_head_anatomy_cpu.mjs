import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import * as THREE from 'three';
const root=new URL('../',import.meta.url),read=p=>fs.readFileSync(new URL(p,root),'utf8');
const html=fs.readFileSync(process.env.SWYRL_ANATOMY_HTML||'dist/swrlz-forge-moba/index.html','utf8');
const model=JSON.parse(html.match(/const MODEL_ATELIER_CANONICAL_PROJECT=(.*?);\n\/\/ §wyrl§ Engine Model Atelier v11.3/s)[1]).project.modelAtelier;
const previous=JSON.parse(read('scenes/model-atelier-festival-polish-v11-19.swyrl.json')).project.modelAtelier;
const reference=read('runtime/model_atelier_reference_v11_13.js'),leaf=reference.slice(reference.indexOf('function atelierReferenceLeaf('),reference.indexOf('function atelierValidateAssemblies('));
const ctx=vm.createContext({THREE,console,model:()=>model,atelierSculptApply:(geometry,part)=>{assert.ok(!part?.sculptBrushes?.length&&!part?.sculptVertexEdits?.length,'Historical anatomy fixture must have no native sculpt edits');return geometry;}});vm.runInContext(read('runtime/model_atelier_density_v11_16.js')+'\n'+leaf+'\n'+html.slice(html.indexOf('// Native HD finishes:'),html.indexOf('// §E v11.52: camera-plane-exact pixel brush sizing',html.indexOf('// Native HD finishes:'))),ctx);
const head=model.parts.find(p=>p.id==='model-0001'),g=ctx.atelierHDGeometry(head),a=g.attributes.position,cols=head.meshDensity.u,rows=head.meshDensity.v;
assert.ok(ctx.atelierHeadAnatomyValid(head));assert.equal(g.index.count/3,2*cols*(rows-1));
for(const key of ['position','normal','color'])for(const n of g.attributes[key].array)assert.ok(Number.isFinite(n));
const widthAt=y=>{let width=0,gap=Infinity;for(let i=0;i<=rows;i++){const yy=a.getY(i*(cols+1));if(Math.abs(yy-y)<gap){gap=Math.abs(yy-y);width=Math.max(...Array.from({length:cols+1},(_,j)=>Math.abs(a.getX(i*(cols+1)+j))));}}return width;};
assert.ok(widthAt(-.60)<widthAt(-.12)*.58,'Mandible must narrow independently into the chin');assert.ok(widthAt(.3)<widthAt(.08)*.97,'Temples must sit inside the cheekbone silhouette');assert.ok(widthAt(-.38)>.60&&widthAt(-.38)<.70,'Jaw angle must remain a distinct width between chin and cheek');
const mesh=new THREE.Mesh(g,new THREE.MeshBasicMaterial({side:THREE.DoubleSide}));mesh.position.fromArray(head.position);mesh.scale.fromArray(head.scale);mesh.updateMatrixWorld(true);const ray=new THREE.Raycaster();
const front=(x,y)=>{ray.set(new THREE.Vector3(x,y,2),new THREE.Vector3(0,0,-1));return ray.intersectObject(mesh,false)[0]?.point;};
assert.ok(front(0,3.963).z-front(.07,3.963).z>.018,'Nose must project from the facial mask in actual geometry');
assert.ok(front(0,4.17).z-front(.12,4.17).z<.018,'Forehead must have a flatter facial plane, not a spherical arc');
const old=ctx.atelierHDGeometry(previous.parts.find(p=>p.id===head.id));old.computeBoundingBox();g.computeBoundingBox();assert.ok(g.boundingBox.max.x<old.boundingBox.max.x*.96,'New cheek width must visibly differ from the old ball');assert.equal(g.boundingBox.max.y,old.boundingBox.max.y);
// Fitted contour roots must sit on the newly constructed head, including scaled mouth parts.
for(const p of model.parts.filter(p=>['smile','lower-lip','left-brow','right-brow'].includes(p.id)||/^(Mouth opening|Upper teeth)/.test(p.name))){assert.equal(p.path.length,33);for(const q of p.path){const w=new THREE.Vector3(...q).multiply(new THREE.Vector3(...p.scale)).applyEuler(new THREE.Euler(...p.rotation)).add(new THREE.Vector3(...p.position));const hit=front(w.x,w.y);assert.ok(hit);const gap=w.z-hit.z;assert.ok(gap>=-1e-6&&gap<.006,'Contour does not contact anatomical head');}}
for(const side of ['left','right']){const eye=model.parts.find(p=>p.id===side+'-sclera'),surface=front(eye.position[0],eye.position[1]);assert.ok(surface&&eye.position[2]-eye.scale[2]<surface.z&&eye.position[2]+eye.scale[2]>surface.z,'Eye must be embedded in the socket surface');}
const edited=new Set(['model-0001','model-0002','smile','lower-lip','left-brow','right-brow',...model.parts.filter(p=>/^(Mouth opening|Upper teeth)/.test(p.name)).map(p=>p.id)]);for(const p of previous.parts)if(!edited.has(p.id))assert.deepEqual(model.parts.find(q=>q.id===p.id),p,'Unrelated anatomy or creature changed');
const neck=model.parts.find(p=>p.id==='model-0002');assert.ok(neck.path[0][1]>3.9,'Neck must extend into the underside behind the jaw');
for(const mutation of [f=>f.sections.reverse(),f=>f.sections[2][0]=f.sections[1][0],f=>f.sections[3][1]=-1,f=>f.sections[0][1]=.3,f=>f.facePlane=2,f=>f.noseProjection=NaN,f=>f.extra=true]){const p=structuredClone(head);mutation(p.headAnatomy);assert.equal(ctx.atelierHeadAnatomyValid(p),false);}
console.log('ANATOMICAL_HEAD_SECTIONS_PLANES_PROFILE_EYE_CONTACT_SAVED_CONTOURS_BOUNDS_AND_PRESERVATION_PASS');
