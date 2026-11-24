#!/usr/bin/env python3
"""Lightweight CI project test gate; no Chromium, no JS execution, no user URLs."""
from __future__ import annotations
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from api.lightweight_webpage_inspector_v1 import inspect_files, inspect_published, model_summary
from scripts import hf_html_project_publish_v1 as publishing


def check_syntax(scripts, *, require_node=True):
    if not scripts:
        return {"checked": 0, "issues": [], "available": True}
    try:
        found = subprocess.run(["node", "--version"], capture_output=True, text=True, timeout=5)
        if found.returncode:
            raise OSError("Node not available")
    except (FileNotFoundError, OSError, subprocess.TimeoutExpired):
        return {"checked": 0, "issues": [{"code": "NODE_UNAVAILABLE", "severity": "error" if require_node else "warning"}], "available": False}
    issues = []
    for script in scripts[:48]:
        code = script["text"]
        if not code.strip():
            continue
        args = ["node", "--check"]
        if script["type"] == "module":
            args.append("--input-type=module")
        try:
            result = subprocess.run(args, input=code, capture_output=True, text=True, timeout=8, env={"PATH": os.environ.get("PATH", "")})
        except (OSError, subprocess.TimeoutExpired) as exc:
            issues.append({"code": "SCRIPT_CHECK_UNAVAILABLE", "file": script["file"], "detail": type(exc).__name__, "severity": "error"})
            continue
        if result.returncode:
            issues.append({"code": "SCRIPT_SYNTAX_INVALID", "file": script["file"], "detail": (result.stderr or result.stdout)[-500:], "severity": "error"})
    return {"checked": len(scripts), "issues": issues, "available": True}


def run(project, mode="prepublish", *, require_node=True):
    raw = dict(publishing.local_files(project))
    report = inspect_files(raw)
    syntax = check_syntax(report.pop("scripts"), require_node=require_node)
    report["syntaxVerified"] = syntax["available"] and not syntax["issues"]
    report["syntaxCheckedCount"] = syntax["checked"]
    report["issues"].extend(syntax["issues"])
    report["staticPass"] = report["staticPass"] and report["syntaxVerified"]
    if mode == "published":
        remote = inspect_published(project, raw)
        report["http"] = remote
        report["staticPass"] = report["staticPass"] and remote["deployedBytesMatch"]
    report["status"] = "STATIC_PASS_RENDERING_UNVERIFIED" if report["staticPass"] and report["renderingRequiredForFullVerification"] else ("STATIC_PASS_INTERACTIONS_UNVERIFIED" if report["staticPass"] else "FAILED")
    return report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--mode", choices=["prepublish", "published"], default="prepublish")
    ap.add_argument("--output")
    args = ap.parse_args()
    result = run(args.project, args.mode)
    if args.output:
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print("SWRLZ_LIGHTWEIGHT_WEB_TEST", model_summary(result), flush=True)
    if not result["staticPass"]:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
