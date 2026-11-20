/* SE528_XR_RAY_AND_PARAMETER_CONTROLS_START */
// Controller-ray-driven native transform gestures. The original gizmo, native
// begin/update/end transaction, checkpoint and B cancel remain authoritative.
(function(){
 'use strict';
 const previousPose=se390UpdatePose;
 function rayWorld(g){
  const cast=se340Cast(g.record);
  return cast&&cast.ray?.origin?.isVector3?cast.ray:null;
 }
 function createRayState(g){
  const ray=rayWorld(g),pivot=se340XR.se372Gizmo?.root?.position?.clone();
  if(!ray||!pivot)return null;
  const axis=g.axis==='x'?new THREE.Vector3(1,0,0):
   g.axis==='y'?new THREE.Vector3(0,1,0):
   g.axis==='z'?new THREE.Vector3(0,0,1):null;
  const axisWorld=axis?.clone().applyQuaternion(g.rootQuaternion).normalize()||null;
  let normal;
  if(g.mode==='rotate'&&axisWorld)normal=axisWorld.clone();
  else if(g.mode==='move'&&axisWorld){
   const sight=ray.origin.clone().sub(pivot).normalize();
   normal=axisWorld.clone().cross(sight).cross(axisWorld).normalize();
   if(normal.lengthSq()<.01)normal=axisWorld.clone().cross(
    Math.abs(axisWorld.y)<.85?new THREE.Vector3(0,1,0):new THREE.Vector3(0,0,1)).cross(axisWorld).normalize();
  }else normal=ray.direction.clone().negate();
  if(!normal||normal.lengthSq()<.01)return null;
  const plane=new THREE.Plane().setFromNormalAndCoplanarPoint(normal,pivot);
  const point=ray.intersectPlane(plane,new THREE.Vector3());
  if(!point)return null;
  return {plane,pivot,axis,axisWorld,last:point,translation:new THREE.Vector3(),
   rotation:new THREE.Quaternion(),logScale:0,scaleAxis:normal.clone().cross(new THREE.Vector3(1,0,0)).normalize(),
   gain:null};
 }
 se390UpdatePose=function(g,pose,gain){
  if(!(g?.se512Trigger||['x','y','z','uniform'].includes(g?.axis))||!['move','rotate','scale'].includes(g.mode))
   return previousPose.apply(this,arguments);
  let state=g.se528Ray;
  if(!state){state=createRayState(g);if(!state)return;g.se528Ray=state;}
  const ray=rayWorld(g);if(!ray)return;
  const point=ray.intersectPlane(state.plane,new THREE.Vector3());
  if(!point)return; // never substitute grip motion after a ray drag begins
  const fine=Number.isFinite(gain)?THREE.MathUtils.clamp(gain,.02,1):1;
  if(state.gain!==null&&Math.abs(state.gain-fine)>.0001){
   // Precision clutch: do not reinterpret already-applied movement.
   state.last.copy(point);state.gain=fine;return;
  }
  state.gain=fine;
  const step=point.clone().sub(state.last),localAxis=state.axis;
  if(g.mode==='move'&&state.axisWorld){
   const worldDelta=state.axisWorld.clone().multiplyScalar(step.dot(state.axisWorld)*fine);
   const start=state.pivot.clone().applyMatrix4(g.rootInverse);
   const end=state.pivot.clone().add(worldDelta).applyMatrix4(g.rootInverse);
   state.translation.add(end.sub(start));
  }else if(g.mode==='rotate'&&localAxis){
   const from=state.last.clone().sub(state.pivot);
   const to=point.clone().sub(state.pivot);
   if(from.lengthSq()>.000025&&to.lengthSq()>.000025){
    const ang=Math.atan2(state.axisWorld.dot(from.clone().cross(to)),from.dot(to))*fine;
    const dq=new THREE.Quaternion().setFromAxisAngle(localAxis,THREE.MathUtils.clamp(ang,-.45,.45));
    state.rotation.premultiply(dq).normalize();
   }
  }else if(g.mode==='scale'){
   const up=new THREE.Vector3(0,1,0).projectOnPlane(state.plane.normal).normalize();
   const direction=up.lengthSq()>.01?up:new THREE.Vector3(1,0,0).projectOnPlane(state.plane.normal).normalize();
   state.logScale=THREE.MathUtils.clamp(state.logScale+step.dot(direction)*fine*3.4,-4.6,4.6);
  }
  state.last.copy(point);
  const translation=state.translation.clone(),rotation=state.rotation.clone();
  let scale=Math.exp(state.logScale);
  if(se340XR.snap){
   for(let i=0;i<3;i++)translation.setComponent(i,Math.round(translation.getComponent(i)/.01)*.01);
   if(g.mode==='rotate'){
    const axis=localAxis||new THREE.Vector3(0,1,0),q=new THREE.Quaternion();
    const angle=2*Math.atan2(new THREE.Vector3(rotation.x,rotation.y,rotation.z).dot(axis),rotation.w);
    const radians=THREE.MathUtils.degToRad(se340XR.inputSample?.thresholds.snapDegrees||15);
    q.setFromAxisAngle(axis,Math.round(angle/radians)*radians);rotation.copy(q);
   }
   scale=1+Math.round((scale-1)/.05)*.05;
  }
  se372Constrain(g,translation,rotation);
  se372GuideUpdate(g,translation,rotation,scale);
  const result=se350Tools().updateGroup({translation:translation.toArray(),rotation:rotation.toArray(),scale});
  if(result?.ok===false)se340CancelGesture(result.error||'Native ray transform canceled.');
 };
 // Quest Touch left application Menu is commonly gamepad button 6; Meta Quest
 // Browser may reserve it, in which case keep the existing X shortcut intact.
 let heldMenu=false;
 const previousDispatch=se350Dispatch;
 se350Dispatch=function(sample){
  const left=se350Record('left');
  const button=left?.input?.gamepad?.buttons?.[6];
  const exposed=!!button;
  const down=exposed&&(button.pressed===true||Number(button.value)>.6);
  if(exposed&&down&&!heldMenu&&left?.targetTracked&&left?.gripTracked&&
     se340VisibleSession()&&!sample?.resetRequired&&!sample?.cancel){
   se340ModelXRAction('palette',left);
  }
  heldMenu=!!down;
  return previousDispatch(sample);
 };
 const priorCleanup=se340Cleanup;
 se340Cleanup=function(...args){heldMenu=false;return priorCleanup.apply(this,args);};
 window.SWYRL_ENGINE_MODEL_VR_RAY_528=Object.freeze({
  inspect:()=>({leftMenuExposed:!!se350Record('left')?.input?.gamepad?.buttons?.[6],
   gestureRay:!!se340XR.gesture?.se528Ray,mode:se340XR.gesture?.mode||null})});
})();
// Unified contextual +/- inspector toolbar: never duplicates the native
// adjustment actions; redirects their already-authenticated ray selection.
(function(){
 'use strict';
 const priorCreate=se340CreateModelVRUI;
 se340CreateModelVRUI=function(options){
  const ui=priorCreate(options),T=options.THREE;
  const details=ui.root.getObjectByName('Model VR · native modifier panel');
  if(!details)return ui;
  const bar=new T.Group();bar.name='§E · contextual parameter toolbar';details.add(bar);
  bar.position.set(-.380,-.005,.088);bar.visible=false;
  const owned=[],targets=[],buttons=[],hidden=[];
  const cv=document.createElement('canvas');cv.width=850;cv.height=870;
  const c=cv.getContext('2d');if(!c)throw Error('Native VR parameter toolbar requires canvas');
  const texture=new T.CanvasTexture(cv);texture.colorSpace=T.SRGBColorSpace;
  texture.minFilter=T.LinearFilter;texture.magFilter=T.LinearFilter;
  const mat=new T.MeshBasicMaterial({map:texture,side:T.DoubleSide,depthTest:false,
   depthWrite:false,transparent:true,toneMapped:false});
  const background=new T.Mesh(new T.PlaneGeometry(.35,.36),mat);
  background.renderOrder=8575;background.position.z=.008;
  background.userData={se340UI:true,editorOnly:true,se340Block:true};
  bar.add(background);owned.push(texture,mat,background.geometry);
  const hitMat=new T.MeshBasicMaterial({color:0xffffff,transparent:true,opacity:0,
   depthTest:false,depthWrite:false,side:T.DoubleSide});owned.push(hitMat);
  for(let i=0;i<6;i++)for(const side of ['minus','plus']){
   const mesh=new T.Mesh(new T.PlaneGeometry(.072,.046),hitMat);
   mesh.position.set(side==='minus'?-.124:.124,.092-i*.0505,.027);
   mesh.userData={editorOnly:true,se340UI:true,se528Parameter:true,se340Action:''};
   mesh.visible=false;mesh.renderOrder=8581;bar.add(mesh);owned.push(mesh.geometry);
   buttons.push({mesh,i,side});targets.push(mesh);
  }
  let groups=[],hover='',signature='',disposed=false;
  const cap=t=>String(t||'').replace(/^brush-/,'').replace(/^rig-/,'').replace(/^accessory-/,'').replaceAll('-',' ');
  function render(){
   if(!bar.visible)return;
   const vals=groups.map(g=>{
    if(g.id==='brush-radius')return Number(se340XR.brushRadius).toFixed(3);
    if(g.id==='brush-strength')return Math.round((se340XR.brushStrength||0)*100)+'%';
    const rig=typeof se514RigXR!=='undefined'?se514RigXR.uiState():null;
    if(g.id==='rig-radius')return Number(rig?.rigRadius||0).toFixed(3);
    if(g.id==='rig-strength')return Math.round((rig?.rigStrength||0)*100)+'%';
    return 'Adjust';
   });
   const state=JSON.stringify([groups.map(g=>g.id),vals,hover]);
   if(signature===state)return;signature=state;
   const h=cv.height,w=cv.width;c.clearRect(0,0,w,h);
   c.fillStyle='#1b293e';c.fillRect(0,0,w,h);
   c.strokeStyle='#7e9fb2';c.lineWidth=5;c.strokeRect(3,3,w-6,h-6);
   c.font='700 40px system-ui';c.fillStyle='#c0f2e5';c.fillText('PARAMETERS',36,64);
   for(let i=0;i<groups.length;i++){
    const y=140+i*122;
    c.fillStyle='#243951';c.fillRect(20,y,810,105);
    c.strokeStyle='#5e8593';c.strokeRect(20,y,810,105);
    c.font='650 34px system-ui';c.fillStyle='#e8f5ff';c.fillText(cap(groups[i].id).toUpperCase(),45,y+35);
    c.font='650 31px system-ui';c.fillStyle='#a7d6d6';c.fillText(vals[i],390,y+72);
    for(const side of ['minus','plus']){
     const x=side==='minus'?60:655,id=groups[i][side];
     c.fillStyle=hover===id?'#377975':'#345466';c.fillRect(x,y+50,118,47);
     c.strokeStyle=hover===id?'#b9ffe0':'#7198a7';c.strokeRect(x,y+50,118,47);
     c.fillStyle='#f7ffff';c.font='800 43px system-ui';c.textAlign='center';
     c.fillText(side==='minus'?'−':'+',x+59,y+86);c.textAlign='left';
    }
   }
   texture.needsUpdate=true;
  }
  const priorUpdate=ui.update,priorHit=ui.hitTest,priorPress=ui.press,
   priorHover=ui.hover,priorDispose=ui.dispose;
  function restore(){for(const t of hidden)t.visible=true;hidden.length=0;}
  function update(next){
   restore();
   const result=priorUpdate(next),info=ui.inspect?.();
   const contextual=!!info?.settingsOpen&&info.drawerProgress>.88;
   const pairs=new Map();
   if(contextual)for(const t of ui.targets||[]){
    if(!t?.visible||!t.userData?.se340Action)continue;
    let parent=t.parent,inside=false;
    for(let n=0;n<8&&parent;n++,parent=parent.parent)if(parent===details){inside=true;break;}
    if(!inside)continue;
    const m=/^(.+)-(minus|plus)$/.exec(t.userData.se340Action);
    if(!m)continue;
    const p=pairs.get(m[1])||{id:m[1],minus:null,plus:null,originals:[]};
    p[m[2]]=m[0];p.originals.push(t);pairs.set(m[1],p);
   }
   groups=[...pairs.values()].filter(x=>x.minus&&x.plus).slice(0,6);
   for(const g of groups)for(const t of g.originals){hidden.push(t);t.visible=false;}
   bar.visible=groups.length>0;
   for(const b of buttons){
    const g=groups[b.i];
    b.mesh.visible=bar.visible&&!!g;
    b.mesh.userData.se340Action=g?.[b.side]||'';
   }
   signature='';render();return result;
  }
  function hitTest(ray){
   if(bar.visible&&!ui.isModalOpen?.()){
    bar.updateWorldMatrix(true,true);
    const item=ray.intersectObjects(targets.filter(t=>t.visible),false)[0];
    if(item)return item;
   }
   return priorHit(ray);
  }
  function press(target){
   if(target?.userData?.se528Parameter)return true;
   return priorPress(target);
  }
  function hover(target){
   if(bar.visible&&target?.userData?.se528Parameter){
    const id=target.userData.se340Action;
    if(id!==hover){hover=id;signature='';render();}
    return null;
   }
   if(hover){hover='';signature='';render();}
   return priorHover(target);
  }
  function dispose(){restore();disposed=true;bar.removeFromParent();
   for(const resource of owned)resource.dispose?.();return priorDispose();}
  return Object.freeze({...ui,update,hitTest,press,hover,dispose,
   parametersInspect:()=>({groups:groups.map(g=>g.id),visible:bar.visible})});
 };
})();
/* SE528_XR_RAY_AND_PARAMETER_CONTROLS_END */