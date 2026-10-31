"""§E v11.181: user-activated immersive WebXR on the existing main Three renderer."""
from pathlib import Path
import json

def once(s,a,b):
    count=s.count(a)
    if count!=1:raise AssertionError((a[:160],count))
    return s.replace(a,b,1)

def apply(html):
    root=Path(__file__).resolve().parents[1]
    js=(root/'runtime/immersive_xr_gateway_v11_181.js').read_text(encoding='utf-8')
    css=(root/'runtime/immersive_xr_gateway_v11_181.css').read_text(encoding='utf-8')
    # Appends only at THE native editor tick, not the exported standalone
    # scene, floating Model Atelier renderer, or other independent RAF loops.
    old="function tick(){\n  requestAnimationFrame(tick);const frameNow=performance.now();samplePerformance(frameNow);resize();"
    new=js+"\nlet se181MainLoopBooted=false;\nfunction tick(){\n  if(!se181MainLoopBooted){se181MainLoopBooted=true;renderer.xr.enabled=true;renderer.setAnimationLoop(tick);}\n  const frameNow=performance.now();samplePerformance(frameNow);resize();"
    html=once(html,old,new)
    # resize() is called in every native editor frame. Never set the WebGL
    # canvas size during the headset's XR framebuffer ownership.
    html=once(html,
      "function resize(){\n  const rect=$('viewport').parentElement.getBoundingClientRect()",
      "function resize(){\n  if(renderer.xr.isPresenting)return;\n  const rect=$('viewport').parentElement.getBoundingClientRect()")
    html=once(html,"if(!playing)orbit.update();if(selectionBox&&selected)selectionBox.update();",
      "if(!playing&&!renderer.xr.isPresenting)orbit.update();if(selectionBox&&selected)selectionBox.update();")
    html=once(html,"if(shouldRenderFrame(frameNow))renderer.render(scene,camera);",
      "if(renderer.xr.isPresenting){se181XRRender();renderer.render(scene,camera);}else if(shouldRenderFrame(frameNow))renderer.render(scene,camera);")
    assert '</head>' in html
    html=html.replace('</head>','<style id="seImmersiveXRV11181">\n'+css+'\n</style>\n</head>',1)
    for a,b in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_180_CHAT_OUTSIDE_DISMISS','SWYRL_ENGINE_DEPLOY_MARKER: V11_181_IMMERSIVE_WEBXR_GATE'),
      ('ENGINE · MAKER v11.180','ENGINE · MAKER v11.181'),
      ('v11.180 · Chat dismisses on outside selection','v11.181 · enter immersive VR from §E'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.180'","window.SWRLZ_FORGE_BUILD={version:'v11.181'"),
      ('<title>§wyrl§ Engine · Maker v11.180</title>','<title>§wyrl§ Engine · Maker v11.181</title>'),
    ]:
        html=once(html,a,b)
    key='const SE_RELEASE_NOTES='
    pos=html.index(key)+len(key)
    notes,length=json.JSONDecoder().raw_decode(html[pos:])
    notes.update(title='Step through the WebXR doorway into §E using Meta Quest Browser',
      date='2026-10-31',changes=[
        'Enter VR explicitly requests immersive-vr/local-floor from a user click; the browser continues to run §E with headset stereo rendering. Exit from the floating 3D EXIT VR sign or Quest system UI.',
        'Convert the existing main Three.js renderer and game/editor tick to a single setAnimationLoop source used in 2D and immersive modes. Preserve scene simulations, editor performance diagnostics and the established 2D layout.',
        'Track Quest XR target-ray controllers in the native scene; highlight ray hits and use trigger select to select actual editor actors. No synthetic clicks or unseen native geometry mutation.',
        'VR Controller Studio receives the real session for read-only device diagnostics. Actual mapping-to-transforms, locomotion, two-handed gestures and sculpt strokes are deferred.',
        'Model Atelier has a distinct renderer and remains 2D for this release; entering immersive mode while Model Atelier is open is blocked rather than opening a misleading workspace.',
        'WebXR requires HTTPS and device/browser permission; no session is requested on page load. Physical Quest 2 acceptance is pending.'
      ])
    return html[:pos]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\\\/')+html[pos+length:]
