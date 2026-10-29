// Sheep Tag controls live inside the native editor session. No pointer lock,
// extra render loop, or saved actors are created by the HUD and build preview.
const stUi = {
  installed: false, shown: false, build: null, preview: null, placement: null,
  follow: true, focus: new THREE.Vector3(), zoom: 1, keys: new Set(), drag: null,
  buildingId: null, lastHud: -Infinity, lastMap: -Infinity, messageUntil: 0,
  cameraSaved: null, rulesReturnFocus: null, rings: null, lastGameMessage: ''
};
const stUiBuildNames = {'st-farm': 'Farm', 'st-income': 'Income farm', 'st-fort': 'Fortified farm'};
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
  stUi.preview = null; stUi.placement = null;
}
function stUiChooseBuild(kind) {
  if (!stSession) return;
  const state = stStatus(), controlled = state.units.find(unit => unit.id === state.controlledId);
  if (state.role !== 'sheep' || !controlled || controlled.captured || controlled.kind !== 'sheep') {
    stUiFeedback('Only a free sheep can build farms.', true); return;
  }
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
    stUiFeedback('Tap open ground to place a ' + stUiBuildNames[kind].toLowerCase() + '. Green fits; red is blocked.');
  } else stUiFeedback('Build placement cancelled.');
  stRefreshHUD(true);
}
function stUiGround(clientX, clientY) {
  const rect = $('viewport').getBoundingClientRect();
  if (!rect.width || !rect.height) return null;
  const pointer = new THREE.Vector2((clientX - rect.left) / rect.width * 2 - 1,
    -(clientY - rect.top) / rect.height * 2 + 1);
  const ray = new THREE.Raycaster(); ray.setFromCamera(pointer, camera);
  return ray.ray.intersectPlane(new THREE.Plane(new THREE.Vector3(0, 1, 0), 0), new THREE.Vector3());
}
function stUiPlacePreview(point) {
  if (!stUi.preview || !stUi.build || !point) return;
  const fit = stCanBuild(stUi.build, point.x, point.z);
  stUi.placement = fit;
  stUi.preview.position.set(Number.isFinite(fit.x) ? fit.x : point.x, 0,
    Number.isFinite(fit.z) ? fit.z : point.z);
  stUi.preview.visible = true;
  stUi.preview.traverse(object => {
    const materials = Array.isArray(object.material) ? object.material : [object.material];
    for (const material of materials) {
      if (material?.color) material.color.set(fit.ok ? 0x83ebb2 : 0xff7777);
      if (material?.emissive) material.emissive.set(fit.ok ? 0x10381d : 0x481414);
    }
  });
}
function stUiPick(clientX, clientY, state) {
  const rect = $('viewport').getBoundingClientRect();
  let nearest = null, best = matchMedia('(pointer:coarse)').matches ? 34 : 24;
  for (const entity of [...state.units, ...state.buildings]) {
    if (!entity.pos) continue;
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
  const point = stUiGround(clientX, clientY); if (!point) return;
  if (stUi.build) {
    stUiPlacePreview(point);
    const fit = stUi.placement;
    if (!fit?.ok) {stUiFeedback(fit?.reason || 'This farm does not fit here.', true); return;}
    const result = stUiCommand('build', {kind: stUi.build, x: fit.x, z: fit.z});
    if (result?.ok) {
      stUiFeedback('Farm ordered. Your sheep will walk over and build it.');
      stUi.build = null; stUiClearPreview(); stRefreshHUD(true);
    }
    return;
  }
  const state = stStatus(), entity = stUiPick(clientX, clientY, state);
  if (entity) {
    if (state.role === 'wolf' && (entity.kind === 'sheep' || entity.kind.startsWith('st-'))) {
      stUiCommand('select', {id: state.controlledId});
      const result = stUiCommand('attack', {id: entity.id});
      if (result?.ok) stUiFeedback('Hunt order issued.');
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
    const result = stUiCommand('move', {x: point.x, z: point.z});
    if (result?.ok) stUiFeedback('Move order issued.');
  }
}
function stCameraFocus(position) {
  const x = Array.isArray(position) ? position[0] : position?.x;
  const z = Array.isArray(position) ? position[2] : position?.z;
  if (!Number.isFinite(x) || !Number.isFinite(z)) return false;
  const bounds = stRules().bounds || 40;
  stUi.focus.set(THREE.MathUtils.clamp(x, -bounds, bounds), 0,
    THREE.MathUtils.clamp(z, -bounds, bounds));
  stUi.follow = false; stRefreshHUD(true); return true;
}
function stUiPan(dx, dy) {
  const rect = $('viewport').getBoundingClientRect();
  const distance = perspectiveCamera.position.distanceTo(stUi.focus);
  const worldHeight = 2 * distance * Math.tan(THREE.MathUtils.degToRad(perspectiveCamera.fov) / 2);
  const scale = worldHeight / Math.max(1, rect.height);
  const bounds = stRules().bounds || 40;
  stUi.follow = false;
  stUi.focus.x = THREE.MathUtils.clamp(stUi.focus.x - dx * scale, -bounds, bounds);
  stUi.focus.z = THREE.MathUtils.clamp(stUi.focus.z - dy * scale * 1.28, -bounds, bounds);
}
function stUpdateCamera(dt = 0) {
  if (!stSession || stSession.simulate) return;
  const state = stStatus();
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
  const bounds = stRules().bounds || 40;
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
    ring.position.set(entity.pos[0], terrainHeight(entity.pos[0], entity.pos[2]) + .035 + index * .004, entity.pos[2]);
    const scale = entity.kind.startsWith('st-') ? 1.6 : entity.kind === 'wolf' ? 1.25 : 1;
    ring.scale.setScalar(scale);
  }
}
function stUiDrawMinimap(state) {
  const canvas = $('stMinimap'), context = canvas?.getContext('2d'); if (!context) return;
  const size = canvas.width, bounds = stRules().bounds || 40;
  const xy = pos => [(pos[0] + bounds) / (bounds * 2) * size, (pos[2] + bounds) / (bounds * 2) * size];
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
  for (const actor of actors) {
    if (actor.userData.actorType !== 'st-tree' && actor.userData.actorType !== 'st-rock') continue;
    const [x, y] = xy(actor.position.toArray()); context.fillStyle = actor.userData.actorType === 'st-tree' ? '#325d39' : '#677467';
    context.fillRect(x - 1.5, y - 1.5, 3, 3);
  }
  for (const building of state.buildings) {
    const [x, y] = xy(building.pos); context.fillStyle = building.kind === 'st-income' ? '#eac666' : '#a9c0a1';
    context.fillRect(x - 2.5, y - 2.5, 5, 5);
  }
  for (const unit of state.units) {
    const [x, y] = xy(unit.pos);
    context.fillStyle = unit.kind === 'wolf' ? '#ef927f' : unit.captured || unit.kind === 'wisp' ? '#76deee' : '#fff4cc';
    context.beginPath(); context.arc(x, y, unit.controlled ? 3.5 : 2.5, 0, Math.PI * 2); context.fill();
    if (unit.id === state.selectedId) {context.strokeStyle = '#fff'; context.stroke();}
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
}
function stRefreshHUD(force = false) {
  const starter = currentProject?.kind === 'sheep-tag';
  $('sheepTagRulesBtn')?.classList.toggle('hidden', !starter || !!stSession);
  if (!stSession || !stUi.shown) return;
  const now = performance.now(); if (!force && now - stUi.lastHud < 100) return; stUi.lastHud = now;
  const state = stStatus();
  const inspectedId = state.simulate ? selected?.userData.id : state.selectedId;
  const unit = state.units.find(item => item.id === inspectedId);
  const building = state.buildings.find(item => item.id === (stUi.buildingId || state.selectedId));
  const controlled = state.units.find(item => item.id === state.controlledId);
  const free = state.units.filter(item => item.kind === 'sheep' && !item.captured).length;
  const wisps = state.units.filter(item => item.captured || item.kind === 'wisp').length;
  stUiText('stTimer', stUiClock(state.remaining)); stUiText('stGold', Math.floor(state.gold || 0) + ' gold');
  stUiText('stCounts', free + ' free · ' + wisps + ' wisps');
  stUiText('stRole', state.role === 'wolf' ? 'WOLF' : 'SHEEP');
  const phase = state.winner ? (state.winner === 'sheep' ? 'The flock survived!' : 'The wolves caught the flock!') :
    paused ? 'Paused' : state.headstartRemaining > 0 ? 'Wolves released in ' + stUiClock(state.headstartRemaining) :
      controlled?.captured ? 'You are a wisp · wait for a teammate to rescue you' : 'The hunt is on';
  stUiText('stPhase', phase); $('stPhase')?.classList.toggle('finished', !!state.winner);
  stUiText('stSelectedName', building ? stUiBuildNames[building.kind] : unit?.name || 'Select a unit');
  const order = typeof unit?.order === 'string' ? unit.order : unit?.order?.action || unit?.order?.type;
  const detail = building ? Math.ceil(building.hp) + '/' + building.maxHp + ' HP · ' +
    (building.progress < 1 ? 'building ' + Math.round(building.progress * 100) + '%' : 'level ' + (building.level || 1)) :
    unit ? (unit.captured || unit.kind === 'wisp' ? 'Captured wisp · center pen' : unit.controlled ? 'Your ' + unit.kind : 'AI ' + unit.kind) +
      (order ? ' · ' + order : '') : 'Tap sheep, wolves, or farms to inspect them.';
  stUiText('stSelectedDetail', detail);
  const mayBuild = state.role === 'sheep' && controlled?.kind === 'sheep' && !controlled.captured && !state.winner;
  for (const [id, kind] of [['stBuildFarm', 'st-farm'], ['stBuildIncome', 'st-income'], ['stBuildFort', 'st-fort']]) {
    const button = $(id); if (!button) continue;
    button.disabled = !mayBuild;
    const config = ST_BUILDINGS[kind];
    const shortcut = { 'st-farm': 'Q', 'st-income': 'E', 'st-fort': 'F' }[kind];
    button.querySelector('small').textContent = (config.cost ? config.cost + ' gold' : 'Free') + ' · ' + shortcut;
    button.setAttribute('aria-pressed', String(stUi.build === kind));
    button.classList.toggle('active', stUi.build === kind);
  }
  $('stCancelBuild').hidden = !stUi.build;
  $('stUpgrade').disabled = !mayBuild || !building || building.owner !== state.controlledId || building.progress < 1;
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
  stUiText('stTip', stUi.build ? 'Place a farm on open ground. Escape cancels.' : state.role === 'wolf' ?
    'Tap a sheep to hunt. Tap a farm to break its wall.' : controlled?.captured ?
      'Float inside the pen. A free sheep can touch your wisp to rescue you.' :
      'Tap ground to move. Build farms to block wolves; reach wisps to rescue allies.');
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
    stUi.lastHud = -Infinity; stUi.lastMap = -Infinity; stUi.lastGameMessage = '';
    const state = stStatus(), controlled = state.units.find(unit => unit.id === state.controlledId);
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
  stUi.build = null; stUi.buildingId = null; stUi.drag = null; stUi.keys.clear(); stUiClearPreview();
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
  const rules = stRules();
  $('stRuleDuration').value = String(rules.duration / 60);
  $('stRuleHeadstart').value = String(rules.headstart);
  $('stRuleRole').value = rules.role;
  $('stRuleGold').value = String(rules.startGold);
  stUiText('stRulesFeedback', 'Rules are saved with this native project.');
  stUi.rulesReturnFocus = document.activeElement;
  $('sheepTagRulesDialog').hidden = false; $('stRuleDuration').focus();
}
function stInstallUI() {
  if (stUi.installed) return; stUi.installed = true;
  const launcher = document.createElement('button'); launcher.id = 'sheepTagRulesBtn'; launcher.type = 'button';
  launcher.textContent = '🐑 Sheep Tag'; launcher.setAttribute('aria-haspopup', 'dialog');
  launcher.onclick = stUiOpenRules; $('playBtn').before(launcher);
  const hud = document.createElement('section'); hud.id = 'sheepTagHUD'; hud.hidden = true;
  hud.setAttribute('aria-label', 'Sheep Tag game controls');
  hud.innerHTML = `<div class="st-score"><div class="st-title"><b>Sheep Tag</b><small>MOONBELL MEADOW · <span id="stRole"></span></small></div><div class="st-readout"><b id="stTimer"></b><span id="stCounts"></span><strong id="stGold"></strong></div><div class="st-session"><button id="stPause" type="button">Ⅱ Pause</button><button id="stStop" type="button">■ Stop</button><button id="stRestart" type="button">↻ Restart</button></div></div>
    <div id="stPhase" class="st-phase" role="status" aria-live="polite"></div>
    <div class="st-commandbar"><div class="st-map"><canvas id="stMinimap" width="144" height="144" aria-label="Map overview; tap to move the camera" tabindex="0"></canvas><span>Map · tap to explore</span></div><div class="st-orders"><div class="st-selection"><div><b id="stSelectedName"></b><small id="stSelectedDetail"></small></div><button id="stSelectMine" type="button">My unit</button></div><div class="st-builds"><button id="stBuildFarm" type="button" title="Q · free blocking farm"><b>Farm</b><small>Free · Q</small></button><button id="stBuildIncome" type="button" title="E · income farm"><b>Income farm</b><small>60 gold · E</small></button><button id="stBuildFort" type="button" title="F · strong blocking farm"><b>Fortified farm</b><small>100 gold · F</small></button><button id="stWolfUpgrade" type="button" hidden><b>Wolf upgrade</b><small>75 gold · at shop</small></button><button id="stCancelBuild" type="button" hidden>✕ Cancel</button></div><div class="st-farm-actions"><button id="stUpgrade" type="button">Upgrade farm</button><button id="stSell" type="button">Sell / clear farm</button></div><div id="stFeedback" class="st-feedback" role="status" aria-live="polite"></div><div id="stTip" class="st-tip"></div><div class="st-camera"><button id="stFollow" type="button" aria-pressed="true">Following</button><button id="stZoomIn" type="button" aria-label="Zoom camera in">＋</button><button id="stZoomOut" type="button" aria-label="Zoom camera out">−</button><button id="stHelp" type="button" aria-expanded="false">How to play</button><span>Drag to pan · WASD / arrows</span></div></div></div>
    <aside id="stHelpPanel" hidden><b>Survive the hunt</b><p>Sheep win when the timer runs out with a free sheep remaining. Wolves win when every sheep is captured at the same time.</p><p>Farms create walls. Income farms earn gold; fortified farms take more hits. Place a farm, then your sheep walks over to construct it. Select your own farm to upgrade it or sell it to reopen a path.</p><p>A captured sheep becomes a glowing wisp in the center pen. A free sheep must reach that wisp to rescue its teammate. Wisps cannot build.</p><p>Tap ground to move; tap units or farms to select them. As a wolf, tap a sheep or farm to attack. Breaking farms and tagging sheep earns bounty gold; visit a corner merchant to upgrade your wolf. This starter runs with AI teammates and opponents.</p><p>Camera: drag on a phone; right-drag or Space + drag on desktop. The map moves the camera. Follow returns to your selected unit.</p><button id="stHelpClose" type="button">Back to game</button></aside>`;
  $('viewport').parentElement.appendChild(hud);
  $('stPause').onclick = () => $('pauseBtn').click();
  $('stStop').onclick = () => $('stopBtn').click();
  $('stRestart').onclick = () => {const simulate = !!stSession?.simulate; $('stopBtn').click(); $(simulate ? 'simulateBtn' : 'playBtn').click();};
  for (const [id, kind] of [['stBuildFarm', 'st-farm'], ['stBuildIncome', 'st-income'], ['stBuildFort', 'st-fort']]) $(id).onclick = () => stUiChooseBuild(kind);
  $('stCancelBuild').onclick = () => {stUi.build = null; stUiClearPreview(); stRefreshHUD(true);};
  $('stSelectMine').onclick = () => {const state = stStatus(); stUi.buildingId = null; stUiCommand('select', {id: state.controlledId}); stUi.follow = true; stRefreshHUD(true);};
  $('stUpgrade').onclick = () => {const result = stUiCommand('upgrade', {id: stUi.buildingId || stStatus().selectedId}); if (result?.ok) stUiFeedback('Farm upgrade ordered.');};
  $('stSell').onclick = () => {const result = stUiCommand('sell', {id: stUi.buildingId || stStatus().selectedId}); if (result?.ok) {stUi.buildingId = null; stUiFeedback('Farm cleared. Refunded ' + (result.refund || 0) + ' gold.');}};
  $('stWolfUpgrade').onclick = () => {const result = stUiCommand('wolf-upgrade'); if (result?.ok) stUiFeedback('Wolf upgraded.');};
  $('stFollow').onclick = () => {stUi.follow = !stUi.follow; stRefreshHUD(true);};
  $('stZoomIn').onclick = () => {stUi.zoom = Math.max(.65, stUi.zoom / 1.18); stUpdateCamera(0);};
  $('stZoomOut').onclick = () => {stUi.zoom = Math.min(1.85, stUi.zoom * 1.18); stUpdateCamera(0);};
  $('stHelp').onclick = () => {$('stHelpPanel').hidden = !$('stHelpPanel').hidden; $('stHelp').setAttribute('aria-expanded', String(!$('stHelpPanel').hidden));};
  $('stHelpClose').onclick = () => {$('stHelpPanel').hidden = true; $('stHelp').setAttribute('aria-expanded', 'false'); $('stHelp').focus();};
  $('stMinimap').addEventListener('pointerdown', event => {
    if (!stSession) return; event.preventDefault(); event.stopPropagation();
    const rect = event.currentTarget.getBoundingClientRect(), bounds = stRules().bounds || 40;
    stCameraFocus({x: (event.clientX - rect.left) / rect.width * bounds * 2 - bounds,
      z: (event.clientY - rect.top) / rect.height * bounds * 2 - bounds}); stUpdateCamera(0);
  });
  const rules = document.createElement('div'); rules.id = 'sheepTagRulesDialog'; rules.hidden = true;
  rules.innerHTML = `<section class="st-rules" role="dialog" aria-modal="true" aria-labelledby="stRulesTitle"><header><div><small>STARTER GAME MODE</small><h2 id="stRulesTitle">Sheep Tag · Moonbell Meadow</h2></div><button id="stRulesClose" type="button">Close</button></header><p>A classic Sheep Tag inspired survival map. Play a sheep builder or a hunting wolf, with AI for the other players.</p><div class="st-rule-fields"><label>Survival time · minutes<input id="stRuleDuration" type="number" min="0.5" max="60" step="0.5"></label><label>Sheep head start · seconds<input id="stRuleHeadstart" type="number" min="0" max="120" step="1"></label><label>Your role<select id="stRuleRole"><option value="sheep">Sheep · build and rescue</option><option value="wolf">Wolf · hunt and destroy</option></select></label><label>Starting gold<input id="stRuleGold" type="number" min="0" max="1000" step="10"></label></div><p class="st-rules-note">Sheep hide behind farms and rescue captured wisps from the center. Wolves break farms to reach them. The native Play, Pause, and Stop buttons run the game.</p><div class="st-rule-actions"><button id="stRulesApply" type="button">Save rules</button><button id="stRulesPlay" type="button">Save &amp; Play</button></div><div class="st-rule-actions"><button id="stRulesSave" type="button">Save project file</button><button id="stRulesLoad" type="button">Load project file</button></div><div id="stRulesFeedback" role="status" aria-live="polite"></div><details><summary>Add map pieces in the editor</summary><p>These are native actors. Place, rotate, group, undo, and save them with the editor.</p><div class="st-prefabs"><button data-st-prefab="st-sheep" type="button">Sheep spawn</button><button data-st-prefab="st-wolf" type="button">Wolf spawn</button><button data-st-prefab="st-pen" type="button">Wisp pen</button><button data-st-prefab="st-farm" type="button">Farm</button><button data-st-prefab="st-income" type="button">Income farm</button><button data-st-prefab="st-fort" type="button">Fortified farm</button><button data-st-prefab="st-tree" type="button">Tree</button><button data-st-prefab="st-rock" type="button">Rock</button><button data-st-prefab="st-shop" type="button">Merchant shop</button><button data-st-prefab="st-pond" type="button">Pond</button></div></details></section>`;
  document.body.appendChild(rules);
  $('stRulesClose').onclick = stUiCloseRules;
  rules.addEventListener('pointerdown', event => {if (event.target === rules) stUiCloseRules();});
  // Stop the editor's W/E/R/Delete shortcuts while the modal owns focus.
  rules.addEventListener('keydown', event => event.stopPropagation());
  const applyRules = play => {
    for (const input of rules.querySelectorAll('input')) {
      if (!input.value || !input.reportValidity()) {stUiText('stRulesFeedback', 'Enter rule values within the displayed limits.'); return false;}
    }
    const patch = {duration: Number($('stRuleDuration').value) * 60, headstart: Number($('stRuleHeadstart').value),
      role: $('stRuleRole').value, startGold: Number($('stRuleGold').value)};
    const result = stConfigureRules(patch);
    if (result === false || result?.ok === false) {stUiText('stRulesFeedback', result?.reason || 'Check the rule values.'); return false;}
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
    if (!stSession || stSession.simulate || ['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement?.tagName) || document.activeElement?.isContentEditable) return;
    const key = event.key.toLowerCase();
    if (['w', 'a', 's', 'd', 'arrowup', 'arrowdown', 'arrowleft', 'arrowright', ' ', 'q', 'e', 'f', 'escape'].includes(key)) {
      event.preventDefault(); event.stopImmediatePropagation(); stUi.keys.add(key);
      if (event.repeat) return;
      if (key === 'q') stUiChooseBuild('st-farm'); if (key === 'e') stUiChooseBuild('st-income'); if (key === 'f') stUiChooseBuild('st-fort');
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
