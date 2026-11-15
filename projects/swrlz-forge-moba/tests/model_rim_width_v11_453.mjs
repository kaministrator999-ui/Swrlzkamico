#!/usr/bin/env node
// v11.453: coplanar inner border and native-only rim width controls.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const html=fs.readFileSync(process.argv[2],'utf8');
const marker='SWYRL_ENGINE_DEPLOY_MARKER: V11_453_INSET_RIM_WIDTH';
assert(html.includes(marker),'New sealed source marker missing');
const a=html.indexOf('/* SE453_INSET_RIM_WIDTH_START */');
const b=html.indexOf('/* SE453_INSET_RIM_WIDTH_END */',a);
assert(a>=0&&b>a,'Missing viewport Inset control');
const js=html.slice(a,b+'/* SE453_INSET_RIM_WIDTH_END */'.length);
new vm.Script(js,{filename:'model_rim_width_v11_453.js'});
for(const token of [
 'window.se453RimBorderAdd?.(record);',
 'window.se453RimBorderClear?.(record);',
 'new THREE.LineLoop(geometry,material)',
 'se430MeshOps.region(record.data,record.selectedFaces)',
 "input.dispatchEvent(new Event('input',{bubbles:true}))",
 'setPointerCapture','releasePointerCapture','se453PrepareRim',
 'Bake edits & preview rim','se451-amount-row','se453RimHandle',
 'window.SWYRL_ENGINE_RIM_WIDTH_453'
])assert(html.includes(token),'Missing native rim workflow: '+token);
assert(!js.includes('api().apply('),'Drag must never Apply geometry');
assert(!js.includes('checkpoint('),'Rim handle may not add history');
let created=0,disposed=0;
class Vec{constructor(x,y,z){this.x=x;this.y=y;this.z=z;}}
class Geo{setFromPoints(points){this.points=points;created++;return this;}dispose(){disposed++;}}
class Material{constructor(options){this.options=options;}dispose(){disposed++;}}
class Loop{constructor(geometry,material){this.geometry=geometry;this.material=material;this.userData={};}}
const mesh={objects:[],add(x){this.objects.push(x);x.parent=this;},
 remove(x){this.objects.splice(this.objects.indexOf(x),1);x.parent=null;}};
const part={partId:'cube'};
const sandbox=vm.createContext({
 window:{},se430BeginnerState:{panel:null},
 se430BeginnerAPI:()=>({inspect:()=>null}),se430BeginnerInstall:()=>{},se430BeginnerTick:()=>{},se430BeginnerRefresh:()=>{},
 THREE:{LineLoop:Loop,BufferGeometry:Geo,LineBasicMaterial:Material,Vector3:Vec},
 se430MeshOps:{region:()=>({ok:true,boundary:[0,1,2,3]})},
 requestAnimationFrame:()=>{},partById:()=>part,
 panel:null,camera:null,renderer:null,modelRoot:null
});
vm.runInContext(js,sandbox);
const record={
 operation:'inset',selectedFaces:[1,2],
 data:{positions:[-1,1,-1,1,1,-1,1,1,1,-1,1,1]},mesh
};
sandbox.window.se453RimBorderAdd(record);
assert.equal(mesh.objects.length,1,'A coplanar Inset must show its inner ring');
assert.equal(mesh.objects[0].geometry.points.length,4);
assert.equal(mesh.objects[0].userData.se453Transient,true);
assert.equal(mesh.objects[0].material.options.depthTest,false);
sandbox.window.se453RimBorderClear(record);
assert.equal(mesh.objects.length,0,'Cancel removes transient ring');
assert.equal(disposed,2,'GPU geometry and material are disposed');
sandbox.window.se453RimBorderClear(record);
assert.equal(disposed,2,'Do not dispose a rim twice');
sandbox.window.se453RimBorderAdd({...record,operation:'extrude'});
assert.equal(mesh.objects.length,0,'Only Inset shows the special coplanar rim');
console.log('SE453_RIM_WIDTH_PASS: explicit inner border visible, disposal verified, touch handle uses native preview input');
