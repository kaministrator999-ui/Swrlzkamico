#!/usr/bin/env python3
"""Guarded existing-Space source patch: §C lyric remixes, parody and remaster QA.

Change two current live Python sources and add one pure helper module.
No whole-Space upload, model/config/voice changes, or destructive resets.
"""
from __future__ import annotations
import argparse
import ast
import hashlib
import io
import json
import os
import re
from pathlib import Path

SPACE="kamiloki/Swyrlz"
ENGINE="lfm2_700m_engine.py"
STRUCTURE="music_structure.py"
HELPER="music_transform_quality.py"
BACKUP=Path("reports/swrlz-music-transform-v1")

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def once(source: str, old: str, new: str, label: str) -> str:
    count=source.count(old)
    if count != 1:
        raise ValueError(f"LIVE_SOURCE_DRIFT {label} expected 1 found {count}")
    return source.replace(old,new,1)

def patch_structure(source: str) -> str:
    if "swrlz-song-transformation-quality-v1" in source:
        raise ValueError("Already installed")
    source=once(source,
        "from typing import Any",
        "from typing import Any\nfrom music_transform_quality import transformation_contract, quality_review",
        "music quality import")
    # The original parser recognized 'those', but missed 'remix it' and
    # 'create a parody from it'. Resolve these ONLY when the user requests
    # a creative transformation and a prior verified song is in the thread.
    source=once(source,
        'r"(?i)\\b(?:those|these|earlier|previous|provided|above|reference|study|from\\s+that)\\b"',
        'r"(?i)\\b(?:those|these|earlier|previous|provided|above|reference|study|from\\s+that|from\\s+it|this|that|it)\\b"',
        "reference pointer")
    wrapper='''# swrlz-song-transformation-quality-v1: extend existing router, do not
# divert ordinary song lookups or music-analysis questions into generation.
_swrlz_prior_creative_transform_request=creative_music_transform_request
def creative_music_transform_request(prompt: str) -> bool:
    return (_swrlz_prior_creative_transform_request(prompt)
            or transformation_contract(prompt) is not None)


'''
    source=once(source,
        "def creative_music_request(prompt: str) -> dict[str,Any]:",
        wrapper+"def creative_music_request(prompt: str) -> dict[str,Any]:",
        "creative intent extension")
    func=next((node for node in ast.parse(source).body
               if isinstance(node,ast.FunctionDef) and node.name=="original_rap_violations"),None)
    if func is None:
        raise ValueError("Missing existing source borrowing guard")
    old=ast.get_source_segment(source,func)
    if not old:
        raise ValueError("Missing lyric guard source")
    review='''    # swrlz-song-transformation-quality-v1: source-safe structural checks.
    review=quality_review(delivered,allow_aab=False)
    faults.extend(x for x in review["reasons"] if x not in faults)
    return faults'''
    patched=once(old,"    return faults",review,"lyric quality gate")
    source=once(source,old,patched,"source borrowing gate extension")
    ast.parse(source,filename=STRUCTURE)
    return source

