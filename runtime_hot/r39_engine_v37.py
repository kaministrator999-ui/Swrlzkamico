"""R39 v37 observation-only inference performance telemetry."""
from __future__ import annotations
import time
import urllib.request

BASE_URL = "https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/494997652994b36b2351edfec51cee1c8b8c3651/runtime_hot/r39_engine_v36.py"
req = urllib.request.Request(BASE_URL, headers={"User-Agent": "swrlz-r39-v37"})
with urllib.request.urlopen(req, timeout=20) as response:
    source = response.read(4_000_001)
if len(source) > 4_000_000:
    raise RuntimeError("R39_V36_SOURCE_TOO_LARGE")
exec(compile(source.decode("utf-8"), BASE_URL + "#v37", "exec"), globals(), globals())

_BASE_INSPECT = inspect_engine
_BASE_GENERATE = generate_events
HOT_SERVER_VERSION = "2.1.48"
HOT_REVISION = "2.1.48-hot-deep-inference-telemetry-v37"
_impl.HOT_SERVER_VERSION = HOT_SERVER_VERSION
_impl.HOT_REVISION = HOT_REVISION


def inspect_engine():
    result = _BASE_INSPECT()
    if isinstance(result, dict):
        result.update({
            "hotServerVersion": HOT_SERVER_VERSION,
            "hotRevision": HOT_REVISION,
            "deepInferenceTelemetry": True,
            "telemetryContract": "r39-deep-inference-telemetry-v1",
            "telemetryChangesInference": False,
        })
    return result


def generate_events(payload, is_cancelled=None):
    started = time.monotonic()
    prefill_started = None
    decode_started = None
    first_delta = None
    deltas = 0
    chars = 0
    yield {"type":"STATUS","phase":"INFERENCE_TELEMETRY","reason":"telemetry-v1 start"}
    for event in _BASE_GENERATE(payload, is_cancelled):
        if isinstance(event, dict):
            now = time.monotonic()
            phase = str(event.get("phase") or "")
            kind = str(event.get("type") or "")
            if prefill_started is None and phase.startswith("PREFILL"):
                prefill_started = now
                yield {"type":"STATUS","phase":"INFERENCE_TELEMETRY","reason":f"telemetry-v1 prefill-start wallMs={int((now-started)*1000)}"}
            if decode_started is None and phase == "GENERATING":
                decode_started = now
                anchor = prefill_started or started
                yield {"type":"STATUS","phase":"INFERENCE_TELEMETRY","reason":f"telemetry-v1 decode-start prefillWallMs={int((now-anchor)*1000)}"}
            if kind == "DELTA":
                deltas += 1
                chars += len(str(event.get("text") or ""))
                if first_delta is None:
                    first_delta = now
                    anchor = decode_started or prefill_started or started
                    yield {"type":"STATUS","phase":"INFERENCE_TELEMETRY","reason":f"telemetry-v1 first-delta decodeWaitMs={int((now-anchor)*1000)} totalMs={int((now-started)*1000)}"}
            if phase == "PERF_METRICS":
                yield {"type":"STATUS","phase":"INFERENCE_TELEMETRY","reason":"telemetry-v1 engine " + str(event.get("reason") or "")[:900]}
            if kind in {"COMPLETED", "FAILED"}:
                yield {"type":"STATUS","phase":"INFERENCE_TELEMETRY","reason":f"telemetry-v1 terminal={kind.lower()} totalMs={int((now-started)*1000)} deltaEvents={deltas} deltaChars={chars}"}
        yield event
