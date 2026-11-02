// §E v11.224 native Particle Studio UI. All values go through core validation.
// The panel is editor-only UI, not project geometry or an independent renderer.
const SE223_FIELDS=[
 ['rate','Particles / second',0,80,1],
 ['burst','Burst count',1,96,1],
 ['life','Lifetime (seconds)',.1,8,.1],
 ['speed','Initial speed',0,12,.1],
 ['spread','Direction spread',0,4,.05],
 ['gravity','Gravity (+ down)',-12,16,.1],
 ['drag','Air resistance',0,5,.05],
 ['size','Particle size',.025,.8,.025],
 ['radius','Emission radius',0,6,.1]
];
function se223UIInput(field,label,min,max,step){
 const row=document.createElement('label');row.className='se223-range-row';
 const top=document.createElement('span');top.textContent=label;
 const number=document.createElement('input');number.type='number';number.min=String(min);
 number.max=String(max);number.step=String(step);number.dataset.se223Field=field;
 number.setAttribute('aria-label',label);
 const slider=document.createElement('input');slider.type='range';slider.min=String(min);
 slider.max=String(max);slider.step=String(step);slider.dataset.se223Field=field;
 slider.setAttribute('aria-label',label+' slider');
 slider.addEventListener('input',()=>{number.value=slider.value;});
 number.addEventListener('input',()=>{slider.value=number.value;});
 const head=document.createElement('span');head.className='se223-range-head';head.append(top,number);
 row.append(head,slider);return row;
}
function se223UILabel(label,control){
 const node=document.createElement('label');node.className='se223-field';
 const text=document.createElement('span');text.textContent=label;node.append(text,control);return node;
}
function se223UISelect(field,label,options){
 const element=document.createElement('select');element.dataset.se223Field=field;
 element.setAttribute('aria-label',label);
 for(const [value,display] of options){const opt=document.createElement('option');opt.value=value;opt.textContent=display;element.append(opt);}
 return se223UILabel(label,element);
}
function se223UIColor(field,label){
 const input=document.createElement('input');input.type='color';input.dataset.se223Field=field;
 input.setAttribute('aria-label',label);return se223UILabel(label,input);
}
function se223UINumberVector(field,label,min,max,step){
 const group=document.createElement('fieldset');group.className='se223-vector';
 const legend=document.createElement('legend');legend.textContent=label;group.append(legend);
 for(const [i,axis] of ['X','Y','Z'].entries()){
  const inp=document.createElement('input');inp.type='number';inp.step=String(step);
  inp.min=String(min);inp.max=String(max);inp.inputMode='decimal';
  inp.dataset.se223Field=field;inp.dataset.se223Axis=String(i);
  inp.setAttribute('aria-label',label+' '+axis);
  group.append(se223UILabel(axis,inp));
 }
 return group;
}
function se223UISection(title){
 const node=document.createElement('details');node.className='se223-section';node.open=true;
 const sum=document.createElement('summary');sum.textContent=title;node.append(sum);return node;
}
function se223UISetStatus(text,error=false){
 const out=document.getElementById('se223Status');if(!out)return;
 out.textContent=text;out.classList.toggle('se223-error',error);
}
function se223UISelected(){
 const e=se223Get(se223State.selected);
 if(e)return e;
 const first=se223Data()?.emitters[0]||null;
 se223State.selected=first?.id||null;
 return first;
}
function se223UIRefresh(){
 const panel=document.getElementById('se223Panel');if(!panel)return;
 const library=se223Data(),current=se223UISelected();
 const list=panel.querySelector('#se223List');
 list.replaceChildren();
 for(const cfg of library?.emitters||[]){
  const o=document.createElement('option');o.value=cfg.id;
  o.textContent=(cfg.enabled?'✦ ':'○ ')+cfg.name;list.append(o);
 }
 list.value=current?.id||'';
 const empty=panel.querySelector('#se223Empty');
 const fields=panel.querySelector('#se223Editor');
 empty.hidden=!!current;fields.hidden=!current;
 panel.querySelector('#se223Remove').disabled=!current||!!playing||!!simulating;
 panel.querySelector('#se223Duplicate').disabled=!current||!!playing||!!simulating;
 panel.querySelector('#se223Burst').disabled=!current;
 panel.querySelector('#se223Attach').disabled=!current||!selected||!!playing||!!simulating;
 panel.querySelector('#se223Detach').disabled=!current||!current.attachActorId||!!playing||!!simulating;
 panel.querySelector('#se223ViewPlace').disabled=!current||!!playing||!!simulating;
 panel.querySelector('#se223Create').disabled=(library?.emitters.length||0)>=SE223_MAX_EMITTERS||!!playing||!!simulating;
 panel.querySelector('#se223Preview').textContent=se223State.preview?'■ Stop preview':'▶ Preview all';
 panel.querySelector('#se223Preview').setAttribute('aria-pressed',String(se223State.preview));
 panel.querySelector('#se223Count').textContent=(library?.emitters.length||0)+' / '+SE223_MAX_EMITTERS+' emitters';
 if(!current){
  se223UISetStatus(library?'Choose a preset to create your first 3D particle emitter.':
   'This project contains invalid particle data; import a valid library.',!library);
  return;
 }
 for(const input of fields.querySelectorAll('[data-se223-field]')){
  const field=input.dataset.se223Field;
  const value=input.dataset.se223Axis!=null?current[field][Number(input.dataset.se223Axis)]:current[field];
  if(input.type==='checkbox')input.checked=!!value;
  else input.value=String(value);
  input.disabled=!!playing||!!simulating;
 }
 const attached=current.attachActorId?actors.find(a=>a.userData.id===current.attachActorId):null;
 panel.querySelector('#se223AttachInfo').textContent=attached?
  'Following '+attached.name+' · position is local offset':
  current.attachActorId?'Attached object not found · world-space fallback':'World-space emitter';
 se223UISetStatus('Editing '+current.name+'. Changes are Undo/Redo steps and save with the project.');
}
function se223UIPreview(){
 se223State.preview=!se223State.preview;
 se223State.playingLast=false;
 if(!se223State.preview){for(const rec of se223State.live.values()){
  rec.particles.length=0;rec.geometry.setDrawRange(0,0);
 }}
 se223UIRefresh();
}
function se223UIAttach(){
 const cfg=se223UISelected();
 if(!cfg||!selected||!selected.userData?.id){se223UISetStatus('Select an actor in the level first.',true);return;}
 se223Update(cfg.id,{attachActorId:selected.userData.id,position:[0,1,0]});
}
function se223UIDetach(){
 const cfg=se223UISelected();if(!cfg)return;
 const world=se223Origin(cfg);
 se223Update(cfg.id,{attachActorId:null,position:world.toArray()});
}
function se223UIViewPlace(){
 const cfg=se223UISelected();if(!cfg||!camera)return;
 const direction=new THREE.Vector3();camera.getWorldDirection(direction);
 const position=camera.position.clone().addScaledVector(direction,4);
 se223Update(cfg.id,{attachActorId:null,position:[
  Math.max(-250,Math.min(250,position.x)),
  Math.max(-250,Math.min(250,position.y)),
  Math.max(-250,Math.min(250,position.z))]});
}
function se223UIApply(input){
 const cfg=se223UISelected();if(!cfg||playing||simulating)return;
 const field=input.dataset.se223Field,axis=input.dataset.se223Axis;
 if(!field)return;
 let value;
 if(input.type==='checkbox')value=input.checked;
 else if(input.type==='number'||input.type==='range'){
  if(input.value.trim()===''||!input.checkValidity()||!Number.isFinite(+input.value)){
   se223UISetStatus('Enter a valid '+field+' value.',true);se223UIRefresh();return;
  }
  value=Number(input.value);
 }else value=input.value;
 const changes={};
 if(axis!=null){const array=[...cfg[field]];array[Number(axis)]=value;changes[field]=array;}
 else changes[field]=value;
 if(se223Update(cfg.id,changes)===false){se223UIRefresh();return;}
 se223UISetStatus('Saved '+cfg.name+' · '+field+'.');
}
function se223UIExport(){
 const data=se223Data();if(!data){se223UISetStatus('Invalid emitter library; cannot export.',true);return;}
 const blob=new Blob([JSON.stringify(data,null,2)+'\n'],{type:'application/json'});
 const url=URL.createObjectURL(blob),a=document.createElement('a');
 a.href=url;a.download='particle-studio.vfx.json';document.body.append(a);a.click();a.remove();
 setTimeout(()=>URL.revokeObjectURL(url),1500);
 se223UISetStatus('Exported native emitter presets to JSON.');
}
async function se223UIImport(file){
 if(!file)return;
 if(file.size>65536){se223UISetStatus('Particle JSON must be below 64 KB.',true);return;}
 try{
  const data=se223ValidateModel(JSON.parse(await file.text()));
  if(!confirm('Replace this project’s particle emitters with '+data.emitters.length+' imported emitters?'))return;
  if(se223Replace(data)){se223State.preview=true;se223UIRefresh();
   se223UISetStatus('Imported '+data.emitters.length+' validated emitters. Undo is available.');}
 }catch(err){se223UISetStatus('Import rejected: '+String(err.message||err).slice(0,130),true);}
}
function se223UIOpen(){
 if(!document.getElementById('se223Panel'))se223Install();
 const panel=document.getElementById('se223Panel');if(!panel)return;
 panel.hidden=false;se223State.panel=true;se223UIRefresh();
 panel.querySelector('#se223List').focus();
}
function se223UIClose(){
 const panel=document.getElementById('se223Panel');if(panel)panel.hidden=true;
 se223State.panel=false;if(!playing&&!simulating)se223State.preview=false;
 const trigger=document.getElementById('se223Open');trigger?.focus();
}
function se223UIInstallDrag(panel){
 const handle=panel.querySelector('.se223-title');
 let drag=null;
 handle.addEventListener('pointerdown',e=>{
  if(e.target.closest('button')||e.button!==0)return;
  const rect=panel.getBoundingClientRect();
  drag={startX:e.clientX,startY:e.clientY,left:rect.left,top:rect.top,id:e.pointerId};
  handle.setPointerCapture?.(e.pointerId);e.preventDefault();
 });
 handle.addEventListener('pointermove',e=>{
  if(!drag||e.pointerId!==drag.id)return;
  panel.style.right='auto';panel.style.bottom='auto';
  panel.style.left=Math.max(4,Math.min(window.innerWidth-panel.offsetWidth-4,
   drag.left+e.clientX-drag.startX))+'px';
  panel.style.top=Math.max(4,Math.min(window.innerHeight-90,
   drag.top+e.clientY-drag.startY))+'px';
 });
 const stop=()=>drag=null;
 handle.addEventListener('pointerup',stop);
 handle.addEventListener('pointercancel',stop);
}
function se223Install(){
 if(document.getElementById('se223Panel'))return;
 const toolbar=document.querySelector('.viewport-toolbar');
 const button=document.createElement('button');button.id='se223Open';
 button.className='se223-open';button.type='button';button.textContent='✨ Particles';
 button.title='Create and edit 3D particle emitters in this project';
 button.addEventListener('click',se223UIOpen);
 if(toolbar)toolbar.append(button);else(document.querySelector('.viewport-wrap')||document.body).prepend(button);
 se223State.toolbar=button;
 const panel=document.createElement('section');
 panel.id='se223Panel';panel.className='se223-panel';panel.hidden=true;
 panel.setAttribute('role','dialog');panel.setAttribute('aria-modal','false');
 panel.setAttribute('aria-label','Particle Studio · 3D effects editor');
 panel.innerHTML=
  '<header class="se223-title"><div><strong>✦ Particle Studio</strong><small>Reusable 3D emitters · v11.224</small></div><button id="se223Close" type="button" aria-label="Close Particle Studio">×</button></header>'+
  '<div class="se223-scroll"><div class="se223-toolbar">'+
  '<label>Effect preset<select id="se223NewPreset" aria-label="New emitter preset"></select></label>'+
  '<button id="se223Create" type="button">+ Create</button></div>'+
  '<div class="se223-row"><label>Project emitters<select id="se223List" aria-label="Select emitter"></select></label>'+
  '<small id="se223Count">0 / 12 emitters</small></div>'+
  '<div class="se223-actions"><button id="se223Duplicate" type="button">Duplicate</button>'+
  '<button id="se223Remove" type="button">Delete</button>'+
  '<button id="se223Preview" type="button">▶ Preview all</button>'+
  '<button id="se223Burst" type="button">✦ Burst now</button></div>'+
  '<p id="se223Empty" class="se223-hint">Create a particle effect from a preset to begin.</p>'+
  '<div id="se223Editor" class="se223-editor"></div>'+
  '<div class="se223-actions"><button id="se223Export" type="button">Export VFX JSON</button>'+
  '<button id="se223Import" type="button">Import VFX JSON</button></div>'+
  '<input id="se223File" type="file" accept=".json,application/json" hidden>'+
  '<p id="se223Status" class="se223-hint" role="status" aria-live="polite"></p></div>';
 document.body.append(panel);
 const get=id=>panel.querySelector('#'+id);
 for(const [key,def] of Object.entries(SE223_PRESETS)){
  const opt=document.createElement('option');opt.value=key;opt.textContent=def.label;
  get('se223NewPreset').append(opt);
 }
 const editor=get('se223Editor');
 const basics=se223UISection('Emitter & spawn');
 const name=document.createElement('input');name.type='text';name.maxLength=64;
 name.dataset.se223Field='name';basics.append(se223UILabel('Emitter name',name));
 const enabled=document.createElement('input');enabled.type='checkbox';enabled.dataset.se223Field='enabled';
 basics.append(se223UILabel('Enabled',enabled));
 basics.append(se223UISelect('mode','Emission mode',[['continuous','Continuous'],['burst','One-shot burst']]));
 basics.append(se223UISelect('shape','Emission shape',
  [['point','Point'],['sphere','Sphere'],['circle','Circle / ring'],['box','Box volume']]));
 for(const row of SE223_FIELDS.slice(0,3))basics.append(se223UIInput(...row));
 editor.append(basics);
 const motion=se223UISection('Motion & physics');
 for(const row of SE223_FIELDS.slice(3,7))motion.append(se223UIInput(...row));
 motion.append(se223UINumberVector('direction','Emission direction',-3,3,.1));
 editor.append(motion);
 const appearance=se223UISection('Appearance');
 for(const row of SE223_FIELDS.slice(7))appearance.append(se223UIInput(...row));
 appearance.append(se223UIColor('startColor','Initial color'));
 appearance.append(se223UIColor('endColor','Fade color'));
 appearance.append(se223UISelect('blend','Blend mode',[['additive','Glow / additive'],['normal','Soft / alpha']]));
 editor.append(appearance);
 const spatial=se223UISection('Location & attachment');
 spatial.append(se223UINumberVector('position','Emitter position / local offset',-250,250,.1));
 const placements=document.createElement('div');placements.className='se223-actions';
 for(const [id,label] of [['se223ViewPlace','Place in view'],
  ['se223Attach','Attach selected actor'],['se223Detach','Detach']]){
  const b=document.createElement('button');b.id=id;b.type='button';b.textContent=label;placements.append(b);
 }
 spatial.append(placements);const att=document.createElement('small');att.id='se223AttachInfo';
 att.className='se223-hint';spatial.append(att);editor.append(spatial);
 get('se223Close').addEventListener('click',se223UIClose);
 get('se223Create').addEventListener('click',()=>{
  const e=se223Create(get('se223NewPreset').value);if(e){se223UIRefresh();se223UISetStatus('Created '+e.name+' · live preview on.');}
 });
 get('se223List').addEventListener('change',e=>{se223State.selected=e.target.value;se223UIRefresh();});
 get('se223Duplicate').addEventListener('click',()=>se223Duplicate(se223State.selected));
 get('se223Remove').addEventListener('click',()=>se223Remove(se223State.selected));
 get('se223Preview').addEventListener('click',se223UIPreview);
 get('se223Burst').addEventListener('click',()=>{se223State.preview=true;
  const count=se223Trigger(se223State.selected);se223UIRefresh();
  se223UISetStatus('Emitted '+count+' particles.');});
 get('se223ViewPlace').addEventListener('click',se223UIViewPlace);
 get('se223Attach').addEventListener('click',se223UIAttach);
 get('se223Detach').addEventListener('click',se223UIDetach);
 get('se223Export').addEventListener('click',se223UIExport);
 get('se223Import').addEventListener('click',()=>get('se223File').click());
 get('se223File').addEventListener('change',async e=>{
  await se223UIImport(e.target.files?.[0]);e.target.value='';});
 editor.addEventListener('change',event=>{
  if(event.target?.matches?.('[data-se223-field]'))se223UIApply(event.target);
 });
 panel.addEventListener('keydown',event=>{
  if(event.key==='Escape'){event.preventDefault();event.stopPropagation();se223UIClose();}
 });
 panel.addEventListener('pointerdown',event=>event.stopPropagation());
 panel.addEventListener('wheel',event=>event.stopPropagation(),{passive:true});
 se223UIInstallDrag(panel);se223UIRefresh();
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',se223Install,{once:true});
else queueMicrotask(se223Install);
window.SWYRL_ENGINE_PARTICLE_STUDIO=Object.freeze({
 open:se223UIOpen,close:se223UIClose,preview:se223UIPreview,refresh:se223UIRefresh
});
