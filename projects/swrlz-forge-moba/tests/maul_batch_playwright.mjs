import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {mkdir,readFile,writeFile} from 'node:fs/promises';
import {resolve} from 'node:path';
import {createHash} from 'node:crypto';
import {gunzipSync} from 'node:zlib';

// Ordinary native editor fixtures are imported only while stopped. Real mouse
// and phone touch drive Play, placement and tower orders. The controlled clock
// advances the existing engine RAF; it never edits combat, economy or match state.
const base=(process.env.SWYRL_ANIME_TEST_URL||'http://127.0.0.1:8765').replace(/\/$/,'');
const query=new URLSearchParams(process.env.SWYRL_ANIME_TEST_QUERY||'');query.set('project','maul-frostveil');
const output=resolve(process.env.SWYRL_ANIME_SCREENSHOTS_DIR||'maul-batch-acceptance');await mkdir(output,{recursive:true});
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
  if(placing&&touchPages.has(page))screen.y+=(await page.evaluate(()=>window.SWYRL_ENGINE_MAUL.batchStatus())).touchLift;
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
function fixture(canonical,pieces,{rules={},towers=[]}={}){const data=structuredClone(canonical),map={cell:2,origin:{x:-40,z:-44}};
  delete data.project.maulConstruction;delete data.project.maulSpawnProtection;data.project.maul={...data.project.maul,autoWaves:false,soloSupport:false,preparation:120,intermission:0,startGold:900,waves:1,lives:30,difficulty:1,...rules};
  data.scene.actors=data.scene.actors.filter(actor=>!towerTypes.has(actor.type));
  for(const [index,t]of towers.entries()){const p=world(map,t.cx,t.cz);data.scene.actors.push({...structuredClone(pieces[t.kind]),id:'acceptance-tower-'+index,
    name:'Authored '+t.kind+' '+index,position:[p.x,0,p.z],rotation:[0,0,0],scale:[1,1,1],baked:true,visible:true,manualVisible:true,
    maul:{level:t.level||1,priority:t.priority||'first'},editorLayerIds:[data.editor.layers[0].id]});}return data;}
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


