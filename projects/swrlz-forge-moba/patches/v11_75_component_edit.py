"""§E v11.75 — Vertex/Edge/Face component edit via native indexed sculpt history.
Extends v11.74 without modifying the canonical 283-part project.
"""
import json
from pathlib import Path

OLD='SWYRL_ENGINE_DEPLOY_MARKER: V11_74_NONDESTRUCTIVE_MESH_GROUPS'
NEW='SWYRL_ENGINE_DEPLOY_MARKER: V11_75_COMPONENT_EDIT_FOUNDATIONS'
CANONICAL='const MODEL_ATELIER_CANONICAL_PROJECT='

def once(html,old,new):
    n=html.count(old)
    assert n==1,(old[:150],n)
    return html.replace(old,new,1)

def scene(html):
    assert html.count(CANONICAL)==1
    raw=html.split(CANONICAL,1)[1]
    _,end=json.JSONDecoder().raw_decode(raw)
    return raw[:end]

def apply(html):
    before=scene(html)
    root=Path(__file__).resolve().parents[1]
    js=(root/'runtime/model_atelier_components_v11_75.js').read_text(encoding='utf-8')
    css=(root/'runtime/model_atelier_components_v11_75.css').read_text(encoding='utf-8')
    html=once(html,'function atelierMeshGizmoBuild(){',
        js+'\nfunction atelierMeshGizmoBuild(){\n'
        " if(atelierComponentMode!=='mesh'){atelierComponentGizmoBuild();return;}")
    # Preserve the original gizmo's pointer dispatch for full meshes and
    # grouping, while routing component transforms through indexed vertices.
    for hook,func in (
      ('GizmoDown','atelierComponentGizmoDown'),
      ('GizmoMove','atelierComponentGizmoMove'),
      ('GizmoUp','atelierComponentGizmoUp')
    ):
        prefix='function atelierMesh'+hook+'(e){'
        html=once(html,prefix,prefix+"\n if(atelierComponentMode!=='mesh')return "+func+"(e);")
    # A component tap, box or lasso must not be intercepted by the native
    # object-picker or the camera's pointer-up selection handler.
    for event in ('Down','Move','Up'):
        prefix='  function pointer'+event+'(e){'
        html=once(html,prefix,prefix+'\n    if(atelierComponentPointer'+event+'(e))return;')
    html=once(html,
      "renderer.domElement.addEventListener('pointercancel',e=>{atelierMeshGizmoCancel();",
      "renderer.domElement.addEventListener('pointercancel',e=>{atelierComponentCancel();atelierMeshGizmoCancel();")
    # Mesh/Group selector remains authoritative for part choice.
    html=once(html,
      ' atelierGroupsUIRefresh();\n}\nfunction atelierGroupsOutline(){',
      ' atelierGroupsUIRefresh();\n if(atelierComponentMode!==\'mesh\')atelierComponentRefresh();\n}\nfunction atelierGroupsOutline(){')
    # Rebuild component overlay only when original model geometry changes.
    html=once(html,
      'queueMicrotask(atelierGroupsOutline);',
      'queueMicrotask(atelierGroupsOutline);queueMicrotask(atelierComponentRefresh);')
    html=once(html,' atelierGroupsInstall(panel);',
      ' atelierGroupsInstall(panel);\n atelierComponentInstall();')
    # Release resources and stale state when the editor closes.
    html=once(html,'  function close(){',
      "  function close(){\n    atelierComponentCancel();atelierComponentOverlayClear();\n"
      "    atelierComponentMode='mesh';atelierComponentIds=[];atelierComponentPartId=null;\n")
    assert '</head>' in html
    html=html.replace('</head>','<style id="atelierComponentsV1175">'+css+'</style>\n</head>',1)
    for old,new in (
      (OLD,NEW),
      ('ENGINE · MAKER v11.74','ENGINE · MAKER v11.75'),
      ('v11.74 · reversible mesh assemblies','v11.75 · component edit foundations'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.74'","window.SWRLZ_FORGE_BUILD={version:'v11.75'"),
      ('<title>§wyrl§ Engine · Maker v11.74</title>','<title>§wyrl§ Engine · Maker v11.75</title>')
    ):
        html=once(html,old,new)
    assert scene(html)==before,'Canonical source model modified'
    assert html.count(NEW)==1
    for function in (
      'atelierComponentInstall()','atelierComponentChoose(id)',
      'atelierComponentCommit(d)','atelierComponentGizmoDown(e)',
      'atelierComponentRegionPick(points,tool)'
    ):
        assert html.count('function '+function)==1,function
    return html
