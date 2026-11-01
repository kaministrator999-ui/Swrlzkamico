"""§E v11.203: Quest Sheep Tag neutral forward placement and wrist UI performance.
Append-only layer on verified v11.202; no game rule or native HMD pose edits.
"""
from pathlib import Path
import json

def once(s,old,new):
    count=s.count(old)
    assert count==1,('v11.203 anchor',old[:140],count)
    return s.replace(old,new,1)

def apply(html):
    root=Path(__file__).resolve().parents[1]
    js=(root/'runtime/engine_xr_wrist_forward_placement_v11_203.js').read_text(encoding='utf8')
    # No live building validation while a VR wrist menu is modal or capture
    # mode is active: avoid background GPU/CPU work and accidental ghost drift.
    html=once(html,
       'if(stUi.build&&now-se193.previewAt>100){',
       'if(stUi.build&&!se195.visible&&!se195.photo&&now-se193.previewAt>100){')
    # The preview foundation overlay should never rebuild under a modal menu;
    # navigation/building truth still updates through the normal game loop.
    html=once(html,
       'if(!se200Active()||!stUi.shown||!stSession)return;',
       "if(!se200Active()||!stUi.shown||!stSession||se195.visible||se195.photo)return;")
    html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=')
    for old,new in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_202_QUEST_WIDE_FOLLOW_JOYSTICK_ONLY',
       'SWYRL_ENGINE_DEPLOY_MARKER: V11_203_QUEST_WRIST_MENU_FORWARD_PLACEMENT'),
      ('ENGINE · MAKER v11.202','ENGINE · MAKER v11.203'),
      ('v11.202 · Quest wider high-framed sheep, joystick-only and performance',
       'v11.203 · Quest sheep near-center aiming and cached wrist camera menu'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.202'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.203'"),
      ('<title>§wyrl§ Engine · Maker v11.202</title>',
       '<title>§wyrl§ Engine · Maker v11.203</title>'),
    ]:html=once(html,old,new)
    key='const SE_RELEASE_NOTES='
    at=html.index(key)+len(key)
    notes,n=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title='Quest Sheep Tag: forward-looking sheep and effortless close-range building; lightweight VR camera menu',
      date='2026-11-01',changes=[
       'Lower the Quest Sheep Tag world camera from 26 to 6.5 vertical units per zoom, retaining v11.202 backward distance (21 horizontal plus 2.5 rear bias). At 1.4 zoom the sheep is approximately 9.1 units below and 31.9 ahead (16 degrees down from neutral gaze versus 49). Preserve physical headset pitch, tracking and stabilized anchor-only follow.',
       'In immersive Sheep Tag build mode, aim near the sheep through a forward-facing controller interaction plane. Neutral or slightly down-angled trigger rays now yield nearby real world building sites; aiming higher extends farther and aiming lower brings the ghost nearer. A steep downward pointing ray preserves ordinary physical ground targeting. All sites still go through the same native snapped stCanBuild, house/pen obstruction, route and anti-trap checks.',
       'Cache Quest wrist/radial menu geometry per actual page and reuse text textures at half linear resolution (256x128 vs 512x256) across BUILD/CAPTURE/SESSION/HELP/BACK. No repeated texture upload or mesh construction when returning to an already visited menu page. Dispose all detached pages and cached textures on true XR session exit.',
       'While the modal radial or photo menu is active, skip pointless running construction ghost revalidations and foundation overlay work; hide the optional animated hand sparks/halos. Normal Sheep Tag simulation, multiplayer authority, game clock, fog and actual model rendering remain intact.',
       'Leave desktop/mobile placement rays, native XR editor gizmos, button mapping, click-free Quest joystick locomotion, sheep radius circles, recorded scenes and other tools unchanged. Only a physical Quest 2 test can confirm final headset comfort and FPS.'
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+n:]
