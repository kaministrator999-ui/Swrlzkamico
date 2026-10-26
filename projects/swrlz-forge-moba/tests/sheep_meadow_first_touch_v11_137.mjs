import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const root='projects/swrlz-forge-moba/';
const assembled=process.env.SE_ASSEMBLED_HTML;
assert.ok(assembled,'Run this integration test against the sealed assembled engine HTML');
const html=fs.readFileSync(assembled,'utf8');
assert.ok(html.includes('SWYRL_ENGINE_DEPLOY_MARKER: V11_137_MEADOW_FIRST_SHEEP_BUILD_DRAG'));
const start=html.indexOf('const stBuildInput={pointer:null,element:null');
const end=html.indexOf('const stRecoverChooseBase=stUiChooseBuild;',start);
assert.ok(start>0&&end>start,'native build-pointer lifecycle must exist');
const lifecycle=html.slice(start,end);
assert.ok(lifecycle.includes("if(stBuildInput.source==='skill'&&event.pointerType!=='mouse')return;"),'phone button press does not move ghost');
assert.ok(lifecycle.includes("if(source==='skill'&&event.pointerType!=='mouse'){"),'all phone skill releases select only');
assert.ok(lifecycle.includes('st135SeedSheepGhost();'),'skill selection restores visible sheep-centered ghost');
assert.ok(lifecycle.includes("if(source==='meadow'&&!stBuildInput.moved)st135TapPlacement(event);"),'tap on meadow still selects exact site');
assert.ok(lifecycle.includes('st135CommitPreview();'),'native order uses preview, not button/finger ray');
assert.ok(lifecycle.includes('if(repeat&&stSession&&!stSession.winner)'),'Rapid repeat is preserved');
const listeners={},docListeners={},seen=[];
const makeElement=name=>({
 name,dataset:{stSkill:'st-farm'},disabled:false,captured:null,
 contains(node){return node===this;},
 hasPointerCapture(id){return this.captured===id;},
 setPointerCapture(id){this.captured=id;},
 releasePointerCapture(){this.captured=null;},
 closest(selector){return name==='skill'&&selector.includes('data-st-skill')?this:null;}
});
const skill=makeElement('skill'),viewport=makeElement('viewport'),empty={closest(){return null;}};
const sheep={id:'sheep',kind:'sheep',captured:false,pos:{x:10,z:20}};
const state={role:'sheep',controlledId:'sheep',resources:{sheep:100},units:[sheep],winner:null,simulate:false};
let stUi={shown:true,build:null,preview:null,placement:null,drag:null};
let ghostVisible=false,commands=[],pointerAimCalls=0,seedCount=0;
const tp={gesture:null,touchPointers:new Set(),blockedPointers:new Set(),valid:false};
const ctx={
 console,window:{addEventListener(type,fn){(listeners[type]??=[]).push(fn);}},
 document:{addEventListener(type,fn){(docListeners[type]??=[]).push(fn);}},
 $:id=>id==='viewport'?viewport:null,
 stSession:state,stUi,stTouchPlacement:tp,
 stBuildingConfig:()=>({cost:0}),stUiBuildNames:{'st-farm':'Free House'},stUiBuildButtons:[],
 stUiFeedback(x){seen.push(x);},stRefreshHUD(){},
 stBuildDragReset(){},stTouchPlacementReset(){tp.gesture=null;tp.valid=false;},
 stTouchPlacementHide(){ghostVisible=false;},stUiClearPreview(){stUi.preview=null;stUi.placement=null;ghostVisible=false;},
 stTouchPlacementEnabled(){return !!stUi.build;},paused:false,
 stUiChooseBuild(kind){stUi.build=kind;stUi.preview={visible:true};stUi.placement=null;ghostVisible=true;},
 st133SeedWhileSkillHeld(){ghostVisible=true;seedCount++;},
 st135SeedSheepGhost(){ghostVisible=true;seedCount++;return true;},
 st126SeedAtSheep(){ghostVisible=true;seedCount++;},
 st135HandleBuildAim(event){
  pointerAimCalls++;
  if(!ctx.aimAnchor){ctx.aimAnchor={x:event.clientX,y:event.clientY};ctx.stBuildInput.moved=false;tp.valid=false;return;}
  const dx=event.clientX-ctx.aimAnchor.x,dy=event.clientY-ctx.aimAnchor.y;
  ctx.stBuildInput.moved=Math.hypot(dx,dy)>8;
  if(ctx.stBuildInput.moved){
   tp.valid=true;stUi.placement={ok:true,x:10+dx/10,z:20+dy/10,rotation:0};
   ghostVisible=true;
  }
 },
 st135TapPlacement(event){tp.valid=true;stUi.placement={ok:true,x:event.clientX/10,z:event.clientY/10,rotation:0};return true;},
 st135CommitPreview(){
  const f=stUi.placement;assert.ok(tp.valid&&f?.ok);
  const result={ok:true};commands.push({...f,kind:stUi.build});
  ctx.stBuildInput.outcome=result;return result;
 },
 st133RememberBuildTouch(){seen.push('recorded touch for synthetic-click guard');},
 stUiOrderAt(){throw Error('old finger-based order should never run');},
 st132Rapid:false
};
vm.createContext(ctx);
vm.runInContext(lifecycle,ctx,{filename:'native-137-build-lifecycle.js'});
ctx.stBuildInput=vm.runInContext('stBuildInput',ctx);
function emit(type,{target=viewport,id=1,x=250,y=300,pointerType='touch',buttons=1}={}){
 const event={type,target,pointerId:id,clientX:x,clientY:y,
  pointerType,button:0,buttons,preventDefault(){},stopImmediatePropagation(){}};
 for(const callback of listeners[type]||[])callback(event);
 return event;
}
// A phone button near bottom-right can only select. Dragging that button
// must NOT spend the gesture moving an offscreen house or create a house.
emit('pointerdown',{target:skill,id:4,x:510,y:750});
emit('pointermove',{target:skill,id:4,x:280,y:450});
assert.equal(pointerAimCalls,0,'button drag is ignored on touch');
emit('pointerup',{target:skill,id:4,x:280,y:450});
assert.equal(stUi.build,'st-farm','a selected tool survives button release');
assert.equal(commands.length,0,'touching the button never builds');
assert.equal(ghostVisible,true,'the ghost remains at sheep on button release');
assert.ok(seen.some(s=>s.includes('Drag anywhere on open meadow')));
// A NEW finger begins on the middle meadow with full screen travel.
ctx.aimAnchor=null;
emit('pointerdown',{target:viewport,id:5,x:230,y:290});
assert.equal(stUi.build,'st-farm','meadow gesture retains selected skill');
assert.equal(commands.length,0,'no construction on meadow pointerdown');
emit('pointermove',{target:viewport,id:5,x:300,y:390});
assert.equal(pointerAimCalls,2);
emit('pointerup',{target:viewport,id:5,x:300,y:390});
assert.equal(commands.length,1);
assert.equal(commands[0].x,17);
assert.equal(commands[0].z,30);
assert.equal(stUi.build,null,'one-shot placement exits build mode');
// Tap-to-place is also retained, including on the next selection.
emit('pointerdown',{target:skill,id:6,x:520,y:740});
emit('pointerup',{target:skill,id:6,x:520,y:740});
ctx.aimAnchor=null;
emit('pointerdown',{target:viewport,id:7,x:260,y:320});
emit('pointerup',{target:viewport,id:7,x:260,y:320});
assert.equal(commands.length,2,'short meadow tap commits a native site');
assert.equal(commands[1].x,26);
// Rapid keeps a tool selected after success for subsequent meadow drags.
ctx.st132Rapid=true;
emit('pointerdown',{target:skill,id:8,x:500,y:750});
emit('pointerup',{target:skill,id:8,x:500,y:750});
ctx.aimAnchor=null;
emit('pointerdown',{target:viewport,id:9,x:190,y:220});
emit('pointermove',{target:viewport,id:9,x:200,y:240});
emit('pointerup',{target:viewport,id:9,x:200,y:240});
assert.equal(commands.length,3);
assert.equal(stUi.build,'st-farm','Rapid retains the house for next meadow gesture');
assert.equal(ghostVisible,true,'Rapid immediately reseeds sheep ghost');
assert.ok(seedCount>=3);
// Mouse-based direct button drag retains legacy semantics.
ctx.st132Rapid=false;
emit('pointerdown',{target:skill,id:10,x:300,y:300,pointerType:'mouse'});
const before=pointerAimCalls;
emit('pointermove',{target:skill,id:10,x:370,y:340,pointerType:'mouse'});
assert.ok(pointerAimCalls>before,'desktop mouse skill drag unchanged');
console.log('SE137_TOUCH_BUTTON_SELECTION_MEADOW_FREE_DRAG_TAP_RAPID_MOUSE_PASS');
