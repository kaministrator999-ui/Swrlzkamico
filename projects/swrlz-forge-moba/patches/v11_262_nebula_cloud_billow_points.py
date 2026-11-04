"""§E v11.262 — texture-shaped, camera-facing nebula smoke in the EXISTING render tick.

Mobile proof across three angles (2:33 PM): thin lines and stars render, while
two ribbon-only smoke bands per arm never provide the soft cloud mass of the
approved galaxy concept. Repeated alpha edits made either solid flat fans or
near-invisible bands. Keep the six filament paths/points unchanged; turn off
the planar smoke strips and replace them with ONE tiny draw-call-efficient
buffer of transparent, procedural smoke billboards per native vortex emitter.
Puffs run off existing se223Step, not another RAF/timer or editor scene.
"""
import json

def once(text, old, new, title):
    n=text.count(old)
    if n!=1:
        raise AssertionError(("v11.262",title,n,old[:180]))
    return text.replace(old,new,1)

def apply(html):
    mist_code=r"""
// §E v11.262: smoke billboards, 54 soft puffs per native arm record.
// One WebGL Points draw call per cyan/violet emitter, no textures/downloads.
const MIST_N=54;
const mistV=[
 'attribute float aMistSize;',
 'attribute float aMistSeed;',
 'attribute vec3 aMistTint;',
 'varying float vMistSeed;',
 'varying vec3 vMistTint;',
 'uniform float uMistPixels;',
 'void main(){',
 ' vMistSeed=aMistSeed;vMistTint=aMistTint;',
 ' vec4 mv=modelViewMatrix*vec4(position,1.0);',
 ' gl_Position=projectionMatrix*mv;',
 ' gl_PointSize=clamp(aMistSize*uMistPixels*(265.0/max(1.0,-mv.z)),3.0,76.0);',
 '}'
].join('\n');
const mistF=[
 'precision mediump float;',
 'varying float vMistSeed;',
 'varying vec3 vMistTint;',
 'uniform float uMistTime;',
 'uniform float uMistDensity;',
 'float mh(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}',
 'float mn(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.0-2.0*f);',
 'return mix(mix(mh(i),mh(i+vec2(1.,0.)),f.x),',
 'mix(mh(i+vec2(0.,1.)),mh(i+vec2(1.,1.)),f.x),f.y);}',
 'void main(){',
 ' vec2 q=gl_PointCoord*2.0-1.0;',
 ' float angle=vMistSeed*6.283185;',
 ' vec2 p=vec2(cos(angle)*q.x-sin(angle)*q.y,sin(angle)*q.x+cos(angle)*q.y);',
 ' vec2 drift=vec2(uMistTime*.023,-uMistTime*.016);',
 ' float n=mn(p*3.1+drift+vec2(vMistSeed*9.0,vMistSeed*13.0));',
 ' float n2=mn(p*7.2-drift*.6+vec2(vMistSeed*21.0,4.2));',
 ' vec2 warped=p+vec2((n-.5)*.52,(n2-.5)*.43);',
 ' float radius=length(warped*vec2(.92,1.22));',
 ' float feather=1.0-smoothstep(.30,.79,radius);',
 ' float texture=smoothstep(.26,.63,.60*n+.40*n2);',
 ' float vein=(p.y-.18*sin(p.x*5.0+vMistSeed*14.0))*4.8;',
 ' float curl=exp(-vein*vein);',
 ' float cloudy=feather*(.30+.70*texture)*(.70+.30*curl);',
 ' float alpha=min(.37,cloudy*(.36+.21*n)*uMistDensity);',
 ' gl_FragColor=vec4(vMistTint*(1.28+.90*n),alpha);',
 '}'
].join('\n');
function makeNebulaMist(cfg){
 const g=new THREE.BufferGeometry(),pos=new Float32Array(MIST_N*3);
 const sizes=new Float32Array(MIST_N),seeds=new Float32Array(MIST_N),
  colors=new Float32Array(MIST_N*3),specs=[];
 const start=new THREE.Color(cfg.startColor),end=new THREE.Color(cfg.endColor);
 for(let i=0;i<MIST_N;i++){
  const branch=i%3,ordinal=Math.floor(i/3);
  const u=.08+.88*(ordinal+.32+Math.random()*.55)/(MIST_N/3);
  const seed=Math.random(),side=(Math.random()-.5)*2.0;
  const variation=.82+Math.random()*.54;
  const size=(.45+1.22*u)*variation;
  sizes[i]=size;seeds[i]=seed;
  temp.copy(start).lerp(end,.06+.28*Math.random());
  temp.toArray(colors,i*3);
  specs.push({u,branch,phase:(Math.random()-.5)*.15,
    lateral:side*(.035+.28*u),height:(Math.random()-.5)*(.08+.30*u),
    depth:(Math.random()-.5)*(.07+.13*u),size});
 }
 g.setAttribute('position',new THREE.BufferAttribute(pos,3).setUsage(THREE.DynamicDrawUsage));
 const sizeAttr=new THREE.BufferAttribute(sizes,1);
 g.setAttribute('aMistSize',sizeAttr);
 g.setAttribute('aMistSeed',new THREE.BufferAttribute(seeds,1));
 g.setAttribute('aMistTint',new THREE.BufferAttribute(colors,3));
 const mat=new THREE.ShaderMaterial({
  vertexShader:mistV,fragmentShader:mistF,
  transparent:true,depthWrite:false,depthTest:true,blending:THREE.AdditiveBlending,
  uniforms:{uMistPixels:{value:Math.min(window.devicePixelRatio||1,2)},
   uMistTime:{value:0},uMistDensity:{value:1}}
 });
 const points=new THREE.Points(g,mat);
 points.name='Astral Vortex · volumetric-looking nebula mist';
 points.frustumCulled=false;points.renderOrder=7;
 return {g,mat,points,specs,sizeAttr,lastSpread:NaN};
}
function updateNebulaMist(m,cfg,rec,origin){
 const pos=m.g.getAttribute('position');
 const phase=rec.se249Time*(cfg.vortexSpin??1)*.22;
 const spread=clamp(cfg.nebulaSpread??1,.25,2.5);
 if(spread!==m.lastSpread){
  for(let i=0;i<m.specs.length;i++){
   m.sizeAttr.setX(i,m.specs[i].size*spread);
  }
  m.sizeAttr.needsUpdate=true;m.lastSpread=spread;
 }
 for(let i=0;i<m.specs.length;i++){
  const s=m.specs[i];
  const p=location(s.u,phase+s.phase,cfg,origin,s.lateral*spread,1,s.branch);
  pos.setXYZ(i,p[0],p[1]+s.height*spread,p[2]+s.depth*spread);
 }
 pos.needsUpdate=true;
 m.mat.uniforms.uMistTime.value=rec.se249Time;
 m.mat.uniforms.uMistDensity.value=clamp(cfg.nebulaDensity??1,.1,2);
}
"""
    html=once(html,
        "function create(cfg,r){",mist_code+"\nfunction create(cfg,r){",
        "install camera-facing mist particles in the existing nebula closure")
    html=once(html,
        """ for(const b of bands)r.cloud.add(b.mesh);
 r.cloud.add(stars.mesh);
 return {bands,stars};""",
        """ // Keep the six bright line filaments; retire only planar smoke sheets.
 for(const b of bands){
  if(b.kind==='smoke')b.mesh.visible=false;
  r.cloud.add(b.mesh);
 }
 const mist=makeNebulaMist(cfg);
 r.cloud.add(mist.points);
 r.cloud.add(stars.mesh);
 return {bands,stars,mist};""",
        "replace flat smoke surfaces, retain thin glowing filaments and stars")
    html=once(html,
        "for(const b of r.se251Nebula.bands)b.mesh.layers.mask=mask;",
        """for(const b of r.se251Nebula.bands)b.mesh.layers.mask=mask;
  r.se251Nebula.mist.points.layers.mask=mask;""",
        "keep existing editor/VR rendering layers for new smoke")
    html=once(html,
        """  for(const band of rec.se251Nebula.bands)writeMesh(band,cfg,rec,origin);
  updateStars(rec.se251Nebula.stars,cfg,rec,origin);""",
        """  for(const band of rec.se251Nebula.bands){
   if(band.kind==='filament')writeMesh(band,cfg,rec,origin);
  }
  updateNebulaMist(rec.se251Nebula.mist,cfg,rec,origin);
  updateStars(rec.se251Nebula.stars,cfg,rec,origin);""",
        "update mist from same existing tick; do not recalc retired smoke")
    html=once(html,
        """  const s=r.se251Nebula.stars;
  s.mesh.removeFromParent();s.g.dispose();s.mat.dispose();
  r.se251Nebula=null;""",
        """  const mist=r.se251Nebula.mist;
  mist.points.removeFromParent();mist.g.dispose();mist.mat.dispose();
  const s=r.se251Nebula.stars;
  s.mesh.removeFromParent();s.g.dispose();s.mat.dispose();
  r.se251Nebula=null;""",
        "dispose billboards and resources on emitter removal")
    html=once(html,
        "smokeLayersPerArm:2,starsPerArm:STARS,rendererCount:1,",
        "smokeLayersPerArm:0,nebulaPuffsPerColor:MIST_N,starsPerArm:STARS,rendererCount:1,",
        "inspection reports current actual smoke renderer")
    for marker in (
        "window.SWYRL_ENGINE_PARTICLE_ERRORS_258",
        "const nextPoint=location(Math.min(1,u+.001)",
        "['nebulaDensity','Smoke density',.1,2,.05,1]",
        "const a=phase+spin+arm*TAU/3+u*3.0+.38*Math.sin(TAU*u)"
    ):
        assert marker in html,("v11.262 legacy guard",marker)
    old=" source.engine='§wyrl§ Engine · Maker v11.261';source.version=11.261;"
    assert html.count(old)==2,("v11.262 provenance",html.count(old))
    html=html.replace(old,
        " source.engine='§wyrl§ Engine · Maker v11.262';source.version=11.262;")
    for before,after in (
        ("SWYRL_ENGINE_DEPLOY_MARKER: V11_261_LUMINOUS_NEBULA_WISPS",
         "SWYRL_ENGINE_DEPLOY_MARKER: V11_262_BILLOWING_GALAXY_MIST"),
        ("ENGINE · MAKER v11.261","ENGINE · MAKER v11.262"),
        ("v11.261 · visible luminous smoke wisps",
         "v11.262 · billowing camera-facing galaxy mist"),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.261'",
         "window.SWRLZ_FORGE_BUILD={version:'v11.262'"),
        ("<title>§wyrl§ Engine · Maker v11.261</title>",
         "<title>§wyrl§ Engine · Maker v11.262</title>")
    ):
        html=once(html,before,after,"release identity")
    key="const SE_RELEASE_NOTES="
    at=html.index(key)+len(key)
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title="Billowing galaxy nebula mist replaces flat smoke ribbons",
       date="2026-11-04",changes=[
        "Replace planar strip-based smoke with 54 fractal-noise, feathered, camera-facing nebula billboards per native violet/cyan emitter (one extra draw call each); keep all six short half-S filaments and stars.",
        "Give each plume a soft opaque-enough center, dark turbulent pockets, slowly crawling curl and irregular fading edges, widening outward instead of rendering smooth translucent fans.",
        "Use existing particle update tick and error containment, dynamic GPU position buffer, no external textures and no new native emitters or animation loops; clean up GPU resources at emitter removal.",
        "Preserve editor camera/pan/zoom/timeline, Sheep Tag, native saved smoke density and nebula spread, v11.257 first-frame repair and v11.258 emitter-failure toasts.",
        "Full source-integrity test precedes deployment; final smoky reference comparison requires owner real-device screenshot and performance assessment."
       ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,
        separators=(",",":")).replace("</","<\\/")+html[at+width:]
