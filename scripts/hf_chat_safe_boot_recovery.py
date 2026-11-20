#!/usr/bin/env python3
"""Recover §C HTTP service without disguising an unavailable Qwen model.

Exact two-file, source-pinned deployment. Native compiler diagnostics remain
observable while a warmup failure is nonfatal to the web/Station ASGI server.
"""
from __future__ import annotations
import ast, hashlib, io, json, os, re, time, urllib.request, urllib.error
from pathlib import Path
from huggingface_hub import HfApi, hf_hub_download, CommitOperationAdd

SPACE="kamiloki/Swyrlz"
EXPECTED="5e646baf86c86703e04e324b928387e565501f33"
FILES=("app.py","qwen35_single_runtime.py")
BACKUP=Path("reports/swrlz-chat-safe-boot-20261120")
BASE="https://kamiloki-swyrlz.hf.space"
APP_OLD='''    except Exception as exc:
        print(json.dumps({"event": "HF_WARMUP_FAILED", "modelId": "qwen35-9b",
                          "errorType": type(exc).__name__, "detail": str(exc)[:300]}), flush=True)
        raise'''
APP_NEW='''    except Exception as exc:
        print(json.dumps({"event": "HF_WARMUP_FAILED", "modelId": "qwen35-9b",
                          "errorType": type(exc).__name__, "detail": str(exc)[:300],
                          "webServerCanStart": True}), flush=True)
        # Preserve a truthful unavailable-model state without killing the web server.
        # No artificial readiness flag or substitute inference route is installed.
        return'''
QWEN_OLD='''        subprocess.run(["cmake", "--build", str(root / "build"), "--target",
                        "llama-server", "--parallel", str(DECODE_THREADS)],
                       check=True, timeout=1200, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)'''
