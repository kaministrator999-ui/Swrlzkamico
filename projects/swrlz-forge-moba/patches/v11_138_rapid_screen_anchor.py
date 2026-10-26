"""§E v11.138: remember Rapid's last VALID built site as screen coordinates.

Do not confuse world coordinates with display coordinates when sheep move and
the follow camera moves with them. No build orders on ghost-only refresh.
"""
from pathlib import Path
import json,hashlib
def once(src,old,new):
 n=src.count(old)
 assert n==1,(old[:160],n)
 return src.replace(old,new,1)
def apply(html):
 root=Path(__file__).resolve().parents[1]
 js=(root/'runtime/sheep_rapid_screen_anchor_v11_138.js').read_text(encoding='utf8')
 html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=')
 # Capture source FIT before it is destroyed; only successful Rapid actions.
 html=once(html,
  "if(outcome?.ok){const repeat=st132Rapid,kind=stBuildInput.kind;stBuildInputFinish('Building accepted');",
  "if(outcome?.ok){const repeat=st132Rapid,kind=stBuildInput.kind;\n  if(repeat)st138RememberLastScreenPosition();\n  stBuildInputFinish('Building accepted');")
 # After Rapid's native re-select (which creates the sheep-centered new ghost),
 # transplant it to the previous successful build's screen position.
 html=once(html,
  "if(repeat&&stSession&&!stSession.winner){stUiChooseBuild(kind);st126SeedAtSheep();}",
  "if(repeat&&stSession&&!stSession.winner){stUiChooseBuild(kind);st126SeedAtSheep();st138SeedFromScreen();}")
 # A fresh meadow finger may begin ANYWHERE. The preview stays on the
 # remembered screen position instead of teleporting under that finger.
 html=once(html,
  "st135AimState={pointer:id,session:stSession,origin:sheep,\n   x,y,ground,hasMoved:false};",
  "st135AimState={pointer:id,session:stSession,origin:sheep,\n   x,y,ground,hasMoved:false};\n  st138AttachAim(st135AimState);")
 # Rapid gesture is a display-space delta from the remembered projected site.
 # Normal (Rapid OFF / first placement) continues previous sheep-origin logic.
 html=once(html,
  "const target=st136StableAimTarget(anchor,x,y);",
  "const rapidTarget=st138RapidTarget(anchor,x,y);\n const target=rapidTarget===undefined?st136StableAimTarget(anchor,x,y):rapidTarget;")
 html=once(html,
  'SWYRL_ENGINE_DEPLOY_MARKER: V11_137_MEADOW_FIRST_SHEEP_BUILD_DRAG',
  'SWYRL_ENGINE_DEPLOY_MARKER: V11_138_RAPID_LAST_BUILD_SCREEN_ANCHOR')
 for old,new in [
  ('ENGINE · MAKER v11.137','ENGINE · MAKER v11.138'),
  ('v11.137 · full-screen sheep meadow placement','v11.138 · rapid remembers last placement on screen'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.137'","window.SWRLZ_FORGE_BUILD={version:'v11.138'"),
  ('<title>§wyrl§ Engine · Maker v11.137</title>','<title>§wyrl§ Engine · Maker v11.138</title>')
 ]:html=once(html,old,new)
 key='const SE_RELEASE_NOTES='
 at=html.index(key)+len(key)
 obj,n=json.JSONDecoder().raw_decode(html[at:])
 obj.update(title='Rapid Build resumes at the last constructed house\'s screen position',
  date='2026-10-26',changes=[
   'Rapid now remembers normalized SCREEN coordinates projected from the exact last successfully built snapped structure, not its previous world coordinates or the sheep\'s position. The following hologram appears at that same position on the display even when the camera follows a moving sheep.',
   'While idle, the preview reprojects its screen anchor into the current camera world without issuing a building order. Dragging from any new meadow touch shifts the remembered screen position by that finger movement, with the original native safety checks controlling all placements.',
   'Rapid OFF, Stop, changed session/player and first build without a prior successful placement all fall back to sheep-origin behavior; canceled/invalid placements never replace memory. The existing single-tap meadow placement remains available.',
   'No changes to wolves, game balance, assets, capture cleanup, multiplayer, abilities or construction costs.'
  ])
 html=html[:at]+json.dumps(obj,ensure_ascii=False,separators=(',',':')).replace('</','<\\\\/')+html[at+n:]
 raw=html.encode('utf8')
 print('SE_V11138_BUILD_MEASURE',len(raw),hashlib.sha256(raw).hexdigest(),flush=True)
 return html
