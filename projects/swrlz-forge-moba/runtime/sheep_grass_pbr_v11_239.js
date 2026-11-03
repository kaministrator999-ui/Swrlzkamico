// §E v11.239 candidate: Sheep Tag grass PBR on existing authored ground.
const se239Grass={ready:false,source:null,normal:null,rough:null,applied:0,errors:0,
  prepared:new WeakSet(),waiting:new WeakSet(),tileCount:16};
function se239SurfaceTexture(canvas){
  const tex=new THREE.CanvasTexture(canvas);
  tex.colorSpace=THREE.NoColorSpace;
  tex.wrapS=tex.wrapT=THREE.RepeatWrapping;
  tex.repeat.set(se239Grass.tileCount,se239Grass.tileCount);
  tex.minFilter=THREE.LinearMipmapLinearFilter;
  tex.magFilter=THREE.LinearFilter;
  tex.generateMipmaps=true;
  tex.anisotropy=Math.min(4,renderer.capabilities.getMaxAnisotropy());
  return tex;
}
function se239PreparePBR(image){
  const tile=document.createElement('canvas');tile.width=tile.height=256;
  const ctx=tile.getContext('2d',{willReadFrequently:true});
  if(!ctx)throw Error('Grass color canvas unavailable');
  ctx.drawImage(image,0,0,256,256);
  const src=ctx.getImageData(0,0,256,256).data;
  const heights=new Float32Array(256*256);
  for(let i=0,j=0;i<src.length;i+=4,j++)
    heights[j]=(src[i]*.299+src[i+1]*.587+src[i+2]*.114)/255;
  const normal=document.createElement('canvas'),rough=document.createElement('canvas');
  normal.width=normal.height=rough.width=rough.height=256;
  const nc=normal.getContext('2d'),rc=rough.getContext('2d');
  if(!nc||!rc)throw Error('Grass map canvas unavailable');
  const nd=nc.createImageData(256,256),rd=rc.createImageData(256,256);
  for(let y=0;y<256;y++)for(let x=0;x<256;x++){
    const k=y*256+x,i=k*4;
    const dx=(heights[y*256+((x+1)&255)]-heights[y*256+((x+255)&255)])*.75;
    const dy=(heights[((y+1)&255)*256+x]-heights[((y+255)&255)*256+x])*.75;
    const inv=1/Math.hypot(dx,dy,1);
    nd.data[i]=Math.round((-.5*dx*inv+.5)*255);
    nd.data[i+1]=Math.round((-.5*dy*inv+.5)*255);
    nd.data[i+2]=Math.round((.5*inv+.5)*255);nd.data[i+3]=255;
    const v=Math.round(224+(0.5-heights[k])*23);
    rd.data[i]=rd.data[i+1]=rd.data[i+2]=Math.max(206,Math.min(247,v));rd.data[i+3]=255;
  }
  nc.putImageData(nd,0,0);rc.putImageData(rd,0,0);
  se239Grass.source=tile;se239Grass.normal=normal;se239Grass.rough=rough;
}
function se239ApplyOneGround(mesh){
  if(!se239Grass.ready||se239Grass.prepared.has(mesh))return;
  if(!mesh?.isMesh||!['stMeadowGround','MoonbellWildwoodGround'].includes(mesh.name))return;
  const original=mesh.material;
  if(!original?.map||!original.isMeshStandardMaterial)return;
  const source=original.map.image;
  const width=source?.naturalWidth||source?.width||0;
  if(!width){
    if(source?.addEventListener&&!se239Grass.waiting.has(mesh)){
      se239Grass.waiting.add(mesh);
      source.addEventListener('load',()=>se239ApplyOneGround(mesh),{once:true});
    }
    return;
  }
  try{
    const quest=/(?:OculusBrowser|Quest)/i.test(navigator.userAgent||'');
    const size=mesh.name==='MoonbellWildwoodGround'&&!quest?2048:1024;
    const canvas=document.createElement('canvas');
    canvas.width=canvas.height=size;
    const ctx=canvas.getContext('2d',{willReadFrequently:true});
    if(!ctx)return;
    ctx.drawImage(source,0,0,size,size);
    const authored=ctx.getImageData(0,0,size,size);
    const grass=document.createElement('canvas');grass.width=grass.height=size;
    const gc=grass.getContext('2d',{willReadFrequently:true});
    if(!gc)return;
    // Match diffuse tiling to the repeated normal and roughness maps.
    // Explicit tiles avoid CanvasPattern.setTransform browser variations.
    const step=size/se239Grass.tileCount;
    for(let y=0;y<se239Grass.tileCount;y++)
      for(let x=0;x<se239Grass.tileCount;x++)
        gc.drawImage(se239Grass.source,x*step,y*step,step,step);
    const d=authored.data,s=gc.getImageData(0,0,size,size).data;
    for(let i=0;i<d.length;i+=4){
      // Green vegetation receives the new texture; roads/landmarks survive.
      const green=Math.max(0,Math.min(1,((d[i+1]-d[i])/(Math.max(1,d[i+1]))-.025)*8));
      const blend=green*.75;
      d[i]=Math.round(d[i]*(1-blend)+s[i]*blend);
      d[i+1]=Math.round(d[i+1]*(1-blend)+s[i+1]*blend);
      d[i+2]=Math.round(d[i+2]*(1-blend)+s[i+2]*blend);
    }
    ctx.putImageData(authored,0,0);
    const material=original.clone();
    const base=new THREE.CanvasTexture(canvas);
    base.colorSpace=THREE.SRGBColorSpace;
    base.minFilter=THREE.LinearMipmapLinearFilter;
    base.magFilter=THREE.LinearFilter;
    base.generateMipmaps=true;
    base.anisotropy=Math.min(4,renderer.capabilities.getMaxAnisotropy());
    material.map=base;
    material.normalMap=se239SurfaceTexture(se239Grass.normal);
    material.normalScale.set(.24,.24); // subtle relief; no Quest stereo crawling
    material.roughnessMap=se239SurfaceTexture(se239Grass.rough);
    material.roughness=1;material.metalness=0;material.needsUpdate=true;
    mesh.material=material;
    mesh.userData.se239GrassMaterial=true;
    se239Grass.prepared.add(mesh);se239Grass.applied++;
  }catch(error){se239Grass.errors++;console.warn('Sheep grass material:',error);}
}
function se239VisitGrass(group){
  group?.traverse?.(object=>se239ApplyOneGround(object));
}
const se239PreviousMakeVisual=stMakeVisual;
stMakeVisual=function(type){
  const result=se239PreviousMakeVisual(type);
  if(type==='st-meadow')se239VisitGrass(result);
  return result;
};
const se239SourceImage=new Image();
se239SourceImage.decoding='async';
se239SourceImage.onload=()=>{
  try{
    se239PreparePBR(se239SourceImage);se239Grass.ready=true;
    if(typeof actors!=='undefined')for(const actor of actors)se239VisitGrass(actor);
  }catch(error){se239Grass.errors++;console.warn('Sheep grass maps:',error);}
};
se239SourceImage.onerror=()=>{se239Grass.errors++;console.warn('Sheep grass color source missing');};
se239SourceImage.src='assets/sheep-tag/grass-source-color-quest.webp';
window.SWYRL_ENGINE_SHEEP_GRASS_PBR_239=Object.freeze({
  status:()=>({ready:se239Grass.ready,applied:se239Grass.applied,
    errors:se239Grass.errors,tiling:se239Grass.tileCount,
    material:'base color + computed tangent normal + matte roughness'})
});