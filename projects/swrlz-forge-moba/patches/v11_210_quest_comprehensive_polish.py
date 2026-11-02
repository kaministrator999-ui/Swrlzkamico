"""§E v11.210: coordinated Quest Sheep Tag Play visual, spatial, controls and FPS pass.
Append-only, backed by two scoped JS modules; preserve ordered history/68 assets.
"""
from pathlib import Path
import json

def once(source,old,new):
    count=source.count(old)
    assert count==1,('v11.210 source anchor',old[:120],count)
    return source.replace(old,new,1)

def apply(html):
    root=Path(__file__).resolve().parents[1]
    # New developer-adjustable button mappings affect only se204 Play-wheel
    # state sampling. Non-VR, camera, editor, grip, game commands unchanged.
    html=once(html,
        "const record=se192InputRecord(side),state=se204.buttons[side];\n  const pressed=se192Pressed(record,4);",
        "const record=se192InputRecord(side),state=se204.buttons[side];\n  const pressed=se210Held(record,side);")
    # If pointing at a floating §E app panel, do not update a world-placed
    # house ghost beneath the panel, even while a build tool is equipped.
    html=once(html,
        "if(stUi.build&&!se195.visible&&!se195.photo&&now-se193.previewAt>100){",
        "if(stUi.build&&!se195.visible&&!se195.photo&&!se210PanelHit(se192InputRecord('right'))&&now-se193.previewAt>100){")
    a=(root/'runtime/sheep_xr_world_quality_metrics_v11_210.js').read_text(encoding='utf8')
    b=(root/'runtime/sheep_xr_workspace_controls_v11_210.js').read_text(encoding='utf8')
    html=once(html,'window.SWRLZ_FORGE_BUILD=',a+'\n'+b+'\nwindow.SWRLZ_FORGE_BUILD=')
    for old,new in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_209_SHEEP_RADIAL_ICONS_FEEDBACK',
       'SWYRL_ENGINE_DEPLOY_MARKER: V11_210_QUEST_COMPREHENSIVE_POLISH'),
      ('ENGINE · MAKER v11.209','ENGINE · MAKER v11.210'),
      ('v11.209 · Sheep Tag Quest graphical house and ability selectors',
       'v11.210 · Sheep Tag Quest world, workspace, controls, FPS and skill polish'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.209'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.210'"),
      ('<title>§wyrl§ Engine · Maker v11.209</title>',
       '<title>§wyrl§ Engine · Maker v11.210</title>'),
    ]:html=once(html,old,new)
    key='const SE_RELEASE_NOTES=';at=html.index(key)+len(key)
    notes,n=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title='Quest Sheep Tag Play: new 3D landmarks, independent spatial workspace, persistent controls, real cooldowns and FPS',
      date='2026-11-01',changes=[
        'The v11.208 biome/landscape is reinforced with reusable low-polygon 3D timber/crystal waymarkers along the peripheral forest, far from houses/lanes and sanctuary. At most two instanced draw calls, zero new game/editor actors, shadows, controller ray targets, navigation cells or collisions.',
        'Add cosmetic-only Quest quality profiles (Performance, Balanced, Quality, Auto). Auto reduces instanced decoration only after sustained FPS loss and restores it after a stable interval. Gameplay physics, real fog/visibility, building and multiplayer remain untouched. No unsupported claim of control over Meta compositor or WebXR frame resolution.',
        'Add real Quest instrumentation for a rolling FPS/frame time, renderer draw calls, triangles, texture/geometry counts, fog CPU time/texture uploads and overlay frames, with an in-VR Metrics panel. Read values from the actual Three.js and frame-state sources; mock tests are not a headset benchmark.',
        'Add independent floating camera/build/skills/metrics/controller panels from the §E game SESSION > WORKSPACE menu. Each has world-space ray interaction, right-grip move/tilt, right-stick held-grip resize, pin/follow toggle, and close controls; positions and scale are saved as safe head-relative offsets in browser localStorage and reconstructed against the next XR session origin.',
        'Introduce Sheep Tag Play controller profile selection in WORKSPACE > QUALITY/controls: default right A and left X, optional both stick-clicks, or A plus left stick-click; hold thresholds are adjustable and haptics toggled. Configuration is scoped to rapid build/skill selection only and never changes editor mappings, B system tools, Y recenter or non-VR controls.',
        'Use actual stArchiveStatus on the currently controlled sheep for Mirror/Illusive Split and Totem remaining cooldown/unlock/one-use/cluster requirements. Display true countdowns in the illustrated radial and Skills panel; refresh at most once per second while a wheel remains open. Keep original skill command/validator authoritative.',
        'Make independently floating panels modal to their own controller ray: world placement previews stop following through panel surfaces, surface selection has priority, and reticle/beam end in front of the panel rather than behind it. The original §E quick A/X radial remains the preferred fast Play action.',
        'Preserve project source architecture, all earlier version checks and 68 bundled assets. Physical Quest 2 visual, fog, controller ergonomics and FPS acceptance still require the owner to test the headset. More extensive authored 3D geometry replacement and unrestricted arbitrary controller bindings remain open work.'
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+n:]
