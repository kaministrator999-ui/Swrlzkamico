/* SE443_MODEL_VR_VERTICAL_DOCK_START */
// Presentation-only wrapper around the existing VR console. Native actions,
// history, controller input, menu Grip gesture and tutorial remain authoritative.
(function(){
 'use strict';
 const previousCreate=se340CreateModelVRUI;
 se340CreateModelVRUI=function(options){
  const ui=previousCreate(options),T=options.THREE,root=ui.root;
  const originalChildren=[...root.children],drawer=new T.Group();
  drawer.name='Model VR · attached right-side tool settings';
  root.add(drawer);
  for(const child of originalChildren)drawer.add(child);
  const dock=new T.Group();dock.name='Model VR · permanent vertical tools';root.add(dock);
  const owned=[],targets=[],rows=[];
  const material=(texture)=>new T.MeshBasicMaterial({map:texture,transparent:true,depthTest:false,depthWrite:false,toneMapped:false,side:T.DoubleSide});
  const make=(name,w,h,x,y,paint,z=.035)=>{
   const canvas=document.createElement('canvas');canvas.width=Math.max(1,Math.round(w*2300));canvas.height=Math.max(1,Math.round(h*2300));
   const ctx=canvas.getContext('2d');if(!ctx)throw Error('VR tool dock requires 2D canvas');
   const texture=new T.CanvasTexture(canvas);texture.colorSpace=T.SRGBColorSpace;texture.minFilter=T.LinearFilter;texture.magFilter=T.LinearFilter;
   const mat=material(texture),geo=new T.PlaneGeometry(w,h),mesh=new T.Mesh(geo,mat);
   owned.push(geo,mat,texture);mesh.name=name;mesh.position.set(x,y,z);mesh.renderOrder=8400;mesh.frustumCulled=false;mesh.userData.editorOnly=true;mesh.userData.se340UI=true;
   (name==='Dock back'?dock:mesh.userData.se443Close?drawer:dock).add(mesh);
   return {mesh,ctx,canvas,texture,paint:()=>{ctx.clearRect(0,0,canvas.width,canvas.height);paint(ctx,canvas.width,canvas.height);texture.needsUpdate=true;}};
  };
  const back=make('Dock back',.19,.83,-.325,0,(c,w,h)=>{
   c.fillStyle='#171c2c';c.fillRect(0,0,w,h);c.strokeStyle='#746b91';c.lineWidth=5;c.strokeRect(3,3,w-6,h-6);
   c.fillStyle='#b8f3e1';c.font='bold 31px system-ui';c.fillText('§E  TOOLS',18,51);
  },.014);back.mesh.userData.se340Block=true;back.paint();targets.push(back.mesh);
  let expanded=false,progress=0,section='tools',nativePage='tools',lastState=null,lastHover=null,closeHit=null,disposed=false;
  const entries=[
   ['inspect','Select','selector'],['grab','Grab','mesh'],['move','Move','mesh'],['rotate','Rotate','mesh'],
   ['scale','Scale','mesh'],['create-menu','Create','create'],['draw','Draw','draw'],['sculpt','Sculpt','sculpt'],
   ['manual-mesh','Mesh edit','manual-mesh'],['objects','Objects','objects'],['views','Display','views'],['projects','Projects','projects']
  ];
  const repaintRow=(item)=>{
   const {ctx:c,canvas,mesh,action,label}=item,w=canvas.width,h=canvas.height;
   c.clearRect(0,0,w,h);
   const selected=item===lastHover||item.active;
   c.fillStyle=selected?'#2f564f':'#272b40';c.fillRect(0,0,w,h);
   c.strokeStyle=selected?'#b3ffdd':'#545d76';c.lineWidth=selected?4:2;c.strokeRect(2,2,w-4,h-4);
   c.fillStyle='#d9eafb';c.textBaseline='middle';
   try{ui.drawGuideIcon(c,action,37,h/2,44,selected?'#e7ffd5':'#b7dbef');}catch(_){}
   c.font='650 32px system-ui';c.fillText(label,78,h/2,w-87);
   item.texture.needsUpdate=true;mesh.userData.se340Selected=!!item.active;
  };
  for(let i=0;i<entries.length;i++){
   const [action,label,page]=entries[i],y=.305-i*.054;
   const item=make('Dock '+label,.172,.050,-.325,y,()=>{},.043);
   Object.assign(item,{action,label,page,active:i===0});
   item.mesh.userData.se340Action=action;
   item.mesh.userData.se443DockAction=action;
   targets.push(item.mesh);rows.push(item);repaintRow(item);
  }
  const quick=[['undo','Undo'],['redo','Redo'],['save-local','Save']];
  for(let i=0;i<quick.length;i++){
   const [action,label]=quick[i],item=make('Dock '+label,.052,.051,-.384+i*.059,-.356,()=>{},.043);
   Object.assign(item,{action,label,page:null,active:false});
   item.mesh.userData.se340Action=action;item.mesh.userData.se443DockAction=action;
   targets.push(item.mesh);rows.push(item);repaintRow(item);
  }
  // The close control travels with the right panel rather than the left dock.
  const close=make('Settings close',.064,.042,.268,.266,(c,w,h)=>{
   c.fillStyle='#30364a';c.fillRect(0,0,w,h);c.strokeStyle='#9ac4b5';c.lineWidth=3;c.strokeRect(2,2,w-4,h-4);
   c.fillStyle='#e6f8ef';c.font='bold 32px system-ui';c.textAlign='center';c.textBaseline='middle';c.fillText('×',w/2,h/2);
  },.055);
  close.mesh.removeFromParent();drawer.add(close.mesh);close.mesh.userData.se340Action='dock-close';close.mesh.userData.se443Close=true;close.paint();closeHit=close.mesh;
  const oldUpdate=ui.update,oldHit=ui.hitTest,oldPress=ui.press,oldHover=ui.hover,oldTick=ui.tick,oldDispose=ui.dispose,oldInspect=ui.inspect;
  const oldOpenWheel=ui.openWheel;
  const originX=-.185,span=.32;
  function syncDrawer(){
   const eased=progress*progress*(3-2*progress);
   drawer.scale.x=Math.max(.001,eased);
   drawer.position.x=originX+span*eased;
   drawer.visible=progress>.001;
   // The original seven horizontal tabs are replaced by permanent tool rows.
   for(const target of ui.targets)if(target.userData?.se360Role==='nav')target.visible=false;
   close.mesh.visible=expanded&&progress>.94;
   // Keep the public target list accurate for controller inspection/tutorials.
   for(const surface of [...targets,close.mesh])if(!ui.targets.includes(surface))ui.targets.push(surface);
   root.updateWorldMatrix(true,true);
  }
  function choose(item){
   if(item.page){
    expanded=true;section=item.page;
    for(const row of rows){const active=!!row.page&&row.action===item.action;if(row.active!==active){row.active=active;repaintRow(row);}}
    if(lastState)oldUpdate({...lastState,page:section});
   }
  }
  function update(next){
   lastState=next||{};
   if(next?.page&&next.page!==nativePage){
    nativePage=next.page;
    if(expanded&&['manual-operation','manual-mesh','accessory','accessory-body','accessory-details','accessory-fit','cameras','aim','help'].includes(next.page))section=next.page;
   }
   oldUpdate({...next,page:expanded?section:(next?.page||'tools')});
   syncDrawer();
  }
  function hitTest(ray){
   if(disposed||!root.visible||!ray?.intersectObjects)return null;
   root.updateWorldMatrix(true,true);
   const rail=ray.intersectObjects(targets.filter(t=>t.visible!==false),false)[0]||null;
   const panel=expanded&&progress>.94?oldHit(ray):null;
   const closeContact=close.mesh.visible?ray.intersectObject(close.mesh,false)[0]:null;
   const candidates=[rail,panel,closeContact].filter(Boolean).sort((a,b)=>a.distance-b.distance);
   return candidates[0]||null;
  }
  function press(target){
   if(target===closeHit){expanded=false;return false;}
   const item=rows.find(row=>row.mesh===target);
   if(item){choose(item);return true;}
   return expanded?oldPress(target):false;
  }
  function hover(target){
   const item=rows.find(row=>row.mesh===target)||null;
   if(lastHover!==item){const before=lastHover;lastHover=item;if(before)repaintRow(before);if(item)repaintRow(item);}
   return oldHover(item?null:target===closeHit?null:target);
  }
  function tick(...args){
   const dt=Math.min(.06,Math.max(0,Number(args[0])||0));
   const goal=expanded?1:0;
   progress=progress<goal?Math.min(goal,progress+dt*7):Math.max(goal,progress-dt*7);
   oldTick(...args);syncDrawer();
  }
  function openWheel(...args){expanded=true;section='tools';const result=oldOpenWheel(...args);if(lastState)oldUpdate({...lastState,page:section});return result;}
  function dispose(){
   disposed=true;
   for(const res of owned)try{res.dispose?.();}catch(_){}
   dock.removeFromParent();close.mesh.removeFromParent();
   return oldDispose();
  }
  syncDrawer();
  return Object.freeze({...ui,update,hitTest,press,hover,tick,openWheel,dispose,inspect:()=>({...oldInspect(),dock:'vertical',drawerExpanded:expanded,drawerProgress:progress,drawerPage:section,toolCount:entries.length})});
 };
 const oldHit=se340Hit;
 se340Hit=function(record,precise=true){
  const hit=oldHit(record,precise);
  if(hit?.ui||hit?.quest||hit?.gizmo)return hit;
  // Pick visible native transform handles before *any* model surface; this
  // applies to Grab as well as Move/Rotate/Scale and never overrides menus.
  const handle=se374GizmoContact(record);
  return handle||hit;
 };
 const oldPoll=se340Poll;
 se340Poll=function(record,frame,dt){
  const result=oldPoll(record,frame,dt);
  if(record.hit?.gizmo&&!record.hit?.ui)record.ray.material.color.setHex(0xffd995);
  return result;
 };
 window.SWYRL_ENGINE_MODEL_VR_DOCK_443=Object.freeze({version:'v11.443',layout:'vertical right drawer',gizmoPriority:'UI > handle > mesh'});
})();
/* SE443_MODEL_VR_VERTICAL_DOCK_END */
