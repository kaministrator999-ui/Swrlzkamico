#!/usr/bin/env python3
"""§C researched-claim guard: prepare exact live Space candidate; guarded release.

No hardware, account, model-weight, stored-conversation or §E edits.
The existing public research adapter owns all outbound network safeguards.
"""
from __future__ import annotations
import argparse
import ast
import hashlib
import http.cookiejar
import json
import os
from pathlib import Path
import re
import time
import urllib.parse
import urllib.request
import uuid

from huggingface_hub import HfApi, hf_hub_download, CommitOperationAdd, CommitOperationDelete

SPACE = "kamiloki/Swyrlz"
BASE = "https://kamiloki-swyrlz.hf.space"
ENGINE = "lfm2_700m_engine.py"
RETRIEVAL = "api/selective_retrieval.py"
AUDITOR = "api/factual_claim_guard_v1.py"
CHANGES = (ENGINE, RETRIEVAL, AUDITOR)
MARKER = "swrlz-evidence-checked-factual-response-v1"
EXPECTED_RETRIEVAL_BLOB = "e8715433f1bfc188dce6a40df30fd65bc3e06a85"
HEADERS = {"User-Agent":"SWRLZ-Grounded-Claim-Verification/1",
           "Cache-Control":"no-cache"}

WRAPPER = r'''

# swrlz-evidence-checked-factual-response-v1
# The existing engine remains responsible for inference and all specialist
# paths. Only ordinary SELECTIVE public evidence answers are held for the
# source-claim gate. No model output is visible before factual checks finish.
_swrlz_original_generate_events_factual_v1 = generate_events


def generate_events(payload):
    from api.factual_claim_guard_v1 import (
        sourced_answer as _sourced_answer_v1,
        inspect_answer as _inspect_factual_v1,
        evidence_only_reply as _evidence_only_v1,
    )
    if not isinstance(payload, dict) or os.environ.get(
            "SWRLZ_FACTUAL_CLAIM_GUARD_ENABLED", "1").strip().lower() in ("0","false","off"):
        yield from _swrlz_original_generate_events_factual_v1(payload)
        return
    from api.selective_retrieval import enrich_payload as _enrich_v1
    researcher = fetcher = None
    try:
        from api.online_research import research as researcher, _page_fetch as fetcher
    except ImportError:
        pass
    try:
        enriched, route = _enrich_v1(
            payload, researcher, fetch_page=fetcher, enabled=True)
    except Exception:
        yield from _swrlz_original_generate_events_factual_v1(payload)
        return
    if not _sourced_answer_v1(enriched):
        yield from _swrlz_original_generate_events_factual_v1(enriched)
        return
    if route.get("phase") == "RESEARCH_READY":
        yield {"type":"STATUS","phase":"RESEARCH_READY",
               "reason":"Public sources were retrieved for this request"}
    yield {"type":"STATUS","phase":"FACTUAL_VERIFICATION_STARTED",
           "reason":"Checking response dates and named versions against the retrieved sources"}
    bundle = enriched["onlineContext"]
    chunks = []
    for event in _swrlz_original_generate_events_factual_v1(enriched):
        if not isinstance(event,dict):
            yield event
            continue
        kind = str(event.get("type") or "").upper()
        if kind == "DELTA":
            chunks.append(str(event.get("text") or ""))
            continue
        if kind in ("COMPLETE", "COMPLETED"):
            answer = "".join(chunks)
            verdict = _inspect_factual_v1(answer,bundle)
            if verdict["status"] == "PASS":
                yield {"type":"STATUS","phase":"FACTUAL_VERIFICATION_PASS",
                       "reason":"Calendar years, numbered Acts and edition aliases passed the source checks"}
                if answer:yield {"type":"DELTA","text":answer}
                yield event
            else:
                reason = ",".join(verdict.get("reasons") or [])[:200]
                yield {"type":"STATUS","phase":"FACTUAL_VERIFICATION_REJECT",
                       "reason":reason}
                yield {"type":"STATUS","phase":"SOURCE_ONLY_FALLBACK",
                       "reason":"Unsupported claims withheld; showing attributable sources instead"}
                yield {"type":"DELTA","text":_evidence_only_v1(payload.get("prompt",""),bundle)}
                yield {"type":"COMPLETED","phase":"COMPLETE",
                       "verification":"SOURCE_ONLY_FALLBACK","modelDraftAccepted":False}
            return
        if kind == "FAILED":
            reason = str(event.get("reason") or "")
            if "OUTPUT_TOKEN_LIMIT" in reason.upper() and chunks:
                yield {"type":"STATUS","phase":"SOURCE_ONLY_FALLBACK",
                       "reason":"The model did not finish within the limit; showing checked sources"}
                yield {"type":"DELTA","text":_evidence_only_v1(payload.get("prompt",""),bundle)}
                yield {"type":"COMPLETED","phase":"COMPLETE",
                       "verification":"SOURCE_ONLY_FALLBACK","modelDraftAccepted":False}
            else:
                yield event
            return
        yield event
'''


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def patch_engine(live: bytes) -> bytes:
    source=live.decode("utf-8")
    if MARKER in source:raise RuntimeError("Already contains factual guard")
    if source.count("\ndef generate_events(payload):") != 1:
        raise RuntimeError("Live engine generate_events anchor drift")
    for marker in ("swrlz-selective-factual-retrieval-v1",
                   "swrlz-research-answer-limit-recovery-v1",
                   'yield {"type":"COMPLETED","phase":"COMPLETE"'):
        if marker not in source:raise RuntimeError("Missing live feature anchor: "+marker)
    candidate=source.rstrip()+"\n"+WRAPPER+"\n"
    ast.parse(candidate,filename=ENGINE)
    if candidate.count(MARKER)!=1:raise RuntimeError("Factual patch marker drift")
    return candidate.encode("utf-8")


