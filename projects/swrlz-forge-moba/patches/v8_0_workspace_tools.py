"""Reusable project-owned workstations, file notebooks, and native world signs.

Applies to the v7.9 engine without changing its version or canonical scene.
"""


def _once(html, old, new):
    if html.count(old) != 1:
        raise RuntimeError("workspace patch expected one anchor: " + old[:120])
    return html.replace(old, new, 1)


CSS = r"""
.workspace-nearby{position:absolute;bottom:48px;left:50%;transform:translateX(-50%);z-index:42;display:none;max-width:90%;padding:10px 18px;border:1px solid #6cd4be;border-radius:12px;background:#081a21ee;color:#e4fff7;font-weight:700}
.workspace-backdrop{position:fixed;inset:0;z-index:200;display:none;align-items:center;justify-content:center;padding:16px;background:#030812bd;backdrop-filter:blur(5px)}
.workspace-backdrop.open{display:flex}.workspace-window{width:min(1050px,96vw);height:min(740px,90vh);display:flex;flex-direction:column;overflow:hidden;border:1px solid #54718b;border-radius:16px;background:#0b1622;color:#e7f2ff;box-shadow:0 20px 80px #0008}
.workspace-window header{display:flex;align-items:center;gap:12px;padding:16px;border-bottom:1px solid #263c50}.workspace-window header h2{margin:0;font-size:19px;flex:1}.workspace-window header button{padding:9px 14px}
.workspace-description{margin:0;padding:10px 16px;color:#a5bbd0;font-size:12px}.workspace-actions{display:flex;flex-wrap:wrap;gap:7px;padding:0 16px 12px}.workspace-actions button,.workspace-actions a{padding:8px 11px;border:1px solid #385570;border-radius:8px;background:#162a3b;color:#e7f2ff;text-decoration:none;font:600 12px system-ui}
.workspace-editor{display:grid;grid-template-columns:190px minmax(0,1fr);min-height:0;flex:1;border-top:1px solid #263c50}.workspace-files{overflow:auto;padding:10px;border-right:1px solid #263c50}.workspace-file{display:block;width:100%;text-align:left;padding:10px;margin-bottom:5px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.workspace-file.active{border-color:var(--workspace-accent,#7be0c5);background:#203a4a}
.workspace-document{display:flex;flex-direction:column;min-height:0;padding:12px;gap:9px}.workspace-filename{width:100%;padding:9px 10px!important}.workspace-text{width:100%;flex:1;min-height:100px;resize:none;padding:14px!important;font:13px/1.65 ui-monospace,SFMono-Regular,Consolas,monospace!important;tab-size:2;white-space:pre;background:#07111b!important;color:#d7eaf6!important}
.workspace-notes-label{font-size:11px;color:#9bb4c9}.workspace-notes{height:70px;resize:vertical;padding:8px!important;font:12px/1.5 system-ui!important}.workspace-save-state{padding:9px 16px;border-top:1px solid #263c50;font-size:11px;color:#8da7bc}.workspace-inspector .field{margin-bottom:8px}.workspace-inspector .row button{flex:1}
@media(max-width:640px){.workspace-backdrop{padding:6px}.workspace-window{width:100%;height:94vh}.workspace-window header{padding:12px}.workspace-window header h2{font-size:16px}.workspace-editor{grid-template-columns:125px minmax(0,1fr)}.workspace-document{padding:8px}.workspace-files{padding:6px}.workspace-actions{padding:0 10px 10px;gap:5px}.workspace-text{font-size:12px!important}}
"""


