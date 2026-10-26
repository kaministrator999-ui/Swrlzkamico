import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const {JSDOM}=require(process.env.SE_JSDOM_MODULE);
const root='projects/swrlz-forge-moba/';
const src=fs.readFileSync(root+'runtime/sheep_directed_mirror_decoy_v11_131.js','utf8');
const css=fs.readFileSync(root+'runtime/sheep_directed_mirror_decoy_v11_131.css','utf8');
const dom=new JSDOM('<section id="sheepTagHUD"><button id="stSplit"><b>Mirror</b><small id="stSplitInfo"></small></button></section>',{url:'https://example.test/'});
const button=dom.window.document.getElementById('stSplit'),feedback=[],traces=[];
const originalOrder={action:'move',x:23,z:-14,joystick:true};
const unit={id:'sheep-a',kind:'sheep',captured:false,isIllusion:false,archiveLevel:1,archiveSplitAt:-Infinity,
 actor:{rotation:{y:.3}},speed:5,pos:{x:4,y:0,z:5},velocity:{x:3,z:0,lengthSq:()=>9},order:originalOrder};
const s={archive:{decoys:new Set(),materialStates:new Map()},rules:{split:true,splitUnlock:1,splitCooldown:12,splitLifetime:5},elapsed:15,units:[unit],controlledId:unit.id,simulate:false,winner:null};
let performanceNow=15000,baseRefreshCalls=0,baseAfterCalls=0,serial=0;
const ctx={document:dom.window.document,window:dom.window,performance:{now:()=>performanceNow},console,
 stSession:s,stUi:{buildingId:null},paused:false,
 $:id=>dom.window.document.getElementById(id),
 stInstallUI:()=>traces.push('installed'),
 stUiRefreshArchive:(state)=>{baseRefreshCalls++;button.disabled=(Number(state.progression?.splitCooldownRemaining)||0)>0;},
 stArchiveAfterUpdate:()=>{baseAfterCalls++;},
 stArchiveSplit:()=>({ok:false,reason:'original split not expected'}),
 stUiFeedback:(message)=>feedback.push(message),stRefreshHUD:()=>traces.push('hud'),
 stResult:(ok,reason='',rest={})=>({ok,reason,...rest}),
 stArchiveDashTarget:(u,angle,length)=>({x:u.pos.x+Math.sin(angle)*length,z:u.pos.z+Math.cos(angle)*length}),
 stArchiveCloneSheep:(session,u)=>{
   const actor={};const id='decoy-'+(++serial);
   const copy={id,kind:'sheep',actor,speed:u.speed,pos:{...u.pos}};
   s.archive.decoys.add(copy);
   const material={opacity:1,transparent:false,depthWrite:true};
   copy.material=material;s.archive.materialStates.set(actor,[{clones:[material]}]);return copy;
 },
 stArchiveSetRoute:(copy,plan)=>{copy.route=plan;},
 stSetOrder:(copy,order)=>{copy.order=order;},
 stUiCommand:(action,payload)=>ctx.stArchiveSplit(s,unit,payload||{})
};
vm.createContext(ctx);vm.runInContext(src,ctx,{filename:'se131-mirror.js'});
ctx.stInstallUI();
const badge=button.querySelector('.st131-mirror-cooldown');
assert.ok(badge,'cooldown number is attached directly to Mirror button');
assert.ok(css.includes('.st131-mirror-cooldown[hidden]'));
ctx.stUiRefreshArchive({progression:{splitCooldownRemaining:11.4}},unit,null,true,0);
assert.equal(badge.textContent,'12');
assert.equal(badge.hidden,false);
assert.equal(button.getAttribute('aria-label'),'Mirror decoy · 12 seconds remaining');
ctx.stUiRefreshArchive({progression:{splitCooldownRemaining:0}},unit,null,true,0);
assert.equal(badge.hidden,true);
assert.equal(button.disabled,false);
assert.equal(ctx.st131MirrorVector(30,0),Math.PI/2,'right drag -> world east');
assert.equal(ctx.st131MirrorVector(0,-30),Math.PI,'upwards drag -> world north (-Z) (angle represented as PI)');
assert.equal(ctx.st131MirrorVector(4,2),null,'small tap uses moving sheep heading');
function pointer(type,x,y,id=2){
 const event=new dom.window.Event(type,{bubbles:true,cancelable:true});
 for(const [k,v] of Object.entries({pointerId:id,pointerType:'touch',button:0,clientX:x,clientY:y}))Object.defineProperty(event,k,{value:v});
 button.dispatchEvent(event);return event;
}
pointer('pointerdown',100,120);pointer('pointermove',145,120);pointer('pointerup',155,120);
assert.equal(serial,1,'drag cast produces exactly one decoy');
const decoy=[...s.archive.decoys][0];
assert.equal(unit.order,originalOrder,'sheep move/joystick order must be unchanged');
assert.equal(unit.pos.x,4);assert.equal(unit.pos.z,5);
assert.ok(decoy.order.x>unit.pos.x+5,'decoy dashes in user drag direction');
assert.ok(Math.abs(decoy.order.z-unit.pos.z)<.000001,'horizontal drag has no opposite-world deflection');
assert.ok(decoy.speed>unit.speed,'decoy darts quickly');
assert.ok(decoy.archiveExpires-s.elapsed<=4,'short limited lifetime');
assert.equal(unit.archiveSplitAt,s.elapsed,'recharge begins on cast');
assert.ok(feedback.some(x=>x.includes('Mirror dashes away')),'feedback confirms cast');
button.click();
assert.equal(serial,1,'synthetic click after pointerup cannot duplicate Mirror');
const denied=ctx.stArchiveSplit(s,unit,{angle:0});
assert.equal(denied.ok,false,'cooldown blocks repeated cast');
assert.ok(denied.cooldown>0);
s.elapsed=decoy.archiveExpires-.35;
ctx.stArchiveAfterUpdate(s,.016,0);
assert.ok(decoy.material.opacity<.55&&decoy.material.opacity>.1,'last 700ms fade');
assert.equal(decoy.material.transparent,true);
assert.equal(decoy.material.depthWrite,false);
assert.equal(baseAfterCalls,1,'preserves original archive/organic animation');
s.elapsed=30;performanceNow=30000;
button.disabled=false;
button.click();
assert.equal(serial,2,'keyboard/simple-tap cast works after cooldown');
const forward=[...s.archive.decoys].find(d=>d.id==='decoy-2');
assert.ok(forward.order.x>unit.pos.x,'simple tap follows current eastward movement');
assert.equal(unit.order,originalOrder,'second cast still preserves navigation');
s.rules.split=false;s.elapsed=50;unit.archiveSplitAt=-Infinity;
const blocked=ctx.stArchiveSplit(s,unit,{angle:1});
assert.equal(blocked.ok,false,'disabled Classic Mirror remains disabled');
const assembled=process.env.SE_ASSEMBLED_HTML&&fs.readFileSync(process.env.SE_ASSEMBLED_HTML,'utf8');
if(assembled){
 for(const token of [
  'SWYRL_ENGINE_DEPLOY_MARKER: V11_131_DIRECTED_SHORT_MIRROR_DECOY_COOLDOWN',
  'st131MirrorDirection','st131InstallMirrorControl','st131-mirror-cooldown',
  'st131AfterBase=stArchiveAfterUpdate',
  'se130InstallSecondTapProtection','st126SeedAtSheep',
  'st127BuildOrganicPrototype','se128InstallStarterChoices'
 ])assert.ok(assembled.includes(token),'missing integrated '+token);
}
console.log('SE131_MOVING_DRAG_DIRECTED_DECOY_COOLDOWN_FADE_AND_NATIVE_GAMEPLAY_PASS');
