#!/usr/bin/env python3
"""Guarded source-preserving HTML quality v2 update for the existing §C Space.

Only the existing html_code_quality_v1.py helper is updated, never model
weights, source projects, accounts, runtimes or other Space files.
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
from pathlib import Path
import sys

from huggingface_hub import HfApi
from hf_chat_html_quality_release_v1 import (
    SPACE, ENGINE, read_source, publish_commit, ready, live_smoke,
)

HELPER = "html_code_quality_v1.py"
STATION = "station.py"
BACKUP = Path("swrlz-html-quality-v2-backup")
TAG = "swrlz-html-code-quality-v2"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def emit(event: str, **fields):
    print("SWRLZ_HTML_QUALITY_V2 " +
          json.dumps({"event": event, **fields}, sort_keys=True, ensure_ascii=False),
          flush=True)


def local_candidate() -> bytes:
    source = Path(__file__).with_name(HELPER).read_bytes()
    ast.parse(source, filename=HELPER)
    text = source.decode("utf-8")
    if TAG not in text:
        raise RuntimeError("Candidate lacks the expected v2 semantic version")
    for marker in ("def diagnose_html_candidate(", "def extend_candidate_check(",
                   "def quality_guidance(", "canvas-pointer-inert",
                   "invalid-radial-gradient-from", "fps-fixed-60"):
        if marker not in text:
            raise RuntimeError("Candidate missing quality boundary: " + marker)
    return source



def replace_exact(text: str, original: str, replacement: str, marker: str) -> str:
    count = text.count(original)
    if count != 1:
        raise RuntimeError("Source drift: " + marker + " occurrences=" + str(count))
    return text.replace(original, replacement, 1)


def patch_station(original: bytes) -> bytes:
    """Make validator-rejected saved drafts retry the *existing* patch executor.

    Limited to two repair handoffs with a SHA no-progress guard. Other Station
    routes, ordinary chat and the resident model are untouched.
    """
    source = original.decode("utf-8")
    tree = ast.parse(source, filename=STATION)
    functions = [n for n in tree.body if isinstance(n, ast.FunctionDef)
                 and n.name == "_swrlz_auto_code_chain"]
    if len(functions) != 1:
        raise RuntimeError("Active auto-code-chain owner not found")
    old = ast.get_source_segment(source, functions[0])
    if old is None:
        raise RuntimeError("Cannot recover exact auto-code-chain source")
    if "swrlz-validator-auto-repair-v1" in old:
        raise RuntimeError("Automatic validator repair was already installed")
    new = replace_exact(
        old, "    last_size=0\n    checkpoints=0",
        '    last_size=0\n    checkpoints=0\n'
        '    # swrlz-validator-auto-repair-v1: bounded existing-source repair.\n'
        '    repair_attempts=0\n    last_repair_sha=""',
        "checkpoint initialization")
    new = replace_exact(
        new, 'and bool(source) and not cp.get("repairNeeded")',
        'and bool(source)', "repair eligibility")
    new = replace_exact(
        new, 'and len(source)>last_size+16 and checkpoints<32',
        'and ((not cp.get("repairNeeded") and len(source)>last_size+16)\n'
        '                      or (bool(cp.get("repairNeeded")) and repair_attempts<2\n'
        '                          and str(cp.get("sourceSha256"))!=last_repair_sha))\n'
        '                     and checkpoints<32',
        "size versus validator repair safety gate")
    new = replace_exact(
        new, '        checkpoints+=1\n        last_size=len(str(saved["source"]))',
        '        checkpoints+=1\n'
        '        if saved.get("repairNeeded"):\n'
        '            repair_attempts+=1\n'
        '            last_repair_sha=str(saved["sourceSha256"])\n'
        '        last_size=len(str(saved["source"]))',
        "repair receipt")
    result = replace_exact(source, old, new, "single canonical auto-chain")
    ast.parse(result, filename=STATION)
    return result.encode("utf-8")


def preflight(api: HfApi):
    revision = api.repo_info(SPACE, repo_type="space").sha
    engine = read_source(api, revision, ENGINE)
    old = read_source(api, revision, HELPER)
    station_old = read_source(api, revision, STATION)
    station_candidate = patch_station(station_old)
    candidate = local_candidate()
    ast.parse(old.decode("utf-8"), filename=HELPER)
    engine_text = engine.decode("utf-8")
    if "from html_code_quality_v1 import " not in engine_text:
        raise RuntimeError("Qwen engine does not import the authoritative HTML quality helper")
    if "_swrlz_html_extend_check" not in engine_text:
        raise RuntimeError("Qwen engine's HTML validator is not connected")
    if digest(old) == digest(candidate):
        raise RuntimeError("Quality candidate is already active; do not publish a duplicate revision")
    BACKUP.mkdir(parents=True, exist_ok=True)
    (BACKUP / "old-helper.py").write_bytes(old)
    (BACKUP / "new-helper.py").write_bytes(candidate)
    (BACKUP / "old-station.py").write_bytes(station_old)
    (BACKUP / "new-station.py").write_bytes(station_candidate)
    receipt = {
        "space": SPACE, "expectedRevision": revision,
        "engineSha256": digest(engine), "oldHelperSha256": digest(old),
        "newHelperSha256": digest(candidate),
        "oldStationSha256": digest(station_old),
        "newStationSha256": digest(station_candidate),
        "filesChanged": [HELPER, STATION], "modelWeightsChanged": False,
        "hardwareChanged": False, "accountDataChanged": False,
        "sourceProjectChanged": False,
    }
    (BACKUP / "receipt.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    emit("PREFLIGHT_PASS", **receipt)


def publish(api: HfApi):
    if os.environ.get("SWRLZ_HTML_QUALITY_APPROVED") != "1":
        raise RuntimeError("Guarded publication approval was not provided")
    receipt = json.loads((BACKUP / "receipt.json").read_text(encoding="utf-8"))
    old = (BACKUP / "old-helper.py").read_bytes()
    candidate = (BACKUP / "new-helper.py").read_bytes()
    station_old = (BACKUP / "old-station.py").read_bytes()
    station_candidate = (BACKUP / "new-station.py").read_bytes()
    if (digest(old) != receipt["oldHelperSha256"] or
            digest(candidate) != receipt["newHelperSha256"] or
            digest(station_old) != receipt["oldStationSha256"] or
            digest(station_candidate) != receipt["newStationSha256"] or
            station_candidate != patch_station(station_old) or
            candidate != local_candidate()):
        raise RuntimeError("Preflight input changed")
    previous = receipt["expectedRevision"]
    if api.repo_info(SPACE, repo_type="space").sha != previous:
        raise RuntimeError("Concurrent HF Space update; refusing stale deployment")
    if digest(read_source(api, previous, HELPER)) != digest(old):
        raise RuntimeError("HF helper bytes changed since preflight")
    if digest(read_source(api, previous, ENGINE)) != receipt["engineSha256"]:
        raise RuntimeError("HF coding engine changed since preflight")
    if digest(read_source(api, previous, STATION)) != digest(station_old):
        raise RuntimeError("HF Station changed since preflight")
    published = None
    try:
        published = publish_commit(api, previous, {HELPER: candidate, STATION: station_candidate},
                                   "§C: fix interactive HTML canvas quality and device diagnostics")
        ready(api, published)
        live_smoke()
        emit("LIVE_ACCEPTANCE_PASS", revision=published,
             previousRevision=previous, modified=[HELPER, STATION])
    except Exception:
        emit("PUBLISH_OR_ACCEPTANCE_FAILED", revision=published)
        if published and api.repo_info(SPACE, repo_type="space").sha == published:
            restored = publish_commit(api, published, {HELPER: old, STATION: station_old},
                                     "Rollback §C HTML quality v2 to exact prior bytes")
            ready(api, restored)
            emit("ROLLBACK_RESTORED", revision=restored)
        elif published:
            emit("ROLLBACK_BLOCKED_CONCURRENT_SOURCE_UPDATE")
        raise


def main():
    if sys.argv[1:] not in (["preflight"], ["publish"]):
        raise SystemExit("Usage: preflight|publish")
    api = HfApi(token=os.environ.get("HF_TOKEN") or None)
    if sys.argv[1] == "preflight":
        preflight(api)
    else:
        publish(api)


if __name__ == "__main__":
    main()
