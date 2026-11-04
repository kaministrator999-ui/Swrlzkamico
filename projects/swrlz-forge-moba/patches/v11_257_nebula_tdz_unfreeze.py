"""§E v11.257 — fix galaxy ribbon's TDZ ReferenceError on first live frame.

Append-only correction to the emitted HTML from v11.251. The original historical
module stays intact. The local b shadows outer band b and reads b.index during
its own initialization, aborting the shared animation callback.
"""
import json

def once(text, old, new, reason):
    count=text.count(old)
    if count!=1:
        raise AssertionError(("v11.257",reason,count,old[:130]))
    return text.replace(old,new,1)

def apply(html):
    html=once(html,
        """   const b=location(Math.min(1,u+.001),phase,cfg,origin,0,b.index);
   const dx=b[0]-a[0],dy=b[1]-a[1],s=Math.max(.0001,Math.hypot(dx,dy));""",
        """   const nextPoint=location(Math.min(1,u+.001),phase,cfg,origin,0,b.index);
   const dx=nextPoint[0]-a[0],dy=nextPoint[1]-a[1],s=Math.max(.0001,Math.hypot(dx,dy));""",
        "remove local b variable shadowing the outer ribbon band argument")
    old=" source.engine='§wyrl§ Engine · Maker v11.256';source.version=11.256;"
    assert html.count(old)==2,("v11.257 provenance",html.count(old))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.257';source.version=11.257;")
    for a,b in (
      ("SWYRL_ENGINE_DEPLOY_MARKER: V11_256_GALAXY_AI_XR_RAY",
       "SWYRL_ENGINE_DEPLOY_MARKER: V11_257_GALAXY_FIRST_FRAME_UNFREEZE"),
      ("ENGINE · MAKER v11.256","ENGINE · MAKER v11.257"),
      ("v11.256 · galaxy chamber, sheep AI pathing and XR build rays",
       "v11.257 · Galaxy first-frame ReferenceError hotfix"),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.256'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.257'"),
      ("<title>§wyrl§ Engine · Maker v11.256</title>",
       "<title>§wyrl§ Engine · Maker v11.257</title>")
    ):html=once(html,a,b,"release identity")
    key="const SE_RELEASE_NOTES="
    at=html.index(key)+len(key)
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title="Galaxy first-frame freeze: ribbon geometry variable repaired",
      date="2026-11-04",changes=[
       "Fix a confirmed JavaScript ReferenceError in Astral Vortex violet/cyan ribbon construction. A local variable shadowed the outer ribbon-band argument, aborting the engine's common animation callback.",
       "The forward normal sample now uses a distinct nextPoint variable. Spiral geometry, shaders, native particles, stars and the single WebGL renderer otherwise remain unchanged.",
       "The timeline/playhead and camera controls should continue updating when the galaxy is loaded. Saved project data, 12-emitter limits, stress tools, Sheep Tag AI and Quest controls are unchanged.",
       "Focused first-frame reproduction showed the original exception. Validate all four emitters and several animation frames with the corrected code before publication; final device acceptance remains pending."
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,
        separators=(",",":")).replace("</","<\\/")+html[at+width:]
