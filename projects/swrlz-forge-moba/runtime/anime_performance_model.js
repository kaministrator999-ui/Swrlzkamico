// Reusable performances stay in the native project. Their pose offsets are
// evaluated from story time, so Preview, Play, reverse and Save/Load agree.
const PERFORMANCE_SCHEMA='anime-performance-v1';
const PERFORMANCE_ACTIONS=Object.freeze([
  {id:'greet',label:'Greet'}, {id:'reach',label:'Reach'},
  {id:'brace',label:'Brace'}, {id:'cast',label:'Cast'},
  {id:'write',label:'Write'}, {id:'step',label:'Step'},
  {id:'hover',label:'Hover'}, {id:'recover',label:'Recover'}
]);
const PERFORMANCE_ACTION_IDS=new Set(PERFORMANCE_ACTIONS.map(item=>item.id));
const PERFORMANCE_MAX_CLIPS=128;
let performanceValidatedProject=null,performanceValidatedModel=null,performanceValidatedDuration=null;
let performanceSamplingDepth=0,performancePendingDuration=null;
function performanceIsProject(){
  return !!currentProject&&(currentProject.canonicalId==='ghosts-different-forms-ep01'||currentProject.animeTimeline?.schema===STORY_SCHEMA);
}
function performanceHasProfile(){return performanceIsProject()&&currentProject.animePerformance?.schema===PERFORMANCE_SCHEMA;}
function performanceDefaultModel(){
  return {schema:PERFORMANCE_SCHEMA,enabled:false,limitDialogue:true,maxDialogueSeconds:4.5,clips:[]};
}
function performanceId(value){return typeof value==='string'&&/^[A-Za-z0-9][A-Za-z0-9_.:-]{0,63}$/.test(value)?value:null;}
function performanceCleanClip(value,duration=storyTimeline().duration){
  const raw=rigObject(value),id=performanceId(raw.id);
  if(!id||!RIG_CHARACTERS.includes(raw.character)||!PERFORMANCE_ACTION_IDS.has(raw.action))return null;
  duration=storyNumber(duration,134,1,3600);
  const time=storyTime(storyNumber(raw.time,0,0,duration-.05),duration);
  return {id,character:raw.character,action:raw.action,time,
    duration:storyNumber(raw.duration,2,.05,Math.max(.05,duration-time)),
    strength:storyNumber(raw.strength,1,0,1.5),side:raw.side==='left'?'left':'right',
    label:storyText(raw.label,PERFORMANCE_ACTIONS.find(item=>item.id===raw.action).label,100)};
}
function performanceSanitizeModel(value,duration=storyTimeline().duration){
  const raw=rigObject(value),model=performanceDefaultModel(),unique=new Map();
  model.enabled=typeof raw.enabled==='boolean'?raw.enabled:false;
  model.limitDialogue=typeof raw.limitDialogue==='boolean'?raw.limitDialogue:true;
  model.maxDialogueSeconds=storyNumber(raw.maxDialogueSeconds,4.5,1,10);
  for(const value of Array.isArray(raw.clips)?raw.clips.slice(0,PERFORMANCE_MAX_CLIPS):[]){
    const clip=performanceCleanClip(value,duration);if(clip)unique.set(clip.id,clip);
  }
  model.clips=[...unique.values()].sort((a,b)=>a.time-b.time||a.id.localeCompare(b.id));
  return model;
}
function performanceModel(){
  if(!performanceHasProfile())return performanceDefaultModel();
  const duration=storyTimeline().duration;
  if(performanceValidatedProject!==currentProject||performanceValidatedModel!==currentProject.animePerformance||performanceValidatedDuration!==duration){
    currentProject.animePerformance=performanceSanitizeModel(currentProject.animePerformance,duration);
    performanceValidatedProject=currentProject;performanceValidatedModel=currentProject.animePerformance;performanceValidatedDuration=duration;
  }
  return currentProject.animePerformance;
}
function performanceAssign(model){
  currentProject.animePerformance=model;
  performanceValidatedProject=currentProject;performanceValidatedModel=model;performanceValidatedDuration=storyTimeline().duration;
}
function performanceNotify(){
  if(animeCine)storyRender();storyNotify();
  if(typeof performanceEditorSync==='function')performanceEditorSync();
}
function performanceMutate(label,callback){
  if(!performanceIsProject()||!storyEditable()||typeof callback!=='function')return false;
  const previous=performanceModel(),draft=storyCopy(previous);
  if(callback(draft)===false)return false;
  const next=performanceSanitizeModel(draft);
  if(JSON.stringify(previous)===JSON.stringify(next))return true;
  beginTransaction(label);performanceAssign(next);commitTransaction(label);performanceNotify();return true;
}
function performanceFinite(value){
  return (typeof value==='number'||typeof value==='string'&&value.trim()!=='')&&Number.isFinite(Number(value));
}
function performanceUpsert(value){
  if(!value||typeof value!=='object'||Array.isArray(value)||!performanceId(value.id)||
    !RIG_CHARACTERS.includes(value.character)||!PERFORMANCE_ACTION_IDS.has(value.action))return false;
  for(const field of ['time','duration','strength'])if(Object.hasOwn(value,field)&&!performanceFinite(value[field]))return false;
  if(Object.hasOwn(value,'side')&&!['left','right'].includes(value.side))return false;
  return performanceMutate('Story action · '+value.action,draft=>{
    const index=draft.clips.findIndex(clip=>clip.id===value.id);
    if(index<0&&draft.clips.length>=PERFORMANCE_MAX_CLIPS)return false;
    const clip=performanceCleanClip({...draft.clips[index],...value});
    if(!clip)return false;
    if(index<0)draft.clips.push(clip);else draft.clips[index]=clip;
  });
}
function performanceRemove(id){
  if(!performanceId(id))return false;
  return performanceMutate('Delete story action',draft=>{
    const index=draft.clips.findIndex(clip=>clip.id===id);if(index<0)return false;
    draft.clips.splice(index,1);
  });
}
function performanceConfigure(value){
  if(!value||typeof value!=='object'||Array.isArray(value))return false;
  if(Object.hasOwn(value,'maxDialogueSeconds')&&!performanceFinite(value.maxDialogueSeconds))return false;
  for(const field of ['enabled','limitDialogue'])if(Object.hasOwn(value,field)&&typeof value[field]!=='boolean')return false;
  return performanceMutate('Story action settings',draft=>{
    for(const field of ['enabled','limitDialogue','maxDialogueSeconds'])if(Object.hasOwn(value,field))draft[field]=value[field];
  });
}
function performanceSmooth(value){const u=Math.max(0,Math.min(1,value));return u*u*(3-2*u);}
function performanceEnvelope(clip,time){
  const local=time-clip.time;if(local<=0||local>=clip.duration)return 0;
  // Reach the pose, hold it through the action, then settle back into the
  // authored limb curves. Both ends meet those curves with zero velocity.
  const attack=Math.min(.6,clip.duration*.22),release=Math.min(.8,clip.duration*.26);
  return performanceSmooth(local/attack)*performanceSmooth((clip.duration-local)/release)*clip.strength;
}
function performanceActive(time,character){
  const model=performanceModel();if(!model.enabled)return [];
  return model.clips.filter(clip=>(!character||clip.character===character)&&time>clip.time&&time<clip.time+clip.duration)
    .map(clip=>({...clip,weight:performanceEnvelope(clip,time),local:time-clip.time}));
}
function performanceOffsets(character,part,time){
  const result=Object.fromEntries(Object.keys(rigPartBounds(part)).map(field=>[field,0]));
  const add=(field,value)=>{if(Object.hasOwn(result,field))result[field]+=value;};
  for(const clip of performanceActive(time,character)){
    const w=clip.weight,hand=clip.side==='left'?'left':'right',sign=hand==='left'?1:-1;
    const upper=hand+'UpperArm',forearm=hand+'Forearm',palm=hand+'Hand';
    const local=clip.local,cycle=Math.sin(local*Math.PI*2/.9);
    if(clip.action==='greet'){
      if(part===upper){add('rotationZ',sign*.42*w);add('rotationY',sign*.08*w);}
      if(part===forearm)add('rotationZ',-sign*(.18+.1*Math.sin(local*9))*w);
      if(part===palm)add('rotationZ',sign*.11*Math.sin(local*9)*w);
      if(part==='head'){add('rotationZ',sign*.06*w);add('rotationY',sign*.1*w);}
      if(part==='cape')add('rotationZ',-sign*.045*w);
    }else if(clip.action==='reach'){
      if(part===upper){add('rotationZ',sign*.33*w);add('rotationY',-sign*.16*w);}
      if(part===forearm){add('rotationZ',-sign*.24*w);add('rotationX',-.09*w);}
      if(part===palm)add('rotationZ',sign*.08*w);
      if(part==='torso'){add('rotationZ',-sign*.07*w);add('rotationY',-sign*.08*w);}
      if(part==='head'){add('rotationX',.055*w);add('rotationY',-sign*.12*w);}
      if(part==='cape')add('rotationZ',sign*.07*w);
    }else if(clip.action==='brace'){
      if(part==='torso'){add('rotationX',.1*w);add('rotationZ',-.07*w);}
      if(part==='pelvis')add('rotationX',-.07*w);
      if(part==='head')add('rotationX',-.1*w);
      if(part==='leftUpperLeg'||part==='rightUpperLeg')add('rotationX',-.11*w);
      if(part==='leftLowerLeg'||part==='rightLowerLeg')add('rotationX',.16*w);
      if(part===upper)add('rotationZ',sign*.25*w);
      if(part===forearm)add('rotationZ',-sign*.27*w);
      if(part==='cape'){add('rotationX',.12*w);add('rotationZ',.055*w);}
    }else if(clip.action==='cast'){
      const pulse=.5+.5*Math.sin(local*5);
      if(part===upper){add('rotationZ',sign*.34*w);add('rotationY',-sign*.1*w);}
      if(part===forearm){add('rotationZ',-sign*.28*w);add('rotationX',-.07*w);}
      if(part===palm)add('rotationZ',sign*.06*w);
      if(part==='torso'){add('rotationZ',-sign*.05*w);add('rotationY',-sign*.07*w);}
      if(part==='head'){add('rotationX',-.07*w);add('rotationY',-sign*.06*w);}
      if(part==='cape'){add('rotationX',(.06+.025*pulse)*w);add('rotationZ',-sign*.08*w);}
      if(part==='staff'&&character==='kami'&&hand==='left')add('depth',.018*pulse*w);
      if(part==='grimoire'&&character==='swyrlz'){add('rotationX',-.05*w);add('depth',.025*pulse*w);}
    }else if(clip.action==='write'){
      if(part===upper)add('rotationZ',sign*.17*w);
      if(part===forearm){add('rotationZ',-sign*(.17+.035*Math.sin(local*12))*w);add('rotationX',.035*Math.sin(local*9)*w);}
      if(part===palm)add('rotationZ',sign*.045*Math.sin(local*12)*w);
      if(part==='head'){add('rotationX',.09*w);add('rotationZ',sign*.025*w);}
      if(part==='torso')add('rotationX',.045*w);
      if(part==='quill'&&character==='kami'&&hand==='right')add('rotationZ',.035*Math.sin(local*12)*w);
      if(part==='grimoire'&&character==='swyrlz'){add('rotationX',-.07*w);add('rotationZ',.025*Math.sin(local*5)*w);}
    }else if(clip.action==='step'){
      const left=part.startsWith('left'),legSign=left?1:-1,stride=cycle*legSign;
      if(part==='leftUpperLeg'||part==='rightUpperLeg'){add('rotationX',.32*stride*w);add('rotationZ',.18*stride*w);}
      if(part==='leftLowerLeg'||part==='rightLowerLeg')add('rotationX',Math.max(0,-stride)*.38*w);
      if(part==='leftFoot'||part==='rightFoot')add('rotationX',-.16*stride*w);
      if(part==='pelvis'){add('rotationZ',.055*cycle*w);add('rotationY',.05*cycle*w);}
      if(part==='torso'){add('rotationZ',-.04*cycle*w);add('rotationX',.035*w);}
      if(part==='cape')add('rotationZ',.09*Math.sin(local*Math.PI*2/.9-.35)*w);
      // Keep Kami's occupied staff hand quiet while the free arm swings.
      if(part==='rightUpperArm'||character==='swyrlz'&&part==='leftUpperArm')add('rotationX',-.12*stride*w);
    }else if(clip.action==='hover'){
      const drift=Math.sin(local*3.2),flutter=Math.sin(local*4.6);
      if(part==='torso'){add('rotationX',.04*drift*w);add('rotationZ',.035*flutter*w);}
      if(part==='pelvis')add('rotationZ',-.04*flutter*w);
      if(part==='cape'){add('rotationX',.065*drift*w);add('rotationZ',.08*flutter*w);}
      if(part==='leftUpperLeg'||part==='rightUpperLeg')add('rotationX',.07*drift*w);
      if(part==='leftLowerLeg'||part==='rightLowerLeg')add('rotationX',.055*w);
      if(part==='head')add('rotationZ',-.025*flutter*w);
      if(part==='grimoire'){add('rotationY',.065*drift*w);add('depth',.014*(.5+.5*drift)*w);}
    }else if(clip.action==='recover'){
      if(part==='torso'){add('rotationX',.07*w);add('rotationZ',sign*.045*w);}
      if(part==='head'){add('rotationX',.1*w);add('rotationY',sign*.07*w);}
      if(part===upper)add('rotationZ',sign*.12*w);
      if(part===forearm)add('rotationZ',-sign*.1*w);
      if(part==='cape')add('rotationX',-.05*w);
    }
  }
  return result;
}
function performanceDialogue(time){
  const beat=storyBeat(time),cues=beat.cues||[];let cue=null,next=beat.end;
  for(const item of cues){if(item.time>time){next=item.time;break;}cue=item;}
  if(!cue)return null;
  const match=cue.text.trim().match(/^(KAMI|[§$]?WYRLZ)\b\s*:\s*(.*)$/i);
  if(!match)return null;
  const character=/^KAMI$/i.test(match[1])?'kami':'swyrlz',words=match[2].trim().split(/\s+/).filter(Boolean).length;
  const span=Math.min(performanceModel().maxDialogueSeconds,Math.max(1,.45+words*.29));
  return {character,start:cue.time,end:Math.min(next,beat.end,cue.time+span),text:cue.text};
}
const performanceOriginalRigSample=rigSample;
function performanceSample(character,part,time){
  const original=performanceOriginalRigSample(character,part,time);if(!original)return original;
  const model=performanceModel();if(!model.enabled)return original;
  const t=storyNumber(time,0,0,storyTimeline().duration),sample={...original},offsets=performanceOffsets(character,part,t);
  for(const [field,[low,high]] of Object.entries(rigPartBounds(part)))sample[field]=storyNumber(sample[field]+offsets[field],sample[field],low,high);
  if(part==='face'&&model.limitDialogue){
    const dialogue=performanceDialogue(t);sample.speech=sample.speech&&!!dialogue&&dialogue.character===character&&t<dialogue.end;
  }
  return sample;
}
// Renderer-only overlays leave the existing joint/face editor and insertion
// samples on their base curves. Editing a key never bakes the same action twice.
rigSample=function(character,part,time){
  return performanceSamplingDepth?performanceSample(character,part,time):performanceOriginalRigSample(character,part,time);
};
const performanceOriginalAnimate=rigAnimateCharacter;
rigAnimateCharacter=function(group,character,time){
  performanceSamplingDepth++;
  try{return performanceOriginalAnimate(group,character,time);}finally{performanceSamplingDepth--;}
};
const performanceOriginalApplyMeta=applyProjectMeta;
applyProjectMeta=function(meta={}){
  const result=performanceOriginalApplyMeta(meta);
  performanceValidatedProject=null;performanceValidatedModel=null;performanceValidatedDuration=null;
  if(performanceIsProject()&&rigObject(meta.animePerformance).schema===PERFORMANCE_SCHEMA)
    performanceAssign(performanceSanitizeModel(meta.animePerformance));
  else if(currentProject)delete currentProject.animePerformance;
  if(typeof performanceEditorSync==='function')performanceEditorSync();return result;
};
const performanceOriginalProjectData=projectData;
projectData=function(){
  const data=performanceOriginalProjectData();
  if(performanceHasProfile())data.project.animePerformance=storyCopy(performanceModel());
  else delete data.project.animePerformance;
  return data;
};
// Insert the scaled clips inside the existing duration transaction, before its
// single commit. The existing Undo snapshot therefore restores every model.
const performanceOriginalCommit=commitTransaction;
commitTransaction=function(label,...args){
  if(label==='Episode duration'&&performancePendingDuration?.project===currentProject){
    performanceAssign(performancePendingDuration.model);performancePendingDuration=null;
  }
  return performanceOriginalCommit(label,...args);
};
const performanceOriginalSetDuration=storySetDuration;
storySetDuration=function(value){
  const number=Number(value),previous=storyTimeline().duration;
  if(performanceHasProfile()&&storyEditable()&&Number.isFinite(number)&&number>=1&&number<=3600&&number!==previous){
    const draft=storyCopy(performanceModel()),ratio=number/previous;
    for(const clip of draft.clips){clip.time*=ratio;clip.duration*=ratio;}
    performancePendingDuration={project:currentProject,model:performanceSanitizeModel(draft,number)};
  }
  try{return performanceOriginalSetDuration(value);}finally{performancePendingDuration=null;}
};
function performanceStatus(time=animeCine?.elapsed||0){
  const t=storyNumber(time,0,0,storyTimeline().duration),model=performanceModel();
  return {schema:PERFORMANCE_SCHEMA,enabled:model.enabled,editable:storyEditable(),time:t,clipCount:model.clips.length,
    active:performanceActive(t).map(({id,character,action,label,weight})=>({id,character,action,label,weight})),
    dialogue:model.enabled&&model.limitDialogue?performanceDialogue(t):null};
}
window.SWYRL_ENGINE_PERFORMANCE=Object.freeze({
  model:()=>storyCopy(performanceModel()),upsert:value=>performanceUpsert(value),remove:id=>performanceRemove(id),
  configure:value=>performanceConfigure(value),sample:(character,part,time)=>performanceIsProject()?performanceSample(character,part,time):null,
  status:time=>performanceStatus(time)
});
