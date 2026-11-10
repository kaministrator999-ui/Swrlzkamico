/* SE390_MODEL_VR_QUICK_CREATE_START */
// Native Model Atelier creation transactions. Controller ghosts stay outside
// the document; only a validated confirmation or duplicate writes history.
const se390ModelCreate = (() => {
  const kinds = new Set(['box', 'sphere', 'cylinder', 'cone']);
  const labels = {box: 'Cube', sphere: 'Sphere', cylinder: 'Cylinder', cone: 'Cone'};
  const editable = ['position', 'rotation', 'scale', 'name', 'color', 'material'];
  const records = new WeakMap();
  let pending = null, serial = 0, lastError = '', lastAction = '';
  const clone = value => structuredClone(value);
  const finiteVector = (value, limit = 100) => Array.isArray(value) && value.length === 3 &&
    value.every(n => typeof n === 'number' && Number.isFinite(n) && Math.abs(n) <= limit);
  const validField = (key, value) => ['position', 'rotation', 'scale'].includes(key) ? finiteVector(value) :
    key === 'name' ? typeof value === 'string' && value.trim().length > 0 && value.length <= 100 :
    key === 'color' ? typeof value === 'string' && /^#[0-9a-fA-F]{6}$/.test(value) :
    key === 'material' ? typeof value === 'string' && MODEL_ATELIER_MATERIALS.includes(value) : false;
  const fail = reason => { lastError = reason; return {ok: false, reason, error: reason}; };
  function nativeState() {
    const native = se340ModelBridge.inspect();
    return native.open && model()?.parts && modelRoot ? native : null;
  }
  function busy(native) {
    return !!native?.gesture || !!se350ModelTools.inspect().gesture || !!se350ModelSurface.inspect().active;
  }
  function newId(prefix) {
    let id;
    do {
      const suffix = typeof crypto?.randomUUID === 'function' ? crypto.randomUUID() : Date.now().toString(36) + '-' + (++serial).toString(36);
      id = prefix + suffix;
    } while (partById(id));
    return id;
  }
  function cancel(handle, reason = '') {
    if (typeof handle === 'string') { reason = handle; handle = undefined; }
    const target = handle === undefined ? pending?.handle : handle;
    const record = target && typeof target === 'object' ? records.get(target) : null;
    if (!record) return {ok: true, changed: false, cancelled: false};
    records.delete(target); if (pending === record) pending = null;
    if (reason) lastError = reason;
    lastAction = 'Creation preview canceled';
    return {ok: true, changed: false, cancelled: true};
  }
  function current(record, strict = false) {
    const native = nativeState();
    return !!native && model() === record.document && model().parts === record.parts && modelRoot === record.root &&
      native.documentToken === record.documentToken && native.revision === record.revision &&
      model().parts.length === record.sources.length && record.sources.every((part, index) => model().parts[index] === part) &&
      (!strict || JSON.stringify(model()) === record.fingerprint);
  }
  function candidate(record) {
    const source = record.handle.part;
    if (!source || source.kind !== record.base.kind || !kinds.has(source.kind)) return null;
    const part = clone(record.base);
    for (const key of editable) {
      if (Object.hasOwn(source, key)) {
        if (!validField(key, source[key])) return null;
        part[key] = Array.isArray(source[key]) ? [...source[key]] : source[key];
      }
    }
    if (typeof part.name !== 'string' || !part.name.trim() || part.name.length > 100 ||
        !['position', 'rotation', 'scale'].every(key => finiteVector(part[key])) || !checkPart(part)) return null;
    return part;
  }
  function draft(kind, options = {}) {
    const native = nativeState();
    if (!native) return fail('MODEL_EDITOR_NOT_OPEN');
    if (busy(native)) return fail('MODEL_GESTURE_ALREADY_ACTIVE');
    if (!kinds.has(kind) || !options || typeof options !== 'object' || Array.isArray(options)) return fail('INVALID_CREATE_PRIMITIVE');
    if (model().parts.length >= MODEL_ATELIER_LIMIT) return fail('MODEL_PART_LIMIT_REACHED');
    const base = {id: newId('vr-preview-'), name: 'VR ' + labels[kind], kind,
      group: 'VR created geometry', position: [0, 0, 0], rotation: [0, 0, 0], scale: [.25, .25, .25],
      color: '#a58bdf', material: 'matte'};
    for (const key of editable) if (Object.hasOwn(options, key)) {
      if (!validField(key, options[key])) return fail('INVALID_NATIVE_CREATE_PART');
      base[key] = Array.isArray(options[key]) ? [...options[key]] : options[key];
    }
    const handle = Object.freeze({ok: true, kind, part: clone(base), documentToken: native.documentToken, revision: native.revision});
    const record = {handle, base, document: model(), parts: model().parts, root: modelRoot,
      documentToken: native.documentToken, revision: native.revision,
      sources: [...model().parts], fingerprint: JSON.stringify(model())};
    if (!candidate(record)) return fail('INVALID_NATIVE_CREATE_PART');
    cancel(); records.set(handle, record); pending = record;
    lastError = ''; lastAction = 'Previewing ' + labels[kind];
    return handle;
  }
  function previewGeometry(handle) {
    const record = handle && typeof handle === 'object' ? records.get(handle) : null;
    if (!record || !current(record)) return fail('MODEL_CREATE_PREVIEW_CHANGED');
    const part = candidate(record); if (!part) return fail('INVALID_NATIVE_CREATE_PART');
    // Return the native unscaled primitive geometry. Its coordinate system and
    // proportions match the exact factory used by the ordinary model rebuild.
    const geometry = atelierCourierBaseGeometry(part);
    if (!geometry?.isBufferGeometry) { geometry?.dispose?.(); return fail('MODEL_CREATE_GEOMETRY_UNAVAILABLE'); }
    return {ok: true, geometry, part: clone(part)};
  }
  function selectCreated(ids) {
    atelierMeshIds = [...ids]; selection = ids.at(-1) || null;
    se350ModelTools.syncSelection();
  }
  function commit(handle, expectedDocToken = handle?.documentToken) {
    const record = handle && typeof handle === 'object' ? records.get(handle) : null;
    if (!record) return fail('MODEL_CREATE_PREVIEW_NOT_FOUND');
    const native = nativeState();
    if (!native || expectedDocToken !== record.documentToken || !current(record, true)) {
      cancel(handle); return fail('MODEL_CHANGED_DURING_CREATE_PREVIEW');
    }
    if (busy(native)) return fail('MODEL_GESTURE_ALREADY_ACTIVE');
    if (model().parts.length >= MODEL_ATELIER_LIMIT) return fail('MODEL_PART_LIMIT_REACHED');
    const part = candidate(record); if (!part) return fail('INVALID_NATIVE_CREATE_PART');
    part.id = newId('vr-create-');
    if (!checkPart(part)) return fail('INVALID_NATIVE_CREATE_PART');
    records.delete(handle); if (pending === record) pending = null;
    checkpoint(); model().parts.push(part); selectCreated([part.id]); signalEdited();
    lastError = ''; lastAction = 'Created ' + part.name;
    return {ok: true, changed: true, id: part.id, ids: [part.id], kind: part.kind, name: part.name, part: clone(part)};
  }
  function duplicate(ids, options = {}) {
    if (Array.isArray(options)) options = {translation: options};
    const native = nativeState();
    if (!native) return fail('MODEL_EDITOR_NOT_OPEN');
    if (busy(native) || pending) return fail('MODEL_GESTURE_ALREADY_ACTIVE');
    if (!options || typeof options !== 'object' || Array.isArray(options) ||
        !finiteVector(options.translation || [0, 0, 0])) return fail('INVALID_DUPLICATE_TRANSLATION');
    if (options.documentToken !== undefined && options.documentToken !== native.documentToken) return fail('MODEL_CHANGED_BEFORE_DUPLICATE');
    if (!Array.isArray(ids) || !ids.length || ids.length > 32 || new Set(ids).size !== ids.length || ids.some(id => typeof id !== 'string' || !partById(id)))
      return fail('INVALID_MODEL_SELECTION');
    if (model().parts.length + ids.length > MODEL_ATELIER_LIMIT) return fail('MODEL_PART_LIMIT_REACHED');
    const projection = se340ModelBridge.projection(), translation = new THREE.Vector3(...(options.translation || [0, 0, 0]));
    modelRoot.updateWorldMatrix(true, true);
    const copies = [], reserved = new Set(model().parts.map(part => part.id));
    for (const id of ids) {
      const source = partById(id), mesh = projection.meshes.find(entry => entry.id === id)?.mesh;
      if (!source || !checkPart(source) || !mesh || mesh.parent !== modelRoot) return fail('MODEL_PROJECTION_NOT_READY');
      if (mesh.matrixAutoUpdate) mesh.updateMatrix();
      const descriptor = new THREE.Matrix4().compose(new THREE.Vector3(...source.position),
        new THREE.Quaternion().setFromEuler(new THREE.Euler(...source.rotation)), new THREE.Vector3(...source.scale));
      const assembly = mesh.matrix.clone().multiply(descriptor.invert());
      if (!Number.isFinite(assembly.determinant()) || Math.abs(assembly.determinant()) < 1e-12) return fail('MODEL_TRANSFORM_BASIS_INVALID');
      // Keep the same native assembly group. Convert the root-local requested
      // displacement into its descriptor basis; cloning never bakes a rig pose.
      const inverse = assembly.invert(), delta = translation.clone().applyMatrix4(inverse).sub(new THREE.Vector3().applyMatrix4(inverse));
      const part = clone(source); do { part.id = newId('vr-copy-'); } while (reserved.has(part.id)); reserved.add(part.id);
      part.name = (String(source.name || 'Mesh').slice(0, 94) + ' copy').slice(0, 100);
      part.position = source.position.map((value, index) => value + delta.getComponent(index));
      if (!finiteVector(part.position) || !checkPart(part)) return fail('INVALID_NATIVE_DUPLICATE_PART');
      copies.push(part);
    }
    checkpoint(); model().parts.push(...copies); selectCreated(copies.map(part => part.id)); signalEdited();
    lastError = ''; lastAction = 'Duplicated ' + copies.length + ' selected meshes';
    return {ok: true, changed: true, ids: copies.map(part => part.id), parts: copies.map(clone)};
  }
  const previousClose = close;
  close = function (...args) { cancel(undefined, 'MODEL_EDITOR_CLOSED'); return previousClose.apply(this, args); };
  return Object.freeze({draft, previewGeometry, commit, duplicate, cancel,
    inspect: () => {
      if (pending && !current(pending)) cancel(undefined, 'MODEL_CHANGED_DURING_CREATE_PREVIEW');
      return {pending: pending ? {kind: pending.base.kind, documentToken: pending.documentToken, revision: pending.revision} : null,
        error: lastError, lastAction};
    }});
})();
/* SE390_MODEL_VR_QUICK_CREATE_END */
