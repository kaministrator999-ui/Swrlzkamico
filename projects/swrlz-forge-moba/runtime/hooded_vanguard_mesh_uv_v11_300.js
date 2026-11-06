// §E v11.300 · simultaneous character surface + UV reconstruction.
// Keeps the actual owner-generated concept artwork image from v11.298, but
// samples *material details*, not entire illustrated cutouts. The 17 editable
// native part identities are preserved, and all new geometry has authored UVs.
// Model geometry and each painted atlas were designed together.
const se300Families=Object.freeze({
 skin:{base:'#caa18d',rough:.9,metal:0},
 hair:{base:'#372821',rough:.78,metal:0},
 hood:{base:'#e3e0d9',rough:.9,metal:0},
 scarf:{base:'#e5e5e0',rough:.92,metal:0},
 uniform:{base:'#39434d',rough:.86,metal:.01},
 armor:{base:'#46545d',rough:.56,metal:.26},
 pauldron:{base:'#555b60',rough:.51,metal:.29},
 teal:{base:'#136f76',rough:.85,metal:0},
 leather:{base:'#51392c',rough:.85,metal:0},
 gloves:{base:'#e3e3dc',rough:.9,metal:0},
 boots:{base:'#40362f',rough:.82,metal:.03}
});
const se300Atlases=new Map(),se300MaterialTex=new Map();
const se300Status={requested:0,created:0,imageReady:false,imageError:null,
 rebuiltParts:0,rebuiltVertices:0,paintedFamilies:0,faceFrontOnly:true,
 materialSource:'existing owner-generated actual-image pixels'};
