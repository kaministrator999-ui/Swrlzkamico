// Story Actions are authored beside the native shot, pose and dialogue tracks.
let performanceEditorInstalled=false,performanceEditorSyncing=false,performanceEditorSelected='';
function performanceEditorAPI(){return window.SWYRL_ENGINE_PERFORMANCE;}
function performanceEditorField(id,label,kind='number',low,high){
  const row=storyEditorElement('label','story-field');row.htmlFor=id;
  row.append(storyEditorElement('span','',label));
  const input=storyEditorElement('input');input.id=id;input.type=kind;input.dataset.performanceEditable='true';
  if(kind==='number'){
    input.step='any';input.required=true;input.inputMode='decimal';
    if(Number.isFinite(low))input.min=String(low);if(Number.isFinite(high))input.max=String(high);
  }else if(kind==='text')input.maxLength=100;
  input.setAttribute('aria-label',label);row.append(input);return row;
}
function performanceEditorSelect(id,label,options){
  const row=storyEditorElement('label','story-field');row.htmlFor=id;
  row.append(storyEditorElement('span','',label));
  const select=storyEditorElement('select');select.id=id;select.dataset.performanceEditable='true';select.setAttribute('aria-label',label);
  for(const [value,text] of options){const option=storyEditorElement('option','',text);option.value=value;select.append(option);}
  row.append(select);return row;
}
function performanceEditorNumber(id){
  const input=document.getElementById(id);
  if(!input||input.value.trim()===''||!Number.isFinite(Number(input.value))||!input.checkValidity()){
    input?.reportValidity();storyEditorNotify('Enter a valid '+(input?.getAttribute('aria-label')||'action value')+'.',true);return null;
  }
  return Number(input.value);
}
function performanceEditorEditable(){return performanceIsProject()&&storyEditable();}
function performanceEditorMakeId(){
  const taken=new Set(performanceEditorAPI().model().clips.map(clip=>clip.id));let serial=1;
  while(taken.has('action-'+serial))serial++;return 'action-'+serial;
}
function performanceEditorSave(){
  if(!performanceEditorEditable()){storyEditorNotify('Pause playback to edit a story action.',true);return;}
  const time=performanceEditorNumber('performanceTime'),duration=performanceEditorNumber('performanceDuration'),strength=performanceEditorNumber('performanceStrength');
  if(time===null||duration===null||strength===null)return;
  if(time+duration>storyTimeline().duration+.000001){storyEditorNotify('The action must finish within the episode.',true);return;}
  const id=performanceEditorSelected||performanceEditorMakeId();
  const clip={id,time,duration,strength,character:document.getElementById('performanceCharacter').value,
    action:document.getElementById('performanceAction').value,side:document.getElementById('performanceSide').value,
    label:document.getElementById('performanceLabel').value.trim()||PERFORMANCE_ACTIONS.find(item=>item.id===document.getElementById('performanceAction').value).label};
  if(!performanceEditorAPI().upsert(clip)){storyEditorNotify('The story action could not be saved. Up to 128 actions fit in one episode.',true);return;}
  performanceEditorSelected=id;performanceEditorSync();
  storyEditorNotify('Saved '+(clip.character==='kami'?'Kami':'§wyrlz')+' · '+clip.label+'.');
}
function performanceEditorDelete(){
  if(!performanceEditorEditable()){storyEditorNotify('Pause playback to delete a story action.',true);return;}
  if(!performanceEditorSelected||!performanceEditorAPI().remove(performanceEditorSelected)){
    storyEditorNotify('Select a saved action to delete it.',true);return;
  }
  performanceEditorSelected='';performanceEditorSync();storyEditorNotify('Story action deleted.');
}
function performanceEditorSettings(){
  if(!performanceEditorEditable()){storyEditorNotify('Pause playback to change Story Actions settings.',true);return;}
  const maxDialogueSeconds=performanceEditorNumber('performanceMaxDialogue');if(maxDialogueSeconds===null)return;
  if(!performanceEditorAPI().configure({enabled:document.getElementById('performanceEnabled').checked,
    limitDialogue:document.getElementById('performanceLimitDialogue').checked,maxDialogueSeconds})){
    storyEditorNotify('Story Actions settings could not be saved.',true);return;
  }
  storyEditorNotify('Story Actions and dialogue timing saved in this project.');
}
function performanceEditorDuration(){
  if(!performanceEditorEditable()){storyEditorNotify('Pause playback to change the episode duration.',true);return;}
  const duration=performanceEditorNumber('performanceEpisodeDuration');if(duration===null)return;
  if(!storySetDuration(duration)){storyEditorNotify('The episode duration could not be saved.',true);return;}
  storyEditorNotify('Episode duration saved. Shots, poses, scenery and actions keep their timing together.');
}
function performanceEditorNew(){
  performanceEditorSelected='';performanceEditorSync();
  document.getElementById('performanceLabel')?.focus();
}
function performanceEditorPreview(){
  const time=performanceEditorNumber('performanceTime'),duration=performanceEditorNumber('performanceDuration');
  if(time===null||duration===null)return;
  storyEditorSetTime(Math.min(storyTimeline().duration,time+duration*.45));
}
function performanceEditorRefreshControls(){
  const section=document.getElementById('storyPerformanceSection');if(!section)return;
  section.hidden=!performanceIsProject();if(section.hidden)return;
  const editable=performanceEditorEditable();
  for(const control of section.querySelectorAll('[data-performance-editable]'))control.disabled=!editable;
  document.getElementById('performanceDelete').disabled=!editable||!performanceEditorSelected;
  // Preview follows the common paused playhead and never changes saved clips.
  document.getElementById('performancePreview').disabled=!editable;
  document.getElementById('performanceSave').textContent=performanceEditorSelected?'Update action':'Add action';
}
function performanceEditorSync(){
  const section=document.getElementById('storyPerformanceSection');if(!section||performanceEditorSyncing)return;
  performanceEditorSyncing=true;
  try{
    section.hidden=!performanceIsProject();if(section.hidden)return;
    const model=performanceEditorAPI().model(),duration=storyTimeline().duration;
    let selected=model.clips.find(clip=>clip.id===performanceEditorSelected);
    if(!selected)performanceEditorSelected='';
    const picker=document.getElementById('performanceClip');picker.replaceChildren();
    const blank=storyEditorElement('option','','New action');blank.value='';picker.append(blank);
    for(const clip of model.clips){
      const option=storyEditorElement('option','',storyEditorNumber(clip.time)+' s · '+(clip.character==='kami'?'Kami':'§wyrlz')+' · '+clip.label);
      option.value=clip.id;picker.append(option);
    }
    picker.value=performanceEditorSelected;
    selected=selected||{character:rigEditorCharacter()||'kami',action:'greet',side:'right',time:Math.min(Math.max(0,storyEditorTime||0),duration-.05),duration:Math.min(2,duration-Math.min(Math.max(0,storyEditorTime||0),duration-.05)),strength:1,label:''};
    document.getElementById('performanceEnabled').checked=model.enabled;
    document.getElementById('performanceLimitDialogue').checked=model.limitDialogue;
    document.getElementById('performanceMaxDialogue').value=storyEditorNumber(model.maxDialogueSeconds,6);
    document.getElementById('performanceEpisodeDuration').value=storyEditorNumber(duration,6);
    for(const field of ['character','action','side','label'])document.getElementById('performance'+field[0].toUpperCase()+field.slice(1)).value=selected[field];
    for(const field of ['time','duration','strength'])document.getElementById('performance'+field[0].toUpperCase()+field.slice(1)).value=storyEditorNumber(selected[field],6);
    document.getElementById('performanceTime').max=String(duration-.05);
    document.getElementById('performanceDuration').max=String(duration);
    const hint=document.getElementById('performanceHint');
    hint.textContent=model.enabled?'Actions blend into connected limb poses. Move each mage through the set with its character track.':
      'Enable Story Actions and save settings to play these performances. Existing pose keys stay editable.';
    document.getElementById('performanceCount').textContent=model.clips.length+' / '+PERFORMANCE_MAX_CLIPS+' saved actions';
    performanceEditorRefreshControls();
  }finally{performanceEditorSyncing=false;}
}
function performanceEditorInstall(){
  const body=document.getElementById('storyStudioBody');if(!body||performanceEditorInstalled)return;
  performanceEditorInstalled=true;
  const section=storyEditorElement('details','story-performance-editor');section.id='storyPerformanceSection';
  section.append(storyEditorElement('summary','','Story Actions'));
  section.append(performanceEditorField('performanceEnabled','Enable Story Actions','checkbox'));
  section.append(performanceEditorField('performanceLimitDialogue','Limit dialogue mouth movement','checkbox'));
  section.append(performanceEditorField('performanceMaxDialogue','Maximum dialogue seconds','number',1,10));
  const settings=storyEditorButton('performanceApplySettings','Save action settings',performanceEditorSettings);
  settings.dataset.performanceEditable='true';section.append(settings);
  section.append(performanceEditorField('performanceEpisodeDuration','Episode duration seconds','number',1,3600));
  const duration=storyEditorButton('performanceApplyDuration','Resize episode timing',performanceEditorDuration);
  duration.dataset.performanceEditable='true';section.append(duration);
  const selectRow=performanceEditorSelect('performanceClip','Saved action',[]),picker=selectRow.querySelector('select');
  picker.addEventListener('change',()=>{
    performanceEditorSelected=picker.value;
    const clip=performanceEditorAPI().model().clips.find(item=>item.id===performanceEditorSelected);
    if(clip)storyEditorSetTime(clip.time);else performanceEditorSync();
  });section.append(selectRow);
  const newAction=storyEditorButton('performanceNew','New action at playhead',performanceEditorNew);
  newAction.dataset.performanceEditable='true';section.append(newAction);
  const fields=storyEditorElement('div','story-performance-fields');
  fields.append(performanceEditorSelect('performanceCharacter','Character',[['kami','Kami'],['swyrlz','§wyrlz']]),
    performanceEditorSelect('performanceAction','Action',PERFORMANCE_ACTIONS.map(item=>[item.id,item.label])),
    performanceEditorSelect('performanceSide','Leading hand',[['left','Left'],['right','Right']]),
    performanceEditorField('performanceTime','Start seconds','number',0,3600),
    performanceEditorField('performanceDuration','Action duration','number',.05,3600),
    performanceEditorField('performanceStrength','Action strength','number',0,1.5));section.append(fields);
  section.append(performanceEditorField('performanceLabel','Action label','text'));
  const actions=storyEditorElement('div','story-key-actions');
  for(const [id,label,callback] of [['performanceSave','Add action',performanceEditorSave],['performanceDelete','Delete action',performanceEditorDelete],['performancePreview','Preview action',performanceEditorPreview]]){
    const button=storyEditorButton(id,label,callback);button.dataset.performanceEditable='true';actions.append(button);
  }section.append(actions);
  const count=storyEditorElement('p','story-muted');count.id='performanceCount';section.append(count);
  const hint=storyEditorElement('p','story-muted');hint.id='performanceHint';section.append(hint);
  const track=document.getElementById('storyTrack')?.closest('label');body.insertBefore(section,track||body.firstChild);
  performanceEditorSync();
}
const performancePreviousEditorInstall=storyEditorInstall;
storyEditorInstall=function(){const result=performancePreviousEditorInstall();performanceEditorInstall();return result;};
const performancePreviousEditorSync=storyEditorSync;
storyEditorSync=function(){const result=performancePreviousEditorSync();performanceEditorSync();return result;};
const performancePreviousEditorRefresh=storyEditorRefreshControls;
storyEditorRefreshControls=function(){const result=performancePreviousEditorRefresh();performanceEditorRefreshControls();return result;};
window.SWYRL_ENGINE_PERFORMANCE_EDITOR=Object.freeze({install:performanceEditorInstall,sync:performanceEditorSync,
  select:id=>{performanceEditorSelected=typeof id==='string'?id:'';performanceEditorSync();}});
