"""Improve recorded Maul spectator quality and add native lossless gzip handoff.

This is append-only: all earlier release patches and runtime sources stay immutable.
"""
from pathlib import Path


def once(html, old, new):
    assert html.count(old) == 1, "Ambiguous recorder quality anchor: " + old[:100]
    return html.replace(old, new, 1)


def apply(html):
    root = Path(__file__).resolve().parent.parent
    modules = "\n".join((root / "runtime" / name).read_text(encoding="utf-8")
                        for name in ("run_maul_spectator.js", "run_recording_compression.js"))
    html = once(html, "window.SWRLZ_FORGE_BUILD=",
                modules + "\nwindow.SWRLZ_FORGE_BUILD=")
    old_extent = "const extent=Number(run.rules?.bounds||run.map?.project?.sheepTag?.bounds||run.project?.sheepTag?.bounds||40);"
    html = once(html, old_extent,
                "const extent=run.mode==='maul'?54:Number(run.rules?.bounds||run.map?.project?.sheepTag?.bounds||run.project?.sheepTag?.bounds||40);")
    old_loop = "const ordered=entities.filter(e=>e.active!==false&&!e.removed&&!e.destroyed)"
    html = once(html, old_loop,
                "if(run.mode==='maul'){stRunDrawMaul(ctx,entities,p=>project(p,width,height,centre),width,height,get('stRunObserver').value,state.game);return;}\n"
                "    " + old_loop)
    html = once(html,
                "stRunDownloadBlob(new Blob([html],{type:'text/html;charset=utf-8'}),name+'html');",
                "const spectatorHtml=run.mode==='maul'?html.replace('<script>window.SWYRL_RUN_VIEWER=',"
                "'<script>'+stRunDrawMaul.toString()+';window.SWYRL_RUN_VIEWER='):html;\n"
                "    stRunDownloadBlob(new Blob([spectatorHtml],{type:'text/html;charset=utf-8'}),name+'html');")
    html = once(html, "stRunInstallUI();",
                "stRunInstallUI();stRunInstallCompressedUI();")
    html = once(html, "V10_9_EPISODE_STORY_ACTIONS", "V11_0_RUN_REPLAY_QUALITY")
    html = html.replace("Maker v10.9", "Maker v11.0").replace("MAKER v10.9", "MAKER v11.0")
    html = html.replace("version:'v10.9'", "version:'v11.0'").replace("version:10.9", "version:11.0")
    html = html.replace("§E v10.9 Tools", "§E v11.0 Tools")
    html = html.replace("v10.9 · STORY ACTIONS · PAPER THEATRE",
                        "v11.0 · LOSSLESS RUN EXPORT · MAUL SPECTATOR")
    html = html.replace("§wyrl§ Engine v10.9 · Animated story actions",
                        "§wyrl§ Engine v11.0 · Recorder and Maul spectator improvements")
    return html
