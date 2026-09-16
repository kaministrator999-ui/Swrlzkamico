"""R39 v52: evidence-driven coding and debugging reasoning.

Extends v51's evidence-preserving conversational recovery into software work.
The policy is deliberately diagnostic rather than verbose: locate the failing
execution boundary, preserve proven-good stages, discriminate causes, patch the
smallest responsible layer, and verify predicted consequences.
"""
from __future__ import annotations
import urllib.request

_V51_COMMIT="a30e2f53df0cbe421ee67e9de40d24a999f9bb17"
_V51_URL=f"https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/{_V51_COMMIT}/runtime_hot/r39_engine_v51.py"
_req=urllib.request.Request(_V51_URL,headers={"User-Agent":"swrlz-r39-v52"})
with urllib.request.urlopen(_req,timeout=20) as _response:_source=_response.read(4_000_001)
if len(_source)>4_000_000:raise RuntimeError("R39_V51_SOURCE_TOO_LARGE")
exec(compile(_source.decode("utf-8"),_V51_URL+"#v52","exec"),globals(),globals())

_V51_INSPECT=inspect_engine
_V51_GENERATE=generate_events
HOT_SERVER_VERSION="2.1.63"
HOT_REVISION="2.1.63-hot-evidence-coding-reasoner-v52"
_impl.HOT_SERVER_VERSION=HOT_SERVER_VERSION
_impl.HOT_REVISION=HOT_REVISION

_CODING_REASONING_POLICY=(
 "Coding/debugging contract: reason from execution evidence before editing. "
 "Locate the narrowest confirmed failing boundary in the pipeline and preserve stages already proven good. "
 "Separate OBSERVED behavior, INFERRED cause, and UNKNOWN cause; an error message or failed phase constrains the search but does not by itself prove the root cause. "
 "Build a small competing-hypothesis set and prefer the next diagnostic that most strongly discriminates among those hypotheses. "
 "Trace ownership and data flow across client, transport, server, persistence, inference, and rendering boundaries instead of patching the layer where the symptom merely appears. "
 "When concurrency is plausible, inspect read-modify-write races, stale snapshots, idempotency identity, revision ownership, retry behavior, and exact read-back verification. "
 "Patch the smallest responsible layer while preserving architectural invariants and fail-closed safety boundaries; never make an error disappear by bypassing the guarantee that exposed it. "
 "Before a patch, predict concrete consequences: what should become observable if the hypothesis is correct, and what observation would falsify it. "
 "After a patch, verify syntax/contract compatibility, the original reproduction path, negative/failure behavior, and regression-sensitive neighboring paths. "
 "For code generation, maintain a requirement ledger: interfaces, invariants, edge cases, concurrency assumptions, error semantics, and acceptance checks. Do not silently drop requirements to fit response budget. "
 "Prefer explicit state transitions and idempotent operations over timing assumptions. Preserve useful failure telemetry without leaking secrets or raw private content. "
 "Core loop: symptom -> execution boundary -> evidence -> competing causes -> discriminating check -> minimal patch -> predicted consequence -> verification."
)

def _with_coding_reasoning(payload):
    if not isinstance(payload,dict):return payload
    enriched=dict(payload)
    history=list(enriched.get("history") or [])
    marker={"role":"system","text":_CODING_REASONING_POLICY}
    enriched["history"]=[marker]+history
    return enriched

def inspect_engine():
    result=_V51_INSPECT()
    if isinstance(result,dict):result.update({
        "hotServerVersion":HOT_SERVER_VERSION,
        "hotRevision":HOT_REVISION,
        "evidenceDrivenCodingReasoning":True,
        "executionBoundaryLocalization":True,
        "competingHypothesisDebugging":True,
        "discriminatingDiagnosticSelection":True,
        "minimalResponsibleLayerPatch":True,
        "predictedConsequenceVerification":True,
        "concurrencyRaceReasoning":True,
        "codingReasoningContract":"swrlz_coding_reasoning_v1",
        "v51SourceCommit":_V51_COMMIT,
    })
    return result

def generate_events(payload,is_cancelled=None):
    request_id=_request_id(payload) if isinstance(payload,dict) else ""
    enriched=_with_coding_reasoning(payload)
    _camera(request_id,"coding-reasoning",contract="swrlz_coding_reasoning_v1",executionBoundary=True,evidenceBoundary=True,minimalPatch=True,verificationPrediction=True)
    for event in _V51_GENERATE(enriched,is_cancelled):yield event
