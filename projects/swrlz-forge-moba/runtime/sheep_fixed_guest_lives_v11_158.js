// §E v11.158 — one guest, one assigned animal for the whole match.
// Captured sheep remain that player's wisp and regain the SAME sheep on rescue.
const se158={initialAssignments:0,captures:0,rescues:0};
const se158OriginalRoster=se152Roster;
se152Roster=function(){
 const s=stSession;
 if(!s||!se150Match.active||se150Match.role!=='host')
  return se158OriginalRoster();
 const peers=se149Peer.links.filter(p=>p.cloud&&p.name&&p.channel?.readyState==='open');
 const reserved=new Set([s.controlledId].filter(Boolean));
 // Existing connected players retain their original animal even if captured.
 // Never select a different sheep/wolf because the original is a wisp.
 for(const peer of peers){
  const assigned=se152.seats.get(peer);
  if(assigned&&s.units.some(u=>u.id===assigned)&&!reserved.has(assigned))
   reserved.add(assigned);
  else se152.seats.delete(peer);
 }
 // Only unassigned (new) players receive an unowned living animal.
 for(const peer of peers){
  if(se152.seats.has(peer))continue;
  const choice=s.units.find(u=>u.kind==='sheep'&&!u.captured&&!reserved.has(u.id))||
    s.units.find(u=>!u.captured&&!reserved.has(u.id));
  if(!choice)continue;
  se152.seats.set(peer,choice.id);
  reserved.add(choice.id);
  se158.initialAssignments++;
 }
 for(const peer of [...se152.seats.keys()])
  if(!peers.includes(peer))se152.seats.delete(peer);
};
const se158PreviousApply=se152ClientApply;
se152ClientApply=function(packet){
 const s=stSession;
 const previousUnit=s?.units.find(u=>u.id===se152.assigned);
 const wasCaptured=!!previousUnit?.captured,assignedBefore=se152.assigned;
 const result=se158PreviousApply(packet);
 if(!s||!se150Match.active||se150Match.role!=='guest')return result;
 const mine=s.units.find(u=>u.id===se152.assigned);
 if(!mine||!se152.assigned)return result;
 // Capture and rescue are host-owned snapshot events; camera and player role
 // must never become those of another sheep/wolf as a result of capture.
 if(mine.captured&&!wasCaptured&&assignedBefore===se152.assigned){
  se158.captures++;
  stUi.build=null;stUiClearPreview();
  stUi.follow=true;
  stUiFeedback('Your sheep was tagged. You are a wisp until a teammate rescues you.');
 }else if(!mine.captured&&wasCaptured&&assignedBefore===se152.assigned){
  se158.rescues++;
  stUi.follow=true;
  stUiFeedback('Rescued! You control your original sheep again.');
 }
 return result;
};
const se158PriorMove=stMobileCanMove;
stMobileCanMove=function(...args){
 if(se150Match.active&&se150Match.role==='guest'){
  const mine=stSession?.units.find(u=>u.id===se152.assigned);
  if(mine?.captured)return false;
 }
 return se158PriorMove(...args);
};
// Native captured sheep cannot physically move. Don't transmit stale joystick
// intent while waiting as a wisp; keep the peer connection and world updates.
const se158PreviousGuestControls=se152GuestControls;
se152GuestControls=function(...args){
 if(se150Match.active&&se150Match.role==='guest'){
  const mine=stSession?.units.find(u=>u.id===se152.assigned);
  if(mine?.captured)return;
 }
 return se158PreviousGuestControls(...args);
};
const se158PriorGuestLabel=se154GuestLabel;
se154GuestLabel=function(...args){
 const result=se158PriorGuestLabel(...args);
 if(se150Match.active&&se150Match.role==='guest'&&se150Match.badge){
  const mine=stSession?.units.find(u=>u.id===se152.assigned);
  if(mine?.captured)se150Match.badge.textContent+=' · WISP / awaiting rescue';
 }
 return result;
};
const se158PreviousStop=se152StopWorld;
se152StopWorld=function(...args){
 se158.initialAssignments=0;se158.captures=0;se158.rescues=0;
 return se158PreviousStop(...args);
};
window.SWYRL_ENGINE_LAN.playerLife=()=>({
 role:se150Match.role,matchActive:se150Match.active,
 assignedCharacter:se150Match.role==='guest'?se152.assigned:null,
 captured:!!stSession?.units.find(u=>u.id===se152.assigned)?.captured,
 playerAssignments:se150Match.role==='host'?
  [...se152.seats.values()]:[],
 captureEvents:se158.captures,rescueEvents:se158.rescues
});
