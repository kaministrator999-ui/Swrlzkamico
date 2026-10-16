import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import * as THREE from 'three';
const root=new URL('../',import.meta.url),read=p=>fs.readFileSync(new URL(p,root),'utf8');
const canonical=JSON.parse(read('scenes/model-atelier-festival-detail-v11-16.swyrl.json')).project.modelAtelier;
const reference=read('runtime/model_atelier_reference_v11_13.js'),leaf=reference.slice(reference.indexOf('function atelierReferenceLeaf('),reference.indexOf('function atelierValidateAssemblies('));
const context=vm.createContext({THREE,console,model:()=>canonical});
vm.runInContext(read('runtime/model_atelier_density_v11_16.js')+'\n'+leaf+'\n'+read('runtime/model_atelier_hd_v11_17.js'),context);
const geometry=(id,style,relief=.7)=>{const p=structuredClone(canonical.parts.find(p=>p.id===id));p.hdFinish={style,relief};p.meshDensity={u:48,v:24};return context.atelierHDGeometry(p);};
const cases=[['model-0001','portrait'],['left-sclera','eye'],['left-iris','iris'],['left-ear','ear'],['hair-bun--1','wrap'],['hair-front--1-0','hair'],['model-0002','skin'],['smile','lip'],['skirt-panel-0','cloth'],['sock-left','sock'],['shoe-left','leather'],['bow-left--1','bow'],['azure-body','paper'],[canonical.parts.find(p=>p.surfaceStyle==='paper-leaf').id,'leaf']];
for(const [id,style]of cases){const g=geometry(id,style),pos=g.attributes.position,norm=g.attributes.normal,col=g.attributes.color;assert.ok(pos.count>20,id);assert.equal(col.count,pos.count,id);assert.equal(norm.count,pos.count,id);
 for(const a of [pos,norm,col])for(const v of a.array)assert.ok(Number.isFinite(v),id+' nonfinite generated attribute');
 for(const i of g.index?.array||[])assert.ok(Number.isInteger(i)&&i>=0&&i<pos.count,id+' invalid face index');
 g.computeBoundingBox();assert.ok(g.boundingBox.getSize(new THREE.Vector3()).length()>0,id);console.log('HD_SURFACE_GEOMETRY_PASS',style,pos.count,Math.floor((g.index?.count||pos.count)/3));
}
const strand=geometry('hair-front--1-0','hair'),norm=strand.attributes.normal;for(let row=0;row<=48;row++){const a=row*25,b=a+24;assert.ok(new THREE.Vector3().fromBufferAttribute(norm,a).distanceTo(new THREE.Vector3().fromBufferAttribute(norm,b))<1e-6,'Visible seam in strand normals');}
assert.notDeepEqual(Array.from(geometry('skirt-panel-0','cloth',0).attributes.position.array),Array.from(geometry('skirt-panel-0','cloth',1).attributes.position.array),'Embroidery relief must alter actual mesh vertices');
const iris=geometry('left-iris','iris').attributes.color.array,shades=new Set();for(let i=0;i<iris.length;i+=3)shades.add([iris[i],iris[i+1],iris[i+2]].map(v=>v.toFixed(3)).join(','));assert.ok(shades.size>100,'Iris has no radial color detail');
const shoe=geometry('shoe-left','leather');shoe.computeBoundingBox();assert.ok(Math.abs(shoe.boundingBox.min.y+1)<1e-6,'Leather finish moved the shoe away from its authored ground contact');
const paper=geometry('azure-body','paper');assert.ok(paper.index.count/3>25000,'Paper finish must contain the core and genuinely subdivided creased leaves');
assert.equal(context.atelierHDGeometry({...canonical.parts[0],hdFinish:undefined}),null);
console.log('HD_GEOMETRY_FINITE_FACES_STRAND_NORMALS_RELIEF_IRIS_AND_PAPER_PASS');
