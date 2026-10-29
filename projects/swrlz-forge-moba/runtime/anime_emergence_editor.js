// Book-opening controls author the same project used by Preview, Play and Watch.
let emergenceEditorInstalled=false,emergenceEditorSyncing=false,emergenceEditorLayer='book';
const EMERGENCE_EDITOR_LABELS={book:'Book · covers and pages',background:'Background · arches and stars',midground:'Midground · library scenery',atmosphere:'Atmosphere · pages and mist',effects:'Effects · magic',kami:'Kami · main mage',swyrlz:'§wyrlz · companion mage',foreground:'Foreground · desk props'};
function emergenceEditorField(id,label,low,high){
  const row=storyEditorElement('label','story-field');row.htmlFor=id;row.append(storyEditorElement('span','',label));
  const input=storyEditorElement('input');input.id=id;input.type='number';input.step='any';input.inputMode='decimal';input.min=String(low);input.max=String(high);input.required=true;
  input.dataset.emergenceEditable='true';input.setAttribute('aria-label',label);row.append(input);return row;
}
function emergenceEditorRead(id){
  const input=document.getElementById(id);
  if(!input||input.value.trim()===''||!Number.isFinite(Number(input.value))||!input.checkValidity()){
    input?.reportValidity();storyEditorNotify('Enter a valid '+(input?.getAttribute('aria-label')||'opening value')+'.',true);return null;
  }
  return Number(input.value);
}
function emergenceEditorApply(){
  if(!storyEditorState().editable){storyEditorNotify('Pause playback to edit the book opening.',true);return;}
  const duration=emergenceEditorRead('emergenceDuration'),delay=emergenceEditorRead('emergenceDelay'),layerDuration=emergenceEditorRead('emergenceLayerDuration');
  if(duration===null||delay===null||layerDuration===null)return;
  const previous=emergenceModel(),ratio=duration/previous.duration;
  // A duration change scales all rows; this selected row's displayed timing
  // is scaled too unless the user explicitly changes it to another value.
  const oldTiming=previous.layers[emergenceEditorLayer],delayEdited=Math.abs(delay-oldTiming.delay)>1e-6,durationEdited=Math.abs(layerDuration-oldTiming.duration)>1e-6;
  const selectedDelay=delayEdited?delay:delay*ratio,selectedDuration=durationEdited?layerDuration:layerDuration*ratio;
  if(selectedDelay+selectedDuration>duration+1e-6){storyEditorNotify('Finish this layer within the opening duration.',true);return;}
  const value={enabled:document.getElementById('emergenceEnabled').checked,duration,
    layers:{[emergenceEditorLayer]:{delay:selectedDelay,duration:selectedDuration}}};
  if(!emergenceConfigure(value)){storyEditorNotify('The book opening could not be saved.',true);return;}
  storyEditorPreviewFrame();emergenceEditorSync();storyEditorNotify('Book opening saved. Preview the first seconds to see the pieces unfold from the pages.');
}
function emergenceEditorRefresh(){
  const section=document.getElementById('storyEmergenceSection');if(!section||section.hidden)return;
  const editable=storyEditorState().editable;
  for(const control of section.querySelectorAll('[data-emergence-editable]'))control.disabled=!editable;
  const output=document.getElementById('emergenceFrameStatus'),time=storyEditorTime||0,model=emergenceModel();
  output.textContent=!model.enabled?'Book opening disabled · saved poses play directly':!editable?'Live opening · pause to edit timing':
    time<model.duration?'Opening '+storyEditorNumber(time)+' / '+storyEditorNumber(model.duration)+' s · '+Math.round(emergenceProgress(emergenceEditorLayer,time)*100)+'% expanded':'Opening complete · saved performance continues';
}
function emergenceEditorSync(){
  const section=document.getElementById('storyEmergenceSection');if(!section||emergenceEditorSyncing)return;
  emergenceEditorSyncing=true;
  try{
    section.hidden=!storyEditorIsProject();if(section.hidden)return;
    const model=emergenceModel(),timing=model.layers[emergenceEditorLayer],limit=Math.min(30,storyTimeline().duration);
    document.getElementById('emergenceEnabled').checked=model.enabled;
    const duration=document.getElementById('emergenceDuration');duration.min=String(Math.min(4,limit));duration.max=String(limit);duration.value=storyEditorNumber(model.duration,6);duration.dataset.referenceDuration=String(model.duration);
    document.getElementById('emergenceLayer').value=emergenceEditorLayer;
    const delay=document.getElementById('emergenceDelay');delay.max=String(Math.max(0,model.duration-.25));delay.value=storyEditorNumber(timing.delay,6);
    const span=document.getElementById('emergenceLayerDuration');span.min=String(Math.min(.25,model.duration-timing.delay));span.max=String(model.duration);span.value=storyEditorNumber(timing.duration,6);
    const list=document.getElementById('emergenceTimingList');list.replaceChildren();
    for(const id of EMERGENCE_LAYERS){
      const value=model.layers[id],row=storyEditorElement('div','story-emergence-timing');row.dataset.emergenceLayer=id;
      row.append(storyEditorElement('span','',EMERGENCE_EDITOR_LABELS[id].split(' · ')[0]),storyEditorElement('span','',storyEditorNumber(value.delay)+'–'+storyEditorNumber(value.delay+value.duration)+' s'));list.append(row);
    }
    emergenceEditorRefresh();
  }finally{emergenceEditorSyncing=false;}
}
function emergenceEditorInstall(){
  const body=document.getElementById('storyStudioBody');if(!body||emergenceEditorInstalled)return;emergenceEditorInstalled=true;
  const section=storyEditorElement('details','story-emergence-section');section.id='storyEmergenceSection';section.open=true;
  section.append(storyEditorElement('summary','','Book Opening · unfold from the pages'));
  const fields=storyEditorElement('div','story-emergence-config');
  const enabledRow=storyEditorElement('label','story-field story-check');enabledRow.htmlFor='emergenceEnabled';enabledRow.append(storyEditorElement('span','','Expand from book'));
  const enabled=storyEditorElement('input');enabled.id='emergenceEnabled';enabled.type='checkbox';enabled.dataset.emergenceEditable='true';enabledRow.append(enabled);
  fields.append(enabledRow,emergenceEditorField('emergenceDuration','Opening duration (s)',4,30));section.append(fields);
  const row=storyEditorElement('label','story-label');row.htmlFor='emergenceLayer';row.append(storyEditorElement('span','','Opening layer'));
  const picker=storyEditorElement('select');picker.id='emergenceLayer';picker.setAttribute('aria-label','Select an opening layer');
  for(const id of EMERGENCE_LAYERS){const option=storyEditorElement('option','',EMERGENCE_EDITOR_LABELS[id]);option.value=id;picker.append(option);}
  picker.addEventListener('change',()=>{emergenceEditorLayer=picker.value;emergenceEditorSync();});row.append(picker);section.append(row);
  const timing=storyEditorElement('div','story-emergence-config');timing.append(emergenceEditorField('emergenceDelay','Start delay (s)',0,11.75),emergenceEditorField('emergenceLayerDuration','Expansion time (s)',.25,12));section.append(timing);
  section.querySelector('#emergenceDuration').addEventListener('input',()=>{
    const duration=Number(section.querySelector('#emergenceDuration').value);if(!Number.isFinite(duration))return;
    section.querySelector('#emergenceDelay').max=String(Math.max(0,duration-.25));
    section.querySelector('#emergenceLayerDuration').max=String(duration);
  });
  section.querySelector('#emergenceDuration').addEventListener('change',()=>{
    const input=section.querySelector('#emergenceDuration'),duration=Number(input.value);if(!input.checkValidity()||!Number.isFinite(duration))return;
    const previous=Number(input.dataset.referenceDuration)||emergenceModel().duration,ratio=duration/previous;
    for(const id of ['emergenceDelay','emergenceLayerDuration']){
      const field=section.querySelector('#'+id);field.value=storyEditorNumber(Number(field.value)*ratio,6);
    }
    input.dataset.referenceDuration=String(duration);
  });
  const apply=storyEditorButton('emergenceApply','Apply Book Opening',emergenceEditorApply);apply.dataset.emergenceEditable='true';section.append(apply);
  section.append(storyEditorElement('p','story-muted','The covers open first. Characters, architecture, stars and props rise and spread from the physical pages; individual scenery pieces unfold in sequence. The saved performance continues after the opening.'));
  const status=storyEditorElement('p','story-muted');status.id='emergenceFrameStatus';section.append(status);
  const list=storyEditorElement('div','story-emergence-timings');list.id='emergenceTimingList';list.setAttribute('aria-label','Book opening layer timing');section.append(list);
  body.insertBefore(section,document.getElementById('storyFrameMode'));emergenceEditorSync();
}
const emergencePreviousEditorInstall=storyEditorInstall,emergencePreviousEditorSync=storyEditorSync,emergencePreviousEditorRefresh=storyEditorRefreshControls;
storyEditorInstall=function(){const result=emergencePreviousEditorInstall();emergenceEditorInstall();return result;};
storyEditorSync=function(){const result=emergencePreviousEditorSync();emergenceEditorSync();return result;};
storyEditorRefreshControls=function(){const result=emergencePreviousEditorRefresh();emergenceEditorRefresh();return result;};
window.SWYRL_ENGINE_EMERGENCE_EDITOR=Object.freeze({install:emergenceEditorInstall,sync:emergenceEditorSync});
