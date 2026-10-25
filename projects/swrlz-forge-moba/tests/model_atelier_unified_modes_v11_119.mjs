import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';
const built=fs.readFileSync('/tmp/se-v11119.mjs','utf8');
function fn(name){
 const i=built.indexOf('function '+name+'(');
 assert.ok(i>=0,'missing '+name);
 const b=built.indexOf('{',i);let n=0;
 for(let j=b;j<built.length;j++){
  if(built[j]==='{')++n;
  else if(built[j]==='}'&&!--n)return built.slice(i,j+1);
 }
 throw Error('unclosed '+name);
}
const names=['seAtelierModeNames','seAtelierModeChoose',
 'seAtelierModeToolbarInstall','seAtelierTopBarArrange'];
const categoryModes={
 Sculpt:['Brush & falloff','Precision circle cut','Brush placement','Brush shape'],
 Topology:['Edge, vertex & face','Mesh audit'],Meshes:['Select & organize','Transform'],
 Appearance:['Materials & colors'],Face:['Portrait & anatomy','Facial landmarks']
};
let selected=null;
const api={
 groups:()=>categoryModes,
 activate:(category,mode)=>{
  if(!categoryModes[category])return false;
  selected={category,mode:mode||categoryModes[category][0]};return true;
 },
 current:()=>({group:selected?.category,operation:selected?.mode})
};
const inspector={attrs:{},setAttribute(k,v){this.attrs[k]=v;}};
const panel={classes:new Set(['atelier-tools-closed']),
 classList:{
  add(s){panel.classes.add(s)},remove(s){panel.classes.delete(s)},
  contains(s){return panel.classes.has(s)}
 },
 querySelector:q=>q==='.atelier-inspector'?inspector:null
};
const context={window:{SWYRL_E_CONTEXT:api},console,document:{}};
vm.createContext(context);
vm.runInContext(names.map(fn).join('\n'),context);
const modes=context.seAtelierModeNames(api,'Sculpt');
assert.deepEqual(Array.from(modes),categoryModes.Sculpt);
assert.deepEqual(Array.from(context.seAtelierModeNames(api,'Nothing')),[]);
assert.equal(context.seAtelierModeChoose(panel,'Sculpt','Precision circle cut'),true);
assert.deepEqual(selected,{category:'Sculpt',mode:'Precision circle cut'});
assert.equal(panel.classes.has('se-inspector-mode-view'),true);
assert.equal(panel.classes.has('atelier-tools-closed'),false);
assert.equal(inspector.attrs['aria-hidden'],'false');
assert.equal(context.seAtelierModeChoose(panel,'Nothing'),false);
assert.ok(built.includes("inspector.append(ui);"),'new sheet not embedded in inspector');
assert.ok(built.includes("panel.classList.toggle('atelier-mobile-context-mode',false)"),'native inspector still hidden by sheet');
assert.ok(built.includes("seAtelierModeToolbarInstall(panel);"),'mode toolbar not installed');
assert.ok(built.includes("seAtelierTopBarArrange(panel);"),'export/camera toolbar not installed');
assert.ok(built.includes("if(open&&lastChoice===label){setOpen(true);return;}"),'category reselect closes inspector');
assert.ok(built.includes("viewMode='all';showOps();"),'submodes remain inaccessible in Quick mode');
assert.ok(built.includes("const modeBar=document.createElement('nav');"),'no secondary mode bar');
assert.ok(built.includes("button.addEventListener('click'"),'mode toolbar actions not wired');
assert.ok(built.includes("const exports=buttons.filter(b=>b!==save&&b!==close);"),'export buttons lost');
assert.ok(built.includes("menu.append(summary,cameras);"),'camera views not preserved');
assert.ok(built.includes("#modelAtelierPanel.se-inspector-mode-view .atelier-inspector"),'native panel mobile layout absent');
assert.ok(built.includes("#modelAtelierPanel .se-atelier-modes[hidden]"),'mode rail missing hidden state');
assert.ok(built.includes("#modelAtelierPanel.se-inspector-mode-view #atelierContextWorkbench"),'inline context display not styled');
console.log('SE_V11119_SINGLE_MOVABLE_INSPECTOR_MODE_RIBBON_AND_TOP_MENUS_PASS');
