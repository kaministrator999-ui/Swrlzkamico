"""R39 hot v25: semantic requirement ledger + truthful completion over v24.

Preserves v24 continuity, batched prefill, hard ceilings, and degeneration guards while
making explicit user obligations first-class generation constraints and refusing to
report successful completion when mandatory requirements remain unmet.
"""
from __future__ import annotations
import re
import urllib.request

_V24_COMMIT = "602ca6168173e93f8e50ccb7c6e486a5a58e888a"
_V24_URL = f"https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/{_V24_COMMIT}/runtime_hot/r39_engine_v24.py"
_req = urllib.request.Request(_V24_URL, headers={"User-Agent": "swrlz-hot-r39-v25"})
with urllib.request.urlopen(_req, timeout=20) as _response:
    _source = _response.read(4_000_001)
if len(_source) > 4_000_000:
    raise RuntimeError("R39_V24_SOURCE_TOO_LARGE")
exec(compile(_source.decode("utf-8"), _V24_URL + "#v25", "exec"), globals(), globals())

_V24_GENERATE = globals().get("generate_events")
_V24_INSPECT = globals().get("inspect_engine")

HOT_SERVER_VERSION = "2.1.35"
HOT_REVISION = "2.1.35-hot-semantic-commit-ledger-v25"
_impl.HOT_SERVER_VERSION = HOT_SERVER_VERSION
_impl.HOT_REVISION = HOT_REVISION

_MAX_RETRIEVED_RE = re.compile(r"\bat\s+most\s+(\d{1,2})\s+(?:retrieved\s+)?(?:older\s+)?messages\b", re.I)
_RECENT_WINDOW_RE = re.compile(r"\b(?:keep\s+the\s+)?(?:most\s+)?recent\s+(\d{1,3})\s+messages\b", re.I)
_CODE_REQUEST_RE = re.compile(r"\b(?:complete\s+)?runnable\s+(?:python\s+)?code\b|\bprovide\s+(?:complete\s+)?(?:runnable\s+)?(?:python\s+)?code\b", re.I)
_ARCH_FIRST_RE = re.compile(r"\bexplain\s+the\s+architecture\s+first\b", re.I)
_EXAMPLE_RE = re.compile(r"\binclude\s+(?:one\s+)?example\b|\bexample\s+conversation\b", re.I)
_PREFILL_EXPLAIN_RE = re.compile(r"\bexplain\b[^.\n]{0,120}\bprompt[- ]prefill\b|\bprompt[- ]prefill\b[^.\n]{0,120}\bcompared\b", re.I)
_PYTHON_REQUEST_RE = re.compile(r"\bpython\b", re.I)
_CODE_FENCE_RE = re.compile(r"```\s*([A-Za-z0-9_+.-]*)\s*\n([\s\S]*?)```", re.M)
_RETRIEVED_HEADING_RE = re.compile(r"^\s*retrieved\s+older\s+messages\s*:??\s*$", re.I)
_LIST_ITEM_RE = re.compile(r"^\s*(?:\d+[.)]|[-*+])\s+\S")


def _requirements(payload):
    prompt = str(payload.get("prompt") or "") if isinstance(payload, dict) else ""
    max_match = _MAX_RETRIEVED_RE.search(prompt)
    recent_match = _RECENT_WINDOW_RE.search(prompt)
    return {
        "maxRetrievedOlder": int(max_match.group(1)) if max_match else None,
        "recentWindow": int(recent_match.group(1)) if recent_match else None,
        "requireRunnableCode": bool(_CODE_REQUEST_RE.search(prompt)),
        "requirePython": bool(_PYTHON_REQUEST_RE.search(prompt) and _CODE_REQUEST_RE.search(prompt)),
        "architectureFirst": bool(_ARCH_FIRST_RE.search(prompt)),
        "requireExample": bool(_EXAMPLE_RE.search(prompt)),
        "requirePrefillExplanation": bool(_PREFILL_EXPLAIN_RE.search(prompt)),
    }


def _ledger_directive(req):
    parts = []
    if req.get("architectureFirst"):
        parts.append("architecture explanation first")
    if req.get("recentWindow") is not None:
        parts.append(f"recent always-available window={req['recentWindow']}")
    if req.get("maxRetrievedOlder") is not None:
        parts.append(f"retrieved older messages<={req['maxRetrievedOlder']}")
    if req.get("requireRunnableCode"):
        parts.append("complete runnable code required")
    if req.get("requireExample"):
        parts.append("example required")
    if req.get("requirePrefillExplanation"):
        parts.append("prompt-prefill explanation required")
    if not parts:
        return ""
    return (
        "Hard response ledger: " + "; ".join(parts) + ". "
        "Treat every ledger item as a literal obligation. Keep the architecture explanation brief, then emit the runnable artifact early. "
        "Do not exceed numeric limits, do not repeat placeholder headings, do not invent measured scores/percentages, and do not claim completion while any ledger item is unmet."
    )


