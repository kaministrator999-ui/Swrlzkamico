import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const {JSDOM}=require(process.env.SE_JSDOM_MODULE);
const root='projects/swrlz-forge-moba/';
const src=fs.readFileSync(root+'runtime/sheep_rapid_cancel_seed_skills_swap_v11_134.js','utf8');
const css=fs.readFileSync(root+'runtime/sheep_rapid_cancel_seed_skills_swap_v11_134.css','utf8');
const {window}=new JSDOM('<div id="sheepTagHUD"><button id="st132RapidBuild"><small>OFF</small></button><div id="stAbilityRing"><button id="stSplit" hidden></button><button id="stTotem" hidden></button></div></div>',{url:'https://example.test/'});
const $=id=>window.document.getElementById(id);
const sheep={id:'our-sheep',kind:'sheep',pos:{x:12.325,y:0,z:-7.885}};
const ctx={window,document:window.document,$,console,stSession:{units:[sheep],controlledId:sheep.id},stUi:{shown:true,build:null,preview:null,placementPoint:null},stBuildInput:{pointer:null},stTouchPlacement:{gesture:null},stPlacementGridSeed:null,
 stUiRules:()=>({split:true,totems:true}),
 stTouchPlacementReset(reason){ctx.stTouchPlacement.gesture=null;ctx.cancelled.push(reason);},
 stBuildInputFinish(reason){ctx.completed.push(reason);ctx.stBuildInput.pointer=null;ctx.stUi.build=null;ctx.stUiClearPreview();},
 stUiClearPreview(){ctx.ghostCleared++;ctx.stUi.preview=null;ctx.stUi.placementPoint=null;},
 stRefreshHUD(){ctx.refreshed++;},cancelled:[],completed:[],ghostCleared:0,refreshed:0,
 st126SeedAtSheep(){
  if(!ctx.stUi.preview)return false;
  // Reproduce native placement snapping a ghost away from the actual sheep.
  ctx.stUi.preview.position.set(sheep.pos.x+.75,0,sheep.pos.z+.35);
  ctx.stUi.preview.visible=true;
  ctx.stUi.placementPoint={...sheep.pos};
  return true;
 },
 stUiChooseBuild(kind){
  if(ctx.stUi.build===kind){ctx.stUi.build=null;ctx.stUiClearPreview();return;}
  ctx.stUi.build=kind;
  ctx.stUi.preview={
   visible:false,position:{x:0,y:0,z:0,set(x,y,z){Object.assign(this,{x,y,z})}},
   updateMatrixWorld(){this.updated=true;}
  };
 },
 stUiRefreshArchive(state){
  $('stSplit').hidden=!state.rules.split;
  $('stTotem').hidden=!state.rules.totems;
  $('stSplit').disabled=!state.rules.split;
  $('stTotem').disabled=!state.rules.totems;
 }
};
vm.createContext(ctx);
vm.runInContext('let st132Rapid=false;function st132SetRapid(value){st132Rapid=!!value;}',ctx);
vm.runInContext(src,ctx,{filename:'se134.js'});
const inspectRapid=()=>vm.runInContext('st132Rapid',ctx);
const button=$('st132RapidBuild');
ctx.stUiChooseBuild('st-farm');
assert.equal(ctx.stUi.build,'st-farm');
assert.ok(ctx.stUi.preview.visible,'ghost is immediately visible on selection');
assert.equal(ctx.stUi.preview.position.x,sheep.pos.x,'ghost X must be exact live sheep position');
assert.equal(ctx.stUi.preview.position.z,sheep.pos.z,'ghost Z must be exact live sheep position');
assert.equal(ctx.stUi.preview.updated,true,'visual transform updated');
assert.equal(ctx.stPlacementGridSeed,ctx.st126SeedAtSheep,'both native seed entrypoints use exact center');
ctx.stUiChooseBuild('st-farm');
assert.equal(ctx.stUi.build,null,'choosing same skill can still explicitly cancel');
ctx.stUiChooseBuild('st-income');
assert.equal(ctx.stUi.preview.position.z,sheep.pos.z,'Income house also starts on sheep');
ctx.st132SetRapid(true);
assert.equal(inspectRapid(),true);
assert.equal(ctx.stUi.build,'st-income','enabling rapid does not cancel ghost');
const removedBefore=ctx.ghostCleared;
ctx.st132SetRapid(false);
assert.equal(inspectRapid(),false);
assert.equal(ctx.stUi.build,null,'turning rapid OFF exits placement mode');
assert.equal(ctx.stUi.preview,null,'unplaced ghost removed');
assert.equal(ctx.stUi.placementPoint,null,'no stale placement marker');
assert.ok(ctx.ghostCleared>removedBefore);
assert.equal(ctx.completed.length,0,'inactive pointer needs no pointer cleanup');
assert.equal(ctx.refreshed,1,'HUD updated immediately when rapid switches off');
// Off without prior rapid ON is idempotent.
ctx.stUiChooseBuild('st-fort');
ctx.st132SetRapid(false);
assert.equal(ctx.stUi.build,'st-fort','ordinary one-shot build unaffected by off');
ctx.st132SetRapid(true);
ctx.stBuildInput.pointer=77;const finishedBefore=ctx.completed.length;
ctx.st132SetRapid(false);
assert.equal(ctx.completed.length,finishedBefore+1,'in-flight rapid placement pointer is cancelled');
assert.equal(ctx.stBuildInput.pointer,null);
assert.equal(ctx.stUi.preview,null);
for(const rules of [{split:false,totems:false},{split:true,totems:true},{split:false,totems:true}]){
 $('stSplit').hidden=$('stTotem').hidden=true;
 $('stSplit').title=$('stTotem').title='';
 $('stSplit').removeAttribute('aria-label');$('stTotem').removeAttribute('aria-label');
 ctx.stUiRefreshArchive({role:'sheep',rules},sheep,null,true,0);
 assert.equal($('stSplit').hidden,false,'Mirror slot remains visible in sheep HUD');
 assert.equal($('stTotem').hidden,false,'Totem slot remains visible in sheep HUD');
 assert.equal($('stSplit').disabled,!rules.split,'Mirror enabled matches rules');
 assert.equal($('stTotem').disabled,!rules.totems,'Totem enabled matches rules');
 if(!rules.split)assert.match($('stSplit').getAttribute('aria-label'),/enable in Sheep Tag rules/);
 if(!rules.totems)assert.match($('stTotem').getAttribute('aria-label'),/enable in Sheep Tag rules/);
}
ctx.stUiRefreshArchive({role:'wolf',rules:{split:false,totems:false}},null,null,false,0);
assert.equal($('stSplit').hidden,true,'wolf role retains hidden sheep abilities');
assert.equal($('stTotem').hidden,true,'wolf role retains hidden sheep abilities');
assert.ok(css.includes('#stBuildFarm')&&css.includes('--st-outer-diag-x'),'Free House moves to old Income position');
assert.ok(css.includes('#stBuildIncome')&&css.includes('--st-outer-end-x'),'Income moves to former bottom-right free slot');
assert.ok(!src.includes("ST_BUILDINGS["),'building costs and game commands unchanged');
if(process.env.SE_ASSEMBLED_HTML){
 const html=fs.readFileSync(process.env.SE_ASSEMBLED_HTML,'utf8');
 for(const marker of [
  'SWYRL_ENGINE_DEPLOY_MARKER: V11_134_RAPID_CANCEL_SHEEP_MARKER_VISIBLE_SKILLS_HOUSE_SWAP',
  'st134RapidBase=st132SetRapid','st134SeedBase=st126SeedAtSheep',
  'st134ChooseBase=stUiChooseBuild','st134AbilitiesBase=stUiRefreshArchive',
  'se134-build-skill-layout','st133RememberBuildTouch',
  'st132InstallRapid','st131MirrorDirection'
 ])assert.ok(html.includes(marker),'integrated feature missing '+marker);
}
console.log('SE134_RAPID_OFF_CANCEL_SHEEP_INITIAL_GHOST_ABILITIES_VISIBLE_HOUSE_INCOME_SWAP_PASS');
