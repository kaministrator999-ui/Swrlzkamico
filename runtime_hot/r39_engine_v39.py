"""R39 v39: recursion-safe structured server-log telemetry over v37.

Loads v37 into an isolated module namespace before wrapping it. This prevents the
v38 global _BASE_GENERATE alias from overwriting v37's own base-generator alias and
recursing. Telemetry remains observation-only and excludes prompt/history/response
text and credentials.
"""
from __future__ import annotations
import json
import re
import time
import types
import urllib.request

_V37_COMMIT = "337aa9838a867432073b4c814298b6bfb266072f"
_BASE_URL = f"https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/{_V37_COMMIT}/runtime_hot/r39_engine_v37.py"
_req = urllib.request.Request(_BASE_URL, headers={"User-Agent": "swrlz-r39-v39"})
with urllib.request.urlopen(_req, timeout=20) as _response:
    _source = _response.read(4_000_001)
if len(_source) > 4_000_000:
    raise RuntimeError("R39_V37_SOURCE_TOO_LARGE")
_v37 = types.ModuleType("swrlz_r39_v37_isolated")
_v37.__file__ = _BASE_URL
exec(compile(_source.decode("utf-8"), _BASE_URL + "#v39-base", "exec"), _v37.__dict__, _v37.__dict__)

# Re-export the engine contract from the isolated v37 namespace, then override only
# inspect/generate with the observation wrapper below.
ENGINE_ID = _v37.ENGINE_ID
MODEL_SHA256 = _v37.MODEL_SHA256
_impl = _v37._impl
_BASE_INSPECT = _v37.inspect_engine
_BASE_GENERATE = _v37.generate_events
HOT_SERVER_VERSION = "2.1.50"
HOT_REVISION = "2.1.50-hot-recursion-safe-server-telemetry-v39"
_impl.HOT_SERVER_VERSION = HOT_SERVER_VERSION
_impl.HOT_REVISION = HOT_REVISION
_TELEMETRY_CONTRACT = "r39-server-log-telemetry-v1"


def _request_id(payload):
    value = str((payload or {}).get("requestId") or "")[:128]
    return value if re.fullmatch(r"[A-Za-z0-9._:-]{1,128}", value) else ""


def _emit(request_id, event, **fields):
    payload = {
        "contract": _TELEMETRY_CONTRACT,
        "requestId": request_id,
        "event": str(event)[:64],
        "engineVersion": HOT_SERVER_VERSION,
        "engineRevision": HOT_REVISION,
        "atUnixMs": int(time.time() * 1000),
    }
    for key, value in fields.items():
        if value is None or isinstance(value, (str, int, float, bool)):
            payload[str(key)[:64]] = value
    print("SWRLZ_R39_TELEMETRY " + json.dumps(payload, ensure_ascii=False, separators=(",", ":")), flush=True)


def _metric_fields(reason):
    text = str(reason or "")[:1200]
    patterns = {
        "ttftMs": r"TTFT=(None|\d+)ms",
        "cachedTokens": r"cached=(\d+)",
        "uncachedTokens": r"uncached=(\d+)",
        "prefillSeconds": r"prefill=([0-9.]+)s/",
        "prefillTokensPerSecond": r"prefill=[0-9.]+s/([0-9.]+) tok/s",
        "batchPrefillTokens": r"batch=(\d+) tok/",
        "batchBlocks": r"batch=\d+ tok/(\d+) blocks",
        "serialPrefillTokens": r"serial-prefill=(\d+) tok",
        "batchFallbacks": r"fallbacks=(\d+)",
        "decodeTokens": r"decode-compute=(\d+) tok/",
        "decodeComputeSeconds": r"decode-compute=\d+ tok/([0-9.]+)s/",
        "decodeTokensPerSecond": r"decode-compute=\d+ tok/[0-9.]+s/([0-9.]+) tok/s",
    }
    out = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        if not match:
            continue
        raw = match.group(1)
        if raw == "None":
            out[key] = None
        elif key.endswith("Seconds") or "PerSecond" in key:
            out[key] = float(raw)
        else:
            out[key] = int(raw)
    return out


def inspect_engine():
    result = _BASE_INSPECT()
    if isinstance(result, dict):
        result.update({
            "hotServerVersion": HOT_SERVER_VERSION,
            "hotRevision": HOT_REVISION,
            "serverLogDeepTelemetry": True,
            "serverLogTelemetryContract": _TELEMETRY_CONTRACT,
            "telemetryChangesInference": False,
            "telemetryLogsPromptOrResponseText": False,
            "telemetryWrapperNamespace": "isolated-v37",
        })
    return result


def generate_events(payload, is_cancelled=None):
    request_id = _request_id(payload)
    started = time.monotonic()
    _emit(request_id, "inference-start")
    last_phase = ""
    terminal_seen = False
    try:
        for event in _BASE_GENERATE(payload, is_cancelled):
            if isinstance(event, dict):
                kind = str(event.get("type") or "")
                phase = str(event.get("phase") or "")
                reason = str(event.get("reason") or "")
                if phase and phase != last_phase and phase not in {"PREFILL_TOKEN", "PREFILL_TRACE", "PREFILL_TRACE_READY"}:
                    _emit(request_id, "phase", phase=phase, elapsedMs=int((time.monotonic() - started) * 1000))
                    last_phase = phase
                if phase == "INFERENCE_TELEMETRY":
                    if "prefill-start" in reason:
                        _emit(request_id, "prefill-start", elapsedMs=int((time.monotonic() - started) * 1000))
                    elif "decode-start" in reason:
                        match = re.search(r"prefillWallMs=(\d+)", reason)
                        _emit(request_id, "decode-start", prefillWallMs=int(match.group(1)) if match else None, elapsedMs=int((time.monotonic() - started) * 1000))
                    elif "first-delta" in reason:
                        wait = re.search(r"decodeWaitMs=(\d+)", reason)
                        total = re.search(r"totalMs=(\d+)", reason)
                        _emit(request_id, "first-delta", decodeWaitMs=int(wait.group(1)) if wait else None, totalMs=int(total.group(1)) if total else None)
                    elif "telemetry-v1 engine " in reason:
                        _emit(request_id, "engine-metrics", **_metric_fields(reason))
                    elif "terminal=" in reason:
                        terminal = re.search(r"terminal=([a-z]+)", reason)
                        total = re.search(r"totalMs=(\d+)", reason)
                        deltas = re.search(r"deltaEvents=(\d+)", reason)
                        chars = re.search(r"deltaChars=(\d+)", reason)
                        _emit(request_id, "terminal-summary", terminal=terminal.group(1) if terminal else "", totalMs=int(total.group(1)) if total else None, deltaEvents=int(deltas.group(1)) if deltas else None, deltaChars=int(chars.group(1)) if chars else None)
                if kind in {"COMPLETED", "FAILED", "CANCELLED"}:
                    terminal_seen = True
                    _emit(request_id, "terminal-event", terminal=kind.lower(), elapsedMs=int((time.monotonic() - started) * 1000))
            yield event
    except Exception as exc:
        _emit(request_id, "telemetry-wrapper-exception", errorType=type(exc).__name__, elapsedMs=int((time.monotonic() - started) * 1000))
        raise
    finally:
        _emit(request_id, "inference-end", terminalSeen=terminal_seen, elapsedMs=int((time.monotonic() - started) * 1000))
