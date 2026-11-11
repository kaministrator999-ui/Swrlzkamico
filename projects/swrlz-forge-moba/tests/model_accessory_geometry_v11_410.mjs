#!/usr/bin/env node
// Exercise the actual accessory recipe through Three 169 and the native
// topology validator/auditor. No substitute geometry implementation is used.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import {fileURLToPath, pathToFileURL} from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
if (!process.argv[2]) throw Error('Usage: node tests/model_accessory_geometry_v11_410.mjs /path/to/three-0.169.0.mjs');
const THREE = await import(pathToFileURL(path.resolve(process.argv[2])));
assert.equal(THREE.REVISION, '169');
const read = name => fs.readFileSync(path.join(ROOT, 'runtime', name), 'utf8');
const source = read('model_accessory_geometry_v11_410.js');
const nativeSource = read('model_atelier.js');
function nativeFunction(name) {
  const start = nativeSource.indexOf('function ' + name + '(');
  assert(start >= 0, 'Native function exists: ' + name);
  let at = nativeSource.indexOf('{', start), depth = 1;
  for (at++; depth; at++) {
    if (nativeSource[at] === '{') depth++;
    else if (nativeSource[at] === '}') depth--;
  }
  return nativeSource.slice(start, at);
}
const ctx = vm.createContext({THREE, structuredClone, console,
  MODEL_ATELIER_KINDS: ['sphere', 'box', 'cone', 'cylinder'],
  MODEL_ATELIER_MATERIALS: ['matte', 'silk', 'gloss', 'metal', 'emissive']});
vm.runInContext(nativeFunction('checkPart') + '\n' +
  read('model_atelier_topology_lod_v11_38.js') + '\n' +
  read('model_atelier_topology_audit_v11_44.js') + '\n' + source +
  '\nglobalThis.buildRecipe = se410BuildAccessoryRecipe;', ctx);
assert.equal(typeof ctx.buildRecipe, 'function');
const plain = value => JSON.parse(JSON.stringify(value));
const same = (actual, expected, message) => assert.deepEqual(plain(actual), plain(expected), message);
const close = (actual, expected, tolerance = 1e-6, message = '') =>
  assert(Math.abs(actual - expected) <= tolerance, message || `${actual} ≈ ${expected}`);
const build = params => ctx.buildRecipe(params);
const partNamed = (recipe, name) => recipe.parts.find(part => part.componentKey === name);
let groups = 0, testedParts = 0, maxVertices = 0, maxTriangles = 0;

function signedVolumes(data) {
  // A merged stitches component can contain several disconnected solids.
  // Check each island so an inverted small piece cannot hide in the sum.
  const {positions, indices} = data, parent = Array.from({length: positions.length / 3}, (_, i) => i);
  const root = i => { while (parent[i] !== i) { parent[i] = parent[parent[i]]; i = parent[i]; } return i; };
  const join = (a, b) => { a = root(a); b = root(b); if (a !== b) parent[b] = a; };
  for (let i = 0; i < indices.length; i += 3) { join(indices[i], indices[i + 1]); join(indices[i], indices[i + 2]); }
  const volumes = new Map();
  for (let i = 0; i < indices.length; i += 3) {
    const a = indices[i] * 3, b = indices[i + 1] * 3, c = indices[i + 2] * 3;
    const volume = (positions[a] * (positions[b + 1] * positions[c + 2] - positions[b + 2] * positions[c + 1]) +
      positions[a + 1] * (positions[b + 2] * positions[c] - positions[b] * positions[c + 2]) +
      positions[a + 2] * (positions[b] * positions[c + 1] - positions[b + 1] * positions[c])) / 6;
    const island = root(indices[i]); volumes.set(island, (volumes.get(island) || 0) + volume);
  }
  return [...volumes.values()];
}

function nativeMesh(part) {
  const geometry = ctx.atelierTopologyGeometry(part);
  const mesh = new THREE.Mesh(geometry, new THREE.MeshBasicMaterial({side: THREE.DoubleSide}));
  mesh.position.fromArray(part.position);
  mesh.rotation.set(...part.rotation);
  mesh.scale.fromArray(part.scale);
  mesh.updateMatrixWorld(true);
  return mesh;
}

