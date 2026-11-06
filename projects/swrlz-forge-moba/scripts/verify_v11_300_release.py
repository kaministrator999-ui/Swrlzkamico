#!/usr/bin/env python3
"""§E v11.300 sealed release: real image-backed UV atlas, byte-accurate assets."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_300_VANGUARD_MESH_UV_COUPLED'
ATLAS_HASH='d34f6afc422cbfafe54dfbbd420752b12d37967654ea5c1443c031f3b6720b27'
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--output',required=True);ap.add_argument('--request',action='store_true')
    a=ap.parse_args()
    m=json.loads((ROOT/'source-manifest.json').read_text('utf8'))
    assert m['name']=='§wyrl§ Engine v11.300'
    assert m['finalArtifact']=='swyrl_engine_v11_300.html'
    assert len(m['patches'])==331
    assert m['patches'][-3:]==[
        'patches/v11_298_actual_reference_uv_atlas.py',
        'patches/v11_299_real_image_uv_alignment.py',
        'patches/v11_300_vanguard_mesh_uv_rebuild.py']
    assert len(m['finalSha256'])==64 and m['finalBytes']>0
    out=Path(a.output).resolve()
    subprocess.run([sys.executable,str(ROOT/'build_space.py'),'--output',str(out)],check=True)
    raw=(out/'index.html').read_bytes()
    assert raw==(out/'modeler.html').read_bytes()
    assert hashlib.sha256(raw).hexdigest()==m['finalSha256'] and len(raw)==m['finalBytes']
    s=raw.decode('utf8')
    for token in (MARKER,'function se297MakePBR(tile){',
        'const se298AtlasDataURL="data:image/jpeg;base64,',
        'function se299ExtractImage(image,family){',
        'function se300BuildCharacter(scene){',
        'function se300DrawArtwork(img,name,canvas){',
        'function se299Material(family){',
        "window.SWYRL_ENGINE_HOODED_VANGUARD=Object.freeze({",
        'se298AtlasMetadata',ATLAS_HASH,'se298GetActualImageTexture',
        "window.SWRLZ_FORGE_BUILD={version:'v11.300'",
        '<strong>Hooded Vanguard · Geometry + UV Rebuild</strong>',
        "se291HeroScene=function(){",
        "se291HeroMaterial=function(part){",
        "function seChatAtelierApply(op)",
        'SE295_CHAT_LOFT_SURFACE_NORMALS_START'):
        assert token in s,token
    assert s.count("source.engine='§wyrl§ Engine · Maker v11.300';source.version=11.300;")==3
    assert '__SE298_ATLAS_DATA_URL__' not in s
    # Test real source image bytes and the saved native UV/material dispatch.
    subprocess.run(['node','--check',str(ROOT/'runtime/hooded_vanguard_mesh_uv_v11_300.js')],check=True)
    subprocess.run(['node',str(ROOT/'tests/hooded_vanguard_mesh_uv_v11_300.cjs')],check=True)
    subprocess.run([sys.executable,str(ROOT/'scripts/check_inline_js_syntax_v11_266.py'),str(out/'index.html')],check=True)
    receipt=json.loads((out/'SOURCE.json').read_text('utf8'))
    assert receipt['sourceVersion']==m['name'] and receipt['finalSha256']==m['finalSha256']
    assert receipt['finalBytes']==m['finalBytes'] and receipt['patches']==m['patches']
    assert len(receipt['assets'])==71
    for rel,meta in receipt['assets'].items():
        data=(out/rel).read_bytes()
        assert hashlib.sha256(data).hexdigest()==meta['sha256'] and len(data)==meta['bytes']
    if a.request:
        request=json.loads((ROOT/'DEPLOY_REQUEST.json').read_text('utf8'))
        assert request['releaseVersion']=='v11.300'
        assert request['deployMarker']==MARKER
        assert request['sourceIntegritySha256']==m['finalSha256']
        assert len(request['sourceCommit'])==40
    print(json.dumps({'status':'REAL_CHARACTER_GEOMETRY_AND_UV_SEALED','version':'v11.300',
         'patches':331,'htmlBytes':len(raw),'sha256':m['finalSha256'],
         'sourceImageSha256':ATLAS_HASH,'assets':len(receipt['assets']),
         'ownerVisualAcceptance':False},indent=2))
if __name__=='__main__':main()
