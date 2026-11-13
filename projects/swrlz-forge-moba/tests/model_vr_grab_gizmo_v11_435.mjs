import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
assert.ok(process.argv[2],'Pass the installed Three r169 module');
const THREE=await import(pathToFileURL(path.resolve(process.argv[2])));
assert.equal(THREE.REVISION,'169');
const read=name=>fs.readFileSync(path.join(ROOT,'runtime',name),'utf8');
const phase=read('model_vr_phase1_v11_372.js');
const fluent=read('model_vr_fluent_tools_v11_390.js');
const section=(s,a,b)=>s.slice(s.indexOf(a),s.indexOf(b,s.indexOf(a)));
const nativeFrame=section(phase,'function se372GizmoFrame(s){','function se372GuideStart(g){');
const nativeConstrain=section(phase,'function se372Constrain(g,translation,rotation){','function se372Dispose(){');
const updatePose=section(fluent,'function se390UpdatePose(g,pose,gain){','function se390UpdateExtrude(g,pose,gain){');
const source431=read('model_vr_gizmo_access_v11_431.js');
const source435=read('model_vr_grab_gizmo_v11_435.js');
function fixture(){
 const scene=new THREE.Scene(),model=new THREE.Group();scene.add(model);
 const selection={ids:['cube'],primaryId:'cube',pivot:[0,0,0]};
 const begins=[],updates=[],pulses=[],notices=[];let fallback=0;
 const s={scene,mode:'grab',lastViewer:{position:new THREE.Vector3(0,0,1)},controllers:[],gesture:null,
  ui:{root:new THREE.Group(),targets:[],hitTest:()=>null},inputSample:{axes:{},thresholds:{snapDegrees:15}},frameDt:.016,snap:false};
 s.ui.root.visible=false;scene.add(s.ui.root);
 const tools={selection:()=>selection,beginGroup:(ids,mode)=>{begins.push(mode);return {ok:true};},
  updateGroup:change=>{updates.push(change);return {ok:true};}};
 const ctx=vm.createContext({window:{},THREE,se340XR:s,se350Tools:()=>tools,se350Root:()=>model,
  se340Cast:r=>r.cast,se340Pulse:(...args)=>pulses.push(args),
  se340Notice:x=>notices.push(x),se390NoticeError:r=>{throw Error(r?.error||'unexpected begin error');},
  se340CancelGesture:()=>{},se372GuideStart:()=>{},se372GuideUpdate:()=>{},
  se390BeginGrab:()=>{fallback++;return true;},se340Poll:r=>{r.hit=se374GizmoContact(r);}});
 vm.runInContext('function se372MakeGizmo(){}\nfunction se374GizmoContact(){}\nfunction se372GizmoHit(){}\n'+
  nativeFrame+nativeConstrain+read('model_vr_grab_v11_390.js')+updatePose+
  source431+source435+
  '\nthis.frame=()=>se372GizmoFrame(se340XR);this.contact=r=>se374GizmoContact(r);'+
  'this.start=(r,p,pose)=>se390BeginGrab(r,p,pose);this.update=(g,pose)=>se390UpdatePose(g,pose,1);',ctx);
 function frame(mode='grab'){
  s.mode=mode;ctx.frame();scene.updateMatrixWorld(true);
 }
 function ray(local){
  const g=s.se372Gizmo.root;g.updateWorldMatrix(true,true);
  const target=g.localToWorld(new THREE.Vector3(...local));
  return {targetTracked:true,cast:new THREE.Raycaster(target.clone().add(new THREE.Vector3(0,0,.8)),
    new THREE.Vector3(0,0,-1),.01,5),input:{handedness:'right'}};
 }
 const pose=(x=0,y=0,z=1)=>({position:new THREE.Vector3(x,y,z),quaternion:new THREE.Quaternion()});
 frame();
 return {s,scene,model,selection,begins,updates,pulses,notices,ctx,frame,ray,pose,get fallback(){return fallback;}};
}
let groups=0;
{
 const f=fixture(),g=f.s.se372Gizmo;
 assert.equal(f.s.mode,'grab');assert.equal(g.root.visible,true);
 assert.equal(g.handles.filter(h=>h.visible).length,6);
 assert.ok(g.handles.filter(h=>h.visible).every(h=>h.userData.se431Role==='move'));
 for(const [axis,position] of [['x',[.185,0,0]],['y',[0,.185,0]],['z',[0,0,.185]]]){
  const record=f.ray(position);assert.equal(f.ctx.contact(record)?.axis,axis);
 }
 assert.equal(f.ctx.window.SWYRL_ENGINE_MODEL_VR_GRAB_GIZMO.inspect().visible,true);
 groups++;
}
{
 const f=fixture(),r=f.ray([.185,0,0]);
 assert.equal(f.ctx.start(r,'grab',f.pose()),true);const g=f.s.gesture;
 assert.equal(g.mode,'move');assert.equal(g.axis,'x');assert.deepEqual(f.begins,['move']);
 f.ctx.update(g,f.pose(.22,.10,1.18));
 assert.equal(f.updates.length,1);
 assert.ok(f.updates[0].translation[0]>.2);
 assert.ok(Math.abs(f.updates[0].translation[1])<1e-8);
 assert.ok(Math.abs(f.updates[0].translation[2])<1e-8);
 assert.equal(f.updates[0].scale,1);
 assert.deepEqual([...f.updates[0].rotation],[0,0,0,1]);
 f.frame('grab');assert.equal(f.s.se372Gizmo.root.visible,true);
 assert.equal(f.ctx.window.SWYRL_ENGINE_MODEL_VR_GRAB_GIZMO.inspect().activeAxis,'x');
 groups++;
}
{
 const f=fixture(),r=f.ray([.8,.8,.2]);
 assert.equal(f.ctx.contact(r),null);
 assert.equal(f.ctx.start(r,'grab',f.pose()),true);
 assert.equal(f.fallback,1);assert.equal(f.begins.length,0);
 groups++;
}
{
 const f=fixture(),r=f.ray([.185,0,0]);
 f.s.ui.root.visible=true;
 const panel=new THREE.Mesh(new THREE.PlaneGeometry(.7,.7),new THREE.MeshBasicMaterial({side:THREE.DoubleSide}));
 panel.position.z=.5;f.s.ui.root.add(panel);f.s.ui.targets=[panel];
 f.s.ui.hitTest=cast=>cast.intersectObjects([panel],false)[0]||null;
 f.scene.updateMatrixWorld(true);
 assert.equal(f.ctx.contact(r),null,'VR menu must own its ray ahead of a handle');
 assert.equal(f.ctx.start(r,'grab',f.pose()),true);assert.equal(f.fallback,1);
 groups++;
}
{
 const f=fixture();f.frame('inspect');assert.equal(f.s.se372Gizmo.root.visible,false);
 f.frame('rotate');assert.equal(f.s.se372Gizmo.handles.filter(h=>h.visible).length,3);
 f.frame('scale');assert.equal(f.s.se372Gizmo.handles.filter(h=>h.visible).length,1);
 f.frame('move');assert.equal(f.s.se372Gizmo.handles.filter(h=>h.visible).length,6);
 f.selection.ids=[];f.frame('grab');assert.equal(f.s.se372Gizmo.root.visible,false);
 assert.equal(f.ctx.contact(f.ray([.185,0,0])),null);
 groups++;
}
console.log('MODEL_VR_GRAB_GIZMO_V11_435_PASS',JSON.stringify({groups,three:THREE.REVISION,
 grabVisual:true,axisGripNativeMove:true,freeGrabRetained:true,menuPriority:true,hiddenSelection:true}));
