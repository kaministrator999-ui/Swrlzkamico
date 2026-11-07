#!/usr/bin/env node
// §E v11.308 focused logic smoke: compiled Arcane XR frame, no headset emulation.
const fs=require('fs'),assert=require('node:assert/strict'),vm=require('node:vm');
const html=fs.readFileSync(process.argv[2],'utf8');
const start=html.indexOf('// SE308_GRIP_ANCHOR:');
const end=html.indexOf('window.SWYRL_ENGINE_BLANK_VR_HANDS=',start);
assert(start>0 && end>start,'compiled grip-frame source present');
const src=html.slice(start,end);
assert(src.includes('r.ray.visible=!se308Active'),'ray visibility scoped to starter');
assert(src.includes('record?.input?.gripSpace'),'grip-space support');
assert(src.includes('se279Animate(hand,record)'),'unchanged analog gesture drive');
assert(html.includes('poseGroup.position.set(side===\'left\'?-.012:.012,-.022,.116)'),'hand fit offset');
assert(html.includes('modelGroup.scale.setScalar(.112)'),'hand fit scale');
assert(html.includes('poseGroup.rotation.set(-Math.PI/2,Math.PI,0)'),'dorsal-up axes retained');
assert(html.includes('function se280Cast(side,record,key){'),'same spell renderer');
assert(html.includes('record.controller.localToWorld(new THREE.Vector3(0,-.025,-.16))'),'same spell aim origin');

class Node {
 constructor(){this.parent=null;this.children=[];}
 add(child){if(child.parent)child.removeFromParent();this.children.push(child);child.parent=this;}
 removeFromParent(){if(!this.parent)return;const a=this.parent.children;const i=a.indexOf(this);if(i>=0)a.splice(i,1);this.parent=null;}
}
const grips=[new Node(),new Node()],controllers=[new Node(),new Node()],scene=new Node();
const records=['left','right'].map((side,index)=>({
 index,controller:controllers[index],input:{handedness:side,gripSpace:{id:side}},
 ray:{visible:true}
}));
const hands={attached:new Map(),gripAnchors:new Map(),lastError:'',updates:0};
let gestures=0,builds=0;
const ctx={Map,console,scene,
 se279Hands:hands,se279GameId:'blank-vr-hands',
 se181XR:{session:{},controllers:records},
 renderer:{xr:{isPresenting:true,getControllerGrip:i=>grips[i]}},
 currentProject:{kind:'blank-vr-hands'},
 se279BuildGlove:side=>(builds++,{side,root:new Node()}),
 se279Animate:()=>{gestures++},
 se279ReleaseHand:view=>view.root.removeFromParent(),
 se279Cleanup:()=>{for(const h of hands.attached.values())h.root.removeFromParent();hands.attached.clear();for(const g of hands.gripAnchors.values())g.removeFromParent();hands.gripAnchors.clear()}
};
vm.createContext(ctx);vm.runInContext(src,ctx);
vm.runInContext('se279XRFrame()',ctx);
assert.deepEqual(records.map(r=>r.ray.visible),[false,false],'in spellcasting, rays visually hidden');
assert.equal(hands.attached.get('left').root.parent,grips[0],'left glove grip tracked');
assert.equal(hands.attached.get('right').root.parent,grips[1],'right glove grip tracked');
assert.equal(hands.gripAnchors.size,2,'grip mounts owned');
assert.equal(gestures,2,'two gloves retain analog gesture frame');
ctx.currentProject={kind:'sheep-tag'};vm.runInContext('se279XRFrame()',ctx);
assert.deepEqual(records.map(r=>r.ray.visible),[true,true],'other projects restore rays');
assert.equal(hands.attached.size,0,'hands removed on project exit');
assert.equal(hands.gripAnchors.size,0,'grip mounts removed on project exit');
ctx.currentProject={kind:'blank-vr-hands'};
records[0].input.gripSpace=null;
vm.runInContext('se279XRFrame()',ctx);
assert.equal(hands.attached.get('left').root.parent,controllers[0],'fallback to target ray if no gripSpace');
assert.equal(hands.attached.get('right').root.parent,grips[1],'right remains on grip');
assert.deepEqual(records.map(r=>r.ray.visible),[false,false],'fallback still hides beams');
ctx.se181XR.session=null;ctx.renderer.xr.isPresenting=false;
vm.runInContext('se279XRFrame()',ctx);
assert.deepEqual(records.map(r=>r.ray.visible),[true,true],'restore ray visibility on VR exit');
console.log('SE308_GRIP_RAY_SMOKE_OK',JSON.stringify({scenarios:4,builds,gestures}));
