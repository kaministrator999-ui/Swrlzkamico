// §E v11.204 — Sheep Tag PLAY-only quick-build and ability wheels.
// Right A: hold to pick a house, tap to repeat that house.
// Left X: hold to pick an ability, tap to activate it.
// Right B: the existing XR tools/capture menu. Left Y: recenter.
// Buildings are world-axis-aligned with a 3.6m square lattice: 2.4m houses
// separated by 1.2m walking lanes. No editor rotations in Sheep Tag Play.
const se204={
 holdMs:340,pitch:3.6,building:null,skill:null,
 anchor:null,session:null,wheel:null,wheels:new Map(),frame:0,
 buttons:{left:{held:false,at:0,opened:false},right:{held:false,at:0,opened:false}},
 selections:0,placed:0,blocked:0,skillUses:0,gridSamples:0,
 wheelBuilds:0,wheelReuses:0,wheelHighlights:0,wheelDisposals:0,
 previousHighlight:null,lastReason:'',lastPreview:null,previewSkipped:0
};
const se204Buildings=Object.freeze([
 {id:'st-farm',label:'FARM',color:0x5ddbbb},
 {id:'st-income',label:'INCOME',color:0xf1cf80},
 {id:'st-fort',label:'FORT',color:0x99b8e8},
 {id:null,label:'CANCEL',color:0xadb5bf}
]);
const se204Skills=Object.freeze([
 {id:'split',label:'MIRROR',color:0x71dafa},
 {id:'totem',label:'TOTEM',color:0x78da9f},
 {id:null,label:'NONE',color:0xa6b2c6}
]);
function se204Gameplay(){
 if(!se193XRGameActive()||!stSession||stSession.role!=='sheep')return false;
 const u=stSession.units.find(u=>u.id===stSession.controlledId);
 return !!u&&u.kind==='sheep'&&!u.captured&&!u.isIllusion&&!stSession.winner;
}
function se204RapidEnabled(){
 return se204Gameplay()&&!!stUi.build&&stUi.build===se204.building;
}
function se204GridPoint(point){
 if(!se204RapidEnabled()||!point||
    !Number.isFinite(point.x)||!Number.isFinite(point.z))return point;
 const nativeSnap=stUiRules().buildSnap||.15;
 // The old coarse 3m rule needs 6m cells to remain on its native lattice.
 // Fine 0.15m rules use 3.6m (2.4m house + 1.2m passage).
 const pitch=nativeSnap>=3?6:se204.pitch;
 if(!se204.anchor||se204.session!==stSession){
  se204.session=stSession;
  se204.anchor={x:Math.round(point.x/nativeSnap)*nativeSnap,
   z:Math.round(point.z/nativeSnap)*nativeSnap};
 }
 const x=Math.round((se204.anchor.x+
  Math.round((point.x-se204.anchor.x)/pitch)*pitch)/nativeSnap)*nativeSnap;
 const z=Math.round((se204.anchor.z+
  Math.round((point.z-se204.anchor.z)/pitch)*pitch)/nativeSnap)*nativeSnap;
 se204.gridSamples++;
 return new THREE.Vector3(x,terrainHeight(x,z),z);
}
const se204OldPreview=stUiPlacePreview;
stUiPlacePreview=function(point){
 // Both live ghost and trigger/rapid taps share the snapped grid.
 if(se204RapidEnabled()){
  stUi.rotation=0;
  const gridPoint=se204GridPoint(point);
  const now=performance.now(),s=stSession;
  const prior=se204.lastPreview;
  const resources=s?.resources?.[s.controlledId]||0;
  if(prior&&prior.session===s&&prior.kind===stUi.build&&
     prior.nav===s.navVersion&&prior.resources===resources&&
     Math.abs(prior.x-gridPoint.x)<.001&&
     Math.abs(prior.z-gridPoint.z)<.001&&
     now-prior.at<430&&stUi.placement){
   se204.previewSkipped++;return;
  }
  se204.lastPreview={session:s,kind:stUi.build,x:gridPoint.x,z:gridPoint.z,
    nav:s.navVersion,resources,at:now};
  return se204OldPreview(gridPoint);
 }
 return se204OldPreview(point);
};
function se204EquipBuilding(kind){
 if(!se204Gameplay())return false;
 if(kind!==null&&!se204Buildings.some(b=>b.id===kind))return false;
 if(kind===null){
  se204.building=null;se204.anchor=null;se204.lastPreview=null;
  stUi.build=null;stUiClearPreview();stRefreshHUD(true);
  se204.lastReason='House tool unequipped';return true;
 }
 se204.building=kind;se204.anchor=null;se204.lastPreview=null;se204.session=stSession;
 stUi.rotation=0; // Only the editor has rotation tools in this Play phase.
 if(stUi.build!==kind)stUiChooseBuild(kind);
 if(stUi.build!==kind){
  se204.building=null;se204.lastReason='House unavailable under current rules';
  return false;
 }
 se204.selections++;se204.lastReason='Equipped '+(stUiBuildNames[kind]||kind);
 return true;
}
function se204HouseTap(){
 if(!se204Gameplay())return false;
 if(!se204RapidEnabled()){
  se204.lastReason='Hold A to equip a house';
  se193XRFeedback({reason:se204.lastReason},false);
  return false;
 }
 const record=se192InputRecord('right');
 if(!record)return false;
 // Use exactly the same mapped world target, snapped ghost and native
 // stCommand as the trigger path. The command result is the build receipt,
 // even for LAN guest requests where a new building is not yet local.
 const point=se193XRGameGround(record);
 if(!point){
  se193XRFeedback({reason:'Aim at the sheep area to place a house'},false);
  se204.blocked++;return false;
 }
 stUiPlacePreview(point);
 const fit=stUi.placement;
 if(!fit?.ok){
  se193XRFeedback({reason:fit?.reason||'House does not fit here'},false);
  se204.blocked++;return false;
 }
 const result=stUiCommand('build',{
  kind:se204.building,x:fit.x,z:fit.z,rotation:0
 });
 se193XRFeedback(result);
 if(result?.ok){
  se204.placed++;se204AfterBuild();
 }else se204.blocked++;
 return !!result?.ok;
}
function se204AfterBuild(){
 if(!se204RapidEnabled())return;
 // Keep the same house equipped. Recheck current cell so the ghost turns
 // red after it becomes occupied, until the player aims at the next cell.
 if(stUi.placementPoint)stUiPlacePreview(stUi.placementPoint);
 stRefreshHUD(true);
}
function se204EquipSkill(skill){
 if(!se204Gameplay())return false;
 if(skill!==null&&!se204Skills.some(o=>o.id===skill))return false;
 se204.skill=skill;se204.selections++;
 se204.lastReason=skill?'Equipped '+skill:'Ability unequipped';
 return true;
}
function se204SkillReady(id){
 if(!stSession)return false;
 if(id==='split')return !!stSession.rules.split;
 if(id==='totem')return !!stSession.rules.totems;
 return true;
}
function se204SkillTap(){
 if(!se204Gameplay())return false;
 if(!se204.skill){se193XRFeedback({reason:'Hold X to select a skill'},false);return false;}
 if(!se204SkillReady(se204.skill)){
  se193XRFeedback({reason:'Enable '+se204.skill+' in Sheep Tag rules first'},false);
  return false;
 }
 const action=se204.skill;
 const payload=action==='split'?{angle:se193.angle}:{
  id:stUi.buildingId||stSession.selectedId
 };
 const result=stUiCommand(action,payload);
 se193XRFeedback(result);
 if(result?.ok)se204.skillUses++;
 return !!result?.ok;
}
function se204MenuToggle(){
 if(!se193XRGameActive())return;
 if(se204.wheel){se204WheelHide();return;}
 se195SetVisible(!se195.visible);
}
function se204Haptic(record){
 try{
  const h=record?.input?.gamepad?.hapticActuators?.[0];
  h?.pulse?.(.16,25)?.catch?.(()=>{});
 }catch(_){}
}
function se204WheelRoot(type){
 const opts=type==='build'?se204Buildings:se204Skills;
 const root=new THREE.Group();
 root.name='Sheep Tag '+type+' hold-select radial';
 root.userData.sheepTagPreview=true;
 const base=new THREE.Mesh(new THREE.CircleGeometry(.33,48),
  new THREE.MeshBasicMaterial({color:0x102c3d,transparent:true,opacity:.89,
   depthTest:false,depthWrite:false,side:THREE.DoubleSide,toneMapped:false}));
 base.position.z=-.02;base.renderOrder=10400;root.add(base);
 const rim=new THREE.Mesh(new THREE.RingGeometry(.328,.34,56),
  new THREE.MeshBasicMaterial({color:0x74e6d4,transparent:true,opacity:.85,
   depthTest:false,depthWrite:false,side:THREE.DoubleSide,toneMapped:false}));
 rim.renderOrder=10401;root.add(rim);
 const title=type==='build'?'HOUSES':'ABILITIES';
 const header=new THREE.Mesh(new THREE.PlaneGeometry(.25,.07),
  new THREE.MeshBasicMaterial({map:se195Text(title,true),transparent:true,
   depthTest:false,depthWrite:false,toneMapped:false,side:THREE.DoubleSide}));
 header.position.set(0,0,.015);header.renderOrder=10403;root.add(header);
 const items=opts.map((entry,i)=>{
  const a=-Math.PI/2+i*2*Math.PI/opts.length;
  const mat=new THREE.MeshBasicMaterial({map:se195Text(entry.label),transparent:true,
   color:entry.color,opacity:.78,depthTest:false,depthWrite:false,
   side:THREE.DoubleSide,toneMapped:false});
  const mesh=new THREE.Mesh(new THREE.PlaneGeometry(.23,.113),mat);
  mesh.position.set(Math.cos(a)*.225,Math.sin(a)*.225,.024);
  mesh.userData.se204Option=entry.id;mesh.renderOrder=10404;root.add(mesh);
  return {entry,mesh};
 });
 root.visible=false;scene.add(root);
 return {root,items,selected:0,type};
}
function se204WheelShow(type){
 if(!se204Gameplay()||se195.visible)return;
 se204WheelHide();
 if(typeof se203GroundGuideHide==='function')se203GroundGuideHide();
 let panel=se204.wheels.get(type);
 if(!panel){
  panel=se204WheelRoot(type);se204.wheels.set(type,panel);
  se204.wheelBuilds++;
 }else se204.wheelReuses++;
 se204.wheel=panel;
 panel.root.visible=true;
 const current=type==='build'?se204.building:se204.skill;
 const i=panel.items.findIndex(item=>item.entry.id===current);
 panel.selected=i>=0&&current!==null?i:0;
 se204WheelPosition();
 se204WheelHighlight(true);
}
function se204WheelPosition(){
 const panel=se204.wheel,pose=se191XRHeadPose();
 if(!panel||!pose)return;
 const aim=pose.forward.clone().normalize();
 const right=new THREE.Vector3().crossVectors(aim,new THREE.Vector3(0,1,0));
 if(right.lengthSq()<.001)right.set(1,0,0);
 right.normalize();
 panel.root.position.copy(pose.eye).addScaledVector(aim,1.0)
  .addScaledVector(right,.14).add(new THREE.Vector3(0,-.1,0));
 panel.root.lookAt(pose.eye);
 panel.root.updateMatrixWorld(true);
}
function se204WheelHighlight(force=false){
 const panel=se204.wheel;
 if(!panel)return;
 for(let i=0;i<panel.items.length;i++){
  const {mesh,entry}=panel.items[i],selected=i===panel.selected;
  mesh.material.opacity=selected?.99:.70;
  mesh.scale.setScalar(selected?1.12:1);
  mesh.material.color.setHex(entry.id&&!se204SkillReady(entry.id)&&panel.type==='skill'?
    0x69747e:entry.color);
 }
 if(force||se204.previousHighlight!==panel.selected){
  se204.wheelHighlights++;se204.previousHighlight=panel.selected;
 }
}
function se204WheelStep(record){
 const panel=se204.wheel;
 if(!panel)return;
 const a=record?.input?.gamepad?.axes;
 if(!a||a.length<2)return;
 const x=Number(a[a.length-2])||0,y=-(Number(a[a.length-1])||0);
 if(Math.hypot(x,y)<.45)return;
 const direction=Math.atan2(y,x),len=panel.items.length;
 let best=panel.selected,score=Infinity;
 for(let i=0;i<len;i++){
  const angle=-Math.PI/2+i*2*Math.PI/len;
  const delta=Math.abs(Math.atan2(Math.sin(direction-angle),Math.cos(direction-angle)));
  if(delta<score){score=delta;best=i;}
 }
 if(best!==panel.selected){
  panel.selected=best;se204WheelHighlight();se204Haptic(record);
 }
}
function se204WheelHide(){
 const panel=se204.wheel;
 if(!panel)return;
 panel.root.visible=false;se204.wheel=null;se204.previousHighlight=null;
}
function se204WheelCommit(){
 const panel=se204.wheel;
 if(!panel)return;
 const item=panel.items[panel.selected]?.entry;
 const type=panel.type;
 se204WheelHide();
 if(!item)return;
 if(type==='build')se204EquipBuilding(item.id);
 else {
  if(item.id&&!se204SkillReady(item.id)){
   se193XRFeedback({reason:'Enable '+item.label+' in Sheep Tag rules'},false);
   return;
  }
  se204EquipSkill(item.id);
 }
}
function se204WheelDispose(){
 se204WheelHide();
 for(const panel of se204.wheels.values()){
  scene.remove(panel.root);
  panel.root.traverse(o=>{
   o.geometry?.dispose?.();
   // Do not dispose cached CanvasTextures shared with the legacy Quest menu.
   if(Array.isArray(o.material))o.material.forEach(m=>m?.dispose?.());
   else o.material?.dispose?.();
  });
  se204.wheelDisposals++;
 }
 se204.wheels.clear();
}
function se204Reset(){
 se204WheelDispose();
 se204.building=se204.skill=null;se204.anchor=null;se204.session=null;
 se204.lastPreview=null;
 for(const state of Object.values(se204.buttons)){
  state.held=false;state.at=0;state.opened=false;
 }
}
function se204InputFrame(){
 if(!se204Gameplay()||se195.visible||se195.photo){
  if(se204.wheel)se204WheelHide();
  for(const state of Object.values(se204.buttons)){
   state.held=false;state.opened=false;
  }
  return;
 }
 const now=performance.now();
 for(const [side,type] of [['right','build'],['left','skill']]){
  const record=se192InputRecord(side),state=se204.buttons[side];
  const pressed=se192Pressed(record,4);
  if(pressed&&!state.held){
   state.held=true;state.at=now;state.opened=false;
  }else if(pressed&&state.held){
   if(!state.opened&&now-state.at>=se204.holdMs){
    state.opened=true;se204WheelShow(type);se204Haptic(record);
   }
   if(state.opened&&se204.wheel?.type===type)
    se204WheelStep(se192InputRecord('right'));
  }else if(!pressed&&state.held){
   if(state.opened)se204WheelCommit();
   else if(side==='right')se204HouseTap();
   else se204SkillTap();
   state.held=false;state.opened=false;
  }
 }
}
const se204OldButton=se192XRGamepadButton;
se192XRGamepadButton=function(record,button){
 if(se204Gameplay()&&!se195.visible&&!se195.photo&&
    (button==='a'||button==='x'))return true; // resolved on release
 return se204OldButton(record,button);
};
const se204OldRaycast=se192Raycast;
se192Raycast=function(record){
 if(se204.wheel)return {ui:'se204:block',distance:1.1};
 return se204OldRaycast(record);
};
const se204OldSelect=se192Select;
se192Select=function(record){
 if(se204.wheel)return; // wheel is MODAL, no buildings selected behind it
 return se204OldSelect(record);
};
const se204OldRenderRay=se192RenderRay;
se192RenderRay=function(record,hit){
 const result=se204OldRenderRay(record,hit);
 if(se204.wheel&&record?.se192){
  // A thumbstick radial is modal. No misleading marker behind the menu.
  record.se192.dot.visible=false;
  if(record.se192.beam){
   record.se192.beam.visible=true;
   record.se192.beam.scale.z=Math.min(1,record.se192.beam.scale.z||1);
  }
 }
 return result;
};
const se204OldStick=se192Stick;
se192Stick=function(record){
 if(se204.wheel&&record===se192InputRecord('right'))return {x:0,y:0};
 return se204OldStick(record);
};
const se204OldFrame=se193XRFrame;
se193XRFrame=function(){
 const r=se204OldFrame();
 se204InputFrame();
 se204.frame++;
 return r;
};
const se204OldStart=se193XRStart;
se193XRStart=function(){se204Reset();return se204OldStart();};
const se204OldCleanup=se193XRCleanup;
se193XRCleanup=function(){se204Reset();return se204OldCleanup();};
window.SWYRL_ENGINE_SHEEP_QUICK_GRID_204=Object.freeze({
 diagnose:()=>({
  gameplay:se204Gameplay(),equippedHouse:se204.building,
  equippedAbility:se204.skill,pitch:se204.pitch,rotation:0,
  anchor:se204.anchor?{...se204.anchor}:null,
  menuType:se204.wheel?.type||null,
  chosen:se204.selections,placed:se204.placed,blocked:se204.blocked,
  skillUses:se204.skillUses,gridSamples:se204.gridSamples,
  previewSkipped:se204.previewSkipped,
  menuBuilds:se204.wheelBuilds,menuReuses:se204.wheelReuses,
  menuHighlights:se204.wheelHighlights,menuDisposals:se204.wheelDisposals,
  lastReason:se204.lastReason
 })
});
