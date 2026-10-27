"""§E v11.147: owner Android collapsed Main Menu viewport repair."""
from pathlib import Path
import hashlib,json
def once(html,old,new):
 assert html.count(old)==1,(old[:90],html.count(old))
 return html.replace(old,new,1)
def apply(html):
 root=Path(__file__).resolve().parents[1]
 css=(root/'runtime/engine_runtime_fullscreen_v11_147.css').read_text(encoding='utf8')
 js=(root/'runtime/engine_runtime_fullscreen_v11_147.js').read_text(encoding='utf8')
 html=html.replace('</head>','<style id="se147-runtime-viewport">'+css+'</style>\n</head>',1)
 html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=')
 html=once(html,'SWYRL_ENGINE_DEPLOY_MARKER: V11_146_LOCAL_LAN_BROWSER',
  'SWYRL_ENGINE_DEPLOY_MARKER: V11_147_FULLSCREEN_MENU_VIEWPORT')
 for old,new in [
  ('ENGINE · MAKER v11.146','ENGINE · MAKER v11.147'),
  ('v11.146 · local LAN directory and host menu','v11.147 · repaired full-screen Sheep Tag menu'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.146'","window.SWRLZ_FORGE_BUILD={version:'v11.147'"),
  ('<title>§wyrl§ Engine · Maker v11.146</title>','<title>§wyrl§ Engine · Maker v11.147</title>')
 ]:html=once(html,old,new)
 key='const SE_RELEASE_NOTES='
 at=html.index(key)+len(key)
 obj,n=json.JSONDecoder().raw_decode(html[at:])
 obj.update(title='Sheep Tag full-screen menu and LAN viewport restoration',
  date='2026-10-27',changes=[
   'Android v11.146 screenshot revealed the Play camera/Start Game squeezed into a thin editor strip with black screen and Exit to editor overlapping the title. This version repairs that scoped immersive viewport, not game content.',
   'On native Main Menu or Gameplay Play only, mount the existing canvas in a fixed full-screen runtime wrapper. Let the existing WebGL resize handler remeasure the drawing buffer and existing v11.143 canvas-bound overlay remeasure its actual box.',
   'Keep the main menu and LAN browser centered with vertical scrolling on short devices, and anchor Exit to editor at the bottom rather than over Start Game.',
   'Stop removes the Play-only layout and restores normal editable scene, level controls and save/export flows. No changes to LAN scanning, lobby semantics, actors, wolves, house placement, animation or the 68 packaged assets.'
  ])
 html=html[:at]+json.dumps(obj,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+n:]
 b=html.encode('utf8')
 print('SE_V11147_BUILD_MEASURE',len(b),hashlib.sha256(b).hexdigest(),flush=True)
 return html
