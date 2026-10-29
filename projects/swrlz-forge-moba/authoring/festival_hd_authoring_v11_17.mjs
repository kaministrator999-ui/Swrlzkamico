import {chromium} from 'playwright';
import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
const base=(process.env.SWYRL_ANIME_TEST_URL||'http://127.0.0.1:8781').replace(/\/$/,''),out=process.env.SWYRL_HD_OUT||'hd-character-evidence',stage=process.env.SWYRL_HD_STAGE||'full';await fs.mkdir(out,{recursive:true});
const browser=await chromium.launch({headless:true,...(process.env.SWYRL_CHROMIUM_PATH?{executablePath:process.env.SWYRL_CHROMIUM_PATH}:{}),args:['--no-sandbox','--disable-dev-shm-usage','--enable-webgl','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader']});
const page=await browser.newPage({viewport:{width:1600,height:1200},acceptDownloads:true}),errors=[],operations=[];page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error'&&/THREE.WebGLProgram|VALIDATE_STATUS|shader error/i.test(m.text()))errors.push(m.text());});page.setDefaultTimeout(90000);
operations.push=(...items)=>{for(const item of items)console.log('NATIVE_EDIT',JSON.stringify(item));return Array.prototype.push.apply(operations,items);};
const snap=()=>page.evaluate(()=>window.SWYRL_ENGINE_AGENT.inspectScene()),parts=async()=>(await snap()).project.modelAtelier.parts;
const hit=async id=>{const n=page.locator('#modelAtelier'+id);await n.click();};
const pick=async id=>{await page.locator('#modelAtelierParts').selectOption(id);};
const val=async(id,value)=>{const n=page.locator('#modelAtelier'+id);await n.fill(String(value));await n.dispatchEvent('change');};
const transform=async(id,values)=>{await pick(id);for(const [key,value]of Object.entries(values)){if(Array.isArray(value)){for(let i=0;i<3;i++)await val(key+i,value[i]);}else await val(key==='name'?'Name':key==='color'?'Color':key,value);}operations.push({id,transform:values});};
const shape=async(id,path,radii)=>{await pick(id);await page.locator('#modelAtelierLoftPath').fill(JSON.stringify(path));await page.locator('#modelAtelierLoftRadii').fill(JSON.stringify(radii));await hit('ApplyLoft');assert.ok(!(await page.locator('#modelAtelierStatus').innerText()).startsWith('Loft rejected:'),id+' spline rejected');assert.deepEqual((await parts()).find(p=>p.id===id).path,path);operations.push({id,path,radii});};
const finish=async(id,style,relief=.7,matching=false)=>{await pick(id);await page.locator('#modelAtelierHDStyle').selectOption(style);await page.locator('#modelAtelierHDRelief').fill(String(relief));await hit(matching?'HDMatch':'HDApply');assert.ok(!(await page.locator('#modelAtelierStatus').innerText()).startsWith('Surface finish rejected:'),id+' '+style);operations.push({id,style,relief,matching});};
const remove=async id=>{if(!(await parts()).some(p=>p.id===id))return;await pick(id);await hit('Delete');operations.push({removed:id});};
const duplicate=async(id,name)=>{const found=(await parts()).find(p=>p.name===name);if(found)return found.id;await pick(id);await hit('Duplicate');const selected=await page.evaluate(()=>window.SWYRL_ENGINE_MODEL_ATELIER.status().selected);await val('Name',name);operations.push({duplicate:id,id:selected,name});return selected;};
const capture=async(name,view='front',selected=null)=>{await page.evaluate(v=>window.SWYRL_ENGINE_MODEL_ATELIER.view(v),view);if(selected){await pick(selected);await hit('FrameSelected');}await page.screenshot({path:out+'/'+name+'.png'});};
try{
 await page.goto(base+'/?project=model-atelier',{waitUntil:'domcontentloaded',timeout:90000});await page.locator('#modelAtelierPanel canvas').waitFor();
 if(process.env.SWYRL_HD_INPUT){await page.locator('#modelAtelierImportFile').setInputFiles(process.env.SWYRL_HD_INPUT);await page.waitForFunction(()=>document.getElementById('modelAtelierStatus').textContent.startsWith('Validated model,'));}
 const bakedSeed=(await snap()).project.modelAtelier;
 if(!['finish','review','polish','hair','sampling','trim'].includes(stage)){
  console.log('HD_FACE_BEGIN');
  for(const side of ['left','right'])for(const suffix of ['iris-ring','iris-gold','pupil','cheek','ear-inner'])await remove(side+'-'+suffix);
  await remove('nose');await remove('nose-tip');
  await finish('model-0001','portrait',.65);await pick('model-0001');await page.locator('#modelAtelierJawTaper').fill('.34');await hit('SurfaceApply');
  await page.locator('#modelAtelierFaceNose').fill('.085');await page.locator('#modelAtelierFaceSocket').fill('.035');await page.locator('#modelAtelierFaceCheek').fill('.045');await hit('DensityApply');await transform('model-0001',{color:'#f8cdc3'});
  for(const [side,s]of [['left',-1],['right',1]]){
   await finish(side+'-sclera','eye',.6);await transform(side+'-sclera',{position:[s*.126,4.059,.296],scale:[.099,.046,.022],rotation:[0,s*.18,s*.05]});
   await finish(side+'-iris','iris',.65);await transform(side+'-iris',{position:[s*.121,4.058,.322],scale:[.034,.038,.016]});
   await finish(side+'-ear','ear',.7);
   await finish(side+'-upper-lid','skin',.4);await shape(side+'-upper-lid',[[s*.032,4.057,.311],[s*.078,4.094,.318],[s*.148,4.103,.302],[s*.217,4.082,.276],[s*.232,4.096,.258]],[.0015,.0045,.005,.003,.0006]);
   await transform(side+'-upper-lid',{color:'#2b1f2b'});
   await finish(side+'-lower-lid','skin',.35);await shape(side+'-lower-lid',[[s*.04,4.049,.314],[s*.125,4.017,.315],[s*.214,4.054,.279]],[.001,.0027,.001]);await transform(side+'-lower-lid',{color:'#bd7f86'});
   await finish(side+'-brow','hair',.25);await shape(side+'-brow',[[s*.044,4.15,.293],[s*.12,4.171,.282],[s*.205,4.15,.249]],[.002,.005,.0007]);
   await transform(side+'-eye-catch',{position:[s*.132,4.077,.335],scale:[.009,.011,.007]});await transform(side+'-eye-catch2',{position:[s*.107,4.04,.335],scale:[.006,.006,.006]});
  }
  await finish('smile','lip',.6);await shape('smile',[[-.073,3.912,.284],[-.026,3.906,.310],[0,3.902,.313],[.026,3.908,.310],[.073,3.918,.284]],[.001,.0055,.004,.005,.001]);await transform('smile',{color:'#a54b62'});
  await finish('lower-lip','lip',.55);await shape('lower-lip',[[-.068,3.912,.285],[0,3.883,.309],[.07,3.918,.284]],[.001,.007,.001]);await transform('lower-lip',{color:'#e8919c'});
  const mouth=await duplicate('smile','Mouth opening · soft smile');await shape(mouth,[[-.061,3.912,.286],[0,3.898,.306],[.062,3.916,.285]],[.0008,.007,.0008]);await transform(mouth,{position:[0,0,0],color:'#4a2238'});
  const teeth=await duplicate('smile','Upper teeth · smile glint');await shape(teeth,[[-.035,3.904,.308],[0,3.902,.313],[.036,3.907,.308]],[.001,.0028,.001]);await transform(teeth,{position:[0,0,0],color:'#fff0db'});
  console.log('HD_FACE_COMPLETE',JSON.stringify(await page.evaluate(()=>window.SWYRL_ENGINE_MODEL_ATELIER.density())).length);
  await capture('face-front','front','model-0001');await capture('face-three','three','model-0001');await capture('face-profile','right','model-0001');
 }
 if(!['face','review','polish','hair','sampling','trim'].includes(stage)){
  console.log('HD_BODY_BEGIN');
  await finish('model-0002','skin',.55,true);await finish('hair-front--1-0','hair',.8,true);await finish('hair-nape-0','hair',.75,true);await finish('portrait-curl--1','hair',.8,true);
  for(const sign of [-1,1]){await finish('hair-bun-'+sign,'wrap',.85);await transform('hair-bun-'+sign,{color:'#292532'});}
  for(const [side,s]of [['left',-1],['right',1]]){
   await transform(side+'-ear',{rotation:[0,s*1.15,s*.06]});
   await shape('portrait-curl-'+s,[[s*.25,4.26,.21],[s*.31,4.08,.16],[s*.325,3.91,.11],[s*.355,3.82,.12],[s*.33,3.78,.17]],[.035,.048,.032,.018,.0015]);
  }
  // Reapply facial loft finishes after the anatomy batch, which shares the original spline category.
  for(const side of ['left','right']){await finish(side+'-brow','hair',.25);await finish(side+'-upper-lid','skin',.4);await finish(side+'-lower-lid','skin',.35);}
  for(const p of await parts())if(p.name.includes('Mouth opening')||p.name.includes('Upper teeth')||['smile','lower-lip'].includes(p.id))await finish(p.id,'lip',.55);
  await finish('skirt-panel-0','cloth',.8,true);await finish('v119-wrap','cloth',.55,true);
  for(const side of ['left','right']){
   for(let i=0;i<4;i++)await remove('sock-fold-'+side+'-'+i);
   await finish('sock-'+side,'sock',.9);await finish('shoe-'+side,'leather',.8);await finish('sole-'+side,'leather',.5);
   for(const s of [-1,1])await finish('bow-'+side+'-'+s,'bow',.8);
  }
  for(const id of ['azure-body','coral-body'])await finish(id,'paper',.9);
  for(const group of ['Azure frost','Coral flare']){
   const first=(await parts()).find(p=>p.group===group&&p.kind==='loft'&&p.surfaceStyle==='anatomy-smooth');await finish(first.id,'skin',.5,true);
   for(const p of (await parts()).filter(p=>p.group===group&&p.kind==='sphere'&&!/eye|catch|tooth/.test(p.id)))await finish(p.id,'skin',.45);
  }
  const leaf=(await parts()).find(p=>p.surfaceStyle==='paper-leaf');await finish(leaf.id,'leaf',.9,true);
  console.log('HD_BODY_COMPLETE');
 }
 if(stage==='polish'){
  await pick('model-0001');await page.locator('#modelAtelierFaceNose').fill('.085');await hit('DensityApply');await transform('model-0001',{color:'#f8cdc3'});
  for(const [side,s]of [['left',-1],['right',1]])await shape(side+'-upper-lid',[[s*.032,4.057,.311],[s*.078,4.094,.318],[s*.148,4.103,.302],[s*.217,4.082,.276],[s*.232,4.096,.258]],[.0015,.0045,.005,.003,.0006]);
 }
 if(['full','hair'].includes(stage)){
  const palettes=[['#24b3c5','#28b7c8','#21aebf','#29b9c9','#2bbaca','#23b1c2','#28b6c7'],['#ed6058','#ef645b','#e85b56','#ef635b','#f0675d','#eb6059','#ed645c']];
  for(const [side,sign]of [[0,-1],[1,1]])for(let j=0;j<7;j++){
   const id='hair-front-'+sign+'-'+j,p=(await parts()).find(q=>q.id===id),z=[.105,.218,.307,.311,.286],path=p.path.map((q,i)=>[q[0],q[1],z[i]+j*.0035*Math.sin(i/4*Math.PI)]);
   await shape(id,path,[.019,.038,.034,.021,.001]);await transform(id,{color:palettes[side][j]});await finish(id,'hair',.8);
  }
 }
 if(['full','trim'].includes(stage)){
  const rows=(await parts()).filter(p=>/^skirt-(piping|inset)-/.test(p.id));
  await pick(rows[0].id);await page.locator('#modelAtelierHDEditor details summary').click();
  for(const p of rows){const match=p.id.match(/^skirt-(piping|inset)-(\d+)-(-?1)$/),inset=match[1]==='inset';await pick(p.id);await page.locator('#modelAtelierHDTrimPanel').selectOption('skirt-panel-'+match[2]);await page.locator('#modelAtelierHDTrimU').fill(String(Number(match[3])*(inset?.8:1)));await page.locator('#modelAtelierHDTrimStart').fill('.12');await page.locator('#modelAtelierHDTrimRadius').fill(inset?'.0018':'.0035');await hit('HDFitTrim');assert.ok(!(await page.locator('#modelAtelierStatus').innerText()).startsWith('Trim fit rejected:'));assert.ok((await parts()).find(q=>q.id===p.id).path.length>20);operations.push({id:p.id,fitTo:'skirt-panel-'+match[2],u:Number(match[3])*(inset?.8:1),start:.12,radius:inset?.0018:.0035});}
 }
 if(stage!=='face'){await page.locator('#modelAtelierDetailBudget summary').click();await page.locator('#modelAtelierDensityPreset').selectOption('hd');await hit('DensityPresetApply');operations.push({preset:'Authored HD sampling'});}
 const waiting=page.waitForEvent('download');await hit('Export');await(await waiting).saveAs(out+'/authored.model.json');const saved=JSON.parse(await fs.readFile(out+'/authored.model.json','utf8'));assert.deepEqual(saved.model,(await snap()).project.modelAtelier);if(stage==='full'&&bakedSeed.parts.find(p=>p.id==='skirt-piping-0-1').path.length>20)assert.deepEqual(saved.model,bakedSeed,'Repeated native authoring must exactly reproduce the saved HD starter');
 await page.locator('#modelAtelierImportFile').setInputFiles(out+'/authored.model.json');await page.waitForFunction(()=>document.getElementById('modelAtelierStatus').textContent.startsWith('Validated model,'));assert.deepEqual(saved.model,(await snap()).project.modelAtelier);
 await fs.writeFile(out+'/authored.swyrl.json',JSON.stringify(await snap(),null,2)+'\n');
 const density=await page.evaluate(()=>window.SWYRL_ENGINE_MODEL_ATELIER.density());await fs.writeFile(out+'/receipt.json',JSON.stringify({operations,parts:saved.model.parts.length,density,nativeRoundTrip:true,errors},null,2)+'\n');
 for(const view of ['front','three','right','back'])await capture('model-'+view,view);
 await capture('face-final','three','model-0001');const png=page.waitForEvent('download');await hit('RenderPNG');await(await png).saveAs(out+'/face-studio-2k.png');
 for(const id of ['hair-front--1-0','skirt-panel-0','shoe-left','azure-skull'])await capture('detail-'+id,'three',id);
 await page.setViewportSize({width:412,height:915});await capture('phone-front');assert.deepEqual(errors,[]);console.log('HD_NATIVE_AUTHORING_PASS',saved.model.parts.length,density.totalTriangles);
}finally{await browser.close();}