QWEN_NEW='''        # Keep inference tuning independent of low-memory native compilation.
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

def sha(v): return hashlib.sha256(v).hexdigest()

def emit(event,**data):
    print("SWRLZ_SAFE_BOOT",json.dumps({"event":event,**data},sort_keys=True),flush=True)

def api_client():
    token=os.environ.get("HF_TOKEN")
    if not token: raise RuntimeError("Existing authorized HF_TOKEN is unavailable")
    return HfApi(token=token)

def get_files(api,revision):
    listed=set(api.list_repo_files(SPACE,repo_type="space",revision=revision))
    if not set(FILES).issubset(listed):
        raise RuntimeError("Expected live native boot sources missing")
    return {name:Path(hf_hub_download(SPACE,name,repo_type="space",
                  revision=revision,token=api.token)).read_bytes() for name in FILES}

def patch(original):
    result={}
    for name,old,new in (("app.py",APP_OLD,APP_NEW),
                         ("qwen35_single_runtime.py",QWEN_OLD,QWEN_NEW)):
        before=original[name].decode("utf-8")
        if before.count(old)!=1:
            raise RuntimeError("Unexpected startup source drift in "+name)
        after=before.replace(old,new,1)
        ast.parse(after,filename=name)
        if name=="app.py":
            if before.count('    _warm_backends()')!=1 or after.count('    _warm_backends()')!=1:
                raise RuntimeError("Missing single canonical startup warmup call")
            if 'uvicorn.run(app,host="0.0.0.0"' not in after:
                raise RuntimeError("Stable ASGI listener missing")
        else:
            for constant in ("MODEL_REPO = ","MODEL_REVISION = ","MODEL_FILE = ",
                             "PROJECTOR_FILE = ","LLAMA_CPP_COMMIT = ",
                             "DECODE_THREADS = ","BATCH_THREADS = "):
                a=[v for v in before.splitlines() if v.startswith(constant)]
                b=[v for v in after.splitlines() if v.startswith(constant)]
                if a!=b: raise RuntimeError("Inference contract drift: "+constant)
        result[name]=after.encode("utf-8")
    return result

def inspect(api):
    revision=api.repo_info(SPACE,repo_type="space").sha
    if revision!=EXPECTED:raise RuntimeError("SPACE_REVISION_DRIFT "+str(revision))
    baseline=get_files(api,revision)
    candidate=patch(baseline)
    BACKUP.mkdir(parents=True,exist_ok=True)
    for name in FILES:
        (BACKUP/"before"/name).parent.mkdir(parents=True,exist_ok=True)
        (BACKUP/"before"/name).write_bytes(baseline[name])
        (BACKUP/"after"/name).parent.mkdir(parents=True,exist_ok=True)
        (BACKUP/"after"/name).write_bytes(candidate[name])
    m={"repo":SPACE,"revision":revision,"files":FILES,"before":{k:sha(v) for k,v in baseline.items()},
       "after":{k:sha(v) for k,v in candidate.items()},"scope":"web-startup-fail-open-and-native-build-logging"}
    (BACKUP/"manifest.json").write_text(json.dumps(m,indent=2)+"\n")
    emit("PREFLIGHT_OK",revision=revision,stage=str(api.get_space_runtime(SPACE).stage),
         fileHashes=m["after"])

def upload(api,parent,files,message):
    r=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=parent,
                        operations=[CommitOperationAdd(path_in_repo=k,path_or_fileobj=io.BytesIO(v))
                                    for k,v in files.items()],commit_message=message)
    return str(r.oid or api.repo_info(SPACE,repo_type="space").sha)

def probe():
    try:
        req=urllib.request.Request(BASE+"/?safe_boot="+str(time.monotonic_ns()),
            headers={"User-Agent":"Swyrlz-Verified-Recovery","Cache-Control":"no-cache"})
        with urllib.request.urlopen(req,timeout=16) as r:
            return r.status
    except urllib.error.HTTPError as e:return e.code
    except Exception:return 0

def capture_compiler_tail(api):
    try:
        lines=list(api.fetch_space_logs(SPACE,follow=False))
        for line in lines:
            s=str(line).strip()
            if "QWEN35_BUILD_FAILED" in s:
                emit("NATIVE_COMPILER_DIAGNOSTIC",detail=s[-6100:])
            elif '"event": "HF_WARMUP_' in s or '"event":"HF_WARMUP_' in s:
                emit("MODEL_WARMUP_STATUS",detail=s[:550])
    except Exception as exc:
        emit("LOGS_UNAVAILABLE",error=type(exc).__name__,detail=str(exc)[:140])

def verify(api,revision):
    prior=None
    consecutive=0
    for attempt in range(1,51):
        if api.repo_info(SPACE,repo_type="space").sha!=revision:
            raise RuntimeError("Concurrent Space revision change")
        runtime=api.get_space_runtime(SPACE)
        state=str(runtime.stage).upper().split(".")[-1]
        serving_sha=str((runtime.raw or {}).get("sha") or "")
        status=probe() if state=="RUNNING" else 0
        observed=(state,serving_sha,status)
        if observed!=prior:
            emit("RUNTIME",attempt=attempt,stage=state,expected=revision,
                 serving=serving_sha,httpStatus=status)
            prior=observed
        if state=="RUNNING" and serving_sha==revision and status==200:
            consecutive+=1
            if consecutive>=2:
                capture_compiler_tail(api)
                emit("WEB_SERVICE_RESTORED",revision=revision,online=True,
                     modelReadinessNotAssumed=True)
                return
        else:consecutive=0
        if state=="RUNTIME_ERROR":
            capture_compiler_tail(api)
            raise RuntimeError("Web service still fails startup after safe-boot patch")
        time.sleep(12)
    capture_compiler_tail(api)
    raise RuntimeError("Space never reached stable exact-revision HTTP 200")

def publish(api):
    if os.environ.get("SWRLZ_SAFE_BOOT_APPROVED")!="yes":
        raise PermissionError("Explicit user-approved recovery not supplied")
    m=json.loads((BACKUP/"manifest.json").read_text())
    old={k:(BACKUP/"before"/k).read_bytes() for k in FILES}
    new={k:(BACKUP/"after"/k).read_bytes() for k in FILES}
    if m["revision"]!=EXPECTED or m["repo"]!=SPACE or tuple(m["files"])!=FILES:
        raise RuntimeError("Unexpected pinned release manifest")
    if {k:sha(v) for k,v in old.items()}!=m["before"] or patch(old)!=new:
        raise RuntimeError("Immutable source or patch differs from preflight")
    if api.repo_info(SPACE,repo_type="space").sha!=EXPECTED or get_files(api,EXPECTED)!=old:
        raise RuntimeError("Live startup source changed since preflight")
    revision=None
    try:
        revision=upload(api,EXPECTED,new,
            "§C: keep Station web startup alive on native warmup failure, log bounded compiler errors")
        emit("SOURCE_COMMITTED",revision=revision)
        if get_files(api,revision)!=new:
            raise RuntimeError("Exact source readback mismatch")
        emit("SOURCE_READBACK_OK",revision=revision)
        verify(api,revision)
    except Exception as exc:
        emit("RECOVERY_REJECTED",revision=revision,error=type(exc).__name__,
             detail=str(exc)[:260])
        if revision and api.repo_info(SPACE,repo_type="space").sha==revision:
            rollback=upload(api,revision,old,
                "Rollback §C safe boot to exact prior app and native runtime")
            emit("EXACT_ROLLBACK",revision=rollback)
        elif revision:
            emit("ROLLBACK_PREVENTED_CONCURRENT_SOURCE_CHANGE")
        raise

if __name__=="__main__":
    import sys
    if sys.argv[1:] not in (["inspect"],["publish"]):
        raise SystemExit("Usage: inspect|publish")
    api=api_client()
    inspect(api) if sys.argv[1]=="inspect" else publish(api)
