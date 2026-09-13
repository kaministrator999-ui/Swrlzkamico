"""R39 hot v26: requirement-driven response planning over v25.

Preserves v25 semantic requirement ledger and truthful completion while turning the
ledger into an ordered response plan before decoding begins.
"""
from __future__ import annotations
import urllib.request

_V25_COMMIT = "64d66949d0c1af42a31a93d2f5a59b02e8bca038"
_V25_URL = f"https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/{_V25_COMMIT}/runtime_hot/r39_engine_v25.py"
_req = urllib.request.Request(_V25_URL, headers={"User-Agent": "swrlz-hot-r39-v26"})
with urllib.request.urlopen(_req, timeout=20) as _response:
    _source = _response.read(4_000_001)
if len(_source) > 4_000_000:
    raise RuntimeError("R39_V25_SOURCE_TOO_LARGE")
exec(compile(_source.decode("utf-8"), _V25_URL + "#v26", "exec"), globals(), globals())

_V25_GENERATE = globals().get("generate_events")
_V25_INSPECT = globals().get("inspect_engine")

HOT_SERVER_VERSION = "2.1.36"
HOT_REVISION = "2.1.36-hot-requirement-plan-rmcca-trace-v26"
_impl.HOT_SERVER_VERSION = HOT_SERVER_VERSION
_impl.HOT_REVISION = HOT_REVISION

def _response_plan(req):
    phases = []
    if req.get("architectureFirst"):
        phases.append("1) ARCHITECTURE: explain the design briefly (target about 50-80 tokens).")
    if req.get("requireRunnableCode"):
        lang = "Python " if req.get("requirePython") else ""
        constraints = []
        if req.get("recentWindow") is not None:
            constraints.append(f"keep exactly the most recent {req['recentWindow']} messages always available")
        if req.get("maxRetrievedOlder") is not None:
            constraints.append(f"return at most {req['maxRetrievedOlder']} retrieved older messages")
        constraint_text = "; ".join(constraints)
        phases.append(
            "2) RUNNABLE ARTIFACT: immediately provide one complete runnable "
            f"{lang}implementation"
            + (f" that actually enforces: {constraint_text}." if constraint_text else ".")
            + " Do not substitute pseudocode, placeholder functions, sample output, or commentary for the implementation."
        )
    if req.get("requireExample"):
        phases.append("3) EXAMPLE: demonstrate the implementation retrieving a relevant older message from an earlier turn.")
    if req.get("requirePrefillExplanation"):
        phases.append("4) PREFILL COST: briefly explain why sending only recent + retrieved relevant history reduces prompt-prefill work versus sending the entire thread.")
    if not phases:
        return ""
    return (
        "Execution plan for this response (internal; do not quote or label it in the answer): "
        + " ".join(phases)
        + " Complete each phase in order. Budget priority is the runnable artifact first after the brief architecture. "
          "If space becomes tight, shorten prose rather than omitting code or explicit numeric constraints."
    )

def _prepare_v26_payload(payload):
    prepared = _prepare_v25_payload(payload)
    req = prepared.get("_swrlzRequirementLedger") or {}
    plan = _response_plan(req)
    if plan:
        existing = str(prepared.get("responseDirective") or "").strip()
        prepared["responseDirective"] = (existing + " " + plan).strip()
        prepared["_swrlzResponsePlan"] = {
            "ordered": True,
            "architectureFirst": bool(req.get("architectureFirst")),
            "artifactEarly": bool(req.get("requireRunnableCode")),
            "exampleAfterArtifact": bool(req.get("requireExample")),
            "prefillExplanationLast": bool(req.get("requirePrefillExplanation")),
            "recentWindow": req.get("recentWindow"),
            "maxRetrievedOlder": req.get("maxRetrievedOlder"),
        }
    return prepared

def inspect_engine():
    result = _V25_INSPECT()
    if isinstance(result, dict):
        result.update({
            "hotServerVersion": HOT_SERVER_VERSION,
            "hotRevision": HOT_REVISION,
            "requirementDrivenResponsePlanner": True,
            "artifactEarlyPlan": True,
            "orderedLedgerExecution": True,
            "plannerShortensProseBeforeDroppingArtifact": True,
            "responsePlanTransportField": "_swrlzResponsePlan",
            "v25SourceCommit": _V25_COMMIT,
        })
    return result

def generate_events(payload, is_cancelled=None):
    prepared = _prepare_v26_payload(payload)
    plan = prepared.get("_swrlzResponsePlan") or {}
    if plan:
        yield {
            "type": "STATUS",
            "phase": "RESPONSE_PLAN",
            "reason": (
                "Requirement-driven response plan armed: brief architecture -> runnable artifact -> example -> prefill explanation; "
                f"recent-window={plan.get('recentWindow')}; max-retrieved-older={plan.get('maxRetrievedOlder')}."
            ),
        }
    for event in _V25_GENERATE(prepared, is_cancelled):
        yield event
