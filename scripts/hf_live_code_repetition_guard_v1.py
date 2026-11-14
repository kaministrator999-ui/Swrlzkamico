#!/usr/bin/env python3
"""Guarded Hugging Face release: recover runaway repeated CSS during code generation.

The live Hugging Face Space is source of truth. A detached GitHub file is not
enough; this release patches and verifies the active coder and saves exact
rollback copies. Existing validated artifacts are never rewritten.
"""
from __future__ import annotations
import ast
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path
from huggingface_hub import HfApi, hf_hub_download, CommitOperationAdd

SPACE="kamiloki/Swyrlz"
BASE="https://kamiloki-swyrlz.hf.space"
SOURCE="qwen_coder_engine.py"
HELPER="code_runaway_guard_v1.py"
BACKUP=Path("hf-css-runaway-backup")
MARK="swrlz-code-runaway-recovery-v1"

def one(s, before, after, label):
    count=s.count(before)
    if count!=1:
        raise RuntimeError(f"LIVE_SOURCE_DRIFT {label}: count={count}")
    return s.replace(before,after,1)

def patch_coder(source):
    if MARK in source:
        raise RuntimeError("Coder already contains repetition guard")
    source=one(source,
        "    parts=[seed_text] if seed_text else []",
        '''    # swrlz-code-runaway-recovery-v1: clean only undeniable repeated
    # adjacent single-line CSS declarations from a saved unverified draft.
    from code_runaway_guard_v1 import collapse_repeated_css_rules
    if seed_text:
        seed_text, initial_cleanup=collapse_repeated_css_rules(seed_text)
        if initial_cleanup:
            yield {"type":"CANDIDATE_PREVIEW_RESET","attempt":attempt}
            yield {"type":"CANDIDATE_PREVIEW_DELTA","attempt":attempt,"text":seed_text}
            yield {"type":"STATUS","phase":"CODE_REPETITION_REMOVED",
                   "reason":"Removed redundant CSS from unverified saved draft; not compiled"}
    parts=[seed_text] if seed_text else []''',
        "recover saved source")
    source=one(source,
        "    next_messages=_swrlz_resume_tail_messages(seed_text) if seed_text else messages",
        '''    next_messages=_swrlz_resume_tail_messages(seed_text) if seed_text else messages
    if seed_text:
        next_messages[0]["content"]+=(
            " Do not repeat identical CSS declarations or selectors. "
            "Finish the outstanding page/script structures instead.")''',
        "prevent repeated CSS in resumed decode")
    source=one(source,
        '''            if addition:
                parts.append(addition)
                preview_buffer+=addition
                if len(preview_buffer)>=128''',
        '''            if addition:
                parts.append(addition)
                preview_buffer+=addition
                # Check only every 24 decoded deltas. Reset preview to the
                # corrected full candidate, then resume from its clean ending
                # at the next automatic checkpoint. Never mark it complete.
                if delta_chunks%24==0:
                    cleaned, evidence=collapse_repeated_css_rules("".join(parts))
                    if evidence:
                        parts=[cleaned]
                        preview_buffer=""
                        pending=""
                        part_observation["finishReason"]="length"
                        part_observation["repetitionRecovered"]=True
                        pause_at_budget=True
                        yield {"type":"CANDIDATE_PREVIEW_RESET","attempt":attempt}
                        yield {"type":"CANDIDATE_PREVIEW_DELTA","text":cleaned,"attempt":attempt}
                        yield {"type":"STATUS","phase":"CODE_REPETITION_RECOVERING",
                               "reason":"Detected repeated CSS; preserved distinct rules and will resume from cleaned source"}
                        break
                if len(preview_buffer)>=128''',
        "detect runaway in native token stream")
    source=one(source,
        '''            "Do not make new claims about execution or successful tests."''',
        '''            "Do not make new claims about execution or successful tests. "
            "Do not repeat CSS rules that are already present; finish missing functionality."''',
        "strengthen internal segment continuation")
    ast.parse(source,filename=SOURCE)
    return source

def sha(data):
    return hashlib.sha256(data).hexdigest()

def test_guard(helper):
    spec=importlib.util.spec_from_file_location("code_runaway_guard_v1",helper)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    f=module.collapse_repeated_css_rules
    rule=".viewport-canvas { width: 100%; height: 100%; }\n.viewport-canvas { display: block; }\n"
    prefix="<!DOCTYPE html>\n<style>\n.hero { color: white; }\n"
    suffix=".footer { margin: 0 }\n</style>"
    raw=prefix+rule*65+suffix
    cleaned,evidence=f(raw)
    assert evidence and evidence["removedRuleLines"]==128
    assert cleaned==prefix+rule+suffix
    small=prefix+rule*3+suffix
    assert f(small)==(small,None)
    different=".stage {border:1px solid #fff;}\n.panel {color:blue;}\n"
    assert f(different)==(different,None)
    print("RUNAWAY_GUARD_SOURCE_PRESERVATION_PASS",flush=True)

