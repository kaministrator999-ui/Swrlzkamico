/* SE340_MODEL_VR_UI_START */
// Native, world-space controls for the Model Studio adapter. No renderer,
// document mutation or input dispatch lives here; the workspace owns those.
function se340CreateModelVRUI(options){
 'use strict';
 const {THREE:T,actions={},status={}}=options||{};
 if(!T?.Group)throw Error('Model VR UI requires Three.js.');
 const root=new T.Group();root.name='Model Studio · VR tools';
 root.userData.editorOnly=true;root.userData.se340ModelUI=true;
 const targets=[],textures=new Set(),materials=new Set(),geometries=new Map();
 const buttons=new Map();let disposed=false,hovered=null,pressed=null,pressTimer=null,paintCount=0,signature='';
 let state={mode:'inspect',selectedName:'',hoverName:'',dragging:false,canUndo:false,canRedo:false,
  message:'Choose a part, then choose an edit tool.',tracking:null,precision:false,snap:false,helpVisible:false,controllerHint:'',page:'tools',viewMode:'orbit',aimHand:'right',aimYaw:0,aimPitch:0};
 const hasAction=id=>Array.isArray(actions)?actions.includes(id):!!actions?.[id];
 const clean=(value,max=84)=>String(value??'').replace(/[\r\n\t]/g,' ').slice(0,max);
 function geometry(w,h){
  const key=w+':'+h;if(!geometries.has(key))geometries.set(key,new T.PlaneGeometry(w,h));
  return geometries.get(key);
 }
 function rounded(c,x,y,w,h,r){
  c.beginPath();
  if(c.roundRect)c.roundRect(x,y,w,h,r);
  else{c.moveTo(x+r,y);c.lineTo(x+w-r,y);c.quadraticCurveTo(x+w,y,x+w,y+r);
   c.lineTo(x+w,y+h-r);c.quadraticCurveTo(x+w,y+h,x+w-r,y+h);
   c.lineTo(x+r,y+h);c.quadraticCurveTo(x,y+h,x,y+h-r);
   c.lineTo(x,y+r);c.quadraticCurveTo(x,y,x+r,y);}
  c.closePath();
 }
 function surface(name,w,h,pw,ph,z=0){
  const canvas=document.createElement('canvas');canvas.width=pw;canvas.height=ph;
  const context=canvas.getContext('2d');if(!context)throw Error('Model VR labels require a 2D canvas.');
  const texture=new T.CanvasTexture(canvas);texture.colorSpace=T.SRGBColorSpace;
  texture.minFilter=T.LinearMipmapLinearFilter;texture.magFilter=T.LinearFilter;
  texture.generateMipmaps=true;texture.anisotropy=2;textures.add(texture);
  const material=new T.MeshBasicMaterial({map:texture,transparent:true,depthTest:false,
   depthWrite:false,toneMapped:false,side:T.DoubleSide});materials.add(material);
  const mesh=new T.Mesh(geometry(w,h),material);mesh.name=name;
  mesh.position.z=z;mesh.renderOrder=8201;mesh.frustumCulled=false;
  mesh.userData.editorOnly=true;mesh.userData.se340UI=true;root.add(mesh);
  return {mesh,canvas,context,texture};
 }
 function repaint(item,draw,key){
  if(disposed||key!==undefined&&item.drawKey===key)return;item.drawKey=key;
  const {context:c,canvas}=item;c.clearRect(0,0,canvas.width,canvas.height);
  draw(c,canvas.width,canvas.height);item.texture.needsUpdate=true;paintCount++;
 }
 function fit(c,text,max,font=42,min=30){
  text=clean(text);let size=font;
  for(;size>min;size-=2){c.font='650 '+size+'px system-ui,sans-serif';if(c.measureText(text).width<=max)break;}
  c.font='650 '+size+'px system-ui,sans-serif';
  while(text.length>2&&c.measureText(text).width>max)text=text.slice(0,-2)+'…';
  return text;
 }
 const plate=surface('Model Studio · tools background',.56,.48,1024,878,0);
 plate.mesh.renderOrder=8200;plate.mesh.userData.se340Block=true;
 repaint(plate,(c,w,h)=>{
  rounded(c,3,3,w-6,h-6,32);c.fillStyle='rgba(19,15,31,.98)';c.fill();
  c.strokeStyle='#8563a8';c.lineWidth=5;c.stroke();
  c.fillStyle='#352344';c.fillRect(26,134,w-52,3);
  c.fillStyle='#b487e1';c.fillRect(34,29,8,68);
 });
 const heading=surface('Model Studio · VR heading',.52,.052,1040,104,.008);heading.mesh.position.y=.200;
 const selection=surface('Model Studio · selected part label',.52,.032,1040,64,.008);selection.mesh.position.y=.148;
 const message=surface('Model Studio · interaction status',.52,.035,1040,70,.008);message.mesh.position.y=-.183;
 const hint=surface('Model Studio · controller hint',.52,.027,1040,54,.008);hint.mesh.position.y=-.219;
 const guide=surface('Model Studio · controller guide',.52,.24,1040,480,.010);guide.mesh.position.y=.005;
 guide.mesh.visible=false;
 const pages={
  tools:[
   ['inspect','Inspect'],['move','Move'],['rotate','Rotate'],
   ['scale','Scale'],['undo','Undo'],['redo','Redo'],
   ['focus','Focus'],['recenter','Recenter'],['views','Views'],
   ...(hasAction('precision')?[['precision','Precision']]:[]),
   ...(hasAction('snap')?[['snap','Snap']]:[]),['exit','Exit VR']
  ],
  views:[
   ['view-front','Front'],['view-back','Back'],['view-left','Left'],
   ['view-right','Right'],['view-top','Top'],['view-bottom','Bottom'],
   ['view-iso','Isometric'],['focus','Focus'],['aim','Aim'],
   ['tools','Tools'],['help','Guide'],['exit','Exit VR']
  ],
  aim:[
   ['aim-hand','Hand L/R'],['aim-yaw-minus','Yaw -2°'],['aim-yaw-plus','Yaw +2°'],
   ['aim-pitch-minus','Pitch -2°'],['aim-pitch-plus','Pitch +2°'],['aim-reset','Reset hand'],
   ['aim-reset-all','Reset both'],['views','Views'],['tools','Tools'],
   ['help','Guide'],['exit','Exit VR']
  ]
 };
 const slots=[];let currentPage='';
 pages.tools.forEach((_,index)=>{
  const item=surface('Model Studio · view tool '+index,.165,.058,512,180,.014);
  const column=index%3,row=Math.floor(index/3);
  item.mesh.position.set((column-1)*.177,.086-row*.070,.014);
  item.home=item.mesh.position.clone();item.id='';item.label='';
  item.mesh.renderOrder=8202;slots.push(item);
 });
 function installPage(page){
  currentPage=page;buttons.clear();hovered=null;pressed=null;
  const entries=pages[page]||pages.tools;
  slots.forEach((item,index)=>{
   const pair=entries[index];
   item.id=pair?.[0]||'';item.label=pair?.[1]||'';
   item.mesh.userData.se340Action=item.id||null;
   item.mesh.visible=!!item.id;item.drawKey=null;
   if(item.id)buttons.set(item.id,item);
  });
 }

 function trackingLabel(){
  const value=state.tracking;
  if(typeof value==='number')return value>0?value+' TRACKED':'NO CONTROLLERS';
  if(value===true)return 'TRACKED';if(value===false)return 'NO CONTROLLERS';
  if(typeof value==='string')return clean(value,20);
  return 'VR WORKSPACE';
 }
 function enabled(id){return id==='undo'?!!state.canUndo:id==='redo'?!!state.canRedo:true;}
 function active(id){return ['inspect','move','rotate','scale'].includes(id)?state.mode===id:
  id==='precision'?!!state.precision:id==='snap'?!!state.snap:id==='help'?!!state.helpVisible:id.startsWith('view-')?state.viewMode===id.slice(5):false;}
 function drawButton(item){
  const disabled=!enabled(item.id),on=active(item.id),over=hovered===item.id,down=pressed===item.id;
  item.mesh.userData.se340Disabled=disabled;item.mesh.userData.se340Selected=on;
  repaint(item,(c,w,h)=>{
   rounded(c,5,5,w-10,h-10,24);
   c.fillStyle=disabled?'#191621':down?'#286e5c':on?'#70459f':over?'#473359':'#231b32';c.fill();
   c.strokeStyle=disabled?'#51465f':down?'#b2ffe1':over?'#c2f7e6':on?'#dcbcff':'#77608f';
   c.lineWidth=on||over||down?7:4;c.stroke();
   c.fillStyle=disabled?'#91869e':'#fff3ff';c.textAlign='center';c.textBaseline='middle';
   const text=item.id==='help'&&state.helpVisible?'Back to panel':item.id==='aim-hand'?'Hand: '+state.aimHand.toUpperCase():item.label;
   c.fillText(fit(c,text,w-52,46,34),w/2,h/2-1);
   if(on){rounded(c,w*.27,h-27,w*.46,9,4);c.fillStyle='#e6c4ff';c.fill();}
   if(item.id==='precision'||item.id==='snap'){
    c.beginPath();c.arc(w-31,28,8,0,Math.PI*2);c.fillStyle=on?'#c4ffe4':'#766584';c.fill();
   }
  },JSON.stringify([disabled,on,over,down,item.id==='help'&&!!state.helpVisible]));
 }
 function drawGuide(){
  repaint(guide,(c,w,h)=>{
   c.fillStyle='#21182f';rounded(c,0,0,w,h,18);c.fill();
   const rows=[
    ['TRIGGER','Select part / press button'],['GRIP','Use Move / Rotate / Scale'],
    ['A / B','Next tool / cancel edit'],['X / Y','Tools palette / Undo'],
    ['LEFT STICK','Pan · X/Y'],['RIGHT STICK','Orbit X/Y · press+Y zoom'],
    ['PRECISION','Fine transform ×0.25'],['SNAP','1 cm · 15° · scale 0.05']
   ];
   rows.forEach(([key,value],i)=>{
    const col=i%2,row=Math.floor(i/2),x=col*w/2+24,y=row*116+33;
    c.textAlign='left';c.textBaseline='middle';c.fillStyle='#d5b1fa';c.font='750 35px system-ui,sans-serif';c.fillText(key,x,y);
    c.fillStyle='#eee5f7';c.fillText(fit(c,value,w/2-44,30,26),x,y+44);
   });
  });
 }
 drawGuide();
 function rebuildTargets(){
  targets.splice(0,targets.length,plate.mesh);
  for(const item of buttons.values())if(item.mesh.visible)targets.push(item.mesh);
 }
 function update(next={}){
  if(disposed)return;
  const incoming=typeof next==='string'?{message:next}:next||{};
  state={...state,...incoming};if(incoming.help!==undefined&&incoming.helpVisible===undefined)state.helpVisible=!!incoming.help;
  const page=pages[state.page]?state.page:'tools';if(page!==currentPage)installPage(page);
  const key=JSON.stringify([state.mode,clean(state.selectedName),clean(state.hoverName),!!state.dragging,
   !!state.canUndo,!!state.canRedo,clean(state.message),trackingLabel(),!!state.precision,!!state.snap,!!state.helpVisible,clean(state.controllerHint),state.page,state.viewMode,state.aimHand,state.aimYaw,state.aimPitch]);
  if(key===signature)return;signature=key;
  const helping=!!state.helpVisible;
  const selectionText=helping?'Standard Touch controls':state.page==='aim'?'ALIGN POINTER · '+state.aimHand.toUpperCase()+' HAND':state.page==='views'?'VIEW PRESETS · '+String(state.viewMode).toUpperCase():state.selectedName?'Selected · '+clean(state.selectedName):'No part selected · Trigger selects';
  const statusText=helping?'View and aim menus do not change saved geometry.':state.page==='aim'?'Yaw '+state.aimYaw+'° · Pitch '+state.aimPitch+'° · saved on this browser':state.dragging?
   'Release Grip to commit · B cancels this edit':state.hoverName&&state.hoverName!==state.selectedName?
   'Hover · '+clean(state.hoverName):clean(state.message)||'Inspect first · choose a tool to edit.';
  const controllerText=state.page==='aim'?'Compare to Meta system ray; adjust left/right separately':state.page==='views'?'Preset angle · right stick resumes free orbit':clean(state.controllerHint)||'Trigger select · Grip edit · Left pan · Right orbit / press to zoom';
  repaint(heading,(c,w,h)=>{
   c.textAlign='left';c.textBaseline='middle';c.fillStyle='#fbf1ff';
   c.font='750 46px system-ui,sans-serif';c.fillText(helping?'CONTROLLER GUIDE':'MODEL STUDIO',12,53);
   c.textAlign='right';c.fillStyle=state.tracking===false||state.tracking===0?'#f5ce98':'#a6e9d3';
   c.fillText(fit(c,trackingLabel(),350,29,25),w-10,53);
  },JSON.stringify([helping,trackingLabel(),state.tracking===false||state.tracking===0]));
  repaint(selection,(c,w,h)=>{
   c.textAlign='left';c.textBaseline='middle';c.fillStyle=state.selectedName?'#ead7ff':'#baa9cb';
   c.fillText(fit(c,selectionText,w-24,36,29),12,h/2);
  },JSON.stringify([selectionText,!!state.selectedName]));
  for(const item of buttons.values()){
   item.mesh.visible=!!item.id&&(!helping||item.id==='help'||item.id==='exit');
   item.mesh.position.copy(item.home);
   if(helping){item.mesh.position.x=item.id==='help'?-.132:.132;item.mesh.position.y=-.160;}
   drawButton(item);
  }
  guide.mesh.visible=helping;hint.mesh.visible=!helping;
  message.mesh.position.y=helping?-.218:-.183;
  repaint(message,(c,w,h)=>{
   c.textAlign='left';c.textBaseline='middle';c.fillStyle=state.dragging?'#b7ffe1':'#dbcae8';
   c.fillText(fit(c,statusText,w-24,33,27),12,h/2);
  },JSON.stringify([statusText,!!state.dragging]));
  repaint(hint,(c,w,h)=>{
   c.textAlign='left';c.textBaseline='middle';c.fillStyle='#b7a7c9';
   c.fillText(fit(c,controllerText,w-24,29,25),12,h/2);
  },controllerText);
  if(hovered&&!buttons.get(hovered)?.mesh.visible)hovered=null;
  rebuildTargets();root.updateWorldMatrix(true,true);
 }
 function resolve(target){return typeof target==='string'?target:(target?.object||target)?.userData?.se340Action||null;}
 function hover(target){
  if(disposed)return;const id=resolve(target),next=buttons.has(id)?id:null;if(next===hovered)return;
  const previous=hovered;hovered=next;if(previous)drawButton(buttons.get(previous));if(hovered)drawButton(buttons.get(hovered));
 }
 function press(target){
  if(disposed)return false;const id=resolve(target),item=buttons.get(id);
  if(!item||!item.mesh.visible||!enabled(id))return false;
  const previous=pressed;pressed=id;if(previous&&previous!==id)drawButton(buttons.get(previous));drawButton(item);
  if(pressTimer!==null)clearTimeout(pressTimer);
  pressTimer=setTimeout(()=>{pressTimer=null;const old=pressed;pressed=null;if(!disposed&&old)drawButton(buttons.get(old));},180);
  return true;
 }
 function hitTest(raycaster){
  if(disposed||!raycaster?.intersectObjects)return null;
  for(let p=root;p;p=p.parent)if(p.visible===false)return null;
  return raycaster.intersectObjects(targets,false)[0]||null;
 }
 function dispose(){
  if(disposed)return;disposed=true;if(pressTimer!==null)clearTimeout(pressTimer);pressTimer=null;
  root.removeFromParent();root.clear();targets.length=0;
  for(const texture of textures)texture.dispose();for(const material of materials)material.dispose();
  for(const geo of geometries.values())geo.dispose();
 }
 update(typeof status==='string'?{message:status}:status);
 return Object.freeze({root,targets,update,hover,press,hitTest,dispose,
  inspect:()=>({width:.56,height:.48,helpVisible:!!state.helpVisible,hovered,pressed,
   buttonCount:buttons.size,targetCount:targets.length,textureCount:textures.size,paintCount,disposed})});
}
/* SE340_MODEL_VR_UI_END */
