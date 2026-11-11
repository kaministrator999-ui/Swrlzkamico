"""Guarded §C Browser Turbo release: preserve offline Vosk and unrelated Space code.

Release only the live Chat selector/version and its Talk controller. Reject
unexpected source, live version, other edits, and concurrent Space changes.
Use the existing HF_TOKEN and rollback-artifact process; no paid speech API.
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
CONTROLLER = "chat/§wyrlz/assets/voice_conversation.js"
LOCAL = "chat/§wyrlz/assets/local_voice_vosk.js"
BEFORE = Path("hf-browser-turbo-rollback")
AFTER = Path("hf-browser-turbo-candidate")
SOURCE = Path("voice-turbo-source")
TOKEN = os.environ.get("HF_TOKEN") or ""
OLD_CONTROLLER_BLOBS = {
    "beedc0a31a1055092309ea67c22d197be1f6063e",
    "389f595c09e6f83aaf03fb9890d03d8483fac127",
}
APPROVED_LOCAL_BLOB = "c9b6b052e73994d41702cb1c0014e5df91db632d"

OLD_SELECTOR = '''          <select id="voiceProviderSelect" aria-label="Talk speech recognition mode" title="Browser default, or opt into ~41 MB on-device streaming transcription">
            <option value="browser" selected>Browser</option>
            <option value="local">Local stream · 41 MB</option>
            <option value="turbo">Local Turbo · 41 MB</option>'''

NEW_SELECTOR = '''          <select id="voiceProviderSelect" aria-label="Talk speech recognition mode" title="Browser and Browser Turbo may use online speech recognition. Offline Local and Local Turbo use an optional ~41 MB on-device model.">
            <option value="browser">Browser</option>
            <option value="turbo" selected>Turbo · Browser recognition</option>
            <option value="local">Local stream · offline · 41 MB</option>
            <option value="local-turbo">Local Turbo · offline · 41 MB</option>'''

def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def git_blob(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()

def live_bytes(path: str, revision: str) -> bytes:
    return Path(hf_hub_download(
        SPACE, path, repo_type="space", revision=revision, token=TOKEN
    )).read_bytes()

def replace_once(contents: str, before: str, after: str, label: str) -> str:
    if before == after or contents.count(before) != 1 or after in contents:
        raise RuntimeError("Live source drift: " + label)
    return contents.replace(before, after, 1)

def run_validation(controller: Path, page: Path) -> None:
    subprocess.run(["node", "--check", str(controller)], check=True)
    for filename in (
        "test_chat_browser_turbo.cjs",
        "test_chat_streaming_voice.cjs",
        "test_chat_local_voice_accuracy_v6.cjs",
        "test_chat_local_streaming_vosk.cjs",
        "test_chat_local_vosk_recovery.cjs",
        "test_chat_local_turbo.cjs",
    ):
        subprocess.run(["node", str(SOURCE / "scripts" / filename)], check=True)
    for index, body in enumerate(re.findall(
        r"<script(?:\s[^>]*)?>([\s\S]*?)</script>",
        page.read_text(encoding="utf-8")
    )):
        if not body.strip():
            continue
        tmp = Path(f"browser-turbo-inline-{index}.js")
        try:
            tmp.write_text(body, encoding="utf-8")
            subprocess.run(["node", "--check", str(tmp)], check=True)
        finally:
            tmp.unlink(missing_ok=True)

def prepare(api: HfApi) -> None:
    revision = api.repo_info(SPACE, repo_type="space").sha
    available = set(api.list_repo_files(SPACE, repo_type="space", revision=revision))
    if not {PAGE, CONTROLLER, LOCAL}.issubset(available):
        raise RuntimeError("Live Chat/Talk/offline model assets missing")
    old_page = live_bytes(PAGE, revision)
    old_controller = live_bytes(CONTROLLER, revision)
    old_local = live_bytes(LOCAL, revision)
    if not (10000 < len(old_page) < 2_000_000 and
            5000 < len(old_controller) < 60000 and
            10000 < len(old_local) < 100000):
        raise RuntimeError("Unexpected live file size")
    actual_controller = git_blob(old_controller)
    if actual_controller not in OLD_CONTROLLER_BLOBS:
        raise RuntimeError("Unreviewed live Talk controller: " + actual_controller)
    if git_blob(old_local) != APPROVED_LOCAL_BLOB:
        raise RuntimeError("Offline Vosk source differs from approved v1.1.37")
    html = old_page.decode("utf-8")
    version = re.search(r'<meta name="swrlz-chat-version" content="1\.1\.(\d+)">', html)
    if not version or version.group(1) != "37":
        raise RuntimeError("Live Chat is not 1.1.37; refuse overwriting newer release")
    if html.count('id="voiceConversationButton"') != 1 or html.count(
            'value="turbo"') != 1 or html.count('value="local"') != 1:
        raise RuntimeError("Unexpected existing Talk UI")
    updated = replace_once(html, OLD_SELECTOR, NEW_SELECTOR, "voice selector")
    updated = replace_once(
        updated, version.group(0),
        '<meta name="swrlz-chat-version" content="1.1.38">', "version meta")
    updated = replace_once(
        updated, 'const SWRLZ_CHAT_VERSION = "1.1.37";',
        'const SWRLZ_CHAT_VERSION = "1.1.38";', "version constant")
    updated = replace_once(
        updated, '/chat/§wyrlz/assets/voice_conversation.js?v=1.1.34',
        '/chat/§wyrlz/assets/voice_conversation.js?v=1.1.38',
        "Talk cache-bust")
    if updated.count('value="local-turbo"') != 1 or updated.count(
            'value="turbo"') != 1 or updated.count(
            'id="voiceConversationButton"') != 1:
        raise RuntimeError("Unexpected candidate Talk options")
    if '/chat/§wyrlz/assets/local_voice_vosk.js?v=1.1.37' not in updated:
        raise RuntimeError("Offline Vosk cache-bust changed; scope violation")

    source_controller = (SOURCE / CONTROLLER).read_bytes()
    source_page = (SOURCE / PAGE).read_text(encoding="utf-8")
    if git_blob(source_controller) != "6ec974e5e02f21b55169ded898d3eba95e0d3d1c":
        raise RuntimeError("Reviewed Browser Turbo controller hash changed")
    if NEW_SELECTOR not in source_page:
        raise RuntimeError("Approved source selector differs from release candidate")
    candidate_text = source_controller.decode("utf-8")
    required = (
        "const localTurboSelected =",
        "const fastSpeechSelected =",
        "const local = localSelected();",
        "if (localTurboSelected()) instance.turbo = true;",
        'engine: local ? (localTurboSelected() ? "local-vosk-turbo"',
        'utterance.rate = fastSpeechSelected() ? 1.14 : 1;',
        'const earlyPhraseLimit = fastSpeechSelected() ? 95 : 170;',
        "const Recognition = local ? window.SwrlzLocalSpeechRecognition : BrowserRecognition;",
    )
    if not all(marker in candidate_text for marker in required):
        raise RuntimeError("Approved Browser Turbo and offline guards incomplete")
    BEFORE.mkdir(exist_ok=False)
    AFTER.mkdir(exist_ok=False)
    (BEFORE / "index.html").write_bytes(old_page)
    (BEFORE / "voice_conversation.js").write_bytes(old_controller)
    (BEFORE / "local_voice_vosk.js").write_bytes(old_local)
    (AFTER / "index.html").write_text(updated, encoding="utf-8")
    (AFTER / "voice_conversation.js").write_bytes(source_controller)
    run_validation(AFTER / "voice_conversation.js", AFTER / "index.html")
    changed = [PAGE, CONTROLLER]
    before = {PAGE: digest(old_page), CONTROLLER: digest(old_controller),
              LOCAL: digest(old_local)}
    after = {PAGE: digest((AFTER / "index.html").read_bytes()),
             CONTROLLER: digest(source_controller)}
    manifest = {"space": SPACE, "previousRevision": revision,
                "version": "1.1.38", "before": before, "after": after,
                "changedPaths": changed, "billingChange": "none"}
    (BEFORE / "manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps({"status": "BROWSER_TURBO_PREPARED",
                      "fromRevision": revision,
                      "changedPaths": changed, "offlineVosk": "UNCHANGED",
                      "tests": "PASS"}))

def publish(api: HfApi) -> None:
    manifest = json.loads((BEFORE / "manifest.json").read_text(
        encoding="utf-8"))
    prior = manifest["previousRevision"]
    changed = [PAGE, CONTROLLER]
    if manifest.get("space") != SPACE or manifest.get("changedPaths") != changed:
        raise RuntimeError("Unexpected publish scope")
    if api.repo_info(SPACE, repo_type="space").sha != prior:
        raise RuntimeError("Space advanced during release; refuse stale overwrite")
    old_files = {PAGE: "index.html", CONTROLLER: "voice_conversation.js",
                 LOCAL: "local_voice_vosk.js"}
    new_files = {PAGE: "index.html", CONTROLLER: "voice_conversation.js"}
    for path, filename in old_files.items():
        if digest((BEFORE / filename).read_bytes()) != manifest["before"][path]:
            raise RuntimeError("Rollback backup corrupted: " + path)
    for path, filename in new_files.items():
        if digest((AFTER / filename).read_bytes()) != manifest["after"][path]:
            raise RuntimeError("Release candidate changed: " + path)
    receipt = api.create_commit(
        repo_id=SPACE, repo_type="space", parent_commit=prior,
        operations=[
            CommitOperationAdd(path_in_repo=path,
                               path_or_fileobj=str(AFTER / filename))
            for path, filename in new_files.items()
        ],
        commit_message="§C v1.1.38: Browser Turbo recognition with offline modes retained")
    sha = str(getattr(receipt, "oid", "") or api.repo_info(
        SPACE, repo_type="space").sha)
    for path in changed:
        if digest(live_bytes(path, sha)) != manifest["after"][path]:
            raise RuntimeError("Published file checksum mismatch: " + path)
    if digest(live_bytes(LOCAL, sha)) != manifest["before"][LOCAL]:
        raise RuntimeError("Offline Vosk unexpectedly changed")
    print(json.dumps({
        "status": "HF_BROWSER_TURBO_PUBLISHED",
        "space": SPACE, "revision": sha, "version": "1.1.38",
        "paths": changed, "offlineVosk": "UNCHANGED",
        "billingChange": "none", "deviceAcceptance": "NOT_VERIFIED"}))

if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ("prepare", "publish"):
        raise SystemExit("Usage: publish_hf_browser_turbo.py prepare|publish")
    if not TOKEN:
        raise SystemExit("HF_TOKEN missing; production unchanged")
    api = HfApi(token=TOKEN)
    (prepare if sys.argv[1] == "prepare" else publish)(api)
