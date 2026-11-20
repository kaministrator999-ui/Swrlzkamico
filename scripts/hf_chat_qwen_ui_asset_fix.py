#!/usr/bin/env python3
"""Recover native Qwen by disabling unneeded llama.cpp embedded WebUI assets.

The app uses llama-server on loopback for JSON/SSE; the llama.cpp browser UI
has no public role. Pin exact live Space source and upstream llama.cpp code.
"""
from __future__ import annotations
import ast, hashlib, io, json, os, time, urllib.request, urllib.error
from pathlib import Path
from huggingface_hub import HfApi, hf_hub_download, CommitOperationAdd

SPACE="kamiloki/Swyrlz"
FILE="qwen35_single_runtime.py"
START_REV="79c9f0dd2cd5ab89d351f2a678f4a52cc338ce88"
BACKUP=Path("reports/swrlz-native-ui-asset-fix")
BASE="https://kamiloki-swyrlz.hf.space"
OLD='''        subprocess.run([
            "cmake", "-S", str(root), "-B", str(root / "build"),
            "-DCMAKE_BUILD_TYPE=Release", "-DLLAMA_BUILD_SERVER=ON",
            "-DLLAMA_BUILD_TESTS=OFF", "-DLLAMA_BUILD_EXAMPLES=OFF",
            "-DLLAMA_CURL=OFF", "-DGGML_NATIVE=OFF",
        ], check=True, timeout=180, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)'''
NEW='''        # Native endpoint serves only loopback HTTP; never embed unrelated
        # Hugging Face llama-ui assets whose "latest" release can drift from
        # the pinned llama.cpp source. Both flags exist at LLAMA_CPP_COMMIT.
        for ui_dir in (root / "tools" / "ui" / "dist",
                       root / "build" / "tools" / "ui" / "dist"):
            if ui_dir.is_dir():
                shutil.rmtree(ui_dir)
        subprocess.run([
            "cmake", "-S", str(root), "-B", str(root / "build"),
            "-DCMAKE_BUILD_TYPE=Release", "-DLLAMA_BUILD_SERVER=ON",
            "-DLLAMA_BUILD_TESTS=OFF", "-DLLAMA_BUILD_EXAMPLES=OFF",
            "-DLLAMA_CURL=OFF", "-DGGML_NATIVE=OFF",
            "-DLLAMA_BUILD_UI=OFF", "-DLLAMA_USE_PREBUILT_UI=OFF",
        ], check=True, timeout=180, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)'''


def sha(blob): return hashlib.sha256(blob).hexdigest()
def emit(name,**props):
    print("SWRLZ_QWEN_UI_ASSET",json.dumps({"event":name,**props},sort_keys=True),flush=True)

def api_client():
    token=os.environ.get("HF_TOKEN")
    if not token: raise RuntimeError("Existing HF_TOKEN unavailable")
    return HfApi(token=token)

def source(api,rev):
    if FILE not in api.list_repo_files(SPACE,repo_type="space",revision=rev):
        raise RuntimeError("Live native model source not present")
    return Path(hf_hub_download(SPACE,FILE,repo_type="space",
                revision=rev,token=api.token)).read_bytes()

def patch(blob):
    original=blob.decode("utf-8")
    if original.count(OLD)!=1: raise RuntimeError("CMake configure source drift")
    if original.count('LLAMA_CPP_COMMIT = "7fe450e19305b828c199d602c23a8337aaa1f03b"')!=1:
        raise RuntimeError("Pinned upstream llama.cpp version changed")
    for needle in ('"QWEN35_BUILD_FAILED"','"QWEN35_BUILD_SUCCEEDED"',
                   'build_threads = max(1, min(2, CPU_CAPACITY))'):
        if needle not in original:raise RuntimeError("Missing verified safe-start diagnostics")
    updated=original.replace(OLD,NEW,1)
    ast.parse(updated,filename=FILE)
    if updated.count(NEW)!=1:raise RuntimeError("UI configure patch missing")
    for key in ("MODEL_REPO = ","MODEL_REVISION = ","MODEL_FILE = ",
                "PROJECTOR_FILE = ","LLAMA_CPP_COMMIT = ","DECODE_THREADS = ",
                "BATCH_THREADS = ","CONTEXT_TOKENS = "):
        before=[line for line in original.splitlines() if line.startswith(key)]
        after=[line for line in updated.splitlines() if line.startswith(key)]
        if before!=after:raise RuntimeError("Native inference identity changed: "+key)
    return updated.encode("utf-8")

def inspect(api):
    head=api.repo_info(SPACE,repo_type="space").sha
    if head!=START_REV:raise RuntimeError("LIVE_REVISION_DRIFT "+str(head))
    rt=api.get_space_runtime(SPACE)
    if str(rt.stage).split(".")[-1].upper()!="RUNNING":
        raise RuntimeError("UI-serving Space no longer RUNNING")
    old=source(api,head)
    new=patch(old)
    BACKUP.mkdir(parents=True,exist_ok=True)
    (BACKUP/"original.py").write_bytes(old)
    (BACKUP/"candidate.py").write_bytes(new)
    m={"space":SPACE,"revision":head,"file":FILE,"oldSha":sha(old),"newSha":sha(new),
       "scope":"disable-unneeded-embedded-ui-assets-on-pinned-native-build"}
    (BACKUP/"manifest.json").write_text(json.dumps(m,indent=2)+"\n",encoding="utf-8")
    emit("PREFLIGHT_OK",revision=head,sourceSha256=sha(old),candidateSha256=sha(new),
         modelWeightsChanged=False,inferenceThreadsChanged=False,webChatChanged=False)

