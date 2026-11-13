/* SE441_SATCHEL_LESSON_START */
// Lesson data and navigation only. Every editable mesh still comes from a
// deliberate native tool gesture and its existing Apply/Undo transaction.
const se441SatchelLesson=(()=>{
 const WORKFLOW='one-body-v1';
 const steps=[
  {title:'Meet your one-cube body',tool:'Meshes · Move / Rotate / Scale',check:'body',
   task:'Your single cube starts at useful bag proportions. Select it and try Move, Rotate or overall Scale; Undo restores it.',
   vrTask:'Trigger selects the body. Grab + Grip moves and turns it; right stick with Grip changes overall size. Try a move, then Y undoes.',
   why:'Block out the large silhouette before details. This is still one solid plain cube; you will create the cavity yourself.',
   hint:'The body is already wider than deep. Preserve that proportion; do not build separate floor or wall cubes.',
   vrHint:'Grip this quest window to move it aside. Grab scales uniformly. Save a checkpoint before face editing.'},
  {title:'Inset and hollow the same body',tool:'Topology · Manual mesh modeling',vrTool:'Mesh tools · Manual modeling',check:'cavity',
   task:'Make mesh editable. Select the top face and flat region. Inset .20, Preview, Apply. Keep inner faces selected; Extrude −.75, Preview, Apply.',
   vrTask:'Make editable → Trigger top → Inset .20 → Preview → Apply. Keep inner faces selected. Extrude −.75 → Preview → Apply.',
   why:'The inset makes a rim. Negative extrusion adds connected inner walls and a recessed floor inside this same body mesh.',
   hint:'Do not Select flat region again after Inset. A negative local depth goes inward; Preview must still leave a floor.',
   vrHint:'SHOW opens real tools. Keep the inner faces after Inset. Extrude suggests −.75 here; negative goes inward.'},
  {title:'Make a separate pointed flap',tool:'Meshes · Add / Scale / Move',vrTool:'Create · Draw outline / Thicken outline / Grab',check:'flap',
   task:'Add one wide, thin flap piece at the upper front. A pointed editable outline is optional. Keep the flap separate and inspect its rim contact.',
   vrTask:'Front view. Draw a wide pointed flap in open space; release. Thicken outline: Grip a short pull, release. Choose Grab and fit the upper front.',
   why:'A separate flap can be adjusted or animated later. Width and a readable lower tip give this simple bag character.',
   hint:'In the flat editor a thin box with numeric scale works. In VR use Draw and thickness, then Grab; no per-axis VR sizing is required.',
   vrHint:'Draw beside the bag, not through it. Ghosts show size and fit, not a tracing surface. B cancels; Y undoes.'},
  {title:'Make a strap with an empty middle',tool:'Meshes · Add / Move / Rotate',vrTool:'Create · Draw outline / Thicken outline / Grab',check:'strap',
   task:'Build an elevated strap with both ends at the bag sides and its middle empty. VR can draw one U-shaped band; flat tools can join narrow sections.',
   vrTask:'Front view. Trace OUTER U, then return on INNER U to close a band. Release; add Grip thickness. Choose Grab and fit both ends at the sides.',
   why:'A strap is a strip around empty space, not a solid filled arch or a single drawn line. Inspect its front and side silhouette.',
   hint:'Keep both ends near the side attachments. Existing segmented learner straps remain valid; no body wall boxes are needed.',
   vrHint:'Draw both edges of the strip so its center stays empty. Fit with Grab, then inspect from the side. Save a checkpoint.'},
  {title:'Fit a small clasp on the flap',tool:'Meshes · Add sphere / Move',vrTool:'Create · Sphere / Grab',check:'clasp',
   task:'Add a small sphere clasp or a thickened diamond on the flap front. Fit the actual mesh before materials. A seam or leaf detail is optional.',
   vrTask:'Create Sphere; use right stick to make it small, then Trigger places. Choose Grab and fit the flap front. A thickened diamond also works.',
   why:'A small contrasting clasp gives the flap a focal point. Geometry is checked now; its metal finish belongs to the next step.',
   hint:'Name/select the small clasp clearly. Do not apply Metal yet just to pass the geometry check.',
   vrHint:'The clasp belongs on the flap, not floating ahead of it. VERIFY checks its shape here; Metal comes next.'},
  {title:'Finish leather and metal',tool:'Meshes · Material & shape',vrTool:'Quest · Materials',check:'material',
   task:'Give the actual body and flap colored matte leather. Apply metal to the actual clasp. Use a restrained palette and inspect under the light.',
   vrTask:'Trigger body, then Leather. Trigger flap, Leather. Trigger small clasp, Metal. Shade is optional. Save a checkpoint after reviewing colors.',
   why:'Matte leather and contrasting metal read clearly without excessive geometry. Coloring an unrelated metal object does not finish the clasp.',
   hint:'Use Material and Color in the native inspector. Keep the strap leather-like; use contrast for small hardware.',
   vrHint:'SHOW opens the existing Materials row. The selected part name identifies what Leather, Metal or Shade will change.'},
  {title:'Inspect, save and reopen',tool:'Views / Projects · Save project',vrTool:'Display · Angles / Projects · Save project',
   task:'Inspect front, side, back and top. Check the cavity and attachments. Save Project, then reopen My Projects to confirm your editable model.',
   vrTask:'Inspect top, front, sides and back. Check the cavity and both strap joins. Projects → Save project. Reopen My Projects to confirm editing.',
   why:'A shape check cannot prove saving. Native Save Project preserves your independent editable lesson; Export is a separate optional step.',
   hint:'Save locally first. Save to Account is separate for another device. Mark this objective after checking your saved project.',
   vrHint:'Local Save needs no login. Save to account is separate. Mark this done only after saving and checking your project.'}
 ].map(Object.freeze);
 const active=()=>currentProject?.se412Tutorial==='satchel-001'&&window.SWYRL_ENGINE_TUTORIAL_412?.status?.().active===true;
 const current=()=>window.SWYRL_ENGINE_TUTORIAL_412?.status?.().current??0;
 function verify(index,parts){
  if(!Array.isArray(parts)||!Number.isInteger(index)||index<0||index>6)return {ok:false,message:'Open your independent satchel lesson first.'};
  const report=window.SWYRL_E_SATCHEL_WORKFLOW_441?.inspect(parts,{allowLegacy:true});
  if(!report)return {ok:false,message:'Native satchel geometry inspection is not ready; no work was changed.'};
  if(index===0){
   const seed=parts.find(p=>p.id==='model-seed')||parts.find(p=>/body|practice/i.test(p.name||''));
   const proportioned=seed&&['box','topologyMesh'].includes(seed.kind)&&Array.isArray(seed.scale)&&seed.scale.length===3&&seed.scale.every(Number.isFinite)&&seed.scale[0]>=1.2&&seed.scale[1]>=.85&&seed.scale[2]>=.35;
   return proportioned||report.body.ok?{ok:true,message:'One practice body has useful proportions. You will make its opening with real Inset and inward Extrude.'}:{ok:false,message:'Select the original body cube and keep useful bag proportions. Do not replace it with separate wall boxes.'};
  }
  if(!report.body.ok)return report.body;
  if(currentProject?.se441TutorialWorkflow===WORKFLOW&&report.body.legacy)return {ok:false,message:'This new lesson uses the same cube as one connected body: Make editable, Inset, then Extrude inward. Separate wall boxes do not complete this objective.'};
  if(index===1)return report.body;
  if(index===2)return report.flap;
  if(index===3)return report.strap;
  if(index===4)return report.flap.ok?report.clasp:{ok:false,message:'Fit a real separate flap first, then place the clasp on its front.'};
  if(index===5)return report.materials;
  const missing=['body','flap','strap','clasp','materials'].find(key=>!report[key].ok);
  if(missing)return report[missing];
  return {ok:null,message:'Shape/material checks passed. Inspect real joins and the cavity, use native Save project, then reopen My Projects. Saving cannot be proved from geometry; mark complete after checking it.'};
 }
 function amountFor(operation){return active()&&current()===1&&operation==='extrude'?-.75:null;}
 function drawName(){return active()?({2:'Satchel flap',3:'Satchel strap',4:'Satchel clasp'}[current()]||'VR outline'):'VR outline';}
 function showMe(index,vr){
  if(!active())return null;
  if(!vr){
   const navigation=[['Meshes','Select & organize'],['Topology','Manual mesh modeling'],['Meshes','Select & organize'],['Meshes','Select & organize'],['Meshes','Select & organize'],['Meshes','Material & shape'],['Meshes','Select & organize']][index];
   if(!navigation)return null;window.SWYRL_E_UNIFIED_TOOLS?.select?.(...navigation);
   const selectors=['#se320ModelTransform [data-se320-transform="move"]','#atelierContextFields [data-se430-native="modelAtelierWorkshopConvert"] button','#atelierContextProxy_modelAtelierPrimitiveKind','#atelierContextProxy_modelAtelierPrimitiveKind','#atelierContextProxy_modelAtelierPrimitiveKind','#atelierContextProxy_modelAtelierMaterial','[data-se371-controls] button:first-child'];
   if(index===1){
    const native=ModelAtelier.workshop.inspect();
    if(native.preview.active)selectors[1]='#atelierContextFields [data-se430-native="modelAtelierWorkshopApply"] button';
    else if(!native.convert.available)selectors[1]=native.selection.faceIds.length?'#atelierContextProxy_modelAtelierWorkshopOperation':'[data-component-mode="face"]';
   }
   const element=document.querySelector(selectors[index]);
   if(!element||!element.getClientRects().length)return {ok:true,message:'Opened the actual '+navigation.join(' → ')+' tools. Choose the control named in this objective.'};
   element.classList.add('se416-show-target');element.scrollIntoView?.({behavior:'smooth',block:'nearest',inline:'nearest'});
   return {ok:true,element,key:'lesson-'+index,message:'Highlighted an actual native control. You choose parameters and apply each edit yourself.'};
  }
  const s=se340XR;if(!s?.session||!s.ui)return {ok:false,message:'Enter Model VR before using its tool highlight.'};
  let action;
  if(index===1){
   const native=ModelAtelier.workshop.inspect(),part=currentProject?.modelAtelier?.parts?.find(p=>p.id===native.selection.partId);
   if(!part||part.id!=='model-seed'&&!/body|practice/i.test(part.name||''))return {ok:false,message:'Trigger the Satchel body first. SHOW will then open its real manual tools.'};
   const complete=window.SWYRL_E_SATCHEL_WORKFLOW_441?.inspect(currentProject.modelAtelier.parts);
   if(complete?.body.ok){se340ModelXRAction('tools');s.ui.highlightTutorialAction?.('focus');return {ok:true,action:'focus',message:'A real cavity is present. Inspect it from above, then VERIFY this objective; SHOW did not apply another extrusion.'};}
   if(!s.se430Manual)se340ModelXRAction('manual-mesh');
   const selection=ModelAtelier.workshop.inspect();
   if(selection.preview.active){s.page='manual-operation';action='manual-apply';}
   else if(selection.convert.available){s.page='manual-mesh';action='manual-convert';}
   else if(!selection.selection.faceIds.length){s.page='manual-mesh';action='manual-pick';}
   else{const insetDone=(part.topologyMesh?.indices?.length||0)>36;se340ModelXRAction(insetDone?'manual-extrude':'manual-inset');action='manual-preview';}
  }else if(index===5){
   const quest=s.se413Quest;if(quest){quest.coachMode='material';quest.signature='';}
   return {ok:true,message:'Materials row is open in this quest. Trigger the actual body/flap for Leather, then the clasp for Metal.'};
  }else{
   const page=index===0?'mesh':index===6?'projects':'create-menu';
   se340ModelXRAction(page);action=index===0?'grab':index===6?'save-local':index===4?'create-sphere':'draw';
  }
  s.paletteVisible=true;s.helpVisible=false;se340SyncUI();s.ui.highlightTutorialAction?.(action);se340Publish();
  return {ok:true,action,message:action==='manual-preview'?'A real geometry Preview is highlighted. Review it, then Apply or Cancel; no edit was applied by SHOW.':'Highlighted '+action+' on the actual native VR console. You perform the gesture or Apply yourself.'};
 }
 function makeGhost(group,index){
  if(!group?.isObject3D||typeof THREE==='undefined')return false;
  const add=(geometry,position=[0,0,0])=>{
   const material=new THREE.MeshBasicMaterial({color:0x75edce,wireframe:true,transparent:true,opacity:.25,depthTest:true,depthWrite:false,side:THREE.DoubleSide});
   const mesh=new THREE.Mesh(geometry,material);mesh.position.fromArray(position);mesh.userData.editorOnly=true;mesh.raycast=()=>{};mesh.name='Satchel lesson reference only';group.add(mesh);return true;
  };
  const outline=(points,z,depth)=>{const shape=new THREE.Shape();points.forEach(([x,y],i)=>i?shape.lineTo(x,y):shape.moveTo(x,y));shape.closePath();return add(new THREE.ExtrudeGeometry(shape,{depth,bevelEnabled:false,curveSegments:1}),[0,0,z]);};
  if(index===0)return add(new THREE.BoxGeometry(1.4,1,.65),[0,1.5,0]);
  if(index===1)return window.SWYRL_E_SATCHEL_CAVITY_436?.makeGhost(group)||false;
  if(index===2)return outline([[-.65,1.95],[.65,1.95],[.57,1.55],[0,1.43],[-.57,1.55]],.36,.04);
  if(index===3)return outline([[-.72,1.65],[-.72,2.80],[-.50,3.05],[.50,3.05],[.72,2.80],[.72,1.65],[.56,1.65],[.56,2.73],[.43,2.90],[-.43,2.90],[-.56,2.73],[-.56,1.65]],.32,.035);
  if(index===4)return add(new THREE.SphereGeometry(.08,16,12),[0,1.68,.405]);
  return false;
 }
 return Object.freeze({steps:Object.freeze(steps),workflow:WORKFLOW,verify,amountFor,drawName,showMe,makeGhost});
})();
window.SWYRL_E_SATCHEL_LESSON_441=se441SatchelLesson;
/* SE441_SATCHEL_LESSON_END */
