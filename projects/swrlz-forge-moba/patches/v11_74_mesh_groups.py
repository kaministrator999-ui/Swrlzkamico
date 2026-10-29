"""§E v11.74: native reversible mesh assemblies and phone multi-select.
Append-only patch. Preserve canonical model, model parts, materials and history.
"""
import json
from pathlib import Path

OLD='SWYRL_ENGINE_DEPLOY_MARKER: V11_73_INSTANT_GIZMO_ROTATION_TOUCH'
NEW='SWYRL_ENGINE_DEPLOY_MARKER: V11_74_NONDESTRUCTIVE_MESH_GROUPS'
CANONICAL='const MODEL_ATELIER_CANONICAL_PROJECT='

def once(html, before, after):
    n=html.count(before)
    assert n==1,(before[:150],n)
    return html.replace(before,after,1)

def native_model(html):
    assert html.count(CANONICAL)==1
    source=html.split(CANONICAL,1)[1]
    _,end=json.JSONDecoder().raw_decode(source)
    return source[:end]

def replace_between(html,before,after,new):
    assert html.count(before)==1,(before,html.count(before))
    assert html.count(after)==1,(after,html.count(after))
    left=html.index(before)
    right=html.index(after,left)
    assert right>left
    return html[:left]+new+'\n'+html[right:]

def apply(html):
    original=native_model(html)
    root=Path(__file__).resolve().parents[1]
    js=(root/'runtime/model_atelier_mesh_groups_v11_74.js').read_text(encoding='utf-8')
    css=(root/'runtime/model_atelier_mesh_groups_v11_74.css').read_text(encoding='utf-8')
    html=once(html,'function atelierMeshGizmoBuild(){',js+'\nfunction atelierMeshGizmoBuild(){')
    # Save exact group membership together with parts in the SAME Undo step.
    # Native modelSnapshot() already serializes the complete model envelope:
    # preserve poseFrames, existing animation assemblies and all extensions.
    assert 'function modelSnapshot(){return JSON.stringify(model());}' in html
    html=once(html,
      'dst.push(modelSnapshot());currentProject.modelAtelier=JSON.parse(src.pop());selection=null;signalEdited();',
      'dst.push(modelSnapshot());currentProject.modelAtelier=JSON.parse(src.pop());selection=null;\n'
      '    atelierMeshIds=[];atelierMeshAdding=false;atelierGroupCurrent=null;\n'
      '    signalEdited();')
    # Keep all data flow in modelAtelier; edits that destroy parts prune stale links.
    html=once(html,'  function signalEdited(){',
      '  function signalEdited(){\n    atelierGroupsPrune();\n    queueMicrotask(atelierGroupsUIRefresh);')
    # Replace the v11.65 queued selection hook. It toggled the *new* id in a
    # microtask, which loses the previous selection while multi-selecting.
    html=replace_between(html,'  function select(id){','  function applyField(key,index,value){',
      '  function select(id){atelierGroupsSelect(id);}')
    # Multi-outline selection still uses the current scene meshes, never a
    # full geometry rebuild just to add/remove a BoxHelper.
    html=once(html,'function atelierMeshSelectFast(){\n if(!modelRoot)return;',
      'function atelierMeshSelectFast(){atelierGroupsOutline();return;\n if(!modelRoot)return;')
    # New selection outlines after topology/part rebuild are recreated from
    # active group selection, with no changes to model parts themselves.
    html=once(html,'  function renderParts(){atelierRuntimeLODStart();queueMicrotask(atelierMeshToolbarRefresh);',
      '  function renderParts(){atelierRuntimeLODStart();queueMicrotask(atelierMeshToolbarRefresh);queueMicrotask(atelierGroupsOutline);')
    # Group-sensitive imports reject invalid memberships and preserve all
    # existing materials, mesh data, transforms, names and source coordinates.
    html=once(html,
      '      const assemblies=atelierValidateAssemblies(source.assemblies,source.parts);',
      "      const importedGroups=source.meshGroups??[];\n"
      "      if(!atelierGroupsValid(importedGroups,source.parts))throw Error('Invalid mesh group memberships.');\n"
      "      const assemblies=atelierValidateAssemblies(source.assemblies,source.parts);")
    html=once(html,
      'checkpoint();model().parts=structuredClone(source.parts);',
      'checkpoint();model().parts=structuredClone(source.parts);\n'
      '      model().meshGroups=structuredClone(importedGroups);\n'
      '      atelierMeshIds=[];atelierGroupCurrent=null;')
    # Existing desktop list multiple selection remains usable, but avoids
    # rebuilding the 283-part model simply to show selection outlines.
    html=once(html,
      "  atelierMeshIds=ids.slice(0,32);selection=atelierMeshIds.at(-1);\n  atelierMeshAdding=false;renderParts();refreshInspector();atelierMeshToolbarRefresh();",
      "  atelierGroupsSelectFromList(ids);\n  refreshInspector();atelierMeshToolbarRefresh();atelierMeshPaintModeImmediately();")
    # The old '+ Add mesh' action reuses the SAME mobile multi-select state.
    html=once(html,
      "  else if(btn.hasAttribute('data-mesh-group')){atelierMeshAdding=!atelierMeshAdding;status(atelierMeshAdding?'Tap additional meshes in the viewport to add/remove from group.':'Group selection finished.');}",
      "  else if(btn.hasAttribute('data-mesh-group'))atelierGroupsToggleMulti();")
    html=once(html,
      ' atelierViewportTopArrange(panel);',
      ' atelierViewportTopArrange(panel);\n atelierGroupsInstall(panel);')
    html=once(html,
      ' if(!atelierMeshDrag)atelierMeshGizmoBuild();\n atelierMeshToolbarPosition();',
      ' if(!atelierMeshDrag)atelierMeshGizmoBuild();\n atelierMeshToolbarPosition();')
    assert '</head>' in html
    html=html.replace('</head>','<style id="atelierMeshGroupsV1174">'+css+'</style>\n</head>',1)
    for before,after in (
       (OLD,NEW),
       ('ENGINE · MAKER v11.73','ENGINE · MAKER v11.74'),
       ('v11.73 · responsive gizmo touch','v11.74 · reversible mesh assemblies'),
       ("window.SWRLZ_FORGE_BUILD={version:'v11.73'","window.SWRLZ_FORGE_BUILD={version:'v11.74'"),
       ('<title>§wyrl§ Engine · Maker v11.73</title>','<title>§wyrl§ Engine · Maker v11.74</title>')
    ):
       html=once(html,before,after)
    assert native_model(html)==original,'Canonical 283-part character modified'
    assert html.count(NEW)==1
    for required in ('function atelierGroupsInstall(panel)',
        'function atelierGroupCreate()','function atelierGroupsHistoryApply(entry)',
        'function atelierGroupsSelect(id)','function atelierGroupUpdateMembers()'):
       assert html.count(required)==1,required
    return html
