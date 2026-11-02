"""§E v11.226 candidate: native unified, context-aware tabbed popup browser.

Append-only patch. Native game/model/material/particle panels are portaled only
while the browser is open and restored on close; no duplicate tool state.
"""
from pathlib import Path
import json

def once(s, old, new):
    count=s.count(old)
    if count != 1:
        raise AssertionError(("v11.226 unified browser anchor", old[:150], count))
    return s.replace(old, new, 1)

def apply(html):
    root=Path(__file__).resolve().parents[1]
    js=(root/"runtime/unified_popup_browser_v11_226.js").read_text("utf8")
    css=(root/"runtime/unified_popup_browser_v11_226.css").read_text("utf8")
    html=once(html, "window.SWRLZ_FORGE_BUILD=",
              js+"\nwindow.SWRLZ_FORGE_BUILD=")
    html=once(html,"</head>","<style id=\"se226UnifiedBrowser\">"+css+"</style>\n</head>")
    html=once(html,
        " source.engine='§wyrl§ Engine · Maker v11.225';source.version=11.225;",
        " source.engine='§wyrl§ Engine · Maker v11.226';source.version=11.226;")
    for old,new in [
        ("SWYRL_ENGINE_DEPLOY_MARKER: V11_225_MATERIAL_TEXTURE_STUDIO_TABS",
         "SWYRL_ENGINE_DEPLOY_MARKER: V11_226_UNIFIED_POPUP_BROWSER"),
        ("ENGINE · MAKER v11.225","ENGINE · MAKER v11.226"),
        ("v11.225 · Material Texture Studio and four workspace tabs",
         "v11.226 · Unified contextual popup browser for native tools"),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.225'",
         "window.SWRLZ_FORGE_BUILD={version:'v11.226'"),
        ("<title>§wyrl§ Engine · Maker v11.225</title>",
         "<title>§wyrl§ Engine · Maker v11.226</title>")
    ]:
        html=once(html,old,new)
    key="const SE_RELEASE_NOTES="
    pos=html.index(key)+len(key)
    notes,consumed=json.JSONDecoder().raw_decode(html[pos:])
    notes.update(title="Universal tabbed browser for §E assets, tools and native inspectors",
                 date="2026-11-02",
                 changes=[
                   "Added one floating, searchable, touch-friendly, resizable and draggable §E Browser, launched from existing Game, Modeling, Particle and Material workspace tab bars. Workspace tab navigation remains independent.",
                   "The Game browser hosts the real Assets and Scene inspector nodes; Modeler hosts its original model/rig inspector; Particle and Materials workspaces host their real authoring inspectors. Native controls are portaled temporarily, not copied, and restored on tab or window close.",
                   "The Tools category discovers existing editor action controls instead of implementing a competing command system. Native button events, scene history, current project data and shared renderer remain authoritative.",
                   "The browser opens context-appropriate categories, supports search, Escape and Ctrl+Space, dismisses on outside click, and stores only tiny per-workspace category preferences in the browser session.",
                   "Compact canvas-first workspace hides the redundant side docks until their tab is opened, freeing viewport space on phone and desktop without removing any underlying editor, VR controller or project state.",
                   "Existing Sheep Tag live quick-build radial, VR in-world controls and headset interaction are unchanged. This version provides the §E browser in the 2D editor/Quest browser surface; a native WebXR spatial browser is a separate device-tested enhancement."
                 ])
    return html[:pos]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace("</","<\\/")+html[pos+consumed:]
