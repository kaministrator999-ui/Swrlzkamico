"""Independent exact §E v11.133 165-patch generated HTML measurement."""
from pathlib import Path
import base64,gzip,json,hashlib,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from build_space import load_patch
m=json.loads((ROOT/'source-manifest.json').read_text())
assert m['name']=='§wyrl§ Engine v11.133' and len(m['patches'])==165
assert m['patches'][-1]=='patches/v11_133_rapid_tappable_sheep_ghost.py'
raw=gzip.decompress(base64.b64decode(''.join((ROOT/p).read_text().strip() for p in m['chunks'])))
assert len(raw)==m['baseBytes'] and hashlib.sha256(raw).hexdigest()==m['baseSha256']
html=raw.decode('utf8')
for p in m['patches']:html=load_patch(ROOT/p)(html)
b=html.encode('utf8')
Path('/tmp/se133-full.html').write_bytes(b)
Path('/tmp/se133-full.mjs').write_text(html.split('<script type="module">',1)[1].rsplit('</script>',1)[0])
print('SE133_FINAL_BYTES',len(b),flush=True)
print('SE133_FINAL_SHA256',hashlib.sha256(b).hexdigest(),flush=True)