def test_decoder(source,helper):
    tree=ast.parse(source)
    fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef)
            and n.name=="_swrlz_code_candidate_preview")
    spec=importlib.util.spec_from_file_location("code_runaway_guard_v1",helper)
    module=importlib.util.module_from_spec(spec)
    sys.modules["code_runaway_guard_v1"]=module
    spec.loader.exec_module(module)
    class Fake:
        def create_chat_completion(self,**kwargs):
            part=".viewport-canvas { width: 100%; height: 100%; }\n.viewport-canvas { display: block; }\n"
            for _ in range(30):
                yield {"choices":[{"delta":{"content":part}}]}
    ns={
        "time":time,
        "_swrlz_resume_tail_messages":lambda x:[{"role":"system","content":"continue"}],
        "observe_completion_chunk":lambda obs,chunk:None,
        "CONTEXT_TOKENS":16384,
        "CONTEXT_SAFETY_TOKENS":512,
        "MIN_OUTPUT_TOKENS":128,
        "_token_count":lambda *args:100,
        "_swrlz_trim_code_resume":lambda prior,pending:pending,
    }
    exec(compile(ast.Module(body=[fn],type_ignores=[]),SOURCE,"exec"),ns)
    gen=ns["_swrlz_code_candidate_preview"](
        Fake(),[{"role":"user","content":"generate"}],4096,0.4,1,allow_continue=True)
    events=[]
    while True:
        try:events.append(next(gen))
        except StopIteration as stop:
            candidate,timing=stop.value
            break
    assert timing["finishReason"]=="length",timing
    assert timing["repetitionRecovered"] is True
    assert candidate.count(".viewport-canvas { width:")==1
    assert candidate.count(".viewport-canvas { display:")==1
    assert any(x.get("phase")=="CODE_REPETITION_RECOVERING" for x in events)
    assert any(x.get("type")=="CANDIDATE_PREVIEW_RESET" for x in events)
    print("RUNAWAY_NATIVE_STREAM_INTERRUPTION_PASS",len(events),flush=True)

def read_live(api):
    revision=api.repo_info(SPACE,repo_type="space").sha
    original=Path(hf_hub_download(
        SPACE,SOURCE,repo_type="space",revision=revision,token=api.token)).read_bytes()
    return revision,original

def preflight(api):
    rev,original=read_live(api)
    root=Path(__file__).resolve().parent
    helper=(root/"code_runaway_guard_v1.py")
    assert helper.exists()
    test_guard(helper)
    patched=patch_coder(original.decode("utf-8"))
    test_decoder(patched,helper)
    BACKUP.mkdir(parents=True,exist_ok=True)
    (BACKUP/SOURCE).write_bytes(original)
    (BACKUP/"revision.txt").write_text(rev)
    (BACKUP/"manifest.json").write_text(json.dumps({
        "revision":rev,"sourceShaBefore":sha(original),
        "sourceShaAfter":sha(patched.encode()),
        "helperSha":sha(helper.read_bytes()),
    },indent=2))
    print("CSS_RUNAWAY_PREFLIGHT_PASS",rev,flush=True)
    return rev

def publish(api,parent,content,helper,commit_message):
    if api.repo_info(SPACE,repo_type="space").sha != parent:
        raise RuntimeError("CONCURRENT_HF_SOURCE_CHANGE")
    with tempfile.TemporaryDirectory() as d:
        path=Path(d)/SOURCE
        path.write_bytes(content)
        update=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=parent,
            operations=[
                CommitOperationAdd(path_in_repo=SOURCE,path_or_fileobj=str(path)),
                CommitOperationAdd(path_in_repo=HELPER,path_or_fileobj=str(helper)),
            ],commit_message=commit_message)
    return str(update.oid)

def live_check():
    info=urllib.request.urlopen(BASE+"/api/hf/qwen35-ready",timeout=25)
    result=json.load(info)
    if result.get("model")!="qwen3.5-9b":raise RuntimeError("MODEL_ROUTE_CHANGED")
    # API route availability and code bytes are separate from integration:
    # after rebuild, confirm HF source revision and Space health.
    print("LIVE_MODEL_ROUTE_HEALTHY",flush=True)

def main():
    api=HfApi(token=os.environ.get("HF_TOKEN") or None)
    mode=sys.argv[1] if len(sys.argv)>1 else "preflight"
    if mode=="preflight":
        preflight(api)
        return
    if mode!="publish":raise SystemExit("preflight|publish")
    if os.environ.get("SWRLZ_CSS_RUNAWAY_APPROVED")!="1" or not api.token:
        raise RuntimeError("DEPLOY_APPROVAL_OR_TOKEN_MISSING")
    root=Path(__file__).resolve().parent
    helper=root/"code_runaway_guard_v1.py"
    parent=(BACKUP/"revision.txt").read_text().strip()
    before=(BACKUP/SOURCE).read_bytes()
    patched=patch_coder(before.decode()).encode()
    if api.repo_info(SPACE,repo_type="space").sha!=parent:
        raise RuntimeError("HF_SOURCE_CHANGED_AFTER_PREFLIGHT")
    deployed=None
    try:
        deployed=publish(api,parent,patched,helper,"§C: recover repeated CSS without rewriting prior code")
        for attempt in range(40):
            try:
                live_check()
                info=api.repo_info(SPACE,repo_type="space")
                if info.sha!=deployed:raise RuntimeError("LIVE_REVISION_MISMATCH")
                if getattr(info,"runtime",None) and getattr(info.runtime,"stage","") not in ("RUNNING","RUNNING_BUILDING"):
                    raise RuntimeError("SPACE_NOT_RUNNING")
                break
            except Exception:
                if attempt==39:raise
                time.sleep(8)
        print("LIVE_CSS_RUNAWAY_GUARD_DEPLOYED",deployed,flush=True)
    except Exception:
        if deployed and api.repo_info(SPACE,repo_type="space").sha==deployed:
            # Exact rollback to original source. Helper may remain inert, but
            # no runtime code imports it after rollback.
            restored=publish(api,deployed,before,helper,"Rollback §C CSS runaway guard to exact prior coder")
            print("LIVE_CSS_RUNAWAY_EXACT_CODER_ROLLBACK",restored,flush=True)
        raise

if __name__=="__main__":main()