const towerActorTypes=new Set(kinds.map(kind=>'maul-'+kind));
const profile='grouped-v1';
const groupEvents=s=>s.events.filter(e=>e.type==='spawn-group');
const spawnEvents=s=>s.events.filter(e=>e.type==='spawned');
const clearCell=(map,p)=>!map.blocked.some(w=>w.x===p.x&&w.z===p.z);
const groupMember=e=>e.details.members;
function verifyBatch(s,event,{blocked=[]}={}){
  const members=groupMember(event),born=spawnEvents(s).filter(e=>e.details.group===event.details.group);
  assert.ok(members?.length>9,'A batch needs several simultaneous minions, not one per sector');
  assert.equal(event.details.count,members.length);assert.equal(born.length,members.length);
  assert.ok(born.every(e=>e.t===event.t),'Members in one batch must share one actual simulation birth timestamp');
  assert.equal(new Set(members.map(m=>m.id)).size,members.length,'Duplicate batch member identities');
  for(let sector=0;sector<9;sector++){
    const list=members.filter(m=>m.sector===sector);assert.equal(list.length,2,'First-round sector batch must have two minions');
    assert.equal(new Set(list.map(m=>m.cx+','+m.cz)).size,list.length,'Minions spawned on top of one another');
    for(const member of list){assert.ok(clearCell(s.map,{x:member.cx,z:member.cz}),'Birth on blocked terrain');
      assert.ok(!blocked.some(p=>p.cx===member.cx&&p.cz===member.cz),'Birth overlaps authored tower');
      const sectorBounds=s.map.sectors[sector];assert.ok(member.cx>=sectorBounds.minX&&member.cx<=sectorBounds.maxX&&member.cz>=sectorBounds.minZ&&member.cz<=sectorBounds.maxZ,'Birth outside native sector');
      const birth=born.find(e=>e.details.id===member.id);assert.equal(birth.details.sector,sector);assert.equal(birth.details.cx,member.cx);assert.equal(birth.details.cz,member.cz);assert.equal(birth.details.index,member.index);
      const unit=s.units.find(u=>u.id===member.id);assert.ok(unit,'Actual native session omits batch member');assert.equal(unit.spawnGroup,event.details.group);assert.equal(unit.spawnIndex,member.index);assert.deepEqual(unit.spawnOrigin,{x:member.cx,z:member.cz});
      assert.deepEqual({x:unit.path[0].x,z:unit.path[0].z},{x:member.cx,z:member.cz},'Ground route begins at the wrong scatter cell');}
  }
}
async function heldPlacement(page,map,cx,cz){const finger=await canvasPoint(page,map,cx,cz,{placing:true});
  if(touchPages.has(page))await touchEvent(page,'touchStart',finger);else{await page.mouse.move(finger.x,finger.y);await page.mouse.down();}
  await frames(page,1);const guide=(await ui(page)).preview;assert.equal(guide?.valid,true,'Native placement preview must accept '+cx+','+cz+': '+JSON.stringify(guide));
  assert.equal(guide.cx,cx);assert.equal(guide.cz,cz);
  const corners=await page.evaluate(({x,z,cell})=>[-1,1].flatMap(dx=>[-1,1].map(dz=>window.SWYRL_ENGINE_MAUL.pointScreen(x+dx*cell/2,z+dz*cell/2,.08))),{...guide.world,cell:map.cell});
  for(const corner of corners){assert.equal(corner.visible,true,'Projected footprint corner leaves renderer');assert.equal(await page.evaluate(p=>{const hit=document.elementFromPoint(p.x,p.y);return hit?.tagName==='CANVAS'||hit?.id==='viewport';},corner),true,'Placement footprint is concealed by editor HUD');}
  if(touchPages.has(page)){assert.ok(Math.max(...corners.map(p=>p.y))<=finger.y-34,'The complete ground footprint must clear the real fingertip, not only its center');
    const top=await page.evaluate(({x,z})=>window.SWYRL_ENGINE_MAUL.pointScreen(x,z,2),guide.world);assert.ok(top.y<finger.y-34,'Ghost tower remains hidden under fingertip');}
  await page.screenshot({path:resolve(output,(touchPages.has(page)?'mobile':'desktop')+'-held-visible-footprint.png')});
  return {finger,guide,corners};
}
async function releasePlacement(page){if(touchPages.has(page))await touchEvent(page,'touchEnd');else await page.mouse.up();await frames(page,1);}
async function cancelPlacement(page){if(touchPages.has(page))await touchEvent(page,'touchCancel');else{await page.keyboard.press('Escape');await page.mouse.up();}await frames(page,1);}
async function downloadRun(page,id,path){const pending=page.waitForEvent('download',{timeout:15000});await tap(page,id);const file=await pending;await file.saveAs(path);return readFile(path,'utf8');}

