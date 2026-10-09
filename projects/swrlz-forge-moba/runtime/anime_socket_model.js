// Saved anatomical sockets join the painted paper pieces. Socket coordinates
// are measured from each cutout's artwork centre, before its rest/pose rotation.
const SOCKET_SCHEMA='anime-rig-sockets-v1';
const SOCKET_CONNECTIONS=Object.freeze({
  pelvis:['torso','waist'],head:['torso','neck'],cape:['torso','back'],
  leftUpperArm:['torso','leftShoulder'],leftForearm:['leftUpperArm','elbow'],leftHand:['leftForearm','wrist'],
  rightUpperArm:['torso','rightShoulder'],rightForearm:['rightUpperArm','elbow'],rightHand:['rightForearm','wrist'],
  leftUpperLeg:['pelvis','leftHip'],leftLowerLeg:['leftUpperLeg','knee'],leftFoot:['leftLowerLeg','ankle'],
  rightUpperLeg:['pelvis','rightHip'],rightLowerLeg:['rightUpperLeg','knee'],rightFoot:['rightLowerLeg','ankle'],
  staff:['leftHand','grip'],quill:['rightHand','grip'],grimoire:['leftHand','book']
});
const SOCKET_TERMINALS=Object.freeze({head:'crown',cape:'hem',leftFoot:'toe',rightFoot:'toe',staff:'magic',quill:'tip',grimoire:'magic'});
const SOCKET_BOUNDS=Object.freeze({x:[-6,6],y:[-6,6],z:[-1,1]});
let socketValidatedProject=null,socketValidatedModel=null;
function socketNames(part){
  const result=Object.values(SOCKET_CONNECTIONS).filter(([parent])=>parent===part).map(([,name])=>name);
  if(SOCKET_TERMINALS[part])result.push(SOCKET_TERMINALS[part]);
  if(part==='staff')result.push('shaft');
  return [...new Set(result)];
}
function socketPoint(value,fallback={x:0,y:0,z:0}){
  const raw=rigObject(value);
  return Object.fromEntries(Object.entries(SOCKET_BOUNDS).map(([field,[low,high]])=>[field,storyNumber(raw[field],fallback[field],low,high)]));
}
function socketDefaults(character,config=rigModel().characters[character]){
  const parts={},connections={},rows=RIG_REST_ROWS[character];
  for(const [id] of rows){
    const fit=config.layout[id],sockets={};
    for(const name of socketNames(id))sockets[name]=name==='shaft'?
      {x:-2/111*fit.width,y:-87/194*fit.height,z:0}:
      {x:0,y:name==='toe'?-.1:fit.height*.42,z:0};
    parts[id]={attach:{x:-fit.artX,y:-fit.artY,z:0},sockets};
  }
  for(const [child,[parent,socket]] of Object.entries(SOCKET_CONNECTIONS)){
    const fit=config.layout[child],owner=config.layout[parent],row=rows.find(row=>row[0]===child);
    parts[parent].sockets[socket]={x:fit.x-owner.artX,y:fit.y-owner.artY,z:row[4]};
    connections[child]={parent,socket,connected:true};
  }
  return {parts,connections};
}
function socketSanitizeModel(value){
  const raw=rigObject(value),characters=rigObject(raw.characters),result={schema:SOCKET_SCHEMA,characters:{}};
  const rigs=rigModel();
  for(const character of RIG_CHARACTERS){
    const defaults=socketDefaults(character,rigs.characters[character]),input=rigObject(characters[character]),parts=rigObject(input.parts),incoming=rigObject(input.connections);
    const output={parts:{},connections:storyCopy(defaults.connections)};
    for(const id of RIG_JOINT_IDS){
      const part=rigObject(parts[id]),outgoing=rigObject(part.sockets),fallback=defaults.parts[id];
      output.parts[id]={attach:socketPoint(part.attach,fallback.attach),sockets:Object.fromEntries(
        socketNames(id).map(name=>[name,socketPoint(outgoing[name],fallback.sockets[name])]))};
    }
    for(const [child,connection] of Object.entries(output.connections)){
      const rawConnection=rigObject(incoming[child]);
      if(rawConnection.parent===connection.parent&&rawConnection.socket===connection.socket&&rawConnection.connected===false)connection.connected=false;
    }
    // A detached piece still retains its valid anatomical destination. Imported
    // parent names or cycles cannot replace this tree with a broken puppet.
    result.characters[character]=output;
  }
  return result;
}
function socketModel(){
  if(!currentProject)return socketSanitizeModel({});
  if(socketValidatedProject!==currentProject||socketValidatedModel!==currentProject.animeSockets){
    currentProject.animeSockets=socketSanitizeModel(currentProject.animeSockets);
    socketValidatedProject=currentProject;socketValidatedModel=currentProject.animeSockets;
  }
  return currentProject.animeSockets;
}
function socketNotify(){
  if(typeof rigRefreshStage==='function')rigRefreshStage();
  if(typeof socketEditorSync==='function')socketEditorSync();
}
function socketMutate(label,callback){
  if(!storyEditable()||typeof callback!=='function')return false;
  const previous=socketModel(),draft=storyCopy(previous);
  if(callback(draft)===false)return false;
  const next=socketSanitizeModel(draft);
  if(JSON.stringify(next)===JSON.stringify(previous))return true;
  beginTransaction(label);currentProject.animeSockets=next;
  socketValidatedProject=currentProject;socketValidatedModel=next;
  if(typeof rigRefreshNativeActors==='function')rigRefreshNativeActors();
  commitTransaction(label);socketNotify();return true;
}
function socketSet(character,part,name,value){
  if(!rigCharacterId(character)||!RIG_JOINT_IDS.includes(part)||
    !(name==='attach'||socketNames(part).includes(name))||!value||typeof value!=='object'||Array.isArray(value))return false;
  if(!['x','y','z'].every(field=>!Object.hasOwn(value,field)||Number.isFinite(Number(value[field]))))return false;
  return socketMutate('Limb socket · '+character+' · '+part+' · '+name,draft=>{
    const target=draft.characters[character].parts[part],previous=name==='attach'?target.attach:target.sockets[name];
    const next=socketPoint({...previous,...value},previous);
    if(name==='attach')target.attach=next;else target.sockets[name]=next;
  });
}
function socketConnect(character,child,parent,socket){
  const expected=SOCKET_CONNECTIONS[child];
  if(!rigCharacterId(character)||!expected||expected[0]!==parent||expected[1]!==socket)return false;
  return socketMutate('Snap limb · '+character+' · '+child,draft=>{
    draft.characters[character].connections[child]={parent,socket,connected:true};
  });
}
function socketDetach(character,child){
  if(!rigCharacterId(character)||!SOCKET_CONNECTIONS[child])return false;
  return socketMutate('Detach limb · '+character+' · '+child,draft=>{draft.characters[character].connections[child].connected=false;});
}
function socketReset(character,part){
  if(!rigCharacterId(character)||!RIG_JOINT_IDS.includes(part))return false;
  return socketMutate('Reset sockets · '+character+' · '+part,draft=>{
    const defaults=socketDefaults(character);draft.characters[character].parts[part]=defaults.parts[part];
    const connection=defaults.connections[part];
    if(connection){draft.characters[character].connections[part]=connection;
      draft.characters[character].parts[connection.parent].sockets[connection.socket]=defaults.parts[connection.parent].sockets[connection.socket];}
  });
}
function socketPublicModel(character){
  const model=socketModel();
  if(character!==undefined&&!rigCharacterId(character))return null;
  return character===undefined?storyCopy(model):{schema:SOCKET_SCHEMA,...storyCopy(model.characters[character]),bounds:storyCopy(SOCKET_BOUNDS)};
}
// Fitting an existing piece remains one Undo action. Its socket artwork frame
// follows art-centre changes, and Joint X/Y move the parent's outgoing socket.
rigMutate=function(label,callback,rebuild=false){
  if(!storyEditable()||typeof callback!=='function')return false;
  const previous=rigModel(),draft=storyCopy(previous),previousSockets=socketModel(),sockets=storyCopy(previousSockets);
  const previousRelief=window.SWYRL_ENGINE_RELIEF?.model?reliefModel():null,relief=previousRelief?storyCopy(previousRelief):null;
  if(callback(draft)===false)return false;
  const next=rigSanitizeModel(draft);
  if(JSON.stringify(next)===JSON.stringify(previous))return true;
  for(const character of RIG_CHARACTERS)for(const part of RIG_JOINT_IDS){
    const before=previous.characters[character].layout[part],after=next.characters[character].layout[part],own=sockets.characters[character].parts[part];
    const shaft=part==='staff'?{...own.sockets.shaft}:null;
    const dx=after.artX-before.artX,dy=after.artY-before.artY;
    if(dx||dy){own.attach.x-=dx;own.attach.y-=dy;for(const point of Object.values(own.sockets)){point.x-=dx;point.y-=dy;}}
    // The shaft mount follows actual painted ink. Artwork-centre shifts move
    // that ink; resizing scales its editable coordinate in the same Undo.
    if(shaft)own.sockets.shaft={x:shaft.x*after.width/before.width,y:shaft.y*after.height/before.height,z:shaft.z};
    const connection=SOCKET_CONNECTIONS[part];
    if(connection&&sockets.characters[character].connections[part].connected){const target=sockets.characters[character].parts[connection[0]].sockets[connection[1]];target.x+=after.x-before.x;target.y+=after.y-before.y;}
  }
  // The existing character-wide thickness control scales the independently
  // fitted costume pieces without replacing their relative thicknesses.
  if(relief)for(const character of RIG_CHARACTERS){
    const before=previous.characters[character].thickness,after=next.characters[character].thickness;
    if(before!==after)for(const config of Object.values(relief.characters[character].parts))
      config.thickness=THREE.MathUtils.clamp(config.thickness*after/before,.02,.18);
  }
  const message=storyText(label,'Edit character pose',100);beginTransaction(message);
  currentProject.animeRigs=next;rigValidatedProject=currentProject;rigValidatedModel=next;
  currentProject.animeSockets=socketSanitizeModel(sockets);socketValidatedProject=currentProject;socketValidatedModel=currentProject.animeSockets;
  if(relief){currentProject.animeRelief=reliefSanitizeModel(relief);reliefValidatedProject=currentProject;reliefValidatedModel=currentProject.animeRelief;}
  if(rebuild&&typeof rigRefreshNativeActors==='function')rigRefreshNativeActors();
  commitTransaction(message);rigNotify();socketNotify();return true;
};
const socketApplyProjectMeta=applyProjectMeta,socketStoryNotify=storyNotify;
applyProjectMeta=function(meta={}){
  const result=socketApplyProjectMeta(meta);socketValidatedProject=null;socketValidatedModel=null;
  if(currentProject&&(currentProject.canonicalId==='ghosts-different-forms-ep01'||meta?.animeSockets)){
    currentProject.animeSockets=socketSanitizeModel(meta?.animeSockets);
    socketValidatedProject=currentProject;socketValidatedModel=currentProject.animeSockets;
  }
  if(typeof socketEditorSync==='function')socketEditorSync();return result;
};
storyNotify=function(){const result=socketStoryNotify();socketNotify();return result;};
window.SWYRL_ENGINE_SOCKETS=Object.freeze({model:socketPublicModel,setSocket:socketSet,connect:socketConnect,detach:socketDetach,reset:socketReset});
