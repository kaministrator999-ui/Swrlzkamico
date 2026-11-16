#!/usr/bin/env python3
"""Source-pinned, non-deploying §C output-budget recovery candidate.

Patch only the common last-decode termination seam in current live engines.
No broad HF Space replacement and no model/context or code artifact changes.
This module deliberately does not publish: promotion must use the governed
existing-space release path after source and test reconciliation.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
from pathlib import Path

SPACE = "kamiloki/Swyrlz"
ENGINE_FILES = ("lfm2_700m_engine.py", "qwen_coder_engine.py")
OLD_TAIL = '''    if candidate_attempts and candidate_attempts[-1].get("finishReason")=="length":
        yield {"type":"FAILED","phase":"FAILED","reason":"OUTPUT_TOKEN_LIMIT","message":"The model reached its output limit before finishing; no complete artifact was accepted.","finishReason":"length"}
        return
'''
NEW_TAIL = '''    if candidate_attempts and candidate_attempts[-1].get("finishReason")=="length":
        # Non-code output caps are a paused delivery, not a failed request.
        # Do not bypass the accepted-code or source-edit validation gates.
        if not programming.get("codingTask") and not locals().get("source_change_mode"):
            if first_delta is None:
                # Buffered text is only revealed when its acceptance gate passed.
                # A rejected lyric/source candidate must never leak here.
                if candidate_check.get("status")=="PASS" and str(candidate_text or "").strip():
                    yield {"type":"DELTA","text":candidate_text}
                else:
                    yield {"type":"DELTA","text":"I reached the response limit before I could verify a complete answer. Please ask me to try the remaining part."}
            yield {"type":"CANDIDATE_VALIDATION","validation":{
                "status":"INCOMPLETE","reasons":["output-token-limit"],
                "verificationState":"UNVERIFIED_PARTIAL","accepted":False}}
            yield {"type":"STATUS","phase":"OUTPUT_LIMIT_PAUSED",
                   "reason":"The response reached a generation limit; existing visible text was retained. It may be incomplete."}
            yield {"type":"COMPLETED","phase":"PARTIAL","outputLimitReached":True}
            return
        yield {"type":"FAILED","phase":"FAILED","reason":"OUTPUT_TOKEN_LIMIT","message":"The model reached its output limit before finishing; no complete artifact was accepted.","finishReason":"length"}
        return
'''

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def patch_source(source: str, path: str = "<engine>") -> str:
    if source.count(OLD_TAIL) != 1:
        raise ValueError(f"UNSAFE_SOURCE_DRIFT {path}: termination anchor count={source.count(OLD_TAIL)}")
    if NEW_TAIL in source:
        raise ValueError(f"ALREADY_PATCHED {path}")
    edited = source.replace(OLD_TAIL, NEW_TAIL, 1)
    ast.parse(edited, filename=path)
    assert edited.count("UNVERIFIED_PARTIAL") == 1
    return edited

def inspect_live() -> None:
    from huggingface_hub import HfApi, hf_hub_download
    api = HfApi()
    revision = api.repo_info(SPACE, repo_type="space").sha
    if not revision or len(revision) != 40:
        raise RuntimeError("Live Hugging Face revision unavailable")
    print("NONCODE_LIMIT_PREFLIGHT revision=" + revision, flush=True)
    for name in ENGINE_FILES:
        source = Path(hf_hub_download(SPACE, name, revision=revision, repo_type="space")).read_text(encoding="utf-8")
        edited = patch_source(source, name)
        print("NONCODE_LIMIT_PREFLIGHT file=" + name
              + " before_sha256=" + sha256(source.encode("utf-8"))
              + " candidate_sha256=" + sha256(edited.encode("utf-8"))
              + " bytes=" + str(len(edited.encode("utf-8"))), flush=True)
    print("NONCODE_LIMIT_PREFLIGHT_OK deploy_inert=true", flush=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("preflight",), help="Read-only; never publishes.")
    args = parser.parse_args()
    if args.mode == "preflight":
        inspect_live()
