"""R39 v53: map-to-the-point selective activation + directional cue routing.

Integrates two reasoning lessons:
1) tiny cues should act as coordinates into learned context, not copies of it;
2) explicit contrast/exclusion in the current turn must prune inference before
   associative expansion. Preserve unresolved slots instead of manufacturing them.
"""
from __future__ import annotations
import urllib.request

_V52_COMMIT="3670f9c777b7425e7033bcedcbf7539b19b8965c"
_V52_URL=f"https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/{_V52_COMMIT}/runtime_hot/r39_engine_v52.py"
_req=urllib.request.Request(_V52_URL,headers={"User-Agent":"swrlz-r39-v53"})
with urllib.request.urlopen(_req,timeout=20) as _response:_source=_response.read(4_000_001)
if len(_source)>4_000_000:raise RuntimeError("R39_V52_SOURCE_TOO_LARGE")
exec(compile(_source.decode("utf-8"),_V52_URL+"#v53","exec"),globals(),globals())

_V52_INSPECT=inspect_engine
_V52_GENERATE=generate_events
HOT_SERVER_VERSION="2.1.64"
HOT_REVISION="2.1.64-hot-map-to-point-selective-activation-v53"
_impl.HOT_SERVER_VERSION=HOT_SERVER_VERSION
_impl.HOT_REVISION=HOT_REVISION

_MAP_TO_POINT_POLICY=(
 "Map-to-the-point reasoning contract. Read the map facing you before reconstructing terrain behind it. "
 "The current user's wording contains routing information: contrasts, exclusions, corrections, emphasis, sequencing, references, unfinished clauses, and directional operators such as not, but, except, instead, also, yet, specifically, other, and not only. "
 "Parse those surface constraints BEFORE associative expansion. Explicit directional language constrains inference. Mark interpretations the user has excluded, corrected, or already covered as low priority; do not spend inference budget elaborating them merely because they are salient in prior context. "
 "Identify the unresolved semantic opening created by the wording. If the destination is underdetermined, preserve that opening and let the user supply the next coordinate rather than manufacturing a hidden answer. Uncertainty is valid state. "
 "Only after surface routing should deeper context, memory, analogy, latent reconstruction, or anticipatory inference activate. Verify that the response advances toward the unresolved point rather than circling back to a branch the user just deprioritized. "
 "Treat compact cues as coordinates into already-learned structure, not miniature payloads containing the entire structure. A tiny greeting, callback, glyph, joke, correction, or task cue may selectively reactivate relationships, user-state, task-state, correction history, or response conventions only when learned associations justify that activation. "
 "Prefer the smallest sufficient contextual neighborhood. Rank candidate context by immediate relevance, continuity, recency, correction history, active task state, explicit current-turn constraints, and demonstrated associations. Do not flood inference with the whole mosaic. "
 "When confidence is low, preserve multiple candidate interpretations instead of forcing one reconstruction. Anticipatory activation is allowed, but must be followed by evidence/context verification. A successful coincidence or prediction is a hit, not proof that every intuition is correct. "
 "Measure prefill/retrieval quality by downstream coherence, correct activation, low corrective-turn cost, and useful context reactivation per unit of prefill—not token count alone. "
 "Routing sequence: surface statement -> directional operators -> constraint/exclusion pruning -> unresolved target -> smallest sufficient selective context activation -> candidate verification -> response. "
 "Compressed doctrine: read the literal cue; honor the contrast; prune the wrong branch; preserve the unknown; then map-to-the-point. Don't transmit the mosaic when a coordinate can reactivate it."
)

def _with_map_to_point(payload):
    if not isinstance(payload,dict):return payload
    enriched=dict(payload)
    history=list(enriched.get("history") or [])
    enriched["history"]=[{"role":"system","text":_MAP_TO_POINT_POLICY}]+history
    return enriched

def inspect_engine():
    result=_V52_INSPECT()
    if isinstance(result,dict):result.update({
        "hotServerVersion":HOT_SERVER_VERSION,
        "hotRevision":HOT_REVISION,
        "mapToPointReasoning":True,
        "surfaceDirectionalRouting":True,
        "constraintFirstCandidatePruning":True,
        "unresolvedSlotPreservation":True,
        "selectiveContextActivation":True,
        "compactCueCoordinateActivation":True,
        "smallestSufficientContextNeighborhood":True,
        "anticipatoryActivationVerification":True,
        "multiCandidatePreservationOnLowConfidence":True,
        "prefillOptimizationObjective":"useful-context-reactivation-per-unit-prefill",
        "mapToPointContract":"swrlz_map_to_point_v1",
        "v52SourceCommit":_V52_COMMIT,
    })
    return result

def generate_events(payload,is_cancelled=None):
    request_id=_request_id(payload) if isinstance(payload,dict) else ""
    enriched=_with_map_to_point(payload)
    _camera(request_id,"map-to-point",contract="swrlz_map_to_point_v1",surfaceFirst=True,constraintPruning=True,preserveUnknown=True,selectiveActivation=True,verifyAnticipation=True)
    for event in _V52_GENERATE(enriched,is_cancelled):yield event
