"""§E v11.224 — Particle Studio reusable VFX authoring, native project persistence.

Append-only patch. No change to built-in Sheep Tag cosmetic effects, §C, AI
models, VR controller mappings or original starter scene geometry.
"""
from pathlib import Path
import json


def once(s,a,b):
    n=s.count(a)
    if n!=1:
        raise AssertionError(('v11.224 particle studio anchor',a[:160],n))
    return s.replace(a,b,1)


def apply(html):
    root=Path(__file__).resolve().parents[1]
    core=(root/'runtime/particle_studio_core_v11_224.js').read_text('utf8')
    ui=(root/'runtime/particle_studio_ui_v11_224.js').read_text('utf8')
    css=(root/'runtime/particle_studio_v11_224.css').read_text('utf8')
    # The native editor's existing WebGL canvas and tick remain authoritative.
    # Particle visuals update immediately before its one render path (flat/XR).
    html=once(html,'beginPhysicalContactFrame();updateWispVisuals(t);',
              'se223Frame(dt,t);beginPhysicalContactFrame();updateWispVisuals(t);')
    html=once(html,'window.SWRLZ_FORGE_BUILD=',
              core+'\n'+ui+'\nwindow.SWRLZ_FORGE_BUILD=')
    assert '</head>' in html
    html=html.replace('</head>','<style id="se223ParticleStudio">'+css+'</style>\n</head>',1)
    html=once(html,
      " source.engine='§wyrl§ Engine · Maker v11.223';source.version=11.223;",
      " source.engine='§wyrl§ Engine · Maker v11.224';source.version=11.223;")
    for old,new in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_223_FIST_CLENCH_WRIST_WAVE',
       'SWYRL_ENGINE_DEPLOY_MARKER: V11_224_NATIVE_PARTICLE_STUDIO'),
      ('ENGINE · MAKER v11.223','ENGINE · MAKER v11.224'),
      ('v11.223 · Stronger hand clench and wrist-driven wave',
       'v11.224 · Native Particle Studio and reusable VFX emitters'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.223'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.224'"),
      ('<title>§wyrl§ Engine · Maker v11.223</title>',
       '<title>§wyrl§ Engine · Maker v11.224</title>')
    ]:html=once(html,old,new)
    tag='const SE_RELEASE_NOTES='
    pos=html.index(tag)+len(tag)
    notes,n=json.JSONDecoder().raw_decode(html[pos:])
    notes.update(title='Native Particle Studio: visual emitter creator, live editing and project VFX',
      date='2026-11-02',changes=[
        'Added a dedicated compact touch-first Particle Studio overlay to the main §E game editor with draggable title, immediate preview, 10 reusable presets, add/duplicate/delete, burst test and emitter picking.',
        'Particle inspector edits emission mode (continuous/one-shot), four spawn shapes, rate, burst count, lifetime, speed, direction, spread, gravity, drag, size, radius, start/end colors, blending and 3D position.',
        'Emitters can attach to the selected native editor actor or be placed in front of the camera; particles follow actor emission position, retaining independent world-space motion after birth.',
        'Native project.particleStudio definitions are included in normal project saves, native Undo/Redo and project level snapshots. Import/export uses a strict versioned emitter-only JSON schema with unique IDs, finite bounded values and 12 emitter limit.',
        'Each active emitter uses one THREE.Points point cloud on the existing renderer and animation frame, with 96 motes per emitter and 576 motes globally. GPU objects are disposable cosmetic render data, not scene actors or physics.',
        'User-custom particle effects are available in both editor preview and project Play/Simulate without a second renderer, cloud dependency or §C change. Existing Sheep Tag spawn/build effects are preserved separately.',
        'Desktop/browser build and script checks do not substitute Android, Quest 2, touch, source import and gameplay quality acceptance; owner hardware review remains pending.'
      ])
    return html[:pos]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[pos+n:]
