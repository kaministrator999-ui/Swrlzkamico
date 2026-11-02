"""Small, source-grounded §E Model Atelier context selector for §C models.

This is *instructional context*, never host authority, a model training record,
a data store, or a native operation executor. The trusted Station/Forge routing,
host lease, explicit approval and native receipt contract remain unchanged.
"""
from __future__ import annotations

import re
from typing import Any

_MODEL_WORDS = re.compile(
    r"\b(?:model(?:er|ing)?|atelier|mesh(?:es)?|sculpt(?:ing)?|vertex|vertices|"
    r"polygon|topolog(?:y|ical)|uvs?|texture|rig(?:ging)?|skeleton|bone(?:s)?|"
    r"skinn(?:ing|ed)|weight(?:s|ed| painting)?|animat(?:e|ion|ing)|"
    r"glove|floating hand|hand|palm|fingers?|thumb|knuckle|gizmo|"
    r"obj|geometry|primitive|cube|sphere|cylinder|cone|"
    r"group(?:ing)?|export|import|part(?:s)?)\b", re.I)
_FORGE_WORDS = re.compile(
    r"(?:§\s*e\b|§wyrl§\s*engine|sw[yr]+lz\s*forge|"
    r"model\s+atelier|forge\s+model(?:er|ing)?)", re.I)
_SURFACE = re.compile(r"\b(?:uvs?|texture|material|paint|mapping)\b", re.I)
_RIG = re.compile(r"\b(?:rig(?:ging)?|skin(?:ning|ned)?|skeleton|bones?|"
                  r"weights?|weight.paint(?:ing)?|animat(?:e|ion|ing)|"
                  r"hand.track(?:ing)?|quest.hand)\b", re.I)
_COMPONENT = re.compile(
    r"\b(?:sculpt(?:ing)?|vertex|vertices|edges?|faces?|brush|falloff|"
    r"component|topology|gizmo|extrud(?:e|ing)|smooth(?:ing)?)\b", re.I)
_ASSEMBLY = re.compile(r"\b(?:group(?:ing)?|join|separat(?:e|ing)|assembl(?:y|ies))\b", re.I)
_HAND = re.compile(r"\b(?:glove|palm|finger|fingers|thumb|knuckle|hand|ulnar)\b", re.I)
_EXPORT = re.compile(r"\b(?:export|import|obj|save|load|json|project|undo|redo)\b", re.I)

_BASE = (
    "§E MODELER REFERENCE (source-grounded instructions, NOT tool access): "
    "The native Model Atelier stores editable parts in project.modelAtelier. "
    "Current §C live tools are mesh.add/set/select/duplicate/remove, with "
    "editor.undo/redo separately; only a fresh authorized §E host may execute "
    "approved typed operations and report real receipts. Never invent IDs, "
    "claim an edit ran, or treat a text plan as saved geometry."
)
_TOPICS = {
    "rig": (
        "Skeletal rigs, skin weights, animations and Quest hand-tracking require "
        "separate verified implementations; a reference picture or organic hand "
        "mesh is NOT a working skinned/animated hand. Do not invent rig tools."
    ),
    "component": (
        "The editor UI supports vertex/edge/face work and sculptVertexEdits, "
        "but direct component brushes/extrusions are NOT present in §C's "
        "typed native-editor allowlist. Explain the native UI or propose a "
        "reviewable engine change rather than a fictional Chat operation."
    ),
    "assembly": (
        "Editor meshGroups are non-destructive assemblies with individually "
        "editable members; grouping is NOT an approved §C native action. "
        "Respect the group's selection scope and native Undo history."
    ),
    "surface": (
        "Color/material fields on a mesh are different from true UVs, texture "
        "painting or a rig. Do not claim a reference image becomes mapped "
        "textures or weights without verified generation and assignment."
    ),
    "hand": (
        "For a hand/glove, inspect four-angle silhouettes, palm/ulnar contour, "
        "thumb saddle/web, finger phalanges, taper/splay and separate armor. "
        "A primitive blockout is not equivalent to finished organic topology."
    ),
    "export": (
        "Native model JSON retains editable parts/materials; OBJ is a "
        "triangulated exchange export, not a complete editable project/history. "
        "Local save and explicit account/cloud save have different receipts."
    ),
    "general": (
        "Use current selection, project, workspace and native part IDs. "
        "Build proportionate primitive blockouts only when fully expressible "
        "by allowlisted operations; advanced sculpting requires its own tools."
    ),
}


def select_modeling_lesson(
    prompt: Any,
    native_context: dict[str, Any] | None = None,
    *,
    role: str = "conversation",
) -> str:
    """Return a bounded lesson only for §E modeling turns, otherwise empty.

    Context is a *hint* about workspace for topic choice; this helper never
    authorizes an edit. Caller owns the authenticated-native-context boundary.
    """
    if not isinstance(prompt, str) or not prompt.strip():
        return ""
    if not _MODEL_WORDS.search(prompt):
        return ""
    context = native_context if isinstance(native_context, dict) else {}
    in_modeler = context.get("workspace") == "model-atelier"
    if not (in_modeler or _FORGE_WORDS.search(prompt)):
        return ""
    if _RIG.search(prompt):
        topic = "rig"
    elif _COMPONENT.search(prompt):
        topic = "component"
    elif _ASSEMBLY.search(prompt):
        topic = "assembly"
    elif _SURFACE.search(prompt):
        topic = "surface"
    elif _HAND.search(prompt):
        topic = "hand"
    elif _EXPORT.search(prompt):
        topic = "export"
    else:
        topic = "general"
    lesson = _BASE + " " + _TOPICS[topic]
    if role == "planner":
        lesson += (
            " For the JSON planner, unsupported operations must return "
            "disposition=clarify with an empty operations list; "
            "no extra operation types are permitted."
        )
    return lesson[:1150]
