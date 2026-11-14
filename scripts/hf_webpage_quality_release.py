"""Guarded opt-in webpage-output quality release for actual running Hugging Face §C."""
from __future__ import annotations
import ast, hashlib, io, json, os, sys, time, urllib.request
from pathlib import Path
from huggingface_hub import HfApi, hf_hub_download, CommitOperationAdd
from hf_webpage_quality_policy_v1 import patch_coder,MARK

SPACE="kamiloki/Swyrlz"
BASE="https://kamiloki-swyrlz.hf.space"
TARGET="qwen_coder_engine.py"
EXPECTED_REV="b5fee5d3d123d4af498326f18b2a71f993e6baf1"
BACKUP=Path("swrlz-webpage-quality-source-backup")
APPROVAL="webpage-html-generation-quality-only"

def emit(stage,**fields):print(stage+" "+json.dumps(fields,sort_keys=True),flush=True)

def get_status(path):
    req=urllib.request.Request(BASE+path,
      headers={"Accept":"application/json","User-Agent":"SWRLZ-HTML-Quality-Release/1"})
    with urllib.request.urlopen(req,timeout=15) as res:
        if res.status!=200:raise RuntimeError("HTTP_STATUS_NON_200")
        data=res.read(3500)
        if len(data)>=3500:raise RuntimeError("BODY_TOO_LARGE")
        body=json.loads(data)
        if not isinstance(body,dict):raise RuntimeError("RESPONSE_SHAPE")
        return body

def healthy(api,deadline=380):
    until=time.monotonic()+deadline
    last="Initializing"
    while time.monotonic()<until:
        try:
            stage=api.get_space_runtime(SPACE).stage
            if stage!="RUNNING":
                last="stage:"+str(stage)[:30]
            else:
                status=get_status("/api/account/status")
                redis=get_status("/api/storage/valkey-native-gateway-check")
                ready=(isinstance(status,dict) and redis.get("backendSelected") is True
                       and redis.get("nativeSETGET") is True
                       and redis.get("nativeLua") is True)
                if ready:
                    emit("SWRLZ_WEB_QUALITY_RUNTIME_PASS",stage=stage,accountHttp=200,
                         aivenSelected=True,nativeRedisOK=True)
                    return True
                last="NATIVE_VALKEY_PROBE_FALSE"
        except Exception as exc:
            last=type(exc).__name__
        time.sleep(8)
    emit("SWRLZ_WEB_QUALITY_RUNTIME_NOT_READY",reasonType=last)
    return False

def main():
    publish=sys.argv[1:]==["publish"]
    if sys.argv[1:] not in ([],["preflight"],["publish"]):
        raise RuntimeError("USAGE preflight|publish")
    token=os.environ.get("HF_TOKEN","").strip()
    if not token:raise RuntimeError("HF_TOKEN_MISSING")
    api=HfApi(token=token)
    actual=api.repo_info(SPACE,repo_type="space").sha
    if actual!=EXPECTED_REV:
        emit("SWRLZ_WEB_QUALITY_SOURCE_DRIFT",expected=EXPECTED_REV,actual=actual,
             sourceModified=False)
        raise RuntimeError("LIVE_SPACE_REVISION_CHANGED_REFUSE_PATCH")
    selected=api.get_space_variables(SPACE).get("SWRLZ_REDIS_BACKEND")
    if (selected.get("value") if isinstance(selected,dict) else getattr(selected,"value",None))!="valkey":
        raise RuntimeError("DO_NOT_PATCH_UNEXPECTED_BACKEND")
    source=Path(hf_hub_download(SPACE,TARGET,repo_type="space",revision=actual,token=token)).read_bytes()
    patched=patch_coder(source)
    ast.parse(patched.decode("utf-8"))
    if patched.count(MARK.encode())<2 or source==patched:
        raise RuntimeError("INVALID_SCOPED_PATCH")
    BACKUP.mkdir(parents=True,exist_ok=True)
    (BACKUP/TARGET).write_bytes(source)
    (BACKUP/"manifest.json").write_text(json.dumps({
        "space":SPACE,"priorRevision":actual,"file":TARGET,
        "priorSHA256":hashlib.sha256(source).hexdigest(),
        "candidateSHA256":hashlib.sha256(patched).hexdigest(),
        "scope":APPROVAL,"accountDataRead":False,
        "redisConfigChanged":False
    },indent=2)+"\n")
    emit("SWRLZ_WEB_QUALITY_PREFLIGHT",sourceRevision=actual,
         file=TARGET,syntaxValidated=True,patchGuarded=True,
         modelWeightsChanged=False,redisBackendChanged=False)
    if not publish:return 0
    if os.environ.get("SWRLZ_WEB_QUALITY_APPROVAL")!=APPROVAL:
        raise RuntimeError("PUBLISH_SCOPE_MISMATCH")
    released=None
    try:
        commit=api.create_commit(repo_id=SPACE,repo_type="space",
          parent_commit=actual,
          operations=[CommitOperationAdd(path_in_repo=TARGET,path_or_fileobj=io.BytesIO(patched))],
          commit_message="Improve §C HTML page generation with functional responsive quality contract")
        released=commit.oid
        emit("SWRLZ_WEB_QUALITY_PUBLISHED",revision=released,sourceOnly=True)
        if not healthy(api):
            raise RuntimeError("LIVE_RUNTIME_FAILED_AFTER_PATCH")
        current=api.repo_info(SPACE,repo_type="space").sha
        if current!=released:raise RuntimeError("CONCURRENT_SOURCE_CHANGE")
        remote=Path(hf_hub_download(SPACE,TARGET,repo_type="space",
                                    revision=released,token=token)).read_bytes()
        if hashlib.sha256(remote).digest()!=hashlib.sha256(patched).digest():
            raise RuntimeError("REMOTE_SOURCE_MISMATCH")
        emit("SWRLZ_WEB_QUALITY_VERIFIED",revision=released,policyInstalled=True,
             nativeBackend="valkey",accountEndpoint=True,
             humanVisibleQualityNotYetTested=True)
        return 0
    except Exception as exc:
        emit("SWRLZ_WEB_QUALITY_ROLLBACK_START",reasonType=type(exc).__name__)
        if released and api.repo_info(SPACE,repo_type="space").sha==released:
            restored=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=released,
              operations=[CommitOperationAdd(path_in_repo=TARGET,
                                             path_or_fileobj=io.BytesIO(source))],
              commit_message="Restore prior §C webpage coding policy after failed verification")
            emit("SWRLZ_WEB_QUALITY_ROLLED_BACK",revision=restored.oid)
        raise

if __name__=="__main__":sys.exit(main())