JS = r"""
// Workspaces contain editable text, never executable engine code.
let workspacePanelOpen=false,workspacePanelActor=null,workspaceActiveFileId=null,workspaceSession=null;
let workspaceLocalAllowed=false,workspaceHydrated=new Set(),workspacePersistTimer=null,workspaceNearbyActor=null,workspaceScanAt=0,workspacePanelDirty=false,workspaceHistoryPending=false;
function workspaceClone(value){return value==null?value:JSON.parse(JSON.stringify(value))}
function workspaceAccent(value){return /^#[0-9a-f]{6}$/i.test(String(value||''))?String(value):'#79dbc3'}
function normalizeWorkspace(config={}){
  const kind=['code','notes','archive','chat','link'].includes(config.kind)?config.kind:'code';
  let url='';try{const parsed=new URL(config.url||'');if(['https:','http:'].includes(parsed.protocol))url=parsed.href}catch{}
  if(kind==='chat'&&!url)url='https://kamiloki-swyrlz.hf.space/';
  const offset=Array.isArray(config.labelOffset)&&config.labelOffset.length===3&&config.labelOffset.every(Number.isFinite)?config.labelOffset:[0,3,0];
  return {title:String(config.title||'Project Workspace').slice(0,100),kind,accent:workspaceAccent(config.accent),url,labelOffset:[...offset],labelWidth:Math.max(.5,Math.min(12,Number(config.labelWidth)||3.4)),radius:Math.max(1,Math.min(8,Number(config.radius)||3.5))};
}
function normalizeWorkspaceStation(value={}){
  const files=Array.isArray(value.files)?value.files:[];
  return {files:files.filter(f=>f&&typeof f==='object').slice(0,100).map((f,i)=>({id:String(f.id||'file-'+i),name:String(f.name||'untitled.txt').slice(0,120),content:String(f.content||'').slice(0,1000000)})),notes:String(value.notes||'').slice(0,1000000),updatedAt:Number(value.updatedAt)||0};
}
function normalizeWorkspaceProject(value){
  const result={schema:'swyrl-workspaces-v1',stations:{}};
  if(value?.stations&&typeof value.stations==='object'&&!Array.isArray(value.stations))for(const [id,v] of Object.entries(value.stations)){if(!['__proto__','constructor','prototype'].includes(id)&&v&&typeof v==='object')result.stations[id]=normalizeWorkspaceStation(v)}
  return result;
}
function ensureWorkspaceProject(){if(currentProject.workspaces?.schema!=='swyrl-workspaces-v1'||!currentProject.workspaces.stations||Array.isArray(currentProject.workspaces.stations))currentProject.workspaces=normalizeWorkspaceProject(currentProject.workspaces);return currentProject.workspaces}
function workspaceStorageKey(id){return 'swyrl.workspace.v1:'+encodeURIComponent(currentProject.canonicalId||currentProject.name||'untitled')+':'+encodeURIComponent(id)}
function workspaceStation(a){
  const p=ensureWorkspaceProject(),id=a.userData.id;
  if(!workspaceHydrated.has(id)){
    const existing=Object.hasOwn(p.stations,id)?p.stations[id]:null;if(existing)p.stations[id]=normalizeWorkspaceStation(existing);
    if(workspaceLocalAllowed){try{const cached=JSON.parse(localStorage.getItem(workspaceStorageKey(id))||'null');if(cached?.schema==='swyrl-workspace-local-v1'&&cached.station&&(!existing||(cached.station.updatedAt||0)>(existing.updatedAt||0)))p.stations[id]=normalizeWorkspaceStation(cached.station)}catch{}}
    workspaceHydrated.add(id);
  }
  if(!p.stations[id])p.stations[id]={files:[{id:uid(),name:a.userData.workspace.kind==='code'?'main.js':'notes.md',content:''}],notes:'',updatedAt:0};
  return p.stations[id];
}
function hydrateWorkspaceStations(){for(const a of actors)if(a.userData.workspace&&hasComponent(a,'Workspace'))workspaceStation(a)}
function commitWorkspaceChanges(){if(!workspacePanelDirty)return;workspacePanelDirty=false;if(playing||simulating)workspaceHistoryPending=true;else commitTransaction('Edit Workspace Documents')}
function commitPendingWorkspaceChanges(){if(workspaceHistoryPending){workspaceHistoryPending=false;commitTransaction('Edit Workspace Documents')}}
function persistWorkspaceNow(){
  clearTimeout(workspacePersistTimer);workspacePersistTimer=null;if(!workspacePanelActor)return;
  const station=workspaceStation(workspacePanelActor);if(workspacePanelDirty||!station.updatedAt)station.updatedAt=Date.now();
  try{localStorage.setItem(workspaceStorageKey(workspacePanelActor.userData.id),JSON.stringify({schema:'swyrl-workspace-local-v1',station}));$('workspaceSaveState').textContent='Draft saved on this device · Save Project includes all workspace files.'}
  catch{$('workspaceSaveState').textContent='Draft is in this project · Save Project to keep a downloadable copy.'}
}
function scheduleWorkspaceSave(){workspacePanelDirty=true;markDirty();clearTimeout(workspacePersistTimer);workspacePersistTimer=setTimeout(persistWorkspaceNow,350)}
function resetWorkspaceState(allowLocal=false){closeWorkspacePanel(false);workspaceHistoryPending=false;workspaceHydrated=new Set();workspaceLocalAllowed=allowLocal;workspaceNearbyActor=null;workspaceScanAt=0}
function workspaceLabelTexture(title,subtitle,accent,width=1024,height=256){
  const c=document.createElement('canvas');c.width=width;c.height=height;const ctx=c.getContext('2d');
  ctx.fillStyle='#081522';ctx.fillRect(0,0,width,height);ctx.fillStyle=workspaceAccent(accent);ctx.fillRect(0,0,12,height);ctx.strokeStyle='#496278';ctx.lineWidth=4;ctx.strokeRect(2,2,width-4,height-4);
  ctx.fillStyle='#edf8ff';ctx.font='bold 62px system-ui';ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText(String(title).slice(0,42),width/2,height*.41,width-70);
  ctx.fillStyle=workspaceAccent(accent);ctx.font='28px system-ui';ctx.fillText(String(subtitle).slice(0,75),width/2,height*.76,width-70);
  const t=new THREE.CanvasTexture(c);t.colorSpace=THREE.SRGBColorSpace;return t;
}
function removeWorkspaceLabel(a){const old=a.getObjectByName('WorkspaceStationLabel');if(old){old.parent.remove(old);old.material.map?.dispose();old.material.dispose()}}
function refreshWorkspaceLabel(a){
  removeWorkspaceLabel(a);if(!a.userData.workspace||!hasComponent(a,'Workspace'))return;
  const w=normalizeWorkspace(a.userData.workspace);a.userData.workspace=w;
  const map=workspaceLabelTexture(w.title,w.kind==='chat'?'CHAT PORTAL · OPEN WORKSPACE':w.kind.toUpperCase()+' WORKSPACE · E / OPEN',w.accent);
  const sprite=new THREE.Sprite(new THREE.SpriteMaterial({map,depthTest:true,depthWrite:false}));sprite.name='WorkspaceStationLabel';sprite.position.fromArray(w.labelOffset);sprite.scale.set(w.labelWidth,w.labelWidth*.25,1);sprite.userData.editorOnly=true;a.add(sprite);
}
function configureWorkspace(id,config={}){
  const a=actors.find(x=>x.userData.id===id);if(!a||a.userData.actorType==='ground')return false;
  beginTransaction('Configure Workspace '+a.name);a.userData.workspace=normalizeWorkspace({...a.userData.workspace,...config});if(!hasComponent(a,'Workspace'))a.userData.components.push('Workspace');refreshWorkspaceLabel(a);commitTransaction('Configure Workspace '+a.name);if(a===selected)syncWorkspaceInspector();return workspaceClone(a.userData.workspace);
}
function makeWorkspaceSign(name='Workspace Sign',text='Welcome',opts={},baked=true){
  const data={text:String(text||'Welcome').slice(0,250),accent:workspaceAccent(opts.accent),width:Math.max(.5,Math.min(16,Number(opts.width)||4)),height:Math.max(.25,Math.min(8,Number(opts.height)||1.15))};
  const g=new THREE.Group(),parts=data.text.split('\n'),map=workspaceLabelTexture(parts[0],parts.slice(1).join(' · '),data.accent);
  const geometry=new THREE.PlaneGeometry(data.width,data.height),material=new THREE.MeshBasicMaterial({map,side:THREE.FrontSide});
  for(const [name,side] of [['WorkspaceSignFace',1],['WorkspaceSignBack',-1]]){const mesh=new THREE.Mesh(geometry,material);mesh.name=name;mesh.position.z=side*.012;if(side<0)mesh.rotation.y=Math.PI;mesh.userData.helper=true;g.add(mesh);}
  const a=markActor(g,'workspaceSign',{name,baked,colliderRadius:0,folder:opts.folder||'Workspace/Signs',components:['Transform','Scene','StaticMesh'],blueprintClass:'BP_WorkspaceSign',tags:['workspace-sign']});a.userData.sign=data;return a;
}
function createWorkspaceSign(name,text,opts={}){
  beginTransaction('Create Workspace Sign');const a=makeWorkspaceSign(name,text,opts,true);if(opts.position)a.position.fromArray(opts.position);if(opts.rotation)a.rotation.set(...opts.rotation);if(opts.scale)a.scale.fromArray(opts.scale);a.userData.spawnPos=a.position.toArray();rebuildHierarchy();selectActor(a);commitTransaction('Create Workspace Sign');return a.userData.id;
}
function updateWorkspaceSign(id,config={}){
  const a=actors.find(x=>x.userData.id===id);if(a?.userData.actorType!=='workspaceSign')return false;
  beginTransaction('Edit Workspace Sign');const s={...a.userData.sign,...config};s.text=String(s.text||'Welcome').slice(0,250);s.accent=workspaceAccent(s.accent);s.width=Math.max(.5,Math.min(16,Number(s.width)||4));s.height=Math.max(.25,Math.min(8,Number(s.height)||1.15));a.userData.sign=s;
  const faces=['WorkspaceSignFace','WorkspaceSignBack'].map(name=>a.getObjectByName(name)).filter(Boolean);
  if(faces.length){for(const geometry of new Set(faces.map(face=>face.geometry)))geometry.dispose();for(const map of new Set(faces.map(face=>face.material.map).filter(Boolean)))map.dispose();const text=s.text.split('\n'),geometry=new THREE.PlaneGeometry(s.width,s.height),map=workspaceLabelTexture(text[0],text.slice(1).join(' · '),s.accent);for(const face of faces){face.geometry=geometry;face.material.map=map;face.material.needsUpdate=true;}}commitTransaction('Edit Workspace Sign');return true;
}
function workspaceSelectedActor(){return selected&&hasComponent(selected,'Workspace')?selected:selected?.userData.actorType==='group'?groupDescendants(selected).find(a=>hasComponent(a,'Workspace'))||null:null}
function clearWorkspaceInput(){keys.clear();heroJumpQueued=false;hoverUpHeld=false;hoverDownHeld=false;resetStick($('moveStick'),fpMove);resetStick($('lookStick'),fpLook)}
function renderWorkspaceFiles(){
  if(!workspacePanelActor)return;const station=workspaceStation(workspacePanelActor),list=$('workspaceFiles');list.replaceChildren();
  if(!station.files.some(x=>x.id===workspaceActiveFileId))workspaceActiveFileId=station.files[0]?.id||null;
  for(const f of station.files){const b=document.createElement('button');b.type='button';b.className='workspace-file'+(f.id===workspaceActiveFileId?' active':'');b.textContent=f.name;b.onclick=()=>{workspaceActiveFileId=f.id;renderWorkspaceFiles()};list.appendChild(b)}
  const f=station.files.find(x=>x.id===workspaceActiveFileId);$('workspaceFilename').value=f?.name||'';$('workspaceText').value=f?.content||'';$('workspaceNotes').value=station.notes;$('workspaceFilename').disabled=!f;$('workspaceText').disabled=!f;$('workspaceDownloadFile').disabled=!f;$('workspaceDeleteFile').disabled=!f;
}
function openWorkspacePanel(id){
  const a=actors.find(x=>x.userData.id===id);if(!a?.userData.workspace||!hasComponent(a,'Workspace'))return false;
  if(workspacePanelOpen){persistWorkspaceNow();commitWorkspaceChanges()}else workspaceSession={playing,simulating,paused};
  workspacePanelActor=a;workspacePanelOpen=true;workspacePanelDirty=false;workspaceActiveFileId=null;clearWorkspaceInput();if(playing||simulating)paused=true;if(document.pointerLockElement)document.exitPointerLock?.();setSessionButtons();
  const w=a.userData.workspace;$('workspaceTitle').textContent=w.title;$('workspacePanel').style.setProperty('--workspace-accent',w.accent);$('workspaceDescription').textContent=w.kind==='chat'?'Keep project notes here, or open the existing §wyrlz chat in a new tab.':'Your project files and notes live with this station. Code is editable text.';
  const link=$('workspaceExternalLink');link.hidden=!w.url;link.href=w.url||'#';link.textContent=w.kind==='chat'?'Open §wyrlz Chat':'Open linked workspace';$('workspaceBackdrop').classList.add('open');$('workspaceNearby').style.display='none';renderWorkspaceFiles();$('workspaceSaveState').textContent='Changes stay with this project · Save Project includes workspace files.';setTimeout(()=>$('workspaceText').focus(),0);return true;
}
function closeWorkspacePanel(resume=true){
  if(!workspacePanelOpen)return;persistWorkspaceNow();commitWorkspaceChanges();workspacePanelOpen=false;workspacePanelActor=null;$('workspaceBackdrop')?.classList.remove('open');clearWorkspaceInput();
  if(resume&&workspaceSession&&playing===workspaceSession.playing&&simulating===workspaceSession.simulating)paused=workspaceSession.paused;workspaceSession=null;setSessionButtons();$('viewport')?.focus();
}
function workspaceActorVisible(a){let node=a;while(node){if(node.visible===false)return false;node=node.parent}return true}
function nearestWorkspace(){
  const h=heroActor();if(!h)return null;scene.updateMatrixWorld(true);const hp=new THREE.Vector3();h.getWorldPosition(hp);let near=null,best=Infinity;
  for(const a of actors){if(!hasComponent(a,'Workspace')||!a.userData.workspace||!a.userData.baked||!workspaceActorVisible(a))continue;const p=new THREE.Vector3();a.getWorldPosition(p);const d=hp.distanceTo(p);if(d<=a.userData.workspace.radius&&d<best){near=a;best=d}}
  return near;
}
function updateWorkspaceInteraction(t){
  if(t<workspaceScanAt)return;workspaceScanAt=t+.18;
  workspaceNearbyActor=playing&&!paused&&!workspacePanelOpen?nearestWorkspace():null;const b=$('workspaceNearby');if(!b)return;b.style.display=workspaceNearbyActor?'block':'none';if(workspaceNearbyActor)b.textContent='E · Open '+workspaceNearbyActor.userData.workspace.title;
}
function syncWorkspaceInspector(){
  if(!$('workspaceConfigTitle'))return;const a=workspaceSelectedActor(),w=normalizeWorkspace(a?.userData.workspace||{title:selected?.name||'Project Workspace'});
  $('workspaceConfigTitle').value=w.title;$('workspaceConfigKind').value=w.kind;$('workspaceConfigAccent').value=w.accent;$('workspaceConfigUrl').value=w.url;$('workspaceOpenSelected').disabled=!a;$('workspaceConfigureSelected').disabled=!selected||selected.userData.actorType==='ground';
  $('workspaceSignFields').hidden=selected?.userData.actorType!=='workspaceSign';$('workspaceSignText').value=selected?.userData.sign?.text||'';
}
function installWorkspaceTools(){
  const option=document.createElement('option');option.value='Workspace';option.textContent='Workspace';$('addComponentSelect').appendChild(option);
  const details=document.createElement('details');details.className='detail-box workspace-inspector';details.innerHTML='<summary>Workspace Station / Sign</summary><div><div class="field"><label>Station title</label><input id="workspaceConfigTitle" maxlength="100"></div><div class="field"><label>Kind</label><select id="workspaceConfigKind"><option value="code">Code</option><option value="notes">Notes</option><option value="archive">Archive</option><option value="chat">Chat portal</option><option value="link">Link</option></select></div><div class="field"><label>Accent</label><input id="workspaceConfigAccent" type="color" value="#79dbc3"></div><div class="field"><label>Optional link</label><input id="workspaceConfigUrl" type="url" placeholder="https://"></div><div class="row"><button id="workspaceConfigureSelected">Configure</button><button id="workspaceOpenSelected">Open Workspace</button></div><div id="workspaceSignFields" hidden><div class="field"><label>Sign text (two lines)</label><textarea id="workspaceSignText" maxlength="250" rows="3"></textarea></div><button id="workspaceUpdateSign">Update sign</button></div></div>';$('inspector').appendChild(details);
  $('workspaceConfigureSelected').onclick=()=>{const a=workspaceSelectedActor()||selected;if(a)configureWorkspace(a.userData.id,{title:$('workspaceConfigTitle').value,kind:$('workspaceConfigKind').value,accent:$('workspaceConfigAccent').value,url:$('workspaceConfigUrl').value})};$('workspaceOpenSelected').onclick=()=>{const a=workspaceSelectedActor();if(a)openWorkspacePanel(a.userData.id)};
  $('workspaceUpdateSign').onclick=()=>{if(selected)updateWorkspaceSign(selected.userData.id,{text:$('workspaceSignText').value,accent:$('workspaceConfigAccent').value})};
  const nearby=document.createElement('button');nearby.id='workspaceNearby';nearby.className='workspace-nearby';nearby.type='button';nearby.onclick=()=>{if(workspaceNearbyActor)openWorkspacePanel(workspaceNearbyActor.userData.id)};$('viewport').parentElement.appendChild(nearby);
  const backdrop=document.createElement('div');backdrop.id='workspaceBackdrop';backdrop.className='workspace-backdrop';backdrop.innerHTML='<section id="workspacePanel" class="workspace-window" role="dialog" aria-modal="true" aria-labelledby="workspaceTitle"><header><h2 id="workspaceTitle">Workspace</h2><button id="workspacePanelClose" type="button">Close / Resume</button></header><p id="workspaceDescription" class="workspace-description"></p><div class="workspace-actions"><button id="workspaceNewFile">New file</button><button id="workspaceDeleteFile">Delete file</button><button id="workspaceDownloadFile">Download file</button><button id="workspaceExport">Export workspace</button><button id="workspaceImport">Import workspace</button><a id="workspaceExternalLink" target="_blank" rel="noopener noreferrer" hidden>Open link</a><input id="workspaceImportFile" type="file" accept=".json,application/json" hidden></div><div class="workspace-editor"><nav id="workspaceFiles" class="workspace-files" aria-label="Workspace files"></nav><div class="workspace-document"><input id="workspaceFilename" class="workspace-filename" aria-label="File name" maxlength="120"><textarea id="workspaceText" class="workspace-text" aria-label="File content" spellcheck="false" maxlength="1000000"></textarea><label for="workspaceNotes" class="workspace-notes-label">Station notes</label><textarea id="workspaceNotes" class="workspace-notes" aria-label="Station notes" maxlength="1000000"></textarea></div></div><div id="workspaceSaveState" class="workspace-save-state" aria-live="polite"></div></section>';document.body.appendChild(backdrop);
  $('workspacePanelClose').onclick=()=>closeWorkspacePanel();backdrop.addEventListener('pointerdown',e=>{if(e.target===backdrop)closeWorkspacePanel()});
  const active=()=>workspacePanelActor?workspaceStation(workspacePanelActor).files.find(x=>x.id===workspaceActiveFileId):null;
  $('workspaceFilename').oninput=()=>{const f=active();if(!f)return;f.name=$('workspaceFilename').value||'untitled.txt';for(const [i,b] of [...$('workspaceFiles').children].entries())b.textContent=workspaceStation(workspacePanelActor).files[i].name;scheduleWorkspaceSave()};
  $('workspaceText').oninput=()=>{const f=active();if(f){f.content=$('workspaceText').value;scheduleWorkspaceSave()}};$('workspaceNotes').oninput=()=>{if(workspacePanelActor){workspaceStation(workspacePanelActor).notes=$('workspaceNotes').value;scheduleWorkspaceSave()}};
  $('workspaceText').addEventListener('keydown',e=>{if(e.key==='Tab'&&!e.shiftKey){e.preventDefault();const el=e.target,start=el.selectionStart,end=el.selectionEnd;el.setRangeText('  ',start,end,'end');el.dispatchEvent(new Event('input',{bubbles:true}))}});
  $('workspaceNewFile').onclick=()=>{if(!workspacePanelActor)return;const station=workspaceStation(workspacePanelActor);if(station.files.length>=100){toast('This station already has 100 files');return}const name=prompt('File name','untitled-'+(station.files.length+1)+'.txt');if(!name?.trim())return;const f={id:uid(),name:name.trim().slice(0,120),content:''};station.files.push(f);workspaceActiveFileId=f.id;renderWorkspaceFiles();scheduleWorkspaceSave();$('workspaceFilename').focus()};
  $('workspaceDeleteFile').onclick=()=>{const f=active();if(!f||!confirm('Delete '+f.name+'?'))return;const station=workspaceStation(workspacePanelActor);station.files=station.files.filter(x=>x.id!==f.id);workspaceActiveFileId=null;renderWorkspaceFiles();scheduleWorkspaceSave()};
  $('workspaceDownloadFile').onclick=()=>{const f=active();if(f)saveBlob(f.name.replace(/[\\/]/g,'_')||'untitled.txt',f.content,'text/plain;charset=utf-8')};
  $('workspaceExport').onclick=()=>{if(!workspacePanelActor)return;persistWorkspaceNow();saveBlob(safeProjectName()+'-'+workspacePanelActor.userData.id+'.workspace.json',JSON.stringify({schema:'swyrl-workspace-v1',projectId:currentProject.canonicalId||currentProject.name,stationId:workspacePanelActor.userData.id,station:workspaceStation(workspacePanelActor)},null,2),'application/json')};
  $('workspaceImport').onclick=()=>$('workspaceImportFile').click();$('workspaceImportFile').onchange=async()=>{const input=$('workspaceImportFile'),file=input.files?.[0],actor=workspacePanelActor;input.value='';if(!file||!actor)return;try{if(file.size>10000000)throw new Error('Workspace file is too large');const data=JSON.parse(await file.text());if(data.schema!=='swyrl-workspace-v1'||!data.station||!Array.isArray(data.station.files))throw new Error('Choose an exported workspace JSON file');if(data.station.files.length>100||data.station.files.some(f=>!f||typeof f!=='object'||String(f.content||'').length>1000000)||String(data.station.notes||'').length>1000000)throw new Error('Workspace supports 100 files, with one million characters per document');if(!workspacePanelOpen||workspacePanelActor!==actor)return;ensureWorkspaceProject().stations[actor.userData.id]=normalizeWorkspaceStation(data.station);workspaceActiveFileId=null;renderWorkspaceFiles();scheduleWorkspaceSave();persistWorkspaceNow();toast('Workspace imported')}catch(e){toast(e.message)}};
  window.addEventListener('keydown',e=>{if(workspacePanelOpen){if(e.key==='Escape'){e.preventDefault();e.stopImmediatePropagation();closeWorkspacePanel()}else if(e.key==='Tab'){const nodes=[...$('workspacePanel').querySelectorAll('button,input,textarea,a[href]')].filter(n=>!n.disabled&&!n.hidden&&n.offsetParent!==null),first=nodes[0],last=nodes.at(-1);if(e.shiftKey&&document.activeElement===first){e.preventDefault();last?.focus()}else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first?.focus()}}return}const tag=document.activeElement?.tagName;if(['INPUT','SELECT','TEXTAREA'].includes(tag)||document.activeElement?.isContentEditable)return;if(playing&&!paused&&e.key.toLowerCase()==='e'){const a=nearestWorkspace();if(a){e.preventDefault();e.stopImmediatePropagation();openWorkspacePanel(a.userData.id)}}},true);
}
installWorkspaceTools();
"""


