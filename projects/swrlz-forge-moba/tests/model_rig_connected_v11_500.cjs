// §E v11.500: pure parent-child chain and automatic-envelope regression.
const fs=require('node:fs'),vm=require('node:vm'),path=require('node:path'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..'),source=fs.readFileSync(path.join(root,'runtime/model_rig_connected_math_v11_500.js'),'utf8');
const sandbox={window:{}};vm.runInNewContext(source,sandbox);
const math=sandbox.window.SWYRL_ENGINE_RIG_CONNECTED_MATH_500;
assert(math?.solve&&math?.snapshot&&math?.apply&&math?.weightOf);
const approx=(a,b)=>assert(Math.abs(a-b)<1e-5,String(a)+' != '+String(b));
const vecApprox=(a,b)=>a.forEach((v,i)=>approx(v,b[i]));
const distance=(a,b)=>Math.hypot(...a.map((x,i)=>x-b[i]));
const rig={bones:[
 {id:'root',parent:null,rest:[0,0,0]},
 {id:'lower',parent:'root',rest:[0,1,0]},
 {id:'mid',parent:'lower',rest:[0,2,0]},
 {id:'tip',parent:'mid',rest:[0,3,0]},
 {id:'side',parent:'root',rest:[1,0,0]}
],envelopes:[
 {bone:'lower',center:[0,.5,0]},
 {bone:'mid',center:[0,1.5,0]},
 {bone:'tip',center:[0,2.5,0]},
 {bone:'side',center:[.8,0,0]}
]};
const untouched=JSON.stringify(rig);
const edit=math.solve(rig,'lower',[1,1,0],true);
assert(edit);assert.equal(edit.locked,true);assert.equal(edit.affected,3);
assert.equal(JSON.stringify(rig),untouched,'preview solver mutated source rig');
const first=math.snapshot(rig);math.apply(rig,edit);
const byId=id=>rig.bones.find(x=>x.id===id).rest;
vecApprox(byId('root'),[0,0,0]);vecApprox(byId('side'),[1,0,0]);
approx(distance(byId('root'),byId('lower')),1);
approx(distance(byId('lower'),byId('mid')),1);
approx(distance(byId('mid'),byId('tip')),1);
vecApprox(byId('lower'),[Math.SQRT1_2,Math.SQRT1_2,0]);
assert.notDeepEqual(rig.envelopes[1].center,[0,1.5,0]);
vecApprox(rig.envelopes[3].center,[.8,0,0]);
math.apply(rig,first);assert.equal(JSON.stringify(rig),untouched,'undo must restore exact rest data');
const free=math.solve(rig,'mid',[.4,2,.2],false);
math.apply(rig,free);
vecApprox(byId('mid'),[.4,2,.2]);vecApprox(byId('tip'),[.4,3,.2]);
math.apply(rig,first);
const rootEdit=math.solve(rig,'root',[1,-.2,.3],true);
math.apply(rig,rootEdit);
vecApprox(byId('side'),[2,-.2,.3]);
vecApprox(byId('tip'),[1,2.8,.3]);
math.apply(rig,first);
assert.equal(math.solve(rig,'lower',[30,0,0],true),null);
assert.equal(math.solve(rig,'missing',[0,0,0],true),null);
// Near-antiparallel vectors must still rotate descendants without NaNs.
const flip=math.solve(rig,'lower',[0,-1,0],true);
assert(flip);math.apply(rig,flip);
approx(distance(byId('lower'),byId('mid')),1);
approx(distance(byId('mid'),byId('tip')),1);
assert(rig.bones.every(b=>b.rest.every(Number.isFinite)));
approx(math.weightOf([0,2,3,2],[.1,.2,.3,.4],2),.6);
approx(math.weightOf([0,2,3,2],[.1,.2,.3,.4],1),0);
approx(math.weightOf([0,1,2,3],[.1,.2,.3,.4],3),.4);
assert.equal(math.weightOf([0,1],[.2,.8],0),0);
console.log('SE500_CONNECTED_BONE_MATH_PASS',JSON.stringify({childrenPreserved:true,rootMovesWholeRig:true,sourceUnchanged:true,undoRestores:true,lockedSegments:true,weightedVertices:true}));
