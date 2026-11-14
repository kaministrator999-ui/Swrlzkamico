/* SE443_MODEL_VR_VERTICAL_DOCK_START */
/* SE445_VR_PROGRESSIVE_TOOLS_START */
// Three-stage world-space menu: far-right primary tools, middle operation list,
// left native settings. No new modeling authority, checkpoint or input system.
(function(){
 'use strict';
 const previousCreate=se340CreateModelVRUI;
 se340CreateModelVRUI=function(options){
  const ui=previousCreate(options),T=options.THREE,root=ui.root;
  const nativeChildren=[...root.children];
  const details=new T.Group();details.name='Model VR · native modifier panel';root.add(details);
  for(const child of nativeChildren)details.add(child);
  const submenu=new T.Group();submenu.name='Model VR · operation submenu';root.add(submenu);
  const rail=new T.Group();rail.name='Model VR · far-right primary tools';root.add(rail);
  const RAIl_X=.51,SUB_X=.29,DETAIL_X=-.16;
  const owned=[],primaryTargets=[],submenuTargets=[],primaryRows=[],submenuRows=[],quickRows=[];
  const paintMesh=(parent,name,w,h,x,y,paint,z=.049)=>{
   const canvas=document.createElement('canvas');
   canvas.width=Math.max(1,Math.round(w*2300));canvas.height=Math.max(1,Math.round(h*2300));
   const ctx=canvas.getContext('2d');if(!ctx)throw Error('VR tool layers require a canvas context');
   const texture=new T.CanvasTexture(canvas);
   texture.colorSpace=T.SRGBColorSpace;texture.minFilter=T.LinearFilter;texture.magFilter=T.LinearFilter;
   const material=new T.MeshBasicMaterial({map:texture,transparent:true,depthTest:false,depthWrite:false,toneMapped:false,side:T.DoubleSide});
   const geometry=new T.PlaneGeometry(w,h),mesh=new T.Mesh(geometry,material);
   owned.push(texture,material,geometry);mesh.name=name;mesh.position.set(x,y,z);
   mesh.renderOrder=8400;mesh.frustumCulled=false;
   mesh.userData.editorOnly=true;mesh.userData.se340UI=true;
   parent.add(mesh);
   const item={mesh,canvas,ctx,texture,paint:()=>{
    ctx.clearRect(0,0,canvas.width,canvas.height);
    paint(ctx,canvas.width,canvas.height);texture.needsUpdate=true;
   }};
   return item;
  };
  function surface(parent,name,w,h,paint){
   const item=paintMesh(parent,name,w,h,0,0,paint,.014);
   item.mesh.userData.se340Block=true;item.paint();return item;
  }
  const primaryBack=surface(rail,'Primary tools background',.192,.84,(c,w,h)=>{
   c.fillStyle='#171c2c';c.fillRect(0,0,w,h);
   c.strokeStyle='#728a96';c.lineWidth=5;c.strokeRect(3,3,w-6,h-6);
   c.fillStyle='#b5f4e0';c.font='700 28px system-ui';c.fillText('§E TOOLS',17,51);
  });
  primaryTargets.push(primaryBack.mesh);
  const submenuBack=surface(submenu,'Operation submenu background',.223,.84,(c,w,h)=>{
   c.fillStyle='#172532';c.fillRect(0,0,w,h);
   c.strokeStyle='#739f9d';c.lineWidth=5;c.strokeRect(3,3,w-6,h-6);
  });
  submenuTargets.push(submenuBack.mesh);
  let category=null,submenuOpen=false,detailsOpen=false,subProgress=0,detailProgress=0;
  let detailPage='tools',lastState=null,lastHover=null,disposed=false;
  const presets={
   inspect:[['inspect','Select'],['selector-sweep','Sweep select'],['selector-lasso-front','Front lasso'],['selector-lasso-through','Through lasso'],['selection-clear','Clear selection'],['focus','Focus selection']],
   grab:[['grab','Grab selected'],['precision','Fine motion'],['snap','Snap'],['focus','Focus'],['duplicate','Duplicate']],
   move:[['move','Move selected'],['precision','Precision'],['snap','Snap'],['focus','Focus'],['undo','Undo']],
   rotate:[['rotate','Rotate selected'],['precision','Precision'],['snap','Snap'],['focus','Focus'],['undo','Undo']],
   scale:[['scale','Scale selected'],['precision','Precision'],['snap','Snap'],['focus','Focus'],['undo','Undo']],
   'create-menu':[['create-box','Cube'],['create-sphere','Sphere'],['create-cylinder','Cylinder'],['create-cone','Cone'],['create-pouch','Hip pouch'],['draw','Draw outline'],['duplicate','Duplicate']],
   draw:[['draw','Draw outline'],['draw-finish','Make face'],['extrude','Thicken outline'],['draw-clear','Discard outline'],['undo','Undo']],
   sculpt:[['sculpt-push','Push'],['sculpt-smooth','Smooth'],['sculpt-flatten','Flatten'],['sculpt-inflate','Inflate'],['sculpt-pinch','Pinch'],['sculpt-translate','Translate'],['manual-inset','Inset face'],['manual-extrude','Extrude face'],['manual-solidify','Solidify'],['manual-subdivide','Subdivide'],['manual-mesh','Other face tools']],
   'manual-mesh':[['manual-convert','Make editable'],['manual-pick','Pick flat region'],['manual-inset','Inset'],['manual-extrude','Extrude'],['manual-solidify','Solidify'],['manual-deleteFaces','Delete faces'],['manual-subdivide','Subdivide'],['manual-repairNormals','Repair normals'],['manual-learn','Learn this tool']],
   objects:[['objects','Object index'],['index-add','Multi select'],['selection-clear','Clear selection'],['focus','Focus selection'],['duplicate','Duplicate']],
   views:[['view-front','Front'],['view-back','Back'],['view-left','Left'],['view-right','Right'],['view-top','Top'],['view-bottom','Bottom'],['view-iso','Isometric'],['display-textured','Textured'],['display-wireframe','Wireframe'],['display-xray','X-ray'],['display-normals','Normals']],
   projects:[['save-local','Save project'],['save-account','Save to account'],['clone-project','Clone project'],['projects','Project tools'],['menu-reset','Reset menu']]
  };
  const entries=[
   ['inspect','Select','selector'],['grab','Grab','mesh'],['move','Move','mesh'],
   ['rotate','Rotate','mesh'],['scale','Scale','mesh'],['create-menu','Create','create'],
   ['draw','Draw','draw'],['sculpt','Sculpt','sculpt'],['manual-mesh','Face tools','manual-mesh'],
   ['objects','Objects','objects'],['views','Display','views'],['projects','Projects','projects'],
   ['delete-selected','Delete',null]
  ];
  function row(parent,action,label,y,width,role){
   const item=paintMesh(parent,role+' '+label,width,.046,0,y,()=>{},.051);
   Object.assign(item,{action,label,role,active:false});
   item.mesh.userData.se340Action=action;item.mesh.userData.se445MenuRole=role;
   item.paint=()=>paintRow(item);item.paint();return item;
  }
  function paintRow(item){
   const {ctx:c,canvas,action,label,mesh}=item,w=canvas.width,h=canvas.height;
   c.clearRect(0,0,w,h);
   const hovered=item===lastHover,selected=!!item.active;
   c.fillStyle=hovered?'#38665a':selected?'#295449':'#263345';c.fillRect(0,0,w,h);
   c.strokeStyle=hovered?'#c7fff2':selected?'#8fe5c5':'#586e7f';
   c.lineWidth=hovered?4:2;c.strokeRect(2,2,w-4,h-4);
   c.fillStyle='#deeffb';c.textBaseline='middle';
   try{ui.drawGuideIcon(c,action,34,h/2,39,selected?'#a8f5dd':'#b8dcec');}catch(_){}
   c.font='650 30px system-ui';c.fillText(label,74,h/2,w-80);
   item.texture.needsUpdate=true;mesh.userData.se340Selected=selected;
  }
  for(let i=0;i<entries.length;i++){
   const [action,label,page]=entries[i];
   const item=row(rail,action,label,.302-i*.047,.174,'primary');
   item.page=page;primaryTargets.push(item.mesh);primaryRows.push(item);
  }
  const quick=[['undo','Undo'],['redo','Redo'],['save-local','Save']];
  for(let i=0;i<quick.length;i++){
   const [action,label]=quick[i];
   const item=paintMesh(rail,'Quick '+label,.055,.052,(i-1)*.058,-.356,()=>{},.053);
   Object.assign(item,{action,label,role:'quick',active:false});
   item.mesh.userData.se340Action=action;
   item.paint=()=>paintRow(item);item.paint();
   primaryTargets.push(item.mesh);quickRows.push(item);
  }
  const subHead=paintMesh(submenu,'Operation category title',.205,.060,0,.352,(c,w,h)=>{
   c.fillStyle='#2d4b57';c.fillRect(0,0,w,h);
   c.fillStyle='#e5fff8';c.font='700 31px system-ui';c.textBaseline='middle';
   c.fillText((primaryRows.find(item=>item.action===category)?.label||'OPERATIONS').toUpperCase(),15,h/2,w-70);
  },.047);
  submenuTargets.push(subHead.mesh);
  const subHint=paintMesh(submenu,'Choose operation hint',.209,.067,0,-.345,(c,w,h)=>{
   c.fillStyle='#c8dfe7';c.font='25px system-ui';c.textBaseline='middle';
   c.fillText('Choose an operation',12,h*.32);c.fillText('to open its settings',12,h*.70);
  },.047);
  submenuTargets.push(subHint.mesh);
  const closeSub=paintMesh(submenu,'Close operation list',.038,.044,.089,.354,(c,w,h)=>{
   c.fillStyle='#324654';c.fillRect(0,0,w,h);c.fillStyle='#eefff7';
   c.font='700 52px system-ui';c.textAlign='center';c.textBaseline='middle';c.fillText('×',w/2,h/2);
  },.057);
  closeSub.mesh.userData.se340Action='se445-close-submenu';submenuTargets.push(closeSub.mesh);closeSub.paint();
  for(let i=0;i<11;i++){
   const item=row(submenu,'','',.280-i*.049,.206,'submenu');
   item.mesh.visible=false;submenuTargets.push(item.mesh);submenuRows.push(item);
  }
  const closeDetail=paintMesh(details,'Close modifier settings',.061,.042,.268,.265,(c,w,h)=>{
   c.fillStyle='#303c4b';c.fillRect(0,0,w,h);
   c.strokeStyle='#a3d1c7';c.lineWidth=3;c.strokeRect(2,2,w-4,h-4);
   c.fillStyle='#f5fff7';c.font='700 35px system-ui';
   c.textAlign='center';c.textBaseline='middle';c.fillText('×',w/2,h/2);
  },.057);
  closeDetail.mesh.userData.se340Action='se445-close-settings';closeDetail.paint();
  const oldUpdate=ui.update,oldHit=ui.hitTest,oldPress=ui.press,oldHover=ui.hover;
  const oldTick=ui.tick,oldDispose=ui.dispose,oldInspect=ui.inspect,oldOpenWheel=ui.openWheel;
  function setCategory(action){
   if(category===action&&submenuOpen){submenuOpen=false;detailsOpen=false;category=null;}
   else{category=action;submenuOpen=true;detailsOpen=false;}
   const options=presets[category]||[];
   for(let i=0;i<submenuRows.length;i++){
    const item=submenuRows[i],entry=options[i];
    item.action=entry?.[0]||'';item.label=entry?.[1]||'';item.active=false;
    item.mesh.userData.se340Action=item.action||null;item.mesh.visible=!!item.action;item.paint();
   }
   subHead.paint();
   for(const item of primaryRows){
    const active=!!category&&item.action===category;
    if(active!==item.active){item.active=active;item.paint();}
   }
  }
  function choosePage(action){
   if(action.startsWith('manual-'))return action==='manual-mesh'||['manual-convert','manual-pick','manual-learn'].includes(action)?'manual-mesh':'manual-operation';
   if(action.startsWith('sculpt-')||action.startsWith('brush-'))return 'sculpt';
   if(action.startsWith('create-')||action==='duplicate')return 'create';
   if(action.startsWith('view-')||action.startsWith('display-'))return 'views';
   if(action.startsWith('index-')||action==='objects')return 'objects';
   if(action.startsWith('save-')||action==='projects'||action==='clone-project')return 'projects';
   if(action.startsWith('draw-')||action==='draw'||action==='extrude')return 'draw';
   if(action.startsWith('accessory-'))return 'accessory';
   if(action.startsWith('selector-')||action==='inspect')return 'selector';
   return 'mesh';
  }
  function chooseOperation(item){
   detailPage=choosePage(item.action);detailsOpen=true;
   for(const row of submenuRows){
    const active=row===item;
    if(row.active!==active){row.active=active;row.paint();}
   }
   if(lastState)oldUpdate({...lastState,page:detailPage});
  }
  function sync(){
   const ease=t=>t*t*(3-2*t),left=ease(subProgress),full=ease(detailProgress);
   rail.position.x=RAIl_X;
   submenu.position.x=RAIl_X+(SUB_X-RAIl_X)*left;
   submenu.scale.x=Math.max(.001,left);submenu.visible=subProgress>.001;
   details.position.x=SUB_X+(DETAIL_X-SUB_X)*full;
   details.scale.x=Math.max(.001,full);details.visible=detailProgress>.001;
   closeSub.mesh.visible=submenuOpen&&subProgress>.94;
   closeDetail.mesh.visible=detailsOpen&&detailProgress>.94;
   // Preserve native menu controls, but suppress its obsolete horizontal tabs.
   for(const target of ui.targets)if(target.userData?.se360Role==='nav')target.visible=false;
   for(const target of [...primaryTargets,...submenuTargets,closeDetail.mesh])
    if(!ui.targets.includes(target))ui.targets.push(target);
   root.updateWorldMatrix(true,true);
  }
  function update(next){
   lastState=next||{};
   if(detailsOpen&&next?.page&&next.page!=='tools'&&next.page!==detailPage)
    detailPage=next.page;
   oldUpdate({...next,page:detailsOpen?detailPage:category==='manual-mesh'?'manual-mesh':'tools'});
   sync();
  }
  function hitTest(ray){
   if(disposed||!root.visible||!ray?.intersectObjects)return null;
   root.updateWorldMatrix(true,true);
   const railHit=ray.intersectObjects(primaryTargets.filter(t=>t.visible),false)[0]||null;
   const subHit=subProgress>.94?ray.intersectObjects(submenuTargets.filter(t=>t.visible),false)[0]||null:null;
   const bigHit=detailsOpen&&detailProgress>.94?oldHit(ray):null;
   const hits=[railHit,subHit,bigHit].filter(Boolean).sort((a,b)=>a.distance-b.distance);
   return hits[0]||null;
  }
  function press(target){
   if(target===closeSub.mesh){setCategory(category);return false;}
   if(target===closeDetail.mesh){detailsOpen=false;return false;}
   const quick=quickRows.find(item=>item.mesh===target);
   if(quick)return true;
   const primary=primaryRows.find(item=>item.mesh===target);
   if(primary){
    if(primary.page)setCategory(primary.action);
    else{detailsOpen=false;}
    return true;
   }
   const secondary=submenuRows.find(item=>item.mesh===target&&item.mesh.visible);
   if(secondary){chooseOperation(secondary);return true;}
   return detailsOpen?oldPress(target):false;
  }
  function hover(target){
   const selected=[...primaryRows,...quickRows,...submenuRows].find(item=>item.mesh===target&&item.mesh.visible)||null;
   if(lastHover!==selected){
    if(lastHover){const before=lastHover;lastHover=null;before.paint();}
    lastHover=selected;if(selected)selected.paint();
   }
   return oldHover(selected||target===closeSub.mesh||target===closeDetail.mesh?null:target);
  }
  function tick(...args){
   const dt=Math.max(0,Math.min(.06,Number(args[0])||0));
   oldTick(...args);
   const step=dt*7;
   subProgress=submenuOpen?Math.min(1,subProgress+step):Math.max(0,subProgress-step);
   detailProgress=detailsOpen?Math.min(1,detailProgress+step):Math.max(0,detailProgress-step);
   sync();
  }
  function openWheel(...args){
   detailsOpen=true;detailPage='tools';
   const result=oldOpenWheel(...args);sync();return result;
  }
  function dispose(){
   disposed=true;
   for(const asset of owned)try{asset.dispose?.();}catch(_){}
   rail.removeFromParent();submenu.removeFromParent();closeDetail.mesh.removeFromParent();
   return oldDispose();
  }
  sync();
  return Object.freeze({...ui,update,hitTest,press,hover,tick,openWheel,dispose,
   inspect:()=>({...oldInspect(),dock:'vertical',menuHierarchy:'primary > operation > modifiers',
    primarySide:'right',category,submenuOpen,settingsOpen:detailsOpen,
    drawerExpanded:detailsOpen,drawerProgress:detailProgress,drawerPage:detailPage,
    submenuProgress:subProgress,toolCount:entries.length})});
 };
 // Preserve prior v11.443 transform-handle priority and menu ownership.
 const oldHit=se340Hit;
 se340Hit=function(record,precise=true){
  const hit=oldHit(record,precise);
  if(hit?.ui||hit?.quest||hit?.gizmo)return hit;
  const handle=se374GizmoContact(record);
  return handle||hit;
 };
 const oldPoll=se340Poll;
 se340Poll=function(record,frame,dt){
  const result=oldPoll(record,frame,dt);
  if(record.hit?.gizmo&&!record.hit?.ui)record.ray.material.color.setHex(0xffd995);
  return result;
 };
 window.SWYRL_ENGINE_MODEL_VR_DOCK_443=Object.freeze({
  version:'v11.445',layout:'three-stage far-right dock',gizmoPriority:'UI > handle > mesh'
 });
 window.SWYRL_ENGINE_MODEL_VR_PROGRESSIVE_445=Object.freeze({
  version:'v11.445',defaultPanels:'primary only',categories:'far right',operations:'middle',modifiers:'native left'
 });
})();
/* SE445_VR_PROGRESSIVE_TOOLS_END */
/* SE443_MODEL_VR_VERTICAL_DOCK_END */
