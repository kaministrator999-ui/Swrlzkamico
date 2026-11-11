// Focused Quest Y-to-tools regression (independent of a headset runtime).
const assert=require('node:assert/strict'),vm=require('node:vm'),fs=require('node:fs');
const script=fs.readFileSync(require('node:path').join(__dirname,'../runtime/sheep_vr_y_tools_radial_v11_391.js'),'utf8');
const left={index:0,input:{handedness:'left',gamepad:{buttons:Array.from({length:6},()=>({pressed:false,value:0}))}}},
right={index:1,input:{handedness:'right',gamepad:{buttons:Array.from({length:6},()=>({pressed:false,value:0}))}}};
const history=[],se193={held:new Map()},se195={visible:false,mode:'game',page:'main',photo:false};
const se204={wheel:null};let vr=true,game=true,blur=false,oldEdges=0,rightFrees=0,wheelHides=0;
const ctx={window:{},se193,se195,se204,
 se192InputRecord:side=>side==='left'?left:right,
 se192Pressed:(r,index)=>r.input.gamepad.buttons[index].pressed,
 se195Active:()=>vr,se193XRGameActive:()=>game,
 se211Visibility:()=>blur?'visible-blurred':'visible',
 se205OverlayActive:()=>blur,
 se204WheelHide:()=>{wheelHides++;se204.wheel=null;},
 se195SetVisible:v=>{se195.visible=v;history.push(v?'open':'close');},
 se193XRButtonEdges:()=>{oldEdges++;for(const r of [left,right]){const held=r.input.gamepad.buttons[5].pressed,prior=!!se193.held.get(r.index);if(held&&!prior){if(r===left)history.push('old-left-follow');else rightFrees++;}se193.held.set(r.index,held);}}
};
vm.createContext(ctx);vm.runInContext(script,ctx);
const edge=()=>ctx.se193XRButtonEdges();
const button=(r,index,value)=>{r.input.gamepad.buttons[index].pressed=value;};
button(left,5,true);edge();assert.deepEqual(history,['open']);
edge();assert.deepEqual(history,['open']);
button(left,5,false);edge();
button(left,5,true);edge();assert.deepEqual(history,['open','close']);
button(left,5,false);edge();
button(right,5,true);edge();assert.equal(rightFrees,1);button(right,5,false);edge();
se204.wheel={type:'skill'};button(left,5,true);edge();assert.equal(wheelHides,1);assert.equal(se195.page,'main');button(left,5,false);edge();
blur=true;button(left,5,true);edge();assert.deepEqual(history,['open','close','open']);
button(left,5,false);edge();blur=false;se195.photo=true;
button(left,5,true);edge();assert.equal(history.length,3);button(left,5,false);edge();se195.photo=false;
vr=false;button(left,5,true);edge();assert.equal(history.length,4);assert.equal(history.at(-1),'old-left-follow');
assert.equal(ctx.window.SWYRL_ENGINE_SHEEP_VR_Y_MENU_391.diagnose().questSystemMenuButtonReserved,true);
assert.equal(oldEdges,14);
console.log('Quest Y radial: open/close, hold debounce, existing right B, wheel cancel, overlay/photo guard and non-XR passthrough passed');