function bodyBounds(recipe) {
  const body = partNamed(recipe, 'body'); assert(body, 'A separately editable body component is present');
  const mesh = nativeMesh(body), bounds = new THREE.Box3().setFromObject(mesh);
  mesh.geometry.dispose(); mesh.material.dispose(); return bounds;
}

function auditRecipe(recipe, label = 'recipe') {
  assert.equal(recipe?.ok, true, `${label}: ${recipe?.reason || recipe?.error || 'Recipe failed'}`);
  assert(Array.isArray(recipe.parts) && recipe.parts.length >= 4 && recipe.parts.length <= 32, label + ': bounded editable component count');
  const keys = recipe.parts.map(part => part.componentKey);
  assert(keys.every(key => typeof key === 'string' && key.length > 0), label + ': stable component keys');
  assert.equal(new Set(keys).size, keys.length, label + ': distinct component keys');
  assert(recipe.parameters && typeof recipe.parameters === 'object');
  const aggregate = new THREE.Box3();
  for (const [index, part] of recipe.parts.entries()) {
    const name = `${label}/${part.componentKey}`;
    assert.equal(part.kind, 'topologyMesh', name + ': actual editable indexed topology');
    assert.equal(typeof part.name, 'string'); assert(part.name.trim() && part.name.length <= 100);
    assert(['matte', 'silk', 'gloss', 'metal', 'emissive'].includes(part.material), name + ': native material vocabulary');
    same(part.position, [0, 0, 0], name + ': component position baked into geometry');
    same(part.rotation, [0, 0, 0], name + ': component rotation baked into geometry');
    same(part.scale, [1, 1, 1], name + ': component scale baked into geometry');
    assert.equal(ctx.checkPart({...part, id: 'accessory-test-' + index}), true, name + ': native part validation');
    assert.equal(ctx.atelierTopologyValid(part), true, name + ': portable native topology validation');
    const audit = ctx.atelierTopologyAudit(part.topologyMesh);
    const report = JSON.stringify({...audit, edges: undefined});
    assert.equal(audit.ok, true, name + ': ' + report);
    for (const key of ['invalidFaces', 'zeroAreaFaces', 'boundaryEdges', 'nonManifoldEdges', 'oppositeWindingErrors'])
      assert.equal(audit[key], 0, name + ': ' + report);
    const volumes = signedVolumes(part.topologyMesh);
    assert(volumes.every(volume => Number.isFinite(volume) && volume > 1e-15), name + ': every closed material island faces outward: ' + volumes);
    const mesh = nativeMesh(part);
    assert(mesh.geometry.boundingSphere && Number.isFinite(mesh.geometry.boundingSphere.radius));
    assert(Array.from(mesh.geometry.attributes.normal.array).every(Number.isFinite), name + ': finite render normals');
    aggregate.union(new THREE.Box3().setFromObject(mesh));
    mesh.geometry.dispose(); mesh.material.dispose();
    testedParts++; maxVertices = Math.max(maxVertices, audit.vertices); maxTriangles = Math.max(maxTriangles, audit.faces);
  }
  assert(recipe.bounds && Array.isArray(recipe.bounds.min) && Array.isArray(recipe.bounds.max) && Array.isArray(recipe.bounds.size));
  const extent = aggregate.getSize(new THREE.Vector3());
  for (let axis = 0; axis < 3; axis++) {
    close(recipe.bounds.min[axis], aggregate.min.getComponent(axis), 2e-6, label + ': native minimum bound');
    close(recipe.bounds.max[axis], aggregate.max.getComponent(axis), 2e-6, label + ': native maximum bound');
    close(recipe.bounds.size[axis], extent.getComponent(axis), 2e-6, label + ': native extent');
    assert(Number.isFinite(recipe.bounds.size[axis]) && recipe.bounds.size[axis] > 0);
  }
  const mount = recipe.mount;
  assert(mount && Array.isArray(mount.position) && Array.isArray(mount.normal));
  assert.equal(mount.position.length, 3); assert(mount.position.every(Number.isFinite));
  close(new THREE.Vector3(...mount.normal).length(), 1, 1e-8, label + ': normalized attachment normal');
  assert(mount.normal[2] < -.99, label + ': mounting normal points toward the back');
  const body = bodyBounds(recipe);
  assert(mount.position[2] <= body.min.z + 1e-6, label + ': attachment behind body back plane');
  return recipe;
}

