import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {mkdir,readFile,writeFile} from 'node:fs/promises';
import {resolve} from 'node:path';

// The fixtures are ordinary native editor projects, imported only while stopped.
// Real mouse/touch input drives the native Play session. The controlled RAF clock
// advances the engine, including movement and collision; no match state is edited.
const base=(process.env.SWYRL_ANIME_TEST_URL||'http://127.0.0.1:8765').replace(/\/$/,'');
const query=new URLSearchParams(process.env.SWYRL_ANIME_TEST_QUERY||'');query.set('project','sheep-tag-meadow');
const output=resolve(process.env.SWYRL_ANIME_SCREENSHOTS_DIR||'sheep-touch-acceptance');await mkdir(output,{recursive:true});
const modes=[{name:'desktop',viewport:{width:1440,height:900},isMobile:false,hasTouch:false},
  {name:'mobile',viewport:{width:390,height:844},isMobile:true,hasTouch:true}]
  .filter(mode=>!process.env.SWYRL_ANIME_TEST_MODE||process.env.SWYRL_ANIME_TEST_MODE===mode.name);
assert.ok(modes.length,'Choose desktop or mobile');
const browser=await chromium.launch({headless:true,
  ...(process.env.SWYRL_CHROMIUM_PATH?{executablePath:process.env.SWYRL_CHROMIUM_PATH}:{}),
  args:['--no-sandbox','--disable-dev-shm-usage','--enable-webgl','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader']});
const receipts=[],touchPages=new WeakSet(),touchSessions=new WeakMap();
const state=page=>page.evaluate(()=>window.SWYRL_ENGINE_SHEEP_TAG.status());
const view=page=>page.evaluate(()=>window.SWYRL_ENGINE_SHEEP_TAG.viewStatus());
const ui=page=>page.evaluate(()=>window.SWYRL_ENGINE_SHEEP_TAG.uiStatus());
const saved=page=>page.evaluate(()=>window.SWYRL_ENGINE_AGENT.inspectScene());
const frames=(page,count=1,ms=50)=>page.evaluate(({count,ms})=>window.__sheepTouchClock.step(count,ms),{count,ms});
const authored=data=>({project:data.project,layers:data.editor.layers,background:data.scene.background,actors:data.scene.actors,paths:data.scene.paths});
const controlled=s=>s.units.find(unit=>unit.id===s.controlledId);
const distance=(a,b)=>Math.hypot(a[0]-b[0],a.at(-1)-b.at(-1));
const close=(actual,expected,label,tolerance=1e-4)=>assert.ok(Number.isFinite(actual)&&Math.abs(actual-expected)<=tolerance,
  label+': expected '+expected+', received '+actual);
async function tap(page,id){const node=page.locator('#'+id);assert.equal(await node.isVisible(),true,'Hidden required control '+id);
  if(touchPages.has(page))await node.tap({force:true});else await node.click({force:true});}
async function native(page,id){await tap(page,id);await frames(page,2);}
async function stop(page){if((await state(page)).active){await native(page,'stStop');assert.equal((await state(page)).active,false);}}
async function focus(page,pos){await page.evaluate(pos=>window.SWYRL_ENGINE_SHEEP_TAG.focus(pos),pos);await frames(page,1);}
async function until(page,predicate,label,max=180){let s=await state(page);for(let i=0;i<max&&!predicate(s);i+=4){await frames(page,Math.min(4,max-i));s=await state(page);}
  assert.ok(predicate(s),label+' did not occur in the actual match: '+JSON.stringify(s));return s;}
async function point(page,x,z,y=0){const p=await page.evaluate(({x,z,y})=>window.SWYRL_ENGINE_SHEEP_TAG.pointScreen(x,z,y),{x,z,y});
  assert.ok(p?.visible,'World input is outside the visible canvas: '+JSON.stringify({x,z,y,screen:p}));
  assert.equal(await page.evaluate(p=>{const n=document.elementFromPoint(p.x,p.y);return n?.tagName==='CANVAS'||n?.id==='viewport';},p),true,
    'World input hits an editor/HUD panel: '+JSON.stringify(p));return p;}
async function screenTap(page,p){if(touchPages.has(page))await page.touchscreen.tap(p.x,p.y);else await page.mouse.click(p.x,p.y);await frames(page,1);}
async function worldTap(page,x,z,y=0){await screenTap(page,await point(page,x,z,y));}
async function houseTap(page,id){const building=(await view(page)).buildings.find(b=>b.id===id);assert.ok(building,'Building must be visible to the player before tapping');
  await worldTap(page,building.pos[0],building.pos[2],1);}
