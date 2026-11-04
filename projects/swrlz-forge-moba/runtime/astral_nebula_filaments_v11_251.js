// §E v11.251 · concept-faithful upright galactic arms.
// Thin tapering filaments + widening jagged volumetric smoke + big/small stars.
// Two native vortex-arm records; same Three.js renderer and main engine tick.
(function(){
'use strict';
const TAU=Math.PI*2,SEG=74,STARS=44,clamp=(x,a,b)=>Math.max(a,Math.min(b,x));
const isArm=k=>k==='vortex'||k==='vortexCyan',isVortex=k=>/^vortex(?:Cyan|Core|Spark)?$/.test(k||'');
const oldRuntime=se223Runtime,oldStep=se223Step,oldDispose=se223DisposeRecord;
const white=new THREE.Color('#ffffff');
const temp=new THREE.Color(),glowColor=new THREE.Color();
const vShader=[
'varying vec2 vUV;',
'void main(){vUV=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);}'
].join('\n');
const fShader=[
'precision mediump float;',
'varying vec2 vUV;',
'uniform vec3 uColor;',
'uniform float uTime;',
'uniform float uOpacity;',
'uniform float uKind;',
'float h(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}',
'float noise2(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.0-2.0*f);',
' return mix(mix(h(i),h(i+vec2(1.,0.)),f.x),',
' mix(h(i+vec2(0.,1.)),h(i+vec2(1.,1.)),f.x),f.y);}',
'void main(){',
' float x=vUV.x,y=vUV.y,edge=abs(y-.5)*2.;',
' float tip=smoothstep(.005,.07,x)*(1.0-smoothstep(.79,1.0,x));',
' float pulse=.84+.16*sin(x*35.-uTime*2.4);',
' if(uKind<.5){',
'  float core=1.0-smoothstep(.0,.72,edge);',
'  float halo=1.0-smoothstep(.26,1.0,edge);',
'  float opacity=tip*(.73*core+.21*halo)*pulse*uOpacity;',
'  gl_FragColor=vec4(uColor*vec3(1.27,1.13,1.29),opacity);',
' }else{',
'  vec2 drift=vec2(x*23.+uTime*.18,y*5.7-uTime*.12);',
'  float n=noise2(drift);',
'  float n2=noise2(drift*2.7+vec2(4.1,7.2));',
'  float jag=.47+.39*n+.16*n2;',
'  float fray=1.0-smoothstep(jag-.28,jag+.23,edge);',
'  float cloud=smoothstep(.28,.77,.55*n+.45*n2);',
'  float smoky=(.18+.82*cloud)*fray;',
'  float glow=(1.0-smoothstep(.0,1.0,edge))*.14;',
'  float opacity=(smoky+glow)*tip*uOpacity;',
'  gl_FragColor=vec4(uColor*(.66+.68*n),opacity);',
' }',
'}'
].join('\n');
const starV=[
'attribute float aSize;',
'attribute float aSeed;',
'attribute vec3 aTint;',
'varying float vSeed;',
'varying vec3 vTint;',
'uniform float uPixels;',
'void main(){',
' vSeed=aSeed;vTint=aTint;',
' vec4 mv=modelViewMatrix*vec4(position,1.0);',
' gl_Position=projectionMatrix*mv;',
' gl_PointSize=clamp(aSize*uPixels*(2.9/max(.7,-mv.z)),1.,37.);',
'}'
].join('\n');
const starF=[
'precision mediump float;',
'varying float vSeed;',
'varying vec3 vTint;',
'uniform float uTime;',
'void main(){',
' vec2 p=gl_PointCoord-.5;',
' float r=length(p);',
' float core=1.0-smoothstep(.03,.23,r);',
' float halo=.24*(1.0-smoothstep(.02,.48,r));',
' float ray=.32*exp(-abs(p.x)*32.0)*(1.0-smoothstep(.05,.48,abs(p.y)));',
' ray+=.32*exp(-abs(p.y)*32.0)*(1.0-smoothstep(.05,.48,abs(p.x)));',
' float sparkle=core+halo+ray*(.55+.45*sin(uTime*4.+vSeed*22.));',
' gl_FragColor=vec4(vTint,sparkle);',
'}'
].join('\n');
function makeRibbon(cfg,kind,index){
 const geom=new THREE.BufferGeometry();
 geom.setAttribute('position',new THREE.BufferAttribute(new Float32Array(SEG*6*3),3));
 geom.setAttribute('uv',new THREE.BufferAttribute(new Float32Array(SEG*6*2),2));
 geom.setDrawRange(0,SEG*6);
 const mat=new THREE.ShaderMaterial({
  transparent:true,depthWrite:false,side:THREE.DoubleSide,blending:THREE.AdditiveBlending,
  uniforms:{
   uColor:{value:new THREE.Color(cfg.startColor)},
   uOpacity:{value:kind==='filament'?.95:index===0?.20:.15},
   uTime:{value:0},uKind:{value:kind==='filament'?0:1}
  },vertexShader:vShader,fragmentShader:fShader
 });
 const mesh=new THREE.Mesh(geom,mat);
 mesh.name='Astral Vortex · '+kind+(index?' '+index:'');
 mesh.frustumCulled=false;
 return {mesh,geom,mat,kind,index};
}
function makeStars(cfg){
 const g=new THREE.BufferGeometry(),n=STARS;
 const positions=new Float32Array(n*3),sizes=new Float32Array(n),
  seeds=new Float32Array(n),tints=new Float32Array(n*3);
 const base=new THREE.Color(cfg.startColor),alt=new THREE.Color(cfg.endColor);
 const specs=[];
 for(let i=0;i<n;i++){
  const u=.08+Math.sqrt(Math.random())*.88;
  const phase=(Math.random()-.5)*.40,radial=(Math.random()-.5)*(.18+.48*u);
  const big=i%9===0,bright=i%4===0;
  sizes[i]=big?8+Math.random()*3:bright?4.1+Math.random()*2:1.4+Math.random()*2.4;
  seeds[i]=Math.random();
  temp.copy(base).lerp(alt,.18+Math.random()*.6);
  if(big)temp.lerp(white,.75);else if(bright)temp.lerp(white,.4);
  temp.toArray(tints,i*3);
  specs.push({u,phase,radial,drift:(Math.random()-.5)*.12});
 }
 g.setAttribute('position',new THREE.BufferAttribute(positions,3));
 g.setAttribute('aSize',new THREE.BufferAttribute(sizes,1));
 g.setAttribute('aSeed',new THREE.BufferAttribute(seeds,1));
 g.setAttribute('aTint',new THREE.BufferAttribute(tints,3));
 const mat=new THREE.ShaderMaterial({vertexShader:starV,fragmentShader:starF,
  transparent:true,depthWrite:false,blending:THREE.AdditiveBlending,
  uniforms:{uTime:{value:0},uPixels:{value:Math.min(devicePixelRatio||1,2)}}});
 const mesh=new THREE.Points(g,mat);mesh.name='Astral Vortex · scattered nebula stars';
 mesh.frustumCulled=false;return {mesh,g,mat,specs};
}
function create(cfg,r){
 const bands=[makeRibbon(cfg,'filament',0),makeRibbon(cfg,'smoke',0),makeRibbon(cfg,'smoke',1)];
 const stars=makeStars(cfg);
 for(const b of bands)r.cloud.add(b.mesh);
 r.cloud.add(stars.mesh);
 return {bands,stars};
}
function location(u,phase,cfg,origin,offset=0,layer=0){
 const pull=cfg.vortexPull??1,spin=cfg.preset==='vortexCyan'?Math.PI:0;
 const r=(.12+2.65*Math.pow(u,Math.max(.35,pull)))+offset;
 const a=phase+spin+u*10.2;
 const x=Math.cos(a)*r,z=Math.sin(a)*r;
 const tilt=cfg.vortexTilt??.7;
 const waviness=Math.sin(u*18.+a*.45+layer*2.1)*.12*tilt*u;
 return [origin.x+x,origin.y+.55+z*.70+waviness,
  origin.z+z*.52+Math.sin(u*12.+layer*1.9)*.05*u];
}
function writeMesh(b,cfg,rec,origin){
 const phase=rec.se249Time*(cfg.vortexSpin??1)*1.65;
 const attr=b.geom.getAttribute('position'),uv=b.geom.getAttribute('uv');
 const widthFactor=cfg.nebulaSpread??1;
 const old=new THREE.Vector3(),next=new THREE.Vector3();
 for(let i=0;i<SEG;i++){
  const u0=i/SEG,u1=(i+1)/SEG;
  const p0=location(u0,phase,cfg,origin,0,b.index);
  const p1=location(u1,phase,cfg,origin,0,b.index);
  const normalAt=u=>{
   const a=location(Math.max(0,u-.001),phase,cfg,origin,0,b.index);
   const b=location(Math.min(1,u+.001),phase,cfg,origin,0,b.index);
   const dx=b[0]-a[0],dy=b[1]-a[1],s=Math.max(.0001,Math.hypot(dx,dy));
   return [-dy/s,dx/s];
  };
  const n0=normalAt(u0),n1=normalAt(u1);
  const grow=u=>b.kind==='filament'?
   .024+u*.010:
   (.035+Math.pow(u,.86)*(.57+b.index*.22))*widthFactor;
  const w0=grow(u0),w1=grow(u1);
  const wav0=b.kind==='filament'?0:.06*Math.sin(u0*66+b.index*4+phase*.2)*u0;
  const wav1=b.kind==='filament'?0:.06*Math.sin(u1*66+b.index*4+phase*.2)*u1;
  const v=[
   [p0[0]+n0[0]*w0,p0[1]+n0[1]*w0,p0[2]+wav0],
   [p0[0]-n0[0]*w0,p0[1]-n0[1]*w0,p0[2]-wav0],
   [p1[0]+n1[0]*w1,p1[1]+n1[1]*w1,p1[2]+wav1],
   [p0[0]-n0[0]*w0,p0[1]-n0[1]*w0,p0[2]-wav0],
   [p1[0]-n1[0]*w1,p1[1]-n1[1]*w1,p1[2]-wav1],
   [p1[0]+n1[0]*w1,p1[1]+n1[1]*w1,p1[2]+wav1]
  ];
  for(let j=0;j<6;j++){
   const ix=i*6+j;
   attr.setXYZ(ix,v[j][0],v[j][1],v[j][2]);
   uv.setXY(ix,(j===2||j===4||j===5)?u1:u0,(j===1||j===3||j===4)?1:0);
  }
 }
 attr.needsUpdate=true;uv.needsUpdate=true;
 b.mat.uniforms.uColor.value.set(cfg.startColor);
 b.mat.uniforms.uTime.value=rec.se249Time;
 b.mat.uniforms.uOpacity.value=(b.kind==='filament'?.84:b.index===0?.23:.16)*
  clamp(cfg.vortexGlow??1,.15,2);
}
function updateStars(s,cfg,rec,origin){
 const a=s.g.getAttribute('position'),phase=rec.se249Time*(cfg.vortexSpin??1)*1.65;
 const density=clamp(cfg.starDensity??.75,0,1);
 const count=Math.max(0,Math.min(STARS,Math.round(STARS*density)));
 s.g.setDrawRange(0,count);
 for(let i=0;i<count;i++){
  const spec=s.specs[i],u=spec.u;
  const p=location(u,phase+spec.phase,cfg,origin,spec.radial,1);
  a.setXYZ(i,p[0],p[1]+spec.drift,p[2]+spec.drift);
 }
 a.needsUpdate=true;s.mat.uniforms.uTime.value=rec.se249Time;
}
se223Runtime=function(cfg){
 const r=oldRuntime(cfg);
 if(isArm(cfg.preset)){
  if(!r.se251Nebula)r.se251Nebula=create(cfg,r);
  const mask=r.cloud.layers.mask;
  for(const b of r.se251Nebula.bands)b.mesh.layers.mask=mask;
  r.se251Nebula.stars.mesh.layers.mask=mask;
  for(const old of r.se249Bands||[])old.mesh.visible=false;
 }
 return r;
};
se223Step=function(cfg,dt){
 const out=oldStep(cfg,dt);
 if(!isVortex(cfg.preset))return out;
 const rec=se223State.live.get(cfg.id);
 if(!rec)return out;
 const origin=se223Origin(cfg);
 // Rotate the existing particle cloud toward the camera as well, so the two
 // colored strands, core and sparks share the same upright spiral plane.
 const positions=rec.geometry.getAttribute('position');
 for(let i=0;i<rec.particles.length;i++){
  const p=rec.particles[i],z=p.z-origin.z;
  p.y+=.55+z*.70;
  p.z=origin.z+z*.52;
  positions.setXYZ(i,p.x,p.y,p.z);
 }
 positions.needsUpdate=true;
 if(isArm(cfg.preset)&&rec.se251Nebula){
  for(const band of rec.se251Nebula.bands)writeMesh(band,cfg,rec,origin);
  updateStars(rec.se251Nebula.stars,cfg,rec,origin);
 }
 return out;
};
se223DisposeRecord=function(r){
 if(r?.se251Nebula){
  for(const b of r.se251Nebula.bands){
   b.mesh.removeFromParent();b.geom.dispose();b.mat.dispose();
  }
  const s=r.se251Nebula.stars;
  s.mesh.removeFromParent();s.g.dispose();s.mat.dispose();
  r.se251Nebula=null;
 }
 return oldDispose(r);
};
window.SWYRL_ENGINE_NEBULA_251=Object.freeze({
 inspect:()=>({filaments:se223State.live.size>0?2:0,
  smokeLayersPerArm:2,starsPerArm:STARS,rendererCount:1,
  oriented:'upright',dynamic:true})
});
})();