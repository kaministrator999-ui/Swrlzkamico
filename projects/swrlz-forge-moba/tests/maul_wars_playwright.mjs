import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {mkdir,readFile,writeFile} from 'node:fs/promises';
import {resolve} from 'node:path';
import {pathToFileURL} from 'node:url';

// Native mouse/touch controls drive these scenarios. Fixtures are ordinary editor
// projects loaded while stopped. The clock advances the real engine RAF and
// never changes match state, AI, camera transforms, resources or combat rules.
const base=(process.env.SWYRL_ANIME_TEST_URL||'http://127.0.0.1:8765').replace(/\/$/,'');
const query=new URLSearchParams(process.env.SWYRL_ANIME_TEST_QUERY||'');query.set('project','maul-wars-frostveil');
const output=resolve(process.env.SWYRL_ANIME_SCREENSHOTS_DIR||'maul-wars-acceptance');await mkdir(output,{recursive:true});
const modes=[{name:'desktop',viewport:{width:1600,height:1000},isMobile:false,hasTouch:false},
  {name:'mobile',viewport:{width:412,height:915},isMobile:true,hasTouch:true}]
  .filter(mode=>!process.env.SWYRL_ANIME_TEST_MODE||process.env.SWYRL_ANIME_TEST_MODE===mode.name);
assert.ok(modes.length,'SWYRL_ANIME_TEST_MODE must be desktop or mobile');
const browser=await chromium.launch({headless:true,
  ...(process.env.SWYRL_CHROMIUM_PATH?{executablePath:process.env.SWYRL_CHROMIUM_PATH}:{}),
  args:['--no-sandbox','--disable-dev-shm-usage','--enable-webgl','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader']});
const touchPages=new WeakSet(),touchSessions=new WeakMap(),receipts=[];
const kinds=['arrow','cannon','frost','storm','maze-wall'];
const buttons={arrow:'warsBuildArrow',cannon:'warsBuildCannon',frost:'warsBuildFrost',storm:'warsBuildStorm','maze-wall':'warsBuildWall'};
const state=page=>page.evaluate(()=>window.SWYRL_ENGINE_MAUL_WARS.status());
const ui=page=>page.evaluate(()=>window.SWYRL_ENGINE_MAUL_WARS.uiStatus());
const saved=page=>page.evaluate(()=>window.SWYRL_ENGINE_AGENT.inspectScene());
const preflight=page=>page.evaluate(()=>window.SWYRL_ENGINE_MAUL_WARS.preflight());
const runStatus=page=>page.evaluate(()=>window.SWYRL_ENGINE_RUNS.status());
const runData=(page,id=null)=>page.evaluate(id=>window.SWYRL_ENGINE_RUNS.data(id),id);
const runFrame=(page,run,t=null)=>page.evaluate(({run,t})=>window.SWYRL_ENGINE_RUNS.frame(run,t),{run,t});
const frames=(page,count=1,ms=50)=>page.evaluate(({count,ms})=>window.__warsClock.step(count,ms),{count,ms});
const authored=data=>({project:data.project,layers:data.editor.layers,background:data.scene.background,actors:data.scene.actors,paths:data.scene.paths});
const close=(actual,expected,label,tolerance=1e-4)=>assert.ok(Number.isFinite(actual)&&Math.abs(actual-expected)<=tolerance,
  label+': expected '+expected+', received '+actual);
const towerTypes=new Set(kinds.map(kind=>'maul-wars-'+kind));
const world=(map,cx,cz)=>({x:map.origin.x+cx*map.cell,z:map.origin.z+cz*map.cell});
async function installClock(context){await context.addInitScript(()=>{
  const nativeRAF=requestAnimationFrame.bind(window),nativeCancel=cancelAnimationFrame.bind(window),nativeNow=performance.now.bind(performance),queue=new Map();
  let frozen=false,now=0,next=1000000000;Object.defineProperty(performance,'now',{configurable:true,value:()=>frozen?now:nativeNow()});
  window.requestAnimationFrame=callback=>{if(!frozen)return nativeRAF(callback);const id=next++;queue.set(id,callback);return id;};
  window.cancelAnimationFrame=id=>{queue.delete(id);nativeCancel(id);};
  window.__warsClock={freeze:()=>{frozen=true;now=nativeNow();return new Promise(resolve=>nativeRAF(()=>nativeRAF(resolve)));},
    step:(count,ms)=>{if(!frozen)throw Error('Clock is not frozen');for(let i=0;i<count;i++){now+=ms;const pending=[...queue.values()];queue.clear();
      if(!pending.length)throw Error('Real engine RAF stopped');for(const callback of pending)callback(now);}return {now,pending:queue.size};}};
});}
async function press(page,selector){const node=page.locator(selector);assert.equal(await node.isVisible(),true,'Hidden required control '+selector);
  await node.evaluate(element=>element.scrollIntoView({block:'nearest',inline:'nearest'}));const box=await node.boundingBox();assert.ok(box,'No hit rectangle for '+selector);
  assert.equal(await node.evaluate(element=>{const r=element.getBoundingClientRect(),hit=document.elementFromPoint(r.x+r.width/2,r.y+r.height/2);
    return element===hit||element.contains(hit);}),true,'A required control is obscured: '+selector);
  if(touchPages.has(page))await node.tap({force:true});else await node.click({force:true});}
