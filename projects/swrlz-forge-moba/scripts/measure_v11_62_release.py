#!/usr/bin/env python3
"""Independent source measurement for v11.62 (never trusts/stamps a final seal)."""
import argparse, base64, gzip, hashlib, json, sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))
from build_space import load_patch

ap = argparse.ArgumentParser()
ap.add_argument('--output', help='Optional directory for raw measured HTML/module')
args = ap.parse_args()
manifest = json.loads((root / 'source-manifest.json').read_text())
patches = list(manifest['patches'])
new_patch = 'patches/v11_62_mobile_adaptive.py'
if new_patch not in patches:
    assert len(patches) == 93 and patches[-1] == 'patches/v11_61_context_workbench.py'
    patches.append(new_patch)
else:
    assert len(patches) == 94 and patches[-1] == new_patch
raw = gzip.decompress(base64.b64decode(''.join((root / part).read_text().strip() for part in manifest['chunks'])))
assert len(raw) == manifest['baseBytes']
assert hashlib.sha256(raw).hexdigest() == manifest['baseSha256']
html = raw.decode('utf-8')
for patch in patches[:-1]:
    html = load_patch(root / patch)(html)
base = html.encode('utf-8')
assert len(base) == 2958383
assert hashlib.sha256(base).hexdigest() == 'cd33b05e3e27304fe9d3e753e488d46fcb844841fd06e19b8058a81516e7d01e'
original = html.split('const MODEL_ATELIER_CANONICAL_PROJECT=', 1)[1]
original, _ = json.JSONDecoder().raw_decode(original)
html = load_patch(root / new_patch)(html)
current = html.split('const MODEL_ATELIER_CANONICAL_PROJECT=', 1)[1]
current, _ = json.JSONDecoder().raw_decode(current)
assert original == current, 'Canonical project changed'
assert html.count('SWYRL_ENGINE_DEPLOY_MARKER: V11_62_MOBILE_ADAPTIVE_TOOL_SHEET') == 1
payload = html.encode('utf-8')
sha = hashlib.sha256(payload).hexdigest()
print('SWRLZ_V1162_INDEPENDENT_MEASURE', json.dumps({
    'name':'§wyrl§ Engine v11.62', 'patches':len(patches),
    'finalBytes':len(payload), 'finalSha256':sha,
    'oldSha256':hashlib.sha256(base).hexdigest(),
    'preservedCanonicalScene':True,
    'manifestSealMatch':(manifest.get('finalBytes') == len(payload) and manifest.get('finalSha256') == sha)
}, sort_keys=True), flush=True)
if args.output:
    out=Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    (out/'index.html').write_bytes(payload)
    module=html.split('<script type="module">', 1)[1].rsplit('</script>',1)[0]
    (out/'module.mjs').write_text(module)
