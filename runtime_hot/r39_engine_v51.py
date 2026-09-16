"""R39 v51: evidence-preserving reasoning recovery and sparse-cue traversal.

Builds on v50 and strengthens conversational reasoning when the user teaches by
small directional cues rather than supplying the destination. The model should
separate observations, inferences, and unknowns; preserve valid prior state across
corrections; recognize invariant mechanisms beneath changing labels; and use
novel evidence-bounded inference as a stronger comprehension signal than agreement.
"""
from __future__ import annotations
import urllib.request

_V50_COMMIT="21b3ee32fa89f6f54917818802b92c8858f13913"
_V50_URL=f"https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/{_V50_COMMIT}/runtime_hot/r39_engine_v50.py"
_req=urllib.request.Request(_V50_URL,headers={"User-Agent":"swrlz-r39-v51"})
with urllib.request.urlopen(_req,timeout=20) as _response:_source=_response.read(4_000_001)
if len(_source)>4_000_000:raise RuntimeError("R39_V50_SOURCE_TOO_LARGE")
exec(compile(_source.decode("utf-8"),_V50_URL+"#v51","exec"),globals(),globals())

_V50_INSPECT=inspect_engine
_V50_GENERATE=generate_events
HOT_SERVER_VERSION="2.1.62"
HOT_REVISION="2.1.62-hot-evidence-recovery-reasoner-v51"
_impl.HOT_SERVER_VERSION=HOT_SERVER_VERSION
_impl.HOT_REVISION=HOT_REVISION

_REASONING_RECOVERY_POLICY=(
 "Reasoning recovery contract: follow the active thread beneath topic changes and treat small user cues as possible directional evidence, not automatically as requests for a full explanation. "
 "Use the smallest interpretation that explains the cue, then traverse prior context to recover the missing rung independently. "
 "Keep OBSERVATION, INFERENCE, and UNKNOWN distinct: do not invent hidden causes, motives, objects, or certainty; equally, do not discard observable shadows, incentive structure, disproportionate reactions, or convergent evidence merely because the hidden cause is unproved. "
 "When corrected, preserve every still-valid part of the prior model, replace only the disproven assumption, and retain the failure path as useful evidence. Never rewrite the earlier mistake as though it never happened. "
 "Prefer invariant mechanism over surface taxonomy when the user's point concerns structure across different labels or masks, while preserving technically meaningful distinctions. "
 "Treat repetition or a tiny referent question as a possible comprehension checksum: retrieve the relevant prior inference and verify that it remains coherent instead of assuming the user failed to understand it. "
 "Agreement and paraphrase are weak evidence of understanding. Stronger evidence is a novel inference or compression that follows from the reconstructed model and remains inside the evidence boundary. "
 "Corroborating routes may raise confidence but never convert inference into direct observation. Seek convergence without manufacturing independence. "
 "Core rule: do not invent the hidden object; do not ignore its shadow. Follow evidence far enough to discover something new, but never farther than the evidence can carry you."
)

def _with_reasoning_recovery(payload):
    if not isinstance(payload,dict):return payload
    enriched=dict(payload)
    history=list(enriched.get("history") or [])
    marker={"role":"system","text":_REASONING_RECOVERY_POLICY}
    # Keep the recovery contract close to the active dialogue without mutating caller state.
    enriched["history"]=[marker]+history
    return enriched

def inspect_engine():
    result=_V50_INSPECT()
    if isinstance(result,dict):result.update({
        "hotServerVersion":HOT_SERVER_VERSION,
        "hotRevision":HOT_REVISION,
        "evidencePreservingReasoning":True,
        "sparseCueTraversal":True,
        "correctionStatePreservation":True,
        "observationInferenceUnknownSeparation":True,
        "novelInferenceComprehensionCheck":True,
        "reasoningRecoveryContract":"swrlz_reasoning_recovery_v1",
        "v50SourceCommit":_V50_COMMIT,
    })
    return result

def generate_events(payload,is_cancelled=None):
    request_id=_request_id(payload) if isinstance(payload,dict) else ""
    enriched=_with_reasoning_recovery(payload)
    _camera(request_id,"reasoning-recovery",contract="swrlz_reasoning_recovery_v1",sparseCueTraversal=True,evidenceBoundary=True,correctionPreservesValidState=True)
    for event in _V50_GENERATE(enriched,is_cancelled):yield event
