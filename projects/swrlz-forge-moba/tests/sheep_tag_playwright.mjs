import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {mkdir,readFile,writeFile} from 'node:fs/promises';
import {resolve} from 'node:path';

// Exercise native editor authorship, visible controls, canvas orders, and the
// actual Play/Stop session. The frame clock controls elapsed real engine time;
// no game state, unit AI, collision, economy, or render function is mocked.
const base=(process.env.SWYRL_ANIME_TEST_URL||'http://127.0.0.1:8765').replace(/\/$/,'');
const query=new URLSearchParams(process.env.SWYRL_ANIME_TEST_QUERY||'');
query.set('project','sheep-tag-meadow');
const output=resolve(process.env.SWYRL_ANIME_SCREENSHOTS_DIR||'sheep-tag-acceptance');
await mkdir(output,{recursive:true});
const modes=[
  {name:'desktop',viewport:{width:1440,height:900},isMobile:false,hasTouch:false},
  {name:'mobile',viewport:{width:390,height:844},isMobile:true,hasTouch:true}
].filter(mode=>!process.env.SWYRL_ANIME_TEST_MODE||process.env.SWYRL_ANIME_TEST_MODE===mode.name);
assert.ok(modes.length,'SWYRL_ANIME_TEST_MODE must be desktop or mobile');
const browser=await chromium.launch({headless:true,
  ...(process.env.SWYRL_CHROMIUM_PATH?{executablePath:process.env.SWYRL_CHROMIUM_PATH}:{}),
  args:['--no-sandbox','--disable-dev-shm-usage','--enable-webgl',
    '--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader']});
const touchPages=new WeakSet(),receipts=[];
const state=page=>page.evaluate(()=>window.SWYRL_ENGINE_SHEEP_TAG.status());
const saved=page=>page.evaluate(()=>window.SWYRL_ENGINE_AGENT.inspectScene());
const frames=(page,count=1,ms=50)=>page.evaluate(({count,ms})=>window.__sheepTestClock.step(count,ms),{count,ms});
const command=(page,name,args={})=>page.evaluate(({name,args})=>window.SWYRL_ENGINE_SHEEP_TAG.command(name,args),{name,args});
const distance=(a,b)=>Math.hypot(a[0]-b[0],a.at(-1)-b.at(-1));
const close=(actual,expected,label,tolerance=1e-6)=>assert.ok(Number.isFinite(actual)&&Math.abs(actual-expected)<=tolerance,
  label+': expected '+expected+', received '+actual);
const authored=p=>({project:p.project,layers:p.editor.layers,background:p.scene.background,
  paths:p.scene.paths,actors:p.scene.actors});
async function tap(page,id){
  const button=page.locator('#'+id);
  assert.equal(await button.isVisible(),true,'Required control is not visible: '+id);
  // A frozen actual RAF cannot satisfy Playwright's two-frame stability wait.
  if(touchPages.has(page))await button.tap({force:true});else await button.click({force:true});
}
async function nativeButton(page,id){
  // The engine keeps the same native session controls on desktop and phone.
  assert.equal(await page.locator('#'+id).isVisible(),true,'Native button is hidden: '+id);
  await tap(page,id);await frames(page,2);
}
async function worldTap(page,x,z,y=0){
  const p=await page.evaluate(({x,z,y})=>window.SWYRL_ENGINE_SHEEP_TAG.pointScreen(x,z,y),{x,z,y});
  assert.ok(p&&Number.isFinite(p.x)&&Number.isFinite(p.y),'World order did not project into the real canvas');
  // Only native Play building placement offsets the finger; movement, rescue,
  // house inspection and the stopped map creator retain their original taps.
  if(touchPages.has(page)&&(await page.evaluate(()=>window.SWYRL_ENGINE_SHEEP_TAG.uiStatus().build)))p.y+=64;
  const hit=await page.evaluate(({x,y})=>{
    const n=document.elementFromPoint(x,y);return !!n&&(n.tagName==='CANVAS'||n.id==='viewport');
  },p);
  assert.equal(hit,true,'World order would hit editor/HUD instead of canvas: '+JSON.stringify(p));
  if(touchPages.has(page))await page.touchscreen.tap(p.x,p.y);else await page.mouse.click(p.x,p.y);
  await frames(page,1);
}
async function until(page,predicate,label,maxFrames=300){
  let current=await state(page);
  for(let i=0;i<maxFrames&&!predicate(current);i+=5){await frames(page,Math.min(5,maxFrames-i));current=await state(page);}
  assert.ok(predicate(current),label+' did not occur in actual rendered simulation: '+JSON.stringify(current));
  return current;
}
async function installClock(context){
  await context.addInitScript(()=>{
    const nativeRAF=window.requestAnimationFrame.bind(window),nativeCancel=window.cancelAnimationFrame.bind(window);
    const nativeNow=performance.now.bind(performance),queue=new Map();
    let frozen=false,now=0,next=1000000000;
    Object.defineProperty(performance,'now',{configurable:true,value:()=>frozen?now:nativeNow()});
    window.requestAnimationFrame=callback=>{if(!frozen)return nativeRAF(callback);const id=next++;queue.set(id,callback);return id;};
    window.cancelAnimationFrame=id=>{queue.delete(id);nativeCancel(id);};
    window.__sheepTestClock={
      freeze:()=>{frozen=true;now=nativeNow();return new Promise(resolve=>nativeRAF(()=>nativeRAF(resolve)));},
      step:(count,ms)=>{
        if(!frozen)throw new Error('The native game frame clock is not frozen');
        for(let i=0;i<count;i++){
          now+=ms;const pending=[...queue.values()];queue.clear();
          if(!pending.length)throw new Error('No actual engine RAF callbacks remain');
          for(const callback of pending)callback(now);
        }
        return {now,pending:queue.size};
      }
    };
  });
}

