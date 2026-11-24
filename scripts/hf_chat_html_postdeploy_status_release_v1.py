#!/usr/bin/env python3
"""Scoped post-approval live-source verification release for existing §C Space."""
from __future__ import annotations

import argparse
import ast
import hashlib
import io
import os
import subprocess
import tempfile
import time
import urllib.request
from pathlib import Path

SPACE="kamiloki/Swyrlz"
BASE="https://kamiloki-swyrlz.hf.space"
API="github_html_publish_action_v1.py"
ASSET="chat/§wyrlz/assets/html-project-publish-review-v1.js"
CHAT="chat/§wyrlz/index.html"
SOURCES={API:Path("api/github_html_publish_action_v1.py"),
         ASSET:Path("chat/html-project-publish-review-v1.js")}
FROM="/chat/§wyrlz/assets/html-project-publish-review-v1.js?v=2"
TO="/chat/§wyrlz/assets/html-project-publish-review-v1.js?v=3"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def selftest():
    source=SOURCES[API].read_bytes()
    ast.parse(source.decode(),filename=API)
    if b"indexGitBlobSha" not in source:
        raise RuntimeError("Publisher preview omits immutable index Git blob identity")
    asset=SOURCES[ASSET].read_bytes()
    if b"gitBlobObjectId" not in asset or b"verifyPublishedSource" not in asset:
        raise RuntimeError("Automatic source verification UI missing")
    with tempfile.TemporaryDirectory(prefix="html-publish-status-") as d:
        path=Path(d)/"status.js";path.write_bytes(asset)
        result=subprocess.run(["node","--check",str(path)],
                              capture_output=True,text=True,timeout=25)
        if result.returncode:raise RuntimeError("JS syntax failed: "+result.stderr[:600])
    print("HTML_POSTDEPLOY_VERIFY_SELFTEST_PASS",sha(source),sha(asset),flush=True)


def health():
    with urllib.request.urlopen(BASE+"/chat/%C2%A7wyrlz?__html_status_probe=3",timeout=20) as response:
        html=response.read(2_000_000).decode("utf-8",errors="replace")
        if response.status!=200 or TO not in html:
            raise RuntimeError("§C chat status-verification asset revision not live")
    with urllib.request.urlopen(BASE+"/chat/%C2%A7wyrlz/assets/html-project-publish-review-v1.js?v=3",timeout=20) as response:
        js=response.read(200_000).decode("utf-8",errors="replace")
        if response.status!=200 or "verifyPublishedSource" not in js or "gitBlobObjectId" not in js:
            raise RuntimeError("§C live status verification JS not served")
    print("HTML_POSTDEPLOY_VERIFY_LIVE_CONFIRMED",flush=True)


def main(mode):
    selftest()
    if mode=="selftest":return
    from huggingface_hub import HfApi,hf_hub_download,CommitOperationAdd
    token=os.getenv("HF_TOKEN") or None
    api=HfApi(token=token)
    current=str(api.repo_info(SPACE,repo_type="space").sha)
    original={p:Path(hf_hub_download(SPACE,p,repo_type="space",
                  revision=current,token=token)).read_bytes() for p in (API,ASSET,CHAT)}
    if b"indexGitBlobSha" in original[API] or b"verifyPublishedSource" in original[ASSET]:
        raise RuntimeError("Already applied or concurrent release; inspect live source before updating")
    if b"swrlz-owner-html-publish-v1" not in original[API]:
        # The marker lives in the actions handler, not in the publishing helper.
        if b"Owner-authenticated, commit-pinned" not in original[API]:
            raise RuntimeError("Existing publisher helper source changed")
    page=original[CHAT].decode("utf-8")
    if page.count(FROM)!=1:
        raise RuntimeError("Chat asset version drift")
    updated={API:SOURCES[API].read_bytes(),ASSET:SOURCES[ASSET].read_bytes(),
             CHAT:page.replace(FROM,TO,1).encode("utf-8")}
    print("HTML_POSTDEPLOY_VERIFY_PREFLIGHT",current,
          {p:sha(blob) for p,blob in updated.items()},flush=True)
    if mode=="preflight":return
    if mode!="publish" or not token or os.getenv("SWRLZ_HTML_POSTDEPLOY_APPROVED")!="1":
        raise PermissionError("Owner-scoped release approval and HF_TOKEN required")
    if str(api.repo_info(SPACE,repo_type="space").sha)!=current:
        raise RuntimeError("Concurrent Hugging Face update refused")
    revision=api.create_commit(
        repo_id=SPACE,repo_type="space",parent_commit=current,
        operations=[CommitOperationAdd(path_in_repo=p,path_or_fileobj=io.BytesIO(blob))
                    for p,blob in updated.items()],
        commit_message="feat(§C): auto-verify approved HTML publication against GitHub blob"
    ).oid
    print("HTML_POSTDEPLOY_VERIFY_SOURCE_COMMITTED",revision,flush=True)
    try:
        for p,blob in updated.items():
            actual=Path(hf_hub_download(SPACE,p,repo_type="space",
                 revision=revision,token=token)).read_bytes()
            if actual!=blob:raise RuntimeError("HF committed source mismatch: "+p)
        for n in range(36):
            try:
                health()
                print("HTML_POSTDEPLOY_VERIFY_RELEASE_SUCCESS",revision,flush=True)
                return
            except (OSError,RuntimeError,TimeoutError) as exc:
                if n==35:raise RuntimeError("Published revision never became live") from exc
                time.sleep(10)
    except Exception:
        if str(api.repo_info(SPACE,repo_type="space").sha)==revision:
            restored=api.create_commit(
                repo_id=SPACE,repo_type="space",parent_commit=revision,
                operations=[CommitOperationAdd(path_in_repo=p,path_or_fileobj=io.BytesIO(blob))
                            for p,blob in original.items()],
                commit_message="rollback(§C): unverified HTML deployment status UI"
            )
            print("HTML_POSTDEPLOY_VERIFY_ROLLBACK",restored.oid,flush=True)
        else:
            print("HTML_POSTDEPLOY_VERIFY_ROLLBACK_BLOCKED_BY_CONCURRENT_UPDATE",flush=True)
        raise


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("mode",choices=("selftest","preflight","publish"))
    main(parser.parse_args().mode)
