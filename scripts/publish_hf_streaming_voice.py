"""Guarded incremental Talk patch for the existing HF Chat Space.

Patch only the live HTML Station DELTA bridge and replace its companion voice JS.
Prepare rollback BEFORE publication; stop on drift; no model/server changes.
"""
from __future__ import annotations
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from huggingface_hub import HfApi, CommitOperationAdd, hf_hub_download

SPACE = "kamiloki/Swyrlz"
PAGE = "chat/§wyrlz/index.html"
VOICE = "chat/§wyrlz/assets/voice_conversation.js"
BEFORE = Path("hf-streaming-voice-rollback")
AFTER = Path("hf-streaming-voice-candidate")
SOURCE = Path("voice-streaming-source")
TOKEN = os.environ.get("HF_TOKEN") or ""

def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()

def live_blob(path: str, revision: str) -> bytes:
    return Path(hf_hub_download(SPACE, path, repo_type="space",
                                revision=revision, token=TOKEN)).read_bytes()

def check_node(path: Path) -> None:
    subprocess.run(["node", "--check", str(path)], check=True)

def prepare(api: HfApi) -> None:
    info = api.repo_info(SPACE, repo_type="space")
    paths = set(api.list_repo_files(SPACE, repo_type="space", revision=info.sha))
    if PAGE not in paths or VOICE not in paths:
        raise RuntimeError("Live Talk baseline not installed; no deployment")
    original_page = live_blob(PAGE, info.sha)
    original_voice = live_blob(VOICE, info.sha)
    if not (10000 < len(original_page) < 2_000_000 and 1000 < len(original_voice) < 100000):
        raise RuntimeError("Unexpected live Chat payload size; no deployment")
    BEFORE.mkdir(exist_ok=False)
    AFTER.mkdir(exist_ok=False)
    (BEFORE / "index.html").write_bytes(original_page)
    (BEFORE / "voice_conversation.js").write_bytes(original_voice)
    manifest = {"space": SPACE, "revision": info.sha,
                "original": {PAGE: digest(original_page), VOICE: digest(original_voice)}}
    (BEFORE / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf8")
    patch = SOURCE / "scripts/patch_hf_streaming_voice.cjs"
    test = SOURCE / "scripts/test_chat_streaming_voice.cjs"
    voice = SOURCE / VOICE
    check_node(patch)
    check_node(test)
    check_node(voice)
    # The browser-mock smoke exercises request binding, audio queue,
    # terminal de-duplication and no-resume-while-generating.
    subprocess.run(["node", str(test)], check=True)
    subprocess.run(["node", str(patch), str(BEFORE / "index.html"),
                    str(AFTER / "index.html")], check=True)
    (AFTER / "voice_conversation.js").write_bytes(voice.read_bytes())
    candidate_page = (AFTER / "index.html").read_text(encoding="utf8")
    if candidate_page.count("swrlz-voice-delta") != 1:
        raise RuntimeError("Streaming voice bridge missing/duplicated")
    if candidate_page.count('id="voiceConversationButton"') != 1:
        raise RuntimeError("Talk UI changed unexpectedly")
    if "const receiveDelta" not in voice.read_text(encoding="utf8"):
        raise RuntimeError("Voice incremental controller absent")
    for index, code in enumerate(re.findall(r'<script(?:\s[^>]*)?>([\s\S]*?)</script>', candidate_page)):
        if code.strip():
            filename = AFTER / f"inline-{index}.js"
            filename.write_text(code, encoding="utf8")
            check_node(filename)
    manifest["candidate"] = {PAGE: digest((AFTER / "index.html").read_bytes()),
                             VOICE: digest((AFTER / "voice_conversation.js").read_bytes())}
    (BEFORE / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf8")
    print(json.dumps({"result": "PREPARED_NOT_PUBLISHED", "liveRevision": info.sha,
                      "paths": [PAGE, VOICE], "browserMock": "PASS"}))

def publish(api: HfApi) -> None:
    manifest = json.loads((BEFORE / "manifest.json").read_text(encoding="utf8"))
    if manifest.get("space") != SPACE:
        raise RuntimeError("Wrong release target")
    rev = manifest["revision"]
    if api.repo_info(SPACE, repo_type="space").sha != rev:
        raise RuntimeError("Space advanced since rollback snapshot; refusing stale patch")
    operations = []
    for path, name in [(PAGE, "index.html"), (VOICE, "voice_conversation.js")]:
        original = (BEFORE / name).read_bytes()
        candidate = (AFTER / name).read_bytes()
        if digest(original) != manifest["original"][path] or digest(candidate) != manifest["candidate"][path]:
            raise RuntimeError("Snapshot or candidate digest mismatch: " + path)
        operations.append(CommitOperationAdd(path_in_repo=path, path_or_fileobj=str(AFTER / name)))
    result = api.create_commit(repo_id=SPACE, repo_type="space", operations=operations,
        parent_commit=rev, commit_message="Stream Talk TTS from Station deltas without waiting for entire reply")
    newrev = str(getattr(result, "oid", "") or api.repo_info(SPACE, repo_type="space").sha)
    for path in (PAGE, VOICE):
        if digest(live_blob(path, newrev)) != manifest["candidate"][path]:
            raise RuntimeError("Published Space file mismatched: " + path)
    print(json.dumps({"result": "HF_STREAMING_TALK_SOURCE_PUBLISHED", "space": SPACE,
                      "previousRevision": rev, "revision": newrev,
                      "changedPaths": [PAGE, VOICE], "deviceAcceptance": "NOT_VERIFIED"}))

if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ("prepare", "publish"):
        raise SystemExit("Usage: publish_hf_streaming_voice.py prepare|publish")
    if not TOKEN:
        raise SystemExit("HF_TOKEN absent; no deployment")
    api = HfApi(token=TOKEN)
    if sys.argv[1] == "prepare":
        prepare(api)
    else:
        publish(api)
