"""Release verification / conditional rollback for a pre-approved §C CPU tuning commit.

No model/provider/hardware changes. Upload and verify on current Space only.
A failed live warmup restores the exact source at the immutable prior HF SHA
unless somebody else has published a newer revision in the meantime.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import tempfile
import time
import urllib.error
import urllib.request

from huggingface_hub import HfApi, hf_hub_download, CommitOperationAdd
from hf_qwen35_free_cpu_tune import SPACE, RUNTIME_FILE, STATION_FILE, candidate

BASE = "https://kamiloki-swyrlz.hf.space"
NAMES = (RUNTIME_FILE, STATION_FILE)
EXPECTED_PROFILE = "swrlz-qwen35-cpu-v2"


def _fetch_json(path: str):
    req = urllib.request.Request(BASE+path, headers={
        "Cache-Control":"no-cache", "User-Agent":"Swrlz-Qwen35-CPU-Profile-Release"})
    with urllib.request.urlopen(req, timeout=14) as response:
        return json.load(response)


def verify_ready(api: HfApi, new_revision: str, *, timeout_seconds: int = 1500):
    deadline=time.monotonic()+timeout_seconds
    attempt=0
    while time.monotonic() < deadline:
        attempt+=1
        if api.repo_info(SPACE,repo_type="space").sha != new_revision:
            raise RuntimeError("Concurrent update detected after publication")
        try:
            snapshot=_fetch_json("/api/hf/qwen35-ready")
            if (snapshot.get("model")=="qwen3.5-9b"
                and snapshot.get("ready") is True
                and snapshot.get("profile")==EXPECTED_PROFILE):
                capacity=_fetch_json("/api/hf/runtime-capacity").get("cpu",{}).get("limitCores")
                permitted=16 if not isinstance(capacity,(int,float)) or capacity<=0 else min(16,max(1,int(capacity)))
                decode=min(10,permitted)
                batch=min(16,permitted)
                if (snapshot.get("decodeThreads") != decode
                    or snapshot.get("batchThreads") != batch
                    or snapshot.get("batchSize") != 512
                    or snapshot.get("microBatchSize") != 256):
                    raise RuntimeError("Runtime CPU profile does not match reported quota")
                print(json.dumps({"status":"QWEN35_TUNED_PROFILE_LIVE_READY",
                    "revision":new_revision,"profile":snapshot,
                    "cpuQuotaCores":capacity,"checks":attempt}),flush=True)
                return
        except (urllib.error.URLError,ValueError,TimeoutError) as error:
            if attempt%6==0:
                print(json.dumps({"status":"CPU_PROFILE_WARMUP_PENDING",
                       "attempts":attempt,"cause":type(error).__name__}),flush=True)
        if attempt%6==0:
            print(json.dumps({"status":"CPU_PROFILE_NOT_YET_READY",
                              "attempts":attempt}),flush=True)
        time.sleep(12)
    raise RuntimeError("New 9B CPU profile did not become warm and ready within verification window")


def rollback(api: HfApi, *, source: str, candidate_revision: str):
    head=api.repo_info(SPACE,repo_type="space").sha
    if head!=candidate_revision:
        raise RuntimeError("Refusing rollback: concurrent Space update is present")
    with tempfile.TemporaryDirectory(prefix="qwen35-cpu-rollback-") as td:
        operations=[]
        for name in NAMES:
            data=Path(hf_hub_download(SPACE,name,revision=source,
                                       repo_type="space",token=api.token)).read_bytes()
            file=Path(td)/name
            file.write_bytes(data)
            operations.append(CommitOperationAdd(path_in_repo=name,
                                                  path_or_fileobj=str(file)))
        res=api.create_commit(
           repo_id=SPACE,repo_type="space",parent_commit=candidate_revision,
           operations=operations,
           commit_message="Rollback §C Qwen3.5-9B CPU profile trial to exact prior source")
        rev=str(res.oid)
        for name in NAMES:
            old=Path(hf_hub_download(SPACE,name,revision=source,
                                     repo_type="space",token=api.token)).read_bytes()
            latest=Path(hf_hub_download(SPACE,name,revision=rev,
                                        repo_type="space",token=api.token)).read_bytes()
            if hashlib.sha256(old).digest()!=hashlib.sha256(latest).digest():
                raise RuntimeError("Incomplete CPU-profile rollback: "+name)
        print(json.dumps({"status":"QWEN35_CPU_PROFILE_ROLLED_BACK",
                          "previous":source,"failedTrial":candidate_revision,
                          "rollbackRevision":rev}),flush=True)


def run():
    if os.environ.get("SWRLZ_QWEN35_CPU_TUNE_APPROVED")!="1":
        raise RuntimeError("Owner approval missing")
    token=os.environ.get("HF_TOKEN") or ""
    if len(token)<12:
        raise RuntimeError("Existing release secret missing")
    api=HfApi(token=token)
    record=candidate(api,publish=True)
    new_revision=record.get("newRevision")
    if not new_revision:
        raise RuntimeError("No confirmed Space publication")
    try:
        verify_ready(api,new_revision)
    except Exception:
        print(json.dumps({"status":"CPU_PROFILE_ACCEPTANCE_FAILED",
                          "revision":new_revision,"action":"guarded rollback"}),flush=True)
        rollback(api,source=record["sourceRevision"],candidate_revision=new_revision)
        raise


if __name__=="__main__":
    run()
