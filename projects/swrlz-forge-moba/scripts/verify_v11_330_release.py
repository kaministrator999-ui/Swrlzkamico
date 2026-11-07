#!/usr/bin/env python3
"""Strict package and scoped native checks for the Materials studio release."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
MARKER = 'SWYRL_ENGINE_DEPLOY_MARKER: V11_330_MATERIAL_STUDIO_LAYOUT'


def main():
    cli = argparse.ArgumentParser()
    cli.add_argument('--output', required=True)
    cli.add_argument('--request', action='store_true')
    args = cli.parse_args()
    manifest = json.loads((ROOT / 'source-manifest.json').read_text('utf8'))
    assert manifest['name'] == '§wyrl§ Engine v11.330'
    assert manifest['finalArtifact'] == 'swyrl_engine_v11_330.html'
    assert len(manifest['patches']) == 343
    assert manifest['patches'][-3:] == [
        'patches/v11_320_studio_navigation_layout.py',
        'patches/v11_321_sheep_sight_xr_crowd.py',
        'patches/v11_330_material_studio_layout.py',
    ]
    assert manifest['finalBytes'] > 0 and len(manifest['finalSha256']) == 64
    out = Path(args.output).resolve()
    subprocess.run([sys.executable, str(ROOT / 'build_space.py'), '--output', str(out)], check=True)
    raw = (out / 'index.html').read_bytes()
    assert raw == (out / 'modeler.html').read_bytes()
    assert len(raw) == manifest['finalBytes']
    assert hashlib.sha256(raw).hexdigest() == manifest['finalSha256']
    html = raw.decode('utf8')
    for token in [MARKER, 'SE330_MATERIAL_STUDIO_LAYOUT_START', 'SE330_MATERIAL_STUDIO_LAYOUT_END',
                  'SE320_PROJECT_STUDIO_ROUTING_START', 'SE320_EDITOR_LAYOUT_START',
                  'SE321_LOS_CORE_START', 'SE304_MODELER_DOCUMENT_VIEW_SYNC_START',
                  "window.SWRLZ_FORGE_BUILD={version:'v11.330'",
                  '<title>§wyrl§ Engine · Maker v11.330</title>']:
        assert token in html, token
    assert html.count('renderer.setAnimationLoop(tick);') == 1
    assert html.count('SE330_MATERIAL_STUDIO_LAYOUT_START') == 1
    assert html.count("source.engine='§wyrl§ Engine · Maker v11.330';source.version=11.330;") == 3
    subprocess.run([sys.executable, str(ROOT / 'scripts/check_inline_js_syntax_v11_266.py'), str(out / 'index.html')], check=True)
    subprocess.run(['node', '--check', str(ROOT / 'runtime/material_studio_layout_v11_330.js')], check=True)
    subprocess.run(['node', str(ROOT / 'scripts/test_material_texture_v11_225.js')], check=True)
    subprocess.run(['node', str(ROOT / 'tests/studio_project_routing_v11_320.cjs')], check=True)
    subprocess.run(['node', str(ROOT / 'tests/sheep_sight_xr_crowd_v11_321.cjs'), str(out / 'index.html')], check=True)
    receipt = json.loads((out / 'SOURCE.json').read_text('utf8'))
    assert receipt['sourceVersion'] == manifest['name']
    assert receipt['patches'] == manifest['patches']
    assert receipt['finalBytes'] == manifest['finalBytes']
    assert receipt['finalSha256'] == manifest['finalSha256']
    assert receipt['workspacePages'] == {'game': 'index.html', 'modeler': 'modeler.html'}
    assert len(receipt['assets']) == 71
    for name, meta in receipt['assets'].items():
        data = (out / name).read_bytes()
        assert len(data) == meta['bytes'] and hashlib.sha256(data).hexdigest() == meta['sha256'], name
    assert len([p for p in out.rglob('*') if p.is_file()]) == 75
    if args.request:
        request = json.loads((ROOT / 'DEPLOY_REQUEST.json').read_text('utf8'))
        assert request['releaseVersion'] == 'v11.330'
        assert request['deployMarker'] == MARKER
        assert request['sourceIntegritySha256'] == manifest['finalSha256']
        assert len(request['sourceCommit']) == 40
    print(json.dumps({'status': 'SEALED_SOURCE_VERIFIED', 'version': 'v11.330',
                     'patches': 343, 'htmlBytes': len(raw), 'sha256': manifest['finalSha256'],
                     'assets': 71, 'physicalDeviceAcceptance': False}, indent=2))


if __name__ == '__main__':
    main()
