"""Strict optional §E studio commands for the existing native Forge bridge.

No capability is inferred from a prompt or project name: the currently leased
host must advertise this exact schema and live per-studio target IDs. These
operations remain in the existing frozen-preview, user-approval, native-receipt
pipeline. Does not create a new executor or any model training.
"""
from __future__ import annotations

import math
import re
from typing import Any

STUDIO_SCHEMA = {
    "material.create": ({"op", "preset"}, {"op", "preset"}),
    "material.set": ({"op", "id"}, {"op", "id", "name", "baseColor", "roughness", "metalness", "glow"}),
    "material.assign": ({"op", "id", "actorId"}, {"op", "id", "actorId"}),
    "particle.create": ({"op", "preset"}, {"op", "preset"}),
    "particle.set": ({"op", "id"}, {"op", "id", "name", "position", "rate", "life", "size", "startColor", "endColor"}),
    "rig.pose": ({"op", "boneId", "rotation"}, {"op", "boneId", "rotation"}),
    "rig.keyframe": ({"op", "time"}, {"op", "time", "clip"}),
}
STUDIO_LABELS = {
    "material.create": "create PBR material", "material.set": "edit PBR material",
    "material.assign": "assign material to scene actor",
    "particle.create": "create particle emitter", "particle.set": "edit particle emitter",
    "rig.pose": "pose rig bone", "rig.keyframe": "save animation keyframe",
}
MATERIAL_PRESETS = frozenset(("metal", "gold", "wood", "stone", "brick",
                              "fabric", "leather", "magic", "glass", "ceramic"))
PARTICLE_PRESETS = frozenset(("magic", "fire", "smoke", "sparks", "snow",
                              "rain", "healing", "build", "portal", "celebration"))
COLOR = re.compile(r"^#[0-9a-fA-F]{6}$")
IDENTIFIER = re.compile(r"^[a-zA-Z0-9_-]{1,90}$")
SPEC = "swrlz-forge-studio-commands-v1"


class StudioCommandError(ValueError):
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


def _fail(code: str):
    raise StudioCommandError(code)


def _rows(value: Any, limit: int) -> set[str]:
    if not isinstance(value, list) or len(value) > limit:
        _fail("FORGE_STUDIO_SNAPSHOT_INVALID")
    ids = []
    for row in value:
        if not isinstance(row, dict) or not isinstance(row.get("id"), str) or not IDENTIFIER.fullmatch(row["id"]):
            _fail("FORGE_STUDIO_SNAPSHOT_INVALID")
        ids.append(row["id"])
    if len(ids) != len(set(ids)):
        _fail("FORGE_STUDIO_SNAPSHOT_INVALID")
    return set(ids)


def _numeric(value: Any, low: float, high: float) -> bool:
    return type(value) in (float, int) and math.isfinite(value) and low <= value <= high


def _positive_name(value: Any, length: int) -> bool:
    return (isinstance(value, str) and 0 < len(value) <= length
            and bool(value.strip()) and all(ord(c) >= 32 and not 127 <= ord(c) <= 159 for c in value))


def _vector(value: Any, low: float, high: float) -> bool:
    return isinstance(value, list) and len(value) == 3 and all(_numeric(n, low, high) for n in value)


def _snapshot(summary: dict) -> dict:
    cap = summary.get("studioCommands")
    if (not isinstance(cap, dict) or cap.get("schema") != SPEC
            or summary.get("mode") != "edit"):
        _fail("FORGE_STUDIO_NOT_ADVERTISED")
    return cap


