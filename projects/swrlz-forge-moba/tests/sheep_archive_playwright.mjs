import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {mkdir,readFile,writeFile} from 'node:fs/promises';
import {resolve} from 'node:path';

// Native editor fixtures are imported only while stopped. Every match then
// runs the real native Play, render loop, navigation, AI, economy and inputs.
// The controlled RAF clock advances engine time; it never edits match state.
const base=(process.env.SWYRL_ANIME_TEST_URL||'http://127.0.0.1:8765').replace(/\/$/,'');
const query=new URLSearchParams(process.env.SWYRL_ANIME_TEST_QUERY||'');query.set('project','sheep-tag-meadow');
const output=resolve(process.env.SWYRL_ANIME_SCREENSHOTS_DIR||'sheep-archive-acceptance');
await mkdir(output,{recursive:true});
const modes=[{name:'desktop',viewport:{width:1440,height:900},isMobile:false,hasTouch:false},
  {name:'mobile',viewport:{width:390,height:844},isMobile:true,hasTouch:true}]
  .filter(mode=>!process.env.SWYRL_ANIME_TEST_MODE||process.env.SWYRL_ANIME_TEST_MODE===mode.name);
assert.ok(modes.length,'Choose desktop or mobile');
const browser=await chromium.launch({headless:true,
  ...(process.env.SWYRL_CHROMIUM_PATH?{executablePath:process.env.SWYRL_CHROMIUM_PATH}:{}),
  args:['--no-sandbox','--disable-dev-shm-usage','--enable-webgl','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader']});
const receipts=[],touchPages=new WeakSet();
const state=page=>page.evaluate(()=>window.SWYRL_ENGINE_SHEEP_TAG.status());
const view=page=>page.evaluate(()=>window.SWYRL_ENGINE_SHEEP_TAG.viewStatus());
const render=page=>page.evaluate(()=>window.SWYRL_ENGINE_SHEEP_TAG.renderStatus());
const ui=page=>page.evaluate(()=>window.SWYRL_ENGINE_SHEEP_TAG.uiStatus());
const saved=page=>page.evaluate(()=>window.SWYRL_ENGINE_AGENT.inspectScene());
const command=(page,action,payload={})=>page.evaluate(({action,payload})=>window.SWYRL_ENGINE_SHEEP_TAG.command(action,payload),{action,payload});
const frames=(page,count=1,ms=50)=>page.evaluate(({count,ms})=>window.__archiveClock.step(count,ms),{count,ms});
const unit=(s,id=s.controlledId)=>s.units.find(u=>u.id===id);
const distance=(a,b)=>Math.hypot(a[0]-b[0],a.at(-1)-b.at(-1));
const authored=data=>({project:data.project,layers:data.editor.layers,background:data.scene.background,actors:data.scene.actors,paths:data.scene.paths});
const close=(actual,expected,label,tolerance=1e-5)=>assert.ok(Number.isFinite(actual)&&Math.abs(actual-expected)<=tolerance,
  label+': expected '+expected+', received '+actual);
async function tap(page,id){const node=page.locator('#'+id);assert.equal(await node.isVisible(),true,'Hidden required control '+id);
  if(touchPages.has(page))await node.tap({force:true});else await node.click({force:true});}
async function native(page,id){await tap(page,id);await frames(page,2);}
async function until(page,predicate,label,max=300){let s=await state(page);for(let i=0;i<max&&!predicate(s);i+=4){await frames(page,Math.min(4,max-i));s=await state(page);}
  assert.ok(predicate(s),label+' did not occur in the actual rendered match: '+JSON.stringify(s));return s;}
async function worldTap(page,x,z){const p=await page.evaluate(({x,z})=>window.SWYRL_ENGINE_SHEEP_TAG.pointScreen(x,z),{x,z});
  assert.ok(p?.visible,'World input is outside the visible canvas: '+JSON.stringify({x,z,screen:p}));
  assert.equal(await page.evaluate(p=>{const n=document.elementFromPoint(p.x,p.y);return n?.tagName==='CANVAS'||n?.id==='viewport';},p),true,'World input hits a panel');
  if(touchPages.has(page))await page.touchscreen.tap(p.x,p.y);else await page.mouse.click(p.x,p.y);await frames(page,1);}
async function installClock(context){await context.addInitScript(()=>{
  const nativeRAF=requestAnimationFrame.bind(window),nativeCancel=cancelAnimationFrame.bind(window),nativeNow=performance.now.bind(performance),queue=new Map();
  let frozen=false,now=0,next=1000000000;Object.defineProperty(performance,'now',{configurable:true,value:()=>frozen?now:nativeNow()});
  window.requestAnimationFrame=callback=>{if(!frozen)return nativeRAF(callback);const id=next++;queue.set(id,callback);return id;};
  window.cancelAnimationFrame=id=>{queue.delete(id);nativeCancel(id);};
  window.__archiveClock={freeze:()=>{frozen=true;now=nativeNow();return new Promise(resolve=>nativeRAF(()=>nativeRAF(resolve)));},
    step:(count,ms)=>{if(!frozen)throw Error('Clock is not frozen');for(let i=0;i<count;i++){now+=ms;const pending=[...queue.values()];queue.clear();if(!pending.length)throw Error('Real engine RAF stopped');for(const callback of pending)callback(now);}return {now,pending:queue.size};}};
});}
async function stop(page){if((await state(page)).active){await native(page,'stStop');assert.equal((await state(page)).active,false);}}
async function focus(page,pos){await page.evaluate(pos=>window.SWYRL_ENGINE_SHEEP_TAG.focus(pos),pos);await frames(page,1);}
async function prototypes(page,canonical){const result=await page.evaluate(()=>{
  const result={};for(const type of ['st-farm','st-income','st-fort','st-wall','st-ramp','st-thorn','st-zone','st-pond','st-road','st-grass','st-earth']){
    const id=window.SWYRL_ENGINE_AGENT.spawn(type,{position:[-35,0,-35],name:'Acceptance '+type});window.SWYRL_ENGINE_AGENT.bake();
    result[type]=window.SWYRL_ENGINE_AGENT.inspectScene().scene.actors.find(a=>a.id===id);
  }return result;});for(const [kind,actor]of Object.entries(result))assert.equal(actor?.type,kind,'Native prefab unavailable '+kind);
  await page.evaluate(data=>window.SWYRL_ENGINE_AGENT.loadScene(data),canonical);await frames(page,1);return result;}
