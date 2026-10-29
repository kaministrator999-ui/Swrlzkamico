// §E v11.144 — cinematic menu camera visits individual authored sheep.
// Retire the duplicate level-strip launch button; the native editor Play
// stays available, while the real menu retains its single START GAME CTA.
se142EnsureGameEntry=function(){
 seLevels.bar?.querySelector('#se142PlayGame')?.remove();
};
se142EnsureGameEntry();
let se144Focus=null;
const se144OldMenuTick=seLevelsMenuTick;
function se144CameraDirector(dt){
 if(!seLevels.playingMenu||seLevelsCurrent()?.role!=='menu')return;
 const sheep=seLevelsMenuActors('st-sheep');
 if(!sheep.length)return;
 const t=seLevels.time;
 // Hold each sheep long enough to see its animation, then ease to the next.
 const duration=7,step=Math.floor(t/duration),phase=(t%duration)/duration;
 const a=sheep[step%sheep.length],candidate=sheep[(step+1)%sheep.length];
 const b=candidate.visible?candidate:a;
 const u=Math.max(0,Math.min(1,(phase-.74)/.26));
 const blend=u*u*(3-2*u);
 const targetX=a.position.x+(b.position.x-a.position.x)*blend;
 const targetY=a.position.y+(b.position.y-a.position.y)*blend;
 const targetZ=a.position.z+(b.position.z-a.position.z)*blend;
 if(!se144Focus)se144Focus={x:targetX,y:targetY,z:targetZ};
 else{
  const follow=1-Math.exp(-Math.max(0,Math.min(.05,Number(dt)||0))*3);
  se144Focus.x+=(targetX-se144Focus.x)*follow;
  se144Focus.y+=(targetY-se144Focus.y)*follow;
  se144Focus.z+=(targetZ-se144Focus.z)*follow;
 }
 const angle=t*Math.PI*2/seLevelsMenuText().orbitSeconds;
 const radius=11.5;
 perspectiveCamera.position.set(
  se144Focus.x+Math.cos(angle)*radius,
  se144Focus.y+6.5+Math.sin(t*.18)*.4,
  se144Focus.z+Math.sin(angle)*radius);
 perspectiveCamera.lookAt(se144Focus.x,se144Focus.y+1.1,se144Focus.z);
 perspectiveCamera.updateMatrixWorld();
}
seLevelsMenuTick=function(dt){
 se144OldMenuTick(dt); // original chase, house build, wolf and gait first
 se144CameraDirector(dt);
};
const se144OldPlayMenu=seLevelsPlayMenu;
seLevelsPlayMenu=function(...args){
 se144Focus=null;
 return se144OldPlayMenu(...args);
};
const se144OldStopMenu=seLevelsStopMenu;
seLevelsStopMenu=function(...args){
 const stopped=se144OldStopMenu(...args);
 if(stopped)se144Focus=null;
 return stopped;
};
const se144PriorStatus=window.SWYRL_ENGINE_LEVELS.status;
window.SWYRL_ENGINE_LEVELS.status=function(){
 return {...se144PriorStatus(),menuCameraDirector:'sheep-portraits-orbit',
  menuCameraFocus:se144Focus&&{...se144Focus},
  extraLevelPlayButton:!!seLevels.bar?.querySelector('#se142PlayGame')};
};
