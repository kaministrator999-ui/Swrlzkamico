#!/usr/bin/env python3
"""CAS upgrade for §C's already-installed existing HTML project repair routing.

Upgrade the two existing helpers only. Verify live Station's installed route,
preserve owner GitHub OAuth and one-use approval, and roll back on failed health.
No HTML projects, models, or engine assets are changed by this release.
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

SPACE = "kamiloki/Swyrlz"
BASE = "https://kamiloki-swyrlz.hf.space"
ROUTE = "station.py"
FILES = {
    "html_project_context_v1.py": Path("api/html_project_context_v1.py"),
    "html_project_repair_v1.py": Path("api/html_project_repair_v1.py"),
}
HEALTH = "/api/html-project-agent-v1/health"
RELEASE = "swrlz-named-project-repair-routing-v2"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def station_guard(source):
    """Check installed production routing before touching its helper modules."""
    ast.parse(source, filename=ROUTE)
    required = (
        "_swrlz_project_context.resolve(prompt,t)",
        'payload["activeHtmlProject"]=html_project_ref',
        'payload["projectFileEvidence"]=_swrlz_project_context.evidence(',
        "_swrlz_project_repair.should_route(payload)",
        'payload["htmlRepairOwner"]=google_owner',
        'payload["htmlRepairThreadId"]=tid',
    )
    missing = [item for item in required if item not in source]
    if not any(route in source for route in ("_swrlz_model_repair.run(payload,_coder_generate)",
            "_swrlz_execute_model_repair_v7(payload,_coder_generate)") ):
        missing.append("verified model repair execution route")
    if missing:
        raise RuntimeError("LIVE_STATION_ROUTE_DRIFT: " + repr(missing))
    # The selected project must win over the old generic source-report route.
    context = source.index("_swrlz_project_context.resolve(prompt,t)")
    report = source.find("elif github_report_explain_v236.is_report_request(prompt):")
    if report >= 0 and context > report:
        raise RuntimeError("PROJECT_CONTEXT_AFTER_GENERIC_GITHUB_REPORT")
    lines = source.splitlines()
    near = next(i for i, line in enumerate(lines)
                if "_swrlz_project_context.resolve(prompt,t)" in line)
    print("LIVE_CONTEXT_ROUTE_LINES",
          "\\n".join(lines[max(near - 5, 0):near + 15]), flush=True)


def selftest():
    from api import html_project_context_v1 as context
    from api import html_project_repair_v1 as repair

    sample = (
        "Inspect the existing interactive-3d-model-viewer project on GitHub. "
        "Identify why it fails to render correctly and repair it using your "
        "own coding model. Retrieve the actual source, generate targeted patches."
    )
    project = context.resolve(sample, {"messages": []})
    if not project or project["project"] != "interactive-3d-model-viewer":
        raise RuntimeError("REPORTED_REPAIR_REQUEST_NOT_RESOLVED")
    fake = {"receivedText": sample, "activeHtmlProject": project,
            "projectFileEvidence": "Verified Git blob: " + "a" * 40,
            "githubSourceChangeTask": "plan"}
    if not repair.should_route(fake):
        raise RuntimeError("GENERIC_GITHUB_PLANNER_STEALS_REPAIR")
    if context.resolve("Repair the project", {"messages": []}) is not None:
        raise RuntimeError("INVENTED_PROJECT_IDENTITY")
    for name, path in FILES.items():
        ast.parse(path.read_text(encoding="utf-8"), filename=name)
    print("NAMED_PROJECT_REPAIR_SELFTEST_PASS", flush=True)


def health():
    request = urllib.request.Request(BASE + HEALTH,
                                     headers={"Cache-Control": "no-cache"})
    with urllib.request.urlopen(request, timeout=22) as response:
        if response.status != 200:
            raise RuntimeError("LIVE_AGENT_HEALTH_HTTP")
        data = json.loads(response.read(2500))
    if data.get("schema") != "swrlz-general-html-repair-agent-live-v1" or data.get("approval") != "required":
        raise RuntimeError("LIVE_GENERAL_REPAIR_AGENT_NOT_RUNNING")


def release(mode):
    selftest()
    if mode == "selftest":
        return
    from huggingface_hub import HfApi, hf_hub_download, CommitOperationAdd
    token = os.getenv("HF_TOKEN") or None
    api = HfApi(token=token)
    revision = str(api.repo_info(SPACE, repo_type="space").sha)
    paths = set(api.list_repo_files(SPACE, repo_type="space", revision=revision))
    if ROUTE not in paths or any(path not in paths for path in FILES):
        raise RuntimeError("REQUIRED_LIVE_MODULE_MISSING")
    station = Path(hf_hub_download(SPACE, ROUTE, repo_type="space",
                                   revision=revision, token=token)).read_text()
    station_guard(station)
    originals = {
        name: Path(hf_hub_download(SPACE, name, repo_type="space",
                                   revision=revision, token=token)).read_bytes()
        for name in FILES
    }
    for name, raw in originals.items():
        ast.parse(raw.decode("utf-8"), filename=name)
    candidates = {name: path.read_bytes() for name, path in FILES.items()}
    updated = {name: blob for name, blob in candidates.items()
               if originals[name] != blob}
    print("NAMED_PROJECT_REPAIR_PREFLIGHT", revision,
          {name: {"before": sha(originals[name]), "after": sha(candidates[name])}
           for name in FILES}, flush=True)
    if mode == "preflight":
        return
    if mode == "verify":
        if updated:
            raise RuntimeError("LIVE_SOURCE_NOT_YET_CURRENT")
        health()
        print("NAMED_PROJECT_REPAIR_LIVE_VERIFIED", revision, flush=True)
        return
    if mode != "publish" or not token or os.getenv("SWRLZ_NAMED_REPAIR_APPROVED") != "1":
        raise PermissionError("NAMED_REPAIR_RELEASE_NOT_AUTHORIZED")
    if not updated:
        health()
        print("NAMED_PROJECT_REPAIR_ALREADY_CURRENT", revision, flush=True)
        return
    if str(api.repo_info(SPACE, repo_type="space").sha) != revision:
        raise RuntimeError("CONCURRENT_SPACE_EDIT")
    def addition(path, raw):
        return CommitOperationAdd(path_in_repo=path, path_or_fileobj=io.BytesIO(raw))
    committed = api.create_commit(
        repo_id=SPACE, repo_type="space", parent_commit=revision,
        operations=[addition(name, raw) for name, raw in updated.items()],
        commit_message="fix(§C): resolve named existing projects into model-led repair").oid
    print("NAMED_PROJECT_REPAIR_SPACE_COMMITTED", committed, flush=True)
    try:
        for name, raw in candidates.items():
            readback = Path(hf_hub_download(
                SPACE, name, repo_type="space", revision=committed,
                token=token)).read_bytes()
            if readback != raw:
                raise RuntimeError("NAMED_REPAIR_READBACK_MISMATCH_" + name)
        print("NAMED_PROJECT_REPAIR_SOURCE_READBACK_PASS", committed, flush=True)
        api.restart_space(SPACE)
        for attempt in range(75):
            try:
                health()
                print("NAMED_PROJECT_REPAIR_HEALTH_VERIFIED", committed, flush=True)
                return
            except Exception as error:
                if attempt % 10 == 0:
                    print("NAMED_REPAIR_HEALTH_PENDING", attempt,
                          type(error).__name__, flush=True)
                if attempt == 74:
                    raise RuntimeError("LIVE_AGENT_HEALTH_NOT_VERIFIED") from error
                time.sleep(8)
    except Exception:
        if str(api.repo_info(SPACE, repo_type="space").sha) == committed:
            restored = api.create_commit(
                repo_id=SPACE, repo_type="space", parent_commit=committed,
                operations=[addition(name, originals[name]) for name in updated],
                commit_message="rollback(§C): named project repair routing health unverified").oid
            print("NAMED_PROJECT_REPAIR_ROLLBACK", restored, flush=True)
            api.restart_space(SPACE)
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("selftest", "preflight", "publish", "verify"))
    release(parser.parse_args().mode)
