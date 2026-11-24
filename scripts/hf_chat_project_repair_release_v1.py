#!/usr/bin/env python3
"""Scoped CAS release: route existing project repair to owner-approved PR builder.

Updates only live Station, existing GitHub action wrapper, existing project
resolver/UI, and one isolated helper. No model, decoder, security or §E changes.
"""
from __future__ import annotations
import argparse
import ast
import hashlib
import io
import os
import time
import urllib.request
from pathlib import Path

SPACE = "kamiloki/Swyrlz"
BASE = "https://kamiloki-swyrlz.hf.space"
STATION = "station.py"
ACTIONS = "github_conversation_actions_v264.py"
HELPER = "html_project_repair_v1.py"
UI = "chat/§wyrlz/assets/html-project-publish-review-v1.js"
HTML = "chat/§wyrlz/index.html"
EXISTING = (STATION, ACTIONS, UI, HTML)
SOURCE = Path("api/html_project_repair_v1.py")
SMARK = "swrlz-existing-project-repair-routing-v1"
AMARK = "swrlz-owner-existing-html-repair-v1"
SROOT = "ROOT=Path(__file__).resolve().parent"
SROUTE = "        elif _swrlz_execution_continuity.read_only(payload):"
SCOMMAND = "    elif _swrlz_explicit_html_publish_command(prompt):"
SCTX = "    elif (html_project_ref := _swrlz_project_context.resolve(prompt,t)):"
UOLD = "html-project-publish-review-v1.js?v=1"
UNEW = "html-project-publish-review-v1.js?v=2"

ACTION_WRAPPER = r'''

# swrlz-owner-existing-html-repair-v1
import html_project_repair_v1 as _swrlz_owner_html_repair
_html_repair_prev_is_action = is_file_action
_html_repair_prev_has_pending = has_pending
_html_repair_prev_pending_kind = pending_kind
_html_repair_prev_expire = expire_interrupted
_html_repair_prev_handle = handle

def is_file_action(prompt, context=None, history=None):
    return (_swrlz_owner_html_repair.is_command(prompt)
            or _html_repair_prev_is_action(prompt, context, history))

def has_pending(user_id, thread_id):
    return (_swrlz_owner_html_repair.has_pending(user_id, thread_id)
            or _html_repair_prev_has_pending(user_id, thread_id))

def pending_kind(user_id, thread_id):
    if _swrlz_owner_html_repair.has_pending(user_id, thread_id):
        return "review-existing-html-repair"
    return _html_repair_prev_pending_kind(user_id, thread_id)

def expire_interrupted(user_id, thread_id):
    _swrlz_owner_html_repair.expire(user_id, thread_id)
    return _html_repair_prev_expire(user_id, thread_id)

def handle(user_id, thread_id, prompt, context=None, history=None):
    if _swrlz_owner_html_repair.has_pending(user_id, thread_id):
        if _YES.fullmatch(prompt or "") or _NO.fullmatch(prompt or ""):
            accepted = bool(_YES.fullmatch(prompt or ""))
            try:
                receipt = _swrlz_owner_html_repair.confirm(user_id, thread_id, accepted)
            except _swrlz_owner_html_repair.RepairError as exc:
                return _out("Repair PR NOT dispatched (" + exc.code +
                            "). No repository write or deployment verified.")
            if not accepted:
                return _out("Repair proposal rejected. No GitHub workflow dispatched.")
            return _out("Repair approved for " + _clean_label(receipt["project"]) +
                " at immutable source " + _clean_label(receipt["sourceSha"]) +
                ". GitHub accepted the build-and-PR workflow dispatch. " +
                "PR creation is NOT verified yet; inspect the workflow before merging. " +
                "[Repair workflow](" + receipt["workflowUrl"] + "). " +
                "No Hugging Face deployment was authorized.")
        _swrlz_owner_html_repair.expire(user_id, thread_id)
    match = _swrlz_owner_html_repair.COMMAND.fullmatch(prompt or "")
    if match:
        _html_repair_prev_expire(user_id, thread_id)
        slug = match.group(1).lower()
        try:
            widget = _swrlz_owner_html_repair.prepare(user_id, thread_id, slug)
        except _swrlz_owner_html_repair.RepairError as exc:
            return _out("Existing project repair cannot be staged (" + exc.code +
                "). No generic HTML rewrite, GitHub mutation or deployment attempted.")
        return _out("Review pinned repair proposal for " + _clean_label(slug) +
            ". Approve to build from the existing source and open an independent " +
            "GitHub PR. This does NOT merge the PR or publish the project. " +
            "The approval expires in five minutes.", widget)
    return _html_repair_prev_handle(user_id, thread_id, prompt, context, history)
'''


