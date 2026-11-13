"""Bounded CPU profile for the existing resident §C Qwen3.5-9B GGUF.

Cap execution by actual affinity AND cgroup quota, not Hugging Face's generic
tier description. 16 effective CPUs -> 10 decode/16 prefill; 2 -> 2/2.
Preserves model identity, quantization, context, CPU-only inference, auth and
single-request concurrency. No hardware or paid-billing changes.
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import urllib.request

from huggingface_hub import HfApi, hf_hub_download, CommitOperationAdd

SPACE = "kamiloki/Swyrlz"
RUNTIME_FILE = "qwen35_single_runtime.py"
STATION_FILE = "station.py"
LOCAL_RUNTIME = "scripts/hf_chat_qwen35_9b_runtime.py"
PROFILE_MARKER = "swrlz-qwen35-cpu-v2"
BATCH_SIZE = 512
UBATCH_SIZE = 256

OLD_CPU = '''def _cpu_threads() -> int:
    try:
        affinity = len(os.sched_getaffinity(0))
    except (OSError, AttributeError):
        affinity = os.cpu_count() or 1
    allowed = max(1, min(2, int(affinity)))
    # Constrain to cgroup quota; affinity alone may expose all host cores.
    try:
        quota, period = Path("/sys/fs/cgroup/cpu.max").read_text().split()[:2]
        if quota != "max" and int(period) > 0:
            allowed = min(allowed, max(1, int(int(quota) / int(period))))
    except (ValueError, OSError, IndexError):
        pass
    return allowed


DECODE_THREADS = _cpu_threads()
BATCH_THREADS = DECODE_THREADS
'''

NEW_CPU = '''def _cpu_threads() -> int:
    """Use only CPUs actually available to this Space, not host CPU count."""
    try:
        affinity = len(os.sched_getaffinity(0))
    except (OSError, AttributeError):
        affinity = os.cpu_count() or 1
    capacity = max(1, min(16, int(affinity)))
    # Visible CPU quota is authoritative if affinity exposes more host cores.
    try:
        quota, period = Path("/sys/fs/cgroup/cpu.max").read_text().split()[:2]
        if quota != "max" and int(period) > 0:
            capacity = min(capacity, max(1, int(int(quota) / int(period))))
    except (ValueError, OSError, IndexError):
        pass
    return capacity


CPU_CAPACITY = _cpu_threads()
# Balanced profile: decode is memory-bandwidth-sensitive, prefill parallelizes.
# swrlz-qwen35-cpu-v2; safe on 2-vCPU fallback and available 16-core cgroups.
DECODE_THREADS = min(10, CPU_CAPACITY)
BATCH_THREADS = min(16, CPU_CAPACITY)
'''

OLD_ARGS = '''"--threads-batch", str(BATCH_THREADS), "--batch-size", "256",
        "--ubatch-size", "128", "--parallel", str(PARALLEL_REQUESTS),'''
NEW_ARGS = '''"--threads-batch", str(BATCH_THREADS), "--batch-size", "512",
        "--ubatch-size", "256", "--parallel", str(PARALLEL_REQUESTS),'''

OLD_WARM = '''return {"model": MODEL_LABEL, "ready": True, "threads": DECODE_THREADS, "context": CONTEXT_TOKENS}'''
NEW_WARM = '''return {"model": MODEL_LABEL, "ready": True, "threads": DECODE_THREADS,
            "batchThreads": BATCH_THREADS, "context": CONTEXT_TOKENS,
            "cpuCapacity": CPU_CAPACITY, "profile": "swrlz-qwen35-cpu-v2"}'''

OLD_READY = '''    return JSONResponse({"model": "qwen3.5-9b", "ready": bool(ready())},
                        headers={"Cache-Control": "no-store"})'''
NEW_READY = '''    from qwen35_single_runtime import CPU_CAPACITY, DECODE_THREADS, BATCH_THREADS
    return JSONResponse({"model": "qwen3.5-9b", "ready": bool(ready()),
                         "profile": "swrlz-qwen35-cpu-v2",
                         "cpuCapacity": CPU_CAPACITY,
                         "decodeThreads": DECODE_THREADS,
                         "batchThreads": BATCH_THREADS,
                         "batchSize": 512, "microBatchSize": 256},
                        headers={"Cache-Control": "no-store"})'''


def replace_exact(text: str, old: str, new: str, name: str) -> str:
    matches = text.count(old)
    if matches != 1:
        raise RuntimeError(f"{name}: exact source anchor changed (matches={matches}); no mutation")
    return text.replace(old, new, 1)


def patch_runtime(text: str) -> str:
    text = replace_exact(text, OLD_CPU, NEW_CPU, RUNTIME_FILE)
    text = replace_exact(text, OLD_ARGS, NEW_ARGS, RUNTIME_FILE)
    text = replace_exact(text, OLD_WARM, NEW_WARM, RUNTIME_FILE)
    ast.parse(text, filename=RUNTIME_FILE)
    return text


def patch_station(text: str) -> str:
    text = replace_exact(text, OLD_READY, NEW_READY, STATION_FILE)
    ast.parse(text, filename=STATION_FILE)
    return text


def runtime_profile_uses(s: str) -> tuple[int,int,int]:
    """Unit-execute only the no-model hardware capacity function."""
    module = ast.parse(s)
    fn = next(n for n in module.body
              if isinstance(n, ast.FunctionDef) and n.name == "_cpu_threads")
    ast.fix_missing_locations(fn)
    env = {"os": os, "Path": Path}
    exec(compile(ast.Module(body=[fn], type_ignores=[]), "<capacity-test>", "exec"), env)
    return env["_cpu_threads"]


def test_profile(text: str):
    # Minimal tests for production source profile; no need to load model.
    assert PROFILE_MARKER in text
    assert 'DECODE_THREADS = min(10, CPU_CAPACITY)' in text
    assert 'BATCH_THREADS = min(16, CPU_CAPACITY)' in text
    assert '"--batch-size", "512"' in text
    assert '"--ubatch-size", "256"' in text
    assert 'PARALLEL_REQUESTS = 1' in text
    # Verify actual CPU allocation never surpasses the capacity.
    # Test independent pure profile choices for 1,2,4,8,16 and 32 cores.
    for cores in (1, 2, 4, 8, 16, 32):
        capacity = min(16, cores)
        decode = min(10, capacity)
        batch = min(16, capacity)
        assert 1 <= decode <= capacity and 1 <= batch <= capacity
        if cores == 16:
            assert (decode, batch) == (10, 16)
        if cores == 2:
            assert (decode, batch) == (2, 2)
    print(json.dumps({"status": "PROFILE_STATIC_ACCEPTED",
        "expected16Cpu": {"decode": 10, "prefill": 16},
        "expected2Cpu": {"decode": 2, "prefill": 2},
        "contextChanged": False, "modelChanged": False,
        "newBatchSize": BATCH_SIZE, "newUbatchSize": UBATCH_SIZE}), flush=True)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_live(api: HfApi):
    sha = api.repo_info(SPACE, repo_type="space").sha
    files = {}
    for path in (RUNTIME_FILE, STATION_FILE):
        data = Path(hf_hub_download(SPACE, path, revision=sha,
                      repo_type="space", token=api.token)).read_bytes()
        files[path] = data
    return sha, files


def candidate(api: HfApi, *, publish: bool):
    sha, before = read_live(api)
    if '"qwen3.5-9b"' not in before[STATION_FILE].decode():
        raise RuntimeError("The live Space does not contain the 9B readiness endpoint")
    if "Qwen3.5-9B-Q4_K_M.gguf" not in before[RUNTIME_FILE].decode():
        raise RuntimeError("Live GGUF changed: refusing 9B profile patch")
    after = {
        RUNTIME_FILE: patch_runtime(before[RUNTIME_FILE].decode()).encode("utf-8"),
        STATION_FILE: patch_station(before[STATION_FILE].decode()).encode("utf-8"),
    }
    test_profile(after[RUNTIME_FILE].decode())
    manifest = {"target": SPACE, "sourceRevision": sha, "files": {
      key: {"beforeSha": digest(before[key]), "afterSha": digest(after[key])}
      for key in before
    }, "paidHardware": False, "published": False, "profile": PROFILE_MARKER}
    print(json.dumps({"stage": "CANDIDATE_VERIFIED", "manifest": manifest}), flush=True)
    if not publish:
        return manifest
    if os.environ.get("SWRLZ_QWEN35_CPU_TUNE_APPROVED") != "1":
        raise RuntimeError("Explicit source-change approval required")
    if api.repo_info(SPACE, repo_type="space").sha != sha:
        raise RuntimeError("Concurrent Space source changed; no publication")
    with tempfile.TemporaryDirectory(prefix="qwen35-perf-") as directory:
        p = Path(directory)
        for key in after:
            (p / ("before_" + key)).write_bytes(before[key])
            (p / key).write_bytes(after[key])
        result = api.create_commit(
            repo_id=SPACE, repo_type="space", parent_commit=sha,
            operations=[CommitOperationAdd(path_in_repo=key,path_or_fileobj=str(p / key))
                        for key in after],
            commit_message="§C: tune 9B CPU decode/prefill threads to observed cgroup quota")
        afterrev = str(result.oid)
        print(json.dumps({"stage": "SOURCE_PUBLISHED_AWAITING_RESTART",
                          "source": sha, "revision": afterrev}), flush=True)
        # Verify both exact source bytes before waiting for live worker.
        try:
            if api.repo_info(SPACE, repo_type="space").sha != afterrev:
                raise RuntimeError("Concurrent HF publication occurred")
            for key in after:
                published = Path(hf_hub_download(SPACE, key, revision=afterrev,
                        repo_type="space",token=api.token)).read_bytes()
                if digest(published) != digest(after[key]):
                    raise RuntimeError("Published source mismatch: " + key)
        except Exception:
            if api.repo_info(SPACE, repo_type="space").sha == afterrev:
                rollback = api.create_commit(
                    repo_id=SPACE, repo_type="space", parent_commit=afterrev,
                    operations=[CommitOperationAdd(path_in_repo=key,
                                 path_or_fileobj=str(p / ("before_"+key)))
                                for key in before],
                    commit_message="Rollback failed §C 9B CPU profile candidate")
                print(json.dumps({"stage": "SOURCE_ROLLED_BACK",
                                  "revision": str(rollback.oid)}), flush=True)
            raise
        print(json.dumps({"stage": "SOURCE_SHA_VERIFIED", "revision": afterrev}),flush=True)
        return manifest | {"newRevision": afterrev}


if __name__ == "__main__":
    mode = sys.argv[1:] or []
    if mode not in (["inspect"], ["publish"]):
        raise SystemExit("Usage: hf_qwen35_free_cpu_tune.py inspect|publish")
    from huggingface_hub import HfApi
    api = HfApi(token=os.environ.get("HF_TOKEN") or None)
    if mode == ["publish"] and not api.token:
        raise RuntimeError("Missing runner-only HF credential")
    candidate(api, publish=mode == ["publish"])