async function tap(page,id){await press(page,'#'+id);}
async function native(page,id){if(touchPages.has(page)&&!(await page.locator('#'+id).isVisible())&&id==='simulateBtn'){
    await tap(page,'mobileToolsBtn');await page.locator('#mobileToolsPanel.show').waitFor({state:'visible'});
    await press(page,'#mobileToolsPanel [data-click="simulateBtn"]');
  }else await tap(page,id);await frames(page,2);}
async function stop(page){if((await state(page)).active){await native(page,'warsStop');assert.equal((await state(page)).active,false);}}
async function importFixture(page,data){await stop(page);await page.evaluate(data=>window.SWYRL_ENGINE_AGENT.loadScene(data),data);await frames(page,2);
  assert.deepEqual(authored(await saved(page)),authored(data),'Stopped native import changed the authored map');}
async function play(page){await native(page,'playBtn');assert.equal((await state(page)).active,true,'Native Play rejected the authored map: '+JSON.stringify(await preflight(page)));}
async function load(page,data){await importFixture(page,data);await play(page);}
async function sector(page,index){assert.equal(await page.locator('#warsSector').isVisible(),true);await page.locator('#warsSector').selectOption(String(index),{force:true});await frames(page,2);
  assert.equal((await state(page)).selectedSector,index,'Sector UI did not select the actual friendly builder wallet');}
async function until(page,predicate,label,max=600){let s=await state(page);for(let i=0;i<max&&!predicate(s);i+=4){await frames(page,Math.min(4,max-i));s=await state(page);}
  assert.ok(predicate(s),label+' did not occur in native Play: '+JSON.stringify({phase:s.phase,teams:s.teams,players:s.players,elapsed:s.elapsed}));return s;}
async function canvasPoint(page,map,cx,cz,{placing=false,y=0}={}){const p=world(map,cx,cz),screen=await page.evaluate(({x,z,y})=>window.SWYRL_ENGINE_MAUL_WARS.pointScreen(x,z,y),{...p,y});
  assert.ok(screen?.visible,'Grid cell is outside the actual camera: '+JSON.stringify({cx,cz,screen}));if(placing&&touchPages.has(page))screen.y+=80;
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
  const guide=await preview(page,map,cx,cz);assert.equal(guide?.valid,true,'Visible preview rejects a legal '+kind+' cell: '+JSON.stringify(guide));
  assert.equal(guide.cx,cx);assert.equal(guide.cz,cz);close(guide.world.x,world(map,cx,cz).x,'Preview X');close(guide.world.z,world(map,cx,cz).z,'Preview Z');
  const before=await state(page);await gridTap(page,map,cx,cz,true);const after=await state(page),tower=after.towers.find(t=>!before.towers.some(old=>old.id===t.id));
  assert.ok(tower,'Physical release did not build a native tower');assert.equal(tower.kind,kind);assert.equal(tower.cx,guide.cx);assert.equal(tower.cz,guide.cz);return tower;}
async function selectTower(page,map,tower){if((await ui(page)).buildKind)await native(page,'warsCancel');const top=await canvasPoint(page,map,tower.cx,tower.cz,{y:1.9});await screenTap(page,top);
  if(touchPages.has(page)){assert.equal((await ui(page)).selectedTowerId,null,'A single phone tap selected a tower');
    assert.equal((await ui(page)).lastTowerTap?.id,tower.id,'A phone tap did not identify the visible upper tower surface');await screenTap(page,top);}
  assert.equal((await ui(page)).selectedTowerId,tower.id,'Native visible-mesh tower selection did not complete');}
async function prototypes(page,canonical){const pieces=await page.evaluate(()=>{const result={};for(const kind of ['arrow','cannon','frost','storm','maze-wall']){
    const type='maul-wars-'+kind,id=window.SWYRL_ENGINE_AGENT.spawn(type,{position:[-30,0,-40],name:'Acceptance '+type});window.SWYRL_ENGINE_AGENT.bake();
    result[kind]=window.SWYRL_ENGINE_AGENT.inspectScene().scene.actors.find(actor=>actor.id===id);}return result;});
  for(const kind of kinds)assert.equal(pieces[kind]?.type,'maul-wars-'+kind,'Missing native editable Wars prefab '+kind);
  await page.evaluate(data=>window.SWYRL_ENGINE_AGENT.loadScene(data),canonical);await frames(page,2);return pieces;}
