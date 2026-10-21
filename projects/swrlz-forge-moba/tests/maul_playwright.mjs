import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {mkdir,readFile,writeFile} from 'node:fs/promises';
import {resolve} from 'node:path';

// Ordinary native editor fixtures are imported only while stopped. Real mouse
// and phone touch drive Play, placement and tower orders. The controlled clock
// advances the existing engine RAF; it never edits combat, economy or match state.
const base=(process.env.SWYRL_ANIME_TEST_URL||'http://127.0.0.1:8765').replace(/\/$/,'');
const query=new URLSearchParams(process.env.SWYRL_ANIME_TEST_QUERY||'');query.set('project','maul-frostveil');
const output=resolve(process.env.SWYRL_ANIME_SCREENSHOTS_DIR||'maul-acceptance');await mkdir(output,{recursive:true});
const modes=[{name:'desktop',viewport:{width:1600,height:1000},isMobile:false,hasTouch:false},
  {name:'mobile',viewport:{width:412,height:915},isMobile:true,hasTouch:true}]
  .filter(mode=>!process.env.SWYRL_ANIME_TEST_MODE||process.env.SWYRL_ANIME_TEST_MODE===mode.name);
assert.ok(modes.length,'SWYRL_ANIME_TEST_MODE must be desktop or mobile');
const browser=await chromium.launch({headless:true,
  ...(process.env.SWYRL_CHROMIUM_PATH?{executablePath:process.env.SWYRL_CHROMIUM_PATH}:{}),
  args:['--no-sandbox','--disable-dev-shm-usage','--enable-webgl','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader']});
const touchPages=new WeakSet(),touchSessions=new WeakMap(),receipts=[];
const kinds=['arrow','cannon','frost','storm','maze-wall'];
const buttons={arrow:'maulBuildArrow',cannon:'maulBuildCannon',frost:'maulBuildFrost',storm:'maulBuildStorm','maze-wall':'maulBuildWall'};
const state=page=>page.evaluate(()=>window.SWYRL_ENGINE_MAUL.status());
const ui=page=>page.evaluate(()=>window.SWYRL_ENGINE_MAUL.uiStatus());
const saved=page=>page.evaluate(()=>window.SWYRL_ENGINE_AGENT.inspectScene());
const preflight=page=>page.evaluate(()=>window.SWYRL_ENGINE_MAUL.preflight());
const runStatus=page=>page.evaluate(()=>window.SWYRL_ENGINE_RUNS.status());
const runData=(page,id=null)=>page.evaluate(id=>window.SWYRL_ENGINE_RUNS.data(id),id);
const runFrame=(page,run,t=null)=>page.evaluate(({run,t})=>window.SWYRL_ENGINE_RUNS.frame(run,t),{run,t});
const frames=(page,count=1,ms=50)=>page.evaluate(({count,ms})=>window.__maulClock.step(count,ms),{count,ms});
const authored=data=>({project:data.project,layers:data.editor.layers,background:data.scene.background,actors:data.scene.actors,paths:data.scene.paths});
const close=(actual,expected,label,tolerance=1e-4)=>assert.ok(Number.isFinite(actual)&&Math.abs(actual-expected)<=tolerance,
  label+': expected '+expected+', received '+actual);
const towerTypes=new Set(kinds.map(kind=>'maul-'+kind));
const world=(map,cx,cz)=>({x:map.origin.x+cx*map.cell,z:map.origin.z+cz*map.cell});
async function installClock(context){await context.addInitScript(()=>{
  const nativeRAF=requestAnimationFrame.bind(window),nativeCancel=cancelAnimationFrame.bind(window),nativeNow=performance.now.bind(performance),queue=new Map();
  let frozen=false,now=0,next=1000000000;Object.defineProperty(performance,'now',{configurable:true,value:()=>frozen?now:nativeNow()});
  window.requestAnimationFrame=callback=>{if(!frozen)return nativeRAF(callback);const id=next++;queue.set(id,callback);return id;};
  window.cancelAnimationFrame=id=>{queue.delete(id);nativeCancel(id);};
  window.__maulClock={freeze:()=>{frozen=true;now=nativeNow();return new Promise(resolve=>nativeRAF(()=>nativeRAF(resolve)));},
    step:(count,ms)=>{if(!frozen)throw Error('Clock is not frozen');for(let i=0;i<count;i++){now+=ms;const pending=[...queue.values()];queue.clear();
      if(!pending.length)throw Error('Real engine RAF stopped');for(const callback of pending)callback(now);}return {now,pending:queue.size};}};
});}
async function press(page,selector){const node=page.locator(selector);assert.equal(await node.isVisible(),true,'Hidden required control '+selector);
  await node.evaluate(element=>element.scrollIntoView({block:'nearest',inline:'nearest'}));
  const box=await node.boundingBox();assert.ok(box,'No hit rectangle for '+selector);
  assert.equal(await node.evaluate(element=>{const r=element.getBoundingClientRect(),hit=document.elementFromPoint(r.x+r.width/2,r.y+r.height/2);
    return element===hit||element.contains(hit);}),true,'A required control is obscured: '+selector);
  if(touchPages.has(page))await node.tap({force:true});else await node.click({force:true});}
