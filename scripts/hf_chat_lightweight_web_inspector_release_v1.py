#!/usr/bin/env python3
"""CAS-protected §C in-chat browser-free project diagnosis release.

Only updates existing HTML context helper and adds a bounded inspector helper
to the same Hugging Face Space. No Station/engine/auth/project writes.
"""
from __future__ import annotations
import argparse
import ast
import hashlib
import io
import os
import time
import urllib.request
from pathlib import Path

SPACE = "kamiloki/Swyrlz"
BASE = "https://kamiloki-swyrlz.hf.space"
FILES = {
    "html_project_context_v1.py": Path("api/html_project_context_v1.py"),
    "lightweight_webpage_inspector_v1.py": Path("api/lightweight_webpage_inspector_v1.py"),
}

def checksum(v):
    return hashlib.sha256(v).hexdigest()

def candidate():
    result = {name: path.read_bytes() for name, path in FILES.items()}
    for name, raw in result.items():
        ast.parse(raw.decode("utf-8"), filename=name)
    evidence = result["html_project_context_v1.py"].decode("utf-8")
    if ("inspect_files(source_files, known_files_complete=False)" not in evidence
            or "inspect_published(project" not in evidence):
        raise RuntimeError("INTEGRATION_TO_OWNER_PROJECT_CONTEXT_MISSING")
    return result

def selftest():
    data = candidate()
    assert b"def inspect_files(" in data["lightweight_webpage_inspector_v1.py"]
    assert b"functionalVerified" in data["lightweight_webpage_inspector_v1.py"]
    print("LIGHTWEIGHT_WEB_RELEASE_SELFTEST_PASS", flush=True)

def health():
    req=urllib.request.Request(BASE+"/chat/%C2%A7wyrlz?__lightweb=1",headers={"Cache-Control":"no-cache"})
    with urllib.request.urlopen(req, timeout=20) as result:
        if result.status != 200 or "text/html" not in result.headers.get("Content-Type", ""):
            raise RuntimeError("CHAT_HEALTH_UNVERIFIED")
        result.read(500)

def main(mode):
    selftest()
    if mode == "selftest":
        return
    from huggingface_hub import HfApi, hf_hub_download, CommitOperationAdd, CommitOperationDelete
    token=os.environ.get("HF_TOKEN") or None
    api=HfApi(token=token)
    revision=str(api.repo_info(SPACE,repo_type="space").sha)
    existing=set(api.list_repo_files(SPACE,repo_type="space",revision=revision))
    if "lightweight_webpage_inspector_v1.py" in existing:
        raise RuntimeError("LIGHTWEIGHT_HELPER_EXISTS_RECONCILE_BEFORE_REPLACE")
    previous=Path(hf_hub_download(SPACE,"html_project_context_v1.py",
                                  repo_type="space",revision=revision,token=token)).read_bytes()
    if b"VERIFIED OWNER GITHUB HTML PROJECT SOURCE" not in previous:
        raise RuntimeError("LIVE_CONTEXT_SOURCE_DRIFT")
    updated=candidate()
    print("LIGHTWEIGHT_WEB_SOURCE_PREFLIGHT",revision,
          {k:checksum(v) for k,v in updated.items()},flush=True)
    if mode=="preflight":
        return
    if mode!="publish" or not token or os.environ.get("SWRLZ_LIGHTWEB_DEPLOY_APPROVED")!="1":
        raise PermissionError("EXPLICIT_SCOPED_RELEASE_AUTHORIZATION_REQUIRED")
    if str(api.repo_info(SPACE,repo_type="space").sha)!=revision:
        raise RuntimeError("CONCURRENT_HF_REVISION_CHANGE")
    new=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=revision,
        operations=[CommitOperationAdd(path_in_repo=p,path_or_fileobj=io.BytesIO(v))
                    for p,v in updated.items()],
        commit_message="feat(§C): inspect owner web projects without a browser").oid
    print("LIGHTWEIGHT_WEB_HF_COMMITTED",new,flush=True)
    try:
        for p,v in updated.items():
            remote=Path(hf_hub_download(SPACE,p,repo_type="space",
                        revision=new,token=token)).read_bytes()
            if remote!=v:
                raise RuntimeError("PUBLISHED_HELPER_SOURCE_MISMATCH:"+p)
        for attempt in range(24):
            try:
                health()
                print("LIGHTWEIGHT_WEB_HF_HEALTH_AND_BYTES_VERIFIED",new,flush=True)
                return
            except (OSError,RuntimeError,TimeoutError) as exc:
                if attempt==23:
                    raise RuntimeError("CHAT_HEALTH_NOT_VERIFIED") from exc
                time.sleep(10)
    except Exception:
        if str(api.repo_info(SPACE,repo_type="space").sha)==new:
            rolled=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=new,
                operations=[
                    CommitOperationAdd(path_in_repo="html_project_context_v1.py",
                                       path_or_fileobj=io.BytesIO(previous)),
                    CommitOperationDelete(path_in_repo="lightweight_webpage_inspector_v1.py")],
                commit_message="rollback(§C): browser-free inspector verification failed")
            print("LIGHTWEIGHT_WEB_HF_ROLLED_BACK",rolled.oid,flush=True)
        raise

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("mode",choices=["selftest","preflight","publish"])
    main(ap.parse_args().mode)
