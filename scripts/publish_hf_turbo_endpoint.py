"""Regression rollback for §C Local Turbo speech recognition.

Restores the exact previously tested v1.1.35 Vosk JS after v1.1.36 made
device recognition worse. Does not revert CPU tuning, regular Browser Talk,
normal Local mode, cached weights or any other Chat features. Version-bumps
the live page to 1.1.37 so Android fetches the restored script.

Prepare saves live production bytes; publish requires the same HF revision and
a successful rollback artifact upload from the existing GitHub workflow.
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
LOCAL = "chat/§wyrlz/assets/local_voice_vosk.js"
FILES = {PAGE:"index.html", LOCAL:"local_voice_vosk.js"}
BEFORE = Path("hf-turbo-endpoint-rollback")
AFTER = Path("hf-turbo-endpoint-candidate")
SOURCE = Path("voice-turbo-source")
TOKEN = os.environ.get("HF_TOKEN") or ""
# Immutable source comparison. Git blob IDs not ordinary SHA256 sums.
BROKEN_LIVE_BLOB = "632bdb17671a5e550f94fd0c471e659e70a9f08e"
KNOWN_BETTER_BLOB = "21e03c72471536d72de4ed70ae6d2808fd261164"

def sha256(data:bytes)->str:
    return hashlib.sha256(data).hexdigest()

def git_blob(data:bytes)->str:
    return hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()

def get_live(path:str, revision:str)->bytes:
    return Path(hf_hub_download(
        SPACE,path,repo_type="space",revision=revision,token=TOKEN
    )).read_bytes()

def patch_once(src:str, old:str, new:str, label:str)->str:
    if src.count(old)!=1 or new in src:
        raise RuntimeError("Live Chat source drift: "+label)
    return src.replace(old,new,1)

def check_js(file:Path)->None:
    subprocess.run(["node","--check",str(file)],check=True)

def prepare(api:HfApi)->None:
    revision=api.repo_info(SPACE,repo_type="space").sha
    listing=set(api.list_repo_files(SPACE,repo_type="space",revision=revision))
    if not set(FILES).issubset(listing):
        raise RuntimeError("Live Chat or Vosk asset unavailable; no deployment")
    old={path:get_live(path,revision) for path in FILES}
    page=old[PAGE].decode("utf-8")
    if git_blob(old[LOCAL])!=BROKEN_LIVE_BLOB:
        raise RuntimeError("Live Vosk differs from the expected v1.1.36 regression")
    if not (10000<len(old[PAGE])<2_000_000 and 10000<len(old[LOCAL])<100_000):
        raise RuntimeError("Unexpected live file size")
    for marker in ('id="voiceProviderSelect"', 'value="turbo"',
                   'swrlz-voice-delta', 'id="voiceConversationButton"'):
        if marker not in page:
            raise RuntimeError("Required Talk baseline missing: "+marker)
    new_page=patch_once(
        page,
        '<meta name="swrlz-chat-version" content="1.1.36">',
        '<meta name="swrlz-chat-version" content="1.1.37">',
        "version metadata")
    new_page=patch_once(
        new_page,
        'const SWRLZ_CHAT_VERSION = "1.1.36";',
        'const SWRLZ_CHAT_VERSION = "1.1.37";',
        "version JavaScript")
    new_page=patch_once(
        new_page,
        '/chat/§wyrlz/assets/local_voice_vosk.js?v=1.1.36',
        '/chat/§wyrlz/assets/local_voice_vosk.js?v=1.1.37',
        "Vosk browser cache invalidation")

    candidate=(SOURCE/LOCAL).read_bytes()
    if git_blob(candidate)!=KNOWN_BETTER_BLOB:
        raise RuntimeError("Rollback Vosk does not match the reviewed v1.1.35 source")
    body=candidate.decode("utf-8")
    for marker in ("TURBO_QUIET_FINAL_MS = 1700", "committedSegments",
                   "new available.KaldiRecognizer(sampleRate)",
                   "turbo ? 2048 : 4096", "window.caches.open(MODEL_CACHE)"):
        if marker not in body:
            raise RuntimeError("Required prior Turbo functionality missing: "+marker)
    for test in (
        "test_chat_streaming_voice.cjs",
        "test_chat_local_streaming_vosk.cjs",
        "test_chat_local_vosk_recovery.cjs",
        "test_chat_local_turbo.cjs",
    ):
        file=SOURCE/"scripts"/test
        check_js(file)
        subprocess.run(["node",str(file)],check=True)
    check_js(SOURCE/LOCAL)
    for i,body in enumerate(re.findall(r'<script(?:\s[^>]*)?>([\s\S]*?)</script>',new_page)):
        if body.strip():
            path=Path(f"restore-voice-inline-{i}.js")
            try:
                path.write_text(body,encoding="utf8")
                check_js(path)
            finally:
                path.unlink(missing_ok=True)

    BEFORE.mkdir(exist_ok=False)
    AFTER.mkdir(exist_ok=False)
    for path,filename in FILES.items():
        (BEFORE/filename).write_bytes(old[path])
    (AFTER/"index.html").write_text(new_page,encoding="utf8")
    (AFTER/"local_voice_vosk.js").write_bytes(candidate)
    manifest={
        "space":SPACE,
        "revision":revision,
        "version":"1.1.37",
        "scope":list(FILES),
        "original":{path:sha256(blob) for path,blob in old.items()},
        "candidate":{path:sha256((AFTER/name).read_bytes()) for path,name in FILES.items()},
        "reason":"Restore prior recognition behavior after device regression",
        "billingChange":"none",
    }
    (BEFORE/"manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf8")
    print(json.dumps({"status":"VOSK_RESTORE_PREPARED_NOT_PUBLISHED",
                      "sourceRevision":revision,"scope":list(FILES),"tests":"PASS"}))

def publish(api:HfApi)->None:
    manifest=json.loads((BEFORE/"manifest.json").read_text(encoding="utf8"))
    revision=manifest["revision"]
    if manifest.get("space")!=SPACE or manifest["scope"]!=list(FILES):
        raise RuntimeError("Invalid target or rollback file scope")
    if api.repo_info(SPACE,repo_type="space").sha!=revision:
        raise RuntimeError("HF source advanced after prepare: refuse stale overwrite")
    ops=[]
    for path,name in FILES.items():
        if sha256((BEFORE/name).read_bytes())!=manifest["original"][path]:
            raise RuntimeError("Rollback artifact integrity failure: "+path)
        if sha256((AFTER/name).read_bytes())!=manifest["candidate"][path]:
            raise RuntimeError("Candidate artifact integrity failure: "+path)
        ops.append(CommitOperationAdd(path_in_repo=path,path_or_fileobj=str(AFTER/name)))
    receipt=api.create_commit(
        repo_id=SPACE,repo_type="space",operations=ops,parent_commit=revision,
        commit_message="Restore §C Local Turbo v1.1.35 speech recognition after v1.1.36 regression")
    new_sha=str(getattr(receipt,"oid","") or api.repo_info(SPACE,repo_type="space").sha)
    for path in FILES:
        if sha256(get_live(path,new_sha))!=manifest["candidate"][path]:
            raise RuntimeError("Published restoration failed integrity check: "+path)
    print(json.dumps({"status":"HF_VOSK_RESTORE_SOURCE_PUBLISHED",
                      "space":SPACE,"revision":new_sha,"version":"1.1.37",
                      "restoredVoskSource":"1.1.35","billingChange":"none",
                      "deviceTest":"NOT_VERIFIED"}))

if __name__=="__main__":
    if len(sys.argv)!=2 or sys.argv[1] not in ("prepare","publish"):
        raise SystemExit("Usage: publish_hf_turbo_endpoint.py prepare|publish")
    if not TOKEN:
        raise SystemExit("HF_TOKEN missing; production unchanged")
    client=HfApi(token=TOKEN)
    (prepare if sys.argv[1]=="prepare" else publish)(client)
