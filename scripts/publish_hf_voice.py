"""Guarded, voice-only Chat release for the existing kamiloki/Swyrlz Space.

Prepare snapshots current live HTML and patches it additively. Publish after
GitHub has stored the rollback artifact. Does not replace models or server.
"""
from __future__ import annotations
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from huggingface_hub import CommitOperationAdd, HfApi, hf_hub_download

SPACE = "kamiloki/Swyrlz"
PAGE = "chat/§wyrlz/index.html"
VOICE = "chat/§wyrlz/assets/voice_conversation.js"
BEFORE = Path("hf-voice-rollback")
AFTER = Path("hf-voice-candidate")
SOURCE = Path("voice-source")
TOKEN = os.environ.get("HF_TOKEN") or ""

def digest(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()

def download(path: str, revision: str) -> bytes:
    return Path(hf_hub_download(SPACE, path, repo_type="space", revision=revision, token=TOKEN)).read_bytes()

def prepare(api: HfApi) -> None:
    info = api.repo_info(SPACE, repo_type="space")
    paths = set(api.list_repo_files(SPACE, repo_type="space", revision=info.sha))
    if PAGE not in paths or VOICE in paths:
        raise RuntimeError("Unsupported live page or voice is already installed; no upload")
    original = download(PAGE, info.sha)
    if not 10_000 < len(original) < 2_000_000:
        raise RuntimeError("Unexpected canonical Chat page size; no upload")
    BEFORE.mkdir(exist_ok=False)
    AFTER.mkdir(exist_ok=False)
    (BEFORE / "index.html").write_bytes(original)
    (BEFORE / "manifest.json").write_text(json.dumps({
        "space": SPACE, "revision": info.sha, "page": PAGE,
        "sha256": digest(original)
    }, indent=2), encoding="utf8")
    patch = SOURCE / "scripts/patch_hf_live_voice.cjs"
    voice = SOURCE / VOICE
    subprocess.run(["node", "--check", str(patch)], check=True)
    subprocess.run(["node", "--check", str(voice)], check=True)
    subprocess.run(["node", str(patch), str(BEFORE / "index.html"), str(AFTER / "index.html")], check=True)
    (AFTER / "voice_conversation.js").write_bytes(voice.read_bytes())
    html = (AFTER / "index.html").read_text(encoding="utf8")
    if html.count('id="voiceConversationButton"') != 1 or html.count('/chat/§wyrlz/assets/voice_conversation.js') != 1:
        raise RuntimeError("HTML voice integration invalid")
    for index, code in enumerate(re.findall(r'<script(?:\s[^>]*)?>([\s\S]*?)</script>', html)):
        if code.strip():
            filename = AFTER / f"inline-{index}.js"
            filename.write_text(code, encoding="utf8")
            subprocess.run(["node", "--check", str(filename)], check=True)
    print(json.dumps({"result":"PREPARED_NOT_PUBLISHED","previousRevision":info.sha,"voice":True}))

def publish(api: HfApi) -> None:
    manifest = json.loads((BEFORE / "manifest.json").read_text(encoding="utf8"))
    original = (BEFORE / "index.html").read_bytes()
    if manifest["space"] != SPACE or manifest["page"] != PAGE or digest(original) != manifest["sha256"]:
        raise RuntimeError("Rollback snapshot failed integrity guard")
    current = api.repo_info(SPACE, repo_type="space")
    if current.sha != manifest["revision"]:
        raise RuntimeError("Live Space advanced after snapshot: refuse stale deployment")
    files = [(PAGE,"index.html"), (VOICE,"voice_conversation.js")]
    operations = [CommitOperationAdd(path_in_repo=path, path_or_fileobj=str(AFTER / name)) for path, name in files]
    receipt = api.create_commit(
        repo_id=SPACE, repo_type="space", operations=operations,
        parent_commit=manifest["revision"],
        commit_message="Scoped §wyrlz Chat live speech · browser APIs only",
    )
    revision = str(getattr(receipt, "oid", "") or api.repo_info(SPACE, repo_type="space").sha)
    for path, name in files:
        expected = (AFTER / name).read_bytes()
        actual = download(path, revision)
        if digest(actual) != digest(expected):
            raise RuntimeError("Post-upload content mismatch for "+path)
    print(json.dumps({
        "result":"HF_SOURCE_PUBLISHED","space":SPACE,
        "previousRevision":manifest["revision"],"revision":revision,
        "changedPaths":[p for p,_ in files],
        "liveRuntimeAndDeviceAcceptance":"NOT_YET_VERIFIED",
    }))

if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in {"prepare", "publish"}:
        raise SystemExit("Usage: publish_hf_voice.py prepare|publish")
    if not TOKEN:
        raise SystemExit("Missing existing HF_TOKEN; no upload")
    client = HfApi(token=TOKEN)
    if sys.argv[1] == "prepare":
        prepare(client)
    else:
        publish(client)
