#!/usr/bin/env node
// Execute shipped gesture math with real Three.js. Native transactions are
// caller-owned; these tests verify that their candidate deltas stay stable.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import {fileURLToPath,pathToFileURL} from 'node:url';
const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
if(!process.argv[2])throw Error('Usage: node tests/model_vr_grab_v11_390.mjs /path/to/three-0.169.0.mjs');
const THREE=await import(pathToFileURL(path.resolve(process.argv[2])));assert.equal(THREE.REVISION,'169');
const source=fs.readFileSync(path.join(ROOT,'runtime/model_vr_grab_v11_390.js'),'utf8');
const context=vm.createContext({THREE});vm.runInContext(source+'\nthis.api={begin:se390BeginPose,candidate:se390PoseCandidate};',context);
const {begin,candidate}=context.api;
const v=(x=0,y=0,z=0)=>new THREE.Vector3(x,y,z),q=()=>new THREE.Quaternion();
const near=(actual,expected,message='number')=>assert.ok(Math.abs(actual-expected)<1e-9,`${message}: ${actual} != ${expected}`);
const nearVector=(actual,expected,message='vector')=>assert.ok(new THREE.Vector3(...actual).distanceTo(expected)<1e-9,message);
const nearQuat=(actual,expected,message='quaternion')=>assert.ok(1-Math.abs(new THREE.Quaternion(...actual).dot(expected))<1e-10,message);
const plain=value=>JSON.parse(JSON.stringify(value));
function fixture(mode='grab',root=null){
 const native=root||new THREE.Group();native.updateMatrixWorld(true);
 const pose={position:v(.2,1.25,-.65),quaternion:q()};
 const g={mode,hand:{position:pose.position.clone(),quaternion:pose.quaternion.clone()},
  rootInverse:native.matrixWorld.clone().invert(),rootQuaternion:native.getWorldQuaternion(q())};
 begin(g,pose);return {g,pose,native,read:options=>plain(candidate(g,pose,{gain:1,dt:1/72,...options}))};
}
let groups=0;
{
 // Inspect and unrelated tools must produce an identity delta even if a
 // caller accidentally samples them through this helper.
 for(const mode of ['inspect','sculpt','draw','lasso','extrude']){
  const f=fixture(mode);f.pose.position.add(v(1,1,1));f.pose.quaternion.setFromAxisAngle(v(0,1,0),.6);
  assert.deepEqual(f.read({scaleAxis:-1}),{translation:[0,0,0],rotation:[0,0,0,1],scale:1});
 }
 groups++;
}
{
 // Model units differ from physical hand units. A rotated/nonuniformly
 // scaled presentation must map hand movement back through its full matrix.
 const root=new THREE.Group();root.position.set(.8,1.1,-1.4);root.rotation.set(.23,-.7,.18);root.scale.set(.7,1.3,.9);
 const f=fixture('grab',root),start=f.pose.position.clone(),inverse=f.g.rootInverse.clone(),basis=f.g.rootQuaternion.clone();
 const worldDelta=q().setFromEuler(new THREE.Euler(.2,.34,-.1));
 f.pose.position.add(v(.12,-.07,.08));f.pose.quaternion.copy(worldDelta);
 const out=f.read(),expected=root.worldToLocal(f.pose.position.clone()).sub(root.worldToLocal(start.clone()));
 nearVector(out.translation,expected,'translation through full native-root matrix');
 const observed=basis.clone().multiply(new THREE.Quaternion(...out.rotation)).multiply(basis.clone().invert());
 nearQuat(observed.toArray(),worldDelta,'world wrist rotation follows root orientation');
 assert.ok(f.g.rootInverse.equals(inverse),'The supplied root inverse must remain untouched');
 assert.ok(f.g.rootQuaternion.equals(basis),'The supplied root quaternion must remain untouched');groups++;
}
{
 // Precision on/off is a speed change from now onward, never a rescaling of
 // an already visible displacement or turn. The transition frame is rebased.
 const f=fixture();f.pose.position.x+=.2;f.pose.quaternion.setFromAxisAngle(v(0,1,0),.4);
 const before=f.read();assert.deepEqual(f.read({gain:.12}),before,'Fine-on must not jump');
 f.pose.position.x+=.1;f.pose.quaternion.setFromAxisAngle(v(0,1,0),.6);
 const fine=f.read({gain:.12});near(fine.translation[0],.212);nearQuat(fine.rotation,q().setFromAxisAngle(v(0,1,0),.424));
 assert.deepEqual(f.read({gain:1}),fine,'Fine-off must not jump');
 f.pose.position.x+=.1;f.pose.quaternion.setFromAxisAngle(v(0,1,0),.7);
 const coarse=f.read();near(coarse.translation[0],.312);nearQuat(coarse.rotation,q().setFromAxisAngle(v(0,1,0),.524));groups++;
}
{
 // A normal initial deadzone suppresses tracking noise. Deliberate movement
 // can accumulate slowly until it crosses the threshold; after activation,
 // even a tiny final release-frame movement is retained.
 const f=fixture('move'),initial=f.pose.position.clone();
 for(let i=1;i<=7;i++){f.pose.position.copy(initial).add(v(i*.0002,0,0));near(f.read().translation[0],0);}
 f.pose.position.copy(initial).add(v(.0016,0,0));near(f.read().translation[0],.0016);
 f.pose.position.x+=.00008;near(f.read().translation[0],.00168,'final small movement');
 f.pose.position.copy(initial);assert.deepEqual(f.read(),{translation:[0,0,0],rotation:[0,0,0,1],scale:1});groups++;
}
{
 // Tool-specific channels remain separate. Moving the wrist during Move or
 // translating it during Rotate must not introduce another saved operation.
 const movement=fixture('move');movement.pose.position.x+=.2;movement.pose.quaternion.setFromAxisAngle(v(1,0,0),.7);
 const m=movement.read({scaleAxis:-1});nearQuat(m.rotation,q());near(m.scale,1);near(m.translation[0],.2);
 const rotation=fixture('rotate');rotation.pose.position.x+=.2;rotation.pose.quaternion.setFromAxisAngle(v(1,0,0),.7);
 const r=rotation.read({scaleAxis:-1});nearVector(r.translation,v());near(r.scale,1);nearQuat(r.rotation,q().setFromAxisAngle(v(1,0,0),.7));groups++;
}
{
 const f=fixture('scale'),initial=f.pose.position.clone();f.pose.position.y+=.2;
 near(f.read().scale,Math.exp(.48));const before=f.read();assert.deepEqual(f.read({gain:.18}),before);
 f.pose.position.y+=.1;near(f.read({gain:.18}).scale,Math.exp(.48+.0432));
 const returned=fixture('scale');returned.pose.position.y+=.2;returned.read();returned.pose.position.copy(initial);near(returned.read().scale,1);groups++;
}
{
 // Stick sizing integrates elapsed time. Different headset frame cadences
 // produce the same result, and a zero-time/release sample adds no scale.
 const scaleAt=fps=>{const f=fixture();for(let i=0;i<fps;i++)f.read({dt:1/fps,scaleAxis:-.75});return f.read({dt:0,scaleAxis:-1}).scale;};
 const a=scaleAt(60),b=scaleAt(90);near(a,b);near(a,Math.exp(1.05));
 const f=fixture();for(let i=0;i<72;i++)f.read({scaleAxis:-1});const before=f.read({dt:0});
 assert.deepEqual(f.read({gain:.12,scaleAxis:-1}),before,'Fine transition must not jump stick sizing');
 for(let i=0;i<72;i++)f.read({gain:.12,scaleAxis:1});near(f.read({gain:.12,dt:0}).scale,Math.exp(1.4*(1-.12)));groups++;
}
{
 // Full wrist loops and returning to the initial pose are exact identity
 // candidates, enabling the native bridge to preserve Redo on no-op release.
 const f=fixture('rotate');for(let i=1;i<=180;i++){f.pose.quaternion.setFromAxisAngle(v(0,1,0),i*Math.PI*2/180);f.read();}
 assert.deepEqual(f.read(),{translation:[0,0,0],rotation:[0,0,0,1],scale:1});
 const noise=fixture('rotate');noise.pose.quaternion.setFromAxisAngle(v(1,0,0),.002);assert.deepEqual(noise.read().rotation,[0,0,0,1]);groups++;
}
{
 // Native snap settings apply to emitted candidates only. They do not feed
 // quantized values back into the incremental state or create zero scales.
 const f=fixture();f.pose.position.add(v(.026,.004,-.016));f.pose.quaternion.setFromAxisAngle(v(0,1,0),THREE.MathUtils.degToRad(38));
 const out=f.read({snap:true,snapDegrees:30});nearVector(out.translation,v(.03,0,-.02));nearQuat(out.rotation,q().setFromAxisAngle(v(0,1,0),Math.PI/6));
 const raw=f.read({snap:false});nearVector(raw.translation,v(.026,.004,-.016));nearQuat(raw.rotation,q().setFromAxisAngle(v(0,1,0),THREE.MathUtils.degToRad(38)));
 const tiny=fixture('scale');tiny.pose.position.y-=10;assert.ok(tiny.read({snap:true}).scale>0);groups++;
}
{
 // A malformed sample must not poison future accumulated candidates. Pose
 // objects and input matrices belong to the renderer and are never mutated.
 const f=fixture(),snapshot=f.pose.position.clone();f.pose.position.x=NaN;assert.throws(()=>f.read(),/finite tracked pose/);
 f.pose.position.copy(snapshot);assert.deepEqual(f.read(),{translation:[0,0,0],rotation:[0,0,0,1],scale:1});
 assert.throws(()=>begin({mode:'grab'},f.pose),/native-root basis/);groups++;
}
console.log('MODEL_VR_GRAB_V11_390_PASS',JSON.stringify({groups,three:THREE.REVISION,precision:'incremental and jump-free',grab:'move, wrist rotation and timed stick scale',sourceWrites:false}));
