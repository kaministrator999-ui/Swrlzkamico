#!/usr/bin/env python3
"""Independently measure the exact governed v11.59 patch chain.

Unlike build_space.py's authoritative release gate this script reports an
unsealed digest during candidate preparation, without substituting test data.
"""
import base64,gzip,hashlib,json,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root))
import build_space
m=json.loads((root/"source-manifest.json").read_text(encoding="utf-8"))
assert m["name"]=="§wyrl§ Engine v11.59"
assert len(m["patches"])==91 and m["patches"][-1]=="patches/v11_59_precision_model_atelier.py"
data=gzip.decompress(base64.b64decode("".join((root/p).read_text().strip() for p in m["chunks"])))
assert len(data)==m["baseBytes"] and hashlib.sha256(data).hexdigest()==m["baseSha256"]
html=data.decode("utf-8")
for patch in m["patches"]:
    html=build_space.load_patch(root/patch)(html)
raw=html.encode("utf-8")
assert html.count("SWYRL_ENGINE_DEPLOY_MARKER: V11_59_PRECISION_MODEL_ATELIER")==1
assert "<title>§wyrl§ Engine · Maker v11.59</title>" in html
print("V1159_GOVERNED_RELEASE_DIGEST",json.dumps({
 "finalSha256":hashlib.sha256(raw).hexdigest(),"finalBytes":len(raw),
 "previousSha256":m["finalSha256"],"previousBytes":m["finalBytes"],
 "manifestMatches":hashlib.sha256(raw).hexdigest()==m["finalSha256"] and len(raw)==m["finalBytes"],
 "patches":len(m["patches"])}))
