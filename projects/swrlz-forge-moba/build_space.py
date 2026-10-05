#!/usr/bin/env python3
import argparse
import base64
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PAYLOAD = ROOT / "payload"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    parts = sorted(PAYLOAD.glob("part-*.txt"))
    if not parts:
        raise SystemExit("No payload chunks found")

    encoded = "".join(p.read_text(encoding="utf-8").strip() for p in parts)
    compressed = base64.b64decode(encoded)
    html = gzip.decompress(compressed)

    manifest = json.loads((ROOT / "source-manifest.json").read_text(encoding="utf-8"))
    got = hashlib.sha256(html).hexdigest()
    expected = manifest["sha256"]
    if got != expected:
        raise SystemExit(f"Source SHA mismatch: expected {expected}, got {got}")
    if len(html) != manifest["bytes"]:
        raise SystemExit(f"Source byte-size mismatch: expected {manifest['bytes']}, got {len(html)}")

    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_bytes(html)
    (out / "README.md").write_text((ROOT / "SPACE_README.md").read_text(encoding="utf-8"), encoding="utf-8")
    (out / "SOURCE.json").write_text(json.dumps({
        "schema": "swrlz-forge-source-v1",
        "sourceSha256": got,
        "sourceBytes": len(html),
        "payloadParts": [p.name for p in parts],
        "projectPath": "projects/swrlz-forge-moba",
    }, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(out), "sha256": got, "bytes": len(html), "parts": len(parts)}))

if __name__ == "__main__":
    main()