async function previewAt(page,x,z){const p=await point(page,x,z);if(touchPages.has(page)){
    const session=touchSessions.get(page);await session.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:p.x,y:p.y,radiusX:2,radiusY:2,force:1,id:0}]});
    // Actual touch cancellation updates the visible guide without committing a
    // building. It also exercises the browser's pointercancel cleanup path.
    await session.send('Input.dispatchTouchEvent',{type:'touchCancel',touchPoints:[]});
  }else await page.mouse.move(p.x,p.y);await frames(page,1);return (await ui(page)).placementGrid;}
async function drag(page,p){if(touchPages.has(page)){
    const session=touchSessions.get(page);await session.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:p.x,y:p.y,radiusX:2,radiusY:2,force:1,id:0}]});
    await session.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x:p.x+28,y:p.y-18,radiusX:2,radiusY:2,force:1,id:0}]});
    await session.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
  }else{await page.mouse.move(p.x,p.y);await page.mouse.down();await page.mouse.move(p.x+28,p.y-18,{steps:3});await page.mouse.up();}
  await frames(page,1);}
async function installClock(context){await context.addInitScript(()=>{
  const nativeRAF=requestAnimationFrame.bind(window),nativeCancel=cancelAnimationFrame.bind(window),nativeNow=performance.now.bind(performance),queue=new Map();
  let frozen=false,now=0,next=1000000000;Object.defineProperty(performance,'now',{configurable:true,value:()=>frozen?now:nativeNow()});
  window.requestAnimationFrame=callback=>{if(!frozen)return nativeRAF(callback);const id=next++;queue.set(id,callback);return id;};
  window.cancelAnimationFrame=id=>{queue.delete(id);nativeCancel(id);};
  window.__sheepTouchClock={freeze:()=>{frozen=true;now=nativeNow();return new Promise(resolve=>nativeRAF(()=>nativeRAF(resolve)));},
    step:(count,ms)=>{if(!frozen)throw Error('Clock is not frozen');for(let i=0;i<count;i++){now+=ms;const pending=[...queue.values()];queue.clear();
      if(!pending.length)throw Error('Real engine RAF stopped');for(const callback of pending)callback(now);}return {now,pending:queue.size};}};
});}
async function models(page,canonical){const result=await page.evaluate(()=>{
  const pieces={};for(const type of ['st-farm','st-income','st-wall','st-ramp']){
    const id=window.SWYRL_ENGINE_AGENT.spawn(type,{position:[-35,0,-35],name:'Touch acceptance '+type});window.SWYRL_ENGINE_AGENT.bake();
    pieces[type]=window.SWYRL_ENGINE_AGENT.inspectScene().scene.actors.find(a=>a.id===id);
  }return pieces;});for(const [kind,actor]of Object.entries(result))assert.equal(actor?.type,kind,'Missing native prefab '+kind);
  await page.evaluate(data=>window.SWYRL_ENGINE_AGENT.loadScene(data),canonical);await frames(page,1);return result;}
function fixture(canonical,prototypes,options={}){
  const data=structuredClone(canonical),first=type=>canonical.scene.actors.find(a=>a.type===type);
  const piece=(type,pos,id,extra={})=>({...structuredClone(prototypes[type]||first(type)),id,name:'Touch '+id,type,position:[...pos],rotation:[0,0,0],scale:[1,1,1],baked:true,visible:true,...extra});
  data.scene.actors=[piece('st-meadow',[0,0,0],'touch-meadow'),piece('st-pen',[0,0,0],'touch-pen'),
    piece('st-sheep',options.sheep||[-16.5,0,-23],'touch-sheep'),piece('st-wolf',options.wolf||[28,0,28],'touch-wolf'),
    ...(options.pieces||[{type:'st-farm',pos:[-18,0,-18]},{type:'st-income',pos:[-15,0,-18]}]).map((spec,i)=>
      piece(spec.type,spec.pos,'touch-building-'+i,{...(spec.rotation?{rotation:spec.rotation}:{}),...(spec.scale?{scale:spec.scale}:{})}))];
  data.project.sheepTag={...canonical.project.sheepTag,preset:'classic',duration:300,headstart:120,bounds:40,startGold:500,role:'sheep',buildSnap:.15,
    fogMode:'off',thorns:false,totems:false,elevated:false,split:false,events:false,seed:731,...options.rules};return data;
}
async function load(page,data){await stop(page);await page.evaluate(data=>window.SWYRL_ENGINE_AGENT.loadScene(data),data);await frames(page,2);
  assert.deepEqual(authored(await saved(page)),authored(data),'Stopped native import changed fixture');await native(page,'playBtn');
  assert.equal((await state(page)).active,true,'Native Play rejected fixture: '+JSON.stringify(await page.evaluate(()=>window.SWYRL_ENGINE_SHEEP_TAG.validateStarts())));
  await focus(page,[-16.5,0,-18]);}
