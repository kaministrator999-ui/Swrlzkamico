// §E v11.176: host UI follows the verified Chat account and the native scene.
// No Google credential, session bearer, or user email crosses the iframe.
let se176AccountConnected=false,se176LocalRows=[],se176CloudRows=[],se176RefreshEpoch=0,se176PickerSignature="";
function se176AccountState(payload){
  const connected=payload?.authenticated===true&&!!payload.user;
  se176AccountConnected=connected;
  accountText.textContent=connected?summaryName(payload.user.name||'Google account'):'Google account not connected';
  const login=document.getElementById('seChatSignIn');
  if(login){login.hidden=connected;login.disabled=connected;}
  const mark=document.getElementById('se176GoogleIcon');
  if(mark)mark.hidden=!connected;
  if(!connected){++se176RefreshEpoch;se176CloudRows=[];}
  se176PaintPicker();
}
function se176NativeName(){
  return summaryName(currentProject?.projectName||currentProject?.name)||'Untitled project';
}
function se176ActiveId(){
  try{return getProjectId();}catch{return '';}
}
function se176PaintPicker(){
  if(!cloudList)return;
  const activeId=se176ActiveId(),activeName=se176NativeName();
  const signature=JSON.stringify([activeId,activeName,se176AccountConnected,
    se176LocalRows.map(p=>[p.id,p.name]),se176CloudRows.map(p=>[p.id,p.name,p.revision])]);
  if(signature===se176PickerSignature&&cloudList.options.length)return;
  const prior=cloudList.value;
  se176PickerSignature=signature;cloudList.replaceChildren();
  const active=document.createElement('option');
  active.value='active';active.textContent='Editing now · '+activeName;
  cloudList.append(active);
  const local=se176LocalRows.filter(p=>p?.id&&p.id!==activeId);
  if(local.length){
    const group=document.createElement('optgroup');group.label='On this device';
    for(const p of local){
      const option=document.createElement('option');
      option.value='local:'+p.id;option.textContent=summaryName(p.name)||'Untitled local project';
      group.append(option);
    }
    cloudList.append(group);
  }
  if(se176AccountConnected&&se176CloudRows.length){
    const group=document.createElement('optgroup');group.label='Saved to Google account';
    for(const p of se176CloudRows){
      const option=document.createElement('option');
      option.value='cloud:'+p.id;
      option.textContent=(summaryName(p.name)||'Untitled cloud project')+' · revision '+p.revision;
      group.append(option);
    }
    cloudList.append(group);
  }
  cloudList.value=Array.from(cloudList.options).some(option=>option.value===prior)?prior:'active';
  se176UpdateLoadButton();
}
function se176UpdateLoadButton(){
  const load=document.getElementById('seChatLoad');
  if(load)load.disabled=!cloudList||cloudList.value==='active'||cloudList.value==='';
}
async function se176RefreshProjects(){
  const stamp=++se176RefreshEpoch;
  try{
    const records=await se175Read();
    if(stamp!==se176RefreshEpoch)return;
    se176LocalRows=Array.isArray(records)?records.filter(p=>p?.id&&typeof p.name==='string').sort((a,b)=>String(b.updatedAt||'').localeCompare(String(a.updatedAt||''))).slice(0,1000):[];
  }catch{
    if(stamp!==se176RefreshEpoch)return;
    se176LocalRows=[];
  }
  se176PickerSignature='';se176PaintPicker();
  if(!se176AccountConnected||!ready)return;
  try{
    const result=await rpc('cloud.list');
    if(stamp!==se176RefreshEpoch||!se176AccountConnected)return;
    se176CloudRows=Array.isArray(result.projects)?result.projects.filter(p=>p&&typeof p.id==='string'):[];
    se176PickerSignature='';se176PaintPicker();
  }catch(error){
    if(stamp!==se176RefreshEpoch)return;
    se176CloudRows=[];se176PickerSignature='';se176PaintPicker();
    setStatus('Account projects could not be listed. Your active/local project is still available.',true);
  }
}
async function se176LoadSelection(){
  if(cloudBusy||!cloudList)return;
  const choice=cloudList.value;
  if(choice.startsWith('local:')){
    const wanted=choice.slice(6),before=se176ActiveId();
    try{
      if(!se175LocalList)throw Error('LOCAL_PROJECT_LIBRARY_UNAVAILABLE');
      await se175RefreshLocal();
      se175LocalList.value=wanted;
      if(se175LocalList.value!==wanted)throw Error('LOCAL_PROJECT_NOT_FOUND');
      await se175LoadLocal();
      if(se176ActiveId()===before&&wanted!==before){setStatus('Could not load the local project. Your editor was preserved.',true);return;}
      setStatus('Opened local project · '+se176NativeName());
      await se176RefreshProjects();
    }catch(error){setStatus('Local project load failed: '+summaryName(error.message),true);}
    return;
  }
  if(choice.startsWith('cloud:')){
    // Existing loadCloud enforces dirty-state confirmation and recovery.
    await loadCloud();
    await se176RefreshProjects();
  }
}
function se176Install(){
  const row=document.querySelector('#seChatAccountPanel .se-chat-row');
  if(row&&!document.getElementById('se176GoogleIcon')){
    const icon=document.createElement('span');icon.id='se176GoogleIcon';
    icon.textContent='G';icon.hidden=true;
    icon.setAttribute('aria-label','Verified Google account');
    icon.title='Connected Google account';
    row.insertBefore(icon,accountText);
  }
  const style=document.createElement('style');
  style.textContent='#se176GoogleIcon{display:inline-grid;place-items:center;flex:0 0 24px;width:24px;height:24px;border-radius:50%;background:#fff;font:900 17px/1 system-ui;color:#4285f4;box-shadow:0 0 0 1px #aaa4}#se176GoogleIcon[hidden]{display:none!important}#seChatSignIn[hidden]{display:none!important}#seChatAccount{flex:1;min-width:90px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}#seChatProjects{min-width:0!important}';
  document.head.append(style);
  if(cloudList){
    cloudList.setAttribute('aria-label','Current editor project, local projects and Google-saved projects');
    cloudList.addEventListener('change',se176UpdateLoadButton);
  }
  document.getElementById('seChatRefresh').onclick=se176RefreshProjects;
  document.getElementById('seChatLoad').onclick=se176LoadSelection;
  se176PaintPicker();
  void se176RefreshProjects();
}