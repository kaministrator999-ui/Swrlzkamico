import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {mkdir,writeFile,readFile} from 'node:fs/promises';
const base=process.env.SWYRL_TEST_URL||'http://127.0.0.1:8790',out=process.env.SWYRL_TEST_OUT||'/workspace/sheep-map-tests';await mkdir(out,{recursive:true});
const old=JSON.parse(await readFile(new URL('../scenes/sheep-tag-moonbell-archive.swyrl.json',import.meta.url)));
const browser=await chromium.launch({headless:true,executablePath:process.env.SWYRL_CHROMIUM_PATH||'/usr/bin/chromium',args:['--no-sandbox','--disable-dev-shm-usage','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader']});
const receipts=[];
try{for(const [mode,viewport] of [['desktop',{width:1440,height:1000}],['phone',{width:412,height:915}]]){
 const context=await browser.newContext({viewport,isMobile:mode==='phone',hasTouch:mode==='phone'});
 await context.addInitScript(()=>{
  const raf=requestAnimationFrame.bind(window),cancel=cancelAnimationFrame.bind(window),now=performance.now.bind(performance),queue=new Map();let frozen=false,time=0,serial=1e9;
  Object.defineProperty(performance,'now',{configurable:true,value:()=>frozen?time:now()});
  window.requestAnimationFrame=cb=>{if(!frozen)return raf(cb);const id=serial++;queue.set(id,cb);return id;};
  window.cancelAnimationFrame=id=>{queue.delete(id);cancel(id);};
  window.wildwoodClock={freeze:()=>{frozen=true;time=now();return new Promise(resolve=>raf(()=>raf(resolve)));},step:n=>{for(let i=0;i<n;i++){time+=50;const work=[...queue.values()];queue.clear();if(!work.length)throw Error('Native RAF stopped');for(const cb of work)cb(time);}}};
 });
 const page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(String(e)));page.setDefaultTimeout(60000);
 const snap=()=>page.evaluate(()=>window.SWYRL_ENGINE_AGENT.inspectScene());
 const map=()=>page.evaluate(()=>window.SWYRL_ENGINE_SHEEP_TAG.mapStatus());
 const state=()=>page.evaluate(()=>window.SWYRL_ENGINE_SHEEP_TAG.status());
 const step=n=>page.evaluate(n=>window.wildwoodClock.step(n),n);
 const click=async id=>{await page.locator('#'+id)[mode==='phone'?'tap':'click']({force:true});await step(1);};
 const command=(action,payload={})=>page.evaluate(({action,payload})=>window.SWYRL_ENGINE_SHEEP_TAG.command(action,payload),{action,payload});
 await page.goto(base+'/index.html?project=sheep-tag-meadow',{waitUntil:'domcontentloaded'});
 await page.waitForFunction(()=>window.SWYRL_ENGINE_SHEEP_TAG?.mapStatus().textureSize?.[0]===4096);
 await page.locator('#perfPreset').selectOption('medium',{force:true});await page.evaluate(()=>window.wildwoodClock.freeze());
 assert.equal(await page.evaluate(()=>window.SWRLZ_FORGE_BUILD.version),'v11.79');
 const canonical=await snap(),info=await map();assert.equal(canonical.project.name,'Sheep Tag · Moonbell Wildwood');
 assert.equal(info.bounds,64);assert.deepEqual(info.groundSize,[128,128]);assert.deepEqual(info.textureSize,[4096,4096]);assert.equal(info.layerCount,9);assert.equal(info.regions.length,4);assert.equal(canonical.scene.actors.length,176);
 assert.equal((await page.evaluate(()=>window.SWYRL_ENGINE_SHEEP_TAG.validateStarts())).ok,true);
 const corners=await page.evaluate(()=>[-64,64].flatMap(x=>[-64,64].map(z=>window.SWYRL_ENGINE_SHEEP_TAG.pointScreen(x,z))));assert.ok(corners.every(p=>p.visible),'Expanded editor framing clips a map corner');
 await page.screenshot({path:out+'/'+mode+'-overview.png'});
 // Actual native navigation from all eight build clearings and four outer
 // roads to the sanctuary. These targets reach past the old 40 m bounds.
 const routes=await page.evaluate(()=>{
  const api=window.SWYRL_ENGINE_SHEEP_TAG,points=[...api.project().scene.actors.filter(a=>a.type==='st-sheep').map(a=>a.position),[0,0,-60],[0,0,60],[-60,0,0],[60,0,0]];
  return points.map(from=>{const r=api.previewPath({from,to:[0,0,0],species:'sheep'});return {from,reachable:r.reachable,length:r.length};});
 });assert.ok(routes.every(r=>r.reachable),'A clearing or outer road is disconnected: '+JSON.stringify(routes));
 const passages=await page.evaluate(()=>[[-21,-35],[35,-21],[21,35],[-35,21]].map(([x,z])=>{
  const paths=['sheep','wolf'].map(species=>window.SWYRL_ENGINE_SHEEP_TAG.previewPath({from:[x,z-5],to:[x,z+5],species}));return {center:[x,z],paths:paths.map(p=>({reachable:p.reachable,length:p.length}))};
 }));
 for(const p of passages){assert.ok(p.paths.every(r=>r.reachable),JSON.stringify(p));assert.ok(p.paths[1].length>p.paths[0].length+1,'Hunter fits a sheep-only gap: '+JSON.stringify(p));}
 console.log('WILDWOOD_ROUTE_NETWORK_PASS',mode);
 await page.evaluate(data=>window.SWYRL_ENGINE_AGENT.loadScene(data),canonical);await step(1);
 assert.deepEqual((await snap()).scene.actors,canonical.scene.actors,'Native reload changed the authored map');
 const portable=await page.evaluate(()=>window.SWYRL_ENGINE_SHEEP_TAG_CREATOR.exportMap());assert.equal(portable.ok,true,JSON.stringify(portable.errors));
 assert.equal(portable.map.actors.length,176);assert.equal(portable.map.layers.length,9);assert.equal(portable.map.rules.bounds,64);
 const imported=await page.evaluate(data=>window.SWYRL_ENGINE_SHEEP_TAG_CREATOR.importMap(data),portable.map);assert.equal(imported.ok,true,JSON.stringify(imported));await step(1);
 assert.deepEqual((await map()).groundSize,[128,128]);assert.equal((await snap()).scene.actors.length,176);
 // A creator import without a saved floor regenerates a correctly sized one.
 const floorless=structuredClone(portable.map);floorless.actors=floorless.actors.filter(a=>a.type!=='st-meadow');
 assert.equal((await page.evaluate(data=>window.SWYRL_ENGINE_SHEEP_TAG_CREATOR.importMap(data),floorless)).ok,true);await step(1);assert.deepEqual((await map()).groundSize,[128,128]);
 await page.evaluate(data=>window.SWYRL_ENGINE_AGENT.loadScene(data),canonical);await step(1);
 // Move the actual player inside the newly added western pasture. Use an
 // authored starting fixture, the normal Play button and native move orders.
 const fixture=structuredClone(canonical),player=fixture.scene.actors.find(a=>a.type==='st-sheep');
 player.position=[-48,0,0];fixture.project.sheepTag.headstart=120;fixture.project.sheepTag.fogMode='off';
 // Avoid overlapping the existing western sheep in this authored test fixture.
 fixture.scene.actors=fixture.scene.actors.filter(a=>a.id===player.id||a.type!=='st-sheep');
 await page.evaluate(data=>window.SWYRL_ENGINE_AGENT.loadScene(data),fixture);await step(1);await click('playBtn');
 assert.equal((await state()).active,true);assert.equal((await command('move',{x:-55,z:0})).ok,true);
 await step(4);const moving=(await state()).units.find(u=>u.controlled);assert.ok(moving.pos[0]<-48.5,'Actual sheep did not enter expanded pasture');
 const build=await command('build',{kind:'st-farm',x:-48,z:4.5});assert.equal(build.ok,true,JSON.stringify(build));
 const hunters=await page.evaluate(()=>window.SWYRL_ENGINE_SHEEP_TAG.renderStatus().units.filter(u=>u.kind==='wolf'));assert.equal(hunters.length,3);assert.ok(hunters.every(u=>u.visualMeshes===106),'Astra hunters were lost');
 const ui=await page.evaluate(()=>window.SWYRL_ENGINE_SHEEP_TAG.uiStatus());assert.equal(ui.minimap.terrain,'moonbell-wildwood','Minimap does not use the expanded terrain artwork');
 const vision=await page.evaluate(()=>window.SWYRL_ENGINE_SHEEP_TAG.viewStatus());assert.equal(vision.rules.bounds,64);
 await page.screenshot({path:out+'/'+mode+'-expanded-pasture.png'});await click('stStop');
 assert.deepEqual((await snap()).scene.actors,fixture.scene.actors,'Stop changed native map objects');
 // Historical native saves still retain their 80 m meadow and roster.
 await page.evaluate(data=>window.SWYRL_ENGINE_AGENT.loadScene(data),old);await step(1);assert.equal((await map()).bounds,40);assert.equal((await map()).textureSize,null);assert.equal((await snap()).scene.actors.length,92);
 assert.equal((await page.evaluate(()=>window.SWYRL_ENGINE_SHEEP_TAG.validateStarts())).ok,true);
 assert.deepEqual(errors,[]);receipts.push({mode,map:info,routes,passages,checks:['all spawns valid','map corners framed','all glades and outer roads connected','four sheep-only shortcuts','native save/reload','portable export/import','floor regeneration','real movement/building beyond old bounds','Astra hunters','terrain minimap','Stop restoration','old map compatibility'],errors});
 console.log('SHEEP_WILDWOOD_MAP_PASS',mode);await context.close();
}}finally{await browser.close();}
await writeFile(out+'/receipt.json',JSON.stringify(receipts,null,2)+'\n');
