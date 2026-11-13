#!/usr/bin/env python3
"""Anonymous baseline for non-social §C 9B routes. No personal data or writes."""
import http.cookiejar,json,time,urllib.parse,urllib.request,uuid,sys
BASE="https://kamiloki-swyrlz.hf.space"
HEAD={"User-Agent":"Swrlz-9B-Global-Profile-Probe"}
tests=[
 ("factual","Explain the difference between CPU RAM and disk storage in three sentences."),
 ("coding","Write a short Python function that returns the square of an integer, and show one example."),
]
for label,prompt in tests:
    thread="global-profile-perf-"+str(uuid.uuid4())
    rid=str(uuid.uuid4())
    opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    started=time.monotonic()
    payload={"modelId":"700m","prompt":prompt,"threadId":thread,
             "requestId":rid,"profileId":"LALM","profile":"","userProfile":"","timeZone":"UTC"}
    req=urllib.request.Request(BASE+"/api/lalm_station/send",method="POST",
         data=json.dumps(payload).encode(),headers={**HEAD,"Content-Type":"application/json"})
    try:
        with opener.open(req,timeout=35) as resp:
            if resp.status!=202:raise RuntimeError("SEND_NOT_ACCEPTED")
            resp.read(1000)
        accepted=round(time.monotonic()-started,2)
        url=BASE+"/api/lalm_station/stream?"+urllib.parse.urlencode({"requestId":rid})
        first=None; complete=None; output=0; tokens={};status=[]
        with opener.open(urllib.request.Request(url,headers=HEAD),timeout=220) as response:
            for raw in response:
                if time.monotonic()-started>210:
                    raise RuntimeError("PERF_PROBE_TIMEOUT")
                try: event=json.loads(raw)
                except (ValueError,UnicodeError):continue
                if event.get("type")=="CONTEXT":
                    tokens={"input":event.get("estimatedInputTokens"),
                       "system":(event.get("tokenBreakdown") or {}).get("system"),
                       "history":(event.get("tokenBreakdown") or {}).get("history"),
                       "reservedOutput":event.get("reservedOutputTokens")}
                elif event.get("type")=="DELTA":
                    v=event.get("text") or ""
                    output+=len(v)
                    if first is None and v:first=round(time.monotonic()-started,2)
                elif event.get("type")=="STATUS":
                    status.append(str(event.get("phase") or ""))
                elif event.get("type") in ("COMPLETE","COMPLETED","FAILED","CANCELLED"):
                    complete=event.get("type")
                    break
        print("GLOBAL_ROUTE_BASELINE",json.dumps({"route":label,"accepted":accepted,
              "firstText":first,"total":round(time.monotonic()-started,2),
              "responseLength":output,"terminal":complete,"tokens":tokens,
              "stages":status[-8:]}),flush=True)
    except Exception as error:
        print("GLOBAL_ROUTE_BASELINE_ERROR",json.dumps({"route":label,
              "exception":type(error).__name__,"seconds":round(time.monotonic()-started,2)}),flush=True)
print("GLOBAL_ROUTE_BASELINE_COMPLETE",flush=True)
