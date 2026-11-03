// §E v11.237 candidate — Sheep Tag Quest stereo visual consistency.
// Do not alter WebXR eye matrices, native HMD tracking, camera anchors,
// fog visibility, simulation, collision, controller input, or editor meshes.
const se237={
  session:null,unit:null,unitMeshCount:0,
  sceneCull:new Map(),characterCull:new Map(),cosmeticDepth:new Map(),
  checks:0,characterGuards:0,groundGuards:0,fogGuards:0,
  transparentDepthGuards:0,restores:0,lastCheck:0,lastError:''
};
function se237ProtectMesh(mesh,map){
  if(!mesh?.isMesh||map.has(mesh))return false;
  map.set(mesh,mesh.frustumCulled);
  mesh.frustumCulled=false;
  return true;
}
function se237RestoreMap(map,key){
  for(const [node,old] of map){
    if(node)node[key]=old;
  }
  map.clear();
}
function se237Release(){
  se237RestoreMap(se237.sceneCull,'frustumCulled');
  se237RestoreMap(se237.characterCull,'frustumCulled');
  se237RestoreMap(se237.cosmeticDepth,'depthWrite');
  se237.session=null;se237.unit=null;
  se237.unitMeshCount=0;se237.lastCheck=0;
  se237.restores++;
}
function se237ProtectCharacter(s){
  const unit=s?.units?.find(u=>u.id===s.controlledId)||null;
  if(unit===se237.unit)return;
  se237RestoreMap(se237.characterCull,'frustumCulled');
  se237.unit=unit;se237.unitMeshCount=0;
  if(!unit?.actor||!['sheep','wolf'].includes(unit.kind))return;
  // Multi-piece organic model: per-mesh frustum tests can disagree at the
  // edges of stereo views while pivots/LOD move. Limit to the controlled
  // character, not every flock member or the entire authored scene.
  const model=unit.actor.getObjectByName('Clover · organic starter sheep')||
    unit.actor.getObjectByName('AstraCometCourier')||unit.actor;
  model.traverse(node=>{
    if(node.isMesh&&se237ProtectMesh(node,se237.characterCull)){
      se237.unitMeshCount++;se237.characterGuards++;
    }
  });
}
function se237ProtectWorld(s){
  const fog=s?.fog?.mesh;
  if(fog&&se237ProtectMesh(fog,se237.sceneCull))se237.fogGuards++;
  if(se206?.mesh&&se237ProtectMesh(se206.mesh,se237.sceneCull))
    se237.groundGuards++;
  // Ground is one plane; never disable culling for hundreds of forest meshes.
  const names=new Set(['stMeadowGround','MoonbellWildwoodGround']);
  for(const actor of actors||[]){
    if(actor?.userData?.actorType!=='st-meadow')continue;
    actor.traverse(node=>{
      if(node.isMesh&&names.has(node.name)&&
         se237ProtectMesh(node,se237.sceneCull))se237.groundGuards++;
    });
  }
  // A transparent *cosmetic* waymarker used to write the depth buffer even
  // with opacity < 1. It could punch holes in fog and underlying scene art.
  // The true game fog mesh retains its existing depthTest/depthWrite rules.
  for(const mesh of se210World?.meshes||[]){
    const mat=mesh?.material;
    if(mat?.transparent&&mat.depthWrite!==false&&!se237.cosmeticDepth.has(mat)){
      se237.cosmeticDepth.set(mat,mat.depthWrite);
      mat.depthWrite=false;
      se237.transparentDepthGuards++;
    }
  }
}
function se237Frame(){
  if(!se193XRGameActive()||!renderer.xr.isPresenting||
     (typeof se211Paused==='function'&&se211Paused())){
    if(se237.session)se237Release();
    return;
  }
  const s=stSession,now=performance.now();
  if(se237.session!==s){se237Release();se237.session=s;}
  // No per-frame scene traversal, bounding box recompute or GPU reupload.
  if(now-se237.lastCheck<240&&se237.unit?.id===s.controlledId)return;
  se237.lastCheck=now;se237.checks++;
  try{se237ProtectCharacter(s);se237ProtectWorld(s);}
  catch(error){se237.lastError=String(error?.message||error).slice(0,150);}
}
const se237PriorFrame=se193XRFrame;
se193XRFrame=function(){
  const out=se237PriorFrame();
  se237Frame();
  return out;
};
const se237PriorCleanup=se193XRCleanup;
se193XRCleanup=function(){
  se237Release();
  return se237PriorCleanup();
};
const se237PriorStop=stStop;
stStop=function(...args){
  se237Release();
  return se237PriorStop(...args);
};
window.SWYRL_ENGINE_QUEST_STEREO_GUARD_237=Object.freeze({
  diagnose:()=>({
    active:se237.session===stSession&&se193XRGameActive(),
    guardedControlledCharacter:se237.unit?.id||null,
    characterMeshes:se237.unitMeshCount,
    activeGroundFogMeshes:se237.sceneCull.size,
    activeCosmeticMaterials:se237.cosmeticDepth.size,
    characterCullGuards:se237.characterGuards,
    fogCullGuards:se237.fogGuards,
    groundCullGuards:se237.groundGuards,
    transparentCosmeticDepthGuards:se237.transparentDepthGuards,
    visualChecks:se237.checks,cleanupCount:se237.restores,
    nativeHeadsetTrackingChanged:false,
    visibilityMasksChanged:false,
    cameraProjectionChanged:false,lastError:se237.lastError
  })
});
