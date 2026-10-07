"""Project-owned, support-validated teleport zones and native authoring UI.

No canonical project or release version is embedded here. Zones travel with
project metadata; movement is runtime-only and native Stop restores the pawn.
"""

def _once(s, old, new):
    if s.count(old) != 1:
        raise RuntimeError('v8.3 teleport expected one anchor: ' + old[:140])
    return s.replace(old, new, 1)

CSS = r'''
<style id="teleportZoneStyles">
.zone-menu-button{position:absolute;z-index:80;top:14px;left:14px;padding:10px 16px;border:1px solid #7197bc;border-radius:11px;background:#0a192ce8;color:#e6f2ff;font-weight:700;display:none}
.app.runtime-play .zone-menu-button{display:block}.zone-backdrop{position:fixed;inset:0;z-index:220;background:#030a14cf;display:none;align-items:center;justify-content:center;padding:18px;backdrop-filter:blur(5px)}.zone-backdrop.open{display:flex}
.zone-dialog{width:min(690px,95vw);max-height:88vh;overflow:auto;background:#0c1727;border:1px solid #567292;border-radius:18px;color:#eaf4ff;box-shadow:0 24px 90px #0009;padding:20px}.zone-dialog header{display:flex;align-items:center;gap:12px}.zone-dialog h2{font-size:22px;margin:0;flex:1}.zone-dialog p{color:#a3bad0;font-size:13px;line-height:1.5}.zone-destinations{display:grid;grid-template-columns:1fr 1fr;gap:10px}.zone-destination{text-align:left;min-height:91px;border:1px solid #314862;border-left:3px solid var(--zone-accent,#79dbc3);border-radius:11px;background:#122337;padding:13px;color:#e9f5ff;white-space:normal}.zone-destination strong{display:block;font-size:15px;margin-bottom:6px}.zone-destination span{display:block;color:#a6bed4;font-size:12px;line-height:1.4}.zone-feedback{min-height:20px;color:#ffce98;font-size:12px;margin-top:12px}.zone-editor .field{margin-bottom:8px}.zone-editor .zone-coordinates{display:grid;grid-template-columns:1fr 1fr 1fr;gap:5px}.zone-editor input,.zone-editor select,.zone-editor textarea{width:100%}.zone-editor .row{display:flex;gap:5px;margin-top:7px;flex-wrap:wrap}.zone-editor .row button{flex:1}.zone-editor-help{font-size:11px;color:#9db4c8;line-height:1.5}.zone-editor-feedback{font-size:11px;color:#ffce98;min-height:16px}.zone-transition{position:fixed;inset:0;z-index:300;background:#020711;pointer-events:none;opacity:0;transition:opacity 120ms ease}.zone-transition.active{opacity:1}
@media(max-width:640px){.zone-backdrop{padding:9px}.zone-dialog{padding:15px;max-height:91vh}.zone-destinations{grid-template-columns:1fr}.zone-menu-button{top:12px;left:10px;padding:9px 12px}.zone-dialog h2{font-size:19px}}
@media(prefers-reduced-motion:reduce){.zone-transition{transition:none}}
</style>
'''

