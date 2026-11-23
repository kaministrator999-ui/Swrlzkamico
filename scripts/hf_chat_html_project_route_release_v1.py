#!/usr/bin/env python3
"""CAS-guarded release of HTML project sandbox route to the existing §C Space.

Only live station.py and isolated new HTML publishing modules/UI asset are modified.
Never uploads a local Station snapshot or touches §E/chat engine/model config.
"""
from __future__ import annotations

import argparse
import ast
import io
import json
import os
from pathlib import Path
import time
from urllib.error import URLError
from urllib.request import Request, urlopen

SPACE = "kamiloki/Swyrlz"
BASE = "https://kamiloki-swyrlz.hf.space"
STATION = "station.py"
HELPER = "html_project_routes_v1.py"
SOURCE = Path("api/html_project_routes_v1.py")
ACTION_SOURCE = Path("api/html_project_publish_action_v1.py")
ASSET_SOURCE = Path("chat/html-project-publish-v1.js")
ACTION_HELPER = "html_project_publish_action_v1.py"
ASSET = "chat/§wyrlz/assets/html-project-publish-v1.js"
ACTION_ANCHOR = "github_connection.install(app, _account_session)"
ACTION_INJECTION = ("\n# swrlz-html-project-publish-owner-approval-v1\n"
    "from html_project_publish_action_v1 import install as _swrlz_install_html_publish\n"
    "_swrlz_install_html_publish(app, _account_session)")
UI_ANCHOR = "    return source.replace(marker,adapter+marker,1) if marker in source else source+adapter"
UI_INJECTION = ("    adapter += '<script src=\"/chat/§wyrlz/assets/html-project-publish-v1.js\" defer></script>'\n"
    + UI_ANCHOR)
ANCHOR = 'app.mount("/chat/§wyrlz/assets",StaticFiles(directory=ROOT/"chat/§wyrlz/assets"),name="chat-assets")'
INJECTION = (
    "\n# swrlz-html-project-isolation-v1\n"
    "from html_project_routes_v1 import install as _swrlz_install_html_projects\n"
    "_swrlz_install_html_projects(app, ROOT)"
)
BACKUP = Path("reports/html-project-route-live-backup")


def prepare(station: bytes, module: bytes, action: bytes | None = None, asset: bytes | None = None) -> bytes:
    original = station.decode("utf-8")
    ast.parse(original, filename=STATION)
    ast.parse(module.decode("utf-8"), filename=HELPER)
    if action is None: action = ACTION_SOURCE.read_bytes()
    if asset is None: asset = ASSET_SOURCE.read_bytes()
    ast.parse(action.decode("utf-8"), filename=ACTION_HELPER)
    if not asset or b"SwrlzHtmlProjectsV1" not in asset:
        raise RuntimeError("HTML project UI asset invalid")
    if INJECTION in original:
        raise RuntimeError("HTML project route is already installed; do not duplicate")
    if original.count(ANCHOR) != 1 or original.count(ACTION_ANCHOR) != 1 or original.count(UI_ANCHOR) != 1:
        raise RuntimeError("Live Station integration anchor changed; refuse unreviewed patch")
    updated = original.replace(ANCHOR, ANCHOR + INJECTION, 1)
    updated = updated.replace(ACTION_ANCHOR, ACTION_ANCHOR + ACTION_INJECTION, 1)
    updated = updated.replace(UI_ANCHOR, UI_INJECTION, 1)
    ast.parse(updated, filename=STATION)
    return updated.encode("utf-8")


