import assert from 'node:assert/strict';import {chromium} from 'playwright';import {readFile} from 'node:fs/promises';
const base=(process.env.SWYRL_SCULPT_TEST_URL||'http://127.0.0.1:8787').replace(/\/$/,'');
const browser=await chromium.launch({headless:true,args:['--no-sandbox','--disable-dev-shm-usage',
 '--enable-webgl','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader']});
try{
 for(const [device,viewport,mobile] of [['desktop',{width:1280,height:900},false],
  ['android-touch',{width:412,height:915},true]]){
  const context=await browser.newContext({viewport,isMobile:mobile,hasTouch:mobile,acceptDownloads:true});
  const page=await context.newPage();page.setDefaultTimeout(65000);
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(base+'/?project=model-atelier',{waitUntil:'domcontentloaded',timeout:90000});
  await page.locator('#modelAtelierPanel:not([hidden]) canvas').waitFor();
  const parts=()=>page.evaluate(()=>window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier.parts);
  assert.equal((await parts()).length,283);
  await page.locator('#modelAtelierParts').selectOption('model-0001');
  await page.locator('#modelAtelierLODRatio').fill('0.15');
  await page.locator('#modelAtelierLODPreview').click();
  const desc=await page.locator('#modelAtelierLODStats').textContent();
  assert.match(desc,/actual triangles/);
  const before=Number(desc.match(/^([\d,]+) →/)?.[1].replaceAll(',',''));
  const after=Number(desc.match(/→ ([\d,]+) actual triangles/)?.[1].replaceAll(',',''));
  assert(after<before&&after>1);
  const objD=page.waitForEvent('download');await page.locator('#modelAtelierLODOBJ').click();
  const obj=await objD;const objText=await readFile(await obj.path(),'utf8');
  assert.equal(objText.match(/^f /mg).length,after);
  assert.equal(objText.match(/^vt /mg).length,Number(desc.match(/· ([\d,]+) actual mesh vertices/)?.[1].replaceAll(',','')));
  await page.locator('#modelAtelierLODBake').click();
  let ps=await parts();assert.equal(ps.length,284);
  const copy=ps.find(x=>x.kind==='topologyMesh');assert(copy);
  assert.equal(copy.topologyMesh.indices.length/3,after);
  assert(ps.find(x=>x.id==='model-0001')?.headAnatomy,'Original head must remain unchanged');
  assert(await page.locator('#modelAtelierTopologyTools').isVisible());
  const originalCopy=JSON.stringify(copy.topologyMesh);
  // Spatial clustering can produce non-manifold candidate edges; only
  // choose an actual nondegenerate edge with at most two incident faces.
  const index=copy.topologyMesh.indices,position=copy.topologyMesh.positions;
  const frequency=new Map();
  for(let i=0;i<index.length;i+=3){
    for(let e=0;e<3;e++){
      const a=index[i+e],b=index[i+(e+1)%3],key=[a,b].sort((l,r)=>l-r).join(':');
      frequency.set(key,(frequency.get(key)||0)+1);
    }
  }
  let selected=null;
  for(let i=0;i<index.length&&!selected;i+=3){
    const ids=index.slice(i,i+3),v=ids.map(id=>position.slice(id*3,id*3+3));
    const a=v[0],b=v[1],c=v[2],AB=b.map((z,k)=>z-a[k]),AC=c.map((z,k)=>z-a[k]);
    const area2=(AB[1]*AC[2]-AB[2]*AC[1])**2+
      (AB[2]*AC[0]-AB[0]*AC[2])**2+(AB[0]*AC[1]-AB[1]*AC[0])**2;
    if(area2<1e-9)continue;
    for(let e=0;e<3;e++){
      const n=frequency.get([ids[e],ids[(e+1)%3]].sort((l,r)=>l-r).join(':'));
      if(n<=2){selected={face:i/3,edge:e,incident:n,vertex:ids[e]};break;}
    }
  }
  assert(selected,'Need a suitable manifold edge on reduced head');
  await page.locator('#modelAtelierTopologyFace').fill(String(selected.face));
  await page.locator('#modelAtelierTopologyEdge').selectOption(String(selected.edge));
  await page.locator('#modelAtelierTopologySplit').click();
  const split=(await parts()).find(x=>x.id===copy.id);
  assert.equal(split.topologyMesh.indices.length,copy.topologyMesh.indices.length+3*selected.incident,await page.locator('#modelAtelierStatus').textContent());
  assert.equal(split.topologyMesh.positions.length,copy.topologyMesh.positions.length+3);
  await page.locator('#modelAtelierTopologyVertex').fill(String(selected.vertex));
  await page.locator('#modelAtelierTopologyDelta0').fill('0');
  await page.locator('#modelAtelierTopologyDelta1').fill('0');
  await page.locator('#modelAtelierTopologyDelta2').fill('.03');
  await page.locator('#modelAtelierTopologyMove').click();
  const moved=(await parts()).find(x=>x.id===copy.id);
  assert(Math.abs(moved.topologyMesh.positions[selected.vertex*3+2]-split.topologyMesh.positions[selected.vertex*3+2]-.03)<1e-5);
  await page.locator('#modelAtelierTopologyRemove').click();
  const removed=(await parts()).find(x=>x.id===copy.id);
  assert.equal(removed.topologyMesh.indices.length,moved.topologyMesh.indices.length-3);
  await page.locator('#modelAtelierTopologyFace').fill('100000');
  await page.locator('#modelAtelierTopologyRemove').click();
  assert.deepEqual((await parts()).find(x=>x.id===copy.id).topologyMesh,removed.topologyMesh);
  await page.locator('#modelAtelierUndo').click();
  assert.deepEqual((await parts()).find(x=>x.id===copy.id).topologyMesh,moved.topologyMesh);
  await page.locator('#modelAtelierUndo').click();
  assert.deepEqual((await parts()).find(x=>x.id===copy.id).topologyMesh,split.topologyMesh);
  await page.locator('#modelAtelierUndo').click();
  assert.equal(JSON.stringify((await parts()).find(x=>x.id===copy.id).topologyMesh),originalCopy);
  await page.locator('#modelAtelierRedo').click();
  assert.deepEqual((await parts()).find(x=>x.id===copy.id).topologyMesh,split.topologyMesh);
  const dl=page.waitForEvent('download');await page.locator('#modelAtelierExport').click();
  const path=await(await dl).path(),json=JSON.parse(await readFile(path,'utf8'));
  assert.equal(json.model.parts.find(x=>x.id===copy.id)?.topologyMesh.indices.length/3,after+selected.incident);
  await page.locator('#modelAtelierUndo').click();
  ps=await parts();assert.equal(ps.length,284);
  await page.locator('#modelAtelierUndo').click();
  ps=await parts();assert.equal(ps.length,283);
  await page.locator('#modelAtelierImportFile').setInputFiles(path);
  await page.waitForFunction(()=>window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier.parts.length===284);
  ps=await parts();assert.equal(ps.find(x=>x.kind==='topologyMesh')?.topologyMesh.indices.length/3,after+selected.incident);
  assert.equal(ps.find(x=>x.id==='model-0001')?.headAnatomy!==undefined,true);
  assert.equal(errors.length,0,errors.join(' | '));
  console.log('V1140_REAL_HEAD_EDGE_VERTEX_FACE_EDIT_UNDO_REDO_NATIVE_RELOAD_PASS',device,before,after);
  await context.close();
 }
}finally{await browser.close();}
