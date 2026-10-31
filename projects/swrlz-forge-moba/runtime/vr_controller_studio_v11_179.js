// §E v11.179 — VR Controller Studio foundation, no pretend immersive editor.
// Configuration and test diagnostics only; native edits are never dispatched.
(()=>{
'use strict';
if(window.SWYRL_VR_CONTROLS)return;
const SCHEMA='swyrl-engine-vr-controls-v1',STORAGE='swyrl.vr.controls.v1.local',CONTEXTS=['global','game','model','sculpt','play'];
const LABEL={LS:'Left thumbstick',RS:'Right thumbstick',LT:'Left trigger',RT:'Right trigger',LG:'Left grip',RG:'Right grip',X:'X',Y:'Y',A:'A',B:'B'};
const ACTIONS=new Set(['open-settings','save-project','redo','toggle-snap','focus','select','multiselect','grab','pan','navigate','orbit','tool','cancel','palette','undo','duplicate','duplicate-place','delete','two-hand','precision','snap','zoom','wireframe','reset-camera','stroke','sample','radius','strength','mirror','temporary-smooth','preview','fine','move','camera','interact','secondary','menu','jump','back','pause','quick-action']);
const BASE={
global:[
['open-settings','hold:LS+RS','Controller settings'],['save-project','hold:Y+B','Save project'],['redo','chord:X+Y','Redo'],['toggle-snap','chord:LG+LS','Toggle snap'],['focus','tap:RS','Focus selection']],
game:[
['select','tap:RT','Select / confirm'],['multiselect','tap:LT','Multi-select'],['grab','hold:RG','Grab actor'],['pan','hold:LG','Pan workbench'],['navigate','axis:LS','Navigate'],['orbit','axis:RS','Orbit / turn'],['tool','tap:A','Transform tool'],['cancel','tap:B','Cancel'],['palette','tap:X','Prefab palette'],['undo','tap:Y','Undo'],['duplicate','chord:X+A','Duplicate actor'],['duplicate-place','chord:X+RT','Duplicate / place'],['delete','hold:X+B','Delete with confirmation'],['two-hand','hold:LG+RG','Two-hand transform'],['precision','hold:LT+RG','Precision transform'],['snap','tap:LS','Grid snap']],
model:[
['select','tap:RT','Select mesh / handle'],['multiselect','tap:LT','Multi-select'],['grab','hold:RG','Grab mesh'],['pan','hold:LG','Move workbench'],['orbit','axis:LS','Orbit'],['zoom','axis:RS','Zoom'],['tool','tap:A','Transform tool'],['cancel','tap:B','Cancel'],['palette','tap:X','Geometry tools'],['undo','tap:Y','Undo'],['duplicate','chord:X+A','Duplicate mesh'],['delete','hold:X+B','Delete with confirmation'],['two-hand','hold:LG+RG','Two-hand transform'],['precision','hold:LT+RG','Precision transform'],['wireframe','chord:X+RS','Wireframe'],['reset-camera','tap:LS','Reset camera']],
sculpt:[
['stroke','hold:RT','Sculpt stroke'],['sample','tap:LT','Surface sample'],['grab','hold:RG','Move mesh'],['pan','hold:LG','Move workbench'],['radius','axis:LS','Brush radius'],['strength','axis:RS','Brush strength'],['tool','tap:A','Brush operation'],['cancel','tap:B','Disarm brush'],['palette','tap:X','Brush palette'],['undo','tap:Y','Undo stroke'],['mirror','chord:X+A','Mirror symmetry'],['temporary-smooth','chord:X+RT','Temporary smooth'],['preview','chord:X+B','Footprint preview'],['two-hand','hold:LG+RG','Reorient view'],['fine','hold:LT+LS','Fine brush']],
play:[
['move','axis:LS','Move'],['camera','axis:RS','Look'],['interact','tap:RT','Primary action'],['secondary','tap:LT','Secondary action'],['grab','hold:RG','Contextual grab'],['menu','tap:X','Action wheel'],['jump','tap:A','Jump / action'],['back','tap:B','Close menu'],['pause','tap:Y','Pause'],['quick-action','chord:X+RT','Quick action']]
};
const PARAMS={triggerThreshold:[.2,.95,.62],gripThreshold:[.2,.95,.6],stickDeadzone:[0,.5,.18],precisionMultiplier:[.02,1,.12],snapDegrees:[1,90,15],chordMs:[60,450,160],longPressMs:[250,1200,450],doubleTapMs:[120,600,280],turnSensitivity:[.1,3,1],brushSensitivity:[.05,3,1]};
const clone=v=>JSON.parse(JSON.stringify(v));
const defaults=()=>({
 schema:SCHEMA,profileId:'kami-precision',profileName:'Kami Precision',profileVersion:1,
 createdAt:'2026-10-31T00:00:00.000Z',modifiedAt:'2026-10-31T00:00:00.000Z',
 dominantHand:'right',thresholds:Object.fromEntries(Object.entries(PARAMS).map(([k,a])=>[k,a[2]])),
 bindings:clone(BASE),customProfiles:[],activeContext:'game'
});
function mirrorCombo(text){const swap={LT:'RT',RT:'LT',LG:'RG',RG:'LG',LS:'RS',RS:'LS',A:'X',X:'A',B:'Y',Y:'B'};return text.replace(/\b(?:LT|RT|LG|RG|LS|RS|A|B|X|Y)\b/g,key=>swap[key]);}
const builtins=(()=>{
 const kami=defaults();
 const standard=clone(kami);standard.profileId='standard';standard.profileName='Standard';standard.bindings=Object.fromEntries(CONTEXTS.map(k=>[k,clone(BASE[k]).filter(row=>!['duplicate-place','temporary-smooth','two-hand','fine'].includes(row[0]))]));
 const left=clone(kami);left.profileId='left-handed';left.profileName='Left-Handed';left.dominantHand='left';for(const ctx of CONTEXTS)left.bindings[ctx]=BASE[ctx].map(([a,b,c])=>[a,mirrorCombo(b),c]);
 const sculpt=clone(kami);sculpt.profileId='precision-sculpt';sculpt.profileName='Precision Sculpt';sculpt.thresholds.precisionMultiplier=.06;sculpt.thresholds.brushSensitivity=.4;
 return [kami,standard,left,sculpt];
})();
const builtInIds=new Set(builtins.map(x=>x.profileId));
const RESERVED=/\b(?:META|MENU|HOME|SYSTEM|OCULUS|QUEST)\b/i;
function parseBinding(binding){
 if(typeof binding!=='string'||binding.length>64||RESERVED.test(binding))throw Error('Reserved or invalid controller binding');
 const m=/^(tap|double|hold|chord|axis|sequence):([A-Z+>]+)$/.exec(binding);
 if(!m)throw Error('Binding syntax: tap:, hold:, chord:, double:, axis: or sequence:');
 const kind=m[1],sep=kind==='sequence'?'>':'+',buttons=m[2].split(sep);
 if(buttons.some(s=>!Object.hasOwn(LABEL,s))||new Set(buttons).size!==buttons.length)throw Error('Unknown or repeated controller input');
 if((kind==='tap'||kind==='double'||kind==='axis')&&buttons.length!==1)throw Error('Single-input binding expected');
 if(kind==='axis'&&!['LS','RS'].includes(buttons[0]))throw Error('Axis requires LS or RS');
 if((kind==='chord'||kind==='sequence')&&buttons.length<2)throw Error('Combination needs multiple inputs');
 if(kind==='hold'&&buttons.length>3||buttons.length>4)throw Error('Too many simultaneous inputs');
 return {kind,buttons,canonical:kind+':'+(kind==='sequence'?buttons.join('>'):buttons.slice().sort().join('+'))};
}
function validateProfile(p){
 if(!p||typeof p!=='object'||Array.isArray(p)||p.schema!==SCHEMA||p.profileVersion!==1)throw Error('Unsupported VR profile schema/version');
 if(typeof p.profileId!=='string'||!/^[a-z0-9-]{1,60}$/.test(p.profileId)||typeof p.profileName!=='string'||!p.profileName.trim()||p.profileName.length>100)throw Error('Invalid profile identity');
 if(!['left','right'].includes(p.dominantHand))throw Error('Invalid dominant hand');
 if(!p.thresholds||typeof p.thresholds!=='object')throw Error('Missing precision values');
 for(const [key,[low,high]] of Object.entries(PARAMS)){const v=p.thresholds[key];if(typeof v!=='number'||!Number.isFinite(v)||v<low||v>high)throw Error('Out-of-range '+key);}
 if(!p.bindings||typeof p.bindings!=='object'||Object.keys(p.bindings).sort().join(',')!==CONTEXTS.slice().sort().join(','))throw Error('Invalid mode list');
 const warnings=[];
 for(const ctx of CONTEXTS){
  const rows=p.bindings[ctx];if(!Array.isArray(rows)||rows.length>60)throw Error('Invalid binding rows');
  const seen=new Set();
  for(const row of rows){
   if(!Array.isArray(row)||row.length!==3||!ACTIONS.has(row[0])||typeof row[2]!=='string'||row[2].length>120)throw Error('Unknown action');
   const parsed=parseBinding(row[1]),key=parsed.canonical;
   if(seen.has(key))throw Error('Ambiguous duplicate binding in '+ctx+': '+row[1]);
   seen.add(key);
   if(ctx!=='global'&&p.bindings.global.some(globalRow=>parseBinding(globalRow[1]).canonical===key))
    warnings.push(ctx+': '+row[1]+' shadows the Global shortcut');
  }
 }
 return warnings;
}
function sanitise(raw){
 if(!raw||typeof raw!=='object'||Array.isArray(raw))throw Error('Invalid file');
 const p=clone(raw);
 // Imported JSON cannot carry code, external URLs, tokens or hidden fields.
 const keys=['schema','profileId','profileName','profileVersion','createdAt','modifiedAt','dominantHand','thresholds','bindings'];
 for(const k of Object.keys(p))if(!keys.includes(k))throw Error('Unknown profile field: '+k);
 for(const context of CONTEXTS)p.bindings?.[context]?.forEach(row=>{if(row.length!==3)throw Error('Bad binding row')});
 validateProfile(p);return p;
}
// A test-only combination resolver: returns symbolic actions, never native writes.
// Captured modifiers suppress singles even if the buttons are subsequently released.
const keyState={pressed:new Map(),consumed:new Set(),fired:new Set(),previousTap:new Map(),context:null};
function clearKeyState(){keyState.pressed.clear();keyState.consumed.clear();keyState.fired.clear();keyState.previousTap.clear();}
function testInput(event,ctx='game'){
 if(!CONTEXTS.includes(ctx)||ctx==='global'||!event||!['down','up','tick','axis','reset'].includes(event.type))throw Error('Invalid diagnostic controller input');
 const time=event.time;
 if(typeof time!=='number'||!Number.isFinite(time)||time<0)throw Error('Invalid event timestamp');
 if(keyState.context!==ctx){clearKeyState();keyState.context=ctx;}
 if(event.type==='reset'){clearKeyState();return [];}
 const key=event.key;
 if(event.type!=='tick'&&!Object.hasOwn(LABEL,key))throw Error('Unknown controller key');
 const rows=[...state.bindings[ctx],...(ctx==='play'?state.bindings.global.filter(row=>row[0]==='open-settings'):state.bindings.global)];
 const fired=[],used=new Set();
 const emit=(row,parsed)=>{
  const identity=parsed.canonical;
  if(used.has(identity)||keyState.fired.has(identity))return;
  used.add(identity);keyState.fired.add(identity);
  parsed.buttons.forEach(k=>keyState.consumed.add(k));
  fired.push(Object.freeze({action:row[0],binding:row[1],context:ctx,simulation:true}));
 };
 if(event.type==='down'&&!keyState.pressed.has(key))keyState.pressed.set(key,time);
 if(event.type==='axis'){
  if(typeof event.value!=='number'||!Number.isFinite(event.value)||Math.abs(event.value)>1)throw Error('Invalid axis value');
  const row=rows.find(r=>{const p=parseBinding(r[1]);return p.kind==='axis'&&p.buttons[0]===key;});
  return row&&Math.abs(event.value)>=state.thresholds.stickDeadzone?
   [{action:row[0],binding:row[1],context:ctx,simulation:true,value:event.value}]:[];
 }
 for(const row of rows){
  const parsed=parseBinding(row[1]),keys=parsed.buttons;
  if(parsed.kind==='chord'&&keys.every(k=>keyState.pressed.has(k))){
   const timestamps=keys.map(k=>keyState.pressed.get(k));
   if(Math.max(...timestamps)-Math.min(...timestamps)<=state.thresholds.chordMs)emit(row,parsed);
  }else if(parsed.kind==='hold'&&keys.every(k=>keyState.pressed.has(k))
       &&time-Math.max(...keys.map(k=>keyState.pressed.get(k)))>=state.thresholds.longPressMs){
   emit(row,parsed);
  }
 }
 if(event.type==='up'&&keyState.pressed.has(key)){
  keyState.pressed.delete(key);
  if(!keyState.consumed.has(key)){
   const double=rows.find(r=>{const p=parseBinding(r[1]);return p.kind==='double'&&p.buttons[0]===key;});
   const tap=rows.find(r=>{const p=parseBinding(r[1]);return p.kind==='tap'&&p.buttons[0]===key;});
   const prior=keyState.previousTap.get(key);
   if(double&&typeof prior==='number'&&time-prior<=state.thresholds.doubleTapMs){
    const parsed=parseBinding(double[1]);keyState.fired.delete(parsed.canonical);emit(double,parsed);keyState.previousTap.delete(key);
   }else if(tap){fired.push(Object.freeze({action:tap[0],binding:tap[1],context:ctx,simulation:true}));keyState.previousTap.set(key,time);}
   else keyState.previousTap.set(key,time);
  }
  keyState.consumed.delete(key);
  if(!keyState.pressed.size)keyState.fired.clear();
 }
 return fired;
}
let state=defaults(),saved=null,dialog=null,chosenContext='game',editing=false,recording=null,diagnostic=false,lastDiagnostic='No controller session attached',xrSupported=null,activeSession=null;
function restore(){
 try{
  const data=localStorage.getItem(STORAGE);if(!data)return;
  const raw=JSON.parse(data);if(raw.schema!==SCHEMA||!Array.isArray(raw.customProfiles)||raw.customProfiles.length>15)throw Error('Profile library incompatible');
  const safe=raw.customProfiles.map(sanitise);
  const id=String(raw.activeId||'kami-precision');
  state=safe.find(p=>p.profileId===id)||builtins.find(p=>p.profileId===id)||builtins[0];
  state=clone(state);state.customProfiles=safe;state.activeContext=CONTEXTS.includes(raw.activeContext)?raw.activeContext:'game';
  validateProfile(state);
 }catch(e){state=defaults();lastDiagnostic='Local VR controls could not be loaded: '+String(e.message);}
}
restore();
function save(){
 const custom=(state.customProfiles||[]).map(sanitise);
 localStorage.setItem(STORAGE,JSON.stringify({schema:SCHEMA,activeId:state.profileId,activeContext:chosenContext,customProfiles:custom}));
 saved=clone(state);
}
function open(){
 if(!dialog)mount();
 if(!dialog)return false;
 dialog.showModal?(!dialog.open&&dialog.showModal()):dialog.setAttribute('open','');
 render();return true;
}
function close(){if(dialog?.open)dialog.close();else dialog?.removeAttribute('open');resetInputs();}
function resetInputs(){recording=null;}
function profileList(){return [...builtins,...(state.customProfiles||[])];}
function selectProfile(id){
 const from=profileList().find(p=>p.profileId===id);if(!from)return;
 const custom=state.customProfiles||[];state=clone(from);state.customProfiles=custom;editing=false;render();
}
function customize(){
 const custom=state.customProfiles||[];
 if(custom.length>=15)throw Error('Custom profile limit reached');
 const id='custom-'+Date.now().toString(36);
 const next=clone(state);delete next.customProfiles;delete next.activeContext;
 next.profileId=id;next.profileName=state.profileName+' copy';next.createdAt=new Date().toISOString();next.modifiedAt=next.createdAt;
 custom.push(sanitise(next));state=clone(next);state.customProfiles=custom;editing=true;render();
}
function updateEditable(){
 const copy=clone(state);delete copy.customProfiles;delete copy.activeContext;
 copy.modifiedAt=new Date().toISOString();validateProfile(copy);
 const idx=state.customProfiles.findIndex(p=>p.profileId===copy.profileId);
 if(idx<0)throw Error('Customize a built-in profile before editing');
 state.customProfiles[idx]=copy;
}
function status(message,bad=false){const el=dialog?.querySelector('#se179Message');if(el){el.textContent=message;el.dataset.error=String(bad);}}
function el(tag,cl,txt){const x=document.createElement(tag);if(cl)x.className=cl;if(txt!=null)x.textContent=String(txt);return x;}
function button(label,fn){const b=el('button','se179-button',label);b.type='button';b.onclick=fn;return b;}
function render(){
 if(!dialog)return;
 const body=dialog.querySelector('#se179Body');if(!body)return;body.replaceChildren();
 const top=el('div','se179-row');
 const select=el('select');select.setAttribute('aria-label','VR controller profile');
 for(const p of profileList()){const option=el('option','',p.profileName+(builtInIds.has(p.profileId)?' · preset':''));option.value=p.profileId;select.append(option);}select.value=state.profileId;select.onchange=()=>selectProfile(select.value);top.append(select);
 top.append(button('Customize copy',()=>{try{customize();status('Editable copy created. Save changes when ready.')}catch(e){status(e.message,true)}}));
 if(!builtInIds.has(state.profileId)){
  top.append(button('Rename',()=>{const v=prompt('Profile name',state.profileName);if(v===null)return;try{state.profileName=v.trim();updateEditable();render()}catch(e){status(e.message,true)}}));
  top.append(button('Delete',()=>{if(!confirm('Delete this custom VR profile?'))return;state.customProfiles=state.customProfiles.filter(p=>p.profileId!==state.profileId);selectProfile('kami-precision')}));
 }
 body.append(top);
 const notice=el('p','se179-note','Device-local configuration only. Tracked immersive editing, controller capture and cloud sync are not active in this release. Built-in profiles are immutable; customize a copy.');
 body.append(notice);
 const tabs=el('nav','se179-tabs');for(const ctx of CONTEXTS){const b=button(ctx==='global'?'Global':ctx==='game'?'Game Editor':ctx==='model'?'Model Editor':ctx==='sculpt'?'Sculpt':'Play',()=>{chosenContext=ctx;render()});b.setAttribute('aria-pressed',String(ctx===chosenContext));tabs.append(b);}body.append(tabs);
 const table=el('div','se179-bindings');table.setAttribute('role','group');table.setAttribute('aria-label',chosenContext+' controller mappings');
 const readOnly=builtInIds.has(state.profileId);
 for(const row of state.bindings[chosenContext]){
  const line=el('div','se179-binding');line.append(el('span','',row[2]+' ('+row[0]+')'));
  const input=el('input');input.value=row[1];input.setAttribute('aria-label','Binding for '+row[0]);input.disabled=readOnly;input.maxLength=64;
  input.onchange=()=>{const prev=row[1];row[1]=input.value.toUpperCase().replace(/^(TAP|HOLD|DOUBLE|CHORD|AXIS|SEQUENCE):/,a=>a.toLowerCase());try{updateEditable();const warnings=validateProfile(state);status('Mapping changed. '+warnings.join(' · '));render()}catch(e){row[1]=prev;input.value=prev;status(e.message,true)}};
  line.append(input);table.append(line);
 }body.append(table);
 const params=el('details','se179-precision');params.append(el('summary','','Gestures and precision'));
 for(const [key,[min,max]] of Object.entries(PARAMS)){const row=el('label','se179-param');row.append(el('span','',key));const inp=el('input');inp.type='number';inp.step=(max>100)?'1':'0.01';inp.min=min;inp.max=max;inp.value=state.thresholds[key];inp.disabled=readOnly;inp.onchange=()=>{const old=state.thresholds[key];state.thresholds[key]=Number(inp.value);try{updateEditable();status('Precision parameter updated. Save to persist.')}catch(e){state.thresholds[key]=old;inp.value=old;status(e.message,true)}};row.append(inp);params.append(row);}body.append(params);
 const controls=el('div','se179-row');
 controls.append(button('Save locally',()=>{try{save();status('VR profile saved on this device.')}catch(e){status('Save failed: '+e.message,true)}}));
 controls.append(button('Revert',()=>{if(!confirm('Discard unsaved VR settings?'))return;restore();render();status('Reverted local VR settings.')}));
 controls.append(button('Export JSON',()=>{const copy=clone(state);delete copy.customProfiles;delete copy.activeContext;const blob=new Blob([JSON.stringify(copy,null,2)],{type:'application/json'}),url=URL.createObjectURL(blob),a=el('a');a.href=url;a.download=copy.profileId+'.vr.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),0)}));
 const importInput=el('input');importInput.type='file';importInput.accept='.json,application/json';importInput.hidden=true;importInput.onchange=async()=>{
  try{const file=importInput.files?.[0];if(!file)return;if(file.size>65536)throw Error('Profile JSON exceeds 64 KiB');
   const p=sanitise(JSON.parse(await file.text()));if(builtInIds.has(p.profileId))throw Error('Cannot replace a built-in preset');
   const existing=state.customProfiles.find(x=>x.profileId===p.profileId);if(existing&&!confirm('Replace an existing custom profile?'))return;
   const others=state.customProfiles.filter(x=>x.profileId!==p.profileId);if(others.length>=15)throw Error('Custom profile limit reached');
   others.push(p);state=clone(p);state.customProfiles=others;render();status('Imported into unsaved local profile library. Save locally to keep it.');
  }catch(e){status('Import rejected: '+e.message,true)}finally{importInput.value=''}
 };
 controls.append(button('Import JSON',()=>importInput.click()),importInput);
 body.append(controls);
 const diagram=el('div','se179-diagram');diagram.append(el('strong','','Controller input map · 2D simulation (not hardware capture)'));
 diagram.append(button('Test X+A chord',()=>{testInput({type:'reset',time:0},chosenContext==='global'?'game':chosenContext);testInput({type:'down',key:'X',time:0},chosenContext==='global'?'game':chosenContext);const fired=testInput({type:'down',key:'A',time:70},chosenContext==='global'?'game':chosenContext);testInput({type:'up',key:'A',time:100},chosenContext==='global'?'game':chosenContext);testInput({type:'up',key:'X',time:120},chosenContext==='global'?'game':chosenContext);status('Simulated action: '+(fired.map(e=>e.action).join(', ')||'unassigned')+' (no editor mutation).');}));
 diagram.append(button('Test Y+B save hold',()=>{const c=chosenContext==='global'?'game':chosenContext;testInput({type:'reset',time:0},c);testInput({type:'down',key:'Y',time:0},c);testInput({type:'down',key:'B',time:50},c);const fired=testInput({type:'tick',time:550},c);const releases=[...testInput({type:'up',key:'B',time:600},c),...testInput({type:'up',key:'Y',time:610},c)];status('Simulated: '+fired.map(e=>e.action).join(', ')+'; extra actions: '+releases.length+' (no editor mutation).');}));
 const keys=el('div','se179-keys');for(const [k,name] of Object.entries(LABEL)){
  keys.append(button(k+' · '+name,()=>{lastDiagnostic='Simulated '+k+' button · native scene unchanged';if(recording){recording.push(k);status('Simulated input: '+recording.join('+')+'; use binding text to assign.')}else status(lastDiagnostic)}));
 }diagram.append(keys);body.append(diagram);
 const diag=el('details','se179-diagnostics');diag.open=diagnostic;diag.append(el('summary','','XR capability and diagnostics'));
 const read=window.SWYRL_ENGINE_DEVICE?.read?.()||{};
 diag.append(el('pre','',JSON.stringify({browserProfile:read.profile||'unknown',xrApi:!!navigator.xr,immersiveVRSupported:xrSupported===null?'NOT YET TESTED':xrSupported?'SUPPORTED':'UNSUPPORTED',activeXRSession:!!activeSession,trackedControllers:activeSession?activeSession.inputSources?.length||0:'NOT CURRENTLY AVAILABLE',bindingExecution:'NOT CONNECTED TO NATIVE EDITORS',profile:state.profileName,context:chosenContext,lastInput:lastDiagnostic},null,2)));
 diag.append(button('Check immersive VR support',async()=>{diagnostic=true;try{xrSupported=!!(navigator.xr&&await navigator.xr.isSessionSupported('immersive-vr'));render();status(xrSupported?'Immersive VR API supported. Tracked editing adapter not connected.':'Immersive VR unsupported in this browser.')}catch(e){xrSupported=false;render();status('Immersive VR capability unavailable: '+e.message,true)}}));
 body.append(diag);
 const w=validateProfile(state);if(w.length)body.append(el('p','se179-warnings','Global overrides: '+w.join(' · ')));
}
function mount(){
 if(dialog)return;
 const bar=document.querySelector('.topbar');if(!bar)return;
 const launcher=button('🎮 VR Controls',open);launcher.id='se179VRControlsOpen';launcher.title='Controller profiles and diagnostics';bar.append(launcher);
 dialog=el('dialog','se179-dialog');dialog.id='se179VRStudio';
 const head=el('div','se179-header');head.append(el('strong','','§E · VR Controller Studio'),button('✕ Close',close));
 const body=el('div','se179-body');body.id='se179Body';
 const msg=el('p','se179-message');msg.id='se179Message';msg.setAttribute('role','status');
 dialog.append(head,body,msg);dialog.addEventListener('close',resetInputs);document.body.append(dialog);
}
function attachSession(session){
 // An existing approved immersive renderer may integrate through this hook.
 // Do not request an XR session or start a competing frame loop.
 if(!session||!('inputSources'in session)||typeof session.addEventListener!=='function')throw Error('Verified XR session required');
 if(activeSession&&activeSession!==session)throw Error('XR session already attached');
 activeSession=session;session.addEventListener('end',()=>{if(activeSession===session){activeSession=null;resetInputs();lastDiagnostic='XR session ended'}} ,{once:true});return true;
}
const api=Object.freeze({
 schema:SCHEMA,open,close,read:()=>({schema:SCHEMA,profileId:state.profileId,profileName:state.profileName,contexts:CONTEXTS.slice(),supportedAPI:!!navigator.xr,sessionAttached:!!activeSession,immersiveCommandsActive:false}),
 inspectBinding:parseBinding,validateProfile,attachSession,testInput,
 diagnose:()=>({xrSupported,sessionAttached:!!activeSession,inputSources:activeSession?Array.from(activeSession.inputSources).map(s=>({handedness:s.handedness,profiles:s.profiles,gamepadButtons:s.gamepad?.buttons?.length??0,gamepadAxes:s.gamepad?.axes?.length??0,hasGrip:!!s.gripSpace})):[],liveNativeDispatch:false}),
 resetInput:resetInputs
});
window.SWYRL_VR_CONTROLS=api;
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',mount,{once:true});else mount();
window.addEventListener('load',mount,{once:true});
})();