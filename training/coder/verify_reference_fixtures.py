#!/usr/bin/env python3
"""Standalone reference-fixture verifier. Does NOT evaluate the Qwen coder model.

Runs only local subprocesses with user-installed compilers; no pip/npm/Cargo installs.
A skipped compiler is not a PASS. This script is not a production runtime dependency.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
CASES = {
    "java": {
        "file": "FrameReconciler.java",
        "tools": ["javac", "java"],
        "steps": [["javac", "FrameReconciler.java"], ["java", "FrameReconciler"]],
        "receipt": "JAVA_FRAME_PASS",
    },
    "typescript": {
        "file": "frame-reconciler.ts",
        "tools": ["tsc", "node"],
        "steps": [
            ["tsc", "--strict", "--target", "es2020", "--module", "commonjs", "--noEmit", "frame-reconciler.ts"],
            ["tsc", "--strict", "--target", "es2020", "--module", "commonjs", "--outDir", "dist", "frame-reconciler.ts"],
            ["node", "dist/frame-reconciler.js"],
        ],
        "receipt": "TYPESCRIPT_FRAME_PASS",
    },
    "kotlin": {
        "file": "FrameReconciler.kt",
        "tools": ["kotlinc", "java"],
        "steps": [
            ["kotlinc", "FrameReconciler.kt", "-include-runtime", "-d", "frames.jar"],
            ["java", "-jar", "frames.jar"],
        ],
        "receipt": "KOTLIN_FRAME_PASS",
    },
    "rust": {
        "file": "frame_reconciler.rs",
        "tools": ["rustc"],
        "steps": [
            ["rustc", "--edition=2021", "--test", "frame_reconciler.rs", "-o", "frame_tests"],
            ["./frame_tests"],
        ],
        "receipt": "test result: ok.",
    },
}


def run_case(language: str, spec: dict) -> dict:
    absent = [name for name in spec["tools"] if shutil.which(name) is None]
    source = HERE / "examples" / spec["file"]
    if not source.is_file():
        return {"language": language, "status": "FAIL", "reason": "SOURCE_NOT_FOUND"}
    if absent:
        return {"language": language, "status": "SKIPPED_TOOL_MISSING", "missing": absent}
    with tempfile.TemporaryDirectory(prefix="swrlz-coder-ref-") as raw:
        root = Path(raw)
        shutil.copyfile(source, root / spec["file"])
        receipt = ""
        for args in spec["steps"]:
            try:
                result = subprocess.run(
                    args, cwd=root, capture_output=True, text=True, timeout=70, check=False,
                )
            except (OSError, subprocess.TimeoutExpired) as exc:
                return {"language": language, "status": "FAIL", "reason": type(exc).__name__}
            if result.returncode != 0:
                return {
                    "language": language, "status": "FAIL",
                    "command": args, "returncode": result.returncode,
                    "stderrTail": result.stderr[-1200:],
                }
            receipt = result.stdout + result.stderr
        if spec["receipt"] not in receipt:
            return {"language": language, "status": "FAIL", "reason": "RECEIPT_NOT_FOUND"}
    return {"language": language, "status": "PASS_REFERENCE_FIXTURE", "receipt": spec["receipt"]}


def main() -> int:
    output = {
        "schema": "swrlz-coder-reference-check-v1",
        "scope": "teacher authored fixtures only; not Qwen-produced code or live Chat",
        "results": [run_case(language, spec) for language, spec in CASES.items()],
    }
    print(json.dumps(output, indent=2))
    return 1 if any(row["status"] == "FAIL" for row in output["results"]) else 0


if __name__ == "__main__":
    sys.exit(main())
