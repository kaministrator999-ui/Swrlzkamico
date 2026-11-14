"""Source-pinned, reversible production §C Redis egress and code completion optimization.

Modify only five existing files in the same HF Space; preserve Valkey secret,
encryption key, Google identity and model. No database deletion/migration.
"""
from __future__ import annotations
import ast
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

from huggingface_hub import HfApi, hf_hub_download, CommitOperationAdd

from hf_valkey_revision_sync_optimization import (
    patch_account, patch_station, patch_html as patch_sync_html
)
from hf_code_finish_and_preview_v1 import (
    patch_coder, patch_telemetry, patch_html as patch_draft_html
)

SPACE="kamiloki/Swyrlz"
EXPECTED_REV="ec81e1b0130d6d17313ba130582407064e276b96"
HF_APP="https://kamiloki-swyrlz.hf.space"
BACKUP=Path("swrlz-valkey-code-finish-exact-backup")
RECORD=Path("swrlz-valkey-code-finish-report.json")
TARGETS=("account_chat_store.py","station.py","qwen_coder_engine.py",
         "programming_telemetry.py","chat/§wyrlz/index.html")
APPROVED_SCOPE="redis-revision-code-fence-and-draft-presentation-only"

def emit(event,**fields):
    print(event+" "+json.dumps(fields,sort_keys=True,ensure_ascii=True),flush=True)

def ready(api,max_seconds=430):
    deadline=time.monotonic()+max_seconds
    last_type="Starting"
    while time.monotonic()<deadline:
        try:
            runtime=api.get_space_runtime(SPACE)
            if runtime.stage!="RUNNING":
                last_type="SpaceStage:"+str(runtime.stage)[:45]
                time.sleep(9)
                continue
            def get(path):
                request=urllib.request.Request(
                    HF_APP+path,headers={"User-Agent":"§C-Redis-Code-Optimization/1",
                                         "Accept":"application/json"})
                with urllib.request.urlopen(request,timeout=16) as response:
                    if response.status!=200:raise RuntimeError("HTTP_NOT_OK")
                    data=response.read(3500)
                    if len(data)>=3500:raise RuntimeError("UNBOUNDED_BODY")
                    return json.loads(data)
            account=get("/api/account/status")
            gateway=get("/api/storage/valkey-native-gateway-check")
            result={
                "stage":runtime.stage,
                "accountHTTP":200,
                "accountJSON":isinstance(account,dict),
                "backendSelected":gateway.get("backendSelected") is True,
                "nativeSETGET":gateway.get("nativeSETGET") is True,
                "nativeLua":gateway.get("nativeLua") is True,
                "liveMigrationPerformed":False
            }
            emit("SWRLZ_OPT_RUNTIME_ACCEPTANCE",**result)
            return (result["accountJSON"] and result["backendSelected"] and
                    result["nativeSETGET"] and result["nativeLua"])
        except Exception as exc:
            last_type=type(exc).__name__
            time.sleep(9)
    emit("SWRLZ_OPT_RUNTIME_UNAVAILABLE",lastType=last_type)
    return False

