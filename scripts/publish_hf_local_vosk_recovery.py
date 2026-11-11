"""Fix local Vosk Talk mic and repeated model downloads without paid services.

Two-phase HF Space release. First snapshot current 1.1.31+ Chat page and
local voice scripts; validate the exact additive patch and regression tests.
Publish only after rollback artifact is safely uploaded. Refuse drift.
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

SPACE="kamiloki/Swyrlz"
PAGE="chat/§wyrlz/index.html"
VOICE="chat/§wyrlz/assets/voice_conversation.js"
LOCAL="chat/§wyrlz/assets/local_voice_vosk.js"
FILES={PAGE:"index.html",VOICE:"voice_conversation.js",LOCAL:"local_voice_vosk.js"}
BEFORE=Path("hf-local-vosk-recovery-rollback")
AFTER=Path("hf-local-vosk-recovery-candidate")
SOURCE=Path("voice-streaming-source")
TOKEN=os.environ.get("HF_TOKEN") or ""

def digest(blob:bytes)->str:
    return hashlib.sha256(blob).hexdigest()

def live_blob(path:str,revision:str)->bytes:
    return Path(hf_hub_download(SPACE,path,repo_type="space",revision=revision,token=TOKEN)).read_bytes()

def check_js(path:Path)->None:
    subprocess.run(["node","--check",str(path)],check=True)

def prepare(api:HfApi)->None:
    revision=api.repo_info(SPACE,repo_type="space").sha
    paths=set(api.list_repo_files(SPACE,repo_type="space",revision=revision))
    if not set(FILES).issubset(paths):
        raise RuntimeError("Current live Talk files missing; refuse deployment")
    originals={path:live_blob(path,revision) for path in FILES}
    if not (10_000<len(originals[PAGE])<2_000_000
            and 8_000<len(originals[VOICE])<100_000
            and 5_000<len(originals[LOCAL])<100_000):
        raise RuntimeError("Live Chat source changed beyond expected size")
    page=originals[PAGE].decode("utf8")
    voice=originals[VOICE].decode("utf8")
    local=originals[LOCAL].decode("utf8")
    if ('id="voiceProviderSelect"' not in page or
            'swrlz-voice-delta' not in page or
            "SwrlzLocalSpeechRecognition" not in voice or
            "window.SwrlzLocalVoice?.dispose()" not in voice or
            "new available.KaldiRecognizer()" not in local):
        raise RuntimeError("Live opt-in Local stream v1 baseline not found")

    BEFORE.mkdir(exist_ok=False)
    AFTER.mkdir(exist_ok=False)
    for path,name in FILES.items():
        (BEFORE/name).write_bytes(originals[path])

    patch=SOURCE/"scripts/patch_hf_local_vosk_recovery.cjs"
    for code in [patch,SOURCE/VOICE,SOURCE/LOCAL]:
        check_js(code)
    tests=[
        SOURCE/"scripts/test_chat_streaming_voice.cjs",
        SOURCE/"scripts/test_chat_local_streaming_vosk.cjs",
        SOURCE/"scripts/test_chat_local_vosk_recovery.cjs",
    ]
    for test in tests:
        check_js(test)
        subprocess.run(["node",str(test)],check=True)

    subprocess.run(["node",str(patch),str(BEFORE/"index.html"),
                    str(AFTER/"index.html")],check=True)
    (AFTER/"voice_conversation.js").write_bytes((SOURCE/VOICE).read_bytes())
    (AFTER/"local_voice_vosk.js").write_bytes((SOURCE/LOCAL).read_bytes())
    patched=(AFTER/"index.html").read_text(encoding="utf8")
    if patched.count('id="voiceProviderSelect"')!=1 or patched.count("swrlz-voice-delta")!=1:
        raise RuntimeError("Chat UI or stream bridge lost in patch")
    if patched.count("local_voice_vosk.js?v=")!=1 or patched.count("voice_conversation.js?v=")!=1:
        raise RuntimeError("Voice asset cache-bust missing or duplicated")
    local_new=(AFTER/"local_voice_vosk.js").read_text(encoding="utf8")
    voice_new=(AFTER/"voice_conversation.js").read_text(encoding="utf8")
    if not all(marker in local_new for marker in [
        "window.caches.open(MODEL_CACHE)", "QUIET_FINAL_MS",
        "latestPartial", "finishUtterance", "audio reached",
        "Microphone audio received", "watchdog"
    ]):
        # Only exact reviewed code is accepted. In particular, a fresh model
        # download on each activation and a partial-only infinite listen fail.
        raise RuntimeError("Vosk recovery invariants missing")
    if "window.SwrlzLocalVoice?.stop()" not in voice_new or "send.click()" not in voice_new:
        raise RuntimeError("Talk session reuse or canonical send lost")
    for i,source in enumerate(re.findall(r'<script(?:\s[^>]*)?>([\s\S]*?)</script>',patched)):
        if source.strip():
            file=AFTER/f"inline-{i}.js"
            file.write_text(source,encoding="utf8")
            check_js(file)

    manifest={
        "space":SPACE,"beforeRevision":revision,
        "before":{path:digest(blob) for path,blob in originals.items()},
        "after":{path:digest((AFTER/name).read_bytes()) for path,name in FILES.items()},
        "scope":list(FILES),
        "billingChange":"none",
        "rollback":"Original three source files saved as GitHub Actions artifact",
    }
    (BEFORE/"manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf8")
    print(json.dumps({"result":"VOSK_RECOVERY_PREPARED_NOT_PUBLISHED",
                      "revision":revision,"changedPaths":list(FILES),
                      "tests":len(tests),"billingChange":"none"}))

def publish(api:HfApi)->None:
    manifest=json.loads((BEFORE/"manifest.json").read_text(encoding="utf8"))
    revision=manifest["beforeRevision"]
    if manifest["space"]!=SPACE or set(manifest["scope"])!=set(FILES):
        raise RuntimeError("Incorrect Space or release file scope")
    if api.repo_info(SPACE,repo_type="space").sha!=revision:
        raise RuntimeError("HF Space advanced since snapshot; refuse stale publication")
    for path,name in FILES.items():
        if digest((BEFORE/name).read_bytes())!=manifest["before"][path]:
            raise RuntimeError("Rollback integrity failure: "+path)
        if digest((AFTER/name).read_bytes())!=manifest["after"][path]:
            raise RuntimeError("Candidate integrity failure: "+path)
    result=api.create_commit(
        repo_id=SPACE,repo_type="space",parent_commit=revision,
        operations=[CommitOperationAdd(path_in_repo=path,
                    path_or_fileobj=str(AFTER/name)) for path,name in FILES.items()],
        commit_message="Fix §C local Vosk: cached archive, reusable worker, partial-silence endpoint",
    )
    newrev=str(getattr(result,"oid","") or api.repo_info(SPACE,repo_type="space").sha)
    for path in FILES:
        if digest(live_blob(path,newrev))!=manifest["after"][path]:
            raise RuntimeError("HF published source does not match candidate: "+path)
    print(json.dumps({
        "result":"HF_VOSK_RECOVERY_SOURCE_PUBLISHED","target":SPACE,
        "beforeRevision":revision,"publishedRevision":newrev,
        "changedPaths":list(FILES),"billingChange":"none",
        "deviceMicrophoneAcceptance":"NOT_VERIFIED",
    }))

if __name__=="__main__":
    if len(sys.argv)!=2 or sys.argv[1] not in ("prepare","publish"):
        raise SystemExit("Usage: publish_hf_local_vosk_recovery.py prepare|publish")
    if not TOKEN:
        raise SystemExit("HF_TOKEN not configured; production untouched")
    client=HfApi(token=TOKEN)
    if sys.argv[1]=="prepare":
        prepare(client)
    else:
        publish(client)
