/* SE350_MODEL_VR_SURFACE_START */
// Native surface gestures: derived geometry previews, one validated native
// checkpoint on release. Nothing is saved while a controller is held.
const se350ModelSurface = (() => {
  let active = null, lastError = '', lastAction = '', serial = 0;
  const skinBonesCache = new WeakMap();
  const vector = (value, limit = 100) => Array.isArray(value) && value.length === 3 && value.every(n => typeof n === 'number' && Number.isFinite(n) && Math.abs(n) <= limit);
  const fail = reason => { lastError = reason; return {ok: false, reason, error: reason}; };
  const ready = () => !!(panel && !panel.hidden && modelRoot && model()?.parts);
  const fingerprint = part => JSON.stringify(part);
  function current(g, strict = false) {
    return ready() && model() === g.document && model().parts === g.parts && modelRoot === g.root &&
      (!g.part || partById(g.id) === g.part &&
        ['position', 'rotation', 'scale'].every(key => g.transform[key].every((n, i) => g.part[key]?.[i] === n)) &&
        Object.entries(g.sources).every(([key, value]) => g.part[key] === value) &&
        (!strict || fingerprint(g.part) === g.fingerprint)) &&
      (!g.mesh || g.mesh.parent === g.root && g.mesh.geometry === (g.preview || g.original)) &&
      (!g.bindPoseSkin || skinAtBindPose(g.mesh));
  }
  function restore(g) {
    if (g.mesh && g.mesh.geometry === g.preview) g.mesh.geometry = g.original;
    if (g.preview && g.preview !== g.original) g.preview.dispose();
    if (g.line) { g.line.removeFromParent(); g.line.geometry.dispose(); g.line.material.dispose(); }
    atelierHDDirty = true;
  }
  function cancel(reason = '') {
    const g = active; active = null;
    if (g) restore(g);
    if (reason) lastError = reason;
    return {ok: true, changed: false, cancelled: !!g};
  }
  function valid(type, strict = false) {
    if (!active || active.type !== type) return false;
    if (!current(active, strict)) { cancel('MODEL_CHANGED_DURING_SURFACE_GESTURE'); return false; }
    return true;
  }
  function skinAtBindPose(mesh) {
    if (!mesh.isSkinnedMesh) return true;
    const skeleton = mesh.skeleton, indices = mesh.geometry?.attributes?.skinIndex, weights = mesh.geometry?.attributes?.skinWeight;
    if (!skeleton || !indices || !weights) return false;
    mesh.updateWorldMatrix(true, false); mesh.updateMatrixWorld(true);
    let cached = skinBonesCache.get(indices);
    if (!cached || cached.weights !== weights || cached.indexVersion !== indices.version || cached.weightVersion !== weights.version) {
      const used = new Set();
      for (let i = 0; i < indices.count; i++) for (let k = 0; k < 4; k++) if (weights.getComponent(i, k) > 1e-7) used.add(indices.getComponent(i, k));
      cached = {weights, indexVersion: indices.version, weightVersion: weights.version, used}; skinBonesCache.set(indices, cached);
    }
    const used = cached.used;
    const effective = new THREE.Matrix4(), boneMatrix = new THREE.Matrix4(), unit = new THREE.Matrix4().elements;
    for (const index of used) {
      const bone = skeleton.bones[index], inverse = skeleton.boneInverses[index];
      if (!bone || !inverse) return false;
      bone.updateWorldMatrix(true, false);
      boneMatrix.multiplyMatrices(bone.matrixWorld, inverse);
      effective.copy(mesh.bindMatrixInverse).multiply(boneMatrix).multiply(mesh.bindMatrix);
      if (effective.elements.some((n, k) => !Number.isFinite(n) || Math.abs(n - unit[k]) > 1e-5)) return false;
    }
    return used.size > 0;
  }
  // Revision/rebuild and reference checks are cheap on XR frames. The full
  // descriptor fingerprint is rechecked immediately before a saved commit.
  function capture(id) {
    if (!ready()) return fail('MODEL_EDITOR_NOT_OPEN');
    if (active || se340ModelBridge.inspect().gesture) return fail('MODEL_GESTURE_ALREADY_ACTIVE');
    const picked = se340ModelBridge.select(id); if (!picked.ok) return picked;
    const part = partById(id), mesh = modelRoot.children.find(m => m.isMesh && m.userData?.atelierId === id);
    if (!part || !mesh?.geometry?.attributes?.position) return fail('MODEL_PROJECTION_NOT_READY');
    return {ok: true, document: model(), parts: model().parts, root: modelRoot, part, id,
      fingerprint: fingerprint(part), mesh, original: mesh.geometry,
      transform: Object.fromEntries(['position', 'rotation', 'scale'].map(key => [key, [...part[key]]])),
      sources: Object.fromEntries(['kind', 'topologyMesh', 'sculptBrushes', 'sculptVertexEdits', 'sculptLassos', 'refinementLayers', 'meshDensity'].map(key => [key, part[key]]))};
  }
  function localHit(id, hit) {
    const mesh = modelRoot?.children.find(m => m.isMesh && m.userData?.atelierId === id);
    if (!mesh || !vector(hit?.point, 1000) || !vector(hit?.normal, 1)) return fail('INVALID_SURFACE_HIT');
    mesh.updateWorldMatrix(true, false);
    const center = mesh.worldToLocal(new THREE.Vector3(...hit.point));
    // World normal -> local normal is transpose(M), unlike a direction.
    const normal = new THREE.Vector3(...hit.normal).applyMatrix3(new THREE.Matrix3().setFromMatrix4(mesh.matrixWorld).transpose()).normalize();
    return {ok: true, center: center.toArray(), normal: normal.toArray()};
  }
  function sculptBegin(id, options = {}) {
    const g = capture(id); if (!g.ok) return g;
    const operation = options.operation || 'push';
    if (!atelierSculptOperations.includes(operation)) return fail('INVALID_SCULPT_OPERATION');
    // Native sparse vertex edits precede refinement and skin deformation.
    // Refuse meshes without stable vertex correspondence rather than saving
    // edits against the wrong vertices when their procedural source rebuilds.
    if (g.original.userData?.refinedTriangles || g.part.refinementLayers?.some(l => l.enabled)) return fail('SCULPT_REQUIRES_UNREFINED_MESH');
    if (g.mesh.isSkinnedMesh && !skinAtBindPose(g.mesh)) return fail('SCULPT_REQUIRES_BIND_POSE');
    const remaining = atelierSculptMaxVertexEdits - (g.part.sculptVertexEdits?.length || 0);
    if (remaining <= 0) return fail('NATIVE_VERTEX_EDIT_BUDGET_REACHED');
    if (g.original.attributes.position.count > 24000) return fail('SCULPT_PREVIEW_VERTEX_BUDGET_EXCEEDED');
    const radius = options.radius ?? .18, strength = options.strength ?? .06;
    if (!Number.isFinite(radius) || radius < .03 || radius > 2.5 || !Number.isFinite(strength) || Math.abs(strength) > .5) return fail('INVALID_BRUSH_SIZE_OR_STRENGTH');
    const regionId = options.regionId === undefined ? atelierLassoActive : options.regionId;
    const region = regionId ? g.part.sculptLassos?.find(r => r.id === regionId && r.enabled) : null;
    if (regionId && options.regionId !== undefined && !region) return fail('SCULPT_REGION_NOT_FOUND');
    if (region && (region.resolution.some((n, i) => n !== atelierSculptResolution(g.part)[i]) || !atelierLassoPolygonValid(region))) return fail('SCULPT_REGION_RESOLUTION_CHANGED');
    const mask = region ? atelierLassoCompiledRegionMask(g.part, region) : null;
    const maskWeights = mask ? new Float32Array(g.original.attributes.position.count) : null;
    if (mask) {
      const positions = g.original.attributes.position, normals = g.original.attributes.normal, axis = new THREE.Vector3(...region.axis);
      for (let i = 0; i < positions.count; i++) {
        const point = [positions.getX(i), positions.getY(i), positions.getZ(i)];
        if (!mask.contains(point) || normals && new THREE.Vector3(normals.getX(i), normals.getY(i), normals.getZ(i)).dot(axis) < -.12) continue;
        maskWeights[i] = region.feather ? THREE.MathUtils.smoothstep(mask.distance(point), 0, region.feather) : 1;
      }
    }
    const preview = g.original.clone(); g.mesh.geometry = preview;
    active = {...g, type: 'sculpt', maskWeights, regionId: region?.id || null, preview, radius, strength, operation, remaining, bindPoseSkin: !!g.mesh.isSkinnedMesh,
      before: new Float32Array(g.original.attributes.position.array), maskPrevious: maskWeights ? new Float32Array(g.original.attributes.position.array.length) : null, changed: false, samples: 0};
    lastError = ''; lastAction = 'Sculpting ' + operation;
    return {ok: true, id, radius, strength, operation, regionId: region?.id || null, mesh: g.mesh};
  }
  function sculptUpdate(sample) {
    if (!valid('sculpt')) return fail('NO_CURRENT_SCULPT_GESTURE');
    const g = active;
    if (!vector(sample?.center) || !vector(sample?.normal, 1) || Math.hypot(...sample.normal) < .5 || sample.delta !== undefined && !vector(sample.delta, .5)) return fail('INVALID_SCULPT_SAMPLE');
    const dt = sample.dt === undefined ? 1 / 60 : sample.dt;
    if (!Number.isFinite(dt) || dt <= 0 || dt > .25) return fail('INVALID_SCULPT_TIME');
    const radius = sample.radius ?? g.radius, strength = sample.strength ?? g.strength;
    if (!Number.isFinite(radius) || radius < .03 || radius > 2.5 || !Number.isFinite(strength) || Math.abs(strength) > .5) return fail('INVALID_BRUSH_SIZE_OR_STRENGTH');
    const axis = new THREE.Vector3(...sample.normal).normalize();
    let amount = strength * Math.min(dt, .05) * 4;
    const operation = sample.smooth ? 'smooth' : g.operation;
    if (operation === 'translate') {
      if (!vector(sample.delta, .5)) return fail('TRANSLATE_REQUIRES_LOCAL_DELTA');
      axis.set(...sample.delta); amount = axis.length();
      if (amount < 1e-7) return {ok: true, changed: g.changed, sampled: false};
      axis.normalize();
    }
    const stroke = {center: sample.center, axis: axis.toArray(), radius, strength: amount,
      operation, falloff: 'smooth', plateau: 0, taper: .5, half: false, level: false,
      pitch: 0, yaw: 0, snap: 0, surfaceMode: 'front', selectionRadius: radius};
    const previous = g.maskPrevious; if (previous) previous.set(g.preview.attributes.position.array);
    atelierSculptApplyOperator(g.preview, stroke);
    const a = g.preview.attributes.position;
    let affected = 0, changed = false;
    for (let i = 0; i < a.count; i++) {
      const xyz = [a.getX(i), a.getY(i), a.getZ(i)];
      if (g.maskWeights) for (let k = 0; k < 3; k++) xyz[k] = previous[i * 3 + k] + (xyz[k] - previous[i * 3 + k]) * g.maskWeights[i];
      for (let k = 0; k < 3; k++) xyz[k] = Math.min(g.before[i * 3 + k] + .49999, Math.max(g.before[i * 3 + k] - .49999, xyz[k]));
      a.setXYZ(i, ...xyz);
      if (xyz.some((n, k) => Math.abs(n - g.before[i * 3 + k]) > 1e-7)) { affected++; changed = true; }
    }
    if (Math.ceil(affected / 256) > g.remaining) { cancel('NATIVE_VERTEX_EDIT_BUDGET_REACHED'); return fail('NATIVE_VERTEX_EDIT_BUDGET_REACHED'); }
    a.needsUpdate = true; g.preview.computeVertexNormals(); g.preview.computeBoundingSphere(); g.preview.computeBoundingBox();
    g.changed = changed; g.samples++; g.radius = radius; g.strength = strength; atelierHDDirty = true;
    return {ok: true, changed, affected, sampled: true};
  }
  function sculptEnd(commit = true) {
    if (!commit) return cancel();
    if (!valid('sculpt', true)) return fail('NO_CURRENT_SCULPT_GESTURE');
    const g = active, a = g.preview.attributes.position;
    const chunks = []; let indices = [], moves = [];
    const flush = () => { if (!indices.length) return; chunks.push({indices, moves, resolution: atelierSculptResolution(g.part)}); indices = []; moves = []; };
    for (let i = 0; i < a.count; i++) {
      const delta = [a.getX(i), a.getY(i), a.getZ(i)].map((n, k) => n - g.before[i * 3 + k]);
      if (delta.every(n => Math.abs(n) <= 1e-7)) continue;
      indices.push(i); moves.push(delta); if (indices.length === 256) flush();
    }
    flush();
    if (!chunks.length) { cancel(); return {ok: true, changed: false}; }
    const candidate = {...g.part, sculptVertexEdits: [...(g.part.sculptVertexEdits || []), ...chunks]};
    delete candidate.runtimeLOD;
    if (!checkPart(candidate)) { cancel('INVALID_NATIVE_SCULPT_EDIT'); return fail('INVALID_NATIVE_SCULPT_EDIT'); }
    active = null; restore(g); checkpoint(); g.part.sculptVertexEdits = candidate.sculptVertexEdits; delete g.part.runtimeLOD;
    selection = g.id; signalEdited(); lastError = ''; lastAction = 'Committed ' + g.operation + ' stroke';
    return {ok: true, changed: true, id: g.id, operation: g.operation, vertexCount: chunks.reduce((n, c) => n + c.indices.length, 0)};
  }
  function drawBegin(options = {}) {
    if (!ready()) return fail('MODEL_EDITOR_NOT_OPEN');
    if (active || se340ModelBridge.inspect().gesture) return fail('MODEL_GESTURE_ALREADY_ACTIVE');
    if (model().parts.length >= MODEL_ATELIER_LIMIT) return fail('MODEL_PART_LIMIT_REACHED');
    if (!vector(options.normal || [0, 0, 1], 1) || Math.hypot(...(options.normal || [0, 0, 1])) < .5) return fail('INVALID_DRAW_PLANE');
    const normal = new THREE.Vector3(...(options.normal || [0, 0, 1])).normalize();
    const helper = Math.abs(normal.y) < .84 ? new THREE.Vector3(0, 1, 0) : new THREE.Vector3(1, 0, 0);
    const u = new THREE.Vector3().crossVectors(helper, normal).normalize(), v = new THREE.Vector3().crossVectors(normal, u).normalize();
    const line = new THREE.Line(new THREE.BufferGeometry(), new THREE.LineBasicMaterial({color: 0xb6f5ff, depthTest: false}));
    line.userData.se350SurfacePreview = true; line.renderOrder = 100; modelRoot.add(line);
    active = {type: 'draw', document: model(), parts: model().parts, root: modelRoot, normal, u, v, points: [], anchor: null, line,
      name: String(options.name || 'VR drawn outline').slice(0, 100), color: /^#[a-fA-F0-9]{6}$/.test(options.color || '') ? options.color : '#af84d8'};
    lastError = ''; lastAction = 'Draw an outline on the work plane';
    return {ok: true};
  }
  function drawUpdate(point) {
    if (!valid('draw')) return fail('NO_CURRENT_DRAW_GESTURE');
    if (!vector(point)) return fail('INVALID_DRAW_POINT');
    const g = active, p = new THREE.Vector3(...point); if (!g.anchor) g.anchor = p.clone();
    p.addScaledVector(g.normal, -p.clone().sub(g.anchor).dot(g.normal));
    if (g.points.length && p.distanceTo(g.points[g.points.length - 1]) < .004) return {ok: true, sampled: false, pointCount: g.points.length};
    if (g.points.length >= 128) return {ok: true, sampled: false, pointCount: g.points.length, limit: true};
    g.points.push(p); const old = g.line.geometry; g.line.geometry = new THREE.BufferGeometry().setFromPoints(g.points); old.dispose(); atelierHDDirty = true;
    return {ok: true, sampled: true, pointCount: g.points.length};
  }
  function outlineData(g) {
    let points = g.points.map(p => p.clone());
    if (points.length > 3 && points[0].distanceTo(points[points.length - 1]) < .012) points.pop();
    for (let changed = true; changed && points.length > 3;) {
      changed = false;
      for (let i = 0; i < points.length; i++) {
        const a = points[(i + points.length - 1) % points.length], b = points[i], c = points[(i + 1) % points.length];
        const ab = b.clone().sub(a), bc = c.clone().sub(b);
        if (ab.length() < .004 || bc.length() < .004 || ab.clone().cross(bc).length() < 1e-5 && ab.dot(bc) >= 0) { points.splice(i, 1); changed = true; break; }
      }
    }
    if (points.length < 3) return fail('OUTLINE_REQUIRES_THREE_CORNERS');
    const center = points.reduce((sum, p) => sum.add(p), new THREE.Vector3()).multiplyScalar(1 / points.length);
    const contour = points.map(p => { const d = p.clone().sub(center); return new THREE.Vector2(d.dot(g.u), d.dot(g.v)); });
    const cross = (a, b, c) => (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x);
    const overlap = (a, b, c, d) => Math.max(Math.min(a.x, b.x), Math.min(c.x, d.x)) <= Math.min(Math.max(a.x, b.x), Math.max(c.x, d.x)) + 1e-8 && Math.max(Math.min(a.y, b.y), Math.min(c.y, d.y)) <= Math.min(Math.max(a.y, b.y), Math.max(c.y, d.y)) + 1e-8;
    for (let i = 0; i < contour.length; i++) for (let j = i + 1; j < contour.length; j++) {
      if (j === i + 1 || i === 0 && j === contour.length - 1) continue;
      const a = contour[i], b = contour[(i + 1) % contour.length], c = contour[j], d = contour[(j + 1) % contour.length];
      if (overlap(a, b, c, d) && cross(a, b, c) * cross(a, b, d) <= 1e-12 && cross(c, d, a) * cross(c, d, b) <= 1e-12) return fail('OUTLINE_SELF_INTERSECTS');
    }
    const faces = THREE.ShapeUtils.triangulateShape(contour, []);
    if (faces.length !== points.length - 2) return fail('OUTLINE_TRIANGULATION_FAILED');
    const indices = [];
    for (const face of faces) {
      const normal = points[face[1]].clone().sub(points[face[0]]).cross(points[face[2]].clone().sub(points[face[0]]));
      if (normal.dot(g.normal) < 0) indices.push(face[0], face[2], face[1]); else indices.push(...face);
    }
    const bounds = new THREE.Box2().setFromPoints(contour), size = bounds.getSize(new THREE.Vector2());
    if (size.x < .005 || size.y < .005) return fail('OUTLINE_AREA_TOO_SMALL');
    const data = {positions: points.flatMap(p => p.clone().sub(center).toArray()), uvs: contour.flatMap(p => [(p.x - bounds.min.x) / size.x, (p.y - bounds.min.y) / size.y]), indices};
    const audit = atelierTopologyAudit(data);
    if (!audit.ok || audit.zeroAreaFaces || audit.nonManifoldEdges || audit.oppositeWindingErrors) return fail('INVALID_OUTLINE_TOPOLOGY');
    return {ok: true, data, center, points};
  }
  function lassoBegin(id, options = {}) {
    const g = capture(id); if (!g.ok) return g;
    if ((g.part.sculptLassos?.length || 0) >= atelierLassoMaxRegions) return fail('NATIVE_LASSO_REGION_LIMIT_REACHED');
    if (g.original.userData?.refinedTriangles || g.part.refinementLayers?.some(l => l.enabled)) return fail('LASSO_REQUIRES_UNREFINED_MESH');
    if (g.mesh.isSkinnedMesh && !skinAtBindPose(g.mesh)) return fail('LASSO_REQUIRES_BIND_POSE');
    if (g.original.attributes.position.count > 24000) return fail('LASSO_ATTACHMENT_VERTEX_BUDGET_EXCEEDED');
    const normal = options.normal || [0, 0, 1];
    if (!vector(normal, 1) || Math.hypot(...normal) < .5) return fail('INVALID_LASSO_PLANE');
    const axis = new THREE.Vector3(...normal).normalize(), helper = Math.abs(axis.y) < .84 ? new THREE.Vector3(0, 1, 0) : new THREE.Vector3(1, 0, 0);
    const u = new THREE.Vector3().crossVectors(helper, axis).normalize(), v = new THREE.Vector3().crossVectors(axis, u).normalize();
    const line = new THREE.Line(new THREE.BufferGeometry(), new THREE.LineBasicMaterial({color: 0xffd66b, depthTest: false}));
    line.userData.se350SurfacePreview = true; line.renderOrder = 100; g.mesh.add(line);
    active = {...g, type: 'lasso', normal: axis, u, v, points: [], anchor: null, line, bindPoseSkin: !!g.mesh.isSkinnedMesh,
      name: String(options.name || 'VR surface region').slice(0, 90)};
    lastError = ''; lastAction = 'Trace a region on the selected surface';
    return {ok: true, id, mesh: g.mesh};
  }
  function lassoUpdate(point) {
    if (!valid('lasso')) return fail('NO_CURRENT_LASSO_GESTURE');
    if (!vector(point, 4)) return fail('INVALID_LASSO_POINT');
    const g = active, p = new THREE.Vector3(...point); if (!g.anchor) g.anchor = p.clone();
    p.addScaledVector(g.normal, -p.clone().sub(g.anchor).dot(g.normal));
    if (g.points.length && p.distanceTo(g.points[g.points.length - 1]) < .004) return {ok: true, sampled: false, pointCount: g.points.length};
    if (g.points.length >= 128) return {ok: true, sampled: false, pointCount: g.points.length, limit: true};
    g.points.push(p); const old = g.line.geometry; g.line.geometry = new THREE.BufferGeometry().setFromPoints(g.points); old.dispose(); atelierHDDirty = true;
    return {ok: true, sampled: true, pointCount: g.points.length};
  }
  function lassoEnd(commit = true) {
    if (!commit) return cancel();
    if (!valid('lasso', true)) return fail('NO_CURRENT_LASSO_GESTURE');
    const g = active, outline = outlineData(g); if (!outline.ok) { cancel(outline.reason); return outline; }
    const points = outline.points;
    // Retain corners with the largest influence while reducing a continuous
    // controller trace to the native 32 surface-attached control-pin budget.
    while (points.length > atelierLassoMaxPins) {
      let least = Infinity, index = -1;
      for (let i = 0; i < points.length; i++) {
        const a = points[(i + points.length - 1) % points.length], b = points[i], c = points[(i + 1) % points.length];
        const area = b.clone().sub(a).cross(c.clone().sub(a)).length();
        if (area < least) { least = area; index = i; }
      }
      points.splice(index, 1);
    }
    const pins = points.map(point => atelierLassoProjectXYZ(g.mesh, point.toArray()));
    if (pins.some(pin => !pin)) { cancel('LASSO_PIN_MISSED_SURFACE'); return fail('LASSO_PIN_MISSED_SURFACE'); }
    const region = {id: 'vr-region-' + Date.now().toString(36) + '-' + (++serial), name: g.name,
      pins, axis: g.normal.toArray(), feather: .03, morph: 0, enabled: true, resolution: atelierSculptResolution(g.part)};
    const candidate = {...g.part, sculptLassos: [...(g.part.sculptLassos || []), region]};
    if (!atelierLassoValid(candidate) || !atelierLassoPolygonValid(region) || !outlineData({...g, points: pins.map(pin => new THREE.Vector3(...pin.point))}).ok || !checkPart(candidate)) {
      cancel('INVALID_NATIVE_LASSO_REGION'); return fail('INVALID_NATIVE_LASSO_REGION');
    }
    active = null; restore(g); checkpoint(); g.part.sculptLassos = candidate.sculptLassos; selection = g.id; signalEdited(); atelierLassoActive = region.id;
    lastError = ''; lastAction = 'Saved surface region · Sculpt is limited to this region';
    return {ok: true, changed: true, id: g.id, regionId: region.id, pins: pins.length};
  }
  function lassoSelect(id, regionId = null) {
    if (!ready()) return fail('MODEL_EDITOR_NOT_OPEN');
    if (active) return fail('MODEL_GESTURE_ALREADY_ACTIVE');
    const part = partById(id); if (!part) return fail('MODEL_PART_NOT_FOUND');
    if (regionId !== null && !part.sculptLassos?.some(r => r.id === regionId && r.enabled)) return fail('SCULPT_REGION_NOT_FOUND');
    const selected = se340ModelBridge.select(id); if (!selected.ok) return selected;
    atelierLassoActive = regionId; lastError = ''; lastAction = regionId ? 'Surface region selected' : 'Sculpt entire surface'; atelierHDDirty = true;
    return {ok: true, selected: true, id, regionId};
  }
  function drawEnd(commit = true) {
    if (!commit) return cancel();
    if (!valid('draw')) return fail('NO_CURRENT_DRAW_GESTURE');
    const g = active, result = outlineData(g);
    if (!result.ok) { cancel(result.reason); return result; }
    if (model().parts.length >= MODEL_ATELIER_LIMIT) { cancel('MODEL_PART_LIMIT_REACHED'); return fail('MODEL_PART_LIMIT_REACHED'); }
    const part = {id: 'vr-outline-' + Date.now().toString(36) + '-' + (++serial), name: g.name, group: 'VR drawn geometry', kind: 'topologyMesh', color: g.color, material: 'matte',
      position: result.center.toArray(), rotation: [0, 0, 0], scale: [1, 1, 1], topologyMesh: result.data};
    if (!checkPart(part)) { cancel('INVALID_NATIVE_OUTLINE'); return fail('INVALID_NATIVE_OUTLINE'); }
    active = null; restore(g); checkpoint(); model().parts.push(part); selection = part.id; signalEdited();
    lastError = ''; lastAction = 'Created editable outline face · pull grip to extrude';
    return {ok: true, changed: true, id: part.id, vertices: part.topologyMesh.positions.length / 3, faces: part.topologyMesh.indices.length / 3};
  }
  function extrudeBegin(id) {
    const g = capture(id); if (!g.ok) return g;
    if (g.part.kind !== 'topologyMesh' || !atelierTopologyValid(g.part)) return fail('EXTRUDE_REQUIRES_NATIVE_OUTLINE_FACE');
    if (g.mesh.isSkinnedMesh && !skinAtBindPose(g.mesh)) return fail('EXTRUDE_REQUIRES_BIND_POSE');
    if (g.part.sculptVertexEdits?.length || g.part.sculptBrushes?.length || g.part.sculptLassos?.length || g.part.refinementLayers?.some(l => l.enabled)) return fail('EXTRUDE_REQUIRES_UNDEFORMED_OUTLINE');
    const t = g.part.topologyMesh, audit = atelierTopologyAudit(t), points = Array.from({length: t.positions.length / 3}, (_, i) => new THREE.Vector3(...t.positions.slice(i * 3, i * 3 + 3)));
    if (!audit.ok || audit.zeroAreaFaces || audit.nonManifoldEdges || audit.oppositeWindingErrors || audit.boundaryEdges !== points.length || t.indices.length / 3 !== points.length - 2) return fail('EXTRUDE_REQUIRES_SINGLE_OPEN_OUTLINE');
    const normal = points[t.indices[1]].clone().sub(points[t.indices[0]]).cross(points[t.indices[2]].clone().sub(points[t.indices[0]])).normalize();
    const origin = points[t.indices[0]];
    if (points.some(p => Math.abs(p.clone().sub(origin).dot(normal)) > 1e-5)) return fail('EXTRUDE_REQUIRES_PLANAR_OUTLINE');
    const boundary = [...audit.edges.values()].filter(e => e.length === 1).map(e => e[0]);
    const outgoing = new Map(boundary.map(e => [e.from, e.to])), visited = new Set(); let next = boundary[0].from;
    for (let i = 0; i < points.length; i++) { if (visited.has(next) || !outgoing.has(next)) return fail('EXTRUDE_REQUIRES_SINGLE_OPEN_OUTLINE'); visited.add(next); next = outgoing.get(next); }
    if (next !== boundary[0].from || visited.size !== points.length) return fail('EXTRUDE_REQUIRES_SINGLE_OPEN_OUTLINE');
    const preview = g.original.clone(); g.mesh.geometry = preview;
    active = {...g, type: 'extrude', preview, normal, boundary, next: null, depth: 0, bindPoseSkin: !!g.mesh.isSkinnedMesh}; lastError = ''; lastAction = 'Pull outline thickness';
    return {ok: true, id, normal: normal.toArray(), mesh: g.mesh};
  }
  function extrudeData(g, depth) {
    const t = g.part.topologyMesh, n = t.positions.length / 3, positions = [...t.positions], indices = [], uvs = [...t.uvs];
    for (let i = 0; i < n; i++) { positions.push(t.positions[i * 3] + g.normal.x * depth, t.positions[i * 3 + 1] + g.normal.y * depth, t.positions[i * 3 + 2] + g.normal.z * depth); uvs.push(t.uvs[i * 2] + .013, t.uvs[i * 2 + 1] + .027); }
    for (let i = 0; i < t.indices.length; i += 3) { const [a, b, c] = t.indices.slice(i, i + 3); indices.push(c, b, a, a + n, b + n, c + n); }
    for (const {from: a, to: b} of g.boundary) indices.push(a, b, b + n, a, b + n, a + n);
    if (depth < 0) for (let i = 0; i < indices.length; i += 3) [indices[i + 1], indices[i + 2]] = [indices[i + 2], indices[i + 1]];
    return {positions, indices, uvs};
  }
  function extrudeUpdate(depth) {
    if (!valid('extrude')) return fail('NO_CURRENT_EXTRUDE_GESTURE');
    if (!Number.isFinite(depth) || Math.abs(depth) > 4) return fail('EXTRUSION_DEPTH_OUT_OF_RANGE');
    const g = active;
    if (Math.abs(depth) < .003) { g.next = null; g.depth = depth; g.mesh.geometry = g.original; g.preview.dispose(); g.preview = g.original.clone(); g.mesh.geometry = g.preview; return {ok: true, changed: false}; }
    const data = extrudeData(g, depth), candidate = {...g.part, topologyMesh: data}; delete candidate.runtimeLOD;
    const audit = atelierTopologyAudit(data);
    if (!checkPart(candidate) || !audit.ok || audit.zeroAreaFaces || audit.boundaryEdges || audit.nonManifoldEdges || audit.oppositeWindingErrors) return fail('INVALID_NATIVE_EXTRUSION');
    const preview = atelierTopologyGeometry(candidate);
    if (g.bindPoseSkin) {
      // At bind pose the skin is locally identity. Duplicate boundary weights
      // for the transient top cap; native rebuild authors fresh spatial
      // weights for the saved extruded vertices on commit.
      for (const key of ['skinIndex', 'skinWeight']) {
        const attr = g.original.getAttribute(key), values = new attr.array.constructor(attr.array.length * 2);
        values.set(attr.array); values.set(attr.array, attr.array.length); preview.setAttribute(key, new THREE.BufferAttribute(values, attr.itemSize, attr.normalized));
      }
    }
    g.mesh.geometry = preview; g.preview.dispose(); g.preview = preview; g.next = data; g.depth = depth; atelierHDDirty = true;
    return {ok: true, changed: true, depth};
  }
  function extrudeEnd(commit = true) {
    if (!commit) return cancel();
    if (!valid('extrude', true)) return fail('NO_CURRENT_EXTRUDE_GESTURE');
    const g = active;
    if (!g.next) { cancel(); return {ok: true, changed: false}; }
    const candidate = {...g.part, topologyMesh: g.next}; delete candidate.runtimeLOD;
    if (!checkPart(candidate)) { cancel('INVALID_NATIVE_EXTRUSION'); return fail('INVALID_NATIVE_EXTRUSION'); }
    active = null; restore(g); checkpoint(); g.part.topologyMesh = g.next; delete g.part.runtimeLOD; selection = g.id; signalEdited();
    lastError = ''; lastAction = 'Committed outline thickness'; return {ok: true, changed: true, id: g.id, depth: g.depth};
  }
  const previousRender = renderParts;
  renderParts = function (...args) { if (active) cancel('MODEL_PROJECTION_REBUILT'); return previousRender.apply(this, args); };
  const previousClose = close;
  close = function (...args) { cancel(); return previousClose.apply(this, args); };
  return Object.freeze({sculptBegin, sculptUpdate, sculptEnd, lassoBegin, lassoUpdate, lassoEnd, lassoSelect, drawBegin, drawUpdate, drawEnd, extrudeBegin, extrudeUpdate, extrudeEnd, localHit, cancel,
    inspect: () => {
      if (active && !current(active)) cancel('MODEL_CHANGED_DURING_SURFACE_GESTURE');
      const part = partById(selection), region = part?.sculptLassos?.find(r => r.id === atelierLassoActive && r.enabled);
      return {selectedRegion: region ? {id: region.id, partId: part.id, axis: [...region.axis], pins: region.pins.map(pin => [...pin.point])} : null, selectedRegionId: part?.sculptLassos?.some(r => r.id === atelierLassoActive && r.enabled) ? atelierLassoActive : null, regions: (part?.sculptLassos || []).map(r => ({id: r.id, name: r.name, enabled: r.enabled})), active: active ? {type: active.type, id: active.id || null, operation: active.operation || null, pointCount: active.points?.length || 0, samples: active.samples || 0, changed: active.changed || !!active.next} : null, error: lastError, lastAction};
    }});
})();
/* SE350_MODEL_VR_SURFACE_END */
