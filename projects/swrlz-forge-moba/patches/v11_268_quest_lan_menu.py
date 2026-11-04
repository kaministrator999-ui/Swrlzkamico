"""§E v11.268 — enable Sheep Tag's existing LAN lobby in immersive Quest menu."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
def once(src,old,new):
    assert src.count(old)==1,("v11.268 source anchor",old[:100],src.count(old))
    return src.replace(old,new,1)

def apply(html):
    runtime=(ROOT/"runtime/sheep_vr_lan_menu_v11_268.js").read_text("utf8")
    for marker in (
        "function se195Options(","function se195HandleAction(",
        "function se195MakeRadial(","function se193XRFrame(",
        "function se146Open(","function se146Scan(",
        "function se148LeaveRoom(","function se151JoinGame(",
        "function se150HostStart(","function se159Start(",
        "window.SWYRL_ENGINE_SHEEP_NERD_STATS_265",
        "window.SWYRL_ENGINE_QUEST_PERFORMANCE_210",
        "function makeNebulaMist(",
    ):
        assert marker in html,("v11.268 prior runtime",marker)
    html=once(html,"window.SWRLZ_FORGE_BUILD=",runtime+"\nwindow.SWRLZ_FORGE_BUILD=")
    old=" source.engine='§wyrl§ Engine · Maker v11.267';source.version=11.267;"
    assert html.count(old)==2,("v11.268 metadata count",html.count(old))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.268';source.version=11.268;")
    for a,b in (
        ("SWYRL_ENGINE_DEPLOY_MARKER: V11_267_CONTINUOUS_GALAXY_WISPS",
         "SWYRL_ENGINE_DEPLOY_MARKER: V11_268_QUEST_LAN_MAIN_MENU"),
        ("ENGINE · MAKER v11.267","ENGINE · MAKER v11.268"),
        ("v11.267 · continuous flowing nebula wisps",
         "v11.268 · Quest Sheep Tag multiplayer LAN menu"),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.267'",
         "window.SWRLZ_FORGE_BUILD={version:'v11.268'"),
        ("<title>§wyrl§ Engine · Maker v11.267</title>",
         "<title>§wyrl§ Engine · Maker v11.268</title>"),
    ):html=once(html,a,b)
    key="const SE_RELEASE_NOTES="
    at=html.index(key)+len(key)
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title="Sheep Tag VR main menu: Local LAN multiplayer",
      date="2026-11-04",changes=[
       "Add LOCAL LAN to Sheep Tag's immersive Quest radial main menu, leading to HOST, FIND ROOMS, JOIN CODE, COPY INVITE, START MATCH, LEAVE and BACK controls, without exiting VR.",
       "Re-use the existing Local LAN bridge and HTTPS WebRTC/PeerJS live-lobby directory, real host and join sessions, authenticated peer seat assignments and host-authoritative match-start flow. No speculative/private subnet scan, fabricated host or duplicate networking stack.",
       "Use controller pointing for VR menu actions and a one-time world-pinned readable multiplayer status and invite board, not a head-chasing overlay; the room list refreshes when genuine directory entries change.",
       "Enable joining discovered rooms and pasting a copied invite from Quest's browser clipboard when permitted; display an explicit fallback when clipboard permissions are unavailable. Native 2D multiplayer menus remain intact.",
       "Preserve v11.267 continuous galaxy wisps, v11.266 startup syntax repair, v11.265 Sheep Tag render batching and Nerd Stats, camera, model editor, saved projects, single renderer and XR control bindings. Real Quest 2 two-device verification is still needed."
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(",",":")).replace("</","<\\/")+html[at+width:]
