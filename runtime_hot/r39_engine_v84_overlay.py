"""R39 v84 research planner scope repair."""
from __future__ import annotations
import json

_V83_INSPECT_V84=inspect_engine
_V49_PLANNER_GENERATE_V84=_V49_GENERATE
_V84_CONTRACT="r39-v84-research-planner-scope-v1"

def _v84_query(candidate):
    if isinstance(candidate,str): return " ".join(candidate.split())[:500]
    if isinstance(candidate,dict):
        for key in ("query","queryText","q","text"):
            value=candidate.get(key)
            if isinstance(value,str) and value.strip(): return " ".join(value.split())[:500]
    return ""

def plan_research(payload):
    if not isinstance(payload,dict): return {}
    original=str(payload.get("prompt") or "").strip()
    if not original:return {}
    outer_id=_request_id(payload)
    planning=dict(payload)
    planning["requestId"]=str(outer_id)[:180]+":planner"
    planning["profileId"]="LALM"
    planning.pop("onlineEvidence",None);planning.pop("researchPlan",None);planning.pop("researchQueries",None)
    planning["generation"]={"temperature":0.1,"topP":0.9,"maxTokens":160}
    planning["history"]=[{"role":"system","text":_PLANNER_POLICY}]+list(planning.get("history") or [])
    chunks=[]
    try:
        for event in _V49_PLANNER_GENERATE_V84(planning,None):
            if isinstance(event,dict) and event.get("type")=="DELTA":
                chunks.append(str(event.get("text") or ""))
                if sum(map(len,chunks))>6000:break
    except Exception as exc:
        _camera(outer_id,"research-plan-fallback",reason=type(exc).__name__)
        return {"intent":"","target":"","requestedInformation":"","targetConfidence":0.0,"constraints":[],"queries":[original],"plannerFallback":True}
    plan=_json_object("".join(chunks))
    if not isinstance(plan,dict):
        _camera(outer_id,"research-plan-fallback",reason="invalid-json")
        return {"intent":"","target":"","requestedInformation":"","targetConfidence":0.0,"constraints":[],"queries":[original],"plannerFallback":True}
    queries=[]
    for candidate in plan.get("queries",[]) if isinstance(plan.get("queries"),list) else []:
        q=_v84_query(candidate)
        if q and q not in queries:queries.append(q)
        if len(queries)>=6:break
    fallback=not bool(queries)
    if not queries:queries=[original]
    out={"intent":str(plan.get("intent") or "")[:200],"target":str(plan.get("target") or "")[:500],"requestedInformation":str(plan.get("requestedInformation") or "")[:500],"targetConfidence":plan.get("targetConfidence",0),"constraints":plan.get("constraints",[])[:16] if isinstance(plan.get("constraints"),list) else [],"queries":queries,"plannerFallback":fallback}
    _camera(outer_id,"research-target",intent=out["intent"],target=out["target"],requestedInformation=out["requestedInformation"],targetConfidence=out["targetConfidence"],queryCount=len(queries),quotationRequired=False)
    print("SWRLZ_R39_RESEARCH_PLANNER_SCOPE "+json.dumps({"contract":_V84_CONTRACT,"requestId":str(outer_id)[:180],"queryCount":len(queries),"fallbackExactPrompt":fallback},separators=(",",":")),flush=True)
    return out

def inspect_engine():
    result=_V83_INSPECT_V84()
    if isinstance(result,dict):result.update({"hotServerVersion":"2.1.96","hotRevision":"2.1.96-hot-research-planner-scope-v84","researchPlannerScoped":True,"researchPlannerQueryNormalization":"explicit-fields-or-exact-prompt","researchPlannerScopeContract":_V84_CONTRACT})
    return result

HOT_SERVER_VERSION="2.1.96"
HOT_REVISION="2.1.96-hot-research-planner-scope-v84"
_impl.HOT_SERVER_VERSION=HOT_SERVER_VERSION
_impl.HOT_REVISION=HOT_REVISION
