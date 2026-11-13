#!/usr/bin/env python3
"""Guarded live §C 9B coding prefill benchmark with exact-source rollback."""
from __future__ import annotations
import http.cookiejar,json,os,re,time,urllib.parse,urllib.request,uuid
from huggingface_hub import HfApi
from hf_chat_qwen35_coder_prefill_v6 import SPACE,publish,rollback
BASE="https://kamiloki-swyrlz.hf.space"
AGENT="Swrlz-9B-Coder-v6-Release"
SIMPLE="Write a short Python function that returns the square of an integer, and show one example."
REPAIR=("Fix this Python function, preserving its name, parameter and return type; "
        "square(3) must return 9:\n"
        "def square(n):\n    return n + n")
PROFILE="swrlz-coder-prefill-v6-compact"

def model_ready():
    req=urllib.request.Request(BASE+"/api/hf/qwen35-ready",
        headers={"User-Agent":AGENT,"Cache-Control":"no-cache"})
    with urllib.request.urlopen(req,timeout=17) as res:data=json.load(res)
    if not(data.get("ready") is True and data.get("model")=="qwen3.5-9b"):
        raise RuntimeError("Resident 9B not ready")
    if (data.get("cpuCapacity"),data.get("decodeThreads"),data.get("batchThreads"))!=(16,16,16):
        raise RuntimeError("Shared 9B CPU plan changed")
    return data

def probe(label,prompt):
    opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    rid=str(uuid.uuid4());thread="swrlz-coder-v6-test-"+str(uuid.uuid4())
    started=time.monotonic()
    head={"User-Agent":AGENT}
    body={"modelId":"700m","prompt":prompt,"threadId":thread,"requestId":rid,
          "profileId":"LALM","profile":"","userProfile":"","timeZone":"UTC"}
    request=urllib.request.Request(BASE+"/api/lalm_station/send",
           data=json.dumps(body).encode("utf-8"),method="POST",
           headers={**head,"Content-Type":"application/json"})
    with opener.open(request,timeout=35) as res:
        if res.status!=202:raise RuntimeError("Synthetic send not accepted")
        res.read(400)
    query=BASE+"/api/lalm_station/stream?"+urllib.parse.urlencode({"requestId":rid})
    phases=[];flags=[];parts=[];terminal=None
    first=None
    with opener.open(urllib.request.Request(query,headers=head),timeout=220) as response:
        for raw in response:
            if time.monotonic()-started>210:raise RuntimeError("Synthetic request timeout")
            try:event=json.loads(raw)
            except (ValueError,UnicodeError):continue
            kind=event.get("type")
            if kind=="STATUS":
                phase=event.get("phase");phases.append(phase)
                if phase=="CODER_PREFILL_PROFILE":flags.append(event.get("reason"))
            elif kind=="DELTA":
                chunk=str(event.get("text") or "")
                if chunk and first is None:first=round(time.monotonic()-started,2)
                parts.append(chunk)
            elif kind in ("COMPLETE","COMPLETED","FAILED","CANCELLED"):
                terminal=kind
                break
    reply="".join(parts)
    # During HF rebuild, a request can be accepted by an old worker and then
    # terminate without a complete response. Report this transition state,
    # rather than failing the release before observing the new version marker.
    req=urllib.request.Request(BASE+"/api/lalm_station/sync",headers=head)
    with opener.open(req,timeout=18) as response:session=json.load(response)
    active=session.get("activeGeneration") or {}
    ctx=active.get("contextBudget") or {}
    telemetry=active.get("generationTelemetry") or {}
    attempts=active.get("candidateAttempts") or []
    validation=active.get("candidateValidation") or {}
    rec={
        "case":label,"totalSec":round(time.monotonic()-started,2),
        "firstVisibleSec":first,"outputChars":len(reply),"flags":flags,
        "terminal":terminal,"isCode":"def " in reply,
        "coderRouteSeen":"CODER_AUTO_ROUTE" in phases,
        "lastWorkflowStages":phases[-8:],
        "status":validation.get("status"),"attemptCount":len(attempts),
        "systemTokens":(ctx.get("tokenBreakdown") or {}).get("system"),
        "totalInputTokens":ctx.get("estimatedInputTokens"),
        "firstNativeTokenMs":attempts[-1].get("firstTokenLatencyMs") if attempts else None,
        "generationMs":telemetry.get("totalCandidateGenerationMs"),
        "maxOutputTokens":(active.get("resourcePlan") or {}).get("maxResponseTokens"),
    }
    print("CODER_V6_BENCHMARK",json.dumps(rec),flush=True)
    return rec,reply

