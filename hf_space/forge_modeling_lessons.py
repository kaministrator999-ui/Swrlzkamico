"""Bounded, source-grounded §E multi-studio guidance for §C's existing models.

Educational context, not tool access, observed ability, training weights or an
engine feature grant. The Station/Forge native host lease, approval, validated
operation schema and receipts remain the only native edit authority.

Source mapping inspected against §E main v11.231 (2026-11-02); do not infer
that a source version is the one currently hosted on the owner's device.
"""
from __future__ import annotations

import re
from typing import Any

_FORGE_WORDS = re.compile(
    r"(?:§\s*e\b|§wyrl§\s*engine|sw[yr]+lz\s*forge|"
    r"model\s+atelier|forge\s+model(?:er|ing)?|"
    r"§\s*c\s*(?:with|using|inside|for)\s*§\s*e)", re.I)
_MODEL = re.compile(
    r"\b(?:model(?:er|ing|s)?|atelier|mesh(?:es)?|sculpt(?:ing)?|"
    r"vertex|vertices|polygon|topolog(?:y|ical)|gizmo|geometry|"
    r"primitive|cube|sphere|cylinder|cone|glove|floating hand|"
    r"hand|palm|fingers?|thumb|knuckle|wolf|sheep|"
    r"group(?:ing)?|part(?:s)?|obj|export|import)\b", re.I)
_MATERIAL = re.compile(
    r"\b(?:materials?|textures?|uvs?|uv.mapping|pbr|"
    r"roughness|metalness|emissi(?:on|ve)|pattern|brush.paint|"
    r"shader|paint(?:ing)?|image.texture|normal.map)\b", re.I)
_RIG = re.compile(
    r"\b(?:rig(?:ging)?|skin(?:ning|ned)?|skeleton|bones?|"
    r"weights?|weight.paint(?:ing)?|hand.track(?:ing)?|quest.hand)\b", re.I)
_ANIMATION = re.compile(
    r"\b(?:animat(?:e|ion|ions|ing)|keyframes?|timeline|"
    r"motion|gestures?|walk.cycle|run.cycle|poses?|"
    r"clips?|retarget(?:ing)?|wave|fist)\b", re.I)
_PARTICLE = re.compile(
    r"\b(?:particles?|vfx|emitters?|motes?|"
    r"sparks?|smoke|flame|portal.shimmer|confetti|"
    r"burst|snowfall|healing.wisps?)\b", re.I)
_GAME = re.compile(
    r"\b(?:game(?:play| design| engine| editor)?|scene|"
    r"level(?:s)?|maps?|sheep.tag|buildings?|"
    r"spawn|gui|hud|menus?|actors?|"
    r"placement|camera|collision|controls?|"
    r"quest|starter.project|prefabs?)\b", re.I)
_COMPONENT = re.compile(
    r"\b(?:sculpt(?:ing)?|vertex|vertices|edges?|faces?|brush|falloff|"
    r"component|topology|gizmo|extrud(?:e|ing)|smooth(?:ing)?)\b", re.I)
