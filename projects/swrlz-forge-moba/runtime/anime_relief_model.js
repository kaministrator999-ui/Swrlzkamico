// Three saved relief sections keep the painted costumes on their original rig.
// The atlas and animation tracks remain immutable when piece depth is edited.
const RELIEF_SCHEMA='anime-character-relief-v1';
const RELIEF_SECTION_IDS=Object.freeze(['left','center','right']);
const RELIEF_BOUNDS=Object.freeze({left:[0,.3],center:[0,.3],right:[0,.3],thickness:[.02,.18],flex:[0,1]});
let reliefValidatedProject=null,reliefValidatedModel=null;
function reliefDefaultPart(part,character){
  const thickness=rigCharacterId(character)?rigModel().characters[character].thickness:.08;
  const cloth=part==='cape'||part==='pelvis',body=part==='torso';
  const armor=/UpperArm|Forearm|UpperLeg|LowerLeg/.test(part);
  if(cloth)return {left:.045,center:.085,right:.055,thickness,flex:.65};
  if(body)return {left:.035,center:.075,right:.045,thickness,flex:.28};
  if(armor)return {left:.025,center:.05,right:.032,thickness,flex:.12};
  if(part==='head')return {left:.015,center:.028,right:.018,thickness,flex:0};
  if(/Hand/.test(part))return {left:.008,center:.015,right:.01,thickness,flex:0};
  return {left:.018,center:.03,right:.022,thickness,flex:part==='grimoire'?.08:0};
}
function reliefCleanPart(part,value,character){
  const input=rigObject(value),defaults=reliefDefaultPart(part,character);
  return Object.fromEntries(Object.entries(RELIEF_BOUNDS).map(([field,[low,high]])=>
    [field,storyNumber(input[field],defaults[field],low,high)]));
}
function reliefSanitizeModel(value){
  const raw=rigObject(value),characters=rigObject(raw.characters);
  return {schema:RELIEF_SCHEMA,characters:Object.fromEntries(RIG_CHARACTERS.map(character=>{
    const parts=rigObject(rigObject(characters[character]).parts);
    return [character,{parts:Object.fromEntries(RIG_JOINT_IDS.map(part=>[part,reliefCleanPart(part,parts[part],character)]))}];
  }))};
}
function reliefModel(){
  if(!currentProject)return reliefSanitizeModel({});
  if(reliefValidatedProject!==currentProject||reliefValidatedModel!==currentProject.animeRelief){
    currentProject.animeRelief=reliefSanitizeModel(currentProject.animeRelief);
    reliefValidatedProject=currentProject;reliefValidatedModel=currentProject.animeRelief;
  }
  return currentProject.animeRelief;
}
function reliefNotify(){
  if(typeof rigRefreshStage==='function')rigRefreshStage();
  if(typeof reliefEditorSync==='function')reliefEditorSync();
}
function reliefMutate(label,callback){
  if(!storyEditable()||typeof callback!=='function')return false;
  const previous=reliefModel(),draft=storyCopy(previous);
  if(callback(draft)===false)return false;
  const next=reliefSanitizeModel(draft);
  if(JSON.stringify(next)===JSON.stringify(previous))return true;
  beginTransaction(label);currentProject.animeRelief=next;
  reliefValidatedProject=currentProject;reliefValidatedModel=next;
  if(typeof rigRefreshNativeActors==='function')rigRefreshNativeActors();
  commitTransaction(label);reliefNotify();return true;
}
function reliefConfigure(character,part,value){
  if(!rigCharacterId(character)||!RIG_JOINT_IDS.includes(part)||!value||typeof value!=='object'||Array.isArray(value))return false;
  if(!Object.keys(RELIEF_BOUNDS).every(field=>!Object.hasOwn(value,field)||Number.isFinite(Number(value[field]))))return false;
  return reliefMutate('Piece depth sections · '+character+' · '+part,draft=>{
    const previous=draft.characters[character].parts[part];
    draft.characters[character].parts[part]=reliefCleanPart(part,{...previous,...value},character);
  });
}
function reliefReset(character,part){
  if(!rigCharacterId(character)||!RIG_JOINT_IDS.includes(part))return false;
  return reliefMutate('Reset piece depth sections · '+character+' · '+part,draft=>{
    draft.characters[character].parts[part]=reliefDefaultPart(part,character);
  });
}
function reliefPublicModel(character){
  if(character!==undefined&&!rigCharacterId(character))return null;
  const model=reliefModel();
  return character===undefined?storyCopy(model):{schema:RELIEF_SCHEMA,...storyCopy(model.characters[character]),bounds:storyCopy(RELIEF_BOUNDS)};
}
const reliefPreviousProjectMeta=applyProjectMeta,reliefPreviousNotify=storyNotify;
applyProjectMeta=function(meta={}){
  const result=reliefPreviousProjectMeta(meta);reliefValidatedProject=null;reliefValidatedModel=null;
  if(currentProject&&(currentProject.canonicalId==='ghosts-different-forms-ep01'||meta?.animeRelief)){
    currentProject.animeRelief=reliefSanitizeModel(meta?.animeRelief);
    reliefValidatedProject=currentProject;reliefValidatedModel=currentProject.animeRelief;
  }
  if(typeof reliefEditorSync==='function')reliefEditorSync();return result;
};
storyNotify=function(){const result=reliefPreviousNotify();reliefNotify();return result;};
window.SWYRL_ENGINE_RELIEF=Object.freeze({model:reliefPublicModel,configure:reliefConfigure,reset:reliefReset});
