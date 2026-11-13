#!/usr/bin/env python3
"""Source-preserving Qwen3.5-9B trial overlay for the existing §C HF Space.

PREPARE ONLY. Never uploads, restarts, changes hardware, erases the historical
model lineage, or replaces the Space with an outdated GitHub source package.
All source anchors must match the current, exact production revision.
"""
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import re
import sys

from huggingface_hub import HfApi, hf_hub_download

SPACE = "kamiloki/Swyrlz"
EXPECTED_LIVE_REVISION = "48b8d5cd8bd5fe1b5446dcfdc99e7a6374166113"
REPO = "twoody/Qwen3.5-9B-GGUF"
REV = "b647a5938c8cf40d1c3553ddd9bf2892895f0110"
WEIGHTS = "Qwen3.5-9B-Q4_K_M.gguf"
PROJECTOR = "mmproj-F16.gguf"
CHECKPOINT = f"{REPO}@{REV}/{WEIGHTS}"
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "qwen35-candidate"
BEFORE = ROOT / "qwen35-rollback"
FILES = (
    "app.py", "model_router.py", "lfm2_700m_engine.py",
    "qwen_coder_engine.py", "chat_vision.py", "README.md",
)
ASSET_FILES = {WEIGHTS: (5780090688, "8c4cc24f54473f3d4e080d4ec7fd2a40d0bbec0f94f3c807cd62694905357d54"),
               PROJECTOR: (918165888, "2f7ce3652232b91c2220fad23f5b62d110f67e84bd5ed33a7d2bea82f8ee1d26")}


def replace_once(body: str, before: str, after: str, path: str) -> str:
    count = body.count(before)
    if count != 1:
        raise AssertionError(f"{path}: source drift: expected 1 matching anchor, got {count}: {before[:80]!r}")
    return body.replace(before, after, 1)


def replace_section(body: str, start: str, following: str, new: str, path: str) -> str:
    assert body.count(start) == 1 and body.count(following) == 1, (path, "section anchors changed")
    first = body.index(start)
    last = body.index(following, first)
    assert 0 < last - first < 1400, (path, "unexpected section size", last - first)
    return body[:first] + new + body[last:]


def patch_model_engine(path: str, old: str) -> str:
    body = old
    body = replace_section(
        body, "def load(context=CONTEXT_TOKENS):", "\ndef _role_frame",
        """def load(context=CONTEXT_TOKENS):
    # One server process and one weight allocation shared by text, coder and vision.
    from qwen35_single_runtime import load as qwen35_load
    return qwen35_load()

""", path)
    # Stay within the 8K context allocated on the free 16GB Space.
    body = replace_once(body, "CONTEXT_TOKENS=32768", "CONTEXT_TOKENS=8192", path)
    body = replace_once(body, "\nOUTPUT_TOKENS=4096\n", "\nOUTPUT_TOKENS=2048\n", path)
    body = replace_once(body, "PROJECT_OUTPUT_TOKENS=8192", "PROJECT_OUTPUT_TOKENS=4096", path)
    body = replace_once(body, "LARGE_OUTPUT_TOKENS=16384", "LARGE_OUTPUT_TOKENS=6144", path)
    if path == "lfm2_700m_engine.py":
        body = replace_once(body, 'MODEL_REPO="LiquidAI/LFM2-700M-GGUF"',
                            f'MODEL_REPO="{REPO}"', path)
        body = replace_once(body, 'MODEL_FILE="LFM2-700M-Q4_K_M.gguf"',
                            f'MODEL_FILE="{WEIGHTS}"', path)
    else:
        body = replace_once(body,
                            'from coder_model_config import MODEL_REPO, MODEL_FILE, download_arguments, verify_artifact',
                            'from qwen35_single_runtime import MODEL_REPO, MODEL_FILE', path)
    return body


