"""R39 hot v27: requirement-enforced artifacts + bounded repair over v26.

The explicit requirement ledger now drives an implementation acceptance contract,
Python syntax validation, unsupported-measurement detection, and one bounded repair
pass before a request is allowed to terminate as failed. Batched prefill and the
v26 planner remain unchanged.
"""
from __future__ import annotations

import ast
import re
import urllib.request

_V26_COMMIT = "6d2bd7424cf047265fb85bcecf85c13c66ed1116"
_V26_URL = f"https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/{_V26_COMMIT}/runtime_hot/r39_engine_v26.py"
_req = urllib.request.Request(_V26_URL, headers={"User-Agent": "swrlz-hot-r39-v27"})
with urllib.request.urlopen(_req, timeout=20) as _response:
    _source = _response.read(4_000_001)
if len(_source) > 4_000_000:
    raise RuntimeError("R39_V26_SOURCE_TOO_LARGE")
exec(compile(_source.decode("utf-8"), _V26_URL + "#v27", "exec"), globals(), globals())

_V26_INSPECT = globals().get("inspect_engine")
_V24_GENERATE_FOR_V27 = globals().get("_V24_GENERATE")
if not callable(_V24_GENERATE_FOR_V27):
    raise RuntimeError("R39_V27_BASE_GENERATOR_MISSING")

HOT_SERVER_VERSION = "2.1.37"
HOT_REVISION = "2.1.37-hot-requirement-repair-rmcca-direct-v27"
_impl.HOT_SERVER_VERSION = HOT_SERVER_VERSION
_impl.HOT_REVISION = HOT_REVISION

_CODE_FENCE_RE_V27 = re.compile(r"```\s*([A-Za-z0-9_+.-]*)\s*\n([\s\S]*?)```", re.M)
_PERCENT_RE = re.compile(r"\b\d+(?:\.\d+)?\s*%")
_LEXICAL_REQUEST_RE = re.compile(r"\blexical\s+relevance\s+score\b", re.I)
_NO_EXTERNAL_RE = re.compile(r"\bwithout\s+external\s+librar(?:y|ies)\b|\bno\s+external\s+librar(?:y|ies)\b", re.I)


def _python_blocks(text):
    blocks = []
    for match in _CODE_FENCE_RE_V27.finditer(str(text or "")):
        lang = (match.group(1) or "").strip().lower()
        if lang in {"", "python", "py"}:
            blocks.append(match.group(2))
    return blocks


def _python_syntax_ok(code):
    try:
        ast.parse(str(code or ""))
        return True
    except SyntaxError:
        return False


def _recent_window_in_code(code, n):
    if n is None:
        return True
    value = str(code or "")
    patterns = [
        rf"maxlen\s*=\s*{int(n)}\b",
        rf"\[\s*-{int(n)}\s*:\s*\]",
        rf"(?:recent|window|limit|max_recent|recent_limit)\w*\s*=\s*{int(n)}\b",
    ]
    return any(re.search(p, value, re.I) for p in patterns)


def _retrieval_cap_in_code(code, n):
    if n is None:
        return True
    value = str(code or "")
    patterns = [
        rf"\[\s*:\s*{int(n)}\s*\]",
        rf"(?:max_results|max_retrieved|retrieval_limit|limit|top_k|k)\w*\s*=\s*{int(n)}\b",
        rf"min\s*\([^\n)]*,\s*{int(n)}\s*\)",
    ]
    return any(re.search(p, value, re.I) for p in patterns)


def _lexical_score_in_code(code):
    value = str(code or "")
    has_score_shape = bool(re.search(r"def\s+\w*(?:score|relev|rank)\w*\s*\(", value, re.I))
    has_tokens = bool(re.search(r"\b(?:set|split|findall)\s*\(|re\.findall", value, re.I))
    has_overlap = bool(re.search(r"\.intersection\s*\(|\&|\boverlap\b|\bcommon\b", value, re.I))
    return has_score_shape and has_tokens and has_overlap


def _standard_library_only(code):
    allowed = {
        "collections", "dataclasses", "typing", "re", "math", "time", "datetime",
        "json", "heapq", "itertools", "functools", "string", "enum", "pathlib",
    }
    try:
        tree = ast.parse(str(code or ""))
    except SyntaxError:
        return False
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".", 1)[0] not in allowed:
                    return False
        elif isinstance(node, ast.ImportFrom):
            if (node.module or "").split(".", 1)[0] not in allowed:
                return False
    return True


