#!/usr/bin/env python3
"""One unauthenticated synthetic coding baseline with stage timings and tokens.

No personal data, no response text persisted/logged, no server mutation.
"""
from __future__ import annotations
import http.cookiejar,json,time,urllib.parse,urllib.request,uuid
BASE="https://kamiloki-swyrlz.hf.space"
prompt="Write a short Python function that returns the square of an integer, and show one example."
opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
HEAD={"User-Agent":"Swrlz-Synthetic-Coder-Prefill-Test"}
request_id=str(uuid.uuid4())
thread_id="synthetic-coder-prefill-"+str(uuid.uuid4())
start=time.monotonic()
def now():return round(time.monotonic()-start,2)
payload={"modelId":"700m","prompt":prompt,"threadId":thread_id,"requestId":request_id,
         "profileId":"LALM","profile":"","userProfile":"","timeZone":"UTC"}
req=urllib.request.Request(BASE+"/api/lalm_station/send",method="POST",
      data=json.dumps(payload).encode(),headers={**HEAD,"Content-Type":"application/json"})
with opener.open(req,timeout=35) as resp:
    if resp.status!=202:raise RuntimeError("No send acceptance")
    resp.read(512)
print("CODER_BASELINE_ACCEPTED_SEC",now(),flush=True)
url=BASE+"/api/lalm_station/stream?"+urllib.parse.urlencode({"requestId":request_id})
status=[]
first=None
chars=0
has_def=False
terminal=None
with opener.open(urllib.request.Request(url,headers=HEAD),timeout=270) as resp:
    for line in resp:
        if now()>260:raise RuntimeError("Coding baseline safety timeout")
        try:event=json.loads(line)
        except ValueError:continue
        kind=event.get("type")
        if kind=="STATUS":
            status.append({"step":event.get("phase"),"sec":now()})
        elif kind=="DELTA":
            chunk=str(event.get("text") or "")
            chars+=len(chunk)
            has_def|="def " in chunk
            if chunk and first is None:first=now()
        elif kind in ("COMPLETE","COMPLETED","FAILED","CANCELLED"):
            terminal=kind
            break
print("CODER_BASELINE_STREAM",json.dumps({"totalSec":now(),"firstTextSec":first,
      "outputChars":chars,"containsDef":has_def,"terminal":terminal,
      "statuses":status},ensure_ascii=False),flush=True)
# Inspect metadata associated only with this synthetic cookie/session, not
# the user's authenticated chat or files.
try:
    req=urllib.request.Request(BASE+"/api/lalm_station/sync",headers=HEAD)
    with opener.open(req,timeout=20) as resp:
        snapshot=json.load(resp)
    gen=snapshot.get("activeGeneration") or {}
    context=gen.get("contextBudget") or {}
    attempt=gen.get("candidateAttempts") or []
    telemetry=gen.get("generationTelemetry") or {}
    resource=gen.get("resourcePlan") or {}
    job=gen.get("stationTiming") or {}
    summary={
      "profile":(gen.get("profileId") or ""),
      "context":{"estimatedInputTokens":context.get("estimatedInputTokens"),
          "reservedOutputTokens":context.get("reservedOutputTokens"),
          "breakdown":context.get("tokenBreakdown"),
          "historyMessagesKept":context.get("historyMessagesKept")},
      "attempts":[{"attempt":i.get("attempt"),"status":i.get("status"),
          "durationMs":i.get("durationMs"),"firstTokenLatencyMs":i.get("firstTokenLatencyMs"),
          "tokenCount":i.get("tokenCount"),"finishReason":i.get("finishReason")}
          for i in attempt[-3:]],
      "generation":{k:v for k,v in telemetry.items() if
          any(z in k.lower() for z in ("latency","ms","duration","attempt","token","reason"))},
      "serverTiming":{k:v for k,v in job.items() if any(z in k.lower() for z in ("ms","latency","duration","wait"))},
      "resources":resource,
    }
    print("CODER_BASELINE_DIAGNOSTICS",json.dumps(summary,ensure_ascii=False),flush=True)
except Exception as error:
    print("CODER_BASELINE_DIAGNOSTICS_UNAVAILABLE",type(error).__name__,flush=True)
if terminal not in ("COMPLETE","COMPLETED") or chars<10:raise RuntimeError("Synthetic coding response invalid")
