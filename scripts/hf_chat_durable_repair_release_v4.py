#!/usr/bin/env python3
"""Scoped Hugging Face §C durable Workstation repair route release and live probe.

CAS source update of queue consumer + one helper. No model weights, project
files, auth credentials, §E files or Chat UI changes. No automatic GitHub writes.
A real anonymous Station/send request with the exact reported prompt must
reach the existing-project route before the release is accepted.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import http.cookiejar
import io
import json
import os
import time
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

SPACE = "kamiloki/Swyrlz"
BASE = "https://kamiloki-swyrlz.hf.space"
QUEUE = "queues/swrlz_generation_v3.py"
HELPER = "api/durable_project_repair_v1.py"
MARKER = "existing-project-repair-route-selected"
ORIGINAL = "    try:\n        for raw in engine.generate_events(engine_payload, cancelled):"
REPLACEMENT = """    try:
        # The browser's /api/lalm_station/send uses this durable queue, not
        # the legacy station.py _run selector. Route verified project repairs
        # BEFORE the generic coding model's failure-evidence fast path.
        from api.durable_project_repair_v1 import route_events
        selected_events = route_events(
            user_id=user_id, thread_id=thread_id, prompt=prompt_text,
            engine=engine, cancelled=cancelled, base_payload=engine_payload)
        if selected_events is not None:
            _camera("existing-project-repair-route-selected", request_id=request_id)
        for raw in (selected_events if selected_events is not None
                    else engine.generate_events(engine_payload, cancelled)):"""
FULL_PROMPT = (
    "Inspect the existing interactive-3d-model-viewer project on GitHub. "
    "Identify why it fails to render correctly and repair it using your own coding model. "
    "Retrieve the actual source, generate targeted patches, validate them, and revise any failed patches until validation passes. "
    "Preserve the existing functionality and design. Do not regenerate the entire HTML page or rely on a predetermined repair script. "
    "Present the actual changes, validation results, and approval request. Once approved, commit, deploy, and verify that the project works."
)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def patch_queue(source):
    if MARKER in source:
        if source.count(MARKER) != 1 or source.count("selected_events = route_events(") != 1:
            raise RuntimeError("PARTIAL_DURABLE_REPAIR_INSTALLATION")
        ast.parse(source, filename=QUEUE)
        return source
    if source.count(ORIGINAL) != 1:
        raise RuntimeError("LIVE_DURABLE_QUEUE_ROUTING_ANCHOR_DRIFT")
    patched = source.replace(ORIGINAL, REPLACEMENT, 1)
    ast.parse(patched, filename=QUEUE)
    if patched.count(MARKER) != 1:
        raise RuntimeError("DURABLE_REPAIR_MARKER_INTEGRITY")
    return patched


def selftest():
    candidate = Path(QUEUE).read_text(encoding="utf-8")
    helper = Path(HELPER).read_text(encoding="utf-8")
    ast.parse(candidate, filename=QUEUE)
    ast.parse(helper, filename=HELPER)
    assert candidate.count(MARKER) == 1
    assert patch_queue("from __future__ import annotations\n" + ORIGINAL + "\n").count(MARKER) == 1
    assert patch_queue(candidate) == candidate
    assert candidate.count("selected_events = route_events(") == 1
    print("DURABLE_REPAIR_SELFTEST_PASS", flush=True)


def live_health():
    with urllib.request.urlopen(BASE + "/api/html-project-agent-v1/health", timeout=25) as resp:
        health = json.load(resp)
        if resp.status != 200 or health.get("approval") != "required":
            raise RuntimeError("PROJECT_AGENT_HEALTH_UNVERIFIED")


def live_prompt_probe():
    """Prove actual ingress and routing, without privileged owner context."""
    agent = "Swrlz-Durable-Repair-Live-Regression-v4"
    jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    rid, thread_id = str(uuid.uuid4()), "repair-route-v4-" + str(uuid.uuid4())
    head = {"User-Agent": agent, "Cache-Control": "no-cache"}
    payload = {
        "modelId": "700m",
        "prompt": FULL_PROMPT,
        "threadId": thread_id,
        "requestId": rid,
        "profileId": "LALM",
        "profile": "", "userProfile": "", "timeZone": "UTC",
    }
    request = urllib.request.Request(
        BASE + "/api/lalm_station/send", data=json.dumps(payload).encode("utf-8"),
        method="POST", headers={**head, "Content-Type": "application/json"})
    with opener.open(request, timeout=40) as response:
        ack = json.load(response)
        if response.status != 202 or ack.get("accepted") is not True:
            raise RuntimeError("LIVE_STATION_REQUEST_NOT_ACCEPTED")
    phases, text_parts = [], []
    terminal = ""
    url = BASE + "/api/lalm_station/stream?" + urllib.parse.urlencode({"requestId": rid})
    with opener.open(urllib.request.Request(url, headers=head), timeout=220) as response:
        for line in response:
            try:
                event = json.loads(line)
            except (ValueError, TypeError):
                continue
            phase = str(event.get("phase") or "")
            kind = str(event.get("type") or "").upper()
            if phase:
                phases.append(phase)
            if kind == "DELTA":
                text_parts.append(str(event.get("text") or ""))
            if kind in ("COMPLETED", "COMPLETE", "FAILED", "CANCELLED"):
                terminal = kind
                break
    result = {
        "selectedRepair": "EXISTING_PROJECT_REPAIR_SELECTED" in phases,
        "authGuard": "EXISTING_PROJECT_REPAIR_AUTH_REQUIRED" in phases,
        "sourceRead": "EXISTING_PROJECT_SOURCE_READING" in phases,
        "sourceBlocker": "EXISTING_PROJECT_SOURCE_UNAVAILABLE" in phases,
        "genericEvidenceGate": "EVIDENCE_REQUIRED" in phases,
        "terminal": terminal,
        "lastPhases": phases[-14:],
        "textChars": sum(len(p) for p in text_parts),
    }
    print("DURABLE_REPAIR_LIVE_REQUEST_RECEIPT", json.dumps(result), flush=True)
    if not result["selectedRepair"]:
        raise RuntimeError("LIVE_PROMPT_NOT_ROUTED_TO_EXISTING_PROJECT")
    if not (result["authGuard"] or result["sourceRead"] or result["sourceBlocker"]):
        raise RuntimeError("LIVE_REPAIR_SOURCE_OR_AUTH_GATE_NOT_OBSERVED")
    if result["genericEvidenceGate"] or "NOVERIFIEDHTMLCODEARTIFACT" in "".join(text_parts):
        raise RuntimeError("OLD_GENERIC_CODER_GATE_STILL_INTERCEPTING")
    if terminal not in ("COMPLETED", "COMPLETE"):
        raise RuntimeError("LIVE_REPAIR_ROUTE_DID_NOT_COMPLETE")
    print("DURABLE_REPAIR_LIVE_PROMPT_VERIFIED", flush=True)


def main(mode):
    selftest()
    if mode == "selftest":
        return
    from huggingface_hub import HfApi, hf_hub_download, CommitOperationAdd, CommitOperationDelete
    token = os.getenv("HF_TOKEN") or None
    api = HfApi(token=token)
    revision = str(api.repo_info(SPACE, repo_type="space").sha)
    names = set(api.list_repo_files(SPACE, repo_type="space", revision=revision))
    if QUEUE not in names:
        raise RuntimeError("LIVE_QUEUE_NOT_IN_SPACE_SOURCE")
    original = Path(hf_hub_download(
        SPACE, QUEUE, repo_type="space", revision=revision, token=token)).read_bytes()
    patched = patch_queue(original.decode("utf-8")).encode("utf-8")
    helper = Path(HELPER).read_bytes()
    existing_helper = (Path(hf_hub_download(
        SPACE, HELPER, repo_type="space", revision=revision, token=token)).read_bytes()
        if HELPER in names else None)
    if existing_helper is not None and existing_helper != helper:
        raise RuntimeError("CONFLICTING_EXISTING_DURABLE_REPAIR_HELPER")
    print("DURABLE_REPAIR_PREFLIGHT", json.dumps({
        "revision": revision, "before": sha(original), "after": sha(patched),
        "helper": sha(helper), "alreadyInstalled": original == patched,
    }), flush=True)
    if mode == "preflight":
        return
    if mode == "verify":
        if original != patched or existing_helper != helper:
            raise RuntimeError("DURABLE_REPAIR_NOT_DEPLOYED_AT_LIVE_REVISION")
        live_health()
        live_prompt_probe()
        print("DURABLE_REPAIR_VERIFIED", revision, flush=True)
        return
    if mode != "publish" or not token or os.getenv("SWRLZ_DURABLE_REPAIR_APPROVED") != "1":
        raise PermissionError("DURABLE_REPAIR_RELEASE_NOT_AUTHORIZED")
    if str(api.repo_info(SPACE, repo_type="space").sha) != revision:
        raise RuntimeError("CONCURRENT_SPACE_SOURCE_EDIT")
    def add(path, raw):
        return CommitOperationAdd(path_in_repo=path, path_or_fileobj=io.BytesIO(raw))
    changes = [add(QUEUE, patched)]
    if existing_helper is None:
        changes.append(add(HELPER, helper))
    if original == patched and existing_helper == helper:
        live_health()
        live_prompt_probe()
        print("DURABLE_REPAIR_ALREADY_LIVE", revision, flush=True)
        return
    committed = api.create_commit(
        repo_id=SPACE, repo_type="space", parent_commit=revision,
        operations=changes,
        commit_message="fix(§C): route actual durable Workstation project repairs before coding evidence gate").oid
    print("DURABLE_REPAIR_HF_COMMITTED", committed, flush=True)
    try:
        for name, expected in ((QUEUE, patched), (HELPER, helper)):
            readback = Path(hf_hub_download(
                SPACE, name, repo_type="space", revision=committed,
                token=token)).read_bytes()
            if readback != expected:
                raise RuntimeError("DURABLE_REPAIR_READBACK_MISMATCH_" + name)
        print("DURABLE_REPAIR_SOURCE_READBACK_PASS", committed, flush=True)
        api.restart_space(SPACE)
        for attempt in range(80):
            try:
                live_health()
                live_prompt_probe()
                print("DURABLE_REPAIR_LIVE_WORKSTATION_VERIFIED", committed, flush=True)
                return
            except Exception as exc:
                if attempt % 10 == 0:
                    print("DURABLE_REPAIR_PROBE_PENDING", attempt,
                          type(exc).__name__, flush=True)
                if attempt == 79:
                    raise RuntimeError("DURABLE_REPAIR_LIVE_REQUEST_NOT_VERIFIED") from exc
                time.sleep(8)
    except Exception:
        if str(api.repo_info(SPACE, repo_type="space").sha) == committed:
            rollback = [add(QUEUE, original)]
            if existing_helper is None:
                rollback.append(CommitOperationDelete(path_in_repo=HELPER))
            reverted = api.create_commit(
                repo_id=SPACE, repo_type="space", parent_commit=committed,
                operations=rollback,
                commit_message="rollback(§C): durable Workstation repair live test failed").oid
            print("DURABLE_REPAIR_ROLLED_BACK", reverted, flush=True)
            api.restart_space(SPACE)
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("selftest", "preflight", "publish", "verify"))
    main(parser.parse_args().mode)
