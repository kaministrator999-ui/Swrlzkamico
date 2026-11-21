#!/usr/bin/env python3
"""Read-only candidate preparation for §C selective public-fact retrieval.

Targets existing kamiloki/Swyrlz ONLY. Does not deploy, alter model weights,
change auth, add a Space, enable paid hardware, or send user data to search.
"""
from __future__ import annotations
import argparse
import ast
import hashlib
import json
import os
from pathlib import Path

SPACE = "kamiloki/Swyrlz"
ENGINE = "lfm2_700m_engine.py"
RESEARCH = "api/online_research.py"
MODULE = "api/selective_retrieval.py"
ANCHOR = "def generate_events(payload):\n"
INJECTION = r'''def generate_events(payload):
    import os
    # swrlz-selective-factual-retrieval-v1: no web search unless owner enables.
    # Never transmit history, identity, files or source changes to search.
    if os.environ.get("SWRLZ_SELECTIVE_RETRIEVAL_ENABLED") == "1":
        from api.selective_retrieval import enrich_payload
        try:
            from api.online_research import research as _public_research, _page_fetch as _public_fetch
        except ImportError:
            _public_research = None
            _public_fetch = None
        payload, _research_route = enrich_payload(
            payload, _public_research, fetch_page=_public_fetch, enabled=True)
        if _research_route["phase"] in ("RESEARCH_READY", "RESEARCH_UNAVAILABLE"):
            yield {"type": "STATUS", "phase": _research_route["phase"],
                   "reason": _research_route["reason"]}
'''

def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def patch_engine(text: str) -> str:
    if "swrlz-selective-factual-retrieval-v1" in text:
        raise RuntimeError("Candidate already present; refuse duplicate insertion")
    if text.count(ANCHOR) != 1:
        raise RuntimeError("Current live generator anchor missing or ambiguous")
    if "onlineContext" not in text:
        raise RuntimeError("Live model has no proven onlineContext hook")
    after = text.replace(ANCHOR, INJECTION, 1)
    assert after.replace(INJECTION, ANCHOR, 1) == text
    ast.parse(after, filename=ENGINE)
    return after

def prepare(root: Path, api, token: str | None):
    from huggingface_hub import hf_hub_download
    revision = api.repo_info(SPACE, repo_type="space").sha
    if not isinstance(revision, str) or len(revision) != 40:
        raise RuntimeError("Cannot pin exact current Hugging Face Space commit")
    downloaded = {}
    for name in (ENGINE, RESEARCH):
        path = hf_hub_download(SPACE, name, repo_type="space",
                               revision=revision, token=token)
        downloaded[name] = Path(path).read_bytes()
    if b"def research(" not in downloaded[RESEARCH]:
        raise RuntimeError("Stable live web research adapter not found")
    module = Path(__file__).resolve().parents[1] / MODULE
    if not module.is_file():
        raise RuntimeError("Selective retrieval module missing")
    new_engine = patch_engine(downloaded[ENGINE].decode("utf-8"))
    ast.parse(module.read_text("utf-8"), filename=MODULE)
    root.mkdir(parents=True, exist_ok=True)
    before = root / "before" / ENGINE
    before.parent.mkdir(parents=True, exist_ok=True)
    before.write_bytes(downloaded[ENGINE])
    (root / ENGINE).write_text(new_engine, "utf-8")
    staged = root / MODULE
    staged.parent.mkdir(parents=True, exist_ok=True)
    staged.write_bytes(module.read_bytes())
    manifest = {
        "space": SPACE, "baseRevision": revision,
        "status": "PREPARED_ONLY_NOT_DEPLOYED",
        "featureFlagDefault": "off",
        "enableViaServerEnvironment": "SWRLZ_SELECTIVE_RETRIEVAL_ENABLED=1",
        "sourceProof": {
            ENGINE: {"originalSha256": digest(downloaded[ENGINE]),
                     "candidateSha256": digest(new_engine.encode("utf-8"))},
            RESEARCH: {"unchangedSha256": digest(downloaded[RESEARCH])},
            MODULE: {"candidateSha256": digest(module.read_bytes())},
        },
        "changedPaths": [ENGINE, MODULE],
        "guardrails": ["no new Space", "no model weight changes",
                       "no automatic lookup unless enabled", "exact live source only",
                       "retrieval evidence never grants instruction authority"],
    }
    (root / "CANDIDATE.json").write_text(json.dumps(manifest, indent=2), "utf-8")
    return manifest

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=".artifacts/selective-retrieval-trial")
    args = parser.parse_args(argv)
    from huggingface_hub import HfApi
    token = os.getenv("HF_TOKEN") or None
    manifest = prepare(Path(args.out), HfApi(token=token), token)
    print(json.dumps({"stage": "STATIC_CANDIDATE_READY_NOT_DEPLOYED",
                      "space": manifest["space"], "baseRevision": manifest["baseRevision"],
                      "changedPaths": manifest["changedPaths"]}, sort_keys=True))

if __name__ == "__main__":
    main()
