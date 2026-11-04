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
for p in m["patches"]:html=load_patch(root/p)(html)
a=html.index("const SE223_SCHEMA=")
b=html.index("function se223Mutate(",a)
vfx=html[a:b]
for term in ["const SE223_PRESETS=","function se223Frame(dt,t)","vortexCyan:"]:
 assert term in vfx,term
out=Path(sys.argv[1]);out.write_text(vfx,encoding="utf8")
print("Native VFX extracted:",len(vfx),"characters")
