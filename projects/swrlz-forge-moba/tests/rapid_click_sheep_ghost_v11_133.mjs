import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const {JSDOM}=require(process.env.SE_JSDOM_MODULE);
const root='projects/swrlz-forge-moba/';
const src=fs.readFileSync(root+'runtime/sheep_build_skill_click_rapid_ui_v11_133.js','utf8');
const css=fs.readFileSync(root+'runtime/sheep_build_skill_click_rapid_ui_v11_133.css','utf8');
const dom=new JSDOM('<section id="sheepTagHUD"><div class="st-builds"><button data-st-skill="st-farm" id="stBuildFarm">House</button><button id="stBuildIncome" data-st-skill="st-income">Income</button></div><button id="st132RapidBuild" aria-pressed="false">RAPID</button><button id="st132Rotate">⟳</button></section><div id="viewport"><canvas id="renderCanvas"></canvas></div>',{url:'https://example.test/'});
const {window}=dom,document=window.document;
let now=5000,selected=null,seeded=0,rapid=false,clicks=0;
const chosen=document.getElementById('stBuildFarm'),rapidButton=document.getElementById('st132RapidBuild');
const gesture={id:17},placement={gesture};
const viewport=document.getElementById('viewport'),canvas=document.getElementById('renderCanvas');
const ctx={window,document,performance:{now:()=>now},stTouchPlacement:placement,
 st126SeedAtSheep:()=>{seeded++;assert.equal(placement.gesture,null,'preview seeded without invalid placement gesture');return true;},
 stTouchPlacementClearCanvas:(x,y)=>false,
 $:id=>document.getElementById(id)};
vm.createContext(ctx);
vm.runInContext(src,ctx,{filename:'se133.js'});
ctx.st133MoveMobileBuildControls();
assert.equal(rapidButton.parentElement.className,'st-builds','Rapid attached to native bottom-right skill cluster');
assert.equal(document.getElementById('st132Rotate').parentElement.className,'st-builds');
rapidButton.addEventListener('click',()=>{rapid=!rapid;clicks++});
rapidButton.click();assert.equal(rapid,true);assert.equal(clicks,1,'Rapid button remains a functioning clickable control');
rapidButton.click();assert.equal(rapid,false);
ctx.st133SeedWhileSkillHeld();
assert.equal(seeded,1);assert.equal(placement.gesture,gesture,'pointer tracking restored after ghost seed');
document.elementFromPoint=()=>canvas;
viewport.getBoundingClientRect=()=>({left:0,top:0,right:500,bottom:900});
assert.equal(ctx.st133CanAimSkillAt(190,300),true,'viewport child canvas counts as meadow');
assert.equal(ctx.st133CanAimSkillAt(520,300),false,'off-canvas gesture is not an aiming point');
const nativeClick=()=>{selected=selected==='st-farm'?null:'st-farm';clicks++};
chosen.onclick=nativeClick;
selected='st-farm';
ctx.st133RememberBuildTouch({pointerType:'touch'},'st-farm');
const synthetic=new window.MouseEvent('click',{bubbles:true,cancelable:true,detail:1});
chosen.dispatchEvent(synthetic);
assert.equal(synthetic.defaultPrevented,true,'only duplicated synthetic click is cancelled');
assert.equal(selected,'st-farm','click does NOT toggle selected build off and remove hologram');
assert.equal(clicks,2,'no duplicate skill onclick reached target');
chosen.dispatchEvent(new window.MouseEvent('click',{bubbles:true,cancelable:true,detail:0}));
assert.equal(selected,null,'keyboard accessibility click remains usable');
ctx.st133RememberBuildTouch({pointerType:'mouse'},'st-farm');
chosen.click();assert.equal(selected,'st-farm','mouse click remains usable');
selected='st-farm';ctx.st133RememberBuildTouch({pointerType:'touch'},'st-farm');
now+=900;
chosen.dispatchEvent(new window.MouseEvent('click',{bubbles:true,cancelable:true,detail:1}));
assert.equal(selected,null,'expired touch suppression never blocks next intentional tap');
const buildClickSelector='#sheepTagHUD .st-builds #st132RapidBuild';
assert.ok(css.includes(buildClickSelector));
assert.ok(css.includes('right:162px!important;bottom:3px!important;'),'Rapid anchors LEFT of Income, level with icon');
assert.ok(css.includes('border-radius:50%!important;'),'Rapid circular under higher specificity native button CSS');
assert.ok(css.includes('pointer-events:auto!important;'),'fix HUD inherited pointer-events none');
assert.ok(css.includes('#st132RapidBuild.active'),'ON state remains visually distinct');
const assembled=process.env.SE_ASSEMBLED_HTML&&fs.readFileSync(process.env.SE_ASSEMBLED_HTML,'utf8');
if(assembled){
 for(const token of [
  'SWYRL_ENGINE_DEPLOY_MARKER: V11_133_TOUCHABLE_RAPID_AND_PERSISTENT_SHEEP_GHOST',
  'st133RememberBuildTouch(event,stBuildInput.kind)',
  'st133SeedWhileSkillHeld()',
  "if(stBuildInput.source==='skill'&&!st133CanAimSkillAt(event.clientX,event.clientY))return;",
  "if(source==='skill'&&!stBuildInput.moved)",
  'st133MoveMobileBuildControls',
  "stBuildInputFinish('New placement',meadow);",
  'st132SetRapid', 'st132GroundUnderDeck','st131InstallMirrorControl'
 ]) assert.ok(assembled.includes(token),'missing integrated behavior '+token);
 const inputStart=assembled.indexOf('const stBuildInput=');
 assert.ok(inputStart>0);
 const up=assembled.slice(assembled.indexOf("window.addEventListener('pointerup',event=>{",inputStart),
  assembled.indexOf("},true);",assembled.indexOf("window.addEventListener('pointerup',event=>{",inputStart))+8);
 assert.ok(up.indexOf("st133RememberBuildTouch(event,stBuildInput.kind)")<up.indexOf("stBuildInputFinish('Tool selected',true)"),'suppression set before tool gesture is reset');
 assert.ok(up.includes("stBuildInputAim(event);"),'skill drag reaching meadow still aims');
 const move=assembled.slice(assembled.indexOf("window.addEventListener('pointermove',event=>{",inputStart),
  assembled.indexOf("},true);",assembled.indexOf("window.addEventListener('pointermove',event=>{",inputStart))+8);
 assert.ok(move.includes("st133CanAimSkillAt"),'skill drag begins to follow on entering meadow');
}
console.log('SE133_SKILL_TOUCH_CLICK_PRESERVES_GHOST_RAPID_CLICKABLE_AND_BELOW_INCOME_PASS');
