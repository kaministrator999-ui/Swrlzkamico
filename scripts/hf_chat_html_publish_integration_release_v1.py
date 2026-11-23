#!/usr/bin/env python3
"""Integrate owner-approved HTML project deployment into the live §C Chat Space.

The CSP-sandboxed project serving route is independently owned and MUST already
be deployed. This release touches only Station, a new owner-action module and
a new Chat UI asset. Never uploads stale Station, models, §E, or other files.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import io
import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path

SPACE = "kamiloki/Swyrlz"
BASE = "https://kamiloki-swyrlz.hf.space"
STATION = "station.py"
HELPER = "html_project_publish_action_v1.py"
ASSET = "chat/§wyrlz/assets/html-project-publish-v1.js"
SOURCE_HELPER = Path("api/html_project_publish_action_v1.py")
SOURCE_ASSET = Path("chat/html-project-publish-v1.js")
SAFE_ROUTE_MODULE = "html_project_safe_route_v1.py"
SAFE_ROUTE_MARKER = "# swrlz-sandboxed-html-project-route-v1"
MARKER = "# swrlz-html-project-publish-owner-approval-v1"
GITHUB_ANCHOR = "github_connection.install(app, _account_session)"
UI_ANCHOR = "    return source.replace(marker,adapter+marker,1) if marker in source else source+adapter"
ACTION_PATCH = (
    "\n" + MARKER +
    "\nfrom html_project_publish_action_v1 import install as _swrlz_html_publish_install" +
    "\n_swrlz_html_publish_install(app, _account_session)\n"
)
UI_LINE = '''    adapter += '<script src="/chat/§wyrlz/assets/html-project-publish-v1.js" defer></script>'\n'''
BACKUP = Path("reports/html-project-chat-release-backup")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def patch_station(raw: bytes, action: bytes, asset: bytes):
    station = raw.decode("utf-8")
    ast.parse(station, filename=STATION)
    ast.parse(action.decode("utf-8"), filename=HELPER)
    if not asset or b"SwrlzHtmlProjectsV1" not in asset:
        raise RuntimeError("HTML publish interface source invalid")
    if SAFE_ROUTE_MARKER not in station:
        raise RuntimeError("Safe HTML route is not installed; cannot enable deployment")
    if MARKER in station or UI_LINE.strip() in station:
        if (station.count(MARKER) == 1 and ACTION_PATCH.strip() in station
                and station.count(UI_LINE.strip()) == 1):
            return raw
        raise RuntimeError("Existing HTML publishing integration differs from approved release")
    if station.count(GITHUB_ANCHOR) != 1 or station.count(UI_ANCHOR) != 1:
        raise RuntimeError("Live Station integration anchor drift")
    updated = station.replace(GITHUB_ANCHOR, GITHUB_ANCHOR + ACTION_PATCH, 1)
    updated = updated.replace(UI_ANCHOR, UI_LINE + UI_ANCHOR, 1)
    ast.parse(updated, filename=STATION)
    return updated.encode("utf-8")


def _probe():
    # The public app must reference the Chat-side approval UI, serve its exact
    # asset and deny anonymous requests to the owner-only deployment API.
    for attempt in range(28):
        try:
            with urllib.request.urlopen(BASE + "/", timeout=20) as response:
                chat = response.read(1_800_000).decode("utf-8", "replace")
            if 'html-project-publish-v1.js' not in chat:
                raise RuntimeError("HTML publishing UI not injected in live Chat")
            with urllib.request.urlopen(BASE + "/chat/%C2%A7wyrlz/assets/html-project-publish-v1.js",
                                        timeout=20) as response:
                asset = response.read(350_000)
                if response.status != 200 or asset != SOURCE_ASSET.read_bytes():
                    raise RuntimeError("Published Chat interface asset is not the approved source")
            request = urllib.request.Request(
                BASE + "/api/html-projects/prepare", data=b'{"project":"sample"}',
                method="POST", headers={
                    "Origin": BASE, "X-Swrlz-Project-Action": "v1",
                    "Content-Type": "application/json",
                })
            try:
                with urllib.request.urlopen(request, timeout=18):
                    raise RuntimeError("Anonymous HTML publishing request unexpectedly accepted")
            except urllib.error.HTTPError as error:
                if error.code != 401:
                    raise RuntimeError("Owner-only publishing API not correctly protected: " +
                                       str(error.code)) from error
            print("HTML_PUBLISH_CHAT_AND_OWNER_BOUNDARY_LIVE_PASS", flush=True)
            return
        except (urllib.error.URLError, TimeoutError, RuntimeError) as error:
            if attempt == 27:
                raise RuntimeError("HTML publishing UI/API not verified live") from error
            time.sleep(5)


def main(mode):
    helper = SOURCE_HELPER.read_bytes()
    asset = SOURCE_ASSET.read_bytes()
    ast.parse(helper.decode("utf-8"), filename=HELPER)
    if mode == "selftest":
        template = ('from pathlib import Path\n'
                    'ROOT=Path(".")\n'
                    'from fastapi import FastAPI\n'
                    'app=FastAPI()\n'
                    + SAFE_ROUTE_MARKER + '\n' + GITHUB_ANCHOR + '\n'
                    + 'def _chat_document():\n    source=""\n    adapter=""\n'
                    + UI_ANCHOR + '\n')
        updated = patch_station(template.encode(), helper, asset)
        assert updated.count(MARKER.encode()) == 1
        assert patch_station(updated, helper, asset) == updated
        print("HTML_PUBLISH_STATION_PATCH_SELFTEST_PASS", flush=True)
        return

    from huggingface_hub import HfApi, hf_hub_download, CommitOperationAdd, CommitOperationDelete
    token = os.environ.get("HF_TOKEN") or None
    if mode == "publish" and (os.environ.get("SWRLZ_HTML_CHAT_PUBLISH_APPROVED") != "1" or not token):
        raise PermissionError("Owner-approved release and HF_TOKEN required")
    api = HfApi(token=token)
    revision = str(api.repo_info(SPACE, repo_type="space").sha)
    files = set(api.list_repo_files(SPACE, repo_type="space", revision=revision))
    if SAFE_ROUTE_MODULE not in files:
        raise RuntimeError("Browser sandbox route module not published")
    original = Path(hf_hub_download(SPACE, STATION, repo_type="space",
                                   revision=revision, token=token)).read_bytes()
    updated = patch_station(original, helper, asset)
    existing = {}
    for name, target in ((HELPER, helper), (ASSET, asset)):
        if name in files:
            current = Path(hf_hub_download(SPACE, name, repo_type="space",
                                           revision=revision, token=token)).read_bytes()
            if current != target:
                raise RuntimeError("Live HTML integration file differs: " + name)
            existing[name] = True
    print("HTML_PUBLISH_CHAT_PREFLIGHT", json.dumps({
        "revision": revision, "before": sha(original),
        "after": sha(updated), "helper": sha(helper), "asset": sha(asset),
        "stationChanged": original != updated,
        "existing": sorted(existing), "scope": [STATION, HELPER, ASSET],
    }, sort_keys=True), flush=True)
    if mode == "preflight":
        return
    if mode == "verify":
        if updated != original or set(existing) != {HELPER, ASSET}:
            raise RuntimeError("HTML publishing code is not installed at live revision")
        _probe()
        print("HTML_PUBLISH_CHAT_RUNTIME_VERIFIED", revision, flush=True)
        return
    if original == updated and set(existing) == {HELPER, ASSET}:
        _probe()
        print("HTML_PUBLISH_CHAT_ALREADY_INSTALLED", revision, flush=True)
        return

    BACKUP.mkdir(parents=True, exist_ok=True)
    (BACKUP / "station.before.py").write_bytes(original)
    (BACKUP / "station.after.py").write_bytes(updated)
    (BACKUP / "html_project_publish_action_v1.py").write_bytes(helper)
    (BACKUP / "html-project-publish-v1.js").write_bytes(asset)
    operations = []
    if original != updated:
        operations.append(CommitOperationAdd(path_in_repo=STATION, path_or_fileobj=io.BytesIO(updated)))
    if HELPER not in existing:
        operations.append(CommitOperationAdd(path_in_repo=HELPER, path_or_fileobj=io.BytesIO(helper)))
    if ASSET not in existing:
        operations.append(CommitOperationAdd(path_in_repo=ASSET, path_or_fileobj=io.BytesIO(asset)))
    if str(api.repo_info(SPACE, repo_type="space").sha) != revision:
        raise RuntimeError("Space changed after preflight; refusing stale Station overwrite")
    result = api.create_commit(
        repo_id=SPACE, repo_type="space", parent_commit=revision,
        operations=operations, commit_message="feat(§C): owner-approved HTML publish interface")
    published = result.oid
    print("HTML_PUBLISH_CHAT_SOURCE_COMMITTED", published, flush=True)
    try:
        for path, expected in ((STATION, updated), (HELPER, helper), (ASSET, asset)):
            live = Path(hf_hub_download(SPACE, path, repo_type="space",
                                       revision=published, token=token)).read_bytes()
            if live != expected:
                raise RuntimeError("Live readback mismatch: " + path)
        _probe()
        print("HTML_PUBLISH_CHAT_DEPLOYED_AND_VERIFIED", published, flush=True)
    except Exception:
        current = str(api.repo_info(SPACE, repo_type="space").sha)
        if current == published:
            rollback = []
            if original != updated:
                rollback.append(CommitOperationAdd(path_in_repo=STATION, path_or_fileobj=io.BytesIO(original)))
            if HELPER not in existing:
                rollback.append(CommitOperationDelete(path_in_repo=HELPER))
            if ASSET not in existing:
                rollback.append(CommitOperationDelete(path_in_repo=ASSET))
            if rollback:
                result = api.create_commit(
                    repo_id=SPACE, repo_type="space", parent_commit=published,
                    operations=rollback, commit_message="rollback(§C): unverified HTML publishing UI/API")
                print("HTML_PUBLISH_CHAT_EXACT_ROLLBACK", result.oid, flush=True)
        else:
            print("HTML_PUBLISH_CHAT_ROLLBACK_SKIPPED_CONCURRENT_RELEASE", current, flush=True)
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("selftest", "preflight", "publish", "verify"))
    main(parser.parse_args().mode)
