"""Atomic HF Space CPU sprint trial, preserving unrelated production code.

Two-stage gate. PREPARE snapshots original live engine files and applies exact,
single-occurrence hunks. PUBLISH can run only after GitHub artifact upload.
No hardware upgrade, paid API, model switch, context change, or new concurrency.
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import sys
from pathlib import Path
from huggingface_hub import HfApi, CommitOperationAdd, hf_hub_download

SPACE = "kamiloki/Swyrlz"
BEFORE = Path("cpu-sprint-rollback")
AFTER = Path("cpu-sprint-candidate")
SOURCE = Path("cpu-sprint-source")
PATCHES = [{"path":"lfm2_700m_engine.py","source":"hf_space/lfm2_700m_engine.py","old":"Bound inference to CPUs available to this process, capped by the Workstation contract.\"\"\"\n    try:\n        available=len(os.sched_getaffinity(0))\n    except (AttributeError,OSError):\n        available=os.cpu_count() or 1\n    return max(1,min(16,int(available)))\n\ndef _thread_plan():\n    \"\"\"Favor broad prompt-prefill parallelism while keeping token decode conservative.\"\"\"\n    capacity=_cpu_capacity()\n    # Trial 10 decode threads on the previously measured 16-core Space;\n    # batch prefill remains bounded by the affinity/capacity contract.\n    return min(10","new":"Constrain model threads to BOTH CPU affinity and cgroup CPU quota.\"\"\"\n    try:\n        available=len(os.sched_getaffinity(0))\n    except (AttributeError,OSError):\n        available=os.cpu_count() or 1\n    capacity=max(1,min(16,int(available)))\n    # Affinity can include host CPUs unavailable to the Space's actual quota.\n    # Never silently oversubscribe a 2-vCPU fallback during a trial.\n    from runtime_capacity import runtime_capacity_snapshot\n    cpu=runtime_capacity_snapshot().get(\"cpu\") or {}\n    quota=cpu.get(\"limitCores\")\n    if isinstance(quota,(int,float)) and not isinstance(quota,bool) and 0<quota<1e6:\n        capacity=min(capacity,max(1,int(quota)))\n    return capacity\n\ndef _thread_plan():\n    \"\"\"Aggressive 14/16 CPU experiment, limited by actual Space capacity.\"\"\"\n    capacity=_cpu_capacity()\n    # Prior passing profile was 10 decode / up to 16 prefill. This trial\n    # changes only decode thread fan-out, leaving model/context/batches intact.\n    # Token decode is memory-bandwidth bound; 14 may be slower than 10.\n    return min(14"},{"path":"qwen3vl_local_server.py","source":"hf_space/qwen3vl_local_server.py","old":"The Space previously reported a 16-core CPU quota. Trial 8 decode / 14\n# image-prefill threads beyond the passing 6/12 profile; keep two cores of\n# quota headroom during prefill and retain a single serialized vision job.\n# Thread counts are configuration, NOT proof of speed or measured CPU usage.\n# Retain pinned weights, context, batch limits and cancellation semantics.\nDECODE_THREADS = 8\nBATCH_THREADS = 14","new":"Aggressive CPU trial: 8/14 -> up to 12 decode / 16 image-prefill.\n# Use cgroup quota as the ceiling; affinity alone can expose host CPUs.\n# Model weights/context/batches, cancellation and serialized vision are unchanged.\ndef _bounded_thread_plan(decode_target: int = 12, batch_target: int = 16) -> tuple[int, int]:\n    from runtime_capacity import runtime_capacity_snapshot\n    try:\n        available = len(os.sched_getaffinity(0))\n    except (AttributeError, OSError):\n        available = os.cpu_count() or 1\n    cap = max(1, min(16, int(available)))\n    cpu = runtime_capacity_snapshot().get(\"cpu\") or {}\n    quota = cpu.get(\"limitCores\")\n    if isinstance(quota, (int, float)) and not isinstance(quota, bool) and 0 < quota < 1e6:\n        cap = min(cap, max(1, int(quota)))\n    return min(decode_target, cap), min(batch_target, cap)\n\nDECODE_THREADS, BATCH_THREADS = _bounded_thread_plan()"}]
TOKEN = os.environ.get("HF_TOKEN") or ""

def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def source_file(path: str) -> Path:
    return SOURCE / "hf_space" / path

def live_bytes(path: str, revision: str) -> bytes:
    return Path(hf_hub_download(SPACE, path, repo_type="space", revision=revision, token=TOKEN)).read_bytes()

def prepare(api: HfApi) -> None:
    info = api.repo_info(SPACE, repo_type="space")
    paths = set(api.list_repo_files(SPACE, repo_type="space", revision=info.sha))
    assert "runtime_capacity.py" in paths, "Production runtime capacity module missing"
    BEFORE.mkdir(exist_ok=False)
    AFTER.mkdir(exist_ok=False)
    original_hashes = {}
    candidate_hashes = {}
    for patch in PATCHES:
        path, old, new = patch["path"], patch["old"], patch["new"]
        assert path in paths, "Production model engine missing: " + path
        text = live_bytes(path, info.sha).decode("utf-8")
        if text.count(old) != 1 or new in text:
            raise RuntimeError("Production source drift or trial already present: " + path)
        candidate = text.replace(old, new, 1)
        ast.parse(candidate, filename=path)
        expected = source_file(path).read_text(encoding="utf-8")
        assert expected.count(new) == 1, "Reviewed candidate missing expected hunk: " + path
        # Compare only the changed hunk. The Space can have other newer changes.
        if path == "qwen3vl_local_server.py":
            assert "PARALLEL_REQUESTS = 1" in candidate
            assert '"--ctx-size", "8192"' in candidate
            assert '"--batch-size", "512"' in candidate
        if path == "lfm2_700m_engine.py":
            assert "n_gpu_layers=0,use_mmap=True" in candidate
            assert "n_batch=512,n_ubatch=512" in candidate
        raw = text.encode("utf-8")
        patched = candidate.encode("utf-8")
        (BEFORE / path).write_bytes(raw)
        (AFTER / path).write_bytes(patched)
        original_hashes[path] = digest(raw)
        candidate_hashes[path] = digest(patched)
    (BEFORE / "manifest.json").write_text(json.dumps({
        "space":SPACE, "beforeRevision":info.sha, "files":original_hashes,
        "afterFiles":candidate_hashes, "trial":"700m 14/16, Qwen VL 12/16 quota-bounded",
    }, indent=2), encoding="utf-8")
    print(json.dumps({"status":"PREPARED_NOT_PUBLISHED",
                      "revision":info.sha,"paths":sorted(original_hashes)}))

def publish(api: HfApi) -> None:
    manifest=json.loads((BEFORE/"manifest.json").read_text(encoding="utf-8"))
    assert manifest["space"]==SPACE, "Wrong HF target"
    source=manifest["beforeRevision"]
    current=api.repo_info(SPACE,repo_type="space")
    if current.sha != source:
        raise RuntimeError("Space revision advanced during validation: refuse stale update")
    ops=[]
    for patch in PATCHES:
        path=patch["path"]
        original=(BEFORE/path).read_bytes()
        candidate=(AFTER/path).read_bytes()
        if digest(original)!=manifest["files"][path] or digest(candidate)!=manifest["afterFiles"][path]:
            raise RuntimeError("Rollback or candidate integrity mismatch")
        ops.append(CommitOperationAdd(path_in_repo=path,path_or_fileobj=str(AFTER/path)))
    receipt=api.create_commit(
        repo_id=SPACE,repo_type="space",operations=ops,parent_commit=source,
        commit_message="Trial §C CPU sprint 14/16 text, 12/16 vision; capacity guarded",
    )
    sha=str(getattr(receipt,"oid",None) or api.repo_info(SPACE,repo_type="space").sha)
    for patch in PATCHES:
        path=patch["path"]
        if digest(live_bytes(path,sha)) != manifest["afterFiles"][path]:
            raise RuntimeError("Published source content mismatch: "+path)
    print(json.dumps({
        "status":"PRODUCTION_SOURCE_PUBLISHED","target":SPACE,
        "previousRevision":source,"newRevision":sha,
        "paths":[patch["path"] for patch in PATCHES],
        "deviceAndRuntimeBenchmark":"NOT_VERIFIED",
    }))

if __name__=="__main__":
    if len(sys.argv)!=2 or sys.argv[1] not in {"prepare","publish"}:
        raise SystemExit("Usage: hf_cpu_sprint_release.py prepare|publish")
    if not TOKEN:
        raise SystemExit("Missing existing HF_TOKEN; no Space changes")
    api=HfApi(token=TOKEN)
    if sys.argv[1]=="prepare":prepare(api)
    else:publish(api)
