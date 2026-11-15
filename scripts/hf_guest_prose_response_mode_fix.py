#!/usr/bin/env python3
"""Guarded §C response-mode correction: respect explicit prose-only intent."""
import ast
import hashlib
import json
import os
import sys
from pathlib import Path
from huggingface_hub import HfApi,hf_hub_download,CommitOperationAdd

SPACE="kamiloki/Swyrlz"
FILE="qwen_coder_engine.py"
MARKER="swrlz-prose-only-response-mode-v1"
OLD='''def _response_mode(prompt, programming):
    original = _swrlz_before_quality_mode(prompt, programming)
    return original + _swrlz_html_guidance(prompt, programming)'''
NEW='''def _response_mode(prompt, programming):
    # swrlz-prose-only-response-mode-v1: current user output medium wins
    # over mentions of Python, JavaScript or a function in a prose request.
    if isinstance(programming, dict) and programming.get("source") == "prose-only-user-direction":
        return (
            "RESPONSE MODE: PROSE-ONLY EXPLANATION. The user explicitly asked "
            "for an explanation, not generated source. Respond directly in "
            "ordinary language. Do not output fenced code, executable code, "
            "function implementations or code examples. Preserve the topic "
            "and constraints. If the user later requests implementation, "
            "the normal coding route remains available."
        )
    original = _swrlz_before_quality_mode(prompt, programming)
    return original + _swrlz_html_guidance(prompt, programming)'''
OUT=Path("reports/chat-prose-response-mode")

def checksum(b):return hashlib.sha256(b).hexdigest()

def build(original):
    code=original.decode("utf-8")
    if MARKER in code:raise RuntimeError("Already patched; no duplicate")
    tree=ast.parse(code)
    candidates=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=="_response_mode"]
    wrappers=[n for n in candidates if " _swrlz_html_guidance(" in (ast.get_source_segment(code,n) or "")]
    if len(wrappers)!=1 or code.count(OLD)!=1:
        raise RuntimeError("Live response-mode wrapper changed; no blind patch")
    candidate=code.replace(OLD,NEW,1)
    compile(candidate,FILE,"exec")
    return candidate.encode("utf-8")

def test(candidate):
    tree=ast.parse(candidate.decode("utf-8"))
    target=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=="_response_mode" and n.lineno>320][-1]
    ns={"_swrlz_before_quality_mode":lambda p, programming:"CODE MODE",
        "_swrlz_html_guidance":lambda p, programming:" HTML MODE"}
    exec(compile(ast.Module(body=[target],type_ignores=[]),FILE,"exec"),ns)
    fn=ns["_response_mode"]
    a=fn("Explain Python fix; no code yet",{"codingTask":False,"source":"prose-only-user-direction"})
    if "PROSE-ONLY EXPLANATION" not in a or "CODE MODE" in a or "HTML MODE" in a:
        raise AssertionError("Prose route failed")
    b=fn("Write Python function",{"codingTask":True,"source":"brain-router"})
    if b!="CODE MODE HTML MODE":raise AssertionError("Coding route changed")
    c=fn("Hello",{"codingTask":False,"source":"brain-router"})
    if c!="CODE MODE HTML MODE":raise AssertionError("Existing default behavior changed")
    print("PROSE_RESPONSE_MODE_STATIC_ACCEPTED 3",flush=True)

def preflight(api):
    oldrev=api.repo_info(SPACE,repo_type="space").sha
    raw=Path(hf_hub_download(SPACE,FILE,repo_type="space",revision=oldrev,token=api.token)).read_bytes()
    patched=build(raw)
    test(patched)
    (OUT/"before").mkdir(parents=True,exist_ok=True)
    (OUT/"after").mkdir(parents=True,exist_ok=True)
    (OUT/"before"/FILE).write_bytes(raw)
    (OUT/"after"/FILE).write_bytes(patched)
    (OUT/"manifest.json").write_text(json.dumps({"Space":SPACE,"file":FILE,"beforeRevision":oldrev,
        "beforeSha":checksum(raw),"afterSha":checksum(patched)},indent=2)+"\n")
    print("PROSE_RESPONSE_MODE_PREFLIGHT",json.dumps({"revision":oldrev,"before":checksum(raw),
        "after":checksum(patched)}),flush=True)
    return oldrev,raw,patched

def publish(api):
    if os.environ.get("SWRLZ_PROSE_RESPONSE_APPROVED")!="1":raise RuntimeError("No explicit approval")
    if not api.token:raise RuntimeError("Existing HF_TOKEN missing")
    old,original,desired=preflight(api)
    if api.repo_info(SPACE,repo_type="space").sha!=old:raise RuntimeError("Concurrent Space change")
    newrev=None
    try:
        result=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=old,
            operations=[CommitOperationAdd(path_in_repo=FILE,path_or_fileobj=str(OUT/"after"/FILE))],
            commit_message="§C prose response mode: honor no-code explanation instruction")
        newrev=str(result.oid)
        readback=Path(hf_hub_download(SPACE,FILE,repo_type="space",revision=newrev,token=api.token)).read_bytes()
        if checksum(readback)!=checksum(desired):
            raise RuntimeError("Published source hash mismatch")
        print("PROSE_RESPONSE_MODE_PUBLISHED",json.dumps({"before":old,"after":newrev}),flush=True)
    except Exception:
        if newrev and api.repo_info(SPACE,repo_type="space").sha==newrev:
            rollback=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=newrev,
                operations=[CommitOperationAdd(path_in_repo=FILE,path_or_fileobj=str(OUT/"before"/FILE))],
                commit_message="Rollback §C prose response mode to exact prior source")
            print("PROSE_RESPONSE_MODE_ROLLED_BACK",rollback.oid,flush=True)
        raise

if __name__=="__main__":
    arg=sys.argv[1:] or ["preflight"]
    if arg not in (["preflight"],["publish"]):
        raise SystemExit("preflight|publish")
    api=HfApi(token=os.environ.get("HF_TOKEN") or None)
    if arg==["preflight"]:preflight(api)
    else:publish(api)
