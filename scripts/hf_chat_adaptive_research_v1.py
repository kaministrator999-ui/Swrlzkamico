#!/usr/bin/env python3
"""Source-exact, guarded §C adaptive multi-pass public research release.

Changes only the existing selective public retrieval, the tagged-model
evidence envelope, and one new pure helper. No account, private history,
weights, §E or code-action changes. Every live change is SHA-checked and
automatically rolled back if acceptance fails and no concurrent change exists.
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

SPACE="kamiloki/Swyrlz"
BASE="https://kamiloki-swyrlz.hf.space"
SELECTIVE="api/selective_retrieval.py"
ENVELOPE="api/research_evidence_envelope_v1.py"
HELPER="api/adaptive_public_research_v1.py"
CHANGES=(SELECTIVE, ENVELOPE, HELPER)
MARKER="swrlz-adaptive-public-research-coverage-v1"
HEADERS={"User-Agent":"SWRLZ-Adaptive-Research-v1","Cache-Control":"no-cache"}

SELECTIVE_WRAPPER=r'''

# swrlz-adaptive-public-research-coverage-v1
# Existing, source-scoped public lookup runs first. Only incomplete multi-
# facet questions receive one bounded supplemental public search pass.
_swrlz_original_choose_retrieval_adaptive_v1=choose_retrieval
_swrlz_original_enrich_payload_adaptive_v1=enrich_payload


def choose_retrieval(prompt, *, has_evidence=False, has_attachment=False,
                     source_change=False, private_context=False):
    original=_swrlz_original_choose_retrieval_adaptive_v1(
        prompt,has_evidence=has_evidence,has_attachment=has_attachment,
        source_change=source_change,private_context=private_context)
    if original.action!="direct" or original.reason!="concept_or_conversation":
        return original
    from api.adaptive_public_research_v1 import should_research_public_explanation
    if should_research_public_explanation(prompt):
        return Decision("retrieve","public_background_explanation",
                        _normalized(prompt))
    return original


def enrich_payload(payload, researcher, *, fetch_page=None, enabled=False):
    enriched,route=_swrlz_original_enrich_payload_adaptive_v1(
        payload,researcher,fetch_page=fetch_page,enabled=enabled)
    if not enabled or not isinstance(enriched,dict):
        return enriched,route
    from api.adaptive_public_research_v1 import adaptive_enrich
    return adaptive_enrich(
        enriched,route,researcher,bounded_evidence=bounded_evidence,
        fetch_page=fetch_page,enabled=enabled)
'''

ADAPTIVE_INFO=r'''
    # swrlz-adaptive-public-research-model-coverage-v1
    adaptive=bundle.get("adaptiveResearch")
    if isinstance(adaptive,dict) and adaptive.get("schema")=="swrlz-adaptive-public-research-v1":
        def _facet_values(key):
            values=adaptive.get(key)
            if not isinstance(values,list):
                return []
            return [_plain(value,90) for value in values[:3]]
        packet["research_process"]={
            "role":"trusted_server_research_coverage_status",
            "passesAttempted":min(2,max(1,int(adaptive.get("passesAttempted") or 1))),
            "facetsRequested":_facet_values("facetsRequested"),
            "topicallyMatchedFacets":_facet_values("facetsCoveredByRetrievedText"),
            "unresolvedEvidenceFacets":_facet_values("facetsNeedingVerification"),
            "coverageMeaning":"Topic-word overlap is not a claim-verification result.",
            "responseGuidance":"Explain missing evidence instead of extrapolating.",
        }
'''

ENVELOPE_ANCHOR='    if checked and isinstance(verified, dict):\n        packet["checked_findings"] = {'


def hash_bytes(b:bytes)->str:
    return hashlib.sha256(b).hexdigest()


def patch_selective(before:bytes)->bytes:
    original=before.decode("utf-8")
    if MARKER in original:raise RuntimeError("Adaptive public source wrapper already installed")
    for marker in (
        "def choose_retrieval(", "def enrich_payload(",
        "def bounded_evidence(", "swrlz-generic-public-research-wikipedia-fallback-v1",
        "historical_class_reference_pages(",
    ):
        if marker not in original:raise RuntimeError("Missing existing research feature: "+marker)
    staged=original.rstrip()+"\n"+SELECTIVE_WRAPPER+"\n"
    ast.parse(staged,filename=SELECTIVE)
    if staged.count(MARKER)!=1:raise RuntimeError("Duplicate adaptive lineage marker")
    return staged.encode("utf-8")


def patch_envelope(before:bytes)->bytes:
    original=before.decode("utf-8")
    if "swrlz-adaptive-public-research-model-coverage-v1" in original:
        raise RuntimeError("Adaptive model envelope already installed")
    if original.count(ENVELOPE_ANCHOR)!=1:
        raise RuntimeError("Role-tagged model envelope anchor moved")
    if "def build_envelope(" not in original or "conversation_context" not in original:
        raise RuntimeError("Existing user/history/source trust boundary missing")
    staged=original.replace(ENVELOPE_ANCHOR,ADAPTIVE_INFO+ENVELOPE_ANCHOR,1)
    ast.parse(staged,filename=ENVELOPE)
    return staged.encode("utf-8")


def revision(api):
    return api.repo_info(SPACE,repo_type="space").sha


def get_bytes(api,path,rev):
    return Path(hf_hub_download(SPACE,path,repo_type="space",
                               revision=rev,token=api.token)).read_bytes()


def prepare(api,folder:Path):
    folder.mkdir(parents=True,exist_ok=True)
    before=revision(api)
    names=set(api.list_repo_files(SPACE,repo_type="space",revision=before))
    if HELPER in names:raise RuntimeError("Helper path exists; refuse unsafe overwrite")
    original={p:get_bytes(api,p,before) for p in (SELECTIVE,ENVELOPE)}
    repo=Path(__file__).resolve().parents[1]
    candidate={
        SELECTIVE:patch_selective(original[SELECTIVE]),
        ENVELOPE:patch_envelope(original[ENVELOPE]),
        HELPER:(repo/HELPER).read_bytes(),
    }
    for name,data in candidate.items():
        ast.parse(data.decode("utf-8"),filename=name)
        file=folder/"candidate"/name
        file.parent.mkdir(parents=True,exist_ok=True)
        file.write_bytes(data)
    for name,data in original.items():
        file=folder/"before"/name
        file.parent.mkdir(parents=True,exist_ok=True)
        file.write_bytes(data)
    receipt={
        "before":before,
        "status":"PREPARED_NOT_PUBLISHED",
        "original":{p:hash_bytes(s) for p,s in original.items()},
        "candidate":{p:hash_bytes(s) for p,s in candidate.items()},
        "scope":list(CHANGES),
    }
    (folder/"receipt.json").write_text(json.dumps(receipt,indent=2),"utf-8")
    print("SWRLZ_ADAPTIVE_RESEARCH_PREPARED "+json.dumps(receipt),flush=True)
    return receipt


def verify_running(api,rev,seconds=960):
    start=time.monotonic()
    checks=0
    while time.monotonic()-start<seconds:
        if revision(api)!=rev:raise RuntimeError("Concurrent Space revision changed")
        checks+=1
        try:
            with urllib.request.urlopen(urllib.request.Request(
                    "https://huggingface.co/api/spaces/"+SPACE,headers=HEADERS),timeout=18) as response:
                metadata=json.load(response)
            runtime=metadata.get("runtime") or {}
            if runtime.get("stage")=="RUNNING" and runtime.get("sha")==rev:
                with urllib.request.urlopen(urllib.request.Request(
                        BASE+"/api/hf/qwen35-ready",headers=HEADERS),timeout=22) as response:
                    ready=json.load(response)
                if ready.get("ready") is True and ready.get("model")=="qwen3.5-9b":
                    print("SWRLZ_ADAPTIVE_RESEARCH_RUNTIME_MATCH "+
                          json.dumps({"sha":rev,"checks":checks}),flush=True)
                    return
        except (OSError,ValueError):
            pass
        time.sleep(12)
    raise RuntimeError("Running 9B source revision did not match published version")


def guest_turn(prompt,*,expected_research:bool):
    jar=http.cookiejar.CookieJar()
    opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    rid=str(uuid.uuid4())
    body={"modelId":"700m","prompt":prompt,
          "threadId":"swrlz-adaptive-guest-"+str(uuid.uuid4()),
          "requestId":rid,"profileId":"LALM",
          "profile":"","userProfile":"","timeZone":"UTC"}
    request=urllib.request.Request(
        BASE+"/api/lalm_station/send",method="POST",
        data=json.dumps(body).encode(),
        headers={**HEADERS,"Content-Type":"application/json"})
    with opener.open(request,timeout=45) as response:
        if response.status!=202:raise RuntimeError("Guest request was not accepted")
    stream_url=BASE+"/api/lalm_station/stream?"+urllib.parse.urlencode({"requestId":rid})
    start=time.monotonic();pieces=[];phases=[];terminal=""
    with opener.open(urllib.request.Request(stream_url,headers=HEADERS),timeout=360) as stream:
        for row in stream:
            if time.monotonic()-start>340:
                raise RuntimeError("Guest answer exceeded bounded acceptance time")
            try:event=json.loads(row)
            except (TypeError,ValueError):continue
            typ=event.get("type")
            if typ=="STATUS":phases.append(str(event.get("phase") or ""))
            elif typ=="DELTA":pieces.append(str(event.get("text") or ""))
            elif typ in ("COMPLETE","COMPLETED","FAILED","CANCELLED"):
                terminal=typ;break
    answer="".join(pieces)
    report={"terminal":terminal,"chars":len(answer),
            "seconds":round(time.monotonic()-start,2),
            "sourceEvents":sum(p in ("RESEARCH_SOURCE_RETRIEVED",
                                    "RESEARCH_SOURCE_CHECKED") for p in phases),
            "phaseTail":phases[-12:],
            "prefix":answer[:180]}
    print("SWRLZ_ADAPTIVE_RESEARCH_LIVE_CASE "+json.dumps(report),flush=True)
    if terminal not in ("COMPLETE","COMPLETED") or not answer.strip():
        raise RuntimeError("Live response did not complete")
    if expected_research and not report["sourceEvents"]:
        raise RuntimeError("No real sourced research was observable in live answer")
    if not expected_research and report["sourceEvents"]:
        raise RuntimeError("Casual conversation unexpectedly invoked public research")
    return report


def publish(api,folder,receipt):
    if os.environ.get("SWRLZ_ADAPTIVE_PUBLIC_RESEARCH_DEPLOY_APPROVED")!="1":
        raise RuntimeError("Owner release gate missing")
    original=receipt["before"]
    if revision(api)!=original:
        raise RuntimeError("Space moved after preflight: refuse concurrent source overwrite")
    published=str(api.create_commit(
        repo_id=SPACE,repo_type="space",parent_commit=original,
        operations=[
            CommitOperationAdd(path_in_repo=path,
                               path_or_fileobj=str(folder/"candidate"/path))
            for path in CHANGES],
        commit_message="§C: bounded adaptive public research with topic coverage in tagged model context").oid)
    receipt.update({"published":published,"status":"PUBLISHED_NOT_YET_VERIFIED"})
    try:
        if revision(api)!=published:raise RuntimeError("Concurrent publish after commit")
        for path,digest in receipt["candidate"].items():
            if hash_bytes(get_bytes(api,path,published))!=digest:
                raise RuntimeError("Published byte mismatch: "+path)
        verify_running(api,published)
        guest_turn("Explain how eclipses work, including lunar geometry, eclipse types, and eye safety.",
                   expected_research=True)
        guest_turn("What were all the classes in Diablo 2 LoD?",expected_research=True)
        guest_turn("Hello there!",expected_research=False)
        receipt["status"]="LIVE_VERIFIED"
        print("SWRLZ_ADAPTIVE_RESEARCH_LIVE_VERIFIED "+published,flush=True)
    except BaseException:
        print("SWRLZ_ADAPTIVE_RESEARCH_ROLLBACK_ATTEMPT",flush=True)
        if revision(api)!=published:
            raise RuntimeError("Concurrent update prevents safe rollback") from None
        operations=[
            CommitOperationAdd(path_in_repo=path,path_or_fileobj=str(folder/"before"/path))
            for path in (SELECTIVE,ENVELOPE)
        ]
        operations.append(CommitOperationDelete(path_in_repo=HELPER))
        restored=str(api.create_commit(
            repo_id=SPACE,repo_type="space",parent_commit=published,
            operations=operations,
            commit_message="Rollback §C adaptive public research to byte-exact prior source").oid)
        if revision(api)!=restored:raise RuntimeError("Rollback revision mismatch")
        for path,digest in receipt["original"].items():
            if hash_bytes(get_bytes(api,path,restored))!=digest:
                raise RuntimeError("Original source was not restored: "+path)
        receipt.update({"status":"ROLLED_BACK","rollback":restored})
        print("SWRLZ_ADAPTIVE_RESEARCH_ROLLBACK_VERIFIED "+restored,flush=True)
        raise
    finally:
        (folder/"receipt.json").write_text(json.dumps(receipt,indent=2),"utf-8")


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--deploy",action="store_true")
    parser.add_argument("--out",default="swrlz-adaptive-research-rollback")
    args=parser.parse_args()
    token=os.environ.get("HF_TOKEN") or None
    if args.deploy and not token:
        raise RuntimeError("Missing owner Hugging Face release credential")
    api=HfApi(token=token)
    folder=Path(args.out)
    receipt=prepare(api,folder)
    if args.deploy:publish(api,folder,receipt)


if __name__=="__main__":
    main()
