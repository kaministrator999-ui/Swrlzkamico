// §E v11.211 – Meta system Camera focus loss, throttled callbacks and safe return.
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
let now=1000,oldFrames=0,oldInputFrames=0,oldMoveWrites=0,originalStart=0,
 originalCleanup=0,worldRefresh=0,radialHides=0,panelDrops=0,gripDrops=0;
const listeners=new Map();
const session={
 visibilityState:'visible',
 addEventListener:(name,fn)=>listeners.set(name,fn),
 removeEventListener:(name,fn)=>{if(listeners.get(name)===fn)listeners.delete(name)},
 fire(){listeners.get('visibilitychange')?.()}
};
const makeObject=visible=>({visible});
const drawA=makeObject(true),drawB=makeObject(false),oldMap=makeObject(true);
const panel1=makeObject(true),panel2=makeObject(false),rim=makeObject(true);
const xrRecords=['left','right'].map((side,index)=>({
 index,input:{handedness:side,gamepad:{buttons:Array.from({length:6},()=>({pressed:false}))}},
 se192:{actionHeld:false}
}));
const obj={
 console,Math,performance:{now:()=>now},
 se181XR:{session,controllers:xrRecords},
 renderer:{xr:{isPresenting:true}},
 se193:{lastFrame:50,held:new Map()},
 se195:{lastFrame:50,radial:rim,referenceOffset:{x:1,y:2,z:3},
  referenceBase:{id:'true WebXR native base'},rigReady:true},
 se192:{lastFrame:50},se207:{lastAt:100,grabbing:false},
 se204:{wheel:{root:makeObject(true)},buttons:{left:{held:true,opened:true},
  right:{held:true,opened:true}}},
 se210UI:{panels:new Map([['camera',{root:panel1}],['metrics',{root:panel2}]]),
  lastAt:50,held:true,grabbing:false},
 se208:{props:[drawA,drawB]},se210World:{meshes:[oldMap],lastReportAt:50},
 se206:{mesh:makeObject(true)},
 se211ActiveWorld:true,
 se192InputRecord:side=>xrRecords.find(r=>r.input.handedness===side),
 se192Pressed:(record,i)=>!!record?.input?.gamepad?.buttons?.[i]?.pressed,
 se210Held:(record,side)=>!!record?.input?.gamepad?.buttons?.[side==='left'?3:4]?.pressed,
 se204WheelHide:()=>{radialHides++;obj.se204.wheel=null},
 se207EndGrab:()=>{gripDrops++;obj.se207.grabbing=false},
 se210PanelRelease:()=>{panelDrops++;obj.se210UI.grabbing=null},
 se210WorldRefreshVisibility:()=>{worldRefresh++},
 se193XRFrame:()=>{oldFrames++},
 se192VRFrame:()=>{oldInputFrames++},
 se195MoveRig:()=>{oldMoveWrites++;return true},
 se193XRStart:()=>{originalStart++},
 se193XRCleanup:()=>{originalCleanup++},
 window:{}
};
vm.createContext(obj);
vm.runInContext(fs.readFileSync(path.join(__dirname,'..','runtime',
 'engine_xr_meta_os_overlay_stability_v11_211.js'),'utf8'),obj);
const d=()=>obj.window.SWYRL_ENGINE_QUEST_OS_STABILITY_211.diagnose();
const local=()=>vm.runInContext('se211',obj);
const core=()=>obj.se193XRFrame();
const input=()=>obj.se192VRFrame();
const framesFor=ms=>{for(let k=0;k<Math.ceil(ms/16);k++){now+=16;core()}};
const focus=v=>{session.visibilityState=v;session.fire()};
const hold=(side,index,v)=>{obj.se192InputRecord(side).input.gamepad.buttons[index].pressed=v};
assert.equal(d().sessionState,'visible');
assert.equal(d().nativeQuestCompositorControlled,false);
obj.se193XRStart();
assert.equal(originalStart,1);
assert.ok(listeners.has('visibilitychange'));
core();input();
assert.equal(oldFrames,1);
assert.equal(oldInputFrames,1);
assert.equal(obj.se195MoveRig(1,0,0),true);
assert.equal(oldMoveWrites,1);
assert.equal(rim.visible,true);
// Native Quest Camera menu gains focus: WebXR reports blurred.
obj.se207.grabbing=true;
obj.se210UI.grabbing={panel:'camera'};
focus('visible-blurred');
assert.equal(d().sessionState,'visible-blurred');
assert.equal(d().overlayBlurEvents,1);
assert.equal(d().cosmeticsHidden,7,'only app HUD + decorative scene items hidden');
assert.equal(drawA.visible,false);assert.equal(drawB.visible,false);
assert.equal(oldMap.visible,false);assert.equal(panel1.visible,false);
assert.equal(panel2.visible,false);assert.equal(rim.visible,false);
assert.equal(obj.se206.mesh.visible,false);
assert.ok(radialHides>=1);
assert.equal(gripDrops,1);assert.equal(panelDrops,1);
assert.equal(obj.se204.buttons.left.held,false);
assert.equal(obj.se204.buttons.right.held,false);
assert.equal(obj.se207.grabbing,false);
assert.equal(obj.se210UI.grabbing,null);
assert.equal(obj.se195MoveRig(1,0,0),false,
 'no camera reference writes under the Meta OS camera overlay');
