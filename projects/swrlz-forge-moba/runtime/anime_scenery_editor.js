// Individual scenery cutouts use the native Animation Studio playhead and history.
let sceneryEditorInstalled = false;
let sceneryEditorSyncing = false;
const sceneryEditorSelections = {background:'arches-left',midground:'pillars-left',atmosphere:'pages',effects:'flame-left'};
const SCENERY_EDITOR_TRACKS = Object.freeze(['background','midground','atmosphere','effects']);
const SCENERY_EDITOR_DEGREES = 180 / Math.PI;
const SCENERY_EDITOR_FIELDS = Object.freeze([
  ['x','sceneryX','Position X',-30,30], ['y','sceneryY','Position Y',-30,30], ['z','sceneryZ','Depth Z',-30,-.1],
  ['rotationX','sceneryRotationX','Lean X (°)',-.5*SCENERY_EDITOR_DEGREES,.5*SCENERY_EDITOR_DEGREES],
  ['rotationY','sceneryRotationY','Turn Y (°)',-.5*SCENERY_EDITOR_DEGREES,.5*SCENERY_EDITOR_DEGREES],
  ['rotationZ','sceneryRotationZ','Turn Z (°)',-.5*SCENERY_EDITOR_DEGREES,.5*SCENERY_EDITOR_DEGREES], ['scale','sceneryScale','Scale',.1,3],
  ['opacity','sceneryOpacity','Opacity',0,1], ['unfold','sceneryUnfold','Unfold',0,1]
]);
function sceneryEditorAPI(){return window.SWYRL_ENGINE_SCENERY;}
function sceneryEditorIsTrack(){return storyEditorIsProject()&&SCENERY_EDITOR_TRACKS.includes(storyEditorTrack);}
function sceneryEditorModel(){return sceneryEditorIsTrack()?sceneryEditorAPI()?.model?.():null;}
function sceneryEditorObjects(model){
  return Object.values(model?.objects||{}).filter(object=>object&&object.parent===storyEditorTrack);
}
function sceneryEditorTime(){return Math.max(0,Number(storyEditorTime)||0);}
function sceneryEditorNumber(value){return String(Number(Number(value||0).toFixed(6)));}
function sceneryEditorEditable(){return !!storyEditorState().editable;}
function sceneryEditorNotice(message,error=false){storyEditorNotify(message,error);}
function sceneryEditorSelected(model=sceneryEditorModel()){
  const objects=sceneryEditorObjects(model),selected=sceneryEditorSelections[storyEditorTrack];
  const object=objects.find(item=>item.id===selected)||objects[0];
  if(object)sceneryEditorSelections[storyEditorTrack]=object.id;
  return object||null;
}
function sceneryEditorField(id,label,low,high){
  const row=storyEditorElement('label','story-field');row.htmlFor=id;
  row.append(storyEditorElement('span','',label));
  const input=storyEditorElement('input');input.id=id;input.type='number';input.step='any';
  input.inputMode='decimal';input.required=true;input.dataset.sceneryEditable='true';
  if(Number.isFinite(low))input.min=String(low);if(Number.isFinite(high))input.max=String(high);
  input.setAttribute('aria-label',label);row.append(input);return row;
}
function sceneryEditorReadNumber(id){
  const input=document.getElementById(id);
  if(!input||input.value.trim()===''||!Number.isFinite(Number(input.value))||!input.checkValidity()){
    input?.reportValidity();sceneryEditorNotice('Enter a valid value for '+(input?.getAttribute('aria-label')||'this scenery piece')+'.',true);return null;
  }
  return Number(input.value);
}
function sceneryEditorPreview(){
  if(typeof storyEditorPreviewFrame==='function')storyEditorPreviewFrame();
  else if(typeof storyRender==='function')storyRender();
  sceneryEditorSync();
}
function sceneryEditorSaveKey(){
  if(!sceneryEditorEditable()){sceneryEditorNotice('Pause playback to edit a scenery piece.',true);return;}
  const object=sceneryEditorSelected();if(!object)return;
  const key={time:sceneryEditorTime(),ease:document.getElementById('sceneryEase').value,
    visible:document.getElementById('sceneryVisible').checked};
  for(const [field,id] of SCENERY_EDITOR_FIELDS){
    const value=sceneryEditorReadNumber(id);if(value===null)return;
    key[field]=field.startsWith('rotation')?value/SCENERY_EDITOR_DEGREES:value;
  }
  const upsert=sceneryEditorAPI()?.upsertKey;
  if(typeof upsert!=='function'||upsert(object.id,key)===false){
    sceneryEditorNotice('This scenery key could not be saved. Pause playback and try again.',true);return;
  }
  sceneryEditorPreview();
  sceneryEditorNotice('Saved '+(object.label||object.id)+' key at '+sceneryEditorNumber(key.time)+' seconds.');
}
function sceneryEditorDeleteKey(){
  if(!sceneryEditorEditable()){sceneryEditorNotice('Pause playback to delete a scenery key.',true);return;}
  const object=sceneryEditorSelected(),remove=sceneryEditorAPI()?.removeKey;
  if(!object||typeof remove!=='function'||remove(object.id,sceneryEditorTime())===false){
    sceneryEditorNotice('Select an existing scenery key to delete it.',true);return;
  }
  sceneryEditorPreview();sceneryEditorNotice('Scenery key deleted. The remaining keys still interpolate.');
}
function sceneryEditorApplyConfig(){
  if(!sceneryEditorEditable()){sceneryEditorNotice('Pause playback to change scenery depth.',true);return;}
  const depth=sceneryEditorReadNumber('sceneryDepth');if(depth===null)return;
  const configure=sceneryEditorAPI()?.configure;
  if(typeof configure!=='function'||configure({enabled:document.getElementById('sceneryEnabled').checked,depth})===false){
    sceneryEditorNotice('Scenery depth could not be saved.',true);return;
  }
  sceneryEditorPreview();sceneryEditorNotice('Layered scenery and pop-out depth saved in this project.');
}
function sceneryEditorSelect(id){
  const object=sceneryEditorObjects(sceneryEditorModel()).find(item=>item.id===id);if(!object)return false;
  sceneryEditorSelections[storyEditorTrack]=id;sceneryEditorSync();return true;
}
function sceneryEditorRefreshControls(){
  const section=document.getElementById('storyScenerySection');if(!section)return;
  const model=sceneryEditorModel(),object=sceneryEditorSelected(model);
  section.hidden=!model||!object;if(section.hidden)return;
  const editable=sceneryEditorEditable(),time=sceneryEditorTime();
  for(const control of section.querySelectorAll('[data-scenery-editable]'))control.disabled=!editable;
  const keys=Array.isArray(object.keys)?object.keys:[],duration=Number(storyEditorModel()?.duration)||134;
  const exact=keys.some(key=>Math.abs(Number(key.time)-time)<1e-6);
  document.getElementById('sceneryDeleteKey').disabled=!editable||!exact||time===0||time===duration;
  document.getElementById('sceneryFrameMode').textContent=!editable?'Live playback · pause to move a scenery piece':exact?
    (time===0||time===duration?'Opening/final scenery key · update its values':'Existing scenery key · update its values'):
    'Interpolated scenery pose · add a key to edit';
}
function sceneryEditorSync(){
  if(sceneryEditorSyncing||!document.getElementById('storyScenerySection'))return;
  sceneryEditorSyncing=true;
  try{
    const section=document.getElementById('storyScenerySection'),model=sceneryEditorModel(),object=sceneryEditorSelected(model);
    section.hidden=!model||!object;if(section.hidden)return;
    document.getElementById('sceneryEnabled').checked=model.enabled!==false;
    const depthInput=document.getElementById('sceneryDepth');
    if(Array.isArray(model.bounds?.depth)){depthInput.min=String(model.bounds.depth[0]);depthInput.max=String(model.bounds.depth[1]);}
    depthInput.value=sceneryEditorNumber(model.depth??1);
    const picker=document.getElementById('sceneryObject');picker.replaceChildren();
    for(const item of sceneryEditorObjects(model)){
      const option=storyEditorElement('option','',item.label||item.id);option.value=item.id;picker.append(option);
    }
    picker.value=object.id;
    const sample=sceneryEditorAPI()?.sample?.(object.id,sceneryEditorTime())||{},keys=Array.isArray(object.keys)?object.keys:[];
    const exact=keys.find(key=>Math.abs(Number(key.time)-sceneryEditorTime())<1e-6);
    for(const [field,id,,low,high] of SCENERY_EDITOR_FIELDS){
      const input=document.getElementById(id),bounds=object.bounds?.[field]||model.bounds?.[field];
      const multiplier=field.startsWith('rotation')?SCENERY_EDITOR_DEGREES:1;
      input.min=Array.isArray(bounds)?String(bounds[0]*multiplier):Number.isFinite(low)?String(low):'';
      input.max=Array.isArray(bounds)?String(bounds[1]*multiplier):Number.isFinite(high)?String(high):'';
      let value=Number(sample[field]??(field==='scale'||field==='opacity'||field==='unfold'?1:0))*multiplier;
      if(!Number.isFinite(value))value=0;
      if(input.min!=='')value=Math.max(Number(input.min),value);
      if(input.max!=='')value=Math.min(Number(input.max),value);
      value=Number(sceneryEditorNumber(value));
      if(input.min!=='')value=Math.max(Number(input.min),value);
      if(input.max!=='')value=Math.min(Number(input.max),value);
      input.value=String(value);
    }
    document.getElementById('sceneryVisible').checked=sample.visible!==false;
    document.getElementById('sceneryEase').value=exact?.ease||sample.ease||'smooth';
    const keyList=document.getElementById('sceneryKeyList');keyList.replaceChildren();
    for(const key of keys){
      const selected=Math.abs(Number(key.time)-sceneryEditorTime())<1e-6;
      const button=storyEditorButton('',sceneryEditorNumber(key.time)+' s',()=>storyEditorSetTime(key.time),
        'Preview '+(object.label||object.id)+' at '+sceneryEditorNumber(key.time)+' seconds');
      button.dataset.sceneryKeyTime=String(key.time);button.classList.toggle('is-selected',selected);
      button.setAttribute('aria-pressed',String(selected));keyList.append(button);
    }
    if(!keys.length)keyList.append(storyEditorElement('span','story-muted','No scenery keys yet. Add this frame.'));
    sceneryEditorRefreshControls();
  }finally{sceneryEditorSyncing=false;}
}
function sceneryEditorInstall(){
  const body=document.getElementById('storyStudioBody');if(sceneryEditorInstalled||!body)return;
  sceneryEditorInstalled=true;
  const section=storyEditorElement('details','story-scenery-section');section.id='storyScenerySection';section.open=true;section.hidden=true;
  section.append(storyEditorElement('summary','','Scenery Depth · individual cutouts'));
  const config=storyEditorElement('div','story-scenery-config');
  const enabledRow=storyEditorElement('label','story-field story-check');enabledRow.htmlFor='sceneryEnabled';
  enabledRow.append(storyEditorElement('span','','Layered scenery'));
  const enabled=storyEditorElement('input');enabled.id='sceneryEnabled';enabled.type='checkbox';enabled.dataset.sceneryEditable='true';enabledRow.append(enabled);
  config.append(enabledRow,sceneryEditorField('sceneryDepth','Pop-out depth',.3,1.5));section.append(config);
  const apply=storyEditorButton('sceneryApplyConfig','Apply Scenery Depth',sceneryEditorApplyConfig);apply.dataset.sceneryEditable='true';section.append(apply);
  const objectRow=storyEditorElement('label','story-label');objectRow.htmlFor='sceneryObject';objectRow.append(storyEditorElement('span','','Scenery piece'));
  const picker=storyEditorElement('select');picker.id='sceneryObject';picker.setAttribute('aria-label','Select an individual scenery piece');
  picker.addEventListener('change',()=>sceneryEditorSelect(picker.value));objectRow.append(picker);section.append(objectRow);
  const fields=storyEditorElement('div','story-key-fields story-scenery-fields');fields.id='sceneryKeyFields';
  for(const [field,id,label,low,high] of SCENERY_EDITOR_FIELDS){
    const row=sceneryEditorField(id,label,low,high);row.querySelector('input').dataset.sceneryField=field;fields.append(row);
  }
  const visibleRow=storyEditorElement('label','story-field story-check');visibleRow.htmlFor='sceneryVisible';visibleRow.append(storyEditorElement('span','','Visible'));
  const visible=storyEditorElement('input');visible.id='sceneryVisible';visible.type='checkbox';visible.dataset.sceneryEditable='true';visibleRow.append(visible);fields.append(visibleRow);section.append(fields);
  section.append(storyEditorElement('p','story-muted','Move this cutout within its scenery layer. Depth Z brings it forward or sends it back; Unfold raises it from the book.'));
  const easeRow=storyEditorElement('label','story-label');easeRow.htmlFor='sceneryEase';easeRow.append(storyEditorElement('span','','Easing to next scenery key'));
  const ease=storyEditorElement('select');ease.id='sceneryEase';ease.dataset.sceneryEditable='true';
  for(const [value,label] of [['smooth','Smooth'],['linear','Linear'],['hold','Hold']]){
    const option=storyEditorElement('option','',label);option.value=value;ease.append(option);
  }
  easeRow.append(ease);section.append(easeRow);
  const actions=storyEditorElement('div','story-key-actions');
  for(const [id,label,callback] of [['sceneryAddKey','Add/Update Scenery Key',sceneryEditorSaveKey],['sceneryDeleteKey','Delete Scenery Key',sceneryEditorDeleteKey]]){
    const button=storyEditorButton(id,label,callback);button.dataset.sceneryEditable='true';actions.append(button);
  }
  section.append(actions);
  const mode=storyEditorElement('p','story-muted');mode.id='sceneryFrameMode';section.append(mode);
  section.append(storyEditorElement('span','story-section-label','Scenery keys · tap to preview'));
  const keyList=storyEditorElement('div','story-key-list');keyList.id='sceneryKeyList';keyList.setAttribute('aria-label','Keyframes on the selected scenery piece');section.append(keyList);
  section.append(storyEditorElement('p','story-muted','The playhead above controls this piece. Scenery keys and depth stay in Save Project and Undo/Redo.'));
  body.insertBefore(section,document.getElementById('storyFrameMode'));sceneryEditorSync();
}
const sceneryPreviousEditorInstall=storyEditorInstall;
storyEditorInstall=function(){const result=sceneryPreviousEditorInstall();sceneryEditorInstall();return result;};
const sceneryPreviousEditorSync=storyEditorSync;
storyEditorSync=function(){const result=sceneryPreviousEditorSync();sceneryEditorSync();return result;};
const sceneryPreviousEditorRefresh=storyEditorRefreshControls;
storyEditorRefreshControls=function(){const result=sceneryPreviousEditorRefresh();sceneryEditorRefreshControls();return result;};
window.SWYRL_ENGINE_SCENERY_EDITOR=Object.freeze({install:sceneryEditorInstall,sync:sceneryEditorSync,selectObject:sceneryEditorSelect});
