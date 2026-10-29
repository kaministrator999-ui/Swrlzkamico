"""Measure the exact 159-patch §E candidate without weakening source integrity."""
from pathlib import Path
import hashlib,base64,gzip,json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from build_space import load_patch
m=json.loads((ROOT/'source-manifest.json').read_text())
assert m['name']=='§wyrl§ Engine v11.127'
assert len(m['patches'])==159
assert m['patches'][-1]=='patches/v11_127_clover_sheep_editor_boot.py'
data=gzip.decompress(base64.b64decode(''.join((ROOT/p).read_text().strip() for p in m['chunks'])))
assert len(data)==m['baseBytes'] and hashlib.sha256(data).hexdigest()==m['baseSha256']
html=data.decode('utf8')
for item in m['patches']:html=load_patch(ROOT/item)(html)
raw=html.encode('utf8')
Path('/tmp/se-v11127-full.html').write_bytes(raw)
Path('/tmp/se-v11127-full.mjs').write_text(html.split('<script type="module">',1)[1].rsplit('</script>',1)[0],encoding='utf8')
print('SE_V11127_FULL_BYTES',len(raw),flush=True)
print('SE_V11127_FULL_SHA256',hashlib.sha256(raw).hexdigest(),flush=True)
