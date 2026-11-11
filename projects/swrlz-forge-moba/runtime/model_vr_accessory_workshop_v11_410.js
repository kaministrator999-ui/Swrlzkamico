/* SE410_MODEL_VR_ACCESSORY_WORKSHOP_START */
// Disposable scene-owned previews. Native geometry/history changes only on a
// fresh primary select away from the spatial menu, through vrAccessory.commit.
se340XR.se410Accessory=null;
const se410AccessoryAPI=()=>ModelAtelier.vrAccessory;
const se410PreviousAction=se340ModelXRAction,se410PreviousTrigger=se340Trigger;
const se410PreviousCancel=se340CancelGesture,se410PreviousNavigate=se350Navigate;
const se410PreviousBegin=se340BeginGesture,se410PreviousInspect=se340ModelXRInspect,se410PreviousDispatch=se350Dispatch;
const se410Styles=[
 {name:'Walnut',bodyColor:'#704b39',flapColor:'#8b6044',trimColor:'#d7b47c',metalColor:'#cda16a'},
 {name:'Plum',bodyColor:'#49304e',flapColor:'#69446c',trimColor:'#e2bf81',metalColor:'#d6ac64'},
 {name:'Fawn',bodyColor:'#a57a58',flapColor:'#bd946e',trimColor:'#f3d7a1',metalColor:'#b98b4f'}
];
function se410AccessoryParams(c){return {...c.draft.parameters,stitches:c.draft.parameters.detail,color:c.draft.parameters.bodyColor};}
function se410AccessoryUI(){
 const c=se340XR.se410Accessory;if(!c)return {accessoryActive:false,accessoryStyleName:'Walnut',accessoryFit:'free'};
 const p=se410AccessoryParams(c),unit=c.physicalUnit*c.factor;
 const cm=n=>+(n*unit*100).toFixed(1)+' cm';
 return {accessoryActive:true,accessoryParams:p,accessoryDimensionLabels:{width:cm(p.width),height:cm(p.height),depth:cm(p.depth),thickness:cm(p.thickness),rounding:cm(p.rounding),flap:Math.round(p.flap*100)+'% cover',strap:cm(p.height*(.22+p.strap*.24))},
  accessoryStyleName:se410Styles[c.style].name,accessoryFit:c.fitMode,accessoryGapLabel:Math.round(c.gap*1000)+' mm',accessoryTargetName:c.targetName||'Aim at a model surface'};
}
function se410ReleaseAccessory(c,committed=false){
 if(!c)return;c.ghost?.removeFromParent();
 c.ghost?.traverse(o=>{o.geometry?.dispose();if(o.material){for(const m of Array.isArray(o.material)?o.material:[o.material])m.dispose();}});
 if(!committed)se410AccessoryAPI().cancel(c.draft);
}
function se410CancelAccessory(){
 const s=se340XR,c=s.se410Accessory;if(!c)return false;
 s.se410Accessory=null;se410ReleaseAccessory(c);s.mode='inspect';s.page='accessory';return true;
}
function se410AccessoryGhost(preview){
 const group=new THREE.Group();group.name='Model VR · uncommitted hip pouch';group.userData.editorOnly=true;group.matrixAutoUpdate=false;
 for(const item of preview.parts){
  const hardware=item.part.material==='metal';
  const material=new THREE.MeshStandardMaterial({color:item.part.color,roughness:hardware?.3:.8,metalness:hardware?.68:0,side:THREE.DoubleSide});
  const mesh=new THREE.Mesh(item.geometry,material);mesh.name=item.part.name;group.add(mesh);
 }
 const box=new THREE.Box3(new THREE.Vector3(...preview.bounds.min),new THREE.Vector3(...preview.bounds.max));
 const boundary=new THREE.Box3Helper(box,0x94e6d0);boundary.material.transparent=true;boundary.material.opacity=.2;boundary.material.depthWrite=false;group.add(boundary);
 return group;
}
function se410UpdateGhost(c){
 const root=se350Root();root.updateWorldMatrix(true,false);const t=c.draft.transform;
 const local=new THREE.Matrix4().compose(new THREE.Vector3(...t.position),new THREE.Quaternion().setFromEuler(new THREE.Euler(...t.rotation)),new THREE.Vector3(...t.scale));
 c.ghost.matrix.copy(root.matrixWorld).multiply(local);c.ghost.matrixWorldNeedsUpdate=true;c.ghost.updateWorldMatrix(true,true);
}
function se410AccessoryPose(c,point,normal=null){
 const root=se350Root();root.updateWorldMatrix(true,false);
 const rootQ=root.getWorldQuaternion(new THREE.Quaternion()),q=new THREE.Quaternion();
 if(normal){
  const up=new THREE.Vector3(0,1,0);if(Math.abs(up.dot(normal))>.97)up.set(0,0,1);
  const right=new THREE.Vector3().crossVectors(up,normal).normalize();up.crossVectors(normal,right).normalize();
  q.setFromRotationMatrix(new THREE.Matrix4().makeBasis(right,up,normal));
  q.multiply(new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0,0,1),c.yaw));
 }else q.copy(rootQ).multiply(new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0,1,0),c.yaw));
 const worldScale=root.getWorldScale(new THREE.Vector3()),rootUnit=Math.max(.001,...worldScale.toArray().map(Math.abs));
 const scale=THREE.MathUtils.clamp(c.physicalUnit*c.factor/rootUnit,.0051,20);
 const localQ=rootQ.clone().invert().multiply(q),euler=new THREE.Euler().setFromQuaternion(localQ);
 let position=root.worldToLocal(point.clone());
 if(normal){
  const mount=new THREE.Vector3(...c.mount.position).multiplyScalar(scale).applyQuaternion(localQ);
  position.sub(mount);
 }
 const t=c.draft.transform;t.position.splice(0,3,...position.toArray());t.rotation.splice(0,3,euler.x,euler.y,euler.z);t.scale.fill(scale);
 se410UpdateGhost(c);
}
function se410ArmAccessory(record=null){
 const s=se340XR;if(s.se410Accessory){s.page='accessory';s.helpVisible=false;se340SyncUI();return true;}
 se340CancelGesture('Previous preview canceled.');record=se390SelectRecord()||record;
 if(!record?.targetTracked||!record.gripTracked){se340Notice('Track your selection controller, then choose Hip pouch.',true);return false;}
 const draft=se410AccessoryAPI().draft({...se410Styles[0]});if(!draft?.ok)return se390NoticeError(draft);
 const preview=se410AccessoryAPI().preview(draft);if(!preview?.ok){se410AccessoryAPI().cancel(draft);return se390NoticeError(preview);}
 const cast=se340Cast(record),depth=THREE.MathUtils.clamp(cast?cast.ray.origin.distanceTo(s.rig.position):.8,.25,2.2);
 const c={draft,record,ghost:se410AccessoryGhost(preview),mount:preview.mount,partCount:preview.parts.length,
  physicalUnit:.14/.9,factor:1,yaw:0,style:0,fitMode:'free',gap:.003,targetName:'',targetId:null,validPose:true,
  keys:se390CreationKeys(record),awaitRelease:true,depth,nextContact:0,
  documentToken:draft.documentToken,revision:draft.revision};
 s.scene.add(c.ghost);s.se410Accessory=c;s.mode='accessory';s.page='accessory';s.helpVisible=false;s.paletteVisible=true;s.ui.closeWheel();s.wheel=null;
 const point=s.rig.position.clone().addScaledVector(s.right,.43).addScaledVector(s.forward,-.17);point.y-=.04;
 c.point=point;c.normal=null;se410AccessoryPose(c,point);
 se340Notice('Hip pouch preview · Body, Details and Fit shape it · aim away from the menu, release then Trigger to place · B cancels.');
 se340SyncUI();se340Publish();return true;
}
function se410RebuildAccessory(c,params){
 const draft=se410AccessoryAPI().rebuild(c.draft,params);if(!draft?.ok)return se390NoticeError(draft);
 const preview=se410AccessoryAPI().preview(draft);if(!preview?.ok){se410CancelAccessory();return se390NoticeError(preview);}
 const ghost=se410AccessoryGhost(preview),old=c.ghost;c.draft=draft;c.ghost=ghost;c.mount=preview.mount;c.partCount=preview.parts.length;
 se340XR.scene.add(ghost);old.removeFromParent();old.traverse(o=>{o.geometry?.dispose();for(const m of o.material?(Array.isArray(o.material)?o.material:[o.material]):[])m.dispose();});
 se410AccessoryPose(c,c.point,c.normal);se340SyncUI();se340Publish();return true;
}
function se410AccessoryFrame(s,dt){
 const c=s.se410Accessory;if(!c)return;const native=se340Bridge().inspect();
 if(!se340VisibleSession()||!c.record.targetTracked||!c.record.gripTracked||native.documentToken!==c.documentToken||native.revision!==c.revision){
  se410CancelAccessory();se340Notice('Tracking or model changed · pouch preview canceled.');return;
 }
 if(c.awaitRelease&&c.keys.every(k=>!s.inputSample?.buttons?.[k]?.physical))c.awaitRelease=false;
 // Menu interaction freezes the last useful placement, instead of dragging
 // the bag behind the panel while a user adjusts its dimensions or details.
 if(se360MenuContact(c.record)||s.gesture?.kind==='menu'){se410UpdateGhost(c);return;}
 const cast=se340Cast(c.record);if(!cast)return;
 if(c.fitMode==='surface'){
  if(performance.now()<c.nextContact){se410UpdateGhost(c);return;}c.nextContact=performance.now()+50;
  const hit=se340Hit(c.record,true);
  if(!hit?.id||!hit.face||!hit.mesh){c.validPose=false;c.targetName='';c.targetId=null;se410UpdateGhost(c);return;}
  hit.mesh.updateWorldMatrix(true,false);
  const normal=hit.face.normal.clone().applyMatrix3(new THREE.Matrix3().getNormalMatrix(hit.mesh.matrixWorld)).normalize();
  c.point=hit.point.clone().addScaledVector(normal,c.gap);c.normal=normal;c.targetName=hit.name;c.targetId=hit.id;c.validPose=true;
 }else{
  c.point=cast.ray.at(c.depth,new THREE.Vector3());c.normal=null;c.targetName='';c.targetId=null;c.validPose=true;
 }
 se410AccessoryPose(c,c.point,c.normal);
}
function se410CommitAccessory(record){
 const s=se340XR,c=s.se410Accessory;if(!c||c.record!==record||c.awaitRelease)return false;
 c.nextContact=0;se410AccessoryFrame(s,0);if(s.se410Accessory!==c)return false;
 if(!c.validPose){se340Notice('Aim at the model surface to fit the bag, or choose Free placement.',true);return false;}
 const result=se410AccessoryAPI().commit(c.draft,c.documentToken);
 if(!result?.ok){se410CancelAccessory();return se390NoticeError(result);}
 s.se410Accessory=null;se410ReleaseAccessory(c,true);se350Invalidate();s.mode='grab';s.page='tools';
 se340Notice('Hip pouch created · '+result.ids.length+' editable components selected · grip to move and turn · Undo removes the whole bag.');
 se340Pulse(record,.35,28);se340SyncUI();se340Publish();return true;
}
se340CancelGesture=function(message='Edit canceled.'){
 const canceled=se410CancelAccessory();return se410PreviousCancel(message)||canceled;
};
se340BeginGesture=function(record,purpose='grab'){
 if(se340XR.se410Accessory){const pose=se340GripPose(record);return !!pose&&se372MenuDragStart(record,pose);}
 return se410PreviousBegin(record,purpose);
};
se340Trigger=function(record,additive=false){
 if(se340XR.se410Accessory){
  if(se360MenuContact(record))return se410PreviousTrigger(record,additive);
  if(!additive)return se410CommitAccessory(record);return;
 }
 return se410PreviousTrigger(record,additive);
};
se340ModelXRAction=function(action,record=null){
 const s=se340XR;if(!s.session||!s.scene||!se340VisibleSession())return false;
 if(action==='accessory-menu'){
  s.page='accessory';s.helpVisible=false;s.paletteVisible=true;s.ui.closeWheel();s.wheel=null;se340SyncUI();se340Publish();return true;
 }
 if(action==='create-pouch')return se410ArmAccessory(record);
 const c=s.se410Accessory;
 if(c&&(action==='focus'||action==='recenter')){
  const root=se350Root();root.updateWorldMatrix(true,false);
  const point=root.worldToLocal(c.point.clone()),normal=c.normal?.clone().applyQuaternion(root.getWorldQuaternion(new THREE.Quaternion()).invert());
  // Native framing cancels native gestures. Temporarily park this source-safe
  // draft, then reproject its placement through the new presentation matrix.
  s.se410Accessory=null;
  try{se410PreviousAction(action,record);}finally{s.se410Accessory=c;}
  root.updateWorldMatrix(true,false);c.point=root.localToWorld(point);c.normal=normal?.applyQuaternion(root.getWorldQuaternion(new THREE.Quaternion()))||null;
  se410AccessoryPose(c,c.point,c.normal);s.mode='accessory';s.page='accessory-fit';se340SyncUI();se340Publish();return true;
 }
 if(['accessory-body','accessory-details','accessory-fit'].includes(action)){
  if(!c)return false;s.page=action;s.helpVisible=false;se340SyncUI();se340Publish();return true;
 }
 if(action.startsWith('accessory-')){
  if(!c)return false;const params={...c.draft.parameters};let change=false;
  const match=/^accessory-(width|height|depth|rounding|thickness|flap|strap)-(minus|plus)$/.exec(action);
  if(match){
   const ranges={width:[.35,1.8,.06],height:[.35,1.8,.06],depth:[.15,.75,.03],rounding:[.02,.25,.02],thickness:[.012,.10,.005],flap:[.25,.85,.05],strap:[0,1,.1]};
   const [min,max,step]=ranges[match[1]];params[match[1]]=THREE.MathUtils.clamp(+(params[match[1]]+(match[2]==='plus'?step:-step)).toFixed(4),min,max);
   params.thickness=Math.min(params.thickness,Math.min(params.depth*.22,params.height*.12,params.width*.12)-.001);change=true;
  }else if(action==='accessory-stitches'){params.detail=!params.detail;change=true;}
  else if(action==='accessory-emblem'){params.emblem=['leaf','star','none'][(['leaf','star','none'].indexOf(params.emblem)+1)%3];change=true;}
  else if(action==='accessory-material'){
   const style=(c.style+1)%se410Styles.length;Object.assign(params,se410Styles[style]);delete params.name;
   const result=se410RebuildAccessory(c,params);if(result)c.style=style;se340SyncUI();return result;
  }else if(action==='accessory-reset'){
   const result=se410RebuildAccessory(c,{...se410Styles[0]});if(result){c.style=0;c.factor=1;c.yaw=0;se410AccessoryPose(c,c.point,c.normal);}se340SyncUI();return result;
  }else if(action==='accessory-surface'||action==='accessory-free'){
   c.fitMode=action==='accessory-surface'?'surface':'free';c.validPose=c.fitMode==='free';c.targetId=null;c.targetName='';c.nextContact=0;
   se340Notice(c.fitMode==='surface'?'Surface fit · aim at the hip · the back of the bag follows the surface · fresh Trigger places.':'Free placement · aim into the workspace · fresh Trigger places.');
  }else if(action==='accessory-align'){c.yaw=0;se410AccessoryPose(c,c.point,c.normal);}
  else if(action==='accessory-gap-minus'||action==='accessory-gap-plus'){
   const old=c.gap;c.gap=THREE.MathUtils.clamp(c.gap+(action.endsWith('plus')?.001:-.001),0,.025);
   if(c.normal)c.point.addScaledVector(c.normal,c.gap-old);se410AccessoryPose(c,c.point,c.normal);
  }else return false;
  if(change)return se410RebuildAccessory(c,params);se340SyncUI();se340Publish();return true;
 }
 if(c&&(action==='undo'||action==='redo')){
  se340CancelGesture();se340Notice('Pouch preview canceled · press again to '+action+'.');se340SyncUI();se340Publish();return true;
 }
 // Reading the Guide, hiding/repositioning the palette and changing display
 // are source-safe. Other tools cancel pending creation before dispatch.
 if(c&&!['help','palette','menu-hide','menu-reset','cancel'].includes(action)&&!action.startsWith('display-'))
  se340CancelGesture('Pouch preview canceled before changing tools.');
 return se410PreviousAction(action,record);
};
se350Navigate=function(sample,dt){
 const c=se340XR.se410Accessory;if(!c)return se410PreviousNavigate(sample,dt);
 const axis=sample.axes.orbit||sample.axes.zoom;
 if(axis){
  c.factor=THREE.MathUtils.clamp(c.factor*Math.exp(-axis.y*dt*1.2),.25,4);c.yaw+=axis.x*dt*1.2;
  se340XR.se390AxisLatch={keys:axis.keys||[],action:sample.axes.orbit?'orbit':'zoom'};se410AccessoryPose(c,c.point,c.normal);
 }
};
se350Dispatch=function(sample){
 if(!se340XR.se410Accessory)return se410PreviousDispatch(sample);
 // Additive world selection is unavailable while placing a draft. Both hands
 // still operate menu cards; no background selection sweep can start.
 const events=sample.events.filter(e=>e.action!=='multiselect'||se360MenuContact(e.source?.record||se350Record(e.hand)));
 se340XR.se372Sweep=null;return se410PreviousDispatch({...sample,events});
};
se340ModelXRInspect=function(options={}){
 const result=se410PreviousInspect(options),c=se340XR.se410Accessory;
 result.accessory=c?{active:true,parameters:{...c.draft.parameters},params:se410AccessoryParams(c),partCount:c.partCount,fitMode:c.fitMode,
  targetName:c.targetName,targetId:c.targetId,position:[...c.draft.transform.position],rotation:[...c.draft.transform.rotation],scale:[...c.draft.transform.scale],awaitRelease:c.awaitRelease,validPose:c.validPose}:
  {active:false};return result;
};
/* SE410_MODEL_VR_ACCESSORY_WORKSHOP_END */
