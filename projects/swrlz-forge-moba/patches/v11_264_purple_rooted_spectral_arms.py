"""§E v11.264 — artist-referenced spectral roots, gradients and inner tendrils.

Maintain the proven six short dynamic half-S spiral curves and sampled mist
atlas. Instead of static emitter-wide purple/cyan, use per-arm shader gradients
rooted in violet, violet interruptions in cyan-dominant outer streams, distinct
mostly-purple paths, and six thin short purple secondary roots between long
arms. Purple halo behind existing white core; no new native emitter or tick.
The current batched mist remains one draw call per arm emitter, with slightly
more overlapped, tangent-biased atlas puffs. Preserve emitter error boundaries.
"""
import json

def once(src,old,new,why):
    n=src.count(old)
    if n!=1: raise AssertionError(("v11.264",why,n,old[:180]))
    return src.replace(old,new,1)

def apply(html):
    helper=r"""
// §E v11.264: each of six branches has its own spectral journey.
// Arm 0 on violet side stays purple; other violet arms mix gently.
// Cyan arms START purple, with the leftward long arm carrying
// intermittent purple bands even through its blue outer section.
const se264Purple=new THREE.Color('#f02bff');
const se264Blue=new THREE.Color('#13c9ff');
function se264Profile(cfg,arm){
 if(cfg.preset==='vortexCyan'){
  if(arm===1)return {blue:.97,patch:.92};
  return arm===0?{blue:.92,patch:.38}:{blue:.78,patch:.46};
 }
 return arm===0?{blue:0,patch:0}:
  arm===1?{blue:.23,patch:.40}:{blue:.50,patch:.65};
}
function se264Smooth(x){const y=clamp(x,0,1);return y*y*(3-2*y);}
function se264Blend(u,profile,seed){
 const root=se264Smooth((u-.16)/.51);
 const a=.5+.5*Math.sin(u*32.+seed*2.1);
 const b=.5+.5*Math.sin(u*13.-seed*3.8);
 const purpleBreak=se264Smooth((a-.43)/.45)*se264Smooth((b-.43)/.44);
 return clamp(root*profile.blue*(1.-profile.patch*.88*purpleBreak),0,1);
}
function se264Tint(out,u,profile,seed){
 return out.copy(se264Purple).lerp(se264Blue,se264Blend(u,profile,seed));
}
"""
    html=once(html,"function makeRibbon(cfg,kind,index,arm){",
              helper+"\nfunction makeRibbon(cfg,kind,index,arm){",
              "add per-arm palette calculator in shared nebula closure")

    html=once(html,"'uniform float uKind;',",
        """'uniform float uKind;',
'uniform float uBlueBlend;',
'uniform float uPurpleBreak;',
'uniform float uBranch;',""",
        "filament palette uniforms for different long/short arm treatments")
    html=once(html,
        "'  gl_FragColor=vec4(uColor*vec3(1.27,1.13,1.29),opacity);',",
        """'  vec3 violet=vec3(.98,.045,.92);',
'  vec3 blue=vec3(.025,.72,1.06);',
'  float b1=smoothstep(.16,.67,x)*uBlueBlend;',
'  float a=.5+.5*sin(x*32.+uBranch*2.1);',
'  float b=.5+.5*sin(x*13.-uBranch*3.8);',
'  float patch=smoothstep(.43,.88,a)*smoothstep(.43,.87,b);',
'  float blueRatio=clamp(b1*(1.-uPurpleBreak*.88*patch),0.,1.);',
'  vec3 stream=mix(violet,blue,blueRatio);',
'  gl_FragColor=vec4(stream*(1.08+.075*sin(x*64.-uTime*.11)),opacity);',""",
        "smooth violet origins and cyan tails with irregular purple intrusions")

    html=once(html,
        "uTime:{value:0},uKind:{value:kind==='filament'?0:1}",
        """uTime:{value:0},uKind:{value:kind==='filament'?0:1},
   uBlueBlend:{value:se264Profile(cfg,arm).blue},
   uPurpleBreak:{value:se264Profile(cfg,arm).patch},
   uBranch:{value:arm+(cfg.preset==='vortexCyan'?1.7:0)}""",
        "assign individual filament profiles without per-frame material creation")
    # The six bright filaments retain branch geometry. Their update only sets
    # opacity and time, and must NOT replace the individual color profiles.
    html=once(html,
        "  temp.copy(base).lerp(alt,.18+Math.random()*.6);",
        "  se264Tint(temp,u,se264Profile(cfg,i%3),i%3+(cfg.preset==='vortexCyan'?1.7:0));",
        "stars also originate violet, though bright stars may whiten later")

    html=once(html,
        "  temp.copy(start).lerp(end,.06+.28*Math.random());",
        "  se264Tint(temp,u,se264Profile(cfg,branch),branch+(cfg.preset==='vortexCyan'?1.7:0));",
        "tint smoke with corresponding gradient and intermittent purple cloud patches")

    # Continuous-looking swirls: more overlap, slightly softer individual stamps.
    html=once(html,"const MIST_N=54;","const MIST_N=72;",
        "24 instead of 18 wisps per long branch; same one-draw-call buffer")
    html=once(html,"const size=(.45+1.22*u)*variation;",
                  "const size=(.52+1.28*u)*variation;",
        "slightly stronger plume overlap, restrained outer width")
    html=once(html,
        "' float alpha=clamp(wisp*edge*uMistDensity*shimmer,0.0,.48);',",
        "' float alpha=clamp(wisp*edge*uMistDensity*shimmer*.78,0.0,.38);',",
        "blend adjacent smoke fragments rather than showing stamped silhouettes")
    html=once(html,
        "' float angle=vMistSeed*6.283185;',",
        "' float angle=1.5707963-vMistAngle+(vMistSeed-.5)*.46;',",
        "orient smoke strokes approximately tangent to current arm on screen")

    html=once(html,
        "'attribute float aMistVariant;',",
        "'attribute float aMistVariant;',\n 'attribute vec3 aMistTangent;',",
        "add dynamic tangent vector to each atlas puff")
    assert html.count("'varying float vMistVariant;',")==2
    html=html.replace("'varying float vMistVariant;',",
      "'varying float vMistVariant;',\n 'varying float vMistAngle;'",)
    html=once(html,
        "' gl_Position=projectionMatrix*mv;',",
        """' gl_Position=projectionMatrix*mv;',
' vec4 toward=projectionMatrix*modelViewMatrix*vec4(position+aMistTangent,1.0);',
' vec2 direction=toward.xy/max(.0001,toward.w)-gl_Position.xy/max(.0001,gl_Position.w);',
' vMistAngle=atan(direction.y,direction.x);',""",
        "derive projected tangent for point-sprite orientation")
    html=once(html,
        """ const g=new THREE.BufferGeometry(),pos=new Float32Array(MIST_N*3);
 const sizes=new Float32Array(MIST_N),seeds=new Float32Array(MIST_N),variants=new Float32Array(MIST_N),""",
        """ const g=new THREE.BufferGeometry(),pos=new Float32Array(MIST_N*3);
 const tangents=new Float32Array(MIST_N*3);
 const sizes=new Float32Array(MIST_N),seeds=new Float32Array(MIST_N),variants=new Float32Array(MIST_N),""",
        "allocate tangent buffer without creating per-puff render objects")
    html=once(html,
        """ g.setAttribute('position',new THREE.BufferAttribute(pos,3).setUsage(THREE.DynamicDrawUsage));""",
        """ g.setAttribute('position',new THREE.BufferAttribute(pos,3).setUsage(THREE.DynamicDrawUsage));
 g.setAttribute('aMistTangent',new THREE.BufferAttribute(tangents,3).setUsage(THREE.DynamicDrawUsage));""",
        "use one dynamic buffer for all smoke orientations")
    html=once(html,
        """ const pos=m.g.getAttribute('position');
 const phase=rec.se249Time*(cfg.vortexSpin??1)*.22;""",
        """ const pos=m.g.getAttribute('position'),orient=m.g.getAttribute('aMistTangent');
 const phase=rec.se249Time*(cfg.vortexSpin??1)*.22;""",
        "access single batched projected-tangent field")
    html=once(html,
        """  pos.setXYZ(i,p[0],p[1]+s.height*spread,p[2]+s.depth*spread);
 }
 pos.needsUpdate=true;""",
        """  pos.setXYZ(i,p[0],p[1]+s.height*spread,p[2]+s.depth*spread);
  const ahead=location(Math.min(.995,s.u+.014),phase+s.phase,cfg,origin,
    s.lateral*spread,1,s.branch);
  orient.setXYZ(i,ahead[0]-p[0],ahead[1]-p[1],ahead[2]-p[2]);
 }
 pos.needsUpdate=true;orient.needsUpdate=true;""",
        "follow each long-arm tangent as the camera and galaxy rotate")

    inner=r"""
// Six short inner violet tendrils, batched as ONE narrow mesh per native
// violet/cyan emitter; all rooted in the central magenta energy sphere.
const ROOT_N=3,ROOT_SEG=26;
function makeInnerTendrils(cfg){
 const g=new THREE.BufferGeometry(),positions=new Float32Array(ROOT_N*ROOT_SEG*18);
 const uv=new Float32Array(ROOT_N*ROOT_SEG*12);
 for(let k=0;k<ROOT_N;k++)for(let i=0;i<ROOT_SEG;i++){
  const u0=i/ROOT_SEG,u1=(i+1)/ROOT_SEG;
  for(let j=0;j<6;j++){
   const ix=(k*ROOT_SEG+i)*6+j;
   uv[ix*2]=(j===2||j===4||j===5)?u1:u0;
   uv[ix*2+1]=(j===1||j===3||j===4)?1:0;
  }
 }
 g.setAttribute('position',new THREE.BufferAttribute(positions,3).setUsage(THREE.DynamicDrawUsage));
 g.setAttribute('uv',new THREE.BufferAttribute(uv,2));
 g.setDrawRange(0,ROOT_N*ROOT_SEG*6);
 const mat=new THREE.ShaderMaterial({vertexShader:vShader,fragmentShader:fShader,
  transparent:true,depthWrite:false,side:THREE.DoubleSide,blending:THREE.AdditiveBlending,
  uniforms:{uColor:{value:se264Purple.clone()},uOpacity:{value:.77},
   uTime:{value:0},uKind:{value:0},uBlueBlend:{value:0},
   uPurpleBreak:{value:0},uBranch:{value:0}}});
 const mesh=new THREE.Mesh(g,mat);
 mesh.frustumCulled=false;mesh.renderOrder=9;
 mesh.name='Astral Vortex · short violet inner roots';
 return {g,mat,mesh};
}
function updateInnerTendrils(t,cfg,rec,origin){
 const attr=t.g.getAttribute('position');
 const phase=rec.se249Time*(cfg.vortexSpin??1)*.22;
 for(let k=0;k<ROOT_N;k++){
  const arm=k+.43+(cfg.preset==='vortexCyan'?.12:0);
  const len=.29+k*.038;
  const at=v=>location(.017+len*v,phase,cfg,origin,0,0,arm);
  for(let i=0;i<ROOT_SEG;i++){
   const u0=i/ROOT_SEG,u1=(i+1)/ROOT_SEG;
   const p0=at(u0),p1=at(u1);
   const before=at(Math.max(0,u0-.004)),after=at(Math.min(1,u1+.004));
   const dx=after[0]-before[0],dy=after[1]-before[1];
   const inv=1/Math.max(.0001,Math.hypot(dx,dy)),nx=-dy*inv,ny=dx*inv;
   const w0=(.004+.015*Math.sin(Math.PI*u0)),w1=(.004+.015*Math.sin(Math.PI*u1));
   const a=[p0[0]+nx*w0,p0[1]+ny*w0,p0[2]];
   const b=[p0[0]-nx*w0,p0[1]-ny*w0,p0[2]];
   const c=[p1[0]+nx*w1,p1[1]+ny*w1,p1[2]];
   const d=[p1[0]-nx*w1,p1[1]-ny*w1,p1[2]];
   const six=[a,b,c,b,d,c];
   for(let j=0;j<6;j++){
    const ix=((k*ROOT_SEG+i)*6+j);
    attr.setXYZ(ix,six[j][0],six[j][1],six[j][2]);
   }
  }
 }
 attr.needsUpdate=true;
 t.mat.uniforms.uTime.value=rec.se249Time;
 t.mat.uniforms.uOpacity.value=.77*clamp(cfg.vortexGlow??1,.15,2);
}
// Purple light bloom around the EXISTING white/hot core emitter.
const haloV=[
 'uniform float uPx;', 'void main(){',
 ' vec4 mv=modelViewMatrix*vec4(position,1.0);',
 ' gl_Position=projectionMatrix*mv;',
 ' gl_PointSize=clamp(1050.*uPx/max(1.0,-mv.z),14.0,158.0);',
 '}'
].join('\n');
const haloF=[
 'precision mediump float;','void main(){',
 ' vec2 q=(gl_PointCoord-.5)*2.;',
 ' float r=length(q);',
 ' float glow=exp(-r*r*3.8)*(1.-smoothstep(.70,1.0,r));',
 ' float nucleus=exp(-r*r*11.0);',
 ' gl_FragColor=vec4(vec3(.94,.06,.91),.33*glow+.22*nucleus);',
 '}'
].join('\n');
function makeCoreHalo(){
 const g=new THREE.BufferGeometry();
 g.setAttribute('position',new THREE.BufferAttribute(new Float32Array(3),3));
 const mat=new THREE.ShaderMaterial({vertexShader:haloV,fragmentShader:haloF,
  transparent:true,depthWrite:false,blending:THREE.AdditiveBlending,
  uniforms:{uPx:{value:Math.min(window.devicePixelRatio||1,2)}}});
 const mesh=new THREE.Points(g,mat);mesh.frustumCulled=false;
 mesh.renderOrder=-1;mesh.name='Astral Vortex · purple core energy halo';
 return {mesh,g,mat};
}
"""
    html=once(html,"function makeStars(cfg){",inner+"\nfunction makeStars(cfg){",
              "add batched short roots and core glow using the existing update tick")
    html=once(html,
        """ const mist=makeNebulaMist(cfg);
 r.cloud.add(mist.points);
 r.cloud.add(stars.mesh);
 return {bands,stars,mist};""",
        """ const mist=makeNebulaMist(cfg);
 const inner=makeInnerTendrils(cfg);
 r.cloud.add(mist.points);
 r.cloud.add(inner.mesh);
 r.cloud.add(stars.mesh);
 return {bands,stars,mist,inner};""",
        "attach three shorter internal purple filaments per native arm emitter")
    html=once(html,
        """se223Runtime=function(cfg){
 const r=oldRuntime(cfg);
 if(isArm(cfg.preset)){""",
        """se223Runtime=function(cfg){
 const r=oldRuntime(cfg);
 if(cfg.preset==='vortexCore'&&!r.se264CoreHalo){
  r.se264CoreHalo=makeCoreHalo();
  r.se264CoreHalo.mesh.layers.mask=r.cloud.layers.mask;
  r.cloud.add(r.se264CoreHalo.mesh);
 }
 if(isArm(cfg.preset)){""",
        "purple halo belongs only to Astral Vortex core record")
    html=once(html,
        """  r.se251Nebula.mist.points.layers.mask=mask;
  r.se251Nebula.stars.mesh.layers.mask=mask;""",
        """  r.se251Nebula.mist.points.layers.mask=mask;
  r.se251Nebula.inner.mesh.layers.mask=mask;
  r.se251Nebula.stars.mesh.layers.mask=mask;""",
        "keep new short roots on correct editor/VR layer")
    html=once(html,
        """ const origin=se223Origin(cfg);
 // Rotate the existing particle cloud toward the camera as well, so the two""",
        """ const origin=se223Origin(cfg);
 if(cfg.preset==='vortexCore'&&rec.se264CoreHalo){
  rec.se264CoreHalo.g.getAttribute('position').setXYZ(0,origin.x,origin.y+1.28,origin.z);
  rec.se264CoreHalo.g.getAttribute('position').needsUpdate=true;
 }
 // Rotate the existing particle cloud toward the camera as well, so the two""",
        "move halo with original center even if emitter position is edited")
    html=once(html,
        """  updateNebulaMist(rec.se251Nebula.mist,cfg,rec,origin);
  updateStars(rec.se251Nebula.stars,cfg,rec,origin);""",
        """  updateNebulaMist(rec.se251Nebula.mist,cfg,rec,origin);
  updateInnerTendrils(rec.se251Nebula.inner,cfg,rec,origin);
  updateStars(rec.se251Nebula.stars,cfg,rec,origin);""",
        "advance roots alongside original dynamic mist and bright arms")
    html=once(html,
        """se223DisposeRecord=function(r){
 if(r?.se251Nebula){""",
        """se223DisposeRecord=function(r){
 if(r?.se264CoreHalo){
  r.se264CoreHalo.mesh.removeFromParent();
  r.se264CoreHalo.g.dispose();r.se264CoreHalo.mat.dispose();
  r.se264CoreHalo=null;
 }
 if(r?.se251Nebula){""",
        "cleanup core halo on deleted project/emitter")
    html=once(html,
        """  const mist=r.se251Nebula.mist;
  mist.points.removeFromParent();mist.g.dispose();mist.mat.dispose();""",
        """  const mist=r.se251Nebula.mist;
  mist.points.removeFromParent();mist.g.dispose();mist.mat.dispose();
  const inner=r.se251Nebula.inner;
  inner.mesh.removeFromParent();inner.g.dispose();inner.mat.dispose();""",
        "cleanup secondary root strand mesh and material")
    html=once(html,
        """nebulaPuffsPerColor:MIST_N,atlasTiles:4,atlasSource:'owner nebula mask',starsPerArm:STARS,rendererCount:1,""",
        """nebulaPuffsPerColor:MIST_N,innerPurpleRootsPerEmitter:ROOT_N,
  armColorProfiles:'violet root / cyan ends / purple patches',purpleCoreHalo:true,
  atlasTiles:4,atlasSource:'owner nebula mask',starsPerArm:STARS,rendererCount:1,""",
        "expose color-structure inspection without modifying editor UI")
    for marker in (
       "window.SWYRL_ENGINE_PARTICLE_ERRORS_258",
       "['nebulaDensity','Smoke density',.1,2,.05,1]",
       "const nextPoint=location(Math.min(1,u+.001)",
       "const a=phase+spin+arm*TAU/3+u*3.0+.38*Math.sin(TAU*u)",
       "const se263AtlasTexture=new THREE.TextureLoader().load(",
    ):
       assert marker in html,("v11.264 preservation",marker)
    old=" source.engine='§wyrl§ Engine · Maker v11.263';source.version=11.263;"
    assert html.count(old)==2,("v11.264 provenance",html.count(old))
    html=html.replace(old,
       " source.engine='§wyrl§ Engine · Maker v11.264';source.version=11.264;")
    for a,b in (
      ("SWYRL_ENGINE_DEPLOY_MARKER: V11_263_REFERENCE_TEXTURED_MIST",
       "SWYRL_ENGINE_DEPLOY_MARKER: V11_264_PURPLE_ROOTED_SPECTRAL_ARMS"),
      ("ENGINE · MAKER v11.263","ENGINE · MAKER v11.264"),
      ("v11.263 · reference-textured nebula mist",
       "v11.264 · purple-rooted spectral galaxy arms"),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.263'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.264'"),
      ("<title>§wyrl§ Engine · Maker v11.263</title>",
       "<title>§wyrl§ Engine · Maker v11.264</title>")
    ):html=once(html,a,b,"release identity")
    key="const SE_RELEASE_NOTES="
    at=html.index(key)+len(key)
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title="Purple-origin branching energy, violet/cyan mixes and glowing sphere",
      date="2026-11-04",changes=[
       "All six long galaxy energy strands originate purple near the glowing center, then follow branch-specific violet/cyan gradients. Keep one entire major violet strand purple; blue-dominant long strands retain irregular purple streaks, especially on the left.",
       "Recolor the existing star group and image-derived smoke atlas puffs to the same per-branch gradient profiles with violet splotches in cyan; do not add any native emitters or per-frame cloned materials.",
       "Draw three narrow short purple-only tendrils per violet/cyan emitter as one batched GPU mesh each, between large spiral arms, and a separate soft magenta sphere glow behind the existing white-hot particle core.",
       "Make the existing 54-point mist batches 72 points each for overlapping flowing texture, with softer stamped alpha and camera-aware tangent alignment. Original user-derived atlas, slow swirl, editor controls and stored smoke density remain intact.",
       "Keep the v11.257 first-frame crash repair, per-emitter preview fault isolation, three-frame workstations, VR controls, resource disposal and original engine render loop; use one release package smoke-check, then owner phone/Quest visual testing."
    ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,
       separators=(",",":")).replace("</","<\\/")+html[at+width:]
