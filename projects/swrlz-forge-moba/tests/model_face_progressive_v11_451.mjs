#!/usr/bin/env node
// §E v11.451: native UI reuse, three-stage drawer wiring and mobile non-overlap.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const html=fs.readFileSync(process.argv[2],'utf8');
const script=fs.readFileSync(new URL('../runtime/model_face_progressive_v11_451.js',import.meta.url),'utf8');
const css=fs.readFileSync(new URL('../runtime/model_face_progressive_v11_451.css',import.meta.url),'utf8');
for(const s of [
 'SWYRL_ENGINE_DEPLOY_MARKER: V11_451_PROGRESSIVE_FACE_DOCK',
 'SE451_FACE_PROGRESSIVE_DOCK_START','SE451_FACE_PROGRESSIVE_DOCK_CSS_START',
 "window.SWRLZ_FORGE_BUILD={version:'v11.451'",
 'SE450_ARMED_FACE_PREVIEW_START','SE450_FACE_PREVIEW_VISIBILITY_START',
 'SE449_MODEL_DOCK_TOUCH_LAYOUT_START','SE445_VR_PROGRESSIVE_TOOLS_START',
 'SE430_MODEL_WORKSHOP_BRIDGE_START'
])assert(html.includes(s),'Missing native preserved integration '+s);
assert(html.indexOf('SE451_FACE_PROGRESSIVE_DOCK_START')>html.indexOf('SE430_MODEL_BEGINNER_UI_END'),
 'Menu hooks should be installed only after native workshop functions exist');
assert(html.includes('window.SWYRL_ENGINE_FACE_PROGRESSIVE_451'), 'Missing behavior inspection API');
assert(script.includes('const oldInstall=se430BeginnerInstall;'));
assert(script.includes('se430BeginnerInstall=function(panel)'), 'Must reuse native installer');
assert(script.includes('const workshop=panel.querySelector(\'#modelAtelierTopologyWorkshop\')'));
assert(script.includes('holder.append(workshop)'), 'Must move the original live workshop into stage three');
assert(script.includes('restoreNative()'), 'Native inspector must be recoverable');
assert(script.includes('se448ShapeQuickActivate(quick,operation)'), 'Inset/Extrude need actual native preview');
assert(script.includes("if(preview()){"),'Cannot hide pending Apply/Cancel');
assert(script.includes("amount.dispatchEvent(new Event('change',{bubbles:true}))"),
 'Amount slider must use native input event semantics');
assert(script.includes("const outcome=api()?.preview?.(op,{amount:value})"),'Slider must rebuild actual preview');
assert(script.includes('clearTimeout(amountTimer)'), 'Repeated input must not queue unbounded geometry rebuilds');
for(const op of ['inset','extrude','solidify','subdivide'])
 assert(script.includes('data-se451-op="'+op+'"'),'Missing face action '+op);
for(const id of ['modelAtelierWorkshopApply','modelAtelierWorkshopPreview','modelAtelierWorkshopCancel'])
 assert(css.includes('#'+id),'Existing native buttons must be visible in settings '+id);
assert(!script.includes('new THREE.Mesh(')&&!script.includes('checkpoint(')&&!script.includes('window.dispatchEvent(new Event(\'resize\'))'),
 'Face menu cannot allocate geometry, rewrite source or reset camera');
assert(css.includes('grid-template-columns:var(--se320-left) minmax(0,1fr) var(--se320-rail) 0px'),
 'Full inspector track must collapse in desktop Face mode');
assert(css.includes('[data-se251-layout="compact"][data-se451-face-open="true"]'),
 'Compact face mode must reclaim native inspector height');
assert(css.includes('[data-se451-stage="settings"] #se451FaceOperations'),
 'Compact Face operations and modifiers cannot overlap each other');
assert(css.includes('[hidden]{display:none!important}'),'Hidden panels must not capture model input');
assert(css.includes('touch-action:pan-y'),'Drawer must scroll without suppressing canvas gestures');
assert(css.includes('prefers-reduced-motion'),'Reduce motion needs supported settings');
// Exercise the hook without DOM to ensure native startup and non-modeling paths
// are not overwritten; the modeler installer calls mount only for real panels.
const events=[],ctx=vm.createContext({
 se430BeginnerInstall:p=>{events.push(p);return 'original';},window:{}
});
vm.runInContext(script,ctx);
assert.equal(ctx.se430BeginnerInstall(null),'original');
assert.equal(events.length,1);
assert.equal(ctx.window.SWYRL_ENGINE_FACE_PROGRESSIVE_451.inspect().active,false);
assert.equal(ctx.window.SWYRL_ENGINE_FACE_PROGRESSIVE_451.choose('inset'),undefined);
console.log('SE451_FACE_PROGRESSIVE_PASS: native preview/undo reused, three stages, safe mobile drawers, camera untouched');
