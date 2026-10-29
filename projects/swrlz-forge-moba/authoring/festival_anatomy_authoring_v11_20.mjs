import {chromium} from 'playwright';
import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
const base=(process.env.SWYRL_ANIME_TEST_URL||'http://127.0.0.1:8785').replace(/\/$/,''),out=process.env.SWYRL_ANATOMY_OUT||'anatomical-head-evidence';
await fs.mkdir(out,{recursive:true});
const browser=await chromium.launch({headless:true,...(process.env.SWYRL_CHROMIUM_PATH?{executablePath:process.env.SWYRL_CHROMIUM_PATH}:{}),args:['--no-sandbox','--disable-dev-shm-usage','--enable-webgl','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader']});
const page=await browser.newPage({viewport:{width:1024,height:800},acceptDownloads:true}),errors=[],operations=[];
page.setDefaultTimeout(90000);page.on('pageerror',e=>errors.push(e.message));
const snap=()=>page.evaluate(()=>window.SWYRL_ENGINE_AGENT.inspectScene()),pick=id=>page.locator('#modelAtelierParts').selectOption(id),hit=id=>page.locator('#modelAtelier'+id).click();
const part=async id=>(await snap()).project.modelAtelier.parts.find(p=>p.id===id);
const record=o=>{operations.push(o);console.log('NATIVE_ANATOMICAL_EDIT',JSON.stringify(o));};
const field=async(id,v)=>{const e=page.locator('#modelAtelier'+id);await e.fill(String(v));await e.dispatchEvent('change');};
const transform=async(id,values)=>{await pick(id);for(const [k,v]of Object.entries(values))if(Array.isArray(v)){for(let i=0;i<3;i++)await field(k+i,v[i]);}else await field(k==='color'?'Color':k,v);record({id,transform:values});};
const shape=async(id,path,radii)=>{await pick(id);await page.locator('#modelAtelierLoftPath').fill(JSON.stringify(path));await page.locator('#modelAtelierLoftRadii').fill(JSON.stringify(radii));await hit('ApplyLoft');assert.deepEqual((await part(id)).path,path);record({id,path,radii});};
const fitFace=async(id,offset)=>{await pick(id);await page.locator('#modelAtelierFaceFitOffset').fill(String(offset));await hit('FaceFit');assert.equal((await part(id)).path.length,33);record({id,fitTo:'model-0001',offset});};
// A floating dock/mobile rail can cover the old hard-coded bottom-right click.
// Select a *visible* canvas location so the historical authoring test exercises
// genuine pointer input without bypassing the overlay or forcing the click.
const clearByVisibleCanvas=async()=>{
 const canvas=page.locator('#modelAtelierViewport canvas');
 const position=await canvas.evaluate(el=>{
  const r=el.getBoundingClientRect();
  for(const [fx,fy] of [[.12,.30],[.77,.22],[.18,.56],[.72,.55],[.50,.45],[.40,.75]]){
   const x=Math.round(r.width*fx),y=Math.round(r.height*fy);
   if(el.ownerDocument.elementFromPoint(r.left+x,r.top+y)===el)return{x,y};
  }
  return null;
 });
 assert.ok(position,'Viewport canvas must have an unobstructed point for native pointer capture');
 await canvas.click({position});
};
const capture=async(name,view,selected)=>{const old=page.viewportSize();if(old.width>750)await page.setViewportSize({width:1440,height:1100});await page.evaluate(v=>window.SWYRL_ENGINE_MODEL_ATELIER.view(v),view);if(selected){await pick(selected);await hit('FrameSelected');}else await clearByVisibleCanvas();await page.screenshot({path:out+'/'+name+'.png'});if(old.width>750)await page.setViewportSize(old);};
try{
 await page.goto(base+'/?project=model-atelier',{waitUntil:'domcontentloaded',timeout:90000});await page.locator('#modelAtelierPanel canvas').waitFor();
 const seed=(await snap()).project.modelAtelier;
 await pick('model-0001');await field('Name','Anatomical head · skull sections, cheekbones and mandible');await hit('HeadAnatomyApply');assert.ok((await part('model-0001')).headAnatomy);record({id:'model-0001',headAnatomy:(await part('model-0001')).headAnatomy});
 for(const [id,path,radii,offset] of [
 ['smile',[[-.058,3.906,.3],[-.021,3.911,.3],[0,3.908,.3],[.021,3.911,.3],[.058,3.912,.3]],[.0004,.0033,.0024,.0033,.0004],.0007],
 ['lower-lip',[[-.057,3.906,.3],[-.018,3.891,.3],[.017,3.892,.3],[.057,3.912,.3]],[.0004,.0045,.0045,.0004],.001],
 ...[['left',-1],['right',1]].map(([side,k])=>[side+'-brow',[[k*.055,4.154,.30],[k*.12,4.168,.30],[k*.192,4.147,.30]],[.0007,.0045,.0006],.0008]),
 [seed.parts.find(p=>p.name.startsWith('Mouth opening')).id,[[-.055,3.906,.3],[-.021,3.901,.3],[0,3.900,.3],[.021,3.902,.3],[.055,3.912,.3]],[.0004,.007,.006,.007,.0004],.0015],
 [seed.parts.find(p=>p.name.startsWith('Upper teeth')).id,[[-.026,3.903,.3],[0,3.904,.3],[.026,3.906,.3]],[.00035,.0011,.00035],.0045]
 ]){await shape(id,path,radii);await fitFace(id,offset);}
 await shape('model-0002',[[0,3.94,-.005],[0,3.77,.005],[0,3.60,.01],[0,3.50,0],[0,3.43,0],[0,3.38,0]],[.105,.095,.112,.158,.25,.28]);
 const download=page.waitForEvent('download');await hit('Export');await(await download).saveAs(out+'/authored.model.json');
 const saved=JSON.parse(await fs.readFile(out+'/authored.model.json','utf8'));assert.deepEqual(saved.model,(await snap()).project.modelAtelier);if(seed.parts.find(p=>p.id==='model-0001').headAnatomy)assert.deepEqual(saved.model,seed,'Native section recipe must exactly reproduce the saved starter');
 await page.locator('#modelAtelierImportFile').setInputFiles(out+'/authored.model.json');await page.waitForFunction(()=>document.getElementById('modelAtelierStatus').textContent.startsWith('Validated model,'));assert.deepEqual(saved.model,(await snap()).project.modelAtelier);
 await fs.writeFile(out+'/authored.swyrl.json',JSON.stringify(await snap(),null,2)+'\n');
 for(const side of ['left','right'])assert.deepEqual((await part('atelier-v118-'+side+'-leg')),seed.parts.find(p=>p.id==='atelier-v118-'+side+'-leg'));
 await capture('portrait-front','front','model-0001');await capture('portrait-profile','right','model-0001');await capture('portrait-three','three','model-0001');
 await capture('model-three','three');await capture('model-back','back');
 await capture('portrait-three','three','model-0001');
 const png=page.waitForEvent('download');await hit('RenderPNG');await(await png).saveAs(out+'/portrait-studio-2k.png');
 await page.setViewportSize({width:412,height:915});await capture('phone-front','front');await capture('phone-profile','right');
 assert.deepEqual(errors,[]);await fs.writeFile(out+'/receipt.json',JSON.stringify({operations,nativeRoundTrip:true,density:await page.evaluate(()=>window.SWYRL_ENGINE_MODEL_ATELIER.density())},null,2));console.log('ANATOMICAL_HEAD_NATIVE_PASS');
}finally{await browser.close();}
