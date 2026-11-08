"""§E v11.340: native Model Studio in the existing immersive XR loop."""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
MARKER = 'SWYRL_ENGINE_DEPLOY_MARKER: V11_340_IMMERSIVE_MODEL_STUDIO'


def once(html, old, new):
    count = html.count(old)
    if count != 1:
        raise AssertionError(('v11.340 anchor', old[:120], count))
    return html.replace(old, new, 1)


def apply(html):
    # Guard all native flat-canvas paints while its actual model root is in XR.
    start = html.index('const ModelAtelier=(()=>{')
    end = html.index('/* ATELIER_BRIDGE_END */', start)
    native = html[start:end]
    assert native.count('renderer.render(world,camera)') == 8
    native = native.replace('renderer.render(world,camera)', '(!se340ModelBridge.isBorrowed()&&renderer.render(world,camera))')
    native = once(native, 'if(!atelierHDEnabled||atelierHDDirty||atelierAssemblyPlaying){',
                  'if(!se340ModelBridge.isBorrowed()&&(!atelierHDEnabled||atelierHDDirty||atelierAssemblyPlaying)){')
    html = html[:start] + native + html[end:]
    bridge = (ROOT / 'runtime/model_vr_bridge_v11_340.js').read_text('utf8')
    html = once(html, '/* ATELIER_BRIDGE_END */', bridge + '\n/* ATELIER_BRIDGE_END */')
    html = once(html, 'return Object.freeze({chatAction:seChatAtelierApply,',
                'return Object.freeze({xrBridge:se340ModelBridge,chatAction:seChatAtelierApply,')
    # Enter before any Game update/VR handler; retain the one existing loop.
    html = once(html, 'let se181MainLoopBooted=false;\nfunction tick(){',
                'let se181MainLoopBooted=false;\nfunction tick(se340Time,se340Frame){')
    boot = 'if(!se181MainLoopBooted){se181MainLoopBooted=true;renderer.xr.enabled=true;renderer.setAnimationLoop(tick);}'
    html = once(html, boot, boot + '\n  if(se340ModelXRActive()){se340ModelXRFrame(se340Time,se340Frame);return;}')
    blocked = "if(se181XRActiveModel()){\n  se181XRNote('Close Model Atelier first. This VR doorway opens the main §E scene; immersive sculpting needs its own adapter.',true);\n  return false;\n }"
    html = once(html, blocked, "if(se181XRActiveModel()){return window.SWYRL_ENGINE_MODEL_VR?.enter?.()||false;}")
    html = once(html, 'async function se181XRExit(){\n if(!se181XR.session)return false;',
                "async function se181XRExit(){\n if(window.SWYRL_ENGINE_MODEL_VR?.read?.().active)return window.SWYRL_ENGINE_MODEL_VR.exit();\n if(!se181XR.session)return false;")
    read = "function se181XRRead(){\n const modelVR=window.SWYRL_ENGINE_MODEL_VR?.read?.();\n if(modelVR?.active)return {...modelVR,mode:'immersive-vr',workspace:'modeler',rendererShared:true,nativeSceneShared:false,modelAtelierXR:true,sculptXR:false,locomotionXR:false,trackedControllers:modelVR.controllers||[],lastError:modelVR.error||''};\n"
    html = once(html, 'function se181XRRead(){\n', read)
    html = once(html, 'modelAtelierXR:false,sculptXR:false,',
                'modelAtelierXR:!!window.SWYRL_ENGINE_MODEL_VR,sculptXR:false,')
    html = once(html, 'const b=se181XR.button;if(!b)return;\n b.disabled=',
                "const b=se181XR.button;if(!b)return;\n const modelVR=window.SWYRL_ENGINE_MODEL_VR?.read?.();\n if(modelVR?.active||modelVR?.busy){b.disabled=!!modelVR.busy;b.textContent=modelVR.active?'🥽 Exit model VR':'🥽 Opening model VR…';b.setAttribute('aria-pressed',String(!!modelVR.active));return;}\n b.disabled=")
    scripts = ['model_studio_vr_ui_v11_340.js', 'model_vr_workspace_v11_340.js', 'model_vr_entry_v11_340.js']
    js = '\n'.join((ROOT / 'runtime' / name).read_text('utf8') for name in scripts)
    html = once(html, 'window.SWRLZ_FORGE_BUILD=', js + '\nwindow.SWRLZ_FORGE_BUILD=')
    css = (ROOT / 'runtime/model_vr_entry_v11_340.css').read_text('utf8')
    assert html.index('</head>') < html.index('<body')
    html = html.replace('</head>', '<style id="se340ModelVRStyle">\n' + css + '\n</style>\n</head>', 1)
    previous = " source.engine='§wyrl§ Engine · Maker v11.337';source.version=11.337;"
    assert html.count(previous) == 3
    html = html.replace(previous, " source.engine='§wyrl§ Engine · Maker v11.340';source.version=11.340;")
    for old, new in [
        ('SWYRL_ENGINE_DEPLOY_MARKER: V11_337_CLIFF_ORGANIC_GEODES', MARKER),
        ('ENGINE · MAKER v11.337', 'ENGINE · MAKER v11.340'),
        ('v11.337 · natural palm wrist taper, smooth fingertips and inset crystal geodes', 'v11.340 · immersive Model Studio and controller authoring'),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.337'", "window.SWRLZ_FORGE_BUILD={version:'v11.340'"),
        ('<title>§wyrl§ Engine · Maker v11.337</title>', '<title>§wyrl§ Engine · Maker v11.340</title>'),
    ]:
        html = once(html, old, new)
    key = 'const SE_RELEASE_NOTES='
    at = html.index(key) + len(key)
    notes, width = json.JSONDecoder().raw_decode(html[at:])
    if not any(item.get('version') == 'v11.337' for item in notes.get('history', [])):
        notes.setdefault('history', []).insert(0, {'version': 'v11.337', 'changes': notes.get('changes', [])})
    notes.update(version='v11.340', title='Model Studio inside VR', date='2026-11-08', changes=[
        'Enter immersive Model VR directly from Model Studio. Inspect the actual native model on a comfortable presentation stage, with a readable world-space tool palette and controller guide.',
        'Trigger selects real model parts. Choose Move, Rotate or Scale before gripping; grip-space motion previews the selected part and release commits one native history edit. Cancel, tracking loss and session exit discard uncommitted previews.',
        'Use the in-headset palette and Touch buttons for tools, undo, redo, precision, snap, focus, recenter and exit. Hover, selection, controller rays and optional haptics provide clear feedback.',
        'Presentation framing and scale do not change saved geometry. Model parts, materials, rigs and geometry stay native, and return to the browser editor on exit.',
        'Keep Game/Arcane/Particle/Materials XR and editing paths separate. Model VR supports part transforms and inspection; sculpt and custom controller-profile execution retain their existing capability boundaries.',
        'Controller-emulation, native history and source checks are recorded separately from physical headset comfort and tracking acceptance.',
    ])
    return html[:at] + json.dumps(notes, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/') + html[at + width:]
