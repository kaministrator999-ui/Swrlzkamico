// Native textured paper actors, shared by editor preview and cinematic Play.
const STORY_VISUALS = Object.freeze({
  kami:{asset:'assets/anime/kami.png',width:4,height:6,hinged:false},
  swyrlz:{asset:'assets/anime/swyrlz.png',width:3.6,height:3.3,hinged:false},
  background:{asset:'assets/anime/cathedral.png',width:42,height:23.625,hinged:true},
  midground:{asset:'assets/anime/workshop.png',width:24,height:13.5,hinged:true},
  foreground:{asset:'assets/anime/foreground.png',width:14,height:7.875,hinged:true},
  atmosphere:{asset:'procedural:mist',width:30,height:16.875,hinged:true},
  effects:{asset:'procedural:runes',width:13,height:9,hinged:true}
});
const storyTextureCache = new Map(), storyAssetPending = new Set(), storyAssetErrors = new Set();
let storyPreviewActive=false, storyCameraSnapshot=null, storyEnvironmentSnapshot=null;
function storySyncStoryStations(){
  const stations=currentProject?.workspaces?.stations||{},beats=storyTimeline().beats;
  for(const [index,beat] of beats.entries()){
    for(const station of Object.values(stations)){
      const script=station.files?.find(file=>file.id==='act-'+index+'-script');
      if(script)script.content='# '+beat.title+'\n\n'+beat.cues.map(cue=>animeClock(cue.time)+' · '+cue.text).join('\n\n');
      const direction=station.files?.find(file=>file.id==='act-'+index+'-direction');
      if(direction)direction.content='# '+beat.title+'\n\nShot and individual layer keyframes are authored in Animation Studio, '+beat.time+'–'+beat.end+' seconds.\nCamera follows the story while preserving the clear central stage.\nKami and §wyrlz remain separate paper actors. Scenery folds away from the camera.';
    }
  }
}
function storyAssetSource(source,fallback){
  if(typeof source!=='string')return fallback;
  if(/^assets\/anime\/[a-z0-9_-]+\.(png|webp|jpe?g)$/i.test(source))return source;
  if(/^data:image\/(png|webp|jpeg);base64,[A-Za-z0-9+/=]+$/.test(source)&&source.length<12000000)return source;
  return fallback;
}
function storyTexture(source){
  if(storyTextureCache.has(source))return storyTextureCache.get(source);
  let texture;
  if(source.startsWith('procedural:')){
    texture=animeDrawSurface((c,w,h)=>{
      c.clearRect(0,0,w,h);
      if(source==='procedural:mist'){
        for(let i=0;i<9;i++){
          const x=70+i*83,y=340+(i%3)*38,g=c.createRadialGradient(x,y,0,x,y,95);
          g.addColorStop(0,'#d3a56922');g.addColorStop(1,'#d3a56900');c.fillStyle=g;c.fillRect(x-95,y-95,190,190);
        }
      }else{
        popRune(c,w*.5,h*.48,125);
        for(let j=0;j<6;j++)popCurl(c,95+j*114,250+(j%2)*93,.22);
      }
    },768,576);
  }else{
    storyAssetPending.add(source);
    texture=new THREE.TextureLoader().load(source,loaded=>{
      // Measure visible ink without changing the artwork. An opaque imported
      // foreground must receive full-height protection, just like a cutout.
      loaded.userData.storyInkHeight=1;
      try{
        const image=loaded.image,canvas=document.createElement('canvas');
        canvas.width=image.naturalWidth||image.width;canvas.height=image.naturalHeight||image.height;
        const context=canvas.getContext('2d',{willReadFrequently:true});context.drawImage(image,0,0);
        const pixels=context.getImageData(0,0,canvas.width,canvas.height).data;
        let first=canvas.height;
        rows:for(let y=0;y<canvas.height;y++)for(let x=0;x<canvas.width;x++)
          if(pixels[(y*canvas.width+x)*4+3]>3){first=y;break rows;}
        loaded.userData.storyInkHeight=(canvas.height-first)/canvas.height;
      }catch(error){/* Full-height fallback also protects cross-origin art. */}
      storyAssetPending.delete(source);storyAssetErrors.delete(source);
    },undefined,()=>{storyAssetPending.delete(source);storyAssetErrors.add(source);editorLog('Artwork failed to load: '+source.slice(0,100),'error');});
  }
  texture.userData.storyInkHeight??=1;
  texture.colorSpace=THREE.SRGBColorSpace;texture.anisotropy=Math.min(4,renderer.capabilities.getMaxAnisotropy());
  storyTextureCache.set(source,texture);return texture;
}
function storyCleanVisual(value={}){
  if(!value||typeof value!=='object'||Array.isArray(value))value={};
  const layer=Object.hasOwn(STORY_VISUALS,value.layer)?value.layer:'kami',base=STORY_VISUALS[layer];
  return {layer,asset:storyAssetSource(value.asset,base.asset),
    width:storyNumber(value.width,base.width,.25,60),height:storyNumber(value.height,base.height,.25,32),
    hinged:base.hinged};
}
function storyPaperVisual(value){
  const visual=storyCleanVisual(value),group=new THREE.Group();group.userData.storyVisual=visual;
  const material=new THREE.MeshBasicMaterial({map:storyTexture(visual.asset),side:THREE.DoubleSide,
    transparent:true,alphaTest:.012,depthWrite:true,depthTest:true,fog:false,toneMapped:false});
  const paper=new THREE.Mesh(new THREE.PlaneGeometry(visual.width,visual.height),material);
  paper.name=visual.layer+' · illustrated paper';paper.userData.storyPaper=true;
  // Geometry translates up from the bottom-edge hinge; unlike Sprite, the
  // surface itself rotates when the card folds flat against the book.
  if(visual.hinged){paper.position.y=visual.height*.5;group.add(paper);}
  else{
    const pivot=new THREE.Group();pivot.position.y=-visual.height*.5;
    pivot.userData.storyCastHinge=true;paper.position.y=visual.height*.5;pivot.add(paper);group.add(pivot);
  }
  group.userData.popupHinge=true;
  return group;
}
function storyBookVisual(){
  const book=animeMakePaperBook();book.position.set(0,0,0);book.userData.storyBook=true;
  // The leather sits beneath the pages, rather than hiding their illustration.
  book.children.find(o=>o.isMesh).position.y=-.2;
  const ink=animeDrawSurface((c,w,h)=>{
    const gradient=c.createLinearGradient(0,0,w,h);gradient.addColorStop(0,'#f4ddad');gradient.addColorStop(.5,'#c6a46c');gradient.addColorStop(1,'#eed7a4');
    c.fillStyle=gradient;c.fillRect(0,0,w,h);c.strokeStyle='#6b493c';c.lineWidth=4;c.strokeRect(16,16,w-32,h-32);
    for(let i=0;i<90;i++){c.fillStyle='#66412b0b';c.fillRect((i*79)%w,(i*43)%h,60,3)}
    popRune(c,w*.5,h*.5,Math.min(w,h)*.3);
    for(const side of [30,w-120])for(let j=0;j<9;j++){c.strokeStyle='#6c4f37aa';c.lineWidth=2;c.beginPath();c.moveTo(side,40+j*21);c.lineTo(side+60+(j%3)*10,40+j*21);c.stroke();}
  },512,320);
  book.children.forEach(o=>{
    if(o.isGroup){
      o.userData.storyPage=true;
      const page=new THREE.Mesh(new THREE.PlaneGeometry(4.05,2.45),new THREE.MeshBasicMaterial({map:ink,side:THREE.DoubleSide,fog:false,toneMapped:false}));
      page.position.set(o.position.x<0?-2.08:2.08,.16,0);page.rotation.x=-Math.PI/2;o.add(page);
    }
    o.scale.x=1.25;o.scale.z=2.2;
  });return book;
}
function storyMakeNativeActor(data){
  const group=data.type==='animeBook'?storyBookVisual():storyPaperVisual(data.storyVisual||{});
  const actor=markActor(group,data.type,{name:data.name||'Paper stage',baked:data.baked!==false,
    folder:data.folder||'Anime Studio/Paper Theatre',components:data.components||['Transform','Scene','StaticMesh','Animation'],
    role:data.role||'',groupParentId:data.groupParentId||null,groupChildIds:data.groupChildIds||[],
    colliderRadius:0,tags:[...new Set([...(data.tags||[]),'anime-stage'])],editorLayerIds:data.editorLayerIds||[],manualVisible:data.manualVisible!==false});
  if(data.id)actor.userData.id=data.id;
  if(data.type==='animeCel')actor.userData.storyVisual=storyCleanVisual(data.storyVisual);
  actor.position.fromArray(data.position||[0,0,0]);actor.rotation.set(...(data.rotation||[0,0,0]));actor.scale.fromArray(data.scale||[1,1,1]);
  actor.userData.spawnPos=actor.position.toArray();syncActorVisibility(actor);return actor;
}
const storyFromData=fromData,storyActorData=actorData;
fromData=function(data){return data?.type==='animeCel'||data?.type==='animeBook'?storyMakeNativeActor(data):storyFromData(data);};
actorData=function(actor){const data=storyActorData(actor);if(actor.userData.storyVisual)data.storyVisual=storyCopy(actor.userData.storyVisual);return data;};
const storyProjectData=projectData;
projectData=function(){
  const data=storyProjectData();
  if(storyEnvironmentSnapshot)data.scene.background='#'+storyEnvironmentSnapshot.background.getHexString();
  return data;
};
function storyBoundActor(layer){return actors.find(a=>layer==='book'?a.userData.actorType==='animeBook':a.userData.storyVisual?.layer===layer);}
function storyCloneVisual(actor,fallback){
  if(!actor)return fallback();
  const clone=actor.userData.actorType==='animeBook'?storyBookVisual():storyPaperVisual(actor.userData.storyVisual);
  clone.userData.storyActorId=actor.userData.id;clone.name=actor.name;return clone;
}
function storyAuthoredVisible(layer){
  const actor=storyBoundActor(layer);return !actor||actor.userData.manualVisible!==false&&
    !(actor.userData.editorLayerIds||[]).some(id=>layerById(id)?.visible===false);
}
function storyBuildStage(){
  if(!storyEditable())return false;
  storyExitPreview();beginTransaction('Build layered pop-up book stage');
  for(const layer of ['background','atmosphere','midground','kami','swyrlz','effects','foreground','book']){
    if(storyBoundActor(layer))continue;
    const id='anime-layer-'+layer;
    if(!editorLayers.some(l=>l.id===id))editorLayers.push({id,name:layer==='kami'?'Kami · main mage':layer==='swyrlz'?'§wyrlz · companion mage':layer+' · paper theatre',visible:true});
    const sample=storySample(layer,8),visual=STORY_VISUALS[layer];
    storyMakeNativeActor({id:'anime-actor-'+layer,name:layer==='kami'?'Kami · horned creator mage':layer==='swyrlz'?'§wyrlz · floating grimoire mage':layer+' · pop-up plate',
      type:layer==='book'?'animeBook':'animeCel',storyVisual:visual?{layer,...visual}:undefined,
      position:[sample.x,sample.y,sample.z],editorLayerIds:[id],baked:true});
  }
  renderLayerPanel();rebuildHierarchy();refreshDebug();commitTransaction('Build layered pop-up book stage');return true;
}
function storyBindArtwork(layer,source){
  if(!storyEditable()||!Object.hasOwn(STORY_VISUALS,layer))return false;
  const actor=storyBoundActor(layer),asset=storyAssetSource(source,null);if(!actor||!asset)return false;
  storyExitPreview();beginTransaction('Replace '+layer+' artwork');
  actor.userData.storyVisual={...actor.userData.storyVisual,asset};
  const replacement=storyPaperVisual(actor.userData.storyVisual);
  for(const old of [...actor.children]){actor.remove(old);old.traverse(o=>{o.geometry?.dispose();o.material?.dispose()})}
  for(const child of [...replacement.children])actor.add(child);
  commitTransaction('Replace '+layer+' artwork');return true;
}
function storyCaptureActorPose(layer,time){
  if(layer==='camera'||!storyEditable())return false;
  const actor=storyBoundActor(layer);if(!actor)return false;
  // Native inspector transforms may belong to a group; capture the world pose.
  actor.updateWorldMatrix(true,false);
  const position=new THREE.Vector3(),quaternion=new THREE.Quaternion(),scale=new THREE.Vector3();
  actor.matrixWorld.decompose(position,quaternion,scale);
  const rotation=new THREE.Euler().setFromQuaternion(quaternion);
  return storyUpsertKey(layer,{...storySample(layer,time),time,x:position.x,y:position.y,z:position.z,scale:scale.x,rotation:rotation.z});
}
animeMakeCast=function(){
  const kami=storyCloneVisual(storyBoundActor('kami'),()=>storyPaperVisual({layer:'kami'}));
  const wisp=storyCloneVisual(storyBoundActor('swyrlz'),()=>storyPaperVisual({layer:'swyrlz'}));
  const dragon=new THREE.Group();dragon.visible=false;scene.add(kami,wisp,dragon);return {kami,wisp,dragon};
};
animeCreateCelLayers=function(){
  const groups={};for(const [id] of ANIME_2D_LAYER_SPECS){const group=new THREE.Group();group.userData.animeLayer=id;scene.add(group);groups[id]=group;}
  for(const layer of ['background','atmosphere','midground','effects','foreground']){
    const item=storyCloneVisual(storyBoundActor(layer),()=>storyPaperVisual({layer}));
    groups[layer].add(item);
  }
  groups.book=new THREE.Group();groups.book.userData.animeLayer='book';scene.add(groups.book);
  groups.book.add(storyCloneVisual(storyBoundActor('book'),storyBookVisual));return groups;
};
function storyRememberCamera(){
  if(storyCameraSnapshot)return;
  storyCameraSnapshot={view:editorCameraView,camera,position:camera.position.clone(),quaternion:camera.quaternion.clone(),
    up:camera.up.clone(),zoom:camera.zoom,fov:perspectiveCamera.fov,target:orbit.target.clone(),enabled:orbit.enabled,rotate:orbit.enableRotate};
}
function storyRestoreCamera(){
  const saved=storyCameraSnapshot;if(!saved)return;
  storyCameraSnapshot=null;setActiveCamera(saved.camera);editorCameraView=saved.view;$('cameraView').value=saved.view;
  saved.camera.position.copy(saved.position);saved.camera.quaternion.copy(saved.quaternion);saved.camera.up.copy(saved.up);saved.camera.zoom=saved.zoom;
  perspectiveCamera.fov=saved.fov;perspectiveCamera.updateProjectionMatrix();saved.camera.updateProjectionMatrix();
  orbit.target.copy(saved.target);orbit.enabled=saved.enabled;orbit.enableRotate=saved.rotate;
}
const storyStartCinematic=animeStartCinematic,storyEndCinematic=animeEndCinematic;
animeStartCinematic=function(){
  storyRememberCamera();const result=storyStartCinematic();if(!result)return result;
  storyEnvironmentSnapshot={background:scene.background.clone(),override:scene.overrideMaterial,
    hidden:[helperGroup,debugGroup,waterGroup,terrainShellGroup,terrainMesh,selectionBox].filter(Boolean).map(o=>[o,o.visible])};
  scene.background.set('#080706');scene.overrideMaterial=null;
  for(const [o] of storyEnvironmentSnapshot.hidden)o.visible=false;
  animeCine.layers.kami.add(animeCine.cast.kami);animeCine.layers.swyrlz.add(animeCine.cast.wisp);
  animeHud.querySelector('#animeCinePrev').onclick=()=>{
    const times=storyTimeline().beats.map(b=>b.time),current=animeCine.elapsed;
    animeSeek([...times].reverse().find(time=>time<current-.25)??0);
  };
  animeHud.querySelector('#animeCineNext').onclick=()=>{
    animeSeek(storyTimeline().beats.find(beat=>beat.time>animeCine.elapsed+.25)?.time??storyTimeline().duration);
  };
  animeCine.layerSettings.guardian=false;storyRender();return result;
};
animeEndCinematic=function(){
  const result=storyEndCinematic();if(storyEnvironmentSnapshot){
    scene.background.copy(storyEnvironmentSnapshot.background);scene.overrideMaterial=storyEnvironmentSnapshot.override;
    for(const [object,visible] of storyEnvironmentSnapshot.hidden)object.visible=visible;storyEnvironmentSnapshot=null;
  }return result;
};
function storyApplyOpacity(group,value){group.traverse(o=>{for(const material of Array.isArray(o.material)?o.material:o.material?[o.material]:[]){
  if(value<1&&!material.transparent){material.transparent=true;material.needsUpdate=true;}
  material.opacity=value;
}});}
function storyForegroundInkHeight(group){
  const card=group.children[0],visual=card?.userData.storyVisual;
  const inkHeight=(visual?.height||STORY_VISUALS.foreground.height)*
    (card?.children.find(o=>o.isMesh)?.material.map?.userData.storyInkHeight??1);
  return (inkHeight*Math.cos(card?.rotation.x||0)*Math.cos(group.rotation.z)+
    (visual?.width||STORY_VISUALS.foreground.width)*.5*Math.abs(Math.sin(group.rotation.z)))*group.scale.y;
}
function storyCastFloor(c){
  scene.updateMatrixWorld(true);
  const visible=[c.cast.kami,c.cast.wisp].filter(group=>group.visible);
  return visible.length?Math.min(...visible.map(group=>new THREE.Box3().setFromObject(group).min.y)):Infinity;
}
function storyRender(){
  const c=animeCine;if(!c)return;
  const t=c.elapsed,model=storyTimeline(),beat=storyBeat(t),cam=storySample('camera',t);
  const minimumWidth=9.7,aspect=perspectiveCamera.aspect||1;
  // On portrait screens widen the camera's distance rather than cropping one
  // of the independently authored characters out of the frame.
  const mobileFit=minimumWidth/(2*Math.tan(THREE.MathUtils.degToRad(cam.fov)*.5)*aspect);
  perspectiveCamera.fov=cam.fov;perspectiveCamera.position.set(cam.x,cam.y,Math.max(cam.z,mobileFit));
  perspectiveCamera.lookAt(cam.tx,cam.ty,cam.tz);perspectiveCamera.updateProjectionMatrix();perspectiveCamera.updateMatrixWorld(true);
  const kami=storySample('kami',t),swyrlz=storySample('swyrlz',t),backLimit=Math.min(kami.z,swyrlz.z)-1.6;
  for(const [id,group] of [['kami',c.cast.kami],['swyrlz',c.cast.wisp]]){
    const key=id==='kami'?kami:swyrlz;
    const cfg=animePopConfig().layers[id];
    group.position.set(key.x+(cfg.offsetX-ANIME_POP_DEFAULT[id].offsetX),key.y,key.z);
    group.rotation.set(0,0,key.rotation);group.scale.setScalar(key.scale);
    const pivot=group.children.find(child=>child.userData.storyCastHinge);
    if(pivot)pivot.rotation.x=-(1-key.unfold)*Math.PI*.5;
    group.visible=key.visible&&key.opacity>.01&&storyAuthoredVisible(id)&&c.layerSettings[id]!==false&&c.layerSettings.characters!==false;
    storyApplyOpacity(group,key.opacity);
  }
  const castFloor=storyCastFloor(c);
  for(const id of ['background','atmosphere','midground','effects','foreground']){
    const key=storySample(id,t),group=c.layers[id],card=group.children[0],cfg=animePopConfig().layers[id];
    group.visible=key.visible&&key.opacity>.01&&storyAuthoredVisible(id)&&c.layerSettings[id]!==false;
    const z=id==='foreground'?Math.min(key.z,1.5):Math.min(key.z,backLimit);
    group.position.set(key.x+cam.x*cfg.parallax*.3,key.y,z);
    group.rotation.set(0,0,key.rotation);group.scale.setScalar(id==='foreground'?Math.min(1,key.scale):key.scale);
    if(card){
      card.position.set(0,0,0);
      // Folding plates swing away from the camera: their top edges move
      // toward negative Z, retaining a clear corridor even before fully open.
      card.rotation.x=-(1-key.unfold)*Math.PI*.5;
      storyApplyOpacity(card,key.opacity);
    }
    if(id==='foreground'){
      // Use the actual cutout bounds; imported opaque art receives the same
      // camera protection as the bundled low strip.
      group.position.y=Math.min(key.y,castFloor-.35-storyForegroundInkHeight(group));
    }
  }
  const book=c.layers.book.children[0],bk=storySample('book',t);
  if(book){
    book.position.set(bk.x,bk.y,Math.min(bk.z,-1.8));
    book.position.y=Math.min(book.position.y,castFloor-.3-.25);
    book.scale.setScalar(Math.min(1.15,bk.scale));book.rotation.set(0,0,bk.rotation);
    for(const page of book.children.filter(o=>o.userData.storyPage)){
      const side=page.position.x<0?-1:1;page.rotation.z=side*(1-bk.unfold)*1.35;
    }
    if(Number.isFinite(castFloor)){
      scene.updateMatrixWorld(true);
      const top=new THREE.Box3().setFromObject(book).max.y,limit=castFloor-.3;
      if(top>limit)book.position.y-=top-limit;
    }
    book.visible=bk.visible&&bk.opacity>.01&&storyAuthoredVisible('book');storyApplyOpacity(book,bk.opacity);
  }
  c.cast.dragon.visible=false;c.stage=beat.index;c.cameraDelta=cam.x;
  c.particlesMaterial.color.set('#f4bd65');c.particlesMaterial.opacity=.32;
  const particles=c.particlesGeometry.getAttribute('position');
  for(let i=0;i<particles.count;i++)particles.setXYZ(i,Math.sin(t*.18+i*2.12)*4,1+((i*.577+t*.14)%6),-2-Math.abs(Math.cos(i*3.1+t*.12))*4);
  particles.needsUpdate=true;c.lamp.position.set(0,6,1);
  // Runtime visibility updates are allowed to recompute native editor actors;
  // cinematic clones remain the only authored stage visible in this pass.
  for(const [actor] of c.hiddenActors)actor.visible=false;
  if(storyEnvironmentSnapshot)for(const [object] of storyEnvironmentSnapshot.hidden)object.visible=false;
  animeHud.querySelector('#animeCineScene').textContent=String(beat.index+1).padStart(2,'0')+' · '+beat.title;
  animeHud.querySelector('#animeCineCaption').textContent=beat.cue||'';
  animeHud.querySelector('.anime-cine-title small').textContent=model.title;
  animeUpdateControls();
}
animeUpdateCinematic=function(dt){
  const c=animeCine;if(!c||!playing&&!storyPreviewActive)return;
  const duration=storyTimeline().duration;
  if(playing&&!paused&&!c.ended)c.elapsed=Math.min(duration,c.elapsed+Math.max(0,Math.min(dt||0,.06)));
  if(c.elapsed>=duration&&playing&&!c.ended){c.ended=true;paused=true;setSessionButtons();}
  storyRender();
};
animeUpdateControls=function(){
  if(!animeCine||!animeHud)return;
  const duration=storyTimeline().duration,c=animeCine;
  animeHud.querySelector('#animeCinePause').textContent=c.ended?'↻ Replay':paused?'▶ Resume':'⏸ Pause';
  const scrub=animeHud.querySelector('#animeCineScrub');scrub.max=String(duration);scrub.value=String(c.elapsed);
  animeHud.querySelector('#animeCineTime').textContent=animeClock(c.elapsed)+' / '+animeClock(duration);
};
animeSeek=function(value){
  if(!animeCine)return false;
  animeCine.elapsed=storyNumber(value,0,0,storyTimeline().duration);animeCine.ended=false;
  storyRender();return true;
};
function storyPreview(time=8){
  if(currentProject?.canonicalId!=='ghosts-different-forms-ep01')return false;
  if(playing){const wasPaused=paused;animeSeek(time);paused=wasPaused;return true;}
  if(!storyPreviewActive){
    storyRememberCamera();storyPreviewActive=true;transform.detach();orbit.enabled=false;setActiveCamera(perspectiveCamera);animeStartCinematic();
    animeHud.classList.remove('show');document.querySelector('.app')?.classList.add('story-preview');
  }
  animeCine.elapsed=storyNumber(time,8,0,storyTimeline().duration);storyRender();return true;
}
function storyExitPreview(){
  if(!storyPreviewActive)return;
  storyPreviewActive=false;animeEndCinematic();document.querySelector('.app')?.classList.remove('story-preview');storyRestoreCamera();
}
const storyClearAll=clearAll,storyBeginPlay=beginPlay,storyStopSession=stopSession;
clearAll=function(){storyExitPreview();return storyClearAll();};
beginPlay=function(fromHere=null){storyExitPreview();storyRememberCamera();return storyBeginPlay(fromHere);};
stopSession=function(){
  if(storyPreviewActive){storyExitPreview();return;}
  const result=storyStopSession();storyRestoreCamera();return result;
};
function storyScreenRect(group){
  const box=new THREE.Box3().setFromObject(group),points=[];
  for(const x of [box.min.x,box.max.x])for(const y of [box.min.y,box.max.y])for(const z of [box.min.z,box.max.z]){
    const v=new THREE.Vector3(x,y,z).project(perspectiveCamera);points.push(v);
  }
  const left=Math.min(...points.map(v=>v.x))*.5+.5,right=Math.max(...points.map(v=>v.x))*.5+.5;
  const top=.5-Math.max(...points.map(v=>v.y))*.5,bottom=.5-Math.min(...points.map(v=>v.y))*.5;
  return {left,right,top,bottom,width:right-left,height:bottom-top,normalized:true};
}
function storyStageStatus(){
  const c=animeCine;
  const editorCamera={view:editorCameraView,position:camera.position.toArray(),quaternion:camera.quaternion.toArray(),
    up:camera.up.toArray(),zoom:camera.zoom,fov:perspectiveCamera.fov,target:orbit.target.toArray(),orbitEnabled:orbit.enabled};
  if(!c)return {active:false,preview:false,assetsReady:storyAssetPending.size===0,assetErrors:[...storyAssetErrors],
    actorBindings:actors.filter(a=>a.userData.tags.includes('anime-stage')).map(a=>({id:a.userData.id,layer:a.userData.storyVisual?.layer||'book',layerIds:a.userData.editorLayerIds})),editorCamera};
  scene.updateMatrixWorld(true);perspectiveCamera.updateMatrixWorld(true);
  const castBounds=[['kami',c.cast.kami],['swyrlz',c.cast.wisp]].map(([id,group])=>({id,visible:group.visible,...storyScreenRect(group)}));
  const castZ=Math.min(c.cast.kami.position.z,c.cast.wisp.position.z),scenery=[];
  for(const id of ['background','atmosphere','midground','effects','foreground']){
    const group=c.layers[id];scenery.push({id,z:group.position.z,frontZ:new THREE.Box3().setFromObject(group).max.z,inkTopY:id==='foreground'?group.position.y+storyForegroundInkHeight(group):undefined});
  }
  const front=c.layers.foreground,book=c.layers.book.children[0],bookBox=new THREE.Box3().setFromObject(book),foregroundInkTopY=scenery.at(-1).inkTopY;
  const safeCameraGap=perspectiveCamera.position.z-Math.max(front.position.z,c.cast.kami.position.z,c.cast.wisp.position.z);
  const castFloor=storyCastFloor(c);
  const castProtected=(!front.visible||foregroundInkTopY<castFloor-.25)&&(!book.visible||bookBox.max.y<castFloor-.25);
  const occlusionSafe=scenery.slice(0,4).every(s=>s.frontZ<castZ-1)&&safeCameraGap>6&&castProtected;
  return {active:!!playing,preview:storyPreviewActive,assetsReady:storyAssetPending.size===0,assetErrors:[...storyAssetErrors],
    actorBindings:actors.filter(a=>a.userData.tags.includes('anime-stage')).map(a=>({id:a.userData.id,layer:a.userData.storyVisual?.layer||'book',layerIds:a.userData.editorLayerIds})),
    layers:Object.fromEntries(Object.entries(c.layers).map(([id,g])=>[id,{visible:g.visible,children:g.children.length}])),
    castBounds,scenery,camera:{position:perspectiveCamera.position.toArray(),near:perspectiveCamera.near,far:perspectiveCamera.far},
    occlusionSafe,bookVisible:book.visible&&c.layers.book.visible,bookBounds:{min:bookBox.min.toArray(),max:bookBox.max.toArray()},bookTopY:bookBox.max.y,foregroundInkTopY,safeCameraGap,editorCamera};
}
animePopupStageSafety=function(c){
  if(!c)return null;const s=storyStageStatus();
  return {bookY:s.bookTopY-.25,bookTopY:s.bookTopY,foregroundInkTopY:s.foregroundInkTopY,
    kamiBottomY:c.cast.kami.position.y-3*c.cast.kami.scale.y,characterZ:c.cast.kami.position.z,
    swyrlzZ:c.cast.wisp.position.z,cathedralZ:c.layers.midground.position.z,cameraFrontGap:s.safeCameraGap};
};
window.SWYRL_ENGINE_STORYBOARD=Object.freeze({buildStage:storyBuildStage,bindArtwork:storyBindArtwork,captureActorPose:storyCaptureActorPose,
  preview:storyPreview,exitPreview:storyExitPreview,stageStatus:storyStageStatus,
  importProject:data=>{storyExitPreview();if(playing||simulating)stopSession();loadProject(storyCopy(data));syncAnimeScreening();return true;}});