async function loadFixture(page,canonical,farm,options={}){
  const data=structuredClone(canonical),actors=data.scene.actors;
  const sheep=actors.filter(a=>a.type==='st-sheep').slice(0,options.sheep?.length||1);
  const wolves=actors.filter(a=>a.type==='st-wolf').slice(0,1);
  const shop=actors.find(a=>a.type==='st-shop');
  const keep=actors.filter(a=>a.type==='st-meadow'||a.type==='st-pen');
  keep.find(a=>a.type==='st-pen').position=options.pen||[0,0,0];
  sheep.forEach((a,index)=>{a.position=options.sheep?.[index]||[18,0,-18];a.rotation=[0,0,0];});
  wolves[0].position=options.wolf||[-18,0,18];wolves[0].rotation=[0,0,0];
  data.scene.actors=[...keep,...sheep,...wolves,...(options.shops||[]).map((position,index)=>
    ({...structuredClone(shop),id:'acceptance-merchant-'+index,name:'Authored acceptance merchant '+index,position})),
    ...(options.farms||[]).map((position,index)=>
    ({...structuredClone(farm),id:'acceptance-farm-'+index,name:'Authored acceptance farm '+index,
      baked:true,position,rotation:[0,0,0],scale:[1,1,1]}))];
  data.project.sheepTag={...canonical.project.sheepTag,duration:1200,headstart:30,bounds:40,startGold:200,role:'sheep',preset:'classic',fogMode:'off',sheepSpeed:5.4,wolfSpeed:6.2,wolfDamage:65,attackInterval:.75,rescueHold:.2,thorns:false,totems:false,elevated:false,split:false,events:false,...options.rules};
  await page.evaluate(data=>window.SWYRL_ENGINE_AGENT.loadScene(data),data);
  await frames(page,2);
  assert.deepEqual(authored(await saved(page)),authored(data),'Native import changed the authored fixture');
  await nativeButton(page,'playBtn');
  assert.equal((await state(page)).active,true,'Authored fixture failed Play preflight: '+JSON.stringify(await page.evaluate(()=>window.SWYRL_ENGINE_SHEEP_TAG.validateStarts())));
  return {data,sheep:sheep.map(a=>a.id),wolf:wolves[0].id};
}
async function visibleBuildSite(page,kind){
  const s=await state(page),unit=s.units.find(u=>u.id===s.controlledId);
  // Frame nearby sites in the usable phone playfield after the build controls
  // open, leaving room below the preview for its actual finger position.
  if(touchPages.has(page)){
    await page.evaluate(pos=>window.SWYRL_ENGINE_SHEEP_TAG.focus(pos),[unit.pos[0],0,unit.pos[2]+8]);
    await frames(page,1);
  }
  const sites=[];
  for(const [dx,dz] of [[3,0],[-3,0],[0,-3],[0,3],[3,-3],[-3,3],[6,0],[-6,0],[0,-6],[0,6]]){
    const fit=await page.evaluate(({kind,x,z})=>window.SWYRL_ENGINE_SHEEP_TAG.canBuild(kind,x,z),
      {kind,x:unit.pos[0]+dx,z:unit.pos[2]+dz});
    if(!fit.ok)continue;
    const p=await page.evaluate(({x,z})=>window.SWYRL_ENGINE_SHEEP_TAG.pointScreen(x,z),fit);
    const free=await page.evaluate(({p,touch})=>{
      if(touch)for(const n of document.querySelectorAll('#sheepTagHUD .st-score,#sheepTagHUD .st-phase,#sheepTagHUD .st-event,#sheepTagHUD .st-attack-feedback')){
        if(n.hidden||!n.getClientRects().length)continue;const r=n.getBoundingClientRect();if(p.x>=r.left-16&&p.x<=r.right+16&&p.y<r.bottom+24)return false;}
      return [p,{x:p.x,y:p.y+(touch?64:0)}].every(q=>{const n=document.elementFromPoint(q.x,q.y);return n?.tagName==='CANVAS'||n?.id==='viewport';});
    },{p,touch:touchPages.has(page)});
    if(p.visible&&free)sites.push(fit);
  }
  assert.ok(sites.length,'No visible clear construction site beside the authored sheep spawn');
  return sites[0];
}
async function nativeExport(page,mode){
  const pending=page.waitForEvent('download',{timeout:15000});
  if(mode.hasTouch){
    await tap(page,'sheepTagRulesBtn');await tap(page,'stRulesSave');
  }else await tap(page,'saveBtn');
  const download=await pending,data=JSON.parse(await readFile(await download.path(),'utf8'));
  if(mode.hasTouch)await tap(page,'stRulesClose');
  return data;
}

