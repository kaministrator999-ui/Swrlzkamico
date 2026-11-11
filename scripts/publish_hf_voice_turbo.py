"""Guarded §C Local Turbo speed trial; existing HF Space, no paid hardware.

Atomic scoped patch of current live Chat HTML, its two voice scripts, and
the 700M CPU thread plan. Never replace live HTML with older GitHub HTML.
Prepare authentic production snapshots before any publication. Fail on drift.
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
ENGINE = "lfm2_700m_engine.py"
FILE_NAMES = {PAGE:"index.html", VOICE:"voice_conversation.js",
              LOCAL:"local_voice_vosk.js", ENGINE:"lfm2_700m_engine.py"}
# Reviewed deployed baselines at §C v1.1.33, exact Git blob hashes.
OLD_VOICE_BLOB = "2cfad1a8b9ab4bc91b65457547b16d49ce400dc8"
OLD_LOCAL_BLOB = "523e5b2b620d918d54e71d65cff7f55d81d446d2"
BEFORE = Path("hf-voice-turbo-rollback")
AFTER = Path("hf-voice-turbo-candidate")
SOURCE = Path("voice-turbo-source")
TOKEN = os.environ.get("HF_TOKEN") or ""

def digest(data:bytes)->str:
    return hashlib.sha256(data).hexdigest()

def git_blob(data:bytes)->str:
    return hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()

def from_space(path:str,revision:str)->bytes:
    return Path(hf_hub_download(SPACE,path,repo_type="space",
                                revision=revision,token=TOKEN)).read_bytes()

def only(s:str,old:str,new:str,tag:str)->str:
    count=s.count(old)
    if count!=1 or new in s:
        raise RuntimeError("TURBO_SOURCE_DRIFT "+tag+" count="+str(count))
    return s.replace(old,new,1)

def check_js(path:Path)->None:
    subprocess.run(["node","--check",str(path)],check=True)

def prepare(api:HfApi)->None:
    rev=api.repo_info(SPACE,repo_type="space").sha
    available=set(api.list_repo_files(SPACE,repo_type="space",revision=rev))
    if not set(FILE_NAMES).issubset(available):
        raise RuntimeError("Production Chat/engine baseline missing")
    live={path:from_space(path,rev) for path in FILE_NAMES}
    page=live[PAGE].decode("utf8")
    engine=live[ENGINE].decode("utf8")

    # Strict source identity: never remove unreviewed changes to the voice JS.
    if git_blob(live[VOICE]) != OLD_VOICE_BLOB or git_blob(live[LOCAL]) != OLD_LOCAL_BLOB:
        raise RuntimeError("Voice scripts changed since reviewed §C 1.1.33; refuse overwrite")
    version=re.search(r'<meta name="swrlz-chat-version" content="1\.1\.(\d+)">',page)
    if not version or version.group(1)!="33":
        raise RuntimeError("Expected live Chat v1.1.33; preserve newer changes")
    if 'swrlz-voice-delta' not in page or page.count('id="voiceProviderSelect"')!=1:
        raise RuntimeError("Canonical Chat streaming Talk integration missing")
    if '<option value="turbo">' in page:
        raise RuntimeError("Local Turbo already installed")
    if 'quota=cpu.get("limitCores")' not in engine:
        raise RuntimeError("CPU quota guard missing; refuse max-thread trial")

    html=only(page,'<meta name="swrlz-chat-version" content="1.1.33">',
              '<meta name="swrlz-chat-version" content="1.1.34">',"version-meta")
    html=only(html,'const SWRLZ_CHAT_VERSION = "1.1.33";',
              'const SWRLZ_CHAT_VERSION = "1.1.34";',"version-js")
    html=only(html,'            <option value="local">Local stream · 41 MB</option>',
              '            <option value="local">Local stream · 41 MB</option>\n'
              '            <option value="turbo">Local Turbo · 41 MB</option>',"selector")
    for name in ("local_voice_vosk.js","voice_conversation.js"):
        pattern=re.compile(r'(/chat/§wyrlz/assets/'+re.escape(name)+r')\?v=1\.1\.\d+')
        if len(pattern.findall(html))!=1:
            raise RuntimeError("Turbo voice script reference drift: "+name)
        html=pattern.sub(lambda m:m.group(1)+"?v=1.1.34",html,count=1)
    if html.count('value="turbo"')!=1 or html.count('id="voiceConversationButton"')!=1:
        raise RuntimeError("Turbo UI source invalid")

    engine_new=only(engine,"return min(14,capacity),capacity",
                    "return min(16,capacity),capacity","700m-decode-threads")
    # Existing quota ceiling stays intact: no overcommit, model/weights unchanged.
    assert 'quota=cpu.get("limitCores")' in engine_new
    assert "n_batch=512,n_ubatch=512,n_gpu_layers=0" in engine_new

    candidate={
        PAGE:html.encode("utf8"),
        VOICE:(SOURCE/VOICE).read_bytes(),
        LOCAL:(SOURCE/LOCAL).read_bytes(),
        ENGINE:engine_new.encode("utf8"),
    }
    voice=candidate[VOICE].decode("utf8")
    local=candidate[LOCAL].decode("utf8")
    if not all(s in voice for s in ('voiceProvider?.value === "local" || turboSelected()',
                                     "instance.turbo = true", "first-text-delta",
                                     "earlyPhraseLimit")):
        raise RuntimeError("Expected Turbo Talk integration missing")
    if not all(s in local for s in ('TURBO_QUIET_FINAL_MS = 650',
                                     'TURBO_STALE_PARTIAL_MS = 1100',
                                     "context.sampleRate", "sampleRate: 16000",
                                     "turbo ? 1024 : 4096")):
        raise RuntimeError("Expected Turbo Vosk audio mode missing")

    tests=[
        "test_chat_streaming_voice.cjs",
        "test_chat_local_streaming_vosk.cjs",
        "test_chat_local_vosk_recovery.cjs",
        "test_chat_local_turbo.cjs",
    ]
    for name in tests:
        script=SOURCE/"scripts"/name
        check_js(script)
        subprocess.run(["node",str(script)],check=True)
    for path in (VOICE,LOCAL):
        check_js(SOURCE/path)
    for i,body in enumerate(re.findall(r'<script(?:\s[^>]*)?>([\s\S]*?)</script>',html)):
        if body.strip():
            script=Path(f"turbo-inline-{i}.js")
            try:
                script.write_text(body,encoding="utf8")
                check_js(script)
            finally:
                script.unlink(missing_ok=True)

    BEFORE.mkdir(exist_ok=False)
    AFTER.mkdir(exist_ok=False)
    for path,name in FILE_NAMES.items():
        (BEFORE/name).write_bytes(live[path])
        (AFTER/name).write_bytes(candidate[path])
    meta={
        "space":SPACE, "sourceRevision":rev, "scope":list(FILE_NAMES),
        "old":{path:digest(data) for path,data in live.items()},
        "new":{path:digest(data) for path,data in candidate.items()},
        "version":"1.1.34",
        "cpuExperiment":"14/16 -> quota-bound 16/16",
        "localTurbo":"16kHz preferred, 1024-frame audio, 650ms quiet threshold",
        "billingChange":"none"
    }
    (BEFORE/"manifest.json").write_text(json.dumps(meta,indent=2),encoding="utf8")
    print(json.dumps({"result":"TURBO_PREPARED_NOT_PUBLISHED",
                      "revision":rev,"files":list(FILE_NAMES),"tests":"PASS"}))

def publish(api:HfApi)->None:
    meta=json.loads((BEFORE/"manifest.json").read_text(encoding="utf8"))
    if meta.get("space")!=SPACE or set(meta["scope"])!=set(FILE_NAMES):
        raise RuntimeError("Wrong target or files")
    rev=meta["sourceRevision"]
    if api.repo_info(SPACE,repo_type="space").sha!=rev:
        raise RuntimeError("HF Space advanced since snapshot: refuse stale Turbo patch")
    for path,name in FILE_NAMES.items():
        if digest((BEFORE/name).read_bytes())!=meta["old"][path]:
            raise RuntimeError("Rollback snapshot corrupted: "+path)
        if digest((AFTER/name).read_bytes())!=meta["new"][path]:
            raise RuntimeError("Turbo candidate corrupted: "+path)
    operations=[
        CommitOperationAdd(path_in_repo=path,path_or_fileobj=str(AFTER/name))
        for path,name in FILE_NAMES.items()
    ]
    receipt=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=rev,
        operations=operations,
        commit_message="§C Local Turbo 16kHz + full quota-bound 16-thread 700M CPU trial")
    sha=str(getattr(receipt,"oid","") or api.repo_info(SPACE,repo_type="space").sha)
    for path in FILE_NAMES:
        if digest(from_space(path,sha))!=meta["new"][path]:
            raise RuntimeError("Published Turbo source mismatch: "+path)
    print(json.dumps({"result":"HF_TURBO_SOURCE_PUBLISHED",
                      "space":SPACE,"revision":sha,"version":meta["version"],
                      "changedPaths":list(FILE_NAMES),"billingChange":"none",
                      "deviceBenchmark":"NOT_VERIFIED"}))

if __name__=="__main__":
    if len(sys.argv)!=2 or sys.argv[1] not in ("prepare","publish"):
        raise SystemExit("Usage: publish_hf_voice_turbo.py prepare|publish")
    if not TOKEN:
        raise SystemExit("Missing HF_TOKEN; no Space change")
    api=HfApi(token=TOKEN)
    (prepare if sys.argv[1]=="prepare" else publish)(api)
