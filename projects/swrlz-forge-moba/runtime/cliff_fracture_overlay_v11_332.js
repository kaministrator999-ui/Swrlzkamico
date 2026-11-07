// §E v11.332: emphasize real mineral fractures from the supplied rock atlas.
// Atlas tile 7 is the authored light-on-dark fracture mask, aligned with
// the clean sandstone albedo (tile 4), normal and AO maps. No new geometry.
const se332CliffCrackStats={passes:0,lastPixels:0,lastMaxContrast:0,lastError:null};
function se332OverlayRockFractures(img,albedoCtx){
 const size=384;
 const mask=document.createElement('canvas');mask.width=mask.height=size;
 const m=mask.getContext('2d',{willReadFrequently:true});
 if(!m)throw Error('Cliff fracture mask canvas unavailable');
 m.drawImage(img,1152,384,size,size,0,0,size,size);
 const src=m.getImageData(0,0,size,size).data;
 const base=albedoCtx.getImageData(0,0,size,size);
 const dst=base.data;
 const signals=new Float32Array(size*size);
 for(let i=0,j=0;i<src.length;i+=4,j++){
  const lum=src[i]*.2126+src[i+1]*.7152+src[i+2]*.0722;
  signals[j]=Math.min(1,Math.max(0,(lum-42)/160));
 }
 let changed=0,maxContrast=0;
 for(let y=0;y<size;y++)for(let x=0;x<size;x++){
  const i=y*size+x,k=i*4,center=signals[i];
  let neighbor=center;
  if(x>0)neighbor=Math.max(neighbor,signals[i-1]);
  if(x<size-1)neighbor=Math.max(neighbor,signals[i+1]);
  if(y>0)neighbor=Math.max(neighbor,signals[i-size]);
  if(y<size-1)neighbor=Math.max(neighbor,signals[i+size]);
  const weight=Math.min(.88,.72*center+.22*Math.max(0,neighbor-center));
  if(weight<.025)continue;
  changed++;maxContrast=Math.max(maxContrast,weight);
  dst[k]=Math.round(dst[k]*(1-weight)+53*weight);
  dst[k+1]=Math.round(dst[k+1]*(1-weight)+36*weight);
  dst[k+2]=Math.round(dst[k+2]*(1-weight)+27*weight);
 }
 albedoCtx.putImageData(base,0,0);
 se332CliffCrackStats.passes++;
 se332CliffCrackStats.lastPixels=changed;
 se332CliffCrackStats.lastMaxContrast=maxContrast;
 se332CliffCrackStats.lastError=null;
 return {pixels:changed,maxContrast};
}
window.SWYRL_ENGINE_CLIFF_FRACTURES_332=Object.freeze({
 atlasTile:7,source:'owner-cliff-pbr-atlas',
 status:()=>({...se332CliffCrackStats,geometryAdded:0})
});
