// §E v11.272 — left Quest joystick press (L3) toggles the existing
// in-game Nerd Stats metrics panel. No new renderer, DOM overlay or VR loop.
// The analog left joystick remains dedicated to sheep movement.
const se272NerdStick={
  pressed:false,presses:0,opens:0,closes:0,ignored:0,
  lastAction:'',lastError:''
};
function se272LeftStickDown(record){
  // WebXR xr-standard: left thumbstick click is gamepad.buttons[3].
  // Never use the axes for the toggle; that would interrupt movement.
  if(!record||record.input?.handedness!=='left')return false;
  const gamepad=record.input.gamepad,btn=gamepad?.buttons?.[3];
  if(!btn)return false;
  return btn.pressed===true||Number(btn.value)>.7;
}
function se272NerdToggle(){
  if(!se210Active())return false;
  const existing=se210UI.panels.get('metrics');
  if(existing?.root?.visible){
    se210PanelClose('metrics');
    se272NerdStick.closes++;se272NerdStick.lastAction='Nerd Stats hidden';
    return true;
  }
  const opened=se210PanelCreate('metrics');
  if(opened?.root?.visible){
    se272NerdStick.opens++;se272NerdStick.lastAction='Nerd Stats shown';
    return true;
  }
  se272NerdStick.lastError='Unable to open existing VR metrics panel';
  return false;
}
function se272NerdInputFrame(){
  const left=se192InputRecord('left');
  const down=se272LeftStickDown(left);
  const eligible=!!left&&se210Active();
  if(!eligible){
    // Re-arm only after release, so a held stick while entering Gameplay
    // or returning from an OS overlay never unexpectedly opens a panel.
    se272NerdStick.pressed=down;
    return;
  }
  if(down&&!se272NerdStick.pressed){
    se272NerdStick.presses++;
    if(!se272NerdToggle())se272NerdStick.ignored++;
  }
  se272NerdStick.pressed=down;
}
const se272PriorXRFrame=se193XRFrame;
se193XRFrame=function(...args){
  const result=se272PriorXRFrame(...args);
  se272NerdInputFrame();
  return result;
};
const se272PriorXRCleanup=se193XRCleanup;
se193XRCleanup=function(...args){
  se272NerdStick.pressed=false;
  return se272PriorXRCleanup(...args);
};
window.SWYRL_ENGINE_SHEEP_NERD_L3_272=Object.freeze({
  toggle:se272NerdToggle,
  diagnose:()=>({
    active:se210Active(),
    leftStickClickHeld:se272NerdStick.pressed,
    metricsVisible:!!se210UI.panels.get('metrics')?.root?.visible,
    l3Presses:se272NerdStick.presses,
    opens:se272NerdStick.opens,closes:se272NerdStick.closes,
    ignored:se272NerdStick.ignored,
    leftJoystickMovementUnchanged:true,
    lastAction:se272NerdStick.lastAction,
    lastError:se272NerdStick.lastError
  })
});
