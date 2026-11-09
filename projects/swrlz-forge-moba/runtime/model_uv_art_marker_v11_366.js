/* §E v11.366 — authoring-space UV marker, not an alternate mesh UV system.
   Mark a real surface point, rotate/scale a flat painting reference, then
   bake authored image pixels back to UNCHANGED UVs before native import. */
let se366Pick=null;
const SE366_SIZE=1024;
function se366Clamp(value,min,max){return Math.max(min,Math.min(max,value));}
function se366Valid(m){
  return !!m&&m.version===1&&Array.isArray(m.centerUV)&&m.centerUV.length===2&&
    m.centerUV.every(v=>Number.isFinite(v)&&v>=0&&v<=1)&&
    Number.isFinite(m.angleDeg)&&m.angleDeg>=-180&&m.angleDeg<=180&&
    Number.isFinite(m.scale)&&m.scale>=.5&&m.scale<=2;
}
function se366Marker(part){
  return se366Valid(part?.uvArtMarker)?part.uvArtMarker:null;
}
function se366NativeToArt(u,v,m){
  const angle=m.angleDeg*Math.PI/180,c=Math.cos(angle),s=Math.sin(angle);
  const x=(u-m.centerUV[0])*m.scale,y=(m.centerUV[1]-v)*m.scale;
  return [.5+x*c-y*s,.5+x*s+y*c];
}
function se366ArtToNative(x,y,m){
  const angle=m.angleDeg*Math.PI/180,c=Math.cos(angle),s=Math.sin(angle);
  const dx=(x-.5)/m.scale,dy=(y-.5)/m.scale;
  return [m.centerUV[0]+dx*c+dy*s,m.centerUV[1]+dx*s-dy*c];
}
function se366SaveMarker(marker){
  const target=se336SelectedMesh();if(!target)return;
  const prior=se366Marker(target.part);
  if(!se366Valid(marker))throw Error('Marker position, rotation or scale is invalid.');
  if(JSON.stringify(prior)===JSON.stringify(marker))return;
  checkpoint();
  target.part.uvArtMarker={version:1,centerUV:marker.centerUV.slice(),
    angleDeg:marker.angleDeg,scale:marker.scale};
  if(!checkPart(target.part)){target.part.uvArtMarker=prior;throw Error('Mesh schema rejected marker.');}
  signalEdited();
  se366Refresh();
  se356UVPreviewSchedule();
}
function se366MarkAt(u,v){
  const target=se336SelectedMesh();if(!target)return;
  const prior=se366Marker(target.part);
  se366SaveMarker({version:1,
    centerUV:[Math.round(se366Clamp(u,0,1)*1000000)/1000000,
              Math.round(se366Clamp(v,0,1)*1000000)/1000000],
    angleDeg:prior?.angleDeg??0,scale:prior?.scale??1});
  status('UV marker placed on '+target.part.name+'. Rotate/scale the authoring frame, then export its guide.');
}
function se366StopPick(){
  se366Pick=null;
  const btn=document.getElementById('se366PickMesh');
  if(btn){btn.setAttribute('aria-pressed','false');btn.textContent='Pick center on model';}
}
function se366UseUVPoint(event){
  if(!se366Pick||se366Pick.mode!=='uv')return;
  const target=se336SelectedMesh();
  if(!target||target.part.id!==se366Pick.id){se366StopPick();return;}
  const rect=event.currentTarget.getBoundingClientRect();
  if(rect.width<=0||rect.height<=0)return;
  const u=se366Clamp((event.clientX-rect.left)/rect.width,0,1);
  const v=1-se366Clamp((event.clientY-rect.top)/rect.height,0,1);
  event.preventDefault();event.stopImmediatePropagation();
  se366StopPick();
  try{se366MarkAt(u,v);se356UVResolve(u,v);}catch(error){status('UV marker: '+error.message,true);}
}
function se366UseMeshPoint(event){
  if(!se366Pick||se366Pick.mode!=='mesh'||event.button!==0)return;
  const target=se336SelectedMesh(),viewport=panel?.querySelector('#modelAtelierViewport');
  if(!target||target.part.id!==se366Pick.id){se366StopPick();return;}
  const rect=viewport?.getBoundingClientRect();
  if(!rect?.width||!rect?.height||!camera)return;
  const mouse=new THREE.Vector2((event.clientX-rect.left)/rect.width*2-1,
    1-(event.clientY-rect.top)/rect.height*2);
  const ray=new THREE.Raycaster();ray.setFromCamera(mouse,camera);
  const hit=ray.intersectObject(target.mesh,false)[0];
  if(!hit?.uv)return;
  event.preventDefault();event.stopImmediatePropagation();
  se366StopPick();
  try{se366MarkAt(hit.uv.x,hit.uv.y);se356UVResolve(hit.uv.x,hit.uv.y);}catch(error){status('UV marker: '+error.message,true);}
}
function se366StartPick(mode){
  const target=se336SelectedMesh();
  if(!target)return;
  if(se366Pick?.id===target.part.id&&se366Pick.mode===mode){se366StopPick();return;}
  if(se336SlideState().enabled)se336SlideToggle();
  // The existing UV-to-mesh picker and new marker picker are mutually exclusive.
  if(se356UVPickMode){
    se356UVPickMode=false;
    const old=document.getElementById('se356UVPick3D');
    if(old){old.setAttribute('aria-pressed','false');old.textContent='Pick on model → UV';}
  }
  se366Pick={id:target.part.id,mode};
  se366Refresh();
  status(mode==='uv'?'Tap the desired center on the wireframe preview.':
    'Tap the desired center on the selected 3D surface. No geometry moves.');
}
function se366DrawMarker(ctx,size,marker){
  if(!se366Valid(marker))return;
  const x=marker.centerUV[0]*size,y=(1-marker.centerUV[1])*size;
  const a=marker.angleDeg*Math.PI/180,arm=Math.max(15,size*.055);
  ctx.save();
  ctx.lineWidth=Math.max(2,size/256);ctx.strokeStyle='#151329';
  ctx.fillStyle='#ffdd78';
  ctx.beginPath();ctx.arc(x,y,Math.max(7,size*.018),0,Math.PI*2);ctx.fill();ctx.stroke();
  ctx.strokeStyle='#fff';ctx.beginPath();ctx.moveTo(x-13,y);ctx.lineTo(x+13,y);
  ctx.moveTo(x,y-13);ctx.lineTo(x,y+13);ctx.stroke();
  const dx=-Math.sin(a)*arm,dy=-Math.cos(a)*arm;
  ctx.strokeStyle='#ffe18e';ctx.lineWidth=Math.max(3,size/160);
  ctx.beginPath();ctx.moveTo(x,y);ctx.lineTo(x+dx,y+dy);ctx.stroke();
  ctx.beginPath();ctx.arc(x+dx,y+dy,Math.max(3,size*.008),0,Math.PI*2);ctx.fill();
  ctx.restore();
}
function se366AuthorGuide(canvas,mesh,marker){
  const base=document.createElement('canvas');
  base.width=base.height=canvas.width;
  const stats=se336UVLayout(mesh,base);
  const ctx=canvas.getContext('2d');
  if(!ctx)throw Error('UV authoring canvas unavailable.');
  const size=canvas.width;
  ctx.clearRect(0,0,size,size);
  ctx.save();ctx.translate(size/2,size/2);
  ctx.rotate(marker.angleDeg*Math.PI/180);
  ctx.scale(marker.scale,marker.scale);
  ctx.translate(-marker.centerUV[0]*size,-(1-marker.centerUV[1])*size);
  // Repeat-seam preview matches the selected material's RepeatWrapping.
  for(let row=-2;row<=2;row++)for(let col=-2;col<=2;col++)
    ctx.drawImage(base,col*size,row*size,size,size);
  ctx.restore();
  // The center glyph is a reference only: hide/delete the guide before import.
  ctx.save();ctx.lineWidth=3;ctx.strokeStyle='#ffe18e';
  ctx.beginPath();ctx.arc(size/2,size/2,15,0,Math.PI*2);ctx.stroke();
  ctx.beginPath();ctx.moveTo(size/2-20,size/2);ctx.lineTo(size/2+20,size/2);
  ctx.moveTo(size/2,size/2-20);ctx.lineTo(size/2,size/2+20);ctx.stroke();
  ctx.restore();
  return stats;
}
function se366BakeArtwork(canvas,image,marker){
  const ctx=canvas.getContext('2d');
  if(!ctx)throw Error('UV artwork canvas unavailable.');
  const size=canvas.width;
  ctx.clearRect(0,0,size,size);
  // Inverse of author guide transform: do not alter mesh UV vertices.
  ctx.save();
  ctx.translate(marker.centerUV[0]*size,(1-marker.centerUV[1])*size);
  ctx.rotate(-marker.angleDeg*Math.PI/180);
  ctx.scale(1/marker.scale,1/marker.scale);
  ctx.translate(-size/2,-size/2);
  // Tile the authored image to avoid white seams on the sphere/hand.
  for(let row=-2;row<=2;row++)for(let col=-2;col<=2;col++)
    ctx.drawImage(image,col*size,row*size,size,size);
  ctx.restore();
}
function se366JSONDownload(obj,name){
  const blob=new Blob([JSON.stringify(obj,null,2)+'\n'],{type:'application/json'});
  const url=URL.createObjectURL(blob),a=document.createElement('a');
  try{
    a.href=url;a.download=name.replace(/[^a-z0-9_.-]+/gi,'-').slice(0,85);
    document.body.append(a);a.click();a.remove();
  }finally{setTimeout(()=>URL.revokeObjectURL(url),1500);}
}
function se366ExportGuide(){
  try{
    const target=se336SelectedMesh(),marker=se366Marker(target?.part);
    if(!target||!marker)throw Error('Place a marker on the selected mesh first.');
    const canvas=document.createElement('canvas');canvas.width=canvas.height=SE366_SIZE;
    se366AuthorGuide(canvas,target.mesh,marker);
    se336SaveCanvas(canvas,target.part.name+'-uv-MARKED-GUIDE.png');
    status('Exported 1024px marker-centered UV guide. Paint artwork aligned to its center; do not include cyan lines or center glyph in the final image.');
  }catch(error){status('Marker guide: '+error.message,true);}
}
function se366ExportProfile(){
  try{
    const target=se336SelectedMesh(),marker=se366Marker(target?.part);
    if(!target||!marker)throw Error('Place a marker on the selected mesh first.');
    const tmp=document.createElement('canvas');tmp.width=tmp.height=128;
    const uv=se336UVLayout(target.mesh,tmp);
    const out={
      schema:'swyrl-model-uv-author-marker-v1',
      mesh:{id:target.part.id,name:target.part.name,kind:target.part.kind,
        position:target.part.position,rotation:target.part.rotation,scale:target.part.scale},
      uvLayout:{triangles:uv.triangles,vertices:uv.vertices,
        pixels:SE366_SIZE,origin:'top-left',vAxis:'up'},
      marker:{...marker,centerPixel:[
        Math.round(marker.centerUV[0]*SE366_SIZE),
        Math.round((1-marker.centerUV[1])*SE366_SIZE)]},
      authoringFrame:{
        size:[SE366_SIZE,SE366_SIZE],center:[512,512],rotationDegreesClockwise:marker.angleDeg,
        scale:marker.scale,
        nativeToArt:'author = center + scale * R_clockwise(angleDeg) * (native - markerPixel)',
        artToNative:'native = markerPixel + R_counterclockwise(angleDeg) * (author - center) / scale',
        wrapping:'repeat',originalUVsChanged:false
      },
      textureSlideAtExport:se336SlideOffset(target.part),
      import:'Use Import marker-aligned artwork in §E; it inversely bakes image pixels into the original UV layout and resets old UV Slide to 0,0.',
      notes:'Center is the surface point the artist chose. Rotating the marker sets the image authoring frame, not the 3D model/camera. Do not include guide lines or center glyph in painted artwork.'
    };
    se366JSONDownload(out,target.part.name+'-uv-MARKER.json');
    status('Exported source-mesh UV marker and exact alignment transform. Share with the marked guide when generating artwork.');
  }catch(error){status('Marker profile: '+error.message,true);}
}
async function se366ImportAuthored(file){
  const target=se336SelectedMesh(),marker=se366Marker(target?.part);
  if(!target||!marker||!file){status('Place a marker and choose an image first.',true);return;}
  if(!['image/png','image/jpeg'].includes(file.type)||file.size>5000000){
    status('Select a PNG/JPEG authored image up to 5 MB.',true);return;
  }
  const id=target.part.id,part=target.part;
  const snapshot=JSON.stringify(marker),url=URL.createObjectURL(file),image=new Image();
  try{
    await new Promise((resolve,reject)=>{
      image.onload=resolve;image.onerror=()=>reject(Error('Could not decode artwork.'));image.src=url;
    });
    if(!image.naturalWidth||!image.naturalHeight||
       image.naturalWidth>4096||image.naturalHeight>4096)
      throw Error('Image dimensions must be 1–4096 pixels.');
    if(selection!==id||partById(id)!==part||
       JSON.stringify(se366Marker(part))!==snapshot)
      throw Error('Selected mesh or marker changed while loading image.');
    const canvas=document.createElement('canvas');canvas.width=canvas.height=SE366_SIZE;
    se366BakeArtwork(canvas,image,marker);
    const blob=await new Promise((resolve,reject)=>
      canvas.toBlob(b=>b?resolve(b):reject(Error('Could not encode mapped PNG.')),'image/png'));
    if(selection!==id||partById(id)!==part||
       JSON.stringify(se366Marker(part))!==snapshot)
      throw Error('Selected mesh or marker changed during conversion.');
    const bakedFile=new File([blob],part.name+'-uv-BAKED.png',{type:'image/png'});
    const imported=await se336ImportPaint(bakedFile);
    if(!imported||selection!==id||partById(id)!==part)return;
    // Native importer committed one Undo checkpoint, before replacing the art.
    // The previous slide and texture are restored TOGETHER by that Undo.
    part.uvPaintOffset=[0,0];
    se336SlidePreview(part);
    signalEdited();
    se336SlideNotify();
    se356UVPreviewSchedule();
    status('Imported marker-aligned artwork to '+part.name+' with original mesh UVs; old UV Slide reset to 0,0. Save Project to keep it.');
  }catch(error){status('Marker artwork import: '+error.message,true);}
  finally{URL.revokeObjectURL(url);}
}
function se366Refresh(){
  const box=document.getElementById('se366MarkerTools');if(!box)return;
  const target=se336SelectedMesh(),marker=se366Marker(target?.part);
  if(se366Pick&&se366Pick.id!==target?.part.id)se366StopPick();
  const output=box.querySelector('#se366MarkerInfo');
  if(output)output.textContent=!target?'Select a mesh to place a marker.':
    marker?('Center U '+marker.centerUV[0].toFixed(3)+' · V '+marker.centerUV[1].toFixed(3)+
      ' · '+marker.angleDeg+'° · '+marker.scale.toFixed(2)+'×'):
    'No marker yet · pick a point on the model or UV preview.';
  for(const el of box.querySelectorAll('[data-se366-needs]')){
    el.disabled=el.dataset.se366Needs==='mesh'?!target:!marker;
  }
  const angle=box.querySelector('#se366Angle'),scale=box.querySelector('#se366Scale');
  if(angle&&marker&&document.activeElement!==angle)angle.value=String(marker.angleDeg);
  if(scale&&marker&&document.activeElement!==scale)scale.value=String(marker.scale);
  const a=box.querySelector('#se366AngleValue'),z=box.querySelector('#se366ScaleValue');
  if(a)a.textContent=(marker?.angleDeg??0)+'°';
  if(z)z.textContent=(marker?.scale??1).toFixed(2)+'×';
  const pick=box.querySelector('#se366PickMesh'),uv=box.querySelector('#se366PickUV');
  if(pick){pick.textContent=se366Pick?.mode==='mesh'?'✓ Tap selected 3D mesh':'Pick center on model';
    pick.setAttribute('aria-pressed',String(se366Pick?.mode==='mesh'));}
  if(uv){uv.textContent=se366Pick?.mode==='uv'?'✓ Tap UV preview':'Pick center on UV preview';
    uv.setAttribute('aria-pressed',String(se366Pick?.mode==='uv'));}
}
function se366Install(){
  const root=document.getElementById('modelAtelierUVLayout');
  const preview=document.getElementById('se356UVPreview');
  if(!root||!preview||root.querySelector('#se366MarkerTools'))return;
  const box=document.createElement('details');
  box.id='se366MarkerTools';box.className='se336-uv-extra';
  box.innerHTML=
    '<summary>🎯 UV alignment marker · center / rotate / scale</summary>'+
    '<p class="se366-hint">Mark the center of a face, palm or other surface. The guide is re-centered and turned for easy artwork creation; native mesh UVs stay unchanged.</p>'+
    '<div class="se366-actions">'+
      '<button type="button" id="se366PickMesh" data-se366-needs="mesh">Pick center on model</button>'+
      '<button type="button" id="se366PickUV" data-se366-needs="mesh">Pick center on UV preview</button></div>'+
    '<p id="se366MarkerInfo" class="se366-info">Select a mesh to place a marker.</p>'+
    '<label class="se366-range">Rotate guide <output id="se366AngleValue">0°</output>'+
      '<input id="se366Angle" data-se366-needs="marker" type="range" min="-180" max="180" step="1" value="0"></label>'+
    '<label class="se366-range">Artwork scale <output id="se366ScaleValue">1.00×</output>'+
      '<input id="se366Scale" data-se366-needs="marker" type="range" min="0.5" max="2" step="0.05" value="1"></label>'+
    '<div class="se366-actions">'+
      '<button id="se366Guide" data-se366-needs="marker" type="button">Export marked UV guide</button>'+
      '<button id="se366Profile" data-se366-needs="marker" type="button">Export marker JSON</button>'+
      '<button id="se366Import" data-se366-needs="marker" type="button">Import marker-aligned artwork</button>'+
      '<button id="se366Reset" data-se366-needs="marker" type="button">Clear marker</button></div>'+
    '<input id="se366File" hidden type="file" accept="image/png,image/jpeg">'+
    '<p class="se366-hint">Draw on the exported authoring guide with its center upright. Remove the wireframe before saving the artwork; importing here reverses the marker alignment and applies it to the original UVs. Ordinary Import painted image and UV Slide still work as before.</p>';
  preview.after(box);
  box.querySelector('#se366PickMesh').addEventListener('click',()=>se366StartPick('mesh'));
  box.querySelector('#se366PickUV').addEventListener('click',()=>se366StartPick('uv'));
  box.querySelector('#se366Angle').addEventListener('change',e=>{
    const target=se336SelectedMesh(),m=se366Marker(target?.part);if(!m)return;
    try{se366SaveMarker({...m,angleDeg:Number(e.target.value)});}
    catch(error){status('UV marker angle: '+error.message,true);}
  });
  box.querySelector('#se366Scale').addEventListener('change',e=>{
    const target=se336SelectedMesh(),m=se366Marker(target?.part);if(!m)return;
    try{se366SaveMarker({...m,scale:Number(e.target.value)});}
    catch(error){status('UV marker scale: '+error.message,true);}
  });
  box.querySelector('#se366Angle').addEventListener('input',e=>{
    box.querySelector('#se366AngleValue').textContent=e.target.value+'°';
  });
  box.querySelector('#se366Scale').addEventListener('input',e=>{
    box.querySelector('#se366ScaleValue').textContent=Number(e.target.value).toFixed(2)+'×';
  });
  box.querySelector('#se366Guide').addEventListener('click',se366ExportGuide);
  box.querySelector('#se366Profile').addEventListener('click',se366ExportProfile);
  box.querySelector('#se366Import').addEventListener('click',()=>box.querySelector('#se366File').click());
  box.querySelector('#se366File').addEventListener('change',async e=>{
    const file=e.target.files?.[0];if(file)await se366ImportAuthored(file);e.target.value='';
  });
  box.querySelector('#se366Reset').addEventListener('click',()=>{
    const target=se336SelectedMesh();if(!target?.part.uvArtMarker)return;
    checkpoint();delete target.part.uvArtMarker;signalEdited();se366StopPick();
    se366Refresh();se356UVPreviewSchedule();status('UV marker cleared. Existing painted image and UV Slide unchanged.');
  });
  const viewport=panel?.querySelector('#modelAtelierViewport');
  if(viewport&&!viewport.dataset.se366Pick){
    viewport.dataset.se366Pick='true';
    viewport.addEventListener('pointerdown',se366UseMeshPoint,true);
  }
  const uvCanvas=preview.querySelector('#se356UVCanvas');
  if(uvCanvas&&!uvCanvas.dataset.se366Pick){
    uvCanvas.dataset.se366Pick='true';
    uvCanvas.addEventListener('click',se366UseUVPoint,true);
  }
  panel?.addEventListener('swrlz:uv-slide-change',se366Refresh);
  se366Refresh();
}
const se366BaseEnsurePanel=ensurePanel;
ensurePanel=function(){
  const result=se366BaseEnsurePanel.apply(this,arguments);
  se366Install();
  return result;
};
const se366BaseRefreshInspector=refreshInspector;
refreshInspector=function(){
  const result=se366BaseRefreshInspector.apply(this,arguments);
  se366Refresh();
  return result;
};
const se366BaseCheckPart=checkPart;
checkPart=function(part){
  return se366BaseCheckPart(part)&&(part.uvArtMarker===undefined||se366Valid(part.uvArtMarker));
};
window.SWYRLZ_E_UV_ART_MARKER=Object.freeze({
  current:()=>{const p=se336SelectedMesh()?.part;return se366Marker(p);},
  nativeToArt:se366NativeToArt,artToNative:se366ArtToNative
});
