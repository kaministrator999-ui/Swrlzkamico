#!/usr/bin/env python3
"""Guarded §C v3 general public research synthesis release, against exact live HF source.

Only existing HF Space API Python files are changed; no model weights,
hardware, private history, accounts, or §E. Immutable GitHub commit and
runtime revision are verified. On rejection restore byte-exact sources.
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
ENGINE="lfm2_700m_engine.py"
RETRIEVAL="api/selective_retrieval.py"
CONTEXT="api/research_synthesis_v3.py"
CHANGES=(ENGINE,RETRIEVAL,CONTEXT)
MARKER="swrlz-general-evidence-synthesis-v3"
EXPECTED_SELECTIVE_SHA256="5795809bde51de7160dc79753e0ca05dd1f7bc708032e12d6395c09ed691f1ae"
HEADERS={"User-Agent":"SWRLZ-Research-Context-v2/1","Cache-Control":"no-cache"}

WRAPPER=r'''
# swrlz-general-evidence-synthesis-v3
# Preserve source facts; let the model write a natural answer; check prior to display.
_swrlz_previous_generate_events_research_v3=generate_events


def generate_events(payload):
    if (not isinstance(payload,dict) or os.environ.get(
        "SWRLZ_GENERAL_RESEARCH_SYNTHESIS_V3_ENABLED","1").strip().lower() in ("0","false","off")
            or os.environ.get("SWRLZ_SELECTIVE_RETRIEVAL_ENABLED","1").strip().lower() in ("0","false","off")):
        yield from _swrlz_previous_generate_events_research_v3(payload)
        return
    from api.selective_retrieval import choose_retrieval as _choose_v3, enrich_payload as _enrich_v3
    from api.research_context_v2 import request_scope as _scope_v3
    from api.research_synthesis_v3 import (
        source_ledger as _ledger_v3,
        validate_roster_answer as _validate_v3,
        repair_repeated_one_lists as _repair_lists_v3,
        fallback_from_verified_facts as _fallback_v3,
        source_links as _links_v3,
        strip_generated_links as _strip_links_v3,
    )
    prompt=str(payload.get("prompt") or "")
    decision=_choose_v3(
        prompt,
        has_evidence=bool(payload.get("onlineContext")),
        has_attachment=bool(payload.get("attachments") or payload.get("uploadedFiles")
                            or payload.get("imageEvidence")),
        source_change=bool(payload.get("githubSourceChangeTask")
                           or payload.get("codingTask")
                           or payload.get("sourceChangeIdentity")
                           or payload.get("nativeEditorEvidence")),
        private_context=bool(payload.get("privateResearchContext")),
    )
    scope=_scope_v3(prompt)
    if (decision.action!="retrieve" or scope.get("rosterQuestion")!="yes"
            or scope.get("scope") not in ("original","expansion")):
        yield from _swrlz_previous_generate_events_research_v3(payload)
        return
    from api.online_research import research as _research_v3, _page_fetch as _safe_fetch_v3
    try:
        enriched,route=_enrich_v3(payload,_research_v3,
                                  fetch_page=_safe_fetch_v3,enabled=True)
    except Exception:
        yield from _swrlz_previous_generate_events_research_v3(payload)
        return
    facts=(enriched.get("onlineContext") or {}).get("verifiedContext")
    if not isinstance(facts,dict):
        yield {"type":"STATUS","phase":"RESEARCH_CONTEXT_INSUFFICIENT",
               "reason":"No independently confirmed full roster was available"}
        yield {"type":"DELTA","text":"I couldn't confirm the complete roster from the available original sources. I won't invent names or counts."}
        yield {"type":"COMPLETED","phase":"COMPLETE",
               "verification":"INSUFFICIENT_PUBLIC_RESEARCH_EVIDENCE"}
        return
    evidence=enriched["onlineContext"]
    ledger=_ledger_v3(prompt,evidence)
    enriched["researchSynthesisV3"]={"enabled":True}
    yield {"type":"STATUS","phase":"RESEARCH_READY",
           "reason":"Retrieved separate original and expansion source passages"}
    yield {"type":"STATUS","phase":"RESEARCH_SYNTHESIS",
           "reason":"Using documented facts and recent conversation context to explain the findings"}
    parts=[]
    completed=False
    # The old v1 verifier understands dates but not roster membership.
    # Collect the core model draft once; then apply BOTH validators to that
    # same candidate, rather than letting the old guard discard it first.
    for event in _swrlz_original_generate_events_factual_v1(enriched):
        if not isinstance(event,dict):
            yield event
            continue
        kind=str(event.get("type") or "").upper()
        if kind=="DELTA":
            parts.append(str(event.get("text") or ""))
            continue
        if kind in ("COMPLETED","COMPLETE"):
            completed=True
            break
        if kind in ("FAILED","CANCELLED"):
            break
        if str(event.get("phase") or "") not in (
                "FACTUAL_VERIFICATION_PASS","GROUNDED_SOURCE_REPAIR","SOURCE_ONLY_FALLBACK"):
            yield event
    candidate=_repair_lists_v3(_strip_links_v3("".join(parts)))
    verdict=_validate_v3(candidate,facts,ledger) if completed else {
        "status":"REJECT","reasons":["model_generation_incomplete"]}
    from api.factual_claim_guard_v1 import inspect_answer as _date_checks_v3
    cards=evidence.get("evidence") or []
    # Existing date and Act checks need to see the separate original and
    # expansion release cards even when seven detail pages are also present.
    chronological=sorted(cards,key=lambda card:
        1 if str(card.get("title") or "").endswith(("release dates","expansion date")) else 0,
        reverse=True)
    date_verdict=_date_checks_v3(candidate,{
        "evidence":chronological,"resultCount":len(chronological)})
    if date_verdict["status"]!="PASS":
        verdict={"status":"REJECT",
                 "reasons":verdict.get("reasons",[])+date_verdict.get("reasons",[])}
    if verdict["status"]=="PASS":
        yield {"type":"STATUS","phase":"RESEARCH_NARRATIVE_ACCEPTED",
               "reason":"Narrative passed source roster membership and description-support checks"}
        yield {"type":"DELTA","text":candidate+_links_v3(ledger)}
        yield {"type":"COMPLETED","phase":"COMPLETE",
               "verification":"EVIDENCE_BOUND_NARRATIVE","modelDraftAccepted":True}
        return
    yield {"type":"STATUS","phase":"RESEARCH_NARRATIVE_REJECTED",
           "reason":",".join(verdict.get("reasons",[]))[:200]}
    yield {"type":"STATUS","phase":"RESEARCH_EVIDENCE_FALLBACK",
           "reason":"Showing grouped publisher-backed facts instead of an unsupported draft"}
    yield {"type":"DELTA","text":_fallback_v3(facts,ledger)}
    yield {"type":"COMPLETED","phase":"COMPLETE",
           "verification":"EVIDENCE_COMPOSED_FALLBACK","modelDraftAccepted":False}

'''



TRUSTED_RESEARCH_POLICY=r'''    # public-source narrative policy injected by guarded release
    if (isinstance(payload.get("onlineContext"),dict)
            and payload["onlineContext"].get("resultCount")
            and not programming.get("codingTask") and not source_change_mode):
        from api.research_synthesis_v3 import instruction_for_synthesis
        facts=payload["onlineContext"].get("verifiedContext")
        system+="\n"+instruction_for_synthesis(facts)
'''


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def guarded_engine_patch(before: bytes) -> bytes:
    text=before.decode("utf-8")
    if MARKER in text:raise RuntimeError("V2 research extension already installed")
    for marker in (
        "swrlz-verified-public-enumerations-v2",
        "swrlz-evidence-checked-factual-response-v1",
        "swrlz-research-answer-limit-recovery-v1",
        "swrlz-selective-factual-retrieval-v1",
    ):
        if marker not in text:raise RuntimeError("Missing live engine lineage marker: "+marker)
    if "def generate_events(payload):" not in text:
        raise RuntimeError("Missing live generate_events entrypoint")
    injection='    if source_change_mode:\n        # Keep source/plan tokens available'
    if text.count(injection)!=1:
        raise RuntimeError("Engine source policy placement drift")
    text=text.replace(injection,TRUSTED_RESEARCH_POLICY+injection,1)
    candidate=text.rstrip()+"\n"+WRAPPER+"\n"
    ast.parse(candidate,filename=ENGINE)
    if candidate.count(MARKER)!=1:raise RuntimeError("Source marker duplicate")
    return candidate.encode("utf-8")


def head(api):
    return api.repo_info(SPACE,repo_type="space").sha


def live_bytes(api,path,rev):
    return Path(hf_hub_download(SPACE,path,repo_type="space",
                               revision=rev,token=api.token)).read_bytes()


def build_candidate(api,out:Path):
    out.mkdir(parents=True,exist_ok=True)
    rev=head(api)
    names=set(api.list_repo_files(SPACE,repo_type="space",revision=rev))
    if CONTEXT in names:raise RuntimeError("New context module path already exists")
    before={ENGINE:live_bytes(api,ENGINE,rev),
            RETRIEVAL:live_bytes(api,RETRIEVAL,rev)}
    if sha256(before[RETRIEVAL])!=EXPECTED_SELECTIVE_SHA256:
        raise RuntimeError("Live selective retrieval diverged; do not overwrite concurrent work")
    root=Path(__file__).resolve().parents[1]
    after={ENGINE:guarded_engine_patch(before[ENGINE]),
           RETRIEVAL:(root/RETRIEVAL).read_bytes(),
           CONTEXT:(root/CONTEXT).read_bytes()}
    for path,data in after.items():
        ast.parse(data.decode("utf-8"),filename=path)
        target=out/"candidate"/path
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(data)
    for path,data in before.items():
        target=out/"before"/path
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(data)
    receipt={"space":SPACE,"before":rev,"status":"PREPARED_NOT_PUBLISHED",
             "original":{k:sha256(v) for k,v in before.items()},
             "candidate":{k:sha256(v) for k,v in after.items()}}
    (out/"receipt.json").write_text(json.dumps(receipt,indent=2),"utf-8")
    print("SWRLZ_RESEARCH_V3_PREPARED "+json.dumps(receipt),flush=True)
    return receipt


def verify_running(api,rev,seconds=950):
    started=time.monotonic()
    attempts=0
    while time.monotonic()-started<seconds:
        if head(api)!=rev:raise RuntimeError("Concurrent Space revision changed")
        attempts+=1
        try:
            req=urllib.request.Request("https://huggingface.co/api/spaces/"+SPACE,headers=HEADERS)
            with urllib.request.urlopen(req,timeout=14) as response:
                metadata=json.load(response)
            runtime=metadata.get("runtime") or {}
            if runtime.get("stage")=="RUNNING" and runtime.get("sha")==rev:
                with urllib.request.urlopen(
                    urllib.request.Request(BASE+"/api/hf/qwen35-ready",headers=HEADERS),
                    timeout=22) as response:
                    status=json.load(response)
                if status.get("model")=="qwen3.5-9b" and status.get("ready") is True:
                    print("SWRLZ_RESEARCH_V3_RUNTIME_MATCH "+json.dumps(
                        {"sha":rev,"checks":attempts}),flush=True)
                    return
        except (ValueError,OSError):
            pass
        if attempts%7==0:
            print("SWRLZ_RESEARCH_V3_RUNTIME_WARMING "+str(attempts),flush=True)
        time.sleep(12)
    raise RuntimeError("Live exact revision never reached ready stage")


def accepts_natural_count_wording(answer: str, expected_count: int) -> bool:
    words={5:"five",7:"seven"}
    count_tokens=(str(expected_count),words.get(expected_count,""))
    return any(re.search(r"\b"+re.escape(part)+r"\b",str(answer or ""),re.I)
               for part in count_tokens if part)


def ask(prompt,expected_count,expected_names,forbidden,expected_years=()):
    jar=http.cookiejar.CookieJar()
    opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    rid=str(uuid.uuid4())
    tid="swrlz-research-v3-guest-eval-"+str(uuid.uuid4())
    body={"modelId":"700m","prompt":prompt,"threadId":tid,"requestId":rid,
          "profileId":"LALM","profile":"","userProfile":"","timeZone":"UTC"}
    req=urllib.request.Request(BASE+"/api/lalm_station/send",method="POST",
        data=json.dumps(body).encode(),headers={**HEADERS,"Content-Type":"application/json"})
    with opener.open(req,timeout=45) as response:
        if response.status!=202:raise RuntimeError("Guest request did not enter Station")
    parts=[];phases=[];reasons=[];terminal="";started=time.monotonic()
    url=BASE+"/api/lalm_station/stream?"+urllib.parse.urlencode({"requestId":rid})
    with opener.open(urllib.request.Request(url,headers=HEADERS),timeout=320) as stream:
        for row in stream:
            if time.monotonic()-started>315:raise RuntimeError("Live response exceeded safety time budget")
            try:entry=json.loads(row)
            except ValueError:continue
            typ=entry.get("type")
            if typ=="STATUS":
                phase=str(entry.get("phase") or "")
                phases.append(phase)
                if phase in ("RESEARCH_NARRATIVE_REJECTED","FACTUAL_VERIFICATION_REJECT"):
                    reasons.append(str(entry.get("reason") or "")[:240])
            elif typ=="DELTA":parts.append(str(entry.get("text") or ""))
            elif typ in ("COMPLETE","COMPLETED","FAILED","CANCELLED"):
                terminal=typ;break
    answer="".join(parts)
    low=answer.lower()
    meta={"terminal":terminal,"chars":len(answer),"elapsed":round(time.monotonic()-started,2),
          "status":phases[-12:],"prefix":answer[:240],
          "modelNarrativeAccepted":"RESEARCH_NARRATIVE_ACCEPTED" in phases,
          "sourceFallback":"RESEARCH_EVIDENCE_FALLBACK" in phases,
          "rejectionReasons":reasons[-3:]}
    print("SWRLZ_RESEARCH_V3_LIVE_CASE "+json.dumps(meta),flush=True)
    if terminal not in ("COMPLETE","COMPLETED"):
        raise RuntimeError("Live request did not complete")
    if expected_count is not None:
        if not ("RESEARCH_NARRATIVE_ACCEPTED" in phases or
                "RESEARCH_EVIDENCE_FALLBACK" in phases):
            raise RuntimeError("Source-grounded roster response route missing")
        # The server's verified roster gate already checks the actual list.
        # Natural prose may express 7 as "seven" or "total to seven";
        # do not require a literal canned phrase in the acceptance harness.
        if not accepts_natural_count_wording(answer,expected_count):
            raise RuntimeError("Expected class count was absent in number and words")
        for name in expected_names:
            if not re.search(r"\b"+re.escape(name)+r"\b",answer,re.I):
                raise RuntimeError("Verified roster missing "+name)
        for name in forbidden:
            if re.search(r"(?m)^\s*(?:[-*]|\d{1,2}[.)])\s+\*{0,2}"
                         +re.escape(name)+r"\b",answer,re.I):
                raise RuntimeError("Historic roster contains invented listed member "+name)
        if len(answer)<120:raise RuntimeError("Answer too short to be useful")
    else:
        # Non-roster requests must never capture the historical roster path.
        if "RESEARCH_CONTEXT_CHECK" in phases:
            raise RuntimeError("Unrelated chat inappropriately entered historical class research")
        if expected_years:
            years=set(re.findall(r"(?<!\d)(?:19|20)\d{2}(?!\d)",answer))
            if not set(expected_years).issubset(years):
                raise RuntimeError("Existing release-date research lost its chronology")
            if years.intersection({"2023","2024"}):
                raise RuntimeError("Existing release-date research again invented remaster dates")
            if "FACTUAL_VERIFICATION_PASS" not in phases:
                raise RuntimeError("The existing source-grounding claim guard was not exercised")
    return meta


def release(api,out,receipt):
    if os.environ.get("SWRLZ_GENERAL_RESEARCH_SYNTHESIS_V3_DEPLOY_APPROVED")!="1":
        raise RuntimeError("Owner gate required")
    previous=receipt["before"]
    if head(api)!=previous:raise RuntimeError("Space changed after preflight")
    result=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=previous,
        operations=[CommitOperationAdd(path_in_repo=p,
                    path_or_fileobj=str(out/"candidate"/p)) for p in CHANGES],
        commit_message="§C: reusable source-ledger research and validated natural explanations")
    published=str(result.oid)
    receipt.update({"published":published,"status":"PUBLISHED_UNVERIFIED"})
    try:
        if head(api)!=published:raise RuntimeError("Concurrent Space update after publication")
        for path,digest in receipt["candidate"].items():
            if sha256(live_bytes(api,path,published))!=digest:
                raise RuntimeError("Published bytes did not match for "+path)
        verify_running(api,published)
        answers=[]
        answers.append(ask("What were all the classes in Diablo 2 LoD? Give a short, source-supported description for each.",7,
            ["Amazon","Barbarian","Paladin","Necromancer","Sorceress","Assassin","Druid"],
            ["Rogue","Warlock"]))
        answers.append(ask("So what were all the classes in Diablo 2 LoD?",7,
            ["Amazon","Barbarian","Paladin","Necromancer","Sorceress","Assassin","Druid"],
            ["Rogue","Warlock"]))
        answers.append(ask("What were all five classes in Diablo 2 Classic?",5,
            ["Amazon","Barbarian","Paladin","Necromancer","Sorceress"],
            ["Assassin","Druid","Rogue","Warlock"]))
        if not any(item["modelNarrativeAccepted"] for item in answers):
            raise RuntimeError("No model-composed factual answer passed verification; the old canned-response problem remains")
        ask("Was Diablo II Classic released before Lord of Destruction? Research both versions and explain the differences.",
            None,[],[],expected_years=("2000","2001"))
        ask("Hello there!",None,[],[])
        receipt["status"]="LIVE_VERIFIED"
        print("SWRLZ_RESEARCH_V3_LIVE_VERIFIED "+json.dumps(
            {"sha":published,"cases":5,"naturalAnswers":sum(item["modelNarrativeAccepted"] for item in answers)}),flush=True)
    except BaseException:
        print("SWRLZ_RESEARCH_V3_ROLLBACK_ATTEMPT",flush=True)
        if head(api)!=published:
            raise RuntimeError("Concurrent change prevents safe rollback") from None
        ops=[CommitOperationAdd(path_in_repo=p,path_or_fileobj=str(out/"before"/p))
             for p in (ENGINE,RETRIEVAL)]
        ops.append(CommitOperationDelete(path_in_repo=CONTEXT))
        back=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=published,
            operations=ops,
            commit_message="Rollback §C research synthesis v3 to exact original sources")
        rollback=str(back.oid)
        if head(api)!=rollback:raise RuntimeError("Rollback revision mismatch")
        for path,digest in receipt["original"].items():
            if sha256(live_bytes(api,path,rollback))!=digest:
                raise RuntimeError("Rollback source integrity failure for "+path)
        receipt.update({"status":"ROLLED_BACK","rollback":rollback})
        print("SWRLZ_RESEARCH_V3_ROLLBACK_VERIFIED "+rollback,flush=True)
        raise
    finally:
        (out/"receipt.json").write_text(json.dumps(receipt,indent=2),"utf-8")


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--deploy",action="store_true")
    parser.add_argument("--out",default="swrlz-research-v3-rollback")
    args=parser.parse_args()
    token=os.environ.get("HF_TOKEN") or None
    if args.deploy and not token:raise RuntimeError("No owner HF release credential")
    api=HfApi(token=token)
    out=Path(args.out)
    receipt=build_candidate(api,out)
    if args.deploy:release(api,out,receipt)


if __name__=="__main__":
    main()