def patch_engine(source: str) -> str:
    if "swrlz-song-transformation-quality-v1" in source:
        raise ValueError("Already installed")
    imports=[line for line in source.splitlines()
             if line.startswith("from music_structure import ")]
    if len(imports)!=1:
        raise ValueError("Cannot find canonical music structure import")
    source=once(source,imports[0],imports[0]+
        "\nfrom music_transform_quality import transformation_contract, transformation_directive, quality_review, repair_directive",
        "music transform imports")
    old='''    music_policy="" if source_change_mode else music_model_policy(prompt)'''
    new='''    # swrlz-song-transformation-quality-v1: classify a genuine creative
    # operation separately from source lookup, analysis or coding.
    music_transform_contract=(transformation_contract(
        prompt,reference_available=bool(reference_structure))
        if not source_change_mode and not programming.get("codingTask") else None)
    music_policy="" if source_change_mode else music_model_policy(prompt)'''
    source=once(source,old,new,"music operation contract")
    source=once(source,
        "    native_evidence=payload.get(\"nativeEditorEvidence\")",
        "    if music_transform_contract:\n        system+=transformation_directive(music_transform_contract)\n    native_evidence=payload.get(\"nativeEditorEvidence\")",
        "operation guidance")
    old='''        elif reference_structure and not programming.get("codingTask"):
            # Complete-song work used the generic 768 token cap'''
    new='''        elif music_transform_contract:
            response_tokens=min(2048,available_output_tokens);temperature=0.42
        elif reference_structure and not programming.get("codingTask"):
            # Complete-song work used the generic 768 token cap'''
    source=once(source,old,new,"creative output budget")
    branch='''        elif longform_target:
            longform_result=complete_longform('''
    replacement='''        elif music_transform_contract and not programming.get("codingTask"):
            # swrlz-song-transformation-quality-v1: buffer all non-source music
            # transformations before emitting text. A rejected duplicate verse
            # must never be published then retracted from an SSE stream.
            lyric_mode=music_transform_contract["mode"]
            draft,timing=buffered_chat_completion(model,messages,response_tokens,temperature)
            candidate_text=original_rap_delivery(draft)
            candidate_check=quality_review(
                candidate_text,
                allow_aab=bool(re.search(r"(?i)\\b(?:aab|12[- ]bar blues)\\b",prompt)))
            first_fp=_candidate_fingerprint(candidate_text)
            candidate_attempts.append(candidate_attempt_receipt(
                1,"music-transform-"+lyric_mode,timing,candidate_check,first_fp))
            yield {"type":"CANDIDATE_ATTEMPT","attempt":candidate_attempts[-1]}
            if candidate_check["status"]!="PASS":
                regeneration_attempted=True
                regeneration_reason="music-structural-quality"
                retry_messages=list(messages)+[{"role":"system","content":
                    repair_directive(candidate_check["reasons"],lyric_mode)}]
                repaired,retry_timing=buffered_chat_completion(
                    model,retry_messages,response_tokens,min(0.52,temperature+0.07))
                candidate_text=original_rap_delivery(repaired)
                candidate_check=quality_review(
                    candidate_text,
                    allow_aab=bool(re.search(r"(?i)\\b(?:aab|12[- ]bar blues)\\b",prompt)))
                candidate_attempts.append(candidate_attempt_receipt(
                    2,"music-transform-repair",retry_timing,candidate_check,
                    _candidate_fingerprint(candidate_text),
                    previous_attempt_fingerprint=first_fp))
                yield {"type":"CANDIDATE_ATTEMPT","attempt":candidate_attempts[-1]}
            if candidate_check["status"]=="PASS":
                first_delta=round((time.perf_counter()-started)*1000,3)
                yield {"type":"DELTA","text":candidate_text}
            else:
                first_delta=round((time.perf_counter()-started)*1000,3)
                yield {"type":"DELTA","text":"I couldn't verify a distinct, complete lyrical transformation. I won't present duplicated verses as a finished song."}
        elif longform_target:
            longform_result=complete_longform('''
    source=once(source,branch,replacement,"transform quality generation branch")
    ast.parse(source,filename=ENGINE)
    return source

def candidate(live: dict[str,bytes]) -> dict[str,bytes]:
    helper=Path(__file__).with_name("music_transform_quality_v1.py").read_bytes()
    ast.parse(helper,filename=HELPER)
    return {
        ENGINE:patch_engine(live[ENGINE].decode("utf-8")).encode("utf-8"),
        STRUCTURE:patch_structure(live[STRUCTURE].decode("utf-8")).encode("utf-8"),
        HELPER:helper,
    }