def patch_vision(old: str) -> str:
    path = "chat_vision.py"
    replacements = {
        'from qwen3vl_local_server import DECODE_THREADS, BATCH_THREADS, PARALLEL_REQUESTS':
            'from qwen35_single_runtime import DECODE_THREADS, BATCH_THREADS, PARALLEL_REQUESTS',
        'VISION_MODEL_VARIANT = "qwen3-vl-4b"': 'VISION_MODEL_VARIANT = "qwen3.5-9b"',
        'MODEL_REPO = "Qwen/Qwen3-VL-4B-Instruct-GGUF"': f'MODEL_REPO = "{REPO}"',
        'MODEL_REVISION = "1cd86afb9a95c410a6038ab3b40d8b578c892266"': f'MODEL_REVISION = "{REV}"',
        'MODEL_FILE = "Qwen3VL-4B-Instruct-Q4_K_M.gguf"': f'MODEL_FILE = "{WEIGHTS}"',
        'PROJECTOR_FILE = "mmproj-Qwen3VL-4B-Instruct-Q8_0.gguf"': f'PROJECTOR_FILE = "{PROJECTOR}"',
        'from qwen3vl_local_server import load': 'from qwen35_single_runtime import load',
    }
    for before, after in replacements.items():
        old = replace_once(old, before, after, path)
    return old


def patch_app(old: str) -> str:
    path = "app.py"
    old = replace_once(old,
        'from original_engine import generate_events as original_generate, load as original_load',
        'from lfm2_700m_engine import generate_events as original_generate, load as original_load',
        path)
    old = replace_once(old, 'from coder_model_config import MODEL_LABEL as CODER_LABEL',
                       'from qwen35_single_runtime import MODEL_LABEL as CODER_LABEL', path)
    old = replace_once(old, '("Original HF · LFM2-350M","stock"),("LFM2-700M Q4_K_M","700m")',
                       '("Qwen3.5-9B · Standard","stock"),("Qwen3.5-9B · General","700m")', path)
    old = replace_section(
        old, "def _warm_backends():", "\ndef _report_zerogpu_startup",
        """def _warm_backends():
    # Readiness requires real model load, tokenizer and short decode.
    # No old models are loaded. Errors are observable and do not claim readiness.
    from qwen35_single_runtime import warmup
    started = time.perf_counter()
    try:
        receipt = warmup()
        print(json.dumps({"event": "HF_WARMUP_READY", "modelId": "qwen35-9b",
                          "elapsedSeconds": round(time.perf_counter()-started, 3),
                          "receipt": receipt}), flush=True)
    except Exception as exc:
        print(json.dumps({"event": "HF_WARMUP_FAILED", "modelId": "qwen35-9b",
                          "errorType": type(exc).__name__, "detail": str(exc)[:300]}), flush=True)

""", path)
    # The Space responds after model warmup; this removes request-triggered cold load.
    old = replace_once(old,
        'threading.Thread(target=_warm_backends,daemon=True,name="swrlz-model-warmup").start()',
        '_warm_backends()', path)
    return old


def patch_router(old: str) -> str:
    path = "model_router.py"
    old = replace_once(old,
        'ModelRoute("stock","Original HF · LFM2-350M Q4_K_M",True,"LiquidAI/LFM2-350M-GGUF@31cd51db1365/LFM2-350M-Q4_K_M.gguf")',
        f'ModelRoute("stock","Qwen3.5-9B · Standard",True,"{CHECKPOINT}")', path)
    old = replace_once(old,
        'ModelRoute("700m","LFM2-700M Q4_K_M",True,"LiquidAI/LFM2-700M-GGUF/LFM2-700M-Q4_K_M.gguf")',
        f'ModelRoute("700m","Qwen3.5-9B · General",True,"{CHECKPOINT}")', path)
    old = replace_once(old, 'ModelRoute("coder",CODER_LABEL,True,CODER_CHECKPOINT)',
                       f'ModelRoute("coder","Qwen3.5-9B · Coding",True,"{CHECKPOINT}")', path)
    return old


