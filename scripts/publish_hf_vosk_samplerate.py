"""HF Chat Vosk sample-rate repair: patch only current live Chat HTML and local ASR.

The recognizer constructor on vosk-browser 0.0.5 requires the actual
AudioContext.sampleRate. The previous no-argument constructor silently
left the decoder unready while microphone VAD continued receiving audio.
Keep browser Talk, model cache, endpoints, and every other Station file intact.
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
FILES = {PAGE: "index.html", LOCAL: "local_voice_vosk.js"}
BEFORE = Path("hf-vosk-samplerate-rollback")
AFTER = Path("hf-vosk-samplerate-candidate")
SOURCE = Path("voice-streaming-source")
TOKEN = os.environ.get("HF_TOKEN") or ""

OLD_INITIALIZATION = '''        context = new AudioContextClass();
        if (typeof context.createScriptProcessor !== "function")
          throw new Error("Streaming audio processor unavailable");
        recognizer = new available.KaldiRecognizer();
        recognizer.setWords?.(false);'''

NEW_INITIALIZATION = '''        context = new AudioContextClass();
        if (typeof context.createScriptProcessor !== "function")
          throw new Error("Streaming audio processor unavailable");
        // Vosk-browser 0.0.5 MUST receive the actual Web Audio sample rate.
        // Android can use 48 kHz even if getUserMedia requested 16 kHz.
        // Omitting this argument leaves the WASM recognizer uninitialized:
        // mic RMS still works, but the worker never produces words.
        const sampleRate = Number(context.sampleRate);
        if (!Number.isFinite(sampleRate) || sampleRate < 8000 || sampleRate > 192000)
          throw new Error("Browser did not provide a valid microphone sample rate");
        recognizer = new available.KaldiRecognizer(sampleRate);
        recognizer.setWords?.(false);'''

OLD_STATUS = 'onStatus?.("Local model ready · checking microphone audio…");'
NEW_STATUS = 'onStatus?.("Vosk " + sampleRate + " Hz · checking microphone audio…");'

def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def live(path: str, revision: str) -> bytes:
    return Path(hf_hub_download(SPACE, path, repo_type="space",
                                revision=revision, token=TOKEN)).read_bytes()

def replace_once(contents: str, old: str, new: str, marker: str) -> str:
    found = contents.count(old)
    if found != 1 or new in contents:
        raise RuntimeError(f"Vosk sample-rate live source drift: {marker}, count={found}")
    return contents.replace(old, new, 1)

def node_check(path: Path) -> None:
    subprocess.run(["node", "--check", str(path)], check=True)

def prepare(api: HfApi) -> None:
    revision=api.repo_info(SPACE, repo_type="space").sha
    files=set(api.list_repo_files(SPACE, repo_type="space", revision=revision))
    if not set(FILES).issubset(files):
        raise RuntimeError("Live Chat page or local Vosk source missing")
    original={path:live(path, revision) for path in FILES}
    if not 10000 < len(original[PAGE]) < 2_000_000:
        raise RuntimeError("Unexpected live Chat HTML length")
    if not 5000 < len(original[LOCAL]) < 100000:
        raise RuntimeError("Unexpected live Vosk JS length")
    html=original[PAGE].decode("utf-8")
    local=original[LOCAL].decode("utf-8")
    if any(s not in local for s in ("window.caches.open(MODEL_CACHE)",
                                    "finishUtterance", "Local microphone audio received")):
        raise RuntimeError("Existing Vosk cache/microphone pipeline missing")
    if any(s not in html for s in ('id="voiceProviderSelect"',
                                   'swrlz-voice-delta', "local_voice_vosk.js?v=")):
        raise RuntimeError("Existing live browser/local Talk UI missing")
    revised_local=replace_once(local, OLD_INITIALIZATION, NEW_INITIALIZATION,
                               "Kaldi recognizer constructor")
    revised_local=replace_once(revised_local, OLD_STATUS, NEW_STATUS,
                               "local microphone status")

    # Only the reviewed, tested two-hunk JS change is authorized.
    expected=(SOURCE/LOCAL).read_text(encoding="utf-8")
    if expected != revised_local:
        raise RuntimeError("Production Vosk JS differs from reviewed candidate; refuse overwrite")
    version=re.search(r'<meta name="swrlz-chat-version" content="(1)\.(1)\.(\d+)">',html)
    if not version or int(version.group(3)) < 32:
        raise RuntimeError("Live Chat voice asset version unsupported")
    old_version=version.group(0)
    next_version=f"1.1.{int(version.group(3))+1}"
    revised_html=replace_once(html,old_version,
        f'<meta name="swrlz-chat-version" content="{next_version}">',"HTML version")
    revised_html=replace_once(revised_html,
        f'const SWRLZ_CHAT_VERSION = "{version.group(1)}.{version.group(2)}.{version.group(3)}";',
        f'const SWRLZ_CHAT_VERSION = "{next_version}";',"JavaScript version")
    match=re.search(r'<script src="(/chat/§wyrlz/assets/local_voice_vosk\.js\?v=[^"]+)" defer></script>',revised_html)
    if not match:
        raise RuntimeError("Local voice script src missing or incompatible")
    revised_html=replace_once(revised_html,match.group(1),
        f"/chat/§wyrlz/assets/local_voice_vosk.js?v={next_version}",
        "Local Vosk asset cache-bust")
    if revised_html.count('id="voiceProviderSelect"') != 1 or revised_html.count("swrlz-voice-delta") != 1:
        raise RuntimeError("Chat integration damaged")

    BEFORE.mkdir(exist_ok=False)
    AFTER.mkdir(exist_ok=False)
    for path,name in FILES.items():
        (BEFORE/name).write_bytes(original[path])
    (AFTER/"index.html").write_text(revised_html, encoding="utf-8")
    (AFTER/"local_voice_vosk.js").write_text(revised_local, encoding="utf-8")

    # Test real repo fixture with 16 kHz and 48 kHz simulated devices.
    tests=["test_chat_streaming_voice.cjs",
           "test_chat_local_streaming_vosk.cjs",
           "test_chat_local_vosk_recovery.cjs"]
    for name in tests:
        file=SOURCE/"scripts"/name
        node_check(file)
        subprocess.run(["node",str(file)],check=True)
    node_check(SOURCE/LOCAL)
    node_check(AFTER/"local_voice_vosk.js")
    for i,code in enumerate(re.findall(r'<script(?:\s[^>]*)?>([\s\S]*?)</script>',revised_html)):
        if code.strip():
            script=AFTER/f"inline-{i}.js"
            script.write_text(code,encoding="utf8")
            node_check(script)

    manifest={"space":SPACE,"oldRevision":revision,
              "before":{path:digest(blob) for path,blob in original.items()},
              "after":{path:digest((AFTER/name).read_bytes()) for path,name in FILES.items()},
              "targetVersion":next_version,"billingChange":"none",
              "scope":list(FILES)}
    (BEFORE/"manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    print(json.dumps({"result":"VOSK_SAMPLERATE_PREPARED_NOT_PUBLISHED",
                      "revision":revision,"targetVersion":next_version,"paths":list(FILES)}))

def publish(api: HfApi) -> None:
    manifest=json.loads((BEFORE/"manifest.json").read_text(encoding="utf-8"))
    if manifest.get("space") != SPACE or set(manifest["scope"]) != set(FILES):
        raise RuntimeError("Incorrect publication target or scope")
    rev=manifest["oldRevision"]
    if api.repo_info(SPACE,repo_type="space").sha != rev:
        raise RuntimeError("HF Space changed after snapshot; refusing stale deployment")
    for path,name in FILES.items():
        if digest((BEFORE/name).read_bytes()) != manifest["before"][path]:
            raise RuntimeError("Vosk rollback integrity changed: "+path)
        if digest((AFTER/name).read_bytes()) != manifest["after"][path]:
            raise RuntimeError("Vosk release integrity changed: "+path)
    receipt=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=rev,
        operations=[CommitOperationAdd(path_in_repo=path,path_or_fileobj=str(AFTER/name)) for path,name in FILES.items()],
        commit_message="Fix local Vosk recognizer sample rate from actual Android AudioContext")
    newrev=str(getattr(receipt,"oid","") or api.repo_info(SPACE,repo_type="space").sha)
    for path in FILES:
        if digest(live(path,newrev)) != manifest["after"][path]:
            raise RuntimeError("Published Vosk source mismatch: "+path)
    print(json.dumps({"result":"HF_VOSK_SAMPLERATE_SOURCE_PUBLISHED",
                      "space":SPACE,"revision":newrev,"version":manifest["targetVersion"],
                      "changedPaths":list(FILES),"deviceAcceptance":"NOT_VERIFIED",
                      "billingChange":"none"}))

if __name__ == "__main__":
    if len(sys.argv)!=2 or sys.argv[1] not in ("prepare","publish"):
        raise SystemExit("Usage: publish_hf_vosk_samplerate.py prepare|publish")
    if not TOKEN:
        raise SystemExit("HF_TOKEN missing; no Space changes made")
    client=HfApi(token=TOKEN)
    (prepare if sys.argv[1]=="prepare" else publish)(client)