def snapshot():
    from huggingface_hub import HfApi,hf_hub_download
    api=HfApi()
    rev=api.repo_info(SPACE,repo_type="space").sha
    if not re.fullmatch(r"[0-9a-f]{40}",str(rev or "")):
        raise ValueError("Live Space sha unavailable")
    before={}
    for f in (ENGINE,STRUCTURE):
        before[f]=Path(hf_hub_download(SPACE,f,repo_type="space",revision=rev)).read_bytes()
    # Avoid silently replacing a helper from another release line.
    info=api.list_repo_files(SPACE,repo_type="space",revision=rev)
    if HELPER in info:
        raise ValueError("Existing helper already deployed; reconcile instead of overwriting")
    modified=candidate(before)
    BACKUP.mkdir(parents=True,exist_ok=True)
    for name,data in before.items():
        (BACKUP / name).write_bytes(data)
    record={"schema":"swrlz-music-transformation-release-v1",
            "space":SPACE,"revision":rev,
            "before":{f:sha(v) for f,v in before.items()},
            "after":{f:sha(v) for f,v in modified.items()}}
    (BACKUP/"manifest.json").write_text(json.dumps(record,indent=2)+"\n")
    print("MUSIC_TRANSFORM_PREFLIGHT",json.dumps(record,sort_keys=True),flush=True)

def publish():
    from huggingface_hub import HfApi,CommitOperationAdd,hf_hub_download
    if os.getenv("SWRLZ_MUSIC_TRANSFORM_APPROVED")!="1":
        raise PermissionError("Missing governed user-approved release mode")
    token=os.getenv("HF_TOKEN")
    if not token:raise PermissionError("Missing guarded Hugging Face credential")
    record=json.loads((BACKUP/"manifest.json").read_text())
    api=HfApi(token=token)
    rev=record["revision"]
    if api.repo_info(SPACE,repo_type="space").sha!=rev:
        raise RuntimeError("SPACE_REVISION_MOVED: no deployment from stale snapshot")
    originals={}
    for name in (ENGINE,STRUCTURE):
        data=(BACKUP/name).read_bytes()
        if sha(data)!=record["before"][name]:
            raise RuntimeError("Snapshot hash mismatch "+name)
        actual=Path(hf_hub_download(SPACE,name,repo_type="space",revision=rev,token=token)).read_bytes()
        if data!=actual:raise RuntimeError("Live source and snapshot disagree "+name)
        originals[name]=data
    edits=candidate(originals)
    for f,data in edits.items():
        if sha(data)!=record["after"][f]:
            raise RuntimeError("Candidate has drifted "+f)
    operations=[CommitOperationAdd(path_in_repo=f,path_or_fileobj=io.BytesIO(data))
                for f,data in edits.items()]
    commit=api.create_commit(repo_id=SPACE,repo_type="space",
             operations=operations,parent_commit=rev,
             commit_message="feat(§C): original remixes, parodies and lyric remaster QA")
    newrev=getattr(commit,"oid",None) or api.repo_info(SPACE,repo_type="space").sha
    try:
        for f,data in edits.items():
            actual=Path(hf_hub_download(SPACE,f,repo_type="space",revision=newrev,token=token)).read_bytes()
            if actual!=data:raise RuntimeError("Published file content differs "+f)
    except Exception:
        if api.repo_info(SPACE,repo_type="space").sha==newrev:
            from huggingface_hub import CommitOperationDelete
            operations=[CommitOperationAdd(path_in_repo=f,path_or_fileobj=io.BytesIO(data))
                        for f,data in originals.items()]
            operations.append(CommitOperationDelete(path_in_repo=HELPER))
            api.create_commit(repo_id=SPACE,repo_type="space",operations=operations,
                              parent_commit=newrev,
                              commit_message="rollback(§C): restore exact music files after verification failure")
        raise
    print("MUSIC_TRANSFORM_PUBLISHED",json.dumps(
         {"before":rev,"after":newrev,"paths":list(edits),"verified":True}),flush=True)

if __name__=="__main__":
    cli=argparse.ArgumentParser()
    cli.add_argument("mode",choices=("snapshot","publish"))
    args=cli.parse_args()
    if args.mode=="snapshot":snapshot()
    else:publish()
