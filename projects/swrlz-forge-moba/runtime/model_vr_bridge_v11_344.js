/* SE340_MODEL_VR_BRIDGE_START */
// This adapter lives inside ModelAtelier. The saved model and native history
// stay authoritative; a controller gesture previews only the derived mesh.
const se340ModelBridge = (() => {
  const fields = ['position', 'rotation', 'scale'];
  const modeField = {move: 'position', rotate: 'rotation', scale: 'scale'};
  let revision = 0, documentToken = 0, owner = null, identityRoot = null;
  let gesture = null, borrowed = null, lastError = '', lastAction = '', projectionCache = null;
  const copyTransform = part => Object.fromEntries(fields.map(key => [key, [...part[key]]]));
  const sameTransform = (a, b) => fields.every(key => a[key].every((n, i) => n === b[key][i]));
  const differs = (a, b) => fields.some(key => a[key].some((n, i) => Math.abs(n - b[key][i]) > 1e-6));
  function failure(reason) { lastError = reason; return {ok: false, reason, error: reason}; }
  function ready() { return !!(panel && !panel.hidden && renderer && world && modelRoot && model()?.parts); }
  function currentOwner() {
    return window.SWYRL_ENGINE_WORKSPACES?.usingScratch?.() ? model() : currentProject;
  }
  function identity() {
    const next = currentOwner();
    if (next !== owner || modelRoot !== identityRoot) {
      owner = next; identityRoot = modelRoot; documentToken++;
    }
    return model();
  }
  function sourceStillCurrent(g) {
    const active = model();
    return ready() && active === g.document && active.parts === g.parts &&
      partById(g.id) === g.part && modelRoot === g.root && revision === g.revision &&
      sameTransform(g.part, g.before);
  }
  function meshStillCurrent(g) {
    return modelRoot === g.root && g.mesh.parent === g.root &&
      g.mesh.userData?.atelierId === g.id;
  }
  function restorePreview(g) {
    // Remove our transient skin hook even if a newer document owns the view.
    if (g.skin) {
      g.skin.state.active = false;
      if (g.mesh.updateMatrixWorld === g.skin.hook) {
        if (g.skin.own) g.mesh.updateMatrixWorld = g.skin.state.original;
        else delete g.mesh.updateMatrixWorld;
      }
    }
    // Never restore descriptors or a replacement document. A geometry rebuild
    // removes its own old projection, so only restore the still-owned mesh.
    if (!sourceStillCurrent(g) || !meshStillCurrent(g)) return;
    g.mesh.position.copy(g.meshState.position);
    g.mesh.quaternion.copy(g.meshState.quaternion);
    g.mesh.scale.copy(g.meshState.scale);
    g.mesh.matrix.copy(g.meshState.matrix);
    g.mesh.matrixAutoUpdate = g.meshState.matrixAutoUpdate;
    g.mesh.matrixWorldNeedsUpdate = true;
    g.mesh.updateWorldMatrix?.(true, true);
    if (g.skin) g.mesh.bindMatrixInverse.copy(g.skin.state.inverse);
    atelierHDDirty = true;
  }
  function cancel(reason = '') {
    const previous = gesture;
    if (!previous) return {ok: true, changed: false, cancelled: false};
    gesture = null;
    restorePreview(previous);
    if (reason) lastError = reason;
    lastAction = 'Cancelled VR preview';
    return {ok: true, changed: false, cancelled: true, id: previous.id};
  }
  function validGesture() {
    if (!gesture) return false;
    identity();
    if (!sourceStillCurrent(gesture) || !meshStillCurrent(gesture)) {
      cancel('MODEL_CHANGED_DURING_GESTURE'); return false;
    }
    return true;
  }
  function matrixFor(transform) {
    return new THREE.Matrix4().compose(new THREE.Vector3(...transform.position),
      new THREE.Quaternion().setFromEuler(new THREE.Euler(...transform.rotation)),
      new THREE.Vector3(...transform.scale));
  }
  function applyPreview() {
    if (!validGesture()) return;
    const g = gesture;
    // Preserve native assembly placement A: (A * P) * inverse(P) * P-next.
    // Reapply just before XR drawing because an active native assembly may
    // have refreshed its own derived matrix since the previous XR frame.
    const next = g.meshState.matrix.clone().multiply(g.descriptorInverse).multiply(matrixFor(g.next));
    g.mesh.matrixAutoUpdate = false;
    g.mesh.matrix.copy(next); g.mesh.matrixWorldNeedsUpdate = true;
    g.mesh.updateWorldMatrix?.(true, true);
  }
  function hideNativeHelpers() {
    if (!borrowed) return;
    const live = new Set();
    borrowed.root.traverse(node => {
      if (!node.userData?.atelierHelper && !node.isBoxHelper && node.type !== 'BoxHelper') return;
      live.add(node);
      if (!borrowed.helpers.has(node)) borrowed.helpers.set(node, node.visible);
      node.visible = false;
    });
    // A BoxHelper can retain its old target mesh and large CPU geometry even
    // after native renderParts disposed that projection. Keep only live refs.
    for (const helper of borrowed.helpers.keys()) if (!live.has(helper)) borrowed.helpers.delete(helper);
  }
  function describe(id = selection) {
    const part = partById(id);
    return part ? {id: part.id, name: part.name, ...copyTransform(part)} : null;
  }
  function selectPart(id) {
    if (!ready()) return failure('MODEL_EDITOR_NOT_OPEN');
    if (gesture) cancel();
    if (id !== null && !partById(id)) return failure('MODEL_PART_NOT_FOUND');
    // VR selects one explicit native part, independently of a previously
    // armed desktop additive/group selection mode. No saved data changes.
    atelierMeshAdding = false; atelierGroupScope = 'child';
    // A repeated trigger or grip on the already-selected part must not
    // re-enter native selection/mesh rebuilding on the XR render thread.
    if (selection === id) {
      lastError = '';
      return {ok: true, unchanged: true, selectedId: selection, part: describe(selection)};
    }
    select(id); hideNativeHelpers(); lastError = '';
    lastAction = id ? 'Selected ' + partById(id).name : 'Cleared selection';
    return {ok: true, selectedId: selection, part: describe(selection)};
  }
  function begin(id, mode = 'move') {
    if (!ready()) return failure('MODEL_EDITOR_NOT_OPEN');
    if (!Object.hasOwn(modeField, mode)) return failure('UNSUPPORTED_MODEL_GESTURE');
    if (gesture) return failure('MODEL_GESTURE_ALREADY_ACTIVE');
    if (!partById(id)) return failure('INVALID_MODEL_PART');
    const picked = selectPart(id); if (!picked.ok) return picked;
    // Selection may change viewport modes and rebuild native projections.
    // Capture the mesh only after the native selection work has completed.
    const active = identity(), part = partById(id);
    if (!part || !checkPart(part)) return failure('INVALID_MODEL_PART');
    const mesh = modelRoot.children.find(node => node.isMesh && node.userData?.atelierId === id);
    if (!mesh) return failure('MODEL_PROJECTION_NOT_READY');
    if (mesh.matrixAutoUpdate) mesh.updateMatrix();
    modelRoot.updateWorldMatrix(true, true);
    if (mesh.isSkinnedMesh) mesh.updateMatrixWorld(true);
    // Topology/loft vertices may be stored away from their mesh origin.
    // Match the native modelling gizmo's geometry-centre pivot.
    if (mesh.isSkinnedMesh && typeof mesh.computeBoundingBox === 'function') mesh.computeBoundingBox();
    else if (!mesh.geometry.boundingBox) mesh.geometry.computeBoundingBox();
    const pivot = (mesh.isSkinnedMesh ? mesh.boundingBox : mesh.geometry.boundingBox)?.getCenter(new THREE.Vector3()) || new THREE.Vector3();
    const before = copyTransform(part);
    gesture = {id, mode, document: active, parts: active.parts, part, root: modelRoot,
      mesh, revision, before, pivot, next: copyTransform(part), fingerprint: JSON.stringify(part),
      descriptorInverse: matrixFor(before).invert(),
      meshState: {position: mesh.position.clone(), quaternion: mesh.quaternion.clone(),
        scale: mesh.scale.clone(), matrix: mesh.matrix.clone(), matrixAutoUpdate: mesh.matrixAutoUpdate}};
    if (mesh.isSkinnedMesh) {
      // Attached skins cancel a mesh-only delta through their inverse bind
      // matrix. Freeze only that inverse during this transient preview.
      const state = {active: true, inverse: mesh.bindMatrixInverse.clone(), original: mesh.updateMatrixWorld};
      const hook = function (...args) {
        const result = state.original.apply(this, args);
        if (state.active) this.bindMatrixInverse.copy(state.inverse);
        return result;
      };
      gesture.skin = {state, hook, own: Object.hasOwn(mesh, 'updateMatrixWorld')};
      mesh.updateMatrixWorld = hook;
    }
    lastError = ''; lastAction = 'Previewing VR ' + mode;
    return {ok: true, id, mode, part: describe(id)};
  }
  function update(candidate) {
    if (!validGesture()) return failure('NO_CURRENT_MODEL_GESTURE');
    if (!candidate || typeof candidate !== 'object' || Array.isArray(candidate) ||
        Object.keys(candidate).some(key => !fields.includes(key))) return failure('INVALID_MODEL_TRANSFORM');
    const g = gesture, next = copyTransform(g.next), activeField = modeField[g.mode];
    for (const key of fields) {
      if (!Object.hasOwn(candidate, key)) continue;
      const value = candidate[key];
      if (!Array.isArray(value) || value.length !== 3 ||
          value.some(n => typeof n !== 'number' || !Number.isFinite(n) || Math.abs(n) > 100) ||
          key === 'scale' && value.some(n => n <= .005 || n > 20)) return failure('MODEL_TRANSFORM_OUT_OF_RANGE');
      if (key !== activeField && value.some((n, i) => n !== g.before[key][i])) return failure('MODEL_GESTURE_MODE_MISMATCH');
      next[key] = [...value];
    }
    if (g.mode === 'rotate' || g.mode === 'scale') {
      const arm = transform => g.pivot.clone().multiply(new THREE.Vector3(...transform.scale))
        .applyQuaternion(new THREE.Quaternion().setFromEuler(new THREE.Euler(...transform.rotation)));
      const offset = arm(g.before).sub(arm(next));
      next.position = g.before.position.map((value, index) => value + offset.getComponent(index));
      if (next.position.some(value => !Number.isFinite(value) || Math.abs(value) > 100)) return failure('MODEL_TRANSFORM_OUT_OF_RANGE');
    }
    g.next = next; applyPreview(); lastError = '';
    return {ok: true, id: g.id, changed: differs(next, g.before), preview: copyTransform(next)};
  }
  function end(commit = true) {
    if (!gesture) return {ok: true, changed: false};
    if (!commit) return cancel();
    if (!validGesture()) return failure('MODEL_CHANGED_DURING_GESTURE');
    const g = gesture;
    if (JSON.stringify(g.part) !== g.fingerprint) {
      cancel('MODEL_PART_CHANGED_DURING_GESTURE'); return failure('MODEL_PART_CHANGED_DURING_GESTURE');
    }
    if (!differs(g.next, g.before)) { cancel(); return {ok: true, changed: false, id: g.id}; }
    const candidate = {...g.part, ...copyTransform(g.next)};
    if (!checkPart(candidate)) { cancel(); return failure('INVALID_NATIVE_MODEL_TRANSFORM'); }
    // Exactly one native checkpoint, at a validated commit. Hover, no-op,
    // cancellation and tracking loss do not consume Undo or erase Redo.
    restorePreview(g); checkpoint(); gesture = null;
    for (const key of fields) g.part[key] = [...candidate[key]];
    selection = g.id; signalEdited(); hideNativeHelpers();
    lastError = ''; lastAction = 'Committed VR ' + g.mode + ' · ' + g.part.name;
    return {ok: true, changed: true, id: g.id, part: describe(g.id)};
  }
  function projection() {
    const active = identity();
    if (gesture) applyPreview(); hideNativeHelpers();
    if (!projectionCache || projectionCache.root !== modelRoot || projectionCache.document !== active ||
        projectionCache.parts !== active?.parts || projectionCache.revision !== revision) {
      const byId = new Map((active?.parts || []).map(part => [part.id, part]));
      const meshes = (modelRoot?.children || []).filter(mesh => mesh.isMesh && byId.has(mesh.userData?.atelierId))
        .map(mesh => ({id: mesh.userData.atelierId, name: byId.get(mesh.userData.atelierId).name,
          mesh, selected: mesh.userData.atelierId === selection}));
      projectionCache = {root: modelRoot, document: active, parts: active?.parts, revision, meshes};
    }
    const meshes = projectionCache.meshes;
    for (const record of meshes) record.selected = record.id === selection;
    modelRoot?.updateWorldMatrix?.(true, true);
    return {ready: ready(), documentToken, revision, root: modelRoot, world, meshes};
  }
  function borrowRoot(parent) {
    if (!ready()) return failure('MODEL_EDITOR_NOT_OPEN');
    if (!parent?.isObject3D || parent === modelRoot) return failure('INVALID_XR_MODEL_PARENT');
    for (let node = parent; node; node = node.parent) if (node === modelRoot) return failure('INVALID_XR_MODEL_PARENT');
    if (borrowed) return borrowed.target === parent ? {ok: true, root: borrowed.root, documentToken} : failure('MODEL_ROOT_ALREADY_BORROWED');
    identity();
    if (modelRoot.matrixAutoUpdate) modelRoot.updateMatrix();
    borrowed = {root: modelRoot, target: parent, parent: modelRoot.parent,
      index: modelRoot.parent?.children.indexOf(modelRoot) ?? -1,
      position: modelRoot.position.clone(), quaternion: modelRoot.quaternion.clone(), scale: modelRoot.scale.clone(),
      matrix: modelRoot.matrix.clone(), matrixAutoUpdate: modelRoot.matrixAutoUpdate, helpers: new Map()};
    parent.add(modelRoot); hideNativeHelpers();
    return {ok: true, root: modelRoot, documentToken};
  }
  function releaseRoot() {
    cancel(); const old = borrowed; if (!old) return {ok: true};
    borrowed = null;
    for (const [helper, visible] of old.helpers) helper.visible = visible;
    old.helpers.clear();
    if (old.root !== modelRoot) {
      if (old.root.parent === old.target) old.root.removeFromParent();
      return failure('MODEL_ROOT_REPLACED');
    }
    if (old.root.parent && old.root.parent !== old.target) return failure('MODEL_ROOT_OWNERSHIP_CHANGED');
    old.root.removeFromParent();
    old.root.position.copy(old.position); old.root.quaternion.copy(old.quaternion); old.root.scale.copy(old.scale);
    old.root.matrix.copy(old.matrix); old.root.matrixAutoUpdate = old.matrixAutoUpdate;
    if (old.parent) {
      old.parent.add(old.root);
      const current = old.parent.children.indexOf(old.root);
      if (current >= 0 && old.index >= 0 && current !== old.index) {
        old.parent.children.splice(current, 1); old.parent.children.splice(Math.min(old.index, old.parent.children.length), 0, old.root);
      }
    }
    old.root.matrixWorldNeedsUpdate = true; old.root.updateWorldMatrix?.(true, true); atelierHDDirty = true;
    return {ok: true};
  }
  function history(backward) {
    if (!ready()) return failure('MODEL_EDITOR_NOT_OPEN');
    cancel();
    if (!(backward ? undo : redo).length) return {ok: true, changed: false};
    historyStep(backward); identity(); hideNativeHelpers(); lastError = '';
    lastAction = backward ? 'Undo model edit' : 'Redo model edit';
    return {ok: true, changed: true};
  }
  const nativeRenderParts = renderParts;
  renderParts = function (...args) {
    if (gesture) cancel('MODEL_PROJECTION_REBUILT');
    const result = nativeRenderParts.apply(this, args); revision++; hideNativeHelpers(); return result;
  };
  const nativeClose = close;
  close = function (...args) { cancel(); releaseRoot(); return nativeClose.apply(this, args); };
  return Object.freeze({projection, describe, select: selectPart, begin, update, end, cancel,
    borrowRoot, releaseRoot, isBorrowed: () => !!borrowed && borrowed.root === modelRoot,
    undo: () => history(true), redo: () => history(false),
    inspect: () => {
      if (gesture) validGesture(); else identity();
      return {open: ready(), documentToken, revision, partCount: model()?.parts?.length || 0,
        selectedId: selection, canUndo: undo.length > 0, canRedo: redo.length > 0,
        undoDepth: undo.length, redoDepth: redo.length,
        gesture: gesture ? {id: gesture.id, mode: gesture.mode, changed: differs(gesture.next, gesture.before)} : null,
        borrowed: !!borrowed, nativeParentRestored: !!modelRoot && modelRoot.parent === world,
        error: lastError, lastAction};
    }});
})();
/* SE340_MODEL_VR_BRIDGE_END */
