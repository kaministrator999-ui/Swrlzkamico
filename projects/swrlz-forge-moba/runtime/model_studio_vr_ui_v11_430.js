/* SE360_MODEL_VR_UI_START */
/* SE390_MODEL_VR_FLUENT_UI */
/* SE410_MODEL_VR_ACCESSORY_UI */
/* SE415_MODEL_VR_ICONOGRAPHY */
/* SE417_MODEL_VR_OBJECT_INDEX_UI */
/* SE430_MODEL_VR_VISUAL_TEACHING */
// World-space Model Studio console. Rendering and input remain in the engine's
// existing XR loop; tick only animates owned presentation meshes/materials.
function se340CreateModelVRUI(options){
 'use strict';
 const {THREE:T,actions={},status={}}=options||{};
 if(!T?.Group)throw Error('Model VR UI requires Three.js.');
 const WIDTH=.64,HEIGHT=.62;
 const root=new T.Group();root.name='Model Studio · spatial console';root.scale.setScalar(1.16);
 root.userData.editorOnly=true;root.userData.se340ModelUI=true;
 const targets=[],textures=new Set(),materials=new Set(),geometries=new Map(),slots=[],navSlots=[];
 const buttons=new Map();let disposed=false,hoveredItem=null,pressedItem=null,pressedRemaining=0,paintCount=0,signature='',wheelKind=null,currentPage='';
 let visibleState=true,reducedMotion=false,reveal=0,transition=1,elapsed=0,activeMotion=true,lastTickDelta=0;
 let state={mode:'inspect',selectedName:'',hoverName:'',dragging:false,canUndo:false,canRedo:false,
  message:'Choose a part, then choose a tool.',tracking:null,precision:false,snap:false,helpVisible:false,controllerHint:'',page:'tools',viewMode:'orbit',displayMode:'textured',aimHand:'right',aimYaw:0,aimPitch:0,selectedCount:0,indexEntries:[],indexSelected:[],indexTotal:0,indexPage:0,indexMulti:false,sculptTool:'push',brushRadius:.08,brushStrength:.35,drawPointCount:0,twoHand:false,selectedRegionId:null,creationActive:false,creationKind:'',creationSize:0,accessoryActive:false,accessoryParams:null,accessoryDimensionLabels:null,accessoryStyleName:'Walnut',accessoryGapLabel:'',accessoryFit:'free',accessoryTargetName:''};
 const clean=(value,max=100)=>String(value??'').replace(/[\r\n\t]/g,' ').slice(0,max);
 function geometry(w,h){const key=w+':'+h;if(!geometries.has(key))geometries.set(key,new T.PlaneGeometry(w,h));return geometries.get(key);}
 function rounded(c,x,y,w,h,r){c.beginPath();if(c.roundRect)c.roundRect(x,y,w,h,r);else{c.moveTo(x+r,y);c.lineTo(x+w-r,y);c.quadraticCurveTo(x+w,y,x+w,y+r);c.lineTo(x+w,y+h-r);c.quadraticCurveTo(x+w,y+h,x+w-r,y+h);c.lineTo(x+r,y+h);c.quadraticCurveTo(x,y+h,x,y+h-r);c.lineTo(x,y+r);c.quadraticCurveTo(x,y,x+r,y);}c.closePath();}
 function gradient(c,x,y,x2,y2,stops){if(!c.createLinearGradient)return stops[0][1];const g=c.createLinearGradient(x,y,x2,y2);for(const [at,color]of stops)g.addColorStop(at,color);return g;}
 function surface(name,w,h,pw,ph,z=0){
  const canvas=document.createElement('canvas');canvas.width=pw;canvas.height=ph;const context=canvas.getContext('2d');if(!context)throw Error('Model VR labels require a 2D canvas.');
  const texture=new T.CanvasTexture(canvas);texture.colorSpace=T.SRGBColorSpace;texture.minFilter=T.LinearMipmapLinearFilter;texture.magFilter=T.LinearFilter;texture.generateMipmaps=true;texture.anisotropy=8;textures.add(texture);
  const material=new T.MeshBasicMaterial({map:texture,transparent:true,depthTest:false,depthWrite:false,toneMapped:false,side:T.DoubleSide});materials.add(material);
  const mesh=new T.Mesh(geometry(w,h),material);mesh.name=name;mesh.position.z=z;mesh.renderOrder=8301;mesh.frustumCulled=false;mesh.userData.editorOnly=true;mesh.userData.se340UI=true;root.add(mesh);
  return {mesh,canvas,context,texture,baseZ:z,baseOpacity:1};
 }
 function repaint(item,draw,key){if(disposed||key!==undefined&&item.drawKey===key)return;item.drawKey=key;const {context:c,canvas}=item;c.clearRect(0,0,canvas.width,canvas.height);draw(c,canvas.width,canvas.height);item.texture.needsUpdate=true;paintCount++;}
 function fit(c,text,max,font=42,min=30,weight=650){text=clean(text);let size=font;for(;size>min;size-=2){c.font=weight+' '+size+'px system-ui,sans-serif';if(c.measureText(text).width<=max)break;}c.font=weight+' '+size+'px system-ui,sans-serif';while(text.length>2&&c.measureText(text).width>max)text=text.slice(0,-2)+'…';return text;}
 function iconType(id){
   if(id==='se416-leather')return 'leather';if(id==='se416-metal')return 'detail';if(id==='se416-shade-plus')return 'star';if(id==='se416-shade-minus')return 'leather';
  // Preserve existing tool dispatch; customize only the pictogram for each control.
  if(id==='objects')return 'layers';
  if(id==='index-add')return 'multi';
  if(id==='index-prev')return 'left-arrow';
  if(id==='index-next')return 'right-arrow';
  if(id.startsWith('index-part-'))return 'cube';
  const se414Icons={
   selector:'select','selector-sweep':'sweep','selector-lasso-front':'lasso-front',
   'selector-lasso-through':'lasso-through',projects:'folder',grab:'grab',
   'save-local':'save','save-account':'cloud','clone-project':'clone',
   'menu-reset':'reset-menu','menu-hide':'hide-menu','aim-hand':'controller',
   'aim-reset':'reset','aim-reset-all':'reset-both',
   'display-textured':'texture','display-solid':'solid',
   'display-wireframe':'wire','display-xray':'xray','display-normals':'normals'
  };
  if(se414Icons[id])return se414Icons[id];
  if(id.startsWith('view-'))return id;
  if(id.startsWith('aim-yaw-'))return 'yaw';
  if(id.startsWith('aim-pitch-'))return 'pitch';
  if(id==='manual-mesh')return 'wire';
  if(id.startsWith('manual-'))return {'manual-pick':'face','manual-convert':'convert','manual-learn':'help','manual-preview':'eye','manual-apply':'confirm','manual-cancel':'clear','manual-amount-minus':'scale','manual-amount-plus':'scale','manual-direction':'extrude'}[id]||id.slice(7);
  if(id.startsWith('sculpt-'))return id.slice(7);if(id.startsWith('brush-radius'))return 'radius';if(id.startsWith('brush-strength'))return 'strength';
  if(id.startsWith('view-'))return 'cube';if(id.startsWith('display-'))return id.includes('wire')?'wire':id.includes('normal')?'normals':'display';
  if(id.startsWith('aim-'))return 'aim';if(id==='draw-clear'||id==='selection-clear')return 'clear';if(id==='draw-finish')return 'face';if(id==='lasso-clear')return 'whole';
  if(id==='create-pouch'||id==='accessory-menu')return 'pouch';
  if(id.startsWith('accessory-'))return id.includes('width')?'width':id.includes('height')?'height':id.includes('depth')?'depth':id.includes('rounding')?'rounding':id.includes('thickness')?'thickness':id.includes('flap')?'flap':id.includes('strap')?'strap':id.includes('stitch')?'stitch':id.includes('emblem')?(String(state.accessoryParams?.emblem).includes('star')?'star':state.accessoryParams?.emblem==='none'?'clear':'leaf'):id.includes('material')?'leather':id.includes('gap')?'gap':id.includes('reset')?'reset':id.includes('body')?'pouch':id.includes('detail')?'detail':id.includes('align')?'align':'fit';
  if(id.startsWith('create-'))return id==='create-menu'?'cube':id==='create-sphere'?'sphere':id==='create-cone'?'cone':id==='create-cylinder'?'cylinder':'cube';
  return {grab:'hands',duplicate:'duplicate',tools:'grid',mesh:'cube',studio:'grid',views:'display',cameras:'cube',help:'help',focus:'focus',recenter:'focus',sculpt:'brush',draw:'pen',lasso:'lasso','two-hand':'hands',inspect:'eye',exit:'exit',precision:'precision',snap:'snap','save-local':'cube','save-account':'display','clone-project':'cube','menu-reset':'focus','menu-hide':'eye'}[id]||id;
 }
 function icon(c,type,x,y,size,color){
  const teaching=window.SWYRL_MODEL_TEACHING;
  if(teaching?.get(type)?.id===type){teaching.drawIcon(c,type,x,y,size,color);return;}
  if(type==='confirm'){c.save();c.strokeStyle=color;c.lineWidth=3;c.beginPath();c.moveTo(x-size*.3,y);c.lineTo(x-size*.06,y+size*.25);c.lineTo(x+size*.34,y-size*.28);c.stroke();c.restore();return;}
  c.save();c.translate(x,y);c.scale(size/48,size/48);c.strokeStyle=color;c.fillStyle=color;c.lineWidth=2.5;c.lineCap='round';c.lineJoin='round';
  const path=(points,close=false)=>{c.beginPath();points.forEach((p,i)=>i?c.lineTo(...p):c.moveTo(...p));if(close)c.closePath();c.stroke();};
  const circle=(x,y,r)=>{c.beginPath();c.arc(x,y,r,0,Math.PI*2);c.stroke();};
   if(type==='layers'){for(const [x,y]of [[0,-12],[-3,0],[0,12]]){path([[-19+x,y],[0+x,y-10],[19+x,y],[0+x,y+10],[-19+x,y]],true);}}
   else if(type==='multi'){rounded(c,-20,-18,24,24,3);c.stroke();rounded(c,-7,-5,24,24,3);c.stroke();path([[5,-20],[5,-9]]);path([[-1,-14],[11,-14]]);}
   else if(type==='left-arrow'||type==='right-arrow'){c.save();if(type==='left-arrow')c.scale(-1,1);path([[-16,-13],[0,-13],[0,-21],[18,0],[0,21],[0,13],[-16,13]]);c.restore();}
   else if(type==='select'){path([[-19,-18],[-19,15],[0,5],[9,22],[16,18],[7,1],[21,-2],[-19,-18]],true);}
   else if(type==='sweep'){c.setLineDash?.([4,4]);rounded(c,-21,-17,42,31,5);c.stroke();c.setLineDash?.([]);path([[-16,19],[-4,8],[6,17],[19,3]]);}
   else if(type==='lasso-front'||type==='lasso-through'){c.setLineDash?.([4,4]);c.beginPath();c.ellipse?.(0,0,19,14,-.25,0,Math.PI*2);c.stroke();c.setLineDash?.([]);if(type==='lasso-through'){c.beginPath();c.ellipse?.(4,-3,12,20,.3,0,Math.PI*2);c.stroke();}else circle(0,0,5);}
   else if(type==='folder'||type==='clone'){path([[-21,-14],[-7,-14],[-2,-8],[21,-8],[21,15],[-21,15],[-21,-14]],true);if(type==='clone')path([[-13,-20],[8,-20],[13,-15]]);}
   else if(type==='save'){rounded(c,-19,-21,38,42,4);c.stroke();rounded(c,-10,-20,21,14,2);c.stroke();rounded(c,-12,5,24,16,2);c.stroke();path([[5,-20],[5,-8]]);}
   else if(type==='cloud'){c.beginPath();c.moveTo(-13,14);c.bezierCurveTo(-26,13,-24,-7,-12,-8);c.bezierCurveTo(-8,-28,15,-25,18,-9);c.bezierCurveTo(32,2,22,16,12,15);c.closePath();c.stroke();path([[0,18],[0,-6],[-7,1],[0,-6],[7,1]]);}
   else if(type==='reset-menu'||type==='hide-menu'){rounded(c,-21,-16,42,32,5);c.stroke();path([[-21,-6],[21,-6]]);if(type==='reset-menu'){c.beginPath();c.arc(1,4,9,-Math.PI*.65,Math.PI*.8);c.stroke();path([[-9,-5],[-10,4],[-1,1]]);}else{path([[-23,22],[23,-22]]);}}
   else if(type==='grab'){rounded(c,-12,-4,24,26,7);c.stroke();for(const x of [-9,-3,3,9])path([[x,-5],[x,-19]]);path([[13,10],[22,2],[22,-4]]);}
   else if(type==='controller'){rounded(c,-11,-19,22,31,9);c.stroke();circle(0,-9,4);path([[0,12],[0,22]]);path([[5,-9],[20,-17]]);}
   else if(type==='yaw'||type==='pitch'){c.save();if(type==='pitch')c.rotate(Math.PI/2);circle(0,0,7);c.beginPath();c.arc(0,0,19,-Math.PI*.75,Math.PI*.60);c.stroke();path([[-19,-16],[-19,-6],[-8,-9]]);c.restore();}
   else if(type==='reset-both'){rounded(c,-23,-11,18,26,5);c.stroke();rounded(c,5,-11,18,26,5);c.stroke();path([[-8,-21],[0,-16],[8,-21]]);}
   else if(type==='texture'){rounded(c,-20,-20,40,40,3);c.stroke();for(let y=0;y<2;y++)for(let x=0;x<2;x++)if((x+y)%2===0)c.fillRect(-20+x*20,-20+y*20,20,20);}
   else if(type==='xray'){path([[0,-20],[18,-10],[18,11],[0,21],[-18,11],[-18,-10],[0,-20]],true);path([[-18,-10],[0,0],[18,-10]]);c.setLineDash?.([3,3]);path([[0,0],[0,21]]);path([[-18,11],[18,-10]]);c.setLineDash?.([]);}
   else if(type==='solid'){path([[0,-20],[18,-10],[18,11],[0,21],[-18,11],[-18,-10],[0,-20]],true);path([[-18,-10],[0,0],[18,-10]]);path([[0,0],[0,21]]);c.globalAlpha=.30;path([[0,0],[18,-10],[18,11],[0,21]],true);c.globalAlpha=1;}
   else if(type.startsWith('view-')){const side=type.slice(5),tag={front:'F',back:'B',left:'L',right:'R',top:'T',bottom:'D',iso:'3D'}[side]||'V';path([[-18,-18],[18,-18],[18,18],[-18,18],[-18,-18]],true);c.font='700 23px system-ui,sans-serif';c.textAlign='center';c.textBaseline='middle';c.fillText(tag,0,1);}
   else if(type==='rotate'){c.beginPath();c.arc(0,0,17,-Math.PI*.60,Math.PI*.13);c.stroke();c.beginPath();c.arc(0,0,17,Math.PI*.38,Math.PI*1.1);c.stroke();path([[16,-13],[18,2],[7,-1]]);path([[-16,13],[-18,-2],[-7,1]]);}
   else if(type==='eye'){c.beginPath();c.moveTo(-20,0);c.quadraticCurveTo(0,-24,20,0);c.quadraticCurveTo(0,24,-20,0);c.stroke();circle(0,0,6);}
  else if(type==='move'){path([[-19,0],[19,0]]);path([[0,-19],[0,19]]);for(const [x,y,dx,dy]of [[19,0,-5,5],[-19,0,5,5],[0,-19,5,5],[0,19,5,-5]]){path([[x+(y?dx:dx),y+(x?dy:dy)],[x,y],[x+(y?-dx:dx),y+(x?-dy:dy)]]);}}
  else if(type==='rotate'||type==='undo'||type==='redo'){c.save();if(type==='redo')c.scale(-1,1);c.beginPath();c.arc(0,1,16,-Math.PI*.8,Math.PI*.65);c.stroke();path([[-15,-18],[-17,-7],[-6,-9]]);c.restore();}
  else if(type==='sphere'){circle(0,0,19);c.beginPath();c.ellipse?.(0,0,8,19,0,0,Math.PI*2);c.stroke();path([[-18,0],[18,0]]);}
  else if(type==='cone'){path([[0,-21],[20,16],[-20,16],[0,-21]],true);c.beginPath();c.ellipse?.(0,16,20,5,0,0,Math.PI*2);c.stroke();}
  else if(type==='cylinder'){path([[-17,-13],[-17,15],[17,15],[17,-13]]);c.beginPath();c.ellipse?.(0,-13,17,6,0,0,Math.PI*2);c.stroke();c.beginPath();c.ellipse?.(0,15,17,6,0,0,Math.PI);c.stroke();}
  else if(type==='duplicate'){rounded(c,-19,-19,27,27,4);c.stroke();rounded(c,-8,-8,27,27,4);c.stroke();}
  else if(type==='pouch'){rounded(c,-18,-12,36,32,7);c.stroke();path([[-18,-9],[0,3],[18,-9]]);rounded(c,-4,1,8,9,2);c.stroke();path([[-11,-13],[-11,-20],[-5,-20],[-5,-13]]);path([[5,-13],[5,-20],[11,-20],[11,-13]]);}
  else if(type==='flap'){path([[-19,-13],[19,-13],[17,7],[0,17],[-17,7],[-19,-13]],true);path([[-17,-7],[0,7],[17,-7]]);circle(0,9,3);}
  else if(type==='strap'){c.beginPath();c.moveTo(-18,17);c.bezierCurveTo(-24,-19,24,-19,18,17);c.stroke();c.beginPath();c.moveTo(-10,17);c.bezierCurveTo(-15,-9,15,-9,10,17);c.stroke();path([[-18,17],[-10,17]]);path([[10,17],[18,17]]);}
  else if(type==='stitch'){rounded(c,-19,-17,38,34,6);c.stroke();c.setLineDash?.([3,4]);rounded(c,-13,-11,26,22,3);c.stroke();c.setLineDash?.([]);}
  else if(type==='leaf'){path([[0,20],[0,-12]]);c.beginPath();c.moveTo(0,3);c.quadraticCurveTo(-24,1,-18,-16);c.quadraticCurveTo(1,-16,0,3);c.moveTo(0,-4);c.quadraticCurveTo(20,-10,16,-23);c.quadraticCurveTo(-1,-20,0,-4);c.stroke();}
  else if(type==='star'){const points=[];for(let i=0;i<10;i++){const a=-Math.PI/2+i*Math.PI/5,r=i%2?8:20;points.push([Math.cos(a)*r,Math.sin(a)*r]);}path(points,true);}
  else if(type==='leather'){path([[-18,-18],[16,-18],[22,-8],[17,18],[-17,18],[-22,6],[-18,-18]],true);path([[-12,-10],[-7,-8]]);path([[6,-2],[11,1]]);path([[-8,10],[-2,10]]);}
  else if(type==='width'||type==='height'||type==='depth'){rounded(c,-12,-12,24,24,4);c.stroke();c.save();if(type==='height')c.rotate(Math.PI/2);if(type==='depth')c.rotate(-Math.PI/4);path([[-23,0],[-15,0]]);path([[15,0],[23,0]]);path([[-18,-5],[-23,0],[-18,5]]);path([[18,-5],[23,0],[18,5]]);c.restore();}
  else if(type==='rounding'){path([[-19,17],[-19,-3]]);c.beginPath();c.moveTo(-19,-3);c.quadraticCurveTo(-19,-19,-3,-19);c.lineTo(18,-19);c.stroke();c.setLineDash?.([3,3]);path([[-9,17],[-9,-3],[18,-3]]);c.setLineDash?.([]);}
  else if(type==='thickness'){path([[-19,-8],[0,-18],[19,-8],[0,2],[-19,-8]],true);path([[-19,1],[0,11],[19,1]]);path([[-19,10],[0,20],[19,10]]);}
  else if(type==='fit'||type==='align'||type==='gap'){rounded(c,-18,-17,36,34,6);c.stroke();path([[-23,0],[-13,0]]);path([[13,0],[23,0]]);path([[0,-23],[0,-13]]);path([[0,13],[0,23]]);if(type==='gap')path([[-8,0],[8,0]]);else circle(0,0,5);}
  else if(type==='detail'){path([[-20,15],[-20,-15],[20,-15],[20,15],[-20,15]],true);path([[-13,-5],[13,-5]]);path([[-13,4],[3,4]]);circle(12,5,3);}
  else if(type==='reset'){c.beginPath();c.arc(0,1,17,-Math.PI*.75,Math.PI*.9);c.stroke();path([[-18,-18],[-18,-6],[-6,-8]]);}
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
   else{path([[-19,-14],[19,-14]]);path([[-19,0],[19,0]]);path([[-19,14],[19,14]]);circle(-6,-14,4);circle(8,0,4);circle(-3,14,4);}
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
 function addGlow(item){const material=new T.MeshBasicMaterial({map:glowTexture,color:0x9df5db,transparent:true,opacity:0,depthTest:false,depthWrite:false,toneMapped:false});materials.add(material);const mesh=new T.Mesh(geometry(item.role==='nav'?.087:.212,item.role==='nav'?.053:.080),material);mesh.renderOrder=8303;mesh.frustumCulled=false;mesh.userData.editorOnly=true;root.add(mesh);item.glow=mesh;item.lift=0;item.halo=0;}
 const pages={
  tools:[
   ['grab','Grab'],['move','Move'],['rotate','Rotate'],
   ['scale','Scale'],['sculpt','Sculpt'],['create-menu','Create'],
   ['two-hand','Two hands'],['undo','Undo'],['redo','Redo'],
   ['focus','Focus'],['studio','Studio'],['exit','Exit VR']
  ],
  mesh:[
   ['inspect','Inspect'],['move','Move'],['rotate','Rotate'],
   ['scale','Scale'],['precision','Precision'],['snap','Snap'],
   ['selection-clear','Clear selection'],['undo','Undo'],['redo','Redo'],
   ['grab','Grab'],['manual-mesh','Manual modeling'],['exit','Exit VR']
  ],
  'manual-mesh':[
   ['manual-convert','Make editable'],['manual-pick','Pick flat region'],['manual-learn','Learn this tool'],
   ['manual-inset','Inset'],['manual-extrude','Extrude'],['manual-solidify','Solidify'],
   ['manual-deleteFaces','Delete faces'],['manual-subdivide','Subdivide'],['manual-repairNormals','Repair normals'],
   ['mesh','Object tools'],['tools','Quick tools'],['exit','Exit VR']
  ],
  'manual-operation':[
   ['manual-amount-minus','Amount −'],['manual-amount-plus','Amount +'],['manual-direction','In / out'],
   ['manual-preview','Preview geometry'],['manual-apply','Apply geometry'],['manual-cancel','Cancel preview'],
   ['manual-pick','Pick flat region'],['manual-convert','Make editable'],['manual-learn','Learn this tool'],
   ['manual-mesh','Manual tools'],['tools','Quick tools'],['exit','Exit VR']
  ],
  studio:[
   ['mesh','Mesh tools'],['sculpt','Sculpt'],['draw','Draw mesh'],
   ['views','Display'],['aim','Pointer aim'],['help','Guide'],
   ['save-local','Save project'],['save-account','Save to account'],['clone-project','Clone project'],
   ['menu-reset','Reset menu'],['menu-hide','Hide menu'],['exit','Exit VR']
  ],
  objects:[],
  selector:[
   ['selector-sweep','Swipe · trigger'],['selector-lasso-front','Lasso · front'],['selector-lasso-through','Lasso · through'],
   ['selection-clear','Clear selection'],['undo','Undo'],['redo','Redo'],
   ['move','Move selected'],['rotate','Rotate selected'],['scale','Scale selected'],
   ['mesh','Mesh tools'],['projects','Projects'],['help','Guide']
  ],
  projects:[
   ['save-account','Save to account'],['save-local','Save project'],['clone-project','Clone project'],
   ['menu-reset','Reset menu'],['menu-hide','Hide menu'],['studio','More tools'],
   ['help','Controller guide'],['tools','Model tools'],['exit','Exit VR']
  ],
  sculpt:[
   ['sculpt-push','Push'],['sculpt-smooth','Smooth'],['sculpt-flatten','Flatten'],
   ['sculpt-inflate','Inflate'],['sculpt-pinch','Pinch'],['sculpt-translate','Translate'],
   ['brush-radius-minus','Radius −'],['brush-radius-plus','Radius +'],['brush-strength-minus','Strength −'],
   ['brush-strength-plus','Strength +'],['studio','Studio'],['exit','Exit VR']
  ],
  create:[
   ['create-box','Cube'],['create-sphere','Sphere'],['create-cylinder','Cylinder'],
   ['create-cone','Cone'],['draw','Draw outline'],['sculpt','Sculpt'],
   ['duplicate','Duplicate'],['undo','Undo'],['accessory-menu','Accessories'],
   ['tools','Model tools'],['help','Guide'],['exit','Exit VR']
  ],
  accessory:[
   ['create-pouch','Hip pouch'],['accessory-body','Body shape'],['accessory-details','Flap & details'],
   ['accessory-fit','Fit & attach'],['accessory-material','Leather'],['accessory-stitches','Stitching'],
   ['accessory-emblem','Emblem'],['accessory-reset','Reset shape'],['create-menu','Other shapes'],
   ['tools','Model tools'],['help','Guide'],['exit','Exit VR']
  ],
  'accessory-body':[
   ['accessory-width-minus','Width −'],['accessory-width-plus','Width +'],['accessory-height-minus','Height −'],
   ['accessory-height-plus','Height +'],['accessory-depth-minus','Depth −'],['accessory-depth-plus','Depth +'],
   ['accessory-rounding-minus','Roundness −'],['accessory-rounding-plus','Roundness +'],['accessory-thickness-minus','Thickness −'],
   ['accessory-thickness-plus','Thickness +'],['accessory-menu','Accessories'],['exit','Exit VR']
  ],
  'accessory-details':[
   ['accessory-flap-minus','Flap −'],['accessory-flap-plus','Flap +'],['accessory-strap-minus','Strap −'],
   ['accessory-strap-plus','Strap +'],['accessory-stitches','Stitching'],['accessory-emblem','Emblem'],
   ['accessory-material','Leather'],['accessory-reset','Reset shape'],['accessory-fit','Fit & attach'],
   ['accessory-menu','Accessories'],['help','Guide'],['exit','Exit VR']
  ],
  'accessory-fit':[
   ['accessory-surface','Surface fit'],['accessory-free','Free placement'],['accessory-align','Align to surface'],
   ['accessory-gap-minus','Closer −'],['accessory-gap-plus','Gap +'],['focus','Focus selection'],
   ['accessory-body','Body shape'],['accessory-details','Flap & details'],['accessory-reset','Reset shape'],
   ['accessory-menu','Accessories'],['help','Guide'],['exit','Exit VR']
  ],
  draw:[
   ['draw','Draw outline'],['draw-finish','Make face'],['extrude','Thicken outline'],
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
  tools:[['grab','Grab'],['move','Move'],['rotate','Rotate'],['scale','Scale'],
   ['inspect','Inspect'],
   ['sculpt','Sculpt'],['draw','Draw mesh'],['two-hand','Two hands']],
  studio:[['mesh','Mesh tools'],['sculpt','Sculpt'],['create-menu','Create'],
   ['views','Display'],['aim','Pointer aim'],['help','Guide']],
  brush:[['sculpt-push','Push'],['sculpt-smooth','Smooth'],['sculpt-flatten','Flatten'],
   ['sculpt-inflate','Inflate'],['sculpt-pinch','Pinch'],['sculpt-translate','Translate']]
 };
 const details={objects:'All named meshes in the current project','index-add':'Toggle additive selection · up to 32 parts','index-prev':'Previous objects · same selection','index-next':'Next objects · same selection','accessory-menu':'Pouches, soft forms & fitted details','create-pouch':'Build a rounded leather hip bag','accessory-body':'Width, height, depth & soft edges','accessory-details':'Flap, strap, stitches & emblem','accessory-fit':'Position the pouch against a model','accessory-material':'Cycle coordinated leather colors','accessory-stitches':'Toggle neat edge stitching','accessory-emblem':'Choose a flap ornament','accessory-reset':'Restore the starting pouch shape','accessory-surface':'Place against the pointed model surface','accessory-free':'Place freely in the workspace','accessory-align':'Match the surface direction','accessory-gap-minus':'Bring the pouch nearer to the surface','accessory-gap-plus':'Leave more space from the surface',grab:'Grip moves and turns selection',duplicate:'Copy selected parts · X + Trigger','create-menu':'Primitives and drawing · X + A','create-box':'Preview, then Trigger to place','create-sphere':'Preview, then Trigger to place','create-cylinder':'Preview, then Trigger to place','create-cone':'Preview, then Trigger to place',selector:'Select overlapping model parts','selector-sweep':'Hold left trigger to add; retrace to remove','selector-lasso-front':'Left Grip · nearby-depth meshes','selector-lasso-through':'Left Grip · all depths in loop',projects:'Save and manage this project',inspect:'View without editing',move:'Position selection',rotate:'Turn selection',scale:'Resize selection',sculpt:'Shape the surface',draw:'Trace a new mesh','two-hand':'Use both grips',undo:'Previous edit',redo:'Restore an edit',focus:'Frame selection',studio:'Browse all tools',exit:'Return to studio',mesh:'Selection & transforms',views:'Material & wireframe',aim:'Align your pointer',help:'Controller controls',precision:'Fine controller motion',snap:'Step-based transforms',recenter:'Reset the workbench',tools:'Your editing toolkit','save-local':'On-device project save','save-account':'Sync cloud model and textures','clone-project':'Independent project copy','menu-reset':'Restore menu position','menu-hide':'X button brings it back','selection-clear':'Deselect all parts',extrude:'Pull a face into depth',lasso:'Mask a surface region','lasso-clear':'Turn off the mask','draw-clear':'Discard this outline','draw-finish':'Create a mesh face',cameras:'Front, side & top',
  'sculpt-push':'Raise or lower','sculpt-smooth':'Soften the surface','sculpt-flatten':'Level local detail','sculpt-inflate':'Build volume','sculpt-pinch':'Gather surface detail','sculpt-translate':'Pull the surface',
  'brush-radius-minus':'Smaller footprint','brush-radius-plus':'Larger footprint','brush-strength-minus':'Softer strokes','brush-strength-plus':'Stronger strokes'};
 const pageTitles={objects:['Object Index','NAMES · SINGLE · MULTI · SILHOUETTE'],'manual-mesh':['Manual mesh tools','SELECT A REAL FACE REGION'],'manual-operation':['Shape selected faces','PREVIEW · APPLY · CANCEL'],accessory:['Accessory workshop','SHAPE · DETAIL · FIT'],'accessory-body':['Pouch body','SHAPE & SOFT EDGES'],'accessory-details':['Pouch details','FLAP · STRAP · FINISH'],'accessory-fit':['Fit the pouch','PLACE IT ON YOUR MODEL'],create:['Create a model','CHOOSE · PREVIEW · PLACE'],selector:['Selector','SWEEP · FRONT LASSO · THROUGH LASSO'],projects:['My projects','SAVE · ACCOUNT · CLONE'],tools:['Quick tools','SELECT · SHAPE · CREATE'],mesh:['Mesh tools','SELECTION & TRANSFORMS'],studio:['Studio tools','YOUR MODELING WORKSPACE'],sculpt:['Sculpt surface','BRUSHES & SURFACE CONTROL'],draw:['Draw & build','OUTLINES · REGIONS · DEPTH'],views:['Model display','PREVIEW MATERIAL & STRUCTURE'],cameras:['Model angles','LOOK FROM EVERY SIDE'],aim:['Pointer alignment','CALIBRATE EACH CONTROLLER'],guide:['Controller guide','DEFAULT QUEST · LIVE LABELS FOLLOW YOUR PROFILE']};
 for(let i=0;i<12;i++){const item=surface('Model Studio · tool card '+i,.19,.066,570,198,.016);item.role='tool';item.home=new T.Vector3((i%3-1)*.202,.086-Math.floor(i/3)*.075,.016);item.mesh.position.copy(item.home);item.id='';item.label='';item.mesh.userData.se360Role='tool';item.mesh.renderOrder=8304;addGlow(item);slots.push(item);}
 [['tools','Tools'],['selector','Select'],['sculpt','Sculpt'],['create-menu','Create'],['views','Display'],['projects','Projects'],['objects','Objects']].forEach(([id,label],i)=>{const item=surface('Model Studio · navigation '+label,.083,.041,330,123,.016);item.id=id;item.label=label;item.role='nav';item.home=new T.Vector3((i-3)*.086,.198,.016);item.mesh.position.copy(item.home);item.mesh.userData.se340Action=id;item.mesh.userData.se360Role='nav';item.mesh.renderOrder=8304;addGlow(item);navSlots.push(item);});
 const allItems=[...slots,...navSlots],surfaces=[plate,header,selection,message,hint,guide,wheelCenter];
 function trackingLabel(){const value=state.tracking;if(typeof value==='number')return value>0?value+' CONNECTED':'NO CONTROLLERS';if(value===true)return 'CONNECTED';if(value===false)return 'NO CONTROLLERS';if(typeof value==='string')return clean(value,23);return 'VR WORKSPACE';}
 const accessoryPages=new Set(['accessory','accessory-body','accessory-details','accessory-fit']);
 const accessoryNavigation=new Set(['accessory-menu','accessory-body','accessory-details','accessory-fit']);
 function accessoryDimension(key){return clean(state.accessoryDimensionLabels?.[key]||'Live preview',24);}
 function accessoryEmblem(){const value=clean(state.accessoryParams?.emblem||'leaf',16);return value==='none'?'No emblem':value.charAt(0).toUpperCase()+value.slice(1);}
 function accessoryContext(){
  if(!state.accessoryActive)return 'A SMALL BAG · SHAPE IT YOUR WAY';
  if(state.page==='accessory-fit')return state.accessoryFit==='surface'?'SURFACE FIT · '+clean(state.accessoryTargetName||'POINT AT YOUR MODEL',52):'FREE PLACEMENT · POINT INTO THE WORKSPACE';
  const d=state.accessoryDimensionLabels||{};
  const size=[['W',d.width],['H',d.height],['D',d.depth]].filter(x=>x[1]).map(([k,v])=>k+' '+clean(v,18)).join(' · ');
  return size||'LIVE POUCH PREVIEW · '+clean(state.accessoryStyleName||'Walnut',20).toUpperCase();
 }
 function accessoryDescription(id){
  if(id==='create-pouch')return state.accessoryActive?'Preview active · tune it or place it':'Start a rounded leather pouch';
  if(!state.accessoryActive&&id.startsWith('accessory-')&&!accessoryNavigation.has(id))return 'Start a pouch preview first';
  const match=/^accessory-(width|height|depth|rounding|thickness|flap|strap)-(minus|plus)$/.exec(id);
  if(match){const word={width:['Narrower','Wider'],height:['Shorter','Taller'],depth:['Shallower','Deeper'],rounding:['Sharper edges','Softer edges'],thickness:['Thinner walls','Thicker walls'],flap:['Shorter cover','Longer cover'],strap:['Shorter loops','Longer loops']}[match[1]][match[2]==='plus'?1:0];return accessoryDimension(match[1])+' · '+word;}
  if(id==='accessory-material')return clean(state.accessoryStyleName||'Walnut',20)+' · coordinated colors';
  if(id==='accessory-stitches')return state.accessoryParams?.stitches===false?'Stitching off · click to add':'Stitching on · neat edge detail';
  if(id==='accessory-emblem')return accessoryEmblem()+' · click to change';
  if(id==='accessory-surface')return state.accessoryTargetName?'Fit against '+clean(state.accessoryTargetName,30):'Point at the model to fit the pouch';
  if(id==='accessory-free')return 'Move the pouch freely in space';
  if(id==='accessory-align')return 'Face the pointed surface cleanly';
  if(id==='accessory-gap-minus'||id==='accessory-gap-plus')return clean(state.accessoryGapLabel||'Surface spacing',24)+' · '+(id.endsWith('plus')?'More space':'Closer fit');
  return details[id]||'Refine the live accessory';
 }
 function enabled(id){
  if(id==='index-prev')return state.indexPage>0;
  if(id==='index-next')return state.indexPage<Math.ceil(state.indexTotal/9)-1;
  if(id==='manual-convert')return !state.manualPreview&&!!state.manualConvert?.available;
  if(id==='manual-apply'||id==='manual-cancel')return !!state.manualPreview;
  if(id==='manual-preview')return !!state.manualAvailability?.[state.manualOperation]?.available;
  if(id==='manual-direction')return state.manualOperation==='extrude';
  if(id.startsWith('manual-amount'))return ['inset','extrude','solidify','subdivide'].includes(state.manualOperation);
if(id.startsWith('accessory-')&&!accessoryNavigation.has(id)&&!state.accessoryActive)return false;return id==='undo'?!!state.canUndo:id==='redo'?!!state.canRedo:id==='duplicate'||id==='selection-clear'?state.selectedCount>0||!!state.selectedName:id==='draw-finish'?(state.drawPointCount||0)>=3:id==='draw-clear'?(state.drawPointCount||0)>0:true;}
 function active(item){const id=item.id;
  if(id==='index-add')return !!state.indexMulti;
  if(id.startsWith('index-part-')){const i=Number(id.slice(11))-state.indexPage*9;return state.indexSelected.includes(state.indexEntries[i]?.id);}
  if(item.role==='nav'){const p=state.helpVisible?'guide':state.page;return id==='help'?p==='guide':id==='tools'?['tools','mesh','studio','manual-mesh','manual-operation'].includes(p):id==='views'?['views','cameras','aim'].includes(p):id==='create-menu'?['create','draw',...accessoryPages].includes(p):p===id;}
  if(id==='create-pouch')return !!state.accessoryActive;if(id==='accessory-menu')return accessoryPages.has(state.page);if(id==='accessory-body'||id==='accessory-details'||id==='accessory-fit')return state.page===id;if(id==='accessory-stitches')return !!state.accessoryActive&&state.accessoryParams?.stitches!==false;if(id==='accessory-emblem')return !!state.accessoryActive&&state.accessoryParams?.emblem!=='none';if(id==='accessory-surface')return state.accessoryActive&&state.accessoryFit==='surface';if(id==='accessory-free')return state.accessoryActive&&state.accessoryFit!=='surface';
  if(id.startsWith('manual-'))return id==='manual-preview'?!!state.manualPreview:id==='manual-mesh'?['manual-mesh','manual-operation'].includes(state.page):id.slice(7)===state.manualOperation;
  return id.startsWith('selector-')?state.selectionMode===id.slice(9):['grab','inspect','move','rotate','scale','sculpt','draw','lasso','extrude','two-hand'].includes(id)?state.mode===id||id==='two-hand'&&!!state.twoHand:id.startsWith('sculpt-')?state.sculptTool===id.slice(7):id==='precision'?!!state.precision:id==='snap'?!!state.snap:id==='help'?!!state.helpVisible:id.startsWith('view-')?state.viewMode===id.slice(5):id.startsWith('display-')?state.displayMode===id.slice(8):false;}
 function label(item){
  if(item.id==='index-add')return state.indexMulti?'Multi: ON':'Multi: OFF';
  if(item.id.startsWith('manual-amount'))return (state.manualOperation==='inset'?'Inset ':state.manualOperation==='solidify'?'Thickness ':'Amount ')+(item.id.endsWith('plus')?'+':'−');
if(item.id==='create-pouch'&&state.accessoryActive)return 'Pouch preview';if(item.id==='accessory-stitches')return 'Stitching '+(state.accessoryParams?.stitches===false?'off':'on');if(item.id==='accessory-material')return clean(state.accessoryStyleName||'Leather',18);return item.id==='help'&&state.helpVisible?'Back to menu':item.id==='aim-hand'?'Hand: '+state.aimHand.toUpperCase():item.label;}
 function description(item){
  if(item.id.startsWith('index-part-')){const i=Number(item.id.slice(11))-state.indexPage*9;return state.indexSelected.includes(state.indexEntries[i]?.id)?'SELECTED · Trigger to '+(state.indexMulti?'remove':'keep'):'Trigger · '+(state.indexMulti?'add to selection':'select only this');}
  if(item.id==='index-add')return state.indexMulti?'Add / remove named parts':'Select only one named part';
  if(item.id==='index-prev'||item.id==='index-next')return 'Page '+(state.indexPage+1)+' / '+Math.max(1,Math.ceil(state.indexTotal/9));
  if(item.id==='help'&&state.learningTool)return 'Return to manual modeling tools';
  if(item.id.startsWith('manual-'))return manualDescription(item.id);
if(item.id.startsWith('accessory-')||item.id==='create-pouch')return accessoryDescription(item.id);if(item.id==='duplicate'&&!enabled(item.id))return 'Select parts before copying';if(item.id==='grab'&&!(state.selectedCount||state.selectedName))return 'Select a part, then hold Grip';if(item.id==='undo'&&!state.canUndo)return 'No earlier edits';if(item.id==='redo'&&!state.canRedo)return 'No later edits';if(item.id.startsWith('view-'))return 'Model orientation';if(item.id.startsWith('display-'))return 'Preview only';if(item.id.startsWith('aim-'))return 'Pointer calibration';return details[item.id]||'Modeling control';}
 function drawButton(item){
  if(!item.id)return;const disabled=!enabled(item.id),on=active(item),over=hoveredItem===item,down=pressedItem===item,tutorialOn=state.tutorialHighlight===item.id;
  item.mesh.userData.se340Disabled=disabled;item.mesh.userData.se340Selected=on;
  const text=label(item),sub=description(item),nav=item.role==='nav',key=JSON.stringify([item.id,text,sub,disabled,on,over,down,tutorialOn,!!wheelKind,item.id==='accessory-material'?state.accessoryParams?.color:null]);
  repaint(item,(c,w,h)=>{const entry=item.id==='create-pouch'||item.id==='accessory-menu',edge=disabled?'#485168':down?'#b5fff0':tutorialOn?'#e7ff74':over?'#a7f6df':on?'#eed5a0':entry?'#a78663':'#59617b';
   rounded(c,4,4,w-8,h-8,nav?25:22);c.fillStyle=gradient(c,0,0,w,h,[[0,disabled?'#1c2232':down?'#245f58':on?'#3c3544':over?'#294343':entry?'#3b303c':'#292d42'],[1,disabled?'#181e2b':down?'#1c403e':on?'#29283c':over?'#202f39':entry?'#292738':'#1e2537']]);c.fill();c.strokeStyle=edge;c.lineWidth=down||over||on||tutorialOn?4.4:2;c.stroke();
   c.strokeStyle='rgba(226,238,255,.055)';c.lineWidth=1;rounded(c,10,10,w-20,h-20,nav?20:17);c.stroke();
   const ink=disabled?'#8792aa':on?'#ffe6b4':over||down?'#c4ffef':entry?'#efd8b5':'#e6edf9';
   if(nav){icon(c,iconType(item.id),41,h/2,31,ink);c.textAlign='left';c.textBaseline='middle';c.fillStyle=ink;c.fillText(fit(c,text,w-96,36,29,700),74,h/2);if(on){c.fillStyle='#eccb94';rounded(c,w*.31,h-14,w*.38,4,2);c.fill();}}
    else{icon(c,iconType(item.id),56,h*.39,43,ink);
     if(/-(?:plus|minus)$/.test(item.id)){
      c.beginPath();c.arc(76,h*.24,17,0,Math.PI*2);
      c.fillStyle=disabled?'#334052':on?'#68513a':'#244c49';c.fill();
      c.strokeStyle=ink;c.lineWidth=2;c.stroke();
      c.beginPath();c.moveTo(68,h*.24);c.lineTo(84,h*.24);
      if(item.id.endsWith('-plus')){c.moveTo(76,h*.24-8);c.lineTo(76,h*.24+8);}c.stroke();
     }
     c.textAlign='left';c.textBaseline='middle';c.fillStyle=ink;c.fillText(fit(c,text,w-134,44,32,750),96,h*.38);
    c.fillStyle=disabled?'#748198':on?'#d9c8af':over?'#c6ded8':'#a9b6cc';c.fillText(fit(c,sub,w-52,27,22,500),26,h*.77);
    if(item.id==='accessory-material'){rounded(c,w-77,17,30,23,6);c.fillStyle=/^#[0-9a-f]{3,8}$/i.test(state.accessoryParams?.color||'')?state.accessoryParams.color:'#886044';c.fill();c.strokeStyle='#e6d1b2';c.lineWidth=1.5;c.stroke();}
    if(on){c.beginPath();c.arc(w-27,26,8,0,Math.PI*2);c.fillStyle='#f5d69e';c.fill();c.strokeStyle='#383044';c.lineWidth=2;pathCheck(c,w-31,26);}
   }
  },key);
 }
 function pathCheck(c,x,y){c.beginPath();c.moveTo(x,y);c.lineTo(x+3,y+3);c.lineTo(x+9,y-4);c.stroke();}
 function drawControllerGuide(){repaint(guide,(c,w,h)=>{rounded(c,0,0,w,h,24);c.fillStyle='#192234';c.fill();const rows=[['SELECT → GRAB','Trigger selects · Grip moves / turns'],['ADD / FINE','Left Trigger adds · + Grip: fine'],['TRANSFORM TOOLS','A: Move / Rotate / Scale'],['ALL TOOLS','Hold A · point · release'],['CREATE / COPY','X + A: Create · X + Trigger: Copy'],['PLACE A SHAPE','Choose shape · aim · Trigger places'],['RIGHT STICK','Grip: resize · otherwise orbit'],['FOCUS / PRECISION','Stick clicks: focus / Precision'],['UNDO / REDO','Y: Undo · X + Y: Redo'],['CANCEL / VIEW','B cancels · Left Grip moves view']];rows.forEach(([key,value],i)=>{const col=i%2,row=Math.floor(i/2),x=col*w/2+26,y=row*110+29;c.fillStyle=col?'#f0ce9c':'#a0ecd5';c.textAlign='left';c.textBaseline='middle';c.font='750 29px system-ui,sans-serif';c.fillText(key,x,y);c.fillStyle='#e7edf8';c.fillText(fit(c,value,w/2-48,29,24,550),x,y+42);if(row<4){c.fillStyle='rgba(176,190,215,.10)';c.fillRect(x,y+74,w/2-48,1);}});});}
 function manualDescription(id){
  const op=state.manualOperation||'inset',entry=window.SWYRL_MODEL_TEACHING?.get(op),amount=Number(state.manualAmount)||0;
  if(id==='manual-convert')return state.manualConvert?.available?'Plain primitive · regenerates UVs':clean(state.manualConvert?.reason||'Select a plain primitive',90);
  if(id==='manual-pick')return 'Trigger a flat face · preserve inner selection after Inset';
  if(id==='manual-learn')return 'Optional Before / During / After lesson';
  if(id==='manual-apply')return state.manualPreview?'Commit displayed mesh · one Undo step':'Preview an operation first';
  if(id==='manual-cancel')return 'Discard only the uncommitted preview';
  if(id==='manual-preview')return state.manualAvailability?.[op]?.available?'Review real geometry before applying':clean(state.manualAvailability?.[op]?.reason||'Choose eligible geometry',90);
  if(id==='manual-direction')return amount<0?'Inward · keep a floor':'Outward · extend the region';
  if(id.startsWith('manual-amount'))return op==='inset'?Math.round(amount*100)+'% inset':amount.toFixed(3)+' local units';
  if(id==='manual-mesh')return 'Convert · select flat region · shape it';
  const tool=window.SWYRL_MODEL_TEACHING?.get(id.slice(7));return clean(state.manualAvailability?.[id.slice(7)]?.reason||tool?.summary||entry?.summary||'Manual topology tool',90);
 }
 function wrapLesson(c,text,x,y,width,size=27,maxLines=2){
  c.font='550 '+size+'px system-ui,sans-serif';const words=String(text||'').split(' ');let line='',row=0;
  for(const word of words){if(line&&c.measureText(line+' '+word).width>width){c.fillText(line,x,y+row*size*1.3);line=word;if(++row>=maxLines)return;}else line+=(line?' ':'')+word;}
  if(row<maxLines)c.fillText(line,x,y+row*size*1.3);
 }
 function drawGuide(){
  const teaching=window.SWYRL_MODEL_TEACHING,tool=state.learningTool;
  if(!tool||!teaching){drawControllerGuide();return;}
  const entry=teaching.get(tool),frame=reducedMotion?0:Math.floor(elapsed*10);
  repaint(guide,(c,w,h)=>{
   rounded(c,0,0,w,h,24);c.fillStyle='#192234';c.fill();
   c.save();c.translate(12,64);teaching.drawDemo(c,tool,reducedMotion?.75:elapsed,w-24,245);c.restore();
   c.textAlign='left';c.textBaseline='middle';c.fillStyle='#b9ffe4';c.font='750 33px system-ui,sans-serif';c.fillText(entry.name,25,32);
   c.fillStyle='#e7edf8';wrapLesson(c,entry.summary,25,340,w-50,28,2);
   c.fillStyle='#f1d39d';wrapLesson(c,'Selection: '+entry.selection,25,420,w-50,25,1);
   c.fillStyle='#c4d2e4';wrapLesson(c,'Use: '+entry.use,25,465,w-50,25,2);
  },'lesson:'+tool+':'+frame);
 }

 drawGuide();
 function installPage(page){
  currentPage=page;buttons.clear();hoveredItem=null;pressedItem=null;pressedRemaining=0;transition=0;
  const helping=page==='guide';
  let entries=wheelKind?wheels[wheelKind]:helping?[['help','Back to menu'],['exit','Exit VR']]:pages[page]||pages.tools;
  if(page==='objects'&&!wheelKind&&!helping){
   const start=state.indexPage*9;
   entries=state.indexEntries.map((part,i)=>['index-part-'+(start+i),part.name||'Unnamed object']);
   while(entries.length<9)entries.push(['','']);
   entries.push(['index-add','Multi select'],['index-prev','Previous'],['index-next','Next']);
  }
  slots.forEach((item,index)=>{const pair=entries[index];item.id=pair?.[0]||'';item.label=pair?.[1]||'';item.mesh.userData.se340Action=item.id||null;item.mesh.visible=!!item.id;item.drawKey=null;item.lift=0;item.halo=0;item.home.set((index%3-1)*.202,.086-Math.floor(index/3)*.075,.016);
   if(helping)item.home.set(index===0?-.102:.102,-.193,.016);
   if(wheelKind){const angle=Math.PI/2-index*Math.PI*2/entries.length;item.home.set(Math.cos(angle)*(entries.length>7?.206:.194),Math.sin(angle)*(entries.length>7?.154:.147)-.012,.016);item.mesh.scale.set(entries.length>7?.74:.80,1.02,1);}else item.mesh.scale.set(1,1,1);
   item.mesh.position.copy(item.home);if(item.id)buttons.set(item.id,item);});
  for(const item of navSlots){item.mesh.visible=!wheelKind;item.drawKey=null;item.lift=0;item.halo=0;item.mesh.position.copy(item.home);}
  guide.mesh.visible=helping;wheelCenter.mesh.visible=!!wheelKind;
  rebuildTargets();
 }
 function rebuildTargets(){targets.splice(0,targets.length,plate.mesh);for(const item of allItems)if(item.id&&item.mesh.visible)targets.push(item.mesh);}
 function statusText(){
  if(wheelKind)return hoveredItem?'Release '+(wheelKind==='studio'?'X':'A')+' for '+label(hoveredItem)+' · '+description(hoveredItem):'Point at a card, then release '+(wheelKind==='studio'?'X':'A')+' to choose.';
  if(state.helpVisible&&state.learningTool)return 'Tool lesson · Guide returns to your work · geometry stays under your control.';
  if(state.manualActive)return hoveredItem?label(hoveredItem)+' · '+description(hoveredItem):state.manualPreview?'Real mesh preview · Apply commits; Cancel preserves source.':'Trigger selects a flat region · Inset then keep inner faces selected for Extrude.';
  if(state.helpVisible)return 'Default shortcuts shown · controller labels follow your active profile.';
  if(state.accessoryActive){if(hoveredItem&&(hoveredItem.id.startsWith('accessory-')||hoveredItem.id==='create-pouch'))return label(hoveredItem)+' · '+description(hoveredItem);return state.accessoryFit==='surface'?'Pouch surface fit · point at your model · Trigger places · B cancels':'Live pouch preview · adjust it, then point and Trigger to place';}
  if(accessoryPages.has(state.page))return hoveredItem?label(hoveredItem)+' · '+description(hoveredItem):'Start a pouch preview, then shape the body, details and fit.';
  if(state.creationActive||state.mode==='create')return 'Place '+(state.creationKind||'shape')+' · Trigger confirms · B cancels';
  if(state.dragging)return state.mode==='grab'?'Grab preview · release Grip to apply · B cancels':state.mode==='sculpt'?'Sculpt preview · release Trigger to apply · B cancels':state.mode==='lasso'?'Trace a surface region · release Trigger to save':state.mode==='draw'?'Trace an outline · release Trigger to make a face':state.mode==='two-hand'?'Two-hand preview · release a grip to apply':'Transform preview · release Grip to apply · B cancels';
  if(hoveredItem)return label(hoveredItem)+' · '+description(hoveredItem);
  return clean(state.message)||'Choose a tool to edit your model.';
 }
 function drawFooter(){const text=statusText();repaint(message,(c,w,h)=>{c.textAlign='left';c.textBaseline='middle';c.fillStyle=state.dragging?'#b1ffe5':hoveredItem?'#d0faec':'#d8e4f5';c.fillText(fit(c,text,w-28,36,28,600),14,h/2);},JSON.stringify([text,!!state.dragging,!!hoveredItem]));}
 function update(next={}){
  if(disposed)return;const incoming=typeof next==='string'?{message:next}:next||{};state={...state,...incoming};if(incoming.help!==undefined&&incoming.helpVisible===undefined)state.helpVisible=!!incoming.help;
  const page=pages[state.page]?state.page:'tools',pageKey=wheelKind?'wheel-'+wheelKind:state.helpVisible?'guide':page==='objects'?page+':'+state.indexPage+':'+state.indexEntries.map(e=>String(e.id)+'='+String(e.name)).join('|'):page;if(pageKey!==currentPage){installPage(pageKey.startsWith('objects:')?'objects':pageKey);currentPage=pageKey;}
  const key=JSON.stringify([state,wheelKind]);if(key===signature)return;signature=key;
  drawGuide();
  const helping=!!state.helpVisible&&!wheelKind,[title,kicker]=pageTitles[helping?'guide':page]||pageTitles.tools;
  selection.mesh.position.y=wheelKind?.205:.150;hint.mesh.visible=!helping;statusLine.visible=!helping;
  message.mesh.position.y=helping?-.272:wheelKind?-.238:-.221;hint.mesh.position.y=wheelKind?-.283:-.278;statusLine.position.y=wheelKind?-.207:-.187;
  repaint(header,(c,w,h)=>{icon(c,wheelKind?'grid':accessoryPages.has(page)?'pouch':'cube',35,54,42,'#a8edd9');c.textAlign='left';c.textBaseline='middle';c.fillStyle='#b4bfd6';c.font='700 21px system-ui,sans-serif';c.fillText('MODEL STUDIO',78,24);c.fillStyle='#f3f6ff';c.fillText(fit(c,wheelKind?(wheelKind==='brush'?'Choose a brush':wheelKind==='studio'?'Choose a studio':'Choose a tool'):helping&&state.learningTool?'Learn '+(window.SWYRL_MODEL_TEACHING?.get(state.learningTool)?.name||'modeling'):title,760,48,38,750),77,73);
   const label=trackingLabel();const pillW=286,pillX=w-pillW-3;rounded(c,pillX,30,pillW,55,27);c.fillStyle='#243c40';c.fill();c.beginPath();c.arc(pillX+23,57,5,0,Math.PI*2);c.fillStyle=state.tracking===false||state.tracking===0?'#f3d69b':'#9ef2d4';c.fill();c.fillStyle='#bcebdc';c.textAlign='left';c.fillText(fit(c,label,pillW-54,25,21,650),pillX+41,57);},JSON.stringify([title,kicker,helping,wheelKind,trackingLabel(),state.tracking]));
  const count=Math.max(Number(state.selectedCount)||0,state.selectedName?1:0),radius=Number(state.brushRadius),strength=Number(state.brushStrength);
  const context=page==='objects'?'OBJECTS '+state.indexTotal+' · PAGE '+(state.indexPage+1)+'/'+Math.max(1,Math.ceil(state.indexTotal/9))+' · '+count+' SELECTED':state.manualActive&&!helping&&!wheelKind?String(state.manualSelection?.faceCount||0)+' FACES · '+(window.SWYRL_MODEL_TEACHING?.get(state.manualOperation||'inset')?.name||'Manual modeling')+(state.manualPreview?' · PREVIEW ONLY':''):accessoryPages.has(page)&&!wheelKind&&!helping?accessoryContext():state.creationActive||state.mode==='create'?'PLACEMENT PREVIEW · '+String(state.creationKind||'shape').toUpperCase():wheelKind?'HOLD · POINT · RELEASE':helping?(state.learningTool?'BEFORE · DURING · AFTER':'CONTROLLERS WORK TOGETHER'):page==='sculpt'?String(state.sculptTool).toUpperCase()+' · Radius '+(Number.isFinite(radius)?radius.toFixed(2):'—')+' · Strength '+(Number.isFinite(strength)?Math.round(strength*100)+'%':'—')+(state.selectedRegionId?' · Mask on':''):page==='draw'?(state.mode==='lasso'?'LASSO':'OUTLINE')+' · '+(Number(state.drawPointCount)||0)+' points':page==='aim'?'POINTER ALIGNMENT · '+state.aimHand.toUpperCase()+' HAND':page==='views'?'DISPLAY · '+String(state.displayMode).toUpperCase():page==='cameras'?'ANGLE · '+String(state.viewMode).toUpperCase():count>0?count+' SELECTED · '+clean(state.selectedName,58):kicker;
  repaint(selection,(c,w,h)=>{c.fillStyle='#b9c8df';c.textAlign='left';c.textBaseline='middle';c.fillText(fit(c,context,w-20,31,25,650),10,h/2);},context);
  for(const item of allItems)if(item.mesh.visible)drawButton(item);
  repaint(wheelCenter,(c,w,h)=>{c.beginPath();c.arc(w/2,h/2,w*.46,0,Math.PI*2);c.fillStyle='#182b36';c.fill();c.strokeStyle='#5e9c94';c.lineWidth=2;c.stroke();icon(c,wheelKind==='brush'?'brush':wheelKind==='studio'?'cube':'grid',w/2,h*.40,70,'#a7f2da');c.fillStyle='#e1f6ee';c.textAlign='center';c.textBaseline='middle';c.font='700 29px system-ui,sans-serif';c.fillText('RELEASE '+(wheelKind==='studio'?'X':'A'),w/2,h*.72);},wheelKind);
  lineMaterial.color.setHex(accessoryPages.has(page)?0xd5b58b:0x89e6cd);
  drawFooter();const controller=page==='objects'&&!wheelKind?'Trigger: select · Multi ON: add/remove · Next / Previous: browse':wheelKind?'Release off a card to keep your tool · B cancels':helping?'Inspect changes the view · edit tools change the model':state.manualActive?'Trigger: flat region · Preview / Apply · B cancels':state.accessoryActive?'Trigger: place · B / Y: cancel · changes preview live':accessoryPages.has(page)?'Start preview · Body / Details / Fit · Trigger places':page==='sculpt'?'Trigger: sculpt · Left stick: radius / strength · Hold A: brushes':page==='draw'?'Trigger: trace · Grip: extrude · Hold X: studio':page==='aim'?'Adjust hand yaw / pitch to align the pointer':state.creationActive||state.mode==='create'?'Right stick: size · Trigger: place · B: cancel':page==='create'?'Choose shape · X + A: Create · X + Trigger: copy':state.mode==='grab'?'Grip: move / turn · Stick: size · Left Trigger: fine':(clean(state.controllerHint).length<=65?clean(state.controllerHint):'')||'Hold A: tools · Hold X: studio · Y: Undo · X+Y: Redo';
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
  elapsed+=dt;lastTickDelta=0;if(state.helpVisible&&state.learningTool)drawGuide();if(!lastVisible)reveal=0;
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
 return Object.freeze({root,targets,drawGuideIcon:(ctx,action,x,y,size,color)=>icon(ctx,iconType(action),x,y,size,color),highlightTutorialAction:action=>update({tutorialHighlight:action}),update,hover,press,hitTest,dispose,openWheel,closeWheel,releaseWheel,tick,
  inspect:()=>({width:WIDTH,height:HEIGHT,indexPage:state.indexPage,indexTotal:state.indexTotal,indexMulti:!!state.indexMulti,page:currentPage,wheel:wheelKind,wheelVisible:!!wheelKind,helpVisible:!!state.helpVisible&&!wheelKind,hovered:hoveredItem?.id||null,pressed:pressedItem?.id||null,selectedCount:state.selectedCount,brushRadius:state.brushRadius,brushStrength:state.brushStrength,sculptTool:state.sculptTool,creationActive:!!state.creationActive,creationKind:state.creationKind,accessoryActive:!!state.accessoryActive,accessoryParams:state.accessoryParams?{...state.accessoryParams}:null,accessoryFit:state.accessoryFit,accessoryTargetName:state.accessoryTargetName,accessoryDimensionLabels:state.accessoryDimensionLabels?{...state.accessoryDimensionLabels}:null,accessoryStyleName:state.accessoryStyleName,drawPointCount:state.drawPointCount,twoHand:!!state.twoHand,selectedRegionId:state.selectedRegionId,buttonCount:buttons.size,targetCount:targets.length,textureCount:textures.size,materialCount:materials.size,geometryCount:geometries.size,effectCount:allItems.length+1,paintCount,disposed,learningTool:state.learningTool||null,manualActive:!!state.manualActive,manualPreview:!!state.manualPreview,motion:{reveal,transition,active:activeMotion,visible:visibleState,reducedMotion,elapsed}})});
}
/* SE360_MODEL_VR_UI_END */
