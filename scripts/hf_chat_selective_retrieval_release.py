#!/usr/bin/env python3
"""Guarded existing-Space rollout of §C selective retrieval, with exact rollback.

Uses only the owner-configured Hugging Face release token from CI.
Never changes model weights, routes, identity, hardware, user data, or §E.
"""
from __future__ import annotations

import ast
import hashlib
import http.cookiejar
import importlib.util
import json
import os
from pathlib import Path
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid

from huggingface_hub import HfApi, hf_hub_download, CommitOperationAdd, CommitOperationDelete
from hf_chat_selective_retrieval_trial import prepare, SPACE, ENGINE, MODULE
from api.selective_retrieval import bounded_evidence, search_queries

BASE = "https://kamiloki-swyrlz.hf.space"
OUT = Path("swrlz-selective-retrieval-rollback")
NEW_FLAG = 'os.environ.get("SWRLZ_SELECTIVE_RETRIEVAL_ENABLED", "1").strip().lower() not in {"0","false","off"}'
OLD_FLAG = 'os.environ.get("SWRLZ_SELECTIVE_RETRIEVAL_ENABLED") == "1"'
HEADERS = {"User-Agent": "SWRLZ-Selective-Retrieval-Guarded-20261115",
           "Cache-Control": "no-cache"}


