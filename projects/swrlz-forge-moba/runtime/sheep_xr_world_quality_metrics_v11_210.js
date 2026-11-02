// §E v11.210 · Sheep Tag Play visual remaster and measurable Quest rendering budget.
// Adds small instanced 3D landmark dressing, never map actors, colliders, or visibility.
// Quality presets adjust ONLY cosmetic content, not simulation/authority/fog masks.
const se210World={
 session:null,meshes:[],mode:'balanced',autoLow:false,
 created:0,disposed:0,landmarks:0,frames:0,frameMs:16.7,
 minFps:Infinity,fps:0,frameBuffer:[],lastReportAt:0,lowSince:0,highSince:0,
 drawCalls:0,triangles:0,textures:0,geometries:0,visibleActors:0,
 fogPaintMs:0,fogSamples:0,fogUploads:0,overlayFrames:0,
 lastOverlay:'visible',manualProfile:'balanced',lastError:''
};
function se210DecorVisible(){
 return se210World.mode!=='performance'&&!se210World.autoLow&&
   se193XRGameActive()&&!se205OverlayActive();
}
function se210Quality(mode){
 if(!['performance','balanced','quality','auto'].includes(mode))return false;
 se210World.mode=mode;
 se210World.manualProfile=mode;se210World.autoLow=false;
 se210World.lowSince=se210World.highSince=0;
 se210WorldRefreshVisibility();
 return true;
}
function se210WorldRefreshVisibility(){
 const show=se210DecorVisible();
 for(const m of se210World.meshes)m.visible=show;
 if(Array.isArray(se208?.props))
  for(const p of se208.props)p.visible=show;
 if(se209?.icons){} // cached menu textures never reallocate here
}
function se210WorldDispose(){
 for(const m of se210World.meshes){
  scene.remove(m);m.geometry.dispose();m.material.dispose();
  se210World.disposed++;
 }
 se210World.meshes.length=0;se210World.session=null;
}
function se210WorldInstances(defs,geometry,color,name){
 if(!defs.length){geometry.dispose();return}
 const material=new THREE.MeshBasicMaterial({
  color,transparent:true,opacity:.90,depthTest:true,depthWrite:true,
  side:THREE.DoubleSide,toneMapped:false
 });
 const mesh=new THREE.InstancedMesh(geometry,material,defs.length);
 mesh.name=name;mesh.userData.se210Cosmetic=true;
 mesh.userData.sheepTagPreview=true;
 mesh.castShadow=false;mesh.receiveShadow=false;mesh.frustumCulled=true;
 mesh.raycast=function(){};
 const pivot=new THREE.Object3D(),axis=new THREE.Vector3(0,1,0);
 defs.forEach((p,i)=>{
  pivot.position.set(p.x,terrainHeight(p.x,p.z)+p.y,p.z);
  pivot.quaternion.setFromAxisAngle(axis,p.angle||0);
  pivot.scale.set(p.size||1,p.height||1,p.size||1);
  pivot.updateMatrix();
  mesh.setMatrixAt(i,pivot.matrix);
 });
 mesh.instanceMatrix.needsUpdate=true;
 mesh.computeBoundingSphere?.();
 scene.add(mesh);se210World.meshes.push(mesh);
 se210World.created++;se210World.landmarks+=defs.length;
}
function se210WorldInit(s){
 if(!s||se210World.session===s)return;
 se210WorldDispose();
 if(!se193XRGameActive()||s.simulate)return;
 // Group signs at the OUTER forest periphery, not the construction grid.
 // Existing village, tree/pond collision and sanctuary are authoritative.
 const bounds=Number(s.rules.bounds)||40;
 if(!Number.isFinite(bounds)||bounds<18)return;
 const positions=[];
 for(let i=0;i<12;i++){
  const angle=i*Math.PI/6+.22;
  const x=Math.cos(angle)*bounds*.91,z=Math.sin(angle)*bounds*.91;
  // World detail, not a fake walkable-house footprint.
  if(!se206RoadClear(x,z,bounds))continue;
  positions.push({x,z,y:.52,size:.62,height:1.3,angle});
 }
 const tops=positions.map(p=>({...p,y:1.34,height:.28,size:.48}));
 se210WorldInstances(positions,
  new THREE.CylinderGeometry(.085,.12,1,6),
  0x897458,'Quest VR biome waymarker timber posts');
 se210WorldInstances(tops,
  new THREE.OctahedronGeometry(.19,0),
  0x9ed4bf,'Quest VR biome waymarker crystal lamps');
 se210World.session=s;se210WorldRefreshVisibility();
}
function se210WorldSample(now){
 const w=se210World;
 const dt=now-(w.lastReportAt||now);
 if(dt>0&&dt<150){
  w.frameBuffer.push(dt);if(w.frameBuffer.length>90)w.frameBuffer.shift();
 }
 w.lastReportAt=now;w.frames++;
 if(w.frames%60!==0)return;
 if(w.frameBuffer.length){
  const sum=w.frameBuffer.reduce((a,b)=>a+b,0);
  w.frameMs=sum/w.frameBuffer.length;
  w.fps=Math.round(1000/w.frameMs);
  w.minFps=Math.min(w.minFps,w.fps);
 }
 const info=renderer?.info;
 w.drawCalls=info?.render?.calls??0;
 w.triangles=info?.render?.triangles??0;
 w.textures=info?.memory?.textures??0;
 w.geometries=info?.memory?.geometries??0;
 w.visibleActors=(Array.isArray(actors)?actors.filter(a=>a.visible).length:0);
 if(w.mode==='auto'&&w.frameBuffer.length>=45){
  // Conservative quality reduction after 2s of persistently poor frame rate.
  if(w.fps<52){
   if(!w.lowSince)w.lowSince=now;
   if(now-w.lowSince>2200){w.autoLow=true;se210WorldRefreshVisibility();}
   w.highSince=0;
  }else if(w.fps>68){
   if(!w.highSince)w.highSince=now;
   if(now-w.highSince>9500){
    w.autoLow=false;w.lowSince=0;se210WorldRefreshVisibility();
   }
  }else w.lowSince=w.highSince=0;
 }
}
function se210WorldFrame(){
 const now=performance.now();
 if(!se193XRGameActive()){
  if(se210World.session)se210WorldDispose();
  return;
 }
 if(stSession&&!stSession.simulate&&se206.mesh)se210WorldInit(stSession);
 const obscured=se205OverlayActive();
 if(obscured)se210World.overlayFrames++;
 // An OS overlay gets immediate cosmetic throttling instead of waiting
 // for the next 60-frame counter. Preserve native XR camera and network.
 if(obscured!==se210World.lastOverlay){
  se210World.lastOverlay=obscured;
  se210WorldRefreshVisibility();
 }
 se210WorldSample(now);
 if(se210World.frames%60===0)se210WorldRefreshVisibility();
}
const se210WorldPrevFrame=se193XRFrame;
se193XRFrame=function(){
 const result=se210WorldPrevFrame();
 se210WorldFrame();
 return result;
};
const se210WorldPrevFogSolo=stSoftFogPaint;
stSoftFogPaint=function(s){
 const now=performance.now();
 const result=se210WorldPrevFogSolo(s);
 if(se193XRGameActive()){
  se210World.fogPaintMs+=performance.now()-now;
  se210World.fogSamples++;
 }
 return result;
};
const se210WorldPrevFogTeam=se156PaintTeamFog;
se156PaintTeamFog=function(s,force=false){
 const now=performance.now(),tex=s?.fog?.texture;
 const before=tex?.version;
 const result=se210WorldPrevFogTeam(s,force);
 if(se193XRGameActive()){
  se210World.fogPaintMs+=performance.now()-now;
  se210World.fogSamples++;
  if(tex&&tex.version!==before)se210World.fogUploads++;
 }
 return result;
};
const se210WorldPrevCleanup=se193XRCleanup;
se193XRCleanup=function(){
 se210WorldDispose();
 return se210WorldPrevCleanup();
};
const se210WorldPrevStop=stStop;
stStop=function(...args){
 se210WorldDispose();
 return se210WorldPrevStop(...args);
};
window.SWYRL_ENGINE_QUEST_PERFORMANCE_210=Object.freeze({
 diagnose:()=>({
  xr:se193XRGameActive(),fps:se210World.fps,
  avgFrameMs:+se210World.frameMs.toFixed(2),
  lowestSampleFps:Number.isFinite(se210World.minFps)?se210World.minFps:0,
  rendererDrawCalls:se210World.drawCalls,triangles:se210World.triangles,
  gpuTextureCount:se210World.textures,gpuGeometryCount:se210World.geometries,
  authoredActorsVisible:se210World.visibleActors,
  fogUpdateCpuMs:+se210World.fogPaintMs.toFixed(1),
  fogSampleCalls:se210World.fogSamples,fogTextureUploads:se210World.fogUploads,
  systemOverlayFrames:se210World.overlayFrames,
  cosmeticQuality:se210World.mode,autoReduced:se210World.autoLow,
  worldLandmarks3d:se210World.landmarks,extraDrawCalls:se210World.meshes.length,
  noPhysicsOrVisibilityChanges:true
 }),
 setQuality:se210Quality
});
