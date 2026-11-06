"""Negotiated native mesh data; never executable code or an authority source."""
from __future__ import annotations

import math

SCHEMA = "swrlz-forge-mesh-tools-v2"
LEGACY_KINDS = ("sphere", "box", "cone", "cylinder")
MESH_KINDS = LEGACY_KINDS + ("loft", "lathe")
GEOMETRY_FIELDS = frozenset({"path", "radii", "profile", "segments", "arcStart", "arcLength"})
FRAME_VIEWS = ("front", "back", "left", "right", "three", "hero", "top", "bottom")
MAX_OPERATIONS = 64


def mesh_tools(summary):
    """Copy only the exact versioned capability of the currently leased host.

    Unknown versions, extra fields, booleans as integers and incomplete kind
    lists fail back to the legacy adapter. Context never grants an account or
    lease: callers still independently verify that original server binding.
    """
    cap = summary.get("meshTools") if isinstance(summary, dict) else None
    if (not isinstance(cap, dict) or set(cap) != {"schema", "kinds", "maxOperations"}
            or cap.get("schema") != SCHEMA or cap.get("kinds") != list(MESH_KINDS)
            or type(cap.get("maxOperations")) is not int or cap["maxOperations"] != MAX_OPERATIONS):
        return None
    return {"schema": SCHEMA, "kinds": list(MESH_KINDS), "maxOperations": MAX_OPERATIONS}


def operation_limit(summary):
    return MAX_OPERATIONS if mesh_tools(summary) else 16


def _number(value, low, high):
    try:
        return type(value) in (int, float) and math.isfinite(value) and low <= value <= high
    except (OverflowError, ValueError):
        return False


def _points(value, count, width, bounds):
    return (isinstance(value, list) and 2 <= len(value) <= count
            and all(isinstance(p, list) and len(p) == width
                    and all(_number(n, *bounds[j]) for j, n in enumerate(p)) for p in value)
            and all(math.dist(a, b) > 1e-6 for a, b in zip(value, value[1:])))


def validate_geometry(op):
    """Mirror §E se276ShapeData exactly, retaining the original frozen values."""
    kind = op.get("kind")
    present = GEOMETRY_FIELDS & set(op)
    if kind == "loft":
        if (not _points(op.get("path"), 40, 3, [(-100, 100)] * 3)
                or not isinstance(op.get("radii"), list) or len(op["radii"]) != len(op["path"])
                or not all(_number(n, .00025, 5) for n in op["radii"])):
            return "FORGE_INVALID_LOFT_PROFILE"
        if present & {"profile", "arcStart", "arcLength"}:
            return "FORGE_UNSUPPORTED_SHAPE_FIELD"
    elif kind == "lathe":
        if (not _points(op.get("profile"), 24, 2, [(0, 5), (-100, 100)])
                or not any(p[0] > 0 for p in op["profile"])):
            return "FORGE_INVALID_LATHE_PROFILE"
        if present & {"path", "radii"}:
            return "FORGE_UNSUPPORTED_SHAPE_FIELD"
        if (("arcStart" in op and not _number(op["arcStart"], -math.tau, math.tau))
                or ("arcLength" in op and not _number(op["arcLength"], .05, math.tau))):
            return "FORGE_INVALID_LATHE_ARC"
    elif present:
        return "FORGE_UNSUPPORTED_SHAPE_FIELD"
    if "segments" in op and (type(op["segments"]) is not int or not 8 <= op["segments"] <= 64):
        return "FORGE_INVALID_MESH_SEGMENTS"
    return None


def extended_plan(operations):
    return len(operations) > 16 or any(op.get("op") == "editor.frame"
        or op.get("kind") in ("loft", "lathe") or GEOMETRY_FIELDS & set(op) for op in operations)