def verify_revision_first(edited):
    class HTTPException(Exception):
        def __init__(self,code,message):
            self.status_code=code
            super().__init__(message)
    account_source=edited["account_chat_store.py"].decode()
    station_source=edited["station.py"].decode()
    account_node=next(x for x in ast.parse(account_source).body
                      if isinstance(x,ast.FunctionDef) and x.name=="peek_chat_revision")
    class Redis:
        revision=4
        def _redis(self,c,*args):
            assert args[0]=="EVAL"
            return self.revision
    redis=Redis()
    account_ns={"_config":lambda:{"configured":True},"_chat_key":lambda o:"owned-key",
                "HTTPException":HTTPException,"gh":redis,"_CHAT_REVISION_LUA":"return 4"}
    exec(compile(ast.Module(body=[account_node],type_ignores=[]),
                 "<peek-chat-revision>","exec"),account_ns)
    assert account_ns["peek_chat_revision"]("google:synthetic")==4
    redis.revision=-2
    try:
        account_ns["peek_chat_revision"]("google:synthetic")
    except HTTPException as e:
        assert e.status_code==503
    else:raise AssertionError("Corrupt manifest accepted")

    refresh_node=next(x for x in ast.parse(station_source).body
                      if isinstance(x,ast.FunctionDef) and x.name=="_refresh_account_chat")
    class Store:
        remote=4
        peek_calls=0
        load_calls=0
        def peek_chat_revision(self,owner):
            self.peek_calls+=1
            return self.remote
        def load_chat(self,owner):
            self.load_calls+=1
            return {"revision":self.remote,"ownerGoogleId":owner,
                    "currentId":"","threads":[],"activeGeneration":None}
    store=Store()
    from types import SimpleNamespace
    env={"account_chat_store":store,"time":SimpleNamespace(monotonic=lambda:100),
         "HTTPException":HTTPException}
    exec(compile(ast.Module(body=[refresh_node],type_ignores=[]),
                 "<refresh-account-state>","exec"),env)
    fn=env["_refresh_account_chat"]
    session={"ownerGoogleId":"google:synthetic","revision":4,"currentId":"",
             "threads":[],"activeGeneration":None}
    assert fn(session) is False and store.peek_calls==1 and store.load_calls==0
    store.remote=5
    assert fn(session) is True and session["revision"]==5 and store.load_calls==1
    assert fn(session,force=True) is False and store.load_calls==2
    store.remote=4
    try:fn(session,force=False)
    except HTTPException as e:assert e.status_code==503
    else:raise AssertionError("Stale remote revision accepted")
    assert "not s.get(\"activeGeneration\")" in station_source
    assert "known.isdecimal()" in station_source

def verify_js(edited):
    html=edited["chat/§wyrlz/index.html"].decode("utf-8")
    scripts=[m.group(1) for m in re.finditer(r"(?is)<script\b[^>]*>(.*?)</script>",html)]
    targets=[s for s in scripts if "const syncStation" in s]
    if len(targets)!=1:raise RuntimeError("LIVE_CHAT_INLINE_JS_MISSING_OR_AMBIGUOUS")
    with tempfile.TemporaryDirectory() as root:
        path=Path(root)/"chat.js";path.write_text(targets[0],"utf-8")
        p=subprocess.run(["node","--check",str(path)],capture_output=True,text=True,timeout=12)
        if p.returncode!=0:
            raise RuntimeError("MODIFIED_BROWSER_SCRIPT_SYNTAX_FAILED")
    assert "stationProjectionOwnerEpoch!==accountProjectionEpoch" in html
    assert "ifRevision=" in html
    assert "draftDisplayed" in html and "draftFile" in html
    assert "const draftText=(savedDraft" in html

def build_patch(files):
    edited={}
    edited["account_chat_store.py"]=patch_account(files["account_chat_store.py"])
    edited["station.py"]=patch_station(files["station.py"])
    edited["qwen_coder_engine.py"]=patch_coder(files["qwen_coder_engine.py"])
    edited["programming_telemetry.py"]=patch_telemetry(files["programming_telemetry.py"])
    edited["chat/§wyrlz/index.html"]=patch_draft_html(
        patch_sync_html(files["chat/§wyrlz/index.html"]))
    for name,content in edited.items():
        if name.endswith(".py"):ast.parse(content.decode("utf-8"),filename=name)
        if content==files[name]:raise RuntimeError("PATCH_DID_NOT_CHANGE:"+name)
    verify_revision_first(edited)
    verify_js(edited)
    return edited

