"""Build the v11.125 additive candidate from the exact sealed v11.124 HTML."""
from pathlib import Path
import hashlib,runpy
root=Path(__file__).resolve().parents[1]
base=Path('/tmp/se-v11124-release/index.html').read_text(encoding='utf8')
key='Leave room for the units standing here.'
i=base.find(key)
print('SE_NATIVE_BUILD_OCCUPANT_CONTEXT',repr(base[i-900:i+150]),flush=True)
apply=runpy.run_path(str(root/'patches/v11_125_gap_builder_exit.py'))['apply']
html=apply(base)
raw=html.encode('utf8')
Path('/tmp/se-v11125.html').write_bytes(raw)
Path('/tmp/se-v11125.mjs').write_text(html.split('<script type="module">',1)[1].rsplit('</script>',1)[0],encoding='utf8')
print('SE_V11125_CANDIDATE_BYTES',len(raw))
print('SE_V11125_CANDIDATE_SHA256',hashlib.sha256(raw).hexdigest())
