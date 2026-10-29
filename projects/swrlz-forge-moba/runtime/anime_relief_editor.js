// Piece depth uses the same native selection, project history and story clock.
let reliefEditorInstalled=false,reliefEditorSyncing=false;
const reliefEditorParts={kami:'cape',swyrlz:'cape'};
function reliefEditorApply(){
  const character=rigEditorCharacter(),part=reliefEditorParts[character];
  if(!character||!rigEditorEditable())return;
  const value={};
  for(const field of Object.keys(RELIEF_BOUNDS)){
    const number=rigEditorReadNumber('relief'+field[0].toUpperCase()+field.slice(1));if(number===null)return;value[field]=number;
  }
  if(!window.SWYRL_ENGINE_RELIEF.configure(character,part,value)){rigEditorNotice('Pause playback to save piece depth sections.',true);return;}
  rigEditorPreview();rigEditorNotice('Saved '+rigEditorLabel(character)+' '+RIG_JOINT_LABELS[part]+' depth sections. Robe and armor depth follows the body’s saved poses.');
}
function reliefEditorReset(){
  const character=rigEditorCharacter(),part=reliefEditorParts[character];
  if(!character||!window.SWYRL_ENGINE_RELIEF.reset(character,part)){rigEditorNotice('Pause playback to reset piece depth.',true);return;}
  rigEditorPreview();rigEditorNotice('Restored the selected piece’s paper depth and costume flex.');
}
function reliefEditorRefreshControls(){
  const section=document.getElementById('storyReliefSection');if(!section)return;
  const character=rigEditorCharacter();section.hidden=!character;
  const editable=!!character&&rigEditorEditable();
  for(const control of section.querySelectorAll('[data-relief-editable]'))control.disabled=!editable;
}
function reliefEditorSync(){
  if(reliefEditorSyncing||!document.getElementById('storyReliefSection'))return;reliefEditorSyncing=true;
  try{
    const section=document.getElementById('storyReliefSection'),character=rigEditorCharacter();section.hidden=!character;if(!character)return;
    const rendered=rigEditorModel()?.parts||[];
    if(!rendered.some(part=>part.id===reliefEditorParts[character]))reliefEditorParts[character]=rendered[0]?.id||'torso';
    const picker=document.getElementById('reliefPart');picker.replaceChildren();
    for(const part of rendered){const option=storyEditorElement('option','',part.label);option.value=part.id;picker.append(option);}
    picker.value=reliefEditorParts[character];
    const config=window.SWYRL_ENGINE_RELIEF.model(character).parts[reliefEditorParts[character]];
    for(const field of Object.keys(RELIEF_BOUNDS))document.getElementById('relief'+field[0].toUpperCase()+field.slice(1)).value=rigEditorNumber(config[field]);
    reliefEditorRefreshControls();
  }finally{reliefEditorSyncing=false;}
}
function reliefEditorInstall(){
  const body=document.getElementById('storyRigSection');if(reliefEditorInstalled||!body)return;reliefEditorInstalled=true;
  const section=storyEditorElement('details','story-relief-section');section.id='storyReliefSection';section.open=true;
  section.append(storyEditorElement('summary','','Character Piece Depth Sections'));
  section.append(storyEditorElement('p','story-muted','Each piece has left, centre and right paper sections, a real back and cut edges. The robe and armor follow the connected body, with gentle flex as its saved poses change.'));
  const row=storyEditorElement('label','story-label');row.htmlFor='reliefPart';row.append(storyEditorElement('span','','Depth body piece'));
  const picker=storyEditorElement('select');picker.id='reliefPart';picker.setAttribute('aria-label','Depth body piece');picker.dataset.reliefEditable='true';
  picker.addEventListener('change',()=>{const character=rigEditorCharacter();if(character){reliefEditorParts[character]=picker.value;reliefEditorSync();}});row.append(picker);section.append(row);
  const fields=storyEditorElement('div','story-key-fields');
  for(const [field,label] of [['left','Depth Left'],['center','Depth Centre'],['right','Depth Right'],['thickness','Paper thickness'],['flex','Costume Flex']]){
    const item=rigEditorField('relief'+field[0].toUpperCase()+field.slice(1),label,...RELIEF_BOUNDS[field]);
    item.querySelector('input').dataset.reliefEditable='true';fields.append(item);
  }section.append(fields);
  section.append(storyEditorElement('p','story-muted','Depth leaves the joints fixed. Flex bends the lower and outer costume sections according to body movement; 0 makes the piece rigid.'));
  const actions=storyEditorElement('div','story-key-actions');
  for(const [id,label,callback] of [['reliefApply','Apply Piece Depth',reliefEditorApply],['reliefReset','Reset Piece Depth',reliefEditorReset]]){
    const button=storyEditorButton(id,label,callback);button.dataset.reliefEditable='true';actions.append(button);
  }section.append(actions);body.insertBefore(section,document.getElementById('rigJointFields'));reliefEditorSync();
}
const reliefPreviousEditorInstall=storyEditorInstall,reliefPreviousEditorSync=storyEditorSync,reliefPreviousEditorRefresh=storyEditorRefreshControls;
storyEditorInstall=function(){const result=reliefPreviousEditorInstall();reliefEditorInstall();return result;};
storyEditorSync=function(){const result=reliefPreviousEditorSync();reliefEditorSync();return result;};
storyEditorRefreshControls=function(){const result=reliefPreviousEditorRefresh();reliefEditorRefreshControls();return result;};
window.SWYRL_ENGINE_RELIEF_EDITOR=Object.freeze({install:reliefEditorInstall,sync:reliefEditorSync});
