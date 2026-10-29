"""§E v11.144: single menu CTA, orbiting actor-following camera cuts."""
from pathlib import Path
import json,hashlib
def once(html,old,new):
 assert html.count(old)==1,(old[:120],html.count(old))
 return html.replace(old,new,1)
def apply(html):
 root=Path(__file__).resolve().parents[1]
 js=(root/'runtime/engine_menu_sheep_camera_v11_144.js').read_text(encoding='utf8')
 html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=')
 html=once(html,
   'SWYRL_ENGINE_DEPLOY_MARKER: V11_143_REAL_VIEWPORT_OVERLAY_HOST',
   'SWYRL_ENGINE_DEPLOY_MARKER: V11_144_SHEEP_PORTRAIT_CAMERA')
 for a,b in [
  ('ENGINE · MAKER v11.143','ENGINE · MAKER v11.144'),
  ('v11.143 · visible editable menus and playable Start Game','v11.144 · one launch control and rotating sheep portraits'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.143'","window.SWRLZ_FORGE_BUILD={version:'v11.144'"),
  ('<title>§wyrl§ Engine · Maker v11.143</title>','<title>§wyrl§ Engine · Maker v11.144</title>')
 ]: html=once(html,a,b)
 key='const SE_RELEASE_NOTES='
 at=html.index(key)+len(key)
 obj,n=json.JSONDecoder().raw_decode(html[at:])
 obj.update(title='Sheep Tag menu camera tours the sheep; remove duplicate editor launcher',
  date='2026-10-26',changes=[
   'Remove the redundant Play Game button from the editable Project Levels strip. Keep native Play/Stop for editor testing and the single large Start Game button on the live menu.',
   'When the menu is playing, rotate the existing camera around individual authored sheep, pausing at each one and smoothly transferring focus after seven seconds instead of staring at a fixed meadow center.',
   'Follow the sheep through the existing chase and gait animation without a second render loop or changing saved scene data. Retain an inert edit-mode preview and exact author transform/camera restoration on Stop.',
   'Keep the independent Gameplay map transition, all level Save/Load/export controls, original game logic and 68 packaged assets.'
  ])
 html=html[:at]+json.dumps(obj,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+n:]
 b=html.encode('utf8')
 print('SE_V11144_BUILD_MEASURE',len(b),hashlib.sha256(b).hexdigest(),flush=True)
 return html
