#!/usr/bin/env python3
"""Guarded, source-pinned Gradio launch hook for §C's existing ASGI-mounted ZeroGPU Space.

Patches only app.py's startup seam. The existing Station API/root, /probe, /legacy,
model checkpoint, account storage, secrets, hardware and app dependencies remain unchanged.
Never publish without explicit approved request + expected exact HF revision.
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import re
import sys
from pathlib import Path

SPACE = "kamiloki/Swyrlz"
FILE = "app.py"
ROOT = Path("reports/chat-zerogpu-launch-bridge-v1")
TAG = "swrlz-zerogpu-gradio-launch-bridge-v1"
OLD = '''    _warm_backends()
    # Bind the Python ASGI app to the Space application port.'''
NEW = '''    # swrlz-zerogpu-gradio-launch-bridge-v1: the mounted /probe Blocks
    # has a real @spaces.GPU-bound event, but mount_gradio_app + uvicorn
    # never fires Gradio's launch hook. Launch that existing Blocks once
    # on a private loopback port solely to register the ZeroGPU handler.
    # The public Station ASGI app still owns port 7860 and all its routes.
    _gradio_port_previous=os.environ.get("GRADIO_SERVER_PORT")
    os.environ["GRADIO_SERVER_PORT"]="7861"
    try:
        demo.launch(server_name="127.0.0.1",server_port=7861,
                    prevent_thread_lock=True,share=False,quiet=True,
                    ssr_mode=False)
    finally:
        if _gradio_port_previous is None:
            os.environ.pop("GRADIO_SERVER_PORT",None)
        else:
            os.environ["GRADIO_SERVER_PORT"]=_gradio_port_previous
    print(json.dumps({"event":"ZEROGPU_GRADIO_LAUNCH_REGISTERED",
                      "publicServer":"ASGI","probePort":7861}),flush=True)
    _warm_backends()
    # Bind the Python ASGI app to the Space application port.'''


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def patch(original: bytes) -> bytes:
    source = original.decode("utf-8")
    if TAG in source:
        raise RuntimeError("BRIDGE_ALREADY_INSTALLED")
    if source.count(OLD) != 1:
        raise RuntimeError("UNSAFE_STARTUP_SOURCE_DRIFT")
    for invariant in (
        "@spaces.GPU(duration=1)",
        "_zg_button.click(fn=_zerogpu_registration_probe",
        'app=gr.mount_gradio_app(station_app,demo,path="/probe",ssr_mode=False)',
        'app=gr.mount_gradio_app(app,legacy["demo"],path="/legacy",ssr_mode=False)',
        'uvicorn.run(app,host="0.0.0.0"',
    ):
        if invariant not in source:
            raise RuntimeError("EXPECTED_ASGI_OR_GPU_HANDLER_MISSING:" + invariant[:70])
    candidate = source.replace(OLD, NEW, 1)
    ast.parse(candidate, filename=FILE)
    if candidate.replace(NEW, OLD, 1) != source:
        raise AssertionError("UNRELATED_SOURCE_MODIFICATION")
    if candidate.count(TAG) != 1:
        raise AssertionError("MISSING_BRIDGE_TAG")
    return candidate.encode("utf-8")


def test(original: bytes, candidate: bytes) -> None:
    source = candidate.decode("utf-8")
    tree = ast.parse(source)
    mains = [
        node for node in tree.body if isinstance(node, ast.If)
        and isinstance(node.test, ast.Compare)
        and "__name__" in (ast.get_source_segment(source, node.test) or "")
    ]
    if len(mains) != 1:
        raise AssertionError("EXPECTED_ONE_MAIN_ENTRYPOINT")
    body = ast.get_source_segment(source, mains[0])
    assert body and body.index("demo.launch(") < body.index("_warm_backends()")
    assert body.index("_warm_backends()") < body.index("uvicorn.run(")
    assert '"GRADIO_SERVER_PORT"="7861"' not in body
    for seam in ("_gradio_port_previous", 'os.environ["GRADIO_SERVER_PORT"]="7861"',
                 "server_name=\"127.0.0.1\"", "server_port=7861",
                 "prevent_thread_lock=True", "ssr_mode=False",
                 "os.environ.pop(", "ZEROGPU_GRADIO_LAUNCH_REGISTERED"):
        if seam not in body:
            raise AssertionError("BRIDGE_INVARIANT_MISSING:" + seam)
    if source.replace(NEW, OLD, 1).encode("utf-8") != original:
        raise AssertionError("NOT_A_SINGLE_REVERSIBLE_PATCH")
    print("SWRLZ_ZEROGPU_BRIDGE_OFFLINE_PASS", flush=True)


def snapshot(api, *, expected: str = "") -> dict:
    from huggingface_hub import hf_hub_download
    info = api.repo_info(SPACE, repo_type="space")
    revision = str(info.sha)
    if expected and revision != expected:
        raise RuntimeError("SPACE_REVISION_CHANGED:" + revision)
    if not re.fullmatch(r"[a-f0-9]{40}", revision):
        raise RuntimeError("SPACE_REVISION_INVALID")
    old = Path(hf_hub_download(SPACE, FILE, repo_type="space",
                               revision=revision, token=api.token)).read_bytes()
    new = patch(old)
    test(old, new)
    (ROOT / "before").mkdir(parents=True, exist_ok=True)
    (ROOT / "after").mkdir(parents=True, exist_ok=True)
    (ROOT / "before" / FILE).write_bytes(old)
    (ROOT / "after" / FILE).write_bytes(new)
    manifest = {"space": SPACE, "file": FILE, "revision": revision,
                "beforeSha256": digest(old), "afterSha256": digest(new),
                "published": False, "integrityVerified": True,
                "singleFile": True, "hardwareChanges": False,
                "modelChanges": False, "accountChanges": False}
    (ROOT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print("SWRLZ_ZEROGPU_BRIDGE_PREFLIGHT", json.dumps(manifest), flush=True)
    return manifest


def publish() -> None:
    if os.getenv("SWRLZ_ZEROGPU_BRIDGE_APPROVED") != "1":
        raise RuntimeError("EXPLICIT_RELEASE_APPROVAL_REQUIRED")
    expected = os.getenv("SWRLZ_EXPECTED_SPACE_REVISION", "").strip()
    if not re.fullmatch(r"[a-f0-9]{40}", expected):
        raise RuntimeError("EXPECTED_SPACE_REVISION_REQUIRED")
    token = os.getenv("HF_TOKEN")
    if not token:
        raise RuntimeError("HF_TOKEN_REQUIRED")
    from huggingface_hub import HfApi, CommitOperationAdd, hf_hub_download
    api = HfApi(token=token)
    manifest = snapshot(api, expected=expected)
    old = (ROOT / "before" / FILE).read_bytes()
    new = (ROOT / "after" / FILE).read_bytes()
    if digest(old) != manifest["beforeSha256"] or digest(new) != manifest["afterSha256"]:
        raise RuntimeError("SOURCE_SNAPSHOT_CHANGED")
    if api.repo_info(SPACE, repo_type="space").sha != expected:
        raise RuntimeError("SOURCE_CHANGED_BEFORE_CAS_COMMIT")
    published = None
    try:
        result = api.create_commit(
            repo_id=SPACE, repo_type="space", parent_commit=expected,
            operations=[CommitOperationAdd(path_in_repo=FILE, path_or_fileobj=new)],
            commit_message="§C ZeroGPU: register mounted Gradio probe at launch, keep ASGI Station")
        published = str(result.oid)
        verified = Path(hf_hub_download(SPACE, FILE, repo_type="space",
                                        revision=published, token=token)).read_bytes()
        if verified != new or api.repo_info(SPACE, repo_type="space").sha != published:
            raise RuntimeError("PUBLISHED_SOURCE_READBACK_MISMATCH")
        manifest.update({"published": True, "publishedRevision": published,
                         "verifiedReadback": True})
        (ROOT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
        print("SWRLZ_ZEROGPU_BRIDGE_PUBLISHED", json.dumps(manifest), flush=True)
    except Exception:
        if published and api.repo_info(SPACE, repo_type="space").sha == published:
            api.create_commit(
                repo_id=SPACE, repo_type="space", parent_commit=published,
                operations=[CommitOperationAdd(path_in_repo=FILE, path_or_fileobj=old)],
                commit_message="Rollback §C ZeroGPU bridge to exact previous app.py")
        raise


def rollback() -> None:
    if os.getenv("SWRLZ_ZEROGPU_BRIDGE_APPROVED") != "1":
        raise RuntimeError("ROLLBACK_APPROVAL_REQUIRED")
    from huggingface_hub import HfApi, CommitOperationAdd, hf_hub_download
    api = HfApi(token=os.environ["HF_TOKEN"])
    manifest = json.loads((ROOT / "manifest.json").read_text())
    published = str(manifest.get("publishedRevision") or "")
    if not manifest.get("published") or not re.fullmatch(r"[a-f0-9]{40}", published):
        raise RuntimeError("NO_OWNED_PUBLICATION")
    if api.repo_info(SPACE, repo_type="space").sha != published:
        raise RuntimeError("NEWER_SOURCE_EXISTS_REFUSE_ROLLBACK")
    old = (ROOT / "before" / FILE).read_bytes()
    if digest(old) != manifest["beforeSha256"]:
        raise RuntimeError("ROLLBACK_BACKUP_CHECKSUM_MISMATCH")
    result = api.create_commit(
        repo_id=SPACE, repo_type="space", parent_commit=published,
        operations=[CommitOperationAdd(path_in_repo=FILE, path_or_fileobj=old)],
        commit_message="Rollback §C ZeroGPU launch registration bridge after failed acceptance")
    verified = Path(hf_hub_download(SPACE, FILE, repo_type="space",
                                    revision=str(result.oid), token=api.token)).read_bytes()
    if verified != old:
        raise RuntimeError("ROLLBACK_READBACK_MISMATCH")
    print("SWRLZ_ZEROGPU_BRIDGE_ROLLED_BACK",
          json.dumps({"from": published, "to": str(result.oid)}), flush=True)


if __name__ == "__main__":
    args = sys.argv[1:] or ["inspect"]
    if args == ["inspect"]:
        from huggingface_hub import HfApi
        snapshot(HfApi(token=os.getenv("HF_TOKEN")),
                 expected=os.getenv("SWRLZ_EXPECTED_SPACE_REVISION", "").strip())
    elif args == ["publish"]:
        publish()
    elif args == ["rollback"]:
        rollback()
    else:
        raise SystemExit("Usage: inspect|publish|rollback")
