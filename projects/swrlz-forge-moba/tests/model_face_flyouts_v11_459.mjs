#!/usr/bin/env node
// §E 11.452: stage changes relocate original controls, not native mesh ownership.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const html=fs.readFileSync(process.argv[2],'utf8');
const runtime=fs.readFileSync(new URL('../runtime/model_face_flyouts_v11_452.js',import.meta.url),'utf8');
const css=fs.readFileSync(new URL('../runtime/model_face_flyouts_v11_452.css',import.meta.url),'utf8');
for(const token of [
 'SWYRL_ENGINE_DEPLOY_MARKER: V11_459_VIEWPORT_BOOT_GUARD',
 "window.SWRLZ_FORGE_BUILD={version:'v11.459'",
 'SE452_NATIVE_FACE_FLYOUTS_START','SE452_NATIVE_FACE_FLYOUTS_CSS_START',
 'SE451_GUIDED_FACE_WORKFLOW_START','SE450_ARMED_FACE_PREVIEW_START',
 'SE450_FACE_PREVIEW_VISIBILITY_START','SE446_PLANAR_FACE_TAP_START',
 'SE449_MODEL_DOCK_TOUCH_LAYOUT_START','SE445_VR_PROGRESSIVE_TOOLS_START',
 'SE430_MODEL_WORKSHOP_BRIDGE_START','SE430_MODEL_BEGINNER_UI_START'
])assert(html.includes(token),'Missing preserved engine/tool source '+token);
new vm.Script(runtime,{filename:'model_face_flyouts_v11_452.js'});
assert(runtime.includes('const previousInstall=se430BeginnerInstall;'));
assert(runtime.includes('se430BeginnerInstall=function(panel)'));
assert(runtime.includes("panel.querySelector('#se445ShapeQuick')"));
assert(runtime.includes("panel.querySelector('#se451FaceWorkflow')"));
for(const token of ['opsHolder.append(quick)','modHolder.append(guided)',
 'quickAnchor.after(quick)','guidedAnchor.after(guided)',
 "panel.dataset.se452Stage=value","stage('operations')","stage('modifiers')",
 "if(isPreview()){","window.SWYRL_ENGINE_GUIDED_FACE_451?.refresh?.()",
 "window.SWYRL_E_UNIFIED_TOOLS?.select?.('Topology','Manual mesh modeling')",
 "panel.querySelector('.se251-external-collapse')"])
 assert(runtime.includes(token),'Native flyout missing '+token);
assert(!runtime.includes('new THREE.Mesh('),'Menus must not duplicate geometry');
assert(!runtime.includes("window.dispatchEvent(new Event('resize'))"),'No camera resize');
assert(!runtime.includes('checkpoint('),'No new undo transactions in menu');
assert(!runtime.includes('setInterval('),'No polling render loop for menus');
for(const token of ['#se452FaceOperations','#se452FaceModifiers',
 '[data-se452-face-open="true"]','minmax(0,1fr) var(--se320-rail) 0px',
 '[data-se251-layout="compact"]','@media(max-width:900px)',
 '[data-se452-stage="modifiers"] #se452FaceOperations','[hidden]',
 'touch-action:pan-y','prefers-reduced-motion'])
 assert(css.includes(token),'Missing responsive/control style '+token);
// Native 451 amount slider, project/history and 450 model camera owner survive.
for(const token of ['se430BeginnerResult(api().preview(op,{amount:n}))',
 'se430BeginnerResult(api()?.apply())','se430BeginnerResult(api()?.cancel())',
 "se450PreviewOutlineAdd(record)","if(e.pointerType==='touch'&&atelierCameraPointerDown(e))",
 "se449ModelDockMetrics","se448ShapeQuickActivate(faceQuick,operation)"])
 assert(html.includes(token),'Previous native behavior lost: '+token);
let installed=0;
const ctx=vm.createContext({
 se430BeginnerInstall:()=>{installed++;return 'native';},
 window:{},
});
vm.runInContext(runtime,ctx);
assert.equal(ctx.se430BeginnerInstall(null),'native');
assert.equal(installed,1);
assert.equal(ctx.window.SWYRL_ENGINE_FACE_FLYOUTS_452.inspect().opened,false);
console.log('SE452_NATIVE_FACE_FLYOUTS_PASS: one native Face/amount/preview owner, 3 stages, phone fallbacks and no camera mutation');
