// Articulated paper puppets share Animation Studio's playhead and project history.
let rigEditorInstalled = false;
let rigEditorSyncing = false;
const rigEditorParts = {kami:'head',swyrlz:'head'};
const RIG_EDITOR_DEGREES = 180 / Math.PI;
const RIG_EDITOR_JOINT_FIELDS = Object.freeze([
  ['rotationX','rigRotationX','Lean X (°)'], ['rotationY','rigRotationY','Turn Y (°)'],
  ['rotationZ','rigRotationZ','Bend Z (°)'], ['depth','rigDepth','Part depth']
]);
const RIG_EDITOR_FACE_FIELDS = Object.freeze([
  ['blink','rigBlink','Blink · 0 open, 1 closed',0,1],
  ['mouth','rigMouth','Mouth openness',0,1],
  ['smile','rigSmile','Smile',-1,1], ['brow','rigBrow','Brow expression',-1,1],
  ['gazeX','rigGazeX','Look left / right',-1,1], ['gazeY','rigGazeY','Look down / up',-1,1]
]);
function rigEditorAPI(){return window.SWYRL_ENGINE_RIG;}
function rigEditorCharacter(){return storyEditorTrack==='kami'||storyEditorTrack==='swyrlz'?storyEditorTrack:null;}
function rigEditorModel(){const character=rigEditorCharacter();return character?rigEditorAPI()?.model?.(character):null;}
function rigEditorTime(){return Math.max(0,Number(storyEditorTime)||0);}
function rigEditorLabel(character){return character==='kami'?'Kami':'§wyrlz';}
function rigEditorNotice(message,error=false){storyEditorNotify(message,error);}
function rigEditorEditable(){return !!storyEditorState().editable;}
function rigEditorNumber(value){return String(Number(Number(value||0).toFixed(6)));}
function rigEditorField(id,label,low,high){
  const row=storyEditorElement('label','story-field');row.htmlFor=id;
  row.append(storyEditorElement('span','',label));
  const input=storyEditorElement('input');input.id=id;input.type='number';input.step='any';
  input.inputMode='decimal';input.required=true;input.dataset.rigEditable='true';
  if(Number.isFinite(low))input.min=String(low);if(Number.isFinite(high))input.max=String(high);
  input.setAttribute('aria-label',label);row.append(input);return row;
}
function rigEditorReadNumber(id){
  const input=document.getElementById(id);
  if(!input||input.value.trim()===''||!Number.isFinite(Number(input.value))||!input.checkValidity()){
    input?.reportValidity();rigEditorNotice('Enter a valid value for '+(input?.getAttribute('aria-label')||'this part')+'.',true);return null;
  }
  return Number(input.value);
}
function rigEditorPreview(){
  if(typeof storyEditorPreviewFrame==='function')storyEditorPreviewFrame();
  else if(typeof storyRender==='function')storyRender();
  rigEditorSync();
}
function rigEditorSaveKey(){
  if(!rigEditorEditable()){rigEditorNotice('Pause playback to edit a character pose.',true);return;}
  const character=rigEditorCharacter(),part=rigEditorParts[character],model=rigEditorModel();
  if(!character||!model||!part)return;
  const key={time:rigEditorTime(),ease:document.getElementById('rigEase').value};
  if(part==='face'){
    key.expression=document.getElementById('rigExpression').value;
    key.speech=document.getElementById('rigSpeech').checked;
    for(const [field,id] of RIG_EDITOR_FACE_FIELDS){const value=rigEditorReadNumber(id);if(value===null)return;key[field]=value;}
  }else{
    for(const [field,id] of RIG_EDITOR_JOINT_FIELDS){
      const value=rigEditorReadNumber(id);if(value===null)return;
      key[field]=field==='depth'?value:value/RIG_EDITOR_DEGREES;
    }
  }
  const upsert=rigEditorAPI()?.upsertKey;
  if(typeof upsert!=='function'||upsert(character,part,key)===false){rigEditorNotice('The pose key could not be saved. Pause playback and try again.',true);return;}
  rigEditorPreview();
  const label=part==='face'?'face':model.parts?.find(item=>item.id===part)?.label||part;
  rigEditorNotice('Saved '+rigEditorLabel(character)+' '+label+' key at '+rigEditorNumber(key.time)+' seconds.');
}
function rigEditorDeleteKey(){
  if(!rigEditorEditable()){rigEditorNotice('Pause playback to delete a pose key.',true);return;}
  const character=rigEditorCharacter(),part=rigEditorParts[character];
  const remove=rigEditorAPI()?.removeKey;
  if(!character||typeof remove!=='function'||remove(character,part,rigEditorTime())===false){
    rigEditorNotice('Select an existing pose key to delete it.',true);return;
  }
  rigEditorPreview();rigEditorNotice('Character pose key deleted. The remaining keys still interpolate.');
}
function rigEditorApplyConfig(){
  if(!rigEditorEditable()){rigEditorNotice('Pause playback to change character depth.',true);return;}
  const character=rigEditorCharacter();if(!character)return;
  const thickness=rigEditorReadNumber('rigThickness'),depth=rigEditorReadNumber('rigDepthAmount');
  if(thickness===null||depth===null)return;
  const config={enabled:document.getElementById('rigEnabled').checked,thickness,depth};
  const configure=rigEditorAPI()?.configure;
  if(typeof configure!=='function'||configure(character,config)===false){rigEditorNotice('Character depth could not be saved.',true);return;}
  rigEditorPreview();rigEditorNotice('Saved '+rigEditorLabel(character)+' character depth and puppet settings.');
}
function rigEditorSelect(part){
  const character=rigEditorCharacter();if(!character)return;
  rigEditorParts[character]=part;rigEditorSync();
}
function rigEditorRefreshControls(){
  const section=document.getElementById('storyRigSection');if(!section)return;
  const character=rigEditorCharacter(),model=rigEditorModel();section.hidden=!character||!model;
  if(section.hidden)return;
  const editable=rigEditorEditable(),part=rigEditorParts[character],time=rigEditorTime();
  for(const control of section.querySelectorAll('[data-rig-editable]'))control.disabled=!editable;
  const keys=model.tracks?.[part]||[],duration=Number(storyEditorModel()?.duration)||134;
  const exact=keys.some(key=>Math.abs(Number(key.time)-time)<1e-6);
  document.getElementById('rigDeleteKey').disabled=!editable||!exact||time===0||time===duration;
  document.getElementById('rigAddKey').textContent=(exact?'Update ':'Add ')+(part==='face'?'Face Key':'Pose Key');
  document.getElementById('rigFrameMode').textContent=!editable?'Live playback · pause to pose':exact?
    (time===0||time===duration?'Opening/final pose key · update its values':'Existing character pose key'):'Interpolated pose · add a key to edit';
}
function rigEditorSync(){
  if(rigEditorSyncing||!document.getElementById('storyRigSection'))return;
  rigEditorSyncing=true;
  try{
    const section=document.getElementById('storyRigSection'),character=rigEditorCharacter(),model=rigEditorModel();
    section.hidden=!character||!model;if(section.hidden)return;
    document.getElementById('rigCharacter').textContent=rigEditorLabel(character)+' · articulated paper puppet';
    document.getElementById('rigEnabled').checked=model.enabled!==false;
    document.getElementById('rigThickness').value=rigEditorNumber(model.thickness??.08);
    document.getElementById('rigDepthAmount').value=rigEditorNumber(model.depth??.85);
    const parts=Array.isArray(model.parts)?model.parts:[];
    const selected=rigEditorParts[character];
    if(selected!=='face'&&!parts.some(part=>part.id===selected))rigEditorParts[character]=parts[0]?.id||'face';
    const part=rigEditorParts[character],picker=document.getElementById('rigPart');picker.replaceChildren();
    for(const item of parts){const option=storyEditorElement('option','',item.label||item.id);option.value=item.id;picker.append(option);}
    const faceOption=storyEditorElement('option','','Face · expression and speech');faceOption.value='face';picker.append(faceOption);picker.value=part;
    document.getElementById('rigJointFields').hidden=part==='face';document.getElementById('rigFaceFields').hidden=part!=='face';
    const sample=rigEditorAPI()?.sample?.(character,part,rigEditorTime())||{};
    const keys=model.tracks?.[part]||[],exact=keys.find(key=>Math.abs(Number(key.time)-rigEditorTime())<1e-6);
    if(part==='face'){
      const expressions=document.getElementById('rigExpression');expressions.replaceChildren();
      for(const expression of model.expressions||[]){
        const item=typeof expression==='string'?{id:expression,label:expression}:expression;
        const option=storyEditorElement('option','',item.label||item.id);option.value=item.id;expressions.append(option);
      }
      if(!expressions.children.length){const option=storyEditorElement('option','','Neutral');option.value='neutral';expressions.append(option);}
      expressions.value=sample.expression||'neutral';
      if(expressions.selectedIndex<0)expressions.selectedIndex=0;
      document.getElementById('rigSpeech').checked=sample.speech===true;
      for(const [field,id] of RIG_EDITOR_FACE_FIELDS)document.getElementById(id).value=rigEditorNumber(sample[field]??0);
    }else{
      const definition=parts.find(item=>item.id===part);
      for(const [field,id] of RIG_EDITOR_JOINT_FIELDS){
        const input=document.getElementById(id),bounds=definition?.bounds?.[field]||
          (field==='depth'?[-.3,.65]:field==='rotationX'?[-.7,.7]:field==='rotationY'?[-.8,.8]:[-1.3,1.3]);
        const multiplier=field==='depth'?1:RIG_EDITOR_DEGREES;
        input.min=String(bounds[0]*multiplier);input.max=String(bounds[1]*multiplier);
        const value=Math.max(Number(input.min),Math.min(Number(input.max),Number(sample[field]??0)*multiplier));
        // Rounding a value at a joint limit must not move it outside that limit.
        input.value=String(Math.max(Number(input.min),Math.min(Number(input.max),Number(rigEditorNumber(value)))));
      }
    }
    document.getElementById('rigEase').value=exact?.ease||sample.ease||'smooth';
    const keyList=document.getElementById('rigKeyList');keyList.replaceChildren();
    for(const key of keys){
      const button=storyEditorButton('',rigEditorNumber(key.time)+' s',()=>storyEditorSetTime(key.time),'Preview character pose at '+rigEditorNumber(key.time)+' seconds');
      button.dataset.rigKeyTime=String(key.time);button.classList.toggle('is-selected',Math.abs(Number(key.time)-rigEditorTime())<1e-6);
      button.setAttribute('aria-pressed',String(Math.abs(Number(key.time)-rigEditorTime())<1e-6));keyList.append(button);
    }
    if(!keys.length)keyList.append(storyEditorElement('span','story-muted','No pose keys yet. Add this frame.'));
    rigEditorRefreshControls();
  }finally{rigEditorSyncing=false;}
}
function rigEditorInstall(){
  const body=document.getElementById('storyStudioBody');if(rigEditorInstalled||!body)return;
  rigEditorInstalled=true;
  const section=storyEditorElement('details','story-rig-section');section.id='storyRigSection';section.open=true;section.hidden=true;
  section.append(storyEditorElement('summary','','Character Rig · limbs and face'));
  const name=storyEditorElement('p','story-rig-character');name.id='rigCharacter';section.append(name);
  const config=storyEditorElement('div','story-rig-config');
  const enabledRow=storyEditorElement('label','story-field story-check');enabledRow.htmlFor='rigEnabled';enabledRow.append(storyEditorElement('span','','Articulated puppet'));
  const enabled=storyEditorElement('input');enabled.id='rigEnabled';enabled.type='checkbox';enabled.dataset.rigEditable='true';enabledRow.append(enabled);config.append(enabledRow);
  config.append(rigEditorField('rigThickness','Paper thickness',.02,.18),rigEditorField('rigDepthAmount','Pop-out depth',.3,1.5));section.append(config);
  const apply=storyEditorButton('rigApplyConfig','Apply Character Depth',rigEditorApplyConfig);apply.dataset.rigEditable='true';section.append(apply);
  const selectRow=storyEditorElement('label','story-label');selectRow.htmlFor='rigPart';selectRow.append(storyEditorElement('span','','Body part or face'));
  const select=storyEditorElement('select');select.id='rigPart';select.setAttribute('aria-label','Select a character body part or face');select.addEventListener('change',()=>rigEditorSelect(select.value));selectRow.append(select);
  section.append(selectRow);
  const shortcuts=storyEditorElement('div','story-rig-shortcuts');
  shortcuts.append(storyEditorButton('rigEditFace','Face & Expression',()=>rigEditorSelect('face')),
    storyEditorButton('rigEditHead','Head',()=>rigEditorSelect('head')));section.append(shortcuts);
  const jointFields=storyEditorElement('div','story-key-fields story-rig-joint-fields');jointFields.id='rigJointFields';
  for(const [field,id,label] of RIG_EDITOR_JOINT_FIELDS){const row=rigEditorField(id,label);row.querySelector('input').dataset.rigField=field;jointFields.append(row);}
  section.append(jointFields);
  const jointHint=storyEditorElement('p','story-muted','Each body part bends around its own joint. Positive part depth moves that part toward the camera.');jointFields.append(jointHint);
  const faceFields=storyEditorElement('div','story-rig-face-fields');faceFields.id='rigFaceFields';faceFields.hidden=true;
  const expressionRow=storyEditorElement('label','story-label');expressionRow.htmlFor='rigExpression';expressionRow.append(storyEditorElement('span','','Facial expression'));
  const expression=storyEditorElement('select');expression.id='rigExpression';expression.dataset.rigEditable='true';expression.setAttribute('aria-label','Facial expression');expressionRow.append(expression);faceFields.append(expressionRow);
  const primaryFace=storyEditorElement('div','story-key-fields');
  for(const [field,id,label,low,high] of RIG_EDITOR_FACE_FIELDS.slice(0,2)){const row=rigEditorField(id,label,low,high);row.querySelector('input').dataset.rigField=field;primaryFace.append(row);}faceFields.append(primaryFace);
  const advanced=storyEditorElement('details','story-rig-advanced');advanced.append(storyEditorElement('summary','','Gaze, smile and dialogue motion'));
  const advancedFields=storyEditorElement('div','story-key-fields');
  for(const [field,id,label,low,high] of RIG_EDITOR_FACE_FIELDS.slice(2)){const row=rigEditorField(id,label,low,high);row.querySelector('input').dataset.rigField=field;advancedFields.append(row);}advanced.append(advancedFields);
  const speechRow=storyEditorElement('label','story-field story-check');speechRow.htmlFor='rigSpeech';speechRow.append(storyEditorElement('span','','Move mouth with saved dialogue'));
  const speech=storyEditorElement('input');speech.id='rigSpeech';speech.type='checkbox';speech.dataset.rigEditable='true';speechRow.append(speech);advanced.append(speechRow);
  faceFields.append(advanced);section.append(faceFields);
  const easeRow=storyEditorElement('label','story-label');easeRow.htmlFor='rigEase';easeRow.append(storyEditorElement('span','','Easing to next pose'));
  const ease=storyEditorElement('select');ease.id='rigEase';ease.dataset.rigEditable='true';
  for(const [value,label] of [['smooth','Smooth'],['linear','Linear'],['hold','Hold']]){const option=storyEditorElement('option','',label);option.value=value;ease.append(option);}easeRow.append(ease);section.append(easeRow);
  const actions=storyEditorElement('div','story-key-actions');
  for(const [id,label,callback] of [['rigAddKey','Add Pose Key',rigEditorSaveKey],['rigDeleteKey','Delete Pose Key',rigEditorDeleteKey]]){const button=storyEditorButton(id,label,callback);button.dataset.rigEditable='true';actions.append(button);}section.append(actions);
  const mode=storyEditorElement('p','story-muted');mode.id='rigFrameMode';section.append(mode);
  section.append(storyEditorElement('span','story-section-label','Character keys · tap to preview'));
  const keyList=storyEditorElement('div','story-key-list');keyList.id='rigKeyList';keyList.setAttribute('aria-label','Keyframes on the selected character body part or face');section.append(keyList);
  section.append(storyEditorElement('p','story-muted','The playhead above controls this pose. Character keys, depth and expressions stay in Save Project and Undo/Redo.'));
  const frameMode=document.getElementById('storyFrameMode');body.insertBefore(section,frameMode);
  rigEditorSync();
}
const rigPreviousEditorInstall=storyEditorInstall;
storyEditorInstall=function(){const result=rigPreviousEditorInstall();rigEditorInstall();return result;};
const rigPreviousEditorSync=storyEditorSync;
storyEditorSync=function(){const result=rigPreviousEditorSync();rigEditorSync();return result;};
const rigPreviousEditorRefresh=storyEditorRefreshControls;
storyEditorRefreshControls=function(){const result=rigPreviousEditorRefresh();rigEditorRefreshControls();return result;};
window.SWYRL_ENGINE_RIG_EDITOR=Object.freeze({install:rigEditorInstall,sync:rigEditorSync,selectPart:rigEditorSelect});
