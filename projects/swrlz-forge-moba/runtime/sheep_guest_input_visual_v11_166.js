// §E v11.166 — reduce input-to-motion delay for the guest's OWN sheep.
// Visual only: host still owns collisions, placement, capture and position.
// No new game loop, packets, or scene objects. Works with v11.165 frame batch.
const se166={
 frames:0,assisted:0,blocked:0,maxVisualLead:0,
 lastLead:0,active:false,corrections:0
};
const se166FrameBefore=se152GuestFrame;
se152GuestFrame=function(...args){
 let modified=null,originalX=0,originalZ=0;
 se166.active=false;
 // Do not send a movement command here. Only bias the existing v11.161
 // presentation target towards the player's currently held joystick.
 if(se150Match.active&&se150Match.role==='guest'&&se152Guest()&&
    stSession&&!paused&&!stSession.winner&&se152.assigned){
  const m=stMobile,u=stSession.units.find(unit=>unit.id===se152.assigned);
  const track=u&&se161.tracks.get(u.id);
  const active=!!u&&!u.captured&&!u.isIllusion&&track&&
   m?.enabled&&m.pointer!==null&&m.session===stSession&&
   Number(m.strength)>.13&&
   (u.kind!=='wolf'||stSession.elapsed>=stSession.rules.headstart);
  if(active){
   const mx=Number(m.x),mz=Number(m.y),strength=Number(m.strength);
   const length=Math.hypot(mx,mz),speed=Number(u.speed);
   if([mx,mz,strength,speed].every(Number.isFinite)&&
      length>.1&&speed>0&&strength<=1.001){
    const now=performance.now();
    const age=Math.max(0,Math.min(1,(now-track.at)/1000));
    const lead=Math.min(.24,age); // v11.161 current host-velocity lead
    const baselineX=track.x+track.vx*lead;
    const baselineZ=track.z+track.vz*lead;
    // Local prediction is capped at ~0.8 terrain units, short of a sheep's
    // footprint. It only applies if it actually advances beyond the existing
    // host-derived target in the intended stick direction.
    const distance=Math.min(.8,speed*Math.min(age,.26)*Math.min(1,strength));
    const dx=mx/length,dz=mz/length;
    const wantedX=track.x+dx*distance,wantedZ=track.z+dz*distance;
    const bonus=(wantedX-baselineX)*dx+(wantedZ-baselineZ)*dz;
    const excess=Math.hypot(wantedX-track.x,wantedZ-track.z);
    if(bonus>.005&&excess<=.801){
     // The client cannot know the host's future path; suppress the visual
     // prediction when native collision geometry already blocks this point.
     let blocked=false;
     try{
      const radius=u.kind==='wolf'?ST_WOLF_RADIUS:ST_SHEEP_RADIUS;
      blocked=stBlocked(wantedX,wantedZ,radius);
     }catch{blocked=true;}
     if(!blocked){
      modified=track;originalX=track.x;originalZ=track.z;
      track.x+=wantedX-baselineX;
      track.z+=wantedZ-baselineZ;
      se166.assisted++;se166.active=true;
      se166.lastLead=distance;
      se166.maxVisualLead=Math.max(se166.maxVisualLead,distance);
     }else se166.blocked++;
    }
   }
  }
 }
 try{
  // All existing v11.161 character interpolation, v11.163 host house growth,
  // and v11.165 coalesced fog painting run exactly once, unchanged.
  return se166FrameBefore(...args);
 }finally{
  if(modified){
   // Restore the authoritative host snapshot anchor immediately. Biasing
   // its presentation target must NOT accumulate into replicated game state.
   modified.x=originalX;modified.z=originalZ;
  }
  se166.frames++;
 }
};
const se166PreviousStop=se152StopWorld;
se152StopWorld=function(...args){
 se166.frames=0;se166.assisted=0;se166.blocked=0;
 se166.maxVisualLead=0;se166.lastLead=0;se166.active=false;
 se166.corrections=0;
 return se166PreviousStop(...args);
};
window.SWYRL_ENGINE_LAN.inputResponse=()=>({
 active:se150Match.active,role:se150Match.role,
 localSmoothingActive:se166.active,
 renderedFrames:se166.frames,assistedFrames:se166.assisted,
 collisionSuppressed:se166.blocked,
 lastVisualLeadUnits:Number(se166.lastLead.toFixed(3)),
 maximumLeadUnits:Number(se166.maxVisualLead.toFixed(3)),
 hostAuthoritative:true,
 guestPacketAgeMs:se161.lastAge*1000
});
