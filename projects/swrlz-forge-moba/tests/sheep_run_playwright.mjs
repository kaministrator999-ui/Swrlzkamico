import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {mkdir,readFile,writeFile} from 'node:fs/promises';
import {resolve} from 'node:path';
import {pathToFileURL} from 'node:url';

// Fixtures are ordinary native editor projects and are imported only while
// stopped. Mouse / real phone touch drive Play, movement and construction. The
// controlled RAF clock is the existing touch suite's clock: it advances the
// actual engine without editing match state, AI, economy or render functions.
const base=(process.env.SWYRL_ANIME_TEST_URL||'http://127.0.0.1:8765').replace(/\/$/,'');
const query=new URLSearchParams(process.env.SWYRL_ANIME_TEST_QUERY||'');query.set('project','sheep-tag-meadow');
const output=resolve(process.env.SWYRL_ANIME_SCREENSHOTS_DIR||'sheep-run-acceptance');await mkdir(output,{recursive:true});
const modes=[{name:'desktop',viewport:{width:1440,height:900},isMobile:false,hasTouch:false},
  {name:'mobile',viewport:{width:390,height:844},isMobile:true,hasTouch:true}]
  .filter(mode=>!process.env.SWYRL_ANIME_TEST_MODE||process.env.SWYRL_ANIME_TEST_MODE===mode.name);
assert.ok(modes.length,'SWYRL_ANIME_TEST_MODE must be desktop or mobile');
const browser=await chromium.launch({headless:true,
  ...(process.env.SWYRL_CHROMIUM_PATH?{executablePath:process.env.SWYRL_CHROMIUM_PATH}:{}),
  args:['--no-sandbox','--disable-dev-shm-usage','--enable-webgl','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader']});
const touchPages=new WeakSet(),receipts=[];
const state=page=>page.evaluate(()=>window.SWYRL_ENGINE_SHEEP_TAG.status());
const saved=page=>page.evaluate(()=>window.SWYRL_ENGINE_AGENT.inspectScene());
const runStatus=page=>page.evaluate(()=>window.SWYRL_ENGINE_SHEEP_TAG_RUNS.status());
const runData=(page,id=null)=>page.evaluate(id=>window.SWYRL_ENGINE_SHEEP_TAG_RUNS.data(id),id);
const runFrame=(page,run,t)=>page.evaluate(({run,t})=>window.SWYRL_ENGINE_SHEEP_TAG_RUNS.frame(run,t),{run,t});
const frames=(page,count=1,ms=50)=>page.evaluate(({count,ms})=>window.__sheepRunClock.step(count,ms),{count,ms});
const authored=data=>({project:data.project,layers:data.editor.layers,background:data.scene.background,actors:data.scene.actors,paths:data.scene.paths});
const controlled=s=>s.units.find(unit=>unit.id===s.controlledId);
const distance=(a,b)=>Math.hypot(a[0]-b[0],a[2]-b[2]);
const close=(actual,expected,label,tolerance=1e-5)=>assert.ok(Number.isFinite(actual)&&Math.abs(actual-expected)<=tolerance,
  label+': expected '+expected+', received '+actual);
const closeArray=(actual,expected,label,tolerance=1e-5)=>{assert.equal(actual?.length,expected.length,label+' length');
  expected.forEach((value,i)=>close(actual[i],value,label+'['+i+']',tolerance));};
function equivalent(actual,expected,label){if(typeof expected==='number'){close(actual,expected,label);return;}
  if(expected&&typeof expected==='object'){assert.deepEqual(Object.keys(actual||{}).sort(),Object.keys(expected).sort(),label+' fields');
    for(const key of Object.keys(expected))equivalent(actual[key],expected[key],label+'.'+key);return;}assert.deepEqual(actual,expected,label);}
async function tap(page,id){const node=page.locator('#'+id);assert.equal(await node.isVisible(),true,'Hidden required control '+id);
  if(touchPages.has(page))await node.tap({force:true});else await node.click({force:true});}
async function native(page,id){if(['pauseBtn','stopBtn'].includes(id)&&await page.evaluate(()=>!!document.pointerLockElement)){await page.keyboard.press('Escape');if(await page.evaluate(()=>!!document.pointerLockElement))await page.evaluate(()=>document.exitPointerLock());}await tap(page,id);await frames(page,2);}
async function stop(page){if((await state(page)).active){await native(page,'stStop');assert.equal((await state(page)).active,false);}}
async function focus(page,pos){await page.evaluate(pos=>window.SWYRL_ENGINE_SHEEP_TAG.focus(pos),pos);await frames(page,1);}
async function until(page,predicate,label,max=200){let s=await state(page);for(let i=0;i<max&&!predicate(s);i+=4){await frames(page,Math.min(4,max-i));s=await state(page);}
  assert.ok(predicate(s),label+' did not occur in actual Play: '+JSON.stringify(s));return s;}
