"""§E v11.196: anchored Quest radial/camera; shared Sheep Tag fog depth.
Retains the verified v11.195 engine and all authored/editor data.
"""
from pathlib import Path
import json

def once(s,old,new):
    n=s.count(old)
    if n!=1: raise AssertionError(('v11.196 anchor',old[:140],n))
    return s.replace(old,new,1)

def apply(html):
    root=Path(__file__).resolve().parents[1]
    js=(root/'runtime/engine_xr_sheep_stability_v11_196.js').read_text(encoding='utf-8')
    html=once(html,"window.SWRLZ_FORGE_BUILD=",js+"\nwindow.SWRLZ_FORGE_BUILD=")
    for old,new in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_195_QUEST_SHEEP_STABILITY_RADIAL',
       'SWYRL_ENGINE_DEPLOY_MARKER: V11_196_SHEEP_FOG_RADIAL_CAMERA_RECOVERY'),
      ('ENGINE · MAKER v11.195','ENGINE · MAKER v11.196'),
      ('v11.195 · Quest Sheep Tag performance and radial controls',
       'v11.196 · Sheep Tag fog and Quest menu/camera recovery'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.195'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.196'"),
      ('<title>§wyrl§ Engine · Maker v11.195</title>',
       '<title>§wyrl§ Engine · Maker v11.196</title>')
    ]: html=once(html,old,new)
    key='const SE_RELEASE_NOTES='
    pos=html.index(key)+len(key)
    notes,count=json.JSONDecoder().raw_decode(html[pos:])
    notes.update(title="Sheep Tag 2D fog depth and Quest camera/menu recovery",
      date='2026-10-31',changes=[
      'Resolve visible flickering zebra stripes across Sheep Tag terrain and fog in browser and immersive modes by lifting the translucent fog canvas from the meadow plane and applying a stable depth offset; coalesce cosmetic texture redraws while keeping gameplay visibility authoritative.',
      'Replace backwards-facing Quest menu rotation with the correct plane-facing orientation. Anchor the right-hand radial in world space only when opened/page changed, so it cannot fly away or turn into mirrored text as the controller aims.',
      'Prevent simultaneous editor fly controls and Sheep Tag cinematic camera controls in XR. The authored menu camera initializes once at a sheep-centered angle instead of chasing moving sheep; default VR menu remains motionless for comfort.',
      'Snap once to a centered elevated follow viewpoint on entering the gameplay headset rig rather than flying 25 world units across the level; smooth follow, orbit, zoom, free pan and Y follow reset continue afterward.',
      'Add independent diagnostic counters for menu anchors, camera snaps and 2D/VR cosmetic fog work, without touching serialized scenes, other projects or native Quest session exit.'
      ])
    return html[:pos]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\\\/')+html[pos+count:]
