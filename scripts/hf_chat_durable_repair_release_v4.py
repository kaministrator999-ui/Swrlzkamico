#!/usr/bin/env python3
"""CAS-scoped deployment of the ACTUAL durable §C Workstation project repair path.

Changes only the Workstation queue handler, signed-session ingress, and a pure
owner-bound helper on the existing Hugging Face Space. Probes the live route
without a user identity, GitHub mutation, model call or project creation.
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
QUEUE = "queues/swrlz_generation_v3.py"
INGRESS = "api/lalm_station.py"
HELPER = "api/durable_project_repair_v1.py"
MARKER = "existing-project-repair-route-selected"
INGRESS_MARKER = "verified_owner_from_session(signed_claims, user_id)"
PROBE_PATH = "/api/lalm_station/repair-route-probe-v4"

OLD_QUEUE = "    try:\n        for raw in engine.generate_events(engine_payload, cancelled):"
NEW_QUEUE = """    try:
        # The browser's /api/lalm_station/send uses this durable queue, not
        # the legacy station.py _run selector. Route verified project repairs
        # BEFORE the generic coding model's failure-evidence fast path.
        from api.durable_project_repair_v1 import route_events
        selected_events = route_events(
            user_id=user_id, owner_google_id=str(data.get("ownerGoogleId") or ""),
            thread_id=thread_id, prompt=prompt_text,
            engine=engine, cancelled=cancelled, base_payload=engine_payload)
        if selected_events is not None:
            _camera("existing-project-repair-route-selected", request_id=request_id)
        for raw in (selected_events if selected_events is not None
                    else engine.generate_events(engine_payload, cancelled)):"""

AUTH_IMPORT = "from api.google_account import AuthenticationError, user_id_from_request"
AUTH_IMPORT_NEW = AUTH_IMPORT + ", verify_session, SESSION_COOKIE"
SEND_ANCHOR = '    @app.post("/api/lalm_station/send", include_in_schema=False)'
INGRESS_USER = "            user_id = user_id_from_request(request)"
INGRESS_USER_NEW = INGRESS_USER + """
            # Bind GitHub ownership to the signed session, never browser JSON.
            from api.durable_project_repair_v1 import verified_owner_from_session
            signed_claims = verify_session(request.cookies.get(SESSION_COOKIE))
            verified_owner_google_id = verified_owner_from_session(signed_claims, user_id)"""
WORK_USER = '                "userId": turn.user_id,'
WORK_USER_NEW = WORK_USER + '\n                "ownerGoogleId": verified_owner_google_id,'
ROUTE_PROBE = """    @app.get("/api/lalm_station/repair-route-probe-v4", include_in_schema=False)
    async def station_repair_route_probe_v4():
        # Fixed unauthenticated prompt; no source lookup, model call or writes.
        from api.durable_project_repair_v1 import route_probe
        return JSONResponse(route_probe(), headers={"Cache-Control": "no-store"})

