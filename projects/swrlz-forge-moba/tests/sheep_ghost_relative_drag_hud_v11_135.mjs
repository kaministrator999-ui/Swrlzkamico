import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const root='projects/swrlz-forge-moba/';
const src=fs.readFileSync(root+'runtime/sheep_build_sheep_origin_mirror_hud_v11_135.js','utf8');
const css=fs.readFileSync(root+'runtime/sheep_build_sheep_origin_mirror_hud_v11_135.css','utf8');
class Vector3{
 constructor(x=0,y=0,z=0){this.x=x;this.y=y;this.z=z;}
 clone(){return new Vector3(this.x,this.y,this.z);}
 set(x,y,z){this.x=x;this.y=y;this.z=z;return this;}
 toArray(){return [this.x,this.y,this.z];}
}
const children=[];
const ring={appendChild(button){button.parentElement=this;children.push(button);}};
const split={hidden:true,disabled:false,parentElement:null,setAttribute(){}};
const totem={hidden:true,disabled:false,parentElement:null,setAttribute(){}};
const nodes={stAbilityRing:ring,stSplit:split,stTotem:totem};
const sheep={id:'sheep',kind:'sheep',captured:false,pos:new Vector3(10,0,20)};
let committed=null,previewCount=0;
const ctx={
 THREE:{Vector3},console,structuredClone,
 stSession:{units:[sheep],controlledId:'sheep',role:'sheep'},
 stUi:{shown:true,build:'st-farm',rotation:0,preview:{visible:false,position:new Vector3()},placement:null,footprint:{visible:true}},
 stBuildInput:{pointer:77,source:'skill',startX:800,startY:1900,moved:false},
 stTouchPlacement:{gesture:{id:77},context:null,valid:false},
 stPlacementGridState:{guide:{root:{visible:true}}},
 $:key=>nodes[key],
 terrainHeight:()=>0,
 stTouchPlacementEnabled:()=>true,
 stTouchPlacementContext(event){ctx.stTouchPlacement.context={x:event.clientX,y:event.clientY,type:event.type};},
 stTouchPlacementOriginalGround:(x,y)=>new Vector3(x/10,0,y/10),
 stTouchPlacementClearCanvas:(x,y)=>x>=0&&x<600&&y>=0&&y<600,
 st126SeedAtSheep(){
  // Old path could seed an offset/snapped position and a detached grid.
  ctx.stUiPlacePreview(new Vector3(sheep.pos.x+5,0,sheep.pos.z+5));
  return true;
 },
 stUiPlacePreview(point){
  previewCount++;
  // Mock actual preview/fit boundary without creating a building.
  ctx.stUi.preview.position.set(point.x,0,point.z);
  ctx.stUi.preview.visible=true;
  ctx.stUi.placement={x:point.x,z:point.z,rotation:0,ok:true,corners:[[point.x-1,point.z-1]]};
 },
 stUiCommand(action,payload){if(action==='build'){committed=payload;return {ok:true};}return {ok:false};},
 stUiRefreshArchive(state){
  split.hidden=!(state?.role==='sheep'&&state?.rules.split);
  totem.hidden=!(state?.role==='sheep'&&state?.rules.totems);
  split.disabled=!state?.rules.split;
  totem.disabled=!state?.rules.totems;
 }
};
vm.createContext(ctx);
vm.runInContext(src,ctx,{filename:'sheep-origin-135.js'});
// The selected skill must show the real sheep-origin ghost, not the nearest
// automatically chosen site or the pointer position on the HUD.
assert.ok(ctx.st135SeedSheepGhost());
assert.equal(ctx.stUi.preview.position.x,10);
assert.equal(ctx.stUi.preview.position.z,20);
assert.equal(ctx.stUi.preview.visible,true);
assert.equal(ctx.stPlacementGridState.guide.root.visible,false,'no detached placement grid before aiming');
assert.equal(ctx.stUi.footprint.visible,false,'footprint waits for explicit aim');
assert.equal(ctx.st135KeepSheepGhostDuringPointer(),true,'camera updater cannot move held ghost');
// A drag from the skill button must be anchored to the FIRST open meadow
// contact; moving to the meadow alone must not teleport to screen coordinates.
const pointer=(pointerId,x,y,type='pointermove')=>({pointerId,clientX:x,clientY:y,type});
ctx.st135HandleBuildAim(pointer(77,300,300));
assert.equal(ctx.stUi.preview.position.x,10);
assert.equal(ctx.stUi.preview.position.z,20);
assert.equal(ctx.stBuildInput.moved,false);
assert.equal(ctx.stTouchPlacement.valid,false);
ctx.st135HandleBuildAim(pointer(77,325,280));
assert.equal(ctx.stBuildInput.moved,true);
assert.equal(ctx.stUi.preview.position.x,12.5);
assert.equal(ctx.stUi.preview.position.z,18);
assert.equal(ctx.stTouchPlacement.valid,true);
assert.ok(previewCount>2);
ctx.st135CommitPreview();
assert.equal(committed.kind,'st-farm');
assert.equal(committed.x,12.5,'commit the ghost, not the finger screen ray at x=32.5');
assert.equal(committed.z,18);
// Separate meadow presses begin on sheep as well, then move relatively.
vm.runInContext('st135AimState=null',ctx);
ctx.stBuildInput.pointer=78;ctx.stBuildInput.source='meadow';
ctx.stTouchPlacement.gesture={id:78};
ctx.st135HandleBuildAim(pointer(78,240,250,'pointerdown'));
assert.equal(ctx.stUi.preview.position.x,10);
ctx.st135HandleBuildAim(pointer(78,251,259));
assert.ok(Math.abs(ctx.stUi.preview.position.x-11.1)<1e-8);
assert.ok(Math.abs(ctx.stUi.preview.position.z-20.9)<1e-8);
// Short, non-drag meadow tap continues to work.
assert.ok(ctx.st135TapPlacement(pointer(78,460,320,'pointerup')));
assert.equal(ctx.stUi.preview.position.x,46);
ctx.st135CommitPreview();
assert.equal(committed.x,46);
// Rule-off means visible-but-disabled; both buttons stay within the ring.
for(const rules of [{split:true,totems:true},{split:false,totems:true},{split:true,totems:false}]){
 ctx.stUiRefreshArchive({role:'sheep',rules,simulate:false});
 assert.equal(split.hidden,false,'Mirror must remain visible');
 assert.equal(totem.hidden,false,'Totem must remain visible');
 assert.equal(split.disabled,!rules.split);
 assert.equal(totem.disabled,!rules.totems);
 assert.equal(split.parentElement,ring);
 assert.equal(totem.parentElement,ring);
}
assert.ok(children.includes(split)&&children.includes(totem));
ctx.stUiRefreshArchive({role:'wolf',rules:{split:false,totems:false},simulate:false});
assert.equal(split.hidden,true,'wolf HUD does not expose sheep Mirror');
assert.equal(totem.hidden,true,'wolf HUD does not expose sheep Totem');
assert.ok(css.includes('#stBuildFarm')&&css.includes('var(--st-outer-x)'),'Free at old Fort slot');
assert.ok(css.includes('var(--st-home-size)*1.12'),'Free diameter enlarged');
assert.ok(css.includes('#stBuildFort')&&css.includes('var(--st-outer-diag-x)'),'Fort at old Free slot');
assert.ok(css.includes('#stSplit:not([hidden])'),'Mirror has an explicit tappable HUD slot');
assert.ok(!src.includes('stBotWolf')&&!src.includes('ST_BUILDINGS['));
if(process.env.SE_ASSEMBLED_HTML){
 const html=fs.readFileSync(process.env.SE_ASSEMBLED_HTML,'utf8');
 for(const term of ['V11_135_SHEEP_ORIGIN_RELATIVE_DRAG_FREE_FORT_MIRROR',
  'if (gesture && !st135KeepSheepGhostDuringPointer())',
  'return st135HandleBuildAim(event);',
  'st135CommitPreview();','se135-sheep-origin-hud'
 ])assert.ok(html.includes(term),'source integration missing '+term);
}
console.log('SE135_SHEEP_ORIGIN_DRAG_FREE_FORT_AND_MIRROR_PASS');
