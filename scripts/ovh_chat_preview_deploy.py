#!/usr/bin/env python3
"""Apply the first OVH chat-context migration to the existing private preview."""
import ast
import os
from pathlib import Path
import re
import subprocess
import tempfile
import time
import urllib.request
import json

SOURCE = Path("/srv/swrlz/source")
PREVIEW = Path("/srv/swrlz/staging/chat-ovh-preview")
TARGET = PREVIEW / "lfm2_700m_engine.py"
PYTHON = "/srv/swrlz/chat-venv/bin/python"
UNIT = "swrlz-chat-preview.service"

def replace_once(s, old, new):
    if s.count(old) != 1:
        raise RuntimeError("Unexpected source shape: " + old[:100])
    return s.replace(old, new, 1)

def patch(s):
    if "OVH_ADAPTIVE_CONTEXT_V1" not in s:
        raise RuntimeError("Expected deployed V1 context patch")
    if "OVH_ADAPTIVE_CONTEXT_V2" in s:
        return s
    start=s.index("    # OVH_ADAPTIVE_CONTEXT_V1")
    end=s.index("    started=time.perf_counter()",start)
    s=s[:start]+r'''
    # OVH_ADAPTIVE_CONTEXT_V1
    # OVH_ADAPTIVE_CONTEXT_V2: port guarded 9B social prefill policy.
    compact_allowed = (
        not file_dialogue and not concise_identity_turn and not identity_followup
        and not reference_structure and not music_policy
        and not any(programming.get(k) for k in (
            "codingTask","failureEvidence","canonicalCarry","artifactMutationRequested",
            "artifactContinuation","newProject","intentContract","needsFailureEvidence"))
        and not any(payload.get(k) for k in (
            "nativeEditorEvidence","onlineContext","githubSourceChangeTask",
            "projectThreadEvidence","archiveEvidence","widgetPresentation",
            "forgeContext","githubAction","githubStart","sourceChangeIdentity","pinnedContext"))
    )
    clean = " ".join(prompt.split())
    compact_math = compact_allowed and not history and bool(re.fullmatch(
        r"(?:(?:hey|hi)\s+§?wyrlz\s*[,!:]?\s*)?"
        r"(?:(?:what is|what's|calculate|compute|solve)\s+)?"
        r"[+-]?\d+(?:\.\d+)?"
        r"(?:\s*[-+*/×÷]\s*[+-]?\d+(?:\.\d+)?)+\s*[?=.]?",
        clean, re.I))
    compact_social = compact_allowed and len(clean)<=170 and bool(re.fullmatch(
        r"(?:"
        r"(?:hi|hello|hey|yo|howdy)(?:[,! ]+§?wyrlz)?(?:[,! ]+(?:how (?:are|r) you|how'?s it going|what'?s up))?"
        r"|how (?:are|r) you|how'?s it going|how have you been|what'?s up"
        r"|(?:pretty|really) (?:good|great|fine|okay)(?: actually| thanks| today)?"
        r"|(?:doing|i'?m doing) (?:good|great|fine|okay|alright)(?: thanks)?"
        r"|that took (?:a while|forever|so long)(?: for you to respond)?(?: lol| lmao)?"
        r"|(?:lol|lmao|lmfao|haha|hahaha|yep|yeah|exactly|nice|cool|awesome)"
        r")[!?. ,]*",clean,re.I))
    # Narrow standalone educational questions, no history or evidence discarded.
    compact_explain = compact_allowed and not history and len(clean)<=160 and bool(re.fullmatch(
        r"(?:what (?:is|are)|define|explain)\s+(?:the\s+)?(?:[A-Za-z][A-Za-z0-9 -]{0,65})"
        r"(?: in (?:one|two|three) sentences)?[?.]?",clean,re.I
    )) and not re.search(r"\b(?:today|current|latest|now|my|our|your|price|weather|news|version|time|date|code|function|script|file|project|repair|fix|write|generate|how|should|best)\b",clean,re.I)
    compact_kind = ("math" if compact_math else "social" if compact_social
                    else "explain" if compact_explain else "standard")
    if compact_kind != "standard":
        system = (
            "You are §wyrlz (Swurlz), an AI assistant distinct from the user. "
            "Answer the actual message directly, naturally and accurately. "
            "Use supplied history for continuity; never invent shared memories, "
            "facts, tool results or actions. Match humor when appropriate. "
            "Be concise for simple questions; honor explicit answer constraints. "
            "Acknowledge uncertainty when necessary."
        )
        if custom_assistant_profile:
            system += "\nUSER ASSISTANT PREFERENCES:\n" + custom_assistant_profile
        if user_profile:
            system += "\nCURRENT USER PROFILE (not assistant identity):\n" + user_profile
        if compact_social:
            system += "\nRespond conversationally using actual supplied context."
        elif compact_math:
            system += "\nCalculate accurately."
    yield {"type":"STATUS","phase":"OVH_PREFILL_PROFILE","reason":compact_kind}

''' + s[end:]
    s=replace_once(s,'        if compact_math:\n            response_tokens=min(128,available_output_tokens)\n            temperature=0.2\n',
        '        if compact_math or compact_social or compact_explain:\n'
        '            response_tokens=min(128 if compact_math else 256,available_output_tokens)\n'
        '            temperature=0.2 if compact_math else 0.4\n')
    s=replace_once(s,'    print(f"CONTEXT_RECEIPT compact_math={compact_math} input_tokens={input_tokens}", flush=True)',
        '    print(f"CONTEXT_RECEIPT profile={compact_kind} input_tokens={input_tokens}", flush=True)')
    return s

