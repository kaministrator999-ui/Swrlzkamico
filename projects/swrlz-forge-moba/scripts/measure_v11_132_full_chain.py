"""Exact full 164-patch assembled §E source for release-seal measurement."""
from pathlib import Path
import json,base64,gzip,hashlib,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from build_space import load_patch
m=json.loads((ROOT/'source-manifest.json').read_text())
assert m['name']=='§wyrl§ Engine v11.132' and len(m['patches'])==164
assert m['patches'][-1]=='patches/v11_132_ghost_rapid_routes_wireframe.py'
raw=gzip.decompress(base64.b64decode(''.join((ROOT/name).read_text().strip() for name in m['chunks'])))
assert len(raw)==m['baseBytes'] and hashlib.sha256(raw).hexdigest()==m['baseSha256']
html=raw.decode('utf8')
for rel in m['patches']:html=load_patch(ROOT/rel)(html)
b=html.encode('utf8')
Path('/tmp/se132-full.html').write_bytes(b)
Path('/tmp/se132-full.mjs').write_text(html.split('<script type="module">',1)[1].rsplit('</script>',1)[0])
print('SE132_FINAL_BYTES',len(b),flush=True)
print('SE132_FINAL_SHA256',hashlib.sha256(b).hexdigest(),flush=True)
