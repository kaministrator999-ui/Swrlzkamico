/* SWRLZ Ice Dragon Theme controller v2.1.0 */
(function (global) {
  'use strict';

  const STORAGE_KEY = 'swrlz.chat.theme';
  const THEME = 'ice-dragon';
  const DEFAULT = 'default';
  const SELECT_ID = 'swrlzThemeSelect';
  const ART_STYLE_ID = 'swrlzIceDragonArt';

  function ensureDragonArt() {
    if (document.getElementById(ART_STYLE_ID)) return;
    const style = document.createElement('style');
    style.id = ART_STYLE_ID;
    style.textContent = `
      body[data-swrlz-theme="ice-dragon"] .dragon-mark > svg { opacity:0 !important; }
      body[data-swrlz-theme="ice-dragon"] .dragon-mark::after {
        content:""; position:absolute; inset:5px; pointer-events:none;
        background:url("/live/web/themes/ice-dragon/assets/ice-dragon-head.svg") center/contain no-repeat;
        filter:drop-shadow(0 0 7px rgba(141,246,255,.45));
      }
      body[data-swrlz-theme="ice-dragon"] .message:not(.user) .avatar > svg { opacity:0 !important; }
      body[data-swrlz-theme="ice-dragon"] .message:not(.user) .avatar {
        position:relative;
        background-image:url("/live/web/themes/ice-dragon/assets/ice-dragon-head.svg"),linear-gradient(145deg,rgba(118,235,255,.14),rgba(64,112,191,.09));
        background-position:center,center; background-repeat:no-repeat,no-repeat; background-size:72%,100%;
      }
      body[data-swrlz-theme="ice-dragon"]::after {
        right:-4vw !important; bottom:-10vh !important;
        width:min(66vw,820px) !important; height:min(66vw,820px) !important;
        opacity:.135 !important; transform:none !important;
      }
      @media(max-width:760px){
        body[data-swrlz-theme="ice-dragon"]::after {
          width:96vw !important; height:96vw !important;
          right:-24vw !important; bottom:9vh !important; opacity:.11 !important;
        }
      }
    `;
    document.head.append(style);
  }

  function current() {
    return document.body?.getAttribute('data-swrlz-theme') === THEME ? THEME : DEFAULT;
  }

  function syncControl(theme) {
    const select = document.getElementById(SELECT_ID);
    if (select && select.value !== theme) select.value = theme;
  }

  function set(theme, persist = true) {
    const body = document.body;
    if (!body) return;
    ensureDragonArt();
    const next = theme === THEME ? THEME : DEFAULT;
    if (next === THEME) body.setAttribute('data-swrlz-theme', THEME);
    else body.removeAttribute('data-swrlz-theme');
    if (persist) {
      try { localStorage.setItem(STORAGE_KEY, next); } catch (_) {}
    }
    syncControl(next);
    global.dispatchEvent(new CustomEvent('swrlz-theme-change', { detail: { theme: next } }));
  }

  function enable() { set(THEME, true); }
  function disable() { set(DEFAULT, true); }
  function toggle() { set(current() === THEME ? DEFAULT : THEME, true); }

  function mountControl() {
    if (document.getElementById(SELECT_ID)) return;
    const host = document.querySelector('.topbar-right');
    if (!host) return;
    const select = document.createElement('select');
    select.id = SELECT_ID;
    select.className = 'swrlz-theme-select';
    select.setAttribute('aria-label', 'Chat theme');
    select.title = 'Chat theme';
    const defaultOption = document.createElement('option');
    defaultOption.value = DEFAULT;
    defaultOption.textContent = 'Default';
    const iceOption = document.createElement('option');
    iceOption.value = THEME;
    iceOption.textContent = '❄ Ice Dragon';
    select.append(defaultOption, iceOption);
    select.value = current();
    select.addEventListener('change', () => set(select.value, true));
    host.insertBefore(select, host.firstChild);
  }

  function init() {
    ensureDragonArt();
    let saved = DEFAULT;
    try { saved = localStorage.getItem(STORAGE_KEY) || DEFAULT; } catch (_) {}
    set(saved, false);
    mountControl();
  }

  global.IceDragonTheme = { enable, disable, toggle, set, current, init, name: THEME };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init, { once: true });
  else init();
})(window);
