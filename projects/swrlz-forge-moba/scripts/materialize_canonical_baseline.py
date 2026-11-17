#!/usr/bin/env python3
"""Materialize an immutable, verified §E source baseline for a parallel migration.

This does not alter the production build, manifest, patches, or HF deployment.
Run from any directory:
  python projects/swrlz-forge-moba/scripts/materialize_canonical_baseline.py --output /tmp/swrlz-engine-baseline
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    target = args.output.resolve()
    manifest = json.loads((ROOT / "source-manifest.json").read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory(prefix="swrlz-verified-baseline-") as temporary:
        package = Path(temporary) / "package"
        subprocess.run(
            [sys.executable, str(ROOT / "build_space.py"), "--output", str(package)],
            check=True,
        )
        original = (package / "index.html").read_bytes()
        modeler = (package / "modeler.html").read_bytes()
        if original != modeler:
            raise SystemExit("BASELINE_MISMATCH: modeler and index differ")
        expected_hash = manifest["finalSha256"]
        expected_bytes = manifest["finalBytes"]
        if digest(original) != expected_hash or len(original) != expected_bytes:
            raise SystemExit("BASELINE_MISMATCH: source differs from manifest")
        if target.exists() and any(target.iterdir()):
            raise SystemExit("Refusing to overwrite a nonempty baseline directory")
        target.mkdir(parents=True, exist_ok=True)
        (target / "engine.baseline.html").write_bytes(original)
        receipt = {
            "sourceVersion": manifest.get("name"),
            "sourceSha256": expected_hash,
            "sourceBytes": expected_bytes,
            "patchCount": len(manifest.get("patches", [])),
            "baselineFile": "engine.baseline.html",
            "productionChanged": False,
            "note": "Byte-for-byte baseline, not yet modularized or production-ready",
        }
        (target / "BASELINE.json").write_text(
            json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        print(json.dumps(receipt, ensure_ascii=False))


if __name__ == "__main__":
    main()
