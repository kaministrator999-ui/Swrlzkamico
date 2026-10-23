#!/usr/bin/env python3
"""Verify smooth native anatomy, restored hair piñatas and immutable lineage."""
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
baseline = json.loads((ROOT / 'tests/smooth_pinata_baseline_v11_92.json').read_text())
assert manifest['name'] == '§wyrl§ Engine v11.93'
assert manifest['finalArtifact'] == 'swyrl_engine_v11_93.html'
assert len(manifest['patches']) == 125
assert manifest['patches'] == baseline['patches'] + ['patches/v11_93_smooth_anatomy_pinatas.py']
assert len(baseline['sources']) == 302
assert len(baseline['assets']) == 65
for path, digest in baseline['sources'].items():
    assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest, path
subprocess.run(['python', str(ROOT / 'build_space.py'), '--output', str(out)],
               check=True, stdout=subprocess.DEVNULL)
raw = (out / 'index.html').read_bytes()
html = raw.decode()
receipt = json.loads((out / 'SOURCE.json').read_text())
assert len(raw) == manifest['finalBytes'] == receipt['finalBytes']
assert hashlib.sha256(raw).hexdigest() == manifest['finalSha256'] == receipt['finalSha256']
assert receipt['sourceVersion'] == manifest['name']
assert receipt['patches'] == manifest['patches']
new_scene = 'scenes/model-atelier-smooth-girl-v11-93.swyrl.json'
assert set(receipt['assets']) == set(baseline['assets']) | {new_scene}
assert len(receipt['assets']) == 66
for path, meta in receipt['assets'].items():
    data = (out / path).read_bytes()
    assert len(data) == meta['bytes'], path
    assert hashlib.sha256(data).hexdigest() == meta['sha256'], path
    if path in baseline['assets']:
        assert meta == baseline['assets'][path], path
for token in [
    'SWYRL_ENGINE_DEPLOY_MARKER: V11_93_SMOOTH_ANATOMY_PINATAS',
    "window.SWRLZ_FORGE_BUILD={version:'v11.93'",
    '<title>§wyrl§ Engine · Maker v11.93</title>',
    'function atelierPortraitRefinementV1193(',
    'function atelierSmoothLegsV1193(', 'function atelierFestivalFinishV1193(',
    new_scene, 'data-project-template="festival-girl-saved"',
]:
    assert token in html, token
assert html.count('SWYRL_ENGINE_DEPLOY_MARKER: V11_93_SMOOTH_ANATOMY_PINATAS') == 1
chunks = sorted((ROOT / 'payload/festival-girl').glob('smooth-v11-93.swyrl.json.gz.part*'))
assert chunks, 'Missing v11.93 lossless native scene payload'
scene_bytes = (out / new_scene).read_bytes()
assert gzip.decompress(b''.join(path.read_bytes() for path in chunks)) == scene_bytes
scene = json.loads(scene_bytes)
previous = json.loads((out / 'scenes/model-atelier-reference-girl-v11-92.swyrl.json').read_bytes())
assert scene['project']['canonicalId'] == previous['project']['canonicalId'] == 'organic-anime-girl'
assert scene['engine'] == '§wyrl§ Engine · Maker v11.93'
model, old_model = scene['project']['modelAtelier'], previous['project']['modelAtelier']
assert model['appearanceRevision'] == 'v11.93'
parts = {part['id']: part for part in model['parts']}
old_parts = {part['id']: part for part in old_model['parts']}
assert len(parts) == len(model['parts']), 'Duplicate native part IDs'
assert model['assemblies'] == old_model['assemblies'], 'Companion/socket/motion assembly changed'
companions = [part for part in old_model['parts'] if part['group'] != 'Character']
assert len(companions) == 117
for part in companions:
    assert parts[part['id']] == part, part['id']
