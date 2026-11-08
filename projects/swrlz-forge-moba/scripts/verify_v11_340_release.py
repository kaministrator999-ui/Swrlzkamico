#!/usr/bin/env python3
"""Verify the exact native Model Studio XR release and bounded regressions."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
MARKER = 'SWYRL_ENGINE_DEPLOY_MARKER: V11_340_IMMERSIVE_MODEL_STUDIO'
THREE_URL = 'https://cdn.jsdelivr.net/npm/three@0.169.0/+esm'
THREE_BYTES = 684391
THREE_SHA = '260fdf7db2ecda0e726a82e37c829cdeb974015c9a4304ea9c51177b2c8b2c1a'


def run(*args):
    subprocess.run([str(a) for a in args], check=True)


def main():
    cli = argparse.ArgumentParser()
    cli.add_argument('--output', required=True)
    cli.add_argument('--request', action='store_true')
    cli.add_argument('--three-module', help='Optional exact pinned Three ESM for offline checks')
    args = cli.parse_args()
    manifest = json.loads((ROOT / 'source-manifest.json').read_text('utf8'))
    assert manifest['name'] == '§wyrl§ Engine v11.340'
    assert manifest['finalArtifact'] == 'swyrl_engine_v11_340.html'
    assert len(manifest['patches']) == 351
    assert manifest['patches'][-2:] == ['patches/v11_337_cliff_organic_geodes.py', 'patches/v11_340_immersive_model_studio.py']
    out = Path(args.output).resolve()
    run(sys.executable, ROOT / 'build_space.py', '--output', out)
    raw = (out / 'index.html').read_bytes()
    assert raw == (out / 'modeler.html').read_bytes()
    assert len(raw) == manifest['finalBytes']
    assert hashlib.sha256(raw).hexdigest() == manifest['finalSha256']
    html = raw.decode('utf8')
    for token in [MARKER, 'SE340_MODEL_VR_BRIDGE_START', 'SE340_MODEL_VR_WORKSPACE_START',
                  'SE340_MODEL_VR_ENTRY_START', 'function se340CreateModelVRUI(',
                  'xrBridge:se340ModelBridge', 'if(se340ModelXRActive()){se340ModelXRFrame(se340Time,se340Frame);return;}',
                  'SE330_MATERIAL_STUDIO_LAYOUT_START', 'SE321_LOS_CORE_START',
                  'function se337HandField(math)', 'function se336UVLayout(mesh, canvas)',
                  '<title>§wyrl§ Engine · Maker v11.340</title>',
                  "window.SWRLZ_FORGE_BUILD={version:'v11.340'"]:
        assert token in html, token
    assert html.count('renderer.setAnimationLoop(tick);') == 1
    assert html.count("source.engine='§wyrl§ Engine · Maker v11.340';source.version=11.340;") == 3
    run(sys.executable, ROOT / 'scripts/check_inline_js_syntax_v11_266.py', out / 'index.html')
    for name in ['model_vr_bridge_v11_340.js', 'model_vr_workspace_v11_340.js',
                 'model_studio_vr_ui_v11_340.js', 'model_vr_entry_v11_340.js']:
        path = ROOT / 'runtime' / name
        run('node', '--check', path)
        assert 'requestAnimationFrame(' not in path.read_text() and 'setAnimationLoop(' not in path.read_text()
    with tempfile.TemporaryDirectory(prefix='swrlz-vr340-three-') as temp:
        if args.three_module:
            module = Path(args.three_module).resolve()
            data = module.read_bytes()
        else:
            with urllib.request.urlopen(THREE_URL, timeout=30) as response:
                data = response.read(THREE_BYTES + 1)
            module = Path(temp) / 'three-0.169.0.mjs'
            module.write_bytes(data)
        assert len(data) == THREE_BYTES and hashlib.sha256(data).hexdigest() == THREE_SHA
        run('node', ROOT / 'tests/model_vr_v11_340.mjs', module)
    run('node', ROOT / 'tests/studio_project_routing_v11_320.cjs')
    run('node', ROOT / 'scripts/test_material_texture_v11_225.js')
    run('node', ROOT / 'tests/arcane_grip_ray_v11_308.cjs', out / 'index.html')
    run('node', ROOT / 'tests/arcane_native_ray_v11_309.cjs', out / 'index.html')
    run('node', ROOT / 'scripts/test_v11_337_cliff_organic_geodes.cjs')
    run('node', ROOT / 'scripts/test_v11_335_cliff_ulnar_contour.cjs')
    receipt = json.loads((out / 'SOURCE.json').read_text())
    for key, expected in [('sourceVersion', manifest['name']), ('patches', manifest['patches']),
                          ('finalBytes', manifest['finalBytes']), ('finalSha256', manifest['finalSha256'])]:
        assert receipt[key] == expected
    assert len(receipt['assets']) == 71
    for name, meta in receipt['assets'].items():
        data = (out / name).read_bytes()
        assert len(data) == meta['bytes'] and hashlib.sha256(data).hexdigest() == meta['sha256'], name
    assert len([p for p in out.rglob('*') if p.is_file()]) == 75
    if args.request:
        request = json.loads((ROOT / 'DEPLOY_REQUEST.json').read_text())
        assert request['releaseVersion'] == 'v11.340' and request['deployMarker'] == MARKER
        assert request['sourceIntegritySha256'] == manifest['finalSha256']
        assert len(request['sourceCommit']) == 40
    print(json.dumps({'status': 'SEALED_SOURCE_VERIFIED', 'version': 'v11.340', 'patches': 351,
                     'htmlBytes': len(raw), 'sha256': manifest['finalSha256'], 'assets': 71,
                     'physicalHeadsetAcceptance': False}, indent=2))


if __name__ == '__main__':
    main()
