'use strict';
/* v11.416 · pure VM smoke tests against the actual authored academy and XR coach.
 * Native editing is mocked, so physical controller comfort remains owner-tested.
 */
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const root=path.resolve(__dirname,'..');
const source=name=>fs.readFileSync(path.join(root,'runtime',name),'utf8');
const mockStore=new Map();
const projectId='satchel-local-test';
const cube=(id,scale,position,material='matte',color='#987153')=>
 ({id,name:id,kind:'box',position,scale,rotation:[0,0,0],material,color,group:'Satchel'});
const floor=cube('floor',[1.4,.1,.65],[0,1.09,0]);
const parts=[
 floor,
 cube('wall-left',[.07,.8,.55],[-.66,1.52,0]),
 cube('wall-right',[.07,.8,.55],[.66,1.52,0]),
 cube('wall-front',[1.4,.8,.07],[0,1.52,.30]),
 cube('wall-back',[1.4,.8,.07],[0,1.52,-.30]),
 cube('flap',[1.2,.07,.4],[0,1.98,.33]),
 cube('strap1',[.09,.5,.08],[-.59,2.06,0]),
 cube('strap2',[.09,.5,.08],[0,2.55,0]),
 cube('strap3',[.09,.5,.08],[.58,2.10,0]),
 cube('buckle',[.15,.12,.07],[0,1.78,.37],'metal','#c9a56c'),
 cube('seam',[.12,.09,.09],[.27,1.72,.37])
];
const model={instanceId:projectId,kind:'model-atelier',se412Tutorial:'satchel-001',modelAtelier:{parts}};
let current=0,done=[1,2];
const lesson={
 status:()=>({active:true,projectId,current,progress:done.length}),
 steps:()=>Array.from({length:7},(_,i)=>({index:i,title:'Stage '+(i+1),done:done.includes(i)})),
 applyProgress:indices=>{done=[...indices];return true;},
 choose:i=>{current=i;return true;}
};
const classChanges=[];
const element={classList:{add(x){classChanges.push('add:'+x);},remove(x){classChanges.push('remove:'+x);}},
 scrollIntoView(){}};
