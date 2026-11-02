"""§E v11.214: Quest Sheep Tag Play wheel camera, head-upright HUD and ray ownership.
Append-only after the native floating-hand starter, preserving all editors and LAN.
"""
from pathlib import Path
import json

def once(html,old,new):
    n=html.count(old)
    assert n==1,('v11.214 source anchor',old[:140],n)
    return html.replace(old,new,1)

def apply(html):
    root=Path(__file__).resolve().parents[1]
    js=(root/'runtime/engine_xr_sheep_wheel_modal_camera_ray_v11_214.js').read_text(encoding='utf8')
    html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=')
    for old,new in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_213_HAND_PRIMITIVE_SCHEMA_FIX',
       'SWYRL_ENGINE_DEPLOY_MARKER: V11_214_SHEEP_QUEST_UPRIGHT_WHEEL_SINGLE_RAY'),
      ('ENGINE · MAKER v11.213','ENGINE · MAKER v11.214'),
      ('v11.213 · floating hand model loader validation fix',
       'v11.214 · Sheep Tag Quest modal build wheel camera and ray ownership fix'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.213'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.214'"),
      ('<title>§wyrl§ Engine · Maker v11.213</title>',
       '<title>§wyrl§ Engine · Maker v11.214</title>')
    ]: html=once(html,old,new)
    tag='const SE_RELEASE_NOTES='
    start=html.index(tag)+len(tag)
    notes,n=json.JSONDecoder().raw_decode(html[start:])
    notes.update(title='Quest Sheep Tag: upright camera-safe quick radials with one pointer owner',
      date='2026-11-02',changes=[
       'Sheep Tag Play A-hold building and X-hold ability wheels now update their view-relative position every XR frame instead of remaining at the initial opening world coordinate. The wheel stays in front of the viewer and is kept upright using horizontal headset heading only: physical head roll and pitch never change the radial orientation.',
       'While either thumbstick-select wheel is visible, temporarily suspend Sheep Tag left-stick sheep locomotion and player-camera world-follow reference translations. Cancel only an in-progress VR-stick move order, not authoritative game timers, network activity, enemy simulation, or unrelated editor actions. Resume original controls on release.',
       'Fix multiple overlapping visual beams: the existing v11.203 virtual building ground link cannot reappear behind a modal wheel; hide all old controller beams, ground markers, extra halo and sparks during thumbstick selection. There is no need for a pointer beam to highlight sectors; user selection remains via the existing right thumbstick.',
       'Outside the quick radial, Sheep Tag Play suppresses its redundant secondary decorative controller aura, preserving the intended primary calibrated controller ray or single virtual-ground build guide. Original full VR tools and Game/Model Editors retain their own independently moveable panels and transform gizmos.',
       'Do NOT clamp, disable, recenter or override real Meta Quest headset pose tracking. The game camera is kept stable by pausing app-generated reference-space follow while the selection modal is open; any natural physical headset roll still rotates the real view as required by VR.',
       'Preserve v11.213 verified floating hand loader, v11.211 Meta OS Camera focus recovery, v11.210 spatial panels, v11.204 A/X rapid build and grid, VR multiplayer visibility and original 68 assets. Test on physical Quest 2 for stutter and comfort.'
      ])
    return html[:start]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[start+n:]
