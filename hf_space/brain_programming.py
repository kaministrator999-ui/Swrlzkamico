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


CODE_TRUTH_POLICY = """[SWRLZ_CODE_TRUTH v1]
Programming is offline-first. Verify the supplied/local artifact before making confident correctness claims.
Check syntax and structure; declarations/references, scope, imports/exports, callable names, types/contracts;
trace relevant control flow, data/state mutation, returns, exceptions, async/event paths, and likely runtime failures.
Prefer concrete defects supported by the code over speculative style/API criticism. Never invent a bug, API rule,
runtime result, or no-op fix. After repairing code, re-trace the affected path and confirm the change materially
fixes the cause.

For HTML/CSS/JavaScript and local UI work also verify semantic HTML, DOM selector/reference wiring, flex/grid/
positioning, stacking contexts, overflow/intrinsic sizing, responsive/mobile/dynamic-viewport behavior,
accessibility/focus, interaction state, long-content robustness, client-side security boundaries, and avoid
unnecessary DOM/scroll/input work. For chat interfaces explicitly protect last-message clearance above an
expanded/collapsed composer, stable pinned/collapsible/code-container state across scroll/re-render,
user-controlled auto-scroll, streaming/final-state separation, roles/timestamps, mobile keyboard/safe areas,
and loading/error/empty/disconnected states.

For generated pages: derive requirements/invariants -> design regions/components -> generate HTML/CSS/JS ->
verify syntax and DOM wiring -> trace interactions/state -> check layout/scroll/overflow and responsive/
accessibility/security/performance -> repair -> re-verify.

For coding repairs and constrained edits, preserve the artifact contract before changing anything:
- extract every explicit MUST, MUST-NOT, exact name/signature, and "change only" boundary into a compact checklist;
- snapshot compatibility surfaces: function/class names, signatures, return/error semantics, workflow names/triggers,
  permissions, runtime/setup versions, existing jobs/steps, selectors, and positioning constraints that were not
  authorized to change;
- apply the smallest repair that satisfies the failed case; do not rename or replace surrounding interfaces
  unless explicitly requested;
- re-check the ORIGINAL requirements after the repair, not only the newest correction, so fixing one condition
  cannot silently regress another;
- for async JavaScript, trace promise/await ordering, HTTP-status checks, body parsing, successful return shape,
  and preservation of network-error identity separately;
- for incremental/stream parsers, explicitly model buffer += chunk, complete-record extraction, retained tail,
  blank/CRLF handling, malformed-record behavior, immediate yielding, and final unterminated input;
- for CSS/layout corrections, treat forbidden layout mechanisms such as "do not absolutely position" as hard
  negative constraints and verify reachability/overlap/viewport containment rather than substituting another
  unresolved height/position trick;
- for workflow/config edits, preserve unrelated keys byte-for-semantics and change only the requested field or
  command when asked; never invent jobs, modules, package managers, setup steps, or dependencies.
Explanations are not verification. Never claim the code performs a step unless that step exists in the returned
artifact in the required order. When runnable tools are unavailable, do a bounded mental acceptance pass and
state no execution claim.

Ordinary standalone browser/UI engineering must not require internet. Use locally supplied project code,
manifests, types, tests, docs, and examples when available. Separate artifact truth from external-provider truth:
Google, Hugging Face, OAuth, hosted SDK endpoints/scopes/versions and similar changing provider contracts may
require current authoritative evidence. Without it, design the boundary/mock/failure states but mark
provider-specific details unverified instead of inventing them.

For project/coding work, declared actions are obligations: if the assistant says it will inspect, edit, test,
clean up, deploy, verify, or otherwise perform a concrete action, do not present the work as complete until each
declared action is executed with evidence, explicitly blocked with the blocker, or legitimately deferred. Never
silently abandon a promised step or replace execution with a future-tense promise. Completion claims must match
the observable action receipts.
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
    return re.sub(r"\`\`\`[\\s\\S]*?\`\`\`"," [CODE_PAYLOAD] ",str(text or ""),flags=re.M)


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
    return {"schema":"swrlz-user-failure-evidence-v2","kind":"execution-failure","source":"user-response","evidence":raw[:6000],"repairTarget":"previous-assistant-candidate"}


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

def programming_intent(prompt: str, history: list[dict[str, Any]], pinned_context: list[dict[str, Any]]) -> dict[str, Any]:
    """Return bounded semantic routing metadata consumed by the Workstation."""
    text=str(prompt or "").strip()
    p=_norm(text)
    pins=_code_pins(pinned_context or [])
    failure_evidence=_user_failure_evidence(text,history or [])
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
        "intentContract":_programming_intent_contract(original_request or text,change),
        "repairDirection":text[:4000] if failure_evidence and original_request else "",
        "failureEvidence":failure_evidence,
        "source":"brain-router",
    }