async function worldTap(page,x,z,y=0){const p=await page.evaluate(({x,z,y})=>window.SWYRL_ENGINE_SHEEP_TAG.pointScreen(x,z,y),{x,z,y});
  assert.ok(p?.visible,'World input is outside the visible canvas: '+JSON.stringify({x,z,y,p}));
  if(touchPages.has(page)&&(await page.evaluate(()=>window.SWYRL_ENGINE_SHEEP_TAG.uiStatus().build)))p.y+=64;
  assert.equal(await page.evaluate(p=>{const n=document.elementFromPoint(p.x,p.y);return n?.tagName==='CANVAS'||n?.id==='viewport';},p),true,
    'Physical world input hits an editor/HUD control: '+JSON.stringify(p));
  if(touchPages.has(page))await page.touchscreen.tap(p.x,p.y);else await page.mouse.click(p.x,p.y);await frames(page,1);}
async function installClock(context){await context.addInitScript(()=>{
  const nativeRAF=requestAnimationFrame.bind(window),nativeCancel=cancelAnimationFrame.bind(window),nativeNow=performance.now.bind(performance),queue=new Map();
  let frozen=false,now=0,next=1000000000;Object.defineProperty(performance,'now',{configurable:true,value:()=>frozen?now:nativeNow()});
  window.requestAnimationFrame=callback=>{if(!frozen)return nativeRAF(callback);const id=next++;queue.set(id,callback);return id;};
  window.cancelAnimationFrame=id=>{queue.delete(id);nativeCancel(id);};
  window.__sheepRunClock={freeze:()=>{frozen=true;now=nativeNow();return new Promise(resolve=>nativeRAF(()=>nativeRAF(resolve)));},
    step:(count,ms)=>{if(!frozen)throw Error('Clock is not frozen');for(let i=0;i<count;i++){now+=ms;const pending=[...queue.values()];queue.clear();
      if(!pending.length)throw Error('Real engine RAF stopped');for(const callback of pending)callback(now);}return {now,pending:queue.size};}};
});}
async function prototypes(page,canonical){const pieces=await page.evaluate(()=>{
  const result={};for(const type of ['st-farm','st-income','st-fort','st-wall','st-ramp']){
    const id=window.SWYRL_ENGINE_AGENT.spawn(type,{position:[-35,0,-35],name:'Run acceptance '+type});window.SWYRL_ENGINE_AGENT.bake();
    result[type]=window.SWYRL_ENGINE_AGENT.inspectScene().scene.actors.find(a=>a.id===id);
  }return result;});for(const [type,actor]of Object.entries(pieces))assert.equal(actor?.type,type,'Missing native prefab '+type);
  await page.evaluate(data=>window.SWYRL_ENGINE_AGENT.loadScene(data),canonical);await frames(page,1);return pieces;}
const escapedName='Run <script>window.__runNameExecuted=true</script> & sheep';
function fixture(canonical,pieces,options={}){const data=structuredClone(canonical),first=type=>canonical.scene.actors.find(actor=>actor.type===type);
  const piece=(type,pos,id,extra={})=>({...structuredClone(pieces[type]||first(type)),id,name:'Run '+id,type,position:[...pos],rotation:[0,0,0],scale:[1,1,1],baked:true,visible:true,...extra});
  data.scene.actors=[piece('st-meadow',[0,0,0],'run-meadow'),piece('st-pen',[0,0,0],'run-pen'),
    piece('st-sheep',options.sheep||[-18.85,0,-18],'run-sheep',{name:escapedName}),piece('st-wolf',options.wolf||[28,0,28],'run-wolf'),
    ...(options.extraSheep||[]).map((pos,i)=>piece('st-sheep',pos,'run-teammate-'+i)),
    ...(options.buildings||[]).map((spec,i)=>piece(spec.type,spec.pos,'run-building-'+i))];
  data.project.sheepTag={...canonical.project.sheepTag,preset:'classic',duration:300,headstart:120,bounds:40,startGold:500,role:'sheep',buildSnap:.15,
    fogMode:'team',thorns:false,totems:false,elevated:false,split:false,events:false,seed:731,...options.rules};return data;
}
async function importFixture(page,data){await stop(page);await page.evaluate(data=>window.SWYRL_ENGINE_AGENT.loadScene(data),data);await frames(page,2);
  assert.deepEqual(authored(await saved(page)),authored(data),'Stopped native import changed fixture');}
async function play(page){await native(page,'playBtn');assert.equal((await state(page)).active,true,
  'Native Play rejected the fixture: '+JSON.stringify(await page.evaluate(()=>window.SWYRL_ENGINE_SHEEP_TAG.validateStarts())));}
