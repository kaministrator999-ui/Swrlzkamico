#!/usr/bin/env python3
"""Read-only emoji routing and performance probe on existing §C 9B server.

No user conversations or PII, all messages are synthetic.
"""
from __future__ import annotations
import re, json, http.cookiejar, urllib.request, urllib.parse, uuid, time
from hf_chat_qwen35_conversation_v4 import CONVERSATION_FUNCTION

scope={"re":re}
exec(CONVERSATION_FUNCTION,scope)
social=scope["_qwen35_plain_social_turn"]

examples={
 "plain": "Lmao electric blue and teal definitely suit you. Mine's more of a shifting mix of colors, depends on the vibe. Anyway, goodnight Swyrlz, don't let the glitches bite!",
 "emoji": "Lmao electric blue and teal definitely suit you 😂 Mine's more of a shifting mix of colors, depends on the vibe. Anyway, goodnight §wyrlz, don't let the glitches bite! 🤣💜",
 "emoji-only": "Haha! 🤣💜",
 "nickname": "Goodnight §wyrlz!",
 "technical": "Can you debug our §E model coding?",
}
for key,phrase in examples.items():
    result=social(phrase,{}, {},None,False)
    print("EMOJI_ROUTE_PREDICATE",json.dumps({"case":key,"compactSocial":result}),flush=True)
    assert result==(key!="technical"),key

# Read-only source check confirms that the production Space still uses the
# expected same classifier without modifying any files.
from huggingface_hub import HfApi, hf_hub_download
from pathlib import Path
api=HfApi()
rev=api.repo_info("kamiloki/Swyrlz",repo_type="space").sha
engine=Path(hf_hub_download("kamiloki/Swyrlz","lfm2_700m_engine.py",
                            repo_type="space",revision=rev)).read_text()
assert CONVERSATION_FUNCTION in engine
print("LIVE_EMOJI_ROUTER_SOURCE_CONFIRMED",rev,flush=True)

# One new synthetic session, two real requests; print only timing and token
# budget metadata, no generated contents or personal user information.
opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
thread="swrlz-emoji-probe-"+str(uuid.uuid4())
base="https://kamiloki-swyrlz.hf.space"
headers={"User-Agent":"Swrlz-Emoji-Route-Test"}
def run(label,prompt):
    rid=str(uuid.uuid4())
    started=time.monotonic()
    payload={"modelId":"700m","prompt":prompt,"threadId":thread,
             "requestId":rid,"profileId":"LALM",
             "profile":"","userProfile":"","timeZone":"UTC"}
    req=urllib.request.Request(base+"/api/lalm_station/send",
         method="POST",data=json.dumps(payload).encode("utf-8"),
         headers={**headers,"Content-Type":"application/json"})
    with opener.open(req,timeout=40) as resp:
        if resp.status!=202:raise RuntimeError("PROBE_CHAT_SEND_NOT_ACCEPTED")
        resp.read(800)
    url=base+"/api/lalm_station/stream?"+urllib.parse.urlencode({"requestId":rid})
    first=None
    chars=0
    token_breakdown=None
    coding=None
    terminal=""
    with opener.open(urllib.request.Request(url,headers=headers),timeout=230) as resp:
        for raw in resp:
            try:
                event=json.loads(raw)
            except ValueError:
                continue
            typ=event.get("type")
            if typ=="DELTA":
                if event.get("text") and first is None:
                    first=round(time.monotonic()-started,2)
                chars+=len(event.get("text") or "")
            elif typ=="CONTEXT":
                token_breakdown=event.get("tokenBreakdown")
            elif typ=="PROGRAMMING_INTENT":
                val=event.get("intent") or {}
                coding=val.get("codingTask")
            elif typ in ("COMPLETE","COMPLETED","FAILED","CANCELLED"):
                terminal=typ
                break
            if time.monotonic()-started>215:
                raise RuntimeError("PROBE_LONG_RUNNING")
    observation={"case":label,"firstTextSeconds":first,
                 "totalSeconds":round(time.monotonic()-started,2),
                 "textLength":chars,"end":terminal,"coding":coding,
                 "tokenBreakdown":token_breakdown}
    print("EMOJI_LIVE_RESULT",json.dumps(observation),flush=True)
    if terminal not in ("COMPLETE","COMPLETED") or chars<3:
        raise RuntimeError("EMOJI_LIVE_PROBE_FAILED")
    return observation

run("prior-color-question","What's your favorite color?")
run("emoji-goodnight",examples["emoji"])
print("EMOJI_ROUTING_PROBE_COMPLETE",flush=True)