def space_sha(api):
    return api.repo_info(SPACE,repo_type="space").sha


def space_file(api,path,rev):
    return Path(hf_hub_download(SPACE,path,repo_type="space",
                               revision=rev,token=api.token)).read_bytes()


def prepare(api,folder):
    folder.mkdir(parents=True,exist_ok=True)
    rev=space_sha(api)
    files=set(api.list_repo_files(SPACE,repo_type="space",revision=rev))
    if AUDITOR in files:raise RuntimeError("Factual auditor already exists in Space")
    originals={ENGINE:space_file(api,ENGINE,rev),
               RETRIEVAL:space_file(api,RETRIEVAL,rev)}
    if git_blob_sha(originals[RETRIEVAL])!=EXPECTED_RETRIEVAL_BLOB:
        raise RuntimeError("Selective retrieval implementation moved: do not overwrite")
    repo_root=Path(__file__).resolve().parents[1]
    changes={ENGINE:patch_engine(originals[ENGINE]),
             RETRIEVAL:(repo_root/RETRIEVAL).read_bytes(),
             AUDITOR:(repo_root/AUDITOR).read_bytes()}
    for path,data in changes.items():
        ast.parse(data.decode("utf-8"),filename=path)
        output=folder/"candidate"/path
        output.parent.mkdir(parents=True,exist_ok=True)
        output.write_bytes(data)
    for path,data in originals.items():
        output=folder/"before"/path
        output.parent.mkdir(parents=True,exist_ok=True)
        output.write_bytes(data)
    receipt={"space":SPACE,"before":rev,"status":"PREPARED_NOT_DEPLOYED",
             "original":{key:digest(data) for key,data in originals.items()},
             "candidate":{key:digest(data) for key,data in changes.items()},
             "changes":list(CHANGES)}
    (folder/"receipt.json").write_text(json.dumps(receipt,indent=2),"utf-8")
    print("SWRLZ_FACTUAL_PREPARED "+json.dumps(receipt),flush=True)
    return receipt


def wait_runtime(api,rev,seconds=960):
    start=time.monotonic()
    checks=0
    while time.monotonic()-start<seconds:
        if space_sha(api)!=rev:raise RuntimeError("Space moved concurrently")
        checks+=1
        try:
            req=urllib.request.Request("https://huggingface.co/api/spaces/"+SPACE,headers=HEADERS)
            with urllib.request.urlopen(req,timeout=14) as response:
                metadata=json.load(response)
            actual=metadata.get("runtime") or {}
            if actual.get("stage")=="RUNNING" and actual.get("sha")==rev:
                with urllib.request.urlopen(
                    urllib.request.Request(BASE+"/api/hf/qwen35-ready",headers=HEADERS),
                    timeout=18) as response:
                    ready=json.load(response)
                if ready.get("ready") is True and ready.get("model")=="qwen3.5-9b":
                    print("SWRLZ_FACTUAL_RUNTIME_VERIFIED "+json.dumps(
                        {"sha":rev,"checks":checks}),flush=True)
                    return
        except (ValueError,OSError):
            pass
        if checks%6==0:print("SWRLZ_FACTUAL_RUNTIME_STARTING "+str(checks),flush=True)
        time.sleep(12)
    raise RuntimeError("Running 9B Space did not match published source revision")


