#!/usr/bin/env python3
"""Wait for the exact Hugging Face Space commit to be RUNNING before live QA.

A ready model endpoint may belong to an OLD Space image. Hugging Face runtime
raw.sha is the image revision; repo_info.sha is only the repository head.
Fail closed if a newer commit supersedes the candidate.
"""
from __future__ import annotations
import argparse,json,os,sys,time
from pathlib import Path
from huggingface_hub import HfApi
DEFAULT_SPACE="kamiloki/Swyrlz"
RUNNING={"RUNNING"}
def ready(stage,served,expected):
    return str(stage).upper() in RUNNING and served==expected and bool(expected)
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--manifest",required=True)
    p.add_argument("--space",default=DEFAULT_SPACE)
    p.add_argument("--limit-seconds",type=int,default=900)
    p.add_argument("--poll-seconds",type=int,default=12)
    x=p.parse_args()
    data=json.loads(Path(x.manifest).read_text())
    expected=str(data.get("publishedRevision") or "").strip()
    if len(expected)!=40 or any(ch not in "0123456789abcdef" for ch in expected):
        raise RuntimeError("Release manifest does not contain an exact 40-character serving SHA")
    api=HfApi(token=os.environ.get("HF_TOKEN") or None)
    # One stable candidate and one stable serving image for at least two polls.
    repeats=0;last=None;started=time.monotonic()
    while time.monotonic()-started<x.limit_seconds:
        head=str(api.repo_info(x.space,repo_type="space").sha)
        if head!=expected:
            raise RuntimeError("Space repository head changed during deployment; cancel acceptance")
        runtime=api.get_space_runtime(x.space)
        stage=str(runtime.stage)
        served=str((runtime.raw or {}).get("sha") or "")
        observed={"expected":expected,"repo_head":head,"served":served,"stage":stage}
        if observed!=last:
            print("SPACE_REVISION_GATE",json.dumps(observed),flush=True)
            last=observed
        if ready(stage,served,expected):
            repeats+=1
            if repeats>=2:
                print("SPACE_REVISION_GATE_ACCEPTED",expected,flush=True)
                return 0
        else:repeats=0
        time.sleep(max(2,x.poll_seconds))
    raise RuntimeError("Exact approved release never reached RUNNING; do not claim live acceptance")
if __name__=="__main__":
    if (os.getenv("SWRLZ_REVISION_GATE_SELFTEST") or "")=="1":
        tests=[("RUNNING","a"*40,"a"*40,True),
               ("RUNNING_APP_STARTING","a"*40,"a"*40,False),
               ("RUNNING","b"*40,"a"*40,False),
               ("STOPPED","a"*40,"a"*40,False)]
        for stage,served,expected,out in tests:
            assert ready(stage,served,expected) is out
        print("SPACE_REVISION_GATE_STATIC_PASS",len(tests),flush=True)
    else:sys.exit(main())
