#!/usr/bin/env node
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const context=vm.createContext({});
vm.runInContext(fs.readFileSync(root+'/runtime/model_vr_input_profile_v11_350.js','utf8')+
 '\nthis.create=se350CreateModelVRInput;this.bindings=SE350_MODEL_VR_BINDINGS;',context);
const clone=x=>JSON.parse(JSON.stringify(x));
const makeProfile=()=>({profileId:'kami-precision',profileName:'Kami Precision',bindings:{
 ...clone(context.bindings),global:[['redo','chord:X+Y','Redo'],['focus','tap:RS','Focus']]},thresholds:{}});
const keyMap={LT:['left',0],LG:['left',1],LS:['left',3],X:['left',4],Y:['left',5],RT:['right',0],RG:['right',1],RS:['right',3],A:['right',4],B:['right',5]};
function setup(profile=makeProfile()){
 const left={handedness:'left',gamepad:{buttons:Array.from({length:6},()=>({pressed:false,value:0})),axes:[0,0,0,0]}};
 const right={handedness:'right',gamepad:{buttons:Array.from({length:6},()=>({pressed:false,value:0})),axes:[0,0,0,0]}};
 let mode='model',t=0,sourceLeft={input:left,tracked:true},sourceRight={input:right,tracked:true};
 const api=context.create({getProfile:()=>profile});
 const sample=(time=t+16)=>{t=time;return api.sample({time,context:mode,sources:[sourceLeft,sourceRight]});};
 const set=(key,value)=>{const [side,i]=keyMap[key];const pad=(side==='left'?left:right).gamepad;pad.buttons[i]={value,pressed:value>.5};};
 sample(0);
 return {api,sample,set,left,right,profile,sourceLeft,sourceRight,mode(value){mode=value;}};
}
let groups=0;
{
 const x=setup();x.set('RT',1);let r=x.sample(10);assert.equal(r.events[0].action,'select');assert.equal(r.events[0].phase,'tap');
 assert.equal(r.buttons.RT.down,true);assert.equal(x.sample(20).events.length,0);x.set('RT',0);assert.equal(x.sample(30).events.length,0);
 x.set('LT',1);assert.equal(x.sample(40).events[0].action,'multiselect');groups++;
}
{
 const x=setup();x.set('A',1);assert.equal(x.sample(10).events.length,0);x.set('A',0);assert.equal(x.sample(100).events[0].action,'tool');
 x.set('A',1);x.sample(200);let r=x.sample(660);assert.equal(r.events[0].action,'tool-wheel');assert(r.held['tool-wheel']);
 x.set('A',0);r=x.sample(700);assert.equal(r.events[0].phase,'end');assert(!r.events.some(e=>e.action==='tool'));groups++;
}
{
 const x=setup();x.set('X',1);x.sample(10);x.set('Y',1);let r=x.sample(80);assert.deepEqual(clone(r.events.map(e=>e.action)),['redo']);
 x.set('X',0);x.set('Y',0);assert.equal(x.sample(100).events.length,0);
 x.set('Y',1);x.sample(200);x.set('Y',0);assert.equal(x.sample(220).events[0].action,'undo');
 x.set('X',1);x.sample(300);assert.equal(x.sample(751).events[0].action,'category-wheel');x.set('X',0);assert.equal(x.sample(800).events[0].phase,'end');groups++;
}
{
 const x=setup();x.set('RG',1);let r=x.sample(10);assert.equal(r.held.grab.action,'grab');assert.equal(r.events[0].phase,'start');
 x.set('RG',0);x.set('B',1);r=x.sample(20);assert(r.cancel);assert.deepEqual(clone(r.events.map(e=>e.action)),['cancel']);
 assert.equal(Object.keys(r.held).length,0);assert(!r.events.some(e=>e.phase==='end'));
 x.set('RG',1);assert.equal(x.sample(30).events.length,0,'cancel held blocks a new grip');
 x.set('B',0);assert.equal(x.sample(40).events.length,0,'grip held through cancel must release before editing');
 x.set('RG',0);x.sample(50);x.set('RG',1);assert.equal(x.sample(60).events[0].action,'grab');
 groups++;
}
{
 const x=setup();x.set('LG',1);x.set('RG',1);let r=x.sample(10);assert(r.held.grab&&r.held.pan);assert(!r.held['two-hand']);
 r=x.sample(470);assert(r.held['two-hand']);assert.equal(r.events.filter(e=>e.action==='two-hand').length,1);
 x.set('LG',0);r=x.sample(490);assert(r.events.some(e=>e.action==='two-hand'&&e.phase==='end'));groups++;
}
{
 const x=setup();x.mode('sculpt');x.sample(10);x.set('RT',1);let r=x.sample(20);assert(r.held.stroke);assert.equal(r.events[0].phase,'start');
 x.set('RT',0);r=x.sample(40);assert(r.events.some(e=>e.action==='stroke'&&e.phase==='end'));
 x.set('LT',1);assert.equal(x.sample(80).events[0].action,'sample');r=x.sample(540);assert(r.held['temporary-smooth']);
 x.set('LT',0);assert(x.sample(550).events.some(e=>e.action==='temporary-smooth'&&e.phase==='end'));groups++;
}
{
 const x=setup();x.left.gamepad.axes=[0,0,.5,-.5];let r=x.sample(10);assert(r.axes.navigate.x>0&&r.axes.navigate.y<0);
 x.left.gamepad.axes=[0,0,1,1];r=x.sample(15);assert(Math.hypot(r.axes.navigate.x,r.axes.navigate.y)<=1.000001,'diagonal input has bounded length');
 x.right.gamepad.axes=[0,0,NaN,Infinity];r=x.sample(20);assert(!r.axes.orbit);
 x.left.gamepad.axes=[0,0,.1,0];assert(!x.sample(30).axes.navigate);
 x.set('RS',1);x.sample(40);x.set('RS',0);assert.equal(x.sample(50).events[0].action,'focus');
 x.set('LS',1);x.sample(60);x.set('LS',0);assert.equal(x.sample(70).events[0].action,'precision');groups++;
}
{
 const p=makeProfile();p.profileId='custom';p.bindings.model.find(r=>r[0]==='tool')[0]='precision';p.thresholds.triggerThreshold=.9;
 const x=setup(p);x.set('A',1);x.sample(10);x.set('A',0);assert.equal(x.sample(20).events[0].action,'precision');
 x.set('RT',.8);assert.equal(x.sample(30).events.length,0);x.set('RT',.91);assert.equal(x.sample(40).events[0].action,'select');
 x.set('RG',1);x.sample(50);p.bindings.model.find(r=>r[0]==='grab')[1]='hold:LG';let r=x.sample(60);
 assert(r.profileChanged&&r.resetRequired);assert(!r.held.grab);assert.equal(x.sample(70).events.length,0);groups++;
}
{
 const p=makeProfile();p.thresholds.triggerThreshold=.9;const x=setup(p);
 x.set('RT',.8);assert.equal(x.sample(10).events.length,0);
 p.thresholds.triggerThreshold=.6;assert.equal(x.sample(20).events.length,0);
 assert.equal(x.sample(30).events.length,0,'threshold decrease cannot select a trigger already held');
 x.set('RT',0);x.sample(40);x.set('RT',.8);assert.equal(x.sample(50).events[0].action,'select');groups++;
}
{
 const x=setup();x.set('RG',1);x.sample(10);x.sourceRight.tracked=false;let r=x.sample(20);
 assert(r.trackingLost&&r.resetRequired);assert.equal(r.events.length,0);assert(!r.held.grab);
 x.sourceRight.tracked=true;assert.equal(x.sample(30).events.length,0,'tracking regain cannot start a held grip');
 x.set('RG',0);x.sample(40);x.set('RG',1);assert.equal(x.sample(50).events[0].action,'grab');
 r=x.sample(5);assert(r.resetRequired);assert.equal(r.events.length,0);groups++;
}
{
 const p=makeProfile();p.bindings.model.push(['delete','tap:B','Unsafe unsupported operation'],['tool','tap:META','Reserved'],['palette','garbage','Bad'],['grab','tap:A','Invalid continuous action']);
 const x=setup(p);assert(x.api.inspect().invalidBindings.includes('delete'));assert.equal(x.api.inspect().invalidBindings.length,4);
 const right={handedness:'right',gamepad:{buttons:Array.from({length:6},(_,i)=>({value:i===1?1:0})),axes:[0,0]}};
 const api=context.create();let r=api.sample({time:0,sources:[{input:right,tracked:true}]});assert.equal(r.events.length,0,'new controller with held grip blocked');
 right.gamepad.buttons[1].value=0;api.sample({time:10,sources:[{input:right,tracked:true}]});right.gamepad.buttons[1].value=1;
 r=api.sample({time:20,sources:[{input:right,tracked:true}]});assert.equal(r.events[0].action,'grab');groups++;
}
{
 const p=makeProfile();p.bindings.model=p.bindings.model.filter(r=>!['tool-wheel','category-wheel'].includes(r[0]));
 p.bindings.model.push(['focus','double:A','Double focus'],['wireframe','sequence:X>A','Display sequence']);
 const x=setup(p);x.set('A',1);x.sample(10);x.set('A',0);assert.equal(x.sample(30).events.length,0);
 x.set('A',1);x.sample(70);x.set('A',0);let r=x.sample(100);assert.equal(r.events[0].action,'focus');
 assert.equal(r.events[0].hand,'right','release events retain the controller source');
 x.set('A',1);x.sample(500);x.set('A',0);x.sample(520);r=x.sample(820);assert.equal(r.events[0].action,'tool');
 x.set('X',1);x.sample(900);x.set('X',0);x.sample(920);x.set('A',1);r=x.sample(960);
 assert.equal(r.events[0].action,'wireframe');x.set('A',0);assert.equal(x.sample(980).events.length,0);groups++;
}
console.log('MODEL_VR_350_LIVE_INPUT_PROFILE_PASS '+groups+' groups');
