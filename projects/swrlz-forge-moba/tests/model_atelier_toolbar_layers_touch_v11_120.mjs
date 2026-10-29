import fs from 'node:fs';import vm from 'node:vm';import assert from 'node:assert/strict';
const source=fs.readFileSync('/tmp/se-v11120.mjs','utf8');
const css=fs.readFileSync('projects/swrlz-forge-moba/runtime/model_atelier_chrome_layer_v11_120.css','utf8');
function isolate(name){
 const st=source.indexOf('function '+name+'(');assert.ok(st>=0,'missing '+name);
 const b=source.indexOf('{',st);let depth=0;
 for(let i=b;i<source.length;i++){if(source[i]==='{')depth++;
  if(source[i]==='}'&&--depth===0)return source.slice(st,i+1);}
 throw Error('unclosed '+name);
}
const ctx={window:{matchMedia:()=>({matches:false})},requestAnimationFrame:f=>frames.push(f),console};
let frames=[],events={},moves=[];
vm.createContext(ctx);vm.runInContext([
 'seAtelierQuickstripSafeTop','seAtelierBottomRailCenter','seAtelierTopMenuExclusivity'
].map(isolate).join('\n'),ctx);
const top={getBoundingClientRect:()=>({bottom:226})};
const stage={getBoundingClientRect:()=>({top:38}),
 closest:()=>({querySelector:()=>top})};
assert.equal(ctx.seAtelierQuickstripSafeTop(stage),196);
assert.equal(ctx.seAtelierQuickstripSafeTop(null),50);
const rect=(left,width)=>({left,width});
const b={textContent:'Sculpt',getAttribute:()=>null,getBoundingClientRect:()=>rect(148,70)};
const selected={textContent:'Meshes',getAttribute:()=>null,getBoundingClientRect:()=>rect(220,70)};
const rail={dataset:{},getBoundingClientRect:()=>rect(10,400),
 contains:n=>n===b||n===selected,querySelectorAll:()=>[b,selected],
 addEventListener:(name,cb)=>events[name]=cb,scrollBy:delta=>moves.push(delta)};
ctx.seAtelierBottomRailCenter({querySelector:()=>rail});
assert.equal(frames.length,1);frames.shift()();
assert.equal(Math.round(moves[0].left),45);
events.click({target:{closest:()=>b}});frames.shift()();
assert.equal(Math.round(moves[1].left),-27);
const a={dataset:{},open:false,addEventListener:(t,cb)=>events.a=cb};
const v={dataset:{},open:false,addEventListener:(t,cb)=>events.v=cb};
ctx.seAtelierTopMenuExclusivity({querySelector:q=>q==='#seAtelierExportMenu'?a:v});
a.open=true;v.open=true;events.a();assert.equal(v.open,false);
v.open=true;events.v();assert.equal(a.open,false);
for(const name of ['#modelAtelierPanel #seAtelierViewMenu[open]',
 '#modelAtelierPanel #seAtelierExportMenu[open]',
 'justify-content:safe center!important',
 '#modelAtelierPanel{touch-action:manipulation}'])
 assert.ok(css.includes(name),name);
assert.ok(!css.includes('maximum-scale'));
assert.ok(!css.includes('touch-action:none!important'));
assert.ok(source.includes('const safeTop=seAtelierQuickstripSafeTop(stage);'));
assert.ok(source.includes('seAtelierBottomRailCenter(panel);'));
console.log('SE_V11120_TOP_LAYER_RAIL_CENTER_AND_SCOPED_DOUBLE_TAP_PASS');
