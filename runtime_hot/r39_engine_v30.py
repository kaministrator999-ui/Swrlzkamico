"""R39 hot v30 staged batched-prefill overlay.

Not live until runtime_hot/r39_engine.py is deliberately switched to v30 after a base
image containing swyrlz._r39_batch is built. v30 preserves v27 region-shared cursor
semantics and substitutes the v26 engine beneath it with the block-prefill variant.
"""
from __future__ import annotations

import urllib.request

_V27_URL = "https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/dev/runtime_hot/r39_engine_v27.py"
_req = urllib.request.Request(_V27_URL, headers={"User-Agent": "swrlz-hot-r39-v30"})
with urllib.request.urlopen(_req, timeout=20) as _response:
    source = _response.read(4_000_001)
if len(source) > 4_000_000:
    raise RuntimeError("R39_V27_SOURCE_TOO_LARGE")
text = source.decode("utf-8")
_old = '''_V26_COMMIT = "3dc70e8d02777fd622db3ae3311fad13b7382e6a"
_V26_URL = f"https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/{_V26_COMMIT}/runtime_hot/r39_engine.py"
'''
_new = '''_V26_COMMIT = "dev-batched-prefill"
_V26_URL = "https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/dev/runtime_hot/r39_engine_v26_batch.py"
'''
if _old not in text:
    raise RuntimeError("R39_V30_V27_BASE_TARGET_MISSING")
text = text.replace(_old, _new, 1)
exec(compile(text, _V27_URL + "#v30", "exec"), globals(), globals())

_impl.HOT_SERVER_VERSION = "2.1.39"
_impl.HOT_REVISION = "2.1.39-hot-boundary-v30-native-batched-prefill-v4.0"
HOT_SERVER_VERSION = _impl.HOT_SERVER_VERSION
HOT_REVISION = _impl.HOT_REVISION

_V27_INSPECT_FOR_V30 = inspect_engine

def inspect_engine():
    result = _V27_INSPECT_FOR_V30()
    if isinstance(result, dict):
        result.update({
            "hotServerVersion": HOT_SERVER_VERSION,
            "hotRevision": HOT_REVISION,
            "batchedPromptPrefillStaged": True,
            "batchBlockTokens": 64,
            "batchKernelAvailable": bool(callable(getattr(_impl.native_bridge, "matmat_available", None)) and _impl.native_bridge.matmat_available()),
            "batchKernel": "direct-quantized-matmat-token-columns",
            "batchIntermediateVocabularyProjection": False,
            "batchCursorSemantics": "v27-region-shared-exact-prefix-preserved",
        })
    return result
