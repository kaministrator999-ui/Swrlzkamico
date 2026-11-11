'use strict';
/* v11.414: source-backed lesson tool identity and VR icon painter usage. */
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');
const root=path.resolve(__dirname,'..');
const source=fs.readFileSync(path.join(root,'runtime/model_satchel_tool_references_v11_414.js'),'utf8');
const ui=fs.readFileSync(path.join(root,'runtime/model_studio_vr_ui_v11_410.js'),'utf8');
const layout=fs.readFileSync(path.join(root,'runtime/studio_editor_layout_v11_320.js'),'utf8');
const atelier=fs.readFileSync(path.join(root,'runtime/model_atelier.js'),'utf8');
assert.match(ui,/function iconType\(id\)/);
assert.match(ui,/function icon\(c,type,x,y,size,color\)/);
for(const action of ['scale','move','rotate','duplicate','create-box','cameras','save-local']){
 if(action==='create-box')assert(ui.includes("['create-box','Cube']"));
 else if(action==='save-local')assert(ui.includes("['save-local','Save project']"));
 else assert(ui.includes(action),action);
}
for(const marker of ['data-se320-transform="move"','data-se320-transform="rotate"','data-se320-transform="scale"'])assert(layout.includes(marker),marker);
for(const id of ['modelAtelierAdd','modelAtelierDuplicate','modelAtelierKind','modelAtelierMaterial','modelAtelierColor'])assert(atelier.includes(id),id);
const sandbox={window:{},document:{}};
vm.runInNewContext(source,sandbox,{filename:'model_satchel_tool_references_v11_414.js'});
const api=sandbox.window.SWYRL_E_SATCHEL_BUTTON_GUIDE_414;
assert(api);
assert.deepEqual(Array.from({length:7},(_,i)=>Array.from(api.references(i),x=>x.key)),
 [['scale'],['add','shape','move'],['add','shape','scale'],['add','move','rotate'],
 ['duplicate','move'],['material','color'],['views','save']]);
const allowed=new Set(['scale','move','rotate','duplicate','create-box','cameras','save-local']);
const ctx={
 save(){},restore(){},beginPath(){},roundRect(){},fill(){},stroke(){},fillText(){},
 measureText(t){return {width:String(t).length*13};}
};
let icons=[];
const nativeVR={drawGuideIcon(c,action,x,y,size,color){
 assert(c===ctx);assert(allowed.has(action),'Guide icon was not a real VR action: '+action);
 icons.push(action);
}};
for(let i=0;i<7;i++){
 const step={...api.references(i)[0],index:i,task:'Add a part, Move and Rotate it, then Save Project.',
  hint:'Use Scale or Duplicate where available.'};
 icons=[];
 assert.equal(api.renderVR(ctx,step,nativeVR),true);
 api.vrTask(ctx,step,nativeVR);
 api.vrHint(ctx,step,nativeVR);
 if(i!==5)assert(icons.length>=1,'No VR control reference at step '+i);
 if(i===5)assert(!api.references(i).some(ref=>ref.vr),'Material/Color cannot imply unsupported VR edit actions');
}
assert(source.includes('native.textContent'),'Flat miniature must reuse the real DOM button label');
assert(source.includes('getComputedStyle(native)'),'Flat miniature must sample native button appearance');
assert(!source.includes('addEventListener('),'Read-only control examples must not steal native input');
console.log('SATCHEL_NATIVE_BUTTON_REFERENCES_PASS: 7 lesson steps, real flat control IDs, VR icon actions, no fake materials.');
