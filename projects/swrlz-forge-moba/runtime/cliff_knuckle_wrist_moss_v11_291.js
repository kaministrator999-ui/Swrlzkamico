// §E v11.291 — stone knuckles drawn into the PBR maps, moss at wrist ONLY.
// One connected native Cliff Hand mesh, unchanged bones/geometry and no 3D add-ons.
const se291Maps=new Map();
const se291State={requests:0,ready:false,failures:0,loadError:null,
 mossRegion:'bottom 23% of gauntlet UV; smooth fade',knuckleMarks:4};
const se291Knuckles=Object.freeze([
 {u:.454,v:.648,rx:25,ry:19,twist:-.15},
 {u:.592,v:.654,rx:24,ry:21,twist:.08},
 {u:.738,v:.644,rx:23,ry:20,twist:-.09},
 {u:.868,v:.625,rx:18,ry:17,twist:.13}
]);
function se291CanvasTexture(kind){
 if(se291Maps.has(kind))return se291Maps.get(kind).tex;
 const canvas=document.createElement('canvas');
 canvas.width=384;canvas.height=384;
 const ctx=canvas.getContext('2d',{willReadFrequently:true});
 if(!ctx)throw Error('Model Atelier cannot allocate mapped cliff material canvas');
 ctx.fillStyle=kind==='color'?'#ba805a':kind==='normal'?'rgb(128,128,255)':
   kind==='ao'?'#eeeeee':'#dddddd';
 ctx.fillRect(0,0,384,384);
 const tex=new THREE.CanvasTexture(canvas);
 tex.colorSpace=kind==='color'?THREE.SRGBColorSpace:THREE.NoColorSpace;
 tex.wrapS=tex.wrapT=THREE.ClampToEdgeWrapping;
 tex.minFilter=THREE.LinearMipmapLinearFilter;
 tex.magFilter=THREE.LinearFilter;
 tex.anisotropy=2;
 se291Maps.set(kind,{tex,ctx});
 return tex;
}
function se291DrawKnuckleColor(ctx){
 // UV coordinates are authored from the actual hand's finger-root placement.
 // Draw stone knuckle planes and edge shadows into COLOR; no rock meshes.
 for(let i=0;i<se291Knuckles.length;i++){
  const k=se291Knuckles[i],x=k.u*384,y=(1-k.v)*384;
  ctx.save();ctx.translate(x,y);ctx.rotate(k.twist);
  const shadow=ctx.createRadialGradient(3,6,3,0,0,k.rx*1.18);
  shadow.addColorStop(0,'rgba(83,49,32,.26)');
  shadow.addColorStop(1,'rgba(83,49,32,0)');
  ctx.fillStyle=shadow;ctx.beginPath();ctx.ellipse(0,2,k.rx*1.23,k.ry*1.32,0,0,Math.PI*2);ctx.fill();
  const points=[[-.92,-.25],[-.66,-.84],[-.16,-1.03],[.48,-.78],
    [.95,-.29],[.85,.53],[.23,.94],[-.58,.73],[-1,.19]];
  ctx.beginPath();
  points.forEach(([a,b],j)=>j?ctx.lineTo(a*k.rx,b*k.ry):ctx.moveTo(a*k.rx,b*k.ry));
  ctx.closePath();
  const rock=ctx.createLinearGradient(-k.rx,-k.ry,k.rx,k.ry);
  rock.addColorStop(0,'rgba(255,218,155,.33)');
  rock.addColorStop(.53,'rgba(198,127,79,.14)');
  rock.addColorStop(1,'rgba(77,49,32,.36)');
  ctx.fillStyle=rock;ctx.fill();
  ctx.lineWidth=1.65;
  ctx.strokeStyle='rgba(69,43,30,.55)';
  ctx.stroke();
  ctx.beginPath();ctx.moveTo(-k.rx*.72,-k.ry*.31);
  ctx.lineTo(-k.rx*.44,-k.ry*.69);ctx.lineTo(k.rx*.08,-k.ry*.87);
  ctx.strokeStyle='rgba(255,222,169,.46)';ctx.lineWidth=1.45;ctx.stroke();
  // Short shallow mineral fault: part of the albedo, not 3D tubes.
  ctx.beginPath();ctx.moveTo(-k.rx*.25,k.ry*.49);
  ctx.lineTo(k.rx*.19,k.ry*.28);ctx.lineTo(k.rx*.52,k.ry*.52);
  ctx.strokeStyle='rgba(75,49,39,.38)';ctx.lineWidth=1.15;ctx.stroke();
  ctx.restore();
 }
}
function se291DrawKnuckleRelief(ctx,kind){
 // Match the exact same four UV locations in normal and AO maps.
 // Pixel shading simulates beveled stone heads on a perfectly smooth mesh.
 const data=ctx.getImageData(0,0,384,384),a=data.data;
 for(const k of se291Knuckles){
  const cx=k.u*384,cy=(1-k.v)*384;
  const minX=Math.max(0,Math.floor(cx-k.rx*1.35)),maxX=Math.min(383,Math.ceil(cx+k.rx*1.35));
  const minY=Math.max(0,Math.floor(cy-k.ry*1.38)),maxY=Math.min(383,Math.ceil(cy+k.ry*1.38));
  for(let y=minY;y<=maxY;y++)for(let x=minX;x<=maxX;x++){
   const dx=(x-cx)/k.rx,dy=(y-cy)/k.ry,d=Math.hypot(dx,dy);
   if(d>1.18)continue;
   const p=(y*384+x)*4;
   if(kind==='normal'&&d<1){
    const fall=(1-d*d)**1.2;
    const weight=.78*fall;
    const targetR=Math.max(16,Math.min(240,128+85*dx));
    const targetG=Math.max(16,Math.min(240,128-84*dy));
    a[p]=Math.round(a[p]*(1-weight)+targetR*weight);
    a[p+1]=Math.round(a[p+1]*(1-weight)+targetG*weight);
    a[p+2]=Math.round(a[p+2]*(1-weight)+245*weight);
   }else if(kind==='ao'){
    const edge=Math.exp(-(((d-.91)/.16)**2));
    const under=Math.max(0,dy)*Math.max(0,1-d);
    const dark=76*edge+23*under;
    a[p]=Math.max(0,a[p]-dark);
    a[p+1]=Math.max(0,a[p+1]-dark);
    a[p+2]=Math.max(0,a[p+2]-dark);
   }
  }
 }
 ctx.putImageData(data,0,0);
}
function se291PaintAtlas(img){
 const at=(type)=>se291Maps.get(type);
 const src={color:[0,384],normal:[384,0],roughness:[768,0],ao:[1152,0]};
 for(const [type,[x,y]] of Object.entries(src)){
  const ctx=at(type).ctx;
  ctx.clearRect(0,0,384,384);
  ctx.drawImage(img,x,y,384,384,0,0,384,384);
 }
 const albedo=at('color').ctx;
 // The upper palm, knuckles, fingers and thumb use CLEAN base sandstone.
 // Composite the source moss only at distal wrist, never everywhere.
 const moss=document.createElement('canvas');moss.width=moss.height=384;
 const mctx=moss.getContext('2d');
 mctx.drawImage(img,0,0,384,384,0,0,384,384);
 mctx.globalCompositeOperation='destination-in';
 const fade=mctx.createLinearGradient(0,275,0,384);
 fade.addColorStop(0,'rgba(0,0,0,0)');
 fade.addColorStop(.30,'rgba(0,0,0,.07)');
 fade.addColorStop(.68,'rgba(0,0,0,.60)');
 fade.addColorStop(1,'rgba(0,0,0,.80)');
 mctx.fillStyle=fade;mctx.fillRect(0,0,384,384);
 mctx.globalCompositeOperation='source-over';
 albedo.drawImage(moss,0,0);
 se291DrawKnuckleColor(albedo);
 for(const type of ['normal','ao'])se291DrawKnuckleRelief(at(type).ctx,type);
 for(const {tex} of se291Maps.values())tex.needsUpdate=true;
 se291State.ready=true;se291State.loadError=null;
}
function se291TextureSet(){
 if(!se291Maps.size){
  for(const kind of ['color','normal','roughness','ao'])se291CanvasTexture(kind);
  se291State.requests++;
  const image=new Image();
  image.onload=()=>{try{se291PaintAtlas(image)}catch(error){
    se291State.failures++;se291State.loadError=String(error?.message||error);
    console.warn('Cliff knuckle texture composition',error);
  }};
  image.onerror=()=>{se291State.failures++;se291State.loadError='Atlas image could not load';
    console.warn('Cliff Hand rock atlas not available');};
  image.src=SE288_ATLAS;
 }
 return Object.fromEntries([...se291Maps].map(([name,value])=>[name,value.tex]));
}
function se291WristMossKnuckleMaterial(part){
 const t=se291TextureSet();
 const mat=new THREE.MeshStandardMaterial({
  color:'#fff2e6',
  map:t.color,normalMap:t.normal,
  normalMapType:THREE.TangentSpaceNormalMap,
  normalScale:new THREE.Vector2(1.12,1.12),
  roughnessMap:t.roughness,roughness:.89,
  aoMap:t.ao,aoMapIntensity:1.24,
  metalness:0,side:THREE.DoubleSide
 });
 mat.name='Cliff Hand · clean sandstone / relief knuckles / wrist-only moss';
 return mat;
}
window.SWYRL_ENGINE_CLIFF_MATERIAL_291=Object.freeze({
 status:()=>({...se291State,createdMaps:se291Maps.size,
  knuckleUVs:se291Knuckles.map(k=>[k.u,k.v]),geometryObjectsCreated:0}),
 createMaterial:se291WristMossKnuckleMaterial
});
