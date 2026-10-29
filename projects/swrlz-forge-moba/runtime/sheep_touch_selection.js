// Sheep movement stays immediate. Building inspection is a second deliberate
// tap on its visible geometry, rather than a large proximity target over gaps.
const stTouchSelection = {
  pending: null, gesture: null, lastPick: null, lastMove: null,
  resetReason: 'initial', windowMs: 360, distancePx: 32
};
function stTouchSelectionReset(reason = 'other input', clearReceipt = false) {
  stTouchSelection.pending = null;
  stTouchSelection.resetReason = reason;
  if (clearReceipt) {stTouchSelection.lastPick = null; stTouchSelection.lastMove = null;}
}
function stTouchSelectionSync() {
  const pending = stTouchSelection.pending;
  if (!pending) return;
  if (!stSession || pending.session !== stSession || stSession.role !== 'sheep' ||
      pending.controlledId !== stSession.controlledId || stSession.simulate ||
      paused || stSession.winner || stUi.build || stUi.route !== 'ground') {
    stTouchSelectionReset('session or mode changed');
  } else if (performance.now() - pending.at > stTouchSelection.windowMs) {
    stTouchSelectionReset('tap window expired');
  }
}
function stTouchVisibleEntity(clientX, clientY, state) {
  const ray = stUiRay(clientX, clientY); if (!ray || !stSession) return null;
  const visible = new Map(state.buildings.filter(building => building.pos &&
    !building.lastKnown && building.visible !== false).map(building => [building.id, building]));
  const visibleUnits = new Map(state.units.filter(unit => unit.pos &&
    !unit.lastKnown && unit.visible !== false).map(unit => [unit.id, unit]));
  const roots = [], owners = new Map();
  for (const building of stSession.buildings) {
    if (building.hp <= 0 || !visible.has(building.id) || !walkingObjectVisible(building.mesh)) continue;
    building.mesh.updateWorldMatrix(true, true);
    roots.push(building.mesh); owners.set(building.mesh, {building, entity: visible.get(building.id)});
  }
  for (const unit of stSession.units) {
    const object = unit.spirit || unit.actor;
    if (!visibleUnits.has(unit.id) || !walkingObjectVisible(object)) continue;
    object.updateWorldMatrix(true, true);
    roots.push(object); owners.set(object, {unit, entity: visibleUnits.get(unit.id)});
  }
  // A unit in front of a house must still receive its normal inspect/rescue
  // tap. Solid scenery also prevents selecting a house hidden behind it.
  for (const actor of actors) {
    if (!['st-tree','st-rock','st-pond','st-shop','st-thorn'].includes(actor.userData.actorType) ||
        actor.userData.baked === false || !walkingObjectVisible(actor)) continue;
    actor.updateWorldMatrix(true, true);
    roots.push(actor); owners.set(actor, {scenery: true});
  }
  for (const hit of ray.intersectObjects(roots, true)) {
    if (!walkingObjectVisible(hit.object)) continue;
    const materials = Array.isArray(hit.object.material) ? hit.object.material : [hit.object.material];
    const material = materials[hit.face?.materialIndex || 0];
    if (!material || material.visible === false || material.opacity <= .02) continue;
    let owner = hit.object;
    while (owner && !owners.has(owner)) owner = owner.parent;
    if (!owner) continue;
    return {...owners.get(owner), point: hit.point.toArray()};
  }
  return null;
}
function stTouchMoveDestination(unit, point) {
  if (unit.captured || unit.archiveOnUpper) return {point: point.clone(), adjusted: false};
  const radius = stUnitRadius(unit);
  // An actual gap always keeps the exact requested ground destination. A
  // disconnected clear destination remains an ordinary failed move order.
  if (!stBlocked(point.x, point.z, radius)) return {point: point.clone(), adjusted: false};
  const candidates = [];
  // A roof tap can project onto a blocked house. Search only the immediately
  // surrounding ground, with the same species collision and navigation rules.
  // This chooses an order destination; it never changes a sheep's position.
  for (let ring = 1; ring <= 12; ring++) {
    const distance = ring * .3;
    for (let spoke = 0; spoke < 16; spoke++) {
      const angle = spoke * Math.PI / 8;
      const candidate = new THREE.Vector3(point.x + Math.cos(angle) * distance, 0,
        point.z + Math.sin(angle) * distance);
      if (!stBlocked(candidate.x, candidate.z, radius)) candidates.push(candidate);
    }
  }
  candidates.sort((a,b) => a.distanceToSquared(point) - b.distanceToSquared(point) ||
    a.distanceToSquared(unit.pos) - b.distanceToSquared(unit.pos));
  for (const candidate of candidates) {
    if (stPath(unit.pos, candidate, radius)) return {point: candidate, adjusted: true};
  }
  return null;
}
const stTouchCommandOriginal = stCommand;
stCommand = function(action, payload = {}) {
  if (action !== 'preview') stTouchSelectionReset('game command: ' + action);
  return stTouchCommandOriginal(action, payload);
};
const stTouchOrderOriginal = stUiOrderAt;
stUiOrderAt = function(clientX, clientY) {
  stTouchSelectionSync();
  if (stSession && !stSession.simulate && paused) {
    stTouchSelectionReset('paused');
    stUiFeedback('Resume the game before giving orders.', true); return;
  }
  if (!stSession || stSession.simulate || stSession.role !== 'sheep' || stUi.build || stUi.route !== 'ground') {
    stTouchSelectionReset('other role or route');
    return stTouchOrderOriginal(clientX, clientY);
  }
  const point = stUiGround(clientX, clientY); if (!point) return;
  const state = stUiView(), geometry = stTouchVisibleEntity(clientX, clientY, state);
  const hit = geometry?.building ? geometry : null;
  stTouchSelection.lastPick = hit ? {buildingId: hit.entity.id, hitPoint: [...hit.point]} : null;
  const pending = stTouchSelection.pending, now = performance.now();
  if (hit && pending && pending.id === hit.entity.id &&
      now - pending.at <= stTouchSelection.windowMs &&
      Math.hypot(clientX - pending.x, clientY - pending.y) <= stTouchSelection.distancePx) {
    stTouchSelectionReset('building double tap');
    stUi.buildingId = hit.entity.id;
    const result = stUiCommand('select', {id: hit.entity.id});
    if (result?.ok) stUiFeedback((stUiBuildNames[hit.entity.kind] || 'Building') + ' selected. Tap ground to run again.');
    return;
  }
  stTouchSelectionReset(hit ? 'first building tap' : 'ground or unit tap');
  // Preserve ordinary unit inspection and the one-tap contact rescue order.
  // Buildings are deliberately absent from the broad screen-distance picker.
  const unitHit = geometry?.unit ? geometry.entity :
    !geometry ? stUiPick(clientX, clientY, {...state, buildings: []}) : null;
  if (unitHit && unitHit.id !== state.controlledId) {
    stUi.buildingId = null;
    if (unitHit.captured) {
      stUiCommand('select', {id: state.controlledId});
      const result = stUiCommand('rescue', {id: unitHit.id});
      if (result?.ok) stUiFeedback('Rescue order issued. Reach the wisp in the center pen.');
    } else stUiCommand('select', {id: unitHit.id});
    return;
  }
  stUi.buildingId = null;
  stUiCommand('select', {id: state.controlledId});
  const unit = stSession.units.find(candidate => candidate.id === state.controlledId);
  const destination = unit ? stTouchMoveDestination(unit, point) : null;
  const result = destination ? stUiCommand('move', {x: destination.point.x, z: destination.point.z, layer: 'ground'}) :
    stResult(false, 'There is no reachable clear ground beside this building.');
  stTouchSelection.lastMove = {requested: [point.x, point.z],
    destination: destination ? [destination.point.x, destination.point.z] : null,
    adjusted: !!destination?.adjusted, ok: !!result?.ok};
  if (!destination) stUiFeedback(result.reason, true);
  else if (result?.ok) stUiFeedback(hit ? 'Move order issued. Double-tap the building to select it.' : 'Move order issued.');
  if (hit && !paused && !stSession.winner) {
    stTouchSelection.pending = {id: hit.entity.id, at: performance.now(), x: clientX, y: clientY,
      session: stSession, controlledId: state.controlledId};
  }
};
const stTouchChooseBuildOriginal = stUiChooseBuild;
stUiChooseBuild = function(kind) {
  stTouchSelectionReset('build placement'); return stTouchChooseBuildOriginal(kind);
};
const stTouchShowHUDOriginal = stShowHUD;
stShowHUD = function(show) {
  stTouchSelectionReset('HUD session changed', true); return stTouchShowHUDOriginal(show);
};
const stTouchDisposeUIOriginal = stDisposeUI;
stDisposeUI = function() {
  stTouchSelectionReset('Stop', true); stTouchSelection.gesture = null;
  return stTouchDisposeUIOriginal();
};
const stTouchStopOriginal = stStop;
stStop = function() {
  stTouchSelectionReset('Stop', true); return stTouchStopOriginal();
};
const stTouchRefreshHUDOriginal = stRefreshHUD;
stRefreshHUD = function(force = false) {
  stTouchSelectionSync(); stTouchRefreshHUDOriginal(force);
  if (stSession?.role === 'sheep' && stUi.shown && !stUi.build &&
      !stSession.units.find(unit => unit.id === stSession.controlledId)?.captured) {
    stUiText('stTip', 'Tap ground to run. Double-tap a building to select it. Build houses to block wolves; reach wisps to rescue allies.');
  }
};
const stTouchStatusOriginal = stUiStatus;
stUiStatus = function() {
  stTouchSelectionSync();
  return {...stTouchStatusOriginal(), buildingSelection: {
    mode: 'double-tap', enabled: !!stSession && stSession.role === 'sheep' && !stSession.simulate,
    pendingId: stTouchSelection.pending?.id || null, windowMs: stTouchSelection.windowMs,
    distancePx: stTouchSelection.distancePx, resetReason: stTouchSelection.resetReason,
    lastPick: stTouchSelection.lastPick ? structuredClone(stTouchSelection.lastPick) : null,
    lastMove: stTouchSelection.lastMove ? structuredClone(stTouchSelection.lastMove) : null
  }};
};
const stTouchInstallUIOriginal = stInstallUI;
stInstallUI = function() {
  stTouchInstallUIOriginal();
  const panel = $('stHelpPanel');
  if (panel && !panel.dataset.sheepDoubleTap) {
    for (const paragraph of panel.querySelectorAll('p')) {
      paragraph.textContent = paragraph.textContent.replace('tap units or farms to select them.',
        'tap units to select them. As a sheep, double-tap the same building to select it; a single tap keeps you running.');
    }
    panel.dataset.sheepDoubleTap = 'true';
  }
};
// Window capture sees gestures before the existing viewport listeners consume
// them. These observers never stop, defer, or synthesize a pointer event.
window.addEventListener('pointerdown', event => {
  if (!stSession || stSession.simulate) return;
  if (!event.target?.closest?.('#viewport')) {
    stTouchSelectionReset('another control'); stTouchSelection.gesture = null; return;
  }
  if (event.button !== 0 || stUi.keys.has(' ') || stTouchSelection.gesture) stTouchSelectionReset('pan or multiple pointers');
  stTouchSelection.gesture = {id: event.pointerId, x: event.clientX, y: event.clientY};
}, true);
window.addEventListener('pointermove', event => {
  const gesture = stTouchSelection.gesture;
  if (gesture?.id === event.pointerId && Math.hypot(event.clientX - gesture.x, event.clientY - gesture.y) > 9)
    stTouchSelectionReset('pointer drag');
}, true);
window.addEventListener('pointerup', event => {
  if (stTouchSelection.gesture?.id === event.pointerId) stTouchSelection.gesture = null;
}, true);
window.addEventListener('pointercancel', () => {
  stTouchSelection.gesture = null; stTouchSelectionReset('pointer cancelled');
}, true);
window.addEventListener('wheel', () => stTouchSelectionReset('camera zoom'), {capture: true, passive: true});
window.addEventListener('keydown', event => {
  if (stSession && ['w','a','s','d','arrowup','arrowdown','arrowleft','arrowright',' ','q','e','f','r','escape'].includes(event.key.toLowerCase()))
    stTouchSelectionReset('keyboard command');
}, true);
window.addEventListener('blur', () => {
  stTouchSelection.gesture = null; stTouchSelectionReset('window blur');
});
document.addEventListener('visibilitychange', () => {
  if (document.hidden) {stTouchSelection.gesture = null; stTouchSelectionReset('document hidden');}
});