async function openPanel(page){await native(page,'stRunLauncher');try{await page.locator('#stRunPanel').waitFor({state:'visible'});}catch(error){console.log('RUN_PANEL_INPUT_FAILURE',await page.evaluate(()=>{const n=document.getElementById('stRunLauncher'),r=n.getBoundingClientRect();return {project:SWYRL_ENGINE_AGENT.project().name,status:SWYRL_ENGINE_RUNS.status(),rect:r.toJSON(),hit:document.elementFromPoint(r.x+r.width/2,r.y+r.height/2)?.outerHTML.slice(0,180),lock:!!document.pointerLockElement};}));await page.screenshot({path:resolve(output,'failed-open-panel.png')});throw error;}}
async function settings(page,enabled,cadence='full'){await openPanel(page);assert.equal(await page.locator('#stRunEnabled').getAttribute('type'),'checkbox');
  if((await page.locator('#stRunEnabled').isChecked())!==enabled)await tap(page,'stRunEnabled');
  await page.locator('#stRunCadence').selectOption(cadence,{force:true});await frames(page,1);
  assert.equal((await runStatus(page)).settings.enabled,enabled);await native(page,'stRunClose');}
async function nativeExport(page,mode){const pending=page.waitForEvent('download',{timeout:15000});
  if(mode.hasTouch){await tap(page,'sheepTagRulesBtn');await tap(page,'stRulesSave');}else await tap(page,'saveBtn');
  const data=JSON.parse(await readFile(await (await pending).path(),'utf8'));if(mode.hasTouch)await tap(page,'stRulesClose');return data;}
async function download(page,id,path){const pending=page.waitForEvent('download',{timeout:15000});await tap(page,id);const file=await pending;
  await file.saveAs(path);return {name:file.suggestedFilename(),text:await readFile(path,'utf8'),path};}
function reconstructed(run,t,count=run.frames.length){const result=structuredClone(run.initial);for(const frame of run.frames.slice(0,count)){if(frame.t>t+1e-8)break;
  for(const [id,patch]of Object.entries(frame.patch)){if(patch===null)delete result.entities[id];else result.entities[id]={...(result.entities[id]||{}),...structuredClone(patch)};}
  if(frame.camera)result.camera=structuredClone(frame.camera);if(frame.game)Object.assign(result.game,structuredClone(frame.game));
}return result;}
function schema(run){assert.equal(run.schema,'swyrl-editor-play-run-v1');assert.equal(typeof run.id,'string');assert.ok(run.id);
  assert.ok(Number.isFinite(Date.parse(run.startedAt)),'Run needs an ISO startedAt');assert.ok(Number.isFinite(run.duration)&&run.duration>=0);
  assert.ok(run.initial?.entities&&run.initial.camera&&run.initial.game,'Initial state omits entities/camera/game');
  assert.ok(Array.isArray(run.frames)&&run.frames.length>0,'No sampled frames');assert.ok(Array.isArray(run.checkpoints));
  assert.ok(Array.isArray(run.events));assert.ok(Array.isArray(run.observations));let tick=-1,t=-1;
  for(const frame of run.frames){assert.ok(Number.isInteger(frame.tick)&&frame.tick>=tick,'Ticks must be monotonic');assert.ok(frame.t>=t&&frame.t<=run.duration+1e-6,'Frame time is invalid');
    assert.ok(Number.isFinite(frame.dt)&&frame.dt>=0);assert.ok(frame.patch&&typeof frame.patch==='object');tick=frame.tick;t=frame.t;}
  for(const event of run.events){assert.ok(Number.isInteger(event.tick)&&Number.isFinite(event.t));assert.equal(typeof event.type,'string');assert.ok(event.details&&typeof event.details==='object');}
  assert.ok(run.observations.every(item=>Number.isFinite(item.t)&&typeof item.text==='string'));
  for(const checkpoint of run.checkpoints){assert.ok(Number.isInteger(checkpoint.index)&&Number.isFinite(checkpoint.t),'Checkpoint omits its frame index/time');
    const expected=reconstructed(run,checkpoint.t,checkpoint.index+1);assert.deepEqual(checkpoint.entities,expected.entities,'Checkpoint entities disagree with compact frame patches');
    assert.deepEqual(checkpoint.camera,expected.camera,'Checkpoint camera disagrees with compact frame patches');assert.deepEqual(checkpoint.game,expected.game,'Checkpoint game disagrees with compact frame patches');}
}
function assertWorld(snapshot,s,render){for(const unit of s.units){const entity=snapshot.entities[unit.id];assert.ok(entity,'Missing logged unit '+unit.id);
  closeArray(entity.position,unit.pos,'World position '+unit.id);assert.equal(entity.captured,unit.captured);equivalent(entity.order,unit.order,'Order '+unit.id);
  const visual=render.units.find(item=>item.id===unit.id);assert.ok(visual,'Missing real unit mesh '+unit.id);
  closeArray(entity.scale,visual.scale,'World scale '+unit.id);assert.equal(entity.appearance.meshCount,visual.meshCount);
  assert.equal(entity.playerVisible,visual.visible);assert.ok(entity.limbs&&Object.keys(entity.limbs).length>=6,'Missing four feet/head/tail transforms');}
  for(const building of s.buildings){const entity=snapshot.entities[building.id];assert.ok(entity,'Missing logged building '+building.id);
    closeArray(entity.position,building.pos,'Building world position');close(entity.hp,building.hp,'Building HP');close(entity.progress,building.progress,'Building progress');}
  assert.deepEqual(snapshot.game.resources,s.resources,'Logged economy differs from native economy');assert.equal(snapshot.game.winner,s.winner);
}
async function canvasData(page,id='stRunReviewCanvas'){return page.locator('#'+id).evaluate(canvas=>{
  const pixels=canvas.getContext('2d').getImageData(0,0,canvas.width,canvas.height).data,colors=new Set();
  for(let i=0;i<pixels.length;i+=Math.max(4,Math.floor(pixels.length/4000/4)*4))if(pixels[i+3])colors.add([pixels[i],pixels[i+1],pixels[i+2]].join(','));
  return {width:canvas.width,height:canvas.height,colors:colors.size,png:canvas.toDataURL()};});}
