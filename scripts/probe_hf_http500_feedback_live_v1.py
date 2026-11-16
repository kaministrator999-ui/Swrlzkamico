#!/usr/bin/env python3
"""Anonymous two-turn production acceptance for a previous remix HTTP500 screenshot.

Source+runtime pinned. No personal account, text logging, imported media,
model configuration changes, account login, or unbounded retries.
"""
from __future__ import annotations
import json
import time
import uuid
import requests
from huggingface_hub import HfApi

SPACE="kamiloki/Swyrlz"
BASE="https://kamiloki-swyrlz.hf.space"
EXPECTED="a72f505a00557ecd7218e6e68fff1fc2baad9e8a"

def log(event,**data):
    print("HTTP500_FOLLOWUP_LIVE",json.dumps({"event":event,**data},sort_keys=True),flush=True)

def await_running():
    api=HfApi()
    deadline=time.monotonic()+540
    while time.monotonic()<deadline:
        info=api.repo_info(SPACE,repo_type="space")
        if info.sha!=EXPECTED:raise RuntimeError("Unexpected live Space head; do not test a moved release")
        runtime=api.get_space_runtime(SPACE)
        stage=str(runtime.stage).upper()
        served=str((runtime.raw or {}).get("sha") or "")
        log("space",stage=stage,correctRevision=(served==EXPECTED))
        if "RUNNING" in stage and served==EXPECTED:return
        time.sleep(12)
    raise TimeoutError("Deployed revision not RUNNING after bounded wait")

def send_and_wait(session,thread_id,text):
    rid="feedback-accept-"+uuid.uuid4().hex[:16]
    body={
      "protocolVersion":2,"modelId":"700m","profileId":"LALM",
      "ingress":"SWRLZ_LALM_STATION","threadId":thread_id,
      "requestId":rid,"messageId":"u-"+uuid.uuid4().hex[:16],
      "assistantMessageId":"a-"+uuid.uuid4().hex[:16],
      "prompt":text,"profile":"","userProfile":"","timeZone":"UTC"
    }
    started=time.monotonic()
    ack=session.post(BASE+"/api/lalm_station/send",json=body,
       headers={"X-SWRLZ-Request-Id":rid},timeout=35)
    if ack.status_code!=202 or ack.json().get("requestId")!=rid:
        raise RuntimeError("Guest send rejected: "+str(ack.status_code))
    log("accepted",http=202)
    end=time.monotonic()+460
    phases=[]
    while time.monotonic()<end:
        data=session.get(BASE+"/api/lalm_station/sync",timeout=35).json()
        g=data.get("activeGeneration") or {}
        if g.get("requestId")==rid:
            phase=str(g.get("phase") or "")
            if phase and phase not in phases:phases.append(phase)
            if g.get("terminal"):
                state=str(g.get("terminalType") or "")
                status=g.get("status") or []
                thread=next((t for t in data.get("threads") or [] if t.get("id")==thread_id),{})
                found=[m for m in (thread.get("messages") or []) if m.get("role")=="assistant"
                       and (m.get("meta") or {}).get("requestId")==rid]
                reply=str((found[-1] if found else {}).get("text") or "")
                receipt={
                  "state":state,
                  "elapsedMs":round((time.monotonic()-started)*1000),
                  "chars":len(reply),
                  "phases":phases[-12:],
                  "researchStarted":any(str(x.get("phase") or "") in ("RESEARCH_STARTED","LYRICS_VERIFICATION") for x in status),
                  "native500":any("QWEN35_HTTP_500" in str(x.get("reason") or "") for x in status),
                }
                log("terminal",**receipt)
                if state not in ("COMPLETE","COMPLETED") or not reply.strip():
                    raise RuntimeError("Guest turn did not generate a durable response")
                return reply,receipt
        time.sleep(2)
    raise TimeoutError("No terminal receipt in bounded guest conversation")

def main():
    await_running()
    s=requests.Session()
    me=s.get(BASE+"/api/account/me",timeout=20)
    if me.ok and (me.json() or {}).get("user"):
        raise RuntimeError("Session is not anonymous; abort")
    if s.get(BASE+"/api/lalm_station/sync",timeout=30).status_code!=200:
        raise RuntimeError("Guest sync unavailable")
    thread="feedback-live-thread-"+uuid.uuid4().hex[:16]
    # User-created fictional source; no third-party lyrics or real identity.
    first=(
      "Make a short complete original rap remix from these two lines I wrote. "
      "Use Verse 1, Chorus, Verse 2, Outro. Give each verse unique wording. "
      "Keep it concise, about a weathered observatory and a lantern. My lines:\n"
      "Clockwork lanterns find the dawn.\nThe mountain winds are moving on."
    )
    reply1,_=send_and_wait(s,thread,first)
    log("source_answer",characters=len(reply1),hasMusicSection=("[Verse" in reply1))
    critique="I was just trying to tell you this is the issues with your remix version of the song"
    reply2,receipt=send_and_wait(s,thread,critique)
    low=reply2.casefold()
    has_generated_verses=("[verse 1]" in low or "[chorus]" in low or "lyrics\n" in low)
    apologetic_error=("local qwen inference failed" in low or "generation failed" in low)
    log("feedback_verdict",chars=len(reply2),
        generatedNewSong=has_generated_verses,
        unexpectedSearch=receipt["researchStarted"],
        displayedModelFailure=apologetic_error)
    if has_generated_verses or receipt["researchStarted"] or apologetic_error:
        raise AssertionError("Feedback turn still took new-lyrics/research/failure path")
    log("PASS",scope="guest-two-turn-feedback",modelIsReal=True)

if __name__=="__main__":
    main()
