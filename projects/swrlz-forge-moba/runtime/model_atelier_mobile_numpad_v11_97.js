// §E v11.97 native mobile numeric editor. Tap without focusing a browser input.
// Preserve ordinary keyboard entry on desktop and all original change handlers.
function seMobileNumberPadInstall(){
 if(document.getElementById('seMobileNumberPad'))return;
 const box=document.createElement('div');
 box.id='seMobileNumberPad';
 box.className='se-mobile-numpad';
 box.hidden=true;
 box.innerHTML='<div class="se-mobile-numpad-shade" data-se-cancel="1"></div>'
  +'<section class="se-mobile-numpad-dialog" role="dialog" aria-modal="true" aria-labelledby="seMobileNumTitle">'
  +'<h3 id="seMobileNumTitle">Edit value</h3><output id="seMobileNumValue" aria-live="polite">0</output>'
  +'<p id="seMobileNumHelp">Use the number buttons to change this value.</p>'
  +'<div class="se-mobile-numpad-grid">'
  +['7','8','9','4','5','6','1','2','3','±','0','.'].map(v=>'<button type="button" data-se-digit="'+v+'">'+v+'</button>').join('')
  +'</div><div class="se-mobile-numpad-actions">'
  +'<button type="button" data-se-back="1">⌫ Delete</button>'
  +'<button type="button" data-se-clear="1">Clear</button>'
  +'<button type="button" data-se-cancel="1">Cancel</button>'
  +'<button type="button" class="se-mobile-numpad-apply" data-se-apply="1">Apply</button>'
  +'</div></section>';
 document.body.append(box);
 const dialog=box.querySelector('.se-mobile-numpad-dialog');
 const output=box.querySelector('#seMobileNumValue');
 const help=box.querySelector('#seMobileNumHelp');
 const apply=box.querySelector('[data-se-apply]');
 let selected=null,draft='';
 const coarse=()=>window.matchMedia('(pointer: coarse)').matches;
 function position(){
  if(box.hidden)return;
  const vv=window.visualViewport;
  const w=vv?.width||window.innerWidth,h=vv?.height||window.innerHeight;
  dialog.style.left=((vv?.offsetLeft||0)+w/2)+'px';
  dialog.style.top=((vv?.offsetTop||0)+h/2)+'px';
  dialog.style.maxWidth=Math.max(180,w-24)+'px';
  dialog.style.maxHeight=Math.max(170,h-24)+'px';
 }
 function valid(){
  const n=Number(draft);
  if(!draft.trim()||!Number.isFinite(n))return false;
  if(selected?.min!==''&&n<Number(selected.min))return false;
  if(selected?.max!==''&&n>Number(selected.max))return false;
  return true;
 }
 function refresh(){
  output.textContent=draft||' ';
  apply.disabled=!valid();
  help.textContent=valid()?'Tap Apply to update the model.':
      'Enter a number within this field’s allowed range.';
 }
 function close(){
  box.hidden=true;
  selected=null;draft='';
 }
 function open(input){
  selected=input;draft=input.value||'0';
  const match=input.id.match(/modelAtelier(position|rotation|scale)([012])$/i);
  const title=match?match[1][0].toUpperCase()+match[1].slice(1)+' '+['X','Y','Z'][Number(match[2])]:
    (input.closest('label')?.textContent||input.getAttribute('aria-label')||'Model value').trim().slice(0,65);
  box.querySelector('#seMobileNumTitle').textContent=title;
  box.hidden=false;refresh();position();
 }
 // Capture before the native input receives touch focus and triggers browser zoom.
 document.addEventListener('pointerdown',event=>{
  const node=event.target;
  const input=node?.closest?.('.model-atelier input[type="number"]');
  if(!coarse()||!input||input.disabled||input.readOnly)return;
  event.preventDefault();
  event.stopImmediatePropagation();
  open(input);
 },true);
 // Touch platforms without Pointer Events: avoid activating native input focus.
 if(!window.PointerEvent)document.addEventListener('touchstart',event=>{
  const input=event.target?.closest?.('.model-atelier input[type="number"]');
  if(!coarse()||!input||input.disabled||input.readOnly)return;
  event.preventDefault();event.stopPropagation();open(input);
 },{capture:true,passive:false});
 box.addEventListener('click',event=>{
  const b=event.target?.closest?.('button,[data-se-cancel]');
  if(!b)return;
  if(b.hasAttribute('data-se-cancel')){close();return;}
  const digit=b.getAttribute('data-se-digit');
  if(digit!==null){
   if(digit==='±')draft=draft.startsWith('-')?draft.slice(1):'-'+draft;
   else if(digit==='.'){if(!draft.includes('.'))draft=(draft||'0')+'.';}
   else if(draft==='0')draft=digit;
   else if(draft==='-0')draft='-'+digit;
   else draft+=digit;
  }else if(b.hasAttribute('data-se-back'))draft=draft.slice(0,-1);
  else if(b.hasAttribute('data-se-clear'))draft='';
  else if(b.hasAttribute('data-se-apply')){
   if(!selected||!selected.isConnected||!valid())return;
   const input=selected;
   const newValue=String(Number(draft));
   close();
   if(input.value!==newValue){
    input.value=newValue;
    input.dispatchEvent(new Event('change',{bubbles:true}));
   }
   return;
  }
  refresh();
 });
 document.addEventListener('keydown',event=>{
  if(box.hidden)return;
  if(event.key==='Escape'){event.preventDefault();event.stopImmediatePropagation();close();}
 },true);
 window.visualViewport?.addEventListener('resize',position,{passive:true});
 window.visualViewport?.addEventListener('scroll',position,{passive:true});
 window.addEventListener('resize',position,{passive:true});
}
