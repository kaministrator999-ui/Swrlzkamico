"""Strict reviewable model-proposed project plan, never an executable instruction.

The source is an existing COMPLETE assistant message in the caller's Station
thread. Parsing/preview does not accept file contents, create a workspace, call
a model, or authorize any source or deployment action.
"""
from __future__ import annotations

import hashlib
import json
import re
from typing import Any

from staged_workspaces import WorkspaceError, manifest

SCHEMA = "swrlz-project-manifest-v1"
MAX_SOURCE_CHARS = 26000
_LANG = re.compile(r"^[a-zA-Z0-9+#_.-]{1,24}$")
_FENCE = re.compile(r"^\x60{3}swrlz-project-manifest[ \t]*\r?\n([\s\S]*?)\r?\n\x60{3}[ \t]*$", re.M)


class PlanError(ValueError):
    pass


def source_sha(text: str) -> str:
    return hashlib.sha256(str(text).encode("utf-8")).hexdigest()


def parse_plan(text: str) -> dict:
    if not isinstance(text, str) or not 1 <= len(text) <= MAX_SOURCE_CHARS:
        raise PlanError("Plan response is missing or exceeds the source cap")
    matches = list(_FENCE.finditer(text))
    if len(matches) != 1:
        raise PlanError("Exactly one swrlz-project-manifest fenced JSON block is required")
    raw = matches[0].group(1)
    if len(raw.encode("utf-8")) > 18000:
        raise PlanError("Plan exceeds the JSON byte cap")
    try:
        document = json.loads(raw, parse_constant=lambda _: (_ for _ in ()).throw(ValueError("Non-finite JSON")))
    except (ValueError, TypeError) as exc:
        raise PlanError("Manifest is not valid strict JSON") from exc
    if not isinstance(document, dict) or document.get("schema") != SCHEMA:
        raise PlanError("Invalid project manifest schema")
    title = document.get("title")
    goal = document.get("goal")
    if not isinstance(title, str) or not 1 <= len(title.strip()) <= 90:
        raise PlanError("Project title is required and must fit 90 characters")
    if goal is not None and (not isinstance(goal, str) or len(goal) > 600):
        raise PlanError("Invalid bounded project goal")
    entries = document.get("files")
    if not isinstance(entries, list):
        raise PlanError("Plan requires a files list")
    try:
        paths = manifest([x.get("path") if isinstance(x, dict) else None for x in entries])
    except WorkspaceError as exc:
        raise PlanError(str(exc)) from exc
    names = {p.casefold(): p for p in paths}
    files = []
    for item, canonical in zip(entries, paths):
        language = item.get("language")
        depends = item.get("dependsOn", [])
        purpose = item.get("purpose", "")
        if not isinstance(language, str) or not _LANG.fullmatch(language):
            raise PlanError("Every planned file must declare a safe programming language")
        if not isinstance(purpose, str) or len(purpose) > 220:
            raise PlanError("File purpose exceeds cap")
        if not isinstance(depends, list) or len(depends) > 31:
            raise PlanError("Invalid dependency list")
        edges = []
        seen = set()
        for raw_dep in depends:
            if not isinstance(raw_dep, str):
                raise PlanError("Dependency must reference a filename")
            dep = names.get(raw_dep.casefold())
            if dep is None or dep == canonical or dep.casefold() in seen:
                raise PlanError("Unknown, self-referential or repeated dependency")
            seen.add(dep.casefold())
            edges.append(dep)
        files.append({"path": canonical, "language": language,
                      "purpose": purpose.strip(), "dependsOn": edges})

    by_name = {x["path"]: x for x in files}
    ordered = []
    remaining = set(by_name)
    while remaining:
        next_entry = next((item for item in files
                           if item["path"] in remaining and
                           all(dep not in remaining for dep in item["dependsOn"])), None)
        if next_entry is None:
            raise PlanError("File dependency graph contains a cycle")
        ordered.append(next_entry["path"])
        remaining.remove(next_entry["path"])

    plan = {"schema": SCHEMA, "title": title.strip(),
            "goal": str(goal or "")[:600], "files": files,
            "generationOrder": ordered}
    digest = hashlib.sha256(json.dumps(plan,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode("utf-8")).hexdigest()
    plan["planSha256"] = digest
    return plan


def next_ready_paths(plan: dict[str, Any], completed_paths: list[str]) -> list[str]:
    if not isinstance(plan, dict) or plan.get("schema") != SCHEMA:
        raise PlanError("Missing reviewed plan")
    done = set(completed_paths)
    return [name for name in plan.get("generationOrder", [])
            if name not in done
            and all(dep in done for file in plan["files"] if file["path"] == name for dep in file["dependsOn"])]


def file_contract(plan: dict[str, Any], path: str) -> dict | None:
    if not isinstance(plan, dict) or plan.get("schema") != SCHEMA:
        raise PlanError("Missing reviewed plan")
    return next((entry for entry in plan.get("files", []) if entry["path"] == path), None)
