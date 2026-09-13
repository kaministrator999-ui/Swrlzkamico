"""R39 hot v28: permission-aware user temporal grounding over v27.

The browser may provide user-local date/time metadata only after explicit consent.
When that bounded metadata survives stable normalization, R39 may use it naturally
when relevant. When it is absent, R39 must not invent the user's current local
hour or daypart and must avoid time-specific greetings unless the user supplied
that temporal information in conversation.
"""
from __future__ import annotations
import urllib.request

_V27_COMMIT = "a5250b6ae2daeaada0dc4434272799ef00bb026b"
_V27_URL = f"https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/{_V27_COMMIT}/runtime_hot/r39_engine_v27.py"
_req = urllib.request.Request(_V27_URL, headers={"User-Agent": "swrlz-hot-r39-v28"})
with urllib.request.urlopen(_req, timeout=20) as _response:
    _source = _response.read(4_000_001)
if len(_source) > 4_000_000:
    raise RuntimeError("R39_V27_SOURCE_TOO_LARGE")
exec(compile(_source.decode("utf-8"), _V27_URL + "#v28", "exec"), globals(), globals())

_V27_INSPECT = globals().get("inspect_engine")
_V27_GENERATE = globals().get("generate_events")
_V22_TIME_NOTE = globals().get("_time_note")
if not callable(_V27_INSPECT) or not callable(_V27_GENERATE) or not callable(_V22_TIME_NOTE):
    raise RuntimeError("R39_V28_BASE_CONTRACT_MISSING")

HOT_SERVER_VERSION = "2.1.38"
HOT_REVISION = "2.1.38-hot-permission-temporal-grounding-v28"
_impl.HOT_SERVER_VERSION = HOT_SERVER_VERSION
_impl.HOT_REVISION = HOT_REVISION


def _approved_temporal_context(payload):
    ctx = payload.get("swrlzUserTimeContext") if isinstance(payload, dict) else None
    if not isinstance(ctx, dict):
        return None
    values = {
        "localDate": str(ctx.get("localDate") or "").strip(),
        "localTime": str(ctx.get("localTime") or "").strip(),
        "daypart": str(ctx.get("daypart") or "").strip(),
        "timeZone": str(ctx.get("timeZone") or "").strip(),
        "utcOffset": str(ctx.get("utcOffset") or "").strip(),
    }
    return values if any(values.values()) else None


def _time_note(payload):
    approved = _approved_temporal_context(payload)
    if approved:
        base = _V22_TIME_NOTE(payload)
        return (
            base
            + " This user-local temporal context was supplied by Chat from an explicitly approved device-time setting."
            + " Use it only when conversationally relevant; do not gratuitously mention the clock or timezone."
        )
    return (
        " User-local temporal context is unavailable or not approved."
        " Do not infer or claim the user's current local hour, date, morning/afternoon/evening/night,"
        " or use a time-specific greeting unless the user explicitly supplied enough temporal information"
        " in the conversation itself. If a request requires the user's local time, state that time-aware"
        " context must be enabled or the user must provide the timezone/time information."
    )


def inspect_engine():
    result = _V27_INSPECT()
    if isinstance(result, dict):
        result.update({
            "hotServerVersion": HOT_SERVER_VERSION,
            "hotRevision": HOT_REVISION,
            "permissionAwareTemporalGrounding": True,
            "timeSpecificClaimsRequireApprovedContext": True,
            "deviceTimeConsentOwnedByChat": True,
            "profileLocationTemporalResolution": False,
            "temporalContextTransportField": "swrlzUserTimeContext",
            "v27SourceCommit": _V27_COMMIT,
        })
    return result


def generate_events(payload, is_cancelled=None):
    for event in _V27_GENERATE(payload, is_cancelled):
        yield event
