/* SE410_MODEL_ACCESSORY_BRIDGE_START */
// Accessory recipes remain disposable previews until one native transaction
// inserts all of their editable topology components. No recipe-only save fields.
const se410ModelAccessory = (() => {
  const records = new WeakMap();
  let pending = null, serial = 0, lastError = '', lastAction = '';
  const clone = value => structuredClone(value);
  const fail = reason => { lastError = reason; return {ok: false, reason, error: reason}; };
  const vector = value => Array.isArray(value) && value.length === 3 &&
    value.every(n => typeof n === 'number' && Number.isFinite(n) && Math.abs(n) <= 100);
  function nativeState() {
    const native = se340ModelBridge.inspect();
    return native.open && Array.isArray(model()?.parts) && modelRoot ? native : null;
  }
  function busy(native) {
    return !!native?.gesture || !!se350ModelTools.inspect().gesture || !!se350ModelSurface.inspect().active ||
      !!se390ModelCreate.inspect().pending;
  }
  function newId(prefix, reserved = new Set()) {
    let id;
    do {
      const suffix = typeof crypto?.randomUUID === 'function' ? crypto.randomUUID() : Date.now().toString(36) + '-' + (++serial).toString(36);
      id = prefix + suffix;
    } while (partById(id) || reserved.has(id));
    reserved.add(id); return id;
  }
  function transformOf(value = {}) {
    if (!value || typeof value !== 'object' || Array.isArray(value)) return null;
    const result = {position: value.position ?? [0, 0, 0], rotation: value.rotation ?? [0, 0, 0], scale: value.scale ?? [1, 1, 1]};
    if (!Object.values(result).every(vector) || result.scale.some(n => n <= .005 || n > 20) ||
        result.scale.some(n => Math.abs(n - result.scale[0]) > 1e-9)) return null;
    return {position: [...result.position], rotation: [...result.rotation], scale: [...result.scale]};
  }
  function current(record, strict = false) {
    const native = nativeState();
    return !!native && model() === record.document && model().parts === record.parts && modelRoot === record.root &&
      native.documentToken === record.documentToken && native.revision === record.revision &&
      model().parts.length === record.sources.length && record.sources.every((part, i) => model().parts[i] === part) &&
      (!strict || JSON.stringify(model()) === record.fingerprint);
  }
  function cancel(handle, reason = '') {
    if (typeof handle === 'string') { reason = handle; handle = undefined; }
    const target = handle === undefined ? pending?.handle : handle;
    const record = target && typeof target === 'object' ? records.get(target) : null;
    if (!record) return {ok: true, changed: false, cancelled: false};
    records.delete(target); if (pending === record) pending = null;
    if (reason) lastError = reason;
    lastAction = 'Accessory preview canceled';
    return {ok: true, changed: false, cancelled: true};
  }
  function recipe(params) {
    let built;
    try { built = se410BuildAccessoryRecipe(params); } catch { return null; }
    if (!built?.ok || !Array.isArray(built.parts) || !built.parts.length || built.parts.length > 32 ||
        !built.parameters || typeof built.parameters !== 'object' || Array.isArray(built.parameters)) return null;
    const reserved = new Set(), groups = new Set(model().parts.map(part => part.group));
    let group = 'Hip bag', suffix = 1;
    while (groups.has(group)) group = 'Hip bag ' + (++suffix);
    const components = [];
    for (const source of built.parts) {
      if (!source || source.kind !== 'topologyMesh') return null;
      // Only ordinary native fields cross into the document. In particular,
      // componentKey/parameters belong to the preview and never extend saves.
      const part = {id: newId('vr-accessory-preview-', reserved), name: String(source.name || 'Hip bag component'),
        kind: 'topologyMesh', group, position: clone(source.position ?? [0, 0, 0]),
        rotation: clone(source.rotation ?? [0, 0, 0]), scale: clone(source.scale ?? [1, 1, 1]),
        color: source.color, material: source.material, topologyMesh: clone(source.topologyMesh)};
      if (!part.name.trim() || part.name.length > 100 || !checkPart(part)) return null;
      components.push(part);
    }
    return {parts: components, parameters: clone(built.parameters), bounds: clone(built.bounds), mount: clone(built.mount)};
  }
  function candidates(record) {
    const transform = transformOf(record.handle.transform);
    if (!transform) return null;
    const rotation = new THREE.Quaternion().setFromEuler(new THREE.Euler(...transform.rotation));
    const parts = [];
    for (const source of record.base.parts) {
      const part = clone(source), position = new THREE.Vector3(...source.position).multiplyScalar(transform.scale[0]).applyQuaternion(rotation);
      position.add(new THREE.Vector3(...transform.position));
      const quaternion = rotation.clone().multiply(new THREE.Quaternion().setFromEuler(new THREE.Euler(...source.rotation)));
      const euler = new THREE.Euler().setFromQuaternion(quaternion);
      part.position = position.toArray(); part.rotation = [euler.x, euler.y, euler.z];
      part.scale = source.scale.map(n => n * transform.scale[0]);
      if (!checkPart(part)) return null;
      parts.push(part);
    }
    return parts;
  }
  function install(base, transform, source) {
    const handle = Object.freeze({ok: true, parameters: Object.freeze(clone(base.parameters)),
      transform: Object.freeze(transform), documentToken: source.documentToken, revision: source.revision});
    const record = {...source, handle, base};
    if (!candidates(record)) return fail('INVALID_ACCESSORY_TRANSFORM');
    cancel(); records.set(handle, record); pending = record;
    lastError = ''; lastAction = 'Previewing hip bag';
    return handle;
  }
  function draft(params = {}, transform = {}) {
    const native = nativeState();
    if (!native) return fail('MODEL_EDITOR_NOT_OPEN');
    if (busy(native)) return fail('MODEL_GESTURE_ALREADY_ACTIVE');
    let pose;
    try { pose = transformOf(transform); } catch { return fail('INVALID_ACCESSORY_TRANSFORM'); }
    if (!pose) return fail('INVALID_ACCESSORY_TRANSFORM');
    let base;
    try { base = recipe(params); } catch { return fail('INVALID_ACCESSORY_RECIPE'); }
    if (!base) return fail('INVALID_ACCESSORY_RECIPE');
    if (model().parts.length + base.parts.length > MODEL_ATELIER_LIMIT) return fail('MODEL_PART_LIMIT_REACHED');
    return install(base, pose, {document: model(), parts: model().parts, root: modelRoot,
      documentToken: native.documentToken, revision: native.revision, sources: [...model().parts], fingerprint: JSON.stringify(model())});
  }
  function rebuild(handle, params) {
    const record = handle && typeof handle === 'object' ? records.get(handle) : null;
    if (!record) return fail('MODEL_ACCESSORY_PREVIEW_NOT_FOUND');
    if (!current(record, true)) { cancel(handle); return fail('MODEL_CHANGED_DURING_ACCESSORY_PREVIEW'); }
    if (busy(nativeState())) return fail('MODEL_GESTURE_ALREADY_ACTIVE');
    let pose, base;
    try { pose = transformOf(handle.transform); base = recipe(params); } catch { return fail('INVALID_ACCESSORY_RECIPE'); }
    if (!pose) return fail('INVALID_ACCESSORY_TRANSFORM');
    if (!base) return fail('INVALID_ACCESSORY_RECIPE');
    if (model().parts.length + base.parts.length > MODEL_ATELIER_LIMIT) return fail('MODEL_PART_LIMIT_REACHED');
    return install(base, pose, record);
  }
  function preview(handle) {
    const record = handle && typeof handle === 'object' ? records.get(handle) : null;
    if (!record || !current(record)) return fail('MODEL_CHANGED_DURING_ACCESSORY_PREVIEW');
    const parts = candidates(record); if (!parts) return fail('INVALID_ACCESSORY_TRANSFORM');
    const previews = [];
    try {
      for (const part of parts) {
        const geometry = atelierCourierBaseGeometry(part);
        if (!geometry?.isBufferGeometry) { geometry?.dispose?.(); throw Error('native geometry'); }
        previews.push({part, geometry});
      }
    } catch {
      for (const item of previews) item.geometry.dispose();
      return fail('MODEL_ACCESSORY_GEOMETRY_UNAVAILABLE');
    }
    return {ok: true, parts: previews, parameters: clone(record.base.parameters), bounds: clone(record.base.bounds),
      mount: clone(record.base.mount), transform: clone(handle.transform)};
  }
  function commit(handle, expectedDocToken = handle?.documentToken) {
    const record = handle && typeof handle === 'object' ? records.get(handle) : null;
    if (!record) return fail('MODEL_ACCESSORY_PREVIEW_NOT_FOUND');
    const native = nativeState();
    if (!native || expectedDocToken !== record.documentToken || !current(record, true)) {
      cancel(handle); return fail('MODEL_CHANGED_DURING_ACCESSORY_PREVIEW');
    }
    if (busy(native)) return fail('MODEL_GESTURE_ALREADY_ACTIVE');
    if (model().parts.length + record.base.parts.length > MODEL_ATELIER_LIMIT) return fail('MODEL_PART_LIMIT_REACHED');
    const parts = candidates(record); if (!parts) return fail('INVALID_ACCESSORY_TRANSFORM');
    const reserved = new Set(model().parts.map(part => part.id));
    for (const part of parts) { part.id = newId('vr-accessory-', reserved); if (!checkPart(part)) return fail('INVALID_NATIVE_ACCESSORY_PART'); }
    // Validate the complete batch before changing history, selection or source.
    const result = parts.map(clone), ids = parts.map(part => part.id);
    records.delete(handle); if (pending === record) pending = null;
    checkpoint(); model().parts.push(...parts);
    atelierMeshIds = [...ids]; selection = ids.at(-1) || null; se350ModelTools.syncSelection(); signalEdited();
    lastError = ''; lastAction = 'Created hip bag with ' + parts.length + ' editable components';
    const after = nativeState();
    return {ok: true, changed: true, ids, parts: result, documentToken: after?.documentToken, revision: after?.revision};
  }
  const previousClose = close;
  close = function (...args) { cancel(undefined, 'MODEL_EDITOR_CLOSED'); return previousClose.apply(this, args); };
  return Object.freeze({draft, rebuild, preview, commit, cancel,
    inspect: () => {
      if (pending && !current(pending)) cancel(undefined, 'MODEL_CHANGED_DURING_ACCESSORY_PREVIEW');
      return {pending: pending ? {parameters: clone(pending.base.parameters), count: pending.base.parts.length,
        documentToken: pending.documentToken, revision: pending.revision} : null, error: lastError, lastAction};
    }});
})();
/* SE410_MODEL_ACCESSORY_BRIDGE_END */
