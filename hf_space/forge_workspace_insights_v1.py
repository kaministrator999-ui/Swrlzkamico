"""Trusted, read-only §E scene insights and compact Chat widget payloads.

Only the freshly revalidated host snapshot may supply facts. This module does
not run model output, dispatch native operations, or infer visual/physics truth.
"""
from __future__ import annotations
from collections import Counter, defaultdict
import json
import math
import re
from typing import Any

CONTRACT = "swrlz-widget-v1"
MAX_ROWS = 48


def _plain(value: Any, limit: int = 100) -> str:
    value = str(value if value is not None else "").strip()
    return "".join(c if c >= " " and c not in "\x7f\x80" else " " for c in value)[:limit]


def _quote(value: Any) -> str:
    # Labels are *data*, never model instructions or markdown/HTML markup.
    return json.dumps(_plain(value), ensure_ascii=False).replace("<", "\\u003c").replace(">", "\\u003e")


def _rows(summary: dict) -> tuple[list[dict], int, str]:
    workspace = summary.get("workspace")
    key = "meshes" if workspace == "model-atelier" else "actors"
    entries = summary.get(key) if isinstance(summary.get(key), list) else []
    items = [x for x in entries[:MAX_ROWS] if isinstance(x, dict)]
    count = summary.get("totalMeshes" if key == "meshes" else "totalActors")
    total = count if type(count) is int and count >= len(items) else len(items)
    return items, total, "Model Atelier meshes" if key == "meshes" else "scene actors"


def _finding_groups(items: list[dict]) -> list[dict]:
    names: dict[str, list[dict]] = defaultdict(list)
    locations: dict[tuple, list[dict]] = defaultdict(list)
    for item in items:
        name = _plain(item.get("name"), 100)
        if name:
            names[name].append(item)
        position = item.get("position")
        if (isinstance(position, list) and len(position) == 3
                and all(type(n) in (int, float) and math.isfinite(n) for n in position)):
            locations[tuple(round(n, 3) for n in position)].append(item)

    result = []
    for name, group in names.items():
        if len(group) < 2 or len(result) >= 5:
            continue
        result.append({
            "code": "duplicate-name", "severity": "review", "count": len(group),
            "title": "Repeated label", "subject": name,
            "evidence": f"{len(group)} sampled objects have the same displayed name.",
            "reason": "Names are not unique IDs. Repetition may be intentional for trees, buildings or character instances.",
            "nextCheck": "Use the Outliner and object IDs to confirm whether these are separate intended instances.",
        })
    for position, group in locations.items():
        if len(group) < 2 or len(result) >= 8:
            continue
        coords = ", ".join(f"{p:.3f}" for p in position)
        result.append({
            "code": "shared-position", "severity": "review", "count": len(group),
            "title": "Shared origin", "subject": coords,
            "evidence": f"{len(group)} sampled objects share the location ({coords}).",
            "reason": "A shared origin may be deliberate (terrain plus an overlay, marker, or nested object). It does not prove a collision.",
            "nextCheck": "Inspect their different types and shapes in the viewport before considering any movement.",
        })
    return result


