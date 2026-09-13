"""R39 hot v30: non-relay temporal context over v29.

Approved device time remains available for reasoning, but implementation metadata
(date/timezone/UTC offset) is context, not answer text. Direct time questions expose
only the human-readable local-time anchor unless the user explicitly asks for date,
timezone, UTC offset, or temporal-debug details.
"""
from __future__ import annotations
import re
import urllib.request

_V29_COMMIT = "49a59dce9cd908d21178626d53f228ec14e8c70d"
_V29_URL = f"https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/{_V29_COMMIT}/runtime_hot/r39_engine_v29.py"
_req = urllib.request.Request(_V29_URL, headers={"User-Agent": "swrlz-hot-r39-v30"})
with urllib.request.urlopen(_req, timeout=20) as _response:
    _source = _response.read(4_000_001)
if len(_source) > 4_000_000:
    raise RuntimeError("R39_V29_SOURCE_TOO_LARGE")
exec(compile(_source.decode("utf-8"), _V29_URL + "#v30", "exec"), globals(), globals())

_V29_INSPECT = globals().get("inspect_engine")
_V29_GENERATE = globals().get("generate_events")
if not callable(_V29_INSPECT) or not callable(_V29_GENERATE):
    raise RuntimeError("R39_V30_BASE_CONTRACT_MISSING")

HOT_SERVER_VERSION = "2.1.40"
HOT_REVISION = "2.1.40-hot-temporal-context-nonrelay-v30"
_impl.HOT_SERVER_VERSION = HOT_SERVER_VERSION
_impl.HOT_REVISION = HOT_REVISION

_DATE_QUERY_RE = re.compile(r"\b(?:what(?:'s| is) (?:the )?date|what day is it|today(?:'s| is the)? date|current date)\b", re.I)
_ZONE_QUERY_RE = re.compile(r"\b(?:time ?zone|timezone|utc(?: offset)?|gmt(?: offset)?|offset from utc)\b", re.I)
_TEMPORAL_DEBUG_RE = re.compile(r"\b(?:temporal context|time context|device time metadata|debug.*time|time.*debug)\b", re.I)


def _display_clock(value):
    text = str(value or "").strip()
    match = re.match(r"^(\d{1,2}):(\d{2})", text)
    if not match:
        return text
    hour = max(0, min(23, int(match.group(1))))
    minute = match.group(2)
    suffix = "PM" if hour >= 12 else "AM"
    return f"{hour % 12 or 12}:{minute} {suffix}"


def _time_note(payload):
    approved = _approved_temporal_context(payload)
    if not approved:
        return (
            " User-local temporal context is unavailable or not approved."
            " Do not infer or claim the user's current local hour, date, morning/afternoon/evening/night,"
            " or use a time-specific greeting unless the user explicitly supplied enough temporal information"
            " in the conversation itself."
        )

    prompt = str(payload.get("prompt") or "") if isinstance(payload, dict) else ""
    clock = _display_clock(approved.get("localTime"))
    daypart = str(approved.get("daypart") or "").strip()
    date = str(approved.get("localDate") or "").strip()
    zone = str(approved.get("timeZone") or "").strip()
    offset = str(approved.get("utcOffset") or "").strip()

    if _DIRECT_LOCAL_TIME_RE.fullmatch(prompt):
        note = (
            f" Approved user-local clock anchor: {clock}."
            + (f" Current daypart: {daypart}." if daypart else "")
            + " Answer the user's time question using that human-readable clock anchor."
            + " Device date, IANA timezone, and UTC-offset fields are internal grounding metadata and MUST NOT be"
            + " listed, echoed, or exposed in the answer unless the user explicitly asks for them."
            + " Do not output a raw temporal-context record."
        )
    else:
        note = (
            (f" Approved user-local clock context: {clock}." if clock else "")
            + (f" Daypart: {daypart}." if daypart else "")
            + " Use this only when conversationally relevant. Do not gratuitously mention the clock."
            + " Device date, timezone, and UTC offset are internal grounding metadata; do not surface them unless requested."
        )

    if _DATE_QUERY_RE.search(prompt) and date:
        note += f" The user explicitly asked for date context; approved local date is {date}."
    if (_ZONE_QUERY_RE.search(prompt) or _TEMPORAL_DEBUG_RE.search(prompt)):
        if zone:
            note += f" The user explicitly asked for timezone/context details; approved IANA timezone is {zone}."
        if offset:
            note += f" Approved UTC offset is {offset}."
    return note


def inspect_engine():
    result = _V29_INSPECT()
    if isinstance(result, dict):
        result.update({
            "hotServerVersion": HOT_SERVER_VERSION,
            "hotRevision": HOT_REVISION,
            "temporalMetadataNonRelayContract": True,
            "rawTemporalRecordExposureSuppressed": True,
            "directTimeHumanClockAnchorOnly": True,
            "timezoneDateOffsetRequireExplicitUserAsk": True,
            "v29SourceCommit": _V29_COMMIT,
        })
    return result


def generate_events(payload, is_cancelled=None):
    for event in _V29_GENERATE(payload, is_cancelled):
        yield event
