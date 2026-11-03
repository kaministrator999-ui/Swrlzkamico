// §E v11.241 candidate: Sheep Tag grass PBR on existing authored ground.
const se241Grass={ready:false,source:null,normal:null,rough:null,applied:0,errors:0,
  prepared:new WeakSet(),waiting:new WeakSet(),tileCount:16};
function se241SurfaceTexture(canvas){
  const tex=new THREE.CanvasTexture(canvas);
  tex.colorSpace=THREE.NoColorSpace;
  tex.wrapS=tex.wrapT=THREE.RepeatWrapping;
  tex.repeat.set(se241Grass.tileCount,se241Grass.tileCount);
  tex.minFilter=THREE.LinearMipmapLinearFilter;
  tex.magFilter=THREE.LinearFilter;
  tex.generateMipmaps=true;
  tex.anisotropy=Math.min(4,renderer.capabilities.getMaxAnisotropy());
  return tex;
}
function se241PreparePBR(image){
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
  se241Grass.source=tile;se241Grass.normal=normal;se241Grass.rough=rough;
}
function se241ApplyOneGround(mesh){
  if(!se241Grass.ready||se241Grass.prepared.has(mesh))return;
  if(!mesh?.isMesh||!['stMeadowGround','MoonbellWildwoodGround'].includes(mesh.name))return;
  const original=mesh.material;
  if(!original?.map||!original.isMeshStandardMaterial)return;
  const source=original.map.image;
  const width=source?.naturalWidth||source?.width||0;
  if(!width){
    // TextureLoader may have no image object until its asynchronous callback.
    // A bounded timer handles this path without polling every XR frame.
    if(!se241Grass.waiting.has(mesh)){
      se241Grass.waiting.add(mesh);
      let tries=0;
      const retry=()=>{
        if(se241Grass.prepared.has(mesh))return;
        const pending=mesh.material?.map?.image;
        if((pending?.naturalWidth||pending?.width||0)>0){
          se241Grass.waiting.delete(mesh);
          se241ApplyOneGround(mesh);
        }else if(++tries<80){
          setTimeout(retry,150);
        }else{
          se241Grass.waiting.delete(mesh);
          se241Grass.errors++;
        }
      };
      setTimeout(retry,90);
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
    const step=size/se241Grass.tileCount;
    for(let y=0;y<se241Grass.tileCount;y++)
      for(let x=0;x<se241Grass.tileCount;x++)
        gc.drawImage(se241Grass.source,x*step,y*step,step,step);
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
    material.normalMap=se241SurfaceTexture(se241Grass.normal);
    material.normalScale.set(.24,.24); // subtle relief; no Quest stereo crawling
    material.roughnessMap=se241SurfaceTexture(se241Grass.rough);
    material.roughness=1;material.metalness=0;material.needsUpdate=true;
    mesh.material=material;
    mesh.userData.se241GrassMaterial=true;
    se241Grass.prepared.add(mesh);se241Grass.applied++;
  }catch(error){se241Grass.errors++;console.warn('Sheep grass material:',error);}
}
function se241VisitGrass(group){
  group?.traverse?.(object=>se241ApplyOneGround(object));
}
const se241PreviousMakeVisual=stMakeVisual;
stMakeVisual=function(type){
  const result=se241PreviousMakeVisual(type);
  if(type==='st-meadow')se241VisitGrass(result);
  return result;
};
const se241SourceImage=new Image();
se241SourceImage.decoding='async';
se241SourceImage.onload=()=>{
  try{
    se241PreparePBR(se241SourceImage);se241Grass.ready=true;
    if(typeof actors!=='undefined')for(const actor of actors)se241VisitGrass(actor);
  }catch(error){se241Grass.errors++;console.warn('Sheep grass maps:',error);}
};
se241SourceImage.onerror=()=>{se241Grass.errors++;console.warn('Sheep grass color source missing');};
se241SourceImage.src='assets/sheep-tag/grass-source-color-quest.webp';
window.SWYRL_ENGINE_SHEEP_GRASS_PBR_241=Object.freeze({
  status:()=>({ready:se241Grass.ready,applied:se241Grass.applied,
    errors:se241Grass.errors,tiling:se241Grass.tileCount,
    material:'base color + computed tangent normal + matte roughness'})
});