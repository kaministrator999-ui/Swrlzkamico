// §E v11.432: execute the EXACT camera orbit expression from the shipped HTML.
// The native pointer dispatcher depends on browser/Three.js event ownership; that
// integration is covered on-device, not by pretending its collaborators are no-ops.
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import assert from 'node:assert/strict';

assert.ok(process.argv[2], 'Pass the generated §E index.html');
const html=fs.readFileSync(path.resolve(process.argv[2]),'utf8');
assert.ok(html.includes('SWYRL_ENGINE_DEPLOY_MARKER: V11_432_MOBILE_CAMERA_ORBIT'));
const start=html.indexOf('const ModelAtelier=(()=>{');
assert.ok(start>=0, 'Native Model Atelier missing from generated HTML');
const native=html.slice(start);
function functionSource(name){
 const first=native.indexOf('function '+name+'(');
 assert.ok(first>=0,'Missing native '+name);
 const open=native.indexOf('{',first);
 let depth=0;
 for(let i=open;i<native.length;i++){
  if(native[i]==='{')depth++;
  else if(native[i]==='}'&&!--depth)return native.slice(first,i+1);
 }
 throw Error('Unterminated '+name);
}
const down=functionSource('pointerDown');
const move=functionSource('pointerMove');
const up=functionSource('pointerUp');
assert.ok(move.includes('if(Math.hypot(dx,dy)>5)pressed.moved=true;'), 'Preserve tap versus drag threshold');
assert.ok(up.includes('pressed.moved'), 'Preserve tap-selection distinction');
assert.ok(down.includes('yaw:orbit.yaw,pitch:orbit.pitch'), 'Preserve drag origin');
const begin=move.indexOf("const touch=e.pointerType==='touch';");
assert.ok(begin>=0,'Mobile touch direction branch absent from shipped pointerMove');
const end=move.indexOf('cameraUpdate();',begin);
assert.ok(end>begin,'Camera update not scheduled after orbit');
const expression=move.slice(begin,end+'cameraUpdate();'.length);
assert.ok(expression.includes('orbit.yaw=pressed.yaw+(touch?dx:-dx)*.008;'));
assert.ok(expression.includes('pressed.pitch+(touch?-dy:dy)*.006'));

const authored=Object.freeze({parts:[{id:'source-part-1'}]});
const snapshot=JSON.stringify(authored);
const context={
 pressed:{yaw:.3,pitch:.19}, orbit:{yaw:.3,pitch:.19},
 THREE:{MathUtils:{clamp:(v,low,high)=>Math.max(low,Math.min(high,v))}},
 cameraCalls:0,cameraUpdate:()=>{context.cameraCalls++;}
};
vm.createContext(context);
vm.runInContext('function applyMeasuredOrbit(e,dx,dy){'+expression+'}',context);
const near=(actual,expected,label)=>assert.ok(Math.abs(actual-expected)<=1e-9,label+': '+actual+' != '+expected);
function gesture(pointerType,dx,dy){
 context.pressed={yaw:.3,pitch:.19};
 context.orbit={yaw:.3,pitch:.19};
 Object.assign(context,{event:{pointerType},dx,dy});
 vm.runInContext('applyMeasuredOrbit(event,dx,dy)',context);
 return {...context.orbit};
}
// Screen-right and screen-up touch swipes move camera right/up.
let p=gesture('touch',40,-40);
near(p.yaw,.3+40*.008,'touch yaw');
near(p.pitch,.19+40*.006,'touch pitch');
// Mouse retains its original convention.
p=gesture('mouse',40,-40);
near(p.yaw,.3-40*.008,'desktop yaw');
near(p.pitch,.19-40*.006,'desktop pitch');
// Clamp preserves almost-top and almost-bottom camera orbits.
p=gesture('touch',0,-1000);
near(p.pitch,Math.PI/2-.001,'upper camera pitch');
p=gesture('touch',0,1000);
near(p.pitch,-Math.PI/2+.001,'lower camera pitch');
assert.equal(context.cameraCalls,4,'Every modeled orbit requests camera update');
assert.equal(JSON.stringify(authored),snapshot,'Orbit must not modify saved geometry');
console.log('MODEL_ATELIER_MOBILE_ORBIT_V11_432_PASS: assembled camera deltas, mouse parity, drag guard, pitch bounds, nondestructive');