const se300Canvas=(w=384,h=384)=>{const c=document.createElement('canvas');c.width=w;c.height=h;return c;};
const se300Hex=(s)=>[1,3,5].map(i=>parseInt(s.slice(i,i+2),16));
let se300Image=null;
const se300ArtFields=Object.freeze({
 skin:[.23,.17,.55,.77],
 hair:[.12,.13,.59,.70],
 hood:[.18,.20,.48,.46],
 scarf:[.07,.10,.50,.52],
 uniform:[.13,.13,.28,.39],
 armor:[.17,.03,.67,.92],
 pauldron:[.05,.05,.78,.76],
 teal:[.13,.09,.53,.81],
 leather:[.10,.06,.57,.19],
 gloves:[.18,.11,.51,.75],
 boots:[.22,.04,.66,.91]
});
function se300DrawArtwork(img,name,canvas){
 const d=se300Families[name],ctx=canvas.getContext('2d',{willReadFrequently:true}),size=canvas.width;
 ctx.fillStyle=d.base;ctx.fillRect(0,0,size,size);
 // Real source pixels, not unrelated rectangles from the presentation sheet.
 const cell=se298AtlasLayout[name],r=se300ArtFields[name];
 if(!cell||!r)throw Error('Unknown art-family for native UV '+name);
 const sx=(cell[0]+r[0])*128,sy=(cell[1]+r[1])*128,
  sw=r[2]*128,sh=r[3]*128;
 if(name==='skin'){
  // Cylindrical face surface: front is u=.5; back is u=0 or 1.
  // Artwork appears ONLY over u=.29..71, world forehead -> jaw. Its alpha
  // is feathered, preventing a second face/ears across rear head geometry.
  const patch=se300Canvas(170,235),pc=patch.getContext('2d');
  pc.drawImage(img,sx,sy,sw,sh,0,0,170,235);
  const raw=pc.getImageData(0,0,170,235),pixels=raw.data;
  for(let y=0;y<235;y++)for(let x=0;x<170;x++){
   const i=(y*170+x)*4,fx=Math.min(x,169-x)/20,fy=Math.min(y,234-y)/26;
   pixels[i+3]=255*Math.max(0,Math.min(1,fx,fy));
  }
  pc.putImageData(raw,0,0);
  ctx.drawImage(patch,107,54,170,259);
  return;
 }
 // Isolate the paint from white concept-sheet paper. Each texture is created
 // on its own deliberate UV canvas; its local geometry uses corresponding
 // UV longitudinal and vertical orientation. Nothing wraps onto the backside
 // unintentionally: body back remains its separate uniform textile.
 const cut=se300Canvas(160,160),cc=cut.getContext('2d',{willReadFrequently:true});
 cc.drawImage(img,sx,sy,sw,sh,0,0,160,160);
 const bitmap=cc.getImageData(0,0,160,160),px=bitmap.data,base=se300Hex(d.base);
 const paleOK=['hood','scarf','gloves'].includes(name);
 for(let y=0;y<160;y++)for(let x=0;x<160;x++){
  const k=(y*160+x)*4,R=px[k],G=px[k+1],B=px[k+2];
  if(!paleOK&&R>218&&G>212&&B>201&&
    Math.max(R,G,B)-Math.min(R,G,B)<38){
   px[k]=base[0];px[k+1]=base[1];px[k+2]=base[2];
  }
 }
 cc.putImageData(bitmap,0,0);
 if(['hair','hood','scarf','uniform','teal','leather'].includes(name)){
  // Symmetric repetition for fabric samples, with source-pixel fold/shading.
  // No entire arm, boot, face or torso illustration is stretched over a leg.
  for(let row=0;row<2;row++)for(let col=0;col<2;col++){
   ctx.save();
   ctx.translate(col*192,row*192);
   if(col){ctx.translate(192,0);ctx.scale(-1,1);}
   if(row){ctx.translate(0,192);ctx.scale(1,-1);}
   ctx.drawImage(cut,0,0,192,192);ctx.restore();
  }
 }else{
  // Hero-object UV region: one matched illustration per shaped geometric part.
  ctx.drawImage(cut,35,8,314,366);
 }
 // A border in correct UV space follows the *constructed fabric edge*.
 // It is not extra 3D geometry or a random floating ornament.
 if(name==='hood'||name==='teal'){
  ctx.strokeStyle=name==='teal'?'rgba(208,179,107,.83)':'rgba(192,152,83,.78)';
  ctx.lineWidth=5;ctx.strokeRect(7,6,370,372);
 }
 if(name==='scarf'){
  ctx.strokeStyle='rgba(191,165,119,.43)';ctx.lineWidth=3;
  ctx.beginPath();ctx.moveTo(13,363);ctx.quadraticCurveTo(192,377,370,362);ctx.stroke();
 }
}
function se300InitArt(){
 if(se300Image)return;
 se300Status.requested++;
 const img=new Image();se300Image=img;
 img.onload=()=>{
  try{
   for(const name of Object.keys(se300Families)){
    const atlas=se300Canvas();
    se300DrawArtwork(img,name,atlas);
    se300Atlases.set(name,atlas);
    const tex=se300MaterialTex.get(name);
    if(tex){tex.image=atlas;tex.needsUpdate=true;}
   }
   se300Status.created=Object.keys(se300Families).length;
   se300Status.paintedFamilies=se300Atlases.size;
   se300Status.imageReady=true;se300Status.imageError=null;
  }catch(err){se300Status.imageError=String(err?.message||err);
   console.error('Vanguard UV-matched real art build failed',err);}
 };
 img.onerror=e=>{
  se300Status.imageError=String(e?.message||'Cannot read real-art reference image');
 };
 img.src=se298AtlasDataURL;
}
function se300Material(part){
 const family=part.heroPBR.tile.slice(5),def=se300Families[family];
 if(!def)throw Error('Unrecognized model-matched material '+family);
 let texture=se300MaterialTex.get(family);
 if(!texture){
  texture=new THREE.CanvasTexture(se300Canvas());
  const ctx=texture.image.getContext('2d');
  ctx.fillStyle=def.base;ctx.fillRect(0,0,384,384);
  texture.name='Hooded Vanguard / geometry-aligned actual art / '+family;
  texture.colorSpace=THREE.SRGBColorSpace;
  texture.wrapS=texture.wrapT=THREE.ClampToEdgeWrapping;
  texture.minFilter=THREE.LinearMipmapLinearFilter;
  texture.magFilter=THREE.LinearFilter;
  texture.anisotropy=2;texture.needsUpdate=true;
  se300MaterialTex.set(family,texture);
 }
 se300InitArt();
 return new THREE.MeshStandardMaterial({
  name:'Model+UV '+family,color:'#ffffff',map:texture,
  roughness:def.rough,metalness:def.metal,side:THREE.DoubleSide
 });
}
function se300Ribbon(rows,cols,fn,uvFn){
 const positions=[],uvs=[],indices=[],R=n=>+n.toFixed(6);
 for(let i=0;i<=rows;i++)for(let j=0;j<=cols;j++){
  const a=i/rows,b=j/cols,pt=fn(a,b),
   uv=uvFn?uvFn(a,b):[b,a];
  if(!pt.every(Number.isFinite)||!uv.every(Number.isFinite))
   throw Error('Non-finite mesh or UV in Vanguard');
  positions.push(...pt.map(R));uvs.push(...uv.map(R));
  if(i<rows&&j<cols){
   const q=i*(cols+1)+j,t=q+cols+1;
   indices.push(q,q+1,t,q+1,t+1,t);
  }
 }
 return {positions,uvs,indices};
}
function se300Join(items){
 const out={positions:[],uvs:[],indices:[]};
 for(const part of items){
  const offset=out.positions.length/3;
  out.positions.push(...part.positions);out.uvs.push(...part.uvs);
  for(const n of part.indices)out.indices.push(n+offset);
 }
 return out;
}
function se300BuildCharacter(scene){
 const model=scene?.project?.modelAtelier,parts=model?.parts;
 if(!Array.isArray(parts)||parts.length!==17||
    !parts.every(p=>p.id.startsWith('vanguard-rebuilt-')))
  throw Error('v11.300 requires the 17-part rebuilt Vanguard starter');
 const replace=(index,family,shape,title)=>{
  const p=parts[index];p.topologyMesh=shape;p.name=title;
  p.heroPBR={...p.heroPBR,tile:'v300:'+family,
   source:'owner-reference-art+topology-matched-UV',
   originalArtworkSha256:se298AtlasMetadata.jpegSha256,
   uvConstruction:'explicit-for-current-shape'};
 };
 // A continuous, naturally rounded head: cheek volume + jaw taper, restrained
 // nose relief and a real cheek-to-neck transition. No independent chin balls.
 replace(1,'skin',se300Ribbon(54,96,(u,v)=>{
  const angle=(v-.5)*Math.PI*2,lat=(u-.5)*Math.PI;
  const bell=Math.pow(Math.max(.006,Math.cos(lat)),.63),
   jaw=1-.14*Math.pow(Math.max(0,.35-u)/.35,1.35);
  const cheek=1+.055*Math.exp(-Math.pow((u-.57)/.18,2));
  const x=.255*bell*jaw*cheek*Math.sin(angle);
  const forehead=1+.022*Math.exp(-Math.pow((u-.74)/.19,2));
  const nose=.029*Math.exp(-Math.pow((u-.47)/.085,2)
   -Math.pow(angle/.15,2));
  const lip=.005*Math.exp(-Math.pow((u-.34)/.039,2)
   -Math.pow(angle/.18,2));
  return [x,3.81+.70*u,
   .055+.218*bell*forehead*Math.cos(angle)+nose+lip];
 }), 'Vanguard / face · continuous sculpt & front facial UV');
 // Crown hair tapers to the skull: broad top, small strands/undercut,
 // rather than the previous straight extrusion or plank-lock haircut.
 const cap=se300Ribbon(24,72,(u,v)=>{
  const theta=(v-.5)*2*Math.PI,ring=Math.sin(Math.PI*.52*u);
  return [.276*ring*Math.sin(theta),4.58-.335*u*u,
   .038+.255*ring*Math.cos(theta)];
 });
 replace(2,'hair',cap,'Vanguard / hair · close-fitting crown');
 const hair=[];
 for(const side of [-1,1])for(let n=0;n<3;n++){
  hair.push(se300Ribbon(26,7,(u,v)=>{
   const t=u,swirl=.045*Math.sin(u*Math.PI*(1.15+n*.12)),
    width=(.047+.01*(n===0))*Math.pow(1-u,.9);
   return [side*(.185+n*.027+swirl)+(v-.5)*width,
    4.43-t*(.35+.16*(n/2)),
    .213+.06*Math.sin(t*3+n*.7)-.027*t+.015*Math.sin(v*Math.PI)];
  }));
 }
 for(let n=0;n<3;n++){
  hair.push(se300Ribbon(16,8,(u,v)=>{
   const center=-.145+n*.14;
   return [center+(v-.5)*(.14-.07*u),
    4.51-u*(.13+.035*Math.abs(n-1)),
    .22+.028*Math.sin(v*Math.PI)-.045*u];
  }));
 }
 replace(3,'hair',se300Join(hair),'Vanguard / hair · sculpted face locks & layered fringe');
 // Tailored hood: domed upper canopy, back/side mantle, curved brow/edge
 // binding and downturned edges. No solid Boba helmet/front face cover.
 const dome=se300Ribbon(25,84,(u,v)=>{
  const a=(v-.5)*Math.PI*2;
  const radius=.37*Math.sin(u*Math.PI/2),
   front=Math.pow(Math.max(0,Math.cos(a)),8);
  return [radius*Math.sin(a),4.65-.35*u*u+.13*front*u*u,
   -.054+.29*radius/.37*Math.cos(a)];
 },(u,v)=>[.15+.7*v,.10+.7*u]);
 const back=se300Ribbon(30,68,(u,v)=>{
  const a=.92+v*(2*Math.PI-1.84);
  const r=.374+.02*Math.sin(u*Math.PI);
  return [r*Math.sin(a),3.77+.68*u,
   -.079+.293*Math.cos(a)+.024*Math.sin(u*Math.PI*2)];
 },(u,v)=>[.11+.78*v,.19+.69*u]);
 const brow=se300Ribbon(6,48,(u,v)=>{
  const x=(v-.5)*.61,arch=Math.sin(Math.PI*v);
  return [x,4.42+.14*arch-.03*u,.239+.025*arch+.01*u];
 },(u,v)=>[.01+.07*u,.12+.75*v]);
 const border=[];
 for(const s of [-1,1])border.push(se300Ribbon(25,4,(u,v)=>{
  const x=s*(.296+.015*Math.sin(Math.PI*u));
  return [x,3.93+.58*u,.21-.015*u+.008*v];
 },(u,v)=>[.01+.07*v,.13+.7*u]));
 replace(4,'hood',se300Join([dome,back,brow,...border]),
  'Vanguard / hood · sculpted wrap, crown and face framing');
 // Scarf geometry follows neck/chest. One gathered neck cowl and draped
 // V-shaped shawl; all the fabric folds appear in its mapped cloth art.
 const cowl=se300Ribbon(24,60,(u,v)=>{
  const a=(v-.5)*Math.PI*2;
  const radius=.192+.046*Math.sin(Math.PI*u);
  return [radius*Math.sin(a),3.58+.28*u,
   .055+(.166+.025*Math.sin(Math.PI*u))*Math.cos(a)+.01*Math.sin(a*3+u*9)];
 });
 replace(5,'scarf',cowl,'Vanguard / scarf · sculpted neck cowl');
 const shawl=se300Ribbon(36,54,(u,v)=>{
  const width=.442-.299*Math.pow(u,.8);
  const x=(2*v-1)*width;
  const point=(1-Math.pow(Math.abs(2*v-1),.7));
  const y=3.66-.44*u-.17*u*point;
  const z=.254+.046*Math.sin(Math.PI*v)+.022*Math.sin(3*Math.PI*u+4*v);
  return [x,y,z];
 });
 replace(6,'scarf',shawl,'Vanguard / scarf · tapered draped chest mantle');
 // Breastplate has sculpted shoulders, narrowed waist, and a breast curve;
 // the armor UV fits its actual silhouette instead of a cardboard rectangle.
 const plate=se300Ribbon(40,60,(u,v)=>{
  const w=.315+.095*Math.sin(Math.PI*u*.88)+.048*u;
  const x=(v-.5)*2*w,hip=2.48+.99*u;
  const middle=Math.max(0,1-Math.pow((v-.5)*2,2));
  const arched=.038*Math.sin(Math.PI*u);
  return [x,hip-.05*Math.pow(Math.abs(v-.5)*2,1.8),
   .207+.072*middle+arched*middle-.016*u];
 });
 replace(7,'armor',plate,'Vanguard / armor · shaped tapered breastplate');
 // Paudrons curve over shoulder volume with layered shoulder height; native
 // part continues to be independently editable and mapped.
 for(let k=8;k<=9;k++){
  const side=k===8?-1:1;
  replace(k,'pauldron',se300Ribbon(30,36,(u,v)=>{
   const a=v*Math.PI*.91;
   const shoulderX=side*(.37+.33*u);
   const width=.145*Math.sin(Math.PI*u);
   return [shoulderX+side*.018*Math.sin(2*Math.PI*v),
     3.54-.21*u+.11*Math.cos(a)-.03*Math.sin(3*Math.PI*u),
     -.07+.198*Math.sin(a)+width*(v-.5)];
  }), 'Vanguard / armor · '+(side<0?'left':'right')+' curved shoulder pauldron');
 }
 // Two overlapping coattail panels from hip to ankle, with widening fabric
 // cross-sections, actual drape, seam and inner/back surface. No spear leaves.
 for(let k=10;k<=11;k++){
  const side=k===10?-1:1;
  const outer=se300Ribbon(54,30,(u,v)=>{
   const wide=.23+.14*Math.sin(.82*Math.PI*u)+.12*u;
   const x=side*(.34+.12*u+.037*Math.sin(2*Math.PI*u))+
    (v-.5)*wide;
   const y=2.52-2.31*u+.065*u*v,
    z=-.14-.10*u-.035*Math.sin(2*Math.PI*u)+
     .052*Math.sin(2*Math.PI*v+2*u);
   return [x,y,z];
  });
  const inner=se300Ribbon(54,30,(u,v)=>{
   const wide=.23+.14*Math.sin(.82*Math.PI*u)+.12*u;
   const x=side*(.34+.12*u+.037*Math.sin(2*Math.PI*u))+
    (v-.5)*wide;
   return [x,2.52-2.31*u+.065*u*v,
    -.161-.10*u-.035*Math.sin(2*Math.PI*u)+
    .052*Math.sin(2*Math.PI*v+2*u)];
  },(u,v)=>[.12+.7*v,.10+.7*u]);
  replace(k,'teal',se300Join([outer,inner]),
   'Vanguard / coat · '+(side<0?'left':'right')+' draped outer & inner cloth');
 }
 // Keep existing belt, five-digit sculpted hands and shaped boots, but supply
 // clean texture UVs with detail from the corresponding actual illustrated art.
 for(const i of [0,12,13,14,15,16]){
  const part=parts[i],family=part.heroPBR?.tile?.slice(5);
  if(!se300Families[family])throw Error('Unknown retained anatomy family '+part.name);
  replace(i,family,part.topologyMesh,part.name);
 }
 // Explicit verification: each edited shape belongs to an atlas built from
 // the same concept artwork and not from an arbitrary transformed picture.
 let verts=0;
 for(const p of parts){
  const g=p.topologyMesh,uv=g.uvs;
  if(!g.positions.length||g.positions.length/3*2!==uv.length||
     g.indices.length%3||g.indices.some(n=>n<0||n>=g.positions.length/3)||
     uv.some(n=>!Number.isFinite(n)||n<-.00001||n>1.00001))
   throw Error('New geometry and UV mismatch: '+p.name);
  verts+=g.positions.length/3;
 }
 model.name='Hooded Vanguard · Geometry + UV Rebuild';
 model.reference='v11.300 refits head, sculpted hood, layered hair, neck/chest scarf, tapered armor and curved shoulders, two real cloth coat tails plus existing detailed hands/boots. All 17 editable parts have explicit shape-matched UVs and source-image-derived material art. Kept original generated concept art source SHA. No bird, weapon or full rig.';
 scene.project.name=model.name;
 scene.engine='§wyrl§ Engine · Maker v11.300';scene.version=11.300;
 se300Status.rebuiltParts=17;se300Status.rebuiltVertices=verts;
 return scene;
}
const se300PriorMaterial=se291HeroMaterial;
se291HeroMaterial=function(part){
 if(!part?.heroPBR?.tile?.startsWith('v300:'))return se300PriorMaterial(part);
 return se300Material(part);
};
const se300PriorScene=se291HeroScene;
se291HeroScene=function(){return se300BuildCharacter(se300PriorScene());};
window.SWYRL_ENGINE_HOODED_VANGUARD=Object.freeze({
 id:'hooded-vanguard',open:se291OpenHero,createScene:se291HeroScene,
 status:()=>({...se291Stats,...se300Status,version:'v11.300',
  sourceImageSha256:se298AtlasMetadata.jpegSha256,
  textureResolution:384,editableParts:17,
  geometryAndUVRebuiltTogether:true,weapon:false,bird:false,rigged:false})
});
