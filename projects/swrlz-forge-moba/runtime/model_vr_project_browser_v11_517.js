/* SE517_XR_PROJECT_BROWSER_START
   #5 object rotation ≠ HMD orbit, #7 project browsing/switching from
   existing three-column immersive menu. No DOM overlays or second XR loop. */
const se517XRProjects=(()=>{
 'use strict';
 const sourceNames={local:'Device',cloud:'Account',starter:'Starters'};
 let source='local',catalog={local:[],cloud:[],starters:[]},page=0,selected=null;
 let pending='',loading=false,opening=false,revision=0,ticket=0;
 const service=()=>window.SWYRL_ENGINE_VR_PROJECT_LIBRARY_517;
 const rows=()=>catalog[source==='starter'?'starters':source]||[];
 const key=x=>x?.source+':'+x?.id;
 const chosen=()=>rows().find(x=>key(x)===selected)||null;
 const note=(s,bad=false)=>{se340Notice(s,bad);se340XR.stateKey='';se340SyncUI();se340Publish();};
 const changed=()=>{revision++;se340XR.stateKey='';if(se340XR.ui)se340SyncUI();};
 async function refresh(){
  if(loading||opening)return;
  const lib=service();if(!lib){note('Project service unavailable. Current project is safe.',true);return;}
  loading=true;const seq=++ticket;changed();
  try{
   const result=await lib.list();
   if(seq!==ticket)return;
   catalog={local:result.local||[],cloud:result.cloud||[],starters:result.starters||[]};
   page=0;selected=null;pending='';
   note('VR projects · '+rows().length+' '+sourceNames[source].toLowerCase()+' choices · select a name, then Open.');
  }catch(error){note('Project list unavailable: '+String(error?.message||error).slice(0,75),true);}
  finally{if(seq===ticket){loading=false;changed();}}
 }
 function start(){
  if(!catalog.local.length&&!catalog.cloud.length&&!catalog.starters.length&&!loading)void refresh();
 }
 function entries(){return rows().slice(page*4,page*4+4);}
 function operations(){
  const choices=entries();
  return [
   ['project-source-local',(source==='local'?'● ':'')+'On device'],
   ['project-source-cloud',(source==='cloud'?'● ':'')+'Google account'],
   ['project-source-starter',(source==='starter'?'● ':'')+'Starters'],
   ['project-page-prev','Previous page'],
   ['project-page-next','Next page'],
   ...Array.from({length:4},(_,i)=>choices[i]?
    ['project-pick-'+i,(selected===key(choices[i])?'● ':'')+choices[i].name.slice(0,27)]:null),
   ['project-open',opening?'Opening…':pending?'CONFIRM switch':chosen()?'Open: '+chosen().name.slice(0,22):'Choose a project'],
   ['project-cancel','Cancel selection']
  ];
 }
 function action(command){
  if(!command.startsWith('project-'))return false;
  if(opening){note('Project loading is in progress.');return true;}
  if(command.startsWith('project-source-')){
   const next=command.slice('project-source-'.length);
   if(!Object.hasOwn(sourceNames,next))return false;
   source=next;page=0;selected=null;pending='';changed();void refresh();return true;
  }
  if(command==='project-page-prev'||command==='project-page-next'){
   const next=page+(command.endsWith('next')?1:-1);
   if(next>=0&&next<Math.ceil(rows().length/4)){page=next;selected=null;pending='';changed();}
   else note('No more projects on this side of the list.');
   return true;
  }
  if(/^project-pick-[0-3]$/.test(command)){
   const which=Number(command.at(-1)),item=entries()[which];
   if(!item){note('No project in that slot.');return true;}
   selected=key(item);pending='';changed();note('Selected '+item.name+' · choose Open to load in this VR session.');return true;
  }
  if(command==='project-cancel'){
   selected=null;pending='';changed();note('Project selection canceled · current model unchanged.');return true;
  }
  if(command==='project-open'){void open();return true;}
  return false;
 }
 async function open(){
  if(opening)return;
  const item=chosen();
  if(!item){note('Choose an available project row first.',true);return;}
  const lib=service(),state=lib?.status?.();
  if(!state||state.busy){note('Finish the current project operation before switching.',true);return;}
  const itemKey=key(item);
  if(state.dirty&&pending!==itemKey){
   pending=itemKey;changed();
   note('Unsaved edits: use Save first, or press CONFIRM switch. A local recovery copy will be saved.',true);
   return;
  }
  if(!se340XR.session||!se340VisibleSession()||!se340XR.scene||se340XR.ending){
   note('Immersive VR session is unavailable. Current project remains open.',true);return;
  }
  if(se340XR.gesture){note('Release the active controller edit before changing projects.',true);return;}
  opening=true;se340XR.se517ProjectBusy=true;changed();
  let released=false,loaded=false;
  try{
   se345RestoreDisplay();
   const returned=se340Bridge().releaseRoot();
   if(returned?.ok===false)throw Error('Current model root is still owned by the VR editor');
   released=true;
   const result=await lib.open(item.source,item.id);
   if(result?.ok!==true)throw Error('Project load was not confirmed');
   loaded=true;
   if(!se340XR.session||!se340XR.scene||se340XR.ending)return;
   const bridge=se340Bridge();
   const borrowed=bridge.borrowRoot(se340XR.pivot);
   if(borrowed?.ok!==true)throw Error('New model could not be attached to the XR workspace');
   se340XR.documentToken=bridge.inspect().documentToken;
   se340XR.cachedEntries=null;se340XR.frameEntries=null;se340XR.projectionRevision=-1;
   se340XR.pickMatrixFrame=-1;se340XR.boxCache=new WeakMap();se343DropHoverSurfaces();
   se340XR.displayOriginals=new Map();se340XR.displayMode='textured';
   se340XR.mode='inspect';se340XR.page='projects';
   se340XR.anchored=false;se340XR.orbitRefState=null;se340XR.hoverId=null;
   selected=null;pending='';page=0;
   note('Opened '+result.name+' in immersive VR · current session preserved.');
  }catch(error){
   // The native service restores the previous document on loader failure.
   // Reborrow its live model before allowing the normal XR frame to run.
   if(released&&se340XR.scene&&se340XR.session&&!se340XR.ending){
    try{
     const borrow=se340Bridge().borrowRoot(se340XR.pivot);
     if(borrow?.ok!==true)throw Error('No model to restore');
     se340XR.documentToken=se340Bridge().inspect().documentToken;
     se340XR.cachedEntries=null;se340XR.frameEntries=null;se340XR.projectionRevision=-1;
     se340XR.anchored=false;
    }catch(_){void se340ModelXRExit();}
   }
   note((loaded?'XR display swap':'Project load')+' failed: '+
    String(error?.message||error).slice(0,85)+'. Recovery copy saved.',true);
  }finally{
   opening=false;se340XR.se517ProjectBusy=false;pending='';changed();
  }
 }
 function reset(){ticket++;opening=false;loading=false;pending='';selected=null;page=0;catalog={local:[],cloud:[],starters:[]};revision++;}
 return Object.freeze({start,refresh,operations,action,reset,
  inspect:()=>({source,page,selected,loading,opening,pending:!!pending,revision,
   count:rows().length,current:chosen()?.name||''})});
})();
const se517PriorXRAction=se340ModelXRAction;
se340ModelXRAction=function(action,record){
 if(action?.startsWith?.('project-'))return se517XRProjects.action(action);
 if(action==='rotate'&&!se350Tools()?.selection?.()?.ids?.length){
  se340Notice('Select the model first. Rotate edits its geometry, not your camera.',true);
  return true;
 }
 return se517PriorXRAction.apply(this,arguments);
};
const se517PriorGesture=se340UpdateGesture;
se340UpdateGesture=function(...args){
 const s=se340XR,g=s.gesture;
 if(g?.kind==='group'&&g.mode==='rotate'){
  if(!g.se517CameraBasis)g.se517CameraBasis={yaw:s.yaw,pitch:s.pitch};
  // A controller transform must NEVER update the headset orbit angles.
  // Right-stick orbit still works normally when no model transform is active.
  else if(Math.abs(s.yaw-g.se517CameraBasis.yaw)>1e-7||
     Math.abs(s.pitch-g.se517CameraBasis.pitch)>1e-7){
   s.yaw=g.se517CameraBasis.yaw;s.pitch=g.se517CameraBasis.pitch;
   se340CancelGesture('Rotation canceled: camera orbit changed during a model edit.');
   return;
  }
 }
 return se517PriorGesture.apply(this,args);
};
const se517PriorCleanup=se340Cleanup;
se340Cleanup=function(...args){se517XRProjects.reset();return se517PriorCleanup.apply(this,args);};
window.SWYRL_ENGINE_VR_PROJECT_BROWSER_517=se517XRProjects;
/* SE517_XR_PROJECT_BROWSER_END */
