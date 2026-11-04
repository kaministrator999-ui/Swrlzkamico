"""§E v11.256 · Particle Chamber project rebind, living-sheep path budget,
and true VR controller ground/menu ray. Append-only; no source history rewrite.
"""
from pathlib import Path
import json

def once(s,old,new,label):
    n=s.count(old)
    if n!=1:raise AssertionError(("v11.256",label,n,old[:140]))
    return s.replace(old,new,1)

def apply(html):
    root=Path(__file__).resolve().parents[1]
    ray=(root/"runtime/sheep_real_build_ray_v11_256.js").read_text("utf8")

    html=once(html,
       """    if(scene!==state.scene||camera!==state.camera||
       currentProject!==state.project||
       window.SWYRL_ENGINE_STUDIOS?.active?.()!=='particles'||
       playing||simulating||renderer.xr?.isPresenting){
      close();return false;
    }""",
       """    const editing=window.SWYRL_ENGINE_STUDIOS?.active?.()==='particles'&&
      !playing&&!simulating&&!renderer.xr?.isPresenting;
    if(!editing||!currentProject){close();return false;}
    if(scene!==state.scene||camera!==state.camera){
      close();
      if(!open())return false;
    }else if(currentProject!==state.project){
      // Editing history may replace project identity without changing scene.
      // Keep the existing chamber camera/layer, discard stale GPU emitters.
      state.project=currentProject;
      se223Reset();
      se223State.preview=true;
      state.projectRebinds=(state.projectRebinds||0)+1;
    }""",
       "keep chamber alive across emitter/project identity changes")

    html=once(html,
       " const stageActive=window.SWYRL_ENGINE_PARTICLE_STAGE_240?.frame?.()===true;",
       """ const chamber=window.SWYRL_ENGINE_PARTICLE_STAGE_240;
 if(!chamber?.active?.()&&window.SWYRL_ENGINE_STUDIOS?.active?.()==='particles'&&
    !playing&&!simulating&&!renderer.xr?.isPresenting)chamber?.open?.();
 const stageActive=chamber?.frame?.()===true;""",
       "recover layer-25 VFX stage on next normal engine tick")
    html=once(html,
       "      rendererCount:1,layer:LAYER,zoomDistance:state.distance,",
       "      rendererCount:1,layer:LAYER,zoomDistance:state.distance,\n"
       "      projectRebinds:state.projectRebinds||0,",
       "expose chamber rebind count")

    old="""  if(danger){
    let best=null,score=-Infinity;
    for(let i=0;i<12;i++){
      const angle=i*Math.PI/6,x=unit.pos.x+Math.cos(angle)*7.5,z=unit.pos.z+Math.sin(angle)*7.5;
      if(stBlocked(x,z,ST_SHEEP_RADIUS))continue;
      const safety=Math.min(...wolves.map(w=>(x-w.pos.x)**2+(z-w.pos.z)**2));
      if(safety>score&&stPath(unit.pos,new THREE.Vector3(x,0,z),ST_SHEEP_RADIUS)){score=safety;best={x,z};}
    }
    if(best)stSetOrder(unit,{action:'move',...best});return;
  }"""
    new="""  if(danger){
    const options=[];
    for(let i=0;i<12;i++){
      const angle=i*Math.PI/6,x=unit.pos.x+Math.cos(angle)*7.5,z=unit.pos.z+Math.sin(angle)*7.5;
      if(stBlocked(x,z,ST_SHEEP_RADIUS))continue;
      const safety=Math.min(...wolves.map(w=>(x-w.pos.x)**2+(z-w.pos.z)**2));
      options.push({x,z,safety});
    }
    // Same safest reachable destination, fewer A* calls for weaker options.
    options.sort((a,b)=>b.safety-a.safety);
    for(const option of options){
      if(stPath(unit.pos,new THREE.Vector3(option.x,0,option.z),ST_SHEEP_RADIUS)){
        stSetOrder(unit,{action:'move',x:option.x,z:option.z});
        break;
      }
    }
    return;
  }"""
    html=once(html,old,new,"rank cheap sheep escape candidates before A*")
    html=once(html,
       "if(unit.captured||s.elapsed<unit.botAt)return;unit.botAt=s.elapsed+.8;",
       "if(unit.captured||s.elapsed<unit.botAt)return;"
       "unit.botAt=s.elapsed+.8+((unit.botIndex||0)%5)*.035;",
       "spread AI sheep replanning over time")

    html=once(html,"window.SWRLZ_FORGE_BUILD=",ray+"\nwindow.SWRLZ_FORGE_BUILD=",
       "integrate physical controller ray after all previous XR wrappers")

    old=" source.engine='§wyrl§ Engine · Maker v11.255';source.version=11.255;"
    assert html.count(old)==2,("v11.256 provenance",html.count(old))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.256';source.version=11.256;")
    for a,b in (
       ("SWYRL_ENGINE_DEPLOY_MARKER: V11_255_PARTICLE_VIEWPORT_OWNERSHIP",
        "SWYRL_ENGINE_DEPLOY_MARKER: V11_256_GALAXY_AI_XR_RAY"),
       ("ENGINE · MAKER v11.255","ENGINE · MAKER v11.256"),
       ("v11.255 · native particle viewport ownership and input",
        "v11.256 · galaxy chamber, sheep AI pathing and XR build rays"),
       ("window.SWRLZ_FORGE_BUILD={version:'v11.255'",
        "window.SWRLZ_FORGE_BUILD={version:'v11.256'"),
       ("<title>§wyrl§ Engine · Maker v11.255</title>",
        "<title>§wyrl§ Engine · Maker v11.256</title>")):
       html=once(html,a,b,"release identity")

    key="const SE_RELEASE_NOTES="
    at=html.index(key)+len(key)
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title="Particle chamber continuity, AI sheep navigation and VR ground-pointer fixes",
      date="2026-11-04",changes=[
       "Particle Studio stays mounted when editing a particle or changing project identity. It rebinds live emitters without discarding camera controls, and recovers the stage after a legitimate scene/camera transition.",
       "Living AI sheep evaluate the safest available escape candidates first, so they perform fewer expensive A* route searches while retaining the same best reachable destination; bot decisions are staggered slightly.",
       "In Sheep Tag Quest Play, the right-hand build selector uses the real controller-to-terrain ray anywhere within the playable map; the sheep-relative synthetic build guide has been disabled.",
       "The building ghost is only visible while aiming at the actual ground; sky, a blocked/outside-map ray or an open radial hides it without unequipping the house.",
       "The normal controller ray and contact reticle render in front of the VR radial menus and show the actual menu hit point. Native movement, selected skills, authoritative building rules and project data are unchanged."
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(",",":")).replace("</","<\\/")+html[at+width:]
