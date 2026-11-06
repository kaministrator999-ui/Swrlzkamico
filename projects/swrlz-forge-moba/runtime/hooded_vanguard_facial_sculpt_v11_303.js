// §E v11.303 · character-portrait anatomy on REAL vertex geometry, with
// a matched high-resolution native UV face painting. Do not add floating face
// stickers, polygons for eyes, or image-sheet cutouts. Other 16 part IDs and
// armour / coat / neutral hand pose are untouched.
const se303FaceStats={version:'v11.303',faceAtlasPixels:768,
 faceVertexCount:0,faceTriangles:0,facialSculpt:true,
 contourPainted:true,paintedAtlasReady:false,
 unchangedArmorAndHands:true,ownerAccepted:false};
const se303Smooth=(v)=>{v=Math.max(0,Math.min(1,v));return v*v*(3-2*v);};
const se303Gauss=(x,c,w)=>Math.exp(-Math.pow((x-c)/w,2));
const se303Twin=(angle,at,w)=>se303Gauss(angle,at,w)+se303Gauss(angle,-at,w);
function se303HeadSurface(t,v){
 // Latitude t=0 at jaw/chin, 1 at scalp. Longitude v=.5 faces camera,
 // v=0/1 is back seam. This is also the UV schema for the actual skin map.
 const angle=(v-.5)*Math.PI*2,lat=(t-.5)*Math.PI;
 const circ=Math.pow(Math.max(.004,Math.cos(lat)),.65);
 const jaw=1-.115*Math.pow(Math.max(0,.36-t)/.36,1.2);
 const cheek=1+.055*se303Gauss(t,.535,.115)*se303Twin(angle,.52,.24);
 const temple=1+.026*se303Gauss(t,.72,.19);
 const x=.267*circ*jaw*cheek*temple*Math.sin(angle);
 const forehead=1+.018*se303Gauss(t,.75,.15);
 const faceDirection=Math.max(0,Math.cos(angle));
 let z=.045+.219*circ*forehead*Math.cos(angle);
 // Sculpture on the actual head topology: brows, sockets, eyelid rims,
 // cheekbones, nasal bridge/alar wings and three-dimensional lips.
 // The separate UV artwork below matches each of these landmarks.
 const brow=.011*se303Gauss(t,.66,.042)*se303Twin(angle,.36,.21);
 const orbit=-.012*se303Gauss(t,.58,.065)*se303Twin(angle,.36,.22);
 const upperLid=.007*se303Gauss(t,.609,.018)*se303Twin(angle,.36,.21);
 const lowerLid=.005*se303Gauss(t,.548,.021)*se303Twin(angle,.36,.21);
 const cheekbone=.016*se303Gauss(t,.495,.07)*se303Twin(angle,.59,.26);
 const noseBridge=.026*se303Gauss(t,.49,.18)*se303Gauss(angle,0,.19);
 const noseTip=.057*se303Gauss(t,.421,.048)*se303Gauss(angle,0,.16);
 const noseWings=.016*se303Gauss(t,.410,.034)*se303Twin(angle,.16,.075);
 const philtrum=.006*se303Gauss(t,.344,.031)*se303Gauss(angle,0,.09);
 const upperLip=.010*se303Gauss(t,.305,.021)*se303Gauss(angle,0,.265);
 const lowerLip=.010*se303Gauss(t,.277,.022)*se303Gauss(angle,0,.264);
 const chin=.010*se303Gauss(t,.195,.055)*se303Gauss(angle,0,.42);
 z+=faceDirection*(brow+orbit+upperLid+lowerLid+cheekbone+
    noseBridge+noseTip+noseWings+philtrum+upperLip+lowerLip+chin);
 const y=3.815+.715*t;
 return [x,y,z];
}
function se303DrawPortrait(canvas){
 const ctx=canvas.getContext('2d');
 if(!ctx)throw Error('No portrait canvas 2D context');
 const s=canvas.width/384;
 ctx.save();ctx.scale(s,s);
 const grad=ctx.createLinearGradient(0,0,384,384);
 for(const [at,col] of [[0,'#eac5af'],[.25,'#dcb59e'],[.56,'#dfb39d'],[.82,'#c79a84'],[1,'#ac7c6c']])
  grad.addColorStop(at,col);
 ctx.fillStyle=grad;ctx.fillRect(0,0,384,384);
 function glow(x,y,rad,inner,outer='rgba(0,0,0,0)'){
  const g=ctx.createRadialGradient(x,y,0,x,y,rad);
  g.addColorStop(0,inner);g.addColorStop(1,outer);
  ctx.fillStyle=g;ctx.fillRect(x-rad,y-rad,rad*2,rad*2);
 }
 function curve(a,c1,c2,b,color,w=1.8){
  ctx.beginPath();ctx.moveTo(...a);ctx.bezierCurveTo(...c1,...c2,...b);
  ctx.strokeStyle=color;ctx.lineWidth=w;ctx.lineCap='round';ctx.stroke();
 }
 function ellipse(x,y,rx,ry,color,stroke=null,width=1){
  ctx.beginPath();ctx.ellipse(x,y,rx,ry,0,0,Math.PI*2);
  ctx.fillStyle=color;ctx.fill();
  if(stroke){ctx.lineWidth=width;ctx.strokeStyle=stroke;ctx.stroke();}
 }
 // Broad warm and cool half-tones reproduce sculpted cheek/jaw/forehead
 // without stamping a photographed face into the model.
 glow(192,115,75,'rgba(255,241,224,.24)');
 glow(162,216,43,'rgba(171,91,84,.20)');
 glow(222,216,43,'rgba(171,91,84,.20)');
 glow(192,257,50,'rgba(126,78,69,.08)');
 glow(192,206,42,'rgba(251,218,190,.10)');
 for(const side of [-1,1]){
  const eyeX=192+side*23;
  const templeX=192+side*47;
  glow(eyeX,151,29,'rgba(102,68,66,.20)');
  glow(eyeX,182,24,'rgba(220,166,142,.34)');
  glow(templeX,185,23,'rgba(175,107,94,.10)');
  // Brow builds from several natural hairs; upper eyelid darker and
  // visibly overlaps the iris while the lower eyelid catches highlights.
  const left=eyeX-17,right=eyeX+17;
  curve([left,141],[eyeX-7,134],[eyeX+8,136],[right,143],'#563c34',3.6);
  curve([left+2,144],[eyeX-4,137],[eyeX+7,139],[right-2,144],
    'rgba(151,105,84,.65)',1.2);
  curve([left-1,161],[eyeX-8,151],[eyeX+9,151],[right,162],
    '#65463f',2.5);
  // The painted sclera and iris share the physical socket location
  // (t approx .58, side longitude approx +/- .36 radians).
  const white=ctx.createLinearGradient(0,156,0,174);
  white.addColorStop(0,'#c7b7aa');white.addColorStop(.35,'#faf0e7');
  white.addColorStop(1,'#ded0c4');
  ellipse(eyeX,166,12.3,6.35,white,'#9b766c',.8);
  ellipse(eyeX,166,6,6.1,'#394f58');
  ellipse(eyeX,166,4.8,5.8,'#749da9');
  ellipse(eyeX,166.7,3.7,4.2,'#3f677a');
  ellipse(eyeX,166.7,2.45,4.1,'#24333d');
  ellipse(eyeX-1.8,163.4,1.8,1.9,'#fff8ea');
  ellipse(eyeX+1.9,169.6,.85,.9,'rgba(240,247,249,.78)');
  curve([left,160],[eyeX-6,156],[eyeX+8,155],[right,161],
    '#49342f',2.4);
  curve([left+2,175],[eyeX-5,179],[eyeX+8,178],[right-1,174],
    'rgba(129,80,76,.55)',1.35);
  curve([left+4,185],[eyeX-8,189],[eyeX+7,188],[right-5,184],
    'rgba(255,227,207,.28)',2);
  for(let i=-1;i<=1;i++){
   const x=eyeX+i*4;
   curve([x,161],[x-1,158],[x-1,155],[x-1,154],
    'rgba(79,52,47,.40)',.65);
  }
  // Cheek mass and nasolabial shading, not a painted cartoon circle.
  glow(eyeX+side*5,209,21,'rgba(197,115,105,.15)');
  curve([192+side*17,217],[192+side*19,229],
    [192+side*15,237],[192+side*10,244],
    'rgba(134,81,77,.12)',1.3);
 }
 // Real nasal structure is mostly topology; the color map follows it.
 glow(192,198,24,'rgba(255,230,209,.25)');
 curve([189,191],[186,203],[188,215],[186,222],
  'rgba(141,83,75,.39)',1.6);
 curve([196,191],[198,204],[196,217],[200,223],
  'rgba(109,66,66,.28)',1.35);
 glow(192,220,13,'rgba(255,215,191,.32)');
 curve([183,222],[185,225],[189,226],[190,224],
  'rgba(108,64,64,.62)',1.3);
 curve([195,224],[198,226],[201,225],[203,222],
  'rgba(108,64,64,.58)',1.3);
 ellipse(186,224,2.5,1.15,'rgba(94,57,58,.50)');
 ellipse(199,224,2.5,1.15,'rgba(94,57,58,.50)');
 curve([191,227],[191,234],[192,237],[192,239],
  'rgba(133,81,78,.19)',1.3);
 // Distinct upper/lower lip volumes and corners; muted, not a drawn slash.
 glow(192,262,26,'rgba(167,89,85,.15)');
 curve([175,260],[180,256],[185,256],[191,259],
  '#965e5d',1.65);
 curve([191,259],[198,255],[203,256],[209,260],
  '#965e5d',1.65);
 curve([176,261],[187,265],[201,265],[209,260],
  '#875858',1.5);
 curve([178,264],[187,268],[200,267],[207,263],
  'rgba(210,129,119,.80)',2.2);
 curve([179,270],[190,274],[203,272],[207,269],
  'rgba(126,77,71,.22)',1.2);
 glow(192,289,35,'rgba(248,219,192,.16)');
 ctx.restore();
}
const se303EarlierPaint=se300DrawArtwork;
se300DrawArtwork=function(reference,family,canvas){
 if(family==='skin'){se303DrawPortrait(canvas);return;}
 return se303EarlierPaint(reference,family,canvas);
};
// The character scene creates 11 material families lazily. Override only
// skin with its sharp 768px atlas, leaving armor/shoulder maps cached and
// unchanged. A new starter creates its own geometry, not a saved-model edit.
const se303EarlierInit=se300InitArt;
let se303SkinAtlas=null;
se300InitArt=function(){
 se303EarlierInit();
 if(!se303SkinAtlas){
  se303SkinAtlas=se300Canvas(768,768);
  se303DrawPortrait(se303SkinAtlas);
  se300Atlases.set('skin',se303SkinAtlas);
  se303FaceStats.paintedAtlasReady=true;
 }
 const skin=se300MaterialTex.get('skin');
 if(skin&&skin.image!==se303SkinAtlas){
  skin.image=se303SkinAtlas;
  skin.needsUpdate=true;
 }
};
const se303PreviousScene=se291HeroScene;
se291HeroScene=function(){
 const scene=se303PreviousScene(),model=scene?.project?.modelAtelier;
 const parts=model?.parts;
 if(!parts||parts.length!==17||!parts[1].id.startsWith('vanguard-rebuilt-'))
  throw Error('Vanguard facial study requires original 17 editable parts');
 const face=se300Ribbon(80,144,se303HeadSurface);
 parts[1].topologyMesh=face;
 parts[1].name='Vanguard / face · sculpted orbit, nose, cheekbones and lips';
 parts[1].heroPBR={...parts[1].heroPBR,frontLongitude:.5,
  uvEyes:[.44,.56],uvNose:.5,atlasResolution:768,
  anatomicalLandmarks:true,paintLayer:'high-res portrait paired with sculpt'};
 // Stop bowl fringe covering the forehead: sculpt the scalp crown around the
 // face and give the lower hairline a shallow irregular sweep.
 const cap=se300Ribbon(28,80,(u,v)=>{
  const a=(v-.5)*Math.PI*2,
   r=.273*Math.sin(.5*Math.PI*u),
   front=Math.max(0,Math.cos(a));
  const hairline=4.575-(.275-.075*front+.017*Math.cos(a*3))*u*u;
  return [r*Math.sin(a),hairline,.040+.246*Math.sin(.5*Math.PI*u)*Math.cos(a)];
 });
 parts[2].topologyMesh=cap;
 parts[2].name='Vanguard / hair · contoured upper hairline and scalp';
 const strands=[];
 for(const side of [-1,1]){
  for(let n=0;n<3;n++){
   strands.push(se300Ribbon(27,6,(t,v)=>{
    const inset=n*.038,curve=.019*Math.sin(t*Math.PI*1.25);
    const width=(.044-n*.005)*(1-.80*t);
    return [
     side*(.203+inset+curve)+(v-.5)*width,
     4.38-t*(.35+n*.064),
     .207+.022*Math.sin(t*4+n)-.012*t+.018*Math.sin(Math.PI*v)];
   }));
  }
 }
 for(let n=-2;n<=2;n++){
  strands.push(se300Ribbon(19,7,(u,v)=>{
   const center=n*.075,shift=-.020*u+.012*Math.sin(3*u+n);
   const width=.081*(1-u*.80);
   return [
    center+shift+(v-.5)*width,
    4.458-u*(.135+.017*(2-Math.abs(n))),
    .243+.017*Math.sin(Math.PI*v)-.018*u];
  }));
 }
 parts[3].topologyMesh=se300Join(strands);
 parts[3].name='Vanguard / hair · separated side locks and eyebrow-clear fringe';
 for(const i of [1,2,3]){
  const g=parts[i].topologyMesh;
  if(g.positions.length/3*2!==g.uvs.length||
     g.uvs.some(n=>n<0||n>1||!Number.isFinite(n))||
     g.indices.some(n=>n>=g.positions.length/3||n<0))
   throw Error('Bad sculpt/UV pairing '+parts[i].name);
 }
 se303FaceStats.faceVertexCount=face.positions.length/3;
 se303FaceStats.faceTriangles=face.indices.length/3;
 model.name='Hooded Vanguard · Anatomical Face Study';
 model.reference='v11.303 high-definition head: real eye sockets, eyelid rims, cheekbones, nose bridge/tip/alar wings, three-dimensional lips and chin; aligned 768px portrait with iris detail, skin tones and lips. Correct hairline, shorter brow-clear fringe. Preserves all chest/shoulders/scarf/coat/neutral wrists, all 17 editable parts, no bird/weapon/full rig.';
 scene.project.name=model.name;scene.engine='§wyrl§ Engine · Maker v11.303';
 scene.version=11.303;
 return scene;
};
window.SWYRL_ENGINE_HOODED_VANGUARD=Object.freeze({
 id:'hooded-vanguard',open:se291OpenHero,createScene:se291HeroScene,
 status:()=>({...se291Stats,...se300Status,...se301Result,...se302SurfaceStatus,
  ...se303FaceStats,correctedHandAlignment:true,nativeUVPBRMaps:true,
  editableParts:17,rigged:false,weapon:false,bird:false})
});
