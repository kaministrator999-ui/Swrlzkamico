#!/usr/bin/env python3
"""Scoped live §C GitHub review release.

Fetch the exact current Space revision, patch only two existing §C files,
add one isolated Python module and one JS asset, CAS-publish, verify readback.
Never package stale station.py or any §E source.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import io
import json
import os
import re
from pathlib import Path

SPACE = "kamiloki/Swyrlz"
ROOT = Path("reports/github-review-live-v1")
ACTIONS = "github_conversation_actions_v264.py"
HTML = "chat/§wyrlz/index.html"
UPDATE = "github_review_update_v1.py"
ASSET = "chat/§wyrlz/assets/github-change-review-v1.js"
SOURCE_UPDATE = Path("api/github_review_update_v1.py")
SOURCE_ASSET = Path("chat/github-change-review-v1.js")
EXISTING = (ACTIONS, HTML)
GUARDS = ("station.py", "github_connection.py", "github_general_create_v262.py")
MARK = "swrlz-github-reviewed-file-actions-v1"

ACTIONS_PATCH = r'''

# swrlz-github-reviewed-file-actions-v1
# Wrap the already authenticated conversational handler; no new endpoint and
# no permissions bypass. Proposals and one-time tickets remain server-side.
import github_review_update_v1 as _swrlz_review_update

_swrlz_before_review_is_file_action = is_file_action
_swrlz_before_review_handle = handle
_swrlz_before_review_confirmation = _confirmation
_swrlz_before_review_prepare_create = _prepare_create

def _swrlz_edit_request(text):
    if not isinstance(text, str) or len(text) > 260000:
        return None
    # Explicit, unambiguous user command; code content follows on separate
    # lines so leading indentation and other source bytes are preserved.
    match = re.match(
        r"(?i)^\s*@github\s+(?:edit|update|replace)\s+(?:the\s+)?"
        r"(?:file\s+)?(?:\x60([^\x60\r\n]+)\x60|([^\s\r\n]+))"
        r"[ \t]*\r?\ncontent:\r?\n", text
    )
    if not match:
        return None
    return (match.group(1) or match.group(2), text[match.end():])


def is_file_action(prompt, context=None, history=None):
    return (_swrlz_edit_request(prompt) is not None or
            _swrlz_before_review_is_file_action(prompt, context, history))


def _prepare_create(user_id, thread_id, path, content):
    result = _swrlz_before_review_prepare_create(user_id, thread_id, path, content)
    if not isinstance(result, dict) or result.get("widget") or not isinstance(content, str):
        return result
    with _lock:
        item = _pending.get((user_id, thread_id))
    if not item or item.get("kind") != "create":
        return result
    with create._lock:
        original = create._pending.get(item.get("ticket"))
    if not original or original.get("userId") != user_id:
        return result
    result["widget"] = {
        "contract": "swrlz-widget-v1", "kind": "github-change-review",
        "title": "GitHub · review new file", "provider": "GitHub",
        "data": {
            "operation": "CREATE_FILE", "repo": original["repo"],
            "branch": original["branch"], "path": original["path"],
            "content": content, "sha256": original["digest"],
            "bytes": len(content.encode("utf-8")), "overwrite": False
        }
    }
    return result


def _prepare_update(user_id, thread_id, path, content):
    try:
        proposal = _swrlz_review_update.prepare(user_id, path, content)
    except CreateFileError as exc:
        return _out("GitHub edit was not prepared (" + str(exc.code) +
                    "). Check the selected repository and authorize public-write access if needed. Nothing changed.")
    _remember(user_id, thread_id, {"kind": "update", "ticket": proposal["approvalToken"]})
    widget = {
        "contract": "swrlz-widget-v1", "kind": "github-change-review",
        "title": "GitHub · review file edit", "provider": "GitHub",
        "data": {
            "operation": "UPDATE_FILE", "repo": proposal["repo"],
            "branch": proposal["branch"], "path": proposal["path"],
            "content": proposal["content"], "before": proposal["before"],
            "diff": proposal["diff"], "sha256": proposal["sha256"],
            "expectedBlobSha": proposal["expectedBlobSha"],
            "bytes": proposal["bytes"], "overwrite": True
        }
    }
    return _out("Review the proposed edit to " + _clean_label(proposal["path"]) +
                " in " + _clean_label(proposal["repo"]) +
                ". **Yes** to approve or **no** to reject within five minutes. Nothing changed.", widget)


def _confirmation(user_id, thread_id, prompt):
    if pending_kind(user_id, thread_id) != "update":
        return _swrlz_before_review_confirmation(user_id, thread_id, prompt)
    pending = _consume(user_id, thread_id)
    if not pending:
        return None
    approved = bool(_YES.fullmatch(prompt))
    if not approved and not _NO.fullmatch(prompt):
        return None
    try:
        receipt = _swrlz_review_update.confirm(user_id, pending["ticket"], approved)
    except CreateFileError as exc:
        return _out("GitHub edit failed (" + str(exc.code) +
                    "). Recheck the file and request a new proposal. No success assumed.")
    if not approved:
        return _out("Rejected GitHub edit. Nothing changed.")
    path = receipt["path"]
    return _out("Updated " + _clean_label(path) + " in " +
                _clean_label(receipt["repo"]) +
                ". GitHub readback verified the exact bytes. [View commit](https://github.com/" +
                receipt["repo"] + "/commit/" + receipt["commitSha"] + ").",
                github_context={
                    "repo": receipt["repo"], "branch": receipt["branch"],
                    "sourceSha": receipt["commitSha"], "kind": "file",
                    "lastFile": path,
                    "directory": path.rsplit("/", 1)[0] if "/" in path else ""
                })


def handle(user_id, thread_id, prompt, context=None, history=None):
    edit = _swrlz_edit_request(prompt)
    if edit is not None:
        # A new request supersedes any previous pending decision.
        expire_interrupted(user_id, thread_id)
        return _prepare_update(user_id, thread_id, edit[0], edit[1])
    return _swrlz_before_review_handle(user_id, thread_id, prompt, context, history)
'''

HTML_HEAD = r'''
<style id="swrlz-github-review-v1">
.swrlz-github-change-review{display:grid;gap:10px;padding:12px;border:1px solid #3f7596;border-radius:12px;background:#081e30;color:#e8f6ff}
.swrlz-github-change-review h3{margin:0;font-size:15px}
.swrlz-github-change-review p{margin:0;font-size:12px;overflow-wrap:anywhere}
.swrlz-github-change-review pre{white-space:pre;overflow:auto;max-height:320px;padding:12px;margin:0;border:1px solid #315e77;border-radius:8px;font:12px/1.5 monospace}
.swrlz-github-change-review details{font-size:12px}
.swrlz-github-change-review button{border:1px solid #477a97;background:#143951;color:#e8f6ff;padding:10px 12px;border-radius:8px;cursor:pointer}
.swrlz-github-change-review button:last-child{background:#11675d;border-color:#37b89e}
.swrlz-github-change-review button:disabled{opacity:.55}
</style>
<script src="/chat/§wyrlz/assets/github-change-review-v1.js?v=1" defer></script>
'''

HTML_WIDGET = r'''}else if(widget.kind==="github-change-review"){
            const reviewThread=String(activeThreadId||"");
            if(!window.SwrlzGithubChangeReviewV1?.render(card,data,{
              threadId:reviewThread,
              currentThread:()=>String(activeThreadId||""),
              isLatest:wrapper=>Array.from(messageList.querySelectorAll(".swrlz-github-change-review"))
                .filter(item=>item.isConnected).at(-1)===wrapper,
              confirm:async accepted=>{
                if(sending)return false;
                const decision=accepted?"yes":"no",priorDraft=prompt.value;
                prompt.value=decision;
                const sent=await commitDraftFromPrompt();
                if(sent){
                  if(!prompt.value)prompt.value=priorDraft;
                  resizeComposer();
                  return true;
                }
                if(prompt.value===decision||!prompt.value)prompt.value=priorDraft;
                resizeComposer();
                return false;
              }
            })){
              card.appendChild(Object.assign(document.createElement("p"),{
                textContent:"GitHub review unavailable; reply yes or no in this thread to decide."
              }));
            }
          }else if(widget.kind==="github-work"){'''


def checksum(raw):
    return hashlib.sha256(raw).hexdigest()


def patch_actions(source):
    assert MARK not in source, "GitHub review integration already present"
    for anchor in ("def handle(", "def is_file_action(", "def _confirmation(",
                   "def _prepare_create(", "def pending_kind(", "def _out("):
        assert anchor in source, "Live GitHub handler changed: " + anchor
    result = source.rstrip() + "\n" + ACTIONS_PATCH + "\n"
    ast.parse(result, filename=ACTIONS)
    return result


def patch_html(source):
    assert "id=\"swrlz-github-review-v1\"" not in source, "Review UI already present"
    assert source.count("</head>") == 1, "HTML head layout changed"
    marker = '}else if(widget.kind==="github-work"){'
    assert source.count(marker) == 1, "GitHub widget renderer changed"
    result = source.replace("</head>", HTML_HEAD + "\n</head>", 1)
    result = result.replace(marker, HTML_WIDGET, 1)
    assert result.count("github-change-review-v1.js") == 1
    return result


def candidate(live):
    update = SOURCE_UPDATE.read_bytes()
    js = SOURCE_ASSET.read_bytes()
    ast.parse(update.decode("utf-8"), filename=UPDATE)
    actions = patch_actions(live[ACTIONS].decode("utf-8")).encode("utf-8")
    html = patch_html(live[HTML].decode("utf-8")).encode("utf-8")
    return {ACTIONS: actions, HTML: html, UPDATE: update, ASSET: js}


def snapshot():
    from huggingface_hub import HfApi, hf_hub_download
    api = HfApi()
    revision = str(api.repo_info(SPACE, repo_type="space").sha)
    if not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise RuntimeError("EXACT_LIVE_REVISION_MISSING")
    files = set(api.list_repo_files(SPACE, repo_type="space", revision=revision))
    if not set(EXISTING + GUARDS).issubset(files):
        raise RuntimeError("LIVE_STATION_LAYOUT_CHANGED")
    if UPDATE in files or ASSET in files:
        raise RuntimeError("REVIEW_ARTIFACT_ALREADY_PRESENT: reconcile first")
    before = {
        p: Path(hf_hub_download(SPACE, p, repo_type="space",
                                revision=revision)).read_bytes()
        for p in EXISTING + GUARDS
    }
    station = before["station.py"].decode("utf-8")
    connection = before["github_connection.py"].decode("utf-8")
    assert "github_chat_files.handle" in station and "github_chat_files.is_file_action" in station
    assert 'GITHUB_CAPABILITY_STAGE = "read-repository"' in connection
    assert '"public-write"' in connection
    assert "github_general_create_v262" in before["github_general_create_v262.py"].decode("utf-8") or "def prepare(" in before["github_general_create_v262.py"].decode("utf-8")
    after = candidate(before)
    (ROOT / "before").mkdir(parents=True, exist_ok=True)
    for p, raw in before.items():
        dest = ROOT / "before" / p
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(raw)
    manifest = {
        "contract": MARK, "space": SPACE, "revision": revision,
        "before": {p: checksum(v) for p, v in before.items()},
        "after": {p: checksum(v) for p, v in after.items()},
        "changedPaths": list(after),
        "preservedPaths": list(GUARDS),
    }
    (ROOT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print("GITHUB_REVIEW_PREFLIGHT", json.dumps(manifest, sort_keys=True), flush=True)


def publish():
    from huggingface_hub import HfApi, hf_hub_download, CommitOperationAdd, CommitOperationDelete
    if os.environ.get("SWRLZ_GITHUB_REVIEW_RELEASE_APPROVED") != "1":
        raise PermissionError("Explicit GitHub release approval missing")
    if not os.environ.get("HF_TOKEN"):
        raise PermissionError("GitHub HF_TOKEN secret unavailable")
    manifest = json.loads((ROOT / "manifest.json").read_text())
    api = HfApi(token=os.environ["HF_TOKEN"])
    revision = manifest["revision"]
    if str(api.repo_info(SPACE, repo_type="space").sha) != revision:
        raise RuntimeError("LIVE_SPACE_MOVED: abort rather than overwrite")
    before = {(p): (ROOT / "before" / p).read_bytes() for p in EXISTING + GUARDS}
    for p, raw in before.items():
        if checksum(raw) != manifest["before"][p]:
            raise RuntimeError("SNAPSHOT_HASH_CHANGED: " + p)
        current = Path(hf_hub_download(SPACE, p, repo_type="space",
                                       revision=revision, token=os.environ["HF_TOKEN"])).read_bytes()
        if current != raw:
            raise RuntimeError("SOURCE_CHANGED_DURING_REVIEW: " + p)
    after = candidate(before)
    if {p: checksum(v) for p, v in after.items()} != manifest["after"]:
        raise RuntimeError("CANDIDATE_CHANGED_AFTER_PREFLIGHT")
    operations = [
        CommitOperationAdd(path_in_repo=p, path_or_fileobj=io.BytesIO(raw))
        for p, raw in after.items()
    ]
    change = api.create_commit(
        repo_id=SPACE, repo_type="space", parent_commit=revision,
        operations=operations,
        commit_message="feat(§C): owner-reviewed GitHub create and edit with live preview",
    )
    new_revision = getattr(change, "oid", None) or str(api.repo_info(SPACE, repo_type="space").sha)
    try:
        for p, raw in after.items():
            observed = Path(hf_hub_download(
                SPACE, p, repo_type="space", revision=new_revision,
                token=os.environ["HF_TOKEN"]
            )).read_bytes()
            if observed != raw:
                raise RuntimeError("RELEASE_READBACK_MISMATCH: " + p)
    except Exception:
        if str(api.repo_info(SPACE, repo_type="space").sha) == new_revision:
            reversal = [
                CommitOperationAdd(path_in_repo=p, path_or_fileobj=io.BytesIO(before[p]))
                for p in EXISTING
            ] + [
                CommitOperationDelete(path_in_repo=p) for p in (UPDATE, ASSET)
            ]
            api.create_commit(
                repo_id=SPACE, repo_type="space", parent_commit=new_revision,
                operations=reversal,
                commit_message="rollback(§C): restore exact previous GitHub review source",
            )
        raise
    print("GITHUB_REVIEW_PUBLISHED", json.dumps({
        "before": revision, "after": new_revision, "verified": True,
        "changedPaths": list(after), "preservedPaths": list(GUARDS),
    }, sort_keys=True), flush=True)



def verify():
    """Read-only post-release verification; safe after a successful publish."""
    from huggingface_hub import HfApi, hf_hub_download
    api = HfApi()
    revision = str(api.repo_info(SPACE, repo_type="space").sha)
    files = set(api.list_repo_files(SPACE, repo_type="space", revision=revision))
    if not set(EXISTING + GUARDS + (UPDATE, ASSET)).issubset(files):
        raise RuntimeError("LIVE_GITHUB_REVIEW_FILES_MISSING")
    data = {
        p: Path(hf_hub_download(SPACE, p, repo_type="space",
                                revision=revision)).read_bytes()
        for p in EXISTING + (UPDATE, ASSET)
    }
    action_source = data[ACTIONS].decode("utf-8")
    html_source = data[HTML].decode("utf-8")
    ast.parse(action_source, filename=ACTIONS)
    assert MARK in action_source, "Expected authenticated handler not installed"
    assert html_source.count('id="swrlz-github-review-v1"') == 1
    assert html_source.count("github-change-review-v1.js") == 1
    if data[UPDATE] != SOURCE_UPDATE.read_bytes():
        raise RuntimeError("LIVE_UPDATE_HELPER_DRIFT")
    if data[ASSET] != SOURCE_ASSET.read_bytes():
        raise RuntimeError("LIVE_REVIEW_UI_ASSET_DRIFT")
    print("GITHUB_REVIEW_LIVE_SOURCE_VERIFIED", json.dumps({
        "revision": revision, "paths": list(data),
        "hashes": {p: checksum(v) for p, v in data.items()},
    }, sort_keys=True), flush=True)

def selftest():
    original_actions = (
        "def handle(a,b,c,d=None,e=None): pass\n"
        "def is_file_action(a,b=None,c=None): pass\n"
        "def _confirmation(a,b,c): pass\n"
        "def _prepare_create(a,b,c,d): pass\n"
        "def pending_kind(a,b): pass\n"
        "def _out(t,widget=None,github_context=None): pass\n"
    )
    p = patch_actions(original_actions)
    assert "swrlz-github-reviewed-file-actions-v1" in p
    assert p.index("def handle(") < p.rindex("def handle(")
    html = "<head></head><body>}else if(widget.kind===\"github-work\"){</body>"
    patched = patch_html(html)
    assert "github-change-review" in patched
    assert "github-work" in patched
    try:
        patch_actions(p)
    except AssertionError:
        pass
    else:
        raise AssertionError("Review patch not idempotent-fail-closed")
    print("GITHUB_REVIEW_PATCH_SELFTEST_PASS", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("selftest", "snapshot", "publish", "verify"))
    args = parser.parse_args()
    {"selftest": selftest, "snapshot": snapshot, "publish": publish, "verify": verify}[args.mode]()
