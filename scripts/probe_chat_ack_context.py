#!/usr/bin/env python3
"""Anonymous live acceptance test for §C bare-ack inferencing.

Creates disposable synthetic conversation only; does not inspect any user
thread, account, persisted personal data or project artifacts.
"""
from __future__ import annotations
import http.cookiejar,json,time,urllib.parse,urllib.request,uuid
BASE="https://kamiloki-swyrlz.hf.space"
HEAD={"User-Agent":"Swrlz-AckContext-Synthetic-Verify-20261113","Cache-Control":"no-cache"}
def chat(opener,thread,prompt):
    rid=str(uuid.uuid4())
    started=time.monotonic()
    req=urllib.request.Request(BASE+"/api/lalm_station/send",method="POST",
        data=json.dumps({"modelId":"700m","prompt":prompt,"threadId":thread,
           "requestId":rid,"profileId":"LALM","profile":"","userProfile":"",
           "timeZone":"UTC"}).encode(),
        headers={**HEAD,"Content-Type":"application/json"})
    with opener.open(req,timeout=35) as response:
        if response.status!=202:raise RuntimeError("Synthetic send rejected")
        response.read()
    url=BASE+"/api/lalm_station/stream?"+urllib.parse.urlencode({"requestId":rid})
    result={"firstTextSec":None,"totalSec":None,"terminal":None,"outputChars":0,
            "ackFastRoute":None,"ackHistoryCompacted":None,
            "historyKept":None,"inputTokens":None}
    with opener.open(urllib.request.Request(url,headers=HEAD),timeout=220) as response:
        for raw in response:
            if time.monotonic()-started>205:
                raise RuntimeError("Synthetic response time budget exceeded")
            try: ev=json.loads(raw)
            except (ValueError,UnicodeError):continue
            kind=ev.get("type")
            if kind=="CONTEXT":
                result["ackFastRoute"]=ev.get("ackFastRoute")
                result["ackHistoryCompacted"]=ev.get("ackHistoryCompacted")
                result["historyKept"]=ev.get("historyMessagesKept")
                result["inputTokens"]=ev.get("estimatedInputTokens")
            if kind=="DELTA":
                t=str(ev.get("text") or "")
                if t and result["firstTextSec"] is None:
                    result["firstTextSec"]=round(time.monotonic()-started,2)
                result["outputChars"]+=len(t)
            if kind in ("COMPLETE","COMPLETED","FAILED","CANCELLED"):
                result["terminal"]=kind
                break
    result["totalSec"]=round(time.monotonic()-started,2)
    if result["terminal"] not in ("COMPLETE","COMPLETED") or result["outputChars"]<4:
        raise RuntimeError("Synthetic completion not accepted")
    return result

def conversation(prompts):
    opener=urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    thread="swrlz-ack-test-"+str(uuid.uuid4())
    results=[]
    for i,prompt in enumerate(prompts):
        r=chat(opener,thread,prompt)
        print("ACK_CONTEXT_SYNTHETIC",json.dumps({"case":i+1,**r}),flush=True)
        results.append(r)
    return results

def verify_live():
    # New Space source may be visible while the old worker is still serving;
    # require new per-turn marker, not just an unchanged readiness endpoint.
    deadline=time.monotonic()+600
    seen=False
    while time.monotonic()<deadline:
        try:
            r=conversation(("Good job!",))[0]
            if r.get("ackFastRoute") is True:
                seen=True
                print("ACK_CONTEXT_NEW_WORKER_LIVE",flush=True)
                break
            print("ACK_CONTEXT_OLD_WORKER_PENDING",flush=True)
        except Exception as exc:
            print("ACK_CONTEXT_RESTART_PENDING",type(exc).__name__,flush=True)
        time.sleep(12)
    if not seen:raise RuntimeError("New ack route marker not yet live")
    results=conversation(("Hey, how are you?","Doing well, just checking in.",
                          "Nice!", "Good job!"))
    ack=results[-1]
    if ack.get("ackFastRoute") is not True:
        raise RuntimeError("Bare social praise did not use fast branch")
    if ack.get("ackHistoryCompacted") is not True:
        raise RuntimeError("History with >=6 prior messages was not compacted")
    if ack.get("historyKept") is None or ack["historyKept"]>4:
        raise RuntimeError("Model received more than 4 prior messages")
    assert all(x["terminal"] in ("COMPLETE","COMPLETED") for x in results)
    print("ACK_CONTEXT_LIVE_REGRESSION_PASS",json.dumps({
        "ackHistoryCompacted":True,"ackFastRoute":True,
        "ackHistoryKept":ack["historyKept"],
        "ackFirstTextSec":ack["firstTextSec"],
        "ackTotalSec":ack["totalSec"],
        "modelNotReplaced":True}),flush=True)

if __name__=="__main__":verify_live()
