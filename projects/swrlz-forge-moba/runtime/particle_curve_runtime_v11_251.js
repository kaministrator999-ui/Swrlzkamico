// §E v11.251: native undoable curve storage and actual renderer modulation.
// Backward compatible with previous swyrl-particle-studio-v1 JSON.
const SE251_CURVE_DEFAULTS=Object.freeze({
 emission:[.64,.75,.88,.75,.64],
 size:[.45,.8,1,.8,.42],
 opacity:[0,.92,1,.92,0],
 color:[0,.22,.5,.78,1],
 rotation:[.47,.62,.75,.62,.47]
});
function se251CurveValidate(value){
 if(value!=null&&(typeof value!=='object'||Array.isArray(value)))
  throw Error('Curves must be a parameter object.');
 const out={};
 for(const [key,defaults] of Object.entries(SE251_CURVE_DEFAULTS)){
  const raw=value?.[key]??defaults;
  if(!Array.isArray(raw)||raw.length!==5||!raw.every(v=>
   typeof v==='number'&&Number.isFinite(v)&&v>=0&&v<=1))
   throw Error('Invalid '+key+' curve: expected five values from 0 to 1.');
  out[key]=raw.map(x=>Math.round(x*1000)/1000);
 }
 return out;
}
function se251CurveValue(cfg,key,t){
 const v=cfg?.curves?.[key]||SE251_CURVE_DEFAULTS[key];
 if(!v)return 1;
 const f=Math.max(0,Math.min(.99999999,Number(t)||0))*4;
 const i=Math.floor(f);
 return v[i]+(v[i+1]-v[i])*(f-i);
}
function se251Cycle(rec){return ((rec?.se251Clock||0)%5)/5}
function se251Rotation(cfg,seconds){
 return .35+2.1*se251CurveValue(cfg,'rotation',(Math.max(0,seconds)||0)%5/5);
}
(function(){
 'use strict';
 const originalDefault=se223Default,originalValidate=se223ValidateEmitter;
 const originalSpawn=se223Spawn,originalStep=se223Step;
 const scratch=new THREE.Color();
 se223Default=function(...args){
  const r=originalDefault(...args);r.curves=se251CurveValidate(null);return r;
 };
 se223ValidateEmitter=function(value){
  const r=originalValidate(value);
  r.curves=se251CurveValidate(value?.curves);
  return r;
 };
 // Native emitter rate and native total cap still gate all spawn work.
 se223Spawn=function(cfg,n){
  let amount=n;
  const rec=se223State.live.get(cfg.id);
  if(cfg.mode==='continuous'){
   const intensity=.3+1.75*se251CurveValue(cfg,'emission',se251Cycle(rec));
   amount=Math.min(24,Math.max(0,Math.round(n*intensity)));
  }
  const count=originalSpawn(cfg,amount);
  // Rotation also changes the heading of non-vortex particle presets.
  if(count>0&&!/^vortex(?:Cyan|Core|Spark)?$/.test(cfg.preset)){
   const r=se223State.live.get(cfg.id);const t=se251Cycle(r);
   const a=(se251CurveValue(cfg,'rotation',t)-.5)*1.4;
   const sin=Math.sin(a),cos=Math.cos(a);
   for(let i=r.particles.length-count;i<r.particles.length;i++){
    const p=r.particles[i];const x=p.vx,z=p.vz;
    p.vx=x*cos-z*sin;p.vz=x*sin+z*cos;
   }
  }
  return count;
 };
 se223Step=function(cfg,dt){
  // The vortex wrapper uses vortexSpin to rotate its native geometric ribbon.
  // Changing a curve cannot mutate persistent cfg outside se223Update.
  const r0=se223State.live.get(cfg.id);
  const cycle=se251Cycle(r0);
  const vortex=/^vortex(?:Cyan|Core|Spark)?$/.test(cfg.preset);
  const adjusted=vortex?{...cfg,vortexSpin:cfg.vortexSpin*se251Rotation(cfg,r0?.se251Clock||0)}:cfg;
  const result=originalStep(adjusted,dt);
  const r=se223State.live.get(cfg.id);
  if(!r)return result;
  r.se251Clock=(r.se251Clock||0)+dt;
  // Core THREE.PointsMaterial is per-emitter, so its size envelope is a
  // 5-second preview modulation. Vertex colors/alpha are per-particle lifetime.
  r.material.size=Math.max(.018,cfg.size*(.25+1.4*se251CurveValue(cfg,'size',cycle)));
  const colors=r.geometry.getAttribute('color');
  const pts=r.particles;
  for(let i=0;i<pts.length;i++){
   const p=pts[i],age=Math.max(0,Math.min(1,p.age/p.life));
   const opacity=se251CurveValue(cfg,'opacity',age);
   const mix=se251CurveValue(cfg,'color',age);
   const brightness=(vortex?Math.min(1,Math.min(age*9,(1-age)*4))*Math.min(1.4,cfg.vortexGlow):1-age)*opacity;
   scratch.copy(r.startColor).lerp(r.endColor,mix).multiplyScalar(brightness);
   colors.setXYZ(i,scratch.r,scratch.g,scratch.b);
  }
  colors.needsUpdate=true;
  if(vortex)for(const band of r.se249Bands||[]){
   const uniforms=band.mesh?.material?.uniforms;
   if(uniforms?.uOpacity)uniforms.uOpacity.value*=Math.max(.1,se251CurveValue(cfg,'opacity',cycle));
  }
  return result;
 };
 window.SWYRL_ENGINE_PARTICLE_CURVE_RUNTIME_251=Object.freeze({
  defaults:()=>structuredClone(SE251_CURVE_DEFAULTS),
  value:(id,key,t)=>se251CurveValue(se223Get(id),key,t),
  inspect:()=>({keys:Object.keys(SE251_CURVE_DEFAULTS),pointsPerCurve:5,
   savesTo:'swyrl-particle-studio-v1',rendererCount:1})
 });
})();
