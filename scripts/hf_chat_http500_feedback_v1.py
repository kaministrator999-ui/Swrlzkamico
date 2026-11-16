#!/usr/bin/env python3
"""Minimal exact-live §C HTTP500 retry and music-feedback intent repair.

Only the verified running Space, immutable parent revision and four narrowly
specified files can be changed; no full Space rebuild, model reload or auth edits.
"""
from __future__ import annotations
import ast
import hashlib
import io
import json
import os
from pathlib import Path

SPACE="kamiloki/Swyrlz"
MUSIC="music_transform_quality.py"
ENGINE="lfm2_700m_engine.py"
NATIVE="qwen35_single_runtime.py"
STATION="station.py"
HELPER="qwen_http500_recovery.py"
FILES=(MUSIC,ENGINE,NATIVE,STATION)
BACKUP=Path("reports/swrlz-http500-feedback-v1")

def once(source,old,new,label):
    count=source.count(old)
    if count!=1:
        raise ValueError(f"UNSAFE_LIVE_SOURCE_DRIFT {label}: expected 1, got {count}")
    return source.replace(old,new,1)

def sha(blob):
    return hashlib.sha256(blob).hexdigest()

def patch_music(source):
    if "swrlz-song-feedback-intent-guard-v1" in source:
        raise ValueError("Feedback guard already installed")
    anchor="def transformation_contract(prompt: str, *, reference_available: bool = False) -> dict | None:"
    new='''# swrlz-song-feedback-intent-guard-v1: a noun is not a command.
# "My remix has issues" is feedback. "Please remix my song" requests work.
def _new_creative_command(prompt: str) -> bool:
    text=" ".join(str(prompt or "").split()).strip()
    direct=re.search(
        r"(?i)^\\s*(?:(?:hey|so|now|please)\\b[\\s,]*)*"
        r"(?:(?:can|could|would|will)\\s+(?:you|we)\\s+(?:please\\s+)?"
        r"|(?:let's|let us|go ahead and|try to)\\s+)?"
        r"(?:remix|re[- ]?mix|remaster|parody|rewrite|rework|reimagine|"
        r"adapt|flip|make|create|write|compose|craft|produce|generate|"
        r"redo|revise|fix|improve|change|turn|blend|give|do|arrange)\\b",text)
    if direct:
        return True
    desired=re.search(
        r"(?i)\\b(?:i(?:'d| would)\\s+like|i\\s+(?:want|need)|"
        r"we\\s+(?:want|need))\\s+(?:(?:you|us)\\s+to\\s+)?"
        r"(?:(?:make|write|create|compose|remix|remaster|parody|rewrite|"
        r"adapt|reimagine|redo|fix|improve|try)\\b|(?:a|an)\\s+"
        r"(?:(?:new|original|different|better)\\s+)?"
        r"(?:remix|parody|remaster|mash[ -]?up|cover|adaptation)\\b)",text)
    if desired:
        return True
    # A correction may contain an explicit request after describing problems.
    if re.search(r"(?i)\\b(?:please|can\\s+you|could\\s+you|would\\s+you)"
                 r"\\s+(?:fix|redo|rewrite|remix|remaster|rework|"
                 r"revise|improve|make|create)\\b",text):
        return True
    return False


'''
    source=once(source,anchor,new+anchor,"new creative intent helper")
    old='''    kind,hit=match
    # Music terms are required except when the current thread has a documented'''
    replacement='''    kind,hit=match
    # An explicit critique is discussion even if it contains "remix" or "parody".
    if not _new_creative_command(text):
        return None
    # Music terms are required except when the current thread has a documented'''
    source=once(source,old,replacement,"intent gate")
    ast.parse(source,filename=MUSIC)
    return source

