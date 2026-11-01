"""§E v11.200 — stabilized Quest sheep spotlight with direct joystick movement.
Add after the verified v11.199 adapter. Keep entire prior source lineage.
"""
from pathlib import Path
import json

def once(s, old, new):
    count=s.count(old)
    if count!=1:raise AssertionError(('v11.200 source anchor',old[:160],count))
    return s.replace(old,new,1)

def apply(html):
    root=Path(__file__).resolve().parents[1]
    script=(root/'runtime/engine_xr_sheep_spotlight_v11_200.js').read_text(encoding='utf8')
    html=once(html,'window.SWRLZ_FORGE_BUILD=',script+'\nwindow.SWRLZ_FORGE_BUILD=')
    for old,new in [
        ('SWYRL_ENGINE_DEPLOY_MARKER: V11_199_SHEEP_VR_THUMBSTICK_FOLLOW',
         'SWYRL_ENGINE_DEPLOY_MARKER: V11_200_SHEEP_VR_STABILIZED_SPOTLIGHT'),
        ('ENGINE · MAKER v11.199','ENGINE · MAKER v11.200'),
        ('v11.199 · Sheep Tag left-stick movement and wider VR follow camera',
         'v11.200 · Sheep Tag stabilized overhead camera and direct movement'),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.199'",
         "window.SWRLZ_FORGE_BUILD={version:'v11.200'"),
        ('<title>§wyrl§ Engine · Maker v11.199</title>',
         '<title>§wyrl§ Engine · Maker v11.200</title>'),
    ]:html=once(html,old,new)
    key='const SE_RELEASE_NOTES='
    pos=html.index(key)+len(key)
    notes,n=json.JSONDecoder().raw_decode(html[pos:])
    notes.update(title='Sheep Tag VR: centered overhead sheep tracking without camera rocking',
      date='2026-11-01',changes=[
        'Keep the live sheep directly beneath the centered virtual spotlight camera with zero sideways offset: steeper top-down framing, 14 world units back and 26 above at base zoom, retaining Quest headset rotational tracking.',
        'Remove the headset-eye position correction loop responsible for camera instability. Snap once to the controlled sheep when entering gameplay or recentering, and subsequently move the XR reference origin only by the smoothed *gameplay camera-anchor delta*. Physical head movement no longer triggers reference-space writes.',
        'Make left-stick sheep and wolf movement use short native swept collision checks with houses, walls and field boundaries instead of updating an A* move destination at every game frame. Retain sliding, analog motion, animation, capture/rescue and gameplay authority.',
        'Right stick remains orbit and zoom. Keep photo mode, radial menu, previous fog and visual fixes, existing editor 6DoF controls, non-VR mobile and LAN systems unchanged. Hardware comfort and VR performance need physical Quest 2 verification.'
      ])
    return html[:pos]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\\\/')+html[pos+n:]
