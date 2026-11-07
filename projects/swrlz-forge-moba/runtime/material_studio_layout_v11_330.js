/* SE330_MATERIAL_STUDIO_LAYOUT_START */
// One material workspace around the existing native library, authoring fields,
// painting surface and renderer. Opening the studio never creates project data.
(function se330MaterialStudio(){
 'use strict';
 const q=(s,r=document)=>r.querySelector(s);
 let ui=null,pending=false;
 const state={pane:'library',preview:'texture'};
 function button(text,fn){const b=document.createElement('button');b.type='button';b.textContent=text;b.addEventListener('click',fn);return b;}
 function choosePane(pane,focus=false){
  if(!ui)return;
  if(pane!=='library'&&!se225MaterialUISelected())pane='library';
  state.pane=pane;ui.panel.dataset.se330Pane=pane;
  for(const b of ui.tabs.querySelectorAll('button')){
   const active=b.dataset.se330Pane===pane;b.setAttribute('aria-selected',String(active));b.tabIndex=active?0:-1;
   if(active&&focus)b.focus();
  }
 }
 function choosePreview(mode){
  state.preview=mode;if(!ui)return;ui.panel.dataset.se330Preview=mode;
  for(const b of ui.modes.querySelectorAll('button'))b.setAttribute('aria-pressed',String(b.dataset.se330Preview===mode));
 }
 function sync(){
  if(!ui)return;
  const material=se225MaterialUISelected(),empty=!material;
  ui.panel.dataset.se330Empty=String(empty);ui.empty.hidden=!empty;
  ui.previewName.textContent=material?.name||'Material preview';
  ui.project.textContent=currentProject?.name||'Current project';
  ui.libraryEmpty.hidden=!!se225MaterialData()?.materials.length;
  for(const b of ui.tabs.querySelectorAll('button'))b.disabled=empty&&b.dataset.se330Pane!=='library';
  if(empty&&state.pane!=='library')choosePane('library');
  for(const input of ui.inspector.querySelectorAll('input[type=number]')){
   const row=input.closest('label');if(row)row.classList.add('se330-number-field');
  }
  ui.frame.setAttribute('aria-label',empty?'Create your first project material':'Material library, texture preview and properties');
 }
 function install(){
  const shell=q('#se225Shell'),panel=q('#se225MaterialsPanel'),library=q('#se251MaterialLibrary');
  if(!shell||!panel||!library)return false;
  if(ui)return true;
  const scroll=q('.se225-m-scroll',panel),edit=q('#se225MEdit',panel),nativeFile=q('#se225MFile',panel);
  const texture=edit?.querySelectorAll(':scope>.se225-m-section')[1],basics=edit?.querySelector(':scope>.se225-m-section');
  if(!scroll||!edit||!texture||!basics)return false;
  panel.dataset.se330Ui='true';shell.dataset.se330Ui='true';
  const header=document.createElement('header');header.className='se330-material-header';
  const identity=document.createElement('div');identity.className='se330-identity';
  const title=document.createElement('strong');title.textContent='Materials & Textures';
  const project=document.createElement('span');project.id='se330MaterialProject';identity.append(title,project);
  const actions=document.createElement('div');actions.className='se330-header-actions';
  const projects=button('Projects',()=>q('#projectBtn')?.click());projects.id='se330MaterialProjects';projects.setAttribute('aria-label','Open starter projects and My Projects');
  const save=button('Save project',()=>q('#saveBtn')?.click());save.id='se330MaterialSave';
  const files=document.createElement('details');files.className='se330-library-menu';
  const filesTitle=document.createElement('summary');filesTitle.textContent='Tools & files';
  const fileOptions=document.createElement('div');fileOptions.className='se330-library-options';
  const utilities=document.createElement('div');utilities.id='se330MaterialTools';utilities.setAttribute('aria-label','Studio diagnostics');
  fileOptions.append(utilities,q('#se225MImportLibrary',panel),q('#se225MExportLibrary',panel));files.append(filesTitle,fileOptions);
  files.addEventListener('keydown',e=>{if(e.key==='Escape'){files.open=false;filesTitle.focus();}});
  document.addEventListener('pointerdown',e=>{if(files.open&&!files.contains(e.target))files.open=false;});
  actions.append(projects,save,files);header.append(identity,actions);panel.prepend(header);
  const tabs=document.createElement('nav');tabs.id='se330MaterialTabs';tabs.setAttribute('role','tablist');tabs.setAttribute('aria-label','Material Studio panels');
  for(const [id,label,target] of [['library','Library','se251MaterialLibrary'],['texture','Preview & paint','se330MaterialPreview'],['properties','Properties','se330MaterialInspector']]){
   const b=button(label,()=>choosePane(id));b.dataset.se330Pane=id;b.id='se330MaterialTab-'+id;b.setAttribute('role','tab');b.setAttribute('aria-controls',target);tabs.append(b);
  }
  tabs.addEventListener('keydown',e=>{
   if(!['ArrowLeft','ArrowRight','Home','End'].includes(e.key))return;
   const list=[...tabs.querySelectorAll('button:not(:disabled)')],i=list.indexOf(document.activeElement);if(i<0)return;
   const n=e.key==='Home'?0:e.key==='End'?list.length-1:(i+(e.key==='ArrowRight'?1:-1)+list.length)%list.length;
   e.preventDefault();choosePane(list[n].dataset.se330Pane,true);
  });
  header.after(tabs);scroll.classList.add('se330-panels');
  library.classList.add('se330-library');library.setAttribute('aria-labelledby','se330MaterialTab-library');
  const heading=q('.se251-side-title',library);heading.textContent='Material library';
  const count=q('#se225MCount',panel);heading.append(count);
  const oldActions=q('.se251-side-actions',library);if(oldActions)oldActions.hidden=true;
  const preset=q('#se225MPreset',panel).closest('.se225-m-row');preset.classList.add('se330-preset-card');
  const presetLabel=q('label',preset);if(presetLabel?.firstChild?.nodeType===3)presetLabel.firstChild.textContent='Start from a preset';
  heading.after(preset);
  const nativeList=q('#se225MList',panel).closest('.se225-m-row');nativeList.classList.add('se330-native-list');nativeList.hidden=true;library.append(nativeList);
  const libraryEmpty=document.createElement('p');libraryEmpty.className='se330-library-empty';libraryEmpty.textContent='No materials yet. Choose a preset above to start your project library.';
  q('#se251MaterialsTree',library).before(libraryEmpty);
  const preview=document.createElement('section');preview.className='se330-preview';preview.id='se330MaterialPreview';preview.setAttribute('aria-labelledby','se330MaterialTab-texture');
  const previewHeader=document.createElement('div');previewHeader.className='se330-preview-heading';
  const previewName=document.createElement('strong');previewName.id='se330PreviewName';
  const modes=document.createElement('div');modes.id='se330PreviewModes';modes.setAttribute('role','group');modes.setAttribute('aria-label','Material preview mode');
  for(const [id,label] of [['texture','Texture & paint'],['scene','3D scene']]){const b=button(label,()=>choosePreview(id));b.dataset.se330Preview=id;modes.append(b);}
  previewHeader.append(previewName,modes);preview.append(previewHeader);
  texture.classList.add('se330-texture-workspace');texture.open=true;
  const textureTitle=q(':scope>summary',texture);if(textureTitle){textureTitle.textContent='Texture & painting';textureTitle.hidden=true;}
  const canvas=q('#se225MCanvas',texture),surface=document.createElement('div');surface.className='se330-paint-surface';canvas.before(surface);surface.append(canvas);
  const canvasLabel=document.createElement('span');canvasLabel.className='se330-texture-caption';canvasLabel.textContent='256 × 256 · paint directly on the texture';surface.append(canvasLabel);
  const sceneStage=document.createElement('div');sceneStage.className='se330-scene-stage';sceneStage.id='se330MaterialSceneStage';
  const sceneNote=document.createElement('div');sceneNote.className='se330-scene-caption';sceneNote.textContent='Live scene · material sample';
  const sceneHint=document.createElement('p');sceneHint.textContent='The sample uses your selected material. Apply it to a scene object in Properties to update that object.';sceneStage.append(sceneNote,sceneHint);
  preview.append(texture,sceneStage);
  const inspector=document.createElement('aside');inspector.className='se330-inspector';inspector.id='se330MaterialInspector';inspector.setAttribute('aria-labelledby','se330MaterialTab-properties');
  const inspectorTitle=document.createElement('h2');inspectorTitle.textContent='Material properties';
  const duplicate=q('#se225MDuplicate',panel).closest('.se225-m-actions');
  inspector.append(inspectorTitle,duplicate,basics,q('.se225-m-assign',panel));
  edit.replaceChildren(preview,inspector);
  const empty=document.createElement('section');empty.className='se330-empty';empty.id='se330MaterialEmpty';
  const emptyIcon=document.createElement('div');emptyIcon.className='se330-empty-icon';emptyIcon.textContent='◈';
  const emptyTitle=document.createElement('h2');emptyTitle.textContent='A surface starts here';
  const emptyText=document.createElement('p');emptyText.textContent='Create a material from steel, wood, fabric and more. Then refine its finish, paint a texture and apply it to your scene.';
  const create=button('Create first material',()=>q('#se225MCreate',panel)?.click());create.id='se330MaterialFirst';
  empty.append(emptyIcon,emptyTitle,emptyText,create);
  const footer=document.createElement('footer');footer.className='se330-material-footer';footer.append(q('#se225MStatus',panel));
  const titleBlock=q('.se225-m-title',panel);titleBlock.hidden=true;
  // Keep all native IDs beneath the original panel so refresh/import closures
  // and the original edit-event delegation continue to own every mutation.
  scroll.replaceChildren(library,edit,empty);
  panel.append(titleBlock,nativeFile||document.createTextNode(''),footer);
  ui={shell,panel,frame:scroll,libraryEmpty,previewName,project,tabs,modes,inspector,empty,sceneStage};
  // Unmodified editor shortcuts belong to this focused studio. Keep local
  // controls/defaults and modified native history/save shortcuts available.
  panel.addEventListener('keydown',event=>{
   if(!event.ctrlKey&&!event.metaKey&&!event.altKey)event.stopPropagation();
  });
  panel.addEventListener('click',event=>{if(event.target.closest('#se225MCreate')){sync();if(se225MaterialUISelected())choosePane('texture');}});
  q('#se225MList',panel).addEventListener('change',()=>{sync();if(se225MaterialUISelected())choosePane('texture');});
  choosePane(se225MaterialUISelected()?'texture':'library');choosePreview('texture');sync();
  return true;
 }
 function schedule(){if(pending)return;pending=true;queueMicrotask(()=>{pending=false;if(install())sync();});}
 function materialDrawPaused(){
  if(!ui||se225Studios.active!=='materials'||document.body.dataset.se225Workspace!=='materials'||
     ui.shell.hidden||ui.panel.hidden||renderer.xr?.isPresenting)return false;
  if(state.preview!=='scene')return true;
  const stage=ui.sceneStage.getBoundingClientRect();
  return stage.width<=0||stage.height<=0;
 }
 // The opaque authoring panes do not need the game scene drawn underneath.
 // Keep the native tick/material sync running and resume the same renderer
 // immediately for the visible 3D stage, other studios and immersive XR.
 const nativeShouldRenderFrame=shouldRenderFrame;
 shouldRenderFrame=function(){
  if(materialDrawPaused())return false;
  return nativeShouldRenderFrame.apply(this,arguments);
 };
 const refresh=se225MaterialUIRefresh;
 se225MaterialUIRefresh=function(){const value=refresh.apply(this,arguments);if(ui)sync();else schedule();return value;};
 // Reposition only the pre-existing editor-only sphere inside the reserved
 // preview region. The existing engine frame and camera remain authoritative.
 const nativeFrame=se225MaterialFrame;
 se225MaterialFrame=function(dt,t){
  nativeFrame(dt,t);
  if(!ui||!se225Mat.preview||se225Studios.active!=='materials')return;
  const mesh=se225Mat.preview,stage=ui.sceneStage.getBoundingClientRect();
  const visible=state.preview==='scene'&&stage.width>0&&stage.height>0;mesh.visible=visible;
  if(!visible||!camera?.isPerspectiveCamera)return;
  const viewport=q('#viewport')?.getBoundingClientRect();if(!viewport?.width)return;
  const depth=3.6,halfHeight=depth*Math.tan(camera.fov*Math.PI/360),halfWidth=halfHeight*camera.aspect;
  const nx=((stage.left+stage.width/2-viewport.left)/viewport.width)*2-1;
  const ny=1-((stage.top+stage.height/2-viewport.top)/viewport.height)*2;
  camera.updateMatrixWorld(true);mesh.position.copy(camera.localToWorld(new THREE.Vector3(nx*halfWidth,ny*halfHeight,-depth)));
  mesh.scale.setScalar(Math.max(.15,Math.min(2,(stage.height*.27/viewport.height)*2*halfHeight/.72)));
 };
 function boot(){schedule();new MutationObserver(records=>{if(!ui&&records.some(r=>r.addedNodes.length))schedule();}).observe(document.body,{childList:true,subtree:true});
  new MutationObserver(schedule).observe(document.body,{attributes:true,attributeFilter:['data-se225-workspace']});
  window.addEventListener('swrlz:project-loaded',schedule);window.addEventListener('resize',schedule,{passive:true});
 }
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot,{once:true});else boot();
 window.SWYRL_ENGINE_MATERIAL_LAYOUT_330=Object.freeze({refresh:schedule,inspect:()=>{
  const sample=se225Mat.preview,stage=ui?.sceneStage.getBoundingClientRect(),viewport=q('#viewport')?.getBoundingClientRect();
  let sampleInsideStage=false;
  if(sample?.visible&&stage?.width&&viewport?.width&&camera){
   const p=sample.position.clone().project(camera),x=viewport.left+(p.x+1)*viewport.width/2,y=viewport.top+(1-p.y)*viewport.height/2;
   sampleInsideStage=x>=stage.left&&x<=stage.right&&y>=stage.top&&y<=stage.bottom;
  }
  return {installed:!!ui,pane:state.pane,preview:state.preview,empty:!se225MaterialUISelected(),sampleVisible:!!sample?.visible,sampleInsideStage,
   renderPaused:materialDrawPaused(),renderFrame:renderer.info.render.frame};
 }});
})();
/* SE330_MATERIAL_STUDIO_LAYOUT_END */
