#!/usr/bin/env python3
"""Guarded §C Qwen3.5-9B latency-v3 publication and real ready/response test."""
from __future__ import annotations
import http.cookiejar
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from huggingface_hub import HfApi
from hf_chat_qwen35_latency_v3 import SPACE, MARKER, prepare, publish, rollback

BASE="https://kamiloki-swyrlz.hf.space"


def _json_get(path,timeout=15):
    request=urllib.request.Request(
        BASE+path,headers={"Cache-Control":"no-cache",
              "User-Agent":"Swrlz-Qwen35-Latency-V3-Verification"})
    with urllib.request.urlopen(request,timeout=timeout) as response:
        return json.load(response)


def verify_ready(api,commit,deadline_seconds=1250):
    end=time.monotonic()+deadline_seconds
    checks=0
    while time.monotonic()<end:
        checks+=1
        if api.repo_info(SPACE,repo_type="space").sha!=commit:
            raise RuntimeError("Concurrent Hugging Face release changed revision")
        try:
            result=_json_get("/api/hf/qwen35-ready")
            if result.get("ready") is True and result.get("profile")==MARKER:
                capacity=int(result.get("cpuCapacity") or 0)
                expected_batch=1024 if capacity>=8 else 512
                expected_ubatch=512 if capacity>=8 else 256
                if (result.get("model")!="qwen3.5-9b"
                    or result.get("batchSize")!=expected_batch
                    or result.get("microBatchSize")!=expected_ubatch
                    or result.get("decodeThreads")!=min(10,capacity)
                    or result.get("batchThreads")!=min(16,capacity)):
                    raise RuntimeError("New live CPU profile did not match declared configuration")
                print(json.dumps({"status":"LATENCY_V3_MODEL_READY",
                                  "revision":commit,"profile":result,"checks":checks}),flush=True)
                return
        except (urllib.error.URLError,TimeoutError,ValueError) as error:
            if checks%6==0:
                print(json.dumps({"status":"WARMUP_PENDING",
                    "attempts":checks,"errorType":type(error).__name__}),flush=True)
        time.sleep(12)
    raise RuntimeError("New 9B profile did not reach verified warm readiness")


def synthetic_test():
    """One new anonymous session; never touches a real user's account or conversation."""
    jar=http.cookiejar.CookieJar()
    opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    rid=str(uuid.uuid4())
    tid="perf-v3-"+str(uuid.uuid4())
    body={"modelId":"700m","prompt":"Hey how are you?","threadId":tid,
          "requestId":rid,"profileId":"LALM","profile":"",
          "userProfile":"","timeZone":"UTC"}
    started=time.monotonic()
    request=urllib.request.Request(BASE+"/api/lalm_station/send",
        method="POST",data=json.dumps(body).encode(),headers={
          "Content-Type":"application/json",
          "User-Agent":"Swrlz-Qwen35-Latency-V3-Synthetic"})
    with opener.open(request,timeout=30) as response:
        if response.status!=202:raise RuntimeError("Synthetic chat not accepted")
        response.read(512)
    url=BASE+"/api/lalm_station/stream?"+urllib.parse.urlencode({"requestId":rid})
    chars=0
    first=None
    terminal=None
    # The server should finish well below 120s; a long cloud prefill is visible
    # as a diagnostic, not permission to invent a successful latency result.
    with opener.open(urllib.request.Request(url,headers={
          "User-Agent":"Swrlz-Qwen35-Latency-V3-Synthetic"}),timeout=300) as response:
        for raw in response:
            now=time.monotonic()
            if now-started>270:
                raise RuntimeError("SYNTHETIC_LATENCY_EXCEEDED_SAFETY_WINDOW")
            try:
                event=json.loads(raw)
            except (ValueError,UnicodeError):
                continue
            if event.get("type")=="DELTA":
                text=str(event.get("text") or "")
                if text and first is None:
                    first=round(now-started,2)
                chars+=len(text)
                if chars>20000:
                    raise RuntimeError("SYNTHETIC_OUTPUT_UNBOUNDED")
            elif event.get("type") in ("COMPLETE","COMPLETED","FAILED","CANCELLED"):
                terminal=event.get("type")
                break
    duration=round(time.monotonic()-started,2)
    if terminal not in ("COMPLETE","COMPLETED") or chars<4 or first is None:
        raise RuntimeError("SYNTHETIC_9B_RESPONSE_FAILED")
    result={"status":"LATENCY_V3_SYNTHETIC_RESPONSE_COMPLETE","firstTextSeconds":first,
            "totalSeconds":duration,"outputCharacters":chars,
            "baselineFirstTextSeconds":74.44,"baselineTotalSeconds":76.41,
            "under50Seconds":duration<50}
    print(json.dumps(result),flush=True)
    return result


def run():
    if os.environ.get("SWRLZ_QWEN35_LATENCY_V3_APPROVED")!="1":
        raise RuntimeError("Missing owner-initiated guarded deploy approval")
    token=os.environ.get("HF_TOKEN") or ""
    if len(token)<12:
        raise RuntimeError("No existing HF release token")
    api=HfApi(token=token)
    _,before,_=prepare(api)
    release=publish(api)
    updated=release["revision"]
    try:
        verify_ready(api,updated)
        synthetic_test()
    except Exception:
        print(json.dumps({"status":"LATENCY_V3_ACCEPTANCE_FAILED",
                          "rollbackAttempt":"exact-prior-source"}),flush=True)
        rollback(api,updated,before)
        raise
    print("LATENCY_V3_DEPLOYMENT_ACCEPTED_AND_TESTED",flush=True)

if __name__=="__main__":
    run()
