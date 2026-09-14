"""R39 hot v33: brain-owned interpretation boundary over v32.

The Chat client is a mask/sensory relay, not a second reasoning controller.  v33
therefore treats browser-supplied cognitive envelopes, intent labels and known
browser-generated response steering as legacy input that must not own
interpretation. Factual approved user context still crosses the boundary, while
task classification, RMCCA reasoning, temporal interpretation, response planning
and semantic acceptance remain LALM responsibilities.
"""
from __future__ import annotations
import re
import urllib.request

_V32_COMMIT = "f8fa75f3afcf0b829e5bfae75688c58cd1b6e2ca"
_V32_URL = f"https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/{_V32_COMMIT}/runtime_hot/r39_engine_v32.py"
_req = urllib.request.Request(_V32_URL, headers={"User-Agent": "swrlz-hot-r39-v33"})
with urllib.request.urlopen(_req, timeout=20) as _response:
    _source = _response.read(4_000_001)
if len(_source) > 4_000_000:
    raise RuntimeError("R39_V32_SOURCE_TOO_LARGE")
exec(compile(_source.decode("utf-8"), _V32_URL + "#v33", "exec"), globals(), globals())

_V32_INSPECT = globals().get("inspect_engine")
_V32_GENERATE = globals().get("generate_events")
_V32_APPROVED_TEMPORAL_CONTEXT = globals().get("_approved_temporal_context")
if not callable(_V32_INSPECT) or not callable(_V32_GENERATE) or not callable(_V32_APPROVED_TEMPORAL_CONTEXT):
    raise RuntimeError("R39_V33_BASE_CONTRACT_MISSING")

HOT_SERVER_VERSION = "2.1.43"
HOT_REVISION = "2.1.43-hot-brain-owned-interpretation-v33"
_impl.HOT_SERVER_VERSION = HOT_SERVER_VERSION
_impl.HOT_REVISION = HOT_REVISION

_LEGACY_CLIENT_COGNITIVE_MARKERS = (
    "RMCCA cognitive policy:",
    "Social opener contract:",
    "Direct current-time response contract:",
    "Approved request-time temporal facts:",
)
_TRANSPORT_DIRECTIVE = (
    "Answer directly and truthfully. Stream only committed assistant response text as DELTA. "
    "Keep status, routing, and operational detail outside assistant prose."
)
_TIME_RE = re.compile(r"^(\d{1,2}):(\d{2})")
_CARRIER_PREFIX = "[[SWRLZ_RMCCA_TRANSPORT_V1:"


def _derive_daypart_from_clock(value):
    """Interpret factual local clock inside the LALM boundary, never in Chat."""
    match = _TIME_RE.match(str(value or "").strip())
    if not match:
        return ""
    hour = max(0, min(23, int(match.group(1))))
    if 5 <= hour < 12:
        return "morning"
    if 12 <= hour < 17:
        return "afternoon"
    if 17 <= hour < 22:
        return "evening"
    return "night"


def _approved_temporal_context(payload):
    """Accept approved factual device context, but let the LALM interpret daypart."""
    approved = _V32_APPROVED_TEMPORAL_CONTEXT(payload)
    if not approved:
        return approved
    result = dict(approved)
    result["daypart"] = _derive_daypart_from_clock(result.get("localTime"))
    return result


def _brain_owned_payload(payload):
    if not isinstance(payload, dict):
        return payload
    clone = dict(payload)

    # Retired browser cognition must never become an interpretation authority.
    clone.pop("swrlzCognitiveContext", None)
    clone.pop("turnIntent", None)
    clone.pop("_swrlzCarrierAttached", None)
    history = clone.get("history")
    if isinstance(history, list):
        clone["history"] = [
            item for item in history
            if not str(item.get("text") or "").startswith(_CARRIER_PREFIX)
            if isinstance(item, dict)
        ]

    # Old cached clients may still append cognitive steering for a short period.
    # Replace only known retired client-authored steering with the neutral stream
    # transport contract; unrelated explicit server/project policy is preserved.
    directive = str(clone.get("responseDirective") or "")
    if any(marker in directive for marker in _LEGACY_CLIENT_COGNITIVE_MARKERS):
        clone["responseDirective"] = _TRANSPORT_DIRECTIVE

    return clone


def inspect_engine():
    result = _V32_INSPECT()
    if isinstance(result, dict):
        result.update({
            "hotServerVersion": HOT_SERVER_VERSION,
            "hotRevision": HOT_REVISION,
            "maskBrainBoundary": "client-relays-lalm-interprets-v1",
            "clientCognitiveEnvelopeIgnored": True,
            "clientIntentLabelIgnored": True,
            "legacyRmccaCarrierIgnored": True,
            "legacyClientCognitiveSteeringIgnored": True,
            "daypartDerivedInsideLalm": True,
            "factualTemporalContextPreserved": True,
            "taskInterpretationOwnedByLalm": True,
            "rmccaInterpretationOwnedByLalm": True,
            "v32SourceCommit": _V32_COMMIT,
        })
    return result


def generate_events(payload, is_cancelled=None):
    owned = _brain_owned_payload(payload)
    for event in _V32_GENERATE(owned, is_cancelled):
        yield event