for component, group, socket, owner in [
    ('azure', 'Azure frost', 'hair-azure', 'hair-bun--1'),
    ('coral', 'Coral flare', 'hair-coral', 'hair-bun-1'),
]:
    assert len([part for part in parts.values() if part['group'] == group]) == 28
    entry = next(c for c in model['assemblies']['components'] if c['id'] == component)
    assert entry['state'] == 'attached' and entry['socketId'] == socket and entry['group'] == group
    binding = next(s for s in model['assemblies']['sockets'] if s['id'] == socket)
    assert binding['partId'] == owner
    for field in ['position', 'rotation', 'scale']:
        assert parts[owner][field] == old_parts[owner][field], (owner, field)
legacy = json.loads((out / 'scenes/model-atelier-organic-anime-girl-v11-91.swyrl.json').read_bytes())
grips = {part['id']: part for part in legacy['project']['modelAtelier']['parts']
         if part['id'] in {'hair-grip--1', 'hair-grip-1'}}
assert len(grips) == 2
for key, original in grips.items():
    assert parts[key] == original, 'Original hair braid connector changed: ' + key
del legacy
triangles = 0
for part in parts.values():
    assert part['kind'] == 'topologyMesh', part['id']
    data = part['topologyMesh']
    vertices = len(data['positions']) // 3
    assert vertices and len(data['positions']) % 3 == 0, part['id']
    assert len(data['uvs']) == vertices * 2, part['id']
    assert len(data['indices']) and len(data['indices']) % 3 == 0, part['id']
    assert all(math.isfinite(v) and abs(v) < 100 for v in data['positions']), part['id']
    assert all(math.isfinite(v) for v in data['uvs']), part['id']
    assert all(type(v) is int and 0 <= v < vertices for v in data['indices']), part['id']
    assert all(len(part[k]) == 3 and all(math.isfinite(v) for v in part[k])
               for k in ['position', 'rotation', 'scale']), part['id']
    triangles += len(data['indices']) // 3
for group in model['meshGroups']:
    assert 1 < len(group['members']) <= 30, group['id']
    assert len(set(group['members'])) == len(group['members']), group['id']
    assert all(member in parts for member in group['members']), group['id']
body = parts['girl-organic-body']['topologyMesh']
old_body = old_parts['girl-organic-body']['topologyMesh']
assert body['indices'] == old_body['indices'], 'Connected skin topology changed'
assert len(body['positions']) == len(old_body['positions'])
changes = collections.Counter()
maximum_displacement = 0
for i in range(0, len(body['positions']), 3):
    before = old_body['positions'][i:i + 3]
    after = body['positions'][i:i + 3]
    x, y, _ = before
    if y < .35:
        assert after == before, 'Foot changed outside the anatomy smoothing scope'
    if max(abs(a - b) for a, b in zip(after, before)) <= .000001:
        continue
    maximum_displacement = max(maximum_displacement, math.dist(after, before))
    if 3.58 <= y <= 4.46:
        changes['portrait'] += 1
    if 2.80 <= y <= 3.48 and .22 <= abs(x) <= .90:
        changes['arms'] += 1
    if .50 <= y <= 2.30 and .08 <= abs(x) <= .85:
        changes['legs'] += 1
assert all(changes[region] > 100 for region in ['portrait', 'arms', 'legs']), changes
assert maximum_displacement < .30, 'Anatomy remap moved skin outside its bounded scope'
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

def world_points(part):
    rx, ry, rz = part['rotation']
    a, b, c, d, e, f = (math.cos(rx), math.sin(rx), math.cos(ry),
                         math.sin(ry), math.cos(rz), math.sin(rz))
    rotation = [[c*e, -c*f, d], [b*d*e+a*f, -b*d*f+a*e, -b*c],
                [-a*d*e+b*f, a*d*f+b*e, a*c]]
    source, scale, position = part['topologyMesh']['positions'], part['scale'], part['position']
    return [[position[axis] + sum(rotation[axis][j] * source[i+j] * scale[j] for j in range(3))
             for axis in range(3)] for i in range(0, len(source), 3)]

