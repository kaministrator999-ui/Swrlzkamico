"""R39 v79: inherited research-call camera over preserved v78 behavior.

Observability only. Instruments the captured v49 callable used by the v50 semantic
research planner, because planner payloads intentionally rewrite profileId to LALM.
This distinguishes planner-internal offline inference from the user's outer online
research request without changing routing or model semantics.
"""
from __future__ import annotations
import json,time

_V79_CONTRACT="r39-v79-inherited-research-call-camera-v1"
_V78_GENERATE_V79=generate_events
_V78_INSPECT_V79=inspect_engine
_V49_GENERATE_V79=_V49_GENERATE

def _v79_profile(payload):
    data=payload if isinstance(payload,dict) else {}
    profile=str(data.get("profileId") or "")[:96]
    p=profile.strip().upper()
    return profile,(p.endswith("+ONLINE") or p.endswith(":ONLINE") or p=="ONLINE")

def _v79_v49_generate(payload,is_cancelled=None):
    profile,online=_v79_profile(payload)
    data=payload if isinstance(payload,dict) else {}
    print("SWRLZ_R39_INHERITED_RESEARCH_CALL "+json.dumps({
        "contract":_V79_CONTRACT,
        "stage":"v49-call",
        "atUnixMs":int(time.time()*1000),
        "requestId":str(data.get("requestId") or "")[:160],
        "profileId":profile,
        "profileOnline":online,
        "hasResearchPlan":isinstance(data.get("researchPlan"),dict),
        "hasOnlineEvidence":isinstance(data.get("onlineEvidence"),dict),
        "generationMaxTokens":(data.get("generation") or {}).get("maxTokens") if isinstance(data.get("generation"),dict) else None,
    },ensure_ascii=False,separators=(",",":")),flush=True)
    for event in _V49_GENERATE_V79(payload,is_cancelled):
        yield event

_V49_GENERATE=_v79_v49_generate

def generate_events(payload,is_cancelled=None):
    for event in _V78_GENERATE_V79(payload,is_cancelled):
        yield event

def inspect_engine():
    result=_V78_INSPECT_V79()
    if isinstance(result,dict):
        result.update({
            "hotServerVersion":"2.1.91",
            "hotRevision":"2.1.91-hot-inherited-research-call-camera-v79",
            "v78Preserved":True,
            "inheritedResearchCallCamera":True,
            "inheritedResearchCallCameraContract":_V79_CONTRACT,
            "inheritedResearchCallCameraChangesSemantics":False,
        })
    return result

HOT_SERVER_VERSION="2.1.91"
HOT_REVISION="2.1.91-hot-inherited-research-call-camera-v79"
_impl.HOT_SERVER_VERSION=HOT_SERVER_VERSION
_impl.HOT_REVISION=HOT_REVISION