def one(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise RuntimeError("LIVE_SOURCE_DRIFT_"+label+"_"+str(count))
    return text.replace(old, new, 1)


def patch_station(source):
    if SMARK in source:
        raise RuntimeError("REPAIR_ALREADY_INSTALLED")
    source = one(source, SROOT,
        "import html_project_repair_v1 as _swrlz_project_repair\n"+SROOT, "station_import")
    source = one(source, SCTX,
        "    elif not _swrlz_project_repair.is_command(prompt) and (html_project_ref := _swrlz_project_context.resolve(prompt,t)):",
        "station_explicit_repair_precedence")
    source = one(source, SCOMMAND,
        "    elif _swrlz_explicit_html_publish_command(prompt) or _swrlz_project_repair.is_command(prompt):",
        "station_owner_command")
    source = one(source, SROUTE,
        "        elif _swrlz_project_repair.should_route(payload):\n"
        "            # "+SMARK+": no generated HTML for existing-project repair.\n"
        "            event_source=_swrlz_project_repair.events(payload)\n"+SROUTE,
        "station_model_route")
    ast.parse(source, filename=STATION)
    return source


def patch_actions(source):
    if AMARK in source:
        raise RuntimeError("ACTION_ALREADY_INSTALLED")
    for name in ("def is_file_action(", "def has_pending(", "def pending_kind(",
                 "def expire_interrupted(", "def handle(", "def _out("):
        if name not in source:
            raise RuntimeError("MISSING_OWNER_ACTION_CONTRACT_"+name)
    result = source.rstrip()+"\n"+ACTION_WRAPPER
    ast.parse(result, filename=ACTIONS)
    return result


def patch_ui(source):
    pairs = [
      ('    const creating=data.mode==="create";',
       '    const creating=data.mode==="create",repairing=data.mode==="repair";'),
      ('heading.textContent=creating?"HTML project · GitHub creation approval":"HTML project · deployment approval";',
       'heading.textContent=creating?"HTML project · GitHub creation approval":repairing?"HTML project · source-preserving repair approval":"HTML project · deployment approval";'),
      ('subtitle.textContent="Project "+data.project+(creating?" · create source in GitHub (no deployment)":" · existing §C Hugging Face Space");',
       'subtitle.textContent="Project "+data.project+(creating?" · create source in GitHub (no deployment)":repairing?" · proposed GitHub repair pull request (no deployment)":" · existing §C Hugging Face Space");'),
      ('[creating?"Proposed GitHub directory":"Published directory",data.destinationPrefix||""]',
       '[creating?"Proposed GitHub directory":repairing?"Existing project directory":"Published directory",data.destinationPrefix||""]'),
      ('note.textContent=creating?"No GitHub files have been created. This approval authorizes only the listed commit; deploying requires a second approval within this thread.":"No deployment dispatched. Approval is valid only in this thread for five minutes.";',
       'note.textContent=creating?"No GitHub files have been created. This approval authorizes only the listed commit; deploying requires a second approval within this thread.":repairing?"No GitHub changes have been made. Approval runs a pinned dependency build and proposes a review PR only. Deployment requires a separate approval.":"No deployment dispatched. Approval is valid only in this thread for five minutes.";'),
      ('decline.textContent=creating?"Cancel creation":"Cancel deployment";',
       'decline.textContent=creating?"Cancel creation":repairing?"Cancel repair":"Cancel deployment";'),
      ('approve.textContent=creating?"Approve GitHub commit":"Approve publish";',
       'approve.textContent=creating?"Approve GitHub commit":repairing?"Approve repair PR build":"Approve publish";'),
      ('if(accepted&&!creating){void verifyPublishedSource(surface,note,data,opts,thread);}',
       'if(accepted&&!creating&&!repairing){void verifyPublishedSource(surface,note,data,opts,thread);}')
    ]
    for i, (old, new) in enumerate(pairs):
        source = one(source, old, new, "ui_"+str(i))
    return source


def patch(before):
    out = dict(before)
    out[STATION] = patch_station(before[STATION])
    out[ACTIONS] = patch_actions(before[ACTIONS])
    out[UI] = patch_ui(before[UI])
    out[HTML] = one(before[HTML], UOLD, UNEW, "html_ui_asset_cache")
    return out


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def selftest():
    helper = SOURCE.read_text(encoding="utf-8")
    ast.parse(helper, filename=HELPER)
    station = (
        "import re\n"+SROOT+"\ndef worker(payload,prompt):\n"
        "    if False:\n        pass\n"+SCTX+"        pass\n"+SCOMMAND+"        pass\n"
        "def stream(payload):\n        if False:\n            pass\n"
        +SROUTE+"            pass\n")
    out = patch_station(station)
    assert SMARK in out and "_swrlz_project_repair.events(payload)" in out
    assert "or _swrlz_project_repair.is_command(prompt)" in out
    fake = ("def is_file_action(*a,**k): pass\n"
            "def has_pending(*a): pass\n"
            "def pending_kind(*a): pass\n"
            "def expire_interrupted(*a): pass\n"
            "def _out(*a): pass\n"
            "def handle(*a,**k): pass\n")
    assert AMARK in patch_actions(fake)
    print("EXISTING_HTML_REPAIR_ROUTING_SELFTEST_PASS", digest(helper.encode()), flush=True)


def health():
    req=urllib.request.Request(BASE+"/chat/%C2%A7wyrlz?__existing_repair=1",
         headers={"Cache-Control":"no-cache"})
    with urllib.request.urlopen(req,timeout=25) as resp:
        if resp.status!=200 or "text/html" not in resp.headers.get("Content-Type",""):
            raise RuntimeError("LIVE_CHAT_HEALTH_FAILED")
        page = resp.read(3_000_000).decode("utf-8", errors="replace")
        if UNEW not in page:
            raise RuntimeError("REPAIR_UI_CACHE_BUST_UNVERIFIED")
    req=urllib.request.Request(BASE+"/chat/%C2%A7wyrlz/assets/"+UNEW,
         headers={"Cache-Control":"no-cache"})
    with urllib.request.urlopen(req,timeout=25) as resp:
        text=resp.read(200_000).decode("utf-8", errors="replace")
        if resp.status!=200 or "repairing=data.mode" not in text:
            raise RuntimeError("REPAIR_UI_NOT_LIVE")


def main(mode):
    selftest()
    if mode=="selftest":
        return
    from huggingface_hub import HfApi,hf_hub_download,CommitOperationAdd,CommitOperationDelete
    token=os.environ.get("HF_TOKEN") or None
    api=HfApi(token=token)
    rev=str(api.repo_info(SPACE,repo_type="space").sha)
    old={p:Path(hf_hub_download(SPACE,p,repo_type="space",
             revision=rev,token=token)).read_bytes() for p in EXISTING}
    paths=set(api.list_repo_files(SPACE,repo_type="space",revision=rev))
    if HELPER in paths:
        raise RuntimeError("REPAIR_HELPER_EXISTS_UNEXPECTEDLY")
    patched=patch({path:data.decode("utf-8") for path,data in old.items()})
    new={p:data.encode("utf-8") for p,data in patched.items()}
    new[HELPER]=SOURCE.read_bytes()
    print("REPAIR_ROUTING_SOURCE_PREFLIGHT",rev,
          {p:digest(raw) for p,raw in new.items()},flush=True)
    if mode=="preflight":
        return
    if mode!="publish" or os.environ.get("SWRLZ_HTML_REPAIR_APPROVED")!="1" or not token:
        raise PermissionError("SCOPED_RELEASE_NOT_AUTHORIZED")
    if str(api.repo_info(SPACE,repo_type="space").sha)!=rev:
        raise RuntimeError("CONCURRENT_SPACE_EDIT")
    committed=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=rev,
       operations=[CommitOperationAdd(path_in_repo=p,path_or_fileobj=io.BytesIO(raw))
                   for p,raw in new.items()],
       commit_message="fix(§C): preserve existing HTML projects during approved repairs").oid
    print("REPAIR_ROUTING_HF_COMMITTED",committed,flush=True)
    try:
        for p,raw in new.items():
            got=Path(hf_hub_download(SPACE,p,repo_type="space",
                     revision=committed,token=token)).read_bytes()
            if got != raw:
                raise RuntimeError("PUBLISHED_BYTES_MISMATCH_"+p)
        for i in range(30):
            try:
                health()
                print("REPAIR_ROUTING_LIVE_VERIFIED",committed,flush=True)
                return
            except (OSError,TimeoutError,RuntimeError) as e:
                if i==29:
                    raise RuntimeError("LIVE_REPAIR_UI_UNVERIFIED") from e
                time.sleep(10)
    except Exception:
        if str(api.repo_info(SPACE,repo_type="space").sha)==committed:
            ops=[CommitOperationAdd(path_in_repo=p,path_or_fileobj=io.BytesIO(raw))
                 for p,raw in old.items()]
            ops.append(CommitOperationDelete(path_in_repo=HELPER))
            restored=api.create_commit(repo_id=SPACE,repo_type="space",
                parent_commit=committed,operations=ops,
                commit_message="rollback(§C): HTML repair route verification failed").oid
            print("REPAIR_ROUTING_ROLLED_BACK",restored,flush=True)
        raise


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("mode",choices=("selftest","preflight","publish"))
    main(p.parse_args().mode)
