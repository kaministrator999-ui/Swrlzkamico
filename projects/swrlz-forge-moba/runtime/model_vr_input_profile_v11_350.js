// §E v11.350 — frame-sampled, profile-driven Model VR controller input.
// This helper owns no XR session, renderer, animation loop or native edits.
const SE350_MODEL_VR_BINDINGS=Object.freeze({
 model:[['select','tap:RT','Select part'],['multiselect','tap:LT','Add / remove part'],
  ['grab','hold:RG','Transform selection'],['pan','hold:LG','Move workbench'],
  ['navigate','axis:LS','Pan model'],['orbit','axis:RS','Orbit camera around stationary model'],
  ['tool','tap:A','Next tool'],['tool-wheel','hold:A','Quick tool wheel'],
  ['cancel','tap:B','Cancel / Inspect'],['palette','tap:X','Show tool palette'],
  ['category-wheel','hold:X','Studio categories'],['undo','tap:Y','Undo'],
  ['two-hand','hold:LG+RG','Two-hand transform'],['precision','tap:LS','Precision mode']],
 sculpt:[['stroke','hold:RT','Sculpt stroke'],['sample','tap:LT','Sample surface'],
  ['temporary-smooth','hold:LT','Temporary smooth'],['grab','hold:RG','Transform selection'],
  ['pan','hold:LG','Move workbench'],['radius','axis:LS','Brush radius / strength'],
  ['orbit','axis:RS','Orbit camera around stationary model'],['tool','tap:A','Next brush'],
  ['tool-wheel','hold:A','Quick brush wheel'],['cancel','tap:B','Cancel stroke / Inspect'],
  ['palette','tap:X','Show tool palette'],['category-wheel','hold:X','Studio categories'],
  ['undo','tap:Y','Undo stroke'],['two-hand','hold:LG+RG','Two-hand transform'],
  ['precision','tap:LS','Precision mode']]
});
function se350CreateModelVRInput({getProfile}={}){
 const allowed=new Set(['select','multiselect','grab','pan','navigate','orbit','zoom','tool',
  'tool-wheel','category-wheel','cancel','palette','undo','redo','focus','precision','snap',
  'toggle-snap','two-hand','wireframe','reset-camera','stroke','sample','radius','strength',
  'temporary-smooth','fine','mirror','preview','open-settings']);
 const labels=new Set(['LT','RT','LG','RG','LS','RS','A','B','X','Y']);
 const defaults={triggerThreshold:.62,gripThreshold:.6,stickDeadzone:.18,
  precisionMultiplier:.12,snapDegrees:15,chordMs:160,longPressMs:450,
  doubleTapMs:280,turnSensitivity:1,brushSensitivity:1};
 const limits={triggerThreshold:[.2,.95],gripThreshold:[.2,.95],stickDeadzone:[0,.5],
  precisionMultiplier:[.02,1],snapDegrees:[1,90],chordMs:[60,450],longPressMs:[250,1200],
  doubleTapMs:[120,600],turnSensitivity:[.1,3],brushSensitivity:[.05,3]};
 let fingerprint='',context='',profile=null,rows=[],thresholds={...defaults},lastTime=null;
 let pressed=new Map(),consumed=new Set(),active=new Map(),fired=new Set(),previousTap=new Map(),sourceForKey=new Map();
 let sequence=new Map(),blocked=new Set(),lastPhysical=new Set(),invalidBindings=[],profileChanged=false,cancelKeys=[];
 const trackedSources=new Map();
 function parse(text){
  if(typeof text!=='string'||text.length>64||/\b(?:META|MENU|HOME|SYSTEM|OCULUS|QUEST)\b/i.test(text))return null;
  const m=/^(tap|double|hold|chord|axis|sequence):([A-Z+>]+)$/.exec(text);if(!m)return null;
  const keys=m[2].split(m[1]==='sequence'?'>':'+');
  if(keys.some(k=>!labels.has(k))||new Set(keys).size!==keys.length||keys.length>4)return null;
  if(['tap','double','axis'].includes(m[1])&&keys.length!==1)return null;
  if(m[1]==='axis'&&!['LS','RS'].includes(keys[0]))return null;
  if(['chord','sequence'].includes(m[1])&&keys.length<2)return null;
  if(m[1]==='hold'&&keys.length>3)return null;
  return {kind:m[1],keys,id:m[1]+':'+(m[1]==='sequence'?keys.join('>'):keys.slice().sort().join('+'))};
 }
 function clear(){pressed.clear();consumed.clear();active.clear();fired.clear();previousTap.clear();sequence.clear();sourceForKey.clear();}
 function reset(){clear();blocked=new Set(lastPhysical);lastTime=null;cancelKeys=[];}
 function load(ctx,physical){
  let raw;try{raw=getProfile?.();}catch(_){raw=null;}
  if(!raw||typeof raw!=='object')raw={profileId:'model-vr-two-hand',profileName:'Model VR · two hand',
   bindings:{...SE350_MODEL_VR_BINDINGS,global:[['redo','chord:X+Y','Redo'],['focus','tap:RS','Focus']]},thresholds:defaults};
  const safe={profileId:String(raw.profileId||'custom').slice(0,60),profileName:String(raw.profileName||'Custom').slice(0,100),
   bindings:{global:raw.bindings?.global,model:raw.bindings?.model,sculpt:raw.bindings?.sculpt},thresholds:raw.thresholds};
  const next=JSON.stringify([safe,ctx]);profileChanged=next!==fingerprint;
  if(!profileChanged)return;
  fingerprint=next;context=ctx;profile={id:safe.profileId,name:safe.profileName};clear();
  // Changing a profile/context while a control is held must never start a new edit.
  blocked=new Set(physical);thresholds={...defaults};
  for(const [key,[lo,hi]] of Object.entries(limits)){
   const value=safe.thresholds?.[key];if(typeof value==='number'&&Number.isFinite(value)&&value>=lo&&value<=hi)thresholds[key]=value;
  }
  rows=[];invalidBindings=[];const seen=new Set();
  for(const row of [...(Array.isArray(safe.bindings[ctx])?safe.bindings[ctx].slice(0,60):[]),
   ...(Array.isArray(safe.bindings.global)?safe.bindings.global.slice(0,60):[])]){
   const parsed=Array.isArray(row)&&parse(row[1]);
   const continuous=Array.isArray(row)&&['grab','pan','stroke'].includes(row[0]);
   const axis=Array.isArray(row)&&['navigate','orbit','zoom','radius','strength'].includes(row[0]);
   if(!parsed||!allowed.has(row[0])||continuous&&parsed.kind!=='hold'||axis&&parsed.kind!=='axis'){
    invalidBindings.push(Array.isArray(row)?String(row[0]).slice(0,40):'invalid');continue;
   }
   if(seen.has(parsed.id))continue;seen.add(parsed.id);
   rows.push({action:row[0],binding:row[1],...parsed});
  }
  // Resolve explicit modifiers before singles, and cancel before commit-like actions.
  rows.sort((a,b)=>(a.action==='cancel'?-1:b.action==='cancel'?1:0)||b.keys.length-a.keys.length);
 }
 function sample({time,context:ctx='model',sources=[]}={}){
  if(!Number.isFinite(time)||time<0)throw Error('Finite XR input timestamp required');
  if(!['model','sculpt'].includes(ctx))throw Error('Model or sculpt input context required');
  const hadProfile=!!fingerprint,hadActivity=active.size>0,previousActive=[...active.values()];
  const clockReset=lastTime!==null&&time<lastTime;
  // Read thresholds before interpreting hardware values, including a changed profile.
  load(ctx,new Set());
  const physical=new Set(),owners=new Map(),axesByKey=new Map(),newlyTrackedKeys=new Set(),presentSources=new Set();
  const numeric=value=>typeof value==='number'&&Number.isFinite(value)?Math.max(-1,Math.min(1,value)):0;
  for(const source of Array.isArray(sources)?sources.slice(0,8):[]){
   const input=source.input||source,side=input?.handedness;
   if(!['left','right'].includes(side))continue;
   presentSources.add(input);
   if(source.tracked===false){trackedSources.set(input,false);continue;}
   const justTracked=trackedSources.get(input)!==true;trackedSources.set(input,true);
   const pad=input.gamepad;if(!pad)continue;
   for(const [key,index,cutoff] of [[side==='left'?'LT':'RT',0,thresholds.triggerThreshold],
    [side==='left'?'LG':'RG',1,thresholds.gripThreshold],[side==='left'?'LS':'RS',3,.5],
    [side==='left'?'X':'A',4,.5],[side==='left'?'Y':'B',5,.5]]){
    const button=pad.buttons?.[index],value=button&&numeric(button.value);
    // WebXR .pressed may use a browser-specific threshold; analog thresholds are profile-owned.
    if(button&&(typeof button.value==='number'?value>=cutoff:button.pressed===true)){
     physical.add(key);owners.set(key,source);if(justTracked)newlyTrackedKeys.add(key);
    }
   }
   const raw=pad.axes||[],x=numeric(raw[raw.length-2]),y=numeric(raw[raw.length-1]);
   axesByKey.set(side==='left'?'LS':'RS',{x,y,source,hand:side});
  }
  for(const input of trackedSources.keys())if(!presentSources.has(input))trackedSources.set(input,false);
  const trackingLost=previousActive.some(v=>trackedSources.get(v.source?.input||v.source)!==true);
  if(profileChanged)blocked=new Set(physical);
  if(clockReset){reset();blocked=new Set(physical);}
  lastTime=time;lastPhysical=new Set(physical);
  for(const key of newlyTrackedKeys)blocked.add(key);
  for(const key of [...blocked])if(!physical.has(key))blocked.delete(key);
  const down=new Set([...physical].filter(k=>!blocked.has(k))),rising=[],falling=[];
  for(const key of down)if(!pressed.has(key)){pressed.set(key,time);sourceForKey.set(key,owners.get(key));rising.push(key);}
  for(const key of pressed.keys())if(!down.has(key))falling.push(key);
  const events=[],held=Object.create(null),axes=Object.create(null),ending=[];
  const owner=row=>row.keys.map(k=>owners.get(k)).find(Boolean)||active.get(row.id)?.source||row.keys.map(k=>sourceForKey.get(k)).find(Boolean)||null;
  const event=(row,phase,extra={})=>({action:row.action,phase,binding:row.binding,
   keys:row.keys.slice(),hand:(owner(row)?.input||owner(row))?.handedness||null,source:owner(row),...extra});
  const consume=row=>row.keys.forEach(k=>consumed.add(k));
  const emit=(row,phase)=>{events.push(event(row,phase));consume(row);fired.add(row.id);};
  // Explicit chords win even when both buttons arrive in the same XR frame.
  for(const row of rows.filter(r=>r.kind==='chord')){
   if(row.keys.every(k=>down.has(k))){
    const at=row.keys.map(k=>pressed.get(k));
    if(Math.max(...at)-Math.min(...at)<=thresholds.chordMs&&!fired.has(row.id))emit(row,'tap');
   }
  }
  for(const row of rows.filter(r=>r.kind==='sequence')){
   let state=sequence.get(row.id)||{index:0,at:time};
   if(time-state.at>Math.max(1000,thresholds.doubleTapMs*row.keys.length))state={index:0,at:time};
   for(const key of rising){
    if(key===row.keys[state.index]){state.index++;state.at=time;consumed.add(key);
     if(state.index===row.keys.length){emit(row,'tap');state={index:0,at:time};}}
    else if(key===row.keys[0])state={index:1,at:time};
   }sequence.set(row.id,state);
  }
  for(const row of rows.filter(r=>r.kind==='hold')){
   const all=row.keys.every(k=>down.has(k));
   const immediate=row.keys.length===1&&['grab','pan','stroke'].includes(row.action);
   const ready=all&&(immediate||time-Math.max(...row.keys.map(k=>pressed.get(k)))>=thresholds.longPressMs);
   const chordCaptured=rows.some(r=>r.kind==='chord'&&fired.has(r.id)&&r.keys.some(k=>row.keys.includes(k)));
   if(ready&&!chordCaptured){
    const data=event(row,'start');held[row.action]=data;
    if(!active.has(row.id)){events.push(data);active.set(row.id,data);consume(row);}
   }else if(active.has(row.id)){ending.push(event(row,'end'));active.delete(row.id);}
  }
  // Trigger selection and cancel respond on depression; face taps wait for release.
  for(const row of rows.filter(r=>r.kind==='tap')){
   const key=row.keys[0],immediate=row.action==='cancel'||(key.endsWith('T')&&['select','multiselect','sample'].includes(row.action));
   if(immediate&&rising.includes(key)&&!consumed.has(key)){
    events.push(event(row,'tap'));if(row.action==='cancel')consume(row);fired.add(row.id);
   }
  }
  for(const key of falling){
   if(!consumed.has(key)){
    const double=rows.find(r=>r.kind==='double'&&r.keys[0]===key);
    const tap=rows.find(r=>r.kind==='tap'&&r.keys[0]===key);
    const prior=previousTap.get(key);
    if(double&&typeof prior==='number'&&time-prior<=thresholds.doubleTapMs){events.push(event(double,'tap'));previousTap.delete(key);}
    else if(double){previousTap.set(key,time);}
    else if(tap&&!fired.has(tap.id))events.push(event(tap,'tap'));
   }
   pressed.delete(key);consumed.delete(key);
   for(const row of rows)if(row.keys.includes(key))fired.delete(row.id);
  }
  // A double binding suppresses its first single until the double-tap window expires.
  for(const [key,at] of [...previousTap])if(time-at>thresholds.doubleTapMs){
   const tap=rows.find(r=>r.kind==='tap'&&r.keys[0]===key);if(tap)events.push(event(tap,'tap'));previousTap.delete(key);
  }
  for(const row of rows.filter(r=>r.kind==='axis')){
   const a=axesByKey.get(row.keys[0]);if(!a)continue;
   const magnitude=Math.hypot(a.x,a.y),length=Math.min(1,magnitude),dz=thresholds.stickDeadzone;
   if(length<=dz)continue;
   const scale=(length-dz)/(1-dz)/Math.max(magnitude,.000001);
   axes[row.action]={...event(row,'axis'),x:a.x*scale,y:a.y*scale,source:a.source,hand:a.hand};
  }
  const cancel=events.some(e=>e.action==='cancel');
  if(cancel)cancelKeys=events.filter(e=>e.action==='cancel').flatMap(e=>e.keys);
  const cancelHeld=cancelKeys.some(key=>physical.has(key));
  if(!cancelHeld)cancelKeys=[];
  if(cancel){
   // Cancel wins over releases from either controller and prevents immediate re-entry.
   for(const key of physical)blocked.add(key);clear();
   events.splice(0,events.length,...events.filter(e=>e.action==='cancel'));
   for(const key of Object.keys(held))delete held[key];for(const key of Object.keys(axes))delete axes[key];
  }else if(trackingLost||cancelHeld){for(const key of physical)blocked.add(key);clear();events.length=0;}
  else events.push(...ending);
  const buttons=Object.fromEntries([...labels].map(key=>[key,{down:down.has(key),physical:physical.has(key),
   pressed:rising.includes(key),released:falling.includes(key),source:owners.get(key)||sourceForKey.get(key)||null}]));
  if(trackingLost||cancelHeld){for(const key of Object.keys(held))delete held[key];for(const key of Object.keys(axes))delete axes[key];}
  return {events,held,axes,buttons,cancel,trackingLost,profileChanged:hadProfile&&profileChanged,
   resetRequired:trackingLost||clockReset||hadProfile&&profileChanged&&hadActivity,
   profile:{...profile},thresholds:{...thresholds},invalidBindings:invalidBindings.slice()};
 }
 return Object.freeze({sample,reset,inspect:()=>({profile:profile&&{...profile},context,
  active:[...active.values()].map(v=>({action:v.action,binding:v.binding})),invalidBindings:invalidBindings.slice()})});
}
