"""§E v11.148: host-owned lobby and visible guest seating, not multiplayer simulation."""
from pathlib import Path
import hashlib, json

def once(html, old, new):
    assert html.count(old) == 1, (old[:110], html.count(old))
    return html.replace(old, new, 1)

def apply(html):
    root = Path(__file__).resolve().parents[1]
    js = (root / 'runtime/sheep_lan_waiting_room_v11_148.js').read_text(encoding='utf8')
    css = (root / 'runtime/sheep_lan_waiting_room_v11_148.css').read_text(encoding='utf8')
    html = html.replace('</head>', '<style id="se148-lan-waiting-room">' + css + '</style>\n</head>', 1)
    html = once(html, 'window.SWRLZ_FORGE_BUILD=', js + '\nwindow.SWRLZ_FORGE_BUILD=')
    html = once(html, 'SWYRL_ENGINE_DEPLOY_MARKER: V11_147_FULLSCREEN_MENU_VIEWPORT',
                'SWYRL_ENGINE_DEPLOY_MARKER: V11_148_LAN_WAITING_ROOM')
    for old, new in [
        ('ENGINE · MAKER v11.147', 'ENGINE · MAKER v11.148'),
        ('v11.147 · repaired full-screen Sheep Tag menu', 'v11.148 · host-controlled LAN waiting lobby'),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.147'", "window.SWRLZ_FORGE_BUILD={version:'v11.148'"),
        ('<title>§wyrl§ Engine · Maker v11.147</title>', '<title>§wyrl§ Engine · Maker v11.148</title>'),
    ]:
        html = once(html, old, new)
    key = 'const SE_RELEASE_NOTES='
    at = html.index(key) + len(key)
    notes, n = json.JSONDecoder().raw_decode(html[at:])
    notes.update(title='Host-controlled Sheep Tag Local LAN waiting lobby',
                 date='2026-10-27', changes=[
                   'Host Game opens a waiting lobby with eight true server-owned seats; host occupies seat one.',
                   'Join Lobby allocates one bounded guest seat and shows real occupied/open slots and guest names.',
                   'Guest heartbeat and leave are reflected in the host roster; the host can close the lobby.',
                   'Only the local bridge host has room authority; clients on public HTTPS cannot host or scan a private LAN.',
                   'Start Match remains unavailable until synchronized gameplay transport exists. Do not confuse the lobby with a playable network match.',
                   'Original editable Main Menu and Gameplay levels, native 3D scene, 179 historical patches and 68 assets remain.'
                 ])
    html = html[:at] + json.dumps(notes, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/') + html[at+n:]
    raw = html.encode('utf8')
    print('SE_V11148_BUILD_MEASURE', len(raw), hashlib.sha256(raw).hexdigest(), flush=True)
    return html