def _prepare_v25_payload(payload):
    clone = dict(payload)
    req = _requirements(clone)
    directive = _ledger_directive(req)
    if directive:
        existing = str(clone.get("responseDirective") or "").strip()
        clone["responseDirective"] = (existing + " " + directive).strip()
    clone["_swrlzRequirementLedger"] = req
    return clone


def _count_retrieved_older(text):
    lines = str(text or "").splitlines()
    active = False
    count = 0
    for line in lines:
        stripped = line.strip()
        if _RETRIEVED_HEADING_RE.match(stripped):
            active = True
            continue
        if active:
            if not stripped:
                if count:
                    active = False
                continue
            if _LIST_ITEM_RE.match(line):
                count += 1
                continue
            if re.match(r"^[A-Za-z][A-Za-z0-9 /_-]{1,50}:\s*$", stripped):
                active = False
    return count


def _has_runnable_code(text, require_python=False):
    for match in _CODE_FENCE_RE.finditer(str(text or "")):
        lang = (match.group(1) or "").lower()
        code = match.group(2)
        if require_python and lang not in {"python", "py", ""}:
            continue
        if require_python:
            if re.search(r"\b(?:def|class|import|from)\b", code) and not re.search(r"^\s*(?:#.*\n?)+$", code, re.M):
                return True
        elif len(code.strip()) >= 40:
            return True
    return False


def _requirement_gaps(text, req):
    value = str(text or "")
    lower = value.lower()
    gaps = []
    maximum = req.get("maxRetrievedOlder")
    if maximum is not None and _count_retrieved_older(value) > maximum:
        gaps.append(f"retrieved-older<={maximum}")
    if req.get("requireRunnableCode") and not _has_runnable_code(value, req.get("requirePython", False)):
        gaps.append("runnable-code")
    if req.get("requireExample") and "example" not in lower:
        gaps.append("example")
    if req.get("requirePrefillExplanation") and not ("prefill" in lower and ("prompt" in lower or "context" in lower)):
        gaps.append("prefill-explanation")
    recent = req.get("recentWindow")
    if recent is not None:
        recent_pattern = re.compile(rf"\b(?:recent|window|latest)[^\n.]{{0,80}}\b{recent}\b|\b{recent}\b[^\n.]{{0,80}}\b(?:recent|window|latest)\b", re.I)
        if not recent_pattern.search(value):
            gaps.append(f"recent-window={recent}")
    return gaps


def inspect_engine():
    result = _V24_INSPECT()
    if isinstance(result, dict):
        result.update({
            "hotServerVersion": HOT_SERVER_VERSION,
            "hotRevision": HOT_REVISION,
            "semanticRequirementLedger": True,
            "truthfulCompletionGate": True,
            "numericRequirementValidation": True,
            "runnableCodeCompletionValidation": True,
            "requirementLedgerTransportField": "_swrlzRequirementLedger",
            "v24SourceCommit": _V24_COMMIT,
        })
    return result


def generate_events(payload, is_cancelled=None):
    prepared = _prepare_v25_payload(payload)
    req = prepared.get("_swrlzRequirementLedger") or {}
    response_text = ""
    for event in _V24_GENERATE(prepared, is_cancelled):
        if not isinstance(event, dict):
            yield event
            continue
        event = dict(event)
        event_type = str(event.get("type") or "")
        if event_type == "DELTA":
            response_text += str(event.get("text") or "")
            yield event
            continue
        if event_type == "COMPLETED":
            gaps = _requirement_gaps(response_text, req)
            if gaps:
                joined = ", ".join(gaps)
                yield {
                    "type": "STATUS",
                    "phase": "REQUIREMENT_GUARD",
                    "reason": f"Final-copy validation found unmet user requirements: {joined}. The response will not be labeled successful.",
                }
                yield {
                    "type": "FAILED",
                    "phase": "ERROR",
                    "reason": f"Generation ended with unmet user requirements: {joined}. Visible committed text is preserved for inspection.",
                }
                return
            event["reason"] = "Local R39 generation completed and the explicit user-requirement ledger passed."
            yield event
            return
        yield event
