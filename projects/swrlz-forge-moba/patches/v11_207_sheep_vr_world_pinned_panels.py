"""§E v11.207 · World-space Quest Sheep Tag PLAY panel manipulation.
Controller grip moves/tilts game UI only; no changes to authored scene tools.
"""
from pathlib import Path
import json
def once(s,old,new):
 count=s.count(old)
 assert count==1,('v11.207 patch anchor',old[:120],count)
 return s.replace(old,new,1)
def apply(html):
 root=Path(__file__).resolve().parents[1]
 js=(root/'runtime/engine_xr_sheep_world_pinned_panels_v11_207.js').read_text(encoding='utf8')
 html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=')
 for old,new in [
  ('SWYRL_ENGINE_DEPLOY_MARKER: V11_206_SHEEP_QUEST_MEADOW_FOG_ART',
   'SWYRL_ENGINE_DEPLOY_MARKER: V11_207_SHEEP_QUEST_SPATIAL_MENU'),
  ('ENGINE · MAKER v11.206','ENGINE · MAKER v11.207'),
  ('v11.206 · Sheep Tag Quest meadow dressing and fog art',
   'v11.207 · Sheep Tag Quest grip-to-move world-pinned tools'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.206'",
   "window.SWRLZ_FORGE_BUILD={version:'v11.207'"),
  ('<title>§wyrl§ Engine · Maker v11.206</title>',
   '<title>§wyrl§ Engine · Maker v11.207</title>'),
 ]:html=once(html,old,new)
 key='const SE_RELEASE_NOTES=';at=html.index(key)+len(key)
 notes,n=json.JSONDecoder().raw_decode(html[at:])
 notes.update(title='Sheep Tag Quest: grab, tilt, pin and resize native VR tool menu',
  date='2026-11-01',changes=[
   'In immersive Sheep Tag Play, point the right controller at the actual §E wrist radial and hold its GRIP button to grab it. Translate and rotate/tilt the physical controller to move the §E menu in 3D; release GRIP to leave that panel anchored in the world. Native HMD pose is never altered.',
   'While gripping, right thumbstick up/down can resize the held menu; ordinary right-stick game orbit/zoom is suppressed only during the grab. B still opens the full tools menu. The modal UI keeps ray target priority over the game world.',
   'The full game wrist menu SESSION page gains a LAYOUT submenu: PIN, RECENTER, SMALLER, LARGER and BACK. Recenter restores the existing safe front-of-head placement and default size; PIN keeps the current location. The page pose and scale persist across in-session menu page changes and reopening.',
   'A small cached GRIP TO MOVE handle label and a subtle fixed grab outline appear on the radial; no per-frame text uploads or new animation loop. Grip transform math reuses Vector3/Quaternion objects. All graphics are already owned by the menu root and disposed with the XR menu lifecycle.',
   'This affects only app-owned Sheep Tag PLAY radial menus. Meta Quest native settings windows are OS controlled. The §E editor/model editor VR object rotation/grip controls, gameplay house orientation, collision, LAN and skills remain unchanged.',
   'World-pinned anchors are intentionally reset on new WebXR sessions because Quest tracking reference-space coordinates may shift. Persistent multi-window layouts and independently pinned inspector/camera panels are future enhancements.'
  ])
 return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+n:]
