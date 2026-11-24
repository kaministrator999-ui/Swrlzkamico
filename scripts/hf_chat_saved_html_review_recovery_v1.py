#!/usr/bin/env python3
"""Repair §C project review placement and resume previously saved HTML source.

A trusted user turn asks to review the canonical thread-owned codeArtifact.
This installs no new automatic write permission. It creates only a same-thread
GitHub creation proposal and preserves the separate deployment approval.
"""
from __future__ import annotations
import argparse,ast,hashlib,io,os,time,urllib.request
from pathlib import Path

SPACE="kamiloki/Swyrlz"
BASE="https://kamiloki-swyrlz.hf.space"
STATION="station.py"
HTML="chat/§wyrlz/index.html"
HANDOFF="github_html_project_handoff_v1.py"
SOURCE=Path("api/github_html_project_handoff_v1.py")
FILES=(STATION,HTML,HANDOFF)
MARK="# swrlz-saved-html-review-recovery-v1"
RESUME_ROUTE_ANCHOR='''    elif payload.get("htmlProjectIntent"):
        # Generate first; only a verified, saved code artifact can be reviewed.
        pass'''
RESUME_ROUTE_REPLACE='''    elif payload.get("htmlProjectIntent"):
        # Generate first; only a verified, saved code artifact can be reviewed.
        pass
    elif _swrlz_html_handoff.is_saved_review_request(prompt):
        # This is the saved source, not a model re-creation or a GitHub write.
        saved_artifact=next(
            (a for a in reversed(t.get("codeArtifacts") or [])
             if isinstance(a,dict) and a.get("type")=="code" and
                any(isinstance(f,dict) and f.get("path")=="index.html"
                    for f in (a.get("files") or []))),None)
        if not google_owner.startswith("google:"):
            payload["verifiedHtmlReview"]={"text":"Sign in with Google to review saved HTML for GitHub. Nothing published."}
        elif saved_artifact is None:
            payload["verifiedHtmlReview"]={"text":"No saved HTML code artifact was found in this conversation. Nothing created or deployed."}
        else:
            try:
                saved_review=_swrlz_html_handoff.stage(
                    google_owner,tid,saved_artifact,
                    {"kind":"html-project-generate-and-publish","requestedSlug":""})
                payload["verifiedHtmlReview"]={"widget":saved_review,
                    "text":"Review the saved HTML project "+
                    str(saved_review["data"]["project"])+
                    " at artifact revision "+str(saved_review["data"]["artifactRevision"])+
                    ". This proposal creates no files until you approve it. "
                    "Deployment requires a second approval."}
            except _swrlz_html_handoff.HandoffError as exc:
                payload["verifiedHtmlReview"]={"text":"Saved HTML review unavailable ("+
                    exc.code+"). Nothing created or deployed."}'''
RUN_ANCHOR='''        elif payload.get("verifiedPrivateAnswer"):
            event_source=iter(({"type":"DELTA","text":payload["verifiedPrivateAnswer"]},{"type":"COMPLETE"}))'''
RUN_REPLACE='''        elif isinstance(payload.get("verifiedHtmlReview"),dict):
            # swrlz-saved-html-review-recovery-v1: no model hallucinations.
            reviewed=payload["verifiedHtmlReview"]
            events=[{"type":"STATUS","phase":"SAVED_HTML_REVIEW",
                     "reason":"Account-owned source; explicit owner approval required."}]
            if isinstance(reviewed.get("widget"),dict):
                events.append({"type":"WIDGET","widget":reviewed["widget"]})
            events.extend(({"type":"DELTA","text":str(reviewed.get("text") or "")},
                           {"type":"COMPLETED","phase":"COMPLETE"}))
            event_source=iter(events)
        elif payload.get("verifiedPrivateAnswer"):
            event_source=iter(({"type":"DELTA","text":payload["verifiedPrivateAnswer"]},{"type":"COMPLETE"}))'''
UI_ANCHOR='''        if(status)status.before(stack);else if(body)body.before(stack);else node.appendChild(stack);'''
UI_REPLACE='''        // Put GitHub creation approval directly after generated or saved code.
        // Other informational widgets retain their existing widget-first order.
        const createReview=normalized.some(item=>item.kind==="github-html-publish-review"&&item.data?.mode==="create");
        if(createReview&&body)body.after(stack);
        else if(status)status.before(stack);else if(body)body.before(stack);else node.appendChild(stack);'''


def one(s,old,new,label):
    n=s.count(old)
    if n!=1:raise RuntimeError("SOURCE_DRIFT_"+label+" occurrences="+str(n))
    return s.replace(old,new,1)


