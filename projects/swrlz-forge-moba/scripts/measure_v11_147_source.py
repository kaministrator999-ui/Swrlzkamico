#!/usr/bin/env python3
"""§E v11.147 reconstruction-based HTML seal and scoped LAN regressions."""
import base64,gzip,hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from build_space import load_patch
m=json.loads((ROOT/"source-manifest.json").read_text(encoding="utf8"))
assert m["name"]=="§wyrl§ Engine v11.147"
assert len(m["patches"])==179
assert m["patches"][-1]=="patches/v11_147_fullscreen_menu_viewport.py"
base="".join((ROOT/x).read_text(encoding="utf8").strip() for x in m["chunks"])
html=gzip.decompress(base64.b64decode(base)).decode("utf8")
for rel in m["patches"]:
 html=load_patch(ROOT/rel)(html)
raw=html.encode("utf8")
digest=hashlib.sha256(raw).hexdigest()
print("SE147_EXACT_BYTES",len(raw),flush=True)
print("SE147_EXACT_SHA256",digest,flush=True)
if len(raw)!=m["finalBytes"] or digest!=m["finalSha256"]:
 print("SE147_NEEDS_MANIFEST_SEAL",flush=True)
 sys.exit(0)
print("SE147_SOURCE_SEAL_MATCH",flush=True)
subprocess.run(["python",str(ROOT/"scripts/verify_v11_147_release.py"),"--output","dist/swrlz-forge-moba"],check=True)
subprocess.run(["node","--check","dist/swrlz-forge-moba-module.mjs"],check=True)
for test in ["sheep_lan_browser_v11_146.mjs", "runtime_fullscreen_menu_v11_147.mjs",
 "sheep_level_menu_runtime_v11_141.mjs",
 "editor_menu_stop_gait_v11_142.mjs","play_scene_build_ghost_v11_145.mjs"]:
 subprocess.run(["node",str(ROOT/"tests"/test)],check=True)
subprocess.run(["python",str(ROOT/"tests/lan_bridge_v11_146_test.py")],check=True)
print("SE147_PACKAGE_MENU_AND_REAL_LAN_HTTP_REGRESSIONS_PASS",flush=True)
