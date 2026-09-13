"""R39 hot v23: continuity-safe cognition transport + bounded generation over v22."""
from __future__ import annotations
import json
import re
import urllib.request

_V22_COMMIT = "5c59eac61256bc76b9eca6e33843ff7d4911877e"
_V22_URL = f"https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/{_V22_COMMIT}/runtime_hot/r39_engine.py"
_req = urllib.request.Request(_V22_URL, headers={"User-Agent": "swrlz-hot-r39-v23"})
with urllib.request.urlopen(_req, timeout=20) as _response:
    _source = _response.read(4_000_001)
if len(_source) > 4_000_000:
    raise RuntimeError("R39_V22_SOURCE_TOO_LARGE")
exec(compile(_source.decode("utf-8"), _V22_URL + "#v23", "exec"), globals(), globals())

_CARRIER = "[[SWRLZ_RMCCA_TRANSPORT_V1:"
_PREFILL_RE = re.compile(r"Prefill new (\d+)/(\d+) · cached (\d+) · ([0-9.]+)s token · ([0-9.]+)s avg · ETA ([0-9.]+)s · backend=([^.]*)\.?$")
_UPPER_NOISE_RE = re.compile(r"(?:\b[A-Z]{2,8}\b[.!?\s]*){5,}")

_BASE_POLICY += (
    " Evidence discipline: never invent retrieved messages, benchmark measurements, scores, percentages, test results, "
    "or repository facts. If an example is hypothetical, label it as an example. If a requested fact was not measured "
    "or supplied, say that rather than manufacturing a number."
)
_TASK_POLICIES["coding"] += (
    " Prioritize the requested runnable artifact before extended commentary. Do not repeat sections already completed. "
    "If output budget is becoming tight, finish syntactically coherent code and the minimum necessary explanation rather than padding."
)


def _decode_carrier(text):
    value = str(text or "")
    if not value.startswith(_CARRIER) or not value.endswith("]]" ):
        return None
    try:
        data = json.loads(value[len(_CARRIER):-2])
        return data if isinstance(data, dict) and data.get("v") == 1 else None
    except Exception:
        return None


def _restore_transport(payload):
    clone = dict(payload)
    history = []
    carrier = None
    for item in list(clone.get("history") or []):
        if isinstance(item, dict):
            decoded = _decode_carrier(item.get("text"))
            if decoded is not None:
                carrier = decoded
                continue
        history.append(item)
    clone["history"] = history
    restored = False
    if isinstance(carrier, dict):
        e = carrier.get("e")
        if isinstance(e, dict) and isinstance(e.get("cognitiveClock"), dict):
            clone["swrlzCognitiveContext"] = {
                "envelopeId": str(e.get("envelopeId") or "swrlz-rmcca-context-v3"),
                "directiveId": str(e.get("directiveId") or "rmcca-cognitive-policy-v4-social-participation"),
                "architecture": "RMCCA",
                "architectureVersion": 4,
                "cognitiveClock": e["cognitiveClock"],
                "transportRestored": True,
            }
            restored = True
        t = carrier.get("t")
        if isinstance(t, dict):
            clone["swrlzUserTimeContext"] = {k: str(t.get(k) or "") for k in ("localDate", "localTime", "daypart", "timeZone", "utcOffset")}
    clone["_swrlzTransportRestored"] = restored
    return clone


_BASE_PLAN = _impl._plan_response_budget

def _bounded_plan(payload):
    result = dict(_BASE_PLAN(payload))
    generation = payload.get("generation") if isinstance(payload.get("generation"), dict) else {}
    if result.get("kind") == "coding" and str(generation.get("budgetMode") or "").lower() != "manual":
        result["planned"] = min(int(result.get("planned", 384)), 352)
        result["wrapAt"] = min(int(result.get("wrapAt", 300)), 304)
        result["hard"] = min(int(result.get("hard", 576)), 448)
    return result
_impl._plan_response_budget = _bounded_plan

_BASE_GAPS = _impl._response_contract_gaps

def _bounded_gaps(text, contract):
    gaps = list(_BASE_GAPS(text, contract))
    words = len(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", str(text or "")))
    if words >= 260 and gaps == ["complete-code"]:
        return []
    return gaps
_impl._response_contract_gaps = _bounded_gaps


def _outside_fences(text):
    parts = str(text or "").split("```")
    return "\n".join(parts[::2])


def _degenerate(text):
    prose = _outside_fences(text)[-500:]
    if _UPPER_NOISE_RE.search(prose):
        return True
    words = re.findall(r"[A-Za-z]{2,20}", prose.lower())[-40:]
    return len(words) >= 24 and len(set(words)) / max(1, len(words)) < 0.28


_V22_INSPECT = globals().get("inspect_engine")
_V22_GENERATE = globals().get("generate_events")
HOT_SERVER_VERSION = "2.1.33"
HOT_REVISION = "2.1.33-hot-continuity-rmcca-guard-v23"
_impl.HOT_SERVER_VERSION = HOT_SERVER_VERSION
_impl.HOT_REVISION = HOT_REVISION


def inspect_engine():
    result = _V22_INSPECT()
    if isinstance(result, dict):
        result.update({
            "hotServerVersion": HOT_SERVER_VERSION,
            "hotRevision": HOT_REVISION,
            "rmccaTransportCarrierV1": True,
            "rmccaTransportRestoredBeforeInference": True,
            "bestPartialRecoveryPolicy": "chat-runtime-overlay",
            "codingGenerationHardCapDefault": 448,
            "degenerationGuard": True,
            "blockAwarePrefillTelemetry": True,
            "v22SourceCommit": _V22_COMMIT,
        })
    return result


def generate_events(payload, is_cancelled=None):
    prepared = _restore_transport(payload)
    response_text = ""
    for event in _V22_GENERATE(prepared, is_cancelled):
        if not isinstance(event, dict):
            yield event
            continue
        event = dict(event)
        if event.get("type") == "STATUS" and event.get("phase") == "PREFILL":
            match = _PREFILL_RE.fullmatch(str(event.get("reason") or ""))
            if match:
                ordinal,total,cached,block_s,_avg,eta,backend = match.groups()
                ordinal_i,total_i = int(ordinal),int(total)
                if ordinal_i % _impl._PREFILL_CHECKPOINT_EVERY != 0 and ordinal_i != total_i:
                    continue
                block_tokens = ordinal_i % _impl._PREFILL_CHECKPOINT_EVERY or _impl._PREFILL_CHECKPOINT_EVERY
                seconds = float(block_s)
                rate = block_tokens / seconds if seconds > 0 else 0.0
                event["reason"] = (
                    f"Prefill batch flush · through {ordinal_i}/{total_i} new token(s) · cached {cached} · "
                    f"block={block_tokens} token(s) · {seconds:.3f}s · {rate:.2f} tok/s · ETA {eta}s · backend={backend}."
                )
        if event.get("type") == "DELTA":
            response_text += str(event.get("text") or "")
            if _degenerate(response_text):
                yield {"type":"STATUS","phase":"DEGENERATION_GUARD","reason":"Generation entered a repetitive/fragmented loop; preserving the coherent response already produced instead of extending noise."}
                yield {"type":"COMPLETED","phase":"COMPLETE","reason":"Generation stopped by continuity guard after repetitive-output detection; coherent partial response preserved."}
                return
        yield event
