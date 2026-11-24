#!/usr/bin/env python3
"""Release the narrow, owner-approved §C generated HTML -> GitHub -> HF handoff.

Reads actual live HF Station and action source, fails closed on source drift,
uses a parent-CAS HF commit, validates published bytes and chat health.
Never modifies §E or model engines. Never embeds credentials in generated HTML.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import io
import os
import subprocess
import tempfile
import time
import urllib.request
from pathlib import Path

SPACE = "kamiloki/Swyrlz"
BASE = "https://kamiloki-swyrlz.hf.space"
STATION = "station.py"
ACTIONS = "github_conversation_actions_v264.py"
CHAT = "chat/§wyrlz/index.html"
ASSET = "chat/§wyrlz/assets/html-project-publish-review-v1.js"
MODULE = "github_html_project_handoff_v1.py"
SOURCE = Path("api/github_html_project_handoff_v1.py")
UI_SOURCE = Path("chat/html-project-publish-review-v1.js")
MARK = "# swrlz-generated-html-github-handoff-v1"
AMARK = "# swrlz-generated-html-action-bridge-v1"
UI_OLD = "/chat/§wyrlz/assets/html-project-publish-review-v1.js?v=1"
UI_NEW = "/chat/§wyrlz/assets/html-project-publish-review-v1.js?v=2"
FILES = (STATION, ACTIONS, CHAT, ASSET)

STATION_ANCHORS = {
    "root": 'ROOT=Path(__file__).resolve().parent',
    "intent": '    local_project_intent=_owned_project_edit_intent(t,prompt,history,pinned_context,payload["priorProgrammingState"])',
    "routing": '    elif _swrlz_explicit_html_publish_command(prompt):',
    "artifact": '            if online_research:\n                # Durable Online Research diagnostics consume',
}
INTENT_HOOK = '''
    # swrlz-generated-html-github-handoff-v1: user-authored instruction only.
    # Neither model text nor imported source can grant repository write access.
    if _swrlz_html_handoff.has_pending(google_owner,tid) and not github_chat_files.is_reply(prompt):
        _swrlz_html_handoff.expire(google_owner,tid)
    if google_owner.startswith("google:"):
        requested_html_flow=_swrlz_html_handoff.intent(prompt)
        if requested_html_flow:
            payload["htmlProjectIntent"]=requested_html_flow
            payload["htmlProjectOwner"]=google_owner
'''
ROUTE_HOOK = '''    elif payload.get("htmlProjectIntent"):
        # Generate first; only a verified, saved code artifact can be reviewed.
        pass
    elif (_swrlz_html_handoff.has_pending(google_owner,tid)
          and github_chat_files.is_reply(prompt)):
        payload["githubChatFileAction"]={"userId":google_owner,
                                         "threadId":tid,"prompt":prompt,
                                         "githubContext":active_github,"history":history[-10:]}
'''
ARTIFACT_HOOK = '''
            # swrlz-generated-html-github-handoff-v1: called only after the
            # canonical code revision is saved; proposal does not write GitHub.
            if payload.get("htmlProjectIntent"):
                if artifact is None or rejected:
                    reason="NO_VERIFIED_HTML_CODE_ARTIFACT"
                    g["status"].append({"phase":"HTML_GITHUB_REVIEW_BLOCKED",
                        "reason":reason})
                    message.setdefault("meta",{})["htmlProjectHandoffError"]=reason
                    notice="\\n\\nGitHub handoff not prepared ("+reason+"). No files were created."
                    message["text"]+=notice
                    g["text"]+=notice
                else:
                    try:
                        review=_swrlz_html_handoff.stage(
                            payload.get("htmlProjectOwner"),payload["threadId"],
                            artifact,payload["htmlProjectIntent"])
                        g.setdefault("widgets",[]).append(copy.deepcopy(review))
                        g["status"].append({"phase":"HTML_GITHUB_CREATE_REVIEW_READY",
                            "reason":"Owner approval required; no GitHub write or deployment performed."})
                        message.setdefault("meta",{})["htmlProjectHandoff"]={
                            "project":review["data"]["project"],
                            "artifactId":review["data"]["artifactId"],
                            "artifactRevision":review["data"]["artifactRevision"],
                            "sourceHash":review["data"]["sourceHash"],
                            "state":"AWAITING_GITHUB_CREATE_APPROVAL"}
                        notice="\\n\\nGitHub creation review is ready below. Approving that commit will request a separate deployment approval."
                        message["text"]+=notice
                        g["text"]+=notice
                    except _swrlz_html_handoff.HandoffError as exc:
                        g["status"].append({"phase":"HTML_GITHUB_REVIEW_BLOCKED",
                            "reason":exc.code})
                        message.setdefault("meta",{})["htmlProjectHandoffError"]=exc.code
                        notice="\\n\\nGitHub handoff not prepared ("+exc.code+"). No files were created."
                        message["text"]+=notice
                        g["text"]+=notice
'''
ACTION_HOOK = r'''

# swrlz-generated-html-action-bridge-v1
import github_html_project_handoff_v1 as _swrlz_html_handoff
_html_handoff_prior_has_pending=has_pending
_html_handoff_prior_pending_kind=pending_kind
_html_handoff_prior_expire=expire_interrupted
_html_handoff_prior_handle=handle

def has_pending(user_id,thread_id):
    return (_swrlz_html_handoff.has_pending(user_id,thread_id)
            or _html_handoff_prior_has_pending(user_id,thread_id))

def pending_kind(user_id,thread_id):
    if _swrlz_html_handoff.has_pending(user_id,thread_id):
        return "create-html-project"
    return _html_handoff_prior_pending_kind(user_id,thread_id)

def expire_interrupted(user_id,thread_id):
    _swrlz_html_handoff.expire(user_id,thread_id)
    return _html_handoff_prior_expire(user_id,thread_id)

def handle(user_id,thread_id,prompt,context=None,history=None):
    if _swrlz_html_handoff.has_pending(user_id,thread_id):
        if _YES.fullmatch(prompt or "") or _NO.fullmatch(prompt or ""):
            approved=bool(_YES.fullmatch(prompt or ""))
            try:
                result=_swrlz_html_handoff.confirm(user_id,thread_id,approved)
            except _swrlz_html_handoff.HandoffError as exc:
                return _out("HTML project creation not verified ("+exc.code+
                    "). No deployment was authorized. Check GitHub source before retrying.")
            return _out(result["text"],result.get("widget"))
        _swrlz_html_handoff.expire(user_id,thread_id)
    return _html_handoff_prior_handle(user_id,thread_id,prompt,context,history)
'''


def exactly(source, old, new, label):
    occurrences = source.count(old)
    if occurrences != 1:
        raise RuntimeError("SOURCE_DRIFT " + label + " occurrences=" + str(occurrences))
    return source.replace(old, new, 1)


def patch(original):
    station = original[STATION].decode("utf-8")
    actions = original[ACTIONS].decode("utf-8")
    page = original[CHAT].decode("utf-8")
    if MARK in station or AMARK in actions or UI_NEW in page:
        raise RuntimeError("Handoff already installed or live source differs; manual inspection required")
    station = exactly(station, STATION_ANCHORS["root"],
                      "import github_html_project_handoff_v1 as _swrlz_html_handoff\n" +
                      STATION_ANCHORS["root"], "Station module import")
    station = exactly(station, STATION_ANCHORS["intent"],
                      INTENT_HOOK + STATION_ANCHORS["intent"], "Station explicit intent")
    station = exactly(station, STATION_ANCHORS["routing"],
                      ROUTE_HOOK + STATION_ANCHORS["routing"], "Station reply routing")
    station = exactly(station, STATION_ANCHORS["artifact"],
                      ARTIFACT_HOOK + STATION_ANCHORS["artifact"], "Station saved artifact")
    ast.parse(station, filename=STATION)
    if not all(s in actions for s in ("def has_pending(", "def pending_kind(",
                                     "def expire_interrupted(", "def handle(")):
        raise RuntimeError("ACTION_HANDLER_DRIFT")
    actions = actions.rstrip() + ACTION_HOOK + "\n"
    ast.parse(actions, filename=ACTIONS)
    page = exactly(page, UI_OLD, UI_NEW, "UI asset cache-buster")
    return {STATION: station.encode("utf-8"), ACTIONS: actions.encode("utf-8"),
            CHAT: page.encode("utf-8"),
            ASSET: UI_SOURCE.read_bytes(), MODULE: SOURCE.read_bytes()}


def digest(b):
    return hashlib.sha256(b).hexdigest()


def selftest():
    ast.parse(SOURCE.read_text(), filename=MODULE)
    with tempfile.TemporaryDirectory(prefix="swrlz-html-ui-") as d:
        script = Path(d)/"review.js"
        script.write_bytes(UI_SOURCE.read_bytes())
        result = subprocess.run(["node", "--check", str(script)], capture_output=True,
                                text=True, timeout=30)
        if result.returncode:
            raise RuntimeError("HTML approval JS invalid: " + result.stderr[:1000])
    for key, anchor in STATION_ANCHORS.items():
        if not anchor:
            raise RuntimeError(key)
    if "create-html-project" not in ACTION_HOOK or "HTML_GITHUB_CREATE_REVIEW_READY" not in ARTIFACT_HOOK:
        raise RuntimeError("Orchestration seams incomplete")
    print("HTML_ARTIFACT_HANDOFF_SOURCE_SELFTEST_PASS", digest(SOURCE.read_bytes()), flush=True)


def live_probe():
    with urllib.request.urlopen(BASE + "/chat/%C2%A7wyrlz?__html_handoff_probe=2", timeout=20) as response:
        page = response.read(2_000_000).decode("utf-8", errors="replace")
        if response.status != 200 or UI_NEW not in page:
            raise RuntimeError("Live §C does not serve new approval asset revision")
    with urllib.request.urlopen(BASE + "/chat/%C2%A7wyrlz/assets/html-project-publish-review-v1.js?v=2", timeout=20) as response:
        asset = response.read(200_000).decode("utf-8", errors="replace")
        if response.status != 200 or 'creating?\"Approve GitHub commit\"' not in asset:
            raise RuntimeError("Live GitHub creation approval UI unavailable")
    print("HTML_ARTIFACT_HANDOFF_LIVE_UI_VERIFIED", flush=True)


def main(mode):
    selftest()
    if mode == "selftest":
        return
    from huggingface_hub import HfApi, hf_hub_download, CommitOperationAdd, CommitOperationDelete
    token = os.getenv("HF_TOKEN") or None
    api = HfApi(token=token)
    revision = str(api.repo_info(SPACE, repo_type="space").sha)
    existing_files = set(api.list_repo_files(SPACE, repo_type="space", revision=revision))
    if MODULE in existing_files:
        raise RuntimeError("Handoff module already exists at live revision; refusing blind overwrite")
    original = {
        path: Path(hf_hub_download(SPACE, path, repo_type="space",
                                  revision=revision, token=token)).read_bytes()
        for path in FILES
    }
    after = patch(original)
    print("HTML_ARTIFACT_HANDOFF_PREFLIGHT", revision,
          {path: digest(blob) for path, blob in after.items()}, flush=True)
    if mode == "preflight":
        return
    if mode == "verify":
        live_probe()
        return
    if mode != "publish" or not token or os.getenv("SWRLZ_HTML_ARTIFACT_HANDOFF_APPROVED") != "1":
        raise PermissionError("Release not authorized")
    if str(api.repo_info(SPACE, repo_type="space").sha) != revision:
        raise RuntimeError("Concurrent Space revision; release refused")
    result = api.create_commit(
        repo_id=SPACE, repo_type="space", parent_commit=revision,
        operations=[
            CommitOperationAdd(path_in_repo=path, path_or_fileobj=io.BytesIO(blob))
            for path, blob in after.items()
        ],
        commit_message="feat(§C): auto-review generated HTML then owner-approved GitHub and Space publish",
    )
    new_revision = result.oid
    print("HTML_ARTIFACT_HANDOFF_SOURCE_COMMITTED", new_revision, flush=True)
    try:
        for path, expected in after.items():
            actual = Path(hf_hub_download(
                SPACE, path, repo_type="space",
                revision=new_revision, token=token)).read_bytes()
            if actual != expected:
                raise RuntimeError("HF committed bytes differ: " + path)
        for attempt in range(36):
            try:
                live_probe()
                print("HTML_ARTIFACT_HANDOFF_LIVE_VERIFIED", new_revision, flush=True)
                return
            except (RuntimeError, OSError, TimeoutError) as exc:
                if attempt == 35:
                    raise RuntimeError("New §C UI not live") from exc
                time.sleep(10)
    except Exception:
        if str(api.repo_info(SPACE, repo_type="space").sha) == new_revision:
            operations = [
                CommitOperationAdd(path_in_repo=p, path_or_fileobj=io.BytesIO(blob))
                for p, blob in original.items()
            ]
            operations.append(CommitOperationDelete(path_in_repo=MODULE))
            rolled = api.create_commit(
                repo_id=SPACE, repo_type="space", parent_commit=new_revision,
                operations=operations,
                commit_message="rollback(§C): unverified generated HTML handoff",
            )
            print("HTML_ARTIFACT_HANDOFF_ROLLED_BACK", rolled.oid, flush=True)
        else:
            print("HTML_ARTIFACT_HANDOFF_ROLLBACK_UNSAFE_CONCURRENT_WRITE", flush=True)
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("selftest", "preflight", "publish", "verify"))
    main(parser.parse_args().mode)