def validate_studio_operation(summary: dict, proposed: dict, count: int) -> dict:
    """Return a canonical copy, or deny before any durable batch is registered."""
    op = proposed["op"]
    if op not in STUDIO_SCHEMA:
        _fail("FORGE_STUDIO_OPERATION_NOT_ALLOWED")
    if count != 1:
        _fail("FORGE_STUDIO_SINGLE_OPERATION_REQUIRED")
    cap = _snapshot(summary)
    area = ("materials" if op.startswith("material.") else
            "particles" if op.startswith("particle.") else "rig")
    state = cap.get(area)
    workspace = summary.get("workspace")
    studio = summary.get("studio")
    if (not isinstance(state, dict) or state.get("available") is not True
            or (area == "rig" and (workspace != "model-atelier" or studio != "modeler"))
            or (area != "rig" and (workspace != "scene" or studio != area))):
        _fail("FORGE_STUDIO_WORKSPACE_MISMATCH")
    result = dict(proposed)
    if area == "materials":
        ids = _rows(state.get("items"), 12)
        if op == "material.create":
            if (not isinstance(state.get("presets"), list) or proposed["preset"] not in MATERIAL_PRESETS
                    or proposed["preset"] not in state["presets"]):
                _fail("FORGE_STUDIO_PRESET_INVALID")
            if len(ids) >= 12:
                _fail("FORGE_STUDIO_CAP_REACHED")
        else:
            if proposed["id"] not in ids:
                _fail("FORGE_STUDIO_TARGET_NOT_IN_SNAPSHOT")
        if op == "material.assign":
            actors = _rows(summary.get("actors"), 48)
            if proposed["actorId"] not in actors:
                _fail("FORGE_STUDIO_TARGET_NOT_IN_SNAPSHOT")
        if op == "material.set":
            fields = set(proposed) - {"op", "id"}
            if not fields:
                _fail("FORGE_STUDIO_EMPTY_CHANGE")
            if "name" in fields and not _positive_name(proposed["name"], 65):
                _fail("FORGE_STUDIO_INVALID_NAME")
            if "baseColor" in fields and not (isinstance(proposed["baseColor"], str)
                                              and COLOR.fullmatch(proposed["baseColor"])):
                _fail("FORGE_STUDIO_INVALID_COLOR")
            for key, maximum in (("roughness", 1), ("metalness", 1), ("glow", 3)):
                if key in fields and not _numeric(proposed[key], 0, maximum):
                    _fail("FORGE_STUDIO_INVALID_NUMBER")
    elif area == "particles":
        ids = _rows(state.get("items"), 12)
        if op == "particle.create":
            if (not isinstance(state.get("presets"), list) or proposed["preset"] not in PARTICLE_PRESETS
                    or proposed["preset"] not in state["presets"]):
                _fail("FORGE_STUDIO_PRESET_INVALID")
            if len(ids) >= 12:
                _fail("FORGE_STUDIO_CAP_REACHED")
        else:
            if proposed["id"] not in ids:
                _fail("FORGE_STUDIO_TARGET_NOT_IN_SNAPSHOT")
            fields = set(proposed) - {"op", "id"}
            if not fields:
                _fail("FORGE_STUDIO_EMPTY_CHANGE")
            if "name" in fields and not _positive_name(proposed["name"], 64):
                _fail("FORGE_STUDIO_INVALID_NAME")
            if "position" in fields and not _vector(proposed["position"], -100, 100):
                _fail("FORGE_STUDIO_INVALID_VECTOR")
            for key, low, high in (("rate", 0, 80), ("life", .1, 8), ("size", .025, .8)):
                if key in fields and not _numeric(proposed[key], low, high):
                    _fail("FORGE_STUDIO_INVALID_NUMBER")
            for color in ("startColor", "endColor"):
                if color in fields and not (isinstance(proposed[color], str)
                                             and COLOR.fullmatch(proposed[color])):
                    _fail("FORGE_STUDIO_INVALID_COLOR")
    else:
        if state.get("kind") not in ("hand", "wolf"):
            _fail("FORGE_STUDIO_RIG_INVALID")
        bones = state.get("bones")
        if (not isinstance(bones, list) or len(bones) != (17 if state["kind"] == "hand" else 14)
                or any(not isinstance(b, str) for b in bones) or len(bones) != len(set(bones))):
            _fail("FORGE_STUDIO_RIG_INVALID")
        if any(not isinstance(b, str) or not IDENTIFIER.fullmatch(b) for b in bones):
            _fail("FORGE_STUDIO_RIG_INVALID")
        if op == "rig.pose":
            if proposed["boneId"] not in bones or not _vector(
                proposed["rotation"], -2.8 if state["kind"] == "hand" else -3.14,
                2.8 if state["kind"] == "hand" else 3.14
            ):
                _fail("FORGE_STUDIO_RIG_POSE_INVALID")
        else:
            duration = state.get("duration")
            keys = state.get("keyCount")
            if not _numeric(duration, .2, 30) or type(keys) is not int or not 0 <= keys <= 64:
                _fail("FORGE_STUDIO_RIG_INVALID")
            if not _numeric(proposed["time"], 0, duration):
                _fail("FORGE_STUDIO_KEY_TIME_INVALID")
            if state["kind"] == "hand":
                if "clip" in proposed or keys >= 32:
                    _fail("FORGE_STUDIO_HAND_KEY_UNAVAILABLE")
            else:
                clips = state.get("clips")
                if (not isinstance(clips, list) or len(clips) > 16
                        or not isinstance(proposed.get("clip"), str)
                        or proposed["clip"] not in clips or proposed["clip"] != state.get("selectedClip") or keys >= 64):
                    _fail("FORGE_STUDIO_WOLF_KEY_UNAVAILABLE")
    return result
