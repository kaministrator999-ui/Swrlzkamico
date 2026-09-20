"""R39 v80: research telemetry scope repair over preserved v79 behavior.

Observability-only repair. The inherited v48 research-policy camera is correct for
its payload but ambiguous when v50 runs an internal offline planning inference under
the outer requestId. v80 scopes that internal pass explicitly so telemetry cannot be
mistaken for the user's outer AUTO+ONLINE intent.
"""
from __future__ import annotations
import json,time

_V80_CONTRACT="r39-v80-research-telemetry-scope-v1"
_V79_GENERATE_V80=generate_events
_V79_INSPECT_V80=inspect_engine
_V49_GENERATE_V80=_V49_GENERATE

def _v80_profile(payload):
    data=payload if isinstance(payload,dict) else {}
    profile=str(data.get("profileId") or "")[:96]
    p=profile.strip().upper()
    return profile,(p.endswith("+ONLINE") or p.endswith(":ONLINE") or p=="ONLINE")

def _v80_v49_generate(payload,is_cancelled=None):
    data=payload if isinstance(payload,dict) else {}
    profile,online=_v80_profile(data)
    internal_planner=(profile.strip().upper()=="LALM" and
                      isinstance(data.get("generation"),dict) and
                      data.get("generation",{}).get("maxTokens")==160 and
                      not isinstance(data.get("researchPlan"),dict) and
                      not isinstance(data.get("onlineEvidence"),dict))
    print("SWRLZ_R39_RESEARCH_SCOPE "+json.dumps({
        "contract":_V80_CONTRACT,
        "stage":"inherited-v49-call",
        "atUnixMs":int(time.time()*1000),
        "requestId":str(data.get("requestId") or "")[:160],
        "inferenceScope":"internal-research-planner" if internal_planner else "inherited-generation",
        "outerUserOnlineState":"not-represented-by-this-payload" if internal_planner else "payload-derived",
        "profileId":profile,
        "payloadOnline":online,
        "researchPolicyFalseMeaning":"expected-internal-offline-planner" if internal_planner and not online else "payload-policy-result",
    },ensure_ascii=False,separators=(",",":")),flush=True)
    for event in _V49_GENERATE_V80(payload,is_cancelled):
        yield event

_V49_GENERATE=_v80_v49_generate

def generate_events(payload,is_cancelled=None):
    for event in _V79_GENERATE_V80(payload,is_cancelled):
        yield event

def inspect_engine():
    result=_V79_INSPECT_V80()
    if isinstance(result,dict):
        result.update({
            "hotServerVersion":"2.1.92",
            "hotRevision":"2.1.92-hot-research-telemetry-scope-v80",
            "v79Preserved":True,
            "researchTelemetryScopeCamera":True,
            "researchTelemetryScopeContract":_V80_CONTRACT,
            "researchTelemetryScopeChangesSemantics":False,
        })
    return result

HOT_SERVER_VERSION="2.1.92"
HOT_REVISION="2.1.92-hot-research-telemetry-scope-v80"
_impl.HOT_SERVER_VERSION=HOT_SERVER_VERSION
_impl.HOT_REVISION=HOT_REVISION
