"""§E v11.265 — batch native runtime Sheep Tag houses and expose live nerd stats.

This is one additive runtime overlay. Leave §E editable model parts, authored
houses, sheep rules, world transforms, Quest camera and XR render loop intact.
"""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]

def replace_once(html,old,new):
    assert html.count(old)==1,("v11.265 missing/duplicated source anchor",old[:110],html.count(old))
    return html.replace(old,new,1)

def apply(html):
    script=(ROOT/"runtime/sheep_dense_render_nerd_stats_v11_265.js").read_text(encoding="utf8")
    for symbol in (
        "function stNewBuilding(","function stDisposeVisual(",
        "function se210PanelLines(","function se210PanelPress(",
        "function se210CanvasRender(","function se193XRFrame(",
        "window.SWYRL_ENGINE_QUEST_PERFORMANCE_210",
        "window.SWYRL_ENGINE_QUEST_HEADTURN_239",
    ):
        assert symbol in html,("v11.265 prerequisite",symbol)
    html=replace_once(html,"window.SWRLZ_FORGE_BUILD=",script+"\nwindow.SWRLZ_FORGE_BUILD=")
    old=" source.engine='§wyrl§ Engine · Maker v11.264';source.version=11.264;"
    assert html.count(old)==2,("v11.265 source metadata count",html.count(old))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.265';source.version=11.265;")
    for before,after in (
        ("SWYRL_ENGINE_DEPLOY_MARKER: V11_264_PURPLE_ROOTED_SPECTRAL_ARMS",
         "SWYRL_ENGINE_DEPLOY_MARKER: V11_265_SHEEP_RENDER_NERD_STATS"),
        ("ENGINE · MAKER v11.264","ENGINE · MAKER v11.265"),
        ("v11.264 · purple-rooted spectral galaxy arms",
         "v11.265 · Sheep Tag runtime batching and nerd stats"),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.264'",
         "window.SWRLZ_FORGE_BUILD={version:'v11.265'"),
        ("<title>§wyrl§ Engine · Maker v11.264</title>",
         "<title>§wyrl§ Engine · Maker v11.265</title>"),
    ):
        html=replace_once(html,before,after)
    key="const SE_RELEASE_NOTES="
    at=html.index(key)+len(key)
    notes,chars=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title="Sheep Tag runtime house batching and in-game Nerd Stats",
      date="2026-11-04",changes=[
        "Batch only static leaf meshes of runtime-placed Sheep Tag houses by material, preserving exact vertex positions, UVs, normals, materials, shadows, windmill/flag pivots and gameplay collision. Authored and editable models remain independent.",
        "Preserve original building construction scaling, health flashes, cleanup, sheep AI, fog masks, multiplayer and native Quest controller/camera ownership; use a safe all-or-nothing visual fallback if packing fails.",
        "Add toggleable in-browser Nerd Stats while Sheep Tag plays, and expand the existing grabbable VR Metrics panel into three Nerd Stats pages accessible directly from SESSION.",
        "Display measured renderer draw calls, triangles, texture/geometry objects, active buildings and sheep, estimated saved house draws, callback cadence, headset callback gaps, and fog CPU/texture counters. Callback FPS is not a real GPU timing measurement.",
        "Run a focused source/package smoke check, then validate visible ten-house scene, fog white patches and headset comfort on the owner's Quest 2. No claim that existing depth/compositor artifacts are already fixed."
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(",",":")).replace("</","<\\/")+html[at+chars:]
