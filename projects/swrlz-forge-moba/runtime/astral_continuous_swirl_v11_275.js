// §E v11.275 — owner requested continuous, independently cycling swirl motes.
// Deliberately installed INSIDE the existing v11.251 nebula closure.
// No new native emitters, main ticks, WebGL contexts or per-frame allocations.
const se275FlowV=[
 'precision mediump float;',
 'attribute float aBirth;',
 'attribute float aLife;',
 'attribute float aStart;',
 'attribute float aTravel;',
 'attribute float aArm;',
 'attribute float aOffset;',
 'attribute float aDepth;',
 'attribute float aSize;',
 'attribute float aTint;',
 'uniform float uTime;',
 'uniform float uSpin;',
 'uniform float uPull;',
 'uniform float uTilt;',
 'uniform float uCyan;',
 'uniform float uPixels;',
 'uniform vec3 uOrigin;',
 'varying float vFade;',
 'varying float vBlue;',
 'varying float vSeed;',
 'const float PI=3.14159265;',
 'const float TAU=6.2831853;',
 'void main(){',
 ' float life=max(1.0,aLife);',
 // Age wraps for memory economy; intensity is already zero at BOTH edges.
 ' float age=fract((uTime+aBirth)/life);',
 ' float ease=age*age*(3.0-2.0*age);',
 ' float u=clamp(aStart+aTravel*ease,.02,.98);',
 ' float pull=max(.35,uPull);',
 ' float radius=.15+2.68*pow(u,pull)+aOffset;',
 ' float spin=uTime*uSpin*.22;',
 ' float phase=uCyan*1.04719755;',
 ' float angle=spin+phase+aArm*TAU/3.0+u*4.85+.18*sin(TAU*u);',
 // Organic motion without reversing or reusing the looping curve timeline.
 ' angle+=u*(.072*sin(u*8.7+aArm*2.3)+.025*sin(u*23.0+aArm*4.1));',
 ' angle+=.15*sin(u*6.1+aBirth*1.7)*age;',
 ' float cx=cos(angle)*radius;',
 ' float cz=sin(angle)*radius;',
 ' float wav=sin(u*18.0+angle*.45+aArm*2.1)*.12*uTilt*u;',
 ' vec3 world=uOrigin+vec3(cx,1.28+cz*.84+wav,cz*.32+aDepth);',
 ' vec4 mv=modelViewMatrix*vec4(world,1.0);',
 ' gl_Position=projectionMatrix*mv;',
 ' float perspective=9.0/max(1.0,-mv.z);',
 ' gl_PointSize=clamp(aSize*uPixels*perspective,1.0,14.0);',
 // Each individual mote dies fully before its next birth; no backward snap.
 ' float enter=smoothstep(0.0,.17,age);',
 ' float exit=1.0-smoothstep(.74,1.0,age);',
 ' vFade=enter*exit;',
 ' vBlue=clamp((u-.15)/.72,0.0,1.0)*aTint;',
 ' vSeed=aBirth;',
 '}'
].join('\n');
const se275FlowF=[
 'precision mediump float;',
 'uniform float uGlow;',
 'varying float vFade;',
 'varying float vBlue;',
 'varying float vSeed;',
 'void main(){',
 ' vec2 q=(gl_PointCoord-.5)*2.0;',
 ' float r=length(q);',
 ' float core=exp(-r*r*12.0);',
 ' float bloom=exp(-r*r*3.7)*(1.0-smoothstep(.74,1.0,r));',
 ' vec3 violet=vec3(1.0,.14,.91);',
 ' vec3 cyan=vec3(.10,.77,1.0);',
 ' vec3 hue=mix(violet,cyan,vBlue);',
 ' float shimmer=.89+.11*sin(vSeed*13.1);',
 ' float alpha=(.62*core+.21*bloom)*vFade*uGlow*shimmer;',
 ' gl_FragColor=vec4(hue,clamp(alpha,0.0,.8));',
 '}'
].join('\n');
const SE275_N=84;
function makeContinuousSwirl(cfg){
 const n=SE275_N,geom=new THREE.BufferGeometry();
 const seed=(k)=>{const arr=new Float32Array(n);for(let i=0;i<n;i++)arr[i]=k(i);return arr;};
 geom.setAttribute('position',new THREE.BufferAttribute(new Float32Array(n*3),3));
 geom.setAttribute('aBirth',new THREE.BufferAttribute(seed(()=>Math.random()*25),1));
 geom.setAttribute('aLife',new THREE.BufferAttribute(seed(()=>2.9+Math.random()*6.1),1));
 geom.setAttribute('aStart',new THREE.BufferAttribute(seed(()=>.035+Math.random()*.19),1));
 geom.setAttribute('aTravel',new THREE.BufferAttribute(seed(()=>.42+Math.random()*.65),1));
 geom.setAttribute('aArm',new THREE.BufferAttribute(seed(()=>Math.floor(Math.random()*3)),1));
 geom.setAttribute('aOffset',new THREE.BufferAttribute(seed(()=>(Math.random()-.5)*.28),1));
 geom.setAttribute('aDepth',new THREE.BufferAttribute(seed(()=>(Math.random()-.5)*.13),1));
 geom.setAttribute('aSize',new THREE.BufferAttribute(seed(()=>1.5+Math.random()*3.0),1));
 geom.setAttribute('aTint',new THREE.BufferAttribute(seed(()=>Math.random()*.94),1));
 const material=new THREE.ShaderMaterial({
  vertexShader:se275FlowV,fragmentShader:se275FlowF,
  transparent:true,depthWrite:false,depthTest:true,
  blending:THREE.AdditiveBlending,
  uniforms:{
   uTime:{value:0},uSpin:{value:1},uPull:{value:1},
   uTilt:{value:.7},uCyan:{value:cfg.preset==='vortexCyan'?1:0},
   uGlow:{value:.72},uPixels:{value:Math.min(window.devicePixelRatio||1,2)},
   uOrigin:{value:new THREE.Vector3()}
  }
 });
 const mesh=new THREE.Points(geom,material);
 mesh.name='Astral Vortex · independent continuous drift motes';
 mesh.frustumCulled=false;mesh.renderOrder=10;
 return {mesh,geom,material,clock:0,particleCount:n};
}
function updateContinuousSwirl(flow,cfg,rec,origin,dt){
 // No rec.se249Time dependency: that clock can rewind at timeline repeat.
 // We only advance this separate lifetime clock while the engine steps.
 const step=Number(dt);
 if(Number.isFinite(step)&&step>0)flow.clock+=Math.min(step,.08);
 const u=flow.material.uniforms;
 u.uTime.value=flow.clock;
 u.uSpin.value=clamp(cfg.vortexSpin??1,-3,3);
 u.uPull.value=clamp(cfg.vortexPull??1,.35,3);
 u.uTilt.value=clamp(cfg.vortexTilt??.7,0,2.5);
 u.uGlow.value=.72*clamp(cfg.vortexGlow??1,.15,2);
 u.uOrigin.value.copy(origin);
}
