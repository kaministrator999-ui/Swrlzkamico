'use strict';
/* Native pick and event arbitration contract — Quest menu vs empty 1.2m ray.
 * No real headset is simulated; a physical Quest 2 pass remains necessary.
 */
const fs=require('node:fs'),assert=require('node:assert/strict'),vm=require('node:vm'),path=require('node:path');
const root=path.resolve(__dirname,'..');
const code=fs.readFileSync(path.join(root,'runtime/model_vr_menu_stability_v11_420.js'),'utf8');
const patch=fs.readFileSync(path.join(root,'patches/v11_420_vr_tutorial_menu_interaction.py'),'utf8');
assert.match(patch,/if\(!s\.anchored/,'Viewer must be calibrated before quest positioning');
assert.match(patch,/box\.positioned\|\|box\.userPositioned/,'Once placed, do not follow camera/model');
assert.match(patch,/right,\.56/,'Fixed world-space panel placement');
assert.match(patch,/root\.visible=false/,'Uncalibrated quest must not flash at cube');
assert.match(patch,/box\.userPositioned=true/,'Grip drag must persist independent window');
assert.match(patch,/originQuat/,'Grip should permit independent world rotation');
assert.match(patch,/root\.scale\.setScalar\(1\.16\)/,'Native tool panel text must be physically larger');
assert.match(patch,/texture\.anisotropy=8/,'Native text texture needs angled viewing clarity');
assert.match(patch,/hoverAction/,'Tutorial needs visual hover feedback');

const scene={};
const button={visible:true,userData:{se340Action:'se413-next'},parent:null};
const background={visible:true,userData:{},parent:null};
const box={root:{visible:true,parent:scene,updateWorldMatrix(){},
 getWorldScale(){return {toArray(){return [1,1,1];}}}},
 buttons:[button],panel:background,folded:false,hoverAction:null,pressedAction:null,signature:'init'};
button.parent=box.root;background.parent=box.root;
const uiRoot={getWorldScale(){return {toArray(){return [1.16,1.16,1.16];}}}};
const ui={root:uiRoot};
const xr={scene,session:{},frameCount:10,controllers:[],se413Quest:box,ui};
let ordinary={distance:1.2,point:{fake:true}},seen=[];
const record={targetTracked:true,target:{},hit:null};
const ctx={
 window:{},
 THREE:{Vector3:function(){return {toArray(){return [1,1,1];}}}},
 se340XR:xr,
 se340VisibleSession:()=>true,
 se340Cast:()=>({intersectObjects(targets){
  const item=targets.find(t=>t===button);
  return item?[{object:item,distance:1.53,point:{x:1,y:0,z:-1}}]:[];
 }}),
 se340Hit:()=>ordinary,
 se340Trigger(){seen.push('trigger');},
 se340ModelXRFrameCore(){
  xr.frameCount++;record.hit=ctx.se340Hit(record,false);return 'rendered';
 }
};
xr.controllers=[record];vm.createContext(ctx);vm.runInContext(code,ctx,{filename:'menu420'});
assert.equal(ctx.se340Hit(record,false).quest,true,'Default 1.2m point must NOT block a real quest hit at 1.53m');
assert.equal(ctx.se340Hit(record,false).action,'se413-next');
ordinary={ui:true,action:'move',distance:.82,point:{real:true}};
assert.equal(ctx.se340Hit(record,false).action,'move','Nearer native console gets the pick');
ordinary={id:'mesh1',distance:.8,point:{}};
assert.equal(ctx.se340Hit(record,false).id,'mesh1','Real nearer model geometry remains clickable');
ordinary={distance:1.2,point:{fake:true}};
const before=box.signature;ctx.se340Trigger(record,false);
assert.equal(box.pressedAction,'se413-next');
assert.equal(box.pressedUntilFrame,23);
assert.notEqual(box.signature,before);
assert.deepEqual(seen,['trigger'],'Native trigger path remains the same');
ctx.se340ModelXRFrameCore();
assert.equal(box.hoverAction,'se413-next','XR hover ray resolves lesson action');
assert.equal(ctx.window.SWYRL_ENGINE_VR_MENU_STABILITY_420.inspect().panelParentIsScene,true);
for(let i=0;i<15;i++)ctx.se340ModelXRFrameCore();
assert.equal(box.pressedAction,null,'Temporary pressed state clears via native frames');
button.visible=false;assert.equal(ctx.se340Hit(record,false).quest,undefined,'Hidden buttons may not steal rays');
button.visible=true;box.root.visible=false;assert.equal(ctx.se340Hit(record,false).quest,undefined,'Closed/invisible panel must not receive input');
console.log('MODEL_VR_MENU_STABILITY_420_PASS: calibrated independent panel, native hover/press, gripped rotation, true ray hit beyond 1.2m, UI/model priority and hidden controls.');