const baseline = auditRecipe(build({}), 'default');
assert(partNamed(baseline, 'flap'), 'Flap is separately editable');
assert(baseline.parts.some(part => part.material === 'metal'), 'Buckle/clasp uses native metal material');
assert(baseline.parts.some(part => /loop/i.test(part.componentKey)), 'Belt loops are native geometry');
assert(baseline.parts.some(part => /emblem/i.test(part.componentKey)), 'Reference leaf emblem is native geometry');
groups++;

{
  const part = partNamed(baseline, 'body'), mesh = nativeMesh(part);
  const bounds = new THREE.Box3().setFromObject(mesh), height = bounds.max.y - bounds.min.y;
  const ray = new THREE.Raycaster(new THREE.Vector3(0, bounds.max.y + height, 0), new THREE.Vector3(0, -1, 0));
  const floor = ray.intersectObject(mesh)[0];
  assert(floor, 'Open cavity ray reaches an inner floor');
  assert(floor.point.y < bounds.max.y - height * .5, 'Body opening is genuinely hollow, not capped by a solid blob');
  ray.set(new THREE.Vector3(0, bounds.min.y - height, 0), new THREE.Vector3(0, 1, 0));
  const bottom = ray.intersectObject(mesh)[0];
  assert(bottom && floor.point.y > bottom.point.y + 1e-5, 'Bottom has real material thickness');
  for (const direction of [new THREE.Vector3(0, 0, -1), new THREE.Vector3(0, 0, 1), new THREE.Vector3(1, 0, 0), new THREE.Vector3(-1, 0, 0)]) {
    ray.set(direction.clone().multiplyScalar(-3), direction);
    const contact = ray.intersectObject(mesh)[0];
    assert(contact && Number.isFinite(contact.distance) && contact.face.normal.lengthSq() > .99, 'Native mesh has selectable front/back/side surfaces');
  }
  mesh.geometry.dispose(); mesh.material.dispose(); groups++;
}

{
  const input = {width: 1.2, height: 1.35, depth: .48, detail: false}, before = structuredClone(input);
  const larger = auditRecipe(build(input), 'larger'); same(input, before, 'Recipe never mutates caller parameters');
  const a = bodyBounds(baseline).getSize(new THREE.Vector3()), b = bodyBounds(larger).getSize(new THREE.Vector3());
  for (const axis of ['x', 'y', 'z']) assert(b[axis] > a[axis] * 1.3, 'Dimensions change actual body ' + axis + ' geometry');
  const detailOff = auditRecipe(build({detail: false}), 'without details');
  const triangles = recipe => recipe.parts.reduce((sum, part) => sum + part.topologyMesh.indices.length / 3, 0);
  assert(triangles(detailOff) < triangles(baseline), 'Detail toggle removes actual seam/stitch topology');
  same(partNamed(detailOff, 'body').topologyMesh, partNamed(baseline, 'body').topologyMesh, 'Detail controls preserve the body');
  same(partNamed(detailOff, 'flap').topologyMesh, partNamed(baseline, 'flap').topologyMesh, 'Detail controls preserve the flap');
  groups++;
}

{
  const short = auditRecipe(build({flap: .3, strap: .1}), 'short flap/strap');
  const long = auditRecipe(build({flap: .8, strap: .9}), 'long flap/strap');
  assert.notEqual(JSON.stringify(partNamed(short, 'flap').topologyMesh), JSON.stringify(partNamed(long, 'flap').topologyMesh), 'Flap reach changes editable geometry');
  const loops = recipe => recipe.parts.filter(part => /loop|strap/i.test(part.componentKey)).map(part => part.topologyMesh);
  assert.notEqual(JSON.stringify(loops(short)), JSON.stringify(loops(long)), 'Strap control changes editable geometry');
  const palette = {bodyColor: '#47305f', flapColor: '#73528b', trimColor: '#f8e3ae', metalColor: '#ffd385'};
  const tinted = auditRecipe(build({...palette, emblem: 'star'}), 'violet star');
  assert.equal(partNamed(tinted, 'body').color.toLowerCase(), palette.bodyColor);
  assert.equal(partNamed(tinted, 'flap').color.toLowerCase(), palette.flapColor);
  assert(tinted.parts.some(part => part.color.toLowerCase() === palette.metalColor), 'Metal palette is applied');
  const emblem = recipe => recipe.parts.filter(part => /emblem/i.test(part.componentKey));
  assert.notEqual(JSON.stringify(emblem(tinted).map(part => part.topologyMesh)), JSON.stringify(emblem(baseline).map(part => part.topologyMesh)), 'Star and leaf are distinct native meshes');
  const unmarked = auditRecipe(build({emblem: 'none'}), 'no emblem');
  assert.equal(emblem(unmarked).length, 0, 'None removes emblem geometry'); groups++;
}

