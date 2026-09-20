"""R39 v81: bounded batch-prefill fallback-detail camera over preserved v80 behavior.

Observability only. Current production metrics prove complete batch fallback but do not
expose lastBatchFallback, so the failure class cannot yet be fixed safely. v81 emits
that already-bounded metric at PERF_METRICS without logging prompt/token/model data.
"""
from __future__ import annotations
import json,time

_V81_CONTRACT="r39-v81-batch-fallback-detail-v1"
_V80_GENERATE_V81=generate_events
_V80_INSPECT_V81=inspect_engine

def _v81_log(request_id,detail):
    print("SWRLZ_R39_BATCH_FALLBACK "+json.dumps({
        "contract":_V81_CONTRACT,
        "stage":"prefill-fallback-detail",
        "atUnixMs":int(time.time()*1000),
        "requestId":str(request_id or "")[:160],
        "lastBatchFallback":str(detail or "")[:240],
    },ensure_ascii=False,separators=(",",":")),flush=True)

def generate_events(payload,is_cancelled=None):
    request_id=_request_id(payload) if isinstance(payload,dict) else ""
    for event in _V80_GENERATE_V81(payload,is_cancelled):
        if str(event.get("phase") or "")=="PERF_METRICS":
            metrics=getattr(_batch._TLS,"metrics",None) if globals().get("_batch") is not None else None
            detail=metrics.get("lastBatchFallback") if isinstance(metrics,dict) else ""
            if detail:_v81_log(request_id,detail)
        yield event

def inspect_engine():
    result=_V80_INSPECT_V81()
    if isinstance(result,dict):
        result.update({
            "hotServerVersion":"2.1.93",
            "hotRevision":"2.1.93-hot-batch-fallback-detail-v81",
            "v80Preserved":True,
            "batchFallbackDetailCamera":True,
            "batchFallbackDetailContract":_V81_CONTRACT,
            "batchFallbackDetailChangesSemantics":False,
        })
    return result

HOT_SERVER_VERSION="2.1.93"
HOT_REVISION="2.1.93-hot-batch-fallback-detail-v81"
_impl.HOT_SERVER_VERSION=HOT_SERVER_VERSION
_impl.HOT_REVISION=HOT_REVISION
