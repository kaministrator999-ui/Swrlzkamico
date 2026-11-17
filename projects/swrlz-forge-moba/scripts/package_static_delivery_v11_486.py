#!/usr/bin/env python3
"""Produce small browser-renderable §E static files from sealed v11.486 HTML.

The exact SHA-sealed 463-patch source is unchanged. A delivery-only transform
moves its 9.8 MB synchronous-order-preserving ES module into one external file,
keeping *each* served file under 10,000,000 bytes (also under 10 MiB). This
avoids large-file/LFS download handling on static hosting.
"""
import argparse
import hashlib
import json
from pathlib import Path

SOURCE_START = b'<script type="module">\n(async()=>{\nconst app=document.getElementById'
SOURCE_CLOSE = b'\n</script>\n</body>\n</html>'
MODULE = "swrlz-engine-v11.486.js"
TAG = ('<script type="module" src="./'+MODULE+'"></script>').encode("ascii")
MAX_FILE = 10_000_000


def digest(data):
    return hashlib.sha256(data).hexdigest()


def split_html(original):
    if original.count(SOURCE_START) != 1:
        raise ValueError("Cannot locate the one root §E module entry")
    start = original.index(SOURCE_START)
    end = original.rfind(SOURCE_CLOSE)
    if end <= start:
        raise ValueError("Root module closing tag is missing")
    prefix = b'<script type="module">'
    assert original[start:start+len(prefix)] == prefix
    module = original[start+len(prefix):end]
    if not module.startswith(b"\n(async()=>{") or not module.rstrip().endswith(b"})();"):
        raise ValueError("Module does not match the sealed engine entry")
    if b'import.meta' in module:
        raise ValueError("Refuse to relocate module with import.meta-relative paths")
    served = original[:start] + TAG + original[end+len(b'\n</script>'):]
    restored = served.replace(TAG, prefix+module+b'\n</script>', 1)
    if restored != original:
        raise ValueError("Static delivery fails lossless round-trip")
    if '<title>§wyrl§ Engine · Maker v11.486</title>'.encode('utf8') not in served:
        raise ValueError("Static document lost its verified version")
    for title, raw in (("HTML", served), ("JavaScript module", module)):
        if len(raw) >= MAX_FILE:
            raise ValueError(f"{title} remains over 10MB: {len(raw)} bytes")
    return served, module


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    root = Path(args.output).resolve()
    receipt_path = root/"SOURCE.json"
    receipt = json.loads(receipt_path.read_text("utf8"))
    page = (root/"index.html").read_bytes()
    other = (root/"modeler.html").read_bytes()
    if page != other:
        raise ValueError("Index/modeler must share the same sealed source")
    if len(page) != receipt["finalBytes"] or digest(page) != receipt["finalSha256"]:
        raise ValueError("Do not transform a source whose original SHA receipt fails")
    served, module = split_html(page)
    (root/"index.html").write_bytes(served)
    (root/"modeler.html").write_bytes(served)
    (root/MODULE).write_bytes(module)
    receipt["staticDelivery"] = {
        "mode": "external-es-module",
        "verifiedSourceSha256": receipt["finalSha256"],
        "module": MODULE,
        "moduleBytes": len(module),
        "moduleSha256": digest(module),
        "indexBytes": len(served),
        "indexSha256": digest(served),
        "modelerBytes": len(served),
        "modelerSha256": digest(served),
        "fileLimitBytes": MAX_FILE,
    }
    receipt_path.write_text(json.dumps(receipt, indent=2)+"\n", encoding="utf8")
    assert (root/"index.html").read_bytes() == (root/"modeler.html").read_bytes()
    assert len((root/MODULE).read_bytes()) < MAX_FILE
    print("SE486_STATIC_DELIVERY_PASS", json.dumps(receipt["staticDelivery"], sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
