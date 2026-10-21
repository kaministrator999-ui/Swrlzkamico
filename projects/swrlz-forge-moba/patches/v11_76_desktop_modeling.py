"""§E v11.76 — resolve desktop gizmo travel, scale/Undo redraw,
wireframe visibility, and close-inspection camera limits without data changes.
"""
import json
from pathlib import Path
OLD='SWYRL_ENGINE_DEPLOY_MARKER: V11_75_COMPONENT_EDIT_FOUNDATIONS'
NEW='SWYRL_ENGINE_DEPLOY_MARKER: V11_76_DESKTOP_MODELING_REPAIR'
CANONICAL='const MODEL_ATELIER_CANONICAL_PROJECT='
def once(html,a,b):
    n=html.count(a)
    assert n==1,(a[:150],n)
    return html.replace(a,b,1)
def canonical(html):
    source=html.split(CANONICAL,1)[1]
    _,end=json.JSONDecoder().raw_decode(source)
    return source[:end]
def apply(html):
    before=canonical(html)
    root=Path(__file__).resolve().parents[1]
    js=(root/'runtime/model_atelier_desktop_edit_v11_76.js').read_text(encoding='utf-8')
    css=(root/'runtime/model_atelier_desktop_edit_v11_76.css').read_text(encoding='utf-8')
    html=once(html,'function atelierMeshGizmoBuild(){',js+'\nfunction atelierMeshGizmoBuild(){')
    # The pointer movement is accumulated by lock-relative deltas on desktop;
    # touch remains unchanged. Do this before component and object listeners.
    html=once(html,'  function pointerMove(e){',
      '  function pointerMove(e){\n    e=atelierDesktopVirtual(e);')
    html=once(html,'  function pointerUp(e){',
      '  function pointerUp(e){\n    e=atelierDesktopVirtual(e);')
    html=once(html,'if(atelierMeshGizmoDown(e))return;',
      "if(atelierMeshGizmoDown(e)){atelierDesktopBegin(e);return;}")
    html=once(html,'if(atelierComponentGizmoDown(e))return true;',
      "if(atelierComponentGizmoDown(e)){atelierDesktopBegin(e,'component');return true;}")
    # Unbounded mouse travel; snapshots + native checkPart are the actual
    # constraints. Both scale and motion are validated before preview.
    html=once(html,'function atelierMeshGizmoMove(e){',
      'function atelierMeshGizmoMove(e){\n if(atelierDesktopMeshMotion(e))return true;')
    # Force one full procedural rebuild only after a SCALE commit, fixing
    # composite native piñata/tail structures which otherwise refresh on Undo.
    html=once(html,'atelierMeshTransformOnlyCommit(next);',
      "atelierMeshTransformOnlyCommit(next);\n if(mode==='scale'){\n"
      "  renderParts();atelierGroupsOutline();atelierMeshToolbarRefresh();\n"
      "  atelierMeshPaintModeImmediately();\n }")
    # Wheel/+ buttons/pinch all agree on close-range access, while front/top
    # preset camera distances remain unchanged.
    html=once(html,"Math.max(atelierCameraMinDistance(),orbit.distance+Math.sign(e.deltaY)*.6)",
      "Math.max(.16,orbit.distance+Math.sign(e.deltaY)*Math.max(.045,orbit.distance*.085))")
    html=once(html,"Math.max(atelierCameraMinDistance(),orbit.distance-.9)",
      "Math.max(.16,orbit.distance-Math.max(.045,orbit.distance*.12))")
    html=once(html,
      "const atelierCameraMinDistance=()=>atelierCameraInterior?.08:(atelierDetailTarget?.4:1.2);",
      "const atelierCameraMinDistance=()=>atelierCameraInterior?.08:.16;")
    html=once(html,'  function cameraUpdate(){',
      "  function cameraUpdate(){\n"
      "    if(camera&&orbit.distance<.55&&camera.near>.018){camera.near=.018;camera.updateProjectionMatrix();}")
    # Wireframe remains nondestructive; dim 282 unrelated wires and draw
    # genuine, size-stable point markers on the selected mesh only.
    html=once(html,
      'queueMicrotask(atelierComponentRefresh);',
      'queueMicrotask(atelierComponentRefresh);queueMicrotask(atelierDesktopWireRefresh);')
    html=once(html,
      'atelierGroupsOutline();atelierSculptOverlayRefresh();atelierLassoOverlayRefresh();',
      'atelierGroupsOutline();atelierSculptOverlayRefresh();atelierLassoOverlayRefresh();\n atelierDesktopWireRefresh();')
    html=once(html,' atelierComponentInstall();',
      " atelierComponentInstall();\n atelierDesktopWireInstall(panel);")
    html=once(html,'  function close(){',
      '  function close(){\n    atelierDesktopCloseRestore();')
    # Reset desktop pointer lock after ALL event handlers run, including
    # pointerup that commits a transform; Escape also releases natively.
    html=once(html,
      ' renderer.domElement.addEventListener(\'pointercancel\',e=>{atelierComponentCancel();',
      ' renderer.domElement.addEventListener(\'pointercancel\',e=>{atelierDesktopEnd();atelierComponentCancel();')
    # Per-editor installation once. Pointer lock is optional; if unsupported,
    # the unlimited but native-validated drag still works within the viewport.
    html=once(html,'function atelierDesktopWireInstall(panel){',
      '''function atelierDesktopWireInstall(panel){
 if(!window.__atelierDesktopReleaseBound){
  window.__atelierDesktopReleaseBound=true;
  window.addEventListener('pointerup',atelierDesktopEnd,{passive:true});
  window.addEventListener('mouseup',atelierDesktopEnd,{passive:true});
  document.addEventListener('pointerlockchange',()=>{
   if(document.pointerLockElement!==renderer?.domElement)atelierDesktopDrag=null;
  });
 }''')
    assert '</head>' in html
    html=html.replace('</head>','<style id="atelierDesktopV1176">'+css+'</style>\n</head>',1)
    for a,b in (
      (OLD,NEW),
      ('ENGINE · MAKER v11.75','ENGINE · MAKER v11.76'),
      ('v11.75 · component edit foundations','v11.76 · precise desktop modeling'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.75'","window.SWRLZ_FORGE_BUILD={version:'v11.76'"),
      ('<title>§wyrl§ Engine · Maker v11.75</title>','<title>§wyrl§ Engine · Maker v11.76</title>')
    ):html=once(html,a,b)
    assert canonical(html)==before,'Canonical 283-part model was changed'
    for token in (
       'function atelierDesktopMeshMotion(e)',
       'function atelierDesktopBoundedAmount(d,raw)',
       'function atelierDesktopWireRefresh()',
       'function atelierDesktopBegin(e,kind=',
       'SWYRL_ENGINE_DEPLOY_MARKER: V11_76_DESKTOP_MODELING_REPAIR'
    ):assert token in html,token
    return html
