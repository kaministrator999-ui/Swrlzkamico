"""§E v11.199 — immersive Sheep Tag left-stick movement and wider follow view.
Append one gameplay-only adapter to the verified v11.198 runtime.
"""
from pathlib import Path
import json

def once(s, old, new):
    count=s.count(old)
    if count!=1:
        raise AssertionError(('v11.199 anchor mismatch',old[:140],count))
    return s.replace(old,new,1)

def apply(html):
    root=Path(__file__).resolve().parents[1]
    js=(root/'runtime/engine_xr_sheep_thumbstick_v11_199.js').read_text(encoding='utf8')
    html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=')
    for old,new in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_198_SPATIAL_EDITOR_FLIGHT_GIZMOS',
       'SWYRL_ENGINE_DEPLOY_MARKER: V11_199_SHEEP_VR_THUMBSTICK_FOLLOW'),
      ('ENGINE · MAKER v11.198','ENGINE · MAKER v11.199'),
      ('v11.198 · smooth Quest editor flight, 3D grabbing and gizmos',
       'v11.199 · Sheep Tag left-stick movement and wider VR follow camera'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.198'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.199'"),
      ('<title>§wyrl§ Engine · Maker v11.198</title>',
       '<title>§wyrl§ Engine · Maker v11.199</title>')
    ]:
      html=once(html,old,new)
    key='const SE_RELEASE_NOTES='
    pos=html.index(key)+len(key)
    notes,n=json.JSONDecoder().raw_decode(html[pos:])
    notes.update(title='Sheep Tag VR: left Quest joystick drives sheep, wide snap-and-follow camera',
      date='2026-11-01',changes=[
       'In immersive Sheep Tag Play, left Quest joystick moves the controlled sheep or wolf relative to the strategic camera heading. Forward, backward, strafing and diagonal inputs use native speed, collision and wall-slide logic; releasing the stick stops the continuous move order.',
       'The left joystick no longer detaches or pans the Sheep Tag camera. Entering Play snaps the headset viewing origin once behind and above the controlled unit at 1.4x the previous standard distance, then tracks movement smoothly without overriding natural head rotation.',
       'Right joystick retains orbit and zoom, with a wider default; manual FREE/FOLLOW and Y recenter remain available through native game controls. This changes immersive Sheep Tag only—editor fly controls, desktop/mobile play, LAN guest input, saved maps, physics and Model Atelier are preserved.',
       'Hardware acceptance on Quest 2 remains required; source and JavaScript regression checks do not prove in-headset controller feel.'
      ])
    return html[:pos]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\\\/')+html[pos+n:]
