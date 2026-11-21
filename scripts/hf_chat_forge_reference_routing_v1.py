#!/usr/bin/env python3
"""Publish a source-pinned change to the existing §C Space."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
from urllib.request import urlopen


SPACE = "kamiloki/Swyrlz"
ROOT = Path(__file__).resolve().parents[1]
RELEASE = ROOT / "scripts/releases/forge_reference_routing_v1"
MANIFEST = json.loads(RELEASE.with_suffix(".json").read_text())
BASE = MANIFEST["baseRevision"]
FILES = MANIFEST["files"]
RECEIPT = Path("reports/forge-reference-routing-v1")
READY = "https://kamiloki-swyrlz.hf.space/api/hf/qwen35-ready"


def prepare(download):
    before = RECEIPT / "before"
    after = RECEIPT / "after"
    for directory in (before, after):
        directory.mkdir(parents=True, exist_ok=True)
    for name, expected in FILES.items():
        raw = download(name, BASE)
        if hashlib.sha256(raw).hexdigest() != expected["before"]:
            raise RuntimeError(f"Pinned live source mismatch for {name}")
        (before / name).write_bytes(raw)
        (after / name).write_bytes(raw)
    patch = ["patch", "-p1", "--fuzz=0", "--batch", "--forward", "-i", str(RELEASE.with_suffix(".patch"))]
    subprocess.run([*patch, "--dry-run"], cwd=after, check=True)
    subprocess.run(patch, cwd=after, check=True)
    for name, expected in FILES.items():
        raw = (after / name).read_bytes()
        if hashlib.sha256(raw).hexdigest() != expected["after"]:
            raise RuntimeError(f"Candidate source mismatch for {name}")
        compile(raw, name, "exec")
    subprocess.run(["python", str(ROOT / "tests/test_forge_reference_routing_v1.py"), str(before), str(after)], check=True)
    return before, after


def wait_until_serving(api, revision):
    consecutive = 0
    for _ in range(60):
        try:
            head = api.repo_info(SPACE, repo_type="space").sha
            if head != revision:
                raise RuntimeError("Concurrent Space release superseded this candidate")
            runtime = api.get_space_runtime(SPACE)
            state = runtime.raw.get("sha") == revision and runtime.stage == "RUNNING"
            if state:
                with urlopen(READY, timeout=15) as response:
                    readiness = json.load(response)
                state = readiness.get("ready") is True and readiness.get("model") == "qwen3.5-9b"
        except OSError:
            state = False
        consecutive = consecutive + 1 if state else 0
        if consecutive == 2:
            return
        time.sleep(12)
    raise RuntimeError("Patched revision did not become ready")


def main():
    from huggingface_hub import CommitOperationAdd, HfApi, hf_hub_download

    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["inspect", "publish"])
    args = parser.parse_args()
    token = os.getenv("HF_TOKEN")
    api = HfApi(token=token or False)

    def download(name, revision):
        return Path(hf_hub_download(SPACE, name, repo_type="space", revision=revision,
                                    token=token or False)).read_bytes()

    if api.repo_info(SPACE, repo_type="space").sha != BASE:
        raise RuntimeError("Space advanced since verification. Rebase and verify the narrow patch.")
    before, after = prepare(download)
    if args.mode == "inspect":
        return
    if not token or os.getenv("SWRLZ_FORGE_REFERENCE_ROUTING_APPROVED") != "1":
        raise RuntimeError("Approved release credentials are required")

    def commit(directory, parent, message):
        return api.create_commit(
            repo_id=SPACE, repo_type="space", parent_commit=parent, commit_message=message,
            operations=[CommitOperationAdd(path_in_repo=name, path_or_fileobj=str(directory / name))
                        for name in FILES],
        ).oid

    revision = commit(after, BASE, "Preserve native modeling intent and verified image evidence")
    (RECEIPT / "publication.json").write_text(json.dumps({"base": BASE, "published": revision, "verified": False}))
    print("FORGE_REFERENCE_ROUTING_PUBLISHED", revision, flush=True)
    try:
        for name in FILES:
            if download(name, revision) != (after / name).read_bytes():
                raise RuntimeError(f"Published bytes mismatch for {name}")
        wait_until_serving(api, revision)
    except Exception:
        if api.repo_info(SPACE, repo_type="space").sha == revision:
            rollback = commit(before, revision, "Restore source after Forge routing readiness failure")
            print("FORGE_REFERENCE_ROUTING_ROLLBACK", rollback, flush=True)
        raise
    (RECEIPT / "publication.json").write_text(json.dumps({"base": BASE, "published": revision, "verified": True}))
    print("FORGE_REFERENCE_ROUTING_LIVE", revision, flush=True)


if __name__ == "__main__":
    main()