{
  const invalid = [null, [], 'pouch', {width: NaN}, {width: null}, {height: Infinity}, {depth: -Infinity}, {thickness: '0.035'},
    {rounding: {}}, {flap: []}, {strap: () => .3}, {detail: 'yes'}, {bodyColor: 'brown'}, {flapColor: '#1234'},
    {trimColor: '#gggggg'}, {metalColor: null}, {detail: null}, {emblem: null}, {emblem: 'logo'}];
  for (const params of invalid) {
    const result = build(params);
    assert.equal(result?.ok, false, 'Typed invalid input explicitly fails: ' + String(params));
    assert.equal(result.parts?.length || 0, 0, 'Invalid input does not expose partial geometry');
    assert(typeof (result.reason || result.error) === 'string', 'Invalid input explains its failure');
  }
  // Numeric extremes may be rejected or visibly normalized. Either path must
  // avoid malformed native geometry and report the effective parameters.
  for (const params of [{width: 0}, {height: -1}, {depth: 200}, {thickness: 4}, {rounding: -4}, {flap: 2}, {strap: -2}]) {
    const result = build(params);
    if (result.ok) { auditRecipe(result, 'normalized ' + JSON.stringify(params)); assert.notEqual(result.parameters[Object.keys(params)[0]], Object.values(params)[0]); }
    else assert(typeof (result.reason || result.error) === 'string');
  }
  groups++;
}

{
  const variants = [
    {width: .35, height: .35, depth: .15, thickness: .012, rounding: .02, flap: .25, strap: 0, detail: false},
    {width: 1.8, height: 1.8, depth: .75, thickness: .1, rounding: .25, flap: .85, strap: 1},
    {width: .5, height: 1.5, depth: .2, thickness: .018, rounding: .05, flap: .7, strap: .7},
    {width: 1.5, height: .5, depth: .65, thickness: .05, rounding: .12, flap: .35, strap: .2},
    {width: .75, height: 1.1, depth: .28, thickness: .03, rounding: .09, flap: .6, strap: .45, emblem: 'star'}
  ];
  for (const [index, params] of variants.entries()) auditRecipe(build(params), 'range ' + index);
  // A difficult mixed slider state either yields a valid normalized recipe or
  // an explicit failure, never NaN surfaces or a half-built component set.
  const mixed = build({width: .35, height: 1.8, depth: .15, thickness: .1, rounding: .25, flap: .85, strap: .02});
  if (mixed.ok) auditRecipe(mixed, 'mixed limits'); else assert(typeof (mixed.reason || mixed.error) === 'string');
  groups++;
}

{
  const second = build({}); same(second, baseline, 'Repeated builds are deterministic');
  assert.notEqual(second.parts[0].topologyMesh.positions, baseline.parts[0].topologyMesh.positions, 'Each build owns its arrays');
  const roundtrip = plain(baseline); auditRecipe(roundtrip, 'JSON save/reload');
  const saved = JSON.stringify(baseline), mutable = build({}); mutable.parts[0].topologyMesh.positions[0] += .123;
  assert.equal(JSON.stringify(baseline), saved, 'Editing a new native component does not mutate previous recipes');
  groups++;
}

console.log('MODEL_ACCESSORY_GEOMETRY_V11_410_PASS', JSON.stringify({groups, three: THREE.REVISION,
  testedParts, maxVertices, maxTriangles, nativeValidator: true, nativeAudit: true,
  cavity: 'open shell with material thickness', persistence: 'ordinary editable topology'}));
