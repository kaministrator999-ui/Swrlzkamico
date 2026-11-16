/* SE471_UV_IMPORT_DISPLAY_START */
const se471UVImportBase=se336ImportPaint;
se336ImportPaint=async function(file){
 const selected=se336SelectedMesh(),before=selected?.part?.uvPaintPNG;
 const id=selected?.part?.id;
 const result=await se471UVImportBase.apply(this,arguments);
 const current=id&&partById(id);
 // The native importer catches/report failures. Avoid a false success or view
 // change when validation fails or the selected mesh is changed mid-upload.
 if(!file||!current?.uvPaintPNG||current.uvPaintPNG===before||
    current.id!==id)return result;
 const switched=window.SWYRL_ENGINE_VIEW_READABILITY_455?.choose?.('shaded') ??
   window.SWYRL_ENGINE_MODEL_VIEW?.setMode?.('shaded');
 const selectedMesh=()=>modelRoot?.children?.find(m=>m.isMesh&&m.userData?.atelierId===id);
 if(current.uvPaintPNG&&!selectedMesh()?.material?.map)renderParts();
 const bound=!!selectedMesh()?.material?.map;
 if(switched===false||!bound)
  status('Image imported. Choose View → Material to see authored artwork; mesh material may need a refresh.',true);
 else status('Imported texture visible on '+current.name+' in Material view. Use UV fine tuning for additional shape correction.');
 return result;
};
/* SE471_UV_IMPORT_DISPLAY_END */
/* SE471_UV_FINE_FIT_START */
const se471GeometryBase=geometry;
const se471CheckPartBase=checkPart;
checkPart=function(part){
 return se471CheckPartBase(part)&&
  (part.uvSphereWarp===undefined||
   (part.kind==='sphere'&&Number.isFinite(part.uvSphereWarp)&&
    part.uvSphereWarp>=0&&part.uvSphereWarp<=1));
};
function se471WarpGeometry(geo,part,blend){
 if(!geo?.getAttribute||part?.kind!=='sphere')return false;
 const uv=geo.getAttribute('uv');
 if(!uv||!uv.count)return false;
 let originals=geo.userData?.se471LatitudeOriginalUV;
 if(!originals||originals.length!==uv.count){
  originals=Float32Array.from({length:uv.count},(_,i)=>uv.getY(i));
  geo.userData.se471LatitudeOriginalUV=originals;
 }
 const curve=se471Latitude.lookup(part.scale);
 const ratio=Math.hypot(part.scale[0],part.scale[2])/Math.SQRT2 /part.scale[1];
 for(let i=0;i<uv.count;i++){
  // Do not mutate V outside the native sphere 0..1 coordinate domain.
  uv.setY(i,se471Latitude.remap(originals[i],curve,blend));
 }
 uv.needsUpdate=true;
 return {ratio,blend};
}
geometry=function(part){
 const geo=se471GeometryBase(part);
 if(part?.kind==='sphere'&&part?.uvSphereWarp>0)se471WarpGeometry(geo,part,part.uvSphereWarp);
 return geo;
};
const se471OriginalUVInstall=se469InstallUI;
se469InstallUI=function(){
 se471OriginalUVInstall.apply(this,arguments);
 const host=document.getElementById('se469UVShapeFit');
 if(!host||host.querySelector('#se471UVFineTune'))return;
 const section=document.createElement('details');
 section.id='se471UVFineTune';
 section.open=false;
 section.innerHTML=
  '<summary>Fine-tune stretched textures</summary>'+
  '<p>Global shape-fit is a starting point. The sphere can also compensate latitude-by-latitude; adjust gradually to preserve logos and atlas details.</p>'+
  '<label>Latitude compensation <output id="se471LatitudeValue">0%</output>'+
  '<input type="range" id="se471LatitudeControl" min="0" max="1" step=".05" value="0"></label>'+
  '<label>Texture width (U) <output id="se471UValue">1.00</output>'+
  '<input type="range" id="se471UControl" min=".15" max="2" step=".01" value="1"></label>'+
  '<label>Texture height (V) <output id="se471VValue">1.00</output>'+
  '<input type="range" id="se471VControl" min=".15" max="2" step=".01" value="1"></label>'+
  '<p id="se471FitInfo">Select a textured sphere. Changes can be undone individually.</p>'+
  '<button type="button" id="se471FineReset">Reset fine tuning</button>';
 host.append(section);
 const updateLabel=(id,val)=>{const x=section.querySelector('#'+id);if(x)x.textContent=val;};
 const target=()=>se336SelectedMesh();
 const controls=[['warp','se471LatitudeControl'],['u','se471UControl'],['v','se471VControl']];
 function read(){
  const item=target(),part=item?.part;
  const values=part?se469Repeat(part):[1,1];
  const enabled=!!part?.uvPaintPNG&&!se469Candidate;
  const sphere=part?.kind==='sphere';
  return {item,enabled,sphere,values,warp:part?.uvSphereWarp||0};
 }
 function draw(){
  const state=read();
  for(const [axis,id] of controls){
   const input=section.querySelector('#'+id);if(!input)continue;
   input.disabled=!state.enabled||(axis==='warp'&&!state.sphere);
   if(document.activeElement!==input){
    input.value=axis==='warp'?state.warp:axis==='u'?state.values[0]:state.values[1];
   }
  }
  updateLabel('se471LatitudeValue',Math.round(Number(section.querySelector('#se471LatitudeControl').value)*100)+'%');
  updateLabel('se471UValue',Number(section.querySelector('#se471UControl').value).toFixed(2));
  updateLabel('se471VValue',Number(section.querySelector('#se471VControl').value).toFixed(2));
  section.querySelector('#se471FineReset').disabled=!state.enabled;
  section.querySelector('#se471FitInfo').textContent=!state.item
   ?'Select a mesh first.'
   :!state.enabled?'Import a painted texture, then fine-tune.'
   :!state.sphere?'U/V controls work here; latitude adjustment is sphere-only.'
   :'Use latitude blending for uneven stretching near the sphere poles. Original PNG remains unchanged.';
 }
 function preview(){
  const state=read(),mesh=state.item?.mesh;
  if(!state.enabled||!mesh)return;
  const warp=Number(section.querySelector('#se471LatitudeControl').value);
  const u=Number(section.querySelector('#se471UControl').value);
  const v=Number(section.querySelector('#se471VControl').value);
  if(state.sphere)se471WarpGeometry(mesh.geometry,state.item.part,warp);
  const mats=Array.isArray(mesh.material)?mesh.material:[mesh.material];
  for(const mat of mats){
   if(!mat?.map?.isTexture)continue;
   mat.map.center.set(.5,.5);mat.map.repeat.set(u,v);
   mat.map.updateMatrix();mat.map.needsUpdate=true;
  }
  updateLabel('se471LatitudeValue',Math.round(warp*100)+'%');
  updateLabel('se471UValue',u.toFixed(2));updateLabel('se471VValue',v.toFixed(2));
  se356UVPreviewSchedule();
 }
 function commit(){
  const state=read(),part=state.item?.part;
  if(!state.enabled||!part)return;
  const nextWarp=state.sphere?Number(section.querySelector('#se471LatitudeControl').value):0;
  const nextU=Number(section.querySelector('#se471UControl').value);
  const nextV=Number(section.querySelector('#se471VControl').value);
  if(![nextWarp,nextU,nextV].every(Number.isFinite))return;
  if(Math.abs((part.uvSphereWarp||0)-nextWarp)<.001&&
   Math.abs(state.values[0]-nextU)<.001&&Math.abs(state.values[1]-nextV)<.001)return;
  checkpoint();
  part.uvSphereWarp=nextWarp;
  part.uvPaintRepeat=[nextU,nextV];
  if(!checkPart(part)){historyStep(true);status('The requested UV fit is outside the safe range.',true);return;}
  signalEdited();select(part.id);
  se356UVPreviewSchedule();draw();
  status('Fine-tuned '+part.name+' UV mapping, saved with Undo. Texture PNG and geometry positions unchanged.');
 }
 for(const [axis,id] of controls){
  const input=section.querySelector('#'+id);
  input.addEventListener('input',preview);
  input.addEventListener('change',commit);
 }
 section.querySelector('#se471FineReset').onclick=()=>{
  const state=read(),part=state.item?.part;if(!state.enabled||!part)return;
  checkpoint();delete part.uvSphereWarp;
  part.uvPaintRepeat=[1,1];signalEdited();select(part.id);
  se356UVPreviewSchedule();draw();
  status('Fine tuning reset to original sphere UV sampling. Undo restores your changes.');
 };
 section.addEventListener('toggle',draw);
 panel?.addEventListener('swrlz:uv-slide-change',draw);
 draw();
};
const se471InspectorBase=refreshInspector;
refreshInspector=function(){
 const done=se471InspectorBase.apply(this,arguments);
 const root=document.getElementById('se471UVFineTune');
 if(root&&root.open){
  const item=se336SelectedMesh();
  const enabled=!!item?.part?.uvPaintPNG;
  for(const input of root.querySelectorAll('input')){
   input.disabled=!enabled||(input.id==='se471LatitudeControl'&&item?.part?.kind!=='sphere');
  }
 }
 return done;
};
/* SE471_UV_FINE_FIT_END */
