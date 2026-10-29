// The opening is composed on top of the saved performance. Its attachment
// point is the physical page hinge, never a camera-relative screen position.
const EMERGENCE_SCHEMA='anime-book-emergence-v1';
const EMERGENCE_LAYERS=Object.freeze(['book','background','midground','atmosphere','effects','kami','swyrlz','foreground']);
const EMERGENCE_DEFAULT_TIMING=Object.freeze({book:[0,3],background:[1,8],midground:[2,8],atmosphere:[3,7],effects:[4,7],kami:[3,7],swyrlz:[4,7],foreground:[2,7]});
let emergenceValidatedProject=null,emergenceValidatedModel=null,emergenceValidatedDuration=null;
function emergenceIsProject(){return !!currentProject&&(currentProject.canonicalId==='ghosts-different-forms-ep01'||currentProject.animeTimeline?.schema===STORY_SCHEMA);}
function emergenceCleanObject(value){return value&&typeof value==='object'&&!Array.isArray(value)?value:{};}
function emergenceSanitize(value){
  const raw=emergenceCleanObject(value),limit=Math.min(30,storyTimeline().duration);
  const duration=storyNumber(raw.duration,Math.min(12,limit),Math.min(4,limit),limit),layers={};
  for(const id of EMERGENCE_LAYERS){
    const spec=emergenceCleanObject(raw.layers?.[id]),defaults=EMERGENCE_DEFAULT_TIMING[id],ratio=duration/12;
    const delay=storyNumber(spec.delay,defaults[0]*ratio,0,Math.max(0,duration-.25));
    layers[id]={delay,duration:storyNumber(spec.duration,defaults[1]*ratio,Math.min(.25,duration-delay),duration-delay)};
  }
  return {schema:EMERGENCE_SCHEMA,enabled:typeof raw.enabled==='boolean'?raw.enabled:true,duration,layers};
}
function emergenceModel(){
  if(!emergenceIsProject())return emergenceSanitize({enabled:false});
  const duration=storyTimeline().duration;
  if(emergenceValidatedProject!==currentProject||emergenceValidatedModel!==currentProject.animeEmergence||emergenceValidatedDuration!==duration){
    currentProject.animeEmergence=emergenceSanitize(currentProject.animeEmergence);
    emergenceValidatedProject=currentProject;emergenceValidatedModel=currentProject.animeEmergence;emergenceValidatedDuration=duration;
  }
  return currentProject.animeEmergence;
}
function emergenceConfigure(value){
  if(!storyEditable()||!emergenceIsProject()||!value||typeof value!=='object'||Array.isArray(value))return false;
  const previous=emergenceModel(),draft=storyCopy(previous);
  if(Object.hasOwn(value,'enabled')&&typeof value.enabled==='boolean')draft.enabled=value.enabled;
  if(Object.hasOwn(value,'duration')){
    const limit=Math.min(30,storyTimeline().duration),next=storyNumber(value.duration,draft.duration,Math.min(4,limit),limit),ratio=next/draft.duration;
    for(const timing of Object.values(draft.layers)){timing.delay*=ratio;timing.duration*=ratio;}
    draft.duration=next;
  }
  for(const id of EMERGENCE_LAYERS)if(value.layers?.[id]&&typeof value.layers[id]==='object'&&!Array.isArray(value.layers[id])){
    const timing=value.layers[id];
    if(Object.hasOwn(timing,'delay'))draft.layers[id].delay=timing.delay;
    if(Object.hasOwn(timing,'duration'))draft.layers[id].duration=timing.duration;
  }
  const next=emergenceSanitize(draft);
  if(JSON.stringify(previous)===JSON.stringify(next))return true;
  beginTransaction('Book opening');currentProject.animeEmergence=next;
  emergenceValidatedProject=currentProject;emergenceValidatedModel=next;emergenceValidatedDuration=storyTimeline().duration;
  commitTransaction('Book opening');if(animeCine)storyRender();storyNotify();return true;
}
function emergenceProgress(id,time,offset=0){
  const model=emergenceModel();if(!model.enabled)return 1;
  const timing=model.layers[id];if(!timing)return 1;
  const extra=Math.min(Math.max(0,offset),timing.duration*.18),span=Math.max(.001,timing.duration-extra);
  const u=Math.max(0,Math.min(1,(time-timing.delay-extra)/span));return u*u*(3-2*u);
}
function emergenceOpening(time){return emergenceIsProject()&&emergenceModel().enabled&&time<emergenceModel().duration;}
function emergencePoseBook(book,key,time){
  const opening=emergenceOpening(time),progress=opening?emergenceProgress('book',time):key.unfold;
  // At rest the left half closes onto the right half. Both covers travel with
  // their page halves, so this is a closed book opening into a real spread.
  for(const page of book.children.filter(o=>o.userData.storyPage))page.rotation.z=page.position.x<0?-(1-progress)*Math.PI:0;
  book.userData.emergence={id:'book',progress:opening?progress:1};
}
function emergencePageAnchor(book){
  scene.updateMatrixWorld(true);
  const right=book.children.find(o=>o.userData.storyPage&&o.position.x>0);
  return (right||book).localToWorld(new THREE.Vector3(0,.16,0));
}
function emergencePrepareFrame(c,book,time){
  const origin=emergencePageAnchor(book);c.bookEmergence={time,origin};return origin;
}
function emergenceBounds(group){
  const box=new THREE.Box3().setFromObject(group);
  return box.isEmpty()?null:{min:box.min.toArray(),max:box.max.toArray()};
}
function emergenceApplyLayer(group,id,time,c){
  const progress=emergenceProgress(id,time);group.userData.emergence={id,progress};
  if(!emergenceOpening(time)||progress>=1)return progress;
  // A saved opacity key may begin fading before this layer's opening row.
  // Keep the collapsed puppet in the book until its physical expansion starts.
  group.visible=group.visible&&progress>.001;
  scene.updateMatrixWorld(true);
  const original=new THREE.Box3().setFromObject(group);if(original.isEmpty())return progress;
  const authored=original.getCenter(new THREE.Vector3());authored.y=original.min.y;
  const origin=c.bookEmergence.origin.clone();origin.y+=.44;
  // Different rows attach to the back and front of the physical page spread.
  // Even a folded paper wall stays behind the character corridor.
  if(['background','midground','atmosphere','effects'].includes(id))origin.z-=2.1;
  else if(id==='foreground')origin.y-=.78;
  else origin.x+=id==='kami'?.24:-.24;
  const size=.012+.988*progress;group.scale.multiplyScalar(size);
  scene.updateMatrixWorld(true);
  const small=new THREE.Box3().setFromObject(group),anchor=small.getCenter(new THREE.Vector3());anchor.y=small.min.y;
  const desired=origin.clone().lerp(authored,progress);
  const localDesired=group.parent?group.parent.worldToLocal(desired):desired;
  const localAnchor=group.parent?group.parent.worldToLocal(anchor):anchor;
  group.position.add(localDesired.sub(localAnchor));
  group.userData.emergence.origin=origin.toArray();
  return progress;
}
function emergenceApplyScenery(card,parent,time){
  const data=card?.userData.storyScenery;if(!data)return;
  const opening=emergenceOpening(time),entries=Object.entries(data.objects);
  for(const [index,[id,item]] of entries.entries()){
    const offset=(index%5)*.12,progress=emergenceProgress(parent,time,offset);
    item.pivot.userData.emergence={id,parent,progress};
    if(!opening||progress>=1)continue;
    item.pivot.position.multiplyScalar(progress);
    item.pivot.scale.multiplyScalar(.035+.965*progress);
    const key=scenerySample(id,time);item.hinge.rotation.x=-(1-key.unfold*progress)*Math.PI*.5;
    item.pivot.visible=item.pivot.visible&&progress>.001;
  }
  if(data.sky){
    const progress=emergenceProgress(parent,time);
    const size=opening ? .025+.975*progress : 1;
    data.sky.scale.setScalar(size);data.sky.position.y=20*size;
    data.sky.material.opacity*=opening?progress*progress:1;
  }
}
function emergenceApplyParticles(c,time){
  const progress=emergenceProgress('effects',time),opening=emergenceOpening(time),positions=c.particlesGeometry.getAttribute('position');
  if(!opening)return;
  const origin=c.bookEmergence.origin;
  // The ornamental motes are native world-space geometry too.
  for(let i=0;i<positions.count;i++)positions.setXYZ(i,
    origin.x+(positions.getX(i)-origin.x)*progress,
    origin.y+(positions.getY(i)-origin.y)*progress,
    origin.z+(positions.getZ(i)-origin.z)*progress);
  c.particlesMaterial.opacity*=progress;positions.needsUpdate=true;
}
function emergenceRenderStatus(){
  const model=emergenceModel(),c=animeCine;
  if(!c)return {active:false,enabled:model.enabled,time:0,origin:null,pageBounds:null,layers:[],objects:[]};
  scene.updateMatrixWorld(true);
  const book=c.layers.book.children[0],pageBox=new THREE.Box3(),layers=[],objects=[];
  for(const half of book.children.filter(o=>o.userData.storyPage))for(const mesh of half.children.filter(o=>o.userData.storyPageInk))pageBox.expandByObject(mesh);
  for(const id of EMERGENCE_LAYERS){
    const group=id==='kami'?c.cast.kami:id==='swyrlz'?c.cast.wisp:id==='book'?book:c.layers[id];
    const state=group.userData.emergence||{};
    layers.push({id,progress:state.progress??emergenceProgress(id,c.elapsed),origin:state.origin||c.bookEmergence?.origin.toArray(),visible:group.visible,bounds:emergenceBounds(group)});
    const data=group.children[0]?.userData.storyScenery;
    for(const [objectId,item] of Object.entries(data?.objects||{}))objects.push({id:objectId,parent:id,progress:item.pivot.userData.emergence?.progress??1,visible:group.visible&&item.pivot.visible,bounds:emergenceBounds(item.part)});
  }
  return {active:true,enabled:model.enabled,time:c.elapsed,origin:emergencePageAnchor(book).toArray(),pageBounds:pageBox.isEmpty()?null:{min:pageBox.min.toArray(),max:pageBox.max.toArray()},layers,objects};
}
const emergencePreviousProjectMeta=applyProjectMeta,emergencePreviousNotify=storyNotify;
applyProjectMeta=function(meta={}){
  const result=emergencePreviousProjectMeta(meta);emergenceValidatedProject=null;emergenceValidatedModel=null;emergenceValidatedDuration=null;
  if(emergenceIsProject()){
    currentProject.animeEmergence=emergenceSanitize(meta?.animeEmergence);
    emergenceValidatedProject=currentProject;emergenceValidatedModel=currentProject.animeEmergence;emergenceValidatedDuration=storyTimeline().duration;
  }
  if(typeof emergenceEditorSync==='function')emergenceEditorSync();return result;
};
storyNotify=function(){emergencePreviousNotify();if(typeof emergenceEditorSync==='function')emergenceEditorSync();};
window.SWYRL_ENGINE_EMERGENCE=Object.freeze({model:()=>storyCopy(emergenceModel()),configure:emergenceConfigure,status:emergenceRenderStatus});
