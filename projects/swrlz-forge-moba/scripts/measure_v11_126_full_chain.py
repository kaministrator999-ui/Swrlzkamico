"""Measure full 158-patch rebuild BEFORE committing production source seal."""
from pathlib import Path
import base64,gzip,hashlib,json,sys
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root))
from build_space import load_patch
manifest=json.loads((root/'source-manifest.json').read_text(encoding='utf8'))
assert manifest['name']=='§wyrl§ Engine v11.126'
assert manifest['patches'][-1]=='patches/v11_126_centered_build_permanent_routes_skills.py'
assert len(manifest['patches'])==158
compressed=''.join((root/name).read_text(encoding='utf8').strip() for name in manifest['chunks'])
raw=gzip.decompress(base64.b64decode(compressed))
assert len(raw)==manifest['baseBytes']
assert hashlib.sha256(raw).hexdigest()==manifest['baseSha256']
html=raw.decode('utf8')
for p in manifest['patches']:
 html=load_patch(root/p)(html)
out=Path('/tmp/se-v11126-full.html')
out.write_bytes(html.encode('utf8'))
a=html.index('<script type="module">')+len('<script type="module">')
b=html.rindex('</script>',a)
Path('/tmp/se-v11126-full.mjs').write_text(html[a:b],encoding='utf8')
print('SE_V11126_FULL_CHAIN_BYTES',len(html.encode('utf8')),flush=True)
print('SE_V11126_FULL_CHAIN_SHA256',hashlib.sha256(html.encode('utf8')).hexdigest(),flush=True)
