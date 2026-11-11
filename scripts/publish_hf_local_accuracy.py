"""Guarded release: improve Local and Turbo transcription accuracy on HF Chat.

Patch only the reviewed local Vosk asset and live HTML version/cache-bust,
preserving Browser Talk, existing model routing, and all unrelated Chat code.
Snapshot before publish. Reject any drift; no new paid service or hardware.
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
BEFORE = Path("hf-voice-accuracy-rollback")
AFTER = Path("hf-voice-accuracy-candidate")
SOURCE = Path("voice-turbo-source")
TOKEN = os.environ.get("HF_TOKEN") or ""
# Exact reviewed on-device Vosk v5 source from deployed §C 1.1.36:
OLD_LOCAL_BLOB = "632bdb17671a5e550f94fd0c471e659e70a9f08e"

def digest(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def git_blob(b: bytes) -> str:
    return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()

def live_bytes(path: str, revision: str) -> bytes:
    return Path(hf_hub_download(SPACE,path,repo_type="space",revision=revision,token=TOKEN)).read_bytes()

def once(text: str, old: str, new: str, label: str) -> str:
    if text.count(old) != 1 or new in text:
        raise RuntimeError("Live Local ASR source drift: "+label)
    return text.replace(old,new,1)

def test_js(path: Path) -> None:
    subprocess.run(["node","--check",str(path)],check=True)

def prepare(api: HfApi) -> None:
    rev=api.repo_info(SPACE,repo_type="space").sha
    files=set(api.list_repo_files(SPACE,repo_type="space",revision=rev))
    if not {PAGE, LOCAL}.issubset(files):
        raise RuntimeError("Live Chat/Local recognizer missing")
    old_page=live_bytes(PAGE,rev)
    old_local=live_bytes(LOCAL,rev)
    html=old_page.decode("utf-8")
    if not 10000<len(old_page)<2_000_000 or not 10000<len(old_local)<100000:
        raise RuntimeError("Unexpected live source size")
    if git_blob(old_local)!=OLD_LOCAL_BLOB:
        raise RuntimeError("Live Vosk does not match the approved §C 1.1.36 baseline")
    if 'swrlz-voice-delta' not in html or html.count('value="turbo"')!=1:
        raise RuntimeError("Live Talk or Local Turbo selector missing")
    version=re.search(r'<meta name="swrlz-chat-version" content="1\.1\.(\d+)">',html)
    if not version or version.group(1)!="36":
        raise RuntimeError("Live Chat must be v1.1.36; preserve newer updates")
    revised=once(html,version.group(0),
        '<meta name="swrlz-chat-version" content="1.1.37">',"meta")
    revised=once(revised,'const SWRLZ_CHAT_VERSION = "1.1.36";',
        'const SWRLZ_CHAT_VERSION = "1.1.37";',"js version")
    revised=once(revised,
        '/chat/§wyrlz/assets/local_voice_vosk.js?v=1.1.36',
        '/chat/§wyrlz/assets/local_voice_vosk.js?v=1.1.37',"asset cache bust")
    if revised.count('id="voiceConversationButton"')!=1 or revised.count('value="turbo"')!=1:
        raise RuntimeError("Chat UI controls changed unexpectedly")

    new_local=(SOURCE/LOCAL).read_bytes()
    local_text=new_local.decode("utf-8")
    required=("committedSegments", "fullTranscript()", "TURBO_QUIET_FINAL_MS = 1900",
              "QUIET_FINAL_MS = 2300", "new available.KaldiRecognizer(sampleRate)",
              "autoGainControl: true", 'window.caches.open(MODEL_CACHE)',
              "recognizer.retrieveFinalResult()", "finalResultAvailable",
              'if (quiet && !finalRequested', 'Final transcription unavailable')
    if local_text.count("finishUtterance(transcription || latestPartial)") or (
            "rms >= (turbo ? 0.006 : 0.008)" not in local_text):
        raise RuntimeError("Old premature-submit path detected or quiet-input guard missing")
    if not all(marker in local_text for marker in required):
        raise RuntimeError("Reviewed Turbo accuracy guards incomplete")

    tests=("test_chat_streaming_voice.cjs","test_chat_local_streaming_vosk.cjs",
           "test_chat_local_vosk_recovery.cjs","test_chat_local_turbo.cjs",
           "test_chat_local_voice_accuracy_v6.cjs")
    for test in tests:
        path=SOURCE/"scripts"/test
        test_js(path)
        subprocess.run(["node",str(path)],check=True)
    test_js(SOURCE/LOCAL)
    for index,body in enumerate(re.findall(r'<script(?:\s[^>]*)?>([\s\S]*?)</script>',revised)):
        if body.strip():
            path=Path(f"voice-accuracy-inline-{index}.js")
            try:
                path.write_text(body,encoding="utf-8")
                test_js(path)
            finally:
                path.unlink(missing_ok=True)
    BEFORE.mkdir(exist_ok=False)
    AFTER.mkdir(exist_ok=False)
    (BEFORE/"index.html").write_bytes(old_page)
    (BEFORE/"local_voice_vosk.js").write_bytes(old_local)
    (AFTER/"index.html").write_text(revised,encoding="utf-8")
    (AFTER/"local_voice_vosk.js").write_bytes(new_local)
    files_before={PAGE:digest(old_page),LOCAL:digest(old_local)}
    files_after={
        PAGE:digest((AFTER/"index.html").read_bytes()),
        LOCAL:digest(new_local)
    }
    manifest={"space":SPACE,"previousRevision":rev,"version":"1.1.37",
              "before":files_before,"after":files_after,
              "changedPaths":[PAGE,LOCAL],"billingChange":"none"}
    (BEFORE/"manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf8")
    print(json.dumps({"status":"VOICE_ACCURACY_PREPARED_NOT_PUBLISHED",
                      "fromRevision":rev,"paths":list(files_after),"tests":"PASS"}))

def publish(api: HfApi) -> None:
    manifest=json.loads((BEFORE/"manifest.json").read_text(encoding="utf8"))
    rev=manifest["previousRevision"]
    if manifest.get("space")!=SPACE or manifest["changedPaths"]!=[PAGE,LOCAL]:
        raise RuntimeError("Unexpected deployment scope")
    if api.repo_info(SPACE,repo_type="space").sha!=rev:
        raise RuntimeError("HF Space advanced after snapshot; refuse stale publish")
    files={PAGE:"index.html",LOCAL:"local_voice_vosk.js"}
    for path,filename in files.items():
        if digest((BEFORE/filename).read_bytes())!=manifest["before"][path]:
            raise RuntimeError("Rollback snapshot corrupted "+path)
        if digest((AFTER/filename).read_bytes())!=manifest["after"][path]:
            raise RuntimeError("Candidate corrupted "+path)
    receipt=api.create_commit(
        repo_id=SPACE,repo_type="space",parent_commit=rev,
        operations=[CommitOperationAdd(path_in_repo=path,path_or_fileobj=str(AFTER/filename))
                    for path,filename in files.items()],
        commit_message="§C Local voice accuracy: preserve all phrases and finalize buffered speech")
    sha=str(getattr(receipt,"oid","") or api.repo_info(SPACE,repo_type="space").sha)
    for path in files:
        if digest(live_bytes(path,sha))!=manifest["after"][path]:
            raise RuntimeError("Published local Turbo file checksum mismatch "+path)
    print(json.dumps({"status":"HF_VOICE_ACCURACY_SOURCE_PUBLISHED","space":SPACE,
                      "revision":sha,"version":"1.1.37",
                      "paths":list(files),"billingChange":"none",
                      "deviceAcceptance":"NOT_VERIFIED"}))

if __name__=="__main__":
    if len(sys.argv)!=2 or sys.argv[1] not in ("prepare","publish"):
        raise SystemExit("Usage: publish_hf_local_accuracy.py prepare|publish")
    if not TOKEN:
        raise SystemExit("HF_TOKEN missing; Space unchanged")
    api=HfApi(token=TOKEN)
    (prepare if sys.argv[1]=="prepare" else publish)(api)
