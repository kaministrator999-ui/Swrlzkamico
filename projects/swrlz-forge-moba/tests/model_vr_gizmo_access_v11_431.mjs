// Real Three r169 meshes, raycasters, transforms and native helper lifecycle.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
assert.ok(process.argv[2],'Pass the existing Three r169 ES module');
const THREE=await import(pathToFileURL(path.resolve(process.argv[2])));
assert.equal(THREE.REVISION,'169');
const legacy=fs.readFileSync(path.join(ROOT,'runtime/model_vr_phase1_v11_372.js'),'utf8');
const source=fs.readFileSync(path.join(ROOT,'runtime/model_vr_gizmo_access_v11_431.js'),'utf8');
function section(start,end){return legacy.slice(legacy.indexOf(start),legacy.indexOf(end,legacy.indexOf(start)));}
const nativeFrame=section('function se372GizmoFrame(s){','function se372GuideStart(g){');
const nativeDispose=section('function se372Dispose(){','async function se372ProjectAction(action){');
function fixture(){
 const scene=new THREE.Scene(),nativeRoot=new THREE.Group();scene.add(nativeRoot);
 const selected={ids:['cube'],pivot:[0,0,0]},pulses=[];
 const menuRoot=new THREE.Group();menuRoot.visible=false;scene.add(menuRoot);
 const menu=new THREE.Mesh(new THREE.PlaneGeometry(.6,.6),new THREE.MeshBasicMaterial({side:THREE.DoubleSide}));
 menu.position.z=.5;menuRoot.add(menu);
 const s={scene,mode:'move',lastViewer:{position:new THREE.Vector3(0,0,1)},controllers:[],gesture:null,
  ui:{root:menuRoot,targets:[menu],hitTest:cast=>cast.intersectObjects([menu],false)[0]||null}};
 const context=vm.createContext({window:{},THREE,se340XR:s,se350Tools:()=>({selection:()=>selected}),se350Root:()=>nativeRoot,
  se340Cast:r=>r.cast,se340Pulse:(r,a,b)=>pulses.push([r,a,b]),se372GuideStop:()=>{}});
 vm.runInContext('function se372MakeGizmo(){}\nfunction se374GizmoContact(){}\nfunction se372GizmoHit(){}\n'+
  'function se340Poll(record){record.hit=se374GizmoContact(record);}\n'+nativeFrame+nativeDispose+'\n'+source+
  '\nthis.frame=()=>se372GizmoFrame(se340XR);this.contact=(r,c)=>se374GizmoContact(r,c);this.axis=r=>se372GizmoHit(r);this.poll=r=>se340Poll(r,null,0);this.dispose=()=>se372Dispose();',context);
 const frame=mode=>{s.mode=mode;context.frame();scene.updateMatrixWorld(true);};
 const point=p=>s.se372Gizmo.root.localToWorld(new THREE.Vector3(...p));
 function ray(local,normal=[0,0,1],distance=.8){
  const target=point(local),direction=new THREE.Vector3(...normal).normalize().transformDirection(s.se372Gizmo.root.matrixWorld);
  const cast=new THREE.Raycaster(target.clone().addScaledVector(direction,distance),direction.clone().negate(),.01,5);
  return {targetTracked:true,cast};
 }
 frame('move');
 return {s,scene,nativeRoot,selected,pulses,context,frame,point,ray,menu,menuRoot};
}
let groups=0;
{
 const f=fixture();
 for(const mode of ['move','rotate','scale']){
  f.frame(mode);const g=f.s.se372Gizmo;
  assert.equal(g.handles.filter(h=>h.visible).length,mode==='move'?6:mode==='rotate'?3:1);
  for(const h of g.handles)assert.equal(h.visible,h.userData.se431Role===mode);
  for(const p of g.se431Picks){assert.equal(p.visible,p.userData.se431Source.visible);assert.equal(p.material.visible,false);}
 }
 assert.equal(f.s.se372Gizmo.handles.find(h=>h.userData.se431Role==='scale').geometry.parameters.width,.052);
 f.context.dispose();groups++;
}
{
 const f=fixture();f.frame('move');
 for(const [axis,position,offset]of [ ['x',[.185,0,0],[0,.028,0]],['y',[0,.185,0],[.028,0,0]],['z',[0,0,.185],[.028,0,0]] ]){
  const exact=f.ray(position);assert.equal(f.context.contact(exact)?.axis,axis,axis+' visible tip');
  const padded=f.ray(position.map((v,i)=>v+offset[i]));const hit=f.context.contact(padded);
  assert.equal(hit?.axis,axis,axis+' padded tip');assert.equal(hit.padded,true);
  assert.equal(f.context.axis(padded),hit.axis,'Grip and hover use the same padded target');
 }
 f.context.dispose();groups++;
}
{
 const f=fixture();f.frame('rotate');
 for(const [axis,normal,point]of [ ['x',[1,0,0],[0,.15/Math.SQRT2,.15/Math.SQRT2]],
  ['y',[0,1,0],[.15/Math.SQRT2,0,.15/Math.SQRT2]],['z',[0,0,1],[.15/Math.SQRT2,.15/Math.SQRT2,0]] ]){
  const exact=f.ray(point,normal);assert.equal(f.context.contact(exact)?.axis,axis,axis+' visible ring');
  const padded=f.ray(point.map(v=>v*1.12),normal);const hit=f.context.contact(padded);
  assert.equal(hit?.axis,axis,axis+' padded ring');assert.equal(hit.padded,true);
  assert.equal(f.context.axis(padded),axis);
 }
 f.context.dispose();groups++;
}
{
 const f=fixture();f.frame('scale');
 const exact=f.ray([0,0,0]);assert.equal(f.context.contact(exact)?.axis,'uniform');assert.equal(f.context.contact(exact)?.padded,false);
 const padded=f.ray([.038,0,0]);assert.equal(f.context.contact(padded)?.axis,'uniform');assert.equal(f.context.contact(padded)?.padded,true);
 // Native scale receives one scalar; no misleading XYZ scale controls exist.
 assert.ok(f.s.se372Gizmo.handles.filter(h=>h.visible).every(h=>h.userData.se372Axis==='uniform'));
 f.context.dispose();groups++;
}
{
 const f=fixture();
 for(const mode of ['move','rotate','scale']){
  f.frame(mode);const r=f.ray(mode==='move'?[.185,0,0]:mode==='rotate'?[.11,.11,0]:[0,0,0]);
  f.menuRoot.visible=true;f.scene.updateMatrixWorld(true);
  assert.ok(f.s.ui.hitTest(r.cast),'An actual menu plane owns the pointer');
  assert.equal(f.context.contact(r),null);assert.equal(f.context.axis(r),null);
  f.menuRoot.visible=false;
 }
 f.context.dispose();groups++;
}
{
 const f=fixture();f.frame('move');const r=f.ray([.185,0,0]);assert.ok(f.context.contact(r));
 r.targetTracked=false;assert.equal(f.context.contact(r),null);r.targetTracked=true;
 f.s.se372Gizmo.root.visible=false;assert.equal(f.context.contact(r),null);f.frame('move');
 f.scene.visible=false;assert.equal(f.context.contact(r),null);f.scene.visible=true;
 f.frame('inspect');assert.equal(f.context.contact(r),null);
 f.selected.ids=[];f.frame('move');assert.equal(f.context.contact(r),null);f.selected.ids=['cube'];f.frame('move');
 for(const handle of f.s.se372Gizmo.handles)if(handle.userData.se372Axis==='x')handle.visible=false;
 assert.equal(f.context.contact(r),null,'Hidden source handles cannot be picked through their padding');
 f.context.dispose();groups++;
}
{
 const f=fixture();f.frame('scale');
 const far=f.ray([0,0,0],[0,0,1],6);assert.equal(f.context.contact(far),null);
 const behind={targetTracked:true,cast:new THREE.Raycaster(new THREE.Vector3(0,0,-1),new THREE.Vector3(0,0,-1),.01,5)};
 assert.equal(f.context.contact(behind),null,'No handle behind the controller ray origin');
 const miss=f.ray([.25,.25,0]);assert.equal(f.context.contact(miss),null,'Expanded tolerance stays local to the gizmo');
 f.context.dispose();groups++;
}
{
 const f=fixture();f.frame('move');const g=f.s.se372Gizmo;
 for(const distance of [.35,.8,1.8,4]){
  f.s.lastViewer.position.set(0,0,distance);f.frame('move');
  assert.ok(g.root.scale.x>=.75&&g.root.scale.x<=2.2);
  const r=f.ray([.185,0,0]);assert.equal(f.context.axis(r),'x','Distance-adjusted exact target remains correct');
 }
 // Native-root orientation and selected pivot still own helper placement.
 f.nativeRoot.rotation.set(.2,.5,0);f.nativeRoot.position.set(.3,.2,-.4);f.selected.pivot=[.2,.1,-.1];f.frame('rotate');
 assert.ok(g.root.position.distanceTo(f.nativeRoot.localToWorld(new THREE.Vector3(...f.selected.pivot)))<1e-10);
 assert.ok(g.root.quaternion.angleTo(f.nativeRoot.getWorldQuaternion(new THREE.Quaternion()))<1e-7);
 assert.equal(f.context.axis(f.ray([0,.11,.11],[1,0,0])),'x');f.context.dispose();groups++;
}
{
 const f=fixture();const r=f.ray([.185,0,0]);f.s.controllers=[r];f.context.poll(r);assert.equal(f.pulses.length,1);
 f.context.poll(r);f.context.poll(r);assert.equal(f.pulses.length,1,'No continuous hover vibration');
 f.frame('move');const axis=f.s.se372Gizmo.handles.find(h=>h.userData.se372Axis==='x');
 const plain=new THREE.Color(axis.userData.se431Color);assert.ok(axis.material.color.r>=plain.r);
 f.s.gesture={kind:'group',axis:'y'};f.frame('move');
 assert.equal(f.s.se372Gizmo.handles.find(h=>h.userData.se372Axis==='x').material.opacity,.42);
 assert.equal(f.s.se372Gizmo.handles.find(h=>h.userData.se372Axis==='y').material.opacity,1);
 f.s.gesture=null;f.context.dispose();groups++;
}
{
 const f=fixture();const g=f.s.se372Gizmo,owned=[...new Set(g.owned)],counts=new Map();
 for(const resource of owned){counts.set(resource,0);resource.addEventListener('dispose',()=>counts.set(resource,counts.get(resource)+1));}
 const allocated=g.owned.length;
 for(let i=0;i<150;i++)f.frame(['move','rotate','scale'][i%3]);
 assert.equal(g.owned.length,allocated,'No per-frame geometry/material allocation');
 f.context.dispose();f.context.dispose();assert.equal(f.s.se372Gizmo,null);
 for(const n of counts.values())assert.equal(n,1,'Native helper lifecycle disposes every owned resource once');
 assert.ok(!source.includes('requestAnimationFrame(')&&!source.includes('setAnimationLoop('));
 assert.ok(!source.includes('ModelAtelier.')&&!source.includes('updateGroup('),'Gizmo access does not replace native model transactions');groups++;
}
{
 const f=fixture();f.frame('move');const r=f.ray([.185,0,0]);
 const root=new THREE.Group();f.scene.add(root);
 const panel=new THREE.Mesh(new THREE.PlaneGeometry(.8,.8),new THREE.MeshBasicMaterial({side:THREE.DoubleSide}));
 panel.position.z=.35;root.add(panel);root.updateMatrixWorld(true);
 f.s.se413Quest={root,panel,buttons:[],folded:false};
 assert.equal(f.context.contact(r),null,'Independent Academy panel owns the ray');
 f.s.se413Quest.folded=true;assert.equal(f.context.axis(r),'x','A folded panel does not retain its hidden face');
 const button=new THREE.Mesh(new THREE.PlaneGeometry(.4,.4),new THREE.MeshBasicMaterial({side:THREE.DoubleSide}));
 button.position.set(.175,0,.4);root.add(button);f.s.se413Quest.buttons=[button];root.updateMatrixWorld(true);
 assert.equal(f.context.axis(r),null,'Folded Academy buttons still own their ray');
 root.visible=false;assert.equal(f.context.axis(r),'x');f.context.dispose();groups++;
}
{
 const f=fixture();const snapshot=f.context.window.SWYRL_ENGINE_MODEL_VR_GIZMO_ACCESS.inspect();
 assert.equal(snapshot.version,'v11.431');assert.equal(snapshot.mode,'move');assert.equal(snapshot.visible,true);
 assert.equal(snapshot.rootMatrixWorld.length,16);assert.equal(snapshot.handles.filter(h=>h.visible).length,6);
 snapshot.handles[0].matrixWorld[12]=999;
 assert.notEqual(f.s.se372Gizmo.handles[0].matrixWorld.elements[12],999,'Inspection exports snapshots without live Three references');
 f.context.dispose();groups++;
}
console.log('MODEL_VR_GIZMO_ACCESS_V11_431_PASS',JSON.stringify({groups,three:THREE.REVISION,modes:['move','rotate','scale'],
 realRayPadding:true,menuPriority:true,hiddenAndBehindRayExcluded:true,sharedHoverAndGrip:true,ownedResources:true,scale:'native uniform scalar'}));
