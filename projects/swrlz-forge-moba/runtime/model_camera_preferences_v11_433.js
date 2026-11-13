/* SE433_CAMERA_PREFS_START */
// Non-destructive, device-local modeling navigation preference. Native mesh
// state, history, camera presets, pinch/pan, desktop mouse and Quest stay owned
// by their existing modules.
const se433CameraPrefs=(()=>{
 const key='swrlz:e:modelStudio:invertTouchOrbit:v1';
 let inverted=false,checkbox=null;
 try{inverted=localStorage.getItem(key)==='1';}catch(_){}
 function setInverted(value){
  inverted=!!value;
  try{localStorage.setItem(key,inverted?'1':'0');}catch(_){}
  if(checkbox)checkbox.checked=inverted;
  return inverted;
 }
 function install(hostPanel){
  const bar=hostPanel?.querySelector('#modelAtelierViewportModes');
  if(!bar)return false;
  let settings=bar.querySelector('#se433CameraSettings');
  if(!settings){
   settings=document.createElement('details');
   settings.id='se433CameraSettings';settings.className='se433-camera-settings';
   settings.setAttribute('aria-label','Model Studio camera settings');
   settings.innerHTML='<summary>Camera settings ▾</summary>'+
    '<div class="se433-camera-settings-body">'+
    '<label class="se433-camera-invert"><input type="checkbox" id="modelAtelierInvertTouchOrbit" aria-label="Invert touch camera orbit"> Invert touch orbit</label>'+
    '<small>Off: camera follows your finger. On: original reversed drag. Affects one-finger mobile orbit only.</small>'+
    '</div>';
   const views=bar.querySelector('#seAtelierViewMenu');
   if(views)views.after(settings);else bar.append(settings);
   settings.addEventListener('pointerdown',event=>event.stopPropagation());
   const input=settings.querySelector('#modelAtelierInvertTouchOrbit');
   input.addEventListener('change',()=>{setInverted(input.checked);status('Touch orbit: '+(inverted?'inverted (original)':'follows finger')+'. Saved on this device.');});
  }
  checkbox=settings.querySelector('#modelAtelierInvertTouchOrbit');
  if(checkbox)checkbox.checked=inverted;
  return true;
 }
 return Object.freeze({get inverted(){return inverted;},setInverted,install});
})();
/* SE433_CAMERA_PREFS_END */
