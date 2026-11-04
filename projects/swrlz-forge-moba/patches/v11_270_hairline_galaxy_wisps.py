"""§E v11.270 — distinct thin secondary wisps for the owner's galaxy reference.

The screenshot after v11.269 proves the compact spiral shape, but fine wisps
are hidden within fat mist stamps. Extend the existing batched purple root
ribbons into visible hairline purple/cyan filaments between and just outside
the large arms. Keep one mesh per vortex emitter, no new renderer, RAF, stars,
or particle emitter. Retain the saved projects, Quest LAN and editor controls.
"""
import json

def once(src,old,new,reason):
    n=src.count(old)
    if n!=1:raise AssertionError(("v11.270",reason,n,old[:180]))
    return src.replace(old,new,1)

def apply(html):
    start="const ROOT_N=3,ROOT_SEG=26;"
    end="// Purple light bloom around the EXISTING white/hot core emitter."
    assert html.count(start)==1 and html.count(end)==1
    a=html.index(start)
    b=html.index(end,a)
    assert "function makeInnerTendrils(cfg){" in html[a:b]
    assert "function updateInnerTendrils(t,cfg,rec,origin){" in html[a:b]
    replacement=r"""
// Three violet nucleus roots and six *independent* hairline wisps for each
// violet/cyan native emitter. One shared, disposable ribbon mesh per emitter.
// Local strand colors are computed only when an emitter is created.
const ROOT_N=9,ROOT_SEG=28,ROOT_INNER=3;
function se270WispSpec(k,cfg){
 const inner=k<ROOT_INNER;
 const n=k-ROOT_INNER;
 return {
  inner,
  start:inner?.012+.020*k:.24+.051*(n%4),
  length:inner?.27+.064*k:.39+.052*(n%3),
  arm:inner?(k+.42):((n*.48)+.20),
  offset:inner?0:((n%2)?-.041:.041),
  height:inner?0:((n%3)-1)*.038,
  blue:!inner&&((cfg.preset==='vortexCyan')||(n%3===1)),
 };
}
function makeInnerTendrils(cfg){
 const g=new THREE.BufferGeometry();
 const positions=new Float32Array(ROOT_N*ROOT_SEG*18);
 const colors=new Float32Array(ROOT_N*ROOT_SEG*18);
 const specs=[];
 const ink=new THREE.Color();
 for(let k=0;k<ROOT_N;k++){
  const spec=se270WispSpec(k,cfg);specs.push(spec);
  for(let i=0;i<ROOT_SEG;i++){
   const u0=i/ROOT_SEG,u1=(i+1)/ROOT_SEG;
   // Vertex order: left/right at start, left/right at end.
   for(let j=0;j<6;j++){
    const t=(j===2||j===4||j===5)?u1:u0;
    const root=se264Smooth((t-.05)/.65);
    const blue=spec.blue?root*(k%3===0?.91:.65):0;
    const soft=spec.inner?.83:.89;
    const fade=Math.pow(Math.sin(Math.PI*(.022+.956*t)),.48);
    const strength=soft*(.19+.81*fade);
    ink.copy(se264Purple).lerp(se264Blue,blue).multiplyScalar(strength);
    ink.toArray(colors,((k*ROOT_SEG+i)*6+j)*3);
   }
  }
 }
 g.setAttribute('position',new THREE.BufferAttribute(positions,3).setUsage(THREE.DynamicDrawUsage));
 g.setAttribute('color',new THREE.BufferAttribute(colors,3));
 g.setDrawRange(0,ROOT_N*ROOT_SEG*6);
 const mat=new THREE.MeshBasicMaterial({color:0xffffff,vertexColors:true,
  transparent:true,depthWrite:false,depthTest:true,side:THREE.DoubleSide,
  blending:THREE.AdditiveBlending,opacity:.82});
 const mesh=new THREE.Mesh(g,mat);
 mesh.frustumCulled=false;mesh.renderOrder=9;
 mesh.name='Astral Vortex · batched slim violet/cyan wisps';
 return {g,mat,mesh,specs};
}
function updateInnerTendrils(t,cfg,rec,origin){
 const attr=t.g.getAttribute('position');
 const phase=rec.se249Time*(cfg.vortexSpin??1)*.22;
 const width=clamp(cfg.vortexGlow??1,.15,2);
 for(let k=0;k<ROOT_N;k++){
  const spec=t.specs[k];
  const arm=spec.arm+(cfg.preset==='vortexCyan'?.5:0);
  const at=v=>location(Math.min(1.08,spec.start+spec.length*v),
   phase,cfg,origin,spec.offset*v,0,arm);
  for(let i=0;i<ROOT_SEG;i++){
   const u0=i/ROOT_SEG,u1=(i+1)/ROOT_SEG;
   const p0=at(u0),p1=at(u1);
   const before=at(Math.max(0,u0-.006)),after=at(Math.min(1,u1+.006));
   const dx=after[0]-before[0],dy=after[1]-before[1];
   const inv=1/Math.max(.0001,Math.hypot(dx,dy)),nx=-dy*inv,ny=dx*inv;
   // Narrow, softly tapered lines: smaller than main energy arms.
   const w=u=>(spec.inner?.0045:.0065)+
      (spec.inner?.010:.009)*Math.sin(Math.PI*u);
   const w0=w(u0),w1=w(u1);
   const a0=[p0[0]+nx*w0,p0[1]+ny*w0,p0[2]+spec.height*u0];
   const b0=[p0[0]-nx*w0,p0[1]-ny*w0,p0[2]+spec.height*u0];
   const a1=[p1[0]+nx*w1,p1[1]+ny*w1,p1[2]+spec.height*u1];
   const b1=[p1[0]-nx*w1,p1[1]-ny*w1,p1[2]+spec.height*u1];
   const six=[a0,b0,a1,b0,b1,a1];
   for(let j=0;j<6;j++){
    const v=six[j],ix=(k*ROOT_SEG+i)*6+j;
    attr.setXYZ(ix,v[0],v[1],v[2]);
   }
  }
 }
 attr.needsUpdate=true;
 t.mat.opacity=clamp(.83*width,.16,1);
}
"""
    html=html[:a]+replacement+html[b:]
    # Correct runtime inspection: only 3 roots, plus 6 fine exterior wisps.
    html=once(html,
        "innerPurpleRootsPerEmitter:ROOT_N,",
        "innerPurpleRootsPerEmitter:ROOT_INNER,slimWispsPerEmitter:ROOT_N-ROOT_INNER,",
        "report inner roots and hairline extensions separately")
    # A slightly less solid mist reveals the fine energy paths. Avoid
    # increasing pixel fill-rate or introducing new cloud layers.
    html=once(html,
        "' float alpha=clamp((haze*.90+wisp*.54)*edge*uMistDensity*shimmer,0.0,.30);',",
        "' float alpha=clamp((haze*.82+wisp*.50)*edge*uMistDensity*shimmer,0.0,.265);',",
        "subtle less opaque smoke body")
    # Preserve one main filament per long arm; make it readable on mobile.
    html=once(html,
        "   .031+u*.014:",
        "   .034+u*.015:",
        "brighten existing flowing large paths only through narrow geometry")
    for marker in (
        "window.SWYRL_ENGINE_PARTICLE_ERRORS_258",
        "window.SWYRL_ENGINE_SHEEP_NERD_STATS_265",
        "window.SWYRL_ENGINE_SHEEP_VR_LAN_268",
        "function se264Profile(cfg,arm){",
        "function makeCoreHalo(){",
        "const se263AtlasTexture=new THREE.TextureLoader().load(",
        "renderer.setAnimationLoop(tick);",
        "['nebulaDensity','Smoke density',.1,2,.05,1]",
    ):
        assert marker in html,("v11.270 preserve",marker)
    old=" source.engine='§wyrl§ Engine · Maker v11.269';source.version=11.269;"
    assert html.count(old)==2,("v11.270 version",html.count(old))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.270';source.version=11.270;")
    for x,y in (
        ("SWYRL_ENGINE_DEPLOY_MARKER: V11_269_REFERENCE_SPIRAL_WISPS",
         "SWYRL_ENGINE_DEPLOY_MARKER: V11_270_HAIRLINE_GALAXY_WISPS"),
        ("ENGINE · MAKER v11.269","ENGINE · MAKER v11.270"),
        ("v11.269 · cohesive spiral galaxy wisps",
         "v11.270 · fine secondary galaxy wisps"),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.269'",
         "window.SWRLZ_FORGE_BUILD={version:'v11.270'"),
        ("<title>§wyrl§ Engine · Maker v11.269</title>",
         "<title>§wyrl§ Engine · Maker v11.270</title>"),
    ):
        html=once(html,x,y,"release identity")
    key="const SE_RELEASE_NOTES="
    at=html.index(key)+len(key)
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title="Reference-style slender violet/cyan wisps between spiral galaxy arms",
        date="2026-11-04",changes=[
            "Add six slim independently curved wisps per colored native vortex emitter between the six broad glowing arms, alongside three short purple central roots per emitter.",
            "Short purple and longer violet-to-cyan fine strands taper gradually and move with the existing spiral. Generate per-vertex spectral colors once; animate only one shared mesh per colored emitter.",
            "Reduce cloud opacity slightly and strengthen the main continuous filaments so small crisp wisps stand in front of the puffy body.",
            "Keep all particle controls, camera/timeline, saved effects, error boundary, Sheep Tag LAN and Nerd Stats. No new WebGL renderer or frame loop.",
            "Visual acceptance requires owner mobile screenshot; Quest performance acceptance remains pending."
        ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,
        separators=(",",":")).replace("</","<\\/")+html[at+width:]
