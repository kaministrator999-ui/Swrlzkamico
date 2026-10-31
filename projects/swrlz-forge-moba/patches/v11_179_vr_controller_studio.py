"""§E v11.179: isolated 2D VR Controller Studio presets and diagnostics."""
from pathlib import Path
import json

def once(source, old, new):
    hits=source.count(old)
    if hits!=1: raise AssertionError((old[:100],hits))
    return source.replace(old,new,1)

def apply(html):
    root=Path(__file__).resolve().parents[1]
    js=(root/'runtime/vr_controller_studio_v11_179.js').read_text(encoding='utf-8')
    css=(root/'runtime/vr_controller_studio_v11_179.css').read_text(encoding='utf-8')
    html=once(html,'</head>','<style id="seVRControllerStudioV11179">\n'+css+'\n</style>\n</head>')
    html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=')
    for before,after in [
        ('SWYRL_ENGINE_DEPLOY_MARKER: V11_178_WORKSPACE_ANALYSIS','SWYRL_ENGINE_DEPLOY_MARKER: V11_179_VR_CONTROLLER_STUDIO'),
        ('ENGINE · MAKER v11.178','ENGINE · MAKER v11.179'),
        ('v11.178 · read-only active workspace analysis','v11.179 · Quest controller profiles and diagnostics'),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.178'","window.SWRLZ_FORGE_BUILD={version:'v11.179'"),
        ('<title>§wyrl§ Engine · Maker v11.178</title>','<title>§wyrl§ Engine · Maker v11.179</title>'),
    ]: html=once(html,before,after)
    key='const SE_RELEASE_NOTES='
    at=html.index(key)+len(key)
    notes,length=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title='VR Controller Studio: safe local profiles and Quest capability diagnostics',
        date='2026-10-31',changes=[
            'Open VR Controls in the editor toolbar to inspect per-mode Kami Precision mappings for Game Editor, Model Editor, Sculpt Workspace, Play and Global.',
            'Customize immutable built-in presets, edit mappings and precision, validate conflicts and reserved headset keys, save locally, import/export safe versioned JSON.',
            'Device diagnostic distinguishes 2D Quest Browser from immersive WebXR capability; no fake controller tracking, native edit dispatch or extra XR render loop.',
            'Future dedicated immersive controller adapters will attach to the native renderer and validated edit transactions; physical Quest 2 acceptance remains pending.'
        ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\\\/')+html[at+length:]
