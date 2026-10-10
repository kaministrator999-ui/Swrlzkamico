// Original painted facial components retain independent native face animation.
// The face still uses the head's exact triangles and transparent padded UVs.
const PAINTED_FACE_ASSET='assets/anime/mage-faces-painted.png';
const PAINTED_FACE_ALPHA=20;
// Measured row bands preserve the complete brushwork in the original atlas.
const PAINTED_FACE_ROWS=[0,320,560,768,1056,1312,1536];
const PAINTED_FACE_IDS=['leftEye','rightEye','leftIris','rightIris','leftClosedEye','rightClosedEye','leftBrow','rightBrow','nose','neutralMouth','openMouth','smileMouth'];
let paintedFaceAtlas=null;
function paintedFaceSource(){
  const texture=storyTexture(PAINTED_FACE_ASSET),image=texture.image;
  if(!image?.width)return null;
  if(paintedFaceAtlas?.image===image)return paintedFaceAtlas;
  const canvas=document.createElement('canvas');canvas.width=image.naturalWidth||image.width;canvas.height=image.naturalHeight||image.height;
  const context=canvas.getContext('2d',{willReadFrequently:true});context.drawImage(image,0,0);
  const pixels=context.getImageData(0,0,canvas.width,canvas.height).data,characters={};
  for(const character of RIG_CHARACTERS){
    const offset=character==='kami'?0:12,parts={};
    for(let index=0;index<PAINTED_FACE_IDS.length;index++){
      const slot=offset+index,column=slot%4,row=Math.floor(slot/4),l=Math.floor(column*canvas.width/4),r=Math.floor((column+1)*canvas.width/4);
      const t=Math.round(PAINTED_FACE_ROWS[row]*canvas.height/1536),b=Math.round(PAINTED_FACE_ROWS[row+1]*canvas.height/1536);
      let x0=r,y0=b,x1=l,y1=t,ink=0;
      for(let y=t;y<b;y++)for(let x=l;x<r;x++)if(pixels[(y*canvas.width+x)*4+3]>PAINTED_FACE_ALPHA){
        x0=Math.min(x0,x);y0=Math.min(y0,y);x1=Math.max(x1,x+1);y1=Math.max(y1,y+1);ink++;
      }
      if(!ink)return null;
      parts[PAINTED_FACE_IDS[index]]={id:PAINTED_FACE_IDS[index],sourceBounds:{min:[x0,y0],max:[x1,y1]},sourceInkPixels:ink};
    }
    characters[character]=parts;
  }
  paintedFaceAtlas={image,canvas,pixels,width:canvas.width,height:canvas.height,characters};return paintedFaceAtlas;
}
function paintedFaceDraw(context,atlas,part,x,y,width,height,rotation=0,alpha=1){
  const [sx,sy]=part.sourceBounds.min,[rx,by]=part.sourceBounds.max;
  context.save();context.translate(x,y);context.rotate(rotation);context.globalAlpha=alpha;
  context.drawImage(atlas.image,sx,sy,rx-sx,by-sy,-width/2,-height/2,width,height);context.restore();
  const corners=[[-width/2,-height/2],[width/2,-height/2],[width/2,height/2],[-width/2,height/2]].map(([a,b])=>[x+a*Math.cos(rotation)-b*Math.sin(rotation),y+a*Math.sin(rotation)+b*Math.cos(rotation)]);
  return {...part,destinationBounds:{min:[Math.min(...corners.map(point=>point[0])),Math.min(...corners.map(point=>point[1]))],max:[Math.max(...corners.map(point=>point[0])),Math.max(...corners.map(point=>point[1]))]}};
}
function paintedFaceEyeClip(context,x,y,width,height,skull){
  context.beginPath();
  if(skull)context.ellipse(x,y,width*.34,height*.29,0,0,Math.PI*2);
  else{
    context.moveTo(x-width*.38,y+height*.10);
    context.bezierCurveTo(x-width*.20,y-height*.24,x+width*.20,y-height*.24,x+width*.37,y+height*.04);
    context.bezierCurveTo(x+width*.16,y+height*.27,x-width*.22,y+height*.27,x-width*.38,y+height*.10);
  }
  context.closePath();context.clip();
}
const paintedFaceOriginalPaint=rigPaintFace;
rigPaintFace=function(face,character,sample,time){
  const cfg=rigModel().characters[character];
  // Imported character art keeps its existing facial rendering behavior.
  const atlas=cfg.asset==='assets/anime/'+character+'-rig.png'?paintedFaceSource():null;
  if(!atlas){face.paintedFeatures=null;return paintedFaceOriginalPaint(face,character,sample,time);}
  const s={...sample},cue=storyBeat(time)?.cue||'';
  const speaking=s.speech&&(character==='kami'?/^KAMI\b/i:/^[§$]?WYRLZ\b/i).test(cue.trim());
  if(speaking)s.mouth=Math.max(s.mouth,.12+.38*(.5+.5*Math.sin(time*31)));
  const hash='painted:'+character+':'+[s.expression,...Object.keys(RIG_FACE_BOUNDS).map(key=>Math.round(s[key]*50))].join(':');
  face.applied=s;if(face.hash===hash)return;face.hash=hash;
  const c=face.canvas.getContext('2d');c.clearRect(0,0,face.canvas.width,face.canvas.height);
  const parts=atlas.characters[character],skull=character==='swyrlz',happy=s.expression==='happy',sad=s.expression==='sad',determined=s.expression==='determined',surprised=s.expression==='surprised',components=[];
  const aperture=Math.max(0,(1-s.blink)*(surprised?1.04:determined?.67:happy?.78:.94));
  const eyeWidth=skull?72:68,eyeHeight=skull?43:35,eyeY=71;
  c.save();
  // These margins map inside the measured skin and leave all UV borders clear.
  c.beginPath();c.rect(13,20,230,151);c.clip();
  for(const side of [-1,1]){
    const prefix=side===-1?'left':'right',x=128+side*50,tilt=side*(determined?-.055:sad?.035:0);
    const openAlpha=Math.min(1,aperture/.22),closedAlpha=1-openAlpha;
    if(openAlpha>0){
      const height=eyeHeight*Math.max(.12,aperture);
      components.push(paintedFaceDraw(c,atlas,parts[prefix+'Eye'],x,eyeY,eyeWidth,height,tilt,openAlpha));
      c.save();paintedFaceEyeClip(c,x,eyeY,eyeWidth,height,skull);
      const ix=x+s.gazeX*(skull?8:7),iy=eyeY+s.gazeY*(skull?5:4)+(skull?0:2);
      components.push(paintedFaceDraw(c,atlas,parts[prefix+'Iris'],ix,iy,skull?18:21,skull?18:23,0,openAlpha));c.restore();
    }
    if(closedAlpha>0)components.push(paintedFaceDraw(c,atlas,parts[prefix+'ClosedEye'],x,eyeY,eyeWidth,skull?18:13,tilt,closedAlpha));
    const browY=38-s.brow*5-(surprised?5:0),browTilt=side*(determined?.17:sad?-.12:0);
    components.push(paintedFaceDraw(c,atlas,parts[prefix+'Brow'],x,browY,skull?60:55,skull?10:8,browTilt));
  }
  components.push(paintedFaceDraw(c,atlas,parts.nose,128,skull?110:109,skull?17:13,skull?24:23));
  const smile=s.smile+(happy?.6:sad?-.4:0),mouthY=145;
  if(s.mouth>.06){
    const width=skull?57:43+(surprised?3:0),height=(skull?7:3)+s.mouth*(skull?20:19);
    components.push(paintedFaceDraw(c,atlas,parts.openMouth,128,mouthY,width,height));
  }else{
    const alpha=Math.max(0,Math.min(1,smile)),width=skull?57:43;
    components.push(paintedFaceDraw(c,atlas,parts.neutralMouth,128,mouthY,width,skull?15:8,0,1-alpha));
    if(alpha>0)components.push(paintedFaceDraw(c,atlas,parts.smileMouth,128,mouthY,width+(skull?3:2)*alpha,skull?15:9,0,alpha));
    // Negative smiles bend the separate painted mouth without moving its anchor.
    if(smile<0){
      c.save();c.globalAlpha=Math.min(.4,-smile*.4);c.strokeStyle=skull?'#916b3b':'#8b5440';c.lineWidth=1;
      c.beginPath();c.moveTo(111,mouthY+1);c.quadraticCurveTo(128,mouthY-3,145,mouthY+1);c.stroke();c.restore();
    }
  }
  c.restore();
  face.paintedFeatures={ready:true,asset:PAINTED_FACE_ASSET,sourceWidth:atlas.width,sourceHeight:atlas.height,sourceAlphaThreshold:PAINTED_FACE_ALPHA,components};
  face.texture.needsUpdate=true;
};
function paintedFaceRegion(pixels,width,height,id,bounds){
  const [x0,y0,x1,y1]=bounds;let hash=2166136261,alphaPixels=0,left=x1,top=y1,right=x0,bottom=y0;const samples=[];
  for(let y=y0;y<Math.min(height,y1);y++)for(let x=x0;x<Math.min(width,x1);x++){
    const i=(y*width+x)*4;
    for(let channel=0;channel<4;channel++){hash^=pixels[i+channel];hash=Math.imul(hash,16777619);}
    if(pixels[i+3]>PAINTED_FACE_ALPHA){alphaPixels++;left=Math.min(left,x);top=Math.min(top,y);right=Math.max(right,x+1);bottom=Math.max(bottom,y+1);}
    if(pixels[i+3]>=248)samples.push({x,y,alpha:pixels[i+3]/255,rgb:[pixels[i],pixels[i+1],pixels[i+2]]});
  }
  const canvasInkBounds=alphaPixels?{min:[left,top],max:[right,bottom]}:null;
  const inkHash=(hash>>>0).toString(16).padStart(8,'0');
  return {id,hash:inkHash,inkHash,alphaPixels,canvasInkBounds,samples};
}
function paintedFaceStatus(rig){
  const face=rig.face;if(!face.paintedFeatures)return {ready:false,asset:PAINTED_FACE_ASSET};
  const width=face.canvas.width,height=face.canvas.height,pixels=face.canvas.getContext('2d').getImageData(0,0,width,height).data;
  const regions=[['leftEye',[36,49,119,96]],['rightEye',[137,49,220,96]],['brows',[38,20,218,49]],['nose',[114,96,142,126]],['mouth',[94,128,163,164]]]
    .map(([id,bounds])=>paintedFaceRegion(pixels,width,height,id,bounds));
  const pixelSamples=[];
  for(const region of regions){
    // Samples cover each feature rather than stopping in the first eyebrow.
    const count=Math.min(12,region.samples.length);
    for(let i=0;i<count;i++){
      const sample=region.samples[Math.floor((i+.5)*region.samples.length/count)];
      const x=((sample.x+.5)/width-.5)*face.fit.width,y=(.5-(sample.y+.5)/height)*face.fit.height;
      const local=new THREE.Vector3(x,y,rigPlaneSurfaceZ(face.mesh,x,y)-face.mesh.position.z);
      const world=face.mesh.localToWorld(local.clone());
      pixelSamples.push({id:region.id,pixel:[sample.x,sample.y],local:local.toArray(),world:world.toArray(),screen:rigProjectedWorld(world),alpha:sample.alpha,rgb:sample.rgb});
    }
  }
  const combined=paintedFaceRegion(pixels,width,height,'face',[0,0,width,height]);
  return {...face.paintedFeatures,inkHash:combined.inkHash,
    regions:Object.fromEntries(regions.map(({samples,...region})=>[region.id,region])),pixelSamples};
}
const paintedFaceOriginalRenderStatus=rigRenderStatus;
rigRenderStatus=function(character){
  const status=paintedFaceOriginalRenderStatus(character);if(!status?.rigged)return status;
  const actor=animeCine?.cast?.[character==='kami'?'kami':'wisp']||storyBoundActor(character),rig=actor?.userData.rig;
  return {...status,face:{...status.face,paintedFeatures:paintedFaceStatus(rig)}};
};
const paintedFaceOriginalTextureLoaded=rigTextureLoaded;
rigTextureLoaded=function(texture,source){
  paintedFaceOriginalTextureLoaded(texture,source);
  if(source===PAINTED_FACE_ASSET){paintedFaceSource();rigRefreshStage();}
};
window.SWYRL_ENGINE_RIG=Object.freeze({...window.SWYRL_ENGINE_RIG,renderStatus:rigRenderStatus});
window.SWYRL_ENGINE_FACE=Object.freeze({asset:PAINTED_FACE_ASSET,ready:()=>!!paintedFaceSource(),renderStatus:character=>rigRenderStatus(character)?.face?.paintedFeatures||null});
