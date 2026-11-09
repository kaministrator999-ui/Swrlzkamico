/* SE350_MODEL_VR_UI_START */
// Native, world-space controls for the Model Studio adapter. No renderer,
// document mutation or input dispatch lives here; the workspace owns those.
function se340CreateModelVRUI(options){
 'use strict';
 const {THREE:T,actions={},status={}}=options||{};
 if(!T?.Group)throw Error('Model VR UI requires Three.js.');
 const root=new T.Group();root.name='Model Studio · VR tools';
 root.userData.editorOnly=true;root.userData.se340ModelUI=true;
 const targets=[],textures=new Set(),materials=new Set(),geometries=new Map();
 const buttons=new Map();let disposed=false,hovered=null,pressed=null,pressTimer=null,paintCount=0,signature='',wheelKind=null;
 let state={mode:'inspect',selectedName:'',hoverName:'',dragging:false,canUndo:false,canRedo:false,
  message:'Choose a part, then choose an edit tool.',tracking:null,precision:false,snap:false,helpVisible:false,controllerHint:'',page:'tools',viewMode:'orbit',displayMode:'textured',aimHand:'right',aimYaw:0,aimPitch:0,selectedCount:0,sculptTool:'push',brushRadius:.08,brushStrength:.35,drawPointCount:0,twoHand:false,selectedRegionId:null};
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
 const guide=surface('Model Studio · controller guide',.52,.28,1040,560,.010);guide.mesh.position.y=-.008;
 guide.mesh.visible=false;
 const pages={
  tools:[
   ['inspect','Inspect'],['move','Move'],['rotate','Rotate'],
   ['scale','Scale'],['sculpt','Sculpt'],['draw','Draw mesh'],
   ['two-hand','Two hands'],['undo','Undo'],['redo','Redo'],
   ['focus','Focus'],['studio','Studio'],['exit','Exit VR']
  ],
  mesh:[
   ['inspect','Inspect'],['move','Move'],['rotate','Rotate'],
   ['scale','Scale'],['precision','Precision'],['snap','Snap'],
   ['selection-clear','Clear selection'],['undo','Undo'],['redo','Redo'],
   ['studio','Studio'],['help','Guide'],['exit','Exit VR']
  ],
  studio:[
   ['mesh','Mesh tools'],['sculpt','Sculpt'],['draw','Draw mesh'],
   ['views','Display & views'],['aim','Pointer aim'],['help','Guide'],
   ['focus','Focus'],['recenter','Recenter'],['tools','Quick tools'],
   ['precision','Precision'],['snap','Snap'],['exit','Exit VR']
  ],
  sculpt:[
   ['sculpt-push','Push'],['sculpt-smooth','Smooth'],['sculpt-flatten','Flatten'],
   ['sculpt-inflate','Inflate'],['sculpt-pinch','Pinch'],['sculpt-translate','Translate'],
   ['brush-radius-minus','Radius −'],['brush-radius-plus','Radius +'],['brush-strength-minus','Strength −'],
   ['brush-strength-plus','Strength +'],['studio','Studio'],['exit','Exit VR']
  ],
  draw:[
   ['draw','Draw outline'],['draw-finish','Make face'],['extrude','Extrude'],
   ['draw-clear','Clear outline'],['precision','Precision'],['lasso-clear','Whole surface'],
   ['undo','Undo'],['redo','Redo'],['lasso','Lasso select'],
   ['studio','Studio'],['help','Guide'],['exit','Exit VR']
  ],
  views:[
   ['display-textured','Textured'],['display-solid','Solid'],['display-wireframe','Wireframe'],
   ['display-xray','X-ray'],['display-normals','Normals'],['cameras','Angles'],
   ['focus','Focus'],['aim','Aim'],['studio','Studio'],
   ['help','Guide'],['tools','Quick tools'],['exit','Exit VR']
  ],
  cameras:[
   ['view-front','Front'],['view-back','Back'],['view-left','Left'],
   ['view-right','Right'],['view-top','Top'],['view-bottom','Bottom'],
   ['view-iso','Isometric'],['focus','Focus'],['views','Display'],
   ['studio','Studio'],['aim','Aim'],['exit','Exit VR']
  ],
  aim:[
   ['aim-hand','Hand L/R'],['aim-yaw-minus','Yaw −2°'],['aim-yaw-plus','Yaw +2°'],
   ['aim-pitch-minus','Pitch −2°'],['aim-pitch-plus','Pitch +2°'],['aim-reset','Reset hand'],
   ['aim-reset-all','Reset both'],['views','Display'],['studio','Studio'],
   ['help','Guide'],['tools','Quick tools'],['exit','Exit VR']
  ]
 };
 const wheels={
  tools:[['inspect','Inspect'],['move','Move'],['rotate','Rotate'],['scale','Scale'],
   ['sculpt','Sculpt'],['draw','Draw mesh'],['two-hand','Two hands']],
  studio:[['mesh','Mesh tools'],['sculpt','Sculpt'],['draw','Draw mesh'],
   ['views','Display'],['aim','Pointer aim'],['help','Guide']],
  brush:[['sculpt-push','Push'],['sculpt-smooth','Smooth'],['sculpt-flatten','Flatten'],
   ['sculpt-inflate','Inflate'],['sculpt-pinch','Pinch'],['sculpt-translate','Translate']]
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
  const entries=wheelKind?wheels[wheelKind]:page==='guide'?[['help','Back to panel'],['exit','Exit VR']]:pages[page]||pages.tools;
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
 function enabled(id){return id==='undo'?!!state.canUndo:id==='redo'?!!state.canRedo:id==='selection-clear'?state.selectedCount>0||!!state.selectedName:id==='draw-finish'?(state.drawPointCount||0)>=3:id==='draw-clear'?(state.drawPointCount||0)>0:true;}
 function active(id){return ['inspect','move','rotate','scale','sculpt','draw','lasso','extrude','two-hand'].includes(id)?state.mode===id||id==='two-hand'&&!!state.twoHand:id.startsWith('sculpt-')?state.sculptTool===id.slice(7):
  id==='precision'?!!state.precision:id==='snap'?!!state.snap:id==='help'?!!state.helpVisible:id.startsWith('view-')?state.viewMode===id.slice(5):id.startsWith('display-')?state.displayMode===id.slice(8):false;}
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
  },JSON.stringify([disabled,on,over,down,item.id==='help'&&!!state.helpVisible,item.id==='aim-hand'&&state.aimHand]));
 }
 function drawGuide(){
  repaint(guide,(c,w,h)=>{
   c.fillStyle='#21182f';rounded(c,0,0,w,h,18);c.fill();
   const rows=[
    ['RIGHT TRIGGER','Select · hold to sculpt / draw'],['LEFT TRIGGER','Add / remove selection'],
    ['RIGHT GRIP','Edit · pull an extruded face'],['LEFT GRIP','Reposition workbench'],
    ['A / B','A: next / hold wheel · B: cancel'],['X / Y','X: panel / hold studio · Y: Undo'],
    ['RIGHT STICK','Camera orbit ↑↓/←→ · click focus'],['LEFT STICK','Pan · click for Precision'],
    ['ZOOM','Left grip + right stick ↑↓'],['TWO HANDS','Choose Two hands · hold grips']
   ];
   rows.forEach(([key,value],i)=>{
    const col=i%2,row=Math.floor(i/2),x=col*w/2+24,y=row*108+27;
    c.textAlign='left';c.textBaseline='middle';c.fillStyle=col?'#f0c9a5':'#b4f5e1';c.font='750 31px system-ui,sans-serif';c.fillText(key,x,y);
    c.fillStyle='#eee5f7';c.fillText(fit(c,value,w/2-44,28,24),x,y+42);
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
  const page=pages[state.page]?state.page:'tools',pageKey=wheelKind?'wheel-'+wheelKind:state.helpVisible?'guide':page;if(pageKey!==currentPage)installPage(pageKey);
  const key=JSON.stringify([state.mode,clean(state.selectedName),clean(state.hoverName),!!state.dragging,
   !!state.canUndo,!!state.canRedo,clean(state.message),trackingLabel(),!!state.precision,!!state.snap,!!state.helpVisible,clean(state.controllerHint),state.page,state.viewMode,state.displayMode,state.aimHand,state.aimYaw,state.aimPitch,state.selectedCount,state.sculptTool,state.brushRadius,state.brushStrength,state.drawPointCount,state.twoHand,state.selectedRegionId,wheelKind]);
  if(key===signature)return;signature=key;
  const helping=!!state.helpVisible&&!wheelKind;
  const count=Math.max(Number(state.selectedCount)||0,state.selectedName?1:0);
  const radius=Number(state.brushRadius),strength=Number(state.brushStrength);
  const brushText=String(state.sculptTool||'push').toUpperCase()+' · radius '+(Number.isFinite(radius)?radius.toFixed(2):'—')+' · strength '+(Number.isFinite(strength)?Math.round(strength*100)+'%':'—');
  const selectionText=wheelKind?'POINT AT A TOOL · RELEASE '+(wheelKind==='studio'?'X':'A')+' TO CHOOSE':helping?'Quest / Touch · left assists, right edits':state.page==='aim'?'ALIGN POINTER · '+state.aimHand.toUpperCase()+' HAND':state.page==='views'?'MODEL DISPLAY · '+String(state.displayMode).toUpperCase():state.page==='cameras'?'MODEL ANGLES · '+String(state.viewMode).toUpperCase():state.page==='sculpt'?brushText+(state.selectedRegionId?' · Lasso mask':' · Whole surface'):state.page==='draw'?(state.mode==='lasso'?'LASSO · ':'OUTLINE · ')+(Number(state.drawPointCount)||0)+' points · '+count+' selected':count>1?count+' PARTS SELECTED · '+clean(state.selectedName,46):state.selectedName?'Selected · '+clean(state.selectedName):'Right trigger selects · left trigger adds';
  const statusText=wheelKind?'Release off a button to keep the current tool.':helping?'X + Y: Redo · B cancels before an edit can commit.':state.page==='aim'?'Yaw '+state.aimYaw+'° · Pitch '+state.aimPitch+'° · saved on this browser':state.dragging?(state.mode==='sculpt'?'Release Trigger to commit stroke'+(state.selectedRegionId?' · Lasso mask':'')+' · B cancels':state.mode==='lasso'?'Trace surface region · release Trigger saves mask · B cancels':state.mode==='draw'?'Draw a closed outline · release Trigger · B cancels':state.mode==='two-hand'?'Release a grip to commit group edit · B cancels':'Release Grip to commit · B cancels this edit'):state.hoverName&&state.hoverName!==state.selectedName?'Hover · '+clean(state.hoverName):clean(state.message)||'Choose a tool to edit the selected geometry.';
  const controllerText=wheelKind?'B cancels · menus block geometry behind them':state.page==='aim'?'Compare with Meta system ray; adjust each hand separately':state.page==='views'?'Display modes change the preview only':state.page==='cameras'?'Preset orientation · right stick resumes free orbit':state.page==='sculpt'?'Hold right Trigger on surface · left stick: radius / strength':state.page==='draw'?'Right Trigger: outline · Make face · Grip: extrude':clean(state.controllerHint)||'A hold: tool wheel · X hold: studio · Y: Undo · X+Y: Redo';
  repaint(heading,(c,w,h)=>{
   c.textAlign='left';c.textBaseline='middle';c.fillStyle='#fbf1ff';
   c.font='750 46px system-ui,sans-serif';c.fillText(helping?'CONTROLLER GUIDE':wheelKind?(wheelKind==='studio'?'STUDIO WHEEL':wheelKind==='brush'?'SCULPT BRUSH WHEEL':'QUICK TOOL WHEEL'):'MODEL STUDIO',12,53);
   c.textAlign='right';c.fillStyle=state.tracking===false||state.tracking===0?'#f5ce98':'#a6e9d3';
   c.fillText(fit(c,trackingLabel(),350,29,25),w-10,53);
  },JSON.stringify([helping,wheelKind,trackingLabel(),state.tracking===false||state.tracking===0]));
  repaint(selection,(c,w,h)=>{
   c.textAlign='left';c.textBaseline='middle';c.fillStyle=state.selectedName?'#ead7ff':'#baa9cb';
   c.fillText(fit(c,selectionText,w-24,36,29),12,h/2);
  },JSON.stringify([selectionText,!!state.selectedName]));
  let wheelIndex=0;
  for(const item of buttons.values()){
   item.mesh.visible=!!item.id&&(!helping||item.id==='help'||item.id==='exit');
   item.mesh.position.copy(item.home);
   if(helping){item.mesh.position.x=item.id==='help'?-.132:.132;item.mesh.position.y=-.170;}
   if(wheelKind){const angle=Math.PI/2-wheelIndex++*Math.PI*2/buttons.size;item.mesh.position.set(Math.cos(angle)*.177,Math.sin(angle)*.116-.015,.014);item.mesh.scale.set(.76,.84,1);}else item.mesh.scale.set(1,1,1);
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
  pressTimer=setTimeout(()=>{pressTimer=null;const old=pressed;pressed=null;if(!disposed&&old&&buttons.has(old))drawButton(buttons.get(old));},180);
  return true;
 }
 // Wheels share the palette's blocking plate and ray targets. The workspace
 // owns A/X hold input and executes the returned action only after release.
 function openWheel(kind='tools'){
  if(disposed||!wheels[kind])return false;
  wheelKind=kind;currentPage='';signature='';update({helpVisible:false});return true;
 }
 function closeWheel(){
  if(disposed||!wheelKind)return false;
  wheelKind=null;currentPage='';signature='';update();return true;
 }
 function releaseWheel(target=hovered){
  if(disposed||!wheelKind)return null;
  const id=resolve(target),item=buttons.get(id),chosen=item&&item.mesh.visible&&enabled(id)?id:null;
  closeWheel();return chosen;
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
 return Object.freeze({root,targets,update,hover,press,hitTest,dispose,openWheel,closeWheel,releaseWheel,
  inspect:()=>({width:.56,height:.48,page:currentPage,wheel:wheelKind,wheelVisible:!!wheelKind,helpVisible:!!state.helpVisible&&!wheelKind,hovered,pressed,selectedCount:state.selectedCount,brushRadius:state.brushRadius,brushStrength:state.brushStrength,sculptTool:state.sculptTool,drawPointCount:state.drawPointCount,twoHand:!!state.twoHand,selectedRegionId:state.selectedRegionId,
   buttonCount:buttons.size,targetCount:targets.length,textureCount:textures.size,paintCount,disposed})});
}
/* SE350_MODEL_VR_UI_END */
