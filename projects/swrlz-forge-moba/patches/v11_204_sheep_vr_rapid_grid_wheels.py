"""§E v11.204 · Sheep Tag Play-only fast house lattice and VR hold radials.
No model-editor rotation, no second gameplay engine, no changes to LAN authority.
"""
from pathlib import Path
import json

def once(s,old,new):
    count=s.count(old)
    assert count==1,('v11.204 exact source anchor',old[:160],count)
    return s.replace(old,new,1)

def apply(html):
    root=Path(__file__).resolve().parents[1]
    js=(root/'runtime/engine_xr_sheep_rapid_grid_wheels_v11_204.js').read_text(encoding='utf8')
    # Native trigger keeps a successfully placed house selected for rapid
    # repeats, only while v11.204's VR gameplay quick tool is equipped.
    html=once(html,
      "if(result?.ok){stUi.build=null;stUiClearPreview();stRefreshHUD(true);}",
      "if(result?.ok){if(se204RapidEnabled())se204AfterBuild();else{stUi.build=null;stUiClearPreview();stRefreshHUD(true);}}")
    # The v11.203 forward-mapped controller beam must not continue
    # projecting onto game ground behind the new hold-to-select radial.
    html=once(html,
      "const isBuild=se200Active()&&stUi.build&&!se195.visible&&!se195.photo;",
      "const isBuild=se200Active()&&stUi.build&&!se195.visible&&!se195.photo&&!se204.wheel;")
    # Right B opens the native capture/settings wrist menu during VR Play.
    # Left Y stays Recenter. Native editor and non-Play VR buttons unchanged.
    html=once(html,
      """if(side==='left')se193XRSnapFollow();
   else if(stUi.build){stUi.build=null;stUiClearPreview();stRefreshHUD(true);}
   else se193.follow=false;""",
      """if(side==='left')se193XRSnapFollow();
   else if(se204Gameplay())se204MenuToggle();
   else if(stUi.build){stUi.build=null;stUiClearPreview();stRefreshHUD(true);}
   else se193.follow=false;""")
    # An axis-aligned HOUSE lattice only while the quick-build tool is on.
    # Preserve fine/coarse snapping, castle wall/ramp gameplay, touch play,
    # and modeling/editor rotations without changing any collision rule.
    html=once(html,
      "const corners = fit.corners, snap = stUi.build && ST_LANE_HOUSES.has(stUi.build) ? ST_GRID : (stUiRules().buildSnap || .15), gridStep = snap===3 ? 3 : .3;",
      "const corners = fit.corners, snap = stUi.build && ST_LANE_HOUSES.has(stUi.build) ? ST_GRID : (stUiRules().buildSnap || .15), gridStep = se204RapidEnabled() ? (stUiRules().buildSnap>=3 ? 6 : se204.pitch) : (snap===3 ? 3 : .3);")
    html=once(html,
      "if (snap!==3) for (let index=1;index<Math.round(length/snap);index++) {",
      "if (snap!==3 && !se204RapidEnabled()) for (let index=1;index<Math.round(length/snap);index++) {")
    html=once(html,
      "stPlacementGridPositions(guide.ticks,tickPositions); guide.ticks.visible = snap!==3;",
      "stPlacementGridPositions(guide.ticks,tickPositions); guide.ticks.visible = snap!==3 && !se204RapidEnabled();")
    html=once(html,
      "const margin = snap===3 ? 3 : 1.2, bounds=stUiRules().bounds || 40;",
      "const margin = se204RapidEnabled() ? gridStep*1.5 : (snap===3 ? 3 : 1.2), bounds=stUiRules().bounds || 40;")
    html=once(html,
      "for (let x=Math.ceil(minX/gridStep)*gridStep;x<=maxX+1e-7;x+=gridStep)",
      "for (let x=Math.ceil((minX-(se204RapidEnabled()?se204.anchor?.x||0:0))/gridStep)*gridStep+(se204RapidEnabled()?se204.anchor?.x||0:0);x<=maxX+1e-7;x+=gridStep)")
    html=once(html,
      "for (let z=Math.ceil(minZ/gridStep)*gridStep;z<=maxZ+1e-7;z+=gridStep)",
      "for (let z=Math.ceil((minZ-(se204RapidEnabled()?se204.anchor?.z||0:0))/gridStep)*gridStep+(se204RapidEnabled()?se204.anchor?.z||0:0);z<=maxZ+1e-7;z+=gridStep)")
    html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=')
    for old,new in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_203_QUEST_WRIST_MENU_FORWARD_PLACEMENT',
       'SWYRL_ENGINE_DEPLOY_MARKER: V11_204_SHEEP_VR_RAPID_GRID_WHEELS'),
      ('ENGINE · MAKER v11.203','ENGINE · MAKER v11.204'),
      ('v11.203 · Quest sheep near-center aiming and cached wrist camera menu',
       'v11.204 · Sheep Tag Quest rapid build grid and persistent skill selection'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.203'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.204'"),
      ('<title>§wyrl§ Engine · Maker v11.203</title>',
       '<title>§wyrl§ Engine · Maker v11.204</title>'),
    ]:html=once(html,old,new)
    key='const SE_RELEASE_NOTES='
    at=html.index(key)+len(key)
    notes,n=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title='Sheep Tag VR: hold to select, tap to repeat houses, real passage-grid, quick abilities',
      date='2026-11-01',changes=[
       'In active Sheep Tag Play, hold Quest right A for a compact, cached house radial; tilt right stick to select Farm, Income or Fort, then release to equip. Tap A repeatedly to place that same house at the controller ground preview. Right trigger also places the equipped house without clearing selection. A cancelled selection turns quick build off.',
       'The new repeatable 3.6-unit axis-aligned housing lattice places 2.4-unit houses with 1.2-unit traversable gaps: the first equipped preview seeds a local grid origin, subsequent placements snap onto that same grid, and the drawn ground lines match the actual building centers. Coarse 3-unit native maps use 6-unit cells instead. The original native stCanBuild collision, units, sanctuary, costs and anti-trap checks remain mandatory.',
       'No building rotation is offered in Sheep Tag Play. Rotation stays in the §E Game Editor/Model Editor and existing optional wall or ramp modes. Grid snapping adjusts centers only, never building orientation.',
       'Hold left X to open a separate compact ability radial. Select Mirror or Totem and release to persist the equipped ability. Tap X to invoke the selected native Sheep Tag skill, respecting preset availability, progression, cooldown and selected house requirements; disabled abilities are explicitly indicated.',
       'Right B opens/closes the existing native Quest tools/capture menu while playing, Left Y recenters on the controlled sheep; tapping/holding A/X actions run only in active free-sheep VR Play and do not affect editor controls, wolves, spectators, mobile or desktop inputs.',
       'Radial visuals are session-reused, use the same cached small Quest text textures and no per-frame material creation; the right stick is temporarily reserved for selector navigation while a hold wheel is open. Haptics are optional. Gameplay world selection is blocked behind modal selectors.',
       'Preserve Quest tracked camera, native ray-to-ground placement mapping, original VR and LAN match authority, fog, visual footprint overlays, Quest2 compositor lifecycle, all 68 asset files. Physical Quest usability and FPS still need hardware acceptance.'
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+n:]