def main():
    publish=sys.argv[1:]==["publish"]
    if sys.argv[1:] not in ([],["preflight"],["publish"]):
        raise RuntimeError("USAGE: preflight|publish")
    token=os.environ.get("HF_TOKEN","").strip()
    if not token:raise RuntimeError("GITHUB_HF_TOKEN_NOT_CONFIGURED")
    api=HfApi(token=token)
    actual=api.repo_info(SPACE,repo_type="space").sha
    if actual!=EXPECTED_REV:
        emit("SWRLZ_OPT_SOURCE_DRIFT",currentRevision=actual,
             expectedRevision=EXPECTED_REV,mutation=False)
        raise RuntimeError("EXACT_LIVE_SOURCE_REVISION_CHANGED")
    variables=api.get_space_variables(SPACE)
    selected=variables.get("SWRLZ_REDIS_BACKEND")
    value=selected.get("value") if isinstance(selected,dict) else getattr(selected,"value",None)
    if value!="valkey":raise RuntimeError("VALKEY_BACKEND_NOT_SELECTED")
    secrets=set(api.get_space_secrets(SPACE))
    if "SWRLZ_VALKEY_URL" not in secrets or "SWRLZ_GITHUB_ENCRYPTION_KEY" not in secrets:
        raise RuntimeError("EXISTING_DATABASE_OR_ENCRYPTION_SECRET_MISSING")
    paths=set(api.list_repo_files(SPACE,repo_type="space",revision=actual))
    if not set(TARGETS).issubset(paths):raise RuntimeError("ACTIVE_SPACE_FILE_LAYOUT_CHANGED")
    originals={}
    for filename in TARGETS:
        originals[filename]=Path(hf_hub_download(
            SPACE,filename,repo_type="space",revision=actual,token=token)).read_bytes()
    patched=build_patch(originals)
    BACKUP.mkdir(parents=True,exist_ok=True)
    for name,raw in originals.items():
        path=BACKUP/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
    manifest={"target":SPACE,"priorRevision":actual,"files":TARGETS,
              "sourceDigests":{x:hashlib.sha256(y).hexdigest() for x,y in originals.items()},
              "candidateDigests":{x:hashlib.sha256(y).hexdigest() for x,y in patched.items()},
              "operation":"additive_source_update_no_secret_or_database_mutation"}
    (BACKUP/"manifest.json").write_text(json.dumps(manifest,indent=2,default=list)+"\n")
    emit("SWRLZ_OPT_PREFLIGHT",
         sourcePinned=True,changedFiles=list(TARGETS),
         pythonSyntaxPassed=True,jsSyntaxPassed=True,
         mockRedisRevisionTestsPassed=True,backendPreserved="valkey")
    if not publish:
        return 0
    if os.environ.get("SWRLZ_OPT_APPROVED_SCOPE")!=APPROVED_SCOPE:
        raise RuntimeError("OWNER_AUTHORIZATION_SCOPE_MISMATCH")
    # One source-pinned atomic Space commit, no model file or secret change.
    published=None
    try:
        commit=api.create_commit(
            repo_id=SPACE,repo_type="space",
            parent_commit=actual,
            operations=[CommitOperationAdd(path_in_repo=name,path_or_fileobj=io.BytesIO(patched[name]))
                        for name in TARGETS],
            commit_message="Reduce §C Redis egress and finalize complete HTML code drafts")
        published=commit.oid
        emit("SWRLZ_OPT_PUBLISHED",revision=published,backend="valkey",
             sourceOnly=True,oldSessionsDeleted=False)
        if not ready(api):
            raise RuntimeError("POST_DEPLOY_RUNTIME_ACCEPTANCE_FAILED")
        latest=api.repo_info(SPACE,repo_type="space").sha
        if latest!=published:raise RuntimeError("POST_DEPLOY_SOURCE_CHANGED")
        emit("SWRLZ_OPT_ACCEPTED",revision=latest,backend="valkey",
             regressionTests=True,accountHTTP=True,
             nativeRedisProbe=True,htmlFinishCodeDeployed=True,
             measuredBandwidthReduction=False)
        return 0
    except Exception as exc:
        emit("SWRLZ_OPT_ROLLBACK_START",causeType=type(exc).__name__,
             sourceRevision=published)
        if published:
            current=api.repo_info(SPACE,repo_type="space").sha
            if current==published:
                backup=api.create_commit(
                    repo_id=SPACE,repo_type="space",parent_commit=published,
                    operations=[CommitOperationAdd(path_in_repo=name,path_or_fileobj=io.BytesIO(originals[name]))
                                for name in TARGETS],
                    commit_message="Rollback failed §C Redis/code optimization to prior source")
                emit("SWRLZ_OPT_ROLLED_BACK",revision=backup.oid,
                     databaseBackendUnchanged=True,previousSourceRevision=actual)
            else:
                emit("SWRLZ_OPT_ROLLBACK_ABORT",reason="Space changed concurrently",
                     currentRevision=current)
        raise

if __name__=="__main__":
    sys.exit(main())