async function tap(page,id){await press(page,'#'+id);}
async function native(page,id){
  if(touchPages.has(page)&&!(await page.locator('#'+id).isVisible())&&id==='simulateBtn'){
    await tap(page,'mobileToolsBtn');await page.locator('#mobileToolsPanel.show').waitFor({state:'visible'});
    await press(page,'#mobileToolsPanel [data-click="simulateBtn"]');
  }else await tap(page,id);
  await frames(page,2);
}
async function stop(page){if((await state(page)).active){await native(page,'maulStop');assert.equal((await state(page)).active,false);}}
async function importFixture(page,data){await stop(page);await page.evaluate(data=>window.SWYRL_ENGINE_AGENT.loadScene(data),data);await frames(page,2);
  assert.deepEqual(authored(await saved(page)),authored(data),'Stopped native import changed the authored map');}
async function play(page){await native(page,'playBtn');assert.equal((await state(page)).active,true,'Native Play rejected the authored map: '+JSON.stringify(await preflight(page)));}
async function load(page,data){await importFixture(page,data);await play(page);}
async function sector(page,index){await page.locator('#maulSector').selectOption(String(index),{force:true});await frames(page,2);
  assert.equal((await state(page)).selectedSector,index,'Sector UI did not select the actual builder sector');}
async function until(page,predicate,label,max=400){let s=await state(page);for(let i=0;i<max&&!predicate(s);i+=4){await frames(page,Math.min(4,max-i));s=await state(page);}
  assert.ok(predicate(s),label+' did not occur in native Play: '+JSON.stringify({phase:s.phase,wave:s.wave,kills:s.kills,leaks:s.leaks,lives:s.lives,elapsed:s.elapsed}));return s;}
async function canvasPoint(page,map,cx,cz,{placing=false,y=0}={}){const p=world(map,cx,cz),screen=await page.evaluate(({x,z,y})=>window.SWYRL_ENGINE_MAUL.pointScreen(x,z,y),{...p,y});
  assert.ok(screen?.visible,'Grid cell is outside the actual camera: '+JSON.stringify({cx,cz,screen}));
  if(placing&&touchPages.has(page))screen.y+=80;
  assert.equal(await page.evaluate(p=>{const hit=document.elementFromPoint(p.x,p.y);return hit?.tagName==='CANVAS'||hit?.id==='viewport';},screen),true,
    'Physical grid input hits an editor or HUD panel: '+JSON.stringify({cx,cz,screen}));return screen;}
async function screenTap(page,p){if(touchPages.has(page))await page.touchscreen.tap(p.x,p.y);else await page.mouse.click(p.x,p.y);await frames(page,1);}
async function gridTap(page,map,cx,cz,placing=false){await screenTap(page,await canvasPoint(page,map,cx,cz,{placing}));}
async function touchEvent(page,type,p){await touchSessions.get(page).send('Input.dispatchTouchEvent',{type,
  touchPoints:p?[{x:p.x,y:p.y,radiusX:2,radiusY:2,force:1,id:0}]:[]});}
async function preview(page,map,cx,cz){const p=await canvasPoint(page,map,cx,cz,{placing:true});
  if(touchPages.has(page)){await touchEvent(page,'touchStart',p);await frames(page,1);const result=(await ui(page)).preview;
    await touchEvent(page,'touchCancel');await frames(page,1);return result;}
  await page.mouse.move(p.x,p.y);await frames(page,1);return (await ui(page)).preview;}
