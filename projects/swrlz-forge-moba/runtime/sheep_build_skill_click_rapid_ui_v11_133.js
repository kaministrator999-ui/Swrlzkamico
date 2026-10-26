// §E v11.133: two independent real-device fixes.
// 1) Native touch pointerup on a build skill selects the active tool, then
// Chrome synthesizes a CLICK which used to toggle the very same tool OFF.
// 2) Rapid button inherited pointer-events:none from the HUD and sat mid-map.
let st133HandledBuildClick=null;
function st133RememberBuildTouch(event,kind){
 if(!kind||(event.pointerType!=='touch'&&event.pointerType!=='pen'))return;
 st133HandledBuildClick={kind,at:performance.now()};
}
document.addEventListener('click',event=>{
 const button=event.target?.closest?.('button[data-st-skill]');
 if(!button||!st133HandledBuildClick)return;
 const recorded=st133HandledBuildClick;
 if(performance.now()-recorded.at>850){st133HandledBuildClick=null;return;}
 if(event.detail===0||button.dataset.stSkill!==recorded.kind)return;
 // Prevent the duplicate synthesized click from calling native onclick
 // stUiChooseBuild(kind), which toggles the just-selected tool back off.
 st133HandledBuildClick=null;event.preventDefault();event.stopImmediatePropagation();
},true);
function st133CanAimSkillAt(x,y){
 // Pointer capture keeps event.target on the skill icon while the finger
 // crosses into the meadow. Use real elementFromPoint, not captured target.
 return stTouchPlacementClearCanvas(x,y);
}
function st133SeedWhileSkillHeld(){
 const original=stTouchPlacement.gesture;
 // The v11.82 touch preview intentionally hides when a gesture is invalid;
 // this is a BUTTON press, not a world-placement gesture yet. Seed at sheep
 // without accidentally hiding it, but retain the tracked pointer for drag.
 stTouchPlacement.gesture=null;
 try{return st126SeedAtSheep();}
 finally{stTouchPlacement.gesture=original;}
}
const st133ClearCanvasBase=stTouchPlacementClearCanvas;
stTouchPlacementClearCanvas=function(x,y){
 if(st133ClearCanvasBase(x,y))return true;
 const view=$('viewport'),box=view?.getBoundingClientRect();
 const target=document.elementFromPoint(x,y);
 return !!view&&!!box&&x>=box.left&&x<box.right&&y>=box.top&&y<box.bottom&&
   !!target&&view.contains(target);
};
function st133MoveMobileBuildControls(){
 const hud=$('sheepTagHUD'),builds=hud?.querySelector('.st-builds');
 if(!builds)return;
 for(const name of ['st132RapidBuild','st132Rotate']){
  const control=$(name);
  if(control&&control.parentElement!==builds)builds.appendChild(control);
 }
}
const st133InstallBase=stInstallUI;
stInstallUI=function(...args){
 const result=st133InstallBase(...args);
 st133MoveMobileBuildControls();
 return result;
};