function fixture(canonical,pieces,{rules={},towers=[],shortRoute=false}={}){const data=structuredClone(canonical),map={cell:2,origin:{x:-48,z:-50}};
  data.project.maulWars={...data.project.maulWars,opponentAI:false,soloSupport:false,preparation:120,startGold:900,startIncome:25,incomeInterval:25,lives:25,difficulty:1,...rules};
  data.scene.actors=data.scene.actors.filter(actor=>!towerTypes.has(actor.type));
  for(const [index,t]of towers.entries()){const p=world(map,t.cx,t.cz);data.scene.actors.push({...structuredClone(pieces[t.kind]),id:'wars-acceptance-tower-'+index,
    name:'Authored '+t.kind+' '+index,position:[p.x,0,p.z],rotation:[0,0,0],scale:[1,1,1],baked:true,visible:true,manualVisible:true,
    wars:{team:t.cz<25?0:1,level:t.level||1,priority:t.priority||'first'},editorLayerIds:[data.editor.layers.at(-1).id]});}
  if(shortRoute){const gates=[[4,3],[4,4],[5,4],[5,3],[6,3]];for(const actor of data.scene.actors){const meta=actor.wars||{};let c;
      if(actor.type==='maul-wars-spawn')c=[3,3];else if(actor.type==='maul-wars-gate')c=gates[meta.stage];else if(actor.type==='maul-wars-exit')c=[6,4];
      if(c){const p=world(map,c[0],meta.team===1?50-c[1]:c[1]);actor.position=[p.x,0,p.z];}}}return data;}
async function configureRecorder(page,enabled){await native(page,'stRunLauncher');await page.locator('#stRunPanel').waitFor({state:'visible'});
  if((await page.locator('#stRunEnabled').isChecked())!==enabled)await tap(page,'stRunEnabled');await page.locator('#stRunCadence').selectOption('full',{force:true});
  await frames(page,1);assert.equal((await runStatus(page)).settings.enabled,enabled);await native(page,'stRunClose');}
async function exportMap(page,mode){const pending=page.waitForEvent('download',{timeout:15000});
  if(mode.hasTouch){await native(page,'warsRulesBtn');await tap(page,'warsRulesSave');}else await tap(page,'saveBtn');
  const file=await pending;await file.saveAs(resolve(output,mode.name+'-authored-wars.swyrl.json'));const data=JSON.parse(await readFile(await file.path(),'utf8'));
  if(mode.hasTouch)await native(page,'warsRulesClose');return data;}
async function download(page,id,path){const pending=page.waitForEvent('download',{timeout:15000});await tap(page,id);const file=await pending;await file.saveAs(path);
  return {name:file.suggestedFilename(),text:await readFile(path,'utf8'),path};}
function reconstruct(run,t=run.duration){const result=structuredClone(run.initial);for(const frame of run.frames){if(frame.t>t+1e-8)break;
  for(const [id,patch]of Object.entries(frame.patch))if(patch===null)delete result.entities[id];else result.entities[id]={...(result.entities[id]||{}),...structuredClone(patch)};
  if(frame.camera)result.camera=structuredClone(frame.camera);if(frame.game)Object.assign(result.game,structuredClone(frame.game));}return result;}

