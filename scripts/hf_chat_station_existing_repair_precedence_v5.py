#!/usr/bin/env python3
"""Correct LIVE §C station.py routing, not an unrelated repository queue.

Moves the existing owner-verified project resolver above the new-HTML branch.
Keeps the original verified GitHub OAuth, model patch, review and approval
handlers. On missing source, fail explicitly rather than generating fresh HTML.
Every write is a source-pinned Hugging Face CAS commit with rollback on failure.
"""
from __future__ import annotations
import argparse
import ast
import difflib
import hashlib
import io
import json
import os
import time
import urllib.request
from pathlib import Path

SPACE = "kamiloki/Swyrlz"
BASE = "https://kamiloki-swyrlz.hf.space"
STATION = "station.py"
MARKER = "# swrlz-existing-repair-before-html-create-v5"
PROJECT = ('    elif not _swrlz_project_repair.is_command(prompt) and '
           '(html_project_ref := _swrlz_project_context.resolve(prompt,t)):')
PROJECT_END = '    elif github_report_explain_v236.is_report_request(prompt):'
HTML_CREATE = '    elif payload.get("htmlProjectIntent"):'
RUN_REPAIR = '        elif _swrlz_project_repair.should_route(payload):'
OWNER_EXCEPT = ('        except Exception:\n'
                '            payload["projectFileEvidence"]=(')
MOUNT = 'app.mount("/chat/§wyrlz/assets",StaticFiles(directory=ROOT/"chat/§wyrlz/assets"),name="chat-assets")'
HEALTH_PATH = "/api/html-existing-repair-v5/route-health"
PROBE_PROMPT = (
    "Inspect the existing interactive-3d-model-viewer project on GitHub. "
    "Identify why it fails to render correctly and repair it using your own coding model. "
    "Retrieve the actual source, generate targeted patches, validate them, and revise any failed patches until validation passes. "
    "Preserve the existing functionality and design. Do not regenerate the entire HTML page or rely on a predetermined repair script. "
    "Present the actual changes, validation results, and approval request. Once approved, commit, deploy, and verify that the project works."
)
FAIL_BRANCH = '''        elif payload.get("existingProjectSourceError"):
            # A selected project with missing verified source NEVER falls back
            # to generic coding or new HTML publication.
            event_source=iter((
                {"type":"STATUS","phase":"EXISTING_PROJECT_SOURCE_UNAVAILABLE",
                 "reason":"Existing project source could not be owner-verified."},
                {"type":"DELTA","text":payload["existingProjectSourceError"]},
                {"type":"COMPLETED","phase":"COMPLETE"}))
'''
FAIL_OWNER = '''        except Exception:
            payload["existingProjectSourceError"]=(
                "The existing project "+html_project_ref["project"]+
                " was identified but its owner-authorized GitHub source could "
                "not be verified. Check the linked GitHub repository and Google "
                "session. No replacement HTML, GitHub edit or deployment occurred.")
            payload["projectFileEvidence"]=('''
HEALTH_ROUTE = '''
# swrlz-existing-repair-before-html-create-v5
@app.get("/api/html-existing-repair-v5/route-health",include_in_schema=False)
def _swrlz_existing_repair_v5_health():
    sample = ("Inspect the existing interactive-3d-model-viewer project on GitHub. "
              "Identify why it fails to render correctly and repair it using your own coding model. "
              "Retrieve the actual source, generate targeted patches, validate them, and revise any failed patches until validation passes. "
              "Preserve the existing functionality and design. Do not regenerate the entire HTML page or rely on a predetermined repair script. "
              "Present the actual changes, validation results, and approval request. Once approved, commit, deploy, and verify that the project works.")
    project = _swrlz_project_context.resolve(sample, {"messages":[]})
    return {
        "schema": "swrlz-existing-repair-route-v5",
        "namedProjectResolved": bool(project and project.get("project")=="interactive-3d-model-viewer"),
        "repairIntentRecognized": bool(_swrlz_project_repair.repair_intent(sample)),
        "sourceAuthorization": "owner-required",
        "githubMutation": "approval-required",
    }
'''


def sha(data):
    return hashlib.sha256(data).hexdigest()


def ensure_route(source):
    if source.count(PROJECT) != 1 or source.count(HTML_CREATE) != 1:
        raise RuntimeError("PROJECT_OR_FRESH_HTML_ROUTE_ANCHOR_DRIFT")
    if source.index(PROJECT) > source.index(HTML_CREATE):
        raise RuntimeError("EXISTING_PROJECT_STILL_AFTER_FRESH_HTML")
    if source.count('payload["existingProjectSourceError"]') < 2:
        raise RuntimeError("SOURCE_FAILURE_NOT_FAIL_CLOSED")
    if source.index('        elif payload.get("existingProjectSourceError"):') > source.index(RUN_REPAIR):
        raise RuntimeError("SOURCE_FAILURE_AFTER_CODER_ROUTING")
    if source.count(MARKER) != 1 or source.count(HEALTH_PATH) != 1:
        raise RuntimeError("LIVE_ROUTE_HEALTH_MISSING")
    ast.parse(source, filename=STATION)


