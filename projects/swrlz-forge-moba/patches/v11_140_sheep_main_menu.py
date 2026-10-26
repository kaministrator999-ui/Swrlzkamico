"""§E v11.140: the Sheep Tag STARTER opens to its own cinematic main menu.

Transient 3D attract objects are never registered into saved actors. Start Game
goes through the native editor Play lifecycle, not a parallel game simulation.
"""
from pathlib import Path
import json,hashlib
def once(html,old,new):
 n=html.count(old)
 assert n==1,(old[:150],n)
 return html.replace(old,new,1)
def apply(html):
 root=Path(__file__).resolve().parents[1]
 css=(root/'runtime/sheep_main_menu_attract_v11_140.css').read_text(encoding='utf8')
 js=(root/'runtime/sheep_main_menu_attract_v11_140.js').read_text(encoding='utf8')
 html=html.replace('</head>','<style id="se140-sheep-main-menu">'+css+'</style>\n</head>',1)
 html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=')
 # Reuse exactly the native render loop: no independent requestAnimationFrame,
 # no additional stUpdate(), wolf AI, navigation or game-clock simulations.
 html=once(html,
  'animeUpdateCinematic(dt);if(stSession){stUpdateCamera(dt);stRefreshHUD();}if(shouldRenderFrame(frameNow))',
  'animeUpdateCinematic(dt);if(stSession){stUpdateCamera(dt);stRefreshHUD();}st140MenuTick(dt);if(shouldRenderFrame(frameNow))')
 html=once(html,
  'SWYRL_ENGINE_DEPLOY_MARKER: V11_139_SAFE_RAPID_CORNER_SNAP',
  'SWYRL_ENGINE_DEPLOY_MARKER: V11_140_SHEEP_START_MENU_CINEMATIC')
 for old,new in [
  ('ENGINE · MAKER v11.139','ENGINE · MAKER v11.140'),
  ('v11.139 · safe rapid house corner snap','v11.140 · Sheep Tag main menu with 3D attract scene'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.139'","window.SWRLZ_FORGE_BUILD={version:'v11.140'"),
  ('<title>§wyrl§ Engine · Maker v11.139</title>','<title>§wyrl§ Engine · Maker v11.140</title>')
 ]:html=once(html,old,new)
 key='const SE_RELEASE_NOTES='
 at=html.index(key)+len(key)
 obj,n=json.JSONDecoder().raw_decode(html[at:])
 obj.update(title='Sheep Tag starter main menu and cinematic 3D attract scene',
  date='2026-10-26',changes=[
   'Opening the Sheep Tag Moonbell Meadow starter shows a real main menu with Sheep Tag title and one large Start Game button. Other §wyrlz Engine starter projects retain their prior editor behavior.',
   'Behind the overlay, the existing THREE scene renders a small scripted 3D sheep-and-wolf chase vignette with houses appearing, fleeing sheep, one temporary tag and a slowly orbiting camera. Uses the existing render clock, no extra loop, expensive bot pathfinding or gameplay session.',
   'The demo scene uses standalone transient Three.js objects, never authored actors; no save/history/undo, team state, economy, timers, capture count or navigation changes. Every temporary mesh, overlay and camera override is removed on Start Game or project switch.',
   'Start Game clicks the existing native Play handler after cleanup; the existing roster/preflight, actual round, sheep HUD, camera follow, 7-minute match, capture and building mechanics remain authoritative. Editor toolbar remains available if a project is edited instead.',
   'Small fixed animation roster keeps mobile GPU/CPU overhead down. All earlier sheep improvements, wolves and original 68 assets are preserved.'
  ])
 html=html[:at]+json.dumps(obj,ensure_ascii=False,separators=(',',':')).replace('</','<\\\\/')+html[at+n:]
 b=html.encode('utf8')
 print('SE_V11140_BUILD_MEASURE',len(b),hashlib.sha256(b).hexdigest(),flush=True)
 return html