def apply(html):
    s = _once(html, "</style>\n</head>", CSS + "\n</style>\n</head>")
    s = _once(s, "function applyProjectMeta(meta={}){", "function applyProjectMeta(meta={}){\n  const workspaceData=normalizeWorkspaceProject(meta.workspaces);")
    s = _once(s, "  const nameEl=$('currentProjectName');if(nameEl)nameEl.textContent=currentProject.name;", "  currentProject.workspaces=workspaceData;if(meta.canonicalId)currentProject.canonicalId=meta.canonicalId;\n  const nameEl=$('currentProjectName');if(nameEl)nameEl.textContent=currentProject.name;")
    s = _once(s, "function projectData(){\n  return {", "function projectData(){\n  hydrateWorkspaceStations();\n  return {")
    s = _once(s, "function loadProject(p, options={}){", "function loadProject(p, options={}){\n  resetWorkspaceState(options.workspaceLocal===true);")
    s = _once(s, "  loadProject(p);", "  loadProject(p,{workspaceLocal:true});")
    s = _once(s, "  currentProject={...p.project};", "  currentProject={...p.project,workspaces:currentProject.workspaces};")
    s = _once(s, "    position:a.position.toArray(), rotation:[a.rotation.x,a.rotation.y,a.rotation.z], scale:a.scale.toArray(),", "    workspace:a.userData.workspace?workspaceClone(a.userData.workspace):null,sign:a.userData.sign?workspaceClone(a.userData.sign):null,\n    position:a.position.toArray(), rotation:[a.rotation.x,a.rotation.y,a.rotation.z], scale:a.scale.toArray(),")
    s = _once(s, "  if(d.type==='group') o=makeGroupActor(d.name||'Group',d.baked!==false);", "  if(d.type==='group') o=makeGroupActor(d.name||'Group',d.baked!==false);\n  if(d.type==='workspaceSign')o=makeWorkspaceSign(d.name,d.sign?.text||d.name,d.sign||{},d.baked!==false);")
    s = _once(s, "  o.scale.set(...(d.scale||[1,1,1]));", "  o.scale.set(...(d.scale||[1,1,1]));\n  if(d.workspace){o.userData.workspace=normalizeWorkspace(d.workspace);if(!(d.components||[]).includes('Workspace'))d.components=[...(d.components||o.userData.components),'Workspace'];}")
    s = _once(s, "  applyGhostVisual(o);\n  return o;", "  applyGhostVisual(o);\n  refreshWorkspaceLabel(o);\n  return o;")
    s = _once(s, "  if(type==='denWorkbench') o = makeDenStructure('creatorAlcove',[0,0,0],false,'Ghost Creator Alcove','#61cfff');", "  if(type==='denWorkbench') o = makeDenStructure('creatorAlcove',[0,0,0],false,'Ghost Creator Alcove','#61cfff');\n  if(type==='workspaceSign')o=makeWorkspaceSign('Workspace Sign','Project Workspace',{accent:'#79dbc3'},false);")
    s = _once(s, "const ASSET_LIBRARY=[", "const ASSET_LIBRARY=[\n  {id:'workspaceSign',name:'World Sign',path:'/Engine/Workspace',desc:'Editable project-owned wayfinding sign'},")
    s = _once(s, "  $('stateBadge').textContent=selected.userData.baked?'BAKED':'GHOST'; $('teamBadge').textContent=selected.userData.team[0].toUpperCase()+selected.userData.team.slice(1); $('classBadge').textContent=selected.userData.blueprintClass||'Actor'; renderComponents();", "  $('stateBadge').textContent=selected.userData.baked?'BAKED':'GHOST'; $('teamBadge').textContent=selected.userData.team[0].toUpperCase()+selected.userData.team.slice(1); $('classBadge').textContent=selected.userData.blueprintClass||'Actor'; renderComponents();syncWorkspaceInspector();")
    s = _once(s, "  if(name==='LaunchPad') actor.userData.launchStrength = actor.userData.launchStrength||8;", "  if(name==='LaunchPad') actor.userData.launchStrength = actor.userData.launchStrength||8;\n  if(name==='Workspace'){actor.userData.workspace=normalizeWorkspace(actor.userData.workspace||{title:actor.name});refreshWorkspaceLabel(actor);}")
    s = _once(s, "  actor.userData.components = (actor.userData.components||[]).filter(x=>x!==name);", "  actor.userData.components = (actor.userData.components||[]).filter(x=>x!==name);\n  if(name==='Workspace'){delete actor.userData.workspace;removeWorkspaceLabel(actor);syncWorkspaceInspector();}")
    s = _once(s, "function stopSession(){", "function stopSession(){\n  closeWorkspacePanel(false);")
    s = _once(s, "editorLog('Editor session stopped','ok');toast('Returned to editor.');", "editorLog('Editor session stopped','ok');toast('Returned to editor.');commitPendingWorkspaceChanges();")
    s = _once(s, "function beginPlay(fromHere=null){", "function beginPlay(fromHere=null){\n  closeWorkspacePanel(false);")
    s = _once(s, "function beginSimulate(){", "function beginSimulate(){\n  closeWorkspacePanel(false);")
    s = _once(s, "  if(!playing||document.pointerLockElement!==$('viewport'))return;", "  if(workspacePanelOpen||!playing||document.pointerLockElement!==$('viewport'))return;")
    s = _once(s, "$('viewport').addEventListener('pointerdown', e=>{", "$('viewport').addEventListener('pointerdown', e=>{\n  if(workspacePanelOpen)return;")
    s = _once(s, "  if(['INPUT','SELECT'].includes(tag)) return;", "  if(workspacePanelOpen||['INPUT','SELECT','TEXTAREA'].includes(tag)||document.activeElement?.isContentEditable) return;")
    s = _once(s, "function updateHero(dt, t){", "function updateHero(dt, t){\n  if(workspacePanelOpen)return;")
    s = _once(s, "  if(runtimeActive&&!paused){", "  if(runtimeActive&&!paused&&!workspacePanelOpen){")
    s = _once(s, "renderer.render(scene,camera);\n}", "updateWorkspaceInteraction(t);renderer.render(scene,camera);\n}")
    s = _once(s, "window.SWRLZ_FORGE_BUILD=", JS + "\nwindow.SWRLZ_FORGE_BUILD=")
    s = _once(s, "window.SWRLZ_FORGE_AGENT={", "window.SWRLZ_FORGE_AGENT={\n  configureWorkspace:(id,config)=>configureWorkspace(id,config),\n  openWorkspace:(id)=>openWorkspacePanel(id),\n  createSign:(name,text,opts)=>createWorkspaceSign(name,text,opts),\n  updateSign:(id,config)=>updateWorkspaceSign(id,config),")
    return s
