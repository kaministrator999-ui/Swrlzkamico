
/* SE558_QA_ONLY: never ship this instrumented module. */
if(new URLSearchParams(location.search).get('serverqa')==='1'){
 let se558QAPass=null,se558QARunning=false;
 const originalInspect=window.SWYRL_ENGINE_UV_NUMBERING.inspect;
 window.SWYRL_ENGINE_UV_NUMBERING=Object.freeze({inspect:()=>{
  const value=originalInspect();
  return {...value,labels:se558QAPass?.ok?value.labels:0,functionalQA:se558QAPass};
 }});
 const qaAssert=(v,msg)=>{if(!v)throw Error('SE558 functional QA: '+msg);};
 const pause=ms=>new Promise(r=>setTimeout(r,ms));
 const same=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
 async function qaRun(host){
  const first=se551Target();qaAssert(first?.part?.topologyMesh,'starter not selected');
  const id=first.part.id, original=JSON.parse(JSON.stringify(first.part)), core=(await se555Imports()).core;
  const find=()=>model().parts.find(p=>p.id===id);
  const originalPartList=JSON.stringify(model().parts);
  const reselect=()=>{select(id);};
  const paint=document.createElement('canvas');paint.width=paint.height=512;
  const ctx=paint.getContext('2d'),img=ctx.createImageData(512,512);
  for(let y=0;y<512;y++)for(let x=0;x<512;x++){
   const i=(y*512+x)*4;img.data[i]=Math.floor(x/2);img.data[i+1]=Math.floor(y/2);img.data[i+2]=Math.floor((x+y)/4);img.data[i+3]=255;
  }
  ctx.putImageData(img,0,0);
  // A disposable fixture with deliberately under-packed existing UVs and known paint.
  checkpoint();
  first.part.topologyMesh.uvs=original.topologyMesh.uvs.map(x=>.06+x*.75);
  first.part.uvPaintPNG=paint.toDataURL('image/png');first.part.uvPaintOffset=[.125,.0625];
  // The fixture uses real native materials, not a Solid/diagnostic view clone.
  first.part.uvPaintSourceW=512;first.part.uvPaintSourceH=512;
  first.part.uvPaintSourceBytes=Math.floor(first.part.uvPaintPNG.split(',')[1].length*3/4)-(first.part.uvPaintPNG.endsWith('==')?2:first.part.uvPaintPNG.endsWith('=')?1:0);
  first.part.uvPaintMaxSize=0;
  atelierViewColors=true;atelierViewTextures=true;atelierViewMaterialOverrides.clear();
  qaAssert(window.SWYRL_ENGINE_VIEW_READABILITY_455.choose('shaded'),'Cannot enter Material view');
  signalEdited();reselect();
  const before=JSON.parse(JSON.stringify(find())), beforeList=JSON.stringify(model().parts);
  const expected=core.optimizeExistingUV(before.topologyMesh);
  qaAssert(expected.changed,'fixture must have measurable optimization');
  await pause(150);
  let result=null,confirmations=0;
  const originalOptimize=se557Optimize,originalConfirm=window.confirm;
  const invoke=async(all,accept)=>{
   const b=host.querySelector(all?'[data-se557-optimize-all]':'[data-se557-optimize]');
   qaAssert(b&&!b.disabled,'optimization button missing');
   result=null;
   window.confirm=msg=>{qaAssert(String(msg).includes('Apply verified UV improvement'),'unexpected confirmation');confirmations++;return accept;};
   se557Optimize=function(...args){result=originalOptimize(...args);return result;};
   try{b.click();qaAssert(result,'button did not invoke optimizer');return await result;}
   finally{se557Optimize=originalOptimize;window.confirm=originalConfirm;}
  };
  const state=()=>find();
  const verifyGeometry=(p)=>{
   qaAssert(same(p.topologyMesh.positions,before.topologyMesh.positions),'geometry positions changed');
   qaAssert(same(p.topologyMesh.indices,before.topologyMesh.indices),'geometry indices changed');
   const selected=se551Target(),uv=selected?.mesh?.geometry?.getAttribute('uv');
   qaAssert(uv&&uv.count*2===p.topologyMesh.uvs.length,'render UV count mismatch');
   for(let i=0;i<uv.count;i++)qaAssert(Math.abs(uv.getX(i)-p.topologyMesh.uvs[2*i])<1e-6&&Math.abs(uv.getY(i)-p.topologyMesh.uvs[2*i+1])<1e-6,'render UV buffer differs');
  };
  qaAssert(await invoke(false,false)===false,'cancel unexpectedly applied');
  qaAssert(JSON.stringify(model().parts)===beforeList&&confirmations===1,'cancel mutated model or skipped confirmation');
  qaAssert(await invoke(false,true)===true,'selected optimize failed');
  const after=JSON.parse(JSON.stringify(state()));
  qaAssert(!same(after.topologyMesh.uvs,before.topologyMesh.uvs),'UVs not changed');
  qaAssert(same(after.topologyMesh.uvs,expected.uvs),'applied UVs differ from numerical candidate');
  qaAssert(after.uvPaintPNG!==before.uvPaintPNG&&same(after.uvPaintOffset,[0,0]),'paint rebake or offset missing');
  reselect();verifyGeometry(after);
  // Independently sample the saved rebaked PNG at actual triangle interior pixels.
  const baked=new Image();baked.src=after.uvPaintPNG;await baked.decode();
  qaAssert(baked.width===512&&baked.height===512,'paint resolution changed');
  const target=document.createElement('canvas');target.width=target.height=512;
  const dc=target.getContext('2d');dc.drawImage(baked,0,0);
  const pixels=dc.getImageData(0,0,512,512).data;
  const uv0=before.topologyMesh.uvs,uv1=after.topologyMesh.uvs,ix=before.topologyMesh.indices;
  const area=(a,b,c)=>(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]);
  const wrap=v=>v-Math.floor(v);
  let samples=0,maxError=0;
  for(let k=0;k<ix.length;k+=3){
   const ids=ix.slice(k,k+3),t=ids.map(i=>[uv1[2*i]*512,(1-uv1[2*i+1])*512]);
   const x=Math.floor((t[0][0]+t[1][0]+t[2][0])/3),y=Math.floor((t[0][1]+t[1][1]+t[2][1])/3),q=[x+.5,y+.5];
   if(x<0||x>=512||y<0||y>=512)continue;
   const a=area(...t);if(Math.abs(a)<2)continue;
   const w=[area(t[1],t[2],q)/a,area(t[2],t[0],q)/a,area(t[0],t[1],q)/a];
   if(Math.min(...w)<.15)continue;
   const u=wrap(ids.reduce((s,i,j)=>s+uv0[i*2]*w[j],.125)),v=wrap(ids.reduce((s,i,j)=>s+uv0[i*2+1]*w[j],.0625));
   const sx=Math.min(511,Math.floor(u*512)),sy=Math.min(511,Math.floor((1-v)*512));
   const src=(sy*512+sx)*4,dst=(y*512+x)*4;
   for(let c=0;c<4;c++)maxError=Math.max(maxError,Math.abs(img.data[src+c]-pixels[dst+c]));
   samples++;
  }
  qaAssert(samples>=100&&maxError<=2,'paint surface sample mismatch: '+samples+' samples, max '+maxError);
  // Check the actual Three.js material after native model rebuild.
  let map;
  for(let n=0;n<30;n++){map=se551Target()?.mesh?.material?.map;if(map?.image?.width===512)break;await pause(100);}
  const actual=se551Target()?.mesh;
  const describeMap=m=>({width:m?.image?.width||null,height:m?.image?.height||null,offset:m?.offset?.toArray?.()||null,source:m?.image?.src?.slice(0,30)||null});
  qaAssert(map?.image?.width===512&&map.offset.x===0&&map.offset.y===0,'render texture not restored: '+JSON.stringify({view:atelierViewModeFor(state()),flags:atelierViewFlagsFor(state()),active:describeMap(map),original:describeMap(actual?.userData?.se455OriginalMaterial?.map),paintBytes:state().uvPaintPNG?.length,sourceWidth:state().uvPaintSourceW}));
  const gpu=document.createElement('canvas');gpu.width=gpu.height=512;const gc=gpu.getContext('2d');gc.drawImage(map.image,0,0);
  const actualPixels=gc.getImageData(0,0,512,512).data;
  qaAssert(actualPixels.every((v,i)=>v===pixels[i]),'rebuilt Three.js texture pixels differ from saved rebake');
  host.querySelector('[data-se551="undo"]').click();reselect();
  qaAssert(JSON.stringify(model().parts)===beforeList,'Undo did not restore exact UV and painted PNG');
  verifyGeometry(state());
  host.querySelector('[data-se551="redo"]').click();reselect();
  qaAssert(same(state(),after),'Redo did not restore applied UV and paint');
  host.querySelector('[data-se551="undo"]').click();reselect();
  qaAssert(await invoke(true,true)===true,'Optimize all control failed');
  qaAssert(same(state().topologyMesh.uvs,after.topologyMesh.uvs),'Optimize all differs from selected on one-part fixture');
  host.querySelector('[data-se551="undo"]').click();reselect();
  qaAssert(JSON.stringify(model().parts)===beforeList,'Optimize all Undo failed');
  host.querySelector('[data-se551="undo"]').click();reselect();
  qaAssert(JSON.stringify(model().parts)===originalPartList,'Disposable fixture failed to restore original starter');
  await pause(100);
  host.querySelector('[data-se551="fit"]').click();await pause(100);
  const canvas=host.querySelector('#se356UVCanvas'),cv=canvas.getBoundingClientRect(),vp=canvas.parentElement.getBoundingClientRect();
  const centerError=Math.abs((cv.left+cv.right-vp.left-vp.right)/2);
  qaAssert(centerError<=3&&cv.width<=vp.width+1&&cv.bottom<=host.getBoundingClientRect().bottom+1,'atlas fit/centering failed');
  return {ok:true,cancel:true,apply:true,undo:true,redo:true,optimizeAllOnePart:true,geometryPreserved:true,paintSamples:samples,maxPaintChannelError:maxError,renderTexture:true,restoredOriginal:true,centerErrorPx:centerError,atlasSizePx:cv.width};
 }
 const open=se552Open;
 se552Open=function(){
  open();if(se558QARunning)return;
  const host=se552Portal?.host;if(!host)return;se558QARunning=true;
  const report=document.createElement('span');report.style.cssText='font-weight:bold;color:#f6df91;padding:6px';report.textContent='QA running';host.children[0].append(report);
  const blocker=host.querySelector('[data-se556-model]');if(blocker)blocker.disabled=true;
  qaRun(host).then(r=>{se558QAPass=r;report.textContent='QA PASS · paint '+r.paintSamples+' samples · undo/redo · centered';report.style.color='#80e6b2';}).catch(e=>{se558QAPass={ok:false,error:String(e)};report.textContent=String(e);report.style.color='#ff8a8a';setTimeout(()=>{throw e},0);}).finally(()=>{if(blocker)blocker.disabled=false;se552ModelRegions(se551Target());se356UVPreviewSchedule();});
 };
}
/* SE558_QA_ONLY_END */
