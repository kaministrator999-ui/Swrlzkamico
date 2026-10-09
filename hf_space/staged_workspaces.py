"""Manifest-backed, process-local staged source assembly.

This module never requests model output, writes arbitrary paths to disk, or
asserts that the generated code passed a compiler. A READY package means only
that every manifest entry has a complete committed source artifact revision.
"""
from __future__ import annotations

import hashlib
import json
import re
from copy import deepcopy
from typing import Any

from code_packages import PackageError, MAX_FILES, MAX_TOTAL_BYTES, _files, safe_relative_path

SCHEMA = "swrlz-staged-code-workspace-v1"
MAX_WORKSPACES_PER_THREAD = 5


class WorkspaceError(ValueError):
    pass


class WorkspaceConflict(WorkspaceError):
    pass


def _sha(files: list[dict]) -> str:
    # Independent of order; preserve format and contents as represented in
    # workspace manifest to detect corrupted session state at download time.
    canonical = [{"path": f["path"], "language": f["language"],
                  "content": f["content"]} for f in sorted(files, key=lambda x: x["path"])]
    return hashlib.sha256(json.dumps(canonical, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")).hexdigest()


def manifest(paths: list[str]) -> list[str]:
    if not isinstance(paths, list) or not 1 <= len(paths) <= MAX_FILES:
        raise WorkspaceError("Manifest requires 1..32 file paths")
    normalized = []
    observed = set()
    for raw in paths:
        try:
            path = safe_relative_path(raw)
        except PackageError as exc:
            raise WorkspaceError(str(exc)) from exc
        if path.casefold() in observed:
            raise WorkspaceError("Duplicate file in manifest")
        observed.add(path.casefold())
        normalized.append(path)
    for child in observed:
        parts=child.split("/")
        for n in range(1,len(parts)):
            if "/".join(parts[:n]) in observed:
                raise WorkspaceError("File path cannot also be a parent directory")
    return normalized


def create_workspace(workspace_id: str, title: str, paths: list[str]) -> dict:
    if not re.fullmatch(r"workspace-[a-f0-9]{32}", workspace_id):
        raise WorkspaceError("Invalid workspace id")
    required = manifest(paths)
    return {
        "schema": SCHEMA,
        "id": workspace_id,
        "title": str(title or "Project files")[:90],
        "revision": 1,
        "state": "IN_PROGRESS",
        "requiredPaths": required,
        "files": {},
        "sourceHash": None,
        "validationState": "NOT_RUN",
    }


def _check(workspace: dict) -> None:
    if not isinstance(workspace, dict) or workspace.get("schema") != SCHEMA:
        raise WorkspaceError("Invalid workspace record")
    manifest(workspace.get("requiredPaths"))
    if workspace.get("state") not in ("IN_PROGRESS", "READY", "CANCELLED"):
        raise WorkspaceError("Invalid workspace state")
    if type(workspace.get("revision")) is not int or workspace["revision"] <= 0:
        raise WorkspaceError("Invalid workspace revision")


def _prepared(committed_files: list[dict]) -> list[dict]:
    try:
        _files(committed_files)
    except PackageError as exc:
        raise WorkspaceError(str(exc)) from exc
    prepared = []
    for src in committed_files:
        if not isinstance(src.get("language"), str) or not src["language"]:
            raise WorkspaceError("Missing code language metadata")
        if src["language"].lower() in {"lyrics", "lyric", "song", "music", "verse", "chorus"}:
            raise WorkspaceError("Music/lyric content cannot be attached as source files")
        prepared.append({"path":safe_relative_path(src["path"]),
                         "language":src["language"][:40], "content":src["content"]})
    return prepared


def attach_revision(workspace: dict, committed_files: list[dict], *,
                    artifact_id: str, artifact_revision: int, artifact_sha: str,
                    expected_revision: int) -> dict:
    """Atomic whole-artifact attachment; caller must independently authenticate source."""
    _check(workspace)
    if workspace["revision"] != expected_revision:
        raise WorkspaceConflict("Workspace revision conflict; refresh before editing")
    if workspace["state"] != "IN_PROGRESS":
        raise WorkspaceConflict("Only active workspaces accept new files")
    if not re.fullmatch(r"[a-f0-9]{64}", str(artifact_sha or "")):
        raise WorkspaceError("Missing artifact SHA")
    if type(artifact_revision) is not int or artifact_revision <= 0:
        raise WorkspaceError("Invalid source revision")
    validated = _prepared(committed_files)
    required = {p.casefold(): p for p in workspace["requiredPaths"]}
    staged = deepcopy(workspace["files"])
    for item in validated:
        path = required.get(item["path"].casefold())
        if not path:
            raise WorkspaceError("Generated source contains a path not in the required manifest")
        item["path"] = path
        item["sourceArtifactId"] = str(artifact_id or "")[:130]
        item["sourceArtifactRevision"] = artifact_revision
        item["sourceArtifactHash"] = artifact_sha
        staged[path] = item
    try:
        _files([{"path": k, "content": v["content"]} for k,v in staged.items()])
    except PackageError as exc:
        raise WorkspaceError(str(exc)) from exc
    next_state = deepcopy(workspace)
    next_state["files"] = staged
    next_state["revision"] += 1
    next_state["sourceHash"] = None
    # A file edit/replacement invalidates previously accepted external tests.
    next_state["validationState"] = "NOT_RUN"
    return next_state


def progress(workspace: dict) -> dict:
    _check(workspace)
    files = workspace.get("files")
    if not isinstance(files, dict):
        raise WorkspaceError("Invalid workspace files")
    required = workspace["requiredPaths"]
    remaining = [path for path in required if path not in files]
    project_plan = workspace.get("projectPlan")
    if project_plan:
        # Planned dependency order is advisory, but only already completed
        # source-file paths count as satisfying dependencies.
        from project_manifest import next_ready_paths
        next_paths = next_ready_paths(project_plan, list(files))
    else:
        next_paths = remaining[:1]
    return {
        "id": workspace["id"], "title": workspace["title"],
        "state": workspace["state"], "revision": workspace["revision"],
        "requiredCount": len(required), "completedCount": len(required)-len(remaining),
        "remainingPaths": remaining,
        "nextReadyPaths": next_paths,
        "hasApprovedPlan": bool(project_plan),
        "sourcePlanMessageId": str(workspace.get("sourcePlanMessageId") or "")[:160],
        "sourceHash": workspace.get("sourceHash"),
        "validationState":workspace.get("validationState") or "NOT_RUN",
    }


def finalize(workspace: dict, expected_revision: int) -> dict:
    _check(workspace)
    if workspace["revision"] != expected_revision:
        raise WorkspaceConflict("Workspace revision conflict; refresh before finalizing")
    if workspace["state"] != "IN_PROGRESS":
        raise WorkspaceConflict("Workspace already finalized or cancelled")
    status = progress(workspace)
    if status["remainingPaths"]:
        raise WorkspaceError("Incomplete workspace; required files are missing")
    files = [workspace["files"][name] for name in workspace["requiredPaths"]]
    _prepared(files)
    packed = deepcopy(workspace)
    packed["state"] = "READY"
    packed["revision"] += 1
    packed["sourceHash"] = _sha(files)
    # Packaging complete does not establish semantics, compiler PASS or tests.
    packed["validationState"] = "NOT_RUN"
    return packed


def cancel(workspace: dict, expected_revision: int) -> dict:
    _check(workspace)
    if workspace["revision"] != expected_revision:
        raise WorkspaceConflict("Workspace revision conflict")
    if workspace["state"] != "IN_PROGRESS":
        raise WorkspaceConflict("Only active workspace can be cancelled")
    result=deepcopy(workspace)
    result["state"]="CANCELLED"
    result["revision"]+=1
    return result


def downloadable_files(workspace: dict, expected_revision: int, expected_sha: str) -> list[dict]:
    _check(workspace)
    if workspace["state"] != "READY" or workspace["revision"] != expected_revision:
        raise WorkspaceConflict("Workspace is not finalized at this revision")
    required = workspace["requiredPaths"]
    try:
        files = [workspace["files"][name] for name in required]
    except (KeyError,TypeError) as exc:
        raise WorkspaceConflict("Workspace is missing required saved file") from exc
    _prepared(files)
    source = _sha(files)
    if source != expected_sha or source != workspace.get("sourceHash"):
        raise WorkspaceConflict("Workspace content integrity mismatch")
    return [{"path": f["path"], "language": f["language"],
             "content": f["content"]} for f in files]
