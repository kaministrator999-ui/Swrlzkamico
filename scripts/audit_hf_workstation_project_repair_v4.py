#!/usr/bin/env python3
"""Read-only audit of ACTUAL Hugging Face §C Station/Workstation code paths.

This script reports source location and tightly bounded routing snippets.
No Space writes, tokens, user data, project edits, or model inference.
"""
from __future__ import annotations

import argparse
import ast
import json
import re
from pathlib import Path

SPACE = "kamiloki/Swyrlz"
MARKERS = (
    "failure-evidence-required", "NOVERIFIEDHTMLCODEARTIFACT",
    "Classifying code request", "Candidate evidence required",
    "Evidence required", "githubSourceChangeTask",
    "projectFileEvidence", "activeHtmlProject", "should_route(payload)",
    "_swrlz_model_repair.run", "swrlz-generation",
    "workstation", "evidence_required",
    "failure_evidence_required",
)
TARGET = re.compile(
    r"station|workstation|generation|candidate|evidence|code|html|project|"
    r"repair|dispatch|intent|worker|response|chat|brain|orchestrat|publish|"
    r"execution", re.I
)

def inspect():
    from huggingface_hub import HfApi, hf_hub_download
    api = HfApi()
    revision = str(api.repo_info(SPACE, repo_type="space").sha)
    filenames = api.list_repo_files(SPACE, repo_type="space", revision=revision)
    candidates = [
        p for p in filenames
        if p.endswith(".py") and "/" not in p and TARGET.search(p)
    ]
    print("WORKSTATION_AUDIT_REVISION", revision, flush=True)
    print("WORKSTATION_AUDIT_FILES", json.dumps(candidates[:220]), flush=True)
    hits = []
    for filename in candidates[:180]:
        try:
            source = Path(hf_hub_download(
                SPACE, filename, repo_type="space", revision=revision)).read_text(
                    encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            print("WORKSTATION_AUDIT_UNREADABLE", filename, type(exc).__name__, flush=True)
            continue
        if len(source) > 1_200_000:
            print("WORKSTATION_AUDIT_OVERSIZE", filename, len(source), flush=True)
            continue
        try:
            ast.parse(source, filename=filename)
        except SyntaxError as exc:
            print("WORKSTATION_AUDIT_PARSE_FAIL", filename, exc.lineno, flush=True)
        lines = source.splitlines()
        filehits = []
        for i, line in enumerate(lines):
            terms = [m for m in MARKERS if m.lower() in line.lower()]
            if terms:
                filehits.append({"line": i + 1, "markers": terms,
                                 "source": line.strip()[:240]})
        if filehits:
            hits.append({"file": filename, "totalMatches": len(filehits),
                         "matches": filehits[:70]})
        if any(m.lower() in source.lower() for m in
               ("failure-evidence-required", "NOVERIFIEDHTMLCODEARTIFACT",
                "Classifying code request", "Candidate evidence required")):
            idx = [i for i, line in enumerate(lines) if
                   any(m.lower() in line.lower() for m in (
                       "failure-evidence-required", "NOVERIFIEDHTMLCODEARTIFACT",
                       "Classifying code request", "Candidate evidence required"))]
            for i in idx[:12]:
                start, end = max(0, i-14), min(len(lines), i+20)
                print("WORKSTATION_AUDIT_FAILURE_CONTEXT", json.dumps({
                    "file": filename, "line": i+1,
                    "lines": [f"{j+1}: {lines[j][:280]}" for j in range(start, end)]
                }), flush=True)
    print("WORKSTATION_AUDIT_HITS", json.dumps(hits[:100]), flush=True)
    if not hits:
        raise RuntimeError("NO_ROUTE_EVIDENCE_FOUND")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("inspect",))
    inspect()