function fixture(canonical,models,options={}){
  const data=structuredClone(canonical),first=type=>canonical.scene.actors.find(a=>a.type===type),sheep=[],wolves=[],buildings=[];
  const piece=(type,position,id,extra={})=>({...structuredClone(models[type]||first(type)),id,name:'Acceptance '+id,type,position:[...position],rotation:[0,0,0],scale:[1,1,1],baked:true,visible:true,...extra});
  data.scene.actors=[piece('st-meadow',[0,0,0],'archive-meadow'),piece('st-pen',options.pen||[0,0,0],'archive-pen')];
  for(const [i,p]of (options.sheep||[[-18,0,-18]]).entries()){const a=piece('st-sheep',p,'archive-sheep-'+i);sheep.push(a.id);data.scene.actors.push(a);}
  for(const [i,p]of (options.wolves||[[24,0,24]]).entries()){const a=piece('st-wolf',p,'archive-wolf-'+i);wolves.push(a.id);data.scene.actors.push(a);}
  for(const [i,spec]of (options.pieces||[]).entries()){const a=piece(spec.type,spec.pos,'archive-piece-'+i,{...(spec.rotation?{rotation:spec.rotation}:{}),...(spec.scale?{scale:spec.scale}:{}),...(spec.owner?{stOwner:spec.owner}:{})});data.scene.actors.push(a);if(['st-farm','st-income','st-fort','st-wall','st-ramp'].includes(spec.type))buildings.push(a.id);}
  data.project.sheepTag={...canonical.project.sheepTag,preset:'classic',duration:300,headstart:120,bounds:40,startGold:500,role:'sheep',buildSnap:.15,fogMode:'off',thorns:false,totems:false,elevated:false,split:false,events:false,seed:173,...options.rules};
  return {data,sheep,wolves,buildings};
}
async function load(page,f,play=true){await stop(page);await page.evaluate(data=>window.SWYRL_ENGINE_AGENT.loadScene(data),f.data);await frames(page,2);
  assert.deepEqual(authored(await saved(page)),authored(f.data),'Stopped native import changed authored fixture');
  if(play){await native(page,'playBtn');assert.equal((await state(page)).active,true);}return f;}
async function move(page,x,z,payload={}){assert.equal((await command(page,'select',{id:(await state(page)).controlledId})).ok,true);
  const result=await command(page,'move',{x,z,...payload});assert.equal(result.ok,true,'Rejected legal movement: '+JSON.stringify(result));return result;}
function fieldsIn(node,keys,label){for(const key of keys)assert.ok(Object.hasOwn(node,key),label+' missing '+key);}
function mapSemantics(map){return {schema:map.schema,name:map.name,rules:map.rules,layers:map.layers.map(l=>({name:l.name,visible:l.visible})),
  actors:map.actors.map(a=>({type:a.type,name:a.name,position:a.position,rotation:a.rotation,scale:a.scale,visible:a.visible,baked:a.baked,
    layers:a.layers.map(id=>map.layers.find(l=>l.id===id)?.name).sort()})).sort((a,b)=>JSON.stringify(a).localeCompare(JSON.stringify(b)))};}