def checksum(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def assert_revision(api, expected: str):
    current = api.repo_info(SPACE, repo_type="space").sha
    if current != expected:
        raise RuntimeError("HF Space changed concurrently, refusing a stale mutation")


def read_live(api, path: str, revision: str) -> bytes:
    return Path(hf_hub_download(SPACE, path, repo_type="space",
                               revision=revision, token=api.token)).read_bytes()


def public_search_acceptance(api, revision: str):
    path = hf_hub_download(SPACE, "api/online_research.py", repo_type="space",
                           revision=revision, token=api.token)
    spec = importlib.util.spec_from_file_location("swrlz_exact_search_acceptance", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load exact live public search source")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    prompt = "Was Diablo II Classic released before Lord of Destruction expansion?"
    plan = search_queries(prompt)
    bundle = module.research({"prompt": prompt, "researchQueries": plan,
                               "requestId": "swrlz-selective-public-test"})
    chosen = bounded_evidence(bundle, query=prompt)
    print("SWRLZ_SELECTIVE_PUBLIC_SEARCH_PREFLIGHT " + json.dumps(
        {"queries": len(plan), "raw": len(bundle.get("evidence") or []),
         "relevant": chosen["resultCount"],
         "titles": [r["title"][:100] for r in chosen["evidence"][:3]]}), flush=True)
    if not chosen["resultCount"]:
        raise RuntimeError("Public search did not return relevant source evidence")


def stage(api):
    OUT.mkdir(parents=True, exist_ok=True)
    candidate = OUT / "candidate"
    manifest = prepare(candidate, api, api.token)
    before_sha = manifest["baseRevision"]
    paths = set(api.list_repo_files(SPACE, repo_type="space", revision=before_sha))
    if MODULE in paths:
        raise RuntimeError("Existing selective module detected; refuse overwriting another deployment")
    original = (candidate / "before" / ENGINE).read_bytes()
    text = (candidate / ENGINE).read_text("utf-8")
    if text.count(OLD_FLAG) != 1:
        raise RuntimeError("Selective feature flag anchor drift")
    # The user approved this live trial; default ON with an emergency opt-out.
    text = text.replace(OLD_FLAG, NEW_FLAG, 1)
    ast.parse(text, filename=ENGINE)
    if text.count("swrlz-selective-factual-retrieval-v1") != 1:
        raise RuntimeError("Duplicate or missing selective retrieval hook")
    enabled = candidate / ENGINE
    enabled.write_text(text, "utf-8")
    new_module = candidate / MODULE
    if not new_module.is_file():
        raise RuntimeError("Review candidate module missing")
    ast.parse(new_module.read_text("utf-8"), filename=MODULE)
    before = OUT / "before" / ENGINE
    before.parent.mkdir(parents=True, exist_ok=True)
    before.write_bytes(original)
    receipt = {"space": SPACE, "before": before_sha,
               "fileHashes": {ENGINE: checksum(enabled.read_bytes()),
                              MODULE: checksum(new_module.read_bytes())},
               "originalEngineHash": checksum(original),
               "status": "STAGED_NOT_PUBLISHED",
               "featureEnabledByDefault": True,
               "disable": "SWRLZ_SELECTIVE_RETRIEVAL_ENABLED=0"}
    (OUT / "receipt.json").write_text(json.dumps(receipt, indent=2), "utf-8")
    return receipt, enabled, new_module


def ready(api, revision: str):
    start = time.monotonic()
    attempts = 0
    while time.monotonic() - start < 1000:
        assert_revision(api, revision)
        attempts += 1
        try:
            with urllib.request.urlopen(
                urllib.request.Request(BASE + "/api/hf/qwen35-ready", headers=HEADERS),
                timeout=14,
            ) as response:
                observation = json.load(response)
            if observation.get("ready") is True and observation.get("model") == "qwen3.5-9b":
                print("SWRLZ_SELECTIVE_9B_READY " + json.dumps(
                    {"attempts": attempts, "model": observation.get("model"),
                     "profile": observation.get("profile")}), flush=True)
                return
        except (OSError, ValueError, urllib.error.URLError):
            pass
        if attempts % 8 == 0:
            print("SWRLZ_SELECTIVE_WARMING " + json.dumps({"attempts": attempts}), flush=True)
        time.sleep(12)
    raise RuntimeError("Qwen3.5-9B not ready on updated Space")


def ask(label: str, prompt: str, *, expected_research: bool):
    jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    rid = str(uuid.uuid4())
    tid = "swrlz-selective-synthetic-" + str(uuid.uuid4())
    req = urllib.request.Request(
        BASE + "/api/lalm_station/send",
        data=json.dumps({"modelId": "700m", "prompt": prompt, "threadId": tid,
                         "requestId": rid, "profileId": "LALM", "profile": "",
                         "userProfile": "", "timeZone": "UTC"}).encode(),
        method="POST", headers={**HEADERS, "Content-Type": "application/json"})
    with opener.open(req, timeout=40) as response:
        if response.status != 202:
            raise RuntimeError("Synthetic request not accepted by live station")
        response.read(1024)
    url = BASE + "/api/lalm_station/stream?" + urllib.parse.urlencode({"requestId": rid})
    phases = []
    parts = []
    terminal = None
    start = time.monotonic()
    with opener.open(urllib.request.Request(url, headers=HEADERS), timeout=240) as response:
        for line in response:
            if time.monotonic() - start > 235:
                raise RuntimeError("Synthetic model output exceeded bounded time")
            try:
                event = json.loads(line)
            except (ValueError, UnicodeError):
                continue
            kind = event.get("type")
            if kind == "STATUS":
                phases.append(event.get("phase"))
            elif kind == "DELTA":
                parts.append(str(event.get("text") or ""))
            elif kind in ("COMPLETE", "COMPLETED", "FAILED", "CANCELLED"):
                terminal = kind
                break
    text = "".join(parts)
    confirmed = "RESEARCH_READY" in phases
    print("SWRLZ_SELECTIVE_LIVE_TURN " + json.dumps({
        "label": label, "terminal": terminal, "researchReady": confirmed,
        "phases": [str(x)[:60] for x in phases[-12:]],
        "characters": len(text), "seconds": round(time.monotonic() - start, 2)}),
        flush=True)
    if terminal not in ("COMPLETE", "COMPLETED") or len(text) < 8:
        raise RuntimeError(label + " did not deliver a completed answer")
    if confirmed != expected_research:
        raise RuntimeError(label + " took the wrong retrieval route")
    if label == "Diablo II factual" and not ("diablo" in text.lower() or "2000" in text or "2001" in text):
        raise RuntimeError("Factual response not about the requested game")


def rollback(api, published: str, receipt: dict):
    assert_revision(api, published)
    before_path = OUT / "before" / ENGINE
    if checksum(before_path.read_bytes()) != receipt["originalEngineHash"]:
        raise RuntimeError("Original source snapshot integrity failed")
    restored = api.create_commit(
        repo_id=SPACE, repo_type="space", parent_commit=published,
        operations=[CommitOperationAdd(path_in_repo=ENGINE, path_or_fileobj=str(before_path)),
                    CommitOperationDelete(path_in_repo=MODULE)],
        commit_message="Rollback §C selective factual retrieval trial to exact prior engine")
    previous = str(restored.oid)
    assert_revision(api, previous)
    if checksum(read_live(api, ENGINE, previous)) != receipt["originalEngineHash"]:
        raise RuntimeError("Selective retrieval rollback source verification failed")
    print("SWRLZ_SELECTIVE_ROLLED_BACK " + json.dumps(
        {"from": published, "to": previous, "restoredOriginal": True}), flush=True)


def main():
    if os.environ.get("SWRLZ_SELECTIVE_RETRIEVAL_DEPLOY_APPROVED") != "1":
        raise RuntimeError("No explicit owner approval for existing Space")
    token = os.environ.get("HF_TOKEN", "")
    if len(token) < 12:
        raise RuntimeError("Missing existing HF_TOKEN deployment credential")
    api = HfApi(token=token)
    receipt, engine, module = stage(api)
    assert_revision(api, receipt["before"])
    public_search_acceptance(api, receipt["before"])
    assert_revision(api, receipt["before"])
    result = api.create_commit(
        repo_id=SPACE, repo_type="space", parent_commit=receipt["before"],
        operations=[CommitOperationAdd(path_in_repo=ENGINE, path_or_fileobj=str(engine)),
                    CommitOperationAdd(path_in_repo=MODULE, path_or_fileobj=str(module))],
        commit_message="§C Qwen3.5-9B: selective public fact retrieval with opt-out")
    published = str(result.oid)
    receipt.update({"status": "SOURCE_PUBLISHED_ACCEPTANCE_PENDING", "published": published})
    (OUT / "receipt.json").write_text(json.dumps(receipt, indent=2), "utf-8")
    try:
        assert_revision(api, published)
        for path, expect in receipt["fileHashes"].items():
            if checksum(read_live(api, path, published)) != expect:
                raise RuntimeError("Published candidate differs from reviewed source: " + path)
        ready(api, published)
        ask("Diablo II factual",
            "Was Diablo II Classic released before Lord of Destruction expansion?",
            expected_research=True)
        ask("conceptual direct", "What is an inventory grid?", expected_research=False)
    except Exception:
        print("SWRLZ_SELECTIVE_ACCEPTANCE_FAILED_ATTEMPT_ROLLBACK", flush=True)
        rollback(api, published, receipt)
        raise
    receipt["status"] = "LIVE_VERIFIED"
    (OUT / "receipt.json").write_text(json.dumps(receipt, indent=2), "utf-8")
    print("SWRLZ_SELECTIVE_RETRIEVAL_LIVE_ACCEPTED " + json.dumps(
        {"space": SPACE, "published": published,
         "model": "qwen3.5-9b", "hardwareChanged": False}), flush=True)


if __name__ == "__main__":
    main()
