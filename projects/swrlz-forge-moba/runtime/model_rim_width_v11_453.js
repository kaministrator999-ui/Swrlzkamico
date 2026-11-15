/* SE453_INSET_RIM_WIDTH_START */
// Visible coplanar rim and a touch-friendly, on-viewport width handle.
// Native se430 preview / Apply / Cancel owns all geometry and Undo transactions.
(function(){
 'use strict';
 let panel=null,button=null,cta=null,tooltip=null,source=null,mesh=null,origin=null,boundaryPoint=null;
 let currentState=null,dragging=false,pointerId=null,scheduled=false,pending=null;
 let lastTopology=null,lastSelection='',lastMesh=null;
 const api=()=>se430BeginnerAPI();
 const amount=()=>panel?.querySelector('#modelAtelierWorkshopAmount');
 const isInset=()=>panel?.querySelector('#modelAtelierWorkshopOperation')?.value==='inset';
 const guided=()=>panel?.querySelector('#se451FaceWorkflow');
 const configured=()=>!!panel?.querySelector('#modelAtelierViewport');
 const number=n=>Number(n.toFixed(3)).toString();
 function stopDrag(){
  if(dragging&&button&&pointerId!==null){try{button.releasePointerCapture(pointerId);}catch(_){}}
  dragging=false;pointerId=null;pending=null;
 }
 function state(){
  try{return api()?.inspect?.()||null;}catch(_){return null;}
 }
 function nativeMesh(id){
  return modelRoot?.children?.find(o=>o.isMesh&&o.userData?.atelierId===id)||null;
 }
 function selectOutlineRegion(record){
  if(record?.operation!=='inset'||!record.selectedFaces?.length||!record.data)return null;
  const r=se430MeshOps.region(record.data,record.selectedFaces);
  return r?.ok&&r.boundary?.length>=3?r:null;
 }
 function clearOutline(record){
  const obj=record?.se453RimOutline;
  if(!obj)return;
  obj.parent?.remove(obj);obj.geometry?.dispose?.();obj.material?.dispose?.();
  record.se453RimOutline=null;
 }
 function addOutline(record){
  clearOutline(record);
  const r=selectOutlineRegion(record);
  if(!r||!record?.mesh||typeof THREE.LineLoop!=='function')return;
  try{
   const points=r.boundary.map(id=>new THREE.Vector3(...record.data.positions.slice(id*3,id*3+3)));
   const geometry=new THREE.BufferGeometry().setFromPoints(points);
   const material=new THREE.LineBasicMaterial({color:0xffd477,depthTest:false,depthWrite:false,transparent:true,opacity:1});
   const line=new THREE.LineLoop(geometry,material);
   line.name='Inset inner rim · transient';
   line.renderOrder=195;
   line.userData.atelierHelper=true;line.userData.se453Transient=true;
   record.mesh.add(line);record.se453RimOutline=line;
  }catch(_){clearOutline(record);}
 }
 function geometry(){
  if(!currentState?.preview?.active||currentState.preview.operation!=='inset'||!isInset())return false;
  const id=currentState.selection?.partId,part=id&&partById(id),m=id&&nativeMesh(id);
  if(part?.kind!=='topologyMesh'||!part.topologyMesh||!m||!currentState.selection.faceIds?.length)return false;
  const selected=currentState.selection.faceIds.join(',');
  if(lastTopology===part.topologyMesh&&lastSelection===selected&&lastMesh===m&&origin&&boundaryPoint){
   mesh=m;return true;
  }
  let region;
  try{region=se430MeshOps.region(part.topologyMesh,currentState.selection.faceIds);}catch{return false;}
  if(!region?.ok||!region.boundary.length)return false;
  lastTopology=part.topologyMesh;lastSelection=selected;lastMesh=m;
  source=region;mesh=m;
  origin=new THREE.Vector3(...region.centroid);
  boundaryPoint=new THREE.Vector3(...part.topologyMesh.positions.slice(region.boundary[0]*3,region.boundary[0]*3+3));
  return true;
 }
 function project(local,rect){
  if(!mesh||!camera||!renderer?.domElement)return null;
  mesh.updateWorldMatrix(true,false);
  camera.updateMatrixWorld(true);
  const v=mesh.localToWorld(local.clone()).project(camera);
  if(!Number.isFinite(v.x)||!Number.isFinite(v.y)||v.z>1||v.z< -1)return null;
  return {x:rect.left+(v.x+1)*rect.width*.5,y:rect.top+(1-v.y)*rect.height*.5};
 }
 function reposition(){
  if(!button||!panel||dragging||!currentState?.preview?.active||!isInset()||!geometry()){
   if(button&&!dragging)button.hidden=true;
   return;
  }
  const canvas=renderer?.domElement,rect=canvas?.getBoundingClientRect?.();
  const host=button.offsetParent,hostRect=host?.getBoundingClientRect?.();
  if(!rect||!rect.width||!rect.height||!hostRect){button.hidden=true;return;}
  const fraction=Number(amount()?.value)||.2;
  const inner=origin.clone().lerp(boundaryPoint,1-fraction);
  const screen=project(inner,rect);
  if(!screen){button.hidden=true;return;}
  button.style.left=(screen.x-hostRect.left)+'px';
  button.style.top=(screen.y-hostRect.top)+'px';
  button.hidden=false;
  button.title='Drag inward to widen the rim; outward to narrow it';
 }
 function setWidth(fraction){
  const input=amount(),cfg=se430BeginnerAmount('inset');
  if(!input||!cfg)return;
  const clipped=Math.min(cfg.max,Math.max(cfg.min,Math.round(fraction*1000)/1000));
  if(Math.abs(Number(input.value)-clipped)<.002)return;
  input.value=number(clipped);
  // One native input event invokes the existing preview, never Apply.
  input.dispatchEvent(new Event('input',{bubbles:true}));
  if(tooltip)tooltip.textContent='Rim inset '+Math.round(clipped*100)+'%';
 }
 function pointerDown(e){
  if(!currentState?.preview?.active||!geometry()||!renderer?.domElement)return;
  if(e.pointerType==='mouse'&&e.button!==0)return;
  e.preventDefault();e.stopPropagation();
  dragging=true;pointerId=e.pointerId;
  button.setPointerCapture(e.pointerId);
 }
 function pointerMove(e){
  if(!dragging||e.pointerId!==pointerId||!mesh||!origin||!boundaryPoint)return;
  e.preventDefault();e.stopPropagation();
  const rect=renderer?.domElement?.getBoundingClientRect?.();if(!rect)return;
  const c=project(origin,rect),b=project(boundaryPoint,rect);
  if(!c||!b)return;
  const dx=b.x-c.x,dy=b.y-c.y,len=dx*dx+dy*dy;
  if(len<64)return; // Nearly edge-on; avoid unstable rim sizes.
  const t=((e.clientX-c.x)*dx+(e.clientY-c.y)*dy)/len;
  pending=Math.min(.8,Math.max(.03,1-t));
  if(!scheduled){
   scheduled=true;
   requestAnimationFrame(()=>{scheduled=false;const value=pending;pending=null;
    if(value!==null&&value!==undefined&&dragging)setWidth(value);
   });
  }
 }
 function pointerEnd(e){
  if(!dragging||e.pointerId!==pointerId)return;
  e.preventDefault();e.stopPropagation();
  const final=pending;stopDrag();
  if(final!==null&&final!==undefined)setWidth(final);
  currentState=state();reposition();
 }
 function prepare(){
  const s=state();if(!s||s.preview.active||!s.convert?.available)return;
  const id=s.selection.partId,seed=s.selection.ids?.find(Number.isInteger);
  if(!id||seed===undefined){se430BeginnerWrite(tooltip,'Tap a square face first.');return;}
  if(/bake.*vertex edit/i.test(s.convert.reason||'')){
   const agree=window.confirm?.('Bake the existing vertex edits into editable topology? This saves one Undo step and preserves the visible shape. Continue?');
   if(!agree)return;
  }
  const converted=api().convert();
  if(!converted?.ok){se430BeginnerResult(converted);return;}
  const region=api().selectRegion(seed,id);
  if(!region?.ok){se430BeginnerResult(region);return;}
  const cfg=se430BeginnerAmount('inset'),value=Number(amount()?.value);
  const result=api().preview('inset',{amount:Number.isFinite(value)?Math.max(cfg.min,Math.min(cfg.max,value)):cfg.value});
  se430BeginnerResult(result);
  currentState=state();refresh();
 }
 function refresh(){
  if(!panel||!cta)return;
  currentState=state();
  const s=currentState,op=isInset()&&panel.dataset.se451Guided==='true';
  const convertible=op&&!s?.preview?.active&&!!s?.convert?.available;
  cta.hidden=!convertible;
  if(convertible){
   const baking=/bake.*vertex edit/i.test(s.convert.reason||'');
   cta.textContent=baking?'Bake edits & preview rim':'Make editable & preview rim';
   cta.title=s.convert.reason||'Convert this selected mesh to native editable topology.';
   cta.disabled=!s.selection?.ids?.some(Number.isInteger);
  }
  const label=guided()?.querySelector('#se451AmountLabel');
  if(label&&op)label.textContent='Rim width · '+Math.round((Number(amount()?.value)||.2)*100)+'% inset (square: half that per side)';
  if(tooltip&&op&&!s?.preview?.active){
   tooltip.textContent=convertible?'Prepare this face before sizing the rim.':s?.operations?.inset?.reason||'Tap a face and select Inset to adjust its rim.';
  }
  reposition();
 }
 function mount(p){
  if(!p||p.dataset.se453RimWidth==='1')return;
  panel=p;const section=guided(),stage=p.querySelector('.atelier-scene');
  if(!section||!stage)return;
  p.dataset.se453RimWidth='1';
  const controls=section.querySelector('#se451AmountControls');
  if(controls){
   const guidance=document.createElement('small');
   guidance.className='se453-rim-help';
   guidance.textContent='The inner border is the rim edge. Drag the gold diamond on the model inward for a wider rim, or adjust the slider.';
   controls.append(guidance);
  }
  cta=document.createElement('button');cta.type='button';cta.id='se453PrepareRim';cta.hidden=true;
  cta.addEventListener('click',prepare);
  section.querySelector('.se451-commit')?.before(cta);
  tooltip=document.createElement('small');tooltip.id='se453RimStatus';tooltip.setAttribute('role','status');
  section.append(tooltip);
  button=document.createElement('button');button.type='button';button.id='se453RimHandle';button.hidden=true;
  button.setAttribute('aria-label','Drag to adjust rim width');
  button.textContent='◆';
  stage.append(button);
  button.addEventListener('pointerdown',pointerDown);
  button.addEventListener('pointermove',pointerMove);
  button.addEventListener('pointerup',pointerEnd);
  button.addEventListener('pointercancel',pointerEnd);
  window.addEventListener('swrlz:model-workshop-change',refresh);
  window.addEventListener('resize',reposition);
  panel.addEventListener('change',e=>{
   if(e.target.id==='modelAtelierWorkshopOperation'||e.target.id==='modelAtelierWorkshopAmount')refresh();
  });
  refresh();
 }
 const originalInstall=se430BeginnerInstall;
 se430BeginnerInstall=function(p){const result=originalInstall(p);mount(p);return result;};
 const originalTick=se430BeginnerTick;
 let lastFrame=0;
 se430BeginnerTick=function(now,...args){
  const result=originalTick.call(this,now,...args);
  if(button&&!button.hidden&&now-lastFrame>90){lastFrame=now;reposition();}
  return result;
 };
 const oldBeginnerRefresh=se430BeginnerRefresh;
 se430BeginnerRefresh=function(...args){
  const result=oldBeginnerRefresh.apply(this,args);
  if(panel)refresh();
  return result;
 };
 window.SWYRL_ENGINE_RIM_WIDTH_453=Object.freeze({version:'v11.453',refresh});
 // Called from native preview allocation and disposal; never persists helpers.
 window.se453RimBorderAdd=addOutline;window.se453RimBorderClear=clearOutline;
})();
/* SE453_INSET_RIM_WIDTH_END */