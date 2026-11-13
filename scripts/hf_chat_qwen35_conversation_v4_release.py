#!/usr/bin/env python3
"""Guarded §C conversation-v4 rollout: actual ready + two-turn live latency test.

No new Space, external inference provider, paid hardware, or older-server sync.
Only existing exact current Hugging Face source; guarded rollback on failure.
"""
from __future__ import annotations
import json,os,time,urllib.error,urllib.request
from huggingface_hub import HfApi
from hf_chat_qwen35_conversation_v4 import SPACE,PROFILE,publish,rollback
from probe_chat_qwen35_two_turns import PROMPTS,turn

BASE="https://kamiloki-swyrlz.hf.space"

def fetch(path):
    request=urllib.request.Request(BASE+path,
             headers={"Cache-Control":"no-cache","User-Agent":"Swrlz-V4-Release-Health"})
    with urllib.request.urlopen(request,timeout=15) as resp:
        return json.load(resp)

def verify_ready(api,revision,timeout=1350):
    start=time.monotonic()
    count=0
    while time.monotonic()-start<timeout:
        count+=1
        if api.repo_info(SPACE,repo_type="space").sha!=revision:
            raise RuntimeError("Space HEAD changed after publication; refuse stale tests")
        try:
            observation=fetch("/api/hf/qwen35-ready")
            if (observation.get("ready") is True and
                 observation.get("model")=="qwen3.5-9b" and
                 observation.get("profile")==PROFILE):
                cpus=int(observation.get("cpuCapacity") or 0)
                if cpus<1:raise RuntimeError("No CPU capacity reported")
                if (observation.get("decodeThreads")!=min(16,cpus)
                    or observation.get("batchThreads")!=min(16,cpus)
                    or observation.get("batchSize")!=(2048 if cpus>=8 else 512)
                    or observation.get("microBatchSize")!=(1024 if cpus>=8 else 256)):
                    raise RuntimeError("Live CPU settings differ from required profile")
                print(json.dumps({"stage":"V4_MODEL_WARM_AND_READY",
                    "revision":revision,"profile":observation,"checks":count}),flush=True)
                return
        except (urllib.error.URLError,ValueError,TimeoutError) as error:
            if count%6==0:
                print(json.dumps({"stage":"V4_WARMUP_PENDING",
                     "attempts":count,"cause":type(error).__name__}),flush=True)
        time.sleep(12)
    raise RuntimeError("§C 9B v4 startup did not confirm the warmed profile")

def benchmark():
    results=[]
    for i,prompt in enumerate(PROMPTS,1):
        outcome=turn(prompt)
        results.append(outcome)
        print("V4_TURN_LATENCY",json.dumps({"turn":i,**outcome}),flush=True)
    initial,followup=results
    if initial["totalSeconds"]>=30:
        raise RuntimeError("Simple greeting latency regressed over 30s")
    if followup["totalSeconds"]>=50:
        raise RuntimeError("Natural followup remains above 50s target")
    print(json.dumps({
        "stage":"V4_TWO_TURN_BENCHMARK_PASS",
        "greetingSeconds":initial["totalSeconds"],
        "followupSeconds":followup["totalSeconds"],
        "oldGreetingSeconds":6.48,"oldFollowupSeconds":77.39,
        "followupSpeedup":round(77.39/followup["totalSeconds"],2)
    }),flush=True)

def main():
    if os.environ.get("SWRLZ_QWEN35_CONVERSATION_V4_APPROVED")!="1":
        raise RuntimeError("No explicit owner-reviewed authorization")
    token=os.environ.get("HF_TOKEN") or ""
    if len(token)<12:raise RuntimeError("Existing owner HF_TOKEN unavailable")
    api=HfApi(token=token)
    revision,before=publish(api)
    try:
        verify_ready(api,revision)
        benchmark()
    except Exception:
        print(json.dumps({"stage":"CONVERSATION_V4_ACCEPTANCE_FAILED",
                          "action":"restore exact original HF files"}),flush=True)
        rollback(api,revision,before)
        raise
    print("QWEN35_CONVERSATION_V4_LIVE_ACCEPTED",flush=True)

if __name__=="__main__":
    main()