async function build(page,kind,map,cx,cz){if((await ui(page)).buildKind!==kind)await native(page,buttons[kind]);
  const guide=await preview(page,map,cx,cz);assert.equal(guide?.valid,true,'Visible grid preview rejects a legal '+kind+' cell: '+JSON.stringify(guide));
  assert.equal(guide.cx,cx);assert.equal(guide.cz,cz);close(guide.world.x,world(map,cx,cz).x,'Grid preview X');close(guide.world.z,world(map,cx,cz).z,'Grid preview Z');
  const before=await state(page);await gridTap(page,map,cx,cz,true);const after=await state(page),tower=after.towers.find(t=>!before.towers.some(old=>old.id===t.id));
  assert.ok(tower,'Physical release did not create a native tower');assert.equal(tower.kind,kind);assert.equal(tower.cx,guide.cx);assert.equal(tower.cz,guide.cz);return tower;}
async function selectTower(page,map,tower){if((await ui(page)).buildKind)await native(page,'maulCancel');const top=await canvasPoint(page,map,tower.cx,tower.cz,{y:1.9});await screenTap(page,top);
  if(touchPages.has(page)){assert.equal((await ui(page)).selectedTowerId,null,'A single phone tap selected a tower');
    assert.equal((await ui(page)).lastTowerTap?.id,tower.id,'A phone tap did not identify the visible tower');await screenTap(page,top);}
  assert.equal((await ui(page)).selectedTowerId,tower.id,'The native tower selection did not complete');}
async function prototypes(page,canonical){const pieces=await page.evaluate(()=>{const result={};for(const kind of ['arrow','cannon','frost','storm','maze-wall']){
    const type='maul-'+kind,id=window.SWYRL_ENGINE_AGENT.spawn(type,{position:[-36,0,-36],name:'Acceptance '+type});window.SWYRL_ENGINE_AGENT.bake();
    result[kind]=window.SWYRL_ENGINE_AGENT.inspectScene().scene.actors.find(actor=>actor.id===id);}return result;});
  for(const kind of kinds)assert.equal(pieces[kind]?.type,'maul-'+kind,'Missing native editable prefab '+kind);
  await page.evaluate(data=>window.SWYRL_ENGINE_AGENT.loadScene(data),canonical);await frames(page,2);return pieces;}
function fixture(canonical,pieces,{rules={},towers=[]}={}){const data=structuredClone(canonical),map={cell:2,origin:{x:-30,z:-37}};
  data.project.maul={...data.project.maul,autoWaves:false,soloSupport:false,preparation:120,intermission:0,startGold:900,waves:1,lives:30,difficulty:1,...rules};
  data.scene.actors=data.scene.actors.filter(actor=>!towerTypes.has(actor.type));
  for(const [index,t]of towers.entries()){const p=world(map,t.cx,t.cz);data.scene.actors.push({...structuredClone(pieces[t.kind]),id:'acceptance-tower-'+index,
    name:'Authored '+t.kind+' '+index,position:[p.x,0,p.z],rotation:[0,0,0],scale:[1,1,1],baked:true,visible:true,manualVisible:true,
    maul:{level:t.level||1,priority:t.priority||'first'},editorLayerIds:['maul-layer-5']});}return data;}
async function configureRecorder(page,enabled){await native(page,'stRunLauncher');await page.locator('#stRunPanel').waitFor({state:'visible'});
  if((await page.locator('#stRunEnabled').isChecked())!==enabled)await tap(page,'stRunEnabled');await page.locator('#stRunCadence').selectOption('full',{force:true});
  await frames(page,1);assert.equal((await runStatus(page)).settings.enabled,enabled);await native(page,'stRunClose');}
async function exportMap(page,mode){const pending=page.waitForEvent('download',{timeout:15000});
  if(mode.hasTouch){await native(page,'maulRulesBtn');await tap(page,'maulRulesSave');}else await tap(page,'saveBtn');
  const file=await pending;await file.saveAs(resolve(output,mode.name+'-authored-map.swyrl.json'));const data=JSON.parse(await readFile(await file.path(),'utf8'));
  if(mode.hasTouch)await native(page,'maulRulesClose');return data;}
