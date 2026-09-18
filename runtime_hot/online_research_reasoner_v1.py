"""§wyrlz runtime-hot online research reasoner v1.

Owns evolvable research strategy and structured research-camera telemetry.
Network authority remains in the stable server capabilities passed to research().
"""
from __future__ import annotations
import json
import time
import uuid
from typing import Any, Callable

MODULE_ID="online-research"
VERSION="1.0.0"
CONTRACT_ID="swrlz_online_research_hot_v1"


def _now_ms()->int:return int(time.time()*1000)
def _elapsed(start:float)->int:return round((time.perf_counter()-start)*1000)
def _clean(v:Any,n:int=500)->str:return " ".join(str(v or "").split())[:n]

def _camera(request_id:str,research_id:str,event:str,start:float,**fields:Any)->None:
    record={"contract":"swrlz_research_camera_v1","event":event,"at":_now_ms(),"sinceRequestMs":_elapsed(start),"requestId":request_id,"researchId":research_id,**fields}
    print("SWRLZ_RESEARCH_CAMERA "+json.dumps(record,ensure_ascii=False,separators=(",",":")),flush=True)

def inspect_research()->dict[str,Any]:
    return {"moduleId":MODULE_ID,"version":VERSION,"contractId":CONTRACT_ID,"hotUpdatable":True,"networkAuthority":"stable-server-capabilities","cameraContract":"swrlz_research_camera_v1"}

def normalize_plan(payload:dict[str,Any])->dict[str,Any]:
    """Normalize a Brain-authored plan; never infer semantics from punctuation alone."""
    raw=payload.get("researchPlan") if isinstance(payload,dict) else None
    raw=raw if isinstance(raw,dict) else {}
    prompt=_clean(payload.get("prompt"),2000)
    target=_clean(raw.get("target"),500)
    intent=_clean(raw.get("intent"),200)
    requested=_clean(raw.get("requestedInformation"),500)
    confidence=raw.get("targetConfidence")
    try: confidence=max(0.0,min(1.0,float(confidence)))
    except (TypeError,ValueError): confidence=0.0
    queries=[]
    for candidate in raw.get("queries",[]) if isinstance(raw.get("queries"),list) else []:
        # Planner output is untrusted structured data. Accept strings directly and
        # only explicit query-bearing fields from objects; never stringify dicts.
        if isinstance(candidate,str):
            q=_clean(candidate,500)
        elif isinstance(candidate,dict):
            q=_clean(candidate.get("query") or candidate.get("q") or candidate.get("text"),500)
        else:
            q=""
        if q and q not in queries:queries.append(q)
        if len(queries)>=6:break
    if not queries:
        # Conservative fallback preserves the exact request. This is transport
        # fallback, not a claim that the whole utterance is the semantic target.
        queries=[prompt] if prompt else []
    return {"intent":intent,"target":target,"requestedInformation":requested,"targetConfidence":confidence,"queries":queries,"constraints":raw.get("constraints",[])[:16] if isinstance(raw.get("constraints"),list) else [],"fallbackExactPrompt":not bool(raw.get("queries"))}

def research(payload:dict[str,Any],capabilities:dict[str,Callable[...,Any]])->dict[str,Any]:
    start=time.perf_counter(); request_id=_clean(payload.get("requestId"),200) or "unknown"; research_id="research:"+uuid.uuid4().hex[:20]
    plan=normalize_plan(payload)
    _camera(request_id,research_id,"RESEARCH_TARGET_RESOLVED",start,intent=plan["intent"],target=plan["target"],requestedInformation=plan["requestedInformation"],targetConfidence=plan["targetConfidence"],fallbackExactPrompt=plan["fallbackExactPrompt"])
    _camera(request_id,research_id,"QUERY_PLAN_READY",start,queries=plan["queries"],constraints=plan["constraints"])
    search=capabilities["search"]; fetch=capabilities.get("fetch")
    evidence=[]; errors=[]; seen=set()
    for qi,query in enumerate(plan["queries"]):
        qstart=time.perf_counter(); _camera(request_id,research_id,"SEARCH_STARTED",start,query=query,queryIndex=qi,provider=capabilities.get("provider","unknown"))
        try: found=search(query)
        except Exception as exc:
            errors.append({"query":query,"error":f"{type(exc).__name__}:{str(exc)[:160]}"}); _camera(request_id,research_id,"SEARCH_FAILED",start,query=query,durationMs=_elapsed(qstart),errorType=type(exc).__name__); continue
        _camera(request_id,research_id,"SEARCH_COMPLETE",start,query=query,durationMs=_elapsed(qstart),resultCount=len(found))
        for item in found:
            url=_clean(item.get("url"),2000)
            if not url or url in seen:continue
            seen.add(url); eid=f"e{len(evidence)+1}"; rec={**item,"evidenceId":eid,"disposition":"candidate","retrievedAt":_now_ms()}
            _camera(request_id,research_id,"URL_DISCOVERED",start,evidenceId=eid,url=url,title=_clean(item.get("title"),300),query=query,rank=item.get("rank"))
            # Fetch only a small high-ranked frontier. The stable capability owns SSRF,
            # redirect, byte, timeout, and protocol enforcement.
            if fetch and len(evidence)<6:
                fstart=time.perf_counter(); _camera(request_id,research_id,"PAGE_FETCH_STARTED",start,evidenceId=eid,url=url)
                try:
                    page=fetch(url); rec.update({"pageTitle":page.get("title",""),"extract":page.get("extract",""),"finalUrl":page.get("finalUrl",url),"httpStatus":page.get("status"),"fetchedAt":page.get("fetchedAt",_now_ms())})
                    _camera(request_id,research_id,"PAGE_FETCH_COMPLETE",start,evidenceId=eid,url=url,finalUrl=rec.get("finalUrl"),httpStatus=rec.get("httpStatus"),durationMs=_elapsed(fstart),extractChars=len(rec.get("extract", "")))
                except Exception as exc:
                    rec["fetchError"]=f"{type(exc).__name__}:{str(exc)[:160]}"; _camera(request_id,research_id,"PAGE_FETCH_FAILED",start,evidenceId=eid,url=url,durationMs=_elapsed(fstart),errorType=type(exc).__name__)
            evidence.append(rec)
            if len(evidence)>=24:break
        if len(evidence)>=24:break
    bundle={"contractId":"swrlz_online_evidence_v2","researchContract":CONTRACT_ID,"researchId":research_id,"requested":True,"provider":capabilities.get("provider","unknown"),"plan":plan,"queries":plan["queries"],"resultCount":len(evidence),"evidence":evidence,"errors":errors,"elapsedMs":_elapsed(start),"epistemicPolicy":"retrieval-is-evidence-not-truth","cameraContract":"swrlz_research_camera_v1"}
    _camera(request_id,research_id,"RESEARCH_BUNDLE_READY",start,resultCount=len(evidence),errorCount=len(errors),elapsedMs=bundle["elapsedMs"])
    return bundle
