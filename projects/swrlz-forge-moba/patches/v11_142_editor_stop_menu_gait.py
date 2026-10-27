"""§E v11.142: repair editor Stop, menu UI playback and visible gait pivots."""
from pathlib import Path
import json,hashlib
def once(s,old,new):
 n=s.count(old)
 assert n==1,(old[:150],n)
 return s.replace(old,new,1)
def apply(html):
 root=Path(__file__).resolve().parents[1]
 js=(root/'runtime/engine_playback_menu_gait_v11_142.js').read_text(encoding='utf-8')
 css=(root/'runtime/engine_playback_menu_gait_v11_142.css').read_text(encoding='utf-8')
 html=html.replace('</head>','<style id="se142-playback-menu-gait">'+css+'</style>\n</head>',1)
 html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=')
 html=once(html,
  'SWYRL_ENGINE_DEPLOY_MARKER: V11_141_EDITABLE_MENU_AND_GAME_LEVELS',
  'SWYRL_ENGINE_DEPLOY_MARKER: V11_142_EDITOR_STOP_MENU_AND_CHARACTER_GAIT')
 for old,new in [
  ('ENGINE · MAKER v11.141','ENGINE · MAKER v11.142'),
  ('v11.141 · editable Sheep Tag menu and gameplay levels','v11.142 · reliable menu playback and animated sheep/wolves'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.141'","window.SWRLZ_FORGE_BUILD={version:'v11.142'"),
  ('<title>§wyrl§ Engine · Maker v11.141</title>','<title>§wyrl§ Engine · Maker v11.142</title>')
 ]:html=once(html,old,new)
 key='const SE_RELEASE_NOTES='
 at=html.index(key)+len(key)
 obj,n=json.JSONDecoder().raw_decode(html[at:])
 obj.update(title='Restore Stop, Start Game UI and sheep/wolf gait in menu Play',
  date='2026-10-26',changes=[
   'Move the Project Levels controls from the native Play/Pause/Stop top toolbar to a small independent editor viewport strip so Stop stays adjacent to playback controls, including on Android portrait screens. Restore native Stop visibility during menu Play and display an inert Stop button in Edit mode.',
   'Harden per-level project identity after native scene loads; menu Play opens the visible Start Game overlay instead of silently falling through to Sheep Tag gameplay. Add an explicit Play Game control to launch the project through its menu even when editing another level.',
   'Animate the original authored stLeg, stHead, stTail joints on moving menu sheep and wolves using world travel distances, with phased diagonal gaits and head/tail reactions. All joint rotations and scene transforms are restored exactly on Stop or Start Game; editor view remains motionless.',
   'Preserve general multi-level project editing/new map/links/save, existing gameplay locomotion and all sheep/wolf mechanics, 68 original assets, and authored level content.'
  ])
 html=html[:at]+json.dumps(obj,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+n:]
 b=html.encode('utf8')
 print('SE_V11142_BUILD_MEASURE',len(b),hashlib.sha256(b).hexdigest(),flush=True)
 return html