def eye_rise(part, side):
    points = world_points(part)
    inner_x = (max if side < 0 else min)(p[0] for p in points)
    outer_x = (min if side < 0 else max)(p[0] for p in points)
    inner = [p[1] for p in points if abs(p[0] - inner_x) < .001]
    outer = [p[1] for p in points if abs(p[0] - outer_x) < .001]
    assert inner and outer
    return sum(outer) / len(outer) - sum(inner) / len(inner)
corner_rises = {}
for side, sign in [('left', -1), ('right', 1)]:
    for suffix in ['sclera', 'iris', 'upper-lid', 'lower-lid', 'brow']:
        key = side + '-' + suffix
        assert parts[key]['topologyMesh']['positions'] != old_parts[key]['topologyMesh']['positions'], key
    corner_rises[side] = eye_rise(parts[side + '-sclera'], sign)
    assert .035 < corner_rises[side] < .065, (side, corner_rises[side])
    assert corner_rises[side] > eye_rise(old_parts[side + '-sclera'], sign) + .005
assert 'girl-reference-cyan-tendril' in parts and 'girl-reference-coral-temple' in parts
fans = [key for key in old_parts if key.startswith('girl-reference-ponytail-')]
assert fans
for key in fans:
    assert key in parts, key
    new_points, old_points = world_points(parts[key]), world_points(old_parts[key])
    new_extent = [max(p[a] for p in new_points) - min(p[a] for p in new_points) for a in range(3)]
    old_extent = [max(p[a] for p in old_points) - min(p[a] for p in old_points) for a in range(3)]
    assert all(new < old * .85 for new, old in zip(new_extent, old_extent)), key

def leg_sections(data):
    result = []
    source = data['positions']
    for y in [.70, .90, 1.10, 1.25, 1.40, 1.52, 1.65, 1.80, 2.00, 2.20]:
        points = [(source[i], source[i+2]) for i in range(0, len(source), 3)
                  if .065 < source[i] < .85 and abs(source[i+1] - y) < .019]
        assert points, ('Missing actual leg skin section', y)
        result.append({'y': y, 'radius': (max(p[0] for p in points) - min(p[0] for p in points)) / 2,
                       'depth': max(p[1] for p in points) - min(p[1] for p in points)})
    return result
sections = leg_sections(body)
radii = {section['y']: section['radius'] for section in sections}
assert radii[1.10] > radii[.70] * 1.10, 'Calf does not flow into a narrower ankle'
assert radii[1.52] < radii[1.25] * 1.15, 'Knee forms an oversized band instead of a taper'
assert radii[2.20] > radii[1.52] * 1.20, 'Thigh-to-knee profile is missing'
coverage=model['coverageRefinement']
assert coverage['underlayer']=='festival-shorts' and coverage['opaque'] is True
assert coverage['armorFit']=='native diagonal hem planes'
assert set(coverage['armorLinings'])=={'right-arm-band','left-wrist-cuff','bodice-stitch-2','right-wrist-0','right-wrist-1','right-wrist-2'}
assert parts['festival-shorts']['topologyMesh']['positions']!=old_parts['festival-shorts']['topologyMesh']['positions']
assert min(parts['festival-shorts']['topologyMesh']['positions'][1::3])<2.0
assert max(parts['festival-shorts']['topologyMesh']['positions'][1::3])>2.8
Path(str(out) + '-module.mjs').write_text(html.split('<script type="module">', 1)[1].rsplit('</script>', 1)[0])
print('SWRLZ_V1193_RELEASE_VERIFIED', len(raw), manifest['finalSha256'],
      '125_PATCHES_66_ASSETS', 'ALL_PREVIOUS_SOURCES_AND_ASSETS_EXACT',
      'CLOSED_CONNECTED_SKIN', 'PARTS', len(parts), 'TRIANGLES', triangles,
      'COMPANIONS_EXACT', len(companions), 'RESTORED_HAIR_GRIPS_EXACT',
      'CHANGED_SKIN_VERTICES', dict(changes), 'ACTUAL_EYE_CORNER_RISES', corner_rises,
      'ACTUAL_LEG_SECTIONS', sections)
