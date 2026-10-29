// Narrative cue authoring shares Animation Studio's playhead and Undo history.
let storyEffectsEditorInstalled=false,storyEffectsEditorSyncing=false,storyEffectsEditorSelection=null;
const STORY_EFFECT_EDITOR_FIELDS=Object.freeze([
  ['time','effectTime','At (seconds)',0,3600],['duration','effectDuration','Duration (seconds)',.1,3600],['strength','effectStrength','Strength',.1,2],
  ['x','effectX','Position X',-20,20],['y','effectY','Position Y',-10,24],['z','effectZ','Depth Z',-30,-.1],
  ['width','effectWidth','Width',.25,12],['height','effectHeight','Height',.25,12],['rotation','effectRotation','Turn (radians)',-Math.PI,Math.PI]
]);
function storyEffectsEditorModel(){return window.SWYRL_ENGINE_STORY_EFFECTS.model();}
function storyEffectsEditorSelected(model=storyEffectsEditorModel()){return model.cues.find(cue=>cue.id===storyEffectsEditorSelection)||null;}
function storyEffectsEditorNextId(model){let index=1;while(model.cues.some(cue=>cue.id==='story-effect-'+index))index++;return 'story-effect-'+index;}
function storyEffectsEditorField(id,label,low,high){
  const row=storyEditorElement('label','story-field');row.htmlFor=id;row.append(storyEditorElement('span','',label));
  const input=storyEditorElement('input');input.id=id;input.type='number';input.step='any';input.inputMode='decimal';input.required=true;input.min=String(low);input.max=String(high);input.dataset.effectEditable='true';input.setAttribute('aria-label',label);row.append(input);return row;
}
function storyEffectsEditorFill(cue){
  document.getElementById('effectType').value=cue.effect;document.getElementById('effectLabel').value=cue.label;
  for(const [field,id] of STORY_EFFECT_EDITOR_FIELDS)document.getElementById(id).value=String(Number(Number(cue[field]).toFixed(6)));
}
function storyEffectsEditorNew(){
  const effect=document.getElementById('effectType')?.value||'page',base=STORY_EFFECT_DEFAULTS[effect];storyEffectsEditorSelection=null;
  storyEffectsEditorFill({effect,label:base.label,time:Number(storyEditorTime)||0,duration:effect==='portal'?24:8,strength:1,x:0,y:effect==='portal'?1:5,z:-4,width:base.width,height:base.height,rotation:0});
  document.getElementById('effectCue').value='';storyEffectsEditorRefresh();storyEditorNotify('Choose the effect and its start time, then Apply Story Effect.');
}
function storyEffectsEditorSave(){
  if(!storyEditorState().editable){storyEditorNotify('Pause playback to edit a story effect.',true);return;}
  const model=storyEffectsEditorModel(),cue={id:storyEffectsEditorSelection||storyEffectsEditorNextId(model),effect:document.getElementById('effectType').value,label:document.getElementById('effectLabel').value};
  for(const [field,id] of STORY_EFFECT_EDITOR_FIELDS){const input=document.getElementById(id);if(input.value.trim()===''||!input.checkValidity()||!Number.isFinite(Number(input.value))){input.reportValidity();storyEditorNotify('Enter a valid '+input.getAttribute('aria-label')+'.',true);return;}cue[field]=Number(input.value);}
  if(cue.time>=storyTimeline().duration){storyEditorNotify('Place the effect before the end of the episode.',true);return;}
  const previous=storyEffectsEditorSelection;storyEffectsEditorSelection=cue.id;
  if(window.SWYRL_ENGINE_STORY_EFFECTS.upsert(cue)===false){storyEffectsEditorSelection=previous;storyEditorNotify('This story effect could not be saved.',true);return;}
  storyEditorPreviewFrame();storyEffectsEditorSync();storyEditorNotify('Saved '+cue.label+' at '+storyEditorNumber(cue.time)+' seconds.');
}
function storyEffectsEditorRemove(){
  if(!storyEditorState().editable||!storyEffectsEditorSelection)return;
  const id=storyEffectsEditorSelection;storyEffectsEditorSelection=null;
  if(window.SWYRL_ENGINE_STORY_EFFECTS.remove(id)===false){storyEffectsEditorSelection=id;storyEditorNotify('Select a story effect to remove it.',true);return;}
  storyEffectsEditorSync();storyEditorPreviewFrame();storyEditorNotify('Story effect removed.');
}
function storyEffectsEditorEnable(){
  if(window.SWYRL_ENGINE_STORY_EFFECTS.configure({enabled:document.getElementById('effectsEnabled').checked})===false){storyEditorNotify('Pause playback to change story effects.',true);return;}
  storyEditorPreviewFrame();storyEffectsEditorSync();storyEditorNotify('Story effects saved in this project.');
}
function storyEffectsEditorSelect(id,preview=false){
  const cue=storyEffectsEditorModel().cues.find(item=>item.id===id);if(!cue)return false;
  storyEffectsEditorSelection=id;storyEffectsEditorSync();if(preview)storyEditorSetTime(Math.min(storyTimeline().duration,cue.time+Math.min(.5,cue.duration*.1)));return true;
}
function storyEffectsEditorRefresh(){
  const section=document.getElementById('storyEffectsSection');if(!section)return;
  section.hidden=!storyEditorIsProject();if(section.hidden)return;
  const editable=storyEditorState().editable;for(const control of section.querySelectorAll('[data-effect-editable]'))control.disabled=!editable;
  document.getElementById('effectRemove').disabled=!editable||!storyEffectsEditorSelected();
  document.getElementById('effectState').textContent=!editable?'Live story effects · pause to edit':storyEffectsEditorSelection?'Edit the selected cue · each Apply is one Undo step':'New cue · choose a time and Apply';
}
function storyEffectsEditorSync(){
  if(storyEffectsEditorSyncing||!document.getElementById('storyEffectsSection'))return;storyEffectsEditorSyncing=true;
  try{
    const section=document.getElementById('storyEffectsSection');section.hidden=!storyEditorIsProject();if(section.hidden)return;
    const model=storyEffectsEditorModel();if(storyEffectsEditorSelection&&!model.cues.some(cue=>cue.id===storyEffectsEditorSelection))storyEffectsEditorSelection=null;
    document.getElementById('effectsEnabled').checked=model.enabled;const picker=document.getElementById('effectCue');picker.replaceChildren();
    const empty=storyEditorElement('option','','New story effect');empty.value='';picker.append(empty);
    for(const cue of model.cues){const option=storyEditorElement('option','',storyEditorNumber(cue.time)+' s · '+cue.label);option.value=cue.id;picker.append(option);}
    picker.value=storyEffectsEditorSelection||'';const selected=storyEffectsEditorSelected(model);if(selected)storyEffectsEditorFill(selected);
    const list=document.getElementById('effectCueList');list.replaceChildren();
    for(const cue of model.cues){const button=storyEditorButton('',storyEditorNumber(cue.time)+' s · '+cue.label,()=>storyEffectsEditorSelect(cue.id,true));button.dataset.effectCueId=cue.id;button.classList.toggle('is-selected',cue.id===storyEffectsEditorSelection);button.setAttribute('aria-pressed',String(cue.id===storyEffectsEditorSelection));list.append(button);}
    if(!model.cues.length)list.append(storyEditorElement('span','story-muted','No story effects yet. Add a cue to animate memory pages, spell ripples, written names or a folded door.'));
    for(const id of ['effectTime','effectDuration'])document.getElementById(id).max=String(storyTimeline().duration);
    storyEffectsEditorRefresh();
  }finally{storyEffectsEditorSyncing=false;}
}
function storyEffectsEditorInstall(){
  const body=document.getElementById('storyStudioBody');if(storyEffectsEditorInstalled||!body)return;storyEffectsEditorInstalled=true;
  const section=storyEditorElement('details','story-effects-section');section.id='storyEffectsSection';section.open=true;section.hidden=true;section.append(storyEditorElement('summary','','Story effects'));
  const toggle=storyEditorElement('label','story-field story-check');toggle.htmlFor='effectsEnabled';toggle.append(storyEditorElement('span','','Story effects enabled'));
  const enabled=storyEditorElement('input');enabled.id='effectsEnabled';enabled.type='checkbox';enabled.dataset.effectEditable='true';toggle.append(enabled);section.append(toggle);
  const applyEnabled=storyEditorButton('effectsApplyEnabled','Apply Effect Visibility',storyEffectsEditorEnable);applyEnabled.dataset.effectEditable='true';section.append(applyEnabled);
  const cueRow=storyEditorElement('label','story-label');cueRow.htmlFor='effectCue';cueRow.append(storyEditorElement('span','','Story cue'));const picker=storyEditorElement('select');picker.id='effectCue';picker.setAttribute('aria-label','Select a story effect');picker.addEventListener('change',()=>picker.value?storyEffectsEditorSelect(picker.value):storyEffectsEditorNew());cueRow.append(picker);section.append(cueRow);
  const typeRow=storyEditorElement('label','story-label');typeRow.htmlFor='effectType';typeRow.append(storyEditorElement('span','','Effect'));const type=storyEditorElement('select');type.id='effectType';type.dataset.effectEditable='true';
  for(const [value,label] of [['page','Floating memory page'],['burst','Broken spell ripple'],['ink','Written names and runes'],['portal','Folded memory door']]){const option=storyEditorElement('option','',label);option.value=value;type.append(option);}typeRow.append(type);section.append(typeRow);
  const labelRow=storyEditorElement('label','story-label');labelRow.htmlFor='effectLabel';labelRow.append(storyEditorElement('span','','Label / written names'));const label=storyEditorElement('input');label.id='effectLabel';label.type='text';label.maxLength=100;label.dataset.effectEditable='true';labelRow.append(label);section.append(labelRow);
  const fields=storyEditorElement('div','story-key-fields');for(const [,id,text,low,high] of STORY_EFFECT_EDITOR_FIELDS)fields.append(storyEffectsEditorField(id,text,low,high));section.append(fields);
  const actions=storyEditorElement('div','story-key-actions');for(const [id,text,handler] of [['effectNew','New Story Effect',storyEffectsEditorNew],['effectApply','Apply Story Effect',storyEffectsEditorSave],['effectRemove','Remove Story Effect',storyEffectsEditorRemove]]){const button=storyEditorButton(id,text,handler);button.dataset.effectEditable='true';actions.append(button);}section.append(actions);
  const state=storyEditorElement('p','story-muted');state.id='effectState';section.append(state);const list=storyEditorElement('div','story-key-list');list.id='effectCueList';list.setAttribute('aria-label','Story effects · tap to preview');section.append(list);
  section.append(storyEditorElement('p','story-muted','Each cue follows the episode playhead in Preview, Play and Watch Episode. Paper magic stays behind the characters and follows the Effects layer visibility. Save Project and Undo include these cues.'));
  body.insertBefore(section,document.getElementById('storyFrameMode'));storyEffectsEditorNew();storyEffectsEditorSync();
}
const storyEffectsPreviousEditorInstall=storyEditorInstall,storyEffectsPreviousEditorSync=storyEditorSync,storyEffectsPreviousEditorRefresh=storyEditorRefreshControls;
storyEditorInstall=function(){const result=storyEffectsPreviousEditorInstall();storyEffectsEditorInstall();return result;};
storyEditorSync=function(){const result=storyEffectsPreviousEditorSync();storyEffectsEditorSync();return result;};
storyEditorRefreshControls=function(){const result=storyEffectsPreviousEditorRefresh();storyEffectsEditorRefresh();return result;};
window.SWYRL_ENGINE_STORY_EFFECTS_EDITOR=Object.freeze({install:storyEffectsEditorInstall,sync:storyEffectsEditorSync,selectCue:storyEffectsEditorSelect});
