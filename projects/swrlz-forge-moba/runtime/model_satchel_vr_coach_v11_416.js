/* SE416_SATCHEL_VR_COACH_START
 * One scene-owned stationary quest window. Adds a contextual second action
 * row, material/color editing on the real selected mesh, and deliberate
 * grip-drag of this panel only (not the camera, model, or native tool menu).
 */
(function se415SatchelVRCoach(){
 'use strict';
 const quest=()=>se340XR.se413Quest,academy=()=>window.SWYRL_E_SATCHEL_ACADEMY_416,
  native=()=>window.SWYRL_E_SATCHEL_NATIVE_416;
 const groupActions=[
  ['se415-show','SHOW','eye'],['se415-ghost','GHOST','cube'],
  ['se415-checkpoint','CHECKPOINT','duplicate'],['se415-restore','RESTORE','undo']
 ];
 const materialActions=[
  ['se415-leather','LEATHER','leather'],['se415-metal','METAL','detail'],
  ['se415-shade-plus','SHADE +','star'],['se415-shade-minus','SHADE -','leather']
 ];
 function install(box,makeButton){
  if(!box||box.se415Installed)return;
  box.se415Installed=true;box.coachMode='guide';box.confirmRestore=false;box.drag=null;
  const options=[...groupActions.map(r=>[r[0],'guide']),...materialActions.map(r=>[r[0],'material'])];
  for(let i=0;i<options.length;i++){
   const [id,mode]=options[i],n=i%4;
   makeButton(box,id,34+n*242,605,218,43);
   box.buttons.at(-1).userData.se415Coach=mode;
  }
  makeButton(box,'se415-mode',737,17,142,84);
  box.buttons.at(-1).userData.se415Coach='mode';
 }
 function colorFor(mode){return mode==='material'?'#77543b':'#4c405f';}
 function draw(c,box,index){
  if(!box||box.folded)return;
  const ui=se340XR.ui,mode=box.coachMode==='material'&&index===5?'material':'guide';
  if(index===5){
   c.beginPath();c.roundRect(738,18,139,82,14);
   c.fillStyle='#4d3b70';c.fill();
   c.strokeStyle='#c8addd';c.lineWidth=2;c.stroke();
   c.fillStyle='#fff8fc';c.font='bold 24px system-ui,sans-serif';c.textAlign='center';
   c.fillText(mode==='guide'?'MATERIALS':'GUIDE',807,66);c.textAlign='left';
  }
  const actions=mode==='material'?materialActions:groupActions;
  for(let i=0;i<actions.length;i++){
   const [action,label,icon]=actions[i],x=34+i*242,y=605,w=218,h=43;
   c.beginPath();c.roundRect(x,y,w,h,9);
   c.fillStyle=colorFor(mode);c.fill();
   c.strokeStyle='#9e81bd';c.lineWidth=2;c.stroke();
   if(ui?.drawGuideIcon)ui.drawGuideIcon(c,action,x+26,y+22,30,'#e5ffe9');
   c.fillStyle='#fff';c.font='bold 21px system-ui,sans-serif';c.textAlign='left';
   const text=action==='se415-restore'&&box.confirmRestore?'CONFIRM RESTORE':label;
   c.fillText(text,x+52,y+29);
  }
 }
 function showNote(result,box){
  box.message=(result?.message||'Tool action did not complete.').slice(0,200);
  if(result?.changed){try{se340SyncUI();se340Publish();}catch(_){}}
  return !!result?.ok;
 }
 function action(action,record=null){
  const box=quest(),api=academy();if(!box||!api||box.folded)return false;
  let result={ok:false,message:'Choose an Apprentice Satchel tool.'};
  if(action==='se415-mode'){box.coachMode=box.coachMode==='material'?'guide':'material';box.confirmRestore=false;
   result={ok:true,message:box.coachMode==='material'?'Materials: select the mesh, then choose Leather, Metal or a shade.':'Interactive guidance controls restored.'};}
  else if(action==='se415-show')result=api.showMe(box.index,true);
  else if(action==='se415-ghost'){
   result={ok:true,message:api.setGhost(!api.ghost())?'Transparent modeling ghost ON; this is not editable geometry.':'Ghost hidden.'};
  }else if(action==='se415-checkpoint')result=api.saveCheckpoint();
  else if(action==='se415-restore'){
   if(box.confirmRestore){result=api.restoreCheckpoint({confirmed:true});box.confirmRestore=false;}
   else{result=api.restoreCheckpoint();box.confirmRestore=!!result.requiresConfirmation;}
  }else if(action==='se415-leather')result=native()?.paint('matte','#916b48');
  else if(action==='se415-metal')result=native()?.paint('metal','#c9a56c');
  else if(action==='se415-shade-plus')result=native()?.shade(1);
  else if(action==='se415-shade-minus')result=native()?.shade(-1);
  else return false;
  const ok=showNote(result,box);
  se340Pulse(record,.17,22);
  // The original VR quest renderer refreshes at its next native frame.
  box.signature='';return ok;
 }
 const baseBegin=se340BeginGesture,baseUpdate=se340UpdateGesture,baseFinish=se340FinishGesture;
 se340BeginGesture=function(record,...args){
  const box=quest(),hit=box&&se340Hit(record,false);
  if(box&&!box.folded&&hit?.quest&&record?.gripTracked&&!se340XR.gesture){
   const pose=se340GripPose(record);
   if(pose){
    box.drag={record,origin:box.root.position.clone(),hand:pose.position.clone()};
    box.message='Grip the quest window and move your hand to reposition it. Release to keep it in world space.';
    box.signature='';return true;
   }
  }
  return baseBegin.call(this,record,...args);
 };
 se340UpdateGesture=function(...args){
  const value=baseUpdate.apply(this,args),box=quest(),drag=box?.drag;
  if(!drag)return value;
  if(!drag.record?.held||!drag.record?.gripTracked||!se340VisibleSession()){
   box.drag=null;box.message='Quest window move canceled; the model was not changed.';box.signature='';return value;
  }
  const pose=se340GripPose(drag.record);if(!pose)return value;
  const delta=pose.position.clone().sub(drag.hand);
  if(delta.length()>.85)delta.setLength(.85);
  box.root.position.copy(drag.origin).add(delta);
  box.root.updateWorldMatrix(true,true);
  return value;
 };
 se340FinishGesture=function(record,...args){
  const box=quest();
  if(box?.drag?.record===record){
   box.drag=null;box.message='Quest window placed independently in world space.';box.signature='';return true;
  }
  return baseFinish.call(this,record,...args);
 };
 const baseCleanup=se340Cleanup;
 se340Cleanup=function(...args){
  const box=quest();if(box)box.drag=null;
  academy()?.clearHighlight?.();return baseCleanup.apply(this,args);
 };
 window.SWYRL_E_SATCHEL_VR_COACH_416=Object.freeze({
  install,draw,action,
  status:()=>({active:!!quest(),coachMode:quest()?.coachMode||null,dragging:!!quest()?.drag,
   ghost:!!academy()?.ghost?.(),panelWorldSpace:true})
 });
})();
 /* SE416_SATCHEL_VR_COACH_END */