JS = r'''
// Destinations belong to the project. Their Y is the authored world feet height.
let teleportMenuOpen=false,teleportMenuSession=null,teleportBusy=false,teleportGeneration=0,teleportReturnFocus=null;
let teleportRecoveryAt=0,teleportRecoveryPending=null;
function normalizeTeleportZone(value={}){
  if(!value||typeof value!=='object')throw new Error('A zone must be an object.');
  if(!Array.isArray(value.position)||value.position.length!==3||!value.position.every(v=>typeof v==='number'&&Number.isFinite(v)&&Math.abs(v)<=10000))throw new Error('Zone feet position needs three finite world coordinates.');
  const name=String(value.name||'').trim().slice(0,100);if(!name)throw new Error('Give this zone a name.');
  const yaw=value.yaw===undefined?0:value.yaw;if(typeof yaw!=='number'||!Number.isFinite(yaw))throw new Error('Zone heading must be a finite angle.');
  const id=value.id===undefined?'zone_'+uid():String(value.id);if(!/^[a-zA-Z0-9_-]{1,100}$/.test(id))throw new Error('Zone ID supports letters, numbers, underscores and hyphens.');
  return {id,name,description:String(value.description||'').slice(0,300),position:[...value.position],yaw:Math.atan2(Math.sin(yaw),Math.cos(yaw)),accent:workspaceAccent(value.accent)};
}
function normalizeTeleportZones(value){
  const result=[],ids=new Set();if(!Array.isArray(value))return result;
  for(const item of value.slice(0,100)){try{const zone=normalizeTeleportZone(item);if(!ids.has(zone.id)){ids.add(zone.id);result.push(zone)}}catch{}}
  return result;
}
function listTeleportZones(){return workspaceClone(currentProject.teleportZones||[])}
function upsertTeleportZone(config){
  if(playing||simulating)throw new Error('Stop Play before editing destinations.');
  const zone=normalizeTeleportZone(config),zones=listTeleportZones(),index=zones.findIndex(z=>z.id===zone.id);if(index<0&&zones.length>=100)throw new Error('A project supports up to 100 teleport zones.');
  beginTransaction('Configure zone '+zone.name);if(index<0)zones.push(zone);else zones[index]=zone;currentProject.teleportZones=zones;commitTransaction('Configure zone '+zone.name);renderTeleportEditor(zone.id);renderTeleportMenu();return workspaceClone(zone);
}
function removeTeleportZone(id){
  if(playing||simulating)throw new Error('Stop Play before editing destinations.');
  const zones=listTeleportZones(),zone=zones.find(z=>z.id===id);if(!zone)return false;
  beginTransaction('Remove zone '+zone.name);currentProject.teleportZones=zones.filter(z=>z.id!==id);commitTransaction('Remove zone '+zone.name);renderTeleportEditor();renderTeleportMenu();return true;
}
function configureNativeProject(meta={}){
  if(playing||simulating)throw new Error('Stop Play before configuring the project.');
  const update={};for(const key of ['name','canonicalId','template','kind','environment'])if(Object.hasOwn(meta,key))update[key]=String(meta[key]||'').slice(0,200);
  if(Object.hasOwn(meta,'environmentSettings')){if(!meta.environmentSettings||typeof meta.environmentSettings!=='object'||Array.isArray(meta.environmentSettings))throw new Error('Environment settings must be an object.');update.environmentSettings={...(currentProject.environmentSettings||{}),...workspaceClone(meta.environmentSettings)}}
  beginTransaction('Configure project');applyProjectMeta({...currentProject,...update});rebuildTerrain();if(currentProject.environment==='dragon-den')clearGroup(waterGroup);else buildSceneryExtras();commitTransaction('Configure project');return workspaceClone(currentProject);
}
function clearTeleportMovement(){clearWorkspaceInput();heroVel.set(0,0,0);heroJumpQueued=false;heroClickTarget=null;fpMove.x=fpMove.y=fpLook.x=fpLook.y=0;}
function teleportFeedback(message){const el=$('zoneFeedback');if(el)el.textContent=message||'';}
function closeTeleportMenu(resume=true){
  if(!teleportMenuOpen&&!teleportBusy)return;
  teleportGeneration++;teleportBusy=false;$('zoneTransition')?.classList.remove('active');teleportMenuOpen=false;$('zoneBackdrop')?.classList.remove('open');clearTeleportMovement();
  if(resume&&teleportMenuSession&&playing===teleportMenuSession.playing&&simulating===teleportMenuSession.simulating)paused=teleportMenuSession.paused;teleportMenuSession=null;setSessionButtons();
  const focus=teleportReturnFocus?.isConnected?teleportReturnFocus:$('viewport');teleportReturnFocus=null;focus?.focus();
}
function openTeleportMenu(){
  if(teleportBusy){toast('Finish the current travel first.');return false;}
  if(!playing){toast('Start Play to travel between zones.');return false}if(workspacePanelOpen){toast('Close the workspace before travelling.');return false}if(teleportMenuOpen)return true;
  teleportReturnFocus=document.activeElement;teleportMenuSession={playing,simulating,paused};teleportMenuOpen=true;paused=true;clearTeleportMovement();if(document.pointerLockElement)document.exitPointerLock?.();setSessionButtons();teleportFeedback('');renderTeleportMenu();$('workspaceNearby').style.display='none';$('zoneBackdrop').classList.add('open');setTimeout(()=>{($('zoneList').querySelector('button')||$('zoneClose')).focus()},0);return true;
}
function renderTeleportMenu(){
  const list=$('zoneList');if(!list)return;const previousFocus=document.activeElement,focusedZone=previousFocus?.dataset?.zoneId,restoreFocus=teleportMenuOpen&&$('zoneDialog')?.contains(previousFocus);list.replaceChildren();
  for(const zone of listTeleportZones()){const button=document.createElement('button');button.type='button';button.className='zone-destination';button.dataset.zoneId=zone.id;button.style.setProperty('--zone-accent',zone.accent);const title=document.createElement('strong'),description=document.createElement('span');title.textContent=zone.name;description.textContent=zone.description||'Travel to this part of the project.';button.append(title,description);button.disabled=teleportBusy;button.onclick=()=>teleportToZone(zone.id);list.appendChild(button)}
  if(!list.children.length){const empty=document.createElement('p');empty.textContent='No destinations yet. Add zones in the editor’s Teleport Zones panel.';list.appendChild(empty)}
  if(restoreFocus){const matching=[...list.querySelectorAll('button')].find(button=>button.dataset.zoneId===focusedZone&&!button.disabled);(matching||$('zoneClose')).focus();}
}
function teleportSupportAt(x,z,targetY,tolerance=.15){
  const meshList=[];if(terrainMesh&&walkingPhysicalMesh(terrainMesh))meshList.push(terrainMesh);
  for(const actor of walkingSurfaceActors())actor.traverse(mesh=>{if(walkingPhysicalMesh(mesh))meshList.push(mesh)});
  const origin=new THREE.Vector3(x,targetY+tolerance+.01,z),ray=new THREE.Raycaster(origin,new THREE.Vector3(0,-1,0),0,tolerance*2+.2),normal=new THREE.Vector3(),matrix=new THREE.Matrix3();
  for(const hit of ray.intersectObjects(physicalContactRayCandidates(meshList,origin,ray.far),false)){if(!hit.face)continue;normal.copy(hit.face.normal).applyMatrix3(matrix.getNormalMatrix(hit.object.matrixWorld)).normalize();if(normal.y<.45)continue;const feet=hit.point.y+HERO_GROUND_OFFSET;if(Math.abs(feet-targetY)<=tolerance)return feet;}
  return null;
}
function teleportSegmentsDistanceSq(p1,q1,p2,q2){
  const d1=q1.clone().sub(p1),d2=q2.clone().sub(p2),r=p1.clone().sub(p2),a=d1.dot(d1),e=d2.dot(d2),f=d2.dot(r),eps=1e-12;let s=0,t=0;
  if(a<=eps&&e<=eps)return p1.distanceToSquared(p2);
  if(a<=eps)t=THREE.MathUtils.clamp(f/e,0,1);else{const c=d1.dot(r);if(e<=eps)s=THREE.MathUtils.clamp(-c/a,0,1);else{const b=d1.dot(d2),den=a*e-b*b;s=den!==0?THREE.MathUtils.clamp((b*f-c*e)/den,0,1):0;t=(b*s+f)/e;if(t<0){t=0;s=THREE.MathUtils.clamp(-c/a,0,1)}else if(t>1){t=1;s=THREE.MathUtils.clamp((b-c)/a,0,1)}}}
  return p1.clone().addScaledVector(d1,s).distanceToSquared(p2.clone().addScaledVector(d2,t));
}
function teleportTriangleDistanceSq(start,end,a,b,c){
  const triangle=new THREE.Triangle(a,b,c),closest=new THREE.Vector3(),direction=end.clone().sub(start),length=direction.length();
  if(length>0&&new THREE.Ray(start,direction.divideScalar(length)).intersectTriangle(a,b,c,false,closest)&&closest.distanceToSquared(start)<=length*length)return 0;
  let distance=Math.min(triangle.closestPointToPoint(start,closest).distanceToSquared(start),triangle.closestPointToPoint(end,closest).distanceToSquared(end));
  for(const [u,v] of [[a,b],[b,c],[c,a]])distance=Math.min(distance,teleportSegmentsDistanceSq(start,end,u,v));return distance;
}
function teleportBodyClear(position,h){
  const radius=.55,height=(h.userData.eyeHeight||FP_EYE_HEIGHT)+.18,start=new THREE.Vector3(position.x,position.y+radius,position.z),end=new THREE.Vector3(position.x,position.y+Math.max(radius,height-radius),position.z);
  const capsuleBounds=new THREE.Box3().setFromPoints([start,end]).expandByScalar(radius-.015),a=new THREE.Vector3(),b=new THREE.Vector3(),c=new THREE.Vector3();
  // Broad-phase boxes are only candidates: vaulted ceilings and rings have
  // large empty interiors. Triangle/capsule contact decides actual clearance.
  const meshes=physicalContactMeshes().slice(),seen=new Set(meshes);
  for(const actor of actors){if(actor===h||!['hero','dragon'].includes(actor.userData.actorType)||!walkingObjectVisible(actor))continue;actor.traverse(mesh=>{if(walkingPhysicalMesh(mesh)&&!seen.has(mesh)){seen.add(mesh);meshes.push(mesh)}})}
  for(const mesh of meshes){
    const bounds=physicalContactWorldBounds(mesh);if(bounds&&!bounds.intersectsBox(capsuleBounds))continue;
    const geometry=mesh.geometry,attribute=geometry?.attributes?.position;if(!attribute)continue;const index=geometry.index,count=index?index.count:attribute.count;
    for(let i=0;i+2<count;i+=3){a.fromBufferAttribute(attribute,index?index.getX(i):i).applyMatrix4(mesh.matrixWorld);b.fromBufferAttribute(attribute,index?index.getX(i+1):i+1).applyMatrix4(mesh.matrixWorld);c.fromBufferAttribute(attribute,index?index.getX(i+2):i+2).applyMatrix4(mesh.matrixWorld);if(teleportTriangleDistanceSq(start,end,a,b,c)<(radius-.015)**2)return false;}
  }
  return true;
}
function validateTeleportLanding(zone){
  if(!playing)return {ok:false,error:'Start Play before travelling.'};if(workspacePanelOpen)return {ok:false,error:'Close the workspace before travelling.'};const h=heroActor();if(!h||!walkingObjectVisible(h))return {ok:false,error:'This project has no visible walking visitor.'};if(h.parent!==scene)return {ok:false,error:'Ungroup the walking visitor before travelling; player movement requires a world-root actor.'};if(h.userData.hoverFlight)return {ok:false,error:'Choose a walking visitor to use floor destinations.'};
  scene.updateMatrixWorld(true);const [x,y,z]=zone.position,support=teleportSupportAt(x,z,y);if(support===null)return {ok:false,error:'This destination’s floor is hidden or no longer supports the saved height.'};
  const position=new THREE.Vector3(x,support,z);
  // A complete footprint is required so a destination near an open ledge
  // cannot place a visitor half outside its supporting platform.
  for(let i=0;i<8;i++){const angle=i*Math.PI/4;if(teleportSupportAt(x+Math.cos(angle)*.5,z+Math.sin(angle)*.5,support,.32)===null)return {ok:false,error:'This destination is too close to an edge or lacks a clear landing pad.'};}
  const collision=position.clone();resolveHeroCollision(collision,.55);if(collision.distanceTo(position)>.005)return {ok:false,error:'A prop or guardrail blocks this destination. Move its landing point in the editor.'};
  if(!teleportBodyClear(position,h))return {ok:false,error:'This destination is occupied or has insufficient body and head clearance.'};
  return {ok:true,h,position};
}
async function teleportToZone(id){
  const zone=listTeleportZones().find(z=>z.id===id);if(!zone){const error='Unknown teleport destination.';teleportFeedback(error);return {ok:false,error}}if(teleportBusy)return {ok:false,error:'A teleport is already in progress.'};
  let landing=validateTeleportLanding(zone);if(!landing.ok){teleportFeedback(landing.error);toast(landing.error);return {ok:false,error:landing.error}};
  const standalone=!teleportMenuOpen,priorPause=paused,token=++teleportGeneration;if(standalone)teleportMenuSession={playing,simulating,paused:priorPause};teleportBusy=true;paused=true;clearTeleportMovement();if(document.pointerLockElement)document.exitPointerLock?.();setSessionButtons();renderTeleportMenu();teleportFeedback('Travelling to '+zone.name+'…');
  const duration=matchMedia('(prefers-reduced-motion:reduce)').matches?0:130;$('zoneTransition').classList.add('active');if(duration)await new Promise(resolve=>setTimeout(resolve,duration));
  if(token!==teleportGeneration||!playing){return {ok:false,error:'Travel was cancelled.'}};
  landing=validateTeleportLanding(zone);if(!landing.ok){teleportBusy=false;$('zoneTransition').classList.remove('active');if(standalone){paused=priorPause;teleportMenuSession=null;}setSessionButtons();renderTeleportMenu();teleportFeedback(landing.error);return {ok:false,error:landing.error}};
  const h=landing.h,world=landing.position;if(h.parent&&h.parent!==scene)h.position.copy(h.parent.worldToLocal(world.clone()));else h.position.copy(world);fpYaw=zone.yaw;fpPitch=0;h.rotation.y=zone.yaw;heroGrounded=true;clearTeleportMovement();
  perspectiveCamera.position.set(world.x,world.y+(h.userData.eyeHeight||FP_EYE_HEIGHT),world.z);perspectiveCamera.lookAt(perspectiveCamera.position.clone().add(new THREE.Vector3(Math.sin(fpYaw),0,-Math.cos(fpYaw))));
  $('zoneTransition').classList.remove('active');if(duration)await new Promise(resolve=>setTimeout(resolve,duration));if(token!==teleportGeneration||!playing)return {ok:false,error:'Travel was cancelled.'};
  teleportBusy=false;if(standalone){paused=priorPause;teleportMenuSession=null;setSessionButtons();renderTeleportMenu()}else closeTeleportMenu(true);editorLog('Travelled to '+zone.name,'ok');toast(zone.name+' · click the view to look around');return {ok:true,zoneId:zone.id,position:world.toArray()};
}
function updateTeleportRecovery(t){
  const settings=currentProject.environmentSettings||{};
  if(!playing||simulating||paused||workspacePanelOpen||teleportMenuOpen||teleportBusy||teleportRecoveryPending||!Number.isFinite(t)||t<teleportRecoveryAt||typeof settings.recoveryHeight!=='number'||!Number.isFinite(settings.recoveryHeight)||typeof settings.recoveryZone!=='string'||!settings.recoveryZone)return false;
  const h=heroActor();if(!h||h.userData.hoverFlight||h.parent!==scene||!walkingObjectVisible(h)||h.getWorldPosition(new THREE.Vector3()).y>=settings.recoveryHeight)return false;
  // A bad or hidden recovery pad never becomes an unchecked fallback. Retry
  // at a modest interval so a project author can restore its support safely.
  teleportRecoveryAt=t+5;const token={};teleportRecoveryPending=token;
  teleportToZone(settings.recoveryZone).then(result=>{if(teleportRecoveryPending!==token)return;if(result.ok){const zone=listTeleportZones().find(zone=>zone.id===settings.recoveryZone);toast('Back at '+(zone?.name||'the landing pad')+' · your work is still here.')}else editorLog('Recovery destination unavailable: '+result.error,'warn')}).catch(error=>{if(teleportRecoveryPending===token)editorLog('Recovery destination unavailable: '+error.message,'warn')}).finally(()=>{if(teleportRecoveryPending===token)teleportRecoveryPending=null});return true;
}
function readTeleportEditor(){return {id:$('zoneEditorSelect').value||undefined,name:$('zoneEditorName').value,description:$('zoneEditorDescription').value,position:['zoneEditorX','zoneEditorY','zoneEditorZ'].map(id=>Number($(id).value)),yaw:THREE.MathUtils.degToRad(Number($('zoneEditorYaw').value)),accent:$('zoneEditorAccent').value};}
function populateTeleportEditor(zone){
  const data=zone||{name:'New zone',description:'',position:heroActor()?.getWorldPosition(new THREE.Vector3()).toArray()||[0,terrainHeight(0,0)+HERO_GROUND_OFFSET,0],yaw:0,accent:'#79dbc3'};
  $('zoneEditorName').value=data.name;$('zoneEditorDescription').value=data.description||'';for(const [i,id] of ['zoneEditorX','zoneEditorY','zoneEditorZ'].entries())$(id).value=data.position[i].toFixed(3);$('zoneEditorYaw').value=THREE.MathUtils.radToDeg(data.yaw||0).toFixed(1);$('zoneEditorAccent').value=data.accent;$('zoneEditorDelete').disabled=!zone;$('zoneEditorFeedback').textContent='';
}
function renderTeleportEditor(preferredId){
  const select=$('zoneEditorSelect');if(!select)return;const wanted=preferredId===undefined?select.value:preferredId;select.replaceChildren();const newOption=document.createElement('option');newOption.value='';newOption.textContent='+ New destination';select.appendChild(newOption);for(const zone of listTeleportZones()){const option=document.createElement('option');option.value=zone.id;option.textContent=zone.name;select.appendChild(option)}select.value=listTeleportZones().some(z=>z.id===wanted)?wanted:'';populateTeleportEditor(listTeleportZones().find(z=>z.id===select.value));
}
function installTeleportTools(){
  const panel=document.createElement('details');panel.className='detail-box zone-editor';panel.id='teleportZoneEditor';panel.innerHTML='<summary>Teleport Zones</summary><div><p class="zone-editor-help">Destinations use world coordinates and feet height. Keep a clear landing pad away from rails and props. Play validates each destination before travel.</p><div class="field"><label for="zoneEditorSelect">Destination</label><select id="zoneEditorSelect"></select></div><div class="field"><label for="zoneEditorName">Name</label><input id="zoneEditorName" maxlength="100"></div><div class="field"><label for="zoneEditorDescription">Description</label><textarea id="zoneEditorDescription" rows="2" maxlength="300"></textarea></div><div class="zone-coordinates"><div class="field"><label for="zoneEditorX">World X</label><input id="zoneEditorX" type="number" step=".1"></div><div class="field"><label for="zoneEditorY">Feet Y</label><input id="zoneEditorY" type="number" step=".1"></div><div class="field"><label for="zoneEditorZ">World Z</label><input id="zoneEditorZ" type="number" step=".1"></div></div><div class="field"><label for="zoneEditorYaw">Heading (degrees)</label><input id="zoneEditorYaw" type="number" step="5"></div><div class="field"><label for="zoneEditorAccent">Accent</label><input id="zoneEditorAccent" type="color"></div><div class="row"><button id="zoneEditorFromSelected" type="button">Use Selected</button><button id="zoneEditorFromVisitor" type="button">Use Visitor</button></div><div class="row"><button id="zoneEditorSave" type="button">Save Zone</button><button id="zoneEditorDelete" type="button">Delete</button></div><div id="zoneEditorFeedback" class="zone-editor-feedback" role="status"></div></div>';$('inspector').parentElement.appendChild(panel);
  $('zoneEditorSelect').onchange=()=>populateTeleportEditor(listTeleportZones().find(z=>z.id===$('zoneEditorSelect').value));const fillPosition=actor=>{if(!actor){$('zoneEditorFeedback').textContent='Select an actor or add a walking visitor first.';return}const point=actor.getWorldPosition(new THREE.Vector3());for(const [i,id] of ['zoneEditorX','zoneEditorY','zoneEditorZ'].entries())$(id).value=point.toArray()[i].toFixed(3);$('zoneEditorYaw').value=THREE.MathUtils.radToDeg(new THREE.Euler().setFromQuaternion(actor.getWorldQuaternion(new THREE.Quaternion()),'YXZ').y).toFixed(1);};
  $('zoneEditorFromSelected').onclick=()=>fillPosition(selected);$('zoneEditorFromVisitor').onclick=()=>fillPosition(heroActor());$('zoneEditorSave').onclick=()=>{try{const zone=upsertTeleportZone(readTeleportEditor());$('zoneEditorFeedback').textContent='Saved '+zone.name+' · test its landing in Play.'}catch(e){$('zoneEditorFeedback').textContent=e.message}};$('zoneEditorDelete').onclick=()=>{try{removeTeleportZone($('zoneEditorSelect').value)}catch(e){$('zoneEditorFeedback').textContent=e.message}};
  const button=document.createElement('button');button.type='button';button.id='zoneMenuBtn';button.className='zone-menu-button';button.textContent='✧ Zones · T';button.setAttribute('aria-haspopup','dialog');button.onclick=openTeleportMenu;$('viewport').parentElement.appendChild(button);
  const backdrop=document.createElement('div');backdrop.id='zoneBackdrop';backdrop.className='zone-backdrop';backdrop.innerHTML='<section id="zoneDialog" class="zone-dialog" role="dialog" aria-modal="true" aria-labelledby="zoneTitle" aria-describedby="zoneDescription"><header><h2 id="zoneTitle">Travel between zones</h2><button id="zoneClose" type="button">Close / Resume</button></header><p id="zoneDescription">Choose where to arrive. Travel keeps your project work in place.</p><div id="zoneList" class="zone-destinations"></div><div id="zoneFeedback" class="zone-feedback" role="status" aria-live="polite"></div></section>';document.body.appendChild(backdrop);$('zoneClose').onclick=()=>closeTeleportMenu();backdrop.addEventListener('pointerdown',e=>{if(e.target===backdrop)closeTeleportMenu()});const transition=document.createElement('div');transition.id='zoneTransition';transition.className='zone-transition';transition.setAttribute('aria-hidden','true');document.body.appendChild(transition);
  window.addEventListener('keydown',event=>{if(teleportMenuOpen){if(event.key==='Escape'){event.preventDefault();event.stopImmediatePropagation();closeTeleportMenu()}else if(event.key==='Tab'){const nodes=[...$('zoneDialog').querySelectorAll('button')].filter(n=>!n.disabled),first=nodes[0],last=nodes.at(-1);if(!$('zoneDialog').contains(document.activeElement)){event.preventDefault();(event.shiftKey?last:first)?.focus()}else if(event.shiftKey&&document.activeElement===first){event.preventDefault();last?.focus()}else if(!event.shiftKey&&document.activeElement===last){event.preventDefault();first?.focus()}}else{event.stopImmediatePropagation()}return}const tag=document.activeElement?.tagName;if(workspacePanelOpen||['INPUT','SELECT','TEXTAREA'].includes(tag)||document.activeElement?.isContentEditable)return;if(playing&&event.key.toLowerCase()==='t'&&!event.ctrlKey&&!event.metaKey&&!event.altKey){event.preventDefault();event.stopImmediatePropagation();openTeleportMenu()}},true);renderTeleportEditor();renderTeleportMenu();
}
installTeleportTools();
'''

