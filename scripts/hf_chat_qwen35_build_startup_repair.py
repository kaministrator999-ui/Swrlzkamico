#!/usr/bin/env python3
"""Revision-pinned, single-file Qwen startup build repair for the existing §C Space.

Fix only llama.cpp build concurrency and preserve useful diagnostics on a failed build.
Do not change inference threads, weights, routing, account, Station, or Chat UI.
"""
import argparse
import ast
import hashlib
import io
import json
import os
from pathlib import Path
import time
import urllib.error
import urllib.request

from huggingface_hub import CommitOperationAdd, HfApi, hf_hub_download

SPACE="kamiloki/Swyrlz"
FILE="qwen35_single_runtime.py"
START_REV="ef65f2a0f38262a37ba98ffba87b3af5c8431675"
BACKUP=Path("reports/swrlz-qwen35-build-startup-repair")
BASE="https://kamiloki-swyrlz.hf.space"
OLD='''        subprocess.run(["cmake", "--build", str(root / "build"), "--target",
                        "llama-server", "--parallel", str(DECODE_THREADS)],
                       check=True, timeout=1200, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)'''
NEW='''        # Build with bounded compile parallelism; inference thread settings are independent.
        # Emit only bounded compiler diagnostics if the native build fails.
        build_threads = max(1, min(2, CPU_CAPACITY))
        build = subprocess.run(["cmake", "--build", str(root / "build"), "--target",
                                "llama-server", "--parallel", str(build_threads)],
                               check=False, timeout=1200, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT, text=True)
        if build.returncode:
            print(json.dumps({"event":"QWEN35_BUILD_FAILED",
                              "exitCode":build.returncode,"buildThreads":build_threads,
                              "compilerTail":(build.stdout or "")[-5000:]}),flush=True)
            raise subprocess.CalledProcessError(build.returncode, "cmake llama-server")
        print(json.dumps({"event":"QWEN35_BUILD_SUCCEEDED",
                          "buildThreads":build_threads}),flush=True)'''


def emit(kind,**details):
    print("SWRLZ_QWEN_BUILD_REPAIR",json.dumps({"event":kind,**details},sort_keys=True),flush=True)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def source(api,revision):
    files=set(api.list_repo_files(SPACE,repo_type="space",revision=revision))
    if FILE not in files: raise RuntimeError("Expected native runtime owner absent")
    return Path(hf_hub_download(SPACE,FILE,repo_type="space",
                revision=revision,token=api.token)).read_bytes()


def patch(blob):
    original=blob.decode("utf-8")
    if original.count(OLD)!=1: raise RuntimeError("SOURCE_DRIFT: expected one native build target")
    if original.count('DECODE_THREADS = 18 if CPU_CAPACITY == 16')!=1:
        raise RuntimeError("Unexpected inference thread profile; refuse patch")
    if 'QWEN35_BUILD_FAILED' in original:
        raise RuntimeError("Repair already applied")
    candidate=original.replace(OLD,NEW,1)
    ast.parse(candidate,filename=FILE)
    for constant in ("MODEL_REPO = ","MODEL_REVISION = ","MODEL_FILE = ","PROJECTOR_FILE = ",
                     "LLAMA_CPP_COMMIT = ","DECODE_THREADS = ","BATCH_THREADS = "):
        before=[line for line in original.splitlines() if line.startswith(constant)]
        after=[line for line in candidate.splitlines() if line.startswith(constant)]
        if before!=after: raise RuntimeError("Model or inference contract was modified: "+constant)
    if candidate.count(NEW)!=1:raise RuntimeError("Expected one bounded build patch")
    return candidate.encode("utf-8")


def checkpoint(api):
    info=api.repo_info(SPACE,repo_type="space")
    if info.sha!=START_REV:
        raise RuntimeError("LIVE_REVISION_MOVED: expected "+START_REV+" got "+str(info.sha))
    runtime=api.get_space_runtime(SPACE)
    emit("BASELINE",revision=info.sha,stage=str(runtime.stage))
    original=source(api,info.sha)
    candidate=patch(original)
    BACKUP.mkdir(parents=True,exist_ok=True)
    (BACKUP/"original.py").write_bytes(original)
    (BACKUP/"candidate.py").write_bytes(candidate)
    (BACKUP/"manifest.json").write_text(json.dumps({
        "space":SPACE,"revision":info.sha,"path":FILE,
        "before":sha(original),"after":sha(candidate),
        "scope":"native-build-concurrency-only",
        "inferenceThreadsUnchanged":True,
        "modelWeightsUnchanged":True,
    },indent=2)+"\n",encoding="utf-8")
    emit("PREFLIGHT_OK",revision=info.sha,before=sha(original),
         after=sha(candidate),changeBytes=len(candidate)-len(original))


