#!/usr/bin/env python3
"""Real anonymous §C Stop probe; exact Space revision, no personal account.
Request and response contents are synthetic and are never printed.
"""
from __future__ import annotations
import json,os,time,uuid
import requests
from huggingface_hub import HfApi

SPACE="kamiloki/Swyrlz"
BASE="https://kamiloki-swyrlz.hf.space"
EXPECTED="e49039b3af00d726742c84077ce3da3b10a0b425"
def log(event,**data):
    print("SWRLZ_GUEST_STOP_LIVE",json.dumps({"event":event,**data},sort_keys=True),flush=True)
def wait_ready():
    api=HfApi()
    end=time.monotonic()+600
    while time.monotonic()<end:
        head=api.repo_info(SPACE,repo_type="space").sha
        if head!=EXPECTED:
            raise RuntimeError("Space head changed; do not test unknown release")
        runtime=api.get_space_runtime(SPACE)
        stage=str(runtime.stage).upper()
        served=str((runtime.raw or {}).get("sha") or "")
        log("space",stage=stage,revisionMatches=(served==EXPECTED))
        if "RUNNING" in stage and served==EXPECTED:
            return
        time.sleep(12)
    raise TimeoutError("New Space revision did not reach RUNNING before deadline")

def main():
    wait_ready()
    sess=requests.Session()
    sess.headers["User-Agent"]="§C-Anonymous-Stop-Acceptance"
    person=sess.get(BASE+"/api/account/me",timeout=25)
    if person.ok and (person.json() or {}).get("user"):
        raise RuntimeError("Unexpected authenticated session")
    initial=sess.get(BASE+"/api/lalm_station/sync",timeout=30)
    if initial.status_code!=200:
        raise RuntimeError("Anonymous Station sync unavailable: "+str(initial.status_code))
    rid="music-stop-test-"+uuid.uuid4().hex[:20]
    tid="music-stop-thread-"+uuid.uuid4().hex[:20]
    prompt="Create a completely original elaborate 100-line folk-fantasy narrative song about an observatory and a mechanical lantern. Write all verses and the ending."
    body={"protocolVersion":2,"modelId":"700m","profileId":"LALM",
          "ingress":"SWRLZ_LALM_STATION","threadId":tid,"requestId":rid,
          "messageId":"u-"+uuid.uuid4().hex[:16],
          "assistantMessageId":"a-"+uuid.uuid4().hex[:16],
          "prompt":prompt,"profile":"","userProfile":"","timeZone":"UTC"}
    started=time.monotonic()
    ack=sess.post(BASE+"/api/lalm_station/send",json=body,
                  headers={"X-SWRLZ-Request-Id":rid},timeout=35)
    if ack.status_code!=202 or ack.json().get("requestId")!=rid:
        raise RuntimeError("Synthetic guest send rejected: "+str(ack.status_code))
    log("accepted",status=ack.status_code)
    phase=""
    max_time=time.monotonic()+90
    while time.monotonic()<max_time:
        snap=sess.get(BASE+"/api/lalm_station/sync",timeout=20).json()
        active=snap.get("activeGeneration") or {}
        if active.get("requestId")==rid:
            phase=str(active.get("phase") or "")
            labels=[str(v.get("phase") or "") for v in active.get("status") or []]
            if phase in ("GENERATING","LOADING") or "GENERATING" in labels:
                break
            if active.get("terminal"):
                raise RuntimeError("Synthetic response already terminal before Stop")
        time.sleep(1)
    log("before_cancel",phase=phase,elapsedMs=round((time.monotonic()-started)*1000))
    stop_started=time.monotonic()
    stop=sess.post(BASE+"/api/lalm_station/cancel",json={"requestId":rid},timeout=20)
    if stop.status_code!=200:
        raise RuntimeError("Stop endpoint rejected: "+str(stop.status_code))
    outcome=stop.json()
    if not outcome.get("ok") or outcome.get("state") not in ("CANCEL_REQUESTED","CANCELLED"):
        raise RuntimeError("Stop was not acknowledged")
    native=bool(outcome.get("nativeInterruptRequested"))
    log("stop_ack",nativeInterruptRequested=native,ackMs=round((time.monotonic()-stop_started)*1000))
    deadline=time.monotonic()+70
    while time.monotonic()<deadline:
        snap=sess.get(BASE+"/api/lalm_station/sync",timeout=20).json()
        active=snap.get("activeGeneration") or {}
        if active.get("requestId")==rid and active.get("terminal"):
            terminal=str(active.get("terminalType") or "")
            elapsed=round((time.monotonic()-stop_started)*1000)
            log("terminal",state=terminal,msFromStop=elapsed,nativeInterruptRequested=native)
            if terminal!="CANCELLED":
                raise RuntimeError("Stop did not result in terminal CANCELLED")
            if elapsed>30000:
                raise RuntimeError("Stop terminal latency exceeded 30 seconds")
            log("guest_stop_pass",requestedModel="700m",syntheticOnly=True)
            return
        time.sleep(1)
    raise TimeoutError("No authoritative CANCELLED terminal state after Stop")

if __name__=="__main__":
    main()
