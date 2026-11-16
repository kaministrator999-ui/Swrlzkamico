// SE469_UV_SHAPE_FIT_START
// Extension of the existing native Model Atelier UV preview and painted-texture material.
// A shape-fit is opt-in, previews in place, and never rewrites mesh vertices or PNG bytes.
let se469Candidate=null,se469Report=null;
const se469OriginalPartCheck=checkPart;
checkPart=function(part){
 if(!se469OriginalPartCheck(part))return false;
 const a=part?.uvPaintRepeat;
 return a===undefined||(Array.isArray(a)&&a.length===2&&a.every(n=>typeof n==='number'&&Number.isFinite(n)&&n>=.15&&n<=4));
};
function se469Repeat(part){
 const a=part?.uvPaintRepeat;
 return Array.isArray(a)&&a.length===2&&a.every(Number.isFinite)?a.slice():[1,1];
}
function se469Offset(part){
 return Array.isArray(part?.uvPaintOffset)?part.uvPaintOffset.slice():[0,0];
}
const se469OriginalMaterial=material;
material=function(part){
 const m=se469OriginalMaterial(part);
 if(m?.map&&part?.uvPaintPNG){
  const repeat=se469Repeat(part);
  m.map.center.set(.5,.5);
  m.map.repeat.set(...repeat);
  m.map.offset.set(...se469Offset(part));
  m.map.needsUpdate=true;
 }
 return m;
};
function se469Target(){
 const target=se336SelectedMesh();
 target?.mesh?.updateWorldMatrix(true,false);
 return target;
}
function se469LiveApply(id,repeat,offset){
 const mesh=modelRoot?.children?.find(m=>m.isMesh&&m.userData?.atelierId===id);
 if(!mesh)return;
 for(const mat of Array.isArray(mesh.material)?mesh.material:[mesh.material]){
  if(!mat?.map||!mat.userData?.se336PaintTexture)continue;
  mat.map.center.set(.5,.5);
  mat.map.repeat.set(...repeat);
  mat.map.offset.set(...offset);
  mat.map.needsUpdate=true;
 }
}
function se469Discard(){
 const old=se469Candidate;se469Candidate=null;
 if(old)se469LiveApply(old.id,old.oldRepeat,old.oldOffset);
}
function se469Measure(){
 const target=se469Target();
 if(!target)throw Error('Select a model mesh first.');
 const report=se469Math.measure(target.mesh.geometry,target.mesh.matrixWorld);
 se469Report={id:target.part.id,part:target.part,report};
 return report;
}
function se469DrawStretch(){
 const root=se356UVPreviewRoot();
 const canvas=root?.querySelector('#se356UVCanvas'),ctx=canvas?.getContext('2d');
 const info=root?.querySelector('#se356UVInfo');
 if(!canvas||!ctx||!info)return;
 const size=canvas.width;ctx.clearRect(0,0,size,size);
 ctx.fillStyle='#142334';ctx.fillRect(0,0,size,size);
 const target=se469Target();
 if(!target){info.textContent='Select a mesh to measure UV stretching.';return;}
 try{
  const result=se469Measure();
  for(const face of result.faces){
   const [u0,v0,u1,v1,u2,v2]=face.uv;
   ctx.fillStyle=face.ratio<1.25?'#2ed5b8':face.ratio<1.75?'#d4da55':face.ratio<3?'#f49846':'#ed5067';
   ctx.beginPath();ctx.moveTo(u0*size,(1-v0)*size);
   ctx.lineTo(u1*size,(1-v1)*size);ctx.lineTo(u2*size,(1-v2)*size);
   ctx.closePath();ctx.fill();
  }
  const guide=document.createElement('canvas');guide.width=guide.height=size;
  se336UVLayout(target.mesh,guide);
  ctx.globalAlpha=.36;ctx.drawImage(guide,0,0);ctx.globalAlpha=1;
  info.textContent=target.part.name+' · '+result.sampled+' sampled triangles / '+result.triangles+
   ' · UV surface stretch peak ×'+Math.min(result.peakRatio,9999).toFixed(2)+
   ' (green low, yellow moderate, orange/red high).';
  if(se356UVPin?.id===target.part.id)se356UVDrawPin(ctx,canvas,se356UVPin.u,se356UVPin.v);
 }catch(error){info.textContent='UV stretch: '+error.message;}
 se469UpdateUI();
}
const se469OriginalUVRender=se356UVRender;
se356UVRender=function(){
 if(se356UVMode==='stretch')return se469DrawStretch();
 se469OriginalUVRender();
 se469UpdateUI();
};
const se469OriginalUVPaintImage=se356UVPaintImage;
se356UVPaintImage=function(ctx,img,part,size){
 const candidate=se469Candidate?.id===part.id&&se469Candidate.part===part?se469Candidate:null;
 const repeat=candidate?.repeat||se469Repeat(part);
 const offset=candidate?.offset||se469Offset(part);
 if(repeat[0]===1&&repeat[1]===1&&!candidate)return se469OriginalUVPaintImage(ctx,img,part,size);
 // Canvas top-down V is opposite the texture's bottom-up V. Draw repeated
 // tiles with the same center=.5, offset, and repeat transform as Three.js.
 const width=size/repeat[0],height=size/repeat[1];
 const left=-(.5-.5*repeat[0]+offset[0])*width;
 const top=-(.5-.5*repeat[1]-offset[1])*height;
 const startX=Math.floor(-left/width),endX=Math.ceil((size-left)/width);
 const startY=Math.floor(-top/height),endY=Math.ceil((size-top)/height);
 for(let y=startY;y<=endY;y++)for(let x=startX;x<=endX;x++)
  ctx.drawImage(img,left+x*width,top+y*height,width,height);
};
function se469UpdateUI(){
 const root=document.getElementById('se469UVShapeFit');if(!root)return;
 const t=se336SelectedMesh();
 if(se469Candidate&&(!t||se469Candidate.id!==t.part.id||se469Candidate.part!==t.part))
  se469Discard();
 const preview=!!se469Candidate,hasPaint=!!t?.part?.uvPaintPNG;
 const info=root.querySelector('#se469UVShapeStatus');
 if(info){
  if(!t)info.textContent='Select a model mesh.';
  else if(preview)info.textContent='Preview only · U ×'+se469Candidate.repeat[0].toFixed(3)+
    ' · V ×'+se469Candidate.repeat[1].toFixed(3)+' · Apply to save or Cancel to restore.';
  else if(se469Report?.id===t.part.id&&se469Report.part===t.part){
   const m=se469Report.report;
   info.textContent='Transform-aware U ×'+m.scaleU.toFixed(3)+' · V ×'+m.scaleV.toFixed(3)+
    ' · proposed repeat U '+m.suggested[0].toFixed(3)+', V '+m.suggested[1].toFixed(3)+
    (hasPaint?'':' · Import a painted image before previewing correction.');
  }else info.textContent=hasPaint?'Analyze the current mesh to preview an aspect correction.':'UV heatmap works without paint; shape-fit needs a painted image.';
 }
 const buttons={
  se469UVAnalyze:!!t,se469UVPreview:!!t&&hasPaint&&!preview,
  se469UVApply:preview,se469UVCancel:preview,
  se469UVReset:!!t&&hasPaint&&!preview&&se469Repeat(t.part).some(x=>Math.abs(x-1)>1e-5)
 };
 for(const [id,on] of Object.entries(buttons)){const b=root.querySelector('#'+id);if(b)b.disabled=!on;}
}
function se469Analyze(){
 try{
  se469Discard();
  se469Measure();
  const b=se356UVPreviewRoot()?.querySelector('[data-se356-mode="stretch"]');
  b?.click();
  se356UVPreviewSchedule();
  se469UpdateUI();
  status('UV distortion measured from transformed mesh geometry, not from the texture image.');
 }catch(error){status('UV distortion: '+error.message,true);}
}
function se469PreviewFit(){
 try{
  se469Discard();
  const t=se469Target();if(!t?.part?.uvPaintPNG)throw Error('Select a mesh with an imported painted texture.');
  const result=se469Measure();
  const before=se469Repeat(t.part),offset=se469Offset(t.part);
  const after=result.suggested;
  const pin=se356UVPin?.id===t.part.id?[se356UVPin.u,se356UVPin.v]:[.5,.5];
  const nextOffset=se469Math.anchoredOffset(offset,before,after,pin);
  if(nextOffset.some(n=>!Number.isFinite(n)||Math.abs(n)>2))
   throw Error('Correction offset exceeds the supported range. Pick a UV anchor closer to the center.');
  se469Candidate={id:t.part.id,part:t.part,oldRepeat:before,oldOffset:offset,
   repeat:after,offset:nextOffset};
  se469LiveApply(t.part.id,after,nextOffset);
  se469UpdateUI();
  // Show exactly what sampling the candidate produces on the imported atlas.
  const paint=se356UVPreviewRoot()?.querySelector('[data-se356-mode="paint"]');
  paint?.click();
  se356UVPreviewSchedule();
  status('Shape-fit preview: original image is unchanged. Atlas bands may be cropped; Apply or Cancel.');
 }catch(error){status('UV shape-fit: '+error.message,true);}
}
function se469ApplyFit(){
 const t=se469Target(),preview=se469Candidate;
 if(!preview||!t||preview.part!==t.part||preview.id!==t.part.id){
  se469Discard();status('Preview the current same mesh first.',true);return;
 }
 const probe={...t.part,uvPaintRepeat:preview.repeat.slice(),uvPaintOffset:preview.offset.slice()};
 if(!checkPart(probe)){se469Discard();status('UV correction failed saved mesh validation.',true);return;}
 checkpoint();
 t.part.uvPaintRepeat=probe.uvPaintRepeat;
 t.part.uvPaintOffset=probe.uvPaintOffset;
 se469Candidate=null;se469Report=null;
 signalEdited();select(t.part.id);
 se356UVPreviewSchedule();
 status('Saved shape-aware texture correction. Undo restores the previous mapping; no image or geometry edits.');
}
function se469CancelFit(){
 se469Discard();se469UpdateUI();se356UVPreviewSchedule();
 status('Shape-fit preview canceled. Saved UVs and painted texture remain unchanged.');
}
function se469ResetFit(){
 const t=se469Target();if(!t?.part?.uvPaintPNG)return;
 if(!t.part.uvPaintRepeat)return;
 checkpoint();delete t.part.uvPaintRepeat;
 se469Candidate=null;se469Report=null;signalEdited();select(t.part.id);
 se356UVPreviewSchedule();
 status('Shape-fit reset to native texture proportions; Undo restores the previous correction.');
}
function se469InstallUI(){
 const preview=se356UVPreviewRoot();if(!preview||preview.querySelector('#se469UVShapeFit'))return;
 const modes=preview.querySelector('.se356-uv-preview-modes');
 if(modes){
  const b=document.createElement('button');b.type='button';
  b.dataset.se356Mode='stretch';b.setAttribute('aria-pressed','false');
  b.textContent='Stretch heatmap';modes.append(b);
 }
 const root=document.createElement('section');root.id='se469UVShapeFit';
 root.className='se469-uv-shape-fit';
 root.innerHTML='<strong>Shape-aware texture correction</strong>'+
  '<p>Analyze real transformed geometry. Heatmap: green = low stretch, orange/red = high. A flattened sphere needs a different image sampling ratio.</p>'+
  '<p id="se469UVShapeStatus" role="status">Select a mesh to begin.</p>'+
  '<div class="se469-uv-controls">'+
   '<button type="button" id="se469UVAnalyze">Analyze stretch</button>'+
   '<button type="button" id="se469UVPreview">Preview shape-fit</button>'+
   '<button type="button" id="se469UVApply">Apply correction</button>'+
   '<button type="button" id="se469UVCancel">Cancel preview</button>'+
   '<button type="button" id="se469UVReset">Reset fit</button>'+
  '</div>'+
  '<p>Preview is non-destructive. Apply stores a per-mesh sampling correction with Undo. Texture image, geometry, and original UV coordinates are preserved. A global correction can crop or repeat atlas artwork: for individual logos, use UV island adjustment instead.</p>';
 preview.append(root);
 // Hidden UV windows must never leave an unapplied material preview visible.
 new MutationObserver(records=>{
  if(se469Candidate&&records.some(record=>
      (record.target?.id==='se355UVPopup'||record.target===panel)&&record.target.hidden)){
   se469Discard();se469UpdateUI();
  }
 }).observe(panel,{subtree:true,attributes:true,attributeFilter:['hidden']});
 for(const [id,cb] of Object.entries({
  se469UVAnalyze:se469Analyze,se469UVPreview:se469PreviewFit,
  se469UVApply:se469ApplyFit,se469UVCancel:se469CancelFit,
  se469UVReset:se469ResetFit
 }))root.querySelector('#'+id).addEventListener('click',cb);
 se469UpdateUI();
}
const se469OriginalInstallPreview=se356UVInstallPreview;
se356UVInstallPreview=function(){
 se469OriginalInstallPreview.apply(this,arguments);
 se469InstallUI();
};
const se469OriginalRefreshInspector=refreshInspector;
refreshInspector=function(){
 const result=se469OriginalRefreshInspector.apply(this,arguments);
 se469UpdateUI();return result;
};
window.SWYRLZ_E_UV_SHAPE_FIT=Object.freeze({
 inspect:()=>{try{return se469Measure()}catch(e){return {ok:false,reason:e.message}}},
 state:()=>({preview:!!se469Candidate,partId:se469Candidate?.id||null}),
 cancel:se469CancelFit
});
// SE469_UV_SHAPE_FIT_END
