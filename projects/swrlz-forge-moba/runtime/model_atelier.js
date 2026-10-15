// §wyrl§ Engine Model Atelier v11.3 — isolated 3D authoring mode.
// All editable source geometry lives in the native project.modelAtelier envelope.
// No network model generation, proprietary game assets, arbitrary code, or HTML imports.
const MODEL_ATELIER_LIMIT=400;
const MODEL_ATELIER_KINDS=['sphere','box','cone','cylinder'];
const MODEL_ATELIER_MATERIALS=['matte','silk','gloss','metal','emissive'];
const ModelAtelier=(()=>{
  let panel,stage,view,renderer,camera,world,modelRoot,selector,selection=null;
  let raycaster,mouse,raf=0,resizeObserver=null,pressed=null,orbit={yaw:.3,pitch:.19,distance:9};
  let undo=[],redo=[],returnFocus=null,updating=false;
  const $m=id=>document.getElementById('modelAtelier'+id);
  const finite=(v,fallback=0)=>{const n=Number(v);return Number.isFinite(n)?n:fallback};
  const safeName=n=>String(n??'Part').slice(0,100);
  function model(){return currentProject?.kind==='model-atelier'?currentProject.modelAtelier:null;}
  function partById(id){return model()?.parts.find(p=>p.id===id)||null;}
  function status(message,error=false){const el=$m('Status');if(el){el.textContent=message;el.classList.toggle('error',error);}}
  function checkPart(p){
    if(!p||typeof p!=='object'||typeof p.id!=='string'||p.id.length>90||!MODEL_ATELIER_KINDS.includes(p.kind)||!/^#[0-9a-fA-F]{6}$/.test(p.color)||!MODEL_ATELIER_MATERIALS.includes(p.material))return false;
    return ['position','rotation','scale'].every(key=>Array.isArray(p[key])&&p[key].length===3&&p[key].every(v=>Number.isFinite(v)&&Math.abs(v)<=100))&&p.scale.every(v=>v>.005&&v<=20);
  }
  function validParts(parts){
    return Array.isArray(parts)&&parts.length>0&&parts.length<=MODEL_ATELIER_LIMIT
      &&parts.every(checkPart)&&new Set(parts.map(p=>p.id)).size===parts.length;
  }
  function modelSnapshot(){return JSON.stringify(model().parts);}
  function checkpoint(){if(!model())return;undo.push(modelSnapshot());if(undo.length>50)undo.shift();redo=[];}
  function signalEdited(){
    if(currentProject&&typeof currentProject==='object')currentProject.modelAtelier.editedAt='local';
    // The workbench has its own part history; the parent project must still
    // register dirty state so Projects/Load won't silently discard model edits.
    if(typeof markDirty==='function')markDirty();
    renderParts();refreshList();refreshInspector();
    status('Editable native project · '+model().parts.length+' parts. Save Project or export JSON to keep changes.');
  }
  function historyStep(backward){
    if(!model())return;
    const src=backward?undo:redo,dst=backward?redo:undo;
    if(!src.length){status('No more '+(backward?'undo':'redo')+' steps.');return;}
    dst.push(modelSnapshot());model().parts=JSON.parse(src.pop());selection=null;signalEdited();
  }
  function geometry(part){
    switch(part.kind){
      case 'box':return new THREE.BoxGeometry(1,1,1);
      case 'cone':return new THREE.ConeGeometry(1,1,9,1);
      case 'cylinder':return new THREE.CylinderGeometry(1,1,1,10,1);
      default:return new THREE.SphereGeometry(1,16,12);
    }
  }
  function material(part){
    const col=new THREE.Color(part.color);
    if(part.material==='emissive')return new THREE.MeshBasicMaterial({color:col});
    return new THREE.MeshStandardMaterial({color:col,roughness:part.material==='gloss'?.19:part.material==='metal'?.28:part.material==='silk'?.53:.85,metalness:part.material==='metal'?.68:.05,side:THREE.DoubleSide});
  }
  function wipeModel(){
    if(!modelRoot)return;
    for(const mesh of [...modelRoot.children]){modelRoot.remove(mesh);mesh.geometry?.dispose();mesh.material?.dispose();}
  }
  function renderParts(){
    if(!modelRoot||!model())return;
    wipeModel();
    for(const p of model().parts){
      const mesh=new THREE.Mesh(geometry(p),material(p));
      mesh.name=p.name;mesh.userData.atelierId=p.id;
      mesh.position.set(...p.position);mesh.rotation.set(...p.rotation);mesh.scale.set(...p.scale);
      mesh.castShadow=false;mesh.receiveShadow=false;modelRoot.add(mesh);
    }
    const current=partById(selection);
    if(current){
      const selected=modelRoot.children.find(o=>o.userData.atelierId===selection);
      if(selected){
        const outline=new THREE.BoxHelper(selected,0xe8f56f);
        outline.userData.atelierHelper=true;modelRoot.add(outline);
      }
    }
  }
  function refreshList(){
    const list=$m('Parts');if(!list||!model())return;
    list.replaceChildren();
    const group=document.createDocumentFragment();
    for(const p of model().parts){
      const option=document.createElement('option');option.value=p.id;
      option.textContent=(p.group||'Part')+' · '+safeName(p.name);group.append(option);
    }
    list.append(group);list.value=selection||'';
    $m('PartCount').textContent=String(model().parts.length)+' individually editable meshes';
    $m('Undo').disabled=!undo.length;$m('Redo').disabled=!redo.length;
  }
  function refreshInspector(){
    const p=partById(selection);updating=true;
    $m('SelectionName').textContent=p?safeName(p.name):'Select an object in the viewport or parts list';
    const controls=$m('InspectorControls');controls.hidden=!p;
    if(p){
      $m('Name').value=p.name;$m('Kind').value=p.kind;
      $m('Color').value=p.color;$m('Material').value=p.material;
      for(const kind of ['position','rotation','scale'])for(let axis=0;axis<3;axis++){
        $m(kind+axis).value=String(Number(p[kind][axis].toFixed(3)));
      }
    }
    updating=false;
  }
  function select(id){selection=partById(id)?id:null;renderParts();refreshList();refreshInspector();}
  function applyField(key,index,value){
    if(updating)return;const p=partById(selection);if(!p)return;
    let next;
    if(index!==null){
      next=finite(value,NaN);
      if(!Number.isFinite(next)||Math.abs(next)>100||key==='scale'&&(next<=.005||next>20)){status('Transform must be finite; scale must be > 0.005 and ≤ 20.',true);refreshInspector();return;}
      if(next===p[key][index])return;
    }else{
      next=String(value);
      if(key==='name')next=safeName(next);
      if(key==='color'&&!/^#[0-9a-fA-F]{6}$/.test(next))return;
      if(key==='material'&&!MODEL_ATELIER_MATERIALS.includes(next))return;
      if(key==='kind'&&!MODEL_ATELIER_KINDS.includes(next))return;
      if(next===p[key])return;
    }
    checkpoint();
    if(index!==null)p[key][index]=next;else p[key]=next;
    signalEdited();
  }
  function addPart(copy=false){
    const data=model();if(!data)return;
    if(data.parts.length>=MODEL_ATELIER_LIMIT){status('Maximum of '+MODEL_ATELIER_LIMIT+' parts for this editor.',true);return;}
    checkpoint();
    const from=copy&&partById(selection);
    const p=from?structuredClone(from):{name:'New mesh',kind:'sphere',position:[0,2.6,.7],rotation:[0,0,0],scale:[.3,.3,.3],color:'#88daff',material:'gloss',group:'Custom'};
    p.id='atelier-local-'+Date.now().toString(36)+'-'+data.parts.length+'-'+Math.random().toString(36).slice(2,7);
    p.name=from?from.name+' copy':p.name;
    p.position=[p.position[0]+.3,p.position[1],p.position[2]+.2];
    data.parts.push(p);selection=p.id;signalEdited();
  }
  function removePart(){const data=model(),index=data?.parts.findIndex(p=>p.id===selection);if(index==null||index<0)return;
    if(data.parts.length<=1){status('Keep at least one mesh in the model.',true);return;}
    checkpoint();data.parts.splice(index,1);selection=null;signalEdited();
  }
  function cameraUpdate(){
    if(!camera)return;
    const h=Math.cos(orbit.pitch);
    camera.position.set(orbit.distance*h*Math.sin(orbit.yaw),2.45+orbit.distance*Math.sin(orbit.pitch),orbit.distance*h*Math.cos(orbit.yaw));
    camera.lookAt(0,2.35,0);
  }
  function point(e){
    const r=renderer.domElement.getBoundingClientRect();
    return {x:(e.clientX-r.left)/r.width*2-1,y:-((e.clientY-r.top)/r.height)*2+1};
  }
  function pointerDown(e){if(e.button!==0)return;pressed={x:e.clientX,y:e.clientY,yaw:orbit.yaw,pitch:orbit.pitch,moved:false};renderer.domElement.setPointerCapture?.(e.pointerId);}
  function pointerMove(e){
    if(!pressed)return;const dx=e.clientX-pressed.x,dy=e.clientY-pressed.y;
    if(Math.hypot(dx,dy)>5)pressed.moved=true;
    if(pressed.moved){orbit.yaw=pressed.yaw-dx*.008;orbit.pitch=Math.max(-.85,Math.min(1.1,pressed.pitch+dy*.006));cameraUpdate();}
  }
  function pointerUp(e){
    if(!pressed)return;const hit=!pressed.moved;pressed=null;
    if(!hit||!modelRoot)return;
    const pos=point(e);mouse.set(pos.x,pos.y);raycaster.setFromCamera(mouse,camera);
    const meshes=modelRoot.children.filter(o=>o.isMesh);
    const hits=raycaster.intersectObjects(meshes,false);select(hits[0]?.object?.userData?.atelierId||null);
  }
  function resize(){
    if(!renderer||!stage)return;
    const w=Math.max(200,stage.clientWidth),h=Math.max(180,stage.clientHeight);
    renderer.setSize(w,h,false);camera.aspect=w/h;camera.updateProjectionMatrix();
  }
  function loop(){
    if(!renderer)return;
    renderer.render(world,camera);raf=requestAnimationFrame(loop);
  }
  function open(){
    if(!model()){status('Open Model Atelier from Projects first.',true);return false;}
    ensurePanel();if(!panel.hidden)return true;
    returnFocus=document.activeElement;panel.hidden=false;
    stage=$m('Viewport');world=new THREE.Scene();world.background=new THREE.Color('#11172c');
    world.fog=new THREE.Fog('#11172c',17,29);
    world.add(new THREE.HemisphereLight(0xcff9ff,0x51435d,2.1));
    const sun=new THREE.DirectionalLight(0xffefdc,3);sun.position.set(5,8,8);world.add(sun);
    const back=new THREE.DirectionalLight(0x22c7f4,2.3);back.position.set(-7,5,-5);world.add(back);
    const floor=new THREE.Mesh(new THREE.CylinderGeometry(3.6,3.9,.16,56),new THREE.MeshStandardMaterial({color:0x222c48,metalness:.36,roughness:.59}));
    floor.position.y=-.07;world.add(floor);
    world.add(new THREE.GridHelper(7,18,0x566788,0x28354d));
    modelRoot=new THREE.Group();world.add(modelRoot);
    camera=new THREE.PerspectiveCamera(44,1,.1,100);cameraUpdate();
    renderer=new THREE.WebGLRenderer({antialias:true,alpha:false,powerPreference:'default'});
    renderer.setPixelRatio(Math.min(window.devicePixelRatio||1,1.65));
    renderer.domElement.style.touchAction='none';stage.append(renderer.domElement);
    raycaster=new THREE.Raycaster();mouse=new THREE.Vector2();
    renderer.domElement.addEventListener('pointerdown',pointerDown);
    renderer.domElement.addEventListener('pointermove',pointerMove);
    renderer.domElement.addEventListener('pointerup',pointerUp);
    renderer.domElement.addEventListener('pointercancel',()=>pressed=null);
    renderer.domElement.addEventListener('wheel',onWheel,{passive:false});
    resizeObserver=new ResizeObserver(resize);resizeObserver.observe(stage);
    resize();renderParts();refreshList();refreshInspector();loop();
    $m('Close').focus();
    status('Original reference study · orbit by dragging, scroll or pinch substitute with zoom buttons, tap to select.');
    return true;
  }
  function onWheel(e){e.preventDefault();orbit.distance=Math.min(22,Math.max(3.7,orbit.distance+Math.sign(e.deltaY)*.6));cameraUpdate();}
  function close(){
    if(!panel||panel.hidden)return;
    panel.hidden=true;cancelAnimationFrame(raf);raf=0;resizeObserver?.disconnect();resizeObserver=null;
    wipeModel();world?.traverse(o=>{if(o.isMesh){o.geometry?.dispose();o.material?.dispose();}});
    renderer?.dispose();renderer?.domElement?.remove();renderer=null;world=null;modelRoot=null;camera=null;
    if(returnFocus?.isConnected)returnFocus.focus();returnFocus=null;
  }
  function download(name,body,type){
    const blob=new Blob([body],{type});const url=URL.createObjectURL(blob);
    const link=document.createElement('a');link.href=url;link.download=name;document.body.append(link);link.click();link.remove();
    setTimeout(()=>URL.revokeObjectURL(url),1500);
  }
  function exportJSON(){if(!model())return;
    download('prism-jester.model.json',JSON.stringify({schema:'swyrl-model-atelier-v1',model:structuredClone(model())},null,2)+'\n','application/json');
    status('Editable model JSON exported.');
  }
  function exportOBJ(){
    if(!modelRoot)return;let vertexIndex=1;
    const lines=['# §wyrl§ Model Atelier v11.3','o Prism_Jester'];
    for(const mesh of modelRoot.children.filter(x=>x.isMesh)){
      const p=partById(mesh.userData.atelierId);if(!p)continue;
      mesh.updateMatrixWorld(true);
      const geometry=mesh.geometry,position=geometry.getAttribute('position'),indices=geometry.getIndex();
      lines.push('g '+safeName(p.name).replace(/[^a-zA-Z0-9_-]/g,'_'));
      for(let i=0;i<position.count;i++){
        const v=new THREE.Vector3().fromBufferAttribute(position,i).applyMatrix4(mesh.matrixWorld);
        lines.push('v '+v.x.toFixed(5)+' '+v.y.toFixed(5)+' '+v.z.toFixed(5));
      }
      const count=indices?indices.count:position.count;
      for(let i=0;i+2<count;i+=3){
        const a=(indices?indices.getX(i):i)+vertexIndex,b=(indices?indices.getX(i+1):i+1)+vertexIndex,c=(indices?indices.getX(i+2):i+2)+vertexIndex;
        lines.push('f '+a+' '+b+' '+c);
      }
      vertexIndex+=position.count;
    }
    download('prism-jester.mesh.obj',lines.join('\n')+'\n','text/plain');
    status('Triangulated OBJ exported. Materials remain editable in the native JSON.');
  }
  async function importJSON(file){
    if(!file||file.size>2_000_000){status('Model file must be JSON below 2 MB.',true);return;}
    try{
      const raw=JSON.parse(await file.text()),source=raw?.schema==='swyrl-model-atelier-v1'?raw.model:raw?.project?.modelAtelier;
      if(source?.schema!=='swyrl-model-atelier-v1'||!validParts(source.parts))throw Error('Invalid model schema, mesh limits, or transforms.');
      checkpoint();model().parts=structuredClone(source.parts);selection=null;signalEdited();status('Validated model imported. You can undo this import.');
    }catch(e){status('Import rejected: '+String(e.message||e),true);}
    $m('ImportFile').value='';
  }
  function ensurePanel(){
    if(panel)return;
    panel=document.createElement('section');panel.id='modelAtelierPanel';panel.className='model-atelier';panel.hidden=true;
    panel.setAttribute('role','dialog');panel.setAttribute('aria-modal','true');panel.setAttribute('aria-label','Model Atelier 3D model editor');
    panel.innerHTML='<div class="atelier-head"><strong>✦ §E Model Atelier <small>v11.3 · original reference study</small></strong><div class="atelier-actions"><button id="modelAtelierExport">Save model JSON</button><button id="modelAtelierOBJ">Export mesh OBJ</button><button id="modelAtelierClose">Close</button></div></div>'
      +'<div class="atelier-body"><div class="atelier-scene"><div id="modelAtelierViewport" class="atelier-viewport" aria-label="Interactive 3D model viewport"></div><div class="atelier-viewport-controls"><button id="modelAtelierZoomIn" aria-label="Zoom in">＋</button><button id="modelAtelierZoomOut" aria-label="Zoom out">−</button><button id="modelAtelierResetCamera">Reset view</button></div></div>'
      +'<aside class="atelier-inspector"><h3>Editable meshes</h3><p id="modelAtelierPartCount"></p><select id="modelAtelierParts" size="7" aria-label="Select model mesh"></select><div class="atelier-inspector-actions"><button id="modelAtelierAdd">Add sphere</button><button id="modelAtelierDuplicate">Duplicate</button><button id="modelAtelierDelete">Delete</button><button id="modelAtelierUndo">Undo</button><button id="modelAtelierRedo">Redo</button></div><strong id="modelAtelierSelectionName">Select a mesh</strong>'
      +'<div id="modelAtelierInspectorControls" hidden><label>Name<input id="modelAtelierName" maxlength="100"></label><div class="atelier-pair"><label>Shape<select id="modelAtelierKind"><option>sphere</option><option>box</option><option>cone</option><option>cylinder</option></select></label><label>Material<select id="modelAtelierMaterial"><option>matte</option><option>silk</option><option>gloss</option><option>metal</option><option>emissive</option></select></label></div><label>Color<input id="modelAtelierColor" type="color"></label>'
      +'<div class="atelier-transform"><strong>Position X/Y/Z</strong><input type="number" step=".05" id="modelAtelierposition0"><input type="number" step=".05" id="modelAtelierposition1"><input type="number" step=".05" id="modelAtelierposition2"><strong>Rotation X/Y/Z (radians)</strong><input type="number" step=".05" id="modelAtelierrotation0"><input type="number" step=".05" id="modelAtelierrotation1"><input type="number" step=".05" id="modelAtelierrotation2"><strong>Scale X/Y/Z</strong><input type="number" step=".05" min=".006" id="modelAtelierscale0"><input type="number" step=".05" min=".006" id="modelAtelierscale1"><input type="number" step=".05" min=".006" id="modelAtelierscale2"></div></div>'
      +'<label class="atelier-import">Import validated model JSON<input id="modelAtelierImportFile" type="file" accept=".json,application/json"></label><p class="atelier-disclaimer">Original modeled study, not an extracted or exact game asset. Model parts are editable; vertex sculpting, UV painting, skinning and animation remain future tools.</p></aside></div>'
      +'<div id="modelAtelierStatus" class="atelier-status" role="status" aria-live="polite"></div>';
    document.body.append(panel);
    const action=(id,fn)=>$m(id).addEventListener('click',fn);
    action('Close',close);action('Export',exportJSON);action('OBJ',exportOBJ);
    action('Add',()=>addPart(false));action('Duplicate',()=>addPart(true));action('Delete',removePart);
    action('Undo',()=>historyStep(true));action('Redo',()=>historyStep(false));
    action('ZoomIn',()=>{orbit.distance=Math.max(3.7,orbit.distance-.9);cameraUpdate();});
    action('ZoomOut',()=>{orbit.distance=Math.min(22,orbit.distance+.9);cameraUpdate();});
    action('ResetCamera',()=>{orbit={yaw:.3,pitch:.19,distance:9};cameraUpdate();});
    $m('Parts').addEventListener('change',e=>select(e.target.value));
    for(const key of ['name','color','kind','material'])$m(key[0].toUpperCase()+key.slice(1)).addEventListener('change',e=>applyField(key,null,e.target.value));
    for(const key of ['position','rotation','scale'])for(let axis=0;axis<3;axis++)
      $m(key+axis).addEventListener('change',e=>applyField(key,axis,e.target.value));
    $m('ImportFile').addEventListener('change',e=>importJSON(e.target.files?.[0]));
    panel.addEventListener('keydown',e=>{if(e.key==='Escape'){e.preventDefault();close();}else if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='z'&&e.target.tagName!=='INPUT'){e.preventDefault();historyStep(!e.shiftKey);}});
  }
  function syncProject(){
    const button=$m('Reopen');if(button)button.hidden=!model();
    if(panel&&!panel.hidden&&!model())close();
  }
  function install(){
    if($m('Reopen'))return;
    const button=document.createElement('button');button.id='modelAtelierReopen';button.type='button';
    button.className='model-atelier-open';button.textContent='✦ Edit 3D Model';button.hidden=true;
    button.addEventListener('click',open);document.body.append(button);syncProject();
  }
  return Object.freeze({open,close,install,syncProject,status:()=>({active:!!model(),open:!!panel&&!panel.hidden,count:model()?.parts?.length||0,selected:selection})});
})();
function loadModelAtelierStarter(force=false){
  if(dirty&&!force&&!confirm('Open Model Atelier and discard unsaved scene changes?'))return false;
  ModelAtelier.close();
  loadProject(structuredClone(MODEL_ATELIER_CANONICAL_PROJECT),{workspaceLocal:true});
  initializeHistory('Opened original 3D Model Atelier starter');markSaved();
  document.getElementById('projectHub')?.classList.remove('show');
  ModelAtelier.syncProject();ModelAtelier.open();
  toast('Model Atelier · Prism Jester · original 3D modeling study');
  return true;
}
const modelAtelierPreviousTemplate=createProjectFromTemplate;
createProjectFromTemplate=function(template,force=false){
  if(template==='model-atelier')return loadModelAtelierStarter(force);
  return modelAtelierPreviousTemplate(template,force);
};
const modelAtelierPreviousLoad=loadProject;
loadProject=function(...args){
  const result=modelAtelierPreviousLoad(...args);
  // Legacy applyProjectMeta copies only four standard fields. Restore the
  // model's native project extension, including edits from imported saves.
  const meta=args[0]?.project;
  if(meta?.kind==='model-atelier'&&meta.modelAtelier?.schema==='swyrl-model-atelier-v1')
    currentProject={...currentProject,...structuredClone(meta)};
  ModelAtelier.syncProject();
  return result;
};
ModelAtelier.install();
window.SWYRL_ENGINE_MODEL_ATELIER=Object.freeze({open:()=>ModelAtelier.open(),loadStarter:()=>loadModelAtelierStarter(),status:()=>ModelAtelier.status()});
if(new URLSearchParams(location.search).get('project')==='model-atelier')
  queueMicrotask(()=>loadModelAtelierStarter());
