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
import re
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
        expected_blob = str(spec.get("sourceBlobSha") or "")
        if not target_name or target_name.startswith("/") or ".." in Path(target_name).parts:
            raise SystemExit(f"invalid accepted target: {target_name!r}")
        source = accepted_root / target_name
        if not source.is_file():
            raise SystemExit(f"accepted source missing: {target_name}")
        data = source.read_bytes()
        data.decode("utf-8")
        actual = hashlib.sha256(data).hexdigest()
        if manifest.get("integrity") == "github-blob-sha":
            header = f"blob {len(data)}\\0".encode("utf-8")
            actual_blob = hashlib.sha1(header + data).hexdigest()
            if actual_blob != expected_blob:
                raise SystemExit(f"accepted source blob mismatch: {target_name}")
        elif str(spec.get("sha256") or "") != actual:
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

    # Vendor and verify the immutable historical R39 chain, then localize the
    # accepted entrypoint so production import performs no GitHub source fetches.
    chain_spec = manifest.get("overlayChain") or []
    if manifest.get("precomposition") != "local-overlay-chain-v1" or not chain_spec:
        raise SystemExit("accepted R39 overlay chain is not registered")
    chain_files = []
    for spec in chain_spec:
        target_name = str(spec.get("acceptedTarget") or "")
        expected_blob = str(spec.get("sourceBlobSha") or "")
        source = accepted_root / target_name
        if not source.is_file():
            raise SystemExit(f"accepted overlay source missing: {target_name}")
        data = source.read_bytes()
        data.decode("utf-8")
        header = f"blob {len(data)}\\0".encode("utf-8")
        actual_blob = hashlib.sha1(header + data).hexdigest()
        if actual_blob != expected_blob:
            raise SystemExit(f"accepted overlay blob mismatch: {target_name}")
        target = output_root / target_name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        chain_files.append({
            "name": spec.get("name"),
            "sourceCommit": spec.get("sourceCommit"),
            "acceptedTarget": target_name,
            "sha256": hashlib.sha256(data).hexdigest(),
        })

    entry = output_root / "lalm" / "r39_engine.py"
    source = entry.read_text(encoding="utf-8")
    if "from pathlib import Path" not in source:
        source = source.replace("import json,time,urllib.request", "import json,time,urllib.request\\nfrom pathlib import Path", 1)
    source = source.replace(
        "def _entry(stage,**fields):",
        '_SWRLZ_CHAIN=Path(__file__).with_name("chain")\\n\\ndef _entry(stage,**fields):',
        1,
    )
    local_map = {
        "_source": "v74.py", "_overlay": "v75.py",
        "_v76_overlay": "v76.py", "_v77_overlay": "v77.py",
        "_v78_overlay": "v78.py", "_v79_overlay": "v79.py",
        "_v80_overlay": "v80.py", "_v81_overlay": "v81.py",
        "_v82_batch_source": "v82_batch.py",
        "_v85_overlay": "v85.py", "_v86_overlay": "v86.py",
        "_v87_overlay": "v87.py", "_v88_overlay": "v88.py",
        "_v89_overlay": "v89.py", "_v90_overlay": "v90.py",
    }
    for variable, filename in local_map.items():
        pattern = re.compile(
            r'(?m)^\\s*with urllib\\.request\\.urlopen\\([^\\n]+\\) as _response:'
            + re.escape(variable) + r'=_response\\.read\\([^\\n]+\\)
        "sourceRuntimeCommit": manifest.get("sourceRuntimeCommit"),
        "acceptedAuthority": "main:accepted_runtime/accepted.json",
        "activation": "bundled-at-production-build",
        "requestPathSyncRequired": False,
        "files": files,
        "r39OverlayChain": chain_files,
        "r39SourceDelivery": "local-precomposed-chain-v1",
    }
    (output_root / "generation.json").write_text(
        json.dumps(prepared, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(prepared, separators=(",", ":")))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

        )
        replacement = f'    {variable}=(_SWRLZ_CHAIN/"{filename}").read_bytes()'
        source, count = pattern.subn(replacement, source)
        if count != 1:
            raise SystemExit(f"R39 localization boundary mismatch for {variable}: {count}")
    entry.write_text(source, encoding="utf-8")
    if "urllib.request.urlopen(" in source:
        raise SystemExit("R39 prepared entrypoint still contains network source fetch")
    compile(source, str(entry), "exec")

    prepared = {
        "contract": "swrlz-prepared-runtime-generation-v3",
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
