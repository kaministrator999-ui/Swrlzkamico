#!/usr/bin/env python3
"""CAS-scoped §C existing HTML repair backend release.

Only production Station routing, owner action handler, and isolated repair helper.
No cached browser HTML/JS changes, model changes, project writes or deployment.
"""
from __future__ import annotations
import argparse
import ast
import hashlib
import io
import json
import os
import time
import urllib.request
from pathlib import Path

SPACE="kamiloki/Swyrlz"
BASE="https://kamiloki-swyrlz.hf.space"
STATION="station.py"
ACTIONS="github_conversation_actions_v264.py"
HELPER="html_project_repair_v1.py"
SOURCE=Path("api/html_project_repair_v1.py")
MARK="swrlz-existing-project-repair-routing-v2"
AMARK="swrlz-owner-existing-html-repair-v2"
SROOT="ROOT=Path(__file__).resolve().parent"
PROJECT_CONTEXT="    elif (html_project_ref := _swrlz_project_context.resolve(prompt,t)):"
OWNER_COMMAND="    elif _swrlz_explicit_html_publish_command(prompt):"
READ_ONLY="        elif _swrlz_execution_continuity.read_only(payload):"
MOUNT='app.mount("/chat/§wyrlz/assets",StaticFiles(directory=ROOT/"chat/§wyrlz/assets"),name="chat-assets")'
HEALTH_PATH="/api/html-project-repair-v1/health"
HEALTH_MARK="swrlz-existing-project-repair-live-v2"
HEALTH_ROUTE=r'''
@app.get("/api/html-project-repair-v1/health",include_in_schema=False)
def _swrlz_existing_html_repair_health():
    return {"schema":"swrlz-existing-project-repair-live-v2",
            "approval":"required","mutation":"none"}
'''
ACTION_WRAPPER=r'''

# swrlz-owner-existing-html-repair-v2
import html_project_repair_v1 as _swrlz_owner_html_repair
_html_repair_prev_is_action=is_file_action
_html_repair_prev_has_pending=has_pending
_html_repair_prev_pending_kind=pending_kind
_html_repair_prev_expire=expire_interrupted
_html_repair_prev_handle=handle

def is_file_action(prompt,context=None,history=None):
    return (_swrlz_owner_html_repair.is_command(prompt)
            or _html_repair_prev_is_action(prompt,context,history))

def has_pending(user_id,thread_id):
    return (_swrlz_owner_html_repair.has_pending(user_id,thread_id)
            or _html_repair_prev_has_pending(user_id,thread_id))

def pending_kind(user_id,thread_id):
    if _swrlz_owner_html_repair.has_pending(user_id,thread_id):
        return "review-existing-html-repair"
    return _html_repair_prev_pending_kind(user_id,thread_id)

def expire_interrupted(user_id,thread_id):
    _swrlz_owner_html_repair.expire(user_id,thread_id)
    return _html_repair_prev_expire(user_id,thread_id)

def handle(user_id,thread_id,prompt,context=None,history=None):
    if _swrlz_owner_html_repair.has_pending(user_id,thread_id):
        if _YES.fullmatch(prompt or "") or _NO.fullmatch(prompt or ""):
            accepted=bool(_YES.fullmatch(prompt or ""))
            try:
                receipt=_swrlz_owner_html_repair.confirm(user_id,thread_id,accepted)
            except _swrlz_owner_html_repair.RepairError as exc:
                return _out("Repair workflow NOT dispatched ("+exc.code+
                    "). No project mutation or deployment verified.")
            if not accepted:
                return _out("Repair proposal rejected. No GitHub operation dispatched.")
            return _out("Source-pinned repair build approved for "+
                _clean_label(receipt["project"])+" at "+
                _clean_label(receipt["sourceSha"])+". GitHub accepted "+
                "a build-and-review-PR workflow dispatch. PR creation is not "+
                "yet verified; [view Actions]("+receipt["workflowUrl"]+"). "+
                "The existing project is not merged or deployed.")
        _swrlz_owner_html_repair.expire(user_id,thread_id)
    command=_swrlz_owner_html_repair.COMMAND.fullmatch(prompt or "")
    if command:
        _html_repair_prev_expire(user_id,thread_id)
        slug=command.group(1).lower()
        try:
            review=_swrlz_owner_html_repair.prepare(user_id,thread_id,slug)
        except _swrlz_owner_html_repair.RepairError as exc:
            return _out("Source-preserving repair cannot be staged ("+exc.code+
                "). No generic HTML rewrite, GitHub mutation or deployment attempted.")
        data=review["data"]
        return _out("Review existing project "+_clean_label(slug)+
            " at immutable GitHub revision "+_clean_label(data["sourceSha"])+
            ", current index blob "+_clean_label(data["indexGitBlobSha"])+
            ". Proposed action: bundle pinned local Three.js dependencies "+
            "using the existing module, run static checks and open a GitHub "+
            "pull request for review. No merge or deployment. "+
            "Reply YES to authorize this build-and-PR workflow, or NO to "+
            "reject it, in this same chat within five minutes.")
    return _html_repair_prev_handle(user_id,thread_id,prompt,context,history)
'''


