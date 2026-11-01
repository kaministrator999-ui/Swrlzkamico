"""§E v11.195 — Quest Sheep Tag camera, render and controller UX repairs.
Append-only. Preserve all prior v11.194 artifacts until a new sealed release.
"""
from pathlib import Path
import json

def once(s,a,b):
    n=s.count(a)
    if n!=1:raise AssertionError(('v11.195 source anchor',a[:160],n))
    return s.replace(a,b,1)

def apply(html):
    root=Path(__file__).resolve().parents[1]
    js=(root/'runtime/engine_xr_sheep_stability_v11_195.js').read_text(encoding='utf8')
    # Source is already fully defined before its build marker. Install the
    # light-touch overrides only after all v11.194 original wrappers exist.
    html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=')
    for old,new in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_194_EMBERFALL_ARPG_STARTER',
       'SWYRL_ENGINE_DEPLOY_MARKER: V11_195_QUEST_SHEEP_STABILITY_RADIAL'),
      ('ENGINE · MAKER v11.194','ENGINE · MAKER v11.195'),
      ('v11.194 · Emberfall hack-and-slash RPG starter',
       'v11.195 · Quest Sheep Tag performance and radial controls'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.194'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.195'"),
      ('<title>§wyrl§ Engine · Maker v11.194</title>',
       '<title>§wyrl§ Engine · Maker v11.195</title>')
    ]:html=once(html,old,new)
    key='const SE_RELEASE_NOTES='
    pos=html.index(key)+len(key)
    notes,n=json.JSONDecoder().raw_decode(html[pos:])
    notes.update(title='Quest Sheep Tag: centered follow view, stable fog, cinematic entry, radial and controller effects',
      date='2026-10-31',changes=[
      'Fix XR sheep-follow camera reference offset by targeting the tracked headset eye at an elevated strategic world position relative to the controlled sheep, while retaining independent head rotation, orbit/zoom and free-pan.',
      'Cut XR-only per-frame full Sheep Tag status reconstruction and hidden browser HUD/minimap updates; render light terrain rays every headset frame and reserve expensive actor raycast for trigger clicks.',
      'Move cosmetic fog above the meadow layer with depth polygon offset and keep image repaints to approximately 3 Hz on Quest while leaving native visibility/AI and explored cells unchanged.',
      'Enter the real authored Main Menu cinematic automatically in VR, animate native sheep and buildings and present the menu from a gently moving sheep-centered viewing position, not by the houses. Allow holding the scene still if desired.',
      'Replace tall in-world dialog stacks with compact near-right-hand radial palettes for Sheep Tag and map editing. Use one calibrated native ray for visual hit feedback, blocking trigger-through into underlying actors.',
      'Retire duplicate in-world Exit VR signage; leave the Meta system exit available and the desktop/browser Exit VR button unchanged. Add simple low-poly controller-grip indicators, aura beams and bounded particles.',
      'Provide an optional freeze-and-frame VR photo mode with trigger shutter plus clean, debug + JSON and stereo capture, using the existing screenshot writer and post-XR download fallback.',
      'Keep main scene/project save, Dragon Den, Emberfall, Model Atelier, §C chat, original WebXR session, multiplayer game commands and all 68 preexisting assets. Physical Quest 2 performance/comfort acceptance remains owner tested.'
      ])
    return html[:pos]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\\\/')+html[pos+n:]
