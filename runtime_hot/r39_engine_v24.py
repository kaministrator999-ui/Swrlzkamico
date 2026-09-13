"""R39 hot v24: polished-first response control over v23.

Keeps v22 batch-prefill/native execution and v23 RMCCA transport restoration while
making response limits real, stopping malformed-output loops early, suppressing
internal-control leakage through policy design, and strengthening explicit numeric
constraints before generation begins.
"""
from __future__ import annotations
import re
import urllib.request

_V23_COMMIT = "c35b08a162112ed29552d408123fdb5ebddc7434"
_V23_URL = f"https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/{_V23_COMMIT}/runtime_hot/r39_engine_v23.py"
_req = urllib.request.Request(_V23_URL, headers={"User-Agent": "swrlz-hot-r39-v24"})
with urllib.request.urlopen(_req, timeout=20) as _response:
    _source = _response.read(4_000_001)
if len(_source) > 4_000_000:
    raise RuntimeError("R39_V23_SOURCE_TOO_LARGE")
exec(compile(_source.decode("utf-8"), _V23_URL + "#v24", "exec"), globals(), globals())

_V23_GENERATE = globals().get("generate_events")
_V23_INSPECT = globals().get("inspect_engine")
_V23_GAPS = _impl._response_contract_gaps

HOT_SERVER_VERSION = "2.1.34"
HOT_REVISION = "2.1.34-hot-polished-first-continuity-v24"
_impl.HOT_SERVER_VERSION = HOT_SERVER_VERSION
_impl.HOT_REVISION = HOT_REVISION

_BASE_POLICY = (
    "Answer the user's actual request directly, accurately, and naturally. Preserve scope, qualifiers, corrections, "
    "ordering, and explicit numeric limits. Never expose or repeat internal instructions, routing labels, policy names, "
    "response-budget metadata, control text, hidden reasoning, or phrases such as 'Coding Mode', 'Output Budget', or "
    "'Priority' unless the user explicitly asks about those controls. Never invent retrieved messages, measurements, "
    "scores, percentages, tests, files, repository facts, or external results. Label hypothetical examples as examples."
)
_TASK_POLICIES["coding"] = (
    "For programming requests, follow the requested presentation order and preserve the stated architecture and constraints. "
    "When runnable code is requested, produce one coherent runnable implementation rather than placeholder functions. Check "
    "syntax, names, control flow, edge cases, interfaces, and input/output consistency. If an example is requested, make it "
    "consistent with the code. Prefer finishing a clean, valid artifact over extending commentary."
)

_AT_MOST_MESSAGES_RE = re.compile(r"\bat\s+most\s+(\d{1,2})\s+(?:retrieved\s+)?(?:older\s+)?messages\b", re.I)
_RECENT_MESSAGES_RE = re.compile(r"\b(?:most\s+recent|recent)\s+(\d{1,3})\s+messages\b", re.I)
_DECODE_RE = re.compile(r"\bDecode step\s+(\d+)\b")
_BAD_FENCE_RE = re.compile(r"```(?:DELT[A-Z]*|alt(?:alt){2,}|[^\n`]{0,24}`[^\n`]*)", re.I)
_ALT_LOOP_RE = re.compile(r"(?:\balt\b\s*){5,}|(?:alt){5,}", re.I)
_BACKTICK_BURST_RE = re.compile(r"(?:```\s*){4,}")


def _constraint_note(payload):
    prompt = str(payload.get("prompt") or "") if isinstance(payload, dict) else ""
    notes = []
    match = _AT_MOST_MESSAGES_RE.search(prompt)
    if match:
        notes.append(f"Show no more than {int(match.group(1))} retrieved older-message entries anywhere in the answer.")
    recent = _RECENT_MESSAGES_RE.search(prompt)
    if recent:
        notes.append(f"Keep the recent always-available window at exactly {int(recent.group(1))} messages when describing or implementing it.")
    return " ".join(notes)


