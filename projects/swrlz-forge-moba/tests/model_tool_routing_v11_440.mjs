// Reuse native Three/editor fixtures; check the assembled dispatch layer that
// earlier isolated geometry tests could not exercise.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import {fileURLToPath,pathToFileURL} from 'node:url';
const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
assert(process.argv[2]&&process.argv[3],'Pass Three r169 ESM and assembled HTML');
const THREE=await import(pathToFileURL(path.resolve(process.argv[2])));assert.equal(THREE.REVISION,'169');
const html=fs.readFileSync(process.argv[3],'utf8'),read=n=>fs.readFileSync(path.join(ROOT,'runtime',n),'utf8');
function section(start,end){const a=html.indexOf(start),b=html.indexOf(end,a);assert(a>=0&&b>a,start);return html.slice(a,b+end.length);}
function reuse(file,start,end,globals){const s=fs.readFileSync(path.join(ROOT,'tests',file),'utf8'),a=s.indexOf(start),b=s.indexOf(end,a);assert(a>=0&&b>a);const c=vm.createContext({assert,fs,path,vm,THREE,ROOT,structuredClone,queueMicrotask,console,...globals});vm.runInContext(s.slice(a,b)+'\nthis.nativeFixture=fixture;',c);return c.nativeFixture;}
const surfaceFixture=reuse('model_vr_sculpt_draw_v11_350.mjs','const source=name=>','const positions=f=>');
const workshopFixture=reuse('model_studio_workshop_bridge_v11_430.mjs','const read=name=>','let groups=');
const route=section('/* SE436_VR_CUBE_EXTRUDE_START */','/* SE436_VR_CUBE_EXTRUDE_END */');
let groups=0;
function attachRoute(f){
 const s={session:true,scene:true,se430Manual:false,mode:'draw'},actions=[];
 Object.assign(f.ctx,{se340XR:s,se340VisibleSession:()=>true,currentProject:{modelAtelier:f.document()},
  ModelAtelier:{workshop:{inspect:()=>({selection:{partId:f.ctx.selection}})}},
  se340ModelXRAction:action=>{actions.push(action);if(action==='extrude')s.mode='extrude';if(action==='manual-mesh')s.se430Manual=true;return true;},
  se350Invalidate:()=>{},se340Notice:()=>{},se340SyncUI:()=>{},se340Publish:()=>{}});
 vm.runInContext(route+'\nthis.action=se340ModelXRAction;',f.ctx);return {s,actions,run:()=>f.ctx.action('extrude')};
}
for(const points of [[[0,0,0],[.5,0,0],[.5,.5,0],[0,.5,0]],[[0,0,0],[.5,0,0],[.5,.5,0],[.25,.25,0],[0,.5,0]]]){
 for(const depth of [.15,-.12]){
  const f=surfaceFixture();assert.equal(f.api.drawBegin({normal:[0,0,1]}).ok,true);for(const p of points)assert.equal(f.api.drawUpdate(p).ok,true);const drawn=f.api.drawEnd();assert.equal(drawn.ok,true);
  const original=structuredClone(f.document()),beforeHistory=f.counts().checkpoints,r=attachRoute(f);r.run();assert.equal(r.s.mode,'extrude');assert.equal(r.s.se430Manual,false);assert.deepEqual(r.actions,['extrude']);
  assert.equal(f.api.extrudeBegin(drawn.id).ok,true);assert.equal(f.api.extrudeUpdate(depth).ok,true);assert.deepEqual(structuredClone(f.document()),original);
  assert.equal(f.api.extrudeEnd(true).changed,true);assert.equal(f.counts().checkpoints,beforeHistory+1);
  const data=f.document().parts.find(p=>p.id===drawn.id).topologyMesh,audit=f.ctx.audit(data);assert.equal(audit.boundaryEdges,0);assert.equal(audit.nonManifoldEdges,0);assert.equal(audit.zeroAreaFaces,0);
  const thick=structuredClone(f.document());f.step(true);assert.deepEqual(structuredClone(f.document()),original);f.step(false);assert.deepEqual(structuredClone(f.document()),thick);groups++;
 }
}
{
 const f=workshopFixture();f.convert();const r=attachRoute(f);r.run();assert.deepEqual(r.actions,['manual-mesh','manual-extrude']);assert.equal(r.s.se430Manual,true);groups++;
}
{
 const f=workshopFixture();f.convert();f.top();const s={session:true,scene:true};
 Object.assign(f.ctx,{se340XR:s,ModelAtelier:{workshop:f.api},se340ModelXRAction:()=>true,se340Trigger:()=>{},se340CancelGesture:()=>{},se340BeginGesture:()=>{},se350Dispatch:()=>{},se340ModelXRInspect:()=>({}),se340VisibleSession:()=>true,se340SyncUI:()=>{},se340Publish:()=>{},se340Notice:()=>{}});
 vm.runInContext(section('/* SE430_MODEL_VR_MANUAL_WORKSHOP_START */','/* SE430_MODEL_VR_MANUAL_WORKSHOP_END */')+'\nthis.action=se340ModelXRAction;',f.ctx);
 s.se430Manual=true;s.se430Operation='subdivide';s.se430Amount=.25;
 for(let i=0;i<25;i++)f.ctx.action('manual-amount-minus');assert.equal(s.se430Amount,.025);
 assert.equal(f.api.preview('subdivide',{amount:s.se430Amount}).ok,true,'Minimum exposed amount must produce a valid native candidate');assert.equal(f.api.cancel().ok,true);groups++;
}
{
 const source=section('/* SE360_MODEL_VR_UI_START */','/* SE360_MODEL_VR_UI_END */');
 const factory=reuse('model_vr_ui_preservation_v11_430.mjs','function fixture(){','let groups=',{source,teaching:read('model_studio_teaching_v11_430.js')});
 const f=factory();f.ui.update({page:'accessory',accessoryActive:false});f.settle();
 for(const id of ['accessory-body','accessory-details','accessory-fit']){assert.equal(f.item(id).userData.se340Disabled,true,'Inactive accessory subpage must be disabled');assert.equal(f.ui.press(f.item(id)),false);}
 assert(f.canvases.some(c=>c.texts.some(t=>t.includes('Start a pouch preview first'))),'Disabled cards must explain prerequisite');
 f.ui.update({page:'accessory',accessoryActive:true});f.settle();for(const id of ['accessory-body','accessory-details','accessory-fit']){assert.equal(f.item(id).userData.se340Disabled,false);assert.equal(f.ui.press(f.item(id)),true);}f.ui.dispose();groups++;
}
console.log('MODEL_TOOL_ROUTING_440_PASS',JSON.stringify({groups,actualNativeOutlineShapes:2,bothDepthDirections:true,undoRedo:true,validSubdivideMinimum:true,accessoryPrerequisites:true}));
