// Sheep Tag controls live inside the native editor session. No pointer lock,
// extra render loop, or saved actors are created by the HUD and build preview.
const stUi = {
  installed: false, shown: false, build: null, preview: null, placement: null,
  follow: true, focus: new THREE.Vector3(), zoom: 1, keys: new Set(), drag: null,
  buildingId: null, lastHud: -Infinity, lastMap: -Infinity, messageUntil: 0,
  cameraSaved: null, rulesReturnFocus: null, rings: null, lastGameMessage: '',
  rotation: 0, route: 'ground', footprint: null, placementPoint: null,
  lastAttack: null, attackUntil: 0, extrasOpen: false, mapReceipt: null
};
const stUiBuildNames = {'st-farm': 'House', 'st-income': 'Income house', 'st-fort': 'Fortified house',
  'st-wall': 'Castle wall', 'st-ramp': 'Ramp', 'st-totem': 'Stealth totem'};
const stUiBuildButtons = [['stBuildFarm', 'st-farm'], ['stBuildIncome', 'st-income'],
  ['stBuildFort', 'st-fort'], ['stBuildWall', 'st-wall'], ['stBuildRamp', 'st-ramp']];
// Player controls never read the diagnostic status, which can contain hidden units.
function stUiView() {return stViewStatus();}
function stUiRules() {return stSession?.rules || stRules();}
function stUiStatus() {
  return {shown:stUi.shown,build:stUi.build,rotation:stUi.rotation,route:stUi.route,
    minimap:stUi.mapReceipt ? structuredClone(stUi.mapReceipt) : null};
}
function stUiText(id, text) {
  const node = $(id);
  if (node && node.textContent !== String(text)) node.textContent = String(text);
}
function stUiClock(seconds) {
  const n = Math.max(0, Math.ceil(Number(seconds) || 0));
  return Math.floor(n / 60) + ':' + String(n % 60).padStart(2, '0');
}
function stUiFeedback(message, error = false) {
  stUiText('stFeedback', message || '');
  $('stFeedback')?.classList.toggle('error', error);
  stUi.messageUntil = performance.now() + 5000;
}
function stUiCommand(action, payload = {}) {
  const result = stCommand(action, payload);
  if (!result?.ok) stUiFeedback(result?.reason || 'That order is unavailable.', true);
  stRefreshHUD(true);
  return result;
}
function stUiClearPreview() {
  if (stUi.preview) {
    scene.remove(stUi.preview);
    stUi.preview.traverse(object => {
      object.geometry?.dispose();
      const materials = Array.isArray(object.material) ? object.material : [object.material];
      for (const material of materials) material?.dispose();
    });
  }
  if (stUi.footprint) {
    scene.remove(stUi.footprint); stUi.footprint.geometry.dispose(); stUi.footprint.material.dispose();
  }
  stUi.preview = null; stUi.placement = null; stUi.footprint = null; stUi.placementPoint = null;
}
function stUiChooseBuild(kind) {
  if (!stSession) return;
  const state = stUiView(), controlled = state.units.find(unit => unit.id === state.controlledId);
  if (state.role !== 'sheep' || !controlled || controlled.captured || controlled.kind !== 'sheep') {
    stUiFeedback('Only a free sheep can build.', true); return;
  }
  if (['st-wall','st-ramp'].includes(kind) && !stUiRules().elevated) {stUiFeedback('Enable raised routes in the map rules first.', true); return;}
  stUiCommand('select', {id: state.controlledId});
  stUi.build = stUi.build === kind ? null : kind;
  stUi.buildingId = null; stUiClearPreview();
  if (stUi.build) {
    stUi.preview = stMakeVisual(stUi.build);
    stUi.preview.name = 'Sheep Tag placement preview';
    stUi.preview.userData.sheepTagPreview = true;
    stUi.preview.traverse(object => {
      if (!object.material) return;
      const original = Array.isArray(object.material) ? object.material : [object.material];
      // stMakeVisual supplies fresh materials, shared only by this preview.
      // Tint them in place so no detached original materials leak per click.
      for (const material of original) {
        material.transparent = true; material.opacity = .48; material.depthWrite = false;
      }
      object.castShadow = false; object.receiveShadow = false;
    });
    stUi.preview.visible = false; scene.add(stUi.preview);
    stUi.footprint = new THREE.LineLoop(new THREE.BufferGeometry(), new THREE.LineBasicMaterial({color: 0x96ffd0, depthTest: false, transparent: true, opacity: .95}));
    stUi.footprint.name = 'Exact building footprint'; stUi.footprint.userData.sheepTagPreview = true;
    stUi.footprint.renderOrder = 100; stUi.footprint.visible = false; scene.add(stUi.footprint);
    stUiFeedback('Tap ground to place a ' + stUiBuildNames[kind].toLowerCase() + '. Green fits; red is blocked.');
  } else stUiFeedback('Build placement cancelled.');
  stRefreshHUD(true);
}
function stUiRay(clientX, clientY) {
  const rect = $('viewport').getBoundingClientRect();
  if (!rect.width || !rect.height) return null;
  const pointer = new THREE.Vector2((clientX - rect.left) / rect.width * 2 - 1,
    -(clientY - rect.top) / rect.height * 2 + 1);
  const ray = new THREE.Raycaster(); ray.setFromCamera(pointer, camera);
  return ray;
}
function stUiGround(clientX, clientY, height = 0) {
  const ray = stUiRay(clientX,clientY);
  return ray?.ray.intersectPlane(new THREE.Plane(new THREE.Vector3(0, 1, 0), -height), new THREE.Vector3()) || null;
}
function stUiUpperPoint(clientX,clientY) {
  if (!stSession || typeof stArchiveSurface !== 'function') return null;
  const ray = stUiRay(clientX,clientY); if (!ray) return null;
  const visibleIds = new Set(stUiView().buildings.filter(building => building.progress >= 1 &&
    ['st-wall','st-ramp'].includes(building.kind)).map(building => building.id));
  let nearest = null, distance = Infinity;
  for (const building of stSession.buildings) {
    if (!visibleIds.has(building.id) || building.mesh.visible === false) continue;
    const surface = stArchiveSurface(building); if (!surface) continue;
    // The same transformed top used for walking supplies a bounded picking
    // plane. This includes authored scale/rotation and the actual ramp slope;
    // picking the railing or the ground below a deck cannot shift its target.
    const plane = new THREE.Plane().setFromCoplanarPoints(surface.point(-1.2,-3),
      surface.point(1.2,-3),surface.point(-1.2,3));
    const point = ray.ray.intersectPlane(plane,new THREE.Vector3()); if (!point) continue;
    const local = point.clone().applyMatrix4(surface.inverse);
    if (Math.abs(local.x) > 1.2 + .001 || Math.abs(local.z) > 3 + .001) continue;
    const candidateDistance = ray.ray.origin.distanceToSquared(point);
    if (candidateDistance < distance) {nearest = point; distance = candidateDistance;}
  }
  return nearest;
}
function stUiPlacePreview(point) {
  if (!stUi.preview || !stUi.build || !point) return;
  const fit = stCanBuild(stUi.build, point.x, point.z, stUiView().controlledId, stUi.rotation);
  stUi.placementPoint = point.clone();
  stUi.placement = fit;
  stUi.preview.position.set(Number.isFinite(fit.x) ? fit.x : point.x, 0,
    Number.isFinite(fit.z) ? fit.z : point.z);
  stUi.preview.visible = true;
  stUi.preview.rotation.y = Number.isFinite(fit.rotation) ? fit.rotation : stUi.rotation;
  if (['st-wall','st-ramp'].includes(stUi.build)) stUi.preview.scale.y = stUiRules().wallHeight / 3.3;
  if (stUi.footprint) {
    const halfX = stUi.build === 'st-wall' || stUi.build === 'st-ramp' ? 1.2 : 1.2;
    const halfZ = stUi.build === 'st-wall' || stUi.build === 'st-ramp' ? 3 : 1.2;
    const rotation = stUi.preview.rotation.y, c = Math.cos(rotation), s = Math.sin(rotation);
    const x = stUi.preview.position.x, z = stUi.preview.position.z;
    const corners = fit.corners || [[-halfX,-halfZ],[halfX,-halfZ],[halfX,halfZ],[-halfX,halfZ]]
      .map(([dx,dz]) => [x + dx*c + dz*s, z - dx*s + dz*c]);
    const positions = corners.flatMap(([cx,cz]) => [cx, terrainHeight(cx,cz) + .055, cz]);
    stUi.footprint.geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
    stUi.footprint.geometry.computeBoundingSphere(); stUi.footprint.visible = true;
    stUi.footprint.material.color.set(fit.ok ? 0x96ffd0 : 0xff7777);
  }
  stUi.preview.traverse(object => {
    const materials = Array.isArray(object.material) ? object.material : [object.material];
    for (const material of materials) {
      if (material?.color) material.color.set(fit.ok ? 0x83ebb2 : 0xff7777);
      if (material?.emissive) material.emissive.set(fit.ok ? 0x10381d : 0x481414);
    }
  });
  const warnings = (fit.warnings || []).map(item => typeof item === 'string' ? item : item.message).filter(Boolean);
  stUiText('stPlacement', !fit.ok ? fit.reason || 'Blocked footprint' :
    'Fits · ' + (fit.halfX && fit.halfZ ? (fit.halfX*2).toFixed(2) + ' × ' + (fit.halfZ*2).toFixed(2) + ' ground units' : 'exact outline shown') +
    (warnings.length ? ' · ' + warnings.join(' · ') : ' · check your escape gap'));
  $('stPlacement')?.classList.toggle('error', !fit.ok);
}
function stUiPick(clientX, clientY, state) {
  const rect = $('viewport').getBoundingClientRect();
  let nearest = null, best = matchMedia('(pointer:coarse)').matches ? 34 : 24;
  for (const entity of [...state.units, ...state.buildings]) {
    if (!entity.pos || entity.lastKnown || entity.visible === false) continue;
    const point = new THREE.Vector3(...entity.pos);
    point.y += entity.kind === 'wisp' ? .2 : entity.kind.startsWith('st-') ? 1 : .7;
    point.project(camera);
    if (point.z < -1 || point.z > 1) continue;
    const x = rect.left + (point.x + 1) * rect.width / 2;
    const y = rect.top + (1 - point.y) * rect.height / 2;
    const distance = Math.hypot(clientX - x, clientY - y);
    if (distance < best) {best = distance; nearest = entity;}
  }
  return nearest;
}
function stUiOrderAt(clientX, clientY) {
  const upperMove = !stUi.build && stUi.route === 'upper';
  const point = upperMove ? stUiUpperPoint(clientX,clientY) : stUiGround(clientX, clientY);
  if (!point) {if (upperMove) stUiFeedback('Tap the walking surface of a completed wall or ramp.',true); return;}
  if (stUi.build) {
    stUiPlacePreview(point);
    const fit = stUi.placement;
    if (!fit?.ok) {stUiFeedback(fit?.reason || 'This building does not fit here.', true); return;}
    const name = stUiBuildNames[stUi.build];
    const result = stUiCommand('build', {kind: stUi.build, x: fit.x, z: fit.z, rotation: fit.rotation ?? stUi.rotation});
    if (result?.ok) {
      stUiFeedback(name + ' ordered. Your sheep will walk to the construction site.');
      stUi.build = null; stUiClearPreview(); stRefreshHUD(true);
    }
    return;
  }
  if (stUi.route === 'upper') {
    const result = stUiCommand('move', {x:point.x,z:point.z,layer:'upper'});
    if (result?.ok) stUiFeedback('Upper route ordered. Reach a connected ramp to ascend.');
    return;
  }
  const state = stUiView(), entity = stUiPick(clientX, clientY, state);
  if (entity) {
    if (state.role === 'wolf' && (entity.kind === 'sheep' || entity.kind.startsWith('st-'))) {
      stUiCommand('select', {id: state.controlledId});
      const result = stUiCommand('attack', {id: entity.id});
      if (result?.ok) stUiFeedback(entity.kind.startsWith('st-') ? 'Demolition ordered. Your wolf will approach and strike.' : 'Hunt order issued.');
    } else if (state.role === 'sheep' && entity.captured && entity.id !== state.controlledId) {
      stUiCommand('select', {id: state.controlledId});
      const result = stUiCommand('rescue', {id: entity.id});
      if (result?.ok) stUiFeedback('Rescue order issued. Reach the wisp in the center pen.');
    } else {
      stUi.buildingId = entity.kind.startsWith('st-') ? entity.id : null;
      stUiCommand('select', {id: entity.id});
    }
  } else {
    stUi.buildingId = null;
    const result = stUiCommand('move', {x: point.x, z: point.z, layer: stUi.route});
    if (result?.ok) stUiFeedback(stUi.route === 'upper' ? 'Upper route ordered. Reach a connected ramp to ascend.' : 'Move order issued.');
  }
}
function stUiRotatePlacement() {
  if (!stUi.build || !['st-wall','st-ramp'].includes(stUi.build)) return;
  stUi.rotation = (stUi.rotation + Math.PI/2) % (Math.PI*2);
  if (stUi.placementPoint) stUiPlacePreview(stUi.placementPoint);
  stRefreshHUD(true);
}
function stCameraFocus(position) {
  const x = Array.isArray(position) ? position[0] : position?.x;
  const z = Array.isArray(position) ? position[2] : position?.z;
  if (!Number.isFinite(x) || !Number.isFinite(z)) return false;
  const bounds = stUiRules().bounds || 40;
  stUi.focus.set(THREE.MathUtils.clamp(x, -bounds, bounds), 0,
    THREE.MathUtils.clamp(z, -bounds, bounds));
  stUi.follow = false; stRefreshHUD(true); return true;
}
function stUiPan(dx, dy) {
  const rect = $('viewport').getBoundingClientRect();
  const distance = perspectiveCamera.position.distanceTo(stUi.focus);
  const worldHeight = 2 * distance * Math.tan(THREE.MathUtils.degToRad(perspectiveCamera.fov) / 2);
  const scale = worldHeight / Math.max(1, rect.height);
  const bounds = stUiRules().bounds || 40;
  stUi.follow = false;
  stUi.focus.x = THREE.MathUtils.clamp(stUi.focus.x - dx * scale, -bounds, bounds);
  stUi.focus.z = THREE.MathUtils.clamp(stUi.focus.z - dy * scale * 1.28, -bounds, bounds);
}
function stUpdateCamera(dt = 0) {
  if (!stSession || stSession.simulate) return;
  const state = stUiView();
  const keyX = (stUi.keys.has('d') || stUi.keys.has('arrowright') ? 1 : 0) -
    (stUi.keys.has('a') || stUi.keys.has('arrowleft') ? 1 : 0);
  const keyZ = (stUi.keys.has('s') || stUi.keys.has('arrowdown') ? 1 : 0) -
    (stUi.keys.has('w') || stUi.keys.has('arrowup') ? 1 : 0);
  if (keyX || keyZ) {
    stUi.follow = false;
    stUi.focus.x += keyX * Math.min(dt, .05) * 22 * stUi.zoom;
    stUi.focus.z += keyZ * Math.min(dt, .05) * 22 * stUi.zoom;
  }
  if (stUi.follow) {
    const unit = state.units.find(item => item.id === state.selectedId) ||
      state.units.find(item => item.id === state.controlledId);
    if (unit) stUi.focus.set(unit.pos[0], 0, unit.pos[2]);
  }
  const bounds = stUiRules().bounds || 40;
  stUi.focus.x = THREE.MathUtils.clamp(stUi.focus.x, -bounds, bounds);
  stUi.focus.z = THREE.MathUtils.clamp(stUi.focus.z, -bounds, bounds);
  const portraitFit = Math.max(1, Math.min(1.35, .7 / Math.max(.3, perspectiveCamera.aspect)));
  const zoom = stUi.zoom * portraitFit;
  perspectiveCamera.fov = 50; perspectiveCamera.up.set(0, 1, 0);
  perspectiveCamera.position.set(stUi.focus.x, 32 * zoom, stUi.focus.z + 25 * zoom);
  perspectiveCamera.lookAt(stUi.focus); perspectiveCamera.updateProjectionMatrix();
  perspectiveCamera.updateMatrixWorld(true);
  stUiUpdateRings(state);
}
function stUiUpdateRings(state) {
  if (!stUi.rings) {
    const make = (inner, outer, color) => {
      const ring = new THREE.Mesh(new THREE.RingGeometry(inner, outer, 48),
        new THREE.MeshBasicMaterial({color, transparent: true, opacity: .88,
          depthWrite: false, side: THREE.DoubleSide}));
      ring.name = 'Sheep Tag selection marker'; ring.userData.sheepTagPreview = true;
      ring.rotation.x = -Math.PI / 2; scene.add(ring); return ring;
    };
    stUi.rings = [make(.78, .90, 0xf6d675), make(1.0, 1.09, 0x7fe1db)];
  }
  for (const [index, id] of [[0, state.controlledId], [1, state.selectedId]]) {
    const entity = [...state.units, ...state.buildings].find(item => item.id === id);
    const ring = stUi.rings[index]; ring.visible = !!entity;
    if (!entity) continue;
    ring.position.set(entity.pos[0], Math.max(entity.pos[1] || 0, terrainHeight(entity.pos[0], entity.pos[2])) + .035 + index * .004, entity.pos[2]);
    const scale = entity.kind.startsWith('st-') ? 1.6 : entity.kind === 'wolf' ? 1.25 : 1;
    ring.scale.setScalar(scale);
  }
}
function stUiDrawMinimap(state) {
  const canvas = $('stMinimap'), context = canvas?.getContext('2d'); if (!context) return;
  const size = canvas.width, bounds = stUiRules().bounds || 40;
  const xy = pos => [(pos[0] + bounds) / (bounds * 2) * size, (pos[2] + bounds) / (bounds * 2) * size];
  const receipt = {unitIds:[],buildingIds:[],lastKnown:[],scentClues:[],fogMode:state.fog?.mode || 'off'};
  context.clearRect(0, 0, size, size); context.fillStyle = '#203c2e'; context.fillRect(0, 0, size, size);
  context.fillStyle = '#15291f'; context.fillRect(0, 0, size, 9); context.fillRect(0, size - 9, size, 9);
  context.fillRect(0, 0, 9, size); context.fillRect(size - 9, 0, 9, size);
  context.strokeStyle = '#7d9a62'; context.lineWidth = 1;
  const pen = state.pen || {x: 0, z: 0, halfX: 7, halfZ: 7};
  const [penX, penY] = xy([pen.x - pen.halfX, 0, pen.z - pen.halfZ]);
  context.strokeRect(penX, penY, size * pen.halfX / bounds, size * pen.halfZ / bounds);
  for (const shop of state.shops || []) {
    const [x, y] = xy(shop.pos); context.fillStyle = '#dec064';
    context.fillRect(x - 3, y - 3, 6, 6);
  }
  // Shade unseen/explored ground from the same vision state as the main view.
  // Do not inspect editor actors or diagnostic enemy coordinates here.
  const fog = state.fog;
  if (fog && fog.mode !== 'off' && fog.width && fog.cellSize) {
    const visible = new Set(fog.visible || []), explored = new Set(fog.explored || []);
    const extent = Number(fog.extent) || bounds, pixels = fog.cellSize / (bounds*2) * size;
    for (let index = 0; index < fog.width * fog.width; index++) {
      if (visible.has(index)) continue;
      const col = index % fog.width, row = Math.floor(index / fog.width);
      const [x,y] = xy([-extent + col*fog.cellSize,0,-extent + row*fog.cellSize]);
      context.fillStyle = explored.has(index) ? '#08171099' : '#020907db';
      context.fillRect(x,y,pixels + .5,pixels + .5);
    }
  }
  for (const building of state.buildings || []) {
    if (!building.pos || building.visible === false || building.lastKnown) continue;
    const [x, y] = xy(building.pos); context.fillStyle = building.kind === 'st-income' ? '#eac666' : '#a9c0a1';
    context.fillRect(x - 2.5, y - 2.5, 5, 5);
    receipt.buildingIds.push(building.id);
  }
  for (const clue of state.scentClues || []) {
    if (!Number.isFinite(clue.x) || !Number.isFinite(clue.z)) continue;
    const [x,y] = xy([clue.x,0,clue.z]);
    context.strokeStyle = '#e9ab62'; context.setLineDash([2,2]);
    context.beginPath(); context.arc(x,y,Math.max(4,(clue.radius || 2.4)/bounds*size/2),0,Math.PI*2); context.stroke(); context.setLineDash([]);
    receipt.scentClues.push({x:clue.x,z:clue.z,radius:clue.radius || 2.4});
  }
  for (const clue of state.lastKnown || []) {
    if (!clue.pos || (state.units || []).some(unit => unit.id === clue.id)) continue;
    const [x,y] = xy(clue.pos); context.strokeStyle = '#b29a83'; context.globalAlpha = .6;
    context.strokeRect(x-2.5,y-2.5,5,5); context.globalAlpha = 1;
    receipt.lastKnown.push({id:clue.id,pos:[...clue.pos],seenAt:clue.seenAt});
  }
  for (const unit of state.units || []) {
    if (!unit.pos || unit.lastKnown || unit.visible === false) continue;
    const [x, y] = xy(unit.pos);
    context.fillStyle = unit.kind === 'wolf' ? '#ef927f' : unit.captured || unit.kind === 'wisp' ? '#76deee' : '#fff4cc';
    context.beginPath(); context.arc(x, y, unit.controlled ? 3.5 : 2.5, 0, Math.PI * 2); context.fill();
    if (unit.id === state.selectedId) {context.strokeStyle = '#fff'; context.stroke();}
    receipt.unitIds.push(unit.id);
  }
  // Project the real camera corners onto the ground, so the inset describes
  // what the player sees at every zoom and phone aspect ratio.
  const rect = $('viewport').getBoundingClientRect(), corners = [[0, 0], [1, 0], [1, 1], [0, 1]];
  context.strokeStyle = '#d9edc3'; context.lineWidth = 1; context.beginPath();
  let first = true;
  for (const [cx, cy] of corners) {
    const point = stUiGround(rect.left + cx * rect.width, rect.top + cy * rect.height);
    if (!point) continue;
    const [x, y] = xy(point.toArray());
    if (first) context.moveTo(x, y); else context.lineTo(x, y); first = false;
  }
  if (!first) {context.closePath(); context.stroke();}
  stUi.mapReceipt = receipt;
}
function stUiRefreshArchive(state,controlled,building,mayBuild,now) {
  const rules = state.rules || stUiRules(), magic = state.progression || controlled?.archive || controlled || {};
  const splitCooldown = Number(magic.splitCooldownRemaining) || 0;
  const level = Number(magic.level ?? controlled?.level) || 1;
  const canSplit = magic.splitUnlocked ?? level >= rules.splitUnlock;
  $('stSplit').hidden = state.role !== 'sheep' || !rules.split;
  $('stSplit').disabled = !mayBuild || !canSplit || splitCooldown > 0;
  stUiText('stSplitInfo', !canSplit ? 'Unlocks at level ' + rules.splitUnlock : splitCooldown > 0 ? stUiClock(splitCooldown) + ' cooldown' : 'Ready · mirrored escape');
  $('stTotem').hidden = state.role !== 'sheep' || !rules.totems;
  const ownedHouse = building && building.owner === state.controlledId && ['st-farm','st-income','st-fort'].includes(building.kind) && building.progress >= 1;
  const totemCooldown = Number(magic.totemCooldownRemaining) || 0;
  const totemAvailable = magic.canTotem !== false && !(rules.totemLimit === 'once' && magic.totemUsed) && totemCooldown <= 0;
  $('stTotem').disabled = !mayBuild || !ownedHouse || !totemAvailable;
  stUiText('stTotemInfo', rules.totemLimit === 'once' && magic.totemUsed ? 'Used this match' : totemCooldown > 0 ? stUiClock(totemCooldown) + ' cooldown' : ownedHouse ?
    (Number.isFinite(magic.density) ? magic.density + '/9 nearby allied houses' : 'Needs 9 nearby allied houses') : 'Select your finished house');
  $('stUpperRoute').hidden = !rules.elevated;
  $('stExitWall').hidden = !rules.elevated;
  $('stUpperRoute').disabled = !controlled || controlled.captured || !!state.winner || !!state.simulate;
  $('stExitWall').disabled = !controlled || controlled.captured || !!state.winner || !!state.simulate || !(magic.upper || controlled.upper || (controlled.pos?.[1] || 0) > 1);
  $('stUpperRoute').classList.toggle('active',stUi.route === 'upper');
  $('stUpperRoute').setAttribute('aria-pressed',String(stUi.route === 'upper'));
  stUiText('stUpperRoute', stUi.route === 'upper' ? 'Move: upper route' : 'Move: ground');
  $('stPlacementTools').hidden = !stUi.build;
  $('stRotatePlacement').hidden = !['st-wall','st-ramp'].includes(stUi.build);
  stUiText('stRotatePlacement', 'Rotate ' + Math.round(stUi.rotation*180/Math.PI) + '°');
  stUiText('stPlacementSnap', rules.buildSnap === 3 ? 'Grid: 3 units' : 'Fine: 0.15 units');
  if (!stUi.build) stUiText('stPlacement','');
  const progressionParts = [];
  if (rules.split && state.role === 'sheep') progressionParts.push('Level ' + level +
    (Number.isFinite(magic.xp) && Number.isFinite(magic.nextLevelXp) ? ' · ' + Math.floor(magic.xp) + '/' + Math.ceil(magic.nextLevelXp) + ' progress' : ''));
  if (magic.scentRemaining > 0) progressionParts.push('Thorn scent · ' + stUiClock(magic.scentRemaining) + ' · wolves get approximate clues');
  if (magic.concealment > .05 && state.role === 'sheep') progressionParts.push('Concealed ' + Math.round(magic.concealment*100) + '%');
  if (state.role === 'wolf' && (state.scentClues || []).length) progressionParts.push('Fresh scent nearby · dashed map circles are approximate');
  stUiText('stMagicReadout',progressionParts.join(' · '));
  const event = state.event;
  $('stEventBanner').hidden = !event;
  stUiText('stEventBanner', event ? (event.label || 'Special event') + ' · ' + (event.state === 'warning' ?
    'starts in ' + stUiClock(event.warningRemaining ?? Math.max(0,(event.startAt || 0)-(state.elapsed || 0))) :
    stUiClock(event.remaining ?? Math.max(0,(event.endAt || 0)-(state.elapsed || 0))) + ' remaining') : '');
  const hits = state.attacks || [];
  const hit = [...hits].reverse().find(item => item.attackerId === state.controlledId || item.buildingId === building?.id);
  const hitId = hit && (hit.id || [hit.attackerId,hit.buildingId,hit.at,hit.remainingHp].join(':'));
  if (hitId && hitId !== stUi.lastAttack) {
    stUi.lastAttack = hitId; stUi.attackUntil = now + 1800;
    stUiText('stAttackFeedback', '-' + Math.round(hit.damage || 0) + ' HP · ' +
      (hit.remainingHp <= 0 ? 'House breached' : Math.ceil(hit.remainingHp) + ' HP remaining'));
  }
  $('stAttackFeedback').hidden = now > stUi.attackUntil;
  const optionsShown = !state.simulate && (state.role === 'sheep' && (rules.totems || rules.split) || rules.elevated);
  $('stMoreActions').hidden = !optionsShown;
  $('stExtraActions').hidden = !optionsShown || !stUi.extrasOpen;
  $('stMoreActions').setAttribute('aria-expanded',String(optionsShown && stUi.extrasOpen));
}
function stRefreshHUD(force = false) {
  const starter = currentProject?.kind === 'sheep-tag';
  $('sheepTagRulesBtn')?.classList.toggle('hidden', !starter || !!stSession);
  if (!stSession || !stUi.shown) return;
  const now = performance.now(); if (!force && now - stUi.lastHud < 100) return; stUi.lastHud = now;
  const state = stUiView();
  const inspectedId = state.simulate ? selected?.userData.id : state.selectedId;
  const unit = state.units.find(item => item.id === inspectedId);
  const building = state.buildings.find(item => item.id === (stUi.buildingId || state.selectedId));
  const controlled = state.units.find(item => item.id === state.controlledId);
  const free = state.counts?.livingSheep ?? state.units.filter(item => item.kind === 'sheep' && !item.captured && !item.isIllusion).length;
  const wisps = state.counts?.capturedSheep ?? state.units.filter(item => item.captured || item.kind === 'wisp').length;
  stUiText('stTimer', stUiClock(state.remaining)); stUiText('stGold', Math.floor(state.gold || 0) + ' gold');
  stUiText('stCounts', free + ' free · ' + wisps + ' wisps');
  stUiText('stRole', state.role === 'wolf' ? 'WOLF' : 'SHEEP');
  const phase = state.winner ? (state.winner === 'sheep' ? 'The flock survived!' : 'The wolves caught the flock!') :
    paused ? 'Paused' : state.headstartRemaining > 0 ? 'Wolves released in ' + stUiClock(state.headstartRemaining) :
      controlled?.captured ? 'You are a wisp · wait for a teammate to rescue you' : 'The hunt is on';
  stUiText('stPhase', phase); $('stPhase')?.classList.toggle('finished', !!state.winner);
  stUiText('stSelectedName', building ? stUiBuildNames[building.kind] || building.name : unit?.name || 'Select a unit');
  const order = typeof unit?.order === 'string' ? unit.order : unit?.order?.action || unit?.order?.type;
  const detail = building ? Math.ceil(building.hp) + '/' + building.maxHp + ' HP · ' +
    (building.progress < 1 ? 'building ' + Math.round(building.progress * 100) + '%' : 'level ' + (building.level || 1)) :
    unit ? (unit.captured || unit.kind === 'wisp' ? 'Captured wisp · center pen' : unit.controlled ? 'Your ' + unit.kind : 'AI ' + unit.kind) +
      (order ? ' · ' + order : '') : 'Tap sheep, wolves, or farms to inspect them.';
  stUiText('stSelectedDetail', detail + (unit?.kind === 'wolf' && unit.damage ? ' · ' + Math.round(unit.damage) + ' damage / strike' : ''));
  $('stHealthTrack').hidden = !building;
  if (building) {
    $('stHealthBar').style.width = Math.max(0,Math.min(100,building.hp/building.maxHp*100)) + '%';
    $('stHealthTrack').setAttribute('aria-label', Math.ceil(building.hp) + ' of ' + Math.ceil(building.maxHp) + ' building health');
  }
  const mayBuild = state.role === 'sheep' && controlled?.kind === 'sheep' && !controlled.captured && !state.winner;
  if (stUi.build && !mayBuild) {stUi.build = null; stUiClearPreview();}
  for (const [id, kind] of stUiBuildButtons) {
    const button = $(id); if (!button) continue;
    const raised = kind === 'st-wall' || kind === 'st-ramp';
    const permitted = !state.rules?.permittedStructures || state.rules.permittedStructures.includes(kind) || state.rules.permittedStructures.includes(kind.replace('st-',''));
    button.hidden = raised && !state.rules?.elevated && !stUiRules().elevated;
    button.disabled = !mayBuild || !permitted;
    const config = ST_BUILDINGS[kind];
    const shortcut = { 'st-farm': 'Q', 'st-income': 'E', 'st-fort': 'F' }[kind];
    const cost = kind === 'st-wall' ? stUiRules().wallCost : kind === 'st-ramp' ? stUiRules().rampCost : config.cost;
    button.querySelector('small').textContent = (cost ? cost + ' gold' : 'Free') + (shortcut ? ' · ' + shortcut : ' · raised route');
    button.setAttribute('aria-pressed', String(stUi.build === kind));
    button.classList.toggle('active', stUi.build === kind);
  }
  $('stCancelBuild').hidden = !stUi.build;
  const ownedHouse = building && ['st-farm','st-income','st-fort'].includes(building.kind) && building.owner === state.controlledId;
  $('stUpgrade').disabled = !mayBuild || !ownedHouse || building.progress < 1;
  $('stSell').disabled = !mayBuild || !building || building.owner !== state.controlledId;
  $('stWolfUpgrade').hidden = state.role !== 'wolf';
  $('stWolfUpgrade').disabled = !!state.winner || controlled?.level >= 3;
  $('stWolfUpgrade').querySelector('small').textContent = controlled?.level >= 3 ? 'Maximum level' :
    (controlled?.upgradeCost ?? 75) + ' gold · at shop';
  $('stGold').hidden = !!state.simulate;
  $('stSelectMine').disabled = !controlled;
  for (const id of ['stFollow', 'stZoomIn', 'stZoomOut']) $(id).disabled = !!state.simulate;
  $('stFollow').setAttribute('aria-pressed', String(stUi.follow));
  stUiText('stFollow', stUi.follow ? 'Following' : 'Follow');
  stUiText('stPause', paused ? '▶ Resume' : 'Ⅱ Pause');
  stUiText('stTip', stUi.build ? 'Exact footprint shown. Tight gaps can trap you; exits are yours to plan.' : state.role === 'wolf' ?
    'Tap a visible sheep to hunt. Tap a house to demolish it.' : controlled?.captured ?
      'Float inside the pen. A free sheep can touch your wisp to rescue you.' :
      'Tap ground to move. Build houses to block wolves; reach wisps to rescue allies.');
  stUiRefreshArchive(state,controlled,building,mayBuild,now);
  stUiUpdateRings({...state, selectedId: inspectedId});
  if (state.message && state.message !== stUi.lastGameMessage) {
    stUi.lastGameMessage = state.message;
    if (now > stUi.messageUntil) stUiFeedback(state.message);
  }
  if (now > stUi.messageUntil) stUiText('stFeedback', '');
  if (force || now - stUi.lastMap > 150) {stUi.lastMap = now; stUiDrawMinimap(state);}
}
function stShowHUD(show) {
  stInstallUI();
  if (show && !stUi.shown) {
    stUi.cameraSaved = {position: perspectiveCamera.position.clone(), quaternion: perspectiveCamera.quaternion.clone(),
      up: perspectiveCamera.up.clone(), fov: perspectiveCamera.fov};
    stUi.follow = true; stUi.zoom = 1; stUi.build = null; stUi.buildingId = null; stUi.keys.clear();
    stUi.rotation = 0; stUi.route = 'ground'; stUi.lastAttack = null; stUi.attackUntil = 0; stUi.extrasOpen = false; stUi.mapReceipt = null;
    stUi.lastHud = -Infinity; stUi.lastMap = -Infinity; stUi.lastGameMessage = '';
    const state = stUiView(), controlled = state.units.find(unit => unit.id === state.controlledId);
    if (controlled) stUi.focus.set(controlled.pos[0], 0, controlled.pos[2]);
    stUiCloseRules();
    if (document.pointerLockElement) document.exitPointerLock?.();
    stUiFeedback('Your game is running in the editor. Pause or Stop at any time.');
  }
  stUi.shown = !!show; $('sheepTagHUD').hidden = !show;
  app.classList.toggle('sheep-tag-runtime', !!show);
  if (show) {stUpdateCamera(0); stRefreshHUD(true);}
}
function stDisposeUI() {
  stUi.build = null; stUi.buildingId = null; stUi.drag = null; stUi.mapReceipt = null; stUi.keys.clear(); stUiClearPreview();
  for (const ring of stUi.rings || []) {scene.remove(ring); ring.geometry.dispose(); ring.material.dispose();}
  stUi.rings = null;
  if (stUi.cameraSaved) {
    perspectiveCamera.position.copy(stUi.cameraSaved.position); perspectiveCamera.quaternion.copy(stUi.cameraSaved.quaternion);
    perspectiveCamera.up.copy(stUi.cameraSaved.up); perspectiveCamera.fov = stUi.cameraSaved.fov;
    perspectiveCamera.updateProjectionMatrix(); stUi.cameraSaved = null;
  }
  if (stUi.installed) {
    stUi.shown = false; $('sheepTagHUD').hidden = true; $('stHelpPanel').hidden = true;
    $('stHelp').setAttribute('aria-expanded', 'false'); app.classList.remove('sheep-tag-runtime');
    $('sheepTagRulesBtn').classList.toggle('hidden', currentProject?.kind !== 'sheep-tag');
  }
}
function stUiCloseRules() {
  const dialog = $('sheepTagRulesDialog'); if (!dialog || dialog.hidden) return;
  dialog.hidden = true; stUi.rulesReturnFocus?.focus(); stUi.rulesReturnFocus = null;
}
function stUiOpenRules() {
  if (stSession || currentProject?.kind !== 'sheep-tag') return;
  const rules = stUiRules();
  $('stRuleDuration').value = String(rules.duration / 60);
  $('stRuleHeadstart').value = String(rules.headstart);
  $('stRuleRole').value = rules.role;
  $('stRuleGold').value = String(rules.startGold);
  for (const input of $('sheepTagRulesDialog').querySelectorAll('[data-st-rule]')) {
    const value = rules[input.dataset.stRule];
    if (input.type === 'checkbox') input.checked = !!value;
    else input.value = String(value ?? input.dataset.stDefault ?? '');
  }
  for (const input of $('sheepTagRulesDialog').querySelectorAll('[data-st-permitted]'))
    input.checked = !rules.permittedStructures || rules.permittedStructures.includes(input.dataset.stPermitted) || rules.permittedStructures.includes(input.dataset.stPermitted.replace('st-',''));
  for (const input of $('sheepTagRulesDialog').querySelectorAll('[data-st-event]')) input.checked = (rules.eventPool || ['pressure','fog','supply']).includes(input.dataset.stEvent);
  stUiText('stRulesFeedback', 'Rules are saved with this native project.');
  stUi.rulesReturnFocus = document.activeElement;
  $('sheepTagRulesDialog').hidden = false; $('stRuleDuration').focus();
}
function stUiRuleField(key,label,min,max,step=1,defaultValue='') {
  // Keep advertised limits identical to the native saved-rule sanitizer.
  const limits = {sheepSpeed:[2,10],wolfSpeed:[2,12],wolfDamage:[20,200],attackInterval:[.25,2],
    farmHp:[80,600],incomeHp:[100,800],fortHp:[200,1600],sheepRadius:[.2,.45],wolfRadius:[.5,1],houseLimit:[9,40],
    sheepVision:[6,40],wolfVision:[6,40],rescueProtection:[0,8],rescueHold:[.2,3],thornDuration:[2,30],thornCooldown:[1,30],
    scentInterval:[1,5],densityRadius:[5,14],totemRadius:[3,10],fadeSeconds:[.5,8],revealSeconds:[.5,8],totemCooldown:[15,900],
    wallCost:[0,200],rampCost:[0,200],wallHp:[100,1200],rampHp:[100,1000],wallHeight:[2.5,4.5],splitUnlock:[2,4],
    progressionSeconds:[5,180],rescueXp:[0,100],splitCooldown:[5,120],splitLifetime:[2,12],eventInterval:[30,900],eventWarning:[5,20],eventDuration:[5,45]};
  if (limits[key]) [min,max] = limits[key];
  return `<label>${label}<input id="stTune_${key}" data-st-rule="${key}" data-st-default="${defaultValue}" type="number" min="${min}" max="${max}" step="${['houseLimit','splitUnlock','seed'].includes(key) ? 1 : 'any'}" required></label>`;
}
function stUiRulesExtras() {
  const fields = list => list.map(spec => stUiRuleField(...spec)).join('');
  const toggle = (key,label) => `<label class="st-check"><input id="stRule_${key}" data-st-rule="${key}" type="checkbox"><span>${label}</span></label>`;
  return `<div class="st-rule-fields st-presets"><label>Rules preset<select id="stRulePreset" data-st-rule="preset"><option value="classic">Classic · house maze &amp; rescue</option><option value="archive">Archive · experimental magic &amp; routes</option></select></label><label>Placement grid<select id="stRuleSnap" data-st-rule="buildSnap"><option value="0.15">Fine · 0.15 ground units</option><option value="3">Coarse · 3 ground units</option></select></label><label>Vision sharing<select id="stRuleFog" data-st-rule="fogMode"><option value="team">Team vision</option><option value="solo">Your unit only</option><option value="off">Fog off</option></select></label><label>Totem use limit<select id="stRuleTotemLimit" data-st-rule="totemLimit"><option value="once">Once per sheep per match</option><option value="cooldown">Repeat after cooldown</option></select></label></div>
    <p class="st-rules-note">Fine placement preserves narrow sheep gaps and your building mistakes. Houses can seal your escape; the game will not open a way out for you.</p>
    <fieldset class="st-rule-checks"><legend>Optional archive experiments</legend>${toggle('thorns','Thorn prick & approximate sensing')}${toggle('totems','Settlement stealth totems')}${toggle('elevated','Castle walls & walkable ramps')}${toggle('split','Level-earned Illusive Split')}${toggle('events','Special events · opt in')}</fieldset>
    <p class="st-rules-note">Archive turns on the four player ideas. Events stay off until you choose them. The values below are adjustable test settings, rather than settled balance rules.</p>
    <details class="st-tuning"><summary>Chase, houses &amp; rescue tuning</summary><div class="st-rule-fields">${fields([
      ['sheepSpeed','Sheep speed',1,20,.1,5.4],['wolfSpeed','Wolf speed',1,25,.1,7.2],
      ['wolfDamage','Wolf damage per strike',1,500,1,85],['attackInterval','Seconds between wolf strikes',.1,5,.05,.65],
      ['farmHp','House health',20,5000,1,180],['incomeHp','Income house health',20,5000,1,240],['fortHp','Fortified house health',20,10000,1,650],
      ['sheepRadius','Sheep collision radius',.1,1.5,.01,.27],['wolfRadius','Wolf collision radius',.2,2,.01,.68],
      ['houseLimit','Houses per sheep',1,150,1,28],['sheepVision','Sheep vision radius',3,80,.5,18],['wolfVision','Wolf vision radius',3,80,.5,20],
      ['rescueHold','Rescue contact · seconds',0,10,.1,.6],['rescueProtection','Protection after rescue · seconds',0,30,.5,3]
    ])}</div></details>
    <details class="st-tuning"><summary>Thorn &amp; stealth tuning</summary><div class="st-rule-fields">${fields([
      ['thornChance','Thorn prick chance · 0 to 1',0,1,.01,.35],['thornDuration','Thorn scent duration · seconds',1,120,1,15],['thornCooldown','Prick retry cooldown · seconds',.1,60,.1,6],
      ['scentInterval','Approximate scent pulse · seconds',.5,15,.5,2],['densityRadius','Nine-house settlement radius',3,30,.5,8],['totemRadius','Totem effect radius',2,30,.5,5.5],
      ['fadeSeconds','Seconds to fade into concealment',.1,15,.1,3],['revealSeconds','Seconds to become visible again',.1,15,.1,2],['totemCooldown','Repeat totem cooldown · seconds',10,1200,1,120]
    ])}</div><p>Nine allied houses in the settlement radius qualify. Convert an owned house; this adds no free building. Thorn sensing gives approximate clues, including through concealment.</p></details>
    <details class="st-tuning"><summary>Raised routes &amp; split tuning</summary><div class="st-rule-fields">${fields([
      ['wallCost','Castle wall cost · gold',0,1000,1,45],['rampCost','Ramp cost · gold',0,1000,1,55],['wallHp','Castle wall health',20,10000,1,360],['rampHp','Ramp health',20,10000,1,300],['wallHeight','Upper deck height',1,8,.1,3.3],
      ['splitUnlock','Illusive Split unlock level',1,10,1,2],['progressionSeconds','Survival seconds per level',5,600,1,45],['rescueXp','Progress earned per rescue',0,300,1,30],['splitCooldown','Split cooldown · seconds',1,180,1,30],['splitLifetime','Mirror lifetime · seconds',1,30,.5,5]
    ])}</div>${toggle('wolvesUseRamps','Wolves can use connected ramps')}<p>Upper moves need a connected ramp. Both teams can damage structures; routes can break during a chase.</p></details>
    <details class="st-tuning"><summary>Event experiments &amp; match seed</summary><div class="st-rule-fields">${fields([
      ['eventInterval','Minimum event interval · seconds',30,1200,1,150],['eventWarning','Advance warning · seconds',3,60,1,8],['eventDuration','Event duration · seconds',3,120,1,15],['seed','Match seed · 0 chooses a new one',0,2147483647,1,0]
    ])}</div><fieldset class="st-rule-checks"><legend>Candidate event pool</legend><label class="st-check"><input data-st-event="pressure" type="checkbox"><span>Hunt pressure</span></label><label class="st-check"><input data-st-event="fog" type="checkbox"><span>Deep fog</span></label><label class="st-check"><input data-st-event="supply" type="checkbox"><span>Supply windfall</span></label></fieldset><p>These effects are provisional event experiments. Every event announces its warning and duration. Seeded matches repeat random choices for testing.</p></details>
    <details class="st-tuning"><summary>Allowed player-built structures</summary><fieldset class="st-rule-checks"><legend>Available buildings</legend>${['st-farm','st-income','st-fort','st-wall','st-ramp'].map(kind => `<label class="st-check"><input data-st-permitted="${kind}" type="checkbox"><span>${stUiBuildNames[kind]}</span></label>`).join('')}</fieldset><p>Walls and ramps also require raised routes to be enabled.</p></details>`;
}
function stInstallUI() {
  if (stUi.installed) return; stUi.installed = true;
  const launcher = document.createElement('button'); launcher.id = 'sheepTagRulesBtn'; launcher.type = 'button';
  launcher.textContent = '🐑 Sheep Tag'; launcher.setAttribute('aria-haspopup', 'dialog');
  launcher.onclick = stUiOpenRules; $('playBtn').before(launcher);
  const hud = document.createElement('section'); hud.id = 'sheepTagHUD'; hud.hidden = true;
  hud.setAttribute('aria-label', 'Sheep Tag game controls');
  hud.innerHTML = `<div class="st-score"><div class="st-title"><b>Sheep Tag</b><small>MOONBELL MEADOW · <span id="stRole"></span></small></div><div class="st-readout"><b id="stTimer"></b><span id="stCounts"></span><strong id="stGold"></strong></div><div class="st-session"><button id="stPause" type="button">Ⅱ Pause</button><button id="stStop" type="button">■ Stop</button><button id="stRestart" type="button">↻ Restart</button></div></div>
    <div id="stPhase" class="st-phase" role="status" aria-live="polite"></div><div id="stEventBanner" class="st-event" role="status" aria-live="polite" hidden></div><div id="stAttackFeedback" class="st-attack-feedback" hidden></div>
    <div class="st-commandbar"><div class="st-map"><canvas id="stMinimap" width="144" height="144" aria-label="Map overview; tap to move the camera" tabindex="0"></canvas><span>Map · tap to explore</span></div><div class="st-orders"><div class="st-selection"><div><b id="stSelectedName"></b><small id="stSelectedDetail"></small><div id="stHealthTrack" class="st-health" hidden role="img"><span id="stHealthBar"></span></div></div><button id="stSelectMine" type="button">My unit</button></div><div class="st-builds"><button id="stBuildFarm" type="button" title="Q · free blocking farm"><b>House</b><small>Free · Q</small></button><button id="stBuildIncome" type="button" title="E · income farm"><b>Income house</b><small>60 gold · E</small></button><button id="stBuildFort" type="button" title="F · strong blocking farm"><b>Fortified house</b><small>100 gold · F</small></button><button id="stBuildWall" type="button" hidden><b>Castle wall</b><small>Raised route</small></button><button id="stBuildRamp" type="button" hidden><b>Ramp</b><small>Ground to deck</small></button><button id="stWolfUpgrade" type="button" hidden><b>Wolf upgrade</b><small>75 gold · at shop</small></button><button id="stCancelBuild" type="button" hidden>✕ Cancel</button></div><div class="st-farm-actions"><button id="stUpgrade" type="button">Upgrade house</button><button id="stSell" type="button">Sell / clear</button></div><div id="stPlacementTools" class="st-placement-tools" hidden><button id="stPlacementSnap" type="button">Fine: 0.15 units</button><button id="stRotatePlacement" type="button" hidden>Rotate 0°</button><span>R rotates · exact outline</span></div><div id="stPlacement" class="st-feedback st-placement"></div><button id="stMoreActions" type="button" aria-expanded="false" hidden>Magic &amp; routes</button><div id="stExtraActions" class="st-extra-actions" hidden><button id="stTotem" type="button" hidden><b>Convert to totem</b><small id="stTotemInfo"></small></button><button id="stSplit" type="button" hidden><b>Illusive Split</b><small id="stSplitInfo"></small></button><button id="stUpperRoute" type="button" aria-pressed="false" hidden>Move: ground</button><button id="stExitWall" type="button" hidden>Descend ramp</button></div><div id="stMagicReadout" class="st-magic-readout"></div><div id="stFeedback" class="st-feedback" role="status" aria-live="polite"></div><div id="stTip" class="st-tip"></div><div class="st-camera"><button id="stFollow" type="button" aria-pressed="true">Following</button><button id="stZoomIn" type="button" aria-label="Zoom camera in">＋</button><button id="stZoomOut" type="button" aria-label="Zoom camera out">−</button><button id="stHelp" type="button" aria-expanded="false">How to play</button><span>Drag to pan · WASD / arrows</span></div></div></div>
    <aside id="stHelpPanel" hidden><b>Survive the hunt</b><p>Sheep win when the timer runs out with a free sheep remaining. Wolves win when every sheep is captured at the same time.</p><p>Houses create mazes. Sheep can fit through smaller gaps than wolves. Place precisely: a too-tight gap can trap you. Income houses earn gold; fortified houses take more hits. Select your own house to upgrade or sell it.</p><p>A captured sheep becomes a glowing wisp in the center pen. A free sheep must reach that wisp to rescue its teammate. Wisps cannot build.</p><p>Tap ground to move; tap units or farms to select them. As a wolf, tap a visible sheep or house to attack. Watch its health fall; demolition opens a breach. Breaking houses and tagging sheep earns bounty gold; visit a corner merchant to upgrade your wolf. This starter runs with AI teammates and opponents.</p><p>Archive experiments: convert an owned house when nine allied houses are nearby, unlock Illusive Split through survival and rescues, or use a connected ramp to reach an upper wall. Thorn scent clues are approximate; hidden enemies do not appear on the map. Events give an advance warning.</p><p>Camera: drag on a phone; right-drag or Space + drag on desktop. The map moves the camera. Follow returns to your selected unit.</p><button id="stHelpClose" type="button">Back to game</button></aside>`;
  $('viewport').parentElement.appendChild(hud);
  $('stPause').onclick = () => $('pauseBtn').click();
  $('stStop').onclick = () => $('stopBtn').click();
  $('stRestart').onclick = () => {const simulate = !!stSession?.simulate; $('stopBtn').click(); $(simulate ? 'simulateBtn' : 'playBtn').click();};
  for (const [id, kind] of stUiBuildButtons) $(id).onclick = () => stUiChooseBuild(kind);
  $('stCancelBuild').onclick = () => {stUi.build = null; stUiClearPreview(); stRefreshHUD(true);};
  $('stSelectMine').onclick = () => {const state = stUiView(); stUi.buildingId = null; stUiCommand('select', {id: state.controlledId}); stUi.follow = true; stRefreshHUD(true);};
  $('stUpgrade').onclick = () => {const result = stUiCommand('upgrade', {id: stUi.buildingId || stUiView().selectedId}); if (result?.ok) stUiFeedback('House upgrade ordered.');};
  $('stSell').onclick = () => {const result = stUiCommand('sell', {id: stUi.buildingId || stUiView().selectedId}); if (result?.ok) {stUi.buildingId = null; stUiFeedback('House cleared. Refunded ' + (result.refund || 0) + ' gold.');}};
  $('stWolfUpgrade').onclick = () => {const result = stUiCommand('wolf-upgrade'); if (result?.ok) stUiFeedback('Wolf upgraded.');};
  $('stTotem').onclick = () => {const result = stUiCommand('totem', {id: stUi.buildingId || stUiView().selectedId}); if (result?.ok) stUiFeedback('House converted to a stealth totem. Stay nearby to fade into cover.');};
  $('stSplit').onclick = () => {stUi.buildingId = null; stUiCommand('select',{id:stUiView().controlledId}); const result = stUiCommand('split'); if (result?.ok) stUiFeedback('Illusive Split! The mirror takes another escape path.');};
  $('stUpperRoute').onclick = () => {stUi.buildingId = null; stUiCommand('select',{id:stUiView().controlledId}); stUi.route = stUi.route === 'upper' ? 'ground' : 'upper'; stRefreshHUD(true); stUiFeedback(stUi.route === 'upper' ? 'Tap an upper wall destination. Your unit needs a connected ramp to reach it.' : 'Ground movement selected.');};
  $('stExitWall').onclick = () => {stUi.buildingId = null; stUiCommand('select',{id:stUiView().controlledId}); const result = stUiCommand('exit-wall'); if (result?.ok) {stUi.route = 'ground'; stUiFeedback('Descending by a connected ramp.');}};
  $('stMoreActions').onclick = () => {stUi.extrasOpen = !stUi.extrasOpen; stRefreshHUD(true);};
  $('stRotatePlacement').onclick = () => stUiRotatePlacement();
  $('stPlacementSnap').onclick = () => {
    const next = stUiRules().buildSnap === 3 ? .15 : 3;
    const result = stUiCommand('build-snap',{value:next});
    if (result?.ok) {if (stUi.placementPoint) stUiPlacePreview(stUi.placementPoint); stUiFeedback(next === 3 ? 'Coarse 3-unit placement grid.' : 'Fine 0.15-unit placement. Check narrow gaps carefully.');}
  };
  $('stFollow').onclick = () => {stUi.follow = !stUi.follow; stRefreshHUD(true);};
  $('stZoomIn').onclick = () => {stUi.zoom = Math.max(.65, stUi.zoom / 1.18); stUpdateCamera(0);};
  $('stZoomOut').onclick = () => {stUi.zoom = Math.min(1.85, stUi.zoom * 1.18); stUpdateCamera(0);};
  $('stHelp').onclick = () => {$('stHelpPanel').hidden = !$('stHelpPanel').hidden; $('stHelp').setAttribute('aria-expanded', String(!$('stHelpPanel').hidden));};
  $('stHelpClose').onclick = () => {$('stHelpPanel').hidden = true; $('stHelp').setAttribute('aria-expanded', 'false'); $('stHelp').focus();};
  $('stMinimap').addEventListener('pointerdown', event => {
    if (!stSession) return; event.preventDefault(); event.stopPropagation();
    const rect = event.currentTarget.getBoundingClientRect(), bounds = stUiRules().bounds || 40;
    stCameraFocus({x: (event.clientX - rect.left) / rect.width * bounds * 2 - bounds,
      z: (event.clientY - rect.top) / rect.height * bounds * 2 - bounds}); stUpdateCamera(0);
  });
  const rules = document.createElement('div'); rules.id = 'sheepTagRulesDialog'; rules.hidden = true;
  rules.innerHTML = `<section class="st-rules" role="dialog" aria-modal="true" aria-labelledby="stRulesTitle"><header><div><small>STARTER GAME MODE</small><h2 id="stRulesTitle">Sheep Tag · Moonbell Meadow</h2></div><button id="stRulesClose" type="button">Close</button></header><p>Build precise house mazes, breach them as a wolf, and rescue captured wisps. Play either role with AI teammates and opponents.</p><div class="st-rule-fields"><label>Survival time · minutes<input id="stRuleDuration" type="number" min="0.5" max="60" step="any"></label><label>Sheep head start · seconds<input id="stRuleHeadstart" type="number" min="0" max="120" step="1"></label><label>Your role<select id="stRuleRole"><option value="sheep">Sheep · build and rescue</option><option value="wolf">Wolf · hunt and destroy</option></select></label><label>Starting gold<input id="stRuleGold" type="number" min="0" max="1000" step="any"></label></div>${stUiRulesExtras()}<p class="st-rules-note">Sheep shelter behind houses and rescue captured wisps from the center. Wolves break houses to reach them. The native Play, Pause, and Stop buttons run the game.</p><div class="st-rule-actions"><button id="stRulesApply" type="button">Save rules</button><button id="stRulesPlay" type="button">Save &amp; Play</button></div><div class="st-rule-actions"><button id="stRulesSave" type="button">Save project file</button><button id="stRulesLoad" type="button">Load project file</button></div><div id="stRulesFeedback" role="status" aria-live="polite"></div><details><summary>Add map pieces in the editor</summary><p>These are native actors. Place, rotate, group, undo, and save them with the editor.</p><div class="st-prefabs"><button data-st-prefab="st-sheep" type="button">Sheep spawn</button><button data-st-prefab="st-wolf" type="button">Wolf spawn</button><button data-st-prefab="st-pen" type="button">Wisp pen</button><button data-st-prefab="st-farm" type="button">House</button><button data-st-prefab="st-income" type="button">Income house</button><button data-st-prefab="st-fort" type="button">Fortified house</button><button data-st-prefab="st-tree" type="button">Tree</button><button data-st-prefab="st-rock" type="button">Rock</button><button data-st-prefab="st-shop" type="button">Merchant shop</button><button data-st-prefab="st-pond" type="button">Pond</button><button data-st-prefab="st-thorn" type="button">Thorn bush</button><button data-st-prefab="st-wall" type="button">Castle wall</button><button data-st-prefab="st-ramp" type="button">Ramp</button><button data-st-prefab="st-zone" type="button">No-build zone</button></div></details></section>`;
  document.body.appendChild(rules);
  $('stRulesClose').onclick = stUiCloseRules;
  rules.addEventListener('pointerdown', event => {if (event.target === rules) stUiCloseRules();});
  // Stop the editor's W/E/R/Delete shortcuts while the modal owns focus.
  rules.addEventListener('keydown', event => event.stopPropagation());
  $('stRulePreset').onchange = () => {
    const archive = $('stRulePreset').value === 'archive';
    for (const key of ['thorns','totems','elevated','split']) $('stRule_' + key).checked = archive;
    $('stRule_events').checked = false;
    stUiText('stRulesFeedback', archive ? 'Archive experiments selected. Events remain off; tune and test these settings.' : 'Classic selected. Advanced experiments and events are off.');
  };
  const applyRules = play => {
    for (const input of rules.querySelectorAll('input')) {
      if (input.type === 'checkbox') continue;
      if (!input.value || !input.checkValidity()) {
        const details = input.closest('details'); if (details) details.open = true;
        input.reportValidity(); stUiText('stRulesFeedback', 'Enter rule values within the displayed limits.'); return false;
      }
    }
    const patch = {duration: Number($('stRuleDuration').value) * 60, headstart: Number($('stRuleHeadstart').value),
      role: $('stRuleRole').value, startGold: Number($('stRuleGold').value)};
    for (const input of rules.querySelectorAll('[data-st-rule]')) {
      const key = input.dataset.stRule;
      patch[key] = input.type === 'checkbox' ? input.checked : input.type === 'number' || key === 'buildSnap' ? Number(input.value) : input.value;
    }
    patch.permittedStructures = [...rules.querySelectorAll('[data-st-permitted]:checked')].map(input => input.dataset.stPermitted);
    patch.eventPool = [...rules.querySelectorAll('[data-st-event]:checked')].map(input => input.dataset.stEvent);
    if (patch.events && !patch.eventPool.length) {stUiText('stRulesFeedback','Select at least one event, or turn special events off.'); return false;}
    const result = stConfigureRules(patch);
    if (result === false || result?.ok === false) {stUiText('stRulesFeedback', result?.reason || 'Check the rule values.'); return false;}
    const saved = result?.rules;
    if (saved) {
      $('stRuleHeadstart').value = String(saved.headstart);
      for (const input of rules.querySelectorAll('[data-st-rule]')) {
        if (input.type === 'checkbox') input.checked = !!saved[input.dataset.stRule];
        else input.value = String(saved[input.dataset.stRule] ?? input.value);
      }
    }
    stUiText('stRulesFeedback', 'Rules saved. Use the native Save button to keep your project.');
    if (play) {stUiCloseRules(); $('playBtn').click();}
    return true;
  };
  $('stRulesApply').onclick = () => applyRules(false); $('stRulesPlay').onclick = () => applyRules(true);
  $('stRulesSave').onclick = () => {if (applyRules(false)) {$('saveBtn').click(); stUiText('stRulesFeedback', 'Saved a native project file with the map, layers, and rules.');}};
  $('stRulesLoad').onclick = () => {stUiCloseRules(); $('loadBtn').click();};
  for (const button of rules.querySelectorAll('[data-st-prefab]')) button.onclick = () => {
    const id = window.SWYRL_ENGINE_AGENT.spawn(button.dataset.stPrefab);
    stUiText('stRulesFeedback', id ? 'Added ' + button.textContent + '. Close this panel to position it in the editor.' : 'Could not create this actor.');
  };
  const viewport = $('viewport');
  viewport.addEventListener('contextmenu', event => {if (stSession && !stSession.simulate) {event.preventDefault(); event.stopImmediatePropagation();}}, true);
  viewport.addEventListener('pointerdown', event => {
    if (!stSession || stSession.simulate) return;
    event.preventDefault(); event.stopImmediatePropagation(); viewport.focus();
    stUi.drag = {id: event.pointerId, x: event.clientX, y: event.clientY,
      lastX: event.clientX, lastY: event.clientY, touch: event.pointerType === 'touch',
      pan: event.button === 2 || stUi.keys.has(' '), moved: false};
    viewport.setPointerCapture?.(event.pointerId); stUiPlacePreview(stUiGround(event.clientX, event.clientY));
  }, true);
  viewport.addEventListener('pointermove', event => {
    if (!stSession || stSession.simulate) return;
    event.preventDefault(); event.stopImmediatePropagation();
    const drag = stUi.drag;
    if (drag && drag.id === event.pointerId) {
      if (Math.hypot(event.clientX - drag.x, event.clientY - drag.y) > 9) {drag.moved = true; if (drag.touch && !stUi.build) drag.pan = true;}
      if (drag.pan) stUiPan(event.clientX - drag.lastX, event.clientY - drag.lastY);
      drag.lastX = event.clientX; drag.lastY = event.clientY;
    }
    stUiPlacePreview(stUiGround(event.clientX, event.clientY));
  }, true);
  viewport.addEventListener('pointerup', event => {
    if (!stSession || stSession.simulate) return;
    event.preventDefault(); event.stopImmediatePropagation();
    const drag = stUi.drag; stUi.drag = null;
    if (drag && drag.id === event.pointerId && !drag.pan && (!drag.moved || stUi.build)) stUiOrderAt(event.clientX, event.clientY);
    if (viewport.hasPointerCapture?.(event.pointerId)) viewport.releasePointerCapture(event.pointerId);
  }, true);
  viewport.addEventListener('pointercancel', event => {if (stSession) {stUi.drag = null; event.stopImmediatePropagation();}}, true);
  viewport.addEventListener('wheel', event => {
    if (!stSession || stSession.simulate) return; event.preventDefault(); event.stopImmediatePropagation();
    stUi.zoom = THREE.MathUtils.clamp(stUi.zoom * (event.deltaY > 0 ? 1.08 : 1 / 1.08), .65, 1.85);
  }, {capture: true, passive: false});
  window.addEventListener('keydown', event => {
    if (!$('sheepTagRulesDialog').hidden) {
      if (event.key === 'Escape') {event.preventDefault(); event.stopImmediatePropagation(); stUiCloseRules();}
      if (event.key === 'Tab') {
        const focusable = [...$('sheepTagRulesDialog').querySelectorAll('button,input,select,summary')].filter(node => !node.disabled && node.getClientRects().length);
        const first = focusable[0], last = focusable[focusable.length - 1];
        if (event.shiftKey && document.activeElement === first) {event.preventDefault(); last?.focus();}
        else if (!event.shiftKey && document.activeElement === last) {event.preventDefault(); first?.focus();}
      }
      return;
    }
    if (!stSession || stSession.simulate || event.target?.closest?.('#stCreatorPanel') || ['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement?.tagName) || document.activeElement?.isContentEditable) return;
    const key = event.key.toLowerCase();
    if (['w', 'a', 's', 'd', 'arrowup', 'arrowdown', 'arrowleft', 'arrowright', ' ', 'q', 'e', 'f', 'r', 'escape'].includes(key)) {
      event.preventDefault(); event.stopImmediatePropagation(); stUi.keys.add(key);
      if (event.repeat) return;
      if (key === 'q') stUiChooseBuild('st-farm'); if (key === 'e') stUiChooseBuild('st-income'); if (key === 'f') stUiChooseBuild('st-fort');
      if (key === 'r') stUiRotatePlacement();
      if (key === 'escape') {stUi.build = null; stUiClearPreview(); $('stHelpPanel').hidden = true; stRefreshHUD(true);}
    }
  }, true);
  window.addEventListener('keyup', event => {stUi.keys.delete(event.key.toLowerCase());}, true);
  window.addEventListener('blur', () => {stUi.keys.clear(); stUi.drag = null;});
  const projectName = $('currentProjectName');
  if (projectName) new MutationObserver(() => {stRefreshHUD(true); if (currentProject?.kind !== 'sheep-tag') stUiCloseRules();})
    .observe(projectName, {childList: true, characterData: true, subtree: true});
  stRefreshHUD(true);
}
