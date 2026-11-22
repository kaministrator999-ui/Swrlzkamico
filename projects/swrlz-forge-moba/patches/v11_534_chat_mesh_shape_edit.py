"""§E v11.534 adds an opt-in in-place native mesh reshape action for §C."""
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PREVIOUS = "SWYRL_ENGINE_DEPLOY_MARKER: V11_533_PROJECT_ACCOUNT_OPEN"
MARKER = "SWYRL_ENGINE_DEPLOY_MARKER: V11_534_CHAT_MESH_SHAPE_EDIT"


def one(text, before, after):
    count = text.count(before)
    if count != 1:
        raise AssertionError(("v11.534", count, before[:120]))
    return text.replace(before, after, 1)


def section(runtime, name):
    return runtime.split(f"/* SE534_{name}_START */", 1)[1].split(f"/* SE534_{name}_END */", 1)[0]


def apply_mesh_shape_edit(html):
    runtime = (ROOT / "runtime/chat_mesh_shape_edit_v11_534.js").read_text("utf8")
    shared = section(runtime, "SHARED")
    html = one(html, "function seChatAtelierApply(op){",
               shared + section(runtime, "ATELIER") + "\nfunction seChatAtelierApply(op){")
    html = one(html, "  if(op.op.startsWith('rig.'))return seChatRigApply(op);",
               "  if(op.op==='mesh.reshape')return se534ChatReshape(op);\n"
               "  if(op.op.startsWith('rig.'))return seChatRigApply(op);")
    html = one(html, "gizmoAccess:se431GizmoAccess,chatAction:seChatAtelierApply,",
               "gizmoAccess:se431GizmoAccess,chatShapeEditable:se534ChatShapeEditable,chatAction:seChatAtelierApply,")
    html = one(html, "setRingAnchor,selectRing,preview,apply,cancel});",
               "setRingAnchor,selectRing,preview,apply,cancel,hasGeometryPreview:()=>!!active});")
    html = one(html, "function validateOperation(op,ctx){",
               shared + section(runtime, "HOST") + "\nfunction validateOperation(op,ctx){")
    html = one(html, "if(!op||typeof op!=='object'||Array.isArray(op))throw Error('INVALID_OPERATION');",
               "if(!op||typeof op!=='object'||Array.isArray(op))throw Error('INVALID_OPERATION');\n"
               "  if(op.op==='mesh.reshape')return se534ValidateShapeEdit(op,ctx);")
    html = one(html, "  const sampledRows=workspace==='model-atelier'?value.meshes:value.actors;while(new TextEncoder().encode(JSON.stringify(value)).length>24000&&sampledRows.length>1)sampledRows.pop();",
               """  const sampledRows=workspace==='model-atelier'?value.meshes:value.actors;
  if(workspace==='model-atelier'&&!scratch&&value.mode==='edit')value.meshShapeEdit=se534ShapeCapability(sampledRows);
  while(new TextEncoder().encode(JSON.stringify(value)).length>24000&&sampledRows.length>1){
    const removed=sampledRows.pop();
    if(value.meshShapeEdit)value.meshShapeEdit.editableIds=value.meshShapeEdit.editableIds.filter(id=>id!==removed.id);
  }
  """)
    anchor = "    for(const op of taken.operations)validateOperation(op,before);"
    return one(html, anchor,
               "    if(taken.operations.length!==1&&taken.operations.some(op=>op?.op==='mesh.reshape'))\n"
               "      throw Error('RESHAPE_REQUIRES_SEPARATE_BATCH');\n" + anchor)


def apply(html):
    html = apply_mesh_shape_edit(html)
    for before, after in (
        (PREVIOUS, MARKER),
        ("ENGINE · MAKER v11.533", "ENGINE · MAKER v11.534"),
        ("v11.533 · verified account project opening", "v11.534 · native in-place mesh reshaping for §Chat"),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.533'", "window.SWRLZ_FORGE_BUILD={version:'v11.534'"),
        ("<title>§wyrl§ Engine · Maker v11.533</title>", "<title>§wyrl§ Engine · Maker v11.534</title>"),
    ):
        html = one(html, before, after)
    provenance = " source.engine='§wyrl§ Engine · Maker v11.533';source.version=11.533;"
    assert html.count(provenance) == 5
    html = html.replace(provenance, provenance.replace("11.533", "11.534"))
    start = html.index("const SE_RELEASE_NOTES=") + len("const SE_RELEASE_NOTES=")
    notes, width = json.JSONDecoder().raw_decode(html[start:])
    notes["history"] = [item for item in notes["history"] if item.get("version") != "v11.533"]
    notes["history"].insert(0, {"version": "v11.533", "changes": notes["changes"]})
    notes.update(version="v11.534", date="2026-11-22", title="Native mesh reshaping for §Chat", changes=[
        "§E can advertise an in-place reshape of one plain primitive or loft from the verified account project editor snapshot.",
        "One reviewed native operation changes the geometry while retaining the mesh ID, transform, material, group and document references.",
        "Existing Undo and account persistence keep the updated geometry. Edited, painted, rigged and topology meshes remain protected.",
        "The new capability requires compatible §Chat planning and exact plan approval.",
    ])
    release = json.dumps(notes, ensure_ascii=False, separators=(",", ":")).replace("</", r"<\/")
    return html[:start] + release + html[start + width:]
