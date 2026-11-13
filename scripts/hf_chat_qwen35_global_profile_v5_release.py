#!/usr/bin/env python3
"""Guarded live benchmark for §C 9B authored-profile inference efficiency.

Operates only on existing Hugging Face §C Space with unchanged hardware.
Records only duration, counts, and model/context version; never logs user data.
Restores exact original engine bytes on readiness / acceptance failure.
"""
from __future__ import annotations
import http.cookiejar,json,os,time,urllib.parse,urllib.request,uuid
from huggingface_hub import HfApi
from hf_chat_qwen35_global_profile_v5 import SPACE,publish,rollback

BASE="https://kamiloki-swyrlz.hf.space"
VERSION="swrlz-qwen35-profile-v5"
HEADERS={"User-Agent":"Swrlz-Profile-v5-Guarded-Release"}
CASES=(
  ("conversation","Hey how are you?",25.0),
  ("factual","Explain the difference between CPU RAM and disk storage in three sentences.",70.0),
  ("coding","Write a short Python function that returns the square of an integer, and show one example.",70.0),
)

def check_ready():
    request=urllib.request.Request(BASE+"/api/hf/qwen35-ready",
         headers={**HEADERS,"Cache-Control":"no-cache"})
    with urllib.request.urlopen(request,timeout=16) as response:
        info=json.load(response)
    if not(info.get("ready") is True and info.get("model")=="qwen3.5-9b"):
        raise RuntimeError("QWEN35_NOT_WARM")
    if info.get("decodeThreads",0)<1 or info.get("batchThreads",0)<1:
        raise RuntimeError("QWEN35_THREADS_NOT_AVAILABLE")
    return {k:info.get(k) for k in ("model","profile","cpuCapacity","decodeThreads","batchThreads")}

def test_turn(label,prompt):
    opener=urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    rid=str(uuid.uuid4())
    tid="swrlz-anonymous-profile-v5-"+str(uuid.uuid4())
    started=time.monotonic()
    body={"modelId":"700m","prompt":prompt,"threadId":tid,
          "requestId":rid,"profileId":"LALM","profile":"",
          "userProfile":"","timeZone":"UTC"}
    req=urllib.request.Request(BASE+"/api/lalm_station/send",
        data=json.dumps(body).encode("utf-8"),method="POST",
        headers={**HEADERS,"Content-Type":"application/json"})
    with opener.open(req,timeout=35) as resp:
        if resp.status!=202:raise RuntimeError("SYNTHETIC_SEND_NOT_ACCEPTED")
        resp.read(1024)
    path="/api/lalm_station/stream?"+urllib.parse.urlencode({"requestId":rid})
    first=None;out=[];status=[];terminal=None
    with opener.open(urllib.request.Request(BASE+path,headers=HEADERS),
                     timeout=230) as response:
        for raw in response:
            if time.monotonic()-started>215:
                raise RuntimeError("LIVE_9B_PROFILE_PROBE_TIMEOUT")
            try:ev=json.loads(raw)
            except (ValueError,UnicodeError):continue
            kind=ev.get("type")
            if kind=="STATUS":
                status.append(ev.get("phase"))
            elif kind=="DELTA":
                text=str(ev.get("text") or "")
                if text and first is None:first=round(time.monotonic()-started,2)
                out.append(text)
            elif kind in ("COMPLETE","COMPLETED","FAILED","CANCELLED"):
                terminal=kind
                break
    value="".join(out)
    stats={"case":label,"firstTextSeconds":first,
           "totalSeconds":round(time.monotonic()-started,2),
           "characters":len(value),
           "composerReady": "PROFILE_CONTEXT_READY" in status,
           "terminal":terminal,"stages":status[-12:]}
    if terminal not in ("COMPLETE","COMPLETED") or len(value)<4:
        raise RuntimeError("PROFILE_V5_INFERENCE_DID_NOT_COMPLETE")
    # Coding trial must still deliver an actual function, not a generic answer.
    if label=="coding" and "def " not in value:
        raise RuntimeError("PROFILE_V5_CODING_CONTRACT_REGRESSION")
    print("PROFILE_V5_LIVE_TIMING",json.dumps(stats),flush=True)
    return stats

def verify(api,new_revision):
    deadline=time.monotonic()+1250
    cycles=0
    while time.monotonic()<deadline:
        cycles+=1
        if api.repo_info(SPACE,repo_type="space").sha!=new_revision:
            raise RuntimeError("Concurrent Hugging Face Space publication")
        try:
            observation=check_ready()
            trial=test_turn("conversation",CASES[0][1])
            if trial["composerReady"]:
                if trial["totalSeconds"]>CASES[0][2]:
                    raise RuntimeError("Conversation perf regression")
                print("PROFILE_V5_NEW_GENERATOR_CONFIRMED",json.dumps(observation),flush=True)
                break
        except (OSError,TimeoutError,ValueError) as exc:
            if cycles%4==0:
                print(json.dumps({"stage":"PROFILE_V5_RESTART_PENDING","round":cycles,
                                  "type":type(exc).__name__}),flush=True)
        time.sleep(12)
    else:
        raise RuntimeError("Updated §C profile composer never became live")
    for label,prompt,max_sec in CASES[1:]:
        result=test_turn(label,prompt)
        if not result["composerReady"]:
            raise RuntimeError("Profile composer reverted during live benchmark")
        if result["totalSeconds"]>max_sec:
            raise RuntimeError(f"{label} response exceeded guarded {max_sec}s threshold")
    print("PROFILE_V5_LIVE_BENCHMARK_ACCEPTED",json.dumps({
        "baseFactualSeconds":82.0,"baseCodingSeconds":35.24,
        "model":"Qwen3.5-9B","hardwareChanged":False
    }),flush=True)

def main():
    if os.environ.get("SWRLZ_QWEN35_PROFILE_V5_APPROVED")!="1":
        raise RuntimeError("Explicit release authorization not present")
    token=os.environ.get("HF_TOKEN") or ""
    if len(token)<12:raise RuntimeError("Missing existing owner HF_TOKEN")
    api=HfApi(token=token)
    newrev,originals=publish(api)
    try:
        verify(api,newrev)
    except Exception:
        print(json.dumps({"stage":"PROFILE_V5_VALIDATION_FAILED",
                          "action":"exact-source-rollback"}),flush=True)
        rollback(api,newrev,originals)
        raise

if __name__=="__main__":main()
