"""§E v11.246: wire the mobile Particle Studio bottom toggle to real collapse.

Append-only over sealed v11.245; retain editor VFX, sections, camera stage,
project persistence, game play and Quest controller behavior unchanged.
"""
from pathlib import Path
import json


def once(source, old, new, purpose):
    count=source.count(old)
    if count!=1:
        raise AssertionError(("v11.246 anchor",purpose,count,old[:100]))
    return source.replace(old,new,1)


def apply(html):
    root=Path(__file__).resolve().parents[1]
    js=(root/"runtime/particle_bottom_toggle_v11_246.js").read_text(encoding="utf8")
    css=(root/"runtime/particle_bottom_toggle_v11_246.css").read_text(encoding="utf8")
    for anchor in (
      "SWYRL_ENGINE_DEPLOY_MARKER: V11_245_PARTICLE_INSPECTOR_COLLAPSE",
      "window.SWYRL_ENGINE_PARTICLE_COLLAPSE_245",
      "se243InspectorToggle",
      "window.SWYRL_ENGINE_PARTICLE_STAGE_240",
      "window.SWRLZ_FORGE_BUILD=",
      "const SE_RELEASE_NOTES=",
    ):
        if anchor not in html:
            raise AssertionError(("v11.246 prerequisite",anchor))
    html=html.replace("</head>",
      '<style id="se246ParticleBottomToggleStyle">\n'+css+'\n</style>\n</head>',1)
    html=once(html,"window.SWRLZ_FORGE_BUILD=",
      js+"\nwindow.SWRLZ_FORGE_BUILD=",
      "install mobile collapse bridge")
    old=" source.engine='§wyrl§ Engine · Maker v11.245';source.version=11.245;"
    if html.count(old)!=2:
        raise AssertionError(("v11.246 provenance",html.count(old)))
    html=html.replace(old,
      " source.engine='§wyrl§ Engine · Maker v11.246';source.version=11.246;")
    for before,after in (
      ("SWYRL_ENGINE_DEPLOY_MARKER: V11_245_PARTICLE_INSPECTOR_COLLAPSE",
       "SWYRL_ENGINE_DEPLOY_MARKER: V11_246_PARTICLE_BOTTOM_TOGGLE"),
      ("ENGINE · MAKER v11.245","ENGINE · MAKER v11.246"),
      ("v11.245 · Particle Studio true inspector collapse",
       "v11.246 · Reliable mobile Particle Studio collapse"),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.245'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.246'"),
      ("<title>§wyrl§ Engine · Maker v11.245</title>",
       "<title>§wyrl§ Engine · Maker v11.246</title>"),
    ):
        html=once(html,before,after,"release identity")
    key="const SE_RELEASE_NOTES="
    at=html.index(key)+len(key)
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title="Particle Studio mobile bottom panel now truly collapses",
      date="2026-11-03",changes=[
        "The visible mobile Particle Studio Compact/Expand button now minimizes settings to the bottom header instead of only resizing the inspector.",
        "Use one obvious Collapse/Show controls button in the phone layout, with the v11.245 control retained for larger screens.",
        "Force a real 59px bottom panel and hide its scroll content, including on mobile browsers where older viewport-height rules had precedence.",
        "Preserve configured particle emitters, unsaved field values, editor section state, native VFX stage, project model, and game/Quest rendering.",
        "Owner Moto G Power and Quest Browser manual acceptance outstanding."
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,
      separators=(",",":")).replace("</","<\\/")+html[at+width:]
