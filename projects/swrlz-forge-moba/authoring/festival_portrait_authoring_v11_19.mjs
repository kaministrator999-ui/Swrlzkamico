import {chromium} from 'playwright';
import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
const base=(process.env.SWYRL_ANIME_TEST_URL||'http://127.0.0.1:8784').replace(/\/$/,''),out=process.env.SWYRL_PORTRAIT_OUT||'portrait-body-evidence';
const stage=process.env.SWYRL_PORTRAIT_STAGE||'full';
await fs.mkdir(out,{recursive:true});
const browser=await chromium.launch({headless:true,...(process.env.SWYRL_CHROMIUM_PATH?{executablePath:process.env.SWYRL_CHROMIUM_PATH}:{}),args:['--no-sandbox','--disable-dev-shm-usage','--enable-webgl','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader']});
const page=await browser.newPage({viewport:{width:1024,height:800},acceptDownloads:true}),errors=[],operations=[];
page.setDefaultTimeout(90000);page.on('pageerror',e=>errors.push(e.message));
const snap=()=>page.evaluate(()=>window.SWYRL_ENGINE_AGENT.inspectScene()),pick=id=>page.locator('#modelAtelierParts').selectOption(id),hit=id=>page.locator('#modelAtelier'+id).click();
const part=async id=>(await snap()).project.modelAtelier.parts.find(p=>p.id===id);
const record=o=>{operations.push(o);console.log('NATIVE_PORTRAIT_EDIT',JSON.stringify(o));};
const field=async(id,v)=>{const e=page.locator('#modelAtelier'+id);await e.fill(String(v));await e.dispatchEvent('change');};
const transform=async(id,values)=>{await pick(id);for(const [k,v]of Object.entries(values))if(Array.isArray(v)){for(let i=0;i<3;i++)await field(k+i,v[i]);}else await field(k==='color'?'Color':k,v);record({id,transform:values});};
const shape=async(id,path,radii)=>{await pick(id);await page.locator('#modelAtelierLoftPath').fill(JSON.stringify(path));await page.locator('#modelAtelierLoftRadii').fill(JSON.stringify(radii));await hit('ApplyLoft');assert.deepEqual((await part(id)).path,path);record({id,path,radii});};
const fitFace=async(id,offset)=>{await pick(id);await page.locator('#modelAtelierFaceFitOffset').fill(String(offset));await hit('FaceFit');assert.equal((await part(id)).path.length,33);record({id,fitTo:'model-0001',offset});};
const cloth=async(id)=>{await pick(id);await page.locator('#modelAtelierPanelCamber').fill('.008');await page.locator('#modelAtelierPanelPleat').fill('.001');await hit('SurfaceApply');await page.locator('#modelAtelierHDRelief').fill('.2');await hit('HDApply');record({id,panelCamber:.008,panelPleat:.001,relief:.2});};
const capture=async(name,view,selected)=>{const old=page.viewportSize();if(old.width>750)await page.setViewportSize({width:1440,height:1100});await page.evaluate(v=>window.SWYRL_ENGINE_MODEL_ATELIER.view(v),view);if(selected){await pick(selected);await hit('FrameSelected');}else await page.locator('#modelAtelierViewport canvas').click({position:{x:10,y:10}});await page.screenshot({path:out+'/'+name+'.png'});if(old.width>750)await page.setViewportSize(old);};
try{
 await page.goto(base+'/?project=model-atelier',{waitUntil:'domcontentloaded',timeout:90000});await page.locator('#modelAtelierPanel canvas').waitFor();
 if(process.env.SWYRL_PORTRAIT_INPUT){await page.locator('#modelAtelierImportFile').setInputFiles(process.env.SWYRL_PORTRAIT_INPUT);await page.waitForFunction(()=>document.getElementById('modelAtelierStatus').textContent.startsWith('Validated model,'));}
 const seed=(await snap()).project.modelAtelier;
 if(stage==='full'){
 await transform('model-0001',{scale:[.285,.346,.26],color:'#f6cbc1'});
 await page.locator('#modelAtelierJawTaper').fill('.32');await hit('SurfaceApply');
 for(const [id,v]of [['FaceNose',.04],['FaceSocket',.045],['FaceCheek',.06]])await page.locator('#modelAtelier'+id).fill(String(v));await hit('DensityApply');
 for(const [id,v]of [['ChinLift',.16],['NoseDefinition',.65],['SkinWarmth',.70]])await page.locator('#modelAtelier'+id).fill(String(v));await hit('PortraitApply');
 assert.deepEqual((await part('model-0001')).portraitFinish,{chinLift:.16,noseDefinition:.65,warmth:.70});record({id:'model-0001',jawTaper:.32,nose:.04,socket:.045,cheek:.06,portraitFinish:{chinLift:.16,noseDefinition:.65,warmth:.70}});
 for(const [side,s]of [['left',-1],['right',1]]){
  await transform(side+'-sclera',{position:[s*.120,4.067,.295],scale:[.085,.047,.023]});
  await transform(side+'-iris',{position:[s*.120,4.066,.321],scale:[.030,.035,.016]});
  await transform(side+'-eye-catch',{position:[s*.130,4.081,.334],scale:[.006,.007,.006]});
  await transform(side+'-eye-catch2',{position:[s*.110,4.050,.334],scale:[.006,.006,.006]});
  await shape(side+'-upper-lid',[[s*.034,4.065,.308],[s*.078,4.103,.315],[s*.14,4.108,.302],[s*.201,4.084,.281],[s*.219,4.096,.265]],[.0006,.0028,.0033,.0025,.0004]);
  await shape(side+'-lower-lid',[[s*.04,4.059,.310],[s*.12,4.030,.315],[s*.20,4.061,.282]],[.0005,.0018,.0005]);
  await transform(side+'-upper-lid',{color:'#352832'});await transform(side+'-lower-lid',{color:'#c78686'});
  await shape(side+'-brow',[[s*.055,4.154,.30],[s*.12,4.168,.30],[s*.192,4.147,.30]],[.0007,.0045,.0006]);await transform(side+'-brow',{color:'#704843'});await fitFace(side+'-brow',.0008);
  for(let i=0;i<3;i++)await shape(side+'-lash-'+i,[[s*(.200+i*.005),4.089-i*.002,.282-i*.002],[s*(.222+i*.006),4.107-i*.003,.264]],[.0024,.00035]);
 }
 await shape('smile',[[-.058,3.906,.3],[-.021,3.911,.3],[0,3.908,.3],[.021,3.911,.3],[.058,3.912,.3]],[.0004,.0033,.0024,.0033,.0004]);await transform('smile',{color:'#b95f6a'});await fitFace('smile',.0007);
 await shape('lower-lip',[[-.057,3.906,.3],[-.018,3.891,.3],[.017,3.892,.3],[.057,3.912,.3]],[.0004,.0045,.0045,.0004]);await transform('lower-lip',{color:'#dc8a91'});await fitFace('lower-lip',.001);
 const mouth=seed.parts.find(p=>p.name.startsWith('Mouth opening'));await shape(mouth.id,[[-.055,3.906,.3],[-.021,3.901,.3],[0,3.900,.3],[.021,3.902,.3],[.055,3.912,.3]],[.0004,.007,.006,.007,.0004]);await transform(mouth.id,{color:'#66343e',position:[0,0,.225],scale:[1,1,.25]});await fitFace(mouth.id,.0015);
 await shape('model-0002',[[0,3.77,.025],[0,3.60,.01],[0,3.50,0],[0,3.43,0],[0,3.38,0]],[.105,.112,.158,.25,.28]);
 await transform('model-0002',{scale:[1,1,.72]});
 await shape('model-0003',[[0,3.5,0],[0,3.38,.01],[0,3.23,.02],[0,3.04,0],[0,2.82,0]],[.225,.30,.275,.208,.29]);
 for(const [side,s]of [['left',-1],['right',1]])await shape('arm-'+side,[[s*.19,3.45,0],[s*.36,3.37,0],[s*.59,3.13,.015],[s*.76,2.96,.04],[s*.91,2.81,.075]],[.09,.114,.075,.071,.052]);
 await shape('dark-shoulder',[[0,3.59,-.01],[-.15,3.49,.11],[-.27,3.34,.13],[-.26,3.12,.14]],[.075,.125,.135,.06]);await cloth('dark-shoulder');await cloth('back-shoulder-panel');
 }
 if(stage==='review'){
  await pick('model-0001');await page.locator('#modelAtelierJawTaper').fill('.32');await hit('SurfaceApply');
  for(const [id,v]of [['FaceNose',.04],['FaceSocket',.045],['FaceCheek',.06]])await page.locator('#modelAtelier'+id).fill(String(v));await hit('DensityApply');
  for(const [id,v]of [['ChinLift',.16],['NoseDefinition',.65],['SkinWarmth',.70]])await page.locator('#modelAtelier'+id).fill(String(v));await hit('PortraitApply');record({id:'model-0001',reviewPortrait:true});
  for(const [side,s]of [['left',-1],['right',1]]){await shape(side+'-brow',[[s*.055,4.154,.30],[s*.12,4.168,.30],[s*.192,4.147,.30]],[.0007,.0045,.0006]);await fitFace(side+'-brow',.0008);}
  await shape('smile',[[-.058,3.906,.3],[-.021,3.911,.3],[0,3.908,.3],[.021,3.911,.3],[.058,3.912,.3]],[.0004,.0033,.0024,.0033,.0004]);await fitFace('smile',.0007);
  await shape('lower-lip',[[-.057,3.906,.3],[-.018,3.891,.3],[.017,3.892,.3],[.057,3.912,.3]],[.0004,.0045,.0045,.0004]);await fitFace('lower-lip',.001);
  const mouth=seed.parts.find(p=>p.name.startsWith('Mouth opening'));await shape(mouth.id,[[-.055,3.906,.3],[-.021,3.901,.3],[0,3.900,.3],[.021,3.902,.3],[.055,3.912,.3]],[.0004,.007,.006,.007,.0004]);await transform(mouth.id,{color:'#66343e',position:[0,0,.225],scale:[1,1,.25]});await fitFace(mouth.id,.0015);
  await transform('model-0002',{scale:[1,1,.72]});for(const [side,s]of [['left',-1],['right',1]])await shape('arm-'+side,[[s*.19,3.45,0],[s*.36,3.37,0],[s*.59,3.13,.015],[s*.76,2.96,.04],[s*.91,2.81,.075]],[.09,.114,.075,.071,.052]);
 }
 if(stage!=='shoulder'){const teeth=seed.parts.find(p=>p.name.startsWith('Upper teeth'));await shape(teeth.id,[[-.026,3.903,.3],[0,3.904,.3],[.026,3.906,.3]],[.00035,.0011,.00035]);await transform(teeth.id,{color:'#f2d9c6',position:[0,0,.225],scale:[1,1,.25]});await fitFace(teeth.id,.0045);}
 if(stage==='shoulder')for(const [side,s]of [['left',-1],['right',1]])await shape('arm-'+side,[[s*.19,3.45,0],[s*.36,3.37,0],[s*.59,3.13,.015],[s*.76,2.96,.04],[s*.91,2.81,.075]],[.09,.114,.075,.071,.052]);
 for(const side of ['left','right']){
  const id='atelier-v118-'+side+'-leg';assert.deepEqual(await part(id),seed.parts.find(p=>p.id===id),'Existing calf sculpt must be preserved');
 }
 const download=page.waitForEvent('download');await hit('Export');await(await download).saveAs(out+'/authored.model.json');
 const saved=JSON.parse(await fs.readFile(out+'/authored.model.json','utf8'));assert.deepEqual(saved.model,(await snap()).project.modelAtelier);
 if(stage==='full'&&seed.parts[0].portraitFinish)assert.deepEqual(saved.model,seed,'The native recipe must exactly reproduce the saved starter');
 await page.locator('#modelAtelierImportFile').setInputFiles(out+'/authored.model.json');await page.waitForFunction(()=>document.getElementById('modelAtelierStatus').textContent.startsWith('Validated model,'));assert.deepEqual(saved.model,(await snap()).project.modelAtelier);
 await fs.writeFile(out+'/authored.swyrl.json',JSON.stringify(await snap(),null,2)+'\n');
 const density=await page.evaluate(()=>window.SWYRL_ENGINE_MODEL_ATELIER.density());
 for(const view of (['teeth','shoulder'].includes(stage)?['three']:['front','three','right','left','back']))await capture('model-'+view,view);
 if(stage!=='shoulder'){await capture('portrait-detail','three','model-0001');const png=page.waitForEvent('download');await hit('RenderPNG');await(await png).saveAs(out+'/portrait-studio-2k.png');
 await capture('portrait-front','front','model-0001');await capture('portrait-profile','right','model-0001');}
 await capture('body-detail','three','model-0003');
 await page.setViewportSize({width:412,height:915});await capture('phone-front','front');await capture('phone-profile','right');
 assert.deepEqual(errors,[]);await fs.writeFile(out+'/receipt.json',JSON.stringify({operations,nativeRoundTrip:true,parts:saved.model.parts.length,density,errors},null,2)+'\n');console.log('PORTRAIT_NATIVE_AUTHORING_PASS',saved.model.parts.length,density.totalTriangles);
}finally{await browser.close();}