def _artifact_acceptance_gaps(text, req, original_prompt):
    if not req.get("requireRunnableCode"):
        return []
    blocks = _python_blocks(text) if req.get("requirePython") else [m.group(2) for m in _CODE_FENCE_RE_V27.finditer(str(text or ""))]
    if not blocks:
        return ["runnable-code"]
    candidates = []
    for code in blocks:
        gaps = []
        if req.get("requirePython") and not _python_syntax_ok(code):
            gaps.append("python-syntax")
        recent = req.get("recentWindow")
        if recent is not None and not _recent_window_in_code(code, recent):
            gaps.append(f"recent-window={recent}-in-code")
        maximum = req.get("maxRetrievedOlder")
        if maximum is not None and not _retrieval_cap_in_code(code, maximum):
            gaps.append(f"retrieved-older<={maximum}-in-code")
        if _LEXICAL_REQUEST_RE.search(str(original_prompt or "")) and not _lexical_score_in_code(code):
            gaps.append("lexical-score-implementation")
        if _NO_EXTERNAL_RE.search(str(original_prompt or "")) and not _standard_library_only(code):
            gaps.append("no-external-libraries")
        candidates.append(gaps)
    if any(not gaps for gaps in candidates):
        return []
    # Return the shortest candidate's concrete deficiencies rather than every block's union.
    return min(candidates, key=len) if candidates else ["runnable-code"]


def _v27_gaps(text, req, original_prompt):
    gaps = list(_requirement_gaps(text, req))
    artifact_gaps = _artifact_acceptance_gaps(text, req, original_prompt)
    for gap in artifact_gaps:
        if gap not in gaps:
            gaps.append(gap)
    # No measured percentage may be asserted unless the user supplied one.
    if not re.search(r"\b\d+(?:\.\d+)?\s*%", str(original_prompt or "")) and _PERCENT_RE.search(str(text or "")):
        gaps.append("unsupported-percentage-claim")
    return gaps


def _implementation_contract(req, original_prompt):
    parts = []
    recent = req.get("recentWindow")
    maximum = req.get("maxRetrievedOlder")
    if recent is not None:
        parts.append(f"the runnable artifact itself must enforce a bounded recent window of exactly {recent} messages (not merely mention {recent} in prose)")
    if maximum is not None:
        parts.append(f"the runnable artifact itself must cap retrieved older messages at {maximum}")
    if _LEXICAL_REQUEST_RE.search(str(original_prompt or "")):
        parts.append("implement lexical relevance as actual token overlap/scoring logic rather than a hard-coded keyword or fixed score")
    if _NO_EXTERNAL_RE.search(str(original_prompt or "")):
        parts.append("use only the Python standard library")
    parts.append("the Python fence must parse as valid Python")
    parts.append("never invent a measured percentage, benchmark, score, version, test result, or retrieval fact")
    return "Implementation acceptance contract: " + "; ".join(parts) + "."


def _prepare_v27_payload(payload):
    prepared = _prepare_v26_payload(payload)
    req = prepared.get("_swrlzRequirementLedger") or {}
    contract = _implementation_contract(req, prepared.get("prompt"))
    existing = str(prepared.get("responseDirective") or "").strip()
    prepared["responseDirective"] = (existing + " " + contract).strip()
    prepared["_swrlzImplementationContract"] = contract
    return prepared


def _repair_payload(prepared, first_text, gaps):
    original_prompt = str(prepared.get("prompt") or "")
    req = prepared.get("_swrlzRequirementLedger") or {}
    history = list(prepared.get("history") or [])
    history.append({"role": "user", "text": original_prompt})
    history.append({"role": "assistant", "text": str(first_text or "")[-5000:]})
    repair_instruction = (
        "Repair only the unmet requirements from the previous candidate. "
        f"Unmet checks: {', '.join(gaps)}. "
        "Do not repeat already-correct architecture prose. Emit the corrected runnable artifact first if code is implicated, "
        "then only the missing example or prefill explanation if needed. The correction must be directly appendable to the final answer. "
        + _implementation_contract(req, original_prompt)
    )
    clone = dict(prepared)
    clone["prompt"] = repair_instruction
    clone["history"] = history[-32:]
    clone["responseDirective"] = (
        "This is one bounded correction pass for the same response. Output only corrected or missing final-copy sections. "
        "Do not discuss the repair process or quote internal requirements. " + repair_instruction
    )
    generation = dict(clone.get("generation") or {})
    generation["maxTokens"] = min(int(generation.get("maxTokens") or 320), 320)
    clone["generation"] = generation
    clone["_swrlzRepairPass"] = 1
    return clone