def upload(api,parent,data,title):
    result=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=parent,
        operations=[CommitOperationAdd(path_in_repo=FILE,path_or_fileobj=io.BytesIO(data))],
        commit_message=title)
    return str(result.oid or api.repo_info(SPACE,repo_type="space").sha)

def http_status():
    try:
        req=urllib.request.Request(BASE+"/?native-ui-asset-check="+str(time.monotonic_ns()),
            headers={"User-Agent":"Swyrlz-Qwen-WebUI-Asset-Fix","Cache-Control":"no-cache"})
        with urllib.request.urlopen(req,timeout=15) as reply:return reply.status
    except urllib.error.HTTPError as exc:return exc.code
    except Exception:return 0

def model_status(api):
    try:
        lines=[str(x) for x in api.fetch_space_logs(SPACE,follow=False)]
        ready=any('"event": "HF_WARMUP_READY"' in line for line in lines)
        failed=[line for line in lines if "QWEN35_BUILD_FAILED" in line or
                '"event": "HF_WARMUP_FAILED"' in line]
        return ready and not failed, failed[-3:]
    except Exception as exc:
        emit("LOG_READ_FAILURE",type=type(exc).__name__,detail=str(exc)[:140])
        return False, []

def verify(api,revision):
    prev=None
    stable=0
    for attempt in range(1,66):
        if api.repo_info(SPACE,repo_type="space").sha!=revision:
            raise RuntimeError("Space revision changed during model repair")
        rt=api.get_space_runtime(SPACE)
        stage=str(rt.stage).split(".")[-1].upper()
        serving=str((rt.raw or {}).get("sha") or "")
        status=http_status() if stage=="RUNNING" else 0
        success=False
        failures=[]
        if stage=="RUNNING" and serving==revision and status==200:
            success,failures=model_status(api)
        observed=(stage,serving,status,success)
        if observed!=prev:
            emit("MODEL_RUNTIME",attempt=attempt,stage=stage,expected=revision,
                 serving=serving,httpStatus=status,warmupReady=success)
            prev=observed
        if failures:
            for line in failures:
                emit("MODEL_STARTUP_FAILURE",detail=line[-5000:])
            raise RuntimeError("Qwen native model warmup failed on new asset-free build")
        if success:
            stable+=1
            if stable>=2:
                emit("MODEL_READY_ACCEPTED",revision=revision,warmupReady=True,httpStatus=status)
                return
        else:stable=0
        if stage=="RUNTIME_ERROR":
            ready,bad=model_status(api)
            for line in bad:emit("RUNTIME_FAILURE_LOG",detail=line[-5000:])
            raise RuntimeError("Space failed startup after UI asset fix")
        time.sleep(12)
    raise RuntimeError("Model native warmup did not become ready on exact serving revision")

def publish(api):
    if os.environ.get("SWRLZ_QWEN_UI_ASSET_APPROVED")!="yes":
        raise PermissionError("Explicit authorized native model fix required")
    m=json.loads((BACKUP/"manifest.json").read_text())
    old=(BACKUP/"original.py").read_bytes()
    new=(BACKUP/"candidate.py").read_bytes()
    if m["revision"]!=START_REV or m["file"]!=FILE or m["space"]!=SPACE:
        raise RuntimeError("Mismatched release manifest")
    if sha(old)!=m["oldSha"] or sha(new)!=m["newSha"] or patch(old)!=new:
        raise RuntimeError("Source patch changed after preflight")
    if api.repo_info(SPACE,repo_type="space").sha!=START_REV or source(api,START_REV)!=old:
        raise RuntimeError("Live Space changed since preflight")
    revision=None
    try:
        revision=upload(api,START_REV,new,
            "§C: disable llama.cpp prebuilt UI assets for pinned Qwen API server")
        emit("MODEL_PATCH_COMMITTED",revision=revision)
        if source(api,revision)!=new:
            raise RuntimeError("Exact Qwen native source readback mismatch")
        emit("EXACT_READBACK_OK",revision=revision)
        verify(api,revision)
    except Exception as exc:
        emit("MODEL_PATCH_REJECTED",revision=revision,type=type(exc).__name__,
             detail=str(exc)[:290])
        if revision and api.repo_info(SPACE,repo_type="space").sha==revision:
            restored=upload(api,revision,old,
                "Rollback native llama UI asset change; preserve live Chat design")
            emit("NATIVE_FILE_ROLLED_BACK",revision=restored)
        elif revision:
            emit("ROLLBACK_BLOCKED_BY_CONCURRENT_UPDATE")
        raise

if __name__=="__main__":
    import sys
    if sys.argv[1:] not in (["inspect"],["publish"]):
        raise SystemExit("Usage: inspect|publish")
    api=api_client()
    inspect(api) if sys.argv[1]=="inspect" else publish(api)
