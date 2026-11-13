// Preserve the current v11.433 camera preferences in the v11.441 engine release.
import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';
assert.ok(process.argv[2],'Pass generated index.html');
const html=fs.readFileSync(process.argv[2],'utf8');
assert.ok(html.includes('SWYRL_ENGINE_DEPLOY_MARKER: V11_441_SATCHEL_VR_WORKFLOW'));
const mark='/* SE433_CAMERA_PREFS_START */',endmark='/* SE433_CAMERA_PREFS_END */';
const begin=html.indexOf(mark),end=html.indexOf(endmark,begin);
assert.ok(begin>=0&&end>begin,'Missing camera preferences runtime');
const state=new Map();
const context={localStorage:{getItem:k=>state.get(k)??null,setItem:(k,v)=>state.set(k,String(v))},cameraUpdate:()=>{},pressed:{yaw:.3,pitch:.19},orbit:{yaw:.3,pitch:.19},THREE:{MathUtils:{clamp:(n,a,b)=>Math.max(a,Math.min(b,n))}}};
vm.createContext(context);
vm.runInContext(html.slice(begin,end+endmark.length)+'\nthis.preferences=se433CameraPrefs;',context);
assert.equal(context.preferences.inverted,false,'Default should retain v11.432 direction');
const anchor="const touch=e.pointerType==='touch',invertTouch=touch&&se433CameraPrefs.inverted;";
const start=html.indexOf(anchor);
assert.ok(start>=0,'Shipped touch direction toggle missing');
const stop=html.indexOf('cameraUpdate();',start);
assert.ok(stop>start,'Camera update missing after gesture');
const expression=html.slice(start,stop+'cameraUpdate();'.length);
assert.ok(expression.includes('orbit.yaw=pressed.yaw+(touch&&!invertTouch?dx:-dx)*.008;'));
assert.ok(expression.includes('pressed.pitch+(touch&&!invertTouch?-dy:dy)*.006'));
vm.runInContext('function applyDrag(e,dx,dy){'+expression+'}',context);
function gesture(pointerType,dx,dy){
 context.pressed={yaw:.3,pitch:.19};context.orbit={yaw:.3,pitch:.19};
 context.event={pointerType};context.dx=dx;context.dy=dy;
 vm.runInContext('applyDrag(event,dx,dy)',context);return {...context.orbit};
}
const near=(v,w)=>assert.ok(Math.abs(v-w)<1e-9,v+' != '+w);
let p=gesture('touch',40,-40);near(p.yaw,.62);near(p.pitch,.43);
context.preferences.setInverted(true);
assert.equal(state.get('swrlz:e:modelStudio:invertTouchOrbit:v1'),'1');
p=gesture('touch',40,-40);near(p.yaw,-.02);near(p.pitch,-.05);
p=gesture('mouse',40,-40);near(p.yaw,-.02);near(p.pitch,-.05);
context.preferences.setInverted(false);
assert.equal(state.get('swrlz:e:modelStudio:invertTouchOrbit:v1'),'0');
p=gesture('touch',0,-1000);near(p.pitch,Math.PI/2-.001);
context.preferences.setInverted(true);
// Inverted pitch uses +dy, so a negative drag reaches the negative bound.
p=gesture('touch',0,-1000);near(p.pitch,-Math.PI/2+.001);
p=gesture('touch',0,1000);near(p.pitch,Math.PI/2-.001);
assert.ok(html.includes('Camera settings ▾')&&html.includes('modelAtelierInvertTouchOrbit'));
assert.ok(html.includes('const targetRadius=type=>type===\'touch\'?28:type===\'pen\'?18:12;'));
assert.ok(html.includes('touchRadius:28,mouseRadius:12'));
assert.ok(html.includes('coarse()?14:6'));
assert.ok(html.includes('se433CameraPrefs.install(panel);'));
console.log('MODEL_CAMERA_PREFERENCES_PRESERVED_V11_441_PASS: both orbit modes, persistence, unchanged desktop, pitch limits, gizmo grab');
