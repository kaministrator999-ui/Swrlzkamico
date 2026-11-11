// §E v11.416 — Sheep Tag solo AI teammate choice before native match start.
// Uses existing authored sheep spawns; never creates actors, a second session,
// a renderer, network clients, or saved map mutations.
const se416Setup={count:null,pending:null,allow:false,dialog:null,returnFocus:null,lastApplied:null};
function se416Max(){
 const target=[...seLevels.records.values()].find(r=>r.role==='game'&&r.data?.project?.kind==='sheep-tag');
 const sheep=(target?.data?.scene?.actors||[]).filter(a=>
   a.type==='st-sheep'&&a.baked!==false&&a.visible!==false).length;
 return Math.min(8,Math.max(0,sheep-1)); // Quest-friendly and never beyond available spawns
}
function se416Count(){
 const max=se416Max();
 if(se416Setup.count===null)se416Setup.count=max; // preserve prior 5-bot default
 se416Setup.count=Math.max(0,Math.min(max,Math.round(Number(se416Setup.count)||0)));
 return se416Setup.count;
}
function se416SetCount(value){
 se416Setup.count=Math.max(0,Math.min(se416Max(),Math.round(Number(value)||0)));
 se416PaintDialog();
 return se416Setup.count;
}
function se416CloseDialog(){
 const prior=se416Setup.dialog;
 se416Setup.dialog=null;
 prior?.remove();
 if(se416Setup.returnFocus?.isConnected)se416Setup.returnFocus.focus();
 se416Setup.returnFocus=null;
}
function se416PaintDialog(){
 const d=se416Setup.dialog;if(!d)return;
 const count=se416Count(),max=se416Max();
 const output=d.querySelector('#se416Value'),range=d.querySelector('#se416Range');
 if(output)output.textContent=String(count);
 if(range){range.max=String(max);range.value=String(count);}
 const note=d.querySelector('#se416Limit');
 if(note)note.textContent='You + '+count+' AI sheep · '+max+' available teammates';
 const minus=d.querySelector('#se416Minus'),plus=d.querySelector('#se416Plus');
 if(minus)minus.disabled=count===0;
 if(plus)plus.disabled=count>=max;
}
function se416ShowBrowser(){
 if(!seLevels.playingMenu||!seLevels.overlay)return false;
 if(se416Setup.dialog){se416PaintDialog();return true;}
 const dialog=document.createElement('section');
 dialog.id='se416FlockSetup';
 dialog.className='se416-backdrop';
 dialog.setAttribute('role','dialog');
 dialog.setAttribute('aria-modal','true');
 dialog.setAttribute('aria-labelledby','se416Heading');
 dialog.innerHTML='<div class="se416-card">'+
  '<small>SHEEP TAG · MATCH SETUP</small>'+
  '<h2 id="se416Heading">Choose your flock</h2>'+
  '<p>How many AI sheep teammates do you want?</p>'+
  '<div class="se416-counter"><button type="button" id="se416Minus" aria-label="Remove one AI sheep">−</button>'+
  '<output id="se416Value" aria-live="polite"></output>'+
  '<button type="button" id="se416Plus" aria-label="Add one AI sheep">+</button></div>'+
  '<input id="se416Range" type="range" min="0" step="1" aria-label="AI sheep teammates">'+
  '<p id="se416Limit" class="se416-note"></p>'+
  '<div class="se416-actions"><button type="button" id="se416Cancel">BACK</button>'+
  '<button type="button" id="se416Launch">START MATCH</button></div></div>';
 dialog.querySelector('#se416Minus').onclick=()=>se416SetCount(se416Count()-1);
 dialog.querySelector('#se416Plus').onclick=()=>se416SetCount(se416Count()+1);
 dialog.querySelector('#se416Range').oninput=e=>se416SetCount(e.target.value);
 dialog.querySelector('#se416Cancel').onclick=se416CloseDialog;
 dialog.querySelector('#se416Launch').onclick=se416Confirm;
 dialog.onkeydown=e=>{
  if(e.key==='Escape'){e.preventDefault();se416CloseDialog();}
  if(e.key==='Tab'){
   const buttons=[...dialog.querySelectorAll('button:not(:disabled),input')];
   const first=buttons[0],last=buttons[buttons.length-1];
   if(e.shiftKey&&document.activeElement===first){e.preventDefault();last.focus();}
   else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first.focus();}
  }
 };
 for(const kind of ['pointerdown','pointerup','click'])dialog.addEventListener(kind,e=>e.stopPropagation());
 se416Setup.returnFocus=document.activeElement;
 seLevels.overlay.appendChild(dialog);
 se416Setup.dialog=dialog;
 se416PaintDialog();
 dialog.querySelector('#se416Launch').focus();
 return true;
}
function se416Show(){
 if(!seLevels.playingMenu||seLevelsCurrent()?.role!=='menu')return false;
 se416Count();
 if(renderer.xr?.isPresenting){
  se195Page('aiSetup');
  se195.lastAction='Choose your AI sheep teammates before starting';
  return true;
 }
 return se416ShowBrowser();
}
function se416Confirm(){
 if(!seLevels.playingMenu)return false;
 se416Setup.pending=se416Count();
 se416Setup.allow=true;
 // The original level transition owns Play, loading, camera, HUD and rules.
 const started=seLevelsTransition('',true);
 if(!started)se416Setup.pending=null;
 return !!started;
}
// One entry point covers desktop title button and Quest Start actions;
// multiplayer's host-authorized match start is intentionally unaffected.
const se416PriorTransition=seLevelsTransition;
seLevelsTransition=function(to,autoPlay=true){
 const current=seLevelsCurrent(),next=seLevels.records.get(to||current?.next);
 const lan=typeof se150Match!=='undefined'&&se150Match.active;
 if(!se416Setup.allow&&autoPlay&&seLevels.playingMenu&&
    current?.role==='menu'&&next?.role==='game'&&!lan)return se416Show();
 se416Setup.allow=false;
 return se416PriorTransition(to,autoPlay);
};
const se416PriorMenuStop=seLevelsStopMenu;
seLevelsStopMenu=function(...args){
 se416CloseDialog();
 return se416PriorMenuStop(...args);
};
// Keep rendering and input entirely inside the existing Quest radial UI.
const se416PriorVROptions=se195Options;
se195Options=function(mode=se195.mode,page=se195.page){
 if(mode==='menu'&&page==='aiSetup')return [
  ['se416Minus','- 1 SHEEP'],['se416Count','AI SHEEP '+se416Count()+'/'+se416Max()],
  ['se416Plus','+ 1 SHEEP'],['se416Launch','START MATCH'],['back','CANCEL']
 ];
 return se416PriorVROptions(mode,page);
};
const se416PriorVRAction=se195HandleAction;
se195HandleAction=function(action,record){
 // The older PLAY handler hides the radial after dispatch. Intercept it so
 // Quest users can actually see and operate the new setup page.
 if(se195.mode==='menu'&&action==='start'&&se195.page==='main')return se416Show();
 if(se195.mode==='menu'&&se195.page==='aiSetup'){
  if(action==='se416Minus'||action==='se416Plus'){
   se416SetCount(se416Count()+(action==='se416Plus'?1:-1));
   se195MakeRadial(false);
   return true;
  }
  if(action==='se416Count')return true;
  if(action==='se416Launch'){
   const started=se416Confirm();
   if(started)se195SetVisible(false);
   return true;
  }
  if(action==='back'){se195Page('main');return true;}
 }
 return se416PriorVRAction(action,record);
};
// A match chooses a subset of the authored starting flock. The invisible,
// inactive actors and their authored transforms are restored by native stStop.
const se416PriorStart=stStart;
stStart=function(simulate=false){
 const result=se416PriorStart(simulate);
 const s=stSession,lan=typeof se150Match!=='undefined'&&se150Match.active;
 if(!result?.ok||!s||simulate||lan||se416Setup.pending===null)return result;
 const controlled=s.units.find(u=>u.id===s.controlledId&&u.kind==='sheep');
 if(!controlled)return result; // the wolf role is not a sheep team setup
 const candidates=s.units.filter(u=>u.kind==='sheep'&&u!==controlled);
 const requested=Math.max(0,Math.min(candidates.length,se416Setup.pending));
 const removed=new Set(candidates.slice(requested).map(u=>u.id));
 for(const unit of candidates.slice(requested)){
  unit.actor.visible=false;
  delete s.resources[unit.id];
 }
 s.units=s.units.filter(u=>!removed.has(u.id));
 for(const b of s.buildings)if(removed.has(b.owner))b.owner=controlled.id;
 s.aiTeammates=requested;
 se416Setup.lastApplied=requested;
 return {...result,...stStatus()};
};
const se416PriorStop=stopSession;
stopSession=function(...args){
 const result=se416PriorStop(...args);
 if(!stSession)se416Setup.pending=null;
 return result;
};
window.SWYRL_ENGINE_SHEEP_TEAM_SETUP_416=Object.freeze({
 max:()=>se416Max(),count:()=>se416Count(),setCount:n=>se416SetCount(n),
 diagnose:()=>({menu:!!seLevels.playingMenu,vr:!!renderer.xr?.isPresenting,
  pending:se416Setup.pending,selected:se416Count(),
  max:se416Max(),activeAI:stSession?.aiTeammates??null,
  sessionSheep:stSession?.units.filter(u=>u.kind==='sheep').length??null})
});
