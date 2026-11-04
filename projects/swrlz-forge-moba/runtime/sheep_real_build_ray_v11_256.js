// §E v11.256: literal right-controller ground aim, no synthetic sheep-relative beam.
(function(){
'use strict';
const stats={samples:0,groundHits:0,misses:0,menuHits:0};
const down=new THREE.Vector3(0,-1,0);
se203GroundFromForwardRay=function(){return null;};
const physicalGround=se193XRGameGround;
se193XRGameGround=function(record){
 if(!se193XRGameActive()||se195.visible||se195.photo||se204.wheel?.root?.visible)return null;
 const cast=se192Ray(record);
 if(!cast?.origin||!cast?.direction||cast.direction.y>=-.018)return null;
 const origin=cast.origin,dir=cast.direction;
 const bounds=stSession?.rules?.bounds??120;
 let t=(terrainHeight(origin.x,origin.z)-origin.y)/dir.y;
 for(let i=0;i<3;i++){
  if(!Number.isFinite(t)||t<.025||t>220)return null;
  const x=origin.x+dir.x*t,z=origin.z+dir.z*t;
  if(!Number.isFinite(x)||!Number.isFinite(z))return null;
  t=(terrainHeight(x,z)-origin.y)/dir.y;
 }
 const x=origin.x+dir.x*t,z=origin.z+dir.z*t;
 if(!Number.isFinite(x)||!Number.isFinite(z)||Math.abs(x)>bounds||Math.abs(z)>bounds)return null;
 return new THREE.Vector3(x,terrainHeight(x,z),z);
};
const previousRaycast=se192Raycast;
se192Raycast=function(record){
 if(!se193XRGameActive()||!stUi.build||se195.visible||se195.photo||se204.wheel?.root?.visible)
  return previousRaycast(record);
 // Existing independent menus and exit controls retain selection priority.
 const prior=previousRaycast(record);
 if(prior?.ui||prior?.exit)return prior;
 stats.samples++;
 const cast=se192Ray(record),point=se193XRGameGround(record);
 if(point&&cast){
  stats.groundHits++;
  return {ground:true,distance:point.distanceTo(cast.origin),point};
 }
 stats.misses++;
 return {empty:true,distance:3.5};
};
const previousRender=se192RenderRay;
se192RenderRay=function(record,hit){
 const result=previousRender(record,hit);
 if(!se193XRGameActive()||!record?.se192)return result;
 const {beam,dot}=record.se192;
 if(typeof se203GroundGuideHide==='function')se203GroundGuideHide();
 const modal=!!se204.wheel?.root?.visible||!!se195.visible;
 const cast=se192Ray(record);
 if(modal){
  beam.visible=true;beam.renderOrder=11100;
  beam.material.depthTest=false;beam.material.depthWrite=false;
  const d=THREE.MathUtils.clamp(Number(hit?.distance)||1.1,.06,3.2);
  beam.scale.z=d;
  if(hit?.point&&cast){
   dot.position.copy(hit.point).addScaledVector(cast.direction,-.018);
   dot.visible=true;dot.scale.setScalar(.7);dot.lookAt(cast.origin);
   stats.menuHits++;
  }else dot.visible=false;
  for(const ring of dot.children){
   ring.renderOrder=11110;ring.material.depthTest=false;ring.material.depthWrite=false;
  }
  if(record.ray)record.ray.visible=false;
 }else{
  beam.renderOrder=9999;
  for(const ring of dot.children)ring.renderOrder=10002;
  if(stUi.build){
   beam.visible=true;
   const point=hit?.ground?hit.point:null;
   beam.scale.z=point&&cast?Math.min(220,point.distanceTo(cast.origin)):3.5;
   if(point&&cast){
    dot.position.copy(point);dot.lookAt(cast.origin);dot.visible=true;
   }else dot.visible=false;
  }
 }
 return result;
};
const previousFrame=se193XRFrame;
se193XRFrame=function(){
 const result=previousFrame();
 if(se193XRGameActive()&&stUi.build){
  const hand=se192InputRecord('right');
  if(!hand||!se193XRGameGround(hand)){
   if(stUi.preview)stUi.preview.visible=false;
   if(stUi.footprint)stUi.footprint.visible=false;
   stUi.placement=null;
  }
 }
 return result;
};
window.SWYRL_ENGINE_SHEEP_BUILD_RAY_256=Object.freeze({
 diagnose:()=>({...stats,physicalControllerRay:true,syntheticBeam:false,menuCursorRenderOrder:11110})
});
})();