def one(source,old,new,label):
    if source.count(old)!=1:
        raise RuntimeError("SOURCE_DRIFT_"+label+"_"+str(source.count(old)))
    return source.replace(old,new,1)


def patch_station(code):
    if MARK in code:
        raise RuntimeError("ROUTING_ALREADY_INSTALLED")
    code=one(code,SROOT,"import html_project_repair_v1 as _swrlz_project_repair\n"+SROOT,"import")
    code=one(code,PROJECT_CONTEXT,
        "    elif not _swrlz_project_repair.is_command(prompt) and (html_project_ref := _swrlz_project_context.resolve(prompt,t)):",
        "owner_command_precedence")
    code=one(code,OWNER_COMMAND,
        "    elif _swrlz_explicit_html_publish_command(prompt) or _swrlz_project_repair.is_command(prompt):",
        "owner_action")
    code=one(code,READ_ONLY,
        "        elif _swrlz_project_repair.should_route(payload):\n"
        "            # "+MARK+": preserve verified project source.\n"
        "            event_source=_swrlz_project_repair.events(payload)\n"+READ_ONLY,
        "read_only_precedence")
    code=one(code,MOUNT,MOUNT+"\n# "+HEALTH_MARK+"\n"+HEALTH_ROUTE,"health")
    ast.parse(code,filename=STATION)
    return code


def patch_actions(code):
    if AMARK in code:
        raise RuntimeError("HANDLER_ALREADY_INSTALLED")
    for field in ("def handle(","def is_file_action(","def has_pending(",
                  "def pending_kind(","def expire_interrupted(","def _out("):
        if field not in code:
            raise RuntimeError("ACTION_HANDLER_DRIFT_"+field)
    result=code.rstrip()+"\n"+ACTION_WRAPPER
    ast.parse(result,filename=ACTIONS)
    return result


def checksum(raw):
    return hashlib.sha256(raw).hexdigest()


def selftest():
    ast.parse(SOURCE.read_text(encoding="utf-8"),filename=HELPER)
    station=("from pathlib import Path\n"+SROOT+"\n"+MOUNT+
            "\ndef user(payload,prompt):\n"
            "    if False:\n        pass\n"+PROJECT_CONTEXT+"        pass\n"+
            OWNER_COMMAND+"        pass\n"
            "def stream(payload):\n        if False:\n            pass\n"+
            READ_ONLY+"            pass\n")
    patched=patch_station(station)
    assert MARK in patched and HEALTH_MARK in patched
    assert "_swrlz_project_repair.events(payload)" in patched
    fake=("def is_file_action(*a,**k): pass\n"
          "def has_pending(*a): pass\n"
          "def pending_kind(*a): pass\n"
          "def expire_interrupted(*a): pass\n"
          "def _out(*a): pass\n"
          "def handle(*a,**k): pass\n")
    assert AMARK in patch_actions(fake)
    print("EXISTING_REPAIR_BACKEND_SELFTEST_PASS",checksum(SOURCE.read_bytes()),flush=True)


