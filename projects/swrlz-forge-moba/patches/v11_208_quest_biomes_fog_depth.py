"""§E v11.208: authored-map-safe Quest four-biome and fog-depth art pass.
Preserve native Sheep Tag scenes, visibility ownership and 239-patch lineage.
"""
from pathlib import Path
import json
def once(s,old,new):
    n=s.count(old)
    assert n==1,('v11.208 expected inherited source anchor',old[:140],n)
    return s.replace(old,new,1)
def apply(html):
    root=Path(__file__).resolve().parents[1]
    js=(root/'runtime/sheep_quest_biome_landmarks_fog_depth_v11_208.js').read_text(encoding='utf8')
    html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=')
    for old,new in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_207_SHEEP_QUEST_SPATIAL_MENU',
       'SWYRL_ENGINE_DEPLOY_MARKER: V11_208_QUEST_BIOMES_FOG_DEPTH'),
      ('ENGINE · MAKER v11.207','ENGINE · MAKER v11.208'),
      ('v11.207 · Sheep Tag Quest grip-to-move world-pinned tools',
       'v11.208 · Sheep Tag Quest four-biome world and fog-layer stability'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.207'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.208'"),
      ('<title>§wyrl§ Engine · Maker v11.207</title>',
       '<title>§wyrl§ Engine · Maker v11.208</title>'),
    ]:html=once(html,old,new)
    tag='const SE_RELEASE_NOTES=';at=html.index(tag)+len(tag)
    notes,n=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title='Sheep Tag VR: four distinct biome landscapes, ground landmarks and fog-layer depth stabilization',
      date='2026-11-01',changes=[
        'Quest Sheep Tag Play now paints four identifiable natural regions (Pinewatch, Moonflower, Amberglade, Willowmere), each with its own ground palette, organic markings and subtle compass-like landmark motif. Existing sanctuary remains marked; native 80m meadow source paths get soft stone/dirt shoulders while 128m Wildwood retains its original 4K road texture.',
        'Region details are drawn into the existing v11.206 768x768 meadow atlas during its initial staged painting: no second texture, no additional shader, no per-frame GPU updates, no second game loop. All gameplay map positions and saved authored scene data remain unchanged.',
        'Add at most three efficiently instanced, low-polygon 3D botanical/pebble groups around existing source trees, ponds and rocks. Nothing blocks movement or intercepts controller rays; props render below fog and are disposed on XR exit or match stop. No extra colliders, game commands, AI or LAN changes.',
        'Harden VR fog surface depth ordering: move the game fog plane slightly above ground art with a stronger polygon-depth offset and explicit render order while retaining the original solo/team sight, explored memory, enemy filtering and painters. v11.206 still restores the native non-VR fog settings upon exit.',
        'Preserve v11.207 world-grabbable VR menu, v11.205 tactical camera/pointer, v11.204 rapid houses and abilities, 68 bundled assets, and desktop/model-editor behavior. Physical Quest 2 visual confirmation and any remaining fog flicker still require headset testing.',
        'This is a substantial visual-map progression rather than final authored-geometry remaster: next phases include stronger props/building art and biome lighting, revised radial icons and independent inspector panels.'
    ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+n:]
