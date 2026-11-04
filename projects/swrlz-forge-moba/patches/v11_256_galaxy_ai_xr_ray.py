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

    # The current effective AI (not the obsolete base Sheep Tag function)
    # uses sheep AND wolf path lengths in its danger score. Spread its exact
    # 12-candidate decision over frames rather than deleting its tactics.
    html=once(html,"function stBotSheep(unit){",
      """const se256AIBudget={frame:-1,used:0,perFrame:2,checks:0,completed:0};
window.SWYRL_ENGINE_SHEEP_AI_BUDGET_256=Object.freeze({
 diagnose:()=>({...se256AIBudget,pending:stSession?.units?.filter(u=>u.se256Escape).length||0})
});
function stBotSheep(unit){""",
      "instrument frame-bounded live AI sheep evaluation")
    html=once(html,
      "if(unit.captured||unit.isIllusion||unit.archiveRoute||s.elapsed<unit.botAt)return;unit.botAt=s.elapsed+1.1;",
      "if(unit.captured||unit.isIllusion||unit.archiveRoute||"
      "(!unit.se256Escape&&s.elapsed<unit.botAt))return;"
      "if(!unit.se256Escape)unit.botAt=s.elapsed+1.1;",
      "continue a pending AI escape search across frames")
    old_start="  if(danger){let best=null,score=-Infinity;const candidates="
    assert html.count(old_start)==1,("v11.256 effective AI danger anchor",html.count(old_start))
    begin=html.index(old_start)
    end_token="}return;}"
    finish=html.index(end_token,begin)+len(end_token)
    replacement="""  if(danger){
    let scan=unit.se256Escape;
    if(!scan||scan.nav!==s.navVersion||scan.near!==near.id){
      const candidates=Array.from({length:12},(_,i)=>
        new THREE.Vector3(unit.pos.x+Math.cos(i*Math.PI/6)*6,0,
          unit.pos.z+Math.sin(i*Math.PI/6)*6));
      if(unit.base)candidates.unshift(unit.base.clone());
      scan=unit.se256Escape={candidates,index:0,score:-Infinity,best:null,
        nav:s.navVersion,near:near.id};
    }
    if(se256AIBudget.frame!==s.elapsed){
      se256AIBudget.frame=s.elapsed;se256AIBudget.used=0;
    }
    if(se256AIBudget.used<se256AIBudget.perFrame&&scan.index<scan.candidates.length){
      se256AIBudget.used++;se256AIBudget.checks++;
      const p=scan.candidates[scan.index++];
      if(!stBlocked(p.x,p.z,stUnitRadius(unit))){
        const route=stPath(unit.pos,p,stUnitRadius(unit));
        if(route){
          const safety=Math.min(...known.map(w=>p.distanceToSquared(w.pos)));
          const wolfPath=stPath(near.pos,p,stUnitRadius('wolf'));
          const defence=wolfPath?0:180;
          const value=safety+defence-route.length*.07;
          if(value>scan.score){scan.score=value;scan.best=p;}
        }
      }
    }
    if(scan.index>=scan.candidates.length){
      if(scan.best){
        unit.aiIntent='evade through a sheep-sized exit';
        stSetOrder(unit,{action:'move',x:scan.best.x,z:scan.best.z});
      }
      unit.se256Escape=null;se256AIBudget.completed++;
    }else unit.botAt=s.elapsed;
    return;
  }
  unit.se256Escape=null;"""
    html=html[:begin]+replacement+html[finish:]
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
       "Living AI sheep retain the existing sheep/wolf escape-route scoring, but evaluate at most two candidate routes across the flock per game frame, distributing A* work instead of producing synchronized spikes.",
       "In Sheep Tag Quest Play, the right-hand build selector uses the real controller-to-terrain ray anywhere within the playable map; the sheep-relative synthetic build guide has been disabled.",
       "The building ghost is only visible while aiming at the actual ground; sky, a blocked/outside-map ray or an open radial hides it without unequipping the house.",
       "The normal controller ray and contact reticle render in front of the VR radial menus and show the actual menu hit point. Native movement, selected skills, authoritative building rules and project data are unchanged."
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(",",":")).replace("</","<\\/")+html[at+width:]
