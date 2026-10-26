"""§E v11.132: meadow drag handoff, rapid build, safe recovery, rotated
permanent crossings and sheep wireframe occlusion visibility."""
from pathlib import Path
import json,hashlib

def once(s,old,new):
 n=s.count(old)
 assert n==1,(old[:180],n)
 return s.replace(old,new,1)

def apply(html):
 root=Path(__file__).resolve().parents[1]
 css=(root/'runtime/sheep_rapid_build_rotated_routes_wireframe_v11_132.css').read_text(encoding='utf8')
 js=(root/'runtime/sheep_rapid_build_rotated_routes_wireframe_v11_132.js').read_text(encoding='utf8')
 html=html.replace('</head>','<style id="se132-rapid-build">'+css+'</style>\n</head>',1)
 html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=')
 # Capture child canvas/visual layers of the viewport, not just the root,
 # when continuing a building ghost after the skill was selected.
 html=once(html,
  "const button=event.target?.closest?.('button[data-st-skill^=\"st-\"]'),world=event.target===$('viewport');",
  "const button=event.target?.closest?.('button[data-st-skill^=\"st-\"]'),viewport=$('viewport'),world=event.target===viewport||viewport?.contains(event.target);")
 # Critical: meadow drag must preserve the existing active tool; reselecting
 # an identical skill toggles it OFF in stUiChooseBuild.
 html=once(html,
  "const kind=button?.dataset.stSkill||stUi.build;\n stBuildInputFinish('New placement');\n if(!stBuildInputCost(kind).ok){stBuildInputReject(stBuildInputFundsMessage(kind));return;}\n stUiChooseBuild(kind);if(!stTouchPlacementEnabled())return;",
  "const kind=button?.dataset.stSkill||stUi.build,meadow=!button;\n stBuildInputFinish('New placement',meadow);\n if(!stBuildInputCost(kind).ok){stBuildInputReject(stBuildInputFundsMessage(kind));return;}\n if(!meadow)stUiChooseBuild(kind); // already-selected tool must survive the next meadow drag\n if(!stTouchPlacementEnabled())return;")
 # Preserve chosen house in Rapid mode only AFTER a successful native order.
 html=once(html,
  "if(outcome?.ok){stBuildInputFinish('Building accepted');stUiFeedback('Building ordered.');}",
  "if(outcome?.ok){const repeat=st132Rapid,kind=stBuildInput.kind;stBuildInputFinish('Building accepted');\n  if(repeat&&stSession&&!stSession.winner){stUiChooseBuild(kind);st126SeedAtSheep();}\n  stUiFeedback(repeat?'Building ordered. Drag to place another.':'Building ordered.');}")
 html=once(html,
  'SWYRL_ENGINE_DEPLOY_MARKER: V11_131_DIRECTED_SHORT_MIRROR_DECOY_COOLDOWN',
  'SWYRL_ENGINE_DEPLOY_MARKER: V11_132_RAPID_BUILD_UNDERPASS_AND_SHEEP_WIREFRAME')
 for old,new in [
  ('ENGINE · MAKER v11.131','ENGINE · MAKER v11.132'),
  ('v11.131 · directed mirror and mobile controls','v11.132 · rapid building and raised crossings'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.131'","window.SWRLZ_FORGE_BUILD={version:'v11.132'"),
  ('<title>§wyrl§ Engine · Maker v11.131</title>',
   '<title>§wyrl§ Engine · Maker v11.132</title>')
 ]:html=once(html,old,new)
 key='const SE_RELEASE_NOTES='
 at=html.index(key)+len(key)
 obj,n=json.JSONDecoder().raw_decode(html[at:])
 obj.update(title='Drag sheep-origin hologram, rapid construction, rotated elevated paths and occlusion wireframe',
  date='2026-10-26',changes=[
  'Corrected the building preview meadow drag regression: after selecting a skill, the next meadow pointerdown retains the active build tool instead of toggling it off by calling stUiChooseBuild again; child canvas hits are recognized as meadow. Pointermove updates the live hologram, and pointerup commits through native safety/resource checks.',
  'New circular Rapid Build toggle is closer to mid-screen. When active, a successful placement keeps that same house/ramp/walkway selected and immediately starts another sheep-origin preview; when disabled it remains single-placement.',
  'Every actual constructed structure briefly imposes a 0.28-second sheep recovery, without freezing the game; a new movement command or an active joystick overrides this pause at once.',
  'Three indestructible prebuilt raised crossings are now oriented in different directions, with geometry-aligned ramp/deck joints. A Rotate 90-degree button beside Rapid Build exposes existing native rotation for player-placed ramp or walkway.',
  'Completed raised decks do not obstruct ground-level sheep or wolves: they can pass under the 3.3-unit-high platform without accessing the upper surface. Ramps and incomplete walkways retain their proper obstacles.',
  'If a sheep passes underneath an elevated walkway or becomes hidden by a house between it and the current camera, a translucent cyan wireframe of that actual sheep appears through the occluder and disappears when clear. Collision, actor mesh, game commands, sprite saves and default models are untouched.',
  'All prior §E features, camera controls, Mirror decoy and 68 bundled assets are preserved.'
 ])
 html=html[:at]+json.dumps(obj,ensure_ascii=False,separators=(',',':')).replace('</','<\\\\/')+html[at+n:]
 raw=html.encode('utf8')
 print('SE_V11132_BUILD_MEASURE',len(raw),hashlib.sha256(raw).hexdigest(),flush=True)
 return html