async function assertSheepSelected(page,label){const s=await state(page);assert.equal(s.selectedId,s.controlledId,label);return s;}
async function visibleSite(page,kind){const s=await view(page),sheep=controlled(s),sites=[];
  for(const [dx,dz]of [[-3,-3],[3,-3],[-6,0],[6,0],[0,-6],[-6,-3],[6,-3],[0,6]]){
    const fit=await page.evaluate(({kind,x,z})=>window.SWYRL_ENGINE_SHEEP_TAG.canBuild(kind,x,z),{kind,x:sheep.pos[0]+dx,z:sheep.pos[2]+dz});
    if(!fit.ok)continue;const p=await page.evaluate(({x,z})=>window.SWYRL_ENGINE_SHEEP_TAG.pointScreen(x,z),fit);
    const canvas=await page.evaluate(p=>{const n=document.elementFromPoint(p.x,p.y);return n?.tagName==='CANVAS'||n?.id==='viewport';},p);
    if(p.visible&&canvas)sites.push(fit);
  }assert.ok(sites.length,'No visible legal site after opening the placement controls');return sites[0];}
function guideGeometry(guide,label){assert.ok(guide?.visible,label+' has no visible ground guide');assert.ok(guide.fillVertices>=6,label+' has no filled footprint');
  assert.ok(guide.boundaryVertices>=4,label+' has no footprint boundary');assert.ok(guide.gridVertices>=4,label+' has no placement grid');
  assert.equal(guide.terrainConforming,true,label+' does not follow the ground');assert.equal(guide.corners.length,4,label+' does not describe four actual footprint corners');
  assert.ok(guide.objects.length>=3,label+' is missing actual scene objects');for(const object of guide.objects){assert.equal(object.parented,true,label+' helper is detached: '+object.name);
    assert.equal(object.visible,true,label+' helper is hidden: '+object.name);assert.ok(object.vertices>0,label+' helper has no geometry: '+object.name);
    assert.equal(object.transparent,true,label+' helper is opaque: '+object.name);assert.equal(object.depthWrite,false,label+' helper hides the ground: '+object.name);}
}
function extents(corners){return [Math.max(...corners.map(c=>c[0]))-Math.min(...corners.map(c=>c[0])),Math.max(...corners.map(c=>c[1]))-Math.min(...corners.map(c=>c[1]))];}
function edgeLengths(corners){return corners.map((corner,i)=>distance(corner,corners[(i+1)%corners.length])).sort((a,b)=>a-b);}
async function nativeExport(page,mode){const pending=page.waitForEvent('download',{timeout:15000});
  if(mode.hasTouch){await tap(page,'sheepTagRulesBtn');await tap(page,'stRulesSave');}else await tap(page,'saveBtn');
  const download=await pending,data=JSON.parse(await readFile(await download.path(),'utf8'));if(mode.hasTouch)await tap(page,'stRulesClose');return data;}

