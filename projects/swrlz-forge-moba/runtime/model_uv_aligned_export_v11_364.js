/* §E v11.364 — export correctly aligned UV texture and the actual correction.
   Adds controls to the existing native UV editor; no geometry or UV rewrite. */
// Export the correction as an actual reusable PNG without changing mesh UVs,
// the current slide, or the project's original painted source image.
// This is the same RepeatWrapping placement used by the 3D material and
// the UV preview: canvas X = -offsetU; canvas Y = +offsetV.
function se364DrawAlignedPaint(canvas, image, offset) {
  const ctx=canvas.getContext('2d');
  if(!ctx)throw Error('2D aligned texture canvas unavailable.');
  const w=canvas.width,h=canvas.height;
  ctx.clearRect(0,0,w,h);
  const u=((offset[0]%1)+1)%1,v=((offset[1]%1)+1)%1;
  for(let row=-1;row<=0;row++)for(let col=0;col<=1;col++)
    ctx.drawImage(image,(col-u)*w,(row+v)*h,w,h);
}
async function se364ExportAlignedPaint() {
  try {
    const target=se336SelectedMesh();
    if(!target?.part.uvPaintPNG)throw Error('Select a mesh with an imported painted texture first.');
    const id=target.part.id, source=target.part.uvPaintPNG;
    const offset=se336SlideOffset(target.part);
    // Preserve the true mesh UVs: only the artwork is shifted for export.
    const probe=document.createElement('canvas');probe.width=probe.height=128;
    se336UVLayout(target.mesh,probe);
    const image=new Image();
    await new Promise((resolve,reject)=>{
      image.onload=resolve;
      image.onerror=()=>reject(Error('The painted texture could not be decoded.'));
      image.src=source;
    });
    if(!image.naturalWidth||!image.naturalHeight||
       image.naturalWidth>4096||image.naturalHeight>4096)
      throw Error('The painted image dimensions are unsupported.');
    if(selection!==id||partById(id)!==target.part||
       target.part.uvPaintPNG!==source||
       se336SlideOffset(target.part).some((value,i)=>value!==offset[i]))
      throw Error('The texture or selected mesh changed during export. Try saving again.');
    const canvas=document.createElement('canvas');
    // Do not needlessly upscale a previously downsampled saved texture.
    canvas.width=image.naturalWidth;canvas.height=image.naturalHeight;
    se364DrawAlignedPaint(canvas,image,offset);
    se336SaveCanvas(canvas,target.part.name+'-uv-ALIGNED.png');
    status('Saved aligned texture PNG with your current UV Slide correction baked in. '+
      'Use it with UV offset 0,0; your existing project and slide are unchanged. '+
      'Export correction JSON too for comparing the original and fixed placements.');
  } catch(error) {status('Save aligned UV: '+error.message,true);}
}
function se364ExportSlideCorrection() {
  try {
    const target=se336SelectedMesh();
    if(!target?.part.uvPaintPNG)throw Error('Select a mesh with an imported painted texture first.');
    const probe=document.createElement('canvas');probe.width=probe.height=128;
    const layout=se336UVLayout(target.mesh,probe);
    const offset=se336SlideOffset(target.part);
    const report={
      schema:'swyrl-model-uv-alignment-correction-v1',
      modelPart:{id:target.part.id,name:target.part.name,kind:target.part.kind,
        position:target.part.position,rotation:target.part.rotation,scale:target.part.scale},
      uvLayout:{triangles:layout.triangles,vertices:layout.vertices,
        coordinateConvention:'PNG top-left is U=0,V=1; bottom-right is U=1,V=0.'},
      correction:{
        textureOffsetUV:offset,
        canvasShiftUV:[-offset[0],offset[1]],
        wrap:'repeat',
        materialTextureFlipY:true,
        correctedPNG:'The companion -uv-ALIGNED.png bakes this offset into the texture.',
        applyAlignedPNGWithOffsetUV:[0,0],
        geometryUVCoordinatesChanged:false
      },
      note:'UV Slide changes texture placement, not mesh vertices or the UV layout. '+
        'Compare the original painted texture with the aligned PNG to understand the correction. '+
        'The original project retains its current UV offset. No anatomical labels are inferred.'
    };
    const blob=new Blob([JSON.stringify(report,null,2)+'\n'],{type:'application/json'});
    const url=URL.createObjectURL(blob),link=document.createElement('a');
    try{
      link.href=url;
      link.download=(target.part.name+'-uv-ALIGNMENT.json')
        .replace(/[^a-z0-9_.-]+/gi,'-').slice(0,85);
      document.body.append(link);link.click();link.remove();
    } finally {setTimeout(()=>URL.revokeObjectURL(url),1500);}
    status('Exported current UV Slide correction metadata. Share it with the original and aligned PNGs for comparison.');
  } catch(error){status('Export UV correction: '+error.message,true);}
}


function se364RefreshControls() {
  const root=document.getElementById('se364UVSaveGroup');
  if(!root)return;
  const painted=!!se336SelectedMesh()?.part.uvPaintPNG;
  root.querySelectorAll('button').forEach(button=>button.disabled=!painted);
}
function se364InstallControls() {
  const root=document.getElementById('modelAtelierUVLayout');
  if(!root)return;
  let group=root.querySelector('#se364UVSaveGroup');
  if(!group){
    group=document.createElement('details');
    group.id='se364UVSaveGroup';
    group.className='se336-uv-extra';
    group.innerHTML=
      '<summary>After UV Slide · save corrected reference</summary>'+
      '<p class="se336-uv-hint">Save Project already retains the live texture offset. '+
      'For comparison or reuse, export your aligned PNG and the matching correction JSON separately. '+
      'The aligned PNG is ready for offset 0,0; mesh UVs and the project remain unchanged.</p>'+
      '<div class="se336-uv-actions">'+
      '<button id="se364UVSaveAligned" type="button">Save aligned PNG</button>'+
      '<button id="se364UVSaveCorrection" type="button">Export correction JSON</button></div>';
    const advanced=root.querySelector('.se336-uv-extra');
    if(advanced)advanced.before(group);else root.append(group);
    group.querySelector('#se364UVSaveAligned').addEventListener('click',se364ExportAlignedPaint);
    group.querySelector('#se364UVSaveCorrection').addEventListener('click',se364ExportSlideCorrection);
    panel.addEventListener('swrlz:uv-slide-change',se364RefreshControls);
  }
  se364RefreshControls();
}
const se364OriginalEnsurePanel=ensurePanel;
ensurePanel=function(){
  const result=se364OriginalEnsurePanel.apply(this,arguments);
  se364InstallControls();
  return result;
};
const se364OriginalRefreshInspector=refreshInspector;
refreshInspector=function(){
  const result=se364OriginalRefreshInspector.apply(this,arguments);
  se364RefreshControls();
  return result;
};
