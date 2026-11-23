#!/usr/bin/env python3
"""CAS-publish only the isolated §C HTML route and its dedicated helper.

Never replace models, §E files, GitHub credentials, or the chat UI.
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
MODULE = "html_project_safe_route_v1.py"
MODULE_SOURCE = Path("api/html_project_safe_route_v1.py")
MARKER = "# swrlz-sandboxed-html-project-route-v1"
ANCHOR = 'app.mount("/chat/§wyrlz/assets",StaticFiles(directory=ROOT/"chat/§wyrlz/assets"),name="chat-assets")'
INSTALL = (
    "\n" + MARKER +
    "\nimport html_project_safe_route_v1 as _swrlz_html_sandbox" +
    "\n_swrlz_html_sandbox.install(app, ROOT)\n"
)


def hashbytes(data):
    return hashlib.sha256(data).hexdigest()


def candidate(source: bytes) -> bytes:
    original = source.decode("utf-8")
    if MARKER in original:
        if original.count(MARKER) != 1 or INSTALL.strip() not in original:
            raise RuntimeError("Existing HTML project route differs from pinned installation")
        ast.parse(original, filename=STATION)
        return source
    if original.count(ANCHOR) != 1:
        raise RuntimeError("Live Station mount anchor changed: refusing unknown patch")
    patched = original.replace(ANCHOR, ANCHOR + INSTALL, 1)
    ast.parse(patched, filename=STATION)
    if patched.count(MARKER) != 1:
        raise RuntimeError("HTML project route installation count invalid")
    return patched.encode("utf-8")


def source_check():
    module = MODULE_SOURCE.read_bytes()
    ast.parse(module.decode("utf-8"), filename=MODULE)
    assert "sandbox allow-scripts" in module.decode()
    assert "allow-same-origin" not in module.decode()
    assert 'connect-src \'none\'' in module.decode()
    assert "published-html-projects" in module.decode()
    print("SAFE_ROUTE_SOURCE_VALIDATED", hashbytes(module), flush=True)
    return module


def public_probe():
    """Require a live response specific to our route, not a generic FastAPI 404."""
    request = urllib.request.Request(
        BASE + "/api/html-projects/unpublished-probe/index.html",
        headers={"Cache-Control": "no-cache", "User-Agent": "SWRLZ-HTML-ROUTE-PROBE/1"})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            raise RuntimeError("Unknown project unexpectedly served")
    except urllib.error.HTTPError as exc:
        body = exc.read(1024).decode("utf-8", errors="replace")
        if exc.code != 404 or '"detail":"Project asset not found"' not in body:
            raise RuntimeError("New project route was not observed: " + str(exc.code) +
                               " " + body[:160])
    with urllib.request.urlopen(BASE + "/chat/%C2%A7wyrlz", timeout=20) as response:
        if response.status != 200 or "text/html" not in response.headers.get("Content-Type", ""):
            raise RuntimeError("§C chat regression detected")
    print("SAFE_PROJECT_ROUTE_LIVE_AND_CHAT_HEALTHY", flush=True)


def main(mode):
    module = source_check()
    if mode == "selftest":
        fake = 'ROOT=Path(".")\napp=object()\n' + ANCHOR + '\n'
        patched = candidate(fake.encode())
        assert candidate(patched) == patched
        assert patched.count(MARKER.encode()) == 1
        try:
            candidate(b"app=object()\n")
        except RuntimeError:
            pass
        else:
            raise RuntimeError("Unknown anchor was accepted")
        print("SAFE_ROUTE_PATCH_SELFTEST_OK", flush=True)
        return
    if mode not in ("preflight", "publish", "verify"):
        raise ValueError(mode)

    from huggingface_hub import HfApi, hf_hub_download, CommitOperationAdd, CommitOperationDelete
    token = os.environ.get("HF_TOKEN") or None
    api = HfApi(token=token)
    revision = str(api.repo_info(SPACE, repo_type="space").sha)
    paths = set(api.list_repo_files(SPACE, repo_type="space", revision=revision))
    original = Path(hf_hub_download(
        SPACE, STATION, repo_type="space", revision=revision, token=token)).read_bytes()
    rewritten = candidate(original)
    existing_helper = None
    if MODULE in paths:
        existing_helper = Path(hf_hub_download(
            SPACE, MODULE, repo_type="space", revision=revision, token=token)).read_bytes()
        if existing_helper != module:
            raise RuntimeError("Previously published HTML route module differs from source")
    print("ROUTE_PREFLIGHT", json.dumps({
        "revision": revision, "before": hashbytes(original),
        "after": hashbytes(rewritten), "module": hashbytes(module),
        "alreadyInstalled": rewritten == original, "moduleExists": MODULE in paths},
        sort_keys=True), flush=True)
    if mode == "preflight":
        return
    if mode == "verify":
        if rewritten != original or existing_helper != module:
            raise RuntimeError("Safe route not installed at this Space revision")
        public_probe()
        return
    if not token or os.environ.get("SWRLZ_HTML_ROUTE_APPROVED") != "1":
        raise PermissionError("Owner-approved route release and HF_TOKEN required")
    if rewritten == original and existing_helper == module:
        public_probe()
        print("SAFE_ROUTE_ALREADY_INSTALLED", revision, flush=True)
        return
    changes = []
    if rewritten != original:
        changes.append(CommitOperationAdd(path_in_repo=STATION, path_or_fileobj=io.BytesIO(rewritten)))
    if existing_helper is None:
        changes.append(CommitOperationAdd(path_in_repo=MODULE, path_or_fileobj=io.BytesIO(module)))
    if str(api.repo_info(SPACE, repo_type="space").sha) != revision:
        raise RuntimeError("Concurrent Space revision; not publishing")
    published = api.create_commit(
        repo_id=SPACE, repo_type="space", parent_commit=revision,
        operations=changes, commit_message="feat(§C): isolated CSP-sandboxed HTML project serving")
    newrev = published.oid
    print("SAFE_ROUTE_SOURCE_COMMITTED", newrev, flush=True)
    try:
        for path, expected in ((STATION, rewritten), (MODULE, module)):
            got = Path(hf_hub_download(
                SPACE, path, repo_type="space", revision=newrev, token=token)).read_bytes()
            if got != expected:
                raise RuntimeError("Published helper/Station differs from exact reviewed bytes: " + path)
        for attempt in range(36):
            try:
                public_probe()
                print("SAFE_ROUTE_DEPLOYED_AND_VERIFIED", newrev, flush=True)
                break
            except (urllib.error.URLError, TimeoutError, RuntimeError) as exc:
                if attempt == 35:
                    raise RuntimeError("Route not proven live after publication") from exc
                time.sleep(10)
    except Exception:
        # CAS rollback of precisely our changed files only, unless another
        # publisher already moved the Space. Preserve concurrent changes.
        if str(api.repo_info(SPACE, repo_type="space").sha) == newrev:
            rollback = []
            if rewritten != original:
                rollback.append(CommitOperationAdd(
                    path_in_repo=STATION, path_or_fileobj=io.BytesIO(original)))
            if existing_helper is None:
                rollback.append(CommitOperationDelete(path_in_repo=MODULE))
            if rollback:
                restored = api.create_commit(
                    repo_id=SPACE, repo_type="space", parent_commit=newrev,
                    operations=rollback, commit_message="rollback(§C): unverified sandboxed HTML route")
                print("SAFE_ROUTE_EXACT_ROLLBACK", restored.oid, flush=True)
        else:
            print("SAFE_ROUTE_ROLLBACK_BLOCKED_BY_CONCURRENT_SPACE_UPDATE", flush=True)
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("selftest", "preflight", "publish", "verify"))
    main(parser.parse_args().mode)
