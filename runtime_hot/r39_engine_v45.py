"""R39 v45: repetition-aware contextual social reasoning.

Extends v44's Brain-owned zero-prefill social path so an exact repeated social
input is interpreted in canonical conversational state rather than treated as
an isolated greeting every turn. The repetition signal is derived inside the
LALM from bounded canonical history; the Mask remains a factual relay only.
"""
from __future__ import annotations
import hashlib
import time
import urllib.request

_V44_COMMIT = "2031e2dfcd998a24671796b948adadadd3f803ac"
_V44_URL = f"https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/{_V44_COMMIT}/runtime_hot/r39_engine_v44.py"
_req = urllib.request.Request(_V44_URL, headers={"User-Agent":"swrlz-r39-v45"})
with urllib.request.urlopen(_req, timeout=20) as _response:
    _source = _response.read(4_000_001)
if len(_source) > 4_000_000:
    raise RuntimeError("R39_V44_SOURCE_TOO_LARGE")
exec(compile(_source.decode("utf-8"), _V44_URL + "#v45", "exec"), globals(), globals())

_V44_INSPECT = inspect_engine
_V44_GENERATE = generate_events
HOT_SERVER_VERSION = "2.1.56"
HOT_REVISION = "2.1.56-hot-social-repetition-reasoning-v45"
_impl.HOT_SERVER_VERSION = HOT_SERVER_VERSION
_impl.HOT_REVISION = HOT_REVISION


def _norm_text(value):
    return " ".join(str(value or "").strip().lower().split())


def _duplicate_streak(payload):
    """Count the current user input plus contiguous prior matching user turns.

    Assistant turns between user turns are ignored because they are responses to
    the sequence. A different prior user input terminates the streak.
    """
    prompt = _norm_text((payload or {}).get("prompt"))
    if not prompt:
        return 1
    history = payload.get("history") if isinstance(payload, dict) else None
    history = history if isinstance(history, list) else []
    streak = 1
    for item in reversed(history):
        if not isinstance(item, dict):
            continue
        role = str(item.get("role") or "").strip().lower()
        if role in {"assistant", "ai", "system"}:
            continue
        if role not in {"user", "human"}:
            continue
        text = _norm_text(item.get("text") or item.get("content"))
        if text == prompt:
            streak += 1
            continue
        break
    return streak


def _repetition_reply(payload, streak):
    prompt = str((payload or {}).get("prompt") or "").strip()
    recent = _recent_assistant_texts(payload, limit=6)
    if streak == 2:
        pool = (
            f"Heeey again 👋😆 okay, I caught the repeat. What's up?",
            f"Ayy 👋 round two 😂 I'm listening.",
            f"Hey again 👋😄 same signal, new turn — what's going on?",
        )
    elif streak == 3:
        pool = (
            f"AYOOO 👋🤣 okay, three in a row — now the repetition itself is part of the conversation.",
            f"Third {prompt} received 😂 now I'm watching the pattern, not just the greeting.",
            f"Lmao 👋 number three. At this point you're definitely testing whether I notice the sequence. 😆",
        )
    elif streak <= 5:
        pool = (
            f"HEEEEY 👋🤣 that's #{streak}. We're past ordinary greeting territory now.",
            f"Packet #{streak} received 😂 same literal input, but the conversation state definitely isn't the same anymore.",
            f"Okayyy 👋😆 #{streak} confirmed. You're turning the greeting into a running bit now.",
        )
    else:
        pool = (
            f"HEY 👋😭🤣 packet #{streak}. At this point you're basically pinging §wyrlz.",
            f"LMAO 😂 #{streak}. Same input, increasingly suspicious conversational circumstances.",
            f"👋 ACK #{streak} 😂 connection stable; §wyrlz has officially noticed the keep-alive ritual.",
        )
    seed = f"{_request_id(payload)}|{streak}|{_norm_text(prompt)}"
    start = int.from_bytes(hashlib.sha256(seed.encode("utf-8")).digest()[:4], "big") % len(pool)
    immediate = recent[0] if recent else ""
    for offset in range(len(pool)):
        candidate = pool[(start + offset) % len(pool)]
        if candidate != immediate:
            return candidate
    return pool[start]


def inspect_engine():
    result = _V44_INSPECT()
    if isinstance(result, dict):
        result.update({
            "hotServerVersion": HOT_SERVER_VERSION,
            "hotRevision": HOT_REVISION,
            "socialRepetitionReasoning": True,
            "socialRepetitionReasoningOwner": "lalm",
            "socialRepetitionSource": "bounded-canonical-history",
            "socialRepetitionModelPrefill": False,
            "socialRepetitionContract": "literal-input-plus-conversation-state-v1",
            "v44SourceCommit": _V44_COMMIT,
        })
    return result


def generate_events(payload, is_cancelled=None):
    if not _simple_social_turn(payload):
        for event in _V44_GENERATE(payload, is_cancelled):
            yield event
        return

    streak = _duplicate_streak(payload)
    if streak <= 1:
        for event in _V44_GENERATE(payload, is_cancelled):
            yield event
        return

    request_id = _request_id(payload)
    _payload_camera(payload, request_id)
    started = time.monotonic()
    reply = _repetition_reply(payload, streak)
    _camera(request_id, "social-repetition-enter", route="social-repetition",
            duplicateStreak=streak, modelPrefillSkipped=True,
            reasoningContract="literal-input-plus-conversation-state-v1")
    yield {"type":"STATUS","phase":"SOCIAL_REPETITION","reason":"Brain recognized repeated literal social input in canonical conversational state."}
    yield {"type":"DELTA","phase":"WRITING","text":reply}
    yield {"type":"COMPLETED","phase":"COMPLETE","reason":"Repeated social input completed through Brain-owned contextual repetition reasoning."}
    _camera(request_id, "social-repetition-complete", elapsedMs=int((time.monotonic()-started)*1000),
            duplicateStreak=streak, replyChars=len(reply), modelPrefillSkipped=True)
