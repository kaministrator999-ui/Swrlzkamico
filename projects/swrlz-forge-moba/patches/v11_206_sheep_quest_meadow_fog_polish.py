"""§E v11.206: staged Meadow art and VR fog surface treatment for Sheep Tag.
All core map data, painter visibility ownership, collision and rules unchanged.
"""
from pathlib import Path
import json
def once(s,old,new):
    count=s.count(old)
    assert count==1,('v11.206 source lineage anchor',old[:110],count)
    return s.replace(old,new,1)
def apply(html):
    root=Path(__file__).resolve().parents[1]
    js=(root/'runtime/sheep_quest_meadow_fog_polish_v11_206.js').read_text(encoding='utf8')
    html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=')
    for old,new in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_205_SHEEP_TACTICAL_MENU_POINTER_OVERLAY',
       'SWYRL_ENGINE_DEPLOY_MARKER: V11_206_SHEEP_QUEST_MEADOW_FOG_ART'),
      ('ENGINE · MAKER v11.205','ENGINE · MAKER v11.206'),
      ('v11.205 · Sheep Tag tactical view and immersive menu polish',
       'v11.206 · Sheep Tag Quest meadow dressing and fog art'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.205'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.206'"),
      ('<title>§wyrl§ Engine · Maker v11.205</title>',
       '<title>§wyrl§ Engine · Maker v11.206</title>'),
    ]:html=once(html,old,new)
    tag='const SE_RELEASE_NOTES=';at=html.index(tag)+len(tag)
    notes,n=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title='Quest Sheep Tag: meadow art treatment, smoother visual fog, minimal GPU cost',
      date='2026-11-01',changes=[
       'A staged Quest Play-only meadow art overlay creates subtle four-quadrant biome tones, tiny wildflowers and grass detail, and a soft cobbled sanctuary perimeter. Existing authored ground, Wildwood texture, road and building transformations, castle/path collisions and nav geometry remain unchanged.',
       'Map decorative art renders as ONE alpha-textured ground plane under the fog, without scene actor or collider registration. It cannot intercept controller rays; controller buildings and sheep movement use exactly the same native gameplay grid and authority as v11.205.',
       'The 768x768 overlay canvas is generated incrementally in a dozen existing WebXR frames, in batches of about 110 tiny details, then uploaded to the GPU once; there is no new render loop and no active per-frame texture repaint. Painting pauses while a game wrist/photo menu or Quest OS overlay is open.',
       'While playing in Quest, fog texture retains the original native per-team visibility/visibility updates and LINEAR filtering, but its cosmetic alpha is eased to .84 and original fog mesh depth ordering/polygon offset is cleaned. Solo fog feather is slightly wider; multiplayer role/knowledge masks are unchanged. Original fog visual state is restored when VR exits.',
       'All new cosmetic material and GPU resources are disposed when a match stops or XR ends. No permanently saved map actors, network protocol changes, physics/AI changes or controller remaps.',
       'This is the FIRST world-art foundation pass; full map re-authoring, level landmarks, further native fog artifact testing, movable spatial panels and physical Quest 2 FPS acceptance remain open.'
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+n:]
