#!/usr/bin/env python3
"""One synthetic, unauthenticated §C latency probe. No personal data or writes."""
import http.cookiejar
import json
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid

BASE="https://kamiloki-swyrlz.hf.space"
SESSION=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
START=time.monotonic()
request_id=str(uuid.uuid4())
thread_id="synthetic-latency-"+str(uuid.uuid4())
payload={"modelId":"700m","prompt":"Hey how are you?","threadId":thread_id,
         "requestId":request_id,"profileId":"LALM","profile":"","userProfile":"",
         "timeZone":"UTC"}
req=urllib.request.Request(BASE+"/api/lalm_station/send",
       data=json.dumps(payload).encode(),method="POST",
       headers={"Content-Type":"application/json","User-Agent":"Swrlz-Anonymous-Perf-Synthetic"})
try:
    with SESSION.open(req,timeout=35) as response:
        initial=response.read(1024)
        print(json.dumps({"phase":"accepted","status":response.status,
            "sinceStartSeconds":round(time.monotonic()-START,2)}),flush=True)
    url=BASE+"/api/lalm_station/stream?"+urllib.parse.urlencode({"requestId":request_id})
    got_first=False
    statuses=[]
    delta_chars=0
    with SESSION.open(urllib.request.Request(url,headers={"User-Agent":"Swrlz-Anonymous-Perf-Synthetic"}),timeout=360) as response:
        for raw in response:
            if time.monotonic()-START>320:
                print(json.dumps({"phase":"probe-timeout","seconds":round(time.monotonic()-START,2)}),flush=True)
                break
            try:
                event=json.loads(raw)
            except (UnicodeError,ValueError):
                continue
            kind=event.get("type")
            if kind=="STATUS":
                statuses.append(event.get("phase"))
            elif kind=="DELTA":
                if not got_first:
                    got_first=True
                    print(json.dumps({"phase":"firstText","seconds":round(time.monotonic()-START,2)}),flush=True)
                delta_chars+=len(event.get("text") or "")
            elif kind in ("COMPLETE","COMPLETED","FAILED","CANCELLED"):
                print(json.dumps({"phase":"terminal","kind":kind,"status":event.get("phase"),
                    "seconds":round(time.monotonic()-START,2),"outputCharacters":delta_chars,
                    "phases":statuses[-12:]}),flush=True)
                break
    print("SYNTHETIC_CHAT_LATENCY_PROBE_FINISHED",flush=True)
except urllib.error.HTTPError as error:
    print(json.dumps({"phase":"unavailable","errorType":"HTTPError","status":error.code,
                     "seconds":round(time.monotonic()-START,2)}),flush=True)
except Exception as error:
    print(json.dumps({"phase":"unavailable","errorType":type(error).__name__,
                     "seconds":round(time.monotonic()-START,2)}),flush=True)
