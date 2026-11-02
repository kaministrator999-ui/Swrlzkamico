"""§E v11.211 Quest OS camera/menu focus-loss stability. Append-only."""
from pathlib import Path
import json

def once(s,old,new):
    n=s.count(old)
    assert n==1,('v11.211 exact source anchor',old[:110],n)
    return s.replace(old,new,1)

def apply(html):
    root=Path(__file__).resolve().parents[1]
    js=(root/'runtime/engine_xr_meta_os_overlay_stability_v11_211.js').read_text(encoding='utf8')
    html=once(html,"const maxStep=timeStep*13;",
        "const maxStep=timeStep*(se211CameraSoftReturn()?3.2:13);")
    html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=')
    for old,new in [
        ('SWYRL_ENGINE_DEPLOY_MARKER: V11_210_QUEST_COMPREHENSIVE_POLISH',
         'SWYRL_ENGINE_DEPLOY_MARKER: V11_211_QUEST_OS_CAMERA_OVERLAY_STABILITY'),
        ('ENGINE · MAKER v11.210','ENGINE · MAKER v11.211'),
        ('v11.210 · Sheep Tag Quest world, workspace, controls, FPS and skill polish',
         'v11.211 · Quest OS Camera menu overlay and XR tracking stability'),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.210'",
         "window.SWRLZ_FORGE_BUILD={version:'v11.211'"),
        ('<title>§wyrl§ Engine · Maker v11.210</title>',
         '<title>§wyrl§ Engine · Maker v11.211</title>'),
    ]: html=once(html,old,new)
    tag='const SE_RELEASE_NOTES='
    at=html.index(tag)+len(tag)
    notes,n=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title='Quest OS Camera overlay: smooth WebXR focus loss and stable headset return',
      date='2026-11-01',changes=[
        'Quest OS Camera/menu WebXR visible-blurred and hidden now suspend only app-owned XR UI/controller/camera adapters and decorative scene elements; the native HMD tracking and authoritative Sheep Tag simulation/rendering remain intact.',
        'A WebXR visibilitychange listener catches focus changes even if hidden sessions stop XR callbacks. Foreground restoration resets stale frame-time baselines without resetting the native headset reference space, camera heading or gameplay focus.',
        'Gaps above 170ms in XR callbacks trigger short camera/input stabilization even if the browser fails to send visible-blurred. App XR controller actions require a fresh release to avoid accidental houses/abilities/menu grabs after Meta system UI returns.',
        'Block reference-space camera writes while the system overlay or recovery is active, then temporarily cap post-overlay sheep-follow correction speed from 13 to 3.2 world units per second; keep native HMD rotation untouched.',
        'Temporarily hide optional app-only decorations/HUD panels while foreground OS menus are active and restore each prior visibility on return; do not alter fog visibility, LAN game authority, colliders, renderer resolution, or saved projects.',
        'Quest OS focus, XR callback gap size, skipped controller/radial frames, blocked camera reference writes and time recovering are now reported via SWYRL_ENGINE_QUEST_OS_STABILITY_211. Physical Quest 2 tests still needed to confirm the symptom improves.'
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+n:]
