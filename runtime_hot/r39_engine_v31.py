"""R39 hot v31 dense-weight cached batched-prefill overlay.

Pins the proven v27 cursor layer and a self-contained v26 batch engine whose block
matmuls retain eligible decoded float32 weights in the warm worker. Native quantized
matmat remains the fallback when cache budget/item bounds are exceeded.
"""
from __future__ import annotations
import urllib.request

_V27_COMMIT = "a7de2c488f97dc4f2f6d019e88edea7021ab2dfc"
_BATCH_COMMIT = "91f64d2de9a98d7b88ef72b4d64a9bcb696fbbcd"
_V27_URL = f"https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/{_V27_COMMIT}/runtime_hot/r39_engine_v27.py"
_req = urllib.request.Request(_V27_URL, headers={"User-Agent": "swrlz-hot-r39-v31"})
with urllib.request.urlopen(_req, timeout=20) as _response:
    source = _response.read(4_000_001)
if len(source) > 4_000_000: raise RuntimeError("R39_V27_SOURCE_TOO_LARGE")
text = source.decode("utf-8")
_old = '''_V26_COMMIT = "3dc70e8d02777fd622db3ae3311fad13b7382e6a"
_V26_URL = f"https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/{_V26_COMMIT}/runtime_hot/r39_engine.py"
'''
_new = f'''_V26_COMMIT = "{_BATCH_COMMIT}"
_V26_URL = f"https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/{{_V26_COMMIT}}/runtime_hot/r39_engine_v26_batch.py"
'''
if _old not in text: raise RuntimeError("R39_V31_V27_BASE_TARGET_MISSING")
text = text.replace(_old, _new, 1)
exec(compile(text, _V27_URL + "#v31", "exec"), globals(), globals())

_impl.HOT_SERVER_VERSION = "2.1.40"
_impl.HOT_REVISION = "2.1.40-hot-boundary-v31-dense-weight-batched-prefill-v4.1"
HOT_SERVER_VERSION = _impl.HOT_SERVER_VERSION
HOT_REVISION = _impl.HOT_REVISION
_V27_INSPECT_FOR_V31 = inspect_engine

def inspect_engine():
    result = _V27_INSPECT_FOR_V31()
    if isinstance(result, dict):
        result.update({
            "hotServerVersion": HOT_SERVER_VERSION,
            "hotRevision": HOT_REVISION,
            "batchedPromptPrefill": True,
            "batchBlockTokens": 64,
            "batchKernelAvailable": bool(callable(getattr(_impl.native_bridge, "matmat_available", None)) and _impl.native_bridge.matmat_available()),
            "batchKernel": "dense-f32-gemm-cache-with-direct-quantized-matmat-fallback",
            "batchIntermediateVocabularyProjection": False,
            "batchCursorSemantics": "v27-region-shared-exact-prefix-preserved",
            "batchDenseCacheBudgetMiB": 384,
            "batchDenseItemMaxMiB": 48,
            "batchSourceCommit": _BATCH_COMMIT,
            "cursorSourceCommit": _V27_COMMIT,
        })
    return result