def commit(api,parent,bytes_,label):
    result=api.create_commit(repo_id=SPACE,repo_type="space",
        parent_commit=parent,operations=[CommitOperationAdd(path_in_repo=FILE,
                                  path_or_fileobj=io.BytesIO(bytes_))],
        commit_message=label)
    return str(result.oid or api.repo_info(SPACE,repo_type="space").sha)


def http_status():
    req=urllib.request.Request(BASE+"/?build_repair_check="+str(time.monotonic_ns()),
        headers={"User-Agent":"Swrlz-Qwen35-Runtime-Repair","Cache-Control":"no-cache"})
    try:
        with urllib.request.urlopen(req,timeout=16) as reply:
            return reply.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:
        return 0


def verify(api,revision):
    prior=None
    continuous=0
    for n in range(1,46):
        info=api.repo_info(SPACE,repo_type="space")
        if info.sha!=revision:raise RuntimeError("Concurrent Space commit changed target")
        state=api.get_space_runtime(SPACE)
        stage=str(state.stage).upper().split(".")[-1]
        served=str((state.raw or {}).get("sha") or "")
        status=http_status() if stage=="RUNNING" else 0
        observation=(stage,served,status)
        if observation!=prior:
            emit("RUNTIME_CHECK",attempt=n,stage=stage,served=served,
                 expected=revision,httpStatus=status)
            prior=observation
        if stage=="RUNNING" and served==revision and status==200:
            continuous+=1
            if continuous>=2:
                emit("RUNTIME_RESTORED",revision=revision,stage=stage,httpStatus=status)
                return
        else:
            continuous=0
        if stage=="RUNTIME_ERROR":
            raise RuntimeError("Space still fails startup after bounded compile attempt")
        time.sleep(12)
    raise RuntimeError("Repaired native Space did not reach verified RUNNING")


def publish(api):
    if os.environ.get("SWRLZ_QWEN_BUILD_REPAIR_APPROVED")!="1":
        raise PermissionError("Explicit approved startup repair required")
    m=json.loads((BACKUP/"manifest.json").read_text())
    before=(BACKUP/"original.py").read_bytes()
    after=(BACKUP/"candidate.py").read_bytes()
    if m["revision"]!=START_REV or m["space"]!=SPACE or m["path"]!=FILE:
        raise RuntimeError("Unexpected source manifest")
    if sha(before)!=m["before"] or sha(after)!=m["after"] or patch(before)!=after:
        raise RuntimeError("Source or patch changed after preflight")
    if api.repo_info(SPACE,repo_type="space").sha!=START_REV or source(api,START_REV)!=before:
        raise RuntimeError("Live source moved since snapshot")
    revision=None
    try:
        revision=commit(api,START_REV,after,
            "§C runtime repair: cap llama native build to 2 workers and expose diagnostics")
        emit("REPAIR_COMMITTED",revision=revision)
        if source(api,revision)!=after:
            raise RuntimeError("Repaired source SHA readback failed")
        emit("SOURCE_READBACK_OK",revision=revision)
        verify(api,revision)
    except Exception as e:
        emit("REPAIR_FAILED",revision=revision,error=type(e).__name__,
             detail=str(e)[:300])
        if revision and api.repo_info(SPACE,repo_type="space").sha==revision:
            restored=commit(api,revision,before,
                "Rollback §C native build to exact preceding source")
            emit("EXACT_SOURCE_ROLLBACK",revision=restored)
        elif revision:
            emit("ROLLBACK_BLOCKED_BY_CONCURRENT_CHANGE")
        raise


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("mode",choices=("inspect","publish"))
    args=parser.parse_args()
    api=HfApi(token=os.environ.get("HF_TOKEN") or None)
    if not api.token:raise RuntimeError("Existing authorized Hugging Face token required")
    if args.mode=="inspect":checkpoint(api)
    else:publish(api)