try{for(const mode of modes){const context=await browser.newContext({viewport:mode.viewport,isMobile:mode.isMobile,hasTouch:mode.hasTouch});await installClock(context);
  const page=await context.newPage(),errors=[],cases=[];if(mode.hasTouch){touchPages.add(page);touchSessions.set(page,await context.newCDPSession(page));}
  page.on('pageerror',error=>errors.push(String(error)));page.setDefaultTimeout(30000);
  const pass=name=>{assert.ok(!cases.includes(name),'Duplicate acceptance case '+name);cases.push(name);console.log('MAUL_WARS_CASE_PASSED',mode.name,name);};
  try{
    await page.goto(base+'/index.html?'+query,{waitUntil:'domcontentloaded',timeout:60000});
    await page.waitForFunction(()=>window.SWYRL_ENGINE_MAUL_WARS?.uiStatus&&window.SWYRL_ENGINE_AGENT.project().canonicalId==='maul-wars-frostveil',undefined,{timeout:60000});
    await page.locator('#perfPreset').selectOption('medium',{force:true});await page.evaluate(()=>window.__warsClock.freeze());await frames(page,2);
    assert.equal(await page.evaluate(()=>window.SWYRL_ENGINE_BUILD.version),'v10.7','Wrong engine release');
    const canonical=await saved(page),mapCheck=await preflight(page),sourceResponse=await context.request.get(base+'/SOURCE.json');
    assert.equal(sourceResponse.ok(),true);const source=await sourceResponse.json();assert.match(source.sourceVersion,/v10\.7/);
    assert.equal(source.patches.length,67);assert.equal(source.patches.at(-1),'patches/v10_7_wintermaul_wars.py');assert.equal(Object.keys(source.assets).length,25);
    assert.match(source.finalSha256,/^[a-f0-9]{64}$/);console.log('MAUL_WARS_SOURCE_SHA256',mode.name,source.finalSha256);
    assert.match(await (await context.request.get(base+'/index.html')).text(),/V10_7_WINTERMAUL_WARS/);
    assert.equal(canonical.version,10.7);assert.equal(canonical.project.kind,'maul-wars');assert.equal(canonical.editor.layers.length,7);
    for(const [type,count]of [['sector',2],['spawn',2],['gate',10],['builder',6],['exit',2]])
      assert.equal(canonical.scene.actors.filter(a=>a.type==='maul-wars-'+type).length,count,'Missing native Wars '+type+' actors');
    assert.equal(mapCheck.ok,true,'Authored Wars routes failed: '+mapCheck.errors.join(' '));assert.equal(mapCheck.map.cols,49);assert.equal(mapCheck.map.rows,51);
    assert.equal(mapCheck.paths.length,2);for(const type of ['spawn','gate','exit'])for(const actor of canonical.scene.actors.filter(a=>a.type==='maul-wars-'+type&&a.wars.team===0)){
      const mirrored=canonical.scene.actors.find(a=>a.type===actor.type&&a.wars.team===1&&(type!=='gate'||a.wars.stage===actor.wars.stage));assert.ok(mirrored);
      close(mirrored.position[0],actor.position[0],'Mirrored '+type+' X');close(mirrored.position[2],-actor.position[2],'Mirrored '+type+' Z');}
    const walls=new Set(mapCheck.map.blocked.map(c=>c.x+','+c.z));for(let cx=0;cx<49;cx++)assert.ok(walls.has(cx+',25'),'The teams have no solid central divide');
    for(const [cx,cz]of [[12,10],[36,14],[12,40],[36,36]])assert.ok(walls.has(cx+','+cz),'A raised frozen island is missing');
    const pieces=await prototypes(page,canonical),empty=fixture(canonical,pieces);
    pass('native_six_defense_sectors_mirrored_team_routes_raised_islands_and_protected_ships');

    await page.evaluate(()=>window.SWYRL_ENGINE_AGENT.openProjects());await frames(page,2);await press(page,'[data-project-template="maul-wars-frostveil"]');await frames(page,2);
    assert.deepEqual(authored(await saved(page)),authored(canonical));const completedBefore=(await runStatus(page)).runs.map(r=>r.id);
    assert.equal((await runStatus(page)).settings.enabled,false,'Run recording must default off');await play(page);let s=await state(page);
    assert.equal(s.players.length,6);assert.equal(s.teams.length,2);assert.equal(s.phase,'preparation');
    assert.equal(s.players.filter(p=>p.ai).length,5);assert.ok(s.towers.some(t=>t.team===0&&t.owner>0),'Friendly AI did not defend its own territory');
    assert.ok(s.towers.some(t=>t.team===1),'Enemy AI did not build defenses');assert.ok((await page.evaluate(()=>window.SWYRL_ENGINE_MAUL_WARS.renderStatus())).meshes>=s.towers.length);
    await stop(page);assert.deepEqual((await runStatus(page)).runs.map(r=>r.id),completedBefore);assert.deepEqual(authored(await saved(page)),authored(canonical));
    pass('project_hub_loads_local_three_vs_three_match_with_five_ai_and_default_off_recording');

    await native(page,'warsRulesBtn');for(const [key,value]of Object.entries({startGold:777,startIncome:31,lives:17,preparation:12,incomeInterval:10,seed:731}))
      await page.locator('#warsRule_'+key).fill(String(value));await page.locator('#warsRule_difficulty').selectOption('0.65',{force:true});
    for(const id of ['warsRule_opponentAI','warsRule_soloSupport'])if(await page.locator('#'+id).isChecked())await tap(page,id);
    await native(page,'warsRulesApply');await native(page,'warsRulesClose');const configured=await saved(page);
    assert.deepEqual(Object.fromEntries(['startGold','startIncome','lives','preparation','incomeInterval','seed','difficulty','opponentAI','soloSupport'].map(k=>[k,configured.project.maulWars[k]])),
      {startGold:777,startIncome:31,lives:17,preparation:12,incomeInterval:10,seed:731,difficulty:.65,opponentAI:false,soloSupport:false});
    const exported=await exportMap(page,mode);assert.deepEqual(authored(exported),authored(configured));await importFixture(page,exported);assert.equal((await preflight(page)).ok,true);
    pass('native_rules_and_project_download_round_trip_wars_economy_ai_settings_and_map');

    await load(page,empty);s=await state(page);await frames(page,30);const preparing=await state(page);
    assert.equal(preparing.phase,'preparation');assert.equal(preparing.units.length,0);assert.equal(preparing.towers.length,0);assert.equal(preparing.gold,900);
    assert.equal(preparing.players.filter(p=>p.ai).length,0);assert.ok(preparing.elapsed>s.elapsed);assert.equal(await page.locator('#warsSendWisp').isEnabled(),false);
    for(const index of [1,2,0]){await sector(page,index);assert.equal((await state(page)).gold,(await state(page)).players[index].gold);}
    await stop(page);pass('preparation_disables_sending_and_three_friendly_controls_select_private_builder_wallets');

    await load(page,empty);await sector(page,0);let map=(await state(page)).map;const created=[];
    for(const [i,kind]of kinds.entries()){const before=await state(page),tower=await build(page,kind,map,8+i,5);created.push(tower);
      close((await state(page)).gold,before.gold-(await page.evaluate(kind=>window.SWYRL_ENGINE_MAUL_WARS.definitions[kind].cost,kind)),'Build cost '+kind);
      assert.equal(tower.owner,0);assert.equal(tower.team,0);}
    assert.equal((await state(page)).towers.length,5);assert.equal((await preflight(page)).ok,true,'Runtime towers contaminated authoring preflight');
    await page.screenshot({path:resolve(output,mode.name+'-native-wars-towers.png')});
    pass('physical_mouse_or_phone_placement_matches_visible_offset_grid_for_all_five_tower_families');

    for(const [cx,cz,reason]of [[8,5,/occup/i],[12,8,/cliff|wall|raised/i],[3,3,/entrance|spawn|open|protected/i]]){
      const before=await state(page),guide=await preview(page,map,cx,cz);assert.equal(guide?.valid,false,'An unavailable grid cell displayed a legal footprint');assert.match(guide.reason,reason);
      await gridTap(page,map,cx,cz,true);const after=await state(page);assert.equal(after.towers.length,before.towers.length);assert.equal(after.gold,before.gold);}
    pass('occupied_cliff_and_protected_entrance_cells_reject_physical_placement_without_charge');

    const beforeCancel=await state(page),cancelPoint=await canvasPoint(page,map,14,5,{placing:true});
    if(mode.hasTouch){await touchEvent(page,'touchStart',cancelPoint);await frames(page,1);assert.ok((await ui(page)).preview);await touchEvent(page,'touchCancel');}
    else{await page.mouse.move(cancelPoint.x,cancelPoint.y);await page.mouse.down();await frames(page,1);await page.keyboard.press('Escape');await page.mouse.up();}
    await frames(page,2);assert.equal((await state(page)).gold,beforeCancel.gold);assert.equal((await state(page)).towers.length,beforeCancel.towers.length);
    if((await ui(page)).buildKind)await native(page,'warsCancel');assert.equal((await ui(page)).buildKind,null);assert.equal((await ui(page)).preview,null);
    pass('cancelled_pointer_gesture_and_cancel_button_do_not_construct_or_spend');

    const arrow=created[0];await selectTower(page,map,arrow);assert.equal(await page.locator('#warsUpgrade').isEnabled(),true);
    assert.match(await page.locator('#warsSelectedDetail').textContent(),/8 range|8.*range|range.*8/i);const beforeUpgrade=await state(page);await native(page,'warsUpgrade');
    assert.equal((await state(page)).towers.find(t=>t.id===arrow.id).level,2);close((await state(page)).gold,beforeUpgrade.gold-35,'Arrow upgrade cost');
    assert.match(await page.locator('#warsSelectedDetail').textContent(),/9 range|9.*range|range.*9/i);await page.locator('#warsPriority').selectOption('strong',{force:true});await frames(page,2);
    assert.equal((await state(page)).towers.find(t=>t.id===arrow.id).priority,'strong');const beforeSell=await state(page);await native(page,'warsSell');
    assert.equal((await state(page)).towers.some(t=>t.id===arrow.id),false);close((await state(page)).gold,beforeSell.gold+38,'70 percent invested gold refund');
    assert.equal((await ui(page)).selectedTowerId,null);await stop(page);assert.deepEqual(authored(await saved(page)),authored(empty));
    pass('upper_surface_ray_selection_phone_double_tap_upgrade_range_priority_and_sell_refund');

    const blocker=fixture(canonical,pieces,{towers:Array.from({length:24},(_,i)=>i+1).filter(cz=>cz!==4&&(cz<8||cz>15)).map(cz=>({kind:'maze-wall',cx:20,cz}))});
    await load(page,blocker);await sector(page,0);map=(await state(page)).map;await native(page,'warsBuildWall');const beforeBlock=await state(page),guide=await preview(page,map,20,4);
    assert.equal(guide?.valid,false,'The last ordered ground route can be sealed');assert.match(guide.reason,/route|ship|open/i);await gridTap(page,map,20,4,true);
    assert.equal((await state(page)).gold,beforeBlock.gold);assert.equal((await state(page)).towers.length,beforeBlock.towers.length);await stop(page);
    assert.deepEqual(authored(await saved(page)),authored(blocker));pass('physical_last_route_blocking_is_rejected_without_charge_or_authoring_corruption');

    await load(page,empty);map=(await state(page)).map;for(const index of [0,1,2]){await sector(page,index);const focus=world(map,map.sectors[index].focus.x,map.sectors[index].focus.z);
      assert.equal((await page.evaluate(p=>window.SWYRL_ENGINE_MAUL_WARS.pointScreen(p.x,p.z),focus)).visible,true,'Friendly sector framing clips its territory');}
    await native(page,'warsEnemyView');for(const c of [map.routes[1].spawn,map.routes[1].exit]){const p=world(map,c.x,c.z);
      assert.equal((await page.evaluate(p=>window.SWYRL_ENGINE_MAUL_WARS.pointScreen(p.x,p.z),p)).visible,true,'Enemy view clips entrance or ship');}
    await native(page,'warsOverview');for(const route of map.routes){const p=world(map,route.spawn.x,route.spawn.z);
      assert.equal((await page.evaluate(p=>window.SWYRL_ENGINE_MAUL_WARS.pointScreen(p.x,p.z),p)).visible,true,'Overview clips a team entrance');}
    await page.screenshot({path:resolve(output,mode.name+'-mirrored-wintermaul-wars-map.png')});await sector(page,0);
    pass('friendly_sector_enemy_view_and_overview_controls_frame_both_mirrored_arenas');

    for(const speed of [2,4,1]){await native(page,'warsSpeed');assert.equal((await state(page)).speed,speed);const before=(await state(page)).elapsed;await frames(page,10);
      close((await state(page)).elapsed-before,.5*speed,'Speed '+speed+' elapsed',.005);}
    await native(page,'warsPause');const paused=await state(page);assert.equal(paused.paused,true);await frames(page,40);close((await state(page)).elapsed,paused.elapsed,'Paused simulation time');
    assert.deepEqual((await state(page)).players,paused.players);assert.equal(await page.locator('#warsBuildArrow').isEnabled(),false);assert.equal(await page.locator('#warsSendWisp').isEnabled(),false);
    await native(page,'warsPause');assert.equal((await state(page)).paused,false);await stop(page);assert.deepEqual(authored(await saved(page)),authored(empty));
    pass('native_speed_pause_and_stop_freeze_resources_and_restore_the_authored_map');

    const battle=fixture(canonical,pieces,{rules:{preparation:0,incomeInterval:5}});await load(page,battle);await sector(page,0);const beforeSend=await state(page);
    await native(page,'warsSendWisp');let sent=await state(page);close(sent.players[0].gold,beforeSend.players[0].gold-15,'Wisp send cost');close(sent.players[0].income,beforeSend.players[0].income+1,'Immediate income gain');
    assert.equal(sent.players[1].gold,beforeSend.players[1].gold);const order=sent.events.find(e=>e.type==='sent');assert.equal(order.details.sourcePlayer,0);assert.equal(order.details.defendTeam,1);
    const spawned=await until(page,s=>s.units.some(u=>u.kind==='wisp'),'Local send entering the opposite maze',30),incoming=spawned.units.find(u=>u.kind==='wisp');
    assert.equal(incoming.defendTeam,1);assert.equal(incoming.sourcePlayer,0);assert.ok(incoming.z>0,'Local send entered its own team arena');
    const paid=await until(page,s=>s.events.some(e=>e.type==='income-paid'&&e.details.player===0),'Recurring income payment',150);
    close(paid.players[0].gold,beforeSend.players[0].gold-15+26,'Income payment after send');close(paid.players[1].gold,beforeSend.players[1].gold+25,'Other builder private income');
    await sector(page,1);const sectorOne=await state(page);await native(page,'warsSendBrute');s=await state(page);close(s.players[1].gold,sectorOne.players[1].gold-40,'Second builder send cost');
    assert.equal(s.players[0].gold,sectorOne.players[0].gold);assert.ok(s.events.some(e=>e.type==='sent'&&e.details.sourcePlayer===1&&e.details.defendTeam===1));await stop(page);
    pass('native_sends_charge_private_wallet_target_enemy_maze_and_raise_recurring_income');

    const aiBattle=fixture(canonical,pieces,{rules:{preparation:0,soloSupport:true,opponentAI:true}});await load(page,aiBattle);
    const ai=await until(page,s=>s.events.some(e=>e.type==='sent'&&e.details.sourceTeam===0)&&s.events.some(e=>e.type==='sent'&&e.details.sourceTeam===1),'Both teams sending and defending through native AI',320);
    assert.equal(ai.players.filter(p=>p.ai).length,5);assert.ok(ai.towers.some(t=>t.owner===1||t.owner===2));assert.ok(ai.towers.some(t=>t.owner>=3));
    assert.ok(ai.units.some(u=>u.defendTeam===0));assert.ok(ai.units.some(u=>u.defendTeam===1));assert.equal(ai.players[0].income,25,'AI charged the local human income');
    await stop(page);assert.deepEqual(authored(await saved(page)),authored(aiBattle));pass('five_optional_ai_builders_defend_own_territories_and_send_to_the_opposing_team');

    const flight=fixture(canonical,pieces,{rules:{preparation:0},towers:[{kind:'maze-wall',cx:12,cz:47}]});await load(page,flight);await native(page,'warsSendWisp');await native(page,'warsSendFlyer');
    const airborne=await until(page,s=>s.units.some(u=>u.kind==='flyer'),'Flying send spawning through native queue',40),flyer=airborne.units.find(u=>u.kind==='flyer'),ground=airborne.units.find(u=>u.kind==='wisp');
    assert.equal(flyer.air,true);assert.equal(ground.air,false);assert.equal(flyer.path.length,7);assert.ok(ground.path.length>flyer.path.length);
    assert.ok(ground.path.every(c=>c.x!==12||c.z!==47),'Ground route crosses a built wall');assert.equal(flyer.path[1].z,47);assert.ok(flyer.path[0].x<12&&flyer.path[1].x>12,'Air route failed to cross above the maze wall');
    await until(page,s=>s.units.some(u=>u.kind==='flyer'&&u.x>world(s.map,12,47).x),'Flyer passing above the real maze wall',130);await stop(page);
    pass('native_flying_send_crosses_maze_walls_while_ground_creep_follows_open_ordered_path');

    const winning=fixture(canonical,pieces,{rules:{preparation:0,lives:1},shortRoute:true});await configureRecorder(page,true);await load(page,winning);await native(page,'warsSendWisp');
    const won=await until(page,s=>s.phase==='won','Opposing ship losing its final shared life',200);assert.equal(won.winner,0);assert.equal(won.teams[1].lives,0);assert.equal(won.teams[1].leaks,1);assert.equal(won.teams[0].lives,1);
    assert.equal(await page.locator('#warsSendWisp').isEnabled(),false);const winnerRun=await runData(page);assert.equal(winnerRun.complete,true);assert.equal(winnerRun.endReason,'winner');
    assert.equal((await runFrame(page,winnerRun)).game.winner,0);assert.match(await page.evaluate(run=>window.SWYRL_ENGINE_RUNS.words(run),winnerRun),/Winner: North\./);assert.equal(winnerRun.events.filter(e=>e.type==='winner').length,1);const winnerRunIds=(await runStatus(page)).runs.map(r=>r.id);
    await stop(page);assert.deepEqual((await runStatus(page)).runs.map(r=>r.id),winnerRunIds,'Stop duplicated a winning run');assert.deepEqual(authored(await saved(page)),authored(winning));await configureRecorder(page,false);
    const losing=fixture(canonical,pieces,{rules:{preparation:0,lives:1,opponentAI:true},shortRoute:true});await load(page,losing);
    const lost=await until(page,s=>s.phase==='lost','Opponent send reaching the local ship',400);assert.equal(lost.winner,1);assert.equal(lost.teams[0].lives,0);assert.equal(lost.teams[0].leaks,1);
    assert.ok(lost.events.some(e=>e.type==='leaked'&&e.details.defendTeam===0));assert.equal(await page.locator('#warsBuildWall').isEnabled(),false);await stop(page);
    assert.deepEqual(authored(await saved(page)),authored(losing));pass('native_enemy_and_local_ship_leaks_end_in_win_or_defeat_and_seal_winner_once');

    const invalid=structuredClone(empty);invalid.scene.actors=invalid.scene.actors.filter(a=>!(a.type==='maul-wars-gate'&&a.wars.team===0&&a.wars.stage===0));
    await importFixture(page,invalid);assert.equal((await preflight(page)).ok,false);await native(page,'playBtn');assert.equal((await state(page)).active,false);
    assert.equal(await page.locator('#warsHUD').isVisible(),false);assert.deepEqual(authored(await saved(page)),authored(invalid));
    pass('native_preflight_rejects_missing_ordered_turn_before_play_and_preserves_fixture');

    await importFixture(page,empty);await configureRecorder(page,true);const beforeSimulate=(await runStatus(page)).runs.map(r=>r.id);
    await native(page,'simulateBtn');assert.equal((await state(page)).active,true);assert.equal((await runStatus(page)).active,null);await frames(page,10);await stop(page);
    assert.deepEqual((await runStatus(page)).runs.map(r=>r.id),beforeSimulate);assert.deepEqual(authored(await saved(page)),authored(empty));
    pass('native_simulate_is_excluded_from_play_run_recording_and_stop_restores_map');

    const recording=fixture(canonical,pieces,{rules:{preparation:0,incomeInterval:5,opponentAI:true},shortRoute:true});await load(page,recording);await sector(page,0);map=(await state(page)).map;
    const recordedTower=await build(page,'arrow',map,4,5);await gridTap(page,map,4,5,true);await native(page,'warsCancel');await gridTap(page,map,12,5);await frames(page,20);
    await native(page,'warsSendBrute');await native(page,'warsSendFlyer');await frames(page,290);const observed=await state(page),liveRun=await runData(page);
    assert.equal(liveRun.mode,'maul-wars');assert.equal(liveRun.initial.game.kind,'maul-wars');assert.equal(liveRun.capture.incomplete,false);
    const matchStart=liveRun.events.find(e=>e.type==='match-start');assert.equal(matchStart.details.role,'builder');assert.equal(matchStart.details.initialSeed,liveRun.initialSeed);assert.ok(Number.isInteger(liveRun.initialSeed));
    for(const type of ['built','sent','spawned','income-paid'])assert.ok(liveRun.events.some(e=>e.type==='maul-wars-'+type),'Recorder omitted Wars '+type+' event');
    assert.ok(liveRun.events.some(e=>/maul-wars-.*rejected/.test(e.type)),'Rejected physical placement was omitted from the run');
    const snapshot=await runFrame(page,liveRun);assert.deepEqual(snapshot.game.players,observed.players);assert.deepEqual(snapshot.game.teams,observed.teams);
    assert.ok(observed.units.some(u=>u.alive!==false),'Recorder scenario has no live creep to compare with the retained world');
    for(const unit of observed.units.filter(u=>u.alive!==false)){const entity=snapshot.entities[unit.id];assert.ok(entity,'Recorder omits native Wars creep '+unit.id);
      close(entity.position[0],unit.x,'Recorded creep X');close(entity.position[2],unit.z,'Recorded creep Z');close(entity.hp,unit.hp,'Recorded creep health');}
    assert.ok(liveRun.frames.some(f=>Object.values(f.patch).some(e=>e?.kind==='projectile'&&e.from?.length===3&&e.to?.length===3)),'Native attack traces were omitted');
    assert.deepEqual(snapshot.game.shots,observed.shots);assert.ok(snapshot.entities[recordedTower.id]?.parts?.length,'Tower part catalog is absent');assert.ok(snapshot.camera?.position?.length===3,'Actual camera is absent');
    const builder=recording.scene.actors.find(a=>a.type==='maul-wars-builder'&&a.wars.sector===0),builderEntity=snapshot.entities[builder.id];assert.ok(builderEntity);
    assert.ok(Math.hypot(builderEntity.position[0]-builder.position[0],builderEntity.position[2]-builder.position[2])>.25,'Ground command did not move the actual native builder');
    await native(page,'warsPause');const pausedRun=await runData(page);await frames(page,20);close((await runData(page)).duration,pausedRun.duration,'Paused recorder time');
    await native(page,'warsStop');const run=await runData(page,liveRun.id);assert.equal(run.complete,true);assert.equal(run.endReason,'stopped');assert.equal((await runStatus(page)).active,null);
    assert.equal((await page.evaluate(run=>window.SWYRL_ENGINE_RUNS.validate(run),run)).ok,true,'Wars run does not validate');
    const independent=reconstruct(run),nativeFrame=await runFrame(page,run);assert.deepEqual(nativeFrame.entities,independent.entities);assert.deepEqual(nativeFrame.camera,independent.camera);
    assert.deepEqual(nativeFrame.game,independent.game);assert.deepEqual(authored(await saved(page)),authored(recording),'Runtime world contaminated authored project');
    await native(page,'stRunLauncher');await page.locator('#stRunPanel').waitFor({state:'visible'});
    const json=await download(page,'stRunExportJson',resolve(output,mode.name+'.maul-wars.swyrl-run.json'));
    const transcript=await download(page,'stRunExportText',resolve(output,mode.name+'.maul-wars.swyrl-run.txt'));
    const html=await download(page,'stRunExportHtml',resolve(output,mode.name+'.maul-wars.swyrl-run.html'));
    assert.deepEqual(JSON.parse(json.text),run);assert.match(transcript.text,/maul-wars|Frostveil|Wars/i);assert.match(transcript.text,/north|south|east|west|heading|facing|direction/i);assert.match(html.text,/<canvas\b/i);
    await native(page,'stRunClose');const offlineContext=await browser.newContext({viewport:mode.viewport,isMobile:mode.isMobile,hasTouch:mode.hasTouch});await offlineContext.setOffline(true);
    const review=await offlineContext.newPage(),offlineErrors=[];review.on('pageerror',e=>offlineErrors.push(String(e)));await review.goto(pathToFileURL(html.path).href,{waitUntil:'load'});
    await review.waitForFunction(()=>window.SWYRL_RUN_VIEWER?.state());assert.deepEqual(await review.locator('#stRunPayload').evaluate(n=>JSON.parse(n.textContent)),run);
    assert.equal(await review.evaluate(()=>!!window.SWYRL_ENGINE_AGENT),false,'Offline review booted gameplay');await review.evaluate(t=>window.SWYRL_RUN_VIEWER.seek(t),run.duration);
    close(await review.evaluate(()=>window.SWYRL_RUN_VIEWER.time()),run.duration,'Offline review final time');assert.deepEqual(offlineErrors,[]);await offlineContext.close();
    await configureRecorder(page,false);assert.equal((await runStatus(page)).error,null);
    pass('full_play_run_exports_wars_sends_income_teams_routes_entities_shots_camera_and_offline_review');

    assert.deepEqual(errors,[],'Browser errors during Wintermaul Wars acceptance');assert.equal(cases.length,18,'Every required Wars case must execute');
    receipts.push({mode:mode.name,viewport:mode.viewport,cases,canonicalId:canonical.project.canonicalId,version:'v10.7',sourceSha256:source.finalSha256,
      mapActors:canonical.scene.actors.length,grid:[map.cols,map.rows],nativeRun:run.id,victory:{winner:won.winner,teams:won.teams},defeat:{winner:lost.winner,teams:lost.teams}});
    await writeFile(resolve(output,mode.name+'-receipt.json'),JSON.stringify(receipts.at(-1),null,2));console.log(mode.name==='desktop'?'MAUL_WARS_DESKTOP_PASS':'MAUL_WARS_MOBILE_PASS');
  }catch(error){await page.screenshot({path:resolve(output,mode.name+'-failure.png')}).catch(()=>{});await writeFile(resolve(output,mode.name+'-failure.json'),
      JSON.stringify({message:String(error),cases,errors,state:await state(page).catch(()=>null),ui:await ui(page).catch(()=>null)},null,2));throw error;}
  finally{await context.close();}
}await writeFile(resolve(output,'receipt.json'),JSON.stringify(receipts,null,2));console.log('MAUL_WARS_ALL_VIEWPORTS_PASS');}
finally{await browser.close();}
