"""§E v11.356: UV preview, popup placement, XR camera orbit and selected-only grip."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_356_UV_PREVIEW_VR_CAMERA_ORBIT'
def once(s,old,new):
    n=s.count(old)
    if n!=1:raise AssertionError(('v11.356 anchor',old[:110],n))
    return s.replace(old,new,1)
def apply(html):
    js=(ROOT/'runtime/model_atelier_uv_preview_v11_356.js').read_text('utf8')
    css=(ROOT/'runtime/model_atelier_uv_preview_v11_356.css').read_text('utf8')
    expected=[
      'function se356ApplyCameraOrbit()',
      'renderer.xr.setReferenceSpace(space);',
      "s.rig.rotation.set(0,s.baseYaw,0,'YXZ')",
      "const tools=se350Tools(),chosen=tools.selection()",
      'function safeBounds(){',
      'fitWindow(true);',
      'window.SWYRLZ_E_UV_POPUP=Object.freeze',
      "function se336UVLayout(mesh, canvas)",
      "function se336SurfaceAnalysis(mesh, canvas)",
      'se345AtlasPreview()',
      'data-se320-history="undo"'
    ]
    for needle in expected:
        if needle not in html:raise AssertionError(('v11.356 runtime',needle))
    for needle in ['function se356UVRender()', 'function se356UVResolve(u,v)',
                   'se336UVLayout(target.mesh,guide)',
                   'se336SurfaceAnalysis(target.mesh,layer)',
                   'function se356UVPick3D(event)',
                   'se356UVMarkerClear()',
                   'se356UVPreviewSchedule()']:
        if needle not in js:raise AssertionError(('v11.356 UV preview',needle))
    html=once(html,'  function ensurePanel(){',js+'\n  function ensurePanel(){')
    assert html.index('</head>')<html.index('<body')
    html=html.replace('</head>','<style id="se356UVPreviewStyle">\n'+css+'\n</style>\n</head>',1)
    for old,new in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_355_MODEL_UV_POPUP',MARKER),
      ('ENGINE · MAKER v11.355','ENGINE · MAKER v11.356'),
      ('v11.355 · separate Model Studio UV editor popup',
       'v11.356 · precise UV preview and XR camera orbit'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.355'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.356'"),
      ('<title>§wyrl§ Engine · Maker v11.355</title>',
       '<title>§wyrl§ Engine · Maker v11.356</title>')
    ]:
        html=once(html,old,new)
    old=" source.engine='§wyrl§ Engine · Maker v11.355';source.version=11.355;"
    assert html.count(old)==3
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.356';source.version=11.356;")
    key='const SE_RELEASE_NOTES='
    at=html.index(key)+len(key)
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    if not any(h.get('version')=='v11.355' for h in notes.get('history',[])):
        notes.setdefault('history',[]).insert(0,{'version':'v11.355','changes':notes.get('changes',[])})
    notes.update(version='v11.356',date='2026-11-08',
      title='UV surface mapping preview and immersive VR camera orbit',
      changes=[
       'Position floating UV Editor below the measured Model Studio header, tabs and viewport transform bar; constrain it to the 3D viewport horizontal bounds without overlapping the left object hierarchy.',
       'Preview actual 512px mesh UV wireframe, colored front/back/left/right/top/bottom surface map and current imported painted PNG/texture slide offset, before exporting 1024px guide.',
       'Tap a UV face/region to highlight a corresponding point on the selected 3D mesh. Pick a face on the 3D model to locate its source UV, and warn when triangles overlap.',
       'In Model VR, right thumbstick yaw and vertical orbit update the tracked XR camera reference around a stationary presentation model, rather than rotating the model rig.',
       'Move/rotate/scale via right grip use the current existing selected mesh(es) only; do not select a new mesh based on grip ray hit. Trigger selection remains explicit.',
       'No changes to authored mesh UV coordinates, body rigging, game editor, source mesh geometry or model save schema. Owner phone/Quest acceptance follows verified deployment.'
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+width:]
