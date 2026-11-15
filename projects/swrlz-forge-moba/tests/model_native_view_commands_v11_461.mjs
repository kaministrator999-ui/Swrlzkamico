#!/usr/bin/env node
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const source=fs.readFileSync(new URL('../runtime/model_native_view_commands_v11_460.js',import.meta.url),'utf8');
new vm.Script(source,{filename:'model_native_view_commands_v11_460.js'});
const calls=[],mesh={isMesh:true,userData:{atelierId:'cube',se455OriginalMaterial:{tag:'base'}},children:[],
 material:{tag:'clone',userData:{atelierViewportClone:true},dispose:()=>calls.push('clone-disposed')},
 remove(o){this.children.splice(this.children.indexOf(o),1);}};
const edge={name:'Viewport wireframe overlay',userData:{se455OwnedGeometry:true},geometry:{dispose:()=>calls.push('edge-disposed')},material:{dispose:()=>calls.push('edge-material-disposed')}};
mesh.children.push(edge);
let preview=false;
const ctx=vm.createContext({
 Map,Set,Object,window:{},
 modelRoot:{children:[mesh]},atelierViewGlobal:'solid',atelierViewOverrides:new Map(),
 atelierCameraInterior:false,
 se430ModelCamera:{inspect:()=>({view:'orbit'}),setView:v=>{calls.push('camera:'+v);return true;}},
 se430BeginnerAPI:()=>({inspect:()=>({preview:{active:preview}})}),
 partById:()=>({id:'cube'}),status:()=>{},
 atelierViewRebuild:()=>calls.push('rebuild'),
 atelierViewModeApply:(m,p)=>{calls.push('material:'+p.id);return m;},
 renderPreview:()=>calls.push('renderPreview')
});
vm.runInContext(source,ctx);
const bridge=ctx.window.SWYRL_ENGINE_MODEL_VIEW;
assert(bridge,'View bridge must be published from the native ModelAtelier closure');
assert.equal(bridge.inspect().mode,'solid');
assert.equal(bridge.setMode('overlay'),true);
assert.equal(bridge.inspect().mode,'overlay');
assert.deepEqual(calls,['rebuild'],'Idle switch delegates native rebuild exactly once');
calls.length=0;preview=true;
assert.equal(bridge.setMode('flat'),true);
assert.equal(bridge.inspect().mode,'flat');
assert(!calls.includes('rebuild'),'Preview mode must not reset/commit/rebuild topology');
assert.deepEqual(calls,['edge-disposed','edge-material-disposed','clone-disposed','material:cube','renderPreview']);
calls.length=0;
assert.equal(bridge.setCamera('front'),false,'Camera blocked during native preview');
assert.deepEqual(calls,[]);
preview=false;
assert.equal(bridge.setCamera('front'),true);
assert.equal(bridge.setCamera('three'),true);
assert.deepEqual(calls,['camera:front','camera:three']);
assert.equal(bridge.setMode('unknown'),false);
assert.equal(bridge.setCamera('unknown'),false);
assert.equal(bridge.setMode('flat'),true);
assert.equal(calls.length,2,'Same mode is an idempotent success');

if(process.argv[2]){
 const html=fs.readFileSync(process.argv[2],'utf8');
 for(const marker of ['SWYRL_ENGINE_DEPLOY_MARKER: V11_461_MODEL_EDGES_ORBIT_DOCK',
 "window.SWRLZ_FORGE_BUILD={version:'v11.461'",
 'SE460_NATIVE_VIEW_COMMANDS_START',
 'window.SWYRL_ENGINE_MODEL_VIEW=se460ModelView;',
 'window.SWYRL_ENGINE_MODEL_VIEW?.setCamera?.(view)',
 'window.SWYRL_ENGINE_MODEL_VIEW?.inspect?.()?.mode']){
 assert(html.includes(marker),'Missing integrated native View bridge: '+marker);
 }
 assert(!html.includes("const mode=()=>panel?.querySelector('#ViewportMode')?.value||'solid';"),
  'The guessed selector must not be used as source of truth');
 assert(html.includes('position:absolute;top:92px;left:8px;z-index:2600;'),
  'Popup must stack above native Zoom overlays on short mobile viewports');
 assert(html.includes('max-height:min(380px,calc(100dvh - 235px));overflow-y:auto;'),
  'Popup must remain scrollable on short mobile viewports');
}
console.log('SE460_NATIVE_VIEW_PASS: real model-state shading, preview safe, camera presets, invalid mode protections');
