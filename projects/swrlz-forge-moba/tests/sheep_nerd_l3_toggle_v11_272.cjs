// §E v11.272: left Quest L3 toggles ONLY the existing Nerd Stats VR panel.
const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const code=fs.readFileSync(path.join(__dirname,'../runtime/sheep_nerd_stats_l3_toggle_v11_272.js'),'utf8');
let xr=true,game=true,overlay=false,held=false;
let opens=0,closes=0,baseFrames=0,baseCleanup=0;
const left={input:{handedness:'left',gamepad:{buttons:[{pressed:false},{pressed:false},{pressed:false},{pressed:false,value:0}],axes:[0,0,.5,-.2]}}};
const right={input:{handedness:'right',gamepad:{buttons:[{pressed:false},{pressed:false},{pressed:false},{pressed:true,value:1}],axes:[0,0,.25,.2]}}};
const records=new Map([['left',left],['right',right]]),panels=new Map();
const ctx={
  window:{},se210UI:{panels},
  se192InputRecord:side=>records.get(side),
  se210Active:()=>xr&&game&&!overlay,
  se193XRFrame:()=>{baseFrames++;},
  se193XRCleanup:()=>{baseCleanup++;},
  se210PanelCreate(kind){
    assert.equal(kind,'metrics');
    opens++;
    const panel=panels.get(kind)||{root:{visible:false}};
    panel.root.visible=true;panels.set(kind,panel);
    return panel;
  },
  se210PanelClose(kind){
    assert.equal(kind,'metrics');
    closes++;panels.get(kind).root.visible=false;
    return true;
  }
};
vm.runInNewContext(code,ctx,{filename:'sheep_nerd_stats_l3_toggle_v11_272.js'});
function tick(pressed){
  left.input.gamepad.buttons[3].pressed=pressed;
  left.input.gamepad.buttons[3].value=pressed?1:0;
  ctx.se193XRFrame();
}
tick(false);
tick(true); // L3 press #1 -> open
assert.equal(opens,1);assert.equal(closes,0);
assert.equal(panels.get('metrics').root.visible,true);
for(let i=0;i<35;i++)tick(true); // hold cannot repeat
assert.equal(opens,1);
assert.deepEqual(left.input.gamepad.axes,[0,0,.5,-.2],'analog movement must remain intact');
tick(false);
tick(true); // L3 press #2 -> close
assert.equal(closes,1);assert.equal(panels.get('metrics').root.visible,false);
tick(false);
game=false;tick(true);game=true;tick(true); // no edge while held across menu
assert.equal(opens,1);
tick(false);
overlay=true;tick(true);overlay=false;tick(true); // same for OS overlay
assert.equal(opens,1);
tick(false);
tick(true);assert.equal(opens,2);
right.input.gamepad.buttons[3].pressed=true;tick(true);
assert.equal(opens,2,'right stick cannot toggle');
ctx.se193XRCleanup();
assert.equal(baseCleanup,1);
const d=ctx.window.SWYRL_ENGINE_SHEEP_NERD_L3_272.diagnose();
assert.equal(d.opens,2);assert.equal(d.closes,1);
assert.equal(d.l3Presses,3);assert.equal(d.leftJoystickMovementUnchanged,true);
console.log('SHEEP_NERD_L3_272_TOGGLE_OK',{
 opens,closes,presses:d.l3Presses,frameCallbacks:baseFrames,
 ignored:d.ignored
});
