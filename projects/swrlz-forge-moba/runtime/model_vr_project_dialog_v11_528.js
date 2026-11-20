/* SE528_XR_PROJECT_DIALOG_START */
// A spacious, single-world-space Projects dialog, sharing the established VR
// document/library controller and the existing three-stage menu's ray pipeline.
// No DOM sheet, second XR scene, second persistence store, or direct cloud RPC.
(function(){
 'use strict';
 const priorCreate=se340CreateModelVRUI;
 se340CreateModelVRUI=function(options){
  const ui=priorCreate(options),T=options.THREE,root=ui.root;
  const modal=new T.Group();modal.name='§E · Project and confirmation dialog';
  modal.position.set(-.205,0,.155);root.add(modal);modal.visible=false;
  const owned=[],targets=[],regions=[],W=.94,H=.77,CW=1504,CH=1232;
  const canvas=document.createElement('canvas');canvas.width=CW;canvas.height=CH;
  const c=canvas.getContext('2d');if(!c)throw Error('XR project dialog requires canvas');
  const texture=new T.CanvasTexture(canvas);texture.colorSpace=T.SRGBColorSpace;
  texture.minFilter=T.LinearFilter;texture.magFilter=T.LinearFilter;owned.push(texture);
  const mat=new T.MeshBasicMaterial({map:texture,side:T.DoubleSide,depthTest:false,
   depthWrite:false,transparent:true,toneMapped:false});
  const plane=new T.PlaneGeometry(W,H);
  const surface=new T.Mesh(plane,mat);surface.position.z=.012;surface.renderOrder=8851;
  surface.userData={editorOnly:true,se340UI:true,se340Block:true,se528Modal:true};
  modal.add(surface);owned.push(mat,plane);targets.push(surface);
  const hitMat=new T.MeshBasicMaterial({color:0xffffff,transparent:true,opacity:0,
   depthTest:false,depthWrite:false,side:T.DoubleSide});
  owned.push(hitMat);
  let active='',selectedHover='',lastSignature='',disposed=false,note='',busy=false;
  let awaitingPose=null,openedToken=null;
  const actions=[
   ['project-dialog-close',.417,.327,.060,.061],
   ['project-source-local',-.312,.235,.284,.062],
   ['project-source-cloud',0,.235,.284,.062],
   ['project-source-starter',.312,.235,.284,.062],
   ['project-pick-0',-.225,.105,.430,.121],
   ['project-pick-1',.225,.105,.430,.121],
   ['project-pick-2',-.225,-.031,.430,.121],
   ['project-pick-3',.225,-.031,.430,.121],
   ['project-page-prev',-.339,-.153,.210,.060],
   ['project-page-next',-.108,-.153,.210,.060],
   ['project-refresh',.124,-.153,.210,.060],
   ['project-open',.333,-.153,.180,.060],
   ['project-save-local',-.312,-.264,.280,.070],
   ['project-save-account',0,-.264,.296,.070],
   ['project-clone',.312,-.264,.280,.070],
   ['project-rest-confirm',-.192,-.233,.330,.076],
   ['project-rest-cancel',.192,-.233,.330,.076]
  ];
  for(const [id,x,y,w,h] of actions){
   const geometry=new T.PlaneGeometry(w,h),mesh=new T.Mesh(geometry,hitMat);
   mesh.position.set(x,y,.043);mesh.renderOrder=8860;mesh.visible=false;
   mesh.userData={editorOnly:true,se340UI:true,se528Modal:true,se340Action:id};
   modal.add(mesh);owned.push(geometry);targets.push(mesh);
   regions.push({id,x,y,w,h,mesh});
  }
  const xpx=x=>(x+W/2)*CW/W,ypx=y=>(H/2-y)*CH/H;
  function rect(x,y,w,h,fill,stroke=null,r=15){
   c.beginPath();if(c.roundRect)c.roundRect(xpx(x-w/2),ypx(y+h/2),w*CW/W,h*CH/H,r);
   else c.rect(xpx(x-w/2),ypx(y+h/2),w*CW/W,h*CH/H);
   c.fillStyle=fill;c.fill();
   if(stroke){c.strokeStyle=stroke;c.lineWidth=2;c.stroke();}
  }
  function words(t,max=42){t=String(t||'');return t.length<=max?t:t.slice(0,max-1)+'…';}
  function txt(t,x,y,size=27,color='#e8edf9',weight=600,align='left'){
   c.font=weight+' '+size+'px system-ui';c.fillStyle=color;
   c.textAlign=align;c.textBaseline='middle';c.fillText(t,xpx(x),ypx(y));
  }
  function button(id,label,{on=true,selected=false}={}){
   const r=regions.find(e=>e.id===id);if(!r)return;
   r.mesh.visible=active==='projects'&&(id!=='project-rest-confirm'&&id!=='project-rest-cancel')||
     active==='rest'&&(id==='project-dialog-close'||id==='project-rest-confirm'||id==='project-rest-cancel');
   if(!r.mesh.visible)return;
   const hover=selectedHover===id;
   rect(r.x,r.y,r.w,r.h,!on?'#272b3b':selected?'#2b6864':hover?'#394b67':'#293448',
    !on?'#39465a':selected?'#8af0d1':hover?'#c4efff':'#526a82',12);
   txt(words(label,25),r.x,r.y,25,on?'#eef8ff':'#8292a6',selected?760:630,'center');
  }
  function draw(){
   if(!active||disposed)return;
   c.clearRect(0,0,CW,CH);
   for(const region of regions)region.mesh.visible=false;
   rect(0,0,W,H,'#151c2b','#8aa0b4',28);
   rect(0,.333,W,.102,'#212d45',null,24);
   txt(active==='rest'?'REST POSE REQUIRED':'MY PROJECTS',-.422,.332,42,'#f7f8ff',800);
   button('project-dialog-close','×');
   if(active==='rest'){
    txt('Sculpt requires the neutral skeleton.',-.397,.138,32,'#e5ebff',670);
    txt('Set this rig to rest pose before Push / Pull?',-.397,.062,30,'#c9d8e7',570);
    txt('Your current pose is added to rig Undo history.',-.397,-.025,25,'#9ab9c6',550);
    txt('No skin weights, geometry or animation keys are deleted.',-.397,-.086,23,'#abc8c3',550);
    button('project-rest-confirm','Set Rest Pose');
    button('project-rest-cancel','Keep Pose');
    txt(words(note||'Choose an action to continue.',80),-.410,-.338,22,'#aacecf',550);
    return;
   }
   const info=se517XRProjects.inspect(),ops=se517XRProjects.operations();
   const labels=new Map(ops.filter(Boolean).map(r=>r));
   const connected=window.SWYRL_ENGINE_VR_PROJECTS_372?.status?.().connected===true;
   txt(words(note||'Choose Device, Account or Starters, then open a project.',74),
    -.418,.280,23,'#aecfda',550);
   for(const [id,title] of [['project-source-local','On device'],
    ['project-source-cloud','My account'],['project-source-starter','Starters']]){
    button(id,title,{selected:info.source===id.slice('project-source-'.length)});
   }
   const names=[0,1,2,3].map(i=>labels.get('project-pick-'+i)||'');
   for(let i=0;i<4;i++){
    const id='project-pick-'+i,r=regions.find(x=>x.id===id),label=names[i];
    r.mesh.visible=!!label;
    rect(r.x,r.y,r.w,r.h,label?.startsWith('●')?'#253b4a':'#202d43',
     label?.startsWith('●')?'#9bf6d5':'#475872',13);
    rect(r.x-r.w/2+.068,r.y,.107,.087,'#2b4a5d','#6a98a7',9);
    txt(info.source==='cloud'?'☁':info.source==='starter'?'◇':'▣',
      r.x-r.w/2+.068,r.y,38,'#a6f3df',750,'center');
    txt(label?words(label.replace(/^● /,''),19):'No project',r.x-r.w/2+.136,r.y+.021,25,
      label?'#f1f4fc':'#70829b',700);
    txt(info.source==='cloud'?'Account project':info.source==='starter'?'Model starter':'Device project',
      r.x-r.w/2+.136,r.y-.030,20,'#94b4c7',520);
   }
   button('project-page-prev','Previous');
   button('project-page-next','Next');
   button('project-refresh',info.loading?'Loading…':'Refresh',{on:!busy&&!info.loading});
   button('project-open',labels.get('project-open')?.includes('CONFIRM')?'Confirm':
    info.opening?'Opening…':'Open',{on:!busy&&!info.opening});
   button('project-save-local','Save to device',{on:!busy});
   button('project-save-account',connected?'Save to account':'Connect account',{on:!busy});
   button('project-clone','Clone project',{on:!busy});
   rect(0,-.351,.861,.036,'#1d2b39',null,10);
   txt((info.source==='cloud'?'ACCOUNT':info.source==='starter'?'STARTERS':'DEVICE')+
       ' · '+info.count+' projects'+(connected?' · Google connected':' · account offline'),
       -.408,-.351,20,'#abc0d7',550);
  }
  function setOpen(next){
   if(disposed)return;
   active=next;modal.visible=!!active;selectedHover='';lastSignature='';note='';
   if(next==='projects'){
    openedToken=se340XR.documentToken;
    se517XRProjects.start();
   }
   render();
  }
  function render(){
   if(!active||disposed)return;
   const info=active==='projects'?se517XRProjects.inspect():{};
   const values=active==='projects'?se517XRProjects.operations():[];
   const stamp=JSON.stringify([active,info,values,note,busy,selectedHover,
    window.SWYRL_ENGINE_VR_PROJECTS_372?.status?.().connected]);
   if(stamp===lastSignature)return;lastSignature=stamp;draw();texture.needsUpdate=true;
  }
  function close(){active='';awaitingPose=null;openedToken=null;modal.visible=false;lastSignature='';}
  function showRestPose(id){if(active==='projects')close();awaitingPose=id;setOpen('rest');}
  function confirmRest(){
   const access=window.SWYRL_ENGINE_MODEL_RIG_ACCESS_518;
   const rig=access?.rig?.();
   if(!awaitingPose||!access?.available?.()||!rig?.bones?.length||!rig.pose){
    note='No valid rig to reset. The current pose was not changed.';render();return;
   }
   if(se340XR.gesture){note='Release the current edit first.';render();return;}
   const neutral={};
   for(const bone of rig.bones)neutral[bone.id]=[0,0,0];
   if(!access.validate?.({...rig,pose:neutral})){
    note='The neutral pose failed rig validation. No changes applied.';render();return;
   }
   access.playing=false;access.remember();
   rig.pose=neutral;access.pose(rig.pose);access.jointUI?.();
   access.touched('Rig returned to rest pose for immersive Push / Pull.');
   se350Invalidate();close();
   se340Notice('Rest pose applied. Point at the model and start Push / Pull again.');
   se340SyncUI();se340Publish();
  }
  async function save(which){
   if(busy)return;busy=true;note='Saving active model…';render();
   try{
    const service=window.SWYRL_ENGINE_VR_PROJECTS_372;
    if(!service)throw Error('Project save service not available');
    const result=which==='account'?
     await (window.SWYRL_ENGINE_ACCOUNT_SAVE_528?.save?.()||service.saveAccount()):
     which==='clone'?await service.clone():await service.saveLocal();
    if(!result?.ok)throw Error(result?.detail||result?.error||'Save was not confirmed');
    note=result.name+' · saved '+(which==='account'?'to account':which==='clone'?'as independent copy':'on device');
    await se517XRProjects.refresh();
   }catch(error){note='Save failed: '+String(error?.message||error).slice(0,85);se340Notice(note,true);}
   finally{busy=false;lastSignature='';render();}
  }
  function perform(id){
   if(id==='project-dialog-close'||id==='project-rest-cancel'){close();return;}
   if(active==='rest'){if(id==='project-rest-confirm')confirmRest();return;}
   if(active!=='projects')return;
   if(busy)return;
   if(id==='project-refresh'){void se517XRProjects.refresh();return;}
   if(id==='project-save-local'){void save('device');return;}
   if(id==='project-save-account'){void save('account');return;}
   if(id==='project-clone'){void save('clone');return;}
   if(id.startsWith('project-'))se517XRProjects.action(id);
   lastSignature='';render();
  }
  const priorHit=ui.hitTest,priorPress=ui.press,priorHover=ui.hover,
   priorUpdate=ui.update,priorDispose=ui.dispose;
  function hitTest(ray){
   if(active&&modal.visible&&root.visible){
    modal.updateWorldMatrix(true,true);
    return ray.intersectObjects(targets.filter(t=>t.visible&&t.parent===modal),false)[0]||null;
   }
   return priorHit(ray);
  }
  function press(target){
   if(active){
    const region=regions.find(x=>x.mesh===target&&x.mesh.visible);
    if(region){perform(region.id);return false;}
    return false;
   }
   if(target?.userData?.se340Action==='projects'){
    setOpen('projects');return false;
   }
   return priorPress(target);
  }
  function hover(target){
   if(active){
    const next=regions.find(x=>x.mesh===target&&x.mesh.visible)?.id||'';
    if(selectedHover!==next){selectedHover=next;render();}
    return null;
   }
   return priorHover(target);
  }
  function update(next){
   const result=priorUpdate(next);
   if(active==='projects'&&openedToken&&se340XR.documentToken!==openedToken)close();
   render();return result;
  }
  function dispose(){
   close();disposed=true;modal.removeFromParent();
   for(const resource of owned)resource.dispose?.();
   return priorDispose();
  }
  return Object.freeze({...ui,hitTest,press,hover,update,dispose,
   openProjects:()=>setOpen('projects'),showRestPose,closeDialog:close,isModalOpen:()=>!!active,
   dialogInspect:()=>({active,note,busy,projectRevision:se517XRProjects.inspect().revision})});
 };
 const priorAction=se340ModelXRAction;
 se340ModelXRAction=function(action,record){
  if(action==='cancel'&&se340XR.ui?.isModalOpen?.()){
   se340XR.ui.closeDialog();return true;
  }
  if(action==='projects'){
   if(se340XR.ui?.isModalOpen?.())se340XR.ui.closeDialog();
   else se340XR.ui?.openProjects?.();
   return true;
  }
  // Modal action buttons use the dialog's native ray targets. Suppress global
  // Undo/Delete, tool mode changes and palette hide while confirmation is open.
  if(se340XR.ui?.isModalOpen?.())return true;
  return priorAction.apply(this,arguments);
 };
 const priorBegin=se340BeginGesture;
 se340BeginGesture=function(...args){
  if(se340XR.ui?.isModalOpen?.())return false;
  return priorBegin.apply(this,args);
 };
 const priorTrigger=se340Trigger;
 se340Trigger=function(record,additive=false){
  if(se340XR.ui?.isModalOpen?.()){
   if(!record?.targetTracked)return false;
   const hit=se340Hit(record,false);
   if(hit?.ui&&hit.target?.userData?.se528Modal)se340XR.ui.press(hit.target);
   return false; // no model selection/sculpt behind a modal
  }
  return priorTrigger.apply(this,arguments);
 };
 const priorStroke=se350BeginStroke;
 se350BeginStroke=function(record,hit){
  const result=priorStroke.apply(this,arguments);
  if(result===false&&['push','translate'].includes(se340XR.sculptTool)&&
     se350Surface()?.inspect?.()?.error==='SCULPT_REQUIRES_BIND_POSE'&&hit?.id){
   se340XR.ui?.showRestPose?.(hit.id);
  }
  return result;
 };
})();
/* SE528_XR_PROJECT_DIALOG_END */