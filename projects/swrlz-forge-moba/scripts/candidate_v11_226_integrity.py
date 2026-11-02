#!/usr/bin/env python3
"""Narrow v11.226 candidate build: compute hash and validate only changed files.

Uses all canonical manifest patches verbatim, confirms the v11.225 artifact
before applying this one candidate. Does not rewrite the source manifest.
"""
import base64
import gzip
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from build_space import load_patch

def sha(value):
    return hashlib.sha256(value).hexdigest()

manifest=json.loads((ROOT/"source-manifest.json").read_text("utf-8"))
encoded="".join((ROOT/p).read_text("utf-8").strip() for p in manifest["chunks"])
base=gzip.decompress(base64.b64decode(encoded))
assert len(base)==manifest["baseBytes"] and sha(base)==manifest["baseSha256"],"Base payload drift"
html=base.decode("utf-8")
for p in manifest["patches"]:
    html=load_patch(ROOT/p)(html)
before=html.encode("utf-8")
assert len(before)==manifest["finalBytes"] and sha(before)==manifest["finalSha256"],"Existing governed v11.225 source changed"
candidate=load_patch(ROOT/"patches/v11_226_unified_popup_browser.py")(html)
out=candidate.encode("utf-8")
for keyword in ["V11_226_UNIFIED_POPUP_BROWSER","se226Browser","§wyrl§ Engine · Maker v11.226",
                "SWYRL_ENGINE_BROWSER"]:
    assert keyword in candidate,keyword+" missing"
assert candidate.count("id='se226Browser'")==0 # DOM built by script; no duplicate static mount
report={"version":"§wyrl§ Engine v11.226","baseVersion":manifest["name"],
        "patches":len(manifest["patches"])+1,
        "finalBytes":len(out),"finalSha256":sha(out),
        "basePreviousSha256":manifest["finalSha256"]}
print(json.dumps(report,ensure_ascii=False,indent=2))
