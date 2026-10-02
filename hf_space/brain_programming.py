"""Brain-owned bounded programming/artifact routing for the HF candidate.

This module classifies semantic programming continuation only. It never mutates
threads, pins, artifacts, files, tools, deployments, or other operational state.
"""
from __future__ import annotations
from typing import Any
import re

_CODE_TERMS=("code","html","css","javascript","typescript","python","kotlin","java","cpp","c++","function","class","file","project","api","server","bug","compile","website","webpage","web page","frontend","ui","interface","dom","responsive","layout","component","debug","syntax")
_NEW_PROJECT=("separate project","separately","new project","another project","different project","from scratch","unrelated project")
_FIX=("fix","bug","broken","error","issue","repair","patch")
_REFACTOR=("refactor","clean up","cleanup","restructure","optimize")
_FEATURE=("add","implement","feature","support","extend","include")
_REVIEW=("review","audit","inspect","check this","find the error","find the bug","what is wrong","validate","verify")
_EXPLAIN=("explain","what does","how does","walk me through")
_CONTINUATION=("this","that","it","same","previous","pinned","code","file","project","continue","keep going","update","change","modify")


CODE_TRUTH_POLICY = """[SWRLZ_CODE_TRUTH v2]
Original request = acceptance contract. Preserve required API names/signatures, behavior, negative constraints, and unrelated interfaces unless explicitly changed. Repair the smallest necessary surface.
Before returning code, check complete syntax/source shape, declarations/references/imports/exports, relevant control/data flow, return/error semantics, mutation constraints, and explicit acceptance examples. Python: distinguish bool from exact built-in int when required. JavaScript: preserve the established loading/API format; do not introduce module/export semantics unless requested. UI: verify DOM wiring, layout/overflow/reachability and accessibility. Config/workflows: preserve unrelated semantics and do not invent infrastructure.
Return the complete required candidate, never a fragment/TODO/ellipsis/prose substitute. Explanations must match the literal code. Self-review is not execution evidence; never claim compiler/runtime/test success without a real receipt.
"""

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



def _strip_fenced_code(text: str) -> str:
    """Remove fenced source/test payloads before extracting natural-language requirements."""
    return re.sub(r"```[\s\S]*?```"," [CODE_PAYLOAD] ",str(text or ""),flags=re.M)


def _programming_intent_contract(prompt: str, change_class: str) -> dict[str, Any]:
    """Compile bounded acceptance requirements from prose, keeping source/test payloads separate."""
    raw=str(prompt or "").strip()
    prose=_strip_fenced_code(raw)
    clauses=[part.strip(" \t-*") for part in re.split(r"(?:\r?\n+|(?<=[.!?;])\s+)",prose) if part.strip(" \t-*") and part.strip()!="[CODE_PAYLOAD]"]
    must=[]; must_not=[]; preserve=[]; evidence=[]
    negative=re.compile(r"\b(?:must\s+not|mustn't|do\s+not|don't|never|without|avoid|no\s+)\b",re.I)
    preserve_rx=re.compile(r"\b(?:keep|preserve|unchanged|do not change|don't change|change only|only change|same\s+(?:name|signature|settings?|config|configuration|permissions?))\b",re.I)
    requirement_rx=re.compile(r"\b(?:must|should|need(?:s)?\s+to|has\s+to|have\s+to|make\s+sure|ensure|require(?:s|d)?|implement|add|fix|accept|reject|support|compile|build|test|pass)\b",re.I)
    for clause in clauses[:32]:
        item=" ".join(clause.split())[:500]
        if negative.search(item): must_not.append(item)
        elif preserve_rx.search(item): preserve.append(item)
        elif requirement_rx.search(item): must.append(item)
    if not must and raw:
        must.append("Satisfy the requested "+str(change_class or "programming")+" operation without changing unrelated behavior.")
    evidence.extend([
        "technical-validity: returned candidate must be complete and syntactically/build valid when applicable",
        "intent-validity: original requirements and preservation constraints must be rechecked after every repair",
        "api-validity: required wrapper/name/signature must remain present unless explicitly changed",
    ])
    return {
        "schema":"swrlz-programming-intent-contract-v2","originalRequest":raw[:4000],
        "must":must[:16],"mustNot":must_not[:16],"preserve":preserve[:16],
        "acceptanceEvidence":evidence,
        "completionRule":"done only when complete-source, technical validity, and intent validity all pass",
    }


