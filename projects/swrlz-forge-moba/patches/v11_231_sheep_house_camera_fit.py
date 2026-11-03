"""§E v11.231 — frame full Sheep Tag houses in the native Model Atelier.

v11.230 proved all five models validate and render, but the generic fixed-size
character camera clips whole buildings on mobile. Reuse the existing measured
bounding-box framing used by Comet Courier only for the five house starters.
No camera behavior changes for ordinary models, no meshes or game physics changed.
"""
import json


def once(s,old,new):
    n=s.count(old)
    if n!=1:raise AssertionError(('v11.231 camera fit source anchor',old[:150],n))
    return s.replace(old,new,1)


def apply(html):
    # Reuse *native* model framing, preserving the camera controls and one renderer.
    # Existing courier branch gets true mesh bounds; houses need exactly the same.
    html=once(html,
        "function atelierSetPoseCamera(view){",
        "function atelierSetPoseCamera(view){\n if(se226BuildingIds.has(currentProject?.canonicalId))return atelierCourierCamera(view);")

    # Expose top/bottom as proper bounds-aware orthographic-ish perspective views
    # only to the house selection (existing top/bottom button still works elsewhere).
    html=once(html,
        "three:[.46,.14],hero:[.32,.10]};if(!presets[view]",
        "three:[.46,.14],hero:[.32,.10],top:[0,1.53],bottom:[0,-1.53]};if(!presets[view]")
    html=once(html,
        "if(preset==='top'||preset==='bottom'){\n       atelierDetailTarget=null;",
        "if(preset==='top'||preset==='bottom'){\n       if(se226BuildingIds.has(currentProject?.canonicalId)){atelierCourierCamera(preset);status('House '+preset+' view · full model framed.');return;}\n       atelierDetailTarget=null;")

    # Auto-sized mobile house framing may legitimately exceed the close character
    # studio fog's old 29-unit cutoff; keep all houses visible at fitted distance.
    html=once(html,
        "orbit.distance=distance*1.12+.15;cameraUpdate();return true;",
        "orbit.distance=distance*1.12+.15;if(se226BuildingIds.has(currentProject?.canonicalId)&&world?.fog){world.fog.near=Math.max(24,orbit.distance*1.15);world.fog.far=Math.max(90,orbit.distance*3);}cameraUpdate();return true;")

    old=" source.engine='§wyrl§ Engine · Maker v11.230';source.version=11.230;"
    new=" source.engine='§wyrl§ Engine · Maker v11.231';source.version=11.231;"
    if html.count(old)!=2:
        raise AssertionError(('v11.231 provenance slots',html.count(old)))
    html=html.replace(old,new)

    for a,b in [
       ('SWYRL_ENGINE_DEPLOY_MARKER: V11_230_WOLF_MODEL_ONE_PASS_LOAD',
        'SWYRL_ENGINE_DEPLOY_MARKER: V11_231_SHEEP_HOUSE_CAMERA_FIT'),
       ('ENGINE · MAKER v11.230','ENGINE · MAKER v11.231'),
       ('v11.230 · Wolf Model single-pass rigged load repair',
        'v11.231 · full sheep house camera fit in Model Atelier'),
       ("window.SWRLZ_FORGE_BUILD={version:'v11.230'",
        "window.SWRLZ_FORGE_BUILD={version:'v11.231'"),
       ('<title>§wyrl§ Engine · Maker v11.230</title>',
        '<title>§wyrl§ Engine · Maker v11.231</title>')
    ]:
        html=once(html,a,b)

    marker='const SE_RELEASE_NOTES='
    i=html.index(marker)+len(marker)
    obj,n=json.JSONDecoder().raw_decode(html[i:])
    obj.update(
      title='Sheep house models: automatic full-building camera framing',
      date='2026-11-02',
      changes=[
        'Fix five sheep house starters appearing invisible or as cropped wall/roof close-ups after successful native load.',
        'Direct modeler starter and Projects card openings now invoke native 3D bounds-aware framing, instead of the generic fixed-distance character camera that cuts off wide buildings.',
        'Full-building front, side, top and 3/4 perspective views remain navigable on a narrow phone viewport; camera distance is derived from the editable mesh bounds and active canvas aspect ratio.',
        'Extend studio view fog only while a sheep-building starter is active and the measured camera requires it. Retain the existing native single 3D renderer and VR input.',
        'All house geometry, colors, material surfaces, mesh groups, saved project handling, wolf/glove models, Sheep Tag build rules, GUI studio and other tabs remain unchanged.',
        'Owner Moto G Power and Quest hands-on visual acceptance remains pending.'
      ])
    return html[:i]+json.dumps(obj,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[i+n:]
