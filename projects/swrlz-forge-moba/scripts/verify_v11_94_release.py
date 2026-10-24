#!/usr/bin/env python3
"""Verify the covered knee skirt, softer portrait and immutable source lineage."""
import argparse
import gzip
import hashlib
import json
import math
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--output', required=True)
args = parser.parse_args()
out = Path(args.output).resolve()
manifest = json.loads((ROOT / 'source-manifest.json').read_text())
baseline = json.loads((ROOT / 'tests/knee_skirt_baseline_v11_93.json').read_text())
assert manifest['name'] == '§wyrl§ Engine v11.94'
assert manifest['finalArtifact'] == 'swyrl_engine_v11_94.html'
assert len(manifest['patches']) == 126
assert manifest['patches'] == baseline['patches'] + ['patches/v11_94_knee_skirt_soft_portrait.py']
assert len(baseline['sources']) == 309 and len(baseline['assets']) == 66
for path, digest in baseline['sources'].items():
    assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest, path
subprocess.run(['python', str(ROOT / 'build_space.py'), '--output', str(out)],
               check=True, stdout=subprocess.DEVNULL)
raw = (out / 'index.html').read_bytes()
html = raw.decode()
receipt = json.loads((out / 'SOURCE.json').read_text())
assert len(raw) == manifest['finalBytes'] == receipt['finalBytes']
assert hashlib.sha256(raw).hexdigest() == manifest['finalSha256'] == receipt['finalSha256']
assert receipt['sourceVersion'] == manifest['name'] and receipt['patches'] == manifest['patches']
new_scene = 'scenes/model-atelier-knee-armor-v11-94.swyrl.json'
assert set(receipt['assets']) == set(baseline['assets']) | {new_scene}
assert len(receipt['assets']) == 67
for path, meta in receipt['assets'].items():
    data = (out / path).read_bytes()
    assert len(data) == meta['bytes'] and hashlib.sha256(data).hexdigest() == meta['sha256'], path
    if path in baseline['assets']:
        assert meta == baseline['assets'][path], path
for token in [
    'SWYRL_ENGINE_DEPLOY_MARKER: V11_94_KNEE_SKIRT_SOFT_PORTRAIT',
    "window.SWRLZ_FORGE_BUILD={version:'v11.94'",
    '<title>§wyrl§ Engine · Maker v11.94</title>',
    'function atelierPortraitV1194(', 'function atelierKneeSkirtV1194(',
    new_scene, 'data-project-template="festival-girl-saved"',
]:
    assert token in html, token
chunks = sorted((ROOT / 'payload/festival-girl').glob('knee-v11-94.swyrl.json.gz.part*'))
scene_bytes = (out / new_scene).read_bytes()
assert chunks and gzip.decompress(b''.join(p.read_bytes() for p in chunks)) == scene_bytes
scene = json.loads(scene_bytes)
previous = json.loads((out / 'scenes/model-atelier-smooth-girl-v11-93.swyrl.json').read_bytes())
model, old_model = scene['project']['modelAtelier'], previous['project']['modelAtelier']
assert scene['engine'] == '§wyrl§ Engine · Maker v11.94'
assert model['appearanceRevision'] == 'v11.94'
assert scene['project']['canonicalId'] == previous['project']['canonicalId'] == 'organic-anime-girl'
parts = {p['id']: p for p in model['parts']}
old_parts = {p['id']: p for p in old_model['parts']}
assert set(parts) == set(old_parts) and len(parts) == len(model['parts']) == 327
assert model['assemblies'] == old_model['assemblies']
assert model['meshGroups'] == old_model['meshGroups']
companions = [p for p in old_model['parts'] if p['group'] != 'Character']
assert len(companions) == 117
for p in companions:
    assert parts[p['id']] == p, p['id']
for key in ['hair-grip--1', 'hair-grip-1', 'hair-bun--1', 'hair-bun-1', 'festival-shorts']:
    assert parts[key] == old_parts[key], key
triangles = 0
changed = []
for key, p in parts.items():
    data, old = p['topologyMesh'], old_parts[key]['topologyMesh']
    vertices = len(data['positions']) // 3
    assert data['indices'] == old['indices'] and data['uvs'] == old['uvs'], key
    assert len(data['positions']) == len(old['positions']) and len(data['uvs']) == vertices * 2, key
    assert all(math.isfinite(v) and abs(v) < 100 for v in data['positions']), key
    assert all(type(v) is int and 0 <= v < vertices for v in data['indices']), key
    assert all(len(p[k]) == 3 and all(math.isfinite(v) for v in p[k])
               for k in ['position', 'rotation', 'scale']), key
    assert all(p[k] == old_parts[key][k] for k in ['position', 'rotation', 'scale']), key
    triangles += len(data['indices']) // 3
    if p != old_parts[key]:
        changed.append(key)
body, old_body = parts['girl-organic-body']['topologyMesh']['positions'], old_parts['girl-organic-body']['topologyMesh']['positions']
changed_head = 0
for i in range(0, len(body), 3):
    before, after = old_body[i:i+3], body[i:i+3]
    if before[1] <= 3.70:
        assert before == after, 'Body outside head scope changed'
    if before != after:
        changed_head += 1
        assert math.dist(before, after) < .06
assert changed_head > 1000
skirt = model['kneeSkirtRefinement']
assert skirt['revision'] == 'v11.94' and skirt['kneeY'] == 1.52
assert len(skirt['panelIds']) == 9
allowed_changes = set(skirt['affectedParts']) | set(model['portraitRefinementV1194']['changedParts'])
assert set(changed) <= allowed_changes, set(changed) - allowed_changes
assert model['festivalDress']['revision'] == 'knee-armor-v11.94'
minimum_y = min(min(parts[key]['topologyMesh']['positions'][1::3]) for key in skirt['affectedParts'])
assert minimum_y >= skirt['kneeY'] - .000001, minimum_y
for key in skirt['panelIds']:
    positions = parts[key]['topologyMesh']['positions']
    assert 1.52 <= min(positions[1::3]) < 1.85, key
    assert max(positions[1::3]) > 2.7, key
assert model['coverageRefinement'] == old_model['coverageRefinement']
assert model['legRefinement'] == old_model['legRefinement']
Path(str(out) + '-module.mjs').write_text(html.split('<script type="module">', 1)[1].rsplit('</script>', 1)[0])
print('SWRLZ_V1194_RELEASE_VERIFIED', len(raw), manifest['finalSha256'],
      '126_PATCHES_67_ASSETS', '309_PREVIOUS_SOURCES_66_ASSETS_EXACT',
      'COMPANIONS_ASSEMBLIES_SHORTS_LEGS_EXACT', 'PARTS', len(parts), 'TRIANGLES', triangles,
      'CHANGED_HEAD_VERTICES', changed_head, 'SKIRT_MINIMUM_Y', minimum_y, 'CHANGED_PARTS', changed)
