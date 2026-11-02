// §E v11.226 material/texture authoring UI — generated textures, direct paint,
// live standard material assignment, portable JSON/PNG. Mobile-first; no new renderer.
const SE225_EDIT_FIELDS=[
 ['roughness','Roughness',0,1,.02],['metalness','Metalness',0,1,.02],
 ['glow','Glow intensity',0,3,.05],['opacity','Opacity',.1,1,.02],
 ['scale','Pattern detail',1,24,1],['tiling','UV repeat',.25,8,.25],['seed','Pattern seed',1,9999,1]
];
function se225MField(label,node){
 const row=document.createElement('label');row.className='se225-m-field';
 const name=document.createElement('span');name.textContent=label;row.append(name,node);return row;
}
function se225MControl(type,field,label){
 const input=document.createElement('input');input.type=type;input.dataset.se225Field=field;
 input.setAttribute('aria-label',label);return se225MField(label,input);
}
function se225MSection(label){
 const d=document.createElement('details');d.className='se225-m-section';d.open=true;
 const s=document.createElement('summary');s.textContent=label;d.append(s);return d;
}
function se225MButton(parent,id,label,handler){
 const b=document.createElement('button');b.type='button';b.id=id;b.textContent=label;
 b.addEventListener('click',handler);parent.append(b);return b;
}
function se225MSelect(parent,id,options){
 const el=document.createElement('select');el.id=id;
 for(const [value,text] of options){const op=document.createElement('option');op.value=value;op.textContent=text;el.append(op);}
 parent.append(el);return el;
}
function se225MaterialUISelected(){
 let def=se225MaterialGet(se225Mat.selected);
 if(!def){def=se225MaterialData()?.materials[0]||null;se225Mat.selected=def?.id||null;}
 return def;
}
function se225MaterialUIStatus(message,error=false){
 const el=document.getElementById('se225MStatus');if(!el)return;
 el.textContent=message;el.classList.toggle('se225-error',!!error);
}
function se225MaterialUIPreview(){
 const c=document.getElementById('se225MCanvas'),m=se225MaterialUISelected();
 if(!c)return;
 const ctx=c.getContext('2d');
 ctx.clearRect(0,0,c.width,c.height);
 if(!m){ctx.fillStyle='#192a38';ctx.fillRect(0,0,256,256);return;}
 const canvas=se225MaterialTexture(m).canvas;
 ctx.drawImage(canvas,0,0,c.width,c.height);
}
function se225MaterialUIRefresh(){
 const pane=document.getElementById('se225MaterialsPanel');if(!pane)return;
 const data=se225MaterialData(),def=se225MaterialUISelected();
 const list=pane.querySelector('#se225MList');list.replaceChildren();
 for(const material of data?.materials||[]){
  const option=document.createElement('option');option.value=material.id;option.textContent=material.name;
  list.append(option);
 }
 list.value=def?.id||'';
 pane.querySelector('#se225MCount').textContent=(data?.materials.length||0)+' / 12 materials';
 pane.querySelector('#se225MCreate').disabled=!data||data.materials.length>=12||playing||simulating;
 pane.querySelector('#se225MDuplicate').disabled=!def||playing||simulating;
 pane.querySelector('#se225MDelete').disabled=!def||playing||simulating;
 const edit=pane.querySelector('#se225MEdit');edit.hidden=!def;
 if(def){
  for(const input of edit.querySelectorAll('[data-se225-field]')){
   input.value=String(def[input.dataset.se225Field]);input.disabled=playing||simulating;
  }
 }
 const targets=pane.querySelector('#se225MTarget'),previous=se225Mat.target||selected?.userData?.id||'';
 targets.replaceChildren();
 const empty=document.createElement('option');empty.value='';empty.textContent='Select a scene actor';targets.append(empty);
 for(const a of actors){
  if(!a?.userData?.id||a.userData.actorType==='group')continue;
  const op=document.createElement('option');op.value=a.userData.id;
  op.textContent=a.name+' · '+a.userData.actorType;targets.append(op);
 }
 targets.value=actors.some(a=>a.userData?.id===previous)?previous:'';
 se225Mat.target=targets.value||null;
 const assigned=data?.assignments.find(x=>x.actorId===se225Mat.target);
 const found=assigned?.materialId?data.materials.find(x=>x.id===assigned.materialId):null;
 pane.querySelector('#se225MAssigned').textContent=found?'Assigned: '+found.name:'No custom material on actor';
 pane.querySelector('#se225MAssign').disabled=!def||!se225Mat.target||playing||simulating;
 pane.querySelector('#se225MUnassign').disabled=!assigned||playing||simulating;
 pane.querySelector('#se225MPaintUndo').disabled=!def?.strokes.length||playing||simulating;
 pane.querySelector('#se225MPaintClear').disabled=!def?.strokes.length||playing||simulating;
 pane.querySelector('#se225MExportTexture').disabled=!def;
 pane.querySelector('#se225MImportImage').disabled=!def||playing||simulating;
 pane.querySelector('#se225MExportLibrary').disabled=!data;
 pane.querySelector('#se225MImportLibrary').disabled=playing||simulating;
 se225MaterialUIPreview();
 if(def)se225MaterialUIStatus('Editing '+def.name+'. Applied materials and texture strokes save with this project.');
 else se225MaterialUIStatus(data?'Select a preset to create a material.':'Project material data is invalid. Import to repair.',!data);
}
function se225MaterialUIEdit(input){
 const m=se225MaterialUISelected();
 if(!m||playing||simulating)return;
 const field=input.dataset.se225Field;
 if(!field)return;
 let value=input.value;
 if(input.type==='number'||input.type==='range'){
  if(!input.checkValidity()||!value.trim()||!Number.isFinite(+value)){
   se225MaterialUIStatus('Invalid '+field+' value.',true);se225MaterialUIRefresh();return;
  }
  value=Number(value);
 }
 if(!se225MaterialEdit(m.id,{[field]:value})){se225MaterialUIRefresh();return;}
 se225MaterialUIStatus('Saved '+m.name+' · '+field+'.');
}
function se225MaterialUIDownload(data,filename,mime){
 const blob=new Blob([data],{type:mime}),url=URL.createObjectURL(blob);
 const a=document.createElement('a');a.href=url;a.download=filename;document.body.append(a);
 a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),2000);
}
function se225MaterialUIExportLibrary(){
 const model=se225MaterialExport();if(!model){se225MaterialUIStatus('No valid library available.',true);return;}
 se225MaterialUIDownload(JSON.stringify(model,null,2)+'\n','materials.swyrl.json','application/json');
}
async function se225MaterialUIImportLibrary(file){
 if(!file)return;
 if(file.size>2400000){se225MaterialUIStatus('Material library exceeds the 2.4 MB limit.',true);return;}
 try{
  const json=JSON.parse(await file.text());
  const data=se225ValidateLibrary(json);
  if(!confirm('Replace project material library with '+data.materials.length+' materials? Existing actor assignments will be cleared. Undo is available.'))return;
  if(se225MaterialImport(data)){
   se225Mat.selected=data.materials[0]?.id||null;se225MaterialUIRefresh();
   se225MaterialUIStatus('Imported '+data.materials.length+' validated material definitions.');
  }
 }catch(error){se225MaterialUIStatus('Import rejected: '+String(error.message||error).slice(0,130),true);}
}
async function se225MaterialUIImportImage(file){
 const m=se225MaterialUISelected();if(!m||!file)return;
 if(!['image/png','image/jpeg'].includes(file.type)||file.size>750000){
  se225MaterialUIStatus('Use a PNG/JPEG under 750 KB.',true);return;
 }
 const url=URL.createObjectURL(file),img=new Image();
 try{
  await new Promise((resolve,reject)=>{img.onload=resolve;img.onerror=()=>reject(Error('Cannot decode image'));img.src=url;});
  if(img.naturalWidth>4096||img.naturalHeight>4096)throw Error('Image dimensions too large.');
  const temp=document.createElement('canvas');temp.width=256;temp.height=256;
  const cx=temp.getContext('2d');cx.drawImage(img,0,0,256,256);
  const png=temp.toDataURL('image/png');
  if(png.length>360000)throw Error('PNG texture exceeds project limit; choose a smaller or simpler image.');
  if(!se225MaterialEdit(m.id,{pattern:'image',imageData:png}))throw Error('Cannot update this material.');
  se225MaterialUIStatus('Imported texture image, scaled to 256×256.');
 }catch(error){se225MaterialUIStatus('Texture import failed: '+error.message,true);}
 finally{URL.revokeObjectURL(url);}
}
function se225MaterialUIExportTexture(){
 const m=se225MaterialUISelected();if(!m)return;
 const canvas=se225MaterialTexture(m).canvas;
 const a=document.createElement('a');a.href=canvas.toDataURL('image/png');
 a.download=m.name.toLowerCase().replace(/[^a-z0-9]+/g,'-').slice(0,55)+'.png';
 document.body.append(a);a.click();a.remove();
 se225MaterialUIStatus('Exported 256×256 PNG texture.');
}
function se225MaterialUIPaintDown(e){
 if(e.button!==0&&e.pointerType!=='touch')return;
 const m=se225MaterialUISelected();
 if(!m||playing||simulating)return;
 if(m.strokes.length>=SE225_STROKES){se225MaterialUIStatus('160 paint strokes maximum. Clear or Undo a stroke.',true);return;}
 const canvas=e.currentTarget;
 const rect=canvas.getBoundingClientRect();
 const point=[se225MClamp((e.clientX-rect.left)/rect.width,0,1),se225MClamp((e.clientY-rect.top)/rect.height,0,1)];
 const color=document.getElementById('se225MBrushColor').value,
  width=Number(document.getElementById('se225MBrushSize').value)/256;
 se225Mat.paint={id:m.id,color,width,points:[point],pointer:e.pointerId};
 try{canvas.setPointerCapture(e.pointerId);}catch{}
 e.preventDefault();
}
function se225MaterialUIPaintMove(e){
 const p=se225Mat.paint;if(!p||p.pointer!==e.pointerId)return;
 const canvas=e.currentTarget,r=canvas.getBoundingClientRect();
 const point=[se225MClamp((e.clientX-r.left)/r.width,0,1),se225MClamp((e.clientY-r.top)/r.height,0,1)];
 const last=p.points.at(-1);
 if(Math.hypot(point[0]-last[0],point[1]-last[1])<.003)return;
 if(p.points.length>=SE225_POINTS)return;
 p.points.push(point);
 const ctx=canvas.getContext('2d');
 ctx.beginPath();ctx.strokeStyle=p.color;ctx.fillStyle=p.color;ctx.lineCap='round';
 ctx.lineJoin='round';ctx.lineWidth=p.width*256;
 ctx.moveTo(last[0]*256,last[1]*256);ctx.lineTo(point[0]*256,point[1]*256);
 ctx.stroke();
 e.preventDefault();
}
function se225MaterialUIPaintEnd(e){
 const p=se225Mat.paint;if(!p||p.pointer!==e.pointerId)return;
 se225Mat.paint=null;
 const m=se225MaterialGet(p.id);
 if(m&&p.points.length){
  const strokes=[...m.strokes,{color:p.color,width:p.width,points:p.points}];
  if(!se225MaterialEdit(p.id,{strokes})){
   se225MaterialUIRefresh();return;
  }
  se225MaterialUIStatus('Paint stroke saved · '+strokes.length+' / '+SE225_STROKES);
 }
 se225MaterialUIPreview();
}
function se225MaterialUIInstall(container){
 let panel=document.getElementById('se225MaterialsPanel');
 if(panel)return panel;
 panel=document.createElement('section');panel.id='se225MaterialsPanel';panel.className='se225-m-panel';panel.hidden=true;
 panel.setAttribute('aria-label','Material & Texture Studio editor');
 panel.innerHTML=
  '<div class="se225-m-scroll"><div class="se225-m-title"><strong>🎨 Material & Texture Studio</strong>'+
  '<span>Procedural • hand-painted • physically based</span></div>'+
  '<div class="se225-m-row"><label>Starting material<select id="se225MPreset"></select></label>'+
  '<button id="se225MCreate" type="button">+ Create</button></div>'+
  '<div class="se225-m-row"><label>My materials<select id="se225MList"></select></label>'+
  '<small id="se225MCount">0 / 12 materials</small></div>'+
  '<div class="se225-m-actions"><button id="se225MDuplicate">Duplicate</button>'+
  '<button id="se225MDelete">Delete</button></div>'+
  '<div id="se225MEdit" class="se225-m-edit"></div>'+
  '<div class="se225-m-section se225-m-assign"><strong>Assign to a scene object</strong>'+
  '<label>Target<select id="se225MTarget"></select></label>'+
  '<small id="se225MAssigned">No custom material on actor</small>'+
  '<div class="se225-m-actions"><button id="se225MAssign">Apply material</button>'+
  '<button id="se225MUnassign">Restore original</button></div></div>'+
  '<div class="se225-m-actions"><button id="se225MExportLibrary">Export JSON library</button>'+
  '<button id="se225MImportLibrary">Import JSON library</button></div>'+
  '<input type="file" id="se225MFile" accept=".json,application/json" hidden>'+
  '<p id="se225MStatus" class="se225-m-hint" role="status" aria-live="polite"></p></div>';
 container.append(panel);
 const get=id=>panel.querySelector('#'+id);
 for(const [key,record] of Object.entries(SE225_M_PRESETS)){
  const option=document.createElement('option');option.value=key;option.textContent=record[0];get('se225MPreset').append(option);
 }
 const edit=get('se225MEdit'),basics=se225MSection('Material properties');
 const name=document.createElement('input');name.type='text';name.maxLength=65;name.dataset.se225Field='name';
 basics.append(se225MField('Name',name));
 for(const [field,label] of [['baseColor','Base color'],['accentColor','Pattern color'],['emissive','Emission color']]){
  basics.append(se225MControl('color',field,label));
 }
 for(const [field,label,a,b,step] of SE225_EDIT_FIELDS){
  const row=se225MControl('number',field,label),input=row.querySelector('input');
  input.min=String(a);input.max=String(b);input.step=String(step);input.inputMode='decimal';
  basics.append(row);
 }
 edit.append(basics);
 const texture=se225MSection('Texture generator & painting');
 const pattern=document.createElement('select');pattern.dataset.se225Field='pattern';
 for(const key of SE225_PATTERNS){const op=document.createElement('option');op.value=key;op.textContent=key[0].toUpperCase()+key.slice(1);pattern.append(op);}
 texture.append(se225MField('Texture pattern',pattern));
 const canvas=document.createElement('canvas');canvas.id='se225MCanvas';canvas.width=256;canvas.height=256;
 canvas.setAttribute('aria-label','Editable 256 by 256 texture paint surface');canvas.style.touchAction='none';
 texture.append(canvas);
 const brush=document.createElement('div');brush.className='se225-m-brush';
 const color=document.createElement('input');color.type='color';color.id='se225MBrushColor';color.value='#f7e69f';
 const size=document.createElement('input');size.type='range';size.id='se225MBrushSize';size.min='2';size.max='50';size.value='12';
 brush.append(se225MField('Brush color',color),se225MField('Brush size',size));texture.append(brush);
 const paintButtons=document.createElement('div');paintButtons.className='se225-m-actions';
 se225MButton(paintButtons,'se225MPaintUndo','Undo brush stroke',()=>{
  const m=se225MaterialUISelected();if(m?.strokes.length)se225MaterialEdit(m.id,{strokes:m.strokes.slice(0,-1)});
 });
 se225MButton(paintButtons,'se225MPaintClear','Clear paint',()=>{
  const m=se225MaterialUISelected();if(m?.strokes.length&&confirm('Clear the painted strokes from this texture? Undo will restore them.'))se225MaterialEdit(m.id,{strokes:[]});
 });
 texture.append(paintButtons);
 const imageButtons=document.createElement('div');imageButtons.className='se225-m-actions';
 se225MButton(imageButtons,'se225MImportImage','Import PNG/JPEG',()=>get('se225MImageFile').click());
 se225MButton(imageButtons,'se225MExportTexture','Export PNG',se225MaterialUIExportTexture);
 texture.append(imageButtons);
 const imageFile=document.createElement('input');imageFile.id='se225MImageFile';imageFile.type='file';
 imageFile.accept='image/png,image/jpeg';imageFile.hidden=true;texture.append(imageFile);
 const hint=document.createElement('small');hint.className='se225-m-hint';
 hint.textContent='Paint directly onto the texture swatch. Brush strokes, pattern and PBR properties save inside the project. PNG export produces a texture for other workflows.';
 texture.append(hint);edit.append(texture);
 get('se225MCreate').addEventListener('click',()=>{
  const v=se225MaterialCreate(get('se225MPreset').value);
  if(v)se225MaterialUIStatus('Created '+v.name+'.');
 });
 get('se225MList').addEventListener('change',e=>{se225Mat.selected=e.target.value;se225MaterialUIRefresh();});
 get('se225MDuplicate').addEventListener('click',()=>se225MaterialDuplicate(se225Mat.selected));
 get('se225MDelete').addEventListener('click',()=>se225MaterialDelete(se225Mat.selected));
 get('se225MTarget').addEventListener('change',e=>{se225Mat.target=e.target.value;se225MaterialUIRefresh();});
 get('se225MAssign').addEventListener('click',()=>{
  if(se225MaterialAssign(se225Mat.target,se225Mat.selected)){
   se225MaterialSync(true);
   se225MaterialUIStatus('Applied material to selected actor · native 3D preview updated.');
  }
 });
 get('se225MUnassign').addEventListener('click',()=>{
  if(se225MaterialUnassign(se225Mat.target)){
   se225MaterialSync(true);se225MaterialUIStatus('Restored original actor material.');
  }
 });
 get('se225MExportLibrary').addEventListener('click',se225MaterialUIExportLibrary);
 get('se225MImportLibrary').addEventListener('click',()=>get('se225MFile').click());
 get('se225MFile').addEventListener('change',async e=>{
  await se225MaterialUIImportLibrary(e.target.files?.[0]);e.target.value='';
 });
 imageFile.addEventListener('change',async e=>{
  await se225MaterialUIImportImage(e.target.files?.[0]);e.target.value='';
 });
 canvas.addEventListener('pointerdown',se225MaterialUIPaintDown);
 canvas.addEventListener('pointermove',se225MaterialUIPaintMove);
 canvas.addEventListener('pointerup',se225MaterialUIPaintEnd);
 canvas.addEventListener('pointercancel',e=>{if(se225Mat.paint?.pointer===e.pointerId){se225Mat.paint=null;se225MaterialUIPreview();}});
 edit.addEventListener('change',event=>{
  const input=event.target;if(input?.matches?.('[data-se225-field]'))se225MaterialUIEdit(input);
 });
 se225MaterialUIRefresh();se225Mat.ui=panel;return panel;
}
window.SWYRL_ENGINE_MATERIAL_STUDIO=Object.freeze({
 open:()=>window.SWYRL_ENGINE_STUDIOS?.open?.('materials'),
 refresh:se225MaterialUIRefresh
});
