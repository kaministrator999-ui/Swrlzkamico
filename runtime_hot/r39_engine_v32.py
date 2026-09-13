"""R39 hot v32: buffered social semantic acceptance over v31.

Exact social greetings are short enough to validate before any assistant text is
committed.  v31 proved that prompt constraints alone are insufficient for this
small model: a candidate can receive an approved ``evening`` anchor, emit
``Good morning``, and even echo internal temporal scaffolding in the same answer.

v32 therefore treats simple social openers as a final-copy acceptance problem:
model DELTAs are buffered privately, checked against approved request-time facts
and non-relay policy, then committed only if they pass.  An invalid candidate is
replaced by a deterministic, context-consistent social micro-response and the
reason remains visible in STATUS telemetry.  Non-social generation is unchanged.
"""
from __future__ import annotations
import re
import urllib.request

_V31_COMMIT = "12f6f99660382607e8ccd99c63f07b4a7890031e"
_V31_URL = f"https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/{_V31_COMMIT}/runtime_hot/r39_engine_v31.py"
_req = urllib.request.Request(_V31_URL, headers={"User-Agent": "swrlz-hot-r39-v32"})
with urllib.request.urlopen(_req, timeout=20) as _response:
    _source = _response.read(4_000_001)
if len(_source) > 4_000_000:
    raise RuntimeError("R39_V31_SOURCE_TOO_LARGE")
exec(compile(_source.decode("utf-8"), _V31_URL + "#v32", "exec"), globals(), globals())

_V31_INSPECT = globals().get("inspect_engine")
_V31_GENERATE = globals().get("generate_events")
if not callable(_V31_INSPECT) or not callable(_V31_GENERATE):
    raise RuntimeError("R39_V32_BASE_CONTRACT_MISSING")

HOT_SERVER_VERSION = "2.1.42"
HOT_REVISION = "2.1.42-hot-social-semantic-acceptance-v32"
_impl.HOT_SERVER_VERSION = HOT_SERVER_VERSION
_impl.HOT_REVISION = HOT_REVISION

_INTERNAL_TEMPORAL_LEAK_RE = re.compile(
    r"(?:\(\s*context\s*:|\bcontext\s*:\s*\d{1,2}:\d{2}|"
    r"\blocalTime\s*=|\bdaypart\s*=|\bapproved\s+request[- ]time|"
    r"\bsocial\s+temporal\s+contract\b|\bfixed\s+factual\s+anchor|"
    r"\bclient/project\s+policy\b|\btemporal\s+grounding\b)",
    re.I,
)
_SERVICE_DESK_RE = re.compile(
    r"\b(?:anything\s+else\s+(?:i\s+can\s+)?help|"
    r"let\s+me\s+know\s+if|"
    r"here\s+(?:whenever|if)\s+you\s+need|"
    r"helping\s+hand|"
    r"how\s+can\s+i\s+help(?:\s+you)?|"
    r"what\s+can\s+i\s+help\s+you\s+with)\b",
    re.I,
)
_DAYPART_RE = re.compile(r"\b(morning|afternoon|evening|night|overnight)\b", re.I)


def _simple_social_turn(payload):
    if not isinstance(payload, dict):
        return False
    prompt = str(payload.get("prompt") or "").strip()
    return bool(_GREETING_RE.fullmatch(prompt) and _classify_task(payload) == "social")


def _normalized_daypart(payload):
    approved = _approved_temporal_context(payload)
    if not approved:
        return ""
    value = str(approved.get("daypart") or "").strip().lower()
    if value in {"morning", "afternoon", "evening", "night", "overnight"}:
        return value
    return ""


def _social_candidate_gaps(text, payload):
    value = str(text or "").strip()
    gaps = []
    if not value:
        gaps.append("empty-social-candidate")
        return gaps
    if _INTERNAL_TEMPORAL_LEAK_RE.search(value):
        gaps.append("internal-temporal-context-leak")
    if _SERVICE_DESK_RE.search(value):
        gaps.append("service-desk-closure")

    approved = _approved_temporal_context(payload)
    daypart = _normalized_daypart(payload)
    mentioned = {m.group(1).lower() for m in _DAYPART_RE.finditer(value)}
    if not approved:
        if mentioned:
            gaps.append("time-specific-greeting-without-approved-context")
    elif daypart:
        contradictory = {x for x in mentioned if x != daypart}
        if contradictory:
            gaps.append("contradictory-daypart:" + ",".join(sorted(contradictory)))
    elif mentioned:
        gaps.append("time-specific-greeting-without-approved-daypart")
    return gaps


def _safe_social_reply(payload):
    daypart = _normalized_daypart(payload)
    if daypart == "morning":
        return "Hey 👋 Good morning!"
    if daypart == "afternoon":
        return "Hey 👋 Good afternoon!"
    if daypart == "evening":
        return "Hey 👋 Good evening!"
    if daypart in {"night", "overnight"}:
        return "Hey 👋 Hope your night's going well."
    return "Hey 👋"


def inspect_engine():
    result = _V31_INSPECT()
    if isinstance(result, dict):
        result.update({
            "hotServerVersion": HOT_SERVER_VERSION,
            "hotRevision": HOT_REVISION,
            "socialSemanticAcceptanceGate": True,
            "socialCandidateBufferedBeforeCommit": True,
            "socialTemporalContradictionRejectedBeforeCommit": True,
            "internalTemporalContextLeakRejectedBeforeCommit": True,
            "serviceDeskSocialClosureRejectedBeforeCommit": True,
            "socialDeterministicSafeFinalizer": True,
            "v31SourceCommit": _V31_COMMIT,
        })
    return result


def generate_events(payload, is_cancelled=None):
    if not _simple_social_turn(payload):
        for event in _V31_GENERATE(payload, is_cancelled):
            yield event
        return

    candidate = ""
    terminal = None
    yield {
        "type": "STATUS",
        "phase": "SOCIAL_ACCEPTANCE",
        "reason": "Short social response is being validated against approved request-time facts and non-relay policy before visible commit.",
    }

    for event in _V31_GENERATE(payload, is_cancelled):
        if not isinstance(event, dict):
            continue
        current = dict(event)
        event_type = str(current.get("type") or "")
        if event_type == "DELTA":
            candidate += str(current.get("text") or "")
            continue
        if event_type in {"COMPLETED", "FAILED"}:
            terminal = current
            break
        # Preserve useful compute/status telemetry while assistant prose remains private.
        yield current

    gaps = _social_candidate_gaps(candidate, payload)
    if terminal is None:
        gaps.append("missing-terminal-event")
    elif str(terminal.get("type") or "") != "COMPLETED":
        gaps.append("generation-terminal-not-completed")

    if not gaps:
        if candidate:
            yield {"type": "DELTA", "phase": "WRITING", "text": candidate}
        terminal = dict(terminal or {})
        terminal["type"] = "COMPLETED"
        terminal["phase"] = "COMPLETE"
        terminal["reason"] = "Buffered social candidate passed temporal consistency, non-relay, and conversational acceptance checks."
        yield terminal
        return

    safe = _safe_social_reply(payload)
    yield {
        "type": "STATUS",
        "phase": "SOCIAL_ACCEPTANCE_REPAIR",
        "reason": "Rejected uncommitted social candidate before display: " + ", ".join(gaps) + ". Emitting a request-time-consistent final-copy response.",
    }
    yield {"type": "DELTA", "phase": "WRITING", "text": safe}
    yield {
        "type": "COMPLETED",
        "phase": "COMPLETE",
        "reason": "Social response completed through the semantic acceptance guard; invalid candidate text was never committed.",
    }
