// §E v11.221 · Gesture library and independent opposition / thumb flex.
// Installed inside existing native ModelAtelier closure; no new renderer.
function se221StudioInstall(){
 const studio=se220R('Studio'),body=studio?.querySelector('.atelier-rig-body');
 if(!body||se220R('Gesture'))return;
 const controls=document.createElement('div');
 controls.className='atelier-gesture-library';
 controls.innerHTML=
  '<label>Hand gesture<select id="modelAtelierRigGesture" aria-label="Choose hand gesture">'+
  '<option value="custom">Custom pose</option></select></label>'+
  '<button type="button" id="modelAtelierRigAnimateGesture">▶ Animate selected gesture</button>';
 body.insertBefore(controls,body.querySelector('.atelier-rig-actions'));
 const select=se220R('Gesture');
 for(const [key,label] of se221Gestures){
  const option=document.createElement('option');
  option.value=key;option.textContent=label;select.append(option);
 }
 select.value='fist';
 const thumb=document.createElement('div');thumb.className='atelier-thumb-kinematics';
 thumb.innerHTML=
  '<strong>Thumb articulation</strong>'+
  '<label>Opposition across palm <output id="modelAtelierRigOpposeValue">0%</output>'+
  '<input id="modelAtelierRigOppose" type="range" min="0" max="100" step="1" value="0"></label>'+
  '<label>Thumb flex / tip curl <output id="modelAtelierRigThumbCurlValue">0%</output>'+
  '<input id="modelAtelierRigThumbCurl" type="range" min="0" max="100" step="1" value="0"></label>'+
  '<small>CMC moves thumb across the palm. MCP and IP follow with separate bends.</small>';
 body.insertBefore(thumb,body.querySelector('.atelier-rig-timeline'));
 const applyGesture=kind=>{
  if(!se220RigAvailable())return;
  se220Playing=false;se220RigRemember();
  const rig=se220Rig();rig.pose=se221GesturePose(rig,kind);
  se220RigPose(rig.pose);se220RigJointUI();se221ThumbSync();
  se220RigTouched('Applied '+(se221Gestures.find(([k])=>k===kind)?.[1]||kind)+' · thumb and finger joints posed independently.');
 };
 select.addEventListener('change',e=>{
  if(e.target.value!=='custom')applyGesture(e.target.value);
 });
 for(const name of ['Open','Fist','Point','Pinch']){
  se220R(name)?.addEventListener('click',()=>{
   select.value=name.toLowerCase();se221ThumbSync();
  });
 }
 for(const id of ['X','Y','Z'])se220R(id)?.addEventListener('change',()=>{
  if(select)select.value='custom';se221ThumbSync();
 });
 let editing=false;
 const onThumbInput=()=>{
  if(!se220RigAvailable())return;
  if(!editing){se220RigRemember();editing=true;}
  se220Playing=false;
  const a=Number(se220R('Oppose').value)/100,b=Number(se220R('ThumbCurl').value)/100;
  const pose=se220Rig().pose;
  pose.thumb_cmc=[.33*a+.08*b,1.20*a,-.44*a];
  pose.thumb_mcp=[.09*a,.13*a,-.05*a+.40*b];
  pose.thumb_ip=[.06*a,-.04*a,-.07*a+.43*b];
  se220RigPose(pose);se220RigJointUI();
  se220R('OpposeValue').textContent=Math.round(a*100)+'%';
  se220R('ThumbCurlValue').textContent=Math.round(b*100)+'%';
  select.value='custom';
 };
 for(const id of ['Oppose','ThumbCurl']){
  const el=se220R(id);
  el.addEventListener('input',onThumbInput);
  el.addEventListener('change',()=>{
   editing=false;se220RigTouched('Thumb opposition and distal flex updated · save a key to animate.');
  });
 }
 se220R('AnimateGesture').addEventListener('click',()=>{
  if(!se220RigAvailable())return;
  const rig=se220Rig();se220Playing=false;se220RigRemember();
  const kind=select.value,gesture=kind==='custom'?structuredClone(rig.pose):se221GesturePose(rig,kind);
  const open=se221GesturePose(rig,'open');
  rig.duration=1.5;
  rig.timeline=[
   {time:0,pose:open},
   {time:.75,pose:structuredClone(gesture)},
   {time:1.5,pose:structuredClone(open)}
  ];
  rig.pose=structuredClone(gesture);
  se220Time=0;se220R('Time').max='1.5';se220R('Time').value='0';
  se220R('Length').value='1.5';
  se220PlayBegin=performance.now();se220Playing=true;
  se220RigPose(open);se220RigJointUI();se220RigTimeLabel();
  se220RigTouched('Playing open → '+(se221Gestures.find(([k])=>k===kind)?.[1]||'custom')+' → open. Edit or save these three keys.');
 });
 se221ThumbSync();
}
function se221ThumbSync(){
 const p=se220Rig()?.pose;
 if(!p||!se220R('Oppose'))return;
 const a=se220Clamp((p.thumb_cmc?.[1]||0)/1.20),b=se220Clamp(
  ((p.thumb_mcp?.[2]||0)+.05*a)/.40);
 se220R('Oppose').value=String(Math.round(a*100));
 se220R('ThumbCurl').value=String(Math.round(b*100));
 se220R('OpposeValue').textContent=Math.round(a*100)+'%';
 se220R('ThumbCurlValue').textContent=Math.round(b*100)+'%';
}