def _user_failure_evidence(prompt: str, history: list[dict[str, Any]]) -> dict[str, Any] | None:
    raw=str(prompt or "").strip()
    lower=raw.lower()
    markers=("syntaxerror","typeerror","nameerror","referenceerror","error:","compilation failed","build failed","failed to compile","cannot find symbol","unresolved reference","undefined reference","exit code","test failed","tests failed","assertionerror")
    if not raw or not any(marker in lower for marker in markers):
        return None
    prior=next((m for m in reversed(history or []) if isinstance(m,dict) and str(m.get("role") or "")=="assistant"),None)
    if prior is None:
        return None
    return {"schema":"swrlz-user-failure-evidence-v3","kind":"execution-failure","source":"user-response","evidence":raw[:6000],"repairTarget":"previous-assistant-candidate","repairTargetMessageId":str(prior.get("id") or "")}


def _looks_like_failure_receipt(text: str) -> bool:
    lower=str(text or "").lower()
    markers=("syntaxerror","typeerror","nameerror","referenceerror","error:","compilation failed","build failed","failed to compile","cannot find symbol","unresolved reference","undefined reference","exit code","test failed","tests failed","assertionerror")
    return bool(text) and any(marker in lower for marker in markers)


def _original_programming_request(history: list[dict[str, Any]]) -> str:
    """Recover the earliest user request in the current coding exchange, excluding execution receipts."""
    for item in history or []:
        if not isinstance(item,dict) or str(item.get("role") or "")!="user":
            continue
        text=str(item.get("content") or item.get("text") or "").strip()
        if not text or _looks_like_failure_receipt(text):
            continue
        if any(term in _norm(text) for term in _CODE_TERMS):
            return text[:4000]
    return ""

def programming_intent(prompt: str, history: list[dict[str, Any]], pinned_context: list[dict[str, Any]], prior_state: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return bounded semantic routing metadata consumed by the Workstation."""
    text=str(prompt or "").strip()
    p=_norm(text)
    pins=_code_pins(pinned_context or [])
    failure_evidence=_user_failure_evidence(text,history or [])
    prior_state=prior_state if isinstance(prior_state,dict) else {}
    prior_contract=prior_state.get("intentContract") if isinstance(prior_state.get("intentContract"),dict) else {}
    correction_direction=bool(prior_contract) and any(x in p for x in ("still","instead","required","requirement","must","should","keep","preserve","do not","don't","wrong","incorrect","guidance","fix","repair","change only","return only"))
    canonical_carry=bool(prior_contract) and not failure_evidence and correction_direction and not any(x in p for x in _NEW_PROJECT)
    original_request=_original_programming_request(history or []) if failure_evidence else ""
    recent=" ".join(_norm(m.get("content") or m.get("text")) for m in (history or [])[-4:] if isinstance(m,dict))
    inherited=bool(pins) or any(term in recent for term in _CODE_TERMS)
    coding=any(term in p for term in _CODE_TERMS) or inherited or bool(failure_evidence)
    if not coding:
        return {
            "schema":"swrlz-programming-intent-v1",
            "codingTask":False,"projectContext":"none","changeClass":"none",
            "artifactContinuation":False,"artifactMutationRequested":False,
            "artifactTargetId":"","artifactTargetMessageId":"","baseRevision":0,
            "newProject":False,"source":"brain-router"
        }

    new_project=any(x in p for x in _NEW_PROJECT)
    if failure_evidence:
        change="fix"
    elif new_project:
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

    explicit_reference=any(x in p for x in _CONTINUATION) or any(
        _norm((value.get("path") or value.get("file") or "") if isinstance(value,dict) else value) in p
        for item in pins for value in (item.get("files") or [])
        if _norm((value.get("path") or value.get("file") or "") if isinstance(value,dict) else value)
    )
    continuation=bool(pins) and not new_project and explicit_reference
    target=_pick_artifact_target(text,pins) if continuation else None
    artifact_id=str((target or {}).get("artifactId") or "")
    target_message_id=str((target or {}).get("messageId") or "")
    base_revision=int((target or {}).get("artifactRevision") or 0)
    mutation=bool(target and change in {"fix","refactor","feature","migrate"})
    active_contract=prior_contract if canonical_carry else _programming_intent_contract(original_request or text,change)\n    return {
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
        "intentContract":active_contract,
        "repairDirection":text[:4000] if ((failure_evidence and original_request) or canonical_carry) else "",\n        "canonicalCarry":canonical_carry,
        "failureEvidence":failure_evidence,
        "source":"brain-router",
    }
