// Real Three.js geometry regressions; no browser, inference or model mutation.
// Usage: node THIS_TEST SEALED_HTML [THREE_0_169_ESM_PATH]
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import {pathToFileURL} from 'node:url';

const THREE = process.argv[3]
  ? await import(pathToFileURL(process.argv[3]).href)
  : await import('three');
assert.equal(THREE.REVISION, '169', 'Use the renderer version shipped by this engine');
const html = fs.readFileSync(process.argv[2], 'utf8');
const between = (start, end) => {
  const begin = html.indexOf(start);
  assert(begin >= 0, start);
  const finish = html.indexOf(end, begin + start.length);
  assert(finish > begin, end);
  return html.slice(begin, finish);
};
const organic = between('function atelierOrganicLoft(part){', '\n// v11.7 original paper construction');
const courier = between('function geometry(part){\n const g=atelierCourierBaseGeometry(part);',
                        '\nfunction atelierCourierCamera(view){');
const correction = between('/* SE295_CHAT_LOFT_SURFACE_NORMALS_START */',
                           '/* SE295_CHAT_LOFT_SURFACE_NORMALS_END */');
assert.equal(html.split('/* SE295_CHAT_LOFT_SURFACE_NORMALS_START */').length - 1, 1);
const context = vm.createContext({THREE, console});
vm.runInContext(organic + '\nfunction atelierCourierBaseGeometry(part){' +
  'return part.kind === "loft" ? atelierOrganicLoft(part) : new THREE.SphereGeometry(1,8,6);' +
  '}\n' + courier, context);
const originalGeometry = context.geometry;
vm.runInContext(correction, context);
const geometry = context.geometry;
const spec = (name, path, radii) => ({
  id: 'atelier-chat-' + name, name, kind: 'loft', path, radii, segments: 32,
  position: [0, 0, 0], rotation: [0, 0, 0], scale: [1, 1, 1],
  color: '#f4ece0', material: 'silk', group: 'Custom',
});
const fixtures = [
  spec('straight', [[0, 0, 0], [0, 2, 0]], [.12, .12]),
  spec('curved-up', [[0, 0, 0], [.2, .7, .05], [-.1, 1.4, .1], [.15, 2.1, 0]],
       [.06, .05, .045, .03]),
  {...spec('curved-down', [[.55, 2.72, .39], [.61, 2.52, .50], [.55, 2.32, .55],
                          [.64, 2.12, .55], [.57, 1.94, .55]], [.12, .13, .115, .12, .07]),
   segments: 12}, // Exact saved sampling of the reported native braid.
];
const sameAttribute = (first, second, name, reason) => assert.deepEqual(
  Array.from(first.getAttribute(name).array), Array.from(second.getAttribute(name).array), reason);
const sameGeometry = (first, second, reason) => {
  for (const name of Object.keys(first.attributes)) sameAttribute(first, second, name, reason + ' ' + name);
  assert.deepEqual(Array.from(first.index.array), Array.from(second.index.array), reason + ' index');
};
function faceDots(geometry, outwardNormals) {
  const positions = geometry.getAttribute('position'), indices = geometry.index.array;
  const dots = [];
  for (let index = 0; index < indices.length; index += 3) {
    const ids = [indices[index], indices[index + 1], indices[index + 2]];
    const [a, b, c] = ids.map(id => new THREE.Vector3().fromBufferAttribute(positions, id));
    const face = b.sub(a).cross(c.sub(a));
    if (face.lengthSq() < 1e-15) continue;
    const radial = ids.reduce((sum, id) => sum.add(
      new THREE.Vector3().fromBufferAttribute(outwardNormals, id)), new THREE.Vector3());
    dots.push(face.normalize().dot(radial.normalize()));
  }
  return dots;
}
for (const part of fixtures) {
  const frozen = structuredClone(part);
  const before = originalGeometry(part), after = geometry(part);
  const radial = before.getAttribute('normal');
  const oldDots = faceDots(before, radial), correctedDots = faceDots(after, radial);
  assert(oldDots.every(dot => dot < 0), part.name + ' fixture must expose historical inward winding');
  assert(correctedDots.every(dot => dot > 0), part.name + ' faces must point toward the outer surface');
  assert(faceDots(after, after.getAttribute('normal')).every(dot => dot > .5),
    part.name + ' recomputed normals must agree with actual face orientation');
  for (const name of ['position', 'uv', 'color']) sameAttribute(before, after, name,
    part.name + ' ' + name + ' must retain its exact source values');
  for (let index = 0; index < before.index.count; index += 3) {
    assert.equal(after.index.array[index], before.index.array[index]);
    assert.equal(after.index.array[index + 1], before.index.array[index + 2]);
    assert.equal(after.index.array[index + 2], before.index.array[index + 1]);
  }
  assert.deepEqual(part, frozen, 'Renderer must not change saved descriptors or native history data');
  const repeat = geometry(part);
  sameGeometry(after, repeat, 'Repeated rendering must produce the same corrected surface');
  console.log('CHAT_LOFT_OUTWARD_SURFACE_PASS', part.name, correctedDots.length);
}

for (const flags of [
  {id: 'historical-starter-loft'},
  {textureBinding: {set: 'astra-4k', tile: 'ivory', normalStrength: .2}},
  {hdFinish: {style: 'hair', relief: .7}},
  {surfaceStyle: 'silken-lock'},
  {organicSurface: {species: 'wolf', region: 'coat'}},
  {kind: 'sphere'},
]) {
  const part = {...structuredClone(fixtures[1]), ...flags};
  const frozen = structuredClone(part);
  const before = originalGeometry(part), after = geometry(part);
  sameGeometry(before, after, 'Preserve existing render path ' + JSON.stringify(flags));
  assert.deepEqual(part, frozen);
  if (part.textureBinding) {
    // The legacy courier path is already outward. A second reversal would
    // invert these faces; comparing buffers also catches a second rebuild.
    const outward = context.atelierOrganicLoft(part).getAttribute('normal');
    assert(faceDots(after, outward).every(dot => dot > 0), 'Textured loft must never be double-flipped');
  }
}
assert(html.includes('model.parts=parts;model.meshGroups=[];model.assemblies=null;'),
  'Keep the canonical v11.294 Vanguard socket-loader correction');
console.log('CHAT_LOFT_SURFACE_NORMALS_V11_295_PASS');
