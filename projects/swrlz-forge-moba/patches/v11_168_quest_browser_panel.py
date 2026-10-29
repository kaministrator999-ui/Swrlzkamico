"""§E v11.168: Meta Quest Browser 2D editor profile, no WebXR hijack."""
from pathlib import Path
import json

def once(s, old, new):
    assert s.count(old) == 1, (old[:120], s.count(old))
    return s.replace(old, new, 1)

def apply(html):
    root = Path(__file__).resolve().parents[1]
    js = (root/'runtime/engine_quest_panel_v11_168.js').read_text(encoding='utf-8')
    css = (root/'runtime/engine_quest_panel_v11_168.css').read_text(encoding='utf-8')
    assert '</head>' in html, 'Missing HTML head end'
    html = html.replace('</head>', '<style id="seQuestPanelV11168">\n'+css+'\n</style>\n</head>', 1)
    html = once(html, 'window.SWRLZ_FORGE_BUILD=', js+'\nwindow.SWRLZ_FORGE_BUILD=')
    html = once(html, 'SWYRL_ENGINE_DEPLOY_MARKER: V11_167_HOST_DIRECT_MOVE_STRICT_BUILD',
                'SWYRL_ENGINE_DEPLOY_MARKER: V11_168_QUEST_BROWSER_PANEL')
    for a,b in [
       ('ENGINE · MAKER v11.167','ENGINE · MAKER v11.168'),
       ('v11.167 · real host sheep movement and legal build previews',
        'v11.168 · Quest Browser comfort and device profiling'),
       ("window.SWRLZ_FORGE_BUILD={version:'v11.167'",
        "window.SWRLZ_FORGE_BUILD={version:'v11.168'"),
       ('<title>§wyrl§ Engine · Maker v11.167</title>',
        '<title>§wyrl§ Engine · Maker v11.168</title>')
    ]:
        html=once(html,a,b)
    key='const SE_RELEASE_NOTES='
    at=html.index(key)+len(key)
    notes,n=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title='Quest 2 Browser editor comfort and detected device profile',
      date='2026-10-28',changes=[
       'Detect the Meta Quest Browser family for 2D panel presentation; use touch and viewport features to distinguish non-Quest phone/tablet from desktop, not user-agent strings for XR capabilities.',
       'Quest Browser defaults to optional oversized controls and focused/high-contrast selection across native toolbar and Model Atelier quick tools, preserving ordinary phone/PC layouts.',
       'Top toolbar Quest UI toggle allows manual activation on other devices and opt-out on headset, with saved local preference.',
       'Expose SWYRL_ENGINE_DEVICE.read() for detected profile, last observed pointerType, resizable viewport and actual immersive-vr API support; never request an XR session without explicit user action.',
       'Preserve established native Three.js renderer, camera navigation, modelling, Sheep Tag controller and multiplayer flows. This is a browser-window UI release, not a claim of tracked immersive VR controller support.',
       'Physical Meta Quest 2 Browser acceptance and precision ray/drag behavior remain to be checked on-device.'
      ])
    html=html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+n:]
    return html