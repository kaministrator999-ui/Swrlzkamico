// Shuttle the same authored clock used by Play, Watch and every paper layer.
// Playback speed is session state; it never changes the saved animation keys.
function episodeTransportRate() {
  return [1, 2, 4, 8, -2, -4, -8].includes(animeCine?.transportRate)
    ? animeCine.transportRate : 1;
}
function episodeTransportSync() {
  if (!animeHud) return;
  const rate = episodeTransportRate();
  for (const [id, direction, label, glyph] of [
    ['animeCineRewind', -1, 'Rewind', '⏪'],
    ['animeCineFastForward', 1, 'Fast forward', '⏩']
  ]) {
    const button = animeHud.querySelector('#' + id);
    if (!button) continue;
    const selected = Math.sign(rate) === direction && Math.abs(rate) > 1;
    const next = selected ? Math.abs(rate) === 8 ? 1 : Math.abs(rate) * 2 : 2;
    button.textContent = glyph + (selected ? ' ' + Math.abs(rate) + '×' : '');
    button.setAttribute('aria-pressed', String(selected));
    const hint = next === 1 ? 'Return to normal playback' : label + ' at ' + next + '×';
    button.setAttribute('aria-label', hint);
    button.title = hint + ' · cycle 2×, 4×, 8×, normal';
  }
  const indicator = animeHud.querySelector('#animeCineRate');
  const text = (rate < 0 ? 'Rewind ' : '') + Math.abs(rate) + '×';
  if (indicator && indicator.textContent !== text) indicator.textContent = text;
}
function episodeTransportCycle(direction) {
  if (!animeCine || !playing) return;
  const rate = episodeTransportRate();
  const current = Math.sign(rate) === direction && Math.abs(rate) > 1 ? Math.abs(rate) : 1;
  const speed = current === 8 ? 1 : current * 2;
  animeCine.transportRate = speed === 1 ? 1 : direction * speed;
  const duration = storyTimeline().duration;
  // Rewind cannot cross the first frame. Fast forward can restart the episode.
  if (animeCine.transportRate < 0 && animeCine.elapsed <= 0) {
    animeCine.transportRate = 1;
    paused = true;
  } else {
    if (animeCine.transportRate > 0 && animeCine.elapsed >= duration) animeCine.elapsed = 0;
    paused = false;
  }
  animeCine.ended = false;
  setSessionButtons();
  animeUpdateCinematic(0);
}
const episodeTransportBuildHud = animeBuildHud;
animeBuildHud = function (...args) {
  const hud = episodeTransportBuildHud(...args);
  if (!hud || hud.querySelector('#animeCineRewind')) return hud;
  const previous = hud.querySelector('#animeCinePrev');
  const pause = hud.querySelector('#animeCinePause');
  const next = hud.querySelector('#animeCineNext');
  const group = document.createElement('span');
  group.className = 'anime-episode-transport';
  group.setAttribute('role', 'group');
  group.setAttribute('aria-label', 'Episode playback');
  previous.before(group);
  const makeButton = (id, direction) => {
    const button = document.createElement('button');
    button.type = 'button'; button.id = id;
    button.onclick = () => episodeTransportCycle(direction);
    return button;
  };
  group.append(previous, makeButton('animeCineRewind', -1), pause,
    makeButton('animeCineFastForward', 1), next);
  const originalPause = pause.onclick;
  pause.onclick = event => {
    const replay = !!animeCine?.ended;
    if (replay) animeCine.transportRate = 1;
    originalPause?.(event);
    // The historical Replay action seeks but keeps the endpoint pause flag.
    if (replay && animeCine) {
      paused = false; setSessionButtons(); animeUpdateCinematic(0);
    }
    episodeTransportSync();
  };
  const indicator = document.createElement('span');
  indicator.id = 'animeCineRate'; indicator.className = 'anime-cine-rate';
  indicator.setAttribute('role', 'status'); indicator.setAttribute('aria-live', 'polite');
  indicator.setAttribute('aria-label', 'Playback speed');
  hud.querySelector('#animeCineTime').after(indicator);
  episodeTransportSync();
  return hud;
};
const episodeTransportStart = animeStartCinematic;
animeStartCinematic = function (...args) {
  const result = episodeTransportStart(...args);
  if (result && animeCine) animeCine.transportRate = 1;
  episodeTransportSync();
  return result;
};
const episodeTransportWatch = storyWatchNativeEpisode;
storyWatchNativeEpisode = function (...args) {
  if (animeCine) animeCine.transportRate = 1;
  return episodeTransportWatch(...args);
};
animeUpdateCinematic = function (dt) {
  const c = animeCine;
  if (!c || !playing && !storyPreviewActive) return;
  const duration = storyTimeline().duration;
  const rate = episodeTransportRate();
  if (playing && !paused && !c.ended) {
    // Keep the engine's frame-delta cap, applying the multiplier afterwards.
    const delta = Number.isFinite(dt) ? Math.max(0, Math.min(dt, .06)) : 0;
    c.elapsed = Math.max(0, Math.min(duration, c.elapsed + delta * rate));
    if (rate < 0 && c.elapsed <= 0) {
      paused = true; c.ended = false; c.transportRate = 1; setSessionButtons();
    }
  }
  // Completion belongs to forward playback. Rewind may begin on the last
  // frame, including a zero-delta resize, before its first backward step.
  if (rate > 0 && c.elapsed >= duration && playing && !c.ended) {
    c.ended = true; paused = true; c.transportRate = 1; setSessionButtons();
  }
  // Render at the signed story time without adding a second forward step.
  storyRender();
};
const episodeTransportControls = animeUpdateControls;
animeUpdateControls = function (...args) {
  const result = episodeTransportControls(...args);
  episodeTransportSync();
  return result;
};
window.SWYRL_ENGINE_TRANSPORT = Object.freeze({
  status: () => ({active: !!animeCine && playing, rate: episodeTransportRate(),
    paused: !!paused, elapsed: animeCine?.elapsed ?? 0, duration: storyTimeline().duration})
});
