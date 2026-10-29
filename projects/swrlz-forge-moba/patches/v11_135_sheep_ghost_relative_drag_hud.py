"""§E v11.135: sheep-origin hologram with relative meadow drag;
larger Free/Fortified slot swap and persistent Mirror ability button."""
from pathlib import Path
import json,hashlib

def once(s,old,new):
 n=s.count(old)
 assert n==1,(old[:180],n)
 return s.replace(old,new,1)

def apply(html):
 root=Path(__file__).resolve().parents[1]
 css=(root/'runtime/sheep_build_sheep_origin_mirror_hud_v11_135.css').read_text(encoding='utf8')
 js=(root/'runtime/sheep_build_sheep_origin_mirror_hud_v11_135.js').read_text(encoding='utf8')
 html=html.replace('</head>','<style id="se135-sheep-origin-hud">'+css+'</style>\n</head>',1)
 html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=')
 # The legacy camera-follow preview re-rays the skill-button finger at every
 # render update even after the sheep-origin ghost was seeded.
 html=once(html,
  '  if (gesture) {\n    const point=stTouchPlacementGround(gesture.x,gesture.y);',
  '  if (gesture && !st135KeepSheepGhostDuringPointer()) {\n    const point=stTouchPlacementGround(gesture.x,gesture.y);')
 # Native v11.84 placement input remains the only pointer owner; translate
 # meadow finger delta from the sheep rather than absolute ray from the HUD.
 html=once(html,
  'stTouchPlacementContext(event);const point=stTouchPlacementGround(g.x,g.y);if(point)stUiPlacePreview(point);',
  'return st135HandleBuildAim(event);')
 html=once(html,
  'function stBuildInputFinish(reason,keepTool=false){\n const id=stBuildInput.pointer,',
  'function stBuildInputFinish(reason,keepTool=false){\n st135AimState=null;\n const id=stBuildInput.pointer,')
 # A stationary tap on meadow is still allowed to place at the tapped point.
 # A moving gesture uses the validated relative location of the live preview.
 html=once(html,
  "if(!stTouchPlacement.valid){if(source==='skill'){stBuildInputFinish('Tool selected',true);",
  "if(source==='meadow'&&!stBuildInput.moved)st135TapPlacement(event);\n if(!stTouchPlacement.valid){if(source==='skill'){stBuildInputFinish('Tool selected',true);")
 html=once(html,
  'stBuildInput.outcome=null;stUiOrderAt(event.clientX,event.clientY);',
  'stBuildInput.outcome=null;st135CommitPreview();')
 html=once(html,
  'SWYRL_ENGINE_DEPLOY_MARKER: V11_134_RAPID_CANCEL_SHEEP_MARKER_VISIBLE_SKILLS_HOUSE_SWAP',
  'SWYRL_ENGINE_DEPLOY_MARKER: V11_135_SHEEP_ORIGIN_RELATIVE_DRAG_FREE_FORT_MIRROR')
 for old,new in [
  ('ENGINE · MAKER v11.134','ENGINE · MAKER v11.135'),
  ('v11.134 · rapid cancel and reliable build HUD','v11.135 · sheep-origin drag and sheep ability HUD'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.134'","window.SWRLZ_FORGE_BUILD={version:'v11.135'"),
  ('<title>§wyrl§ Engine · Maker v11.134</title>','<title>§wyrl§ Engine · Maker v11.135</title>')
 ]:html=once(html,old,new)
 key='const SE_RELEASE_NOTES='
 at=html.index(key)+len(key)
 obj,n=json.JSONDecoder().raw_decode(html[at:])
 obj.update(title='Sheep-origin ghost with relative drag, bigger Free House and visible Mirror',
  date='2026-10-26',changes=[
   'When a sheep selects a build skill, its real 3D hologram begins on the sheep, never beside the building HUD. The existing camera-follow touch updater can no longer reinterpret a held skill-button coordinate as a new placement while input is active.',
   'The first move onto clear meadow establishes a drag anchor without teleporting the ghost. Subsequent mouse/touch drag offsets the ghost from the sheep position; the placement grid, safety checks and final issued building order share the same validated destination. Single-tap meadow placement remains supported.',
   'Free House is larger and physically swaps positions with Fortified House. Income House stays bottom-right with its original cost, the existing 28-structure limit and all build/collision/resource rules.',
   'Both Mirror decoy and Totem have separate visible/tappable mobile ability slots. Owner-created rules still govern whether skills are enabled; Wolf HUD and Wolf gameplay are untouched.',
   'Earlier Rapid ON/OFF, rotated crossings, under-deck navigation, sheep wireframes and all 68 original packaged assets remain unchanged.'
  ])
 html=html[:at]+json.dumps(obj,ensure_ascii=False,separators=(',',':')).replace('</','<\\\\/')+html[at+n:]
 b=html.encode('utf8')
 print('SE_V11135_BUILD_MEASURE',len(b),hashlib.sha256(b).hexdigest(),flush=True)
 return html