try{for(const mode of modes){const context=await browser.newContext({viewport:mode.viewport,isMobile:mode.isMobile,hasTouch:mode.hasTouch});await installClock(context);
  const page=await context.newPage(),errors=[],cases=[];if(mode.hasTouch){touchPages.add(page);touchSessions.set(page,await context.newCDPSession(page));}
  page.on('pageerror',error=>errors.push(String(error)));page.setDefaultTimeout(30000);
  const pass=name=>{assert.equal(cases.includes(name),false,'Duplicate proof case');cases.push(name);console.log('MAUL_BATCH_CASE_PASSED',mode.name,name);};
  try{
    const response=await page.goto(base+'/index.html?'+query,{waitUntil:'domcontentloaded',timeout:60000});assert.ok(response?.ok(),'Editor artifact failed to load');
    const sourceSha256=createHash('sha256').update(await response.body()).digest('hex');console.log('MAUL_BATCH_SOURCE_SHA256',mode.name,sourceSha256);
    await page.waitForFunction(()=>window.SWYRL_ENGINE_MAUL?.batchStatus&&window.SWYRL_ENGINE_AGENT.project().canonicalId==='maul-frostveil',undefined,{timeout:60000});
    await page.locator('#perfPreset').selectOption('medium',{force:true});await page.evaluate(()=>window.__maulClock.freeze());await frames(page,2);
    assert.equal(await page.evaluate(()=>window.SWRLZ_FORGE_BUILD?.version),'v11.62','Wrong engine release');
    const canonical=await saved(page),check=await preflight(page);assert.equal(canonical.project.maulLayout,'classic-v2');assert.equal(canonical.project.maulSpawnStyle,profile);
    // A launchable, separately packaged v11.2 starter must be the source for the actual Projects tile.
    const starterResponse=await context.request.get(base+'/scenes/maul-frostveil-flight.swyrl.json');
    assert.equal(starterResponse.ok(),true,'Dedicated v11.2 Maul starter must ship as a downloadable native scene');
    const starterScene=await starterResponse.json();
    assert.equal(starterScene.version,11.2,'Packaged Maul starter must identify the v11.2 native engine');
    for(const setting of ['maulLayout','maulSpawnStyle','maulConstruction','maulSpawnProtection','maulBuilderFlight','maulVisualStyle'])
      assert.equal(canonical.project[setting],starterScene.project[setting],'Projects starter diverged from packaged scene: '+setting);
    assert.equal(canonical.project.name,starterScene.project.name,'Projects tile did not open the named v11.2 flying builder scene');
    assert.deepEqual(canonical.scene.actors.filter(a=>a.type==='maul-builder').map(a=>a.id).sort(),
      starterScene.scene.actors.filter(a=>a.type==='maul-builder').map(a=>a.id).sort(),
      'Default starter did not load the nine builders from packaged native scene');
    assert.equal((await page.evaluate(()=>window.SWYRL_ENGINE_MAUL.artStatus())).enabled,true,'Glacial art not enabled for packaged Maul starter');

    assert.equal(check.ok,true,'The default grouped starter failed preflight: '+check.errors.join(' '));assert.equal(check.map.spawnStyle,profile);
    assert.equal(canonical.scene.actors.length,78);assert.equal(canonical.editor.layers.length,6);
    for(const layer of canonical.editor.layers)assert.ok(canonical.scene.actors.some(a=>a.editorLayerIds?.includes(layer.id)),'Empty native layer '+layer.name);
    assert.equal(canonical.scene.actors.filter(a=>towerActorTypes.has(a.type)).length,0,'Player one must not open with authored buildings');
    assert.equal(check.towers.length,0);assert.equal(canonical.scene.actors.filter(a=>a.type==='maul-builder').length,9);
    await page.evaluate(()=>window.SWYRL_ENGINE_AGENT.openProjects());await frames(page,2);await press(page,'[data-project-template="maul-frostveil"]');await frames(page,2);
    assert.deepEqual(authored(await saved(page)),authored(canonical),'Hub default differs from native grouped starter');await play(page);
    assert.equal((await state(page)).playerTowers,0,'Player one must begin Play with no free starter buildings');assert.equal((await state(page)).towers.filter(t=>t.owner==='player').length,0);
    assert.equal(canonical.project.maulConstruction,'walk-v1','New canonical map must enable physical builder construction');
    assert.equal(canonical.project.maulBuilderFlight,'hover-v1','Current Frostveil must opt into direct flying builders');
    assert.equal(canonical.project.maulVisualStyle,'glacial-v2','Current Frostveil must use glacial visual materials');
    const flight=await page.evaluate(()=>window.SWYRL_ENGINE_MAUL.flightStatus());
    assert.equal(flight.enabled,true,'Flying builder profile inactive');
    assert.equal(flight.speed,15,'Builder speed differs from v11.2 design');
    assert.equal(flight.builders.length,9,'All nine builders must retain a hover actor');
    for(const pilot of flight.builders)close(pilot.position[1],flight.height,'Builder is not flying at match start',.125);
    assert.equal(canonical.project.maulSpawnProtection,'full-pad-v1');
    assert.equal(await page.locator('#maulBuildWall').isVisible(),false,'Wall construction must not appear in the current map');
    const initialWalk=await state(page),walkMap=initialWalk.map;
    await sector(page,0);await native(page,'maulBuildArrow');
    await gridTap(page,walkMap,5,12,true);
    assert.equal((await state(page)).playerTowers,0,'Construction must not complete instantly');
    assert.equal((await state(page)).gold,initialWalk.gold,'Queued construction must not charge gold early');
    assert.equal((await page.evaluate(()=>window.SWYRL_ENGINE_MAUL.walkBuildStatus())).pending.length,1,'Builder needs a pending travel order');
    const hovering=(await page.evaluate(()=>window.SWYRL_ENGINE_MAUL.walkBuildStatus())).pending[0];
    assert.deepEqual(hovering.destination,{x:5,z:12},'Flying builder must construct directly above the chosen tower cell');
    await until(page,s=>s.playerTowers===1,'Builder walked to tower footprint then constructed',320);
    assert.equal((await page.evaluate(()=>window.SWYRL_ENGINE_MAUL.walkBuildStatus())).pending.length,0);
    assert.equal((await state(page)).gold,initialWalk.gold-20);
    const rejectedSpawn=await page.evaluate(()=>window.SWYRL_ENGINE_MAUL.status().map.reserved.some(p=>p.x===6&&p.z===3));
    assert.equal(rejectedSpawn,true,'Enemy arrival region must reject building');

    await stop(page);assert.deepEqual(authored(await saved(page)),authored(canonical),'Stop adds buildings or changes authored starter');
    const pieces=await prototypes(page,canonical),empty=fixture(canonical,pieces);
    pass('native_default_hub_and_play_stop_have_nine_builders_and_no_player_one_start_buildings');

    await native(page,'maulRulesBtn');await page.locator('#maulRule_startGold').fill('777');await page.locator('#maulRule_preparation').fill('12');
    await page.locator('#maulRule_intermission').fill('3');if(await page.locator('#maulRule_autoWaves').isChecked())await tap(page,'maulRule_autoWaves');
    await native(page,'maulRulesApply');await native(page,'maulRulesClose');const configured=await saved(page),exported=await exportMap(page,mode);
    assert.deepEqual(authored(exported),authored(configured));assert.equal(exported.project.maulSpawnStyle,profile);assert.equal(exported.project.maul.startGold,777);
    assert.equal(exported.project.maul.preparation,12);assert.equal(exported.project.maul.intermission,3);assert.equal(exported.project.maul.autoWaves,false);
    await importFixture(page,exported);assert.equal((await preflight(page)).map.spawnStyle,profile);await play(page);assert.equal((await state(page)).gold,777);await stop(page);
    assert.deepEqual(authored(await saved(page)),authored(exported));
    pass('native_rules_save_load_and_replay_preserve_grouped_spawn_profile_and_empty_map');

    await load(page,empty);await native(page,'maulStartWave');let s=await state(page);assert.equal(s.wave,1);assert.equal(groupEvents(s).length,1);verifyBatch(s,groupEvents(s)[0]);
    const first=structuredClone(groupEvents(s)[0]);await frames(page,20);s=await state(page);assert.equal(groupEvents(s).length,1,'Second batch arrives without the short group delay');assert.equal(spawnEvents(s).length,18,'One-by-one minions leaked out between grouped batches');
    s=await until(page,s=>groupEvents(s).length===2,'Second simultaneous scatter batch',100);verifyBatch(s,groupEvents(s)[1]);
    s=await until(page,s=>groupEvents(s).length===3,'Third simultaneous scatter batch',100);verifyBatch(s,groupEvents(s)[2]);
    const batches=groupEvents(s);assert.equal(spawnEvents(s).length,54,'Round minion count changed');assert.equal(s.queued,0);
    for(let i=1;i<3;i++)close(batches[i].t-batches[i-1].t,2.5,'Actual grouped spawn interval',.06);
    assert.deepEqual(batches.map(e=>e.details.at),[0,2.5,5]);assert.equal(new Set(batches.flatMap(e=>e.details.members.map(m=>m.id))).size,54);
    await page.screenshot({path:resolve(output,mode.name+'-three-scattered-groups.png')});await stop(page);assert.deepEqual(authored(await saved(page)),authored(empty));
    pass('real_first_round_spawns_three_scattered_simultaneous_groups_with_quiet_intervals');

    const obstructed=structuredClone(empty),ridge=obstructed.scene.actors.find(a=>a.type==='maul-cliff');
    const map=check.map,blockPosition=world(map,5,3);obstructed.scene.actors.push({...structuredClone(ridge),id:'acceptance-spawn-ridge',name:'Authored spawn-side obstacle',
      position:[blockPosition.x,0,blockPosition.z],rotation:[0,0,0],scale:[1,1,1],maul:{width:1,depth:1},editorLayerIds:['maul-layer-1']});
    await importFixture(page,obstructed);assert.equal((await preflight(page)).ok,true,'Clear-center spawn with a small side obstacle should remain playable');
    assert.ok((await preflight(page)).map.blocked.some(p=>p.x===5&&p.z===3),'Native edited cliff did not block the intended scatter cell');
    await play(page);await native(page,'maulStartWave');s=await state(page);assert.equal(groupEvents(s).length,1);verifyBatch(s,groupEvents(s)[0]);
    for(const member of groupEvents(s)[0].details.members.filter(m=>m.sector===0)){assert.notDeepEqual([member.cx,member.cz],[5,3]);const unit=s.units.find(u=>u.id===member.id);assert.ok(unit.path.length>1);}
    await stop(page);assert.deepEqual(authored(await saved(page)),authored(obstructed));
    pass('native_edited_spawn_area_obstacle_keeps_group_births_on_clear_routable_distinct_ground');

    await load(page,empty);await sector(page,0);let liveMap=(await state(page)).map;await native(page,'maulBuildArrow');
    const before=await state(page),held=await heldPlacement(page,liveMap,5,11),releaseFinger=await canvasPoint(page,liveMap,5,12,{placing:true});
    if(mode.hasTouch){await page.waitForTimeout(40);await touchEvent(page,'touchMove',releaseFinger);}else await page.mouse.move(releaseFinger.x,releaseFinger.y);await frames(page,1);
    const releaseGuide=(await ui(page)).preview;assert.equal(releaseGuide?.valid,true);assert.deepEqual([releaseGuide.cx,releaseGuide.cz],[5,12]);
    assert.notDeepEqual([releaseGuide.cx,releaseGuide.cz],[held.guide.cx,held.guide.cz],'Dragged preview did not update its snapped cell');
    await releasePlacement(page);s=await state(page);
    const tower=s.towers.find(t=>!before.towers.some(old=>old.id===t.id));assert.ok(tower,'Touch release did not build visible preview');assert.deepEqual([tower.cx,tower.cz],[releaseGuide.cx,releaseGuide.cz]);
    close(s.gold,before.gold-20,'Player building costs gold');assert.equal(s.playerTowers,1);
    const reservedGuide=await preview(page,liveMap,6,3);assert.equal(reservedGuide.valid,false);assert.match(reservedGuide.reason,/spawn|open|reserved|area/i);
    const beforeSpawnReject=await state(page);await gridTap(page,liveMap,6,3,true);assert.equal((await state(page)).gold,beforeSpawnReject.gold);assert.equal((await state(page)).towers.length,beforeSpawnReject.towers.length);
    await sector(page,7);await native(page,'maulBuildWall');const forbidden=await preview(page,liveMap,17,43);assert.equal(forbidden.valid,false);assert.match(forbidden.reason,/wall|water|coast/i);
    const beforeCoast=await state(page);await gridTap(page,liveMap,17,43,true);assert.equal((await state(page)).gold,beforeCoast.gold);assert.equal((await state(page)).towers.length,beforeCoast.towers.length);
    pass('physical_preview_footprint_and_ghost_clear_finger_and_release_builds_exact_grid_cell');

    await sector(page,0);if((await ui(page)).buildKind!=='maze-wall')await native(page,'maulBuildWall');const beforeCancel=await state(page);await heldPlacement(page,liveMap,6,12);await cancelPlacement(page);
    assert.equal((await ui(page)).preview,null);assert.equal((await state(page)).gold,beforeCancel.gold);assert.equal((await state(page)).towers.length,beforeCancel.towers.length);
    if((await ui(page)).buildKind)await native(page,'maulCancel');await selectTower(page,liveMap,tower);await gridTap(page,liveMap,5,14);
    assert.equal((await ui(page)).selectedTowerId,null,'A ground tap should clear tower selection');
    const controlledBuilder=empty.scene.actors.find(a=>a.type==='maul-builder'&&a.maul.sector===0);await stop(page);await configureRecorder(page,true);
    await load(page,empty);await sector(page,0);const gestureRun=await runData(page),beforePan=(await runFrame(page,gestureRun)).camera.target;
    const from=await canvasPoint(page,liveMap,5,14),to={x:from.x+28,y:from.y+18};
    assert.equal(await page.evaluate(p=>{const hit=document.elementFromPoint(p.x,p.y);return hit?.tagName==='CANVAS'||hit?.id==='viewport';},to),true);
    if(mode.hasTouch){await touchEvent(page,'touchStart',from);for(let step=1;step<=8;step++){await page.waitForTimeout(30);await touchEvent(page,'touchMove',{x:from.x+(to.x-from.x)*step/8,y:from.y+(to.y-from.y)*step/8});await frames(page,1);}await touchEvent(page,'touchEnd');}
    else{await page.mouse.move(from.x,from.y);await page.mouse.down();await page.mouse.move(to.x,to.y,{steps:3});await page.mouse.up();}
    await frames(page,1);const afterPan=(await runFrame(page,await runData(page))).camera.target;assert.ok(Math.hypot(afterPan[0]-beforePan[0],afterPan[2]-beforePan[2])>.25,'Canvas pan failed');
    await sector(page,0);await gridTap(page,liveMap,5,14);assert.deepEqual((await runFrame(page,await runData(page))).game.builderOrders[controlledBuilder.id]?.path.at(-1),{x:5,z:14});
    await stop(page);assert.deepEqual(authored(await saved(page)),authored(empty));
    pass('cancelled_physical_placement_pan_double_tap_selection_and_builder_orders_remain_independent');

    await load(page,empty);await sector(page,0);await native(page,'maulStartWave');await frames(page,16);s=await state(page);
    const liveRun=await runData(page),snapshot=await runFrame(page,liveRun);assert.equal(snapshot.game.map.spawnStyle,profile);
    assert.equal(snapshot.game.pendingSpawns.length,2,'Recorder must retain the two complete future groups');
    for(const group of snapshot.game.pendingSpawns){assert.ok(Array.isArray(group.members)&&group.members.length===18);assert.ok([2.5,5].includes(group.at));}
    assert.ok(liveRun.events.some(e=>e.type==='maul-spawn-group'&&e.details.members.length===18));
    for(const unit of s.units.filter(u=>u.alive!==false)){const entity=snapshot.entities[unit.id];assert.ok(entity);assert.equal(entity.spawnGroup,unit.spawnGroup);assert.equal(entity.spawnIndex,unit.spawnIndex);assert.deepEqual(entity.spawnOrigin,unit.spawnOrigin);assert.equal(entity.route.stage,unit.stage);close(entity.position[0],unit.x,'Recorded group X');close(entity.position[2],unit.z,'Recorded group Z');}
    await until(page,s=>groupEvents(s).length===3,'Third recorded group',200);await native(page,'maulStop');const run=await runData(page,liveRun.id);
    assert.equal(run.complete,true);assert.equal(run.capture.incomplete,false);assert.equal(run.endReason,'stopped');assert.equal(run.events.filter(e=>e.type==='maul-spawn-group').length,3);
    assert.equal((await page.evaluate(run=>window.SWYRL_ENGINE_RUNS.validate(run),run)).ok,true);
    const nativeFrame=await runFrame(page,run),independent=reconstruct(run);assert.deepEqual(nativeFrame.entities,independent.entities);assert.deepEqual(nativeFrame.camera,independent.camera);assert.deepEqual(nativeFrame.game,independent.game);
    await native(page,'stRunLauncher');await page.locator('#stRunPanel').waitFor({state:'visible'});
    const jsonPath=resolve(output,mode.name+'.grouped-maul.swyrl-run.json'),textPath=resolve(output,mode.name+'.grouped-maul.swyrl-run.txt'),htmlPath=resolve(output,mode.name+'.grouped-maul.swyrl-run.html');
    assert.deepEqual(JSON.parse(await downloadRun(page,'stRunExportJson',jsonPath)),run);const transcript=await downloadRun(page,'stRunExportText',textPath);assert.match(transcript,/group/i);assert.match(transcript,/camera/i);
    const html=await downloadRun(page,'stRunExportHtml',htmlPath);assert.ok(html.includes('SWYRL_RUN_VIEWER'));assert.ok(html.includes('function stRunDrawMaul('));assert.ok(html.includes(profile));
    const zippedWait=page.waitForEvent('download',{timeout:15000});await tap(page,'stRunExportGzip');
    let zippedFile;try{zippedFile=await zippedWait;}catch(error){
      console.log('MAUL_GZIP_EXPORT_DEBUG',JSON.stringify(await page.evaluate(()=>({
        message:document.getElementById('stRunImportFeedback')?.textContent,
        label:document.getElementById('stRunExportGzip')?.textContent,
        disabled:document.getElementById('stRunExportGzip')?.disabled,
        rawDisabled:document.getElementById('stRunExportJson')?.disabled,
        supported:typeof CompressionStream,hasRecord:!!window.SWYRL_ENGINE_RUNS?.data?.(),
      }))));throw error;
    }
    assert.match(zippedFile.suggestedFilename(),/\.swyrl-run\.json\.gz$/);const gzip=await readFile(await zippedFile.path());
    assert.ok(gzip.length<Buffer.byteLength(JSON.stringify(run)),'Gzip must reduce native recording bytes');
    assert.deepEqual(JSON.parse(gunzipSync(gzip).toString('utf8')),run,'Compressed recording changed captured state/events');
    await page.locator('#stRunFile').setInputFiles({name:'acceptance.swyrl-run.json.gz',mimeType:'application/gzip',buffer:gzip});
    // The deterministic browser clock is frozen in this suite; Playwright's
    // default waitForFunction polls via requestAnimationFrame and may time out
    // after import succeeded. Observe the live DOM from the Node runner instead.
    let compressedImportFeedback='';
    for(let attempt=0;attempt<120;attempt++){
      compressedImportFeedback=await page.locator('#stRunImportFeedback').textContent()||'';
      if(compressedImportFeedback.includes('Compressed recording opened successfully'))break;
      await page.waitForTimeout(250);
    }
    assert.match(compressedImportFeedback,/Compressed recording opened successfully/,
      'Gzip import feedback did not reach success: '+compressedImportFeedback);
    await native(page,'stRunClose');
    const spectator=await context.newPage(),spectatorErrors=[];spectator.on('pageerror',error=>spectatorErrors.push(String(error)));await spectator.route('**/*',route=>route.abort());await spectator.setContent(html,{waitUntil:'domcontentloaded'});
    await spectator.waitForFunction(()=>window.SWYRL_RUN_VIEWER?.state);await spectator.evaluate(duration=>window.SWYRL_RUN_VIEWER.seek(duration),run.duration);
    const offline=await spectator.evaluate(()=>window.SWYRL_RUN_VIEWER.state());assert.deepEqual(offline.entities,nativeFrame.entities);assert.deepEqual(offline.camera,nativeFrame.camera);assert.deepEqual(offline.game,nativeFrame.game);
    assert.equal(await spectator.locator('#stRunReviewCanvas').isVisible(),true);
    const colors=await spectator.evaluate(()=>{const c=document.getElementById('stRunReviewCanvas'),d=c.getContext('2d').getImageData(0,0,c.width,c.height).data,found=new Set();
      for(let i=0;i<d.length;i+=4){const s=[d[i],d[i+1],d[i+2]].map(x=>x.toString(16).padStart(2,'0')).join('');if(s==='d9eaf0'||s==='24495c')found.add(s);}
      return [...found];});assert.ok(colors.includes('d9eaf0')&&colors.includes('24495c'),'Maul spectator must show snowfields and blue water, not beige blocks');
    await spectator.locator('#stRunViewMode').selectOption('camera');assert.deepEqual(spectatorErrors,[]);await spectator.close();
    assert.deepEqual(authored(await saved(page)),authored(empty));
    pass('full_native_group_recording_exports_future_batches_birth_events_and_offline_spectator');

    await importFixture(page,empty);const beforeSimulate=(await runStatus(page)).runs.map(r=>r.id);await native(page,'simulateBtn');assert.equal((await state(page)).active,true);assert.equal((await runStatus(page)).active,null);
    await native(page,'maulStartWave');await frames(page,10);assert.equal(groupEvents(await state(page)).length,1);await stop(page);
    assert.deepEqual((await runStatus(page)).runs.map(r=>r.id),beforeSimulate);assert.deepEqual(authored(await saved(page)),authored(empty));await configureRecorder(page,false);
    pass('native_simulate_uses_grouped_spawns_without_creating_or_overwriting_play_recordings');

    const legacy=await page.evaluate(async()=>{const response=await fetch('scenes/maul-frostveil-classic.swyrl.json');if(!response.ok)throw Error('Published v10.7 map unavailable');return response.json();});
    assert.equal(legacy.project.maulSpawnStyle,undefined);assert.equal(legacy.scene.actors.filter(a=>towerActorTypes.has(a.type)).length,3);
    await importFixture(page,legacy);assert.equal((await preflight(page)).ok,true);assert.equal((await preflight(page)).map.spawnStyle,undefined);
    const legacyExport=await exportMap(page,mode);assert.deepEqual(authored(legacyExport),authored(legacy));await importFixture(page,legacyExport);await play(page);
    assert.equal((await state(page)).playerTowers,3,'A legacy authored project must retain its saved starter towers');await native(page,'maulStartWave');await frames(page,20);s=await state(page);
    assert.equal(groupEvents(s).length,0,'Old authored projects silently opted into new spawn scheduling');
    const sectorBirths=spawnEvents(s).filter(e=>e.details.sector===0);assert.ok(sectorBirths.length>=2);assert.ok(new Set(sectorBirths.map(e=>e.t)).size>=2,'Legacy sequential spawn cadence changed');
    await stop(page);assert.deepEqual(authored(await saved(page)),authored(legacy));await page.evaluate(()=>window.SWYRL_ENGINE_AGENT.openProjects());await frames(page,2);await press(page,'[data-project-template="maul-frostveil"]');await frames(page,2);
    assert.deepEqual(authored(await saved(page)),authored(canonical));
    pass('published_v10_7_import_keeps_authored_buildings_and_sequential_spawns_then_hub_returns_grouped_default');

    assert.deepEqual(errors,[],'Browser errors during grouped Maul acceptance');assert.equal(cases.length,9,'Every focused batch regression must execute');
    receipts.push({mode:mode.name,viewport:mode.viewport,cases,canonicalId:canonical.project.canonicalId,version:'v11.62',sourceSha256,layout:'classic-v2',spawnStyle:profile,nativeRun:run.id,mapActors:canonical.scene.actors.length,groups:batches.map(e=>({group:e.details.group,t:e.t,scheduledAt:e.details.at,count:e.details.count})),firstBatch:first.details});
    await writeFile(resolve(output,mode.name+'-receipt.json'),JSON.stringify(receipts.at(-1),null,2));console.log(mode.name==='desktop'?'MAUL_BATCH_DESKTOP_PASS':'MAUL_BATCH_MOBILE_PASS');
  }catch(error){await page.screenshot({path:resolve(output,mode.name+'-failure.png')}).catch(()=>{});await writeFile(resolve(output,mode.name+'-failure.json'),JSON.stringify({message:String(error),cases,errors,state:await state(page).catch(()=>null),ui:await ui(page).catch(()=>null)},null,2));throw error;}
  finally{await context.close();}
}await writeFile(resolve(output,'receipt.json'),JSON.stringify(receipts,null,2));console.log('MAUL_BATCH_ALL_VIEWPORTS_PASS');}
finally{await browser.close();}
