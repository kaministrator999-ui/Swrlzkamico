#!/usr/bin/env python3
"""Promote an accepted runtime rehearsal into main-owned deployable source.

Run this only after the runtime-hot state has passed live/debug acceptance.
It copies the bounded promotion allowlist into accepted_runtime/ and records
the exact rehearsal commit + hashes. It does not deploy or activate production.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

SOURCES = {
    "legacy-chat/chat.html": "web/chat.html",
    "legacy-chat/chat_enhancements.css": "web/chat_enhancements.css",
    "legacy-chat/chat_enhancements.js": "web/chat_enhancements.js",
    "legacy-chat/chat_stream_focus.js": "web/chat_stream_focus.js",
    "lalm/r39_engine.py": "runtime_hot/r39_engine.py",
    "server-policy/chat_history_policy.py": "runtime_hot/chat_history_policy.py",
}

def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def run(*args: str) -> str:
    return subprocess.check_output(args, text=True).strip()

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--runtime-ref", default="origin/runtime")
    p.add_argument("--output-root", default="accepted_runtime")
    p.add_argument("--worktree-root", default=".promotion-runtime")
    args = p.parse_args()

    runtime_sha = run("git", "rev-parse", args.runtime_ref)
    if len(runtime_sha) != 40:
        raise SystemExit("runtime ref did not resolve to a commit SHA")

    worktree = Path(args.worktree_root).resolve()
    output = Path(args.output_root).resolve()
    if worktree.exists():
        shutil.rmtree(worktree)
    run("git", "worktree", "add", "--detach", str(worktree), runtime_sha)
    try:
        staged: list[tuple[Path, bytes, str, str]] = []
        files = []
        for target_name, source_name in SOURCES.items():
            source = worktree / source_name
            if not source.is_file():
                raise SystemExit(f"required rehearsal source missing: {source_name}")
            data = source.read_bytes()
            data.decode("utf-8")
            staged.append((output / target_name, data, target_name, source_name))
            files.append({
                "owner": target_name.split("/", 1)[0],
                "runtimeSource": source_name,
                "acceptedTarget": target_name,
                "bytes": len(data),
                "sha256": digest(data),
            })

        if output.exists():
            shutil.rmtree(output)
        output.mkdir(parents=True)
        for target, data, _, _ in staged:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)

        manifest = {
            "contract": "swrlz-accepted-runtime-v1",
            "sourceRuntimeCommit": runtime_sha,
            "promotionScope": "legacy-chat+lalm+chat-history-policy",
            "deploymentInput": True,
            "runtimePollingRequired": False,
            "files": files,
        }
        (output / "accepted.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        print(json.dumps(manifest, separators=(",", ":")))
    finally:
        run("git", "worktree", "remove", "--force", str(worktree))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
