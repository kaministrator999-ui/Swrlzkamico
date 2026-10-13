// Wintermaul Wars controls. Orders go through the native game bridge.
const warsUI = {
  installed: false, shown: false, buildKind: null, selectedTowerId: null,
  preview: null, sector: 0, lastRefresh: -Infinity, feedbackUntil: 0,
  pointers: new Set(), gesture: null, lastTowerTap: null, rulesFocus: null
};
const warsUIBuilds = [
  ['warsBuildArrow', 'arrow'], ['warsBuildCannon', 'cannon'],
  ['warsBuildFrost', 'frost'], ['warsBuildStorm', 'storm'], ['warsBuildWall', 'maze-wall']
];
const warsUISends = [
  ['warsSendWisp', 'wisp'], ['warsSendBrute', 'brute'],
  ['warsSendFlyer', 'flyer'], ['warsSendSiege', 'siege']
];
const warsUISectorNames = ['Red builder · west', 'Blue builder · east', 'Teal builder · rear'];
const warsUIRuleNumbers = ['startGold', 'startIncome', 'lives', 'preparation', 'incomeInterval', 'difficulty', 'seed'];
function warsUIText(id, value) { const element = $(id); if (element) element.textContent = String(value ?? ''); }
function warsUIActive() { return currentProject?.kind === 'maul-wars' && !!warsSession && (playing || simulating); }
function warsUICanOrder() { return warsUIActive() && !paused && !['won', 'lost'].includes(warsSession.phase); }
function warsUIPlayer() {
  const index = warsSession?.selectedSector ?? warsUI.sector;
  return warsSession?.players?.find(player => Number(player.id) === Number(index)) || warsSession?.players?.[index] || null;
}
function warsUIFeedback(message, error = false) {
  warsUIText('warsFeedback', message);
  $('warsFeedback')?.classList.toggle('error', !!error);
  warsUI.feedbackUntil = performance.now() + 4500;
}
function warsUICommand(event) {
  if (!warsUICanOrder()) return {ok: false, reason: paused ? 'Resume the game to issue orders.' : 'This run has ended.'};
  const result = warsOrder(event);
  if (result?.ok === false) warsUIFeedback(result.reason || 'That order is unavailable.', true);
  warsRefreshHUD(true);
  return result;
}
function warsUIChooseBuild(kind) {
  if (!warsUICanOrder()) return;
  warsSetBuildKind(warsUI.buildKind === kind ? null : kind);
  warsUI.lastTowerTap = null;
  warsUIFeedback(warsUI.buildKind ? 'Place inside this builder’s sector. Leave a path to the team base.' : 'Build placement cancelled.');
  warsRefreshHUD(true);
}
function warsUICloseRules() {
  if ($('warsRulesPanel')) $('warsRulesPanel').hidden = true;
  $('warsRulesBtn')?.setAttribute('aria-expanded', 'false');
  if (warsUI.rulesFocus?.isConnected) warsUI.rulesFocus.focus();
  warsUI.rulesFocus = null;
}
function warsUIOpenRules() {
  if (currentProject?.kind !== 'maul-wars' || warsUIActive()) return;
  const rules = warsRules();
  for (const key of ['opponentAI', 'soloSupport']) $('warsRule_' + key).checked = !!rules[key];
  for (const key of warsUIRuleNumbers) {
    const input = $('warsRule_' + key), value = String(rules[key]);
    if (key === 'difficulty' && !Array.from(input.options).some(option => option.value === value)) {
      for (const option of input.querySelectorAll('[data-wars-custom]')) option.remove();
      const option = document.createElement('option'); option.value = value;
      option.textContent = 'Custom · ' + value + '×'; option.dataset.warsCustom = 'true'; input.appendChild(option);
    }
    input.value = value;
  }
  warsUI.rulesFocus = document.activeElement;
  $('warsRulesPanel').hidden = false;
  $('warsRulesBtn').setAttribute('aria-expanded', 'true');
  warsUIText('warsRulesFeedback', 'Rules are saved with this project. Stop restores the authored map.');
  $('warsRulesClose').focus();
}
function warsUIApplyRules(play = false) {
  if (currentProject?.kind !== 'maul-wars' || warsUIActive()) return false;
  const patch = {};
  for (const key of ['opponentAI', 'soloSupport']) patch[key] = $('warsRule_' + key).checked;
  for (const key of warsUIRuleNumbers) {
    const input = $('warsRule_' + key);
    if (input.value === '' || !input.checkValidity()) {
      input.reportValidity(); warsUIText('warsRulesFeedback', 'Enter values within the displayed limits.'); return false;
    }
    patch[key] = Number(input.value);
  }
  const result = warsConfigureRules(patch);
  if (result?.ok === false) {warsUIText('warsRulesFeedback', result.reason || 'These rules could not be saved.'); return false;}
  warsUIText('warsRulesFeedback', 'Rules saved. Native Play starts this local tower war.');
  if (play) {warsUICloseRules(); $('playBtn').click();}
  return true;
}
function warsRefreshHUD(force = false) {
  const active = warsUIActive();
  $('warsRulesBtn')?.classList.toggle('hidden', currentProject?.kind !== 'maul-wars' || active);
  if (currentProject?.kind !== 'maul-wars') warsUICloseRules();
  if (!warsUI.shown || !active) return;
  const now = performance.now(); if (!force && now - warsUI.lastRefresh < 100) return;
  warsUI.lastRefresh = now;
  const state = warsSession, rules = state.rules || warsRules(), player = warsUIPlayer();
  const tower = (state.towers || []).find(item => item.id === warsUI.selectedTowerId);
  if (warsUI.selectedTowerId && !tower) warsUI.selectedTowerId = null;
  const finished = ['won', 'lost'].includes(state.phase), canOrder = !paused && !finished;
  const selected = state.selectedSector ?? warsUI.sector;
  warsUI.sector = selected;
  if (document.activeElement !== $('warsSector')) $('warsSector').value = String(selected);
  const north = state.teams?.find(team => Number(team.id) === 0) || state.teams?.[0];
  const south = state.teams?.find(team => Number(team.id) === 1) || state.teams?.[1];
  const own = !!tower && Number(tower.owner) === Number(selected);
  const phases = {preparation: 'Build before the first sends', battle: 'Send creeps · defend your team', won: 'North wins the tower war', lost: 'South wins the tower war'};
  if (finished && state.winner != null) phases[state.phase] = Number(state.winner) === 0 ? 'North wins the tower war' : 'South wins the tower war';
  warsUIText('warsGold', Math.floor(player?.gold || 0) + 'g');
  warsUIText('warsIncome', '+' + Math.floor(player?.income || 0) + 'g / payout');
  warsUIText('warsNorthLives', 'North ' + (north?.lives ?? rules.lives) + ' ♥');
  warsUIText('warsSouthLives', 'South ' + (south?.lives ?? rules.lives) + ' ♥');
  warsUIText('warsPhase', (paused ? 'Paused · ' : '') + (phases[state.phase] || state.phase));
  $('warsPhase').classList.toggle('finished', finished);
  warsUIText('warsTimer', finished ? '' : state.phase === 'preparation' ? 'Sending opens in ' + Math.max(0, Math.ceil(state.timer || 0)) + 's' :
    'Income in ' + Math.max(0, Math.ceil(state.incomeTimer || 0)) + 's · ' + (state.units || []).filter(unit => unit.alive !== false).length + ' creeps in play');
  warsUIText('warsPause', paused ? '▶ Resume' : 'Ⅱ Pause');
  $('warsPause').disabled = finished;
  $('warsSpeed').disabled = paused || finished;
  warsUIText('warsSpeed', 'Speed ×' + (state.speed || 1));
  for (const [id, kind] of warsUIBuilds) {
    const button = $(id), definition = MAUL_WARS_CORE.definitions[kind];
    button.disabled = !canOrder || !definition || (player?.gold || 0) < definition.cost;
    button.classList.toggle('active', warsUI.buildKind === kind);
    button.setAttribute('aria-pressed', String(warsUI.buildKind === kind));
    const cost = button.querySelector('[data-wars-cost]'); if (cost && definition) cost.textContent = definition.cost + 'g';
  }
  for (const [id, kind] of warsUISends) {
    const button = $(id), definition = MAUL_WARS_CORE.sends[kind];
    button.disabled = !canOrder || state.phase !== 'battle' || !definition || (player?.gold || 0) < definition.cost;
    const cost = button.querySelector('[data-wars-send-cost]');
    if (cost && definition) cost.textContent = definition.cost + 'g · +' + definition.income + ' income';
    if (definition) button.setAttribute('aria-label', 'Send ' + definition.name + ', ' + definition.cost + ' gold, adds ' + definition.income + ' income');
  }
  $('warsCancel').hidden = !warsUI.buildKind;
  $('warsCancel').disabled = !canOrder;
  const definition = tower && MAUL_WARS_CORE.definitions[tower.kind];
  const level = definition?.levels?.[(tower?.level || 1) - 1], upgradeCost = level?.upgradeCost || 0;
  const assist = selected !== 0 && rules.soloSupport ? ' · AI assisted' : '';
  warsUIText('warsSelectedName', tower ? definition?.name || tower.kind : warsUI.buildKind ? MAUL_WARS_CORE.definitions[warsUI.buildKind]?.name || warsUI.buildKind : warsUISectorNames[selected] || 'North builder');
  warsUIText('warsSelectedDetail', tower ? 'Level ' + tower.level + ' · ' + (own ? 'This builder’s tower' : 'Another builder’s tower') +
    (tower.kind !== 'maze-wall' && level ? ' · ' + level.damage + ' damage · ' + level.range + ' range' : '') :
    warsUI.buildKind ? 'Highlighted cell is the exact footprint. Red means unavailable.' : 'Separate wallet and maze' + assist + ' · sends grow your income.');
  $('warsTowerActions').hidden = !tower;
  $('warsUpgrade').disabled = !canOrder || !own || !upgradeCost || (player?.gold || 0) < upgradeCost;
  warsUIText('warsUpgrade', upgradeCost ? 'Upgrade · ' + upgradeCost + 'g' : 'Maximum level');
  $('warsSell').disabled = !canOrder || !own;
  $('warsPriority').disabled = !canOrder || !own || tower?.kind === 'maze-wall';
  if (tower && document.activeElement !== $('warsPriority')) $('warsPriority').value = tower.priority || 'first';
  if (now > warsUI.feedbackUntil) warsUIText('warsFeedback', '');
  const placement = warsUI.preview;
  warsUIText('warsPlacement', warsUI.buildKind && placement ? (placement.valid ? 'Ready' : placement.reason || 'Unavailable') + ' · grid ' + placement.cx + ', ' + placement.cz : '');
  $('warsPlacement').classList.toggle('error', !!placement && !placement.valid);
  warsUIText('warsTip', warsUI.buildKind ? 'Preview is above your finger. Cancel exits placement.' : 'Tap ground to move; double-tap towers on phones.');
}
function warsShowHUD(show) {
  warsInstallUI(); warsUI.shown = !!show; $('warsHUD').hidden = !show;
  app.classList.toggle('wars-runtime', !!show);
  if (show) {
    warsUICloseRules(); warsUI.lastRefresh = -Infinity; warsUI.lastTowerTap = null;
    warsUI.pointers.clear(); warsUI.gesture = null;
    warsUI.sector = warsSession?.selectedSector ?? 0;
    $('warsSector').value = String(warsUI.sector);
    warsUIFeedback('West and East defenses lead to the rear catcher, then North’s ship. Build, then send into South.');
    warsRefreshHUD(true);
  }
}
function warsDisposeUI() {
  warsUI.buildKind = null; warsUI.selectedTowerId = null; warsUI.lastTowerTap = null;
  warsUI.pointers.clear(); warsUI.gesture = null; warsClearPreview();
  warsShowHUD(false); $('warsHelpPanel').hidden = true;
  $('warsHelp').setAttribute('aria-expanded', 'false'); warsRefreshHUD(true);
}
function warsUIHandleTap(x, y, touch) {
  const id = warsHitTower(x, y);
  if (id) {
    const previous = warsUI.lastTowerTap, now = performance.now();
    if (!touch || previous?.id === id && now - previous.time < 550 && Math.hypot(x - previous.x, y - previous.y) < 32) {
      warsSelectTower(id); warsUI.lastTowerTap = null; warsRefreshHUD(true);
    } else {warsUI.lastTowerTap = {id, time: now, x, y}; warsUIFeedback('Tap this tower again to select it.');}
  } else {
    warsUI.lastTowerTap = null; warsSelectTower(null);
    warsUICommand({type: 'move-builder', clientX: x, clientY: y});
  }
}
function warsUIInstallInput() {
  const canvas = renderer.domElement;
  const own = event => {event.preventDefault(); event.stopImmediatePropagation();};
  canvas.addEventListener('pointerdown', event => {
    if (!warsUIActive()) return;
    own(event); if (!warsUICanOrder() || event.button !== 0) return;
    warsUI.pointers.add(event.pointerId);
    if (warsUI.pointers.size > 1) {if (warsUI.gesture) warsUI.gesture.cancelled = true; warsClearPreview(); return;}
    warsUI.gesture = {id: event.pointerId, x: event.clientX, y: event.clientY,
      lastX: event.clientX, lastY: event.clientY, touch: event.pointerType === 'touch',
      buildKind: warsUI.buildKind, distance: 0, cancelled: false};
    canvas.setPointerCapture?.(event.pointerId);
    if (warsUI.buildKind) {warsPreviewAt(event.clientX, event.clientY, event.pointerType === 'touch'); warsRefreshHUD(true);}
  }, {capture: true, passive: false});
  canvas.addEventListener('pointermove', event => {
    if (!warsUIActive()) return;
    const gesture = warsUI.gesture;
    if (!gesture && !paused && warsUI.buildKind && event.pointerType !== 'touch') {
      own(event); warsPreviewAt(event.clientX, event.clientY, false); warsRefreshHUD(); return;
    }
    if (!gesture || event.pointerId !== gesture.id) return;
    own(event); if (gesture.cancelled || !warsUICanOrder()) return;
    gesture.distance = Math.max(gesture.distance, Math.hypot(event.clientX - gesture.x, event.clientY - gesture.y));
    if (gesture.buildKind && gesture.buildKind === warsUI.buildKind) {warsPreviewAt(event.clientX, event.clientY, gesture.touch); warsRefreshHUD();}
    else if (gesture.distance > 8 && typeof warsPanCamera === 'function') warsPanCamera(event.clientX - gesture.lastX, event.clientY - gesture.lastY);
    gesture.lastX = event.clientX; gesture.lastY = event.clientY;
  }, {capture: true, passive: false});
  canvas.addEventListener('pointerup', event => {
    if (!warsUIActive()) return;
    own(event); warsUI.pointers.delete(event.pointerId);
    const gesture = warsUI.gesture; if (!gesture || event.pointerId !== gesture.id) return;
    const mayCommit = !gesture.cancelled && warsUICanOrder() && warsUI.pointers.size === 0;
    warsUI.gesture = null;
    if (mayCommit && gesture.buildKind && gesture.buildKind === warsUI.buildKind) {
      warsPreviewAt(event.clientX, event.clientY, gesture.touch);
      if (warsUI.preview) warsCommitPreview(); else warsUIFeedback('Choose a buildable grid cell.', true);
    } else if (mayCommit && !gesture.buildKind && gesture.distance <= 8) warsUIHandleTap(event.clientX, event.clientY, gesture.touch);
    else warsClearPreview();
    warsRefreshHUD(true);
  }, {capture: true, passive: false});
  const cancel = event => {
    if (!warsUIActive()) return;
    own(event); warsUI.pointers.delete(event.pointerId);
    if (warsUI.gesture) warsUI.gesture.cancelled = true;
    if (!warsUI.pointers.size) warsUI.gesture = null;
    warsClearPreview(); warsRefreshHUD(true);
  };
  canvas.addEventListener('pointercancel', cancel, {capture: true, passive: false});
  canvas.addEventListener('lostpointercapture', event => {if (warsUI.gesture?.id === event.pointerId) cancel(event);}, {capture: true, passive: false});
  canvas.addEventListener('click', event => {if (warsUIActive()) own(event);}, {capture: true, passive: false});
  canvas.addEventListener('contextmenu', event => {if (warsUIActive()) own(event);}, {capture: true, passive: false});
  document.addEventListener('keydown', event => {
    if (!warsUIActive() || /^(INPUT|SELECT|TEXTAREA)$/.test(event.target?.tagName || '')) return;
    if (event.key === 'Escape') {
      event.preventDefault(); event.stopImmediatePropagation();
      if (!$('warsHelpPanel').hidden) {$('warsHelpPanel').hidden = true; $('warsHelp').setAttribute('aria-expanded', 'false');}
      else {warsSetBuildKind(null); warsClearPreview(); warsRefreshHUD(true);}
    }
  }, true);
}
function warsUIStatus() {
  return {shown: warsUI.shown, active: warsUIActive(), canOrder: warsUICanOrder(), sector: warsUI.sector,
    buildKind: warsUI.buildKind, selectedTowerId: warsUI.selectedTowerId,
    preview: warsUI.preview ? {cx: warsUI.preview.cx, cz: warsUI.preview.cz,
      world: warsUI.preview.world ? {x: warsUI.preview.world.x, y: warsUI.preview.world.y ?? 0, z: warsUI.preview.world.z} : null,
      valid: !!warsUI.preview.valid, reason: warsUI.preview.reason || ''} : null,
    lastTowerTap: warsUI.lastTowerTap ? {...warsUI.lastTowerTap} : null,
    pointers: warsUI.pointers.size, gesture: !!warsUI.gesture, rulesOpen: !!$('warsRulesPanel') && !$('warsRulesPanel').hidden};
}
function warsInstallUI() {
  if (warsUI.installed) return; warsUI.installed = true;
  const launcher = document.createElement('button'); launcher.id = 'warsRulesBtn'; launcher.type = 'button';
  launcher.textContent = 'Wars rules'; launcher.classList.add('hidden');
  launcher.setAttribute('aria-haspopup', 'dialog'); launcher.setAttribute('aria-expanded', 'false');
  launcher.onclick = warsUIOpenRules; $('playBtn').before(launcher);
  const hud = document.createElement('section'); hud.id = 'warsHUD'; hud.hidden = true;
  hud.setAttribute('aria-label', 'Wintermaul Wars game controls');
  hud.innerHTML = `<header class="wars-score"><div class="wars-title"><b>FROSTVEIL WARS</b><small>THREE BUILDERS · TWO OPPOSING TEAMS</small></div><div id="warsStats" class="wars-stats"><strong id="warsGold"></strong><span id="warsIncome"></span><span id="warsNorthLives"></span><span id="warsSouthLives"></span></div><div class="wars-session"><button id="warsSpeed" type="button">Speed ×1</button><button id="warsPause" type="button">Ⅱ Pause</button><button id="warsStop" type="button">■ Stop</button></div></header>
    <div class="wars-battle-banner"><b id="warsPhase" role="status" aria-live="polite"></b><span id="warsTimer"></span></div>
    <div class="wars-commandbar"><div class="wars-map-controls"><label for="warsSector">Controlled builder</label><select id="warsSector">${warsUISectorNames.map((name, index) => '<option value="' + index + '">' + name + '</option>').join('')}</select><button id="warsOverview" type="button">Map</button><button id="warsEnemyView" type="button">South view</button><button id="warsHelp" type="button" aria-expanded="false">How to play</button></div><div class="wars-orders"><div class="wars-selection"><b id="warsSelectedName"></b><span id="warsSelectedDetail"></span></div><div class="wars-builds" aria-label="Build defenses"><button id="warsBuildArrow" type="button" aria-pressed="false"><b>Arrow</b><small data-wars-cost>20g</small></button><button id="warsBuildCannon" type="button" aria-pressed="false"><b>Cannon</b><small data-wars-cost>50g</small></button><button id="warsBuildFrost" type="button" aria-pressed="false"><b>Frost</b><small data-wars-cost>45g</small></button><button id="warsBuildStorm" type="button" aria-pressed="false"><b>Storm</b><small data-wars-cost>70g</small></button><button id="warsBuildWall" type="button" aria-pressed="false"><b>Wall</b><small data-wars-cost>5g</small></button><button id="warsCancel" type="button" hidden>✕ Cancel</button></div><div class="wars-send-label">SEND INTO SOUTH <span>Spend gold to grow recurring income</span></div><div class="wars-sends" aria-label="Send enemy creeps"><button id="warsSendWisp" type="button"><b>Wisp</b><small data-wars-send-cost></small></button><button id="warsSendBrute" type="button"><b>Brute</b><small data-wars-send-cost></small></button><button id="warsSendFlyer" type="button"><b>Flyer</b><small data-wars-send-cost></small></button><button id="warsSendSiege" type="button"><b>Siege</b><small data-wars-send-cost></small></button></div><div id="warsTowerActions" class="wars-tower-actions" hidden><button id="warsUpgrade" type="button">Upgrade</button><button id="warsSell" type="button">Sell</button><label for="warsPriority">Target<select id="warsPriority"><option value="first">First to base</option><option value="last">Last to base</option><option value="strong">Strongest</option><option value="near">Nearest</option></select></label></div><div id="warsPlacement" class="wars-placement" role="status"></div><div id="warsFeedback" class="wars-feedback" role="status" aria-live="polite"></div><div id="warsTip" class="wars-hint"></div></div></div>
    <aside id="warsHelpPanel" hidden><h2>Maze, send, survive</h2><p>North and South each have three connected defense territories on a cliff-lined horseshoe route: West and East frontline defenses, the rear catcher, then the team ship. Creeps follow this ordered route. Leaks reaching the ship cost shared lives. The first team to lose all lives loses.</p><p>You control North’s Red, Blue and Teal builders. Switch builders to use each separate gold and income balance. Optional assistance builds defenses for Blue and Teal; South’s optional AI builds and sends against you. This starter plays locally.</p><p>Sending creeps costs gold and permanently increases that builder’s recurring income. Balance sends with defenses. Wisps and Brutes follow maze routes; Flyers ignore tower walls. Siege creeps are tougher ground attackers.</p><p>Arrow hits ground and air. Cannon splashes ground targets. Frost slows; Storm chains. Walls make winding routes. You must leave every entrance connected to its base. Select a tower owned by the controlled builder to upgrade, sell or change targeting.</p><p>Tap ground to move a builder. On phones, double-tap a tower to select it; building previews sit above your finger and show the exact footprint. Map and South view reveal both teams. Drag the ground to pan.</p><p>Set starting resources, income timing and AI in Wars rules while stopped. Native Pause freezes play and orders. Stop restores your editable authored map.</p><button id="warsHelpClose" type="button">Back to the war</button></aside>`;
  $('viewport').parentElement.appendChild(hud);
  for (const [id, kind] of warsUIBuilds) $(id).onclick = () => warsUIChooseBuild(kind);
  for (const [id, kind] of warsUISends) $(id).onclick = () => {
    const result = warsUICommand({type: 'send', kind});
    if (result?.ok) warsUIFeedback((MAUL_WARS_CORE.sends[kind]?.name || kind) + ' sent to South · income increased.');
  };
  $('warsCancel').onclick = () => {if (!warsUICanOrder()) return; warsSetBuildKind(null); warsClearPreview(); warsRefreshHUD(true);};
  $('warsUpgrade').onclick = () => {const result = warsUICommand({type: 'upgrade', id: warsUI.selectedTowerId}); if (result?.ok) warsUIFeedback('Tower upgraded.');};
  $('warsSell').onclick = () => {
    const result = warsUICommand({type: 'sell', id: warsUI.selectedTowerId});
    if (result?.ok) {warsSelectTower(null); warsUIFeedback('Tower sold' + (result.refund != null ? ' · ' + result.refund + ' gold returned.' : '.'));}
  };
  $('warsPriority').onchange = () => warsUICommand({type: 'priority', id: warsUI.selectedTowerId, priority: $('warsPriority').value});
  $('warsSector').onchange = () => {
    if (!warsUICanOrder()) {$('warsSector').value = String(warsUI.sector); return;}
    const sector = Number($('warsSector').value); warsSetBuildKind(null); warsSelectTower(null);
    warsClearPreview(); warsFrameSector(sector); warsRefreshHUD(true);
  };
  $('warsOverview').onclick = () => {warsClearPreview(); warsFrameMap();};
  $('warsEnemyView').onclick = () => {warsClearPreview(); warsFrameEnemy();};
  $('warsSpeed').onclick = () => {
    if (!warsUICanOrder()) return;
    const current = warsSession.speed || 1; warsSession.speed = current === 1 ? 2 : current === 2 ? 4 : 1;
    warsUIFeedback('Simulation speed ×' + warsSession.speed); warsRefreshHUD(true);
  };
  $('warsPause').onclick = () => {if (!warsUIActive()) return; warsUI.gesture = null; warsUI.pointers.clear(); warsClearPreview(); $('pauseBtn').click(); warsRefreshHUD(true);};
  $('warsStop').onclick = () => $('stopBtn').click();
  $('warsHelp').onclick = () => {$('warsHelpPanel').hidden = !$('warsHelpPanel').hidden; $('warsHelp').setAttribute('aria-expanded', String(!$('warsHelpPanel').hidden));};
  $('warsHelpClose').onclick = () => {$('warsHelpPanel').hidden = true; $('warsHelp').setAttribute('aria-expanded', 'false'); $('warsHelp').focus();};
  const rules = document.createElement('div'); rules.id = 'warsRulesPanel'; rules.hidden = true;
  rules.innerHTML = `<section class="wars-rules" role="dialog" aria-modal="true" aria-labelledby="warsRulesTitle"><header><div><small>EDITABLE STARTER RULES</small><h2 id="warsRulesTitle">Frostveil Wars</h2></div><button id="warsRulesClose" type="button">Close</button></header><p>A Wintermaul Wars inspired local match: two mirrored teams, three builders per side, tower mazes and an income economy powered by sending creeps.</p><div class="wars-rule-toggles"><label><input id="warsRule_opponentAI" type="checkbox">South AI builds and sends</label><label><input id="warsRule_soloSupport" type="checkbox">Assist North’s Blue and Teal builders</label></div><div class="wars-rule-fields"><label>Starting gold · each builder<input id="warsRule_startGold" type="number" min="0" max="100000" step="1"></label><label>Starting income · each builder<input id="warsRule_startIncome" type="number" min="0" max="1000" step="1"></label><label>Shared lives · each team<input id="warsRule_lives" type="number" min="1" max="200" step="1"></label><label>Preparation · seconds<input id="warsRule_preparation" type="number" min="0" max="180" step="any"></label><label>Income interval · seconds<input id="warsRule_incomeInterval" type="number" min="5" max="120" step="any"></label><label>Creep difficulty<select id="warsRule_difficulty"><option value="0.65">Relaxed · 0.65×</option><option value="1">Classic · 1×</option><option value="1.35">Hard · 1.35×</option><option value="1.75">Brutal · 1.75×</option></select></label><label>Match seed<input id="warsRule_seed" type="number" min="0" max="4294967295" step="1"></label></div><p class="wars-rules-note">Move and save the native entrances, gates, bases, towers and scenery in the editor. Play checks ground routes. Placing a tower cannot close the route to a team base.</p><div class="wars-rule-actions"><button id="warsRulesApply" type="button">Save rules</button><button id="warsRulesPlay" type="button">Save &amp; Play</button></div><div class="wars-rule-actions"><button id="warsRulesSave" type="button">Save Project</button></div><div id="warsRulesFeedback" role="status" aria-live="polite"></div></section>`;
  document.body.appendChild(rules);
  $('warsRulesClose').onclick = warsUICloseRules;
  $('warsRulesApply').onclick = () => warsUIApplyRules(false);
  $('warsRulesPlay').onclick = () => warsUIApplyRules(true);
  $('warsRulesSave').onclick = () => {
    if (currentProject?.kind !== 'maul-wars' || warsUIActive()) return;
    $('saveBtn').click(); warsUIText('warsRulesFeedback', 'Saved the authored project. Use Save rules first to include form changes.');
  };
  rules.addEventListener('pointerdown', event => {if (event.target === rules) warsUICloseRules();});
  rules.addEventListener('keydown', event => {
    event.stopPropagation();
    if (event.key === 'Escape') {event.preventDefault(); warsUICloseRules();}
    if (event.key === 'Tab') {
      const focusable = Array.from(rules.querySelectorAll('button,input,select')).filter(element => !element.disabled);
      const first = focusable[0], last = focusable[focusable.length - 1];
      if (event.shiftKey && document.activeElement === first) {event.preventDefault(); last.focus();}
      else if (!event.shiftKey && document.activeElement === last) {event.preventDefault(); first.focus();}
    }
  });
  warsUIInstallInput();
  const name = $('projectName');
  if (name) new MutationObserver(() => warsRefreshHUD(true)).observe(name, {childList: true, subtree: true, characterData: true});
  warsRefreshHUD(true);
}