def build_insight(summary: dict[str, Any], prompt: str = "") -> tuple[str, dict]:
    """Return a useful explanation and one presentation widget, never an edit."""
    items, total, label = _rows(summary)
    project = summary.get("project") if isinstance(summary.get("project"), dict) else {}
    level = summary.get("activeLevel") if isinstance(summary.get("activeLevel"), dict) else {}
    name = _plain(project.get("name") or "Untitled project")
    level_name = _plain(level.get("name"))
    selected_id = summary.get("selectedId")
    selected = next((r for r in items if r.get("id") == selected_id), None)
    selected_name = _plain(selected.get("name") or selected.get("id")) if selected else ""
    selected_type = _plain(selected.get("type") or selected.get("kind")) if selected else ""
    categories = Counter(_plain(item.get("type") or item.get("kind") or "other", 60) for item in items)
    types = [{"name": kind, "count": count} for kind, count in
             sorted(categories.items(), key=lambda item: (-item[1], item[0]))[:10]]
    findings = _finding_groups(items)
    inspected = len(items)
    omitted = max(0, total - inspected)
    dirty = summary.get("dirty") is True
    reasons = []
    if findings:
        if any(f["code"] == "duplicate-name" for f in findings):
            reasons.append("Repeated labels are an organization hint, not proof of duplicate geometry.")
        if any(f["code"] == "shared-position" for f in findings):
            reasons.append("Shared coordinates can reflect intentional layered scene objects, not a verified overlap defect.")
    else:
        reasons.append("No repeated labels or shared origins were found in the inspected sample; that does not validate the full scene.")
    if omitted:
        reasons.append(f"The remaining {omitted} objects were not inspected, so no conclusion covers the entire scene.")
    recommendations = []
    if dirty:
        recommendations.append({"title": "Preserve the current edits", "why": "The editor reports unsaved changes.", "check": "Save a native project copy before optional manual experiments."})
    if selected:
        recommendations.append({"title": "Inspect the selected object", "why": "The current selection is " + selected_name + ".", "check": "Compare its Outliner identity and transform with what is visible in the viewport."})
    if any(f["code"] == "duplicate-name" for f in findings):
        recommendations.append({"title": "Review repeated labels", "why": "Several sampled actors share labels but not necessarily identity.", "check": "Check the Outliner for separate instances; rename only if navigation is confusing."})
    if any(f["code"] == "shared-position" for f in findings):
        recommendations.append({"title": "Check co-located objects", "why": "Multiple sampled objects have matching XYZ origins.", "check": "Inspect the actual meshes and their intended layering before deciding on a fix."})
    if omitted:
        recommendations.append({"title": "Inspect more of the scene", "why": f"Only {inspected} of {total} objects were sampled.", "check": "Select an object elsewhere in the Outliner and analyze again to bring it into the bounded snapshot."})
    if not recommendations:
        recommendations.append({"title": "Verify the scene visually", "why": "Metadata alone cannot establish render, collision or animation correctness.", "check": "Inspect the viewport or run a separate explicit gameplay test."})
    recommendations = recommendations[:4]
    widget = {
        "contract": CONTRACT, "kind": "forge-workspace", "title": "§e Workspace Intelligence",
        "provider": "Verified editor snapshot",
        "data": {
            "schema": "swrlz-forge-workspace-insights-v1",
            "project": name, "level": level_name, "workspace": _plain(summary.get("workspace"), 30),
            "mode": _plain(summary.get("mode"), 20), "total": total, "sampled": inspected,
            "unit": label, "dirty": dirty, "selection": selected_name,
            "selectedType": selected_type, "types": types, "findings": findings,
            "recommendations": recommendations,
            "limitations": "Read-only metadata. No visual, physics, runtime gameplay or collision verification.",
        },
    }
    lines = [
        f"**§e workspace review:** {_quote(name)}" + (f" · Level {_quote(level_name)}" if level_name else ""),
        f"The current §e workspace contains {total} {label}; {inspected} object records were inspected.",
        ("There are unsaved editor changes." if dirty else "The editor has no unsaved changes.") if type(summary.get("dirty")) is bool else "Save status was not supplied.",
        ("Selected: " + _quote(selected_name) + (f" ({_quote(selected_type)})" if selected_type else "") + ".")
        if selected else ("The selected object is outside the bounded summary." if selected_id else "No object is selected."),
    ]
    starters = summary.get("starters")
    if isinstance(starters, list) and starters:
        names = [_quote(item.get("name") or item.get("id")) for item in starters
                 if isinstance(item, dict)][:3]
        extra = max(0, len(starters) - len(names))
        if names:
            lines.append("Available starters (preview): " + "; ".join(names)
                         + (f" · and {extra} more in the project picker." if extra else "."))
    if findings:
        lines.append("**What stands out:** " + " ".join(reasons))
        lines.append("**Evidence to review:** " + "; ".join(
            f"{f['evidence']} {f['reason']}" for f in findings[:3]
        ))
    else:
        lines.append("**What stands out:** " + " ".join(reasons))
    request = re.sub(r"\s+", " ", str(prompt or "")).lower()
    if re.search(r"why|explain|reason|meaning|duplicate|repeat|overlap|same position|concern", request):
        focus = findings[0] if findings else None
        if "position" in request or "overlap" in request:
            focus = next((f for f in findings if f["code"] == "shared-position"), focus)
        elif "name" in request or "duplicate" in request or "repeat" in request:
            focus = next((f for f in findings if f["code"] == "duplicate-name"), focus)
        if focus:
            lines.append("**Reasoning continuation:** " + focus["evidence"] + " " + focus["reason"]
                         + " Next check: " + focus["nextCheck"])
        else:
            lines.append("**Reasoning continuation:** No matching concern appears in this fresh sample; a previous finding may refer to a different level or unsampled object.")
    elif re.search(r"next|improv|priorit|continue|recommend|what should|focus", request):
        lines.append("**Reasoning continuation:** The next useful action is to confirm the highest-evidence scene detail before making any changes.")
    lines.append("**Suggested next check:** " + recommendations[0]["check"])
    if omitted:
        lines.append(f"This is bounded metadata: {inspected} of {total} objects were sampled, not a full-project audit.")
    else:
        lines.append("This is bounded metadata, not a visual or gameplay audit.")
    lines.append("No objects were modified by this analysis. All findings are review hints, not verified bugs.")
    return "\n\n".join(lines), widget
