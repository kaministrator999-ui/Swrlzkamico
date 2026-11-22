/* §E v11.544 — safe, user-triggered material recovery for the existing
   v11.542 UV-compatible humanoid. This lives inside native ModelAtelier,
   so checkpoint/Undo/paint validation and project ownership stay native. */
const se544ExpectedUV=[
 [0,.056564],[1,.824816],[2,.056732],[3,.861018],
 [125,.408344],[126,.462430],[8001,.740446],
 [8002,.057381],[15999,.229167],[16000,.337147],
 [17582,.288847],[17583,.704507]
];
function se544HasOriginalUVs(part){
 const mesh=part?.topologyMesh;
 if(currentProject?.canonicalId!=='robotic-humanoid-mannequin'||
    part?.id!=='humanoid-body-unified'||part?.kind!=='topologyMesh'||
    mesh?.positions?.length!==8792*3||mesh?.indices?.length!==13932*3||
    mesh?.uvs?.length!==8792*2)return false;
 return se544ExpectedUV.every(([i,v])=>
   Math.abs(mesh.uvs[i]-v)<=.00001);
}
let se544Applying=false;
async function se544RestoreMannequinPaint(){
 const target=se336SelectedMesh(),part=target?.part;
 if(se544Applying||!se544HasOriginalUVs(part)){
  status('This repair requires the existing 84-chart humanoid UV layout. Select the original body; edited/remapped UVs are not overwritten.',true);
  return false;
 }
 if(!confirm('Replace only this mannequin’s painted texture with the correctly mapped robotic material? Your original paint remains available through Undo until you save. Geometry and UVs will not change.'))
   return false;
 se544Applying=true;
 const id=part.id;
 try{
  const response=await fetch(new URL('scenes/model-atelier-futuristic-humanoid-v11-544.swyrl.json',document.baseURI),{cache:'no-cache'});
  if(!response.ok)throw Error('Cannot fetch factory material ('+response.status+').');
  const scene=await response.json();
  if(scene.version!==11.544||scene.project?.canonicalId!=='robotic-humanoid-mannequin')
   throw Error('Factory texture source failed verification.');
  const factory=scene.project.modelAtelier.parts[0],png=factory?.uvPaintPNG;
  if(typeof png!=='string'||png.length>360000||!/^data:image\/png;base64,[A-Za-z0-9+/=]+$/.test(png))
   throw Error('Factory texture PNG failed native-size validation.');
  if(partById(id)!==part||selection!==id||!se544HasOriginalUVs(part))
   throw Error('The selected model changed during the repair.');
  const before=part.uvPaintPNG,offset=part.uvPaintOffset,repeat=part.uvPaintRepeat;
  part.uvPaintPNG=png;
  delete part.uvPaintOffset;delete part.uvPaintRepeat;
  const valid=checkPart(part);
  part.uvPaintPNG=before;
  if(offset===undefined)delete part.uvPaintOffset;
  else part.uvPaintOffset=offset;
  if(repeat===undefined)delete part.uvPaintRepeat;
  else part.uvPaintRepeat=repeat;
  if(!valid)throw Error('Native part schema rejected factory texture.');
  checkpoint();
  part.uvPaintPNG=png;
  delete part.uvPaintOffset;delete part.uvPaintRepeat;
  signalEdited();
  select(id);
  status('Corrected 3D-anchored paint applied to existing mannequin; UVs and geometry unchanged. Undo restores previous material. Save Project to keep the repair.');
  return true;
 }catch(e){
  console.error('§E mannequin factory paint',e);
  status('Could not repair mannequin texture: '+String(e.message||e),true);
  return false;
 }finally{se544Applying=false;se544RefreshRepair();}
}
function se544RefreshRepair(){
 const button=document.getElementById('se544RepairMannequinPaint');
 if(button){
  button.disabled=se544Applying||!se544HasOriginalUVs(se336SelectedMesh()?.part);
  button.title='Replace only the current 84-chart mannequin PNG. Preserves geometry, UVs, Undo and account projects.';
 }
}
function se544MountRepair(){
 const host=document.querySelector('#se356UVPreview .se356-uv-preview-actions');
 if(!host)return;
 let button=document.getElementById('se544RepairMannequinPaint');
 if(!button){
  button=document.createElement('button');button.id='se544RepairMannequinPaint';
  button.type='button';button.textContent='Restore mapped robot texture';
  button.style.minHeight='34px';
  button.addEventListener('click',se544RestoreMannequinPaint);
 }
 if(button.parentElement!==host)host.append(button);
 se544RefreshRepair();
}
const se544PriorEnsurePanel=ensurePanel;
ensurePanel=function(){
 const result=se544PriorEnsurePanel.apply(this,arguments);
 se544MountRepair();
 if(panel&&!panel.dataset.se544RepairWatch){
  panel.dataset.se544RepairWatch='1';
  const observe=new MutationObserver(records=>{
   if(records.some(rec=>Array.from(rec.addedNodes).some(node=>
      node.nodeType===1&&(node.id==='se356UVPreview'||
      node.id==='modelAtelierUVLayout'||node.querySelector?.('#se356UVPreview')))))
      se544MountRepair();
  });
  observe.observe(panel,{childList:true,subtree:true});
  panel.addEventListener('change',()=>queueMicrotask(se544RefreshRepair),true);
 }
 return result;
};
const se544PriorRefreshInspector=refreshInspector;
refreshInspector=function(){
 const result=se544PriorRefreshInspector.apply(this,arguments);
 se544RefreshRepair();
 return result;
};
window.SWYRL_E_MANNEQUIN_PAINT_REPAIR_544=Object.freeze({
 restore:se544RestoreMannequinPaint,
 compatible:()=>se544HasOriginalUVs(se336SelectedMesh()?.part)
});
/* SE544_MAPPED_MANNEQUIN_REPAIR_END */
