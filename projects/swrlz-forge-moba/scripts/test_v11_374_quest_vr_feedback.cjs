/* v11.374 source-backed Quest VR usability regression. */
'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const html=fs.readFileSync(process.argv[2],'utf8');
for(const marker of [
 '/* SE374_MODEL_VR_OWNER_FEEDBACK_START */',
 'se374MenuRayGripStart(s.gesture,hit)',
 'if(se374MenuRayGripUpdate(g))return;',
 'se374GroupBoundary(s,selectedIds);',
 'const gizmo=se374GizmoContact(record,cast);if(gizmo)return finish(gizmo);',
 'hit?.id||hit?.ui||hit?.gizmo',
 "['projects','Projects']",
 "['save-account','Save to account']",
 "action==='projects'",
 "function se372GizmoHit(record){return se374GizmoContact(record)?.axis||null;}"
])assert.ok(html.includes(marker),'Missing integrated VR feature: '+marker);
const begin=html.indexOf('/* SE374_MODEL_VR_OWNER_FEEDBACK_START */'),end=html.indexOf('/* SE374_MODEL_VR_OWNER_FEEDBACK_END */',begin);
assert.ok(begin>=0&&end>begin);
const calls=[];
class Vec {
 constructor(x=0,y=0,z=0){this.x=x;this.y=y;this.z=z}
 clone(){return new Vec(this.x,this.y,this.z)}
 add(v){this.x+=v.x;this.y+=v.y;this.z+=v.z;return this}
 sub(v){this.x-=v.x;this.y-=v.y;this.z-=v.z;return this}
 copy(v){this.x=v.x;this.y=v.y;this.z=v.z;return this}
 toArray(){return [this.x,this.y,this.z]}
 length(){return Math.hypot(this.x,this.y,this.z)}
 multiplyScalar(n){this.x*=n;this.y*=n;this.z*=n;return this}
}
const box=()=>({copy(v){this.value=v;return this},expandByScalar(v){this.pad=v;return this},getSize(){return new Vec(1,1,1)},isEmpty(){return false}});
const s={scene:{add:x=>calls.push(x)},selectedOutline:{visible:true,box:box()},se374MultiOutline:null,
 ui:{root:{position:new Vec(0,1,1),updateWorldMatrix:()=>{}}}};
const sandbox={
 THREE:{Vector3:Vec,Box3:class{},Box3Helper:class{constructor(){this.box=box();this.material={};this.userData={};this.geometry={dispose(){}};this.visible=false;}updateMatrixWorld(){}removeFromParent(){}}},
 se340XR:s,se340Cast:()=>({ray:{at:(d,out)=>out.copy(new Vec(d,1,1))}}),
};
sandbox.THREE.MathUtils={clamp:(n,lo,hi)=>Math.min(hi,Math.max(lo,n))};
vm.createContext(sandbox);vm.runInContext(html.slice(begin,end),sandbox);
sandbox.se374GroupBoundary(s,new Set(['a','b','c']));
assert.equal(s.se374MultiOutline.visible,true);
assert.equal(s.selectedOutline.visible,false);
sandbox.se374GroupBoundary(s,new Set(['a']));
assert.equal(s.se374MultiOutline.visible,false);
assert.equal(s.selectedOutline.visible,true);
const g={record:{},start:new Vec(0,1,1)};
sandbox.se374MenuRayGripStart(g,{point:new Vec(0,1,0.6),distance:.5});
assert.equal(g.se374RayDistance,.5);
assert.equal(sandbox.se374MenuRayGripUpdate(g),true);
assert.equal(s.ui.root.position.x,.5);
console.log('v11.374 group bounds, ray-grip window and first-level project menu PASS');