try{for(const mode of modes){const context=await browser.newContext({viewport:mode.viewport,isMobile:mode.isMobile,hasTouch:mode.hasTouch});await installClock(context);
  const page=await context.newPage(),errors=[],cases=[];if(mode.hasTouch){touchPages.add(page);touchSessions.set(page,await context.newCDPSession(page));}
  page.on('pageerror',error=>errors.push(String(error)));page.setDefaultTimeout(30000);
  const pass=name=>{cases.push(name);console.log('SHEEP_TOUCH_CASE_PASSED',mode.name,name);};
  await page.goto(base+'/index.html?'+query,{waitUntil:'domcontentloaded',timeout:60000});
  await page.waitForFunction(()=>window.SWYRL_ENGINE_SHEEP_TAG?.uiStatus&&window.SWYRL_ENGINE_AGENT.project().canonicalId==='sheep-tag-meadow',undefined,{timeout:60000});
  await page.locator('#perfPreset').selectOption('medium',{force:true});await page.evaluate(()=>window.__sheepTouchClock.freeze());await frames(page,2);
  assert.equal(await page.evaluate(()=>window.SWRLZ_FORGE_BUILD?.version),'v10.2','Wrong engine release');
  const canonical=await saved(page),prototypes=await models(page,canonical),houses=fixture(canonical,prototypes);

  await load(page,houses);let s=await state(page);const a='touch-building-0',b='touch-building-1';
  assert.equal((await ui(page)).buildingSelection.mode,'double-tap');
  await houseTap(page,a);s=await assertSheepSelected(page,'A single building tap selected a house instead of the sheep');
  let selection=(await ui(page)).buildingSelection;assert.equal(selection.pendingId,a,'The visible house was not picked for a possible second tap');
  assert.equal(selection.lastPick.buildingId,a,'Single tap did not intersect the visible building mesh');
  assert.equal(selection.lastMove.ok,true,'Single building tap failed to issue an accessible ground movement');
  assert.ok(selection.lastMove.destination,'Single tap has no actual ground destination');
  const approach=await page.evaluate(({from,to})=>window.SWYRL_ENGINE_SHEEP_TAG.previewPath({from,to,species:'sheep'}),
    {from:controlled(s).pos,to:selection.lastMove.destination});assert.equal(approach.reachable,true,'Single tap sent the sheep into an occupied footprint');
  assert.equal(await page.locator('#stUpgrade').isEnabled(),false,'Single tap opened house management');pass('single_building_tap_keeps_sheep_and_uses_accessible_ground');

  // The .6-unit lane fits a sheep, while both house centers are close enough
  // in screen space for the previous phone proximity picker to swallow it.
  await worldTap(page,-16.5,-18);s=await assertSheepSelected(page,'Tapping the clear house gap inspected a building');
  assert.equal((await ui(page)).buildingSelection.pendingId,null,'A clear gap created a pending house selection');
  assert.equal(controlled(s).order?.action,'move','The clear house gap did not receive a real movement order');
  s=await until(page,s=>distance(controlled(s).pos,[-16.5,0,-18])<.25,'Sheep movement through the actual house gap');
  pass('clear_house_gap_tap_moves_through_without_proximity_selection');

  await tap(page,'stSelectMine');await houseTap(page,a);await houseTap(page,a);s=await state(page);
  assert.equal(s.selectedId,a,'Two taps on the same building did not select it');assert.equal((await ui(page)).buildingSelection.pendingId,null);
  assert.equal(await page.locator('#stUpgrade').isEnabled(),true,'Double-selected owned house cannot be managed');
  await worldTap(page,-16.5,-22);s=await assertSheepSelected(page,'Ground tap after house inspection did not restore sheep selection');
  assert.equal(controlled(s).order?.action,'move');assert.equal(await page.locator('#stUpgrade').isEnabled(),false);pass('same_house_double_tap_selects_and_ground_tap_returns_to_sheep');

  await tap(page,'stSelectMine');await houseTap(page,a);await houseTap(page,b);await assertSheepSelected(page,'Different houses were counted as a double tap');
  assert.equal((await ui(page)).buildingSelection.pendingId,b);await houseTap(page,b);assert.equal((await state(page)).selectedId,b);
  await tap(page,'stSelectMine');await houseTap(page,a);const windowMs=(await ui(page)).buildingSelection.windowMs;
  await frames(page,Math.ceil(windowMs/50)+1);await houseTap(page,a);await assertSheepSelected(page,'Expired taps selected a house');
  assert.equal((await ui(page)).buildingSelection.pendingId,a);pass('different_house_and_expired_tap_do_not_select');

  // Start a drag from a visible mesh, then tap that same house again. The drag
  // must break the pending pair rather than counting as a fast second tap.
  await tap(page,'stSelectMine');await houseTap(page,a);const house=(await view(page)).buildings.find(v=>v.id===a);
  await drag(page,await point(page,house.pos[0],house.pos[2],1));assert.equal((await ui(page)).buildingSelection.pendingId,null,'Camera drag preserved a pending house tap');
  await houseTap(page,a);await assertSheepSelected(page,'Tap after a camera drag counted as the second tap');
  await tap(page,'stPause');assert.equal((await ui(page)).buildingSelection.pendingId,null,'Pause preserved a pending building tap');
  await tap(page,'stPause');await frames(page,1);await houseTap(page,a);await assertSheepSelected(page,'Tap after Pause/resume counted as the second tap');
  await tap(page,'stSelectMine');assert.equal((await ui(page)).buildingSelection.pendingId,null,'A HUD control preserved the pending house tap');
  pass('real_camera_drag_pause_and_hud_control_reset_double_tap');await page.screenshot({path:resolve(output,mode.name+'-house-gap-controls.png')});
  await stop(page);assert.deepEqual(authored(await saved(page)),authored(houses),'Movement and house inspection changed the saved map');

  const hunter=fixture(canonical,prototypes,{sheep:[-30,0,-30],wolf:[-18,0,-23],pieces:[{type:'st-farm',pos:[-18,0,-18]}],
    rules:{role:'wolf',headstart:0,wolfVision:40,wolfDamage:45}});await load(page,hunter);await houseTap(page,a);s=await state(page);
  assert.equal(s.role,'wolf');assert.equal(s.selectedId,s.controlledId,'Single-tap attack deselected the wolf');
  assert.deepEqual(controlled(s).order,{action:'attack',id:a},'Wolf single-tap demolition order changed');
  s=await until(page,s=>s.buildings.find(v=>v.id===a)?.hp<s.buildings.find(v=>v.id===a)?.maxHp,'Actual wolf demolition after one tap');
  pass('wolf_single_tap_still_orders_and_damages_house');await stop(page);

  const ground=fixture(canonical,prototypes,{sheep:[-18,0,-21],pieces:[{type:'st-farm',pos:[-18,0,-18]}],rules:{elevated:true}});
  await load(page,ground);const beforePreview=authored(await saved(page));
  // No mousemove or canvas touch occurs between native Play and this control.
  await tap(page,'stBuildFarm');await frames(page,1);let guide=(await ui(page)).placementGrid;
  guideGeometry(guide,'Immediate '+mode.name+' house preview');assert.equal(guide.kind,'st-farm');
  const size=extents(guide.corners);close(size[0],2.4,'Actual house footprint width');close(size[1],2.4,'Actual house footprint depth');
  assert.ok(await page.locator('#stPlacement').innerText(),'Placement mode gives no visible status');
  pass('ground_grid_and_full_house_footprint_visible_without_hover');

  const site=await visibleSite(page,'st-farm');guide=await previewAt(page,site.x,site.z);guideGeometry(guide,'Legal house site');
  assert.equal(guide.valid,true);assert.equal(guide.fillColor,'96ffd0','Clear ground footprint is not green');
  const legalColor=guide.fillColor;const legalBoundaryColor=guide.boundaryColor;
  guide=await previewAt(page,-18,-18);guideGeometry(guide,'Blocked house site');assert.equal(guide.valid,false);assert.equal(guide.fillColor,'ff7777','Occupied footprint is not red');
  assert.notEqual(guide.fillColor,legalColor,'Blocked footprint has the same fill tint as clear ground');
  assert.notEqual(guide.boundaryColor,legalBoundaryColor,'Blocked boundary has the same tint as clear ground');
  assert.match(await page.locator('#stPlacement').innerText(),/occup|block|space/i,'Blocked site does not explain the occupied footprint');
  await page.screenshot({path:resolve(output,mode.name+'-blocked-placement-grid.png')});
  const beforeRejected=(await state(page)).buildings.length;await worldTap(page,-18,-18);
  assert.equal((await state(page)).buildings.length,beforeRejected,'Red occupied footprint still placed a house');
  assert.equal((await ui(page)).placementGrid.valid,false,'Rejected placement hid the visible boundaries');
  pass('actual_valid_and_blocked_ground_geometry_tints_and_rejection');

  guide=await previewAt(page,site.x+.07,site.z+.07);close(guide.snap,.15,'Fine build snap');
  for(const coordinate of guide.center)close(coordinate/.15,Math.round(coordinate/.15),'Fine preview center grid alignment',1e-3);
  const fineStep=guide.gridStep;await tap(page,'stPlacementSnap');await frames(page,1);guide=(await ui(page)).placementGrid;
  close(guide.snap,3,'Coarse build snap');assert.ok(guide.gridStep>fineStep,'Coarse snap did not update the rendered grid spacing');
  for(const coordinate of guide.center)close(coordinate/3,Math.round(coordinate/3),'Coarse preview center grid alignment');
  await tap(page,'stPlacementSnap');await frames(page,1);close((await ui(page)).placementGrid.snap,.15,'Fine snap restored');
  await tap(page,'stCancelBuild');await frames(page,1);assert.equal((await ui(page)).placementGrid,null,'Cancel left guide geometry active');
  assert.equal((await ui(page)).placementGridResources.live,0,'Cancel retained placement resources');
  assert.deepEqual(authored(await saved(page)),beforePreview,'Transient placement guide was serialized into the native scene');pass('fine_coarse_rendered_grid_snap_and_cancel_disposal');

  for(const [button,kind]of [['stBuildWall','st-wall'],['stBuildRamp','st-ramp']]){
    await tap(page,button);await frames(page,1);guide=(await ui(page)).placementGrid;guideGeometry(guide,'Immediate '+kind+' preview');
    const lengths=edgeLengths(guide.corners);close(lengths[0],2.4,kind+' short footprint edge');close(lengths[1],2.4,kind+' second short edge');
    close(lengths[2],6,kind+' long footprint edge');close(lengths[3],6,kind+' second long edge');const oldExtents=extents(guide.corners);
    await tap(page,'stRotatePlacement');await frames(page,1);guide=(await ui(page)).placementGrid;guideGeometry(guide,'Rotated '+kind+' preview');
    const newExtents=extents(guide.corners);close(newExtents[0],oldExtents[1],kind+' rotated world width');close(newExtents[1],oldExtents[0],kind+' rotated world depth');
    await page.screenshot({path:resolve(output,mode.name+'-'+kind+'-rotated-grid.png')});await tap(page,'stCancelBuild');await frames(page,1);
    assert.equal((await ui(page)).placementGridResources.live,0,kind+' cancellation leaked the guide');
  }pass('wall_and_ramp_full_six_unit_footprints_rotate_with_preview');

  await tap(page,'stBuildFarm');await frames(page,1);const buildSite=await visibleSite(page,'st-farm');await worldTap(page,buildSite.x,buildSite.z);
  assert.equal((await ui(page)).build,null,'Successful construction left build mode active');assert.equal((await ui(page)).placementGrid,null,'Placed house retained its guide');
  assert.equal((await ui(page)).placementGridResources.live,0,'Successful placement leaked guide geometry');
  await until(page,s=>s.buildings.some(v=>v.id!=='touch-building-0'),'Actual house construction from the visible ground grid');
  await tap(page,'stBuildFarm');await frames(page,1);guideGeometry((await ui(page)).placementGrid,'Second construction preview');
  await stop(page);const ended=await ui(page);assert.equal(ended.placementGrid,null,'Stop left placement guide active');
  assert.equal(ended.placementGridResources.live,0,'Stop leaked placement resources');assert.equal(ended.placementGridResources.created,ended.placementGridResources.disposed,'A guide allocation was not disposed');
  assert.deepEqual(authored(await saved(page)),authored(ground),'Stop saved runtime houses or preview helpers');
  const exported=await nativeExport(page,mode);assert.deepEqual(authored(exported),authored(ground),'Native project export saved temporary grid geometry or placement rules');
  const portable=await page.evaluate(()=>window.SWYRL_ENGINE_SHEEP_TAG_CREATOR.exportMap());assert.equal(portable.ok,true);
  assert.equal(portable.map.actors.length,ground.scene.actors.length,'Portable map export included temporary helpers');
  assert.ok(portable.map.actors.every(actor=>!/(preview|footprint|grid)/i.test(actor.name)),'Portable export contains a placement helper');
  pass('placement_and_stop_dispose_helpers_and_exports_preserve_authored_scene');

  await page.evaluate(data=>window.SWYRL_ENGINE_AGENT.loadScene(data),canonical);await frames(page,2);
  assert.deepEqual(authored(await saved(page)),authored(canonical),'Final native starter restoration failed');
  assert.deepEqual(errors,[],'Unhandled browser errors: '+errors.join('\n'));
  receipts.push({mode:mode.name,cases,pass:true});console.log('SHEEP_TOUCH_'+mode.name.toUpperCase()+'_PASS');await context.close();
}
await writeFile(resolve(output,'receipt.json'),JSON.stringify({pass:true,viewports:receipts},null,2));console.log('SHEEP_TOUCH_ALL_VIEWPORTS_PASS');
}finally{await browser.close();}
