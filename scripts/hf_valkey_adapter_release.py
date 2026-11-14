"""Publish source-pinned dormant adapter into live HF Redis gateway, with backup."""
from __future__ import annotations
import ast, hashlib, io, json, os
from pathlib import Path
from huggingface_hub import HfApi, hf_hub_download, CommitOperationAdd
from hf_valkey_live_adapter_prepare import (
    SPACE, BASE_REV, TARGET, ANCHOR, MARKER, PATCH
)
OUT=Path("valkey-real-gateway-backup")

def main():
    token=os.environ.get("HF_TOKEN","").strip()
    if not token: raise RuntimeError("HF_TOKEN_NOT_AVAILABLE")
    api=HfApi(token=token)
    latest=api.repo_info(SPACE,repo_type="space").sha
    if latest != BASE_REV:
        raise RuntimeError("SPACE_REVISION_CHANGED_ABORT")
    if "SWRLZ_REDIS_BACKEND" in api.get_space_secrets(SPACE):
        raise RuntimeError("BACKEND_SWITCH_SECRET_PRESENT_REFUSE")
    variables=api.get_space_variables(SPACE)
    if "SWRLZ_REDIS_BACKEND" in variables:
        raise RuntimeError("BACKEND_SWITCH_VARIABLE_PRESENT_REFUSE")
    previous=Path(hf_hub_download(SPACE,TARGET,repo_type="space",revision=latest,token=token)).read_bytes()
    old=previous.decode("utf-8")
    if hashlib.sha256(previous).hexdigest()!="be1de67b4cb9761e4c4ca7f4ff9b29b60c7e47ecf7e016ecd30ee78a201a6cd8":
        raise RuntimeError("SOURCE_DIGEST_MISMATCH")
    if old.count(ANCHOR)!=1 or MARKER in old:
        raise RuntimeError("REDIS_GATEWAY_NOT_UNIQUE")
    new=old.replace(ANCHOR,PATCH,1)
    ast.parse(new)
    assert new.replace(PATCH,ANCHOR,1)==old
    OUT.mkdir(exist_ok=True)
    (OUT/TARGET).write_bytes(previous)
    (OUT/"manifest.json").write_text(json.dumps({"space":SPACE,"revision":latest,
        "file":TARGET,"sourceSha256":hashlib.sha256(previous).hexdigest(),
        "activeBackend":"upstash","candidateDoesNotSwitch":True},indent=2))
    print("SWRLZ_DORMANT_ADAPTER_PREPARED "+json.dumps({
        "space":SPACE,"revision":latest,"compiled":True,"upstashStillDefault":True}))
    if os.environ.get("SWRLZ_DEPLOY_DORMANT_VALKEY","")=="1":
        result=api.create_commit(repo_id=SPACE,repo_type="space",
           operations=[CommitOperationAdd(path_in_repo=TARGET,path_or_fileobj=io.BytesIO(new.encode("utf-8")))],
           commit_message="Install opt-in native Valkey gateway; retain Upstash default",
           parent_commit=latest)
        print("SWRLZ_DORMANT_ADAPTER_PUBLISHED "+json.dumps({
            "space":SPACE,"revision":result.oid,"upstashStillDefault":True,"keysCopied":False}))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
