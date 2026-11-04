#!/usr/bin/env python3
"""Verify final sealed §E v11.253 startup hotfix after adding release receipts."""
import base64,gzip,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from build_space import load_patch
m=json.loads((ROOT/"source-manifest.json").read_text("utf8"))
patch="patches/v11_253_startup_unfreeze.py"
patches=m["patches"] if m["patches"][-1]==patch else m["patches"]+[patch]
assert len(patches)==284 and patches[-1]==patch
raw=gzip.decompress(base64.b64decode("".join((ROOT/p).read_text("utf8").strip() for p in m["chunks"])))
assert hashlib.sha256(raw).hexdigest()==m["baseSha256"]
html=raw.decode("utf8")
for name in patches:html=load_patch(ROOT/name)(html)
assert html.count("renderer.setAnimationLoop(tick);")==1
assert "V11_253_STARTUP_UNFREEZE" in html
assert "const mounted=records.some(record=>" in html
assert "if(mounted&&(!q('#se251ModelLibrary')" in html
assert "if((!modelOpen&&!particleOpen&&!state.particle)||q('#seReleaseNotesDialog')?.open)" in html
assert "window.SWYRL_ENGINE_STRESS_TEST_252" in html
assert "seReleaseNotesClose" in html
assert "new MutationObserver(()=>{\n if(!q('#se251ModelLibrary')" not in html
data=html.encode("utf8")
print(json.dumps({"version":"v11.253","patches":len(patches),"finalBytes":len(data),
"finalSha256":hashlib.sha256(data).hexdigest(),"singleRenderer":True},indent=2))
