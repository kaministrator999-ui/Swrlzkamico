// Native episode authoring. This panel edits the same project timeline used by Play.
let storyEditorTime = 8;
let storyEditorTrack = 'camera';
let storyEditorBeatIndex = 0;
let storyEditorUpdating = false;
let storyEditorInstalled = false;
let storyEditorReturnFocus = null;
let storyEditorLastRunning = false;
let storyEditorImporting = false;

const STORY_EDITOR_TRACK_LABELS = {
  camera: 'Camera', kami: 'Kami · main mage', swyrlz: '§wyrlz · companion mage',
  background: 'Background · distant arches', atmosphere: 'Atmosphere · light and mist',
  midground: 'Midground · library scenery', effects: 'Effects · magic',
  foreground: 'Foreground · desk props', book: 'Book · page hinges'
};
const STORY_EDITOR_FIELDS = {
  x: ['Position X', .05], y: ['Position Y', .05], z: ['Depth Z', .05],
  tx: ['Look at X', .05], ty: ['Look at Y', .05], tz: ['Look at Z', .05],
  fov: ['Field of view (°)', .5], scale: ['Scale', .01],
  rotation: ['Rotation (radians)', .01], opacity: ['Opacity', .05],
  unfold: ['Unfold', .05]
};

function storyEditorElement(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}
function storyEditorButton(id, text, action, label) {
  const button = storyEditorElement('button', '', text);
  button.id = id; button.type = 'button';
  if (label) button.setAttribute('aria-label', label);
  if (action) button.addEventListener('click', action);
  return button;
}
function storyEditorModel() {
  if (typeof storyTimeline === 'function') return storyTimeline();
  return window.SWYRL_ENGINE_ANIMATION?.getTimeline?.() || null;
}
function storyEditorState() {
  if (typeof storyStatus === 'function') return storyStatus();
  const isPlaying = typeof playing !== 'undefined' && playing;
  const isPaused = typeof paused !== 'undefined' && paused;
  return { playing: isPlaying, paused: isPaused, editable: !isPlaying || isPaused,
    active: typeof animeCine !== 'undefined' && !!animeCine,
    elapsed: typeof animeCine !== 'undefined' ? animeCine?.elapsed || 0 : 0 };
}
function storyEditorIsProject() {
  return typeof currentProject !== 'undefined' &&
    currentProject?.canonicalId === 'ghosts-different-forms-ep01';
}
function storyEditorNotify(message, error = false) {
  const output = document.getElementById('storyEditorStatus');
  if (output) { output.textContent = message; output.classList.toggle('story-error', error); }
}
function storyEditorNumber(value, digits = 2) {
  return String(Number(Number(value || 0).toFixed(digits)));
}
function storyEditorPause() {
  if (typeof playing !== 'undefined' && playing && typeof paused !== 'undefined' && !paused) {
    paused = true;
    if (typeof setSessionButtons === 'function') setSessionButtons();
    if (typeof animeUpdateControls === 'function') animeUpdateControls();
  }
}
function storyEditorPreviewFrame() {
  storyEditorPause();
  if (typeof storyPreview === 'function') {
    const result = storyPreview(storyEditorTime);
    if (result === false) { storyEditorNotify('Open the episode project to preview its frame.', true); return; }
  } else if (typeof animeCine !== 'undefined' && animeCine) {
    animeCine.elapsed = storyEditorTime; animeCine.ended = false;
    if (typeof animeUpdateCinematic === 'function') animeUpdateCinematic(0);
  }
  storyEditorSync();
  storyEditorNotify('Previewing ' + storyEditorNumber(storyEditorTime) + ' seconds.');
}
function storyEditorSetTime(value, preview = true) {
  const timeline = storyEditorModel();
  storyEditorTime = Math.min(Number(timeline?.duration) || 134, Math.max(0, Number(value) || 0));
  if (typeof storyBeat === 'function') storyEditorBeatIndex = storyBeat(storyEditorTime)?.index || 0;
  storyEditorSync();
  if (preview) storyEditorPreviewFrame();
}
// The primary Watch Episode action must play the saved native paper-theatre
// timeline. The 2018-style procedural 2D iframe is retained only as an
// explicitly labeled archival option; it must not silently replace v9 art.
function storyWatchNativeEpisode() {
  if (!storyEditorIsProject()) {
    toast('Open Ghosts in Different Forms from Projects first.'); return false;
  }
  if (typeof closeAnimeScreening === 'function') closeAnimeScreening();
  if (!document.getElementById('storyStudioPanel')?.hidden) storyEditorClose();
  if (typeof storyExitPreview === 'function') storyExitPreview();
  if ((playing || simulating) && !animeCine) stopSession();
  if (!playing) beginPlay();
  if (!animeCine) { toast('The native episode could not start.'); return false; }
  storyEditorTime = 0;
  animeSeek(0);
  paused = false;
  animeCine.ended = false;
  setSessionButtons();
  animeUpdateCinematic(0);
  if (!storyCinemaOpen()) {
    stopSession(); toast('The 2.5D screening player could not open.'); return false;
  }
  storyEditorSync();
  return true;
}
function storyWatchOriginalEpisode() {
  if (!storyEditorIsProject()) return false;
  if (!document.getElementById('storyStudioPanel')?.hidden) storyEditorClose();
  if (typeof storyExitPreview === 'function') storyExitPreview();
  if (playing || simulating) stopSession();
  return openAnimeScreening();
}
function storyEditorTogglePlay() {
  const state = storyEditorState();
  if (state.playing && !state.paused) {
    storyEditorTime = Number(state.elapsed) || storyEditorTime;
    storyEditorPause(); storyEditorSync(); storyEditorNotify('Paused. Edit this frame or choose another keyframe.');
    return;
  }
  if (!state.playing) {
    if (typeof storyExitPreview === 'function') storyExitPreview();
    if (typeof beginPlay === 'function') beginPlay();
  }
  if (typeof animeCine !== 'undefined' && animeCine) {
    animeCine.elapsed = storyEditorTime; animeCine.ended = false;
  }
  if (typeof paused !== 'undefined') paused = false;
  if (typeof setSessionButtons === 'function') setSessionButtons();
  if (typeof animeUpdateCinematic === 'function') animeUpdateCinematic(0);
  storyEditorSync(); storyEditorNotify('Playing the native episode from this frame.');
}
function storyEditorStopPlayback() {
  if (typeof stopSession === 'function') stopSession();
  if (typeof storyExitPreview === 'function') storyExitPreview();
  storyEditorSync(); storyEditorNotify('Stopped. Your timeline changes remain in the project.');
}
function storyEditorSaveProject() {
  const save = document.getElementById('saveBtn');
  if (save) { save.click(); storyEditorNotify('Save Project includes the animation timeline and layers.'); }
  else storyEditorNotify('The project Save control is unavailable.', true);
}
function storyEditorSaveTitle() {
  if (!storyEditorState().editable) { storyEditorNotify('Pause playback to edit the episode title.', true); return; }
  const title = document.getElementById('storyEpisodeName').value.trim();
  if (!title) { storyEditorNotify('Enter an episode title.', true); return; }
  const setTitle = typeof storySetTitle === 'function' ? storySetTitle : window.SWYRL_ENGINE_ANIMATION?.setTitle;
  if (!setTitle || setTitle(title) === false) { storyEditorNotify('The episode title could not be saved.', true); return; }
  if (typeof storyRender === 'function') storyRender();
  storyEditorSync(); storyEditorNotify('Episode title saved in the project.');
}
function storyEditorBuildBookStage() {
  if (!storyEditorState().editable) { storyEditorNotify('Pause playback to build the book stage.', true); return; }
  const build = typeof storyBuildStage === 'function' ? storyBuildStage : window.SWYRL_ENGINE_STORYBOARD?.buildStage;
  if (!build || build() === false) { storyEditorNotify('The native book stage could not be built.', true); return; }
  storyEditorSync(); storyEditorPreviewFrame(); storyEditorNotify('Book stage built with independent saved character and scenery layers.');
}
function storyEditorImportArtwork(event) {
  const input = event.currentTarget;
  const file = input.files?.[0];
  if (!file) return;
  const track = storyEditorTrack;
  if (track === 'camera' || track === 'book' || !storyEditorState().editable) {
    storyEditorNotify('Select a character or scenery track and pause playback before replacing its artwork.', true); input.value = ''; return;
  }
  if (!['image/png', 'image/webp', 'image/jpeg'].includes(file.type)) {
    storyEditorNotify('Choose a PNG, WebP, or JPEG image.', true); input.value = ''; return;
  }
  if (file.size > 8 * 1024 * 1024) {
    storyEditorNotify('Artwork must be 8 MiB or smaller.', true); input.value = ''; return;
  }
  storyEditorImporting = true; storyEditorRefreshControls();
  storyEditorNotify('Reading ' + file.name + ' for ' + STORY_EDITOR_TRACK_LABELS[track] + '.');
  const finish = () => { storyEditorImporting = false; input.value = ''; storyEditorRefreshControls(); };
  const reader = new FileReader();
  reader.onerror = () => { finish(); storyEditorNotify('This image could not be read. Choose it again.', true); };
  reader.onload = () => {
    if (typeof reader.result !== 'string') { finish(); storyEditorNotify('This image could not be read.', true); return; }
    const source = reader.result;
    const image = new Image();
    image.onerror = () => { finish(); storyEditorNotify('The file does not contain a readable image.', true); };
    image.onload = () => {
      const bind = typeof storyBindArtwork === 'function' ? storyBindArtwork : window.SWYRL_ENGINE_STORYBOARD?.bindArtwork;
      if (!bind || bind(track, source) === false) {
        finish(); storyEditorNotify('The image could not be assigned. Pause playback and select a saved layer.', true); return;
      }
      finish(); storyEditorSync(); storyEditorPreviewFrame();
      storyEditorNotify(file.name + ' assigned to ' + STORY_EDITOR_TRACK_LABELS[track] + '. Save Project to keep its artwork.');
    };
    image.src = source;
  };
  reader.readAsDataURL(file);
}
function storyEditorSaveKey() {
  if (!storyEditorState().editable) { storyEditorNotify('Pause playback to edit a keyframe.', true); return; }
  const key = { time: storyEditorTime };
  const panel = document.getElementById('storyStudioPanel');
  for (const input of panel.querySelectorAll('[data-story-field]')) {
    const name = input.dataset.storyField;
    if (input.type === 'checkbox') key[name] = input.checked;
    else if (input.tagName === 'SELECT') key[name] = input.value;
    else {
      if (!input.checkValidity() || !Number.isFinite(Number(input.value)) || input.value.trim() === '') {
        input.reportValidity(); storyEditorNotify('Enter a valid value for ' + (STORY_EDITOR_FIELDS[name]?.[0] || name) + '.', true); return;
      }
      key[name] = Number(input.value);
    }
  }
  if (typeof storyUpsertKey !== 'function' || !storyUpsertKey(storyEditorTrack, key)) {
    storyEditorNotify('The keyframe could not be updated. Pause playback and try again.', true); return;
  }
  storyEditorPreviewFrame();
  storyEditorNotify('Saved ' + STORY_EDITOR_TRACK_LABELS[storyEditorTrack] + ' keyframe at ' + storyEditorNumber(storyEditorTime) + ' seconds.');
}
function storyEditorDeleteKey() {
  if (!storyEditorState().editable) { storyEditorNotify('Pause playback to delete a keyframe.', true); return; }
  if (typeof storyRemoveKey !== 'function' || !storyRemoveKey(storyEditorTrack, storyEditorTime)) {
    storyEditorNotify('Select an existing keyframe to delete it.', true); return;
  }
  storyEditorPreviewFrame(); storyEditorNotify('Keyframe deleted. The remaining keys still interpolate.');
}
function storyEditorCapturePose() {
  if (!storyEditorState().editable) { storyEditorNotify('Pause playback to capture an actor pose.', true); return; }
  if (storyEditorTrack === 'camera') { storyEditorNotify('Select a character, scenery, or book track to capture its actor pose.', true); return; }
  if (typeof storyCaptureActorPose !== 'function' || storyCaptureActorPose(storyEditorTrack, storyEditorTime) === false) {
    storyEditorNotify('The actor pose could not be captured. Build the book stage and choose its saved layer.', true); return;
  }
  storyEditorPreviewFrame();
  storyEditorNotify('Captured ' + STORY_EDITOR_TRACK_LABELS[storyEditorTrack] + ' actor pose at ' + storyEditorNumber(storyEditorTime) + ' seconds.');
}
function storyEditorSaveBeat() {
  if (!storyEditorState().editable) { storyEditorNotify('Pause playback to edit the story.', true); return; }
  const beat = storyEditorModel()?.beats?.[storyEditorBeatIndex];
  if (!beat) return;
  const title = document.getElementById('storyBeatTitle').value.trim();
  if (!title) { storyEditorNotify('Give this story beat a title.', true); return; }
  const lines = document.getElementById('storyDialogue').value.split('\n').map(line => line.trim()).filter(Boolean);
  const cues = [];
  for (let i = 0; i < lines.length; i++) {
    const match = lines[i].match(/^(\d+(?:\.\d+)?)\s*\|\s*(.+)$/);
    const time = match ? Number(match[1]) : Math.min(Number(beat.end), Number(beat.time) + i * 3);
    const text = match ? match[2].trim() : lines[i];
    if (time < Number(beat.time) || time > Number(beat.end)) {
      storyEditorNotify('Dialogue times must be between ' + storyEditorNumber(beat.time) + ' and ' + storyEditorNumber(beat.end) + ' seconds.', true); return;
    }
    cues.push({ time, text });
  }
  if (typeof storySetBeat !== 'function' || !storySetBeat(storyEditorBeatIndex, { title, cues })) {
    storyEditorNotify('The story beat could not be updated. Pause playback and try again.', true); return;
  }
  if (typeof storyRender === 'function') storyRender();
  storyEditorSync(); storyEditorNotify('Story title and dialogue saved in the project.');
}
function storyEditorBuildFields(track) {
  const host = document.getElementById('storyKeyFields');
  host.replaceChildren(); host.dataset.track = track;
  const names = track === 'camera' ? ['x', 'y', 'z', 'tx', 'ty', 'tz', 'fov'] :
    ['x', 'y', 'z', 'scale', 'rotation', 'opacity', 'unfold'];
  for (const name of names) {
    const row = storyEditorElement('label', 'story-field');
    row.append(storyEditorElement('span', '', STORY_EDITOR_FIELDS[name][0]));
    const input = storyEditorElement('input');
    // Interpolated poses contain arbitrary decimals, so fixed step validation
    // would reject otherwise valid camera/layer samples on Add Keyframe.
    input.type = 'number'; input.step = 'any'; input.inputMode = 'decimal';
    input.dataset.storyField = name; input.required = true;
    input.setAttribute('aria-label', STORY_EDITOR_FIELDS[name][0]);
    const bounds = typeof storyBounds === 'function' ? storyBounds(track)[name] : null;
    if (bounds) { input.min = String(bounds[0]); input.max = String(bounds[1]); }
    else {
      if (name === 'scale') input.min = '.01';
      if (name === 'opacity' || name === 'unfold') { input.min = '0'; input.max = '1'; }
      if (name === 'fov') { input.min = '15'; input.max = '100'; }
    }
    row.append(input); host.append(row);
  }
  if (track !== 'camera') {
    const row = storyEditorElement('label', 'story-field story-check');
    row.append(storyEditorElement('span', '', 'Visible'));
    const input = storyEditorElement('input'); input.type = 'checkbox'; input.dataset.storyField = 'visible';
    input.setAttribute('aria-label', 'Layer visible at this keyframe'); row.append(input); host.append(row);
  }
  const easeRow = storyEditorElement('label', 'story-field');
  easeRow.append(storyEditorElement('span', '', 'Easing to next key'));
  const ease = storyEditorElement('select'); ease.dataset.storyField = 'ease'; ease.setAttribute('aria-label', 'Keyframe easing');
  for (const [value, label] of [['linear', 'Linear'], ['smooth', 'Smooth'], ['hold', 'Hold']]) {
    const option = storyEditorElement('option', '', label); option.value = value; ease.append(option);
  }
  easeRow.append(ease); host.append(easeRow);
}
function storyEditorRefreshControls() {
  const panel = document.getElementById('storyStudioPanel');
  if (!panel) return;
  const state = storyEditorState();
  const running = state.playing && !state.paused;
  const play = document.getElementById('storyPlay');
  play.textContent = running ? 'Ⅱ Pause' : state.playing ? '▶ Resume' : '▶ Play';
  play.setAttribute('aria-label', running ? 'Pause the native episode' : 'Play the native episode from the selected frame');
  for (const input of panel.querySelectorAll('[data-story-field], #storyEpisodeName, #storySaveTitle, #storyBeatTitle, #storyDialogue, #storySaveBeat, #storyAddKey')) input.disabled = !state.editable;
  const model = storyEditorModel();
  const exact = model?.tracks?.[storyEditorTrack]?.some(key => Math.abs(Number(key.time) - storyEditorTime) < 1e-6);
  const endpoint = storyEditorTime === 0 || storyEditorTime === Number(model?.duration);
  document.getElementById('storyDeleteKey').disabled = !state.editable || !exact || endpoint;
  document.getElementById('storyAddKey').textContent = exact ? 'Update Keyframe' : 'Add Keyframe';
  document.getElementById('storyCapturePose').disabled = !state.editable || storyEditorTrack === 'camera';
  document.getElementById('storyFrameMode').textContent = running ? 'Live playback · pause to edit' : exact ?
    (endpoint ? 'Opening/final keyframe · update its values' : 'Existing keyframe') : 'Interpolated frame · add a key to edit';
  const artwork = document.getElementById('storyArtwork');
  if (artwork) artwork.disabled = !state.editable || storyEditorImporting;
  const build = document.getElementById('storyBuildStage');
  if (build) build.disabled = !state.editable;
}
function storyEditorSync() {
  if (storyEditorUpdating || !document.getElementById('storyStudioPanel')) return;
  storyEditorUpdating = true;
  try {
    const timeline = storyEditorModel();
    if (!timeline) return;
    const duration = Number(timeline.duration) || 134;
    storyEditorTime = Math.min(duration, Math.max(0, Number(storyEditorTime) || 0));
    document.getElementById('storyEpisodeTitle').textContent = timeline.title || 'Ghosts in Different Forms · Episode 01';
    document.getElementById('storyEpisodeName').value = timeline.title || '';
    const scrub = document.getElementById('storyScrub'); scrub.max = String(duration); scrub.value = String(storyEditorTime);
    const time = document.getElementById('storyTime'); time.max = String(duration); time.value = storyEditorNumber(storyEditorTime, 6);
    document.getElementById('storyDuration').textContent = '/ ' + storyEditorNumber(duration) + ' s';
    const tracks = document.getElementById('storyTrack');
    const names = Object.keys(STORY_EDITOR_TRACK_LABELS).filter(name => timeline.tracks?.[name]);
    if (!names.includes(storyEditorTrack)) storyEditorTrack = names[0] || 'camera';
    tracks.replaceChildren();
    for (const name of names) { const option = storyEditorElement('option', '', STORY_EDITOR_TRACK_LABELS[name]); option.value = name; tracks.append(option); }
    tracks.value = storyEditorTrack;
    const fields = document.getElementById('storyKeyFields');
    if (fields.dataset.track !== storyEditorTrack) storyEditorBuildFields(storyEditorTrack);
    const keys = timeline.tracks?.[storyEditorTrack] || [];
    const exact = keys.find(key => Math.abs(Number(key.time) - storyEditorTime) < 1e-6);
    const sample = (typeof storySample === 'function' ? storySample(storyEditorTrack, storyEditorTime) : exact || keys[0]) || {};
    for (const input of fields.querySelectorAll('[data-story-field]')) {
      const name = input.dataset.storyField;
      if (input.type === 'checkbox') input.checked = sample[name] !== false;
      else if (input.tagName === 'SELECT') input.value = exact?.ease || sample.ease || 'smooth';
      else {
        let value = Number(storyEditorNumber(sample[name] ?? (name === 'scale' || name === 'opacity' || name === 'unfold' ? 1 : 0), 6));
        if (input.min !== '') value = Math.max(Number(input.min), value);
        if (input.max !== '') value = Math.min(Number(input.max), value);
        input.value = String(value);
      }
    }
    const keyList = document.getElementById('storyKeyList'); keyList.replaceChildren();
    for (const key of keys) {
      const button = storyEditorButton('', storyEditorNumber(key.time, 6) + ' s', () => storyEditorSetTime(key.time), 'Preview keyframe at ' + storyEditorNumber(key.time, 6) + ' seconds');
      button.dataset.storyKeyTime = String(key.time);
      const selected = Math.abs(Number(key.time) - storyEditorTime) < 1e-6;
      button.classList.toggle('is-selected', selected); button.setAttribute('aria-pressed', String(selected)); keyList.append(button);
    }
    if (!keys.length) keyList.append(storyEditorElement('span', 'story-muted', 'No keys yet. Add this frame.'));
    const beats = document.getElementById('storyBeatSelect'); beats.replaceChildren();
    storyEditorBeatIndex = Math.min(Math.max(0, storyEditorBeatIndex), Math.max(0, timeline.beats.length - 1));
    timeline.beats.forEach((beat, index) => {
      const option = storyEditorElement('option', '', String(index + 1).padStart(2, '0') + ' · ' + beat.title + ' · ' + storyEditorNumber(beat.time) + ' s');
      option.value = String(index); beats.append(option);
    });
    beats.value = String(storyEditorBeatIndex);
    const beat = timeline.beats[storyEditorBeatIndex];
    document.getElementById('storyBeatTitle').value = beat?.title || '';
    document.getElementById('storyDialogue').value = (beat?.cues || []).map(cue => storyEditorNumber(cue.time, 6) + ' | ' + cue.text).join('\n');
    document.getElementById('storyBeatRange').textContent = beat ? 'Beat range: ' + storyEditorNumber(beat.time) + '–' + storyEditorNumber(beat.end) + ' seconds. One dialogue cue per line: seconds | speaker: dialogue.' : '';
    const artworkRow = document.getElementById('storyArtworkRow');
    artworkRow.hidden = storyEditorTrack === 'camera' || storyEditorTrack === 'book';
    const stage = window.SWYRL_ENGINE_STORYBOARD?.stageStatus?.();
    const stageBuilt = (stage?.actorBindings?.length || 0) >= 8;
    document.getElementById('storyBuildStage').hidden = stageBuilt;
    document.getElementById('storyMaterialStatus').textContent = stage?.assetErrors?.length ?
      'Some layer artwork could not load. Replace its image or reload the project.' : stageBuilt ?
        (stage.assetsReady ? 'Native book stage ready. Each character and scenery layer has its own artwork.' : 'Native book stage built. Loading its independent layer artwork…') :
        'Build a native book stage to save and animate its independent layers.';
    storyEditorRefreshControls(); storyEditorPlaceButton();
  } finally { storyEditorUpdating = false; }
}
function storyEditorSetCollapsed(collapsed) {
  const panel = document.getElementById('storyStudioPanel');
  panel.classList.toggle('is-collapsed', collapsed);
  document.body.classList.toggle('story-studio-collapsed', collapsed);
  const button = document.getElementById('storyCollapse');
  button.textContent = collapsed ? 'Expand' : 'Collapse'; button.setAttribute('aria-expanded', String(!collapsed));
  document.getElementById('storyStudioBody').hidden = collapsed;
}
function storyEditorOpen() {
  if (!storyEditorIsProject()) return;
  storyEditorReturnFocus = document.activeElement;
  storyEditorPause();
  const state = storyEditorState();
  if (state.active) storyEditorTime = Number(state.elapsed) || 0;
  if (typeof storyBeat === 'function') storyEditorBeatIndex = storyBeat(storyEditorTime)?.index || 0;
  if (document.pointerLockElement) document.exitPointerLock?.();
  const director = document.getElementById('animeDirectorPanel'); if (director) director.hidden = true;
  document.getElementById('storyStudioPanel').hidden = false;
  document.getElementById('storyStudioBtn').setAttribute('aria-expanded', 'true');
  document.body.classList.add('story-studio-open'); storyEditorSetCollapsed(false);
  storyEditorSync(); storyEditorPreviewFrame(); document.getElementById('storyTrack').focus();
}
function storyEditorClose() {
  const panel = document.getElementById('storyStudioPanel'); if (!panel) return;
  panel.hidden = true; document.body.classList.remove('story-studio-open', 'story-studio-collapsed');
  document.getElementById('storyStudioBtn')?.setAttribute('aria-expanded', 'false');
  if (!storyEditorState().playing && typeof storyExitPreview === 'function') storyExitPreview();
  if (storyEditorReturnFocus?.isConnected) storyEditorReturnFocus.focus();
  else document.getElementById('storyStudioBtn')?.focus();
  storyEditorReturnFocus = null;
}
function storyEditorPlaceButton() {
  const button = document.getElementById('storyStudioBtn'); if (!button) return;
  const isProject = storyEditorIsProject(); button.hidden = !isProject;
  const panel = document.getElementById('storyStudioPanel');
  if (!isProject && !panel.hidden) storyEditorClose();
  const hud = document.getElementById('animeCineHud');
  const controls = hud?.classList.contains('show') ? hud.querySelector('.anime-cine-controls') : null;
  const entrybar = document.getElementById('storyStudioEntrybar');
  const target = controls || entrybar;
  const director = document.getElementById('animeDirectorBtn');
  if (director && director.parentElement !== target) target.append(director);
  if (button.parentElement !== target) target.append(button);
  entrybar.hidden = !isProject || !!controls;
}
function storyEditorInstall() {
  if (storyEditorInstalled || document.getElementById('storyStudioPanel')) return;
  storyEditorInstalled = true;
  const entrybar = storyEditorElement('div', 'story-studio-entrybar'); entrybar.id = 'storyStudioEntrybar';
  const entry = storyEditorButton('storyStudioBtn', '✦ Animation Studio', () => {
    if (document.getElementById('storyStudioPanel').hidden) storyEditorOpen(); else storyEditorClose();
  }, 'Open the native Animation Studio');
  entry.setAttribute('aria-controls', 'storyStudioPanel'); entry.setAttribute('aria-expanded', 'false'); entry.hidden = true; entrybar.append(entry);
  const panel = storyEditorElement('section', 'story-studio'); panel.id = 'storyStudioPanel'; panel.hidden = true;
  panel.setAttribute('aria-labelledby', 'storyStudioTitle');
  const header = storyEditorElement('header', 'story-studio-head');
  const title = storyEditorElement('strong', '', '✦ Animation Studio'); title.id = 'storyStudioTitle';
  const collapse = storyEditorButton('storyCollapse', 'Collapse', () => storyEditorSetCollapsed(!panel.classList.contains('is-collapsed')), 'Collapse or expand the animation editor');
  collapse.setAttribute('aria-controls', 'storyStudioBody'); collapse.setAttribute('aria-expanded', 'true');
  header.append(title, collapse, storyEditorButton('storyClose', '✕', storyEditorClose, 'Close Animation Studio')); panel.append(header);
  const body = storyEditorElement('div', 'story-studio-body'); body.id = 'storyStudioBody';
  const episodeTitle = storyEditorElement('h2', 'story-episode-title'); episodeTitle.id = 'storyEpisodeTitle'; body.append(episodeTitle);
  const episodeNameLabel = storyEditorElement('label', 'story-label'); episodeNameLabel.append(storyEditorElement('span', '', 'Episode title'));
  const episodeName = storyEditorElement('input'); episodeName.id = 'storyEpisodeName'; episodeName.type = 'text'; episodeName.maxLength = 180; episodeNameLabel.append(episodeName); body.append(episodeNameLabel);
  body.append(storyEditorButton('storySaveTitle', 'Save Title', storyEditorSaveTitle));
  const transport = storyEditorElement('div', 'story-transport');
  transport.append(storyEditorButton('storyPreview', '◈ Preview Frame', storyEditorPreviewFrame),
    storyEditorButton('storyPlay', '▶ Play', storyEditorTogglePlay), storyEditorButton('storyStop', '■ Stop', storyEditorStopPlayback)); body.append(transport);
  const archive = storyEditorButton('storyWatchOriginal', 'Watch original 2D episode (archive)', storyWatchOriginalEpisode,
    'Watch the original procedural 2D episode; the main Watch Episode button plays the current 2.5D scene');
  archive.classList.add('story-archive-link'); body.append(archive);
  const timeRow = storyEditorElement('label', 'story-time-row'); timeRow.append(storyEditorElement('span', '', 'Playhead'));
  const time = storyEditorElement('input'); time.id = 'storyTime'; time.type = 'number'; time.min = '0'; time.step = 'any'; time.required = true;
  time.setAttribute('aria-label', 'Episode playhead in seconds'); time.addEventListener('change', () => { if (time.checkValidity()) storyEditorSetTime(time.value); else time.reportValidity(); });
  const duration = storyEditorElement('span', 'story-muted'); duration.id = 'storyDuration'; timeRow.append(time, duration); body.append(timeRow);
  const scrub = storyEditorElement('input', 'story-scrub'); scrub.id = 'storyScrub'; scrub.type = 'range'; scrub.min = '0'; scrub.step = '.1';
  scrub.setAttribute('aria-label', 'Scrub the native episode timeline'); scrub.addEventListener('input', () => storyEditorSetTime(scrub.value)); body.append(scrub);
  const trackLabel = storyEditorElement('label', 'story-label'); trackLabel.append(storyEditorElement('span', '', 'Animation track'));
  const track = storyEditorElement('select'); track.id = 'storyTrack'; track.setAttribute('aria-label', 'Select camera, character, scenery, or book track');
  track.addEventListener('change', () => { storyEditorTrack = track.value; storyEditorSync(); }); trackLabel.append(track); body.append(trackLabel);
  const stageTools = storyEditorElement('div', 'story-stage-tools');
  stageTools.append(storyEditorButton('storyBuildStage', 'Build Book Stage', storyEditorBuildBookStage));
  const materialStatus = storyEditorElement('p', 'story-muted'); materialStatus.id = 'storyMaterialStatus'; stageTools.append(materialStatus);
  const artworkRow = storyEditorElement('label', 'story-label story-artwork-row'); artworkRow.id = 'storyArtworkRow';
  artworkRow.append(storyEditorElement('span', '', 'Replace layer artwork'));
  const artwork = storyEditorElement('input'); artwork.id = 'storyArtwork'; artwork.type = 'file'; artwork.accept = 'image/png,image/webp,image/jpeg';
  artwork.setAttribute('aria-label', 'Replace the selected character or scenery layer artwork'); artwork.setAttribute('aria-describedby', 'storyArtworkHint');
  artwork.addEventListener('change', storyEditorImportArtwork); artworkRow.append(artwork);
  const artworkHint = storyEditorElement('small', 'story-muted', 'PNG, WebP, or JPEG · up to 8 MiB. Transparent images preserve cutout edges.'); artworkHint.id = 'storyArtworkHint'; artworkRow.append(artworkHint);
  stageTools.append(artworkRow); body.append(stageTools);
  const frameMode = storyEditorElement('p', 'story-muted'); frameMode.id = 'storyFrameMode'; body.append(frameMode);
  const fields = storyEditorElement('div', 'story-key-fields'); fields.id = 'storyKeyFields'; body.append(fields);
  const keyActions = storyEditorElement('div', 'story-key-actions'); keyActions.append(storyEditorButton('storyAddKey', 'Add Keyframe', storyEditorSaveKey),
    storyEditorButton('storyCapturePose', 'Capture Actor Pose', storyEditorCapturePose, 'Copy the saved layer actor Inspector pose to a timeline keyframe'),
    storyEditorButton('storyDeleteKey', 'Delete Keyframe', storyEditorDeleteKey)); body.append(keyActions);
  body.append(storyEditorElement('p', 'story-muted', 'Timeline keys control playback. Capture Actor Pose copies the track’s native Inspector pose to the current keyframe.'));
  const keysTitle = storyEditorElement('span', 'story-section-label', 'Keyframes · tap to preview'); body.append(keysTitle);
  const keyList = storyEditorElement('div', 'story-key-list'); keyList.id = 'storyKeyList'; keyList.setAttribute('aria-label', 'Keyframes on the selected track'); body.append(keyList);
  const storyDetails = storyEditorElement('details', 'story-beat-editor'); storyDetails.open = true;
  storyDetails.append(storyEditorElement('summary', '', 'Story beats and dialogue'));
  const beatLabel = storyEditorElement('label', 'story-label'); beatLabel.append(storyEditorElement('span', '', 'Named story beat'));
  const beatSelect = storyEditorElement('select'); beatSelect.id = 'storyBeatSelect'; beatSelect.setAttribute('aria-label', 'Select a named story beat');
  beatSelect.addEventListener('change', () => {
    storyEditorBeatIndex = Number(beatSelect.value); const beat = storyEditorModel()?.beats?.[storyEditorBeatIndex];
    if (beat) storyEditorSetTime(beat.time);
  }); beatLabel.append(beatSelect); storyDetails.append(beatLabel);
  const beatTitleLabel = storyEditorElement('label', 'story-label'); beatTitleLabel.append(storyEditorElement('span', '', 'Beat title'));
  const beatTitle = storyEditorElement('input'); beatTitle.id = 'storyBeatTitle'; beatTitle.type = 'text'; beatTitle.maxLength = 180; beatTitleLabel.append(beatTitle); storyDetails.append(beatTitleLabel);
  const dialogueLabel = storyEditorElement('label', 'story-label'); dialogueLabel.append(storyEditorElement('span', '', 'Dialogue cues'));
  const dialogue = storyEditorElement('textarea'); dialogue.id = 'storyDialogue'; dialogue.rows = 4; dialogue.spellcheck = true; dialogue.setAttribute('aria-describedby', 'storyBeatRange'); dialogueLabel.append(dialogue); storyDetails.append(dialogueLabel);
  const beatRange = storyEditorElement('p', 'story-muted'); beatRange.id = 'storyBeatRange'; storyDetails.append(beatRange, storyEditorButton('storySaveBeat', 'Save Story Beat', storyEditorSaveBeat)); body.append(storyDetails);
  const footer = storyEditorElement('footer', 'story-studio-footer');
  const status = storyEditorElement('p', 'story-editor-status', 'Changes belong to this project. Save Project to keep a portable copy.'); status.id = 'storyEditorStatus'; status.setAttribute('role', 'status'); status.setAttribute('aria-live', 'polite');
  footer.append(status, storyEditorButton('storySaveProject', 'Save Project', storyEditorSaveProject)); body.append(footer); panel.append(body);
  panel.addEventListener('keydown', event => { if (event.key !== 'Escape') event.stopPropagation(); });
  document.body.append(entrybar, panel);
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && !panel.hidden) { event.preventDefault(); event.stopImmediatePropagation(); storyEditorClose(); }
  }, true);
  if (typeof syncAnimeScreening === 'function') {
    const previous = syncAnimeScreening;
    syncAnimeScreening = function () { previous(); storyEditorPlaceButton(); };
  }
  const directorButton = document.getElementById('animeDirectorBtn');
  directorButton?.addEventListener('click', () => { if (!panel.hidden) storyEditorClose(); });
  storyEditorSync(); storyEditorPlaceButton();
  let lastUpdate = 0;
  function tick(now) {
    if (now - lastUpdate > 150) {
      lastUpdate = now; storyEditorPlaceButton();
      if (!panel.hidden) {
        const state = storyEditorState(); const running = state.playing && !state.paused;
        if (running) {
          storyEditorTime = Number(state.elapsed) || 0;
          document.getElementById('storyTime').value = storyEditorNumber(storyEditorTime, 2);
          document.getElementById('storyScrub').value = String(storyEditorTime);
        } else if (storyEditorLastRunning) storyEditorSync();
        storyEditorLastRunning = running; storyEditorRefreshControls();
      }
    }
    requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
  window.SWYRL_ENGINE_ANIMATION_EDITOR = { open: storyEditorOpen, close: storyEditorClose,
    sync: storyEditorSync, preview: storyEditorSetTime };
}
