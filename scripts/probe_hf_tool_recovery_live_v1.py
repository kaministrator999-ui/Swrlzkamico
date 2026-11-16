#!/usr/bin/env python3
"""Read-only anonymous §C live continuity acceptance, synthetic original music.

Pins source revision. No user's conversation, purchased lyrics, credentials, §E,
login, model updates or production configuration are changed by this probe.
"""
from __future__ import annotations
import json
import re
import time
import uuid
import requests
from huggingface_hub import HfApi
from scripts.probe_hf_http500_feedback_live_v1 import send_and_wait,BASE

SPACE="kamiloki/Swyrlz"
EXPECTED="971de186d00ff0d59494e2cabaeb8b181d17bbbc"

def log(event,**values):
    print("SWRLZ_CAPABILITY_RECOVERY_GUEST "+
          json.dumps({"event":event,**values},sort_keys=True),flush=True)

def ready():
    api=HfApi()
    until=time.monotonic()+540
    while time.monotonic()<until:
        revision=str(api.repo_info(SPACE,repo_type="space").sha)
        if revision!=EXPECTED:
            raise RuntimeError("HF revision moved: refuse test against different source")
        runtime=api.get_space_runtime(SPACE)
        state=str(runtime.stage).upper()
        served=str((runtime.raw or {}).get("sha") or "")
        log("space",state=state,correctRevision=served==EXPECTED)
        if "RUNNING" in state and served==EXPECTED:return
        time.sleep(12)
    raise TimeoutError("Targeted HF revision not running in bounded window")

def main():
    ready()
    session=requests.Session()
    me=session.get(BASE+"/api/account/me",timeout=20)
    if me.ok and (me.json() or {}).get("user"):
        raise RuntimeError("Guest test unexpectedly has a user account")
    if session.get(BASE+"/api/lalm_station/sync",timeout=25).status_code!=200:
        raise RuntimeError("Anonymous Station sync unavailable")
    thread="tool-continuity-guest-"+uuid.uuid4().hex[:16]
    # User-owned fictional reference avoids external lyrics/copyright entirely.
    first=(
        "I wrote a fictional song called Night Lantern by Example Group. "
        "Your previous remix repeated Verse 1 and Verse 3, reused the same "
        "metaphors, and had no meaningful ending. Do you understand those "
        "problems? For now, discuss the critique only; do not write lyrics yet. "
        "Finish by offering to rewrite the song with three different verses, "
        "a new original hook, and an actual ending."
    )
    prior,meta=send_and_wait(session,thread,first)
    last=prior.casefold()
    offered=(bool(re.search(r"would you like.{0,140}(?:rewrite|revise|redo|rework|remix)",last))
             or bool(re.search(r"i can.{0,100}(?:rewrite|revise|redo|rework|remix)",last)))
    log("critique",length=len(prior),offeredRewrite=offered,
        hasUnwantedVerse=bool(re.search(r"(?m)^\s*\[?verse 1\]?",prior,re.I)),
        elapsedMs=meta["elapsedMs"])
    if not offered:
        raise AssertionError("Follow-up offer was not actually made; cannot test acceptance")
    answer,receipt=send_and_wait(session,thread,"Yes please")
    low=answer.casefold()
    has_verse=bool(re.search(r"\bverse\s*1\b",low))
    has_hook=bool(re.search(r"\b(?:chorus|hook)\b",low))
    denied_tool=bool(re.search(
        r"(?:i can(?:not|'t)|i don't|i do not).{0,90}(?:browse|search|access the web)",low))
    asked_for_source=bool(re.search(r"(?:give|provide|paste).{0,60}(?:original hook|lyrics)",low))
    log("accepted_rewrite",characters=len(answer),hasVerse=has_verse,
        hasHook=has_hook,deniedTool=denied_tool,
        requestedPublishedSource=asked_for_source,
        elapsedMs=receipt["elapsedMs"],researchStarted=receipt["researchStarted"])
    if denied_tool or asked_for_source or not has_verse or not has_hook or len(answer)<170:
        raise AssertionError("Accepted task lost continuity or false web incapability surfaced")
    log("PASS",scope="synthetic-anonymous-yes-please-continuity",source=EXPECTED)
if __name__=="__main__":
    main()
