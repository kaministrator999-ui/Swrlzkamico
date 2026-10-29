// The pop-up cinema remains the user's Watch Episode experience. It hosts the
// real v9 WebGL canvas and native cinematic HUD, not the original 2D iframe.
// Do not create a second renderer, record frames or mutate the authored scene.
let storyNativeScreening = null;

function storyCinemaResize() {
  const session = storyNativeScreening;
  if (!session || !session.stage.isConnected) return;
  const rect = session.stage.getBoundingClientRect();
  const w = Math.max(1, Math.round(rect.width)), h = Math.max(1, Math.round(rect.height));
  if (w <= 1 || h <= 1) return;
  renderer.setSize(w, h, false);
  session.canvas.style.width = '100%';
  session.canvas.style.height = '100%';
  perspectiveCamera.aspect = w / h;
  perspectiveCamera.updateProjectionMatrix();
  if (animeCine) animeUpdateCinematic(0);
}
function storyCinemaUpdateChapters() {
  const session = storyNativeScreening;
  if (!session || !animeCine) return;
  const model = storyTimeline(), idx = storyBeat(animeCine.elapsed)?.index ?? 0;
  for (const [i, button] of session.chapters.entries()) {
    const selected = i === idx;
    button.classList.toggle('selected', selected);
    button.setAttribute('aria-current', selected ? 'step' : 'false');
  }
  const heading = session.host.querySelector('#storyCinemaHeading');
  if (heading) heading.textContent = model.title;
}
function storyCinemaRestoreCanvas() {
  const session = storyNativeScreening;
  if (!session) return false;
  storyNativeScreening = null;
  session.observer.disconnect();
  window.removeEventListener('resize', session.resize);
  if (session.nextSibling?.parentNode === session.parent) {
    session.parent.insertBefore(session.canvas, session.nextSibling);
  } else {
    session.parent.append(session.canvas);
  }
  if (session.canvasStyle == null) session.canvas.removeAttribute('style');
  else session.canvas.setAttribute('style', session.canvasStyle);
  session.hudParent.append(session.hud);
  renderer.setSize(session.width, session.height, false);
  perspectiveCamera.aspect = session.aspect;
  perspectiveCamera.updateProjectionMatrix();
  session.host.hidden = true;
  session.panel.classList.remove('story-native-screening');
  session.frame.hidden = false;
  return true;
}
function storyCinemaOpen() {
  if (storyNativeScreening) return true;
  if (!animeCine || !playing || currentProject?.canonicalId !== 'ghosts-different-forms-ep01') return false;
  const panel = document.getElementById('animeScreening');
  const frame = document.getElementById('animeEpisodeFrame');
  const canvas = renderer?.domElement, hud = animeHud;
  if (!panel || !frame || !canvas?.parentNode || !hud?.parentNode) return false;
  let host = document.getElementById('animeScreeningNative');
  if (!host) {
    host = document.createElement('section');
    host.id = 'animeScreeningNative';
    host.className = 'anime-screening-native';
    host.hidden = true;
    host.innerHTML =
      '<div class="story-cinema-meta"><span>§WYRL§ ANIMATION STUDIO · LIVE 2.5D PAPER THEATRE</span>'+
      '<strong id="storyCinemaHeading"></strong></div>'+
      '<div id="storyCinemaStage" class="story-cinema-stage" aria-label="Native 2.5D animated episode"></div>'+
      '<nav id="storyCinemaChapters" class="story-cinema-chapters" aria-label="Episode scenes"></nav>';
    frame.after(host);
  }
  const stage = host.querySelector('#storyCinemaStage');
  const nav = host.querySelector('#storyCinemaChapters');
  if (!stage || !nav) return false;
  const parent = canvas.parentNode, nextSibling = canvas.nextSibling;
  const size = renderer.getSize(new THREE.Vector2());
  const session = {
    panel, frame, host, stage, canvas, hud, parent, nextSibling,
    hudParent: hud.parentNode, canvasStyle: canvas.getAttribute('style'),
    width: size.x, height: size.y, aspect: perspectiveCamera.aspect,
    resize: () => requestAnimationFrame(storyCinemaResize), observer: null, chapters: []
  };
  storyNativeScreening = session;
  animeScreeningReturnFocus = document.activeElement;
  if (document.pointerLockElement) document.exitPointerLock?.();
  frame.removeAttribute('src');
  frame.hidden = true;
  host.hidden = false;
  panel.classList.add('open', 'story-native-screening');
  canvas.style.position = 'relative';
  canvas.style.left = 'auto';
  canvas.style.top = 'auto';
  canvas.style.display = 'block';
  stage.append(canvas, hud);
  const model = storyTimeline();
  nav.replaceChildren();
  for (const [index, beat] of model.beats.entries()) {
    const chapter = document.createElement('button');
    chapter.type = 'button';
    chapter.className = 'story-cinema-chapter';
    const no = document.createElement('b'); no.textContent = String(index + 1).padStart(2, '0');
    const title = document.createElement('span'); title.textContent = beat.title;
    chapter.append(no, title);
    chapter.setAttribute('aria-label', 'Play scene ' + (index + 1) + ': ' + beat.title);
    chapter.addEventListener('click', () => { if (animeCine) { animeSeek(beat.time); storyCinemaUpdateChapters(); } });
    nav.append(chapter); session.chapters.push(chapter);
  }
  session.observer = new ResizeObserver(session.resize);
  session.observer.observe(stage);
  window.addEventListener('resize', session.resize);
  storyCinemaResize();
  requestAnimationFrame(storyCinemaResize);
  storyCinemaUpdateChapters();
  document.getElementById('animeScreeningClose')?.focus();
  return true;
}
const storyOriginalStopSession = stopSession;
stopSession = function (...args) {
  const wasNative = storyCinemaRestoreCanvas();
  const result = storyOriginalStopSession(...args);
  if (wasNative) storyOriginalCloseAnimeScreening();
  return result;
};
const storyOriginalCloseAnimeScreening = closeAnimeScreening;
closeAnimeScreening = function () {
  if (storyCinemaRestoreCanvas() && (playing || simulating)) storyOriginalStopSession();
  return storyOriginalCloseAnimeScreening();
};
const storyOriginalAnimeUpdateControls = animeUpdateControls;
animeUpdateControls = function (...args) {
  const result = storyOriginalAnimeUpdateControls(...args);
  storyCinemaUpdateChapters();
  return result;
};
window.SWYRL_ENGINE_SCREENING = Object.freeze({
  status: () => ({open: !!storyNativeScreening, source: storyNativeScreening ? 'authored-native-2.5d' : null,
    chapters: storyNativeScreening?.chapters.length ?? 0}),
  close: () => closeAnimeScreening()
});
