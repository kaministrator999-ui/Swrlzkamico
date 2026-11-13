/* SE434_ENGINE_EDITOR_SHADOW_CACHE_START */
// The editor's camera can move without changing light-space depth. Reuse a
// static shadow map only after checking native casters/lights, never in Play.
const se434Shadows={frames:0,reused:0,refreshed:0,fallback:0,casters:0};
const se434ShadowObjects=new WeakMap(),se434ShadowLights=new WeakMap();
let se434ShadowScene=null,se434ShadowCount=-1,se434ShadowLightCount=-1,se434ShadowType=-1,se434ShadowSerial=0;
function se434ShadowChanged(s){
 let changed=s!==se434ShadowScene||renderer.shadowMap.type!==se434ShadowType,force=false,count=0,lights=0;
 const serial=++se434ShadowSerial;
 s.updateMatrixWorld(true);
 s.traverseVisible(o=>{
  if(o.isLight&&o.castShadow&&o.shadow){
   lights++;o.target?.updateWorldMatrix(true,false);
   let p=se434ShadowLights.get(o);
   const values=[o.distance,o.angle,o.shadow.focus,o.shadow.mapSize.x,o.shadow.mapSize.y];
   const projection=o.shadow.camera?.projectionMatrix;
   if(!p){p={matrix:new THREE.Matrix4(),target:new THREE.Matrix4(),projection:new THREE.Matrix4(),values:[],seen:-1};se434ShadowLights.set(o,p);}
   if(p.seen!==serial-1||!p.matrix.equals(o.matrixWorld)||o.target&&!p.target.equals(o.target.matrixWorld)||projection&&!p.projection.equals(projection)||values.some((v,i)=>p.values[i]!==v))changed=true;
   p.matrix.copy(o.matrixWorld);if(o.target)p.target.copy(o.target.matrixWorld);if(projection)p.projection.copy(projection);p.values=values;p.seen=serial;
  }
  if(!o.isMesh||!o.castShadow)return;
  count++;const g=o.geometry,materials=Array.isArray(o.material)?o.material:[o.material];
  if(o.isSkinnedMesh||o.morphTargetInfluences?.length||o.morphTexture||o.customDepthMaterial||o.customDistanceMaterial)force=true;
  let p=se434ShadowObjects.get(o);
  if(!p){p={matrix:new THREE.Matrix4(),geometry:null,position:null,index:null,versions:[],materials:[],seen:-1};se434ShadowObjects.set(o,p);}
  const position=g?.attributes?.position,index=g?.index;
  const pv=position?.version,iv=index?.version,nv=g?.attributes?.normal?.version,ds=g?.drawRange?.start,dc=g?.drawRange?.count,layers=o.layers.mask,instance=o.instanceMatrix?.version,instanceCount=o.count;
  if(p.seen!==serial-1||p.geometry!==g||p.position!==position||p.index!==index||!p.matrix.equals(o.matrixWorld)||p.pv!==pv||p.iv!==iv||p.nv!==nv||p.ds!==ds||p.dc!==dc||p.layers!==layers||p.instance!==instance||p.instanceCount!==instanceCount||p.materials.length!==materials.length)changed=true;
  for(let i=0;i<materials.length;i++){
   const m=materials[i],old=p.materials[i];
   if(m&&(m.alphaMap||m.alphaTest>0||m.displacementMap||m.clippingPlanes?.length||m.onBeforeCompile!==THREE.Material.prototype.onBeforeCompile))force=true;
   if(old?.material!==m||old?.version!==m?.version||old?.visible!==m?.visible||old?.side!==m?.side||old?.shadowSide!==m?.shadowSide||old?.opacity!==m?.opacity||old?.transparent!==m?.transparent||old?.alphaHash!==m?.alphaHash)changed=true;
   const record=p.materials[i]||(p.materials[i]={});record.material=m;record.version=m?.version;record.visible=m?.visible;record.side=m?.side;record.shadowSide=m?.shadowSide;record.opacity=m?.opacity;record.transparent=m?.transparent;record.alphaHash=m?.alphaHash;
  }
  p.materials.length=materials.length;p.matrix.copy(o.matrixWorld);p.geometry=g;p.position=position;p.index=index;p.pv=pv;p.iv=iv;p.nv=nv;p.ds=ds;p.dc=dc;p.layers=layers;p.instance=instance;p.instanceCount=instanceCount;p.seen=serial;
 });
 if(count!==se434ShadowCount||lights!==se434ShadowLightCount)changed=true;
 se434ShadowScene=s;se434ShadowCount=count;se434ShadowLightCount=lights;se434ShadowType=renderer.shadowMap.type;se434Shadows.casters=count;
 return {changed,force};
}
const se434EditorRender=renderer.render;
renderer.render=function(s,c,...args){
 const shadow=renderer.shadowMap;
 if(playing||simulating||s!==scene||!shadow?.enabled||!shadow.autoUpdate||s.overrideMaterial||renderer.clippingPlanes?.length){
  se434ShadowScene=null;se434Shadows.fallback++;return se434EditorRender.call(this,s,c,...args);
 }
 se434Shadows.frames++;const check=se434ShadowChanged(s);
 if(check.force){se434ShadowScene=null;se434Shadows.fallback++;return se434EditorRender.call(this,s,c,...args);}
 const previous=shadow.autoUpdate;shadow.autoUpdate=false;
 if(check.changed||shadow.needsUpdate){shadow.needsUpdate=true;se434Shadows.refreshed++;}
 else se434Shadows.reused++;
 try{return se434EditorRender.call(this,s,c,...args);}
 finally{shadow.autoUpdate=previous;}
};
window.SWYRL_ENGINE_EDITOR_SHADOW_CACHE_434=Object.freeze({diagnose:()=>({...se434Shadows,
 originalShadowResolutionAndFiltering:true,gameplayAndSimulationAlwaysNative:true,
 nativeActorLightGeometryAndMaterialInvalidation:true})});
/* SE434_ENGINE_EDITOR_SHADOW_CACHE_END */
