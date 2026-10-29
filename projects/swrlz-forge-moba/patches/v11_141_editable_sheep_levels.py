"""§E v11.141 · separate authored, editable Main Menu / Gameplay levels."""
from pathlib import Path
import json,hashlib
def once(html,old,new):
 n=html.count(old)
 assert n==1,(old[:140],n)
 return html.replace(old,new,1)
def apply(html):
 root=Path(__file__).resolve().parents[1]
 menu=json.loads((root/'scenes/sheep-tag-main-menu-v11-141.swyrl.json').read_text(encoding='utf8'))
 code=(root/'runtime/sheep_editable_levels_v11_141.js').read_text(encoding='utf8')
 css=(root/'runtime/sheep_editable_levels_v11_141.css').read_text(encoding='utf8')
 html=html.replace('</head>','<style id="se141-sheep-editable-levels">'+css+'</style>\n</head>',1)
 # The menu is an ordinary native, editable serialized scene, not an
 # unregistered collection of temporary meshes over the gameplay editor.
 js='const ST141_CANONICAL_MENU='+json.dumps(menu,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+';\n'+code
 html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=')
 # v11.140's native render loop hook is retained, now redirected to
 # st141MenuTick() by the v11.141 runtime. Editor idle is static.
 html=once(html,
 'SWYRL_ENGINE_DEPLOY_MARKER: V11_140_SHEEP_START_MENU_CINEMATIC',
 'SWYRL_ENGINE_DEPLOY_MARKER: V11_141_EDITABLE_MENU_AND_GAME_LEVELS')
 for old,new in [
  ('ENGINE · MAKER v11.140','ENGINE · MAKER v11.141'),
  ('v11.140 · Sheep Tag main menu with 3D attract scene','v11.141 · editable Sheep Tag menu and gameplay levels'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.140'","window.SWRLZ_FORGE_BUILD={version:'v11.141'"),
  ('<title>§wyrl§ Engine · Maker v11.140</title>','<title>§wyrl§ Engine · Maker v11.141</title>')
 ]:html=once(html,old,new)
 key='const SE_RELEASE_NOTES='
 at=html.index(key)+len(key)
 obj,n=json.JSONDecoder().raw_decode(html[at:])
 obj.update(title='Editable Sheep Tag menu level and gameplay level',
  date='2026-10-26',changes=[
   'Architecture correction: opening Sheep Tag starter no longer plays an invisible cinematic inside the editor. Loads a distinct native Main Menu Level with real authored, selectable and movable sheep, wolves, houses, grass and trees; editor animation is OFF until pressing Play.',
   'Editor level bar navigates between separately editable Main Menu and Gameplay scenes, retaining each unsaved level in memory while switching. Export Level downloads the currently edited native .swyrl.json file.',
   'Main Menu UI is editable in Menu UI inspector (eyebrow, title, subtitle, Start Game text, button color and camera orbit duration), saved with the menu-level project metadata and shown as a noninteractive static editor preview.',
   'Playing the menu runs a lightweight looping attract choreography on the EDITABLE scene actors with no match session. Start Game restores authored transforms and switches to the real gameplay level through the existing native Play/preflight.',
   'Stopping the menu restores the editor scene exactly; user edits persist until exported/saved. Existing Sheep Tag mechanics, 68 prior assets, wolf behavior, Rapid, skills, 7-minute gameplay and other §wyrlz Engine projects are preserved.'
  ])
 html=html[:at]+json.dumps(obj,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+n:]
 raw=html.encode('utf8')
 print('SE_V11141_BUILD_MEASURE',len(raw),hashlib.sha256(raw).hexdigest(),flush=True)
 return html