def patch_engine(source):
    if "swrlz-music-feedback-reply-v1" in source:
        raise ValueError("Feedback reply already installed")
    source=once(source,
        "from music_transform_quality import transformation_contract, transformation_directive, quality_review, repair_directive",
        "from music_transform_quality import transformation_contract, transformation_directive, quality_review, repair_directive, music_feedback_followup",
        "feedback import")
    anchor='''    if music_transform_contract:
        system+=transformation_directive(music_transform_contract)
    native_evidence=payload.get("nativeEditorEvidence")'''
    replacement='''    if music_transform_contract:
        system+=transformation_directive(music_transform_contract)
    elif music_feedback_followup(prompt,history):
        # swrlz-music-feedback-reply-v1: the user is explaining an error,
        # not asking for a new song, a lyrics lookup or model-side research.
        system+=(
            "\\nCURRENT TURN IS MUSIC QUALITY FEEDBACK: Address the user's actual "
            "correction about the previous remix or song. Discuss the specific "
            "errors and what needs changing; do not compose a replacement or "
            "retrieve source lyrics unless the user explicitly asks for that. "
            "Do not claim to have verified information not in this thread.")
    native_evidence=payload.get("nativeEditorEvidence")'''
    source=once(source,anchor,replacement,"feedback system response mode")
    ast.parse(source,filename=ENGINE)
    return source

def patch_native(source):
    if "swrlz-qwen-http500-once-retry-v1" in source:
        raise ValueError("Native retry already installed")
    source=once(source,
        "from stop_transport import completion_response, generation_cancelled",
        "from stop_transport import completion_response, generation_cancelled\nfrom qwen_http500_recovery import native_stream_once_retry",
        "native retry import")
    before='''                with completion_response(payload,SERVER_PORT,_post,timeout=900) as response:
                    for raw in response:
                        if generation_cancelled():
                            return
                        if not raw.startswith(b"data:"):
                            continue
                        content = raw.split(b":", 1)[1].strip()
                        if content == b"[DONE]":
                            completed = True
                            break
                        if content:
                            value = json.loads(content)
                            if value.get("error"):
                                raise RuntimeError("QWEN35_INFERENCE_ERROR")
                            if isinstance(value.get("timings"), dict):
                                native_timing = value["timings"]
                            delta = (value.get("choices") or [{}])[0].get("delta") or {}
                            if first_delta_at is None and delta.get("content"):
                                first_delta_at = time.perf_counter()
                            yield value'''
    after='''                # swrlz-qwen-http500-once-retry-v1: uncached retry only if
                # the local server fails before a single SSE byte is emitted.
                for raw in native_stream_once_retry(
                        payload,lambda p:completion_response(
                            p,SERVER_PORT,_post,timeout=900),
                        generation_cancelled,
                        lambda:print(json.dumps({
                            "event":"QWEN35_HTTP500_UNCACHED_RETRY",
                            "attempt":2,"originalStatus":500}),flush=True)):
                    if generation_cancelled():
                        return
                    if not raw.startswith(b"data:"):
                        continue
                    content = raw.split(b":", 1)[1].strip()
                    if content == b"[DONE]":
                        completed = True
                        break
                    if content:
                        value = json.loads(content)
                        if value.get("error"):
                            raise RuntimeError("QWEN35_INFERENCE_ERROR")
                        if isinstance(value.get("timings"), dict):
                            native_timing = value["timings"]
                        delta = (value.get("choices") or [{}])[0].get("delta") or {}
                        if first_delta_at is None and delta.get("content"):
                            first_delta_at = time.perf_counter()
                        yield value'''
    source=once(source,before,after,"native SSE retry wrapping")
    ast.parse(source,filename=NATIVE)
    return source

def patch_station(source):
    # Keep the terminal failure and original diagnostic code in Activity Log.
    # Only replace the raw technical error in the human-facing bubble.
    before='''"Generation failed: "+str(exc)[:240]'''
    after='''("Local Qwen inference failed after a retry. Your message was saved; please try again."
                            if str(exc)=="QWEN35_HTTP_500"
                            else "Generation failed: "+str(exc)[:240])'''
    source=once(source,before,after,"human-facing exhausted native 500")
    ast.parse(source,filename=STATION)
    return source

def build(originals):
    helper=Path(__file__).with_name("qwen_http500_recovery_v1.py").read_bytes()
    ast.parse(helper,filename=HELPER)
    return {
        MUSIC:patch_music(originals[MUSIC].decode()).encode(),
        ENGINE:patch_engine(originals[ENGINE].decode()).encode(),
        NATIVE:patch_native(originals[NATIVE].decode()).encode(),
        STATION:patch_station(originals[STATION].decode()).encode(),
        HELPER:helper,
    }