"""


def sha(value):
    return hashlib.sha256(value).hexdigest()


def patch_queue(source):
    if MARKER in source:
        if source.count(MARKER) != 1 or source.count("selected_events = route_events(") != 1:
            raise RuntimeError("PARTIAL_QUEUE_INSTALLATION")
        ast.parse(source, filename=QUEUE)
        return source
    if source.count(OLD_QUEUE) != 1:
        raise RuntimeError("LIVE_DURABLE_QUEUE_ANCHOR_DRIFT")
    updated = source.replace(OLD_QUEUE, NEW_QUEUE, 1)
    ast.parse(updated, filename=QUEUE)
    return updated


def patch_ingress(source):
    if INGRESS_MARKER in source:
        if (source.count(INGRESS_MARKER) != 1
                or source.count('"ownerGoogleId": verified_owner_google_id') != 1
                or source.count(PROBE_PATH) != 1):
            raise RuntimeError("PARTIAL_INGRESS_INSTALLATION")
        ast.parse(source, filename=INGRESS)
        return source
    if source.count(AUTH_IMPORT) != 1 or source.count(SEND_ANCHOR) != 1:
        raise RuntimeError("LIVE_DURABLE_INGRESS_ANCHOR_DRIFT")
    source = source.replace(AUTH_IMPORT, AUTH_IMPORT_NEW, 1)
    start = source.index(SEND_ANCHOR)
    end = source.find('    @app.get("/api/lalm_station/live-code"', start)
    if end < 0:
        raise RuntimeError("INGRESS_BOUNDARY_DRIFT")
    section = source[start:end]
    if section.count(INGRESS_USER) != 1 or section.count(WORK_USER) != 1:
        raise RuntimeError("INGRESS_WORK_OWNER_ANCHOR_DRIFT")
    section = section.replace(INGRESS_USER, INGRESS_USER_NEW, 1)
    section = section.replace(WORK_USER, WORK_USER_NEW, 1)
    source = source[:start] + section + source[end:]
    source = source.replace(SEND_ANCHOR, ROUTE_PROBE + SEND_ANCHOR, 1)
    ast.parse(source, filename=INGRESS)
    return source


def selftest():
    for name in (QUEUE, INGRESS, HELPER):
        ast.parse(Path(name).read_text(encoding="utf-8"), filename=name)
    if patch_queue(Path(QUEUE).read_text(encoding="utf-8")) != Path(QUEUE).read_text(encoding="utf-8"):
        raise RuntimeError("GITHUB_QUEUE_NOT_PATCHED")
    if patch_ingress(Path(INGRESS).read_text(encoding="utf-8")) != Path(INGRESS).read_text(encoding="utf-8"):
        raise RuntimeError("GITHUB_INGRESS_NOT_PATCHED")
    print("DURABLE_REPAIR_V4_SELFTEST_PASS", flush=True)


def probe_live_route():
    with urllib.request.urlopen(BASE + PROBE_PATH, timeout=25) as response:
        info = json.load(response)
        if response.status != 200:
            raise RuntimeError("LIVE_ROUTE_PROBE_HTTP_ERROR")
    required = {
        "schema": "swrlz-durable-project-repair-route-v4",
        "selectedRepair": True,
        "authGuard": True,
        "genericEvidenceGate": False,
        "terminal": True,
        "githubMutation": False,
        "modelCalled": False,
    }
    if info != required:
        raise RuntimeError("LIVE_DURABLE_REPAIR_ROUTE_PROBE_FAILED: " + repr(info)[:600])
    print("DURABLE_REPAIR_LIVE_QUEUE_ROUTE_VERIFIED", json.dumps(info), flush=True)


def main(mode):
    selftest()
    if mode == "selftest":
        return
    from huggingface_hub import HfApi, hf_hub_download, CommitOperationAdd, CommitOperationDelete
    token = os.getenv("HF_TOKEN") or None
    api = HfApi(token=token)
    rev = str(api.repo_info(SPACE, repo_type="space").sha)
    names = set(api.list_repo_files(SPACE, repo_type="space", revision=rev))
    if QUEUE not in names or INGRESS not in names:
        raise RuntimeError("LIVE_DURABLE_SOURCE_NOT_IN_SPACE")
    original = {
        path: Path(hf_hub_download(
            SPACE, path, repo_type="space", revision=rev, token=token)).read_bytes()
        for path in (QUEUE, INGRESS)
    }
    target = {
        QUEUE: patch_queue(original[QUEUE].decode("utf-8")).encode("utf-8"),
        INGRESS: patch_ingress(original[INGRESS].decode("utf-8")).encode("utf-8"),
        HELPER: Path(HELPER).read_bytes(),
    }
    if HELPER in names:
        original[HELPER] = Path(hf_hub_download(
            SPACE, HELPER, repo_type="space", revision=rev, token=token)).read_bytes()
        if original[HELPER] != target[HELPER]:
            raise RuntimeError("CONFLICTING_INSTALLED_HELPER")
    changed = {path: raw for path, raw in target.items()
               if path not in original or original[path] != raw}
    print("DURABLE_REPAIR_V4_PREFLIGHT", json.dumps({
        "revision": rev,
        "files": {path: {"before": sha(original[path]) if path in original else None,
                          "after": sha(value)} for path, value in target.items()},
        "changed": sorted(changed),
    }), flush=True)
    if mode == "preflight":
        return
    if mode == "verify":
        if changed:
            raise RuntimeError("DEPLOYED_SOURCE_READBACK_MISMATCH")
        probe_live_route()
        print("DURABLE_REPAIR_V4_VERIFIED", rev, flush=True)
        return
    if mode != "publish" or not token or os.getenv("SWRLZ_DURABLE_REPAIR_APPROVED") != "1":
        raise PermissionError("DURABLE_REPAIR_RELEASE_NOT_APPROVED")
    if str(api.repo_info(SPACE, repo_type="space").sha) != rev:
        raise RuntimeError("CONCURRENT_SPACE_SOURCE_UPDATE")
    def add(path, raw):
        return CommitOperationAdd(path_in_repo=path, path_or_fileobj=io.BytesIO(raw))
    if not changed:
        probe_live_route()
        print("DURABLE_REPAIR_V4_ALREADY_CURRENT", rev, flush=True)
        return
    new = api.create_commit(
        repo_id=SPACE, repo_type="space", parent_commit=rev,
        operations=[add(path, raw) for path, raw in changed.items()],
        commit_message="fix(§C): route durable Workstation repair via verified owner source").oid
    print("DURABLE_REPAIR_V4_COMMITTED", new, flush=True)
    try:
        for path, raw in target.items():
            readback = Path(hf_hub_download(
                SPACE, path, repo_type="space", revision=new, token=token)).read_bytes()
            if readback != raw:
                raise RuntimeError("DURABLE_REPAIR_SOURCE_MISMATCH:" + path)
        print("DURABLE_REPAIR_V4_READBACK_PASS", new, flush=True)
        api.restart_space(SPACE)
        for attempt in range(80):
            try:
                probe_live_route()
                print("DURABLE_REPAIR_V4_DEPLOYED_AND_VERIFIED", new, flush=True)
                return
            except Exception as exc:
                if attempt % 10 == 0:
                    print("DURABLE_REPAIR_V4_PROBE_PENDING", attempt, type(exc).__name__, flush=True)
                if attempt == 79:
                    raise RuntimeError("LIVE_DURABLE_ROUTE_NOT_VERIFIED") from exc
                time.sleep(8)
    except Exception:
        if str(api.repo_info(SPACE, repo_type="space").sha) == new:
            rollback = [add(path, original[path]) for path in changed if path in original]
            rollback += [CommitOperationDelete(path_in_repo=path)
                         for path in changed if path not in original]
            reverted = api.create_commit(
                repo_id=SPACE, repo_type="space", parent_commit=new,
                operations=rollback,
                commit_message="rollback(§C): durable Workstation repair route probe failed").oid
            print("DURABLE_REPAIR_V4_ROLLBACK", reverted, flush=True)
            api.restart_space(SPACE)
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("selftest", "preflight", "publish", "verify"))
    main(parser.parse_args().mode)
