import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const root='projects/swrlz-forge-moba/';
const src=fs.readFileSync(root+'runtime/sheep_rapid_screen_anchor_v11_138.js','utf8');
const html=fs.readFileSync(process.env.SE_ASSEMBLED_HTML,'utf8');
for(const token of [
 'SWYRL_ENGINE_DEPLOY_MARKER: V11_138_RAPID_LAST_BUILD_SCREEN_ANCHOR',
 'if(repeat)st138RememberLastScreenPosition();',
 'stUiChooseBuild(kind);st126SeedAtSheep();st138SeedFromScreen();',
 'st138AttachAim(st135AimState);',
 'const rapidTarget=st138RapidTarget(anchor,x,y);'
])assert.ok(html.includes(token),'assembled Rapid integration missing '+token);
class Vector3{
 constructor(x=0,y=0,z=0){this.x=x;this.y=y;this.z=z;}
 clone(){return new Vector3(this.x,this.y,this.z);}
 project(camera){
  const x=(this.x-camera.panX)/50;
  const y=-(this.z-camera.panZ)/50;
  this.x=x;this.y=y;this.z=0;return this;
 }
}
let time=1000,seedSheepCount=0,placedPreviews=0,orders=0;
const rect={left:100,top:80,width:1000,height:800,right:1100,bottom:880};
const camera={panX:0,panZ:0};
const viewport={getBoundingClientRect(){return rect;}};
const sheep={kind:'sheep',id:'one',captured:false,pos:new Vector3(2,0,9)};
const session={controlledId:'one',units:[sheep],simulate:false,winner:null};
const ui={build:'st-farm',shown:true,placement:{ok:true,x:15,z:20,rotation:0},
 preview:{visible:true,position:new Vector3()},footprint:{visible:true}};
const tp={gesture:null,context:null,valid:false};
const guide={root:{visible:true}};
let rapid=false;
const ctx={
 console,Number,Math,Infinity,
 THREE:{Vector3},camera,performance:{now(){return time;}},stSession:session,
 stUi:ui,stTouchPlacement:tp,stPlacementGridState:{guide},stBuildInput:{pointer:null},
 terrainHeight(){return 0;},$:id=>id==='viewport'?viewport:null,
 stTouchPlacementOriginalGround(x,y){
  const u=(x-rect.left)/rect.width,v=(y-rect.top)/rect.height;
  return new Vector3(camera.panX+(u-.5)*100,0,camera.panZ+(v-.5)*100);
 },
 stTouchPlacementClearCanvas(x,y){
  return x>=rect.left&&x<rect.right&&y>=rect.top&&y<rect.bottom;
 },
 stUiPlacePreview(point){
  placedPreviews++;
  ui.placement={ok:true,x:point.x,z:point.z,rotation:0};
  ui.preview.position=point.clone();ui.preview.visible=true;
  guide.root.visible=true;
 },
 st132Rapid:false,
 st135SeedSheepGhost(){
  seedSheepCount++;ui.preview.position=sheep.pos.clone();return true;
 },
 stUiChooseBuild(kind){ui.build=kind;return true;},
 st132SetRapid(enabled){ctx.st132Rapid=!!enabled;},
 stStop(){orders++;},
 stUpdateCamera(){},
 stUiStatus(){return {};}
};
vm.createContext(ctx);
vm.runInContext(src,ctx,{filename:'rapid-screen-138.js'});
const call=(expr)=>vm.runInContext(expr,ctx);
assert.equal(call('st138SeedFromScreen()'),false,'first ever ghost is sheep-centered');
ctx.st132SetRapid(true);
assert.equal(call('st138RememberLastScreenPosition()'),true);
const remembered=call('stUiStatus().rapidScreenAnchor');
assert.ok(Math.abs(remembered.u-.65)<1e-7);
assert.ok(Math.abs(remembered.v-.7)<1e-7);
const anchoredPixel={x:rect.left+remembered.u*rect.width,y:rect.top+remembered.v*rect.height};
sheep.pos.x=60;sheep.pos.z=80;
camera.panX=50;camera.panZ=-40;
assert.equal(call('st138SeedFromScreen()'),true);
const worldPoint=ui.preview.position.clone();
assert.ok(Math.abs(worldPoint.x-65)<1e-7);
assert.ok(Math.abs(worldPoint.z-(-20))<1e-7);
const projected=worldPoint.clone().project(camera);
assert.ok(Math.abs(rect.left+(projected.x+1)*rect.width/2-anchoredPixel.x)<1e-7);
assert.ok(Math.abs(rect.top+(1-projected.y)*rect.height/2-anchoredPixel.y)<1e-7);
assert.equal(tp.valid,false,'no ghost-only order can commit');
assert.equal(orders,0);
ctx.activeAim={session,pointer:21,x:280,y:240};
call('st138AttachAim(activeAim)');
assert.ok(ctx.activeAim.st138Screen,'screen anchor attaches to a meadow gesture');
const moved=call('st138RapidTarget(activeAim,380,290)');
const newProjected=moved.clone().project(camera);
assert.ok(Math.abs(rect.left+(newProjected.x+1)*rect.width/2-(anchoredPixel.x+100))<1e-7);
assert.ok(Math.abs(rect.top+(1-newProjected.y)*rect.height/2-(anchoredPixel.y+50))<1e-7);
assert.equal(call('st138RapidTarget(activeAim,1200,290)'),null,'outside viewport does not jump to sheep');
ctx.stBuildInput.pointer=21;
const before=placedPreviews;
time=1100;ctx.stUpdateCamera(.016);
assert.equal(placedPreviews,before,'idle pin does not override an active meadow drag');
ctx.stBuildInput.pointer=null;
camera.panX=77;time=1200;ctx.stUpdateCamera(.016);
assert.ok(placedPreviews>before,'camera movement reprojects idle ghost');
const after=placedPreviews;
time=1201;ctx.stUpdateCamera(.016);
assert.equal(placedPreviews,after,'idle pin is throttled');
ctx.st132SetRapid(false);
assert.equal(call('stUiStatus().rapidScreenAnchor'),null);
assert.equal(call('st138SeedFromScreen()'),false);
assert.equal(call('st138RapidTarget({x:20,y:20},30,30)'),undefined);
ctx.st132SetRapid(true);
assert.equal(call('st138SeedFromScreen()'),false,'Rapid reenabled without valid previous placement resets');
camera.panX=0;camera.panZ=0;
ui.placement={ok:true,x:8,z:9,rotation:0};
assert.equal(call('st138RememberLastScreenPosition()'),true);
session.controlledId='two';
assert.equal(call('st138SeedFromScreen()'),false,'memory cannot leak to another sheep');
session.controlledId='one';
ctx.stStop();
assert.equal(call('stUiStatus().rapidScreenAnchor'),null,'stopping clears repeat position');
console.log('SE138_RAPID_LAST_SUCCESSFUL_SCREEN_SPOT_CAMERA_PAN_DRAG_RESET_PASS');
