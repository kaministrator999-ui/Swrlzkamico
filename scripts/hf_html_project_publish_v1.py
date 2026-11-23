#!/usr/bin/env python3
"""Publish one owner-approved static HTML project into the existing §C HF Space.

Runs only in a GitHub Actions runner with the existing HF_TOKEN secret.
Never updates Station, engine files, or an arbitrary Space path.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import urllib.error
import urllib.request

SPACE = "kamiloki/Swyrlz"
BASE_URL = "https://kamiloki-swyrlz.hf.space"
SOURCE_ROOT = Path(os.environ.get("SWRLZ_PROJECT_SOURCE_ROOT", "."))
PROJECT_ROOT = SOURCE_ROOT / "html-projects"
MAX_FILES = 48
MAX_TOTAL_BYTES = 1_000_000
ALLOWED = {".html", ".htm", ".css", ".js", ".mjs", ".json", ".svg",
           ".png", ".jpg", ".jpeg", ".webp", ".gif", ".ico", ".woff", ".woff2"}
SLUG = re.compile(r"[a-z0-9](?:[a-z0-9-]{0,46}[a-z0-9])?\Z")
SHA = re.compile(r"[0-9a-f]{40}\Z")


def validate_slug(slug: str) -> str:
    if not SLUG.fullmatch(slug):
        raise ValueError("Invalid project slug")
    return slug


def local_files(slug: str) -> list[tuple[str, bytes]]:
    candidate = PROJECT_ROOT / validate_slug(slug)
    if PROJECT_ROOT.is_symlink() or candidate.is_symlink():
        raise ValueError("Symlink project root forbidden")
    root = candidate.resolve()
    parent = PROJECT_ROOT.resolve()
    if root.parent != parent or not root.is_dir():
        raise ValueError("Project directory missing")
    output = []
    total = 0
    for directory in root.rglob("*"):
        if directory.is_symlink():
            raise ValueError("Symlink forbidden")
    for file in sorted(root.rglob("*")):
        if file.is_symlink():
            raise ValueError("Symlink forbidden")
        if not file.is_file():
            continue
        rel = file.relative_to(root).as_posix()
        p = PurePosixPath(rel)
        if len(p.parts) > 8 or any(x.startswith(".") for x in p.parts):
            raise ValueError("Hidden or deeply nested path forbidden")
        if not all(re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_.-]*", part) for part in p.parts):
            raise ValueError("Invalid project asset name: " + rel)
        if p.suffix.lower() not in ALLOWED:
            raise ValueError("File extension not approved: " + rel)
        data = file.read_bytes()
        total += len(data)
        if total > MAX_TOTAL_BYTES or len(output) >= MAX_FILES:
            raise ValueError("Project exceeds publication limits")
        if p.suffix.lower() in {".html", ".htm", ".css", ".js", ".mjs", ".json", ".svg"}:
            data.decode("utf-8")
        output.append((rel, data))
    if not any(p == "index.html" for p, _ in output):
        raise ValueError("index.html is required")
    for rel, data in output:
        if rel.endswith((".html", ".htm")) and not data.strip():
            raise ValueError("Empty HTML entry")
    return output


def manifest(slug: str) -> dict:
    files = local_files(slug)
    return {"space": SPACE, "project": slug, "count": len(files),
            "bytes": sum(len(data) for _, data in files),
            "paths": {rel: hashlib.sha256(data).hexdigest() for rel, data in files},
            "destinationPrefix": "chat/§wyrlz/projects/" + slug + "/",
            "url": BASE_URL + "/chat/%C2%A7wyrlz/projects/" + slug + "/index.html"}


def assert_immutable_source() -> str:
    expected = os.environ.get("SOURCE_SHA", "")
    if not SHA.fullmatch(expected):
        raise ValueError("An immutable 40-character source SHA is mandatory")
    import subprocess
    actual = subprocess.check_output(["git", "-C", str(SOURCE_ROOT), "rev-parse", "HEAD"], text=True).strip()
    if actual != expected:
        raise ValueError("Approved source does not match checked-out source")
    return actual


def publish(slug: str, approved: str) -> dict:
    if approved != "yes" or os.getenv("SWRLZ_HTML_PROJECT_APPROVED") != "1":
        raise PermissionError("Publication requires explicit owner approval")
    assert_immutable_source()
    token = os.environ.get("HF_TOKEN", "")
    if not token:
        raise PermissionError("HF_TOKEN is missing")
    from huggingface_hub import HfApi, CommitOperationAdd, hf_hub_download
    api = HfApi(token=token)
    revision = str(api.repo_info(SPACE, repo_type="space").sha)
    if not SHA.fullmatch(revision):
        raise RuntimeError("Live Space revision unavailable")
    prefix = "chat/§wyrlz/projects/" + slug + "/"
    files = local_files(slug)
    existing = set(api.list_repo_files(SPACE, repo_type="space", revision=revision))
    # Preserve every file outside this project's private prefix.
    existing_project = {p for p in existing if p.startswith(prefix)}
    # Do not silently remove files that belonged to another project version.
    expected = {prefix + rel for rel, _ in files}
    stale = sorted(existing_project - expected)
    if stale:
        raise RuntimeError("Project contains previously published files not in source; explicit deletion workflow required")
    ops = [CommitOperationAdd(path_in_repo=prefix + rel, path_or_fileobj=io.BytesIO(data))
           for rel, data in files]
    if str(api.repo_info(SPACE, repo_type="space").sha) != revision:
        raise RuntimeError("Space changed during preflight")
    result = api.create_commit(repo_id=SPACE, repo_type="space", parent_commit=revision,
                               operations=ops, commit_message="publish(§C): HTML project " + slug)
    published = result.oid
    for rel, raw in files:
        got = Path(hf_hub_download(SPACE, prefix + rel, repo_type="space", revision=published, token=token)).read_bytes()
        if got != raw:
            raise RuntimeError("Published bytes mismatch: " + rel)
    receipt = manifest(slug)
    receipt.update(sourceSha=os.environ["SOURCE_SHA"], beforeRevision=revision,
                   spaceRevision=published, verifiedSource=True, runtimeVerified=False)
    Path("html-project-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    return receipt


def runtime_probe(url: str) -> None:
    import time
    request = urllib.request.Request(url, headers={"Cache-Control": "no-cache"})
    for attempt in range(12):
        try:
            with urllib.request.urlopen(request, timeout=15) as response:
                mime = response.headers.get("Content-Type", "").lower()
                disposition = response.headers.get("Content-Disposition", "").lower()
                body = response.read(512_000)
                if response.status == 200 and "text/html" in mime and "attachment" not in disposition and body:
                    return
        except (urllib.error.URLError, TimeoutError):
            pass
        if attempt < 11:
            time.sleep(5)
    raise RuntimeError("Browser-facing HTML was not verified; source publication is not runtime success")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["validate", "publish", "probe"])
    parser.add_argument("--project", required=True)
    parser.add_argument("--approved", default="no", choices=["yes", "no"])
    args = parser.parse_args()
    receipt = manifest(args.project)
    if args.mode == "validate":
        print("HTML_PROJECT_VALIDATED", json.dumps(receipt, sort_keys=True))
    elif args.mode == "publish":
        print("HTML_PROJECT_SOURCE_PUBLISHED", json.dumps(publish(args.project, args.approved), sort_keys=True))
    else:
        runtime_probe(receipt["url"])
        receipt_path = Path("html-project-receipt.json")
        if receipt_path.exists():
            published_receipt = json.loads(receipt_path.read_text())
            if published_receipt.get("url") != receipt["url"]:
                raise RuntimeError("Receipt URL and probed URL differ")
            published_receipt["runtimeVerified"] = True
            receipt_path.write_text(json.dumps(published_receipt, indent=2) + "\n")
        print("HTML_PROJECT_RUNTIME_VERIFIED", receipt["url"])


if __name__ == "__main__":
    main()
