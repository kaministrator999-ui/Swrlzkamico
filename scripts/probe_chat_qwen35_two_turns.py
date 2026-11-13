#!/usr/bin/env python3
"""Probe two anonymous §C turns in one session; print timings only, no texts."""
import http.cookiejar
import json
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid

BASE="https://kamiloki-swyrlz.hf.space"
SESS=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
THREAD="swrlz-conversation-latency-"+str(uuid.uuid4())
HEADERS={"User-Agent":"Swrlz-TwoTurn-Synthetic-Profiler"}
PROMPTS=("Hey how are you?", "Doing well, just checking in on you")

def turn(prompt):
    rid=str(uuid.uuid4())
    start=time.monotonic()
    payload={"modelId":"700m","prompt":prompt,"threadId":THREAD,"requestId":rid,
             "profileId":"LALM","profile":"","userProfile":"","timeZone":"UTC"}
    request=urllib.request.Request(BASE+"/api/lalm_station/send",
              data=json.dumps(payload).encode("utf-8"),method="POST",
              headers={**HEADERS,"Content-Type":"application/json"})
    with SESS.open(request,timeout=35) as resp:
        if resp.status!=202: raise RuntimeError("CHAT_NOT_ACCEPTED")
        resp.read(1024)
    accepted=time.monotonic()-start
    q=urllib.parse.urlencode({"requestId":rid})
    statuses=[]
    first=None
    chars=0
    terminal=""
    with SESS.open(urllib.request.Request(BASE+"/api/lalm_station/stream?"+q,
                     headers=HEADERS),timeout=240) as response:
        for raw in response:
            event=json.loads(raw)
            kind=event.get("type")
            if kind=="STATUS":
                statuses.append(str(event.get("phase") or ""))
            elif kind=="DELTA":
                delta=str(event.get("text") or "")
                if delta and first is None:first=time.monotonic()-start
                chars+=len(delta)
            elif kind in ("COMPLETE","COMPLETED","FAILED","CANCELLED"):
                terminal=kind
                break
            if time.monotonic()-start>220:
                raise RuntimeError("EXCEEDED_TWO_TURN_PROBE_SAFETY_WINDOW")
    stats={"acceptedSeconds":round(accepted,2),
           "firstTextSeconds":round(first,2) if first is not None else None,
           "totalSeconds":round(time.monotonic()-start,2),
           "outputLength":chars,"status":terminal,
           "recordedWorkflowStages":statuses[-12:]}
    if terminal not in ("COMPLETE","COMPLETED") or chars<4:
        raise RuntimeError("TWO_TURN_PROBE_FAILED")
    return stats

if __name__=="__main__":
    results=[]
    for index,prompt in enumerate(PROMPTS):
        result=turn(prompt)
        print("TWO_TURN_TIMING",json.dumps({"turn":index+1,**result}),flush=True)
        results.append(result)
    print("TWO_TURN_SYNTHETIC_COMPLETE",json.dumps({
        "firstTurn":results[0]["totalSeconds"],
        "followup":results[1]["totalSeconds"]}),flush=True)
