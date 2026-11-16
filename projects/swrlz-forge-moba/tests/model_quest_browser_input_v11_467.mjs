import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const path=process.argv[2];assert.ok(path,'Pass assembled candidate HTML');
const html=fs.readFileSync(path,'utf8');
const start=html.indexOf('function atelierCameraPointerUp('),end=html.indexOf('function atelierViewportInstall(',start);
assert(start>0&&end>start,'Native camera handlers are present');
const source=html.slice(start,end);
const state={
 atelierCameraTouches:new Map([[1,{x:10,y:10}],[2,{x:30,y:10}]]),
 atelierCameraConsumedTouches:new Set([1,2]),
 atelierCameraGesture:{separation:20},
 atelierCameraMousePan:null,
 atelierCameraTouchMetrics:()=>null,pressed:{moved:true},orbit:{yaw:0,pitch:0}
};
const sandbox=vm.createContext(state);
vm.runInContext(source+'\nthis.up=atelierCameraPointerUp;this.cancel=atelierCameraPointerCancel;',sandbox);
assert.equal(sandbox.up({pointerId:2,pointerType:'touch'}),true);
assert.equal(sandbox.atelierCameraTouches.size,1);
assert(sandbox.atelierCameraConsumedTouches.has(1),'Remaining pinch pointer must stay consumed');
assert.equal(sandbox.pressed,null,'Pinch release must not re-arm orbit');
assert.equal(sandbox.up({pointerId:1,pointerType:'touch'}),true);
assert.equal(sandbox.atelierCameraTouches.size,0);
assert.equal(sandbox.atelierCameraConsumedTouches.size,0);
sandbox.atelierCameraTouches.set(3,{x:1,y:1});
sandbox.atelierCameraTouches.set(4,{x:2,y:2});
sandbox.atelierCameraConsumedTouches.add(3);
sandbox.atelierCameraConsumedTouches.add(4);
sandbox.pressed={moved:true};
sandbox.cancel({pointerId:3,pointerType:'touch'});
assert(!sandbox.atelierCameraTouches.has(3));
assert(sandbox.atelierCameraConsumedTouches.has(4));
assert.equal(sandbox.pressed,null);
assert(html.includes("const tol=e.pointerType==='touch'?31:"),'Touch precision preserved');
assert(html.includes('se467World'),'Zoom-relative point tolerance installed');
assert(html.includes('se467QuestInstall(panel);'),'Native panel binding installed');
assert(html.includes('se467ViewportPointerAllowed(e)'),'DOM overlap viewport guard installed');
assert(html.includes('ring.hidden=selection.mode!==\'vertex\'&&!se467Extrude'),'Ring/arc controls accessible in Extrude');
assert(html.includes('face.hidden=!se467Extrude'),'Face extrusion controls accessible in Extrude');
assert(html.includes('data-se467-never-hide'),'Legacy narrow inspector cannot hide native tools');
assert(html.includes('function gamepadScroll(now)'),'Controller axis scrolling installed');
assert(html.includes('inspector.setPointerCapture'),'Controller drag scrolling installed');
assert(html.includes('SE467_QUEST_BROWSER_STYLES_START'));
console.log('SE467_QUEST_BROWSER_INPUT_PASS: pinch release/cancel, viewport priority, controller scrolling, visible extrude and ring tools');
