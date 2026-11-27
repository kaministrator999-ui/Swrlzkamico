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
    if "OVH_ADAPTIVE_CONTEXT_V1" in s:
        # The previously supplied terminal patch may already be installed.
        if "if compact_math:" not in s or "CONTEXT_RECEIPT compact_math=" not in s:
            raise RuntimeError("Incomplete previous context patch")
        return s
    anchor = "    started=time.perf_counter()\n    yield"
    addition = r'''
    # OVH_ADAPTIVE_CONTEXT_V1
    compact_math = (
        not programming.get("codingTask")
        and not programming.get("failureEvidence")
        and not programming.get("canonicalCarry")
        and not file_dialogue
        and bool(re.fullmatch(
            r"(?:(?:hey|hi)\s+§?wyrlz\s*[,!:]?\s*)?"
            r"(?:(?:what is|what's|calculate|compute|solve)\s+)?"
            r"[+-]?\d+(?:\.\d+)?"
            r"(?:\s*[-+*/×÷]\s*[+-]?\d+(?:\.\d+)?)+"
            r"\s*[?=.]?", prompt.strip(), re.I
        ))
    )
    if compact_math:
        system = (
            "You are §wyrlz. Answer the self-contained arithmetic "
            "question accurately and concisely."
        )
        model_history = []

'''
    s = replace_once(s, anchor, addition + anchor)
    anchor = '        mode=_response_mode(prompt,programming,history)\n        if file_dialogue:'
    s = replace_once(s, anchor,
        '        mode=_response_mode(prompt,programming,history)\n'
        '        if compact_math:\n'
        '            response_tokens=min(128,available_output_tokens)\n'
        '            temperature=0.2\n'
        '        elif file_dialogue:')
    anchor = "    history_tokens=max(0,input_tokens-system_tokens-prompt_tokens)"
    s = replace_once(s, anchor, anchor + '\n'
        '    print(f"CONTEXT_RECEIPT compact_math={compact_math} input_tokens={input_tokens}", flush=True)')
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
    except Exception:
        if updated != s:
            write_atomic(TARGET, original)
            restart()
        raise
    print("SWRLZ_CHAT_PREVIEW_DEPLOY_OK")
    print(rev)

if __name__ == "__main__":
    main()