let restored=0,painted=0,shaded=0;
class Vec{
 constructor(x=0,y=0,z=0){this.x=x;this.y=y;this.z=z;}
 clone(){return new Vec(this.x,this.y,this.z);}
 copy(v){this.x=v.x;this.y=v.y;this.z=v.z;return this;}
 add(v){this.x+=v.x;this.y+=v.y;this.z+=v.z;return this;}
 sub(v){this.x-=v.x;this.y-=v.y;this.z-=v.z;return this;}
 length(){return Math.hypot(this.x,this.y,this.z);}
 setLength(n){const k=n/this.length();this.x*=k;this.y*=k;this.z*=k;return this;}
}
const ctx={
 console,JSON,Set,Map,Date,Math,Number,String,Array,Object,structuredClone,
 document:{querySelector(sel){return sel==='#dummy' ? element:null;}},
 localStorage:{getItem:k=>mockStore.get(k)||null,setItem:(k,v)=>mockStore.set(k,v)},
 currentProject:model,projectData(){return {project:{...model}};},
 se175Snapshot(){return {id:projectId,data:{project:{...model}}};},
 window:{SWYRL_ENGINE_TUTORIAL_412:lesson,
 SWYRL_E_SATCHEL_BUTTON_GUIDE_414:{references:i=>[{
   key:'scale',name:'Scale',flat:'#dummy',vr:i===0?'scale':'create-box'
 }]}},
 se340XR:{ui:{highlightTutorialAction(){},drawGuideIcon(){}}},
 se340SyncUI(){},se340Publish(){},se340Pulse(){},se340VisibleSession(){return true;},
 se340Hit(){return {quest:true}},
 se340GripPose(){return {position:new Vec(0,0,0)};},
 se340BeginGesture(){return false;},se340UpdateGesture(){return null;},
 se340FinishGesture(){return false;},se340Cleanup(){return false;}
};
ctx.window.SWYRL_E_SATCHEL_NATIVE_416={
 root:()=>null,busy:()=>false,
 validate:objects=>objects.every(o=>!!o.id&&o.kind==='box'),
 restore:objects=>{restored++;model.modelAtelier.parts.splice(0,model.modelAtelier.parts.length,...objects);return {ok:true};},
 paint:(m,c)=>{painted++;return {ok:true,changed:true,message:m+':'+c};},
 shade:()=>{shaded++;return {ok:true,changed:true,message:'Changed shade'};}
};
ctx.se340XR.ui.root={};ctx.se340XR.paletteVisible=true;ctx.se340XR.page='tools';
vm.createContext(ctx);
vm.runInContext(source('model_satchel_academy_v11_416.js'),ctx,{filename:'academy'});
const academy=ctx.window.SWYRL_E_SATCHEL_ACADEMY_416;
assert(academy&&academy.verify(0).ok===true,'A completed open-top pouch also satisfies the earlier blockout objective');
assert.equal(academy.verify(1).ok,true,'Floor plus four real surrounding walls verified');
assert.equal(academy.verify(2).ok,true,'Separate flap detected');
assert.equal(academy.verify(3).ok,true,'Strap segments at varying heights verified');
assert.equal(academy.verify(4).ok,true,'Metal clasp plus details verified');
assert.equal(academy.verify(5).ok,true,'Leather and metal materials verified');
assert.equal(academy.verify(6).ok,null,'Save must not be falsely auto-certified');
academy.progressUpdate(done);
const meta=model.se416TutorialState;
assert.equal(meta.schema,'se416-quest-progress-v1');
assert.equal(JSON.stringify(meta.done),'[1,2]','Cross-context project progress persisted');
assert.equal(ctx.se175Snapshot().data.project.se416TutorialState.lesson,'satchel-001');
assert.equal(ctx.projectData().project.se416TutorialState.lesson,'satchel-001');
assert.equal(academy.showMe(0,false).ok,true);
assert(classChanges.includes('add:se416-show-target'));
const saved=academy.saveCheckpoint();assert.equal(saved.ok,true,saved.message);
model.modelAtelier.parts.splice(0,model.modelAtelier.parts.length,cube('temporary',[1,1,1],[0,0,0]));
assert.equal(academy.restoreCheckpoint().requiresConfirmation,true);
assert.equal(academy.restoreCheckpoint({confirmed:true}).ok,true);
assert.equal(restored,1);
assert.equal(model.modelAtelier.parts.length,parts.length);
assert.equal(academy.inspect().checkpoints,1);
ctx.se340XR.se413Quest={root:{position:new Vec(0,1,-1),updateWorldMatrix(){}},
 folded:false,index:5,buttons:[],message:'',signature:'',canvas:{},texture:{}};
vm.runInContext(source('model_satchel_vr_coach_v11_416.js'),ctx,{filename:'xrCoach'});
const coach=ctx.window.SWYRL_E_SATCHEL_VR_COACH_416;
const makeButton=(b,id)=>b.buttons.push({userData:{se340Action:id}});
coach.install(ctx.se340XR.se413Quest,makeButton);
assert.equal(ctx.se340XR.se413Quest.buttons.length,9);
assert.equal(coach.action('se416-mode'),true);
assert.equal(ctx.se340XR.se413Quest.coachMode,'material');
assert.equal(coach.action('se416-leather'),true);
assert.equal(coach.action('se416-metal'),true);
assert.equal(coach.action('se416-shade-plus'),true);
assert.equal(painted,2);assert.equal(shaded,1);
const record={gripTracked:true,targetTracked:true,held:true};
assert.equal(ctx.se340BeginGesture(record),true,'Quest grip intercepted before model editing');
assert.equal(coach.status().dragging,true);
assert.equal(ctx.se340FinishGesture(record),true);
assert.equal(coach.status().dragging,false);
console.log('SATCHEL_ACADEMY_415_PASS: seven objective checks, safe checkpoints and restore, project progress metadata, native Show Me, VR material actions and world-space grip interception.');