def live_inference():
    jar=http.cookiejar.CookieJar()
    opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    prompt=("Was Diablo II Classic released before Lord of Destruction? "
            "Research both versions and explain the differences.")
    request_id=str(uuid.uuid4())
    body={"modelId":"700m","prompt":prompt,
          "threadId":"swrlz-factual-regression-"+str(uuid.uuid4()),
          "requestId":request_id,"profileId":"LALM","profile":"",
          "userProfile":"","timeZone":"UTC"}
    req=urllib.request.Request(
        BASE+"/api/lalm_station/send",method="POST",
        data=json.dumps(body).encode(),
        headers={**HEADERS,"Content-Type":"application/json"})
    with opener.open(req,timeout=40) as resp:
        if resp.status!=202:raise RuntimeError("Synthetic request not accepted")
    stream=BASE+"/api/lalm_station/stream?"+urllib.parse.urlencode({"requestId":request_id})
    parts=[];phases=[];terminal="";started=time.monotonic()
    with opener.open(urllib.request.Request(stream,headers=HEADERS),timeout=370) as response:
        for raw in response:
            if time.monotonic()-started>360:
                raise RuntimeError("Factual acceptance inference time budget exceeded")
            try:entry=json.loads(raw)
            except ValueError:continue
            typ=entry.get("type")
            if typ=="DELTA":parts.append(str(entry.get("text") or ""))
            elif typ=="STATUS":phases.append(str(entry.get("phase") or ""))
            elif typ in ("COMPLETE","COMPLETED","FAILED","CANCELLED"):
                terminal=typ;break
    answer="".join(parts)
    low=answer.lower()
    result={"terminal":terminal,"characters":len(answer),
            "research":"RESEARCH_READY" in phases,
            "sourceChecked":"FACTUAL_VERIFICATION_PASS" in phases,
            "fallback":"SOURCE_ONLY_FALLBACK" in phases,
            "durationSeconds":round(time.monotonic()-started,2),
            "years":sorted(set(re.findall(r"(?<!\d)(?:19|20)\d{2}(?!\d)",answer)))[:15],
            "versionLabels":{"lord":"lord of destruction" in low,
                             "classic":"classic" in low,
                             "remaster":"resurrected" in low}}
    print("SWRLZ_FACTUAL_LIVE_ACCEPTANCE "+json.dumps(result),flush=True)
    # Stronger than previous test: specific supported chronological facts
    # must appear in the completed answer. Source-only fallback isn't a pass.
    if terminal not in ("COMPLETE","COMPLETED") or not result["research"]:
        raise RuntimeError("Live research generation did not complete")
    if not result["sourceChecked"] or result["fallback"]:
        raise RuntimeError("Live model answer failed factual evidence verification")
    years=set(result["years"])
    if not {"2000","2001"}.issubset(years) or len(answer)<120:
        raise RuntimeError("Verified base/expansion release years absent from answer")
    if any(y in years for y in ("2023","2024")):
        raise RuntimeError("Live answer confused original and remastered release dates")
    if not result["versionLabels"]["lord"]:
        raise RuntimeError("Expansion version missing from answer")


def release(api,folder,receipt):
    if os.environ.get("SWRLZ_FACTUAL_GROUNDING_DEPLOY_APPROVED")!="1":
        raise RuntimeError("Owner approval environment flag required")
    before=receipt["before"]
    if space_sha(api)!=before:raise RuntimeError("Space changed after stage")
    result=api.create_commit(
        repo_id=SPACE,repo_type="space",parent_commit=before,
        operations=[CommitOperationAdd(path_in_repo=p,path_or_fileobj=str(folder/"candidate"/p))
                    for p in CHANGES],
        commit_message="§C: source-backed version dates and researched-answer claim gate")
    published=str(result.oid)
    receipt.update({"status":"PUBLISHED_ACCEPTANCE_PENDING","published":published})
    try:
        if space_sha(api)!=published:raise RuntimeError("Concurrent publication detected")
        for path,sha in receipt["candidate"].items():
            if digest(space_file(api,path,published))!=sha:
                raise RuntimeError("Published bytes mismatch: "+path)
        wait_runtime(api,published)
        live_inference()
        receipt["status"]="LIVE_VERIFIED"
        print("SWRLZ_FACTUAL_LIVE_VERIFIED "+json.dumps(
            {"space":SPACE,"revision":published}),flush=True)
    except BaseException:
        print("SWRLZ_FACTUAL_ROLLBACK_REQUESTED",flush=True)
        if space_sha(api)!=published:
            raise RuntimeError("Concurrent change prevents safe rollback") from None
        operations=[
            CommitOperationAdd(path_in_repo=p,path_or_fileobj=str(folder/"before"/p))
            for p in (ENGINE,RETRIEVAL)]
        operations.append(CommitOperationDelete(path_in_repo=AUDITOR))
        rolled=api.create_commit(
            repo_id=SPACE,repo_type="space",parent_commit=published,
            operations=operations,
            commit_message="Rollback §C factual claim gate to byte-exact prior runtime")
        restored=str(rolled.oid)
        if space_sha(api)!=restored:
            raise RuntimeError("Rollback revision mismatch")
        for path,sha in receipt["original"].items():
            if digest(space_file(api,path,restored))!=sha:
                raise RuntimeError("Rollback source hash mismatch: "+path)
        receipt.update({"status":"ROLLED_BACK","restored":restored})
        print("SWRLZ_FACTUAL_ROLLBACK_VERIFIED "+restored,flush=True)
        raise
    finally:
        (folder/"receipt.json").write_text(json.dumps(receipt,indent=2),"utf-8")


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",default="swrlz-factual-source-rollback")
    parser.add_argument("--deploy",action="store_true")
    args=parser.parse_args()
    token=os.environ.get("HF_TOKEN") or None
    if args.deploy and not token:
        raise RuntimeError("Missing owner Hugging Face deployment credential")
    api=HfApi(token=token)
    folder=Path(args.out)
    receipt=prepare(api,folder)
    if args.deploy:release(api,folder,receipt)


if __name__=="__main__":
    main()
