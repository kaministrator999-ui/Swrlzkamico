"""R39 v78: online-research handoff camera over preserved v77 behavior.

Observability only. Captures bounded routing fields at the outer Brain/LALM entry so
we can distinguish an upstream handoff loss from mutation inside the R39 lineage.
No prompt, history, evidence text, tokens, logits, or hidden reasoning are logged.
"""
from __future__ import annotations
import json,time

_V78_CONTRACT="r39-v78-online-research-handoff-camera-v1"
_V77_GENERATE=generate_events
_V77_INSPECT=inspect_engine

def _v78_profile_online(profile):
    p=str(profile or "").strip().upper()
    return p.endswith("+ONLINE") or p.endswith(":ONLINE") or p=="ONLINE"

def _v78_log(payload):
    data=payload if isinstance(payload,dict) else {}
    profile=str(data.get("profileId") or "")[:96]
    record={
        "contract":_V78_CONTRACT,
        "stage":"brain-entry",
        "atUnixMs":int(time.time()*1000),
        "requestId":str(data.get("requestId") or "")[:160],
        "profileId":profile,
        "profileOnline":_v78_profile_online(profile),
        "hasResearchPlan":isinstance(data.get("researchPlan"),dict),
        "hasOnlineEvidence":isinstance(data.get("onlineEvidence"),dict),
        "payloadOnlineResearchRequested":data.get("onlineResearchRequested") if isinstance(data.get("onlineResearchRequested"),bool) else None,
    }
    print("SWRLZ_R39_RESEARCH_HANDOFF "+json.dumps(record,ensure_ascii=False,separators=(",",":")),flush=True)

def generate_events(payload,is_cancelled=None):
    _v78_log(payload)
    for event in _V77_GENERATE(payload,is_cancelled):
        yield event

def inspect_engine():
    result=_V77_INSPECT()
    if isinstance(result,dict):
        result.update({
            "hotServerVersion":"2.1.90",
            "hotRevision":"2.1.90-hot-online-research-handoff-camera-v78",
            "v77Preserved":True,
            "onlineResearchHandoffCamera":True,
            "onlineResearchHandoffCameraContract":_V78_CONTRACT,
            "onlineResearchHandoffCameraChangesSemantics":False,
        })
    return result

HOT_SERVER_VERSION="2.1.90"
HOT_REVISION="2.1.90-hot-online-research-handoff-camera-v78"
_impl.HOT_SERVER_VERSION=HOT_SERVER_VERSION
_impl.HOT_REVISION=HOT_REVISION