def health():
    req=urllib.request.Request(BASE+HEALTH_PATH,
         headers={"Cache-Control":"no-cache"})
    with urllib.request.urlopen(req,timeout=25) as resp:
        body=resp.read(1000)
        if resp.status!=200 or resp.headers.get("content-type","").split(";")[0].lower()!="application/json":
            raise RuntimeError("LIVE_REPAIR_HEALTH_INVALID")
        try: value=json.loads(body)
        except ValueError as exc:
            raise RuntimeError("LIVE_REPAIR_HEALTH_NOT_JSON") from exc
        if value!={"schema":HEALTH_MARK,"approval":"required","mutation":"none"}:
            raise RuntimeError("LIVE_REPAIR_REVISION_NOT_ACTIVE")


def main(mode):
    selftest()
    if mode=="selftest":
        return
    from huggingface_hub import HfApi,hf_hub_download,CommitOperationAdd,CommitOperationDelete
    token=os.getenv("HF_TOKEN") or None
    api=HfApi(token=token)
    revision=str(api.repo_info(SPACE,repo_type="space").sha)
    original={p:Path(hf_hub_download(SPACE,p,repo_type="space",
              revision=revision,token=token)).read_bytes()
              for p in (STATION,ACTIONS)}
    if HELPER in set(api.list_repo_files(SPACE,repo_type="space",revision=revision)):
        raise RuntimeError("REPAIR_HELPER_ALREADY_EXISTS")
    patched={
        STATION:patch_station(original[STATION].decode("utf-8")).encode("utf-8"),
        ACTIONS:patch_actions(original[ACTIONS].decode("utf-8")).encode("utf-8"),
        HELPER:SOURCE.read_bytes()
    }
    print("SOURCE_PRESERVING_REPAIR_PREFLIGHT",revision,
          {p:checksum(data) for p,data in patched.items()},flush=True)
    if mode=="preflight":
        return
    if mode!="publish" or not token or os.getenv("SWRLZ_HTML_REPAIR_APPROVED")!="1":
        raise PermissionError("RELEASE_NOT_AUTHORIZED")
    if str(api.repo_info(SPACE,repo_type="space").sha)!=revision:
        raise RuntimeError("CONCURRENT_SPACE_EDIT")
    commit=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=revision,
          operations=[CommitOperationAdd(path_in_repo=p,path_or_fileobj=io.BytesIO(data))
                      for p,data in patched.items()],
          commit_message="fix(§C): route existing HTML repair through approved source patches").oid
    print("SOURCE_PRESERVING_REPAIR_COMMITTED",commit,flush=True)
    try:
        for p,data in patched.items():
            got=Path(hf_hub_download(SPACE,p,repo_type="space",
                     revision=commit,token=token)).read_bytes()
            if got!=data:
                raise RuntimeError("SOURCE_READBACK_FAILED_"+p)
        api.restart_space(SPACE)
        print("REPAIR_BACKEND_RESTART_REQUESTED",commit,flush=True)
        for attempt in range(60):
            try:
                health()
                print("REPAIR_BACKEND_LIVE_ROUTE_VERIFIED",commit,flush=True)
                return
            except Exception as exc:
                if attempt%10==0:
                    print("REPAIR_BACKEND_LIVE_CHECK_PENDING",attempt,
                          type(exc).__name__,flush=True)
                if attempt==59:
                    raise RuntimeError("LIVE_ROUTE_NOT_VERIFIED") from exc
                time.sleep(10)
    except Exception:
        if str(api.repo_info(SPACE,repo_type="space").sha)==commit:
            ops=[CommitOperationAdd(path_in_repo=p,path_or_fileobj=io.BytesIO(data))
                 for p,data in original.items()]
            ops.append(CommitOperationDelete(path_in_repo=HELPER))
            reverted=api.create_commit(repo_id=SPACE,repo_type="space",
                parent_commit=commit,operations=ops,
                commit_message="rollback(§C): unverified existing HTML repair route").oid
            print("REPAIR_BACKEND_ROLLED_BACK",reverted,flush=True)
            api.restart_space(SPACE)
            print("REPAIR_BACKEND_ROLLBACK_RESTART_REQUESTED",reverted,flush=True)
        raise


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("mode",choices=("selftest","preflight","publish"))
    main(parser.parse_args().mode)
