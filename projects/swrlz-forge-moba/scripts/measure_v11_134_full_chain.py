"""Measure the complete §E v11.134 artifact from all 166 ordered patches."""
from pathlib import Path
import base64,gzip,json,hashlib,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from build_space import load_patch
m=json.loads((ROOT/'source-manifest.json').read_text())
assert m['name']=='§wyrl§ Engine v11.134' and len(m['patches'])==166
assert m['patches'][-1]=='patches/v11_134_rapid_cancel_sheep_seed_skills_house_swap.py'
raw=gzip.decompress(base64.b64decode(''.join((ROOT/p).read_text().strip() for p in m['chunks'])))
assert len(raw)==m['baseBytes'] and hashlib.sha256(raw).hexdigest()==m['baseSha256']
html=raw.decode('utf8')
for rel in m['patches']:html=load_patch(ROOT/rel)(html)
b=html.encode('utf8')
Path('/tmp/se134-full.html').write_bytes(b)
Path('/tmp/se134-full.mjs').write_text(html.split('<script type="module">',1)[1].rsplit('</script>',1)[0],encoding='utf8')
print('SE134_FULL_BYTES',len(b),flush=True)
print('SE134_FULL_SHA256',hashlib.sha256(b).hexdigest(),flush=True)
