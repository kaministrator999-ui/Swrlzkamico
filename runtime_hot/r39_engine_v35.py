"""R39 hot v35: non-coding context hygiene over v34.

Preserves v34's mask/human/brain ownership and runnable-code-only implementation
contract. Additionally removes previously leaked implementation-acceptance assistant
turns from inference history on non-coding requests so a conversation contaminated by
an older runtime does not keep teaching the model to repeat internal evaluator prose.
The user's text is never rewritten or filtered, and coding turns retain their normal
history and semantic acceptance machinery.
"""
from __future__ import annotations
import urllib.request

_V34_COMMIT = "0c0b0e2033ca848768a38207fd104eefacc0d0be"
_V34_URL = f"https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/{_V34_COMMIT}/runtime_hot/r39_engine_v34.py"
_req = urllib.request.Request(_V34_URL, headers={"User-Agent": "swrlz-hot-r39-v35"})
with urllib.request.urlopen(_req, timeout=20) as _response:
    _source = _response.read(4_000_001)
if len(_source) > 4_000_000:
    raise RuntimeError("R39_V34_SOURCE_TOO_LARGE")
exec(compile(_source.decode("utf-8"), _V34_URL + "#v35", "exec"), globals(), globals())

_V34_INSPECT = globals().get("inspect_engine")
_V34_GENERATE = globals().get("generate_events")
if not callable(_V34_INSPECT) or not callable(_V34_GENERATE):
    raise RuntimeError("R39_V35_BASE_CONTRACT_MISSING")

HOT_SERVER_VERSION = "2.1.46"
HOT_REVISION = "2.1.46-hot-noncoding-context-hygiene-v35"
_impl.HOT_SERVER_VERSION = HOT_SERVER_VERSION
_impl.HOT_REVISION = HOT_REVISION

_LEAK_MARKERS = (
    "implementation acceptance contract",
    "acceptance contract confirms that the python fence",
    "python fence must parse as valid python",
    "client has approved the response and will stream the text to delta",
)


def _is_noncoding_turn(payload):
    try:
        req = _requirements(payload if isinstance(payload, dict) else {})
    except Exception:
        return False
    return not bool((req or {}).get("requireRunnableCode"))


def _clean_noncoding_history(payload):
    if not isinstance(payload, dict) or not _is_noncoding_turn(payload):
        return payload
    history = payload.get("history")
    if not isinstance(history, list) or not history:
        return payload
    cleaned = []
    removed = 0
    for item in history:
        if not isinstance(item, dict):
            cleaned.append(item)
            continue
        role = str(item.get("role") or "").strip().lower()
        text = str(item.get("text") or item.get("content") or "")
        lower = text.lower()
        leaked = role == "assistant" and any(marker in lower for marker in _LEAK_MARKERS)
        if leaked:
            removed += 1
            continue
        cleaned.append(item)
    if not removed:
        return payload
    clone = dict(payload)
    clone["history"] = cleaned
    clone["_swrlzContextHygiene"] = {"removedLeakedAssistantTurns": removed}
    return clone


def inspect_engine():
    result = _V34_INSPECT()
    if isinstance(result, dict):
        result.update({
            "hotServerVersion": HOT_SERVER_VERSION,
            "hotRevision": HOT_REVISION,
            "nonCodingContextHygiene": True,
            "leakedImplementationTurnsExcludedFromNonCodingInference": True,
            "userTextRewrite": False,
            "codingHistoryPreserved": True,
            "v34SourceCommit": _V34_COMMIT,
        })
    return result


def generate_events(payload, is_cancelled=None):
    prepared = _clean_noncoding_history(payload)
    for event in _V34_GENERATE(prepared, is_cancelled):
        yield event
