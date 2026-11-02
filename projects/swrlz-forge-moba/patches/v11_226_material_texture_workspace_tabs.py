"""§E v11.226 — native four-tab workspaces + Material & Texture Studio.

Append-only. Preserve v11.224 Particle Studio runtime, editor and VFX project
format; move Particle Studio into its own workspace alongside Game and Modeling.
Share one existing §E Three.js renderer and authored project history.
"""
from pathlib import Path
import json

def once(html, old, new):
    count=html.count(old)
    if count!=1:
        raise AssertionError(('v11.226 material/studio anchor',old[:145],count))
    return html.replace(old,new,1)

def apply(html):
    root=Path(__file__).resolve().parents[1]
    material=(root/'runtime/material_texture_core_v11_226.js').read_text('utf8')
    editor=(root/'runtime/material_texture_editor_v11_226.js').read_text('utf8')
    tabs=(root/'runtime/studio_workspace_tabs_v11_226.js').read_text('utf8')
    css=(root/'runtime/studio_material_texture_v11_226.css').read_text('utf8')
    # Add four native workspace tabs into existing Game/Modeler navigation.
    # Existing Game & Modeling tab events and project/Modeler controllers own
    # their original lifecycle, scratch drafts and saved project data.
    html=once(html,
        '  return nav;\n }\n function installTabs(){',
        '  se225DecorateNativeTabs(nav);\n  return nav;\n }\n function installTabs(){')
    # Historic viewport shortcut opens Particle Studio tab, not a floating
    # standalone popup. All old Particle Studio controls remain intact.
    html=once(html,
        "button.addEventListener('click',se223UIOpen);",
        "button.addEventListener('click',()=>se225Open('particles'));")
    # Update and preview materials on the authoritative existing engine tick.
    html=once(html,
        'se223Frame(dt,t);beginPhysicalContactFrame();',
        'se223Frame(dt,t);se225MaterialFrame(dt,t);beginPhysicalContactFrame();')
    html=once(html,'window.SWRLZ_FORGE_BUILD=',
        material+'\n'+editor+'\n'+tabs+'\nwindow.SWRLZ_FORGE_BUILD=')
    assert '</head>' in html
    html=html.replace('</head>','<style id="se225StudioMaterials">'+css+'</style>\n</head>',1)
    # Repair inherited v11.224 SOURCE.version inconsistency while bumping
    # provenance. No historical patch or asset bytes are rewritten.
    html=once(html,
        " source.engine='§wyrl§ Engine · Maker v11.225';source.version=11.225;",
        " source.engine='§wyrl§ Engine · Maker v11.226';source.version=11.225;")
    for old,new in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_225_ASTRA_WOLF_RIG_SHEEP_TAG',
       'SWYRL_ENGINE_DEPLOY_MARKER: V11_226_MATERIAL_TEXTURE_STUDIO_TABS'),
      ('ENGINE · MAKER v11.225','ENGINE · MAKER v11.226'),
      ('v11.225 · Astra wolf rig and Sheep Tag animations',
       'v11.226 · Material Texture Studio and four workspace tabs'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.225'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.226'"),
      ('<title>§wyrl§ Engine · Maker v11.225</title>',
       '<title>§wyrl§ Engine · Maker v11.226</title>')
    ]:html=once(html,old,new)
    key='const SE_RELEASE_NOTES='
    pos=html.index(key)+len(key)
    notes,n=json.JSONDecoder().raw_decode(html[pos:])
    notes.update(title='Four native workspaces: Game, Modeling, Particle Studio and Material & Texture Studio',
      date='2026-11-02',changes=[
       'Game Engine and Modeling now share a four-tab §E workspace bar with dedicated Particle Studio and Materials & Textures tabs. Both new studio pages preserve the game scene and native WebGL renderer as a live preview instead of creating a second render loop.',
       'Particle Studio is promoted from the floating viewport tool into its own routed workspace. Its 10 presets, bound emitter runtime, native scene persistence, VR renderer, import/export and 576-particle cap remain intact.',
       'Material & Texture Studio provides ten PBR starting materials: steel, gold, wood, stone, brick, fabric, leather, arcane glow, glass and ceramic. Create, duplicate, edit and delete project material assets.',
       'Generate 256×256 color textures using eight procedural patterns, seeded detail and UV repeat. Paint vector brush strokes directly onto textures, undo or clear paint and import PNG/JPEG images under strict size limits. Export rendered PNG or versioned, validated material JSON libraries.',
       'Edit base/pattern/emissive colors, roughness, metalness, glow, opacity, texture detail, seed and UV tiling. Apply named material assets to specific selected scene actors; restore the original actor appearance at any time.',
       'Project material definitions and actor assignments participate in native save/export, history Undo/Redo and project level snapshots. GPU texture caches and temporary preview sphere are disposed/rebuilt on project changes, and no physics, multiplayer or §C data is changed.',
       'Material Studio previews in the native game 3D viewport; applying directly to Model Atelier mesh parts is not yet exposed. Physical Android and Quest 2 mobile/VR visual and ergonomic acceptance remains owner-tested.'
      ])
    return html[:pos]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[pos+n:]
