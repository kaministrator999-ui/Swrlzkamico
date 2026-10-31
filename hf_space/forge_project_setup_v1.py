"""A bounded §e starter chooser for a user-requested new-project conversation.

The widget only proposes a selection, with no authority to mutate the editor.
Creation continues through an explicit human prompt, fresh native lease, typed
project.create and host receipt. Never use historical chat text as edit consent.
"""
from __future__ import annotations
import re
from typing import Any


def build_project_setup(summary: dict[str, Any], prompt: str = "") -> tuple[str, dict[str, Any]]:
    """Present the *current editor's* advertised starter choices, never guesses."""
    advertised = summary.get("starters") if isinstance(summary, dict) else None
    if not isinstance(advertised, list):
        raise ValueError("FORGE_PROJECT_STARTER_UNAVAILABLE")
    starters: list[dict[str, str]] = []
    seen: set[str] = set()
    for item in advertised[:16]:
        if not isinstance(item, dict):
            continue
        ident = item.get("id")
        if not isinstance(ident, str) or not re.fullmatch(r"[a-z][a-z0-9-]{0,79}", ident) or ident in seen:
            continue
        seen.add(ident)
        name = item.get("name")
        starters.append({
            "id": ident,
            "name": name[:100] if isinstance(name, str) and name.strip() else ident,
            "kind": str(item.get("kind") or "")[:60],
            "workspace": str(item.get("workspace") or "")[:60],
            "group": "fresh" if ident in ("blank-scene", "blank-model") else "starter",
        })
    if not starters:
        raise ValueError("FORGE_PROJECT_STARTER_UNAVAILABLE")
    # Suggest a starting point from the CURRENT authorized editor catalog.
    # This is presentation only: never authorize a write or invent a starter.
    from brain_forge import current_command_text
    command = current_command_text(prompt).lower()
    if re.search(r"\bsheep[\s-]+tag\b", command):
        suggested = "sheep-tag-meadow"
    elif re.search(r"\b(?:glitch\s+)?dragon(?:'s|s)?[\s-]+den\b", command):
        suggested = "glitch-dragons-den"
    elif re.search(r"\b(?:model\s+starter|starter\s+(?:3d\s+)?model)\b", command):
        suggested = "model-atelier"
    elif re.search(r"\b(?:3d\s+model|models?|sculpt(?:ure)?)\b", command):
        suggested = "blank-model"
    else:
        suggested = "blank-scene"
    if suggested not in seen:
        suggested = ""
    widget = {
        "contract": "swrlz-widget-v1",
        "kind": "forge-project-setup",
        "title": "🐉 New §e Project",
        "provider": "Current editor starter catalog",
        "data": {"schema": "swrlz-forge-project-setup-v1",
                 "currentProject": str((summary.get("project") or {}).get("name") or "Open project")[:100],
                 "starters": starters,
                 "suggestedStarterId": suggested,
                 "notice": "A separate editable local project will be created. The original project and built-in starter are preserved. Saving to your Google account is a separate action."}
    }
    return ("**Let's set up a separate §e project.** I've suggested a starting point from the editor's "
            "current catalog where your request identifies one. Give your project a name, or change the "
            "starting point. Review and press Create project; your current workspace remains untouched "
            "until §e confirms creation."), widget
