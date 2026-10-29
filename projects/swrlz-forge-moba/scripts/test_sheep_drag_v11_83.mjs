import {chromium} from 'playwright';import assert from 'node:assert/strict';import {mkdir,writeFile} from 'node:fs/promises';
const base=process.env.SWYRL_TEST_URL||'http://127.0.0.1:8797',out=process.env.SWYRL_TEST_OUT||'/workspace/sheep-drag-tests';await mkdir(out,{recursive:true});
const browser=await chromium.launch({headless:true,executablePath:'/usr/bin/chromium',args:['--no-sandbox','--disable-dev-shm-usage','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader']});const results=[];
try{for(const [mode,viewport,touch] of [['portrait',{width:412,height:915},true],['landscape',{width:915,height:412},true],['desktop',{width:1440,height:1000},false]].filter(x=>!process.env.SWYRL_MODE||x[0]===process.env.SWYRL_MODE)){
 const c=await browser.newContext({viewport,isMobile:touch,hasTouch:touch});await c.addInitScript(()=>{const make=document.createElement.bind(document);window.fogTestCanvases=[];document.createElement=function(...args){const node=make(...args);if(args[0]==='canvas')window.fogTestCanvases.push(node);return node;};});
 await c.addInitScript(()=>{const raf=requestAnimationFrame.bind(window),now=performance.now.bind(performance),queue=new Map();let frozen=false,time=0,serial=1e9;Object.defineProperty(performance,'now',{configurable:true,value:()=>frozen?time:now()});window.requestAnimationFrame=cb=>{if(!frozen)return raf(cb);const id=serial++;queue.set(id,cb);return id;};window.touchClock={freeze:()=>{frozen=true;time=now();return new Promise(r=>raf(()=>raf(r)));},step:n=>{for(let i=0;i<n;i++){time+=50;const work=[...queue.values()];queue.clear();for(const cb of work)cb(time);}}};});
 const page=await c.newPage(),errors=[];page.on('pageerror',e=>errors.push(String(e)));page.setDefaultTimeout(90000);const step=n=>page.evaluate(n=>window.touchClock.step(n),n),api=(method,...args)=>page.evaluate(({method,args})=>window.SWYRL_ENGINE_SHEEP_TAG[method](...args),{method,args});
 const state=()=>api('status'),ui=()=>api('uiStatus'),player=async()=> (await state()).units.find(u=>u.controlled),click=async id=>{await page.locator('#'+id)[touch?'tap':'click']({force:true});await step(1);};
 await page.goto(base+'/index.html?project=sheep-tag-meadow',{waitUntil:'domcontentloaded'});await page.waitForFunction(()=>window.SWYRL_ENGINE_SHEEP_TAG?.mapStatus().textureSize?.[0]===4096);await page.locator('#perfPreset').selectOption('medium',{force:true});await page.evaluate(()=>window.touchClock.freeze());
 const fixture=await page.evaluate(()=>window.SWYRL_ENGINE_AGENT.inspectScene()),sheep=fixture.scene.actors.find(a=>a.type==='st-sheep'),wolf=fixture.scene.actors.find(a=>a.type==='st-wolf');fixture.scene.actors=fixture.scene.actors.filter(a=>!['st-sheep','st-wolf','st-tree','st-rock','st-pond','st-thorn'].includes(a.type));sheep.position=[40,0,0];wolf.position=[-80,0,-80];fixture.scene.actors.push(sheep,wolf);fixture.project.sheepTag.headstart=120;fixture.project.sheepTag.startGold=60;
 await page.evaluate(data=>window.SWYRL_ENGINE_AGENT.loadScene(data),fixture);await step(1);await click('playBtn');assert.equal((await state()).active,true);console.log('TOUCH_BOOT',mode);

 assert.equal((await ui()).movement,'joystick');assert.equal((await ui()).mobileControls.enabled,true);
 const fog=(await ui()).fogDisplay;assert.equal(fog.linear,true);assert.equal(fog.resolution,fog.logicalWidth*4);assert.equal(fog.feather,1.5);
 const fogPixels=await page.evaluate(()=>{const canvas=window.fogTestCanvases.find(c=>c.width===512&&c.height===512&&c.getContext('2d')?.getImageData(0,0,1,1).data[3]===165);if(!canvas)return null;const ctx=canvas.getContext('2d'),alpha=new Set();const data=ctx.getImageData(0,0,512,512).data;for(let i=3;i<data.length;i+=4)alpha.add(data[i]);return {levels:alpha.size,unseen:ctx.getImageData(0,0,1,1).data[3],center:ctx.getImageData(336,256,1,1).data[3],outside:ctx.getImageData(374,256,1,1).data[3]};});assert.ok(fogPixels.levels>30,JSON.stringify(fogPixels));assert.equal(fogPixels.unseen,165);assert.equal(fogPixels.center,0);assert.equal(fogPixels.outside,165);assert.ok(!(await api('viewStatus')).units.some(u=>u.kind==='wolf'));
 const initial=await player(),ground=await api('pointScreen',44,5);
 if(touch)await page.touchscreen.tap(ground.x,ground.y);else await page.mouse.click(ground.x,ground.y);
 await step(8);assert.deepEqual((await player()).pos,initial.pos,'Ground tap moved the sheep');assert.equal((await player()).order,null);
 const session=await c.newCDPSession(page),send=(type,points)=>session.send('Input.dispatchTouchEvent',{type,touchPoints:points.map(p=>({...p,radiusX:9,radiusY:9,force:1}))});
 const box=await page.locator('#stMoveStick').boundingBox(),center={x:box.x+box.width/2,y:box.y+box.height/2,id:1},right={...center,x:center.x+36};
 if(touch)await send('touchStart',[right]);else {await page.mouse.move(right.x,right.y);await page.mouse.down();}
 await step(5);assert.ok((await player()).pos[0]>initial.pos[0]+.5,'Joystick did not move sheep');
 if(!touch)await page.mouse.up();else await send('touchEnd',[]);
 await step(1);const stopPos=(await player()).pos;await step(4);assert.deepEqual((await player()).pos,stopPos,'Joystick release did not stop');
 console.log('JOYSTICK_ONLY_PASS',mode);
 async function drag(kind,worldX,worldZ,{holdStick=false,cancel=false}={}){
  const id={'st-farm':'stBuildFarm','st-income':'stBuildIncome','st-fort':'stBuildFort'}[kind],b=await page.locator('#'+id).boundingBox(),start={x:b.x+b.width/2,y:b.y+b.height/2,id:2};
  const p=await api('pointScreen',worldX,worldZ),aim={x:p.x,y:p.y+(await ui()).touchPlacement.desiredOffsetPx,id:2};
  assert.ok(aim.x>0&&aim.x<viewport.width&&aim.y<viewport.height,JSON.stringify({mode,aim}));
  if(touch){if(holdStick)await send('touchStart',[right]);await send('touchStart',holdStick?[right,start]:[start]);await send('touchMove',holdStick?[right,aim]:[aim]);}
  else {await page.mouse.move(start.x,start.y);await page.mouse.down();await page.mouse.move(aim.x,aim.y,{steps:4});}
  await page.waitForFunction(x=>Math.abs((window.SWYRL_ENGINE_SHEEP_TAG.uiStatus().touchPlacement.rawScreen?.[0]??-999)-x)<.5,aim.x,{polling:50,timeout:10000});
  await step(1);const before=await ui();assert.equal(before.buildDrag.active,true);assert.ok(before.touchPlacement.offsetPx>=70);assert.ok(before.touchPlacement.targetScreen[1]<aim.y-69);
  await page.screenshot({path:out+'/'+mode+'-'+kind+(cancel?'-cancel':'')+'-aim.png'});
  const displayed=(await ui()).touchPlacement.fit;
  if(touch){if(cancel)await send('touchCancel',[]);else await send('touchEnd',holdStick?[aim]:[]);}
  else {if(cancel)await page.evaluate(()=>window.dispatchEvent(new Event('blur')));await page.mouse.up();}
  await step(1);return {displayed,before,after:await ui()};
 }
 // Reject a paid house without spending, then build with the exact 60 balance.
 const px=(await player()).pos[0],rejected=await drag('st-fort',px+2,4.5);assert.equal(rejected.displayed.ok,false);assert.match(rejected.before.touchPlacement.fit.ok?'':await page.locator('#stPlacement').textContent(),/Need 100/);assert.equal((await state()).buildings.length,0);
 await click('stRestart');const income=await drag('st-income',px+2,4.5,{holdStick:touch});assert.equal(income.displayed.ok,true,JSON.stringify(income));assert.equal(income.after.buildDrag.lastResult?.ok,true);assert.equal(income.after.mobileControls.joystick.active,false,'Held joystick overwrote construction');
 const committed=income.after.touchPlacement.lastCommitted;assert.equal(committed.x,income.displayed.x);assert.equal(committed.z,income.displayed.z);
 assert.equal((await state()).gold,60,'Charged before reaching construction site');
 await step(80);let buildings=(await state()).buildings;assert.equal(buildings.length,1,'Accepted drag never constructed a house');assert.equal(buildings[0].kind,'st-income');assert.ok(buildings[0].progress>=1,'Construction never finished');assert.equal(buildings[0].pos[0],committed.x);assert.equal(buildings[0].pos[2],committed.z);assert.ok((await state()).gold<10,'Construction did not charge the 60 gold cost');
 if(touch)await send('touchEnd',[]);await step(1);const afterBuilt=(await player()).pos;await step(2);assert.deepEqual((await player()).pos,afterBuilt,'Old held joystick restarted after building');
 console.log('DIRECT_DRAG_ACTUAL_CONSTRUCTION_EXACT_COST_AND_STICK_OWNERSHIP_PASS',mode);
 const rejectedOccupied=await drag('st-farm',committed.x,committed.z);assert.equal(rejectedOccupied.displayed.ok,false);assert.equal((await state()).buildings.length,1);
 const pos=(await player()).pos;await drag('st-farm',pos[0]+4,3,{cancel:true});await step(10);assert.equal((await state()).buildings.length,1,'Cancelled drag created a house');assert.equal((await ui()).buildDrag.active,false);
 // Visible house taps select without ordering movement.
 await page.locator('#stCancelBuild')[touch?'tap':'click']({force:true});await step(1);const houseScreen=await api('pointScreen',committed.x,committed.z,1.2);
 if(touch)await page.touchscreen.tap(houseScreen.x,houseScreen.y);else await page.mouse.click(houseScreen.x,houseScreen.y);await step(1);assert.equal((await state()).selectedId,buildings[0].id);assert.equal((await player()).order,null);
 await page.screenshot({path:out+'/'+mode+'-built-soft-fog.png'});
 await click('stStop');
 if(mode==='portrait'){
  assert.equal((await api('configure',{startGold:59})).ok,true);await click('playBtn');await page.locator('#stBuildIncome').press('Enter');await step(1);assert.equal((await ui()).touchPlacement.active,false);assert.equal((await ui()).placementGrid.valid,false);assert.match(await page.locator('#stPlacement').textContent(),/Need 60/);
  await step(20);assert.equal((await state()).gold,60);assert.equal((await ui()).placementGrid.valid,true,'Stationary preview stayed red after receiving gold');assert.ok(!(await page.locator('#stPlacement').textContent()).includes('Need 60'));assert.equal((await state()).buildings.length,0);await click('stStop');console.log('STATIONARY_AFFORDABILITY_REFRESH_PASS',mode);
 }
 assert.equal((await ui()).buildDrag.active,false);assert.equal((await ui()).mobileControls.enabled,false);assert.deepEqual((await page.evaluate(()=>window.SWYRL_ENGINE_AGENT.inspectScene())).scene.actors,fixture.scene.actors);assert.deepEqual(errors,[]);
 results.push({mode,groundTapDoesNotMove:true,joystickMovesAndStops:true,directIconDrag:true,actualPaidHouseConstructed:true,exact60GoldAccepted:true,heldStickDoesNotCancelBuild:true,liftedPreviewExactCommit:true,blockedAndCancelledDropsDoNotBuild:true,houseSelection:true,fog,fogPixels,stationaryAffordability:mode==='portrait',errors});await c.close();console.log('SHEEP_DRAG_SOFT_FOG_PASS',mode);
}}finally{await browser.close();}await writeFile(out+'/receipt.json',JSON.stringify(results,null,2)+'\n');
