// Project-owned paper-puppet posing. Global story tracks still position the cast.
const RIG_SCHEMA='anime-character-rigs-v1';
const RIG_CHARACTERS=Object.freeze(['kami','swyrlz']);
const RIG_JOINT_LABELS=Object.freeze({
  torso:'Torso',pelvis:'Pelvis',head:'Head',cape:'Cape',
  leftUpperArm:'Left upper arm',leftForearm:'Left forearm',leftHand:'Left hand',
  rightUpperArm:'Right upper arm',rightForearm:'Right forearm',rightHand:'Right hand',
  leftUpperLeg:'Left upper leg',leftLowerLeg:'Left lower leg',leftFoot:'Left foot',
  rightUpperLeg:'Right upper leg',rightLowerLeg:'Right lower leg',rightFoot:'Right foot',
  staff:'Staff',quill:'Quill',grimoire:'Grimoire'
});
const RIG_JOINT_IDS=Object.freeze(Object.keys(RIG_JOINT_LABELS));
const RIG_PART_IDS=new Set([...RIG_JOINT_IDS,'face']);
const RIG_JOINT_BOUNDS=Object.freeze({rotationX:[-.7,.7],rotationY:[-.8,.8],rotationZ:[-1.3,1.3],depth:[-.3,.65]});
const RIG_FACE_BOUNDS=Object.freeze({blink:[0,1],mouth:[0,1],smile:[-1,1],brow:[-1,1],gazeX:[-1,1],gazeY:[-1,1]});
const RIG_EXPRESSIONS=Object.freeze([
  {id:'neutral',label:'Neutral'},{id:'happy',label:'Happy'},{id:'determined',label:'Determined'},
  {id:'surprised',label:'Surprised'},{id:'sad',label:'Sad'}
]);
const RIG_EXPRESSION_IDS=new Set(RIG_EXPRESSIONS.map(expression=>expression.id));
let rigValidatedProject=null,rigValidatedModel=null;
function rigObject(value){return value&&typeof value==='object'&&!Array.isArray(value)?value:{};}
function rigCharacterId(character){return RIG_CHARACTERS.includes(character)?character:null;}
function rigPartBounds(part){return part==='face'?RIG_FACE_BOUNDS:RIG_JOINT_BOUNDS;}
function rigDefaultKey(part,time=0){
  const key={time,ease:'smooth'};
  for(const field of Object.keys(rigPartBounds(part)))key[field]=0;
  if(part==='face'){key.expression='neutral';key.speech=false;}
  return key;
}
function rigCleanKey(part,value,duration){
  const raw=rigObject(value),key=rigDefaultKey(part,storyTime(raw.time,duration));
  for(const [field,[low,high]] of Object.entries(rigPartBounds(part)))
    key[field]=storyNumber(raw[field],0,low,high);
  key.ease=STORY_EASES.has(raw.ease)?raw.ease:'smooth';
  if(part==='face'){
    key.expression=RIG_EXPRESSION_IDS.has(raw.expression)?raw.expression:'neutral';
    key.speech=typeof raw.speech==='boolean'?raw.speech:false;
  }
  return key;
}
function rigCleanKeys(part,value,duration){
  const unique=new Map();
  for(const raw of Array.isArray(value)?value.slice(0,256):[]){
    if(!raw||typeof raw!=='object'||Array.isArray(raw))continue;
    const key=rigCleanKey(part,raw,duration);unique.set(key.time,key);
  }
  let keys=[...unique.values()].sort((a,b)=>a.time-b.time);
  if(!keys.length)keys=[rigDefaultKey(part,0)];
  if(keys[0].time!==0)keys.unshift({...keys[0],time:0});
  if(keys.at(-1).time!==duration)keys.push({...keys.at(-1),time:duration});
  // Endpoints count toward the limit, including when importing malformed data.
  if(keys.length>256)keys=[keys[0],...keys.slice(1,-1).slice(0,254),keys.at(-1)];
  return keys;
}
function rigSanitizeModel(value,duration=storyTimeline().duration){
  const raw=rigObject(value),characters=rigObject(raw.characters),result={schema:RIG_SCHEMA,characters:{}};
  for(const character of RIG_CHARACTERS){
    const input=rigObject(characters[character]),joints=rigObject(input.joints),atlas='assets/anime/'+character+'-rig.png';
    result.characters[character]={
      enabled:typeof input.enabled==='boolean'?input.enabled:true,
      asset:storyAssetSource(input.asset,atlas),
      thickness:storyNumber(input.thickness,.08,.02,.18),depth:storyNumber(input.depth,1,.3,1.5),
      joints:Object.fromEntries(RIG_JOINT_IDS.map(part=>[part,rigCleanKeys(part,joints[part],duration)])),
      face:rigCleanKeys('face',input.face,duration)
    };
  }
  return result;
}
function rigModel(){
  if(!currentProject)return rigSanitizeModel({});
  if(rigValidatedProject!==currentProject||rigValidatedModel!==currentProject.animeRigs){
    currentProject.animeRigs=rigSanitizeModel(currentProject.animeRigs);
    rigValidatedProject=currentProject;rigValidatedModel=currentProject.animeRigs;
  }
  return currentProject.animeRigs;
}
function rigKeys(character,part){
  if(!rigCharacterId(character)||!RIG_PART_IDS.has(part))return null;
  const config=rigModel().characters[character];return part==='face'?config.face:config.joints[part];
}
function rigSample(character,part,time){
  const keys=rigKeys(character,part);if(!keys)return null;
  const duration=storyTimeline().duration,t=storyNumber(time,0,0,duration);
  let low=0,high=keys.length-1;
  while(low+1<high){const middle=(low+high)>>1;if(keys[middle].time<=t)low=middle;else high=middle;}
  if(t>=keys[high].time)return {...keys[high],time:t};
  const a=keys[low],b=keys[high],fraction=(t-a.time)/Math.max(b.time-a.time,1e-9);
  const u=a.ease==='hold'?0:a.ease==='linear'?fraction:fraction*fraction*(3-2*fraction);
  const sample={time:t,ease:a.ease};
  for(const field of Object.keys(rigPartBounds(part)))sample[field]=a[field]+(b[field]-a[field])*u;
  if(part==='face'){sample.expression=a.expression;sample.speech=a.speech;}
  return sample;
}
function rigNotify(){
  if(typeof rigRefreshStage==='function')rigRefreshStage();
  if(typeof rigEditorSync==='function')rigEditorSync();
}
function rigMutate(label,callback,rebuild=false){
  if(!storyEditable()||typeof callback!=='function')return false;
  const previous=rigModel(),draft=storyCopy(previous);
  if(callback(draft)===false)return false;
  const next=rigSanitizeModel(draft);
  if(JSON.stringify(next)===JSON.stringify(previous))return true;
  const message=storyText(label,'Edit character pose',100);
  beginTransaction(message);
  currentProject.animeRigs=next;rigValidatedProject=currentProject;rigValidatedModel=next;
  if(rebuild&&typeof rigRefreshNativeActors==='function')rigRefreshNativeActors();
  commitTransaction(message);rigNotify();return true;
}
function rigUpsertKey(character,part,key){
  if(!rigCharacterId(character)||!RIG_PART_IDS.has(part)||!key||typeof key!=='object'||Array.isArray(key))return false;
  return rigMutate('Pose key · '+character+' · '+part,draft=>{
    const duration=storyTimeline().duration,time=storyTime(key.time,duration),config=draft.characters[character];
    const keys=part==='face'?config.face:config.joints[part],index=keys.findIndex(item=>Math.abs(item.time-time)<1e-6);
    const previous=index>=0?keys[index]:rigSample(character,part,time);
    const next=rigCleanKey(part,{...previous,...key,time},duration);
    if(index>=0)keys[index]=next;else if(keys.length<256)keys.push(next);else return false;
  });
}
function rigRemoveKey(character,part,time){
  if(!rigCharacterId(character)||!RIG_PART_IDS.has(part))return false;
  const duration=storyTimeline().duration,t=storyTime(time,duration);
  if(t===0||t===duration)return false;
  return rigMutate('Delete pose key · '+character+' · '+part,draft=>{
    const config=draft.characters[character],keys=part==='face'?config.face:config.joints[part];
    const index=keys.findIndex(key=>Math.abs(key.time-t)<1e-6);if(index<0)return false;
    keys.splice(index,1);
  });
}
function rigConfigure(character,value){
  if(!rigCharacterId(character)||!value||typeof value!=='object'||Array.isArray(value))return false;
  return rigMutate('Character depth · '+character,draft=>{
    const config=draft.characters[character];
    if(Object.hasOwn(value,'enabled'))config.enabled=typeof value.enabled==='boolean'?value.enabled:config.enabled;
    if(Object.hasOwn(value,'asset'))config.asset=storyAssetSource(value.asset,config.asset);
    if(Object.hasOwn(value,'thickness'))config.thickness=storyNumber(value.thickness,config.thickness,.02,.18);
    if(Object.hasOwn(value,'depth'))config.depth=storyNumber(value.depth,config.depth,.3,1.5);
  },true);
}
function rigSetArtworkMode(character,asset){
  if(!rigCharacterId(character)||!currentProject)return false;
  const model=storyCopy(rigModel()),config=model.characters[character];
  if(asset!==config.asset)config.enabled=false;
  currentProject.animeRigs=model;rigValidatedProject=currentProject;rigValidatedModel=model;
  return true;
}
function rigPublicModel(character){
  if(!rigCharacterId(character))return null;
  const config=storyCopy(rigModel().characters[character]);
  return {enabled:config.enabled,asset:config.asset,thickness:config.thickness,depth:config.depth,
    parts:RIG_JOINT_IDS.filter(part=>character==='kami'?part!=='grimoire':part!=='staff'&&part!=='quill')
      .map(id=>({id,label:RIG_JOINT_LABELS[id],bounds:storyCopy(RIG_JOINT_BOUNDS)})),
    expressions:storyCopy(RIG_EXPRESSIONS),tracks:{...config.joints,face:config.face}};
}
const rigApplyProjectMeta=applyProjectMeta,rigStoryNotify=storyNotify;
applyProjectMeta=function(meta={}){
  const result=rigApplyProjectMeta(meta);
  rigValidatedProject=null;rigValidatedModel=null;
  if(currentProject&&(currentProject.canonicalId==='ghosts-different-forms-ep01'||meta?.animeRigs)){
    currentProject.animeRigs=rigSanitizeModel(meta?.animeRigs);
    rigValidatedProject=currentProject;rigValidatedModel=currentProject.animeRigs;
  }
  if(typeof rigEditorSync==='function')rigEditorSync();return result;
};
storyNotify=function(){rigStoryNotify();if(typeof rigEditorSync==='function')rigEditorSync();};
const rigStorySetDuration=storySetDuration;
storySetDuration=function(value){
  const number=Number(value);if(!Number.isFinite(number)||number<1||number>3600)return false;
  if(!storyEditable())return rigStorySetDuration(value);
  const timeline=storyCopy(storyTimeline()),poses=storyCopy(rigModel()),ratio=number/timeline.duration;
  if(ratio===1)return true;
  for(const keys of Object.values(timeline.tracks))for(const key of keys)key.time*=ratio;
  for(const beat of timeline.beats){beat.time*=ratio;beat.end*=ratio;for(const cue of beat.cues)cue.time*=ratio;}
  for(const config of Object.values(poses.characters)){
    for(const keys of [...Object.values(config.joints),config.face])for(const key of keys)key.time*=ratio;
  }
  timeline.duration=number;
  const nextTimeline=storySanitizeTimeline(timeline),nextPoses=rigSanitizeModel(poses,number);
  // Both animation models belong to one edit, so Undo restores both together.
  beginTransaction('Episode duration');
  currentProject.animeTimeline=nextTimeline;storyValidatedProject=currentProject;storyValidatedModel=nextTimeline;
  currentProject.animeRigs=nextPoses;rigValidatedProject=currentProject;rigValidatedModel=nextPoses;
  if(typeof storySyncStoryStations==='function')storySyncStoryStations();
  commitTransaction('Episode duration');storyNotify();rigNotify();return true;
};
window.SWYRL_ENGINE_RIG=Object.freeze({
  model:character=>rigPublicModel(character),sample:(character,part,time)=>rigSample(character,part,time),
  upsertKey:(character,part,key)=>rigUpsertKey(character,part,key),
  removeKey:(character,part,time)=>rigRemoveKey(character,part,time),
  configure:(character,config)=>rigConfigure(character,config)
});
