// Native character studio controls for the saved attachment/socket tree.
let socketEditorInstalled=false,socketEditorSyncing=false,socketEditorShowGuides=false;
const socketEditorParts={kami:'leftHand',swyrlz:'leftHand'};
const socketEditorNames={kami:'attach',swyrlz:'attach'};
function socketEditorGuides(character){
  return socketEditorShowGuides&&rigEditorCharacter()===character&&rigEditorEditable()&&
    !document.getElementById('storyStudioPanel')?.hidden&&
    !document.getElementById('animeScreening')?.classList.contains('open');
}
function socketEditorPreview(){rigEditorPreview();if(typeof rigRefreshStage==='function')rigRefreshStage();}
function socketEditorApply(){
  const character=rigEditorCharacter(),part=socketEditorParts[character],name=socketEditorNames[character];
  if(!character||!rigEditorEditable())return;
  const point={};for(const field of ['x','y','z']){const value=rigEditorReadNumber('socket'+field.toUpperCase());if(value===null)return;point[field]=value;}
  if(!window.SWYRL_ENGINE_SOCKETS.setSocket(character,part,name,point)){rigEditorNotice('Pause playback to save this limb socket.',true);return;}
  socketEditorPreview();rigEditorNotice('Saved '+rigEditorLabel(character)+' '+RIG_JOINT_LABELS[part]+' '+name+' socket. Connected pieces follow this joint.');
}
function socketEditorSnap(){
  const character=rigEditorCharacter(),part=socketEditorParts[character],connection=SOCKET_CONNECTIONS[part];
  if(!character||!connection||!window.SWYRL_ENGINE_SOCKETS.connect(character,part,...connection)){rigEditorNotice('Choose a connected limb and pause playback to snap it.',true);return;}
  socketEditorPreview();rigEditorNotice('Snapped '+RIG_JOINT_LABELS[part]+' to '+RIG_JOINT_LABELS[connection[0]]+' · '+connection[1]+'. The pieces rotate together from this socket.');
}
function socketEditorReset(){
  const character=rigEditorCharacter(),part=socketEditorParts[character];
  if(!character||!window.SWYRL_ENGINE_SOCKETS.reset(character,part)){rigEditorNotice('Pause playback to reset the selected sockets.',true);return;}
  socketEditorPreview();rigEditorNotice('Restored the selected piece’s fitted attachment and outgoing sockets. Pose keys are preserved.');
}
function socketEditorDetach(){
  const character=rigEditorCharacter(),part=socketEditorParts[character];
  if(!character||!window.SWYRL_ENGINE_SOCKETS.detach(character,part)){rigEditorNotice('Choose a connected piece and pause playback to detach it.',true);return;}
  socketEditorPreview();rigEditorNotice('Detached '+RIG_JOINT_LABELS[part]+'. Use Fit Body Piece to position it, then Snap to Socket to reconnect.');
}
function socketEditorRefreshControls(){
  const section=document.getElementById('storySocketSection');if(!section)return;
  const character=rigEditorCharacter();section.hidden=!character;
  if(!character)return;
  const editable=rigEditorEditable();for(const control of section.querySelectorAll('[data-socket-editable]'))control.disabled=!editable;
  document.getElementById('socketSnap').disabled=!editable||!SOCKET_CONNECTIONS[socketEditorParts[character]];
  document.getElementById('socketDetach').disabled=!editable||!SOCKET_CONNECTIONS[socketEditorParts[character]];
  document.getElementById('socketOverlay').disabled=!editable;
  for(const id of RIG_CHARACTERS){const actor=storyBoundActor(id),cast=animeCine?.cast?.[id==='kami'?'kami':'wisp'];
    for(const group of [actor,cast].filter(Boolean))if(group.userData.rig)rigUpdateSocketGuides(group);}
}
function socketEditorSync(){
  if(socketEditorSyncing||!document.getElementById('storySocketSection'))return;socketEditorSyncing=true;
  try{
    const section=document.getElementById('storySocketSection'),character=rigEditorCharacter();section.hidden=!character;if(!character)return;
    const model=window.SWYRL_ENGINE_SOCKETS.model(character),renderedParts=rigEditorModel()?.parts||[];
    if(!renderedParts.some(item=>item.id===socketEditorParts[character]))socketEditorParts[character]=renderedParts[0]?.id||'torso';
    const part=socketEditorParts[character],names=['attach',...socketNames(part)];
    if(!names.includes(socketEditorNames[character]))socketEditorNames[character]='attach';
    const picker=document.getElementById('socketPart');picker.replaceChildren();
    for(const item of renderedParts){const option=storyEditorElement('option','',item.label);option.value=item.id;picker.append(option);}picker.value=part;
    const socketPicker=document.getElementById('socketName');socketPicker.replaceChildren();
    for(const name of names){const option=storyEditorElement('option','',name==='attach'?'Incoming · attach':'Outgoing · '+name);option.value=name;socketPicker.append(option);}socketPicker.value=socketEditorNames[character];
    const connection=model.connections[part],parent=document.getElementById('socketParent'),target=document.getElementById('socketTargetSocket');parent.replaceChildren();target.replaceChildren();
    const parentOption=storyEditorElement('option','',connection?RIG_JOINT_LABELS[connection.parent]:'Book-mounted root');parentOption.value=connection?.parent||'';parent.append(parentOption);
    const targetOption=storyEditorElement('option','',connection?.socket||'Root hinge');targetOption.value=connection?.socket||'';target.append(targetOption);
    const point=socketEditorNames[character]==='attach'?model.parts[part].attach:model.parts[part].sockets[socketEditorNames[character]];
    for(const field of ['x','y','z'])document.getElementById('socket'+field.toUpperCase()).value=rigEditorNumber(point[field]);
    document.getElementById('socketOverlay').checked=socketEditorShowGuides;
    const incoming=connection?(connection.connected?'Attached to ':'Detached · destination ')+RIG_JOINT_LABELS[connection.parent]+' · '+connection.socket:'Attached to the book hinge';
    document.getElementById('socketConnection').textContent=incoming+' · incoming attach → '+(socketNames(part).join(', ')||'end')+'.';
    socketEditorRefreshControls();
  }finally{socketEditorSyncing=false;}
}
function socketEditorInstall(){
  const body=document.getElementById('storyRigSection');if(socketEditorInstalled||!body)return;socketEditorInstalled=true;
  const section=storyEditorElement('details','story-socket-section');section.id='storySocketSection';section.open=true;
  section.append(storyEditorElement('summary','','Limb Sockets · snap and rotate'));
  section.append(storyEditorElement('p','story-muted','Each painted piece has an incoming attachment and named outgoing sockets. Connected limbs stay together as they bend, turn or gain paper depth.'));
  for(const [id,label] of [['socketPart','Socket body piece'],['socketName','Attachment or outgoing socket']]){
    const row=storyEditorElement('label','story-label');row.htmlFor=id;row.append(storyEditorElement('span','',label));
    const select=storyEditorElement('select');select.id=id;select.setAttribute('aria-label',label);select.addEventListener('change',()=>{
      const character=rigEditorCharacter();if(!character)return;
      if(id==='socketPart'){socketEditorParts[character]=select.value;socketEditorNames[character]='attach';}else socketEditorNames[character]=select.value;
      socketEditorSync();});row.append(select);section.append(row);
  }
  const connection=storyEditorElement('p','story-socket-connection');connection.id='socketConnection';section.append(connection);
  const parents=storyEditorElement('div','story-key-fields');
  for(const [id,label] of [['socketParent','Connect to piece'],['socketTargetSocket','Parent socket']]){
    const row=storyEditorElement('label','story-field');row.htmlFor=id;row.append(storyEditorElement('span','',label));
    const select=storyEditorElement('select');select.id=id;select.disabled=true;select.setAttribute('aria-label',label);row.append(select);parents.append(row);
  }section.append(parents);
  const fields=storyEditorElement('div','story-key-fields');
  for(const field of ['x','y','z']){const row=rigEditorField('socket'+field.toUpperCase(),'Socket '+field.toUpperCase(),...SOCKET_BOUNDS[field]);row.querySelector('input').dataset.socketEditable='true';fields.append(row);}section.append(fields);
  section.append(storyEditorElement('p','story-muted','Coordinates use the painted piece’s centre. Incoming attach sets its rotation pivot; an outgoing socket positions its attached child.'));
  const actions=storyEditorElement('div','story-key-actions');
  for(const [id,label,callback] of [['socketApply','Apply Socket',socketEditorApply],['socketSnap','Snap to Socket',socketEditorSnap],['socketDetach','Detach Piece',socketEditorDetach],['socketReset','Reset Piece Sockets',socketEditorReset]]){
    const button=storyEditorButton(id,label,callback);button.dataset.socketEditable='true';actions.append(button);
  }section.append(actions);
  const overlayRow=storyEditorElement('label','story-field story-check');overlayRow.htmlFor='socketOverlay';overlayRow.append(storyEditorElement('span','','Show joint sockets'));
  const overlay=storyEditorElement('input');overlay.id='socketOverlay';overlay.type='checkbox';overlay.addEventListener('change',()=>{socketEditorShowGuides=overlay.checked;socketEditorRefreshControls();if(animeCine)storyRender();});overlayRow.append(overlay);section.append(overlayRow);
  body.insertBefore(section,document.getElementById('rigJointFields'));socketEditorSync();
}
const socketPreviousEditorInstall=storyEditorInstall,socketPreviousEditorSync=storyEditorSync,socketPreviousEditorRefresh=storyEditorRefreshControls;
storyEditorInstall=function(){const result=socketPreviousEditorInstall();socketEditorInstall();return result;};
storyEditorSync=function(){const result=socketPreviousEditorSync();socketEditorSync();return result;};
storyEditorRefreshControls=function(){const result=socketPreviousEditorRefresh();socketEditorRefreshControls();return result;};
window.SWYRL_ENGINE_SOCKET_EDITOR=Object.freeze({install:socketEditorInstall,sync:socketEditorSync});
