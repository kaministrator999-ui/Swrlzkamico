/* SE455_VIEW_READABILITY_START */
// Compact viewport display controls and NONDESTRUCTIVE solid/flat/clay materials.
// All geometry, native topology, source materials and preview transactions remain owned
// by the pre-existing Model Atelier and se430 native workshop.
(function(){
 'use strict';
 let panel=null,root=null,menu=null,trigger=null;
 const labels={solid:'Solid',shaded:'Material',overlay:'Shaded wire',wireframe:'Wireframe',
  xray:'X-Ray',flat:'Flat',clay:'Clay'};
 const active=()=>se430BeginnerAPI()?.inspect?.()?.preview?.active===true;
 const mode=()=>atelierViewGlobal;
 function valid(x){return Object.hasOwn(labels,x);}
 function originalFor(mesh){
  if(!mesh.userData.se455OriginalMaterial)mesh.userData.se455OriginalMaterial=mesh.material;
  return mesh.userData.se455OriginalMaterial;
 }
 function cleanupMaterial(mesh){
  const material=mesh.material,base=originalFor(mesh);
  for(const child of [...mesh.children]){
   if(child.name==='Viewport wireframe overlay'||child.userData?.se455DisplayEdges){
    mesh.remove(child);
    if(child.userData?.se455OwnedGeometry)child.geometry?.dispose?.();
    child.material?.dispose?.();
   }
  }
  if(material&&material!==base&&material.userData?.atelierViewportClone)material.dispose?.();
  mesh.material=base;
 }
 function liveSwitch(){
  if(!modelRoot)return;
  for(const mesh of modelRoot.children){
   if(!mesh?.isMesh||!mesh.userData?.atelierId)continue;
   const part=partById(mesh.userData.atelierId);if(!part)continue;
   cleanupMaterial(mesh);
   atelierViewModeApply(mesh,part);
  }
  // Only ask the existing render loop for a visual refresh. Do not call
  // renderParts() here: the native workshop would cancel its live preview.
  if(typeof renderPreview==='function')renderPreview();
 }
 function update(){
  if(!panel||!menu||!trigger)return;
  const selected=mode();
  trigger.textContent='View · '+(labels[selected]||'Material');
  trigger.setAttribute('aria-expanded',String(!menu.hidden));
  for(const button of menu.querySelectorAll('[data-se455-mode]')){
   const pressed=button.dataset.se455Mode===selected;
   button.setAttribute('aria-pressed',String(pressed));
   button.classList.toggle('active',pressed);
  }
  const scope=panel.querySelector('#ViewportScope');
  const native=panel.querySelector('#ViewportMode');
  if(scope&&scope.value!=='all')scope.value='all';
  if(native&&native.value!==selected)native.value=selected;
 }
 function choose(next){
  if(!valid(next))return false;
  if(!modelRoot)return false;
  if(atelierCameraInterior){
   // Leave the native interior X-Ray inspection alone; choosing a display
   // preset after exit is supported instead of overriding its safety state.
   if(typeof status==='function')status('Exit interior inspection before changing the whole viewport display.');
   return false;
  }
  atelierViewGlobal=next;atelierViewOverrides.clear();
  const scope=panel?.querySelector('#ViewportScope');
  const native=panel?.querySelector('#ViewportMode');
  if(scope)scope.value='all';
  if(native)native.value=next;
  if(active())liveSwitch();
  else atelierViewRebuild();
  update();
  if(typeof status==='function')status('Viewport '+labels[next]+' · model geometry, camera and Undo unchanged.');
  return true;
 }
 function selectCamera(view){
  if(!['front','right','top','three'].includes(view))return;
  // Camera orientation remains the existing native six-axis implementation.
  // Do not change the model while an inset/extrude candidate owns the preview.
  if(active())return;
  se430ModelCamera.setView(view);
  menu.hidden=true;update();
 }
 function addOptions(){
  const select=panel?.querySelector('#ViewportMode');
  if(!select)return;
  for(const [key,label] of Object.entries(labels)){
   if([...select.options].some(o=>o.value===key))continue;
   const opt=document.createElement('option');opt.value=key;opt.textContent=label;
   select.append(opt);
  }
  // Selecting the buried native selector also keeps the quick readout in sync.
  select.addEventListener('change',()=>queueMicrotask(update));
 }
 function mount(p){
  if(!p||p.dataset.se455ViewReadability==='1')return;
  const stage=p.querySelector('.atelier-scene');
  if(!stage)return;
  panel=p;p.dataset.se455ViewReadability='1';
  addOptions();
  root=document.createElement('div');root.id='se455ViewSwitch';root.className='se455-view-switch';
  root.innerHTML='<button type="button" id="se455ViewButton" aria-haspopup="true" aria-expanded="false">View · Solid</button>'+
   '<div id="se455ViewMenu" role="group" aria-label="Viewport shading and camera" hidden>'+
   '<div class="se455-menu-heading">Display</div>'+
   Object.entries(labels).map(([key,label])=>'<button type="button" data-se455-mode="'+key+'" aria-pressed="false">'+label+'</button>').join('')+
   '<div class="se455-menu-heading">Camera</div>'+
   [['front','Front'],['right','Right'],['top','Top'],['three','3/4']].map(([key,label])=>
    '<button type="button" data-se455-camera="'+key+'">'+label+'</button>').join('')+
   '<div class="se455-menu-help">Display modes do not edit meshes. Solid hides transparent shading for clean modeling; Material shows authored appearance.</div>'+
   '</div>';
  stage.append(root);menu=root.querySelector('#se455ViewMenu');trigger=root.querySelector('#se455ViewButton');
  // Keep click/touch events out of the camera's orbit/pan handlers.
  root.addEventListener('pointerdown',e=>e.stopPropagation());
  trigger.addEventListener('click',()=>{menu.hidden=!menu.hidden;update();});
  menu.addEventListener('click',e=>{
   const b=e.target.closest('button');if(!b)return;
   if(b.dataset.se455Mode){const changed=choose(b.dataset.se455Mode);if(changed)menu.hidden=true;}
   else if(b.dataset.se455Camera)selectCamera(b.dataset.se455Camera);
   update();
  });
  document.addEventListener('pointerdown',e=>{
   if(menu&&!menu.hidden&&!root.contains(e.target)){menu.hidden=true;update();}
  });
  window.addEventListener('keydown',e=>{
   if(e.key==='Escape'&&menu&&!menu.hidden){menu.hidden=true;update();}
  });
  update();
 }
 const previousInstall=se430BeginnerInstall;
 se430BeginnerInstall=function(p){const result=previousInstall(p);mount(p);return result;};
 window.SWYRL_ENGINE_VIEW_READABILITY_455=Object.freeze({
  version:'v11.455',choose,inspect:()=>({mode:atelierViewGlobal,installed:!!panel,
    previewActive:active(),camera:se430ModelCamera.inspect()?.view||'orbit'})
 });
})();
/* SE455_VIEW_READABILITY_END */
/* SE455_TRANSIENT_FACE_HIGHLIGHT_START */
// The newly created inset cap needs a readable visual distinction from its rim.
// This mesh belongs only to the disposable native preview record; no saved
// topology or material is modified by these helper calls.
(function(){
 'use strict';
 function clear(record){
  const tint=record?.se455FaceTint;if(!tint)return;
  tint.parent?.remove(tint);
  tint.geometry?.dispose?.();tint.material?.dispose?.();
  record.se455FaceTint=null;
 }
 function add(record){
  clear(record);
  if(!['inset','extrude'].includes(record?.operation)||!record.data||!record.mesh)return;
  const ids=record.selectedFaces;
  const data=record.data;
  if(!Array.isArray(ids)||ids.length<1||ids.length>256)return;
  const buffer=[];
  for(const f of ids){
   if(!Number.isInteger(f)||f<0||f*3+2>=data.indices.length)return;
   for(let i=0;i<3;i++){
    const index=data.indices[f*3+i],k=index*3;
    if(!Number.isInteger(index)||k+2>=data.positions.length)return;
    buffer.push(data.positions[k],data.positions[k+1],data.positions[k+2]);
   }
  }
  if(!buffer.length)return;
  let geometry=null,material=null;
  try{
   geometry=new THREE.BufferGeometry();
   geometry.setAttribute('position',new THREE.Float32BufferAttribute(buffer,3));
   geometry.computeVertexNormals();
   material=new THREE.MeshBasicMaterial({
    color:record.operation==='extrude'?0x9dc8f8:0x87f0cf,
    transparent:true,opacity:.14,side:THREE.DoubleSide,
    depthTest:true,depthWrite:false,
    polygonOffset:true,polygonOffsetFactor:-2,polygonOffsetUnits:-2
   });
   const tint=new THREE.Mesh(geometry,material);
   tint.name='Transient selected face preview · v11.455';
   tint.userData.atelierHelper=true;tint.userData.se455Transient=true;
   tint.renderOrder=185;
   record.mesh.add(tint);record.se455FaceTint=tint;
  }catch(_){geometry?.dispose?.();material?.dispose?.();}
 }
 window.se455PreviewTintAdd=add;
 window.se455PreviewTintClear=clear;
})();
/* SE455_TRANSIENT_FACE_HIGHLIGHT_END */
