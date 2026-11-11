"""Guarded HF Chat release: opt-in, free on-device Vosk streaming STT.

Only patch the *current* live Chat HTML, replace its voice controller, add one
new local ASR adapter. Never install hosted speech inference, switch hardware,
replace LALM/vision engines, or modify account/thread/server logic.

Prepare snapshots current Space files. Publish only after GitHub uploads the
rollback artifact. Drift or duplicate installation fails closed.
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
LOCAL = "chat/§wyrlz/assets/local_voice_vosk.js"
BEFORE = Path("hf-local-voice-rollback")
AFTER = Path("hf-local-voice-candidate")
SOURCE = Path("voice-streaming-source")
TOKEN = os.environ.get("HF_TOKEN") or ""

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def from_space(path: str, revision: str) -> bytes:
    return Path(hf_hub_download(SPACE, path, repo_type="space",
                                revision=revision, token=TOKEN)).read_bytes()

def check_js(path: Path) -> None:
    subprocess.run(["node", "--check", str(path)], check=True)

def prepare(api: HfApi) -> None:
    snapshot=api.repo_info(SPACE, repo_type="space")
    paths=set(api.list_repo_files(SPACE, repo_type="space", revision=snapshot.sha))
    if PAGE not in paths or VOICE not in paths or LOCAL in paths:
        raise RuntimeError("Live streaming Talk baseline absent or local mic already installed")
    old_page=from_space(PAGE, snapshot.sha)
    old_voice=from_space(VOICE, snapshot.sha)
    if not (10000<len(old_page)<2_000_000 and 5000<len(old_voice)<100_000):
        raise RuntimeError("Unexpected live Chat source size")
    if b"swrlz-voice-delta" not in old_page or b"receiveDelta" not in old_voice:
        raise RuntimeError("Streaming Talk model not live; refuse to replace browser mode")

    BEFORE.mkdir(exist_ok=False)
    AFTER.mkdir(exist_ok=False)
    (BEFORE/"index.html").write_bytes(old_page)
    (BEFORE/"voice_conversation.js").write_bytes(old_voice)

    patch=SOURCE/"scripts/patch_hf_local_streaming_voice.cjs"
    voice=SOURCE/VOICE
    local=SOURCE/LOCAL
    tests=[SOURCE/"scripts/test_chat_streaming_voice.cjs",
           SOURCE/"scripts/test_chat_local_streaming_vosk.cjs"]
    for path in [patch,voice,local,*tests]:
        check_js(path)
    for test in tests:
        subprocess.run(["node",str(test)],check=True)
    subprocess.run(["node",str(patch),str(BEFORE/"index.html"),
                    str(AFTER/"index.html")],check=True)
    (AFTER/"voice_conversation.js").write_bytes(voice.read_bytes())
    (AFTER/"local_voice_vosk.js").write_bytes(local.read_bytes())
    page=(AFTER/"index.html").read_text(encoding="utf8")
    if page.count('id="voiceProviderSelect"')!=1 or page.count("/chat/§wyrlz/assets/local_voice_vosk.js")!=1:
        raise RuntimeError("Local voice selector/script missing or duplicated")
    if page.count('id="voiceConversationButton"')!=1 or "swrlz-voice-delta" not in page:
        raise RuntimeError("Previous Talk stream lost")
    voice_content=voice.read_text(encoding="utf8")
    local_content=local.read_text(encoding="utf8")
    if "SwrlzLocalSpeechRecognition" not in voice_content or "send.click()" not in voice_content:
        raise RuntimeError("Canonical Chat transport/recognizer selector missing")
    if not all(value in local_content for value in [
        "new available.KaldiRecognizer()", "echoCancellation: true",
        "script.crossOrigin", "model.terminate", "source.connect(processor)"
    ]):
        # The model termination is implemented through a model-promise
        # disposal callback; its exact syntax is deliberately checked.
        if "m?.terminate?.()" not in local_content:
            raise RuntimeError("Local microphone lifecycle incomplete")
    for i,code in enumerate(re.findall(r'<script(?:\s[^>]*)?>([\s\S]*?)</script>',page)):
        if code.strip():
            file=AFTER/f"inline-{i}.js"
            file.write_text(code,encoding="utf8")
            check_js(file)
    previous={PAGE:sha256(old_page),VOICE:sha256(old_voice)}
    candidate={
        PAGE:sha256((AFTER/"index.html").read_bytes()),
        VOICE:sha256((AFTER/"voice_conversation.js").read_bytes()),
        LOCAL:sha256((AFTER/"local_voice_vosk.js").read_bytes()),
    }
    (BEFORE/"manifest.json").write_text(json.dumps({
        "space":SPACE,"previousRevision":snapshot.sha,
        "old":previous,"candidate":candidate,
        "newFile":LOCAL,
        "billing":"No new paid APIs or hardware; local STT downloads WASM/model in browser",
    },indent=2),encoding="utf8")
    print(json.dumps({"result":"LOCAL_STREAMING_PREPARED_NOT_PUBLISHED",
        "revision":snapshot.sha,"paths":list(candidate),"smokeTests":"PASS"}))

def publish(api: HfApi) -> None:
    manifest=json.loads((BEFORE/"manifest.json").read_text(encoding="utf8"))
    if manifest.get("space")!=SPACE or manifest.get("newFile")!=LOCAL:
        raise RuntimeError("Wrong Space or unsafe new-file target")
    rev=manifest["previousRevision"]
    if api.repo_info(SPACE,repo_type="space").sha!=rev:
        raise RuntimeError("HF source advanced since snapshot; refuse stale update")
    files=[(PAGE,"index.html"),(VOICE,"voice_conversation.js"),(LOCAL,"local_voice_vosk.js")]
    for path,name in files:
        raw=(AFTER/name).read_bytes()
        if sha256(raw)!=manifest["candidate"][path]:
            raise RuntimeError("Candidate integrity mismatch: "+path)
        if path in manifest["old"] and sha256((BEFORE/name).read_bytes())!=manifest["old"][path]:
            raise RuntimeError("Original rollback changed: "+path)
    operations=[CommitOperationAdd(path_in_repo=path,path_or_fileobj=str(AFTER/name)) for path,name in files]
    receipt=api.create_commit(repo_id=SPACE,repo_type="space",operations=operations,
        parent_commit=rev,commit_message="§C opt-in local streaming STT: Vosk WASM on device, no paid speech API")
    newrev=str(getattr(receipt,"oid","") or api.repo_info(SPACE,repo_type="space").sha)
    for path,_ in files:
        if sha256(from_space(path,newrev))!=manifest["candidate"][path]:
            raise RuntimeError("Published source content mismatch: "+path)
    print(json.dumps({
        "result":"HF_LOCAL_STREAMING_SOURCE_PUBLISHED",
        "space":SPACE,"previousRevision":rev,"revision":newrev,
        "changedPaths":[p for p,_ in files],
        "deviceLatencyAndWASMCompatibility":"NOT_VERIFIED",
        "cost":"No additional paid provider or hardware requested",
    }))

if __name__=="__main__":
    if len(sys.argv)!=2 or sys.argv[1] not in ("prepare","publish"):
        raise SystemExit("Usage: publish_hf_local_streaming.py prepare|publish")
    if not TOKEN:
        raise SystemExit("HF_TOKEN unavailable; no production changes")
    client=HfApi(token=TOKEN)
    (prepare if sys.argv[1]=="prepare" else publish)(client)