def inspect(snapshot=False):
    from huggingface_hub import HfApi,hf_hub_download
    api=HfApi()
    revision=api.repo_info(SPACE,repo_type="space").sha
    if len(str(revision or ""))!=40:
        raise RuntimeError("No immutable Space revision available")
    source_files=set(api.list_repo_files(SPACE,repo_type="space",revision=revision))
    if HELPER in source_files:
        raise RuntimeError("Helper already exists; refuse overwrite")
    originals={
        f:Path(hf_hub_download(SPACE,f,repo_type="space",revision=revision)).read_bytes()
        for f in FILES
    }
    edited=build(originals)
    manifest={"space":SPACE,"revision":revision,
              "before":{f:sha(v) for f,v in originals.items()},
              "after":{f:sha(v) for f,v in edited.items()}}
    if snapshot:
        BACKUP.mkdir(parents=True,exist_ok=True)
        for f,v in originals.items():
            (BACKUP/f).write_bytes(v)
        (BACKUP/"manifest.json").write_text(json.dumps(manifest,sort_keys=True,indent=2)+"\n")
    print("HTTP500_FEEDBACK_PREFLIGHT",json.dumps(manifest,sort_keys=True),flush=True)

def publish():
    from huggingface_hub import HfApi,CommitOperationAdd,CommitOperationDelete,hf_hub_download
    if os.environ.get("SWRLZ_HTTP500_FEEDBACK_APPROVED")!="1":
        raise PermissionError("Governed release approval absent")
    token=os.environ.get("HF_TOKEN")
    if not token:
        raise PermissionError("Missing approved Hugging Face secret")
    manifest=json.loads((BACKUP/"manifest.json").read_text())
    api=HfApi(token=token)
    revision=manifest["revision"]
    if manifest["space"]!=SPACE or api.repo_info(SPACE,repo_type="space").sha!=revision:
        raise RuntimeError("Space revision changed: refuse stale release")
    live_files=set(api.list_repo_files(SPACE,repo_type="space",revision=revision))
    if HELPER in live_files:
        raise RuntimeError("Helper already exists")
    originals={}
    for f in FILES:
        original=(BACKUP/f).read_bytes()
        live=Path(hf_hub_download(SPACE,f,repo_type="space",revision=revision,token=token)).read_bytes()
        if sha(original)!=manifest["before"][f] or original!=live:
            raise RuntimeError("Immutable source drift: "+f)
        originals[f]=original
    edited=build(originals)
    if {f:sha(v) for f,v in edited.items()}!=manifest["after"]:
        raise RuntimeError("Candidate checksum differs")
    commit=api.create_commit(
        repo_id=SPACE,repo_type="space",parent_commit=revision,
        operations=[CommitOperationAdd(path_in_repo=f,path_or_fileobj=io.BytesIO(v))
                    for f,v in edited.items()],
        commit_message="fix(§C): route remix critiques to conversation and retry Qwen HTTP500")
    new_rev=str(getattr(commit,"oid",None) or api.repo_info(SPACE,repo_type="space").sha)
    try:
        for f,v in edited.items():
            readback=Path(hf_hub_download(SPACE,f,repo_type="space",revision=new_rev,token=token)).read_bytes()
            if readback!=v:raise RuntimeError("Published content differs: "+f)
    except Exception:
        if api.repo_info(SPACE,repo_type="space").sha==new_rev:
            api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=new_rev,
               operations=[
                *[CommitOperationAdd(path_in_repo=f,path_or_fileobj=io.BytesIO(v))
                  for f,v in originals.items()],
                CommitOperationDelete(path_in_repo=HELPER)],
               commit_message="rollback(§C): restore exact Qwen and music files after readback failure")
        raise
    print("HTTP500_FEEDBACK_PUBLISHED",json.dumps({"before":revision,"after":new_rev,
         "paths":list(edited),"verified":True}),flush=True)

if __name__=="__main__":
    import argparse
    cli=argparse.ArgumentParser()
    cli.add_argument("mode",choices=("inspect","snapshot","publish"))
    mode=cli.parse_args().mode
    if mode=="publish":publish()
    else:inspect(snapshot=(mode=="snapshot"))
