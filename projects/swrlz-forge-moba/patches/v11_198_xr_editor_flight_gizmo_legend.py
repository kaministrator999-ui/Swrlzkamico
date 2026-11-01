"""§E v11.198 — Quest spatial editor flight, grab, gizmos and key legend.
Single existing XR renderer, native project history and actor scene.
"""
from pathlib import Path
import json

def once(s,a,b):
    n=s.count(a)
    if n!=1:raise AssertionError(('v11.198 source anchor',a[:180],n))
    return s.replace(a,b,1)

def apply(html):
    root=Path(__file__).resolve().parents[1]
    js=(root/'runtime/engine_xr_editor_controls_v11_198.js').read_text(encoding='utf8')
    html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=')
    for old,new in [
       ('SWYRL_ENGINE_DEPLOY_MARKER: V11_197_MEADOW_FOG_CAMERA_STABILITY',
        'SWYRL_ENGINE_DEPLOY_MARKER: V11_198_SPATIAL_EDITOR_FLIGHT_GIZMOS'),
       ('ENGINE · MAKER v11.197','ENGINE · MAKER v11.198'),
       ('v11.197 · Sheep Tag meadow and fog rendering stabilization',
        'v11.198 · smooth Quest editor flight, 3D grabbing and gizmos'),
       ("window.SWRLZ_FORGE_BUILD={version:'v11.197'",
        "window.SWRLZ_FORGE_BUILD={version:'v11.198'"),
       ('<title>§wyrl§ Engine · Maker v11.197</title>',
        '<title>§wyrl§ Engine · Maker v11.198</title>')
    ]:html=once(html,old,new)
    key='const SE_RELEASE_NOTES='
    pos=html.index(key)+len(key)
    notes,n=json.JSONDecoder().raw_decode(html[pos:])
    notes.update(title='Quest VR Editor: smooth flight, six-axis grabbing, pointer gizmos and in-world key legend',
      date='2026-11-01',changes=[
       'Make immersive Editor free-flight responsive with acceleration/deceleration and adjustable speeds (1.5, 3.2, 6.4 or 12.8 world units/sec), left thumbstick-click boost and left grip + right stick vertical flight. Preserve independent natural headset look and adjustable comfort snap turn. Per-device preferences are saved.',
       'Fix object pull depth. Right grip follows true controller displacement in all three world axes instead of constraining the object to one fixed ray distance. A single native undo transaction commits each actual drag, including precise parent-transform handling.',
       'Provide ray-selectable X/Y/Z world-axis gizmo handles. Select the colored arrow with the trigger, drag to move only along that axis, release trigger to commit native history; the right-grip grab remains available for unconstrained moving.',
       'Present a readable, native in-VR button legend under EDITOR > LEGEND, plus FLIGHT, GIZMOS, PREFABS and capture pages in the existing compact radial; keep modal input protection for menus.',
       'Reduce oversized Quest controller models and excessively bright beam aura/sparks, hide obsolete standalone transform helper axes while immersive editing, and exclude editor-only gizmo/legend art from clean screenshots.',
       'Re-use the single stable XR reference-space translation base already used in Sheep Tag to prevent repeated reference-space nesting from increasing during prolonged editor locomotion. Normal project files, modeler, Sheep Tag, Chat auth and existing controllers retain their ownership.'
      ])
    return html[:pos]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\\\/')+html[pos+n:]
