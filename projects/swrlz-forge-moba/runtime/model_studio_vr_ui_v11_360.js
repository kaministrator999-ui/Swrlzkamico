/* SE360_MODEL_VR_UI_START */
// World-space Model Studio console. Rendering and input remain in the engine's
// existing XR loop; tick only animates owned presentation meshes/materials.
function se340CreateModelVRUI(options){
 'use strict';
 const {THREE:T,actions={},status={}}=options||{};
 if(!T?.Group)throw Error('Model VR UI requires Three.js.');
 const WIDTH=.64,HEIGHT=.62;
 const root=new T.Group();root.name='Model Studio · spatial console';
 root.userData.editorOnly=true;root.userData.se340ModelUI=true;
 const targets=[],textures=new Set(),materials=new Set(),geometries=new Map(),slots=[],navSlots=[];
 const buttons=new Map();let disposed=false,hoveredItem=null,pressedItem=null,pressedRemaining=0,paintCount=0,signature='',wheelKind=null,currentPage='';
 let visibleState=true,reducedMotion=false,reveal=0,transition=1,elapsed=0,activeMotion=true,lastTickDelta=0;
 let state={mode:'inspect',selectedName:'',hoverName:'',dragging:false,canUndo:false,canRedo:false,
  message:'Choose a part, then choose a tool.',tracking:null,precision:false,snap:false,helpVisible:false,controllerHint:'',page:'tools',viewMode:'orbit',displayMode:'textured',aimHand:'right',aimYaw:0,aimPitch:0,selectedCount:0,sculptTool:'push',brushRadius:.08,brushStrength:.35,drawPointCount:0,twoHand:false,selectedRegionId:null};
 const clean=(value,max=100)=>String(value??'').replace(/[\r\n\t]/g,' ').slice(0,max);
 function geometry(w,h){const key=w+':'+h;if(!geometries.has(key))geometries.set(key,new T.PlaneGeometry(w,h));return geometries.get(key);}
 function rounded(c,x,y,w,h,r){c.beginPath();if(c.roundRect)c.roundRect(x,y,w,h,r);else{c.moveTo(x+r,y);c.lineTo(x+w-r,y);c.quadraticCurveTo(x+w,y,x+w,y+r);c.lineTo(x+w,y+h-r);c.quadraticCurveTo(x+w,y+h,x+w-r,y+h);c.lineTo(x+r,y+h);c.quadraticCurveTo(x,y+h,x,y+h-r);c.lineTo(x,y+r);c.quadraticCurveTo(x,y,x+r,y);}c.closePath();}
 function gradient(c,x,y,x2,y2,stops){if(!c.createLinearGradient)return stops[0][1];const g=c.createLinearGradient(x,y,x2,y2);for(const [at,color]of stops)g.addColorStop(at,color);return g;}
 function surface(name,w,h,pw,ph,z=0){
  const canvas=document.createElement('canvas');canvas.width=pw;canvas.height=ph;const context=canvas.getContext('2d');if(!context)throw Error('Model VR labels require a 2D canvas.');
  const texture=new T.CanvasTexture(canvas);texture.colorSpace=T.SRGBColorSpace;texture.minFilter=T.LinearMipmapLinearFilter;texture.magFilter=T.LinearFilter;texture.generateMipmaps=true;texture.anisotropy=2;textures.add(texture);
  const material=new T.MeshBasicMaterial({map:texture,transparent:true,depthTest:false,depthWrite:false,toneMapped:false,side:T.DoubleSide});materials.add(material);
  const mesh=new T.Mesh(geometry(w,h),material);mesh.name=name;mesh.position.z=z;mesh.renderOrder=8301;mesh.frustumCulled=false;mesh.userData.editorOnly=true;mesh.userData.se340UI=true;root.add(mesh);
  return {mesh,canvas,context,texture,baseZ:z,baseOpacity:1};
 }
 function repaint(item,draw,key){if(disposed||key!==undefined&&item.drawKey===key)return;item.drawKey=key;const {context:c,canvas}=item;c.clearRect(0,0,canvas.width,canvas.height);draw(c,canvas.width,canvas.height);item.texture.needsUpdate=true;paintCount++;}
 function fit(c,text,max,font=42,min=30,weight=650){text=clean(text);let size=font;for(;size>min;size-=2){c.font=weight+' '+size+'px system-ui,sans-serif';if(c.measureText(text).width<=max)break;}c.font=weight+' '+size+'px system-ui,sans-serif';while(text.length>2&&c.measureText(text).width>max)text=text.slice(0,-2)+'…';return text;}
 function iconType(id){
  if(id.startsWith('sculpt-'))return id.slice(7);if(id.startsWith('brush-radius'))return 'radius';if(id.startsWith('brush-strength'))return 'strength';
  if(id.startsWith('view-'))return 'cube';if(id.startsWith('display-'))return id.includes('wire')?'wire':id.includes('normal')?'normals':'display';
  if(id.startsWith('aim-'))return 'aim';if(id==='draw-clear'||id==='selection-clear')return 'clear';if(id==='draw-finish')return 'face';if(id==='lasso-clear')return 'whole';
  return {tools:'grid',mesh:'cube',studio:'grid',views:'display',cameras:'cube',help:'help',focus:'focus',recenter:'focus',sculpt:'brush',draw:'pen',lasso:'lasso','two-hand':'hands',inspect:'eye',exit:'exit',precision:'precision',snap:'snap'}[id]||id;
 }
 function icon(c,type,x,y,size,color){
  c.save();c.translate(x,y);c.scale(size/48,size/48);c.strokeStyle=color;c.fillStyle=color;c.lineWidth=2.5;c.lineCap='round';c.lineJoin='round';
  const path=(points,close=false)=>{c.beginPath();points.forEach((p,i)=>i?c.lineTo(...p):c.moveTo(...p));if(close)c.closePath();c.stroke();};
  const circle=(x,y,r)=>{c.beginPath();c.arc(x,y,r,0,Math.PI*2);c.stroke();};
  if(type==='eye'){c.beginPath();c.moveTo(-20,0);c.quadraticCurveTo(0,-24,20,0);c.quadraticCurveTo(0,24,-20,0);c.stroke();circle(0,0,6);}
  else if(type==='move'){path([[-19,0],[19,0]]);path([[0,-19],[0,19]]);for(const [x,y,dx,dy]of [[19,0,-5,5],[-19,0,5,5],[0,-19,5,5],[0,19,5,-5]]){path([[x+(y?dx:dx),y+(x?dy:dy)],[x,y],[x+(y?-dx:dx),y+(x?-dy:dy)]]);}}
  else if(type==='rotate'||type==='undo'||type==='redo'){c.save();if(type==='redo')c.scale(-1,1);c.beginPath();c.arc(0,1,16,-Math.PI*.8,Math.PI*.65);c.stroke();path([[-15,-18],[-17,-7],[-6,-9]]);c.restore();}
  else if(type==='scale'){path([[-18,18],[18,-18]]);path([[6,-18],[18,-18],[18,-6]]);path([[-18,6],[-18,18],[-6,18]]);}
  else if(['cube','wire','face','extrude','whole'].includes(type)){path([[0,-20],[18,-10],[18,11],[0,21],[-18,11],[-18,-10],[0,-20]],true);path([[-18,-10],[0,0],[18,-10]]);path([[0,0],[0,21]]);if(type==='extrude')path([[0,-29],[0,-14],[-5,-19],[0,-14],[5,-19]]);}
  else if(type==='brush'||type==='pen'||type==='push'||type==='translate'){path([[-13,9],[9,-17],[18,-8],[-5,17],[-17,21],[-13,9]],true);path([[-10,5],[0,14]]);if(type==='brush')path([[-18,20],[-22,14],[-20,7]]);}
  else if(type==='smooth'||type==='flatten'){path([[-20,13],[-11,6],[-2,9],[8,-1],[19,-6]]);path([[-18,-12],[18,-12]]);if(type==='smooth'){c.beginPath();c.moveTo(-20,18);c.bezierCurveTo(-9,0,4,19,20,0);c.stroke();}}
  else if(type==='inflate'||type==='pinch'){circle(0,0,10);const sign=type==='inflate'?1:-1;for(const [x,y]of [[-1,0],[1,0],[0,-1],[0,1]]){const a=sign>0?13:21,b=sign>0?22:12;path([[x*a,y*a],[x*b,y*b]]);const px=-y*4,py=x*4;path([[x*(b-5*sign)+px,y*(b-5*sign)+py],[x*b,y*b],[x*(b-5*sign)-px,y*(b-5*sign)-py]]);}}
  else if(type==='grid'){for(const x of [-10,10])for(const y of [-10,10]){rounded(c,x-6,y-6,12,12,3);c.stroke();}}
  else if(type==='display'||type==='normals'){rounded(c,-21,-15,42,29,5);c.stroke();path([[-7,21],[7,21]]);path([[0,14],[0,21]]);if(type==='normals'){path([[-12,5],[0,-8],[12,5]],true);}else path([[-12,4],[-3,-5],[4,2],[10,-7]]);}
  else if(type==='focus'||type==='precision'||type==='aim'){circle(0,0,type==='precision'?6:10);path([[-22,0],[-14,0]]);path([[14,0],[22,0]]);path([[0,-22],[0,-14]]);path([[0,14],[0,22]]);}
  else if(type==='hands'){rounded(c,-23,-12,17,32,6);c.stroke();rounded(c,6,-12,17,32,6);c.stroke();path([[-11,-17],[0,-23],[11,-17]]);}
  else if(type==='lasso'){c.setLineDash?.([4,4]);c.beginPath();c.ellipse?.(0,-2,19,14,-.25,0,Math.PI*2);c.stroke();c.setLineDash?.([]);path([[14,9],[8,20],[-3,20]]);}
  else if(type==='exit'){path([[-3,-20],[-18,-20],[-18,20],[-3,20]]);path([[-4,0],[21,0],[12,-8],[21,0],[12,8]]);}
  else if(type==='clear'){path([[-13,-13],[13,13]]);path([[13,-13],[-13,13]]);circle(0,0,20);}
  else if(type==='radius'){circle(0,0,18);circle(0,0,5);path([[3,-3],[14,-14]]);}
  else if(type==='strength'){path([[-16,18],[-16,9],[-8,9],[-8,18],[-16,18]],true);path([[-4,18],[-4,-2],[4,-2],[4,18],[-4,18]],true);path([[8,18],[8,-16],[16,-16],[16,18],[8,18]],true);}
  else if(type==='snap'){path([[-18,-18],[-18,18],[18,18]]);path([[-8,-10],[-8,8],[10,8]]);circle(12,-12,4);}
  else{circle(0,0,20);c.font='700 29px system-ui,sans-serif';c.textAlign='center';c.textBaseline='middle';c.fillText('?',0,1);}
  c.restore();
 }
 const plate=surface('Model Studio · console background',WIDTH,HEIGHT,1280,1240,0);plate.mesh.renderOrder=8300;plate.mesh.userData.se340Block=true;
 repaint(plate,(c,w,h)=>{rounded(c,3,3,w-6,h-6,48);c.fillStyle=gradient(c,0,0,w,h,[[0,'#252139'],[.5,'#171b2b'],[1,'#131827']]);c.fill();c.strokeStyle='#776787';c.lineWidth=3;c.stroke();rounded(c,11,11,w-22,h-22,42);c.strokeStyle='rgba(212,226,255,.08)';c.lineWidth=2;c.stroke();
  c.fillStyle=gradient(c,36,0,w-36,0,[[0,'#a5eed6'],[.45,'#afa1ef'],[1,'rgba(155,128,225,0)']]);c.fillRect(46,17,w-92,3);
  c.fillStyle='rgba(5,9,18,.54)';rounded(c,28,1045,w-56,166,25);c.fill();c.strokeStyle='rgba(158,175,210,.10)';c.lineWidth=2;c.stroke();});
 const header=surface('Model Studio · console header',.59,.060,1180,120,.008);header.mesh.position.y=.264;
 const selection=surface('Model Studio · context',.59,.032,1180,64,.008);selection.mesh.position.y=.150;
 const message=surface('Model Studio · action feedback',.58,.046,1160,92,.010);message.mesh.position.y=-.221;
 const hint=surface('Model Studio · controls hint',.58,.026,1160,52,.010);hint.mesh.position.y=-.278;
 const guide=surface('Model Studio · controller guide',.59,.282,1180,564,.012);guide.mesh.position.y=-.010;guide.mesh.visible=false;
 const wheelCenter=surface('Model Studio · wheel context',.102,.102,300,300,.012);wheelCenter.mesh.position.y=-.015;wheelCenter.mesh.visible=false;
 const lineMaterial=new T.MeshBasicMaterial({color:0x89e6cd,transparent:true,opacity:.6,depthTest:false,depthWrite:false,toneMapped:false});materials.add(lineMaterial);
 const statusLine=new T.Mesh(geometry(.57,.0017),lineMaterial);statusLine.position.set(0,-.187,.012);statusLine.renderOrder=8302;root.add(statusLine);
 const glowCanvas=document.createElement('canvas');glowCanvas.width=512;glowCanvas.height=220;const gc=glowCanvas.getContext('2d');
 if(!gc)throw Error('Model VR labels require a 2D canvas.');
 for(let i=14;i>=0;i--){rounded(gc,20-i,20-i,472+i*2,180+i*2,25+i);gc.strokeStyle='rgba(255,255,255,'+(i===0?.35:.025)+')';gc.lineWidth=3;gc.stroke();}
 const glowTexture=new T.CanvasTexture(glowCanvas);glowTexture.colorSpace=T.SRGBColorSpace;glowTexture.minFilter=T.LinearFilter;glowTexture.magFilter=T.LinearFilter;glowTexture.generateMipmaps=false;textures.add(glowTexture);
 function addGlow(item){const material=new T.MeshBasicMaterial({map:glowTexture,color:0x9df5db,transparent:true,opacity:0,depthTest:false,depthWrite:false,toneMapped:false});materials.add(material);const mesh=new T.Mesh(geometry(item.role==='nav'?.123:.212,item.role==='nav'?.053:.080),material);mesh.renderOrder=8303;mesh.frustumCulled=false;mesh.userData.editorOnly=true;root.add(mesh);item.glow=mesh;item.lift=0;item.halo=0;}
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
 const details={inspect:'View without editing',move:'Position selection',rotate:'Turn selection',scale:'Resize selection',sculpt:'Shape the surface',draw:'Trace a new mesh','two-hand':'Use both grips',undo:'Previous edit',redo:'Restore an edit',focus:'Frame selection',studio:'Browse all tools',exit:'Return to studio',mesh:'Selection & transforms',views:'Material & wireframe',aim:'Align your pointer',help:'Controller controls',precision:'Fine controller motion',snap:'Step-based transforms',recenter:'Reset the workbench',tools:'Your editing toolkit','selection-clear':'Deselect all parts',extrude:'Pull a face into depth',lasso:'Mask a surface region','lasso-clear':'Turn off the mask','draw-clear':'Discard this outline','draw-finish':'Create a mesh face',cameras:'Front, side & top',
  'sculpt-push':'Raise or lower','sculpt-smooth':'Soften the surface','sculpt-flatten':'Level local detail','sculpt-inflate':'Build volume','sculpt-pinch':'Gather surface detail','sculpt-translate':'Pull the surface',
  'brush-radius-minus':'Smaller footprint','brush-radius-plus':'Larger footprint','brush-strength-minus':'Softer strokes','brush-strength-plus':'Stronger strokes'};
 const pageTitles={tools:['Quick tools','SELECT · SHAPE · CREATE'],mesh:['Mesh tools','SELECTION & TRANSFORMS'],studio:['Studio tools','YOUR MODELING WORKSPACE'],sculpt:['Sculpt surface','BRUSHES & SURFACE CONTROL'],draw:['Draw & build','OUTLINES · REGIONS · DEPTH'],views:['Model display','PREVIEW MATERIAL & STRUCTURE'],cameras:['Model angles','LOOK FROM EVERY SIDE'],aim:['Pointer alignment','CALIBRATE EACH CONTROLLER'],guide:['Controller guide','LEFT ASSISTS · RIGHT EDITS']};
 for(let i=0;i<12;i++){const item=surface('Model Studio · tool card '+i,.19,.066,570,198,.016);item.role='tool';item.home=new T.Vector3((i%3-1)*.202,.086-Math.floor(i/3)*.075,.016);item.mesh.position.copy(item.home);item.id='';item.label='';item.mesh.userData.se360Role='tool';item.mesh.renderOrder=8304;addGlow(item);slots.push(item);}
 [['tools','Tools'],['sculpt','Sculpt'],['draw','Draw'],['views','Display'],['help','Guide']].forEach(([id,label],i)=>{const item=surface('Model Studio · navigation '+label,.11,.041,330,123,.016);item.id=id;item.label=label;item.role='nav';item.home=new T.Vector3((i-2)*.121,.198,.016);item.mesh.position.copy(item.home);item.mesh.userData.se340Action=id;item.mesh.userData.se360Role='nav';item.mesh.renderOrder=8304;addGlow(item);navSlots.push(item);});
 const allItems=[...slots,...navSlots],surfaces=[plate,header,selection,message,hint,guide,wheelCenter];
 function trackingLabel(){const value=state.tracking;if(typeof value==='number')return value>0?value+' CONNECTED':'NO CONTROLLERS';if(value===true)return 'CONNECTED';if(value===false)return 'NO CONTROLLERS';if(typeof value==='string')return clean(value,23);return 'VR WORKSPACE';}
 function enabled(id){return id==='undo'?!!state.canUndo:id==='redo'?!!state.canRedo:id==='selection-clear'?state.selectedCount>0||!!state.selectedName:id==='draw-finish'?(state.drawPointCount||0)>=3:id==='draw-clear'?(state.drawPointCount||0)>0:true;}
 function active(item){const id=item.id;if(item.role==='nav'){const p=state.helpVisible?'guide':state.page;return id==='help'?p==='guide':id==='tools'?['tools','mesh','studio'].includes(p):id==='views'?['views','cameras','aim'].includes(p):p===id;}
  return ['inspect','move','rotate','scale','sculpt','draw','lasso','extrude','two-hand'].includes(id)?state.mode===id||id==='two-hand'&&!!state.twoHand:id.startsWith('sculpt-')?state.sculptTool===id.slice(7):id==='precision'?!!state.precision:id==='snap'?!!state.snap:id==='help'?!!state.helpVisible:id.startsWith('view-')?state.viewMode===id.slice(5):id.startsWith('display-')?state.displayMode===id.slice(8):false;}
 function label(item){return item.id==='help'&&state.helpVisible?'Back to tools':item.id==='aim-hand'?'Hand: '+state.aimHand.toUpperCase():item.label;}
 function description(item){if(item.id==='undo'&&!state.canUndo)return 'No earlier edits';if(item.id==='redo'&&!state.canRedo)return 'No later edits';if(item.id.startsWith('view-'))return 'Model orientation';if(item.id.startsWith('display-'))return 'Preview only';if(item.id.startsWith('aim-'))return 'Pointer calibration';return details[item.id]||'Modeling control';}
 function drawButton(item){
  if(!item.id)return;const disabled=!enabled(item.id),on=active(item),over=hoveredItem===item,down=pressedItem===item;
  item.mesh.userData.se340Disabled=disabled;item.mesh.userData.se340Selected=on;
  const text=label(item),sub=description(item),nav=item.role==='nav',key=JSON.stringify([item.id,text,sub,disabled,on,over,down,!!wheelKind]);
  repaint(item,(c,w,h)=>{const edge=disabled?'#485168':down?'#b5fff0':over?'#a7f6df':on?'#eed5a0':'#59617b';
   rounded(c,4,4,w-8,h-8,nav?25:22);c.fillStyle=gradient(c,0,0,w,h,[[0,disabled?'#1c2232':down?'#245f58':on?'#3c3544':over?'#294343':'#292d42'],[1,disabled?'#181e2b':down?'#1c403e':on?'#29283c':over?'#202f39':'#1e2537']]);c.fill();c.strokeStyle=edge;c.lineWidth=down||over||on?3.5:2;c.stroke();
   c.strokeStyle='rgba(226,238,255,.055)';c.lineWidth=1;rounded(c,10,10,w-20,h-20,nav?20:17);c.stroke();
   const ink=disabled?'#8792aa':on?'#ffe6b4':over||down?'#c4ffef':'#e6edf9';
   if(nav){icon(c,iconType(item.id),41,h/2,31,ink);c.textAlign='left';c.textBaseline='middle';c.fillStyle=ink;c.fillText(fit(c,text,w-96,36,29,700),74,h/2);if(on){c.fillStyle='#eccb94';rounded(c,w*.31,h-14,w*.38,4,2);c.fill();}}
   else{icon(c,iconType(item.id),56,h*.39,43,ink);c.textAlign='left';c.textBaseline='middle';c.fillStyle=ink;c.fillText(fit(c,text,w-134,44,32,750),96,h*.38);
    c.fillStyle=disabled?'#748198':on?'#d9c8af':over?'#c6ded8':'#a9b6cc';c.fillText(fit(c,sub,w-52,27,22,500),26,h*.77);
    if(on){c.beginPath();c.arc(w-27,26,8,0,Math.PI*2);c.fillStyle='#f5d69e';c.fill();c.strokeStyle='#383044';c.lineWidth=2;pathCheck(c,w-31,26);}
   }
  },key);
 }
 function pathCheck(c,x,y){c.beginPath();c.moveTo(x,y);c.lineTo(x+3,y+3);c.lineTo(x+9,y-4);c.stroke();}
 function drawGuide(){repaint(guide,(c,w,h)=>{rounded(c,0,0,w,h,24);c.fillStyle='#192234';c.fill();const rows=[['RIGHT TRIGGER','Select · hold to sculpt / draw'],['LEFT TRIGGER','Add / remove a selection'],['RIGHT GRIP','Transform · pull to extrude'],['LEFT GRIP','Reposition the workbench'],['A / B','A: next / hold tools · B: cancel'],['X / Y','X: menu / hold studio · Y: Undo'],['RIGHT STICK','Orbit · click to focus'],['LEFT STICK','Pan · click Precision'],['ZOOM','Left grip + right stick up/down'],['TWO HANDS','Choose Two hands · hold grips']];rows.forEach(([key,value],i)=>{const col=i%2,row=Math.floor(i/2),x=col*w/2+26,y=row*110+29;c.fillStyle=col?'#f0ce9c':'#a0ecd5';c.textAlign='left';c.textBaseline='middle';c.font='750 29px system-ui,sans-serif';c.fillText(key,x,y);c.fillStyle='#e7edf8';c.fillText(fit(c,value,w/2-48,29,24,550),x,y+42);if(row<4){c.fillStyle='rgba(176,190,215,.10)';c.fillRect(x,y+74,w/2-48,1);}});});}
 drawGuide();
 function installPage(page){
  currentPage=page;buttons.clear();hoveredItem=null;pressedItem=null;pressedRemaining=0;transition=0;
  const helping=page==='guide',entries=wheelKind?wheels[wheelKind]:helping?[['help','Back to tools'],['exit','Exit VR']]:pages[page]||pages.tools;
  slots.forEach((item,index)=>{const pair=entries[index];item.id=pair?.[0]||'';item.label=pair?.[1]||'';item.mesh.userData.se340Action=item.id||null;item.mesh.visible=!!item.id;item.drawKey=null;item.lift=0;item.halo=0;item.home.set((index%3-1)*.202,.086-Math.floor(index/3)*.075,.016);
   if(helping)item.home.set(index===0?-.102:.102,-.193,.016);
   if(wheelKind){const angle=Math.PI/2-index*Math.PI*2/entries.length;item.home.set(Math.cos(angle)*.194,Math.sin(angle)*.147-.012,.016);item.mesh.scale.set(.80,1.02,1);}else item.mesh.scale.set(1,1,1);
   item.mesh.position.copy(item.home);if(item.id)buttons.set(item.id,item);});
  for(const item of navSlots){item.mesh.visible=!wheelKind;item.drawKey=null;item.lift=0;item.halo=0;item.mesh.position.copy(item.home);}
  guide.mesh.visible=helping;wheelCenter.mesh.visible=!!wheelKind;
  rebuildTargets();
 }
 function rebuildTargets(){targets.splice(0,targets.length,plate.mesh);for(const item of allItems)if(item.id&&item.mesh.visible)targets.push(item.mesh);}
 function statusText(){
  if(wheelKind)return hoveredItem?'Release '+(wheelKind==='studio'?'X':'A')+' for '+label(hoveredItem)+' · '+description(hoveredItem):'Point at a card, then release '+(wheelKind==='studio'?'X':'A')+' to choose.';
  if(state.helpVisible)return 'X + Y: Redo · B cancels an unfinished edit.';
  if(state.dragging)return state.mode==='sculpt'?'Sculpt preview · release Trigger to apply · B cancels':state.mode==='lasso'?'Trace a surface region · release Trigger to save':state.mode==='draw'?'Trace an outline · release Trigger to make a face':state.mode==='two-hand'?'Two-hand preview · release a grip to apply':'Transform preview · release Grip to apply · B cancels';
  if(hoveredItem)return label(hoveredItem)+' · '+description(hoveredItem);
  return clean(state.message)||'Choose a tool to edit your model.';
 }
 function drawFooter(){const text=statusText();repaint(message,(c,w,h)=>{c.textAlign='left';c.textBaseline='middle';c.fillStyle=state.dragging?'#b1ffe5':hoveredItem?'#d0faec':'#d8e4f5';c.fillText(fit(c,text,w-28,36,28,600),14,h/2);},JSON.stringify([text,!!state.dragging,!!hoveredItem]));}
 function update(next={}){
  if(disposed)return;const incoming=typeof next==='string'?{message:next}:next||{};state={...state,...incoming};if(incoming.help!==undefined&&incoming.helpVisible===undefined)state.helpVisible=!!incoming.help;
  const page=pages[state.page]?state.page:'tools',pageKey=wheelKind?'wheel-'+wheelKind:state.helpVisible?'guide':page;if(pageKey!==currentPage)installPage(pageKey);
  const key=JSON.stringify([state,wheelKind]);if(key===signature)return;signature=key;
  const helping=!!state.helpVisible&&!wheelKind,[title,kicker]=pageTitles[helping?'guide':page]||pageTitles.tools;
  selection.mesh.position.y=wheelKind?.205:.150;hint.mesh.visible=!helping;statusLine.visible=!helping;
  message.mesh.position.y=helping?-.272:wheelKind?-.238:-.221;hint.mesh.position.y=wheelKind?-.283:-.278;statusLine.position.y=wheelKind?-.207:-.187;
  repaint(header,(c,w,h)=>{icon(c,wheelKind?'grid':'cube',35,54,42,'#a8edd9');c.textAlign='left';c.textBaseline='middle';c.fillStyle='#b4bfd6';c.font='700 21px system-ui,sans-serif';c.fillText('MODEL STUDIO',78,24);c.fillStyle='#f3f6ff';c.fillText(fit(c,wheelKind?(wheelKind==='brush'?'Choose a brush':wheelKind==='studio'?'Choose a studio':'Choose a tool'):title,760,48,38,750),77,73);
   const label=trackingLabel();const pillW=286,pillX=w-pillW-3;rounded(c,pillX,30,pillW,55,27);c.fillStyle='#243c40';c.fill();c.beginPath();c.arc(pillX+23,57,5,0,Math.PI*2);c.fillStyle=state.tracking===false||state.tracking===0?'#f3d69b':'#9ef2d4';c.fill();c.fillStyle='#bcebdc';c.textAlign='left';c.fillText(fit(c,label,pillW-54,25,21,650),pillX+41,57);},JSON.stringify([title,kicker,helping,wheelKind,trackingLabel(),state.tracking]));
  const count=Math.max(Number(state.selectedCount)||0,state.selectedName?1:0),radius=Number(state.brushRadius),strength=Number(state.brushStrength);
  const context=wheelKind?'HOLD · POINT · RELEASE':helping?'CONTROLLERS WORK TOGETHER':page==='sculpt'?String(state.sculptTool).toUpperCase()+' · Radius '+(Number.isFinite(radius)?radius.toFixed(2):'—')+' · Strength '+(Number.isFinite(strength)?Math.round(strength*100)+'%':'—')+(state.selectedRegionId?' · Mask on':''):page==='draw'?(state.mode==='lasso'?'LASSO':'OUTLINE')+' · '+(Number(state.drawPointCount)||0)+' points':page==='aim'?'POINTER ALIGNMENT · '+state.aimHand.toUpperCase()+' HAND':page==='views'?'DISPLAY · '+String(state.displayMode).toUpperCase():page==='cameras'?'ANGLE · '+String(state.viewMode).toUpperCase():count>0?count+' SELECTED · '+clean(state.selectedName,58):kicker;
  repaint(selection,(c,w,h)=>{c.fillStyle='#b9c8df';c.textAlign='left';c.textBaseline='middle';c.fillText(fit(c,context,w-20,31,25,650),10,h/2);},context);
  for(const item of allItems)if(item.mesh.visible)drawButton(item);
  repaint(wheelCenter,(c,w,h)=>{c.beginPath();c.arc(w/2,h/2,w*.46,0,Math.PI*2);c.fillStyle='#182b36';c.fill();c.strokeStyle='#5e9c94';c.lineWidth=2;c.stroke();icon(c,wheelKind==='brush'?'brush':wheelKind==='studio'?'cube':'grid',w/2,h*.40,70,'#a7f2da');c.fillStyle='#e1f6ee';c.textAlign='center';c.textBaseline='middle';c.font='700 29px system-ui,sans-serif';c.fillText('RELEASE '+(wheelKind==='studio'?'X':'A'),w/2,h*.72);},wheelKind);
  drawFooter();const controller=wheelKind?'Release off a card to keep your tool · B cancels':helping?'Inspect changes the view · edit tools change the model':page==='sculpt'?'Trigger: sculpt · Left stick: radius / strength · Hold A: brushes':page==='draw'?'Trigger: trace · Grip: extrude · Hold X: studio':page==='aim'?'Adjust hand yaw / pitch to align the pointer':(clean(state.controllerHint).length<=65?clean(state.controllerHint):'')||'Hold A: tools · Hold X: studio · Y: Undo · X+Y: Redo';
  repaint(hint,(c,w,h)=>{c.textAlign='left';c.textBaseline='middle';c.fillStyle='#a6b5ce';c.fillText(fit(c,controller,w-28,28,23,550),14,h/2);},controller);
  root.updateWorldMatrix(true,true);
 }
 function resolveItem(target){if(!target)return null;if(typeof target==='string')return buttons.get(target)||navSlots.find(i=>i.id===target&&i.mesh.visible)||null;const object=target.object||target;return allItems.find(item=>item.mesh===object)||null;}
 function hover(target){if(disposed)return;const candidate=resolveItem(target),next=candidate?.mesh.visible?candidate:null;if(next===hoveredItem)return;const previous=hoveredItem;hoveredItem=next;if(previous)drawButton(previous);if(next)drawButton(next);drawFooter();activeMotion=true;}
 function press(target){if(disposed||!visibleState)return false;const item=resolveItem(target);if(!item||!item.mesh.visible||!enabled(item.id))return false;const previous=pressedItem;pressedItem=item;pressedRemaining=.18;if(previous&&previous!==item)drawButton(previous);drawButton(item);activeMotion=true;return true;}
 function openWheel(kind='tools'){if(disposed||!wheels[kind])return false;wheelKind=kind;currentPage='';signature='';update({helpVisible:false});return true;}
 function closeWheel(){if(disposed||!wheelKind)return false;wheelKind=null;currentPage='';signature='';update();return true;}
 function releaseWheel(target=hoveredItem?.mesh){if(disposed||!wheelKind)return null;const item=resolveItem(target),chosen=item?.mesh.visible&&item.role==='tool'&&enabled(item.id)?item.id:null;closeWheel();return chosen;}
 function hitTest(raycaster){if(disposed||!visibleState||!raycaster?.intersectObjects)return null;for(let p=root;p;p=p.parent)if(p.visible===false)return null;return raycaster.intersectObjects(targets,false)[0]||null;}
 function damp(value,target,dt,speed=20){const next=value+(target-value)*(1-Math.exp(-speed*dt));return Math.abs(next-target)<.00001?target:next;}
 function tick(delta,settings={}){
  if(disposed)return;const dt=Number.isFinite(delta)?Math.min(.05,Math.max(0,delta)):0,lastVisible=visibleState;visibleState=settings.visible!==false;reducedMotion=!!settings.reducedMotion;
  if(!visibleState){if(lastVisible){hover(null);const old=pressedItem;pressedItem=null;pressedRemaining=0;if(old)drawButton(old);}reveal=0;transition=1;for(const item of allItems){item.lift=0;item.halo=0;item.mesh.position.copy(item.home);item.mesh.material.opacity=0;item.glow.visible=false;}for(const item of surfaces)item.mesh.material.opacity=0;lineMaterial.opacity=0;activeMotion=false;lastTickDelta=0;return;}
  elapsed+=dt;lastTickDelta=0;if(!lastVisible)reveal=0;
  if(pressedRemaining>0){pressedRemaining=Math.max(0,pressedRemaining-dt);if(!pressedRemaining){const old=pressedItem;pressedItem=null;if(old)drawButton(old);}}
  reveal=reducedMotion?1:damp(reveal,1,dt,18);transition=reducedMotion?1:damp(transition,1,dt,24);
  const globalAlpha=.60+.40*reveal,pageAlpha=.72+.28*transition;
  for(const item of surfaces)item.mesh.material.opacity=globalAlpha*(item===guide||item===wheelCenter?pageAlpha:1);
  for(const item of allItems){const over=hoveredItem===item&&!item.mesh.userData.se340Disabled,on=active(item),down=pressedItem===item;
   const targetLift=reducedMotion?0:down?-.0025:over?.0055:on?.0015:0,targetHalo=reducedMotion?(over||down?.45:on?.18:0):down?.8:over?.52:on?.16:0;
   const lift=reducedMotion?targetLift:damp(item.lift,targetLift,dt,24),halo=reducedMotion?targetHalo:damp(item.halo,targetHalo,dt,18);lastTickDelta=Math.max(lastTickDelta,Math.abs(lift-targetLift),Math.abs(halo-targetHalo));item.lift=lift;item.halo=halo;
   item.mesh.position.copy(item.home);item.mesh.position.z+=lift+(reducedMotion?0:-.006*(1-transition));item.mesh.material.opacity=globalAlpha*pageAlpha;
   item.glow.visible=item.mesh.visible&&halo>0;item.glow.position.copy(item.mesh.position);item.glow.position.z-=.001;item.glow.scale.copy(item.mesh.scale);item.glow.material.opacity=halo*globalAlpha;item.glow.material.color.setHex(on?0xf0cd91:0x9df5dc);
  }
  lineMaterial.opacity=state.dragging?.78:.38;statusLine.scale.x=state.dragging&&!reducedMotion?.92+.08*Math.sin(elapsed*3):1;
  activeMotion=!reducedMotion&&(reveal!==1||transition!==1||lastTickDelta>0||pressedRemaining>0||!!state.dragging);root.updateWorldMatrix(true,true);
 }
 function dispose(){if(disposed)return;disposed=true;root.removeFromParent();root.clear();targets.length=0;for(const t of textures)t.dispose();for(const m of materials)m.dispose();for(const g of geometries.values())g.dispose();hoveredItem=null;pressedItem=null;pressedRemaining=0;activeMotion=false;}
 update(typeof status==='string'?{message:status}:status);
 return Object.freeze({root,targets,update,hover,press,hitTest,dispose,openWheel,closeWheel,releaseWheel,tick,
  inspect:()=>({width:WIDTH,height:HEIGHT,page:currentPage,wheel:wheelKind,wheelVisible:!!wheelKind,helpVisible:!!state.helpVisible&&!wheelKind,hovered:hoveredItem?.id||null,pressed:pressedItem?.id||null,selectedCount:state.selectedCount,brushRadius:state.brushRadius,brushStrength:state.brushStrength,sculptTool:state.sculptTool,drawPointCount:state.drawPointCount,twoHand:!!state.twoHand,selectedRegionId:state.selectedRegionId,buttonCount:buttons.size,targetCount:targets.length,textureCount:textures.size,materialCount:materials.size,geometryCount:geometries.size,effectCount:allItems.length+1,paintCount,disposed,motion:{reveal,transition,active:activeMotion,visible:visibleState,reducedMotion,elapsed}})});
}
/* SE360_MODEL_VR_UI_END */
