#!/usr/bin/env python3
"""§C 16-vs-18 thread experiment on the existing 16-core HF Space.

No new CPUs, hardware upgrades, private messages or model changes. Baseline and
candidate use two anonymous repeatable coding prompts each. Keep only on
repeatable measured improvement; restore exact original bytes otherwise.
"""
from __future__ import annotations

import ast
import hashlib
import http.cookiejar
import json
import os
from pathlib import Path
import statistics
import sys
import time
import urllib.parse
import urllib.request
import uuid

from huggingface_hub import CommitOperationAdd, HfApi, hf_hub_download

SPACE = "kamiloki/Swyrlz"
FILE = "qwen35_single_runtime.py"
BASE = "https://kamiloki-swyrlz.hf.space"
BACKUP = Path("qwen35-thread-experiment-backup")
ORIGINAL = BACKUP / FILE
REVISION = BACKUP / "source_revision.txt"
OLD = "DECODE_THREADS = min(16, CPU_CAPACITY)\nBATCH_THREADS = min(16, CPU_CAPACITY)"
NEW = ("# swrlz-qwen35-thread-trial-18; intentionally compare 18 worker "
       "threads on the unchanged 16-CPU quota.\n"
       "DECODE_THREADS = 18 if CPU_CAPACITY == 16 else min(16, CPU_CAPACITY)\n"
       "BATCH_THREADS = 18 if CPU_CAPACITY == 16 else min(16, CPU_CAPACITY)")
HEADERS = {"Cache-Control": "no-cache", "User-Agent": "Swyrlz-9B-18Thread-AB-20261113"}


def emit(stage, **data):
    print("THREAD_EXPERIMENT", json.dumps({"stage": stage, **data}, sort_keys=True),
          flush=True)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def fetch_json(path, timeout=20):
    request = urllib.request.Request(BASE + path, headers=HEADERS)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.load(response)


def ready():
    return fetch_json("/api/hf/qwen35-ready")


def assert_ready(decode):
    r = ready()
    if (r.get("model"), r.get("ready"), r.get("cpuCapacity"),
        r.get("decodeThreads"), r.get("batchThreads")) != (
            "qwen3.5-9b", True, 16, decode, decode):
        raise RuntimeError("Expected 9B 16-core profile with %s threads, observed %r" %
                           (decode, {k:r.get(k) for k in (
                           "model","ready","cpuCapacity","decodeThreads","batchThreads")}))
    return r


def space_head(api):
    return api.repo_info(SPACE, repo_type="space").sha


def src(api, revision):
    path = hf_hub_download(SPACE, FILE, repo_type="space", revision=revision, token=api.token)
    return Path(path).read_bytes()


def source_candidate(original):
    content = original.decode("utf-8")
    if content.count(OLD) != 1 or "swrlz-qwen35-thread-trial-18" in content:
        raise RuntimeError("Expected 16/16 live source anchor changed; no mutation")
    if "Qwen3.5-9B-Q4_K_M.gguf" not in content or "PARALLEL_REQUESTS = 1" not in content:
        raise RuntimeError("Resident model or concurrency changed; no mutation")
    candidate = content.replace(OLD, NEW, 1)
    ast.parse(candidate, filename=FILE)
    return candidate.encode("utf-8")


def quota_check():
    info = fetch_json("/api/hf/runtime-capacity")
    cores = (info.get("cpu") or {}).get("limitCores")
    if not isinstance(cores, (float, int)) or abs(cores - 16) > 0.01:
        raise RuntimeError("Live CPU quota changed; no 16-to-18 trial")
    emit("MEASURED_QUOTA", quotaCores=cores, paidUpgrade=False)


def probe(model, prompt, label):
    opener = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    request_id = str(uuid.uuid4())
    payload = {"modelId": model, "prompt": prompt,
               "requestId": request_id, "threadId": "thread-ab-"+str(uuid.uuid4()),
               "profileId": "LALM", "profile": "", "userProfile": "",
               "timeZone": "UTC"}
    started = time.monotonic()
    req = urllib.request.Request(BASE + "/api/lalm_station/send",
              data=json.dumps(payload).encode("utf-8"), method="POST",
              headers={"Content-Type": "application/json", **HEADERS})
    with opener.open(req, timeout=35) as response:
        if response.status != 202:
            raise RuntimeError("Synthetic send not accepted")
        response.read()
    stream = BASE + "/api/lalm_station/stream?" + urllib.parse.urlencode(
        {"requestId": request_id})
    first = None
    count = 0
    terminal = None
    with opener.open(urllib.request.Request(stream, headers=HEADERS),
                     timeout=220) as response:
        for raw in response:
            if time.monotonic() - started > 205:
                break
            try:
                event = json.loads(raw)
            except (ValueError, UnicodeError):
                continue
            typ = event.get("type")
            if typ == "DELTA":
                delta = str(event.get("text") or "")
                if delta and first is None:
                    first = time.monotonic()-started
                count += len(delta)
            if typ in ("COMPLETE", "COMPLETED", "FAILED", "CANCELLED"):
                terminal = typ
                break
    total = time.monotonic()-started
    result = {"case": label, "totalSec": round(total, 3),
              "firstTextSec": round(first, 3) if first is not None else None,
              "outputChars": count, "terminal": terminal}
    emit("SYNTHETIC_RESULT", **result)
    if terminal not in ("COMPLETE", "COMPLETED") or first is None or count < 15:
        raise RuntimeError("Synthetic benchmark failed acceptance: "+label)
    return result


