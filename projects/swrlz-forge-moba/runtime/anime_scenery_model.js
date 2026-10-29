// Independent project-owned paper scenery. The parent story tracks still stage
// the complete set; these keys pose each cutout inside its parent layer.
const SCENERY_SCHEMA='anime-scenery-v1';
const SCENERY_PARENTS=Object.freeze(['background','midground','atmosphere','effects']);
const SCENERY_ASSET='assets/anime/scenery-parts.png';
const SCENERY_BOUNDS=Object.freeze({
  x:[-30,30],y:[-30,30],z:[-30,-.1],rotationX:[-.5,.5],
  rotationY:[-.5,.5],rotationZ:[-.5,.5],
  scale:[.1,3],opacity:[0,1],unfold:[0,1]
});
// Atlas slots are row-major in its four-column/five-row image. Positions are
// parent-local; rendering protects every cutout behind both character rigs.
const SCENERY_DEFAULTS=Object.freeze([
  {id:'arches-left',label:'Left gothic arch',parent:'background',slot:0,width:11,height:15,x:-12,y:0,z:-4,parallax:.15},
  {id:'arches-center',label:'Central gothic arch',parent:'background',slot:0,width:11,height:15,x:0,y:0,z:-3,parallax:.18},
  {id:'arches-right',label:'Right gothic arch',parent:'background',slot:0,width:11,height:15,x:12,y:0,z:-4,parallax:.15},
  {id:'windows-left',label:'Left stained-glass window',parent:'background',slot:1,width:3.2,height:10,x:-7,y:2,z:-8,parallax:.1},
  {id:'windows-right',label:'Right stained-glass window',parent:'background',slot:1,width:3.2,height:10,x:7,y:2,z:-8,parallax:.1},
  {id:'castle-left',label:'Left distant castle',parent:'background',slot:13,width:12,height:14,x:-12,y:0,z:-13,parallax:.05},
  {id:'castle-center',label:'Central distant castle',parent:'background',slot:13,width:12,height:14,x:0,y:0,z:-14,parallax:.05},
  {id:'castle-right',label:'Right distant castle',parent:'background',slot:13,width:12,height:14,x:12,y:0,z:-12,parallax:.05},
  {id:'bridge',label:'Distant gothic bridge',parent:'background',slot:14,width:14,height:2.2,x:0,y:7.2,z:-6,parallax:.12},
  {id:'moon',label:'Crescent moon',parent:'background',slot:11,width:3,height:3,x:0,y:16,z:-12,parallax:.08},
  {id:'stars-far',label:'Far constellation stars',parent:'background',kind:'stars',count:70,width:44,height:25,x:0,y:0,z:-20,parallax:.05,opacity:.65},
  {id:'stars-middle',label:'Middle constellation stars',parent:'background',kind:'stars',count:70,width:44,height:25,x:0,y:0,z:-12,parallax:.18,opacity:.8},
  {id:'stars-near',label:'Near constellation stars',parent:'background',kind:'stars',count:70,width:44,height:25,x:0,y:0,z:-6,parallax:.4,opacity:.9},
  {id:'pillars-left',label:'Left carved pillar',parent:'midground',slot:2,width:1.3,height:12,x:-6.8,y:0,z:-.6,parallax:.65},
  {id:'pillars-right',label:'Right carved pillar',parent:'midground',slot:2,width:1.3,height:12,x:6.8,y:0,z:-.6,parallax:.65},
  {id:'bookcase-left',label:'Left library bookcase',parent:'midground',slot:4,width:3.5,height:10,x:-8.2,y:0,z:-1.2,parallax:.75},
  {id:'bookcase-right',label:'Right library bookcase',parent:'midground',slot:5,width:3.5,height:10,x:8.2,y:0,z:-1.2,parallax:.75},
  {id:'banner-left',label:'Left moon banner',parent:'midground',slot:3,width:1.1,height:4.2,x:-4.9,y:6.6,z:-.8,parallax:.55},
  {id:'banner-right',label:'Right moon banner',parent:'midground',slot:3,width:1.1,height:4.2,x:4.9,y:6.6,z:-.8,parallax:.55},
  {id:'lantern-left',label:'Left hanging lantern',parent:'midground',slot:6,width:.8,height:2.2,x:-5.8,y:4.5,z:-.3,parallax:.85},
  {id:'lantern-right',label:'Right hanging lantern',parent:'midground',slot:6,width:.8,height:2.2,x:5.8,y:4.5,z:-.3,parallax:.85},
  {id:'chains-left',label:'Left lantern chain',parent:'midground',slot:10,width:.22,height:3,x:-5.8,y:6.5,z:-.4,parallax:.85},
  {id:'chains-right',label:'Right lantern chain',parent:'midground',slot:10,width:.22,height:3,x:5.8,y:6.5,z:-.4,parallax:.85},
  {id:'candelabra-left',label:'Left candelabra',parent:'midground',slot:7,width:1.2,height:2.2,x:-6,y:0,z:-.4,parallax:.9},
  {id:'candelabra-right',label:'Right candelabra',parent:'midground',slot:7,width:1.2,height:2.2,x:6,y:0,z:-.4,parallax:.9},
  {id:'books-left',label:'Left loose books',parent:'midground',slot:8,width:1.6,height:1,x:-5.7,y:0,z:-.2,parallax:1},
  {id:'books-right',label:'Right loose books',parent:'midground',slot:8,width:1.6,height:1,x:5.7,y:0,z:-.2,parallax:1},
  {id:'crystal-right',label:'Golden crystal',parent:'midground',slot:9,width:.6,height:1.2,x:5.9,y:.3,z:-.1,parallax:1},
  {id:'pages',label:'Floating loose pages',parent:'atmosphere',slot:15,width:1.2,height:1.2,x:-3.5,y:4,z:-.6,parallax:.7},
  {id:'mist-left',label:'Left golden mist',parent:'atmosphere',slot:18,width:4.2,height:3.8,x:-5,y:1,z:-.5,parallax:.65,opacity:.55},
  {id:'mist-right',label:'Right golden mist',parent:'atmosphere',slot:18,width:4.2,height:3.8,x:5,y:1,z:-.5,parallax:.65,opacity:.55},
  {id:'flame-left',label:'Left gold flame',parent:'effects',slot:19,width:.5,height:1.2,x:-5,y:2,z:-.4,parallax:1},
  {id:'flame-right',label:'Right gold flame',parent:'effects',slot:19,width:.5,height:1.2,x:5,y:2,z:-.4,parallax:1},
  {id:'starornament',label:'Hanging star ornament',parent:'effects',slot:12,width:.6,height:.6,x:0,y:8,z:-2,parallax:.7}
].map(spec=>Object.freeze({...spec})));
const SCENERY_DEFAULT_BY_ID=new Map(SCENERY_DEFAULTS.map(spec=>[spec.id,spec]));
let sceneryValidatedProject=null,sceneryValidatedModel=null;
function sceneryObject(value){return value&&typeof value==='object'&&!Array.isArray(value)?value:{};}
function sceneryIsProject(){
  return !!currentProject&&(currentProject.canonicalId==='ghosts-different-forms-ep01'||currentProject.animeTimeline?.schema===STORY_SCHEMA);
}
function sceneryDefaultKey(spec,time=0){
  const key={time,ease:'smooth',visible:spec.visible!==false};
  for(const [field,[low,high]] of Object.entries(SCENERY_BOUNDS)){
    const fallback=field==='scale'||field==='opacity'||field==='unfold'?1:field==='z'?-1:0;
    key[field]=storyNumber(spec[field],fallback,low,high);
  }
  return key;
}
function sceneryCleanKey(spec,value,duration){
  const raw=sceneryObject(value),key=sceneryDefaultKey(spec,storyTime(raw.time,duration));
  for(const [field,[low,high]] of Object.entries(SCENERY_BOUNDS))
    key[field]=storyNumber(raw[field],key[field],low,high);
  key.visible=typeof raw.visible==='boolean'?raw.visible:key.visible;
  key.ease=STORY_EASES.has(raw.ease)?raw.ease:'smooth';return key;
}
function sceneryCleanKeys(spec,value,duration){
  const unique=new Map();
  for(const raw of Array.isArray(value)?value.slice(0,128):[]){
    if(!raw||typeof raw!=='object'||Array.isArray(raw))continue;
    const key=sceneryCleanKey(spec,raw,duration);unique.set(key.time,key);
  }
  let keys=[...unique.values()].sort((a,b)=>a.time-b.time);
  if(!keys.length)keys=[sceneryDefaultKey(spec,0)];
  if(keys[0].time!==0)keys.unshift({...keys[0],time:0});
  if(keys.at(-1).time!==duration)keys.push({...keys.at(-1),time:duration});
  if(keys.length>128)keys=[keys[0],...keys.slice(1,-1).slice(0,126),keys.at(-1)];
  return keys;
}
function scenerySanitizeModel(value,duration=storyTimeline().duration){
  duration=storyNumber(duration,134,1,3600);
  const raw=sceneryObject(value),objects=sceneryObject(raw.objects);
  const result={schema:SCENERY_SCHEMA,enabled:typeof raw.enabled==='boolean'?raw.enabled:true,
    depth:storyNumber(raw.depth,1,.3,1.5),objects:{}};
  for(const spec of SCENERY_DEFAULTS){
    const input=sceneryObject(objects[spec.id]);
    const object={id:spec.id,label:storyText(input.label,spec.label,100),
      parent:SCENERY_PARENTS.includes(input.parent)?input.parent:spec.parent,
      asset:storyAssetSource(input.asset,SCENERY_ASSET),
      width:storyNumber(input.width,spec.width,.25,60),height:storyNumber(input.height,spec.height,.25,32),
      thickness:storyNumber(input.thickness,spec.thickness??.04,.02,.12),
      parallax:storyNumber(input.parallax,spec.parallax??.5,.05,1),
      keys:sceneryCleanKeys(spec,input.keys,duration)};
    if(spec.kind==='stars'){object.kind='stars';object.count=spec.count;}
    else object.slot=Math.round(storyNumber(input.slot,spec.slot,0,19));
    result.objects[spec.id]=object;
  }
  return result;
}
function sceneryModel(){
  // Opening Embervault or Starforge must not attach anime project metadata.
  if(!sceneryIsProject())return scenerySanitizeModel({});
  if(sceneryValidatedProject!==currentProject||sceneryValidatedModel!==currentProject.animeScenery){
    currentProject.animeScenery=scenerySanitizeModel(currentProject.animeScenery);
    sceneryValidatedProject=currentProject;sceneryValidatedModel=currentProject.animeScenery;
  }
  return currentProject.animeScenery;
}
function scenerySample(id,time){
  if(!SCENERY_DEFAULT_BY_ID.has(id))return null;
  const keys=sceneryModel().objects[id].keys,t=storyNumber(time,0,0,storyTimeline().duration);
  let low=0,high=keys.length-1;
  while(low+1<high){const middle=(low+high)>>1;if(keys[middle].time<=t)low=middle;else high=middle;}
  if(t>=keys[high].time)return {...keys[high],time:t};
  const a=keys[low],b=keys[high],fraction=(t-a.time)/Math.max(b.time-a.time,1e-9);
  const u=a.ease==='hold'?0:a.ease==='linear'?fraction:fraction*fraction*(3-2*fraction),sample={time:t,ease:a.ease,visible:a.visible};
  for(const field of Object.keys(SCENERY_BOUNDS))sample[field]=a[field]+(b[field]-a[field])*u;
  return sample;
}
function sceneryNotify(){
  if(typeof sceneryRefreshStage==='function')sceneryRefreshStage();
  storyNotify();
}
function sceneryMutate(label,callback,rebuild=false){
  if(!storyEditable()||!sceneryIsProject()||typeof callback!=='function')return false;
  const previous=sceneryModel(),draft=storyCopy(previous);
  if(callback(draft)===false)return false;
  const next=scenerySanitizeModel(draft);
  if(JSON.stringify(next)===JSON.stringify(previous))return true;
  const message=storyText(label,'Edit paper scenery',100);beginTransaction(message);
  currentProject.animeScenery=next;sceneryValidatedProject=currentProject;sceneryValidatedModel=next;
  if(rebuild&&typeof sceneryRefreshNativeActors==='function')sceneryRefreshNativeActors();
  commitTransaction(message);sceneryNotify();return true;
}
function sceneryUpsertKey(id,key){
  const spec=SCENERY_DEFAULT_BY_ID.get(id);
  if(!spec||!key||typeof key!=='object'||Array.isArray(key))return false;
  return sceneryMutate('Scenery key · '+spec.label,draft=>{
    const duration=storyTimeline().duration,time=storyTime(key.time,duration),keys=draft.objects[id].keys;
    const index=keys.findIndex(item=>Math.abs(item.time-time)<1e-6);
    const previous=index>=0?keys[index]:scenerySample(id,time);
    const next=sceneryCleanKey(spec,{...previous,...key,time},duration);
    if(index>=0)keys[index]=next;else if(keys.length<128)keys.push(next);else return false;
  });
}
function sceneryRemoveKey(id,time){
  const spec=SCENERY_DEFAULT_BY_ID.get(id);if(!spec)return false;
  const t=storyTime(time,storyTimeline().duration);if(t===0||t===storyTimeline().duration)return false;
  return sceneryMutate('Delete scenery key · '+spec.label,draft=>{
    const keys=draft.objects[id].keys,index=keys.findIndex(key=>Math.abs(key.time-t)<1e-6);
    if(index<0)return false;keys.splice(index,1);
  });
}
function sceneryConfigure(value){
  if(!value||typeof value!=='object'||Array.isArray(value))return false;
  return sceneryMutate('Paper scenery depth',draft=>{
    if(Object.hasOwn(value,'enabled'))draft.enabled=typeof value.enabled==='boolean'?value.enabled:draft.enabled;
    if(Object.hasOwn(value,'depth'))draft.depth=storyNumber(value.depth,draft.depth,.3,1.5);
  },true);
}
const sceneryApplyProjectMeta=applyProjectMeta,sceneryStoryNotify=storyNotify;
applyProjectMeta=function(meta={}){
  const result=sceneryApplyProjectMeta(meta);sceneryValidatedProject=null;sceneryValidatedModel=null;
  if(sceneryIsProject()){
    currentProject.animeScenery=scenerySanitizeModel(meta?.animeScenery);
    sceneryValidatedProject=currentProject;sceneryValidatedModel=currentProject.animeScenery;
  }
  if(typeof sceneryEditorSync==='function')sceneryEditorSync();return result;
};
storyNotify=function(){sceneryStoryNotify();if(typeof sceneryEditorSync==='function')sceneryEditorSync();};
const sceneryStorySetDuration=storySetDuration;
storySetDuration=function(value){
  const number=Number(value);if(!Number.isFinite(number)||number<1||number>3600)return false;
  if(!storyEditable()||!sceneryIsProject())return sceneryStorySetDuration(value);
  const timeline=storyCopy(storyTimeline()),poses=storyCopy(rigModel()),scenery=storyCopy(sceneryModel());
  const ratio=number/timeline.duration;if(ratio===1)return true;
  for(const keys of Object.values(timeline.tracks))for(const key of keys)key.time*=ratio;
  for(const beat of timeline.beats){beat.time*=ratio;beat.end*=ratio;for(const cue of beat.cues)cue.time*=ratio;}
  for(const config of Object.values(poses.characters))
    for(const keys of [...Object.values(config.joints),config.face])for(const key of keys)key.time*=ratio;
  for(const object of Object.values(scenery.objects))for(const key of object.keys)key.time*=ratio;
  timeline.duration=number;
  const nextTimeline=storySanitizeTimeline(timeline),nextPoses=rigSanitizeModel(poses,number),nextScenery=scenerySanitizeModel(scenery,number);
  // Shot, character, and scenery time scaling is one native edit, so a single
  // Undo restores all three models and their endpoint keys together.
  beginTransaction('Episode duration');
  currentProject.animeTimeline=nextTimeline;storyValidatedProject=currentProject;storyValidatedModel=nextTimeline;
  currentProject.animeRigs=nextPoses;rigValidatedProject=currentProject;rigValidatedModel=nextPoses;
  currentProject.animeScenery=nextScenery;sceneryValidatedProject=currentProject;sceneryValidatedModel=nextScenery;
  if(typeof storySyncStoryStations==='function')storySyncStoryStations();
  commitTransaction('Episode duration');rigNotify();sceneryNotify();return true;
};
window.SWYRL_ENGINE_SCENERY=Object.freeze({
  model:()=>storyCopy(sceneryModel()),sample:(id,time)=>scenerySample(id,time),
  upsertKey:(id,key)=>sceneryUpsertKey(id,key),removeKey:(id,time)=>sceneryRemoveKey(id,time),
  configure:config=>sceneryConfigure(config)
});
