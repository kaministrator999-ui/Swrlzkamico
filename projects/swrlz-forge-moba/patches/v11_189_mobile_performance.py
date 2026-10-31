"""§E v11.189 — opt-in Mobile Boost, efficient editor viewport checks and frame diagnostics."""
from pathlib import Path
import json

def once(s,old,new):
    count=s.count(old)
    if count!=1:raise AssertionError(('v11.189 anchor mismatch',old[:170],count))
    return s.replace(old,new,1)

def apply(html):
    root=Path(__file__).resolve().parents[1]
    js=(root/'runtime/engine_mobile_performance_v11_189.js').read_text(encoding='utf8')
    css=(root/'runtime/engine_mobile_performance_v11_189.css').read_text(encoding='utf8')
    html=html.replace('</head>','<style id="se189MobilePerformance">\n'+css+'\n</style>\n</head>',1)
    # Do not change existing medium/high or saved user choices. New preset is
    # explicitly user-selectable, without changing models or authored scenes.
    html=once(html,
        "if(!['auto','low','medium','high','custom'].includes(performancePrefs.preset))",
        "if(!['auto','mobile','low','medium','high','custom'].includes(performancePrefs.preset))")
    html=once(html,
        "loadPerformancePrefs();\nrenderer.setPixelRatio(performancePixelRatio());",
        """PERFORMANCE_PRESETS.mobile={renderScale:.62,shadows:false,shadowSize:512,maxFps:60};
loadPerformancePrefs();
renderer.setPixelRatio(performancePixelRatio());""")
    html=once(html,
        "installPerformanceSettings();applyPerformanceSettings();",
        "installPerformanceSettings();se189InstallPerfUI();applyPerformanceSettings();")
    # A native tick previously forced getBoundingClientRect() for the 3D
    # viewport every frame, even when layout is unchanged. Observe the parent
    # dimensions and check at most 4 Hz as a bounded safety fallback.
    html=once(html,
        "let se181MainLoopBooted=false;\nfunction tick(){",
        js+"\nlet se181MainLoopBooted=false;\nfunction tick(){")
    html=once(html,
        "const frameNow=performance.now();samplePerformance(frameNow);resize();",
        "const frameNow=performance.now();samplePerformance(frameNow);se189ResizeIfNeeded(frameNow);")
    # Keep XR's native stereo frame path intact. Measure CPU submission only;
    # no performance claim is made for asynchronous GPU timing.
    html=once(html,
        "if(renderer.xr.isPresenting){se181XRRender();renderer.render(scene,camera);}else if(shouldRenderFrame(frameNow))renderer.render(scene,camera);",
        """const se189RenderStart=performance.now();
  let se189Rendered=false;
  if(renderer.xr.isPresenting){
    se181XRRender();renderer.render(scene,camera);se189Rendered=true;
  }else if(shouldRenderFrame(frameNow)){
    renderer.render(scene,camera);se189Rendered=true;
  }
  se189TrackMainFrame(frameNow,se189RenderStart,se189Rendered);""")
    for old,new in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_188_GAME_FIRST_WORKSPACE_TABS','SWYRL_ENGINE_DEPLOY_MARKER: V11_189_MOBILE_RENDER_BOOST'),
      ('ENGINE · MAKER v11.188','ENGINE · MAKER v11.189'),
      ('v11.188 · Game Engine default landing tab','v11.189 · mobile graphics optimization'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.188'","window.SWRLZ_FORGE_BUILD={version:'v11.189'"),
      ('<title>§wyrl§ Engine · Maker v11.188</title>','<title>§wyrl§ Engine · Maker v11.189</title>'),
    ]:html=once(html,old,new)
    key='const SE_RELEASE_NOTES='
    pos=html.index(key)+len(key)
    notes,count=json.JSONDecoder().raw_decode(html[pos:])
    notes.update(title='Mobile rendering boost and inspectable scene frame costs',date='2026-10-31',
      changes=[
       'Add opt-in Mobile Boost to Graphics & Performance: 62% render scale, shadows off, 512 shadow tier and 60 FPS cap. All actual game/model geometry remains unchanged.',
       'Eliminate unconditional DOM viewport measurement every render frame: ResizeObserver invalidation, mobile orientation and visual viewport events plus a bounded 250ms fallback.',
       'Show native WebGL draw calls and triangle counts plus separately labeled JavaScript/update and render-submission times in the Graphics & Performance panel, without misrepresenting GPU time.',
       'Keep existing Auto, Low, Medium, High and Custom settings, authored rendering preferences, saved projects, modeler page, VR ownership and game simulation unchanged.',
       'Performance gains depend on device and scene. Owner comparison before/after on Android and Quest is still needed.'
      ])
    return html[:pos]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\\\/')+html[pos+count:]