assert.equal(oldMoveWrites,1);
now+=150;core();input();
assert.equal(oldFrames,1,'game XR menu/frame adapters suspended');
assert.equal(oldInputFrames,1,'controller targeting stopped while OS owns focus');
assert.equal(d().skippedGameXRFrames,1);
assert.equal(d().skippedControllerXRFrames,1);
assert.equal(d().blockedCameraReferenceWrites,1);
const reference=obj.se195.referenceBase;
const offset=obj.se195.referenceOffset;
focus('hidden');
assert.equal(d().overlayHiddenEvents,1);
assert.equal(d().cosmeticsHidden,7);
assert.equal(oldFrames,1,'OS hidden can stop browser callbacks entirely');
now+=800; // No XR callback while Meta native UI is foregrounded.
hold('right',4,true);
hold('left',3,true);
focus('visible');
assert.equal(d().overlayReturns,1);
assert.ok(d().overlayTimeMs>=950);
assert.equal(obj.se195.referenceBase,reference,
 'headset referenceBase preserved, not reset or rebased');
assert.equal(obj.se195.referenceOffset,offset);
assert.equal(obj.se193.lastFrame,now);
assert.equal(obj.se195.lastFrame,now);
assert.equal(obj.se192.lastFrame,now);
assert.equal(obj.se210World.lastReportAt,now);
assert.equal(d().waitingForButtonRelease,true);
now+=400;core();input();
assert.equal(oldFrames,1,'held A/X and alternate stick-click cannot fire after OS return');
assert.equal(oldInputFrames,1);
assert.equal(d().blockedCameraReferenceWrites,1);
assert.equal(obj.se195MoveRig(1,0,0),false);
assert.ok(d().blockedStaleControllerInputs>=1);
hold('right',4,false);hold('left',3,false);
now+=2;core();input();
assert.equal(oldFrames,2,'normal XR game update after release');
assert.equal(oldInputFrames,2);
assert.equal(d().waitingForButtonRelease,false);
assert.equal(obj.se195MoveRig(1,0,0),true);
assert.equal(oldMoveWrites,2);
assert.equal(vm.runInContext('se211CameraSoftReturn()',obj),true);
assert.equal(d().cosmeticsHidden,7,'lightweight scene remains hidden for brief recovery');
assert.ok(local().returnUntil>0);
framesFor(900);
assert.equal(d().cosmeticsHidden,0);
assert.equal(drawA.visible,true);
assert.equal(drawB.visible,false,'original hidden geometry stays hidden');
assert.equal(oldMap.visible,true);
assert.equal(panel1.visible,true);
assert.equal(panel2.visible,false,'closed floating panels stay closed');
assert.equal(rim.visible,true);
assert.equal(obj.se206.mesh.visible,true);
assert.ok(worldRefresh>=1);
assert.ok(d().cosmeticRestores>=1);
assert.equal(vm.runInContext('se211CameraSoftReturn()',obj),false);
// Repeated 170ms XR-gap detector: Meta sometimes does not report blur at all.
const before=oldFrames,gaps=d().callbackGaps;
now+=320;core();
assert.equal(oldFrames,before,'large callback gap triggers camera/input recovery');
assert.equal(d().callbackGaps,gaps+1);
assert.ok(d().largestGapMs>=320);
assert.equal(d().lastCause.includes('XR callback gap'),true);
assert.equal(d().overlayBlurEvents,1,'gap is not misreported as explicit Meta blur');
assert.equal(obj.se195MoveRig(1,0,0),false);
framesFor(352);
assert.ok(oldFrames>before);
assert.equal(obj.se195MoveRig(1,0,0),true);
assert.equal(obj.se204.buttons.right.held,false);
assert.equal(obj.se204.buttons.left.held,false);
assert.equal(obj.se195.referenceBase,reference,'gap recovery preserves reference base');
assert.equal(obj.se195.referenceOffset,offset,'gap recovery preserves cumulative offset');
assert.equal(d().recoveryDtResets>=2);
assert.equal(d().cosmeticSuspends>=2,true);
framesFor(900);
assert.equal(drawA.visible,true);
assert.ok(d().cosmeticRestores>=2);
const skipOld=oldFrames;
focus('visible-blurred');now+=100;core();
assert.equal(oldFrames,skipOld);
focus('visible');now+=400;core();
assert.equal(oldFrames,skipOld+1,'repeated Meta menu cycles do not wedge XR');
framesFor(1312);
assert.equal(d().cosmeticsHidden,0);
obj.se193XRCleanup();
assert.equal(originalCleanup,1);
assert.equal(listeners.size,0,'remove native WebXR visibilitychange listener on exit');
assert.equal(d().sessionState,'visible');
assert.equal(d().cosmeticsHidden,0);
assert.equal(d().waitingForButtonRelease,false);
const patch=fs.readFileSync(path.join(__dirname,'..','patches',
 'v11_211_quest_os_camera_overlay_stability.py'),'utf8');
assert.ok(patch.includes('const maxStep=timeStep*(se211CameraSoftReturn()?3.2:13);'));
assert.ok(patch.includes('V11_211_QUEST_OS_CAMERA_OVERLAY_STABILITY'));
assert.equal(patch.includes('renderer.xr.setReferenceSpace('),false,
 'no force rebase while Meta OS Camera is open');
console.log(JSON.stringify({pass:true,checks:58,blurEvents:d().overlayBlurEvents,
 resumed:d().overlayReturns,frameGaps:d().callbackGaps,
 blockedWrites:d().blockedCameraReferenceWrites,
 skippedXR:d().skippedGameXRFrames,skippedInput:d().skippedControllerXRFrames,
 finalDisplays:d().cosmeticsHidden}));