def patch(original):
    station=original[STATION].decode()
    html=original[HTML].decode()
    if MARK in station or "swrlz-html-review-scroll-repair-v1" not in html:
        raise RuntimeError("LIVE_FIRST_REPAIR_NOT_FOUND_OR_REAPPLIED")
    station=one(station,RESUME_ROUTE_ANCHOR,RESUME_ROUTE_REPLACE,"SAVED_REVIEW_ROUTING")
    station=one(station,RUN_ANCHOR,RUN_REPLACE,"SAVED_REVIEW_EVENT_DISPATCH")
    station=one(station,'payload.get("verifiedPrivateAnswer") or',
                'payload.get("verifiedPrivateAnswer") or payload.get("verifiedHtmlReview") or',
                "STOCK_MODEL_SAFE_DISPATCH")
    station=station.replace('''import github_html_project_handoff_v1 as _swrlz_html_handoff''',
        '''import github_html_project_handoff_v1 as _swrlz_html_handoff
'''+MARK,1)
    html=one(html,UI_ANCHOR,UI_REPLACE,"REVIEW_AFTER_CODE")
    ast.parse(station,filename=STATION)
    if "is_saved_review_request" not in SOURCE.read_text():
        raise RuntimeError("SAVED_REVIEW_COMMAND_NOT_AVAILABLE")
    ast.parse(SOURCE.read_text(),filename=HANDOFF)
    return {STATION:station.encode(),HTML:html.encode(),HANDOFF:SOURCE.read_bytes()}


def local():
    ast.parse(SOURCE.read_text(),filename=HANDOFF)
    import re
    assert re.search(r"is_saved_review_request",SOURCE.read_text())
    print("SAVED_HTML_REVIEW_RECOVERY_SOURCE_PASS",flush=True)


def live_probe():
    with urllib.request.urlopen(BASE+"/chat/%C2%A7wyrlz?__html_saved_review=1",timeout=20) as r:
        page=r.read(3_000_000).decode("utf-8",errors="replace")
        if r.status!=200 or "const createReview=normalized.some" not in page:
            raise RuntimeError("Live HTML creation review is not placed below code")
    print("SAVED_HTML_REVIEW_LIVE_PLACEMENT_VERIFIED",flush=True)


def main(mode):
    local()
    if mode=="selftest":return
    from huggingface_hub import HfApi,hf_hub_download,CommitOperationAdd
    token=os.getenv("HF_TOKEN") or None
    api=HfApi(token=token)
    rev=str(api.repo_info(SPACE,repo_type="space").sha)
    original={p:Path(hf_hub_download(SPACE,p,repo_type="space",revision=rev,token=token)).read_bytes() for p in FILES}
    updated=patch(original)
    print("SAVED_HTML_REVIEW_PREFLIGHT",rev,
          {p:hashlib.sha256(data).hexdigest() for p,data in updated.items()},flush=True)
    if mode=="preflight":return
    if mode!="publish" or not token or os.getenv("SWRLZ_SAVED_HTML_REVIEW_APPROVED")!="1":
        raise PermissionError("RELEASE_NOT_OWNER_APPROVED")
    if str(api.repo_info(SPACE,repo_type="space").sha)!=rev:
        raise RuntimeError("CONCURRENT_SPACE_WRITE")
    newrev=api.create_commit(
        repo_id=SPACE,repo_type="space",parent_commit=rev,
        operations=[CommitOperationAdd(path_in_repo=p,path_or_fileobj=io.BytesIO(blob))
                    for p,blob in updated.items()],
        commit_message="fix(§C): render GitHub approval after code and resume saved HTML").oid
    print("SAVED_HTML_REVIEW_COMMITTED",newrev,flush=True)
    try:
        for p,v in updated.items():
            got=Path(hf_hub_download(SPACE,p,repo_type="space",revision=newrev,token=token)).read_bytes()
            if got!=v:raise RuntimeError("SOURCE_HASH_MISMATCH_"+p)
        for i in range(36):
            try:
                live_probe()
                print("SAVED_HTML_REVIEW_LIVE_VERIFIED",newrev,flush=True)
                return
            except (OSError,TimeoutError,RuntimeError) as exc:
                if i==35:raise RuntimeError("SAVED_REVIEW_LIVE_TIMEOUT") from exc
                time.sleep(10)
    except Exception:
        if str(api.repo_info(SPACE,repo_type="space").sha)==newrev:
            rollback=api.create_commit(
                repo_id=SPACE,repo_type="space",parent_commit=newrev,
                operations=[CommitOperationAdd(path_in_repo=p,path_or_fileobj=io.BytesIO(v))
                            for p,v in original.items()],
                commit_message="rollback(§C): unverified saved HTML review recovery")
            print("SAVED_HTML_REVIEW_ROLLED_BACK",rollback.oid,flush=True)
        else:
            print("SAVED_HTML_REVIEW_ROLLBACK_BLOCKED_BY_CONCURRENT_UPDATE",flush=True)
        raise


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("mode",choices=("selftest","preflight","publish"))
    main(parser.parse_args().mode)
