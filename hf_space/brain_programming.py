"""Brain-owned bounded programming/artifact routing for the HF candidate.

This module classifies semantic programming continuation only. It never mutates
threads, pins, artifacts, files, tools, deployments, or other operational state.
"""
from __future__ import annotations
import hashlib
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


def _extract_candidate_code(text: str) -> str:
    """Return the primary executable candidate, ignoring prose/examples/comments."""
    raw=str(text or "").strip()
    fenced=re.findall(r"```[^\n`]*\n([\s\S]*?)```",raw)
    candidate=next((part for part in fenced if part.strip()),raw)
    lines=[]
    for line in candidate.strip().splitlines():
        stripped=line.strip()
        if not stripped or stripped.startswith(("#","//","/*","*","*/")):
            continue
        lines.append(line.rstrip())
    return "\n".join(lines)



def _receipt_semantics(raw: str) -> dict[str, Any]:
    """Extract bounded, language-agnostic repair facts from compiler/test/runtime logs."""
    text=str(raw or "")
    lines=[line.strip() for line in text.splitlines() if line.strip()]
    exceptions=[]
    for match in re.finditer(r"\b([A-Za-z_][A-Za-z0-9_]*(?:Error|Exception|Failure))\b",text):
        value=match.group(1)
        if value not in exceptions: exceptions.append(value)
    exit_codes=[]
    for match in re.finditer(r"(?i)\b(?:exit(?:\s+code|\s+status)?|status)\s*[:=]?\s*(-?\d+)\b",text):
        value=int(match.group(1))
        if value not in exit_codes: exit_codes.append(value)
    failing=[]; passing=[]; mismatches=[]
    for line in lines:
        if re.search(r"(?i)\b(?:fail(?:ed|ure)?|assert(?:ion)?|mismatch|expected|actual|error)\b",line):
            failing.append(line[:500])
        elif re.search(r"(?i)\b(?:pass(?:ed)?|ok|success(?:ful)?)\b",line):
            passing.append(line[:500])
        if re.search(r"(?i)\bexpected\b",line) and re.search(r"(?i)\bactual|got|received\b",line):
            mismatches.append(line[:500])
    categories=[]
    probes=(
        ("syntax",r"(?i)syntax|parse error|unexpected token|indentationerror"),
        ("type",r"(?i)typeerror|wrong type|type mismatch"),
        ("name-or-symbol",r"(?i)nameerror|referenceerror|cannot find symbol|unresolved reference|not defined"),
        ("assertion",r"(?i)assertionerror|assertion failed|test failed|tests failed"),
        ("build",r"(?i)compilation failed|build failed|failed to compile"),
        ("runtime",r"(?i)runtimeerror|exception|traceback"),
        ("timeout",r"(?i)timeout|timed out"),
        ("behavior-mismatch",r"(?i)expected.+(?:actual|got|received)|(?:actual|got|received).+expected"),
    )
    for name,pattern in probes:
        if re.search(pattern,text): categories.append(name)
    return {
        "categories":categories[:8],"exceptionTypes":exceptions[:8],"exitCodes":exit_codes[:8],
        "failingSignals":failing[:12],"passingSignals":passing[:8],"expectedActual":mismatches[:8],
    }


def _failure_receipt_detected(text: str) -> bool:
    """Recognize common compiler, test-runner, build, runtime and CI failure logs."""
    raw=str(text or "")
    if not raw.strip():
        return False
    patterns=(
        r"\b(?:syntaxerror|typeerror|nameerror|referenceerror|assertionerror|indentationerror|runtimeerror|exception|traceback)\b",
        r"\b(?:compilation|build|link|lint|typecheck|test(?:s| suite)?)\s+(?:failed|failure|error)\b",
        r"\b(?:failed to compile|cannot find symbol|unresolved reference|undefined reference|module not found|cannot resolve)\b",
        r"(?im)^\s*(?:FAIL|FAILED|ERROR)\b",
        r"\b(?:exit(?:\s+code|\s+status)?|status)\s*[:=]?\s*[1-9]\d*\b",
        r"\b\d+\s+failed(?:,|\b)",
        r"\bexpected\b[\s\S]{0,240}\b(?:actual|got|received)\b",
        r"\b(?:actual|got|received)\b[\s\S]{0,240}\bexpected\b",
    )
    return any(re.search(pattern,raw,re.I) for pattern in patterns)


