#!/usr/bin/env node
// §E v11.447: verify Face viewport orbit updates DURING drag, not at release,
// with bounded frame work, native touch invert, and preview geometry isolation.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const html=fs.readFileSync(process.argv[2],'utf8');
const begin='/* SE447_FACE_CAMERA_ORBIT_START */',end='/* SE447_FACE_CAMERA_ORBIT_END */';
const from=html.indexOf(begin),to=html.indexOf(end,from);
assert.ok(from>=0&&to>from,'Smooth orbit helper missing');
const src=html.slice(from,to+end.length);
let calls=0,frames=new Map(),nextFrame=1;
const orbit={yaw:.2,pitch:.1};
const se433CameraPrefs={inverted:false};
const canvas={setPointerCapture(){}};
const ctx=vm.createContext({
 orbit,se433CameraPrefs,
 THREE:{MathUtils:{clamp:(v,a,b)=>Math.max(a,Math.min(b,v))}},
 requestAnimationFrame:cb=>{const id=nextFrame++;frames.set(id,cb);return id;},
 cancelAnimationFrame:id=>frames.delete(id),
 cameraUpdate:()=>calls++,
 renderer:{domElement:canvas},
 atelierCameraPointerDown:()=>false,
 atelierCameraPointerMove:()=>false,
 atelierCameraPointerUp:()=>false
});
vm.runInContext(src+
 '\nthis.start=se447CameraOrbitStart;this.queue=se447CameraOrbitQueue;this.stop=se447CameraOrbitStop;',ctx);
const event=(x,y,pointerType='touch',pointerId=1)=>({clientX:x,clientY:y,pointerType,pointerId,button:0,cancelable:true,preventDefault(){}});
let g=ctx.start(event(100,150));
g.moved=true;ctx.queue(g,event(110,149));ctx.queue(g,event(130,130));
assert.equal(frames.size,1,'Multiple pointermoves must share one frame');
assert.equal(calls,0,'Do not update projection for every individual touch event');
for(const callback of frames.values())callback();
frames.clear();
assert.equal(calls,1,'Camera must update during drag (without pointerup)');
assert.ok(Math.abs(orbit.yaw-(.2+30*.008))<1e-12,'Default touchscreen drag follows finger');
assert.ok(Math.abs(orbit.pitch-(.1+20*.006))<1e-12);
ctx.stop(g,event(135,125));
assert.equal(calls,2);
assert.equal(g.active,false);
assert.equal(frames.size,0);
orbit.yaw=.2;orbit.pitch=.1;
se433CameraPrefs.inverted=true;
g=ctx.start(event(100,100));
g.moved=true;ctx.queue(g,event(120,110));
for(const callback of frames.values())callback();frames.clear();
assert.ok(Math.abs(orbit.yaw-(.2-20*.008))<1e-12,'Invert preference preserved');
assert.ok(Math.abs(orbit.pitch-(.1+10*.006))<1e-12);
ctx.stop(g,event(120,110),false);
orbit.yaw=.2;orbit.pitch=.1;
g=ctx.start(event(100,100,'mouse'));g.moved=true;
ctx.queue(g,event(120,110,'mouse'));
for(const callback of frames.values())callback();frames.clear();
assert.ok(Math.abs(orbit.yaw-(.2-20*.008))<1e-12,'Desktop orbit unchanged');
ctx.stop(g,event(120,110,'mouse'),false);
assert.ok(html.includes('if(d.moved&&atelierComponentTool===\'tap\')se447CameraOrbitQueue(d,e);'),'Face mode must schedule orbit on move');
assert.ok(html.includes('else se447CameraOrbitStop(d,e);'),'Release should finish, not start, orbit');
const a=html.indexOf('const priorPointer=pointerDown,priorPointerMove=pointerMove,priorPointerUp=pointerUp;');
const b=html.indexOf('const priorComponentUIRefresh=atelierComponentUIRefresh;',a);
assert.ok(a>=0&&b>a,'Native preview pointer wrappers missing');
let originalDown=0,originalMove=0,originalUp=0;
ctx.pointerDown=()=>originalDown++;
ctx.pointerMove=()=>originalMove++;
ctx.pointerUp=()=>originalUp++;
ctx.active={operation:'inset',data:{indices:[0,1,2]}};
ctx.ownedPreview=ctx.active;
vm.runInContext(html.slice(a,b),ctx);
ctx.pointerDown(event(100,100));ctx.pointerMove(event(142,126));
assert.equal(frames.size,1,'Preview touch drag must schedule smooth orbit');
for(const callback of frames.values())callback();frames.clear();
assert.ok(calls>=5,'Preview must orbit while still held, not only on release');
assert.equal(originalDown,0,'Preview navigation may not invoke mesh editing pointerdown');
assert.equal(originalMove,0,'Preview navigation may not invoke component editing');
ctx.pointerUp(event(142,126));
assert.equal(originalUp,0,'Preview release must not select another mesh');
assert.equal(ctx.active,ctx.ownedPreview,'Orbit must never mutate or cancel pending Inset preview');
ctx.active=null;
ctx.pointerDown(event(100,100));ctx.pointerMove(event(100,100));ctx.pointerUp(event(100,100));
assert.equal(originalDown,1,'Normal pointerdown remains delegated');
assert.equal(originalMove,1,'Normal pointermove remains delegated');
assert.equal(originalUp,1,'Normal pointerup remains delegated');
console.log('SE447_SMOOTH_ORBIT_PASS: live Face drag, one frame scheduling, invert/mouse semantics, preview isolation');
