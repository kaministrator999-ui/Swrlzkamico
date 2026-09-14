"""R39 hot v36: token-exact prefill trace diagnostics over v35.

Temporarily exposes the exact rendered prompt entering R39 prefill as STATUS telemetry,
one token at a time. This is diagnostic-only: it does not alter prompt content,
classification, cache semantics, inference state, or visible assistant DELTA text.
"""
from __future__ import annotations
import urllib.request

_V35_COMMIT = "2d6c942da0166bb752a7f3e3d8ae62f92602dec1"
_V35_URL = f"https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/{_V35_COMMIT}/runtime_hot/r39_engine_v35.py"
_req = urllib.request.Request(_V35_URL, headers={"User-Agent": "swrlz-hot-r39-v36"})
with urllib.request.urlopen(_req, timeout=20) as _response:
    _source = _response.read(4_000_001)
if len(_source) > 4_000_000:
    raise RuntimeError("R39_V35_SOURCE_TOO_LARGE")
exec(compile(_source.decode("utf-8"), _V35_URL + "#v36", "exec"), globals(), globals())

_V35_INSPECT = globals().get("inspect_engine")
_V35_GENERATE = globals().get("generate_events")
if not callable(_V35_INSPECT) or not callable(_V35_GENERATE):
    raise RuntimeError("R39_V36_BASE_CONTRACT_MISSING")

HOT_SERVER_VERSION = "2.1.47"
HOT_REVISION = "2.1.47-hot-token-exact-prefill-trace-v36"
_impl.HOT_SERVER_VERSION = HOT_SERVER_VERSION
_impl.HOT_REVISION = HOT_REVISION


def _trace_token_text(tokenizer, token_id):
    try:
        raw = tokenizer.token_bytes(int(token_id))
        if raw is None:
            token = tokenizer.tokens[int(token_id)] if 0 <= int(token_id) < len(tokenizer.tokens) else "<special>"
            return str(token)
        return raw.decode("utf-8", errors="replace")
    except Exception as exc:
        return f"<decode-error:{type(exc).__name__}>"


def _visible_token_text(value):
    return (
        str(value)
        .replace("\\", "\\\\")
        .replace("\r", "\\r")
        .replace("\n", "\\n")
        .replace("\t", "\\t")
    )


def _prefill_trace(payload):
    prepared = _clean_noncoding_history(payload)
    prompt = base.render_chat_prompt(prepared)
    model = _get_model()
    tokens = model.tokenizer.encode(prompt)
    yield {
        "type": "STATUS",
        "phase": "PREFILL_TRACE",
        "reason": f"Prefill trace armed · exact rendered prompt={len(prompt)} chars · {len(tokens)} token(s). Each PREFILL_TOKEN entry below is input presented to R39 in order.",
    }
    for index, token_id in enumerate(tokens, start=1):
        piece = _visible_token_text(_trace_token_text(model.tokenizer, token_id))
        yield {
            "type": "STATUS",
            "phase": "PREFILL_TOKEN",
            "reason": f"Prefill token {index}/{len(tokens)} · id={int(token_id)} · text={piece!r}",
        }
    yield {
        "type": "STATUS",
        "phase": "PREFILL_TRACE_READY",
        "reason": f"Prefill trace emitted all {len(tokens)} token(s); inference now continues unchanged through v35.",
    }


def inspect_engine():
    result = _V35_INSPECT()
    if isinstance(result, dict):
        result.update({
            "hotServerVersion": HOT_SERVER_VERSION,
            "hotRevision": HOT_REVISION,
            "tokenExactPrefillTrace": True,
            "prefillTracePhase": "PREFILL_TOKEN",
            "prefillTraceChangesInference": False,
            "v35SourceCommit": _V35_COMMIT,
        })
    return result


def generate_events(payload, is_cancelled=None):
    try:
        for event in _prefill_trace(payload):
            yield event
    except Exception as exc:
        yield {
            "type": "STATUS",
            "phase": "PREFILL_TRACE_ERROR",
            "reason": f"Prefill trace failed without blocking inference: {type(exc).__name__}: {exc}",
        }
    for event in _V35_GENERATE(payload, is_cancelled):
        yield event
