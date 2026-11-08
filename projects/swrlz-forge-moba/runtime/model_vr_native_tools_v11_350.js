/* SE350_MODEL_VR_NATIVE_TOOLS_START */
// Native, transient multi-selection and group transforms. The XR workspace
// supplies root-local controller deltas; only a validated release edits data.
const se350ModelTools = (() => {
  const fields = ['position', 'rotation', 'scale'];
  let active = null, lastError = '', lastAction = '';
  const copy = part => Object.fromEntries(fields.map(key => [key, [...part[key]]]));
  const matrixFor = part => new THREE.Matrix4().compose(new THREE.Vector3(...part.position),
    new THREE.Quaternion().setFromEuler(new THREE.Euler(...part.rotation)), new THREE.Vector3(...part.scale));
  const failure = reason => { lastError = reason; return {ok: false, reason, error: reason}; };
  const changed = (a, b) => fields.some(key => a[key].some((n, i) => Math.abs(n - b[key][i]) > 1e-6));
  const finiteArray = (value, length, limit = 100) => Array.isArray(value) && value.length === length &&
    value.every(n => typeof n === 'number' && Number.isFinite(n) && Math.abs(n) <= limit);
  function nativeIds() {
    const valid = new Set(model()?.parts?.map(part => part.id) || []);
    atelierMeshIds = [...new Set(atelierMeshIds)].filter(id => valid.has(id)).slice(0, 32);
    if (!atelierMeshIds.length && valid.has(selection)) atelierMeshIds = [selection];
    if (!valid.has(selection) || !atelierMeshIds.includes(selection)) selection = atelierMeshIds.at(-1) || null;
    return [...atelierMeshIds];
  }
  function syncSelection() {
    nativeIds(); atelierGroupScope = 'child'; atelierGroupCurrent = null;
    atelierMeshAdding = atelierMeshIds.length > 1;
    // Do not enter native select(), which can rebuild a large skinned model.
    // The next native inspector refresh reads these same authoritative IDs.
    atelierHDDirty = true;
  }
  function groupPivot(ids, entries) {
    const root = modelRoot, bounds = new THREE.Box3(), inverse = root.matrixWorld.clone().invert();
    for (const entry of entries) {
      if (!ids.includes(entry.id)) continue;
      const mesh = entry.mesh;
      if (!mesh.geometry?.boundingBox) mesh.geometry?.computeBoundingBox?.();
      const local = mesh.isSkinnedMesh && mesh.boundingBox && !mesh.boundingBox.isEmpty()
        ? mesh.boundingBox : mesh.geometry?.boundingBox;
      if (!local || local.isEmpty()) continue;
      const box = local.clone().applyMatrix4(inverse.clone().multiply(mesh.matrixWorld));
      bounds.union(box);
    }
    return bounds.isEmpty() ? new THREE.Vector3() : bounds.getCenter(new THREE.Vector3());
  }
  function selectionSummary() {
    const ids = nativeIds(), projection = se340ModelBridge.projection();
    return {ids, primaryId: selection, pivot: projection.ready && ids.length
      ? groupPivot(ids, projection.meshes).toArray() : null};
  }
  function selectPart(id, options = {}) {
    if (!se340ModelBridge.inspect().open) return failure('MODEL_EDITOR_NOT_OPEN');
    if (active || se340ModelBridge.inspect().gesture) return failure('MODEL_GESTURE_ALREADY_ACTIVE');
    if (id !== null && !partById(id)) return failure('MODEL_PART_NOT_FOUND');
    let ids = nativeIds();
    if (options.additive && id !== null) {
      if (ids.includes(id)) ids = ids.filter(value => value !== id);
      else if (ids.length < 32) ids.push(id);
      else return failure('MODEL_SELECTION_LIMIT_32');
    } else ids = id === null ? [] : [id];
    atelierMeshIds = ids; selection = ids.includes(id) ? id : ids.at(-1) || null;
    syncSelection(); lastError = ''; lastAction = ids.length + ' selected model parts';
    return {ok: true, ...selectionSummary()};
  }
  function sourceCurrent(g) {
    const native = se340ModelBridge.inspect();
    return native.open && native.documentToken === g.documentToken && native.revision === g.revision &&
      model() === g.document && model()?.parts === g.parts && modelRoot === g.root &&
      g.entries.every(entry => partById(entry.id) === entry.part &&
        fields.every(key => entry.before[key].every((value, index) => entry.part[key]?.[index] === value)) && entry.mesh.parent === g.root &&
        entry.mesh.userData?.atelierId === entry.id);
  }
  function restoreEntry(entry, root) {
    if (entry.skin) {
      entry.skin.state.active = false;
      if (entry.mesh.updateMatrixWorld === entry.skin.hook) {
        if (entry.skin.own) entry.mesh.updateMatrixWorld = entry.skin.state.original;
        else delete entry.mesh.updateMatrixWorld;
      }
    }
    if (entry.mesh.parent !== root || entry.mesh.userData?.atelierId !== entry.id) return;
    // Restore only a matrix still owned by this preview. An independent edit
    // must never have its newer derived matrix overwritten by cancellation.
    if (entry.previewMatrix && !entry.mesh.matrix.equals(entry.previewMatrix)) return;
    const old = entry.meshState, mesh = entry.mesh;
    mesh.position.copy(old.position); mesh.quaternion.copy(old.quaternion); mesh.scale.copy(old.scale);
    mesh.matrix.copy(old.matrix); mesh.matrixAutoUpdate = old.matrixAutoUpdate;
    mesh.matrixWorldNeedsUpdate = true; mesh.updateWorldMatrix?.(true, true);
    if (entry.skin) mesh.bindMatrixInverse.copy(entry.skin.state.inverse);
  }
  function cancel(reason = '') {
    const previous = active; active = null;
    if (!previous) return {ok: true, changed: false, cancelled: false};
    for (const entry of previous.entries) restoreEntry(entry, previous.root);
    atelierHDDirty = true; if (reason) lastError = reason;
    lastAction = 'Cancelled VR group preview';
    return {ok: true, changed: false, cancelled: true};
  }
  function valid() {
    if (!active) return false;
    if (!sourceCurrent(active)) { cancel('MODEL_CHANGED_DURING_GESTURE'); return false; }
    return true;
  }
  function beginGroup(ids = nativeIds(), mode = 'move', pivot = null) {
    const native = se340ModelBridge.inspect();
    if (!native.open) return failure('MODEL_EDITOR_NOT_OPEN');
    if (active || native.gesture) return failure('MODEL_GESTURE_ALREADY_ACTIVE');
    if (!['move', 'rotate', 'scale', 'two-hand'].includes(mode)) return failure('UNSUPPORTED_MODEL_GESTURE');
    if (!Array.isArray(ids) || !ids.length || ids.length > 32 || new Set(ids).size !== ids.length ||
        ids.some(id => !partById(id))) return failure('INVALID_MODEL_SELECTION');
    if (pivot !== null && !finiteArray(pivot, 3)) return failure('INVALID_MODEL_PIVOT');
    const projection = se340ModelBridge.projection();
    modelRoot.updateWorldMatrix(true, true);
    const entries = [];
    for (const id of ids) {
      const part = partById(id), mesh = projection.meshes.find(entry => entry.id === id)?.mesh;
      if (!part || !checkPart(part) || !mesh || mesh.parent !== modelRoot) return failure('MODEL_PROJECTION_NOT_READY');
      if (mesh.matrixAutoUpdate) mesh.updateMatrix();
      if (mesh.isSkinnedMesh) mesh.updateMatrixWorld(true);
      const before = copy(part), state = {position: mesh.position.clone(), quaternion: mesh.quaternion.clone(),
        scale: mesh.scale.clone(), matrix: mesh.matrix.clone(), matrixAutoUpdate: mesh.matrixAutoUpdate};
      const assembly = state.matrix.clone().multiply(matrixFor(before).invert());
      if (!Number.isFinite(assembly.determinant()) || Math.abs(assembly.determinant()) < 1e-12)
        return failure('MODEL_TRANSFORM_BASIS_INVALID');
      entries.push({id, part, mesh, before, next: copy(part), fingerprint: JSON.stringify(part),
        meshState: state, assemblyInverse: assembly.invert(), previewMatrix: state.matrix.clone()});
    }
    const center = pivot ? new THREE.Vector3(...pivot) : groupPivot(ids, projection.meshes);
    active = {ids: [...ids], mode, pivot: center, entries, document: model(), parts: model().parts,
      root: modelRoot, documentToken: native.documentToken, revision: native.revision};
    for (const entry of entries) if (entry.mesh.isSkinnedMesh) {
      const mesh = entry.mesh, state = {active: true, inverse: mesh.bindMatrixInverse.clone(), original: mesh.updateMatrixWorld};
      const hook = function (...args) { const result = state.original.apply(this, args);
        if (state.active) this.bindMatrixInverse.copy(state.inverse); return result; };
      entry.skin = {state, hook, own: Object.hasOwn(mesh, 'updateMatrixWorld')}; mesh.updateMatrixWorld = hook;
    }
    atelierMeshIds = [...ids]; selection = ids.includes(selection) ? selection : ids.at(-1); syncSelection();
    lastError = ''; lastAction = 'Previewing ' + mode + ' · ' + ids.length + ' parts';
    return {ok: true, ids: [...ids], mode, pivot: center.toArray()};
  }
  function applyPreview() {
    if (!valid()) return;
    for (const entry of active.entries) {
      entry.mesh.matrixAutoUpdate = false; entry.mesh.matrix.copy(entry.previewMatrix);
      entry.mesh.matrixWorldNeedsUpdate = true; entry.mesh.updateWorldMatrix?.(true, true);
    }
  }
  function updateGroup(delta = {}) {
    if (!valid()) return failure('NO_CURRENT_MODEL_GESTURE');
    if (!delta || typeof delta !== 'object' || Array.isArray(delta) ||
        Object.keys(delta).some(key => !['translation', 'rotation', 'scale'].includes(key))) return failure('INVALID_MODEL_TRANSFORM');
    const translation = delta.translation ?? [0, 0, 0], rotation = delta.rotation ?? [0, 0, 0, 1], scale = delta.scale ?? 1;
    if (!finiteArray(translation, 3) || !finiteArray(rotation, 4, 1.00001) ||
        typeof scale !== 'number' || !Number.isFinite(scale) || scale < .01 || scale > 100)
      return failure('MODEL_TRANSFORM_OUT_OF_RANGE');
    const quaternion = new THREE.Quaternion(...rotation);
    if (Math.abs(quaternion.lengthSq() - 1) > 1e-4) return failure('INVALID_MODEL_ROTATION');
    quaternion.normalize();
    const moving = translation.some(value => Math.abs(value) > 1e-12),
      turning = 1 - Math.abs(quaternion.w) > 1e-12, resizing = Math.abs(scale - 1) > 1e-12;
    if (active.mode !== 'two-hand' && (moving && active.mode !== 'move' || turning && active.mode !== 'rotate' || resizing && active.mode !== 'scale'))
      return failure('MODEL_GESTURE_MODE_MISMATCH');
    if (!moving && !turning && !resizing) {
      for (const entry of active.entries) { entry.next = copy(entry.before); entry.previewMatrix = entry.meshState.matrix.clone(); }
      applyPreview(); lastError = ''; return {ok: true, changed: false, ids: [...active.ids]};
    }
    const transform = new THREE.Matrix4().makeTranslation(...translation)
      .multiply(new THREE.Matrix4().makeTranslation(...active.pivot.toArray()))
      .multiply(new THREE.Matrix4().makeRotationFromQuaternion(quaternion))
      .multiply(new THREE.Matrix4().makeScale(scale, scale, scale))
      .multiply(new THREE.Matrix4().makeTranslation(...active.pivot.clone().negate().toArray()));
    const candidates = [];
    for (const entry of active.entries) {
      const preview = transform.clone().multiply(entry.meshState.matrix);
      const descriptor = entry.assemblyInverse.clone().multiply(preview);
      const p = new THREE.Vector3(), q = new THREE.Quaternion(), s = new THREE.Vector3(); descriptor.decompose(p, q, s);
      const reconstructed = new THREE.Matrix4().compose(p, q, s);
      const tolerance = Math.max(1, ...descriptor.elements.map(Math.abs)) * 1e-7;
      if (descriptor.elements.some((value, index) => !Number.isFinite(value) || Math.abs(value - reconstructed.elements[index]) > tolerance))
        return failure('MODEL_GROUP_SHEAR_UNSUPPORTED');
      const next = {position: p.toArray(), rotation: new THREE.Euler().setFromQuaternion(q).toArray().slice(0, 3), scale: s.toArray()};
      // Translation has no angular/scale effect, and uniform scaling has no
      // angular effect. Keep the original Euler representation exactly.
      if (!turning) next.rotation = [...entry.before.rotation];
      if (!turning && !resizing) next.scale = [...entry.before.scale];
      if (fields.some(key => !finiteArray(next[key], 3)) || next.scale.some(value => value <= .005 || value > 20) ||
          !checkPart({...entry.part, ...next})) return failure('MODEL_TRANSFORM_OUT_OF_RANGE');
      candidates.push({entry, next, preview});
    }
    for (const {entry, next, preview} of candidates) { entry.next = next; entry.previewMatrix = preview; }
    applyPreview(); lastError = '';
    return {ok: true, changed: active.entries.some(entry => changed(entry.next, entry.before)), ids: [...active.ids]};
  }
  function endGroup(commit = true) {
    if (!active) return {ok: true, changed: false};
    if (!commit) return cancel();
    if (!valid()) return failure('MODEL_CHANGED_DURING_GESTURE');
    const previous = active;
    // Full mesh descriptors can contain thousands of vertices. Fingerprint
    // them only at begin/commit; frames use identities, revision and TRS.
    if (previous.entries.some(entry => JSON.stringify(entry.part) !== entry.fingerprint)) {
      cancel('MODEL_PART_CHANGED_DURING_GESTURE'); return failure('MODEL_PART_CHANGED_DURING_GESTURE');
    }
    if (!previous.entries.some(entry => changed(entry.next, entry.before))) { cancel(); return {ok: true, changed: false}; }
    if (previous.entries.some(entry => !checkPart({...entry.part, ...entry.next}))) {
      cancel('INVALID_NATIVE_MODEL_TRANSFORM'); return failure('INVALID_NATIVE_MODEL_TRANSFORM');
    }
    // Restore before checkpoint, then change every descriptor atomically.
    // signalEdited rebuilds once; its wrapper sees no remaining gesture.
    for (const entry of previous.entries) restoreEntry(entry, previous.root);
    active = null; checkpoint();
    for (const entry of previous.entries) for (const field of fields) entry.part[field] = [...entry.next[field]];
    signalEdited(); syncSelection(); lastError = '';
    lastAction = 'Committed ' + previous.mode + ' · ' + previous.ids.length + ' parts';
    return {ok: true, changed: true, ids: [...previous.ids]};
  }
  const originalRender = renderParts;
  renderParts = function (...args) { if (active) cancel('MODEL_PROJECTION_REBUILT'); return originalRender.apply(this, args); };
  const originalClose = close;
  close = function (...args) { cancel(); return originalClose.apply(this, args); };
  function refreshSelection() {
    if (!se340ModelBridge.inspect().open) return {ok: true, refreshed: false};
    if (se340ModelBridge.isBorrowed()) return failure('MODEL_ROOT_STILL_BORROWED');
    cancel(); syncSelection(); renderParts(); refreshList(); refreshInspector();
    return {ok: true, refreshed: true};
  }
  return Object.freeze({selection: selectionSummary, select: selectPart, beginGroup, updateGroup, endGroup, cancel, syncSelection, refreshSelection,
    projection: () => { const result = se340ModelBridge.projection(); if (active) applyPreview();
      const ids = new Set(nativeIds()); for (const entry of result.meshes) entry.selected = ids.has(entry.id); return result; },
    inspect: () => { if (active) valid(); return {selectedIds: nativeIds(), primaryId: selection,
      gesture: active ? {ids: [...active.ids], mode: active.mode, pivot: active.pivot.toArray(),
        changed: active.entries.some(entry => changed(entry.next, entry.before))} : null, error: lastError, lastAction}; }});
})();
/* SE350_MODEL_VR_NATIVE_TOOLS_END */
