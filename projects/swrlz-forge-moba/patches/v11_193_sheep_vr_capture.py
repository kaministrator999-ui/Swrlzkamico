"""§E v11.193 candidate — preserve the single XR scene, add native Sheep Tag controls.

Source-only feature branch until the full packaged HTML checksum and governed
release metadata are rebuilt together. Never mutate earlier patch lineage.
"""
from pathlib import Path
import json

def once(html, old, new):
    count=html.count(old)
    if count != 1:
        raise AssertionError(("v11.193 anchor",old[:150],count))
    return html.replace(old,new,1)

def apply(html):
    root=Path(__file__).resolve().parents[1]
    js=(root/'runtime/engine_xr_sheep_capture_v11_193.js').read_text(encoding='utf-8')
    html=once(html,
        'let se181MainLoopBooted=false;\nfunction tick(){',
        js+'\nlet se181MainLoopBooted=false;\nfunction tick(){')
    html=once(html,
        'function se192Select(record){\n const hit=se192Raycast(record);',
        'function se192Select(record){\n if(se193XRSelect(record))return;\n const hit=se192Raycast(record);')
    html=once(html,
        'const cast=se192Ray(record);if(!cast)return null;\n // Native exit sign',
        'const cast=se192Ray(record);if(!cast)return null;\n const nativeSheepUi=se193XRHit(record,cast);if(nativeSheepUi)return nativeSheepUi;\n // Native exit sign')
    html=once(html,
        "function se192XRGamepadButton(record,button){\n if(record.input?.handedness==='left'",
        "function se192XRGamepadButton(record,button){\n if(se193XRGameButton(record,button))return true;\n if(record.input?.handedness==='left'")
    # Sheep Tag strategic scale can put the controller 50+ meters from the
    # terrain. Keep the editor's normal ray limit unchanged outside gameplay.
    html=once(html,
        'return {origin,direction,ray:new THREE.Raycaster(origin,direction,.025,35)};',
        'return {origin,direction,ray:new THREE.Raycaster(origin,direction,.025,se193XRGameActive()?140:35)};')
    html=once(html,
        'point.distanceTo(cast.origin)<35&&point.distanceTo(cast.origin)>.025',
        'point.distanceTo(cast.origin)<(se193XRGameActive()?140:35)&&point.distanceTo(cast.origin)>.025')
    html=once(html,
        'THREE.MathUtils.clamp(Number(hit?.distance)||3,.12,20)',
        'THREE.MathUtils.clamp(Number(hit?.distance)||3,.12,se193XRGameActive()?140:20)')
    # From the high Sheep Tag camera, keep Quest's beam comfortable and short
    # while the hit reticle still tracks the actual distant placement target.
    html=once(html,
        'beam.scale.z=dist; // local Z beam endpoint and raycast share a calibrated origin',
        'beam.scale.z=se193XRGameActive()?Math.min(dist,3.2):dist; // short game beam, distant target reticle')
    html=once(html,
        'dot.position.copy(cast.origin).addScaledVector(cast.direction,dist);',
        'dot.position.copy(cast.origin).addScaledVector(cast.direction,dist);\\n'
        ' dot.scale.setScalar(se193XRGameActive()?THREE.MathUtils.clamp(dist/5,1,20):1);')
    # The existing creator palette remains authoritative: add one doorway to
    # the compact XR capture panel rather than a second permanent toolbar.
    html=once(html,
        "['rock','PLACE ROCK'],['undo','UNDO'],['aimLeft','AIM ←'],",
        "['rock','PLACE ROCK'],['undo','UNDO'],['capture','CAPTURE'],['aimLeft','AIM ←'],")
    html=once(html,
        'function se192Action(action,record){\n se192.lastAction=action;',
        "function se192Action(action,record){\n se192.lastAction=action;\n if(action==='capture'){se193XRAction('editorCapture');return true;}")
    # The old authoring grip must not select/move map objects while a
    # native game menu, game session, or capture panel owns input.
    html=once(html,
        "if(!gripping||playing||simulating)return;\n const cast=se192Ray(record);if(!cast)return;",
        "if(!gripping||playing||simulating||se193XRMenuActive()||se193XRGameActive()||se193.editorCaptureOpen)return;\n const cast=se192Ray(record);if(!cast)return;")
    html=once(html,
        'if(!playing&&!simulating)se192MoveFrame(dt);',
        'if(!playing&&!simulating&&!se193XRMenuActive())se192MoveFrame(dt);')
    html=once(html,
        'se181XRRender();se192VRFrame();renderer.render(scene,camera);',
        'se181XRRender();se192VRFrame();se193XRFrame();renderer.render(scene,camera);')
    html=once(html,
        '  se192VRStart();',
        '  se192VRStart();\n  se193XRStart();')
    html=once(html,
        ' se192VRCleanup();\n se191XRCleanup();',
        ' se193XRCleanup();\n se192VRCleanup();\n se191XRCleanup();')
    for old,new in [
        ('SWYRL_ENGINE_DEPLOY_MARKER: V11_192_XR_SPATIAL_EDITOR',
         'SWYRL_ENGINE_DEPLOY_MARKER: V11_193_SHEEP_VR_CAPTURE'),
        ('ENGINE · MAKER v11.192','ENGINE · MAKER v11.193'),
        ('v11.192 · spatial VR map editor','v11.193 · immersive Sheep Tag and capture'),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.192'",
         "window.SWRLZ_FORGE_BUILD={version:'v11.193'"),
        ('<title>§wyrl§ Engine · Maker v11.192</title>',
         '<title>§wyrl§ Engine · Maker v11.193</title>')
    ]:
        html=once(html,old,new)
    key='const SE_RELEASE_NOTES='
    pos=html.index(key)+len(key)
    notes,count=json.JSONDecoder().raw_decode(html[pos:])
    notes.update(title='Sheep Tag immersive VR: in-world menu, elevated follow camera and Quest screenshots',
      date='2026-10-31',changes=[
        'Keep the authored Sheep Tag main menu and its existing Play pathway but offer a native ray-selectable 3D menu while in immersive VR; the 2D menu remains for browser users.',
        'Follow a controlled sheep using a smoothed elevated XR reference-space camera origin with wide map visibility; retain natural headset rotation, free-pan, orbit, zoom and recenter.',
        'Let the calibrated Quest ray select sheep, buildings and terrain, issue authoritative move/attack/rescue orders, and place validated farm types with the existing game-state and preview controllers.',
        'Use X to toggle in-world Sheep Tag tools, A to cycle build types, Y to snap back to the sheep and B to cancel building or detach the camera; trigger activates the selected target.',
        'Capture a clean 2D editor image or an optional stereo side-by-side image through an offscreen render target without adding another render loop; show a normal-browser download fallback after leaving VR.',
        'Keep authored project data, desktop/mobile Sheep Tag controls, independent Model Atelier and the Quest system exit untouched. Physical Quest 2 UX/performance acceptance is still required.'
      ])
    return html[:pos]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\\\/')+html[pos+count:]