def probe():
    url = BASE + "/api/html-projects/security"
    for attempt in range(24):
        try:
            with urlopen(Request(url, headers={"Cache-Control": "no-cache"}), timeout=18) as response:
                document = json.loads(response.read(4096))
                if (response.status == 200 and
                        document.get("contract") == "swrlz-html-project-isolation-v1" and
                        document.get("isolated") is True and
                        document.get("sameOriginPermission") is False):
                    return document
        except (URLError, TimeoutError, ValueError, OSError):
            pass
        if attempt < 23:
            time.sleep(5)
    raise RuntimeError("Live sandbox route contract not verified")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("preflight", "publish", "verify"))
    args = parser.parse_args()
    from huggingface_hub import HfApi, hf_hub_download, CommitOperationAdd, CommitOperationDelete

    token = os.environ.get("HF_TOKEN") if args.mode == "publish" else None
    if args.mode == "publish" and (os.environ.get("SWRLZ_HTML_ROUTE_APPROVED") != "1" or not token):
        raise PermissionError("Explicit guarded release approval and HF_TOKEN required")

    api = HfApi(token=token)
    revision = str(api.repo_info(SPACE, repo_type="space").sha)
    files = set(api.list_repo_files(SPACE, repo_type="space", revision=revision))
    station_before = Path(hf_hub_download(SPACE, STATION, repo_type="space", revision=revision, token=token)).read_bytes()
    module = SOURCE.read_bytes()
    action = ACTION_SOURCE.read_bytes()
    asset = ASSET_SOURCE.read_bytes()

    if args.mode == "verify":
        if (INJECTION.encode() not in station_before or ACTION_INJECTION.encode() not in station_before or
            UI_INJECTION.encode() not in station_before or
            not {HELPER, ACTION_HELPER, ASSET}.issubset(files)):
            raise RuntimeError("HTML project live source integration not installed")
        for name, expected in ((HELPER, module), (ACTION_HELPER, action), (ASSET, asset)):
            live = Path(hf_hub_download(SPACE, name, repo_type="space", revision=revision, token=token)).read_bytes()
            if live != expected:
                raise RuntimeError("HTML project integration byte readback mismatch: " + name)
        assert probe()["isolated"]
        print("SWRLZ_HTML_PROJECT_ROUTE_LIVE_VERIFIED", revision, flush=True)
        return

    if any(name in files for name in (HELPER, ACTION_HELPER, ASSET)):
        raise RuntimeError("Existing live helper/asset requires dedicated review; refusing overwrite")
    station_after = prepare(station_before, module, action, asset)
    print("SANDBOX_PREFLIGHT", json.dumps({
        "revision": revision, "sourceBytes": len(station_before),
        "newStationBytes": len(station_after), "helperBytes": len(module),
        "actionBytes": len(action), "uiBytes": len(asset),
        "changedFiles": [STATION, HELPER, ACTION_HELPER, ASSET],
    }), flush=True)
    if args.mode == "preflight":
        return

    BACKUP.mkdir(parents=True, exist_ok=True)
    (BACKUP / "station.before.py").write_bytes(station_before)
    (BACKUP / "station.after.py").write_bytes(station_after)
    (BACKUP / "html_project_routes_v1.py").write_bytes(module)
    (BACKUP / "html_project_publish_action_v1.py").write_bytes(action)
    (BACKUP / "html-project-publish-v1.js").write_bytes(asset)
    if str(api.repo_info(SPACE, repo_type="space").sha) != revision:
        raise RuntimeError("Live Station changed after preflight")
    result = api.create_commit(
        repo_id=SPACE, repo_type="space", parent_commit=revision,
        operations=[
            CommitOperationAdd(path_in_repo=HELPER, path_or_fileobj=io.BytesIO(module)),
            CommitOperationAdd(path_in_repo=ACTION_HELPER, path_or_fileobj=io.BytesIO(action)),
            CommitOperationAdd(path_in_repo=ASSET, path_or_fileobj=io.BytesIO(asset)),
            CommitOperationAdd(path_in_repo=STATION, path_or_fileobj=io.BytesIO(station_after)),
        ],
        commit_message="feat(§C): sandbox project HTML at /projects with opaque CSP origin",
    )
    deployed = result.oid
    print("ROUTE_SOURCE_PUBLISHED", deployed, flush=True)
    try:
        for name, wanted in ((STATION, station_after), (HELPER, module),
                             (ACTION_HELPER, action), (ASSET, asset)):
            actual = Path(hf_hub_download(SPACE, name, repo_type="space",
                                         revision=deployed, token=token)).read_bytes()
            if actual != wanted:
                raise RuntimeError("Live source readback mismatch for " + name)
        verified = probe()
        print("SWRLZ_HTML_PROJECT_ROUTE_LIVE_VERIFIED", json.dumps({
            "beforeRevision": revision, "afterRevision": deployed,
            "security": verified, "updatedFiles": [STATION, HELPER, ACTION_HELPER, ASSET],
        }), flush=True)
    except Exception:
        # Undo only if the precise failed publication remains HEAD. Never
        # replace another actor's newer Station changes.
        try:
            head = str(api.repo_info(SPACE, repo_type="space").sha)
            if head == deployed:
                restore = api.create_commit(
                    repo_id=SPACE, repo_type="space", parent_commit=deployed,
                    operations=[
                        CommitOperationAdd(path_in_repo=STATION, path_or_fileobj=io.BytesIO(station_before)),
                        CommitOperationDelete(path_in_repo=HELPER),
                        CommitOperationDelete(path_in_repo=ACTION_HELPER),
                        CommitOperationDelete(path_in_repo=ASSET),
                    ],
                    commit_message="revert(§C): unverified HTML sandbox route",
                )
                print("ROUTE_ROLLED_BACK", restore.oid, flush=True)
            else:
                print("ROUTE_ROLLBACK_SKIPPED_CONCURRENT_RELEASE", head, flush=True)
        finally:
            raise


if __name__ == "__main__":
    main()
