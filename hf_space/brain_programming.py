"""Brain-owned bounded programming/artifact routing for the HF candidate.

This module classifies semantic programming continuation only. It never mutates
threads, pins, artifacts, files, tools, deployments, or other operational state.
"""
from __future__ import annotations
from typing import Any

_CODE_TERMS=("code","html","css","javascript","typescript","python","kotlin","java","cpp","c++","function","class","file","project","api","server","bug","compile")
_NEW_PROJECT=("separate project","separately","new project","another project","different project","from scratch","unrelated project")
_FIX=("fix","bug","broken","error","issue","repair","patch")
_REFACTOR=("refactor","clean up","cleanup","restructure","optimize")
_FEATURE=("add","implement","feature","support","extend","include")
_REVIEW=("review","audit","inspect","check this")
_EXPLAIN=("explain","what does","how does","walk me through")
_CONTINUATION=("this","that","it","same","previous","pinned","code","file","project","continue","keep going","update","change","modify")


def _norm(value: Any) -> str:
    return " ".join(str(value or "").lower().split())


def _code_pins(pinned_context: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result=[]
    for item in pinned_context:
        if not isinstance(item,dict):
            continue
        text=str(item.get("text") or "")
        if item.get("artifactType")=="code" or item.get("artifactId") or "```" in text:
            result.append(item)
    return result


def _pick_artifact_target(prompt: str, code_pins: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Resolve the most applicable pinned code artifact without granting mutation authority."""
    if not code_pins:
        return None
    p=_norm(prompt)
    # Prefer an explicitly named file/path/project when that metadata is available.
    scored=[]
    for index,item in enumerate(code_pins):
        score=index  # recency remains the bounded fallback.
        for value in item.get("files") or []:
            if isinstance(value,dict):
                name=_norm(value.get("path") or value.get("file") or "")
            else:
                name=_norm(value)
            if name and name in p:
                score+=1000
        title=_norm(item.get("artifactTitle") or "")
        if title and title in p:
            score+=900
        artifact_id=_norm(item.get("artifactId") or "")
        if artifact_id and artifact_id in p:
            score+=1200
        scored.append((score,item))
    scored.sort(key=lambda pair:pair[0])
    return scored[-1][1]


def programming_intent(prompt: str, history: list[dict[str, Any]], pinned_context: list[dict[str, Any]]) -> dict[str, Any]:
    """Return bounded semantic routing metadata consumed by the Workstation."""
    text=str(prompt or "").strip()
    p=_norm(text)
    pins=_code_pins(pinned_context or [])
    recent=" ".join(_norm(m.get("content") or m.get("text")) for m in (history or [])[-4:] if isinstance(m,dict))
    inherited=bool(pins) or any(term in recent for term in _CODE_TERMS)
    coding=any(term in p for term in _CODE_TERMS) or inherited
    if not coding:
        return {
            "schema":"swrlz-programming-intent-v1",
            "codingTask":False,"projectContext":"none","changeClass":"none",
            "artifactContinuation":False,"artifactMutationRequested":False,
            "artifactTargetId":"","artifactTargetMessageId":"","baseRevision":0,
            "newProject":False,"source":"brain-router"
        }

    new_project=any(x in p for x in _NEW_PROJECT)
    if new_project:
        change="create"
    elif any(x in p for x in _FIX):
        change="fix"
    elif any(x in p for x in _REFACTOR):
        change="refactor"
    elif any(x in p for x in _FEATURE):
        change="feature"
    elif any(x in p for x in _REVIEW):
        change="review"
    elif any(x in p for x in _EXPLAIN):
        change="explain"
    else:
        change="create" if not pins else "feature"

    continuation=bool(pins) and not new_project and (
        any(x in p for x in _CONTINUATION) or change in {"fix","refactor","feature"}
    )
    target=_pick_artifact_target(text,pins) if continuation else None
    artifact_id=str((target or {}).get("artifactId") or "")
    target_message_id=str((target or {}).get("messageId") or "")
    base_revision=int((target or {}).get("artifactRevision") or 0)
    mutation=bool(target and change in {"fix","refactor","feature","migrate"})
    return {
        "schema":"swrlz-programming-intent-v1",
        "codingTask":True,
        "projectContext":"new" if new_project else ("existing" if pins else "none"),
        "changeClass":change,
        "artifactContinuation":bool(target),
        "artifactMutationRequested":mutation,
        "artifactTargetId":artifact_id,
        "artifactTargetMessageId":target_message_id,
        "baseRevision":base_revision,
        "newProject":new_project,
        "pinnedCodeArtifactCount":len(pins),
        "source":"brain-router",
    }