def inspect_engine():
    result = _V26_INSPECT()
    if isinstance(result, dict):
        result.update({
            "hotServerVersion": HOT_SERVER_VERSION,
            "hotRevision": HOT_REVISION,
            "requirementArtifactAcceptance": True,
            "pythonAstSyntaxGate": True,
            "recentWindowMustExistInCode": True,
            "retrievalLimitMustExistInCode": True,
            "lexicalScoreImplementationGate": True,
            "unsupportedPercentageCompletionGate": True,
            "boundedRequirementRepairPass": 1,
            "directRmccaEnvelopePreferred": True,
            "carrierRemainsFallback": True,
            "v26SourceCommit": _V26_COMMIT,
        })
    return result


def generate_events(payload, is_cancelled=None):
    prepared = _prepare_v27_payload(payload)
    req = prepared.get("_swrlzRequirementLedger") or {}
    original_prompt = str(prepared.get("prompt") or "")
    first_text = ""
    terminal_seen = False

    yield {
        "type": "STATUS",
        "phase": "IMPLEMENTATION_CONTRACT",
        "reason": "Requirement ledger is enforcing artifact semantics before successful completion; one bounded correction pass is available if necessary.",
    }

    for event in _V24_GENERATE_FOR_V27(prepared, is_cancelled):
        if not isinstance(event, dict):
            yield event
            continue
        event = dict(event)
        event_type = str(event.get("type") or "")
        if event_type == "DELTA":
            first_text += str(event.get("text") or "")
            yield event
            continue
        if event_type in {"COMPLETED", "FAILED"}:
            terminal_seen = True
            gaps = _v27_gaps(first_text, req, original_prompt)
            if not gaps and event_type == "COMPLETED":
                event["reason"] = "Local R39 generation completed and semantic artifact acceptance passed."
                yield event
                return
            # Suppress the first terminal event and repair once inside the same server generation session.
            yield {
                "type": "STATUS",
                "phase": "REQUIREMENT_REPAIR",
                "reason": f"The first candidate missed: {', '.join(gaps or ['generation-terminal'])}. Running one bounded correction pass before finalizing.",
            }
            repair = _repair_payload(prepared, first_text, gaps or ["generation-terminal"])
            repair_text = ""
            for repaired in _V24_GENERATE_FOR_V27(repair, is_cancelled):
                if not isinstance(repaired, dict):
                    yield repaired
                    continue
                repaired = dict(repaired)
                repaired_type = str(repaired.get("type") or "")
                if repaired_type == "DELTA":
                    repair_text += str(repaired.get("text") or "")
                    yield repaired
                    continue
                if repaired_type in {"COMPLETED", "FAILED"}:
                    combined = first_text + "\n" + repair_text
                    remaining = _v27_gaps(combined, req, original_prompt)
                    if remaining:
                        yield {
                            "type": "STATUS",
                            "phase": "REQUIREMENT_GUARD",
                            "reason": f"Bounded correction pass still left unmet requirements: {', '.join(remaining)}.",
                        }
                        yield {
                            "type": "FAILED",
                            "phase": "ERROR",
                            "reason": f"Generation ended after one bounded repair with unmet requirements: {', '.join(remaining)}. Valid committed text is preserved.",
                        }
                    else:
                        yield {
                            "type": "COMPLETED",
                            "phase": "COMPLETE",
                            "reason": "Generation completed after one bounded requirement repair; semantic artifact acceptance passed.",
                        }
                    return
                yield repaired
            yield {"type": "FAILED", "phase": "ERROR", "reason": "The bounded requirement repair ended without a terminal event."}
            return
        yield event

    if not terminal_seen:
        yield {"type": "FAILED", "phase": "ERROR", "reason": "Generation ended without a terminal event before requirement acceptance."}
