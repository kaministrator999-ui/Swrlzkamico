import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {mkdir,writeFile} from 'node:fs/promises';
const base=process.env.SWYRL_TEST_URL||'http://127.0.0.1:8789';
const out=process.env.SWYRL_TEST_OUT||'/workspace/sheep-astra-tests';await mkdir(out,{recursive:true});
const browser=await chromium.launch({headless:true,executablePath:process.env.SWYRL_CHROMIUM_PATH||'/usr/bin/chromium',args:['--no-sandbox','--disable-dev-shm-usage','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader']});
const receipts=[];
try{for(const [mode,viewport] of [['desktop',{width:1440,height:900}],['phone',{width:412,height:915}]]){
 const context=await browser.newContext({viewport,isMobile:mode==='phone',hasTouch:mode==='phone'});
 // Advance the real frame callbacks deterministically; never alter match state.
 await context.addInitScript(()=>{
  const raf=requestAnimationFrame.bind(window),cancel=cancelAnimationFrame.bind(window),now=performance.now.bind(performance),queue=new Map();let frozen=false,time=0,serial=1e9;
  Object.defineProperty(performance,'now',{configurable:true,value:()=>frozen?time:now()});
  window.requestAnimationFrame=cb=>{if(!frozen)return raf(cb);const id=serial++;queue.set(id,cb);return id;};
  window.cancelAnimationFrame=id=>{queue.delete(id);cancel(id);};
  window.courierClock={freeze:()=>{frozen=true;time=now();return new Promise(resolve=>raf(()=>raf(resolve)));},step:n=>{for(let i=0;i<n;i++){time+=50;const work=[...queue.values()];queue.clear();if(!work.length)throw Error('Native RAF stopped');for(const cb of work)cb(time);}}};
 });
 const page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(String(e)));page.setDefaultTimeout(60000);
 const snap=()=>page.evaluate(()=>window.SWYRL_ENGINE_AGENT.inspectScene());
 const state=()=>page.evaluate(()=>window.SWYRL_ENGINE_SHEEP_TAG.status());
 const render=()=>page.evaluate(()=>window.SWYRL_ENGINE_SHEEP_TAG.renderStatus());
 const step=n=>page.evaluate(n=>window.courierClock.step(n),n);
 const command=(action,payload={})=>page.evaluate(({action,payload})=>window.SWYRL_ENGINE_SHEEP_TAG.command(action,payload),{action,payload});
 const click=async id=>{await page.locator('#'+id)[mode==='phone'?'tap':'click']({force:true});await step(1);};
 await page.goto(base+'/index.html?project=sheep-tag-meadow',{waitUntil:'domcontentloaded'});
 await page.waitForFunction(()=>window.SWYRL_ENGINE_AGENT?.project().canonicalId==='sheep-tag-meadow');
 assert.equal(await page.evaluate(()=>window.SWRLZ_FORGE_BUILD.version),'v11.78');
 await page.locator('#perfPreset').selectOption('medium',{force:true});await page.evaluate(()=>window.courierClock.freeze());
 const canonical=await snap();assert.equal(canonical.scene.actors.filter(a=>a.type==='st-wolf').length,3);
 await click('playBtn');
 await page.waitForFunction(()=>window.SWYRL_ENGINE_SHEEP_TAG.renderStatus().units.filter(u=>u.kind==='wolf').every(u=>u.visualTextures?.length===2&&u.visualTextures.every(t=>t.width===4096&&t.height===4096)));
 const hunters=(await render()).units.filter(u=>u.kind==='wolf');
 assert.equal(hunters.length,3);
 for(const hunter of hunters){assert.equal(hunter.visualModel,'comet-courier');assert.equal(hunter.visualMeshes,106);assert.equal(hunter.visualTriangles,274980);assert.equal(hunter.visualPivots.length,6);assert.ok(hunter.visualPivots.every(p=>p.children>0));assert.ok(hunter.bounds[1]>1.8&&hunter.bounds[1]<2.5);}
 assert.deepEqual(hunters[0].visualTextures,hunters[1].visualTextures,'Hunter instances must share the actual atlas image sources');
 await page.screenshot({path:out+'/'+mode+'-canonical-match.png'});await click('stStop');
 assert.deepEqual((await snap()).scene.actors,canonical.scene.actors,'Play/Stop changed authored map actors');
 // Old native saves and newly spawned wolves both reconstruct the new visual.
 const id=await page.evaluate(()=>{const id=window.SWYRL_ENGINE_AGENT.spawn('st-wolf',{position:[-8,0,-8],name:'Astra extra hunter'});window.SWYRL_ENGINE_AGENT.bake();return id;});
 const spawned=await snap();assert.equal(spawned.scene.actors.find(a=>a.id===id).type,'st-wolf');
 await page.evaluate(data=>window.SWYRL_ENGINE_AGENT.loadScene(data),spawned);await step(1);
 assert.deepEqual((await snap()).scene.actors,spawned.scene.actors,'Native save/reload changed actor identities or transforms');
 await click('playBtn');assert.equal((await render()).units.find(u=>u.id===id).visualMeshes,106);await click('stStop');
 // A small authored classic fixture isolates real movement/attack/tag behavior.
 const farmId=await page.evaluate(()=>{const id=window.SWYRL_ENGINE_AGENT.spawn('st-farm',{position:[30,0,30]});window.SWYRL_ENGINE_AGENT.bake();return id;});
 const farmPrototype=(await snap()).scene.actors.find(a=>a.id===farmId);
 const fixture=structuredClone(canonical),first=type=>type==='st-farm'?farmPrototype:canonical.scene.actors.find(a=>a.type===type);
 const piece=(type,id,position)=>({...structuredClone(first(type)),id,name:id,position,rotation:[0,0,0],scale:[1,1,1],baked:true,visible:true});
 fixture.scene.actors=[piece('st-meadow','ground',[0,0,0]),piece('st-pen','pen',[20,0,20]),piece('st-wolf','hunter',[0,0,0]),piece('st-sheep','runner',[0,0,7]),piece('st-farm','target-farm',[4,0,0])];
 fixture.project.sheepTag={...fixture.project.sheepTag,preset:'classic',role:'wolf',headstart:0,fogMode:'off',wolfSpeed:8,sheepSpeed:1,wolfDamage:200,thorns:false,totems:false,elevated:false,split:false,events:false,duration:300};
 await page.evaluate(data=>window.SWYRL_ENGINE_AGENT.loadScene(data),fixture);await step(1);await click('playBtn');
 assert.equal((await state()).controlledId,'hunter');assert.equal((await command('move',{x:0,z:2})).ok,true);await step(4);
 const walking=(await render()).units.find(u=>u.id==='hunter'),moved=(await state()).units.find(u=>u.id==='hunter');
 assert.ok(moved.pos[2]>.5,'Actual hunter did not move');
 assert.ok(walking.visualPivots.filter(p=>p.name.startsWith('stLeg')).every(p=>Math.abs(p.rotation[0])>.02),'Four leg meshes did not animate');
 const leg=Object.fromEntries(walking.visualPivots.map(p=>[p.name,p.rotation[0]]));assert.ok(leg.stLeg0*leg.stLeg3>0&&leg.stLeg0*leg.stLeg1<0,'Diagonal gait phase is broken');
 const attack=await command('attack',{id:'target-farm'});assert.equal(attack.ok,true,JSON.stringify(attack));
 let hit=false,headAnimated=false;
 for(let n=0;n<60&&!hit;n+=2){await step(2);const s=await state();hit=s.attacks.some(a=>a.buildingId==='target-farm')||!s.buildings.some(b=>b.id==='target-farm');const h=(await render()).units.find(u=>u.id==='hunter');headAnimated ||= Math.abs(h.visualPivots.find(p=>p.name==='stHead').rotation[0])>.01;}
 assert.ok(hit,'Hunter attack no longer damages buildings');assert.ok(headAnimated,'Hunter head attack joint stayed still');
 await page.evaluate(()=>window.SWYRL_ENGINE_SHEEP_TAG.focus(window.SWYRL_ENGINE_SHEEP_TAG.status().units.find(u=>u.id==='hunter').pos));
 await page.screenshot({path:out+'/'+mode+'-courier-hunter.png'});
 assert.equal((await command('attack',{id:'runner'})).ok,true);
 let tagged=false;for(let n=0;n<160&&!tagged;n+=4){await step(4);tagged=(await state()).units.find(u=>u.id==='runner').captured;}
 assert.ok(tagged,'Courier hunter can no longer tag a sheep');await click('stStop');
 assert.deepEqual((await snap()).scene.actors,fixture.scene.actors,'Stop failed to restore authored transforms');
 await click('playBtn');assert.ok((await render()).units.find(u=>u.id==='hunter').visualPivots.filter(p=>p.name.startsWith('stLeg')).every(p=>Math.abs(p.rotation[0])<.0001),'Restart retained gait rotations');await click('stStop');
 // The independent editable model remains available after gameplay.
 await page.evaluate(()=>window.SWYRL_ENGINE_AGENT.createProject('comet-courier'));await step(1);
 assert.equal((await snap()).project.modelAtelier.parts.length,106);assert.equal((await snap()).project.modelAtelier.meshGroups.length,6);
 await page.evaluate(()=>window.SWYRL_ENGINE_AGENT.createProject('sheep-tag-meadow'));await step(1);await click('playBtn');
 assert.equal((await render()).units.filter(u=>u.kind==='wolf'&&u.visualMeshes===106).length,3);await click('stStop');
 assert.deepEqual(errors,[]);receipts.push({mode,hunters:3,meshes:106,triangles:274980,textures:hunters[0].visualTextures,checks:['4K images','shared resources','native spawn/save/reload','four-leg diagonal gait','movement','building damage/head attack','sheep capture','Stop/restart','independent model project'],errors});
 console.log('SHEEP_COURIER_GAMEPLAY_PASS',mode);await context.close();
}}finally{await browser.close();}
await writeFile(out+'/receipt.json',JSON.stringify(receipts,null,2)+'\n');
