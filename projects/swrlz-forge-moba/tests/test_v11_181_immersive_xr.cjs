// Focused invariants of the gateway. Headset tracking must be accepted on a real Quest.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),vm=require('node:vm');
const script=fs.readFileSync(path.join(__dirname,'../runtime/immersive_xr_gateway_v11_181.js'),'utf8');
new vm.Script(script);
assert.match(script,/renderer\.xr\.setSession\(requested\)/);
assert.match(script,/navigator\.xr\.requestSession\('immersive-vr',\{requiredFeatures:\['local-floor'\]\}\)/);
assert.match(script,/renderer\.xr\.getController\(index\)/);
assert.match(script,/se181XRRaycast\(record\)/);
assert.match(script,/selectActor\(hit\.object\)/);
assert.match(script,/if\(playing\|\|simulating\)return/);
assert.match(script,/se181XRActiveModel\(\)/);
assert.match(script,/se181XRExitPanel|se181XRMakeExitPanel/);
assert.doesNotMatch(script,/new THREE\.WebGLRenderer/);
assert.doesNotMatch(script,/requestAnimationFrame\(/);
assert.doesNotMatch(script,/dispatchEvent\(new (?:Mouse|Pointer)Event/);
console.log('XR_GATEWAY_STATIC_CONTRACT_PASS');
