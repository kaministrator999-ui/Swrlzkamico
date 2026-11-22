#!/usr/bin/env python3
"""CAS-guarded, reversible §C Analyze Project progressive stream release.

Publishes ONLY model_router.py and a new read-only review module to the
existing kamiloki/Swyrlz Space. No changes to the engine, scenes, accounts,
OAuth, native write capabilities or model weights.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from urllib.request import urlopen

ROOT=Path(__file__).resolve().parents[1]
SPACE="kamiloki/Swyrlz"
BASE="e55aa8736a4929d3587652f9894b5d3fb6e2db01"
SOURCE_SHA={
    "model_router.py":"e60fd7f3fe250d053083552b4380eb4b70b8c58cff23064b55ebfa13f313be4a",
    "forge_workspace_insights_v1.py":"c068425b1c5152673814604f4614ecc2a396dba673e306a62fee30b8c57b8720",
}
NEW="forge_progressive_review_v1.py"
OUT=ROOT/"reports/forge-progressive-review-v1"
READY="https://kamiloki-swyrlz.hf.space/api/hf/qwen35-ready"
ANCHOR=(
    "            yield from generate_events(native_payload,forge_context,forge_embed.create_batch,forge_embed.wait_batch)\n"
    "            return"
)
REPLACE=(
    "            if (native_intent.get(\"disposition\") == \"read\" and not exact_approval\n"
    "                    and not native_preview):\n"
    "                # Native inspection is authenticated and read-only. Stream\n"
    "                # recorded facts first; Qwen then summarizes that evidence.\n"
    "                from forge_progressive_review_v1 import stream_insight\n"
    "                forge_embed.revalidate(forge_context, require_snapshot=True)\n"
    "                yield from stream_insight(forge_context.model_context(), command,\n"
    "                                          model_generate=large_generate,\n"
    "                                          source_payload=native_payload)\n"
    "            else:\n"
    "                yield from generate_events(native_payload,forge_context,forge_embed.create_batch,forge_embed.wait_batch)\n"
    "            return"
)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def prepare(download):
    before, after = OUT/"before", OUT/"after"
    for folder in (before,after): folder.mkdir(parents=True,exist_ok=True)
    for name, expected in SOURCE_SHA.items():
        data = download(name, BASE)
        if sha(data)!=expected:
            raise RuntimeError("Live §C source hash mismatch: "+name)
        for folder in (before,after):
            path=folder/name
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_bytes(data)
    raw=(before/"model_router.py").read_text("utf8")
    if raw.count(ANCHOR)!=1 or "forge_progressive_review_v1" in raw:
        raise RuntimeError("Native read route changed; aborting rather than guessing")
    rewritten=raw.replace(ANCHOR,REPLACE,1)
    (after/"model_router.py").write_text(rewritten,"utf8")
    data=(ROOT/"scripts/releases"/NEW).read_bytes()
    (after/NEW).write_bytes(data)
    for path in (after/"model_router.py",after/NEW):
        compile(path.read_bytes(),path.name,"exec")
    subprocess.run([sys.executable,str(ROOT/"tests/test_forge_progressive_review_v1.py"),
                    str(before),str(after)],check=True)
    digest={name:sha((after/name).read_bytes()) for name in ("model_router.py",NEW)}
    (OUT/"candidate.json").write_text(json.dumps({"base":BASE,"files":digest},indent=2)+"\n")
    print("FORGE_PROGRESSIVE_REVIEW_CANDIDATE",json.dumps(digest),flush=True)
    return before,after,digest


def wait_running(api, revision):
    consecutive=0
    for _ in range(60):
        if api.repo_info(SPACE,repo_type="space").sha != revision:
            raise RuntimeError("Live Space changed during the release")
        try:
            runtime=api.get_space_runtime(SPACE)
            ok=runtime.stage=="RUNNING" and runtime.raw.get("sha")==revision
            if ok:
                with urlopen(READY,timeout=15) as response:
                    ready=json.load(response)
                ok=ready.get("ready") is True and ready.get("model")=="qwen3.5-9b"
        except OSError:
            ok=False
        consecutive=consecutive+1 if ok else 0
        if consecutive>=2:return
        time.sleep(12)
    raise RuntimeError("Updated Chat runtime failed Qwen readiness verification")


def main():
    from huggingface_hub import HfApi,hf_hub_download,CommitOperationAdd,CommitOperationDelete
    parser=argparse.ArgumentParser()
    parser.add_argument("mode",choices=["inspect","publish"])
    args=parser.parse_args()
    token=os.environ.get("HF_TOKEN") or False
    api=HfApi(token=token)
    if api.repo_info(SPACE,repo_type="space").sha!=BASE:
        raise RuntimeError("Chat Space has advanced; rebase source and re-run inspection")
    if NEW in api.list_repo_files(SPACE,repo_type="space",revision=BASE):
        raise RuntimeError("Progressive review already exists; refusing replacement")
    def download(name,revision):
        return Path(hf_hub_download(SPACE,name,repo_type="space",revision=revision,token=token)).read_bytes()
    before,after,digest=prepare(download)
    if args.mode=="inspect":return
    if not token or os.environ.get("SWRLZ_FORGE_REVIEW_APPROVED")!="yes":
        raise RuntimeError("Explicit scoped deployment approval and HF_TOKEN required")
    result=api.create_commit(
        repo_id=SPACE,repo_type="space",parent_commit=BASE,
        commit_message="Stream verified §E project observations before natural Qwen synthesis",
        operations=[
            CommitOperationAdd(path_in_repo="model_router.py",path_or_fileobj=str(after/"model_router.py")),
            CommitOperationAdd(path_in_repo=NEW,path_or_fileobj=str(after/NEW)),
        ])
    revision=result.oid
    (OUT/"publication.json").write_text(json.dumps({"base":BASE,"revision":revision,"verified":False}))
    print("FORGE_PROGRESSIVE_REVIEW_PUBLISHED",revision,flush=True)
    try:
        for name, expected in digest.items():
            if sha(download(name,revision))!=expected:
                raise RuntimeError("Published source mismatched verified candidate: "+name)
        wait_running(api,revision)
    except Exception:
        if api.repo_info(SPACE,repo_type="space").sha==revision:
            rollback=api.create_commit(
                repo_id=SPACE,repo_type="space",parent_commit=revision,
                commit_message="Restore §C after progressive review readiness failure",
                operations=[
                    CommitOperationAdd(path_in_repo="model_router.py",path_or_fileobj=str(before/"model_router.py")),
                    CommitOperationDelete(path_in_repo=NEW),
                ]).oid
            print("FORGE_PROGRESSIVE_REVIEW_ROLLBACK",rollback,flush=True)
        raise
    (OUT/"publication.json").write_text(json.dumps({"base":BASE,"revision":revision,"verified":True}))
    print("FORGE_PROGRESSIVE_REVIEW_LIVE",revision,flush=True)


if __name__=="__main__":
    main()
