/* SE390_MODEL_VR_FLUENT_TOOLS_START */
// Intentional native edits: select -> Grab, scoped transform cycling, and
// placement previews. All updates use the existing XR loop and native history.
se340XR.se390Creation=null;
se340XR.se390AxisLatch=null;
const se390CreateAPI=()=>ModelAtelier.vrCreate;
const se390BaseAction=se340ModelXRAction,se390BaseTrigger=se340Trigger;
const se390BaseCancel=se340CancelGesture,se390BaseDispatch=se350Dispatch;
const se390BaseNavigate=se350Navigate,se390BaseFinish=se340FinishGesture;
const se390BaseInspect=se340ModelXRInspect;
function se390NoticeError(result){
 const reason=String(result?.error||result?.reason||'Operation unavailable.');
 se340Notice(reason.replaceAll('_',' ').toLowerCase(),true);return false;
}
function se390SelectRecord(sample=se340XR.inputSample){
 const profile=window.SWYRL_VR_CONTROLS?.currentProfile?.(),row=profile?.bindings?.model?.find(r=>r[0]==='select');
 const keys=String(row?.[1]||'').split(':')[1]?.split('+')||[],key=keys.find(k=>k.endsWith('T'))||keys[0];
 const side=key?(['LT','LG','LS','X','Y'].includes(key)?'left':'right'):(profile?.dominantHand==='left'?'left':'right');
 return se350Record(side)||sample?.events?.find(e=>e.action==='select')?.source?.record;
}
function se390DisposeCreation(c,committed=false){
 if(!c)return;
 c.ghost?.removeFromParent();c.geometry?.dispose();c.edges?.dispose();c.material?.dispose();c.edgeMaterial?.dispose();
 if(!committed)se390CreateAPI()?.cancel?.(c.draft);
}
function se390CancelCreation(){
 const s=se340XR,c=s.se390Creation;if(!c)return false;
 s.se390Creation=null;se390DisposeCreation(c);s.mode='inspect';s.page='create';return true;
}
function se390CreationKeys(record){
 if(record?.se390SelectKeys?.length)return [...record.se390SelectKeys];
 const profile=window.SWYRL_VR_CONTROLS?.currentProfile?.();
 const row=profile?.bindings?.model?.find(r=>r[0]==='select');
 const match=/^(?:tap|hold):([A-Z]+)$/.exec(row?.[1]||'');
 return match?[match[1]]:[record?.input?.handedness==='left'?'LT':'RT'];
}
function se390ArmCreate(kind,record=null){
 const s=se340XR;
 if(!['box','sphere','cylinder','cone'].includes(kind))return false;
 se340CancelGesture('Previous preview canceled.');
 // Either hand may press a menu button; placement follows the profile's
 // primary selection controller, so the other hand never strands a draft.
 record=se390SelectRecord()||record;
 if(!record?.targetTracked||!record.gripTracked){se340Notice('Track a controller and choose the shape again.',true);return false;}
 const draft=se390CreateAPI().draft(kind,{color:'#bca4ed'});if(!draft?.ok)return se390NoticeError(draft);
 const preview=se390CreateAPI().previewGeometry(draft);if(!preview?.ok){se390CreateAPI().cancel(draft);return se390NoticeError(preview);}
 const geometry=preview.geometry;geometry.computeBoundingBox();
 const size=geometry.boundingBox.getSize(new THREE.Vector3()),root=se350Root();root.updateWorldMatrix(true,false);
 const worldScale=root.getWorldScale(new THREE.Vector3()),extent=Math.max(.001,size.x,size.y,size.z);
 const unit=THREE.MathUtils.clamp(.14/(extent*Math.max(.001,worldScale.x,worldScale.y,worldScale.z)),.0051,20);
 const material=new THREE.MeshStandardMaterial({color:draft.part.color,transparent:true,opacity:.42,roughness:.65,depthWrite:false,side:THREE.DoubleSide});
 const ghost=new THREE.Mesh(geometry,material);ghost.name='Model VR · uncommitted '+kind;ghost.userData.editorOnly=true;ghost.matrixAutoUpdate=false;
 const edges=new THREE.EdgesGeometry(geometry),edgeMaterial=new THREE.LineBasicMaterial({color:0x9ffff0,transparent:true,opacity:.9,depthTest:false});
 const wire=new THREE.LineSegments(edges,edgeMaterial);wire.renderOrder=9300;ghost.add(wire);s.scene.add(ghost);
 const cast=se340Cast(record),depth=THREE.MathUtils.clamp(cast?cast.ray.origin.distanceTo(s.rig.position):.8,.25,2.2);
 s.se390Creation={draft,kind,record,geometry,material,ghost,edges,edgeMaterial,depth,unit,factor:1,yaw:0,
  keys:se390CreationKeys(record),awaitRelease:true,documentToken:se340Bridge().inspect().documentToken,revision:se340Bridge().inspect().revision};
 s.mode='create';s.page='create';s.ui.closeWheel();s.wheel=null;
 se390CreationFrame(s,0);se340Notice('Place '+kind+' · point into the workspace, release then press Trigger to confirm · B cancels.');
 se340SyncUI();se340Publish();return true;
}
function se390CreationFrame(s,dt){
 const c=s.se390Creation;if(!c)return;
 const native=se340Bridge().inspect();
 if(!se340VisibleSession()||!c.record.targetTracked||!c.record.gripTracked||native.documentToken!==c.documentToken||native.revision!==c.revision){
  se390CancelCreation();se340Notice('Tracking or source changed · creation preview canceled.');return;
 }
 if(c.awaitRelease&&c.keys.every(k=>!s.inputSample?.buttons?.[k]?.physical))c.awaitRelease=false;
 const cast=se340Cast(c.record);if(!cast)return;
 const point=se350Root().worldToLocal(cast.ray.at(c.depth,new THREE.Vector3()));
 c.draft.part.position=point.toArray().map(v=>THREE.MathUtils.clamp(s.snap?Math.round(v/.01)*.01:v,-100,100));
 c.draft.part.rotation=[0,c.yaw,0];
 c.draft.part.scale=[1,1,1].map(()=>THREE.MathUtils.clamp(c.unit*c.factor,.0051,20));
 const local=new THREE.Matrix4().compose(new THREE.Vector3(...c.draft.part.position),new THREE.Quaternion().setFromEuler(new THREE.Euler(...c.draft.part.rotation)),new THREE.Vector3(...c.draft.part.scale));
 c.ghost.matrix.copy(se350Root().matrixWorld).multiply(local);c.ghost.matrixWorldNeedsUpdate=true;c.ghost.updateWorldMatrix(true,true);
}
function se390CommitCreation(record){
 const s=se340XR,c=s.se390Creation;if(!c||c.record!==record||c.awaitRelease)return false;
 se390CreationFrame(s,0);if(s.se390Creation!==c)return false;
 const result=se390CreateAPI().commit(c.draft,c.documentToken);
 if(!result?.ok){se390CancelCreation();return se390NoticeError(result);}
 s.se390Creation=null;se390DisposeCreation(c,true);se350Invalidate();s.mode='grab';s.page='tools';
 se340Notice('Created '+c.kind+' · grip moves and turns it · A cycles axis tools.');se340Pulse(record,.35,28);se340Publish();return true;
}
function se390BeginGrab(record,purpose,pose){
 const s=se340XR;if(purpose==='pan')return se350BeginView(record);
 const chosen=se350Tools().selection();if(!chosen.ids.length){se340Notice('Point and select a mesh first, then grip to grab.');return false;}
 const result=se350Tools().beginGroup(undefined,'two-hand');if(!result?.ok)return se390NoticeError(result);
 const root=se350Root();root.updateWorldMatrix(true,false);
 const g={kind:'group',record,id:chosen.primaryId||chosen.ids[0],mode:'grab',hand:pose,
  rootInverse:root.matrixWorld.clone().invert(),rootQuaternion:root.getWorldQuaternion(new THREE.Quaternion())};
 s.gesture=g;se390BeginPose(g,pose);se372GuideStart(g);
 se340Notice('Grab · move and turn · right stick sizes · left trigger slows · release applies; B cancels.');se340Pulse(record,.2,20);return true;
}
function se390UpdatePose(g,pose,gain){
 const s=se340XR,axes=s.inputSample?.axes||{},axis=axes.orbit||axes.zoom;
 const value=g.mode==='grab'&&axis?axis.y:0;
 if(value)s.se390AxisLatch={keys:axis.keys||[],action:axes.orbit?'orbit':'zoom'};
 const candidate=se390PoseCandidate(g,pose,{gain,dt:s.frameDt||0,scaleAxis:value,snap:s.snap,snapDegrees:s.inputSample?.thresholds.snapDegrees??15});
 const translation=new THREE.Vector3(...candidate.translation),rotation=new THREE.Quaternion(...candidate.rotation);
 se372Constrain(g,translation,rotation);se372GuideUpdate(g,translation,rotation,candidate.scale);
 const result=se350Tools().updateGroup({translation:translation.toArray(),rotation:rotation.toArray(),scale:candidate.scale});
 if(!result?.ok)se340CancelGesture(result.error||'The source changed; preview canceled.');
}
function se390UpdateExtrude(g,pose,gain){
 const state=g.se390Extrude||(g.se390Extrude={position:g.hand.position.clone(),gain,depth:0});
 if(state.gain!==gain){state.position.copy(pose.position);state.gain=gain;}
 else{const delta=pose.position.clone().applyMatrix4(g.rootInverse).sub(state.position.clone().applyMatrix4(g.rootInverse));
  state.depth+=delta.dot(g.normal)*gain;state.position.copy(pose.position);}
 const result=se350Surface().extrudeUpdate(state.depth);if(!result?.ok)se340CancelGesture(result.error);
}
function se390PairCandidate(g,mid,span,gain){
 const p=g.se390Pair||(g.se390Pair={mid:g.pair.mid.clone(),span:g.pair.span.clone(),gain,
  translation:new THREE.Vector3(),rotation:new THREE.Quaternion(),logScale:0});
 if(p.gain!==gain){p.mid.copy(mid);p.span.copy(span);p.gain=gain;}
 else{
  p.translation.add(mid.clone().applyMatrix4(g.rootInverse).sub(p.mid.clone().applyMatrix4(g.rootInverse)).multiplyScalar(gain));
  p.logScale+=Math.log(span.length()/p.span.length())*gain;
  const world=new THREE.Quaternion().setFromUnitVectors(p.span.clone().normalize(),span.clone().normalize());
  const local=g.rootQuaternion.clone().invert().multiply(world).multiply(g.rootQuaternion);
  p.rotation.premultiply(new THREE.Quaternion().slerp(local,gain)).normalize();p.mid.copy(mid);p.span.copy(span);
 }
 return {translation:p.translation.toArray(),rotation:p.rotation.toArray(),scale:Math.exp(THREE.MathUtils.clamp(p.logScale,-9,9))};
}
function se390Duplicate(record=null){
 const s=se340XR;if(s.gesture||s.se390Creation){se340CancelGesture('Preview canceled · release controls and repeat Duplicate.');return true;}
 const ids=se350Tools().selection().ids;if(!ids.length){se340Notice('Select one or more meshes before duplicating.');return true;}
 const root=se350Root();root.updateWorldMatrix(true,false);
 const inverse=root.matrixWorld.clone().invert(),delta=s.right.clone().multiplyScalar(.07).applyMatrix4(inverse).sub(new THREE.Vector3().applyMatrix4(inverse));
 const result=se390CreateAPI().duplicate(ids,{translation:delta.toArray(),documentToken:se340Bridge().inspect().documentToken});
 if(!result?.ok)return se390NoticeError(result);
 s.ui.closeWheel();s.wheel=null;s.mode='grab';s.page='tools';se350Invalidate();
 se340Notice('Duplicated '+result.ids.length+' mesh'+(result.ids.length===1?'':'es')+' · new copies selected · grip to place.');se340Pulse(record,.3,25);se340SyncUI();se340Publish();return true;
}
se340CancelGesture=function(message='Edit canceled.'){
 const created=se390CancelCreation();se340XR.se372Sweep=null;
 return se390BaseCancel(message)||created;
};
se340Trigger=function(record,additive=false){
 const s=se340XR,c=s.se390Creation;
 if(c){const hit=se340Hit(record,false);if(hit?.ui)return se390BaseTrigger(record,additive);if(!additive)return se390CommitCreation(record);return;}
 const wasInspect=s.mode==='inspect';se390BaseTrigger(record,additive);
 const hit=record.se372TriggerHit;
 if(wasInspect&&!additive&&hit?.id&&!hit.ui&&!s.gesture&&se350Tools().selection().ids.includes(hit.id)){
  s.mode='grab';se340Notice('Grab ready · grip moves and turns selection · A cycles Move, Rotate, Scale.');se340SyncUI();se340Publish();
 }
};
se340ModelXRAction=function(action,record=null){
 const s=se340XR;if(!s.session||!s.scene||!se340VisibleSession())return false;
 if(action==='create-menu'){
  se340CancelGesture('Preview canceled before creation.');s.ui.closeWheel();s.wheel=null;s.page='create';s.helpVisible=false;s.paletteVisible=true;se340PlacePalette(s.lastViewer||s.anchor);
  se340Notice('Create · choose a shape, aim in the workspace, then Trigger to place.');se340SyncUI();se340Publish();return true;
 }
 if(action.startsWith('create-'))return se390ArmCreate(action.slice(7),record);
 if(action==='duplicate')return se390Duplicate(record);
 if(action==='grab'){
  se340CancelGesture('Previous preview canceled.');s.mode='grab';s.page='tools';s.helpVisible=false;
  se340Notice('Grab selected · grip moves and turns; right stick sizes; left trigger slows.');se340SyncUI();se340Publish();return true;
 }
 if((action==='undo'||action==='redo')&&s.se390Creation){
  se340CancelGesture('Placement canceled · press again to '+action+'.');se340SyncUI();se340Publish();return true;
 }
 if(s.se390Creation&&(action==='selector'||action.startsWith('selector-')||['tools','studio','projects','views','cameras','aim','help'].includes(action)))
  se340CancelGesture('Creation preview canceled before changing workspace tools.');
 if(action==='next-tool'){
  const list=['move','rotate','scale'];action=list[(list.indexOf(s.mode)+1)%list.length];
 }
 return se390BaseAction(action,record);
};
se350Dispatch=function(sample){
 const s=se340XR;if(sample.cancel)return se390BaseDispatch(sample);
 const events=[];
 for(const event of sample.events){
  const record=event.source?.record||se350Record(event.hand);
  if(['select','stroke'].includes(event.action)&&record)record.se390SelectKeys=[...event.keys];
  if(event.cancelled){if(['grab','pan','stroke','two-hand'].includes(event.action)&&s.gesture)se340CancelGesture('Shortcut changed · unfinished preview canceled.');continue;}
  if(['create-menu','duplicate'].includes(event.action)&&event.phase!=='end'){
   const triggerKey=event.keys.find(k=>k.endsWith('T')),triggerRecord=triggerKey?sample.buttons?.[triggerKey]?.source?.record:null;
   if(event.action==='duplicate'&&triggerRecord&&se340Hit(triggerRecord,false)?.ui){se340Trigger(triggerRecord);continue;}
   se340ModelXRAction(event.action,triggerRecord||record);continue;
  }
  events.push(event);
 }
 const result=se390BaseDispatch({...sample,events}),sweep=s.se372Sweep;
 const sweepEvent=events.find(e=>e.action==='multiselect'&&e.phase!=='end'&&e.source?.record===sweep?.record);
 if(sweepEvent)sweep.keys=[...sweepEvent.keys];
 return result;
};
se350Navigate=function(sample,dt){
 const s=se340XR,c=s.se390Creation;
 if(c){const axis=sample.axes.orbit||sample.axes.zoom;
  if(axis){c.factor=THREE.MathUtils.clamp(c.factor*Math.exp(-axis.y*dt*1.4),.1,10);c.yaw+=axis.x*dt*1.3;s.se390AxisLatch={keys:axis.keys||[],action:sample.axes.orbit?'orbit':'zoom'};}
  return;
 }
 const latch=s.se390AxisLatch;
 if(latch){const axis=sample.axes[latch.action];if(!axis||Math.hypot(axis.x,axis.y)<.001)s.se390AxisLatch=null;
  else{const axes={...sample.axes};delete axes[latch.action];return se390BaseNavigate({...sample,axes},dt);}}
 return se390BaseNavigate(sample,dt);
};
se340FinishGesture=function(record){return se390BaseFinish(record);};
se340ModelXRInspect=function(options={}){
 const result=se390BaseInspect(options),c=se340XR.se390Creation;
 result.creation=c?{active:true,phase:'placing',kind:c.kind,position:[...c.draft.part.position],scale:[...c.draft.part.scale],awaitRelease:c.awaitRelease}:
  {active:false,phase:null,kind:null,position:null,scale:null,awaitRelease:false};
 result.shortcuts={transformCycle:['move','rotate','scale'],grab:'move-turn-size',creation:'create-menu',axisLatched:!!se340XR.se390AxisLatch};
 return result;
};
/* SE390_MODEL_VR_FLUENT_TOOLS_END */
