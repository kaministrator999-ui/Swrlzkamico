"""§E v11.258 — slow reference-shaped nebula + particle-fault containment.

Append-only source patch. v11.257's first-frame TDZ correction is retained.
Only particle effects / their isolated preview are changed; one invalid
emitter must never stop the editor's main WebGL animation tick.
"""
import json

def once(text, old, new, label):
    count=text.count(old)
    if count != 1:
        raise AssertionError(("v11.258",label,count,old[:120]))
    return text.replace(old,new,1)

def apply(html):
    # Six independent short, half-S wisps (3 violet + 3 cyan). The old
    # two enormous spiral rings were over 1.5 turns each.
    html=once(html,
        "const TAU=Math.PI*2,SEG=74,STARS=44,clamp=",
        "const TAU=Math.PI*2,SEG=74,STARS=60,clamp=",
        "more star variety without increasing native emitter count")
    html=once(html,
        "function makeRibbon(cfg,kind,index){",
        "function makeRibbon(cfg,kind,index,arm){",
        "short wisp branches")
    html=once(html,
        "mesh.name='Astral Vortex · '+kind+(index?' '+index:'');",
        "mesh.name='Astral Vortex · '+kind+' · arm '+arm+(index?' '+index:'');",
        "inspectable strand names")
    html=once(html,
        "return {mesh,geom,mat,kind,index};",
        "return {mesh,geom,mat,kind,index,arm};",
        "retain wisp branch index")
    html=once(html,
        "const bands=[makeRibbon(cfg,'filament',0),makeRibbon(cfg,'smoke',0),makeRibbon(cfg,'smoke',1)];",
        """const bands=[];
 for(let arm=0;arm<3;arm++){
  bands.push(makeRibbon(cfg,'filament',0,arm),
    makeRibbon(cfg,'smoke',0,arm),makeRibbon(cfg,'smoke',1,arm));
 }""",
        "three short filaments and layered clouds per color")
    html=once(html,
        "specs.push({u,phase,radial,drift:(Math.random()-.5)*.12});",
        "specs.push({u,phase,radial,arm:i%3,drift:(Math.random()-.5)*.12});",
        "scatter star groups among three true strands")
    html=once(html,
        "function location(u,phase,cfg,origin,offset=0,layer=0){",
        "function location(u,phase,cfg,origin,offset=0,layer=0,arm=0){",
        "address branch in shared upright trajectory")
    html=once(html,
        """ const pull=cfg.vortexPull??1,spin=cfg.preset==='vortexCyan'?Math.PI:0;
 const r=(.12+2.65*Math.pow(u,Math.max(.35,pull)))+offset;
 const a=phase+spin+u*10.2;""",
        """ const pull=cfg.vortexPull??1,spin=cfg.preset==='vortexCyan'?Math.PI/3:0;
 const r=(.15+2.68*Math.pow(u,Math.max(.35,pull)))+offset;
 // A short curved half-S, not a long circular orbit; alternating colors.
 const a=phase+spin+arm*TAU/3+u*3.0+.38*Math.sin(TAU*u);""",
        "short half-S sweep per branch")
    for before,after in (
       ("location(u0,phase,cfg,origin,0,b.index)",
        "location(u0,phase,cfg,origin,0,b.index,b.arm)"),
       ("location(u1,phase,cfg,origin,0,b.index)",
        "location(u1,phase,cfg,origin,0,b.index,b.arm)"),
       ("location(Math.max(0,u-.001),phase,cfg,origin,0,b.index)",
        "location(Math.max(0,u-.001),phase,cfg,origin,0,b.index,b.arm)"),
       ("location(Math.min(1,u+.001),phase,cfg,origin,0,b.index)",
        "location(Math.min(1,u+.001),phase,cfg,origin,0,b.index,b.arm)"),
       ("location(u,phase+spec.phase,cfg,origin,spec.radial,1)",
        "location(u,phase+spec.phase,cfg,origin,spec.radial,1,spec.arm)")
    ):
       html=once(html,before,after,"branch-aware filament and stars")
    # The curve runtime already multiplies vortexSpin by the editable
    # rotation curve; do not apply that curve *again* to render geometry.
    phase_old="rec.se249Time*(cfg.vortexSpin??1)*se251Rotation(cfg,rec.se251Clock||0)*1.65"
    assert html.count(phase_old)==2,("v11.258 double rotation",html.count(phase_old))
    html=html.replace(phase_old,"rec.se249Time*(cfg.vortexSpin??1)*.22")
    html=once(html,
        " const t=angle+u*10.2;",
        " const t=angle+u*3.0+.38*Math.sin(TAU*u);",
        "native vortex points follow short S, not old long orbit")
    html=once(html,
        "s.se249Arm=cfg.preset==='vortexCyan'?Math.PI:.0;",
        "s.se249Arm=(cfg.preset==='vortexCyan'?Math.PI/3:0)+Math.floor(Math.random()*3)*TAU/3;",
        "distribute native stars along the 3 alternating branches")
    html=once(html,
        "const a=rec.se249Time*spin*1.65+(s.se249Arm||0)+f*.85+s.se249Jitter;",
        "const a=rec.se249Time*spin*.22+(s.se249Arm||0)+f*.35+s.se249Jitter;",
        "slow native particles and reduce drift from filaments")
    html=once(html,
        "const a=(s.se249Phase||0)+(rec.se249Time*spin*2);",
        "const a=(s.se249Phase||0)+(rec.se249Time*spin*.3);",
        "slow outward sparks")
    html=once(html,
        "for(const band of rec.se249Bands||[])paintRibbon(cfg,rec,band);",
        "for(const band of rec.se249Bands||[])if(band.mesh.visible)paintRibbon(cfg,rec,band);",
        "do not recalculate invisible legacy spiral meshes")
    # Shader: keep translucent soft wisps visible at phone pixel sizes.
    html=once(html,
        "'  float cloud=smoothstep(.28,.77,.55*n+.45*n2);',",
        "'  float cloud=smoothstep(.24,.73,.55*n+.45*n2);',",
        "increase visible irregular cloud coverage")
    html=once(html,
        "'  float smoky=(.18+.82*cloud)*fray;',",
        "'  float smoky=(.31+.69*cloud)*fray;',",
        "smoke wisps retain base body and textured irregularities")
    html=once(html,
        """b.mat.uniforms.uOpacity.value=(b.kind==='filament'?.84:b.index===0?.23:.16)*""",
        """b.mat.uniforms.uOpacity.value=(b.kind==='filament'?.95:b.index===0?.46:.30)*""",
        "visible filament and layered smoke under additive glow")
    html=once(html,
        "' float pulse=.84+.16*sin(x*35.-uTime*2.4);',",
        "' float pulse=.91+.09*sin(x*19.-uTime*.55);',",
        "slow filament shimmer while the swirl turns")
    html=once(html,
        "' vec2 drift=vec2(x*23.+uTime*.18,y*5.7-uTime*.12);',",
        "' vec2 drift=vec2(x*23.+uTime*.045,y*5.7-uTime*.026);',",
        "slow internal nebula drift")

    # Recover from bad project particle data once per invalid instance.
    html=once(html,
        "const se223VerifiedModels=new WeakSet();",
        "const se223VerifiedModels=new WeakSet(),se258InvalidWarned=new WeakSet();",
        "limit invalid-project warning to a single toast")
    html=once(html,
        "  catch(error){return null;}\n }\n return data;\n}\nfunction se223List(){",
        """  catch(error){
   if(!se258InvalidWarned.has(data)){
    se258InvalidWarned.add(data);
    window.SWYRL_ENGINE_PARTICLE_ERRORS_258?.invalidLibrary(error);
   }
   return null;
  }
 }
 return data;
}
function se223List(){""",
        "warn on invalid embedded/saved particle models")
    # Scope failures to the emitter that raised them; do not mutate saved JSON.
    html=once(html,
        """ for(const cfg of data.emitters){
  const r=se223Runtime(cfg);r.cloud.visible=cfg.enabled;
  if(!cfg.enabled){r.particles.length=0;r.geometry.setDrawRange(0,0);continue;}
  if(cfg.mode==='burst'){if(!r.burstFired){se223Spawn(cfg,cfg.burst);r.burstFired=true;}}
  else{r.carry+=delta*cfg.rate;const amount=Math.min(24,Math.floor(r.carry));
   r.carry-=amount;if(amount)se223Spawn(cfg,amount);}
  se223Step(cfg,delta);
 }""",
        """ for(const cfg of data.emitters){
  if(window.SWYRL_ENGINE_PARTICLE_ERRORS_258?.shouldSkip(cfg))continue;
  try{
   const r=se223Runtime(cfg);r.cloud.visible=cfg.enabled;
   if(!cfg.enabled){r.particles.length=0;r.geometry.setDrawRange(0,0);continue;}
   if(cfg.mode==='burst'){if(!r.burstFired){se223Spawn(cfg,cfg.burst);r.burstFired=true;}}
   else{r.carry+=delta*cfg.rate;const amount=Math.min(24,Math.floor(r.carry));
    r.carry-=amount;if(amount)se223Spawn(cfg,amount);}
   se223Step(cfg,delta);
  }catch(error){
   window.SWYRL_ENGINE_PARTICLE_ERRORS_258?.emitterFailure(cfg,error);
   try{se223Drop(cfg.id);}catch(cleanup){
    const record=se223State.live.get(cfg.id);
    if(record?.cloud)record.cloud.visible=false;
    se223State.live.delete(cfg.id);
   }
  }
 }""",
        "contain faults per emitter without stopping shared frame loop")
    html=once(html,
        "se223Frame(dt,t);window.SWYRL_ENGINE_PARTICLE_UI_249?.frame?.(dt);",
        """try{se223Frame(dt,t);}catch(error){
 window.SWYRL_ENGINE_PARTICLE_ERRORS_258?.frameFailure(error);
}window.SWYRL_ENGINE_PARTICLE_UI_249?.frame?.(dt);""",
        "last-resort guard at the editor-to-particle boundary")
    guard = """// §E v11.258 — runtime fault boundary; no per-frame DOM writes.
(function(){
'use strict';
const failures=new Map(),fatalMessages=new Set();
let last=null;
function notify(message){
 const detail=String(message||'Unknown particle error').slice(0,130);
 try{toast('Particle effect error: '+detail);}catch(e){console.warn(detail);}
 const status=document.getElementById('se223Status');
 if(status){status.textContent='Particle preview error · '+detail;status.dataset.error='true';}
}
const api={
 shouldSkip:cfg=>{
  const previous=failures.get(cfg.id);
  if(!previous)return false;
  if(previous.cfg===cfg)return true;
  failures.delete(cfg.id);return false;
 },
 emitterFailure:(cfg,error)=>{
  const previous=failures.get(cfg.id);
  if(previous?.cfg===cfg)return;
  failures.set(cfg.id,{cfg,error:String(error?.message||error)});
  last={emitterId:cfg.id,name:cfg.name,message:String(error?.message||error)};
  console.error('[§E particle emitter isolated]',cfg.name,error);
  notify((cfg.name||'Emitter')+' disabled in preview · '+last.message);
 },
 invalidLibrary:error=>{
  last={invalidLibrary:true,message:String(error?.message||error)};
  console.warn('[§E particle data rejected]',error);
  notify('Invalid saved particle data · '+last.message);
 },
 frameFailure:error=>{
  const msg=String(error?.message||error);
  if(fatalMessages.has(msg))return;
  fatalMessages.add(msg);last={frameFailure:true,message:msg};
  console.error('[§E particle frame isolated]',error);
  notify('Preview frame failed · '+msg);
 },
 inspect:()=>({failedEmitters:[...failures].map(([id,v])=>({id,message:v.error})),
  last,isolated:true})
};
window.SWYRL_ENGINE_PARTICLE_ERRORS_258=Object.freeze(api);
})();
"""
    html=once(html,"window.SWRLZ_FORGE_BUILD=",guard+"\nwindow.SWRLZ_FORGE_BUILD=",
        "install preview diagnostics and editor-preserving fault boundary")

    old=" source.engine='§wyrl§ Engine · Maker v11.257';source.version=11.257;"
    assert html.count(old)==2,("v11.258 provenance",html.count(old))
    html=html.replace(old,
        " source.engine='§wyrl§ Engine · Maker v11.258';source.version=11.258;")
    for before,after in (
       ("SWYRL_ENGINE_DEPLOY_MARKER: V11_257_GALAXY_FIRST_FRAME_UNFREEZE",
        "SWYRL_ENGINE_DEPLOY_MARKER: V11_258_SLOW_NEBULA_FAULT_GUARD"),
       ("ENGINE · MAKER v11.257","ENGINE · MAKER v11.258"),
       ("v11.257 · Galaxy first-frame ReferenceError hotfix",
        "v11.258 · slow half-S nebula and isolated particle errors"),
       ("window.SWRLZ_FORGE_BUILD={version:'v11.257'",
        "window.SWRLZ_FORGE_BUILD={version:'v11.258'"),
       ("<title>§wyrl§ Engine · Maker v11.257</title>",
        "<title>§wyrl§ Engine · Maker v11.258</title>")
    ):html=once(html,before,after,"release identity")
    key="const SE_RELEASE_NOTES="
    at=html.index(key)+len(key)
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title="Slow galaxy swirls, layered half-S smoke and resilient Particle Studio",
      date="2026-11-04",changes=[
       "Rebuild the portal's two long orbiting rings as six short half-S energy filaments: three violet, three cyan, each with two widening jagged smoke layers and twinkling small and large stars.",
       "Give the smoke visible textured opacity and a soft fade at the ends; enhance the bright filaments and reduce internal shimmer speed without creating another WebGL renderer.",
       "Rotate the galaxy and native particle trajectories slowly, removing duplicated rotation-curve multiplication and unnecessary invisible legacy ribbon updates.",
       "Contain particle runtime exceptions per emitter: faulty effects disappear from preview and show a one-time error toast, while remaining emitters, timeline, camera navigation and editor main tick continue.",
       "Reject invalid project particle libraries with a one-time visible toast rather than silently blanking the effect. No destructive changes to saved particle JSON.",
       "v11.257's first-frame TDZ fix, one renderer, native particle limit, Sheep Tag, game models and Quest controls remain in place. Owner mobile and Quest visual/performance acceptance required."
    ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,
        separators=(",",":")).replace("</","<\\/")+html[at+width:]
