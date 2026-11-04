"""§E v11.267 — expose existing local LAN/WebRTC multiplayer in Quest VR menu.

Presentation only: add controller-selectable VR radial actions, optional world
pinned read-only lobby board, and reuse native LAN lobby and match-start APIs.
No new renderer, extra simulation clock, subnet scanning, or fake player seats.
"""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def once(src,old,new):
    assert src.count(old)==1,("v11.267 missing source anchor",old[:115],src.count(old))
    return src.replace(old,new,1)

def apply(html):
    source=(ROOT/"runtime/sheep_vr_lan_menu_v11_267.js").read_text("utf8")
    for term in (
        "function se195Options(","function se195HandleAction(",
        "function se195MakeRadial(","function se193XRFrame(",
        "function se146Open(","function se146Scan(",
        "function se148LeaveRoom(","function se151JoinGame(",
        "function se150HostStart(","function se159Start(",
        "window.SWYRL_ENGINE_SHEEP_NERD_STATS_265",
        "window.SWYRL_ENGINE_QUEST_PERFORMANCE_210",
    ):
        assert term in html,("v11.267 LAN prerequisite",term)
    html=once(html,"window.SWRLZ_FORGE_BUILD=",
              source+"\nwindow.SWRLZ_FORGE_BUILD=")
    old=" source.engine='§wyrl§ Engine · Maker v11.266';source.version=11.266;"
    assert html.count(old)==2,("v11.267 source version count",html.count(old))
    html=html.replace(old,
       " source.engine='§wyrl§ Engine · Maker v11.267';source.version=11.267;")
    for before,after in (
        ("SWYRL_ENGINE_DEPLOY_MARKER: V11_266_SHADER_ARRAY_BOOT_FIX",
         "SWYRL_ENGINE_DEPLOY_MARKER: V11_267_QUEST_LAN_MAIN_MENU"),
        ("ENGINE · MAKER v11.266","ENGINE · MAKER v11.267"),
        ("v11.266 · galaxy mist JS syntax and editor boot fix",
         "v11.267 · Quest Sheep Tag multiplayer LAN menu"),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.266'",
         "window.SWRLZ_FORGE_BUILD={version:'v11.267'"),
        ("<title>§wyrl§ Engine · Maker v11.266</title>",
         "<title>§wyrl§ Engine · Maker v11.267</title>"),
    ):html=once(html,before,after)
    key="const SE_RELEASE_NOTES="
    at=html.index(key)+len(key)
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title="Sheep Tag VR main menu: Local LAN multiplayer",
      date="2026-11-04",changes=[
        "Show LOCAL LAN directly on the Quest 2 immersive Sheep Tag main radial, with native HOST, FIND ROOMS, JOIN CODE, COPY INVITE, START MATCH, LEAVE and BACK controls; use the existing browser LAN/WebRTC owner and do not add a second network stack.",
        "Display a world-pinned readable lobby board with connected-player count, actual host invite, discovered live rooms and error/connection feedback. It is placed once in world space rather than constantly chasing the headset.",
        "Connect only to actual discovered peers or verified one-code PeerJS invitations. Public HTTPS discovery groups by shared internet egress, not a private subnet scan. Exact invite can be read/copied, or pasted from Quest clipboard when browser permissions permit.",
        "Preserve the existing host-authoritative shared world, sheep guest assignment, builds, fog, native headset/controller tracking and studio tooling. Match START is enabled only through the existing host flow with a connected guest.",
        "Preserve v11.266 startup syntax repair and v11.265 runtime house batching/Nerd Stats; acceptance requires actual Quest 2 Host/Join/Start tests with a second device."
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(",",":")).replace("</","<\\/")+html[at+width:]
