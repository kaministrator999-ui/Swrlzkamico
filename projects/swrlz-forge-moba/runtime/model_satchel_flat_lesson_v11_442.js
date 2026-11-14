/* SE442_SATCHEL_FLAT_LESSON_START */
// Flat-browser instruction and native-control navigation only. Creation,
// transforms, previews, Apply and Undo remain the learner's native gestures.
(function se442SatchelFlatLesson(){
 'use strict';
 const base=window.SWYRL_E_SATCHEL_LESSON_441;
 if(!base)return;
 const numeric='On a phone, hold a number field still for about 380 ms to open the keypad. Clear, enter the value, then tap keypad Apply. Undo reverses an actual edit.';
 const copy=[
  {tool:'Meshes · Transform',
   task:'Start in the regular browser with the one Satchel body cube. Its Position is X 0, Y 1.5, Z 0; Scale is X 1.4, Y 1, Z .65. Try a small Move or Scale, then Undo to keep these lesson proportions.',
   hint:'Size & position opens the real Transform fields. X is width, Y is height and Z is depth. '+numeric+' Keep this same body cube; the next objective hollows it.'},
  {tool:'Topology · Manual mesh modeling',
   task:'Select Satchel body. Make mesh editable, choose Face mode and Top view, then tap the top face. Select flat region to include both top triangles. Choose Inset with amount .20, Preview geometry, then Apply geometry. Keep the new inner faces selected. Choose Extrude with depth −.75, Preview, inspect the floor, then Apply.',
   hint:'Inset .20 means a 20% inset fraction; Extrude −.75 is inward local depth. Do not Select flat region again after Inset: that also includes the rim. If you lose the inner selection, Undo the Inset and repeat it while keeping its resulting faces. '+numeric+' Cancel discards a preview; Apply commits one Undo step.'},
  {tool:'Meshes · Select & organize / Transform',
   task:'Choose Cube in the primitive picker, then Add cube for one separate flap. Use Size & position: Position X 0, Y 1.75, Z .355; Scale X 1.3, Y .5, Z .06; Rotation X/Y/Z 0. This makes a thin front flap that touches the body rim.',
   hint:'Show Me opens the actual primitive picker or Add cube. Size & position opens Transform for the selected part. Name it Satchel flap using Mesh identity. Keep the body separate. '+numeric+' Inspect the front and side; the flap back at Z .325 should touch the body front.'},
  {tool:'Meshes · Select & organize / Transform',
   task:'Make a strap from three separate narrow cubes. Left leg: Position −.66, 2.37, 0; Scale .08, .98, .06. Right leg: Position .66, 2.37, 0; same Scale. Top bridge: Position 0, 2.84, 0; Scale 1.32, .08, .06. All triples are X/Y/Z; keep every Rotation at 0.',
   hint:'For each piece choose Cube → Add cube, then Size & position. You can Duplicate the first leg and change only its X position for the other leg. The top bridge joins both legs; both lower ends meet the bag sides, with the middle empty. '+numeric+' These strap pieces do not replace the one connected body.'},
  {tool:'Meshes · Select & organize / Transform',
   task:'Choose Sphere in the primitive picker, then Add sphere for a separate small clasp. Use Size & position: Position X 0, Y 1.68, Z .465; Scale X/Y/Z .08; Rotation X/Y/Z 0. The native sphere uses Scale as its radius, so this clasp is .16 across.',
   hint:'Name it Satchel clasp in Mesh identity. Its back at Z .385 touches the flap front. Check this actual fit before assigning metal. '+numeric+' Use Show Me to find Sphere/Add; Size & position opens the real numeric controls.'},
  {tool:'Appearance · Materials & colors',
   task:'Select the actual body, choose Material matte and a brown or other leather color. Do the same for the flap and strap pieces. Select Satchel clasp, choose Material metal and a contrasting hardware color. Orbit under the light to inspect the result.',
   hint:'Show Me opens the real Material and Color controls. Select each part in the mesh list or by tapping it in Object mode. Changing an unrelated metal object does not finish this clasp. Use Undo if you color the wrong part.'},
  {tool:'Views / Projects · Save Project',
   task:'Use the native Front, Side, Back and Top views to check the cavity, flap contact and both strap joins. Tap the real Save Project button. Open Projects → My Projects, reopen your editable satchel and confirm its pieces and lesson progress.',
   hint:'Show Me highlights Save Project in this Model Studio. Views opens camera controls; view changes do not edit geometry. Local Save Project needs no login. Save to Account is separate for another device. Mark this objective complete after reopening your saved project; shape checks cannot prove saving.'}
 ];
 const steps=Object.freeze(base.steps.map((row,index)=>Object.freeze({...row,vrTool:row.vrTool||row.tool,...copy[index]})));
 const current=()=>window.SWYRL_ENGINE_TUTORIAL_412?.status?.().current??0;
 const active=()=>window.SWYRL_ENGINE_TUTORIAL_412?.status?.().active===true;
 const panel=()=>document.querySelector('#modelAtelierPanel');
 const validIndex=index=>Number.isInteger(index)&&index>=0&&index<steps.length;
 const visible=element=>!!element&&!element.disabled&&!element.closest('[hidden]')&&!!element.getClientRects().length;
 function find(selectors){
  const host=panel();if(!host)return null;
  for(const selector of selectors){const element=host.querySelector(selector);if(visible(element))return element;}
  return null;
 }
 function controls(id){
  return ['#atelierContextProxy_'+id,'#atelierContextFields [data-se430-native="'+id+'"] button','#'+id];
 }
 function highlight(selectors,index,message){
  const element=find(selectors);
  if(!element)return {ok:true,message:message+' The native tools are open; scroll their settings to the named control.'};
  element.classList.add('se416-show-target');
  element.scrollIntoView?.({behavior:'smooth',block:'nearest',inline:'nearest'});
  return {ok:true,element,key:'flat-442-'+index,message};
 }
 function navigate(category,mode){
  const host=panel(),tools=window.SWYRL_E_UNIFIED_TOOLS;
  if(!host||!tools?.select)return false;
  // Reopen the actual responsive inspector with its existing toggle, rather
  // than changing layout state behind the native layout controller.
  if(host.dataset.se251RightCollapsed==='true')host.querySelector('.se251-external-collapse')?.click();
  tools.select(category,mode);
  return true;
 }
 function saveControl(){
  const button=panel()?.querySelector('[data-se371-action="save"]');
  // The native header can put file commands in its own details menu.
  // Opening that existing menu is navigation, not a save operation.
  if(button){for(let node=button.parentElement;node&&node!==panel();node=node.parentElement)if(node.tagName==='DETAILS')node.open=true;}
  return button;
 }
 function openTools(index=current(),options={}){
  if(!active()||!validIndex(index))return {ok:false,message:'Open your independent satchel lesson first.'};
  if(options?.transform||index===0){
   const ok=navigate('Meshes','Transform');
   return {ok,message:ok?'Size & position: use the actual Position, Rotation and Scale X/Y/Z fields. '+numeric:'Open Meshes → Transform in the native Model Studio.'};
  }
  if(index===6){
   saveControl();
   return {ok:true,message:'Use Save Project in the Model Studio header, then Projects → My Projects to reopen your editable lesson.'};
  }
  const route=index===1?['Topology','Manual mesh modeling']:index===5?['Appearance','Materials & colors']:['Meshes','Select & organize'];
  const ok=navigate(...route);
  return {ok,message:ok?'Opened '+route.join(' → ')+'. You choose the parameters and apply each edit yourself.':'Open '+route.join(' → ')+' in the native Model Studio.'};
 }
 function cavityShow(index){
  const workshop=window.SWYRL_ENGINE_MODEL_WORKSHOP||(typeof ModelAtelier!=='undefined'?ModelAtelier.workshop:null);
  const state=workshop?.inspect?.();
  if(!state)return {ok:false,message:'The native manual modeling tools are not ready. No model was changed.'};
  const parts=typeof currentProject!=='undefined'?currentProject?.modelAtelier?.parts:[];
  const part=parts?.find(row=>row.id===state.selection.partId);
  if(!part||(part.id!=='model-seed'&&!/body|practice/i.test(part.name||'')))
   return highlight(controls('modelAtelierParts'),index,'Select the original Satchel body in the mesh list first, then use Show Me again.');
  if(state.preview.active)
   return highlight(controls('modelAtelierWorkshopApply'),index,'Review the actual '+state.preview.operation+' preview. Apply geometry commits it; Cancel preview keeps the source. Show Me did not apply an edit.');
  if(state.convert.available)
   return highlight(controls('modelAtelierWorkshopConvert'),index,'Tap Make mesh editable for this same body cube. This explicit native edit enables face modeling; Undo can restore the primitive.');
  const completed=window.SWYRL_E_SATCHEL_WORKFLOW_441?.inspect?.(parts);
  if(completed?.body.ok&&!completed.body.legacy){
   window.SWYRL_ENGINE_MODEL_CAMERA?.setView?.('top');
   return highlight(['[data-se430-view="top"]','[data-at-view="top"]'],index,'The real connected cavity is present. Inspect the Top view and use Check my work; Show Me did not inset or extrude again.');
  }
  if(part.kind!=='topologyMesh')
   return highlight(controls('modelAtelierWorkshopConvert'),index,'Select the original plain body cube and Make mesh editable before picking its top face.');
  const faces=state.selection.faceIds||[],originalCube=(part.topologyMesh?.indices?.length||0)===36;
  if(!faces.length){
   if(state.selection.mode!=='face')workshop.setComponentMode?.('face');
   window.SWYRL_ENGINE_MODEL_CAMERA?.setView?.('top');
   return highlight(['[data-component-mode="face"]','[data-se430-view="top"]'],index,originalCube
    ?'Face mode and Top view are open. Tap the body top yourself, then Show Me can point to Select flat region. No face was picked for you.'
    :'The inner face selection was lost. Undo the Inset and repeat it, keeping its new inner faces for inward Extrude. Do not Select flat region again after Inset.');
  }
  if(originalCube&&faces.length===1)
   return highlight(controls('modelAtelierWorkshopSelectRegion'),index,'Tap Select flat region to include both original top triangles before Inset. Use this once on the original cube top; keep the inner faces after applying Inset.');
  const operation=originalCube?'inset':'extrude',amount=originalCube ? .20 : -.75;
  const nativeOperation=panel()?.querySelector('#modelAtelierWorkshopOperation');
  if(nativeOperation?.value!==operation)
   return highlight(controls('modelAtelierWorkshopOperation'),index,'Choose '+(originalCube?'Inset for the selected original top region.':'Extrude for the retained inner faces. Do not expand the flat region again.')+' Show Me does not change operation values or preview geometry.');
  const nativeAmount=panel()?.querySelector('#modelAtelierWorkshopAmount');
  if(!nativeAmount||Math.abs(Number(nativeAmount.value)-amount)>1e-8)
   return highlight(controls('modelAtelierWorkshopAmount'),index,'Set '+(originalCube?'Inset fraction .20.':'Extrude depth −.75; negative goes inward.')+' '+numeric+' Then use Preview geometry.');
  return highlight(controls('modelAtelierWorkshopPreview'),index,'Tap Preview geometry for '+(originalCube?'Inset .20':'inward Extrude −.75')+'. Inspect the preview, then Apply geometry yourself. Keep a floor and preserve the inner face selection.');
 }
 function showMe(index,vr=false){
  if(vr)return base.showMe(index,true);
  if(!active()||!validIndex(index))return null;
  const opened=openTools(index);if(!opened.ok)return opened;
  if(index===0)return highlight(controls('modelAtelierscale0'),index,'The real Transform fields are open. Keep body Scale X/Y/Z 1.4, 1, .65 after your practice edit and Undo. '+numeric);
  if(index===1)return cavityShow(index);
  if(index>=2&&index<=4){
   const kind=index===4?'sphere':'box',picker=panel()?.querySelector('#modelAtelierPrimitiveKind');
   return highlight(controls(picker?.value===kind?'modelAtelierAdd':'modelAtelierPrimitiveKind'),index,
    'Choose '+(kind==='sphere'?'Sphere':'Cube')+' in the actual primitive picker, then tap Add '+(kind==='sphere'?'sphere':'cube')+'. After creating each part, use Size & position for the lesson values. Show Me creates no geometry.');
  }
  if(index===5)return highlight(controls('modelAtelierMaterial'),index,'Select the actual body, flap or strap and use matte plus a leather color. Select the small clasp and use metal. Material and Color change the selected native part.');
  saveControl();
  return highlight(['[data-se371-action="save"]'],index,'Tap this Model Studio Save Project button, then Projects → My Projects to reopen your editable satchel. Export and Save to Account are separate choices.');
 }
 const lesson=Object.freeze({...base,steps,showMe});
 window.SWYRL_E_SATCHEL_LESSON_441=lesson;
 window.SWYRL_E_SATCHEL_FLAT_LESSON_442=Object.freeze({openTools,showMe,steps});
})();
/* SE442_SATCHEL_FLAT_LESSON_END */
