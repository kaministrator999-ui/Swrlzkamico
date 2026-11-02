// §E v11.207 · Sheep Tag PLAY native spatial wrist menu: grip → grab,
// translate/tilt in 6DoF → release to pin, resize or center with its own tools.
// Does not control Meta Quest OS panels or §E editor transforms.
const se207={
 pinned:false,grabbing:false,held:false,controller:null,panel:null,
 anchor:null,scale:1,offset:new THREE.Vector3(),
 relative:new THREE.Quaternion(),handPos:new THREE.Vector3(),
 handRotation:new THREE.Quaternion(),world:new THREE.Vector3(),
 gripStarts:0,moveFrames:0,gripReleases:0,recenters:0,resizes:0,
 decorateCount:0,decorReuses:0,ignoredGrips:0,invalidInputs:0,
 lastError:'',lastAt:0
};
function se207PlayMenu(){
 return se193XRGameActive()&&se195.mode==='game'&&
  !!se195.radial&&se195.visible&&!se195.photo&&!se205OverlayActive();
}
function se207ApplySize(){
 const root=se195.radial;
 if(root)root.scale.setScalar(.86*se207.scale);
}
function se207HoldAnchor(){
 const root=se195.radial;
 if(!root)return;
 se207.anchor={position:root.position.clone(),quaternion:root.quaternion.clone()};
 se207.pinned=true;
}
function se207Recenter(){
 se207.grabbing=false;se207.held=false;se207.controller=null;
 se207.panel=null;se207.anchor=null;se207.pinned=false;
 se207.scale=1;se207.recenters++;
 if(se195.radial)se195.radial.scale.setScalar(.86);
 // Let the original v11.196 positioning system place menu comfortably in
 // front of the HMD; it owns tracked head pose and orientation.
 se195PositionRadial(true);
}
function se207AdjustSize(delta){
 se207.scale=THREE.MathUtils.clamp(se207.scale+delta,.72,1.40);
 se207ApplySize();se207.resizes++;
 if(se207.pinned)se207HoldAnchor();
}
const se207PriorOptions=se195Options;
se195Options=function(mode=se195.mode,page=se195.page){
 if(mode==='game'&&page==='layout')return [
  ['pin','PIN'],['unpin','RECENTER'],
  ['sizeMinus','SMALLER'],['sizePlus','LARGER'],['back','BACK']
 ];
 const options=se207PriorOptions(mode,page);
 if(mode==='game'&&page==='more')return [...options,['layoutPage','LAYOUT']];
 return options;
};
const se207PriorAction=se195HandleAction;
se195HandleAction=function(action,record){
 if(se195.mode==='game'){
  if(action==='layoutPage'){se195Page('layout');return true;}
  if(action==='pin'){se207HoldAnchor();se195Page('main');return true;}
  if(action==='unpin'){se207Recenter();se195Page('main');return true;}
  if(action==='sizeMinus'){se207AdjustSize(-.12);return true;}
  if(action==='sizePlus'){se207AdjustSize(.12);return true;}
 }
 return se207PriorAction(action,record);
};
function se207Decorate(){
 const root=se195.radial;
 if(!root||se195.mode!=='game')return;
 if(root.userData.se207Decor){se207.decorReuses++;return;}
 root.userData.se207Decor=true;
 // One label and one lightweight focus halo, cached with the page root.
 const handle=new THREE.Mesh(
  new THREE.PlaneGeometry(.23,.066),
  new THREE.MeshBasicMaterial({map:se195Text('GRIP TO MOVE'),transparent:true,
   depthTest:false,depthWrite:false,side:THREE.DoubleSide,toneMapped:false})
 );
 handle.name='§E native VR menu grip label';handle.position.set(0,-.52,.028);
 handle.renderOrder=10601;root.add(handle);
 const outline=new THREE.Mesh(
  new THREE.RingGeometry(.452,.462,56),
  new THREE.MeshBasicMaterial({color:0x7ee7d4,transparent:true,opacity:.07,
   depthTest:false,depthWrite:false,side:THREE.DoubleSide,toneMapped:false})
 );
 outline.name='§E menu grab outline';outline.position.z=-.008;
 outline.renderOrder=10105;root.add(outline);
 root.userData.se207GrabOutline=outline;
 se207.decorateCount++;
}
const se207PriorMake=se195MakeRadial;
se195MakeRadial=function(reposition=true){
 const result=se207PriorMake(reposition);
 se207Decorate();
 if(se195.mode==='game'&&se207.pinned&&se207.anchor&&se195.radial){
  se195.radial.position.copy(se207.anchor.position);
  se195.radial.quaternion.copy(se207.anchor.quaternion);
  se195.radial.updateMatrixWorld(true);
 }
 se207ApplySize();
 return result;
};
const se207PriorPosition=se195PositionRadial;
se195PositionRadial=function(force=false){
 if(se195.mode==='game'&&(se207.pinned||se207.grabbing))return;
 return se207PriorPosition(force);
};
function se207BeginGrab(record){
 const root=se195.radial,controller=record?.controller;
 if(!root||!controller||!se207PlayMenu())return false;
 // A grip without pointing at the actual radial is not a menu grab.
 const hit=se195RadialHit(record);
 if(!hit?.ui?.startsWith('se195:')){se207.ignoredGrips++;return false;}
 controller.updateMatrixWorld(true);
 controller.getWorldPosition(se207.handPos);
 controller.getWorldQuaternion(se207.handRotation);
 const inverse=se207.handRotation.clone().invert();
 se207.offset.copy(root.position).sub(se207.handPos).applyQuaternion(inverse);
 se207.relative.copy(inverse).multiply(root.quaternion);
 se207.controller=record;se207.panel=root;
 se207.grabbing=true;se207.pinned=false;se207.anchor=null;
 se207.gripStarts++;
 const outline=root.userData?.se207GrabOutline;
 if(outline)outline.material.opacity=.7;
 return true;
}
function se207MoveGrab(dt){
 const record=se207.controller,root=se207.panel;
 if(!se207.grabbing||!record?.controller||!root)return;
 if(root!==se195.radial){se207EndGrab(false);return;}
 record.controller.updateMatrixWorld(true);
 record.controller.getWorldPosition(se207.handPos);
 record.controller.getWorldQuaternion(se207.handRotation);
 se207.world.copy(se207.offset).applyQuaternion(se207.handRotation)
  .add(se207.handPos);
 root.position.copy(se207.world);
 root.quaternion.copy(se207.handRotation).multiply(se207.relative);
 root.updateMatrixWorld(true);
 // Right-stick up/down resizes while the right grip is HELD. In other modes
 // right stick retains its existing sheep orbit and tactical zoom.
 const axes=record.input?.gamepad?.axes;
 const y=axes?.length>=2?Number(axes[axes.length-1])||0:0;
 if(Math.abs(y)>.22)se207AdjustSize(-y*Math.min(dt,.05)*.64);
 se207.moveFrames++;
}
function se207EndGrab(pin=true){
 if(!se207.grabbing)return;
 const panel=se207.panel;
 if(panel?.userData?.se207GrabOutline)
  panel.userData.se207GrabOutline.material.opacity=.07;
 if(pin&&panel===se195.radial){
  se207HoldAnchor();se207.gripReleases++;
 }
 se207.grabbing=false;se207.controller=null;se207.panel=null;
}
function se207Frame(){
 // Only immersive Sheep Tag's built-in gameplay menu uses this grip model.
 // Meta menus are compositor-owned; editors have independent gizmo grips.
 if(!se207PlayMenu()){
  if(se207.grabbing)se207EndGrab(false);
  se207.held=false;
  if(se195.mode!=='game'&&se207.pinned){
   se207.anchor=null;se207.pinned=false;
  }
  return;
 }
 const record=se192InputRecord('right');
 const down=!!record&&se192Pressed(record,1);
 const now=performance.now();
 const dt=Math.min(.05,Math.max(0,(now-(se207.lastAt||now))/1000));
 se207.lastAt=now;
 if(down&&!se207.held)se207BeginGrab(record);
 else if(!down&&se207.held)se207EndGrab(true);
 se207.held=down;
 if(se207.grabbing&&down)se207MoveGrab(dt);
}
const se207PriorStick=se192Stick;
se192Stick=function(record){
 if(se207.grabbing&&record===se192InputRecord('right'))return {x:0,y:0};
 return se207PriorStick(record);
};
const se207PriorFrame=se193XRFrame;
se193XRFrame=function(){const out=se207PriorFrame();se207Frame();return out;};
function se207Reset(){
 se207EndGrab(false);
 se207.held=false;se207.lastAt=0;se207.anchor=null;
 se207.pinned=false;se207.scale=1;se207.controller=null;se207.panel=null;
}
const se207PriorStart=se193XRStart;
se193XRStart=function(){se207Reset();return se207PriorStart();};
const se207PriorCleanup=se193XRCleanup;
se193XRCleanup=function(){se207Reset();return se207PriorCleanup();};
window.SWYRL_ENGINE_SHEEP_VR_SPATIAL_207=Object.freeze({
 diagnose:()=>({
  available:se207PlayMenu(),grabbing:se207.grabbing,pinned:se207.pinned,
  scale:se207.scale,mode:'game-menu-only',
  gripStarts:se207.gripStarts,gripMoves:se207.moveFrames,
  gripReleases:se207.gripReleases,gripMisses:se207.ignoredGrips,
  menuPagesDecorated:se207.decorateCount,menuCacheReuses:se207.decorReuses,
  recenters:se207.recenters,resizes:se207.resizes,
  lastError:se207.lastError
 })
});
