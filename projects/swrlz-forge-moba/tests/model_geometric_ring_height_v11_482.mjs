import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const root=new URL('../runtime/',import.meta.url);
const ring=fs.readFileSync(new URL('model_geometric_ring_v11_482.js',root),'utf8');
const drag=fs.readFileSync(new URL('model_ring_height_layout_v11_482.js',root),'utf8');
const css=fs.readFileSync(new URL('model_ring_height_layout_v11_482.css',root),'utf8');
const patch=fs.readFileSync(new URL('../patches/v11_482_geometric_ring_height.py',import.meta.url),'utf8');
new vm.Script(ring);new vm.Script(drag);
const host={};
const ctx=vm.createContext({window:{
 addEventListener(){},SWYRL_ENGINE_MODEL_WORKSHOP:null},
 document:{readyState:'loading',addEventListener(){}},
 se430BeginnerInstall(){},Math,Number,Array,Set,Map,Node:{TEXT_NODE:3},
 queueMicrotask:()=>{},console});
vm.runInContext(ring,ctx);
const api=ctx.window.SWYRL_ENGINE_GEOMETRIC_RING_482;
assert(api?.choose&&api?.selectCenter&&api?.sampleSlots);
const xyz=[],edges=[];
const push=(radius,count,y)=>{
 const start=xyz.length;
 for(let k=0;k<count;k++){const t=k*2*Math.PI/count;xyz.push([
   radius*Math.cos(t),y,radius*Math.sin(t)
 ]);}
 for(let k=0;k<count;k++)edges.push([start+k,start+(k+1)%count]);
 return start;
};
const outer=push(1,16,.5);
const inner=push(.6,16,.65);
const below=push(1,16,-.5);
const island=push(1,16,.5);
const middle=xyz.length;xyz.push([0,.7,0]);
for(let k=0;k<16;k++){edges.push([outer+k,inner+k]);
 edges.push([outer+k,below+k]);edges.push([middle,inner+k]);}
const top={vertices:xyz.map((_,i)=>i),edges};
const pos={getX:i=>xyz[i][0],getY:i=>xyz[i][1],getZ:i=>xyz[i][2]};
const geo={attributes:{position:pos}};
const ringResult=api.choose(top,geo,0,{kind:'rim',mode:'outline',plane:'xz'});
assert(ringResult.ok);
assert.equal(ringResult.vertexSlots.length,16,'Real planar radius selects entire circular band');
assert(ringResult.vertexSlots.every(i=>i<16),'No other radial layer, disconnected island, or rear shell');
assert(ringResult.vertexSlots.includes(0),'Touched vertex belongs to selected rim');
const fillResult=api.choose(top,geo,0,{kind:'rim',mode:'fill',plane:'xz'});
assert(fillResult.ok);
assert(ringResult.vertexSlots.every(id=>fillResult.vertexSlots.includes(id)),
 'Filled radius contains every outline vertex');
assert(fillResult.vertexSlots.includes(16),'Fill includes physically connected interior');
assert(!fillResult.vertexSlots.includes(48),'Fill excludes equal-radius disconnected island');
const centerResult=api.choose(top,geo,middle,{kind:'center',mode:'outline',plane:'xz',steps:1});
assert(centerResult.ok);
assert(centerResult.vertexSlots.length>=16,'Explicit center uses Euclidean circle');
assert(!centerResult.vertexSlots.includes(middle),'Outline omits center');
for(const token of [
 'getViewport','setPointerCapture','pointermove','pointerup','ArrowUp',
 'window.SWYRL_ENGINE_RING_HEIGHT_LAYOUT_482',
 '--se482-ring-left','--se482-ring-top',
 'window.addEventListener(\'swrlz:model-workshop-change\''
])assert(drag.includes(token),'Missing draggable height control: '+token);
for(const token of [
 '#se451FaceWorkflow','#se445ShapeQuick','#modelAtelierTopologyWorkshop',
 '#se482CircleControl','#se478RingHeightSlider',
 'transform:none!important','min-height:42px!important'
])assert(css.includes(token),'Missing responsive style: '+token);
for(const token of [
 'se482GeometricRing.choose(top,mesh.geometry,slot',
 'se482GeometricRing.noteRim(slot)',
 'se482GeometricRing.selectCenter(slot,options(mode))',
 'V11_482_GEOMETRIC_RING_HEIGHT'
])assert(patch.includes(token),'Missing assembled geometry source: '+token);
console.log('SE482_GEOMETRIC_STATIC_PASS: real circular outline, filled interior, center, rear/island separation, drag and inspector');
