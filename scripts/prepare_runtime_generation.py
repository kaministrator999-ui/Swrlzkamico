#!/usr/bin/env python3
"""Validate and package the main-owned accepted runtime generation.

The mutable runtime branch is rehearsal authority only. Production preparation
consumes accepted_runtime/, verifies its promotion manifest/hashes, and emits
the immutable bundle generation. No network access or production activation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--accepted-root", default="accepted_runtime")
    parser.add_argument("--output-root", required=True)
    args = parser.parse_args()

    accepted_root = Path(args.accepted_root).resolve()
    output_root = Path(args.output_root).resolve()
    authority = accepted_root / "accepted.json"
    if not authority.is_file():
        raise SystemExit("accepted runtime authority missing")
    manifest = json.loads(authority.read_text(encoding="utf-8"))
    if manifest.get("contract") != "swrlz-accepted-runtime-v1":
        raise SystemExit("accepted runtime contract mismatch")
    if manifest.get("status") == "bootstrap-pending-explicit-promotion":
        raise SystemExit("accepted runtime has not been explicitly promoted yet")
    files_spec = manifest.get("files")
    if not isinstance(files_spec, list) or not files_spec:
        raise SystemExit("accepted runtime contains no promoted files")

    if output_root.exists():
        shutil.rmtree(output_root)
    output_root.mkdir(parents=True)

    files = []
    for spec in files_spec:
        target_name = str(spec.get("acceptedTarget") or "")
        expected = str(spec.get("sha256") or "")
        if not target_name or target_name.startswith("/") or ".." in Path(target_name).parts:
            raise SystemExit(f"invalid accepted target: {target_name!r}")
        source = accepted_root / target_name
        if not source.is_file():
            raise SystemExit(f"accepted source missing: {target_name}")
        data = source.read_bytes()
        data.decode("utf-8")
        actual = hashlib.sha256(data).hexdigest()
        if actual != expected:
            raise SystemExit(f"accepted source hash mismatch: {target_name}")
        target = output_root / target_name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        files.append({
            "owner": spec.get("owner"),
            "acceptedTarget": target_name,
            "runtimeSource": spec.get("runtimeSource"),
            "bytes": len(data),
            "sha256": actual,
        })

    prepared = {
        "contract": "swrlz-prepared-runtime-generation-v2",
        "sourceRuntimeCommit": manifest.get("sourceRuntimeCommit"),
        "acceptedAuthority": "main:accepted_runtime/accepted.json",
        "activation": "bundled-at-production-build",
        "requestPathSyncRequired": False,
        "files": files,
    }
    (output_root / "generation.json").write_text(
        json.dumps(prepared, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(prepared, separators=(",", ":")))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
