"""§E v11.202 — rearward Quest sheep framing, joystick movement only, faster
preview and obstacle snapshots. Source-truth anchored, append-only patch.
"""
from pathlib import Path
import json

def once(s,old,new):
    n=s.count(old)
    assert n==1,('v11.202 anchor',old[:170],n)
    return s.replace(old,new,1)

def apply(html):
    root=Path(__file__).resolve().parents[1]
    js=(root/'runtime/engine_xr_sheep_framing_input_v11_202.js').read_text(encoding='utf8')
    # VR trigger over unoccupied ground must never issue a click-to-move order.
    # Native trigger interaction with buildings, rescue, attack and build stays.
    html=once(html,
      """ if(ground){
  stUi.buildingId=null;
  stUiCommand('select',{id:state.controlledId});
  se193XRFeedback(stUiCommand('move',{x:ground.x,z:ground.z}));
 }
 return true;
}
function se193XRSnapFollow(){""",
      """ if(ground){
  // v11.202 · Quest gameplay movement is exclusively the LEFT JOYSTICK.
  // Empty ground selects nothing; building, targeting and rescues still work.
  se202.noClickMoves++;
 }
 return true;
}
function se193XRSnapFollow(){""")
    # Avoid making a full fog/visibility status snapshot each preview tick.
    # Outside XR, preserve the original native stUiView semantics unchanged.
    html=once(html,
      'const fit = stCanBuild(stUi.build, point.x, point.z, stUiView().controlledId, stUi.rotation);',
      'const fit = stCanBuild(stUi.build, point.x, point.z, se202PreviewOwner(), stUi.rotation);')
    html=once(html,
      "const visible=(stUiView().buildings||[]).filter(b=>ST_LANE_HOUSES.has(b.kind));",
      "const visible=se202VisibleBuildings().filter(b=>ST_LANE_HOUSES.has(b.kind));")
    # Use a collision snapshot only for the direct XR thumbstick step.
    # Higher-level pathfinding and LAN inputs still use native stObstacles().
    html=once(html,
      "const context={rules:s.rules,obstacles:stObstacles()};\n      const radius=stUnitRadius(unit),before=unit.pos.clone();",
      "const context={rules:s.rules,obstacles:se202ObstacleSnapshot()};\n      const radius=stUnitRadius(unit),before=unit.pos.clone();")
    # Only do expensive build preview validation when ray aim, resource,
    # navigation or player moved, or at 520ms to catch unit movement.
    html=once(html,
      """   const right=se192InputRecord('right'),point=right&&se193XRGameGround(right);
   if(point)stUiPlacePreview(point);
   se193.previewAt=now;""",
      """   const right=se192InputRecord('right'),point=right&&se193XRGameGround(right);
   if(point&&se202ShouldRefreshPreview(point))stUiPlacePreview(point);
   se193.previewAt=now;""")
    html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=')
    for old,new in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_201_SHEEP_CLEARANCE_FOUNDATIONS',
       'SWYRL_ENGINE_DEPLOY_MARKER: V11_202_QUEST_WIDE_FOLLOW_JOYSTICK_ONLY'),
      ('ENGINE · MAKER v11.201','ENGINE · MAKER v11.202'),
      ('v11.201 · Warcraft-style Sheep Tag foundations and passage guides',
       'v11.202 · Quest wider high-framed sheep, joystick-only and performance'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.201'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.202'"),
      ('<title>§wyrl§ Engine · Maker v11.201</title>',
       '<title>§wyrl§ Engine · Maker v11.202</title>'),
    ]:html=once(html,old,new)
    at=html.index('const SE_RELEASE_NOTES=')+len('const SE_RELEASE_NOTES=')
    notes,n=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title='Quest Sheep Tag: pullback framing, joystick-only controls, smoother building performance',
      date='2026-11-01',changes=[
       'Move the Quest 2 camera BACK only, to 21 horizontal units at 1.4 zoom plus 2.5 world units rearward bias. Keep the previous 26 unit vertical camera configuration at the same 1.4 zoom, preserving its exact 36.4-unit effective height; never raise the camera or override physical headset pitch/motion.',
       'Draw a dominant cyan ring at the true native sheep collision radius and a much fainter model-sized selection halo around its visible wool/head. These deliberately differ because the sheep model overhangs its smaller physics radius. Rings track the user-controlled sheep at ground height, reuse the same meshes, and dispose on XR exit.',
       'Immersive VR right trigger over empty ground no longer issues click-to-move orders; left thumbstick remains sole locomotion. Ray selection of units/houses, targeting, rescue, building placement, right-stick orbit/zoom, wrist radial and editor controls remain.',
       'Skip heavyweight 2D status/fog snapshots when constructing Quest building ghost previews. Read current authoritative controlledId and visible buildings directly with stSeenByRole to respect fog.',
       'Skip redundant preview validations for effectively unchanged ray points, with a 520ms expiry to catch moving blockers; maintain same native collision and placement rules.',
       'Cache direct joystick obstacle snapshots only until the navigation version or completed raised wall count changes, preventing repeated rebuilt footprint arrays every XR step. AI, network, 2D movement and paths remain unmodified.',
       'Refresh new Warwick-style house foundations at a low frequency when navigation, visibility-relevant position or controlled unit changes. No new render loop; all previous release regression checks remain required. VR device testing still pending.'
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+n:]
