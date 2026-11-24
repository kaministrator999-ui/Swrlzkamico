#!/usr/bin/env python3
"""Guarded HF patch for §C project context precedence; source-CAS and scoped rollback."""
from __future__ import annotations
import argparse,ast,hashlib,io,os,time,urllib.request
from pathlib import Path
SPACE="kamiloki/Swyrlz"
BASE="https://kamiloki-swyrlz.hf.space"
STATION="station.py"
MODULE="html_project_context_v1.py"
SOURCE=Path("api/html_project_context_v1.py")
MARK="# swrlz-html-project-context-routing-v1"
ROOT_ANCHOR='ROOT=Path(__file__).resolve().parent'
ROUTE_ANCHOR='    elif github_report_explain_v236.is_report_request(prompt):'
IMPORT='import html_project_context_v1 as _swrlz_project_context\n'
ROUTE='''    elif (html_project_ref := _swrlz_project_context.resolve(prompt,t)):
        # swrlz-html-project-context-routing-v1: inspect the actual project before a stale report scope.
        # This is read-only; GitHub edits and publishing still need explicit owner approval.
        try:
            html_project_source=_swrlz_project_context.read_project_source(
                google_owner,html_project_ref)
            payload["projectFileEvidence"]=_swrlz_project_context.evidence(
                html_project_ref,html_project_source)
            payload["activeHtmlProject"]=html_project_ref
        except Exception:
            payload["projectFileEvidence"]=(
                "The user refers to HTML project "+html_project_ref["project"]+
                " at "+html_project_ref["path"]+
                " but exact owner-authorized GitHub source could not be retrieved. "
                "Do not claim source inspection, repair, repository edit, deployment or "
                "runtime verification. Recover GitHub access or report this blocker.")
        # Preserve the normal model response path with grounded project evidence.
'''
def digest(data):return hashlib.sha256(data).hexdigest()
def patch(station):
    if MARK in station:
        if station.count(MARK) != 1 or 'payload["activeHtmlProject"]=html_project_ref' not in station:
            raise RuntimeError("PARTIAL_PROJECT_CONTEXT_INSTALLATION")
        ast.parse(station,filename=STATION)
        return station
    if station.count(ROOT_ANCHOR)!=1 or station.count(ROUTE_ANCHOR)!=1:
        raise RuntimeError("LIVE_PROJECT_ROUTING_ANCHOR_DRIFT")
    if "projectFileEvidence" not in station:
        raise RuntimeError("PROJECT_FILE_EVIDENCE_CHANNEL_MISSING")
    station=station.replace(ROOT_ANCHOR,IMPORT+ROOT_ANCHOR,1)
    station=station.replace(ROUTE_ANCHOR,ROUTE+ROUTE_ANCHOR,1)
    ast.parse(station,filename=STATION)
    return station
def selftest():
    ast.parse(SOURCE.read_text(encoding="utf-8"),filename=MODULE)
    fake='''from pathlib import Path
payload={"projectFileEvidence":None}
t={}
google_owner=""
prompt=""
ROOT=Path(__file__).resolve().parent
def route():
    if False:
        pass
    elif github_report_explain_v236.is_report_request(prompt):
        pass
'''
    out=patch(fake)
    assert MARK in out and out.count(ROUTE_ANCHOR)==1
    assert patch(out) == out
    print("PROJECT_CONTEXT_ROUTING_SELFTEST_PASS",digest(SOURCE.read_bytes()),flush=True)
def live_health():
    with urllib.request.urlopen(BASE+"/chat/%C2%A7wyrlz?__project_context=1",timeout=20) as r:
        if r.status!=200 or "text/html" not in r.headers.get("Content-Type",""):
            raise RuntimeError("LIVE_CHAT_UNHEALTHY")
        r.read(500)
    print("PROJECT_CONTEXT_CHAT_LIVE_HEALTHY",flush=True)
def main(mode):
    selftest()
    if mode=="selftest":return
    from huggingface_hub import HfApi,hf_hub_download,CommitOperationAdd,CommitOperationDelete
    token=os.environ.get("HF_TOKEN") or None
    api=HfApi(token=token)
    current=str(api.repo_info(SPACE,repo_type="space").sha)
    files=set(api.list_repo_files(SPACE,repo_type="space",revision=current))
    original=Path(hf_hub_download(SPACE,STATION,repo_type="space",revision=current,token=token)).read_bytes()
    code=original.decode("utf-8")
    module=SOURCE.read_bytes()
    if mode=="verify":
        if MARK not in code or MODULE not in files:
            raise RuntimeError("PROJECT_CONTEXT_NOT_PUBLISHED")
        got=Path(hf_hub_download(SPACE,MODULE,repo_type="space",revision=current,token=token)).read_bytes()
        if got!=module:raise RuntimeError("PUBLISHED_HELPER_SOURCE_DRIFT")
        ast.parse(code,filename=STATION)
        live_health()
        print("PROJECT_CONTEXT_LIVE_SOURCE_VERIFIED",current,flush=True)
        return
    if MODULE in files and mode=="publish":
        raise RuntimeError("USE_NAMED_PROJECT_REPAIR_UPGRADE_FOR_EXISTING_HELPER")
    after=patch(code).encode("utf-8")
    print("PROJECT_CONTEXT_PREFLIGHT",current,{STATION:digest(after),MODULE:digest(module)},flush=True)
    if mode=="preflight":return
    if mode!="publish" or not token or os.environ.get("SWRLZ_HTML_CONTEXT_RELEASE_APPROVED")!="1":
        raise PermissionError("RELEASE_NOT_AUTHORIZED")
    if str(api.repo_info(SPACE,repo_type="space").sha)!=current:
        raise RuntimeError("CONCURRENT_SPACE_WRITE")
    new=api.create_commit(
        repo_id=SPACE,repo_type="space",parent_commit=current,
        operations=[
            CommitOperationAdd(path_in_repo=STATION,path_or_fileobj=io.BytesIO(after)),
            CommitOperationAdd(path_in_repo=MODULE,path_or_fileobj=io.BytesIO(module))],
        commit_message="fix(§C): select verified HTML project before stale GitHub file scopes").oid
    print("PROJECT_CONTEXT_HF_COMMITTED",new,flush=True)
    try:
        for path,expected in ((STATION,after),(MODULE,module)):
            got=Path(hf_hub_download(SPACE,path,repo_type="space",revision=new,token=token)).read_bytes()
            if got!=expected:raise RuntimeError("PUBLISHED_SOURCE_MISMATCH_"+path)
        for attempt in range(30):
            try:
                live_health()
                print("PROJECT_CONTEXT_HF_LIVE_VERIFIED",new,flush=True)
                return
            except (OSError,TimeoutError,RuntimeError) as exc:
                if attempt==29:raise RuntimeError("LIVE_HEALTH_FAILED") from exc
                time.sleep(10)
    except Exception:
        if str(api.repo_info(SPACE,repo_type="space").sha)==new:
            rollback=api.create_commit(
                repo_id=SPACE,repo_type="space",parent_commit=new,
                operations=[
                    CommitOperationAdd(path_in_repo=STATION,path_or_fileobj=io.BytesIO(original)),
                    CommitOperationDelete(path_in_repo=MODULE)],
                commit_message="rollback(§C): project routing live verification failed")
            print("PROJECT_CONTEXT_ROLLED_BACK",rollback.oid,flush=True)
        else:print("PROJECT_CONTEXT_ROLLBACK_BLOCKED_CONCURRENT_WRITE",flush=True)
        raise
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("mode",choices=("selftest","preflight","publish","verify"))
    main(p.parse_args().mode)
