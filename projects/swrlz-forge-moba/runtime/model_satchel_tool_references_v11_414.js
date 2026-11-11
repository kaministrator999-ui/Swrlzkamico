/* SE414_SATCHEL_NATIVE_TOOL_REFERENCES_START
 * Read native button labels/glyphs and reuse the actual XR console icon painter.
 * Read-only guidance: never duplicate event handlers or change native controls.
 */
(function se414SatchelToolReferences(){
 'use strict';
 const tools={
  scale:{name:'Scale',flat:'#modelAtelierPanel [data-se320-transform="scale"]',vr:'scale',vrName:'Scale'},
  move:{name:'Move',flat:'#modelAtelierPanel [data-se320-transform="move"]',vr:'move',vrName:'Move'},
  rotate:{name:'Rotate',flat:'#modelAtelierPanel [data-se320-transform="rotate"]',vr:'rotate',vrName:'Rotate'},
  add:{name:'Add mesh',flat:'#modelAtelierAdd',vr:'create-box',vrName:'Cube'},
  shape:{name:'Shape',flat:'#modelAtelierKind',vr:'create-box',vrName:'Cube'},
  duplicate:{name:'Duplicate',flat:'#modelAtelierDuplicate',vr:'duplicate',vrName:'Duplicate'},
  material:{name:'Material',flat:'#modelAtelierMaterial',vr:null,vrName:'Material (flat editor)'},
  color:{name:'Color',flat:'#modelAtelierColor',vr:null,vrName:'Color (flat editor)'},
  views:{name:'Views',flat:'#seAtelierViewMenu summary',vr:'cameras',vrName:'Angles'},
  save:{name:'Save Project',flat:'[data-se371-controls] button:first-child',vr:'save-local',vrName:'Save project'}
 };
 const byStep=[
  ['scale'],['add','shape','move'],['add','shape','scale'],['add','move','rotate'],
  ['duplicate','move'],['material','color'],['views','save']
 ];
 const terms=[
  ['Save to Account','save'],['Save Project','save'],['Add Box','add'],
  ['Duplicate','duplicate'],['Material','material'],['Rotate','rotate'],
  ['Scale','scale'],['Shape','shape'],['Color','color'],['Move','move'],
  ['Orbit','views'],['Views','views'],['Add','add']
 ];
 const matcher=new RegExp('\\b('+terms.map(([word])=>word).join('|')+')\\b','gi');
 function references(index){return (byStep[index]||[]).map(key=>({key,...tools[key]}));}
 function nativeButton(key){const tool=tools[key];return tool?document.querySelector(tool.flat):null;}
 function buttonLook(key,mini=false){
  const native=nativeButton(key),tool=tools[key];
  const chip=document.createElement('span');chip.className='se414-native-look'+(mini?' se414-mini':'');
  if(!tool)return chip;
  let label=tool.name;
  if(native?.tagName==='BUTTON'||native?.tagName==='SUMMARY')
   label=(native.textContent||'').trim().replace(/\s+/g,' ').slice(0,48)||label;
  else if(native?.tagName==='SELECT')label=tool.name+' ▾';
  else if(native?.tagName==='INPUT')label=tool.name+' ◼';
  chip.textContent=label;
  // Copy visual presentation, not IDs, event listeners or native state.
  if(native&&typeof getComputedStyle==='function'){
   const css=getComputedStyle(native);
   for(const prop of ['backgroundColor','color','borderColor','borderStyle','borderWidth','borderRadius'])
    try{chip.style[prop]=css[prop];}catch(_){}
  }
  chip.setAttribute('aria-hidden','true');return chip;
 }
 function inline(container,source,index){
  const allowed=new Set(byStep[index]||[]),fragment=document.createDocumentFragment();
  matcher.lastIndex=0;let from=0,match;
  while((match=matcher.exec(source))){
   const key=terms.find(([word])=>word.toLowerCase()===match[0].toLowerCase())?.[1];
   if(!allowed.has(key))continue;
   if(match.index>from)fragment.append(document.createTextNode(source.slice(from,match.index)));
   const together=document.createElement('span');together.className='se414-inline-ref';
   together.append(buttonLook(key,true),document.createTextNode(match[0]));
   fragment.append(together);from=match.index+match[0].length;
  }
  fragment.append(document.createTextNode(source.slice(from)));container.replaceChildren(fragment);
 }
 function renderFlat(panel,index,step){
  if(!panel||!step||!Number.isInteger(index))return;
  const label=panel.querySelector('#se412Tool');if(!label)return;
  let host=panel.querySelector('#se414ToolGuide');
  if(!host){host=document.createElement('div');host.id='se414ToolGuide';
   host.setAttribute('aria-label','Native tool button reference');label.after(host);}
  host.replaceChildren();
  const heading=document.createElement('small');heading.textContent='FIND THESE ACTUAL CONTROLS';host.append(heading);
  const line=document.createElement('div');line.className='se414-button-row';host.append(line);
  for(const reference of references(index)){
   const item=document.createElement('span');item.className='se414-tool-item';
   item.append(buttonLook(reference.key));
   const name=document.createElement('span');name.textContent=reference.name;item.append(name);line.append(item);
  }
  let help=panel.querySelector('#se414ToolExplanation');
  if(!help){help=document.createElement('p');help.id='se414ToolExplanation';host.after(help);}
  help.textContent=[1,2,3].includes(index)
   ?'In flat Model Studio, Add sphere makes a sphere. Select that part, then use Shape → box. In VR, Create → Cube places a box directly.'
   :index===5?'Material and Color live in the regular Model Studio inspector; this does not claim a matching general-purpose VR material button.'
   :'Button miniatures are visual references, not extra editing controls.';
  const task=panel.querySelector('#se412Task'),hint=panel.querySelector('#se412HintText');
  if(task)inline(task,step.task||'',index);
  if(hint)inline(hint,step.hint||'',index);
 }
 const wordVR={scale:'scale',move:'move',rotate:'rotate',add:'create-box',
  duplicate:'duplicate',view:'cameras',views:'cameras',orbit:'cameras',save:'save-local'};
 function renderRich(ctx,text,x,y,width,lh,limit,vrUI){
  let atX=x,atY=y,lines=1;
  const words=String(text||'').split(/\s+/).filter(Boolean);
  for(const word of words){
   const match=/^[A-Za-z]+/.exec(word),action=match?wordVR[match[0].toLowerCase()]:null;
   const v=ctx.measureText(word+' ').width,extra=action&&vrUI?.drawGuideIcon?29:0;
   if(atX+v+extra>x+width&&atX>x){if(lines>=limit)break;atX=x;atY+=lh;lines++;}
   if(extra){vrUI.drawGuideIcon(ctx,action,atX+12,atY-8,25,'#a6e8d3');atX+=extra;}
   ctx.fillText(word+' ',atX,atY);atX+=v;
  }
 }
 function renderVR(ctx,step,ui){
  if(!ctx||!step)return false;
  const refs=references(step.index);
  if(!ui?.drawGuideIcon)return false;
  ctx.save();ctx.font='bold 25px system-ui,sans-serif';ctx.fillStyle='#d0b3fc';
  ctx.fillText('FIND THESE BUTTONS',32,313);
  for(let i=0;i<refs.length;i++){
   const ref=refs[i],left=32+i*326,top=325;
   ctx.beginPath();ctx.roundRect(left,top,Math.min(314,1024-left-32),57,11);
   ctx.fillStyle='#4a365f';ctx.fill();ctx.strokeStyle='#9d82be';ctx.lineWidth=2;ctx.stroke();
   if(ref.vr)ui.drawGuideIcon(ctx,ref.vr,left+30,top+28,42,'#d5fff2');
   else{ctx.fillStyle='#f3c58f';ctx.font='bold 32px system-ui';ctx.fillText('▾',left+18,top+39);}
   ctx.fillStyle='#fff4ff';ctx.font='bold 27px system-ui';
   ctx.fillText((ref.vrName||ref.name).slice(0,18),left+63,top+37);
  }
  ctx.restore();return true;
 }
 function vrTask(ctx,step,ui){
  ctx.save();ctx.font='29px system-ui,sans-serif';ctx.fillStyle='#f2e9fd';
  renderRich(ctx,step.task,32,416,944,37,4,ui);ctx.restore();
 }
 function vrHint(ctx,step,ui){
  ctx.save();ctx.font='italic 27px system-ui,sans-serif';ctx.fillStyle='#d0b8e8';
  renderRich(ctx,'TIP: '+step.hint,32,559,944,32,2,ui);ctx.restore();
 }
 window.SWYRL_E_SATCHEL_BUTTON_GUIDE_414=Object.freeze({references,renderFlat,renderVR,vrTask,vrHint});
})();
 /* SE414_SATCHEL_NATIVE_TOOL_REFERENCES_END */