_ASSEMBLY = re.compile(r"\b(?:group(?:ing)?|join|separat(?:e|ing)|assembl(?:y|ies))\b", re.I)
_HAND = re.compile(r"\b(?:glove|palm|finger|fingers|thumb|knuckle|hand|ulnar)\b", re.I)
_EXPORT = re.compile(r"\b(?:export|import|obj|save|load|json|project|undo|redo)\b", re.I)
# Only actual workspace names, not generic page labels, can focus a lesson.
_WORKSPACES = frozenset({
    "model-atelier", "scene", "game", "game-engine", "particles",
    "particle-studio", "materials", "material-studio", "material-texture",
})
_BASE = (
    "§E STUDIO REFERENCE (source-grounded instructions, NOT tool access): "
    "The native Model Atelier edits project.modelAtelier; game scene actors, "
    "currentProject.materialStudio, particleStudio and guiStudio are separate "
    "owners. §C's existing typed mesh/actor/project actions and editor.undo/redo "
    "need a fresh authorized §E host, validated approval and actual receipts. "
    "Never invent IDs, claim an edit ran or treat a proposal as a saved project."
)
_TOPICS = {
    "cross-studio": (
        "For a playable asset: plan scene/gameplay → editable model → "
        "material/texture → rig/clip → particle effects → native preview/save. "
        "Keep each studio's schema and project/selection ownership distinct. "
        "Source code, reference art and Chat proposals do not automatically "
        "create, transfer or wire assets into another studio."
    ),
    "game": (
        "Game Editor owns scene actors, placement, starter/play state and "
        "gameplay, not modeler part geometry. guiStudio has up to 24 bounded "
        "label/button/panel elements; editor-preview hide differs from Show "
        "in Play. Built-in GUI button actions are limited, not arbitrary JS. "
        "Verify actual starter/level state before changing rules or controls."
    ),
    "material": (
        "Material & Texture Studio stores up to 12 PBR materials in "
        "currentProject.materialStudio; 8 base texture types, seeded patterns, "
        "bounded paint strokes and local image import. Apply targets Game "
        "Editor actors, NOT individual Model Atelier parts. Color is not "
        "UVs, and image paint is not automatic UV unwrapping. No native §C "
        "material.create/assign action is approved."
    ),
    "particle": (
        "Particle Studio writes currentProject.particleStudio emitter definitions "
        "for the Game Editor: up to 12 emitters, 96 points per emitter and "
        "576 live points total. An attached source follows its actor while "
        "already-spawned motes remain in world space. Preview/burst and "
        "gameplay effects differ. No native §C particle.create tool exists."
    ),
    "animation": (
        "The glove has 17-bone skeletal skin weights and keyed gestures; "
        "Astra Wolf Model uses a separate 14-bone rig and 10 motion clips, "
        "while its Sheep Tag renderer animates optimized pivots. Clover's "
        "sheep preview changes part transforms, not wolf SkinnedMesh. "
        "Pose/keyframe, save and game trigger are separate; §C has no native "
        "bone or keyframe edit action."
    ),
    "rig": (
        "Native new-glove Rig Studio has 17 bones with skin weights; "
        "wolf uses 14. Old unrigged saves do not auto-convert. A reference "
        "picture is not topology, bind pose, weights or clips. Quest hand "
        "tracking is not §E motion capture. §C has no native rig.pose tool."
    ),
    "component": (
        "Model Atelier UI supports vertex/edge/face editing and "
        "sculptVertexEdits. Direct brush/extrusion writes are NOT in §C's "
        "typed allowlist; use actual UI or a reviewable engine patch."
    ),
    "assembly": (
        "Model Atelier meshGroups are non-destructive assemblies with "
        "editable members; mesh grouping is NOT a typed §C operation. "
        "Respect group/child selection and native Undo history."
    ),
    "hand": (
        "For a hand/glove, compare front/side/back/top phalanges, "
        "palm/ulnar contour, thumb saddle/web, finger taper/splay and separate "
        "armor. A primitive blockout is not finished organic topology."
    ),
    "export": (
        "Native model JSON retains editable parts/materials and eligible rigs; "
        "triangulated OBJ is not a full rigged editable project. Local "
        "project persistence and explicit cloud/account saves differ."
    ),
    "general": (
        "Inspect current native selection, workspace and project IDs before "
        "proposing bounded primitive edits. Do not confuse Game Editor actors "
        "with Model Atelier geometry or assume UI actions are Chat tools."
    ),
}


def select_modeling_lesson(
    prompt: Any,
    native_context: dict[str, Any] | None = None,
    *,
    role: str = "conversation",
) -> str:
    """Return <=1150 chars of context for a genuine §E studio turn, else ''.

    Native context is a topic hint, not permission: the caller authenticates it.
    No web/source fetch, editor action, native tool grant or model training here.
    """
    if not isinstance(prompt, str) or not prompt.strip():
        return ""
    context = native_context if isinstance(native_context, dict) else {}
    explicit_forge = bool(_FORGE_WORDS.search(prompt))
    in_native = context.get("workspace") in _WORKSPACES
    if not (explicit_forge or in_native):
        return ""
    matches = {
        "game": bool(_GAME.search(prompt)),
        "model": bool(_MODEL.search(prompt)),
        "material": bool(_MATERIAL.search(prompt)),
        "animation": bool(_ANIMATION.search(prompt) or _RIG.search(prompt)),
        "particle": bool(_PARTICLE.search(prompt)),
    }
    if not any(matches.values()):
        return ""
    if sum(matches.values()) >= 3:
        topic = "cross-studio"
    elif matches["particle"]:
        topic = "particle"
    elif matches["material"]:
        topic = "material"
    elif _ANIMATION.search(prompt):
        topic = "animation"
    elif _RIG.search(prompt):
        topic = "rig"
    elif matches["game"] and not matches["model"]:
        topic = "game"
    elif _COMPONENT.search(prompt):
        topic = "component"
    elif _ASSEMBLY.search(prompt):
        topic = "assembly"
    elif _HAND.search(prompt):
        topic = "hand"
    elif _EXPORT.search(prompt):
        topic = "export"
    elif matches["game"]:
        topic = "game"
    else:
        topic = "general"
    lesson = _BASE + " " + _TOPICS[topic]
    if role == "planner":
        lesson += (
            " Native JSON planner: unsupported operations must return "
            "disposition=clarify and an empty operations list; no new "
            "operation types are authorized."
        )
    # All current topic combinations fit; hard cap protects inference budget.
    return lesson[:1150]
