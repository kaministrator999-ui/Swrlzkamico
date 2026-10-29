"""§E v11.137: tap a building skill, then freely aim from the meadow on touch.

The skill button is not a full-screen virtual joystick. Preserve mouse drag
and all existing placement, rapid/repeat, navigation and ability logic.
"""
from pathlib import Path
import json,hashlib

def once(s,old,new):
 n=s.count(old)
 assert n==1,(old[:150],n)
 return s.replace(old,new,1)

def apply(html):
 # On phones, keeping a captured finger on a bottom-right button and dragging
 # toward the meadow offers an asymmetrical, very short travel range. The
 # button should only select a tool; the next *separate* meadow gesture owns
 # placement, including the real sheep-origin preview and native build checks.
 html=once(html,
  "if(stBuildInput.source==='skill'&&!st133CanAimSkillAt(event.clientX,event.clientY))return; // preview stays at sheep until finger enters open meadow",
  "if(stBuildInput.source==='skill'&&event.pointerType!=='mouse')return; // touch skill selects only; a fresh meadow gesture moves the ghost")
 html=once(html,
  "if(source==='skill'&&!stBuildInput.moved){\n  stBuildInputFinish('Tool selected',true);\n  st126SeedAtSheep();\n  stUiFeedback('House ghost ready at your sheep. Drag onto meadow or touch meadow to place.');return;\n }",
  "if(source==='skill'&&event.pointerType!=='mouse'){\n  stBuildInputFinish('Tool selected',true);\n  st135SeedSheepGhost();\n  stUiFeedback('House selected! Drag anywhere on open meadow; release to build, or tap a target.');return;\n }\n if(source==='skill'&&!stBuildInput.moved){\n  stBuildInputFinish('Tool selected',true);\n  st135SeedSheepGhost();\n  stUiFeedback('House selected! Drag on the meadow; release to build.');return;\n }")
 html=once(html,
  'SWYRL_ENGINE_DEPLOY_MARKER: V11_136_SHEEP_DRAG_CAMERA_CAPTURE_CLEANUP',
  'SWYRL_ENGINE_DEPLOY_MARKER: V11_137_MEADOW_FIRST_SHEEP_BUILD_DRAG')
 for old,new in [
  ('ENGINE · MAKER v11.136','ENGINE · MAKER v11.137'),
  ('v11.136 · camera-stable sheep drag and capture cleanup','v11.137 · full-screen sheep meadow placement'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.136'","window.SWRLZ_FORGE_BUILD={version:'v11.137'"),
  ('<title>§wyrl§ Engine · Maker v11.136</title>','<title>§wyrl§ Engine · Maker v11.137</title>')
 ]:html=once(html,old,new)
 key='const SE_RELEASE_NOTES='
 at=html.index(key)+len(key)
 obj,n=json.JSONDecoder().raw_decode(html[at:])
 obj.update(title='Tap a house, then drag anywhere on the meadow from the sheep',
  date='2026-10-26',changes=[
   'Mobile house/ramp/walkway skill buttons now SELECT the tool instead of requiring a continuous drag beginning in the bottom-right corner. This removes the physical edge-of-screen travel restriction reported on Android.',
   'The hologram remains at the actual sheep after releasing the skill button. A new finger may start from any clear point on the central meadow; movement is anchored at that point and moves the sheep-origin ghost relative to finger travel without jumping. Tapping a meadow destination without dragging remains an alternative placement gesture.',
   'The final meadow release still commits through native construction validation, resource checks and same-target position. One-shot build and Rapid repeat remain unchanged; Rapid still reselects the current tool after a successful build.',
   'Mouse drag on a skill remains supported. All sheep abilities, existing wolf gameplay, pathfinding and previous frame-performance changes are untouched.'
  ])
 html=html[:at]+json.dumps(obj,ensure_ascii=False,separators=(',',':')).replace('</','<\\\\/')+html[at+n:]
 raw=html.encode('utf8')
 print('SE_V11137_BUILD_MEASURE',len(raw),hashlib.sha256(raw).hexdigest(),flush=True)
 return html
