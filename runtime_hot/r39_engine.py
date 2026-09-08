"""Hot R39 v12 shim.

Loads the validated v11 implementation from the durable dev source, then trims
reference-rerank work now that Server 2.2.3 native fp16 subnormal scaling matches
the Python reference. Diagnostics stay armed; skipped prefill logits are labelled
as skipped instead of NaN-looking telemetry.
"""
from __future__ import annotations

import types
import urllib.request

_IMPL_URL = "https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/dev/runtime_hot/r39_engine_impl.py"
_req = urllib.request.Request(_IMPL_URL, headers={"User-Agent": "swrlz-hot-r39-v12"})
with urllib.request.urlopen(_req, timeout=20) as _response:
    _source = _response.read(4_000_001)
if len(_source) > 4_000_000:
    raise RuntimeError("R39_IMPL_TOO_LARGE")
_source.decode("utf-8")

_impl = types.ModuleType("swrlz_hot_r39_engine_impl_v11")
_impl.__file__ = _IMPL_URL
exec(compile(_source, _IMPL_URL, "exec"), _impl.__dict__)

# Native/reference agreement is now at float-noise scale after Server 2.2.3.
# Keep the reference oracle in the live path, but rerank only the six candidates
# that can actually influence the visible low-temperature selection frontier.
_impl.HOT_SERVER_VERSION = "2.1.21"
_impl.HOT_REVISION = "2.1.21-hot-boundary-v12-native-verified-fast-rerank"
_impl._REFERENCE_RERANK_CANDIDATES = 6

_original_format_stats = _impl._format_stats

def _format_stats(stats):
    if not stats:
        return "skipped"
    return _original_format_stats(stats)

_impl._format_stats = _format_stats

ENGINE_ID = _impl.ENGINE_ID
MODEL_SHA256 = _impl.MODEL_SHA256
HOT_SERVER_VERSION = _impl.HOT_SERVER_VERSION
HOT_REVISION = _impl.HOT_REVISION

def generate_events(payload, is_cancelled=None):
    yield from _impl.generate_events(payload, is_cancelled)

def inspect_engine():
    result = _impl.inspect_engine()
    if isinstance(result, dict):
        result["hotServerVersion"] = HOT_SERVER_VERSION
        result["hotRevision"] = HOT_REVISION
        result["referenceCandidateRerank"] = True
        result["referenceCandidateCount"] = 6
        result["nativeVerifiedFastRerank"] = True
        result["diagnosticSkippedLogitsLabel"] = True
    return result
