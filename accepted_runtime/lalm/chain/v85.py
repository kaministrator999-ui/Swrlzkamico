"""R39 v85: stream real internal research-planner status telemetry to the server."""
from __future__ import annotations
import json

_V84_INSPECT_V85=inspect_engine
_V49_PLANNER_GENERATE_V85=_V49_GENERATE
_V85_CONTRACT="r39-v85-live-planner-status-v1"

def _v85_prepare(payload):
    outer_id=_request_id(payload)
    planning=dict(payload)
    planning["requestId"]=str(outer_id)[:180]+":planner"
    planning["profileId"]="LALM"
    planning.pop("onlineEvidence",None);planning.pop("researchPlan",None);planning.pop("researchQueries",None)
    planning["generation"]={"temperature":0.1,"topP":0.9,"maxTokens":160}
    planning["history"]=[{"role":"system","text":_PLANNER_POLICY}]+list(planning.get("history") or [])
    return outer_id,planning

def _v85_finish(original,outer_id,chunks):
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
    return out

def plan_research_stream(payload):
    if not isinstance(payload,dict):yield {"type":"PLAN","plan":{}};return
    original=str(payload.get("prompt") or "").strip()
    if not original:yield {"type":"PLAN","plan":{}};return
    outer_id,planning=_v85_prepare(payload);chunks=[]
    try:
        for event in _V49_PLANNER_GENERATE_V85(planning,None):
            if not isinstance(event,dict):continue
            if event.get("type")=="DELTA":
                chunks.append(str(event.get("text") or ""))
                if sum(map(len,chunks))>6000:break
            elif event.get("type")=="STATUS":
                yield {"type":"STATUS","phase":str(event.get("phase") or "STATE_VALIDATION"),"reason":str(event.get("reason") or "")[:1000],"categories":["ONLINE_RESEARCH","INTERNAL_PLANNER"]}
    except Exception as exc:
        _camera(outer_id,"research-plan-fallback",reason=type(exc).__name__)
        yield {"type":"PLAN","plan":{"intent":"","target":"","requestedInformation":"","targetConfidence":0.0,"constraints":[],"queries":[original],"plannerFallback":True,"plannerError":type(exc).__name__}}
        return
    out=_v85_finish(original,outer_id,chunks)
    print("SWRLZ_R39_LIVE_PLANNER_STATUS "+json.dumps({"contract":_V85_CONTRACT,"requestId":str(outer_id)[:180],"queryCount":len(out.get("queries",[]))},separators=(",",":")),flush=True)
    yield {"type":"PLAN","plan":out}

def plan_research(payload):
    plan={}
    for item in plan_research_stream(payload):
        if isinstance(item,dict) and item.get("type")=="PLAN":plan=item.get("plan") or {}
    return plan

def inspect_engine():
    result=_V84_INSPECT_V85()
    if isinstance(result,dict):result.update({"hotServerVersion":"2.1.97","hotRevision":"2.1.97-hot-live-planner-status-v85","liveResearchPlannerStatus":True,"liveResearchPlannerStatusContract":_V85_CONTRACT})
    return result

HOT_SERVER_VERSION="2.1.97"
HOT_REVISION="2.1.97-hot-live-planner-status-v85"
_impl.HOT_SERVER_VERSION=HOT_SERVER_VERSION
_impl.HOT_REVISION=HOT_REVISION
