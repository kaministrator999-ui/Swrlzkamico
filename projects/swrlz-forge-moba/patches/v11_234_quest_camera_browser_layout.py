"""§E v11.234 candidate: bounded Sheep Tag XR follow writes, Quest 2D UI fit.

Append-only: consumes the existing 200/202/211/216 camera ownership and
the existing v11.168 Quest Browser detection. This patch is NOT shipped until
the governed manifest is extended and exact built HTML hashes are recalculated.
"""
from pathlib import Path
import json

def once(s, old, new):
    count = s.count(old)
    assert count == 1, ("v11.234 expected one source anchor", old[:100], count)
    return s.replace(old, new, 1)

def apply(html):
    root = Path(__file__).resolve().parents[1]
    js = (root / "runtime/engine_xr_sheep_reference_budget_v11_234.js").read_text(encoding="utf-8")
    css = (root / "runtime/engine_quest_compact_layout_v11_234.css").read_text(encoding="utf-8")
    for dep in ("se200CameraAnchor", "se195MoveRig", "se200.anchorReady",
                "SWYRL_ENGINE_QUEST_OS_STABILITY_211", "SWYRL_ENGINE_DEVICE"):
        assert dep in html, ("v11.234 missing runtime dependency", dep)
    html = once(html, "</head>", '<style id="se234QuestCompactBrowser">\n'+css+'\n</style>\n</head>')
    html = once(html, "window.SWRLZ_FORGE_BUILD=", js + "\nwindow.SWRLZ_FORGE_BUILD=")
    old = " source.engine='§wyrl§ Engine · Maker v11.233';source.version=11.233;"
    new = " source.engine='§wyrl§ Engine · Maker v11.234';source.version=11.234;"
    assert html.count(old) == 2, ("v11.234 source provenance", html.count(old))
    html = html.replace(old, new)
    for before, after in (
        ("SWYRL_ENGINE_DEPLOY_MARKER: V11_233_CHAT_NATIVE_STUDIO_BRIDGE",
         "SWYRL_ENGINE_DEPLOY_MARKER: V11_234_QUEST_CAMERA_BROWSER_LAYOUT"),
        ("ENGINE · MAKER v11.233", "ENGINE · MAKER v11.234"),
        ("v11.233 · Chat Studio Commands v1 reviewed native editing",
         "v11.234 · Quest browser windows and Sheep Tag XR camera write budget"),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.233'",
         "window.SWRLZ_FORGE_BUILD={version:'v11.234'"),
        ("<title>§wyrl§ Engine · Maker v11.233</title>",
         "<title>§wyrl§ Engine · Maker v11.234</title>"),
    ):
        html = once(html, before, after)
    marker = "const SE_RELEASE_NOTES="
    at = html.index(marker) + len(marker)
    notes, width = json.JSONDecoder().raw_decode(html[at:])
    notes.update(title="Quest 2D browser layout fit and smoother Sheep Tag VR follow",
        date="2026-11-02", changes=[
            "Keep the Quest Browser's §E toolbar and Model Atelier tabs horizontally scrollable instead of pinning the studio tab rail above adjacent buttons.",
            "Use a 44px Quest toolbar target within the actual 48px row to prevent clipped controls without changing the phone/PC UI or Meta OS browser-window arrangement.",
            "Bound world-follow XR reference-space writes using a small positional dead zone and a short write interval. Large movements still take the native fast path.",
            "Leave Quest head rotation and physical translation under WebXR; do not use live HMD head movement as a follow-camera correction signal.",
            "Preserve Sheep Tag live left-stick movement, right-stick house selection, build previews, focus-loss guards, multiplayer, fog and the editor.",
            "Expose SWYRL_ENGINE_QUEST_FRAME_BUDGET_234 diagnostics. Quest 2 owner acceptance is needed to establish actual comfort/FPS gain."
        ])
    return html[:at] + json.dumps(notes, ensure_ascii=False, separators=(",",":")).replace("</","<\\/") + html[at+width:]
