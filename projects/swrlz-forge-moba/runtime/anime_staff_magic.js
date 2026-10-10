// Small embers belong to the authored Effects layer and follow the fitted
// staff head. Every position comes from story time, including paused previews.
function staffMagicCreate(c){
  const group=new THREE.Group();group.name='Kami · staff-head embers';
  const canvas=document.createElement('canvas');canvas.width=64;canvas.height=64;
  const context=canvas.getContext('2d'),glow=context.createRadialGradient(32,32,0,32,32,30);
  glow.addColorStop(0,'rgba(255,242,191,1)');glow.addColorStop(.18,'rgba(255,202,95,.9)');
  glow.addColorStop(.5,'rgba(239,146,40,.3)');glow.addColorStop(1,'rgba(239,146,40,0)');
  context.fillStyle=glow;context.fillRect(0,0,64,64);
  const texture=new THREE.CanvasTexture(canvas);texture.colorSpace=THREE.SRGBColorSpace;
  const geometry=new THREE.BufferGeometry();
  geometry.setAttribute('position',new THREE.Float32BufferAttribute(new Float32Array(18*3),3));
  const material=new THREE.PointsMaterial({map:texture,color:'#ffd184',size:.085,
    transparent:true,opacity:0,depthWrite:false,blending:THREE.AdditiveBlending,fog:false,toneMapped:false});
  const motes=new THREE.Points(geometry,material);motes.frustumCulled=false;group.add(motes);
  const arcGeometry=new THREE.BufferGeometry(),vertices=[];
  for(let i=0;i<=40;i++){const a=i/40*Math.PI*1.5;vertices.push(Math.cos(a)*.31,Math.sin(a)*.19,0);}
  arcGeometry.setAttribute('position',new THREE.Float32BufferAttribute(vertices,3));
  const arc=new THREE.Line(arcGeometry,new THREE.LineBasicMaterial({color:'#eab15a',transparent:true,
    opacity:0,depthWrite:false,blending:THREE.AdditiveBlending,fog:false,toneMapped:false}));
  group.add(arc);scene.add(group);
  c.staffMagic={group,motes,arc,texture,anchor:new THREE.Vector3(),time:0};return c.staffMagic;
}
function staffMagicFrame(c,t){
  const actor=c.cast.kami,rig=actor?.userData.rig,part=rig?.joints.staff?.userData.part;
  const enabled=part&&rigUsesNaturalGrip('kami',rigModel().characters.kami);
  if(!enabled&&!c.staffMagic)return;
  const effect=c.staffMagic||staffMagicCreate(c),key=storySample('effects',t);
  const progress=typeof emergenceProgress==='function'?emergenceProgress('effects',t):1;
  const visible=!!(enabled&&actor.visible&&c.layers.effects.visible&&key.visible&&key.opacity>.01&&progress>.01);
  effect.group.visible=visible;effect.time=t;if(!enabled)return;
  scene.updateMatrixWorld(true);
  // Above the painted skull, clear of the gripping hand and the mage's face.
  part.localToWorld(effect.anchor.set(0,part.userData.rigSize.height*.22,.1));
  effect.group.position.copy(effect.anchor);
  part.getWorldQuaternion(effect.group.quaternion);
  effect.group.scale.copy(part.getWorldScale(new THREE.Vector3()));
  const pulse=.78+.22*Math.sin(t*1.8),opacity=key.opacity*progress;
  effect.motes.material.opacity=.5*opacity*pulse;effect.arc.material.opacity=.22*opacity*pulse;
  effect.arc.rotation.z=t*.28;effect.arc.position.z=.035;
  const points=effect.motes.geometry.getAttribute('position');
  for(let i=0;i<points.count;i++){
    const phase=(t*.24+i*.61803398875)%1,angle=t*.5+i*2.39996323;
    const radius=.1+.19*phase;
    points.setXYZ(i,Math.cos(angle)*radius,.04+phase*.48,Math.sin(angle)*radius*.35+.04);
  }
  points.needsUpdate=true;
}
const staffMagicRender=storyRender;
storyRender=function(){staffMagicRender();if(animeCine)staffMagicFrame(animeCine,animeCine.elapsed);};
const staffMagicEnd=animeEndCinematic;
animeEndCinematic=function(){
  const effect=animeCine?.staffMagic;
  if(effect){effect.group.removeFromParent();effect.motes.geometry.dispose();effect.motes.material.dispose();
    effect.arc.geometry.dispose();effect.arc.material.dispose();effect.texture.dispose();}
  return staffMagicEnd();
};
const staffMagicStatus=window.SWYRL_ENGINE_STORYBOARD.stageStatus;
window.SWYRL_ENGINE_STORYBOARD=Object.freeze({...window.SWYRL_ENGINE_STORYBOARD,stageStatus:function(){
  const status=staffMagicStatus(),effect=animeCine?.staffMagic;
  return {...status,staffMagic:effect?{visible:effect.group.visible,time:effect.time,
    anchor:effect.anchor.toArray(),opacity:effect.motes.material.opacity,
    positions:Array.from(effect.motes.geometry.getAttribute('position').array),
    count:effect.motes.geometry.getAttribute('position').count}:null};
}});
