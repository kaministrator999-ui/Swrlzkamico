// §E v11.370 · Cliff stone surface polish on the genuine WebXR hand.
// Retain the approved 1360-vertex hand, all UV islands, 17 bones and other starters.
// This one-time atlas bake uses *actual mesh UV triangles* to localize moss and
// wrist wear rather than assuming the WebXR islands follow a planar UV layout.
const se370State={requests:0,successes:0,errors:0,lastError:null,
  mappedPixels:0,crackPixels:0,mossPixels:0,textureSize:384,
  sourceAtlas:SE288_ATLAS,atlasTiles:[4,1,2,3,7],geometryChanged:false};
let se370Maps=null,se370Loading=false;
const se370Pending=new Set();
const se370Clamp=v=>Math.max(0,Math.min(1,v));
const se370Smooth=(a,b,v)=>{const t=se370Clamp((v-a)/(b-a));return t*t*(3-2*t);};
function se370Hash(x,y){
 let n=((x*374761393+y*668265263)|0);
 n=Math.imul(n^(n>>>13),1274126177);
 return ((n^(n>>>16))>>>0)/4294967295;
}
function se370Noise(x,y){
 const ix=Math.floor(x),iy=Math.floor(y),fx=x-ix,fy=y-iy;
 const u=fx*fx*(3-2*fx),v=fy*fy*(3-2*fy);
 const a=se370Hash(ix,iy)*(1-u)+se370Hash(ix+1,iy)*u;
 const b=se370Hash(ix,iy+1)*(1-u)+se370Hash(ix+1,iy+1)*u;
 return a*(1-v)+b*v;
}
function se370SurfaceUV(mesh,size){
 const pos=mesh.positions,uv=mesh.uvs,idx=mesh.indices;
 if(pos.length!==4080||uv.length!==2720||idx.length!==6942)
  throw Error('Cliff material requires exact original WebXR hand topology');
 const n=size*size,xs=new Float32Array(n),ys=new Float32Array(n),
  zs=new Float32Array(n),filled=new Uint8Array(n);
 const out=[0,0,0],p=[0,0,0];
 for(let t=0;t<idx.length;t+=3){
  const a=idx[t],b=idx[t+1],c=idx[t+2];
  const ax=uv[a*2]*(size-1),ay=(1-uv[a*2+1])*(size-1);
  const bx=uv[b*2]*(size-1),by=(1-uv[b*2+1])*(size-1);
  const cx=uv[c*2]*(size-1),cy=(1-uv[c*2+1])*(size-1);
  const det=(by-cy)*(ax-cx)+(cx-bx)*(ay-cy);
  if(Math.abs(det)<1e-8)continue;
  const minx=Math.max(0,Math.floor(Math.min(ax,bx,cx)));
  const maxx=Math.min(size-1,Math.ceil(Math.max(ax,bx,cx)));
  const miny=Math.max(0,Math.floor(Math.min(ay,by,cy)));
  const maxy=Math.min(size-1,Math.ceil(Math.max(ay,by,cy)));
  for(let y=miny;y<=maxy;y++)for(let x=minx;x<=maxx;x++){
   const px=x+.5,py=y+.5;
   const w1=((by-cy)*(px-cx)+(cx-bx)*(py-cy))/det;
   const w2=((cy-ay)*(px-cx)+(ax-cx)*(py-cy))/det;
   const w3=1-w1-w2;
   if(w1<-.0005||w2<-.0005||w3<-.0005)continue;
   const j=y*size+x;filled[j]=1;
   xs[j]=w1*pos[a*3]+w2*pos[b*3]+w3*pos[c*3];
   ys[j]=w1*pos[a*3+1]+w2*pos[b*3+1]+w3*pos[c*3+1];
   zs[j]=w1*pos[a*3+2]+w2*pos[b*3+2]+w3*pos[c*3+2];
  }
 }
 return {xs,ys,zs,filled};
}
function se370RefinePixel(x,y,z,rgb,mossRgb,fracture,rough,ao){
 const coarse=se370Noise(x*5.9+z*3.2,y*6.6-z*2.8);
 const mineral=se370Noise(x*23+y*2,y*18-z*7);
 const grain=(mineral-.5)*7;
 // Preserve the owner's original sandstone, but prevent every tile boundary
 // becoming an equally dark, unbroken line.
 const crack=se370Clamp((fracture-55)/167);
 const interruptions=se370Smooth(.20,.74,coarse)*(.55+.45*mineral);
 const seam=crack**1.42*(.19+.55*interruptions);
 let r=rgb[0],g=rgb[1],b=rgb[2];
 const blend=(target,v,a)=>v+(target-v)*a;
 r=blend(76,r,seam);g=blend(53,g,seam);b=blend(42,b,seam);
 // Map actual wrist, thenar/thumb web and back-of-hand creases into UV
 // islands. This is based on model coordinates, not arbitrary UV quadrants.
 const wrist=1-se370Smooth(.94,1.50,y);
 const thumbWeb=Math.exp(-(((x+.46)/.31)**2+((y-1.58)/.28)**2));
 const dorsal=(se370Smooth(1.39,1.67,y)*
  (1-se370Smooth(1.96,2.20,y)))*se370Smooth(-.08,.11,-z);
 const region=se370Clamp(.65*wrist+.27*thumbWeb+.20*dorsal);
 const patches=se370Smooth(.43,.73,coarse)*se370Smooth(.32,.66,mineral);
 const moss=se370Clamp(region*patches*(.46+.24*seam));
 // Use the real owner moss pigment as pigment, not a green flat shader.
 // Neutral clean sandstone comes from tile 4 and source moss from tile 0.
 const pigment=[Math.min(105,mossRgb[0]*.67+31),
  Math.min(133,Math.max(83,mossRgb[1]*.80+17)),
  Math.min(83,mossRgb[2]*.45+24)];
 r=blend(pigment[0],r,moss);g=blend(pigment[1],g,moss);b=blend(pigment[2],b,moss);
 // A subtle darker eroded stone lip visually finishes the real clipped
 // wrist end without changing the already-approved mesh silhouette.
 const cuff=(1-se370Smooth(.71,.91,y))*(.44+.56*coarse);
 const wear=.10*cuff;
 r=blend(98,r,wear)+grain;g=blend(75,g,wear)+grain;b=blend(57,b,wear)+grain;
 const roughDelta=Math.round(8*mineral+15*moss+8*cuff);
 const aoDelta=Math.round(24*seam+9*moss+6*cuff);
 return {color:[r,g,b].map(v=>Math.min(255,Math.max(0,Math.round(v)))),
  rough:Math.min(255,rough+roughDelta),
  ao:Math.max(0,ao-aoDelta),seam,moss,cuff};
}
function se370BakeTiles(img,mesh){
 const size=384,canvases=[],contexts=[],images=[];
 // 0=albedo (clean tile 4), 1=normal, 2=roughness, 3=AO,
 // 4=owner moss pigment (tile 0), 5=fracture signal (tile 7).
 const tiles=[[0,384],[384,0],[768,0],[1152,0],[0,0],[1152,384]];
 for(const [sx,sy] of tiles){
  const canvas=document.createElement('canvas');canvas.width=canvas.height=size;
  const ctx=canvas.getContext('2d',{willReadFrequently:true});
  if(!ctx)throw Error('Cliff mapped stone canvas unavailable');
  ctx.drawImage(img,sx,sy,size,size,0,0,size,size);
  canvases.push(canvas);contexts.push(ctx);images.push(ctx.getImageData(0,0,size,size));
 }
 const [color,normal,rough,ao,pigment,fractures]=images;
 const coords=se370SurfaceUV(mesh,size);
 let mapped=0,cracks=0,mossed=0;
 for(let i=0;i<size*size;i++){
  if(!coords.filled[i])continue;
  mapped++;
  const j=i*4;
  const signal=fractures.data[j]*.2126+fractures.data[j+1]*.7152+
   fractures.data[j+2]*.0722;
  const r=se370RefinePixel(coords.xs[i],coords.ys[i],coords.zs[i],
   [color.data[j],color.data[j+1],color.data[j+2]],
   [pigment.data[j],pigment.data[j+1],pigment.data[j+2]],
   signal,rough.data[j],ao.data[j]);
  for(let k=0;k<3;k++)color.data[j+k]=r.color[k];
  for(let k=0;k<3;k++)rough.data[j+k]=r.rough;
  for(let k=0;k<3;k++)ao.data[j+k]=r.ao;
  if(r.seam>.12)cracks++;if(r.moss>.02)mossed++;
 }
 for(const k of [0,2,3])contexts[k].putImageData(images[k],0,0);
 if(mapped<4000)throw Error('WebXR UV islands could not be located for stone maps');
 const maps=canvases.slice(0,4).map((canvas,i)=>{
  const texture=new THREE.CanvasTexture(canvas);
  texture.colorSpace=i===0?THREE.SRGBColorSpace:THREE.NoColorSpace;
  texture.wrapS=texture.wrapT=THREE.ClampToEdgeWrapping;
  texture.minFilter=THREE.LinearMipmapLinearFilter;
  texture.magFilter=THREE.LinearFilter;
  texture.anisotropy=2;texture.needsUpdate=true;
  return texture;
 });
 return {maps,mapped,cracks,mossed};
}
function se370AttachMaps(material,maps){
 [material.map,material.normalMap,material.roughnessMap,material.aoMap]=maps;
 material.normalScale.set(.85,.85);
 material.roughness=.91;material.aoMapIntensity=1.07;
 material.color.set('#ffffff');
 material.name='Cliff · graded mineral seams / joint moss / eroded sandstone cuff';
 material.needsUpdate=true;
}
function se370PolishedCliffMaterial(part){
 // Keep native, already-visible stone maps until the one-time edited maps
 // have loaded, including any CDN/atlas fallback.
 const mat=se290CliffMaterial(part);
 mat.name='Cliff · WebXR sandstone surface polish (source atlas loading)';
 if(se370Maps){se370AttachMaps(mat,se370Maps);return mat;}
 se370Pending.add(mat);
 if(!se370Loading){
  se370Loading=true;se370State.requests++;
  const image=new Image();
  image.onload=()=>{
   try{
    const result=se370BakeTiles(image,part.topologyMesh);
    se370Maps=result.maps;
    se370State.mappedPixels=result.mapped;
    se370State.crackPixels=result.cracks;
    se370State.mossPixels=result.mossed;
    se370State.successes++;
    for(const pending of se370Pending)se370AttachMaps(pending,se370Maps);
    se370Pending.clear();se370State.lastError=null;
   }catch(e){
    se370State.errors++;se370State.lastError=String(e?.message||e);
    console.warn('Cliff stone UV refinement',e);se370Pending.clear();
   }
   se370Loading=false;
  };
  image.onerror=()=>{
   se370State.errors++;se370State.lastError='Owner Cliff PBR atlas unavailable';
   se370Pending.clear();se370Loading=false;
  };
  image.src=SE288_ATLAS;
 }
 return mat;
}
window.SWYRL_ENGINE_CLIFF_POLISH_370=Object.freeze({
 status:()=>({...se370State,ready:!!se370Maps,queued:se370Pending.size,
  originalUV:true,geometryObjectsAdded:0}),
 refine:se370RefinePixel,
 bake:se370BakeTiles,material:se370PolishedCliffMaterial
});
