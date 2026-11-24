#!/usr/bin/env python3
"""GitHub Actions side of owner-approved, source-pinned model repair PR.

Runs without production credentials. Does not merge or deploy.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from pathlib import Path

from api.html_project_agent_v1 import (
    apply_proposal, verify_source, inspect_static, safe_path, ProposalError
)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--project", required=True)
    p.add_argument("--source-root", default="reviewed-source")
    p.add_argument("--output-root", default="repair-output")
    args = p.parse_args()
    sha = os.environ.get("SOURCE_SHA", "")
    if not re.fullmatch(r"[0-9a-f]{40}", sha):
        raise ProposalError("INVALID_SOURCE_SHA")
    root = Path(args.source_root).resolve()
    head = subprocess.check_output(
        ["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
    if head != sha:
        raise ProposalError("CHECKOUT_SOURCE_MISMATCH")
    folder = root / "html-projects" / args.project
    if not folder.is_dir() or folder.is_symlink():
        raise ProposalError("INVALID_PROJECT_ROOT")
    sources = {}
    for f in sorted(folder.rglob("*")):
        if f.is_symlink():
            raise ProposalError("PROJECT_SYMLINK_FORBIDDEN")
        if not f.is_file():
            continue
        rel = f.relative_to(folder).as_posix()
        if f.suffix.lower() not in {".html", ".htm", ".js", ".mjs",
                                    ".css", ".json", ".svg"}:
            continue
        safe_path(rel)
        sources[rel] = f.read_text(encoding="utf-8")
    verify_source(args.project, sources)
    proposal_raw = os.environ.get("MODEL_PROPOSAL_JSON") or ""
    if len(proposal_raw.encode("utf-8")) > 48_000:
        raise ProposalError("PROPOSAL_EXCEEDS_APPROVED_INPUT_LIMIT")
    proposal = json.loads(proposal_raw)
    result = apply_proposal(
        args.project, sources, proposal, validation=inspect_static)
    if not result["readyForOwnerReview"]:
        raise ProposalError("VALIDATION_NOT_PASSED")
    output = Path(args.output_root).resolve() / args.project
    output.mkdir(parents=True, exist_ok=True)
    for rel, content in result["proposedFiles"].items():
        path = output / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    receipt = {
        "schema": "swrlz-html-repair-agent-pr-v1",
        "sourceSha": sha, "project": args.project,
        "files": result["changedFiles"],
        "sourceHashes": result["beforeHashes"],
        "resultHashes": result["afterHashes"],
        "validation": result["validation"],
        "runtimeVerified": False,
        "ownerApproved": True,
        "merged": False,
        "deployed": False,
    }
    (output / "repair-receipt.json").write_text(
        json.dumps(receipt, indent=2), encoding="utf-8")
    print("MODEL_REPAIR_PR_STATIC_GATE_PASS", json.dumps(receipt), flush=True)


if __name__ == "__main__":
    main()