def patch_station(source):
    if MARKER in source:
        ensure_route(source)
        return source
    if (source.count(PROJECT) != 1 or source.count(PROJECT_END) != 1
            or source.count(HTML_CREATE) != 1 or source.count(RUN_REPAIR) != 1
            or source.count(MOUNT) != 1):
        raise RuntimeError("LIVE_STATION_ROUTE_ANCHOR_DRIFT")
    start = source.index(PROJECT)
    end = source.index(PROJECT_END, start)
    moved = source[start:end]
    if moved.count(OWNER_EXCEPT) != 1:
        raise RuntimeError("LIVE_PROJECT_SOURCE_FAILURE_BRANCH_DRIFT")
    moved = moved.replace(PROJECT, PROJECT + "\n        " + MARKER, 1)
    moved = moved.replace(OWNER_EXCEPT, FAIL_OWNER, 1)
    without = source[:start] + source[end:]
    creation = without.index(HTML_CREATE)
    without = without[:creation] + moved + without[creation:]
    without = without.replace(RUN_REPAIR, FAIL_BRANCH + RUN_REPAIR, 1)
    without = without.replace(MOUNT, MOUNT + "\n" + HEALTH_ROUTE, 1)
    ensure_route(without)
    return without


def selftest():
    from api import html_project_context_v1 as context
    from api import html_project_repair_v1 as repair
    project = context.resolve(PROBE_PROMPT, {"messages":[]})
    assert project and project["project"] == "interactive-3d-model-viewer"
    assert repair.repair_intent(PROBE_PROMPT)
    assert context.resolve("Make a new HTML page", {"messages":[]}) is None
    print("STATION_REPAIR_V5_PROMPT_REGRESSION_PASS", flush=True)


def health():
    request = urllib.request.Request(BASE + HEALTH_PATH,
                                     headers={"Cache-Control":"no-cache"})
    with urllib.request.urlopen(request, timeout=22) as response:
        data = json.load(response)
    assert data == {
        "schema": "swrlz-existing-repair-route-v5",
        "namedProjectResolved": True,
        "repairIntentRecognized": True,
        "sourceAuthorization": "owner-required",
        "githubMutation": "approval-required",
    }, "NEW_VERSION_ROUTE_PROBE_FAILED"
    print("STATION_REPAIR_V5_LIVE_ROUTE_HEALTH_PASS", flush=True)


def main(mode):
    selftest()
    if mode == "selftest":
        return
    from huggingface_hub import HfApi, hf_hub_download, CommitOperationAdd
    token = os.environ.get("HF_TOKEN") or None
    api = HfApi(token=token)
    rev = str(api.repo_info(SPACE,repo_type="space").sha)
    original = Path(hf_hub_download(
        SPACE, STATION, repo_type="space",revision=rev,token=token)).read_bytes()
    before = original.decode("utf-8")
    after = patch_station(before).encode("utf-8")
    delta = list(difflib.unified_diff(
        before.splitlines(), after.decode("utf-8").splitlines(),
        fromfile="production-before",tofile="production-after",lineterm=""))
    print("STATION_REPAIR_V5_PREFLIGHT",json.dumps({
        "revision":rev,"before":sha(original),"after":sha(after),
        "diffLines":len(delta),"alreadyInstalled":original==after,
    }),flush=True)
    if mode=="preflight":
        print("STATION_REPAIR_V5_SCOPED_DIFF", "\n".join(delta[:100]), flush=True)
        return
    if mode=="verify":
        if original != after:
            raise RuntimeError("PRODUCTION_SOURCE_NOT_AT_EXPECTED_REVISION")
        health()
        print("STATION_REPAIR_V5_SOURCE_AND_LIVE_VERIFIED", rev, flush=True)
        return
    if (mode!="publish" or not token or
            os.environ.get("SWRLZ_STATION_REPAIR_V5_APPROVED")!="1"):
        raise PermissionError("STATION_REPAIR_RELEASE_NOT_AUTHORIZED")
    if original==after:
        health()
        print("STATION_REPAIR_V5_ALREADY_INSTALLED",rev,flush=True)
        return
    if str(api.repo_info(SPACE,repo_type="space").sha)!=rev:
        raise RuntimeError("CONCURRENT_HF_SOURCE_UPDATE")
    def add(raw):
        return CommitOperationAdd(path_in_repo=STATION,path_or_fileobj=io.BytesIO(raw))
    committed=api.create_commit(
        repo_id=SPACE,repo_type="space",parent_commit=rev,
        operations=[add(after)],
        commit_message="fix(§C): resolve existing owner GitHub project before new HTML generation").oid
    print("STATION_REPAIR_V5_HF_COMMITTED",committed,flush=True)
    try:
        got=Path(hf_hub_download(SPACE,STATION,repo_type="space",
                                revision=committed,token=token)).read_bytes()
        if got!=after:
            raise RuntimeError("HF_SOURCE_READBACK_MISMATCH")
        print("STATION_REPAIR_V5_SOURCE_READBACK_PASS",committed,flush=True)
        api.restart_space(SPACE)
        for attempt in range(75):
            try:
                health()
                print("STATION_REPAIR_V5_DEPLOYED_VERIFIED",committed,flush=True)
                return
            except Exception as exc:
                if attempt%10==0:
                    print("STATION_REPAIR_V5_LIVE_PENDING",attempt,type(exc).__name__,flush=True)
                if attempt==74:
                    raise RuntimeError("LIVE_ROUTING_NOT_VERIFIED") from exc
                time.sleep(8)
    except Exception:
        if str(api.repo_info(SPACE,repo_type="space").sha)==committed:
            reverted=api.create_commit(
                repo_id=SPACE,repo_type="space",parent_commit=committed,
                operations=[add(original)],
                commit_message="rollback(§C): existing HTML repair route failed validation").oid
            print("STATION_REPAIR_V5_ROLLED_BACK",reverted,flush=True)
            api.restart_space(SPACE)
        raise


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("mode",choices=("selftest","preflight","publish","verify"))
    main(parser.parse_args().mode)
