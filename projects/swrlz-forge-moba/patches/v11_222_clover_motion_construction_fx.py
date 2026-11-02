"""§E v11.222 — one shared Clover sheep animation source and bounded cosmetic VFX.

Both the standalone sheep-model starter and Sheep Tag use the identical joint
motion equations. Keep physics, LAN construction authority, authored maps and
original editable vertices untouched. No second renderer or animation loop.
"""
from pathlib import Path
import json


def once(html, old, new):
    count=html.count(old)
    if count!=1:
        raise AssertionError(('v11.222 sheep animation anchor', old[:140], count))
    return html.replace(old,new,1)


def apply(html):
    root=Path(__file__).resolve().parents[1]
    preview=(root/'runtime/model_atelier_sheep_animations_v11_222.js').read_text('utf8')
    shared=(root/'runtime/sheep_animation_particles_v11_222.js').read_text('utf8')
    css=(root/'runtime/model_atelier_sheep_animations_v11_222.css').read_text('utf8')

    # Model Atelier stays editable. Only the viewport mesh instances move;
    # active project parts, Undo/Redo, transforms and exports remain neutral.
    html=once(html,'  function refreshList(){',
              preview+'\n  function refreshList(){')
    html=once(html,'se220RigControlsInstall();se221StudioInstall();',
              'se220RigControlsInstall();se221StudioInstall();se222SheepStudioInstall();')
    html=once(html,'  function loop(){\n    if(!renderer)return;\n    se220RigFrame();',
              '  function loop(){\n    if(!renderer)return;\n    se220RigFrame();se222SheepPreviewFrame();')
    html=once(html,'  function close(){\n    se220RigClose();',
              '  function close(){\n    se222SheepPreviewClose();se220RigClose();')

    # The stock sheep-model card and deep link become animation-enabled
    # immediately on load. Exported native model JSON includes authored clips.
    html=once(html,'if(rebuild)data.project.modelAtelier=atelierAnimalBuild(species);',
              "if(rebuild)data.project.modelAtelier=atelierAnimalBuild(species);\n"
              " if(species==='sheep')data.project.modelAtelier.sheepAnimations=se222SheepClips();")
    # Native standalone model JSON imports preserve only safe, bounded sheep
    # joint-key clips; the modeler's existing parts validator still owns meshes.
    html=once(html,'model().parts=structuredClone(source.parts);',
              "model().parts=structuredClone(source.parts);\n"
              "       if(se222SheepIsModel()&&source.sheepAnimations&&"
              "se222SheepClipsValid(source.sheepAnimations))"
              "model().sheepAnimations=structuredClone(source.sheepAnimations);")

    # Runtime-only effects hook into the existing game tick, start and stop.
    # They never alter the modeler renderer or any match/host/guest game data.
    html=once(html,'window.SWRLZ_FORGE_BUILD=',shared+'\nwindow.SWRLZ_FORGE_BUILD=')
    html=once(html,'</head>',
              '<style id="se222SheepStudio">'+css+'</style>\n</head>')
    html=once(html,
      " source.engine='§wyrl§ Engine · Maker v11.221';source.version=11.221;",
      " source.engine='§wyrl§ Engine · Maker v11.222';source.version=11.222;")
    for old,new in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_221_THUMB_OPPOSITION_GESTURES',
       'SWYRL_ENGINE_DEPLOY_MARKER: V11_222_CLOVER_MOTIONS_BUILD_SPARKS'),
      ('ENGINE · MAKER v11.221','ENGINE · MAKER v11.222'),
      ('v11.221 · Opposable thumb and gesture animation library',
       'v11.222 · Clover motions and Sheep Tag building sparkles'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.221'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.222'"),
      ('<title>§wyrl§ Engine · Maker v11.221</title>',
       '<title>§wyrl§ Engine · Maker v11.222</title>')
    ]: html=once(html,old,new)

    tag='const SE_RELEASE_NOTES='
    pos=html.index(tag)+len(tag)
    notes,n=json.JSONDecoder().raw_decode(html[pos:])
    notes.update(title='Clover comes alive: animated sheep and magical house construction',
      date='2026-11-02',changes=[
       'The same existing Clover Meadow Sheep joint motion library now provides six clips: Idle, Graze, Walk, Trot, Build and Celebrate. Sheep Tag and the standalone Sheep Model starter share joint names and pose calculations.',
       'Model Atelier sheep-model opens with exportable timed joint keys and a touch-friendly animation selector with live play/stop preview. Preview only changes viewport meshes; authoring and saved geometry stay neutral until explicitly saved.',
       'In Sheep Tag, each live Clover plays a distance-sensitive gait, relaxed breathing/head/tail motions, house-building hoof taps and a brief celebratory motion upon completing its own house.',
       'Starting the match produces a short cyan/teal sheep-spawn sparkle. Houses emit warm amber construction motes during progress and a teal finish burst at host-authoritative completion.',
       'All game particles are client-side cosmetic, share one GPU Points draw call, cap at 96 motes, and are disposed on match stop. There is no new render loop or networking, no changes to collision, house timers, resources or fog.',
       'Saved user projects, other starters, existing glove rig and Quest input remain unchanged. Physical Quest and Android performance and animation acceptance remain owner-tested.'
      ])
    return html[:pos]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[pos+n:]