def patch_card(old: str) -> str:
    path = "README.md"
    entry = ('  - "Qwen/Qwen3-VL-4B-Instruct-GGUF '
             'Qwen3VL-4B-Instruct-Q4_K_M.gguf,mmproj-Qwen3VL-4B-Instruct-Q8_0.gguf '
             '1cd86afb9a95c410a6038ab3b40d8b578c892266"')
    next_entry = f'  - "{REPO} {WEIGHTS},{PROJECTOR} {REV}"'
    old = replace_once(old, entry, next_entry, path)
    # Preserve all prior release history; only add a current top-of-card notice.
    marker = "# §wyrlz Chat candidate"
    addition = (marker + "\n\n### Qwen3.5-9B single-resident trial (candidate, not yet accepted)\n"
                "Text, coding and image requests share one Q4_K_M GGUF and projector, "
                "pinned at an immutable revision. No paid hardware, external inference "
                "provider or separate per-task model loading is introduced. The 8192-token "
                "initial context is intentionally bounded for free CPU Basic memory. "
                "The model is verified with a short generation before the app is exposed; "
                "device latency, §E actions, voice, and image correctness still require "
                "live validation.\n")
    return replace_once(old, marker, addition, path)


def prepare() -> None:
    api = HfApi()
    live = api.repo_info(SPACE, repo_type="space").sha
    if live != EXPECTED_LIVE_REVISION:
        raise RuntimeError(f"SPACE_REVISION_CHANGED: {live}; expected {EXPECTED_LIVE_REVISION}; no files altered")
    files = set(api.list_repo_files(SPACE, repo_type="space", revision=live))
    assert set(FILES).issubset(files), ("Production files missing", sorted(set(FILES) - files))
    assert "qwen35_single_runtime.py" not in files, "9B runtime already present: review before retry"
    if OUT.exists() or BEFORE.exists():
        raise RuntimeError("Candidate/rollback directories already exist; use clean workspace")
    OUT.mkdir()
    BEFORE.mkdir()
    patches = {
        "app.py": patch_app,
        "model_router.py": patch_router,
        "lfm2_700m_engine.py": lambda text: patch_model_engine("lfm2_700m_engine.py", text),
        "qwen_coder_engine.py": lambda text: patch_model_engine("qwen_coder_engine.py", text),
        "chat_vision.py": patch_vision,
        "README.md": patch_card,
    }
    receipts = []
    for path in FILES:
        previous = Path(hf_hub_download(SPACE, path, repo_type="space", revision=live)).read_bytes()
        original = previous.decode("utf-8")
        candidate = patches[path](original)
        if path.endswith(".py"):
            ast.parse(candidate, filename=path)
        (BEFORE / path).write_bytes(previous)
        (OUT / path).write_text(candidate, encoding="utf-8")
        receipts.append({"path": path, "beforeSha": hashlib.sha256(previous).hexdigest(),
                         "afterSha": hashlib.sha256(candidate.encode("utf-8")).hexdigest(),
                         "changed": previous != candidate.encode("utf-8")})
    extra = ROOT / "scripts" / "hf_chat_qwen35_9b_runtime.py"
    new_runtime = extra.read_text("utf-8")
    ast.parse(new_runtime, filename="qwen35_single_runtime.py")
    (OUT / "qwen35_single_runtime.py").write_text(new_runtime, encoding="utf-8")
    receipts.append({"path": "qwen35_single_runtime.py",
                     "afterSha": hashlib.sha256(new_runtime.encode()).hexdigest(), "changed": True})
    manifest = {"schema": "swrlz-qwen35-9b-single-model-candidate-v1",
                "space": SPACE, "previousRevision": live, "published": False,
                "model": CHECKPOINT, "projector": PROJECTOR,
                "files": receipts, "assets": ASSET_FILES,
                "hardwareChange": False, "productionMutation": False}
    (OUT / "CANDIDATE.json").write_text(json.dumps(manifest, indent=2), "utf-8")
    print(json.dumps({"status": "CANDIDATE_PREPARED_NOT_DEPLOYED",
                      "previousRevision": live, "files": [r["path"] for r in receipts],
                      "artifact": str(OUT)}, ensure_ascii=False))


if __name__ == "__main__":
    if sys.argv[1:] != ["prepare"]:
        raise SystemExit("Only read-only prepare is supported; no deploy mode")
    prepare()
