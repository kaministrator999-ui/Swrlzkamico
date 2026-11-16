#!/usr/bin/env python3
"""Guarded exact-HF-Space patch for bounded §C tool-capability recovery.

Runs only via the existing canonical Hugging Face request -> manual workflow.
Never overwrites a diverged live source, model weights, auth, user data, or §E.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import io
import json
import os
from pathlib import Path

SPACE = "kamiloki/Swyrlz"
ENGINE = "lfm2_700m_engine.py"
HELPER = "api/tool_capability_recovery_v1.py"
FILES = (ENGINE,)
ROOT = Path("reports/swrlz-tool-capability-recovery-v1")
MARK = "swrlz-runtime-tool-capability-recovery-v1"
ANCHOR = '''def generate_events(payload):
    if not isinstance(payload,dict) or payload.get("githubSourceChangeTask"):
        yield from _swrlz_prior_generate_events_prose_v1(payload)
        return'''
REPLACEMENT = '''def generate_events(payload):
    # swrlz-runtime-tool-capability-recovery-v1: server capabilities win over
    # pretrained model self-descriptions. One task-aware retry, no new state owner.
    if (isinstance(payload,dict) and not payload.get("_toolRecoveryPass")
            and os.environ.get("SWRLZ_TOOL_CAPABILITY_RECOVERY_ENABLED","1").strip().lower()
                not in ("0","false","off")):
        from api.tool_capability_recovery_v1 import (
            relevant as _swrlz_tool_recovery_relevant,
            run as _swrlz_run_tool_recovery,
        )
        if _swrlz_tool_recovery_relevant(payload):
            from api.online_research import research as _swrlz_public_research
            from stop_transport import generation_cancelled as _swrlz_recovery_cancelled
            def _swrlz_recovery_search(query):
                return _swrlz_public_research({
                    "prompt":query,"researchQueries":[query],
                })
            yield from _swrlz_run_tool_recovery(
                payload,
                lambda candidate: generate_events({
                    **candidate,"_toolRecoveryPass":True,
                }),
                _swrlz_recovery_search,
                _swrlz_recovery_cancelled,
            )
            return
    if not isinstance(payload,dict) or payload.get("githubSourceChangeTask"):
        yield from _swrlz_prior_generate_events_prose_v1(payload)
        return'''


def checksum(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def patch_engine(text: str) -> str:
    if MARK in text:
        raise RuntimeError("TOOL_RECOVERY_ALREADY_PRESENT")
    if text.count(ANCHOR) != 1:
        raise RuntimeError("TOOL_RECOVERY_SOURCE_DRIFT: outermost engine hook")
    changed = text.replace(ANCHOR, REPLACEMENT, 1)
    ast.parse(changed, filename=ENGINE)
    assert changed.count(MARK) == 1
    assert changed.count("_swrlz_prior_generate_events_prose_v1(payload)") >= 1
    return changed


def build(before: dict[str, bytes]) -> dict[str, bytes]:
    helper = Path(HELPER).read_bytes()
    ast.parse(helper.decode("utf-8"), filename=HELPER)
    return {ENGINE: patch_engine(before[ENGINE].decode("utf-8")).encode("utf-8"),
            HELPER: helper}


def stage(*, snapshot: bool = True, token: str | None = None):
    from huggingface_hub import HfApi, hf_hub_download
    api = HfApi(token=token)
    rev = str(api.repo_info(SPACE, repo_type="space").sha)
    if len(rev) != 40:
        raise RuntimeError("EXACT_SPACE_REVISION_UNAVAILABLE")
    paths = set(api.list_repo_files(SPACE, repo_type="space", revision=rev))
    if HELPER in paths:
        raise RuntimeError("TOOL_RECOVERY_HELPER_ALREADY_ON_SPACE")
    previous = {
        ENGINE: Path(hf_hub_download(SPACE,ENGINE,repo_type="space",
                                     revision=rev,token=token)).read_bytes()}
    candidate = build(previous)
    manifest = {
        "contract":MARK, "space":SPACE, "revision":rev,
        "before":{name:checksum(data) for name,data in previous.items()},
        "after":{name:checksum(data) for name,data in candidate.items()},
        "paths":list(candidate),
        "modelWeightsChanged":False, "authChanged":False,
    }
    if snapshot:
        (ROOT/"before").mkdir(parents=True,exist_ok=True)
        (ROOT/"candidate"/"api").mkdir(parents=True,exist_ok=True)
        for name,data in previous.items():
            (ROOT/"before"/name).write_bytes(data)
        for name,data in candidate.items():
            (ROOT/"candidate"/name).write_bytes(data)
        (ROOT/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print("TOOL_RECOVERY_PREFLIGHT "+json.dumps(manifest,sort_keys=True),flush=True)
    return manifest,previous,candidate


def publish():
    from huggingface_hub import HfApi,hf_hub_download,CommitOperationAdd,CommitOperationDelete
    if os.environ.get("SWRLZ_TOOL_RECOVERY_DEPLOY_APPROVED")!="1":
        raise PermissionError("CANONICAL_DEPLOY_APPROVAL_REQUIRED")
    token = os.environ.get("HF_TOKEN")
    if not token:
        raise PermissionError("HF_TOKEN_MISSING")
    stored = json.loads((ROOT/"manifest.json").read_text())
    api = HfApi(token=token)
    if str(api.repo_info(SPACE,repo_type="space").sha)!=stored["revision"]:
        raise RuntimeError("CONCURRENT_SPACE_REVISION_CHANGED")
    live = Path(hf_hub_download(SPACE,ENGINE,repo_type="space",
                                revision=stored["revision"],token=token)).read_bytes()
    if checksum(live)!=stored["before"][ENGINE]:
        raise RuntimeError("LIVE_ENGINE_BYTES_CHANGED")
    previous={ENGINE:live}
    candidate=build(previous)
    if {name:checksum(b) for name,b in candidate.items()}!=stored["after"]:
        raise RuntimeError("PREFLIGHT_CANDIDATE_CHANGED")
    rev=None
    try:
        commit=api.create_commit(
            repo_id=SPACE,repo_type="space",parent_commit=stored["revision"],
            operations=[CommitOperationAdd(path_in_repo=name,path_or_fileobj=io.BytesIO(b))
                        for name,b in candidate.items()],
            commit_message="feat(§C): bounded research capability recovery and accepted-offer continuation")
        rev=str(commit.oid)
        for name,b in candidate.items():
            actual=Path(hf_hub_download(SPACE,name,repo_type="space",
                         revision=rev,token=token)).read_bytes()
            if actual!=b:raise RuntimeError("SPACE_READBACK_MISMATCH:"+name)
        print("TOOL_RECOVERY_PUBLISHED "+json.dumps({"previous":stored["revision"],
              "revision":rev,"paths":list(candidate),"byteExact":True}),flush=True)
    except Exception:
        # Roll back only this exact revision. Never overwrite unrelated changes.
        if rev and str(api.repo_info(SPACE,repo_type="space").sha)==rev:
            inverse=[CommitOperationAdd(path_in_repo=ENGINE,
                                        path_or_fileobj=io.BytesIO(live)),
                     CommitOperationDelete(path_in_repo=HELPER)]
            reverted=api.create_commit(
                repo_id=SPACE,repo_type="space",parent_commit=rev,
                operations=inverse,commit_message="rollback(§C): tool capability readback failed")
            print("TOOL_RECOVERY_ROLLBACK "+str(reverted.oid),flush=True)
        raise


if __name__=="__main__":
    cli=argparse.ArgumentParser()
    cli.add_argument("mode",choices=("preflight","snapshot","publish"))
    args=cli.parse_args()
    if args.mode=="publish":publish()
    else:stage(snapshot=args.mode=="snapshot")
