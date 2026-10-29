// Native Maul controls: all game orders pass through the domain bridge.
const maulUI = {
  installed: false, shown: false, buildKind: null, selectedTowerId: null,
  preview: null, sector: 0, lastRefresh: -Infinity, feedbackUntil: 0,
  pointers: new Set(), gesture: null, lastTowerTap: null, rulesFocus: null
};
const maulUIBuilds = [
  ['maulBuildArrow', 'arrow'], ['maulBuildCannon', 'cannon'],
  ['maulBuildFrost', 'frost'], ['maulBuildStorm', 'storm'], ['maulBuildWall', 'maze-wall']
];
const maulUISectorNames = [
  '1 · Northwest', '2 · North', '3 · Northeast',
  '4 · West', '5 · Center', '6 · East',
  '7 · Southwest', '8 · South', '9 · Southeast'
];
function maulUIText(id, value) { const element = $(id); if (element) element.textContent = String(value ?? ''); }
function maulUIActive() { return !!maulSession && (playing || simulating); }
function maulUICanOrder() { return maulUIActive() && !paused && !['won', 'lost'].includes(maulSession.phase); }
function maulUIFeedback(message, error = false) {
  maulUIText('maulFeedback', message);
  $('maulFeedback')?.classList.toggle('error', !!error);
  maulUI.feedbackUntil = performance.now() + 4500;
}
function maulUICommand(event) {
  if (!maulUICanOrder()) return {ok: false, reason: paused ? 'Resume the game to issue orders.' : 'This run has ended.'};
  const result = maulOrder(event);
  if (result?.ok === false) maulUIFeedback(result.reason || 'That order is unavailable.', true);
  maulRefreshHUD(true);
  return result;
}
function maulUIChooseBuild(kind) {
  if (!maulUICanOrder()) return;
  maulSetBuildKind(maulUI.buildKind === kind ? null : kind);
  maulUI.lastTowerTap = null;
  maulUIFeedback(maulUI.buildKind ? 'Place on the grid. Keep a route from every entrance to the exit.' : 'Build placement cancelled.');
  maulRefreshHUD(true);
}
function maulUICloseRules() {
  if ($('maulRulesPanel')) $('maulRulesPanel').hidden = true;
  $('maulRulesBtn')?.setAttribute('aria-expanded', 'false');
  if (maulUI.rulesFocus?.isConnected) maulUI.rulesFocus.focus();
  maulUI.rulesFocus = null;
}
function maulUIOpenRules() {
  if (currentProject?.kind !== 'maul' || maulUIActive()) return;
  const rules = maulRules();
  for (const key of ['autoWaves', 'soloSupport']) $('maulRule_' + key).checked = !!rules[key];
  for (const key of ['startGold', 'lives', 'waves', 'preparation', 'intermission', 'difficulty']) {
    const input = $('maulRule_' + key), value = String(rules[key]);
    if (key === 'difficulty' && !Array.from(input.options).some(option => option.value === value)) {
      for (const option of input.querySelectorAll('[data-maul-custom]')) option.remove();
      const option = document.createElement('option'); option.value = value;
      option.textContent = 'Custom · ' + value + '×'; option.dataset.maulCustom = 'true'; input.appendChild(option);
    }
    input.value = value;
  }
  maulUI.rulesFocus = document.activeElement;
  $('maulRulesPanel').hidden = false;
  $('maulRulesBtn').setAttribute('aria-expanded', 'true');
  maulUIText('maulRulesFeedback', 'Rules are saved with this project. Stop restores the authored map.');
  $('maulRulesClose').focus();
}
function maulUIApplyRules(play = false) {
  if (currentProject?.kind !== 'maul' || maulUIActive()) return false;
  const patch = {};
  for (const key of ['autoWaves', 'soloSupport']) patch[key] = $('maulRule_' + key).checked;
  for (const key of ['startGold', 'lives', 'waves', 'preparation', 'intermission', 'difficulty']) {
    const input = $('maulRule_' + key);
    if (input.value === '' || !input.checkValidity()) {
      input.reportValidity(); maulUIText('maulRulesFeedback', 'Enter values within the displayed limits.'); return false;
    }
    patch[key] = Number(input.value);
  }
  const result = maulConfigureRules(patch);
  if (result?.ok === false) {maulUIText('maulRulesFeedback', result.reason || 'These rules could not be saved.'); return false;}
  maulUIText('maulRulesFeedback', 'Rules saved. Use native Play to defend the map.');
  if (play) {maulUICloseRules(); $('playBtn').click();}
  return true;
}
function maulRefreshHUD(force = false) {
  const active = maulUIActive();
  $('maulRulesBtn')?.classList.toggle('hidden', currentProject?.kind !== 'maul' || active);
  if (currentProject?.kind !== 'maul') maulUICloseRules();
  if (!maulUI.shown || !active) return;
  const now = performance.now(); if (!force && now - maulUI.lastRefresh < 100) return;
  maulUI.lastRefresh = now;
  const state = maulSession, rules = state.rules || maulRules();
  const tower = (state.towers || []).find(item => item.id === maulUI.selectedTowerId);
  if (maulUI.selectedTowerId && !tower) maulUI.selectedTowerId = null;
  const finished = state.phase === 'won' || state.phase === 'lost';
  const canOrder = !paused && !finished;
  const waveType = wave => wave % 10 === 0 ? 'Boss' : wave % 5 === 0 ? 'Air' : 'Ground';
  const phases = {preparation: 'Build your first maze', wave: waveType(state.wave) + ' wave · enemies on the march', intermission: 'Strengthen the maze', won: 'The citadel held!', lost: 'The last gate fell'};
  maulUIText('maulGold', Math.floor(state.gold || 0) + ' gold');
  maulUIText('maulLives', state.lives + ' lives');
  maulUIText('maulWave', 'Wave ' + (state.wave || 0) + ' / ' + rules.waves);
  maulUIText('maulEnemies', (state.units || []).filter(unit => unit.alive !== false).length + ' enemies');
  maulUIText('maulPhase', (paused ? 'Paused · ' : '') + (phases[state.phase] || state.phase));
  $('maulPhase').classList.toggle('finished', finished);
  const timedPhase = state.phase === 'preparation' || state.phase === 'intermission';
  maulUIText('maulTimer', !finished && timedPhase ? 'Next: ' + waveType((state.wave || 0) + 1) + ' wave ' + ((state.wave || 0) + 1) + ' · ' +
    (rules.autoWaves ? 'starts in ' + Math.max(0, Math.ceil(state.timer || 0)) + 's' : 'start when ready') : '');
  maulUIText('maulPause', paused ? '▶ Resume' : 'Ⅱ Pause');
  $('maulPause').disabled = finished;
  $('maulStartWave').disabled = !canOrder || !timedPhase;
  maulUIText('maulStartWave', state.wave ? 'Start next wave' : 'Start wave 1');
  for (const [id, kind] of maulUIBuilds) {
    const button = $(id), definition = MAUL_CORE.definitions[kind];
    button.disabled = !canOrder || (state.gold || 0) < definition.cost;
    button.classList.toggle('active', maulUI.buildKind === kind);
    button.setAttribute('aria-pressed', String(maulUI.buildKind === kind));
  }
  $('maulCancel').hidden = !maulUI.buildKind;
  $('maulCancel').disabled = !canOrder;
  $('maulSpeed').disabled = paused || finished;
  maulUIText('maulSpeed', 'Speed ×' + (state.speed || 1));
  const definition = tower && MAUL_CORE.definitions[tower.kind];
  const level = definition?.levels?.[(tower?.level || 1) - 1];
  const upgradeCost = level?.upgradeCost || 0;
  const owner = tower?.owner || 'player', owned = owner === 'player';
  maulUIText('maulSelectedName', tower ? definition?.name || tower.kind : maulUI.buildKind ? MAUL_CORE.definitions[maulUI.buildKind]?.name || maulUI.buildKind : 'Build a connected maze');
  maulUIText('maulSelectedDetail', tower ? 'Level ' + tower.level + ' · ' + (owned ? 'Your tower' : 'Support tower') +
    (tower.kind !== 'maze-wall' && level ? ' · ' + level.damage + ' damage · ' + level.range + ' range' : '') :
    maulUI.buildKind ? 'Highlighted footprint is the exact placement. Red means unavailable.' : 'Select a tower to upgrade, sell or change its target.');
  $('maulTowerActions').hidden = !tower;
  $('maulUpgrade').disabled = !canOrder || !owned || !upgradeCost || state.gold < upgradeCost;
  maulUIText('maulUpgrade', upgradeCost ? 'Upgrade · ' + upgradeCost + 'g' : 'Maximum level');
  $('maulSell').disabled = !canOrder || !owned;
  $('maulPriority').disabled = !canOrder || !owned || tower?.kind === 'maze-wall';
  if (tower && document.activeElement !== $('maulPriority')) $('maulPriority').value = tower.priority || 'first';
  if (now > maulUI.feedbackUntil) maulUIText('maulFeedback', '');
  const placement = maulUI.preview;
  maulUIText('maulPlacement', maulUI.buildKind && placement ? (placement.valid ? 'Ready' : placement.reason || 'Unavailable') +
    ' · grid ' + placement.cx + ', ' + placement.cz : '');
  $('maulPlacement').classList.toggle('error', !!placement && !placement.valid);
  maulUIText('maulTip', maulUI.buildKind ? 'Tap to build; on phones the preview sits above your finger. Cancel exits placement.' :
    'Ground tap moves the builder. Double-tap towers on a phone to select. Air waves ignore maze paths.');
}
function maulShowHUD(show) {
  maulInstallUI();
  maulUI.shown = !!show; $('maulHUD').hidden = !show;
  app.classList.toggle('maul-runtime', !!show);
  if (show) {
    maulUICloseRules(); maulUI.lastRefresh = -Infinity; maulUI.lastTowerTap = null;
    maulUI.pointers.clear(); maulUI.gesture = null; maulUIFeedback('Build towers to shape the route, then start the first wave.');
    $('maulSector').value = String(maulUI.sector); maulRefreshHUD(true);
  }
}
function maulDisposeUI() {
  maulUI.buildKind = null; maulUI.selectedTowerId = null; maulUI.lastTowerTap = null;
  maulUI.pointers.clear(); maulUI.gesture = null; maulClearPreview();
  maulShowHUD(false); $('maulHelpPanel').hidden = true;
  $('maulHelp').setAttribute('aria-expanded', 'false');
  maulRefreshHUD(true);
}
function maulUIHandleTap(x, y, touch) {
  const id = maulHitTower(x, y);
  if (id) {
    const previous = maulUI.lastTowerTap, now = performance.now();
    if (!touch || previous?.id === id && now - previous.time < 550 && Math.hypot(x - previous.x, y - previous.y) < 32) {
      maulSelectTower(id); maulUI.lastTowerTap = null; maulRefreshHUD(true);
    } else {
      maulUI.lastTowerTap = {id, time: now, x, y};
      maulUIFeedback('Tap this tower again to select it.');
    }
  } else {
    maulUI.lastTowerTap = null; maulSelectTower(null);
    maulUICommand({type: 'move-builder', clientX: x, clientY: y});
  }
}
function maulUIInstallInput() {
  const canvas = renderer.domElement;
  const own = event => {event.preventDefault(); event.stopImmediatePropagation();};
  canvas.addEventListener('pointerdown', event => {
    if (!maulUIActive()) return;
    own(event);
    if (!maulUICanOrder() || event.button !== 0) return;
    maulUI.pointers.add(event.pointerId);
    if (maulUI.pointers.size > 1) {
      if (maulUI.gesture) maulUI.gesture.cancelled = true;
      maulClearPreview(); return;
    }
    maulUI.gesture = {id: event.pointerId, x: event.clientX, y: event.clientY,
      lastX: event.clientX, lastY: event.clientY, touch: event.pointerType === 'touch',
      buildKind: maulUI.buildKind, distance: 0, cancelled: false};
    canvas.setPointerCapture?.(event.pointerId);
    if (maulUI.buildKind) {maulPreviewAt(event.clientX, event.clientY, event.pointerType === 'touch'); maulRefreshHUD(true);}
  }, {capture: true, passive: false});
  canvas.addEventListener('pointermove', event => {
    if (!maulUIActive()) return;
    const gesture = maulUI.gesture;
    // Mouse hover shows the same grid footprint as click placement.
    if (!gesture && !paused && maulUI.buildKind && event.pointerType !== 'touch') {
      own(event); maulPreviewAt(event.clientX, event.clientY, false); maulRefreshHUD(); return;
    }
    if (!gesture || event.pointerId !== gesture.id) return;
    own(event);
    if (gesture.cancelled || !maulUICanOrder()) return;
    gesture.distance = Math.max(gesture.distance, Math.hypot(event.clientX - gesture.x, event.clientY - gesture.y));
    if (gesture.buildKind && gesture.buildKind === maulUI.buildKind) {
      maulPreviewAt(event.clientX, event.clientY, gesture.touch); maulRefreshHUD();
    } else if (gesture.distance > 8 && typeof maulPanCamera === 'function') {
      maulPanCamera(event.clientX - gesture.lastX, event.clientY - gesture.lastY);
    }
    gesture.lastX = event.clientX; gesture.lastY = event.clientY;
  }, {capture: true, passive: false});
  canvas.addEventListener('pointerup', event => {
    if (!maulUIActive()) return;
    own(event);
    maulUI.pointers.delete(event.pointerId);
    const gesture = maulUI.gesture;
    if (!gesture || event.pointerId !== gesture.id) return;
    const mayCommit = !gesture.cancelled && maulUICanOrder() && maulUI.pointers.size === 0;
    maulUI.gesture = null;
    if (mayCommit && gesture.buildKind && gesture.buildKind === maulUI.buildKind) {
      maulPreviewAt(event.clientX, event.clientY, gesture.touch);
      if (maulUI.preview) maulCommitPreview();
      else maulUIFeedback('Choose a buildable grid cell.', true);
    } else if (mayCommit && !gesture.buildKind && gesture.distance <= 8) {
      maulUIHandleTap(event.clientX, event.clientY, gesture.touch);
    } else maulClearPreview();
    maulRefreshHUD(true);
  }, {capture: true, passive: false});
  const cancel = event => {
    if (!maulUIActive()) return;
    own(event); maulUI.pointers.delete(event.pointerId);
    if (maulUI.gesture) maulUI.gesture.cancelled = true;
    if (!maulUI.pointers.size) maulUI.gesture = null;
    maulClearPreview(); maulRefreshHUD(true);
  };
  canvas.addEventListener('pointercancel', cancel, {capture: true, passive: false});
  canvas.addEventListener('lostpointercapture', event => {
    if (maulUI.gesture?.id === event.pointerId) cancel(event);
  }, {capture: true, passive: false});
  canvas.addEventListener('click', event => {if (maulUIActive()) own(event);}, {capture: true, passive: false});
  canvas.addEventListener('contextmenu', event => {if (maulUIActive()) own(event);}, {capture: true, passive: false});
  document.addEventListener('keydown', event => {
    if (!maulUIActive() || /^(INPUT|SELECT|TEXTAREA)$/.test(event.target?.tagName || '')) return;
    if (event.key === 'Escape') {
      event.preventDefault(); event.stopImmediatePropagation();
      if (!$('maulHelpPanel').hidden) {$('maulHelpPanel').hidden = true; $('maulHelp').setAttribute('aria-expanded', 'false');}
      else {maulSetBuildKind(null); maulClearPreview(); maulRefreshHUD(true);}
    }
  }, true);
}
function maulInstallUI() {
  if (maulUI.installed) return; maulUI.installed = true;
  const launcher = document.createElement('button'); launcher.id = 'maulRulesBtn'; launcher.type = 'button';
  launcher.textContent = 'Maul rules'; launcher.classList.add('hidden');
  launcher.setAttribute('aria-haspopup', 'dialog'); launcher.setAttribute('aria-expanded', 'false');
  launcher.onclick = maulUIOpenRules; $('playBtn').before(launcher);
  const hud = document.createElement('section'); hud.id = 'maulHUD'; hud.hidden = true;
  hud.setAttribute('aria-label', 'Maul tower defense game controls');
  hud.innerHTML = `<header class="maul-score"><div class="maul-title"><b>FROSTVEIL MAUL</b><small>NINE SECTORS · ONE LAST GATE</small></div><div id="maulStats" class="maul-stats"><strong id="maulGold"></strong><span id="maulLives"></span><span id="maulWave"></span><span id="maulEnemies"></span></div><div class="maul-session"><button id="maulSpeed" type="button">Speed ×1</button><button id="maulPause" type="button">Ⅱ Pause</button><button id="maulStop" type="button">■ Stop</button></div></header>
    <div class="maul-wave-banner"><b id="maulPhase" role="status" aria-live="polite"></b><span id="maulTimer"></span></div>
    <div class="maul-commandbar"><div class="maul-map-controls"><label for="maulSector">Defense sector</label><select id="maulSector">${maulUISectorNames.map((name, index) => '<option value="' + index + '">' + name + '</option>').join('')}</select><button id="maulOverview" type="button">Map overview</button><button id="maulStartWave" type="button">Start wave 1</button></div><div class="maul-orders"><div class="maul-selection"><b id="maulSelectedName">Build a connected maze</b><span id="maulSelectedDetail"></span></div><div class="maul-builds"><button id="maulBuildArrow" type="button" aria-pressed="false"><b>Arrow</b><small>20g · ground &amp; air</small></button><button id="maulBuildCannon" type="button" aria-pressed="false"><b>Cannon</b><small>50g · ground splash</small></button><button id="maulBuildFrost" type="button" aria-pressed="false"><b>Frost</b><small>45g · slowing bolts</small></button><button id="maulBuildStorm" type="button" aria-pressed="false"><b>Storm</b><small>70g · chain &amp; air</small></button><button id="maulBuildWall" type="button" aria-pressed="false"><b>Maze wall</b><small>5g · shapes paths</small></button><button id="maulCancel" type="button" hidden>✕ Cancel</button></div><div id="maulTowerActions" class="maul-tower-actions" hidden><button id="maulUpgrade" type="button">Upgrade</button><button id="maulSell" type="button">Sell</button><label for="maulPriority">Target<select id="maulPriority"><option value="first">First to the exit</option><option value="last">Last to the exit</option><option value="strong">Strongest</option><option value="near">Nearest</option></select></label></div><div id="maulPlacement" class="maul-placement" role="status"></div><div id="maulFeedback" class="maul-feedback" role="status" aria-live="polite"></div><div class="maul-hint"><span id="maulTip"></span><button id="maulHelp" type="button" aria-expanded="false">How to play</button></div></div></div>
    <aside id="maulHelpPanel" hidden><h2>Hold the last gate</h2><p>Build towers on the grid to make winding enemy routes through nine connected sectors. Leaks from upstream sectors arrive at downstream defenses. Every enemy escaping the last gate costs shared lives.</p><p>Arrow towers attack ground and air. Cannons splash ground enemies. Frost slows targets; Storm chains between enemies. Cheap walls extend the maze. Select your tower to upgrade, sell or choose its target priority.</p><p>You must leave a connected route from every entrance to the exit. The placement outline shows the exact occupied grid cell. Flying waves ignore maze walls; bosses arrive every tenth wave.</p><p>On a phone, tap the ground to move your builder and double-tap a tower to select it. While building, the preview is above your finger. Sector controls and Map overview move the camera.</p><p>This is a local starter with optional support towers in the other sectors. Set support, wave timers and difficulty in Maul rules while stopped. Native Pause freezes orders; Stop restores your editable map.</p><button id="maulHelpClose" type="button">Back to defense</button></aside>`;
  $('viewport').parentElement.appendChild(hud);
  for (const [id, kind] of maulUIBuilds) $(id).onclick = () => maulUIChooseBuild(kind);
  $('maulCancel').onclick = () => {if (!maulUICanOrder()) return; maulSetBuildKind(null); maulClearPreview(); maulRefreshHUD(true);};
  $('maulStartWave').onclick = () => maulUICommand({type: 'start-wave'});
  $('maulUpgrade').onclick = () => {
    const result = maulUICommand({type: 'upgrade', id: maulUI.selectedTowerId});
    if (result?.ok) maulUIFeedback('Tower upgraded.');
  };
  $('maulSell').onclick = () => {
    const result = maulUICommand({type: 'sell', id: maulUI.selectedTowerId});
    if (result?.ok) {maulSelectTower(null); maulUIFeedback('Tower sold' + (result.refund != null ? ' · ' + result.refund + ' gold returned.' : '.'));}
  };
  $('maulPriority').onchange = () => maulUICommand({type: 'priority', id: maulUI.selectedTowerId, priority: $('maulPriority').value});
  $('maulSector').onchange = () => {
    maulUI.sector = Number($('maulSector').value); maulClearPreview(); maulFrameSector(maulUI.sector); maulRefreshHUD(true);
  };
  $('maulOverview').onclick = () => {maulClearPreview(); maulFrameMap();};
  $('maulSpeed').onclick = () => {
    if (!maulUICanOrder()) return;
    const current = maulSession.speed || 1; maulSession.speed = current === 1 ? 2 : current === 2 ? 4 : 1;
    maulUIFeedback('Simulation speed ×' + maulSession.speed); maulRefreshHUD(true);
  };
  $('maulPause').onclick = () => {if (!maulUIActive()) return; maulUI.gesture = null; maulUI.pointers.clear(); maulClearPreview(); $('pauseBtn').click(); maulRefreshHUD(true);};
  $('maulStop').onclick = () => $('stopBtn').click();
  $('maulHelp').onclick = () => {$('maulHelpPanel').hidden = !$('maulHelpPanel').hidden; $('maulHelp').setAttribute('aria-expanded', String(!$('maulHelpPanel').hidden));};
  $('maulHelpClose').onclick = () => {$('maulHelpPanel').hidden = true; $('maulHelp').setAttribute('aria-expanded', 'false'); $('maulHelp').focus();};
  const rules = document.createElement('div'); rules.id = 'maulRulesPanel'; rules.hidden = true;
  rules.innerHTML = `<section class="maul-rules" role="dialog" aria-modal="true" aria-labelledby="maulRulesTitle"><header><div><small>EDITABLE STARTER RULES</small><h2 id="maulRulesTitle">Frostveil Maul</h2></div><button id="maulRulesClose" type="button">Close</button></header><p>A cooperative Wintermaul-style maze defense with nine connected sectors, shared lives and thirty waves. This starter runs locally; optional support towers cover the other sectors.</p><div class="maul-rule-toggles"><label><input id="maulRule_autoWaves" type="checkbox">Automatically start waves</label><label><input id="maulRule_soloSupport" type="checkbox">Support towers in other sectors</label></div><div class="maul-rule-fields"><label>Starting gold<input id="maulRule_startGold" type="number" min="0" max="100000" step="1"></label><label>Shared lives<input id="maulRule_lives" type="number" min="1" max="200" step="1"></label><label>Wave count<input id="maulRule_waves" type="number" min="1" max="30" step="1"></label><label>Preparation · seconds<input id="maulRule_preparation" type="number" min="0" max="180" step="any"></label><label>Between waves · seconds<input id="maulRule_intermission" type="number" min="0" max="60" step="any"></label><label>Enemy difficulty<select id="maulRule_difficulty"><option value="0.65">Relaxed · 0.65×</option><option value="1">Classic · 1×</option><option value="1.35">Hard · 1.35×</option><option value="1.75">Brutal · 1.75×</option></select></label></div><p class="maul-rules-note">You can move and save the native spawn, exit, tower and scenery actors in the editor. Ground routes are checked before Play and before each tower placement. Flying enemies follow their own path.</p><div class="maul-rule-actions"><button id="maulRulesApply" type="button">Save rules</button><button id="maulRulesPlay" type="button">Save &amp; Play</button></div><div class="maul-rule-actions"><button id="maulRulesSave" type="button">Save Project</button></div><div id="maulRulesFeedback" role="status" aria-live="polite"></div></section>`;
  document.body.appendChild(rules);
  $('maulRulesClose').onclick = maulUICloseRules;
  $('maulRulesApply').onclick = () => maulUIApplyRules(false);
  $('maulRulesPlay').onclick = () => maulUIApplyRules(true);
  $('maulRulesSave').onclick = () => {
    if (currentProject?.kind !== 'maul' || maulUIActive()) return;
    $('saveBtn').click();
    maulUIText('maulRulesFeedback', 'Saved the authored project. Use Save rules first to include changes in this form.');
  };
  rules.addEventListener('pointerdown', event => {if (event.target === rules) maulUICloseRules();});
  rules.addEventListener('keydown', event => {
    event.stopPropagation();
    if (event.key === 'Escape') {event.preventDefault(); maulUICloseRules();}
    if (event.key === 'Tab') {
      const focusable = Array.from(rules.querySelectorAll('button,input,select')).filter(element => !element.disabled);
      const first = focusable[0], last = focusable[focusable.length - 1];
      if (event.shiftKey && document.activeElement === first) {event.preventDefault(); last.focus();}
      else if (!event.shiftKey && document.activeElement === last) {event.preventDefault(); first.focus();}
    }
  });
  maulUIInstallInput();
  const name = $('projectName');
  if (name) new MutationObserver(() => maulRefreshHUD(true)).observe(name, {childList: true, subtree: true, characterData: true});
  maulRefreshHUD(true);
}
