"""§E v11.143 · real canvas host correction for editable levels and Start Game."""
from pathlib import Path
import json,hashlib
def once(s,a,b):
 assert s.count(a)==1,(a[:160],s.count(a))
 return s.replace(a,b,1)
def apply(html):
 root=Path(__file__).resolve().parents[1]
 js=(root/'runtime/engine_canvas_overlay_host_v11_143.js').read_text(encoding='utf8')
 css=(root/'runtime/engine_canvas_overlay_host_v11_143.css').read_text(encoding='utf8')
 html=html.replace('</head>','<style id="se143-canvas-overlay-host">'+css+'</style>\n</head>',1)
 html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=')
 html=once(html,
 'SWYRL_ENGINE_DEPLOY_MARKER: V11_142_EDITOR_STOP_MENU_AND_CHARACTER_GAIT',
 'SWYRL_ENGINE_DEPLOY_MARKER: V11_143_REAL_VIEWPORT_OVERLAY_HOST')
 for old,new in [
  ('ENGINE · MAKER v11.142','ENGINE · MAKER v11.143'),
  ('v11.142 · reliable menu playback and animated sheep/wolves','v11.143 · visible editable menus and playable Start Game'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.142'","window.SWRLZ_FORGE_BUILD={version:'v11.143'"),
  ('<title>§wyrl§ Engine · Maker v11.142</title>','<title>§wyrl§ Engine · Maker v11.143</title>')
 ]:html=once(html,old,new)
 key='const SE_RELEASE_NOTES='
 at=html.index(key)+len(key)
 obj,n=json.JSONDecoder().raw_decode(html[at:])
 obj.update(title='Fix hidden Sheep Tag Start Game menu on actual mobile browsers',
  date='2026-10-26',changes=[
   'Root cause confirmed in real Chrome mobile: the native #viewport element is a CANVAS. Earlier versions appended HTML menu and Project Levels controls directly INSIDE that canvas; browsers treat those as fallback markup and give them zero-sized invisible boxes even while menu Play is running.',
   'Mount the authored menu runtime overlay, static editable menu preview and Project Levels/New Map controls as normal HTML siblings of the canvas in its real viewport wrapper; preserve native scene, menu camera, real animal gait and independent level data.',
   'Keep the responsive Start Game button tappable and visibly layered over the animated 3D background. Retain existing native Stop, Start Game transition to gameplay and no animation in edit mode.',
   'Add true headless mobile touch-and-layout regression: verify menu geometry and a successful human-style Start Game tap, not simply the existence of DOM nodes or programmatic click.'
  ])
 html=html[:at]+json.dumps(obj,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+n:]
 b=html.encode('utf8')
 print('SE_V11143_BUILD_MEASURE',len(b),hashlib.sha256(b).hexdigest(),flush=True)
 return html
