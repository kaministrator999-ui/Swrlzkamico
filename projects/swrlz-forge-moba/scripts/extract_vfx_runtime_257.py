#!/usr/bin/env python3
"""Extract effective VFX core from current sealed patch source for targeted Node tests."""
import base64,gzip,json,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root))
from build_space import load_patch
m=json.loads((root/"source-manifest.json").read_text("utf8"))
raw=gzip.decompress(base64.b64decode("".join((root/p).read_text("utf8").strip() for p in m["chunks"])))
html=raw.decode("utf8")
patches=m["patches"]
if patches[-1]!="patches/v11_257_nebula_tdz_unfreeze.py":
 patches=patches+["patches/v11_257_nebula_tdz_unfreeze.py"]
for p in patches:html=load_patch(root/p)(html)
a=html.index("const SE223_SCHEMA=")
b=html.index("function se223Mutate(",a)
vfx=html[a:b]
for term in ["const SE223_PRESETS=","function se223Frame(dt,t)","vortexCyan:"]:
 assert term in vfx,term
out=Path(sys.argv[1]);out.write_text(vfx,encoding="utf8")
print("Native VFX extracted:",len(vfx),"characters")

# Use exactly the corrected embedded nebula script from the patched HTML,
# not the historical v11.251 source file which deliberately remains intact.
tag="// §E v11.251 · concept-faithful upright galactic arms."
a=html.index(tag)
end=html.index("window.SWYRL_ENGINE_NEBULA_251=Object.freeze",a)
b=html.index("\n})();",end)+len("\n})();")
script=html[a:b]
assert "const nextPoint=location(" in script
assert "const b=location(Math.min(1,u+.001)" not in script
Path(sys.argv[2]).write_text(script,encoding="utf8")
print("Extracted corrected galaxy script:",len(script),"characters")
