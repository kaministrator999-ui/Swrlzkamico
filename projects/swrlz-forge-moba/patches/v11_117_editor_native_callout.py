"""§E v11.117 — scope long-press browser menu suppression to Model Atelier."""
from pathlib import Path
import hashlib,json

CSS=r"""
/* No native touch callout on Model Atelier's viewport, floating tool docks,
   labels and numeric pad. Do not alter touch-action or inspector scrolling. */
#modelAtelierPanel,#modelAtelierPanel *,
#seMobileNumberPad,#seMobileNumberPad *{
 -webkit-touch-callout:none!important;
}
#modelAtelierPanel,
#modelAtelierPanel *:not(input):not(textarea):not(select):not([contenteditable]):not([role="textbox"]),
#seMobileNumberPad,#seMobileNumberPad *{
 -webkit-user-select:none;
 user-select:none;
}
#modelAtelierPanel input,
#modelAtelierPanel textarea,
#modelAtelierPanel [contenteditable],
#modelAtelierPanel [role="textbox"]{
 -webkit-user-select:text;
 user-select:text;
}
"""

def once(src,old,new):
 n=src.count(old)
 assert n==1,(old[:110],n)
 return src.replace(old,new,1)

def apply(html):
 root=Path(__file__).resolve().parent.parent
 runtime=(root/'runtime/model_atelier_callout_guard_v11_117.js').read_text(encoding='utf8')
 html=once(html,'function atelierSculptGhostInstall(){',
    runtime+'\nfunction atelierSculptGhostInstall(){')
 html=once(html,'ModelAtelier.install();',
    'ModelAtelier.install();\nseAtelierCalloutInstall();')
 assert '</head>' in html
 html=html.replace('</head>','<style id="se-v11117-native-callout">'+CSS+'</style>\n</head>',1)
 html=once(html,
    'SWYRL_ENGINE_DEPLOY_MARKER: V11_116_PRECISION_TOUCH_CAMERA_REPAIR',
    'SWYRL_ENGINE_DEPLOY_MARKER: V11_117_EDITOR_NATIVE_CALLOUT_GUARD')
 for old,new in [
    ('ENGINE · MAKER v11.116','ENGINE · MAKER v11.117'),
    ('v11.116 · stable precision touch and camera','v11.117 · no browser hold menu'),
    ("window.SWRLZ_FORGE_BUILD={version:'v11.116'",
     "window.SWRLZ_FORGE_BUILD={version:'v11.117'"),
    ('<title>§wyrl§ Engine · Maker v11.116</title>',
     '<title>§wyrl§ Engine · Maker v11.117</title>')
 ]:html=once(html,old,new)
 key='const SE_RELEASE_NOTES='
 at=html.index(key)+len(key)
 notes,n=json.JSONDecoder().raw_decode(html[at:])
 notes.update(title='Suppress browser long-press menus inside Model Atelier',
 date='2026-10-25',
 changes=[
  'Prevent browser context menus from touch-hold and mouse right-click inside the open Model Atelier.',
  'Include detached in-editor numeric keypad, floating tool docks, buttons and viewport chrome.',
  'Stop accidental long-hold text selection on non-editable surfaces while retaining editable field caret, selection and paste.',
  'Leave outside-editor browser behavior, touch/pointer dragging, two-finger camera controls and tool-panel scrolling untouched.',
  'Preserve every previous modeling capability, saved scene, 148 patches and all 68 bundled assets.'
 ])
 html=html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+n:]
 data=html.encode('utf8')
 print('SWRLZ_V11117_BUILD_MEASURE',len(data),hashlib.sha256(data).hexdigest(),flush=True)
 return html
