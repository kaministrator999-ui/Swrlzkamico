// Focused VM smoke check: no browser/Quest hardware, no game/UI side effects.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');
const src=fs.readFileSync(path.join(__dirname,'../runtime/sheep_vr_frame_cadence_v11_379.js'),'utf8');
let now=1000,originalCalls=0,blurEvents=0,fbCalls=0,previousCalls=0;
const s={lastFrame:1000,lastVisible:'visible',returnUntil:0,pendingRelease:false};
const ctx={
  performance:{now:()=>now},document:{visibilityState:'visible'},
  se211:s,se211Visibility:()=>ctx.visibility,
  se238NativeMenuOpen:()=>ctx.menuOpen,
  se195Gameplay:()=>ctx.gameplay,stSession:{simulate:false},
  currentProject:{kind:'sheep-tag'},performancePrefs:{preset:'auto'},
  se191XR:{framebufferScale:.72},
  se195OriginalFramebuffer:()=>{fbCalls++;},
  se191XRPrepareFramebuffer:()=>{previousCalls++;},
  se193XRCleanup:()=>{},
  window:{},visibility:'visible',menuOpen:false,gameplay:true,
  se211OnFrame:()=>{
    originalCalls++;
    if(now-s.lastFrame>170){blurEvents++;s.returnUntil=now+300;}
    s.lastFrame=now;
  }
};
vm.runInNewContext(src,ctx);
now=1230;ctx.se211OnFrame();
assert.equal(blurEvents,0,'visible 230ms Sheep Tag hitch is not an OS overlay');
assert.equal(originalCalls,1,'original observer still runs');
assert.equal(ctx.window.SWYRL_ENGINE_SHEEP_VR_CADENCE_379.diagnose().visibleGameplayGapsNotMistakenForOSBlur,1);
now=2050;ctx.se211OnFrame();
assert.equal(blurEvents,1,'long 820ms gap retains native OS recovery');
ctx.se211.returnUntil=0;ctx.se211.lastFrame=2100;now=2350;
ctx.visibility='visible-blurred';ctx.se211OnFrame();
assert.equal(blurEvents,2,'real XR blur is not bypassed');
ctx.visibility='visible';ctx.menuOpen=true;ctx.se211.lastFrame=2400;now=2630;
ctx.se211OnFrame();assert.equal(blurEvents,3,'menu handling stays with existing v11.238 guard');
ctx.menuOpen=false;ctx.se211.returnUntil=0;
for(const [preset,expected] of [['low',.60],['high',.86],['mobile',.58],['auto',.72],['custom',.90]]){
  ctx.performancePrefs.preset=preset;ctx.performancePrefs.renderScale=2;
  ctx.se191XRPrepareFramebuffer();
  assert.equal(ctx.se191XR.framebufferScale,expected,preset);
}
assert.equal(fbCalls,5);assert.equal(previousCalls,0,'Sheep avoids constant .72 wrapper');
ctx.currentProject.kind='other';ctx.se191XRPrepareFramebuffer();assert.equal(previousCalls,1,'other projects unchanged');
assert.equal(ctx.window.SWYRL_ENGINE_SHEEP_VR_CADENCE_379.diagnose().framebufferChangesRequireVRReentry,true);
console.log('v11.379 focused VR cadence / focus-guard / preset smoke: PASS');
