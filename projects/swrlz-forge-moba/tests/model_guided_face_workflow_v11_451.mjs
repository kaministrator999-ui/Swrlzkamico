#!/usr/bin/env node
// §E v11.451: guided controls delegate to the existing transactional bridge.
import fs from 'node:fs';
import assert from 'node:assert/strict';
import vm from 'node:vm';
const html=fs.readFileSync(process.argv[2],'utf8');
const start='/* SE451_GUIDED_FACE_WORKFLOW_START */',end='/* SE451_GUIDED_FACE_WORKFLOW_END */';
const a=html.indexOf(start),b=html.indexOf(end,a);
assert(a>=0&&b>a,'Guided component must be bundled in generated editor');
const js=html.slice(a,b+end.length);
new vm.Script(js,{filename:'model_guided_face_workflow_v11_451.js'});
for(const text of [
 'se430BeginnerResult(api().preview(op,{amount:n}))',
 'se430BeginnerResult(api()?.apply())',
 'se430BeginnerResult(api()?.cancel())',
 'se451Advanced','se451AmountRange','se451AmountNumber',
 'data-se445-op','SWYRL_ENGINE_DEPLOY_MARKER: V11_451_GUIDED_FACE_WORKFLOW'
])assert(html.includes(text),'Missing guided native workflow integration: '+text);
assert(!html.includes("api.cancel('Amount changed. Preview again"),'Numeric adjustment must not cancel active preview');
assert(html.includes('window.SWYRL_ENGINE_GUIDED_FACE_451?.refresh?.()'),
 'Advanced amount control must sync the guided preview');
const css=html.slice(html.indexOf('/* SE451_GUIDED_FACE_STYLES_START */'),html.indexOf('/* SE451_GUIDED_FACE_STYLES_END */'));
assert(css.includes('[data-se451-guided=true]:not([data-se451-advanced=true]) #atelierContextFields'));
assert(css.includes('#se451FaceWorkflow[hidden]'));
assert(css.includes('#se451AmountRange'));
let installs=0,refreshes=0;
const box=vm.createContext({
 window:{SWYRL_E_CONTEXT:{current:()=>({})}},
 se430BeginnerState:{panel:null},
 se430BeginnerInstall:()=>{installs++;},
 se430BeginnerRefresh:()=>{refreshes++;},
 se430BeginnerAPI:()=>null,
 se430BeginnerAmount:()=>null
});
vm.runInContext(js,box);
assert.equal(box.window.SWYRL_ENGINE_GUIDED_FACE_451.version,'v11.451');
box.se430BeginnerInstall(null);box.se430BeginnerRefresh();
assert.equal(installs,1);assert.equal(refreshes,1);
assert(html.includes('se450PreviewOutlineClear(record)')&&html.includes('se450PreviewOutlineAdd(record)'),
 'Live updates must retain disposable native geometry outline lifecycle');
console.log('SE451_GUIDED_FACE_PASS: progressive panel, preview-only modifiers, native Apply/Cancel, advanced controls accessible');
