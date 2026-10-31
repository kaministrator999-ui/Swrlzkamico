"""A read-only illustrative blockout for §E's existing native planner.

Proposals are UI guidance, never privileged operation payloads. Pressing Build
starts a NEW human request, fresh model plan and native context validation.
The preview is not a frozen source-of-truth plan or a rendered model.
"""
from __future__ import annotations

import re
from typing import Any
from brain_forge import current_command_text

_PREVIEW = re.compile(r"\b(?:preview|mock[ -]?up|sketch|draft|visuali[sz]e|design|propose)\b", re.I)
_TARGET = re.compile(
    r"§[eE]|\b(?:3d|model|mesh|sculpt|scene|actor|editor|atelier|object|"
    r"robot|dragon|castle|tower|bridge|house|character|statue|armor|"
    r"vehicle|tree|arch|stairs|pillar|terrain|environment)\b", re.I)
_COMPLEX = re.compile(
    r"\b(?:robot|dragon|castle|tower|bridge|house|character|statue|armor|"
    r"vehicle|tree|arch|stairs|pillar|terrain|environment|multi[ -]?part)\b", re.I)
_EXPLANATION = re.compile(
    r"^(?:how|why|what if|should|explain|teach|describe|is it possible|"
    r"can (?:you|i|we|the model|the ai))\b", re.I)
_APPLY = re.compile(r"^Apply in §e now:\s+", re.I)


def wants_preview(prompt: Any) -> bool:
    """Design intent must be in the user's CURRENT unquoted command."""
    if not isinstance(prompt, str) or not prompt.strip():
        return False
    command = current_command_text(prompt)
    if (_APPLY.search(command) or _EXPLANATION.search(command) or re.search(
            r"\b(?:do not|don't|dont|never|avoid)\s+(?:\w+\s+){0,3}"
            r"(?:preview|design|propose|make|build|create)\b", command, re.I)):
        return False
    return bool(_PREVIEW.search(command) and _TARGET.search(command))


def should_preview(prompt: Any, operations: list[dict[str, Any]]) -> bool:
    if len(operations) == 1 and operations[0]["op"] == "project.create":
        return False
    command = current_command_text(prompt) if isinstance(prompt, str) else ""
    if _APPLY.search(command):
        return False  # The user explicitly sent the fresh follow-up command.
    additions = sum(op.get("op") in ("mesh.add", "sceneactor.add") for op in operations)
    return wants_preview(prompt) or additions >= 2 or bool(_COMPLEX.search(command) and additions)


def _text(value: Any, limit: int = 120) -> str:
    return "".join(c if c >= " " and c not in "\x7f\x80" else " "
                   for c in str(value if value is not None else ""))[:limit]


def _vector(value: Any, default: list[float]) -> list[float]:
    return list(value) if isinstance(value, list) and len(value) == 3 else list(default)


def _step_command(op: dict[str, Any]) -> str:
    """Readable action words, never client-supplied JSON or executable scripts."""
    name = op["op"]
    if name == "mesh.add":
        verb = "Add a " + op["kind"] + " mesh"
    elif name == "sceneactor.add":
        verb = "Add a " + op["prefab"] + " scene actor"
    elif name == "mesh.set":
        verb = "Edit mesh ID " + op["id"]
    elif name == "sceneactor.transform":
        verb = "Transform scene actor ID " + op["id"]
    elif name == "sceneactor.rename":
        verb = "Rename scene actor ID " + op["id"]
    elif name == "mesh.remove":
        return "Delete mesh ID " + op["id"]
    elif name == "mesh.duplicate":
        return "Duplicate mesh ID " + op["id"]
    elif name.endswith(".select"):
        return "Select " + ("mesh" if name.startswith("mesh") else "scene actor") + " ID " + op["id"]
    elif name in ("editor.undo", "editor.redo"):
        return name.split(".")[1].capitalize() + " the last edit"
    else:
        return "Change " + _text(name)
    for field in ("name", "position", "rotation", "scale", "color", "material"):
        if field in op:
            verb += ", " + field + "=" + (repr(op[field]) if field != "name" else repr(_text(op[field], 100)))
    return verb


def build_preview(summary: dict[str, Any], operations: list[dict[str, Any]],
                  request: str) -> tuple[str, dict[str, Any]]:
    """UI wireframe shows approximate positions/sizes, not actual native meshes."""
    workspace = summary.get("workspace")
    entries = summary.get("meshes" if workspace == "model-atelier" else "actors")
    by_id = {item.get("id"): item for item in (entries or [])
             if isinstance(item, dict) and isinstance(item.get("id"), str)}
    steps = []
    for index, op in enumerate(operations[:16], 1):
        source = by_id.get(op.get("id")) or {}
        steps.append({
            "index": index, "op": op["op"],
            "name": _text(op.get("name") or source.get("name") or op.get("kind")
                          or op.get("prefab") or op["op"]),
            "kind": _text(op.get("kind") or op.get("prefab") or source.get("kind")
                          or source.get("type") or "object", 50),
            "position": _vector(op.get("position") or source.get("position"), [0, 0, 0]),
            "scale": _vector(op.get("scale") or source.get("scale"), [1, 1, 1]),
            "color": op.get("color") or source.get("color") or "#65d9f5",
            "material": _text(op.get("material") or source.get("material") or "", 32),
            "target": _text(op.get("id") or "", 80),
        })
    project = summary.get("project") if isinstance(summary.get("project"), dict) else {}
    # Re-approval sends a fresh NATURAL-LANGUAGE command. It is not a hidden
    # token, doesn't bypass the planner and may be rejected/replanned.
    followup = "Apply in §e now: " + "; ".join(_step_command(op) for op in operations)
    widget = {
        "contract": "swrlz-widget-v1", "kind": "forge-design-preview",
        "title": "§E Design Studio · Review",
        "provider": "Current native context + constrained model plan",
        "data": {
            "schema": "swrlz-forge-design-preview-v1",
            "project": _text(project.get("name") or "Open project"),
            "workspace": workspace, "operationCount": len(steps), "steps": steps,
            "request": _text(request, 300), "followup": followup[:3200],
            "notice": "Illustrative wireframe only—not a rendered mesh, saved scene or frozen operation. "
                      "No editor operation has run. Build starts a NEW request that re-plans and "
                      "validates against the current workspace, so compare the final result.",
        },
    }
    return ("Prepared a **reviewable §E design blockout** with " + str(len(steps)) +
            " native step" + ("" if len(steps) == 1 else "s") +
            ". The workspace has **not changed**. Inspect the interactive preview "
            "and build steps, then choose Build or revise the design."), widget
