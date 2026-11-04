"""§E v11.250 — desktop/VR docks, resize/collapse and soft nebular vortex ribbons.
Only the Particle Studio runtime, UI and visuals are changed. No new renderer,
external resources, project schema or scene/VR gameplay mutations.
"""
from pathlib import Path
import json


def once(source, old, new, meaning):
    number=source.count(old)
    if number!=1:
        raise AssertionError(("v11.250",meaning,number,old[:180]))
    return source.replace(old,new,1)


def apply(html):
    root=Path(__file__).resolve().parents[1]
    js=(root/"runtime/particle_studio_docking_v11_250.js").read_text("utf8")
    css=(root/"runtime/particle_studio_docking_v11_250.css").read_text("utf8")
    # Fix the previous mobile breakpoint. Desktop-site and XR browser are
    # often coarse pointer / 980 CSS pixels and need true side panels.
    html=once(html,
       "@media(max-width:1080px),(pointer:coarse) and (max-width:1200px){",
       "@media(max-width:700px){","avoid misclassifying VR/desktop as mobile")
    # Add a post-v11.249 layout layer, initialized after the workstation exists.
    html=once(html,"window.SWRLZ_FORGE_BUILD=",
       js+"\nwindow.SWRLZ_FORGE_BUILD=","install real dock controls")
    html=html.replace("</head>",
       '<style id="se250DesktopDocksStyle">\n'+css+'\n</style>\n</head>',1)
    # Replace hard-edged colored triangle strips by smoothed, feathered GPU
    # ribbons; stays four lightweight meshes in the same THREE renderer.
    html=once(html,
      "  g.setAttribute('color',new THREE.BufferAttribute(new Float32Array(SEG*6*3),3));\n"
      "  g.setDrawRange(0,SEG*6);",
      "  g.setAttribute('color',new THREE.BufferAttribute(new Float32Array(SEG*6*3),3));\n"
      "  g.setAttribute('uv',new THREE.BufferAttribute(new Float32Array(SEG*6*2),2));\n"
      "  g.setDrawRange(0,SEG*6);",
      "add ribbon feather UV coordinates")
    old_mat="""  const mat=new THREE.MeshBasicMaterial({
   vertexColors:true,side:THREE.DoubleSide,transparent:true,depthWrite:false,
   blending:THREE.AdditiveBlending,opacity,color:0xffffff
  });"""
    new_mat="""  const mat=new THREE.ShaderMaterial({
   side:THREE.DoubleSide,transparent:true,depthWrite:false,
   blending:THREE.AdditiveBlending,
   uniforms:{uOpacity:{value:opacity},uTime:{value:0}},
   vertexShader:\`
    varying vec2 vRibbonUV;
    varying vec3 vRibbonColor;
    void main(){
     vRibbonUV=uv;
     vRibbonColor=color;
     gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);
    }\`,
   fragmentShader:\`
    precision mediump float;
    varying vec2 vRibbonUV;
    varying vec3 vRibbonColor;
    uniform float uOpacity;
    uniform float uTime;
    void main(){
     float edge=abs(vRibbonUV.y-0.5)*2.0;
     float feather=pow(1.0-smoothstep(0.09,0.98,edge),2.3);
     float flow=0.76+0.24*sin(vRibbonUV.x*28.0-uTime*2.2);
     float wisp=0.74+0.26*sin(vRibbonUV.x*59.0+uTime*1.4+edge*7.0);
     float lengthFade=smoothstep(0.0,0.06,vRibbonUV.x)*
       (1.0-smoothstep(0.83,1.0,vRibbonUV.x));
     float alpha=feather*flow*wisp*lengthFade*uOpacity;
     gl_FragColor=vec4(vRibbonColor*1.18,alpha);
    }\`
  });"""
    html=once(html,old_mat,new_mat,"feather ribbons in the original WebGL renderer")
    # Old segment normal produced visible dark cuts between individual ribbon
    # triangles. Compute a consistent joint normal at both segment endpoints.
    old_geometry="""  const tangentX=p1[0]-p0[0],tangentZ=p1[2]-p0[2];
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
   [p1[0]+nx*q1,p1[1],p1[2]+nz*q1]];"""
    new_geometry="""  const normalAt=t=>{
   const a=curve(Math.max(0,t-.001),phase+spin,pull,tilt);
   const b=curve(Math.min(1,t+.001),phase+spin,pull,tilt);
   const x=b[0]-a[0],z=b[2]-a[2],scale=Math.max(.00001,Math.hypot(x,z));
   return [-z/scale,x/scale];
  };
  const n0=normalAt(t0),n1=normalAt(t1);
  const q0=w*(.25+.75*Math.pow(1-t0,.4));
  const q1=w*(.25+.75*Math.pow(1-t1,.4));
  const verts=[
   [p0[0]+n0[0]*q0,p0[1],p0[2]+n0[1]*q0],
   [p0[0]-n0[0]*q0,p0[1],p0[2]-n0[1]*q0],
   [p1[0]+n1[0]*q1,p1[1],p1[2]+n1[1]*q1],
   [p0[0]-n0[0]*q0,p0[1],p0[2]-n0[1]*q0],
   [p1[0]-n1[0]*q1,p1[1],p1[2]-n1[1]*q1],
   [p1[0]+n1[0]*q1,p1[1],p1[2]+n1[1]*q1]];"""
    html=once(html,old_geometry,new_geometry,
      "make adjacent ribbon segments share normals and eliminate black seams")
    html=once(html,
      " const pos=band.mesh.geometry.attributes.position;\n const col=band.mesh.geometry.attributes.color;",
      " const pos=band.mesh.geometry.attributes.position;\n"
      " const col=band.mesh.geometry.attributes.color;\n"
      " const uv=band.mesh.geometry.attributes.uv;",
      "enable continuous ribbon transparency along its surface")
    html=once(html,
      " band.mesh.material.opacity=Math.min(1.65,band.opacity*(cfg.vortexGlow??1));",
      " band.mesh.material.uniforms.uOpacity.value=Math.min(1.2,band.opacity*(cfg.vortexGlow??1));\n"
      " band.mesh.material.uniforms.uTime.value=rec.se249Time||0;",
      "drive GPU color and opacity without material recompiles")
    html=once(html,
      "   pos.setXYZ(idx,src[0]+origin.x,src[1]+origin.y-1.7,src[2]+origin.z);",
      "   pos.setXYZ(idx,src[0]+origin.x,src[1]+origin.y-1.7,src[2]+origin.z);\n"
      "   const uvPair=[[t0,0],[t0,1],[t1,0],[t0,1],[t1,1],[t1,0]][v];\n"
      "   uv.setXY(idx,uvPair[0],uvPair[1]);",
      "soft edge interpolation on each ribbon triangle")
    html=once(html,
      " pos.needsUpdate=true;col.needsUpdate=true;\n}\nse223Step=function(cfg,dt){",
      " pos.needsUpdate=true;col.needsUpdate=true;uv.needsUpdate=true;\n}\n"
      "se223Step=function(cfg,dt){",
      "update ribbon UV buffers")
    # Dynamic ribbons are smoother, more wispy, and less like thick neon
    # concentric rings. The outer glowing halo stays visibly translucent.
    html=once(html,
       " const types=[['main',.14,.86],['halo',.35,.17]];",
       " const types=[['main',.13,.79],['halo',.31,.13]];",
       "tune volumetric wisps vs neon bands")
    html=once(html,
       "    entries:0,exits:0,lastError:'',yaw:.55,pitch:.26,distance:10.5,",
       "    entries:0,exits:0,lastError:'',yaw:.55,pitch:.62,distance:8.7,",
       "frame vortex in a studio-friendly oblique default perspective")
    html=once(html,
       "if(kind==='reset'){state.yaw=.55;state.pitch=.26;state.distance=10.5;",
       "if(kind==='reset'){state.yaw=.55;state.pitch=.62;state.distance=8.7;",
       "reset frame to showcase the vortex")
    # Loading Astral Vortex repeatedly should not display all older copies
    # of the four emitters together in the same isolated preview.
    old_group=""" const se248Selected=se223State.selected||data.emitters[0]?.id;
 const se248Group=stageActive&&data.emitters.some(e=>e.id===se248Selected&&/^vortex(?:Cyan|Core|Spark)?$/.test(e.preset));
 const editEmitters=stageActive?data.emitters.filter(e=>se248Group?/^vortex(?:Cyan|Core|Spark)?$/.test(e.preset):e.id===se248Selected):data.emitters;"""
    new_group=""" const se248Selected=se223State.selected||data.emitters[0]?.id;
 const selectedIndex=data.emitters.findIndex(e=>e.id===se248Selected);
 const se248Group=stageActive&&selectedIndex>=0&&/^vortex(?:Cyan|Core|Spark)?$/.test(data.emitters[selectedIndex]?.preset);
 let se250GroupStart=selectedIndex;
 if(se248Group){
  while(se250GroupStart>0&&data.emitters[se250GroupStart]?.preset!=='vortex'&&
   /^vortex(?:Cyan|Core|Spark)?$/.test(data.emitters[se250GroupStart-1]?.preset))se250GroupStart--;
 }
 const selectedGroup=se248Group?data.emitters.slice(se250GroupStart,se250GroupStart+4):[];
 const groupIds=new Set(selectedGroup.map(e=>e.id));
 const editEmitters=stageActive?data.emitters.filter(e=>se248Group?
   groupIds.has(e.id):e.id===se248Selected):data.emitters;"""
    html=once(html,old_group,new_group,"render only selected starter instance")
    # Only the editor CSS and UI change. Keep historical v11.249 identifier in
    # the old source snapshot, update the current built release identity.
    old_provenance=" source.engine='§wyrl§ Engine · Maker v11.249';source.version=11.249;"
    if html.count(old_provenance)!=2:
       raise AssertionError(("v11.250 source provenance",html.count(old_provenance)))
    html=html.replace(old_provenance,
       " source.engine='§wyrl§ Engine · Maker v11.250';source.version=11.250;")
    for old,new in (
      ("SWYRL_ENGINE_DEPLOY_MARKER: V11_249_PARTICLE_WORKSTATION",
       "SWYRL_ENGINE_DEPLOY_MARKER: V11_250_DESKTOP_DOCKS"),
      ("ENGINE · MAKER v11.249","ENGINE · MAKER v11.250"),
      ("v11.249 · full Particle Editor workstation and ribbon VFX",
       "v11.250 · resizable desktop/VR Particle Studio and soft vortex"),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.249'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.250'"),
      ("<title>§wyrl§ Engine · Maker v11.249</title>",
       "<title>§wyrl§ Engine · Maker v11.250</title>")
    ):html=once(html,old,new,"release identity")
    key="const SE_RELEASE_NOTES="
    at=html.index(key)+len(key)
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title="True desktop/VR docks and softened flowing Astral Vortex",
      date="2026-11-04",changes=[
       "Desktop-site mode and Quest browser are no longer forced into the narrow mobile stack by a 1080px/coarse-pointer breakpoint.",
       "Particle Studio uses independent left Project/Assets, right modifier and lower Timeline/Curves docks; all three have keyboard/pointer/touch resize handles, collapse/restore controls and session-persisted widths.",
       "A Layout selector chooses Auto, Desktop/VR and Compact; Auto uses a 700 CSS-pixel threshold; desktop can be explicitly selected on any screen.",
       "Both left tree and right modifier sections have independently collapsible native categories plus Expand all/Collapse all controls.",
       "Astral Vortex uses continuously joined, additive-shader alpha-feathered 3D ribbons rather than hard-edged segmented geometry; camera framing starts closer and higher.",
       "Previewing a selected Astral Vortex starter displays only that four-emitter instance, even when multiple copies exist in the native project library.",
       "The original WebGL renderer, native stage input, single tick, native emitters, scene/VR game controls, existing undo and project data format are preserved. Owner phone and Quest acceptance pending."
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,
      separators=(",",":")).replace("</","<\\/")+html[at+width:]
