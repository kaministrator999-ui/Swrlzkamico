'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs');
const vm=require('node:vm'),path=require('node:path');
const script=fs.readFileSync(path.join(__dirname,'../runtime/sheep_xr_guest_sync_v11_381.js'),'utf8');
let now=1000,visual=0,raf=0,oldGuestControls=0,xrFrames=0,cameraSaw=0;
let pausedFlag=false,stick={x:.6,z:-.8,strength:1},packets=[];
const u={id:'sheep-2',pos:{x:0,z:0},kind:'sheep',captured:false};
const world={units:[u],simulate:false,winner:null,elapsed:12,rules:{headstart:8}};
const conn={open:true};
const c={
 performance:{now:()=>now},
 renderer:{xr:{isPresenting:false}},se181XR:{session:null},
 currentProject:{kind:'sheep-tag'},stSession:world,paused:false,
 se150Match:{active:true,role:'guest',matchId:'match-1',roomId:'room-1'},
 se151:{guestConn:conn},se152:{assigned:u.id,received:1},
 se154:{clientSeq:15,tx:0},window:{},
 se152Guest:()=>conn.open,
 se152Send:(dest,pkt)=>{assert.strictEqual(dest,conn);packets.push(pkt);},
 se211Paused:()=>pausedFlag,
 se199StickIntent:()=>({...stick}),
 se152GuestFrame:()=>{visual++;u.pos.x+=1;},
 se156GuestFrameOnce:()=>{raf++;},
 se152GuestControls:()=>{oldGuestControls++;},
 se193XRFrame:()=>{xrFrames++;cameraSaw=u.pos.x;},
 se152StopWorld:()=>{},se193XRCleanup:()=>{}
};
vm.runInNewContext(script,c,{filename:'sheep_xr_guest_sync_v11_381.js'});
// Browser-only guest keeps its existing rendering and touch sender.
c.se156GuestFrameOnce();c.se152GuestControls();c.se193XRFrame();
assert.equal(raf,1);assert.equal(visual,0);assert.equal(oldGuestControls,1);assert.equal(packets.length,0);
c.renderer.xr.isPresenting=true;c.se181XR.session={};
c.se156GuestFrameOnce();
assert.equal(raf,1,'the normal browser guest RAF must not double XR interpolation');
c.se193XRFrame();
assert.equal(visual,1,'new XR guest frame must animate replicated sheep');
assert.equal(cameraSaw,1,'VR camera observes newly interpolated guest position');
assert.equal(packets.length,1);
assert.equal(packets[0].kind,'guest-stick-v2');
assert.equal(packets[0].seq,16);assert.equal(packets[0].x,.6);
assert.equal(packets[0].z,-.8);assert.equal(packets[0].strength,1);
assert.equal(packets[0].roomId,'room-1');assert.equal(packets[0].matchId,'match-1');
c.se152GuestControls();assert.equal(packets.length,1,'no duplicate XR send from browser timer');
now+=78;c.se152GuestControls();
assert.equal(packets.length,2);assert.equal(packets[1].seq,17);
stick={x:0,z:0,strength:0};now+=1;
c.se193XRFrame();
assert.equal(packets.length,3,'release sends immediately');
assert.equal(packets[2].strength,0);
const before=c.window.SWYRL_ENGINE_SHEEP_XR_GUEST_381.diagnose();
assert.equal(before.visualSyncFrames,2);assert.equal(before.browserFramesSuppressedInXR,1);
assert.equal(before.lastAppliedSnapshot,1);
// XR overlay suppresses input and interpolation but preserves the network room.
pausedFlag=true;stick={x:1,z:0,strength:1};now+=100;
c.se193XRFrame();
assert.equal(visual,2,'no guest updates during genuine XR overlay interruption');
assert.equal(packets.at(-1).strength,0,'do not drive a sheep from hidden controller state');
pausedFlag=false;now+=85;c.se193XRFrame();
assert.equal(packets.at(-1).strength,1);
assert.equal(visual,3);
// On exit, flush a neutral packet; subsequent browser control path resumes.
c.se193XRCleanup();
assert.equal(packets.at(-1).strength,0);
c.renderer.xr.isPresenting=false;c.se181XR.session=null;
c.se156GuestFrameOnce();c.se152GuestControls();
assert.equal(raf,2);assert.equal(oldGuestControls,2);
c.se193XRFrame();assert.equal(visual,3);
// Hosting in VR must not use guest-only code, preserving local game input.
c.renderer.xr.isPresenting=true;c.se181XR.session={};
c.se150Match.role='host';
c.se156GuestFrameOnce();c.se152GuestControls();c.se193XRFrame();
assert.equal(raf,3);assert.equal(oldGuestControls,3);assert.equal(visual,3);
// World teardown resets VR guest state for the next lobby/match.
c.se150Match.role='guest';c.se152StopWorld();
const after=c.window.SWYRL_ENGINE_SHEEP_XR_GUEST_381.diagnose();
assert.equal(after.lastInputSeq,0);assert.equal(after.lastStickStrength,0);
console.log('v11.381 Quest-as-guest vs phone-host: host snapshots, WebXR interpolation, controller TX, timer dedupe, release, overlay and browser fallbacks PASS');
