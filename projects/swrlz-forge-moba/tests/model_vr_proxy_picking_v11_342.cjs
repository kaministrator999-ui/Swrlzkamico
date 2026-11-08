#!/usr/bin/env node
'use strict';
const assert=require('node:assert/strict'),fs=require('fs'),path=require('path'),vm=require('vm');
const d=path.resolve(__dirname,'../runtime');
const w=fs.readFileSync(path.join(d,'model_vr_workspace_v11_342.js'),'utf8');
const u=fs.readFileSync(path.join(d,'model_studio_vr_ui_v11_342.js'),'utf8');
new vm.Script(w);new vm.Script(u);
function extract(name,next){let a=w.indexOf('function '+name+'('),b=w.indexOf('\nfunction '+next+'(',a);assert(a>=0&&b>a);return w.slice(a,b);}
class V{constructor(x=0,y=0,z=0){Object.assign(this,{x,y,z});}distanceTo(o){return Math.hypot(this.x-o.x,this.y-o.y,this.z-o.z);}}
const mesh={isSkinnedMesh:true,visible:true,userData:{}},entries=[{id:'hand',name:'Hand',mesh}];
let exact=0,world=0;
const ray={origin:new V(),intersectBox:(_,v)=>{v.x=.55;return v;},intersectsBox:()=>true,at:(d,v)=>{v.x=d;return v;}};
const cast={ray,near:.01,far:5,intersectObjects:(roots)=>{exact++;assert.equal(roots[0],mesh);return [{object:mesh,distance:.6,point:new V(.6)}];}};
const c={performance,THREE:{Vector3:V},se340Cast:()=>cast,se340PartEntries:()=>entries,se340PartBox:()=>({}),
 se340XR:{ui:{root:{visible:false}},frameCount:9,pickMatrixFrame:-1,pivot:{updateWorldMatrix:()=>world++},pickStats:{hoverCount:0,preciseCount:0,preciseCandidates:0,lastHoverMs:0,maxHoverMs:0}}};
vm.createContext(c);vm.runInContext(extract('se340Hit','se340Pressed')+'\nthis.testHit=se340Hit;',c);
assert.equal(c.testHit({},false).id,'hand');assert.equal(c.testHit({},false).id,'hand');
assert.equal(exact,0,'two hovering hands cannot triangle-raycast');
assert.equal(world,1,'two hands share a matrix update');
assert.equal(c.se340XR.pickStats.hoverCount,2);
assert.equal(c.testHit({},true).id,'hand');assert.equal(exact,1);
assert.equal(c.se340XR.pickStats.preciseCandidates,1);
class M{equals(){return true;}clone(){return new M();}}
class B{constructor(){this.margin=0;}clone(){return new B();}applyMatrix4(){return this;}getSize(v){v.x=1;v.y=2;v.z=1;return v;}expandByScalar(n){this.margin+=n;return this;}}
const geo={boundingBox:new B(),getAttribute:()=>({version:1}),computeBoundingBox:()=>{throw Error('unnecessary recompute');}};
const skin={geometry:geo,isSkinnedMesh:true,matrixWorld:new M(),boundingBox:null,computeBoundingBox:()=>{throw Error('CPU skinning in hover');}};
const bb={THREE:{Box3:B,Vector3:V},se340XR:{boxCache:new WeakMap()},performance};vm.createContext(bb);
vm.runInContext(extract('se340PartBox','se340SourceBounds')+'\nthis.testBox=se340PartBox;',bb);
const a=bb.testBox(skin);assert.equal(bb.testBox(skin),a);assert(a.margin>0);
assert(w.includes('se340Hit(record,false)'));assert(w.includes('s.projectionRevision!==native.revision'));
assert(!u.includes('root.updateWorldMatrix(true,true);return raycaster.intersectObjects'));
console.log('MODEL_VR_342_DUAL_HOVER_NO_TRIANGLES_PASS');
