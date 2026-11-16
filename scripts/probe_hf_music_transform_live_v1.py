#!/usr/bin/env python3
"""Anonymous real-model §C music-transform acceptance, synthetic authored lyrics."""
from __future__ import annotations
import json,time,uuid
import requests
from scripts.probe_hf_music_stop_live_v1 import wait_ready,BASE
from scripts.music_transform_quality_v1 import quality_review

SOURCE=[
    "In a quiet brass observatory the first lantern began to glow",
    "A clock beneath the moon kept time for footsteps in the snow",
    "The keeper found a tiny gear behind the cedar door",
    "And heard a distant signal from the lighthouse on the shore",
]
def log(event,**data):
    print("SWRLZ_GUEST_MUSIC_LIVE",json.dumps({"event":event,**data},sort_keys=True),flush=True)
def main():
    wait_ready()
    s=requests.Session()
    response=s.get(BASE+"/api/account/me",timeout=25)
    if response.ok and (response.json() or {}).get("user"):
        raise RuntimeError("Authenticated identity in guest test")
    if s.get(BASE+"/api/lalm_station/sync",timeout=30).status_code!=200:
        raise RuntimeError("Guest sync unavailable")
    rid="music-transform-test-"+uuid.uuid4().hex[:18]
    tid="music-transform-thread-"+uuid.uuid4().hex[:18]
    prompt=(
        "Create a complete ORIGINAL folk-rap remix from this little song fragment I wrote. "
        "Make a fresh new title, Verse 1, Chorus, Verse 2, Chorus, Verse 3, and Outro. "
        "Each verse should depict a different event and have a unique rhyme palette. "
        "Do not repeat non-chorus verses or copy any complete source line. "
        "Keep an emotionally coherent opening, turning point and ending. "
        "Return the song only. Here is my original sample:\n"+
        "\n".join(SOURCE))
    body={"protocolVersion":2,"modelId":"700m","profileId":"LALM",
          "ingress":"SWRLZ_LALM_STATION","threadId":tid,"requestId":rid,
          "messageId":"u-"+uuid.uuid4().hex[:16],"assistantMessageId":"a-"+uuid.uuid4().hex[:16],
          "prompt":prompt,"profile":"","userProfile":"","timeZone":"UTC"}
    start=time.monotonic()
    r=s.post(BASE+"/api/lalm_station/send",json=body,headers={"X-SWRLZ-Request-Id":rid},timeout=35)
    if r.status_code!=202 or r.json().get("requestId")!=rid:
        raise RuntimeError("Guest music send rejected "+str(r.status_code))
    log("accepted",status=202)
    deadline=time.monotonic()+390
    while time.monotonic()<deadline:
        snapshot=s.get(BASE+"/api/lalm_station/sync",timeout=25).json()
        active=snapshot.get("activeGeneration") or {}
        if active.get("requestId")==rid and active.get("terminal"):
            if str(active.get("terminalType") or "") not in ("COMPLETE","COMPLETED"):
                raise RuntimeError("Music turn did not complete: "+str(active.get("terminalType")))
            thread=next((x for x in snapshot.get("threads") or [] if x.get("id")==tid),{})
            msgs=[x for x in thread.get("messages") or [] if x.get("role")=="assistant"
                  and (x.get("meta") or {}).get("requestId")==rid]
            if not msgs:
                raise RuntimeError("No durable assistant message after success")
            text=str(msgs[-1].get("text") or "")
            quality=quality_review(text)
            sections={x.lower() for x in ("verse 1","verse 2","verse 3","chorus","outro") if x in text.lower()}
            copied=sum(1 for line in SOURCE if line.casefold() in text.casefold())
            fallback="couldn't verify" in text.lower() or "couldn't complete" in text.lower()
            log("finished",elapsedMs=round((time.monotonic()-start)*1000),
                chars=len(text),quality=quality["status"],reasons=quality["reasons"],
                verseCount=quality["verseCount"],sectionLabels=sorted(sections),
                verbatimReferenceLines=copied,fallback=fallback)
            if quality["status"]!="PASS" or copied or fallback or len(sections)<4:
                raise AssertionError("Real music remix output failed structural acceptance")
            log("music_transform_pass",syntheticOnly=True)
            return
        time.sleep(2)
    raise TimeoutError("No complete music turn within bounded evaluation window")

if __name__=="__main__":
    main()
