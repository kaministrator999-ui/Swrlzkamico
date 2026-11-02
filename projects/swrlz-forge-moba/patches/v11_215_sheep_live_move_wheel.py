"""§E v11.215: keep sheep moving while selecting houses/skills in Quest Play.
Append-only, narrow v11.214 overcorrection fix. Preserve camera and ray fixes.
"""
from pathlib import Path
import json

def once(html,old,new):
    count=html.count(old)
    assert count==1,('v11.215 expected source',old[:140],count)
    return html.replace(old,new,1)

def apply(html):
    root=Path(__file__).resolve().parents[1]
    js=(root/'runtime/engine_xr_sheep_live_wheel_v11_215.js').read_text(encoding='utf8')
    html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=')
    for old,new in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_214_SHEEP_QUEST_UPRIGHT_WHEEL_SINGLE_RAY',
       'SWYRL_ENGINE_DEPLOY_MARKER: V11_215_SHEEP_LIVE_MOVE_WHILE_SELECTING'),
      ('ENGINE · MAKER v11.214','ENGINE · MAKER v11.215'),
      ('v11.214 · Sheep Tag Quest modal build wheel camera and ray ownership fix',
       'v11.215 · Sheep Tag Quest keep moving while selecting A/X wheel'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.214'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.215'"),
      ('<title>§wyrl§ Engine · Maker v11.214</title>',
       '<title>§wyrl§ Engine · Maker v11.215</title>')
    ]:html=once(html,old,new)
    key='const SE_RELEASE_NOTES='
    at=html.index(key)+len(key)
    notes,n=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title='Quest Sheep Tag: keep moving while choosing buildings and skills',
      date='2026-11-02',changes=[
        'Correct the v11.214 overcorrection: the Sheep Tag player must be able to move the sheep freely with the LEFT joystick while holding right A to choose a building or left X to choose a skill. Keep running through existing collision-checked paths even while the selector is open.',
        'Keep the Sheep Tag third-person tactical camera following the moving sheep during A/X selection; otherwise the world would freeze and jump back after menu release. Retain v11.214’s upright, head-following radial geometry, which updates every XR frame without inheriting headset roll or pitch.',
        'RIGHT joystick remains exclusively the quick-wheel sector selector while A/X is held. v11.204 already neutralizes that stick for normal orbit/zoom handling; do not change its raw gamepad selection axes.',
        'Opening a quick wheel must not clear an existing VR joystick movement order or reset movement-held state. Restore the original se199StickIntent and se195FollowCamera paths under the already existing v11.214 safe wheel/pointer wrapper, without changing any game authoritative build checks.',
        'Preserve v11.214 duplicate beam/ground guide suppression while choosing, native Meta Quest head-tracking, v11.211 OS Camera focus handling, v11.212/213 hand starter, v11.210 spatial workspace and all 68 source assets. Real Quest 2 comfort remains to be verified.'
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+n:]
