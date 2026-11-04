// §E v11.249 · authentic, layered, animated spiral ribbons for existing native VFX.
// Not a static sprite and NOT another renderer. 2 ribbons per colored emitter.
(function(){
'use strict';
const isVortex=k=>/^vortex(?:Cyan|Core|Spark)?$/.test(k||'');
const prevSpawn=se223Spawn,prevStep=se223Step,prevDispose=se223DisposeRecord;
const TAU=Math.PI*2, SEG=62;
const ctmp=new THREE.Color();
function curve(u,angle,pull,tilt){
 const r=.13+2.65*Math.pow(u,Math.max(.35,pull));
 const t=angle+u*10.2;
 return [Math.cos(t)*r,1.7+Math.sin(u*10+t*.25)*tilt*.36,
         Math.sin(t)*r];
}
function createRibbon(cfg,rec){
 const types=[['main',.14,.86],['halo',.35,.17]];
 const meshes=[];
 for(const [kind,width,opacity] of types){
  const g=new THREE.BufferGeometry();
  g.setAttribute('position',new THREE.BufferAttribute(new Float32Array(SEG*6*3),3));
  g.setAttribute('color',new THREE.BufferAttribute(new Float32Array(SEG*6*3),3));
  g.setDrawRange(0,SEG*6);
  const mat=new THREE.MeshBasicMaterial({
   vertexColors:true,side:THREE.DoubleSide,transparent:true,depthWrite:false,
   blending:THREE.AdditiveBlending,opacity,color:0xffffff
  });
  const mesh=new THREE.Mesh(g,mat);
  mesh.name='Astral Vortex · '+kind+' energy ribbon';
  mesh.layers.set(window.SWYRL_ENGINE_PARTICLE_STAGE_240?.active?.()?25:0);
  mesh.frustumCulled=false;rec.cloud.add(mesh);meshes.push({mesh,width,opacity});
 }
 return meshes;
}
const origRuntime=se223Runtime;
se223Runtime=function(cfg){
 const rec=origRuntime(cfg);
 if(['vortex','vortexCyan'].includes(cfg.preset)){
  if(!rec.se249Bands)rec.se249Bands=createRibbon(cfg,rec);
  for(const b of rec.se249Bands)b.mesh.layers.mask=rec.cloud.layers.mask;
 }
 return rec;
};
se223Spawn=function(cfg,n){
 const added=prevSpawn(cfg,n);
 if(!added||!isVortex(cfg.preset))return added;
 const rec=se223State.live.get(cfg.id);
 const first=rec.particles.length-added;
 const c=cfg.preset==='vortexCore',sp=cfg.preset==='vortexSpark';
 for(let i=first;i<rec.particles.length;i++){
  const p=rec.particles[i],s=p.se248;
  if(!s)continue;
  const u=c ? (.015+Math.random()*.13) : Math.random();
  s.se249U=u;
  s.se249Phase=Math.random()*TAU;
  s.se249Jitter=(Math.random()-.5)*(sp?.45:.055);
  s.se249Arm=cfg.preset==='vortexCyan'?Math.PI:.0;
  s.se249Height=(Math.random()-.5)*.18;
  s.se249Trail=Math.random()*.9;
 }
 return added;
};
function paintRibbon(cfg,rec,band){
 const phase=(rec.se249Time||0)*(cfg.vortexSpin??1)*1.65;
 const spin=cfg.preset==='vortexCyan'?Math.PI:.0;
 const pull=cfg.vortexPull??1,tilt=cfg.vortexTilt??.7;
 const origin=se223Origin(cfg);
 const w=band.width*(.6+(cfg.vortexGlow??1)*.4);
 const pos=band.mesh.geometry.attributes.position;
 const col=band.mesh.geometry.attributes.color;
 const a=new THREE.Color(cfg.startColor),z=new THREE.Color(cfg.endColor);
 band.mesh.material.opacity=Math.min(1.65,band.opacity*(cfg.vortexGlow??1));
 for(let i=0;i<SEG;i++){
  const t0=i/SEG,t1=(i+1)/SEG;
  const p0=curve(t0,phase+spin,pull,tilt),p1=curve(t1,phase+spin,pull,tilt);
  const tangentX=p1[0]-p0[0],tangentZ=p1[2]-p0[2];
  const scale=Math.max(.0001,Math.hypot(tangentX,tangentZ));
  const nx=-tangentZ/scale,nz=tangentX/scale;
  const q0=w*(.25+.75*Math.pow(1-t0,.4));
  const q1=w*(.25+.75*Math.pow(1-t1,.4));
  const verts=[
   [p0[0]+nx*q0,p0[1],p0[2]+nz*q0],
   [p0[0]-nx*q0,p0[1],p0[2]-nz*q0],
   [p1[0]+nx*q1,p1[1],p1[2]+nz*q1],
   [p0[0]-nx*q0,p0[1],p0[2]-nz*q0],
   [p1[0]-nx*q1,p1[1],p1[2]-nz*q1],
   [p1[0]+nx*q1,p1[1],p1[2]+nz*q1]];
  for(let v=0;v<6;v++){
   const idx=i*6+v,src=verts[v],u=v<=1?t0:t1;
   pos.setXYZ(idx,src[0]+origin.x,src[1]+origin.y-1.7,src[2]+origin.z);
   const energy=Math.max(.05,Math.pow(1-u,.6))*(.78+.22*Math.sin(u*18+phase*2));
   ctmp.copy(a).lerp(z,u*.56).multiplyScalar(energy);
   col.setXYZ(idx,ctmp.r,ctmp.g,ctmp.b);
  }
 }
 pos.needsUpdate=true;col.needsUpdate=true;
}
se223Step=function(cfg,dt){
 if(!isVortex(cfg.preset))return prevStep(cfg,dt);
 const rec=se223Runtime(cfg),ps=rec.particles;
 rec.se249Time=(rec.se249Time||0)+dt;
 const spin=cfg.vortexSpin??1,pull=cfg.vortexPull??1,tilt=cfg.vortexTilt??.7;
 const pos=rec.geometry.getAttribute('position'),colors=rec.geometry.getAttribute('color');
 const start=rec.startColor,end=rec.endColor;
 for(let i=ps.length-1;i>=0;i--){
  const p=ps[i];p.age+=dt;
  if(p.age>=p.life){ps[i]=ps[ps.length-1];ps.pop();continue;}
  const s=p.se248;if(!s)continue;
  const f=p.age/p.life;
  if(s.core){
   const a=(s.se249Phase||0)+f*TAU*2.2;
   const r=.025+Math.abs(Math.sin(a*1.4))*.11;
   p.x=s.ox+Math.cos(a)*r;p.z=s.oz+Math.sin(a)*r;
   p.y=s.oy+(Math.random()-.5)*.025;
  } else if(s.sparks){
   const a=(s.se249Phase||0)+(rec.se249Time*spin*2);
   const r=.4+(s.se249U||.5)*2.6+f*.35;
   p.x=s.ox+Math.cos(a)*r;p.z=s.oz+Math.sin(a)*r;
   p.y=s.oy+(s.se249Height||0)+Math.sin(a*2)*.22;
  } else {
   const u=Math.max(.01,Math.min(1,(s.se249U??.7)+(.18-f*.18)));
   const a=rec.se249Time*spin*1.65+(s.se249Arm||0)+f*.85+s.se249Jitter;
   const q=curve(u,a,pull,tilt);
   p.x=s.ox+q[0];p.y=s.oy+(q[1]-1.7)+(s.se249Height||0);p.z=s.oz+q[2];
  }
 }
 const glow=cfg.vortexGlow??1;
 for(let i=0;i<ps.length;i++){
  const p=ps[i],progress=Math.min(1,p.age/p.life);
  const opacity=Math.max(0,Math.min(progress*9,(1-progress)*4,1));
  pos.setXYZ(i,p.x,p.y,p.z);
  ctmp.copy(start).lerp(end,progress*.65).multiplyScalar(
   opacity*glow*(cfg.preset==='vortexCore'?.78:1));
  colors.setXYZ(i,ctmp.r,ctmp.g,ctmp.b);
 }
 rec.material.size=cfg.preset==='vortexCore'?Math.min(.20,cfg.size):
  cfg.size*(cfg.preset==='vortexSpark'?.7:.95);
 rec.geometry.setDrawRange(0,ps.length);
 pos.needsUpdate=true;colors.needsUpdate=true;
 for(const band of rec.se249Bands||[])paintRibbon(cfg,rec,band);
};
se223DisposeRecord=function(rec){
 if(rec?.se249Bands){for(const b of rec.se249Bands){
  b.mesh.removeFromParent();b.mesh.geometry.dispose();b.mesh.material.dispose();
 }rec.se249Bands=null;}
 return prevDispose(rec);
};
window.SWYRL_ENGINE_RIBBONS_249=Object.freeze({inspect:()=>{
 const records=[...se223State.live.values()];
 return {ribbons:records.reduce((n,r)=>n+(r.se249Bands?.length||0),0),
   nativeRenderer:1,particles:records.reduce((n,r)=>n+r.particles.length,0)};
}});
})();