def write_atomic(path, data):
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as f:
        temp = Path(f.name)
        f.write(data)
    try:
        os.chmod(temp, path.stat().st_mode & 0o777)
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)

def health():
    with urllib.request.urlopen("http://127.0.0.1:16947/health", timeout=3) as r:
        assert json.load(r)["status"] == "ok"
    with urllib.request.urlopen("http://127.0.0.1:8766/api/hf/models", timeout=3) as r:
        models = json.load(r)["models"]
        assert any(m["available"] and m["model_id"] == "700m" for m in models)
    with urllib.request.urlopen("http://127.0.0.1:8766/", timeout=3) as r:
        assert r.status == 200

def restart():
    subprocess.run(["/usr/bin/sudo", "-n", "/usr/bin/systemctl", "restart", UNIT], check=True, timeout=45)
    for _ in range(20):
        try:
            health()
            return
        except Exception:
            time.sleep(1)
    raise RuntimeError("Preview health failed")


def probe(label,prompt,expected):
    import http.cookiejar
    import urllib.parse
    import uuid
    base="http://127.0.0.1:8766"
    opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    rid=str(uuid.uuid4())
    body={"modelId":"700m","prompt":prompt,"threadId":"ovh-perf-"+rid,
          "requestId":rid,"profileId":"LALM","profile":"","userProfile":"","timeZone":"UTC"}
    started=time.monotonic()
    req=urllib.request.Request(base+"/api/lalm_station/send",data=json.dumps(body).encode(),
                              headers={"Content-Type":"application/json"},method="POST")
    with opener.open(req,timeout=15) as r:
        if r.status!=202: raise RuntimeError("Probe not accepted")
        r.read()
    first=None; parts=[]; terminal=None; tokens=None; profile=None
    with opener.open(base+"/api/lalm_station/stream?"+urllib.parse.urlencode({"requestId":rid}),timeout=90) as r:
        for raw in r:
            if time.monotonic()-started>100: raise RuntimeError("Probe deadline")
            try: event=json.loads(raw)
            except ValueError: continue
            kind=event.get("type")
            if kind=="STATUS" and event.get("phase")=="OVH_PREFILL_PROFILE":
                profile=event.get("reason")
            if kind=="CONTEXT": tokens=event.get("estimatedInputTokens")
            if kind=="DELTA":
                piece=str(event.get("text") or "")
                if piece and first is None: first=round(time.monotonic()-started,2)
                parts.append(piece)
            if kind in ("COMPLETE","COMPLETED","FAILED","CANCELLED"):
                terminal=kind;break
    # Station stores CONTEXT in its session projection, not the NDJSON stream.
    with opener.open(base+"/api/lalm_station/sync",timeout=10) as r:
        active=json.load(r).get("activeGeneration") or {}
    if active.get("requestId")!=rid:
        raise RuntimeError("Probe session generation mismatch")
    tokens=(active.get("contextBudget") or {}).get("estimatedInputTokens",tokens)
    receipt={"case":label,"profile":profile,"inputTokens":tokens,"firstVisibleSec":first,
             "totalSec":round(time.monotonic()-started,2),"terminal":terminal,"outputChars":len("".join(parts))}
    print("SWRLZ_PERF_RECEIPT "+json.dumps(receipt,separators=(",",":")),file=__import__("sys").stderr,flush=True)
    if terminal not in ("COMPLETE","COMPLETED") or not parts or first is None:
        raise RuntimeError("End-to-end generation failed: "+label)
    if profile!=expected or not isinstance(tokens,int) or tokens>512:
        raise RuntimeError("Compact profile budget not verified: "+label)
    if label=="math" and not re.search(r"(?<!\d)4(?!\d)","".join(parts)):
        raise RuntimeError("Arithmetic acceptance failed")
    if first>45:
        raise RuntimeError("First token latency exceeded 45 seconds: "+label)

def main():
    if os.geteuid() == 0:
        raise RuntimeError("Run as deployment user, not root")
    rev = subprocess.check_output(["git", "-C", str(SOURCE), "rev-parse", "HEAD"], text=True).strip()
    original = TARGET.read_bytes()
    s = original.decode("utf-8")
    updated = patch(s)
    ast.parse(updated)
    if updated != s:
        backup = TARGET.with_name(TARGET.name + ".ovh-" + rev[:12] + ".bak")
        if not backup.exists():
            with backup.open("xb") as f:
                f.write(original)
        write_atomic(TARGET, updated.encode("utf-8"))
    try:
        subprocess.run([PYTHON, "-c", "from ovh_chat import app"], cwd=PREVIEW, check=True, timeout=45)
        restart()
        probe('math','Hey §wyrlz, what is 2 + 2?','math')
        probe('social','Hello §wyrlz!','social')
        probe('explain','What is RAM?','explain')
    except Exception:
        if updated != s:
            write_atomic(TARGET, original)
            restart()
        raise
    print("SWRLZ_CHAT_PREVIEW_DEPLOY_OK")
    print(rev)

if __name__ == "__main__":
    main()
