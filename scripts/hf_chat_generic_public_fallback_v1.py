#!/usr/bin/env python3
"""Guarded §C generic Wikipedia fallback for empty public search results.

Changes exactly the public retrieval module and one new pure search helper.
The existing 9B core, visible source panel, historical class verifier, UI,
account data and hosting controls remain untouched.
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

from huggingface_hub import HfApi,hf_hub_download,CommitOperationAdd,CommitOperationDelete

SPACE="kamiloki/Swyrlz"
BASE="https://kamiloki-swyrlz.hf.space"
RETRIEVAL="api/selective_retrieval.py"
FALLBACK="api/generic_public_source_fallback_v1.py"
MARKER="swrlz-generic-public-research-wikipedia-fallback-v1"
HEADERS={"User-Agent":"SWRLZ-Research-Sources-Fallback/1","Cache-Control":"no-cache"}

OLD=r'''    evidence = bounded_evidence({"evidence": references + list(searched)},
                                query=decision.query)
    if evidence["resultCount"] == 0:
        return out, {"phase": "RESEARCH_UNAVAILABLE", "reason": "no_relevant_evidence"}'''
NEW=r'''    evidence = bounded_evidence({"evidence": references + list(searched)},
                                query=decision.query)
    # swrlz-generic-public-research-wikipedia-fallback-v1: if the
    # primary public search provided no relevant source, discover real
    # encyclopedia articles using the existing bounded safe page fetcher.
    # Results are only retrieved references, NEVER verified exhaustive facts.
    if evidence["resultCount"] == 0 and callable(fetch_page):
        from api.generic_public_source_fallback_v1 import wikipedia_public_fallback
        encyclopedia = wikipedia_public_fallback(decision.query,fetch_page)
        if encyclopedia:
            evidence = bounded_evidence({"evidence": encyclopedia},
                                        query=decision.query)
    if evidence["resultCount"] == 0:
        return out, {"phase": "RESEARCH_UNAVAILABLE", "reason": "no_relevant_evidence"}'''


def digest(data:bytes)->str:
    return hashlib.sha256(data).hexdigest()


def patch_retrieval(before:bytes)->bytes:
    text=before.decode("utf-8")
    if MARKER in text:raise RuntimeError("Wikipedia source fallback already installed")
    if text.count(OLD)!=1:
        raise RuntimeError("Live public researcher enrichment contract moved")
    for marker in ("def bounded_evidence(","def enrich_payload(",
                   "historical_class_reference_pages("):
        if marker not in text:raise RuntimeError("Missing existing selective research route")
    revised=text.replace(OLD,NEW,1)
    ast.parse(revised,filename=RETRIEVAL)
    return revised.encode("utf-8")


def head(api):
    return api.repo_info(SPACE,repo_type="space").sha


def live_bytes(api,path,rev):
    return Path(hf_hub_download(SPACE,path,repo_type="space",
                               revision=rev,token=api.token)).read_bytes()


def prepare(api,out:Path):
    out.mkdir(parents=True,exist_ok=True)
    before=head(api)
    existing=set(api.list_repo_files(SPACE,repo_type="space",revision=before))
    if FALLBACK in existing:raise RuntimeError("Fallback module already exists; do not overwrite")
    source=live_bytes(api,RETRIEVAL,before)
    root=Path(__file__).resolve().parents[1]
    candidate={RETRIEVAL:patch_retrieval(source),
               FALLBACK:(root/FALLBACK).read_bytes()}
    for path,content in candidate.items():
        ast.parse(content.decode("utf-8"),filename=path)
        target=out/"candidate"/path;target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(content)
    path=out/"before"/RETRIEVAL;path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(source)
    receipt={"before":before,"status":"PREPARED_NOT_PUBLISHED",
             "original":{RETRIEVAL:digest(source)},
             "candidate":{p:digest(data) for p,data in candidate.items()},
             "paths":list(candidate)}
    (out/"receipt.json").write_text(json.dumps(receipt,indent=2),"utf-8")
    print("SWRLZ_GENERIC_RESEARCH_PREPARED "+json.dumps(receipt),flush=True)
    return receipt


def verify_runtime(api,rev,seconds=1000):
    start=time.monotonic();checks=0
    while time.monotonic()-start<seconds:
        if head(api)!=rev:raise RuntimeError("Concurrent Hugging Face change")
        checks+=1
        try:
            with urllib.request.urlopen(urllib.request.Request(
                    "https://huggingface.co/api/spaces/"+SPACE,headers=HEADERS),
                    timeout=18) as response:
                metadata=json.load(response)
            runtime=metadata.get("runtime") or {}
            if runtime.get("stage")=="RUNNING" and runtime.get("sha")==rev:
                with urllib.request.urlopen(urllib.request.Request(
                        BASE+"/api/hf/qwen35-ready",headers=HEADERS),
                        timeout=22) as response:
                    status=json.load(response)
                if status.get("model")=="qwen3.5-9b" and status.get("ready") is True:
                    print("SWRLZ_GENERIC_RESEARCH_RUNTIME_MATCH "+json.dumps(
                        {"sha":rev,"checks":checks}),flush=True)
                    return
        except (OSError,ValueError):
            pass
        time.sleep(12)
    raise RuntimeError("Current 9B runtime never reached exact revision")


def guest_turn(prompt,*,expected_research=False,expected_names=()):
    jar=http.cookiejar.CookieJar()
    opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    rid=str(uuid.uuid4())
    body={"modelId":"700m","prompt":prompt,
          "threadId":"swrlz-generic-evidence-test-"+str(uuid.uuid4()),
          "requestId":rid,"profileId":"LALM",
          "profile":"","userProfile":"","timeZone":"UTC"}
    req=urllib.request.Request(BASE+"/api/lalm_station/send",
        method="POST",data=json.dumps(body).encode(),
        headers={**HEADERS,"Content-Type":"application/json"})
    with opener.open(req,timeout=42) as response:
        if response.status!=202:raise RuntimeError("Guest test request not accepted")
    stream_url=BASE+"/api/lalm_station/stream?"+urllib.parse.urlencode({"requestId":rid})
    started=time.monotonic();parts=[];phases=[];terminal=""
    with opener.open(urllib.request.Request(stream_url,headers=HEADERS),timeout=370) as stream:
        for row in stream:
            if time.monotonic()-started>360:
                raise RuntimeError("Generic research test time budget exceeded")
            try:event=json.loads(row)
            except (TypeError,ValueError):continue
            typ=event.get("type")
            if typ=="DELTA":parts.append(str(event.get("text") or ""))
            elif typ=="STATUS":phases.append(str(event.get("phase") or ""))
            elif typ in ("COMPLETE","COMPLETED","FAILED","CANCELLED"):
                terminal=typ;break
    answer="".join(parts)
    matched={name:bool(re.search(r"\b"+re.escape(name)+r"\b",answer,re.I))
             for name in expected_names}
    record={"terminal":terminal,"characters":len(answer),
            "durationSeconds":round(time.monotonic()-started,2),
            "researchStarted":"RESEARCH_STARTED" in phases,
            "sourceCount":sum(x in ("RESEARCH_SOURCE_RETRIEVED",
                                    "RESEARCH_SOURCE_CHECKED") for x in phases),
            "expectedNames":matched,"phaseTail":phases[-16:]}
    print("SWRLZ_GENERIC_RESEARCH_LIVE_CASE "+json.dumps(record),flush=True)
    if terminal not in ("COMPLETE","COMPLETED") or not answer.strip():
        raise RuntimeError("Model answer failed to complete")
    if expected_research and (not record["researchStarted"] or record["sourceCount"]<1):
        raise RuntimeError("No actual public sources for the general research question")
    if any(not value for value in matched.values()):
        raise RuntimeError("Model failed to report source-supported expected names")
    if not expected_research and record["sourceCount"]:
        raise RuntimeError("Casual conversation was incorrectly routed to public source search")
    return record


def deploy(api,out,receipt):
    if os.environ.get("SWRLZ_GENERIC_PUBLIC_FALLBACK_DEPLOY_APPROVED")!="1":
        raise RuntimeError("Owner-approved release flag missing")
    before=receipt["before"]
    if head(api)!=before:raise RuntimeError("Space changed after staging")
    result=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=before,
        operations=[CommitOperationAdd(path_in_repo=p,
                    path_or_fileobj=str(out/"candidate"/p))
                    for p in (RETRIEVAL,FALLBACK)],
        commit_message="§C: generic public source fallback for empty research queries")
    rev=str(result.oid)
    receipt.update({"published":rev,"status":"PUBLISHED_ACCEPTANCE_PENDING"})
    try:
        if head(api)!=rev:raise RuntimeError("Other Space publisher moved revision")
        for path,d in receipt["candidate"].items():
            if digest(live_bytes(api,path,rev))!=d:
                raise RuntimeError("Published bytes mismatch for "+path)
        verify_runtime(api,rev)
        guest_turn("Research: what are the moons of Mars? List their names.",
                   expected_research=True,expected_names=("Phobos","Deimos"))
        guest_turn("What were all the classes in Diablo 2 LoD?",expected_research=True,
                   expected_names=("Amazon","Barbarian","Necromancer","Paladin",
                                   "Sorceress","Assassin","Druid"))
        guest_turn("Hello there!",expected_research=False)
        receipt["status"]="LIVE_VERIFIED"
        print("SWRLZ_GENERIC_RESEARCH_LIVE_VERIFIED "+rev,flush=True)
    except BaseException:
        print("SWRLZ_GENERIC_RESEARCH_ROLLBACK_REQUESTED",flush=True)
        if head(api)!=rev:
            raise RuntimeError("Concurrent Space change prevents safe rollback") from None
        rolled=str(api.create_commit(repo_id=SPACE,repo_type="space",
            parent_commit=rev,
            operations=[
                CommitOperationAdd(path_in_repo=RETRIEVAL,
                                   path_or_fileobj=str(out/"before"/RETRIEVAL)),
                CommitOperationDelete(path_in_repo=FALLBACK),
            ],commit_message="Rollback §C generic source fallback to byte-exact prior lookup").oid)
        if head(api)!=rolled or digest(live_bytes(api,RETRIEVAL,rolled))!=receipt["original"][RETRIEVAL]:
            raise RuntimeError("Rollback source integrity mismatch")
        receipt.update({"status":"ROLLED_BACK","restored":rolled})
        print("SWRLZ_GENERIC_RESEARCH_ROLLBACK_VERIFIED "+rolled,flush=True)
        raise
    finally:
        (out/"receipt.json").write_text(json.dumps(receipt,indent=2),"utf-8")


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--deploy",action="store_true")
    parser.add_argument("--out",default="swrlz-generic-research-source-backup")
    args=parser.parse_args()
    token=os.environ.get("HF_TOKEN") or None
    if args.deploy and not token:raise RuntimeError("Missing HF deployment credential")
    api=HfApi(token=token)
    out=Path(args.out)
    receipt=prepare(api,out)
    if args.deploy:deploy(api,out,receipt)


if __name__=="__main__":
    main()
