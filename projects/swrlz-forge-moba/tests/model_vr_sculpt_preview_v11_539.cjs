/* Targeted §E v11.539 integrity/behavior contracts.
 * Physical Quest 2 XR latency and frame timing require device acceptance.
 */
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const root=path.resolve(__dirname,'..');
const vr=fs.readFileSync(path.join(root,'runtime/model_vr_sculpt_preview_v11_539.js'),'utf8');
const patch=fs.readFileSync(path.join(root,'patches/v11_539_immersive_sculpt_load.py'),'utf8');
for(const token of [
 'SE539_IMMERSIVE_SCULPT_REPAIR_START','MAX_EDGES=480',
 'se350UpdateStroke=function(g)',"g.se538FinalSample=true",
 'se350UpdateBrush=function()', 'SphereGeometry(1,24,8',
 'RingGeometry(.975,1,48)','setDrawRange(0,count*2)',
 'se350Surface()?.inspect?.()?.selectedRegion','se517ProjectBusy',
 'se340ModelXRFrameCore=function(time,frame)',
 'se340CreateModelVRUI=function(options)',
 'tex.needsUpdate=true','stats.gridUpdates++'
])assert.ok(vr.includes(token),'Missing native XR implementation: '+token);
for(const token of [
 'SCULPT', 'const raw = a.array', 'const weights = g.maskWeights',
 'Smooth Witch Hat', 'se175StarterKinds',
 'SE539_IMMERSIVE_SCULPT_REPAIR_END','v11.539',
 'SE350_MODEL_VR_SURFACE_START'
])assert.ok(patch.includes(token),'Missing append-only source patch contract: '+token);
assert.ok(!/requestAnimationFrame\s*\(/.test(vr),'Do not create extra XR render loops');
assert.ok(!/loadProject\s*\(/.test(vr),'XR overlay must never own model persistence');
assert.ok(!/window\.SWRLZ_FORGE_BUILD\s*=/.test(vr),'Runtime overlay cannot forge release identity');
console.log('SE539_SCULPT_TARGETED_CONTRACTS_PASS');
