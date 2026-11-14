#!/usr/bin/env python3
"""Read-only disposable two-turn Station session/request binding diagnostic."""
import http.cookiejar,json,time,urllib.request,urllib.parse,uuid
BASE="https://kamiloki-swyrlz.hf.space"
heads={"User-Agent":"Swrlz-Two-Turn-Session-Audit","Cache-Control":"no-cache"}
jar=http.cookiejar.CookieJar()
opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
thread="swrlz-session-check-"+str(uuid.uuid4())

def sync():
    with opener.open(urllib.request.Request(BASE+"/api/lalm_station/sync",headers=heads),timeout=24) as r:
        obj=json.load(r)
    gen=obj.get("activeGeneration") or {}
    threads=obj.get("threads") or []
    mine=next((x for x in threads if x.get("id")==thread),{})
    return {"active":gen.get("requestId"),"terminal":gen.get("terminal"),
        "phase":gen.get("phase"),"thread":gen.get("threadId"),
        "currentId":obj.get("currentId"),"threadExists":bool(mine),
        "messages":len(mine.get("messages") or []),
        "cookies":[x.name for x in jar]}

for i,prompt in enumerate(("What is 2 + 2? Answer 4 only.","What is 9 times 9? Answer 81 only.")):
    rid=str(uuid.uuid4())
    print("SESSION_TURN_BEGIN",json.dumps({"turn":i+1,"requestId":rid,
                                         "syncBefore":sync()}),flush=True)
    data={"modelId":"700m","prompt":prompt,"threadId":thread,"requestId":rid,
          "profileId":"LALM","timeZone":"UTC"}
    with opener.open(urllib.request.Request(BASE+"/api/lalm_station/send",
        method="POST",headers={**heads,"Content-Type":"application/json"},
        data=json.dumps(data).encode()),timeout=35) as response:
        print("SESSION_SEND",json.dumps({"status":response.status,
              "response":response.read().decode()[:120]}),flush=True)
    print("SESSION_AFTER_SEND",json.dumps(sync()),flush=True)
    url=BASE+"/api/lalm_station/stream?"+urllib.parse.urlencode({"requestId":rid})
    events=[];terminal=None
    with opener.open(urllib.request.Request(url,headers=heads),timeout=190) as stream:
        for ln in stream:
            try:ev=json.loads(ln)
            except Exception:continue
            kind=ev.get("type")
            if kind in ("STATUS","DELTA","COMPLETE","COMPLETED","FAILED","CANCELLED"):
                events.append({"kind":kind,"phase":ev.get("phase"),
                       "rid":ev.get("requestId"),"bytes":len(str(ev.get("text") or ""))})
            if kind in ("COMPLETE","COMPLETED","FAILED","CANCELLED"):
                terminal=kind;break
    print("SESSION_STREAM_DONE",json.dumps({"turn":i+1,"terminal":terminal,
         "lastEvents":events[-9:]}),flush=True)
    for n in range(8):
        state=sync()
        print("SESSION_SYNC_SNAPSHOT",json.dumps({"turn":i+1,
            "iteration":n,"expected":rid,**state}),flush=True)
        if state["active"]==rid and state["terminal"]:break
        time.sleep(2)
print("SESSION_TWO_TURN_AUDIT_COMPLETE",flush=True)
