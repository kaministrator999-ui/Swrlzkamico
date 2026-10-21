"""§E v11.65 selection-first native mesh tools, preserving original model data.

The floating U/V stepper retains pending values until explicitly applied.
"""
import json
from pathlib import Path

OLD='SWYRL_ENGINE_DEPLOY_MARKER: V11_64_VERSION_SMOKE_TEST'
NEW='SWYRL_ENGINE_DEPLOY_MARKER: V11_65_SELECTION_MESH_GIZMOS'
CANONICAL='const MODEL_ATELIER_CANONICAL_PROJECT='

def once(html,old,new):
    count=html.count(old)
    assert count==1,(old[:100],count)
    return html.replace(old,new,1)

def scene(html):
    assert html.count(CANONICAL)==1
    payload=html.split(CANONICAL,1)[1]
    _,end=json.JSONDecoder().raw_decode(payload)
    return payload[:end]

def apply(html):
    original=scene(html)
    js=(Path(__file__).resolve().parents[1]/'runtime/model_atelier_selection_gizmo_v11_65.js').read_text()
    css=(Path(__file__).resolve().parents[1]/'runtime/model_atelier_selection_gizmo_v11_65.css').read_text()
    html=once(html,'  function refreshList(){',js+'\n  function refreshList(){')
    html=once(html,'  function select(id){',
        '  function select(id){queueMicrotask(()=>{atelierMeshSelected(selection);refreshList();atelierMeshToolbarRefresh();});')
    html=once(html,"list.append(group);list.value=selection||'';",
        "list.append(group);list.value=selection||'';atelierMeshListSync(list);")
    html=once(html,"  function geometry(part){",
        "  function geometry(part){\n    const detail=atelierMeshPrimitiveDensityGeometry(part);if(detail)return detail;")
    html=once(html,"  function checkPart(p){",
        "  function checkPart(p){\n    if(!atelierMeshPrimitiveDensityValid(p))return false;")
    html=once(html,"  function renderParts(){atelierRuntimeLODStart();",
        "  function renderParts(){atelierRuntimeLODStart();queueMicrotask(atelierMeshToolbarRefresh);")
    html=once(html,"    atelierMobileLayoutInstall(panel);\n",
        "    atelierMobileLayoutInstall(panel);\n    atelierMeshControlsInstall(panel);\n")
    for name,hook in (
        ('pointerDown','if(atelierMeshGizmoDown(e))return;'),
        ('pointerMove','if(atelierMeshGizmoMove(e))return;'),
        ('pointerUp','if(atelierMeshGizmoUp(e))return;')
    ):
        html=once(html,'  function '+name+'(e){','  function '+name+'(e){'+hook)
    html=once(html,'  function loop(){\n    if(!renderer)return;',
        '  function loop(){\n    if(!renderer)return;atelierMeshToolbarPosition();')
    html=once(html,"renderer.domElement.addEventListener('pointercancel',e=>{atelierLassoPointerCancel(e);",
        "renderer.domElement.addEventListener('pointercancel',e=>{atelierMeshGizmoCancel();atelierLassoPointerCancel(e);")
    html=once(html,"  function close(){\n    atelierSurfacePreviewClear();",
        "  function close(){\n    atelierMeshGizmoCancel();atelierMeshGizmoClear();atelierMeshHidden=false;atelierMeshIds=[];\n    atelierSurfacePreviewClear();")
    assert '</head>' in html
    html=html.replace('</head>','<style id="atelierMeshGizmoV1165">'+css+'</style>\n</head>',1)
    for before,after in (
        (OLD,NEW),
        ('ENGINE · MAKER v11.64','ENGINE · MAKER v11.65'),
        ('v11.64 · mobile adaptive Model Atelier tools','v11.65 · selection mesh gizmos'),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.64'","window.SWRLZ_FORGE_BUILD={version:'v11.65'"),
        ('<title>§wyrl§ Engine · Maker v11.64</title>','<title>§wyrl§ Engine · Maker v11.65</title>'),
    ):
        html=once(html,before,after)
    assert scene(html)==original,'Canonical 283-part scene changed'
    assert html.count(NEW)==1
    assert html.count('function atelierMeshControlsInstall(panel)')==1
    return html
