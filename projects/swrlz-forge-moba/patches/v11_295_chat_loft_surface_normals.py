"""§E v11.295: outward shading for plain Chat-authored organic lofts.

Append-only successor of sealed v11.294. Historical builders, saved model
descriptors and the existing atlas-loft winding correction remain unchanged.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def once(text, old, new):
    count = text.count(old)
    if count != 1:
        raise AssertionError(("v11.295 anchor", old[:150], count))
    return text.replace(old, new, 1)


def apply(html):
    source = (ROOT / "runtime/chat_loft_surface_normals_v11_295.js").read_text("utf8")
    html = once(html, "/* ATELIER_BRIDGE_START */", source + "\n/* ATELIER_BRIDGE_START */")
    previous = " source.engine='§wyrl§ Engine · Maker v11.294';source.version=11.294;"
    if html.count(previous) != 3:
        raise AssertionError(("v11.295 provenance", html.count(previous)))
    html = html.replace(previous, " source.engine='§wyrl§ Engine · Maker v11.295';source.version=11.295;")
    for old, new in (
        ("SWYRL_ENGINE_DEPLOY_MARKER: V11_294_VANGUARD_SOCKET_LOAD_FIX",
         "SWYRL_ENGINE_DEPLOY_MARKER: V11_295_CHAT_LOFT_SURFACE_NORMALS"),
        ("ENGINE · MAKER v11.294", "ENGINE · MAKER v11.295"),
        ("v11.294 · Hooded Vanguard model loads without inherited sockets",
         "v11.295 · Chat loft surfaces keep their intended colors"),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.294'",
         "window.SWRLZ_FORGE_BUILD={version:'v11.295'"),
        ("<title>§wyrl§ Engine · Maker v11.294</title>",
         "<title>§wyrl§ Engine · Maker v11.295</title>"),
    ):
        html = once(html, old, new)
    token = "const SE_RELEASE_NOTES="
    at = html.index(token) + len(token)
    notes, width = json.JSONDecoder().raw_decode(html[at:])
    notes.update(
        title="Plain Chat lofts use outward surface lighting",
        date="2026-11-06",
        changes=[
            "Fix the inward triangle winding exposed by plain Chat-authored lofts: ivory hair and brown wood retained their saved colors but received inside-face lighting from the cyan backlight.",
            "Reverse triangle winding and recompute surface normals only for plain atelier-chat lofts. Positions, UVs, vertex colors, saved part properties and native history remain unchanged.",
            "Keep the existing textured-loft correction, HD and styled surfaces, organic starter models and historical non-Chat lofts on their original rendering paths.",
            "Preserve the v11.294 Hooded Vanguard socket-loader repair and the v11.293 native Chat geometry tools, receipt-backed progress and single renderer.",
            "Focused geometric regressions verify outward faces and unchanged data; owner Android and Quest visual acceptance remains separate.",
        ],
    )
    return html[:at] + json.dumps(notes, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/") + html[at + width:]
