// §E v11.206 · Sheep Tag PLAY meadow dressing, fog layering and stable Quest FPS.
// Scene-only appearance; never add actors, colliders, rules or visibility data.
const se206={
 session:null,canvas:null,ctx:null,mesh:null,texture:null,stage:0,seed:0,
 blooms:0,avoidedRoads:0,frames:0,textureUploads:0,decorCreated:0,
 decorRemoved:0,fogSession:null,fogOriginal:null,fogSetups:0,skippedModalFrames:0,
 groundPosition:null,paintMs:0,lastError:''
};
function se206Random(){
 se206.seed=(Math.imul(se206.seed,1664525)+1013904223)>>>0;
 return se206.seed/4294967296;
}
function se206RoadClear(x,z,bounds){
 // Visual-only approximate roads: keep the center, cross and diagonal
 // approach lanes clean for fast house placement. Actual map collision,
 // painted roads and existing authored level data remain untouched.
 const span=Math.max(20,bounds),p=Math.hypot(x,z);
 if(p<10.5)return false;
 if(Math.abs(x)<2.5||Math.abs(z)<2.5)return false;
 if(p<span*.89&&(Math.abs(x-z)<2.4||Math.abs(x+z)<2.4))return false;
 return true;
}
function se206RestoreFog(){
 const old=se206.fogOriginal;
 if(!old)return;
 const {fog,material,mesh,texture}=old;
 material.opacity=old.opacity;material.depthWrite=old.depthWrite;
 material.depthTest=old.depthTest;
 material.polygonOffset=old.polygonOffset;
 material.polygonOffsetFactor=old.polygonOffsetFactor;
 material.polygonOffsetUnits=old.polygonOffsetUnits;
 mesh.position.y=old.height;mesh.renderOrder=old.renderOrder;
 texture.minFilter=old.minFilter;texture.magFilter=old.magFilter;
 texture.generateMipmaps=old.generateMipmaps;
 fog.feather=old.feather;
 se206.fogOriginal=null;
}
function se206DecorStop(){
 se206RestoreFog();
 if(se206.mesh){
  scene.remove(se206.mesh);
  se206.mesh.geometry.dispose();
  se206.mesh.material.dispose();
  se206.mesh=null;se206.decorRemoved++;
 }
 se206.texture?.dispose();
 se206.texture=null;se206.canvas=null;se206.ctx=null;
 se206.session=null;se206.stage=0;se206.fogSession=null;
 se206.groundPosition=null;
}
function se206InitDecor(s){
 se206DecorStop();
 const c=document.createElement('canvas');
 c.width=c.height=768;
 const ctx=c.getContext('2d');
 if(!ctx){se206.lastError='Canvas2D unavailable';return;}
 se206.session=s;se206.seed=0x0a041e^Math.round(s.rules.bounds*157);
 se206.canvas=c;se206.ctx=ctx;se206.stage=1;
 ctx.clearRect(0,0,768,768);
 // Four subdued meadow biomes, not high-contrast roads or build outlines.
 // Transparent map overlay preserves the authored ground and road texture.
 for(let i=0;i<28;i++){
  const x=se206Random()*768,y=se206Random()*768;
  const r=22+se206Random()*66;
  const gradient=ctx.createRadialGradient(x,y,0,x,y,r);
  const colors=['#8fbf75','#89b79c','#c9bd83','#8ba8b3'];
  const hex=colors[((x>384)?1:0)+((y>384)?2:0)];
  gradient.addColorStop(0,hex+'24');gradient.addColorStop(1,hex+'00');
  ctx.fillStyle=gradient;ctx.beginPath();ctx.arc(x,y,r,0,Math.PI*2);ctx.fill();
 }
 const meadow=actors.find(a=>a.userData?.actorType==='st-meadow');
 if(meadow?.updateMatrixWorld)meadow.updateMatrixWorld(true);
 const pos=meadow?.getWorldPosition?.(new THREE.Vector3())||new THREE.Vector3();
 se206.groundPosition=pos;
}
function se206PaintSlice(s){
 const ctx=se206.ctx;if(!ctx)return;
 const bounds=Number(s.rules.bounds)||40;
 // 110 very cheap tiny flowers/clover/grass tufts per XR frame.
 // One completed CanvasTexture after 12 passes = one GPU upload.
 for(let i=0;i<110;i++){
  const x=(se206Random()*2-1)*bounds;
  const z=(se206Random()*2-1)*bounds;
  if(!se206RoadClear(x,z,bounds)){se206.avoidedRoads++;continue;}
  const u=(x/bounds+1)*384,v=(z/bounds+1)*384;
  const r=se206Random(),palette=r<.20?'#efe4bc':r<.35?'#d8bf77':
   r<.55?'#7caa78':r<.75?'#a1bf78':'#4b856c';
  ctx.fillStyle=palette+(r<.35?'9c':'75');
  const w=r<.3?1.65:2.9,h=r<.3?2.1:4.2;
  ctx.fillRect(u,v,w,h);
  if(r>.55){
   ctx.fillStyle='#b6cf8c60';
   ctx.fillRect(u+2,v-2,.8,3);
  }
  se206.blooms++;
 }
 se206.stage++;
}
function se206FinishDecor(s){
 const ctx=se206.ctx,bounds=Number(s.rules.bounds)||40;
 if(!ctx)return;
 // Sanctuary approach has a gentle cobbled/flower rim, not a collider ring.
 const center=384,radius=10.7/bounds*384;
 ctx.save();ctx.globalAlpha=.28;
 ctx.setLineDash([2.8,7]);ctx.strokeStyle='#d6d2a1';
 ctx.lineWidth=1.5;ctx.beginPath();ctx.arc(center,center,radius,0,Math.PI*2);
 ctx.stroke();ctx.setLineDash([]);
 ctx.restore();
 const texture=new THREE.CanvasTexture(se206.canvas);
 texture.colorSpace=THREE.SRGBColorSpace;
 texture.minFilter=THREE.LinearMipmapLinearFilter;
 texture.magFilter=THREE.LinearFilter;
 texture.generateMipmaps=true;texture.anisotropy=2;
 const mesh=new THREE.Mesh(
  new THREE.PlaneGeometry(bounds*2,bounds*2),
  new THREE.MeshBasicMaterial({map:texture,transparent:true,opacity:.83,
   depthWrite:false,depthTest:true,polygonOffset:true,
   polygonOffsetFactor:-.5,polygonOffsetUnits:-.7,
   side:THREE.DoubleSide,toneMapped:false})
 );
 mesh.name='Sheep Tag Quest meadow watercolor/floral dressing';
 mesh.userData.sheepTagPreview=true;
 mesh.userData.se206DecorOnly=true; // no game authority, no editor actor
 mesh.rotation.x=-Math.PI/2;
 const pos=se206.groundPosition||new THREE.Vector3();
 mesh.position.set(pos.x,pos.y+.059,pos.z);
 mesh.renderOrder=2;mesh.frustumCulled=true;
 mesh.raycast=function(){}; // decorative layer cannot intercept controller
 scene.add(mesh);
 se206.mesh=mesh;se206.texture=texture;
 se206.canvas=null;se206.ctx=null;se206.stage=14;
 se206.textureUploads++;se206.decorCreated++;
}
function se206AdjustFog(s){
 if(!s?.fog||se206.fogSession===s)return;
 const fog=s.fog;
 // Preserve f.visible / f.explored / player knowledge / fog painting
 // and every host/guest visibility rule. Cosmetic material changes only.
 const mesh=fog.mesh,material=fog.material;
 if(!mesh||!material||!fog.texture)return;
 se206RestoreFog();
 const tex=fog.texture;
 se206.fogOriginal={fog,material,mesh,texture:tex,
  opacity:material.opacity,depthWrite:material.depthWrite,
  depthTest:material.depthTest,polygonOffset:material.polygonOffset,
  polygonOffsetFactor:material.polygonOffsetFactor,
  polygonOffsetUnits:material.polygonOffsetUnits,
  height:mesh.position.y,renderOrder:mesh.renderOrder,
  minFilter:tex.minFilter,magFilter:tex.magFilter,
  generateMipmaps:tex.generateMipmaps,feather:fog.feather};
 fog.texture.minFilter=THREE.LinearFilter;
 fog.texture.magFilter=THREE.LinearFilter;
 fog.texture.generateMipmaps=false;
 material.transparent=true;material.depthWrite=false;material.depthTest=true;
 material.opacity=.84;
 material.polygonOffset=true;material.polygonOffsetFactor=-1;
 material.polygonOffsetUnits=-2;
 mesh.position.y=Math.max(.175,mesh.position.y);
 mesh.renderOrder=3;
 fog.feather=Math.max(2.15,Number(fog.feather)||0);
 se206.fogSession=s;se206.fogSetups++;
}
function se206VisualFrame(){
 se206.frames++;
 if(!se193XRGameActive()||!stSession||stSession.simulate){
  if(se206.session)se206DecorStop();
  return;
 }
 const s=stSession;
 if(s!==se206.session)se206InitDecor(s);
 se206AdjustFog(s);
 if(!se206.ctx||se206.stage>=14)return;
 if(se195.visible||se195.photo||se205OverlayActive()){
  se206.skippedModalFrames++;return;
 }
 const start=performance.now();
 if(se206.stage<=12)se206PaintSlice(s);
 else se206FinishDecor(s);
 se206.paintMs+=performance.now()-start;
}
const se206OldFrame=se193XRFrame;
se193XRFrame=function(){const out=se206OldFrame();se206VisualFrame();return out;};
const se206OldStop=stStop;
stStop=function(...args){se206DecorStop();return se206OldStop(...args);};
const se206OldCleanup=se193XRCleanup;
se193XRCleanup=function(){se206DecorStop();return se206OldCleanup();};
window.SWYRL_ENGINE_SHEEP_MEADOW_FOG_206=Object.freeze({
 diagnose:()=>({
  active:!!se206.session,ready:!!se206.mesh,
  sourceDecorOnly:true,geometryAdded:se206.mesh?1:0,
  biomeBlooms:se206.blooms,roadSitesAvoided:se206.avoidedRoads,
  paintStages:se206.stage,textureUploads:se206.textureUploads,
  decorCreated:se206.decorCreated,decorRemoved:se206.decorRemoved,
  fogVisualSetups:se206.fogSetups,fogOpacity:stSession?.fog?.material?.opacity,
  fogPaintAuthority:'unchanged',modalFramesSkipped:se206.skippedModalFrames,
  paintMs:Math.round(se206.paintMs*100)/100,lastError:se206.lastError
 })
});
