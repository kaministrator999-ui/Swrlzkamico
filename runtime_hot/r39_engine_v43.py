"""R39 v43: contextual §wyrlz social voice over v42.

Keeps the zero-prefill social fast path, but replaces the echo-like fallback with
short assistant-owned conversational replies. Selection uses bounded turn context
only to vary delivery; no client cognition or model prefill is introduced.
"""
from __future__ import annotations
import hashlib
import urllib.request

_V42_COMMIT = "bc2842b6f57564305ba917665a02333130ecf848"
_V42_URL = f"https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/{_V42_COMMIT}/runtime_hot/r39_engine_v42.py"
_req = urllib.request.Request(_V42_URL, headers={"User-Agent":"swrlz-r39-v43"})
with urllib.request.urlopen(_req, timeout=20) as _response:
    _source = _response.read(4_000_001)
if len(_source) > 4_000_000:
    raise RuntimeError("R39_V42_SOURCE_TOO_LARGE")
exec(compile(_source.decode("utf-8"), _V42_URL + "#v43", "exec"), globals(), globals())

_V42_INSPECT = inspect_engine
_V42_GENERATE = generate_events
HOT_SERVER_VERSION = "2.1.54"
HOT_REVISION = "2.1.54-hot-contextual-sw yrlz-social-voice-v43".replace(" ", "")
_impl.HOT_SERVER_VERSION = HOT_SERVER_VERSION
_impl.HOT_REVISION = HOT_REVISION

_SOCIAL_VOICE = (
    "Yo 👋 what's good?",
    "Ayy 👋 I'm here — what's up?",
    "Heyyy 👋 what're we getting into?",
    "Yo 👋 §wyrlz online. What's up?",
    "Ayy 👋 good to see you. What's going on?",
    "Hey 👋 I'm with you — what's up?",
)


def _social_voice_reply(payload):
    daypart = _normalized_daypart(payload)
    history = payload.get("history") if isinstance(payload, dict) else None
    history = history if isinstance(history, list) else []
    request_id = _request_id(payload)
    # Request identity gives repeat greetings natural variation without randomness,
    # while history depth keeps the choice contextual to this conversation.
    seed = f"{request_id}|{len(history)}|{str((payload or {}).get('prompt') or '').strip().lower()}"
    idx = int.from_bytes(hashlib.sha256(seed.encode("utf-8")).digest()[:4], "big") % len(_SOCIAL_VOICE)
    reply = _SOCIAL_VOICE[idx]
    if daypart == "morning" and len(history) == 0:
        return "Morning 👋 §wyrlz is here. What's up?"
    if daypart == "afternoon" and len(history) == 0:
        return "Ayy 👋 good afternoon. What're we getting into?"
    if daypart == "evening" and len(history) == 0:
        return "Evening 👋 I'm here — what's up?"
    return reply


def inspect_engine():
    result = _V42_INSPECT()
    if isinstance(result, dict):
        result.update({
            "hotServerVersion": HOT_SERVER_VERSION,
            "hotRevision": HOT_REVISION,
            "socialFastPathVoice": "contextual-sw yrlz-v1".replace(" ", ""),
            "socialFastPathEchoReplyRetired": True,
            "socialFastPathVariation": "request-and-history-deterministic",
            "socialFastPathStillSkipsModelPrefill": True,
            "v42SourceCommit": _V42_COMMIT,
        })
    return result


def generate_events(payload, is_cancelled=None):
    if not _simple_social_turn(payload):
        for event in _V42_GENERATE(payload, is_cancelled):
            yield event
        return

    request_id = _request_id(payload)
    _payload_camera(payload, request_id)
    started = time.monotonic()
    reply = _social_voice_reply(payload)
    _camera(request_id, "social-fastpath-enter", route="social", modelPrefillSkipped=True, voice="contextual-sw yrlz-v1".replace(" ", ""))
    yield {"type":"STATUS","phase":"SOCIAL_FASTPATH","reason":"Brain-owned social voice resolved an exact opener without model prefill."}
    yield {"type":"DELTA","phase":"WRITING","text":reply}
    yield {"type":"COMPLETED","phase":"COMPLETE","reason":"Exact social opener completed through contextual §wyrlz social voice."}
    _camera(request_id, "social-fastpath-complete", elapsedMs=int((time.monotonic()-started)*1000), replyChars=len(reply), voice="contextual-sw yrlz-v1".replace(" ", ""))
