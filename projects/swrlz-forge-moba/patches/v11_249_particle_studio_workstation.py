"""§E v11.249 · real Particle Editor workstation, ribbon VFX and native modifier data.

Additive to sealed v11.248. Keep project schema compatible, preserve original
render loop, legacy game/VR controls, materials, models and Sheep Tag world.
"""
from pathlib import Path
import json


def once(s, old, new, why):
    count=s.count(old)
    if count!=1:
        raise AssertionError(("v11.249", why, count, old[:170]))
    return s.replace(old,new,1)


def apply(html):
    root=Path(__file__).resolve().parents[1]
    ui=(root/"runtime/particle_studio_workstation_v11_249.js").read_text("utf8")
    css=(root/"runtime/particle_studio_workstation_v11_249.css").read_text("utf8")
    ribbon=(root/"runtime/astral_vortex_ribbons_v11_249.js").read_text("utf8")
    # Compatible validated extension: pre-v11.249 project particles receive
    # defaults when validated/edited, and new fields survive Undo/Redo and JSON.
    html=once(html,
      "const SE223_NUMERIC=Object.freeze({\n rate:[0,80],burst:[1,96],life:[.1,8],speed:[0,12],spread:[0,4],",
      "const SE223_NUMERIC=Object.freeze({\n vortexSpin:[.1,5],vortexPull:[.1,2.5],vortexGlow:[.05,2],vortexTilt:[0,1.8],\n rate:[0,80],burst:[1,96],life:[.1,8],speed:[0,12],spread:[0,4],",
      "validate vortex modifiers")
    html=once(html,
      "  startColor:p.startColor,endColor:p.endColor,blend:p.blend,attachActorId:null};",
      "  startColor:p.startColor,endColor:p.endColor,blend:p.blend,attachActorId:null,\n"
      "  vortexSpin:p.vortexSpin??1,vortexPull:p.vortexPull??1,\n"
      "  vortexGlow:p.vortexGlow??1,vortexTilt:p.vortexTilt??.7};",
      "give old presets safe modifier defaults")
    html=once(html,
      "  blend:v.blend,attachActorId:v.attachActorId};",
      "  blend:v.blend,attachActorId:v.attachActorId,\n"
      "  vortexSpin:v.vortexSpin,vortexPull:v.vortexPull,\n"
      "  vortexGlow:v.vortexGlow,vortexTilt:v.vortexTilt};",
      "preserve validated vortex modifiers on save")
    # The isolated authoring stage owns its orbit camera, one existing renderer
    # and its hit shield. Extend its camera API without an extra render loop.
    html=once(html,
      "    entries:0,exits:0,lastError:'',yaw:.55,pitch:.26,distance:10.5,shield:null,hint:null,drag:null};",
      "    entries:0,exits:0,lastError:'',yaw:.55,pitch:.26,distance:10.5,\n"
      "    targetX:0,targetY:1.35,targetZ:0,shield:null,hint:null,drag:null};",
      "persist test chamber orbit target")
    html=once(html,
      "      state.yaw-=(e.clientX-d.x)*.007;\n"
      "      state.pitch=Math.max(-.15,Math.min(1.2,state.pitch+(e.clientY-d.y)*.006));",
      "      const mode=window.SWYRL_ENGINE_PARTICLE_UI_249?.inspect?.().tool||'orbit';\n"
      "      if(mode==='pan'){\n"
      "        state.targetX-=(e.clientX-d.x)*.012;\n"
      "        state.targetZ+=(e.clientY-d.y)*.012;\n"
      "      }else if(mode==='zoom'){\n"
      "        state.distance=Math.max(3.2,Math.min(23,state.distance+(e.clientY-d.y)*.04));\n"
      "      }else{\n"
      "        state.yaw-=(e.clientX-d.x)*.007;\n"
      "        state.pitch=Math.max(-.15,Math.min(1.54,state.pitch+(e.clientY-d.y)*.006));\n"
      "      }",
      "make existing stage drag tools functional")
    html=once(html,
      "    camera.position.set(Math.sin(state.yaw)*c*d,1.35+Math.sin(state.pitch)*d,Math.cos(state.yaw)*c*d);\n"
      "    camera.lookAt(0,1.35,0);",
      "    camera.position.set(state.targetX+Math.sin(state.yaw)*c*d,\n"
      "      state.targetY+Math.sin(state.pitch)*d,state.targetZ+Math.cos(state.yaw)*c*d);\n"
      "    camera.lookAt(state.targetX,state.targetY,state.targetZ);",
      "functional camera pan and focus")
    stage_api="""    adjust:(kind,value)=>{
      if(kind==='reset'){state.yaw=.55;state.pitch=.26;state.distance=10.5;
        state.targetX=0;state.targetY=1.35;state.targetZ=0;return true;}
      if(kind==='zoom'){state.distance=Math.max(3.2,Math.min(23,state.distance+Number(value||0)));return true;}
      if(kind==='view'){
        if(value==='top'){state.yaw=.01;state.pitch=1.53;}
        else if(value==='front'){state.yaw=0;state.pitch=0;}
        else if(value==='side'){state.yaw=Math.PI/2;state.pitch=0;}
        else{state.yaw=.55;state.pitch=.26;}
        return true;
      }
      return false;
    },
"""
    html=once(html,
      "    open,close,active:()=>state.active,frame,\n    inspect:()=>({",
      "    open,close,active:()=>state.active,frame,\n"+stage_api+"    inspect:()=>({",
      "expose existing stage camera modes")
    # Run UI timeline from the existing §E frame loop (no second RAF loop).
    html=once(html,
      "se223Frame(dt,t);se225MaterialFrame(dt,t);beginPhysicalContactFrame();",
      "se223Frame(dt,t);window.SWYRL_ENGINE_PARTICLE_UI_249?.frame?.(dt);"
      "se225MaterialFrame(dt,t);beginPhysicalContactFrame();",
      "native timeline update once per engine frame")
    html=once(html,"window.SWRLZ_FORGE_BUILD=",
      ribbon+"\n"+ui+"\nwindow.SWRLZ_FORGE_BUILD=",
      "mount workstation and extended vortex geometry")
    html=html.replace("</head>",
      '<style id="se249ParticleWorkstationStyle">\n'+css+'\n</style>\n</head>',1)
    old=" source.engine='§wyrl§ Engine · Maker v11.248';source.version=11.248;"
    if html.count(old)!=2:
      raise AssertionError(("v11.249 provenance count",html.count(old)))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.249';source.version=11.249;")
    for a,b in (
      ("SWYRL_ENGINE_DEPLOY_MARKER: V11_248_ASTRAL_VORTEX_STARTERS",
       "SWYRL_ENGINE_DEPLOY_MARKER: V11_249_PARTICLE_WORKSTATION"),
      ("ENGINE · MAKER v11.248","ENGINE · MAKER v11.249"),
      ("v11.248 · Astral Vortex and Starter Particles",
       "v11.249 · full Particle Editor workstation and ribbon VFX"),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.248'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.249'"),
      ("<title>§wyrl§ Engine · Maker v11.248</title>",
       "<title>§wyrl§ Engine · Maker v11.249</title>")
    ):html=once(html,a,b,"release identity")
    key="const SE_RELEASE_NOTES="
    at=html.index(key)+len(key)
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title="Native Particle Editor workstation matching purple concept UI",
      date="2026-11-04",changes=[
       "Desktop compositor now has a menu-and-command header, dedicated Project/Assets tree and thumbnail, central 3D stage tool strips, Timeline/Curves/Output dock and tabbed Properties/Emission/Forces/Material inspector.",
       "True collapsible property accordions retain the original native event bindings, project transactions, imports, exports and emitter selection; no decorative Save/Undo buttons replace the real editor actions.",
       "Touch devices show a visible timeline and one-at-a-time Project/Modifiers drawers so the viewport does not become a full-screen stack of forms.",
       "The isolated authoring stage adds real camera orbit/pan/zoom/focus and perspective/top/front/side control while preserving the game camera pose on exit.",
       "Astral Vortex now has animated, additive violet/cyan ribbon meshes, coherent spiraling point trajectories and editable, schema-validated spin, radial pull, glow and tilt parameters with backward-compatible defaults.",
       "All changes reuse the original Three.js renderer, engine tick, project serializer and 576-particle cap; no changes to Sheep Tag world objects, 3D physics, networking or Quest play controls.",
       "Owner Moto/Quest browser visual/performance acceptance remains required; narrow source syntax and manifest verification do not replace it."
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,
                                 separators=(",",":")).replace("</","<\\/")+html[at+width:]