CASES = (
    ("coder", "Write a Python function named square(n) that returns n * n, and show one example call.", "square"),
    ("coder", "Write a Python function named is_even(n) returning whether n is even, and show one example call.", "even"),
)


def measure(profile):
    assert_ready(profile)
    observations = []
    for model, prompt, label in CASES:
        observations.append(probe(model, prompt, label))
    return observations


def wait_profile(api, expected_sha, threads, timeout=850):
    deadline = time.monotonic()+timeout
    attempts=0
    while time.monotonic() < deadline:
        if space_head(api) != expected_sha:
            raise RuntimeError("Concurrent Space release; cannot assume ownership")
        attempts += 1
        try:
            snap = assert_ready(threads)
            emit("READY", threads=threads, attempts=attempts, profile=snap.get("profile"))
            return
        except Exception as exc:
            if attempts % 6 == 0:
                emit("WARMUP", threads=threads, attempts=attempts,
                     reason=type(exc).__name__)
        time.sleep(12)
    raise RuntimeError("Trial model not ready in bounded window")


def publish(api, previous_sha, contents, message):
    if space_head(api) != previous_sha:
        raise RuntimeError("Concurrent HF update, refusing to overwrite")
    from tempfile import NamedTemporaryFile
    with NamedTemporaryFile(prefix="swrlz-thread-ab-", suffix=".py") as f:
        f.write(contents)
        f.flush()
        updated = api.create_commit(
            repo_id=SPACE, repo_type="space", parent_commit=previous_sha,
            operations=[CommitOperationAdd(path_in_repo=FILE, path_or_fileobj=f.name)],
            commit_message=message)
    revision = str(updated.oid)
    actual = src(api, revision)
    if sha(actual) != sha(contents):
        raise RuntimeError("Published source differs from candidate")
    emit("SOURCE_VERIFIED", revision=revision, sha256=sha(contents))
    return revision


def decision(before, after):
    a = [r["totalSec"] for r in before]
    b = [r["totalSec"] for r in after]
    fa = [r["firstTextSec"] for r in before]
    fb = [r["firstTextSec"] for r in after]
    baseline = statistics.median(a)
    candidate = statistics.median(b)
    gain = (baseline - candidate)/baseline
    safe = (gain >= 0.05 and
            statistics.median(fb) <= statistics.median(fa)*0.98 and
            all(new <= old*1.10 for new,old in zip(b,a)))
    emit("COMPARISON", baselineMedianSec=round(baseline,3),
         candidateMedianSec=round(candidate,3), changePct=round(gain*100,2),
         firstText16=round(statistics.median(fa),3),
         firstText18=round(statistics.median(fb),3),
         keep18=safe, minimumImprovementPct=5)
    return safe


def snapshot():
    api=HfApi(token=os.environ.get("HF_TOKEN") or None)
    original_revision=space_head(api)
    content=src(api, original_revision)
    source_candidate(content)
    assert_ready(16)
    quota_check()
    BACKUP.mkdir(exist_ok=True)
    ORIGINAL.write_bytes(content)
    REVISION.write_text(original_revision, encoding="ascii")
    emit("EXACT_SOURCE_SNAPSHOT", revision=original_revision, sha256=sha(content),
         existingThreads=16, trialThreads=18)


def trial():
    token=os.environ.get("HF_TOKEN", "")
    if len(token) < 12 or os.environ.get("SWRLZ_THREAD_TRIAL_APPROVED") != "1":
        raise RuntimeError("Explicit release authorization/credential missing")
    api=HfApi(token=token)
    original_revision=REVISION.read_text(encoding="ascii").strip()
    original=ORIGINAL.read_bytes()
    if space_head(api) != original_revision or sha(src(api, original_revision)) != sha(original):
        raise RuntimeError("Live source changed after backup; no mutation")
    candidate=source_candidate(original)
    assert_ready(16)
    quota_check()
    baseline=measure(16)
    current_revision=None
    kept=False
    try:
        current_revision=publish(api, original_revision, candidate,
             "§C temporary 18-thread trial on unchanged 16-core quota")
        wait_profile(api, current_revision, 18)
        newer=measure(18)
        kept=decision(baseline,newer)
    finally:
        if current_revision and not kept:
            if space_head(api) == current_revision:
                restored=publish(api, current_revision, original,
                    "§C rollback oversubscribed thread experiment to exact 16/16 source")
                wait_profile(api, restored, 16)
                emit("ROLLED_BACK", revision=restored, verifiedExact=True)
            else:
                emit("ROLLBACK_BLOCKED", reason="Concurrent HF update; avoid overwriting")
                raise RuntimeError("Concurrent release prevents controlled rollback")
    if kept:
        emit("KEPT_18", revision=current_revision, expectedCpuQuota=16)
    else:
        emit("KEPT_16", reason="No stable >=5% improvement from oversubscription")


if __name__ == "__main__":
    if sys.argv[1:] == ["snapshot"]:
        snapshot()
    elif sys.argv[1:] == ["trial"]:
        trial()
    else:
        raise SystemExit("Usage: thread_trial.py snapshot|trial")
