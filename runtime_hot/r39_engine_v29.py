"""R39 hot v29: anchored personalized temporal responses over v28.

Direct user-local time questions keep two factual anchors fixed when available:
the user's preferred name supplied by Chat policy and the approved current local
time. The model may add natural personality around those anchors, but it must not
replace, contradict, or redundantly restate them. Time answers prefer a fitting
time-of-day emoji over a generic greeting wave.
"""
from __future__ import annotations
import re
import urllib.request

_V28_COMMIT = "f7ffe36332349a5745b122de71d4880340aa66ee"
_V28_URL = f"https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/{_V28_COMMIT}/runtime_hot/r39_engine_v28.py"
_req = urllib.request.Request(_V28_URL, headers={"User-Agent": "swrlz-hot-r39-v29"})
with urllib.request.urlopen(_req, timeout=20) as _response:
    _source = _response.read(4_000_001)
if len(_source) > 4_000_000:
    raise RuntimeError("R39_V28_SOURCE_TOO_LARGE")
exec(compile(_source.decode("utf-8"), _V28_URL + "#v29", "exec"), globals(), globals())

_V28_INSPECT = globals().get("inspect_engine")
_V28_GENERATE = globals().get("generate_events")
_V28_TIME_NOTE = globals().get("_time_note")
if not callable(_V28_INSPECT) or not callable(_V28_GENERATE) or not callable(_V28_TIME_NOTE):
    raise RuntimeError("R39_V29_BASE_CONTRACT_MISSING")

HOT_SERVER_VERSION = "2.1.39"
HOT_REVISION = "2.1.39-hot-anchored-temporal-personality-v29"
_impl.HOT_SERVER_VERSION = HOT_SERVER_VERSION
_impl.HOT_REVISION = HOT_REVISION

_DIRECT_LOCAL_TIME_RE = re.compile(
    r"^\s*(?:what(?:'s| is)(?: the)? time(?: for me| here| right now)?|"
    r"what time is it(?: for me| here| right now)?|"
    r"tell me(?: the)?(?: current| local)? time|"
    r"current time(?: for me| here)?|my(?: current| local)? time)\s*[?.!]*\s*$",
    re.I,
)


def _time_note(payload):
    note = _V28_TIME_NOTE(payload)
    prompt = str(payload.get("prompt") or "") if isinstance(payload, dict) else ""
    approved = _approved_temporal_context(payload)
    if approved and _DIRECT_LOCAL_TIME_RE.fullmatch(prompt):
        note += (
            " This is a direct current-user-time question. Treat the approved local clock as a fixed factual anchor."
            " If Chat's client policy supplies a user preferred-name anchor, include that exact preferred name naturally once."
            " Treat preferred name and exact approved local time as fixed semantic blocks; wording before, between, and after"
            " those blocks may carry §wyrlz personality. Prefer a fitting time-of-day emoji (for example sun, coffee, sunset,"
            " moon, or stars as appropriate) rather than defaulting to a waving-hand greeting. Avoid redundant constructions"
            " such as saying an AM time 'in the morning'; if daypart context is useful, phrase it separately and naturally."
            " Keep a simple time answer concise while still sounding conversational rather than robotic."
        )
    return note


def inspect_engine():
    result = _V28_INSPECT()
    if isinstance(result, dict):
        result.update({
            "hotServerVersion": HOT_SERVER_VERSION,
            "hotRevision": HOT_REVISION,
            "directTimeFixedAnchorContract": True,
            "preferredNameTemporalAnchorSupported": True,
            "temporalPersonalityOutsideAnchors": True,
            "timeAppropriateEmojiGuidance": True,
            "redundantDaypartSuppression": True,
            "v28SourceCommit": _V28_COMMIT,
        })
    return result


def generate_events(payload, is_cancelled=None):
    for event in _V28_GENERATE(payload, is_cancelled):
        yield event