try{for(const mode of modes){const context=await browser.newContext({viewport:mode.viewport,isMobile:mode.isMobile,hasTouch:mode.hasTouch});await installClock(context);
  const page=await context.newPage(),errors=[],cases=[];const recordCase=(...names)=>{for(const name of names){cases.push(name);console.log('SHEEP_ARCHIVE_CASE_PASSED',mode.name,name);}};if(mode.hasTouch)touchPages.add(page);page.on('pageerror',error=>errors.push(String(error)));page.setDefaultTimeout(30000);
  await page.goto(base+'/index.html?'+query,{waitUntil:'domcontentloaded',timeout:60000});
  await page.waitForFunction(()=>window.SWYRL_ENGINE_SHEEP_TAG_CREATOR&&window.SWYRL_ENGINE_SHEEP_TAG?.viewStatus&&window.SWYRL_ENGINE_AGENT.project().canonicalId==='sheep-tag-meadow',undefined,{timeout:60000});
  await page.locator('#perfPreset').selectOption('medium',{force:true});await page.evaluate(()=>window.__archiveClock.freeze());await frames(page,2);
  const canonical=await saved(page);assert.equal(await page.evaluate(()=>window.SWRLZ_FORGE_BUILD?.version),'v11.62');
  assert.equal(canonical.scene.actors.filter(a=>a.type==='st-sheep').length,8);assert.equal(canonical.scene.actors.filter(a=>a.type==='st-wolf').length,3);
  assert.equal(canonical.scene.actors.length,92,'Wrong native Archive map package');assert.equal(canonical.editor.layers.length,6,'Archive starter needs its six native map layers');
  assert.equal(canonical.project.sheepTag.preset,'archive');assert.equal(canonical.project.sheepTag.events,false,'Default starter forces experimental events');
  for(const flag of ['thorns','totems','elevated','split'])assert.equal(canonical.project.sheepTag[flag],true,'Archive starter does not showcase '+flag);
  fieldsIn(canonical.project.sheepTag,['preset','buildSnap','fogMode','wolfSpeed','wolfDamage','rescueHold','thorns','totems','elevated','split','events','seed'],'Saved archive rules');
  const models=await prototypes(page,canonical);

  // Native Play and portable import reject occupied starting ground without
  // relocating units. This does not require an exit from a free house pocket.
  for(const options of [
    {sheep:[[-18,0,-18]],pieces:[{type:'st-pond',pos:[-18,0,-18]}]},
    {pen:[38,0,0]},
    {wolves:[[24,0,24]],pieces:[{type:'st-farm',pos:[24,0,24]}]}
  ]){
    const blocked=fixture(canonical,models,options);await load(page,blocked,false);
    const before=authored(await saved(page));
    const check=await page.evaluate(()=>window.SWYRL_ENGINE_SHEEP_TAG.validateStarts());
    assert.equal(check.ok,false,'Invalid authored start passed physical preflight');
    await native(page,'playBtn');assert.equal((await state(page)).active,false,'Invalid map started a match');
    assert.deepEqual(authored(await saved(page)),before,'Rejected Play moved or altered the map');
    const portable=await page.evaluate(()=>window.SWYRL_ENGINE_SHEEP_TAG_CREATOR.exportMap());
    assert.equal(portable.ok,false,'Portable map bypassed physical preflight');
  }
  await page.evaluate(data=>window.SWYRL_ENGINE_AGENT.loadScene(data),canonical);await frames(page,2);
  recordCase('authored_spawn_pen_preflight_without_relocation');

  // Rules expose provisional experiments separately, and preserve native Undo.
  await tap(page,'sheepTagRulesBtn');await page.locator('#stRulePreset').selectOption('archive',{force:true});
  for(const flag of ['thorns','totems','elevated','split'])assert.equal(await page.locator('#stRule_'+flag).isChecked(),true,'Archive preset missed '+flag);
  assert.equal(await page.locator('#stRule_events').isChecked(),false,'Random events became a forced rule');
  await page.locator('#stRuleFog').selectOption('solo',{force:true});await tap(page,'stRulesApply');await tap(page,'stRulesClose');
  assert.equal((await saved(page)).project.sheepTag.fogMode,'solo');assert.equal((await saved(page)).project.sheepTag.events,false);
  await page.locator('#undoBtn').evaluate(n=>n.click());await frames(page,1);assert.deepEqual((await saved(page)).project.sheepTag,canonical.project.sheepTag,'Native Undo lost complete rule fields');
  await page.locator('#redoBtn').evaluate(n=>n.click());await frames(page,1);assert.equal((await saved(page)).project.sheepTag.preset,'archive');
  recordCase('native_classic_archive_rules_undo_redo');

  // A legal seventh-house pocket can be closed deliberately with fine snapping.
  // The engine must preserve this tactical mistake, with no forced relocation.
  const pocket=[];for(const dx of [-2.55,0,2.55])for(const dz of [-2.55,0,2.55])if((dx||dz)&&!(dx===0&&dz===-2.55))pocket.push({type:'st-farm',pos:[-18+dx,0,-18+dz]});
  const trap=fixture(canonical,models,{pieces:pocket});await load(page,trap);const beforeTrap=unit(await state(page)).pos;
  const closeTrap=await command(page,'build',{kind:'st-farm',x:-18,z:-20.55});assert.equal(closeTrap.ok,true,'Precision house closure was automatically corrected');
  let s=await until(page,s=>s.buildings.length===8&&s.buildings.every(b=>b.progress===1),'Deliberate tight-house construction',100);
  const rejected=await command(page,'move',{x:-18,z:-10});assert.equal(rejected.ok,false,'Trapped sheep escaped through a too-tight gap');assert.match(rejected.reason,/route|clear/i);
  assert.ok(Math.abs(unit(s).pos[0]-beforeTrap[0])<1.35&&Math.abs(unit(s).pos[2]-beforeTrap[2])<1.35,'House placement forcibly moved the sheep outside its pocket');
  const preview=await page.evaluate(()=>window.SWYRL_ENGINE_SHEEP_TAG.previewPath({from:[-18,-18],to:[-18,-10],species:'sheep'}));
  assert.equal(preview.reachable,false,'Species preview hides deliberate self-trapping');
  await page.screenshot({path:resolve(output,mode.name+'-precision-self-trap.png')});await stop(page);
  assert.deepEqual(authored(await saved(page)),authored(trap.data),'Stop retained runtime pocket closure');recordCase('fine_placement_deliberate_self_trap');

  // An actual wolf bot demolishes a boundary-to-boundary house barrier and
  // follows its breach. The sheep remains controlled rather than test-teleported.
  const barrier=[];for(let x=-24;x<=24;x+=3)barrier.push({type:'st-farm',pos:[x,0,-6]});
  const breach=fixture(canonical,models,{sheep:[[1.5,0,3]],wolves:[[1.5,0,-14]],pieces:barrier,
    pen:[20,0,20],rules:{bounds:26,headstart:0,wolfVision:30,sheepVision:30,wolfDamage:85,wolfSpeed:7.2}});
  await load(page,breach);const intact=(await state(page)).buildings.length;
  s=await until(page,s=>s.buildings.some(b=>b.hp<b.maxHp),'Wolf bot visible house damage',200);
  assert.match(unit(s,breach.wolves[0]).ai.intent,/breach|demolish/i,'Wolf damaged a farm without choosing a breach');
  s=await until(page,s=>s.buildings.length<intact,'Wolf bot house demolition',160);
  assert.ok(s.attacks.length||s.buildings.some(b=>b.damageAt>0),'Wolf pressure has no actual damage evidence');
  s=await until(page,s=>unit(s,breach.wolves[0]).pos[2]>-4.5||unit(s,breach.sheep[0]).captured,'Wolf bot traversal through its demolished opening',160);
  assert.ok(unit(s,breach.wolves[0]).pos[2]>-4.5||unit(s,breach.sheep[0]).captured,'Wolf stopped after breaching the house maze');
  await page.screenshot({path:resolve(output,mode.name+'-wolf-breach.png')});await stop(page);recordCase('wolf_ai_damage_demolition_breach_pursuit');

  // A bot creates a compact, purposeful base and keeps a real sheep-sized exit.
  const builders=fixture(canonical,models,{sheep:[[-24,0,18],[18,0,-18]],wolves:[[-24,0,-24]]});await load(page,builders);
  s=await until(page,s=>s.buildings.filter(b=>b.owner===builders.sheep[1]&&b.progress===1).length>=3,'Purposeful sheep bot layout',500);
  const bot=unit(s,builders.sheep[1]),houses=s.buildings.filter(b=>b.owner===bot.id);
  assert.match(bot.ai.intent,/maze|exit|build/i);assert.ok(bot.ai.base,'Bot has no deliberate base choice');
  for(const b of houses)assert.ok(distance(b.pos,bot.ai.base)<=10.5,'Bot scattered houses without a coherent maze');
  const exit=await page.evaluate(({from,to})=>window.SWYRL_ENGINE_SHEEP_TAG.previewPath({from,to,species:'sheep'}),{from:bot.pos,to:[bot.ai.base[0],0,bot.ai.base[2]+7.5]});
  assert.equal(exit.reachable,true,'Bot sealed its only tested sheep escape lane');await stop(page);recordCase('purposeful_sheep_bot_maze_and_usable_exit');

  // Fog hides actual enemy actors, minimap markers, selection and resources.
  // Then a faster sheep leaves sight; the hunter may search only stale memories.
  const fog=fixture(canonical,models,{sheep:[[-18,0,-18]],wolves:[[18,0,18]],rules:{fogMode:'solo',sheepVision:8,wolfVision:8}});await load(page,fog);
  let safe=await view(page);assert.ok(!safe.units.some(u=>u.id===fog.wolves[0]),'Fog leaked an unseen wolf into player view');
  assert.ok(!Object.hasOwn(safe.resources,fog.wolves[0]),'Fog leaked hostile economy');
  assert.equal((await command(page,'select',{id:fog.wolves[0]})).ok,false,'Hidden wolf is selectable');
  const hiddenRender=await render(page);assert.equal(hiddenRender.units.find(u=>u.id===fog.wolves[0]).visible,false,'Hidden enemy actor remains rendered');
  assert.ok(!(await ui(page)).minimap.unitIds.includes(fog.wolves[0]),'Hidden enemy is drawn on minimap');
  assert.ok(safe.fog.visible.length&&safe.fog.explored.length&&safe.fog.visible.length<safe.fog.width**2,'Fog did not keep unexplored map cells');
  await page.screenshot({path:resolve(output,mode.name+'-fog-hidden-enemy.png')});await stop(page);
  const memory=fixture(canonical,models,{sheep:[[-12,0,-12]],wolves:[[-12,0,-6.3]],rules:{headstart:0,fogMode:'solo',sheepVision:6,wolfVision:6,sheepSpeed:10,wolfSpeed:2}});await load(page,memory);
  await move(page,-24,-24);s=await until(page,s=>/last-observed/.test(unit(s,memory.wolves[0]).ai.intent),'Wolf last-known search after losing sight',120);
  const hunter=unit(s,memory.wolves[0]),last=hunter.ai.lastKnown.find(m=>m.id===memory.sheep[0]);
  assert.ok(last&&last.seenAt<s.elapsed,'Hunter has no time-stamped last sighting');
  assert.ok(distance(last.pos,unit(s,memory.sheep[0]).pos)>2,'Hunter memory tracks invisible live coordinates');
  assert.ok(distance([hunter.order.x,0,hunter.order.z],last.pos)<.2,'Hunter search order follows unseen live sheep instead of remembered location');
  assert.ok(!(await view(page)).units.some(u=>u.id===memory.wolves[0]),'Sheep HUD still exposes a hunter outside its sight');
  await stop(page);recordCase('fog_actual_actor_minimap_selection_and_ai_last_known');

  // Contact probability endpoints are reproducible. Staying inside a bush or
  // reentering during cooldown must not repeatedly refresh a temporary prick.
  for(const chance of [0,1]){
    const hazard=fixture(canonical,models,{sheep:[[-22,0,-18]],pieces:[{type:'st-thorn',pos:[-18,0,-18]}],rules:{thorns:true,thornChance:chance,thornCooldown:6,thornDuration:15,scentInterval:2}});
    await load(page,hazard);await move(page,-18,-18);s=await until(page,s=>distance(unit(s).pos,[-18,0,-18])<.3,'Actual thorn contact',80);
    const firstExpiry=unit(s).scentUntil;
    if(chance===0)assert.equal(firstExpiry,0,'Zero-chance thorn pricked a sheep');else assert.ok(firstExpiry>s.elapsed+12,'Guaranteed contact failed to start temporary tracking');
    await frames(page,40);assert.equal(unit(await state(page)).scentUntil,firstExpiry,'Staying in a bush rerolled the prick every frame');
    await move(page,-22,-18);await until(page,s=>distance(unit(s).pos,[-22,0,-18])<.3,'Leave thorn bush',80);
    await move(page,-18,-18);s=await until(page,s=>distance(unit(s).pos,[-18,0,-18])<.3,'Early reentry into thorn bush',80);
    assert.equal(unit(s).scentUntil,firstExpiry,'Reentry bypassed thorn cooldown');
    await frames(page,90);await move(page,-22,-18);await until(page,s=>distance(unit(s).pos,[-22,0,-18])<.3,'Second thorn exit',80);
    await move(page,-18,-18);s=await until(page,s=>distance(unit(s).pos,[-18,0,-18])<.3,'Fresh thorn entry after cooldown',80);
    if(chance===1){assert.ok(unit(s).scentUntil>firstExpiry+5,'Fresh legal thorn entry never rolled again');
      assert.equal((await command(page,'role',{role:'wolf'})).ok,true);await frames(page,1);safe=await view(page);
      assert.ok(safe.scentClues.length,'Pricked sheep has no hunting opportunity');
      for(const clue of safe.scentClues){assert.ok(clue.radius>=2,'Scent clue is an exact position marker');assert.ok(!Object.hasOwn(clue,'id')&&!Object.hasOwn(clue,'unitId'),'Scent clue discloses the tracked unit');}
      const clue=structuredClone(safe.scentClues.at(-1));
      close(clue.x/1.5,Math.round(clue.x/1.5),'Approximate scent lattice X');close(clue.z/1.5,Math.round(clue.z/1.5),'Approximate scent lattice Z');
      assert.equal((await command(page,'role',{role:'sheep'})).ok,true);await move(page,-25,-18);await frames(page,10);
      assert.equal((await command(page,'role',{role:'wolf'})).ok,true);await frames(page,1);
      const frozenClue=(await view(page)).scentClues.find(c=>c.expires===clue.expires);
      assert.ok(frozenClue,'Scent pulse expired before its documented window');assert.deepEqual(frozenClue,clue,'Scent clue followed live invisible sheep coordinates');
      await page.screenshot({path:resolve(output,mode.name+'-approximate-thorn-scent.png')});
    }else assert.equal(unit(s).scentUntil,0,'Zero-chance reentry produced scent');
    await stop(page);assert.deepEqual(authored(await saved(page)),authored(hazard.data),'Thorn effects remained in native project after Stop');
  }
  recordCase('thorn_probability_entry_cooldown_temporary_approximate_scent');

  // Nine means nine including the converted original house. Concealment and
  // reveal are gradual, and removing a supporting house removes the benefit.
  const settlement=[];for(const dx of [-3,0,3])for(const dz of [-3,0,3])settlement.push({type:'st-farm',pos:[-18+dx,0,-18+dz]});
  const totem=fixture(canonical,models,{sheep:[[-16.5,0,-16.5]],pieces:settlement,rules:{totems:true,densityRadius:8,totemRadius:5.5,fadeSeconds:3,revealSeconds:2,totemLimit:'once'}});
  await load(page,totem);const housesBefore=(await state(page)).buildings.length;
  assert.equal((await command(page,'select',{id:totem.buildings[4]})).ok,true);await frames(page,1);
  if(!await page.locator('#stTotem').isVisible())await tap(page,'stMoreActions');
  assert.equal(await page.locator('#stTotem').isDisabled(),false,'Nine-house conversion is unavailable');await tap(page,'stTotem');
  s=await state(page);assert.equal(s.buildings.length,housesBefore,'Totem conversion created a free extra house');assert.equal(s.buildings.filter(b=>b.kind==='st-totem').length,1);
  assert.equal(s.progression.density,9,'Converted original house stopped counting toward its settlement');
  await frames(page,20);s=await state(page);assert.ok(unit(s).concealment>.2&&unit(s).concealment<.5,'Stealth became an instant binary toggle');
  const fadeRender=await render(page);assert.ok(fadeRender.units.find(u=>u.id===s.controlledId).opacity<1,'Concealment did not fade actual character materials');
  await frames(page,60);assert.ok(unit(await state(page)).concealment>.95,'Nearby sheep never became concealed');
  assert.equal((await command(page,'totem',{id:totem.buildings[0]})).ok,false,'One-per-match totem rule was ignored');
  await move(page,-9,-16.5);s=await until(page,s=>distance(unit(s).pos,[-9,0,-16.5])<.3,'Leave stealth settlement',100);
  assert.ok(unit(s).concealment>0&&unit(s).concealment<1,'Leaving the totem did not gradually restore visibility');
  await frames(page,45);assert.equal(unit(await state(page)).concealment,0,'Visibility never returned outside settlement');
  await move(page,-16.5,-16.5);await until(page,s=>distance(unit(s).pos,[-16.5,0,-16.5])<.3,'Return to stealth settlement',100);await frames(page,65);
  assert.ok(unit(await state(page)).concealment>.95);assert.equal((await command(page,'sell',{id:totem.buildings[0]})).ok,true,'Supporting house cannot be removed');
  await frames(page,20);s=await state(page);assert.equal(s.buildings.length,8);assert.ok(unit(s).concealment>.35&&unit(s).concealment<.75,'Support loss did not start gradual reveal');
  await frames(page,25);assert.equal(unit(await state(page)).concealment,0,'Unsupported eight-house settlement kept its stealth bonus');
  await page.screenshot({path:resolve(output,mode.name+'-nine-house-totem.png')});await stop(page);
  assert.deepEqual(authored(await saved(page)),authored(totem.data),'Totem conversion or material fading altered authored map');recordCase('nine_house_conversion_gradual_fade_reveal_support_removal');

  // Upper routes require an actual connected ramp. They travel above ground
  // water and houses, then descend an actual exit with continuous positions.
  const elevatedPieces=[{type:'st-ramp',pos:[-18,0,-12]},{type:'st-wall',pos:[-18,0,-18]},
    {type:'st-wall',pos:[-18,0,-24]},{type:'st-ramp',pos:[-18,0,-30],rotation:[0,Math.PI,0]},
    {type:'st-pond',pos:[-18,0,-18]},{type:'st-farm',pos:[-18,0,-24]}];
  const elevated=fixture(canonical,models,{sheep:[[-18,0,-6]],pieces:elevatedPieces,rules:{elevated:true}});await load(page,elevated);
  const groundStart=unit(await state(page)).pos;const route=await command(page,'move',{x:-18,z:-25,layer:'upper'});assert.equal(route.ok,true,'Connected ramp route rejected: '+JSON.stringify(route));
  assert.deepEqual(unit(await state(page)).pos,groundStart,'An upper destination teleported directly to a roof');
  let climbed=false,crossedWater=false,crossedFarm=false,lastPos=groundStart;
  for(let i=0;i<160;i+=4){await frames(page,4);s=await state(page);const p=unit(s).pos;
    assert.ok(Math.hypot(p[0]-lastPos[0],p[1]-lastPos[1],p[2]-lastPos[2])<=s.rules.sheepSpeed*.2+.08,'Upper movement jumped between surfaces');
    climbed||=p[1]>.25&&p[1]<s.rules.wallHeight-.25;
    crossedWater||=Math.abs(p[2]+18)<1&&p[1]>3;crossedFarm||=Math.abs(p[2]+24)<1&&p[1]>3;lastPos=p;
    if(distance(p,[-18,0,-25])<.3)break;
  }
  assert.ok(climbed&&crossedWater&&crossedFarm,'Upper route did not climb continuously over water and farms');assert.ok(unit(s).onUpper&&distance(unit(s).pos,[-18,0,-25])<.3,'Sheep did not reach connected deck');
  if(!await page.locator('#stExitWall').isVisible())await tap(page,'stMoreActions');await tap(page,'stExitWall');
  s=await until(page,s=>!unit(s).onUpper&&Math.abs(unit(s).pos[1])<.05,'Continuous connected-ramp ground exit',140);
  assert.ok(unit(s).pos[2]<-32||unit(s).pos[2]>-9,'Upper exit silently dropped through a middle wall');
  await page.screenshot({path:resolve(output,mode.name+'-connected-raised-route.png')});await stop(page);recordCase('connected_ramp_continuous_pond_house_crossing_and_ground_exit');
  const disconnected=fixture(canonical,models,{pieces:[{type:'st-ramp',pos:[-18,0,-12]},{type:'st-wall',pos:[-18,0,-19]}],sheep:[[-18,0,-6]],rules:{elevated:true}});
  await load(page,disconnected);const noRoute=await command(page,'move',{x:-18,z:-20,layer:'upper'});assert.equal(noRoute.ok,false,'Disconnected raised decks created an invisible bridge');assert.match(noRoute.reason,/connect|entrance/i);
  assert.equal(unit(await state(page)).onUpper,false);await stop(page);recordCase('disconnected_deck_rejects_top_teleport');

  // Both species may ascend when configured. A ground wolf underneath a deck
  // cannot tag through its height, but demolition removes that tactical cover.
  const pursuit=fixture(canonical,models,{sheep:[[24,0,24]],wolves:[[-18,0,-6]],pieces:elevatedPieces.slice(0,2),rules:{role:'wolf',headstart:0,elevated:true,wolvesUseRamps:true}});
  await load(page,pursuit);const wolfGround=unit(await state(page)).pos;assert.equal((await command(page,'move',{x:-18,z:-20,layer:'upper'})).ok,true);
  assert.deepEqual(unit(await state(page)).pos,wolfGround,'Wolf upper pursuit teleported');
  s=await until(page,s=>unit(s).onUpper&&unit(s).pos[1]>3&&distance(unit(s).pos,[-18,0,-20])<.3,'Actual wolf ramp pursuit',160);
  await stop(page);
  const roof=fixture(canonical,models,{sheep:[[-18,0,-6],[24,0,-24]],wolves:[[-16,0,-18]],pieces:elevatedPieces.slice(0,2),rules:{headstart:8,elevated:true,wolvesUseRamps:false,wolfDamage:85,wolfSpeed:2,fogMode:'team',wolfVision:6}});
  await load(page,roof);await move(page,-17.07,-18,{layer:'upper'});s=await until(page,s=>unit(s).onUpper&&distance(unit(s).pos,[-17.07,0,-18])<.06,'Reach deck over ground hunter',140);
  const groundReach=s.rules.wolfRadius+s.rules.sheepRadius+.1;
  assert.ok(distance(unit(s,roof.wolves[0]).pos,unit(s).pos)<groundReach,'Height fixture has no hunter within ground tag range at the deck edge: '+JSON.stringify(s.units));
  await until(page,s=>s.headstartRemaining===0,'Release ground hunter for vertical-contact proof',180);
  await frames(page,25);s=await state(page);assert.equal(unit(s,roof.sheep[0]).captured,false,'Ground wolf tagged through the raised floor');
  assert.ok(distance(unit(s,roof.wolves[0]).pos,unit(s).pos)<groundReach,'Released hunter left the tested ground-contact range');
  assert.equal((await command(page,'role',{role:'wolf'})).ok,true);
  assert.equal((await command(page,'move',{x:-18,z:-18,layer:'upper'})).ok,false,'Disabled wolf ramp setting was ignored');
  assert.equal((await command(page,'attack',{id:roof.buildings[1]})).ok,true,'Wolf cannot attack a supporting wall');
  assert.equal((await command(page,'role',{role:'sheep'})).ok,true,'Restore control to keep the sheep on its chosen deck');
  s=await until(page,s=>!s.buildings.some(b=>b.id===roof.buildings[1]),'Occupied wall demolition',240);
  assert.ok(unit(s,roof.sheep[0]).pos[1]>0,'Destroyed deck teleported its occupant directly to ground');
  s=await until(page,s=>unit(s,roof.sheep[0]).captured,'Wolf tags only after destroyed-deck fall reaches ground',100);
  assert.equal(unit(s,roof.sheep[0]).kind,'wisp');await stop(page);recordCase('wolf_ramp_pursuit_elevation_aware_tag_and_deck_demolition');

  // Being above the pen cannot rescue through its roof. Ground rescue and a
  // separate connected extraction route allow the revived bot to follow on foot.
  const roofRescue=fixture(canonical,models,{sheep:[[-7.3,0,6],[24,0,-24]],wolves:[[24.2,0,-24]],pen:[-5,0,-5],
    pieces:[{type:'st-ramp',pos:[-7.3,0,1]},{type:'st-wall',pos:[-7.3,0,-5]}],rules:{headstart:0,elevated:true,wolfSpeed:2}});
  await load(page,roofRescue);await until(page,s=>unit(s,roofRescue.sheep[1]).captured,'Roof rescue teammate capture',10);
  await move(page,-7.3,-5,{layer:'upper'});await until(page,s=>unit(s).onUpper&&distance(unit(s).pos,[-7.3,0,-5])<.25,'Raised route directly above wisp',180);
  await frames(page,30);assert.equal(unit(await state(page),roofRescue.sheep[1]).captured,true,'Raised sheep rescued through the floor');await stop(page);
  const evacuation=fixture(canonical,models,{sheep:[[-12,0,-5],[24,0,-24]],wolves:[[24.2,0,-24]],pen:[-5,0,-5],
    pieces:[{type:'st-ramp',pos:[-5,0,-17]},{type:'st-wall',pos:[-5,0,-23]}],rules:{headstart:0,elevated:true,wolfSpeed:2,rescueHold:.6}});
  await load(page,evacuation);await until(page,s=>unit(s,evacuation.sheep[1]).captured,'Extraction teammate capture',10);
  assert.equal((await command(page,'rescue',{id:evacuation.sheep[1]})).ok,true);
  s=await until(page,s=>!unit(s,evacuation.sheep[1]).captured,'Actual held ground rescue',100);
  assert.ok(s.progression.xp>=s.rules.rescueXp,'Rescue did not earn real sheep progression');
  const rescuedGround=unit(s,evacuation.sheep[1]).pos;assert.ok(Math.abs(rescuedGround[1])<.05,'Ground rescue placed the ally on a roof');
  await move(page,-5,-24,{layer:'upper'});s=await until(page,s=>unit(s,evacuation.sheep[1]).onUpper&&unit(s,evacuation.sheep[1]).pos[1]>2,'Rescued ally walks connected ramp extraction',240);
  assert.ok(distance(rescuedGround,unit(s,evacuation.sheep[1]).pos)>6,'Rescued ally did not leave the spirit pen');
  assert.equal(s.counts.capturedSheep,0);await page.screenshot({path:resolve(output,mode.name+'-raised-wisp-extraction.png')});await stop(page);
  recordCase('height_aware_rescue_and_rescued_bot_connected_extraction');

  // Earn the unlock on engine time; the mirrored target keeps real geometry,
  // moves separately, costs no extra income and reveals no hostile copy flag.
  const illusion=fixture(canonical,models,{sheep:[[-18,0,-18]],rules:{split:true,splitUnlock:2,progressionSeconds:5,splitCooldown:12,splitLifetime:4}});await load(page,illusion);
  assert.equal((await command(page,'split')).ok,false,'Level-one sheep used a progression-gated ability');
  s=await until(page,s=>s.progression.splitUnlocked,'Real survival progression unlock',120);
  assert.ok(s.progression.level>=2);if(!await page.locator('#stSplit').isVisible())await tap(page,'stMoreActions');
  assert.equal(await page.locator('#stSplit').isDisabled(),false,'Earned Split remains unavailable in HUD');
  const incomeBefore=s.gold,splitElapsed=s.elapsed;await tap(page,'stSplit');s=await state(page);const copy=s.units.find(u=>u.isIllusion),real=unit(s);
  assert.ok(copy,'Visible Split produced no mirrored sheep');assert.equal(s.counts.sheep,1,'Illusion counted as another real sheep');
  assert.equal((await command(page,'split')).ok,false,'Split cooldown was ignored');
  const bodies=await render(page),realBody=bodies.units.find(u=>u.id===real.id),copyBody=bodies.units.find(u=>u.id===copy.id);
  assert.equal(copyBody.geometrySignature,realBody.geometrySignature,'Copy has visibly different body geometry');assert.ok(copyBody.opacity>.9,'Mirrored sheep is visibly transparent');
  await frames(page,24);s=await state(page);assert.ok(distance(unit(s).pos,unit(s,copy.id).pos)>4,'Real sheep and mirrored sheep never diverged');
  close(s.gold-incomeBefore,Math.floor(s.elapsed+1e-6)-Math.floor(splitElapsed+1e-6),'Illusion granted extra passive income');
  assert.equal((await command(page,'role',{role:'wolf'})).ok,true);await frames(page,1);safe=await view(page);
  const hostileTargets=safe.units.filter(u=>u.kind==='sheep');assert.equal(hostileTargets.length,2,'Visible wolf view lost one split target with fog off');
  for(const target of hostileTargets){assert.ok(!Object.hasOwn(target,'isIllusion')&&!Object.hasOwn(target,'progression')&&!Object.hasOwn(target,'ai'),'Wolf receives a privileged true-copy identity');assert.equal(target.name,'Sheep');assert.equal(target.order,null);}
  s=await until(page,s=>!s.units.some(u=>u.isIllusion),'Temporary split lifetime',100);assert.equal(s.counts.sheep,1);assert.equal(s.counts.capturedSheep,0);
  await stop(page);assert.deepEqual(authored(await saved(page)),authored(illusion.data),'Split left its copy in authored project');
  recordCase('earned_progression_plausible_split_divergence_cooldown_lifetime_no_enemy_identity');

  // A wolf commits to a plausible mirrored target after the level unlock.
  // Contact, rather than its lifetime, dissolves that target with no tag bounty.
  const contact=fixture(canonical,models,{sheep:[[-18,0,-18]],wolves:[[-12,0,-18]],rules:{headstart:5,split:true,splitUnlock:2,progressionSeconds:5,splitLifetime:12,wolfSpeed:12,fogMode:'off'}});
  await load(page,contact);await until(page,s=>s.progression.splitUnlocked,'Contact fixture earns Split before the hunt',120);
  assert.equal((await command(page,'split')).ok,true);s=await state(page);const contactCopy=s.units.find(u=>u.isIllusion),createdAt=s.elapsed;
  assert.ok(contactCopy);assert.equal((await command(page,'role',{role:'wolf'})).ok,true);await frames(page,8);
  assert.equal((await command(page,'attack',{id:contactCopy.id})).ok,true,'Wolf cannot choose a visible mirrored target');
  const bountyBefore=(await state(page)).gold;
  s=await until(page,s=>!s.units.some(u=>u.id===contactCopy.id),'Actual wolf contact dissolves mirrored target',100);
  assert.ok(s.elapsed-createdAt<5,'Decoy was removed by its timeout rather than wolf contact');assert.match(s.message,/contact|dissolv/i);
  assert.equal(s.counts.capturedSheep,0,'Contact with an illusion tagged the real sheep');assert.equal(s.winner,null);
  assert.equal(s.gold,bountyBefore,'Illusion contact granted a real sheep tag bounty');await stop(page);
  recordCase('actual_wolf_decoy_contact_without_capture_or_tag_bounty');

  // Warned seeded events are opt-in and spaced after their duration. Pause
  // freezes the warning and Restart repeats the seed-derived first event.
  const events=fixture(canonical,models,{sheep:[[-35,0,-35]],wolves:[[35,0,35]],rules:{events:true,headstart:0,eventInterval:30,eventWarning:5,eventDuration:5,eventPool:['pressure','fog','supply'],fogMode:'solo',wolfVision:6,sheepVision:6,wolfSpeed:2,seed:4321}});
  await load(page,events);s=await until(page,s=>s.event?.state==='warning','Warned seeded event',610);const firstKind=s.event.kind,warning=structuredClone(s.event);
  assert.ok(warning.warningRemaining>4.5,'Event started without usable advance warning');
  assert.match(await page.locator('#stEventBanner').innerText(),/experimental|starts|warning/i,'Warned event lacks visible feedback');
  await tap(page,'stPause');await frames(page,30);assert.deepEqual((await state(page)).event,warning,'Pause advanced experimental event warning');await tap(page,'stPause');
  s=await until(page,s=>s.event?.state==='active','Experimental event starts after warning',110);const firstEnd=s.event.endAt;
  assert.ok(s.event.remaining>4.5);await until(page,s=>!s.event,'Experimental event ends on actual clock',110);
  await frames(page,200);assert.equal((await state(page)).event,null,'Events ignored the safe spacing after duration');
  await tap(page,'stRestart');await frames(page,1);s=await until(page,s=>s.event?.state==='warning','Seeded event replay',610);
  assert.equal(s.event.kind,firstKind,'Same positive seed failed to reproduce first event');assert.ok(s.event.endAt<=firstEnd+.2);
  await stop(page);recordCase('opt_in_seeded_events_warning_duration_safe_spacing_pause_restart');

  // Curated creator paints native layered pieces in one Undo transaction and
  // compares the same .6-unit lane for differently sized species while stopped.
  const previewWall=[];for(let x=-15;x<=15;x+=3)previewWall.push({type:'st-farm',pos:[x,0,0]});
  const previewMap=fixture(canonical,models,{sheep:[[1.5,0,-6]],wolves:[[10,0,10]],pen:[-10,0,10],pieces:previewWall,rules:{bounds:16}});
  await load(page,previewMap,false);await tap(page,'stCreatorLauncher');
  const prePreview=authored(await saved(page));const comparison=await page.evaluate(()=>window.SWYRL_ENGINE_SHEEP_TAG_CREATOR.inspectPath({from:[1.5,-6],to:[1.5,6]}));
  assert.equal(comparison.results.find(r=>r.species==='sheep').reachable,true,'Creator rejects a legitimate sheep-sized .6 gap');
  assert.equal(comparison.results.find(r=>r.species==='wolf').reachable,false,'Creator claims a large wolf fits the same .6 gap');
  assert.match(await page.locator('#stCreatorFeedback').innerText(),/Sheep: route open/);assert.match(await page.locator('#stCreatorFeedback').innerText(),/Wolf:.*blocked|Wolf:.*No ground route/i);
  assert.equal((await state(page)).active,false,'Editor path preview secretly started a match');assert.deepEqual(authored(await saved(page)),prePreview,'Route helpers entered native serialization');
  await tap(page,'stCreatorClearRoute');assert.deepEqual(authored(await saved(page)),prePreview);await tap(page,'stCreatorClose');
  const creatorMap=fixture(canonical,models,{sheep:[[-24,0,-24]],wolves:[[24,0,24]]});await load(page,creatorMap,false);await tap(page,'stCreatorLauncher');
  assert.equal(await page.locator('#stCreatorPanel').isVisible(),true);
  const toolChoices=await page.locator('#stCreatorTool option').evaluateAll(nodes=>nodes.map(n=>n.value));
  for(const type of ['st-grass','st-earth','st-road','st-tree','st-rock','st-pond','st-thorn','st-sheep','st-wolf','st-pen','st-shop','st-zone','st-wall','st-ramp','route'])assert.ok(toolChoices.includes(type),'Creator lacks '+type);
  assert.ok(!toolChoices.includes('hero')&&!toolChoices.includes('script'),'Curated creator exposes arbitrary engine objects');
  await page.locator('#stCreatorTool').selectOption('st-road',{force:true});await page.locator('#stCreatorCells').selectOption('2',{force:true});
  await tap(page,'stCreatorFrame');await frames(page,1);const beforePaint=await saved(page);await worldTap(page,-18,-18);const afterPaint=await saved(page);
  assert.equal(afterPaint.scene.actors.filter(a=>a.type==='st-road').length,4,'Two-cell brush did not create four native road tiles');
  for(const actor of afterPaint.scene.actors.filter(a=>a.type==='st-road'))assert.ok(actor.baked&&actor.editorLayerIds.length,'Paint tile is not a baked layered native actor');
  await tap(page,'stCreatorUndo');await frames(page,1);assert.deepEqual(authored(await saved(page)),authored(beforePaint),'One native Undo failed to remove entire multi-tile brush');
  await tap(page,'stCreatorRedo');await frames(page,1);assert.deepEqual(authored(await saved(page)),authored(afterPaint),'Native Redo did not restore paint stroke');
  // The native history loader restores its saved camera mode. Creator history
  // must retain the working Top view as well as its projected painting sites.
  assert.equal((await page.evaluate(()=>window.SWYRL_ENGINE_SHEEP_TAG_CREATOR.paint({type:'st-earth',x:-10,z:-20,cells:1}))).ok,true);
  await page.locator('#cameraView').selectOption('top',{force:true});await frames(page,1);
  const topSite=await page.evaluate(()=>window.SWYRL_ENGINE_SHEEP_TAG.pointScreen(-10,-20));
  await tap(page,'stCreatorUndo');await frames(page,1);
  assert.equal(await page.locator('#cameraView').inputValue(),'top','Creator Undo lost its working Top view');
  const topAfterUndo=await page.evaluate(()=>window.SWYRL_ENGINE_SHEEP_TAG.pointScreen(-10,-20));
  close(topAfterUndo.x,topSite.x,'Top-view Undo painting site X');close(topAfterUndo.y,topSite.y,'Top-view Undo painting site Y');
  await tap(page,'stCreatorFrame');await frames(page,1);
  await page.locator('#stCreatorCells').selectOption('1',{force:true});
  for(const [type,x,z]of [['st-grass',-12,-18],['st-earth',-6,-18],['st-thorn',0,-18],['st-sheep',-24,-18],['st-wolf',24,-18],['st-zone',12,-18]]){
    await page.locator('#stCreatorTool').selectOption(type,{force:true});await worldTap(page,x,z);
  }
  let designed=await saved(page);assert.equal(designed.scene.actors.filter(a=>a.type==='st-sheep').length,2);assert.equal(designed.scene.actors.filter(a=>a.type==='st-wolf').length,2);
  assert.equal(designed.scene.actors.filter(a=>a.type==='st-zone').length,1,'Creator did not author a no-build zone');
  const controls=await page.locator('#stCreatorTool,#stCreatorUndo,#stCreatorRedo,#stCreatorPlay').evaluateAll(nodes=>nodes.map(n=>{const r=n.getBoundingClientRect();return {id:n.id,width:r.width,height:r.height};}));
  for(const c of controls)assert.ok(c.width>=44&&c.height>=44,'Creator phone control too small: '+c.id);
  for(const summary of await page.locator('#stCreatorPanel details summary').all())await summary.evaluate(n=>n.click());
  await page.locator('#stCreatorFog').selectOption('team',{force:true});await page.locator('#stCreatorRule-thorns').check({force:true});
  assert.equal(await page.locator('#stCreatorRule-events').isChecked(),false,'Creator enables random events without a choice');await tap(page,'stCreatorApplyRules');await frames(page,1);
  const pendingMap=page.waitForEvent('download');await tap(page,'stCreatorExport');const downloadedMap=JSON.parse(await readFile(await (await pendingMap).path(),'utf8'));
  assert.equal(downloadedMap.schema,'swyrl-sheep-tag-map-v1');assert.ok(!downloadedMap.project&&!downloadedMap.scene&&!downloadedMap.scripts,'Independent map export contains a full engine project or scripts');
  const validation=await page.evaluate(map=>window.SWYRL_ENGINE_SHEEP_TAG_CREATOR.validateMap(map),downloadedMap);assert.equal(validation.ok,true,'Valid portable creator map rejected');
  for(const invalid of ['script','unknown-piece','missing-wolf','duplicate-pen','nonfinite-position','outside-bounds','missing-layer']){
    const result=await page.evaluate(({map,invalid})=>{const data=structuredClone(map);
      if(invalid==='script')data.scripts=['window.alert(1)'];
      if(invalid==='unknown-piece')data.actors[0].type='hero';
      if(invalid==='missing-wolf')data.actors=data.actors.filter(a=>a.type!=='st-wolf');
      if(invalid==='duplicate-pen'){const a=structuredClone(data.actors.find(a=>a.type==='st-pen'));a.id+='-extra';data.actors.push(a);}
      if(invalid==='nonfinite-position')data.actors[0].position[0]=NaN;
      if(invalid==='outside-bounds')data.actors[0].position[0]=100000;
      if(invalid==='missing-layer')data.actors[0].layers=['not-an-authored-layer'];
      return window.SWYRL_ENGINE_SHEEP_TAG_CREATOR.validateMap(data);
    },{map:downloadedMap,invalid});assert.equal(result.ok,false,'Portable map validator accepted '+invalid);
  }
  const added=await page.evaluate(()=>window.SWYRL_ENGINE_SHEEP_TAG_CREATOR.paint({type:'st-tree',x:-30,z:12,cells:1}));assert.equal(added.ok,true);const beforeImport=await saved(page);
  await page.locator('#stCreatorFile').setInputFiles({name:'acceptance.sheep-tag-map.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(downloadedMap))});
  await page.waitForFunction(count=>window.SWYRL_ENGINE_AGENT.inspectScene().scene.actors.length===count,downloadedMap.actors.length,{polling:100});await frames(page,2);
  const roundtrip=await page.evaluate(()=>window.SWYRL_ENGINE_SHEEP_TAG_CREATOR.exportMap());assert.equal(roundtrip.ok,true);
  assert.deepEqual(mapSemantics(roundtrip.map),mapSemantics(downloadedMap),'Portable map import changed species, terrain, rules, or layer membership');
  await tap(page,'stCreatorUndo');await frames(page,1);assert.deepEqual(authored(await saved(page)),authored(beforeImport),'Native Undo failed to restore map before independent import');
  await tap(page,'stCreatorRedo');await frames(page,1);assert.deepEqual(mapSemantics((await page.evaluate(()=>window.SWYRL_ENGINE_SHEEP_TAG_CREATOR.exportMap())).map),mapSemantics(downloadedMap));
  const pendingProject=page.waitForEvent('download');await tap(page,'stCreatorSaveProject');const fullProject=JSON.parse(await readFile(await (await pendingProject).path(),'utf8'));
  assert.deepEqual(authored(fullProject),authored(await saved(page)),'Creator native Save lost authored layers or rules');
  const playtestBaseline=await saved(page);await tap(page,'stCreatorPlay');await frames(page,2);s=await state(page);
  assert.equal(s.active,true,'Creator one-click Playtest did not use native Play');assert.equal(await page.locator('#stCreatorPanel').isVisible(),false,'Creator panel covers match controls');
  const zone=await command(page,'preview',{kind:'st-farm',x:12,z:-18});assert.equal(zone.ok,false,'Creator no-build zone allows construction');assert.match(zone.reason,/zone|prohibit|no.build/i);
  assert.equal((await page.evaluate(()=>window.SWYRL_ENGINE_SHEEP_TAG_CREATOR.paint({type:'st-road',x:-12,z:-12}))).ok,false,'Creator edits a live match');
  await tap(page,'stStop');await frames(page,2);assert.equal(await page.locator('#stCreatorPanel').isVisible(),true,'Stop did not return to creator revision');
  assert.deepEqual(authored(await saved(page)),authored(playtestBaseline),'Creator Playtest saved runtime positions or structures');
  await page.screenshot({path:resolve(output,mode.name+'-curated-map-creator.png')});await tap(page,'stCreatorClose');
  await page.evaluate(data=>window.SWYRL_ENGINE_AGENT.loadScene(data),canonical);await frames(page,2);assert.deepEqual(authored(await saved(page)),authored(canonical),'Final starter restoration failed');
  assert.deepEqual(errors,[],'Unhandled browser errors: '+errors.join('\n'));
  recordCase('curated_species_path_preview_without_match_or_saved_helpers','creator_canvas_layered_paint_spawns_zones_undo_redo',
    'independent_map_file_validation_import_native_history_save','creator_one_click_native_playtest_stop_revision');
  receipts.push({mode:mode.name,mapActors:canonical.scene.actors.length,layers:canonical.editor.layers.length,cases,controls,pass:true});
  console.log('SHEEP_ARCHIVE_'+mode.name.toUpperCase()+'_ALL_'+cases.length+'_CASES_PASS');await context.close();
}
await writeFile(resolve(output,'receipt.json'),JSON.stringify({pass:true,viewports:receipts},null,2));console.log(modes.length===2?'SHEEP_ARCHIVE_ALL_VIEWPORTS_PASSED':'SHEEP_ARCHIVE_SELECTED_VIEWPORT_PASSED');
}finally{await browser.close();}
