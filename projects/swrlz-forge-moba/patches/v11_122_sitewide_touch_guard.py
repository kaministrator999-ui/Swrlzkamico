"""§E v11.122: suppress browser doubletap/longhold on main engine too."""
from pathlib import Path
import hashlib,json
def once(src,old,new):
 n=src.count(old)
 assert n==1,(old[:120],n)
 return src.replace(old,new,1)
def apply(html):
 root=Path(__file__).resolve().parent.parent
 css=(root/'runtime/engine_site_touch_guard_v11_122.css').read_text(encoding='utf8')
 js=(root/'runtime/engine_site_touch_guard_v11_122.js').read_text(encoding='utf8')
 # Site-wide controls are installed at document level, not just while the
 # Model Atelier overlay is active. These are separate from pointer gestures.
 html=html.replace('</head>',
  '<style id="se-v11122-site-touch-guard">'+css+'</style>\n'
  '<script id="se-v11122-site-touch-script">'+js+'</script>\n</head>',1)
 # Historical Atelier guard also intercepted contextmenu on real text inputs.
 # Allow native input selection/paste while leaving normal tool guards intact.
 html=once(html,'if(activeScope(event.target))event.preventDefault();',
  'if(activeScope(event.target)&&!window.seEngineIsEditable(event.target))event.preventDefault();')
 html=once(html,'SWYRL_ENGINE_DEPLOY_MARKER: V11_121_UNCOVERED_MESH_COMPONENT_TOOLBAR',
  'SWYRL_ENGINE_DEPLOY_MARKER: V11_122_SITEWIDE_EDITOR_TOUCH_BOUNDARIES')
 for a,b in [
 ('ENGINE · MAKER v11.121','ENGINE · MAKER v11.122'),
 ('v11.121 · uncovered mesh component tools','v11.122 · full-engine touch guard'),
 ("window.SWRLZ_FORGE_BUILD={version:'v11.121'","window.SWRLZ_FORGE_BUILD={version:'v11.122'"),
 ('<title>§wyrl§ Engine · Maker v11.121</title>','<title>§wyrl§ Engine · Maker v11.122</title>')
 ]:html=once(html,a,b)
 tag='const SE_RELEASE_NOTES=';at=html.index(tag)+len(tag)
 notes,n=json.JSONDecoder().raw_decode(html[at:])
 notes.update(title='Double-tap and long-hold browser guards across the whole engine',
 date='2026-10-25',changes=[
  'Extend double-tap browser page zoom prevention from Model Atelier to the normal §E editor and main page.',
  'Suppress browser text-selection/copy menus on non-editable interface surfaces in every editor workspace.',
  'Keep context menu, caret, selection and paste available inside actual text inputs, textareas and contenteditable fields, including Model Atelier.',
  'Retain native touch-action overrides used by 3D camera/drawing surfaces, one-finger manipulation, pinch zoom, scrolling and normal taps.',
  'Do not change browser settings on unrelated websites or impose global browser maximum-scale limits.'
 ])
 html=html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+n:]
 raw=html.encode('utf8')
 print('SWRLZ_V11122_BUILD_MEASURE',len(raw),hashlib.sha256(raw).hexdigest(),flush=True)
 return html