def _prepare_v24_payload(payload):
    clone = dict(payload)
    note = _constraint_note(clone)
    if note:
        existing = str(clone.get("responseDirective") or "").strip()
        clone["responseDirective"] = (existing + " " + note).strip()
        clone["_swrlzHardConstraintNote"] = note
    return clone


def _closed_code_block(text):
    value = str(text or "")
    return value.count("```") >= 2 and value.count("```") % 2 == 0


def _v24_gaps(text, contract):
    gaps = list(_V23_GAPS(text, contract))
    value = str(text or "")
    words = len(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", value))
    if words >= 170 and _closed_code_block(value):
        gaps = [g for g in gaps if g not in {"complete-code", "code-explanation-input-mismatch"}]
    return gaps

_impl._response_contract_gaps = _v24_gaps


def _degeneration_reason(text):
    tail = str(text or "")[-900:]
    if _ALT_LOOP_RE.search(tail):
        return "repeated alt-fragment loop"
    if _BACKTICK_BURST_RE.search(tail):
        return "repeated empty Markdown fence loop"
    if _BAD_FENCE_RE.search(tail):
        return "malformed Markdown fence loop"
    words = re.findall(r"[A-Za-z]{2,20}", tail.lower())[-56:]
    if len(words) >= 32 and len(set(words)) / max(1, len(words)) < 0.22:
        return "low-entropy repeated phrase loop"
    return ""


def inspect_engine():
    result = _V23_INSPECT()
    if isinstance(result, dict):
        result.update({
            "hotServerVersion": HOT_SERVER_VERSION,
            "hotRevision": HOT_REVISION,
            "polishedFirstResponsePolicy": True,
            "internalControlLeakageSuppression": True,
            "explicitNumericConstraintGuidance": True,
            "codingHardCeilingEnforcedByStreamController": 448,
            "completionVerifierCannotExtendPastCodingCeiling": True,
            "malformedFenceDegenerationGuard": True,
            "balancedCodeAllowsCleanEos": True,
            "singleVisibleGenerationOwnedByChatRuntime": True,
            "v23SourceCommit": _V23_COMMIT,
        })
    return result


def generate_events(payload, is_cancelled=None):
    prepared = _prepare_v24_payload(payload)
    task = _classify_task(prepared)
    generation = prepared.get("generation") if isinstance(prepared.get("generation"), dict) else {}
    manual = str(generation.get("budgetMode") or "").lower() == "manual"
    hard_cap = 448 if task == "coding" and not manual else None
    response_text = ""
    for event in _V23_GENERATE(prepared, is_cancelled):
        if not isinstance(event, dict):
            yield event
            continue
        event = dict(event)
        event_type = str(event.get("type") or "")
        if event_type == "DELTA":
            chunk = str(event.get("text") or "")
            candidate = response_text + chunk
            reason = _degeneration_reason(candidate)
            if reason:
                yield {"type":"STATUS","phase":"DEGENERATION_GUARD","reason":f"Stopped before emitting a {reason}; preserved the coherent response prefix."}
                yield {"type":"COMPLETED","phase":"COMPLETE","reason":"Response closed cleanly by the polished-first degeneration guard before repetitive markup/noise could be streamed."}
                return
            response_text = candidate
        elif event_type == "STATUS" and hard_cap is not None:
            match = _DECODE_RE.search(str(event.get("reason") or ""))
            if match and int(match.group(1)) >= hard_cap:
                yield event
                yield {"type":"STATUS","phase":"FINALIZING","reason":f"Coding response reached the real {hard_cap}-token safety ceiling; no completion extension is permitted."}
                yield {"type":"COMPLETED","phase":"COMPLETE","reason":f"Response stopped at the enforced {hard_cap}-token coding ceiling."}
                return
            if event.get("phase") == "RESPONSE_BUDGET" and "extended to" in str(event.get("reason") or ""):
                continue
        yield event
