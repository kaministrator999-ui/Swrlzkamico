#!/usr/bin/env python3
"""Verify the fitted skirt waist and immutable source lineage."""
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
baseline = json.loads((ROOT / 'tests/fitted_skirt_baseline_v11_94.json').read_text())
assert manifest['name'] == '§wyrl§ Engine v11.95'
assert manifest['finalArtifact'] == 'swyrl_engine_v11_95.html'
assert len(manifest['patches']) == 127
assert manifest['patches'] == baseline['patches'] + ['patches/v11_95_fitted_skirt_waist.py']
assert len(baseline['sources']) == 312 and len(baseline['assets']) == 67
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
new_scene = 'scenes/model-atelier-fitted-waist-v11-95.swyrl.json'
assert set(receipt['assets']) == set(baseline['assets']) | {new_scene}
assert len(receipt['assets']) == 68
for path, meta in receipt['assets'].items():
    data = (out / path).read_bytes()
    assert len(data) == meta['bytes'] and hashlib.sha256(data).hexdigest() == meta['sha256'], path
    if path in baseline['assets']:
        assert meta == baseline['assets'][path], path
for token in [
    'SWYRL_ENGINE_DEPLOY_MARKER: V11_95_FITTED_SKIRT_WAIST',
    "window.SWRLZ_FORGE_BUILD={version:'v11.95'",
    '<title>§wyrl§ Engine · Maker v11.95</title>',
    'function atelierFittedSkirtV1195(',
    new_scene, 'data-project-template="festival-girl-saved"',
]:
    assert token in html, token
chunks = sorted((ROOT / 'payload/festival-girl').glob('fitted-v11-95.swyrl.json.gz.part*'))
scene_bytes = (out / new_scene).read_bytes()
assert chunks and gzip.decompress(b''.join(p.read_bytes() for p in chunks)) == scene_bytes
scene = json.loads(scene_bytes)
previous = json.loads((out / 'scenes/model-atelier-knee-armor-v11-94.swyrl.json').read_bytes())
model, old_model = scene['project']['modelAtelier'], previous['project']['modelAtelier']
assert scene['engine'] == '§wyrl§ Engine · Maker v11.95'
assert model['appearanceRevision'] == 'v11.95'
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
assert parts['girl-organic-body'] == old_parts['girl-organic-body'], 'Skin/portrait/legs changed outside waist scope'
fit = model['skirtFitV1195']
assert fit['version'] == 'v11.95'
assert set(changed) <= set(fit['affectedParts']), set(changed) - set(fit['affectedParts'])
assert model['festivalDress']['revision'] == 'fitted-waist-v11.95'
for key in fit['affectedParts']:
    before, after = old_parts[key]['topologyMesh']['positions'], parts[key]['topologyMesh']['positions']
    p = parts[key]
    rx,ry,rz = p['rotation']; sx,sy,sz = p['scale']
    a,b,c,d,e,f = math.cos(rx),math.sin(rx),math.cos(ry),math.sin(ry),math.cos(rz),math.sin(rz)
    coefficients = [(b*d*e+a*f)*sx,(-b*d*f+a*e)*sy,-b*c*sz]
    for i in range(0, len(before), 3):
        old_y = p['position'][1] + sum(coefficients[j]*before[i+j] for j in range(3))
        new_y = p['position'][1] + sum(coefficients[j]*after[i+j] for j in range(3))
        assert abs(old_y-new_y) <= .000002, 'World-space height changed: ' + key
        if old_y <= 2.4:
            assert before[i:i+3] == after[i:i+3], 'Lower skirt silhouette changed: ' + key
for key in ['assemblies', 'meshGroups', 'portraitRefinement', 'portraitRefinementV1194',
            'legRefinement', 'anatomySmoothing', 'coverageRefinement', 'kneeSkirtRefinement']:
    assert model[key] == old_model[key], key
panels = model['kneeSkirtRefinement']['panelIds']
assert len(panels) == 9
minimum_y = min(min(parts[key]['topologyMesh']['positions'][1::3]) for key in model['kneeSkirtRefinement']['affectedParts'])
assert minimum_y >= 1.52

def section(source, y):
    xz = []
    for key in panels:
        p = source[key]
        assert p['position'] == [0,0,0] and p['rotation'] == [0,0,0] and p['scale'] == [1,1,1]
        data = p['topologyMesh']; ps, ids = data['positions'], data['indices']
        for i in range(0, len(ids), 3):
            face = [ids[i+j]*3 for j in range(3)]
            if min(ps[k+1] for k in face) > y or max(ps[k+1] for k in face) < y:
                continue
            for a,b in [(face[0],face[1]),(face[1],face[2]),(face[2],face[0])]:
                dy = ps[b+1] - ps[a+1]
                if abs(dy) < 1e-12:
                    continue
                t = (y - ps[a+1]) / dy
                if 0 <= t <= 1:
                    xz.append((ps[a]+(ps[b]-ps[a])*t, ps[a+2]+(ps[b+2]-ps[a+2])*t))
    assert xz, y
    return [max(abs(p[i]) for p in xz) for i in [0,1]]
sections=[]
for y in [2.65, 2.8, 2.9]:
    before,after=section(old_parts,y),section(parts,y)
    ratios=[a/b for a,b in zip(after,before)]
    if y >= 2.8:
        assert all(.60 < v < .88 for v in ratios), (y,ratios)
    sections.append({'y':y,'before':before,'after':after,'ratios':ratios})
Path(str(out) + '-module.mjs').write_text(html.split('<script type="module">', 1)[1].rsplit('</script>', 1)[0])
print('SWRLZ_V1195_RELEASE_VERIFIED', len(raw), manifest['finalSha256'],
      '127_PATCHES_68_ASSETS', '312_PREVIOUS_SOURCES_67_ASSETS_EXACT',
      'BODY_PORTRAIT_COMPANIONS_ASSEMBLIES_SHORTS_LOWER_HEM_EXACT', 'PARTS', len(parts),
      'TRIANGLES', triangles, 'SKIRT_MINIMUM_Y', minimum_y, 'ACTUAL_WAIST_SECTIONS', sections)