def apply(html):
    s=html.replace('</head>',CSS+'\n</head>',1)
    s=_once(s,'installWorkspaceTools();','installWorkspaceTools();\n'+JS)
    s=_once(s,'  configureWorkspace:(id,config)=>configureWorkspace(id,config),',"  upsertTeleportZone:(zone)=>upsertTeleportZone(zone),\n  removeTeleportZone:(id)=>removeTeleportZone(id),\n  listTeleportZones:()=>listTeleportZones(),\n  teleportToZone:(id)=>teleportToZone(id),\n  openTeleportMenu:()=>openTeleportMenu(),\n  closeTeleportMenu:()=>closeTeleportMenu(),\n  configureProject:(meta)=>configureNativeProject(meta),\n  configureWorkspace:(id,config)=>configureWorkspace(id,config),")
    s=_once(s,'  currentProject.workspaces=workspaceData;if(meta.canonicalId)currentProject.canonicalId=meta.canonicalId;', '  currentProject.workspaces=workspaceData;if(meta.canonicalId)currentProject.canonicalId=meta.canonicalId;\n  currentProject.teleportZones=normalizeTeleportZones(meta.teleportZones);renderTeleportEditor();renderTeleportMenu();')
    s=_once(s,"function clearAll(){\n  transform.detach(); selected=null;","function clearAll(){\n  closeTeleportMenu(false);teleportRecoveryAt=0;teleportRecoveryPending=null;\n  transform.detach(); selected=null;")
    for name in ['beginPlay(fromHere=null)','beginSimulate()','stopSession()']:
        s=_once(s,'function '+name+'{\n  closeWorkspacePanel(false);','function '+name+'{\n  closeTeleportMenu(false);\n  closeWorkspacePanel(false);')
    s=_once(s,"  if(workspacePanelOpen)return;\n  const h=heroActor();if(!h||h.visible===false)return;", "  if(workspacePanelOpen||teleportMenuOpen||teleportBusy)return;\n  const h=heroActor();if(!h||h.visible===false)return;")
    s=_once(s,"  if(workspacePanelOpen)return;\n  if(playing){","  if(workspacePanelOpen||teleportMenuOpen||teleportBusy)return;\n  if(playing){")
    s=_once(s,"  if(workspacePanelOpen||['INPUT','SELECT','TEXTAREA'].includes(tag)||document.activeElement?.isContentEditable) return;","  if(workspacePanelOpen||teleportMenuOpen||teleportBusy||['INPUT','SELECT','TEXTAREA'].includes(tag)||document.activeElement?.isContentEditable) return;")
    s=_once(s,"  if(workspacePanelOpen||!playing||document.pointerLockElement!==$('viewport'))return;","  if(workspacePanelOpen||teleportMenuOpen||teleportBusy||!playing||document.pointerLockElement!==$('viewport'))return;")
    s=_once(s,'function openWorkspacePanel(id){\n  const a=',"function openWorkspacePanel(id){\n  if(teleportMenuOpen||teleportBusy){toast('Close travel before opening a workspace.');return false;}\n  const a=")
    s=_once(s,'    if(playing)updateHero(dt,t);updateRuntimeComponents(dt,t);','    if(playing){updateHero(dt,t);updateTeleportRecovery(t);}if(!paused)updateRuntimeComponents(dt,t);')
    return s
