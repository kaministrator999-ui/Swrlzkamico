// v11.22 §E Model Atelier: self-contained, portable, multi-view image reference studio.
// References are INSPECTION overlays, not OBJ geometry or UV/texture edits.
// All imagery comes from explicit local files; no network fetches, arbitrary HTML,
// remote URLs, or automatic model reconstruction.
const atelierRefMaxImages=4,atelierRefMaxInputBytes=12_000_000;
const atelierRefMaxEncodedLength=240_000;
const atelierRefAngles=['front','right','left','back','three','top','free'];
let atelierRefDock=null,atelierRefDrag=null,atelierRefImageDrag=null;
let atelierRefTransient=new Map();
function atelierRefValid(refs){
 if(!Array.isArray(refs)||refs.length>atelierRefMaxImages)return false;
 const ids=new Set();
 return refs.every(r=>{
   if(!r||typeof r!=='object'||Array.isArray(r))return false;
   if(typeof r.id!=='string'||r.id.length>72||ids.has(r.id))return false;
   ids.add(r.id);
   if(typeof r.name!=='string'||r.name.length>100)return false;
   if(typeof r.data!=='string'||r.data.length>atelierRefMaxEncodedLength||
      !/^data:image\/(?:webp|jpeg|png);base64,[A-Za-z0-9+/]+={0,2}$/.test(r.data))return false;
   if(!atelierRefAngles.includes(r.angle))return false;
   if(![r.zoom,r.offsetX,r.offsetY,r.rotation,r.opacity].every(Number.isFinite))return false;
   if(r.zoom<.25||r.zoom>5||Math.abs(r.offsetX)>750||Math.abs(r.offsetY)>750||
     Math.abs(r.rotation)>360||r.opacity<.15||r.opacity>1||typeof r.mirror!=='boolean')return false;
   return typeof r.visible==='boolean';
 });
}
function atelierRefLayoutValid(v){
 if(v==null)return true;
 return !!v&&typeof v==='object'&&!Array.isArray(v)
   &&[v.x,v.y].every(n=>Number.isFinite(n)&&n>=0&&n<=6000)
   &&typeof v.open==='boolean'&&typeof v.collapsed==='boolean'
   &&(v.active===null||(typeof v.active==='string'&&v.active.length<=72));
}
function atelierRefReadImport(source){
 if(source.references!==undefined&&!atelierRefValid(source.references))
   throw new Error('Reference images failed portable image size/type or transform validation.');
 if(!atelierRefLayoutValid(source.referenceLayout))
   throw new Error('Reference panel layout is invalid.');
 if(source.referenceLayout?.active&&!source.references?.some(r=>r.id===source.referenceLayout.active))
   throw new Error('Reference panel points to a missing image.');
 return {
   references:structuredClone(source.references||[]),
   referenceLayout:structuredClone(source.referenceLayout||{
      x:12,y:12,open:false,collapsed:false,active:null
   })
 };
}
function atelierRefEnsure(){
 if(!model())return null;
 if(!Array.isArray(model().references))model().references=[];
 if(!model().referenceLayout)model().referenceLayout={
   x:12,y:12,open:false,collapsed:false,active:null
 };
 return model();
}
function atelierRefCurrent(){
 const m=atelierRefEnsure();if(!m)return null;
 return m.references.find(r=>r.id===m.referenceLayout.active)||m.references[0]||null;
}
function atelierRefMark(message){
 const m=atelierRefEnsure();if(!m)return;
 m.editedAt='local';if(typeof markDirty==='function')markDirty();
 refreshList(); // sync Undo/Redo button availability with native checkpoint()
 if(message)status(message);
}
function atelierRefSetData(ref,next){
 const original=ref;
 const changed={...original,...next};
 if(!atelierRefValid([changed])){status('Reference transform rejected by validation.',true);return false;}
 Object.assign(ref,next);atelierRefMark();atelierRefPaint();return true;
}
function atelierRefClampLayout(){
 const m=atelierRefEnsure();
 if(!m||!atelierRefDock||!stage)return;
 const l=m.referenceLayout;
 const w=atelierRefDock.offsetWidth||250,h=atelierRefDock.offsetHeight||240;
 // The view-mode toolbar is a sibling over the 3D canvas. Dock images
 // BELOW its actual rendered height: on narrow phones the toolbar wraps,
 // and the reference window previously covered Wireframe/X-Ray controls.
 const sceneRect=stage.getBoundingClientRect();
 const toolbar=$m('ViewportModes');
 const toolbarBottom=toolbar?.getBoundingClientRect().bottom||sceneRect.top;
 const minY=Math.max(12,Math.ceil(toolbarBottom-sceneRect.top+8));
 l.x=Math.max(0,Math.min(l.x,Math.max(0,stage.clientWidth-w)));
 l.y=Math.max(minY,Math.min(l.y,Math.max(minY,stage.clientHeight-Math.min(h,stage.clientHeight-minY))));
 atelierRefDock.style.left=l.x+'px';
 atelierRefDock.style.top=l.y+'px';
 atelierRefDock.style.maxHeight='calc(100% - '+l.y+'px - 8px)';
}
function atelierRefPaint(){
 const m=atelierRefEnsure(),dock=atelierRefDock;
 if(!m||!dock)return;
 const layout=m.referenceLayout,r=atelierRefCurrent();
 dock.hidden=!layout.open;
 dock.classList.toggle('atelier-ref-collapsed',layout.collapsed);
 $m('ReferenceToggle').setAttribute('aria-expanded',String(layout.open));
 if(layout.open){
   atelierRefClampLayout();
   const tabs=$m('ReferenceTabs');tabs.replaceChildren();
   for(const ref of m.references){
     const btn=document.createElement('button');
     btn.type='button';btn.textContent=ref.name.slice(0,16);
     btn.title=ref.name;btn.className=ref.id===r?.id?'atelier-ref-active':'';
     btn.setAttribute('aria-pressed',String(ref.id===r?.id));
     btn.addEventListener('click',()=>{
       if(m.referenceLayout.active===ref.id)return;
       checkpoint();m.referenceLayout.active=ref.id;
       atelierRefMark();atelierRefPaint();
     });
     tabs.append(btn);
   }
   const display=$m('ReferenceImage'),empty=$m('ReferenceEmpty');
   const detail=$m('ReferenceDetail');
   const thumb=$m('ReferenceThumbnail');
   thumb.hidden=!layout.collapsed||!r;
   if(r&&thumb.getAttribute('data-ref-id')!==r.id){
     thumb.src=r.data;thumb.setAttribute('data-ref-id',r.id);
   }
   detail.hidden=!r;
   if(r){
     empty.hidden=true;display.hidden=!r.visible;
     if(display.getAttribute('data-ref-id')!==r.id){
       display.src=r.data;display.setAttribute('data-ref-id',r.id);
     }
     display.alt='Visual reference: '+r.name;
     const temp=atelierRefTransient.get(r.id)||{};
     const zoom=temp.zoom??r.zoom,offX=temp.offsetX??r.offsetX,offY=temp.offsetY??r.offsetY;
     display.style.opacity=String(temp.opacity??r.opacity);
     display.style.transform='translate('+offX+'px,'+offY+'px) rotate('+r.rotation+
        'deg) scaleX('+(r.mirror?-1:1)+') scale('+zoom+')';
     $m('ReferenceAngle').value=r.angle;
     $m('ReferenceZoom').value=String(zoom);
     $m('ReferenceOpacity').value=String(temp.opacity??r.opacity);
     $m('ReferenceShow').checked=r.visible;
     $m('ReferenceName').textContent=r.name;
   }else{
     empty.hidden=false;display.hidden=true;
     display.removeAttribute('src');display.removeAttribute('data-ref-id');
   }
   $m('ReferenceCount').textContent=m.references.length+'/'+atelierRefMaxImages+' images';
   $m('ReferenceCollapse').textContent=layout.collapsed?'Expand':'Minimize';
 }
}
function atelierRefSnapshotBefore(action){
 const m=atelierRefEnsure();if(!m)return;
 checkpoint();action(m);
 atelierRefMark();atelierRefPaint();
}
async function atelierRefCompress(file){
 if(!file||!['image/jpeg','image/png','image/webp'].includes(file.type)||
   file.size>atelierRefMaxInputBytes||file.size<12)
   throw Error('Choose a JPEG, PNG or WebP image under 12 MB.');
 const bitmap=await createImageBitmap(file);
 try{
   const ratio=Math.min(1,1024/Math.max(bitmap.width,bitmap.height));
   const canvas=document.createElement('canvas');
   canvas.width=Math.max(1,Math.round(bitmap.width*ratio));
   canvas.height=Math.max(1,Math.round(bitmap.height*ratio));
   const ctx=canvas.getContext('2d',{alpha:true});
   if(!ctx)throw Error('Image conversion is not available in this browser.');
   ctx.drawImage(bitmap,0,0,canvas.width,canvas.height);
   for(const q of [.84,.7,.55,.4,.28]){
     let url=canvas.toDataURL('image/webp',q);
     if(!url.startsWith('data:image/webp;'))url=canvas.toDataURL('image/jpeg',q);
     if(url.length<=atelierRefMaxEncodedLength)return url;
   }
   throw Error('Image is too detailed for portable save. Crop or downsize it first.');
 }finally{bitmap.close?.();}
}
async function atelierRefUpload(files){
 const items=Array.from(files||[]);
 if(!items.length)return;
 const m=atelierRefEnsure();if(!m)return;
 if(m.references.length+items.length>atelierRefMaxImages){
   status('Maximum '+atelierRefMaxImages+' reference images. Remove one before importing more.',true);return;
 }
 const prepared=[];
 try{
   for(const file of items){
     const data=await atelierRefCompress(file);
     const ref={
       id:'ref-'+Date.now().toString(36)+'-'+Math.random().toString(36).slice(2,8),
       name:file.name.slice(0,100),data,
       angle:prepared.length?'right':'front',zoom:1,offsetX:0,offsetY:0,
       rotation:0,mirror:false,opacity:.87,visible:true
     };
     prepared.push(ref);
   }
   if(!atelierRefValid([...m.references,...prepared]))throw Error('Reference set failed validation.');
   atelierRefSnapshotBefore(modelState=>{
     modelState.references.push(...prepared);
     modelState.referenceLayout.active=prepared[0].id;
     modelState.referenceLayout.open=true;modelState.referenceLayout.collapsed=false;
   });
   status('Added '+prepared.length+' portable references. They are saved in project/model JSON, not applied as a mesh texture.');
 }catch(e){status('Reference import rejected: '+String(e.message||e),true);}
 finally{$m('ReferenceFile').value='';}
}
function atelierRefDockPointerDown(e){
 if(e.button!==0)return;
 const m=atelierRefEnsure();if(!m)return;
 // Avoid interfering with normal header buttons, model gestures and the
 // image-pan area. Touch target is the header's free space only.
 if(e.target.closest('button,input,select,img'))return;
 atelierRefDrag={pointerId:e.pointerId,startX:e.clientX,startY:e.clientY,
    x:m.referenceLayout.x,y:m.referenceLayout.y,moved:false};
 e.currentTarget.setPointerCapture?.(e.pointerId);
 e.preventDefault();
}
function atelierRefDockPointerMove(e){
 const d=atelierRefDrag,m=atelierRefEnsure();
 if(!d||d.pointerId!==e.pointerId||!m)return;
 const dx=e.clientX-d.startX,dy=e.clientY-d.startY;
 if(!d.moved&&Math.hypot(dx,dy)>3){checkpoint();d.moved=true;}
 if(!d.moved)return;
 m.referenceLayout.x=d.x+dx;m.referenceLayout.y=d.y+dy;
 atelierRefClampLayout();e.preventDefault();
}
function atelierRefDockPointerUp(e){
 if(atelierRefDrag?.pointerId!==e.pointerId)return;
 const d=atelierRefDrag;atelierRefDrag=null;
 if(d.moved){atelierRefMark('Reference panel repositioned. Model geometry untouched.');}
}
function atelierRefImagePointerDown(e){
 if(e.button!==0)return;
 const r=atelierRefCurrent();if(!r)return;
 atelierRefImageDrag={pointerId:e.pointerId,id:r.id,startX:e.clientX,startY:e.clientY,
   x:r.offsetX,y:r.offsetY,moved:false};
 e.currentTarget.setPointerCapture?.(e.pointerId);e.preventDefault();
}
function atelierRefImagePointerMove(e){
 const d=atelierRefImageDrag,r=atelierRefCurrent();if(!d||!r||r.id!==d.id||e.pointerId!==d.pointerId)return;
 const dx=e.clientX-d.startX,dy=e.clientY-d.startY;
 if(!d.moved&&Math.hypot(dx,dy)>3){checkpoint();d.moved=true;}
 if(!d.moved)return;
 // Keep per-reference pan inside safe serialized bounds.
 r.offsetX=Math.max(-750,Math.min(750,d.x+dx));
 r.offsetY=Math.max(-750,Math.min(750,d.y+dy));
 atelierRefPaint();e.preventDefault();
}
function atelierRefImagePointerUp(e){
 if(atelierRefImageDrag?.pointerId!==e.pointerId)return;
 const d=atelierRefImageDrag;atelierRefImageDrag=null;
 if(d.moved)atelierRefMark('Reference image panned. Saved with project.');
}
function atelierRefInstall(){
 atelierRefDock=$m('ReferenceDock');
 $m('ReferenceToggle').addEventListener('click',()=>{
   atelierRefSnapshotBefore(m=>{m.referenceLayout.open=!m.referenceLayout.open;});
 });
 $m('ReferenceClose').addEventListener('click',()=>{
   atelierRefSnapshotBefore(m=>{m.referenceLayout.open=false;});
 });
 $m('ReferenceThumbnail').addEventListener('click',()=>{$m('ReferenceCollapse').click();});
 $m('ReferenceCollapse').addEventListener('click',()=>{
   atelierRefSnapshotBefore(m=>{m.referenceLayout.collapsed=!m.referenceLayout.collapsed;});
 });
 $m('ReferenceFile').addEventListener('change',e=>atelierRefUpload(e.target.files));
 $m('ReferenceAngle').addEventListener('change',e=>{
   const r=atelierRefCurrent();if(r)atelierRefSnapshotBefore(()=>{r.angle=e.target.value;});
 });
 $m('ReferenceCamera').addEventListener('click',()=>{
   const r=atelierRefCurrent();if(!r)return;
   if(r.angle==='free'){status('Choose a front, side, back or other named reference angle first.',true);return;}
   const view=r.angle;
   if(!atelierSetPoseCamera(view)){status('View orientation unavailable.',true);return;}
   status('Camera matched to '+view+' reference. Reference image itself is unchanged.');
 });
 $m('ReferenceFlip').addEventListener('click',()=>{
   const r=atelierRefCurrent();if(r)atelierRefSnapshotBefore(()=>{r.mirror=!r.mirror;});
 });
 for(const [name,delta]of [['ReferenceRotateLeft',-90],['ReferenceRotateRight',90]]){
   $m(name).addEventListener('click',()=>{
     const r=atelierRefCurrent();if(r)atelierRefSnapshotBefore(()=>{
       r.rotation=((((r.rotation+delta)%360)+540)%360)-180;
     });
   });
 }
 $m('ReferenceReset').addEventListener('click',()=>{
   const r=atelierRefCurrent();if(r)atelierRefSnapshotBefore(()=>{
      Object.assign(r,{zoom:1,offsetX:0,offsetY:0,rotation:0,mirror:false,opacity:.87});
   });
 });
 $m('ReferenceDelete').addEventListener('click',()=>{
   const r=atelierRefCurrent();if(!r)return;
   atelierRefSnapshotBefore(m=>{
      m.references=m.references.filter(v=>v.id!==r.id);
      m.referenceLayout.active=m.references[0]?.id||null;
      atelierRefTransient.delete(r.id);
   });
 });
 $m('ReferenceShow').addEventListener('change',e=>{
   const r=atelierRefCurrent();if(r)atelierRefSnapshotBefore(()=>{r.visible=e.target.checked;});
 });
 // Range 'input' drives only ephemeral preview. Committing on 'change'
 // checkpoints BEFORE updating the saved model (reliable Undo semantics).
 for(const [id,key,lo,hi]of [['ReferenceZoom','zoom',.25,5],['ReferenceOpacity','opacity',.15,1]]){
   const el=$m(id);
   el.addEventListener('input',()=>{
     const r=atelierRefCurrent();if(!r)return;
     const value=Number(el.value);
     if(!Number.isFinite(value)||value<lo||value>hi)return;
     atelierRefTransient.set(r.id,{...(atelierRefTransient.get(r.id)||{}),[key]:value});
     atelierRefPaint();
   });
   el.addEventListener('change',()=>{
     const r=atelierRefCurrent();if(!r)return;
     const value=Number(el.value);
     atelierRefTransient.delete(r.id);
     if(!Number.isFinite(value)||value<lo||value>hi){atelierRefPaint();return;}
     if(r[key]!==value)atelierRefSnapshotBefore(()=>{r[key]=value;});
   });
 }
 const handle=$m('ReferenceHandle');
 handle.addEventListener('pointerdown',atelierRefDockPointerDown);
 handle.addEventListener('pointermove',atelierRefDockPointerMove);
 handle.addEventListener('pointerup',atelierRefDockPointerUp);
 handle.addEventListener('pointercancel',atelierRefDockPointerUp);
 const frame=$m('ReferenceImageFrame');
 frame.addEventListener('pointerdown',atelierRefImagePointerDown);
 frame.addEventListener('pointermove',atelierRefImagePointerMove);
 frame.addEventListener('pointerup',atelierRefImagePointerUp);
 frame.addEventListener('pointercancel',atelierRefImagePointerUp);
 window.SWYRL_ENGINE_REFERENCE=Object.freeze({status:()=>({
   count:model()?.references?.length||0,
   active:model()?.referenceLayout?.active||null,
   open:!!model()?.referenceLayout?.open,
   collapsed:!!model()?.referenceLayout?.collapsed,
   imageDataBytes:model()?.references?.map(r=>r.data.length)||[],
   cameraAngle:atelierRefCurrent()?.angle||null
 })});
 atelierRefPaint();
}
