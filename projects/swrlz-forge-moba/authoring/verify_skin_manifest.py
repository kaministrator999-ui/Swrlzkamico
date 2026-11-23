#!/usr/bin/env python3
"""Verify generated UV texture assets using the bake's own manifest paths."""
import base64,hashlib,json,struct,sys
from pathlib import Path

root=Path(__file__).resolve().parents[1]
manifest=Path(sys.argv[1]).resolve()
assert manifest.is_relative_to(root) and manifest.is_file()
proof=json.loads(manifest.read_text('utf8'))
assets=proof['assets']
assert proof['triangles']==13932 and proof['uvVertices']==8902
assert not any(proof[k] for k in ('uvCoordinatesModified','geometryModified','oldMaterialOverwritten','triangulationPaintedIntoTexture'))
assert assets['validation']==str(manifest.relative_to(root))
for key,res in (('4kMaterial',4096),('2kMaterial',2048),('nativeMaterial',1024)):
    path=(root/assets[key]).resolve()
    assert path.is_relative_to(root/'assets/models') and path.is_file(),path
    data=path.read_bytes()
    assert data[:8]==b'\x89PNG\r\n\x1a\n'
    assert struct.unpack('>II',data[16:24])==(res,res)
    assert proof[key]['size']==[res,res]
    assert hashlib.sha256(data).hexdigest()==proof[key]['sha256']
    assert len(data)<10_000_000
native=(root/assets['nativeMaterial']).read_bytes()
assert len(base64.b64encode(native))+22<=360000
view=(root/assets['renderProof']).resolve()
assert view.is_relative_to(root/'docs/qa') and view.is_file()
assert struct.unpack('>II',view.read_bytes()[16:24])==(1560,606)
scene=(root/'scenes/model-atelier-futuristic-humanoid-v11-546.swyrl.json').read_bytes()
assert hashlib.sha256(scene).hexdigest()==proof['sourceSceneSha256']
print('SKIN_ASSET_MANIFEST_INTEGRITY_PASS',json.dumps(assets))
