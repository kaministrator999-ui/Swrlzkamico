import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {mkdir,readFile,writeFile} from 'node:fs/promises';
import {resolve} from 'node:path';
import {createHash} from 'node:crypto';

// Ordinary native editor fixtures are imported only while stopped. Real mouse
// and phone touch drive Play, placement and tower orders. The controlled clock
// advances the existing engine RAF; it never edits combat, economy or match state.
const base=(process.env.SWYRL_ANIME_TEST_URL||'http://127.0.0.1:8765').replace(/\/$/,'');
const query=new URLSearchParams(process.env.SWYRL_ANIME_TEST_QUERY||'');query.set('project','maul-frostveil');
const output=resolve(process.env.SWYRL_ANIME_SCREENSHOTS_DIR||'maul-layout-acceptance');await mkdir(output,{recursive:true});
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
function fixture(canonical,pieces,{rules={},towers=[]}={}){const data=structuredClone(canonical),map={cell:2,origin:{x:-40,z:-44}};
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


const expectedSpawns=[[7,3],[20,3],[33,3],[3,24],[20,23],[37,24],[4,33],[20,34],[36,33]];
const expectedGates=[[7,21],[20,21],[33,21],[8,26],[20,26],[32,26],[10,39],[20,41],[30,39]];
const cellOf=(map,actor)=>({x:Math.round((actor.position[0]-map.origin.x)/map.cell),z:Math.round((actor.position[2]-map.origin.z)/map.cell)});
const orderedActors=(canonical,type)=>canonical.scene.actors.filter(a=>a.type===type).sort((a,b)=>a.maul.sector-b.maul.sector);
// Independently reconstruct the renderer projection from the exported world
// pose and lens matrix. This does not import Three or call engine projection code.
function recordedPoint(camera,position,rect){
  const v=position.map((n,i)=>n-camera.position[i]),[x,y,z,w]=[-camera.quaternion[0],-camera.quaternion[1],-camera.quaternion[2],camera.quaternion[3]];
  const tx=2*(y*v[2]-z*v[1]),ty=2*(z*v[0]-x*v[2]),tz=2*(x*v[1]-y*v[0]);
  const r=[v[0]+w*tx+y*tz-z*ty,v[1]+w*ty+z*tx-x*tz,v[2]+w*tz+x*ty-y*tx],m=camera.projectionMatrix;
  const clipW=m[3]*r[0]+m[7]*r[1]+m[11]*r[2]+m[15];assert.ok(clipW>0,'Recorded object is behind the camera');
  const nx=(m[0]*r[0]+m[4]*r[1]+m[8]*r[2]+m[12])/clipW,ny=(m[1]*r[0]+m[5]*r[1]+m[9]*r[2]+m[13])/clipW;
  return {x:rect.left+(nx+1)*rect.width/2,y:rect.top+(1-ny)*rect.height/2};
}
async function downloadRun(page,id,path){const pending=page.waitForEvent('download',{timeout:15000});await tap(page,id);const file=await pending;await file.saveAs(path);return readFile(path,'utf8');}

try{for(const mode of modes){const context=await browser.newContext({viewport:mode.viewport,isMobile:mode.isMobile,hasTouch:mode.hasTouch});await installClock(context);
  const page=await context.newPage(),errors=[],cases=[];if(mode.hasTouch){touchPages.add(page);touchSessions.set(page,await context.newCDPSession(page));}
  page.on('pageerror',error=>errors.push(String(error)));page.setDefaultTimeout(30000);
  const pass=name=>{assert.equal(cases.includes(name),false,'Duplicate proof case');cases.push(name);console.log('MAUL_LAYOUT_CASE_PASSED',mode.name,name);};
  try{
    const response=await page.goto(base+'/index.html?'+query,{waitUntil:'domcontentloaded',timeout:60000});
    assert.ok(response?.ok(),'Editor artifact failed to load');const sourceSha256=createHash('sha256').update(await response.body()).digest('hex');
    console.log('MAUL_LAYOUT_SOURCE_SHA256',mode.name,sourceSha256);
    await page.waitForFunction(()=>window.SWYRL_ENGINE_MAUL?.uiStatus&&window.SWYRL_ENGINE_AGENT.project().canonicalId==='maul-frostveil',undefined,{timeout:60000});
    await page.locator('#perfPreset').selectOption('medium',{force:true});await page.evaluate(()=>window.__maulClock.freeze());await frames(page,2);
    assert.equal(await page.evaluate(()=>window.SWRLZ_FORGE_BUILD?.version),'v11.62','Wrong engine release');
    const defaultCanonical=await saved(page);assert.equal(defaultCanonical.project.maulSpawnStyle,'grouped-v1','Hub/query must open current grouped starter');
    const preservedClassic=await page.evaluate(async()=>{const response=await fetch('scenes/maul-frostveil-classic.swyrl.json');if(!response.ok)throw Error('Published classic map unavailable');return response.json();});
    await importFixture(page,preservedClassic);
    const canonical=await saved(page),mapCheck=await preflight(page),canonicalMap=mapCheck.map;
    assert.equal(canonical.project.kind,'maul');assert.equal(canonical.project.maulLayout,'classic-v2');assert.equal(canonical.editor.layers.length,7);
    assert.equal(mapCheck.ok,true,'Authored classic routes failed: '+mapCheck.errors.join(' '));
    assert.equal(canonicalMap.layout,'classic-v2');assert.deepEqual([canonicalMap.cols,canonicalMap.rows,canonicalMap.cell],[41,45,2]);assert.deepEqual(canonicalMap.origin,{x:-40,z:-44});
    for(const [type,expected]of [['maul-spawn',expectedSpawns],['maul-gate',expectedGates]]){
      const list=orderedActors(canonical,type);assert.equal(list.length,9);assert.deepEqual(list.map(a=>{const p=cellOf(canonicalMap,a);return [p.x,p.z];}),expected);}
    assert.equal(orderedActors(canonical,'maul-builder').length,9);assert.equal(canonical.scene.actors.filter(a=>a.type==='maul-exit').length,1);
    const turns=canonical.scene.actors.filter(a=>a.type==='maul-route-turn');assert.equal(turns.length,6);assert.deepEqual(turns.map(a=>a.maul.turnKey).sort(),['eastEntry','eastOuter','eastReturn','westEntry','westOuter','westReturn']);
    for(const turn of turns)assert.deepEqual(cellOf(canonicalMap,turn),canonicalMap.turns[turn.maul.turnKey],'The authored turn must drive the native route');
    assert.deepEqual(cellOf(canonicalMap,canonical.scene.actors.find(a=>a.type==='maul-exit')),{x:20,z:43});
    for(const layer of canonical.editor.layers)assert.ok(canonical.scene.actors.some(a=>a.editorLayerIds?.includes(layer.id)),'Empty authored layer '+layer.name);
    assert.ok(canonical.scene.actors.some(a=>a.type==='maul-snowfield'),'Missing continuous authored snow terrain');assert.ok(canonical.scene.actors.some(a=>a.type==='maul-water'),'Missing southern water');
    assert.ok(canonicalMap.sectors.slice(0,3).every(s=>s.maxZ-s.minZ>s.maxX-s.minX),'Northern bays must be long, not square tiles');
    for(const [x,z]of [[12,10],[27,10],[5,27],[35,27],[16,31],[24,31],[15,43],[25,43]])assert.ok(canonicalMap.blocked.some(p=>p.x===x&&p.z===z),'Missing reference-shaped cliff/coast at '+x+','+z);
    for(const sectorRecord of canonicalMap.sectors)assert.ok(sectorRecord.gates.some(g=>g.x===20&&g.z===41),'A defender stream misses the shared rear catcher');
    assert.ok(canonicalMap.sectors[0].gates.some((p,i,list)=>i&&p.z<list[i-1].z),'West lower wing must return north');
    assert.ok(canonicalMap.sectors[2].gates.some((p,i,list)=>i&&p.z<list[i-1].z),'East lower wing must return north');
    const pieces=await prototypes(page,canonical),empty=fixture(canonical,pieces);
    await page.screenshot({path:resolve(output,mode.name+'-classic-authored-overview.png')});
    pass('native_classic_map_has_long_front_bays_crossbar_lower_returns_shared_harbor_and_seven_layers');

    await page.evaluate(()=>window.SWYRL_ENGINE_AGENT.openProjects());await frames(page,2);await press(page,'[data-project-template="maul-frostveil"]');await frames(page,2);
    assert.deepEqual(authored(await saved(page)),authored(defaultCanonical),'Projects hub must open the current grouped starter');
    await importFixture(page,canonical);await play(page);let s=await state(page);assert.equal(s.map.layout,'classic-v2');assert.equal(s.gold,canonical.project.maul.startGold);assert.deepEqual([...new Set(s.towers.filter(t=>/^ally-[1-8]$/.test(t.owner)).map(t=>t.owner))].sort(),Array.from({length:8},(_,i)=>'ally-'+(i+1)),'Optional support must cover every other defender');
    assert.ok((await page.evaluate(()=>window.SWYRL_ENGINE_MAUL.renderStatus())).meshes>=s.towers.length,'Native towers are not rendered');await stop(page);
    assert.deepEqual(authored(await saved(page)),authored(canonical));
    pass('native_projects_hub_opens_classic_default_and_play_stop_restores_all_authored_actors');

    await native(page,'maulRulesBtn');await page.locator('#maulRule_startGold').fill('777');await page.locator('#maulRule_lives').fill('17');
    await page.locator('#maulRule_waves').fill('2');await page.locator('#maulRule_preparation').fill('12');await page.locator('#maulRule_intermission').fill('3');
    await page.locator('#maulRule_difficulty').selectOption('0.65',{force:true});for(const id of ['maulRule_autoWaves','maulRule_soloSupport'])if(await page.locator('#'+id).isChecked())await tap(page,id);
    await native(page,'maulRulesApply');await native(page,'maulRulesClose');
    const westTurn=turns.find(a=>a.maul.turnKey==='westReturn'),editedTurn=world(canonicalMap,15,34);
    assert.equal(await page.evaluate(({id,position})=>window.SWYRL_ENGINE_AGENT.setTransform(id,{position}),{id:westTurn.id,position:[editedTurn.x,0,editedTurn.z]}),true,'Native authoring could not move the return waypoint');await frames(page,2);
    const editedCheck=await preflight(page);assert.equal(editedCheck.ok,true,'Valid native return-marker edit failed preflight');assert.deepEqual(editedCheck.map.turns.westReturn,{x:15,z:34});assert.ok(editedCheck.map.sectors[0].gates.some(p=>p.x===15&&p.z===34));
    const configured=await saved(page),exported=await exportMap(page,mode);
    assert.deepEqual(authored(exported),authored(configured));assert.equal(exported.project.maulLayout,'classic-v2');
    assert.deepEqual(Object.fromEntries(['startGold','lives','waves','preparation','intermission','difficulty','autoWaves','soloSupport'].map(k=>[k,exported.project.maul[k]])),
      {startGold:777,lives:17,waves:2,preparation:12,intermission:3,difficulty:.65,autoWaves:false,soloSupport:false});
    await importFixture(page,exported);assert.equal((await preflight(page)).map.layout,'classic-v2');assert.equal((await preflight(page)).ok,true);assert.deepEqual((await preflight(page)).map.turns.westReturn,{x:15,z:34});
    pass('native_rules_and_save_load_keep_classic_layout_flag_waypoints_layers_and_settings');

    await load(page,empty);await sector(page,0);let map=(await state(page)).map;const created=[];
    for(const [i,kind]of kinds.entries()){const before=await state(page),tower=await build(page,kind,map,4+i,11);created.push(tower);
      close((await state(page)).gold,before.gold-(await page.evaluate(kind=>window.SWYRL_ENGINE_MAUL.definitions[kind].cost,kind)),'Native build cost '+kind);}
    assert.equal((await state(page)).towers.length,5);assert.equal((await preflight(page)).ok,true);
    await page.screenshot({path:resolve(output,mode.name+'-long-bay-five-tower-family.png')});
    pass('actual_mouse_and_phone_finger_offset_build_all_five_families_on_long_frontline_grid');

    for(const [index,cx,cz,reason]of [[0,12,11,/wall|cliff/i],[0,7,3,/spawn|gate|open/i],[7,17,43,/wall|coast|water/i]]){
      await sector(page,index);const before=await state(page),guide=await preview(page,map,cx,cz);assert.equal(guide?.valid,false,'Protected terrain shows a legal footprint');assert.match(guide.reason,reason);
      await gridTap(page,map,cx,cz,true);const after=await state(page);assert.equal(after.towers.length,before.towers.length);assert.equal(after.gold,before.gold);}
    pass('physical_cliff_spawn_and_southern_water_previews_reject_building_without_spending');

    await sector(page,0);const arrow=created[0];await selectTower(page,map,arrow);assert.match(await page.locator('#maulSelectedDetail').textContent(),/8 range/);
    const beforeUpgrade=await state(page);await native(page,'maulUpgrade');assert.equal((await state(page)).towers.find(t=>t.id===arrow.id).level,2);close((await state(page)).gold,beforeUpgrade.gold-35,'Upgrade debit');
    assert.match(await page.locator('#maulSelectedDetail').textContent(),/9 range/);await page.locator('#maulPriority').selectOption('strong',{force:true});await frames(page,2);
    assert.equal((await state(page)).towers.find(t=>t.id===arrow.id).priority,'strong');const beforeSell=await state(page);await native(page,'maulSell');
    assert.equal((await state(page)).towers.some(t=>t.id===arrow.id),false);close((await state(page)).gold,beforeSell.gold+38,'Sell investment refund');await stop(page);
    assert.deepEqual(authored(await saved(page)),authored(empty));
    pass('visible_tower_head_hit_phone_double_tap_upgrade_priority_and_sell_work_on_classic_camera');

    const blocked=fixture(canonical,pieces,{towers:Array.from({length:10},(_,i)=>i+2).filter(cx=>cx!==7).map(cx=>({kind:'maze-wall',cx,cz:12}))});
    await load(page,blocked);await sector(page,0);map=(await state(page)).map;await native(page,'maulBuildWall');const beforeBlock=await state(page),guide=await preview(page,map,7,12);
    assert.equal(guide?.valid,false,'Last northern maze gap may not close');assert.match(guide.reason,/route|sector|exit/i);await gridTap(page,map,7,12,true);
    assert.equal((await state(page)).gold,beforeBlock.gold);assert.equal((await state(page)).towers.length,beforeBlock.towers.length);await stop(page);assert.deepEqual(authored(await saved(page)),authored(blocked));
    pass('native_wall_placement_cannot_seal_last_long_bay_route_or_corrupt_authored_maze');

    await load(page,empty);map=(await state(page)).map;for(let i=0;i<9;i++){await sector(page,i);const record=map.sectors[i],p=world(map,(record.minX+record.maxX)/2,(record.minZ+record.maxZ)/2);
      assert.equal((await page.evaluate(p=>window.SWYRL_ENGINE_MAUL.pointScreen(p.x,p.z),p)).visible,true,'Sector camera misses defender '+i);}
    await native(page,'maulOverview');for(const p of [...map.spawns,map.exit]){const at=world(map,p.x,p.z);assert.equal((await page.evaluate(p=>window.SWYRL_ENGINE_MAUL.pointScreen(p.x,p.z),at)).visible,true,'Overview clips an entrance or harbor');}
    await page.screenshot({path:resolve(output,mode.name+'-classic-live-overview.png')});await stop(page);
    pass('native_sector_camera_controls_and_overview_frame_all_long_bays_wings_and_harbor');

    const looping=fixture(canonical,pieces,{rules:{lives:200,spawnInterval:.1,preparation:0}});await load(page,looping);await native(page,'maulStartWave');await native(page,'maulSpeed');await native(page,'maulSpeed');
    const returning=await until(page,state=>state.units.some(u=>u.alive!==false&&u.sector===6&&u.stage>=1&&u.cz<38&&u.cx>=10),'Native lower-left creep returning north',900);
    const tracking=returning.units.find(u=>u.alive!==false&&u.sector===6&&u.stage>=1&&u.cz<38&&u.cx>=10);assert.ok(tracking);
    assert.ok(tracking.path.some((p,i,list)=>i&&p.z<list[i-1].z),'Real native creep did not receive a north-return path');await sector(page,6);map=(await state(page)).map;
    const beforeRoute=(await state(page)).units.find(u=>u.id===tracking.id),rerouteTower=await build(page,'arrow',map,3,36),afterRoute=(await state(page)).units.find(u=>u.id===tracking.id);
    assert.ok(afterRoute.stage>=beforeRoute.stage,'Build reroute repeated a completed lower-wing stage');assert.ok(afterRoute.path.every(p=>p.stage>=beforeRoute.stage));
    await selectTower(page,map,rerouteTower);await native(page,'maulSell');const afterSell=(await state(page)).units.find(u=>u.id===tracking.id);assert.ok(afterSell.stage>=afterRoute.stage);
    assert.ok(afterSell.path.every(p=>p.stage>=afterRoute.stage),'Sell reroute returned the live creep to old objectives');
    const previousStage=afterSell.stage;await frames(page,25);const later=(await state(page)).units.find(u=>u.id===tracking.id);assert.ok(later.stage>=previousStage);await stop(page);
    assert.deepEqual(authored(await saved(page)),authored(looping));
    pass('real_creep_returns_north_through_lower_wing_and_build_sell_reroutes_keep_completed_stage');

    await load(page,empty);for(const speed of [2,4,1]){await native(page,'maulSpeed');assert.equal((await state(page)).speed,speed);const before=(await state(page)).elapsed;await frames(page,10);close((await state(page)).elapsed-before,.5*speed,'Native speed '+speed,.005);}
    await native(page,'maulPause');const paused=await state(page);await frames(page,40);assert.equal((await state(page)).paused,true);close((await state(page)).elapsed,paused.elapsed,'Pause simulation freeze');
    assert.equal(await page.locator('#maulStartWave').isEnabled(),false);assert.equal(await page.locator('#maulBuildArrow').isEnabled(),false);await native(page,'maulPause');await stop(page);
    assert.deepEqual(authored(await saved(page)),authored(empty));
    pass('classic_play_speed_pause_and_stop_freeze_orders_and_restore_editable_scene');

    const defenders=expectedSpawns.flatMap(([cx,cz])=>[-1,1].map(dx=>({kind:'storm',cx:cx+dx,cz:cz+1,level:3})));
    const winning=fixture(canonical,pieces,{rules:{waves:10,lives:200,difficulty:.25,spawnInterval:.1,preparation:0,autoWaves:true},towers:defenders});
    await load(page,winning);await native(page,'maulSpeed');await native(page,'maulSpeed');
    const won=await until(page,s=>s.phase==='won','Ten real ground, flying and boss waves defended',1800);
    assert.equal(won.wave,10);assert.ok(won.kills>0);assert.equal(won.events.filter(e=>e.type==='wave-cleared').length,10);assert.ok(won.events.some(e=>e.type==='spawned'&&e.details.air));assert.ok(won.events.some(e=>e.type==='spawned'&&e.details.boss));
    assert.equal(won.events.filter(e=>e.type==='won').length,1);assert.ok(won.lives>0);assert.equal(await page.locator('#maulStartWave').isEnabled(),false);await stop(page);assert.deepEqual(authored(await saved(page)),authored(winning));
    pass('native_classic_combat_defends_ten_real_waves_including_fliers_and_siege_bosses');

    const losing=fixture(canonical,pieces,{rules:{lives:1,preparation:0}});await load(page,losing);await native(page,'maulStartWave');await native(page,'maulSpeed');await native(page,'maulSpeed');
    const lost=await until(page,s=>s.phase==='lost','Real creep reaching the south-center shared exit',600);assert.equal(lost.lives,0);assert.equal(lost.leaks,1);assert.equal(lost.kills,0);
    assert.ok(lost.events.some(e=>e.type==='leaked'&&e.details.sector===7),'Rear catcher stream must reach the shared harbor first');assert.equal(lost.events.filter(e=>e.type==='lost').length,1);await stop(page);assert.deepEqual(authored(await saved(page)),authored(losing));
    pass('native_rear_catcher_creep_reaches_one_shared_harbor_and_costs_a_life');

    const invalidTurn=structuredClone(empty);invalidTurn.scene.actors=invalidTurn.scene.actors.filter(a=>!(a.type==='maul-route-turn'&&a.maul.turnKey==='westReturn'));await importFixture(page,invalidTurn);assert.equal((await preflight(page)).ok,false,'Missing lower return marker must fail authored preflight');await native(page,'playBtn');assert.equal((await state(page)).active,false);assert.deepEqual(authored(await saved(page)),authored(invalidTurn));
    for(const [axis,offset,label]of [[0,.5,'off-grid X'],[1,1,'raised Y']]){const misplacedTurn=structuredClone(empty),turn=misplacedTurn.scene.actors.find(a=>a.type==='maul-route-turn'&&a.maul.turnKey==='westReturn');turn.position[axis]+=offset;
      await importFixture(page,misplacedTurn);const turnCheck=await preflight(page);assert.equal(turnCheck.ok,false,'Lower return marker '+label+' must fail authored preflight');assert.match(turnCheck.reason,/lower-lane turn.*ground grid/i);
      await native(page,'playBtn');assert.equal((await state(page)).active,false,'Native Play accepted a lower return marker '+label);assert.equal(await page.locator('#maulHUD').isVisible(),false);assert.deepEqual(authored(await saved(page)),authored(misplacedTurn),'Rejected lower return marker '+label+' changed the authored scene');}
    const invalid=structuredClone(empty);invalid.scene.actors=invalid.scene.actors.filter(a=>!(a.type==='maul-gate'&&a.maul.sector===0));await importFixture(page,invalid);
    assert.equal((await preflight(page)).ok,false);await native(page,'playBtn');assert.equal((await state(page)).active,false);assert.equal(await page.locator('#maulHUD').isVisible(),false);assert.deepEqual(authored(await saved(page)),authored(invalid));
    pass('native_classic_preflight_rejects_missing_authored_waypoint_and_preserves_bad_project');

    await importFixture(page,empty);await configureRecorder(page,true);const completedBefore=(await runStatus(page)).runs.map(run=>run.id);await native(page,'simulateBtn');
    assert.equal((await state(page)).active,true);assert.equal((await runStatus(page)).active,null);await frames(page,10);await stop(page);assert.deepEqual((await runStatus(page)).runs.map(run=>run.id),completedBefore);assert.deepEqual(authored(await saved(page)),authored(empty));
    pass('native_simulate_on_classic_map_excludes_recordings_and_stop_preserves_authored_state');

    await load(page,empty);await sector(page,0);map=(await state(page)).map;const recordedTower=await build(page,'arrow',map,6,5);await gridTap(page,map,7,3,true);await native(page,'maulCancel');
    const builder=empty.scene.actors.find(a=>a.type==='maul-builder'&&a.maul.sector===0);
    await selectTower(page,map,recordedTower);await gridTap(page,map,5,12);
    const orderedSnapshot=await runFrame(page,await runData(page));
    assert.deepEqual(orderedSnapshot.game.builderOrders[builder.id]?.path.at(-1),{x:5,z:12},'Clearing tower selection changed the ground-tap destination');
    const beforePan=orderedSnapshot.camera.target,panStart=await canvasPoint(page,map,5,14),panEnd={x:panStart.x+32,y:panStart.y+22};
    assert.equal(await page.evaluate(p=>{const hit=document.elementFromPoint(p.x,p.y);return hit?.tagName==='CANVAS'||hit?.id==='viewport';},panEnd),true,'Physical camera pan ends behind the HUD');
    if(mode.hasTouch){await touchEvent(page,'touchStart',panStart);await frames(page,1);for(let step=1;step<=8;step++){await page.waitForTimeout(40);await touchEvent(page,'touchMove',{x:panStart.x+(panEnd.x-panStart.x)*step/8,y:panStart.y+(panEnd.y-panStart.y)*step/8});await frames(page,1);}await touchEvent(page,'touchEnd');}
    else{await page.mouse.move(panStart.x,panStart.y);await page.mouse.down();await page.mouse.move(panEnd.x,panEnd.y,{steps:3});await page.mouse.up();}
    await frames(page,1);const pannedTarget=(await runFrame(page,await runData(page))).camera.target;
    assert.ok(Math.hypot(pannedTarget[0]-beforePan[0],pannedTarget[2]-beforePan[2])>.25,'Native canvas drag did not pan the actual camera');
    // Device gestures need real time even while game updates use a frozen clock.
    if(mode.hasTouch)await page.waitForTimeout(100);
    await native(page,'maulBuildArrow');assert.equal((await ui(page)).buildKind,'arrow','The physical tool tap must activate Arrow placement');const toolTarget=(await runFrame(page,await runData(page))).camera.target;
    for(const axis of [0,1,2])close(toolTarget[axis],pannedTarget[axis],'Choosing a build tool preserves the panned camera target '+axis);
    await native(page,'maulCancel');await sector(page,0);await frames(page,20);await native(page,'maulStartWave');await frames(page,40);const observed=await state(page),liveRun=await runData(page),snapshot=await runFrame(page,liveRun);
    assert.equal(liveRun.mode,'maul');assert.equal(liveRun.capture.incomplete,false);assert.equal(snapshot.game.map.layout,'classic-v2');assert.equal(snapshot.game.gold,observed.gold);assert.equal(snapshot.game.wave,observed.wave);assert.equal(snapshot.game.lives,observed.lives);
    assert.ok(liveRun.events.some(e=>e.type==='maul-built'&&e.details.id===recordedTower.id));assert.ok(liveRun.events.some(e=>e.type==='maul-build-rejected'));assert.ok(liveRun.events.some(e=>e.type==='maul-wave-started'));
    for(const unit of observed.units.filter(u=>u.alive!==false)){const entity=snapshot.entities[unit.id];assert.ok(entity,'Recorded world omits a native creep');close(entity.position[0],unit.x,'Recorded creep X');close(entity.position[2],unit.z,'Recorded creep Z');close(entity.hp,unit.hp,'Recorded creep health');assert.equal(entity.route.stage,unit.stage);assert.deepEqual(entity.route.waypoints,unit.path);}
    assert.ok(liveRun.frames.some(f=>Object.values(f.patch).some(e=>e?.kind==='projectile'&&e.from?.length===3&&e.to?.length===3)),'Recorded native attack traces are absent');
    assert.deepEqual(snapshot.game.shots,observed.shots);assert.ok(snapshot.entities[recordedTower.id]?.parts?.length);assert.ok(snapshot.camera?.position?.length===3);
    assert.equal(snapshot.camera.projectionMatrix.length,16);assert.ok(snapshot.camera.projectionMatrix.every(Number.isFinite));
    if(mode.hasTouch){assert.equal(snapshot.camera.view?.enabled,true);assert.ok(snapshot.camera.view.offsetY>0,'Phone camera must frame the usable area above the HUD');}
    const cameraUnit=observed.units.find(u=>u.alive!==false&&u.sector===0)||observed.units.find(u=>u.alive!==false),cameraPosition=snapshot.entities[cameraUnit.id].position;
    const rect=await page.locator('#viewport').evaluate(element=>element.getBoundingClientRect().toJSON()),independentlyProjected=recordedPoint(snapshot.camera,cameraPosition,rect);
    const nativeProjection=await page.evaluate(p=>window.SWYRL_ENGINE_MAUL.pointScreen(p[0],p[2],p[1]),cameraPosition);assert.equal(nativeProjection.visible,true,'Observed frontline creep should be in the actual camera');
    close(independentlyProjected.x,nativeProjection.x,'Exported camera matrix reproduces native X',1);close(independentlyProjected.y,nativeProjection.y,'Exported camera matrix reproduces native Y',1);

    const recordedBuilder=snapshot.entities[builder.id];assert.ok(recordedBuilder);assert.ok(Math.hypot(recordedBuilder.position[0]-builder.position[0],recordedBuilder.position[2]-builder.position[2])>.25);
    await native(page,'maulPause');const pausedRun=await runData(page);await frames(page,20);close((await runData(page)).duration,pausedRun.duration,'Paused recorder time');await native(page,'maulStop');
    const run=await runData(page,liveRun.id);assert.equal(run.complete,true);assert.equal(run.endReason,'stopped');assert.ok((await page.evaluate(run=>window.SWYRL_ENGINE_RUNS.validate(run),run)).ok);
    const independent=reconstruct(run),nativeFrame=await runFrame(page,run);assert.deepEqual(nativeFrame.entities,independent.entities);assert.deepEqual(nativeFrame.camera,independent.camera);assert.deepEqual(nativeFrame.game,independent.game);assert.deepEqual(authored(await saved(page)),authored(empty));
    await native(page,'stRunLauncher');await page.locator('#stRunPanel').waitFor({state:'visible'});
    const jsonPath=resolve(output,mode.name+'.classic-maul.swyrl-run.json'),textPath=resolve(output,mode.name+'.classic-maul.swyrl-run.txt'),htmlPath=resolve(output,mode.name+'.classic-maul.swyrl-run.html');
    assert.deepEqual(JSON.parse(await downloadRun(page,'stRunExportJson',jsonPath)),run);const transcript=await downloadRun(page,'stRunExportText',textPath);assert.match(transcript,/maul|Frostveil/i);assert.match(transcript,/camera/i);
    const html=await downloadRun(page,'stRunExportHtml',htmlPath);assert.ok(html.includes('SWYRL_RUN_VIEWER'));assert.ok(html.includes('classic-v2'));await native(page,'stRunClose');
    const spectator=await context.newPage(),spectatorErrors=[];spectator.on('pageerror',error=>spectatorErrors.push(String(error)));await spectator.route('**/*',route=>route.abort());await spectator.setContent(html,{waitUntil:'domcontentloaded'});
    await spectator.waitForFunction(()=>window.SWYRL_RUN_VIEWER?.state);await spectator.evaluate(duration=>window.SWYRL_RUN_VIEWER.seek(duration),run.duration);
    const offline=await spectator.evaluate(()=>window.SWYRL_RUN_VIEWER.state());assert.deepEqual(offline.entities,nativeFrame.entities);assert.deepEqual(offline.camera,nativeFrame.camera);assert.deepEqual(offline.game,nativeFrame.game);
    assert.equal(await spectator.locator('#stRunReviewCanvas').isVisible(),true);await spectator.locator('#stRunViewMode').selectOption('camera');await spectator.locator('#stRunObserver').selectOption(recordedTower.id);assert.match(await spectator.locator('#stRunNarrative').inputValue(),/FOLLOWING/);assert.deepEqual(spectatorErrors,[],'Offline camera projection caused browser errors');await spectator.close();await configureRecorder(page,false);assert.equal((await runStatus(page)).error,null);
    pass('full_classic_run_exports_stages_world_camera_attacks_and_offline_spectator_json_text_html');

    const legacy=await page.evaluate(async()=>{const response=await fetch('scenes/maul-frostveil.swyrl.json');if(!response.ok)throw Error('Published legacy map unavailable');return response.json();});await importFixture(page,legacy);
    const legacyCheck=await preflight(page);assert.equal(legacyCheck.ok,true);assert.deepEqual([legacyCheck.map.cols,legacyCheck.map.rows],[31,38]);assert.notEqual(legacyCheck.map.layout,'classic-v2');assert.notEqual((await saved(page)).project.maulLayout,'classic-v2');
    const legacyExport=await exportMap(page,mode);assert.deepEqual(authored(legacyExport),authored(legacy));await importFixture(page,legacyExport);
    await play(page);assert.deepEqual([(await state(page)).map.cols,(await state(page)).map.rows],[31,38]);await stop(page);assert.deepEqual(authored(await saved(page)),authored(legacy));
    await page.evaluate(()=>window.SWYRL_ENGINE_AGENT.openProjects());await frames(page,2);await press(page,'[data-project-template="maul-frostveil"]');await frames(page,2);assert.deepEqual(authored(await saved(page)),authored(defaultCanonical));
    pass('published_legacy_maul_import_keeps_old_geometry_and_projects_switches_back_to_classic_default');

    assert.deepEqual(errors,[],'Browser errors during classic Maul acceptance');assert.equal(cases.length,16,'Every classic layout case must execute');
    receipts.push({mode:mode.name,viewport:mode.viewport,cases,canonicalId:canonical.project.canonicalId,version:'v11.62',sourceSha256,layout:'classic-v2',nativeRun:run.id,mapActors:canonical.scene.actors.length,grid:[41,45],lowerReturn:{unit:tracking.id,stage:previousStage},victory:{waves:won.wave,kills:won.kills,lives:won.lives},defeat:{leaks:lost.leaks,lives:lost.lives}});
    await writeFile(resolve(output,mode.name+'-receipt.json'),JSON.stringify(receipts.at(-1),null,2));console.log(mode.name==='desktop'?'MAUL_LAYOUT_DESKTOP_PASS':'MAUL_LAYOUT_MOBILE_PASS');
  }catch(error){await page.screenshot({path:resolve(output,mode.name+'-failure.png')}).catch(()=>{});await writeFile(resolve(output,mode.name+'-failure.json'),JSON.stringify({message:String(error),cases,errors,state:await state(page).catch(()=>null),ui:await ui(page).catch(()=>null)},null,2));throw error;}
  finally{await context.close();}
}await writeFile(resolve(output,'receipt.json'),JSON.stringify(receipts,null,2));console.log('MAUL_LAYOUT_ALL_VIEWPORTS_PASS');}
finally{await browser.close();}
