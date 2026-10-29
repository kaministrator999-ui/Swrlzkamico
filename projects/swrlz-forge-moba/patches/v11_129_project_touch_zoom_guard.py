"""§E v11.129: browser page double-tap zoom prevention at project handoff."""
from pathlib import Path
import hashlib,json

def once(src,old,new):
 n=src.count(old)
 assert n==1,(old[:140],n)
 return src.replace(old,new,1)

def apply(html):
 root=Path(__file__).resolve().parents[1]
 css=(root/'runtime/engine_project_zoom_guard_v11_129.css').read_text(encoding='utf8')
 js=(root/'runtime/engine_project_zoom_guard_v11_129.js').read_text(encoding='utf8')
 html=html.replace('</head>','<style id="se129-project-zoom-guard">'+css+'</style>\n</head>',1)
 html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=')
 html=once(html,
  'SWYRL_ENGINE_DEPLOY_MARKER: V11_128_SINGLE_DEFAULT_STARTER_AND_STABLE_BOOT',
  'SWYRL_ENGINE_DEPLOY_MARKER: V11_129_PROJECT_HANDOFF_PAGE_ZOOM_GUARD')
 for old,new in [
  ('ENGINE · MAKER v11.128','ENGINE · MAKER v11.129'),
  ('v11.128 · organic sheep and default starter','v11.129 · project transition touch protection'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.128'","window.SWRLZ_FORGE_BUILD={version:'v11.129'"),
  ('<title>§wyrl§ Engine · Maker v11.128</title>','<title>§wyrl§ Engine · Maker v11.129</title>')
 ]:html=once(html,old,new)
 tag='const SE_RELEASE_NOTES='
 at=html.index(tag)+len(tag)
 notes,n=json.JSONDecoder().raw_decode(html[at:])
 notes.update(title='Protect project switching from Android browser page double-tap zoom',
  date='2026-10-26',changes=[
   'User repeatedly reproduced browser PAGE zoom (not 3D camera zoom) immediately after selecting a starter project. The known touch-action:manipulation site-wide guard remains active.',
   'Apply browser-native manipulation touch policy explicitly to starter cards, their checkbox wrappers, the Projects menu and editor workflow controls; native pinch and scrolling remain enabled.',
   'On a genuine touchscreen starter-card selection, install a temporary transparent 420ms handoff shield after the native project-opening click. It catches rapid second taps during DOM/scene replacement instead of allowing them to become a browser smart-zoom gesture or unrelated editor input.',
   'Keyboard and mouse project selection, default-starter checkbox changes, text-field selection/paste, page pinch accessibility and 3D viewport touch/camera controls remain unchanged.',
   'All organic Clover sheep, starter defaults, startup restore, native gameplay, editor files and 68 assets are unchanged.'
  ])
 html=html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\\\/')+html[at+n:]
 raw=html.encode('utf8')
 print('SE_V11129_BUILD_MEASURE',len(raw),hashlib.sha256(raw).hexdigest(),flush=True)
 return html
