// §E v11.420 — make the Sheep Tag VR AI count page use the same persistent
// controller-ray/trigger targets and hover behavior as the main Quest radial.
// No new XR input handler, renderer, floating menu, or game-state owner.
const se420FlockMenu={actions:0,textureUpdates:0,lastAction:''};
const se420PreviousOptions=se195Options;
se195Options=function(mode=se195.mode,page=se195.page){
 if(mode==='menu'&&page==='aiSetup'){
  const count=se416Count(),max=se416Max();
  return [
   ['se416Minus',count===0?'MIN 0':'- 1 SHEEP'],
   ['se416Plus',count>=max?'MAX '+max:'+ 1 SHEEP'],
   ['se420None','NO AI SHEEP'],
   ['se416Launch','START MATCH'],
   ['back','CANCEL']
  ];
 }
 return se420PreviousOptions(mode,page);
};
function se420SwapMenuTexture(mesh,label){
 if(!mesh?.material||!label)return;
 if(mesh.userData.se420Label===label)return;
 const old=mesh.material.map;
 mesh.material.map=se195Text(label,!!mesh.userData.se420Heading);
 mesh.material.needsUpdate=true;
 mesh.userData.se420Label=label;
 if(old){
  const i=se195.textures.indexOf(old);
  if(i>=0)se195.textures.splice(i,1);
  old.dispose?.();
 }
 se420FlockMenu.textureUpdates++;
}
function se420SyncFlockMenu(){
 // Keep all original Three.js mesh identities and hit areas. Rebuilding the
 // radial on each +/- press discarded hovered/clicked controller targets.
 if(se195.mode!=='menu'||se195.page!=='aiSetup'||!se195.radial)return false;
 const count=se416Count(),max=se416Max(),label='AI SHEEP '+count+'/'+max;
 const heading=se195.radial.children.find(o=>o.material?.map&&!o.userData?.se195Action);
 if(heading){
  heading.userData.se420Heading=true;
  se420SwapMenuTexture(heading,label);
 }
 for(const [action,caption] of se195Options('menu','aiSetup')){
  const mesh=se195.buttons.find(b=>b.userData?.se195Action===action);
  if(!mesh)continue;
  se420SwapMenuTexture(mesh,caption);
  const atLimit=(action==='se416Minus'&&count===0)||
    (action==='se416Plus'&&count===max);
  mesh.material.color?.setHex?.(atLimit?0xa0a6a9:0xffffff);
 }
 return true;
}
const se420PreviousShow=se416Show;
se416Show=function(...args){
 const opened=se420PreviousShow(...args);
 if(opened&&renderer.xr?.isPresenting)se420SyncFlockMenu();
 return opened;
};
const se420PreviousAction=se195HandleAction;
se195HandleAction=function(action,record){
 if(se195.mode==='menu'&&se195.page==='aiSetup'){
  if(action==='se416Minus'||action==='se416Plus'||action==='se420None'){
   const count=se416Count(),max=se416Max();
   const next=action==='se416Minus'?Math.max(0,count-1):
     action==='se416Plus'?Math.min(max,count+1):0;
   se416SetCount(next);
   se420FlockMenu.actions++;
   se420FlockMenu.lastAction=action;
   se195.lastAction=next===count?
     (action==='se416Minus'?'Minimum AI sheep: 0':'Maximum AI sheep: '+max):
     ('AI sheep teammates: '+next+' of '+max);
   se420SyncFlockMenu(); // textures only; don't move/dispose controller targets
   return true;
  }
  if(action==='se416Launch')se195.lastAction='Start match with '+se416Count()+' AI sheep';
 }
 return se420PreviousAction(action,record);
};
window.SWYRL_ENGINE_SHEEP_SETUP_MENU_420=Object.freeze({
 diagnose:()=>({active:se195.mode==='menu'&&se195.page==='aiSetup',
  count:se416Count(),max:se416Max(),
  radialVisible:!!se195.visible,actions:se420FlockMenu.actions,
  textureUpdates:se420FlockMenu.textureUpdates,
  lastAction:se420FlockMenu.lastAction,stableNativeRayTargets:true})
});
