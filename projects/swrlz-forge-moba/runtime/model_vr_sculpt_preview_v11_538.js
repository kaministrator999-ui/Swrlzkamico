/* SE538_IMMERSIVE_SCULPT_REPAIR_START
 * Native WebXR Model Studio: bounded stroke cadence, projected brush profile,
 * source-mesh influence grid, compact existing parameters, async project handoff.
 * Do not add a scene, edit saved model data on hover, or change 2D editor input.
 */
(function () {
 'use strict';
 const T=THREE;
 const stats={strokes:0,skipped:0,lastStrokeMs:0,maxStrokeMs:0,lastCommitMs:0,maxCommitMs:0,gridUpdates:0,gridEdges:0,loadHoldFrames:0};
 // Preserve displacement integrated over time while eliminating redundant
 // full-mesh normals/bounds computations between headset refreshes.
 const nativeStroke=se350UpdateStroke;
 se350UpdateStroke=function(g){
  if(!g||g.kind!=='sculpt')return nativeStroke.apply(this,arguments);
  const now=performance.now(),last=g.se538StrokeAt||0;
  if(last&&now-last<33&&!g.se538FinalSample){stats.skipped++;return;}
  const oldDt=se340XR.frameDt;
  const dt=last?Math.min(.05,Math.max(1/120,(now-last)/1000)):Math.max(1/120,oldDt||1/72);
  g.se538StrokeAt=now;g.se538FinalSample=false;
  se340XR.frameDt=dt;
  try{
   const start=performance.now(),answer=nativeStroke.apply(this,arguments);
   const ms=performance.now()-start;stats.strokes++;stats.lastStrokeMs=ms;
   stats.maxStrokeMs=Math.max(stats.maxStrokeMs,ms);
   return answer;
  }finally{se340XR.frameDt=oldDt;}
 };
 const nativeFinish=se350FinishTrigger;
 se350FinishTrigger=function(record){
  const g=se340XR.gesture;
  if(g?.kind==='sculpt'&&g.record===record)g.se538FinalSample=true;
  const start=performance.now(),answer=nativeFinish.apply(this,arguments);
  if(g?.kind==='sculpt'){stats.lastCommitMs=performance.now()-start;
   stats.maxCommitMs=Math.max(stats.maxCommitMs,stats.lastCommitMs);}
  return answer;
 };
 // The XR project service deliberately releases the old root before awaiting
 // a potentially slow fetch/clone/load. Keep the session alive during this
 // documented transition; otherwise the normal frame guard would exit VR.
 const nativeFrame=se340ModelXRFrameCore;
 se340ModelXRFrameCore=function(time,frame){
  const s=se340XR;
  if(s.se517ProjectBusy&&s.session&&s.scene&&!s.ending){
   s.frameCount++;stats.loadHoldFrames++;
   const viewer=se340Viewer(frame);
   if(viewer)s.lastViewer=viewer;
   if(s.ui){
    s.ui.tick?.(Math.min(.05,s.frameDt||.014));
   }
   renderer.render(s.scene,s.camera);return;
  }
  return nativeFrame.apply(this,arguments);
 };
 // Existing grouped parameter toolbar already owns its real action IDs.
 // Crop its empty canvas tail instead of creating a second settings system.
 const nativeUI=se340CreateModelVRUI;
 se340CreateModelVRUI=function(options){
  const ui=nativeUI(options),root=ui.root;
  const details=root.getObjectByName('Model VR · native modifier panel');
  const bar=details?.getObjectByName('§E · contextual parameter toolbar');
  const background=bar?.children.find(x=>x.isMesh&&x.userData?.se340Block);
  const controls=bar?.children.filter(x=>x.userData?.se528Parameter)||[];
  if(!bar||!background)return ui;
  const nativeUpdate=ui.update,nativeTick=ui.tick;
  let previous=-1;
  function tidy(){
   const count=Math.min(6,ui.parametersInspect?.().groups?.length||0);
   const fraction=count?Math.min(1,(146+count*122)/870):1;
   // Keep the header and controls aligned to their unchanged original pixels.
   if(fraction!==previous){
    background.scale.y=fraction;
    background.position.y=.18*(1-fraction);
    const tex=background.material?.map;
    if(tex){tex.repeat.y=fraction;tex.offset.y=1-fraction;tex.needsUpdate=true;}
    previous=fraction;
   }
   if(count){
    // Within the existing Sculpt inspector rather than a detached panel
    // beneath the model. Native ray targets stay at their original positions.
    bar.position.set(-.02,-.33,.095);
    for(const target of controls)target.renderOrder=8581;
   }
  }
  return Object.freeze({...ui,
   update:function(){const r=nativeUpdate.apply(this,arguments);tidy();return r;},
   tick:function(){const r=nativeTick.apply(this,arguments);tidy();return r;},
   inspect:()=>({...ui.inspect(),se538CompactParameters:previous})});
 };
 const preview={scene:null,dome:null,selector:null,point:null,wires:null,
  coords:null,colors:null,key:null,at:0,mask:null,maskId:null};
 const MAX_EDGES=480;
 const tmp=new T.Vector3(),tmpB=new T.Vector3(),normal=new T.Vector3();
 function hide(){for(const k of ['dome','selector','point','wires'])if(preview[k])preview[k].visible=false;}
 function own(x){return se340Own(x);}
 function build(s){
  if(preview.scene===s.scene&&preview.dome)return;
  preview.scene=s.scene;preview.key=null;preview.at=0;
  const domeMat=own(new T.MeshBasicMaterial({color:0x66f2c4,transparent:true,opacity:.19,
   side:T.DoubleSide,depthTest:false,depthWrite:false,wireframe:false,toneMapped:false}));
  preview.dome=new T.Mesh(own(new T.SphereGeometry(1,24,8,0,Math.PI*2,0,Math.PI/2)),domeMat);
  preview.dome.name='Sculpt strength envelope';preview.dome.renderOrder=9004;
  preview.dome.raycast=()=>{};
  const rimMat=own(new T.MeshBasicMaterial({color:0x9affe2,transparent:true,opacity:.9,
   side:T.DoubleSide,depthTest:false,depthWrite:false}));
  preview.selector=new T.Mesh(own(new T.RingGeometry(.975,1,48)),rimMat);
  preview.selector.name='Sculpt area selector';preview.selector.renderOrder=9005;
  preview.selector.raycast=()=>{};
  preview.point=new T.Mesh(own(new T.SphereGeometry(.007,8,6)),
   own(new T.MeshBasicMaterial({color:0xe8fff3,depthTest:false,depthWrite:false})));
  preview.point.renderOrder=9006;preview.point.raycast=()=>{};
  preview.coords=new Float32Array(MAX_EDGES*6);
  preview.colors=new Float32Array(MAX_EDGES*6);
  const geo=own(new T.BufferGeometry());
  geo.setAttribute('position',new T.BufferAttribute(preview.coords,3).setUsage(T.DynamicDrawUsage));
  geo.setAttribute('color',new T.BufferAttribute(preview.colors,3).setUsage(T.DynamicDrawUsage));
  geo.setDrawRange(0,0);
  preview.wires=new T.LineSegments(geo,own(new T.LineBasicMaterial({
   vertexColors:true,transparent:true,opacity:.85,depthTest:false,depthWrite:false})));
  preview.wires.matrixAutoUpdate=false;preview.wires.frustumCulled=false;
  preview.wires.renderOrder=9003;preview.wires.raycast=()=>{};
  preview.wires.name='Sculpt actual source-mesh influence';
  for(const k of ['wires','dome','selector','point']){
   preview[k].userData.se350SurfacePreview=true;
   preview[k].userData.editorOnly=true;s.scene.add(preview[k]);
  }
 }
 function regionMask(hit){
  const region=se350Surface()?.inspect?.()?.selectedRegion;
  if(!region||region.partId!==hit.id||typeof atelierLassoCompiledRegionMask!=='function')
   return null;
  const part=partById(hit.id),item=part?.sculptLassos?.find(x=>x.id===region.id&&x.enabled);
  if(!item)return null;
  if(preview.maskId===item&&preview.mask)return preview.mask;
  try{preview.mask=atelierLassoCompiledRegionMask(part,item);preview.maskId=item;}
  catch(_){preview.mask=null;preview.maskId=null;}
  return preview.mask;
 }
 function updateInfluence(hit,center,radius,mask){
  const mesh=hit.mesh,geo=mesh?.geometry,position=geo?.getAttribute?.('position');
  if(!position||position.itemSize!==3){preview.wires.visible=false;return;}
  const idx=geo.getIndex(),points=position.array,indices=idx?.array;
  const faces=Math.floor((idx?idx.count:position.count)/3);
  const step=Math.max(1,Math.ceil(faces/2500));
  const r2=radius*radius,flat=preview.coords,colors=preview.colors;
  const valid=(i)=>{
   const j=i*3,dx=points[j]-center.x,dy=points[j+1]-center.y,dz=points[j+2]-center.z;
   const d=dx*dx+dy*dy+dz*dz;
   if(d>r2)return 0;
   if(mask&&!mask.contains([points[j],points[j+1],points[j+2]]))return 0;
   const t=1-Math.sqrt(d)/Math.max(radius,1e-5);
   return t*t*(3-2*t);
  };
  let count=0;
  for(let f=0;f<faces&&count<MAX_EDGES;f+=step){
   const q=f*3,a=indices?indices[q]:q,b=indices?indices[q+1]:q+1,
    c=indices?indices[q+2]:q+2;
   const va=valid(a),vb=valid(b),vc=valid(c);
   for(const [i,j,wi,wj] of [[a,b,va,vb],[b,c,vb,vc],[c,a,vc,va]]){
    if(count>=MAX_EDGES)break;
    if(wi<.01||wj<.01)continue;
    const at=count*6,ix=i*3,jx=j*3;
    flat[at]=points[ix];flat[at+1]=points[ix+1];flat[at+2]=points[ix+2];
    flat[at+3]=points[jx];flat[at+4]=points[jx+1];flat[at+5]=points[jx+2];
    for(let k=0;k<2;k++){const w=k===0?wi:wj,p=at+k*3;
     colors[p]=.06+.5*w;colors[p+1]=.35+.65*w;colors[p+2]=.42+.55*w;}
    count++;
   }
  }
  const wireGeo=preview.wires.geometry;
  wireGeo.setDrawRange(0,count*2);
  wireGeo.attributes.position.needsUpdate=true;wireGeo.attributes.color.needsUpdate=true;
  preview.wires.matrix.copy(mesh.matrixWorld);
  preview.wires.matrixWorldNeedsUpdate=true;
  preview.wires.visible=count>0;stats.gridUpdates++;stats.gridEdges=count;
 }
 function surfaceNormal(hit,local){
  if(hit.face?.normal?.isVector3)normal.copy(hit.face.normal)
   .transformDirection(hit.mesh.matrixWorld);
  else if(hit.normal?.isVector3)normal.copy(hit.normal);
  else{
   const attr=hit.mesh.geometry?.getAttribute?.('normal');
   const pos=hit.mesh.geometry?.getAttribute?.('position');
   let best=-1,min=Infinity;
   if(attr&&pos){const stride=Math.max(1,Math.ceil(pos.count/2000));
    for(let i=0;i<pos.count;i+=stride){
     const d=(pos.getX(i)-local.x)**2+(pos.getY(i)-local.y)**2+
      (pos.getZ(i)-local.z)**2;
     if(d<min){min=d;best=i;}
    }
    if(best>=0)normal.set(attr.getX(best),attr.getY(best),attr.getZ(best))
     .transformDirection(hit.mesh.matrixWorld);
   }
   if(best<0)normal.copy(se340Cast(se350Record('right'))?.ray?.direction||new T.Vector3(0,0,-1)).negate();
  }
  normal.normalize();
  if(!Number.isFinite(normal.x)||normal.lengthSq()<.5)normal.set(0,1,0);
  return normal;
 }
 // Keep the existing physical controller ray. Only replace the legacy flat
 // ring with non-interactive, pooled geometry. No new raycast inputs.
 se350UpdateBrush=function(){
  const s=se340XR;
  if(!s.scene||s.mode!=='sculpt'||!se340VisibleSession()){hide();return;}
  const record=s.inputSample?.held?.stroke?.source?.record||se350Record('right'),
   hit=record?.hit;
  if(!hit?.id||!hit.mesh||!hit.point||hit.ui||hit.gizmo){hide();return;}
  build(s);
  const mesh=hit.mesh;
  mesh.updateWorldMatrix(true,false);
  const local=mesh.worldToLocal(hit.point.clone()),r=Math.max(.03,s.brushRadius||.12);
  const direction=s.sculptDirection==='in'&&s.sculptTool==='push'?-1:1;
  const n=surfaceNormal(hit,local);
  const rWorld=mesh.getWorldScale(tmp).length()/Math.sqrt(3)*r;
  const height=Math.max(.012,Math.abs(s.brushStrength||.3)*.32);
  preview.dome.position.copy(hit.point);
  preview.dome.quaternion.setFromUnitVectors(new T.Vector3(0,1,0),tmpB.copy(n).multiplyScalar(direction));
  preview.dome.scale.set(rWorld,height*mesh.getWorldScale(tmp).length()/Math.sqrt(3),rWorld);
  preview.dome.material.color.setHex(direction<0?0xfca46b:0x5be7c7);
  preview.dome.visible=true;
  preview.selector.position.copy(hit.point).addScaledVector(n,.001);
  preview.selector.quaternion.setFromUnitVectors(new T.Vector3(0,0,1),n);
  preview.selector.scale.setScalar(rWorld);preview.selector.visible=true;
  preview.point.position.copy(hit.point);preview.point.visible=true;
  const now=performance.now(),version=mesh.geometry?.getAttribute('position')?.version||0;
  const key=[hit.id,version,r,s.sculptTool,s.sculptDirection,
   se350Surface()?.inspect?.()?.selectedRegionId||''].join(':');
  const moved=!preview.lastPoint||preview.lastPoint.distanceToSquared(hit.point)>(rWorld*.075)**2;
  if(key!==preview.key||moved&&now-preview.at>46){
   const mask=regionMask(hit);
   updateInfluence(hit,local,r,mask);
   preview.key=key;preview.lastPoint=hit.point.clone();preview.at=now;
  }else if(preview.wires.visible){
   preview.wires.matrix.copy(mesh.matrixWorld);preview.wires.matrixWorldNeedsUpdate=true;
  }
 };
 const nativeCleanup=se340Cleanup;
 se340Cleanup=function(){
  hide();
  if(preview.scene){
   for(const k of ['dome','selector','point','wires'])preview[k]?.removeFromParent?.();
  }
  preview.scene=null;preview.dome=null;preview.selector=null;preview.point=null;
  preview.wires=null;preview.coords=null;preview.colors=null;preview.key=null;
  preview.at=0;preview.mask=null;preview.maskId=null;preview.lastPoint=null;
  return nativeCleanup.apply(this,arguments);
 };
 window.SWYRL_ENGINE_IMMERSIVE_SCULPT_538=Object.freeze({
  inspect:()=>({...stats,previewActive:!!preview.dome?.visible,
   gridVisible:!!preview.wires?.visible,compactParameters:se340XR.ui?.inspect?.().se538CompactParameters??null})
 });
})();
/* SE538_IMMERSIVE_SCULPT_REPAIR_END */