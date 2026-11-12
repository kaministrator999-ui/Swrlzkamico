/* SE430_MODEL_VR_MANUAL_WORKSHOP_START */
// Reuses the native manual-mesh transaction, existing spatial console and XR
// loop. The headset keeps its perspective projection and world-space windows.
se340XR.se430Manual=false;se340XR.se430Operation='inset';se340XR.se430Amount=.2;
se340XR.se430Learning=null;se340XR.se430RegionVisual=null;
const se430VRWorkshop=()=>ModelAtelier.workshop;
const se430PreviousAction=se340ModelXRAction,se430PreviousTrigger=se340Trigger;
const se430PreviousCancel=se340CancelGesture,se430PreviousBegin=se340BeginGesture;
const se430PreviousDispatch=se350Dispatch,se430PreviousInspect=se340ModelXRInspect;
const se430VRDefaults={inset:.2,extrude:.15,solidify:.1,deleteFaces:0,subdivide:.25,repairNormals:0};
function se430VRUI(){
 const s=se340XR;if(!s.se430Manual&&!s.se430Learning)return {manualActive:false,learningTool:null};
 const native=se430VRWorkshop().inspect();
 return {manualActive:!!s.se430Manual,manualOperation:s.se430Operation,manualAmount:s.se430Amount,
  manualSelection:{name:native.selection.name,mode:native.selection.mode,faceCount:native.selection.faceIds.length},
  manualAvailability:native.operations,manualConvert:native.convert,manualPreview:!!native.preview.active,
  learningTool:s.se430Learning};
}
function se430DropRegionVisual(){
 const s=se340XR,o=s.se430RegionVisual;if(!o)return;
 o.mesh.removeFromParent();o.mesh.geometry.dispose();o.mesh.material.dispose();s.se430RegionVisual=null;
}
function se430RegionVisual(native){
 const s=se340XR;if(!s.se430Manual||!s.scene){se430DropRegionVisual();return;}
 const entry=se340PartEntries().find(e=>e.id===native.selection.partId),source=entry?.mesh?.geometry;
 const ids=native.preview.active?native.preview.selectedFaces||[]:native.selection.faceIds;
 if(!source||!ids.length){se430DropRegionVisual();return;}
 const key=entry.id+':'+source.uuid+':'+ids.join(',');
 if(s.se430RegionVisual?.key!==key){
  se430DropRegionVisual();const positions=[],p=source.attributes.position,index=source.index;
  for(const id of ids){for(let k=0;k<3;k++){const slot=id*3+k,i=index?.getX(slot)??slot;if(i>=p.count)continue;positions.push(p.getX(i),p.getY(i),p.getZ(i));}}
  if(!positions.length)return;
  const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.Float32BufferAttribute(positions,3));
  const material=new THREE.MeshBasicMaterial({color:0xffd683,transparent:true,opacity:.33,depthTest:false,depthWrite:false,side:THREE.DoubleSide});
  const mesh=new THREE.Mesh(geometry,material);mesh.name='Model VR · selected planar faces';mesh.userData.editorOnly=true;mesh.matrixAutoUpdate=false;mesh.renderOrder=7900;s.scene.add(mesh);s.se430RegionVisual={key,mesh};
 }
 entry.mesh.updateWorldMatrix(true,false);s.se430RegionVisual.mesh.matrix.copy(entry.mesh.matrixWorld);s.se430RegionVisual.mesh.matrixWorldNeedsUpdate=true;
}
function se430ManualFrame(s){
 if(!s.se430Manual){se430DropRegionVisual();return;}
 const native=se430VRWorkshop().inspect(),record=se390SelectRecord();
 if(!se340VisibleSession()||!record?.targetTracked||!record.gripTracked){
  se430VRWorkshop().cancel('Controller tracking changed; manual preview canceled.');s.se430Manual=false;s.mode='inspect';s.page='mesh';se430DropRegionVisual();return;
 }
 se430RegionVisual(native);
}
function se430ManualResult(result,notice){
 if(!result?.ok){se340Notice(result?.reason||result?.error||'This operation is unavailable for the current selection.',true);return false;}
 se350Invalidate();se340Notice(notice||se430VRWorkshop().inspect().message||'Manual mesh operation complete.');se340SyncUI();se340Publish();return true;
}
function se430ChooseManualOperation(operation){
 const s=se340XR;if(!Object.hasOwn(se430VRDefaults,operation))return false;
 const pending=se430VRWorkshop().inspect().preview;
 if(pending.active)se430VRWorkshop().cancel('Operation changed; uncommitted preview canceled.');
 s.se430Operation=operation;s.se430Amount=se430VRDefaults[operation];s.page='manual-operation';s.helpVisible=false;s.se430Learning=null;
 const availability=se430VRWorkshop().inspect().operations[operation];
 se340Notice(availability?.available?'Set the amount, Preview, then Apply or Cancel.':availability?.reason||'Select an eligible editable surface.');
 se340SyncUI();se340Publish();return true;
}
se340CancelGesture=function(message='Edit canceled.'){
 const native=se430VRWorkshop().inspect(),pending=!!native.preview.active;
 if(pending)se430VRWorkshop().cancel(message);
 se430DropRegionVisual();se340XR.se430Learning=null;
 if(!pending)se340XR.se430Manual=false;
 return se430PreviousCancel(message)||pending;
};
se340BeginGesture=function(record,purpose='grab'){
 if(se340XR.se430Manual){
  const pose=se340GripPose(record);if(pose&&se372MenuDragStart(record,pose))return true;
  if(purpose==='pan'&&!se430VRWorkshop().inspect().preview.active)return se350BeginView(record);
  return false;
 }
 return se430PreviousBegin(record,purpose);
};
se340Trigger=function(record,additive=false){
 const s=se340XR;if(!s.se430Manual)return se430PreviousTrigger(record,additive);
 if(se360MenuContact(record))return se430PreviousTrigger(record,additive);
 if(additive)return;
 if(se430VRWorkshop().inspect().preview.active){se340Notice('Review the preview, then choose Apply or Cancel before selecting another face.');return;}
 const hit=se340Hit(record,true);
 if(!hit?.id||!Number.isInteger(hit.faceIndex)){se340Notice('Point at an editable mesh face to select its connected flat region.');return;}
 se430ManualResult(se430VRWorkshop().selectRegion(hit.faceIndex,hit.id),'Flat face region selected · choose Inset, then Preview and Apply.');
};
se340ModelXRAction=function(action,record=null){
 const s=se340XR;if(!s.session||!s.scene||!se340VisibleSession())return false;
 if(action==='manual-mesh'){
  se340CancelGesture('Previous preview canceled before manual modeling.');s.se430Manual=true;s.mode='manual-mesh';s.page='manual-mesh';s.helpVisible=false;s.se430Learning=null;s.paletteVisible=true;s.ui.closeWheel();s.wheel=null;
  se340Notice('Manual mesh tools · convert a plain primitive, then Trigger a flat face. Inset leaves inner faces selected for Extrude.');se340SyncUI();se340Publish();return true;
 }
 if(action.startsWith('manual-')){
  if(!s.se430Manual)return false;
  const api=se430VRWorkshop();
  if(action==='manual-convert')return se430ManualResult(api.convert(),'Converted plain geometry · UV coordinates regenerated · point and Trigger a flat face.');
  if(action==='manual-pick'){
   api.cancel('Selection armed; preview canceled.');s.helpVisible=false;s.se430Learning=null;
   se340Notice('Point into the model and Trigger a connected flat face region. After Inset, keep the selected inner faces for Extrude.');se340SyncUI();return true;
  }
  if(action==='manual-learn'){
   s.se430Learning=s.se430Operation;s.helpVisible=true;s.paletteVisible=true;se340SyncUI();se340Publish();return true;
  }
  if(action==='manual-preview')return se430ManualResult(api.preview(s.se430Operation,{amount:s.se430Amount}),'Live geometry preview · source unchanged · Apply commits one Undo step; Cancel restores.');
  if(action==='manual-apply')return se430ManualResult(api.apply(),'Applied native mesh edit · inner/result faces stay selected · Undo restores the previous mesh.');
  if(action==='manual-cancel')return se430ManualResult(api.cancel(),'Preview canceled · committed source and history retained.');
  if(action==='manual-amount-minus'||action==='manual-amount-plus'||action==='manual-direction'){
   if(api.inspect().preview.active)api.cancel('Amount changed; preview canceled before rebuilding.');
   const op=s.se430Operation,step=op==='inset'?.025:.025;
   if(action==='manual-direction'&&op==='extrude')s.se430Amount=-s.se430Amount;
   else if(action!=='manual-direction')s.se430Amount=THREE.MathUtils.clamp(+(s.se430Amount+(action.endsWith('plus')?step:-step)).toFixed(4),op==='inset'?.03:op==='extrude'?-4:.005,op==='inset'?.8:4);
   if(op==='extrude'&&Math.abs(s.se430Amount)<.005)s.se430Amount=.025;
   se340SyncUI();se340Publish();return true;
  }
  const op=action.slice(7);return se430ChooseManualOperation(op);
 }
 if(s.se430Manual&&(action==='undo'||action==='redo')&&se430VRWorkshop().inspect().preview.active){
  se430VRWorkshop().cancel('Uncommitted manual preview canceled.');se340Notice('Preview canceled · press again to '+action+'.');se350Invalidate();se340SyncUI();return true;
 }
 if(action==='help'){s.se430Learning=null;return se430PreviousAction(action,record);}
 if(s.se430Manual&&(action==='focus'||action==='recenter'||action.startsWith('view-'))){
  const page=s.page;se430VRWorkshop().cancel('Preview canceled before framing the model.');
  const result=se430PreviousAction(action,record);s.se430Manual=true;s.mode='manual-mesh';s.page=page;s.se430Learning=null;
  se350Invalidate();se340SyncUI();se340Publish();return result;
 }
 const sourceSafe=['palette','menu-hide','menu-reset','cancel','undo','redo','focus','recenter'];
 if(s.se430Manual&&!sourceSafe.includes(action)&&!action.startsWith('display-')&&!action.startsWith('view-')){
  se430VRWorkshop().cancel('Manual preview canceled before switching tools.');s.se430Manual=false;s.se430Learning=null;se430DropRegionVisual();
 }
 if(['mirror','preview'].includes(action)){se340Notice(action==='mirror'?'General mirror is incomplete. Sculpt X symmetry is available in its native brush settings.':'Use Manual mesh tools → Preview for supported face operations.',true);return true;}
 return se430PreviousAction(action,record);
};
se350Dispatch=function(sample){
 if(!se340XR.se430Manual)return se430PreviousDispatch(sample);
 if(sample.profileChanged){se430VRWorkshop().cancel('Controller profile changed; manual preview canceled.');se340XR.se430Manual=false;se430DropRegionVisual();}
 const events=sample.events.filter(e=>e.action!=='multiselect'||se360MenuContact(e.source?.record||se350Record(e.hand)));
 se340XR.se372Sweep=null;return se430PreviousDispatch({...sample,events});
};
se340ModelXRInspect=function(options={}){
 const result=se430PreviousInspect(options);result.manual={active:!!se340XR.se430Manual,operation:se340XR.se430Operation,amount:se340XR.se430Amount,learning:se340XR.se430Learning,native:se430VRWorkshop().inspect()};return result;
};
/* SE430_MODEL_VR_MANUAL_WORKSHOP_END */
