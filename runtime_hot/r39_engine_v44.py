"""R39 v44: recent-response-aware contextual §wyrlz social voice.

Keeps the Brain-owned zero-prefill social fast path from v43 while preventing an
immediately repeated canned social reply when canonical history already contains
that reply. The decision remains inside the LALM and uses bounded canonical history.
"""
from __future__ import annotations
import hashlib
import urllib.request

_V43_COMMIT = "ecfc9d1001822bc5eeefb7501574e1cb4d49a3c8"
_V43_URL = f"https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/{_V43_COMMIT}/runtime_hot/r39_engine_v43.py"
_req = urllib.request.Request(_V43_URL, headers={"User-Agent":"swrlz-r39-v44"})
with urllib.request.urlopen(_req, timeout=20) as _response:
    _source = _response.read(4_000_001)
if len(_source) > 4_000_000:
    raise RuntimeError("R39_V43_SOURCE_TOO_LARGE")
exec(compile(_source.decode("utf-8"), _V43_URL + "#v44", "exec"), globals(), globals())

_V43_INSPECT = inspect_engine
_V43_GENERATE = generate_events
HOT_SERVER_VERSION = "2.1.55"
HOT_REVISION = "2.1.55-hot-social-recent-reply-anti-repeat-v44"
_impl.HOT_SERVER_VERSION = HOT_SERVER_VERSION
_impl.HOT_REVISION = HOT_REVISION


def _recent_assistant_texts(payload, limit=4):
    history = payload.get("history") if isinstance(payload, dict) else None
    history = history if isinstance(history, list) else []
    found = []
    for item in reversed(history):
        if not isinstance(item, dict):
            continue
        role = str(item.get("role") or "").strip().lower()
        if role not in {"assistant", "ai"}:
            continue
        text = str(item.get("text") or item.get("content") or "").strip()
        if text:
            found.append(text)
            if len(found) >= limit:
                break
    return found


def _social_voice_reply(payload):
    daypart = _normalized_daypart(payload)
    history = payload.get("history") if isinstance(payload, dict) else None
    history = history if isinstance(history, list) else []
    request_id = _request_id(payload)
    seed = f"{request_id}|{len(history)}|{str((payload or {}).get('prompt') or '').strip().lower()}"
    start = int.from_bytes(hashlib.sha256(seed.encode("utf-8")).digest()[:4], "big") % len(_SOCIAL_VOICE)

    if daypart == "morning" and len(history) == 0:
        return "Morning 👋 §wyrlz is here. What's up?"
    if daypart == "afternoon" and len(history) == 0:
        return "Ayy 👋 good afternoon. What're we getting into?"
    if daypart == "evening" and len(history) == 0:
        return "Evening 👋 I'm here — what's up?"

    recent = _recent_assistant_texts(payload)
    immediate = recent[0] if recent else ""
    for offset in range(len(_SOCIAL_VOICE)):
        candidate = _SOCIAL_VOICE[(start + offset) % len(_SOCIAL_VOICE)]
        if candidate != immediate:
            return candidate
    return _SOCIAL_VOICE[start]


def inspect_engine():
    result = _V43_INSPECT()
    if isinstance(result, dict):
        result.update({
            "hotServerVersion": HOT_SERVER_VERSION,
            "hotRevision": HOT_REVISION,
            "socialFastPathVoice": "contextual-swyrlz-v2",
            "socialFastPathAntiRepeat": True,
            "socialFastPathAntiRepeatScope": "immediate-canonical-assistant-reply",
            "socialFastPathStillSkipsModelPrefill": True,
            "v43SourceCommit": _V43_COMMIT,
        })
    return result


def generate_events(payload, is_cancelled=None):
    if not _simple_social_turn(payload):
        for event in _V43_GENERATE(payload, is_cancelled):
            yield event
        return

    request_id = _request_id(payload)
    _payload_camera(payload, request_id)
    started = time.monotonic()
    recent = _recent_assistant_texts(payload)
    reply = _social_voice_reply(payload)
    avoided_repeat = bool(recent and reply != recent[0])
    _camera(request_id, "social-fastpath-enter", route="social", modelPrefillSkipped=True,
            voice="contextual-swyrlz-v2", recentAssistantReplies=len(recent),
            immediateRepeatAvoided=avoided_repeat)
    yield {"type":"STATUS","phase":"SOCIAL_FASTPATH","reason":"Brain-owned social voice resolved an exact opener without model prefill."}
    yield {"type":"DELTA","phase":"WRITING","text":reply}
    yield {"type":"COMPLETED","phase":"COMPLETE","reason":"Exact social opener completed through contextual §wyrlz social voice."}
    _camera(request_id, "social-fastpath-complete", elapsedMs=int((time.monotonic()-started)*1000),
            replyChars=len(reply), voice="contextual-swyrlz-v2", immediateRepeatAvoided=avoided_repeat)
