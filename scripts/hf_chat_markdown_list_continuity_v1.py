#!/usr/bin/env python3
"""§C Markdown list continuity fix, exact HF UI source and guarded rollback."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import time
import urllib.request

from huggingface_hub import HfApi,hf_hub_download,CommitOperationAdd

SPACE="kamiloki/Swyrlz"
PATH="chat/§wyrlz/index.html"
BASE="https://kamiloki-swyrlz.hf.space/"
MARKER="swrlz-markdown-list-continuity-v1"
ORIGINAL="            closeList();addParagraph(line);"
NEW=r"""            // swrlz-markdown-list-continuity-v1: CommonMark-style blank lines
            // between items must not produce several ordered lists starting at 1.
            const _nextNonBlank=lines.slice(lineIndex+1).find(part=>part.trim());
            if(!line.trim()){
              const _sameList=!!_nextNonBlank&&(
                (listType==="ol"&&/^\s*\d+[.)]\s+/.test(_nextNonBlank))||
                (listType==="ul"&&/^\s*[-*+]\s+/.test(_nextNonBlank))
              );
              if(_sameList)continue;
              closeList();continue;
            }
            closeList();addParagraph(line);"""


def patched(original: bytes) -> bytes:
    text=original.decode("utf-8")
    if MARKER in text:raise RuntimeError("Already patched")
    if text.count(ORIGINAL)!=1:
        raise RuntimeError("Markdown renderer drift: expected exactly one list-close site")
    for anchor in ('const closeList=()=>{list=null;listType="";};',
                   'const line=rawLine.trimEnd(),heading=',
                   'if(ordered||unordered){const type=ordered?"ol":"ul";'):
        if anchor not in text:
            raise RuntimeError("Markdown parser source anchor drift")
    out=text.replace(ORIGINAL,NEW,1)
    if out.count(MARKER)!=1:raise RuntimeError("Marker duplication")
    return out.encode("utf-8")


def fingerprint(contents:bytes)->str:
    return hashlib.sha256(contents).hexdigest()


def sha(api):
    return api.repo_info(SPACE,repo_type="space").sha


def contents(api,rev):
    return Path(hf_hub_download(SPACE,PATH,revision=rev,
                               repo_type="space",token=api.token)).read_bytes()


def prepare(api,out):
    out.mkdir(parents=True,exist_ok=True)
    rev=sha(api);original=contents(api,rev);candidate=patched(original)
    for label,data in (("before",original),("candidate",candidate)):
        file=out/label/PATH;file.parent.mkdir(parents=True,exist_ok=True)
        file.write_bytes(data)
    receipt={"target":SPACE,"before":rev,"status":"PREPARED_NOT_DEPLOYED",
             "oldSha256":fingerprint(original),"newSha256":fingerprint(candidate)}
    (out/"receipt.json").write_text(json.dumps(receipt,indent=2),"utf-8")
    print("SWRLZ_LISTS_PREPARED "+json.dumps(receipt),flush=True)
    return receipt


def verify(api,commit,seconds=780):
    started=time.monotonic();attempts=0
    while time.monotonic()-started<seconds:
        if sha(api)!=commit:raise RuntimeError("Concurrent HF revision changed")
        attempts+=1
        try:
            with urllib.request.urlopen(urllib.request.Request(
                    "https://huggingface.co/api/spaces/"+SPACE,
                    headers={"Cache-Control":"no-cache"}),timeout=18) as response:
                metadata=json.load(response)
            runtime=metadata.get("runtime") or {}
            if runtime.get("stage")=="RUNNING" and runtime.get("sha")==commit:
                with urllib.request.urlopen(urllib.request.Request(
                        BASE,headers={"Cache-Control":"no-cache"}),
                        timeout=28) as response:
                    served=response.read(2800000).decode("utf-8","replace")
                if MARKER in served:
                    print("SWRLZ_LISTS_UI_LIVE_VERIFIED "+json.dumps(
                        {"revision":commit,"checks":attempts}),flush=True)
                    return
        except (OSError,ValueError):
            pass
        time.sleep(10)
    raise RuntimeError("Exact live UI marker and revision did not become ready")


def release(api,out,receipt):
    if os.environ.get("SWRLZ_LIST_CONTINUITY_DEPLOY_APPROVED")!="1":
        raise RuntimeError("Owner approval gate missing")
    if sha(api)!=receipt["before"]:raise RuntimeError("Space moved after stage")
    published=str(api.create_commit(
        repo_id=SPACE,repo_type="space",parent_commit=receipt["before"],
        operations=[CommitOperationAdd(path_in_repo=PATH,path_or_fileobj=str(out/"candidate"/PATH))],
        commit_message="§C: keep ordered list numbering across blank Markdown lines").oid)
    receipt.update({"published":published,"status":"PUBLISHED_ACCEPTANCE_PENDING"})
    try:
        if sha(api)!=published or fingerprint(contents(api,published))!=receipt["newSha256"]:
            raise RuntimeError("Published UI integrity mismatch")
        verify(api,published)
        receipt["status"]="LIVE_VERIFIED"
        print("SWRLZ_LISTS_PUBLISHED_AND_VERIFIED "+published,flush=True)
    except BaseException:
        if sha(api)!=published:
            raise RuntimeError("Concurrent source moved; rollback unsafe") from None
        restored=str(api.create_commit(
            repo_id=SPACE,repo_type="space",parent_commit=published,
            operations=[CommitOperationAdd(path_in_repo=PATH,
                        path_or_fileobj=str(out/"before"/PATH))],
            commit_message="Rollback §C Markdown continuity to exact original UI").oid)
        if sha(api)!=restored or fingerprint(contents(api,restored))!=receipt["oldSha256"]:
            raise RuntimeError("Original UI restoration integrity mismatch")
        receipt.update({"status":"ROLLED_BACK","rollback":restored})
        print("SWRLZ_LISTS_ROLLED_BACK "+restored,flush=True)
        raise
    finally:
        (out/"receipt.json").write_text(json.dumps(receipt,indent=2),"utf-8")


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--deploy",action="store_true")
    parser.add_argument("--out",default="swrlz-list-continuity-rollback")
    args=parser.parse_args()
    token=os.environ.get("HF_TOKEN") or None
    if args.deploy and not token:raise RuntimeError("HF credential missing")
    api=HfApi(token=token)
    out=Path(args.out);receipt=prepare(api,out)
    if args.deploy:release(api,out,receipt)


if __name__=="__main__":
    main()
