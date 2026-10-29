import {chromium} from 'playwright';
import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
const base=(process.env.SWYRL_ANIME_TEST_URL||'http://127.0.0.1:8783').replace(/\/$/,''),out=process.env.SWYRL_REFERENCE_OUT||'reference-character-evidence',stage=process.env.SWYRL_REFERENCE_STAGE||'full';
await fs.mkdir(out,{recursive:true});
const browser=await chromium.launch({headless:true,...(process.env.SWYRL_CHROMIUM_PATH?{executablePath:process.env.SWYRL_CHROMIUM_PATH}:{}),args:['--no-sandbox','--disable-dev-shm-usage','--enable-webgl','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader']});
const page=await browser.newPage({viewport:{width:1024,height:800},acceptDownloads:true}),errors=[],operations=[];
page.setDefaultTimeout(90000);page.on('pageerror',e=>errors.push(e.message));
const snap=()=>page.evaluate(()=>window.SWYRL_ENGINE_AGENT.inspectScene());
const part=async id=>(await snap()).project.modelAtelier.parts.find(p=>p.id===id);
const pick=id=>page.locator('#modelAtelierParts').selectOption(id);
const hit=id=>page.locator('#modelAtelier'+id).click();
const field=async(id,v)=>{const n=page.locator('#modelAtelier'+id);await n.fill(String(v));await n.dispatchEvent('change');};
const record=o=>{operations.push(o);console.log('NATIVE_REFERENCE_EDIT',JSON.stringify(o));};
const transform=async(id,values)=>{await pick(id);for(const [k,v]of Object.entries(values)){if(Array.isArray(v)){for(let i=0;i<3;i++)await field(k+i,v[i]);}else await field(k==='color'?'Color':k==='name'?'Name':k,v);}record({id,transform:values});};
const shape=async(id,path,radii)=>{await pick(id);await page.locator('#modelAtelierLoftPath').fill(JSON.stringify(path));await page.locator('#modelAtelierLoftRadii').fill(JSON.stringify(radii));await hit('ApplyLoft');assert.deepEqual((await part(id)).path,path);record({id,path,radii});};
const finish=async(id,style,relief)=>{await pick(id);await page.locator('#modelAtelierHDStyle').selectOption(style);await page.locator('#modelAtelierHDRelief').fill(String(relief));await hit('HDApply');assert.equal((await part(id)).hdFinish.style,style);record({id,style,relief});};
const cloth=async(id,camber,pleat)=>{await pick(id);await page.locator('#modelAtelierPanelCamber').fill(String(camber));await page.locator('#modelAtelierPanelPleat').fill(String(pleat));await hit('SurfaceApply');assert.equal((await part(id)).panelCamber,camber);record({id,panelCamber:camber,panelPleat:pleat});};
const fit=async(id,u,radius)=>{await pick(id);const d=page.locator('#modelAtelierHDEditor details');if(!await d.evaluate(e=>e.open))await d.locator('summary').click();await page.locator('#modelAtelierHDTrimPanel').selectOption('v119-wrap');await page.locator('#modelAtelierHDTrimU').fill(String(u));await page.locator('#modelAtelierHDTrimStart').fill('.12');await page.locator('#modelAtelierHDTrimRadius').fill(String(radius));await hit('HDFitTrim');assert.equal((await part(id)).path.length,33);record({id,fitTo:'v119-wrap',u,start:.12,radius});};
const tailor=async()=>{await cloth('chest-coral',.004,.0016);await finish('chest-coral','cloth',.2);await shape('v119-wrap',[[-.22,3.39,.16],[-.11,3.27,.232],[.07,3.12,.20],[.18,2.97,.13]],[.065,.17,.18,.065]);await cloth('v119-wrap',.008,.002);await finish('chest-gold','skin',.25);await fit('chest-gold',.6,.0025);await fit('bodice-stitch-0',-.6,.0014);};
const calves=async()=>{for(const side of ['left','right']){const id='atelier-v118-'+side+'-leg';await pick(id);await page.locator('#modelAtelierCalfFullness').fill('.065');await page.locator('#modelAtelierShinTaper').fill('.012');await hit('LegApply');assert.deepEqual((await part(id)).legAnatomy,{calfFullness:.065,shinTaper:.012});record({id,legAnatomy:{calfFullness:.065,shinTaper:.012}});}};
const colorInput=(id,value)=>page.locator('#modelAtelier'+id).evaluate((e,v)=>{e.value=v;e.dispatchEvent(new Event('input',{bubbles:true}));e.dispatchEvent(new Event('change',{bubbles:true}));},value);
const capture=async(name,view,selected)=>{const editing=page.viewportSize();if(editing.width>750)await page.setViewportSize({width:1440,height:1100});await page.evaluate(v=>window.SWYRL_ENGINE_MODEL_ATELIER.view(v),view);if(selected){await pick(selected);await hit('FrameSelected');}else await page.locator('#modelAtelierViewport canvas').click({position:{x:10,y:10}});await page.screenshot({path:out+'/'+name+'.png'});if(editing.width>750)await page.setViewportSize(editing);};
try{
 await page.goto(base+'/?project=model-atelier',{waitUntil:'domcontentloaded',timeout:90000});await page.locator('#modelAtelierPanel canvas').waitFor();
 if(process.env.SWYRL_REFERENCE_INPUT){await page.locator('#modelAtelierImportFile').setInputFiles(process.env.SWYRL_REFERENCE_INPUT);await page.waitForFunction(()=>document.getElementById('modelAtelierStatus').textContent.startsWith('Validated model,'));}
 const seed=(await snap()).project.modelAtelier;
 if(!['review','fabric','calves'].includes(stage)){
 await capture('before-profile','right');
 for(const [side,sign]of [['left',-1],['right',1]]){
  const xs=[.245,.31,.414,.45,.555,.64],ys=[2.53,2.17,1.66,1.49,.95,.49],zs=[0,.012,.035,.038,.027,.035];
  await shape('atelier-v118-'+side+'-leg',xs.map((x,i)=>[sign*x,ys[i],zs[i]]),[.164,.151,.106,.105,.100,.066]);
 }
 await calves();
 await capture('corrected-profile','right');await capture('corrected-opposite-profile','left');
 if(stage!=='legs'){
  await transform('model-0001',{scale:[.292,.346,.26]});await pick('model-0001');await page.locator('#modelAtelierJawTaper').fill('.36');await hit('SurfaceApply');
  await page.locator('#modelAtelierFaceNose').fill('.075');await page.locator('#modelAtelierFaceCheek').fill('.04');await hit('DensityApply');record({id:'model-0001',jawTaper:.36,nose:.075,cheek:.04});
  for(const [side,s]of [['left',-1],['right',1]]){
   await transform(side+'-sclera',{position:[s*.122,4.061,.295],scale:[.090,.042,.023]});
   await transform(side+'-iris',{position:[s*.121,4.060,.321],scale:[.030,.034,.016]});
   await colorInput('IrisUpper','#6d3439');await colorInput('IrisLower','#d9a34f');await hit('IrisApply');assert.deepEqual((await part(side+'-iris')).irisPigments,{upper:'#6d3439',lower:'#d9a34f'});record({id:side+'-iris',irisPigments:{upper:'#6d3439',lower:'#d9a34f'}});
   await transform(side+'-eye-catch',{position:[s*.130,4.076,.334],scale:[.008,.009,.006]});await transform(side+'-eye-catch2',{position:[s*.110,4.044,.334],scale:[.0035,.004,.004]});
   await shape(side+'-upper-lid',[[s*.032,4.059,.309],[s*.078,4.091,.317],[s*.145,4.097,.302],[s*.205,4.078,.281],[s*.221,4.091,.263]],[.001,.004,.0045,.003,.0005]);
   await shape(side+'-lower-lid',[[s*.04,4.052,.312],[s*.12,4.024,.316],[s*.205,4.054,.282]],[.0008,.0025,.0008]);
   await shape(side+'-brow',[[s*.044,4.149,.289],[s*.12,4.166,.282],[s*.200,4.147,.251]],[.001,.0035,.0005]);
   for(let i=0;i<3;i++)await shape(side+'-lash-'+i,[[s*(.201+i*.006),4.086-i*.003,.282-i*.002],[s*(.224+i*.007),4.105-i*.004,.263]],[.0035,.0005]);
   await transform(side+'-ear',{position:[s*.294,3.999,.019]});await transform(side+'-earring',{position:[s*.309,3.921,.062]});
  }
  await shape('smile',[[-.06862,3.912,.284],[-.02444,3.906,.310],[0,3.902,.313],[.02444,3.908,.310],[.06862,3.918,.284]],[.0009,.00495,.0036,.00495,.0009]);
  await shape('lower-lip',[[-.06392,3.912,.285],[0,3.883,.309],[.0658,3.918,.284]],[.0009,.0063,.0009]);
  // The small mouth is an existing independently editable part.
  const mouth=seed.parts.find(p=>p.name.startsWith('Mouth opening'));await shape(mouth.id,[[-.057,3.912,.286],[0,3.899,.306],[.058,3.916,.285]],[.0008,.0048,.0008]);
  await finish('hair-cap','crown',.65);
  await transform('hair-cap',{color:'#25b9c8'});await pick('hair-cap');await colorInput('DyeAccent','#ed6159');await hit('SurfaceApply');record({id:'hair-cap',dyeAccent:'#ed6159'});
  for(const s of [-1,1]){
   await finish('hair-bun-'+s,'knot',.8);await transform('hair-bun-'+s,{scale:[.15,.145,.14],color:'#292433'});
   for(let j=0;j<7;j++){
    const path=[[s*(.010+j*.028)-(s===1?.03:0),4.445-j*.004,.085],[s*(.044+j*.027)-(s===1?.015:0),4.385-j*.004,.213],[s*(.09+j*.025),4.28-j*.006,.310],[s*(.17+j*.021),4.185-j*.015,.308],[s*(.202+j*.020),4.13-j*.021,.265]];
    await shape('hair-front-'+s+'-'+j,path,[.026,.044,.039,.027,.0007]);
   }
  }
  await shape('chest-coral',[[.235,3.46,.15],[.14,3.36,.25],[-.07,3.30,.26],[-.25,3.27,.16]],[.045,.064,.062,.026]);
  await shape('v119-wrap',[[-.22,3.39,.16],[-.11,3.27,.232],[.09,3.12,.235],[.20,2.97,.18]],[.065,.17,.18,.065]);
  const loop=(y,r)=>Array.from({length:21},(_,i)=>{const a=i/20*Math.PI*2;return [Math.cos(a)*r,y,.018+Math.sin(a)*r*.84];});
  await shape('bodice-stitch-2',[[0,3.68,.020],[0,3.61,.015]],[.114,.118]);await transform('bodice-stitch-2',{name:'Black fitted neck collar',color:'#20232e',scale:[1,1,.84]});
  await shape('bodice-stitch-1',loop(3.61,.123),Array(21).fill(.005));await transform('bodice-stitch-1',{name:'Coral collar piping',color:'#f26958'});
  const stripes=[[[.625,3.10,.02],[.710,3.01,.031]],[ [.711,3.009,.031],[.807,2.910,.052] ],[[.808,2.909,.052],[.886,2.833,.070]]];
  for(let i=0;i<3;i++){await shape('right-wrist-'+i,stripes[i],[[.086,.080],[.079,.068],[.068,.056]][i]);await transform('right-wrist-'+i,{color:i===1?'#2cc8d0':'#ee6456'});}
  await tailor();
 }
 }
 if(stage==='review'){await shape('bodice-stitch-2',[[0,3.68,.020],[0,3.61,.015]],[.114,.118]);await transform('bodice-stitch-2',{name:'Black fitted neck collar',color:'#20232e',scale:[1,1,.84]});}
 if(stage==='fabric')await tailor();
 if(stage==='calves')await calves();
 const waiting=page.waitForEvent('download');await hit('Export');await(await waiting).saveAs(out+'/authored.model.json');
 const saved=JSON.parse(await fs.readFile(out+'/authored.model.json','utf8'));assert.deepEqual(saved.model,(await snap()).project.modelAtelier);
 if(stage==='full'&&seed.parts.find(p=>p.id==='hair-cap').hdFinish?.style==='crown')assert.deepEqual(saved.model,seed,'The native recipe must exactly reproduce the saved starter');
 await page.locator('#modelAtelierImportFile').setInputFiles(out+'/authored.model.json');await page.waitForFunction(()=>document.getElementById('modelAtelierStatus').textContent.startsWith('Validated model,'));assert.deepEqual(saved.model,(await snap()).project.modelAtelier);
 await fs.writeFile(out+'/authored.swyrl.json',JSON.stringify(await snap(),null,2)+'\n');
 const density=await page.evaluate(()=>window.SWYRL_ENGINE_MODEL_ATELIER.density());
 for(const view of ['front','three','right','left','back'])await capture('model-'+view,view);
 await capture('face-detail','three','model-0001');const png=page.waitForEvent('download');await hit('RenderPNG');await(await png).saveAs(out+'/portrait-studio-2k.png');
 await capture('leg-detail','right','atelier-v118-right-leg');await capture('wrap-detail','three','hair-bun-1');await capture('bodice-detail','three','model-0003');
 await page.setViewportSize({width:412,height:915});await capture('phone-front','front');await capture('phone-profile','right');
 assert.deepEqual(errors,[]);await fs.writeFile(out+'/receipt.json',JSON.stringify({operations,nativeRoundTrip:true,parts:saved.model.parts.length,density,errors},null,2)+'\n');
 console.log('REFERENCE_NATIVE_AUTHORING_PASS',saved.model.parts.length,density.totalTriangles);
}finally{await browser.close();}
