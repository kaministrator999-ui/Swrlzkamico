#!/usr/bin/env python3
"""Prepare one immutable accepted runtime generation for production bundling.

This script runs in the approved production workflow before Vercel build. It
copies only the legacy Chat + hydrated LALM/history-policy owners from one
already-resolved runtime commit and emits a hash manifest. It performs no
network access and does not activate production.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path

SOURCES = {
    "legacy-chat/chat.html": "web/chat.html",
    "legacy-chat/chat_enhancements.css": "web/chat_enhancements.css",
    "legacy-chat/chat_enhancements.js": "web/chat_enhancements.js",
    "legacy-chat/chat_stream_focus.js": "web/chat_stream_focus.js",
    "lalm/r39_engine.py": "runtime_hot/r39_engine.py",
    "server-policy/chat_history_policy.py": "runtime_hot/chat_history_policy.py",
}

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime-root", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--runtime-sha", required=True)
    args = parser.parse_args()

    runtime_root = Path(args.runtime_root).resolve()
    output_root = Path(args.output_root).resolve()
    runtime_sha = args.runtime_sha.strip().lower()
    if len(runtime_sha) != 40 or any(ch not in "0123456789abcdef" for ch in runtime_sha):
        raise SystemExit("runtime SHA must be a 40-character commit SHA")
    if output_root.exists():
        shutil.rmtree(output_root)
    output_root.mkdir(parents=True)

    files = []
    for target_name, source_name in SOURCES.items():
        source = runtime_root / source_name
        if not source.is_file():
            raise SystemExit(f"required runtime source missing: {source_name}")
        data = source.read_bytes()
        if b"\x00" in data:
            raise SystemExit(f"runtime source is not text: {source_name}")
        data.decode("utf-8")
        target = output_root / target_name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        files.append({
            "owner": target_name.split("/", 1)[0],
            "source": source_name,
            "target": target_name,
            "bytes": len(data),
            "sha256": sha256(target),
        })

    manifest = {
        "contract": "swrlz-prepared-runtime-generation-v1",
        "runtimeCommit": runtime_sha,
        "activation": "bundled-at-production-build",
        "requestPathSyncRequired": False,
        "files": files,
    }
    (output_root / "generation.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, separators=(",", ":")))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