try{
  for(const mode of modes){
    const context=await browser.newContext({viewport:mode.viewport,isMobile:mode.isMobile,hasTouch:mode.hasTouch});
    await installClock(context);
    const page=await context.newPage(),errors=[];
    if(mode.hasTouch)touchPages.add(page);
    page.on('pageerror',error=>errors.push(String(error)));
    page.setDefaultTimeout(30000);
    await page.goto(base+'/index.html?'+query,{waitUntil:'domcontentloaded',timeout:60000});
    await page.waitForFunction(()=>window.SWYRL_ENGINE_SHEEP_TAG&&window.SWYRL_ENGINE_AGENT.project().canonicalId==='sheep-tag-meadow',undefined,{timeout:60000});
    await page.locator('#perfPreset').selectOption('medium',{force:true});
    await page.evaluate(()=>window.__sheepTestClock.freeze());await frames(page,2);
    const canonical=await saved(page);
    assert.equal(canonical.version,11.9,'Wrong native project release');
    assert.equal(await page.evaluate(()=>window.SWRLZ_FORGE_BUILD?.version),'v11.62','Wrong sealed engine release');
    assert.equal(canonical.project.kind,'sheep-tag');
    assert.equal(canonical.project.sheepTag.duration,1200,'Classic starter survival timer changed');
    assert.equal(canonical.project.sheepTag.headstart,30,'Sheep need a real building head start');
    assert.equal(canonical.scene.actors.filter(a=>a.type==='st-sheep').length,8);
    assert.equal(canonical.scene.actors.filter(a=>a.type==='st-wolf').length,3);
    assert.equal(canonical.scene.actors.filter(a=>a.type==='st-pen').length,1);
    assert.ok(canonical.scene.actors.some(a=>a.type==='st-tree')&&canonical.scene.actors.some(a=>a.type==='st-pond'),
      'Starter map lacks its native woodland, water, and escape spaces');
    assert.ok(canonical.editor.layers.length>=6,'Map scenery, pen, and spawns do not have editable layers');
    for(const actor of canonical.scene.actors)assert.ok(actor.editorLayerIds?.length&&actor.baked,'Starter has an unlayered or unbaked actor: '+actor.name);
    const initialRules=canonical.project.sheepTag;
    await tap(page,'sheepTagRulesBtn');
    assert.equal(await page.locator('#sheepTagRulesDialog').isVisible(),true);
    await page.locator('#stRuleDuration').fill('2');await page.locator('#stRuleHeadstart').fill('30');
    await page.locator('#stRuleGold').fill('200');await tap(page,'stRulesApply');await tap(page,'stRulesClose');
    assert.deepEqual((await saved(page)).project.sheepTag,{...initialRules,duration:120,startGold:200},'Visible rule edits were not authored');
    await page.locator('#undoBtn').evaluate(button=>button.click());await frames(page,1);
    assert.deepEqual((await saved(page)).project.sheepTag,initialRules,'Native Undo did not restore authored game rules');
    await page.locator('#redoBtn').evaluate(button=>button.click());await frames(page,1);
    assert.equal((await saved(page)).project.sheepTag.startGold,200,'Native Redo did not restore authored rule edit');
    const playable=await saved(page),exported=await nativeExport(page,mode);
    assert.deepEqual(authored(exported),authored(playable),'Native Save lost map actors, layers, or rules');
    await page.evaluate(data=>window.SWYRL_ENGINE_AGENT.loadScene(data),exported);await frames(page,2);
    assert.deepEqual(authored(await saved(page)),authored(exported),'Native Save/import roundtrip changed authored project');
    console.log('SHEEP_TAG_'+mode.name.toUpperCase()+'_RULES_SAVE_IMPORT_UNDO_REDO_PASS');

    // Use the real editor to obtain the farm actor serialization for all small
    // authored scenarios below. Fixtures are native project data, never injected
    // into a running session or used to overwrite its runtime state.
    const farm=await page.evaluate(()=>{
      const id=window.SWYRL_ENGINE_AGENT.spawn('st-farm',{position:[-12,0,12],name:'Native test farm'});
      window.SWYRL_ENGINE_AGENT.bake();
      return window.SWYRL_ENGINE_AGENT.inspectScene().scene.actors.find(a=>a.id===id);
    });
    assert.ok(farm&&farm.type==='st-farm','Editor cannot create the reusable native building prefab');
    await page.evaluate(data=>window.SWYRL_ENGINE_AGENT.loadScene(data),playable);await frames(page,1);
    await nativeButton(page,'playBtn');
    let s=await state(page);assert.equal(s.active,true);assert.equal(s.role,'sheep');
    const unreleasedWolves=s.units.filter(u=>u.kind==='wolf').map(u=>({id:u.id,pos:u.pos}));
    assert.equal(s.units.length,11);assert.ok(s.headstartRemaining>29,'Hunt skipped its head start');
    assert.equal(await page.locator('#sheepTagHUD').isVisible(),true,'Native Play did not open the game controls');
    assert.equal(await page.evaluate(()=>document.pointerLockElement),null,'RTS player entered first person pointer lock');
    const metrics=await page.locator('#stBuildFarm,#stBuildIncome,#stBuildFort,#stPause,#stStop,#stRestart,#stSelectMine').evaluateAll(buttons=>buttons.map(button=>{
      const r=button.getBoundingClientRect();return {id:button.id,left:r.left,right:r.right,top:r.top,bottom:r.bottom,width:r.width,height:r.height,w:innerWidth,h:innerHeight};
    }));
    for(const r of metrics){
      assert.ok(r.left>=0&&r.right<=r.w+1&&r.top>=0&&r.bottom<=r.h+1,'Game controls overflow the viewport: '+JSON.stringify(r));
      assert.ok(r.width>=40&&r.height>=35,'Game control is too small to operate: '+r.id);
    }
    await tap(page,'stHelp');assert.match(await page.locator('#stHelpPanel').innerText(),/wisp|spirit/i);
    await tap(page,'stHelpClose');
    const controlled=s.units.find(u=>u.id===s.controlledId),moveSite={x:controlled.pos[0],z:controlled.pos[2]-6};
    await tap(page,'stSelectMine');await worldTap(page,moveSite.x,moveSite.z);
    s=await until(page,s=>distance(s.units.find(u=>u.id===s.controlledId).pos,[moveSite.x,0,moveSite.z])<.6,'Visible canvas move');
    await tap(page,'stBuildIncome');assert.equal(await page.locator('#stBuildIncome').getAttribute('aria-pressed'),'true');await frames(page,1);
    const site=await visibleBuildSite(page,'st-income'),beforeBuild=await state(page);
    await worldTap(page,site.x,site.z);
    let constructing=await until(page,s=>s.buildings.some(b=>b.owner===s.controlledId&&b.kind==='st-income'),'Visible construction order',200);
    const income=constructing.buildings.find(b=>b.owner===constructing.controlledId&&b.kind==='st-income');
    assert.ok(income.progress<1,'Income farm skipped its actual construction phase');
    const deltaTime=constructing.elapsed-beforeBuild.elapsed;
    assert.ok(constructing.gold<=beforeBuild.gold-60+Math.ceil(deltaTime)+1,'Paid building did not charge its construction cost');
    s=await until(page,s=>s.buildings.find(b=>b.id===income.id)?.progress===1,'Income farm construction',100);
    const incomeBefore=s.gold;await frames(page,60);s=await state(page);
    assert.ok(s.gold-incomeBefore>=12,'Completed income farm did not increase the real economy');
    const rejectionBefore=await state(page),overlap=await command(page,'build',{kind:'st-income',x:site.x,z:site.z});
    assert.equal(overlap.ok,false,'Overlapping construction was accepted');
    assert.match(overlap.reason,/occup|space|building/i);assert.equal((await state(page)).gold,rejectionBefore.gold,'Rejected overlap spent gold');
    const penReject=await command(page,'build',{kind:'st-income',x:0,z:0});
    assert.equal(penReject.ok,false,'Construction blocked the central wisp pen');
    assert.match(penReject.reason,/pen|entrance|clear/i);assert.equal((await state(page)).gold,rejectionBefore.gold,'Rejected pen construction spent gold');
    await worldTap(page,site.x,site.z,1);
    assert.equal((await state(page)).selectedId,(await state(page)).controlledId,'Single house tap should keep the sheep selected');
    await worldTap(page,site.x,site.z,1);assert.equal((await state(page)).selectedId,income.id,'Canvas double tap did not select the owned farm');
    const beforeUpgrade=await state(page);await tap(page,'stUpgrade');s=await state(page);
    assert.equal(s.buildings.find(b=>b.id===income.id).level,2,'Visible upgrade did not improve the owned farm');
    close(beforeUpgrade.gold-s.gold,50,'Upgrade cost');
    assert.deepEqual(s.units.filter(u=>u.kind==='wolf').map(u=>({id:u.id,pos:u.pos})),unreleasedWolves,
      'Wolves moved before the authored head start expired');
    await tap(page,'stPause');const paused=await state(page);await frames(page,20);
    assert.deepEqual(await state(page),paused,'Native Pause advanced game time, orders, construction, or income');
    assert.match(await page.locator('#stPhase').innerText(),/paused/i);
    await tap(page,'stPause');await frames(page,2);assert.ok((await state(page)).elapsed>paused.elapsed,'Native Resume did not restart the game clock');
    await page.screenshot({path:resolve(output,mode.name+'-sheep-builder.png')});
    const beforeSell=await state(page);await tap(page,'stSell');s=await state(page);
    assert.ok(!s.buildings.some(b=>b.id===income.id),'Visible Sell did not clear the selected owned farm');
    close(s.gold-beforeSell.gold,55,'Upgraded income farm sell refund');
    await tap(page,'stSelectMine');
    await tap(page,'stBuildFarm');await frames(page,1);
    const freeSite=await visibleBuildSite(page,'st-farm'),beforeFree=await state(page);
    await worldTap(page,freeSite.x,freeSite.z);
    s=await until(page,s=>s.buildings.some(b=>b.owner===s.controlledId&&b.kind==='st-farm'),'Visible free farm construction',150);
    assert.ok(s.gold>=beforeFree.gold,'Free blocking farm incorrectly spent the sheep’s gold');
    const freeFarm=s.buildings.find(b=>b.owner===s.controlledId&&b.kind==='st-farm');
    await until(page,s=>s.buildings.find(b=>b.id===freeFarm.id)?.progress===1,'Free farm construction',50);
    console.log('SHEEP_TAG_'+mode.name.toUpperCase()+'_CANVAS_BUILD_INCOME_UPGRADE_SELL_PAUSE_PASS');
    await tap(page,'stRestart');await frames(page,1);s=await state(page);
    assert.ok(s.elapsed<.1,'Restart retained the old match clock');
    assert.equal(s.buildings.length,0,'Restart retained transient farms');
    assert.equal(s.units.filter(u=>u.captured).length,0,'Restart retained captured wisps');
    assert.equal(s.gold,200,'Restart retained spent or earned gold');
    await tap(page,'stStop');await frames(page,1);
    assert.equal((await state(page)).active,false);assert.equal(await page.locator('#sheepTagHUD').isVisible(),false);
    assert.deepEqual(authored(await saved(page)),authored(playable),'Stop baked runtime positions or buildings into the authored map');
    console.log('SHEEP_TAG_'+mode.name.toUpperCase()+'_RESTART_STOP_AUTHORING_RESTORATION_PASS');

    // Continuous authored farm wall: sheep fit its 0.6-unit gaps; larger wolves
    // cannot route through or around its boundary-to-boundary barrier.
    const wall=[];for(let x=-15;x<=15;x+=3)wall.push([x,0,0]);
    await loadFixture(page,canonical,farm,{sheep:[[1.5,0,-6]],wolf:[10,0,10],farms:wall,pen:[-10,0,10],rules:{bounds:16}});
    assert.equal((await command(page,'move',{x:1.5,z:6})).ok,true,'Sheep cannot enter its narrow farm passage');
    s=await until(page,s=>s.units.find(u=>u.controlled).pos[2]>5.5,'Sheep-only passage',150);
    assert.ok(s.units.find(u=>u.controlled).pos[0]>1.2&&s.units.find(u=>u.controlled).pos[0]<1.8,'Sheep crossed through a farm rather than the gap');
    await tap(page,'stStop');await frames(page,1);
    await loadFixture(page,canonical,farm,{sheep:[[10,0,10]],wolf:[1.5,0,-6],farms:wall,pen:[-10,0,10],rules:{bounds:16,role:'wolf',headstart:0}});
    const wolfBefore=(await state(page)).units.find(u=>u.controlled).pos;
    const blocked=await command(page,'move',{x:1.5,z:6});assert.equal(blocked.ok,false,'Wolf fitted into the sheep-only farm gap');
    assert.match(blocked.reason,/route/i);await frames(page,5);
    assert.deepEqual((await state(page)).units.find(u=>u.controlled).pos,wolfBefore,'Rejected wolf route crossed a farm wall');
    await tap(page,'stStop');await frames(page,1);
    console.log('SHEEP_TAG_'+mode.name.toUpperCase()+'_SHEEP_PASSAGE_WOLF_BLOCKED_PASS');

    // Capture the controlled sheep through real native spawn placement. Its
    // buildings disappear, its Den-style wisp stays in the pen, and it cannot
    // buy or construct buildings while captured.
    const captive=await loadFixture(page,canonical,farm,{sheep:[[-18,0,-18],[-9,0,0]],wolf:[-17.8,0,-18],
      farms:[[-21,0,-18],[12,0,9]],rules:{headstart:0}});
    s=await until(page,s=>s.units.find(u=>u.id===captive.sheep[0]).captured,'Real wolf capture',10);
    assert.equal(s.units.find(u=>u.id===captive.sheep[0]).kind,'wisp','Captured sheep did not become a wisp');
    assert.ok(!s.buildings.some(b=>b.owner===captive.sheep[0]),'Captured sheep kept its farm walls');
    assert.ok(s.buildings.some(b=>b.owner===captive.sheep[1]),'Capture removed another sheep’s farm');
    const capturedGold=s.gold,cannotBuild=await command(page,'build',{kind:'st-income',x:12,z:12});
    assert.equal(cannotBuild.ok,false);assert.match(cannotBuild.reason,/living|sheep/i);assert.equal((await state(page)).gold,capturedGold);
    assert.equal(await page.locator('#stBuildFarm').isDisabled(),true,'Captured wisp still has an enabled build button');
    assert.equal((await command(page,'move',{x:100,z:-100})).ok,true);await frames(page,25);s=await state(page);
    const spirit=s.units.find(u=>u.id===captive.sheep[0]);
    assert.ok(spirit.captured&&Math.abs(spirit.pos[0])<=4.2&&Math.abs(spirit.pos[2])<=4.2,'Wisp escaped the central prison');
    await page.screenshot({path:resolve(output,mode.name+'-captured-wisp.png')});
    await tap(page,'stStop');await frames(page,1);

    // The controlled living sheep rescues a tagged teammate by reaching the
    // actual wisp. The ordered rescue is issued by tapping the real canvas.
    const rescue=await loadFixture(page,canonical,farm,{sheep:[[-9,0,0],[-18,0,-18]],wolf:[-17.8,0,-18],
      farms:[[-21,0,-18]],rules:{headstart:0}});
    s=await until(page,s=>s.units.find(u=>u.id===rescue.sheep[1]).captured,'Teammate capture',10);
    const wisp=s.units.find(u=>u.id===rescue.sheep[1]);
    await page.evaluate(pos=>window.SWYRL_ENGINE_SHEEP_TAG.focus(pos),wisp.pos);await frames(page,1);
    await worldTap(page,wisp.pos[0],wisp.pos[2]);
    assert.equal((await state(page)).units.find(u=>u.controlled).order?.action,'rescue','Canvas wisp tap did not issue a rescue');
    s=await until(page,s=>!s.units.find(u=>u.id===rescue.sheep[1]).captured,'Living sheep rescue',100);
    assert.equal(s.units.find(u=>u.id===rescue.sheep[1]).kind,'sheep');
    assert.ok(!s.buildings.some(b=>b.owner===rescue.sheep[1]),'Rescue resurrected the old blocking farms');
    assert.match(s.message,/rescu/i,'Real rescue has no game feedback');
    await tap(page,'stStop');await frames(page,1);
    console.log('SHEEP_TAG_'+mode.name.toUpperCase()+'_ACTUAL_CAPTURE_WISP_BOUNDS_CANVAS_RESCUE_PASS');

    // Play as the wolf and destroy an authored farm through the visible attack
    // gesture. The real attack cooldown must apply damage before destruction.
    await loadFixture(page,canonical,farm,{sheep:[[20,0,-20]],wolf:[-12,0,12],farms:[[-9,0,12]],rules:{role:'wolf',headstart:0}});
    const huntBefore=await state(page),target=huntBefore.buildings[0];
    await worldTap(page,target.pos[0],target.pos[2]);
    assert.equal((await state(page)).units.find(u=>u.controlled).order?.action,'attack','Wolf canvas tap did not attack the farm');
    s=await until(page,s=>s.buildings.some(b=>b.id===target.id&&b.hp<target.hp),'Actual wolf damage',80);
    assert.ok(s.buildings.find(b=>b.id===target.id).hp>0,'Farm was destroyed without intermediate damage');
    s=await until(page,s=>!s.buildings.some(b=>b.id===target.id),'Actual farm destruction',100);
    assert.ok(s.gold>huntBefore.gold,'Farm destruction did not award the hunting wolf its bounty');
    await page.screenshot({path:resolve(output,mode.name+'-wolf-hunt.png')});
    await tap(page,'stStop');await frames(page,1);

    // Three legal tags earn enough bounty to buy a hunting upgrade beside an
    // authored merchant. A fourth distant living sheep keeps the round open.
    // The native fixture places these spawns before Play; no gold is injected.
    await loadFixture(page,canonical,farm,{sheep:[[-11.3,0,12],[-12.35,0,11.394],[-12.35,0,12.606],[20,0,-20]],
      wolf:[-12,0,12],shops:[[-15,0,12]],rules:{role:'wolf',headstart:0}});
    s=await until(page,s=>s.units.filter(u=>u.captured).length===3,'Hunting tag bounty',10);
    assert.equal(s.winner,null,'Merchant fixture ended before the living sheep could survive');
    close(s.gold,180,'Three real tag bounties');
    const hunter=s.units.find(u=>u.controlled),purchaseGold=s.gold;
    assert.equal(await page.locator('#stWolfUpgrade').isDisabled(),false,'Nearby merchant upgrade is unavailable despite earned bounty');
    await tap(page,'stWolfUpgrade');s=await state(page);
    const upgraded=s.units.find(u=>u.controlled);
    assert.equal(upgraded.level,2,'Visible merchant button did not upgrade the wolf');
    close(purchaseGold-s.gold,75,'Merchant hunting upgrade cost');
    close(upgraded.damage-hunter.damage,25,'Hunting damage improvement');
    close(upgraded.speed-hunter.speed,.55,'Hunting speed improvement');
    await page.screenshot({path:resolve(output,mode.name+'-wolf-merchant.png')});
    await tap(page,'stStop');await frames(page,1);
    console.log('SHEEP_TAG_'+mode.name.toUpperCase()+'_ACTUAL_WOLF_DAMAGE_BOUNTY_MERCHANT_PURCHASE_PASS');

    // Both victory conditions run on the real engine clock using legal short
    // authored rules. A head start equal to the timer keeps this timing case
    // about survival rather than an unrelated bot chase.
    await loadFixture(page,canonical,farm,{sheep:[[18,0,-18]],wolf:[-18,0,18],rules:{duration:30,headstart:30}});
    s=await until(page,s=>s.winner==='sheep','Survival timer victory',610);
    close(s.elapsed,30,'Survival timer boundary');assert.equal(s.remaining,0);
    const victory=await state(page);await frames(page,20);assert.deepEqual(await state(page),victory,'Finished survival round kept simulating');
    assert.match(await page.locator('#stPhase').innerText(),/surviv/i);
    await tap(page,'stStop');await frames(page,1);
    await loadFixture(page,canonical,farm,{sheep:[[-18,0,-18]],wolf:[-17.8,0,-18],rules:{headstart:0,role:'wolf'}});
    s=await until(page,s=>s.winner==='wolves','All-captured wolf victory',10);
    assert.equal(s.units.filter(u=>u.kind==='sheep').length,0);assert.equal(s.units.filter(u=>u.kind==='wisp').length,1);
    assert.match(await page.locator('#stPhase').innerText(),/caught/i);
    await tap(page,'stStop');await frames(page,1);
    console.log('SHEEP_TAG_'+mode.name.toUpperCase()+'_NATIVE_TIMER_AND_WOLF_VICTORY_PASS');

    // Leaving this game releases its input/camera/HUD and preserves the older
    // native starters. Load each ordinary project and enter its native Play.
    await page.evaluate(()=>window.SWYRL_ENGINE_AGENT.buildGlitchDragonsDen());await frames(page,2);
    const den=await saved(page);assert.equal((await state(page)).active,false);
    await nativeButton(page,'playBtn');await frames(page,3);
    await page.evaluate(()=>document.exitPointerLock?.());await frames(page,1);await nativeButton(page,'stopBtn');
    assert.deepEqual(authored(await saved(page)),authored(den),'Sheep Tag polluted the Den’s native lifecycle');
    await page.evaluate(()=>window.SWYRL_ENGINE_AGENT.buildAnimeEpisode());await frames(page,2);
    const anime=await saved(page);await nativeButton(page,'playBtn');await frames(page,3);
    assert.equal(await page.evaluate(()=>window.SWYRL_ENGINE_CINEMATIC.status().active),true,'Sheep Tag intercepted the anime’s native Play');
    await nativeButton(page,'stopBtn');assert.deepEqual(authored(await saved(page)),authored(anime),'Sheep Tag changed the existing anime starter');
    assert.equal((await state(page)).active,false);assert.equal(await page.locator('#sheepTagHUD').isVisible(),false);
    await page.evaluate(data=>window.SWYRL_ENGINE_AGENT.loadScene(data),canonical);await frames(page,2);
    assert.deepEqual(authored(await saved(page)),authored(canonical),'Final native roundtrip failed to restore the untouched starter');
    assert.deepEqual(errors,[],'Unhandled browser errors: '+errors.join('\n'));
    receipts.push({mode:mode.name,mapActors:canonical.scene.actors.length,layers:canonical.editor.layers.length,
      controls:metrics,pass:true,cases:['native_rules_save_import_undo_redo','canvas_move_build_upgrade',
        'income_cost_construction_overlap_pen','native_sell_refund_clear_free_farm','pause_restart_stop_restoration','sheep_only_farm_gap',
        'wolf_blocked_gap','capture_wisp_bounds_no_build','canvas_rescue','wolf_damage_destruction_bounty',
        'earned_tag_bounty_native_merchant_purchase','survival_timer_win','all_captured_wolf_win','den_anime_lifecycle_isolation']});
    console.log('SHEEP_TAG_'+mode.name.toUpperCase()+'_NATIVE_EDITOR_UI_GAMEPLAY_LIFECYCLE_PASS');
    await context.close();
  }
  await writeFile(resolve(output,'receipt.json'),JSON.stringify({pass:true,viewports:receipts},null,2));
  console.log('SHEEP_TAG_ALL_VIEWPORTS_PASSED');
}finally{await browser.close();}
