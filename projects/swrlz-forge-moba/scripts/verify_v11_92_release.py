#!/usr/bin/env python3
"""Verify the reference-refined native starter and immutable v11.91 lineage."""
import argparse
import collections
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
baseline = json.loads((ROOT / 'tests/festival_reference_baseline_v11_91.json').read_text())
assert manifest['name'] == '§wyrl§ Engine v11.92'
assert manifest['finalArtifact'] == 'swyrl_engine_v11_92.html'
assert len(manifest['patches']) == 124
assert manifest['patches'] == baseline['patches'] + ['patches/v11_92_festival_reference_refinement.py']
for path, digest in baseline['sources'].items():
    assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest, path
subprocess.run(['python', str(ROOT / 'build_space.py'), '--output', str(out)], check=True, stdout=subprocess.DEVNULL)
raw = (out / 'index.html').read_bytes()
html = raw.decode()
receipt = json.loads((out / 'SOURCE.json').read_text())
assert len(raw) == manifest['finalBytes'] == receipt['finalBytes']
assert hashlib.sha256(raw).hexdigest() == manifest['finalSha256'] == receipt['finalSha256']
assert receipt['sourceVersion'] == manifest['name']
assert receipt['patches'] == manifest['patches']
new_scene = 'scenes/model-atelier-reference-girl-v11-92.swyrl.json'
assert set(receipt['assets']) == set(baseline['assets']) | {new_scene}
assert len(receipt['assets']) == 65
for path, meta in receipt['assets'].items():
    data = (out / path).read_bytes()
    assert len(data) == meta['bytes'], path
    assert hashlib.sha256(data).hexdigest() == meta['sha256'], path
    if path in baseline['assets']:
        assert meta == baseline['assets'][path], path
for token in [
    'SWYRL_ENGINE_DEPLOY_MARKER: V11_92_FESTIVAL_REFERENCE',
    "window.SWRLZ_FORGE_BUILD={version:'v11.92'",
    '<title>§wyrl§ Engine · Maker v11.92</title>',
    'function atelierFestivalRefineFace(', 'function atelierFestivalRefineDress(',
    new_scene, 'data-project-template="festival-girl-saved"',
]:
    assert token in html, token
assert html.count('SWYRL_ENGINE_DEPLOY_MARKER: V11_92_FESTIVAL_REFERENCE') == 1
packed = sorted((ROOT / 'payload/festival-girl').glob('reference-v11-92.swyrl.json.gz.part*'))
assert packed, 'Missing v11.92 lossless scene payload'
scene_bytes = (out / new_scene).read_bytes()
assert gzip.decompress(b''.join(path.read_bytes() for path in packed)) == scene_bytes
scene = json.loads(scene_bytes)
previous = json.loads((out / 'scenes/model-atelier-organic-anime-girl-v11-91.swyrl.json').read_bytes())
assert scene['project']['canonicalId'] == previous['project']['canonicalId'] == 'organic-anime-girl'
assert scene['engine'] == '§wyrl§ Engine · Maker v11.92'
model, old_model = scene['project']['modelAtelier'], previous['project']['modelAtelier']
parts = {part['id']: part for part in model['parts']}
old_parts = {part['id']: part for part in old_model['parts']}
assert len(parts) == len(model['parts']), 'Duplicate native part IDs'
assert model['assemblies'] == old_model['assemblies'], 'Companion/motion assembly changed'
companions = [part for part in old_model['parts'] if part['group'] != 'Character']
assert companions, 'The previous starter must have companions'
for part in companions:
    assert parts[part['id']] == part, part['id']
triangles = 0
for part in parts.values():
    assert part['kind'] == 'topologyMesh', part['id']
    data = part['topologyMesh']
    vertices = len(data['positions']) // 3
    assert vertices and len(data['positions']) % 3 == 0, part['id']
    assert len(data['uvs']) == vertices * 2, part['id']
    assert len(data['indices']) and len(data['indices']) % 3 == 0, part['id']
    assert all(math.isfinite(value) and abs(value) < 100 for value in data['positions']), part['id']
    assert all(math.isfinite(value) for value in data['uvs']), part['id']
    assert all(isinstance(value, int) and 0 <= value < vertices for value in data['indices']), part['id']
    assert all(len(part[key]) == 3 and all(math.isfinite(v) for v in part[key]) for key in ['position', 'rotation', 'scale']), part['id']
    triangles += len(data['indices']) // 3
for group in model['meshGroups']:
    assert 1 < len(group['members']) <= 30, group['id']
    assert len(set(group['members'])) == len(group['members']), group['id']
    assert all(member in parts for member in group['members']), group['id']