async function scrub(page,key){const slider=page.locator('#stRunTimeline');await slider.focus();await slider.press(key);await frames(page,1);
  return Number(await slider.inputValue());}
function parity(s){return {role:s.role,elapsed:s.elapsed,winner:s.winner,resources:s.resources,counts:s.counts,
  units:s.units.map(({id,kind,pos,captured,order,level,speed,damage,isIllusion,ai,concealment,onUpper,scentUntil,progression,traffic})=>
    ({id,kind,pos,captured,order,level,speed,damage,isIllusion,ai,concealment,onUpper,scentUntil,progression,traffic})),buildings:s.buildings};}

try{for(const mode of modes){const context=await browser.newContext({viewport:mode.viewport,isMobile:mode.isMobile,hasTouch:mode.hasTouch});await installClock(context);
  const page=await context.newPage(),errors=[],cases=[];if(mode.hasTouch)touchPages.add(page);
  page.on('pageerror',error=>errors.push(String(error)));page.setDefaultTimeout(30000);
  const pass=name=>{cases.push(name);console.log('SHEEP_RUN_CASE_PASSED',mode.name,name);};
  await page.goto(base+'/index.html?'+query,{waitUntil:'domcontentloaded',timeout:60000});
  await page.waitForFunction(()=>window.SWYRL_ENGINE_SHEEP_TAG_RUNS&&window.SWYRL_ENGINE_AGENT.project().canonicalId==='sheep-tag-meadow',undefined,{timeout:60000});
  await page.locator('#perfPreset').selectOption('medium',{force:true});await page.evaluate(()=>window.__sheepRunClock.freeze());await frames(page,2);
  assert.equal(await page.evaluate(()=>window.SWYRL_ENGINE_BUILD.version),'v11.62');const canonical=await saved(page);assert.equal(canonical.version,11.9);
  const sourceResponse=await context.request.get(base+'/SOURCE.json');assert.equal(sourceResponse.ok(),true);const source=await sourceResponse.json();
  assert.match(source.sourceVersion,/v11\.62/);assert.equal(source.patches.length,94);assert.equal(source.patches.at(-1),'patches/v11_62_mobile_adaptive.py');
  assert.equal(Object.keys(source.assets).length,43,'Unexpected bundled starter/media asset set');
  const htmlResponse=await context.request.get(base+'/index.html');assert.match(await htmlResponse.text(),/V11_62_MOBILE_ADAPTIVE_TOOL_SHEET/);
  assert.equal(canonical.scene.actors.length,92,'Archive map changed');const pieces=await prototypes(page,canonical),map=fixture(canonical,pieces);
  if(!process.env.SWYRL_RUN_GENERIC_ONLY){
  await openPanel(page);assert.equal(await page.locator('#stRunEnabled').isChecked(),false,'Logging must default off');
  assert.equal((await runStatus(page)).settings.enabled,false);await native(page,'stRunClose');pass('v10_9_source_native_starter_and_default_off_checkbox');

  await importFixture(page,map);await play(page);await focus(page,[-18,0,-10]);const beforeOff=await state(page);
  const originalRender=await page.evaluate(()=>window.SWYRL_ENGINE_SHEEP_TAG.renderStatus());await frames(page,25);await stop(page);
  assert.equal((await runStatus(page)).runs.length,0,'Disabled Play recorded a run');assert.equal(await runData(page),null);
  assert.deepEqual(authored(await saved(page)),authored(map),'Disabled Stop altered the map');
  assert.ok(beforeOff.units.length===2&&originalRender.units.every(unit=>unit.meshCount>0));pass('disabled_logging_creates_no_run_and_preserves_native_map');

  await settings(page,true,'full');const nativeMap=await nativeExport(page,mode);assert.deepEqual(authored(nativeMap),authored(map),'Run preferences leaked into Save Project');
  const portable=await page.evaluate(()=>window.SWYRL_ENGINE_SHEEP_TAG_CREATOR.exportMap());assert.equal(portable.ok,true);
  assert.ok(!JSON.stringify(nativeMap).includes('swyrl-editor-play-run-v1'),'Native save embedded a recording');
  assert.ok(!JSON.stringify(portable.map).includes('swyrl-editor-play-run-v1'),'Portable map embedded a recording');pass('editor_run_preferences_are_excluded_from_native_and_portable_maps');

  await play(page);await focus(page,[-18,0,-10]);let s=await state(page),active=await runData(page);schema(active);
  assert.equal(active.complete,false);assert.equal((await runStatus(page)).stateLocked,true);
  assert.equal(await page.locator('#stRunPanel').isVisible(),false,'Play exposed the review panel');
  assert.equal(await page.locator('#stRunBadge').isVisible(),true,'Recording badge is absent during Play');
  if(await page.locator('#stRunLauncher').isVisible())assert.equal(await page.locator('#stRunLauncher').isDisabled(),true,'Live review launcher is usable');
  assert.equal(await page.locator('#stRunReviewCanvas').isVisible(),false,'Play exposed an omniscient review canvas');
  assert.equal(await page.locator('#stRunNarrative').isVisible(),false,'Play exposed hidden-info narration');
  const view=await page.evaluate(()=>window.SWYRL_ENGINE_SHEEP_TAG.viewStatus());assert.ok(!view.units.some(unit=>unit.id==='run-wolf'),'Fixture must hide its remote wolf');
  const hidden=active.initial.entities['run-wolf'];assert.ok(hidden,'Full run lost the hidden actor');assert.equal(hidden.playerVisible,false);
  const locked=await page.evaluate(()=>window.SWYRL_ENGINE_SHEEP_TAG_RUNS.configure({enabled:false}));assert.equal(locked.ok,false,'Recording settings changed mid-Play');
  pass('play_locks_review_and_settings_and_keeps_hidden_wolves_out_of_player_hud');

  const startPose=controlled(s).pos;await worldTap(page,-18,-23);await frames(page,18);s=await state(page);
  assert.ok(distance(controlled(s).pos,startPose)>1,'Actual canvas move did not move the sheep');
  active=await runData(page);let recorded=reconstructed(active,active.duration),render=await page.evaluate(()=>window.SWYRL_ENGINE_SHEEP_TAG.renderStatus());
  assertWorld(recorded,s,render);assert.notDeepEqual(recorded.entities['run-sheep'].limbAngles,active.initial.entities['run-sheep'].limbAngles,'Moving gait was not captured');
  assert.notDeepEqual(recorded.camera,active.initial.camera,'Follow-camera movement was not captured');
  assert.deepEqual((await runFrame(page,active,active.duration)).entities,recorded.entities,'Public frame reconstruction differs from compact patches');
  for(const unit of render.units){const original=originalRender.units.find(item=>item.id===unit.id);assert.equal(unit.geometrySignature,original.geometrySignature,'Recording changed existing creature geometry');}
  pass('real_canvas_move_records_world_pose_limbs_camera_and_original_geometry');

  await until(page,s=>controlled(s).order===null,'Movement completion',120);s=await state(page);await focus(page,[controlled(s).pos[0],0,controlled(s).pos[2]+8]);
  const feet=[...controlled(s).pos];await tap(page,'stBuildIncome');await frames(page,1);await worldTap(page,feet[0],feet[2]);
  s=await until(page,s=>s.buildings.length===1,'Native paid construction at sheep feet',80);const house=s.buildings[0];
  assert.ok(distance(controlled(s).pos,feet)>.5,'Build at feet did not move the builder to a clear side');assert.ok(s.gold<500,'Paid construction omitted its economy cost');
  const beforeReject={gold:s.gold,buildings:s.buildings.length};const reject=await page.evaluate(({x,z})=>window.SWYRL_ENGINE_SHEEP_TAG.command('build',{kind:'st-income',x,z}),{x:house.pos[0],z:house.pos[2]});
  assert.equal(reject.ok,false,'Overlapping build must be rejected');await frames(page,1);s=await state(page);
  assert.equal(s.gold,beforeReject.gold);assert.equal(s.buildings.length,beforeReject.buildings);
  await until(page,s=>s.buildings[0]?.progress===1,'Actual construction completion',120);await frames(page,25);s=await state(page);active=await runData(page);
  recorded=reconstructed(active,active.duration);render=await page.evaluate(()=>window.SWYRL_ENGINE_SHEEP_TAG.renderStatus());assertWorld(recorded,s,render);
  assert.equal(recorded.entities[house.id].origin,'runtime');assert.ok(active.events.some(event=>event.type==='building-created'&&event.actorId===house.id));
  assert.ok(active.events.some(event=>event.type==='command'&&event.details.ok===false),'Rejected command is absent from the run');
  assert.ok(active.checkpoints.length>0,'Longer run omitted reconstruction checkpoints');
  pass('real_build_at_feet_records_runtime_house_economy_and_rejected_command');

  await tap(page,'stPause');await frames(page,1);const paused=await state(page),pausedRun=await runData(page);await frames(page,50);
  assert.deepEqual(await state(page),paused,'Pause advanced gameplay');const frozenRun=await runData(page);close(frozenRun.duration,pausedRun.duration,'Paused run duration');
  assert.deepEqual(frozenRun.frames,pausedRun.frames,'Pause recorded artificial advancing frames');assert.ok(frozenRun.events.some(event=>event.type==='paused'));
  await tap(page,'stPause');await frames(page,8);assert.ok((await state(page)).elapsed>paused.elapsed);assert.ok((await runData(page)).events.some(event=>event.type==='resumed'));
  pass('pause_freezes_log_time_and_resume_keeps_the_same_run');

  const liveBeforeStop=await state(page),liveRunBeforeStop=await runData(page),lastId=liveRunBeforeStop.id;
  const liveSnapshotBeforeStop=reconstructed(liveRunBeforeStop,liveRunBeforeStop.duration);await stop(page);const completed=await runData(page,lastId);schema(completed);
  assert.equal(completed.complete,true);assert.match(completed.endReason,/stop/);close(completed.duration,liveBeforeStop.elapsed,'Stop final duration');
  recorded=reconstructed(completed,completed.duration);closeArray(recorded.entities['run-sheep'].position,controlled(liveBeforeStop).pos,'Retained final sheep pose');
  assert.deepEqual(recorded.camera,liveSnapshotBeforeStop.camera,'Stop logged a restored editor camera instead of the final Play camera');
  assert.deepEqual(recorded.entities['run-sheep'].limbAngles,liveSnapshotBeforeStop.entities['run-sheep'].limbAngles,'Stop logged restored editor limbs instead of the final animated Play pose');
  assert.ok(recorded.entities[house.id],'Stop discarded the runtime house before recording its final state');assert.deepEqual(recorded.game.resources,liveBeforeStop.resources);
  assert.ok(completed.events.some(event=>event.type==='match-end'));assert.deepEqual(authored(await saved(page)),authored(map),'Stop saved runtime poses, houses or recording');
  assert.equal((await runStatus(page)).active,null);assert.equal((await runStatus(page)).stateLocked,false);
  pass('stop_seals_full_final_world_before_restoring_authored_native_map');

  await openPanel(page);assert.equal(await page.locator('#stRunNarrative').getAttribute('readonly')!==null,true,'Narrative should be read-only');
  const json=await download(page,'stRunExportJson',resolve(output,mode.name+'.swyrl-run.json'));
  const text=await download(page,'stRunExportText',resolve(output,mode.name+'.swyrl-run.txt'));
  const html=await download(page,'stRunExportHtml',resolve(output,mode.name+'.swyrl-run.html'));
  assert.match(json.name,/\.swyrl-run\.json$/);assert.match(text.name,/\.swyrl-run\.txt$/);assert.match(html.name,/\.swyrl-run\.html$/);
  assert.deepEqual(JSON.parse(json.text),completed,'JSON download differs from the completed run');assert.ok(text.text.includes(escapedName),'Text dropped actor names');
  assert.ok(text.text.includes('x '+recorded.entities['run-sheep'].position[0]),'Transcript omitted the actual retained sheep position');
  assert.match(text.text,/north|south|east|west|heading|facing|direction/i,'Transcript omitted spatial directions');
  assert.match(html.text,/<canvas\b/i,'HTML export omitted the actual review canvas');assert.ok(!html.text.includes('<script>window.__runNameExecuted=true</script>'),'HTML embedded an executable actor name');
  await page.screenshot({path:resolve(output,mode.name+'-run-review.png')});await native(page,'stRunClose');
  const offlineContext=await browser.newContext({viewport:mode.viewport,isMobile:mode.isMobile,hasTouch:mode.hasTouch});await offlineContext.setOffline(true);
  const review=await offlineContext.newPage(),offlineErrors=[];if(mode.hasTouch)touchPages.add(review);review.on('pageerror',error=>offlineErrors.push(String(error)));
  await review.goto(pathToFileURL(html.path).href,{waitUntil:'load'});await review.waitForFunction(()=>window.SWYRL_RUN_VIEWER?.state());
  assert.deepEqual(await review.locator('#stRunPayload').evaluate(node=>JSON.parse(node.textContent)),completed);
  assert.equal(await review.evaluate(()=>window.__runNameExecuted),undefined,'Exported actor name executed as script');
  assert.equal(await review.evaluate(()=>!!window.SWYRL_ENGINE_AGENT||!!window.SWYRL_ENGINE_SHEEP_TAG),false,'Read-only export booted a gameplay engine');
  await review.evaluate(()=>window.SWYRL_RUN_VIEWER.seek(0));const firstCanvas=await canvasData(review);assert.ok(firstCanvas.width>0&&firstCanvas.height>0&&firstCanvas.colors>4,'Offline viewer did not render actors');
  await tap(review,'stRunViewPlay');await review.waitForFunction(()=>window.SWYRL_RUN_VIEWER.time()>.05);await tap(review,'stRunViewPlay');
  assert.match(await review.locator('#stRunViewPlay').innerText(),/Play recording/,'Export playback cannot be paused');
  await tap(review,'stRunViewReset');assert.equal(await review.locator('#stRunTimeline').isVisible(),true);
  // seek through the public viewer API and compare its actual drawn canvas.
  await review.evaluate(t=>window.SWYRL_RUN_VIEWER.seek(t),completed.duration);const finalCanvas=await canvasData(review);assert.notEqual(finalCanvas.png,firstCanvas.png,'Offline viewer canvas ignored recorded movement/building');
  close(await review.evaluate(()=>window.SWYRL_RUN_VIEWER.time()),completed.duration,'Offline review final time');
  assert.equal(await review.locator('#stRunNarrative').evaluate(node=>node.readOnly),true);assert.deepEqual(offlineErrors,[]);await offlineContext.close();
  pass('native_json_spatial_text_and_escaped_self_contained_offline_html_downloads');

  await play(page);const restartFrom=(await runData(page)).id;await frames(page,10);await native(page,'stRestart');const restarted=await runData(page);
  assert.notEqual(restarted.id,restartFrom,'Restart reused the run ID');assert.ok(restarted.duration<.2,'Restart reused elapsed time');
  assert.equal((await runData(page,restartFrom)).complete,true,'Restart discarded its prior run');assert.equal((await runData(page,restartFrom)).endReason,'restart');
  assert.deepEqual(await runData(page,lastId),completed,'Restart changed an earlier completed run');await stop(page);pass('restart_allocates_a_new_run_and_retains_prior_completed_history');

  const winning=fixture(canonical,pieces,{sheep:[-30,0,-30],wolf:[30,0,30],rules:{duration:30,headstart:30}});
  await importFixture(page,winning);await play(page);const winId=(await runData(page)).id;await until(page,s=>s.winner==='sheep','Native survival win',650);
  const won=await runData(page,winId);schema(won);assert.equal(won.complete,true);assert.match(won.endReason,/win|winner|sheep/);close(won.duration,30,'Winner final elapsed');
  assert.equal(reconstructed(won,won.duration).game.winner,'sheep');await frames(page,20);assert.deepEqual(await runData(page,winId),won,'Winner kept recording idle frames');
  await stop(page);assert.deepEqual(await runData(page,winId),won,'Stop replaced the finalized winning run');
  assert.deepEqual(authored(await saved(page)),authored(winning));pass('native_win_finalizes_once_and_keeps_the_winning_final_state');

  await openPanel(page);const beforeImport=authored(await saved(page));await page.locator('#stRunFile').setInputFiles(json.path);await frames(page,2);
  assert.equal(await page.locator('#stRunReviewCanvas').isVisible(),true);assert.equal(await page.locator('#stRunNarrative').evaluate(node=>node.readOnly),true);
  const atStart=await scrub(page,'Home'),importFirst=await canvasData(page);close(atStart,0,'Imported scrub start');
  const atEnd=await scrub(page,'End'),importLast=await canvasData(page);close(atEnd,completed.duration,'Imported scrub end',.051);
  assert.notEqual(importFirst.png,importLast.png,'Imported review scrub did not reconstruct recorded actors');
  const finalWords=await page.locator('#stRunNarrative').inputValue();assert.ok(finalWords.includes(escapedName),'Imported narrative omitted recorded actors');
  const expected=await runFrame(page,completed,atEnd);assert.deepEqual(expected.entities,reconstructed(completed,atEnd).entities,'Imported final frame disagrees with JSON patches');
  assert.deepEqual(authored(await saved(page)),beforeImport,'Run JSON import changed the authored map');
  await page.locator('#stRunRun').selectOption(winId,{force:true});await frames(page,1);close(Number(await page.locator('#stRunTimeline').getAttribute('max')),won.duration,'Selected history duration');
  assert.ok((await page.locator('#stRunNarrative').inputValue()).includes(escapedName));
  await native(page,'stRunClose');pass('json_import_history_and_native_scrubber_review_without_editor_mutation');

  const parityMap=fixture(canonical,pieces,{extraSheep:[[-15,0,-18]],rules:{fogMode:'off',headstart:0,seed:741,wolfVision:40}}),traces=[];
  for(const enabled of [false,true]){await importFixture(page,parityMap);await settings(page,enabled,'full');await play(page);await focus(page,[-18,0,-10]);await worldTap(page,-18,-23);
    const trace=[];for(let i=0;i<8;i++){await frames(page,10);trace.push(parity(await state(page)));}traces.push(trace);await stop(page);}
  assert.deepEqual(traces[1],traces[0],'Recording changed seeded gameplay, AI, movement, orders or economy');pass('seeded_actual_gameplay_has_identical_logging_on_and_off_results');

  const cadenceCounts=[];for(const cadence of ['full','0.1','0.5']){await importFixture(page,map);await settings(page,true,cadence);await play(page);await frames(page,40);await stop(page);
    const cadenceRun=await runData(page);schema(cadenceRun);cadenceCounts.push(cadenceRun.frames.length);assert.equal(cadenceRun.complete,true);}
  assert.ok(cadenceCounts[0]>cadenceCounts[1]&&cadenceCounts[1]>cadenceCounts[2],'Editor cadence choices did not alter actual sampling: '+cadenceCounts);
  }
  // Every native project builder uses the same opt-in recorder, not a copied
  // Sheep Tag session. Include both a new empty project and every starter.
  for(const template of ['default','moba','dragons-den','starforge-observatory','anime-ghosts-ep01','sheep-tag-meadow','maul-frostveil']){
    console.log('SHEEP_RUN_STARTER_CHECK',mode.name,template);await page.evaluate(template=>window.SWYRL_ENGINE_AGENT.createProject(template),template);await frames(page,2);
    assert.equal(await page.locator('#stRunLauncher').isVisible(),true,'Recorder missing from '+template);
    await settings(page,false);const beforeDisabled=(await runStatus(page)).runs.map(r=>r.id);
    await native(page,'playBtn');await frames(page,4);await native(page,'stopBtn');
    assert.deepEqual((await runStatus(page)).runs.map(r=>r.id),beforeDisabled,'Disabled '+template+' Play recorded data');
    await settings(page,true);const project=await saved(page);await native(page,'playBtn');await frames(page,8);
    const observed=await runData(page);assert.equal(observed.capture.incomplete,false,'Recorder error in '+template+': '+JSON.stringify(observed.capture.errors));
    assert.equal(await page.evaluate(()=>window.SWYRL_ENGINE_RUNS===window.SWYRL_ENGINE_SHEEP_TAG_RUNS),true);
    assert.ok(Object.keys(observed.initial.entities).length>=project.scene.actors.length,'Missing '+template+' actor catalog');
    const cameraBeforeStop=reconstructed(observed,observed.duration).camera;
    await native(page,'pauseBtn');const frozenTime=(await runData(page)).duration;await frames(page,5);
    close((await runData(page)).duration,frozenTime,'Paused '+template+' time');await native(page,'pauseBtn');await frames(page,3);
    await native(page,'stopBtn');const ended=await runData(page);schema(ended);
    assert.equal(ended.complete,true,'Incomplete '+template+' run: '+JSON.stringify(ended.capture.errors));
    assert.equal(ended.project.project.name,project.project.name);assert.ok(ended.duration>0);assert.ok(cameraBeforeStop.position);
    assert.ok(ended.events.some(e=>e.type==='paused')&&ended.events.some(e=>e.type==='resumed'));
    await openPanel(page);assert.ok((await page.locator('#stRunNarrative').inputValue()).length>100);await native(page,'stRunClose');
  }
  pass('all_seven_native_project_builders_support_recording_toggle_pause_stop_and_review');
  // A user-authored project works through the ordinary importer as well.
  const custom=structuredClone(await saved(page));custom.project={...custom.project,name:'Custom recording project',kind:'default',template:'custom',canonicalId:null};
  await page.evaluate(data=>window.SWYRL_ENGINE_AGENT.loadScene(data),custom);await frames(page,2);await settings(page,true);
  await native(page,'playBtn');await frames(page,5);await native(page,'stopBtn');const customRun=await runData(page);schema(customRun);
  assert.equal(customRun.complete,true);assert.equal(customRun.project.project.name,'Custom recording project');
  pass('imported_custom_projects_use_the_same_engine_recorder');
  await settings(page,false,'full');await page.evaluate(data=>window.SWYRL_ENGINE_AGENT.loadScene(data),canonical);await frames(page,2);
  assert.deepEqual(authored(await saved(page)),authored(canonical),'Final canonical restoration failed');assert.deepEqual(errors,[],'Unhandled browser errors: '+errors.join('\n'));
  if(!process.env.SWYRL_RUN_GENERIC_ONLY)pass('full_tenth_and_half_second_cadence_controls_and_final_native_restoration');
  receipts.push({mode:mode.name,cases,pass:true});console.log('SHEEP_RUN_'+mode.name.toUpperCase()+'_PASS');await context.close();
}
await writeFile(resolve(output,'receipt.json'),JSON.stringify({pass:true,viewports:receipts},null,2));console.log('SHEEP_RUN_ALL_VIEWPORTS_PASS');
}finally{await browser.close();}
