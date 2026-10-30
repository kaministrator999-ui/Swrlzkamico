"""§E v11.174: restore phone canvas fill and separate native editor overlays."""
from pathlib import Path
import json


def once(html, old, new):
    assert html.count(old)==1,(old[:100],html.count(old))
    return html.replace(old,new,1)


def apply(html):
    root=Path(__file__).resolve().parents[1]
    css=(root/'runtime/engine_mobile_editor_viewport_v11_174.css').read_text()
    js=(root/'runtime/engine_mobile_editor_viewport_v11_174.js').read_text()
    assert '</head>' in html
    html=html.replace('</head>','<style id="seMobileEditorViewportV11174">\n'+css+'\n</style>\n</head>',1)
    anchor='installPerformanceSettings();applyPerformanceSettings();se128LaunchStartupProject();'
    html=once(html,anchor,js+'\n'+anchor)
    for old,new in [
        ('SWYRL_ENGINE_DEPLOY_MARKER: V11_173_DIALOG_LAYER_PRIORITY','SWYRL_ENGINE_DEPLOY_MARKER: V11_174_MOBILE_EDITOR_VIEWPORT'),
        ('ENGINE · MAKER v11.173','ENGINE · MAKER v11.174'),
        ('v11.173 · corrected editor dialog stacking','v11.174 · full-height mobile editor and clear controls'),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.173'","window.SWRLZ_FORGE_BUILD={version:'v11.174'"),
        ('<title>§wyrl§ Engine · Maker v11.173</title>','<title>§wyrl§ Engine · Maker v11.174</title>'),
    ]:
        html=once(html,old,new)
    key='const SE_RELEASE_NOTES='
    at=html.index(key)+len(key)
    notes,n=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title='Full-height mobile editor and clear controls',date='2026-10-29',changes=[
        'Normal phone mode now stretches the native 3D canvas through the available editor workspace, without requiring desktop mode.',
        'Mobile inspector and outliner buttons follow the actual level controls; selection information moves away from them.',
        'Desktop keyboard hints and the obsolete template stamp stay out of the phone viewport.',
        'Chat header controls have room below the hosting badge. Shared Google history, project Save/Load and scoped native edits remain available.',
        'Preserve desktop layout, existing native renderer, authored projects, Quest controls and game/LAN behavior.',
    ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+n:]