def _repair_actions(semantics: dict[str, Any]) -> list[str]:
    categories=set(str(x) for x in (semantics.get("categories") or []))
    actions=[]
    mapping=(
        ("syntax","repair parser/syntax failure at the reported source location before changing behavior"),
        ("name-or-symbol","restore or correctly resolve the reported identifier/module/symbol without renaming required public APIs"),
        ("type","trace concrete runtime types through the failing operation and change the operation or validation causing the mismatch"),
        ("assertion","map each failing assertion to the exact source operation that produces its observed value"),
        ("behavior-mismatch","change the producer of the actual value so it matches the expected contract; do not patch only the displayed example"),
        ("build","repair the failing build/compile stage while preserving unrelated build configuration"),
        ("runtime","trace the exception to its first relevant application frame and repair the causing state/operation"),
        ("timeout","remove the blocking/unbounded operation while preserving required ordering and completion semantics"),
    )
    for key,action in mapping:
        if key in categories: actions.append(action)
    if not actions:
        actions.append("use the failing receipt to identify the first concrete failing operation, then change that operation while preserving passing behavior")
    return actions[:6]


def _user_failure_evidence(prompt: str, history: list[dict[str, Any]]) -> dict[str, Any] | None:
    raw=str(prompt or "").strip()
    if not _failure_receipt_detected(raw):
        return None
    assistants=[m for m in reversed(history or []) if isinstance(m,dict) and str(m.get("role") or "")=="assistant"]
    if not assistants:
        return None
    prior=assistants[0]
    prior_text=str(prior.get("content") or prior.get("text") or "").strip()
    raw_norm=" ".join(raw.lower().split())
    prior_candidate=_extract_candidate_code(prior_text)
    prior_norm=" ".join(prior_candidate.lower().split())
    # Convergence signal: receipts can be routed perfectly while a small model
    # repeats the same candidate. Count exact normalized candidate repeats so the
    # engine can force a strategy change instead of rewarding cosmetic rewrites.
    assistant_norms=[]
    for item in history or []:
        if not isinstance(item,dict) or str(item.get("role") or "")!="assistant":
            continue
        candidate_norm=" ".join(_extract_candidate_code(str(item.get("content") or item.get("text") or "")).lower().split())
        if candidate_norm:
            assistant_norms.append(candidate_norm)
    exact_repeat_count=sum(1 for candidate_norm in assistant_norms if candidate_norm==prior_norm)
    receipt_failure_lines=[
        line.strip()[:500]
        for line in raw.splitlines()
        if re.search(r"\b(?:fail(?:ed|ure)?|assert(?:ion)?|expected|actual|mismatch|error)\b",line,re.I)
    ][:12]
    user_seed_markers=("original user seed","original seed","user seed","provided source","supplied source","baseline source","original source")
    seed_owned=any(marker in raw_norm for marker in user_seed_markers)
    assistant_owned=any(marker in raw_norm for marker in ("your code","your function","your candidate","assistant code","assistant candidate","previous response","previous assistant"))
    ownership="user-seed" if seed_owned and not assistant_owned else "previous-assistant-candidate"
    # A receipt may describe source that was never the assistant's candidate. Keep
    # that distinction explicit so a passing assistant candidate is not repaired
    # toward a failing user seed merely because it is the nearest message.
    return {
        "schema":"swrlz-user-failure-evidence-v4","kind":"execution-failure","source":"user-response",
        "evidence":raw[:6000],"receiptSourceOwnership":ownership,
        "repairTarget":ownership,
        "repairTargetMessageId":str(prior.get("id") or "") if ownership=="previous-assistant-candidate" else "",
        "previousAssistantCandidateId":str(prior.get("id") or ""),
        "previousAssistantCandidateComparable":bool(prior_norm),
        "exactCandidateRepeatCount":exact_repeat_count,
        "stalledRepair":exact_repeat_count>=1,
        "failureSignals":receipt_failure_lines,
        "receiptSemantics":_receipt_semantics(raw),
        "repairActions":_repair_actions(_receipt_semantics(raw)),
    }

def _looks_like_failure_receipt(text: str) -> bool:
    return _failure_receipt_detected(text)

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
    prior_failure_history=prior_state.get("failureHistory") if isinstance(prior_state.get("failureHistory"),list) else []
    failure_history=[dict(x) for x in prior_failure_history[-3:] if isinstance(x,dict)]
    if failure_evidence:
        failure_history.append({"categories":list((failure_evidence.get("receiptSemantics") or {}).get("categories") or [])[:6],"failureSignals":list(failure_evidence.get("failureSignals") or [])[:8],"candidateFingerprint":failure_evidence.get("candidateFingerprint"),"repairActions":list(failure_evidence.get("repairActions") or [])[:6]})
        failure_history=failure_history[-4:]
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
    active_contract=prior_contract if canonical_carry else _programming_intent_contract(original_request or text,change)
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
        "intentContract":active_contract,
        "repairDirection":text[:4000] if ((failure_evidence and original_request) or canonical_carry) else "",
        "canonicalCarry":canonical_carry,
        "failureEvidence":failure_evidence,
        "failureHistory":failure_history,
        "source":"brain-router",
    }