def is_live_version_accepted(candidate):
    """A stale or transitioning HF worker is pending, not a tested regression."""
    if PROFILE not in candidate.get("flags",[]):
        return False
    if (candidate.get("terminal") not in ("COMPLETE","COMPLETED")
        or not candidate.get("isCode") or not candidate.get("coderRouteSeen")
        or candidate.get("status")!="PASS"):
        raise RuntimeError("Live new-version coding request failed acceptance")
    return True

def acceptance(api,revision):
    deadline=time.monotonic()+1050
    attempt=0
    result=None
    while time.monotonic()<deadline:
        attempt+=1
        if api.repo_info(SPACE,repo_type="space").sha!=revision:
            raise RuntimeError("Concurrent Hugging Face commit changed source")
        try:
            model_ready()
            candidate,_=probe("short-function",SIMPLE)
            if is_live_version_accepted(candidate):
                result=candidate
                print("CODER_V6_WARMUP_CONFIRMED",json.dumps({"attempts":attempt}),flush=True)
                break
            print("CODER_V6_OLD_OR_RESTART_WORKER",json.dumps({
                "attempt":attempt,"terminal":candidate["terminal"],
                "profileFlags":candidate["flags"],
                "stages":candidate["lastWorkflowStages"][-4:]}),flush=True)
        except (OSError,ValueError,TimeoutError) as err:
            if attempt%3==0:
                print("CODER_V6_WARMUP",json.dumps({"attempt":attempt,"error":type(err).__name__}),flush=True)
        time.sleep(12)
    if result is None:raise RuntimeError("New coder v6 source never reached live instance")
    if result["totalSec"]>=39.0:
        raise RuntimeError("Short-code speed not improved enough (baseline 48.45s)")
    if not isinstance(result["systemTokens"],int) or result["systemTokens"]>=2705:
        raise RuntimeError("Short coding system prompt was not actually reduced")
    if result["maxOutputTokens"]>1024:
        raise RuntimeError("Short coding output budget was not applied")
    if (isinstance(result["firstNativeTokenMs"],(int,float))
        and result["firstNativeTokenMs"]>=42544.505):
        raise RuntimeError("Measured first token latency did not improve")
    repaired,code=probe("existing-source-repair",REPAIR)
    if (repaired["terminal"] not in ("COMPLETE","COMPLETED")
        or not repaired["isCode"] or not repaired["coderRouteSeen"]
        or repaired["status"]!="PASS"):
        raise RuntimeError("Source-repair candidate validation regressed")
    if PROFILE in repaired["flags"] or "swrlz-coder-prefill-v6-standard" not in repaired["flags"]:
        raise RuntimeError("Complex repair incorrectly used compact prompt")
    if repaired["totalSec"]>125:raise RuntimeError("Repair coding latency regressed badly")
    if not re.search(r"n\s*\*\s*n|n\s*\*\*\s*2|pow\s*\(",code):
        raise RuntimeError("Repair failed square(3) acceptance")
    print("CODER_V6_ACCEPTED",json.dumps({
        "beforeShortCodeSeconds":48.45,"afterShortCodeSeconds":result["totalSec"],
        "speedup":round(48.45/result["totalSec"],2),
        "repairValidationPreserved":True,"model":"Qwen3.5-9B",
        "paidHardwareChange":False}),flush=True)

def main():
    if os.environ.get("SWRLZ_QWEN35_CODER_V6_APPROVED")!="1":
        raise RuntimeError("Owner-approved release permission missing")
    token=os.environ.get("HF_TOKEN") or ""
    if len(token)<12:raise RuntimeError("Existing Hugging Face credential missing")
    api=HfApi(token=token)
    published,before=publish(api)
    try:acceptance(api,published)
    except Exception:
        print("CODER_V6_ACCEPTANCE_FAILED_ROLLING_BACK",flush=True)
        rollback(api,published,before)
        raise
if __name__=="__main__":main()
