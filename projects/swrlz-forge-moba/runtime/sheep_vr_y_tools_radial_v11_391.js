// §E v11.391 — Quest Browser reserves the left Menu system button.
// Use the left Y face button for one-press access to the EXISTING Sheep Tag
// tools radial. The X skill wheel, A build wheel, L3 statistics and right B
// camera-free shortcut keep their established mappings. No new frame loop.
const se391Menu={opens:0,closes:0,ignored:0,lastAction:'',lastError:''};
const se391PriorButtonEdges=se193XRButtonEdges;
se193XRButtonEdges=function(...args){
  const left=se192InputRecord('left');
  if(!se195Active()||!se193XRGameActive()||!left||!Number.isInteger(left.index))
    return se391PriorButtonEdges(...args);
  // xr-standard buttons[5] is left Y (NOT the OS-reserved Menu button).
  const held=!!se192Pressed(left,5);
  const prior=!!se193.held.get(left.index);
  const available=se211Visibility()==='visible'&&
    !se205OverlayActive()&&!se195.photo;
  if(held&&!prior){
    if(available){
      // Do not activate building/skill commands behind the tools surface.
      if(se204.wheel)se204WheelHide();
      if(!se195.visible){
        se195.mode='game';
        se195.page='main'; // FOLLOW / FREE are immediately accessible.
        se195SetVisible(true);
        se391Menu.opens++;
        se391Menu.lastAction='Y opened Sheep Tag tools radial';
      }else{
        se195SetVisible(false);
        se391Menu.closes++;
        se391Menu.lastAction='Y closed Sheep Tag tools radial';
      }
    }else se391Menu.ignored++;
  }
  // The original v11.193 edge handler treats left Y as FOLLOW. Consume
  // only that old edge: its right-B FREE and other camera handling still run.
  se193.held.set(left.index,held);
  return se391PriorButtonEdges(...args);
};
window.SWYRL_ENGINE_SHEEP_VR_Y_MENU_391=Object.freeze({
  diagnose:()=>({
    active:se195Active()&&se193XRGameActive(),
    leftYAvailable:!!se192InputRecord('left')?.input?.gamepad?.buttons?.[5],
    radialVisible:!!se195.visible,radialPage:se195.page,
    opens:se391Menu.opens,closes:se391Menu.closes,
    ignored:se391Menu.ignored,lastAction:se391Menu.lastAction,
    lastError:se391Menu.lastError,
    questSystemMenuButtonReserved:true,
    rightBFreeCameraPreserved:true,xSkillAndABuildPreserved:true,
    leftStickStatsPreserved:true
  })
});