function reconstruct(run,t=run.duration){const result=structuredClone(run.initial);for(const frame of run.frames){if(frame.t>t+1e-8)break;
  for(const [id,patch]of Object.entries(frame.patch))if(patch===null)delete result.entities[id];else result.entities[id]={...(result.entities[id]||{}),...structuredClone(patch)};
  if(frame.camera)result.camera=structuredClone(frame.camera);if(frame.game)Object.assign(result.game,structuredClone(frame.game));}return result;}

try{for(const mode of modes){const context=await browser.newContext({viewport:mode.viewport,isMobile:mode.isMobile,hasTouch:mode.hasTouch});await installClock(context);
  const page=await context.newPage(),errors=[],cases=[];if(mode.hasTouch){touchPages.add(page);touchSessions.set(page,await context.newCDPSession(page));}
  page.on('pageerror',error=>errors.push(String(error)));page.setDefaultTimeout(30000);
  const pass=name=>{cases.push(name);console.log('MAUL_CASE_PASSED',mode.name,name);};
  try{
    await page.goto(base+'/index.html?'+query,{waitUntil:'domcontentloaded',timeout:60000});
    await page.waitForFunction(()=>window.SWYRL_ENGINE_MAUL?.uiStatus&&window.SWYRL_ENGINE_AGENT.project().canonicalId==='maul-frostveil',undefined,{timeout:60000});
    await page.locator('#perfPreset').selectOption('medium',{force:true});await page.evaluate(()=>window.__maulClock.freeze());await frames(page,2);
    assert.equal(await page.evaluate(()=>window.SWRLZ_FORGE_BUILD?.version),'v11.62','Wrong engine release');
    // Retain the complete published v10.6 geometry as an ordinary stopped editor fixture.
    const legacy=await page.evaluate(async()=>{const response=await fetch('scenes/maul-frostveil.swyrl.json');if(!response.ok)throw Error('Legacy Maul asset unavailable');return response.json();});
    await importFixture(page,legacy);
    const canonical=await saved(page),mapCheck=await preflight(page);
    assert.equal(canonical.project.kind,'maul');assert.equal(canonical.editor.layers.length,6);
    assert.equal(canonical.scene.actors.filter(a=>a.type==='maul-spawn').length,9);assert.equal(canonical.scene.actors.filter(a=>a.type==='maul-gate').length,9);
    assert.equal(canonical.scene.actors.filter(a=>a.type==='maul-builder').length,9);assert.equal(canonical.scene.actors.filter(a=>a.type==='maul-exit').length,1);
    assert.equal(mapCheck.ok,true,'Authored starter routes failed: '+mapCheck.errors.join(' '));assert.equal(mapCheck.paths?.length??mapCheck.map.spawns.length,9);
    const pieces=await prototypes(page,canonical),empty=fixture(canonical,pieces);
    pass('native_starter_has_nine_spawns_gates_builders_six_layers_and_open_routes');

    await page.evaluate(()=>window.SWYRL_ENGINE_AGENT.openProjects());await frames(page,2);
    await press(page,'[data-project-template="maul-frostveil"]');await frames(page,2);
    assert.equal((await saved(page)).project.canonicalId,'maul-frostveil');assert.equal((await saved(page)).project.maulLayout,'classic-v2','Projects must open the revised classic map');
    await importFixture(page,canonical);
    await play(page);let s=await state(page);assert.equal(s.wave,0);assert.equal(s.gold,canonical.project.maul.startGold);assert.ok(s.allyTowers>=16,'Solo support did not cover the other eight sectors');
    assert.ok((await page.evaluate(()=>window.SWYRL_ENGINE_MAUL.renderStatus())).meshes>=s.towers.length,'Native towers have no renderer objects');await stop(page);
    assert.deepEqual(authored(await saved(page)),authored(canonical));pass('project_hub_opens_playable_maul_with_optional_support_and_original_scene_restore');

    await native(page,'maulRulesBtn');await page.locator('#maulRule_startGold').fill('777');await page.locator('#maulRule_lives').fill('17');
    await page.locator('#maulRule_waves').fill('2');await page.locator('#maulRule_preparation').fill('12');await page.locator('#maulRule_intermission').fill('3');
    await page.locator('#maulRule_difficulty').selectOption('0.65',{force:true});
    for(const id of ['maulRule_autoWaves','maulRule_soloSupport'])if(await page.locator('#'+id).isChecked())await tap(page,id);
    await native(page,'maulRulesApply');await native(page,'maulRulesClose');const configured=await saved(page);
    assert.deepEqual(Object.fromEntries(['startGold','lives','waves','preparation','intermission','difficulty','autoWaves','soloSupport'].map(k=>[k,configured.project.maul[k]])),
      {startGold:777,lives:17,waves:2,preparation:12,intermission:3,difficulty:.65,autoWaves:false,soloSupport:false});
    const exported=await exportMap(page,mode);assert.deepEqual(authored(exported),authored(configured));await importFixture(page,exported);
    assert.equal((await preflight(page)).ok,true);pass('native_rules_dialog_and_project_download_round_trip_authored_settings_and_map');

    await load(page,empty);s=await state(page);await frames(page,30);const preparing=await state(page);
    assert.equal(preparing.phase,'preparation');assert.equal(preparing.wave,0);assert.equal(preparing.units.length,0);assert.equal(preparing.gold,900);
    assert.ok(preparing.elapsed>s.elapsed,'Native Play time never advances');assert.equal(preparing.allyTowers,0);await stop(page);
    pass('manual_preparation_waits_for_start_wave_and_disabling_support_removes_allies');

    await load(page,empty);await sector(page,0);let map=(await state(page)).map;const created=[];
    for(const [i,kind]of kinds.entries()){const before=await state(page),tower=await build(page,kind,map,2+i,4);created.push(tower);
      close((await state(page)).gold,before.gold-(await page.evaluate(kind=>window.SWYRL_ENGINE_MAUL.definitions[kind].cost,kind)),'Physical build cost '+kind);}
    assert.equal((await state(page)).towers.length,5);assert.equal((await preflight(page)).ok,true,'Runtime towers leaked into authoring preflight');
    await page.screenshot({path:resolve(output,mode.name+'-native-five-tower-family.png')});
    pass('physical_mouse_or_phone_placement_matches_grid_preview_for_all_five_build_families');

    for(const [cx,cz,reason]of [[0,4,/wall/i],[5,1,/spawn|gate|open/i]]){
      const before=await state(page),guide=await preview(page,map,cx,cz);assert.equal(guide?.valid,false,'An invalid grid cell displayed a legal footprint');assert.match(guide.reason,reason);
      await gridTap(page,map,cx,cz,true);const after=await state(page);assert.equal(after.towers.length,before.towers.length);assert.equal(after.gold,before.gold);}
    pass('cliff_and_protected_spawn_placement_show_invalid_preview_and_never_charge_gold');

    const beforeCancel=await state(page),cancelPoint=await canvasPoint(page,map,8,5,{placing:true});
    if(mode.hasTouch){await touchEvent(page,'touchStart',cancelPoint);await frames(page,1);assert.ok((await ui(page)).preview);await touchEvent(page,'touchCancel');}
    else{await page.mouse.move(cancelPoint.x,cancelPoint.y);await page.mouse.down();await frames(page,1);await page.keyboard.press('Escape');await page.mouse.up();}
    await frames(page,2);assert.equal((await state(page)).gold,beforeCancel.gold);assert.equal((await state(page)).towers.length,beforeCancel.towers.length);
    if((await ui(page)).buildKind)await native(page,'maulCancel');assert.equal((await ui(page)).buildKind,null);assert.equal((await ui(page)).preview,null);
    pass('cancelled_native_pointer_gesture_and_cancel_control_do_not_place_or_spend');

    const arrow=created[0];await selectTower(page,map,arrow);assert.equal(await page.locator('#maulUpgrade').isEnabled(),true);
    assert.match(await page.locator('#maulSelectedDetail').textContent(),/8 range/);const beforeUpgrade=await state(page);await native(page,'maulUpgrade');
    let selected=(await state(page)).towers.find(t=>t.id===arrow.id);assert.equal(selected.level,2);close((await state(page)).gold,beforeUpgrade.gold-35,'Arrow upgrade cost');
    assert.match(await page.locator('#maulSelectedDetail').textContent(),/9 range/);await page.locator('#maulPriority').selectOption('strong',{force:true});await frames(page,2);
    assert.equal((await state(page)).towers.find(t=>t.id===arrow.id).priority,'strong');const beforeSell=await state(page);await native(page,'maulSell');
    assert.equal((await state(page)).towers.some(t=>t.id===arrow.id),false);close((await state(page)).gold,beforeSell.gold+38,'70 percent total investment refund');
    assert.equal((await ui(page)).selectedTowerId,null);await stop(page);assert.deepEqual(authored(await saved(page)),authored(empty));
    pass('native_tower_selection_phone_double_tap_upgrade_range_target_priority_and_sell_refund');

    const blocked=fixture(canonical,pieces,{towers:Array.from({length:9},(_,i)=>i+1).filter(cx=>cx!==5).map(cx=>({kind:'maze-wall',cx,cz:5}))});
    await load(page,blocked);await sector(page,0);map=(await state(page)).map;await native(page,'maulBuildWall');
    const beforeBlock=await state(page),blockedGuide=await preview(page,map,5,5);assert.equal(blockedGuide?.valid,false,'The last route can be sealed');
    assert.match(blockedGuide.reason,/route|sector|exit/i);await gridTap(page,map,5,5,true);assert.equal((await state(page)).gold,beforeBlock.gold);
    assert.equal((await state(page)).towers.length,beforeBlock.towers.length);await stop(page);assert.deepEqual(authored(await saved(page)),authored(blocked));
    pass('actual_grid_placement_rejects_closing_last_ground_route_without_charge_or_author_corruption');

    await load(page,empty);map=(await state(page)).map;for(let i=0;i<9;i++){await sector(page,i);const sectorMap=map.sectors[i],p=world(map,(sectorMap.minX+sectorMap.maxX)/2,(sectorMap.minZ+sectorMap.maxZ)/2);
      const projected=await page.evaluate(p=>window.SWYRL_ENGINE_MAUL.pointScreen(p.x,p.z),p);assert.equal(projected.visible,true);}
    await native(page,'maulOverview');for(const sectorMap of map.sectors){const p=world(map,sectorMap.spawn.x,sectorMap.spawn.z);
      assert.equal((await page.evaluate(p=>window.SWYRL_ENGINE_MAUL.pointScreen(p.x,p.z),p)).visible,true,'Overview clips a sector entrance');}
    await page.screenshot({path:resolve(output,mode.name+'-nine-sector-overview.png')});await sector(page,0);
    pass('sector_controls_frame_each_builder_and_map_overview_keeps_all_nine_entrances_visible');

    for(const speed of [2,4,1]){await native(page,'maulSpeed');assert.equal((await state(page)).speed,speed);const before=(await state(page)).elapsed;await frames(page,10);
      close((await state(page)).elapsed-before,.5*speed,'Native speed '+speed+' elapsed',.005);}
    await native(page,'maulPause');const paused=await state(page);assert.equal(paused.paused,true);await frames(page,40);
    close((await state(page)).elapsed,paused.elapsed,'Paused simulation time');assert.equal(await page.locator('#maulStartWave').isEnabled(),false);
    assert.equal(await page.locator('#maulBuildArrow').isEnabled(),false);await native(page,'maulPause');assert.equal((await state(page)).paused,false);await stop(page);
    assert.deepEqual(authored(await saved(page)),authored(empty));pass('native_speed_cycles_one_two_four_and_pause_freezes_simulation_and_orders');

    const defenders=[];for(let row=0;row<3;row++)for(let col=0;col<3;col++)for(const dx of [-1,1])defenders.push({kind:'storm',cx:col*10+5+dx,cz:row*11+3,level:3});
    const winning=fixture(canonical,pieces,{rules:{preparation:0},towers:defenders});await configureRecorder(page,true);await load(page,winning);await native(page,'maulStartWave');
    const won=await until(page,s=>s.phase==='won','Ground wave defended to native victory',300);assert.equal(won.wave,1);assert.equal(won.kills,54);assert.equal(won.leaks,0);assert.equal(won.lives,30);
    close(won.gold,900+54*5+44,'Kill bounties and clear bonus');assert.ok(won.events.some(e=>e.type==='wave-cleared'));assert.ok(won.events.some(e=>e.type==='won'));
    assert.equal(await page.locator('#maulStartWave').isEnabled(),false);const winnerRun=await runData(page);assert.equal((await runStatus(page)).active,null);
    assert.equal(winnerRun.complete,true);assert.equal(winnerRun.endReason,'winner');assert.equal((await runFrame(page,winnerRun)).game.winner,'builders');
    assert.equal(winnerRun.events.filter(event=>event.type==='winner').length,1,'Native victory must seal the recording exactly once');
    const winnerRunIds=(await runStatus(page)).runs.map(run=>run.id);await page.screenshot({path:resolve(output,mode.name+'-native-victory.png')});await stop(page);
    assert.deepEqual((await runStatus(page)).runs.map(run=>run.id),winnerRunIds,'Stop duplicated the completed victory run');
    assert.deepEqual(authored(await saved(page)),authored(winning));await configureRecorder(page,false);
    pass('native_ground_wave_combat_awards_bounties_and_wave_bonus_and_finishes_in_victory');

    const losing=fixture(canonical,pieces,{rules:{lives:1,preparation:0}});await load(page,losing);await native(page,'maulStartWave');await native(page,'maulSpeed');await native(page,'maulSpeed');
    const lost=await until(page,s=>s.phase==='lost','Undefended creep reaching the shared exit',350);assert.equal(lost.lives,0);assert.equal(lost.leaks,1);assert.equal(lost.kills,0);
    assert.ok(lost.events.some(e=>e.type==='leaked'));assert.ok(lost.events.some(e=>e.type==='lost'));assert.equal(await page.locator('#maulBuildWall').isEnabled(),false);await stop(page);
    assert.deepEqual(authored(await saved(page)),authored(losing));pass('native_undefended_creep_leaks_at_shared_exit_costs_life_and_ends_in_defeat');

    const invalid=structuredClone(empty);invalid.scene.actors=invalid.scene.actors.filter(a=>!(a.type==='maul-gate'&&a.maul.sector===0));
    await importFixture(page,invalid);assert.equal((await preflight(page)).ok,false);await native(page,'playBtn');assert.equal((await state(page)).active,false);
    assert.equal(await page.locator('#maulHUD').isVisible(),false);assert.deepEqual(authored(await saved(page)),authored(invalid));
    pass('native_play_preflight_rejects_missing_waypoint_and_preserves_invalid_author_fixture');

    await importFixture(page,empty);await configureRecorder(page,true);const completedBefore=(await runStatus(page)).runs.map(run=>run.id);
    await native(page,'simulateBtn');assert.equal((await state(page)).active,true);assert.equal((await runStatus(page)).active,null);await frames(page,10);await stop(page);
    assert.deepEqual((await runStatus(page)).runs.map(run=>run.id),completedBefore);assert.deepEqual(authored(await saved(page)),authored(empty));
    pass('native_simulate_never_creates_play_recording_and_stop_restores_authored_map');

    await load(page,empty);await sector(page,0);map=(await state(page)).map;const recordedTower=await build(page,'arrow',map,4,3);await gridTap(page,map,5,1,true);await native(page,'maulCancel');
    await gridTap(page,map,3,5);await frames(page,15);await native(page,'maulStartWave');await frames(page,20);const observed=await state(page),liveRun=await runData(page);
    assert.equal(liveRun.mode,'maul');const matchStart=liveRun.events.find(e=>e.type==='match-start');assert.equal(matchStart.details.role,'builder');assert.equal(matchStart.details.initialSeed,liveRun.initialSeed);assert.ok(Number.isInteger(liveRun.initialSeed));assert.ok(liveRun.events.some(e=>e.type==='maul-build-rejected'),'Rejected touch/mouse placement was omitted from the log');assert.equal(liveRun.initial.game.kind,'maul');assert.equal(liveRun.initial.game.role,'builder');assert.equal(liveRun.capture.incomplete,false);
    assert.ok(liveRun.events.some(event=>event.type==='maul-built'&&event.details.id===recordedTower.id));assert.ok(liveRun.events.some(event=>event.type==='maul-wave-started'));
    const snapshot=await runFrame(page,liveRun);assert.equal(snapshot.game.gold,observed.gold);assert.equal(snapshot.game.wave,observed.wave);assert.equal(snapshot.game.lives,observed.lives);
    for(const unit of observed.units.filter(u=>u.alive!==false)){const entity=snapshot.entities[unit.id];assert.ok(entity,'Recorder omits a visible native creep '+unit.id);
      close(entity.position[0],unit.x,'Recorded native creep X');close(entity.position[2],unit.z,'Recorded native creep Z');close(entity.hp,unit.hp,'Recorded native creep health');}
    assert.ok(liveRun.frames.some(frame=>Object.values(frame.patch).some(entity=>entity?.kind==='projectile'&&entity.from?.length===3&&entity.to?.length===3)),'Native tower attack traces are missing from the recorded world');assert.deepEqual(snapshot.game.shots,observed.shots);assert.ok(snapshot.entities[recordedTower.id]?.parts?.length,'Recorder lacks tower part catalog');assert.ok(snapshot.camera?.position?.length===3,'Recorder lacks actual camera');
    const builder=empty.scene.actors.find(a=>a.type==='maul-builder'&&a.maul.sector===0),builderEntity=snapshot.entities[builder.id];assert.ok(builderEntity);
    assert.ok(Math.hypot(builderEntity.position[0]-builder.position[0],builderEntity.position[2]-builder.position[2])>.25,'Ground movement never moved the actual builder');
    await native(page,'maulPause');const pausedRecord=await runData(page);await frames(page,20);close((await runData(page)).duration,pausedRecord.duration,'Paused recorder time');
    await native(page,'maulStop');const run=await runData(page,liveRun.id);assert.equal(run.complete,true);assert.equal(run.endReason,'stopped');assert.equal((await runStatus(page)).active,null);
    assert.ok((await page.evaluate(run=>window.SWYRL_ENGINE_RUNS.validate(run),run)).ok,'Exported Maul log fails recorder validation');
    const independent=reconstruct(run),nativeFrame=await runFrame(page,run);assert.deepEqual(nativeFrame.entities,independent.entities);assert.deepEqual(nativeFrame.camera,independent.camera);
    assert.deepEqual(nativeFrame.game,independent.game);assert.deepEqual(authored(await saved(page)),authored(empty),'Play builder movement or temporary towers contaminated authoring');
    await native(page,'stRunLauncher');await page.locator('#stRunPanel').waitFor({state:'visible'});const pending=page.waitForEvent('download',{timeout:15000});await tap(page,'stRunExportJson');
    const file=await pending,path=resolve(output,mode.name+'.maul.swyrl-run.json');await file.saveAs(path);assert.deepEqual(JSON.parse(await readFile(path,'utf8')),run);
    await native(page,'stRunClose');await configureRecorder(page,false);assert.equal((await runStatus(page)).error,null);
    pass('native_full_play_recorder_preserves_maul_events_world_entities_camera_pause_and_download');

    assert.deepEqual(errors,[],'Browser errors during Maul acceptance');assert.equal(cases.length,16,'Every required Maul case must execute');
    receipts.push({mode:mode.name,viewport:mode.viewport,cases,canonicalId:canonical.project.canonicalId,version:'v11.62',nativeRun:run.id,
      mapActors:canonical.scene.actors.length,grid:[map.cols,map.rows],victory:{kills:won.kills,gold:won.gold},defeat:{leaks:lost.leaks,lives:lost.lives}});
    await writeFile(resolve(output,mode.name+'-receipt.json'),JSON.stringify(receipts.at(-1),null,2));
    console.log(mode.name==='desktop'?'MAUL_DESKTOP_PASS':'MAUL_MOBILE_PASS');
  }catch(error){await page.screenshot({path:resolve(output,mode.name+'-failure.png')}).catch(()=>{});await writeFile(resolve(output,mode.name+'-failure.json'),JSON.stringify({message:String(error),cases,errors,state:await state(page).catch(()=>null),ui:await ui(page).catch(()=>null)},null,2));throw error;}
  finally{await context.close();}
}await writeFile(resolve(output,'receipt.json'),JSON.stringify(receipts,null,2));console.log('MAUL_ALL_VIEWPORTS_PASS');}
finally{await browser.close();}
