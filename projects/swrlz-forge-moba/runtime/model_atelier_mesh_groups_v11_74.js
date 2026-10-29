// §E v11.74 — non-destructive flat mesh assemblies and touch-first selection.
// Project data is plain {id,name,members[]} in modelAtelier.meshGroups.
// No mesh reparenting; all parts retain their authored world transforms/materials.
let atelierGroupScope='group'; // group: pick linked assembly, child: pick only touched member
let atelierGroupCurrent=null;
const atelierGroupLimit=96;
function atelierGroups(){return Array.isArray(model()?.meshGroups)?model().meshGroups:[];}
function atelierGroupOf(id){return atelierGroups().find(g=>g.members.includes(id))||null;}
function atelierGroupById(id){return atelierGroups().find(g=>g.id===id)||null;}
function atelierGroupsValid(groups,parts=model()?.parts||[]){
 if(!Array.isArray(groups)||groups.length>atelierGroupLimit)return false;
 const ids=new Set(parts.map(p=>p.id)),seenIds=new Set(),seenMembers=new Set();
 return groups.every(g=>{
  if(!g||typeof g!=='object'||typeof g.id!=='string'||g.id.length<1||g.id.length>90||
   typeof g.name!=='string'||g.name.length<1||g.name.length>100||
   !Array.isArray(g.members)||g.members.length<2||g.members.length>32||
   seenIds.has(g.id))return false;
  seenIds.add(g.id);
  for(const id of g.members){
   if(typeof id!=='string'||!ids.has(id)||seenMembers.has(id))return false;
   seenMembers.add(id);
  }
  return true;
 });
}
// Removal and destructive join may leave group references to absent parts.
// Prune only after a checkpoint has been taken by the calling edit.
function atelierGroupsPrune(){
 const project=model();if(!project||!Array.isArray(project.meshGroups))return;
 const alive=new Set(project.parts.map(p=>p.id)),seen=new Set();
 project.meshGroups=project.meshGroups.map(g=>({
  id:g.id,name:g.name,
  members:g.members.filter(id=>{if(!alive.has(id)||seen.has(id))return false;seen.add(id);return true;})
 })).filter(g=>g.members.length>=2);
 if(atelierGroupCurrent&&!project.meshGroups.some(g=>g.id===atelierGroupCurrent))atelierGroupCurrent=null;
}
function atelierGroupsSnapshot(){
 return JSON.stringify({parts:model().parts,meshGroups:structuredClone(atelierGroups())});
}
function atelierGroupsHistoryApply(entry){
 const data=JSON.parse(entry);
 const parts=Array.isArray(data)?data:data.parts;
 const groups=Array.isArray(data)?[]:data.meshGroups||[];
 if(!validParts(parts)||!atelierGroupsValid(groups,parts))throw Error('Invalid group/history snapshot');
 model().parts=parts;model().meshGroups=groups;
 selection=null;atelierMeshIds=[];atelierMeshAdding=false;atelierGroupCurrent=null;
}
function atelierGroupMembers(group){
 return group.members.filter(id=>!!partById(id));
}
function atelierGroupsSelect(id){
 const p=partById(id);
 if(atelierMeshAdding){
  if(!p){
   // In multi-select, tapping empty space never discards the selection.
   atelierGroupsUIRefresh();return;
  }
  if(atelierMeshIds.includes(id)){
   atelierMeshIds=atelierMeshIds.filter(x=>x!==id);
  }else if(atelierMeshIds.length<32)atelierMeshIds.push(id);
  else status('Select at most 32 meshes at once.',true);
  selection=atelierMeshIds.at(-1)||null;
  // Preserve the chosen assembly while changing its membership.
 }else{
  selection=p?id:null;
  const group=p&&atelierGroupScope==='group'?atelierGroupOf(id):null;
  atelierMeshIds=group?atelierGroupMembers(group):(p?[id]:[]);
  atelierGroupCurrent=group?.id||null;
 }
 atelierGroupsOutline();atelierSculptOverlayRefresh();atelierLassoOverlayRefresh();
 refreshList();refreshInspector();
 atelierMeshToolbarRefresh();atelierMeshPaintModeImmediately();
 atelierGroupsUIRefresh();
}
function atelierGroupsOutline(){
 if(!modelRoot)return;
 const selected=new Set(atelierMeshActiveIds());
 const helpers=modelRoot.children.filter(x=>x instanceof THREE.BoxHelper);
 for(const helper of helpers){
  modelRoot.remove(helper);helper.geometry?.dispose();helper.material?.dispose();
 }
 for(const mesh of modelRoot.children.filter(x=>x.isMesh&&selected.has(x.userData.atelierId))){
  const active=mesh.userData.atelierId===selection;
  const helper=new THREE.BoxHelper(mesh,active?0xffdc8d:0x58e3d4);
  helper.userData.atelierHelper=true;
  helper.material.depthTest=false;helper.renderOrder=32;
  modelRoot.add(helper);
 }
}
function atelierGroupsSelectFromList(ids){
 atelierMeshIds=ids.slice(0,32);
 selection=atelierMeshIds.at(-1)||null;
 atelierGroupCurrent=null;
 atelierMeshAdding=ids.length>1;
 atelierGroupsOutline();
 atelierGroupsUIRefresh();
}
function atelierGroupCreate(){
 const ids=[...new Set(atelierMeshActiveIds())];
 if(ids.length<2){status('Select at least two meshes to group.',true);return;}
 if(ids.length>32){status('One group supports up to 32 meshes.',true);return;}
 if(atelierGroups().length>=atelierGroupLimit){status('Maximum mesh group count reached.',true);return;}
 if(ids.some(id=>atelierGroupOf(id))){
  status('Some meshes already belong to a group. Ungroup them before regrouping.',true);return;
 }
 const id='atelier-group-'+Date.now().toString(36)+'-'+Math.random().toString(36).slice(2,7);
 const name='Assembly '+(atelierGroups().length+1);
 checkpoint();
 model().meshGroups=[...atelierGroups(),{id,name,members:ids}];
 atelierGroupCurrent=id;atelierGroupScope='group';atelierMeshAdding=false;
 selection=ids.at(-1);
 signalEdited();
 atelierGroupsSelect(selection);
 status('Grouped '+ids.length+' meshes non-destructively. Each part and material is still editable.');
}
function atelierGroupUngroup(){
 const g=atelierGroupById(atelierGroupCurrent)||atelierGroupOf(selection);
 if(!g){status('Select a mesh assembly to ungroup.',true);return;}
 checkpoint();
 model().meshGroups=atelierGroups().filter(other=>other.id!==g.id);
 atelierGroupCurrent=null;atelierGroupScope='child';atelierMeshAdding=false;
 const id=selection;
 signalEdited();atelierGroupsSelect(id);
 status('Ungrouped '+g.name+'. Original meshes and transforms preserved.');
}
function atelierGroupRemoveChild(){
 const group=atelierGroupOf(selection);
 if(!group||atelierGroupScope!=='child'){status('Choose Edit Child and select a grouped mesh first.',true);return;}
 checkpoint();
 group.members=group.members.filter(id=>id!==selection);
 atelierGroupsPrune();
 const id=selection;
 signalEdited();atelierGroupsSelect(id);
 status('Child removed from assembly without changing its geometry or transform.');
}
function atelierGroupUpdateMembers(){
 const g=atelierGroupById(atelierGroupCurrent);
 if(!g){status('Choose an existing assembly before updating members.',true);return;}
 const members=[...new Set(atelierMeshActiveIds())];
 if(members.length<2||members.length>32){status('Groups require 2–32 selected meshes.',true);return;}
 if(members.some(id=>atelierGroupOf(id)&&atelierGroupOf(id).id!==g.id)){
  status('A mesh already belongs to another assembly. Remove it there first.',true);return;
 }
 checkpoint();
 g.members=members;atelierMeshAdding=false;atelierGroupScope='group';
 signalEdited();atelierGroupsSelect(members.at(-1));
 status('Assembly membership updated; child materials and transforms preserved.');
}
function atelierGroupsSetScope(scope){
 if(!['group','child'].includes(scope))return;
 atelierGroupScope=scope;atelierMeshAdding=false;
 if(selection)atelierGroupsSelect(selection);
 else atelierGroupsUIRefresh();
}
function atelierGroupsPick(id){
 const g=atelierGroupById(id);
 if(!g)return;
 atelierGroupCurrent=g.id;atelierGroupScope='group';atelierMeshAdding=false;
 atelierGroupsSelect(g.members.at(-1));
}
function atelierGroupsToggleMulti(force){
 atelierMeshAdding=typeof force==='boolean'?force:!atelierMeshAdding;
 if(!atelierMeshAdding&&selection&&atelierGroupScope==='group'){
  const group=atelierGroupOf(selection);
  if(group){atelierMeshIds=atelierGroupMembers(group);atelierGroupCurrent=group.id;}
 }
 atelierGroupsUIRefresh();atelierMeshToolbarRefresh();
 status(atelierMeshAdding?'Multi-select ON: tap meshes to add/remove; empty space keeps selection.':
  'Multi-select OFF: tap an assembly to edit its linked meshes.');
}
function atelierGroupsSelectAll(){
 const all=model()?.parts.map(p=>p.id)||[];
 atelierMeshIds=all.slice(0,32);selection=atelierMeshIds.at(-1)||null;
 atelierMeshAdding=true;atelierGroupCurrent=null;
 atelierGroupsOutline();refreshList();refreshInspector();atelierMeshToolbarRefresh();
 atelierGroupsUIRefresh();atelierMeshPaintModeImmediately();
 status('Selected '+atelierMeshIds.length+' meshes'+(all.length>32?' (32-mesh selection limit).':'.'));
}
function atelierGroupsClear(){
 atelierMeshIds=[];selection=null;atelierGroupCurrent=null;
 atelierGroupsOutline();refreshList();refreshInspector();atelierMeshToolbarRefresh();
 atelierGroupsUIRefresh();atelierMeshPaintModeImmediately();
}
function atelierGroupsUIRefresh(){
 const root=panel?.querySelector('[data-atelier-groups]');
 if(!root)return;
 const count=atelierMeshIds.filter(id=>!!partById(id)).length;
 const toggle=root.querySelector('[data-group-multi]');
 if(toggle){
  toggle.setAttribute('aria-pressed',String(atelierMeshAdding));
  toggle.textContent=(atelierMeshAdding?'✓ Multi ON':'＋ Multi-select');
 }
 const counter=root.querySelector('[data-group-counter]');
 if(counter)counter.textContent=count+' selected';
 const scope=root.querySelector('[data-group-scope]');
 if(scope){scope.value=atelierGroupScope;scope.disabled=atelierMeshAdding;}
 const list=root.querySelector('[data-group-picker]');
 if(list){
  const current=atelierGroupCurrent||atelierGroupOf(selection)?.id||'';
  const fingerprint=atelierGroups().map(g=>g.id+'|'+g.name+'|'+g.members.length).join(';');
  if(list.dataset.fingerprint!==fingerprint){
   list.replaceChildren(new Option('Select assembly…',''),
    ...atelierGroups().map(g=>new Option(g.name+' · '+g.members.length+' meshes',g.id)));
   list.dataset.fingerprint=fingerprint;
  }
  list.value=atelierGroupById(current)?current:'';
 }
 const group=atelierGroupById(atelierGroupCurrent)||atelierGroupOf(selection);
 const buttons={
  '[data-group-create]':count>=2&&!atelierGroupById(atelierGroupCurrent),
  '[data-group-ungroup]':!!group,
  '[data-group-remove]':!!atelierGroupOf(selection)&&atelierGroupScope==='child'&&!atelierMeshAdding,
  '[data-group-update]':!!atelierGroupById(atelierGroupCurrent)&&atelierMeshAdding&&count>=2
 };
 for(const [selector,enabled] of Object.entries(buttons)){
  const btn=root.querySelector(selector);if(btn)btn.disabled=!enabled;
 }
 const stripName=atelierMeshStrip?.querySelector('[data-mesh-name]');
 if(stripName&&group&&!atelierMeshAdding&&atelierGroupScope==='group')
  stripName.textContent=group.name+' · '+group.members.length+' linked meshes';
}
function atelierGroupsInstall(panel){
 if(panel.querySelector('[data-atelier-groups]'))return;
 const viewportControls=panel.querySelector('.atelier-viewport-controls');
 if(!viewportControls)return;
 const dock=document.createElement('div');
 dock.className='atelier-group-mobile';dock.dataset.atelierGroups='1';
 dock.setAttribute('aria-label','Mesh multi-selection and editable assemblies');
 dock.innerHTML='<div class="atelier-group-quick">'+
  '<button type="button" data-group-multi aria-pressed="false">＋ Multi-select</button>'+
  '<span data-group-counter aria-live="polite">0 selected</span>'+
  '<button type="button" data-group-all>Select 32</button>'+
  '<button type="button" data-group-clear>Clear</button>'+
  '<button type="button" data-group-done>Done</button></div>'+
  '<details class="atelier-group-details"><summary>▣ Assemblies · Group / Child</summary>'+
  '<div class="atelier-group-actions">'+
  '<label>Selection <select data-group-scope aria-label="Edit group or individual child">'+
  '<option value="group">Edit group</option><option value="child">Edit child</option></select></label>'+
  '<label>Assembly <select data-group-picker aria-label="Choose a mesh assembly"></select></label></div>'+
  '<div class="atelier-group-actions">'+
  '<button type="button" data-group-create>Group selected</button>'+
  '<button type="button" data-group-ungroup>Ungroup</button>'+
  '<button type="button" data-group-update>Update members</button>'+
  '<button type="button" data-group-remove>Remove child</button></div>'+
  '<small>Groups are non-destructive. Join selected permanently combines topology.</small></details>';
 viewportControls.append(dock);
 dock.addEventListener('pointerdown',event=>event.stopPropagation());
 dock.addEventListener('click',e=>{
  const btn=e.target.closest('button');if(!btn)return;
  if(btn.hasAttribute('data-group-multi'))atelierGroupsToggleMulti();
  else if(btn.hasAttribute('data-group-all'))atelierGroupsSelectAll();
  else if(btn.hasAttribute('data-group-clear'))atelierGroupsClear();
  else if(btn.hasAttribute('data-group-done'))atelierGroupsToggleMulti(false);
  else if(btn.hasAttribute('data-group-create'))atelierGroupCreate();
  else if(btn.hasAttribute('data-group-ungroup'))atelierGroupUngroup();
  else if(btn.hasAttribute('data-group-update'))atelierGroupUpdateMembers();
  else if(btn.hasAttribute('data-group-remove'))atelierGroupRemoveChild();
 });
 dock.querySelector('[data-group-scope]').addEventListener('change',e=>atelierGroupsSetScope(e.target.value));
 dock.querySelector('[data-group-picker]').addEventListener('change',e=>atelierGroupsPick(e.target.value));
 atelierGroupsUIRefresh();
}
