"""R39 v50: semantic online research planner + provenance-aware synthesis.

Adds a bounded Brain-owned pre-retrieval planner. Quotation marks are evidence for
target resolution, never a requirement. The planner resolves natural requests such
as 'look up hey', 'what does hey mean', and 'hey, look up hay' by meaning/context.
"""
from __future__ import annotations
import json
import re
import urllib.request

_V49_COMMIT="930f6305cb65e55070214a046c400da6234fc387"
_V49_URL=f"https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/{_V49_COMMIT}/runtime_hot/r39_engine_v49.py"
_req=urllib.request.Request(_V49_URL,headers={"User-Agent":"swrlz-r39-v50"})
with urllib.request.urlopen(_req,timeout=20) as _response:_source=_response.read(4_000_001)
if len(_source)>4_000_000:raise RuntimeError("R39_V49_SOURCE_TOO_LARGE")
exec(compile(_source.decode("utf-8"),_V49_URL+"#v50","exec"),globals(),globals())

_V49_INSPECT=inspect_engine
_V49_GENERATE=generate_events
HOT_SERVER_VERSION="2.1.61"
HOT_REVISION="2.1.61-hot-semantic-online-reasoner-v50"
_impl.HOT_SERVER_VERSION=HOT_SERVER_VERSION
_impl.HOT_REVISION=HOT_REVISION

_PLANNER_POLICY=(
 "You are the pre-retrieval research planner inside the §wyrlz Brain. Return one compact JSON object only. "
 "Resolve the user's actual research intent and target from semantics and active context before making queries. "
 "Quotation marks are useful evidence that can increase target confidence but are NEVER required. Do not implement a quoted-token lookup rule. "
 "Distinguish greetings/discourse from the lookup target: for example, in 'Hey, can you look up hay and its definition?' the target is hay, not Hey. "
 "Preserve requested information, hard constraints, referents, architecture/version/runtime qualifiers, exclusions, and freshness needs. "
 "Use the minimum sufficient search specificity. Search the exact architecture/artifact/domain when context supplies it; do not broaden to a parent category without reason. "
 "Output keys: intent, target, requestedInformation, targetConfidence (0..1), constraints (array), queries (array, max 6). "
 "Queries should be externally useful search strings, not conversational filler. Do not answer the user's question in this planning step."
)

def _json_object(text):
    text=str(text or "").strip()
    try:
        obj=json.loads(text)
        return obj if isinstance(obj,dict) else None
    except Exception:pass
    m=re.search(r"\{[\s\S]*\}",text)
    if not m:return None
    try:
        obj=json.loads(m.group(0));return obj if isinstance(obj,dict) else None
    except Exception:return None

def plan_research(payload):
    """Run a bounded semantic planning pass before the server performs retrieval."""
    if not isinstance(payload,dict):return {}
    original=str(payload.get("prompt") or "").strip()
    if not original:return {}
    planning=dict(payload)
    planning["profileId"]="LALM"
    planning.pop("onlineEvidence",None); planning.pop("researchPlan",None); planning.pop("researchQueries",None)
    planning["generation"]={"temperature":0.1,"topP":0.9,"maxTokens":160}
    history=list(planning.get("history") or [])
    planning["history"]=[{"role":"system","text":_PLANNER_POLICY}]+history
    chunks=[]
    try:
        for event in _V49_GENERATE(planning,None):
            if isinstance(event,dict) and event.get("type")=="DELTA":
                chunks.append(str(event.get("text") or ""))
                if sum(map(len,chunks))>6000:break
    except Exception as exc:
        _camera(_request_id(payload),"research-plan-fallback",reason=type(exc).__name__)
        return {"intent":"","target":"","requestedInformation":"","targetConfidence":0.0,"constraints":[],"queries":[original],"plannerFallback":True}
    plan=_json_object("".join(chunks))
    if not isinstance(plan,dict):
        _camera(_request_id(payload),"research-plan-fallback",reason="invalid-json")
        return {"intent":"","target":"","requestedInformation":"","targetConfidence":0.0,"constraints":[],"queries":[original],"plannerFallback":True}
    queries=[]
    for q in plan.get("queries",[]) if isinstance(plan.get("queries"),list) else []:
        q=" ".join(str(q).split())[:500]
        if q and q not in queries:queries.append(q)
        if len(queries)>=6:break
    if not queries:queries=[original]
    out={"intent":str(plan.get("intent") or "")[:200],"target":str(plan.get("target") or "")[:500],"requestedInformation":str(plan.get("requestedInformation") or "")[:500],"targetConfidence":plan.get("targetConfidence",0),"constraints":plan.get("constraints",[])[:16] if isinstance(plan.get("constraints"),list) else [],"queries":queries,"plannerFallback":False}
    _camera(_request_id(payload),"research-target",intent=out["intent"],target=out["target"],requestedInformation=out["requestedInformation"],targetConfidence=out["targetConfidence"],queryCount=len(queries),quotationRequired=False)
    return out

def inspect_engine():
    result=_V49_INSPECT()
    if isinstance(result,dict):result.update({"hotServerVersion":HOT_SERVER_VERSION,"hotRevision":HOT_REVISION,"semanticResearchPlanner":True,"researchTargetResolution":"semantic-contextual-v1","quotationMarks":"evidence-not-requirement","preRetrievalPlanContract":"swrlz_research_plan_v1","v49SourceCommit":_V49_COMMIT})
    return result

def generate_events(payload,is_cancelled=None):
    request_id=_request_id(payload)
    bundle=payload.get("onlineEvidence") if isinstance(payload,dict) else None
    if isinstance(bundle,dict) and bundle.get("researchId"):
        _camera(request_id,"research-provenance",researchId=bundle.get("researchId"),resultCount=bundle.get("resultCount",0),queries=bundle.get("queries",[])[:6],cameraContract=bundle.get("cameraContract"))
        yield {"type":"STATUS","phase":"EVIDENCE_EVALUATION_STARTED","reason":"Brain is evaluating retrieved evidence against the resolved target, constraints, source quality, freshness, corroboration and conflicts."}
    for event in _V49_GENERATE(payload,is_cancelled):yield event
