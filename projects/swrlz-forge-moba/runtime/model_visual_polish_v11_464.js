/* SE464_MODEL_VISUAL_POLISH_START */
// Scoped to the original ModelAtelier closure. Presentation only: never
// touch part descriptors, source materials, face IDs, history or geometry.
let se464LightScene=null,se464LightObjects=[];
function se464StudioLights(){
 if(!world||se464LightScene===world)return;
 se464LightScene=world;se464LightObjects=[];
 // Two soft fixed-direction work lights supplement the native model lighting.
 // Helpers are attached to the render scene, NOT modelRoot or saved parts.
 for(const [color,power,pos] of [
  [0xf5e9da,.42,[-6,8,6]],[0x8fc5ff,.21,[6,2,-5]]
 ]){
  const light=new THREE.DirectionalLight(color,power);
  light.name='Model Studio display fill (v11.464)';
  light.position.set(...pos);
  light.userData.atelierHelper=true;
  light.userData.se464ViewOnly=true;
  light.visible=false;
  world.add(light);se464LightObjects.push(light);
 }
}
function se464StudioLightVisibility(){
 const on=!!world&&!se340ModelBridge?.isBorrowed?.()&&!!panel&&!panel.hidden;
 for(const light of se464LightObjects){
  if(light.visible!==on){light.visible=on;atelierHDDirty=true;}
 }
}
function se464XrayCleanup(mesh){
 for(const child of [...(mesh?.children||[])]){
  if(!child.userData?.se464XrayDepth)continue;
  mesh.remove(child);
  // The depth-only helper borrows the OWNED mesh geometry. NEVER dispose it.
  child.material?.dispose?.();
 }
}
function se464XrayMaterial(mesh){
 const previous=mesh.material,original=mesh.userData?.se455OriginalMaterial;
 if(!previous||Array.isArray(previous))return false;
 const next=new THREE.MeshBasicMaterial({
  color:0xaecbdf,transparent:true,opacity:.13,side:THREE.FrontSide,
  depthTest:true,depthWrite:false
 });
 next.userData={atelierViewportClone:true,se464XraySurface:true};
 mesh.material=next;
 if(previous!==original&&previous.userData?.atelierViewportClone)previous.dispose?.();
 return true;
}
function se464XrayDepth(mesh){
 const material=new THREE.MeshBasicMaterial({
  color:0xffffff,colorWrite:false,transparent:false,
  depthTest:true,depthWrite:true,side:THREE.FrontSide,
  polygonOffset:true,polygonOffsetFactor:1,polygonOffsetUnits:1
 });
 const helper=new THREE.Mesh(mesh.geometry,material);
 helper.name='X-Ray depth-only visibility pass';
 helper.userData.atelierHelper=true;
 helper.userData.se455DisplayEdges=true;
 helper.userData.se464XrayDepth=true;
 helper.raycast=()=>{}; // Native geometry picking still belongs to parent mesh.
 helper.renderOrder=-1;
 mesh.add(helper);
 return helper;
}
const se464PreviousViewApply=atelierViewModeApply;
atelierViewModeApply=function(mesh,part){
 const result=se464PreviousViewApply.apply(this,arguments);
 if(!mesh?.isMesh||!part)return result;
 se464XrayCleanup(mesh);
 const mode=atelierViewModeFor(part);
 if(['solid','shaded','overlay','flat','clay'].includes(mode)){
  se464StudioLights();se464StudioLightVisibility();
 }
 if(mode!=='xray'||!se462EligibleWire(mesh))return result;
 if(!se464XrayMaterial(mesh))return result;
 // Transparent front faces by themselves do not occlude back lines.
 // A depth-only front-surface pass provides exact visibility without changing
 // face colors, UVs, actual material or native topology.
 se464XrayDepth(mesh);
 const n=mesh.geometry?.getIndex?.()?.count||
   mesh.geometry?.getAttribute?.('position')?.count||0;
 if(n>18000)return result; // Limit diagnostic allocations on dense assets.
 const primary=new THREE.EdgesGeometry(mesh.geometry,22);
 se462AddLine(mesh,primary.clone(),{
  color:0x84a8d1,opacity:.21,depthTest:false,
  name:'X-Ray hidden topology',order:11
 });
 se462AddLine(mesh,primary,{
  color:se462PrimaryColor(part),opacity:1,depthTest:true,
  name:'X-Ray visible topology',order:12,primary:true
 });
 return result;
};
const se464PreviousToolbarRefresh=atelierMeshToolbarRefresh;
atelierMeshToolbarRefresh=function(){
 const result=se464PreviousToolbarRefresh.apply(this,arguments);
 se462Recolor();
 const element=panel;
 if(element){
  element.dataset.se464Selection=partById(selection)?'selected':'none';
  element.dataset.se464Component=atelierComponentMode||'mesh';
 }
 return result;
};
// Modify only the native view helper's line color, not its transform handles.
const se464PreviousGizmoBuild=atelierMeshGizmoBuild;
atelierMeshGizmoBuild=function(){
 const result=se464PreviousGizmoBuild.apply(this,arguments);
 atelierMeshGizmo?.traverse?.(child=>{
  if(child?.type!=='BoxHelper'&&!child?.isBoxHelper)return;
  child.material?.color?.setHex?.(0x8fffe3);
  if(child.material){child.material.depthTest=false;child.material.needsUpdate=true;}
 });
 return result;
};
const se464PreviousTick=se430BeginnerTick;
se430BeginnerTick=function(now){
 const result=se464PreviousTick.apply(this,arguments);
 if(se464LightObjects.length)se464StudioLightVisibility();
 return result;
};
function se464InspectorInstall(host){
 if(!host||host.dataset.se464InspectorReady==='1')return;
 const inspector=host.querySelector('.atelier-inspector');
 const handle=inspector?.querySelector('.atelier-tool-handle');
 if(!inspector||!handle)return;
 host.dataset.se464InspectorReady='1';
 const focus=document.createElement('button');
 focus.id='se464InspectorFocus';
 focus.type='button';focus.textContent='⤢ Expand';
 focus.setAttribute('aria-label','Expand model tool settings over viewport');
 focus.setAttribute('aria-pressed','false');
 focus.title='Read tool settings at full width without changing dock sizes';
 const sync=()=>{
  const expanded=host.dataset.se464InspectorFocus==='true';
  focus.textContent=expanded?'↙ Dock':'⤢ Expand';
  focus.setAttribute('aria-pressed',String(expanded));
  focus.setAttribute('aria-label',expanded?'Return tool settings to dock':'Expand model tool settings over viewport');
 };
 const set=value=>{
  if(value&&(!host.hidden)&&host.dataset.se320InspectorCollapsed!=='true')
   host.dataset.se464InspectorFocus='true';
  else delete host.dataset.se464InspectorFocus;
  sync();
 };
 focus.addEventListener('pointerdown',event=>event.stopPropagation());
 focus.addEventListener('click',event=>{
  event.preventDefault();event.stopPropagation();
  set(host.dataset.se464InspectorFocus!=='true');
 });
 handle.append(focus);
 host.addEventListener('keydown',event=>{
  if(event.key==='Escape'&&host.dataset.se464InspectorFocus==='true'){
   set(false);focus.focus();event.stopPropagation();
  }
 });
 new MutationObserver(()=>{
  if(host.hidden||host.dataset.se320InspectorCollapsed==='true')set(false);
  else sync();
 }).observe(host,{attributes:true,attributeFilter:[
  'hidden','data-se320-inspector-collapsed','data-se464-inspector-focus'
 ]});
 window.addEventListener('swrlz:project-loaded',()=>set(false));
 sync();
}
const se464PreviousInstall=se430BeginnerInstall;
se430BeginnerInstall=function(host){
 const result=se464PreviousInstall(host);
 se464InspectorInstall(host);
 return result;
};
window.SWYRL_ENGINE_VIEW_POLISH_464=Object.freeze({
 version:'v11.464',
 inspect:()=>({
  focus:panel?.dataset?.se464InspectorFocus==='true',
  component:atelierComponentMode||'mesh',
  selected:!!partById(selection),
  lights:se464LightObjects.length
 })
});
 /* SE464_MODEL_VISUAL_POLISH_END */