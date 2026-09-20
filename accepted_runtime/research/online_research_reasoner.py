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
VERSION="1.0.1"
CONTRACT_ID="swrlz_online_research_hot_v2"


def _now_ms()->int:return int(time.time()*1000)
def _elapsed(start:float)->int:return round((time.perf_counter()-start)*1000)
def _clean(v:Any,n:int=500)->str:return " ".join(str(v or "").split())[:n]

def _camera(request_id:str,research_id:str,event:str,start:float,**fields:Any)->None:
    record={"contract":"swrlz_research_camera_v1","event":event,"at":_now_ms(),"sinceRequestMs":_elapsed(start),"requestId":request_id,"researchId":research_id,**fields}
    print("SWRLZ_RESEARCH_CAMERA "+json.dumps(record,ensure_ascii=False,separators=(",",":")),flush=True)

def inspect_research()->dict[str,Any]:
    return {"moduleId":MODULE_ID,"version":VERSION,"contractId":CONTRACT_ID,"hotUpdatable":True,"networkAuthority":"stable-server-capabilities","cameraContract":"swrlz_research_camera_v1"}


_STOP={"the","a","an","and","or","to","of","in","on","for","with","is","are","was","were","be","been","being","what","tell","me","look","up","find","current"}
def _terms(plan:dict[str,Any])->list[str]:
    import re
    text=" ".join([str(plan.get("target") or ""),str(plan.get("requestedInformation") or "")," ".join(plan.get("queries") or [])]).lower()
    out=[]
    for token in re.findall(r"[a-z0-9][a-z0-9_-]{2,}",text):
        if token not in _STOP and token not in out:out.append(token)
    return out[:24]

def _passage(text:Any,terms:list[str],limit:int=1400)->str:
    value=" ".join(str(text or "").split())
    if not value:return ""
    low=value.lower(); hits=[low.find(t) for t in terms if low.find(t)>=0]
    center=min(hits) if hits else 0
    start=max(0,center-limit//3); end=min(len(value),start+limit)
    if end-start<limit:start=max(0,end-limit)
    return value[start:end].strip()

def _score(item:dict[str,Any],terms:list[str])->int:
    title=str(item.get("title") or "").lower()
    hay=(title+" "+str(item.get("snippet") or "")).lower()
    return sum(4 if t in title else 1 for t in terms if t in hay)-max(0,int(item.get("rank") or 1)-1)

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
            q=_clean(candidate.get("query") or candidate.get("queryText") or candidate.get("q") or candidate.get("text"),500)
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
    plan=normalize_plan(payload); terms=_terms(plan)
    _camera(request_id,research_id,"RESEARCH_TARGET_RESOLVED",start,intent=plan["intent"],target=plan["target"],requestedInformation=plan["requestedInformation"],targetConfidence=plan["targetConfidence"],fallbackExactPrompt=plan["fallbackExactPrompt"])
    _camera(request_id,research_id,"QUERY_PLAN_READY",start,queries=plan["queries"],constraints=plan["constraints"],termCount=len(terms))
    search=capabilities["search"]; fetch=capabilities.get("fetch")
    candidates=[]; errors=[]; seen=set(); inspected=0; fetched=0; inspected_chars=0
    for qi,query in enumerate(plan["queries"][:4]):
        qstart=time.perf_counter(); _camera(request_id,research_id,"SEARCH_STARTED",start,query=query,queryIndex=qi,provider=capabilities.get("provider","unknown"))
        try: found=search(query)
        except Exception as exc:
            errors.append({"query":query,"error":f"{type(exc).__name__}:{str(exc)[:160]}"}); _camera(request_id,research_id,"SEARCH_FAILED",start,query=query,durationMs=_elapsed(qstart),errorType=type(exc).__name__); continue
        inspected+=len(found); inspected_chars+=sum(len(str(x.get("title") or ""))+len(str(x.get("snippet") or "")) for x in found if isinstance(x,dict))
        _camera(request_id,research_id,"SEARCH_COMPLETE",start,query=query,durationMs=_elapsed(qstart),resultCount=len(found))
        for item in found:
            if not isinstance(item,dict):continue
            url=_clean(item.get("url"),2000)
            if not url or url in seen:continue
            seen.add(url); rec={**item,"query":query,"relevanceScore":_score(item,terms)}
            rec["snippet"]=_passage(rec.get("snippet"),terms,700); candidates.append(rec)
    candidates.sort(key=lambda x:(-int(x.get("relevanceScore") or 0),int(x.get("rank") or 999)))
    evidence=[]
    for rec in candidates[:8]:
        eid=f"e{len(evidence)+1}"; rec={**rec,"evidenceId":eid,"disposition":"selected","retrievedAt":_now_ms()}; url=_clean(rec.get("url"),2000)
        _camera(request_id,research_id,"URL_SELECTED",start,evidenceId=eid,url=url,title=_clean(rec.get("title"),300),query=rec.get("query"),rank=rec.get("rank"),relevanceScore=rec.get("relevanceScore"))
        if fetch and len(evidence)<3:
            fstart=time.perf_counter(); _camera(request_id,research_id,"PAGE_FETCH_STARTED",start,evidenceId=eid,url=url)
            try:
                page=fetch(url); raw_extract=str(page.get("extract") or ""); inspected_chars+=len(raw_extract); fetched+=1
                rec.update({"pageTitle":page.get("title",""),"extract":_passage(raw_extract,terms,1400),"finalUrl":page.get("finalUrl",url),"httpStatus":page.get("status"),"fetchedAt":page.get("fetchedAt",_now_ms())})
                _camera(request_id,research_id,"PAGE_FETCH_COMPLETE",start,evidenceId=eid,url=url,finalUrl=rec.get("finalUrl"),httpStatus=rec.get("httpStatus"),durationMs=_elapsed(fstart),inspectedChars=len(raw_extract),admittedChars=len(rec.get("extract","")))
            except Exception as exc:
                rec["fetchError"]=f"{type(exc).__name__}:{str(exc)[:160]}"; _camera(request_id,research_id,"PAGE_FETCH_FAILED",start,evidenceId=eid,url=url,durationMs=_elapsed(fstart),errorType=type(exc).__name__)
        evidence.append(rec)
    admitted_chars=sum(len(str(x.get("title") or ""))+len(str(x.get("snippet") or ""))+len(str(x.get("extract") or "")) for x in evidence)
    budget={"queriesExecuted":min(4,len(plan["queries"])),"searchResultsInspected":inspected,"pagesFetched":fetched,"externalCharsInspected":inspected_chars,"evidenceItemsAdmitted":len(evidence),"evidenceCharsAdmitted":admitted_chars,"maxEvidenceItems":8,"maxPagePassageChars":1400,"maxSnippetChars":700}
    bundle={"contractId":"swrlz_online_evidence_v3","researchContract":CONTRACT_ID,"researchId":research_id,"requested":True,"provider":capabilities.get("provider","unknown"),"plan":plan,"queries":plan["queries"][:4],"resultCount":len(evidence),"evidence":evidence,"errors":errors,"elapsedMs":_elapsed(start),"budget":budget,"epistemicPolicy":"retrieval-is-evidence-not-truth","cameraContract":"swrlz_research_camera_v1"}
    _camera(request_id,research_id,"EVIDENCE_BUDGET",start,**budget)
    _camera(request_id,research_id,"RESEARCH_BUNDLE_READY",start,resultCount=len(evidence),errorCount=len(errors),elapsedMs=bundle["elapsedMs"])
    return bundle