body = parts['girl-organic-body']['topologyMesh']
old_body = old_parts['girl-organic-body']['topologyMesh']
assert body['indices'] == old_body['indices'], 'Connected skin topology changed'
assert len(body['positions']) == len(old_body['positions'])
assert body['positions'] != old_body['positions'], 'Requested facial sculpt did not change'
# Preserve the original body below the portrait and keep every old skin edge
# closed. The geometry itself is checked, independently of descriptive metadata.
for i in range(0, len(body['positions']), 3):
    if old_body['positions'][i + 1] < 3.58:
        assert body['positions'][i:i + 3] == old_body['positions'][i:i + 3]
vertex_count = len(body['positions']) // 3
edges = collections.Counter()
parent = list(range(vertex_count))
def find(i):
    while parent[i] != i:
        parent[i] = parent[parent[i]]
        i = parent[i]
    return i
for a, b, c in zip(body['indices'][::3], body['indices'][1::3], body['indices'][2::3]):
    for u, v in [(a, b), (b, c), (c, a)]:
        edges[min(u, v) * vertex_count + max(u, v)] += 1
        ru, rv = find(u), find(v)
        if ru != rv:
            parent[rv] = ru
assert set(edges.values()) == {2}, 'Skin has an open/non-manifold edge'
assert len({find(i) for i in range(vertex_count)}) == 1, 'Skin disconnected'
profile = model['referenceProfile']
assert profile['version'] == 'v11.92'
assert profile['face']['eyeCantDegrees'] == 8
for side in ['left', 'right']:
    for suffix in ['sclera', 'iris', 'brow', 'upper-lid', 'lower-lid']:
        part = parts[side + '-' + suffix]
        assert part['topologyMesh']['positions'] != old_parts[part['id']]['topologyMesh']['positions'], part['id']
    assert parts['girl-pupil-' + side]['topologyMesh']['positions'] != old_parts['girl-pupil-' + side]['topologyMesh']['positions']
assert 'girl-reference-cyan-tendril' in parts
assert 'girl-reference-coral-temple' in parts
ponytails=[part for key,part in parts.items() if key.startswith('girl-reference-ponytail-') and not key.endswith('-silk')]
assert len(ponytails)==10
assert max(max(part['topologyMesh']['positions'][1::3]) for part in ponytails)>4.8, 'Upward tied tuft silhouette missing'
assert all(key in parts for key in ['hair-bun--1','hair-bun-1']), 'Companion socket owners missing'
assert len([key for key in parts if key.startswith('girl-reference-fringe-')]) >= 12
assert not any(key.startswith('girl-fiber-') for key in parts), 'Old highlights left behind'

def world_min_y(part):
    a, b = math.cos(part['rotation'][0]), math.sin(part['rotation'][0])
    c, d = math.cos(part['rotation'][1]), math.sin(part['rotation'][1])
    e, f = math.cos(part['rotation'][2]), math.sin(part['rotation'][2])
    data = part['topologyMesh']['positions']
    scale = part['scale']
    return min((a*f+b*e*d)*data[i]*scale[0] + (a*e-b*f*d)*data[i+1]*scale[1] - b*c*data[i+2]*scale[2] + part['position'][1] for i in range(0, len(data), 3))
for index in [0, 1, 3, 5]:
    key = 'skirt-panel-' + str(index)
    assert world_min_y(parts[key]) < world_min_y(old_parts[key]) - .1, key
    assert parts[key]['tailoring']['lengthRatio'] > 1, key
for key in ['girl-dress-inset-pleat-seams', 'girl-dress-brocade-diamonds', 'girl-dress-running-stitches', 'girl-dress-gold-tail-tassel']:
    assert key in parts, key
assert len([key for key in parts if key.startswith('girl-dress-pastel-bauble-')]) == 15
assert len([key for key in parts if key.startswith('girl-dress-bauble-loop-')]) == 15
assert set(model['festivalDress']['detailParts']) <= set(parts)
assert model['festivalDress']['pleatSeams'] == 11
assert model['festivalDress']['brocadeMotifs'] == 45
assert model['festivalDress']['pastelBaubles'] == 15
Path(str(out) + '-module.mjs').write_text(html.split('<script type="module">', 1)[1].rsplit('</script>', 1)[0])
print('SWRLZ_V1192_RELEASE_VERIFIED', len(raw), manifest['finalSha256'], '124_PATCHES_65_ASSETS',
      'ALL_PREVIOUS_SOURCES_AND_ASSETS_EXACT', 'CLOSED_CONNECTED_SKIN',
      'PARTS', len(parts), 'TRIANGLES', triangles, 'COMPANIONS_EXACT', len(companions))
