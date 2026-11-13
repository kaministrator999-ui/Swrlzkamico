import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import {fileURLToPath,pathToFileURL} from 'node:url';
const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const THREE=await import(pathToFileURL(path.resolve(process.argv[2])));assert.equal(THREE.REVISION,'169');
const html=fs.readFileSync(process.argv[3],'utf8');
function fn(name){const a=html.indexOf('function '+name+'(');assert(a>=0,name);let i=html.indexOf('{',a),d=0;for(;i<html.length;i++){if(html[i]==='{')d++;else if(html[i]==='}'&&!--d)return html.slice(a,i+1);}throw Error(name);}
const reference={offset:'current model orbit'},calls=[],target=new THREE.Group(),grip=new THREE.Group(),scene=new THREE.Scene();scene.add(target,grip);target.matrixAutoUpdate=grip.matrixAutoUpdate=false;target.matrix.makeTranslation(-3,0,0);grip.matrix.makeTranslation(-2,0,0);scene.updateMatrixWorld(true);
const record={target,grip,input:{targetRaySpace:{kind:'ray'},gripSpace:{kind:'grip'}}},ctx=vm.createContext({renderer:{xr:{getReferenceSpace:()=>reference}}});vm.runInContext(fn('se340Tracked'),ctx);
const quaternion=new THREE.Quaternion().setFromEuler(new THREE.Euler(.2,.4,0)),matrix=new THREE.Matrix4().compose(new THREE.Vector3(.2,1.3,-.4),quaternion,new THREE.Vector3(1,1,1));
const frame={getPose:(space,ref)=>{calls.push([space,ref]);return {transform:{matrix:matrix.toArray()}};}};let groups=0;
assert.equal(ctx.se340Tracked(record,frame,'target'),true);target.updateWorldMatrix(true,false);assert.deepEqual(target.matrixWorld.toArray(),matrix.toArray());assert.equal(calls[0][0],record.input.targetRaySpace);assert.equal(calls[0][1],reference);groups++;
{
 const direction=new THREE.Vector3(0,0,-1).applyQuaternion(quaternion),center=target.position.clone().addScaledVector(direction,.5),plane=new THREE.Mesh(new THREE.PlaneGeometry(.2,.15),new THREE.MeshBasicMaterial({side:THREE.DoubleSide}));plane.position.copy(center);plane.quaternion.copy(quaternion);scene.add(plane);scene.updateMatrixWorld(true);
 const cast=new THREE.Raycaster(target.getWorldPosition(new THREE.Vector3()),new THREE.Vector3(0,0,-1).transformDirection(target.matrixWorld));assert.equal(cast.intersectObject(plane,false).length>0,true,'Exact-frame native controller pose must hit the intended tool card');plane.geometry.dispose();plane.material.dispose();groups++;
}
assert.equal(ctx.se340Tracked(record,frame,'grip'),true);assert.deepEqual(grip.position.toArray(),[.2,1.3,-.4]);assert.equal(calls[1][0],record.input.gripSpace);groups++;
{
 const saved=target.matrix.clone();for(const frame of [{getPose:()=>null},{getPose:()=>({transform:{matrix:[NaN,...Array(15).fill(0)]}})},{getPose:()=>{throw Error('tracking');}},{}]){assert.equal(ctx.se340Tracked(record,frame,'target'),false);assert.equal(target.matrix.equals(saved),true);}groups++;
}
{
 const test=fs.readFileSync(path.join(ROOT,'tests/model_vr_ui_preservation_v11_430.mjs'),'utf8'),a=test.indexOf('function fixture(){'),b=test.indexOf('let groups=',a);
 const begin=html.indexOf('/* SE360_MODEL_VR_UI_START */'),end=html.indexOf('/* SE360_MODEL_VR_UI_END */',begin);
 const sandbox=vm.createContext({THREE,assert,vm,source:html.slice(begin,end),teaching:fs.readFileSync(path.join(ROOT,'runtime/model_studio_teaching_v11_430.js'),'utf8')});vm.runInContext(test.slice(a,b)+'\nthis.createFixture=fixture;',sandbox);const f=sandbox.createFixture();f.settle();const visible=f.targets()[0],hidden=f.targets()[1];hidden.visible=false;hidden.position.copy(visible.position);hidden.quaternion.copy(visible.quaternion);hidden.position.z+=.03;f.ui.root.updateMatrixWorld(true,true);assert.equal(f.hit(visible)?.object===visible,true,'An invisible card must never intercept a visible control ray');assert.equal(f.ui.press(hidden),false);groups++;
 // Input can arrive before the renderer propagates a moved spatial window.
 // Aim at its current local transform without updating cached matrixWorld.
 f.ui.root.position.add(new THREE.Vector3(.35,.22,-.4));
 const currentRoot=new THREE.Matrix4().compose(f.ui.root.position,f.ui.root.quaternion,f.ui.root.scale),point=visible.position.clone().applyMatrix4(currentRoot),normal=new THREE.Vector3(0,0,1).applyQuaternion(f.ui.root.quaternion);
 const cast=new THREE.Raycaster(point.clone().addScaledVector(normal,.4),normal.clone().negate());assert.equal(f.ui.hitTest(cast)?.object===visible,true,'Ray picks must propagate the current menu matrices before render');f.ui.dispose();groups++;
}
console.log('MODEL_CONTROLLER_FRAME_440_PASS',JSON.stringify({groups,existingTrackingPoseQuery:true,currentOffsetReference:true,noHeadPoseChanges:true,trackingLossPreserved:true,hiddenCardsExcluded:true}));
