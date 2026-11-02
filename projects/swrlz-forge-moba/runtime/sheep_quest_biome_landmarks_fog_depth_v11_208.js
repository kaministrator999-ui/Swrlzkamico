// §E v11.208 — Sheep Tag Quest Play: four-biome map and fog depth stability.
// Draws exclusively cosmetic layers over the existing *authored* world.
// Saved actors, multiplayer discovery, pathfinding and native collision stay unchanged.
const se208={
 session:null,props:[],species:0,details:0,decorations:0,
 created:0,disposed:0,uploads:0,fogSession:null,fogSetups:0,
 depthRepairs:0,paintPasses:0,landmarks:0,roadHighlights:0,
 budgetSamples:0,drawCalls:0,liveProps:0,sourceActors:0,
 nativeVisionUntouched:true,seed:0x852bd5c1,lastError:''
};
function se208Rand(){
 se208.seed=(Math.imul(se208.seed,1664525)+1013904223)>>>0;
 return se208.seed/4294967296;
}
function se208CanvasCoord(x,z,bounds){
 return [384*(1+x/bounds),384*(1+z/bounds)];
}
function se208ArtBase(s){
 const ctx=se206.ctx,canvas=se206.canvas;
 if(!ctx||!canvas)return;
 const b=s.rules.bounds||40,sc=384/b;
 // Each quadrant has its own restrained material language, with soft
 // transitions instead of arbitrary large opaque color rectangles.
 const zones=[
  {x:-.53,z:-.54,color:'#477e76',name:'PINEWATCH'},
  {x:.53,z:-.54,color:'#7b8ea1',name:'MOONFLOWER'},
  {x:-.53,z:.54,color:'#a49a64',name:'AMBERGLADE'},
  {x:.53,z:.54,color:'#6f9f8b',name:'WILLOWMERE'}
 ];
 for(const zone of zones){
  const [cx,cy]=se208CanvasCoord(zone.x*b,zone.z*b,b);
  const radius=268;
  const gradient=ctx.createRadialGradient(cx,cy,18,cx,cy,radius);
  gradient.addColorStop(0,zone.color+'38');
  gradient.addColorStop(.64,zone.color+'1f');
  gradient.addColorStop(1,zone.color+'00');
  ctx.fillStyle=gradient;
  ctx.fillRect(Math.max(0,cx-radius),Math.max(0,cy-radius),
    Math.min(768-cx+radius,radius*2),Math.min(768-cy+radius,radius*2));
 }
 // Path shoulders follow the source 80m meadow's *authored* cross and four
 // diagonals; for 128m Wildwood, leave its existing 4K texture's road shapes.
 if(Math.abs(b-40)<.1){
  ctx.save();
  ctx.lineCap='round';ctx.lineJoin='round';
  for(const pts of [
   [[0,-36],[0,36]],[[-36,0],[36,0]],
   [[-34,-30],[-22,-24],[-10,-12],[0,0]],
   [[34,-30],[22,-24],[10,-12],[0,0]],
   [[-34,30],[-22,24],[-10,12],[0,0]],
   [[34,30],[22,24],[10,12],[0,0]]
  ]){
   ctx.beginPath();
   pts.forEach(([x,z],i)=>{
    const [px,py]=se208CanvasCoord(x,z,b);
    if(i===0)ctx.moveTo(px,py);else ctx.lineTo(px,py);
   });
   ctx.strokeStyle='#e4d7ae40';ctx.lineWidth=3.5*sc;
   ctx.stroke();
   ctx.strokeStyle='#856e4b20';ctx.lineWidth=2.8*sc;
   ctx.stroke();
   se208.roadHighlights++;
  }
  ctx.restore();
 }
}
function se208ArtSlice(s){
 const ctx=se206.ctx,b=s.rules.bounds||40;
 if(!ctx)return;
 ctx.save();
 // Palette per quadrant. Paint one cheap small patch per sample, with
 // no additional CanvasTexture upload until v11.206 finishes all slices.
 for(let i=0;i<95;i++){
  const x=(se208Rand()*2-1)*b,z=(se208Rand()*2-1)*b;
  if(!se206RoadClear(x,z,b))continue;
  const [u,v]=se208CanvasCoord(x,z,b);
  const region=(x<0?0:1)+(z>=0?2:0);
  const palette=[
   ['#c3d7ac','#6d927e','#f0dba7'],
   ['#b7cdcf','#7a9eac','#e8d2cb'],
   ['#d4c59b','#a0a767','#e3b97b'],
   ['#afceb2','#74ad95','#d4e1bb']
  ][region];
  const r=se208Rand();
  const radius=(r<.28?4:2.1)*(.55+se208Rand());
  ctx.fillStyle=palette[Math.floor(se208Rand()*3)]+(r<.25?'48':'2b');
  ctx.beginPath();ctx.ellipse(u,v,radius,radius*.43,
   se208Rand()*Math.PI,0,Math.PI*2);
  ctx.fill();se208.details++;
 }
 ctx.restore();
 se208.paintPasses++;
}
function se208ArtFinish(s){
 const ctx=se206.ctx,b=s.rules.bounds||40;if(!ctx)return;
 ctx.save();ctx.textAlign='center';ctx.textBaseline='middle';
 const sigils=[
  {x:-.58,z:-.58,c:'#d0e7c1',symbol:'✦',label:'PINEWATCH'},
  {x:.58,z:-.58,c:'#c0e4e5',symbol:'✧',label:'MOONFLOWER'},
  {x:-.58,z:.58,c:'#efdfa7',symbol:'✺',label:'AMBERGLADE'},
  {x:.58,z:.58,c:'#bfe4d0',symbol:'❖',label:'WILLOWMERE'}
 ];
 for(const p of sigils){
  const [cx,cy]=se208CanvasCoord(b*p.x,b*p.z,b);
  ctx.save();ctx.globalAlpha=.42;
  ctx.fillStyle='#31453d';ctx.strokeStyle=p.c;ctx.lineWidth=1.5;
  ctx.beginPath();ctx.arc(cx,cy,19,0,Math.PI*2);ctx.fill();ctx.stroke();
  ctx.beginPath();ctx.arc(cx,cy,15,0,Math.PI*2);ctx.stroke();
  for(let k=0;k<8;k++){
   const angle=k*Math.PI/4;
   ctx.beginPath();ctx.moveTo(cx+Math.cos(angle)*16,cy+Math.sin(angle)*16);
   ctx.lineTo(cx+Math.cos(angle)*23,cy+Math.sin(angle)*23);ctx.stroke();
  }
  ctx.font='bold 15px sans-serif';ctx.fillStyle=p.c;
  ctx.fillText(p.symbol,cx,cy+1);
  ctx.font='bold 10px sans-serif';
  ctx.fillText(p.label,cx,cy+34);
  ctx.restore();se208.landmarks++;
 }
 // A slightly textured sanctuary approach matches the already-authored pen.
 // This is a low-opacity *art motif*, never a navigational collision radius.
 const [sx,sy]=se208CanvasCoord(0,0,b),r=10.7/b*384;
 ctx.save();ctx.globalAlpha=.23;ctx.lineWidth=2;
 ctx.strokeStyle='#e8e0bd';
 ctx.setLineDash([3,9]);ctx.beginPath();
 ctx.arc(sx,sy,r,0,Math.PI*2);ctx.stroke();
 ctx.setLineDash([]);ctx.restore();
 ctx.restore();
}
function se208Dispose(){
 for(const mesh of se208.props){
  scene.remove(mesh);
  mesh.geometry?.dispose();
  mesh.material?.dispose();
  se208.disposed++;
 }
 se208.props.length=0;se208.session=null;se208.liveProps=0;
 se208.fogSession=null;
}
function se208WorldPoints(s){
 // Only around existing authored trees, rocks and ponds: new geometry
 // cannot pretend to be a collidable building or obstruct a sheep's view.
 const bounds=Number(s.rules.bounds)||40,leaves=[],stones=[],plants=[];
 se208.seed=(0xd551c82e^Math.round(bounds*24))>>>0;
 const candidates=actors.filter(a=>['st-tree','st-rock','st-pond'].includes(
  a?.userData?.actorType)).slice(0,90);
 se208.sourceActors=candidates.length;
 for(const actor of candidates){
  actor.updateWorldMatrix?.(true,false);
  const p=actor.getWorldPosition?.(new THREE.Vector3());
  if(!p||!Number.isFinite(p.x)||!Number.isFinite(p.z))continue;
  const kind=actor.userData.actorType;
  const n=kind==='st-tree'?6:kind==='st-rock'?4:5;
  for(let i=0;i<n;i++){
   const a=se208Rand()*Math.PI*2;
   const distance=(kind==='st-pond'?3.1:kind==='st-tree'?1.95:1.4)+se208Rand()*1.2;
   const x=p.x+Math.cos(a)*distance,z=p.z+Math.sin(a)*distance;
   if(Math.abs(x)>bounds-1.2||Math.abs(z)>bounds-1.2||
      !se206RoadClear(x,z,bounds))continue;
   const entry={x,z,angle:se208Rand()*Math.PI*2,size:.55+se208Rand()*.65,
    color:(x<0?0:1)+(z>=0?2:0)};
   if(kind==='st-rock'||kind==='st-pond')stones.push(entry);
   else (i%3===0?plants:leaves).push(entry);
  }
 }
 return {leaves:leaves.slice(0,160),stones:stones.slice(0,100),
  plants:plants.slice(0,90)};
}
function se208AddInstances(list,geometry,baseColor,colors,name,yScale){
 if(!list.length){geometry.dispose();return;}
 const material=new THREE.MeshBasicMaterial({
  color:baseColor,vertexColors:true,side:THREE.DoubleSide,
  transparent:true,opacity:.84,depthWrite:false,depthTest:true,
  polygonOffset:true,polygonOffsetFactor:-1,polygonOffsetUnits:-1,
  toneMapped:false
 });
 const mesh=new THREE.InstancedMesh(geometry,material,list.length);
 mesh.name=name;mesh.userData.sheepTagPreview=true;
 mesh.userData.se208VisualOnly=true;mesh.renderOrder=2;
 mesh.castShadow=false;mesh.receiveShadow=false;
 mesh.raycast=function(){}; // world-picking/house previews never hit foliage
 const pivot=new THREE.Object3D(),matrix=new THREE.Matrix4();
 const color=new THREE.Color();
 for(let i=0;i<list.length;i++){
  const v=list[i],y=terrainHeight(v.x,v.z);
  pivot.position.set(v.x,y+.073,v.z);
  pivot.quaternion.setFromAxisAngle(new THREE.Vector3(0,1,0),v.angle);
  pivot.scale.set(v.size,yScale*v.size,v.size);
  pivot.updateMatrix();
  matrix.copy(pivot.matrix);
  mesh.setMatrixAt(i,matrix);
  mesh.setColorAt(i,color.set(colors[v.color]));
 }
 mesh.instanceMatrix.needsUpdate=true;
 if(mesh.instanceColor)mesh.instanceColor.needsUpdate=true;
 mesh.computeBoundingSphere?.();
 mesh.frustumCulled=true;
 scene.add(mesh);se208.props.push(mesh);
 se208.created++;se208.liveProps++;
 se208.species+=list.length;
}
function se208MakeProps(s){
 if(!s||se208.session===s)return;
 se208Dispose();
 const points=se208WorldPoints(s);
 // Low polygon silhouettes: 3 draw calls total for scattered land detail.
 se208AddInstances(points.leaves,
  new THREE.IcosahedronGeometry(.18,0),'#ffffff',
  ['#729d72','#7fa5a6','#b3a05c','#5b9c83'],
  'Pinewatch/Moonflower/Amberglade/Willowmere fallen leaves',.20);
 se208AddInstances(points.stones,
  new THREE.DodecahedronGeometry(.19,0),'#ffffff',
  ['#83938a','#a0adb5','#afaa8b','#8caca5'],
  'Moss and riverbank pebble clusters',.32);
 se208AddInstances(points.plants,
  new THREE.ConeGeometry(.15,.3,5),'#ffffff',
  ['#7eae7c','#96b2b9','#c1b57f','#75b49e'],
  'Small meadow wildflower stalks',.75);
 se208.session=s;se208.uploads++;
}
function se208TightenFog(s){
 if(!s?.fog?.mesh||se208.fogSession===s)return;
 const fog=s.fog,mesh=fog.mesh,material=fog.material;
 // The v11.206 fog state snapshot still owns restoration to desktop state.
 // Raise plane slightly above meadow overlays to minimize depth-precision
 // competition on Quest, without touching fog mask bytes or team painters.
 mesh.position.y=Math.max(mesh.position.y,.24);
 material.depthTest=true;material.depthWrite=false;
 material.polygonOffset=true;material.polygonOffsetFactor=-2.5;
 material.polygonOffsetUnits=-3;
 mesh.renderOrder=14;
 se208.fogSession=s;se208.fogSetups++;se208.depthRepairs++;
}
const se208OldInit=se206InitDecor;
se206InitDecor=function(s){
 const result=se208OldInit(s);
 if(se206.ctx)se208ArtBase(s);
 return result;
};
const se208OldSlice=se206PaintSlice;
se206PaintSlice=function(s){
 const result=se208OldSlice(s);
 if(se206.ctx)se208ArtSlice(s);
 return result;
};
const se208OldFinish=se206FinishDecor;
se206FinishDecor=function(s){
 if(se206.ctx)se208ArtFinish(s);
 return se208OldFinish(s);
};
const se208OldFog=se206AdjustFog;
se206AdjustFog=function(s){
 const result=se208OldFog(s);
 se208TightenFog(s);
 return result;
};
const se208OldDecorStop=se206DecorStop;
se206DecorStop=function(){
 se208Dispose();
 return se208OldDecorStop();
};
const se208OldFrame=se193XRFrame;
se193XRFrame=function(){
 const result=se208OldFrame();
 if(se193XRGameActive()&&se206.mesh&&stSession&&!stSession.simulate&&
    se208.session!==stSession)se208MakeProps(stSession);
 if(++se208.budgetSamples%120===0)
  se208.drawCalls=renderer.info?.render?.calls??0;
 return result;
};
window.SWYRL_ENGINE_SHEEP_BIOMES_208=Object.freeze({
 diagnose:()=>({
  active:se208.session===stSession&&!!se206.mesh,
  quadrantNames:['Pinewatch','Moonflower','Amberglade','Willowmere'],
  roadHighlights:se208.roadHighlights,regionLandmarks:se208.landmarks,
  paintedGroundDetails:se208.details,
  instancedDrawCalls:se208.liveProps,instances:se208.species,
  sourceAuthoredProps:se208.sourceActors,
  instanceBuffersUploaded:se208.uploads,decorationsDisposed:se208.disposed,
  fogDepthGuards:se208.depthRepairs,fogHeight:stSession?.fog?.mesh?.position?.y,
  fogPainter:'original native solo/team unchanged',
  navVersion:stSession?.navVersion??null,
  sceneDrawCalls:se208.drawCalls,sourceActorsUnchanged:true,
  lastError:se208.lastError
 })
});
