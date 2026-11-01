// §E v11.197: one meadow texture, one authoritative fog painter,
// and direct scene-state camera tracking for native Sheep Tag gameplay.
// All state remains in existing §E scenes; no second render/update loop.
const se197={flatCameraFrames:0,avoidedCameraSnapshots:0,
 multiplayerFogOverrides:0,groundMipFilter:'mipmapped',
 previousProject:null,lastError:''};
const se197CameraPrevious=stUpdateCamera;
stUpdateCamera=function(dt=0){
 if(!stSession||stSession.simulate)return;
 // v11.195 deliberately disables the 2D camera inside WebXR.
 if(se195Gameplay())return;
 const s=stSession;
 const keyX=Number(stUi.keys.has('d')||stUi.keys.has('arrowright'))-
  Number(stUi.keys.has('a')||stUi.keys.has('arrowleft'));
 const keyZ=Number(stUi.keys.has('s')||stUi.keys.has('arrowdown'))-
  Number(stUi.keys.has('w')||stUi.keys.has('arrowup'));
 if(keyX||keyZ){
  stUi.follow=false;
  stUi.focus.x+=keyX*Math.min(Math.max(0,Number(dt)||0),.05)*22*stUi.zoom;
  stUi.focus.z+=keyZ*Math.min(Math.max(0,Number(dt)||0),.05)*22*stUi.zoom;
 }
 const controlled=s.units.find(u=>u.id===s.controlledId);
 const selected=s.units.find(u=>u.id===s.selectedId);
 if(stUi.follow){
  const focus=selected||controlled;
  const pos=focus?.spirit?.position||focus?.pos;
  if(pos)stUi.focus.set(pos.x,0,pos.z);
 }
 const bounds=Number(s.rules?.bounds)||40;
 stUi.focus.x=THREE.MathUtils.clamp(stUi.focus.x,-bounds,bounds);
 stUi.focus.z=THREE.MathUtils.clamp(stUi.focus.z,-bounds,bounds);
 const portraitFit=Math.max(1,Math.min(1.35,.7/Math.max(.3,perspectiveCamera.aspect)));
 const zoom=stUi.zoom*portraitFit;
 if(perspectiveCamera.fov!==50){
  perspectiveCamera.fov=50;
  perspectiveCamera.updateProjectionMatrix();
 }
 perspectiveCamera.up.set(0,1,0);
 perspectiveCamera.position.set(stUi.focus.x,32*zoom,stUi.focus.z+25*zoom);
 perspectiveCamera.lookAt(stUi.focus);
 perspectiveCamera.updateMatrixWorld(true);
 // The old 60-Hz camera called stStatus(), building a complete snapshot
 // of AI memories, fog, buildings and every sheep purely to draw two rings.
 // Feed the original ring artist the two relevant native entities only.
 const ids=new Set([s.controlledId,s.selectedId].filter(Boolean));
 const units=s.units.filter(u=>ids.has(u.id)).map(u=>{
  const p=u.spirit?.position||u.pos;
  return {id:u.id,kind:u.kind,pos:[p.x,p.y,p.z]};
 });
 const buildings=s.buildings.filter(b=>b.hp>0&&ids.has(b.id))
  .map(b=>({id:b.id,kind:b.kind,pos:[b.pos.x,b.pos.y,b.pos.z]}));
 stUiUpdateRings({controlledId:s.controlledId,selectedId:s.selectedId,units,buildings});
 se197.flatCameraFrames++;se197.avoidedCameraSnapshots++;
};
// Multiplayer has a separate team-vision compositor which preserves
// visibility and explores territory shared by teammate houses. Never
// overwrite it with the solo soft-fog painter on an intervening frame.
const se197SoftFogPrevious=stSoftFogPaint;
stSoftFogPaint=function(s){
 if(s?.fog&&typeof se150Match!=='undefined'&&se150Match.active){
  se197.multiplayerFogOverrides++;
  return;
 }
 return se197SoftFogPrevious(s);
};
function se197MeadowInfo(){
 let info=null;
 for(const actor of actors){
  actor.traverse(o=>{
   if(o.name!=='stMeadowGround'&&o.name!=='MoonbellWildwoodGround')return;
   const tex=o.material?.map;
   info={name:o.name,mipmapped:tex?.minFilter===THREE.LinearMipmapLinearFilter,
    anisotropy:tex?.anisotropy||0,generateMipmaps:!!tex?.generateMipmaps,
    textureWidth:tex?.image?.width||tex?.image?.naturalWidth||0,
    questDownsampled:!!tex?.userData?.se197QuestDownsampled};
  });
  if(info)break;
 }
 return info;
}
window.SWYRL_ENGINE_SHEEP_VISUAL_197=Object.freeze({
 diagnose:()=>({
  version:'v11.197',cameraFrames:se197.flatCameraFrames,
  avoidedFullStatusSnapshots:se197.avoidedCameraSnapshots,
  multiplayerFogOverwritePrevented:se197.multiplayerFogOverrides,
  visualFogDepth:stSession?.fog?.mesh?.position?.y??null,
  meadow:se197MeadowInfo(),
  active:!!stSession,renderCalls:renderer.info?.render?.calls??null,
  lastError:se197.lastError
 })
});