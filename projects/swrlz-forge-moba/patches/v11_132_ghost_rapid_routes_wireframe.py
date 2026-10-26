"""§E v11.132: native touch meadow aiming, opt-in rapid-build rhythm,
rotated permanent crossings, ground underpasses and occluded sheep outlines."""
from pathlib import Path
import json,hashlib

def once(s,old,new):
 n=s.count(old)
 assert n==1,(old[:180],n)
 return s.replace(old,new,1)

def apply(html):
 root=Path(__file__).resolve().parents[1]
 css=(root/'runtime/sheep_rapid_build_meadow_drag_v11_132.css').read_text(encoding='utf8')
 movement=(root/'runtime/sheep_rapid_build_meadow_drag_v11_132.js').read_text(encoding='utf8')
 world=(root/'runtime/sheep_world_underpass_wireframe_v11_132.js').read_text(encoding='utf8')
 html=html.replace('</head>','<style id="se132-rapid-build">'+css+'</style>\n</head>',1)
 html=once(html,'window.SWRLZ_FORGE_BUILD=',movement+'\n'+world+'\nwindow.SWRLZ_FORGE_BUILD=')
 # Renderer-owned canvas children are ground, not a different control.
 html=once(html,
   """const button=event.target?.closest?.('button[data-st-skill^="st-"]'),world=event.target===$('viewport');""",
   """const button=event.target?.closest?.('button[data-st-skill^="st-"]'),world=st132MeadowTarget(event.target);""")
 html=once(html,"document.elementFromPoint(x,y)===viewport;","st132MeadowTarget(document.elementFromPoint(x,y));")
 html=html.replace("if (gesture && (event.pointerType!=='touch' || event.target!==$('viewport'))) {",
                "if (gesture && (event.pointerType!=='touch' || !st132MeadowTarget(event.target))) {")
 html=html.replace(
   "if (!stTouchPlacementEnabled() || event.pointerType!=='touch' || event.target!==$('viewport') ||",
   "if (!stTouchPlacementEnabled() || event.pointerType!=='touch' || !st132MeadowTarget(event.target) ||")
 # Preserve a selected house after a successful order only when toggled on.
 html=once(html,
   "stUiFeedback(name + ' ordered. Your sheep will walk to the construction site.');\n       stUi.build = null; stUiClearPreview(); stRefreshHUD(true);",
   "stUiFeedback(name + ' ordered. Your sheep will walk to the construction site.');\n       if(!st132Rapid.on){stUi.build = null; stUiClearPreview();} stRefreshHUD(true);")
 # Native world pointerup returns the next ghost to the sheep while keeping
 # the selected build kind. A skill tap continues to be selection-only.
 html=once(html,
   "if(outcome?.ok){stBuildInputFinish('Building accepted');stUiFeedback('Building ordered.');}",
   "if(outcome?.ok){stBuildInputFinish('Building accepted',st132Rapid.on);if(st132Rapid.on)st126SeedAtSheep();stUiFeedback(st132Rapid.on?'House ordered. Continue dragging to build.':'Building ordered.');}")
 html=once(html,
  'SWYRL_ENGINE_DEPLOY_MARKER: V11_131_DIRECTED_SHORT_MIRROR_DECOY_COOLDOWN',
  'SWYRL_ENGINE_DEPLOY_MARKER: V11_132_MEADOW_GHOST_DRAG_RAPID_BUILDER_ROTATED_UNDERPASS_WIREFRAME')
 for a,b in [
  ('ENGINE · MAKER v11.131','ENGINE · MAKER v11.132'),
  ('v11.131 · directed mirror and mobile controls','v11.132 · rapid builder and visible sheep'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.131'","window.SWRLZ_FORGE_BUILD={version:'v11.132'"),
  ('<title>§wyrl§ Engine · Maker v11.131</title>','<title>§wyrl§ Engine · Maker v11.132</title>')
 ]:html=once(html,a,b)
 tag='const SE_RELEASE_NOTES='
 i=html.index(tag)+len(tag)
 notes,n=json.JSONDecoder().raw_decode(html[i:])
 notes.update(title='Drag house ghost on meadow, Rapid Build toggle, cancellable build beat, rotated crossings and occluded sheep outline',
  date='2026-10-26',changes=[
   'The house hologram starts at the controlled sheep and now follows a fresh meadow touch drag even if the browser targets a child of the native viewport; HUD, control buttons and text inputs are still excluded. Green/red fit and collision checks continue updating before release.',
   'A new interior circular Rapid Build toggle on mobile keeps the selected house tool active after a valid placement, allowing consecutive previews and orders, with a capped pending construction queue. Turn off to resume normal one-shot building.',
   'A sheep pauses for 0.18 game seconds immediately after constructing a house. Any joystick movement or move order cancels that short construction beat (and stale pending orders) immediately; no other units pause.',
   'The three permanent raised ramp/deck/ramp starter crossings now face three different world headings while remaining continuous, indestructible elevated pathways.',
   'Permanent completed raised walkway decks no longer block sheep ground navigation underneath; lower sloping ramps, player-made buildings, and solid houses retain collision.',
   'When a visible sheep is obscured by a house or elevated walkway from the current camera, a turquoise depth-independent wireframe of that sheep appears through the obstacle. The outline disappears when the sheep is visible and never reveals fog-hidden enemy sheep.',
   'The earlier v11.131 Mirror decoy, v11.130 browser zoom guard and all previous engine code and art assets remain unchanged.'
  ])
 html=html[:i]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\\\/')+html[i+n:]
 raw=html.encode('utf8')
 print('SE_V11132_BUILD_MEASURE',len(raw),hashlib.sha256(raw).hexdigest(),flush=True)
 return html
