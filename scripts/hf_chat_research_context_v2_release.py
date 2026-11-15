#!/usr/bin/env python3
"""Guarded §C v2 research-context deployment, against exact live HF source.

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
CONTEXT="api/research_context_v2.py"
CHANGES=(ENGINE,RETRIEVAL,CONTEXT)
MARKER="swrlz-verified-public-enumerations-v2"
EXPECTED_SELECTIVE_SHA256="a8003722e70a1f1762d4dde35996c371d6889136308d5411a2c6e26fb66afd69"
HEADERS={"User-Agent":"SWRLZ-Research-Context-v2/1","Cache-Control":"no-cache"}

WRAPPER=r'''

# swrlz-verified-public-enumerations-v2
# The model's factual-answer path remains intact for non-roster questions.
# The exact historical edition/class roster path is source-extracted and
# checked before display; no user-private data, tool execution or weights.
_swrlz_previous_generate_events_research_v2=generate_events


def generate_events(payload):
    if not isinstance(payload,dict) or os.environ.get(
        "SWRLZ_RESEARCH_CONTEXT_V2_ENABLED","1").strip().lower() in ("0","false","off"):
        yield from _swrlz_previous_generate_events_research_v2(payload)
        return
    from api.research_context_v2 import (
        request_scope as _research_scope_v2,
        grounded_roster_reply as _research_roster_reply_v2,
    )
    from api.selective_retrieval import (
        choose_retrieval as _research_route_v2,
        enrich_payload as _enrich_public_v2,
    )
    prompt=str(payload.get("prompt") or "")
    decision=_research_route_v2(
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
    intent=_research_scope_v2(prompt)
    if (decision.action!="retrieve" or intent.get("rosterQuestion")!="yes"
            or intent.get("scope") not in ("original","expansion")):
        yield from _swrlz_previous_generate_events_research_v2(payload)
        return
    from api.online_research import research as _research_v2, _page_fetch as _safe_page_fetch_v2
    try:
        enriched,route=_enrich_public_v2(payload,_research_v2,
                                         fetch_page=_safe_page_fetch_v2,enabled=True)
    except Exception:
        yield from _swrlz_previous_generate_events_research_v2(payload)
        return
    if route.get("phase")!="RESEARCH_READY":
        yield {"type":"STATUS","phase":"RESEARCH_UNAVAILABLE",
               "reason":"No verified historical roster sources were available"}
        yield {"type":"DELTA","text":"I couldn't verify a complete class roster from primary sources, so I won't invent a count or class names."}
        yield {"type":"COMPLETED","phase":"COMPLETE",
               "verification":"INSUFFICIENT_PUBLIC_ROSTER_EVIDENCE"}
        return
    bundle=enriched.get("onlineContext") or {}
    yield {"type":"STATUS","phase":"RESEARCH_READY",
           "reason":"Retrieved edition-specific public research sources"}
    yield {"type":"STATUS","phase":"RESEARCH_CONTEXT_CHECK",
           "reason":"Matching named classes and counts to primary sources for the requested edition"}
    response=_research_roster_reply_v2(prompt,bundle)
    if response and bundle.get("verifiedContext"):
        yield {"type":"STATUS","phase":"FACTUAL_VERIFICATION_PASS",
               "reason":"Confirmed the class names, original/expansion ownership, and total count against separate sources"}
        yield {"type":"DELTA","text":response}
        yield {"type":"COMPLETED","phase":"COMPLETE",
               "verification":"PRIMARY_SOURCE_ROSTER",
               "sourceCount":len(bundle.get("verifiedContext",{}).get("evidence",[]))}
        return
    yield {"type":"STATUS","phase":"RESEARCH_CONTEXT_INSUFFICIENT",
           "reason":"Public results were relevant but did not establish a complete edition-specific roster"}
    yield {"type":"DELTA","text":"I found references, but they don't establish the complete class roster for the requested edition. I won't guess at the names or total. Please try again after the sources become available."}
    yield {"type":"COMPLETED","phase":"COMPLETE",
           "verification":"INSUFFICIENT_PUBLIC_ROSTER_EVIDENCE"}
'''


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def guarded_engine_patch(before: bytes) -> bytes:
    text=before.decode("utf-8")
    if MARKER in text:raise RuntimeError("V2 research extension already installed")
    for marker in (
        "swrlz-evidence-checked-factual-response-v1",
        "swrlz-research-answer-limit-recovery-v1",
        "swrlz-selective-factual-retrieval-v1",
    ):
        if marker not in text:raise RuntimeError("Missing live engine lineage marker: "+marker)
    if "def generate_events(payload):" not in text:
        raise RuntimeError("Missing live generate_events entrypoint")
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
    print("SWRLZ_RESEARCH_V2_PREPARED "+json.dumps(receipt),flush=True)
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
                    print("SWRLZ_RESEARCH_V2_RUNTIME_MATCH "+json.dumps(
                        {"sha":rev,"checks":attempts}),flush=True)
                    return
        except (ValueError,OSError):
            pass
        if attempts%7==0:
            print("SWRLZ_RESEARCH_V2_RUNTIME_WARMING "+str(attempts),flush=True)
        time.sleep(12)
    raise RuntimeError("Live exact revision never reached ready stage")


def ask(prompt,expected_count,expected_names,forbidden):
    jar=http.cookiejar.CookieJar()
    opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    rid=str(uuid.uuid4())
    tid="swrlz-research-v2-guest-eval-"+str(uuid.uuid4())
    body={"modelId":"700m","prompt":prompt,"threadId":tid,"requestId":rid,
          "profileId":"LALM","profile":"","userProfile":"","timeZone":"UTC"}
    req=urllib.request.Request(BASE+"/api/lalm_station/send",method="POST",
        data=json.dumps(body).encode(),headers={**HEADERS,"Content-Type":"application/json"})
    with opener.open(req,timeout=45) as response:
        if response.status!=202:raise RuntimeError("Guest request did not enter Station")
    parts=[];phases=[];terminal="";started=time.monotonic()
    url=BASE+"/api/lalm_station/stream?"+urllib.parse.urlencode({"requestId":rid})
    with opener.open(urllib.request.Request(url,headers=HEADERS),timeout=320) as stream:
        for row in stream:
            if time.monotonic()-started>315:raise RuntimeError("Live response exceeded safety time budget")
            try:entry=json.loads(row)
            except ValueError:continue
            typ=entry.get("type")
            if typ=="STATUS":phases.append(str(entry.get("phase") or ""))
            elif typ=="DELTA":parts.append(str(entry.get("text") or ""))
            elif typ in ("COMPLETE","COMPLETED","FAILED","CANCELLED"):
                terminal=typ;break
    answer="".join(parts)
    low=answer.lower()
    meta={"terminal":terminal,"chars":len(answer),"elapsed":round(time.monotonic()-started,2),
          "status":phases[-12:],"prefix":answer[:240]}
    print("SWRLZ_RESEARCH_V2_LIVE_CASE "+json.dumps(meta),flush=True)
    if terminal not in ("COMPLETE","COMPLETED"):
        raise RuntimeError("Live request did not complete")
    if expected_count is not None:
        if "FACTUAL_VERIFICATION_PASS" not in phases:
            raise RuntimeError("Live request missing verified roster evidence")
        if str(expected_count)+" playable classes" not in answer:
            raise RuntimeError("The expected class count was not returned")
        for name in expected_names:
            if not re.search(r"\b"+re.escape(name)+r"\b",answer,re.I):
                raise RuntimeError("Verified roster missing "+name)
        for name in forbidden:
            if re.search(r"\b"+re.escape(name)+r"\b",answer,re.I):
                raise RuntimeError("Historic roster contains invented "+name)
        if len(answer)<120:raise RuntimeError("Answer too short to be useful")
    else:
        # An ordinary chat must not suddenly spawn historical roster research.
        if "RESEARCH_CONTEXT_CHECK" in phases:
            raise RuntimeError("Casual chat inappropriately entered historical research route")
    return meta


def release(api,out,receipt):
    if os.environ.get("SWRLZ_RESEARCH_CONTEXT_V2_DEPLOY_APPROVED")!="1":
        raise RuntimeError("Owner gate required")
    previous=receipt["before"]
    if head(api)!=previous:raise RuntimeError("Space changed after preflight")
    result=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=previous,
        operations=[CommitOperationAdd(path_in_repo=p,
                    path_or_fileobj=str(out/"candidate"/p)) for p in CHANGES],
        commit_message="§C: evidence-scoped factual research context and verified class rosters")
    published=str(result.oid)
    receipt.update({"published":published,"status":"PUBLISHED_UNVERIFIED"})
    try:
        if head(api)!=published:raise RuntimeError("Concurrent Space update after publication")
        for path,digest in receipt["candidate"].items():
            if sha256(live_bytes(api,path,published))!=digest:
                raise RuntimeError("Published bytes did not match for "+path)
        verify_running(api,published)
        ask("What were all the classes in Diablo 2 LoD?",7,
            ["Amazon","Barbarian","Paladin","Necromancer","Sorceress","Assassin","Druid"],
            ["Rogue","Warlock"])
        ask("What were all five classes in Diablo 2 Classic?",5,
            ["Amazon","Barbarian","Paladin","Necromancer","Sorceress"],
            ["Assassin","Druid","Rogue","Warlock"])
        ask("Hello there!",None,[],[])
        receipt["status"]="LIVE_VERIFIED"
        print("SWRLZ_RESEARCH_V2_LIVE_VERIFIED "+json.dumps(
            {"sha":published,"cases":3}),flush=True)
    except BaseException:
        print("SWRLZ_RESEARCH_V2_ROLLBACK_ATTEMPT",flush=True)
        if head(api)!=published:
            raise RuntimeError("Concurrent change prevents safe rollback") from None
        ops=[CommitOperationAdd(path_in_repo=p,path_or_fileobj=str(out/"before"/p))
             for p in (ENGINE,RETRIEVAL)]
        ops.append(CommitOperationDelete(path_in_repo=CONTEXT))
        back=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=published,
            operations=ops,
            commit_message="Rollback §C public factual research-context v2 to exact original sources")
        rollback=str(back.oid)
        if head(api)!=rollback:raise RuntimeError("Rollback revision mismatch")
        for path,digest in receipt["original"].items():
            if sha256(live_bytes(api,path,rollback))!=digest:
                raise RuntimeError("Rollback source integrity failure for "+path)
        receipt.update({"status":"ROLLED_BACK","rollback":rollback})
        print("SWRLZ_RESEARCH_V2_ROLLBACK_VERIFIED "+rollback,flush=True)
        raise
    finally:
        (out/"receipt.json").write_text(json.dumps(receipt,indent=2),"utf-8")


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--deploy",action="store_true")
    parser.add_argument("--out",default="swrlz-research-v2-rollback")
    args=parser.parse_args()
    token=os.environ.get("HF_TOKEN") or None
    if args.deploy and not token:raise RuntimeError("No owner HF release credential")
    api=HfApi(token=token)
    out=Path(args.out)
    receipt=build_candidate(api,out)
    if args.deploy:release(api,out,receipt)


if __name__=="__main__":
    main()
