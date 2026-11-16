/* SE472_NATIVE_TEXTURE_RESOLUTION_START */
// Preserve the user's imported bytes. UV sampling, mesh topology and the
// account-saved source are independent of the optional GPU display resolution.
const SE472_TEXTURE_SIZES=Object.freeze([0,4096,2048,1024,512,256]);
const SE472_SOURCE_LIMIT=5_000_000; // Existing import permission: 5 MB, no automatic recompression.
const se472BaseCheckPart=checkPart;
checkPart=function(part){
 if(!se472BaseCheckPart(part))return false;
 const size=part?.uvPaintMaxSize;
 if(size!==undefined&&!SE472_TEXTURE_SIZES.includes(size))return false;
 for(const key of ['uvPaintSourceW','uvPaintSourceH']){
  if(part[key]!==undefined&&(!Number.isInteger(part[key])||part[key]<1||part[key]>4096))return false;
 }
 if(part.uvPaintSourceBytes!==undefined&&
    (!Number.isInteger(part.uvPaintSourceBytes)||part.uvPaintSourceBytes<1||
      part.uvPaintSourceBytes>SE472_SOURCE_LIMIT))return false;
 return true;
};
function se472DisplaySize(part){
 const width=part?.uvPaintSourceW,height=part?.uvPaintSourceH,choice=part?.uvPaintMaxSize||0;
 if(!width||!height)return null;
 const factor=choice?Math.min(1,choice/Math.max(width,height)):1;
 return [Math.max(1,Math.round(width*factor)),Math.max(1,Math.round(height*factor))];
}
function se472ApplyFiltering(tex){
 tex.colorSpace=THREE.SRGBColorSpace;
 tex.flipY=true;
 tex.wrapS=THREE.RepeatWrapping;tex.wrapT=THREE.RepeatWrapping;
 tex.generateMipmaps=true;tex.minFilter=THREE.LinearMipmapLinearFilter;
 tex.magFilter=THREE.LinearFilter;
 const limit=renderer?.capabilities?.getMaxAnisotropy?.()||1;
 tex.anisotropy=Math.max(1,Math.min(8,limit));
 return tex;
}
const se472BaseMaterial=material;
material=function(part){
 const mat=se472BaseMaterial(part);
 if(!part?.uvPaintPNG||!mat?.map?.isTexture)return mat;
 const original=mat.map;
 se472ApplyFiltering(original);
 const size=se472DisplaySize(part),selected=part.uvPaintMaxSize||0;
 if(!selected||!size||Math.max(size[0],size[1])>=Math.max(part.uvPaintSourceW,part.uvPaintSourceH))
  return mat; // Always bind original pixels by default; no canvas conversion.
 // Only the GPU representation is downsampled. Original data URI stays in
 // part.uvPaintPNG and is saved exactly as imported, even across reloads.
 const preview=se472ApplyFiltering(new THREE.Texture());
 preview.center.copy(original.center);preview.offset.copy(original.offset);
 preview.repeat.copy(original.repeat);preview.rotation=original.rotation;
 mat.map=preview;mat.needsUpdate=true;
 original.dispose();
 const image=new Image(),expectedSource=part.uvPaintPNG;
 image.onload=()=>{
  if(mat.map!==preview)return;
  try{
   const w=image.naturalWidth,h=image.naturalHeight;
   if(!w||!h)throw Error('Image has no dimensions.');
   const factor=Math.min(1,selected/Math.max(w,h));
   const canvas=document.createElement('canvas');
   canvas.width=Math.max(1,Math.round(w*factor));
   canvas.height=Math.max(1,Math.round(h*factor));
   const ctx=canvas.getContext('2d',{alpha:true});
   if(!ctx)throw Error('Unable to make a GPU texture preview.');
   ctx.imageSmoothingEnabled=true;
   ctx.imageSmoothingQuality='high';
   ctx.drawImage(image,0,0,canvas.width,canvas.height);
   preview.image=canvas;preview.needsUpdate=true;
  }catch(error){
   // Keep the mesh visible, preserve the original bytes, and report failure.
   preview.image=image;preview.needsUpdate=true;
   status('Display downscale failed; using original texture: '+error.message,true);
  }
 };
 image.onerror=()=>{
  if(mat.map===preview)status('Unable to decode saved texture for display.',true);
 };
 image.src=expectedSource;
 return mat;
};
function se472ReadFile(file){
 return new Promise((resolve,reject)=>{
  const reader=new FileReader();
  reader.onload=()=>typeof reader.result==='string'?resolve(reader.result):
   reject(Error('Imported texture was not readable.'));
  reader.onerror=()=>reject(Error('Could not read the imported texture.'));
  reader.readAsDataURL(file);
 });
}
function se472DecodeDimensions(source){
 return new Promise((resolve,reject)=>{
  const image=new Image();
  image.onload=()=>resolve([image.naturalWidth,image.naturalHeight]);
  image.onerror=()=>reject(Error('Image could not be decoded.'));
  image.src=source;
 });
}
const se472PriorImport=se336ImportPaint;
se336ImportPaint=async function(file){
 const target=se336SelectedMesh();
 if(!target||!file){status('Select a mesh and a texture image.',true);return false;}
 if(!['image/png','image/jpeg'].includes(file.type)||file.size>SE472_SOURCE_LIMIT||!file.size){
  status('Choose a PNG or JPEG up to 5 MB. No image will be silently resized.',true);return false;
 }
 const id=target.part.id,part=target.part;
 try{
  // Require the actual selected mesh UVs, as the existing importer does.
  const guide=document.createElement('canvas');guide.width=guide.height=256;
  se336UVLayout(target.mesh,guide);
  const source=await se472ReadFile(file);
  const [w,h]=await se472DecodeDimensions(source);
  if(!w||!h||w>4096||h>4096)
   throw Error('This editor supports textures up to 4096 × 4096. The original has not been modified.');
  if(!/^data:image\/(?:png|jpeg);base64,[A-Za-z0-9+/=]+$/.test(source))
   throw Error('Imported image bytes were not a supported PNG or JPEG.');
  if(source.length>7_000_000)
   throw Error('Original texture exceeds the supported save envelope. No downscaling was performed.');
  if(selection!==id||partById(id)!==part)
   throw Error('Selected mesh changed while importing. Choose it and try again.');
  const probe={...part,uvPaintPNG:source,uvPaintMaxSize:0,
   uvPaintSourceW:w,uvPaintSourceH:h,uvPaintSourceBytes:file.size};
  if(!checkPart(probe))
   throw Error('The model schema could not save the original image. No texture was changed.');
  checkpoint();
  part.uvPaintPNG=source;
  part.uvPaintMaxSize=0;
  part.uvPaintSourceW=w;part.uvPaintSourceH=h;part.uvPaintSourceBytes=file.size;
  signalEdited();select(id);
  se336SlideNotify();
  se356UVPreviewSchedule();
  const switched=window.SWYRL_ENGINE_VIEW_READABILITY_455?.choose?.('shaded') ??
    window.SWYRL_ENGINE_MODEL_VIEW?.setMode?.('shaded');
  const mesh=modelRoot?.children?.find(m=>m.isMesh&&m.userData?.atelierId===id);
  if(!mesh?.material?.map||switched===false)
   status('Full-resolution image saved. Switch View → Material to see its texture.',true);
  else status('Texture imported at ORIGINAL '+w+' × '+h+' ('+(file.size/1048576).toFixed(2)+
   ' MiB). No resizing or guide removal. Save to account to keep it.');
  return true;
 }catch(error){
  status('Texture import: '+error.message,true);
  return false;
 }
};
const se472PriorRemovePaint=se336RemovePaint;
se336RemovePaint=function(){
 const part=partById(selection);
 se472PriorRemovePaint.apply(this,arguments);
 if(part&&!part.uvPaintPNG){
  delete part.uvPaintMaxSize;delete part.uvPaintSourceW;
  delete part.uvPaintSourceH;delete part.uvPaintSourceBytes;
  se472UpdateControls();
 }
};
function se472UpdateControls(){
 const root=document.getElementById('se472TextureResolution');
 if(!root)return;
 const part=se336SelectedMesh()?.part;
 const select=root.querySelector('#se472DisplayResolution');
 const info=root.querySelector('#se472TextureInfo');
 const hasTexture=!!part?.uvPaintPNG;
 select.disabled=!hasTexture;
 if(hasTexture){
  select.value=String(part.uvPaintMaxSize||0);
  const dims=se472DisplaySize(part);
  if(dims){
   const size=part.uvPaintSourceW+' × '+part.uvPaintSourceH;
   const format=part.uvPaintPNG.startsWith('data:image/jpeg')?'JPEG':'PNG';
   info.textContent='Original imported: '+size+' · '+format+
    (part.uvPaintSourceBytes?' · '+(part.uvPaintSourceBytes/1048576).toFixed(2)+' MiB':'')+
    ' · 3D display: '+dims[0]+' × '+dims[1]+
    ' · source stored unmodified.';
  }else{
   info.textContent='Legacy texture (original resolution unavailable). Reimport the original image for full quality.';
  }
 }else{
  select.value='0';
  info.textContent='Import a painted image to use its original resolution. No image is imported yet.';
 }
}
const se472PriorInstallUV=se336InstallUI;
se336InstallUI=function(){
 const result=se472PriorInstallUV.apply(this,arguments);
 const root=document.getElementById('modelAtelierUVLayout');
 if(!root||root.querySelector('#se472TextureResolution'))return result;
 const block=document.createElement('section');block.id='se472TextureResolution';
 block.className='se472-texture-resolution';
 block.innerHTML='<strong>Texture resolution</strong>'+
  '<p>Full resolution is the default. Lower settings only reduce the 3D viewport texture; the saved original image remains intact, so Original always restores full quality.</p>'+
  '<label for="se472DisplayResolution">Viewport resolution</label>'+
  '<select id="se472DisplayResolution">'+
   '<option value="0">Original (full resolution)</option>'+
   '<option value="4096">Up to 4096</option>'+
   '<option value="2048">Up to 2048</option>'+
   '<option value="1024">Up to 1024</option>'+
   '<option value="512">Up to 512</option>'+
   '<option value="256">Up to 256</option></select>'+
  '<p id="se472TextureInfo" role="status"></p>'+
  '<p>Account project size still reflects the full-resolution source; very large projects may exceed account storage limits.</p>';
 (root.querySelector('#se336UVHasPaint')||root).after(block);
 block.querySelector('select').addEventListener('change',()=>{
  const target=se336SelectedMesh(),part=target?.part;
  if(!part?.uvPaintPNG){se472UpdateControls();return;}
  const size=Number(block.querySelector('select').value);
  if(!SE472_TEXTURE_SIZES.includes(size)){se472UpdateControls();return;}
  if((part.uvPaintMaxSize||0)===size)return;
  checkpoint();
  part.uvPaintMaxSize=size;
  if(!checkPart(part)){historyStep(true);status('Invalid texture size.',true);return;}
  signalEdited();select(part.id);
  se356UVPreviewSchedule();se472UpdateControls();
  const dims=se472DisplaySize(part);
  status('Viewport texture '+(dims?dims.join(' × '):'Original')+
   '. The full-resolution imported image is preserved. Undo restores the setting.');
 });
 se472UpdateControls();return result;
};
const se472PriorUVUpdate=se336UpdateUI;
se336UpdateUI=function(){
 const result=se472PriorUVUpdate.apply(this,arguments);
 se472UpdateControls();
 return result;
};
window.SWYRLZ_E_TEXTURE_472=Object.freeze({
 version:'v11.472',sizes:SE472_TEXTURE_SIZES.slice(),
 selection:()=>{
  const p=se336SelectedMesh()?.part;
  return p?.uvPaintPNG?{source:[p.uvPaintSourceW||null,p.uvPaintSourceH||null],
    display:se472DisplaySize(p),maxDimension:p.uvPaintMaxSize||0}:null;
 }
});
/* SE472_NATIVE_TEXTURE_RESOLUTION_END */
