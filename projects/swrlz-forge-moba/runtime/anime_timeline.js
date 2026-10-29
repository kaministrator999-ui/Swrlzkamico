// Native, project-owned animation data. Rendering and authoring UI share this model.
const STORY_SCHEMA = 'anime-timeline-v1';
const STORY_TRACK_NAMES = Object.freeze(['camera','kami','swyrlz','background','atmosphere','midground','effects','foreground','book']);
const STORY_EASES = new Set(['linear','smooth','hold']);
// A story camera may aim at the low book pages as well as the standing cast.
const STORY_CAMERA_BOUNDS = Object.freeze({x:[-4,4],y:[2,9],z:[9,24],tx:[-4,4],ty:[-3,6],tz:[-4,1],fov:[35,65]});
const STORY_LAYER_BOUNDS = Object.freeze({x:[-12,12],y:[-3,12],z:[-28,6],scale:[.1,2],rotation:[-Math.PI/2,Math.PI/2],opacity:[0,1],unfold:[0,1]});
const STORY_CAST_BOUNDS = Object.freeze({...STORY_LAYER_BOUNDS,x:[-4,4],y:[1,7],z:[-3,1],scale:[.25,1.4],rotation:[-.4,.4]});
const STORY_DEFAULT_VALUES = Object.freeze({
  camera:{x:0,y:4.85,z:12.8,tx:0,ty:4.2,tz:-1.7,fov:48},
  kami:{x:1.32,y:4.08,z:-.65,scale:1,rotation:0,opacity:1,visible:true,unfold:1},
  swyrlz:{x:-1.48,y:4.4,z:-.45,scale:1,rotation:0,opacity:1,visible:true,unfold:1},
  background:{x:0,y:1.9,z:-21,scale:1,rotation:0,opacity:1,visible:true,unfold:1},
  atmosphere:{x:0,y:1.9,z:-16,scale:1,rotation:0,opacity:1,visible:true,unfold:1},
  midground:{x:0,y:1.9,z:-9,scale:1,rotation:0,opacity:1,visible:true,unfold:1},
  effects:{x:0,y:1.9,z:-2.6,scale:1,rotation:0,opacity:1,visible:true,unfold:1},
  foreground:{x:0,y:.7,z:1.5,scale:1,rotation:0,opacity:1,visible:true,unfold:1},
  book:{x:0,y:.15,z:-1.85,scale:.9,rotation:0,opacity:1,visible:true,unfold:1}
});
let storyValidatedProject = null, storyValidatedModel = null;
function storyCopy(value){return JSON.parse(JSON.stringify(value));}
function storyNumber(value, fallback, low, high){
  const usable=(typeof value==='number'||typeof value==='string'&&value.trim()!=='')?Number(value):NaN;
  return Math.max(low,Math.min(high,Number.isFinite(usable)?usable:fallback));
}
function storyText(value, fallback='', limit=180){
  return typeof value==='string'?value.replace(/[\u0000-\u0008\u000b\u000c\u000e-\u001f]/g,'').slice(0,limit):fallback;
}
function storyTime(value,duration){return Math.min(duration,Math.round(storyNumber(value,0,0,duration)*1e6)/1e6);}
function storyBounds(track){return track==='camera'?STORY_CAMERA_BOUNDS:track==='kami'||track==='swyrlz'?STORY_CAST_BOUNDS:STORY_LAYER_BOUNDS;}
function storyCleanKey(track,input,duration){
  const raw=input&&typeof input==='object'&&!Array.isArray(input)?input:{},base=STORY_DEFAULT_VALUES[track],bounds=storyBounds(track);
  const key={time:storyTime(raw.time,duration)};
  for(const [field,[low,high]] of Object.entries(bounds))key[field]=storyNumber(raw[field],base[field],low,high);
  if(track!=='camera')key.visible=typeof raw.visible==='boolean'?raw.visible:true;
  key.ease=STORY_EASES.has(raw.ease)?raw.ease:'smooth';
  return key;
}
function storyDefaultTimeline(){
  const boundaries=[0,14,30,46,66,84,103,121,134];
  const names=['The Signal','Just Visiting','Ghost in Code','Build a Door','The Guardian','The Younger Dreamer','One Forge','End Credits'];
  return {schema:STORY_SCHEMA,title:'Ghosts in Different Forms · Episode 01',duration:134,
    beats:names.map((title,i)=>({time:boundaries[i],end:boundaries[i+1],title,cues:[]})),
    tracks:Object.fromEntries(STORY_TRACK_NAMES.map(track=>[track,[{time:0,...STORY_DEFAULT_VALUES[track],ease:'smooth'},
      {time:134,...STORY_DEFAULT_VALUES[track],ease:'smooth'}]]))};
}
function storySanitizeTimeline(value){
  const raw=value&&typeof value==='object'&&!Array.isArray(value)?value:{},fallback=storyDefaultTimeline();
  const duration=storyNumber(raw.duration,134,1,3600),tracks={};
  for(const track of STORY_TRACK_NAMES){
    const source=Array.isArray(raw.tracks?.[track])?raw.tracks[track].slice(0,256):fallback.tracks[track];
    const unique=new Map();
    for(const input of source){if(!input||typeof input!=='object'||Array.isArray(input))continue;
      const key=storyCleanKey(track,input,duration);unique.set(key.time,key);}
    let keys=[...unique.values()].sort((a,b)=>a.time-b.time);
    if(!keys.length)keys=[storyCleanKey(track,{time:0},duration)];
    if(keys[0].time!==0)keys.unshift({...keys[0],time:0});
    if(keys.at(-1).time!==duration)keys.push({...keys.at(-1),time:duration});
    tracks[track]=keys;
  }
  const source=Array.isArray(raw.beats)&&raw.beats.length?raw.beats.slice(0,32):fallback.beats;
  const beatMap=new Map();
  for(const item of source){
    if(!item||typeof item!=='object'||Array.isArray(item))continue;
    const time=storyTime(item.time,duration);
    if(time>=duration)continue;
    beatMap.set(time,{time,title:storyText(item.title,'Scene',180),raw:item});
  }
  let beats=[...beatMap.values()].sort((a,b)=>a.time-b.time);
  if(!beats.length)beats=[{time:0,title:'Scene 01',raw:{}}];
  // Every episode begins with a beat and has continuous, non-overlapping coverage.
  if(beats[0].time!==0)beats.unshift({time:0,title:'Opening',raw:{}});
  beats=beats.map((beat,index)=>{
    const end=index+1<beats.length?beats[index+1].time:duration,cueMap=new Map();
    for(const item of Array.isArray(beat.raw.cues)?beat.raw.cues.slice(0,64):[]){
      if(!item||typeof item!=='object'||Array.isArray(item))continue;
      const text=storyText(item.text,'',1000),time=storyNumber(item.time,beat.time,beat.time,end);
      if(text.trim())cueMap.set(time,{time,text});
    }
    return {time:beat.time,end,title:beat.title,cues:[...cueMap.values()].sort((a,b)=>a.time-b.time)};
  });
  return {schema:STORY_SCHEMA,title:storyText(raw.title,fallback.title,180),duration,beats,tracks};
}
function storyTimeline(){
  if(!currentProject||(currentProject.canonicalId!=='ghosts-different-forms-ep01'&&currentProject.animeTimeline?.schema!==STORY_SCHEMA))return storySanitizeTimeline({});
  if(storyValidatedProject!==currentProject||storyValidatedModel!==currentProject.animeTimeline){
    currentProject.animeTimeline=storySanitizeTimeline(currentProject.animeTimeline);
    storyValidatedProject=currentProject;storyValidatedModel=currentProject.animeTimeline;
  }
  return currentProject.animeTimeline;
}
function storySample(track,time){
  if(!STORY_TRACK_NAMES.includes(track))return null;
  const model=storyTimeline(),keys=model.tracks[track],t=storyNumber(time,0,0,model.duration);
  let low=0,high=keys.length-1;
  while(low+1<high){const middle=(low+high)>>1;if(keys[middle].time<=t)low=middle;else high=middle;}
  if(t>=keys[high].time)return {...keys[high],time:t};
  const a=keys[low],b=keys[high],fraction=(t-a.time)/Math.max(b.time-a.time,1e-9);
  const u=a.ease==='hold'?0:a.ease==='linear'?fraction:fraction*fraction*(3-2*fraction);
  const sample={time:t,ease:a.ease};
  for(const field of Object.keys(storyBounds(track)))sample[field]=a[field]+(b[field]-a[field])*u;
  if(track!=='camera')sample.visible=a.visible;
  return sample;
}
function storyBeat(time){
  const model=storyTimeline(),t=storyNumber(time,0,0,model.duration);
  let index=0;for(let i=1;i<model.beats.length;i++){if(model.beats[i].time>t)break;index=i;}
  const beat=model.beats[index];let cue='';
  for(const item of beat.cues){if(item.time>t)break;cue=item.text;}
  return {...beat,index,local:t-beat.time,cue};
}
function storyEditable(){
  return !!currentProject&&(currentProject.canonicalId==='ghosts-different-forms-ep01'||currentProject.animeTimeline?.schema===STORY_SCHEMA)&&(!playing||paused);
}
function storyNotify(){
  if(typeof storyEditorSync==='function')storyEditorSync();
}
function storyMutate(label,callback){
  if(!storyEditable()||typeof callback!=='function')return false;
  const original=storyTimeline(),draft=storyCopy(original);
  if(callback(draft)===false)return false;
  const next=storySanitizeTimeline(draft);
  if(JSON.stringify(next)===JSON.stringify(original))return true;
  const message=storyText(label,'Edit animation',100);
  beginTransaction(message);
  currentProject.animeTimeline=next;storyValidatedProject=currentProject;storyValidatedModel=next;
  if(typeof storySyncStoryStations==='function')storySyncStoryStations();
  commitTransaction(message);storyNotify();return true;
}
function storySetTitle(value){
  if(typeof value!=='string'||!value.trim())return false;
  return storyMutate('Episode title',draft=>{draft.title=storyText(value.trim(),'Episode 01',180);});
}
function storyUpsertKey(track,key){
  if(!STORY_TRACK_NAMES.includes(track)||!key||typeof key!=='object'||Array.isArray(key))return false;
  return storyMutate('Keyframe · '+track,draft=>{
    const time=storyTime(key.time,draft.duration),keys=draft.tracks[track],index=keys.findIndex(k=>Math.abs(k.time-time)<1e-6);
    const previous=index>=0?keys[index]:storySample(track,time);
    const next=storyCleanKey(track,{...previous,...key,time},draft.duration);
    if(index>=0)keys[index]=next;else if(keys.length<256)keys.push(next);else return false;
  });
}
function storyRemoveKey(track,time){
  if(!STORY_TRACK_NAMES.includes(track))return false;
  const model=storyTimeline(),t=storyTime(time,model.duration);
  if(t===0||t===model.duration)return false;
  return storyMutate('Delete keyframe · '+track,draft=>{
    const keys=draft.tracks[track],index=keys.findIndex(key=>Math.abs(key.time-t)<1e-6);
    if(index<0)return false;keys.splice(index,1);
  });
}
function storySetBeat(index,data){
  if(!Number.isInteger(index)||!data||typeof data!=='object'||Array.isArray(data))return false;
  return storyMutate('Edit scene '+(index+1),draft=>{
    if(index<0||index>=draft.beats.length)return false;
    const previous=draft.beats[index],next={...previous,...storyCopy(data)};
    // Editing a boundary shifts the following scene rather than introducing a gap.
    if(index===0)next.time=0;
    else if(Object.hasOwn(data,'time'))next.time=storyNumber(data.time,previous.time,draft.beats[index-1].time+.001,
      index+1<draft.beats.length?draft.beats[index+1].time-.001:draft.duration-.001);
    if(Object.hasOwn(data,'end')&&index+1<draft.beats.length){
      draft.beats[index+1].time=storyNumber(data.end,previous.end,next.time+.001,
        index+2<draft.beats.length?draft.beats[index+2].time-.001:draft.duration-.001);
    }
    draft.beats[index]=next;
  });
}
function storySetDuration(value){
  const number=Number(value);if(!Number.isFinite(number)||number<1||number>3600)return false;
  return storyMutate('Episode duration',draft=>{
    const ratio=number/draft.duration;
    for(const keys of Object.values(draft.tracks))for(const key of keys)key.time*=ratio;
    for(const beat of draft.beats){beat.time*=ratio;beat.end*=ratio;for(const cue of beat.cues)cue.time*=ratio;}
    draft.duration=number;
  });
}
function storySeek(time){
  const t=storyNumber(time,0,0,storyTimeline().duration);
  if(animeCine){
    const wasPaused=paused,result=animeSeek(t);
    if(wasPaused){paused=true;setSessionButtons();animeUpdateControls();}
    return result;
  }
  if(typeof storyPreview==='function'){storyPreview(t);return true;}
  return false;
}
function storyStatus(){
  const model=storyTimeline();
  return {active:!!animeCine,playing:!!playing,paused:!!paused,editable:storyEditable(),
    projectId:currentProject?.canonicalId||null,title:model.title,duration:model.duration,
    elapsed:animeCine?.elapsed||0,beatCount:model.beats.length,tracks:[...STORY_TRACK_NAMES],
    keyCounts:Object.fromEntries(STORY_TRACK_NAMES.map(track=>[track,model.tracks[track].length]))};
}
const storyApplyProjectMeta = applyProjectMeta;
applyProjectMeta = function(meta={}){
  const result=storyApplyProjectMeta(meta);
  storyValidatedProject=null;storyValidatedModel=null;
  if(currentProject?.canonicalId==='ghosts-different-forms-ep01'||meta.animeTimeline){
    currentProject.animeTimeline=storySanitizeTimeline(meta.animeTimeline);
    storyValidatedProject=currentProject;storyValidatedModel=currentProject.animeTimeline;
  }
  storyNotify();return result;
};
window.SWYRL_ENGINE_ANIMATION=Object.freeze({
  getTimeline:()=>storyCopy(storyTimeline()),
  upsertKey:(track,key)=>storyUpsertKey(track,key),removeKey:(track,time)=>storyRemoveKey(track,time),
  setBeat:(index,data)=>storySetBeat(index,data),setDuration:value=>storySetDuration(value),setTitle:value=>storySetTitle(value),
  serializedProject:()=>storyCopy(projectData()),seek:time=>storySeek(time),status:()=>storyStatus(),
  sample:(track,time)=>storySample(track,time)
});
